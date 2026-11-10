# SPDX-License-Identifier: Apache-2.0

"""Workspace / Drafting table procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/drafting_table.md

A tilting drawing board on a floor-standing support with a user-set angle lock.
The drawing board (a single wide planar work surface) + its front-edge tilt hinge
are the constant identity layer carried by the grounded support chassis. Structural
diversity lives in the SUPPORT BASE (① skeleton, 6 candidates); the angle-hold
hardware (② mechanism, 3) and the rotary control (③ form family, 3) are the other
slots, with an N-drawer multiplicity apron.

Pattern = parallel_children (+ multiplicity): one grounded ``mount`` chassis part
(``frame``; the telescoping base splits into grounded ``base`` -> PRISMATIC
``carriage`` = mount) carries the REVOLUTE tilting ``tabletop`` and two REVOLUTE
lock controls; the angle mechanism + drawer faces are host ``.visual(...)`` on the
mount. All bases build their legs up to ONE shared upper-frame interface (front
hinge rail / side rails / hinge pin / knob sockets) so the board, controls,
mechanism and drawers mate identically regardless of base.

Rules:
  Rule 1 — non-articulating hardware (ratchet teeth, quadrant plate, drawer faces,
    ring pulls, grain, feet) is a host ``.visual(...)``; the only real parts are the
    tilt board, the 2 lock controls, and (telescoping) the sliding carriage.
  Rule 2 — every moving child is a captured pin/slide (barrel-around-pin,
    shaft-in-socket, tube-in-sleeve); ``MatingContract`` cannot express these, so
    the joints are grandfathered (omit ``mating=``) and kept honest with
    element-scoped ``allow_overlap`` + ``expect_overlap`` mirroring the sources.
  Rule 3 — structure derives from the declared 5-star sources (3 origins + 5 forks).
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism (tilt / lock spin / telescoping lift).
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
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
SupportBase = Literal[
    "cantilever_zframe",
    "splayed_xbrace",
    "wood_trestle",
    "pedestal_column",
    "four_post",
    "telescoping_carriage",
]
AngleMech = Literal["friction_knob_lock", "linear_toothed_ratchet", "curved_ratchet_quadrant"]
Control = Literal["paired_symmetric_knobs", "differentiated_knobs", "crank_winder"]
PaletteStyle = Literal["pale_wood_black", "warm_red_wood_black", "cherry_wood_black", "grey_metal_pale"]

SUPPORT_BASES: tuple[SupportBase, ...] = (
    "cantilever_zframe",
    "splayed_xbrace",
    "wood_trestle",
    "pedestal_column",
    "four_post",
    "telescoping_carriage",
)
ANGLE_MECHS: tuple[AngleMech, ...] = (
    "friction_knob_lock",
    "linear_toothed_ratchet",
    "curved_ratchet_quadrant",
)
CONTROLS: tuple[Control, ...] = (
    "paired_symmetric_knobs",
    "differentiated_knobs",
    "crank_winder",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "pale_wood_black",
    "warm_red_wood_black",
    "cherry_wood_black",
    "grey_metal_pale",
)

# Bases that present a front apron zone able to host cosmetic drawers.
DRAWER_CAPABLE: frozenset[SupportBase] = frozenset(
    {"cantilever_zframe", "splayed_xbrace", "four_post", "telescoping_carriage"}
)
# Wood-framed base uses wood as its structural material.
WOOD_FRAMED: frozenset[SupportBase] = frozenset({"wood_trestle"})

# ---------------------------------------------------------------------------
# Palettes. `wood`/`wood_edge`/`grain_a`/`grain_b` carry the board colorway;
# `metal` the frame steel; hardware near-constant.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "pale_wood_black": {
        "wood": (0.92, 0.70, 0.40, 1.0),
        "wood_edge": (0.74, 0.45, 0.22, 1.0),
        "grain_a": (0.78, 0.55, 0.26, 1.0),
        "grain_b": (0.58, 0.37, 0.16, 1.0),
        "metal": (0.02, 0.022, 0.020, 1.0),
    },
    "warm_red_wood_black": {
        "wood": (0.46, 0.20, 0.075, 1.0),
        "wood_edge": (0.20, 0.085, 0.035, 1.0),
        "grain_a": (0.58, 0.25, 0.090, 1.0),
        "grain_b": (0.34, 0.14, 0.050, 1.0),
        "metal": (0.015, 0.017, 0.016, 1.0),
    },
    "cherry_wood_black": {
        "wood": (0.62, 0.28, 0.09, 1.0),
        "wood_edge": (0.38, 0.15, 0.045, 1.0),
        "grain_a": (0.74, 0.34, 0.11, 1.0),
        "grain_b": (0.50, 0.20, 0.060, 1.0),
        "metal": (0.015, 0.014, 0.012, 1.0),
    },
    "grey_metal_pale": {
        "wood": (0.80, 0.78, 0.72, 1.0),
        "wood_edge": (0.55, 0.53, 0.48, 1.0),
        "grain_a": (0.70, 0.68, 0.62, 1.0),
        "grain_b": (0.58, 0.56, 0.50, 1.0),
        "metal": (0.22, 0.23, 0.24, 1.0),
    },
}
_HARDWARE = {
    "grey": (0.19, 0.20, 0.19, 1.0),
    "plastic": (0.01, 0.011, 0.012, 1.0),
    "steel": (0.82, 0.78, 0.70, 1.0),
    "pale": (0.78, 0.76, 0.68, 1.0),
    "dark": (0.02, 0.02, 0.02, 1.0),
}

# ---------------------------------------------------------------------------
# Single-sourced interface geometry (world meters). +Y = back (depth), -Y =
# front (hinge/low edge), X = width, Z = up. Every base builds up to these.
# ---------------------------------------------------------------------------
SIDE_X = 0.55           # side-rail / leg half-track
TUBE = 0.035            # frame tube cross-section
HINGE_Y = -0.365        # tilt axis (front/low edge)
HINGE_Z = 0.755         # tilt axis height
RAIL_Z = 0.715          # front hinge rail height (below the pivot so the orbiting barrel clears)
TOP_Z = 0.720           # level upper-frame height (below the flat-posed board, which sits ~0.79+)
REAR_RAIL_Y = 0.325
KNOB_Y = -0.175
KNOB_Z = 0.455
KNOB_SOCKET_X = 0.552
KNOB_JOINT_X = 0.600
FLOOR_Z = 0.035         # nominal floor beam center
BOARD_W = 1.20          # nominal board width (x)
BOARD_D = 0.76          # nominal board depth (y)

SIDES: tuple[tuple[str, float], ...] = (("0", -1.0), ("1", 1.0))


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _beam_pose(p0, p1) -> tuple[Origin, float]:
    """Origin aligning a local +Z box/cylinder from p0 to p1."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0:
        raise ValueError("beam endpoints must be distinct")
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    center = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5)
    return Origin(xyz=center, rpy=(0.0, pitch, yaw)), length


