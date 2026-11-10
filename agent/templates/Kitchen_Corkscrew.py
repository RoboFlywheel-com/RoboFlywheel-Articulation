# SPDX-License-Identifier: Apache-2.0

"""Wine corkscrew (winged "butterfly" / direct-pull T-handle) modular template.

NOTE on the slug name: ``corkscrew`` here = a **wine corkscrew** (a helical worm
bottle opener), NOT a beer bottle opener (lever cap-pryer, no worm), NOT a
waiter's friend (folding lever wine key), NOT an electric / lever-arm opener.
The defining identity is a real **helical worm** (true ``cq.Wire.makeHelix``
sweep) that the user spins CONTINUOUSLY into the cork, plus a feed mechanism
that drives the spindle DOWN (PRISMATIC) and extracts the cork.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Corkscrew.md`` and the
``picture/Kitchen/Corkscrew`` 5-star sample pool (1 parent + 7 slot-fork
variants), all synced under ``data/records/``.

Coordinate convention (unified across all 8 samples, no family split): the
object stands upright; the hollow bell skirt grounds at world z=0; +Z is up =
the worm / spindle axis; wing pivots are mirrored about Y (axis = (0, +/-1, 0));
the T-bar lies along X; the spindle descends along (0, 0, -1) PRISMATIC; the
worm and foil cutter spin CONTINUOUS about (0, 0, +1).

Structure (pattern = ``parallel_children``): a single fixed root ``body_frame``
(bell skirt + twin plates + legs; winged adds rivet bosses, direct_pull adds a
top bridge + shaft bore). Shared by every candidate: ``rack_spindle`` on a
``spindle_travel`` PRISMATIC, and ``t_handle_worm`` on a ``worm_spin``
CONTINUOUS parented to the spindle. Four named module axes:

  * ``mechanism`` (2): winged (two ``wing_lever_{i}`` levers on mirrored REVOLUTE
    rivet pivots, ~100 deg) / direct_pull (no wings, body gets a top bridge).
    The DEFINING motion topology axis. (parent / mech variant)
  * ``wing_geometry`` (4): the two wings' blade mesh — spade / paddle / curved /
    lattice. **Only present when mechanism=winged** (compatibility gate); the
    part tree / joint topology is unchanged by the mesh swap. (parent + 3 wing
    variants)
  * ``handle`` (3): the top user grip on the worm part — straight_t_bar (cross
    bar + ball tips) / angled_bar (V-bent arms + ball tips) / ball_knob (single
    sphere on a neck). A worm-part visual, no independent joint. (parent + 2
    handle variants)
  * ``foil_crown`` (2): plain (bare bell bore) / rotating_cutter (an extra
    ``foil_cutter`` collar + 3 inward blades on a CONTINUOUS ``cutter_spin``
    press-fit in the bell bore). Adds +1 part +1 non-fixed joint. (parent +
    crown variant)

The two wings are a FIXED PAIR (N=2) — never a multiplicity axis. All handle /
tip / rivet / ring / blade arrays are module-local fixed symmetric visuals
emitted via shared helpers and absolute placement (Rule 1: the only separate
parts are the ones that genuinely articulate — wings, spindle, worm, cutter).
The rivet-in-hub-bore, guide-collar-in-plate-slot, shaft-in-sleeve-bore, and
cutter-collar-in-bell-bore captures are all captured-pin geometry, so those
joints omit ``MatingContract`` (grandfathered) and rely on the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block).
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
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    min_clearance_at_pose,
)

__modular__ = True

Mechanism = Literal["winged", "direct_pull"]
WingGeometry = Literal["spade", "paddle", "curved", "lattice"]
Handle = Literal["straight_t_bar", "angled_bar", "ball_knob"]
FoilCrown = Literal["plain", "rotating_cutter"]
PaletteStyle = Literal[
    "chrome_black",
    "all_chrome",
    "brass_black",
    "gunmetal",
    "antique_brass",
]

MECHANISMS: tuple[Mechanism, ...] = ("winged", "direct_pull")
WING_GEOMETRIES: tuple[WingGeometry, ...] = ("spade", "paddle", "curved", "lattice")
HANDLES: tuple[Handle, ...] = ("straight_t_bar", "angled_bar", "ball_knob")
FOIL_CROWNS: tuple[FoilCrown, ...] = ("plain", "rotating_cutter")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "chrome_black",
    "all_chrome",
    "brass_black",
    "gunmetal",
    "antique_brass",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys drive every .visual material so the swept
# pool is colorful (module_topology_diversity only counts structure). Keys:
# frame (body) / spindle (rack) / worm (helix + shaft) / handle (grip) /
# accent (tips / caps) / cutter (foil cutter).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "chrome_black": {
        "frame": (0.07, 0.07, 0.08, 1.0),
        "spindle": (0.76, 0.78, 0.81, 1.0),
        "worm": (0.76, 0.78, 0.81, 1.0),
        "handle": (0.86, 0.87, 0.89, 1.0),
        "accent": (0.86, 0.87, 0.89, 1.0),
        "cutter": (0.72, 0.73, 0.76, 1.0),
    },
    "all_chrome": {
        "frame": (0.78, 0.80, 0.83, 1.0),
        "spindle": (0.76, 0.78, 0.81, 1.0),
        "worm": (0.82, 0.84, 0.87, 1.0),
        "handle": (0.86, 0.87, 0.89, 1.0),
        "accent": (0.70, 0.72, 0.75, 1.0),
        "cutter": (0.74, 0.76, 0.79, 1.0),
    },
    "brass_black": {
        "frame": (0.07, 0.07, 0.08, 1.0),
        "spindle": (0.80, 0.62, 0.26, 1.0),
        "worm": (0.80, 0.62, 0.26, 1.0),
        "handle": (0.84, 0.66, 0.30, 1.0),
        "accent": (0.72, 0.55, 0.22, 1.0),
        "cutter": (0.80, 0.62, 0.26, 1.0),
    },
    "gunmetal": {
        "frame": (0.28, 0.30, 0.33, 1.0),
        "spindle": (0.34, 0.36, 0.39, 1.0),
        "worm": (0.76, 0.78, 0.81, 1.0),
        "handle": (0.34, 0.36, 0.39, 1.0),
        "accent": (0.62, 0.64, 0.67, 1.0),
        "cutter": (0.62, 0.64, 0.67, 1.0),
    },
    "antique_brass": {
        "frame": (0.66, 0.52, 0.30, 1.0),
        "spindle": (0.70, 0.56, 0.32, 1.0),
        "worm": (0.70, 0.56, 0.32, 1.0),
        "handle": (0.45, 0.30, 0.16, 1.0),
        "accent": (0.45, 0.30, 0.16, 1.0),
        "cutter": (0.62, 0.64, 0.67, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), unified A-family convention (parent +
# variants). A small butterfly corkscrew: body ~0.05 m wide, ~0.17 m tall at
# the T-bar top, spindle travel ~0.038 m. Mechanical fits (bore embeds,
# clearances) are never scaled; geometry / travel / angles are scaled.
# ---------------------------------------------------------------------------
# Bell skirt (hollow cone shell, grounds on the bottle neck at z=0).
_BELL_H = 0.028
_BELL_R_BOT_OUT = 0.0240
_BELL_R_BOT_IN = 0.0205
_BELL_R_TOP_OUT = 0.0195
_BELL_R_TOP_IN = 0.0160

# Twin vertical body plates + their support legs.
_PLATE_W = 0.050
_PLATE_T = 0.003
_PLATE_Y_IN = 0.007  # inner face of each plate -> central mechanism slot
_PLATE_Z0 = 0.063
_PLATE_Z1 = 0.123
_LEG_W = 0.009
_LEG_X = 0.016

# Top bridge (direct_pull only).
_BRIDGE_T = 0.004

# Wing pivots (rivet bosses near the top of the plates; winged only).
_PIVOT_X = 0.0185
_PIVOT_X_FLOOR = 0.0215  # narrow-body floor: keep the wing swing clear of the rack
_PIVOT_Z = 0.113
_RIVET_PIN_R = 0.0033
_RIVET_CAP_R = 0.0055

# Lever wings.
_WING_HALF_T = 0.0025
_PADDLE_MAX_HALF_W = 0.015
_WING_RANGE = math.radians(100.0)

# Lattice perforation rows (lattice wing).
_PERF_HOLE_R = 0.0015
_PERF_ROWS: tuple[tuple[float, tuple[float, ...]], ...] = (
    (-0.010, (-0.004, 0.000, 0.004)),
    (-0.017, (-0.002, 0.002)),
    (-0.024, (-0.004, 0.000, 0.004)),
    (-0.031, (-0.002, 0.002)),
    (-0.038, (-0.003, 0.000, 0.003)),
    (-0.045, (-0.0015, 0.0015)),
)

# Shaft / rack stack.
_SHAFT_R = 0.0045
_SLEEVE_BORE_R = 0.0042  # light running fit: shaft core seats in this bore
_SLEEVE_R = 0.0062
_RING_R = 0.0068
_TRAVEL = 0.038
# The thick smooth shaft_core must stay above the bell mouth at full descent — only
# the thin worm helix may pass through the bell / central bore. Travel is capped so
# the shaft_core bottom clears the bell mouth by this margin at full travel.
_SHAFT_BELL_CLEAR = 0.004
_JOINT_TOP_Z = 0.123  # prismatic joint frame: top plane of the body plates
# Guide key width (X). Kept slim so the winged levers, which pivot close to the
# central axis and sweep up-and-over through the region occupied by this guide
# (world z ~= pivot_z), clear the central rack column throughout their arc — a
# fat 0.012 key was swept THROUGH by the wing blade mid-travel (genuine 穿模).
# The guide's real job is the anti-rotation / vertical-travel key against the
# plate inner faces, which is set by _GUIDE_HALF_Y (Y interference), not width.
_GUIDE_X = 0.006
_GUIDE_HALF_Y = 0.0073  # 0.3 mm interference against each plate inner face
_GUIDE_Z0 = -0.024
_GUIDE_Z1 = 0.004

# T-handle / worm locals (in the spinning shaft frame; origin coincides with the
# prismatic frame at rest -> world z = JOINT_TOP_Z).
_WORM_COIL_R = 0.0042
_WORM_WIRE_R = 0.0017
_WORM_Z0 = -0.113  # world 0.012 at rest
_WORM_HEIGHT = 0.046
_CORE_Z0 = -0.071
_CORE_Z1 = 0.047  # straight / angled bar: shaft core top
_CORE_Z1_BALL = 0.025  # ball_knob: lowered to seat the ball above
_TBAR_Z = 0.046
_TBAR_LEN = 0.060
_TBAR_R = 0.0065
_TBAR_TILT_DEG = 30.0  # angled_bar arms angled up from horizontal

# Ball-knob grip.
_BALL_R = 0.0105
_BALL_NECK_R = 0.005
_BALL_NECK_H = 0.006

# Foil-cutter crown (rotating_cutter only).
_CUTTER_Z0 = -0.003  # collar bottom in part frame (world z=0 at rest)
_CUTTER_H = 0.006
_CUTTER_R_OUT = 0.0200  # light press fit against bell inner wall
_CUTTER_R_IN = 0.0130  # standard wine-bottle neck bore
_BLADE_COUNT = 3
_BLADE_RADIAL = 0.004
_BLADE_AXIAL = 0.003
_BLADE_THICK = 0.0008
_BLADE_EMBED = 0.001
_BLADE_R_OUTER = _CUTTER_R_IN + _BLADE_EMBED  # 0.014 — inside collar wall
_BLADE_R_INNER = _CUTTER_R_IN - _BLADE_RADIAL  # 0.009 — cutting edge

# Mesh tessellation tolerance (slightly coarsened from the 0.001 default for
# these small parts to keep the swept meshes light — the helix sweep and lofts
# are the heaviest; geometry stays legible at 0.0015).
_MESH_TOL = 0.0015
_MESH_ANG_TOL = 0.25


def _mesh(solid: cq.Workplane, name: str, *, assets):
    return mesh_from_cadquery(
        solid, name, assets=assets, tolerance=_MESH_TOL, angular_tolerance=_MESH_ANG_TOL
    )


def _scale_z(solid: cq.Workplane, sz: float) -> cq.Workplane:
    """Non-uniform affine scale about z=0 (lengthens a wing lever hanging along
    -Z). Implemented via an OCC GTransform since cadquery's .scale is uniform."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_GTransform
    from OCP.gp import gp_GTrsf, gp_Mat, gp_XYZ

    shape = solid.val().wrapped
    mat = gp_Mat(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, float(sz))
    gtrsf = gp_GTrsf(mat, gp_XYZ(0.0, 0.0, 0.0))
    transformed = BRepBuilderAPI_GTransform(shape, gtrsf, True).Shape()
    return cq.Workplane(obj=cq.Shape.cast(transformed))


