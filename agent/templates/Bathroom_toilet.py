# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Procedural template: ceramic TOILET fixture.
#
# Axes (sourced from the bathroom/toilet workbench variants in articraft_data):
#   - body/mount:  one_piece_floor / two_piece / wall_hung   (Slot A, 3)
#   - flush:       dual_button(PRISMATIC) / side_lever(REVOLUTE) / pull_chain(PRISMATIC)
#                  (Slot B, compatibility-gated to the body)
#   - seat:        ring_lid / ring_only                       (Slot C, 2)
#   - palette:     white / ivory / gray
#
# Geometry conventions (meters, Z-up): +X = front (seat/lid free edge), -X = rear
# (tank/wall), +Z = up, floor at z=0. The seat ring + lid hinge on the lateral Y
# axis at the rear of the bowl rim.
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
    CylinderGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

BodyModule = Literal["one_piece_floor", "two_piece", "wall_hung"]
FlushModule = Literal["dual_button", "side_lever", "pull_chain"]
SeatModule = Literal["ring_lid", "ring_only"]
PaletteTheme = Literal[
    "white", "ivory", "gray", "gold", "matte_black", "rose_gold", "navy", "sage", "copper"
]

BODY_MODULES: tuple[BodyModule, ...] = ("one_piece_floor", "two_piece", "wall_hung")
FLUSH_MODULES: tuple[FlushModule, ...] = ("dual_button", "side_lever", "pull_chain")
SEAT_MODULES: tuple[SeatModule, ...] = ("ring_lid", "ring_only")
PALETTE_THEMES: tuple[PaletteTheme, ...] = (
    "white",
    "ivory",
    "gray",
    "gold",
    "matte_black",
    "rose_gold",
    "navy",
    "sage",
    "copper",
)

# flush options allowed per body (wall_hung uses a wall plate -> button only)
_FLUSH_BY_BODY: dict[BodyModule, tuple[FlushModule, ...]] = {
    "one_piece_floor": ("dual_button", "side_lever", "pull_chain"),
    "two_piece": ("dual_button", "side_lever", "pull_chain"),
    "wall_hung": ("dual_button",),
}

PALETTES: dict[PaletteTheme, dict[str, tuple[float, float, float, float]]] = {
    # Each palette carries 3 coordinated tones so the parts read as separate:
    #   ceramic = bowl/tank, seat = seat ring + lid (distinct), chrome = metal trim.
    "white": {
        "ceramic": (0.95, 0.96, 0.97, 1.0),
        "seat": (0.85, 0.88, 0.93, 1.0),
        "chrome": (0.55, 0.57, 0.62, 1.0),
    },
    "ivory": {
        "ceramic": (0.93, 0.90, 0.82, 1.0),
        "seat": (0.83, 0.79, 0.69, 1.0),
        "chrome": (0.56, 0.55, 0.52, 1.0),
    },
    "gray": {
        "ceramic": (0.78, 0.80, 0.82, 1.0),
        "seat": (0.59, 0.62, 0.66, 1.0),
        "chrome": (0.42, 0.44, 0.48, 1.0),
    },
    # luxury / designer finishes — body in the finish color, lighter seat, dark metal
    "gold": {
        "ceramic": (0.85, 0.68, 0.27, 1.0),
        "seat": (0.93, 0.81, 0.43, 1.0),
        "chrome": (0.52, 0.40, 0.14, 1.0),
    },
    "matte_black": {
        "ceramic": (0.09, 0.09, 0.10, 1.0),
        "seat": (0.22, 0.22, 0.24, 1.0),
        "chrome": (0.52, 0.52, 0.56, 1.0),
    },
    "rose_gold": {
        "ceramic": (0.86, 0.64, 0.60, 1.0),
        "seat": (0.94, 0.81, 0.78, 1.0),
        "chrome": (0.66, 0.45, 0.40, 1.0),
    },
    "navy": {
        "ceramic": (0.14, 0.20, 0.36, 1.0),
        "seat": (0.29, 0.37, 0.55, 1.0),
        "chrome": (0.78, 0.80, 0.85, 1.0),
    },
    "sage": {
        "ceramic": (0.55, 0.64, 0.51, 1.0),
        "seat": (0.75, 0.81, 0.71, 1.0),
        "chrome": (0.45, 0.48, 0.44, 1.0),
    },
    "copper": {
        "ceramic": (0.72, 0.45, 0.30, 1.0),
        "seat": (0.87, 0.63, 0.49, 1.0),
        "chrome": (0.45, 0.29, 0.20, 1.0),
    },
}

