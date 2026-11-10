# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'ironing_board2' template.

Rebuilt from the two ``pictureX/0611/ironing_board2`` origin records and the five
accepted forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_ironing_board2.md``.

Category identity: one padded ironing top plus the support that holds it at
working height and folds away.  Two independent structural axes:

* ``board_style``   — a tapered capsule top, a straight slotted pan, or a top
  that also carries a hinged sleeve board.
* ``support_style`` — scissor leg frames, long floor X-legs, short tabletop
  legs, telescoping height posts, or a wall bracket with a prop arm.

Coordinate frame: the board is the assembly root.  +X runs from the wide (heel)
end at ``-half`` to the narrow (nose) end at ``+half``, +Y is the board width,
and the ironing surface is z = 0 with the shell hanging into -Z.  A support
therefore reaches down to ``-board_height_m``.

This file is the only runtime truth.  It imports the stdlib and the Articraft
``sdk`` only.
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
    Box,
    Cylinder,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    register_interface_mate,
)

BoardStyle = Literal["tapered_capsule", "rect_slotted"]
SleeveOption = Literal["plain_top", "sleeve_board"]
CoverStyle = Literal["plain", "grid", "ellipse"]
SupportStyle = Literal[
    "scissor_legs",
    "floor_x_legs",
    "short_tabletop_legs",
    "telescoping_posts",
    "wall_bracket",
]

BOARD_STYLES: tuple[BoardStyle, ...] = ("tapered_capsule", "rect_slotted")
SLEEVE_OPTIONS: tuple[SleeveOption, ...] = ("plain_top", "sleeve_board")
COVER_STYLES: tuple[CoverStyle, ...] = ("plain", "grid", "ellipse")
SUPPORT_STYLES: tuple[SupportStyle, ...] = (
    "scissor_legs",
    "floor_x_legs",
    "short_tabletop_legs",
    "telescoping_posts",
    "wall_bracket",
)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("board_style", BOARD_STYLES),
        component_slot("sleeve_option", SLEEVE_OPTIONS),
        component_slot("support_style", SUPPORT_STYLES),
    )
)

_BOARD_LENGTH_RANGE = (0.620, 1.250)
_BOARD_WIDTH_RANGE = (0.260, 0.460)
_BOARD_HEIGHT_RANGE = (0.600, 0.950)
_TAPER_RATIO_RANGE = (0.34, 0.74)
_SPREAD_RATIO_RANGE = (0.34, 0.72)
_BOARD_STYLE_DIMENSIONS = {
    # Full-height boards: the source silhouettes stay slender without the
    # implausible 0.62 m x 0.46 m and 1.25 m x 0.26 m seed cross-products.
    "tapered_capsule": ((0.900, 1.250), (0.300, 0.440)),
    # The second origin is a compact tabletop board with a broader capsule.
    "rect_slotted": ((0.620, 0.940), (0.280, 0.410)),
}

_SHELL_T = 0.012  # board shell depth below the ironing surface
_PAD_T = 0.006
_TUBE = 0.010
_HINGE_R = 0.0090
_WELD = 0.0008
_CLEAR = 0.0015
_STATION_X = 0.30  # leg stations sit at +-station_x * half length
_CAP_NODES = 16  # arc steps across each round board end
_BODY_NODES_MAX = 16  # cap on the width steps along the tapered run
# Width of the cover band wrapped over the board edge.  Every plate strip is
# inscribed to its narrower station, so the band has to be wider than one step's
# width drop for it to always overlap the strip it covers.
_RIM_T = 0.013
# Height step between overlapping board layers.  Coplanar top faces on two
# solids that lap over each other z-fight into speckle and fan artefacts.
_LAYER = 0.00025


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    board_style: BoardStyle = "tapered_capsule"
    sleeve_option: SleeveOption = "plain_top"
    cover_style: CoverStyle = "grid"
    support_style: SupportStyle = "scissor_legs"
    board_length_m: float | None = None
    board_width_m: float | None = None
    board_height_m: float | None = None
    taper_ratio: float | None = None
    spread_ratio: float | None = None
    name: str = "pictureX_0611_ironing_board2"