@dataclass(frozen=True)
class CorkscrewConfig:
    mechanism: Mechanism | None = None
    wing_geometry: WingGeometry | None = None
    handle: Handle | None = None
    foil_crown: FoilCrown | None = None
    palette_style: PaletteStyle = "chrome_black"
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    spindle_travel_scale: float = 1.0
    worm_radius_scale: float = 1.0
    wing_len_scale: float = 1.0
    wing_open_scale: float = 1.0
    handle_span_scale: float = 1.0
    cutter_radius_scale: float = 1.0
    name: str = "corkscrew"


@dataclass(frozen=True)
class ResolvedCorkscrewConfig:
    mechanism: Mechanism
    wing_geometry: WingGeometry | None  # None when direct_pull
    handle: Handle
    foil_crown: FoilCrown
    palette_style: PaletteStyle
    # Scaled / derived geometry.
    body_width_scale: float
    plate_w: float
    bell_scale: float
    plate_z0: float
    plate_z1: float
    joint_top_z: float
    pivot_x: float
    pivot_z: float
    wing_range: float
    wing_len_scale: float
    travel: float
    worm_coil_r: float
    worm_wire_r: float
    worm_z0: float
    worm_height: float
    shaft_r: float
    sleeve_bore_r: float
    core_z0: float
    core_z1: float
    tbar_z: float
    tbar_len: float
    ball_r: float
    cutter_r_out: float
    cutter_r_in: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CorkscrewConfig:
    rng = random.Random(seed)
    mechanism: Mechanism = rng.choice(MECHANISMS)
    # Compatibility gate: wing_geometry is sampled ONLY when winged. direct_pull
    # has no wings, so the wing_geometry slot is absent (left None).
    wing_geometry: WingGeometry | None = (
        rng.choice(WING_GEOMETRIES) if mechanism == "winged" else None
    )
    handle: Handle = rng.choice(HANDLES)
    foil_crown: FoilCrown = rng.choice(FOIL_CROWNS)
    return CorkscrewConfig(
        mechanism=mechanism,
        wing_geometry=wing_geometry,
        handle=handle,
        foil_crown=foil_crown,
        palette_style=rng.choice(PALETTE_STYLES),
        body_width_scale=round(rng.uniform(0.90, 1.12), 4),
        body_height_scale=round(rng.uniform(0.90, 1.12), 4),
        spindle_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        worm_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        wing_len_scale=round(rng.uniform(0.85, 1.15), 4),
        wing_open_scale=round(rng.uniform(0.85, 1.05), 4),
        handle_span_scale=round(rng.uniform(0.85, 1.15), 4),
        cutter_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_corkscrew_{seed}",
    )