# ---- Base dimensions (ported from the one-piece parent) ---------------------
BOWL_WIDTH = 0.37
BOWL_FRONT_X = 0.34
BOWL_REAR_X = -0.16
TANK_FRONT_X = -0.16
TANK_REAR_X = -0.34
TANK_WIDTH = 0.36
TANK_TOP_Z = 0.80
BOWL_RIM_Z = 0.40
HINGE_X = -0.13
HINGE_Z = BOWL_RIM_Z
SEAT_FRONT_X = 0.33
SEAT_HALF_LEN = (SEAT_FRONT_X - HINGE_X) / 2.0
SEAT_MID_X = (SEAT_FRONT_X + HINGE_X) / 2.0
SEAT_HALF_W = 0.165
BUTTON_R = 0.034
# Dual-flush hardware (unscaled, like the button cylinders themselves)
FLUSH_PLATE_R = 0.052
FLUSH_PLATE_REAR_GAP = 0.008  # plate edge to tank rear face
BUTTON_H = 0.018
# Required clearance between the swept seat-ring/lid arc and the raised buttons
SEAT_BUTTON_CLEAR = 0.006
SEAT_OPEN_FULL = math.radians(100.0)
SEAT_OPEN_MIN = math.radians(90.0)


def _clampf(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ToiletConfig:
    body_module: BodyModule = "one_piece_floor"
    flush_module: FlushModule = "dual_button"
    seat_module: SeatModule = "ring_lid"
    palette_theme: PaletteTheme = "white"
    width_scale: float = 1.0
    height_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedToiletConfig:
    body_module: BodyModule
    flush_module: FlushModule
    seat_module: SeatModule
    palette_theme: PaletteTheme
    width_scale: float
    height_scale: float
    tank_top_z: float  # flush mount height for this body
    tank_center_x: float  # dual-button mount x (tank top center)
    tank_front_x: float  # tank/carrier front face x (lever/chain mount)
    tank_side_y: float  # tank side y (lever/chain offset)
    tank_half_w: float  # tank +Y outer side face y (side-mounted flush)
    bowl_rise: float  # how far the bowl rim is raised (wall_hung)
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> ToiletConfig:
    rng = random.Random(seed)
    body = rng.choice(BODY_MODULES)
    flush = rng.choice(_FLUSH_BY_BODY[body])
    seat = rng.choice(SEAT_MODULES)
    palette = rng.choice(PALETTE_THEMES)
    return ToiletConfig(
        body_module=body,
        flush_module=flush,
        seat_module=seat,
        palette_theme=palette,
        width_scale=round(rng.uniform(0.92, 1.10), 4),
        height_scale=round(rng.uniform(0.92, 1.10), 4),
    )


def resolve_config(config: ToiletConfig) -> ResolvedToiletConfig:
    body = config.body_module if config.body_module in BODY_MODULES else "one_piece_floor"
    flush = config.flush_module
    if flush not in _FLUSH_BY_BODY[body]:
        flush = _FLUSH_BY_BODY[body][0]
    seat = config.seat_module if config.seat_module in SEAT_MODULES else "ring_lid"
    palette_theme = config.palette_theme if config.palette_theme in PALETTES else "white"
    tank_top = {"one_piece_floor": 0.80, "two_piece": 0.72, "wall_hung": 1.00}[body]
    ws = _clampf(config.width_scale, 0.85, 1.18)
    # Dual-button mount x: anchor the escutcheon to the tank REAR face rather
    # than the tank middle, so the raised seat ring/lid arc (hinged at
    # HINGE_X=-0.13, reach 2*SEAT_HALF_LEN) clears the raised buttons. The
    # plate radius + rear gap are unscaled hardware dims while the rear face
    # sits at tank_rear*width_scale, hence the /ws term.
    tank_rear = {"one_piece_floor": -0.34, "two_piece": -0.40, "wall_hung": -0.36}[body]
    tank_center = tank_rear + (FLUSH_PLATE_R + FLUSH_PLATE_REAR_GAP) / ws
    tank_front = {"one_piece_floor": -0.16, "two_piece": -0.16, "wall_hung": -0.16}[body]
    tank_side = {"one_piece_floor": 0.16, "two_piece": 0.17, "wall_hung": 0.18}[body]
    tank_half_w = {"one_piece_floor": 0.18, "two_piece": 0.20, "wall_hung": 0.22}[body]
    bowl_rise = 0.0
    return ResolvedToiletConfig(
        body_module=body,
        flush_module=flush,
        seat_module=seat,
        palette_theme=palette_theme,
        width_scale=ws,
        height_scale=_clampf(config.height_scale, 0.85, 1.18),
        tank_top_z=tank_top,
        tank_center_x=tank_center,
        tank_front_x=tank_front,
        tank_side_y=tank_side,
        tank_half_w=tank_half_w,
        bowl_rise=bowl_rise,
        palette=dict(PALETTES[palette_theme]),
    )


# ---------------------------------------------------------------------------
# Geometry helpers (ported from the one-piece parent)
# ---------------------------------------------------------------------------
# Dimensions are scaled at BUILD time (coordinate scaling: X,Y by wf, Z by hf)
# — robust, unlike a post-hoc non-uniform transformGeometry which can break the
# mesh into non-manifold pieces.
def _loft_x(sections, wf: float, hf: float) -> cq.Workplane:
    wp = cq.Workplane("YZ")
    prev = 0.0
    for i, s in enumerate(sections):
        x = s[1] * wf
        off = x if i == 0 else x - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        if s[0] == "ellipse":
            wp = wp.ellipse(s[2] * wf, s[3] * hf)
        else:
            wp = wp.rect(s[2] * wf, s[3] * hf)
        prev = x
    return wp.loft(ruled=False)


def _bowl(bottom_z: float, wf: float, hf: float) -> cq.Workplane:
    """Skirted bowl lofted front->rear; slab spans z in [bottom_z, bottom_z+0.40]."""
    bowl = _loft_x(
        [
            ("rect", BOWL_FRONT_X, 0.13, 0.40),
            ("rect", BOWL_FRONT_X - 0.05, 0.26, 0.40),
            ("rect", 0.18, 0.345, 0.40),
            ("rect", 0.02, BOWL_WIDTH, 0.40),
            ("rect", BOWL_REAR_X + 0.04, BOWL_WIDTH, 0.40),
        ],
        wf,
        hf,
    )
    return bowl.translate((0.0, 0.0, (bottom_z + 0.20) * hf))


def _basin_cut(wf: float, hf: float, rise: float = 0.0) -> cq.Workplane:
    # Recess opens at the (possibly raised) bowl rim so it never severs the bowl.
    return (
        cq.Workplane("XY")
        .workplane(offset=(BOWL_RIM_Z + rise + 0.001) * hf)
        .center(0.10 * wf, 0.0)
        .ellipse(0.135 * wf, 0.115 * wf)
        .workplane(offset=-0.18 * hf)
        .center(-0.02 * wf, 0.0)
        .ellipse(0.075 * wf, 0.065 * wf)
        .loft(ruled=False)
    )


def _hinge_boss(wf: float, hf: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center((HINGE_X + 0.005) * wf, 0.0)
        .rect(0.05 * wf, 0.24 * wf)
        .extrude(0.452 * hf)
    )


def _box(x0, x1, y_w, z0, z1, wf: float = 1.0, hf: float = 1.0) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .center((x0 + x1) / 2.0 * wf, 0.0)
        .rect((x1 - x0) * wf, y_w * wf)
        .extrude((z1 - z0) * hf)
        .translate((0.0, 0.0, z0 * hf))
    )