@dataclass(frozen=True)
class ResolvedConfig:
    board_style: BoardStyle
    sleeve_option: SleeveOption
    cover_style: CoverStyle
    support_style: SupportStyle
    board_length_m: float
    board_width_m: float
    board_height_m: float
    taper_ratio: float
    spread_ratio: float
    # derived
    half_length_m: float
    nose_width_m: float
    support_height_m: float
    station_x_m: float
    spread_m: float
    fold_rad: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x1B0A2D)
    length_range, width_range = _BOARD_STYLE_DIMENSIONS[choices["board_style"]]
    length = rng.uniform(*length_range)
    # Keep every sampled board in a source-like aspect band.  The public
    # Config still accepts the full authored ranges for intentional corners.
    width_low = max(width_range[0], length / 3.55)
    width_high = min(width_range[1], length / 2.15)
    if width_low > width_high:
        width_low = width_high = _clamp(length / 2.75, *width_range)
    return Config(
        board_style=choices["board_style"],
        sleeve_option=choices["sleeve_option"],
        support_style=choices["support_style"],
        cover_style=COVER_STYLES[rng.randrange(len(COVER_STYLES))],
        board_length_m=round(length, 5),
        board_width_m=round(rng.uniform(width_low, width_high), 5),
        board_height_m=round(rng.uniform(*_BOARD_HEIGHT_RANGE), 5),
        taper_ratio=round(rng.uniform(*_TAPER_RATIO_RANGE), 5),
        spread_ratio=round(rng.uniform(*_SPREAD_RATIO_RANGE), 5),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "board_style": config.board_style,
            "sleeve_option": config.sleeve_option,
            "support_style": config.support_style,
        }
    )
    if config.cover_style not in COVER_STYLES:
        raise ValueError(f"cover_style must be one of {COVER_STYLES}, got {config.cover_style!r}")
    length = 0.980 if config.board_length_m is None else float(config.board_length_m)
    width = 0.330 if config.board_width_m is None else float(config.board_width_m)
    height = 0.820 if config.board_height_m is None else float(config.board_height_m)
    taper = 0.52 if config.taper_ratio is None else float(config.taper_ratio)
    spread = 0.52 if config.spread_ratio is None else float(config.spread_ratio)
    _range_check("board_length_m", length, _BOARD_LENGTH_RANGE)
    _range_check("board_width_m", width, _BOARD_WIDTH_RANGE)
    _range_check("board_height_m", height, _BOARD_HEIGHT_RANGE)
    _range_check("taper_ratio", taper, _TAPER_RATIO_RANGE)
    _range_check("spread_ratio", spread, _SPREAD_RATIO_RANGE)

    half = length / 2.0
    # Short tabletop legs and the wall bracket use a fraction of the standing
    # height; every other support reaches the floor.
    if config.support_style == "short_tabletop_legs":
        support_height = height * 0.34
    elif config.support_style == "wall_bracket":
        support_height = height * 0.55
    else:
        support_height = height
    station = half * _STATION_X
    foot_spread = support_height * spread
    # A support may fold only until it lies just under the board, never into it.
    rest_tilt = math.atan(spread * 0.82)
    fold = _clamp(math.pi / 2.0 - rest_tilt - 0.12, 0.40, 1.18)
    return ResolvedConfig(
        board_style=config.board_style,
        sleeve_option=config.sleeve_option,
        cover_style=config.cover_style,
        support_style=config.support_style,
        board_length_m=length,
        board_width_m=width,
        board_height_m=height,
        taper_ratio=taper,
        spread_ratio=spread,
        half_length_m=half,
        nose_width_m=width * taper,
        support_height_m=support_height,
        station_x_m=station,
        spread_m=foot_spread,
        fold_rad=fold,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("board_style", config.board_style),
        ("sleeve_option", config.sleeve_option),
        ("support_style", config.support_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    cover_rgba = {
        "plain": (0.24, 0.57, 0.60, 1.0),
        "grid": (0.82, 0.84, 0.82, 1.0),
        "ellipse": (0.63, 0.72, 0.76, 1.0),
    }[r.cover_style]
    seam_rgba = {
        "plain": (0.16, 0.40, 0.42, 1.0),
        "grid": (0.42, 0.45, 0.44, 1.0),
        "ellipse": (0.36, 0.46, 0.52, 1.0),
    }[r.cover_style]
    model.material("cover_fabric", rgba=cover_rgba)
    model.material("cover_seam", rgba=seam_rgba)
    model.material("mesh_steel", rgba=(0.72, 0.74, 0.76, 1.0))
    model.material("chrome_tube", rgba=(0.80, 0.82, 0.84, 1.0))
    model.material("dark_fitting", rgba=(0.18, 0.19, 0.20, 1.0))
    model.material("foot_rubber", rgba=(0.06, 0.06, 0.06, 1.0))
    return {
        "cover": "cover_fabric",
        "seam": "cover_seam",
        "mesh": "mesh_steel",
        "tube": "chrome_tube",
        "fitting": "dark_fitting",
        "foot": "foot_rubber",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="fabric.upholstery_plain")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.chrome_polished",
    )


_Y_AXIS_RPY = (math.pi / 2.0, 0.0, 0.0)
_X_AXIS_RPY = (0.0, math.pi / 2.0, 0.0)


def _bar_xz(part, p0, p1, thickness, width, material, name) -> None:
    dx = p1[0] - p0[0]
    dz = p1[2] - p0[2]
    length = math.hypot(dx, dz)
    _box(
        part,
        (length + thickness, width, thickness),
        ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, (p0[2] + p1[2]) / 2.0),
        material,
        name,
        rpy=(0.0, -math.atan2(dz, dx), 0.0),
    )


def _bar_yz(part, p0, p1, thickness, width, material, name) -> None:
    dy = p1[1] - p0[1]
    dz = p1[2] - p0[2]
    length = math.hypot(dy, dz)
    _box(
        part,
        (width, length + thickness, thickness),
        ((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0, (p0[2] + p1[2]) / 2.0),
        material,
        name,
        rpy=(math.atan2(dz, dy), 0.0, 0.0),
    )


def _tube_ring(
    part,
    *,
    radius: float,
    wall: float,
    z: float,
    height: float,
    segments: int,
    x: float,
    material: str,
    prefix: str,
) -> None:
    """A hollow sleeve: wall boxes on a circle, open for the tube that runs in it."""
    for index in range(segments):
        angle = 2.0 * math.pi * float(index) / float(segments)
        tangential = 2.0 * math.pi * radius / float(segments) * 1.35 + wall
        _box(
            part,
            (tangential, wall, height),
            (x + radius * math.sin(angle), radius * math.cos(angle), z),
            material,
            f"{prefix}_{index}",
            rpy=(0.0, 0.0, -angle),
        )


def _spin_joint(
    model: ArticulatedObject,
    parent,
    child,
    *,
    name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    radius: float,
    joint_type: ArticulationType,
    limits: MotionLimits,
    child_radial: tuple[float, float, float] | None = None,
    meta: dict | None = None,
) -> str:
    provider = AxisInterface(
        name=f"{name}__provider",
        point=point,
        axis=axis,
        radial=radial,
        radius=radius + _CLEAR,
    )
    consumer = AxisInterface(
        name=f"{name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=radial if child_radial is None else child_radial,
        radius=radius,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        joint_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=1.4, friction=0.7),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)
    return name


# --------------------------------------------------------------------------- #
# board_style candidates
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Board:
    part: object
    half_width_at: object  # callable: x -> half width of the board at that x


@dataclass(frozen=True)
class _Planform:
    """The board plan: one tapered run closed by a round cap at each end."""

    heel_center_x: float
    heel_radius: float
    nose_center_x: float
    nose_radius: float
    taper_exponent: float


def _planform(r: ResolvedConfig) -> _Planform:
    half = r.half_length_m
    wide = r.board_width_m / 2.0
    if r.board_style == "rect_slotted":
        # A true stadium.  The caps carry exactly the run's own half width, so
        # the flanks run straight into the arc instead of stepping at the joint.
        return _Planform(-half + wide, wide, half - wide, wide, 1.0)
    narrow = r.nose_width_m / 2.0
    return _Planform(-half + wide, wide, half - narrow, narrow, 1.45)


def _half_width(r: ResolvedConfig, x: float) -> float:
    """Rounded source-like planform, wide at the heel and narrow at the nose."""
    p = _planform(r)
    x = _clamp(x, -r.half_length_m, r.half_length_m)
    if x < p.heel_center_x:
        dx = x - p.heel_center_x
        return math.sqrt(max(p.heel_radius * p.heel_radius - dx * dx, 0.0))
    if x > p.nose_center_x:
        dx = x - p.nose_center_x
        return math.sqrt(max(p.nose_radius * p.nose_radius - dx * dx, 0.0))
    frac = (x - p.heel_center_x) / max(p.nose_center_x - p.heel_center_x, 1e-6)
    return p.heel_radius + (p.nose_radius - p.heel_radius) * frac**p.taper_exponent


def _body_node_count(r: ResolvedConfig) -> int:
    """Enough steps that no single step drops more width than the rim can cover.

    A straight-flanked board needs exactly one, and pays for nothing more.
    """
    p = _planform(r)
    drop = abs(p.heel_radius - p.nose_radius)
    return max(1, min(_BODY_NODES_MAX, math.ceil(drop / (_RIM_T * 0.80))))