def resolve_config(config: CorkscrewConfig | None = None) -> ResolvedCorkscrewConfig:
    cfg = config or CorkscrewConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    mechanism: Mechanism = _pick(cfg.mechanism, MECHANISMS)
    handle = _pick(cfg.handle, HANDLES)
    foil_crown = _pick(cfg.foil_crown, FOIL_CROWNS)
    # wing_geometry only meaningful when winged (compatibility gate).
    if mechanism == "winged":
        wing_geometry: WingGeometry | None = _pick(cfg.wing_geometry, WING_GEOMETRIES)
    else:
        wing_geometry = None

    width_scale = _clamp(cfg.body_width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.12)
    travel_scale = _clamp(cfg.spindle_travel_scale, 0.85, 1.10)
    worm_radius_scale = _clamp(cfg.worm_radius_scale, 0.90, 1.10)
    wing_len_scale = _clamp(cfg.wing_len_scale, 0.85, 1.15)
    wing_open_scale = _clamp(cfg.wing_open_scale, 0.85, 1.05)
    handle_span_scale = _clamp(cfg.handle_span_scale, 0.85, 1.15)
    cutter_radius_scale = _clamp(cfg.cutter_radius_scale, 0.90, 1.10)

    # Body height: scale the plate band (PLATE_Z0/Z1) about the bell top so the
    # bell stays grounded; PIVOT_Z / JOINT_TOP_Z ride along. Keep ~0.17 m tall.
    plate_z0 = _PLATE_Z0 * height_scale
    plate_z1 = _PLATE_Z1 * height_scale
    joint_top_z = plate_z1
    pivot_z = _PIVOT_Z * height_scale
    # Wing pivot X: never let a NARROW body pull the rivet (and the wings that
    # hang from it) inward toward the central rack. The levers pivot close in and
    # sweep up-and-over the central column while the rack descends through the
    # same region, so a smaller pivot_x crowds the rack_spindle and the blade
    # sweeps into it (the wider seeds clear it by ~1.5 mm; the narrow ones dug
    # in). Floor the pivot so every body keeps that clearance; only WIDER bodies
    # push it further out. (Cap caps' proud read on the narrowest plate is
    # accepted — the rivet still seats on the plate via the through-pin.)
    pivot_x = max(_PIVOT_X * width_scale, _PIVOT_X_FLOOR)

    # Body width: PLATE_W scales but the rest test asserts 0.046..0.054 so keep
    # the scale modest and within band.
    plate_w = _clamp(_PLATE_W * width_scale, 0.046, 0.0539)
    bell_scale = _clamp(width_scale, 0.92, 1.08)

    # Wing open range (winged): keep <= pi * 0.62 so wings never fold backward.
    wing_range = _clamp(_WING_RANGE * wing_open_scale, math.radians(80.0), math.pi * 0.62)

    # Worm radius (also widens the shaft core; keep the shaft-in-sleeve embed so
    # bore stays just inside the shaft for a running fit).
    worm_coil_r = _WORM_COIL_R * worm_radius_scale
    shaft_r = _SHAFT_R * worm_radius_scale
    sleeve_bore_r = max(shaft_r - 0.0003, _SLEEVE_R - 0.001)  # bore tighter than shaft
    sleeve_bore_r = min(sleeve_bore_r, shaft_r - 0.0002)

    # Travel must keep the worm hanging above the table at rest and not punch the
    # worm out below the bell (spec §7 inequalities); the rest geometry is fixed
    # so the nominal 0.038 m already satisfies both — only scale modestly.
    travel = _clamp(_TRAVEL * travel_scale, 0.030, 0.044)

    tbar_len = _TBAR_LEN * (handle_span_scale if handle != "ball_knob" else 1.0)
    ball_r = _BALL_R * (handle_span_scale if handle == "ball_knob" else 1.0)

    # Worm-frame z layout scales with body height so the whole worm/handle
    # assembly shrinks/grows with the (height-scaled) joint_top_z. This keeps the
    # worm bottom at world ~0.012 * height_scale (hangs above the bell at rest)
    # and the T-bar top at ~0.17 m * height_scale, regardless of height_scale.
    worm_z0 = _WORM_Z0 * height_scale
    worm_height = _WORM_HEIGHT * height_scale
    core_z0 = _CORE_Z0 * height_scale
    core_z1_base = _CORE_Z1_BALL if handle == "ball_knob" else _CORE_Z1
    core_z1 = core_z1_base * height_scale
    tbar_z = _TBAR_Z * height_scale

    # Cap travel so the thick smooth shaft_core never descends into the bell / through
    # the central bore — only the thin worm helix may pass the bell mouth at full
    # descent. shaft_core bottom at rest = joint_top_z + core_z0; keep it above the
    # (unscaled) bell mouth by _SHAFT_BELL_CLEAR. (Without this the whole thick rod
    # plunged through the central hole and the thin worm shot out the bell bottom.)
    shaft_bottom_rest = joint_top_z + core_z0
    travel = min(travel, shaft_bottom_rest - _BELL_H - _SHAFT_BELL_CLEAR)

    # Cutter outer radius press-fit band (rotating_cutter): keep >= bell inner
    # wall + 0.002 so it stays a press fit in the bell bore.
    bell_inner_r = _BELL_R_BOT_IN * bell_scale
    cutter_r_out = max(_CUTTER_R_OUT * cutter_radius_scale, bell_inner_r + 0.002)
    cutter_r_in = min(_CUTTER_R_IN, cutter_r_out - 0.004)

    return ResolvedCorkscrewConfig(
        mechanism=mechanism,
        wing_geometry=wing_geometry,
        handle=handle,
        foil_crown=foil_crown,
        palette_style=palette_style,
        body_width_scale=width_scale,
        plate_w=plate_w,
        bell_scale=bell_scale,
        plate_z0=plate_z0,
        plate_z1=plate_z1,
        joint_top_z=joint_top_z,
        pivot_x=pivot_x,
        pivot_z=pivot_z,
        wing_range=wing_range,
        wing_len_scale=wing_len_scale if mechanism == "winged" else 1.0,
        travel=travel,
        worm_coil_r=worm_coil_r,
        worm_wire_r=_WORM_WIRE_R,
        worm_z0=worm_z0,
        worm_height=worm_height,
        shaft_r=shaft_r,
        sleeve_bore_r=sleeve_bore_r,
        core_z0=core_z0,
        core_z1=core_z1,
        tbar_z=tbar_z,
        tbar_len=tbar_len,
        ball_r=ball_r,
        cutter_r_out=cutter_r_out,
        cutter_r_in=cutter_r_in,
        name=cfg.name or "corkscrew",
    )