def _sc(p, wf: float, hf: float) -> tuple[float, float, float]:
    return (p[0] * wf, p[1] * wf, p[2] * hf)


def _clean(wp: cq.Workplane) -> cq.Workplane:
    """Merge coplanar faces / coincident seams so the tessellation shares
    vertices (avoids spurious disconnected-mesh-island findings)."""
    try:
        return wp.clean()
    except Exception:
        return wp


def _seat_ring_mesh(wf: float, hf: float):
    outer = cq.Workplane("XY").ellipse(SEAT_HALF_LEN * wf, SEAT_HALF_W * wf).extrude(0.022 * hf)
    hole = (
        cq.Workplane("XY")
        .workplane(offset=-0.002 * hf)
        .ellipse((SEAT_HALF_LEN - 0.045) * wf, (SEAT_HALF_W - 0.045) * wf)
        .extrude(0.030 * hf)
    )
    ring = outer.cut(hole)
    try:
        ring = ring.edges("|Z").fillet(0.006 * wf)
    except Exception:
        pass
    return mesh_from_cadquery(ring, "seat_ring_shell")


def _lid_mesh(wf: float, hf: float):
    lid = (
        cq.Workplane("XY")
        .ellipse((SEAT_HALF_LEN + 0.004) * wf, (SEAT_HALF_W + 0.004) * wf)
        .extrude(0.020 * hf)
    )
    try:
        lid = lid.edges("|Z").fillet(0.010 * wf)
        lid = lid.faces(">Z").fillet(0.006 * wf)
    except Exception:
        pass
    return mesh_from_cadquery(lid, "lid_shell")


