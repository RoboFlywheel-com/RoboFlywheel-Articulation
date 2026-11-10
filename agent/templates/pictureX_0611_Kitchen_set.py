# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained installed kitchen set template.

One fixed ``kitchen_carcass`` root (toe kick, base run with N bays, shallow upper
run, stone countertop with real sink/cooktop through-cutouts, sink basin, cooktop,
backsplash, faucet, and a full-height tall feature on the left), plus N revolute
upper ``cabinet_door`` fronts and N prismatic ``base_drawer`` trays.

Structural slots (source-derived, freely combinable):
  * door_style:   framed_panel | slab
  * drawer_style: runner_tray  | reveal_tray
  * tower_style:  appliance_tower | open_shelf_tower
Multiplicity: bay_count in 2..5 drives drawers, doors, dividers and gables.

Frame: +X along the wall, +Y toward the viewer, +Z up.  The carcass back is at -Y.
Doors swing toward +Y about a vertical hinge; drawers pull toward +Y.

No source runtime is imported; only stdlib, cadquery, and the SDK are used.  No
motion clamping and no overlap allowance: captured contacts are real geometry kept
under the collision tolerance.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

DoorStyle = Literal["framed_panel", "slab"]
DrawerStyle = Literal["runner_tray", "reveal_tray"]
TowerStyle = Literal["appliance_tower", "open_shelf_tower"]
IslandModule = Literal["waterfall_peninsula", "open_cubby_return"]

DOOR_STYLES: tuple[DoorStyle, ...] = ("framed_panel", "slab")
DRAWER_STYLES: tuple[DrawerStyle, ...] = ("runner_tray", "reveal_tray")
TOWER_STYLES: tuple[TowerStyle, ...] = ("appliance_tower", "open_shelf_tower")
ISLAND_MODULES: tuple[IslandModule, ...] = ("waterfall_peninsula", "open_cubby_return")
BAY_COUNTS: tuple[int, ...] = (2, 3, 4, 5)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("door_style", DOOR_STYLES),
        component_slot("drawer_style", DRAWER_STYLES),
        component_slot("tower_style", TOWER_STYLES),
        component_slot("island_module", ISLAND_MODULES),
        multiplicity_slot("bay_count", BAY_COUNTS, item_slot="drawer_style"),
    )
)

# Continuous parameter bounds (m).  Continuous dimensions do not inflate core/raw.
_BAY_WIDTH_MIN, _BAY_WIDTH_MAX = 0.50, 0.75
_COUNTER_DEPTH_MIN, _COUNTER_DEPTH_MAX = 0.55, 0.66
_BASE_HEIGHT_MIN, _BASE_HEIGHT_MAX = 0.82, 0.92

# Fixed cross-section constants (surface detail, not core/raw).
_TOE_H = 0.10            # toe-kick height
_PANEL_T = 0.018         # carcass sheet thickness
_COUNTER_T = 0.040       # stone counter slab
_FRONT_T = 0.019         # door / drawer front thickness
# Gap between adjacent fronts.  A door pivoting about its back face sweeps a
# quarter-circle whose radius is the leaf thickness, so at 90 deg its trailing
# corner reaches _FRONT_T to the hinge side.  The reveal must exceed that or
# every door clips its neighbour -- and door 0 clips the full-depth tall tower.
# Paired with the 90 deg swing limit below (past 90 the leaf tip itself swings
# back over the neighbour, which no reveal can absorb).  At 8 mm the residual
# neighbour overlap is _FRONT_T - 2*_REVEAL = 3 mm, inside the 5 mm collision
# tolerance, while the leaf and its knuckles still lap the gable so the door
# reads as carried by the carcass rather than an isolated part.
_REVEAL = 0.008
_BACKSPLASH_H = 0.52     # counter top -> upper run bottom
_UPPER_H = 0.72          # upper cabinet run height
_UPPER_DEPTH = 0.33      # shallow upper run depth
_TOWER_W = 0.62          # tall left feature width
_BASIN_H = 0.20          # sink bowl depth below the counter
# Captured contact: fronts lap their host by less than the collision tolerance,
# so QC reads real contact without needing an overlap allowance.
_MOUNT = 0.0006
# Door leaves pivot about their BACK face: every leaf element is offset half a
# thickness forward of the hinge plane.  Centring the leaf on the axis instead
# swept 9.5 mm of it backward through the carcass gable at every open angle.
_LEAF_Y = 0.5 * 0.019
_MESH_TOL = 0.0012
_MESH_ANG_TOL = 0.16


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    door_style: DoorStyle = "framed_panel"
    drawer_style: DrawerStyle = "runner_tray"
    tower_style: TowerStyle = "appliance_tower"
    island_module: IslandModule = "waterfall_peninsula"
    bay_count: int = 4
    bay_width_m: float | None = None
    counter_depth_m: float | None = None
    base_height_m: float | None = None
    name: str = "pictureX_0611_Kitchen_set"


@dataclass(frozen=True)
class ResolvedConfig:
    door_style: DoorStyle
    drawer_style: DrawerStyle
    tower_style: TowerStyle
    island_module: IslandModule
    bay_count: int
    bay_width_m: float
    counter_depth_m: float
    base_height_m: float
    run_width_m: float
    tower_x0: float
    front_width_m: float
    drawer_front_h: float
    sink_drawer_front_h: float
    drawer_box_depth: float
    drawer_travel: float
    door_h: float
    upper_z0: float
    name: str

    @property
    def assembly_center_x(self) -> float:
        return self.tower_x0 + 0.5 * (_TOWER_W + self.run_width_m)

    def bay_center_x(self, index: int) -> float:
        """Centre X of base/upper bay `index`, left to right along the wall."""
        return self.tower_x0 + _TOWER_W + (index + 0.5) * self.bay_width_m


