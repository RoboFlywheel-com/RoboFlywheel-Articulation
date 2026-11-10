# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'drum_pedal_with_beater_and_spring_return' template.

Rebuilt from the ``pictureX/0611/drum_pedal_with_beater_and_spring_return``
origin record and its eleven accepted forks, listed in
``articraft_template_authoring/source_maps/pictureX_0611_drum_pedal_with_beater_and_spring_return.md``.

Category identity: one floor frame carrying a hinged footboard, a drive
coupling from the board up to a rocker shaft and cam, a beater swinging off that
shaft, a hoop clamp at the front of the frame and a return spring.  Seven
independent structural axes:

* ``frame_style``   — one cast side post, or twin uprights on an open rail.
* ``board_style``   — a short hinged plate, a longboard, or a split heel plate
  plus toe board on two hinges.
* ``drive_style``   — single chain, double chain, nylon strap, or a rigid
  direct link hinged on the board.
* ``cam_style``     — a concentric round cam, an offset accelerator profile, or a
  135-degree D-shaped sector that the drive member wraps.
* ``beater_style``  — a one-piece beater, a beater with a reversible head, or a
  prismatic height carriage carrying the beater.
* ``clamp_style``   — a screw hoop clamp or a three-part over-centre toggle.
* ``spring_style``  — a coil return with a tension adjuster, or a leaf spring.

Coordinate frame: the floor is z = 0, +X points forward toward the drum hoop,
and the rocker shaft lies on the +Y axis at x = 0.  The footboard hinges at the
heel behind the frame and rises toward the shaft.

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
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    register_interface_mate,
)

FrameStyle = Literal["cast_post", "twin_post_rail"]
BoardStyle = Literal["hinged_plate", "longboard", "split_heel"]
DriveStyle = Literal["single_chain", "double_chain", "strap", "direct_link"]
CamStyle = Literal["round_cam", "eccentric_accel", "d_sector"]
BeaterStyle = Literal["fixed_head", "reversible_head", "height_carriage"]
ClampStyle = Literal["screw_clamp", "overcenter_toggle"]
SpringStyle = Literal["coil_return", "leaf_return"]

FRAME_STYLES: tuple[FrameStyle, ...] = ("cast_post", "twin_post_rail")
BOARD_STYLES: tuple[BoardStyle, ...] = ("hinged_plate", "longboard", "split_heel")
DRIVE_STYLES: tuple[DriveStyle, ...] = ("single_chain", "double_chain", "strap", "direct_link")
CAM_STYLES: tuple[CamStyle, ...] = ("round_cam", "eccentric_accel", "d_sector")
BEATER_STYLES: tuple[BeaterStyle, ...] = ("fixed_head", "reversible_head", "height_carriage")
CLAMP_STYLES: tuple[ClampStyle, ...] = ("screw_clamp", "overcenter_toggle")
SPRING_STYLES: tuple[SpringStyle, ...] = ("coil_return", "leaf_return")

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("frame_style", FRAME_STYLES),
        component_slot("board_style", BOARD_STYLES),
        component_slot("drive_style", DRIVE_STYLES),
        component_slot("cam_style", CAM_STYLES),
        component_slot("beater_style", BEATER_STYLES),
        component_slot("clamp_style", CLAMP_STYLES),
        component_slot("spring_style", SPRING_STYLES),
    )
)

_BOARD_LENGTH_RANGE = (0.200, 0.340)
_BOARD_WIDTH_RANGE = (0.085, 0.135)
_SHAFT_HEIGHT_RANGE = (0.110, 0.200)
_BEATER_LENGTH_RANGE = (0.150, 0.260)
_FRAME_MARGIN_RANGE = (0.014, 0.040)

_BASE_T = 0.010  # base plate thickness
_HINGE_Z = 0.026  # heel hinge height above the floor
_HINGE_R = 0.0075
_POST_T = 0.014  # upright thickness in x
_BOARD_T = 0.008
_CAM_W = 0.016
_WELD = 0.0008  # every fused feature keeps at least this much real overlap
_CLEAR = 0.0015
_SIDE_GAP = 0.014  # clear width between the board edge and a frame upright
_BEATER_Y = _CAM_W / 2.0 + 0.012  # the beater rides the shaft beside the cam disc
_HUB_HALF = _BEATER_Y + 0.008  # half length of the cam hub on the rocker shaft


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    frame_style: FrameStyle = "cast_post"
    board_style: BoardStyle = "hinged_plate"
    drive_style: DriveStyle = "single_chain"
    cam_style: CamStyle = "round_cam"
    beater_style: BeaterStyle = "fixed_head"
    clamp_style: ClampStyle = "screw_clamp"
    spring_style: SpringStyle = "coil_return"
    board_length_m: float | None = None
    board_width_m: float | None = None
    shaft_height_m: float | None = None
    beater_length_m: float | None = None
    frame_margin_m: float | None = None
    name: str = "pictureX_0611_drum_pedal_with_beater_and_spring_return"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_style: FrameStyle
    board_style: BoardStyle
    drive_style: DriveStyle
    cam_style: CamStyle
    beater_style: BeaterStyle
    clamp_style: ClampStyle
    spring_style: SpringStyle
    board_length_m: float
    board_width_m: float
    shaft_height_m: float
    beater_length_m: float
    frame_margin_m: float
    frame_width_m: float
    # derived
    heel_x_m: float
    base_length_m: float
    base_front_x_m: float
    cam_radius_m: float
    board_tilt_rad: float
    board_press_rad: float
    post_y_m: float
    clamp_x_m: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x0D2AB1)
    return Config(
        frame_style=choices["frame_style"],
        board_style=choices["board_style"],
        drive_style=choices["drive_style"],
        cam_style=choices["cam_style"],
        beater_style=choices["beater_style"],
        clamp_style=choices["clamp_style"],
        spring_style=choices["spring_style"],
        board_length_m=round(rng.uniform(*_BOARD_LENGTH_RANGE), 5),
        board_width_m=round(rng.uniform(*_BOARD_WIDTH_RANGE), 5),
        shaft_height_m=round(rng.uniform(*_SHAFT_HEIGHT_RANGE), 5),
        beater_length_m=round(rng.uniform(*_BEATER_LENGTH_RANGE), 5),
        frame_margin_m=round(rng.uniform(*_FRAME_MARGIN_RANGE), 5),
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "frame_style": config.frame_style,
            "board_style": config.board_style,
            "drive_style": config.drive_style,
            "cam_style": config.cam_style,
            "beater_style": config.beater_style,
            "clamp_style": config.clamp_style,
            "spring_style": config.spring_style,
        }
    )
    board_len = 0.262 if config.board_length_m is None else float(config.board_length_m)
    board_w = 0.105 if config.board_width_m is None else float(config.board_width_m)
    shaft_h = 0.150 if config.shaft_height_m is None else float(config.shaft_height_m)
    beater_len = 0.205 if config.beater_length_m is None else float(config.beater_length_m)
    margin = 0.020 if config.frame_margin_m is None else float(config.frame_margin_m)
    _range_check("board_length_m", board_len, _BOARD_LENGTH_RANGE)
    _range_check("board_width_m", board_w, _BOARD_WIDTH_RANGE)
    _range_check("shaft_height_m", shaft_h, _SHAFT_HEIGHT_RANGE)
    _range_check("beater_length_m", beater_len, _BEATER_LENGTH_RANGE)
    _range_check("frame_margin_m", margin, _FRAME_MARGIN_RANGE)

    # Host capacity: the frame is derived from the board it must clear, so a
    # wider board always widens the frame instead of cutting into it.
    frame_w = board_w + 2.0 * (margin + 0.010)
    heel_x = -(board_len + 0.020)
    base_front = 0.070
    base_length = base_front - heel_x + 0.030
    cam_radius = _clamp(shaft_h * 0.21, 0.024, 0.040)
    # The board rises from the heel hinge toward the shaft; the rise is a real
    # fraction of the shaft height, so a tall pedal gets a steeper board.
    board_tilt = math.asin(_clamp(0.30 * shaft_h / board_len, 0.08, 0.45))
    board_press = _clamp(board_tilt - 0.04, 0.05, 0.34)
    return ResolvedConfig(
        frame_style=config.frame_style,
        board_style=config.board_style,
        drive_style=config.drive_style,
        cam_style=config.cam_style,
        beater_style=config.beater_style,
        clamp_style=config.clamp_style,
        spring_style=config.spring_style,
        board_length_m=board_len,
        board_width_m=board_w,
        shaft_height_m=shaft_h,
        beater_length_m=beater_len,
        frame_margin_m=margin,
        frame_width_m=frame_w,
        heel_x_m=heel_x,
        base_length_m=base_length,
        base_front_x_m=base_front,
        cam_radius_m=cam_radius,
        board_tilt_rad=board_tilt,
        board_press_rad=board_press,
        post_y_m=frame_w / 2.0 - 0.008,
        clamp_x_m=base_front - 0.014,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("frame_style", config.frame_style),
        ("board_style", config.board_style),
        ("drive_style", config.drive_style),
        ("cam_style", config.cam_style),
        ("beater_style", config.beater_style),
        ("clamp_style", config.clamp_style),
        ("spring_style", config.spring_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("black_cast", rgba=(0.10, 0.10, 0.11, 1.0))
    model.material("chrome", rgba=(0.78, 0.80, 0.82, 1.0))
    model.material("brushed_steel", rgba=(0.58, 0.60, 0.62, 1.0))
    model.material("felt_tan", rgba=(0.72, 0.60, 0.40, 1.0))
    model.material("rubber_black", rgba=(0.05, 0.05, 0.05, 1.0))
    return {
        "cast": "black_cast",
        "chrome": "chrome",
        "steel": "brushed_steel",
        "felt": "felt_tan",
        "rubber": "rubber_black",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.blackened_gunmetal")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.chrome_polished",
    )


def _ball(part, radius, xyz, material: str, name: str) -> None:
    part.visual(Sphere(radius=radius), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.generic_plain")


_Y_AXIS_RPY = (math.pi / 2.0, 0.0, 0.0)
_X_AXIS_RPY = (0.0, math.pi / 2.0, 0.0)


def _knurled(part, radius, length, xyz, mats, name: str, rpy, bands: int = 12) -> None:
    _cyl(part, radius, length, xyz, mats["chrome"], name, rpy=rpy)
    for index in range(bands):
        angle = 2.0 * math.pi * float(index) / float(bands)
        local = (radius * math.cos(angle), radius * math.sin(angle))
        if rpy == _X_AXIS_RPY:
            offset = (xyz[0], xyz[1] + local[0], xyz[2] + local[1])
        elif rpy == _Y_AXIS_RPY:
            offset = (xyz[0] + local[0], xyz[1], xyz[2] + local[1])
        else:
            offset = (xyz[0] + local[0], xyz[1] + local[1], xyz[2])
        _cyl(
            part, radius * 0.11, length * 0.9, offset, mats["steel"], f"{name}_rib_{index}", rpy=rpy
        )


def _bar(part, mats, p0, p1, thickness, width, material, name) -> None:
    """One straight bar in the XZ plane between two points of the part frame."""
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
        motion_properties=MotionProperties(damping=1.2, friction=0.6),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)
    return name


# --------------------------------------------------------------------------- #
# frame_style candidates
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Frame:
    part: object
    shaft_point: tuple[float, float, float]
    heel_point: tuple[float, float, float]
    clamp_point: tuple[float, float, float]
    spring_y: float


def _base_plate(part, r: ResolvedConfig, mats) -> None:
    _box(
        part,
        (r.base_length_m, r.frame_width_m, _BASE_T),
        (r.heel_x_m - 0.020 + r.base_length_m / 2.0, 0.0, _BASE_T / 2.0),
        mats["cast"],
        "base_plate",
    )
    for index, (bx, by) in enumerate(
        (
            (r.heel_x_m - 0.008, -r.post_y_m),
            (r.heel_x_m - 0.008, r.post_y_m),
            (r.base_front_x_m - 0.010, -r.post_y_m),
            (r.base_front_x_m - 0.010, r.post_y_m),
        )
    ):
        _cyl(part, 0.011, 0.008, (bx, by, 0.002), mats["rubber"], f"foot_pad_{index}")
    _hinge_clevis(part, r, mats, r.heel_x_m, _HINGE_Z, "heel")


_CLAMP_CHEEK_Y = 0.026


def _clamp_clevis(part, r: ResolvedConfig, mats) -> None:
    """The hoop-clamp lever swings between two cheeks on its own stub pins."""
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.048, 0.012, 0.030),
            (r.clamp_x_m - 0.006, sign * _CLAMP_CHEEK_Y, 0.017),
            mats["cast"],
            f"clamp_cheek_{index}",
        )
        _cyl(
            part,
            0.0050,
            0.012,
            (r.clamp_x_m, sign * (_CLAMP_CHEEK_Y - 0.004), 0.026),
            mats["chrome"],
            f"clamp_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    _box(
        part,
        (0.048, 2.0 * _CLAMP_CHEEK_Y + 0.012, 0.012),
        (r.clamp_x_m - 0.006, 0.0, 0.008),
        mats["cast"],
        "clamp_tie",
    )


