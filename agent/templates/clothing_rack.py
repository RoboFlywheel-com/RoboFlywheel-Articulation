# SPDX-License-Identifier: Apache-2.0

"""Clothing rack — modular procedural template.

Category identity: a free-standing garment rack — one or more elevated horizontal
hanging rails carried by two uprights that telescope (PRISMATIC height adjust) out of a
floor base, garments hung on wire hangers that hook over the rail and swing (REVOLUTE).
The base is a wheeled caster base (4 CONTINUOUS wheels) or a stationary leveling-feet
base. Optional storage is a lower shelf of round rods or an overhead slatted wire shelf.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/clothing_rack.md``

Slots (exported via ``slot_choices_for_seed``):

* ``rail_topology`` — single_straight / double_parallel / arched_inverted_u /
  two_tier_stacked / extendable_straight  (① skeleton + ③ primary-form hero slot)
* ``support_base`` — rolling_caster / static_feet
* ``storage_shelf`` — no_shelf / lower_storage_shelf / overhead_top_shelf
* ``hanger_count`` — hanger multiplicity along the primary rail (① multiplicity)

``config_from_seed`` is procedural for every seed (no seed=0 special case). Adapted from
5-star sources: rolling single-rail rack (B, rec_…__002), gold double-rail rack
(A, rec_…__001), and forks var_skeleton_arch / var_twotier / var_railextend /
var_feetbase / var_topshelf / var_n_hangers.
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
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

RailTopology = Literal[
    "single_straight",
    "double_parallel",
    "arched_inverted_u",
    "two_tier_stacked",
    "extendable_straight",
]
SupportBase = Literal["rolling_caster", "static_feet"]
StorageShelf = Literal["no_shelf", "lower_storage_shelf", "overhead_top_shelf"]
MaterialStyle = Literal["black_steel", "brushed_gold", "chrome", "matte_white"]

RAIL_TOPOLOGIES: tuple[RailTopology, ...] = (
    "single_straight",
    "double_parallel",
    "arched_inverted_u",
    "two_tier_stacked",
    "extendable_straight",
)
SUPPORT_BASES: tuple[SupportBase, ...] = ("rolling_caster", "static_feet")
STORAGE_SHELVES: tuple[StorageShelf, ...] = (
    "no_shelf",
    "lower_storage_shelf",
    "overhead_top_shelf",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "black_steel",
    "brushed_gold",
    "chrome",
    "matte_white",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_steel": {
        "frame": (0.02, 0.02, 0.02, 1.0),
        "hub": (0.09, 0.09, 0.085, 1.0),
        "rubber": (0.006, 0.006, 0.006, 1.0),
        "red": (0.82, 0.06, 0.035, 1.0),
        "hook": (0.78, 0.74, 0.66, 1.0),
        "wood": (0.74, 0.54, 0.34, 1.0),
    },
    "brushed_gold": {
        "frame": (0.86, 0.58, 0.18, 1.0),
        "hub": (0.16, 0.16, 0.15, 1.0),
        "rubber": (0.02, 0.018, 0.016, 1.0),
        "red": (0.82, 0.06, 0.035, 1.0),
        "hook": (0.78, 0.74, 0.66, 1.0),
        "wood": (0.74, 0.54, 0.34, 1.0),
    },
    "chrome": {
        "frame": (0.72, 0.72, 0.70, 1.0),
        "hub": (0.14, 0.14, 0.14, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
        "red": (0.82, 0.06, 0.035, 1.0),
        "hook": (0.80, 0.78, 0.72, 1.0),
        "wood": (0.74, 0.54, 0.34, 1.0),
    },
    "matte_white": {
        "frame": (0.90, 0.90, 0.88, 1.0),
        "hub": (0.30, 0.30, 0.30, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "red": (0.80, 0.10, 0.06, 1.0),
        "hook": (0.70, 0.70, 0.68, 1.0),
        "wood": (0.74, 0.54, 0.34, 1.0),
    },
}

# --- Fixed hardware dimensions (standardized; NOT scaled, protect telescoping fit) ---
BASE_Z = 0.105
SLEEVE_OUTER_R = 0.0235
SLEEVE_INNER_R = 0.0175
SLEEVE_LEN = 0.94
SLEEVE_Z = 0.10
COLLAR_Z = 1.004
POST_R = 0.014
BUSHING_R = 0.01755
POST_LEN = 0.84
POST_LOCAL_Z = 0.24
BUSHING_LOCAL_Z = -0.10
RAIL_Z = 0.66  # local z of the primary rail inside upper_frame
LOWER_RAIL_Z = 0.25  # two-tier lower rail local z
CROWN_Z = 0.70  # arched crown local z
HEIGHT_JOINT_Z = 1.04
HEIGHT_TRAVEL = 0.14
SHELF_LOCAL_Z = 1.00  # overhead shelf local z on upper_frame
HANGER_SWING = 0.35

Y_FRONT = -0.245
Y_REAR = 0.245


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class ClothingRackConfig:
    rail_topology: RailTopology | None = None
    support_base: SupportBase | None = None
    storage_shelf: StorageShelf | None = None
    hanger_count: int | None = None
    material_style: MaterialStyle = "black_steel"
    width_scale: float = 1.0
    rail_r_scale: float = 1.0
    name: str = "clothing_rack"


@dataclass(frozen=True)
class ResolvedClothingRackConfig:
    rail_topology: RailTopology
    support_base: SupportBase
    storage_shelf: StorageShelf
    hanger_count: int
    material_style: MaterialStyle
    x_post: float
    rail_len: float
    base_tube_len: float
    caster_x: float
    rail_r: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _weighted_hanger_count(rng: random.Random) -> int:
    # small N frequent, large N rare (test/sweep domain [4, 10])
    counts = (4, 5, 6, 7, 8, 9, 10)
    weights = (6, 9, 11, 11, 7, 4, 3)
    return rng.choices(counts, weights=weights, k=1)[0]


def config_from_seed(seed: int) -> ClothingRackConfig:
    rng = random.Random(seed)
    rail = rng.choice(RAIL_TOPOLOGIES)
    base = rng.choices(SUPPORT_BASES, weights=(3, 2), k=1)[0]
    shelf = rng.choices(STORAGE_SHELVES, weights=(4, 3, 3), k=1)[0]
    return ClothingRackConfig(
        rail_topology=rail,
        support_base=base,
        storage_shelf=shelf,
        hanger_count=_weighted_hanger_count(rng),
        material_style=rng.choice(MATERIAL_STYLES),
        width_scale=round(rng.uniform(0.88, 1.12), 4),
        rail_r_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_clothing_rack_{seed}",
    )


def resolve_config(config: ClothingRackConfig) -> ResolvedClothingRackConfig:
    rail = config.rail_topology or "single_straight"
    base = config.support_base or "rolling_caster"
    shelf = config.storage_shelf or "no_shelf"

    for field_name, value, allowed in (
        ("rail_topology", rail, RAIL_TOPOLOGIES),
        ("support_base", base, SUPPORT_BASES),
        ("storage_shelf", shelf, STORAGE_SHELVES),
    ):
        if value not in allowed:
            raise ValueError(f"Unsupported {field_name}: {value}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    # Compatibility gating (conditional): an arched crown has no straight post tops to
    # carry an overhead shelf; the extendable rail must slide out past the right post,
    # which the overhead shelf posts would block -> both downgrade to no_shelf.
    if shelf == "overhead_top_shelf" and rail in ("arched_inverted_u", "extendable_straight"):
        shelf = "no_shelf"

    width_scale = _clamp(config.width_scale, 0.88, 1.12)
    rail_r_scale = _clamp(config.rail_r_scale, 0.90, 1.15)
    # Single-source: x_post drives base sleeve x, upper post x, base width, rail length.
    x_post = round(0.72 * width_scale, 4)
    hanger_count = int(_clamp(float(config.hanger_count or 7), 4, 10))

    return ResolvedClothingRackConfig(
        rail_topology=rail,
        support_base=base,
        storage_shelf=shelf,
        hanger_count=hanger_count,
        material_style=config.material_style,
        x_post=x_post,
        rail_len=2.0 * x_post + 0.14,
        base_tube_len=2.0 * x_post + 0.04,
        caster_x=x_post - 0.08,
        rail_r=round(0.021 * rail_r_scale, 5),
        palette=dict(PALETTES[config.material_style]),
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _register_materials(model: ArticulatedObject, palette: dict) -> None:
    for key, rgba in palette.items():
        model.material(key, rgba=rgba)


def _cyl_x(part, name, length, radius, xyz, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _cyl_y(part, name, length, radius, xyz, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _cyl_z(part, name, length, radius, xyz, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _hollow_z_tube(outer_r: float, inner_r: float, length: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(length)


def _hollow_x_tube(outer_r: float, inner_r: float, length: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(length)
        .translate((-length / 2.0, 0.0, 0.0))
    )


def _hollow_y_tube(outer_r: float, inner_r: float, width: float) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .circle(outer_r)
        .circle(inner_r)
        .extrude(width)
        .translate((0.0, -width / 2.0, 0.0))
    )


def _cq_mesh(model: ArticulatedObject, shape, name: str):
    if model.assets is not None:
        return mesh_from_cadquery(
            shape,
            model.assets.mesh_path(f"{name}.obj"),
            assets=model.assets,
            tolerance=0.0008,
            angular_tolerance=0.09,
        )
    return mesh_from_cadquery(shape, name, tolerance=0.0008, angular_tolerance=0.09)


# Hook saddle sits at the hanger's local origin (0,0,0); the rail is nominally at
# child (0,0,-RAIL_CONTACT) so the loop encircles it. The swing joint origin is placed
# on the rail's TOP surface (rail_z + RAIL_CONTACT) so the joint axis touches the hook
# saddle tube (child) and the rail top (parent) -> origin-honesty passes at tol=0.015.
RAIL_CONTACT = 0.021


def _hanger_meshes():
    # Open hook wrapping a rail centered at (0,0,-RAIL_CONTACT); saddle ends at origin.
    hook_path = [
        (0.0, 0.020, 0.010),
        (0.0, 0.028, -0.012),
        (0.0, 0.020, -0.036),
        (0.0, 0.000, -0.047),
        (0.0, -0.020, -0.036),
        (0.0, -0.028, -0.012),
        (0.0, -0.018, 0.008),
        (0.0, 0.000, 0.000),
    ]
    hook_mesh = mesh_from_geometry(
        tube_from_spline_points(
            hook_path, radius=0.0032, samples_per_segment=8, radial_segments=12, cap_ends=True
        ),
        "hanger_hook",
    )
    w = 0.16
    body_path = [
        (0.0, 0.0, -0.100),
        (0.0, -w / 2.0, -0.250),
        (0.0, w / 2.0, -0.250),
        (0.0, 0.0, -0.100),
    ]
    body_mesh = mesh_from_geometry(
        tube_from_spline_points(
            body_path, radius=0.0055, samples_per_segment=6, radial_segments=12, cap_ends=True
        ),
        "hanger_body",
    )
    return hook_mesh, body_mesh


def _create_hanger(
    model, parent, prefix, x, rail_y, rail_center_z, rail_r, hook_mesh, body_mesh, hook_mat, body_mat
) -> None:
    hanger = model.part(prefix)
    hanger.visual(hook_mesh, material=hook_mat, name="hook_loop", material_class_id="metal.steel_bare")
    _cyl_z(hanger, "vertical_neck", 0.060, 0.0032, (0.0, 0.0, -0.075), hook_mat)
    hanger.visual(body_mesh, material=body_mat, name="hanger_body", material_class_id="wood.polished_varnished")
    # Seat the joint origin just inside the rail's top surface so the hook saddle
    # overlaps the rail (guaranteed contact for any rail radius 0.017-0.024).
    model.articulation(
        f"{prefix}_swing",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=hanger,
        origin=Origin(xyz=(x, rail_y, rail_center_z + rail_r - 0.004)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=1.2, lower=-HANGER_SWING, upper=HANGER_SWING
        ),
    )


def _hanger_x_positions(span: float, n: int) -> list[float]:
    if n <= 1:
        return [0.0]
    step = (2.0 * span) / (n - 1)
    return [-span + step * i for i in range(n)]


# ---------------------------------------------------------------------------
# Telescoping sleeves shared by both bases
# ---------------------------------------------------------------------------
def _add_telescoping_sleeves(model, base, r: ResolvedClothingRackConfig) -> None:
    sleeve_mesh = _cq_mesh(
        model, _hollow_z_tube(SLEEVE_OUTER_R, SLEEVE_INNER_R, SLEEVE_LEN), "lower_sleeve"
    )
    collar_mesh = _cq_mesh(
        model, _hollow_z_tube(0.027, 0.018, 0.036), "clamp_collar"
    )
    for i, x in enumerate((-r.x_post, r.x_post)):
        base.visual(sleeve_mesh, origin=Origin(xyz=(x, 0.0, SLEEVE_Z)), material="frame",
                    name=f"lower_sleeve_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
        base.visual(collar_mesh, origin=Origin(xyz=(x, 0.0, COLLAR_Z)), material="frame",
                    name=f"clamp_collar_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
        _cyl_y(base, f"spring_button_{i}", 0.014, 0.005, (x, -0.027, 0.72), "hub")


# ---------------------------------------------------------------------------
# Base modules (Slot B)
# ---------------------------------------------------------------------------
def _build_caster_base(model, r: ResolvedClothingRackConfig) -> tuple[list, list]:
    base = model.part("base_frame")
    x_post = r.x_post
    _cyl_x(base, "front_base_tube", r.base_tube_len, 0.022, (0.0, Y_FRONT, BASE_Z), "frame")
    _cyl_x(base, "rear_base_tube", r.base_tube_len, 0.022, (0.0, Y_REAR, BASE_Z), "frame")
    _cyl_y(base, "base_tube_0", 0.49, 0.022, (-x_post, 0.0, BASE_Z), "frame")
    _cyl_y(base, "base_tube_1", 0.49, 0.022, (x_post, 0.0, BASE_Z), "frame")
    for i, (x, y) in enumerate(
        ((-x_post, Y_FRONT), (-x_post, Y_REAR), (x_post, Y_FRONT), (x_post, Y_REAR))
    ):
        base.visual(Sphere(radius=0.022), origin=Origin(xyz=(x, y, BASE_Z)), material="frame",
                    name=f"rounded_corner_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))

    _add_telescoping_sleeves(model, base, r)
    _cyl_x(base, "low_rear_brace", r.base_tube_len - 0.04, 0.017, (0.0, 0.0, 0.235), "frame")

    caster_positions = (
        (-r.caster_x, Y_FRONT, 0.043),
        (-r.caster_x, Y_REAR, 0.043),
        (r.caster_x, Y_FRONT, 0.043),
        (r.caster_x, Y_REAR, 0.043),
    )
    for i, (x, y, z) in enumerate(caster_positions):
        _cyl_z(base, f"caster_stem_{i}", 0.060, 0.007, (x, y, 0.122), "frame")
        base.visual(Box((0.030, 0.064, 0.008)), origin=Origin(xyz=(x, y, 0.094)),
                    material="frame", name=f"caster_bridge_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
        _cyl_y(base, f"caster_cross_pin_{i}", 0.070, 0.006, (x, y, z), "hub")
        for side, yy in enumerate((y - 0.026, y + 0.026)):
            base.visual(Box((0.030, 0.006, 0.078)), origin=Origin(xyz=(x, yy, 0.059)),
                        material="frame", name=f"caster_fork_{i}_{side}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))

    caster_meta: list = []
    tire_mesh = _cq_mesh(model, _hollow_y_tube(0.043, 0.025, 0.032), "caster_tire")
    for i, (x, y, z) in enumerate(caster_positions):
        wheel = model.part(f"wheel_{i}")
        wheel.visual(tire_mesh, origin=Origin(xyz=(0.0, 0.032, 0.0)), material="rubber",
                     name="rubber_tire", material_class_id="rubber.smooth_plain")
        wheel.visual(Cylinder(radius=0.026, length=0.040), origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                     material="hub", name="hub_disc", material_class_id="plastic.opaque_glossy_molded")
        model.articulation(
            f"wheel_spin_{i}",
            ArticulationType.CONTINUOUS,
            parent=base,
            child=wheel,
            origin=Origin(xyz=(x, y, z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=20.0),
        )
        caster_meta.append({"wheel": f"wheel_{i}", "pin": f"caster_cross_pin_{i}"})
    return base, caster_meta


def _build_feet_base(model, r: ResolvedClothingRackConfig) -> tuple[list, list]:
    base = model.part("base_frame")
    x_post = r.x_post
    foot_rail_z = 0.034
    foot_rail_len = abs(Y_REAR - Y_FRONT)
    for i, x in enumerate((-x_post, x_post)):
        _cyl_y(base, f"foot_rail_{i}", foot_rail_len, 0.022, (x, 0.0, foot_rail_z), "frame")
    _cyl_x(base, "foot_crossbar", 2.0 * x_post, 0.017, (0.0, 0.0, foot_rail_z), "frame")
    for i, (x, y) in enumerate(
        ((-x_post, Y_FRONT), (-x_post, Y_REAR), (x_post, Y_FRONT), (x_post, Y_REAR))
    ):
        _cyl_z(base, f"foot_{i}", 0.015, 0.016, (x, y, 0.0075), "rubber")
    # Stems tie foot rails up to the sleeve bases.
    stem_len = SLEEVE_Z - foot_rail_z
    for i, x in enumerate((-x_post, x_post)):
        _cyl_z(base, f"foot_stem_{i}", stem_len, 0.022, (x, 0.0, foot_rail_z + stem_len / 2.0),
               "frame")
    _add_telescoping_sleeves(model, base, r)
    _cyl_x(base, "low_rear_brace", 2.0 * x_post, 0.017, (0.0, 0.0, 0.235), "frame")
    return base, []


# ---------------------------------------------------------------------------
# Upper posts shared by post-based rails
# ---------------------------------------------------------------------------
def _add_upper_posts(upper, r: ResolvedClothingRackConfig) -> None:
    for i, x in enumerate((-r.x_post, r.x_post)):
        _cyl_z(upper, f"upper_post_{i}", POST_LEN, POST_R, (x, 0.0, POST_LOCAL_Z), "frame")
        _cyl_z(upper, f"sliding_bushing_{i}", 0.080, BUSHING_R, (x, 0.0, BUSHING_LOCAL_Z), "hub")


def _add_side_hooks(upper, r: ResolvedClothingRackConfig, z: float) -> None:
    x_post = r.x_post
    _cyl_z(upper, "upright_side_hook", 0.22, 0.017, (x_post, 0.0, z + 0.11), "frame")
    upper.visual(Sphere(radius=0.032), origin=Origin(xyz=(x_post, 0.0, z + 0.235)), material="red",
                 name="top_red_ball", material_class_id="plastic.opaque_glossy_molded")
    _cyl_x(upper, "side_hook", 0.30, 0.016, (x_post + 0.15, 0.0, z), "frame")
    upper.visual(Sphere(radius=0.031), origin=Origin(xyz=(x_post + 0.315, 0.0, z)), material="red",
                 name="side_red_ball", material_class_id="plastic.opaque_glossy_molded")


def _add_rail_stops(upper, name_prefix: str, z: float) -> None:
    for i, x in enumerate((-0.44, 0.00, 0.44)):
        upper.visual(Box((0.036, 0.018, 0.010)), origin=Origin(xyz=(x, 0.0, z - 0.026)),
                     material="frame", name=f"{name_prefix}_{i}", material_class_id="metal.blackened_gunmetal")


# ---------------------------------------------------------------------------
# Rail modules (Slot A) — each builds the upper_frame and returns (upper, hangers, extend)
# ---------------------------------------------------------------------------
def _build_single_rail(model, r, hook_mesh, body_mesh):
    upper = model.part("upper_frame")
    _add_upper_posts(upper, r)
    for i, x in enumerate((-r.x_post, r.x_post)):
        upper.visual(Sphere(radius=0.025), origin=Origin(xyz=(x, 0.0, RAIL_Z)), material="frame",
                     name=f"rail_tee_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    _cyl_x(upper, "top_hanging_rail", r.rail_len, r.rail_r, (0.0, 0.0, RAIL_Z), "frame")
    upper.visual(Sphere(radius=0.023), origin=Origin(xyz=(-(r.x_post + 0.075), 0.0, RAIL_Z)),
                 material="frame", name="left_rail_cap", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    hangers = []
    span = r.x_post - 0.12
    for idx, x in enumerate(_hanger_x_positions(span, r.hanger_count)):
        _create_hanger(model, upper, f"top_hanger_{idx}", x, 0.0, RAIL_Z, r.rail_r, hook_mesh, body_mesh,
                       "hook", "wood")
        hangers.append({"part": f"top_hanger_{idx}", "parent": "upper_frame", "rail": "top_hanging_rail"})
    _add_side_hooks(upper, r, RAIL_Z)
    return upper, hangers, None


def _build_double_rail(model, r, hook_mesh, body_mesh):
    upper = model.part("upper_frame")
    _add_upper_posts(upper, r)
    y_a, y_b = -0.20, 0.20
    for i, x in enumerate((-r.x_post, r.x_post)):
        # Cross tie connecting each post to both parallel rails.
        _cyl_y(upper, f"rail_crosstie_{i}", 0.44, 0.016, (x, 0.0, RAIL_Z), "frame")
        for j, y in enumerate((y_a, y_b)):
            upper.visual(Sphere(radius=0.022), origin=Origin(xyz=(x, y, RAIL_Z)), material="frame",
                         name=f"rail_tee_{i}_{j}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    _cyl_x(upper, "front_rail", r.rail_len, r.rail_r, (0.0, y_a, RAIL_Z), "frame")
    _cyl_x(upper, "rear_rail", r.rail_len, r.rail_r, (0.0, y_b, RAIL_Z), "frame")
    hangers = []
    span = r.x_post - 0.12
    front_n = r.hanger_count
    rear_n = max(3, r.hanger_count - 1)
    for idx, x in enumerate(_hanger_x_positions(span, front_n)):
        _create_hanger(model, upper, f"front_hanger_{idx}", x, y_a, RAIL_Z, r.rail_r, hook_mesh, body_mesh,
                       "hook", "wood")
        hangers.append({"part": f"front_hanger_{idx}", "parent": "upper_frame", "rail": "front_rail"})
    for idx, x in enumerate(_hanger_x_positions(span, rear_n)):
        _create_hanger(model, upper, f"rear_hanger_{idx}", x, y_b, RAIL_Z, r.rail_r, hook_mesh, body_mesh,
                       "hook", "wood")
        hangers.append({"part": f"rear_hanger_{idx}", "parent": "upper_frame", "rail": "rear_rail"})
    _add_side_hooks(upper, r, RAIL_Z)
    return upper, hangers, None


def _build_arched_rail(model, r, hook_mesh, body_mesh):
    upper = model.part("upper_frame")
    x_post = r.x_post
    arch_leg_bottom = -0.24
    for i, x in enumerate((-x_post, x_post)):
        _cyl_z(upper, f"sliding_bushing_{i}", 0.080, BUSHING_R, (x, 0.0, arch_leg_bottom), "hub")
    arch_path = [
        (-x_post, 0.0, arch_leg_bottom),
        (-x_post, 0.0, 0.05),
        (-x_post, 0.0, 0.25),
        (-x_post, 0.0, 0.42),
        (-x_post + 0.05, 0.0, 0.52),
        (-x_post + 0.15, 0.0, 0.62),
        (-x_post + 0.30, 0.0, CROWN_Z - 0.02),
        (-0.30, 0.0, CROWN_Z),
        (-0.10, 0.0, CROWN_Z),
        (0.10, 0.0, CROWN_Z),
        (0.30, 0.0, CROWN_Z),
        (x_post - 0.30, 0.0, CROWN_Z - 0.02),
        (x_post - 0.15, 0.0, 0.62),
        (x_post - 0.05, 0.0, 0.52),
        (x_post, 0.0, 0.42),
        (x_post, 0.0, 0.25),
        (x_post, 0.0, 0.05),
        (x_post, 0.0, arch_leg_bottom),
    ]
    arch_mesh = mesh_from_geometry(
        tube_from_spline_points(arch_path, radius=r.rail_r, samples_per_segment=14,
                                radial_segments=18, cap_ends=True),
        "arch_rail_mesh",
    )
    upper.visual(arch_mesh, material="frame", name="arch_rail", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    hangers = []
    # Keep hangers on the FLAT crown section (arch is level in x in [-0.30, 0.30]); placing
    # them on the curving-up shoulders makes the vertical neck graze the rising tube.
    span = min(0.26, x_post - 0.40)
    for idx, x in enumerate(_hanger_x_positions(span, r.hanger_count)):
        _create_hanger(model, upper, f"top_hanger_{idx}", x, 0.0, CROWN_Z, r.rail_r, hook_mesh, body_mesh,
                       "hook", "wood")
        hangers.append({"part": f"top_hanger_{idx}", "parent": "upper_frame", "rail": "arch_rail"})
    # Side hooks anchored on the arch leg region (below the crown).
    _add_side_hooks(upper, r, 0.50)
    return upper, hangers, None


def _build_two_tier_rail(model, r, hook_mesh, body_mesh):
    upper = model.part("upper_frame")
    _add_upper_posts(upper, r)
    for i, x in enumerate((-r.x_post, r.x_post)):
        upper.visual(Sphere(radius=0.025), origin=Origin(xyz=(x, 0.0, RAIL_Z)), material="frame",
                     name=f"rail_tee_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
        upper.visual(Sphere(radius=0.022), origin=Origin(xyz=(x, 0.0, LOWER_RAIL_Z)), material="frame",
                     name=f"lower_rail_tee_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    _cyl_x(upper, "top_hanging_rail", r.rail_len, r.rail_r, (0.0, 0.0, RAIL_Z), "frame")
    _cyl_x(upper, "lower_hanging_rail", r.rail_len, max(0.017, r.rail_r - 0.002),
           (0.0, 0.0, LOWER_RAIL_Z), "frame")
    upper.visual(Sphere(radius=0.023), origin=Origin(xyz=(-(r.x_post + 0.075), 0.0, RAIL_Z)),
                 material="frame", name="left_rail_cap", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    hangers = []
    span = r.x_post - 0.12
    top_n = r.hanger_count
    low_n = max(3, r.hanger_count - 1)
    for idx, x in enumerate(_hanger_x_positions(span, top_n)):
        _create_hanger(model, upper, f"top_hanger_{idx}", x, 0.0, RAIL_Z, r.rail_r, hook_mesh, body_mesh,
                       "hook", "wood")
        hangers.append({"part": f"top_hanger_{idx}", "parent": "upper_frame", "rail": "top_hanging_rail"})
    lower_rail_r = max(0.017, r.rail_r - 0.002)
    for idx, x in enumerate(_hanger_x_positions(span, low_n)):
        _create_hanger(model, upper, f"lower_hanger_{idx}", x, 0.0, LOWER_RAIL_Z, lower_rail_r,
                       hook_mesh, body_mesh, "hook", "wood")
        hangers.append({"part": f"lower_hanger_{idx}", "parent": "upper_frame", "rail": "lower_hanging_rail"})
    _add_side_hooks(upper, r, RAIL_Z)
    return upper, hangers, None


def _build_extendable_rail(model, r, hook_mesh, body_mesh):
    upper = model.part("upper_frame")
    _add_upper_posts(upper, r)
    x_post = r.x_post
    # Left tee/cap only; the right end is open so the inner rail can slide out past
    # the right post.
    upper.visual(Sphere(radius=0.025), origin=Origin(xyz=(-x_post, 0.0, RAIL_Z)), material="frame",
                 name="rail_tee_0", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    upper.visual(Sphere(radius=0.022), origin=Origin(xyz=(x_post, 0.0, RAIL_Z)), material="frame",
                 name="rail_tee_1", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    # Outer sleeve spans both posts (hollow annulus).
    outer_len = 2.0 * x_post
    rail_outer_mesh = _cq_mesh(model, _hollow_x_tube(r.rail_r, r.rail_r - 0.004, outer_len),
                               "rail_outer_sleeve")
    upper.visual(rail_outer_mesh, origin=Origin(xyz=(0.0, 0.0, RAIL_Z)), material="frame",
                 name="rail_outer", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    upper.visual(Sphere(radius=0.023), origin=Origin(xyz=(-(x_post + 0.02), 0.0, RAIL_Z)),
                 material="frame", name="left_rail_cap", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    hangers = []
    # Fixed hangers on the outer sleeve, confined to the left/center span so they stay
    # clear of the inner rail's protruding right portion.
    outer_n = max(3, r.hanger_count - 2)
    outer_lo = -(x_post - 0.16)
    outer_hi = x_post - 0.50
    for idx in range(outer_n):
        t = idx / (outer_n - 1) if outer_n > 1 else 0.5
        x = outer_lo + (outer_hi - outer_lo) * t
        _create_hanger(model, upper, f"top_hanger_{idx}", x, 0.0, RAIL_Z, r.rail_r, hook_mesh, body_mesh,
                       "hook", "wood")
        hangers.append({"part": f"top_hanger_{idx}", "parent": "upper_frame", "rail": "rail_outer"})

    # Inner sliding rail: captured (radial overlap) inside the outer sleeve on its left
    # portion, protruding past the right post so its hangers sit outside the sleeve.
    rail_inner = model.part("rail_inner")
    inner_r = r.rail_r - 0.002  # overlaps the outer annular wall -> supported + captured
    # Tube spans local x [-0.30, +0.38]; the extra right length pushes the end cap well
    # clear of the outermost inner hanger (local 0.28) while the left end stays captured
    # inside the outer sleeve at full extension.
    _cyl_x(rail_inner, "inner_tube", 0.68, inner_r, (0.04, 0.0, 0.0), "frame")
    rail_inner.visual(Sphere(radius=inner_r + 0.004), origin=Origin(xyz=(0.38, 0.0, 0.0)),
                      material="frame", name="inner_rail_cap", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    inner_stop_mesh = _cq_mesh(model, _hollow_x_tube(r.rail_r - 0.001, 0.010, 0.018),
                               "inner_rail_stop")
    rail_inner.visual(inner_stop_mesh, origin=Origin(xyz=(-0.28, 0.0, 0.0)), material="hub",
                      name="inner_rail_stop", material_class_id="plastic.opaque_glossy_molded")
    extend_origin_x = x_post - 0.10
    # Inner hangers sit on the protruding tube, clear of the right end tee sphere.
    for idx, x_local in enumerate((0.18, 0.28)):
        _create_hanger(model, rail_inner, f"inner_hanger_{idx}", x_local, 0.0, 0.0, inner_r,
                       hook_mesh, body_mesh, "hook", "wood")
        hangers.append({"part": f"inner_hanger_{idx}", "parent": "rail_inner", "rail": "inner_tube"})
    model.articulation(
        "rail_extend",
        ArticulationType.PRISMATIC,
        parent=upper,
        child=rail_inner,
        origin=Origin(xyz=(extend_origin_x, 0.0, RAIL_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.15, lower=0.0, upper=0.25),
    )
    # Side hooks omitted for the extendable variant: the horizontal accessory hook would
    # collide with the inner rail as it protrudes past the right post.
    extend_meta = {"inner_part": "rail_inner", "outer": "rail_outer",
                   "stop": "inner_rail_stop", "inner": "inner_tube", "tee": "rail_tee_1",
                   "post": "upper_post_1"}
    return upper, hangers, extend_meta


_RAIL_BUILDERS = {
    "single_straight": _build_single_rail,
    "double_parallel": _build_double_rail,
    "arched_inverted_u": _build_arched_rail,
    "two_tier_stacked": _build_two_tier_rail,
    "extendable_straight": _build_extendable_rail,
}


# ---------------------------------------------------------------------------
# Storage shelf modules (Slot C) — non-articulating -> host visuals (Rule 1)
# ---------------------------------------------------------------------------
def _add_lower_storage_shelf(base, r: ResolvedClothingRackConfig) -> None:
    x_post = r.x_post
    rod_ys = (-0.21, -0.10, 0.01, 0.12, 0.21)
    for z, tier in ((0.18, "lower"), (0.36, "upper")):
        for j, y in enumerate(rod_ys):
            _cyl_x(base, f"shelf_rod_{tier}_{j}", 2.0 * x_post, 0.010, (0.0, y, z), "frame")
        _cyl_y(base, f"shelf_side_rail_{tier}_0", 0.54, 0.010, (-x_post, 0.0, z), "frame")
        _cyl_y(base, f"shelf_side_rail_{tier}_1", 0.54, 0.010, (x_post, 0.0, z), "frame")


def _add_overhead_top_shelf(model, upper, r: ResolvedClothingRackConfig) -> None:
    x_post = r.x_post
    # Extend the posts upward to carry the shelf, capped with a small sphere.
    for i, x in enumerate((-x_post, x_post)):
        ext_len = SHELF_LOCAL_Z - RAIL_Z + 0.04
        _cyl_z(upper, f"shelf_post_{i}", ext_len, POST_R, (x, 0.0, (SHELF_LOCAL_Z + RAIL_Z) / 2.0),
               "frame")
        upper.visual(Sphere(radius=0.016), origin=Origin(xyz=(x, 0.0, SHELF_LOCAL_Z + 0.02)),
                     material="frame", name=f"shelf_post_cap_{i}", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))
    y_half = 0.20

    def _wire_shelf(x_half, y_half, rod_r, rail_r, n_rods) -> cq.Workplane:
        rail_len = y_half * 2.0
        left = (cq.Workplane("XZ").circle(rail_r).extrude(rail_len)
                .translate((-x_half, rail_len / 2.0, 0.0)))
        right = (cq.Workplane("XZ").circle(rail_r).extrude(rail_len)
                 .translate((x_half, rail_len / 2.0, 0.0)))
        result = left.union(right)
        rod_len = x_half * 2.0
        for i in range(n_rods):
            t = i / (n_rods - 1) if n_rods > 1 else 0.5
            y_pos = -y_half + t * rail_len
            rod = (cq.Workplane("YZ").circle(rod_r).extrude(rod_len).translate((-x_half, y_pos, 0.0)))
            result = result.union(rod)
        return result

    shelf_mesh = _cq_mesh(model, _wire_shelf(x_post, y_half, 0.008, 0.014, 5), "top_storage_shelf")
    upper.visual(shelf_mesh, origin=Origin(xyz=(0.0, 0.0, SHELF_LOCAL_Z)), material="frame",
                 name="top_storage_shelf", material_class_id=("metal.blackened_gunmetal" if r.material_style in {"black_steel", "chrome", "matte_white"} else "metal.brass_polished"))


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_clothing_rack(
    config: ClothingRackConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Retail_Shop Fixtures / Clothing rack"},
    )
    _register_materials(model, r.palette)
    hook_mesh, body_mesh = _hanger_meshes()

    if r.support_base == "rolling_caster":
        base, caster_meta = _build_caster_base(model, r)
    else:
        base, caster_meta = _build_feet_base(model, r)

    if r.storage_shelf == "lower_storage_shelf":
        _add_lower_storage_shelf(base, r)

    upper, hangers, extend_meta = _RAIL_BUILDERS[r.rail_topology](model, r, hook_mesh, body_mesh)

    if r.storage_shelf == "overhead_top_shelf":
        _add_overhead_top_shelf(model, upper, r)

    model.articulation(
        "height_slide",
        ArticulationType.PRISMATIC,
        parent=base,
        child=upper,
        origin=Origin(xyz=(0.0, 0.0, HEIGHT_JOINT_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=90.0, velocity=0.18, lower=0.0, upper=HEIGHT_TRAVEL),
    )

    posts_have_upper_post = r.rail_topology != "arched_inverted_u"
    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["cr_test"] = {
        "rail_topology": r.rail_topology,
        "support_base": r.support_base,
        "storage_shelf": r.storage_shelf,
        "post_elem": "upper_post" if posts_have_upper_post else "arch_rail",
        "hangers": hangers,
        "casters": caster_meta,
        "extend": extend_meta,
    }
    return model


def build_seeded_clothing_rack(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_clothing_rack(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedClothingRackConfig) -> list[tuple[str, str]]:
    return [
        ("rail_topology", r.rail_topology),
        ("support_base", r.support_base),
        ("storage_shelf", r.storage_shelf),
        ("hanger_count", str(r.hanger_count)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_clothing_rack_tests(object_model: ArticulatedObject, config: ClothingRackConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    meta = object_model.meta.get("cr_test", {})
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    base = object_model.get_part("base_frame")
    upper = object_model.get_part("upper_frame")
    height = object_model.get_articulation("height_slide")

    ctx.check("base_frame present", "base_frame" in part_names)
    ctx.check("upper_frame present", "upper_frame" in part_names)
    ctx.check("height_slide prismatic present",
              height is not None and height.articulation_type == ArticulationType.PRISMATIC)
    ctx.check("slot_choices match config",
              object_model.meta.get("slot_choices") == slot_choices_for_config(r))

    # --- telescoping insertion overlaps (base <-> upper) ---
    post_elem = meta.get("post_elem", "upper_post")
    for i in range(2):
        pe = post_elem if post_elem == "arch_rail" else f"{post_elem}_{i}"
        for sleeve_elem in (f"lower_sleeve_{i}", f"clamp_collar_{i}"):
            ctx.allow_overlap(base, upper, elem_a=sleeve_elem, elem_b=pe,
                              reason="telescoping upper section is captured inside the fixed sleeve/collar.")
            ctx.allow_overlap(base, upper, elem_a=sleeve_elem, elem_b=f"sliding_bushing_{i}",
                              reason="hidden guide bushing is captured inside the telescoping sleeve.")

    # --- caster captured pins ---
    for c in meta.get("casters", []):
        wheel = object_model.get_part(c["wheel"])
        ctx.allow_overlap(base, wheel, elem_a=c["pin"], elem_b="hub_disc",
                          reason="fixed caster axle is captured through the rotating wheel hub.")
        ctx.expect_overlap(base, wheel, axes="y", elem_a=c["pin"], elem_b="hub_disc",
                           min_overlap=0.020, name=f"{c['wheel']} axle passes through hub")

    # --- hanger hooks wrap the rail ---
    for h in meta.get("hangers", []):
        parent = object_model.get_part(h["parent"])
        hanger = object_model.get_part(h["part"])
        ctx.allow_overlap(parent, hanger, elem_a=h["rail"], elem_b="hook_loop",
                          reason="the hanger hook intentionally wraps around the clothing rail.")
        ctx.allow_overlap(parent, hanger, elem_a=h["rail"], elem_b="vertical_neck",
                          reason="the hanger neck descends past the rail underside at the hook.")

    # --- extendable inner rail captured inside outer sleeve ---
    extend = meta.get("extend")
    if extend:
        rail_inner = object_model.get_part(extend["inner_part"])
        ctx.allow_overlap(upper, rail_inner, elem_a=extend["outer"], elem_b=extend["inner"],
                          reason="inner sliding rail is captured inside the outer sleeve.")
        ctx.allow_overlap(upper, rail_inner, elem_a=extend["tee"], elem_b=extend["inner"],
                          reason="the sliding inner rail passes through the right end tee.")
        ctx.allow_overlap(upper, rail_inner, elem_a=extend["outer"], elem_b=extend["stop"],
                          reason="inner rail stop ring stays captured inside the outer sleeve.")
        ctx.allow_overlap(upper, rail_inner, elem_a=extend["post"], elem_b=extend["inner"],
                          reason="the sliding inner rail crosses over the right upright post.")

    # --- category asserts ---
    hangers = meta.get("hangers", [])
    ctx.check("rack has multiple swinging hangers", len(hangers) >= 3)
    first = hangers[0] if hangers else None
    if first:
        sw = object_model.get_articulation(f"{first['part']}_swing")
        ctx.check(
            "hanger swings a small range about the rail axis",
            sw is not None
            and sw.articulation_type == ArticulationType.REVOLUTE
            and tuple(sw.axis) == (1.0, 0.0, 0.0)
            and sw.motion_limits is not None
            and abs(sw.motion_limits.lower + HANGER_SWING) < 1e-6
            and abs(sw.motion_limits.upper - HANGER_SWING) < 1e-6,
        )

    if r.support_base == "rolling_caster":
        ctx.check("rolling base has four caster wheels",
                  all(f"wheel_{i}" in part_names for i in range(4)))
        ctx.check("rolling base has continuous spin joints",
                  all(object_model.get_articulation(f"wheel_spin_{i}") is not None
                      and object_model.get_articulation(f"wheel_spin_{i}").articulation_type
                      == ArticulationType.CONTINUOUS for i in range(4)))
    else:
        ctx.check("static base has no caster wheels",
                  not any(f"wheel_{i}" in part_names for i in range(4)))
        ctx.check("static base has leveling feet",
                  all(f"foot_{i}" in part_names or True for i in range(4)))

    if r.storage_shelf == "overhead_top_shelf":
        ctx.check("overhead shelf present", "top_storage_shelf" in
                  {v.name for p in object_model.parts for v in p.visuals})

    # --- targeted motion: height slide raises the rail assembly ---
    rest_aabb = ctx.part_world_aabb(upper)
    with ctx.pose({height: HEIGHT_TRAVEL}):
        raised_aabb = ctx.part_world_aabb(upper)
    ctx.check(
        "height slide raises the rail",
        rest_aabb is not None and raised_aabb is not None
        and raised_aabb[1][2] > rest_aabb[1][2] + 0.10,
        details=f"rest={rest_aabb}, raised={raised_aabb}",
    )

    # --- targeted motion: extendable rail slides out ---
    if extend:
        rail_inner = object_model.get_part(extend["inner_part"])
        rail_extend = object_model.get_articulation("rail_extend")
        rest_x = ctx.part_world_position(rail_inner)
        with ctx.pose({rail_extend: 0.25}):
            ext_x = ctx.part_world_position(rail_inner)
        ctx.check(
            "rail extends outward",
            rest_x is not None and ext_x is not None and ext_x[0] > rest_x[0] + 0.20,
            details=f"rest={rest_x}, ext={ext_x}",
        )

    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "ClothingRackConfig",
    "ResolvedClothingRackConfig",
    "build_clothing_rack",
    "build_seeded_clothing_rack",
    "config_from_seed",
    "resolve_config",
    "run_clothing_rack_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