def _body_stations(r: ResolvedConfig, segments: int) -> list[float]:
    """x samples spaced so every step drops the same half width.

    Sampling the tapered run uniformly in x stairsteps hardest exactly where the
    taper steepens.  Inverting the taper exponent makes the width step constant,
    which is what the rim band has to be able to cover.
    """
    p = _planform(r)
    span = p.nose_center_x - p.heel_center_x
    power = 1.0 / p.taper_exponent
    return [
        p.heel_center_x + span * (float(index) / float(segments)) ** power
        for index in range(segments + 1)
    ]


def _cap_angles(segments: int) -> list[float]:
    """Arc parameters across a board end, from one flank to the other."""
    return [
        -math.pi / 2.0 + math.pi * float(index) / float(segments) for index in range(segments + 1)
    ]


def _outline_loop(r: ResolvedConfig) -> list[tuple[float, float]]:
    """The closed planform outline, walked counter-clockwise from the heel flank.

    The caps are walked by arc angle rather than by x: an x-parametrised chain
    cannot describe an end that turns through 180 degrees, which is why the old
    perimeter chain crossed the centreline and threw a plate past each tip.
    """
    p = _planform(r)
    points: list[tuple[float, float]] = []
    for t in _cap_angles(_CAP_NODES):
        points.append((p.heel_center_x - p.heel_radius * math.cos(t), p.heel_radius * math.sin(t)))
    stations = _body_stations(r, _body_node_count(r))
    for x in stations[1:-1]:
        points.append((x, _half_width(r, x)))
    for t in reversed(_cap_angles(_CAP_NODES)):
        points.append((p.nose_center_x + p.nose_radius * math.cos(t), p.nose_radius * math.sin(t)))
    for x in reversed(stations[1:-1]):
        points.append((x, -_half_width(r, x)))
    loop: list[tuple[float, float]] = []
    for point in points:
        if not loop or math.hypot(point[0] - loop[-1][0], point[1] - loop[-1][1]) > 1e-7:
            loop.append(point)
    while len(loop) > 3 and math.hypot(loop[0][0] - loop[-1][0], loop[0][1] - loop[-1][1]) <= 1e-7:
        loop.pop()
    return loop


def _add_body_plate(part, r: ResolvedConfig, mats, stations, *, prefix: str) -> None:
    """Pad and pan strips along the tapered run.

    Each strip is inscribed to the narrower of its two stations, so no strip can
    poke out past the rim band that wraps the edge.
    """
    for index in range(len(stations) - 1):
        x0 = stations[index]
        x1 = stations[index + 1]
        width = 2.0 * min(_half_width(r, x0), _half_width(r, x1))
        if width <= 0.004 or x1 - x0 <= 1e-6:
            continue
        _box(
            part,
            (x1 - x0 + 3.0 * _WELD, width, _PAD_T),
            ((x0 + x1) / 2.0, 0.0, _PAD_T / 2.0),
            mats["cover"],
            f"{prefix}_pad_{index}",
        )
        _box(
            part,
            (x1 - x0 + 2.0 * _WELD, max(width - 0.006, 0.004), _SHELL_T),
            ((x0 + x1) / 2.0, 0.0, -_SHELL_T / 2.0 + _WELD),
            mats["mesh"],
            f"{prefix}_shell_{index}",
        )


def _cap_disc_inset(r: ResolvedConfig, *, center_x: float, radius: float, inward: float) -> float:
    """How far a one-piece cap disc has to shrink to stay tucked inside the board.

    Two constraints: it must not poke past the chord polygon the rim band is
    built on, and its inboard half must not push out through the flank it runs
    into, which a sharp taper narrows faster than the disc does.
    """
    inset = radius * (1.0 - math.cos(math.pi / (2.0 * _CAP_NODES))) + 0.0005
    for index in range(1, 65):
        d = radius * float(index) / 65.0
        flank = _half_width(r, center_x + inward * d)
        inset = max(inset, radius - math.hypot(flank, d))
    return _clamp(inset, 0.0, _RIM_T * 0.62)


def _add_cap_plate(
    part, r: ResolvedConfig, mats, *, center_x: float, radius: float, inward: float, prefix: str
) -> None:
    """A round board end as one disc.

    A fan of pie wedges is exactly round too, but sixteen of them meeting at the
    cap centre draw a sunburst of interpenetration seams across the pad.
    """
    disc = radius - _cap_disc_inset(r, center_x=center_x, radius=radius, inward=inward)
    # Tier 1: the disc sits over the body strips, which it overlaps for its whole
    # inboard half.  Sharing their exact top plane makes the two z-fight, and a
    # cylinder's fan-tessellated cap turns that into a sunburst across the pad.
    pad_h = _PAD_T + _LAYER
    _cyl(part, disc, pad_h, (center_x, 0.0, pad_h / 2.0), mats["cover"], f"{prefix}_pad")
    shell_h = _SHELL_T + _LAYER
    _cyl(
        part,
        max(disc - 0.003, 0.004),
        shell_h,
        (center_x, 0.0, -shell_h / 2.0 + _WELD),
        mats["mesh"],
        f"{prefix}_shell",
    )


def _add_rim(part, r: ResolvedConfig, mats, loop, *, prefix: str) -> None:
    """The cover pulled over the pan edge: a wrap band, a rolled bead, a hem cord.

    Every piece is aligned to the local outline tangent and offset along the
    inward normal, so the band's outer face lies on the true planform and the
    bead's outer surface is tangent to it.
    """
    bead_r = 0.0052
    hem_r = 0.0026
    count = len(loop)
    for index in range(count):
        x0, y0 = loop[index]
        x1, y1 = loop[(index + 1) % count]
        run = math.hypot(x1 - x0, y1 - y0)
        if run <= 1e-6:
            continue
        yaw = math.atan2(y1 - y0, x1 - x0)
        # Inward normal of a counter-clockwise loop.
        nx = (y1 - y0) / run
        ny = -(x1 - x0) / run
        mx = (x0 + x1) / 2.0
        my = (y0 + y1) / 2.0
        # Tier 2: proud of both the strips and the cap discs it laps over, which
        # is also how a bound cover edge actually stands on the board.
        wrap_h = _SHELL_T + _PAD_T + 4.0 * _LAYER
        _box(
            part,
            (run + _RIM_T, _RIM_T, wrap_h),
            (
                mx + nx * _RIM_T / 2.0,
                my + ny * _RIM_T / 2.0,
                _PAD_T + 2.0 * _LAYER - wrap_h / 2.0,
            ),
            mats["cover"],
            f"{prefix}_wrap_{index}",
            rpy=(0.0, 0.0, yaw),
        )
        _cyl(
            part,
            bead_r,
            run + bead_r,
            (mx + nx * bead_r, my + ny * bead_r, _PAD_T - bead_r * 0.40),
            mats["cover"],
            f"{prefix}_bead_{index}",
            rpy=(0.0, math.pi / 2.0, yaw),
        )
        _cyl(
            part,
            hem_r,
            run + hem_r,
            (
                mx + nx * (_RIM_T + hem_r * 0.5),
                my + ny * (_RIM_T + hem_r * 0.5),
                -_SHELL_T + hem_r * 0.35,
            ),
            mats["seam"],
            f"{prefix}_hem_{index}",
            rpy=(0.0, math.pi / 2.0, yaw),
        )