def _hinge_clevis(part, r: ResolvedConfig, mats, x: float, z: float, tag: str) -> None:
    """A two-cheek clevis with stub pins, so the board eye runs in real clearance."""
    inner = r.board_width_m / 2.0 + 0.0025
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.030, 0.010, z + 0.008),
            (x, sign * (inner + 0.005), (z + 0.008) / 2.0),
            mats["cast"],
            f"{tag}_cheek_{index}",
        )
        _cyl(
            part,
            _HINGE_R,
            0.012,
            (x, sign * (inner + 0.0005), z),
            mats["chrome"],
            f"{tag}_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    # The cross tie stays below the hinge bore so the board can swing through.
    _box(
        part,
        (0.030, 2.0 * inner + 0.020, 0.012),
        (x, 0.0, 0.006),
        mats["cast"],
        f"{tag}_tie",
    )


def _shaft_hardware(part, r: ResolvedConfig, mats) -> None:
    # The shaft is journalled either side of the cam hub, never through it.
    stub = r.post_y_m + 0.010 - _HUB_HALF
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            0.0075,
            stub,
            (0.0, sign * (_HUB_HALF + stub / 2.0 + 0.0005), r.shaft_height_m),
            mats["chrome"],
            f"rocker_shaft_{index}",
            rpy=_Y_AXIS_RPY,
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            0.0140,
            0.014,
            (0.0, sign * r.post_y_m, r.shaft_height_m),
            mats["cast"],
            f"bearing_boss_{index}",
            rpy=_Y_AXIS_RPY,
        )


def _frame_style_cast_post_build(model, r: ResolvedConfig, mats) -> _Frame:
    """001 L112-L248: one cast side post closing the frame in a single body."""
    part = model.part(
        "frame_style__cast_post__frame",
        meta={"role": "frame", "construction": "single cast side post"},
    )
    _base_plate(part, r, mats)
    for index, sign in enumerate((-1.0, 1.0)):
        # A tall cast cheek that tapers from the base up to the bearing.
        steps = 4
        for step in range(steps):
            lo = float(step) / float(steps)
            hi = float(step + 1) / float(steps)
            _box(
                part,
                (
                    0.062 - 0.030 * (lo + hi) / 2.0,
                    _POST_T,
                    r.shaft_height_m * (hi - lo) + 2.0 * _WELD,
                ),
                (0.006, sign * r.post_y_m, r.shaft_height_m * (lo + hi) / 2.0),
                mats["cast"],
                f"cast_cheek_{index}_{step}",
            )
    _box(
        part,
        (0.040, r.frame_width_m - 2.0 * _POST_T, 0.020),
        (0.006, 0.0, 0.030),
        mats["cast"],
        "cast_web",
    )
    _shaft_hardware(part, r, mats)
    _clamp_clevis(part, r, mats)
    return _Frame(
        part=part,
        shaft_point=(0.0, 0.0, r.shaft_height_m),
        heel_point=(r.heel_x_m, 0.0, _HINGE_Z),
        clamp_point=(r.clamp_x_m, 0.0, 0.026),
        spring_y=r.post_y_m + _POST_T / 2.0 + 0.016,
    )


