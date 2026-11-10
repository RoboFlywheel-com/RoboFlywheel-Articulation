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
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

# ---------------------------------------------------------------------------
# Type aliases for the discrete style knobs from spec section 2.
# ---------------------------------------------------------------------------

BoxAspectRatio = Literal["long", "compact", "deep"]
LidStyle = Literal["flat", "raised", "ribbed", "recessed"]
LatchStyle = Literal["flip_tab", "clamp", "hook"]
HandleStyle = Literal["top_bar", "folding", "molded", "none"]
CornerGuard = Literal["none", "small", "reinforced"]
MaterialStyle = Literal["plastic", "metal", "rugged_polymer"]

# ---------------------------------------------------------------------------
# Per-aspect-ratio envelope ranges. The aspect ratio is the spine "class" and
# the continuous lengths/widths/heights drawn from these ranges break the
# "same-class clone" effect, satisfying the discrete-bucket + continuous-range
# requirement in section 0 of 0_revised.md.
# ---------------------------------------------------------------------------

ASPECT_LENGTH_RANGES: dict[BoxAspectRatio, tuple[float, float]] = {
    "long": (0.420, 0.560),
    "compact": (0.260, 0.360),
    "deep": (0.300, 0.400),
}
ASPECT_WIDTH_RANGES: dict[BoxAspectRatio, tuple[float, float]] = {
    "long": (0.190, 0.260),
    "compact": (0.200, 0.260),
    "deep": (0.220, 0.290),
}
ASPECT_HEIGHT_RANGES: dict[BoxAspectRatio, tuple[float, float]] = {
    "long": (0.120, 0.170),
    "compact": (0.110, 0.160),
    "deep": (0.190, 0.260),
}

# ---------------------------------------------------------------------------
# Geometric constants (proportions, not absolute dimensions).
# ---------------------------------------------------------------------------

WALL_THICKNESS_RATIO = 0.045  # of body width
RIM_HEIGHT = 0.006
LID_THICKNESS = 0.022
HINGE_KNUCKLE_RADIUS = 0.0065
# The lid is authored in the hinge-local frame.  Start its panel just beyond
# the knuckle envelope so the alternating body-side knuckles have real sweep
# clearance instead of cutting through the panel.
LID_PANEL_REAR_X = HINGE_KNUCKLE_RADIUS + 0.001
LATCH_MOUNT_HEIGHT = 0.030
FOOT_HEIGHT = 0.012
TRAY_THICKNESS = 0.008
TRAY_RIM_HEIGHT = 0.014

# Latch pivot in the lid's local frame: just past the lid's front edge and
# slightly above the lid panel top so the latch hangs cleanly outside the body
# front wall when the lid is closed.
LATCH_PIVOT_X_PAST_LID_FRONT = 0.012
LATCH_PIVOT_Z_ABOVE_LID_TOP = 0.002

# Per-style keeper Z (block center) offset below the body rim. Tuned so that the
# bottom hook of each latch wraps the keeper pin in the closed pose.
LATCH_KEEPER_Z_BELOW_TOP: dict[str, float] = {
    "flip_tab": 0.022,
    "clamp": 0.038,
    "hook": 0.034,
}

MATERIAL_PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "plastic": {
        "body": (0.10, 0.32, 0.20, 1.0),
        "rim": (0.05, 0.20, 0.13, 1.0),
        "lid": (0.13, 0.40, 0.24, 1.0),
        "tray": (0.82, 0.76, 0.58, 1.0),
        "hardware": (0.78, 0.78, 0.74, 1.0),
        "handle": (0.10, 0.10, 0.10, 1.0),
    },
    "metal": {
        "body": (0.65, 0.66, 0.65, 1.0),
        "rim": (0.45, 0.46, 0.47, 1.0),
        "lid": (0.74, 0.74, 0.72, 1.0),
        "tray": (0.60, 0.60, 0.58, 1.0),
        "hardware": (0.30, 0.30, 0.31, 1.0),
        "handle": (0.10, 0.10, 0.10, 1.0),
    },
    "rugged_polymer": {
        "body": (0.18, 0.21, 0.24, 1.0),
        "rim": (0.10, 0.13, 0.15, 1.0),
        "lid": (0.55, 0.40, 0.10, 1.0),
        "tray": (0.25, 0.27, 0.29, 1.0),
        "hardware": (0.65, 0.67, 0.70, 1.0),
        "handle": (0.05, 0.05, 0.05, 1.0),
    },
}


@dataclass(frozen=True)
class TackleBoxConfig:
    box_aspect_ratio: BoxAspectRatio = "long"
    lid_style: LidStyle = "flat"
    latch_count: int = 1
    latch_style: LatchStyle = "flip_tab"
    handle_style: HandleStyle = "top_bar"
    tray_count: int = 1
    compartment_count: int = 4
    corner_guard: CornerGuard = "none"
    feet_count: int = 0
    material_style: MaterialStyle = "plastic"
    length: float | None = None
    width: float | None = None
    body_height: float | None = None
    name: str = "reference_tackle_box"


@dataclass(frozen=True)
class ResolvedTackleBoxConfig:
    box_aspect_ratio: BoxAspectRatio
    lid_style: LidStyle
    latch_count: int
    latch_style: LatchStyle
    handle_style: HandleStyle
    tray_count: int
    compartment_count: int
    corner_guard: CornerGuard
    feet_count: int
    material_style: MaterialStyle
    length: float
    width: float
    body_height: float
    wall_thickness: float
    name: str


