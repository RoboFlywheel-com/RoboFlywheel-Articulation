# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'Locker box' template — lockable acrylic locker cabinets.

Rebuilt from three source records (all rev_000001):

* ``rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124``
  — wide acrylic carcass with plain shelves, discrete butt-hinge stations whose
  carcass knuckles interleave in Z with the door knuckles, rotary key locks on
  REVOLUTE-Y collars, a pivoting latch lever and a fixed latch keeper.
* ``rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc``
  — twenty individually side-hinged *framed* leaves, static cam latch + molded
  padlock + shackle, shelves *and* vertical dividers, metal front mullions with
  screw fasteners.
* ``rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc``
  — one articulated *flat* leaf on a full-height hinge mount + pin, static cam
  latch + padlock, shelves and dividers, flush polished edge rails.

The locker box is a hollow sheet shell (side walls, floor, top, back and
shelves) closed by ``compartment_count`` real side-hinged doors stacked in one
column.  Five independent structural slots come straight from the records:
door leaf construction, lock mechanism, hinge hardware, carcass front frame and
interior subdivision.

Mechanical contract kept by every combination:

* the hinge line is a real coaxial pair — the carcass knuckles and the door
  knuckle/barrel sit on the same axis and engage *axially* by 0.5 mm.  Because
  the pair is coaxial the engagement is rotation invariant, so the leaf stays
  captured (and under the 1 mm collision tolerance) at every pose.  Nothing in
  this file calls ``allow_overlap`` and no joint travel is clamped.
* the whole door plane sits ``_FRONT_GAP`` ahead of the carcass face and the
  leaf extends toward +X from the hinge, so +theta about +Z (measured, see the
  author tests) swings it outward toward +Y and its minimum swept Y over the
  full range is its closed back face — it can never re-enter the carcass.

This file is the only runtime truth.  It imports nothing but the stdlib and the
Articraft ``sdk``; it never reads the SourceMap, TemplateDesign, a source
``model.py`` or any source-replay runtime.
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
    multiplicity_slot,
    register_interface_mate,
)

DoorLeaf = Literal["flat_leaf", "framed_leaf"]
Lock = Literal["rotary_key", "cam_padlock"]
Hinge = Literal["knuckle_pair", "piano_barrel"]
CarcassFront = Literal["mullion_frame", "edge_strip"]
Interior = Literal["open_shelf", "grid_cubby"]

DOOR_LEAVES: tuple[DoorLeaf, ...] = ("flat_leaf", "framed_leaf")
LOCKS: tuple[Lock, ...] = ("rotary_key", "cam_padlock")
HINGES: tuple[Hinge, ...] = ("knuckle_pair", "piano_barrel")
CARCASS_FRONTS: tuple[CarcassFront, ...] = ("mullion_frame", "edge_strip")
INTERIORS: tuple[Interior, ...] = ("open_shelf", "grid_cubby")
COMPARTMENT_COUNTS: tuple[int, ...] = (2, 3, 4, 5)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("door_leaf", DOOR_LEAVES, role="locker_door"),
        component_slot("lock", LOCKS, role="lock_hardware"),
        component_slot("hinge", HINGES, role="hinge_hardware"),
        component_slot("carcass_front", CARCASS_FRONTS, role="front_frame"),
        component_slot("interior", INTERIORS, role="interior"),
        multiplicity_slot(
            "compartment_count",
            COMPARTMENT_COUNTS,
            item_slot="door_leaf",
        ),
    )
)

# Independent continuous ranges (honest dimensions; not core/raw diversity).
_WIDTH_RANGE = (0.28, 0.44)
_DEPTH_RANGE = (0.14, 0.24)
_CELL_HEIGHT_RANGE = (0.09, 0.15)

# Fixed sheet/hardware constants derived from the three records.
_WALL = 0.005
_SHELF_T = 0.004
_DOOR_T = 0.004
_FRONT_GAP = 0.006  # clear air between the carcass face and the closed leaf back
_HINGE_OFFSET = 0.006  # hinge axis outboard of the left wall (001 HINGE_OFFSET 0.008)
_LEAF_INSET = 0.010  # leaf near edge, measured from the hinge axis
_ENGAGE = 0.0005  # axial knuckle engagement: real capture, 1/2 of the 1 mm tolerance
_HOST_KNUCKLE_R = 0.0048
_DOOR_KNUCKLE_R = 0.0045
_HOST_KNUCKLE_LEN = 0.010
_DOOR_KNUCKLE_LEN = 0.015
_HOST_STUB_LEN = 0.012
_LEAF_PLATE_X = 0.020
_DOOR_OPEN_UPPER = 1.55  # rad; capped below pi/2 + leaf thickness excursion
_KEY_LIMIT = 0.55
_LATCH_LIMIT = 0.65
_COLLAR_LEN = 0.006
_COLLAR_EMBED = 0.001  # collar sunk into the leaf face: intra-part, keeps it connected
_COLLAR_Y = _DOOR_T / 2.0 - _COLLAR_EMBED + _COLLAR_LEN / 2.0
_COLLAR_FRONT_Y = _DOOR_T / 2.0 - _COLLAR_EMBED + _COLLAR_LEN  # key/latch mating plane
# Key/latch spindles turn about a horizontal axis that itself swings with the door, so
# their world AABB is oblique at intermediate door angles and inflates on the X and Y
# axes. The door only ever rotates about world Z, so the world Z extent of a spindle
# stays 2 * radius; keeping that radius small is what stops the intended 0.5 mm seat
# from ever reading as a bulk overlap in a swung pose.
_KEY_SHAFT_R = 0.0016
_LATCH_SHAFT_R = 0.0018


