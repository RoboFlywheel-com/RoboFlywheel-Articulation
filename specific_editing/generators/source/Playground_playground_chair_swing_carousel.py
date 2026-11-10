# SPDX-License-Identifier: Apache-2.0

"""Playground chair-swing carousel modular template.

Reviewed spec:
``articraft_template_authoring/specs_modular_v1/Playground_Playground_playground_chair_swing_carousel.md``.

Identity = a powered chair-swing carousel (wave-swinger, park scale). A grounded
``base_form`` carries a central column; the column top hosts a ``rotor`` that
spins about the vertical Z axis through ONE CONTINUOUS joint. The rotor emits N
equiangular ``arm_structure`` stations (radial spokes / spline lattice / single
cantilever / overhead chain-hung ring). Each station ends in a tangential
pivot, and one ``seat_type`` chair hangs from it on a REVOLUTE ``seat_swing_i``
joint that lets the chair swing outward/inward (+-swing_limit).

Slots (per reviewed spec):

* ``base_form`` — square_slab_base / splayed_leg_base / pedestal_column /
  tripod_stand (grounded root, normalised top HUB_Z).
* ``arm_structure`` — straight_radial_arm / spline_tube_lattice /
  cantilever_arm / overhead_chain_hung (rotor topology + seat pivot form).
* ``seat_type`` — flat_platform_seat / slatted_bucket_rail / deep_bucket_seat
  (the swinging chair part tree).

Multiplicity axis: ``seat_count`` N in [2, 8] (weighted, small-N frequent).
Per-seed ``palette_style`` (5 colorways) drives every visual material.

Module sources (spec Module Source Index): S_A (splayed/spline/slatted),
S_B (square/straight/platform), S_PED, S_TRI, S_CAN, S_CHN, S_BKT, S_N2, S_N6.

Following ``wood_swing`` / ``playground_swing``: the grounded base is the root,
the rotor parts directly to the base (single CONTINUOUS spin), and every seat
parts directly to the rotor (REVOLUTE swing on real arm-tip pivot hardware).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


BaseFormModule = Literal[
    "square_slab_base",
    "splayed_leg_base",
    "pedestal_column",
    "tripod_stand",
]
ArmStructureModule = Literal[
    "straight_radial_arm",
    "spline_tube_lattice",
    "cantilever_arm",
    "overhead_chain_hung",
]
SeatTypeModule = Literal[
    "flat_platform_seat",
    "slatted_bucket_rail",
    "deep_bucket_seat",
]
PaletteStyle = Literal[
    "rust_red_cream",
    "weathered_white_carnival",
    "galvanized_steel",
    "faded_teal_rust",
    "candy_repaint",
]

BASE_FORM_MODULES: tuple[BaseFormModule, ...] = (
    "square_slab_base",
    "splayed_leg_base",
    "pedestal_column",
    "tripod_stand",
)
ARM_STRUCTURE_MODULES: tuple[ArmStructureModule, ...] = (
    "straight_radial_arm",
    "spline_tube_lattice",
    "cantilever_arm",
    "overhead_chain_hung",
)
SEAT_TYPE_MODULES: tuple[SeatTypeModule, ...] = (
    "flat_platform_seat",
    "slatted_bucket_rail",
    "deep_bucket_seat",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "rust_red_cream",
    "weathered_white_carnival",
    "galvanized_steel",
    "faded_teal_rust",
    "candy_repaint",
)

# Weighted seat-count domain: small N frequent, large N rare.
_SEAT_COUNT_CHOICES: tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8)
_SEAT_COUNT_WEIGHTS: tuple[float, ...] = (0.10, 0.12, 0.30, 0.16, 0.16, 0.08, 0.08)


# Each palette names >=5 distinct material tokens fed to every .visual(...).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "rust_red_cream": {
        "column": (0.74, 0.24, 0.16, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0),
        "dark": (0.18, 0.16, 0.15, 1.0),
        "seat": (0.90, 0.84, 0.66, 1.0),
        "accent": (0.62, 0.20, 0.14, 1.0),
        "band": (0.40, 0.16, 0.11, 1.0),
    },
    "weathered_white_carnival": {
        "column": (0.90, 0.90, 0.88, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
        "dark": (0.20, 0.21, 0.23, 1.0),
        "seat": (0.10, 0.30, 0.66, 1.0),
        "accent": (0.94, 0.74, 0.10, 1.0),
        "band": (0.66, 0.20, 0.14, 1.0),
    },
    "galvanized_steel": {
        "column": (0.66, 0.68, 0.70, 1.0),
        "metal": (0.74, 0.76, 0.78, 1.0),
        "dark": (0.22, 0.23, 0.25, 1.0),
        "seat": (0.30, 0.33, 0.36, 1.0),
        "accent": (0.50, 0.62, 0.72, 1.0),
        "band": (0.40, 0.42, 0.45, 1.0),
    },
    "faded_teal_rust": {
        "column": (0.20, 0.46, 0.46, 1.0),
        "metal": (0.52, 0.56, 0.56, 1.0),
        "dark": (0.14, 0.18, 0.18, 1.0),
        "seat": (0.80, 0.74, 0.58, 1.0),
        "accent": (0.66, 0.34, 0.18, 1.0),
        "band": (0.14, 0.30, 0.30, 1.0),
    },
    "candy_repaint": {
        "column": (0.86, 0.24, 0.42, 1.0),
        "metal": (0.60, 0.62, 0.64, 1.0),
        "dark": (0.16, 0.15, 0.18, 1.0),
        "seat": (0.96, 0.80, 0.22, 1.0),
        "accent": (0.18, 0.52, 0.78, 1.0),
        "band": (0.40, 0.12, 0.24, 1.0),
    },
}


@dataclass(frozen=True)
class PlaygroundChairSwingCarouselConfig:
    base_form_module: BaseFormModule = "square_slab_base"
    arm_structure_module: ArmStructureModule = "straight_radial_arm"
    seat_type_module: SeatTypeModule = "flat_platform_seat"
    seat_count: int = 4
    palette_style: PaletteStyle = "rust_red_cream"
    seat_radius_scale: float = 1.0
    column_height_scale: float = 1.0
    arm_thickness_scale: float = 1.0
    swing_limit_rad: float = 0.524
    name: str = "playground_chair_swing_carousel"
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["rust_red_cream"])
    )


@dataclass(frozen=True)
class ResolvedConfig:
    base_form_module: BaseFormModule
    arm_structure_module: ArmStructureModule
    seat_type_module: SeatTypeModule
    seat_count: int
    palette_style: PaletteStyle
    seat_radius_scale: float
    # Derived geometry.
    hub_z: float  # world z of the rotor spin bearing / hub top
    seat_radius: float  # plan radius of the seat-pivot ring
    pivot_drop: float  # how far below the rotor deck the pivot sits
    pivot_z: float  # world z of the seat-pivot line (non-chain)
    ring_z: float  # world z of the overhead chain ring vertex
    arm_radius: float  # tube radius for arms/struts
    swing_limit: float
    column_scale: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


# ---------------------------------------------------------------------------
# Procedural sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> PlaygroundChairSwingCarouselConfig:
    """Deterministic procedural sampling for every seed (seed 0 not special)."""
    rng = random.Random(seed * 2654435761 + 40503)

    base_form = rng.choice(BASE_FORM_MODULES)
    arm_structure = rng.choice(ARM_STRUCTURE_MODULES)
    seat_type = rng.choice(SEAT_TYPE_MODULES)
    palette = rng.choice(PALETTE_STYLES)

    seat_count = rng.choices(_SEAT_COUNT_CHOICES, weights=_SEAT_COUNT_WEIGHTS, k=1)[0]

    seat_radius_scale = round(rng.uniform(0.85, 1.20), 4)
    column_height_scale = round(rng.uniform(0.90, 1.20), 4)
    arm_thickness_scale = round(rng.uniform(0.80, 1.30), 4)
    swing_limit = round(rng.uniform(0.42, 0.62), 4)

    return PlaygroundChairSwingCarouselConfig(
        base_form_module=base_form,
        arm_structure_module=arm_structure,
        seat_type_module=seat_type,
        seat_count=seat_count,
        palette_style=palette,
        seat_radius_scale=seat_radius_scale,
        column_height_scale=column_height_scale,
        arm_thickness_scale=arm_thickness_scale,
        swing_limit_rad=swing_limit,
        name=f"seeded_playground_chair_swing_carousel_{seed}",
        palette=dict(PALETTES[palette]),
    )


def resolve_config(config: PlaygroundChairSwingCarouselConfig) -> ResolvedConfig:
    if config.base_form_module not in BASE_FORM_MODULES:
        raise ValueError(f"Unknown base_form_module {config.base_form_module!r}")
    if config.arm_structure_module not in ARM_STRUCTURE_MODULES:
        raise ValueError(f"Unknown arm_structure_module {config.arm_structure_module!r}")
    if config.seat_type_module not in SEAT_TYPE_MODULES:
        raise ValueError(f"Unknown seat_type_module {config.seat_type_module!r}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unknown palette_style {config.palette_style!r}")

    seat_count = int(_clamp(config.seat_count, 2, 8))

    col_scale = _clamp(config.column_height_scale, 0.90, 1.20)
    rad_scale = _clamp(config.seat_radius_scale, 0.85, 1.20)
    arm_scale = _clamp(config.arm_thickness_scale, 0.80, 1.30)

    # Normalised hub height across all base families (column_height_scale driven).
    hub_z = 1.30 * col_scale

    # Seat-pivot ring radius. Enforce tangential non-self-collision: adjacent
    # stations are 2*pi/N apart, chord = 2 R sin(pi/N) must clear the seat width.
    base_radius = 1.40 * rad_scale
    seat_tangential_width = 0.52  # generous seat half-extent in tangential dir
    min_chord = seat_tangential_width + 0.10
    # Required radius so the chord at this N clears the seat width.
    needed_radius = min_chord / (2.0 * math.sin(math.pi / seat_count))
    seat_radius = max(base_radius, needed_radius)
    seat_radius = _clamp(seat_radius, 0.95, 2.6)

    pivot_drop = 0.10 * col_scale
    pivot_z = hub_z - pivot_drop
    ring_z = hub_z + 0.45 * col_scale

    arm_radius = 0.045 * arm_scale

    return ResolvedConfig(
        base_form_module=config.base_form_module,
        arm_structure_module=config.arm_structure_module,
        seat_type_module=config.seat_type_module,
        seat_count=seat_count,
        palette_style=config.palette_style,
        seat_radius_scale=rad_scale,
        hub_z=hub_z,
        seat_radius=seat_radius,
        pivot_drop=pivot_drop,
        pivot_z=pivot_z,
        ring_z=ring_z,
        arm_radius=arm_radius,
        swing_limit=_clamp(config.swing_limit_rad, 0.40, 0.65),
        column_scale=col_scale,
        name=config.name,
        palette=dict(config.palette) if config.palette else dict(PALETTES[config.palette_style]),
    )


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _mat(model: ArticulatedObject, key: str, rgba: tuple[float, float, float, float]):
    return model.material(key, rgba=rgba)


def _segment_pose(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
) -> tuple[Origin, float]:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return Origin(xyz=start), 0.0
    yaw = math.atan2(dy, dx)
    pitch = math.acos(max(-1.0, min(1.0, dz / length)))
    return (
        Origin(
            xyz=((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, (start[2] + end[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        length,
    )


def _add_tube(part, name: str, start, end, radius: float, material) -> None:
    origin, length = _segment_pose(start, end)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=origin,
        material=material,
        name=name,
        material_class_id="metal.paint_coated",
    )


def _seat_angles(n: int) -> list[float]:
    return [2.0 * math.pi * i / n for i in range(n)]


# ---------------------------------------------------------------------------
# Slot A — base_form (grounded root, normalised top spin bearing at hub_z)
# ---------------------------------------------------------------------------
def _build_base_form(model: ArticulatedObject, r: ResolvedConfig) -> None:
    column = _mat(model, "base_column", r.palette["column"])
    metal = _mat(model, "base_metal", r.palette["metal"])
    dark = _mat(model, "base_dark", r.palette["dark"])
    band = _mat(model, "base_band", r.palette["band"])

    base = model.part("support_column")
    base.inertial = Inertial.from_geometry(
        Box((1.2, 1.2, r.hub_z + 0.1)),
        mass=180.0,
        origin=Origin(xyz=(0.0, 0.0, (r.hub_z + 0.1) * 0.5)),
    )

    module = r.base_form_module
    shaft_r = 0.10
    # Column shaft runs all the way up THROUGH the hub interface so the rotor
    # hub sleeve is captured on a real shaft (volumetric overlap, not tangent).
    shaft_top = r.hub_z + 0.08
    base.visual(
        Cylinder(radius=shaft_r, length=shaft_top),
        origin=Origin(xyz=(0.0, 0.0, shaft_top * 0.5)),
        material=column,
        name="column_shaft",
        material_class_id=(
            "rust.painted_weathered"
            if r.palette_style in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
            else "metal.steel_galvanized"
        ),
    )
    # Two rust/colour bands on the shaft (parent visual decoration).
    for k, zf in enumerate((0.32, 0.62)):
        base.visual(
            Cylinder(radius=shaft_r + 0.006, length=0.06),
            origin=Origin(xyz=(0.0, 0.0, r.hub_z * zf)),
            material=band,
            name=f"column_band_{k}",
            material_class_id=(
                "rust.painted_weathered"
                if r.palette_style
                in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                else "metal.paint_coated"
            ),
        )
    # Bearing collar just under the hub interface.
    base.visual(
        Cylinder(radius=shaft_r + 0.03, length=0.08),
        origin=Origin(xyz=(0.0, 0.0, r.hub_z - 0.06)),
        material=metal,
        name="bearing_collar",
        material_class_id=(
            "metal.steel_galvanized"
            if r.palette_style
            in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
            else "rust.oxidized_metal"
        ),
    )

    if module == "square_slab_base":
        base.visual(
            Box((0.66, 0.66, 0.06)),
            origin=Origin(xyz=(0.0, 0.0, 0.03)),
            material=dark,
            name="base_plate",
            material_class_id="metal.blackened_gunmetal",
        )
        for sx in (-0.27, 0.27):
            for sy in (-0.27, 0.27):
                base.visual(
                    Cylinder(radius=0.02, length=0.07),
                    origin=Origin(xyz=(sx, sy, 0.05)),
                    material=metal,
                    name=f"anchor_bolt_{sx:+.2f}_{sy:+.2f}",
                    material_class_id=(
                        "metal.steel_galvanized"
                        if r.palette_style
                        in {
                            "rust_red_cream",
                            "galvanized_steel",
                            "faded_teal_rust",
                            "candy_repaint",
                        }
                        else "rust.oxidized_metal"
                    ),
                )
        base.visual(
            Cylinder(radius=shaft_r + 0.05, length=0.05),
            origin=Origin(xyz=(0.0, 0.0, 0.085)),
            material=metal,
            name="column_base_collar",
            material_class_id=(
                "metal.steel_galvanized"
                if r.palette_style
                in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                else "rust.oxidized_metal"
            ),
        )
    elif module == "splayed_leg_base":
        base.visual(
            Cylinder(radius=0.34, length=0.05),
            origin=Origin(xyz=(0.0, 0.0, 0.025)),
            material=dark,
            name="base_plate",
            material_class_id="metal.blackened_gunmetal",
        )
        # Four splayed short legs derived from the column down to a wide foot ring.
        for i in range(4):
            ang = math.pi / 4.0 + i * math.pi / 2.0
            fx, fy = 0.34 * math.cos(ang), 0.34 * math.sin(ang)
            _add_tube(
                base,
                f"splay_leg_{i}",
                (0.0, 0.0, 0.18),
                (fx, fy, 0.05),
                0.028,
                column,
            )
            base.visual(
                Box((0.10, 0.10, 0.04)),
                origin=Origin(xyz=(fx, fy, 0.03)),
                material=metal,
                name=f"foot_pad_{i}",
                material_class_id=(
                    "metal.steel_galvanized"
                    if r.palette_style
                    in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                    else "rust.oxidized_metal"
                ),
            )
        # Exposed spindle + nut above the bearing collar.
        base.visual(
            Cylinder(radius=0.018, length=0.10),
            origin=Origin(xyz=(0.0, 0.0, r.hub_z + 0.01)),
            material=metal,
            name="spindle",
            material_class_id=(
                "metal.steel_galvanized"
                if r.palette_style
                in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                else "rust.oxidized_metal"
            ),
        )
    elif module == "pedestal_column":
        # LatheGeometry wide disc foot bell-flaring up into the shaft.
        profile = [
            (0.0, 0.0),
            (0.40, 0.0),
            (0.40, 0.05),
            (0.20, 0.10),
            (shaft_r + 0.04, 0.22),
            (shaft_r + 0.02, 0.34),
            (0.0, 0.34),
        ]
        base.visual(
            mesh_from_geometry(LatheGeometry(profile, segments=40), "pedestal_foot_mesh"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=column,
            name="pedestal_foot",
            material_class_id=(
                "rust.painted_weathered"
                if r.palette_style
                in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                else "metal.steel_galvanized"
            ),
        )
    else:  # tripod_stand
        hub_z0 = 0.18
        base.visual(
            Cylinder(radius=0.12, length=0.10),
            origin=Origin(xyz=(0.0, 0.0, hub_z0)),
            material=dark,
            name="tripod_hub",
            material_class_id="metal.blackened_gunmetal",
        )
        for i in range(3):
            ang = i * 2.0 * math.pi / 3.0
            fx, fy = 0.40 * math.cos(ang), 0.40 * math.sin(ang)
            _add_tube(base, f"leg_{i}", (0.0, 0.0, hub_z0), (fx, fy, 0.05), 0.032, column)
            base.visual(
                Box((0.12, 0.12, 0.04)),
                origin=Origin(xyz=(fx, fy, 0.03)),
                material=metal,
                name=f"ground_pad_{i}",
                material_class_id=(
                    "metal.steel_galvanized"
                    if r.palette_style
                    in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                    else "rust.oxidized_metal"
                ),
            )
            base.visual(
                Cylinder(radius=0.018, length=0.06),
                origin=Origin(xyz=(fx, fy, 0.05)),
                material=dark,
                name=f"pad_bolt_{i}",
                material_class_id="metal.blackened_gunmetal",
            )


# ---------------------------------------------------------------------------
# Slot B — rotor + arm_structure (single CONTINUOUS spin about Z)
# ---------------------------------------------------------------------------
def _tapered_cantilever_arm_mesh(hub_r: float, tip_r: float, length: float, name: str):
    """CadQuery loft frustum: a single tapered cantilever arm along +X."""
    arm = cq.Workplane("YZ").circle(hub_r).workplane(offset=length).circle(tip_r).loft(combine=True)
    return mesh_from_cadquery(arm, name)


def _build_rotor(model: ArticulatedObject, r: ResolvedConfig) -> None:
    metal = _mat(model, "rotor_metal", r.palette["metal"])
    dark = _mat(model, "rotor_dark", r.palette["dark"])
    accent = _mat(model, "rotor_accent", r.palette["accent"])
    column = _mat(model, "rotor_column", r.palette["column"])

    rotor = model.part("rotor")
    # The rotor part frame origin sits at the column top (world z = hub_z), set
    # by the rotor_spin joint origin. All rotor geometry below is authored in
    # this LOCAL frame: deck at local z=0, pivots at local -pivot_drop, ring at
    # local +ring_local.
    rotor.inertial = Inertial.from_geometry(
        Cylinder(radius=r.seat_radius, length=0.2),
        mass=40.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    # Central deck plate ties the hub sleeve, cap and every arm base into one
    # connected island (all of them overlap this disc at the deck plane z=0).
    rotor.visual(
        Cylinder(radius=0.20, length=0.05),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=metal,
        name="hub_deck",
        material_class_id=(
            "metal.steel_galvanized"
            if r.palette_style
            in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
            else "rust.oxidized_metal"
        ),
    )
    # Hub sleeve straddles the column top (captured-shaft) + cap.
    rotor.visual(
        Cylinder(radius=0.13, length=0.18),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=metal,
        name="hub_sleeve",
        material_class_id=(
            "metal.steel_galvanized"
            if r.palette_style
            in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
            else "rust.oxidized_metal"
        ),
    )
    rotor.visual(
        Cylinder(radius=0.15, length=0.04),
        origin=Origin(xyz=(0.0, 0.0, 0.10)),
        material=dark,
        name="hub_cap",
        material_class_id="metal.blackened_gunmetal",
    )

    angles = _seat_angles(r.seat_count)
    module = r.arm_structure_module
    R = r.seat_radius
    deck_z = 0.0
    pivot_z = -r.pivot_drop
    ring_local = 0.45 * r.column_scale

    if module == "straight_radial_arm":
        for i, th in enumerate(angles):
            tx, ty = R * math.cos(th), R * math.sin(th)
            _add_tube(
                rotor,
                f"arm_{i}",
                (0.13 * math.cos(th), 0.13 * math.sin(th), deck_z),
                (tx, ty, deck_z),
                r.arm_radius,
                metal,
            )
            # Clevis yoke + two lugs straddling the tangential pivot pin.
            ttx, tty = -math.sin(th), math.cos(th)  # tangent direction
            rotor.visual(
                Cylinder(radius=0.05, length=0.05),
                origin=Origin(xyz=(tx, ty, deck_z)),
                material=dark,
                name=f"tip_yoke_{i}",
                material_class_id="metal.blackened_gunmetal",
            )
            lug_h = (deck_z - pivot_z) + 0.06
            for s, sgn in (("a", 1.0), ("b", -1.0)):
                lx = tx + ttx * sgn * 0.06
                ly = ty + tty * sgn * 0.06
                rotor.visual(
                    Box((0.05, 0.05, lug_h)),
                    origin=Origin(xyz=(lx, ly, deck_z - lug_h * 0.5 + 0.03)),
                    material=dark,
                    name=f"tip_lug_{i}_{s}",
                    material_class_id="metal.blackened_gunmetal",
                )
            _add_pivot_pin(rotor, f"pivot_pin_{i}", tx, ty, pivot_z, th, metal)
        # X-truss braces between adjacent arms (tangent-offset for large N).
        brace_off = 0.06 + 0.30 * (1.0 - min(1.0, 4.0 / r.seat_count))
        for i in range(r.seat_count):
            th0 = angles[i]
            th1 = angles[(i + 1) % r.seat_count]
            mid_r = R * 0.62
            a0 = (mid_r * math.cos(th0), mid_r * math.sin(th0), deck_z - 0.02)
            a1 = (mid_r * math.cos(th1), mid_r * math.sin(th1), deck_z - 0.02)
            _add_tube(rotor, f"brace_{2 * i}", a0, a1, r.arm_radius * 0.55, accent)
            inner_r = R * 0.30 + brace_off * 0.0
            b0 = (inner_r * math.cos(th0), inner_r * math.sin(th0), deck_z - 0.02)
            b1 = (mid_r * math.cos(th1), mid_r * math.sin(th1), deck_z - 0.02)
            _add_tube(rotor, f"brace_{2 * i + 1}", b0, b1, r.arm_radius * 0.45, accent)

    elif module == "spline_tube_lattice":
        for i, th in enumerate(angles):
            tx, ty = R * math.cos(th), R * math.sin(th)
            ttx, tty = -math.sin(th), math.cos(th)
            # Two splayed spline tubes from the hub fanning out to the tip.
            for k, sgn in enumerate((1.0, -1.0)):
                hub_x = 0.12 * math.cos(th) + ttx * sgn * 0.10
                hub_y = 0.12 * math.sin(th) + tty * sgn * 0.10
                pts = [
                    (hub_x, hub_y, deck_z),
                    (
                        R * 0.45 * math.cos(th) + ttx * sgn * 0.16,
                        R * 0.45 * math.sin(th) + tty * sgn * 0.16,
                        deck_z + 0.05,
                    ),
                    (
                        R * 0.78 * math.cos(th) + ttx * sgn * 0.06,
                        R * 0.78 * math.sin(th) + tty * sgn * 0.06,
                        deck_z,
                    ),
                    (tx, ty, deck_z),
                ]
                tube_geom = tube_from_spline_points(
                    pts, radius=r.arm_radius * 0.9, radial_segments=8, samples_per_segment=6
                )
                rotor.visual(
                    mesh_from_geometry(tube_geom, f"arm_tube_{i}_{k}"),
                    origin=Origin(),
                    material=column,
                    name=f"arm_tube_{i}_{k}",
                    material_class_id=(
                        "rust.painted_weathered"
                        if r.palette_style
                        in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                        else "metal.steel_galvanized"
                    ),
                )
            # Short drop link from the arm-tip deck down to the pivot bar so the
            # bar is part of the same connected island (not a floating tip).
            _add_tube(
                rotor,
                f"tip_drop_{i}",
                (tx, ty, deck_z),
                (tx, ty, pivot_z),
                r.arm_radius * 0.8,
                metal,
            )
            _add_pivot_bar(rotor, f"pivot_bar_{i}", tx, ty, pivot_z, th, metal)

    elif module == "cantilever_arm":
        for i, th in enumerate(angles):
            tx, ty = R * math.cos(th), R * math.sin(th)
            hub_x, hub_y = 0.13 * math.cos(th), 0.13 * math.sin(th)
            length = math.hypot(tx - hub_x, ty - hub_y)
            arm_mesh = _tapered_cantilever_arm_mesh(
                0.055, 0.034, length, f"cantilever_arm_{i}_mesh"
            )
            rotor.visual(
                arm_mesh,
                origin=Origin(xyz=(hub_x, hub_y, deck_z), rpy=(0.0, 0.0, th)),
                material=column,
                name=f"cantilever_arm_{i}",
                material_class_id=(
                    "rust.painted_weathered"
                    if r.palette_style
                    in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                    else "metal.steel_galvanized"
                ),
            )
            _add_tube(
                rotor,
                f"tip_drop_{i}",
                (tx, ty, deck_z),
                (tx, ty, pivot_z),
                r.arm_radius * 0.8,
                metal,
            )
            _add_pivot_bar(rotor, f"pivot_bar_{i}", tx, ty, pivot_z, th, metal)

    else:  # overhead_chain_hung
        ring_z = ring_local
        # N inclined struts rise from the hub to elevated ring vertices.
        for i, th in enumerate(angles):
            vx, vy = R * math.cos(th), R * math.sin(th)
            _add_tube(
                rotor,
                f"strut_{i}",
                (0.12 * math.cos(th), 0.12 * math.sin(th), deck_z + 0.10),
                (vx, vy, ring_z),
                r.arm_radius,
                metal,
            )
        # Ring segments connecting adjacent vertices into an N-gon.
        for i, th in enumerate(angles):
            th1 = angles[(i + 1) % r.seat_count]
            a = (R * math.cos(th), R * math.sin(th), ring_z)
            b = (R * math.cos(th1), R * math.sin(th1), ring_z)
            _add_tube(rotor, f"ring_seg_{i}", a, b, r.arm_radius * 0.9, dark)
            # Tangential pivot bar AT the ring vertex (swing interface).
            _add_pivot_bar(
                rotor, f"pivot_bar_{i}", R * math.cos(th), R * math.sin(th), ring_z, th, metal
            )


def _add_pivot_pin(rotor, name, tx, ty, pz, th, mat) -> None:
    # Tangential pin (axis along tangent direction) at the arm tip.
    rotor.visual(
        Cylinder(radius=0.022, length=0.16),
        origin=Origin(xyz=(tx, ty, pz), rpy=(math.pi / 2.0, 0.0, th)),
        material=mat,
        name=name,
        material_class_id="metal.stainless_matte",
    )


def _add_pivot_bar(rotor, name, tx, ty, pz, th, mat) -> None:
    rotor.visual(
        Cylinder(radius=0.026, length=0.18),
        origin=Origin(xyz=(tx, ty, pz), rpy=(math.pi / 2.0, 0.0, th)),
        material=mat,
        name=name,
        material_class_id="metal.stainless_matte",
    )


# ---------------------------------------------------------------------------
# Slot C — seat_type (one chair per station, REVOLUTE swing on the arm pivot)
# ---------------------------------------------------------------------------
def _bucket_shell_mesh(width: float, depth: float, height: float, name: str):
    outer = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=0.04)
        .box(width - 0.08, depth - 0.08, height, centered=(True, True, False))
    )
    shell = outer.cut(cavity)
    # Front opening (toward +X / outward) so legs can hang out.
    front_cut = (
        cq.Workplane("XY")
        .workplane(offset=height * 0.45)
        .box(width + 0.1, depth - 0.10, height, centered=(True, True, False))
        .translate((width * 0.5, 0.0, 0.0))
    )
    shell = shell.cut(front_cut)
    return mesh_from_cadquery(shell, name)


def _build_seats(model: ArticulatedObject, r: ResolvedConfig) -> None:
    metal = _mat(model, "seat_metal", r.palette["metal"])
    dark = _mat(model, "seat_dark", r.palette["dark"])
    seat_mat = _mat(model, "seat_seat", r.palette["seat"])
    accent = _mat(model, "seat_accent", r.palette["accent"])

    angles = _seat_angles(r.seat_count)
    chain_hung = r.arm_structure_module == "overhead_chain_hung"
    # Joint origins are expressed in the ROTOR-local frame (parent=rotor),
    # whose origin sits at world z=hub_z. Local pivot z = -pivot_drop; local
    # ring vertex z = +ring_local (matches _build_rotor's local authoring).
    ring_local = 0.45 * r.column_scale
    anchor_z = ring_local if chain_hung else -r.pivot_drop

    for i, th in enumerate(angles):
        ux, uy = math.cos(th), math.sin(th)
        px, py = r.seat_radius * ux, r.seat_radius * uy
        seat = model.part(f"seat_{i}")

        # The seat part frame origin is at the pivot. Author seat geometry in the
        # part-local frame where +z is up and +x points radially outward. Every
        # piece must form ONE connected island: the suspension hardware reaches
        # from the pivot (local z~=0) down to the body top (body_z + pan_top),
        # and the body parts all embed into a continuous floor pan.
        if chain_hung:
            body_z = -0.62
            pan_top = body_z + 0.04  # top face of the floor pan
            # Bracket at the pivot + two chains running the full drop to the pan.
            seat.visual(
                Box((0.10, 0.20, 0.06)),
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=metal,
                name="hanger_bracket",
                material_class_id=(
                    "metal.steel_galvanized"
                    if r.palette_style
                    in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                    else "rust.oxidized_metal"
                ),
            )
            for j, sgn in enumerate((1.0, -1.0)):
                _add_tube(
                    seat,
                    f"chain_{j}",
                    (0.0, sgn * 0.08, 0.02),
                    (0.0, sgn * 0.08, pan_top),
                    0.014,
                    dark,
                )
        else:
            body_z = -0.52
            pan_top = body_z + 0.04
            # Hanger sleeve captures the tangential pivot bar/pin + two straps
            # that run the full drop down into the floor pan.
            seat.visual(
                Cylinder(radius=0.034, length=0.16),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=metal,
                name="hanger_sleeve",
                material_class_id=(
                    "metal.steel_galvanized"
                    if r.palette_style
                    in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                    else "rust.oxidized_metal"
                ),
            )
            for j, sgn in enumerate((1.0, -1.0)):
                _add_tube(
                    seat,
                    f"hanger_strap_{j}",
                    (0.0, sgn * 0.085, 0.0),
                    (0.02, sgn * 0.085, pan_top),
                    0.016,
                    metal,
                )

        _emit_seat_body(seat, r, metal, dark, seat_mat, accent, body_z)

        # REVOLUTE swing: the joint origin is yawed by th so the seat-local +x
        # points radially outward. In that yawed joint frame, axis (0,-1,0)
        # maps to the world tangent (-sin th, cos th, 0): the seat swings
        # outward/inward in the radial-vertical plane.
        model.articulation(
            f"seat_swing_{i}",
            ArticulationType.REVOLUTE,
            parent="rotor",
            child=seat,
            origin=Origin(xyz=(px, py, anchor_z), rpy=(0.0, 0.0, th)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=120.0, velocity=2.0, lower=-r.swing_limit, upper=r.swing_limit
            ),
        )


def _emit_seat_body(seat, r, metal, dark, seat_mat, accent, body_z) -> None:
    module = r.seat_type_module
    # Continuous floor pan: every body variant builds on this so all visuals
    # form one connected island. Top face at body_z + 0.04 = the hanger landing.
    pan_top = body_z + 0.04
    if module == "flat_platform_seat":
        seat.visual(
            Box((0.45, 0.42, 0.05)),
            origin=Origin(xyz=(0.0, 0.0, body_z + 0.025)),
            material=seat_mat,
            name="platform",
            material_class_id=(
                "plastic.weathered_worn"
                if r.palette_style
                in {
                    "rust_red_cream",
                    "weathered_white_carnival",
                    "faded_teal_rust",
                    "candy_repaint",
                }
                else "plastic.opaque_generic"
            ),
        )
        for j, sgn in enumerate((1.0, -1.0)):
            seat.visual(
                Box((0.05, 0.05, 0.28)),
                origin=Origin(xyz=(-0.18, sgn * 0.16, pan_top + 0.13)),
                material=metal,
                name=f"backrest_post_{j}",
                material_class_id=(
                    "metal.steel_galvanized"
                    if r.palette_style
                    in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                    else "rust.oxidized_metal"
                ),
            )
        seat.visual(
            Box((0.05, 0.42, 0.06)),
            origin=Origin(xyz=(-0.18, 0.0, pan_top + 0.26)),
            material=accent,
            name="backrest_rail",
            material_class_id=(
                "rust.painted_weathered"
                if r.palette_style
                in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                else "metal.paint_coated"
            ),
        )
    elif module == "slatted_bucket_rail":
        # Solid floor pan + slat strips embedded on top + side rails embedded
        # into the pan edges + wrap-around guard rail rising from the rails.
        seat.visual(
            Box((0.44, 0.46, 0.05)),
            origin=Origin(xyz=(0.0, 0.0, body_z + 0.025)),
            material=seat_mat,
            name="floor_pan",
            material_class_id=(
                "plastic.weathered_worn"
                if r.palette_style
                in {
                    "rust_red_cream",
                    "weathered_white_carnival",
                    "faded_teal_rust",
                    "candy_repaint",
                }
                else "plastic.opaque_generic"
            ),
        )
        for j, sgn in enumerate((1.0, -1.0)):
            seat.visual(
                Box((0.44, 0.05, 0.22)),
                origin=Origin(xyz=(0.0, sgn * 0.21, pan_top + 0.08)),
                material=metal,
                name=f"side_rail_{j}",
                material_class_id=(
                    "metal.steel_galvanized"
                    if r.palette_style
                    in {"rust_red_cream", "galvanized_steel", "faded_teal_rust", "candy_repaint"}
                    else "rust.oxidized_metal"
                ),
            )
        n_slats = 6
        for k in range(n_slats):
            sy = -0.18 + k * (0.36 / (n_slats - 1))
            seat.visual(
                Box((0.44, 0.05, 0.03)),
                origin=Origin(xyz=(0.0, sy, pan_top + 0.005)),
                material=seat_mat,
                name=f"slat_{k}",
                material_class_id=(
                    "plastic.weathered_worn"
                    if r.palette_style
                    in {
                        "rust_red_cream",
                        "weathered_white_carnival",
                        "faded_teal_rust",
                        "candy_repaint",
                    }
                    else "plastic.opaque_generic"
                ),
            )
        # Wrap-around guard rail (front + two sides, opening toward center/-x).
        gz = pan_top + 0.20
        guard_pts = [
            (-0.18, 0.235, gz),
            (0.22, 0.235, gz),
            (0.28, 0.0, gz),
            (0.22, -0.235, gz),
            (-0.18, -0.235, gz),
        ]
        guard_geom = tube_from_spline_points(
            guard_pts, radius=0.02, radial_segments=8, samples_per_segment=6
        )
        seat.visual(
            mesh_from_geometry(guard_geom, "guard_rail"),
            origin=Origin(),
            material=accent,
            name="guard_rail",
            material_class_id=(
                "rust.painted_weathered"
                if r.palette_style
                in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                else "metal.paint_coated"
            ),
        )
        for j, sgn in enumerate((1.0, -1.0)):
            _add_tube(
                seat,
                f"rail_post_{j}",
                (0.22, sgn * 0.235, pan_top + 0.04),
                (0.22, sgn * 0.235, gz),
                0.018,
                accent,
            )
    else:  # deep_bucket_seat
        # Floor pan + deep CadQuery shell sitting on it + lap bar.
        seat.visual(
            Box((0.44, 0.46, 0.05)),
            origin=Origin(xyz=(0.0, 0.0, body_z + 0.025)),
            material=dark,
            name="hanger_mount",
            material_class_id="metal.blackened_gunmetal",
        )
        seat.visual(
            _bucket_shell_mesh(0.44, 0.46, 0.34, "bucket_shell_mesh"),
            origin=Origin(xyz=(0.05, 0.0, pan_top)),
            material=seat_mat,
            name="bucket_shell",
            material_class_id=(
                "plastic.weathered_worn"
                if r.palette_style
                in {
                    "rust_red_cream",
                    "weathered_white_carnival",
                    "faded_teal_rust",
                    "candy_repaint",
                }
                else "plastic.opaque_generic"
            ),
        )
        # Lap / safety bar across the front (fixed visual, part of the swing).
        bar_z = pan_top + 0.24
        for j, sgn in enumerate((1.0, -1.0)):
            _add_tube(
                seat,
                f"bar_bracket_{j}",
                (0.10, sgn * 0.20, pan_top + 0.04),
                (0.24, sgn * 0.20, bar_z),
                0.016,
                accent,
            )
        seat.visual(
            Cylinder(radius=0.02, length=0.42),
            origin=Origin(xyz=(0.24, 0.0, bar_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=accent,
            name="safety_bar",
            material_class_id=(
                "rust.painted_weathered"
                if r.palette_style
                in {"rust_red_cream", "weathered_white_carnival", "faded_teal_rust"}
                else "metal.paint_coated"
            ),
        )


# ---------------------------------------------------------------------------
# Top-level builders
# ---------------------------------------------------------------------------
def build_playground_chair_swing_carousel(
    config: PlaygroundChairSwingCarouselConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or PlaygroundChairSwingCarouselConfig())
    model = ArticulatedObject(name=r.name, assets=assets)
    _build_base_form(model, r)
    _build_rotor(model, r)

    # ONE CONTINUOUS spin: rotor about Z through the column top.
    model.articulation(
        "rotor_spin",
        ArticulationType.CONTINUOUS,
        parent="support_column",
        child="rotor",
        origin=Origin(xyz=(0.0, 0.0, r.hub_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=8.0),
        meta={"type": "continuous", "axis": (0.0, 0.0, 1.0), "range": "continuous"},
    )

    _build_seats(model, r)

    model.meta["template_slug"] = "playground_chair_swing_carousel"
    model.meta["base_form_module"] = r.base_form_module
    model.meta["arm_structure_module"] = r.arm_structure_module
    model.meta["seat_type_module"] = r.seat_type_module
    model.meta["seat_count"] = r.seat_count
    return model


def build_seeded_playground_chair_swing_carousel(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_playground_chair_swing_carousel(config_from_seed(seed), assets=assets)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("base_form", r.base_form_module),
        ("arm_structure", r.arm_structure_module),
        ("seat_type", r.seat_type_module),
        ("seat_count", f"N{r.seat_count}"),
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_playground_chair_swing_carousel_tests(
    object_model: ArticulatedObject,
    config: PlaygroundChairSwingCarouselConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_by_name = {part.name: part for part in object_model.parts}
    base = object_model.get_part("support_column")
    rotor = object_model.get_part("rotor")

    # Captured-shaft: rotor hub sleeve straddles the column top bearing.
    ctx.allow_overlap(
        base,
        rotor,
        reason="The rotor hub sleeve is captured on the column top bearing collar (spin bearing).",
    )

    # Captured-pin: each seat hanger captures its tangential pivot on the rotor.
    for i in range(r.seat_count):
        seat = part_by_name.get(f"seat_{i}")
        if seat is None:
            continue
        ctx.allow_overlap(
            rotor,
            seat,
            reason="Each seat hanger sleeve/bracket is captured on its arm-tip tangential pivot.",
        )

    ctx.check_model_valid()

    parts = {part.name for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}

    ctx.check("support_column_present", "support_column" in parts)
    ctx.check("rotor_present", "rotor" in parts)

    # ONE CONTINUOUS spin about Z.
    spin = joints.get("rotor_spin")
    ctx.check("rotor_spin_present", spin is not None)
    if spin is not None:
        ctx.check(
            "rotor_spin_continuous",
            spin.articulation_type == ArticulationType.CONTINUOUS,
            details=str(spin.articulation_type),
        )
        ctx.check(
            "rotor_spin_axis_vertical",
            tuple(round(a, 3) for a in spin.axis) == (0.0, 0.0, 1.0),
            details=str(spin.axis),
        )
    continuous_joints = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.CONTINUOUS
    ]
    ctx.check(
        "exactly_one_continuous_spin",
        len(continuous_joints) == 1,
        details=str([j.name for j in continuous_joints]),
    )

    # N seats + N REVOLUTE swing joints, equiangular.
    seat_parts = [p for p in parts if p.startswith("seat_")]
    ctx.check(
        "seat_count_matches",
        len(seat_parts) == r.seat_count,
        details=f"{len(seat_parts)} vs {r.seat_count}",
    )
    for i in range(r.seat_count):
        jn = f"seat_swing_{i}"
        j = joints.get(jn)
        ctx.check(f"{jn}_present", j is not None, details=jn)
        if j is not None:
            ctx.check(
                f"{jn}_revolute",
                j.articulation_type == ArticulationType.REVOLUTE,
                details=str(j.articulation_type),
            )
            # Tangential swing axis: in the yawed joint frame the axis is the
            # local y direction (0,-1,0); the origin yaw (rpy z) maps it to the
            # world tangent. Verify axis is horizontal local-y and origin yaw=th.
            ctx.check(
                f"{jn}_axis_tangential",
                tuple(round(a, 3) for a in j.axis) == (0.0, -1.0, 0.0),
                details=str(j.axis),
            )
            th = 2.0 * math.pi * i / r.seat_count
            yaw = j.origin.rpy[2] if j.origin is not None else 0.0
            ctx.check(
                f"{jn}_origin_yaw_equiangular",
                abs(((yaw - th + math.pi) % (2.0 * math.pi)) - math.pi) < 1e-3,
                details=f"yaw={yaw:.4f} th={th:.4f}",
            )

    return ctx.report()


__all__ = [
    "PlaygroundChairSwingCarouselConfig",
    "ResolvedConfig",
    "build_playground_chair_swing_carousel",
    "build_seeded_playground_chair_swing_carousel",
    "config_from_seed",
    "resolve_config",
    "run_playground_chair_swing_carousel_tests",
    "slot_choices_for_seed",
    "__modular__",
]