def _beam(part, p0, p1, size: float, material, name: str, overshoot: float = 0.020) -> None:
    origin, length = _beam_pose(p0, p1)
    part.visual(Box((size, size, length + overshoot)), origin=origin, material=material, name=name, material_class_id="metal.paint_coated")


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.veneer_panel")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Cylinder(radius=radius, length=length), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.stainless_matte")


def _annular_sector_yz(
    *, center_y: float, center_z: float, radius: float, radial_width: float,
    x_center: float, x_thickness: float, start_angle: float, end_angle: float, segments: int = 36,
) -> MeshGeometry:
    """Curved metal quadrant strip in the YZ plane, extruded in X (adapted from
    origin 003 `_annular_sector_geometry`, replanted onto the +X tilt axis)."""
    geom = MeshGeometry()
    x0 = x_center - x_thickness / 2.0
    x1 = x_center + x_thickness / 2.0
    inner = radius - radial_width
    outer = radius + radial_width
    rings: list[tuple[int, int, int, int]] = []
    for i in range(segments + 1):
        t = start_angle + (end_angle - start_angle) * i / segments
        c = math.cos(t)
        s = math.sin(t)
        rings.append((
            geom.add_vertex(x0, center_y + outer * c, center_z + outer * s),
            geom.add_vertex(x0, center_y + inner * c, center_z + inner * s),
            geom.add_vertex(x1, center_y + outer * c, center_z + outer * s),
            geom.add_vertex(x1, center_y + inner * c, center_z + inner * s),
        ))
    for i in range(segments):
        of0, inf0, ob0, ib0 = rings[i]
        of1, inf1, ob1, ib1 = rings[i + 1]
        geom.add_face(of0, of1, inf1)
        geom.add_face(of0, inf1, inf0)
        geom.add_face(ob0, ib1, ob1)
        geom.add_face(ob0, ib0, ib1)
        geom.add_face(of0, ob0, ob1)
        geom.add_face(of0, ob1, of1)
        geom.add_face(inf0, inf1, ib1)
        geom.add_face(inf0, ib1, ib0)
    for idx in (0, -1):
        of0, inf0, ob0, ib0 = rings[idx]
        geom.add_face(of0, inf0, ib0)
        geom.add_face(of0, ib0, ob0)
    return geom


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class DraftingTableConfig:
    support_base: SupportBase | None = None
    angle_mechanism: AngleMech | None = None
    control_handle: Control | None = None
    n_drawers: int = 0
    palette_style: PaletteStyle = "pale_wood_black"
    board_width_scale: float = 1.0
    board_depth_scale: float = 1.0
    tilt_lower: float = -0.30
    tilt_upper: float = 0.55
    name: str = "drafting_table"


@dataclass(frozen=True)
class ResolvedDraftingTableConfig:
    support_base: SupportBase
    angle_mechanism: AngleMech
    control_handle: Control
    n_drawers: int
    palette_style: PaletteStyle
    board_width_scale: float
    board_depth_scale: float
    tilt_lower: float
    tilt_upper: float
    name: str

    @property
    def half_width(self) -> float:
        """Single source for board half-width and all width-derived spans."""
        return 0.5 * BOARD_W * self.board_width_scale

    @property
    def board_depth(self) -> float:
        return BOARD_D * self.board_depth_scale

    @property
    def is_telescoping(self) -> bool:
        return self.support_base == "telescoping_carriage"


def config_from_seed(seed: int) -> DraftingTableConfig:
    """Deterministic procedural sampling over the full slot domain; seed 0 is not
    special. n_drawers is gated to bases with a front apron zone."""
    rng = random.Random(seed)
    base = rng.choice(SUPPORT_BASES)
    mech = rng.choice(ANGLE_MECHS)
    ctrl = rng.choice(CONTROLS)
    # Weighted drawer multiplicity: small N (incl. 0) more common; only capable bases.
    if base in DRAWER_CAPABLE:
        n_draw = rng.choices((0, 1, 2, 3, 4), weights=(3, 2, 3, 2, 2))[0]
    else:
        n_draw = 0
    return DraftingTableConfig(
        support_base=base,
        angle_mechanism=mech,
        control_handle=ctrl,
        n_drawers=n_draw,
        palette_style=rng.choice(PALETTE_STYLES),
        board_width_scale=round(rng.uniform(0.95, 1.08), 4),
        board_depth_scale=round(rng.uniform(0.97, 1.05), 4),
        tilt_lower=round(rng.uniform(-0.30, -0.20), 4),
        tilt_upper=round(rng.uniform(0.45, 0.65), 4),
        name=f"seeded_drafting_table_{seed}",
    )