def config_from_seed(seed: int) -> TackleBoxConfig:
    rng = random.Random(seed)
    aspect = rng.choices(
        ("long", "compact", "deep"),
        weights=(0.45, 0.30, 0.25),
        k=1,
    )[0]
    length = round(rng.uniform(*ASPECT_LENGTH_RANGES[aspect]), 3)
    width = round(rng.uniform(*ASPECT_WIDTH_RANGES[aspect]), 3)
    body_height = round(rng.uniform(*ASPECT_HEIGHT_RANGES[aspect]), 3)

    lid_style = rng.choice(("flat", "raised", "ribbed", "recessed"))
    latch_count = rng.choices((0, 1, 2, 3), weights=(0.20, 0.40, 0.30, 0.10), k=1)[0]
    latch_style = rng.choice(("flip_tab", "clamp", "hook"))
    handle_style = rng.choices(
        ("top_bar", "folding", "molded", "none"),
        weights=(0.35, 0.25, 0.25, 0.15),
        k=1,
    )[0]
    tray_count = rng.choices((0, 1, 2), weights=(0.25, 0.50, 0.25), k=1)[0]
    if tray_count == 0:
        compartment_count = 0
    else:
        compartment_count = rng.randint(2, 12)
    corner_guard = rng.choices(
        ("none", "small", "reinforced"),
        weights=(0.45, 0.35, 0.20),
        k=1,
    )[0]
    feet_count = rng.choice((0, 4))
    material_style = rng.choice(("plastic", "metal", "rugged_polymer"))

    return TackleBoxConfig(
        box_aspect_ratio=aspect,
        lid_style=lid_style,
        latch_count=latch_count,
        latch_style=latch_style,
        handle_style=handle_style,
        tray_count=tray_count,
        compartment_count=compartment_count,
        corner_guard=corner_guard,
        feet_count=feet_count,
        material_style=material_style,
        length=length,
        width=width,
        body_height=body_height,
        name=f"seeded_tackle_box_{seed}",
    )