def _add_top(part, r: ResolvedConfig, mats, *, prefix: str) -> None:
    """Padded fabric top, pressed pan, wrapped edge, vents and cover pattern."""
    p = _planform(r)
    _add_body_plate(part, r, mats, _body_stations(r, _body_node_count(r)), prefix=prefix)
    _add_cap_plate(
        part,
        r,
        mats,
        center_x=p.heel_center_x,
        radius=p.heel_radius,
        inward=1.0,
        prefix=f"{prefix}_heel",
    )
    _add_cap_plate(
        part,
        r,
        mats,
        center_x=p.nose_center_x,
        radius=p.nose_radius,
        inward=-1.0,
        prefix=f"{prefix}_nose",
    )
    _add_rim(part, r, mats, _outline_loop(r), prefix=prefix)
    # Pressed-pan vent recesses remain visible from below without perforating
    # the padded top.  They follow the local width rather than a box AABB.
    for ix in range(-5, 6):
        x = r.half_length_m * 0.72 * float(ix) / 5.0
        half_width = _half_width(r, x)
        for iy in (-0.55, 0.0, 0.55):
            y = half_width * iy
            _cyl(
                part,
                0.0032,
                0.0016,
                (x, y, -_SHELL_T + 0.0003),
                mats["fitting"],
                f"{prefix}_vent_{ix + 5}_{iy:+.2f}",
            )

    # Two source-backed cover treatments: the irregular grid from origin 001
    # and the elliptical patches from origin 002.  "plain" keeps a clean pad.
    if r.cover_style == "grid":
        for index in range(-5, 6):
            x = r.half_length_m * 0.78 * float(index) / 5.0
            width = max(2.0 * _half_width(r, x) - 0.026, 0.010)
            _box(
                part,
                (0.0015, width, 0.0008),
                (x, 0.004 * float(index % 3 - 1), _PAD_T + 0.0003),
                mats["seam"],
                f"{prefix}_grid_cross_{index + 5}",
                rpy=(0.0, 0.0, 0.08 * float(index % 2)),
            )
        for index, y_ratio in enumerate((-0.52, -0.18, 0.18, 0.52)):
            _box(
                part,
                (r.board_length_m * 0.76, 0.0015, 0.0008),
                (0.0, y_ratio * r.board_width_m / 2.0, _PAD_T + 0.0003),
                mats["seam"],
                f"{prefix}_grid_long_{index}",
                rpy=(0.0, 0.0, 0.025 * (-1.0 if index % 2 else 1.0)),
            )
    elif r.cover_style == "ellipse":
        for index, (x_ratio, y_ratio, angle) in enumerate(
            ((-0.52, -0.18, -0.22), (-0.18, 0.20, 0.15), (0.18, -0.20, -0.12), (0.48, 0.16, 0.24))
        ):
            x = x_ratio * r.half_length_m
            local_half = _half_width(r, x)
            _box(
                part,
                (r.board_length_m * 0.13, max(local_half * 0.42, 0.024), 0.0009),
                (x, y_ratio * local_half, _PAD_T + 0.00035),
                mats["seam"],
                f"{prefix}_ellipse_patch_{index}",
                rpy=(0.0, 0.0, angle),
            )
    # One central spine under the shell ties the support stations together and
    # keeps the leg, brace and prop paths clear.
    _box(
        part,
        (2.0 * r.half_length_m * 0.86, 0.030, 0.010),
        (0.0, 0.0, -_SHELL_T - 0.004),
        mats["mesh"],
        f"{prefix}_spine",
    )


def _board_style_tapered_capsule_build(model, r, mats) -> _Board:
    """001 L26-L131: the tapering capsule top with a vented tray and cover."""
    part = model.part(
        "board_style__tapered_capsule__board",
        meta={"role": "board", "construction": "tapered capsule top"},
    )
    _add_top(part, r, mats, prefix="capsule")
    return _Board(part=part, half_width_at=lambda x: _half_width(r, x))


def _board_style_rect_slotted_build(model, r, mats) -> _Board:
    """002 L29-L132: the straight slotted pan with elliptical patches."""
    part = model.part(
        "board_style__rect_slotted__board",
        meta={"role": "board", "construction": "straight slotted pan"},
    )
    _add_top(part, r, mats, prefix="pan")
    # Real slots pressed through the pan, the feature that names this top.
    rows = 7
    for index in range(rows):
        x = -r.half_length_m * 0.80 + 2.0 * r.half_length_m * 0.80 * float(index) / float(rows - 1)
        _box(
            part,
            (0.014, 2.0 * _half_width(r, x) - 0.030, 0.004),
            (x, 0.0, -_PAD_T - 0.002),
            mats["fitting"],
            f"pan_slot_{index}",
        )
    return _Board(part=part, half_width_at=lambda x: _half_width(r, x))


def _sleeve_option_plain_top_build(model, r, mats, board: _Board) -> None:
    """001/002: the top is a single ironing surface."""

    return None


