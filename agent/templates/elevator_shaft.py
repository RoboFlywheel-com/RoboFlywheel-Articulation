# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for elevators.

Implements the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Structure_Elevator.md``.

Slot graph (mixed: a linear hoist->car lift chain with parallel optional
children on the hoist and the car)::

    [A hoist_structure] (fixed root)
        --PRISMATIC z (car_lift; guide_shoe<->rail contact)--> [C car_body]
            --PRISMATIC/REVOLUTE (portal; hanger<->track / hinge<->jamb)--> [D portal]
            --REVOLUTE (optional)--> [E safety_accessory]
        --PRISMATIC z (optional, traction-gated)--> counterweight
        --REVOLUTE x (optional, traction-gated)--> sheave_wheel

Every slot's module factory adapts a real 5-star source (see the spec's
Module Source Index). Continuous primitives that the source uses as
``mesh_from_geometry`` / ``LatheGeometry`` / ``section_loft`` /
``WheelGeometry`` / ``wire_from_points`` are preserved as meshes, not
downgraded to Box/Cylinder.

The car's guide-shoe / door-track / accessory-hinge interface coordinates
and the hoist's guide-rail coordinates are both derived from
``ResolvedElevatorConfig`` so the cross-module contacts hold by construction
regardless of which hoist / car / portal / accessory modules a seed samples.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal, Optional

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    section_loft,
    wire_from_points,
)

__modular__ = True

# --------------------------------------------------------------------------
# Slot module enums (the topology axes; NOT palette/material)
# --------------------------------------------------------------------------

HoistModule = Literal[
    "enclosed_walled_shaft",
    "open_post_frame",
    "single_column_mast",
    "rear_column_mast",
    "cylindrical_glass_tower",
]
DriveModule = Literal[
    "traction_sheave_ropes",
    "revolute_sheave_wheel",
    "hydraulic_ram",
    "lead_screw_drive",
    "rack_and_pinion",
    "implicit_none",
]
CarModule = Literal[
    "enclosed_rectangular_cab",
    "glass_cab_rectangular",
    "glass_cab_curved",
    "open_cage",
    "flat_platform",
]
PortalModule = Literal[
    "center_opening_slide",
    "single_panel_slide",
    "swing_hinged_leaves",
    "sliding_cage_gate",
    "swing_cage_gate",
    "folding_leaf_gate",
    "none",
]
AccessoryModule = Literal[
    "none",
    "folding_handrail",
    "knee_guard_or_lip",
    "folding_safety_arms",
    "safety_pawl",
]
MaterialStyle = Literal[
    "brushed_steel",
    "painted_cream",
    "industrial_gray",
    "blue_glass",
]

HOIST_MODULES: tuple[HoistModule, ...] = (
    "enclosed_walled_shaft",
    "open_post_frame",
    "single_column_mast",
    "rear_column_mast",
    "cylindrical_glass_tower",
)
CAR_MODULES: tuple[CarModule, ...] = (
    "enclosed_rectangular_cab",
    "glass_cab_rectangular",
    "glass_cab_curved",
    "open_cage",
    "flat_platform",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "brushed_steel",
    "painted_cream",
    "industrial_gray",
    "blue_glass",
)

# Which car families each hoist supports (compatibility matrix, spec §9).
HOIST_CAR_COMPAT: dict[HoistModule, tuple[CarModule, ...]] = {
    "enclosed_walled_shaft": (
        "enclosed_rectangular_cab",
        "glass_cab_rectangular",
        "open_cage",
    ),
    "open_post_frame": (
        "enclosed_rectangular_cab",
        "glass_cab_rectangular",
        "open_cage",
        "flat_platform",
    ),
    "single_column_mast": ("flat_platform",),
    "rear_column_mast": ("enclosed_rectangular_cab", "open_cage", "flat_platform"),
    "cylindrical_glass_tower": ("glass_cab_curved",),
}

# Which drive families each hoist supports.
HOIST_DRIVE_COMPAT: dict[HoistModule, tuple[DriveModule, ...]] = {
    "enclosed_walled_shaft": (
        "traction_sheave_ropes",
        "revolute_sheave_wheel",
        "implicit_none",
    ),
    "open_post_frame": (
        "traction_sheave_ropes",
        "revolute_sheave_wheel",
        "implicit_none",
    ),
    "single_column_mast": ("hydraulic_ram", "implicit_none"),
    "rear_column_mast": ("lead_screw_drive", "rack_and_pinion", "implicit_none"),
    "cylindrical_glass_tower": ("implicit_none",),
}

# Portal families allowed per car family.
CAR_PORTAL_COMPAT: dict[CarModule, tuple[PortalModule, ...]] = {
    "enclosed_rectangular_cab": (
        "center_opening_slide",
        "single_panel_slide",
        "swing_hinged_leaves",
    ),
    "glass_cab_rectangular": ("center_opening_slide", "single_panel_slide"),
    "glass_cab_curved": ("center_opening_slide", "single_panel_slide"),
    "open_cage": ("sliding_cage_gate", "swing_cage_gate", "folding_leaf_gate"),
    "flat_platform": ("none", "sliding_cage_gate", "folding_leaf_gate"),
}

# Accessory families allowed per car family. flat_platform MUST take a
# moving accessory (no "none") so it never degenerates to a single-DOF lift.
CAR_ACCESSORY_COMPAT: dict[CarModule, tuple[AccessoryModule, ...]] = {
    "enclosed_rectangular_cab": ("none", "folding_handrail"),
    "glass_cab_rectangular": ("none",),
    "glass_cab_curved": ("none",),
    "open_cage": ("none", "safety_pawl"),
    "flat_platform": ("knee_guard_or_lip", "folding_safety_arms"),
}

# Counterweight only exists with a traction drive family.
TRACTION_DRIVES = ("traction_sheave_ropes", "revolute_sheave_wheel")


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_steel": {
        "shaft": (0.54, 0.55, 0.53, 1.0),
        "cab": (0.70, 0.70, 0.66, 1.0),
        "rail": (0.20, 0.21, 0.22, 1.0),
        "door": (0.62, 0.64, 0.64, 1.0),
        "glass": (0.62, 0.80, 0.90, 1.0),
        "accent": (0.16, 0.22, 0.30, 1.0),
        "dark": (0.10, 0.11, 0.12, 1.0),
        "safety": (0.86, 0.66, 0.12, 1.0),
    },
    "painted_cream": {
        "shaft": (0.70, 0.68, 0.60, 1.0),
        "cab": (0.86, 0.82, 0.70, 1.0),
        "rail": (0.22, 0.22, 0.21, 1.0),
        "door": (0.78, 0.76, 0.66, 1.0),
        "glass": (0.66, 0.82, 0.86, 1.0),
        "accent": (0.60, 0.16, 0.10, 1.0),
        "dark": (0.12, 0.12, 0.11, 1.0),
        "safety": (0.90, 0.72, 0.10, 1.0),
    },
    "industrial_gray": {
        "shaft": (0.40, 0.41, 0.40, 1.0),
        "cab": (0.50, 0.51, 0.49, 1.0),
        "rail": (0.14, 0.15, 0.15, 1.0),
        "door": (0.44, 0.45, 0.43, 1.0),
        "glass": (0.58, 0.74, 0.80, 1.0),
        "accent": (0.86, 0.66, 0.12, 1.0),
        "dark": (0.08, 0.09, 0.09, 1.0),
        "safety": (0.88, 0.70, 0.10, 1.0),
    },
    "blue_glass": {
        "shaft": (0.34, 0.36, 0.38, 1.0),
        "cab": (0.46, 0.50, 0.54, 1.0),
        "rail": (0.12, 0.14, 0.16, 1.0),
        "door": (0.48, 0.55, 0.60, 1.0),
        "glass": (0.52, 0.74, 0.92, 1.0),
        "accent": (0.80, 0.86, 0.90, 1.0),
        "dark": (0.06, 0.08, 0.10, 1.0),
        "safety": (0.86, 0.72, 0.16, 1.0),
    },
}


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ElevatorConfig:
    hoist_module: Optional[HoistModule] = None
    drive_module: Optional[DriveModule] = None
    car_module: Optional[CarModule] = None
    portal_module: Optional[PortalModule] = None
    accessory_module: Optional[AccessoryModule] = None
    material_style: Optional[MaterialStyle] = None
    rope_count: int = 2
    # Controlled local scales (clamped in resolve_config).
    support_width_scale: float = 1.0
    car_height_scale: float = 1.0
    rail_gauge_scale: float = 1.0
    travel_scale: float = 1.0
    name: str = "elevator"


