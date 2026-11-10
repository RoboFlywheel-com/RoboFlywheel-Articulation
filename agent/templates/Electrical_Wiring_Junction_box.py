# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — junction_box (Electrical_Wiring / Junction box).

Waterproof IP68 electrical junction box. A grounded root ``enclosure`` (FIXED to
world, single root) holds a removable ``cover`` joined by ONE joint — a hinged
flip cover = REVOLUTE about -X, or a 4-screw lift-off cover = PRISMATIC +Z. N
threaded cable glands protrude from the side walls; the interior is a populated
terminal strip or a bare gasketed pass-through. Housing color is an ⑥ palette axis.

Mixed pattern (cushion style, no SlotSpec assembler). Discrete slots:
  - ③ footprint_envelope : rectangular (Box walls)  / round (LatheGeometry wall)
  - ② lid_mechanism      : hinged_flip (REVOLUTE -X) / screw_liftoff (PRISMATIC +Z)
  - C  interior_fitout   : terminal_strip / empty_passthrough
  - ①  gland_count N ∈ [2,8] (weighted), extrapolable
  - ⑥  palette_style     : 5 realistic IP-box colorways

Sources: origins S1/S2/S3 (black/gray/clear, 6/4/3 glands) + forks 2way (gland
loop), screw_lid (PRISMATIC), empty_passthrough (bare interior), round_box
(LatheGeometry). The glands come from ONE data-driven loop over ``gland_specs``
(the three origins copy-pasted ``_add_gland``; the 2way fork converged it). The
gland ribbed nut keeps ``KnobGeometry`` and the round wall keeps ``LatheGeometry``
(TEMPLATE_DESIGN_RULES ③ — never downgrade to a bare Cylinder/Box).

Frame: X = long axis (rect L), Y = short axis / depth (rear hinge at +Y), Z up
(floor at 0, mouth at H). Body centered on XY.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot vocabularies
# ---------------------------------------------------------------------------
Footprint = Literal["rectangular", "round"]
LidMechanism = Literal["hinged_flip", "screw_liftoff"]
Interior = Literal["terminal_strip", "empty_passthrough"]
PaletteStyle = Literal[
    "clear_polycarbonate",
    "black_abs",
    "light_gray_abs",
    "diecast_aluminum",
    "safety_blue_painted",
]

FOOTPRINTS: tuple[Footprint, ...] = ("rectangular", "round")
LID_MECHANISMS: tuple[LidMechanism, ...] = ("hinged_flip", "screw_liftoff")
INTERIORS: tuple[Interior, ...] = ("terminal_strip", "empty_passthrough")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_polycarbonate",
    "black_abs",
    "light_gray_abs",
    "diecast_aluminum",
    "safety_blue_painted",
)

# gland multiplicity — product {2,3,4,6}, template [2,8], small-N high-frequency.
N_MIN, N_MAX = 2, 8
GLAND_NS: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8)
GLAND_WEIGHTS: tuple[float, ...] = (0.28, 0.24, 0.22, 0.12, 0.10, 0.02, 0.02)

# ---------------------------------------------------------------------------
# Palettes — only shell/shell_edge vary per style; hardware colors are fixed
# realistic values (yellow gasket, white terminals, brass, metal screws, black
# glands). EVERY visual pulls its material from this dict (per-seed color axis).
# ---------------------------------------------------------------------------
_HARDWARE: dict[str, tuple[float, float, float, float]] = {
    "gasket": (1.0, 0.80, 0.03, 1.0),
    "terminal": (0.92, 0.91, 0.86, 1.0),
    "brass": (0.95, 0.66, 0.24, 1.0),
    "copper": (0.90, 0.42, 0.16, 1.0),
    "screw_metal": (0.82, 0.84, 0.85, 1.0),
    "dark": (0.02, 0.02, 0.02, 1.0),
    "gland_body": (0.11, 0.11, 0.12, 1.0),
    "gland_nut": (0.03, 0.03, 0.035, 1.0),
    "label": (0.93, 0.90, 0.80, 1.0),
    "label_dark": (0.05, 0.05, 0.05, 1.0),
}
_SHELLS: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "clear_polycarbonate": {"shell": (0.76, 0.84, 1.00, 0.42), "shell_edge": (0.70, 0.78, 1.00, 0.55)},
    "black_abs": {"shell": (0.02, 0.02, 0.022, 1.0), "shell_edge": (0.07, 0.07, 0.075, 1.0)},
    "light_gray_abs": {"shell": (0.62, 0.64, 0.65, 1.0), "shell_edge": (0.50, 0.52, 0.53, 1.0)},
    "diecast_aluminum": {"shell": (0.66, 0.68, 0.70, 1.0), "shell_edge": (0.55, 0.57, 0.60, 1.0)},
    "safety_blue_painted": {"shell": (0.10, 0.24, 0.48, 1.0), "shell_edge": (0.07, 0.18, 0.38, 1.0)},
}