def with_overrides(config: CorkscrewConfig, **kwargs: object) -> CorkscrewConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Slot choices (consumed by module_topology_diversity). direct_pull omits the
# wing_geometry tuple entirely (slot absent), which distinguishes it from winged.
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: CorkscrewConfig | ResolvedCorkscrewConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCorkscrewConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [("mechanism", r.mechanism)]
    if r.mechanism == "winged" and r.wing_geometry is not None:
        choices.append(("wing_geometry", r.wing_geometry))
    choices.append(("handle", r.handle))
    choices.append(("foil_crown", r.foil_crown))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body frame mesh (shared bell + plates + legs; winged adds nothing here — the
# rivet bosses are separate Cylinder visuals — direct_pull adds a top bridge +
# shaft bore). Bell width scales with bell_scale; plate band with height.
# ---------------------------------------------------------------------------
def _build_body_frame(r: ResolvedCorkscrewConfig) -> cq.Workplane:
    bs = r.bell_scale
    bell = (
        cq.Workplane("XZ")
        .polyline(
            [
                (_BELL_R_BOT_IN * bs, 0.0),
                (_BELL_R_BOT_OUT * bs, 0.0),
                (_BELL_R_TOP_OUT * bs, _BELL_H),
                (_BELL_R_TOP_IN * bs, _BELL_H),
            ]
        )
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )

    body = bell
    plate_h = r.plate_z1 - r.plate_z0
    for sy in (-1.0, 1.0):
        y_c = sy * (_PLATE_Y_IN + 0.5 * _PLATE_T)
        plate = (
            cq.Workplane("XY")
            .box(r.plate_w, _PLATE_T, plate_h)
            .edges("|Y and >Z")
            .fillet(0.012)
            .translate((0.0, y_c, r.plate_z0 + 0.5 * plate_h))
        )
        body = body.union(plate)
        # Legs bridge the bell top up to the plate bottom; derive their height
        # from plate_z0 so they always span the gap (height_scale lifts the
        # plate band, so a fixed-height leg would detach when height_scale>1).
        leg_z0 = 0.023
        leg_z1 = r.plate_z0 + 0.006  # overlap into the plate band
        leg_h = leg_z1 - leg_z0
        for sx in (-1.0, 1.0):
            leg = (
                cq.Workplane("XY")
                .box(_LEG_W, _PLATE_T, leg_h)
                .translate((sx * _LEG_X, y_c, leg_z0 + 0.5 * leg_h))
            )
            body = body.union(leg)

    if r.foil_crown == "rotating_cutter":
        # Central cross-rib spanning the bell mouth: the foil cutter's collar
        # journals around this little mount, and it gives the cutter_spin axis
        # real body geometry near the center (origin must be within 0.015 m of
        # parent mesh; the bare bell inner wall at r~0.0205 is too far). A
        # central bore lets the worm core pass through on full descent.
        rib_z = 0.004
        # Span the full bell mouth (to the OUTER wall) so the rib fuses solidly
        # into the bell shell on both ends.
        rib = (
            cq.Workplane("XY")
            .box(2.0 * _BELL_R_BOT_OUT * bs, 0.0030, 0.0040)
            .translate((0.0, 0.0, rib_z))
        )
        boss = (
            cq.Workplane("XY").circle(0.0050).extrude(0.0050).translate((0.0, 0.0, rib_z - 0.0025))
        )
        body = body.union(rib).union(boss)
        # Bore sized for the thin WORM (coil + wire), not the shaft: only the helical
        # worm passes down through this central hole; the thick shaft_core stays above
        # the bell mouth (travel is capped for that). Clearance 0.001 for a clean pass.
        worm_pass_r = r.worm_coil_r + r.worm_wire_r + 0.0010
        worm_bore = (
            cq.Workplane("XY")
            .circle(worm_pass_r)
            .extrude(0.012)
            .translate((0.0, 0.0, rib_z - 0.006))
        )
        body = body.cut(worm_bore)

    if r.mechanism == "direct_pull":
        # Top bridge across the plate gap + shaft bore (user pulls against it).
        bridge_gap = 2.0 * _PLATE_Y_IN
        bridge = (
            cq.Workplane("XY")
            .box(r.plate_w - 0.008, bridge_gap + 2.0 * _PLATE_T, _BRIDGE_T)
            .edges("|Z")
            .fillet(0.004)
            .translate((0.0, 0.0, r.plate_z1 + 0.5 * _BRIDGE_T))
        )
        body = body.union(bridge)
        shaft_bore = (
            cq.Workplane("XY")
            .circle(r.shaft_r + 0.001)
            .extrude(_BRIDGE_T + 0.004)
            .translate((0.0, 0.0, r.plate_z1 - 0.002))
        )
        body = body.cut(shaft_bore)

    return body


# ---------------------------------------------------------------------------
# Wing blade meshes (Slot wing_geometry). Local frame: pivot at origin, blade
# hangs along -Z at q=0; inner_sign is the local X facing the central shaft.
# All four keep the toothed sector + hub bore (rivet journal) primitives.
# ---------------------------------------------------------------------------
def _build_spade_wing(inner_sign: float, *, lattice: bool = False) -> cq.Workplane:
    hub = cq.Workplane("XZ").circle(0.0095).extrude(_WING_HALF_T, both=True)
    arm = (
        cq.Workplane("XZ")
        .polyline(
            [
                (-0.0080, -0.004),
                (0.0080, -0.004),
                (0.0055, -0.046),
                (0.0095, -0.062),
                (0.0095, -0.070),
                (0.0040, -0.070),
                (0.0000, -0.0585),
                (-0.0040, -0.070),
                (-0.0095, -0.070),
                (-0.0095, -0.062),
                (-0.0055, -0.046),
            ]
        )
        .close()
        .extrude(_WING_HALF_T, both=True)
    )
    wing = hub.union(arm)

    if lattice:
        for z_row, x_positions in _PERF_ROWS:
            for x_pos in x_positions:
                hole = (
                    cq.Workplane("XY", origin=(x_pos, 0.0, z_row))
                    .circle(_PERF_HOLE_R)
                    .extrude(_WING_HALF_T * 3.0, both=True)
                )
                wing = wing.cut(hole)

    for phi_deg in (12.0, 38.0, 64.0, 90.0):
        phi = math.radians(phi_deg)
        cx = inner_sign * 0.0093 * math.sin(phi)
        cz = 0.0093 * math.cos(phi)
        tooth = cq.Workplane("XZ", origin=(cx, 0.0, cz)).circle(0.0019).extrude(0.0022, both=True)
        wing = wing.union(tooth)

    pivot_hole = cq.Workplane("XZ").circle(0.0030).extrude(0.02, both=True)
    return wing.cut(pivot_hole)


def _build_paddle_wing(inner_sign: float) -> cq.Workplane:
    hub = cq.Workplane("XZ").circle(0.0095).extrude(_WING_HALF_T, both=True)
    blade = (
        cq.Workplane("XZ")
        .polyline(
            [
                (-0.006, -0.005),
                (0.006, -0.005),
                (0.011, -0.020),
                (_PADDLE_MAX_HALF_W, -0.036),
                (0.014, -0.056),
                (0.009, -0.068),
                (0.000, -0.072),
                (-0.009, -0.068),
                (-0.014, -0.056),
                (-_PADDLE_MAX_HALF_W, -0.036),
                (-0.011, -0.020),
            ]
        )
        .close()
        .extrude(_WING_HALF_T, both=True)
    )
    wing = hub.union(blade)

    tooth_inner = 0.0075
    tooth_outer = 0.0130
    tooth_half_w = 0.0010
    tooth_half_t = 0.0018
    for phi_deg in (8.0, 24.0, 40.0, 56.0, 72.0, 88.0):
        phi = math.radians(phi_deg)
        r_mid = 0.5 * (tooth_inner + tooth_outer)
        cx = inner_sign * r_mid * math.sin(phi)
        cz = r_mid * math.cos(phi)
        tooth_len = tooth_outer - tooth_inner
        tooth = (
            cq.Workplane("XZ", origin=(cx, 0.0, cz))
            .transformed(rotate=(0.0, -math.degrees(phi), 0.0))
            .rect(tooth_len, 2.0 * tooth_half_w)
            .extrude(tooth_half_t, both=True)
        )
        wing = wing.union(tooth)

    pivot_hole = cq.Workplane("XZ").circle(0.0030).extrude(0.02, both=True)
    return wing.cut(pivot_hole)


def _build_aero_blade(inner_sign: float) -> cq.Workplane:
    s = inner_sign
    t = _WING_HALF_T
    hub = cq.Workplane("XZ").circle(0.0095).extrude(t * 1.5, both=True)
    blade = (
        cq.Workplane("XY", origin=(s * -0.002, 0.0, -0.003))
        .ellipse(0.007, t * 1.2)
        .workplane(offset=-0.034)
        .center(s * -0.012, 0.0)
        .ellipse(0.006, t * 0.9)
        .workplane(offset=-0.033)
        .center(s * 0.009, 0.0)
        .ellipse(0.003, t * 0.5)
        .loft()
    )
    wing = hub.union(blade)
    for phi_deg in (20.0, 50.0, 80.0):
        phi = math.radians(phi_deg)
        cx = s * 0.0093 * math.sin(phi)
        cz = 0.0093 * math.cos(phi)
        tooth = cq.Workplane("XZ", origin=(cx, 0.0, cz)).circle(0.0019).extrude(0.0022, both=True)
        wing = wing.union(tooth)
    pivot_hole = cq.Workplane("XZ").circle(0.0030).extrude(0.02, both=True)
    return wing.cut(pivot_hole)


def _build_wing_mesh(r: ResolvedCorkscrewConfig, inner_sign: float, name: str, *, assets):
    geom = r.wing_geometry
    if geom == "paddle":
        solid = _build_paddle_wing(inner_sign)
    elif geom == "curved":
        solid = _build_aero_blade(inner_sign)
    elif geom == "lattice":
        solid = _build_spade_wing(inner_sign, lattice=True)
    else:  # spade (baseline)
        solid = _build_spade_wing(inner_sign, lattice=False)
    # wing_len_scale (conditional, winged only) stretches the lever along -Z
    # about the hub at the origin; the toothed sector / hub bore near z=0 are
    # nearly unchanged so the rivet journal fit is preserved.
    if abs(r.wing_len_scale - 1.0) > 1e-6:
        solid = _scale_z(solid, r.wing_len_scale)
    return _mesh(solid, name, assets=assets)


# ---------------------------------------------------------------------------
# Rack spindle (shared: ring stack + guide collar + bore).
# ---------------------------------------------------------------------------
def _build_rack_sleeve(r: ResolvedCorkscrewConfig) -> cq.Workplane:
    sleeve = cq.Workplane("XY").cylinder(0.025, _SLEEVE_R).translate((0.0, 0.0, 0.0145))
    for z_ring in (0.0065, 0.0125, 0.0185):
        ring = cq.Workplane("XY").cylinder(0.0035, _RING_R).translate((0.0, 0.0, z_ring))
        sleeve = sleeve.union(ring)
    guide = (
        cq.Workplane("XY")
        .box(_GUIDE_X, 2.0 * _GUIDE_HALF_Y, _GUIDE_Z1 - _GUIDE_Z0)
        .translate((0.0, 0.0, 0.5 * (_GUIDE_Z0 + _GUIDE_Z1)))
    )
    sleeve = sleeve.union(guide)
    bore = cq.Workplane("XY").cylinder(0.064, r.sleeve_bore_r).translate((0.0, 0.0, 0.0045))
    return sleeve.cut(bore)


# ---------------------------------------------------------------------------
# Worm helix (shared, true cq.Wire.makeHelix sweep — no primitive downgrade).
# ---------------------------------------------------------------------------
def _build_worm(r: ResolvedCorkscrewConfig) -> cq.Workplane:
    helix = cq.Wire.makeHelix(pitch=0.0115, height=r.worm_height, radius=r.worm_coil_r)
    path = cq.Workplane("XY").newObject([helix])
    worm = (
        cq.Workplane("XZ")
        .center(r.worm_coil_r, 0.0)
        .circle(r.worm_wire_r)
        .sweep(path, isFrenet=True)
    )
    return worm.translate((0.0, 0.0, r.worm_z0))


# ---------------------------------------------------------------------------
# Handle meshes (Slot handle; worm-part visuals, no joint).
# ---------------------------------------------------------------------------
def _build_bent_tbar(r: ResolvedCorkscrewConfig) -> cq.Workplane:
    half_len = 0.5 * r.tbar_len
    boss = (
        cq.Workplane("XY")
        .circle(_SHAFT_R * 1.6)
        .extrude(2.4 * _TBAR_R)
        .translate((0.0, 0.0, r.tbar_z - 1.2 * _TBAR_R))
    )
    tbar = boss
    for sign in (-1.0, 1.0):
        arm = cq.Workplane("YZ").circle(_TBAR_R).extrude(half_len)
        tip = cq.Workplane("YZ", origin=(half_len, 0.0, 0.0)).sphere(_TBAR_R)
        piece = arm.union(tip)
        piece = piece.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), -_TBAR_TILT_DEG)
        if sign < 0.0:
            piece = piece.mirror("YZ")
        piece = piece.translate((0.0, 0.0, r.tbar_z))
        tbar = tbar.union(piece)
    return tbar