def _sleeve_option_sleeve_board_build(model, r, mats, board: _Board) -> None:
    """sleeve fork L326-L461: a second hinged sleeve surface over the main top.

    The hinge posts stand on whichever top construction was built, so the sleeve
    rides the capsule and the slotted pan alike.
    """

    part = board.part
    prefix = "sleeve_option__sleeve_board"
    hinge_x = -r.half_length_m * 0.10
    board_edge_y = board.half_width_at(hinge_x)
    hinge_y = board_edge_y + 0.016
    hinge_z = 0.022
    _box(
        part,
        (0.190, 0.052, 0.008),
        (hinge_x, board_edge_y - 0.006, 0.006),
        mats["mesh"],
        f"{prefix}__hinge_mount_plate",
    )
    for index, dx in enumerate((-0.075, 0.075)):
        _box(
            part,
            (0.020, 0.014, 0.032),
            (hinge_x + dx, hinge_y, hinge_z - 0.014),
            mats["fitting"],
            f"{prefix}__hinge_post_{index}",
        )
        _cyl(
            part,
            _HINGE_R,
            0.020,
            (hinge_x + dx, hinge_y, hinge_z),
            mats["fitting"],
            f"{prefix}__hinge_boss_{index}",
            rpy=_X_AXIS_RPY,
        )
    sleeve = model.part(
        f"{prefix}__sleeve_board",
        meta={"role": "sleeve_board", "construction": "hinged sleeve board"},
    )
    # Source sleeve board projects across the main board's long axis, not as a
    # tiny parallel plank.  Its local +Y direction runs away from the hinge.
    sleeve_len = _clamp(r.board_length_m * 0.34, 0.260, 0.390)
    sleeve_w = _clamp(r.board_width_m * 0.30, 0.082, 0.118)
    steps = 9
    for index in range(steps):
        frac = (float(index) + 0.5) / float(steps)
        width = sleeve_w * (1.0 - 0.28 * frac)
        y = 0.046 + sleeve_len * frac
        _box(
            sleeve,
            (width, sleeve_len / float(steps) + 2.0 * _WELD, _PAD_T),
            (0.0, y, 0.030),
            mats["cover"],
            f"{prefix}__pad_{index}",
        )
        _box(
            sleeve,
            (width - 0.006, sleeve_len / float(steps) + 2.0 * _WELD, 0.010),
            (0.0, y, 0.030 - _PAD_T / 2.0 - 0.005 + _WELD),
            mats["mesh"],
            f"{prefix}__shell_{index}",
        )
        if r.cover_style != "plain" and index in (2, 5, 8):
            _box(
                sleeve,
                (width - 0.014, 0.0014, 0.0008),
                (0.0, y, 0.030 + _PAD_T / 2.0 + 0.0003),
                mats["seam"],
                f"{prefix}__cover_detail_{index}",
            )
    for index, dx in enumerate((-0.060, 0.060)):
        _bar_yz(
            sleeve,
            (dx, 0.0, 0.0),
            (dx * 0.72, 0.112, 0.024),
            0.008,
            0.008,
            mats["fitting"],
            f"{prefix}__bracket_arm_{index}",
        )
    _box(
        sleeve,
        (0.106, 0.068, 0.008),
        (0.0, 0.112, 0.021),
        mats["mesh"],
        f"{prefix}__mount_plate",
    )
    _cyl(
        sleeve,
        _HINGE_R,
        0.132,
        (0.0, 0.0, 0.0),
        mats["fitting"],
        f"{prefix}__hinge_rod",
        rpy=_X_AXIS_RPY,
    )
    _spin_joint(
        model,
        part,
        sleeve,
        name=f"{prefix}__sleeve_hinge",
        point=(hinge_x, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=_HINGE_R,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=6.0, velocity=2.0, lower=-1.20, upper=0.0),
        meta={"mechanism": "sleeve board hinge"},
    )


_SLEEVE_BUILDERS = {
    "plain_top": _sleeve_option_plain_top_build,
    "sleeve_board": _sleeve_option_sleeve_board_build,
}


_BOARD_BUILDERS = {
    "tapered_capsule": _board_style_tapered_capsule_build,
    "rect_slotted": _board_style_rect_slotted_build,
}


# --------------------------------------------------------------------------- #
# support_style candidates
# --------------------------------------------------------------------------- #
def _mount_z(r: ResolvedConfig) -> float:
    """z of the support mounting line under the board shell."""
    return -_PAD_T - _SHELL_T - 0.017


def _leg_station_y(r: ResolvedConfig, x: float) -> float:
    return max(_half_width(r, x) - 0.028, 0.030)


def _hinge_pads(board, r, mats, x: float, prefix: str, span: float | None = None) -> None:
    """Two bearing lugs just outboard of the hinge rod they carry."""
    span = _leg_station_y(r, x) if span is None else span
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            board.part,
            (0.034, 0.010, 0.026),
            (x, sign * (span + 0.013), _mount_z(r) + 0.011),
            mats["fitting"],
            f"{prefix}_pad_{index}",
        )