def _bay_drawer_geometry(r: "ResolvedConfig", index: int) -> tuple[float, float]:
    """Return (front_height, front_top_z) for the drawer in bay `index`.

    Bay 0 carries the sink, so its drawer is shorter and tops out beneath the
    bowl; every other bay runs full height up to the counter underside.
    """
    if index == 0:
        top_z = r.base_height_m - _COUNTER_T - _BASIN_H - _REVEAL
        return r.sink_drawer_front_h, top_z
    return r.drawer_front_h, r.base_height_m - _COUNTER_T - _REVEAL


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x4B17_C5E7)
    return Config(
        door_style=choices["door_style"],
        drawer_style=choices["drawer_style"],
        tower_style=choices["tower_style"],
        island_module=choices["island_module"],
        bay_count=choices["bay_count"],
        bay_width_m=round(rng.uniform(_BAY_WIDTH_MIN, _BAY_WIDTH_MAX), 4),
        counter_depth_m=round(rng.uniform(_COUNTER_DEPTH_MIN, _COUNTER_DEPTH_MAX), 4),
        base_height_m=round(rng.uniform(_BASE_HEIGHT_MIN, _BASE_HEIGHT_MAX), 4),
        name=f"pictureX_0611_Kitchen_set_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "door_style": cfg.door_style,
            "drawer_style": cfg.drawer_style,
            "tower_style": cfg.tower_style,
            "island_module": cfg.island_module,
            "bay_count": cfg.bay_count,
        }
    )
    bay_width = _clamp(
        0.62 if cfg.bay_width_m is None else cfg.bay_width_m, _BAY_WIDTH_MIN, _BAY_WIDTH_MAX
    )
    counter_depth = _clamp(
        0.60 if cfg.counter_depth_m is None else cfg.counter_depth_m,
        _COUNTER_DEPTH_MIN,
        _COUNTER_DEPTH_MAX,
    )
    base_height = _clamp(
        0.88 if cfg.base_height_m is None else cfg.base_height_m,
        _BASE_HEIGHT_MIN,
        _BASE_HEIGHT_MAX,
    )
    bay_count = int(cfg.bay_count)
    run_width = bay_count * bay_width
    total_w = _TOWER_W + run_width
    tower_x0 = -0.5 * total_w
    front_width = bay_width - 2.0 * _REVEAL
    # Clear span between the carcass floor's top face and the counter's
    # underside, less a reveal at each end.  Omitting the floor thickness made
    # the front _PANEL_T too tall and it drove straight into the countertop.
    drawer_front_h = base_height - _TOE_H - _COUNTER_T - _PANEL_T - 2.0 * _REVEAL
    # The sink bay's bowl hangs _BASIN_H below the counter and occupies the top
    # of that bay, so its drawer is derived to fit UNDER the bowl.  A fixed false
    # front on the carcass fills the leftover height, exactly as a real sink
    # cabinet does -- every bay still gets one working drawer.
    basin_bottom_z = base_height - _COUNTER_T - _BASIN_H
    sink_drawer_front_h = basin_bottom_z - (_TOE_H + _PANEL_T) - 2.0 * _REVEAL
    # Hollow tray: clearance at the front face and behind the box.
    drawer_box_depth = counter_depth - 0.055
    # Travel keeps the tray retained: it never fully leaves the carcass.
    drawer_travel = 0.62 * drawer_box_depth
    upper_z0 = base_height + _BACKSPLASH_H
    door_h = _UPPER_H - 2.0 * _REVEAL
    return ResolvedConfig(
        door_style=cfg.door_style,
        drawer_style=cfg.drawer_style,
        tower_style=cfg.tower_style,
        island_module=cfg.island_module,
        bay_count=bay_count,
        bay_width_m=bay_width,
        counter_depth_m=counter_depth,
        base_height_m=base_height,
        run_width_m=run_width,
        tower_x0=tower_x0,
        front_width_m=front_width,
        drawer_front_h=drawer_front_h,
        sink_drawer_front_h=sink_drawer_front_h,
        drawer_box_depth=drawer_box_depth,
        drawer_travel=drawer_travel,
        door_h=door_h,
        upper_z0=upper_z0,
        name=cfg.name,
    )


def slot_choices_for_config(r: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("door_style", r.door_style),
        ("drawer_style", r.drawer_style),
        ("tower_style", r.tower_style),
        ("island_module", r.island_module),
        ("bay_count", r.bay_count),
    )