def _frame_style_twin_post_rail_build(model, r: ResolvedConfig, mats) -> _Frame:
    """twin_post fork L113-L278: two slim uprights tied by an open cross rail."""
    part = model.part(
        "frame_style__twin_post_rail__frame",
        meta={"role": "frame", "construction": "twin uprights on an open rail"},
    )
    _base_plate(part, r, mats)
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            0.0090,
            r.shaft_height_m + 0.010,
            (0.006, sign * r.post_y_m, (r.shaft_height_m + 0.010) / 2.0),
            mats["chrome"],
            f"upright_tube_{index}",
        )
        _box(
            part,
            (0.030, _POST_T, 0.028),
            (0.006, sign * r.post_y_m, 0.016),
            mats["cast"],
            f"upright_shoe_{index}",
        )
    # The open cross rail replaces the closed casting.
    _box(
        part,
        (0.020, r.frame_width_m - 0.012, 0.014),
        (0.006, 0.0, r.shaft_height_m * 0.62),
        mats["cast"],
        "cross_rail",
    )
    _box(
        part,
        (0.014, 0.014, r.shaft_height_m * 0.40),
        (0.006, 0.0, r.shaft_height_m * 0.62 - r.shaft_height_m * 0.20),
        mats["cast"],
        "rail_drop",
    )
    _shaft_hardware(part, r, mats)
    _clamp_clevis(part, r, mats)
    _bar(
        part,
        mats,
        (r.base_front_x_m - 0.020, 0.0, 0.014),
        (0.006, 0.0, 0.030),
        0.012,
        r.frame_width_m - 0.030,
        mats["cast"],
        "front_tie",
    )
    return _Frame(
        part=part,
        shaft_point=(0.0, 0.0, r.shaft_height_m),
        heel_point=(r.heel_x_m, 0.0, _HINGE_Z),
        clamp_point=(r.clamp_x_m, 0.0, 0.026),
        spring_y=r.post_y_m + 0.0090 + 0.016,
    )


_FRAME_BUILDERS = {
    "cast_post": _frame_style_cast_post_build,
    "twin_post_rail": _frame_style_twin_post_rail_build,
}


# --------------------------------------------------------------------------- #
# board_style candidates
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Board:
    part: object  # the part the drive coupling hangs from
    drive_point: tuple[float, float, float]  # in that part's own frame
    hinge_joint: str
    parts: tuple[object, ...]


_DRIVE_LIFT = 0.014


def _drive_station(r: ResolvedConfig, hinge_xz, length: float) -> float:
    """How far along a board section the drive lug can sit.

    Host capacity: the lug must stay far enough from the rocker shaft that the
    coupling has a real run, so a board whose toe crowds the shaft moves its
    station back instead of burying the lug in the cam.
    """
    need = _drive_anchor_radius(r) + 0.090
    tilt = r.board_tilt_rad
    ratio = 0.92
    while ratio > 0.45:
        bx = length * ratio
        bz = _BOARD_T / 2.0 + _DRIVE_LIFT
        world_x = hinge_xz[0] + bx * math.cos(tilt) - bz * math.sin(tilt)
        world_z = hinge_xz[1] + bx * math.sin(tilt) + bz * math.cos(tilt)
        if math.hypot(world_x, world_z - r.shaft_height_m) >= need:
            return ratio
        ratio -= 0.04
    return 0.45


def _drive_bracket(part, r: ResolvedConfig, mats, x: float, prefix: str) -> None:
    """The lug that carries the drive coupling above the board face."""
    _box(
        part,
        (0.018, 0.026, _DRIVE_LIFT + _BOARD_T),
        (x, 0.0, _DRIVE_LIFT / 2.0),
        mats["cast"],
        f"{prefix}_drive_lug",
    )


def _board_plate(part, r: ResolvedConfig, mats, *, length: float, prefix: str) -> None:
    """A ribbed footboard plate lying along the part's +X axis."""
    _box(
        part,
        (length, r.board_width_m, _BOARD_T),
        (length / 2.0, 0.0, 0.0),
        mats["chrome"],
        f"{prefix}_plate",
    )
    ribs = max(4, int(length / 0.038))
    for index in range(ribs):
        x = length * (0.10 + 0.80 * float(index) / float(max(ribs - 1, 1)))
        _box(
            part,
            (0.008, r.board_width_m - 0.016, 0.0034),
            (x, 0.0, _BOARD_T / 2.0 + 0.0009),
            mats["steel"],
            f"{prefix}_rib_{index}",
        )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (length, 0.006, _BOARD_T + 0.005),
            (length / 2.0, sign * (r.board_width_m / 2.0 - 0.003), 0.0),
            mats["steel"],
            f"{prefix}_edge_{index}",
        )


def _hinge_board(model, r, frame: _Frame, part, name: str, *, effort: float, press: float) -> str:
    return _spin_joint(
        model,
        frame.part,
        part,
        name=name,
        point=frame.heel_point,
        axis=(0.0, -1.0, 0.0),
        radial=(math.cos(r.board_tilt_rad), 0.0, math.sin(r.board_tilt_rad)),
        child_radial=(1.0, 0.0, 0.0),
        radius=_HINGE_R,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=effort, velocity=7.0, lower=-press, upper=0.05),
        meta={"mechanism": "footboard hinge", "positive_motion": "the toe lifts back up"},
    )


def _board_eye(part, r, mats, prefix: str) -> None:
    _cyl(
        part,
        _HINGE_R + 0.0035,
        r.board_width_m - 0.010,
        (0.0, 0.0, 0.0),
        mats["chrome"],
        f"{prefix}_hinge_eye",
        rpy=_Y_AXIS_RPY,
    )


def _board_style_hinged_plate_build(model, r, mats, frame: _Frame) -> _Board:
    """001 L249-L309: a short ribbed plate hinged at the heel block."""
    part = model.part(
        "board_style__hinged_plate__footboard",
        meta={"role": "footboard", "section": "toe"},
    )
    _board_eye(part, r, mats, "board")
    station = r.board_length_m * _drive_station(r, (r.heel_x_m, _HINGE_Z), r.board_length_m)
    # The plate ends just past its drive station so the coupling keeps clearance.
    _board_plate(part, r, mats, length=min(r.board_length_m, station + 0.016), prefix="board")
    _drive_bracket(part, r, mats, station, "board")
    joint = _hinge_board(
        model,
        r,
        frame,
        part,
        "board_style__hinged_plate__hinge",
        effort=420.0,
        press=r.board_press_rad,
    )
    return _Board(
        part=part,
        drive_point=(station, 0.0, _BOARD_T / 2.0 + _DRIVE_LIFT),
        hinge_joint=joint,
        parts=(part,),
    )


def _board_style_longboard_build(model, r, mats, frame: _Frame) -> _Board:
    """longboard fork L242-L315: one continuous board reaching past the heel."""
    part = model.part(
        "board_style__longboard__footboard",
        meta={"role": "footboard", "section": "long"},
    )
    _board_eye(part, r, mats, "board")
    length = r.board_length_m
    station = length * _drive_station(r, (r.heel_x_m, _HINGE_Z), length)
    _board_plate(part, r, mats, length=min(length, station + 0.016), prefix="board")
    # The long board continues behind the hinge as one plate.
    tail = 0.070
    _box(
        part,
        (tail, r.board_width_m, _BOARD_T),
        (-tail / 2.0, 0.0, 0.0),
        mats["chrome"],
        "board_tail",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            part,
            (tail, 0.006, _BOARD_T + 0.005),
            (-tail / 2.0, sign * (r.board_width_m / 2.0 - 0.003), 0.0),
            mats["steel"],
            f"board_tail_edge_{index}",
        )
    _drive_bracket(part, r, mats, station, "board")
    joint = _hinge_board(
        model,
        r,
        frame,
        part,
        "board_style__longboard__hinge",
        effort=430.0,
        press=r.board_press_rad,
    )
    return _Board(
        part=part,
        drive_point=(station, 0.0, _BOARD_T / 2.0 + _DRIVE_LIFT),
        hinge_joint=joint,
        parts=(part,),
    )


def _board_style_split_heel_build(model, r, mats, frame: _Frame) -> _Board:
    """split fork L301-L417: an independently hinged heel plate and toe board."""
    heel = model.part(
        "board_style__split_heel__heel_plate",
        meta={"role": "footboard", "section": "heel"},
    )
    _board_eye(heel, r, mats, "heel")
    heel_len = r.board_length_m * 0.34
    _board_plate(heel, r, mats, length=heel_len, prefix="heel")
    _hinge_board(
        model,
        r,
        frame,
        heel,
        "board_style__split_heel__heel_hinge",
        effort=280.0,
        press=r.board_press_rad * 0.55,
    )
    toe = model.part(
        "board_style__split_heel__toe_board",
        meta={"role": "footboard", "section": "toe"},
    )
    toe_len = r.board_length_m - heel_len - 0.012
    _board_eye(toe, r, mats, "toe")

    # The toe board hinges on its own pin further forward on the heel block.
    toe_hinge = (
        r.heel_x_m + (heel_len + 0.010) * math.cos(r.board_tilt_rad),
        0.0,
        _HINGE_Z + (heel_len + 0.010) * math.sin(r.board_tilt_rad),
    )
    _hinge_clevis(frame.part, r, mats, toe_hinge[0], toe_hinge[2], "toe")
    toe_station = toe_len * _drive_station(r, (toe_hinge[0], toe_hinge[2]), toe_len)
    _board_plate(toe, r, mats, length=min(toe_len, toe_station + 0.016), prefix="toe")
    _drive_bracket(toe, r, mats, toe_station, "toe")
    joint = _spin_joint(
        model,
        frame.part,
        toe,
        name="board_style__split_heel__toe_hinge",
        point=toe_hinge,
        axis=(0.0, -1.0, 0.0),
        radial=(math.cos(r.board_tilt_rad), 0.0, math.sin(r.board_tilt_rad)),
        child_radial=(1.0, 0.0, 0.0),
        radius=_HINGE_R,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=420.0, velocity=7.0, lower=-r.board_press_rad, upper=0.05),
        meta={"mechanism": "footboard hinge", "positive_motion": "the toe lifts back up"},
    )
    return _Board(
        part=toe,
        drive_point=(toe_station, 0.0, _BOARD_T / 2.0 + _DRIVE_LIFT),
        hinge_joint=joint,
        parts=(heel, toe),
    )