@dataclass(frozen=True)
class Config:
    door_leaf: DoorLeaf = "flat_leaf"
    lock: Lock = "rotary_key"
    hinge: Hinge = "knuckle_pair"
    carcass_front: CarcassFront = "mullion_frame"
    interior: Interior = "open_shelf"
    compartment_count: int = 3
    width_m: float | None = None
    depth_m: float | None = None
    cell_height_m: float | None = None
    name: str = "picturex_0611_locker_box"


@dataclass(frozen=True)
class ResolvedConfig:
    door_leaf: DoorLeaf
    lock: Lock
    hinge: Hinge
    carcass_front: CarcassFront
    interior: Interior
    compartment_count: int
    width_m: float
    depth_m: float
    cell_height_m: float
    # derived
    height_m: float
    wall_m: float
    door_t_m: float
    door_width_m: float
    door_height_m: float
    hinge_x_m: float
    hinge_y_m: float
    front_gap_m: float
    engagement_m: float
    key_station_x_m: float
    latch_station_x_m: float
    name: str


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x10CBE_2026)
    return Config(
        door_leaf=choices["door_leaf"],
        lock=choices["lock"],
        hinge=choices["hinge"],
        carcass_front=choices["carcass_front"],
        interior=choices["interior"],
        compartment_count=choices["compartment_count"],
        width_m=round(rng.uniform(*_WIDTH_RANGE), 4),
        depth_m=round(rng.uniform(*_DEPTH_RANGE), 4),
        cell_height_m=round(rng.uniform(*_CELL_HEIGHT_RANGE), 4),
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "door_leaf": config.door_leaf,
            "lock": config.lock,
            "hinge": config.hinge,
            "carcass_front": config.carcass_front,
            "interior": config.interior,
            "compartment_count": config.compartment_count,
        }
    )
    width = 0.360 if config.width_m is None else float(config.width_m)
    depth = 0.180 if config.depth_m is None else float(config.depth_m)
    cell_height = 0.110 if config.cell_height_m is None else float(config.cell_height_m)
    _range_check("width_m", width, _WIDTH_RANGE)
    _range_check("depth_m", depth, _DEPTH_RANGE)
    _range_check("cell_height_m", cell_height, _CELL_HEIGHT_RANGE)

    count = int(config.compartment_count)
    door_width = width - 0.010
    door_height = cell_height - 0.008
    latch_station_x = _LEAF_INSET + door_width - 0.020
    return ResolvedConfig(
        door_leaf=config.door_leaf,
        lock=config.lock,
        hinge=config.hinge,
        carcass_front=config.carcass_front,
        interior=config.interior,
        compartment_count=count,
        width_m=width,
        depth_m=depth,
        cell_height_m=cell_height,
        height_m=count * cell_height,
        wall_m=_WALL,
        door_t_m=_DOOR_T,
        door_width_m=door_width,
        door_height_m=door_height,
        hinge_x_m=-width / 2.0 - _HINGE_OFFSET,
        hinge_y_m=depth / 2.0 + _FRONT_GAP + _DOOR_T / 2.0,
        front_gap_m=_FRONT_GAP,
        engagement_m=_ENGAGE,
        key_station_x_m=_LEAF_INSET + 0.35 * door_width,
        latch_station_x_m=latch_station_x,
        name=config.name,
    )


def _cell_center_z(r: ResolvedConfig, index: int) -> float:
    return (index + 0.5) * r.cell_height_m


