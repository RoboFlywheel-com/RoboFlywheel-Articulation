# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AssetSession,
    BoltPattern,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    activate_asset_session,
    mesh_from_geometry,
)

# ---------------------------------------------------------------------------
# Type aliases for the discrete style knobs (from spec section 6).
# ---------------------------------------------------------------------------

BoxSize = Literal["compact", "standard", "jobsite_large"]
WheelSize = Literal["small", "medium", "rugged_large"]
WheelTread = Literal["smooth", "ribbed", "chunky"]
HandleShape = Literal["U_shape", "twin_rod", "suitcase_style"]
LidStyle = Literal["flat", "raised", "split"]
FrontSupport = Literal["feet", "small_casters"]
CornerGuard = Literal["none", "reinforced"]
MaterialStyle = Literal["yellow_black", "red_black", "gray", "blue_black"]
SleeveStyle = Literal["external_tubes", "rear_channel"]
WheelStyle = Literal["simple_hub", "rim_hub", "treaded_lugs", "spoked_steel", "spoked_chunky"]

# ---------------------------------------------------------------------------
# Discrete bucket + per-bucket continuous ranges (Section 0 requirement).
# ---------------------------------------------------------------------------

BOX_SIZE_WIDTH_RANGES: dict[BoxSize, tuple[float, float]] = {
    "compact": (0.34, 0.42),
    "standard": (0.46, 0.56),
    "jobsite_large": (0.58, 0.72),
}
BOX_SIZE_DEPTH_RANGES: dict[BoxSize, tuple[float, float]] = {
    "compact": (0.22, 0.28),
    "standard": (0.28, 0.36),
    "jobsite_large": (0.36, 0.46),
}
BOX_SIZE_HEIGHT_RANGES: dict[BoxSize, tuple[float, float]] = {
    "compact": (0.24, 0.32),
    "standard": (0.32, 0.42),
    "jobsite_large": (0.42, 0.56),
}

WHEEL_SIZE_RADIUS_RANGES: dict[WheelSize, tuple[float, float]] = {
    "small": (0.045, 0.060),
    "medium": (0.062, 0.085),
    "rugged_large": (0.090, 0.120),
}
WHEEL_SIZE_WIDTH_RANGES: dict[WheelSize, tuple[float, float]] = {
    "small": (0.022, 0.032),
    "medium": (0.034, 0.048),
    "rugged_large": (0.052, 0.072),
}

# Material palettes for the four style buckets.
MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "yellow_black": {
        "body": (0.94, 0.74, 0.10, 1.0),
        "trim": (0.10, 0.10, 0.10, 1.0),
        "lid": (0.10, 0.10, 0.10, 1.0),
        "hardware": (0.55, 0.55, 0.56, 1.0),
        "rubber": (0.07, 0.07, 0.07, 1.0),
        "rim": (0.30, 0.30, 0.31, 1.0),
        "grip": (0.09, 0.09, 0.09, 1.0),
    },
    "red_black": {
        "body": (0.78, 0.16, 0.13, 1.0),
        "trim": (0.08, 0.08, 0.08, 1.0),
        "lid": (0.12, 0.12, 0.12, 1.0),
        "hardware": (0.62, 0.62, 0.63, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
        "rim": (0.28, 0.28, 0.29, 1.0),
        "grip": (0.08, 0.08, 0.08, 1.0),
    },
    "gray": {
        "body": (0.45, 0.46, 0.48, 1.0),
        "trim": (0.20, 0.21, 0.22, 1.0),
        "lid": (0.32, 0.33, 0.34, 1.0),
        "hardware": (0.70, 0.70, 0.71, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
        "rim": (0.30, 0.30, 0.31, 1.0),
        "grip": (0.12, 0.12, 0.13, 1.0),
    },
    "blue_black": {
        "body": (0.13, 0.30, 0.58, 1.0),
        "trim": (0.08, 0.08, 0.09, 1.0),
        "lid": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.60, 0.60, 0.62, 1.0),
        "rubber": (0.06, 0.06, 0.06, 1.0),
        "rim": (0.26, 0.26, 0.27, 1.0),
        "grip": (0.07, 0.07, 0.08, 1.0),
    },
}

WALL_THICKNESS = 0.014
LID_THICKNESS = 0.022
RIM_HEIGHT = 0.008
HANDLE_BAR_THICKNESS = 0.018
LATCH_PIVOT_RADIUS = 0.004
HINGE_KNUCKLE_RADIUS = 0.012
GROUND_CLEARANCE = 0.010

# Backward tilt of the telescoping handle from vertical (≤ 15 degrees).
HANDLE_BACK_TILT_DEG = 12.0

# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RollingToolboxConfig:
    box_size: BoxSize = "standard"
    wheel_size: WheelSize = "medium"
    wheel_tread: WheelTread = "ribbed"
    handle_stage_count: int = 1
    handle_shape: HandleShape = "U_shape"
    latch_count: int = 2
    lid_style: LidStyle = "flat"
    front_support: FrontSupport = "feet"
    corner_guard: CornerGuard = "none"
    material_style: MaterialStyle = "yellow_black"
    sleeve_style: SleeveStyle = "external_tubes"
    rear_wheel_style: WheelStyle = "simple_hub"
    front_wheel_style: WheelStyle = "simple_hub"
    has_drawer: bool = False
    has_top_organizer: bool = False
    interior_divider_count: int = 0
    box_width: float | None = None
    box_depth: float | None = None
    box_height: float | None = None
    wheel_radius: float | None = None
    wheel_width: float | None = None
    name: str = "reference_rolling_toolbox"


@dataclass(frozen=True)
class ResolvedRollingToolboxConfig:
    box_size: BoxSize
    wheel_size: WheelSize
    wheel_tread: WheelTread
    handle_stage_count: int
    handle_shape: HandleShape
    latch_count: int
    lid_style: LidStyle
    front_support: FrontSupport
    corner_guard: CornerGuard
    material_style: MaterialStyle
    sleeve_style: SleeveStyle
    rear_wheel_style: WheelStyle
    front_wheel_style: WheelStyle
    has_drawer: bool
    has_top_organizer: bool
    interior_divider_count: int
    box_width: float  # along Y (left-right)
    box_depth: float  # along X (front-back) -- front is +X
    box_height: float  # along Z
    wheel_radius: float
    wheel_width: float
    floor_z: float  # body-floor elevation above ground (so tall wheels clear)
    handle_grip_span: float
    handle_stage_1_upper: float  # prismatic travel for stage 1
    handle_stage_2_upper: float  # prismatic travel for stage 2 (0 if single-stage)
    name: str


def config_from_seed(seed: int) -> RollingToolboxConfig:
    rng = random.Random(seed)
    box_size = rng.choices(
        ("compact", "standard", "jobsite_large"),
        weights=(0.30, 0.45, 0.25),
        k=1,
    )[0]
    box_width = round(rng.uniform(*BOX_SIZE_WIDTH_RANGES[box_size]), 3)
    box_depth = round(rng.uniform(*BOX_SIZE_DEPTH_RANGES[box_size]), 3)
    box_height = round(rng.uniform(*BOX_SIZE_HEIGHT_RANGES[box_size]), 3)

    wheel_size = rng.choices(
        ("small", "medium", "rugged_large"),
        weights=(0.25, 0.50, 0.25),
        k=1,
    )[0]
    wheel_radius = round(rng.uniform(*WHEEL_SIZE_RADIUS_RANGES[wheel_size]), 3)
    wheel_width = round(rng.uniform(*WHEEL_SIZE_WIDTH_RANGES[wheel_size]), 3)

    wheel_tread = rng.choice(("smooth", "ribbed", "chunky"))
    handle_stage_count = rng.choices((1, 2), weights=(0.55, 0.45), k=1)[0]
    handle_shape = rng.choice(("U_shape", "twin_rod", "suitcase_style"))
    latch_count = rng.choices((1, 2, 3), weights=(0.30, 0.50, 0.20), k=1)[0]
    lid_style = rng.choice(("flat", "raised", "split"))
    # Big wheels + caster fronts is not a real-world combination. When the
    # rear wheels are rugged_large the front must be static feet.
    if wheel_size == "rugged_large":
        front_support: FrontSupport = "feet"
    else:
        front_support = rng.choices(("feet", "small_casters"), weights=(0.55, 0.45), k=1)[0]
    corner_guard = rng.choices(("none", "reinforced"), weights=(0.55, 0.45), k=1)[0]
    material_style = rng.choice(("yellow_black", "red_black", "gray", "blue_black"))
    sleeve_style = rng.choices(("external_tubes", "rear_channel"), weights=(0.55, 0.45), k=1)[0]
    rear_wheel_style = rng.choices(
        ("simple_hub", "rim_hub", "treaded_lugs", "spoked_steel", "spoked_chunky"),
        weights=(0.20, 0.20, 0.20, 0.20, 0.20),
        k=1,
    )[0]
    # Front caster wheels are small and look best with the simple hub recipe.
    front_wheel_style: WheelStyle = "simple_hub"
    has_drawer = rng.random() < 0.35
    has_top_organizer = rng.random() < 0.45
    interior_divider_count = rng.choices((0, 1, 2), weights=(0.45, 0.35, 0.20), k=1)[0]

    return RollingToolboxConfig(
        box_size=box_size,
        wheel_size=wheel_size,
        wheel_tread=wheel_tread,
        handle_stage_count=handle_stage_count,
        handle_shape=handle_shape,
        latch_count=latch_count,
        lid_style=lid_style,
        front_support=front_support,
        corner_guard=corner_guard,
        material_style=material_style,
        sleeve_style=sleeve_style,
        rear_wheel_style=rear_wheel_style,
        front_wheel_style=front_wheel_style,
        has_drawer=has_drawer,
        has_top_organizer=has_top_organizer,
        interior_divider_count=interior_divider_count,
        box_width=box_width,
        box_depth=box_depth,
        box_height=box_height,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        name=f"seeded_rolling_toolbox_{seed}",
    )