# ---------------------------------------------------------------------------
# Body
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedToiletConfig, prefix: str = ""):
    P = r.palette
    ceramic = model.material(f"{prefix}ceramic", rgba=P["ceramic"])
    body = model.part(f"{prefix}body")
    bm = r.body_module
    wf, hf = r.width_scale, r.height_scale

    if bm == "wall_hung":
        # Floor bowl + a tall, flat WALL-CARRIER panel (concealed cistern) joined
        # by a shoulder loft — same clean construction as one_piece (which passes
        # the mesh checks), but the cistern is a tall thin wall panel.
        bowl = _bowl(0.0, wf, hf)
        panel = _box(-0.36, -0.16, 0.44, 0.0, 1.00, wf, hf)
        shoulder = _loft_x(
            [("rect", BOWL_REAR_X + 0.04, BOWL_WIDTH, 0.40), ("rect", -0.16, 0.44, 0.40)],
            wf,
            hf,
        ).translate((0.0, 0.0, 0.20 * hf))
        shell = bowl.union(shoulder).union(panel).union(_hinge_boss(wf, hf))
        try:
            shell = shell.edges("|Z").fillet(0.025 * wf)
        except Exception:
            pass
        shell = shell.cut(_basin_cut(wf, hf, r.bowl_rise))
        body.visual(mesh_from_cadquery(shell, "body_shell"), material=ceramic, name="body_shell", material_class_id="ceramic.porcelain_glazed_plain")
    elif bm == "two_piece":
        # Floor bowl + a rear ceramic pedestal (floor->shelf) that grounds and
        # supports the SEPARATE close-coupled tank, + a visible tank lid seam.
        bowl = (
            _bowl(0.0, wf, hf)
            .union(_hinge_boss(wf, hf))
            .union(_box(-0.40, -0.10, 0.34, 0.0, 0.42, wf, hf))
        )
        try:
            bowl = bowl.edges("|Z").fillet(0.025 * wf)
        except Exception:
            pass
        bowl = bowl.cut(_basin_cut(wf, hf, r.bowl_rise))
        body.visual(mesh_from_cadquery(bowl, "body_shell"), material=ceramic, name="body_shell", material_class_id="ceramic.porcelain_glazed_plain")
        # Tank front sits BEHIND the seat hinge (x=-0.16 < hinge -0.13) so the
        # close-coupled cistern never overlaps the seat ring/lid.
        tank = _box(-0.40, -0.16, 0.40, 0.40, 0.70, wf, hf)
        try:
            tank = tank.edges("|Z").fillet(0.03 * wf)
        except Exception:
            pass
        body.visual(mesh_from_cadquery(tank, "tank_shell"), material=ceramic, name="tank_shell", material_class_id="ceramic.porcelain_glazed_plain")
        body.visual(
            Box((0.26 * wf, 0.42 * wf, 0.03 * hf)),
            origin=Origin(xyz=_sc((-0.28, 0.0, 0.715), wf, hf)),
            material=ceramic,
            name="tank_lid", material_class_id="ceramic.porcelain_glazed_plain",
        )
    else:  # one_piece_floor
        bowl = _bowl(0.0, wf, hf)
        tank = _box(TANK_REAR_X, TANK_FRONT_X, TANK_WIDTH, 0.40, TANK_TOP_Z, wf, hf)
        shoulder = _loft_x(
            [
                ("rect", BOWL_REAR_X + 0.04, BOWL_WIDTH, 0.40),
                ("rect", TANK_FRONT_X, TANK_WIDTH, 0.40),
            ],
            wf,
            hf,
        ).translate((0.0, 0.0, 0.20 * hf))
        shell = bowl.union(shoulder).union(tank).union(_hinge_boss(wf, hf))
        try:
            shell = shell.edges("|Z").fillet(0.03 * wf)
        except Exception:
            pass
        shell = shell.cut(_basin_cut(wf, hf, r.bowl_rise))
        body.visual(mesh_from_cadquery(shell, "body_shell"), material=ceramic, name="body_shell", material_class_id="ceramic.porcelain_glazed_plain")

    # Ceramic hinge barrel along Y on the bowl rim: real hardware at the seat /
    # lid hinge origin (origin-distance gate) that the ring + lid rears ride.
    body.visual(
        Cylinder(0.022 * hf, 0.30 * wf),
        origin=Origin(
            xyz=_sc((HINGE_X, 0.0, HINGE_Z + r.bowl_rise), wf, hf), rpy=(math.pi / 2.0, 0.0, 0.0)
        ),
        material=ceramic,
        name="hinge_barrel", material_class_id="ceramic.porcelain_glazed_plain",
    )
    body.inertial = Inertial.from_geometry(
        Box((0.68 * wf, 0.37 * wf, 0.80 * hf)),
        mass=28.0,
        origin=Origin(xyz=_sc((0.0, 0.0, 0.40), wf, hf)),
    )
    return body