_BOARD_BUILDERS = {
    "hinged_plate": _board_style_hinged_plate_build,
    "longboard": _board_style_longboard_build,
    "split_heel": _board_style_split_heel_build,
}


# --------------------------------------------------------------------------- #
# cam_style candidates
# --------------------------------------------------------------------------- #
_SECTOR_WRAP = math.radians(135.0)  # strap fork L68: the sector's own wrap angle


def _cam_rim_radius(r: ResolvedConfig, angle: float) -> float:
    """Drive radius of the cam at one rim angle, in the cam's own frame."""
    if r.cam_style == "eccentric_accel":
        return r.cam_radius_m * (1.0 + 0.24 * math.cos(angle - 0.5))
    return r.cam_radius_m


def _cam_max_radius(r: ResolvedConfig) -> float:
    return r.cam_radius_m * 1.24 if r.cam_style == "eccentric_accel" else r.cam_radius_m


def _finish_cam(model, r: ResolvedConfig, mats, frame: _Frame, part):
    """Hang whichever cam profile was built on the frame's rocker shaft."""
    joint = _spin_joint(
        model,
        frame.part,
        part,
        name=f"cam_style__{r.cam_style}__rocker",
        point=frame.shaft_point,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0130,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=350.0, velocity=12.0, lower=-0.25, upper=0.38),
        meta={"mechanism": "rocker shaft cam", "positive_motion": "swings the beater forward"},
    )
    return part, joint


def _cam_drive_angle(r: ResolvedConfig, frame: _Frame, board: _Board) -> float:
    """Rim angle the drive member leaves the cam at, in the cam's own frame."""
    start, _ = _drive_geometry(r, frame, board)
    return math.atan2(start[0], start[1])


def _cam_style_d_sector_build(part, r: ResolvedConfig, mats, drive_angle: float) -> None:
    """strap fork L68-L390: a solid 135-degree pie sector with a bore boss ring.

    The source extrudes one CadQuery pie slice; here the same body is a fan of
    overlapping radial fill bars capped by rim segments, and the wrap is centred
    on the run the drive member actually takes so it always has material to
    anchor to.
    """
    radius = r.cam_radius_m
    hub = 0.0130
    steps = 13
    start = drive_angle - _SECTOR_WRAP / 2.0
    step = _SECTOR_WRAP / float(steps - 1)
    # Boss ring bridging the axle surface to the sector bore, as the source does.
    _cyl(
        part,
        hub + 0.0022,
        _CAM_W * 0.86,
        (0.0, 0.0, 0.0),
        mats["cast"],
        "cam_boss_ring",
        rpy=_Y_AXIS_RPY,
    )
    for index in range(steps):
        angle = start + step * float(index)
        mid = (hub + radius) / 2.0
        span = radius - hub
        # Each fill bar is wide enough tangentially to overlap its neighbour at
        # the bore, which is the tightest place on the fan.
        _box(
            part,
            (step * hub * 1.45 + 0.004, _CAM_W, span),
            (mid * math.sin(angle), 0.0, mid * math.cos(angle)),
            mats["cast"],
            f"sector_fill_{index}",
            rpy=(0.0, -angle, 0.0),
        )
        _box(
            part,
            (step * radius * 1.45 + 0.004, _CAM_W, 0.006),
            ((radius - 0.002) * math.sin(angle), 0.0, (radius - 0.002) * math.cos(angle)),
            mats["cast"],
            f"sector_rim_{index}",
            rpy=(0.0, -angle, 0.0),
        )


def _build_cam(model, r: ResolvedConfig, mats, frame: _Frame, board: _Board):
    part = model.part(
        f"cam_style__{r.cam_style}__drive_cam",
        meta={"role": "drive_cam", "profile": r.cam_style},
    )
    _cyl(
        part,
        0.0130,
        2.0 * _HUB_HALF,
        (0.0, 0.0, 0.0),
        mats["cast"],
        "cam_hub",
        rpy=_Y_AXIS_RPY,
    )
    if r.beater_style == "height_carriage":
        # Host adaptation: the sliding carriage needs a real guide column.
        _cyl(part, 0.0055, 0.062, (0.0, _BEATER_Y, 0.035), mats["chrome"], "carriage_guide")
    if r.cam_style == "d_sector":
        _cam_style_d_sector_build(part, r, mats, _cam_drive_angle(r, frame, board))
        return _finish_cam(model, r, mats, frame, part)
    segments = 16
    for index in range(segments):
        angle = 2.0 * math.pi * float(index) / float(segments)
        radius = _cam_rim_radius(r, angle)
        mid = radius * 0.62
        _box(
            part,
            (
                2.0 * math.pi * radius / float(segments) * 1.35 + 0.004,
                _CAM_W,
                radius - mid + 0.006,
            ),
            (radius * 0.86 * math.sin(angle), 0.0, radius * 0.86 * math.cos(angle)),
            mats["cast"],
            f"cam_rim_{index}",
            rpy=(0.0, -angle, 0.0),
        )
        _bar(
            part,
            mats,
            (0.0, 0.0, 0.0),
            (radius * 0.86 * math.sin(angle), 0.0, radius * 0.86 * math.cos(angle)),
            0.008,
            _CAM_W * 0.55,
            mats["cast"],
            f"cam_spoke_{index}",
        )
    return _finish_cam(model, r, mats, frame, part)


# --------------------------------------------------------------------------- #
# drive_style candidates
# --------------------------------------------------------------------------- #
def _drive_anchor_radius(r: ResolvedConfig) -> float:
    """Radius of the cam's drive lug: outside every rim segment corner."""
    return _cam_max_radius(r) * 1.16 + 0.010


def _drive_geometry(r: ResolvedConfig, frame: _Frame, board: _Board):
    """The run from the cam rim down to just above the board's drive lug.

    Expressed in the cam's own frame, whose rest orientation matches the world.
    """
    bx, _, bz = board.drive_point
    tilt = r.board_tilt_rad
    world_x = r.heel_x_m + bx * math.cos(tilt) - bz * math.sin(tilt)
    world_z = _HINGE_Z + bx * math.sin(tilt) + bz * math.cos(tilt)
    dx = world_x
    dz = world_z - r.shaft_height_m
    reach = max(math.hypot(dx, dz), 1e-6)
    unit = (dx / reach, dz / reach)
    hang = _drive_anchor_radius(r) + 0.0006
    # The coupling is a rigid member in this model, so it reaches only part of
    # the way down the run; the board carries the matching drive lug.
    end_radius = hang + max(0.34 * (reach - hang), 0.010)
    start = (unit[0] * hang, unit[1] * hang)
    end = (unit[0] * end_radius, unit[1] * end_radius)
    return start, end


def _drive_anchor(cam, r: ResolvedConfig, mats, start) -> None:
    """The radial lug on the cam that the drive member is anchored to."""
    length = math.hypot(start[0], start[1]) or 1.0
    unit = (start[0] / length, start[1] / length)
    inner = _cam_max_radius(r) * 0.55
    _bar(
        cam,
        mats,
        (unit[0] * inner, 0.0, unit[1] * inner),
        (unit[0] * (length - 0.008), 0.0, unit[1] * (length - 0.008)),
        0.011,
        0.024,
        mats["cast"],
        "drive_anchor_lug",
    )