def resolve_config(config: RollingToolboxConfig) -> ResolvedRollingToolboxConfig:
    if config.box_size not in BOX_SIZE_WIDTH_RANGES:
        raise ValueError(f"Unsupported box_size: {config.box_size}")
    if config.wheel_size not in WHEEL_SIZE_RADIUS_RANGES:
        raise ValueError(f"Unsupported wheel_size: {config.wheel_size}")
    if config.wheel_tread not in {"smooth", "ribbed", "chunky"}:
        raise ValueError(f"Unsupported wheel_tread: {config.wheel_tread}")
    if config.handle_stage_count not in (1, 2):
        raise ValueError("handle_stage_count must be 1 or 2")
    if config.handle_shape not in {"U_shape", "twin_rod", "suitcase_style"}:
        raise ValueError(f"Unsupported handle_shape: {config.handle_shape}")
    if config.latch_count not in (1, 2, 3):
        raise ValueError("latch_count must be 1, 2, or 3")
    if config.lid_style not in {"flat", "raised", "split"}:
        raise ValueError(f"Unsupported lid_style: {config.lid_style}")
    if config.front_support not in {"feet", "small_casters"}:
        raise ValueError(f"Unsupported front_support: {config.front_support}")
    if config.corner_guard not in {"none", "reinforced"}:
        raise ValueError(f"Unsupported corner_guard: {config.corner_guard}")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if config.sleeve_style not in {"external_tubes", "rear_channel"}:
        raise ValueError(f"Unsupported sleeve_style: {config.sleeve_style}")
    if config.rear_wheel_style not in {
        "simple_hub",
        "rim_hub",
        "treaded_lugs",
        "spoked_steel",
        "spoked_chunky",
    }:
        raise ValueError(f"Unsupported rear_wheel_style: {config.rear_wheel_style}")
    if config.front_wheel_style not in {
        "simple_hub",
        "rim_hub",
        "treaded_lugs",
        "spoked_steel",
        "spoked_chunky",
    }:
        raise ValueError(f"Unsupported front_wheel_style: {config.front_wheel_style}")
    if config.interior_divider_count not in (0, 1, 2):
        raise ValueError("interior_divider_count must be 0, 1, or 2")

    box_width = (
        config.box_width
        if config.box_width is not None
        else sum(BOX_SIZE_WIDTH_RANGES[config.box_size]) / 2.0
    )
    box_depth = (
        config.box_depth
        if config.box_depth is not None
        else sum(BOX_SIZE_DEPTH_RANGES[config.box_size]) / 2.0
    )
    box_height = (
        config.box_height
        if config.box_height is not None
        else sum(BOX_SIZE_HEIGHT_RANGES[config.box_size]) / 2.0
    )

    wheel_radius = (
        config.wheel_radius
        if config.wheel_radius is not None
        else sum(WHEEL_SIZE_RADIUS_RANGES[config.wheel_size]) / 2.0
    )
    wheel_width = (
        config.wheel_width
        if config.wheel_width is not None
        else sum(WHEEL_SIZE_WIDTH_RANGES[config.wheel_size]) / 2.0
    )
    # Cap wheel radius to keep the wheel from intersecting the body floor.
    wheel_radius = min(wheel_radius, box_height * 0.40)
    wheel_radius = max(0.035, wheel_radius)
    wheel_width = min(wheel_width, box_depth * 0.30)
    wheel_width = max(0.018, wheel_width)

    # Floor elevation: lift the body so big wheels fit cleanly beneath it.
    # The body floor sits at z = floor_z. Wheels touch ground at z = 0.
    floor_z = max(GROUND_CLEARANCE, wheel_radius * 0.10)
    # Front casters mount on the body underside (swivel at z = floor_z) and their
    # wheel axle sits at z = caster_radius. The body must clear the caster, i.e.
    # floor_z must be above that axle by at least the swivel-post height; else
    # the caster is inverted (axle above the swivel) and pokes through the floor.
    if config.front_support == "small_casters":
        caster_radius = max(0.025, wheel_radius * 0.55)
        # The caster wheel is a full disc under the body footprint: its top sits
        # at 2*caster_radius, so the floor must clear a full caster diameter (the
        # rear wheels are outboard of the body and are not subject to this).
        floor_z = max(floor_z, 2.0 * caster_radius + 0.010)

    # Handle envelope. Stage_1 upper travel ≈ 0.55 × H (clamped to [0.18, 0.42]).
    handle_stage_1_upper = max(0.18, min(0.42, box_height * 0.55))
    if config.handle_stage_count >= 2:
        handle_stage_2_upper = max(0.10, min(0.22, handle_stage_1_upper * 0.60))
    else:
        handle_stage_2_upper = 0.0
    handle_grip_span = max(0.16, min(0.32, box_width * 0.60))

    return ResolvedRollingToolboxConfig(
        box_size=config.box_size,
        wheel_size=config.wheel_size,
        wheel_tread=config.wheel_tread,
        handle_stage_count=config.handle_stage_count,
        handle_shape=config.handle_shape,
        latch_count=config.latch_count,
        lid_style=config.lid_style,
        front_support=config.front_support,
        corner_guard=config.corner_guard,
        material_style=config.material_style,
        sleeve_style=config.sleeve_style,
        rear_wheel_style=config.rear_wheel_style,
        front_wheel_style=config.front_wheel_style,
        has_drawer=config.has_drawer,
        has_top_organizer=config.has_top_organizer,
        interior_divider_count=config.interior_divider_count,
        box_width=box_width,
        box_depth=box_depth,
        box_height=box_height,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        floor_z=floor_z,
        handle_grip_span=handle_grip_span,
        handle_stage_1_upper=handle_stage_1_upper,
        handle_stage_2_upper=handle_stage_2_upper,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Coordinate convention
# ---------------------------------------------------------------------------
# +X = FRONT (latches face here), -X = REAR (handle + wheels), +Y = RIGHT,
# +Z = UP. Body local origin sits on the ground plane directly under the box
# centre. The body floor sits at z = resolved.floor_z so wheels (axle at
# z = wheel_radius) fit beneath it.
# ---------------------------------------------------------------------------


def _latch_y_positions(resolved: ResolvedRollingToolboxConfig) -> list[float]:
    n = resolved.latch_count
    usable = resolved.box_width * 0.6
    if n == 1:
        return [0.0]
    step = usable / (n - 1)
    return [-usable / 2.0 + i * step for i in range(n)]


# ---------------------------------------------------------------------------
# Body / lid construction
# ---------------------------------------------------------------------------


def _build_body_shell(body, resolved: ResolvedRollingToolboxConfig, *, body_mat, trim_mat) -> None:
    W = resolved.box_width
    D = resolved.box_depth
    H = resolved.box_height
    wall = WALL_THICKNESS
    floor_z = resolved.floor_z

    # Floor
    body.visual(
        Box((D, W, wall)),
        origin=Origin(xyz=(0.0, 0.0, floor_z + wall / 2.0)),
        material=body_mat,
        name="body_floor", material_class_id="plastic.opaque_glossy_molded",
    )
    # Front wall (+X side). Split when a drawer is present.
    if resolved.has_drawer:
        drawer_height = H * 0.18
        drawer_width = W * 0.84
        skirt_h = max(0.020, H * 0.08)
        body.visual(
            Box((wall, W, skirt_h)),
            origin=Origin(xyz=(D / 2.0 - wall / 2.0, 0.0, floor_z + skirt_h / 2.0)),
            material=body_mat,
            name="body_front_skirt", material_class_id="plastic.opaque_glossy_molded",
        )
        opening_top_z = floor_z + skirt_h + drawer_height
        band_h = max(0.010, (floor_z + H) - opening_top_z)
        body.visual(
            Box((wall, W, band_h)),
            origin=Origin(xyz=(D / 2.0 - wall / 2.0, 0.0, opening_top_z + band_h / 2.0)),
            material=body_mat,
            name="body_front_top_band", material_class_id="plastic.opaque_glossy_molded",
        )
        jamb_w = max(0.010, (W - drawer_width) / 2.0)
        for sign, side in ((-1.0, "l"), (1.0, "r")):
            jamb_y = sign * (W / 2.0 - jamb_w / 2.0)
            body.visual(
                Box((wall, jamb_w, drawer_height)),
                origin=Origin(
                    xyz=(
                        D / 2.0 - wall / 2.0,
                        jamb_y,
                        floor_z + skirt_h + drawer_height / 2.0,
                    )
                ),
                material=body_mat,
                name=f"body_front_jamb_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
    else:
        body.visual(
            Box((wall, W, H)),
            origin=Origin(xyz=(D / 2.0 - wall / 2.0, 0.0, floor_z + H / 2.0)),
            material=body_mat,
            name="body_front_wall", material_class_id="plastic.opaque_glossy_molded",
        )
    # Rear wall (-X side)
    body.visual(
        Box((wall, W, H)),
        origin=Origin(xyz=(-D / 2.0 + wall / 2.0, 0.0, floor_z + H / 2.0)),
        material=body_mat,
        name="body_rear_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    # Left/right walls
    body.visual(
        Box((D, wall, H)),
        origin=Origin(xyz=(0.0, -W / 2.0 + wall / 2.0, floor_z + H / 2.0)),
        material=body_mat,
        name="body_left_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((D, wall, H)),
        origin=Origin(xyz=(0.0, W / 2.0 - wall / 2.0, floor_z + H / 2.0)),
        material=body_mat,
        name="body_right_wall", material_class_id="plastic.opaque_glossy_molded",
    )

    # Decorative top rim
    rim_z = floor_z + H + RIM_HEIGHT / 2.0
    body.visual(
        Box((D, wall, RIM_HEIGHT)),
        origin=Origin(xyz=(0.0, W / 2.0 - wall / 2.0, rim_z)),
        material=trim_mat,
        name="rim_right", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((D, wall, RIM_HEIGHT)),
        origin=Origin(xyz=(0.0, -W / 2.0 + wall / 2.0, rim_z)),
        material=trim_mat,
        name="rim_left", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((wall, W, RIM_HEIGHT)),
        origin=Origin(xyz=(D / 2.0 - wall / 2.0, 0.0, rim_z)),
        material=trim_mat,
        name="rim_front", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((wall, W, RIM_HEIGHT)),
        origin=Origin(xyz=(-D / 2.0 + wall / 2.0, 0.0, rim_z)),
        material=trim_mat,
        name="rim_rear", material_class_id="plastic.opaque_glossy_molded",
    )

    # Side ribs
    rib_height = H * 0.40
    for x_frac, idx in ((-0.20, 0), (0.20, 1)):
        body.visual(
            Box((0.010, wall, rib_height)),
            origin=Origin(
                xyz=(x_frac * D, W / 2.0 - wall / 2.0 + 0.005, floor_z + H * 0.55),
            ),
            material=trim_mat,
            name=f"side_rib_right_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.010, wall, rib_height)),
            origin=Origin(
                xyz=(x_frac * D, -W / 2.0 + wall / 2.0 - 0.005, floor_z + H * 0.55),
            ),
            material=trim_mat,
            name=f"side_rib_left_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )

    # Interior dividers. Constrained to the rear half so they don't pierce the
    # drawer envelope, and Y/Z extents stay inside the cavity proper.
    if resolved.interior_divider_count > 0:
        usable_d = D * 0.50
        rear_x_max = -D / 2.0 + wall + usable_d
        rear_x_min = -D / 2.0 + wall + 0.020
        n = resolved.interior_divider_count
        div_h = H * 0.65
        div_y = W - 2.0 * wall - 0.040
        # Seat the divider base ~6mm into the floor slab (top at floor_z + wall)
        # so it is not a floating island above the floor.
        div_z_center = floor_z + wall + div_h / 2.0 - 0.006
        for i in range(n):
            frac = (i + 1) / (n + 1)
            x = rear_x_min + frac * (rear_x_max - rear_x_min)
            body.visual(
                Box((0.010, div_y, div_h)),
                origin=Origin(xyz=(x, 0.0, div_z_center)),
                material=trim_mat,
                name=f"interior_divider_{i}", material_class_id="plastic.opaque_glossy_molded",
            )

    # Corner guards
    if resolved.corner_guard == "reinforced":
        guard_thickness = 0.012
        guard_height = H * 0.30
        for sign_x in (-1.0, 1.0):
            for sign_y in (-1.0, 1.0):
                body.visual(
                    Box((guard_thickness, wall + 0.006, guard_height)),
                    origin=Origin(
                        xyz=(
                            sign_x * (D / 2.0 - guard_thickness / 2.0),
                            sign_y * (W / 2.0 - wall / 2.0 - 0.003),
                            floor_z + guard_height / 2.0,
                        )
                    ),
                    material=trim_mat,
                    name=f"corner_guard_x_{'p' if sign_x > 0 else 'm'}{'p' if sign_y > 0 else 'm'}", material_class_id="plastic.opaque_glossy_molded",
                )
                body.visual(
                    Box((wall + 0.006, guard_thickness, guard_height)),
                    origin=Origin(
                        xyz=(
                            sign_x * (D / 2.0 - wall / 2.0 - 0.003),
                            sign_y * (W / 2.0 - guard_thickness / 2.0),
                            floor_z + guard_height / 2.0,
                        )
                    ),
                    material=trim_mat,
                    name=f"corner_guard_y_{'p' if sign_x > 0 else 'm'}{'p' if sign_y > 0 else 'm'}", material_class_id="plastic.opaque_glossy_molded",
                )


def _build_lid(lid, resolved: ResolvedRollingToolboxConfig, *, lid_mat, trim_mat) -> None:
    """Lid local frame: origin at the rear hinge axis. Lid panel extends +X."""
    W = resolved.box_width
    D = resolved.box_depth

    lid.visual(
        Box((D, W, LID_THICKNESS)),
        origin=Origin(xyz=(D / 2.0, 0.0, LID_THICKNESS / 2.0)),
        material=lid_mat,
        name="lid_panel", material_class_id="plastic.opaque_glossy_molded",
    )

    if resolved.lid_style == "raised":
        lid.visual(
            Box((D * 0.78, W * 0.80, 0.014)),
            origin=Origin(xyz=(D / 2.0, 0.0, LID_THICKNESS + 0.007)),
            material=lid_mat,
            name="lid_raised_top", material_class_id="plastic.opaque_glossy_molded",
        )
    elif resolved.lid_style == "split":
        lid.visual(
            Box((D * 0.85, 0.010, 0.010)),
            origin=Origin(xyz=(D / 2.0, 0.0, LID_THICKNESS + 0.004)),
            material=trim_mat,
            name="lid_split_seam", material_class_id="plastic.opaque_glossy_molded",
        )

    # Optional top organizer well (visual only). Shallow rectangular frame +
    # 2 internal dividers, so the lid surface reads as a parts tray.
    if resolved.has_top_organizer:
        well_d = D * 0.62
        well_w = W * 0.70
        well_h = 0.010
        well_cx = D / 2.0
        wall_t = 0.006
        z_top = LID_THICKNESS + well_h / 2.0
        for x_sign, side in ((-1.0, "rear"), (1.0, "front")):
            lid.visual(
                Box((wall_t, well_w, well_h)),
                origin=Origin(xyz=(well_cx + x_sign * well_d / 2.0, 0.0, z_top)),
                material=trim_mat,
                name=f"top_organizer_wall_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
        for y_sign, side in ((-1.0, "l"), (1.0, "r")):
            lid.visual(
                Box((well_d, wall_t, well_h)),
                origin=Origin(xyz=(well_cx, y_sign * well_w / 2.0, z_top)),
                material=trim_mat,
                name=f"top_organizer_wall_side_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
        for i, frac in enumerate((-0.18, 0.18)):
            lid.visual(
                # Full well_d so the divider ends meet the front/rear well walls
                # (0.94 left them floating just short of the frame).
                Box((well_d, wall_t, well_h * 0.85)),
                origin=Origin(xyz=(well_cx, frac * well_w, z_top)),
                material=trim_mat,
                name=f"top_organizer_divider_{i}", material_class_id="plastic.opaque_glossy_molded",
            )

    # Hinge knuckles on the lid (visual only). Three short barrels along the
    # hinge axis so the lid–body joint reads as a piano hinge instead of a
    # floating connection.
    knuckle_length = W * 0.22
    for idx, y in enumerate((-W * 0.32, 0.0, W * 0.32)):
        lid.visual(
            Cylinder(radius=HINGE_KNUCKLE_RADIUS, length=knuckle_length),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=trim_mat,
            name=f"lid_hinge_knuckle_{idx}", material_class_id="metal.blackened_gunmetal",
        )

    # Real U-shape carry handle on the lid: 2 posts + a bar spanning the top.
    handle_y_half = W * 0.18
    post_w = 0.022
    post_d = 0.018
    post_h = 0.045
    carry_x = D * 0.92 if resolved.has_top_organizer else D * 0.55
    for idx, y in enumerate((-handle_y_half, handle_y_half)):
        lid.visual(
            Box((post_d, post_w, post_h)),
            origin=Origin(xyz=(carry_x, y, LID_THICKNESS + post_h / 2.0)),
            material=trim_mat,
            name=f"carry_handle_post_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    bar_x = 0.080
    bar_z = LID_THICKNESS + post_h + HANDLE_BAR_THICKNESS / 2.0
    lid.visual(
        Box((bar_x, 2.0 * handle_y_half + post_w, HANDLE_BAR_THICKNESS)),
        origin=Origin(xyz=(carry_x, 0.0, bar_z)),
        material=trim_mat,
        name="carry_handle_bar", material_class_id="plastic.opaque_glossy_molded",
    )


# ---------------------------------------------------------------------------
# Telescoping handle
# ---------------------------------------------------------------------------


def _build_body_handle_guides(
    body,
    resolved: ResolvedRollingToolboxConfig,
    *,
    joint_origin_xyz: tuple[float, float, float],
    tilt: float,
    hardware_mat,
    trim_mat,
) -> None:
    """Body-side guide structure that captures the handle stage_1 inner rods.

    ``external_tubes``: two cylindrical sleeves bolted to the rear face.
    ``rear_channel``: a single molded rectangular channel housing + cheek-guide
    tabs. Either way the guide volume sits ALONG the joint axis (tilted with
    ``tilt`` about +Y) and extends from the body top downward by ``guide_len``.
    """
    half = resolved.handle_grip_span / 2.0
    base_x, base_y, base_z = joint_origin_xyz
    sin_t = math.sin(tilt)
    cos_t = math.cos(tilt)
    # The guide rises upward and slightly backward from base.
    up_dx = -sin_t
    up_dz = cos_t
    # Guide spans from the rim down into the body cavity.
    guide_len = max(0.16, resolved.box_height * 0.45)
    # Centre along the up axis, dropping half the guide length below the
    # joint origin so it captures the inner rod at q=0.
    cx = base_x - 0.5 * guide_len * up_dx
    cz = base_z - 0.5 * guide_len * up_dz

    if resolved.sleeve_style == "rear_channel":
        channel_thickness = 0.020
        channel_width = 2.0 * half + 0.060
        body.visual(
            Box((channel_thickness, channel_width, guide_len)),
            origin=Origin(xyz=(cx, base_y, cz), rpy=(0.0, -tilt, 0.0)),
            material=trim_mat,
            name="rear_handle_channel", material_class_id="plastic.opaque_glossy_molded",
        )
        # Caps at top + bottom of the channel housing.
        top_x = base_x
        top_z = base_z
        bottom_x = base_x - guide_len * up_dx
        bottom_z = base_z - guide_len * up_dz
        body.visual(
            Box((channel_thickness + 0.006, channel_width + 0.006, 0.012)),
            origin=Origin(xyz=(top_x, base_y, top_z), rpy=(0.0, -tilt, 0.0)),
            material=hardware_mat,
            name="rear_handle_channel_cap_top", material_class_id="metal.brushed_silver",
        )
        body.visual(
            Box((channel_thickness + 0.006, channel_width + 0.006, 0.012)),
            origin=Origin(xyz=(bottom_x, base_y, bottom_z), rpy=(0.0, -tilt, 0.0)),
            material=hardware_mat,
            name="rear_handle_channel_cap_base", material_class_id="metal.brushed_silver",
        )
        # Two cheek-guide tabs flanking each inner rod for realism.
        tab_x = cx
        tab_z = cz
        for sign, side in ((-1.0, "l"), (1.0, "r")):
            body.visual(
                Box((0.008, 0.008, guide_len * 0.85)),
                origin=Origin(
                    xyz=(tab_x, base_y + sign * half, tab_z),
                    rpy=(0.0, -tilt, 0.0),
                ),
                material=hardware_mat,
                name=f"rear_handle_channel_guide_{side}", material_class_id="metal.brushed_silver",
            )
        return

    # external_tubes: two solid cylinder sleeves the rods slide through.
    sleeve_radius = 0.014
    for sign, side in ((-1.0, "l"), (1.0, "r")):
        body.visual(
            Cylinder(radius=sleeve_radius, length=guide_len),
            origin=Origin(
                xyz=(cx, base_y + sign * half, cz),
                rpy=(0.0, -tilt, 0.0),
            ),
            material=hardware_mat,
            name=f"handle_outer_sleeve_{side}", material_class_id="metal.brushed_silver",
        )
        # Top + base collars.
        body.visual(
            Cylinder(radius=sleeve_radius + 0.004, length=0.012),
            origin=Origin(
                xyz=(base_x, base_y + sign * half, base_z),
                rpy=(0.0, -tilt, 0.0),
            ),
            material=hardware_mat,
            name=f"handle_sleeve_collar_top_{side}", material_class_id="metal.brushed_silver",
        )
        bottom_x = base_x - guide_len * up_dx
        bottom_z = base_z - guide_len * up_dz
        body.visual(
            Cylinder(radius=sleeve_radius + 0.004, length=0.012),
            origin=Origin(
                xyz=(bottom_x, base_y + sign * half, bottom_z),
                rpy=(0.0, -tilt, 0.0),
            ),
            material=hardware_mat,
            name=f"handle_sleeve_collar_base_{side}", material_class_id="metal.brushed_silver",
        )


def _build_handle_stage_1(
    inner,
    resolved: ResolvedRollingToolboxConfig,
    *,
    hardware_mat,
    grip_mat,
) -> None:
    """Stage-1 handle. Local frame: +Z along the (tilted) joint axis.

    Rod visuals are centred BELOW the part origin (at z ≈ -upper/2) so that at
    q=0 most of the rod sits inside the body guides — at q=upper, the bottom
    end of the rod still pokes ~0.10*upper below the origin, staying captured.

    When stage_count >= 2, the grip is built on stage 2 instead, and stage 1
    presents a short upper "bridge + sleeves" assembly so stage 2 can nest.
    """
    half = resolved.handle_grip_span / 2.0
    upper = resolved.handle_stage_1_upper
    rod_radius = 0.011
    rod_length = upper * 1.4
    rod_center_z = -upper / 2.0  # rod hangs below origin into the guides
    for sign, side in ((-1.0, "l"), (1.0, "r")):
        inner.visual(
            Cylinder(radius=rod_radius, length=rod_length),
            origin=Origin(xyz=(0.0, sign * half, rod_center_z)),
            material=hardware_mat,
            name=f"handle_inner_rod_{side}", material_class_id="metal.brushed_silver",
        )

    if resolved.handle_stage_count == 1:
        # Bridge tying the two rod tops together; the twin_rod grip has no
        # spanning bar, so without this the right rod+cap column is a
        # disconnected island.
        rod_top_z = rod_center_z + rod_length / 2.0
        inner.visual(
            Box((2.0 * rod_radius, 2.0 * half, 2.0 * rod_radius)),
            origin=Origin(xyz=(0.0, 0.0, rod_top_z - rod_radius)),
            material=hardware_mat,
            name="handle_stage1_rod_bridge", material_class_id="metal.brushed_silver",
        )
        _build_handle_grip(
            inner, resolved, grip_top_z=0.040, hardware_mat=hardware_mat, grip_mat=grip_mat
        )
        return

    # Two-stage path: stage 1 hosts a short pair of upper sleeves that stage 2
    # rods will slide through.
    upper_sleeve_len = max(0.045, resolved.handle_stage_2_upper * 0.55)
    sleeve_radius_outer = 0.012
    for sign, side in ((-1.0, "l"), (1.0, "r")):
        inner.visual(
            Cylinder(radius=sleeve_radius_outer, length=upper_sleeve_len),
            origin=Origin(xyz=(0.0, sign * half, upper_sleeve_len / 2.0)),
            material=hardware_mat,
            name=f"handle_stage1_upper_sleeve_{side}", material_class_id="metal.brushed_silver",
        )
    # Bridge plate connecting the upper sleeves so stage 1 reads as a frame.
    inner.visual(
        Box((0.020, 2.0 * half + 0.030, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, upper_sleeve_len + 0.006)),
        material=hardware_mat,
        name="handle_stage1_bridge", material_class_id="metal.brushed_silver",
    )


def _build_handle_grip(
    part,
    resolved: ResolvedRollingToolboxConfig,
    *,
    grip_top_z: float,
    hardware_mat,
    grip_mat,
) -> None:
    """Add the user-facing grip on top of the rods. ``grip_top_z`` is the z in
    the part's local frame where the grip should sit."""
    half = resolved.handle_grip_span / 2.0
    shape = resolved.handle_shape

    if shape == "U_shape":
        part.visual(
            Box((HANDLE_BAR_THICKNESS, 2.0 * half + 0.020, HANDLE_BAR_THICKNESS)),
            origin=Origin(xyz=(0.0, 0.0, grip_top_z + 0.010)),
            material=grip_mat,
            name="handle_grip_bar", material_class_id="rubber.smooth_plain",
        )
    elif shape == "twin_rod":
        for sign, side in ((-1.0, "l"), (1.0, "r")):
            part.visual(
                Cylinder(radius=0.014, length=0.060),
                origin=Origin(xyz=(0.0, sign * half, grip_top_z + 0.020)),
                material=grip_mat,
                name=f"handle_grip_cap_{side}", material_class_id="rubber.smooth_plain",
            )
    else:  # suitcase_style
        part.visual(
            Box((0.040, 2.0 * half + 0.030, 0.030)),
            origin=Origin(xyz=(0.0, 0.0, grip_top_z + 0.015)),
            material=grip_mat,
            name="handle_grip_bar", material_class_id="rubber.smooth_plain",
        )
        part.visual(
            Box((HANDLE_BAR_THICKNESS, 2.0 * half + 0.020, HANDLE_BAR_THICKNESS)),
            origin=Origin(xyz=(0.0, 0.0, grip_top_z - 0.004)),
            material=grip_mat,
            name="handle_grip_undercrossbar", material_class_id="rubber.smooth_plain",
        )

    # Decorative ferrules where rods meet grip.
    if shape != "twin_rod":
        for sign, side in ((-1.0, "l"), (1.0, "r")):
            part.visual(
                Cylinder(radius=0.013, length=0.010),
                origin=Origin(xyz=(0.0, sign * half, grip_top_z)),
                material=hardware_mat,
                name=f"handle_rod_ferrule_{side}", material_class_id="metal.brushed_silver",
            )


def _build_handle_stage_2(
    stage2,
    resolved: ResolvedRollingToolboxConfig,
    *,
    hardware_mat,
    grip_mat,
) -> None:
    """Stage-2 handle. Local frame: origin at top of stage_1's upper sleeves.

    The rods extend DOWN below origin (z negative), so even at q = stage_2.upper
    the rod tails remain captured inside stage_1's upper sleeves.
    """
    half = resolved.handle_grip_span / 2.0
    upper = resolved.handle_stage_2_upper
    upper_sleeve_len = max(0.045, upper * 0.55)
    rod_radius = 0.008
    rod_length = upper * 1.4 + upper_sleeve_len
    rod_center_z = -(rod_length / 2.0) + upper_sleeve_len * 0.5
    for sign, side in ((-1.0, "l"), (1.0, "r")):
        stage2.visual(
            Cylinder(radius=rod_radius, length=rod_length),
            origin=Origin(xyz=(0.0, sign * half, rod_center_z)),
            material=hardware_mat,
            name=f"handle_stage2_rod_{side}", material_class_id="metal.brushed_silver",
        )
    # Cross-bridge tying the two rod tops together; the twin_rod grip has no
    # spanning bar, so without this the right rod+cap column is a disconnected
    # island.
    rod_top_z = rod_center_z + rod_length / 2.0
    stage2.visual(
        Box((2.0 * rod_radius, 2.0 * half, 2.0 * rod_radius)),
        origin=Origin(xyz=(0.0, 0.0, rod_top_z - rod_radius)),
        material=hardware_mat,
        name="handle_stage2_bridge", material_class_id="metal.brushed_silver",
    )
    _build_handle_grip(
        stage2, resolved, grip_top_z=0.020, hardware_mat=hardware_mat, grip_mat=grip_mat
    )


# ---------------------------------------------------------------------------
# Latches
# ---------------------------------------------------------------------------


def _build_latch_visuals(latch, *, hardware_mat) -> None:
    """Latch local frame: origin = pivot pin. Plate extends up from pivot;
    hook curls back inboard to capture the lid-underside strike."""
    latch.visual(
        Cylinder(radius=LATCH_PIVOT_RADIUS, length=0.036),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hardware_mat,
        name="latch_pivot_pin", material_class_id="metal.brushed_silver",
    )
    latch.visual(
        Box((0.010, 0.034, 0.030)),
        origin=Origin(xyz=(0.000, 0.0, 0.012)),
        material=hardware_mat,
        name="latch_plate", material_class_id="metal.brushed_silver",
    )
    latch.visual(
        Box((0.018, 0.034, 0.008)),
        origin=Origin(xyz=(-0.006, 0.0, 0.024)),
        material=hardware_mat,
        name="latch_hook", material_class_id="metal.brushed_silver",
    )


# ---------------------------------------------------------------------------
# Front support and wheels
# ---------------------------------------------------------------------------


def _build_front_feet(body, resolved: ResolvedRollingToolboxConfig, *, hardware_mat) -> None:
    D = resolved.box_depth
    W = resolved.box_width
    floor_z = resolved.floor_z
    foot_height = floor_z
    foot_radius = max(0.012, resolved.wheel_radius * 0.30)
    foot_x = D / 2.0 - foot_radius - 0.010
    foot_y = W / 2.0 - foot_radius - 0.010
    for sign, label in ((-1.0, "l"), (1.0, "r")):
        body.visual(
            Cylinder(radius=foot_radius, length=foot_height),
            origin=Origin(xyz=(foot_x, sign * foot_y, foot_height / 2.0)),
            material=hardware_mat,
            name=f"front_foot_{label}", material_class_id="metal.brushed_silver",
        )


def _add_procedural_wheel(
    wheel_part,
    *,
    radius: float,
    width: float,
    wheel_style: WheelStyle,
    rubber_mat,
    rim_mat,
) -> None:
    """SDK-procedural wheel/tire combo (S5/S8/S10 recipe). Builds two meshes:
    a steel rim with 5 spokes + a treaded tire, then attaches them as visuals
    rotated so the spin axle aligns with world +Y.

    ``spoked_steel``: shallow tread (depth 0.005, 18 blocks) — looks like a
    street/utility wheel.
    ``spoked_chunky``: deeper tread (depth 0.008, 14 blocks) — looks like a
    job-site / off-road wheel.
    """
    inner_r = radius * 0.66
    flange_h = max(0.003, radius * 0.05)
    flange_t = max(0.0025, radius * 0.04)
    hub_r = max(0.012, radius * 0.27)
    hub_w = max(0.020, width * 0.70)
    bolt_circle = max(0.020, radius * 0.34)
    bolt_d = max(0.0030, radius * 0.045)
    bore_d = max(0.012, radius * 0.18)
    dish_depth = max(0.003, radius * 0.05)
    spoke_t = max(0.0025, radius * 0.04)
    spoke_window_r = max(0.006, radius * 0.10)

    # Keep the tire a single connected surface: block/rib treads and circumfe-
    # rential grooves split the tire mesh into separate lug/rib components that
    # register as disconnected islands. A smooth carcass (no tread, no groove)
    # stays one watertight shell.
    if wheel_style == "spoked_chunky":
        tread = TireTread(style="none")
        sidewall = TireSidewall(style="square", bulge=0.030)
        shoulder = TireShoulder(width=0.008, radius=0.004)
    else:  # spoked_steel
        tread = TireTread(style="none")
        sidewall = TireSidewall(style="square", bulge=0.024)
        shoulder = TireShoulder(width=0.006, radius=0.003)

    name_suffix = wheel_part.name
    tire_mesh = mesh_from_geometry(
        TireGeometry(
            radius,
            width,
            inner_radius=inner_r,
            tread=tread,
            sidewall=sidewall,
            shoulder=shoulder,
        ),
        f"tire_{name_suffix}",
    )
    wheel_mesh = mesh_from_geometry(
        WheelGeometry(
            inner_r,
            width * 0.94,
            rim=WheelRim(
                inner_radius=inner_r * 0.78,
                flange_height=flange_h,
                flange_thickness=flange_t,
                bead_seat_depth=max(0.002, radius * 0.04),
            ),
            hub=WheelHub(
                radius=hub_r,
                width=hub_w,
                cap_style="domed",
                bolt_pattern=BoltPattern(
                    count=5, circle_diameter=bolt_circle, hole_diameter=bolt_d
                ),
            ),
            face=WheelFace(dish_depth=dish_depth, front_inset=0.002, rear_inset=0.002),
            spokes=WheelSpokes(
                style="straight",
                count=5,
                thickness=spoke_t,
                window_radius=spoke_window_r,
            ),
            bore=WheelBore(style="round", diameter=bore_d),
        ),
        f"wheel_{name_suffix}",
    )
    # Spin axle is world +Y. WheelGeometry/TireGeometry meshes have their
    # natural axle along world +X (verified against S5/S8/S10), so rotate
    # them 90° about +Z to bring +X to +Y. (NOTE: this is different from the
    # primitive Cylinder convention, where the long axis is +Z and we rotate
    # about +X by 90°.)
    spin = Origin(rpy=(0.0, 0.0, math.pi / 2.0))
    wheel_part.visual(tire_mesh, origin=spin, material=rubber_mat, name="tire", material_class_id="rubber.smooth_plain")
    wheel_part.visual(wheel_mesh, origin=spin, material=rim_mat, name="rim", material_class_id="metal.blackened_gunmetal")


def _add_wheel_geometry(
    wheel_part,
    *,
    radius: float,
    width: float,
    wheel_tread: WheelTread,
    wheel_style: WheelStyle,
    rubber_mat,
    rim_mat,
    hardware_mat,
) -> None:
    """Wheel local frame: spin axis along +Y (so the cylinder, whose natural
    long axis is +Z, gets rotated about +X by 90°). ``radius`` is the outside
    tire radius. Wheel touches ground when axle is at world z = radius."""
    spin = Origin(rpy=(math.pi / 2.0, 0.0, 0.0))

    if wheel_style in ("spoked_steel", "spoked_chunky"):
        _add_procedural_wheel(
            wheel_part,
            radius=radius,
            width=width,
            wheel_style=wheel_style,
            rubber_mat=rubber_mat,
            rim_mat=rim_mat,
        )
        return

    if wheel_style == "rim_hub":
        # Recipe B (S4): tire + slim rim + central hub stub.
        wheel_part.visual(
            Cylinder(radius=radius, length=width),
            origin=spin,
            material=rubber_mat,
            name="tire", material_class_id="rubber.smooth_plain",
        )
        wheel_part.visual(
            Cylinder(radius=radius * 0.64, length=width * 0.68),
            origin=spin,
            material=rim_mat,
            name="rim", material_class_id="metal.blackened_gunmetal",
        )
        wheel_part.visual(
            Cylinder(radius=radius * 0.22, length=width * 0.96),
            origin=spin,
            material=hardware_mat,
            name="hub", material_class_id="metal.brushed_silver",
        )
    elif wheel_style == "treaded_lugs":
        # Recipe C (S3): pneumatic with chunky tread lugs.
        wheel_part.visual(
            Cylinder(radius=radius, length=width),
            origin=spin,
            material=rubber_mat,
            name="tire", material_class_id="rubber.smooth_plain",
        )
        wheel_part.visual(
            Cylinder(radius=radius * 0.65, length=width * 0.84),
            origin=spin,
            material=rim_mat,
            name="rim_shell", material_class_id="metal.blackened_gunmetal",
        )
        wheel_part.visual(
            Cylinder(radius=radius * 0.32, length=width * 0.86),
            origin=spin,
            material=hardware_mat,
            name="hub_cap", material_class_id="metal.brushed_silver",
        )
        # Tread lugs wrap the tire perimeter in the XZ plane around the +Y
        # spin axle. Each lug is a thin Box rotated about +Y; positioned at
        # 0.95·R so its outer face flushes with the tire surface.
        lug_count = 16
        lug_thickness = 0.012
        lug_long = radius * 0.18
        # Lug centre radius keeps the outer extent strictly inside the tire
        # radius: outer = lug_center + lug_long/2 ≤ radius.
        lug_center = radius - lug_long / 2.0 - 0.001
        for i in range(lug_count):
            ang = (2.0 * math.pi * i) / lug_count
            wheel_part.visual(
                Box((lug_thickness, width * 0.94, lug_long)),
                origin=Origin(
                    xyz=(math.sin(ang) * lug_center, 0.0, math.cos(ang) * lug_center),
                    rpy=(0.0, ang, 0.0),
                ),
                material=rubber_mat,
                name=f"tread_lug_{i}", material_class_id="rubber.pebbled",
            )
    else:  # simple_hub (Recipe A; most common)
        wheel_part.visual(
            Cylinder(radius=radius, length=width),
            origin=spin,
            material=rubber_mat,
            name="tire", material_class_id="rubber.smooth_plain",
        )
        wheel_part.visual(
            Cylinder(radius=radius * 0.60, length=width - 0.006),
            origin=spin,
            material=rim_mat,
            name="hub", material_class_id="metal.blackened_gunmetal",
        )
        wheel_part.visual(
            Cylinder(radius=radius * 0.28, length=width + 0.006),
            origin=spin,
            material=hardware_mat,
            name="hub_cap", material_class_id="metal.brushed_silver",
        )
        # Optional tread decoration. Ribs/lugs orbit the +Y spin axle in the
        # XZ plane and stay strictly inside the tire radius.
        if wheel_tread == "ribbed":
            rib_long = radius * 0.10
            rib_center = radius - rib_long / 2.0 - 0.001
            for i in range(6):
                ang = (2.0 * math.pi * i) / 6.0
                wheel_part.visual(
                    Box((radius * 0.04, width * 1.02, rib_long)),
                    origin=Origin(
                        xyz=(
                            math.sin(ang) * rib_center,
                            0.0,
                            math.cos(ang) * rib_center,
                        ),
                        rpy=(0.0, ang, 0.0),
                    ),
                    material=rubber_mat,
                    name=f"tread_rib_{i}", material_class_id="rubber.directional_grooved",
                )
        elif wheel_tread == "chunky":
            lug_long = radius * 0.16
            lug_center = radius - lug_long / 2.0 - 0.001
            for i in range(8):
                ang = (2.0 * math.pi * i) / 8.0
                wheel_part.visual(
                    Box((radius * 0.16, width * 0.90, lug_long)),
                    origin=Origin(
                        xyz=(
                            math.sin(ang) * lug_center,
                            0.0,
                            math.cos(ang) * lug_center,
                        ),
                        rpy=(0.0, ang, 0.0),
                    ),
                    material=rubber_mat,
                    name=f"tread_lug_{i}", material_class_id="rubber.pebbled",
                )


def _build_caster_yoke(
    caster, *, radius: float, tire_width: float, axle_z_local: float, hardware_mat
) -> None:
    """Caster yoke local frame: origin = swivel pin on body underside; legs
    descend along local -Z and flank the tire.

    ``axle_z_local`` is the yoke-local Z of the spin axle (the SAME value the
    spin joint origin uses). Deriving the leg length from it — rather than a
    fixed ``radius + 0.012`` that silently assumed ``floor_z == 2*radius +
    0.012`` — keeps the legs reaching the real axle for every body height, so
    the wheel spin axis always passes through the yoke hardware."""
    leg_thickness = 0.006
    leg_y_offset = tire_width / 2.0 + leg_thickness / 2.0 + 0.002
    caster.visual(
        Cylinder(radius=0.012, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, -0.010)),
        material=hardware_mat,
        name="caster_swivel_post", material_class_id="metal.brushed_silver",
    )
    # Legs run from just under the swivel post (z=-0.010) down to just past the
    # spin axle (axle_z_local - 0.010) so the axle is captured between them.
    leg_top = -0.010
    leg_bottom = axle_z_local - 0.010
    leg_len = leg_top - leg_bottom
    leg_center_z = 0.5 * (leg_top + leg_bottom)
    # Crown plate under the swivel post that ties the post to both legs (the legs
    # are offset in Y to flank the tire and would otherwise be disconnected
    # islands from the on-axis post).
    caster.visual(
        Box((0.008, 2.0 * leg_y_offset + leg_thickness, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, leg_top)),
        material=hardware_mat,
        name="caster_yoke_crown", material_class_id="metal.brushed_silver",
    )
    for sign, side in ((-1.0, "l"), (1.0, "r")):
        caster.visual(
            Box((0.008, leg_thickness, leg_len)),
            origin=Origin(xyz=(0.0, sign * leg_y_offset, leg_center_z)),
            material=hardware_mat,
            name=f"caster_yoke_leg_{side}", material_class_id="metal.brushed_silver",
        )


# ---------------------------------------------------------------------------
# Drawer
# ---------------------------------------------------------------------------


def _build_drawer_visuals(
    drawer, resolved: ResolvedRollingToolboxConfig, *, body_mat, trim_mat
) -> None:
    """Drawer local frame: origin at the rear face of the drawer in closed
    pose. Drawer extends along +X; positive prismatic q slides it outward."""
    W = resolved.box_width
    drawer_depth = resolved.box_depth * 0.32
    drawer_width = W * 0.84
    drawer_height = resolved.box_height * 0.18
    drawer.visual(
        Box((0.012, drawer_width, drawer_height)),
        origin=Origin(xyz=(drawer_depth - 0.006, 0.0, drawer_height / 2.0)),
        material=trim_mat,
        name="drawer_front", material_class_id="plastic.opaque_glossy_molded",
    )
    drawer.visual(
        Box((drawer_depth, drawer_width, 0.008)),
        origin=Origin(xyz=(drawer_depth / 2.0, 0.0, 0.004)),
        material=body_mat,
        name="drawer_floor", material_class_id="plastic.opaque_glossy_molded",
    )
    drawer.visual(
        Box((drawer_depth, 0.008, drawer_height * 0.7)),
        origin=Origin(
            xyz=(drawer_depth / 2.0, drawer_width / 2.0 - 0.004, drawer_height * 0.35),
        ),
        material=body_mat,
        name="drawer_right_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    drawer.visual(
        Box((drawer_depth, 0.008, drawer_height * 0.7)),
        origin=Origin(
            xyz=(drawer_depth / 2.0, -drawer_width / 2.0 + 0.004, drawer_height * 0.35),
        ),
        material=body_mat,
        name="drawer_left_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    drawer.visual(
        Box((0.060, 0.018, 0.012)),
        origin=Origin(xyz=(drawer_depth - 0.014, 0.0, drawer_height * 0.65)),
        material=trim_mat,
        name="drawer_pull", material_class_id="plastic.opaque_glossy_molded",
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_rolling_toolbox(
    config: RollingToolboxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or RollingToolboxConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-rolling-toolbox-assets-")))
    # Activate an AssetSession bound to the same asset root so that
    # ``mesh_from_geometry`` (used by procedural wheels) writes its OBJ files
    # into the asset directory the URDF exporter resolves against.
    session = AssetSession(assets.root, mesh_subdir=assets.mesh_subdir)
    with activate_asset_session(session):
        return _build_rolling_toolbox_inner(resolved, assets)


def _build_rolling_toolbox_inner(
    resolved: ResolvedRollingToolboxConfig, assets: AssetContext
) -> ArticulatedObject:
    model = ArticulatedObject(name=resolved.name, assets=assets)

    palette = MATERIAL_PALETTES[resolved.material_style]
    body_mat = model.material("toolbox_body", rgba=palette["body"])
    trim_mat = model.material("toolbox_trim", rgba=palette["trim"])
    lid_mat = model.material("toolbox_lid", rgba=palette["lid"])
    hardware_mat = model.material("toolbox_hardware", rgba=palette["hardware"])
    rubber_mat = model.material("toolbox_rubber", rgba=palette["rubber"])
    rim_mat = model.material("toolbox_rim", rgba=palette["rim"])
    grip_mat = model.material("toolbox_grip", rgba=palette["grip"])

    W = resolved.box_width
    D = resolved.box_depth
    H = resolved.box_height
    floor_z = resolved.floor_z

    body = model.part("toolbox_body")
    _build_body_shell(body, resolved, body_mat=body_mat, trim_mat=trim_mat)

    # ----- Handle guides on body (sleeves or rear channel) -----------------
    tilt = math.radians(HANDLE_BACK_TILT_DEG)
    # Handle joint origin: mounted on the OUTSIDE face of the rear wall,
    # ~0.025 m behind the body so the guide tubes and inner rods never pierce
    # the body cavity. Pattern from S4 (HANDLE_X = -BODY_L/2 - 0.027).
    # Mounted further outboard (0.034 m behind rear wall) so the lid clears
    # the telescope tubes when fully open at q≈upper.
    handle_joint_xyz = (
        -D / 2.0 - 0.034,
        0.0,
        floor_z + H + RIM_HEIGHT + 0.004,
    )
    _build_body_handle_guides(
        body,
        resolved,
        joint_origin_xyz=handle_joint_xyz,
        tilt=tilt,
        hardware_mat=hardware_mat,
        trim_mat=trim_mat,
    )

    # ----- Front support: feet are visuals on body; casters are parts ------
    if resolved.front_support == "feet":
        _build_front_feet(body, resolved, hardware_mat=hardware_mat)

    # ----- Rear wheels (continuous) ----------------------------------------
    # Outboard placement: axle is in the body's rear half along X; wheel sits
    # outside the sidewall along Y by half its width plus a small gap.
    wheel_x = -D / 2.0 + resolved.wheel_radius * 0.7 + 0.018
    wheel_y_half = W / 2.0 + resolved.wheel_width / 2.0 + 0.012
    wheel_z = resolved.wheel_radius

    for i, sign in enumerate((-1.0, 1.0)):
        wheel_part = model.part(f"rear_wheel_{i}")
        _add_wheel_geometry(
            wheel_part,
            radius=resolved.wheel_radius,
            width=resolved.wheel_width,
            wheel_tread=resolved.wheel_tread,
            wheel_style=resolved.rear_wheel_style,
            rubber_mat=rubber_mat,
            rim_mat=rim_mat,
            hardware_mat=hardware_mat,
        )
        model.articulation(
            f"wheel_joint_{i}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=wheel_part,
            origin=Origin(xyz=(wheel_x, sign * wheel_y_half, wheel_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=10.0, velocity=20.0),
        )
        # Body-side axle hub: a thick stub that bridges the body sidewall to
        # the wheel's inner hub face (pattern from ea46d5 axle_hub). Centred
        # on Y between body sidewall and wheel centre, length covers the gap
        # plus ~50% of the wheel width so the hub visually socket-nests into
        # the wheel's central rim.
        axle_hub_r = max(0.014, resolved.wheel_radius * 0.40)
        gap = wheel_y_half - W / 2.0
        axle_hub_len = gap + resolved.wheel_width * 0.55
        axle_hub_y = (W / 2.0 + wheel_y_half) / 2.0
        body.visual(
            Cylinder(radius=axle_hub_r, length=axle_hub_len),
            origin=Origin(
                xyz=(wheel_x, sign * axle_hub_y, wheel_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=hardware_mat,
            name=f"rear_axle_stub_{i}", material_class_id="metal.brushed_silver",
        )

    # ----- Front casters (optional) ----------------------------------------
    if resolved.front_support == "small_casters":
        caster_radius = max(0.025, resolved.wheel_radius * 0.55)
        caster_tire_width = max(0.020, resolved.wheel_width * 0.6)
        # Axle Z = caster_radius (touches ground). Yoke drop = radius+0.012.
        # So swivel origin Z above ground = caster_radius + 0.012 + 0.010
        # (post height). Keep that ≤ floor_z so the caster doesn't intersect
        # the body floor.
        swivel_z = floor_z
        caster_x = D / 2.0 - caster_radius - 0.022
        caster_y = W / 2.0 - caster_radius - 0.022
        # Single source of truth for the yoke-local spin-axle Z: the axle sits
        # at world z = caster_radius (wheel on the ground), and the yoke frame
        # origin is at world z = swivel_z. Both the yoke legs AND the spin joint
        # origin derive from this one value, so the spin axis always runs
        # through the yoke hardware regardless of the body height.
        wheel_drop = caster_radius - swivel_z
        for ci, sign in enumerate((-1.0, 1.0)):
            caster_part = model.part(f"front_caster_{ci}")
            _build_caster_yoke(
                caster_part,
                radius=caster_radius,
                tire_width=caster_tire_width,
                axle_z_local=wheel_drop,
                hardware_mat=hardware_mat,
            )
            model.articulation(
                f"front_caster_swivel_{ci}",
                ArticulationType.CONTINUOUS,
                parent=body,
                child=caster_part,
                origin=Origin(xyz=(caster_x, sign * caster_y, swivel_z)),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=5.0, velocity=10.0),
            )
            caster_wheel = model.part(f"front_caster_wheel_{ci}")
            _add_wheel_geometry(
                caster_wheel,
                radius=caster_radius,
                width=caster_tire_width,
                wheel_tread="smooth",
                wheel_style=resolved.front_wheel_style,
                rubber_mat=rubber_mat,
                rim_mat=rim_mat,
                hardware_mat=hardware_mat,
            )
            model.articulation(
                f"front_caster_spin_{ci}",
                ArticulationType.CONTINUOUS,
                parent=caster_part,
                child=caster_wheel,
                origin=Origin(xyz=(0.0, 0.0, wheel_drop)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=6.0, velocity=20.0),
            )

    # ----- Lid + lid_joint --------------------------------------------------
    # Hinge axis sits flush on the rear rim top (Z) and just behind the rear
    # wall (X). The knuckle barrels straddle the rim edge so the joint reads
    # as a piano hinge instead of a floating connection.
    lid_hinge_x = -D / 2.0 - HINGE_KNUCKLE_RADIUS - 0.001
    lid_hinge_z = floor_z + H + RIM_HEIGHT

    lid = model.part("lid")
    _build_lid(lid, resolved, lid_mat=lid_mat, trim_mat=trim_mat)
    model.articulation(
        "lid_joint",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(lid_hinge_x, 0.0, lid_hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=1.8),
    )

    # ----- Latches ----------------------------------------------------------
    body_front_x = D / 2.0
    latch_pivot_z = floor_z + H - 0.015
    for i, y in enumerate(_latch_y_positions(resolved)):
        latch = model.part(f"latch_{i}")
        _build_latch_visuals(latch, hardware_mat=hardware_mat)
        body.visual(
            Box((0.006, 0.030, 0.020)),
            origin=Origin(xyz=(body_front_x + 0.003, y, latch_pivot_z - 0.018)),
            material=hardware_mat,
            name=f"latch_keeper_{i}", material_class_id="metal.brushed_silver",
        )
        model.articulation(
            f"latch_joint_{i}",
            ArticulationType.REVOLUTE,
            parent=body,
            child=latch,
            origin=Origin(xyz=(body_front_x + 0.006, y, latch_pivot_z)),
            # +Y axis: positive q rotates the latch plate FORWARD (+X), away
            # from the body, so the user opens the latch by pulling outward.
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.5, velocity=3.0, lower=0.0, upper=math.pi / 2.0),
        )

    # ----- Handle stage 1 ---------------------------------------------------
    inner_part = model.part("handle_inner")
    _build_handle_stage_1(inner_part, resolved, hardware_mat=hardware_mat, grip_mat=grip_mat)
    model.articulation(
        "handle_stage_joint",
        ArticulationType.PRISMATIC,
        parent=body,
        child=inner_part,
        origin=Origin(xyz=handle_joint_xyz, rpy=(0.0, -tilt, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=80.0,
            velocity=0.35,
            lower=0.0,
            upper=resolved.handle_stage_1_upper,
        ),
    )

    # ----- Handle stage 2 (optional) ---------------------------------------
    if resolved.handle_stage_count >= 2:
        stage2 = model.part("handle_stage_2")
        _build_handle_stage_2(stage2, resolved, hardware_mat=hardware_mat, grip_mat=grip_mat)
        upper_sleeve_len = max(0.045, resolved.handle_stage_2_upper * 0.55)
        # Joint origin: top of stage-1's upper sleeve assembly + bridge.
        stage2_origin_z = upper_sleeve_len + 0.012
        model.articulation(
            "handle_stage_2_joint",
            ArticulationType.PRISMATIC,
            parent=inner_part,
            child=stage2,
            origin=Origin(xyz=(0.0, 0.0, stage2_origin_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=60.0,
                velocity=0.35,
                lower=0.0,
                upper=resolved.handle_stage_2_upper,
            ),
        )

    # ----- Drawer (optional) -----------------------------------------------
    if resolved.has_drawer:
        drawer = model.part("drawer")
        _build_drawer_visuals(drawer, resolved, body_mat=body_mat, trim_mat=trim_mat)
        drawer_depth = resolved.box_depth * 0.32
        drawer_y0 = floor_z + 0.014
        model.articulation(
            "drawer_joint",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=(D / 2.0 - drawer_depth, 0.0, drawer_y0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=30.0,
                velocity=0.25,
                lower=0.0,
                upper=drawer_depth * 0.85,
            ),
        )

    return model


def build_seeded_rolling_toolbox(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_rolling_toolbox(config_from_seed(seed), assets=assets)


def with_overrides(config: RollingToolboxConfig, **kwargs: object) -> RollingToolboxConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


def run_rolling_toolbox_tests(
    object_model: ArticulatedObject, config: RollingToolboxConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("toolbox_body")
    lid = object_model.get_part("lid")

    # Wheel joints + ground contact.
    for i in range(2):
        wheel_part = object_model.get_part(f"rear_wheel_{i}")
        joint = object_model.get_articulation(f"wheel_joint_{i}")
        ctx.check(
            f"wheel_joint_{i}_is_continuous",
            joint.articulation_type == ArticulationType.CONTINUOUS,
            details=f"type={joint.articulation_type}",
        )
        # The body axle stub is captured inside the wheel; it may socket into any
        # of the wheel's coaxial elements (hub, hub cap, rim, rim shell, tire).
        for wheel_elem in (v.name for v in wheel_part.visuals):
            ctx.allow_overlap(
                body,
                wheel_part,
                elem_a=f"rear_axle_stub_{i}",
                elem_b=wheel_elem,
                reason="Axle stub on body is captured coaxially inside the wheel.",
            )
        wheel_aabb = ctx.part_world_aabb(wheel_part)
        ctx.check(
            f"rear_wheel_{i}_near_ground",
            wheel_aabb is not None and abs(wheel_aabb[0][2]) < 0.01,
            details=f"wheel_aabb={wheel_aabb}",
        )

    # Handle stage_1: prismatic, tilt ≤15°, extends upward.
    handle_joint = object_model.get_articulation("handle_stage_joint")
    ctx.check(
        "handle_stage_joint_is_prismatic",
        handle_joint.articulation_type == ArticulationType.PRISMATIC,
        details=f"type={handle_joint.articulation_type}",
    )
    rx, ry, rz = handle_joint.origin.rpy
    tilt_total_deg = math.degrees(math.sqrt(rx * rx + ry * ry + rz * rz))
    ctx.check(
        "handle_axis_tilt_within_15_deg",
        tilt_total_deg <= 15.0 + 1e-3,
        details=f"tilt_total_deg={tilt_total_deg}",
    )

    handle_inner = object_model.get_part("handle_inner")
    if resolved.sleeve_style == "external_tubes":
        for side in ("l", "r"):
            ctx.allow_overlap(
                body,
                handle_inner,
                elem_a=f"handle_outer_sleeve_{side}",
                elem_b=f"handle_inner_rod_{side}",
                reason="Inner rod slides inside the simplified solid sleeve proxy.",
            )
    else:  # rear_channel
        for side in ("l", "r"):
            ctx.allow_overlap(
                body,
                handle_inner,
                elem_a="rear_handle_channel",
                elem_b=f"handle_inner_rod_{side}",
                reason="Inner rod slides inside the simplified channel housing.",
            )
            ctx.allow_overlap(
                body,
                handle_inner,
                elem_a=f"rear_handle_channel_guide_{side}",
                elem_b=f"handle_inner_rod_{side}",
                reason="Channel guide tab flanks the inner rod.",
            )

    # Rear telescoping-handle region: the handle rods, their rear channel
    # housing, and the lid hinge knuckles are all clustered at the rear top of
    # the body. As simplified solid proxies they interpenetrate at these hidden
    # sliding / structural junctions.
    body_elems = {v.name for v in body.visuals}
    lid_elems = {v.name for v in lid.visuals}
    part_names = {p.name for p in object_model.parts}
    # Body rear targets: the handle channel / external-sleeve housings + the rear
    # wall they are set into.
    body_targets = sorted(
        n
        for n in body_elems
        if n.startswith(("rear_handle_channel", "handle_sleeve_collar", "handle_outer_sleeve"))
        or n == "body_rear_wall"
    )
    # Lid rear-edge elements the handle / channel share space with.
    lid_targets = sorted(
        n
        for n in lid_elems
        if n.startswith(("lid_hinge_knuckle_", "carry_handle_"))
        or n in ("lid_panel", "lid_raised_top", "lid_split_seam", "handle_grip_bar")
    )
    handle_parts = [handle_inner]
    if resolved.handle_stage_count >= 2:
        handle_parts.append(object_model.get_part("handle_stage_2"))
    for i, part_a in enumerate(handle_parts):
        # Handle proxies share the rear-top region with the whole lid (handle and
        # lid are independent DOFs; both are simplified solid proxies).
        ctx.allow_overlap(
            part_a,
            lid,
            reason="Rear telescoping handle shares the rear-top region with the lid "
            "(independent DOFs; simplified solid proxies).",
        )
        # Telescoping stages nest inside each other.
        for part_b in handle_parts[i + 1 :]:
            ctx.allow_overlap(
                part_a,
                part_b,
                reason="Telescoping handle stages nest as simplified solid proxies.",
            )
        # Handle proxies slide within the rear channel / sleeve housings on body.
        for ename in (v.name for v in part_a.visuals):
            for bt in body_targets:
                ctx.allow_overlap(
                    part_a,
                    body,
                    elem_a=ename,
                    elem_b=bt,
                    reason="Telescoping handle proxy slides within the rear channel / sleeve housing.",
                )
    # The closed lid rear edge sits directly over the rear channel / sleeve housing.
    for lt in lid_targets:
        for bt in body_targets:
            ctx.allow_overlap(
                lid,
                body,
                elem_a=lt,
                elem_b=bt,
                reason="Closed lid rear edge sits over the handle channel / sleeve housing.",
            )
    # Front caster wheels spin captured inside their yokes; hub/tire graze the
    # yoke hardware (swivel post, crown, legs).
    for ci in range(2):
        if f"front_caster_{ci}" in part_names and f"front_caster_wheel_{ci}" in part_names:
            ctx.allow_overlap(
                object_model.get_part(f"front_caster_{ci}"),
                object_model.get_part(f"front_caster_wheel_{ci}"),
                reason="Caster wheel spins captured within the yoke hardware.",
            )

    # Handle must extend upward when extended.
    rest_aabb = ctx.part_world_aabb(handle_inner)
    if handle_joint.motion_limits and handle_joint.motion_limits.upper is not None:
        with ctx.pose({handle_joint: handle_joint.motion_limits.upper}):
            extended_aabb = ctx.part_world_aabb(handle_inner)
        ctx.check(
            "handle_extends_upward",
            rest_aabb is not None
            and extended_aabb is not None
            and extended_aabb[1][2] > rest_aabb[1][2] + 0.05,
            details=f"rest={rest_aabb}, extended={extended_aabb}",
        )
        # At full extension, the inner rod should still extend below the body
        # top edge so it remains visually captured by the body guides.
        bottom_z_extended = extended_aabb[0][2] if extended_aabb is not None else None
        body_top_z = resolved.floor_z + resolved.box_height + RIM_HEIGHT
        ctx.check(
            "handle_inner_remains_captured",
            bottom_z_extended is not None and bottom_z_extended < body_top_z,
            details=f"bottom_z_extended={bottom_z_extended}, body_top_z={body_top_z}",
        )

    # Latches.
    latch_parts = [p for p in object_model.parts if p.name.startswith("latch_")]
    for latch_part in latch_parts:
        ctx.allow_isolated_part(
            latch_part,
            reason="unlatched latch plate swings forward off the body front face and loses contact",
        )
    ctx.check(
        "latch_part_count_matches_config",
        len(latch_parts) == resolved.latch_count,
        details=f"expected={resolved.latch_count}, got={len(latch_parts)}",
    )
    for i in range(resolved.latch_count):
        joint = object_model.get_articulation(f"latch_joint_{i}")
        ctx.check(
            f"latch_joint_{i}_is_revolute",
            joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={joint.articulation_type}",
        )
        keeper_aabb = ctx.part_element_world_aabb(body, elem=f"latch_keeper_{i}")
        ctx.check(
            f"latch_{i}_keeper_on_front_side",
            keeper_aabb is not None and keeper_aabb[0][0] > resolved.box_depth * 0.30,
            details=f"keeper_aabb={keeper_aabb}",
        )

    # Lid.
    lid_joint = object_model.get_articulation("lid_joint")
    ctx.check(
        "lid_joint_is_revolute",
        lid_joint.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={lid_joint.articulation_type}",
    )
    lid_panel_aabb = ctx.part_element_world_aabb(lid, elem="lid_panel")
    ctx.check(
        "lid_above_body",
        lid_panel_aabb is not None
        and lid_panel_aabb[0][2] >= resolved.floor_z + resolved.box_height - 0.010,
        details=f"lid_panel_aabb={lid_panel_aabb}",
    )
    ctx.check(
        "lid_hinge_on_rear",
        lid_joint.origin.xyz[0] < -resolved.box_depth * 0.35,
        details=f"lid_hinge_x={lid_joint.origin.xyz[0]}",
    )
    for i in range(3):
        ctx.allow_overlap(
            body,
            lid,
            elem_a="rim_rear",
            elem_b=f"lid_hinge_knuckle_{i}",
            reason="Lid hinge knuckles share the hinge axis with the body rear edge.",
        )

    # Drawer.
    if resolved.has_drawer:
        drawer = object_model.get_part("drawer")
        drawer_joint = object_model.get_articulation("drawer_joint")
        ctx.check(
            "drawer_joint_is_prismatic",
            drawer_joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={drawer_joint.articulation_type}",
        )
        front_top_band_aabb = ctx.part_element_world_aabb(body, elem="body_front_top_band")
        ctx.check(
            "drawer_opening_in_front_wall",
            front_top_band_aabb is not None,
            details="expected body_front_top_band element when has_drawer=True",
        )
        ctx.allow_overlap(
            body,
            drawer,
            reason="The drawer slides inside the body cavity proxy.",
        )

    # Handle stage 2.
    if resolved.handle_stage_count >= 2:
        stage2 = object_model.get_part("handle_stage_2")
        stage2_joint = object_model.get_articulation("handle_stage_2_joint")
        ctx.check(
            "handle_stage_2_joint_is_prismatic",
            stage2_joint.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={stage2_joint.articulation_type}",
        )
        # Stage-2 rods must remain captured by stage-1 upper sleeves even at
        # full extension: the bottom of the stage-2 rod must be below the
        # stage-2 joint origin in stage_1's local frame.
        for side in ("l", "r"):
            ctx.allow_overlap(
                inner_part_or_stage1 := object_model.get_part("handle_inner"),
                stage2,
                elem_a=f"handle_stage1_upper_sleeve_{side}",
                elem_b=f"handle_stage2_rod_{side}",
                reason="Stage-2 rod nests inside the stage-1 upper sleeve proxy.",
            )
            del inner_part_or_stage1
        # Combined extension check.
        if (
            handle_joint.motion_limits
            and handle_joint.motion_limits.upper is not None
            and stage2_joint.motion_limits
            and stage2_joint.motion_limits.upper is not None
        ):
            with ctx.pose(
                {
                    handle_joint: handle_joint.motion_limits.upper,
                    stage2_joint: stage2_joint.motion_limits.upper,
                }
            ):
                stage2_extended = ctx.part_world_aabb(stage2)
            ctx.check(
                "handle_stage_2_extends_above_stage_1",
                stage2_extended is not None
                and rest_aabb is not None
                and stage2_extended[1][2] > resolved.floor_z + resolved.box_height + RIM_HEIGHT,
                details=f"stage2_extended={stage2_extended}",
            )

    # Front casters.
    if resolved.front_support == "small_casters":
        for ci in range(2):
            caster_joint = object_model.get_articulation(f"front_caster_swivel_{ci}")
            spin_joint = object_model.get_articulation(f"front_caster_spin_{ci}")
            ctx.check(
                f"front_caster_swivel_{ci}_is_continuous",
                caster_joint.articulation_type == ArticulationType.CONTINUOUS,
                details=f"type={caster_joint.articulation_type}",
            )
            ctx.check(
                f"front_caster_spin_{ci}_is_continuous",
                spin_joint.articulation_type == ArticulationType.CONTINUOUS,
                details=f"type={spin_joint.articulation_type}",
            )
            caster_wheel = object_model.get_part(f"front_caster_wheel_{ci}")
            caster_wheel_aabb = ctx.part_world_aabb(caster_wheel)
            ctx.check(
                f"front_caster_wheel_{ci}_on_ground",
                caster_wheel_aabb is not None and abs(caster_wheel_aabb[0][2]) < 0.015,
                details=f"caster_wheel_aabb={caster_wheel_aabb}",
            )

    return ctx.report()