def _build_ball_knob(r: ResolvedCorkscrewConfig) -> cq.Workplane:
    sphere_center_z = r.core_z1 + _BALL_NECK_H + r.ball_r
    neck = (
        cq.Workplane("XY")
        .cylinder(_BALL_NECK_H, _BALL_NECK_R)
        .translate((0.0, 0.0, r.core_z1 + 0.5 * _BALL_NECK_H))
    )
    ball = cq.Workplane("XY").sphere(r.ball_r).translate((0.0, 0.0, sphere_center_z))
    return neck.union(ball)


# ---------------------------------------------------------------------------
# Foil-cutter crown meshes (Slot foil_crown / rotating_cutter).
# ---------------------------------------------------------------------------
def _build_foil_cutter_collar(r: ResolvedCorkscrewConfig) -> cq.Workplane:
    collar = (
        cq.Workplane("XZ")
        .polyline(
            [
                (r.cutter_r_in, _CUTTER_Z0),
                (r.cutter_r_out, _CUTTER_Z0),
                (r.cutter_r_out, _CUTTER_Z0 + _CUTTER_H),
                (r.cutter_r_in, _CUTTER_Z0 + _CUTTER_H),
            ]
        )
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )
    return collar


def _build_cutter_blade() -> cq.Workplane:
    blade_width = _BLADE_R_OUTER - _BLADE_R_INNER
    blade = (
        cq.Workplane("XY")
        .box(blade_width, _BLADE_THICK, _BLADE_AXIAL)
        .translate((0.5 * (_BLADE_R_INNER + _BLADE_R_OUTER), 0.0, _CUTTER_Z0 + 0.5 * _CUTTER_H))
    )
    return blade