def _rim_outer(r: ResolvedConfig, angle: float) -> float:
    """Farthest rim-box corner near one angle, in the cam's own frame.

    The rim is drawn as sixteen rotated boxes, so the real envelope is the box
    corner, not the nominal radius; anything mounted on the rim measures from
    here or it will bite into a segment.
    """
    step = 2.0 * math.pi / 16.0
    best = 0.0
    for offset in (-step, 0.0, step):
        radius = _cam_rim_radius(r, angle + offset)
        tangential = (2.0 * math.pi * radius / 16.0 * 1.35 + 0.004) / 2.0
        radial = (0.38 * radius + 0.006) / 2.0
        best = max(best, math.hypot(0.86 * radius + radial, tangential))
    return best


def _drive_strip(
    part, r, mats, start_xz, end_xz, *, width: float, thickness: float, y: float, name: str
) -> None:
    _bar(
        part,
        mats,
        (0.0, y, 0.0),
        (end_xz[0] - start_xz[0], y, end_xz[1] - start_xz[1]),
        thickness,
        width,
        mats["chrome"],
        name,
    )


def _strip_delta(start_xz, end_xz) -> tuple[float, float]:
    return end_xz[0] - start_xz[0], end_xz[1] - start_xz[1]


def _mount_drive(model, r, mats, cam, start, part, name: str):
    """Fix one flexible drive member to the cam it wraps."""
    _drive_anchor(cam, r, mats, start)
    model.articulation(
        name,
        ArticulationType.FIXED,
        parent=cam,
        child=part,
        origin=Origin(xyz=(start[0], 0.0, start[1])),
        meta={"mechanism": "drive coupling between the footboard and the cam"},
    )
    return name


def _drive_style_single_chain_build(model, r, mats, frame, board, cam) -> list[str]:
    """001 L370-L394: one chain strip fixed to the board and wrapping the cam."""
    part = model.part(
        "drive_style__single_chain__chain",
        meta={"role": "drive_link", "kind": "single chain"},
    )
    start, end = _drive_geometry(r, frame, board)
    _drive_strip(part, r, mats, start, end, width=0.014, thickness=0.005, y=0.0, name="chain_strip")
    links = 7
    dx, dz = _strip_delta(start, end)
    for index in range(links):
        frac = (float(index) + 0.5) / float(links)
        _cyl(
            part,
            0.0032,
            0.020,
            (dx * frac, 0.0, dz * frac),
            mats["steel"],
            f"chain_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    return [_mount_drive(model, r, mats, cam, start, part, "drive_style__single_chain__anchor")]


def _drive_style_double_chain_build(model, r, mats, frame, board, cam) -> list[str]:
    """double_chain fork L400-L445: two indexed chain rows side by side."""
    part = model.part(
        "drive_style__double_chain__chain",
        meta={"role": "drive_link", "kind": "double chain"},
    )
    start, end = _drive_geometry(r, frame, board)
    dx, dz = _strip_delta(start, end)
    for row, sign in enumerate((-1.0, 1.0)):
        _drive_strip(
            part,
            r,
            mats,
            start,
            end,
            width=0.011,
            thickness=0.005,
            y=sign * 0.011,
            name=f"chain_row_{row}",
        )
    for index in range(7):
        frac = (float(index) + 0.5) / 7.0
        _cyl(
            part,
            0.0030,
            0.034,
            (dx * frac, 0.0, dz * frac),
            mats["steel"],
            f"row_pin_{index}",
            rpy=_Y_AXIS_RPY,
        )
    return [_mount_drive(model, r, mats, cam, start, part, "drive_style__double_chain__anchor")]


def _drive_style_strap_build(model, r, mats, frame, board, cam) -> list[str]:
    """strap fork L430-L482: one wide nylon strap with a clamped end tab."""
    part = model.part(
        "drive_style__strap__strap",
        meta={"role": "drive_link", "kind": "nylon strap"},
    )
    start, end = _drive_geometry(r, frame, board)
    _drive_strip(part, r, mats, start, end, width=0.030, thickness=0.0032, y=0.0, name="strap_web")
    dx, dz = _strip_delta(start, end)
    _box(part, (0.020, 0.034, 0.006), (dx * 0.94, 0.0, dz * 0.94), mats["cast"], "strap_clamp_tab")
    _cyl(
        part,
        0.0030,
        0.030,
        (dx * 0.94, 0.0, dz * 0.94),
        mats["steel"],
        "strap_clamp_bolt",
        rpy=_Y_AXIS_RPY,
    )
    return [_mount_drive(model, r, mats, cam, start, part, "drive_style__strap__anchor")]


def _drive_style_direct_link_build(model, r, mats, frame, board, cam) -> list[str]:
    """direct fork L373-L449: a rigid forged link hinged on the footboard."""
    part = model.part(
        "drive_style__direct_link__link",
        meta={"role": "drive_link", "kind": "rigid direct link"},
    )
    start, end = _drive_geometry(r, frame, board)
    length = math.hypot(end[0] - start[0], end[1] - start[1])
    _cyl(part, 0.0040, 0.024, (0.0, 0.0, 0.0), mats["chrome"], "link_eye", rpy=_Y_AXIS_RPY)
    _bar(
        part,
        mats,
        (0.0, 0.0, -0.008),
        (0.0, 0.0, -length),
        0.011,
        0.016,
        mats["chrome"],
        "link_body",
    )
    _cyl(part, 0.0040, 0.020, (0.0, 0.0, -length), mats["chrome"], "link_far_eye", rpy=_Y_AXIS_RPY)
    _drive_anchor(cam, r, mats, start)
    unit_len = math.hypot(start[0], start[1]) or 1.0
    pin = (start[0] / unit_len * (unit_len + 0.002), start[1] / unit_len * (unit_len + 0.002))
    joint = _spin_joint(
        model,
        cam,
        part,
        name="drive_style__direct_link__swing",
        point=(pin[0], 0.0, pin[1]),
        axis=(0.0, 1.0, 0.0),
        radial=(start[0] / unit_len, 0.0, start[1] / unit_len),
        child_radial=(0.0, 0.0, -1.0),
        radius=0.0040,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=85.0, velocity=6.0, lower=-0.03, upper=0.03),
        meta={"mechanism": "rigid direct drive link"},
    )
    return [joint]


_DRIVE_BUILDERS = {
    "single_chain": _drive_style_single_chain_build,
    "double_chain": _drive_style_double_chain_build,
    "strap": _drive_style_strap_build,
    "direct_link": _drive_style_direct_link_build,
}


# --------------------------------------------------------------------------- #
# beater_style candidates
# --------------------------------------------------------------------------- #
_BEATER_ROOT_Z = 0.012


def _beater_shaft(part, r, mats, *, length: float, prefix: str) -> None:
    """The shaft rises out of a clamp collar that grips the rocker shaft."""
    _cyl(
        part,
        0.0044,
        length,
        (0.0, 0.0, _BEATER_ROOT_Z + length / 2.0),
        mats["chrome"],
        f"{prefix}_shaft",
    )
    _cyl(
        part,
        0.0090,
        0.018,
        (0.0, 0.0, _BEATER_ROOT_Z + 0.008),
        mats["cast"],
        f"{prefix}_shaft_collar",
    )


def _beater_adjuster(model, r, mats, host, name: str) -> str:
    """The small knurled beater-angle screw on the cam hub."""
    _cyl(host, 0.0050, 0.020, (0.0, -0.014, 0.006), mats["cast"], f"{name}_boss", rpy=_Y_AXIS_RPY)
    knob = model.part(name, meta={"role": "adjuster", "mechanism": "beater angle screw"})
    _cyl(knob, 0.0022, 0.014, (0.0, 0.0, 0.0), mats["steel"], "screw_stem", rpy=_Y_AXIS_RPY)
    _knurled(knob, 0.0070, 0.007, (0.0, -0.010, 0.0), mats, "screw_knob", _Y_AXIS_RPY, bands=12)
    return _spin_joint(
        model,
        host,
        knob,
        name=f"{name}__spin",
        point=(0.0, -0.020, 0.006),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0022,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=20.0, velocity=6.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "beater angle screw"},
    )


def _beater_style_fixed_head_build(model, r, mats, frame, cam) -> list[str]:
    """001 L398-L444: a one-piece beater clamped straight onto the cam hub."""
    part = model.part(
        "beater_style__fixed_head__beater",
        meta={"role": "beater", "head": "fixed felt"},
    )
    length = r.beater_length_m
    _beater_shaft(part, r, mats, length=length, prefix="beater")
    _cyl(
        part,
        0.0180,
        0.030,
        (0.0, 0.0, _BEATER_ROOT_Z + length - 0.006),
        mats["felt"],
        "beater_head",
    )
    _cyl(
        part,
        0.0090,
        0.010,
        (0.0, 0.0, _BEATER_ROOT_Z + length - 0.022),
        mats["cast"],
        "head_collar",
    )
    joint = _spin_joint(
        model,
        cam,
        part,
        name="beater_style__fixed_head__pitch",
        point=(0.0, _BEATER_Y, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0044,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=160.0, velocity=8.0, lower=-0.18, upper=0.18),
        meta={"mechanism": "beater angle on the rocker shaft"},
    )
    adjuster = _beater_adjuster(model, r, mats, cam, "beater_style__fixed_head__angle_screw")
    return [joint, adjuster]