def _leg_frame_part(
    model,
    r,
    mats,
    name: str,
    *,
    length: float,
    top_span: float,
    foot_span: float,
    role: str = "leg",
):
    """One A-shaped leg frame: two rails, a foot bar and rubber feet."""
    part = model.part(name, meta={"role": role, "construction": "folding leg frame"})
    _cyl(
        part,
        _HINGE_R,
        2.0 * top_span + 0.020,
        (0.0, 0.0, 0.0),
        mats["tube"],
        "leg_pivot_rod",
        rpy=_Y_AXIS_RPY,
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _bar_yz(
            part,
            (0.0, sign * top_span, 0.0),
            (0.0, sign * foot_span, -length),
            _TUBE,
            _TUBE,
            mats["tube"],
            f"leg_rail_{index}",
        )
        _cyl(
            part,
            0.013,
            0.034,
            (0.0, sign * foot_span, -length - 0.004),
            mats["foot"],
            f"leg_foot_{index}",
            rpy=_Y_AXIS_RPY,
        )
    _bar_yz(
        part,
        (0.0, -foot_span, -length + 0.020),
        (0.0, foot_span, -length + 0.020),
        0.011,
        0.011,
        mats["tube"],
        "leg_foot_bar",
    )
    _bar_yz(
        part,
        (0.0, -(top_span + foot_span) / 2.0, -length * 0.50),
        (0.0, (top_span + foot_span) / 2.0, -length * 0.50),
        0.010,
        0.010,
        mats["tube"],
        "leg_cross_tie",
    )
    return part


def _brace_part(
    model, r, mats, name: str, *, length: float, span: float, rod_span: float | None = None
):
    """A lock brace: its rails run inboard of the rod that pins it."""
    part = model.part(name, meta={"role": "brace", "construction": "folding lock brace"})
    rod_span = span if rod_span is None else rod_span
    _cyl(
        part,
        0.0075,
        2.0 * rod_span + 0.020,
        (0.0, 0.0, 0.0),
        mats["tube"],
        "brace_pivot_rod",
        rpy=_Y_AXIS_RPY,
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _bar_yz(
            part,
            (0.0, sign * span, 0.0),
            (0.0, sign * span * 0.90, -length),
            0.010,
            0.010,
            mats["tube"],
            f"brace_rail_{index}",
        )
    _bar_yz(
        part,
        (0.0, -span * 0.86, -length + 0.016),
        (0.0, span * 0.86, -length + 0.016),
        0.009,
        0.009,
        mats["tube"],
        "brace_tie",
    )
    return part


def _hinge_leg(
    model, r, board, part, *, name: str, x: float, sign: float, fold: float, tilt: float
) -> str:
    fold = _clamp(math.pi / 2.0 - abs(tilt) - 0.12, 0.30, fold)
    return _spin_joint(
        model,
        board.part,
        part,
        name=name,
        point=(x, 0.0, _mount_z(r)),
        axis=(0.0, -sign, 0.0),
        radial=(math.sin(tilt) * sign, 0.0, -math.cos(tilt)),
        child_radial=(0.0, 0.0, -1.0),
        radius=_HINGE_R,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=18.0, velocity=2.2, lower=0.0, upper=fold),
        meta={"mechanism": "board support hinge", "positive_motion": "folds the support flat"},
    )


def _leg_pair(
    model, r, mats, board, *, candidate: str, length: float, brace_on_board: bool, tilt: float
) -> list[str]:
    joints: list[str] = []
    for index, sign in enumerate((-1.0, 1.0)):
        x = sign * r.station_x_m
        span = _leg_station_y(r, x)
        _hinge_pads(board, r, mats, x, f"support_style__{candidate}__station_{index}")
        leg = _leg_frame_part(
            model,
            r,
            mats,
            f"support_style__{candidate}__leg_{index}",
            length=length,
            top_span=span,
            foot_span=span + r.spread_m * 0.30,
        )
        joints.append(
            _hinge_leg(
                model,
                r,
                board,
                leg,
                name=f"support_style__{candidate}__leg_{index}__fold",
                x=x,
                sign=sign,
                fold=r.fold_rad,
                tilt=tilt * sign,
            )
        )
        # Source-visible pivot washers and a stamped height-lock quadrant make
        # the folding mechanism readable at side-view scale.
        for side_index, y_sign in enumerate((-1.0, 1.0)):
            _cyl(
                leg,
                _HINGE_R + 0.0035,
                0.004,
                (0.0, y_sign * (span + 0.003), 0.0),
                mats["fitting"],
                f"pivot_washer_{side_index}",
                rpy=_Y_AXIS_RPY,
            )
        if index == 0:
            tooth_count = 5
            _box(
                board.part,
                (0.088, 0.012, 0.036),
                (
                    x + sign * 0.048,
                    -span * 0.72,
                    _mount_z(r) + 0.010,
                ),
                mats["fitting"],
                f"support_style__{candidate}__height_rack",
                rpy=(0.0, -0.12 * sign, 0.0),
            )
            for tooth in range(tooth_count):
                _box(
                    board.part,
                    (0.009, 0.006, 0.010),
                    (
                        x + sign * (0.028 + 0.010 * float(tooth)),
                        -span * 0.72,
                        _mount_z(r) - 0.004,
                    ),
                    mats["fitting"],
                    f"support_style__{candidate}__height_tooth_{tooth}",
                    rpy=(0.0, -0.18 * sign, 0.0),
                )
        # A board-mounted brace hangs in the leg's fold corridor, so its reach is
        # capped by the board length as well as by the leg run.
        brace_len = min(length * 0.18, r.half_length_m * 0.22) if brace_on_board else length * 0.18
        foot_span = span + r.spread_m * 0.30
        brace_span = span * 0.66
        rod_span = brace_span
        brace = _brace_part(
            model,
            r,
            mats,
            f"support_style__{candidate}__brace_{index}",
            length=brace_len,
            span=brace_span,
            rod_span=rod_span,
        )
        if brace_on_board:
            # The brace hangs inboard of its leg station: the leg folds outward
            # along the board, so an outboard brace would sit in its corridor.
            brace_x = x - sign * r.half_length_m * 0.20
            _hinge_pads(
                board,
                r,
                mats,
                brace_x,
                f"support_style__{candidate}__brace_seat_{index}",
                span=brace_span,
            )
            joints.append(
                _spin_joint(
                    model,
                    board.part,
                    brace,
                    name=f"support_style__{candidate}__brace_{index}__fold",
                    point=(brace_x, 0.0, _mount_z(r)),
                    axis=(0.0, -sign, 0.0),
                    radial=(math.sin(tilt * 0.6) * sign, 0.0, -math.cos(tilt * 0.6)),
                    child_radial=(0.0, 0.0, -1.0),
                    radius=0.0075,
                    joint_type=ArticulationType.REVOLUTE,
                    limits=MotionLimits(
                        effort=6.0,
                        velocity=2.5,
                        lower=0.0,
                        upper=_clamp(math.pi / 2.0 - abs(tilt) * 0.6 - 0.12, 0.22, 0.26),
                    ),
                    meta={"mechanism": "lock brace hinge"},
                )
            )
        else:
            # A real bracket bar on the leg carries the brace pin in its own plane.
            rail_y = span + 0.66 * (foot_span - span)
            _bar_yz(
                leg,
                (0.0105, -rail_y, -length * 0.66 + 0.014),
                (0.0105, rail_y, -length * 0.66 + 0.014),
                0.012,
                0.012,
                mats["tube"],
                "brace_bracket",
            )
            joints.append(
                _spin_joint(
                    model,
                    leg,
                    brace,
                    name=f"support_style__{candidate}__brace_{index}__fold",
                    point=(0.0135, 0.0, -length * 0.66),
                    axis=(0.0, sign, 0.0),
                    radial=(0.0, 0.0, -1.0),
                    child_radial=(0.0, 0.0, -1.0),
                    radius=0.0075,
                    joint_type=ArticulationType.REVOLUTE,
                    limits=MotionLimits(effort=4.0, velocity=2.5, lower=-0.90, upper=0.90),
                    meta={"mechanism": "lock brace hinge"},
                )
            )
        if candidate == "floor_x_legs" and index == 0:
            _cyl(
                leg,
                0.012,
                2.0 * (span + r.spread_m * 0.18),
                (0.0, 0.0, -length * 0.50),
                mats["fitting"],
                "scissor_centre_pin",
                rpy=_Y_AXIS_RPY,
            )
    return joints


def _support_style_scissor_legs_build(model, r, mats, board) -> list[str]:
    """001 L176-L323: scissor leg frames whose braces hinge on the legs."""
    tilt = _clamp(math.atan(r.spread_ratio * 0.78), 0.28, 0.52)
    length = (r.support_height_m + _mount_z(r)) / math.cos(tilt)
    return _leg_pair(
        model,
        r,
        mats,
        board,
        candidate="scissor_legs",
        length=length,
        brace_on_board=False,
        tilt=tilt,
    )


def _support_style_floor_x_legs_build(model, r, mats, board) -> list[str]:
    """x_leg fork L257-L388: long crossed floor legs with board-mounted braces."""
    tilt = _clamp(math.atan(r.spread_ratio), 0.34, 0.62)
    length = (r.support_height_m + _mount_z(r)) / math.cos(tilt)
    return _leg_pair(
        model,
        r,
        mats,
        board,
        candidate="floor_x_legs",
        length=length,
        brace_on_board=True,
        tilt=tilt,
    )


def _support_style_short_tabletop_legs_build(model, r, mats, board) -> list[str]:
    """tabletop fork L255-L365: short legs that stand the board on a table."""
    tilt = _clamp(math.atan(r.spread_ratio * 0.76), 0.26, 0.50)
    length = (r.support_height_m + _mount_z(r)) / math.cos(tilt)
    return _leg_pair(
        model,
        r,
        mats,
        board,
        candidate="short_tabletop_legs",
        length=length,
        brace_on_board=True,
        tilt=tilt,
    )


def _support_style_telescoping_posts_build(model, r, mats, board) -> list[str]:
    """t_leg fork L245-L345: telescoping height posts with twist lock collars."""
    joints: list[str] = []
    outer_len = (r.support_height_m + _mount_z(r)) * 0.55
    travel = (r.support_height_m + _mount_z(r)) * 0.30
    for index, sign in enumerate((-1.0, 1.0)):
        x = sign * r.station_x_m
        span = _leg_station_y(r, x)
        _hinge_pads(board, r, mats, x, f"support_style__telescoping_posts__station_{index}")
        # The outer bracket tube is board geometry; the post slides inside it.
        _tube_ring(
            board.part,
            radius=0.0150,
            wall=0.0055,
            z=_mount_z(r) + 0.024 - outer_len / 2.0,
            height=outer_len,
            segments=10,
            x=x,
            material=mats["tube"],
            prefix=f"support_style__telescoping_posts__sleeve_{index}",
        )
        post = model.part(
            f"support_style__telescoping_posts__post_{index}",
            meta={"role": "leg", "construction": "telescoping height post"},
        )
        post_len = outer_len + travel + 0.030
        _cyl(post, 0.0120, post_len, (0.0, 0.0, -post_len / 2.0), mats["tube"], "post_tube")
        _bar_yz(
            post,
            (0.0, -span - r.spread_m * 0.30, -post_len + 0.014),
            (0.0, span + r.spread_m * 0.30, -post_len + 0.014),
            0.011,
            0.011,
            mats["tube"],
            "post_crossbar",
        )
        _box(
            post,
            (0.032, 0.032, 0.022),
            (0.0, 0.0, -post_len + 0.020),
            mats["fitting"],
            "post_base_gusset",
        )
        for marker in range(4):
            _cyl(
                post,
                0.0024,
                0.0016,
                (0.0121, 0.0, -outer_len * (0.32 + 0.13 * float(marker))),
                mats["fitting"],
                f"height_index_{marker}",
                rpy=_X_AXIS_RPY,
            )
        for foot, fsign in enumerate((-1.0, 1.0)):
            _cyl(
                post,
                0.013,
                0.014,
                (0.0, fsign * (span + r.spread_m * 0.30), -post_len + 0.008),
                mats["foot"],
                f"post_foot_{foot}",
            )
        name = f"support_style__telescoping_posts__post_{index}__extend"
        model.articulation(
            name,
            ArticulationType.PRISMATIC,
            parent=board.part,
            child=post,
            origin=Origin(xyz=(x, 0.0, _mount_z(r) + 0.004)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=40.0, velocity=0.15, lower=0.0, upper=travel),
            motion_properties=MotionProperties(damping=1.8, friction=0.9),
            meta={"mechanism": "board height adjustment"},
        )
        joints.append(name)
        collar = model.part(
            f"support_style__telescoping_posts__collar_{index}",
            meta={"role": "brace", "construction": "twist lock collar"},
        )
        _tube_ring(
            collar,
            radius=0.0165,
            wall=0.0075,
            z=0.0,
            height=0.024,
            segments=8,
            x=0.0,
            material=mats["fitting"],
            prefix="collar_body",
        )
        for lug in range(4):
            angle = 2.0 * math.pi * float(lug) / 4.0
            _box(
                collar,
                (0.010, 0.006, 0.020),
                (0.0205 * math.sin(angle), 0.0205 * math.cos(angle), 0.0),
                mats["fitting"],
                f"collar_lug_{lug}",
                rpy=(0.0, 0.0, -angle),
            )
        _box(
            collar,
            (0.044, 0.010, 0.016),
            (0.036, 0.0, 0.0),
            mats["fitting"],
            "collar_release_lever",
        )
        joints.append(
            _spin_joint(
                model,
                post,
                collar,
                name=f"support_style__telescoping_posts__collar_{index}__twist",
                point=(0.0, 0.0, -outer_len - 0.020),
                axis=(0.0, 0.0, 1.0),
                radial=(1.0, 0.0, 0.0),
                radius=0.0120,
                joint_type=ArticulationType.REVOLUTE,
                limits=MotionLimits(effort=4.0, velocity=2.0, lower=-1.2, upper=1.2),
                meta={"mechanism": "height lock collar"},
            )
        )
    return joints


def _support_style_wall_bracket_build(model, r, mats, board) -> list[str]:
    """wall fork L233-L321 + L419-L510: a wall plate and a prop arm."""
    hinge_x = -r.half_length_m + 0.030
    span = _leg_station_y(r, hinge_x)
    _hinge_pads(board, r, mats, hinge_x, "support_style__wall_bracket__station")
    bracket = model.part(
        "support_style__wall_bracket__bracket",
        meta={"role": "leg", "construction": "wall mounting bracket"},
    )
    height = r.support_height_m
    _box(
        bracket,
        (0.012, 2.0 * span + 0.040, height),
        (-0.012, 0.0, -height / 2.0 - 0.004),
        mats["mesh"],
        "bracket_plate",
    )
    _cyl(
        bracket,
        _HINGE_R,
        2.0 * span + 0.020,
        (0.0, 0.0, 0.0),
        mats["tube"],
        "bracket_pivot_rod",
        rpy=_Y_AXIS_RPY,
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            bracket,
            (0.030, 0.014, 0.052),
            (0.006, sign * (span - 0.014), -0.020),
            mats["fitting"],
            f"bracket_cheek_{index}",
        )
        for hole in range(2):
            _cyl(
                bracket,
                0.0055,
                0.014,
                (-0.010, sign * (span + 0.006), -height * (0.30 + 0.45 * float(hole))),
                mats["fitting"],
                f"bracket_anchor_{index}_{hole}",
                rpy=_X_AXIS_RPY,
            )
    fold = _spin_joint(
        model,
        board.part,
        bracket,
        name="support_style__wall_bracket__fold",
        point=(hinge_x, 0.0, _mount_z(r)),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        child_radial=(0.0, 0.0, -1.0),
        radius=_HINGE_R,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=25.0, velocity=1.5, lower=0.0, upper=0.40),
        meta={"mechanism": "board support hinge", "positive_motion": "folds the board down"},
    )
    arm = model.part(
        "support_style__wall_bracket__support_arm",
        meta={"role": "brace", "construction": "fold-down prop arm"},
    )
    reach = r.half_length_m * 0.55
    _cyl(
        arm,
        0.0075,
        2.0 * span * 0.70 + 0.020,
        (0.0, 0.0, 0.0),
        mats["tube"],
        "arm_pivot_rod",
        rpy=_Y_AXIS_RPY,
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _bar_xz(
            arm,
            (0.0, sign * span * 0.70, 0.0),
            (-reach * 0.80, sign * span * 0.70, -0.052),
            0.011,
            0.011,
            mats["tube"],
            f"arm_rail_{index}",
        )
    _bar_yz(
        arm,
        (-reach * 0.62, -span * 0.70, -0.040),
        (-reach * 0.62, span * 0.70, -0.040),
        0.010,
        0.010,
        mats["tube"],
        "arm_tie",
    )
    _hinge_pads(
        board,
        r,
        mats,
        hinge_x + reach,
        "support_style__wall_bracket__landing",
        span=span * 0.70,
    )
    prop = _spin_joint(
        model,
        board.part,
        arm,
        name="support_style__wall_bracket__prop",
        point=(hinge_x + reach, 0.0, _mount_z(r)),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0075,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=8.0, velocity=2.0, lower=-0.50, upper=0.0),
        meta={"mechanism": "prop arm hinge"},
    )
    return [fold, prop]