# ---------------------------------------------------------------------------
# Part builders.
# ---------------------------------------------------------------------------
def _build_body(model: ArticulatedObject, r: ResolvedCorkscrewConfig, mats, *, assets):
    body = model.part("body_frame")
    body.visual(
        _mesh(_build_body_frame(r), "body_frame", assets=assets),
        material=mats["frame"],
        name="frame_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
    )
    if r.mechanism == "winged":
        # Rivet bosses: a pin through both plates + proud caps, one per wing.
        for i, sx in enumerate((-1.0, 1.0)):
            body.visual(
                Cylinder(radius=_RIVET_PIN_R, length=0.025),
                origin=Origin(xyz=(sx * r.pivot_x, 0.0, r.pivot_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["accent"],
                name=f"rivet_pin_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
            )
            for sy in (-1.0, 1.0):
                body.visual(
                    Cylinder(radius=_RIVET_CAP_R, length=0.0025),
                    origin=Origin(
                        xyz=(sx * r.pivot_x, sy * 0.0112, r.pivot_z),
                        rpy=(math.pi / 2.0, 0.0, 0.0),
                    ),
                    material=mats["accent"],
                    name=f"rivet_cap_{i}_{sy > 0:d}", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
                )
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=0.025, length=r.plate_z1),
        mass=0.18,
        origin=Origin(xyz=(0.0, 0.0, r.plate_z1 * 0.5)),
    )
    return body


def _build_wings(model: ArticulatedObject, r: ResolvedCorkscrewConfig, body, mats, *, assets):
    """Emit the FIXED PAIR of wing levers (N=2, never a multiplicity axis) on
    mirrored REVOLUTE rivet pivots. Returns the wing part names."""
    names: list[str] = []
    for i in range(2):
        sx = -1.0 if i == 0 else 1.0
        inner_sign = 1.0 if i == 0 else -1.0
        axis = (0.0, 1.0, 0.0) if i == 0 else (0.0, -1.0, 0.0)
        wing = model.part(f"wing_lever_{i}")
        wing.visual(
            _build_wing_mesh(r, inner_sign, f"wing_lever_{i}", assets=assets),
            material=mats["spindle"],
            name="wing_blade", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "antique_brass"} else "metal.blackened_gunmetal"),
        )
        wing.inertial = Inertial.from_geometry(
            Cylinder(radius=0.012, length=0.07),
            mass=0.02,
            origin=Origin(xyz=(0.0, 0.0, -0.035)),
        )
        model.articulation(
            f"wing_pivot_{i}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=wing,
            origin=Origin(xyz=(sx * r.pivot_x, 0.0, r.pivot_z)),
            axis=axis,
            motion_limits=MotionLimits(effort=20.0, velocity=3.0, lower=0.0, upper=r.wing_range),
        )
        names.append(f"wing_lever_{i}")
    return names


def _build_spindle_and_worm(
    model: ArticulatedObject, r: ResolvedCorkscrewConfig, body, mats, *, assets
):
    """Emit the shared rack_spindle (PRISMATIC) + t_handle_worm (CONTINUOUS),
    with the worm's helix, shaft core and chosen handle visuals."""
    sleeve = model.part("rack_spindle")
    sleeve.visual(
        _mesh(_build_rack_sleeve(r), "rack_spindle", assets=assets),
        material=mats["spindle"],
        name="rack_sleeve", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "antique_brass"} else "metal.blackened_gunmetal"),
    )
    sleeve.inertial = Inertial.from_geometry(
        Cylinder(radius=_SLEEVE_R, length=0.05),
        mass=0.04,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    worm = model.part("t_handle_worm")
    worm.visual(
        _mesh(_build_worm(r), "worm_screw", assets=assets),
        material=mats["worm"],
        name="worm_helix", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
    )
    worm.visual(
        Cylinder(radius=r.shaft_r, length=r.core_z1 - r.core_z0),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (r.core_z0 + r.core_z1))),
        material=mats["worm"],
        name="shaft_core", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
    )
    # --- Handle visuals on the worm part (no independent joint). ---
    if r.handle == "straight_t_bar":
        worm.visual(
            Cylinder(radius=_TBAR_R, length=r.tbar_len),
            origin=Origin(xyz=(0.0, 0.0, r.tbar_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["handle"],
            name="t_bar", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "antique_brass"} else "metal.blackened_gunmetal"),
        )
        for i, sx in enumerate((-1.0, 1.0)):
            worm.visual(
                Sphere(radius=_TBAR_R),
                origin=Origin(xyz=(sx * 0.5 * r.tbar_len, 0.0, r.tbar_z)),
                material=mats["accent"],
                name=f"t_bar_tip_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
            )
    elif r.handle == "angled_bar":
        worm.visual(
            _mesh(_build_bent_tbar(r), "bent_t_bar", assets=assets),
            material=mats["handle"],
            name="t_bar", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "antique_brass"} else "metal.blackened_gunmetal"),
        )
    else:  # ball_knob
        worm.visual(
            _mesh(_build_ball_knob(r), "ball_knob", assets=assets),
            material=mats["handle"],
            name="ball_knob", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "antique_brass"} else "metal.blackened_gunmetal"),
        )

    worm.inertial = Inertial.from_geometry(
        Cylinder(radius=r.worm_coil_r + r.worm_wire_r, length=r.core_z1 - r.core_z0),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (r.core_z0 + r.core_z1))),
    )

    # --- Shared main feed: rack spindle descends through the plate slot. ---
    model.articulation(
        "spindle_travel",
        ArticulationType.PRISMATIC,
        parent=body,
        child=sleeve,
        origin=Origin(xyz=(0.0, 0.0, r.joint_top_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.10, lower=0.0, upper=r.travel),
    )
    # --- Shared worm spin: T-handle + worm spin continuously on the shaft. ---
    model.articulation(
        "worm_spin",
        ArticulationType.CONTINUOUS,
        parent=sleeve,
        child=worm,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=8.0),
    )
    return sleeve, worm


