# SPDX-License-Identifier: Apache-2.0

"""Container box — modular procedural template.

Category identity: an upright hollow storage / gift / shipping box (cardboard,
corrugated, solid wood keepsake, slatted crate). A rectangular ``box_shell``
(ROOT) rests on z=0, centered on (x=0, y=0). Its main articulation comes from a
*closure mechanism* that opens/closes about an edge/face. Optional interior
structure (lift-out tray / stacking lip / N compartment dividers) and a wall
surface treatment (solid / slatted / perforated) round out the topology.

Three parallel slots + one multiplicity axis (spec ``Container_Box.md``):

  * ``wall_surface`` (3) — how the ROOT ``box_shell`` mesh is emitted:
      - solid: outer box minus inner cavity (corrugated / finger-joint wood).
      - slatted: maple corner posts + walnut horizontal slat boards + gaps.
      - perforated: solid shell pierced by a regular grid of vent holes.
  * ``closure_mechanism`` (6, each >=1 non-fixed joint) — the active closure:
      - four_top_flaps: four REVOLUTE flaps about the top rim inner edges.
      - liftoff_telescoping_lid: a single PRISMATIC +Z lift-off skirted lid.
      - rear_hinged_flat_lid: a REVOLUTE -X flat lid hinged at the rear rim.
      - sliding_drawer: a PRISMATIC -Y matchbox tray out the front.
      - swing_double_door: two REVOLUTE +/-Z front doors.
      - front_drop_door: one REVOLUTE +X front panel folding down.
  * ``interior_structure`` (4, incl. ``plain``) — interior fixed visual /
    moving child:
      - plain: empty cavity.
      - liftout_tray: a shallow PRISMATIC +Z tray seated on an inner ledge.
      - stacking_lip: a raised inner rim lip + footing groove (fixed visuals).
      - compartment_dividers_N: N PRISMATIC +Z lift-out dividers (multiplicity
        axis, N in [1, 8]).

Continuous size/proportion variation (box height / footprint / wall thickness /
closure travel scales) lives in ``resolve_config`` as clamped params, never as
slot candidates.

Sources (articraft_data ``picture/Container/Box`` 5-star pool): 4 parents
(closed kraft shipping box ``0c476a9b``; kraft lift-off gift box ``3386fca8``;
walnut rear-hinge keepsake ``c87d6c10``; open corrugated four-flap ``ef4e9e5a``)
+ 9 converged forks (sliding_drawer / swing_double_door / front_drop_door
[roll_top record] / liftout_tray / stacking_lip / n2_dividers / n4_dividers /
slatted_walls / perforated_walls).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Box.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
ClosureMechanism = Literal[
    "four_top_flaps",
    "liftoff_telescoping_lid",
    "rear_hinged_flat_lid",
    "sliding_drawer",
    "swing_double_door",
    "front_drop_door",
]
InteriorStructure = Literal[
    "plain",
    "liftout_tray",
    "stacking_lip",
    "compartment_dividers_N",
]
WallSurface = Literal["solid", "slatted", "perforated"]
PaletteStyle = Literal[
    "kraft_corrugated",
    "white_gift",
    "white_gift_gloss",
    "walnut_keepsake",
    "natural_crate",
    "gray_shipping",
    "black_rigid_gift",
    "red_gift",
    "forest_gift",
    "printed_kraft",
]

CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "four_top_flaps",
    "liftoff_telescoping_lid",
    "rear_hinged_flat_lid",
    "sliding_drawer",
    "swing_double_door",
    "front_drop_door",
)
INTERIOR_STRUCTURES: tuple[InteriorStructure, ...] = (
    "plain",
    "liftout_tray",
    "stacking_lip",
    "compartment_dividers_N",
)
WALL_SURFACES: tuple[WallSurface, ...] = ("solid", "slatted", "perforated")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "kraft_corrugated",
    "white_gift",
    "white_gift_gloss",
    "walnut_keepsake",
    "natural_crate",
    "gray_shipping",
    "black_rigid_gift",
    "red_gift",
    "forest_gift",
    "printed_kraft",
)

# divider_count multiplicity axis — weighted toward small N (spec §Multiplicity).
DIVIDER_NS: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8)
DIVIDER_WEIGHTS: tuple[float, ...] = (
    0.10, 0.30, 0.22, 0.18, 0.10, 0.06, 0.025, 0.015,
)

# ---------------------------------------------------------------------------
# Palette: body (box_shell) + closure (lid/door/drawer) + interior + accent.
# finish is an explicit material-treatment dimension (matte / glossy / wood /
# satin / printed-graphic) carried alongside the rgba (spec palette table).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, object]] = {
    "kraft_corrugated": {
        "body": (0.78, 0.62, 0.40, 1.0),
        "closure": (0.80, 0.69, 0.49, 1.0),
        "interior": (0.72, 0.56, 0.36, 1.0),
        "accent": (0.20, 0.20, 0.22, 1.0),
        "finish": "kraft_corrugated_matte",
    },
    "white_gift": {
        "body": (0.93, 0.92, 0.90, 1.0),
        "closure": (0.95, 0.94, 0.92, 1.0),
        "interior": (0.90, 0.86, 0.78, 1.0),
        "accent": (0.55, 0.55, 0.58, 1.0),
        "finish": "white_gift_matte",
    },
    "white_gift_gloss": {
        "body": (0.96, 0.96, 0.95, 1.0),
        "closure": (0.97, 0.97, 0.96, 1.0),
        "interior": (0.88, 0.88, 0.90, 1.0),
        "accent": (0.78, 0.79, 0.82, 1.0),
        "finish": "white_gift_glossy",
    },
    "walnut_keepsake": {
        "body": (0.36, 0.22, 0.13, 1.0),
        "closure": (0.36, 0.22, 0.13, 1.0),
        "interior": (0.82, 0.66, 0.42, 1.0),
        "accent": (0.74, 0.58, 0.26, 1.0),
        "finish": "wood_grain_natural",
    },
    "natural_crate": {
        "body": (0.74, 0.60, 0.40, 1.0),
        "closure": (0.74, 0.60, 0.40, 1.0),
        "interior": (0.62, 0.46, 0.30, 1.0),
        "accent": (0.82, 0.66, 0.42, 1.0),
        "finish": "wood_grain_natural",
    },
    "gray_shipping": {
        "body": (0.62, 0.60, 0.58, 1.0),
        "closure": (0.62, 0.60, 0.58, 1.0),
        "interior": (0.56, 0.55, 0.53, 1.0),
        "accent": (0.20, 0.18, 0.15, 1.0),
        "finish": "shipping_board_matte",
    },
    "black_rigid_gift": {
        "body": (0.13, 0.13, 0.14, 1.0),
        "closure": (0.13, 0.13, 0.14, 1.0),
        "interior": (0.22, 0.22, 0.24, 1.0),
        "accent": (0.80, 0.66, 0.30, 1.0),
        "finish": "rigid_gift_black_matte",
    },
    "red_gift": {
        "body": (0.66, 0.16, 0.16, 1.0),
        "closure": (0.66, 0.16, 0.16, 1.0),
        "interior": (0.90, 0.86, 0.78, 1.0),
        "accent": (0.80, 0.66, 0.30, 1.0),
        "finish": "colored_gift_satin",
    },
    "forest_gift": {
        "body": (0.18, 0.34, 0.24, 1.0),
        "closure": (0.18, 0.34, 0.24, 1.0),
        "interior": (0.72, 0.56, 0.36, 1.0),
        "accent": (0.80, 0.66, 0.30, 1.0),
        "finish": "colored_gift_satin",
    },
    "printed_kraft": {
        "body": (0.78, 0.62, 0.40, 1.0),
        "closure": (0.80, 0.69, 0.49, 1.0),
        "interior": (0.72, 0.56, 0.36, 1.0),
        "accent": (0.16, 0.30, 0.42, 1.0),
        "finish": "printed_graphic",
    },
}

# ---------------------------------------------------------------------------
# Nominal box geometry (meters). A ~0.26 x 0.22 x 0.20 m rectangular box.
# Footprint centered at x=y=0, floor at z=0. LEN_X = long axis (X), DEP_Y =
# short axis / front-back (Y), HGT_Z = height (Z). Front wall is -Y.
# ---------------------------------------------------------------------------
_LEN_X = 0.260
_DEP_Y = 0.220
_HGT_Z = 0.200
_WALL = 0.006
_FLAP_T = 0.005
_SEAM = 0.0015

# Closure travel / clearance nominals.
_LID_LIFT = 0.060          # liftoff lid straight-up travel
_LID_SKIRT_H = 0.034       # liftoff lid skirt drop over the walls
_LID_TOP_T = 0.006
_LID_CLEAR = 0.0012
_DRAWER_RETAIN = 0.040     # tray inserted length kept inside at max pull
_TRAY_LIFT = 0.070         # liftout tray lift travel
_DIV_LIFT = 0.10           # divider lift travel
_MIN_COMPARTMENT = 0.018   # min compartment width (caps divider_count)

# slatted / perforated derived params.
_SLAT_H = 0.012
_SLAT_GAP = 0.010
_POST_SIZE = 0.016
_HOLE_D = 0.008
_HOLE_R = _HOLE_D / 2.0
_HOLE_PITCH = 0.026        # coarser than the 0.016 source to keep boolean fast
_HOLE_MARGIN = 0.018


@dataclass(frozen=True)
class ContainerBoxConfig:
    closure_mechanism: ClosureMechanism = "four_top_flaps"
    interior_structure: InteriorStructure = "plain"
    wall_surface: WallSurface = "solid"
    palette_style: PaletteStyle = "kraft_corrugated"
    divider_count: int = 2
    box_height_scale: float = 1.0
    box_footprint_scale: float = 1.0
    wall_thickness_scale: float = 1.0
    closure_travel_scale: float = 1.0
    name: str = "container_box"


@dataclass(frozen=True)
class ResolvedContainerBoxConfig:
    closure_mechanism: ClosureMechanism
    interior_structure: InteriorStructure
    wall_surface: WallSurface
    palette_style: PaletteStyle
    divider_count: int
    box_height_scale: float
    box_footprint_scale: float
    wall_thickness_scale: float
    closure_travel_scale: float
    # derived geometry
    len_x: float
    dep_y: float
    hgt_z: float
    wall: float
    flap_t: float
    # derived closure travels (already projected to be safe)
    lid_lift: float
    drawer_travel: float
    tray_lift: float
    div_lift: float
    name: str

    # --- convenience derived properties (cavity extents) ---
    @property
    def hx(self) -> float:
        return self.len_x / 2.0

    @property
    def hy(self) -> float:
        return self.dep_y / 2.0

    @property
    def inner_w(self) -> float:
        return self.len_x - 2.0 * self.wall

    @property
    def inner_d(self) -> float:
        return self.dep_y - 2.0 * self.wall

    @property
    def inner_h(self) -> float:
        return self.hgt_z - self.wall


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerBoxConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    closure = rng.choice(CLOSURE_MECHANISMS)
    interior = rng.choice(INTERIOR_STRUCTURES)
    wall = rng.choice(WALL_SURFACES)
    palette = rng.choice(PALETTE_STYLES)
    divider_count = rng.choices(DIVIDER_NS, weights=DIVIDER_WEIGHTS, k=1)[0]
    return ContainerBoxConfig(
        closure_mechanism=closure,
        interior_structure=interior,
        wall_surface=wall,
        palette_style=palette,
        divider_count=divider_count,
        box_height_scale=round(rng.uniform(0.85, 1.20), 4),
        box_footprint_scale=round(rng.uniform(0.88, 1.18), 4),
        wall_thickness_scale=round(rng.uniform(0.80, 1.25), 4),
        closure_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_box_{seed}",
    )


def resolve_config(
    config: ContainerBoxConfig | None = None,
) -> ResolvedContainerBoxConfig:
    cfg = config or ContainerBoxConfig()
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    interior = _pick(cfg.interior_structure, INTERIOR_STRUCTURES)
    wall_surface = _pick(cfg.wall_surface, WALL_SURFACES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    h_scale = _clamp(cfg.box_height_scale, 0.85, 1.20)
    fp_scale = _clamp(cfg.box_footprint_scale, 0.88, 1.18)
    wt_scale = _clamp(cfg.wall_thickness_scale, 0.80, 1.25)
    ct_scale = _clamp(cfg.closure_travel_scale, 0.85, 1.10)

    len_x = _LEN_X * fp_scale
    dep_y = _DEP_Y * fp_scale
    hgt_z = _HGT_Z * h_scale
    wall = _WALL * wt_scale
    flap_t = _FLAP_T * wt_scale

    inner_w = len_x - 2.0 * wall
    inner_d = dep_y - 2.0 * wall
    inner_h = hgt_z - wall  # cavity height above floor

    # --- divider_count: weighted sample already done; clamp to box-width cap ---
    max_dividers = max(1, int(inner_w / _MIN_COMPARTMENT) - 1)
    divider_count = int(_clamp(cfg.divider_count, 1, max_dividers))

    # --- closure travel inequality projection (travel <= usable - retain) ---
    # liftoff lid: lift may be generous; cap so it doesn't fly absurdly high.
    lid_lift = _clamp(_LID_LIFT * ct_scale, 0.02, hgt_z)
    # drawer: keep ~40 mm of tray inside the cavity at max pull (travel <=
    # cavity_depth - retain_margin).
    drawer_usable = max(inner_d - _DRAWER_RETAIN, 0.02)
    drawer_travel = _clamp(drawer_usable * ct_scale, 0.02, drawer_usable)
    # tray / divider lift: must not exceed the cavity height (do not pop the top
    # so far the part fully clears — keep a small retain so it reads as seated).
    tray_lift = _clamp(_TRAY_LIFT * ct_scale, 0.02, inner_h)
    div_lift = _clamp(_DIV_LIFT * ct_scale, 0.02, inner_h)

    return ResolvedContainerBoxConfig(
        closure_mechanism=closure,
        interior_structure=interior,
        wall_surface=wall_surface,
        palette_style=palette,
        divider_count=divider_count,
        box_height_scale=h_scale,
        box_footprint_scale=fp_scale,
        wall_thickness_scale=wt_scale,
        closure_travel_scale=ct_scale,
        len_x=len_x,
        dep_y=dep_y,
        hgt_z=hgt_z,
        wall=wall,
        flap_t=flap_t,
        lid_lift=lid_lift,
        drawer_travel=drawer_travel,
        tray_lift=tray_lift,
        div_lift=div_lift,
        name=cfg.name or "container_box",
    )


def slot_choices_for_config(
    config: ContainerBoxConfig | ResolvedContainerBoxConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerBoxConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [
        ("closure_mechanism", r.closure_mechanism),
        ("interior_structure", r.interior_structure),
        ("wall_surface", r.wall_surface),
    ]
    if r.interior_structure == "compartment_dividers_N":
        choices.append(("divider_count", f"n{r.divider_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shell openness flags (which faces the closure needs open / cut).
# ---------------------------------------------------------------------------
def _shell_flags(r: ResolvedContainerBoxConfig) -> dict[str, bool]:
    """Return which shell faces are open for the chosen closure.

    open_top:    cavity open through the top rim (flaps / rear-hinge lid /
                 liftoff lid seat on / cover the open top).
    front_opening: a rectangular hole cut in the front (-Y) wall (drawer).
    front_open:  the whole front (-Y) face removed (swing doors / drop door).
    """
    closure = r.closure_mechanism
    return {
        "open_top": closure in ("four_top_flaps", "liftoff_telescoping_lid", "rear_hinged_flat_lid"),
        "front_opening": closure == "sliding_drawer",
        "front_open": closure in ("swing_double_door", "front_drop_door"),
    }


# ---------------------------------------------------------------------------
# Slot C: wall_surface — the ROOT box_shell mesh. Three emission strategies.
# ---------------------------------------------------------------------------
def _solid_shell_solid(r: ResolvedContainerBoxConfig, flags: dict[str, bool]) -> cq.Workplane:
    """Solid hollow box shell (corrugated / finger-joint wood).

    Adapted from ``_shell_solid`` (ef4e9e5a) / ``_box_base_solid`` (c87d6c10).
    open_top punches the cavity through the rim; closed top leaves a top wall.
    front_opening cuts a drawer hole; front_open removes the whole front face.
    """
    len_x, dep_y, hgt_z, wall = r.len_x, r.dep_y, r.hgt_z, r.wall
    outer = cq.Workplane("XY").box(len_x, dep_y, hgt_z, centered=(True, True, False))

    if flags["open_top"]:
        cavity_h = hgt_z - wall + 0.01  # punch past the top rim
    else:
        cavity_h = hgt_z - 2.0 * wall   # leave a top wall

    cavity = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .box(len_x - 2.0 * wall, dep_y - 2.0 * wall, cavity_h, centered=(True, True, False))
    )
    shell = outer.cut(cavity)

    if flags["front_open"]:
        # Remove the entire front (-Y) wall between floor, ceiling, side walls.
        cav_w = len_x - 2.0 * wall
        cav_h = hgt_z - 2.0 * wall
        cav_d = dep_y - wall + 0.02
        cav_cy = (r.hy - wall) - cav_d / 2.0
        front_cut = (
            cq.Workplane("XY")
            .box(cav_w, cav_d, cav_h, centered=(True, True, True))
            .translate((0.0, cav_cy, wall + cav_h / 2.0))
        )
        shell = shell.cut(front_cut)
    elif flags["front_opening"]:
        # Rectangular drawer opening in the front (-Y) wall.
        open_w = len_x - 2.0 * wall - 0.004
        open_h = hgt_z - 2.0 * wall - 0.004
        open_cy = -r.hy + wall / 2.0
        open_cz = wall + 0.002 + open_h / 2.0
        front_cut = (
            cq.Workplane("XY")
            .box(open_w, wall + 0.010, open_h, centered=(True, True, True))
            .translate((0.0, open_cy, open_cz))
        )
        shell = shell.cut(front_cut)

    return shell


def _perforated_shell_solid(r: ResolvedContainerBoxConfig, flags: dict[str, bool]) -> cq.Workplane:
    """Solid shell pierced by a regular grid of vent holes.

    Adapted from ``_perforated_shell`` (perforated_walls record). Holes are cut
    only on walls that are not the closure opening; the floor stays solid.
    """
    shell = _solid_shell_solid(r, flags)
    hgt_z, wall = r.hgt_z, r.wall
    hx, hy = r.hx, r.hy
    cut_ext = wall + 0.004
    z_lo = wall + _HOLE_MARGIN
    z_hi = hgt_z - _HOLE_MARGIN

    def _grid(lo: float, hi: float) -> list[tuple[float, float]]:
        pts: list[tuple[float, float]] = []
        u = lo + _HOLE_MARGIN
        while u <= hi - _HOLE_MARGIN:
            v = z_lo
            while v <= z_hi:
                pts.append((u, v))
                v += _HOLE_PITCH
            u += _HOLE_PITCH
        return pts

    long_pts = _grid(-hx, hx)   # X/Z grid for +/-Y walls
    short_pts = _grid(-hy, hy)  # Y/Z grid for +/-X walls

    # Back (+Y) wall: always present.
    if long_pts:
        shell = shell.cut(
            cq.Workplane("XZ").workplane(offset=hy + 0.001)
            .pushPoints(long_pts).circle(_HOLE_R).extrude(-cut_ext)
        )
    # Front (-Y) wall: only when it is a real solid wall (no front opening/open).
    if long_pts and not (flags["front_open"] or flags["front_opening"]):
        shell = shell.cut(
            cq.Workplane("XZ").workplane(offset=-hy - 0.001)
            .pushPoints(long_pts).circle(_HOLE_R).extrude(cut_ext)
        )
    # Side (+/-X) walls: always present.
    if short_pts:
        shell = shell.cut(
            cq.Workplane("YZ").workplane(offset=hx + 0.001)
            .pushPoints(short_pts).circle(_HOLE_R).extrude(-cut_ext)
        )
        shell = shell.cut(
            cq.Workplane("YZ").workplane(offset=-hx - 0.001)
            .pushPoints(short_pts).circle(_HOLE_R).extrude(cut_ext)
        )
    return shell


def _slat_count(r: ResolvedContainerBoxConfig) -> int:
    """Number of slat boards per wall, derived from cavity height (controlled
    local parameterization, NOT an independent sampling axis)."""
    pitch = _SLAT_H + _SLAT_GAP
    return max(2, int(round((r.hgt_z - r.wall) / pitch)))


def _emit_slatted_shell(body, r: ResolvedContainerBoxConfig, flags: dict[str, bool],
                        *, body_mat, accent_mat) -> None:
    """Open-slatted crate walls: maple corner posts + walnut horizontal slats.

    Adapted from slatted_walls record (``_corner_posts_solid`` + ``_slat_board``
    loop + ``_floor_panel_solid``). The wall facing the closure opening is
    suppressed; remaining walls emit slats. Each board is a named visual on the
    box_shell part (no independent joint).
    """
    len_x, dep_y, hgt_z, wall = r.len_x, r.dep_y, r.hgt_z, r.wall
    half_w, half_d = r.hx, r.hy

    # Floor panel.
    body.visual(
        mesh_from_cadquery(
            cq.Workplane("XY").box(len_x, dep_y, wall, centered=(True, True, False)),
            "floor_panel",
        ),
        material=accent_mat,
        name="floor_panel", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"),
    )

    # Four corner posts.
    posts = None
    post_centers = [
        (half_w - _POST_SIZE / 2.0, half_d - _POST_SIZE / 2.0),
        (-half_w + _POST_SIZE / 2.0, half_d - _POST_SIZE / 2.0),
        (half_w - _POST_SIZE / 2.0, -half_d + _POST_SIZE / 2.0),
        (-half_w + _POST_SIZE / 2.0, -half_d + _POST_SIZE / 2.0),
    ]
    for px, py in post_centers:
        post = (
            cq.Workplane("XY").center(px, py)
            .box(_POST_SIZE, _POST_SIZE, hgt_z, centered=(True, True, False))
        )
        posts = post if posts is None else posts.union(post)
    body.visual(
        mesh_from_cadquery(posts, "corner_posts"),
        material=accent_mat,
        name="corner_posts", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"),
    )

    n_slats = _slat_count(r)
    slat_pitch = _SLAT_H + _SLAT_GAP
    fb_len = len_x - 2.0 * _POST_SIZE
    lr_len = dep_y - 2.0 * _POST_SIZE

    # Suppress the wall that hosts the closure opening so the closure can move.
    suppress_front = flags["front_open"] or flags["front_opening"]

    walls = [
        ("back", fb_len, 0.0, half_d - wall / 2.0, False),
        ("left", lr_len, -half_w + wall / 2.0, 0.0, True),
        ("right", lr_len, half_w - wall / 2.0, 0.0, True),
    ]
    if not suppress_front:
        walls.append(("front", fb_len, 0.0, -half_d + wall / 2.0, False))

    for wall_name, length, cx, cy, rotate in walls:
        for i in range(n_slats):
            z_base = wall + i * slat_pitch
            if z_base + _SLAT_H > hgt_z + 0.002:
                break
            slat = cq.Workplane("XY").box(length, wall, _SLAT_H, centered=(True, True, False))
            if rotate:
                slat = slat.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 90.0)
            slat = slat.translate((cx, cy, z_base))
            body.visual(
                mesh_from_cadquery(slat, f"{wall_name}_slat_{i}"),
                material=body_mat,
                name=f"{wall_name}_slat_{i}", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"),
            )


def _emit_box_shell(body, r: ResolvedContainerBoxConfig, flags: dict[str, bool],
                    *, body_mat, accent_mat) -> None:
    """Emit the ROOT box_shell mesh per wall_surface."""
    if r.wall_surface == "slatted":
        _emit_slatted_shell(body, r, flags, body_mat=body_mat, accent_mat=accent_mat)
        return
    if r.wall_surface == "perforated":
        solid = _perforated_shell_solid(r, flags)
    else:
        solid = _solid_shell_solid(r, flags)
    body.visual(mesh_from_cadquery(solid, "box_shell"), material=body_mat, name="box_shell", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))


# ---------------------------------------------------------------------------
# Slot A: closure_mechanism builders. Each emits its moving child + joint(s).
# ---------------------------------------------------------------------------
def _build_four_top_flaps(model, body, r: ResolvedContainerBoxConfig, *, closure_mat) -> None:
    """Four REVOLUTE flaps about the top rim inner edges (0c476a9b ``flap_defs``
    + ``box_to_{flap}`` loop; ef4e9e5a fold-out flaps)."""
    hgt_z, wall, flap_t = r.hgt_z, r.wall, r.flap_t
    in_hx = r.hx - wall
    in_hy = r.hy - wall
    long_len = r.inner_w - 0.002
    short_len = r.inner_d - 0.002
    long_reach = in_hy - _SEAM   # north/south flaps reach toward center in Y
    short_reach = in_hx - _SEAM  # east/west flaps reach toward center in X
    open_angle = math.radians(100.0)

    def _flap_slab(length: float, reach: float) -> cq.Workplane:
        # hinge edge at local y=0, slab reaches +Y, thickness hangs at -Z.
        return (
            cq.Workplane("XY").center(0.0, reach / 2.0)
            .box(length, reach, flap_t, centered=(True, True, False))
            .translate((0.0, 0.0, -flap_t))
        )

    # name, hinge xyz, axis, rot_z_deg (to point local +Y reach toward center).
    flap_defs = [
        ("flap_n", (0.0, in_hy, hgt_z), (-1.0, 0.0, 0.0), 180.0, long_len, long_reach),
        ("flap_s", (0.0, -in_hy, hgt_z), (1.0, 0.0, 0.0), 0.0, long_len, long_reach),
        ("flap_e", (in_hx, 0.0, hgt_z - flap_t), (0.0, 1.0, 0.0), 90.0, short_len, short_reach),
        ("flap_w", (-in_hx, 0.0, hgt_z - flap_t), (0.0, -1.0, 0.0), -90.0, short_len, short_reach),
    ]
    for name, hinge_xyz, axis, rot_deg, hinge_len, reach in flap_defs:
        flap = model.part(name)
        slab = _flap_slab(hinge_len, reach)
        flap.visual(
            mesh_from_cadquery(slab, name),
            origin=Origin(rpy=(0.0, 0.0, math.radians(rot_deg))),
            material=closure_mat,
            name=name, material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"),
        )
        flap.inertial = Inertial.from_geometry(
            Box((hinge_len, reach, flap_t)),
            mass=0.03,
            origin=Origin(xyz=_rot_z((0.0, reach / 2.0, -flap_t / 2.0), rot_deg)),
        )
        model.articulation(
            f"box_to_{name}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=flap,
            origin=Origin(xyz=hinge_xyz),
            axis=axis,
            motion_limits=MotionLimits(lower=0.0, upper=open_angle, effort=2.0, velocity=2.0),
        )


def _build_liftoff_lid(model, body, r: ResolvedContainerBoxConfig, *, closure_mat) -> None:
    """Single PRISMATIC +Z lift-off telescoping lid (3386fca8 ``box_to_lid``).

    The box top is open, so the joint origin is anchored on the real back-wall
    rim (``anchor_y``) rather than the empty rim center — otherwise
    ``fail_if_articulation_origin_far_from_geometry`` flags the air at the
    center. The lid mesh is authored shifted by ``-anchor_y`` so it stays
    centered over the footprint after the off-axis origin is applied; the lid
    skirt back wall passes through local y=0 so child geometry sits at the
    joint origin too (container_jar lift-off cap pattern).
    """
    lid_out = r.len_x + 2.0 * (_LID_CLEAR + r.wall)
    lid_out_y = r.dep_y + 2.0 * (_LID_CLEAR + r.wall)
    lid_wall = r.wall
    # Anchor the origin on a back corner post / wall top that is real, full-height
    # geometry for every wall_surface (slatted top slats can fall short of the
    # rim). The lid mesh is authored shifted by -(anchor) so it re-centers.
    anchor_x = -(r.hx - _POST_SIZE / 2.0)
    anchor_y = r.hy - _POST_SIZE / 2.0

    def _lid_solid() -> cq.Workplane:
        # top panel at local z=0, skirt hangs to -Z; authored shifted by -anchor
        # so after the off-axis origin the lid re-centers on the box.
        top = cq.Workplane("XY").box(lid_out, lid_out_y, _LID_TOP_T, centered=(True, True, False))
        skirt_outer = (
            cq.Workplane("XY").workplane(offset=-_LID_SKIRT_H)
            .box(lid_out, lid_out_y, _LID_SKIRT_H, centered=(True, True, False))
        )
        skirt_cavity = (
            cq.Workplane("XY").workplane(offset=-_LID_SKIRT_H - 0.001)
            .box(lid_out - 2.0 * lid_wall, lid_out_y - 2.0 * lid_wall,
                 _LID_SKIRT_H + 0.002, centered=(True, True, False))
        )
        return top.union(skirt_outer.cut(skirt_cavity)).translate((-anchor_x, -anchor_y, 0.0))

    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(_lid_solid(), "lid_shell"), material=closure_mat, name="lid_shell", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))
    lid.inertial = Inertial.from_geometry(
        Box((lid_out, lid_out_y, _LID_SKIRT_H + _LID_TOP_T)),
        mass=0.06,
        origin=Origin(xyz=(-anchor_x, -anchor_y, -_LID_SKIRT_H / 2.0)),
    )
    model.articulation(
        "box_to_lid",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(anchor_x, anchor_y, r.hgt_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.lid_lift, effort=5.0, velocity=0.2),
    )


def _build_rear_hinged_lid(model, body, r: ResolvedContainerBoxConfig,
                           *, closure_mat, accent_mat) -> None:
    """REVOLUTE -X flat lid hinged at the rear (+Y) top rim + brass knuckles
    (c87d6c10 ``base_to_lid`` + knuckle pattern)."""
    len_x, dep_y, hgt_z, wall = r.len_x, r.dep_y, r.hgt_z, r.wall
    lid_t = max(0.010, 1.2 * wall)
    hinge_y = r.hy - wall / 2.0
    hinge_z = hgt_z
    knuckle_r = min(0.006, wall)
    # For slatted walls there is no solid back rim, so seat the base knuckles
    # over the back corner posts (full-height solid). For solid/perforated the
    # back wall is solid, so spread them across the rear rim.
    if r.wall_surface == "slatted":
        kx_span = r.hx - _POST_SIZE / 2.0
        knuckle_z = hgt_z - knuckle_r - 0.001
    else:
        kx_span = min(0.055, len_x * 0.22)
        knuckle_z = hgt_z - knuckle_r - 0.001  # embed into the back wall rim

    def _lid_solid() -> cq.Workplane:
        # local frame: hinge line at y=0, lid extends toward -Y, top at z=0.
        return (
            cq.Workplane("XY").center(0.0, -dep_y / 2.0)
            .box(len_x, dep_y, lid_t, centered=(True, True, False))
            .translate((0.0, 0.0, -lid_t))
        )

    # Base knuckles on the box (fixed visuals embedded into the rear rim / posts).
    for i, kx in enumerate((-kx_span, kx_span)):
        knuckle = (
            cq.Workplane("YZ").workplane(offset=kx - 0.010)
            .center(hinge_y, knuckle_z).circle(knuckle_r).extrude(0.020)
        )
        body.visual(
            mesh_from_cadquery(knuckle, f"base_knuckle_{i}"),
            material=accent_mat,
            name=f"base_knuckle_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "black_rigid_gift", "red_gift", "forest_gift", "printed_kraft"} else "metal.blackened_gunmetal"),
        )

    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(_lid_solid(), "lid_slab"), material=closure_mat, name="lid_slab", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))
    # Lid-side interleaved knuckles on the hinge line. Lid-local origin is at the
    # hinge (world z=hinge_z); offset z so they sit on the same pin line as the
    # base knuckles, and offset x so they interleave between them.
    lid_knuckle_local_z = knuckle_z - hinge_z
    for i, kx in enumerate((-kx_span + 0.030, kx_span - 0.030)):
        knuckle = (
            cq.Workplane("YZ").workplane(offset=kx - 0.010)
            .center(0.0, lid_knuckle_local_z).circle(knuckle_r).extrude(0.020)
        )
        lid.visual(
            mesh_from_cadquery(knuckle, f"lid_knuckle_{i}"),
            material=accent_mat,
            name=f"lid_knuckle_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "black_rigid_gift", "red_gift", "forest_gift", "printed_kraft"} else "metal.blackened_gunmetal"),
        )
    lid.inertial = Inertial.from_geometry(
        Box((len_x, dep_y, lid_t)),
        mass=0.25,
        origin=Origin(xyz=(0.0, -dep_y / 2.0, -lid_t / 2.0)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=math.radians(100.0), effort=4.0, velocity=2.0),
    )


def _build_sliding_drawer(model, body, r: ResolvedContainerBoxConfig,
                          *, closure_mat, accent_mat) -> None:
    """PRISMATIC -Y matchbox drawer tray out the front (sliding_drawer record
    ``_drawer_tray`` + ``body_to_drawer``)."""
    len_x, dep_y, hgt_z, wall = r.len_x, r.dep_y, r.hgt_z, r.wall
    clear = 0.002
    draw_w = len_x - 2.0 * wall - 2.0 * clear
    draw_h = hgt_z - 2.0 * wall - 2.0 * clear
    draw_d = dep_y - 2.0 * wall - 2.0 * clear
    draw_wall = max(0.003, 0.7 * wall)
    front_t = wall
    floor_t = wall

    def _drawer_tray() -> cq.Workplane:
        # local: front face outer at y=0, tray extends +Y; bottom at z=0.
        outer = cq.Workplane("XY").box(draw_w, draw_d, draw_h, centered=(True, False, False))
        cavity_w = draw_w - 2.0 * draw_wall
        cavity_d = draw_d - front_t - draw_wall
        cavity_h = draw_h - floor_t + 0.005
        cavity = (
            cq.Workplane("XY").workplane(offset=floor_t)
            .box(cavity_w, cavity_d, cavity_h, centered=(True, False, False))
            .translate((0.0, front_t, 0.0))
        )
        return outer.cut(cavity)

    drawer = model.part("drawer")
    drawer.visual(mesh_from_cadquery(_drawer_tray(), "tray"), material=closure_mat, name="tray", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))
    # Finger-pull grip bar near the top of the front face (named visual).
    drawer.visual(
        Box((min(0.050, draw_w * 0.4), 0.004, 0.010)),
        origin=Origin(xyz=(0.0, -0.002, draw_h - 0.020)),
        material=accent_mat,
        name="pull_grip", material_class_id=("metal.brass_polished" if r.palette_style in {"white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "black_rigid_gift", "red_gift", "forest_gift", "printed_kraft"} else "metal.blackened_gunmetal"),
    )
    drawer.inertial = Inertial.from_geometry(
        Box((draw_w, draw_d, draw_h)),
        mass=0.15,
        origin=Origin(xyz=(0.0, draw_d / 2.0, draw_h / 2.0)),
    )
    joint_z = wall + clear
    model.articulation(
        "body_to_drawer",
        ArticulationType.PRISMATIC,
        parent=body,
        child=drawer,
        origin=Origin(xyz=(0.0, -r.hy, joint_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.drawer_travel, effort=8.0, velocity=0.5),
    )


def _build_swing_double_door(model, body, r: ResolvedContainerBoxConfig,
                             *, closure_mat, accent_mat) -> None:
    """Two REVOLUTE +/-Z front doors with integrated pull handles
    (swing_double_door record ``door_{i}_hinge`` for-loop)."""
    hgt_z, wall = r.hgt_z, r.wall
    in_hx = r.hx - wall
    seam = 0.002
    door_t = wall
    door_w = in_hx - seam
    door_h = hgt_z - 2.0 * wall
    open_angle = math.radians(90.0)

    def _door_panel(side: int) -> cq.Workplane:
        # local origin at hinge edge, outer face at y=0, z centered.
        panel = cq.Workplane("XY").box(door_w, door_t, door_h, centered=(False, False, True))
        handle_r = min(0.005, door_t)
        handle_len = 0.012
        handle_x = door_w - 0.025
        handle = (
            cq.Workplane("XZ").workplane(offset=0.002).center(handle_x, 0.0)
            .circle(handle_r).extrude(-(handle_len + 0.002))
        )
        panel = panel.union(handle)
        if side > 0:
            panel = panel.mirror("YZ")
        return panel

    sides = [-1, 1]
    for i in range(2):
        side = sides[i]
        door = model.part(f"door_{i}")
        door.visual(mesh_from_cadquery(_door_panel(side), "panel"), material=closure_mat, name="panel", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))
        # Printed label on the outer face (named visual).
        label_x = (door_w / 2.0) if side < 0 else -(door_w / 2.0)
        door.visual(
            Box((min(0.055, door_w * 0.5), 0.001, min(0.032, door_h * 0.3))),
            origin=Origin(xyz=(label_x, -0.0005, 0.0)),
            material=accent_mat,
            name="label", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        door.inertial = Inertial.from_geometry(
            Box((door_w, door_t, door_h)),
            mass=0.04,
            origin=Origin(xyz=(side * (door_w / 2.0), door_t / 2.0, 0.0)),
        )
        hinge_x = -in_hx if side < 0 else in_hx
        axis = (0.0, 0.0, -1.0) if side < 0 else (0.0, 0.0, 1.0)
        model.articulation(
            f"door_{i}_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=door,
            origin=Origin(xyz=(hinge_x, -r.hy, hgt_z / 2.0)),
            axis=axis,
            motion_limits=MotionLimits(lower=0.0, upper=open_angle, effort=3.0, velocity=2.0),
        )


def _build_front_drop_door(model, body, r: ResolvedContainerBoxConfig,
                           *, closure_mat, accent_mat) -> None:
    """One REVOLUTE +X front panel hinged at the bottom-front rim, folds down
    (roll_top_tambour record front_drop_door form ``door_hinge``)."""
    len_x, hgt_z, wall = r.len_x, r.hgt_z, r.wall
    door_clear = 0.001
    door_w = len_x - 2.0 * wall - 2.0 * door_clear
    door_h = hgt_z - 2.0 * wall
    door_t = wall

    def _door_panel() -> cq.Workplane:
        # local: hinge edge at origin along X, panel extends +Z and +Y(thickness).
        return cq.Workplane("XY").box(door_w, door_t, door_h, centered=(True, True, False))

    door = model.part("front_door")
    door.visual(mesh_from_cadquery(_door_panel(), "panel"), material=closure_mat, name="panel", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))
    # Printed label on the door outer face (local outer face at y=-door_t/2).
    door.visual(
        Box((min(0.16, door_w * 0.7), 0.001, min(0.085, door_h * 0.5))),
        origin=Origin(xyz=(0.0, -door_t / 2.0, door_h * 0.5)),
        material=accent_mat,
        name="front_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    door.inertial = Inertial.from_geometry(
        Box((door_w, door_t, door_h)),
        mass=0.04,
        origin=Origin(xyz=(0.0, door_t / 2.0, door_h / 2.0)),
    )
    model.articulation(
        "door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(0.0, -r.hy, wall)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=math.radians(85.0), effort=3.0, velocity=2.0),
    )


# ---------------------------------------------------------------------------
# Slot B: interior_structure builders.
# ---------------------------------------------------------------------------
def _interior_top_clear(r: ResolvedContainerBoxConfig) -> float:
    """The z below which interior fixed visuals / moving children must stay so
    they don't poke through a closed top (for closed-top closures)."""
    flags = _shell_flags(r)
    if flags["open_top"]:
        return r.hgt_z  # open top: interior may reach the rim
    return r.hgt_z - r.wall  # closed top: stay under the top wall