def _beater_style_reversible_head_build(model, r, mats, frame, cam) -> list[str]:
    """reversible fork L443-L508: a head that flips about the shaft axis."""
    part = model.part(
        "beater_style__reversible_head__beater",
        meta={"role": "beater", "head": "reversible"},
    )
    length = r.beater_length_m
    _beater_shaft(part, r, mats, length=length, prefix="beater")
    _cyl(
        part, 0.0075, 0.014, (0.0, 0.0, _BEATER_ROOT_Z + length - 0.002), mats["cast"], "head_yoke"
    )
    joint = _spin_joint(
        model,
        cam,
        part,
        name="beater_style__reversible_head__pitch",
        point=(0.0, _BEATER_Y, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0044,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=160.0, velocity=8.0, lower=-0.18, upper=0.18),
        meta={"mechanism": "beater angle on the rocker shaft"},
    )
    head = model.part(
        "beater_style__reversible_head__head",
        meta={"role": "beater_head", "mechanism": "reversible felt/plastic head"},
    )
    # Felt on one side, moulded plastic on the other, on one cross barrel; a half
    # turn about the transverse axis brings the other face round to the drum.
    _cyl(head, 0.0080, 0.026, (0.0, 0.0, 0.0), mats["chrome"], "head_hub")
    _cyl(head, 0.0160, 0.018, (0.018, 0.0, 0.0), mats["felt"], "felt_face", rpy=_X_AXIS_RPY)
    _cyl(head, 0.0150, 0.014, (-0.018, 0.0, 0.0), mats["cast"], "plastic_face", rpy=_X_AXIS_RPY)
    _bar(
        head,
        mats,
        (-0.018, 0.0, 0.0),
        (0.018, 0.0, 0.0),
        0.009,
        0.012,
        mats["chrome"],
        "head_yoke_bar",
    )
    flip = _spin_joint(
        model,
        part,
        head,
        name="beater_style__reversible_head__flip",
        point=(0.0, 0.0, _BEATER_ROOT_Z + length + 0.016),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0080,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=12.0, velocity=4.0, lower=0.0, upper=math.pi),
        meta={"mechanism": "reversible beater head"},
    )
    adjuster = _beater_adjuster(model, r, mats, cam, "beater_style__reversible_head__angle_screw")
    return [joint, flip, adjuster]


def _beater_style_height_carriage_build(model, r, mats, frame, cam) -> list[str]:
    """carriage fork L426-L555: a prismatic height carriage under the beater."""
    carriage = model.part(
        "beater_style__height_carriage__carriage",
        meta={"role": "beater_carriage", "mechanism": "beater height slide"},
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            carriage,
            (0.009, 0.030, 0.050),
            (sign * 0.0105, 0.0, 0.023),
            mats["cast"],
            f"carriage_cheek_{index}",
        )
        _box(
            carriage,
            (0.030, 0.007, 0.050),
            (0.0, sign * 0.0125, 0.023),
            mats["cast"],
            f"carriage_wall_{index}",
        )
    _box(carriage, (0.030, 0.030, 0.008), (0.0, 0.0, 0.044), mats["cast"], "carriage_cap")
    _cyl(carriage, 0.0050, 0.020, (0.0, 0.018, 0.030), mats["cast"], "lock_boss", rpy=_Y_AXIS_RPY)
    travel = 0.022
    prismatic = "beater_style__height_carriage__lift"
    model.articulation(
        prismatic,
        ArticulationType.PRISMATIC,
        parent=cam,
        child=carriage,
        origin=Origin(xyz=(0.0, _BEATER_Y, 0.022)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.4, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=1.6, friction=0.8),
        meta={"mechanism": "beater height adjustment"},
    )
    lock = model.part(
        "beater_style__height_carriage__lock",
        meta={"role": "adjuster", "mechanism": "carriage locking knob"},
    )
    _cyl(lock, 0.0022, 0.014, (0.0, 0.0, 0.0), mats["steel"], "lock_stem", rpy=_Y_AXIS_RPY)
    _knurled(lock, 0.0072, 0.008, (0.0, 0.011, 0.0), mats, "lock_knob", _Y_AXIS_RPY, bands=12)
    lock_joint = _spin_joint(
        model,
        carriage,
        lock,
        name="beater_style__height_carriage__lock_spin",
        point=(0.0, 0.026, 0.030),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0022,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=12.0, velocity=8.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "carriage lock"},
    )
    beater = model.part(
        "beater_style__height_carriage__beater",
        meta={"role": "beater", "head": "fixed felt on a height carriage"},
    )
    length = r.beater_length_m
    _beater_shaft(beater, r, mats, length=length, prefix="beater")
    _cyl(
        beater,
        0.0180,
        0.030,
        (0.0, 0.0, _BEATER_ROOT_Z + length - 0.006),
        mats["felt"],
        "beater_head",
    )
    _cyl(
        beater,
        0.0090,
        0.010,
        (0.0, 0.0, _BEATER_ROOT_Z + length - 0.022),
        mats["cast"],
        "head_collar",
    )
    pitch = _spin_joint(
        model,
        carriage,
        beater,
        name="beater_style__height_carriage__pitch",
        point=(0.0, 0.0, 0.034),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0044,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=160.0, velocity=8.0, lower=-0.18, upper=0.18),
        meta={"mechanism": "beater angle on the carriage"},
    )
    return [prismatic, lock_joint, pitch]


_BEATER_BUILDERS = {
    "fixed_head": _beater_style_fixed_head_build,
    "reversible_head": _beater_style_reversible_head_build,
    "height_carriage": _beater_style_height_carriage_build,
}


# --------------------------------------------------------------------------- #
# clamp_style candidates
# --------------------------------------------------------------------------- #
def _clamp_style_screw_clamp_build(model, r, mats, frame: _Frame) -> list[str]:
    """001 L447-L510: a clamp lever with a knurled hoop screw."""
    lever = model.part(
        "clamp_style__screw_clamp__clamp_lever",
        meta={"role": "hoop_clamp", "mechanism": "screw hoop clamp"},
    )
    _cyl(lever, 0.0060, 0.040, (0.0, 0.0, 0.0), mats["cast"], "lever_eye", rpy=_Y_AXIS_RPY)
    _box(lever, (0.048, 0.038, 0.012), (0.022, 0.0, 0.002), mats["cast"], "lever_jaw")
    _box(lever, (0.014, 0.038, 0.026), (0.042, 0.0, 0.015), mats["cast"], "jaw_lip")
    joint = _spin_joint(
        model,
        frame.part,
        lever,
        name="clamp_style__screw_clamp__swing",
        point=frame.clamp_point,
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0060,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=95.0, velocity=2.5, lower=-0.12, upper=0.16),
        meta={"mechanism": "hoop clamp lever"},
    )
    screw = model.part(
        "clamp_style__screw_clamp__hoop_screw",
        meta={"role": "adjuster", "mechanism": "hoop clamp screw"},
    )
    _cyl(screw, 0.0026, 0.028, (0.0, 0.0, -0.010), mats["steel"], "screw_stem")
    _knurled(screw, 0.0090, 0.008, (0.0, 0.0, 0.008), mats, "screw_knob", (0.0, 0.0, 0.0), bands=14)
    spin = _spin_joint(
        model,
        lever,
        screw,
        name="clamp_style__screw_clamp__screw_spin",
        point=(0.022, 0.0, 0.020),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0026,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=28.0, velocity=10.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "hoop clamp screw"},
    )
    return [joint, spin]