def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    return {**_HARDWARE, **_SHELLS[style]}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters).
# ---------------------------------------------------------------------------
_BASE_L = 0.180
_BASE_W = 0.130
_BASE_R = 0.075
_BASE_H = 0.058
_WALL_RECT = 0.007
_WALL_ROUND = 0.005
_FLOOR = 0.004
_GASKET_H = 0.002
_COVER_T = 0.008

_GLAND_PITCH = 0.046   # min gland center-to-center along a wall / around the ring
_END_MARGIN = 0.026    # margin from the wall ends to the first gland
_GLAND_MAX_R = 0.0155  # gland collar/nut outer radius (vertical fit budget)
_HINGE_OFFSET = 0.014  # hinge pivot outboard of the box rear face
_SEAT_GAP = 0.0008     # hinged cover clearance above the gasket top

# gland stack local offsets (distance outward from the wall surface). Faithful to
# S3 _add_gland (L45-56) / round_box _add_radial_gland (L47-63).
_GLAND_THREAD_RINGS = (-0.007, -0.003, 0.001, 0.005)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class JunctionBoxConfig:
    footprint_envelope: Footprint | None = None
    lid_mechanism: LidMechanism | None = None
    interior_fitout: Interior | None = None
    gland_count: int | None = None
    palette_style: PaletteStyle = "clear_polycarbonate"
    terminal_count: int | None = None
    len_scale: float = 1.0
    width_scale: float = 1.0
    radius_scale: float = 1.0
    height_scale: float = 1.0
    lid_open_scale: float = 1.0
    lift_travel_scale: float = 1.0
    name: str = "junction_box"


@dataclass(frozen=True)
class ResolvedJunctionBoxConfig:
    footprint_envelope: Footprint
    lid_mechanism: LidMechanism
    interior_fitout: Interior
    gland_count: int
    palette_style: PaletteStyle
    terminal_count: int
    # concrete geometry
    L: float
    W: float
    R: float
    H: float
    wall: float
    floor: float
    gland_z: float
    mouth_top: float
    box_rear: float
    hinge_y: float
    hinge_z: float
    lift_z: float
    lid_open: float
    lift_travel: float
    name: str

    @property
    def is_round(self) -> bool:
        return self.footprint_envelope == "round"