# ---------------------------------------------------------------------------
# Materials / helpers
# ---------------------------------------------------------------------------
def _materials(model: ArticulatedObject) -> dict[str, str]:
    spec = {
        "cabinet": (0.42, 0.45, 0.40, 1.0),
        "front": (0.51, 0.54, 0.47, 1.0),
        "stone": (0.86, 0.86, 0.84, 1.0),
        "splash": (0.90, 0.89, 0.86, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "dark": (0.13, 0.13, 0.14, 1.0),
        "glass": (0.20, 0.24, 0.26, 1.0),
        "charcoal": (0.22, 0.23, 0.24, 1.0),
    }
    out: dict[str, str] = {}
    for key, rgba in spec.items():
        model.material(key, color=rgba)
        out[key] = key
    return out


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.engineered_board")


# ---------------------------------------------------------------------------
# Countertop: characteristic cadquery slab with real through-cutouts
# ---------------------------------------------------------------------------
def _counter_geom(r: ResolvedConfig, sink_dx: float, hob_dx: float):
    width = _TOWER_W + r.run_width_m
    depth = r.counter_depth_m
    slab = cq.Workplane("XY").box(width, depth, _COUNTER_T)
    sink_w = min(0.52, r.bay_width_m - 0.10)
    sink_d = min(0.40, depth - 0.16)
    slab = slab.cut(
        cq.Workplane("XY").center(sink_dx, -0.02).box(sink_w, sink_d, _COUNTER_T * 3.0)
    )
    hob_w = min(0.56, r.bay_width_m - 0.08)
    hob_d = min(0.44, depth - 0.14)
    slab = slab.cut(
        cq.Workplane("XY").center(hob_dx, -0.02).box(hob_w, hob_d, _COUNTER_T * 3.0)
    )
    # Eased front arris: the stone's read-at-a-glance profile.
    slab = slab.edges("|X and >Y").chamfer(0.004)
    return slab


# ---------------------------------------------------------------------------
# Tall left feature (tower_style slot)
# ---------------------------------------------------------------------------
def _tower_common(part, r: ResolvedConfig, mats, cand: str) -> tuple[float, float, float]:
    cx = r.tower_x0 + 0.5 * _TOWER_W
    depth = r.counter_depth_m
    height = r.upper_z0 + _UPPER_H
    # The tower is full counter depth up to the worktop and steps back to the
    # shallow upper-run depth above it -- exactly like a real tall unit beside a
    # wall run.  A full-depth upper section would stand 0.27 m proud of the
    # uppers and the adjacent cabinet door would swing straight into it.
    step_z = r.base_height_m
    lower_h = step_z - _TOE_H
    upper_h = height - step_z
    upper_y = -0.5 * depth + 0.5 * _UPPER_DEPTH
    for i, sx in enumerate((-1.0, 1.0)):
        gx = cx + sx * (0.5 * _TOWER_W - 0.5 * _PANEL_T)
        _box(part, (_PANEL_T, depth, lower_h), (gx, 0.0, _TOE_H + 0.5 * lower_h), mats["cabinet"], f"tower_style__{cand}__gable_{i}")
        _box(part, (_PANEL_T, _UPPER_DEPTH, upper_h), (gx, upper_y, step_z + 0.5 * upper_h), mats["cabinet"], f"tower_style__{cand}__upper_gable_{i}")
    _box(part, (_TOWER_W, _UPPER_DEPTH, _PANEL_T), (cx, upper_y, height - 0.5 * _PANEL_T), mats["cabinet"], f"tower_style__{cand}__top")
    _box(
        part,
        (_TOWER_W, _PANEL_T, height - _TOE_H),
        (cx, -0.5 * depth + 0.5 * _PANEL_T, _TOE_H + 0.5 * (height - _TOE_H)),
        mats["cabinet"],
        f"tower_style__{cand}__back",
    )
    _box(part, (_TOWER_W, _UPPER_DEPTH, _PANEL_T), (cx, upper_y, step_z + 0.5 * _PANEL_T), mats["cabinet"], f"tower_style__{cand}__step_shelf")
    _box(
        part,
        (_TOWER_W - 2.0 * _PANEL_T, depth - 0.06, _TOE_H + 0.004),
        (cx, 0.03, 0.5 * (_TOE_H + 0.004)),
        mats["dark"],
        f"tower_style__{cand}__toe_kick",
    )
    return cx, depth, height


def _tower_style_appliance_tower_build(part, r: ResolvedConfig, mats) -> None:
    """Closed full-height tower with an integrated oven chassis (source 002)."""
    cand = "appliance_tower"
    cx, depth, height = _tower_common(part, r, mats, cand)
    inner_w = _TOWER_W - 2.0 * _PANEL_T
    oven_z0 = r.base_height_m - 0.02
    oven_h = 0.60
    front_y = 0.5 * depth - 0.5 * _PANEL_T
    lower_h = oven_z0 - _TOE_H
    _box(part, (inner_w, _PANEL_T, lower_h), (cx, front_y, _TOE_H + 0.5 * lower_h), mats["front"], f"tower_style__{cand}__lower_front")
    upper_h = height - (oven_z0 + oven_h) - _PANEL_T
    if upper_h > 0.02:
        _box(part, (inner_w, _PANEL_T, upper_h), (cx, front_y, oven_z0 + oven_h + 0.5 * upper_h), mats["front"], f"tower_style__{cand}__upper_front")
    # Oven chassis recessed into the bay, glass + control + handle.
    _box(part, (inner_w - 0.01, 0.07, oven_h), (cx, 0.5 * depth - 0.035, oven_z0 + 0.5 * oven_h), mats["dark"], f"tower_style__{cand}__oven_chassis")
    _box(part, (inner_w - 0.09, 0.014, oven_h - 0.20), (cx, 0.5 * depth - 0.004, oven_z0 + 0.5 * oven_h - 0.03), mats["glass"], f"tower_style__{cand}__oven_glass")
    _box(part, (inner_w - 0.05, 0.016, 0.055), (cx, 0.5 * depth - 0.004, oven_z0 + oven_h - 0.045), mats["charcoal"], f"tower_style__{cand}__oven_control")
    part.visual(
        Cylinder(radius=0.011, length=inner_w - 0.07),
        origin=Origin(xyz=(cx, 0.5 * depth + 0.006, oven_z0 + oven_h - 0.115), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name=f"tower_style__{cand}__oven_handle", material_class_id="metal.brushed_silver",
    )
    for i in range(2):
        z = oven_z0 + oven_h + 0.16 + i * 0.24
        if z < height - 0.06:
            _box(part, (inner_w, depth - 0.05, _PANEL_T), (cx, 0.01, z), mats["cabinet"], f"tower_style__{cand}__shelf_{i}")


def _tower_style_open_shelf_tower_build(part, r: ResolvedConfig, mats) -> None:
    """Open full-height shelving tower with a ribbed back (source 003)."""
    cand = "open_shelf_tower"
    cx, depth, height = _tower_common(part, r, mats, cand)
    inner_w = _TOWER_W - 2.0 * _PANEL_T
    back_h = height - _TOE_H - 0.02
    _box(
        part,
        (inner_w, 0.012, back_h),
        (cx, -0.5 * depth + _PANEL_T + 0.004, _TOE_H + 0.5 * back_h),
        mats["charcoal"],
        f"tower_style__{cand}__rib_backing",
    )
    rib_count = 7
    rib_h = height - _TOE_H - 0.06
    for i in range(rib_count):
        rx = cx + (i - (rib_count - 1) * 0.5) * (inner_w / rib_count)
        _box(
            part,
            (0.012, 0.016, rib_h),
            (rx, -0.5 * depth + _PANEL_T + 0.014, _TOE_H + 0.5 * rib_h),
            mats["charcoal"],
            f"tower_style__{cand}__rib_{i}",
        )
    shelf_count = 5
    span = height - _TOE_H - 0.12
    for i in range(shelf_count):
        z = _TOE_H + 0.10 + (i + 1) * span / (shelf_count + 1)
        _box(part, (inner_w, depth - 0.04, _PANEL_T), (cx, 0.01, z), mats["cabinet"], f"tower_style__{cand}__shelf_{i}")


_TOWER_BUILDERS = {
    "appliance_tower": _tower_style_appliance_tower_build,
    "open_shelf_tower": _tower_style_open_shelf_tower_build,
}


# ---------------------------------------------------------------------------
# Doors (door_style slot).  Local origin sits ON the hinge axis; the leaf spans
# +x toward the swing edge so mate_axes places it against the gable.
# ---------------------------------------------------------------------------
def _door_hinge_hardware(part, r: ResolvedConfig, mats, index: int, cand: str) -> None:
    """Hinge knuckles centred ON the hinge axis, shared by both door styles.

    They sit at local x=0 so they stay engaged with the gable at every swing
    angle -- without them a fully-open door touches nothing and QC reports the
    leaf as an isolated part.  Hinge hardware is common to both fronts; the style
    distinction lives in the frame/panel vs slab/reveal geometry.
    """
    h = r.door_h
    # The leaf's back face sits `_FRONT_T/2 - _MOUNT` behind the axis, so the
    # gable's front face is at axis_y - (_FRONT_T/2 - _MOUNT).  A knuckle centred
    # on the axis therefore only needs that radius plus _MOUNT to seat on the
    # gable; at 13 mm it speared the gable and reached the neighbouring door.
    # The small +x offset keeps it clear of the neighbour's leaf while staying
    # within the gable's x footprint at every swing angle.
    knuckle_r = 0.0035
    for i, kz in enumerate((-0.5 * h + 0.075, 0.5 * h - 0.075)):
        part.visual(
            Cylinder(radius=knuckle_r, length=0.052),
            origin=Origin(xyz=(0.002, 0.0, kz)),
            material=mats["dark"],
            name=f"door_style__{cand}__knuckle_{index}_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _door_style_framed_panel_build(part, r: ResolvedConfig, mats, index: int) -> None:
    """Perimeter-framed panel door with hinge knuckles (source 002)."""
    cand = "framed_panel"
    w, h = r.front_width_m, r.door_h
    rail = min(0.075, 0.28 * w)
    _box(part, (w, _FRONT_T, rail), (0.5 * w, _LEAF_Y, 0.5 * h - 0.5 * rail), mats["front"], f"door_style__{cand}__top_rail_{index}")
    _box(part, (w, _FRONT_T, rail), (0.5 * w, _LEAF_Y, -0.5 * h + 0.5 * rail), mats["front"], f"door_style__{cand}__bottom_rail_{index}")
    for i, sx in enumerate((0.0, 1.0)):
        _box(
            part,
            (rail, _FRONT_T, h - 2.0 * rail),
            (0.5 * rail + sx * (w - rail), _LEAF_Y, 0.0),
            mats["front"],
            f"door_style__{cand}__stile_{index}_{i}",
        )
    _box(
        part,
        (w - 2.0 * rail, _FRONT_T * 0.55, h - 2.0 * rail),
        (0.5 * w, _LEAF_Y - _FRONT_T * 0.2, 0.0),
        mats["front"],
        f"door_style__{cand}__centre_panel_{index}",
    )
    _door_hinge_hardware(part, r, mats, index, cand)
    part.visual(
        Cylinder(radius=0.009, length=h * 0.42),
        origin=Origin(xyz=(w - 0.035, _LEAF_Y + 0.5 * _FRONT_T + 0.006, 0.0)),
        material=mats["steel"],
        name=f"door_style__{cand}__pull_{index}", material_class_id="metal.brushed_silver",
    )


def _door_style_slab_build(part, r: ResolvedConfig, mats, index: int) -> None:
    """Handleless flat slab with a routed finger reveal (source 003)."""
    cand = "slab"
    w, h = r.front_width_m, r.door_h
    _box(part, (w, _FRONT_T, h), (0.5 * w, _LEAF_Y, 0.0), mats["front"], f"door_style__{cand}__slab_{index}")
    _box(
        part,
        (w - 0.02, _FRONT_T * 0.5, 0.030),
        (0.5 * w, _LEAF_Y - _FRONT_T * 0.26, -0.5 * h + 0.018),
        mats["dark"],
        f"door_style__{cand}__finger_reveal_{index}",
    )
    _box(
        part,
        (0.012, _FRONT_T * 0.6, h - 0.04),
        (0.012, _LEAF_Y - _FRONT_T * 0.22, 0.0),
        mats["charcoal"],
        f"door_style__{cand}__shadow_gap_{index}",
    )
    _door_hinge_hardware(part, r, mats, index, cand)


_DOOR_BUILDERS = {
    "framed_panel": _door_style_framed_panel_build,
    "slab": _door_style_slab_build,
}


# ---------------------------------------------------------------------------
# Drawers (drawer_style slot) — hollow trays, never solid boxes
# ---------------------------------------------------------------------------
def _tray_shell(part, r: ResolvedConfig, mats, index: int, cand: str, h: float) -> None:
    w = r.front_width_m
    d = r.drawer_box_depth
    side_h = max(0.06, h - 0.045)
    # Inset front: an overlay front as wide as the bay overlapped each divider by
    # 5 mm.  Narrowing it by one panel thickness keeps it inside the opening; the
    # tray is carried by its runners/lips, which lap the dividers by _MOUNT.
    front_w = w - _PANEL_T
    _box(part, (front_w, _FRONT_T, h), (0.0, 0.5 * d, 0.0), mats["front"], f"drawer_style__{cand}__front_{index}")
    # Run the floor and sides right up to the front's back face (plus _MOUNT),
    # otherwise they stop half a front-thickness short and the front panel reads
    # as a floating island inside its own tray.
    box_len = d - 0.5 * _FRONT_T + _MOUNT
    box_cy = 0.5 * (_MOUNT - 0.5 * _FRONT_T)
    _box(
        part,
        (w - 0.05, box_len, _PANEL_T),
        (0.0, box_cy, -0.5 * side_h),
        mats["cabinet"],
        f"drawer_style__{cand}__floor_{index}",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        _box(
            part,
            (_PANEL_T, box_len, side_h),
            (sx * (0.5 * w - 0.025 - 0.5 * _PANEL_T), box_cy, 0.0),
            mats["cabinet"],
            f"drawer_style__{cand}__side_{index}_{i}",
        )
    _box(
        part,
        (w - 0.05, _PANEL_T, side_h),
        (0.0, -0.5 * d + 0.5 * _PANEL_T, 0.0),
        mats["cabinet"],
        f"drawer_style__{cand}__back_{index}",
    )


def _drawer_style_runner_tray_build(part, r: ResolvedConfig, mats, index: int, front_h: float | None = None) -> None:
    """Tray with an edge-pull bar and its own side runner rails (source 002)."""
    cand = "runner_tray"
    h = r.drawer_front_h if front_h is None else front_h
    _tray_shell(part, r, mats, index, cand, h)
    w, d = r.front_width_m, r.drawer_box_depth
    side_h = max(0.06, h - 0.045)
    part.visual(
        Cylinder(radius=0.010, length=w * 0.62),
        origin=Origin(xyz=(0.0, 0.5 * d + 0.5 * _FRONT_T + 0.008, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name=f"drawer_style__{cand}__pull_bar_{index}", material_class_id="metal.brushed_silver",
    )
    # The runners ride the bay dividers: reach out to lap each divider's inner
    # face by _MOUNT so the tray is genuinely carried by the carcass.
    # Span the whole gap: lap the tray side on the inside and the bay divider on
    # the outside, so the rail is genuinely carried between the two.
    runner_outer = 0.5 * r.bay_width_m - 0.5 * _PANEL_T + _MOUNT
    runner_inner = 0.5 * w - 0.025 - _MOUNT
    for i, sx in enumerate((-1.0, 1.0)):
        _box(
            part,
            (runner_outer - runner_inner, d - 0.05, 0.026),
            (sx * 0.5 * (runner_outer + runner_inner), -0.5 * _FRONT_T, -0.5 * side_h + 0.030),
            mats["steel"],
            f"drawer_style__{cand}__runner_{index}_{i}",
        )


def _drawer_style_reveal_tray_build(part, r: ResolvedConfig, mats, index: int, front_h: float | None = None) -> None:
    """Handleless tray retained by side overlap lips, finger reveal only (003)."""
    cand = "reveal_tray"
    h = r.drawer_front_h if front_h is None else front_h
    _tray_shell(part, r, mats, index, cand, h)
    w, d = r.front_width_m, r.drawer_box_depth
    side_h = max(0.06, h - 0.045)
    _box(
        part,
        (w - _PANEL_T - 0.02, _FRONT_T * 0.5, 0.028),
        (0.0, 0.5 * d - _FRONT_T * 0.26, 0.5 * h - 0.017),
        mats["dark"],
        f"drawer_style__{cand}__finger_reveal_{index}",
    )
    # The overlap lips retain the tray against the bay dividers (no separate
    # runners); they lap each divider's inner face by _MOUNT.
    # Span the whole gap so the lip is carried by the tray side and rides the
    # bay divider, rather than floating between the two.
    lip_outer = 0.5 * r.bay_width_m - 0.5 * _PANEL_T + _MOUNT
    lip_inner = 0.5 * w - 0.025 - _MOUNT
    for i, sx in enumerate((-1.0, 1.0)):
        _box(
            part,
            (lip_outer - lip_inner, d - 0.08, 0.014),
            (sx * 0.5 * (lip_outer + lip_inner), -0.5 * _FRONT_T, 0.5 * side_h - 0.020),
            mats["cabinet"],
            f"drawer_style__{cand}__retain_lip_{index}_{i}",
        )


_DRAWER_BUILDERS = {
    "runner_tray": _drawer_style_runner_tray_build,
    "reveal_tray": _drawer_style_reveal_tray_build,
}



# ---------------------------------------------------------------------------
# Island module (island_module slot)
#
# A counter-height return off the right-hand end of the run.  Both candidates
# attach to the run rather than standing detached: a genuinely freestanding
# island touches nothing and QC reports it as an isolated body.  Source 003's
# island drawers become a fixed drawer-front bank, because the working-drawer
# axis is already carried by `drawer_style`.
# ---------------------------------------------------------------------------
def _island_geometry(r: ResolvedConfig) -> tuple[float, float, float, float]:
    """(x_centre, y_centre, length_y, width_x) of the return volume.

    The return sits BEYOND the run's right-hand end and projects forward, so it
    laps the run's end panel (staying connected) while never standing in front
    of a bay -- an earlier version ran a spine down the front and a fully-open
    drawer drove straight into it.
    """
    depth = r.counter_depth_m
    run_x1 = r.tower_x0 + _TOWER_W + r.run_width_m
    width_x = min(0.72, 1.15 * r.bay_width_m)
    length_y = depth + 0.40
    cx = run_x1 + 0.5 * width_x - _MOUNT
    cy = -0.5 * depth + 0.5 * length_y
    return cx, cy, length_y, width_x


def _island_link(part, r: ResolvedConfig, mats, cand: str) -> tuple[float, float, float, float]:
    """The return laps the run's end panel directly; no separate spine needed."""
    return _island_geometry(r)


def _island_module_waterfall_peninsula_build(part, r: ResolvedConfig, mats) -> None:
    """Closed waterfall peninsula: solid volume, wrap-around side, rear brace."""
    cand = "waterfall_peninsula"
    cx, cy, ly, wx = _island_link(part, r, mats, cand)
    body_h = r.base_height_m - _COUNTER_T
    _box(part, (wx, ly, body_h), (cx, cy, 0.5 * body_h), mats["front"], f"island_module__{cand}__body")
    _box(part, (wx + 0.06, ly + 0.06, _COUNTER_T), (cx, cy, body_h + 0.5 * _COUNTER_T), mats["stone"], f"island_module__{cand}__counter")
    # Waterfall side panel running the counter down to the floor on both ends.
    for i, sy in enumerate((-1.0, 1.0)):
        _box(
            part,
            (wx + 0.06, 0.055, body_h + _COUNTER_T),
            (cx, cy + sy * (0.5 * ly + 0.0275 - _MOUNT), 0.5 * (body_h + _COUNTER_T)),
            mats["front"],
            f"island_module__{cand}__waterfall_{i}",
        )
    # Concealed rear brace making the load path explicit (source L178-179).
    _box(part, (0.05, ly - 0.10, 0.09), (cx - 0.5 * wx + 0.03, cy, body_h - 0.10), mats["cabinet"], f"island_module__{cand}__rear_brace")


def _island_module_open_cubby_return_build(part, r: ResolvedConfig, mats) -> None:
    """Open-cubby return: exposed compartments plus a fixed drawer-front bank."""
    cand = "open_cubby_return"
    cx, cy, ly, wx = _island_link(part, r, mats, cand)
    body_h = r.base_height_m - _COUNTER_T
    # Carcass shell: floor, back and two ends -- the cubbies stay open.
    _box(part, (wx, ly, _PANEL_T), (cx, cy, 0.5 * _PANEL_T), mats["cabinet"], f"island_module__{cand}__floor")
    _box(part, (_PANEL_T, ly, body_h), (cx - 0.5 * wx + 0.5 * _PANEL_T, cy, 0.5 * body_h), mats["charcoal"], f"island_module__{cand}__back")
    for i, sy in enumerate((-1.0, 1.0)):
        _box(part, (wx, _PANEL_T, body_h), (cx, cy + sy * (0.5 * ly - 0.5 * _PANEL_T), 0.5 * body_h), mats["cabinet"], f"island_module__{cand}__end_{i}")
    _box(part, (wx + 0.06, ly + 0.06, _COUNTER_T), (cx, cy, body_h + 0.5 * _COUNTER_T), mats["stone"], f"island_module__{cand}__counter")
    # Three open cubbies divided by real shelves/dividers.
    for i in range(2):
        _box(part, (wx - _PANEL_T, _PANEL_T, body_h - _PANEL_T), (cx + 0.5 * _PANEL_T, cy + (i - 0.5) * ly / 3.0, 0.5 * (body_h + _PANEL_T)), mats["charcoal"], f"island_module__{cand}__cubby_divider_{i}")
    _box(part, (wx - _PANEL_T, ly - 2.0 * _PANEL_T, _PANEL_T), (cx + 0.5 * _PANEL_T, cy, 0.55 * body_h), mats["cabinet"], f"island_module__{cand}__cubby_shelf")
    # Fixed drawer-front bank on the outward face.
    for i in range(3):
        _box(
            part,
            (0.020, ly / 3.0 - 0.02, body_h / 3.0 - 0.02),
            (cx + 0.5 * wx - 0.010 + _MOUNT, cy + (i - 1) * ly / 3.0, body_h * (i + 0.5) / 3.0),
            mats["front"],
            f"island_module__{cand}__drawer_front_{i}",
        )


_ISLAND_BUILDERS = {
    "waterfall_peninsula": _island_module_waterfall_peninsula_build,
    "open_cubby_return": _island_module_open_cubby_return_build,
}


# ---------------------------------------------------------------------------
# Carcass
# ---------------------------------------------------------------------------
def _build_carcass(model: ArticulatedObject, r: ResolvedConfig, mats):
    carcass = model.part("kitchen_carcass", meta={"role": "kitchen_carcass"})
    depth = r.counter_depth_m
    run_x0 = r.tower_x0 + _TOWER_W
    run_cx = run_x0 + 0.5 * r.run_width_m
    base_body_h = r.base_height_m - _TOE_H - _COUNTER_T

    _box(carcass, (r.run_width_m, depth - 0.06, _TOE_H + 0.004), (run_cx, 0.03, 0.5 * (_TOE_H + 0.004)), mats["dark"], "base_toe_kick")
    _box(carcass, (r.run_width_m, _PANEL_T, base_body_h), (run_cx, -0.5 * depth + 0.5 * _PANEL_T, _TOE_H + 0.5 * base_body_h), mats["cabinet"], "base_back")
    _box(carcass, (r.run_width_m, depth, _PANEL_T), (run_cx, 0.0, _TOE_H + 0.5 * _PANEL_T), mats["cabinet"], "base_floor")
    for i in range(r.bay_count + 1):
        _box(
            carcass,
            (_PANEL_T, depth - 0.02, base_body_h),
            (run_x0 + i * r.bay_width_m, -0.01, _TOE_H + 0.5 * base_body_h),
            mats["cabinet"],
            f"base_divider_{i}",
        )
    # Tucked against the back panel: at y=-depth/2+0.05 this rail ran straight
    # through the drawer box's back wall.
    _box(carcass, (r.run_width_m, 0.030, 0.05), (run_cx, -0.5 * depth + 0.018, r.base_height_m - _COUNTER_T - 0.025), mats["cabinet"], "base_top_rail")

    sink_x = r.bay_center_x(0)
    hob_x = r.bay_center_x(r.bay_count - 1)
    acx = r.assembly_center_x
    counter = mesh_from_cadquery(
        _counter_geom(r, sink_x - acx, hob_x - acx),
        "kitchen_counter_slab",
        tolerance=_MESH_TOL,
        angular_tolerance=_MESH_ANG_TOL,
    )
    carcass.visual(
        counter,
        origin=Origin(xyz=(acx, 0.0, r.base_height_m - 0.5 * _COUNTER_T)),
        material=mats["stone"],
        name="countertop", material_class_id="stone.polished_granite",
    )

    # Sink basin hung under the cutout at the rear of bay 0.  The bowl and that
    # bay's drawer used to fight for the same volume; bay 0's drawer is now
    # derived to fit beneath the bowl (see `_bay_drawer_geometry`) with a fixed
    # false front closing the gap up to the worktop.
    # The bowl must be WIDER than its cutout, or it simply falls through the
    # hole and reads as a floating island.  Sizing it just outside the opening
    # seats the rim on the counter underside, like a real undermount sink.
    basin_w = min(0.52, r.bay_width_m - 0.10) + 0.024
    basin_d = min(0.40, depth - 0.16) + 0.024
    basin_h = _BASIN_H
    basin_y = -0.02
    basin_top = r.base_height_m - _COUNTER_T + _MOUNT
    _box(carcass, (basin_w, basin_d, _PANEL_T), (sink_x, basin_y, basin_top - basin_h), mats["steel"], "sink_basin_bottom")
    for i, sx in enumerate((-1.0, 1.0)):
        _box(carcass, (0.010, basin_d, basin_h), (sink_x + sx * (0.5 * basin_w - 0.005), basin_y, basin_top - 0.5 * basin_h), mats["steel"], f"sink_basin_side_{i}")
    for i, sy in enumerate((-1.0, 1.0)):
        _box(carcass, (basin_w, 0.010, basin_h), (sink_x, basin_y + sy * (0.5 * basin_d - 0.005), basin_top - 0.5 * basin_h), mats["steel"], f"sink_basin_end_{i}")

    # False drawer front: the fixed filler between the sink bay's shorter working
    # drawer and the worktop.  Real sink cabinets carry exactly this panel.
    false_top = r.base_height_m - _COUNTER_T + _MOUNT
    false_bottom = r.base_height_m - _COUNTER_T - _BASIN_H
    false_h = false_top - false_bottom
    if false_h > 0.01:
        _box(
            carcass,
            (r.bay_width_m - _PANEL_T - 2.0 * _REVEAL, _FRONT_T, false_h),
            (sink_x, 0.5 * depth - 0.02 - _MOUNT + 0.5 * _FRONT_T, false_bottom + 0.5 * false_h),
            mats["front"],
            "sink_false_front",
        )

    fy = basin_y - 0.5 * basin_d - 0.045
    carcass.visual(Cylinder(radius=0.032, length=0.014), origin=Origin(xyz=(sink_x, fy, r.base_height_m + 0.004)), material=mats["steel"], name="faucet_flange", material_class_id="metal.chrome_polished")
    carcass.visual(Cylinder(radius=0.014, length=0.26), origin=Origin(xyz=(sink_x, fy, r.base_height_m + 0.13)), material=mats["steel"], name="faucet_riser", material_class_id="metal.chrome_polished")
    carcass.visual(Cylinder(radius=0.012, length=0.19), origin=Origin(xyz=(sink_x, fy + 0.085, r.base_height_m + 0.25), rpy=(math.pi / 2.0, 0.0, 0.0)), material=mats["steel"], name="faucet_spout", material_class_id="metal.chrome_polished")

    # Flush cooktop on the counter: no downward intrusion.
    # Drop-in hob: its flange laps the cutout rim so it rests on the stone
    # instead of sitting in the hole with nothing under it.
    hob_w = min(0.56, r.bay_width_m - 0.08) + 0.030
    hob_d = min(0.44, depth - 0.14) + 0.030
    _box(carcass, (hob_w, hob_d, 0.014), (hob_x, -0.02, r.base_height_m + 0.002), mats["dark"], "cooktop_plate")
    for i in range(4):
        bx = hob_x + (-1.0 if i % 2 == 0 else 1.0) * hob_w * 0.22
        by = -0.02 + (-1.0 if i < 2 else 1.0) * hob_d * 0.22
        carcass.visual(
            Cylinder(radius=min(0.075, hob_w * 0.16), length=0.004),
            origin=Origin(xyz=(bx, by, r.base_height_m + 0.010)),
            material=mats["charcoal"],
            name=f"cooktop_burner_{i}", material_class_id="metal.cast_iron_bare",
        )

    _box(carcass, (r.run_width_m, 0.016, _BACKSPLASH_H), (run_cx, -0.5 * depth + 0.008, r.base_height_m + 0.5 * _BACKSPLASH_H), mats["splash"], "backsplash")

    _box(carcass, (r.run_width_m, _PANEL_T, _UPPER_H), (run_cx, -0.5 * depth + 0.5 * _PANEL_T, r.upper_z0 + 0.5 * _UPPER_H), mats["cabinet"], "upper_back")
    _box(carcass, (r.run_width_m, _UPPER_DEPTH, _PANEL_T), (run_cx, -0.5 * depth + 0.5 * _UPPER_DEPTH, r.upper_z0 + 0.5 * _PANEL_T), mats["cabinet"], "upper_bottom")
    _box(carcass, (r.run_width_m, _UPPER_DEPTH, _PANEL_T), (run_cx, -0.5 * depth + 0.5 * _UPPER_DEPTH, r.upper_z0 + _UPPER_H - 0.5 * _PANEL_T), mats["cabinet"], "upper_top")
    for i in range(r.bay_count + 1):
        _box(
            carcass,
            (_PANEL_T, _UPPER_DEPTH, _UPPER_H),
            (run_x0 + i * r.bay_width_m, -0.5 * depth + 0.5 * _UPPER_DEPTH, r.upper_z0 + 0.5 * _UPPER_H),
            mats["cabinet"],
            f"upper_gable_{i}",
        )
    return carcass


# ---------------------------------------------------------------------------
# Joints
# ---------------------------------------------------------------------------
def _add_door_joint(model, carcass, door, r: ResolvedConfig, index: int) -> None:
    name = f"door_style__{r.door_style}__door_hinge_{index}"
    hinge_x = r.bay_center_x(index) - 0.5 * r.front_width_m
    # The hinge plane IS the leaf's back face; sit it _MOUNT behind the upper
    # run's front face so the leaf and knuckles seat on the gable (real contact)
    # while nothing sweeps deeper than that at any swing angle.
    hinge_y = -0.5 * r.counter_depth_m + _UPPER_DEPTH - _MOUNT
    hinge_z = r.upper_z0 + 0.5 * _UPPER_H
    provider = AxisInterface(
        name=f"{name}__provider",
        point=(hinge_x, hinge_y, hinge_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(name=f"{name}__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=0.0, upper=math.radians(90.0), effort=18.0, velocity=1.6),
        meta={"mechanism": "upper cabinet door", "bay_index": index},
    )
    register_interface_mate(model, name, mate)


def _add_drawer_joint(model, carcass, drawer, r: ResolvedConfig, index: int) -> None:
    name = f"drawer_style__{r.drawer_style}__drawer_slide_{index}"
    cx = r.bay_center_x(index)
    # Place the tray so its front's back face laps the carcass front plane
    # (dividers end at depth/2 - 0.02) by _MOUNT: real seating, no deep overlap.
    cy = (
        0.5 * r.counter_depth_m
        - 0.02
        - _MOUNT
        + 0.5 * _FRONT_T
        - 0.5 * r.drawer_box_depth
    )
    # Hang the front from whatever caps this bay -- the counter underside, or
    # the sink bowl in bay 0 -- with a reveal below it.
    front_h, top_z = _bay_drawer_geometry(r, index)
    cz = top_z - 0.5 * front_h
    model.articulation(
        name,
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=drawer,
        origin=Origin(xyz=(cx, cy, cz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.drawer_travel, effort=45.0, velocity=0.5),
        meta={"mechanism": "base drawer", "bay_index": index},
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_picturex_0611_kitchen_set(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Kitchen_set",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/kitchen_set",
        },
    )
    mats = _materials(model)
    carcass = _build_carcass(model, r, mats)
    _TOWER_BUILDERS[r.tower_style](carcass, r, mats)
    _ISLAND_BUILDERS[r.island_module](carcass, r, mats)

    door_builder = _DOOR_BUILDERS[r.door_style]
    drawer_builder = _DRAWER_BUILDERS[r.drawer_style]
    for index in range(r.bay_count):
        door = model.part(
            f"door_style__{r.door_style}__cabinet_door_{index}",
            meta={"role": "cabinet_door", "candidate": r.door_style, "bay_index": index},
        )
        door_builder(door, r, mats, index)
        _add_door_joint(model, carcass, door, r, index)

        drawer = model.part(
            f"drawer_style__{r.drawer_style}__base_drawer_{index}",
            meta={"role": "base_drawer", "candidate": r.drawer_style, "bay_index": index},
        )
        drawer_builder(drawer, r, mats, index, _bay_drawer_geometry(r, index)[0])
        _add_drawer_joint(model, carcass, drawer, r, index)

    model.meta["risk_poses"] = (
        {
            f"door_style__{r.door_style}__door_hinge_{i}": math.radians(90.0)
            for i in range(r.bay_count)
        },
        {
            f"drawer_style__{r.drawer_style}__drawer_slide_{i}": r.drawer_travel
            for i in range(r.bay_count)
        },
    )
    return model


def build_seeded_picturex_0611_kitchen_set(seed: int, *, assets: AssetContext | None = None):
    return build_picturex_0611_kitchen_set(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Author tests — category invariants only.
#
# Exact-collision, sampled-pose, isolated-geometry and articulation-origin QC are
# owned by the sweep harness on every built seed.  Restating them here would also
# force mesh materialization during preflight, which deliberately defers it (the
# cadquery countertop has no OBJ at probe time).
# ---------------------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_kitchen_set_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    carcasses = _parts_by_role(object_model, "kitchen_carcass")
    doors = _parts_by_role(object_model, "cabinet_door")
    drawers = _parts_by_role(object_model, "base_drawer")
    carcass = carcasses[0] if carcasses else None
    names = {v.name or "" for v in carcass.visuals} if carcass is not None else set()

    ctx.check(
        "category_anchor: single installed kitchen carcass",
        len(carcasses) == 1
        and {"countertop", "backsplash", "base_toe_kick", "upper_back", "base_floor"} <= names
        and any(n.startswith("sink_basin_") for n in names)
        and any(n.startswith("cooktop_") for n in names)
        and any(n.startswith("faucet_") for n in names)
        and sum(1 for n in names if n.startswith("base_divider_")) == r.bay_count + 1
        and sum(1 for n in names if n.startswith("upper_gable_")) == r.bay_count + 1,
        details=f"carcasses={len(carcasses)}, visuals={len(names)}",
    )

    door_joints = [j for j in object_model.articulations if "door_hinge" in j.name]
    drawer_joints = [j for j in object_model.articulations if "drawer_slide" in j.name]
    ctx.check(
        "category_anchor: N articulated doors and drawers",
        len(doors) == r.bay_count
        and len(drawers) == r.bay_count
        and len(door_joints) == r.bay_count
        and len(drawer_joints) == r.bay_count
        and all(
            j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(v, 6) for v in j.axis) == (0.0, 0.0, 1.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
            and j.parent == "kitchen_carcass"
            for j in door_joints
        )
        and all(
            j.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(v, 6) for v in j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
            and j.parent == "kitchen_carcass"
            for j in drawer_joints
        ),
        details=f"doors={len(doors)}, drawers={len(drawers)}, N={r.bay_count}",
    )

    for drawer in drawers:
        elems = {v.name or "" for v in drawer.visuals}
        ctx.check(
            f"{drawer.name} is a hollow tray",
            any("__front_" in n for n in elems)
            and any("__floor_" in n for n in elems)
            and any("__back_" in n for n in elems)
            and sum(1 for n in elems if "__side_" in n) == 2,
            details=f"elements={sorted(elems)}",
        )

    ctx.check(
        "drawer travel retains the tray in the carcass",
        0.0 < r.drawer_travel <= 0.75 * r.drawer_box_depth,
        details=f"travel={r.drawer_travel:.4f}, box_depth={r.drawer_box_depth:.4f}",
    )

    if r.tower_style == "appliance_tower":
        ctx.check(
            "category_anchor: appliance_tower identity",
            any("appliance_tower__oven_chassis" in n for n in names)
            and any("appliance_tower__oven_glass" in n for n in names)
            and any("appliance_tower__lower_front" in n for n in names),
            details="closed tower with an integrated oven chassis",
        )
    else:
        ctx.check(
            "category_anchor: open_shelf_tower identity",
            sum(1 for n in names if "open_shelf_tower__shelf_" in n) >= 4
            and any("open_shelf_tower__rib_" in n for n in names)
            and not any("oven" in n for n in names),
            details="open shelving tower with a ribbed back and no oven",
        )

    if r.island_module == "waterfall_peninsula":
        ctx.check(
            "category_anchor: island module identity",
            any("waterfall_peninsula__waterfall_" in n for n in names)
            and any("waterfall_peninsula__rear_brace" in n for n in names)
            and not any("cubby" in n for n in names if "island_module" in n),
            details="closed waterfall peninsula with a concealed rear brace",
        )
    else:
        ctx.check(
            "category_anchor: island module identity",
            sum(1 for n in names if "open_cubby_return__cubby_divider_" in n) == 2
            and any("open_cubby_return__cubby_shelf" in n for n in names)
            and sum(1 for n in names if "open_cubby_return__drawer_front_" in n) == 3
            and not any("waterfall" in n for n in names),
            details="open-cubby return with a fixed drawer-front bank",
        )

    if doors and drawers:
        door = doors[0]
        dj = next(j for j in door_joints if j.child == door.name)
        leaf = "slab" if r.door_style == "slab" else "centre_panel"
        leaf_elem = next(
            (v.name for v in door.visuals if v.name and leaf in v.name), None
        )
        rest = ctx.part_element_world_aabb(door, elem=leaf_elem)
        with ctx.pose({dj: dj.motion_limits.upper}):
            swung = ctx.part_element_world_aabb(door, elem=leaf_elem)
        ctx.check(
            "door swings open about its hinge",
            rest is not None
            and swung is not None
            and math.dist(
                [0.5 * (rest[0][i] + rest[1][i]) for i in range(2)],
                [0.5 * (swung[0][i] + swung[1][i]) for i in range(2)],
            )
            > 0.05,
            details=f"rest={rest}, swung={swung}",
        )
        drawer = drawers[0]
        sj = next(j for j in drawer_joints if j.child == drawer.name)
        closed = ctx.part_world_position(drawer)
        with ctx.pose({sj: sj.motion_limits.upper}):
            opened = ctx.part_world_position(drawer)
        ctx.check(
            "drawer pulls forward along +Y",
            closed is not None
            and opened is not None
            and (opened[1] - closed[1]) > 0.5 * r.drawer_travel,
            details=f"closed={closed}, opened={opened}",
        )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ---------------------------------------------------------------------------
# High-risk corners
# ---------------------------------------------------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "max_bays_framed_runner_appliance",
        {
            "door_style": "framed_panel",
            "drawer_style": "runner_tray",
            "tower_style": "appliance_tower",
            "bay_count": 5,
            "bay_width_m": _BAY_WIDTH_MAX,
            "counter_depth_m": _COUNTER_DEPTH_MAX,
            "base_height_m": _BASE_HEIGHT_MAX,
        },
    ),
    corner_case(
        "min_bays_slab_reveal_open_shelf",
        {
            "door_style": "slab",
            "drawer_style": "reveal_tray",
            "tower_style": "open_shelf_tower",
            "bay_count": 2,
            "bay_width_m": _BAY_WIDTH_MIN,
            "counter_depth_m": _COUNTER_DEPTH_MIN,
            "base_height_m": _BASE_HEIGHT_MIN,
        },
    ),
    corner_case(
        "narrow_deep_slab_runner_appliance",
        {
            "door_style": "slab",
            "drawer_style": "runner_tray",
            "tower_style": "appliance_tower",
            "bay_count": 4,
            "bay_width_m": _BAY_WIDTH_MIN,
            "counter_depth_m": _COUNTER_DEPTH_MAX,
            "base_height_m": _BASE_HEIGHT_MIN,
        },
    ),
)