def _clamp_style_overcenter_toggle_build(model, r, mats, frame: _Frame) -> list[str]:
    """overcenter fork L452-L619: a cam lever, a toggle link and a pressure shoe."""
    lever = model.part(
        "clamp_style__overcenter_toggle__cam_lever",
        meta={"role": "hoop_clamp", "mechanism": "over-centre cam lever"},
    )
    _cyl(lever, 0.0070, 0.030, (0.0, 0.0, 0.0), mats["cast"], "lever_eye", rpy=_Y_AXIS_RPY)
    _bar(lever, mats, (0.0, 0.0, 0.0), (0.006, 0.0, 0.052), 0.013, 0.022, mats["cast"], "lever_arm")
    _box(lever, (0.030, 0.026, 0.012), (0.014, 0.0, 0.056), mats["rubber"], "lever_grip")
    joint = _spin_joint(
        model,
        frame.part,
        lever,
        name="clamp_style__overcenter_toggle__swing",
        point=frame.clamp_point,
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0070,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=120.0, velocity=3.0, lower=-0.20, upper=0.30),
        meta={"mechanism": "over-centre cam lever"},
    )
    link = model.part(
        "clamp_style__overcenter_toggle__toggle_link",
        meta={"role": "hoop_clamp_link", "mechanism": "toggle link"},
    )
    _cyl(link, 0.0044, 0.020, (0.0, 0.0, 0.0), mats["chrome"], "link_eye", rpy=_Y_AXIS_RPY)
    _bar(link, mats, (0.0, 0.0, 0.0), (0.026, 0.0, 0.0), 0.010, 0.012, mats["chrome"], "link_body")
    _cyl(link, 0.0044, 0.020, (0.026, 0.006, 0.0), mats["chrome"], "link_far_eye", rpy=_Y_AXIS_RPY)
    toggle = _spin_joint(
        model,
        lever,
        link,
        name="clamp_style__overcenter_toggle__toggle",
        point=(0.004, 0.017, 0.026),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0044,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=80.0, velocity=4.0, lower=-0.30, upper=0.30),
        meta={"mechanism": "toggle link"},
    )
    shoe = model.part(
        "clamp_style__overcenter_toggle__pressure_shoe",
        meta={"role": "hoop_clamp_shoe", "mechanism": "pressure shoe"},
    )
    _cyl(shoe, 0.0044, 0.018, (0.0, 0.0, 0.0), mats["chrome"], "shoe_eye", rpy=_Y_AXIS_RPY)
    _box(shoe, (0.026, 0.032, 0.010), (0.011, 0.0, -0.006), mats["cast"], "shoe_plate")
    _box(shoe, (0.026, 0.032, 0.005), (0.011, 0.0, -0.013), mats["rubber"], "shoe_pad")
    press = _spin_joint(
        model,
        link,
        shoe,
        name="clamp_style__overcenter_toggle__press",
        point=(0.026, 0.014, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0044,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=40.0, velocity=2.0, lower=-0.26, upper=0.26),
        meta={"mechanism": "pressure shoe"},
    )
    return [joint, toggle, press]


_CLAMP_BUILDERS = {
    "screw_clamp": _clamp_style_screw_clamp_build,
    "overcenter_toggle": _clamp_style_overcenter_toggle_build,
}


# --------------------------------------------------------------------------- #
# spring_style candidates
# --------------------------------------------------------------------------- #
def _clamp_style_spring_mount(frame: _Frame, r: ResolvedConfig) -> tuple[float, float, float]:
    return (0.006, frame.spring_y, r.shaft_height_m * 0.30)


def _spring_style_coil_return_build(model, r, mats, frame: _Frame) -> list[str]:
    """001 L512-L608: a coil spring on the post with a knurled tension nut."""
    mount = _clamp_style_spring_mount(frame, r)
    _box(
        frame.part,
        (0.016, max(frame.spring_y - r.post_y_m - 0.008, 0.006), 0.018),
        (mount[0], (frame.spring_y + r.post_y_m - 0.008) / 2.0, mount[2]),
        mats["cast"],
        "spring_lug",
    )
    spring = model.part(
        "spring_style__coil_return__return_spring",
        meta={"role": "return_spring", "mechanism": "coil return spring"},
    )
    length = r.shaft_height_m * 0.52
    _cyl(spring, 0.0022, length, (0.0, 0.0, length / 2.0), mats["steel"], "spring_core")
    coils = 9
    for index in range(coils):
        z = length * (0.06 + 0.88 * float(index) / float(coils - 1))
        _cyl(spring, 0.0075, 0.0030, (0.0, 0.0, z), mats["chrome"], f"spring_coil_{index}")
    _cyl(spring, 0.0055, 0.008, (0.0, 0.0, length), mats["chrome"], "spring_top_hook")
    model.articulation(
        "spring_style__coil_return__anchor",
        ArticulationType.FIXED,
        parent=frame.part,
        child=spring,
        origin=Origin(xyz=mount),
        meta={"mechanism": "return spring anchor"},
    )
    nut = model.part(
        "spring_style__coil_return__tension_nut",
        meta={"role": "adjuster", "mechanism": "spring tension adjuster"},
    )
    _cyl(nut, 0.0026, 0.016, (0.0, 0.0, 0.0), mats["steel"], "nut_stem")
    _knurled(nut, 0.0090, 0.008, (0.0, 0.0, -0.006), mats, "nut_knob", (0.0, 0.0, 0.0), bands=14)
    spin = _spin_joint(
        model,
        frame.part,
        nut,
        name="spring_style__coil_return__tension_spin",
        point=(mount[0], mount[1], mount[2] - 0.006),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0026,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=18.0, velocity=8.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "spring tension adjuster"},
    )
    return [spin]


def _spring_style_leaf_return_build(model, r, mats, frame: _Frame) -> list[str]:
    """leaf fork L601-L663: a bolted cantilever leaf stack, no coil or nut."""
    mount = _clamp_style_spring_mount(frame, r)
    _box(
        frame.part,
        (0.020, max(frame.spring_y - r.post_y_m - 0.008, 0.006), 0.024),
        (mount[0], (frame.spring_y + r.post_y_m - 0.008) / 2.0, mount[2]),
        mats["cast"],
        "leaf_boss",
    )
    leaf = model.part(
        "spring_style__leaf_return__leaf_spring",
        meta={"role": "return_spring", "mechanism": "cantilever leaf spring"},
    )
    length = r.shaft_height_m * 0.60
    for index in range(3):
        leaf_len = length * (1.0 - 0.16 * float(index))
        _bar(
            leaf,
            mats,
            (0.0, 0.0, 0.0),
            (leaf_len * 0.22, 0.0, leaf_len),
            0.0028,
            0.018 - 0.003 * float(index),
            mats["steel"],
            f"leaf_{index}",
        )
    _box(leaf, (0.020, 0.024, 0.012), (0.0, 0.0, 0.002), mats["cast"], "leaf_clamp_block")
    _cyl(leaf, 0.0026, 0.028, (0.0, 0.0, 0.002), mats["steel"], "leaf_bolt", rpy=_Y_AXIS_RPY)
    model.articulation(
        "spring_style__leaf_return__anchor",
        ArticulationType.FIXED,
        parent=frame.part,
        child=leaf,
        origin=Origin(xyz=mount),
        meta={"mechanism": "leaf spring anchor"},
    )
    return []