# ---------------------------------------------------------------------------
# Seat opening limit (derived from the swept arc vs the dual-flush buttons)
# ---------------------------------------------------------------------------
def _dual_button_clearance(r: ResolvedToiletConfig, theta_max: float) -> float:
    """Min XZ-plane clearance (negative = penetration) between the seat
    ring/lid slabs swept over [0, theta_max] about the -Y hinge and the two
    raised dual-flush buttons, using the exact resolved build dims. The
    buttons sit near y=0 and both slabs are much wider in Y, so the 2D
    side-view analysis is exact for this pair."""
    wf, hf = r.width_scale, r.height_scale
    cx = r.tank_center_x * wf
    base = (r.tank_top_z + 0.007) * hf  # button base = prismatic joint plane
    rects = [
        (cx - 0.042, cx + 0.010, base, base + BUTTON_H),  # full-flush button
        (cx + 0.007, cx + 0.041, base, base + BUTTON_H),  # half-flush button
    ]
    # (hinge_xz, slab local x span, slab thickness) — slab local z in [0, t]
    slabs = [
        (
            (HINGE_X * wf, (HINGE_Z + r.bowl_rise) * hf),
            0.0,
            2.0 * SEAT_HALF_LEN * wf,
            0.022 * hf,
        )
    ]
    if r.seat_module == "ring_lid":
        slabs.append(
            (
                (HINGE_X * wf, (HINGE_Z + r.bowl_rise + 0.016) * hf),
                -0.004 * wf,
                (2.0 * SEAT_HALF_LEN + 0.004) * wf,
                0.020 * hf,
            )
        )
    pts: list[tuple[float, float]] = []
    for x0, x1, z0, z1 in rects:
        for i in range(13):
            f = i / 12.0
            xs, zs = x0 + (x1 - x0) * f, z0 + (z1 - z0) * f
            pts.extend([(xs, z0), (xs, z1), (x0, zs), (x1, zs)])
    best = math.inf
    for (hx, hz), x0, x1, t in slabs:
        for k in range(121):
            th = theta_max * k / 120.0
            ct, st = math.cos(th), math.sin(th)
            for px, pz in pts:
                dx, dz = px - hx, pz - hz
                xl = dx * ct + dz * st  # slab-local coords of the button point
                zl = -dx * st + dz * ct
                gx = max(x0 - xl, 0.0, xl - x1)
                gz = max(-zl, 0.0, zl - t)
                if gx == 0.0 and gz == 0.0:
                    d = -min(xl - x0, x1 - xl, zl, t - zl)
                else:
                    d = math.hypot(gx, gz)
                if d < best:
                    best = d
    return best


def _seat_open_upper(r: ResolvedToiletConfig) -> float:
    """Seat ring/lid opening limit. 100 deg when nothing sits in the swept
    arc; with a dual button on the tank top, the largest angle in
    [90, 100] deg whose swept ring/lid slab still clears the raised buttons
    by >= SEAT_BUTTON_CLEAR (clearance shrinks monotonically with angle)."""
    if r.flush_module != "dual_button":
        return SEAT_OPEN_FULL
    if _dual_button_clearance(r, SEAT_OPEN_FULL) >= SEAT_BUTTON_CLEAR:
        return SEAT_OPEN_FULL
    lo, hi = SEAT_OPEN_MIN, SEAT_OPEN_FULL
    for _ in range(20):
        mid = 0.5 * (lo + hi)
        if _dual_button_clearance(r, mid) >= SEAT_BUTTON_CLEAR:
            lo = mid
        else:
            hi = mid
    return lo