def _build_liftout_tray(model, body, r: ResolvedContainerBoxConfig,
                        *, interior_mat, accent_mat) -> None:
    """Shallow PRISMATIC +Z tray seated on an inner ledge (liftout_tray record
    ``_inner_ledge_solid`` + ``_tray_*_solid`` + ``base_to_tray``)."""
    wall = r.wall
    cav_w = r.inner_w
    cav_d = r.inner_d
    top_clear = _interior_top_clear(r)

    ledge_w = 0.006
    ledge_t = 0.004
    # Seat the ledge low enough that the tray (rim + lift) stays under top_clear.
    tray_floor_t = 0.003
    tray_wall_h = 0.006
    tray_rim_t = 0.002
    tray_stack = tray_floor_t + tray_wall_h + tray_rim_t
    ledge_z = _clamp(0.45 * r.inner_h, wall + 0.004,
                     top_clear - wall - tray_stack - r.tray_lift)
    if ledge_z < wall + 0.004:
        ledge_z = wall + 0.004
    seat_z = ledge_z + ledge_t

    # Inner ledge shelf (fixed visual on box_shell).
    ledge = None
    for sign in (+1, -1):
        strip = (
            cq.Workplane("XY").workplane(offset=ledge_z)
            .center(0.0, sign * (cav_d / 2.0 - ledge_w / 2.0))
            .box(cav_w, ledge_w, ledge_t, centered=(True, True, False))
        )
        ledge = strip if ledge is None else ledge.union(strip)
    mid_d = cav_d - 2.0 * ledge_w
    for sign in (+1, -1):
        strip = (
            cq.Workplane("XY").workplane(offset=ledge_z)
            .center(sign * (cav_w / 2.0 - ledge_w / 2.0), 0.0)
            .box(ledge_w, mid_d, ledge_t, centered=(True, True, False))
        )
        ledge = ledge.union(strip)
    body.visual(mesh_from_cadquery(ledge, "inner_ledge"), material=interior_mat, name="inner_ledge", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))

    # Tray geometry (floor + walls + rim), authored with floor bottom at z=0.
    tray_clear = 0.002
    ledge_open_w = cav_w - 2.0 * ledge_w
    ledge_open_d = cav_d - 2.0 * ledge_w
    tray_ow = ledge_open_w - 2.0 * tray_clear
    tray_od = ledge_open_d - 2.0 * tray_clear
    tray_wall_t = 0.005
    rim_ow = cav_w - 2.0 * 0.001
    rim_od = cav_d - 2.0 * 0.001

    def _tray_solid() -> cq.Workplane:
        floor = cq.Workplane("XY").box(tray_ow, tray_od, tray_floor_t, centered=(True, True, False))
        walls = None
        for sign in (+1, -1):
            w = (
                cq.Workplane("XY").workplane(offset=tray_floor_t)
                .center(0.0, sign * (tray_od / 2.0 - tray_wall_t / 2.0))
                .box(tray_ow, tray_wall_t, tray_wall_h, centered=(True, True, False))
            )
            walls = w if walls is None else walls.union(w)
        mid = tray_od - 2.0 * tray_wall_t
        for sign in (+1, -1):
            w = (
                cq.Workplane("XY").workplane(offset=tray_floor_t)
                .center(sign * (tray_ow / 2.0 - tray_wall_t / 2.0), 0.0)
                .box(tray_wall_t, mid, tray_wall_h, centered=(True, True, False))
            )
            walls = walls.union(w)
        rim_z = tray_floor_t + tray_wall_h
        rim_outer = (
            cq.Workplane("XY").workplane(offset=rim_z)
            .box(rim_ow, rim_od, tray_rim_t, centered=(True, True, False))
        )
        rim_inner = (
            cq.Workplane("XY").workplane(offset=rim_z)
            .box(tray_ow - 2.0 * tray_wall_t, tray_od - 2.0 * tray_wall_t,
                 tray_rim_t + 0.001, centered=(True, True, False))
        )
        rim = rim_outer.cut(rim_inner)
        return floor.union(walls).union(rim)

    # Anchor the +Z joint origin on the front ledge strip top (real geometry on
    # the body side) rather than the empty cavity center; shift the tray mesh by
    # -anchor_y so it re-centers in the cavity. The tray is also dropped by -rim_z
    # so the rim flange bottom rests ON the ledge top (z=seat_z) and the body
    # hangs into the cavity — keeps the tray supported (not floating).
    anchor_y = -(cav_d / 2.0 - ledge_w / 2.0)
    rim_z = tray_floor_t + tray_wall_h

    tray = model.part("tray")
    tray.visual(
        mesh_from_cadquery(_tray_solid().translate((0.0, -anchor_y, -rim_z)), "tray_body"),
        material=accent_mat,
        name="tray_body", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"),
    )
    tray.inertial = Inertial.from_geometry(
        Box((tray_ow, tray_od, tray_stack)),
        mass=0.10,
        origin=Origin(xyz=(0.0, -anchor_y, -rim_z + tray_stack / 2.0)),
    )
    model.articulation(
        "base_to_tray",
        ArticulationType.PRISMATIC,
        parent=body,
        child=tray,
        origin=Origin(xyz=(0.0, anchor_y, seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.tray_lift, effort=3.0, velocity=0.5),
    )


def _build_stacking_lip(body, r: ResolvedContainerBoxConfig, *, interior_mat) -> None:
    """Raised inner rim lip (fixed visual, no joint) — stacking_lip record
    ``_inner_lip``. Footing groove is omitted (floor solid) to keep the shell
    boolean light; the lip is the defining stacking feature."""
    wall = r.wall
    cavity_w = r.inner_w
    cavity_d = r.inner_d
    lip_w = 0.004
    lip_h = 0.005
    top_clear = _interior_top_clear(r)
    # Place the lip so it sits just below/at the rim; for closed-top, keep it
    # under the ceiling.
    lip_base = min(r.hgt_z - 0.001, top_clear - lip_h - 0.001)
    if lip_base < wall:
        lip_base = wall
    lip_inner_w = cavity_w - 2.0 * lip_w
    lip_inner_d = cavity_d - 2.0 * lip_w

    def _rect_ring(ow: float, od: float, iw: float, id_: float, h: float, z0: float) -> cq.Workplane:
        outer = (
            cq.Workplane("XY").workplane(offset=z0)
            .box(ow, od, h, centered=(True, True, False))
        )
        inner = (
            cq.Workplane("XY").workplane(offset=z0 - 0.0005)
            .box(iw, id_, h + 0.001, centered=(True, True, False))
        )
        return outer.cut(inner)

    lip = _rect_ring(
        cavity_w + 0.001, cavity_d + 0.001, lip_inner_w, lip_inner_d,
        lip_h + 0.001, lip_base,
    )
    body.visual(mesh_from_cadquery(lip, "inner_lip"), material=interior_mat, name="inner_lip", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"))


def _build_dividers(model, body, r: ResolvedContainerBoxConfig, *, interior_mat) -> None:
    """N PRISMATIC +Z lift-out compartment dividers (n2/n4 records
    ``_divider_solid`` + ``for i in range(N)`` + ``base_to_divider_i``)."""
    wall = r.wall
    iw = r.inner_w
    id_ = r.inner_d
    n = r.divider_count
    div_t = 0.004
    div_d = id_ - 0.004
    top_clear = _interior_top_clear(r)
    # Panel height: stay under the top clearance, and leave room to lift out.
    div_h = _clamp(r.inner_h - 0.004, 0.01, top_clear - wall - 0.002)
    compartment_w = iw / (n + 1)
    divider_xs = [-iw / 2.0 + (i + 1) * compartment_w for i in range(n)]

    def _divider_solid() -> cq.Workplane:
        return cq.Workplane("XY").box(div_t, div_d, div_h, centered=(True, True, False))

    for i in range(n):
        divider = model.part(f"divider_{i}")
        divider.visual(
            mesh_from_cadquery(_divider_solid(), f"divider_panel_{i}"),
            material=interior_mat,
            name=f"divider_panel_{i}", material_class_id=("paper.cardboard" if r.palette_style in {"kraft_corrugated", "white_gift", "white_gift_gloss", "walnut_keepsake", "natural_crate", "gray_shipping", "black_rigid_gift", "printed_kraft"} else "fabric.satin_silk"),
        )
        divider.inertial = Inertial.from_geometry(
            Box((div_t, div_d, div_h)),
            mass=0.05,
            origin=Origin(xyz=(0.0, 0.0, div_h / 2.0)),
        )
        model.articulation(
            f"base_to_divider_{i}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=divider,
            origin=Origin(xyz=(divider_xs[i], 0.0, wall)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(lower=0.0, upper=r.div_lift, effort=2.0, velocity=0.5),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _rot_z(xyz, deg: float):
    a = math.radians(deg)
    x, y, z = xyz
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a), z)


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_box(
    config: ContainerBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cb_body_{r.palette_style}", rgba=pal["body"])
    closure_mat = model.material(f"cb_closure_{r.palette_style}", rgba=pal["closure"])
    interior_mat = model.material(f"cb_interior_{r.palette_style}", rgba=pal["interior"])
    accent_mat = model.material(f"cb_accent_{r.palette_style}", rgba=pal["accent"])

    flags = _shell_flags(r)

    # --- ROOT: box_shell (wall_surface) --------------------------------------
    body = model.part("box_shell")
    _emit_box_shell(body, r, flags, body_mat=body_mat, accent_mat=accent_mat)
    body.inertial = Inertial.from_geometry(
        Box((r.len_x, r.dep_y, r.hgt_z)),
        mass=0.45,
        origin=Origin(xyz=(0.0, 0.0, r.hgt_z / 2.0)),
    )

    # --- closure_mechanism ---------------------------------------------------
    closure = r.closure_mechanism
    if closure == "four_top_flaps":
        _build_four_top_flaps(model, body, r, closure_mat=closure_mat)
    elif closure == "liftoff_telescoping_lid":
        _build_liftoff_lid(model, body, r, closure_mat=closure_mat)
    elif closure == "rear_hinged_flat_lid":
        _build_rear_hinged_lid(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)
    elif closure == "sliding_drawer":
        _build_sliding_drawer(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)
    elif closure == "swing_double_door":
        _build_swing_double_door(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)
    elif closure == "front_drop_door":
        _build_front_drop_door(model, body, r, closure_mat=closure_mat, accent_mat=accent_mat)

    # --- interior_structure --------------------------------------------------
    interior = r.interior_structure
    if interior == "liftout_tray":
        _build_liftout_tray(model, body, r, interior_mat=interior_mat, accent_mat=accent_mat)
    elif interior == "stacking_lip":
        _build_stacking_lip(body, r, interior_mat=interior_mat)
    elif interior == "compartment_dividers_N":
        _build_dividers(model, body, r, interior_mat=interior_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["palette_style"] = r.palette_style
    model.meta["finish"] = pal["finish"]
    return model


def build_seeded_container_box(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_box(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid skirt over walls, drawer-in-cavity,
# divider-in-floor, tray-on-ledge, flap corners, knuckle interleave) are
# declared element-scoped; the closure + interior actions are exercised.
# ---------------------------------------------------------------------------
def run_container_box_tests(
    object_model: ArticulatedObject,
    config: ContainerBoxConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("box_shell")

    # ---- box shell rests on the ground (base near z=0), real volume ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "box shell rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"shell min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "box shell has real footprint and height",
        bext[0] > 0.05 and bext[1] > 0.05 and bext[2] > 0.05,
        details=f"shell extents={bext}",
    )

    # =====================================================================
    # Closure mechanism: action + captured-fit overlaps.
    # =====================================================================
    closure = r.closure_mechanism

    if closure == "four_top_flaps":
        flaps = {n: object_model.get_part(n) for n in ("flap_n", "flap_s", "flap_e", "flap_w")}
        joints = {n: object_model.get_articulation(f"box_to_{n}") for n in flaps}
        # Adjacent flap corners and flap-on-rim contacts overlap when closed.
        for a in ("flap_n", "flap_s"):
            for b in ("flap_e", "flap_w"):
                ctx.allow_overlap(
                    flaps[a], flaps[b],
                    reason="Closed top flaps lie in adjacent thin layers and abut near the box center.",
                )
        # Each flap's hinge edge sits on the box top rim and may touch the wall
        # or the interior lip / ledge near the rim.
        for n in flaps:
            _allow_closure_against_shell(ctx, flaps[n], body, r, elem_a=n)
        for n in flaps:
            ctx.check(
                f"{n} hinge is REVOLUTE",
                joints[n].articulation_type == ArticulationType.REVOLUTE,
                details=f"{n} type={joints[n].articulation_type}",
            )
            rest_top = ctx.part_world_aabb(flaps[n])[1][2]
            with ctx.pose({joints[n]: math.radians(90.0)}):
                open_top = ctx.part_world_aabb(flaps[n])[1][2]
            ctx.check(
                f"{n} free edge swings up when opened",
                open_top > rest_top + 0.03,
                details=f"{n} rest_top={rest_top:.4f}, open_top={open_top:.4f}",
            )

    elif closure == "liftoff_telescoping_lid":
        lid = object_model.get_part("lid")
        lift = object_model.get_articulation("box_to_lid")
        _allow_lid_over_walls(ctx, lid, body, r)
        if r.interior_structure == "stacking_lip":
            # The stacking lip protrudes near the rim into the seated lid cavity.
            ctx.allow_overlap(
                lid, body, elem_a="lid_shell", elem_b="inner_lip",
                reason="The stacking lip sits inside the seated lid cavity; it does "
                "not block lid removal.",
            )
        ctx.check(
            "box_to_lid is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99,
            details=f"axis={lift.axis}, type={lift.articulation_type}",
        )
        rest = ctx.part_world_position(lid)
        with ctx.pose({lift: r.lid_lift}):
            up = ctx.part_world_position(lid)
        ctx.check(
            "lid lifts straight up off the box",
            up[2] > rest[2] + r.lid_lift * 0.5
            and abs(up[0] - rest[0]) < 1e-4 and abs(up[1] - rest[1]) < 1e-4,
            details=f"rest={rest}, up={up}",
        )

    elif closure == "rear_hinged_flat_lid":
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("base_to_lid")
        _allow_closure_against_shell(ctx, lid, body, r, elem_a="lid_slab")
        for i in (0, 1):
            _allow_closure_against_shell(ctx, lid, body, r, elem_a=f"lid_knuckle_{i}")
            ctx.allow_overlap(
                lid, body, elem_a=f"lid_knuckle_{i}", elem_b=f"base_knuckle_{i}",
                reason="Interleaved hinge knuckles share the rear hinge pin line.",
            )
            ctx.allow_overlap(
                lid, body, elem_a="lid_slab", elem_b=f"base_knuckle_{i}",
                reason="Closed lid slab rests over the rear hinge knuckles.",
            )
        ctx.check(
            "base_to_lid is REVOLUTE about -X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: math.radians(100.0)}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "rear lid front edge lifts when opened",
            top1 > top0 + 0.04,
            details=f"closed_top={top0:.4f}, open_top={top1:.4f}",
        )

    elif closure == "sliding_drawer":
        drawer = object_model.get_part("drawer")
        slide = object_model.get_articulation("body_to_drawer")
        _allow_closure_against_shell(ctx, drawer, body, r, elem_a="tray")
        ctx.check(
            "body_to_drawer is PRISMATIC about -Y",
            slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[1]) > 0.99,
            details=f"axis={slide.axis}, type={slide.articulation_type}",
        )
        rest = ctx.part_world_position(drawer)
        with ctx.pose({slide: r.drawer_travel}):
            ext = ctx.part_world_position(drawer)
        ctx.check(
            "drawer pulls out toward -Y",
            ext[1] < rest[1] - min(0.05, r.drawer_travel * 0.5),
            details=f"rest_y={rest[1]:.4f}, ext_y={ext[1]:.4f}",
        )

    elif closure == "swing_double_door":
        d0 = object_model.get_part("door_0")
        d1 = object_model.get_part("door_1")
        for d, name in ((d0, "door_0"), (d1, "door_1")):
            _allow_closure_against_shell(ctx, d, body, r, elem_a="panel")
            hinge = object_model.get_articulation(f"{name}_hinge")
            ctx.check(
                f"{name}_hinge is REVOLUTE about +/-Z",
                hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[2]) > 0.99,
                details=f"axis={hinge.axis}, type={hinge.articulation_type}",
            )
            rest_min_y = ctx.part_world_aabb(d)[0][1]
            with ctx.pose({hinge: math.radians(90.0)}):
                open_min_y = ctx.part_world_aabb(d)[0][1]
            ctx.check(
                f"{name} swings outward when opened",
                open_min_y < rest_min_y - 0.03,
                details=f"{name} rest_min_y={rest_min_y:.4f}, open_min_y={open_min_y:.4f}",
            )

    elif closure == "front_drop_door":
        door = object_model.get_part("front_door")
        hinge = object_model.get_articulation("door_hinge")
        _allow_closure_against_shell(ctx, door, body, r, elem_a="panel")
        ctx.check(
            "door_hinge is REVOLUTE about +X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        rest_top = ctx.part_world_aabb(door)[1][2]
        with ctx.pose({hinge: math.radians(85.0)}):
            open_top = ctx.part_world_aabb(door)[1][2]
        ctx.check(
            "drop door top drops when opened",
            open_top < rest_top - 0.05,
            details=f"rest_top={rest_top:.4f}, open_top={open_top:.4f}",
        )

    # =====================================================================
    # Interior structure: fixed visual / moving child + captured-fit overlaps.
    # =====================================================================
    interior = r.interior_structure

    if interior == "liftout_tray":
        tray = object_model.get_part("tray")
        lift = object_model.get_articulation("base_to_tray")
        for elem_b in _cavity_wall_elems(r):
            ctx.allow_overlap(
                tray, body, elem_a="tray_body", elem_b=elem_b,
                reason="The lift-out tray rim seats inside the cavity and may touch "
                "the inward wall / post geometry.",
            )
        ctx.allow_overlap(
            tray, body, elem_a="tray_body", elem_b="inner_ledge",
            reason="The tray rim rests directly on the inner ledge shelf.",
        )
        ctx.check(
            "base_to_tray is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99,
            details=f"axis={lift.axis}, type={lift.articulation_type}",
        )
        rest = ctx.part_world_position(tray)
        with ctx.pose({lift: r.tray_lift}):
            up = ctx.part_world_position(tray)
        ctx.check(
            "tray lifts straight up out of the cavity",
            up[2] > rest[2] + r.tray_lift * 0.5
            and abs(up[0] - rest[0]) < 0.002 and abs(up[1] - rest[1]) < 0.002,
            details=f"rest={rest}, up={up}",
        )

    elif interior == "stacking_lip":
        ctx.check(
            "inner lip visual exists on the box shell",
            body.get_visual("inner_lip") is not None,
            details="inner_lip visual not found",
        )

    elif interior == "compartment_dividers_N":
        n = r.divider_count
        cavity_elems = _cavity_wall_elems(r)
        for i in range(n):
            divider = object_model.get_part(f"divider_{i}")
            joint = object_model.get_articulation(f"base_to_divider_{i}")
            for elem_b in cavity_elems:
                ctx.allow_overlap(
                    divider, body, elem_a=f"divider_panel_{i}", elem_b=elem_b,
                    reason=f"Divider {i} drops into the cavity and rests on the floor / wall.",
                )
            ctx.check(
                f"base_to_divider_{i} is PRISMATIC about +Z",
                joint.articulation_type == ArticulationType.PRISMATIC and abs(joint.axis[2]) > 0.99,
                details=f"axis={joint.axis}, type={joint.articulation_type}",
            )
        # Verify lift on the first divider (representative).
        d0 = object_model.get_part("divider_0")
        j0 = object_model.get_articulation("base_to_divider_0")
        rest = ctx.part_world_position(d0)
        with ctx.pose({j0: r.div_lift}):
            up = ctx.part_world_position(d0)
        ctx.check(
            "divider_0 lifts out when joint is positive",
            up[2] > rest[2] + r.div_lift * 0.5,
            details=f"rest_z={rest[2]:.4f}, up_z={up[2]:.4f}",
        )

    # =====================================================================
    # Wall surface: slatted gaps / perforated grid sanity.
    # =====================================================================
    if r.wall_surface == "slatted":
        ctx.check(
            "slatted corner posts visual exists",
            body.get_visual("corner_posts") is not None,
            details="corner_posts visual not found",
        )

    # ---- at least one non-fixed joint exists (category identity) ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed closure joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


def _cavity_wall_elems(r: ResolvedContainerBoxConfig) -> list[str]:
    """Body-side visual element names that bound the cavity, for element-scoped
    overlap allowances of interior / closure parts that sit inside / on it.

    For solid / perforated shells the single ``box_shell`` mesh is the cavity
    wall; for slatted shells the inward-protruding corner posts and slats are.
    """
    if r.wall_surface != "slatted":
        return ["box_shell"]
    elems = ["corner_posts", "floor_panel"]
    n_slats = _slat_count(r)
    flags = _shell_flags(r)
    walls = ["back", "left", "right"]
    if not (flags["front_open"] or flags["front_opening"]):
        walls.append("front")
    for w in walls:
        for i in range(n_slats):
            elems.append(f"{w}_slat_{i}")
    return elems


def _interior_fixed_elems(r: ResolvedContainerBoxConfig) -> list[str]:
    """Body-side interior fixed visuals (inner_lip / inner_ledge) that a closure
    piece may legitimately rest over / touch when closed."""
    if r.interior_structure == "stacking_lip":
        return ["inner_lip"]
    if r.interior_structure == "liftout_tray":
        return ["inner_ledge"]
    return []


def _allow_closure_against_shell(ctx: TestContext, child, body,
                                 r: ResolvedContainerBoxConfig, *, elem_a: str) -> None:
    """Allow a closure piece (``elem_a`` on ``child``) to overlap the cavity wall
    elements and the interior fixed visuals it seats against when closed."""
    for elem_b in _cavity_wall_elems(r) + _interior_fixed_elems(r):
        ctx.allow_overlap(
            child, body, elem_a=elem_a, elem_b=elem_b,
            reason="Closed closure piece seats on the box rim / wall / interior "
            "feature (captured fit).",
        )


def _allow_lid_over_walls(ctx: TestContext, lid, body, r: ResolvedContainerBoxConfig) -> None:
    """Liftoff lid skirt telescopes over the box top outer walls; the element
    name on the body side differs by wall_surface."""
    if r.wall_surface == "slatted":
        # The skirt drops over the corner posts and the topmost slats.
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="corner_posts",
            reason="The lift-off lid skirt telescopes over the box top outer posts.",
        )
        n_slats = _slat_count(r)
        flags = _shell_flags(r)
        walls = ["back", "left", "right"]
        if not (flags["front_open"] or flags["front_opening"]):
            walls.append("front")
        top_idx = n_slats - 1
        for w in walls:
            ctx.allow_overlap(
                lid, body, elem_a="lid_shell", elem_b=f"{w}_slat_{top_idx}",
                reason="The lift-off lid skirt telescopes over the box top outer slats.",
            )
    else:
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="box_shell",
            reason="The lift-off lid skirt is intended to telescope over the box top outer walls.",
        )