_SPRING_BUILDERS = {
    "coil_return": _spring_style_coil_return_build,
    "leaf_return": _spring_style_leaf_return_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_drum_pedal_with_beater_and_spring_return(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_drum_pedal_with_beater_and_spring_return",
            "identified_object": "bass drum pedal with beater and spring return",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": (
                "a floor frame, a hinged footboard, a drive coupling to a rocker cam, "
                "a beater, a hoop clamp and a return spring"
            ),
        },
    )
    mats = _materials(model)
    frame = _FRAME_BUILDERS[r.frame_style](model, r, mats)
    board = _BOARD_BUILDERS[r.board_style](model, r, mats, frame)
    cam, _ = _build_cam(model, r, mats, frame, board)
    _DRIVE_BUILDERS[r.drive_style](model, r, mats, frame, board, cam)
    _BEATER_BUILDERS[r.beater_style](model, r, mats, frame, cam)
    _CLAMP_BUILDERS[r.clamp_style](model, r, mats, frame)
    _SPRING_BUILDERS[r.spring_style](model, r, mats, frame)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_pictureX_0611_drum_pedal_with_beater_and_spring_return_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "frame")
    boards = _parts_by_role(model, "footboard")
    cams = _parts_by_role(model, "drive_cam")
    beaters = _parts_by_role(model, "beater")
    drives = _parts_by_role(model, "drive_link")
    clamps = _parts_by_role(model, "hoop_clamp")
    springs = _parts_by_role(model, "return_spring")

    ctx.check(
        "category_anchor: one floor frame carries the pedal",
        len(frames) == 1,
        details=f"frames={[part.name for part in frames]}",
    )
    ctx.check(
        "category_anchor: a hinged footboard rides the frame",
        len(boards) == (2 if r.board_style == "split_heel" else 1),
        details=f"boards={[part.name for part in boards]}",
    )
    ctx.check(
        "category_anchor: a rocker cam turns on the frame shaft",
        len(cams) == 1,
        details=f"cams={[part.name for part in cams]}",
    )
    ctx.check(
        "category_anchor: a beater swings off the rocker shaft",
        len(beaters) == 1,
        details=f"beaters={[part.name for part in beaters]}",
    )
    ctx.check(
        "category_anchor: a hoop clamp closes on the frame front",
        len(clamps) == 1,
        details=f"clamps={[part.name for part in clamps]}",
    )
    ctx.check(
        "category_anchor: a return spring is anchored to the frame",
        len(springs) == 1,
        details=f"springs={[part.name for part in springs]}",
    )
    ctx.check(
        "category_anchor: the footboard drives the cam through a real coupling",
        len(drives) == (0 if r.drive_style == "direct_link" else 1)
        or r.drive_style == "direct_link",
        details=f"drive links={[part.name for part in drives]}",
    )

    board_hinges = [
        joint for joint in model.articulations if joint.meta.get("mechanism") == "footboard hinge"
    ]
    ctx.check(
        "every footboard section hinges on a real revolute joint",
        len(board_hinges) == len(boards)
        and all(joint.articulation_type == ArticulationType.REVOLUTE for joint in board_hinges),
        details=f"hinges={[joint.name for joint in board_hinges]}",
    )

    rocker = next(
        joint for joint in model.articulations if joint.meta.get("mechanism") == "rocker shaft cam"
    )
    beater = beaters[0]
    rest = ctx.part_world_aabb(beater)
    with ctx.pose({rocker: rocker.motion_limits.upper}):
        struck = ctx.part_world_aabb(beater)
    moved = None
    if rest is not None and struck is not None:
        moved = abs((struck[0][0] + struck[1][0]) / 2.0 - (rest[0][0] + rest[1][0]) / 2.0)
    ctx.check(
        "category_anchor: turning the rocker swings the beater forward",
        moved is not None and moved > 0.010,
        details=f"rest={rest}, struck={struck}, moved={moved}",
    )

    for hinge in board_hinges:
        child = model.get_part(hinge.child)
        up = ctx.part_world_aabb(child)
        with ctx.pose({hinge: hinge.motion_limits.lower}):
            down = ctx.part_world_aabb(child)
        dropped = None
        if up is not None and down is not None:
            dropped = up[1][2] - down[1][2]
        ctx.check(
            f"{hinge.name} presses the board down toward the floor",
            dropped is not None and dropped > 0.002,
            details=f"released={up}, pressed={down}, drop={dropped}",
        )

    if r.beater_style == "height_carriage":
        lift = next(joint for joint in model.articulations if joint.name.endswith("__lift"))
        child = model.get_part(lift.child)
        low = ctx.part_world_aabb(child)
        with ctx.pose({lift: lift.motion_limits.upper}):
            high = ctx.part_world_aabb(child)
        ctx.check(
            "the beater height carriage really slides on the hub",
            low is not None
            and high is not None
            and abs(high[0][2] - low[0][2]) > 0.4 * lift.motion_limits.upper,
            details=f"low={low}, high={high}",
        )

    ctx.check(
        "the footboard runs clear between the frame uprights",
        r.frame_width_m >= r.board_width_m + 2.0 * r.frame_margin_m,
        details=f"frame={r.frame_width_m:.4f}, board={r.board_width_m:.4f}",
    )
    ctx.check(
        "the beater reaches above the rocker shaft",
        r.beater_length_m > r.cam_radius_m * 2.0,
        details=f"beater={r.beater_length_m:.4f}, cam_r={r.cam_radius_m:.4f}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "sector_cam_longest_board_strap",
        {
            "frame_style": "twin_post_rail",
            "board_style": "longboard",
            "drive_style": "strap",
            "cam_style": "d_sector",
            "beater_style": "height_carriage",
            "clamp_style": "screw_clamp",
            "spring_style": "leaf_return",
            "board_length_m": 0.340,
            "board_width_m": 0.135,
            "shaft_height_m": 0.200,
            "beater_length_m": 0.260,
            "frame_margin_m": 0.040,
        },
        reason="the 135-degree sector must still carry the drive lug at the shallowest strap run",
    ),
    corner_case(
        "sector_cam_shortest_board_direct_link",
        {
            "frame_style": "cast_post",
            "board_style": "split_heel",
            "drive_style": "direct_link",
            "cam_style": "d_sector",
            "beater_style": "reversible_head",
            "clamp_style": "overcenter_toggle",
            "spring_style": "coil_return",
            "board_length_m": 0.240,
            "board_width_m": 0.095,
            "shaft_height_m": 0.140,
            "beater_length_m": 0.180,
            "frame_margin_m": 0.018,
        },
        reason="the steepest drive run puts the sector wrap at its most tilted",
    ),
    corner_case(
        "widest_board_tallest_shaft_double_chain",
        {
            "frame_style": "cast_post",
            "board_style": "longboard",
            "drive_style": "double_chain",
            "cam_style": "eccentric_accel",
            "beater_style": "height_carriage",
            "clamp_style": "overcenter_toggle",
            "spring_style": "coil_return",
            "board_length_m": 0.340,
            "board_width_m": 0.135,
            "shaft_height_m": 0.200,
            "beater_length_m": 0.260,
            "frame_margin_m": 0.040,
        },
        reason="longest board and tallest shaft with the deepest cam profile",
    ),
    corner_case(
        "smallest_pedal_direct_link",
        {
            "frame_style": "twin_post_rail",
            "board_style": "split_heel",
            "drive_style": "direct_link",
            "cam_style": "round_cam",
            "beater_style": "fixed_head",
            "clamp_style": "screw_clamp",
            "spring_style": "leaf_return",
            "board_length_m": 0.200,
            "board_width_m": 0.085,
            "shaft_height_m": 0.110,
            "beater_length_m": 0.150,
            "frame_margin_m": 0.014,
        },
        reason="shortest split board on the lowest shaft with a rigid link",
    ),
    corner_case(
        "narrow_frame_wide_board_capacity",
        {
            "frame_style": "twin_post_rail",
            "board_style": "hinged_plate",
            "drive_style": "strap",
            "cam_style": "eccentric_accel",
            "beater_style": "reversible_head",
            "clamp_style": "overcenter_toggle",
            "spring_style": "leaf_return",
            "board_length_m": 0.320,
            "board_width_m": 0.135,
            "shaft_height_m": 0.120,
            "beater_length_m": 0.250,
            "frame_margin_m": 0.014,
        },
        reason="the widest board forces the narrow frame to widen to host capacity",
    ),
    corner_case(
        "tall_shaft_short_board_strap",
        {
            "frame_style": "cast_post",
            "board_style": "split_heel",
            "drive_style": "strap",
            "cam_style": "round_cam",
            "beater_style": "height_carriage",
            "clamp_style": "screw_clamp",
            "spring_style": "coil_return",
            "board_length_m": 0.200,
            "board_width_m": 0.090,
            "shaft_height_m": 0.200,
            "beater_length_m": 0.150,
            "frame_margin_m": 0.022,
        },
        reason="the steepest board angle the geometry allows under a tall shaft",
    ),
    corner_case(
        "longboard_reversible_head_low_shaft",
        {
            "frame_style": "twin_post_rail",
            "board_style": "longboard",
            "drive_style": "single_chain",
            "cam_style": "eccentric_accel",
            "beater_style": "reversible_head",
            "clamp_style": "screw_clamp",
            "spring_style": "coil_return",
            "board_length_m": 0.340,
            "board_width_m": 0.120,
            "shaft_height_m": 0.110,
            "beater_length_m": 0.260,
            "frame_margin_m": 0.032,
        },
        reason="the flattest long board under the longest beater",
    ),
    corner_case(
        "direct_link_height_carriage",
        {
            "frame_style": "cast_post",
            "board_style": "hinged_plate",
            "drive_style": "direct_link",
            "cam_style": "eccentric_accel",
            "beater_style": "height_carriage",
            "clamp_style": "overcenter_toggle",
            "spring_style": "leaf_return",
            "board_length_m": 0.260,
            "board_width_m": 0.110,
            "shaft_height_m": 0.170,
            "beater_length_m": 0.230,
            "frame_margin_m": 0.028,
        },
        reason="a rigid link swinging beside a sliding beater carriage",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_drum_pedal_with_beater_and_spring_return",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_drum_pedal_with_beater_and_spring_return_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