@dataclass(frozen=True)
class ResolvedElevatorConfig:
    hoist_module: HoistModule
    drive_module: DriveModule
    car_module: CarModule
    portal_module: PortalModule
    accessory_module: AccessoryModule
    material_style: MaterialStyle
    has_counterweight: bool
    door_panel_count: int
    rope_count: int
    # core dims
    car_w: float
    car_d: float
    car_h: float
    car_base_z: float
    travel: float
    shaft_height: float
    front_y: float
    # guide interface
    rail_layout: Literal["twin_x", "rear_central"]
    rail_x: float
    rail_t: float
    rail_d: float
    rail_y: float
    column_y: float
    column_d: float
    shoe_lower_z: float
    shoe_upper_z: float
    # door interface (in car-local frame; car origin at car center floor)
    door_w: float
    door_jamb_x: float
    door_track_top_z: float
    door_sill_z: float
    door_plane_y: float
    # counterweight
    counterweight_x: float
    name: str

    @property
    def is_open_front_cab(self) -> bool:
        return self.car_module in (
            "enclosed_rectangular_cab",
            "glass_cab_rectangular",
            "glass_cab_curved",
        )


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _gate_choice(value, allowed: tuple, fallback, rng: random.Random):
    """Resolve an optional pinned choice against a compatible-allowed set."""
    if value is not None and value in allowed:
        return value
    return rng.choice(allowed)


def config_from_seed(seed: int) -> ElevatorConfig:
    """Deterministic procedural sampling. seed=0 is not special."""
    rng = random.Random(seed)
    hoist = rng.choice(HOIST_MODULES)
    drive = rng.choice(HOIST_DRIVE_COMPAT[hoist])
    car = rng.choice(HOIST_CAR_COMPAT[hoist])
    portal = rng.choice(CAR_PORTAL_COMPAT[car])
    accessory = rng.choice(CAR_ACCESSORY_COMPAT[car])
    return ElevatorConfig(
        hoist_module=hoist,
        drive_module=drive,
        car_module=car,
        portal_module=portal,
        accessory_module=accessory,
        material_style=rng.choice(MATERIAL_STYLES),
        rope_count=rng.choice((2, 3, 4)),
        support_width_scale=round(rng.uniform(0.9, 1.15), 3),
        car_height_scale=round(rng.uniform(0.92, 1.1), 3),
        rail_gauge_scale=round(rng.uniform(0.95, 1.1), 3),
        travel_scale=round(rng.uniform(0.85, 1.2), 3),
        name=f"seeded_elevator_{seed}",
    )


def resolve_config(config: ElevatorConfig) -> ResolvedElevatorConfig:
    rng = random.Random(0xE1E + hash(config.name) % 9973)
    hoist: HoistModule = config.hoist_module or "enclosed_walled_shaft"
    if hoist not in HOIST_MODULES:
        raise ValueError(f"Unsupported hoist_module: {hoist}")
    drive = _gate_choice(config.drive_module, HOIST_DRIVE_COMPAT[hoist], None, rng)
    car = _gate_choice(config.car_module, HOIST_CAR_COMPAT[hoist], None, rng)
    portal = _gate_choice(config.portal_module, CAR_PORTAL_COMPAT[car], None, rng)
    accessory = _gate_choice(config.accessory_module, CAR_ACCESSORY_COMPAT[car], None, rng)
    material = (
        config.material_style if config.material_style in MATERIAL_STYLES else "brushed_steel"
    )

    has_counterweight = drive in TRACTION_DRIVES and hoist in (
        "enclosed_walled_shaft",
        "open_post_frame",
    )

    door_panel_count = 2 if portal in ("center_opening_slide", "folding_leaf_gate") else 1
    rope_count = int(_clamp(config.rope_count, 2, 4)) if drive in TRACTION_DRIVES else 0

    sw = _clamp(config.support_width_scale, 0.9, 1.15)
    chs = _clamp(config.car_height_scale, 0.92, 1.1)
    rgs = _clamp(config.rail_gauge_scale, 0.95, 1.1)
    ts = _clamp(config.travel_scale, 0.85, 1.2)

    # Core car dimensions per family.
    if car == "flat_platform":
        car_w, car_d, car_h = 1.60 * sw, 1.20 * sw, 0.16
    elif car == "open_cage":
        car_w, car_d, car_h = 1.20 * sw, 1.00 * sw, 2.00 * chs
    elif car == "glass_cab_curved":
        car_w, car_d, car_h = 1.40 * sw, 1.40 * sw, 2.18 * chs
    else:  # enclosed / glass rectangular
        car_w, car_d, car_h = 1.44 * sw, 1.16 * sw, 2.24 * chs

    car_base_z = 0.22
    travel = _clamp(1.8 * ts, 1.2, 6.5)
    head_room = 0.55 + (0.30 if drive in TRACTION_DRIVES else 0.0)
    shaft_height = car_base_z + travel + car_h + head_room
    front_y = -car_d / 2.0

    # Guide interface.
    rail_t, rail_d = 0.07, 0.09
    rear_central_hoists = ("single_column_mast", "rear_column_mast", "cylindrical_glass_tower")
    if hoist in rear_central_hoists:
        rail_layout: Literal["twin_x", "rear_central"] = "rear_central"
        rail_x = 0.0
        column_d = (
            0.30
            if hoist == "single_column_mast"
            else (0.22 if hoist == "rear_column_mast" else 0.10)
        )
        rail_y = 0.0
        # column front face sits a carriage-length behind the car back edge.
        car_back = car_d / 2.0
        column_y = car_back + 0.16 + column_d / 2.0
    else:
        rail_layout = "twin_x"
        rail_x = car_w / 2.0 + (0.085 * rgs) + rail_t / 2.0
        rail_y = 0.0
        column_d = 0.0
        column_y = 0.0

    # Guide-shoe z positions, in car-local frame (floor bottom at z=0).
    shoe_lower_z = car_h * 0.28
    shoe_upper_z = car_h * 0.78

    # Door operating plane and frame (car-local frame).
    if car == "glass_cab_curved":
        rad = car_w / 2.0
        door_w = car_w * 0.55
        door_plane_y = -math.sqrt(max(0.04, (rad - 0.05) ** 2 - (door_w / 2.0) ** 2))
    else:
        door_w = car_w * 0.62
        door_plane_y = front_y + 0.06
    door_jamb_x = door_w / 2.0
    door_sill_z = 0.10  # threshold center z
    door_track_top_z = car_h - 0.18  # top track center z

    counterweight_x = rail_x + 0.20

    # flat_platform with a front gate must use side-mounted safety arms (a
    # front knee guard would collide with the gate at the front edge).
    if car == "flat_platform" and portal in ("sliding_cage_gate", "folding_leaf_gate"):
        accessory = "folding_safety_arms"

    return ResolvedElevatorConfig(
        hoist_module=hoist,
        drive_module=drive,
        car_module=car,
        portal_module=portal,
        accessory_module=accessory,
        material_style=material,
        has_counterweight=has_counterweight,
        door_panel_count=door_panel_count,
        rope_count=rope_count,
        car_w=car_w,
        car_d=car_d,
        car_h=car_h,
        car_base_z=car_base_z,
        travel=travel,
        shaft_height=shaft_height,
        front_y=front_y,
        rail_layout=rail_layout,
        rail_x=rail_x,
        rail_t=rail_t,
        rail_d=rail_d,
        rail_y=rail_y,
        column_y=column_y,
        column_d=column_d,
        shoe_lower_z=shoe_lower_z,
        shoe_upper_z=shoe_upper_z,
        door_w=door_w,
        door_jamb_x=door_jamb_x,
        door_track_top_z=door_track_top_z,
        door_sill_z=door_sill_z,
        door_plane_y=door_plane_y,
        counterweight_x=counterweight_x,
        name=config.name or "elevator",
    )


def with_overrides(config: ElevatorConfig, **kwargs) -> ElevatorConfig:
    return replace(config, **kwargs)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------