def config_from_seed(seed: int) -> JunctionBoxConfig:
    rng = random.Random(seed)
    return JunctionBoxConfig(
        footprint_envelope=rng.choice(FOOTPRINTS),
        lid_mechanism=rng.choice(LID_MECHANISMS),
        interior_fitout=rng.choice(INTERIORS),
        gland_count=rng.choices(GLAND_NS, weights=GLAND_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        terminal_count=rng.randint(3, 8),
        len_scale=round(rng.uniform(0.85, 1.20), 4),
        width_scale=round(rng.uniform(0.85, 1.20), 4),
        radius_scale=round(rng.uniform(0.85, 1.20), 4),
        height_scale=round(rng.uniform(0.80, 1.25), 4),
        lid_open_scale=round(rng.uniform(0.85, 1.10), 4),
        lift_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_junction_box_{seed}",
    )


def resolve_config(config: JunctionBoxConfig | None = None) -> ResolvedJunctionBoxConfig:
    cfg = config or JunctionBoxConfig()
    footprint = _pick(cfg.footprint_envelope, FOOTPRINTS)
    lid = _pick(cfg.lid_mechanism, LID_MECHANISMS)
    interior = _pick(cfg.interior_fitout, INTERIORS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(_clamp(int(cfg.gland_count if cfg.gland_count is not None else 4), N_MIN, N_MAX))
    k = int(_clamp(int(cfg.terminal_count if cfg.terminal_count is not None else 6), 3, 8))

    is_round = footprint == "round"
    wall = _WALL_ROUND if is_round else _WALL_RECT

    len_s = _clamp(cfg.len_scale, 0.85, 1.20)
    width_s = _clamp(cfg.width_scale, 0.85, 1.20)
    rad_s = _clamp(cfg.radius_scale, 0.85, 1.20)
    h_s = _clamp(cfg.height_scale, 0.80, 1.25)

    if is_round:
        # inequality: glands spaced around the ring must not overlap.
        min_r = n * _GLAND_PITCH / (2.0 * math.pi) + wall + 0.006
        R = _clamp(max(_BASE_R * rad_s, min_r), 0.055, 0.110)
        L = W = 2.0 * R
        box_rear = R
    else:
        # inequality: ceil(N/2) glands per long wall must not overlap.
        front_n = math.ceil(n / 2.0)
        min_L = (front_n - 1) * _GLAND_PITCH + 2.0 * _END_MARGIN
        L = _clamp(max(_BASE_L * len_s, min_L), min_L, 0.30)
        W = _clamp(_BASE_W * width_s, 0.095, 0.180)
        R = 0.0
        box_rear = W / 2.0

    # inequality: H must fit a wall-centered gland vertically.
    H = _BASE_H * h_s
    H = max(H, 2.0 * _GLAND_MAX_R + _FLOOR + 0.010, 0.047)

    mouth_top = H
    gland_z = _FLOOR + (H - _FLOOR) * 0.42
    hinge_y = box_rear + _HINGE_OFFSET
    panel_bottom = mouth_top + _GASKET_H + _SEAT_GAP
    hinge_z = panel_bottom + _COVER_T / 2.0
    lift_z = mouth_top + _GASKET_H

    lid_open = _clamp(1.15 * _clamp(cfg.lid_open_scale, 0.85, 1.10), 1.0, 1.35)
    lift_travel = _clamp(0.075 * _clamp(cfg.lift_travel_scale, 0.85, 1.15), 0.06, 0.10)

    return ResolvedJunctionBoxConfig(
        footprint_envelope=footprint,
        lid_mechanism=lid,
        interior_fitout=interior,
        gland_count=n,
        palette_style=palette,
        terminal_count=k,
        L=L,
        W=W,
        R=R,
        H=H,
        wall=wall,
        floor=_FLOOR,
        gland_z=gland_z,
        mouth_top=mouth_top,
        box_rear=box_rear,
        hinge_y=hinge_y,
        hinge_z=hinge_z,
        lift_z=lift_z,
        lid_open=lid_open,
        lift_travel=lift_travel,
        name=cfg.name or "junction_box",
    )


def with_overrides(config: JunctionBoxConfig, **kwargs: object) -> JunctionBoxConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: JunctionBoxConfig | ResolvedJunctionBoxConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedJunctionBoxConfig) else resolve_config(config)
    return (
        ("footprint_envelope", r.footprint_envelope),
        ("lid_mechanism", r.lid_mechanism),
        ("interior_fitout", r.interior_fitout),
        ("gland_count", f"n{r.gland_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Small visual helper
# ---------------------------------------------------------------------------
def _v(part, geom, xyz, mat, name, rpy=(0.0, 0.0, 0.0)):
    part.visual(geom, origin=Origin(xyz=xyz, rpy=rpy), material=mat, name=name, material_class_id="plastic.opaque_glossy_molded")


# ---------------------------------------------------------------------------
# Gland (multiplicity) — ONE shared stack helper + ONE shared ribbed-nut mesh.
# ---------------------------------------------------------------------------
def _gland_layout(r: ResolvedJunctionBoxConfig) -> list[tuple[tuple[float, float, float], float]]:
    """Return [(wall_point, outward_azimuth_theta), ...] for the N glands."""
    n = r.gland_count
    specs: list[tuple[tuple[float, float, float], float]] = []
    if r.is_round:
        for i in range(n):
            theta = -math.pi / 2.0 + i * (2.0 * math.pi / n)
            point = (r.R * math.cos(theta), r.R * math.sin(theta), r.gland_z)
            specs.append((point, theta))
        return specs
    # rectangular: split N over front (-Y) and rear (+Y) long walls.
    front_n = math.ceil(n / 2.0)
    rear_n = n - front_n
    usable = r.L - 2.0 * _END_MARGIN
    for wall_sign, theta, count in ((-1.0, -math.pi / 2.0, front_n), (1.0, math.pi / 2.0, rear_n)):
        if count <= 0:
            continue
        if count == 1:
            xs = [0.0]
        else:
            xs = [-usable / 2.0 + i * (usable / (count - 1)) for i in range(count)]
        y_wall = wall_sign * (r.W / 2.0)
        for x in xs:
            specs.append(((x, y_wall, r.gland_z), theta))
    return specs


def _emit_gland(part, point, theta, mats, ribbed_mesh, prefix):
    px, py, pz = point
    ct, st = math.cos(theta), math.sin(theta)
    rpy = (0.0, math.pi / 2.0, theta)

    def at(d):
        return (px + d * ct, py + d * st, pz)

    _v(part, Cylinder(0.0115, 0.020), at(0.002), mats["gland_body"], f"{prefix}_thread", rpy)
    for i, d in enumerate(_GLAND_THREAD_RINGS):
        _v(part, Cylinder(0.0127, 0.0012), at(d), mats["gland_body"], f"{prefix}_thread_ring_{i}", rpy)
    _v(part, Cylinder(0.0155, 0.0055), at(0.0125), mats["gland_nut"], f"{prefix}_collar", rpy)
    _v(part, ribbed_mesh, at(0.027), mats["gland_nut"], f"{prefix}_ribbed_nut", rpy)
    _v(part, Cylinder(0.0135, 0.006), at(0.040), mats["gland_nut"], f"{prefix}_domed_end", rpy)
    _v(part, Cylinder(0.0070, 0.0014), at(0.043), mats["dark"], f"{prefix}_bore", rpy)


def _emit_glands(enc, r, mats, ribbed_mesh):
    for i, (point, theta) in enumerate(_gland_layout(r)):
        _emit_gland(enc, point, theta, mats, ribbed_mesh, f"gland_{i}")


# ---------------------------------------------------------------------------
# Enclosure (root) — footprint-dependent walls + gasket + mount ears + labels.
# ---------------------------------------------------------------------------
def _build_enclosure(model, r: ResolvedJunctionBoxConfig, mats):
    enc = model.part("enclosure")
    shell = mats["shell"]
    edge = mats["shell_edge"]

    if r.is_round:
        R, H, wall = r.R, r.H, r.wall
        wall_geom = mesh_from_geometry(
            LatheGeometry.from_shell_profiles(
                [(R, r.floor), (R, H)],
                [(R - wall, r.floor), (R - wall, H)],
                segments=48,
            ),
            "cylindrical_wall",
        )
        _v(enc, wall_geom, (0.0, 0.0, 0.0), shell, "cylindrical_wall")
        _v(enc, Cylinder(R, r.floor), (0.0, 0.0, r.floor / 2.0), shell, "floor_plate")
        gasket_geom = mesh_from_geometry(
            LatheGeometry.from_shell_profiles(
                [(R - 0.001, r.mouth_top), (R - 0.001, r.mouth_top + _GASKET_H)],
                [(R - wall + 0.001, r.mouth_top), (R - wall + 0.001, r.mouth_top + _GASKET_H)],
                segments=48,
            ),
            "gasket_ring",
        )
        _v(enc, gasket_geom, (0.0, 0.0, 0.0), mats["gasket"], "gasket_ring")
        # 4 diagonal external mounting ears.
        for i in range(4):
            ang = math.pi / 4.0 + i * (math.pi / 2.0)
            er = R + 0.010
            ex, ey = er * math.cos(ang), er * math.sin(ang)
            _v(enc, Box((0.020, 0.014, 0.005)), (ex, ey, 0.007), edge, f"mount_ear_{i}", (0.0, 0.0, ang))
            _v(enc, Cylinder(0.0032, 0.006), (ex, ey, 0.009), mats["dark"], f"mount_hole_{i}")
    else:
        L, W, H, wall = r.L, r.W, r.H, r.wall
        _v(enc, Box((L, W, r.floor)), (0.0, 0.0, r.floor / 2.0), shell, "floor_plate")
        _v(enc, Box((L, wall, H)), (0.0, -W / 2.0 + wall / 2.0, H / 2.0), shell, "front_wall")
        _v(enc, Box((L, wall, H)), (0.0, W / 2.0 - wall / 2.0, H / 2.0), shell, "rear_wall")
        _v(enc, Box((wall, W, H)), (-L / 2.0 + wall / 2.0, 0.0, H / 2.0), shell, "side_wall_0")
        _v(enc, Box((wall, W, H)), (L / 2.0 - wall / 2.0, 0.0, H / 2.0), shell, "side_wall_1")
        gz = r.mouth_top + _GASKET_H / 2.0
        _v(enc, Box((L - 0.02, 0.005, _GASKET_H)), (0.0, -W / 2.0 + wall / 2.0, gz), mats["gasket"], "gasket_front")
        _v(enc, Box((L - 0.02, 0.005, _GASKET_H)), (0.0, W / 2.0 - wall / 2.0, gz), mats["gasket"], "gasket_rear")
        _v(enc, Box((0.005, W - 0.02, _GASKET_H)), (-L / 2.0 + wall / 2.0, 0.0, gz), mats["gasket"], "gasket_side_0")
        _v(enc, Box((0.005, W - 0.02, _GASKET_H)), (L / 2.0 - wall / 2.0, 0.0, gz), mats["gasket"], "gasket_side_1")
        # 4 external mounting ears on the two ±X side walls.
        for i, (xs, y) in enumerate(((-1.0, -0.030), (-1.0, 0.030), (1.0, -0.030), (1.0, 0.030))):
            ex = xs * (L / 2.0 + 0.010)
            _v(enc, Box((0.020, 0.014, 0.005)), (ex, y, 0.007), edge, f"mount_ear_{i}")
            _v(enc, Cylinder(0.0032, 0.006), (ex, y, 0.009), mats["dark"], f"mount_hole_{i}")
        # flat rating label on the (flat) front wall exterior — host-conformal.
        _v(enc, Box((0.048, 0.0016, 0.016)), (-0.02, -W / 2.0, H * 0.55), mats["label"], "rating_label")
        for i in range(3):
            _v(enc, Box((0.036, 0.0018, 0.0018)), (-0.02, -W / 2.0 - 0.0009, H * 0.55 - 0.004 + i * 0.004), mats["label_dark"], f"rating_stripe_{i}")
    return enc


# ---------------------------------------------------------------------------
# Interior fit-out (Rule 1: inline non-moving visuals on the enclosure part).
# ---------------------------------------------------------------------------
def _interior_half_extents(r: ResolvedJunctionBoxConfig) -> tuple[float, float]:
    if r.is_round:
        span = (r.R - r.wall) * 0.60
        return span, span * 0.62
    return (r.L / 2.0 - r.wall - 0.004), (r.W / 2.0 - r.wall - 0.004)


def _emit_ground_lug(enc, r, mats):
    ihx, ihy = _interior_half_extents(r)
    gx, gy = -ihx * 0.6, ihy * 0.55
    z0 = r.floor
    _v(enc, Box((0.024, 0.014, 0.004)), (gx, gy, z0 + 0.002), mats["brass"], "ground_lug_plate")
    _v(enc, Cylinder(0.005, 0.003), (gx, gy, z0 + 0.0055), mats["screw_metal"], "ground_lug_screw")
    _v(enc, Box((0.016, 0.0016, 0.0012)), (gx, gy - 0.009, z0 + 0.0003), mats["label_dark"], "ground_symbol")


def _emit_terminal_strip(enc, r, mats):
    ihx, ihy = _interior_half_extents(r)
    z0 = r.floor
    bx = _clamp(2.0 * ihx * 0.82, 0.05, 0.14)
    by = _clamp(2.0 * ihy * 0.78, 0.02, 0.06)
    _v(enc, Box((bx, by, 0.006)), (0.0, 0.0, z0 + 0.003), mats["terminal"], "terminal_base")
    _v(enc, Box((bx * 0.88, 0.004, 0.0016)), (0.0, -by * 0.22, z0 + 0.0068), mats["brass"], "brass_bus_bar")
    top = z0 + 0.006
    usable = bx - 0.018
    k = r.terminal_count
    if k == 1:
        xs = [0.0]
    else:
        xs = [-usable / 2.0 + i * (usable / (k - 1)) for i in range(k)]
    for i, x in enumerate(xs):
        y = by * 0.14
        _v(enc, Cylinder(0.0042, 0.010), (x, y, top + 0.005), mats["terminal"], f"terminal_{i}_insulator")
        _v(enc, Cylinder(0.0026, 0.0022), (x, y, top + 0.0094), mats["brass"], f"terminal_{i}_cup")
        _v(enc, Cylinder(0.0015, 0.0016), (x, y, top + 0.0104), mats["dark"], f"terminal_{i}_bore")
    _emit_ground_lug(enc, r, mats)


_INTERIOR_BUILDERS = {
    "terminal_strip": _emit_terminal_strip,
    "empty_passthrough": lambda enc, r, mats: _emit_ground_lug(enc, r, mats),
}


# ---------------------------------------------------------------------------
# Cover mechanisms.
# ---------------------------------------------------------------------------
def _cover_top_labels(cover, r, mats, y0, z_top):
    """Flat warning label + stripes on the (flat) cover top — host-conformal ④."""
    _v(cover, Box((0.040, 0.016, 0.0008)), (0.0, y0, z_top + 0.0004), mats["gasket"], "cover_warning_label")
    for i in range(3):
        _v(cover, Box((0.030, 0.0018, 0.0010)), (0.0, y0 - 0.004 + i * 0.004, z_top + 0.0010), mats["label_dark"], f"cover_warning_line_{i}")


def _hinge_x_positions(r: ResolvedJunctionBoxConfig) -> tuple[float, float]:
    half_span = (2.0 * r.R) if r.is_round else r.L
    x_b = _clamp(0.28 * half_span, 0.020, 0.050)
    return (-x_b, x_b)


def _emit_hinged_cover(model, r: ResolvedJunctionBoxConfig, enc, mats):
    shell, edge, metal = mats["shell"], mats["shell_edge"], mats["screw_metal"]
    x_left, x_right = _hinge_x_positions(r)
    x_b = x_right

    # --- base hinge hardware on the enclosure (rear edge) ---
    leaf_w = 2.0 * x_b + 0.030
    _v(enc, Box((leaf_w, 0.016, 0.012)), (0.0, r.box_rear + 0.006, r.hinge_z - 0.002), edge, "base_hinge_leaf")
    for i, x in enumerate((x_left, x_right)):
        _v(enc, Cylinder(0.0040, 0.024), (x, r.hinge_y, r.hinge_z), metal, f"base_hinge_barrel_{i}", (0.0, math.pi / 2.0, 0.0))

    # --- cover part, authored in the hinge-pivot frame (pivot at part origin) ---
    cover = model.part("cover")
    if r.is_round:
        disc_r = r.R + 0.002
        _v(cover, Cylinder(disc_r, _COVER_T), (0.0, -r.hinge_y, 0.0), shell, "cover_panel")
        z_top = _COVER_T / 2.0
        _cover_top_labels(cover, r, mats, -r.hinge_y, z_top)
        # retained screws evenly around the circular lid.
        sr = r.R - 0.012
        for i in range(6):
            a = i * (math.pi / 3.0)
            sx, sy = sr * math.cos(a), -r.hinge_y + sr * math.sin(a)
            _v(cover, Cylinder(0.006, 0.0022), (sx, sy, z_top - 0.0004), metal, f"cover_screw_{i}")
    else:
        cov_w = 2.0 * r.box_rear + 0.004
        _v(cover, Box((r.L + 0.008, cov_w, _COVER_T)), (0.0, -r.hinge_y, 0.0), shell, "cover_panel")
        z_top = _COVER_T / 2.0
        _cover_top_labels(cover, r, mats, -r.hinge_y, z_top)
        for i, (sx, sy) in enumerate(
            (
                (-r.L / 2.0 + 0.014, -r.hinge_y - cov_w / 2.0 + 0.014),
                (r.L / 2.0 - 0.014, -r.hinge_y - cov_w / 2.0 + 0.014),
                (-r.L / 2.0 + 0.014, -r.hinge_y + cov_w / 2.0 - 0.014),
                (r.L / 2.0 - 0.014, -r.hinge_y + cov_w / 2.0 - 0.014),
            )
        ):
            _v(cover, Cylinder(0.006, 0.0022), (sx, sy, z_top - 0.0004), metal, f"cover_screw_{i}")

    # cover hinge leaf (panel -> pins) + 2 pins ON the pivot axis (local y=z=0).
    _v(cover, Box((2.0 * x_b + 0.024, 0.014, 0.005)), (0.0, -0.005, 0.0), edge, "cover_hinge_leaf")
    for i, x in enumerate((x_left, x_right)):
        _v(cover, Cylinder(0.0024, 0.030), (x, 0.0, 0.0), metal, f"cover_hinge_pin_{i}", (0.0, math.pi / 2.0, 0.0))

    model.articulation(
        "cover_hinge",
        ArticulationType.REVOLUTE,
        parent=enc,
        child=cover,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=0.0, upper=r.lid_open),
    )
    return cover


def _emit_screw_cover(model, r: ResolvedJunctionBoxConfig, enc, mats):
    shell, edge, metal, dark = mats["shell"], mats["shell_edge"], mats["screw_metal"], mats["dark"]
    cover = model.part("cover")
    # part frame at the mouth; panel bottom rests on the gasket top (contact).
    if r.is_round:
        _v(cover, Cylinder(r.R + 0.003, _COVER_T), (0.0, 0.0, _COVER_T / 2.0), shell, "cover_panel")
        z_top = _COVER_T
        # recessed rib ring on the lid top.
        _v(cover, Cylinder(r.R * 0.7, 0.0016), (0.0, 0.0, z_top + 0.0008), edge, "cover_rib_0")
        screw_r = r.R - 0.010
        for i in range(6):
            a = i * (math.pi / 3.0)
            sx, sy = screw_r * math.cos(a), screw_r * math.sin(a)
            _v(cover, Cylinder(0.0072, 0.0022), (sx, sy, z_top - 0.0004), edge, f"cover_screw_pad_{i}")
            _v(cover, Cylinder(0.0056, 0.0026), (sx, sy, z_top + 0.0009), metal, f"cover_screw_{i}")
            _v(cover, Box((0.010, 0.0016, 0.0006)), (sx, sy, z_top + 0.0020), dark, f"cover_screw_slot_{i}")
        _cover_top_labels(cover, r, mats, 0.0, z_top)
    else:
        _v(cover, Box((r.L + 0.008, r.W + 0.008, _COVER_T)), (0.0, 0.0, _COVER_T / 2.0), shell, "cover_panel")
        z_top = _COVER_T
        # recessed rib frame (host-conformal on the flat top).
        _v(cover, Box((r.L - 0.02, 0.004, 0.0016)), (0.0, -(r.W / 2.0 - 0.018), z_top + 0.0008), edge, "cover_rib_0")
        _v(cover, Box((r.L - 0.02, 0.004, 0.0016)), (0.0, (r.W / 2.0 - 0.018), z_top + 0.0008), edge, "cover_rib_1")
        _v(cover, Box((0.004, r.W - 0.036, 0.0016)), (-(r.L / 2.0 - 0.018), 0.0, z_top + 0.0008), edge, "cover_rib_2")
        _v(cover, Box((0.004, r.W - 0.036, 0.0016)), ((r.L / 2.0 - 0.018), 0.0, z_top + 0.0008), edge, "cover_rib_3")
        for i, (sx, sy) in enumerate(
            (
                (-r.L / 2.0 + 0.014, -r.W / 2.0 + 0.014),
                (r.L / 2.0 - 0.014, -r.W / 2.0 + 0.014),
                (-r.L / 2.0 + 0.014, r.W / 2.0 - 0.014),
                (r.L / 2.0 - 0.014, r.W / 2.0 - 0.014),
            )
        ):
            _v(cover, Cylinder(0.0072, 0.0022), (sx, sy, z_top - 0.0004), edge, f"cover_screw_pad_{i}")
            _v(cover, Cylinder(0.0056, 0.0026), (sx, sy, z_top + 0.0009), metal, f"cover_screw_{i}")
            _v(cover, Box((0.010, 0.0016, 0.0006)), (sx, sy, z_top + 0.0020), dark, f"cover_screw_slot_{i}")
        _cover_top_labels(cover, r, mats, 0.0, z_top)

    model.articulation(
        "cover_lift",
        ArticulationType.PRISMATIC,
        parent=enc,
        child=cover,
        origin=Origin(xyz=(0.0, 0.0, r.lift_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=r.lift_travel),
    )
    return cover


_LID_BUILDERS = {
    "hinged_flip": _emit_hinged_cover,
    "screw_liftoff": _emit_screw_cover,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_junction_box(
    config: JunctionBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"class": "Junction box", "domain": "Electrical_Wiring"},
    )
    mats = {
        key: model.material(f"jb_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in _palette_rgba(r.palette_style).items()
    }

    # Shared ribbed gland-nut mesh (KnobGeometry) reused across all N glands.
    ribbed_mesh = mesh_from_geometry(
        KnobGeometry(
            0.030,
            0.026,
            body_style="cylindrical",
            edge_radius=0.001,
            grip=KnobGrip(style="ribbed", count=32, depth=0.0013, width=0.0012),
        ),
        "ribbed_cable_gland_nut",
    )

    enc = _build_enclosure(model, r, mats)
    _emit_glands(enc, r, mats, ribbed_mesh)
    _INTERIOR_BUILDERS[r.interior_fitout](enc, r, mats)
    _LID_BUILDERS[r.lid_mechanism](model, r, enc, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_junction_box(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_junction_box(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_junction_box_tests(
    object_model: ArticulatedObject,
    config: JunctionBoxConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    enc = object_model.get_part("enclosure")
    cover = object_model.get_part("cover")

    # ---- Captured-hinge allowances (element-scoped). ----
    if r.lid_mechanism == "hinged_flip":
        for i in range(2):
            ctx.allow_overlap(
                cover, enc,
                elem_a=f"cover_hinge_pin_{i}", elem_b=f"base_hinge_barrel_{i}",
                reason="cover hinge pin is captured inside the base hinge barrel (pin-in-sleeve).",
            )
            ctx.allow_overlap(
                cover, enc,
                elem_a="cover_hinge_leaf", elem_b=f"base_hinge_barrel_{i}",
                reason="the cover hinge leaf wraps the base barrel at the pivot line (knuckle interleave).",
            )
        ctx.allow_overlap(
            cover, enc,
            elem_a="cover_hinge_leaf", elem_b="base_hinge_leaf",
            reason="the interleaved hinge knuckle plates meet at the pivot line.",
        )

    ctx.allow_isolated_part(
        cover,
        reason="flip-up cover opens clear of the enclosure and loses body contact",
    )

    # ---- Compiler baseline (honors the allowances above). ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    ctx.check(
        "classified as electrical junction box",
        object_model.meta.get("class") == "Junction box"
        and object_model.meta.get("domain") == "Electrical_Wiring",
        details=str(object_model.meta),
    )
    part_names = {p.name for p in object_model.parts}
    ctx.check("enclosure + cover present", {"enclosure", "cover"} <= part_names, details=str(sorted(part_names)))

    enc_names = {v.name for v in enc.visuals}

    # ③ footprint form family realized as the right primitive.
    if r.is_round:
        ctx.check("round footprint uses a LatheGeometry cylindrical wall", "cylindrical_wall" in enc_names)
    else:
        ctx.check("rectangular footprint has 4 box walls", {"front_wall", "rear_wall", "side_wall_0", "side_wall_1"} <= enc_names)

    # ① multiplicity: exactly N glands, each with its KnobGeometry ribbed nut.
    gland_nuts = [n for n in enc_names if n.startswith("gland_") and n.endswith("_ribbed_nut")]
    ctx.check(
        f"exactly N={r.gland_count} cable glands (single gland_specs loop)",
        len(gland_nuts) == r.gland_count,
        details=f"found {len(gland_nuts)} ribbed nuts: {sorted(gland_nuts)}",
    )

    # C interior fit-out.
    if r.interior_fitout == "terminal_strip":
        terms = [n for n in enc_names if n.startswith("terminal_") and n.endswith("_insulator")]
        ctx.check(
            "terminal strip populated (base + K terminals + ground lug)",
            "terminal_base" in enc_names and "ground_lug_plate" in enc_names and len(terms) == r.terminal_count,
            details=f"terminals={len(terms)} expected={r.terminal_count}",
        )
    else:
        ctx.check(
            "empty pass-through (ground lug only, no terminal_base)",
            "ground_lug_plate" in enc_names and "terminal_base" not in enc_names,
            details=str(sorted(n for n in enc_names if "terminal" in n)),
        )

    # ② lid mechanism joint topology.
    if r.lid_mechanism == "hinged_flip":
        j = object_model.get_articulation("cover_hinge")
        ctx.check(
            "cover_hinge is REVOLUTE about -X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:
        j = object_model.get_articulation("cover_lift")
        ctx.check(
            "cover_lift is PRISMATIC about +Z with real travel",
            j.articulation_type == ArticulationType.PRISMATIC
            and abs(j.axis[2]) > 0.99
            and j.motion_limits is not None
            and j.motion_limits.upper > 0.05,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} limits={j.motion_limits}",
        )

    # Closed/seated cover spans the enclosure mouth.
    ctx.expect_overlap(
        cover, enc, axes="xy",
        elem_a="cover_panel", elem_b="floor_plate",
        min_overlap=0.06,
        name="cover spans the enclosure mouth",
    )

    # ---- Dynamic motion (Rule 5): sampled overlap + one targeted pose. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    if r.lid_mechanism == "hinged_flip":
        j = object_model.get_articulation("cover_hinge")
        closed = ctx.part_element_world_aabb(cover, elem="cover_panel")
        with ctx.pose({j: r.lid_open * 0.85}):
            opened = ctx.part_element_world_aabb(cover, elem="cover_panel")
        ctx.check(
            "hinged cover opens upward",
            closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.030,
            details=f"closed_top={None if closed is None else closed[1][2]:.4f} open_top={None if opened is None else opened[1][2]:.4f}",
        )
    else:
        j = object_model.get_articulation("cover_lift")
        seated = ctx.part_world_position(cover)
        with ctx.pose({j: r.lift_travel * 0.9}):
            lifted = ctx.part_world_position(cover)
        ctx.check(
            "screw cover lifts straight up (+Z)",
            seated is not None and lifted is not None and lifted[2] > seated[2] + 0.030,
            details=f"seated_z={None if seated is None else seated[2]:.4f} lifted_z={None if lifted is None else lifted[2]:.4f}",
        )

    # slot_choices recorded.
    ctx.check(
        "slot_choices recorded (footprint/lid/interior/gland_count)",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "JunctionBoxConfig",
    "ResolvedJunctionBoxConfig",
    "build_junction_box",
    "build_seeded_junction_box",
    "config_from_seed",
    "resolve_config",
    "run_junction_box_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