def _build_foil_cutter(model: ArticulatedObject, r: ResolvedCorkscrewConfig, body, mats, *, assets):
    """Emit the optional rotating foil cutter (collar + 3 inward blades) on a
    CONTINUOUS cutter_spin press-fit in the bell bore."""
    cutter = model.part("foil_cutter")
    cutter.visual(
        _mesh(_build_foil_cutter_collar(r), "cutter_collar", assets=assets),
        material=mats["cutter"],
        name="cutter_collar", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black"} else "metal.stainless_matte"),
    )
    for i in range(_BLADE_COUNT):
        angle = i * 2.0 * math.pi / _BLADE_COUNT
        cutter.visual(
            _mesh(_build_cutter_blade(), f"blade_{i}", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, angle)),
            material=mats["accent"],
            name=f"blade_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_black", "all_chrome", "brass_black", "gunmetal"} else "metal.brass_aged"),
        )
    cutter.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cutter_r_out, length=_CUTTER_H),
        mass=0.015,
        origin=Origin(xyz=(0.0, 0.0, _CUTTER_Z0 + 0.5 * _CUTTER_H)),
    )
    model.articulation(
        "cutter_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=cutter,
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=6.0),
    )
    return cutter


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_corkscrew(
    config: CorkscrewConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"corkscrew_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)
    if r.mechanism == "winged":
        _build_wings(model, r, body, mats, assets=assets)
    _build_spindle_and_worm(model, r, body, mats, assets=assets)
    if r.foil_crown == "rotating_cutter":
        _build_foil_cutter(model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_corkscrew(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_corkscrew(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_corkscrew_tests(
    object_model: ArticulatedObject,
    config: CorkscrewConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body_frame")
    sleeve = object_model.get_part("rack_spindle")
    worm = object_model.get_part("t_handle_worm")

    part_names = {p.name for p in object_model.parts}
    joint_names = {a.name for a in object_model.articulations}

    # ---- Captured-fit allowances (element-scoped, mirroring the sources). ----
    # Guide collar press-fit in the plate slot.
    ctx.allow_overlap(
        sleeve,
        body,
        elem_a="rack_sleeve",
        elem_b="frame_shell",
        reason="Guide collar slides in the body plate slot with a light press fit that carries the rack stage.",
    )
    # Shaft core running fit inside the rack sleeve bore.
    ctx.allow_overlap(
        sleeve,
        worm,
        elem_a="rack_sleeve",
        elem_b="shaft_core",
        reason="Polished shaft runs inside the rack sleeve bore as the spin bearing (light running fit).",
    )
    if r.mechanism == "winged":
        for i in range(2):
            wing = object_model.get_part(f"wing_lever_{i}")
            ctx.allow_overlap(
                body,
                wing,
                elem_a=f"rivet_pin_{i}",
                elem_b="wing_blade",
                reason="Rivet pin is intentionally captured in the wing hub bore as the pivot journal.",
            )
    if r.foil_crown == "rotating_cutter":
        cutter = object_model.get_part("foil_cutter")
        ctx.allow_overlap(
            body,
            cutter,
            elem_a="frame_shell",
            elem_b="cutter_collar",
            reason="Cutter collar is a light press-fit bearing inside the bell bore; the outer surface rides against the bell inner wall.",
        )

    # ---- Baseline checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root + shared spindle/worm motion (all candidates). ----
    roots = object_model.root_parts()
    ctx.check(
        "body_frame is the single root",
        len(roots) == 1 and roots[0].name == "body_frame",
        details=f"roots={[p.name for p in roots]}",
    )
    j_travel = object_model.get_articulation("spindle_travel")
    ctx.check(
        "spindle_travel is a descending PRISMATIC about the vertical axis",
        j_travel.articulation_type == ArticulationType.PRISMATIC
        and abs(j_travel.axis[2]) > 0.99
        and abs(j_travel.axis[0]) < 1e-6
        and abs(j_travel.axis[1]) < 1e-6
        and j_travel.axis[2] < 0.0
        and abs(j_travel.motion_limits.upper - r.travel) < 1e-9,
        details=f"type={j_travel.articulation_type} axis={tuple(j_travel.axis)}",
    )
    j_spin = object_model.get_articulation("worm_spin")
    ctx.check(
        "worm_spin is CONTINUOUS about +Z with no limits",
        j_spin.articulation_type == ArticulationType.CONTINUOUS
        and tuple(j_spin.axis) == (0.0, 0.0, 1.0)
        and j_spin.motion_limits is not None
        and j_spin.motion_limits.lower is None
        and j_spin.motion_limits.upper is None,
        details=f"type={j_spin.articulation_type} axis={tuple(j_spin.axis)}",
    )
    ctx.check(
        "at least one non-fixed joint exists",
        any(a.articulation_type != ArticulationType.FIXED for a in object_model.articulations),
    )

    # ---- Identity: a true helical worm hangs above the table at rest. ----
    hb = ctx.part_world_aabb(worm)
    ctx.check(
        "worm hangs above the table at rest (worm bottom above z=0)",
        hb is not None and hb[0][2] > 0.004,
        details=f"worm aabb={hb}",
    )
    wa = ctx.part_element_world_aabb(worm, elem="worm_helix")
    ctx.check(
        "helical worm coil is legible above the bell",
        wa is not None and wa[0][2] > 0.005 and (wa[1][0] - wa[0][0]) > 2.2 * r.shaft_r,
        details=f"worm_helix aabb={wa}",
    )

    # ---- Mechanism topology. ----
    if r.mechanism == "winged":
        ctx.check(
            "winged: two wing lever parts present",
            "wing_lever_0" in part_names and "wing_lever_1" in part_names,
            details=str(sorted(part_names)),
        )
        j_w0 = object_model.get_articulation("wing_pivot_0")
        j_w1 = object_model.get_articulation("wing_pivot_1")
        ctx.check(
            "both wing pivots are REVOLUTE, mirrored about Y, ~100 deg range",
            j_w0.articulation_type == ArticulationType.REVOLUTE
            and j_w1.articulation_type == ArticulationType.REVOLUTE
            and abs(j_w0.axis[1]) > 0.99
            and abs(j_w1.axis[1]) > 0.99
            and j_w0.axis[1] * j_w1.axis[1] < 0.0
            and j_w0.motion_limits.lower == 0.0
            and abs(j_w0.motion_limits.upper - r.wing_range) < 1e-9
            and abs(j_w1.motion_limits.upper - r.wing_range) < 1e-9,
            details=f"w0 axis={tuple(j_w0.axis)} w1 axis={tuple(j_w1.axis)}",
        )
        # Wings hang down at rest, then swing up + out under full travel.
        wing_0 = object_model.get_part("wing_lever_0")
        wing_1 = object_model.get_part("wing_lever_1")
        w0_rest = ctx.part_world_aabb(wing_0)
        w1_rest = ctx.part_world_aabb(wing_1)
        ctx.check(
            "wings hang down beside the frame at rest",
            w0_rest is not None
            and w1_rest is not None
            and w0_rest[0][2] < r.pivot_z
            and w1_rest[0][2] < r.pivot_z,
            details=f"w0_bottom={w0_rest[0][2]:.4f} w1_bottom={w1_rest[0][2]:.4f} pivot_z={r.pivot_z:.4f}",
        )
        with ctx.pose({j_w0: r.wing_range, j_w1: r.wing_range}):
            w0_up = ctx.part_world_aabb(wing_0)
            w1_up = ctx.part_world_aabb(wing_1)
            ctx.check(
                "raising the levers swings both blades upward and outward",
                w0_up[0][2] > w0_rest[0][2] + 0.030
                and w1_up[0][2] > w1_rest[0][2] + 0.030
                and w0_up[0][0] < w0_rest[0][0] - 0.020
                and w1_up[1][0] > w1_rest[1][0] + 0.020,
                details=f"w0_up={w0_up} w1_up={w1_up}",
            )
        # The lever pivots close to the central axis and sweeps up-and-over
        # through the region occupied by the rack column; the blade must clear
        # the rack_spindle at EVERY swing angle (the collision is mid-travel, not
        # at an endpoint), so scan the whole arc rather than just rest/full-open.
        swing_min_clear = min(
            min_clearance_at_pose(
                object_model,
                joint="wing_pivot_0",
                joint_positions={"wing_pivot_0": float(ang)},
                keepout=["rack_spindle"],
            )
            for ang in (r.wing_range * k / 12.0 for k in range(13))
        )
        ctx.check(
            "wing blade clears the central rack column throughout its swing arc",
            swing_min_clear > 0.001,
            details=f"min swing clearance to rack_spindle={swing_min_clear:.5f}",
        )
    else:  # direct_pull
        ctx.check(
            "direct_pull: no wing parts present",
            not any("wing" in n for n in part_names),
            details=str(sorted(part_names)),
        )
        ctx.check(
            "direct_pull: no wing pivot joints present",
            not any("wing" in n for n in joint_names),
            details=str(sorted(joint_names)),
        )

    # ---- Handle silhouette identity. ----
    if r.handle == "straight_t_bar":
        bar = ctx.part_element_world_aabb(worm, elem="t_bar")
        if bar is not None:
            ctx.check(
                "straight T-bar spans X above the frame, long and thin",
                (bar[1][0] - bar[0][0]) >= 0.045
                and (bar[1][0] - bar[0][0]) > (bar[1][1] - bar[0][1]) * 2.5,
                details=f"x-span={bar[1][0] - bar[0][0]:.4f} y-span={bar[1][1] - bar[0][1]:.4f}",
            )
    elif r.handle == "angled_bar":
        ctx.check("angled_bar has a t_bar visual", "t_bar" in {v.name for v in worm.visuals})
    else:  # ball_knob
        ball = ctx.part_element_world_aabb(worm, elem="ball_knob")
        if ball is not None:
            ctx.check(
                "ball knob is a compact rounded grip at the top",
                (ball[1][0] - ball[0][0]) >= 0.014 and (ball[1][0] - ball[0][0]) <= 0.030,
                details=f"x-span={ball[1][0] - ball[0][0]:.4f}",
            )

    # ---- Foil crown topology. ----
    if r.foil_crown == "rotating_cutter":
        ctx.check(
            "foil_cutter part present", "foil_cutter" in part_names, details=str(sorted(part_names))
        )
        j_cut = object_model.get_articulation("cutter_spin")
        ctx.check(
            "cutter_spin is CONTINUOUS about +Z with no limits",
            j_cut.articulation_type == ArticulationType.CONTINUOUS
            and tuple(j_cut.axis) == (0.0, 0.0, 1.0)
            and j_cut.motion_limits is not None
            and j_cut.motion_limits.lower is None
            and j_cut.motion_limits.upper is None,
            details=f"type={j_cut.articulation_type} axis={tuple(j_cut.axis)}",
        )
        cutter = object_model.get_part("foil_cutter")
        ca = ctx.part_world_aabb(cutter)
        ctx.check(
            "cutter crown seated in the bell bore, not below the bell",
            ca is not None and ca[0][2] >= -0.002,
            details=f"cutter aabb={ca}",
        )
        blades = [v.name for v in cutter.visuals if v.name.startswith("blade_")]
        ctx.check(
            "cutter has 3 blades", len(blades) == _BLADE_COUNT, details=f"blades={sorted(blades)}"
        )
    else:
        ctx.check(
            "plain crown: no foil_cutter part / cutter_spin joint",
            "foil_cutter" not in part_names and "cutter_spin" not in joint_names,
            details=str(sorted(part_names)),
        )

    # ---- Body identity: bell grounded at z=0, body ~0.05 m wide. ----
    bb = ctx.part_world_aabb(body)
    ctx.check(
        "bell skirt grounds at z=0",
        bb is not None and abs(bb[0][2]) <= 2.0e-3,
        details=f"body aabb={bb}",
    )
    ctx.check(
        "body reads as a corkscrew (~0.05 m wide)",
        bb is not None and 0.044 <= (bb[1][0] - bb[0][0]) <= 0.056,
        details=f"body x-span={(bb[1][0] - bb[0][0]):.4f}" if bb else "no bb",
    )

    # ---- Mechanism: spinning the worm proves real continuous rotation. ----
    with ctx.pose({j_spin: math.pi / 2.0}):
        hq = ctx.part_world_aabb(worm)
        if r.handle in ("straight_t_bar", "angled_bar") and hb is not None and hq is not None:
            ctx.check(
                "quarter turn swings the handle bar from X toward Y",
                (hq[1][1] - hq[0][1]) > (hb[1][1] - hb[0][1]) + 0.02,
                details=f"rest_y={hb[1][1] - hb[0][1]:.4f} turned_y={hq[1][1] - hq[0][1]:.4f}",
            )

    # ---- Mechanism: advancing the spindle drives the worm DOWN. ----
    p0 = ctx.part_world_position(worm)
    with ctx.pose({j_travel: r.travel}):
        p1 = ctx.part_world_position(worm)
        # Only the thin worm helix may pass the bell mouth: the thick smooth
        # shaft_core must stay above it at full descent (travel is capped for this).
        shaft_fed = ctx.part_element_world_aabb(worm, elem="shaft_core")
    if p0 is not None and p1 is not None:
        ctx.check(
            "advancing the spindle drives the worm down into the bottle",
            p1[2] < p0[2] - 0.5 * r.travel,
            details=f"rest_z={p0[2]:.4f} fed_z={p1[2]:.4f} travel={r.travel:.4f}",
        )
    if shaft_fed is not None:
        ctx.check(
            "thick shaft_core stays above the bell mouth at full descent (only the worm passes through)",
            shaft_fed[0][2] >= _BELL_H - 1.0e-6,
            details=f"shaft_core bottom at full travel={shaft_fed[0][2]:.4f} bell_mouth={_BELL_H:.4f}",
        )

    return ctx.report()


__all__ = (
    "CorkscrewConfig",
    "ResolvedCorkscrewConfig",
    "build_corkscrew",
    "build_seeded_corkscrew",
    "config_from_seed",
    "resolve_config",
    "run_corkscrew_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