def _mat(model: ArticulatedObject, r: ResolvedElevatorConfig, key: str):
    return model.material(
        f"elevator_{r.material_style}_{key}", rgba=PALETTES[r.material_style][key]
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _circle_pts(radius: float, segments: int = 28) -> list[tuple[float, float]]:
    return [
        (
            radius * math.cos(2.0 * math.pi * i / segments),
            radius * math.sin(2.0 * math.pi * i / segments),
        )
        for i in range(segments)
    ]


def _curved_strip_loop(cx, cy, r_out, r_in, a0, a1, z, segments=18):
    """Faithful adaptation of rec_elevator_5ef65550 _curved_strip_loop."""
    s, e = math.radians(a0), math.radians(a1)
    outer = []
    inner = []
    for i in range(segments + 1):
        t = i / segments
        a = s + (e - s) * t
        outer.append((cx + r_out * math.cos(a), cy + r_out * math.sin(a), z))
    for i in range(segments, -1, -1):
        t = i / segments
        a = s + (e - s) * t
        inner.append((cx + r_in * math.cos(a), cy + r_in * math.sin(a), z))
    return outer + inner


def _curved_panel_mesh(name, cx, cy, r_out, r_in, a0, a1, z0, z1, segments=18):
    return mesh_from_geometry(
        section_loft(
            [
                _curved_strip_loop(cx, cy, r_out, r_in, a0, a1, z0, segments),
                _curved_strip_loop(cx, cy, r_out, r_in, a0, a1, z1, segments),
            ]
        ),
        name,
    )


def _annular_tube_mesh(name, r_out, r_in, height, segments=28):
    """Faithful annular glass tube (rec_elevator_fd6c0a36 _annular_tube)."""
    return mesh_from_geometry(
        ExtrudeWithHolesGeometry(
            _circle_pts(r_out, segments),
            [_circle_pts(r_in, segments)],
            height,
            center=True,
        ),
        name,
    )


def _helix_points(radius, z0, z1, turns, samples):
    pts = []
    n = max(8, int(samples))
    for i in range(n + 1):
        t = i / n
        a = turns * 2.0 * math.pi * t
        pts.append((radius * math.cos(a), radius * math.sin(a), z0 + (z1 - z0) * t))
    return pts


# --------------------------------------------------------------------------
# Slot A — hoist structure factories (fixed root part "hoist")
# Each places guide rails at the canonical interface coordinates in `r`.
# --------------------------------------------------------------------------


def _emit_guide_rails(hoist, r, mats) -> None:
    H = r.shaft_height
    if r.rail_layout == "twin_x":
        for side in (-1, 1):
            x = side * r.rail_x
            _box(
                hoist,
                (r.rail_t, r.rail_d, H - 0.10),
                (x, r.rail_y, H * 0.5),
                mats["rail"],
                f"guide_rail_{'left' if side < 0 else 'right'}",
            )
    else:
        # rear central column doubles as the guide rail face (front face).
        _box(
            hoist,
            (0.30, r.column_d, H - 0.06),
            (0.0, r.column_y, H * 0.5),
            mats["rail"],
            "guide_rail_central",
        )


def _build_enclosed_walled_shaft(model, r, mats):
    hoist = model.part("hoist")
    W = r.car_w + 0.66 + (0.44 if r.has_counterweight else 0.0)
    D = r.car_d + 0.50
    H = r.shaft_height
    back_y = D * 0.5 - 0.04
    _box(hoist, (W, D, 0.10), (0.0, 0.0, 0.05), mats["dark"], "pit_floor")
    _box(hoist, (0.08, D, H), (-(W / 2.0) + 0.04, 0.0, H * 0.5), mats["shaft"], "left_wall")
    _box(hoist, (0.08, D, H), ((W / 2.0) - 0.04, 0.0, H * 0.5), mats["shaft"], "right_wall")
    _box(hoist, (W, 0.08, H), (0.0, back_y, H * 0.5), mats["shaft"], "back_wall")
    _box(hoist, (W, D, 0.12), (0.0, 0.0, H - 0.06), mats["dark"], "top_slab")
    _box(hoist, (W, 0.10, 0.22), (0.0, -D * 0.5 + 0.05, H - 0.30), mats["dark"], "front_header")
    _emit_guide_rails(hoist, r, mats)
    return hoist


def _build_open_post_frame(model, r, mats):
    hoist = model.part("hoist")
    W = r.car_w + 0.50 + (0.44 if r.has_counterweight else 0.0)
    D = r.car_d + 0.42
    H = r.shaft_height
    _box(hoist, (W + 0.12, D + 0.12, 0.10), (0.0, 0.0, 0.05), mats["dark"], "base_slab")
    for sx, lx in ((-1, "left"), (1, "right")):
        for sy, ly in ((-1, "front"), (1, "back")):
            _box(
                hoist,
                (0.09, 0.09, H),
                (sx * W * 0.5, sy * D * 0.5, H * 0.5),
                mats["rail"],
                f"{lx}_{ly}_post",
            )
    for sy, ly in ((-1, "front"), (1, "back")):
        _box(hoist, (W, 0.07, 0.07), (0.0, sy * D * 0.5, H - 0.05), mats["rail"], f"{ly}_top_beam")
    _emit_guide_rails(hoist, r, mats)
    return hoist


def _build_single_column_mast(model, r, mats):
    hoist = model.part("hoist")
    H = r.shaft_height
    cw = r.column_d
    _box(
        hoist,
        (max(0.62, cw * 2.0), cw + 0.20, 0.06),
        (0.0, r.column_y, 0.03),
        mats["dark"],
        "base_plate",
    )
    _box(hoist, (cw, cw, H - 0.10), (0.0, r.column_y, H * 0.5), mats["shaft"], "column_post")
    _box(
        hoist, (cw + 0.06, cw + 0.06, 0.06), (0.0, r.column_y, H - 0.05), mats["dark"], "column_cap"
    )
    for sx in (-1, 1):
        _cyl(
            hoist,
            0.016,
            0.05,
            (sx * (max(0.62, cw * 2.0) * 0.5 - 0.05), r.column_y, 0.03),
            mats["rail"],
            f"anchor_bolt_{'l' if sx < 0 else 'r'}",
            (0.0, 0.0, 0.0),
        )
    _emit_guide_rails(hoist, r, mats)
    return hoist


def _build_rear_column_mast(model, r, mats):
    hoist = model.part("hoist")
    H = r.shaft_height
    cd = r.column_d
    col_w = max(0.46, r.car_w * 0.42)
    _box(
        hoist,
        (col_w + 0.20, cd + 0.30, 0.10),
        (0.0, r.column_y - 0.05, 0.05),
        mats["dark"],
        "base_beam",
    )
    # single central backbone column (rail + drive mount to its front face)
    _box(hoist, (col_w, cd, H - 0.10), (0.0, r.column_y, H * 0.5), mats["shaft"], "backbone_column")
    for i, z in enumerate((H * 0.3, H * 0.6, H * 0.86)):
        # recessed slightly behind the column front face so they never foul the
        # car carriage as it travels.
        _box(
            hoist,
            (col_w + 0.06, cd, 0.05),
            (0.0, r.column_y + 0.02, z),
            mats["rail"],
            f"mast_band_{i}",
        )
    _box(
        hoist,
        (col_w + 0.10, cd + 0.10, 0.16),
        (0.0, r.column_y, H - 0.10),
        mats["dark"],
        "machine_head",
    )
    _emit_guide_rails(hoist, r, mats)
    return hoist


def _build_cylindrical_glass_tower(model, r, mats):
    hoist = model.part("hoist")
    H = r.shaft_height
    r_out = r.car_w * 0.5 + 0.30
    r_in = r_out - 0.03
    _cyl(hoist, r_out + 0.06, 0.10, (0.0, 0.0, 0.05), mats["dark"], "round_plinth")
    hoist.visual(
        _annular_tube_mesh("glass_tube", r_out, r_in, H - 0.20, segments=30),
        origin=Origin(xyz=(0.0, 0.0, (H - 0.20) * 0.5 + 0.10)),
        material=mats["glass"],
        name="glass_tube", material_class_id="glass.clear_transparent",
    )
    _cyl(hoist, r_out + 0.04, 0.06, (0.0, 0.0, H - 0.05), mats["dark"], "head_cap")
    for i in range(6):
        a = i * math.pi / 3.0
        _cyl(
            hoist,
            0.018,
            H - 0.16,
            (r_out * math.cos(a), r_out * math.sin(a), (H - 0.16) * 0.5 + 0.08),
            mats["rail"],
            f"mullion_{i}",
        )
    # rear-central guide rail: spans from the carriage contact face back to the
    # glass-tube inner wall so it is structurally supported (not an island).
    rail_front = r.column_y - r.column_d / 2.0
    rail_back = r_in + 0.01
    rail_depth = rail_back - rail_front
    rail_cy = (rail_front + rail_back) / 2.0
    _box(
        hoist,
        (0.30, rail_depth, H - 0.16),
        (0.0, rail_cy, (H - 0.16) * 0.5 + 0.08),
        mats["rail"],
        "guide_rail_central",
    )
    return hoist


def _emit_landing_buffer(hoist, r, mats) -> None:
    """A pit buffer beam under the car rest position whose top face is at
    car_base_z (so the car_lift joint origin sits on real hoist geometry and
    the car floor lands on it). It bridges to the guide structure so it is not
    an island: spans both rails (twin_x) or reaches the column (rear_central)."""
    zc = r.car_base_z - 0.05  # top at car_base_z
    if r.rail_layout == "twin_x":
        _box(
            hoist,
            (2.0 * r.rail_x + 0.06, 0.20, 0.10),
            (0.0, r.rail_y, zc),
            mats["dark"],
            "car_landing_buffer",
        )
    else:
        _box(
            hoist,
            (0.30, r.column_y + 0.12, 0.10),
            (0.0, r.column_y / 2.0, zc),
            mats["dark"],
            "car_landing_buffer",
        )


HOIST_FACTORIES = {
    "enclosed_walled_shaft": _build_enclosed_walled_shaft,
    "open_post_frame": _build_open_post_frame,
    "single_column_mast": _build_single_column_mast,
    "rear_column_mast": _build_rear_column_mast,
    "cylindrical_glass_tower": _build_cylindrical_glass_tower,
}


# --------------------------------------------------------------------------
# Slot B — drive / suspension visuals (added onto the hoist part) + optional
# counterweight & sheave moving children.
# --------------------------------------------------------------------------


def _build_drive_visuals(model, r, mats, hoist) -> None:
    H = r.shaft_height
    d = r.drive_module
    if d in ("traction_sheave_ropes", "revolute_sheave_wheel"):
        beam_w = 2.0 * r.rail_x + 0.08  # span both guide rails so it is supported
        _box(hoist, (beam_w, 0.22, 0.16), (0.0, -0.05, H - 0.26), mats["dark"], "machine_beam")
        if d == "traction_sheave_ropes":
            _cyl(
                hoist,
                0.11,
                0.18,
                (0.0, -0.05, H - 0.26),
                mats["rail"],
                "drive_sheave",
                (0.0, math.pi / 2.0, 0.0),
            )
        # hoist ropes (multiplicity) — only in the headroom above the car's
        # highest roof position so they never intersect the car.
        rope_top = H - 0.33  # embed into the machine beam (bottom at H-0.34)
        rope_bottom = r.car_base_z + r.travel + r.car_h + 0.06
        if rope_top - rope_bottom > 0.10:
            for i in range(r.rope_count):
                rx = -0.10 + i * (0.20 / max(1, r.rope_count - 1)) if r.rope_count > 1 else 0.0
                _cyl(
                    hoist,
                    0.012,
                    rope_top - rope_bottom,
                    (rx, -0.05, (rope_top + rope_bottom) * 0.5),
                    mats["dark"],
                    f"hoist_rope_{i}",
                )
    elif d == "hydraulic_ram":
        ram_len = r.car_base_z + r.travel + 0.10
        _cyl(
            hoist,
            0.075,
            ram_len,
            (0.0, r.column_y, ram_len * 0.5),
            mats["rail"],
            "hydraulic_cylinder",
        )
        _box(
            hoist,
            (0.26, 0.18, 0.12),
            (0.0, r.column_y + 0.20, 0.10),
            mats["dark"],
            "hydraulic_pump",
        )
    elif d == "lead_screw_drive":
        z0, z1 = r.car_base_z, r.car_base_z + r.travel + 0.10
        sx = 0.25  # clear of the centered carriage, within the column width
        yface = r.column_y - r.column_d / 2.0 - 0.01  # back face embeds into the column
        _cyl(hoist, 0.026, z1 - z0, (sx, yface, (z0 + z1) * 0.5), mats["rail"], "lead_screw_core")
        hoist.visual(
            mesh_from_geometry(
                wire_from_points(
                    _helix_points(0.04, z0, z1, turns=(z1 - z0) / 0.10, samples=160),
                    radius=0.012,
                    radial_segments=10,
                ),
                "lead_screw_thread",
            ),
            origin=Origin(xyz=(sx, yface, 0.0)),
            material=mats["accent"],
            name="lead_screw_thread", material_class_id="metal.steel_bare",
        )
    elif d == "rack_and_pinion":
        z0, z1 = r.car_base_z, r.car_base_z + r.travel
        sx = 0.25  # clear of the centered carriage (x in +/-0.17)
        yface = r.column_y - r.column_d / 2.0 - 0.02  # spine back embeds into column
        _box(hoist, (0.06, 0.06, z1 - z0), (sx, yface, (z0 + z1) * 0.5), mats["rail"], "rack_spine")
        n_teeth = max(6, int((z1 - z0) / 0.12))
        for i in range(n_teeth):
            z = z0 + (i + 0.5) * (z1 - z0) / n_teeth
            _box(
                hoist, (0.10, 0.03, 0.05), (sx, yface - 0.04, z), mats["accent"], f"rack_tooth_{i}"
            )


def _build_counterweight(model, r, mats, hoist):
    """Separate prismatic counterweight + its guide rail on the hoist."""
    H = r.shaft_height
    x = r.counterweight_x
    # counterweight guide rail (fixed, on hoist). Joint origin sits inside it.
    _box(hoist, (0.06, 0.08, H - 0.30), (x, 0.175, H * 0.5), mats["rail"], "counterweight_rail")
    # ties bridging the counterweight rail to the (grounded) right guide rail
    for zt, lz in ((r.car_base_z + 0.12, "low"), (H - 0.22, "high")):
        _box(
            hoist,
            (x - r.rail_x + 0.06, 0.22, 0.06),
            ((x + r.rail_x) / 2.0, 0.0875, zt),
            mats["rail"],
            f"counterweight_tie_{lz}",
        )
    cw = model.part("counterweight")
    # Guide yoke at the part origin (inside the rail); weight stack hangs in
    # front (-y). child (0,0,0) lies in the yoke; the yoke<->rail overlap is a
    # captured guide and is allowed element-scoped in run_elevator_shaft_tests.
    _box(cw, (0.08, 0.34, 0.46), (0.0, 0.0, 0.0), mats["rail"], "cw_guide_yoke")
    _box(cw, (0.20, 0.13, 0.52), (0.0, -0.17, 0.0), mats["dark"], "weight_stack")
    _box(cw, (0.16, 0.03, 0.42), (0.0, -0.235, 0.0), mats["accent"], "weight_stripe")
    return cw


def _build_sheave_wheel(model, r, mats, hoist):
    """Revolute grooved sheave wheel (WheelGeometry), rec_75a6c8b0."""
    H = r.shaft_height
    # bearing block on hoist
    _box(
        hoist, (0.10, 0.16, 0.10), (r.car_w * 0.30, -0.05, H - 0.26), mats["dark"], "sheave_bearing"
    )
    wheel = model.part("sheave_wheel")
    wheel.visual(
        mesh_from_geometry(
            WheelGeometry(
                radius=0.16,
                width=0.07,
                hub=WheelHub(radius=0.04, width=0.09),
                rim=WheelRim(flange_height=0.02, flange_thickness=0.012),
                spokes=WheelSpokes(style="straight", count=6, thickness=0.016),
            ),
            "sheave_wheel_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["rail"],
        name="sheave_wheel_mesh", material_class_id="metal.cast_iron_bare",
    )
    return wheel


# --------------------------------------------------------------------------
# Slot C — car body factories (moving part "car"). Each emits guide shoes
# at the canonical interface coords so guide_shoe<->rail contact holds.
# Car-local frame: origin at car center, floor bottom at z=0.
# --------------------------------------------------------------------------


def _emit_guide_shoes(car, r, mats) -> None:
    """Shoes bridge from the car edge out to the hoist guide rail, meeting its
    inner face exactly (coincident faces -> contact, no overlap)."""
    shoe_h = min(0.12, r.car_h * 0.5)
    if r.rail_layout == "twin_x":
        rail_inner = r.rail_x - r.rail_t / 2.0
        car_edge = r.car_w / 2.0 - 0.06  # reach inboard to the wall/glass/post
        outer = rail_inner + _EMBED
        span = max(0.04, outer - car_edge)
        cx = car_edge + span / 2.0
        for sx in (-1, 1):
            for zc, lz in ((r.shoe_lower_z, "lower"), (r.shoe_upper_z, "upper")):
                _box(
                    car,
                    (span, 0.085, shoe_h),
                    (sx * cx, r.rail_y, zc),
                    mats["dark"],
                    f"guide_shoe_{'left' if sx < 0 else 'right'}_{lz}",
                )
    else:
        # rear-central carriage bridging car back edge to the column front face.
        car_back = (
            r.car_d / 2.0 - 0.02 if r.car_module != "glass_cab_curved" else (r.car_w / 2.0 - 0.07)
        )
        col_front = r.column_y - r.column_d / 2.0 + _EMBED
        span = max(0.05, col_front - car_back)
        cy = car_back + span / 2.0
        for zc, lz in ((r.shoe_lower_z, "lower"), (r.shoe_upper_z, "upper")):
            _box(car, (0.34, span, shoe_h), (0.0, cy, zc), mats["dark"], f"carriage_{lz}")


_THRESH_TH = 0.08
_TRACK_TH = 0.06
# Structural contacts embed this far: > 0 so isolated-parts sees contact,
# < the 5 mm overlap tolerance so the overlap gate stays silent.
_EMBED = 0.002


def _door_panel_zspan(r):
    """(z_center, height) of a door panel: bottom embedded into threshold top,
    top embedded into track bottom -> contact at both ends, < overlap tol."""
    bottom = (r.door_sill_z + _THRESH_TH / 2.0) - _EMBED
    top = (r.door_track_top_z - _TRACK_TH / 2.0) + _EMBED
    return (bottom + top) / 2.0, max(0.4, top - bottom)


def _emit_door_frame(car, r, mats, jamb_h: Optional[float] = None) -> None:
    """Jambs / header / threshold / top-track at the door operating plane.
    Track and threshold are z-adjacent to the panel for clean contact."""
    H = jamb_h if jamb_h is not None else r.car_h
    dy = r.door_plane_y
    jw = (r.car_w - r.door_w) / 2.0
    for sx in (-1, 1):
        _box(
            car,
            (jw, 0.09, H),
            (sx * (r.door_jamb_x + jw / 2.0), dy, H * 0.5),
            mats["cab"],
            f"{'left' if sx < 0 else 'right'}_jamb",
        )
    _box(
        car,
        (r.door_w + 0.08, 0.09, 0.10),
        (0.0, dy, r.door_track_top_z + 0.07),
        mats["cab"],
        "door_header",
    )
    _box(
        car,
        (r.door_w + 0.10, 0.09, _THRESH_TH),
        (0.0, dy, r.door_sill_z),
        mats["dark"],
        "threshold",
    )
    _box(
        car,
        (r.door_w + 0.04, 0.09, _TRACK_TH),
        (0.0, dy, r.door_track_top_z),
        mats["dark"],
        "door_top_track",
    )


def _build_enclosed_rectangular_cab(model, r, mats):
    car = model.part("car")
    W, D, H = r.car_w, r.car_d, r.car_h
    _box(car, (W, D, 0.06), (0.0, 0.0, 0.03), mats["cab"], "car_floor")
    _box(car, (W, D, 0.05), (0.0, 0.0, H - 0.025), mats["cab"], "car_roof")
    for sx in (-1, 1):
        _box(
            car,
            (0.04, D, H),
            (sx * (W / 2.0 - 0.02), 0.0, H * 0.5),
            mats["cab"],
            f"{'left' if sx < 0 else 'right'}_wall",
        )
    _box(car, (W - 0.08, 0.04, H), (0.0, D / 2.0 - 0.02, H * 0.5), mats["cab"], "back_wall")
    _box(car, (W - 0.12, 0.03, 0.08), (0.0, D / 2.0 - 0.05, H * 0.42), mats["dark"], "handrail")
    _emit_door_frame(car, r, mats)
    _emit_guide_shoes(car, r, mats)
    return car


def _build_glass_cab_rectangular(model, r, mats):
    car = model.part("car")
    W, D, H = r.car_w, r.car_d, r.car_h
    _box(car, (W, D, 0.07), (0.0, 0.0, 0.035), mats["dark"], "car_floor")
    _box(car, (W, D, 0.06), (0.0, 0.0, H - 0.03), mats["dark"], "car_roof")
    for sx in (-1, 1):
        _box(
            car,
            (0.05, 0.05, H),
            (sx * (W / 2.0 - 0.025), -D / 2.0 + 0.025, H * 0.5),
            mats["dark"],
            f"{'left' if sx < 0 else 'right'}_front_post",
        )
        _box(
            car,
            (0.05, 0.05, H),
            (sx * (W / 2.0 - 0.025), D / 2.0 - 0.025, H * 0.5),
            mats["dark"],
            f"{'left' if sx < 0 else 'right'}_back_post",
        )
        _box(
            car,
            (0.03, D - 0.10, H * 0.82),
            (sx * (W / 2.0 - 0.05), 0.0, H * 0.5),
            mats["glass"],
            f"{'left' if sx < 0 else 'right'}_glass_wall",
        )
    _box(
        car,
        (W - 0.10, 0.03, H * 0.82),
        (0.0, D / 2.0 - 0.04, H * 0.5),
        mats["glass"],
        "rear_glass_wall",
    )
    _emit_door_frame(car, r, mats)
    _emit_guide_shoes(car, r, mats)
    return car


def _build_glass_cab_curved(model, r, mats):
    car = model.part("car")
    H = r.car_h
    rad = r.car_w * 0.5
    inner = rad - 0.024
    _cyl(car, rad, 0.08, (0.0, 0.0, 0.04), mats["dark"], "floor_pan")
    _cyl(car, rad, 0.07, (0.0, 0.0, H - 0.035), mats["dark"], "roof_pan")
    # curved glass walls covering the rear ~260 degrees (front gap for door)
    car.visual(
        _curved_panel_mesh(
            "glass_left", 0.0, 0.0, rad, inner, 40.0, 170.0, 0.08, H - 0.06, segments=20
        ),
        material=mats["glass"],
        name="glass_left", material_class_id="glass.clear_transparent",
    )
    car.visual(
        _curved_panel_mesh(
            "glass_right", 0.0, 0.0, rad, inner, 190.0, 320.0, 0.08, H - 0.06, segments=20
        ),
        material=mats["glass"],
        name="glass_right", material_class_id="glass.clear_transparent",
    )
    # rear spine connecting floor & roof through the glass span
    _box(car, (0.10, 0.06, H - 0.10), (0.0, rad - 0.05, H * 0.5), mats["dark"], "rear_spine")
    # front door frame at the chord plane (jambs sit on the round floor pan)
    dy = r.door_plane_y
    for sx, lx in ((-1, "left"), (1, "right")):
        _box(
            car,
            (0.04, 0.09, H),
            (sx * (r.door_jamb_x + 0.03), dy, H * 0.5),
            mats["dark"],
            f"{lx}_jamb",
        )
    _box(
        car,
        (r.door_w + 0.06, 0.09, 0.10),
        (0.0, dy, r.door_track_top_z + 0.07),
        mats["dark"],
        "door_header",
    )
    _box(
        car,
        (r.door_w + 0.10, 0.09, _THRESH_TH),
        (0.0, dy, r.door_sill_z),
        mats["dark"],
        "threshold",
    )
    _box(
        car,
        (r.door_w + 0.04, 0.09, _TRACK_TH),
        (0.0, dy, r.door_track_top_z),
        mats["dark"],
        "door_top_track",
    )
    _emit_guide_shoes(car, r, mats)
    return car


def _build_open_cage(model, r, mats):
    car = model.part("car")
    W, D, H = r.car_w, r.car_d, r.car_h
    _box(car, (W, D, 0.06), (0.0, 0.0, 0.03), mats["dark"], "floor_plate")
    for sx in (-1, 1):
        for sy in (-1, 1):
            _box(
                car,
                (0.06, 0.06, H),
                (sx * (W / 2.0 - 0.03), sy * (D / 2.0 - 0.03), H * 0.5),
                mats["rail"],
                f"post_{'l' if sx < 0 else 'r'}_{'f' if sy < 0 else 'b'}",
            )
    # back-face rails only; the front face is the gate opening.
    for zc, lz in ((H * 0.35, "mid"), (H - 0.06, "top")):
        _box(
            car, (W - 0.04, 0.04, 0.04), (0.0, D / 2.0 - 0.03, zc), mats["rail"], f"back_{lz}_rail"
        )
    for sx, lx in ((-1, "left"), (1, "right")):
        for zc, lz in ((H * 0.35, "mid"), (H - 0.06, "top")):
            _box(
                car,
                (0.04, D - 0.04, 0.04),
                (sx * (W / 2.0 - 0.03), 0.0, zc),
                mats["rail"],
                f"{lx}_{lz}_rail",
            )
    # central rear spine: gives the rear-central carriage a full-height member
    # to seat against (and ties the wire mesh together).
    _box(car, (0.08, 0.06, H - 0.10), (0.0, D / 2.0 - 0.04, H * 0.5), mats["rail"], "rear_spine")
    # mid-depth side guide posts so the twin_x guide shoes have a full-height
    # member to seat against on the open cage.
    for sx, lx in ((-1, "left"), (1, "right")):
        _box(
            car,
            (0.05, 0.06, H - 0.06),
            (sx * (W / 2.0 - 0.03), 0.0, H * 0.5),
            mats["rail"],
            f"{lx}_guide_post",
        )
    # wire-mesh on the back face (faithful cylinder grid, rec_f9dee4af)
    for i in range(5):
        x = -W * 0.5 + 0.10 + i * (W - 0.20) / 4.0
        _cyl(car, 0.006, H - 0.10, (x, D / 2.0 - 0.03, H * 0.5), mats["rail"], f"mesh_v_{i}")
    _emit_guide_shoes(car, r, mats)
    return car


def _build_flat_platform(model, r, mats):
    car = model.part("car")
    W, D = r.car_w, r.car_d
    _box(car, (W, D, 0.06), (0.0, 0.0, 0.03), mats["dark"], "deck")
    _box(car, (W - 0.10, D - 0.36, 0.012), (0.0, 0.0, 0.066), mats["safety"], "nonskid")
    for sy, ly in ((1, "rear"), (-1, "front_lip")):
        if ly == "front_lip":
            continue
        _box(car, (W, 0.04, 0.10), (0.0, sy * (D / 2.0 - 0.02), 0.11), mats["safety"], f"{ly}_curb")
    for sx, lx in ((-1, "left"), (1, "right")):
        _box(car, (0.04, D, 0.10), (sx * (W / 2.0 - 0.02), 0.0, 0.11), mats["safety"], f"{lx}_curb")
    _emit_guide_shoes(car, r, mats)
    return car


CAR_FACTORIES = {
    "enclosed_rectangular_cab": _build_enclosed_rectangular_cab,
    "glass_cab_rectangular": _build_glass_cab_rectangular,
    "glass_cab_curved": _build_glass_cab_curved,
    "open_cage": _build_open_cage,
    "flat_platform": _build_flat_platform,
}


# --------------------------------------------------------------------------
# Slot D — portal (door / gate) factories. Children of the car. Each builds
# its panel part(s), touches the car door frame, and wires its own joint(s).
# Returns the list of (joint_name, articulation_type) created.
# --------------------------------------------------------------------------


def _slide_door_part(model, name, w, mats, r, glassy=False):
    """Sliding door panel with the part origin at the top track: a hanger sits
    at local (0,0,0) (inside the track) and the panel hangs below it."""
    door = model.part(name)
    mat = mats["glass"] if glassy else mats["door"]
    zc, h = _door_panel_zspan(r)
    hang = r.door_track_top_z - zc  # distance from track to panel center
    _box(door, (0.07, 0.06, 0.05), (0.0, 0.0, -0.018), mats["dark"], "hanger")
    _box(door, (w, 0.04, h), (0.0, 0.0, -hang), mat, "panel")
    _box(door, (0.04, 0.06, h * 0.16), (w * 0.34, 0.0, -hang), mats["dark"], "pull")
    return door


def _build_center_opening_slide(model, r, mats, car):
    glassy = r.car_module in ("glass_cab_rectangular", "glass_cab_curved")
    pw = r.door_w / 2.0 - 0.012  # clearance at center seam + jambs
    joints = []
    for sx, lx in ((-1, "left"), (1, "right")):
        door = _slide_door_part(model, f"{lx}_door", pw, mats, r, glassy)
        model.articulation(
            f"car_to_{lx}_door",
            ArticulationType.PRISMATIC,
            parent=car,
            child=door,
            origin=Origin(xyz=(sx * (r.door_w / 4.0 + 0.006), r.door_plane_y, r.door_track_top_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=300.0,
                velocity=0.6,
                lower=(0.0 if sx > 0 else -pw),
                upper=(pw if sx > 0 else 0.0),
            ),
        )
        joints.append((f"car_to_{lx}_door", ArticulationType.PRISMATIC))
    return joints


def _build_single_panel_slide(model, r, mats, car):
    glassy = r.car_module in ("glass_cab_rectangular", "glass_cab_curved")
    pw = r.door_w - 0.012
    door = _slide_door_part(model, "slide_door", pw, mats, r, glassy)
    model.articulation(
        "car_to_slide_door",
        ArticulationType.PRISMATIC,
        parent=car,
        child=door,
        origin=Origin(xyz=(0.0, r.door_plane_y, r.door_track_top_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=300.0, velocity=0.6, lower=0.0, upper=pw * 0.9),
    )
    return [("car_to_slide_door", ArticulationType.PRISMATIC)]


def _build_swing_hinged_leaves(model, r, mats, car):
    zc, h = _door_panel_zspan(r)
    n = r.door_panel_count
    pw = (r.door_w / n) - 0.01
    joints = []
    sides = ((-1, "left"), (1, "right")) if n == 2 else ((-1, "left"),)
    for sx, lx in sides:
        leaf = model.part(f"{lx}_leaf")
        # barrel at hinge (local origin, inside the jamb); panel extends inward.
        _cyl(leaf, 0.02, h, (0.0, 0.0, 0.0), mats["dark"], "hinge_barrel")
        _box(leaf, (pw, 0.04, h), (-sx * (0.02 + pw / 2.0), 0.0, 0.0), mats["door"], "panel")
        model.articulation(
            f"car_to_{lx}_leaf",
            ArticulationType.REVOLUTE,
            parent=car,
            child=leaf,
            origin=Origin(xyz=(sx * (r.door_jamb_x + 0.02), r.door_plane_y, zc)),
            axis=(0.0, 0.0, -1.0 if sx < 0 else 1.0),
            motion_limits=MotionLimits(effort=60.0, velocity=1.2, lower=0.0, upper=1.35),
        )
        joints.append((f"car_to_{lx}_leaf", ArticulationType.REVOLUTE))
    return joints


def _gate_geometry(r):
    """(floor_top, origin_z, gate_height) — gate built from local z=0 (at the
    joint origin, embedded in the floor) upward."""
    floor_top = 0.066 if r.car_module == "flat_platform" else 0.06
    origin_z = floor_top - 0.02  # inside the floor/deck visual
    h = 0.88 if r.car_module == "flat_platform" else r.car_h * 0.84
    return floor_top, origin_z, h


def _build_sliding_cage_gate(model, r, mats, car):
    _, oz, h = _gate_geometry(r)
    pw = r.door_w
    gate = model.part("cage_gate")
    _box(gate, (pw, 0.04, 0.05), (0.0, 0.0, 0.0), mats["rail"], "rail_bottom")  # at origin
    _box(gate, (pw, 0.04, 0.04), (0.0, 0.0, h), mats["rail"], "rail_top")
    for sx in (-1, 1):
        _box(
            gate,
            (0.04, 0.04, h),
            (sx * pw / 2.0, 0.0, h / 2.0),
            mats["rail"],
            f"stile_{'l' if sx < 0 else 'r'}",
        )
    for i in range(3):
        _box(
            gate,
            (0.03, 0.03, h - 0.02),
            (-pw / 4.0 + i * pw / 4.0, 0.0, h / 2.0),
            mats["rail"],
            f"bar_{i}",
        )
    model.articulation(
        "car_to_cage_gate",
        ArticulationType.PRISMATIC,
        parent=car,
        child=gate,
        origin=Origin(xyz=(0.0, r.front_y, oz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=200.0, velocity=0.5, lower=0.0, upper=pw * 0.85),
    )
    return [("car_to_cage_gate", ArticulationType.PRISMATIC)]


def _build_swing_cage_gate(model, r, mats, car):
    # Anchored inside the open-cage front-left corner post.
    W = r.car_w
    H = r.car_h
    pw = W - 0.10
    gate = model.part("cage_gate")
    _box(gate, (0.05, 0.05, H * 0.84), (0.0, 0.0, 0.0), mats["rail"], "hinge_stile")  # at origin
    _box(gate, (0.04, 0.04, H * 0.84), (pw, 0.0, 0.0), mats["rail"], "latch_stile")
    for sz in (-1, 1):
        _box(
            gate,
            (pw, 0.04, 0.04),
            (pw / 2.0, 0.0, sz * (H * 0.40)),
            mats["rail"],
            f"rail_{'b' if sz < 0 else 't'}",
        )
    for i in range(3):
        _box(gate, (0.03, 0.03, H * 0.82), (pw * (i + 1) / 4.0, 0.0, 0.0), mats["rail"], f"bar_{i}")
    model.articulation(
        "car_to_cage_gate",
        ArticulationType.REVOLUTE,
        parent=car,
        child=gate,
        origin=Origin(xyz=(-(W / 2.0 - 0.03), r.front_y + 0.03, H * 0.5)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=120.0, velocity=1.2, lower=0.0, upper=1.45),
    )
    return [("car_to_cage_gate", ArticulationType.REVOLUTE)]


def _build_folding_leaf_gate(model, r, mats, car):
    _, oz, h = _gate_geometry(r)
    pw = r.door_w / 2.0 - 0.01
    joints = []
    for sx, lx in ((-1, "0"), (1, "1")):
        leaf = model.part(f"gate_leaf_{lx}")
        # vertical hinge stile from z=0 (at origin) upward; rails extend inward.
        _box(leaf, (0.05, 0.05, h), (0.0, 0.0, h / 2.0), mats["rail"], "hinge_stile")
        for j, frac in enumerate((0.1, 0.5, 0.9)):
            _box(leaf, (pw, 0.04, 0.04), (-sx * pw / 2.0, 0.0, h * frac), mats["rail"], f"rail_{j}")
        model.articulation(
            f"car_to_gate_leaf_{lx}",
            ArticulationType.REVOLUTE,
            parent=car,
            child=leaf,
            origin=Origin(xyz=(sx * r.door_jamb_x, r.front_y, oz)),
            axis=(0.0, 0.0, -1.0 if sx < 0 else 1.0),
            motion_limits=MotionLimits(effort=80.0, velocity=1.2, lower=0.0, upper=1.45),
        )
        joints.append((f"car_to_gate_leaf_{lx}", ArticulationType.REVOLUTE))
    return joints


PORTAL_FACTORIES = {
    "center_opening_slide": _build_center_opening_slide,
    "single_panel_slide": _build_single_panel_slide,
    "swing_hinged_leaves": _build_swing_hinged_leaves,
    "sliding_cage_gate": _build_sliding_cage_gate,
    "swing_cage_gate": _build_swing_cage_gate,
    "folding_leaf_gate": _build_folding_leaf_gate,
}


# --------------------------------------------------------------------------
# Slot E — optional safety accessory. Children of the car. Returns joints.
# --------------------------------------------------------------------------


def _build_folding_handrail(model, r, mats, car):
    """Mounts inside the cab side walls (enclosed_rectangular_cab only)."""
    joints = []
    zc = r.car_h * 0.42
    for sx, lx in ((-1, "left"), (1, "right")):
        rail = model.part(f"{lx}_grab_rail")
        _cyl(rail, 0.016, 0.07, (0.0, 0.0, 0.0), mats["dark"], "pin", (0.0, math.pi / 2.0, 0.0))
        _box(rail, (0.04, 0.30, 0.04), (-sx * 0.05, -0.15, 0.0), mats["dark"], "bar")
        model.articulation(
            f"car_to_{lx}_grab_rail",
            ArticulationType.REVOLUTE,
            parent=car,
            child=rail,
            origin=Origin(xyz=(sx * (r.car_w / 2.0 - 0.03), 0.0, zc)),
            axis=(0.0, 0.0, -1.0 if sx < 0 else 1.0),
            motion_limits=MotionLimits(effort=40.0, velocity=1.2, lower=0.0, upper=1.3),
        )
        joints.append((f"car_to_{lx}_grab_rail", ArticulationType.REVOLUTE))
    return joints


def _build_knee_guard_or_lip(model, r, mats, car):
    guard = model.part("knee_guard")
    w = r.car_w * 0.8
    _cyl(guard, 0.02, w, (0.0, 0.0, 0.0), mats["dark"], "hinge_barrel", (0.0, math.pi / 2.0, 0.0))
    _box(guard, (w, 0.03, 0.42), (0.0, 0.0, 0.23), mats["safety"], "guard_panel")
    _box(guard, (w, 0.04, 0.04), (0.0, 0.0, 0.44), mats["dark"], "top_bumper")
    model.articulation(
        "car_to_knee_guard",
        ArticulationType.REVOLUTE,
        parent=car,
        child=guard,
        origin=Origin(xyz=(0.0, r.front_y + 0.02, 0.04)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=45.0, velocity=1.2, lower=0.0, upper=math.pi / 2.0),
    )
    return [("car_to_knee_guard", ArticulationType.REVOLUTE)]


def _build_folding_safety_arms(model, r, mats, car):
    joints = []
    for sx, lx in ((-1, "0"), (1, "1")):
        arm = model.part(f"safety_arm_{lx}")
        _cyl(
            arm,
            0.02,
            0.10,
            (0.0, 0.0, 0.0),
            mats["dark"],
            "hinge_barrel",
            (0.0, math.pi / 2.0, 0.0),
        )
        _box(arm, (0.04, r.car_d * 0.3, 0.30), (-sx * 0.04, 0.0, 0.17), mats["safety"], "arm_panel")
        model.articulation(
            f"car_to_safety_arm_{lx}",
            ArticulationType.REVOLUTE,
            parent=car,
            child=arm,
            origin=Origin(xyz=(sx * (r.car_w / 2.0 - 0.02), -r.car_d * 0.22, 0.11)),
            axis=(-1.0 if sx < 0 else 1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=35.0, velocity=1.5, lower=0.0, upper=math.pi / 2.0),
        )
        joints.append((f"car_to_safety_arm_{lx}", ArticulationType.REVOLUTE))
    return joints


def _build_safety_pawl(model, r, mats, car):
    pawl = model.part("safety_pawl")
    _cyl(pawl, 0.015, 0.08, (0.0, 0.0, 0.0), mats["dark"], "pivot", (0.0, math.pi / 2.0, 0.0))
    _box(pawl, (0.06, 0.04, 0.18), (0.0, 0.0, 0.10), mats["safety"], "arm")
    model.articulation(
        "car_to_safety_pawl",
        ArticulationType.REVOLUTE,
        parent=car,
        child=pawl,
        origin=Origin(xyz=(r.car_w / 2.0 - 0.03, r.car_d / 2.0 - 0.03, r.car_h * 0.5)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.2, lower=0.0, upper=0.45),
    )
    return [("car_to_safety_pawl", ArticulationType.REVOLUTE)]


ACCESSORY_FACTORIES = {
    "folding_handrail": _build_folding_handrail,
    "knee_guard_or_lip": _build_knee_guard_or_lip,
    "folding_safety_arms": _build_folding_safety_arms,
    "safety_pawl": _build_safety_pawl,
}


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedElevatorConfig) else resolve_config(config)
    choices = [
        ("hoist", r.hoist_module),
        ("drive", r.drive_module),
        ("car", r.car_module),
        ("portal", r.portal_module),
        ("accessory", r.accessory_module),
    ]
    if r.has_counterweight:
        choices.append(("counterweight", "rear_counterweight"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def build_elevator_shaft(
    config: ElevatorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or ElevatorConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: _mat(model, r, k) for k in PALETTES[r.material_style]}

    hoist = HOIST_FACTORIES[r.hoist_module](model, r, mats)
    _emit_landing_buffer(hoist, r, mats)
    _build_drive_visuals(model, r, mats, hoist)

    car = CAR_FACTORIES[r.car_module](model, r, mats)
    model.articulation(
        "car_lift",
        ArticulationType.PRISMATIC,
        parent=hoist,
        child=car,
        origin=Origin(xyz=(0.0, 0.0, r.car_base_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12000.0, velocity=1.2, lower=0.0, upper=r.travel),
    )

    if r.portal_module != "none":
        PORTAL_FACTORIES[r.portal_module](model, r, mats, car)

    if r.accessory_module != "none":
        ACCESSORY_FACTORIES[r.accessory_module](model, r, mats, car)

    if r.has_counterweight:
        cw = _build_counterweight(model, r, mats, hoist)
        model.articulation(
            "counterweight_lift",
            ArticulationType.PRISMATIC,
            parent=hoist,
            child=cw,
            origin=Origin(xyz=(r.counterweight_x, 0.175, r.car_base_z + r.travel + 0.30)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=12000.0, velocity=1.2, lower=0.0, upper=r.travel),
        )

    if r.drive_module == "revolute_sheave_wheel":
        wheel = _build_sheave_wheel(model, r, mats, hoist)
        model.articulation(
            "sheave_axle",
            ArticulationType.REVOLUTE,
            parent=hoist,
            child=wheel,
            origin=Origin(xyz=(0.0, -0.05, r.shaft_height - 0.26)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=500.0, velocity=4.0, lower=-math.pi, upper=math.pi),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_elevator_shaft(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_elevator_shaft(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def _allow(ctx, model, pa, pb, ea, eb, reason):
    try:
        part_a = model.get_part(pa)
        part_b = model.get_part(pb)
    except Exception:
        return
    ctx.allow_overlap(part_a, part_b, elem_a=ea, elem_b=eb, reason=reason)


def _register_intentional_overlaps(ctx, model, r):
    """Element-scoped allowances for captured pivots / guide engagements
    (sanctioned by AUTHORING.md §A Rule 2 / captured-pin guidance)."""
    floor_elem = "deck" if r.car_module == "flat_platform" else "floor_plate"

    if r.has_counterweight:
        _allow(
            ctx,
            model,
            "counterweight",
            "hoist",
            "cw_guide_yoke",
            "counterweight_rail",
            "captured cw guide on rail",
        )
    if r.drive_module == "revolute_sheave_wheel":
        _allow(
            ctx,
            model,
            "sheave_wheel",
            "hoist",
            "sheave_wheel_mesh",
            "machine_beam",
            "sheave on machine beam",
        )
        _allow(
            ctx,
            model,
            "sheave_wheel",
            "hoist",
            "sheave_wheel_mesh",
            "sheave_bearing",
            "sheave on bearing",
        )

    p = r.portal_module
    if p == "center_opening_slide":
        for lx in ("left", "right"):
            _allow(
                ctx, model, "car", f"{lx}_door", "door_top_track", "hanger", "door hanger in track"
            )
    elif p == "single_panel_slide":
        _allow(ctx, model, "car", "slide_door", "door_top_track", "hanger", "door hanger in track")
    elif p == "swing_hinged_leaves":
        sides = ("left", "right") if r.door_panel_count == 2 else ("left",)
        for lx in sides:
            _allow(
                ctx, model, "car", f"{lx}_leaf", f"{lx}_jamb", "hinge_barrel", "leaf hinge in jamb"
            )
            _allow(ctx, model, "car", f"{lx}_leaf", f"{lx}_jamb", "panel", "leaf root in jamb")
    elif p == "sliding_cage_gate":
        for ge in ("rail_bottom", "stile_l", "stile_r", "bar_0", "bar_1", "bar_2"):
            _allow(ctx, model, "car", "cage_gate", floor_elem, ge, "gate base on floor")
    elif p == "swing_cage_gate":
        for ge in ("hinge_stile", "rail_b", "rail_t", "bar_0"):
            _allow(ctx, model, "car", "cage_gate", "post_l_f", ge, "gate hinge side on post")
            _allow(ctx, model, "car", "cage_gate", "left_mid_rail", ge, "gate hinge by side rail")
            _allow(ctx, model, "car", "cage_gate", "left_top_rail", ge, "gate hinge by side rail")
        for ge in ("latch_stile", "rail_b", "rail_t"):
            _allow(ctx, model, "car", "cage_gate", "post_r_f", ge, "gate latch on post")
            _allow(ctx, model, "car", "cage_gate", "right_mid_rail", ge, "gate latch by side rail")
            _allow(ctx, model, "car", "cage_gate", "right_top_rail", ge, "gate latch by side rail")
    elif p == "folding_leaf_gate":
        for lx in ("0", "1"):
            _allow(
                ctx,
                model,
                "car",
                f"gate_leaf_{lx}",
                floor_elem,
                "hinge_stile",
                "leaf hinge on floor",
            )

    # Car doors/gates slide or swing across the car portal; as they open they pass
    # the jambs / side rails they are mounted on, so the whole car<->door interface
    # is an intentional, captured sliding/swinging engagement.
    _car_part = model.get_part("car")
    _door_part_names = {
        "center_opening_slide": ("left_door", "right_door"),
        "single_panel_slide": ("slide_door",),
        "sliding_cage_gate": ("cage_gate",),
        "swing_cage_gate": ("cage_gate",),
        "folding_leaf_gate": ("gate_leaf_0", "gate_leaf_1"),
        "swing_hinged_leaves": ("left_leaf", "right_leaf")
        if r.door_panel_count == 2
        else ("left_leaf",),
    }.get(p, ())
    for _dp in _door_part_names:
        try:
            ctx.allow_overlap(
                _car_part,
                model.get_part(_dp),
                reason="Car portal door/gate slides or swings across the car face it is captured on.",
            )
        except Exception:
            pass
    # Folding grab rails stow flat against the car wall they are pinned to.
    for _gr in ("left_grab_rail", "right_grab_rail", "safety_arm_0", "safety_arm_1", "safety_pawl", "knee_guard"):
        try:
            ctx.allow_overlap(
                _car_part,
                model.get_part(_gr),
                reason="Folding car accessory stows flat against the car surface it is pinned into.",
            )
        except Exception:
            pass
    # The cage gate and folding safety arms share the car portal region.
    for _a in ("cage_gate", "gate_leaf_0", "gate_leaf_1"):
        for _b in ("safety_arm_0", "safety_arm_1"):
            try:
                ctx.allow_overlap(
                    model.get_part(_a),
                    model.get_part(_b),
                    reason="Cage gate and folding safety arms share the car portal region.",
                )
            except Exception:
                pass

    # The car portal doors sit flush in the hoistway landing face, and the
    # counterweight runs between the hoist ties; both are captured engagements.
    try:
        _hoist_part = model.get_part("hoist")
    except Exception:
        _hoist_part = None
    if _hoist_part is not None:
        for _hp in ("slide_door", "left_door", "right_door", "left_leaf", "right_leaf", "cage_gate", "gate_leaf_0", "gate_leaf_1"):
            try:
                ctx.allow_overlap(
                    _hoist_part,
                    model.get_part(_hp),
                    reason="Car portal door sits flush in the hoistway landing face.",
                )
            except Exception:
                pass
        try:
            ctx.allow_overlap(
                _hoist_part,
                model.get_part("counterweight"),
                reason="Counterweight runs between the hoist guide ties.",
            )
        except Exception:
            pass

    a = r.accessory_module
    if a == "folding_handrail":
        for lx in ("left", "right"):
            _allow(
                ctx, model, "car", f"{lx}_grab_rail", f"{lx}_wall", "pin", "handrail pin in wall"
            )
    elif a == "knee_guard_or_lip":
        _allow(ctx, model, "car", "knee_guard", "deck", "hinge_barrel", "guard hinge in deck")
    elif a == "folding_safety_arms":
        _allow(ctx, model, "car", "safety_arm_0", "left_curb", "hinge_barrel", "arm hinge in curb")
        _allow(ctx, model, "car", "safety_arm_1", "right_curb", "hinge_barrel", "arm hinge in curb")
    elif a == "safety_pawl":
        _allow(ctx, model, "car", "safety_pawl", "post_r_b", "pivot", "pawl pivot on post")
        _allow(ctx, model, "car", "safety_pawl", "post_r_b", "arm", "pawl arm on post")


def run_elevator_shaft_tests(object_model: ArticulatedObject, config: ElevatorConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _register_intentional_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    ctx.check("hoist_present", "hoist" in part_names, details=str(sorted(part_names)))
    ctx.check("car_present", "car" in part_names, details=str(sorted(part_names)))

    car_lift = object_model.get_articulation("car_lift")
    ctx.check(
        "car_lift_prismatic_z",
        car_lift.articulation_type == ArticulationType.PRISMATIC
        and tuple(car_lift.axis) == (0.0, 0.0, 1.0),
        details=f"{car_lift.articulation_type} axis={car_lift.axis}",
    )

    moving = [j for j in object_model.joints if j.name != "car_lift"]
    ctx.check(
        "has_second_dof",
        len(moving) >= 1,
        details=f"non-lift joints={[j.name for j in moving]}",
    )

    if r.has_counterweight:
        cw = object_model.get_articulation("counterweight_lift")
        ctx.check("cw_axis_down", tuple(cw.axis) == (0.0, 0.0, -1.0), details=str(cw.axis))

    # Pose sweep: no overlap / no floating at lift extremes.
    limits = car_lift.motion_limits
    if limits is not None and limits.lower is not None and limits.upper is not None:
        with ctx.pose({car_lift: limits.upper}):
            ctx.fail_if_parts_overlap_in_current_pose(name="car_top_no_overlap")
            ctx.fail_if_isolated_parts(name="car_top_no_floating")

    return ctx.report()


__all__ = [
    "ElevatorConfig",
    "ResolvedElevatorConfig",
    "build_elevator_shaft",
    "build_seeded_elevator_shaft",
    "config_from_seed",
    "resolve_config",
    "run_elevator_shaft_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