def resolve_config(config: TackleBoxConfig) -> ResolvedTackleBoxConfig:
    if config.box_aspect_ratio not in ASPECT_LENGTH_RANGES:
        raise ValueError(f"Unsupported box_aspect_ratio: {config.box_aspect_ratio}")
    if config.lid_style not in ("flat", "raised", "ribbed", "recessed"):
        raise ValueError(f"Unsupported lid_style: {config.lid_style}")
    if config.latch_count not in (0, 1, 2, 3):
        raise ValueError("latch_count must be one of 0,1,2,3")
    if config.latch_style not in ("flip_tab", "clamp", "hook"):
        raise ValueError(f"Unsupported latch_style: {config.latch_style}")
    if config.handle_style not in ("top_bar", "folding", "molded", "none"):
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.tray_count not in (0, 1, 2):
        raise ValueError("tray_count must be 0,1, or 2")
    if config.compartment_count < 0 or config.compartment_count > 12:
        raise ValueError("compartment_count must be in [0, 12]")
    if config.corner_guard not in ("none", "small", "reinforced"):
        raise ValueError(f"Unsupported corner_guard: {config.corner_guard}")
    if config.feet_count not in (0, 4):
        raise ValueError("feet_count must be 0 or 4")
    if config.material_style not in MATERIAL_PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")

    length = (
        config.length
        if config.length is not None
        else sum(ASPECT_LENGTH_RANGES[config.box_aspect_ratio]) / 2.0
    )
    width = (
        config.width
        if config.width is not None
        else sum(ASPECT_WIDTH_RANGES[config.box_aspect_ratio]) / 2.0
    )
    body_height = (
        config.body_height
        if config.body_height is not None
        else sum(ASPECT_HEIGHT_RANGES[config.box_aspect_ratio]) / 2.0
    )

    # Auto-clamp coupling: when there are no trays, no compartments either.
    compartment_count = config.compartment_count if config.tray_count > 0 else 0
    # When there are trays but compartment_count was set to 0, bump to a sensible minimum.
    if config.tray_count > 0 and compartment_count < 2:
        compartment_count = 2

    wall_thickness = max(0.008, min(0.018, width * WALL_THICKNESS_RATIO))

    return ResolvedTackleBoxConfig(
        box_aspect_ratio=config.box_aspect_ratio,
        lid_style=config.lid_style,
        latch_count=config.latch_count,
        latch_style=config.latch_style,
        handle_style=config.handle_style,
        tray_count=config.tray_count,
        compartment_count=compartment_count,
        corner_guard=config.corner_guard,
        feet_count=config.feet_count,
        material_style=config.material_style,
        length=length,
        width=width,
        body_height=body_height,
        wall_thickness=wall_thickness,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _latch_y_positions(latch_count: int, width: float) -> list[float]:
    """Return Y coordinates for `latch_count` latches across the front edge."""
    if latch_count == 0:
        return []
    usable = width * 0.55
    if latch_count == 1:
        return [0.0]
    span = usable
    step = span / (latch_count - 1)
    start = -span / 2.0
    return [start + i * step for i in range(latch_count)]


def _foot_xy_positions(length: float, width: float) -> list[tuple[float, float]]:
    fx = length / 2.0 - 0.022
    fy = width / 2.0 - 0.022
    return [(-fx, -fy), (fx, -fy), (-fx, fy), (fx, fy)]


# ---------------------------------------------------------------------------
# Body construction
# ---------------------------------------------------------------------------


def _build_body_shell(body, resolved: ResolvedTackleBoxConfig, *, body_mat, rim_mat) -> None:
    L = resolved.length
    W = resolved.width
    H = resolved.body_height
    wall = resolved.wall_thickness
    floor = 0.012

    body.visual(
        Box((L, W, floor)),
        origin=Origin(xyz=(0.0, 0.0, floor / 2.0)),
        material=body_mat,
        name="body_floor", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((wall, W, H)),
        origin=Origin(xyz=(-L / 2.0 + wall / 2.0, 0.0, H / 2.0)),
        material=body_mat,
        name="body_rear_wall", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((wall, W, H)),
        origin=Origin(xyz=(L / 2.0 - wall / 2.0, 0.0, H / 2.0)),
        material=body_mat,
        name="body_front_wall", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((L, wall, H)),
        origin=Origin(xyz=(0.0, -W / 2.0 + wall / 2.0, H / 2.0)),
        material=body_mat,
        name="body_left_wall", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((L, wall, H)),
        origin=Origin(xyz=(0.0, W / 2.0 - wall / 2.0, H / 2.0)),
        material=body_mat,
        name="body_right_wall", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )

    # Top rim (visual only) sits at z = H + RIM_HEIGHT/2.
    rim_z = H + RIM_HEIGHT / 2.0
    body.visual(
        Box((L, wall, RIM_HEIGHT)),
        origin=Origin(xyz=(0.0, W / 2.0 - wall / 2.0, rim_z)),
        material=rim_mat,
        name="rim_right", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((L, wall, RIM_HEIGHT)),
        origin=Origin(xyz=(0.0, -W / 2.0 + wall / 2.0, rim_z)),
        material=rim_mat,
        name="rim_left", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((wall, W, RIM_HEIGHT)),
        origin=Origin(xyz=(L / 2.0 - wall / 2.0, 0.0, rim_z)),
        material=rim_mat,
        name="rim_front", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((wall, W, RIM_HEIGHT)),
        origin=Origin(xyz=(-L / 2.0 + wall / 2.0, 0.0, rim_z)),
        material=rim_mat,
        name="rim_rear", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )


def _build_corner_guards(body, resolved: ResolvedTackleBoxConfig, *, hardware_mat) -> None:
    if resolved.corner_guard == "none":
        return
    L = resolved.length
    W = resolved.width
    H = resolved.body_height
    thickness = 0.006 if resolved.corner_guard == "small" else 0.010
    guard_h = 0.030 if resolved.corner_guard == "small" else 0.046
    cx = L / 2.0 - thickness / 2.0 - 0.0005
    cy = W / 2.0 - thickness / 2.0 - 0.0005
    for ix, sign_x in enumerate((-1.0, 1.0)):
        for iy, sign_y in enumerate((-1.0, 1.0)):
            body.visual(
                Box((thickness, 0.030, guard_h)),
                origin=Origin(xyz=(sign_x * cx, sign_y * (W / 2.0 - 0.018), guard_h / 2.0)),
                material=hardware_mat,
                name=f"corner_guard_x_{ix}_{iy}", material_class_id=("metal.stainless_matte" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
            )
            body.visual(
                Box((0.030, thickness, guard_h)),
                origin=Origin(xyz=(sign_x * (L / 2.0 - 0.018), sign_y * cy, guard_h / 2.0)),
                material=hardware_mat,
                name=f"corner_guard_y_{ix}_{iy}", material_class_id=("metal.stainless_matte" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
            )
            # top corner cap that wraps over the rim
            body.visual(
                Box((0.026, 0.026, 0.006)),
                origin=Origin(
                    xyz=(
                        sign_x * (L / 2.0 - 0.013),
                        sign_y * (W / 2.0 - 0.013),
                        H + RIM_HEIGHT + 0.003,
                    )
                ),
                material=hardware_mat,
                name=f"corner_guard_cap_{ix}_{iy}", material_class_id=("metal.stainless_matte" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
            )


def _build_feet(body, resolved: ResolvedTackleBoxConfig, *, hardware_mat) -> None:
    if resolved.feet_count == 0:
        return
    for idx, (x, y) in enumerate(_foot_xy_positions(resolved.length, resolved.width)):
        body.visual(
            Cylinder(radius=0.011, length=FOOT_HEIGHT),
            origin=Origin(xyz=(x, y, -FOOT_HEIGHT / 2.0)),
            material=hardware_mat,
            name=f"foot_{idx}", material_class_id="rubber.smooth_plain",
        )


def _build_trays(body, resolved: ResolvedTackleBoxConfig, *, tray_mat) -> None:
    if resolved.tray_count == 0:
        return
    L = resolved.length
    W = resolved.width
    H = resolved.body_height
    wall = resolved.wall_thickness

    inner_L = L - 2.0 * wall - 0.020
    # The tray bears on the two inner side walls. Leaving a decorative gap
    # made the complete tray assembly a disconnected island in the body part.
    inner_W = W - 2.0 * wall
    # The lowest tray sits about 55% of the body height, the second tray at 80% if present.
    tray_levels = [0.55 * H] if resolved.tray_count == 1 else [0.45 * H, 0.78 * H]

    total_compartments = resolved.compartment_count
    # Distribute compartments across trays as evenly as possible.
    per_tray_counts: list[int] = []
    if resolved.tray_count > 0 and total_compartments > 0:
        base = total_compartments // resolved.tray_count
        rem = total_compartments % resolved.tray_count
        for i in range(resolved.tray_count):
            per_tray_counts.append(base + (1 if i < rem else 0))
    else:
        per_tray_counts = [0] * resolved.tray_count

    for t_idx, z in enumerate(tray_levels):
        body.visual(
            Box((inner_L, inner_W, TRAY_THICKNESS)),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=tray_mat,
            name=f"tray_{t_idx}_floor", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        # Tray side rails (visual only) keep it reading as a tray rather than a slab.
        body.visual(
            Box((inner_L, 0.008, TRAY_RIM_HEIGHT)),
            origin=Origin(xyz=(0.0, inner_W / 2.0 - 0.004, z + TRAY_RIM_HEIGHT / 2.0)),
            material=tray_mat,
            name=f"tray_{t_idx}_rail_right", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        body.visual(
            Box((inner_L, 0.008, TRAY_RIM_HEIGHT)),
            origin=Origin(xyz=(0.0, -inner_W / 2.0 + 0.004, z + TRAY_RIM_HEIGHT / 2.0)),
            material=tray_mat,
            name=f"tray_{t_idx}_rail_left", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        body.visual(
            Box((0.008, inner_W, TRAY_RIM_HEIGHT)),
            origin=Origin(xyz=(inner_L / 2.0 - 0.004, 0.0, z + TRAY_RIM_HEIGHT / 2.0)),
            material=tray_mat,
            name=f"tray_{t_idx}_rail_front", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        body.visual(
            Box((0.008, inner_W, TRAY_RIM_HEIGHT)),
            origin=Origin(xyz=(-inner_L / 2.0 + 0.004, 0.0, z + TRAY_RIM_HEIGHT / 2.0)),
            material=tray_mat,
            name=f"tray_{t_idx}_rail_rear", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )

        # Compartment dividers: alternate longitudinal and transverse to span
        # the requested count, all derived from inner_L / inner_W.
        count = per_tray_counts[t_idx] if t_idx < len(per_tray_counts) else 0
        if count > 1:
            # Use count-1 dividers laid along Y to make 'count' bays in X.
            divider_count = count - 1
            for d in range(divider_count):
                x = -inner_L / 2.0 + (inner_L * (d + 1)) / count
                body.visual(
                    Box((0.006, inner_W - 0.010, 0.026)),
                    origin=Origin(xyz=(x, 0.0, z + TRAY_THICKNESS / 2.0 + 0.013)),
                    material=tray_mat,
                    name=f"tray_{t_idx}_divider_{d}", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
                )
            # Add a single transverse divider for trays with ≥6 compartments
            # to create a 2-row layout while still respecting the requested count.
            if count >= 6:
                body.visual(
                    Box((inner_L - 0.012, 0.006, 0.024)),
                    origin=Origin(xyz=(0.0, 0.0, z + TRAY_THICKNESS / 2.0 + 0.012)),
                    material=tray_mat,
                    name=f"tray_{t_idx}_cross_divider", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
                )


def _build_hinge_hardware(
    body,
    resolved: ResolvedTackleBoxConfig,
    *,
    hardware_mat,
    hinge_x: float,
    hinge_z: float,
) -> None:
    W = resolved.width
    # Two body-side hinge leaves attached to the rear face.
    leaf_thickness = 0.005
    for idx, y in enumerate((-W * 0.30, W * 0.30)):
        body.visual(
            Box((leaf_thickness, 0.060, 0.022)),
            origin=Origin(xyz=(hinge_x + HINGE_KNUCKLE_RADIUS + leaf_thickness / 2.0, y, hinge_z)),
            material=hardware_mat,
            name=f"body_hinge_leaf_{idx}", material_class_id="metal.stainless_matte",
        )
        body.visual(
            Cylinder(radius=HINGE_KNUCKLE_RADIUS, length=0.046),
            origin=Origin(
                xyz=(hinge_x, y, hinge_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=hardware_mat,
            name=f"body_hinge_knuckle_{idx}", material_class_id="metal.stainless_matte",
        )


def _build_latch_keepers(
    body,
    resolved: ResolvedTackleBoxConfig,
    *,
    hardware_mat,
    keeper_z: float,
) -> None:
    if resolved.latch_count == 0:
        return
    L = resolved.length
    # A projecting pad bolted to the outer front face, with a horizontal pin at
    # its tip.  The hook closes behind the pin with a small real clearance;
    # interpenetrating the pin made every latched seed fail motion QC.
    for i, y in enumerate(_latch_y_positions(resolved.latch_count, resolved.width)):
        body.visual(
            Box((0.028, 0.030, 0.022)),
            origin=Origin(xyz=(L / 2.0 + 0.014, y, keeper_z)),
            material=hardware_mat,
            name=f"keeper_block_{i}", material_class_id="metal.stainless_matte",
        )
        body.visual(
            Cylinder(radius=0.0033, length=0.040),
            origin=Origin(
                xyz=(L / 2.0 + 0.027, y, keeper_z + 0.014),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=hardware_mat,
            name=f"keeper_pin_{i}", material_class_id="metal.stainless_matte",
        )


def _build_top_bar_handle(
    lid, resolved: ResolvedTackleBoxConfig, *, hardware_mat, handle_mat
) -> None:
    L = resolved.length
    W = resolved.width
    # A fixed top-bar carry handle bolted to the lid top, so it rises with the
    # lid when the lid opens. Each side is a single solid foot block (no thin
    # bracket+post sandwich) that embeds slightly into the lid panel for a clean
    # join with no z-fighting.
    # Lid origin is at the rear hinge; the lid panel extends from x=0 to x=L
    # in lid local frame, with its top face at z = LID_THICKNESS.
    mount_x = LID_PANEL_REAR_X + L * 0.50
    foot_embed = 0.004  # how far the foot sinks into the lid panel
    foot_above = 0.034  # how far the foot rises above the lid panel
    foot_height = foot_embed + foot_above
    foot_z_center = LID_THICKNESS - foot_embed + foot_height / 2.0
    foot_top_z = LID_THICKNESS + foot_above
    bar_thickness = 0.014
    bar_z = foot_top_z + bar_thickness / 2.0
    bar_length = W * 0.66
    for idx, y_frac in enumerate((-0.36, 0.36)):
        y = y_frac * W
        lid.visual(
            Box((0.024, 0.026, foot_height)),
            origin=Origin(xyz=(mount_x, y, foot_z_center)),
            material=hardware_mat,
            name=f"handle_foot_{idx}", material_class_id="metal.stainless_matte",
        )
    lid.visual(
        Box((0.030, bar_length, bar_thickness)),
        origin=Origin(xyz=(mount_x, 0.0, bar_z)),
        material=handle_mat,
        name="top_bar_handle", material_class_id="plastic.opaque_glossy_molded",
    )
    # Decorative grip ribbing in the middle of the bar.
    for idx, ry in enumerate((-0.04, 0.0, 0.04)):
        lid.visual(
            Box((0.030, 0.006, 0.008)),
            origin=Origin(xyz=(mount_x, ry, bar_z + bar_thickness / 2.0 + 0.004)),
            material=handle_mat,
            name=f"top_bar_grip_rib_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_molded_handle_on_lid(lid, resolved: ResolvedTackleBoxConfig, *, handle_mat) -> None:
    L = resolved.length
    # Recessed molded grip on the lid top.
    z = LID_THICKNESS + 0.004
    lid.visual(
        Box((0.140, 0.040, 0.010)),
        origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.18, 0.0, z)),
        material=handle_mat,
        name="molded_grip_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    lid.visual(
        Box((0.110, 0.012, 0.006)),
        origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.18, 0.0, z + 0.008)),
        material=handle_mat,
        name="molded_grip_pull", material_class_id="plastic.opaque_glossy_molded",
    )
    _ = resolved


# ---------------------------------------------------------------------------
# Lid construction
# ---------------------------------------------------------------------------


def _build_lid_shell(lid, resolved: ResolvedTackleBoxConfig, *, lid_mat) -> None:
    L = resolved.length
    W = resolved.width
    # The lid origin is the rear hinge axis.  The panel starts beyond the
    # knuckle radius and still spans the full body length.
    panel = Box((L, W, LID_THICKNESS))
    lid.visual(
        panel,
        origin=Origin(xyz=(LID_PANEL_REAR_X + L / 2.0, 0.0, LID_THICKNESS / 2.0)),
        material=lid_mat,
        name="lid_panel", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
    )

    style = resolved.lid_style
    if style == "raised":
        lid.visual(
            Box((L * 0.78, W * 0.76, 0.012)),
            origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.50, 0.0, LID_THICKNESS + 0.006)),
            material=lid_mat,
            name="lid_raised_panel", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
    elif style == "ribbed":
        # Three longitudinal stiffening ribs.
        for idx, y_frac in enumerate((-0.30, 0.0, 0.30)):
            lid.visual(
                Box((L * 0.78, 0.012, 0.006)),
                origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.50, y_frac * W, LID_THICKNESS + 0.003)),
                material=lid_mat,
                name=f"lid_rib_{idx}", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
            )
    elif style == "recessed":
        # Recessed center: emulate the recess with a slightly thinner overlay frame.
        lid.visual(
            Box((L * 0.86, 0.014, 0.006)),
            origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.50, W * 0.36, LID_THICKNESS + 0.003)),
            material=lid_mat,
            name="lid_recess_frame_top", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        lid.visual(
            Box((L * 0.86, 0.014, 0.006)),
            origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.50, -W * 0.36, LID_THICKNESS + 0.003)),
            material=lid_mat,
            name="lid_recess_frame_bottom", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        lid.visual(
            Box((0.014, W * 0.70, 0.006)),
            origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.08, 0.0, LID_THICKNESS + 0.003)),
            material=lid_mat,
            name="lid_recess_frame_rear", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )
        lid.visual(
            Box((0.014, W * 0.70, 0.006)),
            origin=Origin(xyz=(LID_PANEL_REAR_X + L * 0.92, 0.0, LID_THICKNESS + 0.003)),
            material=lid_mat,
            name="lid_recess_frame_front", material_class_id=("metal.aluminum_bare" if resolved.material_style == "metal" else "plastic.opaque_glossy_molded"),
        )


def _build_lid_hinge_hardware(lid, resolved: ResolvedTackleBoxConfig, *, hardware_mat) -> None:
    W = resolved.width
    lid.visual(
        Cylinder(radius=HINGE_KNUCKLE_RADIUS, length=W * 0.50),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hardware_mat,
        name="lid_hinge_knuckle", material_class_id="metal.stainless_matte",
    )
    lid.visual(
        Box((0.026, W * 0.56, 0.004)),
        origin=Origin(xyz=(0.013, 0.0, 0.001)),
        material=hardware_mat,
        name="lid_hinge_leaf", material_class_id="metal.stainless_matte",
    )


def _build_latch_mounts_on_lid(
    lid,
    resolved: ResolvedTackleBoxConfig,
    *,
    hardware_mat,
) -> None:
    if resolved.latch_count == 0:
        return
    L = resolved.length
    # Two narrow side arms extend past the lid's front edge to carry the latch
    # pivot. Keeping the center open gives the moving plate a real sweep path.
    pivot_x = LID_PANEL_REAR_X + L + LATCH_PIVOT_X_PAST_LID_FRONT
    pivot_z = LID_THICKNESS + LATCH_PIVOT_Z_ABOVE_LID_TOP
    for i, y in enumerate(_latch_y_positions(resolved.latch_count, resolved.width)):
        # Two knuckle ears, one on each side of the pivot axis.
        for side_idx, y_off in enumerate((-0.028, 0.028)):
            lid.visual(
                Box((0.020, 0.006, 0.010)),
                origin=Origin(xyz=(pivot_x - 0.010, y + y_off, pivot_z)),
                material=hardware_mat,
                name=f"latch_mount_arm_{i}_{side_idx}", material_class_id="metal.stainless_matte",
            )
            lid.visual(
                Cylinder(radius=0.0050, length=0.006),
                origin=Origin(
                    xyz=(pivot_x, y + y_off, pivot_z),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=hardware_mat,
                name=f"latch_knuckle_{i}_{side_idx}", material_class_id="metal.stainless_matte",
            )


# ---------------------------------------------------------------------------
# Latch parts
# ---------------------------------------------------------------------------


def _build_latch_visuals(latch, *, style: LatchStyle, hardware_mat, handle_mat) -> None:
    # Latch local frame: pivot is at origin, latch dangles down toward -Z (closed pose).
    latch.visual(
        Cylinder(radius=0.0040, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hardware_mat,
        name="latch_pivot_pin", material_class_id="metal.stainless_matte",
    )
    if style == "flip_tab":
        latch.visual(
            Box((0.006, 0.034, 0.040)),
            origin=Origin(xyz=(0.004, 0.0, -0.020)),
            material=hardware_mat,
            name="latch_plate", material_class_id="metal.stainless_matte",
        )
        # Hook flange extends BACKWARD (-X) past the keeper pin so the latch
        # actually locks the pin against the plate in the closed pose.
        latch.visual(
            Box((0.018, 0.034, 0.006)),
            origin=Origin(xyz=(-0.001, 0.0, -0.042)),
            material=hardware_mat,
            name="latch_hook", material_class_id="metal.stainless_matte",
        )
        latch.visual(
            Box((0.012, 0.030, 0.008)),
            origin=Origin(xyz=(0.011, 0.0, -0.030)),
            material=handle_mat,
            name="latch_pull", material_class_id="plastic.opaque_glossy_molded",
        )
    elif style == "clamp":
        latch.visual(
            Box((0.008, 0.044, 0.054)),
            origin=Origin(xyz=(0.006, 0.0, -0.028)),
            material=hardware_mat,
            name="latch_plate", material_class_id="metal.stainless_matte",
        )
        latch.visual(
            Box((0.022, 0.044, 0.006)),
            origin=Origin(xyz=(0.000, 0.0, -0.058)),
            material=hardware_mat,
            name="latch_hook", material_class_id="metal.stainless_matte",
        )
        latch.visual(
            Box((0.014, 0.044, 0.012)),
            origin=Origin(xyz=(0.013, 0.0, -0.036)),
            material=handle_mat,
            name="latch_pull", material_class_id="plastic.opaque_glossy_molded",
        )
        latch.visual(
            Cylinder(radius=0.0026, length=0.046),
            origin=Origin(
                xyz=(0.012, 0.0, -0.020),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=hardware_mat,
            name="latch_clamp_cam", material_class_id="metal.stainless_matte",
        )
    else:  # hook
        latch.visual(
            Box((0.006, 0.026, 0.052)),
            origin=Origin(xyz=(0.004, 0.0, -0.024)),
            material=hardware_mat,
            name="latch_plate", material_class_id="metal.stainless_matte",
        )
        latch.visual(
            Box((0.020, 0.020, 0.006)),
            origin=Origin(xyz=(-0.001, 0.0, -0.053)),
            material=hardware_mat,
            name="latch_hook", material_class_id="metal.stainless_matte",
        )


# ---------------------------------------------------------------------------
# Carry handle (folding)
# ---------------------------------------------------------------------------


def _build_folding_handle_visuals(handle, *, width: float, hardware_mat, handle_mat) -> None:
    # Local frame: pivot is at origin, handle in stowed pose sticks +X along the lid top.
    # When the joint rotates around Y, the handle swings up.
    arm_length = 0.090
    handle.visual(
        Cylinder(radius=0.0050, length=width * 0.60 + 0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=hardware_mat,
        name="handle_pivot_pin", material_class_id="metal.stainless_matte",
    )
    handle.visual(
        Box((arm_length, 0.014, 0.008)),
        origin=Origin(xyz=(arm_length / 2.0, -width * 0.30, 0.0)),
        material=hardware_mat,
        name="handle_arm_left", material_class_id="metal.stainless_matte",
    )
    handle.visual(
        Box((arm_length, 0.014, 0.008)),
        origin=Origin(xyz=(arm_length / 2.0, width * 0.30, 0.0)),
        material=hardware_mat,
        name="handle_arm_right", material_class_id="metal.stainless_matte",
    )
    handle.visual(
        Box((0.020, width * 0.60 + 0.014, 0.018)),
        origin=Origin(xyz=(arm_length, 0.0, 0.0)),
        material=handle_mat,
        name="handle_grip_bar", material_class_id="plastic.opaque_glossy_molded",
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_tackle_box(
    config: TackleBoxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or TackleBoxConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-tackle-box-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)

    palette = MATERIAL_PALETTES[resolved.material_style]
    body_mat = model.material("tackle_body", rgba=palette["body"])
    rim_mat = model.material("tackle_rim", rgba=palette["rim"])
    lid_mat = model.material("tackle_lid", rgba=palette["lid"])
    tray_mat = model.material("tackle_tray", rgba=palette["tray"])
    hardware_mat = model.material("tackle_hardware", rgba=palette["hardware"])
    handle_mat = model.material("tackle_handle", rgba=palette["handle"])

    L = resolved.length
    H = resolved.body_height

    # Hinge axis lives just behind the rear wall of the body, slightly above the rim.
    hinge_x = -L / 2.0 - HINGE_KNUCKLE_RADIUS - 0.002
    hinge_z = H + RIM_HEIGHT + HINGE_KNUCKLE_RADIUS - 0.002

    body = model.part("body")
    _build_body_shell(body, resolved, body_mat=body_mat, rim_mat=rim_mat)
    _build_trays(body, resolved, tray_mat=tray_mat)
    _build_corner_guards(body, resolved, hardware_mat=hardware_mat)
    _build_feet(body, resolved, hardware_mat=hardware_mat)
    _build_hinge_hardware(
        body, resolved, hardware_mat=hardware_mat, hinge_x=hinge_x, hinge_z=hinge_z
    )
    keeper_z = H - LATCH_KEEPER_Z_BELOW_TOP[resolved.latch_style]
    _build_latch_keepers(body, resolved, hardware_mat=hardware_mat, keeper_z=keeper_z)

    lid = model.part("lid")
    _build_lid_shell(lid, resolved, lid_mat=lid_mat)
    _build_lid_hinge_hardware(lid, resolved, hardware_mat=hardware_mat)
    _build_latch_mounts_on_lid(lid, resolved, hardware_mat=hardware_mat)
    if resolved.handle_style == "molded":
        _build_molded_handle_on_lid(lid, resolved, handle_mat=handle_mat)
    if resolved.handle_style == "top_bar":
        _build_top_bar_handle(lid, resolved, hardware_mat=hardware_mat, handle_mat=handle_mat)

    model.articulation(
        "lid_joint",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=1.8),
    )

    # Latch parts and joints. The pivot sits just past the lid's front edge so
    # the latch can hang outside the body's front wall in the closed pose and
    # wrap its hook around the keeper pin.
    for i, y in enumerate(_latch_y_positions(resolved.latch_count, resolved.width)):
        latch = model.part(f"latch_{i}")
        _build_latch_visuals(
            latch,
            style=resolved.latch_style,
            hardware_mat=hardware_mat,
            handle_mat=handle_mat,
        )
        pivot_x = LID_PANEL_REAR_X + L + LATCH_PIVOT_X_PAST_LID_FRONT
        pivot_z = LID_THICKNESS + LATCH_PIVOT_Z_ABOVE_LID_TOP
        joint_type = (
            ArticulationType.FIXED if resolved.latch_style == "hook" else ArticulationType.REVOLUTE
        )
        kwargs: dict = {}
        if joint_type == ArticulationType.REVOLUTE:
            kwargs["motion_limits"] = MotionLimits(effort=2.5, velocity=3.0, lower=0.0, upper=1.30)
            kwargs["axis"] = (0.0, -1.0, 0.0)
        model.articulation(
            f"latch_joint_{i}",
            joint_type,
            parent=lid,
            child=latch,
            origin=Origin(xyz=(pivot_x, y, pivot_z)),
            **kwargs,
        )

    # Folding carry handle: revolute joint on the lid top.
    if resolved.handle_style == "folding":
        handle = model.part("carry_handle")
        _build_folding_handle_visuals(
            handle,
            width=resolved.width,
            hardware_mat=hardware_mat,
            handle_mat=handle_mat,
        )
        # Two lid-side bosses support the full-width pivot bar.  Their height
        # clears the selected lid profile while keeping the stowed arms 1 mm
        # above it, so the handle remains connected without cutting through a
        # raised/ribbed lid.
        profile_height = {
            "flat": 0.0,
            "raised": 0.012,
            "ribbed": 0.006,
            "recessed": 0.006,
        }[resolved.lid_style]
        pivot_x = LID_PANEL_REAR_X + L * 0.18
        boss_height = profile_height + 0.004
        boss_top_z = LID_THICKNESS + boss_height
        for idx, y_frac in enumerate((-0.30, 0.30)):
            lid.visual(
                Box((0.020, 0.018, boss_height)),
                origin=Origin(
                    xyz=(pivot_x, y_frac * resolved.width, LID_THICKNESS + boss_height / 2.0)
                ),
                material=hardware_mat,
                name=f"folding_handle_boss_{idx}", material_class_id="metal.stainless_matte",
            )
        pivot_z = boss_top_z + 0.005
        model.articulation(
            "handle_joint",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=handle,
            origin=Origin(xyz=(pivot_x, 0.0, pivot_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.5, lower=0.0, upper=1.6),
        )

    return model


def build_seeded_tackle_box(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_tackle_box(config_from_seed(seed), assets=assets)


def with_overrides(config: TackleBoxConfig, **kwargs: object) -> TackleBoxConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_tackle_box_tests(object_model: ArticulatedObject, config: TackleBoxConfig) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    lid = object_model.get_part("lid")
    lid_joint = object_model.get_articulation("lid_joint")

    # Required revolute lid joint.
    ctx.check(
        "lid_joint is revolute",
        lid_joint.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={lid_joint.articulation_type}",
    )
    # Lid hinge must sit on the rear edge of the body (negative X side).
    ctx.check(
        "hinge sits on rear side of body",
        lid_joint.origin.xyz[0] < -resolved.length * 0.40,
        details=f"hinge_x={lid_joint.origin.xyz[0]}, length={resolved.length}",
    )
    # Lid sweep range matches spec (60-120 deg ~ 1.0-2.1 rad).
    ctx.check(
        "lid sweep within spec range",
        lid_joint.motion_limits is not None
        and lid_joint.motion_limits.lower is not None
        and lid_joint.motion_limits.upper is not None
        and abs(lid_joint.motion_limits.lower) < 1e-6
        and 1.0 <= lid_joint.motion_limits.upper <= 2.2,
        details=f"limits={lid_joint.motion_limits}",
    )

    # Closed lid sits above body rim with a small controlled gap.
    ctx.expect_gap(
        lid,
        body,
        axis="z",
        positive_elem="lid_panel",
        negative_elem="rim_front",
        min_gap=0.0,
        max_gap=0.040,
        name="closed lid rests just above the body rim",
    )
    # Closed lid footprint registers over the body floor.
    ctx.expect_overlap(
        lid,
        body,
        axes="xy",
        elem_a="lid_panel",
        elem_b="body_floor",
        min_overlap=min(resolved.length, resolved.width) * 0.50,
        name="closed lid footprint covers the body opening",
    )

    # Tray containment: every tray floor must lie inside the body footprint and below the rim.
    for t_idx in range(resolved.tray_count):
        ctx.expect_within(
            body,
            body,
            axes="xy",
            inner_elem=f"tray_{t_idx}_floor",
            outer_elem="body_floor",
            margin=0.001,
            name=f"tray_{t_idx} floor is inside body footprint",
        )

    # Lid opens upward about the rear hinge.
    closed_aabb = ctx.part_element_world_aabb(lid, elem="lid_panel")
    with ctx.pose({lid_joint: 1.30}):
        open_aabb = ctx.part_element_world_aabb(lid, elem="lid_panel")
    ctx.check(
        "lid opens upward about rear hinge",
        closed_aabb is not None
        and open_aabb is not None
        and open_aabb[1][2] > closed_aabb[1][2] + 0.08,
        details=f"closed={closed_aabb}, open={open_aabb}",
    )

    # Latches: present count matches and each non-fixed latch is articulated correctly.
    latch_parts = [p for p in object_model.parts if p.name.startswith("latch_")]
    ctx.check(
        "latch part count matches configuration",
        len(latch_parts) == resolved.latch_count,
        details=f"expected={resolved.latch_count}, got={len(latch_parts)}",
    )
    for i in range(resolved.latch_count):
        joint = object_model.get_articulation(f"latch_joint_{i}")
        # Latch keeper must be on the front (positive X) edge of the body.
        keeper_aabb = ctx.part_element_world_aabb(body, elem=f"keeper_block_{i}")
        ctx.check(
            f"latch_{i} keeper is on front edge",
            keeper_aabb is not None and keeper_aabb[0][0] > resolved.length * 0.30,
            details=f"keeper_aabb={keeper_aabb}",
        )
        if resolved.latch_style == "hook":
            ctx.check(
                f"latch_{i} hook joint is fixed",
                joint.articulation_type == ArticulationType.FIXED,
                details=f"type={joint.articulation_type}",
            )
        else:
            ctx.check(
                f"latch_{i} joint is revolute",
                joint.articulation_type == ArticulationType.REVOLUTE,
                details=f"type={joint.articulation_type}",
            )

    # Folding handle articulation, if present, must rotate the grip up and away.
    if resolved.handle_style == "folding":
        handle_part = object_model.get_part("carry_handle")
        handle_joint = object_model.get_articulation("handle_joint")
        ctx.check(
            "folding handle is revolute",
            handle_joint.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={handle_joint.articulation_type}",
        )
        rest_pos = ctx.part_element_world_aabb(handle_part, elem="handle_grip_bar")
        with ctx.pose({handle_joint: 1.40}):
            raised_pos = ctx.part_element_world_aabb(handle_part, elem="handle_grip_bar")
        ctx.check(
            "folding handle lifts the grip bar",
            rest_pos is not None
            and raised_pos is not None
            and raised_pos[1][2] > rest_pos[1][2] + 0.03,
            details=f"rest={rest_pos}, raised={raised_pos}",
        )

    # If a top_bar handle is present, its bar must sit above the rim AND be
    # attached to the lid (so it rises with the lid when opened).
    if resolved.handle_style == "top_bar":
        bar_aabb = ctx.part_element_world_aabb(lid, elem="top_bar_handle")
        ctx.check(
            "top bar handle sits above the body rim",
            bar_aabb is not None and bar_aabb[0][2] > resolved.body_height + RIM_HEIGHT - 0.002,
            details=f"bar_aabb={bar_aabb}, body_top={resolved.body_height + RIM_HEIGHT}",
        )
        closed_bar = bar_aabb
        with ctx.pose({lid_joint: 1.30}):
            open_bar = ctx.part_element_world_aabb(lid, elem="top_bar_handle")
        ctx.check(
            "top bar handle lifts with the lid",
            closed_bar is not None and open_bar is not None and open_bar[0][2] > closed_bar[1][2],
            details=f"closed={closed_bar}, open={open_bar}",
        )

    # Hardware overlap allowances: hinge knuckles intentionally embed slightly.
    ctx.allow_overlap(
        body,
        lid,
        elem_a="body_hinge_knuckle_0",
        elem_b="lid_hinge_knuckle",
        reason="The body and lid hinge knuckles share the hinge axis.",
    )
    ctx.allow_overlap(
        body,
        lid,
        elem_a="body_hinge_knuckle_1",
        elem_b="lid_hinge_knuckle",
        reason="The body and lid hinge knuckles share the hinge axis.",
    )

    return ctx.report()