# ---------------------------------------------------------------------------
# Seat (ring + optional lid)
# ---------------------------------------------------------------------------
def _build_seat(model: ArticulatedObject, r: ResolvedToiletConfig, body, prefix: str = ""):
    # Seat ring + lid get their own coordinated tone (distinct from the bowl/tank
    # ceramic) so the articulated parts read as separate pieces.
    seat_mat = model.material(f"{prefix}seat", rgba=r.palette["seat"])
    wf, hf = r.width_scale, r.height_scale
    open_upper = _seat_open_upper(r)
    seat = model.part(f"{prefix}seat_ring")
    seat.visual(
        _seat_ring_mesh(wf, hf),
        origin=Origin(xyz=_sc((SEAT_MID_X - HINGE_X, 0.0, 0.0), wf, hf)),
        material=seat_mat,
        name="seat_ring_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    seat.inertial = Inertial.from_geometry(
        Box((2.0 * SEAT_HALF_LEN * wf, 2.0 * SEAT_HALF_W * wf, 0.022 * hf)),
        mass=0.9,
        origin=Origin(xyz=_sc((SEAT_MID_X - HINGE_X, 0.0, 0.011), wf, hf)),
    )
    model.articulation(
        f"{prefix}body_to_seat_ring",
        ArticulationType.REVOLUTE,
        parent=body,
        child=seat,
        origin=Origin(xyz=_sc((HINGE_X, 0.0, HINGE_Z + r.bowl_rise), wf, hf)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=open_upper),
    )
    if r.seat_module == "ring_lid":
        lid = model.part(f"{prefix}seat_lid")
        lid.visual(
            _lid_mesh(wf, hf),
            origin=Origin(xyz=_sc((SEAT_MID_X - HINGE_X, 0.0, 0.0), wf, hf)),
            material=seat_mat,
            name="lid_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        lid.inertial = Inertial.from_geometry(
            Box((2.0 * SEAT_HALF_LEN * wf, 2.0 * SEAT_HALF_W * wf, 0.020 * hf)),
            mass=0.8,
            origin=Origin(xyz=_sc((SEAT_MID_X - HINGE_X, 0.0, 0.010), wf, hf)),
        )
        model.articulation(
            f"{prefix}body_to_seat_lid",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lid,
            # Hinge a touch above the ring so the lid rests on (overlaps) it.
            origin=Origin(xyz=_sc((HINGE_X, 0.0, HINGE_Z + r.bowl_rise + 0.016), wf, hf)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=open_upper),
        )