_SUPPORT_BUILDERS = {
    "scissor_legs": _support_style_scissor_legs_build,
    "floor_x_legs": _support_style_floor_x_legs_build,
    "short_tabletop_legs": _support_style_short_tabletop_legs_build,
    "telescoping_posts": _support_style_telescoping_posts_build,
    "wall_bracket": _support_style_wall_bracket_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_ironing_board2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_ironing_board2",
            "identified_object": "domestic ironing board",
            "slot_choices": slot_choices_for_config(r),
            "cover_style": r.cover_style,
            "source_layout": "a padded ironing top over a folding or adjustable support",
        },
    )
    mats = _materials(model, r)
    board = _BOARD_BUILDERS[r.board_style](model, r, mats)
    _SLEEVE_BUILDERS[r.sleeve_option](model, r, mats, board)
    _SUPPORT_BUILDERS[r.support_style](model, r, mats, board)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_pictureX_0611_ironing_board2_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    boards = _parts_by_role(model, "board")
    legs = _parts_by_role(model, "leg")
    braces = _parts_by_role(model, "brace")

    ctx.check(
        "category_anchor: one padded ironing top",
        len(boards) == 1,
        details=f"boards={[part.name for part in boards]}",
    )
    expected_legs = 1 if r.support_style == "wall_bracket" else 2
    ctx.check(
        "category_anchor: the board stands on its own support",
        len(legs) == expected_legs,
        details=f"legs={[part.name for part in legs]} expected={expected_legs}",
    )
    ctx.check(
        "category_anchor: the support carries a brace or lock",
        len(braces) == expected_legs,
        details=f"braces={[part.name for part in braces]}",
    )

    supports = [
        joint
        for joint in model.articulations
        if joint.meta.get("mechanism") in {"board support hinge", "board height adjustment"}
    ]
    ctx.check(
        "category_anchor: the support really folds or adjusts away from the board",
        len(supports) == expected_legs,
        details=f"support joints={[joint.name for joint in supports]}",
    )

    for joint in supports:
        child = model.get_part(joint.child)
        rest = ctx.part_world_aabb(child)
        with ctx.pose({joint: joint.motion_limits.upper}):
            folded = ctx.part_world_aabb(child)
        moved = None
        if rest is not None and folded is not None:
            moved = max(
                abs(
                    (folded[0][index] + folded[1][index]) / 2.0
                    - (rest[0][index] + rest[1][index]) / 2.0
                )
                for index in range(3)
            )
        ctx.check(
            f"{joint.name} really moves the support",
            moved is not None and moved > 0.008,
            details=f"rest={rest}, folded={folded}, moved={moved}",
        )

    sleeves = _parts_by_role(model, "sleeve_board")
    ctx.check(
        "category_anchor: the sleeve option matches the selected top",
        len(sleeves) == (1 if r.sleeve_option == "sleeve_board" else 0),
        details=f"sleeve_option={r.sleeve_option}, sleeves={[p.name for p in sleeves]}",
    )
    if r.sleeve_option == "sleeve_board":
        hinge = next(
            joint
            for joint in model.articulations
            if joint.meta.get("mechanism") == "sleeve board hinge"
        )
        ctx.check(
            "category_anchor: the sleeve board swings on its own hinge",
            len(sleeves) == 1 and hinge.articulation_type == ArticulationType.REVOLUTE,
            details=f"sleeves={[part.name for part in sleeves]}, hinge={hinge.name}",
        )

    ctx.check(
        "the top narrows from the heel toward the nose",
        r.nose_width_m <= r.board_width_m,
        details=f"width={r.board_width_m:.4f}, nose={r.nose_width_m:.4f}",
    )
    aspect = r.board_length_m / r.board_width_m
    ctx.check(
        "the board keeps a source-like usable planform",
        1.50 <= aspect <= 4.20,
        details=f"length/width aspect={aspect:.3f}",
    )
    ctx.check(
        "the support reaches a real working height",
        r.support_height_m > 0.15,
        details=f"support height={r.support_height_m:.4f}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "longest_widest_board_scissor",
        {
            "board_style": "tapered_capsule",
            "support_style": "scissor_legs",
            "board_length_m": 1.250,
            "board_width_m": 0.460,
            "board_height_m": 0.950,
            "taper_ratio": 0.74,
            "spread_ratio": 0.72,
        },
        reason="the longest board on the widest-spread scissor legs",
    ),
    corner_case(
        "shortest_narrowest_board_wall",
        {
            "board_style": "rect_slotted",
            "support_style": "wall_bracket",
            "board_length_m": 0.620,
            "board_width_m": 0.260,
            "board_height_m": 0.600,
            "taper_ratio": 0.34,
            "spread_ratio": 0.34,
        },
        reason="the smallest board folding down off a wall bracket",
    ),
    corner_case(
        "sleeve_board_on_telescoping_posts",
        {
            "board_style": "tapered_capsule",
            "sleeve_option": "sleeve_board",
            "support_style": "telescoping_posts",
            "board_length_m": 1.250,
            "board_width_m": 0.400,
            "board_height_m": 0.950,
            "taper_ratio": 0.34,
            "spread_ratio": 0.72,
        },
        reason="the sleeve board swings beside the tallest telescoping posts",
    ),
    corner_case(
        "tabletop_legs_max_spread",
        {
            "board_style": "tapered_capsule",
            "support_style": "short_tabletop_legs",
            "board_length_m": 0.620,
            "board_width_m": 0.400,
            "board_height_m": 0.600,
            "taper_ratio": 0.74,
            "spread_ratio": 0.72,
        },
        reason="the shortest legs at the widest spread under a stubby wide board",
    ),
    corner_case(
        "floor_x_legs_narrow_nose",
        {
            "board_style": "tapered_capsule",
            "sleeve_option": "sleeve_board",
            "support_style": "floor_x_legs",
            "board_length_m": 1.100,
            "board_width_m": 0.270,
            "board_height_m": 0.950,
            "taper_ratio": 0.34,
            "spread_ratio": 0.34,
        },
        reason="board-mounted braces on the narrowest top",
    ),
    corner_case(
        "rect_pan_telescoping_min",
        {
            "board_style": "rect_slotted",
            "support_style": "telescoping_posts",
            "board_length_m": 0.620,
            "board_width_m": 0.260,
            "board_height_m": 0.600,
            "taper_ratio": 0.74,
            "spread_ratio": 0.34,
        },
        reason="the shortest telescoping stroke under a straight pan",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_ironing_board2",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_ironing_board2_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
