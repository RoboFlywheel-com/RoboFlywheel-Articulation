# SPDX-License-Identifier: Apache-2.0

"""Source-backed round cabinet template with mechanically gated facade profiles.

The original asset is not a full-width door plus full-width drawers.  It is a
partitioned demilune cabinet: one curved closure occupies one quadrant and a
stack of complete curved drawers occupies the other.  The paired-door variant
is the only profile that replaces the drawer bank.  Keeping that dependency in
one ``FacadeProfile`` prevents the invalid Cartesian products produced by the
legacy template.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BodyForm = Literal["d_shape", "full_cylinder", "oval_drum"]
FacadeProfile = Literal[
    "hinged_side_door_drawers",
    "arc_slide_side_door_drawers",
    "tambour_side_door_drawers",
    "paired_curved_doors",
]
BaseProfile = Literal["tapered_legs", "rotating_pedestal"]
Handedness = Literal["door_left", "door_right"]
PaletteStyle = Literal[
    "charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter", "ebony_pearl"
]

BODY_FORMS: tuple[BodyForm, ...] = ("d_shape", "full_cylinder", "oval_drum")
FACADE_PROFILES: tuple[FacadeProfile, ...] = (
    "hinged_side_door_drawers",
    "arc_slide_side_door_drawers",
    "tambour_side_door_drawers",
    "paired_curved_doors",
)
BASE_PROFILES: tuple[BaseProfile, ...] = ("tapered_legs", "rotating_pedestal")
HANDEDNESS: tuple[Handedness, ...] = ("door_left", "door_right")
DRAWER_COUNTS: tuple[int, ...] = (2, 3, 4)
SHELF_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "charcoal_brass",
    "walnut_bronze",
    "ivory_gold",
    "sage_pewter",
    "ebony_pearl",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_brass": {
        "carcass": (0.105, 0.095, 0.085, 1.0),
        "panel": (0.145, 0.132, 0.118, 1.0),
        "interior": (0.115, 0.102, 0.090, 1.0),
        "trim": (0.72, 0.62, 0.47, 1.0),
        "hardware": (0.79, 0.77, 0.70, 1.0),
    },
    "walnut_bronze": {
        "carcass": (0.28, 0.16, 0.08, 1.0),
        "panel": (0.36, 0.22, 0.12, 1.0),
        "interior": (0.22, 0.13, 0.06, 1.0),
        "trim": (0.62, 0.44, 0.24, 1.0),
        "hardware": (0.75, 0.60, 0.36, 1.0),
    },
    "ivory_gold": {
        "carcass": (0.90, 0.88, 0.82, 1.0),
        "panel": (0.85, 0.82, 0.76, 1.0),
        "interior": (0.78, 0.75, 0.68, 1.0),
        "trim": (0.85, 0.68, 0.32, 1.0),
        "hardware": (0.92, 0.80, 0.44, 1.0),
    },
    "sage_pewter": {
        "carcass": (0.58, 0.62, 0.52, 1.0),
        "panel": (0.48, 0.54, 0.44, 1.0),
        "interior": (0.40, 0.44, 0.36, 1.0),
        "trim": (0.60, 0.62, 0.64, 1.0),
        "hardware": (0.70, 0.72, 0.74, 1.0),
    },
    "ebony_pearl": {
        "carcass": (0.055, 0.05, 0.045, 1.0),
        "panel": (0.90, 0.88, 0.83, 1.0),
        "interior": (0.10, 0.09, 0.08, 1.0),
        "trim": (0.85, 0.83, 0.78, 1.0),
        "hardware": (0.90, 0.88, 0.83, 1.0),
    },
}


def _arc_points(
    rx: float, ry: float, a0: float, a1: float, count: int
) -> list[tuple[float, float]]:
    return [
        (
            rx * math.cos(math.radians(a0 + (a1 - a0) * i / count)),
            ry * math.sin(math.radians(a0 + (a1 - a0) * i / count)),
        )
        for i in range(count + 1)
    ]


def _sector(
    inner: float,
    outer: float,
    a0: float,
    a1: float,
    z0: float,
    height: float,
    ry_scale: float = 1.0,
    segments: int = 40,
) -> cq.Workplane:
    points = _arc_points(outer, outer * ry_scale, a0, a1, segments)
    points += list(reversed(_arc_points(inner, inner * ry_scale, a0, a1, segments)))
    return cq.Workplane("XY").polyline(points).close().extrude(height).translate((0.0, 0.0, z0))


def _plate(radius: float, ry_scale: float, z0: float, height: float, full: bool) -> cq.Workplane:
    a0, a1 = (0.0, 360.0) if full else (-180.0, 0.0)
    return _sector(0.001, radius, a0, a1, z0, height, ry_scale, 72)


def _annulus(inner: float, outer: float, ry_scale: float, z0: float, height: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .ellipse(outer, outer * ry_scale)
        .ellipse(inner, inner * ry_scale)
        .extrude(height)
        .translate((0.0, 0.0, z0))
    )


def _localize(shape: cq.Workplane, xyz: tuple[float, float, float]) -> cq.Workplane:
    return shape.translate((-xyz[0], -xyz[1], -xyz[2]))


def _tapered_square(
    x: float,
    y: float,
    z0: float,
    height: float,
    bottom_size: float,
    top_size: float,
) -> cq.Workplane:
    """Source-backed load-bearing leg loft with a broad cabinet-side shoulder."""

    return (
        cq.Workplane("XY")
        .rect(bottom_size, bottom_size)
        .workplane(offset=height)
        .rect(top_size, top_size)
        .loft()
        .translate((x, y, z0))
    )


@dataclass(frozen=True)
class RoundCabinetConfig:
    body_form: BodyForm = "d_shape"
    facade_profile: FacadeProfile = "hinged_side_door_drawers"
    base_profile: BaseProfile = "tapered_legs"
    handedness: Handedness = "door_left"
    drawer_count: int = 3
    shelf_count: int = 2
    palette_style: PaletteStyle = "charcoal_brass"
    cabinet_radius: float = 0.46
    cabinet_height: float = 0.90
    oval_x_over_y: float = 1.20
    door_open_angle: float = math.radians(96.0)
    drawer_travel: float = 0.24
    name: str = "round_cabinet"


@dataclass(frozen=True)
class ResolvedRoundCabinetConfig:
    body_form: BodyForm
    facade_profile: FacadeProfile
    base_profile: BaseProfile
    handedness: Handedness
    drawer_count: int
    shelf_count: int
    palette_style: PaletteStyle
    outer_r: float
    ry_scale: float
    height: float
    z_base: float
    z_top: float
    door_a0: float
    door_a1: float
    drawer_a0: float
    drawer_a1: float
    door_open_angle: float
    drawer_travel: float
    drawer_z: tuple[float, ...]
    drawer_height: float
    name: str


def config_from_seed(seed: int) -> RoundCabinetConfig:
    rng = random.Random(seed)
    body = rng.choice(BODY_FORMS)
    facade = rng.choice(
        FACADE_PROFILES
        if body != "oval_drum"
        else ("hinged_side_door_drawers", "paired_curved_doors")
    )
    return RoundCabinetConfig(
        body_form=body,
        facade_profile=facade,
        base_profile=rng.choice(BASE_PROFILES),
        handedness=rng.choice(HANDEDNESS),
        drawer_count=rng.choice(DRAWER_COUNTS),
        palette_style=rng.choice(PALETTE_STYLES),
        shelf_count=rng.choice(SHELF_COUNTS),
        cabinet_radius=round(rng.uniform(0.40, 0.50), 3),
        cabinet_height=round(rng.uniform(0.84, 0.96), 3),
        oval_x_over_y=round(rng.uniform(1.10, 1.30), 3),
        door_open_angle=round(rng.uniform(math.radians(82.0), math.radians(105.0)), 3),
        drawer_travel=round(rng.uniform(0.20, 0.27), 3),
        name=f"seeded_round_cabinet_{seed}",
    )


def resolve_config(config: RoundCabinetConfig | None = None) -> ResolvedRoundCabinetConfig:
    cfg = config or RoundCabinetConfig()
    if cfg.body_form not in BODY_FORMS or cfg.facade_profile not in FACADE_PROFILES:
        raise ValueError("unsupported body_form or facade_profile")
    if cfg.base_profile not in BASE_PROFILES or cfg.handedness not in HANDEDNESS:
        raise ValueError("unsupported base_profile or handedness")
    if cfg.body_form == "oval_drum" and cfg.facade_profile in {
        "arc_slide_side_door_drawers",
        "tambour_side_door_drawers",
    }:
        raise ValueError("oval_drum has no accepted constant-curvature carrier profile")
    if (
        cfg.drawer_count not in DRAWER_COUNTS
        or cfg.shelf_count not in SHELF_COUNTS
        or cfg.palette_style not in PALETTES
    ):
        raise ValueError("unsupported drawer_count, shelf_count or palette_style")
    outer = max(0.38, min(0.52, cfg.cabinet_radius))
    height = max(0.82, min(0.98, cfg.cabinet_height))
    ry = max(0.72, min(0.92, 1.0 / cfg.oval_x_over_y)) if cfg.body_form == "oval_drum" else 1.0
    z_base, z_top = 0.18, height - 0.045
    # One master handedness profile drives door, drawer, stiles, tracks and axes.
    if cfg.handedness == "door_left":
        door_a0, door_a1, drawer_a0, drawer_a1 = -176.0, -96.0, -86.0, -4.0
    else:
        door_a0, door_a1, drawer_a0, drawer_a1 = -84.0, -4.0, -176.0, -94.0
    count = 0 if cfg.facade_profile == "paired_curved_doors" else cfg.drawer_count
    band = z_top - z_base - 0.04
    pitch = band / max(count, 1)
    drawer_h = min(0.205, pitch * 0.82)
    drawer_z = tuple(z_base + 0.02 + i * pitch + (pitch - drawer_h) / 2.0 for i in range(count))
    return ResolvedRoundCabinetConfig(
        cfg.body_form,
        cfg.facade_profile,
        cfg.base_profile,
        cfg.handedness,
        count,
        cfg.shelf_count,
        cfg.palette_style,
        outer,
        ry,
        height,
        z_base,
        z_top,
        door_a0,
        door_a1,
        drawer_a0,
        drawer_a1,
        max(math.radians(75.0), min(math.radians(108.0), cfg.door_open_angle)),
        max(0.18, min(0.29, cfg.drawer_travel)),
        drawer_z,
        drawer_h,
        cfg.name or "round_cabinet",
    )


def with_overrides(config: RoundCabinetConfig, **kwargs: object) -> RoundCabinetConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RoundCabinetConfig | ResolvedRoundCabinetConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRoundCabinetConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("facade_profile", r.facade_profile),
        ("base_profile", r.base_profile),
        ("handedness", r.handedness),
        ("drawer_count", str(r.drawer_count)),
        ("shelf_count", str(r.shelf_count)),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _emit_carcass(part, r: ResolvedRoundCabinetConfig, mats: dict[str, object]) -> None:
    full = r.body_form != "d_shape"
    if r.facade_profile in {"arc_slide_side_door_drawers", "tambour_side_door_drawers"}:
        # The top is split around a real arc slot.  This keeps the moving
        # carrier bracket out of solid slab geometry instead of hiding the
        # intersection with an overlap allowance.
        part.visual(
            mesh_from_cadquery(
                _plate(r.outer_r - 0.050, r.ry_scale, r.z_top, 0.035, full), "top_slab_core"
            ),
            material=mats["carcass"],
            name="top_slab_core", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )
        slot0 = max(-180.0, r.door_a0 - 12.0)
        slot1 = min(0.0, r.door_a1 + 12.0)
        rim_ranges = [(-180.0, slot0), (slot1, 0.0)]
        if full:
            rim_ranges.append((0.0, 180.0))
        for i, (a0, a1) in enumerate(rim_ranges):
            if a1 - a0 > 2.0:
                part.visual(
                    mesh_from_cadquery(
                        _sector(
                            r.outer_r - 0.055,
                            r.outer_r + 0.012,
                            a0,
                            a1,
                            r.z_top,
                            0.035,
                            r.ry_scale,
                            36,
                        ),
                        f"top_slab_rim_{i}",
                    ),
                    material=mats["carcass"],
                    name=f"top_slab_rim_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
                )
    else:
        part.visual(
            mesh_from_cadquery(
                _plate(r.outer_r + 0.012, r.ry_scale, r.z_top, 0.035, full), "top_slab"
            ),
            material=mats["carcass"],
            name="top_slab", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )
    part.visual(
        mesh_from_cadquery(
            _plate(r.outer_r, r.ry_scale, r.z_base - 0.045, 0.045, full), "base_slab"
        ),
        material=mats["carcass"],
        name="base_slab", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
    )
    if full:
        part.visual(
            mesh_from_cadquery(
                _sector(
                    r.outer_r - 0.030,
                    r.outer_r,
                    3.0,
                    177.0,
                    r.z_base,
                    r.z_top - r.z_base,
                    r.ry_scale,
                    54,
                ),
                "rear_shell",
            ),
            material=mats["carcass"],
            name="rear_shell", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )
    else:
        part.visual(
            Box((2.0 * r.outer_r - 0.025, 0.024, r.z_top - r.z_base)),
            origin=Origin(xyz=(0.0, 0.006, (r.z_top + r.z_base) / 2.0)),
            material=mats["carcass"],
            name="flat_back", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )
    # Edge and partition stiles are derived from the same handed facade profile.
    boundaries = (-179.0, -90.0, -1.0)
    # A full-height jamb cannot occupy the same swept volume as the external
    # hinge leaf.  The hinge-side boundary is therefore an intentional opening
    # carried by the thrust pad/spindle assembly rather than a collision hidden
    # by an overlap allowance.
    omitted_stiles: set[int] = set()
    if r.facade_profile == "paired_curved_doors":
        omitted_stiles = {0, 2}
    elif r.facade_profile == "hinged_side_door_drawers":
        omitted_stiles = {0 if r.handedness == "door_left" else 2}
    for i, a in enumerate(boundaries):
        if i in omitted_stiles:
            continue
        part.visual(
            mesh_from_cadquery(
                _sector(
                    r.outer_r - 0.035,
                    r.outer_r - 0.006,
                    a - 1.5,
                    a + 1.5,
                    r.z_base,
                    r.z_top - r.z_base,
                    r.ry_scale,
                    6,
                ),
                f"stile_{i}",
            ),
            material=mats["carcass"],
            name=f"stile_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )

    if r.facade_profile == "paired_curved_doors":
        # Two interior shelves, safely recessed from the door swept envelope.
        for i in range(r.shelf_count):
            z = r.z_base + (i + 1) / (r.shelf_count + 1) * (r.z_top - r.z_base)
            part.visual(
                mesh_from_cadquery(
                    _plate(r.outer_r - 0.034, r.ry_scale, z, 0.014, False), f"shelf_{i}"
                ),
                material=mats["interior"],
                name=f"shelf_{i}", material_class_id="wood.engineered_board",
            )
    else:
        # Door-quadrant shelves do not intrude into the drawer bank.
        for i in range(r.shelf_count):
            z = r.z_base + (i + 1) / (r.shelf_count + 1) * (r.z_top - r.z_base)
            part.visual(
                mesh_from_cadquery(
                    _sector(
                        0.08,
                        r.outer_r - 0.034,
                        -180.0 if r.door_a0 < -90.0 else -90.0,
                        -90.0 if r.door_a1 < -90.0 else 0.0,
                        z,
                        0.014,
                        r.ry_scale,
                        36,
                    ),
                    f"door_shelf_{i}",
                ),
                material=mats["interior"],
                name=f"door_shelf_{i}", material_class_id="wood.engineered_board",
            )
        # Each drawer has two longitudinal side rails, never a transverse support shelf.
        # A central structural spine belongs to the carcass, behind the drawer
        # rear constraints.  Short rear yokes mount both side rails to it; the
        # spine is not a drawer guide and never enters the tray cavity.
        part.visual(
            Box((0.035, 0.035, r.z_top - r.z_base)),
            origin=Origin(xyz=(0.0, 0.0, (r.z_top + r.z_base) / 2.0)),
            material=mats["carcass"],
            name="drawer_mounting_spine", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )
        center = math.radians((r.drawer_a0 + r.drawer_a1) / 2.0)
        radial = (math.cos(center), math.sin(center) * r.ry_scale)
        radial_norm = math.hypot(radial[0], radial[1])
        radial = (radial[0] / radial_norm, radial[1] / radial_norm)
        tangent = (-radial[1], radial[0])
        rail_length = r.outer_r * 0.85
        rail_center_radius = r.outer_r * 0.55
        # Keep both runners under the tray floor, clear of the curved side
        # walls even when the master profile is oval-scaled.
        half_width = r.outer_r * 0.18
        yaw = math.atan2(radial[1], radial[0])
        for i, z0 in enumerate(r.drawer_z):
            for side, s in (("left", -1.0), ("right", 1.0)):
                x = rail_center_radius * radial[0] + s * half_width * tangent[0]
                y = rail_center_radius * radial[1] + s * half_width * tangent[1]
                part.visual(
                    Box((rail_length, 0.014, 0.014)),
                    origin=Origin(xyz=(x, y, z0 - 0.007), rpy=(0.0, 0.0, yaw)),
                    material=mats["trim"],
                    name=f"drawer_rail_{i}_{side}", material_class_id=("metal.brass_aged" if r.palette_style in {"charcoal_brass", "walnut_bronze", "sage_pewter", "ebony_pearl"} else "metal.brass_polished"),
                )
                inner_radius = rail_center_radius - rail_length / 2.0
                rail_inner = (
                    inner_radius * radial[0] + s * half_width * tangent[0],
                    inner_radius * radial[1] + s * half_width * tangent[1],
                )
                bracket_target = (0.0, 0.0)
                bdx = bracket_target[0] - rail_inner[0]
                bdy = bracket_target[1] - rail_inner[1]
                bracket_length = math.hypot(bdx, bdy)
                part.visual(
                    Box((bracket_length + 0.040, 0.014, 0.014)),
                    origin=Origin(
                        xyz=(
                            (rail_inner[0] + bracket_target[0]) / 2.0,
                            (rail_inner[1] + bracket_target[1]) / 2.0,
                            z0 - 0.008,
                        ),
                        rpy=(0.0, 0.0, math.atan2(bdy, bdx)),
                    ),
                    material=mats["trim"],
                    name=f"drawer_rail_bracket_{i}_{side}", material_class_id=("metal.brass_aged" if r.palette_style in {"charcoal_brass", "walnut_bronze", "sage_pewter", "ebony_pearl"} else "metal.brass_polished"),
                )


def _emit_base(
    model: ArticulatedObject, carcass, r: ResolvedRoundCabinetConfig, mats: dict[str, object]
) -> None:
    if r.base_profile == "tapered_legs":
        # The accepted origin has three visibly tapered front legs with foot
        # tips.  Their broad shoulders overlap the base-slab underside by
        # 6 mm, so they are a real load path rather than decorative blocks.
        base_underside = r.z_base - 0.045
        leg_bottom = -0.015
        leg_top = base_underside + 0.006
        foot_bottom = -0.047
        foot_top = leg_bottom + 0.006
        for i, a in enumerate((-155.0, -90.0, -25.0)):
            x = r.outer_r * 0.84 * math.cos(math.radians(a))
            y = r.outer_r * 0.84 * r.ry_scale * math.sin(math.radians(a))
            carcass.visual(
                mesh_from_cadquery(
                    _tapered_square(
                        x,
                        y,
                        leg_bottom,
                        leg_top - leg_bottom,
                        0.032,
                        0.054,
                    ),
                    f"leg_{i}",
                ),
                material=mats["carcass"],
                name=f"leg_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
            )
            carcass.visual(
                mesh_from_cadquery(
                    _tapered_square(
                        x,
                        y,
                        foot_bottom,
                        foot_top - foot_bottom,
                        0.027,
                        0.034,
                    ),
                    f"foot_tip_{i}",
                ),
                material=mats["hardware"],
                name=f"foot_tip_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
            )
        return
    pedestal = model.part("pedestal")
    # Child geometry is local to the bearing-plane joint.  Everything stays
    # below z=0, leaving real clearance below the carcass base slab.
    pedestal.visual(
        mesh_from_cadquery(
            _plate(r.outer_r + 0.018, r.ry_scale, -0.110, 0.080, r.body_form != "d_shape"),
            "pedestal_disk",
        ),
        material=mats["carcass"],
        name="pedestal_disk", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
    )
    pedestal.visual(
        Cylinder(radius=0.075, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, -0.015)),
        material=mats["hardware"],
        name="bearing_hub", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
    )
    pedestal.inertial = Inertial.from_geometry(Cylinder(radius=r.outer_r, length=0.08), mass=10.0)
    model.articulation(
        "carcass_to_rotating_pedestal",
        ArticulationType.CONTINUOUS,
        parent=carcass,
        child=pedestal,
        origin=Origin(xyz=(0.0, 0.0, r.z_base - 0.045)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=35.0, velocity=0.8),
        mating=MatingContract(
            parent_face_geometry="base_slab",
            parent_face_side="negative_z",
            child_face_geometry="bearing_hub",
            child_face_side="positive_z",
            contact_tol=0.05,
        ),
        meta={"mechanism": "turntable pedestal with central bearing clearance"},
    )


def _emit_curved_panel(
    part,
    r: ResolvedRoundCabinetConfig,
    mats: dict[str, object],
    origin: tuple[float, float, float],
    a0: float,
    a1: float,
    name: str = "curved_panel",
) -> None:
    part.visual(
        mesh_from_cadquery(
            _localize(
                _sector(
                    r.outer_r - 0.025,
                    r.outer_r - 0.009,
                    a0,
                    a1,
                    r.z_base + 0.018,
                    r.z_top - r.z_base - 0.036,
                    r.ry_scale,
                    40,
                ),
                origin,
            ),
            name,
        ),
        material=mats["carcass"],
        name=name, material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
    )
    part.visual(
        mesh_from_cadquery(
            _localize(
                _sector(
                    r.outer_r - 0.009,
                    r.outer_r - 0.004,
                    a0 + 4.0,
                    a1 - 4.0,
                    r.z_base + 0.045,
                    r.z_top - r.z_base - 0.090,
                    r.ry_scale,
                    34,
                ),
                origin,
            ),
            "panel_field",
        ),
        material=mats["panel"],
        name="panel_field", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
    )


def _emit_external_hinge(
    carcass,
    door,
    r: ResolvedRoundCabinetConfig,
    mats: dict[str, object],
    *,
    origin: tuple[float, float, float],
    panel_edge_angle: float,
    index: int,
) -> None:
    """External thrust hinge with a real, non-penetrating support face."""
    door_h = r.z_top - r.z_base - 0.036
    # The spindle centre sits 10 mm outside the nominal curved base radius.
    # A 20 mm square pad only touched the tessellated base at a mathematical
    # tangent, leaving a 41.54 µm mesh gap.  Use a real round thrust-bearing
    # landing with 18 mm radius: it laps the load-bearing base slab radially by
    # at least 8 mm and vertically by 10 mm, so support is mechanical rather
    # than a tolerance trick or collision allowance.
    carcass.visual(
        Cylinder(radius=0.018, length=0.028),
        origin=Origin(xyz=(origin[0], origin[1], origin[2] - 0.014)),
        material=mats["hardware"],
        name=f"door_thrust_pad_{index}", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
    )
    door.visual(
        Cylinder(radius=0.006, length=door_h),
        origin=Origin(xyz=(0.0, 0.0, door_h / 2.0)),
        material=mats["hardware"],
        name="pivot_spindle", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
    )
    target = (
        (r.outer_r - 0.017) * math.cos(math.radians(panel_edge_angle)),
        (r.outer_r - 0.017) * r.ry_scale * math.sin(math.radians(panel_edge_angle)),
    )
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    length = math.hypot(dx, dy)
    door.visual(
        Box((length + 0.012, 0.014, door_h * 0.90)),
        origin=Origin(
            xyz=(dx / 2.0, dy / 2.0, door_h / 2.0),
            rpy=(0.0, 0.0, math.atan2(dy, dx)),
        ),
        material=mats["hardware"],
        name="hinge_leaf", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
    )


def _emit_closures(
    model: ArticulatedObject, carcass, r: ResolvedRoundCabinetConfig, mats: dict[str, object]
) -> None:
    if r.facade_profile == "paired_curved_doors":
        specs = ((-176.0, -94.0, -177.5, -1.0), (-86.0, -4.0, -2.5, 1.0))
        for i, (a0, a1, hinge_a, axis_z) in enumerate(specs):
            hr = r.outer_r + 0.010
            origin = (
                hr * math.cos(math.radians(hinge_a)),
                hr * r.ry_scale * math.sin(math.radians(hinge_a)),
                r.z_base + 0.018,
            )
            door = model.part(f"cabinet_door_{i}")
            _emit_curved_panel(door, r, mats, origin, a0, a1)
            _emit_external_hinge(
                carcass,
                door,
                r,
                mats,
                origin=origin,
                panel_edge_angle=a0 if i == 0 else a1,
                index=i,
            )
            handle_a = a1 - 8.0 if i == 0 else a0 + 8.0
            door.visual(
                Sphere(radius=0.012),
                origin=Origin(
                    xyz=(
                        (r.outer_r + 0.006) * math.cos(math.radians(handle_a)) - origin[0],
                        (r.outer_r + 0.006) * r.ry_scale * math.sin(math.radians(handle_a))
                        - origin[1],
                        (r.z_top - r.z_base) * 0.52,
                    )
                ),
                material=mats["hardware"],
                name="handle", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
            )
            door.inertial = Inertial.from_geometry(
                Box((r.outer_r, 0.025, r.z_top - r.z_base)), mass=4.5
            )
            model.articulation(
                f"body_to_cabinet_door_{i}",
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=door,
                origin=Origin(xyz=origin),
                axis=(0.0, 0.0, axis_z),
                motion_limits=MotionLimits(
                    effort=18.0, velocity=1.0, lower=0.0, upper=r.door_open_angle
                ),
                mating=MatingContract(
                    parent_face_geometry=f"door_thrust_pad_{i}",
                    parent_face_side="positive_z",
                    child_face_geometry="pivot_spindle",
                    child_face_side="negative_z",
                    contact_tol=0.002,
                ),
            )
        return

    a0, a1 = r.door_a0, r.door_a1
    if r.facade_profile == "hinged_side_door_drawers":
        hinge_a = a0 - 1.5 if r.handedness == "door_left" else a1 + 1.5
        axis_z = -1.0 if r.handedness == "door_left" else 1.0
        hr = r.outer_r + 0.010
        origin = (
            hr * math.cos(math.radians(hinge_a)),
            hr * r.ry_scale * math.sin(math.radians(hinge_a)),
            r.z_base + 0.018,
        )
        door = model.part("cabinet_door_0")
        _emit_curved_panel(door, r, mats, origin, a0, a1)
        _emit_external_hinge(
            carcass,
            door,
            r,
            mats,
            origin=origin,
            panel_edge_angle=a0 if r.handedness == "door_left" else a1,
            index=0,
        )
        limits = MotionLimits(effort=18.0, velocity=1.0, lower=0.0, upper=r.door_open_angle)
        model.articulation(
            "body_to_cabinet_door_0",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=door,
            origin=Origin(xyz=origin),
            axis=(0.0, 0.0, axis_z),
            motion_limits=limits,
            mating=MatingContract(
                parent_face_geometry="door_thrust_pad_0",
                parent_face_side="positive_z",
                child_face_geometry="pivot_spindle",
                child_face_side="negative_z",
                contact_tol=0.002,
            ),
        )
        return

    # Arc-slide and tambour are rigid segmented shells captured by a concealed
    # annular carrier.  The carrier makes the curvature-centre revolute joint a
    # real bearing centreline; there is no fake radial spoke through the cavity.
    door = model.part("cabinet_door_0")
    origin = (0.0, 0.0, 0.0)
    if r.handedness == "door_left":
        moving_a0, moving_a1, axis_z = (
            a0,
            a0 + (48.0 if "tambour" in r.facade_profile else 64.0),
            1.0,
        )
    else:
        moving_a0, moving_a1, axis_z = (
            a1 - (48.0 if "tambour" in r.facade_profile else 64.0),
            a1,
            -1.0,
        )
    panel_name = (
        "tambour_shell" if r.facade_profile == "tambour_side_door_drawers" else "curved_panel"
    )
    panel = _sector(
        r.outer_r - 0.025,
        r.outer_r - 0.009,
        moving_a0,
        moving_a1,
        r.z_base + 0.018,
        r.z_top - r.z_base - 0.036,
        r.ry_scale,
        40,
    )
    # A compact carrier lug remains inside the deliberate gap between the two
    # stationary bearing-track arcs for the complete joint range.  Using the
    # whole door arc as a bracket would sweep through the fixed track.
    if r.handedness == "door_left":
        bracket_a0, bracket_a1 = moving_a0, moving_a0 + 10.0
    else:
        bracket_a0, bracket_a1 = moving_a1 - 10.0, moving_a1
    bracket = _sector(
        r.outer_r - 0.047,
        r.outer_r + 0.010,
        bracket_a0,
        bracket_a1,
        r.z_top - 0.026,
        0.078,
        r.ry_scale,
        40,
    )
    door.visual(mesh_from_cadquery(panel, panel_name), material=mats["carcass"], name=panel_name, material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"))
    door.visual(
        mesh_from_cadquery(bracket, "carrier_bracket"),
        material=mats["hardware"],
        name="carrier_bracket", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
    )
    # Keep one annular carrier as its own named element so joint-origin QC can
    # verify the true curvature centreline instead of treating the asymmetric
    # door shell's AABB centre as the pivot.
    door.visual(
        mesh_from_cadquery(
            _annulus(
                r.outer_r - 0.005,
                r.outer_r + 0.018,
                1.0,
                r.z_top + 0.042,
                0.010,
            ),
            "carrier_bearing_ring",
        ),
        material=mats["hardware"],
        name="carrier_bearing_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
    )
    support_ranges = (
        ((-104.0, 0.0), (0.0, 180.0))
        if r.handedness == "door_left"
        else ((-180.0, -76.0), (0.0, 180.0))
    )
    for i, (support_a0, support_a1) in enumerate(support_ranges):
        carcass.visual(
            mesh_from_cadquery(
                _sector(
                    r.outer_r - 0.006,
                    r.outer_r + 0.019,
                    support_a0,
                    support_a1,
                    r.z_top + 0.032,
                    0.010,
                    1.0,
                    48,
                ),
                f"carrier_bearing_track_{i}",
            ),
            material=mats["hardware"],
            name=f"carrier_bearing_track_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
        )
    door.visual(
        mesh_from_cadquery(
            _sector(
                r.outer_r - 0.009,
                r.outer_r - 0.004,
                moving_a0 + 3.0,
                moving_a1 - 3.0,
                r.z_base + 0.045,
                r.z_top - r.z_base - 0.090,
                r.ry_scale,
                34,
            ),
            "panel_field",
        ),
        material=mats["panel"],
        name="panel_field", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
    )
    track_name = "tambour_track" if r.facade_profile == "tambour_side_door_drawers" else "arc_track"
    for suffix, z in (("lower", r.z_base - 0.002),):
        carcass.visual(
            mesh_from_cadquery(
                _sector(
                    r.outer_r - 0.006,
                    r.outer_r + 0.018,
                    a0 - 12.0,
                    a1 + 12.0,
                    z,
                    0.010,
                    r.ry_scale,
                    50,
                ),
                f"{track_name}_{suffix}",
            ),
            material=mats["trim"],
            name=f"{track_name}_{suffix}", material_class_id=("metal.brass_aged" if r.palette_style in {"charcoal_brass", "walnut_bronze", "sage_pewter", "ebony_pearl"} else "metal.brass_polished"),
        )
    limits = MotionLimits(
        effort=18.0,
        velocity=0.8,
        lower=0.0,
        upper=math.radians(14.0 if "arc_slide" in r.facade_profile else 35.0),
    )
    model.articulation(
        "body_to_cabinet_door_0",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=Origin(xyz=origin),
        axis=(0.0, 0.0, axis_z),
        motion_limits=limits,
        mating=MatingContract(
            parent_face_geometry="carrier_bearing_track_0",
            parent_face_side="positive_z",
            child_face_geometry="carrier_bearing_ring",
            child_face_side="negative_z",
            contact_tol=0.002,
        ),
        meta={"mechanism": "concentric guided curved closure; not a linear slide"},
    )


def _drawer_tray(r: ResolvedRoundCabinetConfig, z0: float) -> cq.Workplane:
    a0, a1 = r.drawer_a0, r.drawer_a1
    h = r.drawer_height
    front = _sector(r.outer_r - 0.050, r.outer_r - 0.018, a0, a1, z0, h, r.ry_scale, 42)
    bottom = _sector(r.outer_r * 0.25, r.outer_r - 0.035, a0, a1, z0 + 0.006, 0.012, r.ry_scale, 42)
    rear = _sector(
        r.outer_r * 0.26, r.outer_r * 0.32, a0, a1, z0 + 0.006, max(0.06, h - 0.035), r.ry_scale, 28
    )
    side0 = _sector(
        r.outer_r * 0.25,
        r.outer_r - 0.035,
        a0 - 0.5,
        a0 + 3.0,
        z0 + 0.006,
        max(0.06, h - 0.035),
        r.ry_scale,
        6,
    )
    side1 = _sector(
        r.outer_r * 0.25,
        r.outer_r - 0.035,
        a1 - 3.0,
        a1 + 0.5,
        z0 + 0.006,
        max(0.06, h - 0.035),
        r.ry_scale,
        6,
    )
    return front.union(bottom).union(rear).union(side0).union(side1)


def _emit_drawers(
    model: ArticulatedObject, carcass, r: ResolvedRoundCabinetConfig, mats: dict[str, object]
) -> None:
    center = math.radians((r.drawer_a0 + r.drawer_a1) / 2.0)
    axis = (math.cos(center), math.sin(center) * r.ry_scale, 0.0)
    norm = math.hypot(axis[0], axis[1])
    axis = (axis[0] / norm, axis[1] / norm, 0.0)
    tangent = (-axis[1], axis[0])
    rail_center_radius = r.outer_r * 0.55
    glide_half_width = r.outer_r * 0.18
    glide_length = r.outer_r * 0.45
    yaw = math.atan2(axis[1], axis[0])
    for i, z0 in enumerate(r.drawer_z):
        origin = (
            r.outer_r * 0.50 * axis[0],
            r.outer_r * 0.50 * axis[1],
            z0 + r.drawer_height / 2.0,
        )
        drawer = model.part(f"drawer_{i}")
        drawer.visual(
            mesh_from_cadquery(_localize(_drawer_tray(r, z0), origin), "drawer_tray"),
            material=mats["interior"],
            name="drawer_tray", material_class_id="wood.plywood",
        )
        for side, s in (("left", -1.0), ("right", 1.0)):
            gx = rail_center_radius * axis[0] + s * glide_half_width * tangent[0]
            gy = rail_center_radius * axis[1] + s * glide_half_width * tangent[1]
            drawer.visual(
                Box((glide_length, 0.012, 0.006)),
                origin=Origin(
                    xyz=(gx - origin[0], gy - origin[1], z0 + 0.003 - origin[2]),
                    rpy=(0.0, 0.0, yaw),
                ),
                material=mats["trim"],
                name=f"drawer_glide_{side}", material_class_id=("metal.brass_aged" if r.palette_style in {"charcoal_brass", "walnut_bronze", "sage_pewter", "ebony_pearl"} else "metal.brass_polished"),
            )
        drawer.visual(
            mesh_from_cadquery(
                _localize(
                    _sector(
                        r.outer_r - 0.018,
                        r.outer_r - 0.008,
                        r.drawer_a0 + 4.0,
                        r.drawer_a1 - 4.0,
                        z0 + 0.018,
                        r.drawer_height - 0.036,
                        r.ry_scale,
                        36,
                    ),
                    origin,
                ),
                "drawer_front_field",
            ),
            material=mats["panel"],
            name="drawer_front_field", material_class_id=("wood.painted_clean" if r.palette_style in {"charcoal_brass", "walnut_bronze", "ivory_gold", "sage_pewter"} else "wood.polished_varnished"),
        )
        for j, offset in enumerate((-0.20, 0.20)):
            handle_a = (r.drawer_a0 + r.drawer_a1) / 2.0 + offset * (r.drawer_a1 - r.drawer_a0)
            drawer.visual(
                Sphere(radius=0.010),
                origin=Origin(
                    xyz=(
                        (r.outer_r - 0.001) * math.cos(math.radians(handle_a)) - origin[0],
                        (r.outer_r - 0.001) * r.ry_scale * math.sin(math.radians(handle_a))
                        - origin[1],
                        0.0,
                    )
                ),
                material=mats["hardware"],
                name=f"drawer_pull_{j}", material_class_id=("metal.brass_polished" if r.palette_style in {"charcoal_brass", "ivory_gold", "sage_pewter", "ebony_pearl"} else "metal.bronze_cast"),
            )
        drawer.inertial = Inertial.from_geometry(
            Box((r.outer_r * 0.55, r.outer_r * 0.55, r.drawer_height)), mass=3.2
        )
        model.articulation(
            f"body_to_drawer_{i}",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=drawer,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=MotionLimits(
                effort=70.0, velocity=0.35, lower=0.0, upper=r.drawer_travel
            ),
            mating=MatingContract(
                parent_face_geometry=f"drawer_rail_{i}_left",
                parent_face_side="positive_z",
                child_face_geometry="drawer_glide_left",
                child_face_side="negative_z",
                contact_tol=0.020,
            ),
            meta={"mechanism": "complete open-top tray on bilateral longitudinal rails"},
        )


def build_round_cabinet(
    config: RoundCabinetConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Round_cabinet", "mechanism_profile": r.facade_profile},
    )
    palette = PALETTES[r.palette_style]
    mats = {role: model.material(f"round_cabinet_{role}", rgba=palette[role]) for role in palette}
    carcass = model.part("carcass")
    _emit_carcass(carcass, r, mats)
    carcass.inertial = Inertial.from_geometry(
        Box((2 * r.outer_r, 2 * r.outer_r * r.ry_scale, r.height)), mass=45.0
    )
    _emit_base(model, carcass, r, mats)
    _emit_closures(model, carcass, r, mats)
    _emit_drawers(model, carcass, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_round_cabinet(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_round_cabinet(config_from_seed(seed), assets=assets)


def run_round_cabinet_tests(
    object_model: ArticulatedObject, config: RoundCabinetConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    names = {p.name for p in object_model.parts}
    ctx.check("category binding retained", object_model.meta.get("category") == "Round_cabinet")
    ctx.check("carcass present", "carcass" in names)
    carcass = object_model.get_part("carcass")
    carcass_visuals = {visual.name for visual in carcass.visuals}
    if r.base_profile == "tapered_legs":
        for i in range(3):
            ctx.check(f"load-bearing tapered leg {i} present", f"leg_{i}" in carcass_visuals)
            ctx.check(f"leg foot tip {i} present", f"foot_tip_{i}" in carcass_visuals)
        ctx.check("pedestal excluded from leg profile", "pedestal" not in names)
    else:
        ctx.check("rotating pedestal retained", "pedestal" in names)
        ctx.check("leg geometry excluded from pedestal profile", "leg_0" not in carcass_visuals)
    expected_doors = 2 if r.facade_profile == "paired_curved_doors" else 1
    ctx.check(
        "facade gate controls drawer bank",
        r.drawer_count == (0 if expected_doors == 2 else config.drawer_count),
    )
    for i in range(expected_doors):
        ctx.check(f"door {i} complete", f"cabinet_door_{i}" in names)
    for i in range(r.drawer_count):
        drawer = object_model.get_part(f"drawer_{i}")
        ctx.check(f"drawer {i} is complete tray", drawer.get_visual("drawer_tray") is not None)
        joint = object_model.get_articulation(f"body_to_drawer_{i}")
        rest = ctx.part_world_position(drawer)
        with ctx.pose({joint: joint.motion_limits.upper}):
            moved = ctx.part_world_position(drawer)
        travel = (
            None
            if rest is None or moved is None
            else sum((moved[k] - rest[k]) * joint.axis[k] for k in range(3))
        )
        ctx.check(
            f"drawer {i} travels outward",
            travel is not None and travel > 0.17,
            details=f"rest={rest}, moved={moved}, travel={travel}",
        )
    # No overlap allowance is declared here: every moving element remains collision-tested.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.035)
    return ctx.report()


__all__ = [
    "RoundCabinetConfig",
    "ResolvedRoundCabinetConfig",
    "build_round_cabinet",
    "build_seeded_round_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_round_cabinet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
