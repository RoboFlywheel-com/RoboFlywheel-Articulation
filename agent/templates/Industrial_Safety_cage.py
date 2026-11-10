# SPDX-License-Identifier: Apache-2.0

"""Industrial wire safety cage / guard enclosure -- modular procedural template.

A welded rectangular steel ``cage_frame`` (root: base rails + top rails + four
upright corner posts, standing on leveling feet OR swivel casters) whose bays are
enclosed by a protective ``wall_infill`` surface -- crossed galvanized wire mesh,
stout vertical bars, or solid perforated sheet-metal panels. Access is through at
least one articulated ``door_system`` (single side-hinged leaf, double leaves, a
side-sliding gate, or a top-hinged awning) secured by a ``latch`` (rotating
drop-hasp or sliding bolt). An ``interior`` slot holds a fixed equipment cabinet,
a pull-out tray, or open shelving.

Slot graph (pattern = mixed: root + parallel children + door-parented latch +
multiplicity):

    cage_frame (root, steel; feet|casters; latch keeper)
        -> wall_infill  (visuals only on the cage: wire_mesh / vertical_bar_grille
                          / solid_perforated_panels; wire x mesh_density rods)
        -> interior      (fixed_cabinet FIXED | pull_out_drawer PRISMATIC-Y |
                          shelf_stack visuals-only)
        -> door_system   (single_hinged_door / double_door REVOLUTE-Z |
                          sliding_gate PRISMATIC-X | top_awning REVOLUTE-X)
              -> latch    (rotating_latch REVOLUTE-X | sliding_bolt PRISMATIC-Y),
                          parented to the primary door leaf

Coordinate frame: Z-up, floor z=0, front face = -Y (the door side), centerline
x=0. Mirrored pieces straddle x=0. The defining door joint is ALWAYS present.

Adopted sources (see spec Module Source Index):
  S1  origin -- box wire cage, single hinged door, rotating latch, fixed cabinet
  S2  double_door -- two mirrored REVOLUTE-Z leaves
  S3  drawer_payload -- PRISMATIC-Y pull-out tray on slide rails
  S4  mesh_density -- coarser wire-rod counts
  S5  mobile_caster_base -- swivel-caster base (fused visuals)
  S6  shelf_levels -- N internal shelves
  S7  sliding_bolt_latch -- PRISMATIC-Y bolt
  S8  sliding_door -- PRISMATIC-X gate on overhead track
  S9  solid_perforated_panels -- solid sheet-metal bays
  S10 top_hinge_awning -- REVOLUTE-X awning
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
    mount_fixed,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True

PI = math.pi

# --------------------------------------------------------------------------- #
# Module enums
# --------------------------------------------------------------------------- #

WallInfillModule = Literal[
    "wire_mesh",
    "vertical_bar_grille",
    "solid_perforated_panels",
]
DoorModule = Literal[
    "single_hinged_door",
    "double_door",
    "sliding_gate",
    "top_awning",
]
LatchModule = Literal[
    "rotating_latch",
    "sliding_bolt",
]
InteriorModule = Literal[
    "fixed_cabinet",
    "pull_out_drawer",
    "shelf_stack",
]
BaseStyle = Literal["leveling_feet", "casters"]
SafetyCagePalette = Literal[
    "industrial_gray",
    "safety_yellow_black",
    "galvanized_zinc",
    "municipal_blue",
    "workshop_green",
    "powder_black",
]

# --------------------------------------------------------------------------- #
# Palette presets (>=6 colorways). Tokens: frame / wire / door / payload / rubber.
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "industrial_gray": {
        "frame": (0.46, 0.49, 0.48, 1.0),
        "wire": (0.78, 0.80, 0.78, 1.0),
        "door": (1.0, 0.70, 0.05, 1.0),
        "payload": (0.62, 0.05, 0.035, 1.0),
        "rubber": (0.05, 0.05, 0.045, 1.0),
    },
    "safety_yellow_black": {
        "frame": (0.12, 0.12, 0.13, 1.0),
        "wire": (0.62, 0.63, 0.64, 1.0),
        "door": (0.95, 0.78, 0.06, 1.0),
        "payload": (0.20, 0.20, 0.22, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
    "galvanized_zinc": {
        "frame": (0.70, 0.72, 0.74, 1.0),
        "wire": (0.80, 0.82, 0.84, 1.0),
        "door": (0.86, 0.72, 0.16, 1.0),
        "payload": (0.40, 0.42, 0.45, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
    },
    "municipal_blue": {
        "frame": (0.20, 0.35, 0.62, 1.0),
        "wire": (0.72, 0.74, 0.76, 1.0),
        "door": (0.90, 0.76, 0.12, 1.0),
        "payload": (0.16, 0.28, 0.50, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
    },
    "workshop_green": {
        "frame": (0.20, 0.42, 0.24, 1.0),
        "wire": (0.70, 0.72, 0.70, 1.0),
        "door": (0.88, 0.74, 0.14, 1.0),
        "payload": (0.62, 0.10, 0.06, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "powder_black": {
        "frame": (0.14, 0.14, 0.15, 1.0),
        "wire": (0.40, 0.41, 0.43, 1.0),
        "door": (0.90, 0.30, 0.08, 1.0),
        "payload": (0.30, 0.31, 0.33, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
}
PALETTE_NAMES: tuple[str, ...] = tuple(PALETTES.keys())

# --------------------------------------------------------------------------- #
# Fixed hardware dimensions (standardized; not scaled with the envelope).
# --------------------------------------------------------------------------- #

POST = 0.045
RAIL_H = 0.050
BOTTOM_Z = 0.035
DOOR_BAR = 0.035
MESH_R = 0.0038
BAR_R = 0.008
BARREL_R = 0.012

# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class SafetyCageConfig:
    """Public safety_cage config. ``None`` module fields fall back to the origin
    anchor in ``resolve_config``."""

    wall_infill_module: WallInfillModule | None = None
    door_module: DoorModule | None = None
    latch_module: LatchModule | None = None
    interior_module: InteriorModule | None = None
    base_style: BaseStyle = "leveling_feet"
    palette_style: SafetyCagePalette = "industrial_gray"

    mesh_density: int = 7
    width_scale: float = 1.0
    depth_scale: float = 1.0
    height_scale: float = 1.0
    door_open: float = 1.57
    latch_throw: float = 0.04


@dataclass(frozen=True)
class ResolvedSafetyCageConfig:
    """Clamped + derived config consumed by builders."""

    wall_infill_module: WallInfillModule
    door_module: DoorModule
    latch_module: LatchModule
    interior_module: InteriorModule
    base_style: BaseStyle
    palette_style: str

    mesh_density: int
    width: float
    depth: float
    height: float
    door_open: float
    latch_throw: float

    # Derived cage envelope geometry.
    top_z: float
    rail_top: float
    toprail_bot: float
    panel_mid_z: float
    panel_h: float
    hinge_y: float  # world Y of the front hinge line (just outside the front face)

    # Door geometry.
    door_h: float
    door_w: float
    leaf_w: float

    # Latch mount (in the primary door part's local frame).
    primary_door_part: str
    latch_mount_local: tuple[float, float, float]
    latch_plate_local: tuple[float, float, float]
    latch_rot_axis: tuple[float, float, float]
    latch_slide_axis: tuple[float, float, float]
    latch_mount_rpy: tuple[float, float, float]

    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> SafetyCageConfig:
    """Deterministic procedural sampling. seed 0 = origin canonical anchor."""
    if seed == 0:
        return SafetyCageConfig(
            wall_infill_module="wire_mesh",
            door_module="single_hinged_door",
            latch_module="rotating_latch",
            interior_module="fixed_cabinet",
            base_style="leveling_feet",
            palette_style="industrial_gray",
            mesh_density=7,
        )

    rng = random.Random(seed)
    wall = rng.choice(
        ("wire_mesh", "vertical_bar_grille", "solid_perforated_panels")
    )
    door = rng.choice(
        ("single_hinged_door", "double_door", "sliding_gate", "top_awning")
    )
    latch = rng.choice(("rotating_latch", "sliding_bolt"))
    interior = rng.choice(("fixed_cabinet", "pull_out_drawer", "shelf_stack"))
    base = rng.choice(("leveling_feet", "casters"))
    palette = rng.choice(PALETTE_NAMES)

    mesh_density = rng.choices((7, 6, 5), weights=(0.5, 0.2, 0.3))[0]

    return SafetyCageConfig(
        wall_infill_module=wall,
        door_module=door,
        latch_module=latch,
        interior_module=interior,
        base_style=base,
        palette_style=palette,
        mesh_density=mesh_density,
        width_scale=round(rng.uniform(0.85, 1.20), 4),
        depth_scale=round(rng.uniform(0.85, 1.20), 4),
        height_scale=round(rng.uniform(0.85, 1.20), 4),
        door_open=round(rng.uniform(1.30, 1.57), 4),
        latch_throw=round(rng.uniform(0.03, 0.05), 4),
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: SafetyCageConfig) -> ResolvedSafetyCageConfig:
    wall = config.wall_infill_module or "wire_mesh"
    door = config.door_module or "single_hinged_door"
    latch = config.latch_module or "rotating_latch"
    interior = config.interior_module or "fixed_cabinet"
    base = config.base_style if config.base_style in ("leveling_feet", "casters") else "leveling_feet"

    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    mesh_density = int(_clamp(config.mesh_density, 5, 7)) if wall == "wire_mesh" else 7

    width = _clamp(0.62 * config.width_scale, 0.45, 0.85)
    depth = _clamp(0.50 * config.depth_scale, 0.38, 0.70)
    height = _clamp(0.72 * config.height_scale, 0.55, 0.95)
    door_open = _clamp(config.door_open, 1.10, PI / 2.0)
    latch_throw = _clamp(config.latch_throw, 0.03, 0.05)

    top_z = height
    rail_top = BOTTOM_Z + RAIL_H / 2.0
    toprail_bot = top_z - POST / 2.0
    panel_mid_z = (rail_top + toprail_bot) / 2.0
    panel_h = (toprail_bot - rail_top) + 0.02
    # Push the hinge plane ~2cm out in front of the frame so the whole door
    # (bars + stiles) clears the posts/rails through its full swing; hinge leaves
    # reach back to the post for a captured contact (see _emit_hinged_leaf).
    hinge_y = -depth / 2.0 - POST / 2.0 - BARREL_R - 0.020

    door_h = height - 0.06
    door_w = width - POST - 0.02
    leaf_w = (width - POST) / 2.0 - 0.030

    # Latch mount in the primary door part's local frame + axes (see spec Slot C).
    hs_y = -(BARREL_R + DOOR_BAR / 2.0)  # hinge-stile local Y for hinged doors
    if door == "single_hinged_door":
        primary = "access_door"
        free_y = hs_y - door_w
        plate_local = (-0.022, free_y + 0.015, 0.030)
        mount_local = (-0.024, free_y + 0.015, 0.070)
        rot_axis = (1.0, 0.0, 0.0)
        slide_axis = (0.0, -1.0, 0.0)
        mount_rpy = (0.0, 0.0, 0.0)
    elif door == "double_door":
        primary = "door_leaf_0"
        free_y = hs_y - leaf_w
        plate_local = (-0.022, free_y + 0.015, 0.030)
        mount_local = (-0.024, free_y + 0.015, 0.070)
        rot_axis = (1.0, 0.0, 0.0)
        slide_axis = (0.0, -1.0, 0.0)
        mount_rpy = (0.0, 0.0, 0.0)
    elif door == "sliding_gate":
        primary = "access_door"
        plate_local = (door_w / 2.0 - 0.010, -DOOR_BAR / 2.0 - 0.005, 0.030)
        mount_local = (door_w / 2.0 - 0.015, -DOOR_BAR / 2.0 - 0.012, 0.070)
        rot_axis = (1.0, 0.0, 0.0)
        slide_axis = (1.0, 0.0, 0.0)
        mount_rpy = (0.0, 0.0, 0.0)
    else:  # top_awning
        primary = "access_door"
        door_depth = door_h
        # Seat the latch pivot into the awning frame's top face (door frame spans
        # local z in +-DOOR_BAR/2=+-0.0175); mount z=0.024 puts the rotating
        # pivot_pin (radius 0.010, bottom at 0.014) and the sliding bolt body
        # physically against the frame so the latch is captured -- at the prior
        # z=0.030 the rotating pivot floated ~2.5mm proud of the frame. Kept as
        # small a drop as possible so the outward-pointing latch still clears the
        # interior payload through the full open swing.
        plate_local = (0.15, -door_depth + 0.015, 0.024)
        mount_local = (0.15, -door_depth + 0.015, 0.024)
        rot_axis = (1.0, 0.0, 0.0)
        slide_axis = (0.0, 1.0, 0.0)
        # Flip the latch 180deg about X so its hasp/bolt/knob point OUTWARD (-Y in
        # world) when the awning is closed, clearing the interior payload + base rail.
        mount_rpy = (PI, 0.0, 0.0)

    return ResolvedSafetyCageConfig(
        wall_infill_module=wall,
        door_module=door,
        latch_module=latch,
        interior_module=interior,
        base_style=base,
        palette_style=config.palette_style,
        mesh_density=mesh_density,
        width=width,
        depth=depth,
        height=height,
        door_open=door_open,
        latch_throw=latch_throw,
        top_z=top_z,
        rail_top=rail_top,
        toprail_bot=toprail_bot,
        panel_mid_z=panel_mid_z,
        panel_h=panel_h,
        hinge_y=hinge_y,
        door_h=door_h,
        door_w=door_w,
        leaf_w=leaf_w,
        primary_door_part=primary,
        latch_mount_local=mount_local,
        latch_plate_local=plate_local,
        latch_rot_axis=rot_axis,
        latch_slide_axis=slide_axis,
        latch_mount_rpy=mount_rpy,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _box(part, name, size, xyz, material) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.paint_coated")


def _rod_z(part, name, radius, length, xyz, material) -> None:
    part.visual(Cylinder(radius, length), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.steel_galvanized")


def _rod_x(part, name, radius, length, xyz, material) -> None:
    part.visual(
        Cylinder(radius, length),
        origin=Origin(xyz=xyz, rpy=(0.0, PI / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _rod_y(part, name, radius, length, xyz, material) -> None:
    part.visual(
        Cylinder(radius, length),
        origin=Origin(xyz=xyz, rpy=(-PI / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _spread(lo: float, hi: float, n: int) -> list[float]:
    if n <= 1:
        return [(lo + hi) / 2.0]
    return [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def _passthrough_downstream(ctx: ModuleBuildContext) -> InterfaceSpec:
    """Re-export the cage downstream so later parallel-children slots find it."""
    return ctx.upstream_interface  # type: ignore[return-value]


# --------------------------------------------------------------------------- #
# Root: cage_frame
# --------------------------------------------------------------------------- #


def _build_cage(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedSafetyCageConfig = ctx.config  # type: ignore[assignment]
    W, D, H = r.width, r.depth, r.height
    cage = model.part("cage_frame")

    cage.inertial = Inertial.from_geometry(
        Box((W + 0.1, D + 0.1, H + 0.1)),
        mass=18.0,
        origin=Origin(xyz=(0.0, 0.0, H * 0.5)),
    )

    top_z = r.top_z
    # Base + top structural rails.
    _box(cage, "front_base_rail", (W + POST, POST, RAIL_H), (0.0, -D / 2.0, BOTTOM_Z), "frame")
    _box(cage, "rear_base_rail", (W + POST, POST, RAIL_H), (0.0, D / 2.0, BOTTOM_Z), "frame")
    _box(cage, "side_base_rail_0", (POST, D + POST, RAIL_H), (-W / 2.0, 0.0, BOTTOM_Z), "frame")
    _box(cage, "side_base_rail_1", (POST, D + POST, RAIL_H), (W / 2.0, 0.0, BOTTOM_Z), "frame")
    _box(cage, "front_top_rail", (W + POST, POST, POST), (0.0, -D / 2.0, top_z), "frame")
    _box(cage, "rear_top_rail", (W + POST, POST, POST), (0.0, D / 2.0, top_z), "frame")
    _box(cage, "side_top_rail_0", (POST, D + POST, POST), (-W / 2.0, 0.0, top_z), "frame")
    _box(cage, "side_top_rail_1", (POST, D + POST, POST), (W / 2.0, 0.0, top_z), "frame")

    # Four upright corner posts.
    post_names = {
        (0, 0): "front_left_post",
        (1, 0): "front_right_post",
        (0, 1): "rear_left_post",
        (1, 1): "rear_right_post",
    }
    for ix, x in enumerate((-W / 2.0, W / 2.0)):
        for iy, y in enumerate((-D / 2.0, D / 2.0)):
            _box(cage, post_names[(ix, iy)], (POST, POST, H - 0.02), (x, y, H / 2.0 + 0.02), "frame")

    # Base: leveling feet or swivel casters (static fused visuals; Rule 1).
    if r.base_style == "leveling_feet":
        for ix, x in enumerate((-W / 2.0 + 0.030, W / 2.0 - 0.030)):
            for iy, y in enumerate((-D / 2.0 + 0.030, D / 2.0 - 0.030)):
                _rod_z(cage, f"foot_{ix}_{iy}", 0.030, 0.028, (x, y, 0.010), "rubber")
    else:
        _emit_casters(cage, r)

    # Latch keeper standoff on the front-right post (door seats against it closed).
    _box(cage, "latch_keeper", (0.018, 0.014, 0.070), (W / 2.0 - POST / 2.0, -D / 2.0 - POST / 2.0 - 0.004, r.panel_mid_z), "wire")

    downstream = InterfaceSpec(
        interface_name="downstream",
        part_name="cage_frame",
        visual_name="front_base_rail",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, BOTTOM_Z),
        contact_tol=0.004,
    )
    return ModuleBuild(
        module_name="cage_frame",
        parts_emitted=["cage_frame"],
        internal_articulations=[],
        interfaces={"downstream": downstream},
    )


def _emit_casters(cage, r: ResolvedSafetyCageConfig) -> None:
    """Four swivel-caster assemblies fused as cage visuals (S5)."""
    W, D = r.width, r.depth
    wheel_r, wheel_w = 0.019, 0.020
    stem_r, stem_l = 0.008, 0.028
    swivel_r, swivel_h = 0.015, 0.006
    fork_h, fork_w, fork_t = 0.042, 0.010, 0.005
    axle_r = 0.004
    rail_bot = BOTTOM_Z - RAIL_H / 2.0
    for i in range(2):
        x = (-W / 2.0 + 0.030) if i == 0 else (W / 2.0 - 0.030)
        for j in range(2):
            y = (-D / 2.0 + 0.030) if j == 0 else (D / 2.0 - 0.030)
            stem_bot = rail_bot - 0.005
            stem_cz = stem_bot + stem_l / 2.0
            _rod_z(cage, f"caster_stem_{i}_{j}", stem_r, stem_l, (x, y, stem_cz), "wire")
            swivel_cz = stem_bot - swivel_h / 2.0
            _rod_z(cage, f"caster_swivel_{i}_{j}", swivel_r, swivel_h, (x, y, swivel_cz), "wire")
            fork_top = stem_bot - swivel_h
            fork_cz = fork_top - fork_h / 2.0
            fork_y_off = wheel_w / 2.0 + fork_t / 2.0
            for side, dy in enumerate((-fork_y_off, fork_y_off)):
                _box(cage, f"caster_fork_{side}_{i}_{j}", (fork_w, fork_t, fork_h), (x, y + dy, fork_cz), "wire")
            wheel_cz = fork_top - fork_h + wheel_r
            axle_l = 2.0 * fork_y_off + fork_t
            _rod_y(cage, f"caster_axle_{i}_{j}", axle_r, axle_l, (x, y, wheel_cz), "wire")
            cage.visual(
                Cylinder(wheel_r, wheel_w),
                origin=Origin(xyz=(x, y, wheel_cz), rpy=(-PI / 2.0, 0.0, 0.0)),
                material="rubber",
                name=f"caster_wheel_{i}_{j}", material_class_id="rubber.smooth_plain",
            )


# --------------------------------------------------------------------------- #
# Slot A -- wall_infill (visuals only, added to cage)
# --------------------------------------------------------------------------- #


def _build_wire_mesh(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedSafetyCageConfig = ctx.config  # type: ignore[assignment]
    cage = ctx.model.get_part("cage_frame")
    W, D = r.width, r.depth
    n = r.mesh_density
    _emit_lattice(cage, r, n_v=n, n_h=n + 1, radius=MESH_R, roof=True)
    return ModuleBuild("wire_mesh", [], [], {"downstream": _passthrough_downstream(ctx)})


def _build_vertical_bar_grille(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedSafetyCageConfig = ctx.config  # type: ignore[assignment]
    cage = ctx.model.get_part("cage_frame")
    # Stout vertical bars only (no horizontals); light wire roof retained.
    _emit_lattice(cage, r, n_v=7, n_h=0, radius=BAR_R, roof=True, roof_radius=MESH_R)
    return ModuleBuild("vertical_bar_grille", [], [], {"downstream": _passthrough_downstream(ctx)})


def _emit_lattice(cage, r: ResolvedSafetyCageConfig, *, n_v, n_h, radius, roof, roof_radius=None) -> None:
    W, D = r.width, r.depth
    top_z = r.top_z
    z_lo, z_hi = r.rail_top + 0.02, r.toprail_bot - 0.02
    for side_index, x in enumerate((-W / 2.0, W / 2.0)):
        side = "left_side" if side_index == 0 else "right_side"
        for i, y in enumerate(_spread(-D / 2.0 + 0.06, D / 2.0 - 0.06, n_v)):
            _rod_z(cage, f"{side}_vertical_{i}", radius, r.panel_h, (x, y, r.panel_mid_z), "wire")
        for i, z in enumerate(_spread(z_lo, z_hi, n_h)):
            _rod_y(cage, f"{side}_horizontal_{i}", radius, D, (x, 0.0, z), "wire")
    for i, x in enumerate(_spread(-W / 2.0 + 0.06, W / 2.0 - 0.06, n_v + 2)):
        _rod_z(cage, f"rear_vertical_{i}", radius, r.panel_h, (x, D / 2.0, r.panel_mid_z), "wire")
    for i, z in enumerate(_spread(z_lo, z_hi, n_h)):
        _rod_x(cage, f"rear_horizontal_{i}", radius, W, (0.0, D / 2.0, z), "wire")
    if roof:
        rr = roof_radius if roof_radius is not None else radius
        for i, x in enumerate(_spread(-W / 2.0 + 0.08, W / 2.0 - 0.08, max(3, n_v - 1))):
            _rod_y(cage, f"roof_front_back_{i}", rr, D, (x, 0.0, top_z + 0.004), "wire")
        for i, y in enumerate(_spread(-D / 2.0 + 0.08, D / 2.0 - 0.08, max(3, n_v - 2))):
            _rod_x(cage, f"roof_side_side_{i}", rr, W, (0.0, y, top_z + 0.004), "wire")


def _build_solid_perforated_panels(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedSafetyCageConfig = ctx.config  # type: ignore[assignment]
    cage = ctx.model.get_part("cage_frame")
    W, D = r.width, r.depth
    top_z = r.top_z
    t, embed = 0.003, 0.008
    span_z = r.panel_h + 2.0 * embed
    depth_y = D - POST + 2.0 * embed
    span_x = W - POST + 2.0 * embed
    for side_index, x in enumerate((-W / 2.0, W / 2.0)):
        side = "left_side" if side_index == 0 else "right_side"
        _box(cage, f"panel_{side}", (t, depth_y, span_z), (x, 0.0, r.panel_mid_z), "wire")
    _box(cage, "panel_rear", (span_x, t, span_z), (0.0, D / 2.0, r.panel_mid_z), "wire")
    _box(cage, "panel_roof", (span_x, depth_y, t), (0.0, 0.0, top_z + 0.004), "wire")
    return ModuleBuild("solid_perforated_panels", [], [], {"downstream": _passthrough_downstream(ctx)})


# --------------------------------------------------------------------------- #
# Slot B -- door_system (parallel children on the cage front -Y)
# --------------------------------------------------------------------------- #


def _door_wire_fill_z(door, r, y_of, w, h) -> None:
    """Crossed wire mesh for a door authored in the Y-Z plane (hinged/double)."""
    for i, yy in enumerate(_spread(-0.05, -(w - 0.05), 6)):
        _rod_z(door, f"door_vertical_{i}", MESH_R, h - 0.02, (0.0, y_of(yy), 0.0), "wire")
    for i, z in enumerate(_spread(-h / 2.0 + 0.05, h / 2.0 - 0.05, 7)):
        _rod_y(door, f"door_horizontal_{i}", MESH_R, w - 0.035, (0.0, y_of(-w / 2.0), z), "wire")


def _emit_vertical_hinge_boss(cage, r, part_name, x, z, suffix="u") -> None:
    """Cage boss for a vertical (Z-axis) hinge: bridges the post front face out
    to the hinge axis so the axis touches cage geometry and captures the barrel."""
    post_front = -r.depth / 2.0 - POST / 2.0
    standoff = post_front - r.hinge_y  # positive distance from axis to post face
    boss_y = (post_front + r.hinge_y) / 2.0
    _box(cage, f"{part_name}_boss_{suffix}", (0.034, standoff + 0.008, 0.060), (x, boss_y, z), "frame")


def _emit_hinged_leaf(model, cage, r, *, part_name, hinge_x, axis_sign, w, keeper_post) -> None:
    door = model.part(part_name)
    h = r.door_h
    hs_y = -(BARREL_R + DOOR_BAR / 2.0)

    def ay(y: float) -> float:
        return hs_y + y

    door.inertial = Inertial.from_geometry(
        Box((DOOR_BAR, w + DOOR_BAR, h)),
        mass=3.0,
        origin=Origin(xyz=(0.0, ay(-w / 2.0), 0.0)),
    )
    _box(door, "hinge_stile", (DOOR_BAR, DOOR_BAR, h), (0.0, ay(0.0), 0.0), "door")
    _box(door, "free_stile", (DOOR_BAR, DOOR_BAR, h), (0.0, ay(-w), 0.0), "door")
    _box(door, "top_rail", (DOOR_BAR, w + DOOR_BAR, DOOR_BAR), (0.0, ay(-w / 2.0), h / 2.0), "door")
    _box(door, "bottom_rail", (DOOR_BAR, w + DOOR_BAR, DOOR_BAR), (0.0, ay(-w / 2.0), -h / 2.0), "door")
    _box(door, "middle_rail", (DOOR_BAR, w + DOOR_BAR, 0.026), (0.0, ay(-w / 2.0), 0.030), "door")
    _door_wire_fill_z(door, r, ay, w, h)
    _rod_z(door, "upper_hinge_barrel", BARREL_R, 0.105, (0.0, 0.0, 0.205), "wire")
    _rod_z(door, "lower_hinge_barrel", BARREL_R, 0.105, (0.0, 0.0, -0.205), "wire")
    # Leaves connect the barrels back to the hinge stile (door-internal only).
    _box(door, "upper_hinge_leaf", (0.030, 0.030, 0.080), (0.0, hs_y / 2.0, 0.205), "wire")
    _box(door, "lower_hinge_leaf", (0.030, 0.030, 0.080), (0.0, hs_y / 2.0, -0.205), "wire")
    _box(door, "latch_plate", (0.010, 0.070, 0.060), (-0.022, ay(-w) + 0.015, 0.030), "wire")
    # Cage-side hinge bosses reach from the post front face out to the hinge axis
    # (so the joint axis touches cage hardware and the door barrel is captured).
    _emit_vertical_hinge_boss(cage, r, part_name, hinge_x, r.panel_mid_z + 0.205)
    _emit_vertical_hinge_boss(cage, r, part_name, hinge_x, r.panel_mid_z - 0.205, suffix="l")
    model.articulation(
        f"cage_to_{part_name}",
        ArticulationType.REVOLUTE,
        parent=cage,
        child=door,
        origin=Origin(xyz=(hinge_x, r.hinge_y, r.panel_mid_z)),
        axis=(0.0, 0.0, axis_sign),
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=r.door_open),
    )


def _build_single_hinged_door(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    _emit_hinged_leaf(
        model, cage, r, part_name="access_door", hinge_x=-r.width / 2.0,
        axis_sign=1.0, w=r.door_w, keeper_post="front_right_post",
    )
    return ModuleBuild("single_hinged_door", ["access_door"], ["cage_to_access_door"],
                       {"downstream": _passthrough_downstream(ctx)})


def _build_double_door(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    _emit_hinged_leaf(model, cage, r, part_name="door_leaf_0", hinge_x=-r.width / 2.0,
                      axis_sign=1.0, w=r.leaf_w, keeper_post="front_left_post")
    _emit_hinged_leaf(model, cage, r, part_name="door_leaf_1", hinge_x=r.width / 2.0,
                      axis_sign=-1.0, w=r.leaf_w, keeper_post="front_right_post")
    return ModuleBuild("double_door", ["door_leaf_0", "door_leaf_1"],
                       ["cage_to_door_leaf_0", "cage_to_door_leaf_1"],
                       {"downstream": _passthrough_downstream(ctx)})


def _build_sliding_gate(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    W, D = r.width, r.depth
    top_z = r.top_z
    w, h = r.door_w, r.door_h
    # Extra standoff so the front-hung gate + hanger brackets clear the front rail.
    door_y = -D / 2.0 - POST / 2.0 - DOOR_BAR / 2.0 - 0.020
    door_center_z = top_z - h / 2.0 - 0.020
    track_z = top_z + 0.050
    roller_zl = track_z - door_center_z  # roller local z so it rides in the track center

    door = model.part("access_door")
    door.inertial = Inertial.from_geometry(
        Box((w + DOOR_BAR, DOOR_BAR, h)), mass=3.5, origin=Origin(),
    )
    _box(door, "hinge_stile", (DOOR_BAR, DOOR_BAR, h), (-w / 2.0, 0.0, 0.0), "door")
    _box(door, "free_stile", (DOOR_BAR, DOOR_BAR, h), (w / 2.0, 0.0, 0.0), "door")
    _box(door, "top_rail", (w + DOOR_BAR, DOOR_BAR, DOOR_BAR), (0.0, 0.0, h / 2.0), "door")
    _box(door, "bottom_rail", (w + DOOR_BAR, DOOR_BAR, DOOR_BAR), (0.0, 0.0, -h / 2.0), "door")
    _box(door, "middle_rail", (w + DOOR_BAR, DOOR_BAR, 0.026), (0.0, 0.0, 0.030), "door")
    for i, x in enumerate(_spread(-w / 2.0 + 0.05, w / 2.0 - 0.05, 7)):
        _rod_z(door, f"door_vertical_{i}", MESH_R, h - 0.02, (x, 0.0, 0.0), "wire")
    for i, z in enumerate(_spread(-h / 2.0 + 0.05, h / 2.0 - 0.05, 7)):
        _rod_x(door, f"door_horizontal_{i}", MESH_R, w - 0.035, (0.0, 0.0, z), "wire")
    # Hanger risers + rollers rise from the door top_rail up into the overhead
    # track. They stay at the door plane (front), clear of the front top rail.
    riser_top = roller_zl
    for i, hx in enumerate((-w / 2.0 + 0.060, w / 2.0 - 0.060)):
        riser_lo = h / 2.0
        _box(door, f"hanger_bracket_{i}", (0.026, 0.022, (riser_top - riser_lo) + 0.02),
             (hx, 0.0, (riser_lo + riser_top) / 2.0), "wire")
        _rod_y(door, f"hanger_roller_{i}", 0.012, 0.026, (hx, 0.0, riser_top), "wire")
    _box(door, "latch_plate", (0.010, 0.070, 0.060), (w / 2.0 - 0.010, -DOOR_BAR / 2.0 - 0.005, 0.030), "wire")

    # Overhead track (cage visual). Rollers ride inside it (allowed overlap).
    track_len = W + w + 0.05
    track_cx = (w + 0.05) / 2.0
    _box(cage, "door_track", (track_len, 0.030, 0.035), (track_cx, door_y, track_z), "frame")
    # Single central mount bridges the front top rail up to the track (x=0 lies
    # between the two hanger rollers, so it never fouls them).
    mount_y0 = -D / 2.0
    mount_z_bot = top_z + 0.005  # above the door top_rail, into the rail top
    mount_z_top = track_z + 0.02
    _box(cage, "track_mount_0",
         (0.030, abs(door_y - mount_y0) + 0.03, mount_z_top - mount_z_bot),
         (0.0, (door_y + mount_y0) / 2.0, (mount_z_bot + mount_z_top) / 2.0), "frame")
    # Support leg at the extended (right) track end.
    track_right_x = W / 2.0 + w + 0.04
    leg_h = track_z - 0.0175 + 0.005
    _box(cage, "track_support_leg", (0.030, 0.030, leg_h), (track_right_x, door_y, leg_h / 2.0), "frame")
    _rod_z(cage, "track_support_foot", 0.025, 0.018, (track_right_x, door_y, 0.010), "rubber")

    model.articulation(
        "cage_to_access_door",
        ArticulationType.PRISMATIC,
        parent=cage,
        child=door,
        origin=Origin(xyz=(0.0, door_y, door_center_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.5, lower=0.0, upper=w),
    )
    return ModuleBuild("sliding_gate", ["access_door"], ["cage_to_access_door"],
                       {"downstream": _passthrough_downstream(ctx)})


def _build_top_awning(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    W, D = r.width, r.depth
    top_z = r.top_z
    door_depth = r.door_h
    opening_w = W - POST

    door = model.part("access_door")
    door.inertial = Inertial.from_geometry(
        Box((opening_w, door_depth, DOOR_BAR)), mass=3.0,
        origin=Origin(xyz=(0.0, -door_depth / 2.0, 0.0)),
    )
    _box(door, "top_rail", (opening_w, DOOR_BAR, DOOR_BAR), (0.0, 0.0, 0.0), "door")
    _box(door, "bottom_rail", (opening_w, DOOR_BAR, DOOR_BAR), (0.0, -door_depth, 0.0), "door")
    _box(door, "hinge_stile", (DOOR_BAR, door_depth, DOOR_BAR), (-(opening_w - DOOR_BAR) / 2.0, -door_depth / 2.0, 0.0), "door")
    _box(door, "free_stile", (DOOR_BAR, door_depth, DOOR_BAR), ((opening_w - DOOR_BAR) / 2.0, -door_depth / 2.0, 0.0), "door")
    _box(door, "middle_rail", (opening_w, DOOR_BAR, 0.026), (0.0, -door_depth / 2.0, 0.0), "door")
    # Verticals start ~0.05 below the hinge line so they clear the cage hinge
    # bosses through the full swing (points near the pivot axis barely move).
    v_top, v_bot = -0.05, -(door_depth - 0.03)
    for i, x in enumerate(_spread(-opening_w / 2.0 + 0.05, opening_w / 2.0 - 0.05, 7)):
        _rod_y(door, f"door_vertical_{i}", MESH_R, v_top - v_bot, (x, (v_top + v_bot) / 2.0, 0.0), "wire")
    for i, y in enumerate(_spread(-0.06, -(door_depth - 0.06), 8)):
        _rod_x(door, f"door_horizontal_{i}", MESH_R, opening_w - 0.01, (0.0, y, 0.0), "wire")
    _rod_x(door, "upper_hinge_barrel", BARREL_R, 0.105, (-opening_w / 4.0, 0.0, 0.0), "wire")
    _rod_x(door, "lower_hinge_barrel", BARREL_R, 0.105, (opening_w / 4.0, 0.0, 0.0), "wire")
    # Leaves connect barrels to the door top_rail (door-internal only).
    _box(door, "upper_hinge_leaf", (0.080, 0.030, 0.030), (-opening_w / 4.0, -0.018, 0.0), "wire")
    _box(door, "lower_hinge_leaf", (0.080, 0.030, 0.030), (opening_w / 4.0, -0.018, 0.0), "wire")
    _box(door, "latch_plate", (0.070, 0.010, 0.060), (0.15, -door_depth + 0.015, -0.022), "wire")

    # Cage-side bosses reach from the front top rail out to the awning hinge axis.
    post_front = -D / 2.0 - POST / 2.0
    standoff = post_front - r.hinge_y
    boss_y = (post_front + r.hinge_y) / 2.0
    for bx in (-opening_w / 4.0, opening_w / 4.0):
        _box(cage, f"awning_boss_{'p' if bx > 0 else 'n'}", (0.060, standoff + 0.008, 0.034), (bx, boss_y, top_z), "frame")

    model.articulation(
        "cage_to_access_door",
        ArticulationType.REVOLUTE,
        parent=cage,
        child=door,
        origin=Origin(xyz=(0.0, r.hinge_y, top_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=min(r.door_open, PI / 2.0)),
    )
    return ModuleBuild("top_awning", ["access_door"], ["cage_to_access_door"],
                       {"downstream": _passthrough_downstream(ctx)})


# --------------------------------------------------------------------------- #
# Slot C -- latch (child of the primary door part)
# --------------------------------------------------------------------------- #


def _build_rotating_latch(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    door = model.get_part(r.primary_door_part)
    latch = model.part("latch_handle")
    latch.inertial = Inertial.from_geometry(Box((0.05, 0.05, 0.12)), mass=0.2, origin=Origin(xyz=(-0.02, 0.0, -0.05)))
    _rod_x(latch, "pivot_pin", 0.010, 0.024, (-0.012, 0.0, 0.0), "wire")
    _box(latch, "drop_hasp", (0.010, 0.024, 0.082), (-0.024, 0.0, -0.044), "wire")
    latch.visual(Sphere(0.018), origin=Origin(xyz=(-0.024, 0.0, -0.092)), material="wire", name="pull_knob", material_class_id="metal.steel_galvanized")
    model.articulation(
        "door_to_latch",
        ArticulationType.REVOLUTE,
        parent=door,
        child=latch,
        origin=Origin(xyz=r.latch_mount_local, rpy=r.latch_mount_rpy),
        axis=r.latch_rot_axis,
        motion_limits=MotionLimits(effort=1.5, velocity=4.0, lower=-0.75, upper=0.75),
    )
    return ModuleBuild("rotating_latch", ["latch_handle"], ["door_to_latch"],
                       {"downstream": _passthrough_downstream(ctx)})


def _build_sliding_bolt(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    door = model.get_part(r.primary_door_part)
    latch = model.part("latch_handle")
    latch.inertial = Inertial.from_geometry(Box((0.05, 0.09, 0.05)), mass=0.2, origin=Origin())
    _rod_y(latch, "bolt_body", 0.008, 0.065, (0.0, -0.020, 0.0), "wire")
    latch.visual(Sphere(0.016), origin=Origin(xyz=(0.0, 0.025, 0.0)), material="wire", name="pull_knob", material_class_id="metal.steel_galvanized")
    model.articulation(
        "door_to_latch",
        ArticulationType.PRISMATIC,
        parent=door,
        child=latch,
        origin=Origin(xyz=r.latch_mount_local, rpy=r.latch_mount_rpy),
        axis=r.latch_slide_axis,
        motion_limits=MotionLimits(effort=1.5, velocity=2.0, lower=0.0, upper=r.latch_throw),
    )
    return ModuleBuild("sliding_bolt", ["latch_handle"], ["door_to_latch"],
                       {"downstream": _passthrough_downstream(ctx)})


# --------------------------------------------------------------------------- #
# Slot D -- interior (parallel child on the cage)
# --------------------------------------------------------------------------- #


def _emit_cabinet_visuals(payload, r) -> None:
    _box(payload, "red_cabinet", (0.36, 0.26, 0.24), (0.0, 0.0, 0.0), "payload")
    _box(payload, "top_cap", (0.38, 0.28, 0.025), (0.0, 0.0, 0.132), "payload")


def _build_fixed_cabinet(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    W, D = r.width, r.depth
    _box(cage, "bottom_shelf", (W - POST + 0.02, D - 0.02, 0.018), (0.0, 0.0, r.rail_top + 0.009), "wire")
    shelf_top = r.rail_top + 0.009 + 0.009
    payload = model.part("red_payload")
    payload.inertial = Inertial.from_geometry(Box((0.36, 0.26, 0.24)), mass=5.0, origin=Origin())
    _emit_cabinet_visuals(payload, r)
    _box(payload, "front_handle", (0.090, 0.012, 0.030), (0.0, -0.136, 0.035), "wire")
    mount_fixed(
        model, joint_name="cage_to_payload", parent=cage, child=payload,
        parent_anchor=(0.0, 0.02, shelf_top), child_anchor=(0.0, 0.0, -0.12),
    )
    return ModuleBuild("fixed_cabinet", ["red_payload"], ["cage_to_payload"],
                       {"downstream": _passthrough_downstream(ctx)})


def _build_pull_out_drawer(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    W, D = r.width, r.depth
    _box(cage, "bottom_shelf", (W - POST + 0.02, D - 0.02, 0.018), (0.0, 0.0, r.rail_top + 0.009), "wire")
    tray_half_w = 0.18 + 0.015
    rail_len = min(0.40, D - 0.06)
    rail_base_z = r.rail_top + 0.009 + 0.009 + 0.004
    for ix, xs in enumerate((-1.0, 1.0)):
        rail_x = xs * tray_half_w
        _box(cage, f"slide_rail_base_{ix}", (0.030, rail_len, 0.008), (rail_x, 0.02, rail_base_z), "wire")
        _box(cage, f"slide_rail_lip_{ix}", (0.006, rail_len - 0.02, 0.020), (rail_x - xs * 0.012, 0.02, rail_base_z + 0.014), "wire")

    payload = model.part("red_payload")
    payload.inertial = Inertial.from_geometry(Box((0.36, 0.26, 0.24)), mass=5.0, origin=Origin())
    _emit_cabinet_visuals(payload, r)
    _box(payload, "front_handle", (0.120, 0.018, 0.035), (0.0, -0.139, 0.035), "wire")
    tray_center_z = rail_base_z + 0.004 + 0.12
    drawer_travel = _clamp(D - 0.22, 0.10, 0.34)
    model.articulation(
        "cage_to_payload",
        ArticulationType.PRISMATIC,
        parent=cage,
        child=payload,
        origin=Origin(xyz=(0.0, 0.055, tray_center_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=drawer_travel),
    )
    return ModuleBuild("pull_out_drawer", ["red_payload"], ["cage_to_payload"],
                       {"downstream": _passthrough_downstream(ctx)})


def _build_shelf_stack(ctx: ModuleBuildContext) -> ModuleBuild:
    model, r = ctx.model, ctx.config
    cage = model.get_part("cage_frame")
    W, D = r.width, r.depth
    n = 3
    z_lo = r.rail_top + 0.018
    z_hi = r.toprail_bot - 0.018
    for i, z in enumerate(_spread(z_lo, z_hi, n)):
        _box(cage, f"shelf_level_{i}", (W - POST + 0.02, D - 0.02, 0.018), (0.0, 0.0, z), "wire")
    return ModuleBuild("shelf_stack", [], [], {"downstream": _passthrough_downstream(ctx)})


# --------------------------------------------------------------------------- #
# Slot graph + entry points
# --------------------------------------------------------------------------- #

WALL_FACTORIES = {
    "wire_mesh": _build_wire_mesh,
    "vertical_bar_grille": _build_vertical_bar_grille,
    "solid_perforated_panels": _build_solid_perforated_panels,
}
DOOR_FACTORIES = {
    "single_hinged_door": _build_single_hinged_door,
    "double_door": _build_double_door,
    "sliding_gate": _build_sliding_gate,
    "top_awning": _build_top_awning,
}
LATCH_FACTORIES = {
    "rotating_latch": _build_rotating_latch,
    "sliding_bolt": _build_sliding_bolt,
}
INTERIOR_FACTORIES = {
    "fixed_cabinet": _build_fixed_cabinet,
    "pull_out_drawer": _build_pull_out_drawer,
    "shelf_stack": _build_shelf_stack,
}


def _slots_for_config(r: ResolvedSafetyCageConfig) -> list[SlotSpec]:
    return [
        SlotSpec("cage_frame", {"cage_frame": _build_cage}, "cage_frame"),
        SlotSpec("wall_infill", {r.wall_infill_module: WALL_FACTORIES[r.wall_infill_module]}, r.wall_infill_module),
        SlotSpec("interior", {r.interior_module: INTERIOR_FACTORIES[r.interior_module]}, r.interior_module),
        SlotSpec("door_system", {r.door_module: DOOR_FACTORIES[r.door_module]}, r.door_module),
        SlotSpec("latch", {r.latch_module: LATCH_FACTORIES[r.latch_module]}, r.latch_module),
    ]


def build_industrial_safety_cage(
    config: SafetyCageConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="industrial_safety_cage", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)
    rng = random.Random(0)
    assemble(
        model,
        slots=_slots_for_config(r),
        rng=rng,
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_industrial_safety_cage(seed: int) -> ArticulatedObject:
    return build_industrial_safety_cage(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("wall_infill", r.wall_infill_module),
        ("mesh_density", str(r.mesh_density) if r.wall_infill_module == "wire_mesh" else "n/a"),
        ("door_system", r.door_module),
        ("latch", r.latch_module),
        ("interior", r.interior_module),
        ("base", r.base_style),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _door_part_names(r: ResolvedSafetyCageConfig) -> list[str]:
    if r.door_module == "double_door":
        return ["door_leaf_0", "door_leaf_1"]
    return ["access_door"]


def _door_keeper_post(r: ResolvedSafetyCageConfig) -> dict[str, str]:
    if r.door_module == "double_door":
        return {"door_leaf_0": "front_left_post", "door_leaf_1": "front_right_post"}
    if r.door_module == "single_hinged_door":
        return {"access_door": "front_right_post"}
    return {}


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedSafetyCageConfig) -> None:
    parts = {p.name for p in model.parts}
    cage = model.get_part("cage_frame")

    # Captured hinge barrels/stile against their cage-side hinge bosses (revolute).
    if r.door_module in ("single_hinged_door", "double_door"):
        door_parts = ["door_leaf_0", "door_leaf_1"] if r.door_module == "double_door" else ["access_door"]
        for dp in door_parts:
            if dp in parts:
                door = model.get_part(dp)
                for sfx in ("u", "l"):
                    for elem in ("upper_hinge_barrel", "lower_hinge_barrel", "hinge_stile",
                                 "upper_hinge_leaf", "lower_hinge_leaf"):
                        ctx.allow_overlap(door, cage, elem_a=elem, elem_b=f"{dp}_boss_{sfx}",
                                          reason="Hinge stile/barrel/leaf is captured against the cage hinge boss for pivot support.")
    if r.door_module == "top_awning" and "access_door" in parts:
        door = model.get_part("access_door")
        for bn in ("awning_boss_n", "awning_boss_p"):
            for elem in ("upper_hinge_barrel", "lower_hinge_barrel", "top_rail",
                         "upper_hinge_leaf", "lower_hinge_leaf"):
                ctx.allow_overlap(door, cage, elem_a=elem, elem_b=bn,
                                  reason="Awning top rail/barrel/leaf is captured against the cage hinge boss at the hinge line.")
    if r.door_module == "sliding_gate" and "access_door" in parts:
        door = model.get_part("access_door")
        for elem in ("hanger_roller_0", "hanger_roller_1", "hanger_bracket_0", "hanger_bracket_1"):
            ctx.allow_overlap(door, cage, elem_a=elem, elem_b="door_track",
                              reason="Sliding-gate hanger hardware rides inside the overhead track channel.")

    # Latch keeper engagement (door seats against the keeper when closed).
    for dp in _door_part_names(r):
        if dp in parts:
            door = model.get_part(dp)
            for elem in ("free_stile", "middle_rail", "bottom_rail"):
                ctx.allow_overlap(door, cage, elem_a=elem, elem_b="latch_keeper",
                                  reason="Latch keeper engagement: the door frame seats against the keeper when closed.")

    # Latch is a small hardware sub-assembly bolted onto and fully captured by the
    # primary door leaf at its free edge; its pin/hasp/bolt/knob intentionally seat
    # into the door frame and mesh. Part-scoped allowance (latch<->its own door
    # only) -- never a door<->cage overlap.
    if "latch_handle" in parts:
        latch = model.get_part("latch_handle")
        door = model.get_part(r.primary_door_part)
        ctx.allow_overlap(latch, door,
                          reason="Latch hardware is bolted onto and captured by the door leaf at its free edge.")

    # Pull-out tray captured on its slide rails; sequenced with the door.
    if r.interior_module == "pull_out_drawer" and "red_payload" in parts:
        payload = model.get_part("red_payload")
        ctx.allow_overlap(cage, payload, elem_a="slide_rail_lip_0", elem_b="red_cabinet",
                          reason="Tray edge rides captured inside the slide-rail lip.")
        ctx.allow_overlap(cage, payload, elem_a="slide_rail_lip_1", elem_b="red_cabinet",
                          reason="Tray edge rides captured inside the slide-rail lip.")
        for dp in _door_part_names(r):
            if dp in parts:
                ctx.allow_overlap(payload, model.get_part(dp),
                                  reason="Sequenced mechanism: the drawer is pulled out only once the access door is open; travel through the closed-door plane is allowed by the operating sequence.")
        # The latch hardware is bolted rigidly onto the primary door leaf and moves
        # as one with it; it shares the identical operating-sequence exemption as the
        # door<->drawer pair above (same sweep, same closed-door plane the drawer
        # travels through only when the door is open).
        if "latch_handle" in parts:
            ctx.allow_overlap(payload, model.get_part("latch_handle"),
                              reason="Sequenced mechanism: the latch rides on the door leaf; the drawer is pulled out only once the door is open, so latch/drawer travel through the closed-door plane is allowed by the operating sequence.")


def _expect_door_joint(ctx: TestContext, model: ArticulatedObject, r: ResolvedSafetyCageConfig) -> None:
    joints = {j.name: j for j in getattr(model, "articulations", [])}
    door_joints = [j for n, j in joints.items() if n.startswith("cage_to_") and ("door" in n or "leaf" in n)]
    ctx.check("door_joint_present", len(door_joints) >= 1,
              details=f"door joints={[j.name for j in door_joints]}")
    if r.door_module in ("single_hinged_door", "double_door", "top_awning"):
        ok = all(j.articulation_type == ArticulationType.REVOLUTE for j in door_joints)
        ctx.check("door_joint_revolute", ok, details=f"types={[j.articulation_type for j in door_joints]}")
    elif r.door_module == "sliding_gate":
        ok = all(j.articulation_type == ArticulationType.PRISMATIC for j in door_joints)
        ctx.check("door_joint_prismatic", ok, details=f"types={[j.articulation_type for j in door_joints]}")


def run_industrial_safety_cage_tests(
    model: ArticulatedObject,
    config: SafetyCageConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_door_joint(ctx, model, r)

    # Rule 5: full-travel sampled overlap check.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    joints = {j.name: j for j in getattr(model, "articulations", [])}

    # Targeted door motion (open->displacement).
    primary_door_joint = None
    for n in ("cage_to_access_door", "cage_to_door_leaf_0"):
        if n in joints:
            primary_door_joint = joints[n]
            break
    if primary_door_joint is not None:
        dp = model.get_part(r.primary_door_part)
        rest = ctx.part_world_aabb(dp)
        upper = primary_door_joint.motion_limits.upper if primary_door_joint.motion_limits else 1.0
        with ctx.pose({primary_door_joint: upper}):
            moved = ctx.part_world_aabb(dp)
        disp = 0.0
        if rest is not None and moved is not None:
            disp = max(abs(moved[0][i] - rest[0][i]) + abs(moved[1][i] - rest[1][i]) for i in range(3))
        ctx.check("door actuates with visible displacement", disp > 0.05,
                  details=f"rest={rest}, moved={moved}, disp={disp:.3f}")

    # Targeted latch motion.
    if "door_to_latch" in joints:
        lj = joints["door_to_latch"]
        latch = model.get_part("latch_handle")
        rest = ctx.part_world_aabb(latch)
        val = (lj.motion_limits.upper if lj.motion_limits and lj.motion_limits.upper else 0.5)
        with ctx.pose({lj: val}):
            moved = ctx.part_world_aabb(latch)
        moved_ok = rest is not None and moved is not None and any(
            abs(moved[k][i] - rest[k][i]) > 0.005 for k in (0, 1) for i in range(3)
        )
        ctx.check("latch actuates", moved_ok, details=f"rest={rest}, moved={moved}")

    # Targeted drawer motion.
    if r.interior_module == "pull_out_drawer" and "cage_to_payload" in joints:
        dj = joints["cage_to_payload"]
        if dj.articulation_type == ArticulationType.PRISMATIC:
            payload = model.get_part("red_payload")
            rest = ctx.part_world_position(payload)
            upper = dj.motion_limits.upper if dj.motion_limits else 0.28
            with ctx.pose({dj: upper}):
                ext = ctx.part_world_position(payload)
            ctx.check("drawer extends forward (-Y)",
                      rest is not None and ext is not None and ext[1] < rest[1] - 0.08,
                      details=f"rest={rest}, ext={ext}")

    return ctx.report()


__all__ = [
    "SafetyCageConfig",
    "ResolvedSafetyCageConfig",
    "SafetyCagePalette",
    "WallInfillModule",
    "DoorModule",
    "LatchModule",
    "InteriorModule",
    "BaseStyle",
    "build_industrial_safety_cage",
    "build_seeded_industrial_safety_cage",
    "config_from_seed",
    "resolve_config",
    "run_industrial_safety_cage_tests",
    "slot_choices_for_seed",
]
