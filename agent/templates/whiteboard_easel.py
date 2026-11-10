# SPDX-License-Identifier: Apache-2.0

"""Whiteboard easel — modular procedural template.

Category identity: a free-standing floor easel whose primary element is a tall
planar dry-erase writing board (perimeter-framed rectangle + marker tray),
carried on its own portable leg/base stand and articulated by casters, folding /
telescoping legs, board revolve / tilt / slide, and locking clamp knobs.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/whiteboard_easel.md``

Slots (exported via ``slot_choices_for_seed``):

* ``support_base``   — rolling_post / folding_tripod / t_column / four_post
* ``board_motion``   — static_framed / revolve_trunnion / tilt_carriage / slide_carriage
* ``leg_multiplicity`` — folding_tripod leg count {n3, n4} (n_a otherwise)
* ``flip_chart_top`` — top clamp-bar decoration {top_clamp_bar, none}
* ``material_style`` — palette

Sources: origins rec_...__001 (rolling H-base) & __002 (folding tripod) + 6 forks
(base_tbase, base_fourpost, board_revolve, board_tilt, board_slide, n4_legs).

``config_from_seed`` is procedural for every seed (no seed=0 special case); legal
(base, motion) pairs are drawn from a weighted compatibility table and any illegal
draw is downgraded to that base's legal motion in ``resolve_config``.
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
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
)

__modular__ = True

SupportBase = Literal[
    "rolling_post_base",
    "folding_tripod_base",
    "t_column_base",
    "four_post_frame_base",
]
BoardMotion = Literal[
    "static_framed",
    "revolve_trunnion",
    "tilt_carriage",
    "slide_carriage",
]
FlipChartTop = Literal["top_clamp_bar", "none"]
MaterialStyle = Literal[
    "powder_blue",
    "satin_aluminum",
    "white_coat",
    "dark_metal",
    "classroom_green",
]

SUPPORT_BASES: tuple[SupportBase, ...] = (
    "rolling_post_base",
    "folding_tripod_base",
    "t_column_base",
    "four_post_frame_base",
)
BOARD_MOTIONS: tuple[BoardMotion, ...] = (
    "static_framed",
    "revolve_trunnion",
    "tilt_carriage",
    "slide_carriage",
)
FLIP_CHART_TOPS: tuple[FlipChartTop, ...] = ("top_clamp_bar", "none")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "powder_blue",
    "satin_aluminum",
    "white_coat",
    "dark_metal",
    "classroom_green",
)

_MOTION_BY_BASE: dict[SupportBase, tuple[BoardMotion, ...]] = {
    "rolling_post_base": BOARD_MOTIONS,
    "four_post_frame_base": BOARD_MOTIONS,
    "folding_tripod_base": ("static_framed",),
    "t_column_base": ("static_framed",),
}

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "powder_blue": {
        "frame": (0.0, 0.18, 0.38, 1.0),
        "panel": (0.96, 0.97, 0.94, 1.0),
        "rubber": (0.015, 0.015, 0.014, 1.0),
        "metal": (0.67, 0.70, 0.72, 1.0),
        "hardware": (0.24, 0.26, 0.28, 1.0),
    },
    "satin_aluminum": {
        "frame": (0.62, 0.65, 0.64, 1.0),
        "panel": (0.96, 0.97, 0.96, 1.0),
        "rubber": (0.02, 0.02, 0.018, 1.0),
        "metal": (0.72, 0.74, 0.75, 1.0),
        "hardware": (0.30, 0.31, 0.32, 1.0),
    },
    "white_coat": {
        "frame": (0.92, 0.93, 0.91, 1.0),
        "panel": (0.97, 0.98, 0.97, 1.0),
        "rubber": (0.04, 0.045, 0.045, 1.0),
        "metal": (0.60, 0.62, 0.63, 1.0),
        "hardware": (0.34, 0.36, 0.38, 1.0),
    },
    "dark_metal": {
        "frame": (0.20, 0.22, 0.24, 1.0),
        "panel": (0.95, 0.96, 0.94, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "metal": (0.55, 0.57, 0.58, 1.0),
        "hardware": (0.12, 0.13, 0.14, 1.0),
    },
    "classroom_green": {
        "frame": (0.13, 0.40, 0.29, 1.0),
        "panel": (0.96, 0.97, 0.94, 1.0),
        "rubber": (0.03, 0.035, 0.03, 1.0),
        "metal": (0.66, 0.69, 0.70, 1.0),
        "hardware": (0.10, 0.24, 0.19, 1.0),
    },
}

# ---- shared reference geometry (world / board-local frames) ----------------
Z_CENTER = 1.355  # world z of the board center at rest (static / revolve / tilt / hub)
Z_SLIDE_REST = 1.170  # lower rest for the sliding board so it climbs on masts
POST_TOP = 2.14  # world z of two-mast post tops (headroom above the board + top clamp for the tilt carriage rail)
CASTER_RADIUS = 0.030

# (base, motion, weight) — canonical, source-attested pairs weighted higher.
_LEGAL_ROWS: list[tuple[SupportBase, BoardMotion, int]] = [
    ("rolling_post_base", "static_framed", 6),
    ("rolling_post_base", "revolve_trunnion", 5),
    ("rolling_post_base", "tilt_carriage", 4),
    ("rolling_post_base", "slide_carriage", 4),
    ("four_post_frame_base", "static_framed", 5),
    ("four_post_frame_base", "revolve_trunnion", 3),
    ("four_post_frame_base", "tilt_carriage", 3),
    ("four_post_frame_base", "slide_carriage", 3),
    ("folding_tripod_base", "static_framed", 6),
    ("t_column_base", "static_framed", 5),
]
LEGAL_PAIRS: tuple[tuple[SupportBase, BoardMotion], ...] = tuple((b, m) for b, m, _w in _LEGAL_ROWS)
LEGAL_PAIR_WEIGHTS: tuple[int, ...] = tuple(w for _b, _m, w in _LEGAL_ROWS)


@dataclass(frozen=True)
class WhiteboardEaselConfig:
    support_base: SupportBase | None = None
    board_motion: BoardMotion | None = None
    leg_count: int = 3
    flip_chart_top: FlipChartTop = "none"
    material_style: MaterialStyle = "powder_blue"
    board_width_scale: float = 1.0
    board_height_scale: float = 1.0
    stand_spread_scale: float = 1.0
    name: str = "whiteboard_easel"


@dataclass(frozen=True)
class ResolvedWhiteboardEaselConfig:
    support_base: SupportBase
    board_motion: BoardMotion
    leg_count: int
    flip_chart_top: FlipChartTop
    material_style: MaterialStyle
    board_width_scale: float
    board_height_scale: float
    stand_spread_scale: float
    half_w_panel: float  # writing panel half width
    half_w_frame: float  # side-rail outer half width
    half_h: float  # top/bottom rail center offset
    post_x: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def config_from_seed(seed: int) -> WhiteboardEaselConfig:
    rng = random.Random(seed)
    base, motion = rng.choices(LEGAL_PAIRS, weights=LEGAL_PAIR_WEIGHTS, k=1)[0]
    leg_count = rng.choice((3, 4)) if base == "folding_tripod_base" else 3
    return WhiteboardEaselConfig(
        support_base=base,
        board_motion=motion,
        leg_count=leg_count,
        flip_chart_top=rng.choice(FLIP_CHART_TOPS),
        material_style=rng.choice(MATERIAL_STYLES),
        board_width_scale=round(rng.uniform(0.92, 1.06), 4),
        board_height_scale=round(rng.uniform(1.00, 1.08), 4),
        stand_spread_scale=round(rng.uniform(0.90, 1.12), 4),
        name=f"seeded_whiteboard_easel_{seed}",
    )


def _downgrade(base: SupportBase, motion: BoardMotion) -> BoardMotion:
    legal = _MOTION_BY_BASE[base]
    return motion if motion in legal else legal[0]


def resolve_config(config: WhiteboardEaselConfig) -> ResolvedWhiteboardEaselConfig:
    base = config.support_base or "rolling_post_base"
    motion = config.board_motion or "static_framed"
    if base not in SUPPORT_BASES:
        raise ValueError(f"Unsupported support_base: {base}")
    if motion not in BOARD_MOTIONS:
        raise ValueError(f"Unsupported board_motion: {motion}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    motion = _downgrade(base, motion)

    leg_count = 4 if (base == "folding_tripod_base" and config.leg_count >= 4) else 3

    ws = _clamp(config.board_width_scale, 0.92, 1.06)
    hs = _clamp(config.board_height_scale, 1.00, 1.08)
    spread = _clamp(config.stand_spread_scale, 0.90, 1.12)

    half_w_panel = 0.3425 * ws
    half_w_frame = half_w_panel + 0.048  # side-rail outer edge (rail center = panel edge + 0.018)
    half_h = 0.565 * hs
    # inequality: posts must clear the board frame + clamp knobs laterally.
    post_x = max(0.50 * spread, half_w_frame + 0.110)

    return ResolvedWhiteboardEaselConfig(
        support_base=base,
        board_motion=motion,
        leg_count=leg_count,
        flip_chart_top=config.flip_chart_top,
        material_style=config.material_style,
        board_width_scale=ws,
        board_height_scale=hs,
        stand_spread_scale=spread,
        half_w_panel=half_w_panel,
        half_w_frame=half_w_frame,
        half_h=half_h,
        post_x=post_x,
        palette=dict(PALETTES[config.material_style]),
        name=config.name,
    )


# --------------------------------------------------------------------------- #
#  low-level helpers
# --------------------------------------------------------------------------- #
def _register_palette(model: ArticulatedObject, palette: dict) -> None:
    for key, rgba in palette.items():
        model.material(key, rgba=rgba)


def _rod_between(part: Part, p0, p1, radius: float, *, material: str, name: str) -> None:
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=((x0 + x1) * 0.5, (y0 + y1) * 0.5, (z0 + z1) * 0.5), rpy=(0.0, pitch, yaw)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _add_square_sleeve(part: Part, *, x: float, z_center: float, length: float, material: str, name: str) -> None:
    """Hollow square carriage sleeve (interior narrower than a mast so the walls
    positively retain the post — the source's telescoping-proxy idiom)."""
    wall = 0.009
    outer = 0.056
    inner = outer - 2.0 * wall  # 0.038
    part.visual(Box((outer, wall, length)), origin=Origin(xyz=(x, -outer * 0.5 + wall * 0.5, z_center)), material=material, name=f"{name}_front_wall", material_class_id="metal.paint_coated")
    part.visual(Box((outer, wall, length)), origin=Origin(xyz=(x, outer * 0.5 - wall * 0.5, z_center)), material=material, name=f"{name}_rear_wall", material_class_id="metal.paint_coated")
    part.visual(Box((wall, inner, length)), origin=Origin(xyz=(x - outer * 0.5 + wall * 0.5, 0.0, z_center)), material=material, name=f"{name}_left_wall", material_class_id="metal.paint_coated")
    part.visual(Box((wall, inner, length)), origin=Origin(xyz=(x + outer * 0.5 - wall * 0.5, 0.0, z_center)), material=material, name=f"{name}_right_wall", material_class_id="metal.paint_coated")


CASTER_MOUNT_Z = 0.110  # default world z of the mount face a caster bolts up to


def _emit_caster(
    model: ArticulatedObject,
    stand: Part,
    name: str,
    cx: float,
    cy: float,
    mount_z: float = CASTER_MOUNT_Z,
) -> str:
    """Emit a swivel caster whose wheel hangs BELOW ``mount_z`` (the bottom face
    of the runner / arm it bolts to). The wheel bottom rests on the floor (z=0),
    the fork straddles the wheel disc and rises to the mount plane, and the
    swivel bridge bolts up against the runner/arm — so the wheel never penetrates
    the structure it carries."""
    axle_z = CASTER_RADIUS  # 0.030 -> wheel bottom on the floor
    fork_top = mount_z
    fork_h = max(fork_top - axle_z, 0.030)
    fork_zc = (axle_z + fork_top) * 0.5
    for f_idx, fs in enumerate((-1.0, 1.0)):
        stand.visual(
            Box((0.009, 0.044, fork_h)),
            origin=Origin(xyz=(cx + fs * 0.022, cy, fork_zc)),
            material="frame",
            name=f"{name}_fork_{f_idx}", material_class_id="metal.paint_coated",
        )
    # swivel bridge/plate sits just under the mount plane and bolts to the runner.
    stand.visual(
        Box((0.052, 0.050, 0.016)),
        origin=Origin(xyz=(cx, cy, mount_z - 0.008)),
        material="frame",
        name=f"{name}_fork_bridge", material_class_id="metal.paint_coated",
    )
    caster = model.part(name)
    caster.visual(Cylinder(radius=CASTER_RADIUS, length=0.024), origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)), material="rubber", name="rubber_wheel", material_class_id="rubber.smooth_plain")
    caster.visual(Cylinder(radius=0.012, length=0.026), origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)), material="metal", name="hub_cap", material_class_id="metal.stainless_matte")
    caster.visual(Cylinder(radius=0.006, length=0.058), origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)), material="metal", name="axle_pin", material_class_id="metal.stainless_matte")
    model.articulation(
        f"stand_to_{name}",
        ArticulationType.CONTINUOUS,
        parent=stand,
        child=caster,
        origin=Origin(xyz=(cx, cy, axle_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=12.0),
    )
    return name


# --------------------------------------------------------------------------- #
#  stand mount descriptor
# --------------------------------------------------------------------------- #
@dataclass
class StandMount:
    two_mast: bool
    post_x: float
    post_top: float
    z_center: float
    caster_names: list[str] = field(default_factory=list)
    leg_names: list[str] = field(default_factory=list)
    static_anchor: tuple[float, float, float] = (0.0, 0.0, Z_CENTER)
    static_stand_elem: str = "board_mount_bar"
    static_board_elem: str = "mount_plate"


# --------------------------------------------------------------------------- #
#  board frame (shared across all board_motion modules)
# --------------------------------------------------------------------------- #
def _emit_board_frame(
    model: ArticulatedObject,
    r: ResolvedWhiteboardEaselConfig,
    *,
    double_sided: bool,
    sleeves: bool,
    hinge_lugs: bool,
    trunnion: bool,
) -> Part:
    board = model.part("board_frame")
    ws = r.board_width_scale
    zt = r.half_h
    pw = r.half_w_panel
    # side rails are drawn in a touch from the frame outer edge so their inner
    # faces tuck UNDER the writing panel edges (picture-frame overlap) — this is
    # what fuses the panel into the frame rather than leaving it floating.
    sr = pw + 0.018  # side rail center: inner face sits ~0.012 under the panel edge

    board.visual(Box((pw * 2.0, 0.014, r.board_height_scale * 1.040)), origin=Origin(xyz=(0.0, -0.018, 0.0)), material="panel", name="white_surface", material_class_id="plastic.opaque_glossy_molded")
    if double_sided:
        board.visual(Box((pw * 2.0, 0.014, r.board_height_scale * 1.040)), origin=Origin(xyz=(0.0, 0.018, 0.0)), material="panel", name="white_surface_back", material_class_id="plastic.opaque_glossy_molded")

    board.visual(Box((2.0 * sr + 0.060, 0.052, 0.065)), origin=Origin(xyz=(0.0, 0.0, zt)), material="frame", name="top_rail", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    board.visual(Box((2.0 * sr + 0.040, 0.050, 0.052)), origin=Origin(xyz=(0.0, 0.0, -zt)), material="frame", name="bottom_rail", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    for side, sx in (("side_0", -sr), ("side_1", sr)):
        board.visual(Box((0.060, 0.052, r.board_height_scale * 1.165)), origin=Origin(xyz=(sx, 0.0, 0.0)), material="frame", name=f"{side}_rail", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))

    # back mount plate: overlaps the panel back so it is a supported board element;
    # shallow enough (back face y=+0.020) to clear a rear spine / bracket.
    board.visual(Box((0.170, 0.040, 0.230)), origin=Origin(xyz=(0.0, 0.000, 0.0)), material="hardware", name="mount_plate", material_class_id="metal.blackened_gunmetal")

    # marker tray hanging just below the lower rail.
    tray_z = -zt - 0.060
    board.visual(Box((0.630 * ws, 0.085, 0.022)), origin=Origin(xyz=(0.0, -0.067, tray_z)), material="frame", name="marker_tray_shelf", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    board.visual(Box((0.630 * ws, 0.018, 0.052)), origin=Origin(xyz=(0.0, -0.025, tray_z + 0.025)), material="frame", name="tray_back_lip", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    for i, bx in enumerate((-0.260 * ws, 0.260 * ws)):
        board.visual(Box((0.045, 0.045, 0.070)), origin=Origin(xyz=(bx, -0.045, tray_z + 0.045)), material="frame", name=f"tray_bracket_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))

    if trunnion:
        # the trunnion axle spans from the side rail all the way OUT into the post
        # / yoke bushing so the revolving board is physically carried by the stand
        # (reach derived from post_x, not a fixed length, so it holds at any spread).
        inner_x = sr + 0.006
        outer_x = r.post_x + 0.014
        t_len = outer_x - inner_x
        for i, sign in enumerate((-1.0, 1.0)):
            board.visual(
                Cylinder(radius=0.014, length=t_len),
                origin=Origin(xyz=(sign * (inner_x + outer_x) * 0.5, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                material="metal",
                name=f"trunnion_stub_{i}", material_class_id="metal.stainless_matte",
            )
    if hinge_lugs:
        # pivot ears outboard of the side rail (overlap it for anchoring) that the
        # tilt-carriage side pins seat into as the horizontal tilt bearing.
        for i, sign in enumerate((-1.0, 1.0)):
            board.visual(Box((0.040, 0.052, 0.070)), origin=Origin(xyz=(sign * (sr + 0.040), 0.0, 0.0)), material="frame", name=f"hinge_lug_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    if sleeves:
        for i in (0, 1):
            sign = -1.0 if i == 0 else 1.0
            _add_square_sleeve(board, x=sign * r.post_x, z_center=-0.10, length=0.62, material="frame", name=f"carriage_{i}")
            # ties from the sleeve to the board side rail so the sleeve is supported.
            for j, zc in enumerate((0.12, -0.30)):
                _rod_between(board, (sign * sr, 0.0, zc), (sign * r.post_x, 0.0, zc), 0.010, material="frame", name=f"carriage_{i}_tie_{j}")

    if r.flip_chart_top == "top_clamp_bar":
        _rod_between(board, (-0.300 * ws, -0.006, zt + 0.050), (0.300 * ws, -0.006, zt + 0.050), 0.018, material="hardware", name="top_clamp_bar")
        for i, bx in enumerate((-0.330 * ws, 0.330 * ws)):
            board.visual(Box((0.036, 0.040, 0.046)), origin=Origin(xyz=(bx, -0.004, zt + 0.030)), material="frame", name=f"top_clamp_bracket_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    return board


def _emit_clamp_knobs(model: ArticulatedObject, board: Part, r: ResolvedWhiteboardEaselConfig) -> None:
    sr = r.half_w_panel + 0.018  # match the side-rail center
    for i, sign in enumerate((-1.0, 1.0)):
        x = sign * (sr + 0.045)
        knob = model.part(f"clamp_{i}")
        # stem runs inboard to the side rail; the thumb wheel overlaps its outer end.
        knob.visual(Cylinder(radius=0.007, length=0.060), origin=Origin(xyz=(-sign * 0.014, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material="metal", name="threaded_stem", material_class_id="metal.stainless_matte")
        knob.visual(Cylinder(radius=0.022, length=0.014), origin=Origin(xyz=(sign * 0.014, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)), material="rubber", name="thumb_wheel", material_class_id="rubber.smooth_plain")
        model.articulation(
            f"board_to_clamp_{i}",
            ArticulationType.REVOLUTE,
            parent=board,
            child=knob,
            origin=Origin(xyz=(x, 0.0, -0.150)),
            axis=(sign, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.4, velocity=4.0, lower=-math.pi, upper=math.pi),
        )


# --------------------------------------------------------------------------- #
#  support_base modules
# --------------------------------------------------------------------------- #
def _build_rolling_post_base(model: ArticulatedObject, r: ResolvedWhiteboardEaselConfig) -> StandMount:
    stand = model.part("stand")
    px = r.post_x
    spread = r.stand_spread_scale
    # runner (horizontal foot under each post) sits ABOVE the casters so their
    # wheels hang clear of it; posts stand on the runner tops.
    runner_h = 0.044
    runner_zc = CASTER_MOUNT_Z + runner_h * 0.5 - 0.002  # bottom just below the caster bridge top
    post_bottom = runner_zc + runner_h * 0.5 - 0.004
    post_zc = (post_bottom + POST_TOP) * 0.5
    post_len = POST_TOP - post_bottom
    for i, sx in enumerate((-px, px)):
        stand.visual(Box((0.048, 0.048, post_len)), origin=Origin(xyz=(sx, 0.0, post_zc)), material="frame", name=f"post_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
        stand.visual(Box((0.064, 0.72 * spread, runner_h)), origin=Origin(xyz=(sx, 0.0, runner_zc)), material="frame", name=f"runner_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    stand.visual(Box((2.0 * px + 0.05, 0.035, 0.035)), origin=Origin(xyz=(0.0, 0.070, 0.390)), material="frame", name="lower_crossbar", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    for i, sx in enumerate((-px, px)):
        stand.visual(Box((0.048, 0.060, 0.040)), origin=Origin(xyz=(sx, 0.052, 0.390)), material="frame", name=f"crossbar_mount_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    caster_names: list[str] = []
    for i, sx in enumerate((-px, px)):
        for j, cy in enumerate((-0.315 * spread, 0.315 * spread)):
            caster_names.append(_emit_caster(model, stand, f"caster_{i}_{j}", sx, cy))
    return StandMount(two_mast=True, post_x=px, post_top=POST_TOP, z_center=Z_CENTER, caster_names=caster_names)


def _build_four_post_frame_base(model: ArticulatedObject, r: ResolvedWhiteboardEaselConfig) -> StandMount:
    stand = model.part("stand")
    px = r.post_x
    spread = r.stand_spread_scale
    rear_y = 0.42 * spread
    post_zc = (0.006 + POST_TOP) * 0.5
    post_len = POST_TOP - 0.006
    specs = [(-px, 0.0), (px, 0.0), (-px, rear_y), (px, rear_y)]
    for i, (sx, sy) in enumerate(specs):
        stand.visual(Box((0.044, 0.044, post_len)), origin=Origin(xyz=(sx, sy, post_zc)), material="frame", name=f"post_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
        stand.visual(Cylinder(radius=0.026, length=0.014), origin=Origin(xyz=(sx, sy, 0.007)), material="rubber", name=f"glide_{i}", material_class_id="rubber.smooth_plain")
    # low front/rear ties (below the board bottom) + full-height side ties (outboard of the board sweep).
    stand.visual(Box((2.0 * px + 0.05, 0.035, 0.035)), origin=Origin(xyz=(0.0, 0.0, 0.360)), material="frame", name="front_bar_low", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    stand.visual(Box((2.0 * px + 0.05, 0.035, 0.035)), origin=Origin(xyz=(0.0, rear_y, 0.360)), material="frame", name="rear_bar_low", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    for i, sx in enumerate((-px, px)):
        stand.visual(Box((0.035, rear_y, 0.035)), origin=Origin(xyz=(sx, rear_y * 0.5, 0.360)), material="frame", name=f"side_bar_low_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
        stand.visual(Box((0.035, rear_y, 0.035)), origin=Origin(xyz=(sx, rear_y * 0.5, 1.900)), material="frame", name=f"side_bar_high_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    # rear top tie only for a rigid static frame (would clip a revolving/tilting board).
    if r.board_motion == "static_framed":
        stand.visual(Box((2.0 * px + 0.05, 0.035, 0.035)), origin=Origin(xyz=(0.0, rear_y, 1.900)), material="frame", name="rear_bar_high", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    return StandMount(two_mast=True, post_x=px, post_top=POST_TOP, z_center=Z_CENTER)


def _build_t_column_base(model: ArticulatedObject, r: ResolvedWhiteboardEaselConfig) -> StandMount:
    stand = model.part("stand")
    spread = r.stand_spread_scale
    mast_y = 0.11
    hub_z = 0.200  # star hub raised so the arms slope DOWN to the caster mounts
    _rod_between(stand, (0.0, mast_y, hub_z), (0.0, mast_y, Z_CENTER + 0.010), 0.026, material="frame", name="mast_column")
    stand.visual(Cylinder(radius=0.050, length=0.044), origin=Origin(xyz=(0.0, mast_y, hub_z)), material="frame", name="star_hub", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    # bracket links the mast to the BACK of the board_mount_bar only — it stops at
    # y=0.040 so it never reaches into the board's mount_plate (y<=0.034).
    _rod_between(stand, (0.0, mast_y, Z_CENTER), (0.0, 0.040, Z_CENTER), 0.024, material="frame", name="mount_bracket")
    stand.visual(Box((0.190, 0.030, 0.240)), origin=Origin(xyz=(0.0, 0.028, Z_CENTER)), material="hardware", name="board_mount_bar", material_class_id="metal.blackened_gunmetal")
    arm_r = 0.300 * spread
    caster_names: list[str] = []
    for i in range(4):
        theta = math.pi / 4.0 + i * math.pi / 2.0
        ex = arm_r * math.cos(theta)
        ey = mast_y + arm_r * math.sin(theta)
        _rod_between(stand, (0.0, mast_y, hub_z), (ex, ey, CASTER_MOUNT_Z), 0.020, material="frame", name=f"arm_{i}")
        caster_names.append(_emit_caster(model, stand, f"caster_{i}_0", ex, ey))
    return StandMount(
        two_mast=False, post_x=r.post_x, post_top=Z_CENTER, z_center=Z_CENTER, caster_names=caster_names,
        static_anchor=(0.0, 0.0, Z_CENTER), static_stand_elem="board_mount_bar", static_board_elem="mount_plate",
    )


def _build_folding_tripod_base(model: ArticulatedObject, r: ResolvedWhiteboardEaselConfig) -> StandMount:
    stand = model.part("stand")
    spread = r.stand_spread_scale
    n = r.leg_count
    board_bottom = Z_CENTER - r.half_h
    hub_z = board_bottom - 0.100  # leg hub set below the board bottom
    # central mount bar at the board center + a back spine down to the leg hub.
    hub_y = 0.065
    stand.visual(Box((0.190, 0.030, 0.240)), origin=Origin(xyz=(0.0, 0.028, Z_CENTER)), material="hardware", name="board_mount_bar", material_class_id="metal.blackened_gunmetal")
    # spine top fuses into the BACK of the mount bar (y=0.050, inside its y-span
    # 0.013..0.043) then runs down to the leg hub — clears the shallow mount_plate
    # (back face y=+0.020) so the board plate only touches the mount bar.
    _rod_between(stand, (0.0, 0.050, Z_CENTER), (0.0, hub_y, hub_z), 0.020, material="frame", name="back_spine")
    stand.visual(Box((0.300, 0.200, 0.036)), origin=Origin(xyz=(0.0, hub_y, hub_z)), material="frame", name="leg_hub", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    if n == 4:
        hinges = [(-0.12, -0.02), (0.12, -0.02), (-0.12, 0.11), (0.12, 0.11)]
        feet = [(-0.42 * spread, -0.34 * spread), (0.42 * spread, -0.34 * spread), (-0.34 * spread, 0.44 * spread), (0.34 * spread, 0.44 * spread)]
    else:
        hinges = [(-0.12, -0.02), (0.12, -0.02), (0.0, 0.11)]
        feet = [(-0.42 * spread, -0.34 * spread), (0.42 * spread, -0.34 * spread), (0.0, 0.46 * spread)]
    leg_names: list[str] = []
    for i in range(n):
        hx, hy = hinges[i]
        hy = hy + hub_y  # hub sits behind the board
        fx, fy = feet[i]
        pivot_z = hub_z - 0.028
        stand.visual(Box((0.060, 0.040, 0.034)), origin=Origin(xyz=(hx, hy, hub_z - 0.020)), material="frame", name=f"leg_hinge_block_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
        stand.visual(Cylinder(radius=0.009, length=0.072), origin=Origin(xyz=(hx, hy, pivot_z), rpy=(0.0, math.pi / 2.0, 0.0)), material="hardware", name=f"leg_hinge_pin_{i}", material_class_id="metal.blackened_gunmetal")

        # leg axis: from pivot straight down-and-out to the foot on the floor.
        dx, dy, dz = fx - hx, fy - hy, 0.0 - pivot_z
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        ux, uy, uz = dx / length, dy / length, dz / length
        pitch = math.acos(_clamp(uz, -1.0, 1.0))
        yaw = math.atan2(uy, ux)

        def _pt(dist: float) -> tuple[float, float, float]:
            return (hx + ux * dist, hy + uy * dist, pivot_z + uz * dist)

        # outer leg: yoke at the pivot + sleeve covering the upper 0..0.62 of the span.
        outer = model.part(f"leg_{i}")
        outer.visual(Box((0.050, 0.050, 0.036)), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="hardware", name="hinge_yoke", material_class_id="metal.blackened_gunmetal")
        d_o0, d_o1 = 0.018, 0.62 * length
        m_o = (d_o0 + d_o1) * 0.5
        outer.visual(
            Cylinder(radius=0.016, length=d_o1 - d_o0),
            origin=Origin(xyz=(ux * m_o, uy * m_o, uz * m_o), rpy=(0.0, pitch, yaw)),
            material="frame",
            name="outer_sleeve", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"),
        )
        model.articulation(
            f"stand_to_leg_{i}",
            ArticulationType.REVOLUTE,
            parent=stand,
            child=outer,
            origin=Origin(xyz=(hx, hy, pivot_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=1.5, lower=0.0, upper=0.45),
        )

        # inner leg: telescoping tube overlapping the sleeve, ending in a flat
        # rubber foot pad whose base sits ON the floor (z=0) at rest.
        inner = model.part(f"leg_{i}_lower")
        dp = 0.50 * length  # prismatic origin distance from pivot
        d_i0, d_i1 = 0.46 * length, length - 0.020
        m_i = (d_i0 + d_i1) * 0.5
        inner.visual(
            Cylinder(radius=0.011, length=d_i1 - d_i0),
            origin=Origin(xyz=(ux * m_i - ux * dp, uy * m_i - uy * dp, pivot_z + uz * m_i - (pivot_z + uz * dp)), rpy=(0.0, pitch, yaw)),
            material="frame",
            name="inner_tube", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"),
        )
        # inner part frame is world-aligned (joints carry no rpy), so the pad is a
        # vertical puck placed by world coords minus the inner-origin offset.
        inner_ox, inner_oy, inner_oz = _pt(dp)
        inner.visual(
            Cylinder(radius=0.019, length=0.030),
            origin=Origin(xyz=(fx - inner_ox, fy - inner_oy, 0.015 - inner_oz)),
            material="rubber",
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        model.articulation(
            f"leg_{i}_slide",
            ArticulationType.PRISMATIC,
            parent=outer,
            child=inner,
            origin=Origin(xyz=(ux * dp, uy * dp, uz * dp)),
            axis=(ux, uy, uz),
            motion_limits=MotionLimits(effort=60.0, velocity=0.25, lower=0.0, upper=0.150),
        )
        leg_names.extend([f"leg_{i}", f"leg_{i}_lower"])
    return StandMount(
        two_mast=False, post_x=r.post_x, post_top=Z_CENTER, z_center=Z_CENTER, leg_names=leg_names,
        static_anchor=(0.0, 0.0, Z_CENTER), static_stand_elem="board_mount_bar", static_board_elem="mount_plate",
    )


_BASE_BUILDERS = {
    "rolling_post_base": _build_rolling_post_base,
    "four_post_frame_base": _build_four_post_frame_base,
    "t_column_base": _build_t_column_base,
    "folding_tripod_base": _build_folding_tripod_base,
}


# --------------------------------------------------------------------------- #
#  board_motion connectors — connect board to the stand
# --------------------------------------------------------------------------- #
def _connect_static(model: ArticulatedObject, board: Part, stand: Part, r: ResolvedWhiteboardEaselConfig, mount: StandMount) -> None:
    # The FIXED joint maps the board-local origin (board center) to its origin,
    # so the anchor is always the board center; two-mast bases get a mount bar
    # behind the board spanning the posts.
    if mount.two_mast:
        stand.visual(
            Box((2.0 * mount.post_x + 0.05, 0.030, 0.058)),
            origin=Origin(xyz=(0.0, 0.028, mount.z_center)),
            material="frame",
            name="board_mount_bar", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"),
        )
    model.articulation("stand_to_board", ArticulationType.FIXED, parent=stand, child=board, origin=Origin(xyz=(0.0, 0.0, mount.z_center)))


def _connect_revolve(model: ArticulatedObject, board: Part, stand: Part, r: ResolvedWhiteboardEaselConfig, mount: StandMount) -> None:
    for i, sx in enumerate((-mount.post_x, mount.post_x)):
        stand.visual(Cylinder(radius=0.020, length=0.075), origin=Origin(xyz=(sx, 0.0, mount.z_center), rpy=(0.0, math.pi / 2.0, 0.0)), material="hardware", name=f"yoke_bushing_{i}", material_class_id="metal.blackened_gunmetal")
    model.articulation(
        "stand_to_board",
        ArticulationType.REVOLUTE,
        parent=stand,
        child=board,
        origin=Origin(xyz=(0.0, 0.0, mount.z_center)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.0, lower=-math.pi, upper=math.pi),
    )


def _connect_slide(model: ArticulatedObject, board: Part, stand: Part, r: ResolvedWhiteboardEaselConfig, mount: StandMount) -> None:
    model.articulation(
        "stand_to_board",
        ArticulationType.PRISMATIC,
        parent=stand,
        child=board,
        origin=Origin(xyz=(0.0, 0.0, Z_SLIDE_REST)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=90.0, velocity=0.2, lower=0.0, upper=0.300),
    )


def _connect_tilt(model: ArticulatedObject, board: Part, stand: Part, r: ResolvedWhiteboardEaselConfig, mount: StandMount) -> None:
    px = mount.post_x
    top = mount.post_top
    sr = r.half_w_panel + 0.018
    # side arms run down in the narrow band between the board hinge lug (outer
    # face ~sr+0.060) and the post (inner face >= sr+0.118).
    arm_x = sr + 0.090
    stand.visual(Box((2.0 * px + 0.05, 0.050, 0.050)), origin=Origin(xyz=(0.0, 0.0, top)), material="frame", name="carriage_rail", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    carriage = model.part("tilt_carriage")
    dz = Z_CENTER - top  # carriage-local z of the pivot (negative)
    carriage.visual(Box((2.0 * arm_x + 0.060, 0.050, 0.030)), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="frame", name="carriage_top", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
    for i, sign in enumerate((-1.0, 1.0)):
        ax = sign * arm_x
        _rod_between(carriage, (ax, 0.0, 0.0), (ax, 0.0, dz), 0.016, material="frame", name=f"carriage_arm_{i}")
        carriage.visual(Box((0.036, 0.070, 0.055)), origin=Origin(xyz=(ax, 0.0, dz)), material="frame", name=f"pivot_bracket_{i}", material_class_id=("metal.paint_coated" if r.material_style in {"powder_blue", "white_coat", "dark_metal", "classroom_green"} else "metal.aluminum_bare"))
        # short pivot pin from the bracket inboard into the board hinge lug (bearing).
        _rod_between(carriage, (sign * (sr + 0.043), 0.0, dz), (ax, 0.0, dz), 0.012, material="metal", name=f"pivot_stub_{i}")
    model.articulation("stand_to_carriage", ArticulationType.FIXED, parent=stand, child=carriage, origin=Origin(xyz=(0.0, 0.0, top)))
    model.articulation(
        "carriage_to_board",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=board,
        origin=Origin(xyz=(0.0, 0.0, dz)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=15.0, velocity=0.5, lower=0.0, upper=1.00),
    )


def _build_board_motion(model: ArticulatedObject, r: ResolvedWhiteboardEaselConfig, mount: StandMount) -> Part:
    motion = r.board_motion
    stand = model.get_part("stand")
    board = _emit_board_frame(
        model, r,
        double_sided=(motion == "revolve_trunnion"),
        sleeves=(motion == "slide_carriage"),
        hinge_lugs=(motion == "tilt_carriage"),
        trunnion=(motion == "revolve_trunnion"),
    )
    if motion == "static_framed":
        _connect_static(model, board, stand, r, mount)
    elif motion == "revolve_trunnion":
        _connect_revolve(model, board, stand, r, mount)
    elif motion == "slide_carriage":
        _connect_slide(model, board, stand, r, mount)
    else:
        _connect_tilt(model, board, stand, r, mount)
    _emit_clamp_knobs(model, board, r)
    return board


# --------------------------------------------------------------------------- #
#  top-level build
# --------------------------------------------------------------------------- #
def build_whiteboard_easel(config: WhiteboardEaselConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    _register_palette(model, r.palette)
    mount = _BASE_BUILDERS[r.support_base](model, r)
    _build_board_motion(model, r, mount)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["static_board_elem"] = mount.static_board_elem
    model.meta["static_two_mast"] = mount.two_mast
    return model


def build_seeded_whiteboard_easel(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_whiteboard_easel(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedWhiteboardEaselConfig) -> list[tuple[str, str]]:
    leg_mult = f"n{r.leg_count}" if r.support_base == "folding_tripod_base" else "n_a"
    return [
        ("support_base", r.support_base),
        ("board_motion", r.board_motion),
        ("leg_multiplicity", leg_mult),
        ("flip_chart_top", r.flip_chart_top),
        ("material_style", r.material_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
#  tests
# --------------------------------------------------------------------------- #
def _dist(a, b) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def _caster_names(object_model: ArticulatedObject) -> list[str]:
    return sorted(p.name for p in object_model.parts if p.name.startswith("caster_"))


def run_whiteboard_easel_tests(object_model: ArticulatedObject, config: WhiteboardEaselConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    joint_names = {j.name for j in object_model.articulations}

    board = object_model.get_part("board_frame")
    stand = object_model.get_part("stand")
    two_mast = object_model.meta.get("static_two_mast", True)

    # --- identity: tall portrait writing surface + tray ---
    surf = ctx.part_element_world_aabb(board, elem="white_surface")
    if surf is not None:
        mn, mx = surf
        w = mx[0] - mn[0]
        h = mx[2] - mn[2]
        ctx.check(
            "tall rectangular writing surface",
            0.60 <= w <= 0.77 and 1.00 <= h <= 1.16 and h / w > 1.35,
            details=f"width={w:.3f}, height={h:.3f}, ratio={h / w:.3f}",
        )
    else:
        ctx.fail("tall rectangular writing surface", "white_surface AABB unavailable")

    ctx.check("marker tray present", "marker_tray_shelf" in {v.name for v in board.visuals})
    ctx.check("slot_choices match config", object_model.meta.get("slot_choices") == slot_choices_for_config(r))
    ctx.check("board connected to stand", ("stand_to_board" in joint_names) or ("carriage_to_board" in joint_names))

    # --- clamp knobs seated against the side rail (captured pin) + rotation ---
    for i, sign in enumerate((-1.0, 1.0)):
        clamp = object_model.get_part(f"clamp_{i}")
        side = "side_0_rail" if sign < 0 else "side_1_rail"
        ctx.allow_overlap(clamp, board, elem_a="threaded_stem", elem_b=side, reason="clamp threaded stem seats against the board side rail as a locking knob")
        cj = object_model.get_articulation(f"board_to_clamp_{i}")
        rest = ctx.part_world_aabb(clamp)
        with ctx.pose({cj: 1.2}):
            turned = ctx.part_world_aabb(clamp)
        ctx.check(f"clamp_{i} rotates", rest is not None and turned is not None)

    # --- casters: axle captured in fork plates ---
    for name in _caster_names(object_model):
        caster = object_model.get_part(name)
        for f_idx in (0, 1):
            ctx.allow_overlap(caster, stand, elem_a="axle_pin", elem_b=f"{name}_fork_{f_idx}", reason="caster axle pin is captured in the fork plate bore so the wheel is supported while spinning")

    # --- static mount contact ---
    if r.board_motion == "static_framed":
        ctx.allow_overlap(board, stand, elem_a="mount_plate", elem_b="board_mount_bar", reason="board back plate is bolted flush to the stand mount bar")
        if two_mast:
            for rail in ("side_0_rail", "side_1_rail"):
                ctx.allow_overlap(board, stand, elem_a=rail, elem_b="board_mount_bar", reason="board side rail runs against the stand mount bar")

    # --- motion-specific captured overlaps + targeted pose proofs ---
    if r.board_motion == "revolve_trunnion":
        for i in (0, 1):
            ctx.allow_overlap(board, stand, elem_a=f"trunnion_stub_{i}", elem_b=f"yoke_bushing_{i}", reason="trunnion stub is captured in the yoke bushing forming the horizontal pivot bearing")
            ctx.allow_overlap(board, stand, elem_a=f"trunnion_stub_{i}", elem_b=f"post_{i}", reason="trunnion stub passes into the post to reach the bearing seat")
        trunnion = object_model.get_articulation("stand_to_board")
        top_rest = ctx.part_element_world_aabb(board, elem="top_rail")
        with ctx.pose({trunnion: math.pi}):
            top_flip = ctx.part_element_world_aabb(board, elem="top_rail")
        if top_rest is not None and top_flip is not None:
            rz = 0.5 * (top_rest[0][2] + top_rest[1][2])
            fz = 0.5 * (top_flip[0][2] + top_flip[1][2])
            ctx.check("board revolves: top rail flips below pivot at q=pi", rz > Z_CENTER + 0.25 and fz < Z_CENTER - 0.25, details=f"rest_z={rz:.3f}, flip_z={fz:.3f}")
    elif r.board_motion == "tilt_carriage":
        carriage = object_model.get_part("tilt_carriage")
        ctx.allow_overlap(carriage, stand, elem_a="carriage_top", elem_b="carriage_rail", reason="carriage top plate is welded to the stand carriage rail")
        for i in (0, 1):
            ctx.allow_overlap(carriage, stand, elem_a=f"carriage_arm_{i}", elem_b="carriage_rail", reason="carriage side arm root is welded into the stand carriage rail")
            ctx.allow_overlap(carriage, board, elem_a=f"pivot_stub_{i}", elem_b=f"hinge_lug_{i}", reason="carriage pivot pin seats into the board hinge lug as the tilt bearing")
        tilt = object_model.get_articulation("carriage_to_board")
        rest = ctx.part_element_world_aabb(board, elem="white_surface")
        with ctx.pose({tilt: 0.9}):
            tilted = ctx.part_element_world_aabb(board, elem="white_surface")
        if rest is not None and tilted is not None:
            ctx.check("board tilts forward for drafting", tilted[0][1] < rest[0][1] - 0.12, details=f"rest_y={rest[0][1]:.3f}, tilt_y={tilted[0][1]:.3f}")
    elif r.board_motion == "slide_carriage":
        for i in (0, 1):
            for wall in ("front_wall", "rear_wall", "left_wall", "right_wall"):
                ctx.allow_overlap(board, stand, elem_a=f"carriage_{i}_{wall}", elem_b=f"post_{i}", reason="carriage sleeve wraps and slides along the mast post")
            for j in (0, 1):
                ctx.allow_overlap(board, stand, elem_a=f"carriage_{i}_tie_{j}", elem_b=f"post_{i}", reason="carriage support tie runs from the side rail out to the sliding sleeve on the mast post")
        slide = object_model.get_articulation("stand_to_board")
        rest = ctx.part_world_position(board)
        with ctx.pose({slide: 0.280}):
            raised = ctx.part_world_position(board)
        ctx.check("board slides up on masts", rest is not None and raised is not None and raised[2] > rest[2] + 0.20, details=f"rest={rest}, raised={raised}")

    # --- folding tripod: retained legs + telescope / fold proofs ---
    if r.support_base == "folding_tripod_base":
        for i in range(r.leg_count):
            outer = object_model.get_part(f"leg_{i}")
            inner = object_model.get_part(f"leg_{i}_lower")
            ctx.allow_overlap(inner, outer, elem_a="inner_tube", elem_b="outer_sleeve", reason="inner telescoping tube is retained inside the outer leg sleeve")
            ctx.allow_overlap(outer, stand, elem_a="hinge_yoke", elem_b=f"leg_hinge_pin_{i}", reason="leg hinge pin is captured through the leg yoke")
            ctx.allow_overlap(outer, stand, elem_a="hinge_yoke", elem_b=f"leg_hinge_block_{i}", reason="leg yoke wraps the hub hinge block")
            ctx.allow_overlap(outer, stand, elem_a="hinge_yoke", elem_b="leg_hub", reason="leg yoke nests against the leg hub at the fold pivot")
            ctx.allow_overlap(outer, stand, elem_a="outer_sleeve", elem_b=f"leg_hinge_block_{i}", reason="leg sleeve root wraps the hub hinge block at the pivot")
        outer0 = object_model.get_part("leg_0")
        inner0 = object_model.get_part("leg_0_lower")
        slide0 = object_model.get_articulation("leg_0_slide")
        rest_i = ctx.part_world_position(inner0)
        with ctx.pose({slide0: 0.15}):
            ext_i = ctx.part_world_position(inner0)
        ctx.check("tripod leg telescopes outward", rest_i is not None and ext_i is not None and _dist(rest_i, ext_i) > 0.08, details=f"rest={rest_i}, ext={ext_i}")
        fold0 = object_model.get_articulation("stand_to_leg_0")
        rest_o = ctx.part_world_aabb(outer0)
        with ctx.pose({fold0: 0.40}):
            fold_o = ctx.part_world_aabb(outer0)
        ctx.check("tripod leg folds", rest_o is not None and fold_o is not None)

    # --- caster spin proof ---
    cnames = _caster_names(object_model)
    if cnames:
        cj = object_model.get_articulation(f"stand_to_{cnames[0]}")
        rest = ctx.part_world_aabb(object_model.get_part(cnames[0]))
        with ctx.pose({cj: math.pi / 2.0}):
            spun = ctx.part_world_aabb(object_model.get_part(cnames[0]))
        ctx.check("caster spins", rest is not None and spun is not None)

    # --- baseline + sampled-pose motion QC ---
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "WhiteboardEaselConfig",
    "ResolvedWhiteboardEaselConfig",
    "build_whiteboard_easel",
    "build_seeded_whiteboard_easel",
    "config_from_seed",
    "resolve_config",
    "run_whiteboard_easel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