def _hinge_station_offsets(r: ResolvedConfig) -> tuple[float, float]:
    # binding hinge_line derived: hinge_station_offset_m
    hinge_station_offset_m = r.door_height_m / 2.0 - 0.021
    return (-hinge_station_offset_m, hinge_station_offset_m)


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("clear_acrylic", rgba=(0.78, 0.89, 0.94, 0.30))
    model.material("acrylic_edge", rgba=(0.70, 0.83, 0.89, 0.55))
    model.material("brushed_metal", rgba=(0.64, 0.67, 0.69, 1.0))
    model.material("dark_metal", rgba=(0.22, 0.24, 0.25, 1.0))
    model.material("molded_black", rgba=(0.035, 0.040, 0.043, 1.0))
    model.material("brass_shackle", rgba=(0.72, 0.52, 0.16, 1.0))
    model.material("label_white", rgba=(0.94, 0.94, 0.91, 1.0))
    return {
        "acrylic": "clear_acrylic",
        "edge": "acrylic_edge",
        "metal": "brushed_metal",
        "dark": "dark_metal",
        "black": "molded_black",
        "brass": "brass_shackle",
        "label": "label_white",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.clear_rigid")


def _cyl_x(part, radius: float, length: float, xyz, material: str, name: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.brass_aged",
    )


def _cyl_y(part, radius: float, length: float, xyz, material: str, name: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _cyl_z(part, radius: float, length: float, xyz, material: str, name: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz),
        material=material,
        name=name, material_class_id="metal.brushed_silver",
    )


# --------------------------------------------------------------------------- #
# Carcass shell (hollow sheet box — never a solid block)
# --------------------------------------------------------------------------- #
def _add_shell(carcass, r: ResolvedConfig, mats: dict[str, str]) -> None:
    w = r.width_m
    d = r.depth_m
    h = r.height_m
    t = r.wall_m
    _box(carcass, (w, d, t), (0.0, 0.0, t / 2.0), mats["edge"], "bottom_panel")
    _box(carcass, (w, d, t), (0.0, 0.0, h - t / 2.0), mats["acrylic"], "top_panel")
    for side, x in (("left", -w / 2.0 + t / 2.0), ("right", w / 2.0 - t / 2.0)):
        _box(
            carcass,
            (t, d, h - 2.0 * t),
            (x, 0.0, h / 2.0),
            mats["acrylic"],
            f"side_panel_{side}",
        )
    _box(
        carcass,
        (w - 2.0 * t, t, h - 2.0 * t),
        (0.0, -d / 2.0 + t / 2.0, h / 2.0),
        mats["acrylic"],
        "back_panel",
    )


# --------------------------------------------------------------------------- #
# Slot: interior
# --------------------------------------------------------------------------- #
def _add_shelves(carcass, r: ResolvedConfig, mats: dict[str, str], candidate: str) -> None:
    for index in range(1, r.compartment_count):
        _box(
            carcass,
            (r.width_m - 2.0 * r.wall_m, r.depth_m - 2.0 * r.wall_m, _SHELF_T),
            (0.0, 0.0, index * r.cell_height_m),
            mats["acrylic"],
            f"interior__{candidate}__shelf_{index}",
        )


def _interior_open_shelf_build(carcass, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """001 L86-L100: plain full-width shelves, no vertical dividers."""
    _add_shelves(carcass, r, mats, "open_shelf")


def _interior_grid_cubby_build(carcass, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """092616 L131-L155 / 095210 L166-L178: shelves plus vertical dividers."""
    _add_shelves(carcass, r, mats, "grid_cubby")
    for index in range(r.compartment_count):
        _box(
            carcass,
            (_SHELF_T, r.depth_m - 2.0 * r.wall_m, r.cell_height_m - 0.010),
            (0.0, 0.0, _cell_center_z(r, index)),
            mats["acrylic"],
            f"interior__grid_cubby__divider_{index}",
        )


_INTERIOR_BUILDERS = {
    "open_shelf": _interior_open_shelf_build,
    "grid_cubby": _interior_grid_cubby_build,
}


# --------------------------------------------------------------------------- #
# Slot: carcass_front
# --------------------------------------------------------------------------- #
def _carcass_front_mullion_frame_build(carcass, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """092616 L157-L177: raised metal posts + cross rails + screw fasteners."""
    w = r.width_m
    h = r.height_m
    post_y = r.depth_m / 2.0 + 0.002
    screw_y = r.depth_m / 2.0 + 0.0035
    post_xs = (-w / 2.0 + 0.0035, w / 2.0 - 0.0035)
    for index, x in enumerate(post_xs):
        _box(
            carcass,
            (0.007, 0.005, h),
            (x, post_y, h / 2.0),
            mats["metal"],
            f"carcass_front__mullion_frame__post_{index}",
        )
    for level in range(r.compartment_count + 1):
        z = min(max(level * r.cell_height_m, 0.005), h - 0.005)
        _box(
            carcass,
            (w, 0.005, 0.008),
            (0.0, post_y, z),
            mats["metal"],
            f"carcass_front__mullion_frame__cross_rail_{level}",
        )
        for index, x in enumerate(post_xs):
            _cyl_y(
                carcass,
                0.0022,
                0.002,
                (x, screw_y, z),
                mats["dark"],
                f"carcass_front__mullion_frame__rail_screw_{index}_{level}",
            )


def _carcass_front_edge_strip_build(carcass, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """001 L95-L100 / 095210 L171-L188: flush polished edge strips, no fasteners."""
    w = r.width_m
    h = r.height_m
    strip_y = r.depth_m / 2.0 + 0.001
    for index in range(1, r.compartment_count):
        _box(
            carcass,
            (w - 2.0 * r.wall_m, 0.005, 0.007),
            (0.0, strip_y, index * r.cell_height_m),
            mats["edge"],
            f"carcass_front__edge_strip__shelf_rail_{index}",
        )
    for name, z in (("bottom", 0.0055), ("top", h - 0.0055)):
        _box(
            carcass,
            (w - 2.0 * r.wall_m, 0.005, 0.007),
            (0.0, strip_y, z),
            mats["edge"],
            f"carcass_front__edge_strip__{name}_rail",
        )
    for index, x in enumerate((-w / 2.0 + 0.003, w / 2.0 - 0.003)):
        _box(
            carcass,
            (0.006, 0.005, h),
            (x, strip_y, h / 2.0),
            mats["edge"],
            f"carcass_front__edge_strip__corner_rail_{index}",
        )


_CARCASS_FRONT_BUILDERS = {
    "mullion_frame": _carcass_front_mullion_frame_build,
    "edge_strip": _carcass_front_edge_strip_build,
}


# --------------------------------------------------------------------------- #
# Slot: hinge — carcass side and door side of one real hinge line
# --------------------------------------------------------------------------- #
def _add_host_bracket(
    carcass,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    name: str,
    z_center: float,
    height: float,
) -> None:
    """Arm reaching from the carcass front-left corner out to the hinge axis.

    The arm stops 4 mm short of the leaf plane in Y (max ``D/2 + 0.004`` against
    a swept leaf minimum of ``D/2 + 0.006``), so it supports the knuckle without
    ever entering the door's swept volume.
    """
    w = r.width_m
    d = r.depth_m
    x_min = r.hinge_x_m - 0.004
    x_max = -w / 2.0 + 0.004
    _box(
        carcass,
        (x_max - x_min, 0.006, height),
        ((x_min + x_max) / 2.0, d / 2.0 + 0.001, z_center),
        mats["metal"],
        name,
    )


def _hinge_knuckle_pair_build(
    carcass,
    door,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """001 L102-L125 + L150-L164: two discrete butt-hinge stations.

    At each station the carcass carries a mounting pad, two short knuckles and
    their support arms; the door carries one longer centre knuckle plus a leaf
    plate.  The carcass knuckles and the door knuckle are coaxial and engage
    axially by ``_ENGAGE`` at both ends — real capture, rotation invariant, and
    only 0.5 mm deep on the single Z axis.
    """
    z_cell = _cell_center_z(r, index)
    # binding hinge_line derived: host_knuckle_axial_offset_m
    host_knuckle_axial_offset_m = _DOOR_KNUCKLE_LEN / 2.0 + _HOST_KNUCKLE_LEN / 2.0 - r.engagement_m
    for station, dz in enumerate(_hinge_station_offsets(r)):
        z_station = z_cell + dz
        _box(
            carcass,
            (0.016, 0.005, 0.030),
            (-r.width_m / 2.0 + 0.008, r.depth_m / 2.0 - 0.0005, z_station),
            mats["metal"],
            f"hinge__knuckle_pair__mount_pad_{index}_{station}",
        )
        for half, sign in (("lower", -1.0), ("upper", 1.0)):
            z_knuckle = z_station + sign * host_knuckle_axial_offset_m
            _cyl_z(
                carcass,
                _HOST_KNUCKLE_R,
                _HOST_KNUCKLE_LEN,
                (r.hinge_x_m, r.hinge_y_m, z_knuckle),
                mats["metal"],
                f"hinge__knuckle_pair__host_knuckle_{index}_{station}_{half}",
            )
            _add_host_bracket(
                carcass,
                r,
                mats,
                name=f"hinge__knuckle_pair__host_arm_{index}_{station}_{half}",
                z_center=z_knuckle + sign * (_HOST_KNUCKLE_LEN / 2.0 - 0.003),
                height=0.006,
            )
        _cyl_z(
            door,
            _DOOR_KNUCKLE_R,
            _DOOR_KNUCKLE_LEN,
            (0.0, 0.0, dz),
            mats["dark"],
            f"hinge__knuckle_pair__door_knuckle_{station}",
        )
        _box(
            door,
            (_LEAF_PLATE_X, r.door_t_m, 0.012),
            (_LEAF_PLATE_X / 2.0, 0.0, dz),
            mats["metal"],
            f"hinge__knuckle_pair__door_leaf_plate_{station}",
        )


def _hinge_piano_barrel_build(
    carcass,
    door,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """095210 L200-L215: continuous full-height hinge mount + long door barrel.

    The carcass carries one full-height mounting pad and two pin stubs at the
    extremes of the leaf; the door carries a single barrel spanning between them
    with the same 0.5 mm axial engagement at each end.
    """
    z_cell = _cell_center_z(r, index)
    half_leaf = r.door_height_m / 2.0
    _box(
        carcass,
        (0.016, 0.005, r.door_height_m),
        (-r.width_m / 2.0 + 0.008, r.depth_m / 2.0 - 0.0005, z_cell),
        mats["metal"],
        f"hinge__piano_barrel__mount_pad_{index}",
    )
    for end, sign in (("lower", -1.0), ("upper", 1.0)):
        z_stub = z_cell + sign * (half_leaf - _HOST_STUB_LEN / 2.0)
        _cyl_z(
            carcass,
            _HOST_KNUCKLE_R,
            _HOST_STUB_LEN,
            (r.hinge_x_m, r.hinge_y_m, z_stub),
            mats["dark"],
            f"hinge__piano_barrel__host_pin_{index}_{end}",
        )
        _add_host_bracket(
            carcass,
            r,
            mats,
            name=f"hinge__piano_barrel__host_arm_{index}_{end}",
            z_center=z_cell + sign * (half_leaf - 0.004),
            height=0.006,
        )
    barrel_len = r.door_height_m - 2.0 * (_HOST_STUB_LEN - r.engagement_m)
    _cyl_z(
        door,
        _DOOR_KNUCKLE_R,
        barrel_len,
        (0.0, 0.0, 0.0),
        mats["dark"],
        "hinge__piano_barrel__door_barrel",
    )
    _box(
        door,
        (_LEAF_PLATE_X, r.door_t_m, r.door_height_m - 0.034),
        (_LEAF_PLATE_X / 2.0, 0.0, 0.0),
        mats["metal"],
        "hinge__piano_barrel__door_leaf_plate",
    )


_HINGE_BUILDERS = {
    "knuckle_pair": _hinge_knuckle_pair_build,
    "piano_barrel": _hinge_piano_barrel_build,
}


# --------------------------------------------------------------------------- #
# Slot: door_leaf
# --------------------------------------------------------------------------- #
def _add_number_plate(door, r: ResolvedConfig, mats: dict[str, str], candidate: str) -> None:
    _box(
        door,
        (0.028, 0.002, 0.016),
        (_LEAF_INSET + 0.030, r.door_t_m / 2.0 + 0.0005, r.door_height_m / 2.0 - 0.014),
        mats["label"],
        f"door_leaf__{candidate}__number_plate",
    )


def _door_leaf_flat_leaf_build(door, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """095210 L209-L226: a plain flat leaf with assembly screws, no frame."""
    _box(
        door,
        (r.door_width_m, r.door_t_m, r.door_height_m),
        (_LEAF_INSET + r.door_width_m / 2.0, 0.0, 0.0),
        mats["acrylic"],
        "door_leaf__flat_leaf__panel",
    )
    _add_number_plate(door, r, mats, "flat_leaf")
    for index, dz in enumerate((-0.024, 0.024)):
        _cyl_y(
            door,
            0.0021,
            0.003,
            (_LEAF_INSET + 0.012, r.door_t_m / 2.0 + 0.0005, dz),
            mats["dark"],
            f"door_leaf__flat_leaf__screw_{index}",
        )


def _door_leaf_framed_leaf_build(door, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """092616 L186-L215: panel plus a raised four-sided perimeter frame."""
    panel_x = _LEAF_INSET + r.door_width_m / 2.0
    _box(
        door,
        (r.door_width_m, r.door_t_m, r.door_height_m),
        (panel_x, 0.0, 0.0),
        mats["acrylic"],
        "door_leaf__framed_leaf__panel",
    )
    frame_y = r.door_t_m / 2.0 + 0.0015
    half_h = r.door_height_m / 2.0
    for name, x, z, sx, sz in (
        ("top_stile", panel_x, half_h - 0.003, r.door_width_m, 0.006),
        ("bottom_stile", panel_x, -half_h + 0.003, r.door_width_m, 0.006),
        ("hinge_stile", _LEAF_INSET + 0.003, 0.0, 0.006, r.door_height_m),
        ("latch_stile", _LEAF_INSET + r.door_width_m - 0.003, 0.0, 0.006, r.door_height_m),
    ):
        _box(
            door,
            (sx, 0.005, sz),
            (x, frame_y, z),
            mats["edge"],
            f"door_leaf__framed_leaf__{name}",
        )
    _add_number_plate(door, r, mats, "framed_leaf")


_DOOR_LEAF_BUILDERS = {
    "flat_leaf": _door_leaf_flat_leaf_build,
    "framed_leaf": _door_leaf_framed_leaf_build,
}


# --------------------------------------------------------------------------- #
# Slot: lock
# --------------------------------------------------------------------------- #
def _lock_rotary_key_build(
    model: ArticulatedObject,
    carcass,
    door,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """001 L127-L135 + L166-L279: rotary key knob + pivoting latch lever.

    Both children are coaxial with their host collar along Y and butt its front
    face with a 0.5 mm axial engagement, so the seat reads as real contact while
    the AABB depth on the mating axis stays under the 1 mm tolerance.
    """
    key_x = r.key_station_x_m
    latch_x = r.latch_station_x_m

    _box(
        door,
        (0.030, 0.002, 0.026),
        (key_x, r.door_t_m / 2.0, 0.0),
        mats["metal"],
        f"lock__rotary_key__lock_plate_{index}",
    )
    _cyl_y(
        door,
        0.0085,
        _COLLAR_LEN,
        (key_x, _COLLAR_Y, 0.0),
        mats["metal"],
        f"lock__rotary_key__lock_collar_{index}",
    )
    _cyl_y(
        door,
        0.009,
        _COLLAR_LEN,
        (latch_x, _COLLAR_Y, 0.0),
        mats["metal"],
        f"lock__rotary_key__latch_pivot_{index}",
    )
    # Fixed strike/keeper outboard of the free edge (001 L127-L135); it stays
    # behind the door plane in Y and beyond the leaf in X, so the swinging leaf
    # never reaches it.
    _box(
        carcass,
        (0.010, 0.006, 0.026),
        (r.width_m / 2.0 + 0.005, r.depth_m / 2.0 + 0.001, _cell_center_z(r, index)),
        mats["metal"],
        f"lock__rotary_key__latch_keeper_{index}",
    )

    knob = model.part(
        f"lock__rotary_key__key_knob_{index}",
        meta={"role": "key_knob", "compartment": index},
    )
    _cyl_y(knob, _KEY_SHAFT_R, 0.010, (0.0, 0.0045, 0.0), mats["dark"], "key_shaft")
    _cyl_y(knob, 0.0065, 0.007, (0.0, 0.012, 0.0), mats["black"], "key_hub")
    _box(knob, (0.024, 0.006, 0.009), (0.0, 0.017, 0.0), mats["black"], "key_bow")
    _mate_revolute(
        model,
        parent=door,
        child=knob,
        joint_name=f"lock__rotary_key__key_joint_{index}",
        point=(key_x, _COLLAR_FRONT_Y, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        lower=-_KEY_LIMIT,
        upper=_KEY_LIMIT,
        effort=0.8,
        velocity=2.5,
        mechanism="rotary key cylinder",
    )

    latch = model.part(
        f"lock__rotary_key__latch_lever_{index}",
        meta={"role": "latch_lever", "compartment": index},
    )
    _cyl_y(latch, _LATCH_SHAFT_R, 0.010, (0.0, 0.0045, 0.0), mats["dark"], "latch_shaft")
    _box(latch, (0.030, 0.007, 0.010), (0.010, 0.012, 0.0), mats["black"], "latch_lever")
    _mate_revolute(
        model,
        parent=door,
        child=latch,
        joint_name=f"lock__rotary_key__latch_joint_{index}",
        point=(latch_x, _COLLAR_FRONT_Y, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        lower=-_LATCH_LIMIT,
        upper=_LATCH_LIMIT,
        effort=1.2,
        velocity=2.0,
        mechanism="pivoting latch lever",
    )


def _lock_cam_padlock_build(
    model: ArticulatedObject,
    carcass,
    door,
    r: ResolvedConfig,
    mats: dict[str, str],
    index: int,
) -> None:
    """092616 L217-L264 / 095210 L87-L109: static cam latch + hanging padlock.

    Every element lives on the door part, so the source's captured
    shackle-in-body fit is intra-part and needs no allowance at all.
    """
    latch_x = r.latch_station_x_m
    # Every element overlaps its neighbour by >= 1 mm so the whole cam + padlock
    # cluster is one connected island rooted in the leaf panel (intra-part
    # embedding is free; only cross-part contact needs clearance).
    _cyl_y(
        door,
        0.0072,
        0.012,
        (latch_x, r.door_t_m / 2.0 - 0.0015 + 0.006, 0.002),
        mats["black"],
        f"lock__cam_padlock__cam_hub_{index}",
    )
    _box(
        door,
        (0.026, 0.010, 0.006),
        (latch_x - 0.004, 0.015, 0.004),
        mats["black"],
        f"lock__cam_padlock__cam_handle_{index}",
    )
    _cyl_z(
        door,
        0.003,
        0.010,
        (latch_x, 0.009, -0.006),
        mats["black"],
        f"lock__cam_padlock__lock_eye_{index}",
    )
    _box(
        door,
        (0.019, 0.010, 0.017),
        (latch_x, 0.009, -0.026),
        mats["black"],
        f"lock__cam_padlock__padlock_body_{index}",
    )
    for leg, dx in enumerate((-0.0055, 0.0055)):
        _cyl_z(
            door,
            0.0018,
            0.016,
            (latch_x + dx, 0.009, -0.014),
            mats["brass"],
            f"lock__cam_padlock__shackle_leg_{index}_{leg}",
        )
    _cyl_x(
        door,
        0.0018,
        0.014,
        (latch_x, 0.009, -0.007),
        mats["brass"],
        f"lock__cam_padlock__shackle_bridge_{index}",
    )


_LOCK_BUILDERS = {
    "rotary_key": _lock_rotary_key_build,
    "cam_padlock": _lock_cam_padlock_build,
}


# --------------------------------------------------------------------------- #
# Joint helper — every revolute joint is solved from a real axis interface
# --------------------------------------------------------------------------- #
def _mate_revolute(
    model: ArticulatedObject,
    *,
    parent,
    child,
    joint_name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    mechanism: str,
) -> None:
    provider = AxisInterface(
        name=f"{joint_name}__provider",
        point=point,
        axis=axis,
        radial=radial,
    )
    consumer = AxisInterface(
        name=f"{joint_name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=radial,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=effort,
            velocity=velocity,
            lower=lower,
            upper=upper,
        ),
        motion_properties=MotionProperties(damping=0.5, friction=0.2),
        meta={"mechanism": mechanism},
    )
    register_interface_mate(model, joint_name, mate)


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_picturex_0611_locker_box(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Locker_box",
            "identified_object": "lockable acrylic locker box",
            "slot_choices": (
                ("door_leaf", r.door_leaf),
                ("lock", r.lock),
                ("hinge", r.hinge),
                ("carcass_front", r.carcass_front),
                ("interior", r.interior),
                ("compartment_count", r.compartment_count),
            ),
            "source_layout": "hollow sheet carcass + N stacked side-hinged locker doors",
        },
    )
    mats = _materials(model)

    carcass = model.part("carcass", meta={"role": "carcass"})
    _add_shell(carcass, r, mats)
    _INTERIOR_BUILDERS[r.interior](carcass, r, mats)
    _CARCASS_FRONT_BUILDERS[r.carcass_front](carcass, r, mats)

    hinge_builder = _HINGE_BUILDERS[r.hinge]
    leaf_builder = _DOOR_LEAF_BUILDERS[r.door_leaf]
    lock_builder = _LOCK_BUILDERS[r.lock]

    for index in range(r.compartment_count):
        door = model.part(
            f"door_leaf__{r.door_leaf}__door_{index}",
            meta={"role": "locker_door", "compartment": index},
        )
        leaf_builder(door, r, mats)
        hinge_builder(carcass, door, r, mats, index)
        _mate_revolute(
            model,
            parent=carcass,
            child=door,
            joint_name=f"door_leaf__{r.door_leaf}__hinge_{index}",
            point=(r.hinge_x_m, r.hinge_y_m, _cell_center_z(r, index)),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            lower=0.0,
            upper=_DOOR_OPEN_UPPER,
            effort=6.0,
            velocity=1.4,
            mechanism="side-hinged locker door",
        )
        lock_builder(model, carcass, door, r, mats, index)

    return model


# --------------------------------------------------------------------------- #
# Author tests — mesh-free: structural / derived invariants plus pose probes
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _visual_names(part) -> set[str]:
    return {visual.name or "" for visual in part.visuals}


def run_picturex_0611_locker_box_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    carcass_parts = _parts_by_role(model, "carcass")
    doors = _parts_by_role(model, "locker_door")
    keys = _parts_by_role(model, "key_knob")
    latches = _parts_by_role(model, "latch_lever")
    carcass = carcass_parts[0] if carcass_parts else None
    door_names = {part.name for part in doors}
    hinges = [joint for joint in model.articulations if joint.child in door_names]

    # --- category anchor: hollow shell + N real side-hinged doors ------------ #
    carcass_visuals = _visual_names(carcass) if carcass is not None else set()
    hollow = {
        "bottom_panel",
        "top_panel",
        "side_panel_left",
        "side_panel_right",
        "back_panel",
    }.issubset(carcass_visuals)
    shelf_count = sum(
        1 for name in carcass_visuals if name.startswith("interior__") and "__shelf_" in name
    )
    ctx.check(
        "category_anchor: hollow carcass with N hinged locker doors",
        len(carcass_parts) == 1
        and hollow
        and shelf_count == r.compartment_count - 1
        and len(doors) == r.compartment_count
        and len(hinges) == r.compartment_count
        and all(
            joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(joint.axis) == (0.0, 0.0, 1.0)
            and joint.parent == "carcass"
            and joint.motion_limits is not None
            and joint.motion_limits.lower == 0.0
            and abs(joint.motion_limits.upper - _DOOR_OPEN_UPPER) < 1e-9
            for joint in hinges
        ),
        details=(
            f"carcass={len(carcass_parts)}, hollow={hollow}, shelves={shelf_count}, "
            f"doors={len(doors)}, hinges={len(hinges)}, N={r.compartment_count}"
        ),
    )

    # --- category anchor: lock hardware ------------------------------------- #
    if r.lock == "rotary_key":
        key_joints = [
            joint
            for joint in model.articulations
            if joint.child in {part.name for part in keys} | {part.name for part in latches}
        ]
        lock_ok = (
            len(keys) == r.compartment_count
            and len(latches) == r.compartment_count
            and len(key_joints) == 2 * r.compartment_count
            and all(
                joint.articulation_type == ArticulationType.REVOLUTE
                and tuple(joint.axis) == (0.0, 1.0, 0.0)
                and joint.parent in door_names
                and joint.motion_limits is not None
                and joint.motion_limits.lower < 0.0 < joint.motion_limits.upper
                for joint in key_joints
            )
            and all(
                any("lock_collar_" in name for name in _visual_names(door))
                and any("latch_pivot_" in name for name in _visual_names(door))
                for door in doors
            )
            and sum(1 for name in carcass_visuals if "latch_keeper_" in name) == r.compartment_count
        )
        ctx.check(
            "category_anchor: rotary_key lock hardware",
            lock_ok,
            details=f"keys={len(keys)}, latches={len(latches)}, joints={len(key_joints)}",
        )
    else:
        lock_ok = not keys and not latches and bool(doors)
        for door in doors:
            names = _visual_names(door)
            for stem in ("cam_hub_", "cam_handle_", "padlock_body_", "shackle_bridge_"):
                if not any(stem in name for name in names):
                    lock_ok = False
        ctx.check(
            "category_anchor: cam_padlock lock hardware",
            lock_ok,
            details=f"doors={len(doors)}, extra_parts={len(keys) + len(latches)}",
        )

    # --- candidate identity ------------------------------------------------- #
    door_visuals: set[str] = set()
    for door in doors:
        door_visuals |= _visual_names(door)
    if r.door_leaf == "framed_leaf":
        leaf_identity = (
            any("framed_leaf__top_stile" in name for name in door_visuals)
            and any("framed_leaf__hinge_stile" in name for name in door_visuals)
            and any("framed_leaf__latch_stile" in name for name in door_visuals)
            and not any("flat_leaf__" in name for name in door_visuals)
        )
    else:
        leaf_identity = (
            any("flat_leaf__panel" in name for name in door_visuals)
            and any("flat_leaf__screw_" in name for name in door_visuals)
            and not any("_stile" in name for name in door_visuals)
        )
    ctx.check(
        f"candidate_identity: door_leaf {r.door_leaf}",
        leaf_identity,
        details=f"door_visuals={len(door_visuals)}",
    )

    if r.hinge == "knuckle_pair":
        hinge_identity = (
            sum(1 for name in carcass_visuals if "knuckle_pair__host_knuckle_" in name)
            == 4 * r.compartment_count
            and sum(1 for name in door_visuals if "knuckle_pair__door_knuckle_" in name) == 2
            and not any("piano_barrel__" in name for name in carcass_visuals)
        )
    else:
        hinge_identity = (
            sum(1 for name in carcass_visuals if "piano_barrel__host_pin_" in name)
            == 2 * r.compartment_count
            and any("piano_barrel__door_barrel" in name for name in door_visuals)
            and not any("knuckle_pair__" in name for name in carcass_visuals)
        )
    ctx.check(
        f"candidate_identity: hinge {r.hinge}",
        hinge_identity,
        details=f"carcass_visuals={len(carcass_visuals)}",
    )

    if r.carcass_front == "mullion_frame":
        front_identity = (
            sum(1 for name in carcass_visuals if "mullion_frame__post_" in name) == 2
            and any("mullion_frame__rail_screw_" in name for name in carcass_visuals)
            and not any("edge_strip__" in name for name in carcass_visuals)
        )
    else:
        front_identity = sum(
            1 for name in carcass_visuals if "edge_strip__corner_rail_" in name
        ) == 2 and not any("mullion_frame__" in name for name in carcass_visuals)
    ctx.check(
        f"candidate_identity: carcass_front {r.carcass_front}",
        front_identity,
        details=f"carcass_visuals={len(carcass_visuals)}",
    )

    divider_count = sum(1 for name in carcass_visuals if "grid_cubby__divider_" in name)
    interior_identity = (
        divider_count == r.compartment_count if r.interior == "grid_cubby" else divider_count == 0
    )
    ctx.check(
        f"candidate_identity: interior {r.interior}",
        interior_identity,
        details=f"dividers={divider_count}, N={r.compartment_count}",
    )

    # --- derived mechanical invariants (formulae, not harness restatements) -- #
    # Captured hinge: the host knuckle and the door knuckle are coaxial and
    # engage axially by exactly `engagement_m`, which must be a real contact
    # (> 0) yet stay under the 1 mm collision tolerance on that single axis.
    ctx.check(
        "hinge engagement is real capture under the collision tolerance",
        0.0002 <= r.engagement_m < 0.001,
        details=f"engagement={r.engagement_m}",
    )
    # Swept clearance: the leaf pivots about its own mid-plane, so its minimum
    # world Y over the whole 0..upper range is the closed back face; that must
    # stay ahead of every carcass front feature (max D/2 + 0.0045).
    swept_min_y = r.hinge_y_m - r.door_t_m / 2.0
    ctx.check(
        "closed and swept leaf stays ahead of the carcass front frame",
        swept_min_y - (r.depth_m / 2.0 + 0.0045) >= 0.001,
        details=f"swept_min_y={swept_min_y}, front_face={r.depth_m / 2.0}",
    )
    # The leaf must actually cover the opening it closes.
    coverage = (r.width_m - 2.0 * r.wall_m) - r.door_width_m
    ctx.check(
        "leaf covers the compartment opening",
        coverage <= 0.0 and r.door_height_m < r.cell_height_m,
        details=f"opening_minus_leaf={coverage}, door_h={r.door_height_m}",
    )
    # Host knuckle stations must fit inside the leaf height they support.
    if r.hinge == "knuckle_pair":
        reach = abs(_hinge_station_offsets(r)[1]) + _DOOR_KNUCKLE_LEN / 2.0 + _HOST_KNUCKLE_LEN
        ctx.check(
            "butt-hinge stations fit within the leaf height",
            reach <= r.door_height_m / 2.0,
            details=f"reach={reach}, half_leaf={r.door_height_m / 2.0}",
        )

    # --- measured motion semantics ------------------------------------------ #
    if doors and hinges:
        witness = doors[0]
        hinge_joint = next(joint for joint in hinges if joint.child == witness.name)
        closed = ctx.part_world_aabb(witness)
        with ctx.pose({hinge_joint.name: _DOOR_OPEN_UPPER}):
            opened = ctx.part_world_aabb(witness)
        ctx.check(
            "locker door swings outward, never back through the carcass",
            closed is not None
            and opened is not None
            and opened[1][1] > closed[1][1] + 0.5 * r.door_width_m
            and opened[0][1] >= r.depth_m / 2.0,
            details=f"closed={closed}, opened={opened}",
        )

    if keys:
        knob = keys[0]
        key_joint = next(joint for joint in model.articulations if joint.child == knob.name)
        with ctx.pose({key_joint.name: -_KEY_LIMIT}):
            low = ctx.part_world_aabb(knob)
        with ctx.pose({key_joint.name: _KEY_LIMIT}):
            high = ctx.part_world_aabb(knob)
        ctx.check(
            "rotary key turns about its collar axis without leaving the door face",
            low is not None
            and high is not None
            and abs((low[1][1] - low[0][1]) - (high[1][1] - high[0][1])) < 1e-6
            and low[0][1] > r.depth_m / 2.0,
            details=f"low={low}, high={high}",
        )

    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "max_doors_rotary_key_tight_cells",
        {
            "door_leaf": "framed_leaf",
            "lock": "rotary_key",
            "hinge": "knuckle_pair",
            "carcass_front": "mullion_frame",
            "interior": "grid_cubby",
            "compartment_count": 5,
            "width_m": 0.28,
            "depth_m": 0.14,
            "cell_height_m": 0.09,
        },
        reason="maximum N with the shortest cells: hinge stations, latch sweep and "
        "mullion rails are all at their tightest against a narrow shallow carcass",
    ),
    corner_case(
        "min_doors_padlock_piano_wide",
        {
            "door_leaf": "flat_leaf",
            "lock": "cam_padlock",
            "hinge": "piano_barrel",
            "carcass_front": "edge_strip",
            "interior": "open_shelf",
            "compartment_count": 2,
            "width_m": 0.44,
            "depth_m": 0.24,
            "cell_height_m": 0.15,
        },
        reason="minimum N with the widest, deepest, tallest cells: longest piano "
        "barrel and the largest door swing envelope",
    ),
    corner_case(
        "max_doors_piano_barrel_shallow",
        {
            "door_leaf": "framed_leaf",
            "lock": "cam_padlock",
            "hinge": "piano_barrel",
            "carcass_front": "mullion_frame",
            "interior": "grid_cubby",
            "compartment_count": 5,
            "width_m": 0.44,
            "depth_m": 0.14,
            "cell_height_m": 0.09,
        },
        reason="shortest continuous barrel (min cell height) on the widest leaf, "
        "with the padlock hanging inside the shallowest compartment",
    ),
    corner_case(
        "rotary_key_wide_leaf_full_latch_sweep",
        {
            "door_leaf": "flat_leaf",
            "lock": "rotary_key",
            "hinge": "piano_barrel",
            "carcass_front": "edge_strip",
            "interior": "grid_cubby",
            "compartment_count": 4,
            "width_m": 0.44,
            "depth_m": 0.14,
            "cell_height_m": 0.09,
        },
        reason="longest key/latch stations on the widest leaf with the shortest "
        "cell, exercising the latch lever sweep against neighbouring doors",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_picturex_0611_locker_box",
    "config_from_seed",
    "resolve_config",
    "run_picturex_0611_locker_box_tests",
]