def resolve_config(config: DraftingTableConfig | None = None) -> ResolvedDraftingTableConfig:
    cfg = config or DraftingTableConfig()
    base = _pick(cfg.support_base, SUPPORT_BASES)
    mech = _pick(cfg.angle_mechanism, ANGLE_MECHS)
    ctrl = _pick(cfg.control_handle, CONTROLS)
    n_draw = int(cfg.n_drawers) if cfg.n_drawers in (0, 1, 2, 3, 4) else 0
    if base not in DRAWER_CAPABLE:
        n_draw = 0
    return ResolvedDraftingTableConfig(
        support_base=base,
        angle_mechanism=mech,
        control_handle=ctrl,
        n_drawers=n_draw,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        board_width_scale=_clamp(cfg.board_width_scale, 0.95, 1.08),
        board_depth_scale=_clamp(cfg.board_depth_scale, 0.97, 1.05),
        tilt_lower=_clamp(cfg.tilt_lower, -0.30, -0.20),
        tilt_upper=_clamp(cfg.tilt_upper, 0.45, 0.65),
        name=cfg.name or "drafting_table",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedDraftingTableConfig) else resolve_config(config)
    return (
        ("support_base", r.support_base),
        ("angle_mechanism", r.angle_mechanism),
        ("control_handle", r.control_handle),
        ("n_drawers", f"n{r.n_drawers}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared upper-frame interface (present on every base's mount part)
# ===========================================================================
def _emit_upper_frame(mount, mats, metal) -> None:
    """The rigid rectangular upper frame at the board line + hinge/knob hardware.
    Emitted for every base so the tabletop, controls, mechanism and drawers mate
    identically. All members mutually overlap into one connected cluster."""
    grey = mats["grey"]
    for idx, sx in SIDES:
        # Level side rails at the frame top (below the flat board).
        _beam(mount, (sx * SIDE_X, -0.34, TOP_Z), (sx * SIDE_X, 0.34, TOP_Z), TUBE, metal, f"top_side_rail_{idx}")
    # Front hinge rail (spans full width; guarantees the board is carried across width).
    _beam(mount, (-0.58, HINGE_Y, RAIL_Z), (0.58, HINGE_Y, RAIL_Z), TUBE, metal, "front_hinge_rail")
    _beam(mount, (-SIDE_X, REAR_RAIL_Y, TOP_Z), (SIDE_X, REAR_RAIL_Y, TOP_Z), TUBE, metal, "rear_top_rail")
    # Captured hinge pin + end brackets (bracket bridges pin to hinge rail; kept
    # below the board panel so the tilting board clears it at every angle).
    _cyl(mount, 0.012, 1.18, (0.0, HINGE_Y, HINGE_Z), grey, "hinge_pin", rpy=(0.0, math.pi / 2.0, 0.0))
    for idx, sx in SIDES:
        _box(mount, (0.030, 0.050, 0.050), (sx * 0.585, HINGE_Y, 0.728), grey, f"hinge_end_bracket_{idx}")
        # Side knob socket + mount tab bridging the socket up into the side rail.
        _cyl(mount, 0.030, 0.034, (sx * KNOB_SOCKET_X, KNOB_Y, KNOB_Z), grey, f"knob_socket_{idx}", rpy=(0.0, math.pi / 2.0, 0.0))
        _box(mount, (0.024, 0.044, 0.310), (sx * KNOB_SOCKET_X, KNOB_Y, 0.583), grey, f"knob_mount_tab_{idx}")


# ===========================================================================
# Slot A: support_base — grounded legs built up to the shared upper frame.
# Returns the ``mount`` part everything else parents to.
# ===========================================================================
def _build_support_base(model, r: ResolvedDraftingTableConfig, mats):
    metal = mats["wood"] if r.support_base in WOOD_FRAMED else mats["metal"]
    if r.is_telescoping:
        return _base_telescoping(model, r, mats, mats["metal"])
    mount = model.part("frame")
    _emit_upper_frame(mount, mats, mats["metal"] if r.support_base not in WOOD_FRAMED else mats["metal"])
    builder = {
        "cantilever_zframe": _legs_cantilever,
        "splayed_xbrace": _legs_xbrace,
        "wood_trestle": _legs_trestle,
        "pedestal_column": _legs_pedestal,
        "four_post": _legs_four_post,
    }[r.support_base]
    builder(mount, r, mats, metal)
    return mount


def _legs_xbrace(mount, r, mats, metal) -> None:
    """Origin 002: splayed legs + floor runners + X side braces."""
    grey = mats["grey"]
    for idx, sx in SIDES:
        x = sx * SIDE_X
        _beam(mount, (x, -0.46, FLOOR_Z), (x, -0.34, TOP_Z), TUBE, metal, f"front_leg_{idx}")
        _beam(mount, (x, 0.46, FLOOR_Z), (x, 0.34, TOP_Z), TUBE, metal, f"rear_leg_{idx}")
        _beam(mount, (x, -0.50, 0.040), (x, 0.50, 0.040), TUBE, metal, f"floor_runner_{idx}")
        _beam(mount, (x, -0.34, 0.700), (x, 0.08, 0.330), 0.026, metal, f"side_brace_{idx}")
        _beam(mount, (x, 0.08, 0.330), (x, 0.38, 0.055), 0.026, metal, f"rear_kick_brace_{idx}")
    _beam(mount, (-SIDE_X, 0.105, 0.325), (SIDE_X, 0.105, 0.325), 0.028, metal, "low_crossbar")


def _legs_cantilever(mount, r, mats, metal) -> None:
    """Origin 001: splayed Z-frame with foot bars + basket rails + leveling feet."""
    rubber = mats["plastic"]
    for idx, sx in SIDES:
        x = sx * SIDE_X
        _beam(mount, (x, -0.48, 0.045), (x, 0.36, 0.045), 0.045, metal, f"foot_bar_{idx}")
        _beam(mount, (x, -0.44, 0.075), (x, -0.34, TOP_Z), 0.044, metal, f"front_leg_{idx}")
        _beam(mount, (x, 0.34, 0.075), (x, 0.34, TOP_Z), 0.044, metal, f"rear_leg_{idx}")
        _beam(mount, (x, -0.34, 0.330), (x, -0.34, 0.560), 0.030, metal, f"basket_side_{idx}")
    _beam(mount, (-SIDE_X, -0.34, 0.330), (SIDE_X, -0.34, 0.330), 0.032, metal, "basket_bottom_rail")
    _beam(mount, (-SIDE_X, -0.34, 0.560), (SIDE_X, -0.34, 0.560), 0.032, metal, "basket_top_rail")
    _beam(mount, (-SIDE_X, 0.32, 0.10), (SIDE_X, 0.32, 0.10), 0.030, metal, "rear_low_crossbar")
    for i, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        _cyl(mount, 0.040, 0.020, (sx * SIDE_X, sy * (0.48 if sy < 0 else 0.36), 0.0125), rubber, f"leveling_foot_{i}")


def _legs_trestle(mount, r, mats, metal) -> None:
    """Origin 003: wood trestle — a left + right A-frame end assembly (front-leaning
    + rear-leaning uprights meeting near the frame top), tied by lengthwise
    stretchers in X (wood material)."""
    wood = mats["wood"]
    wood_dark = mats["wood_edge"]
    for idx, sx in SIDES:
        x = sx * 0.50  # inboard of the side knob assembly (x ~ 0.55-0.60)
        # Foot runner grows up to z~0.09 so the splayed upright bottoms (lowest
        # point ~z=0.077 at y=-0.38/+0.38) seat into it -> foot island stays joined.
        _box(mount, (0.11, 0.82, 0.090), (x, 0.0, 0.045), wood, f"floor_foot_{idx}")
        _box(mount, (0.16, 0.24, 0.14), (x, 0.0, 0.14), wood_dark, f"foot_block_{idx}")
        # Steep uprights: at knob height (z~0.455) they sit near y~-0.24 / +0.24,
        # clear of the side knob at y=-0.175.
        _beam(mount, (x, -0.38, 0.10), (x, -0.14, TOP_Z), 0.078, wood, f"front_upright_{idx}")
        _beam(mount, (x, 0.38, 0.10), (x, 0.14, TOP_Z), 0.078, wood, f"rear_upright_{idx}")
        # Cap tying the two upright tops out to the level side rail.
        _beam(mount, (x, -0.14, TOP_Z), (sx * SIDE_X, 0.14, TOP_Z), 0.055, wood, f"trestle_cap_{idx}")
    # Lengthwise stretchers connect the left + right end frames.
    _box(mount, (1.06, 0.06, 0.055), (0.0, -0.32, 0.235), wood, "lower_front_stretcher")
    _box(mount, (1.06, 0.055, 0.055), (0.0, 0.32, 0.215), wood_dark, "lower_rear_stretcher")
    # Mid stretcher tied onto the FRONT uprights (at z=0.36 they sit at y~-0.279);
    # a y=0 member would float free, so it rides the front pair as a real brace.
    _box(mount, (1.06, 0.055, 0.055), (0.0, -0.279, 0.360), wood, "mid_cross_stretcher")


def _legs_pedestal(mount, r, mats, metal) -> None:
    """Fork base_column: cruciform foot + central column + fabricated yoke head."""
    grey = mats["grey"]
    worn = mats["wood_edge"]
    foot_h = 0.028
    _box(mount, (0.64, 0.055, foot_h), (0.0, 0.0, foot_h / 2.0), metal, "foot_arm_0")
    _box(mount, (0.055, 0.54, foot_h), (0.0, 0.0, foot_h / 2.0), metal, "foot_arm_1")
    for i, (px, py) in enumerate(((0.32, 0.0), (-0.32, 0.0), (0.0, 0.27), (0.0, -0.27))):
        _cyl(mount, 0.024, 0.014, (px, py, 0.007), worn, f"foot_pad_{i}")
    col_top = 0.695
    _cyl(mount, 0.045, col_top - foot_h, (0.0, -0.02, foot_h + (col_top - foot_h) / 2.0), metal, "pedestal_column")
    _cyl(mount, 0.058, 0.040, (0.0, -0.02, col_top - 0.020), grey, "column_collar")
    _beam(mount, (-0.50, -0.12, col_top), (0.50, -0.12, col_top), 0.040, metal, "yoke_crossbar")
    _beam(mount, (0.0, -0.12, col_top), (0.0, HINGE_Y, RAIL_Z), 0.035, metal, "yoke_front_arm")
    _beam(mount, (0.0, -0.12, col_top), (0.0, 0.22, col_top), 0.030, metal, "yoke_rear_arm")
    for idx, sx in SIDES:
        _beam(mount, (sx * 0.50, -0.12, col_top), (sx * SIDE_X, 0.10, TOP_Z), 0.026, metal, f"yoke_side_strut_{idx}")
        _beam(mount, (sx * 0.50, -0.12, col_top), (sx * KNOB_SOCKET_X, KNOB_Y, 0.60), 0.024, metal, f"yoke_knob_strut_{idx}")


def _legs_four_post(mount, r, mats, metal) -> None:
    """Fork base_fourpost: four straight corner posts + box apron + side stretchers."""
    apron_z = 0.69
    posts = (("0", -1.0, -1.0), ("1", 1.0, -1.0), ("2", -1.0, 1.0), ("3", 1.0, 1.0))
    for tag, sx, sy in posts:
        py = -0.34 if sy < 0 else 0.34
        _beam(mount, (sx * SIDE_X, py, 0.02), (sx * SIDE_X, py, TOP_Z), 0.040, metal, f"leg_{tag}")
    _beam(mount, (-SIDE_X, -0.34, apron_z), (SIDE_X, -0.34, apron_z), TUBE, metal, "front_apron")
    _beam(mount, (-SIDE_X, 0.34, apron_z), (SIDE_X, 0.34, apron_z), TUBE, metal, "rear_apron")
    _beam(mount, (-SIDE_X, -0.34, apron_z), (-SIDE_X, 0.34, apron_z), TUBE, metal, "left_apron")
    _beam(mount, (SIDE_X, -0.34, apron_z), (SIDE_X, 0.34, apron_z), TUBE, metal, "right_apron")
    for idx, sx in SIDES:
        _beam(mount, (sx * SIDE_X, -0.34, 0.30), (sx * SIDE_X, 0.34, 0.30), 0.028, metal, f"side_stretcher_{idx}")


def _base_telescoping(model, r, mats, metal):
    """Fork mech_height: grounded ``base`` (outer sleeves) + PRISMATIC ``carriage``
    (= mount, inner tubes + upper frame)."""
    grey = mats["grey"]
    steel = mats["steel"]
    base = model.part("base")
    for idx, sx in SIDES:
        x = sx * SIDE_X
        _beam(base, (x, -0.50, 0.040), (x, 0.50, 0.040), TUBE, metal, f"floor_runner_{idx}")
        _beam(base, (x, -0.46, FLOOR_Z), (x, -0.378, 0.420), 0.042, metal, f"outer_front_sleeve_{idx}")
        _beam(base, (x, 0.46, FLOOR_Z), (x, 0.367, 0.459), 0.042, metal, f"outer_rear_sleeve_{idx}")
        _box(base, (0.058, 0.058, 0.032), (x, -0.378, 0.434), grey, f"front_sleeve_collar_{idx}")
        _box(base, (0.058, 0.058, 0.032), (x, 0.367, 0.474), grey, f"rear_sleeve_collar_{idx}")
    _beam(base, (-SIDE_X, -0.435, 0.15), (SIDE_X, -0.435, 0.15), 0.028, metal, "front_lower_crossbar")
    _beam(base, (-SIDE_X, 0.435, 0.15), (SIDE_X, 0.435, 0.15), 0.028, metal, "rear_lower_crossbar")

    carriage = model.part("carriage")
    _emit_upper_frame(carriage, mats, metal)
    for idx, sx in SIDES:
        x = sx * SIDE_X
        _beam(carriage, (x, -0.425, 0.200), (x, -0.34, TOP_Z), 0.030, steel, f"inner_front_tube_{idx}")
        _beam(carriage, (x, 0.424, 0.200), (x, 0.34, TOP_Z), 0.030, steel, f"inner_rear_tube_{idx}")
    model.articulation(
        "base_to_carriage", ArticulationType.PRISMATIC, parent=base, child=carriage,
        origin=Origin(xyz=(0.0, 0.0, 0.0)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.08, lower=0.0, upper=0.15),
    )
    return carriage


# ===========================================================================
# Constant layer: the tilting drawing board (carried by the mount chassis).
# ===========================================================================
def _emit_tabletop(model, mount, r: ResolvedDraftingTableConfig, mats):
    wood = mats["wood"]
    wood_edge = mats["wood_edge"]
    grey = mats["grey"]
    metal = mats["metal"]
    hw = r.half_width
    depth = r.board_depth
    top = model.part("tabletop")
    # Board authored flat in its own frame; the joint applies the ~20deg pre-tilt.
    _box(top, (2 * hw, depth, 0.040), (0.0, 0.5 * depth, 0.035), wood, "wood_drawing_board")
    # Dark raised perimeter lips (embed into the board so they connect).
    _box(top, (2 * hw + 0.06, 0.045, 0.060), (0.0, 0.015, 0.050), wood_edge, "front_lip")
    _box(top, (2 * hw + 0.04, 0.038, 0.050), (0.0, depth + 0.005, 0.055), wood_edge, "rear_lip")
    for idx, sx in SIDES:
        _box(top, (0.045, depth + 0.02, 0.055), (sx * (hw + 0.010), 0.5 * depth + 0.01, 0.055), wood_edge, f"side_lip_{idx}")
        _box(top, (0.030, 0.52 * (depth / BOARD_D), 0.020), (sx * (hw - 0.045), 0.5 * depth + 0.015, 0.050), metal, f"paper_channel_{idx}")
    # Front paper stop / parallel-rule bar (embeds into the board top).
    _box(top, (2 * hw - 0.16, 0.022, 0.020), (0.0, 0.105, 0.048), metal, "paper_stop")
    # Tilt barrel (captured around the frame hinge pin); part origin sits on it.
    # Standardized hinge hardware length (independent of board width) so it never
    # reaches the side hinge-end brackets.
    _cyl(top, 0.021, 1.12, (0.0, -0.006, 0.018), grey, "tilt_barrel", rpy=(0.0, math.pi / 2.0, 0.0))
    # Host-conformal grain streaks embedded into the board top.
    grain_rows = (
        (-0.12, 0.155, 0.78, mats["grain_b"]), (-0.06, 0.195, 0.84, mats["grain_a"]),
        (-0.18, 0.240, 0.72, mats["grain_b"]), (0.02, 0.285, 0.86, mats["grain_a"]),
        (-0.08, 0.330, 0.80, mats["grain_b"]), (0.10, 0.375, 0.70, mats["grain_a"]),
        (-0.04, 0.420, 0.82, mats["grain_b"]), (0.05, 0.465, 0.76, mats["grain_a"]),
        (-0.16, 0.510, 0.68, mats["grain_b"]), (0.00, 0.555, 0.84, mats["grain_a"]),
        (-0.09, 0.605, 0.74, mats["grain_b"]), (0.12, 0.650, 0.62, mats["grain_a"]),
    )
    wscale = min(1.0, r.board_width_scale)
    for i, (x, y, length, material) in enumerate(grain_rows):
        yy = y * (depth / BOARD_D)
        _box(top, (length * wscale, 0.005, 0.006), (x * r.board_width_scale, yy, 0.050), material, f"wood_grain_{i}",
             rpy=(0.0, 0.0, 0.025 * (-1 if i % 2 else 1)))
    model.articulation(
        "frame_to_tabletop", ArticulationType.REVOLUTE, parent=mount, child=top,
        origin=Origin(xyz=(0.0, HINGE_Y, HINGE_Z), rpy=(math.radians(20.0), 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.45, lower=r.tilt_lower, upper=r.tilt_upper),
    )
    return top


# ===========================================================================
# Slot B: angle_mechanism — non-articulating hardware (host visuals on mount).
# ===========================================================================
def _emit_angle_mechanism(mount, r: ResolvedDraftingTableConfig, mats):
    metal = mats["wood"] if r.support_base in WOOD_FRAMED else mats["metal"]
    grey = mats["grey"]
    # All angle-hold hardware lives in the near-hinge, under-board zone (z <= 0.72)
    # that the tilting board provably clears (like the front hinge rail).
    if r.angle_mechanism == "friction_knob_lock":
        # Origin 001: plain side hinge cheeks, no teeth (friction hold).
        for idx, sx in SIDES:
            _box(mount, (0.055, 0.080, 0.090), (sx * 0.515, HINGE_Y + 0.020, 0.685), metal, f"hinge_cheek_{idx}")
    elif r.angle_mechanism == "linear_toothed_ratchet":
        # Origin 002: two toothed ratchet racks under the board, near the hinge.
        y0, z0, y1, z1 = -0.28, 0.520, -0.08, 0.700
        for idx, sx in SIDES:
            _beam(mount, (sx * 0.525, y0, z0), (sx * 0.525, y1, z1), 0.020, grey, f"ratchet_backbone_{idx}")
            # Bracket tying the backbone to the side knob mount tab (support path).
            _beam(mount, (sx * 0.525, y0, z0 + 0.010), (sx * KNOB_SOCKET_X, KNOB_Y, z0 + 0.010), 0.018, grey, f"ratchet_mount_{idx}")
            for tooth in range(6):
                t = tooth / 5.0
                _box(mount, (0.026, 0.030, 0.018), (sx * 0.525, y0 + t * (y1 - y0), z0 + t * (z1 - z0)), grey, f"ratchet_tooth_{idx}_{tooth}")
    else:  # curved_ratchet_quadrant
        # Origin 003: annular quadrant plate (YZ plane about the +X tilt axis).
        cy, cz, radius = -0.18, 0.540, 0.150
        a0, a1 = math.radians(15.0), math.radians(115.0)
        for idx, sx in SIDES:
            arc = _annular_sector_yz(
                center_y=cy, center_z=cz, radius=radius, radial_width=0.018,
                x_center=sx * 0.525, x_thickness=0.024, start_angle=a0, end_angle=a1, segments=40,
            )
            mount.visual(mesh_from_geometry(arc, f"ratchet_arc_plate_{idx}"), material=grey, name=f"ratchet_arc_plate_{idx}", material_class_id="metal.blackened_gunmetal")
            # Mount ties the arc mid-span to the side knob mount tab (support path).
            am = (a0 + a1) * 0.5
            _beam(mount, (sx * 0.525, cy + radius * math.cos(am), cz + radius * math.sin(am)),
                  (sx * KNOB_SOCKET_X, KNOB_Y, 0.600), 0.018, grey, f"arc_mount_{idx}")


# ===========================================================================
# Slot C: control_handle — 2 REVOLUTE lock controls (children of mount).
# ===========================================================================
def _knob_disk(part, sx, mats) -> None:
    plastic = mats["plastic"]
    grey = mats["grey"]
    _cyl(part, 0.055, 0.026, (0.0, 0.0, 0.0), plastic, "knob_disk", rpy=(0.0, math.pi / 2.0, 0.0))
    _cyl(part, 0.014, 0.090, (-sx * 0.045, 0.0, 0.0), grey, "knob_shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    for k, angle in enumerate((0.0, math.pi / 3.0, 2.0 * math.pi / 3.0)):
        _box(part, (0.012, 0.080, 0.010), (sx * 0.026, 0.0, 0.004), grey, f"grip_rib_{k}", rpy=(0.0, math.pi / 2.0, angle))


def _knob_lobed(part, sx, mats, *, radius: float, height: float, count: int) -> None:
    grey = mats["grey"]
    metal = mats["metal"]
    _cyl(part, 0.014, 0.090, (-sx * 0.045, 0.0, 0.0), grey, "knob_shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    mesh = mesh_from_geometry(
        KnobGeometry(radius, height, body_style="lobed", base_diameter=radius * 0.75,
                     top_diameter=radius * 0.90, grip=KnobGrip(style="ribbed", count=count, depth=0.002)),
        f"lobed_knob_{sx:.0f}",
    )
    part.visual(mesh, origin=Origin(xyz=(sx * 0.004, 0.0, 0.0), rpy=(0.0, sx * math.pi / 2.0, 0.0)), material=metal, name="lobed_knob", material_class_id="metal.paint_coated")


def _crank_handle(part, sx, mats) -> None:
    steel = mats["steel"]
    black = mats["metal"]
    _cyl(part, 0.014, 0.090, (-sx * 0.045, 0.0, 0.0), steel, "knob_shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    _cyl(part, 0.016, 0.010, (0.0, 0.0, 0.0), steel, "crank_hub", rpy=(0.0, math.pi / 2.0, 0.0))
    arm_reach_y = 0.085
    arm_drop_z = 0.022
    arm_span = math.sqrt(arm_reach_y ** 2 + arm_drop_z ** 2)
    arm_pitch = math.atan2(arm_drop_z, arm_reach_y)
    part.visual(Box((0.014, arm_span, 0.012)), origin=Origin(xyz=(0.0, -arm_reach_y * 0.5, -arm_drop_z * 0.5), rpy=(arm_pitch, 0.0, 0.0)),
                material=steel, name="crank_arm", material_class_id="metal.steel_bare")
    _cyl(part, 0.011, 0.048, (0.0, -arm_reach_y, -arm_drop_z), black, "crank_grip", rpy=(0.0, math.pi / 2.0, 0.0))


def _emit_control(model, mount, r: ResolvedDraftingTableConfig, mats):
    parts = []
    for idx, sx in SIDES:
        name = f"lock_control_{idx}"
        part = model.part(name)
        if r.control_handle == "paired_symmetric_knobs":
            _knob_disk(part, sx, mats)
        elif r.control_handle == "differentiated_knobs":
            # Left large, right small (heterogeneous lobed knobs).
            if sx < 0:
                _knob_lobed(part, sx, mats, radius=0.070, height=0.030, count=10)
            else:
                _knob_lobed(part, sx, mats, radius=0.044, height=0.024, count=8)
        else:  # crank_winder
            _crank_handle(part, sx, mats)
        model.articulation(
            f"frame_to_{name}", ArticulationType.REVOLUTE, parent=mount, child=part,
            origin=Origin(xyz=(sx * KNOB_JOINT_X, KNOB_Y, KNOB_Z)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=4.0, lower=-math.pi, upper=math.pi),
        )
        parts.append(name)
    return parts


# ===========================================================================
# Multiplicity: drawer bank — cosmetic FIXED faces on the mount front apron.
# ===========================================================================
def _emit_drawers(mount, r: ResolvedDraftingTableConfig, mats):
    n = r.n_drawers
    if n <= 0:
        return
    metal = mats["metal"]
    pale = mats["pale"]
    grey = mats["grey"]
    dark = mats["dark"]
    steel = mats["steel"]
    # Tray shelf + rails hung under the board front (connects to knob mount tabs).
    _box(mount, (2 * SIDE_X - 0.02, 0.18, 0.020), (0.0, -0.295, 0.645), metal, "front_supply_tray")
    _beam(mount, (-SIDE_X, -0.205, 0.655), (SIDE_X, -0.205, 0.655), 0.030, metal, "tray_rear_rail")
    _beam(mount, (-SIDE_X, -0.385, 0.655), (SIDE_X, -0.385, 0.655), 0.030, metal, "tray_front_rail")
    apron_half = SIDE_X - 0.06
    cell_w = (2.0 * apron_half) / n
    ring_mesh = mesh_from_geometry(TorusGeometry(0.030, 0.006, radial_segments=16, tubular_segments=28), "drawer_pull_ring")
    for i in range(n - 1):
        div_x = -apron_half + cell_w * (i + 1)
        _box(mount, (0.014, 0.020, 0.062), (div_x, -0.392, 0.685), dark, f"drawer_divider_{i}")
    for i in range(n):
        cx = -apron_half + cell_w * (i + 0.5)
        _box(mount, (cell_w - 0.03, 0.014, 0.055), (cx, -0.392, 0.682), pale, f"drawer_face_{i}")
        _cyl(mount, 0.026, 0.012, (cx, -0.399, 0.682), steel, f"pull_mount_{i}", rpy=(math.pi / 2.0, 0.0, 0.0))
        mount.visual(ring_mesh, origin=Origin(xyz=(cx, -0.405, 0.682), rpy=(math.pi / 2.0, 0.0, 0.0)), material=grey, name=f"pull_ring_{i}", material_class_id="metal.stainless_matte")


# ===========================================================================
# Assembly
# ===========================================================================
def build_drafting_table(config: DraftingTableConfig | None = None, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets, meta={"category": "Workspace / Drafting table"})
    base_rgba = dict(PALETTES[r.palette_style])
    base_rgba.update(_HARDWARE)
    mats = {k: model.material(f"draft_{k}_{r.palette_style}", rgba=v) for k, v in base_rgba.items()}

    mount = _build_support_base(model, r, mats)
    _emit_angle_mechanism(mount, r, mats)
    _emit_tabletop(model, mount, r, mats)
    _emit_control(model, mount, r, mats)
    _emit_drawers(mount, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_drafting_table(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_drafting_table(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_captured_pins(ctx, model, mount_name: str, r: ResolvedDraftingTableConfig) -> None:
    mount = model.get_part(mount_name)
    tabletop = model.get_part("tabletop")
    # Hinge: board barrel captured around the frame hinge pin.
    ctx.allow_overlap(mount, tabletop, elem_a="hinge_pin", elem_b="tilt_barrel",
                      reason="The tabletop hinge barrel is intentionally represented around the frame hinge pin.")
    # Controls: shaft/stem seated in the side socket.
    for idx, sx in SIDES:
        ctrl = model.get_part(f"lock_control_{idx}")
        ctx.allow_overlap(mount, ctrl, elem_a=f"knob_socket_{idx}", elem_b="knob_shaft",
                          reason="The lock control shaft intentionally seats in the side bushing.")
        ctx.allow_overlap(mount, ctrl, elem_a=f"knob_mount_tab_{idx}", elem_b="knob_shaft",
                          reason="The control shaft passes the side mount tab into the socket.")
    if r.is_telescoping:
        base = model.get_part("base")
        carriage = model.get_part("carriage")
        for idx, sx in SIDES:
            ctx.allow_overlap(base, carriage, elem_a=f"outer_front_sleeve_{idx}", elem_b=f"inner_front_tube_{idx}",
                              reason="Inner front tube slides inside the outer front sleeve.")
            ctx.allow_overlap(base, carriage, elem_a=f"outer_rear_sleeve_{idx}", elem_b=f"inner_rear_tube_{idx}",
                              reason="Inner rear tube slides inside the outer rear sleeve.")
            ctx.allow_overlap(base, carriage, elem_a=f"front_sleeve_collar_{idx}", elem_b=f"inner_front_tube_{idx}",
                              reason="Front sleeve collar wraps the inner tube as a visible clamp.")
            ctx.allow_overlap(base, carriage, elem_a=f"rear_sleeve_collar_{idx}", elem_b=f"inner_rear_tube_{idx}",
                              reason="Rear sleeve collar wraps the inner tube as a visible clamp.")


def run_drafting_table_tests(object_model: ArticulatedObject, config: DraftingTableConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    mount_name = "carriage" if r.is_telescoping else "frame"

    _allow_captured_pins(ctx, object_model, mount_name, r)

    mount = object_model.get_part(mount_name)
    tabletop = object_model.get_part("tabletop")
    tilt = object_model.get_articulation("frame_to_tabletop")

    # ---- Identity: tilting board + rotary lock controls. ----
    ctx.check(
        "drafting table has an articulated tilt top",
        tilt.articulation_type == ArticulationType.REVOLUTE
        and tilt.motion_limits is not None
        and tilt.motion_limits.lower is not None and tilt.motion_limits.upper is not None
        and tilt.motion_limits.lower < 0.0 and tilt.motion_limits.upper > 0.40,
        details=f"limits={tilt.motion_limits}",
    )
    for idx, sx in SIDES:
        j = object_model.get_articulation(f"frame_to_lock_control_{idx}")
        ctx.check(
            f"lock_control_{idx} is a rotary control",
            j.articulation_type == ArticulationType.REVOLUTE
            and j.motion_limits is not None and j.motion_limits.upper is not None
            and j.motion_limits.upper >= math.pi,
            details=f"type={j.articulation_type}, limits={j.motion_limits}",
        )

    # Wide board carried across the frame width.
    ctx.expect_overlap(mount, tabletop, axes="x", elem_b="wood_drawing_board", min_overlap=1.0,
                       name="wide table top is carried by the frame width")

    # ---- Targeted mechanism poses. ----
    rest = ctx.part_world_aabb(tabletop)
    with ctx.pose({tilt: r.tilt_upper}):
        raised = ctx.part_world_aabb(tabletop)
    ctx.check(
        "positive tabletop tilt raises the rear edge",
        rest is not None and raised is not None and raised[1][2] > rest[1][2] + 0.12,
        details=f"rest={rest}, raised={raised}",
    )
    for idx, sx in SIDES:
        ctrl = object_model.get_part(f"lock_control_{idx}")
        j = object_model.get_articulation(f"frame_to_lock_control_{idx}")
        before = ctx.part_world_position(ctrl)
        with ctx.pose({j: 1.2}):
            after = ctx.part_world_position(ctrl)
        ctx.check(
            f"lock_control_{idx} spins in place",
            before is not None and after is not None and max(abs(before[k] - after[k]) for k in range(3)) < 1e-6,
            details=f"before={before}, after={after}",
        )

    if r.is_telescoping:
        base = object_model.get_part("base")
        carriage = object_model.get_part("carriage")
        hj = object_model.get_articulation("base_to_carriage")
        ctx.check("height joint is PRISMATIC +Z", hj.articulation_type == ArticulationType.PRISMATIC and abs(hj.axis[2]) > 0.99,
                  details=f"type={hj.articulation_type}, axis={hj.axis}")
        rest_pos = ctx.part_world_position(carriage)
        with ctx.pose({hj: 0.15}):
            up_pos = ctx.part_world_position(carriage)
        ctx.check(
            "base_to_carriage raises the carriage ~0.15 m",
            rest_pos is not None and up_pos is not None and abs((up_pos[2] - rest_pos[2]) - 0.15) < 0.003,
            details=f"rest_z={rest_pos[2] if rest_pos else None}, up_z={up_pos[2] if up_pos else None}",
        )
        for idx, sx in SIDES:
            ctx.expect_overlap(carriage, base, axes="z", elem_a=f"inner_front_tube_{idx}", elem_b=f"outer_front_sleeve_{idx}",
                               min_overlap=0.15, name=f"front tube {idx} well-inserted in sleeve at rest")

    # ---- n_drawers multiplicity. ----
    if r.n_drawers > 0:
        for i in range(r.n_drawers):
            ctx.check(f"drawer face {i} present", any(v.name == f"drawer_face_{i}" for v in mount.visuals),
                      details=f"drawer_face_{i} missing")

    # ---- Rule 5: full-travel non-穿模. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)

    # ---- Compiler-owned baseline. ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "SupportBase",
    "AngleMech",
    "Control",
    "PaletteStyle",
    "DraftingTableConfig",
    "ResolvedDraftingTableConfig",
    "build_drafting_table",
    "build_seeded_drafting_table",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_drafting_table_tests",
]