# ---------------------------------------------------------------------------
# Flush control
# ---------------------------------------------------------------------------
def _build_flush(model: ArticulatedObject, r: ResolvedToiletConfig, body, prefix: str = ""):
    chrome = model.material(f"{prefix}chrome", rgba=r.palette["chrome"])
    top_z = r.tank_top_z
    wf, hf = r.width_scale, r.height_scale
    fm = r.flush_module
    if fm == "dual_button":
        # Refined dual-flush: an oval chrome escutcheon recessed in the tank top
        # (static) carrying two RAISED buttons (large = full flush, small = half).
        # The buttons start well proud of the plate and press only a few mm, so
        # they stay clearly visible when actuated.
        plate_z = top_z + 0.004  # bottom sits ~3mm into the tank top -> fused
        body.visual(
            mesh_from_geometry(
                CylinderGeometry(FLUSH_PLATE_R, 0.014, radial_segments=48), "flush_plate"
            ),
            origin=Origin(xyz=_sc((r.tank_center_x, 0.0, plate_z), wf, hf)),
            material=chrome,
            name="flush_plate", material_class_id="metal.chrome_polished",
        )
        button = model.part(f"{prefix}flush_button")
        # two buttons overlapping at the base so the part is one connected island
        button.visual(
            mesh_from_geometry(
                CylinderGeometry(0.026, BUTTON_H, radial_segments=40), "flush_button_full"
            ),
            origin=Origin(xyz=(-0.016, 0.0, BUTTON_H / 2.0)),
            material=chrome,
            name="flush_button_full", material_class_id="metal.chrome_polished",
        )
        button.visual(
            mesh_from_geometry(
                CylinderGeometry(0.017, BUTTON_H, radial_segments=36), "flush_button_half"
            ),
            origin=Origin(xyz=(0.024, 0.0, BUTTON_H / 2.0)),
            material=chrome,
            name="flush_button_half", material_class_id="metal.chrome_polished",
        )
        button.inertial = Inertial.from_geometry(
            Cylinder(0.026, BUTTON_H), mass=0.03, origin=Origin(xyz=(0.0, 0.0, BUTTON_H / 2.0))
        )
        model.articulation(
            f"{prefix}body_to_flush_button",
            ArticulationType.PRISMATIC,
            parent=body,
            child=button,
            origin=Origin(xyz=_sc((r.tank_center_x, 0.0, top_z + 0.007), wf, hf)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=15.0, velocity=0.05, lower=0.0, upper=0.006),
        )
    elif fm == "side_lever":
        # Refined trip lever on the tank SIDE (+Y) face near the front-top:
        # an escutcheon base plate (static) + a hub + a flat paddle handle that
        # rotates DOWN about the fore-aft (X) axis with a rounded grip at the tip.
        lx = r.tank_front_x - 0.05
        lz = top_z - 0.08
        # y-width spans from inside the tank wall to outside so it stays fused to
        # the body across the width_scale range (the tank face scales with wf).
        body.visual(
            Box((0.10, 0.050, 0.11)),
            origin=Origin(xyz=_sc((lx, r.tank_half_w + 0.010, lz), wf, hf)),
            material=chrome,
            name="flush_lever_plate", material_class_id="metal.chrome_polished",
        )
        lever = model.part(f"{prefix}flush_lever")
        lever.visual(
            Cylinder(0.016, 0.05),
            origin=Origin(xyz=(0.0, 0.025, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=chrome,
            name="lever_hub", material_class_id="metal.chrome_polished",
        )
        lever.visual(
            Box((0.05, 0.11, 0.020)),
            origin=Origin(xyz=(0.01, 0.095, 0.0)),
            material=chrome,
            name="lever_paddle", material_class_id="metal.chrome_polished",
        )
        lever.visual(
            Cylinder(0.020, 0.03),
            origin=Origin(xyz=(0.01, 0.155, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=chrome,
            name="lever_grip", material_class_id="metal.chrome_polished",
        )
        lever.inertial = Inertial.from_geometry(
            Box((0.05, 0.18, 0.04)), mass=0.06, origin=Origin(xyz=(0.01, 0.09, 0.0))
        )
        model.articulation(
            f"{prefix}body_to_flush_lever",
            ArticulationType.REVOLUTE,
            parent=body,
            child=lever,
            origin=Origin(xyz=_sc((lx, r.tank_half_w, lz), wf, hf)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=0.45),
        )
    else:  # pull_chain
        # Refined pull-chain on the tank SIDE (+Y) face near the front-top: a wall
        # bracket (static) + a short run of chain links + a pull grip; pulls down.
        px = r.tank_front_x - 0.04
        pz = top_z - 0.03
        # y-width spans from inside the tank wall to past the hanging chain so it
        # stays fused to the body across the width_scale range.
        # The bracket is a GUIDE the rod slides through: the rod spans from above
        # the joint origin down past the grip, so across the whole pull range its
        # upper section always remains inside the bracket (never floats off).
        body.visual(
            Box((0.045, 0.060, 0.075)),
            origin=Origin(xyz=_sc((px, r.tank_half_w + 0.010, pz), wf, hf)),
            material=chrome,
            name="pull_chain_bracket", material_class_id="metal.chrome_polished",
        )
        pull = model.part(f"{prefix}pull_handle")
        # Continuous thin rod (passes through the bracket guide) + wider link bumps
        # for the chain look + a grip; all coaxial and overlapping -> one island.
        pull.visual(
            Cylinder(0.005, 0.20),
            origin=Origin(xyz=(0.0, 0.0, -0.070)),
            material=chrome,
            name="chain_rod", material_class_id="metal.chrome_polished",
        )
        for i in range(4):
            pull.visual(
                Cylinder(0.010, 0.012),
                origin=Origin(xyz=(0.0, 0.0, -0.022 - i * 0.030)),
                material=chrome,
                name=f"chain_link_{i}", material_class_id="metal.chrome_polished",
            )
        pull.visual(
            Cylinder(0.018, 0.055),
            origin=Origin(xyz=(0.0, 0.0, -0.180)),
            material=chrome,
            name="chain_grip", material_class_id="metal.chrome_polished",
        )
        pull.inertial = Inertial.from_geometry(
            Cylinder(0.018, 0.24), mass=0.05, origin=Origin(xyz=(0.0, 0.0, -0.09))
        )
        model.articulation(
            f"{prefix}body_to_pull_chain",
            ArticulationType.PRISMATIC,
            parent=body,
            child=pull,
            origin=Origin(xyz=_sc((px, r.tank_half_w + 0.020, pz), wf, hf)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=10.0, velocity=0.3, lower=0.0, upper=0.04),
        )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_toilet(config: ToiletConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="toilet", assets=assets)
    body = _build_body(model, r)
    _build_seat(model, r, body)
    _build_flush(model, r, body)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_toilet(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_toilet(config_from_seed(seed), assets=assets)


def build_toilet_fixture(
    model: ArticulatedObject,
    config: ToiletConfig,
    *,
    prefix: str,
    mount_parent,
    mount_origin: Origin,
) -> tuple:
    """Build a toilet fixture (body + seat/lid + flush) INTO an existing model
    under the given name `prefix`, FIXED-mounted to `mount_parent` at
    `mount_origin`. Returns (body_part, resolved_config). Used to drop a toilet
    into each stall of a composite block (e.g. furnished_public_toilet)."""
    r = resolve_config(config)
    body = _build_body(model, r, prefix=prefix)
    _build_seat(model, r, body, prefix=prefix)
    _build_flush(model, r, body, prefix=prefix)
    model.articulation(
        f"{prefix}mount",
        ArticulationType.FIXED,
        parent=mount_parent,
        child=body,
        origin=mount_origin,
    )
    return body, r


def slot_choices_for_config(r: ResolvedToiletConfig) -> list[tuple[str, str]]:
    return [
        ("body", r.body_module),
        ("flush", r.flush_module),
        ("seat", r.seat_module),
        ("palette", r.palette_theme),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_toilet_tests(object_model: ArticulatedObject, config: ToiletConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    names = {p.name for p in object_model.parts}

    ctx.check("body_present", "body" in names, "missing body")
    ctx.check("seat_ring_present", "seat_ring" in names, "missing seat_ring")

    sr = object_model.get_articulation("body_to_seat_ring")
    ctx.check(
        "seat_ring_revolute_y",
        sr.articulation_type == ArticulationType.REVOLUTE
        and abs(sr.axis[1]) > 0.99
        and abs(sr.motion_limits.lower) < 1e-9,
        "seat ring must be a lateral revolute opening from closed",
    )
    if r.seat_module == "ring_lid":
        ctx.check("lid_present", "seat_lid" in names, "ring_lid must have a lid")
        ld = object_model.get_articulation("body_to_seat_lid")
        ctx.check(
            "lid_revolute_y",
            ld.articulation_type == ArticulationType.REVOLUTE and abs(ld.axis[1]) > 0.99,
            "lid revolute Y",
        )
    else:
        ctx.check("no_lid", "seat_lid" not in names, "ring_only must not have a lid")

    # flush joint type matches the module
    fm = r.flush_module
    if fm == "dual_button":
        fj = object_model.get_articulation("body_to_flush_button")
        ctx.check(
            "flush_prismatic",
            fj.articulation_type == ArticulationType.PRISMATIC,
            "dual_button must be prismatic",
        )
        ctx.allow_overlap(
            object_model.get_part("flush_button"),
            body,
            reason="Flush button seats into the tank-top recess; on-axis press.",
        )
    elif fm == "side_lever":
        fj = object_model.get_articulation("body_to_flush_lever")
        ctx.check(
            "flush_revolute",
            fj.articulation_type == ArticulationType.REVOLUTE,
            "side_lever must be revolute",
        )
        ctx.allow_overlap(
            object_model.get_part("flush_lever"),
            body,
            reason="Lever pivot boss embeds into the tank side; on the hinge axis.",
        )
    else:
        fj = object_model.get_articulation("body_to_pull_chain")
        ctx.check(
            "flush_prismatic",
            fj.articulation_type == ArticulationType.PRISMATIC,
            "pull_chain must be prismatic",
        )
        ctx.allow_overlap(
            object_model.get_part("pull_handle"),
            body,
            reason="Pull rod seats into the tank-front guide; on-axis pull.",
        )

    # seat ring + lid rear ride the bowl-rim hinge barrel/boss (pose-invariant)
    ctx.allow_overlap(
        object_model.get_part("seat_ring"),
        body,
        reason="Seat ring rear rides the bowl-rim hinge barrel/boss; pose-invariant at the hinge.",
    )
    if r.seat_module == "ring_lid":
        ctx.allow_overlap(
            object_model.get_part("seat_lid"),
            body,
            reason="Closed lid rests on the rim / hinge barrel; pose-invariant at the hinge.",
        )
        ctx.allow_overlap(
            object_model.get_part("seat_lid"),
            object_model.get_part("seat_ring"),
            reason="Closed lid stacks flush on the seat ring.",
        )

    return ctx.report()


__all__ = [
    "ToiletConfig",
    "ResolvedToiletConfig",
    "config_from_seed",
    "resolve_config",
    "build_toilet",
    "build_seeded_toilet",
    "slot_choices_for_seed",
    "run_toilet_tests",
]
