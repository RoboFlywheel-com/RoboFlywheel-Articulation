# SPDX-License-Identifier: Apache-2.0

"""Self-contained round dining table with a lazy-susan turntable.

One rigid ``tabletop`` root carries the round slab, its edge band, the circular
apron, the radial underframe and every support mount.  A single
``turntable_tray`` is a REVOLUTE (+z) child of that root, spinning on a central
bearing; it is continuous in practice, so its limits run -pi..+pi.

``tray_build`` changes what sits on the bearing together with the matching host
feature it needs (pocket and lip, detent ring, annular race, roller retainer,
lower shelf).  ``base_build`` is one structural family of table bases carrying
``support_count`` members: hinged folding legs, or a central column whose hub
spreads the same number of feet.

No source-replay import, no motion clamping, no whole-part overlap allowance.
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
    ExtrudeGeometry,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

TrayBuild = Literal[
    "woven_lattice",
    "flush_recessed",
    "raised_guard_rim",
    "two_tier",
    "segmented_wedge",
]
BearingBuild = Literal[
    "race_and_plate",
    "ring_and_hub",
    "roller_retainer",
    "detent_index",
]
BaseBuild = Literal["folding_legs", "pedestal_column", "tripod_pedestal"]
PaletteStyle = Literal["pale_oak", "walnut", "ivory", "graphite"]

TRAY_BUILDS: tuple[TrayBuild, ...] = (
    "woven_lattice",
    "flush_recessed",
    "raised_guard_rim",
    "two_tier",
    "segmented_wedge",
)
BEARING_BUILDS: tuple[BearingBuild, ...] = (
    "race_and_plate",
    "ring_and_hub",
    "roller_retainer",
    "detent_index",
)
BASE_BUILDS: tuple[BaseBuild, ...] = ("folding_legs", "pedestal_column", "tripod_pedestal")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("pale_oak", "walnut", "ivory", "graphite")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("tray_build", TRAY_BUILDS),
        component_slot("bearing_build", BEARING_BUILDS),
        component_slot("base_build", BASE_BUILDS),
        multiplicity_slot("support_count", (3, 4, 6), item_slot="base_build"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "pale_oak": {
        "wood": (0.78, 0.72, 0.62, 1.0),
        "edge": (0.63, 0.55, 0.45, 1.0),
        "tray": (0.55, 0.54, 0.50, 1.0),
        "seam": (0.24, 0.24, 0.23, 1.0),
        "metal": (0.82, 0.81, 0.76, 1.0),
        "steel": (0.48, 0.50, 0.50, 1.0),
        "accent": (0.66, 0.49, 0.22, 1.0),
        "rubber": (0.045, 0.05, 0.05, 1.0),
    },
    "walnut": {
        "wood": (0.38, 0.25, 0.16, 1.0),
        "edge": (0.27, 0.17, 0.11, 1.0),
        "tray": (0.46, 0.33, 0.24, 1.0),
        "seam": (0.18, 0.12, 0.09, 1.0),
        "metal": (0.30, 0.29, 0.28, 1.0),
        "steel": (0.44, 0.45, 0.46, 1.0),
        "accent": (0.72, 0.58, 0.30, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "ivory": {
        "wood": (0.90, 0.88, 0.83, 1.0),
        "edge": (0.76, 0.73, 0.67, 1.0),
        "tray": (0.84, 0.82, 0.78, 1.0),
        "seam": (0.42, 0.41, 0.39, 1.0),
        "metal": (0.88, 0.87, 0.84, 1.0),
        "steel": (0.58, 0.59, 0.60, 1.0),
        "accent": (0.72, 0.66, 0.50, 1.0),
        "rubber": (0.08, 0.08, 0.08, 1.0),
    },
    "graphite": {
        "wood": (0.26, 0.26, 0.27, 1.0),
        "edge": (0.17, 0.17, 0.18, 1.0),
        "tray": (0.33, 0.33, 0.34, 1.0),
        "seam": (0.11, 0.11, 0.12, 1.0),
        "metal": (0.22, 0.23, 0.24, 1.0),
        "steel": (0.52, 0.53, 0.54, 1.0),
        "accent": (0.60, 0.62, 0.64, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
}

TOP_T = 0.036  # tabletop slab thickness
EDGE_H = 0.018  # edge band height
APRON_H = 0.059  # circular apron depth
FRAME_T = 0.028  # radial frame rail thickness
HINGE_INSET = 0.150  # support mount inset from the tabletop rim
TRAY_GAP = 0.0005  # running gap between tray and its bearing race
MOUNT = 0.0008  # intra-part embedment so one part stays one island
YOKE_Y = 0.026  # half spacing of every bearing yoke cheek
BEARING_RISE = 0.0115  # every host bearing feature tops out this far above the top


@dataclass(frozen=True)
class Config:
    tray_build: TrayBuild = "woven_lattice"
    bearing_build: BearingBuild = "race_and_plate"
    base_build: BaseBuild = "folding_legs"
    support_count: int = 4
    table_diameter_m: float | None = None
    tray_diameter_ratio: float | None = None
    table_height_m: float | None = None
    palette_style: PaletteStyle = "pale_oak"
    name: str = "pictureX_0611_Folding_table4"


@dataclass(frozen=True)
class ResolvedConfig:
    tray_build: TrayBuild
    bearing_build: BearingBuild
    base_build: BaseBuild
    support_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    table_diameter_m: float
    tray_diameter_ratio: float
    table_height_m: float
    table_radius_m: float
    tray_radius_m: float
    hinge_radius_m: float
    top_z: float
    under_z: float
    frame_z: float
    hinge_z: float
    support_drop_m: float
    bearing_radius_m: float
    bearing_top_z: float
    tray_mount_z: float
    leg_fold_rad: float
    shelf_radius_m: float
    tray_thick_m: float
    angles: tuple[float, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x0F74_2204)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        tray_build=choices["tray_build"],
        bearing_build=choices["bearing_build"],
        base_build=choices["base_build"],
        support_count=choices["support_count"],
        table_diameter_m=round(rng.uniform(1.00, 1.45), 4),
        tray_diameter_ratio=round(rng.uniform(0.55, 0.72), 4),
        table_height_m=round(rng.uniform(0.68, 0.78), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_table4_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "tray_build": config.tray_build,
            "bearing_build": config.bearing_build,
            "base_build": config.base_build,
            "support_count": config.support_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.table_diameter_m is not None and not 1.00 <= float(config.table_diameter_m) <= 1.45:
        raise ValueError("table_diameter_m must be in [1.00, 1.45]")
    if config.tray_diameter_ratio is not None and not (
        0.55 <= float(config.tray_diameter_ratio) <= 0.72
    ):
        raise ValueError("tray_diameter_ratio must be in [0.55, 0.72]")
    if config.table_height_m is not None and not 0.68 <= float(config.table_height_m) <= 0.78:
        raise ValueError("table_height_m must be in [0.68, 0.78]")

    diameter = (
        _clamp(config.table_diameter_m, 1.00, 1.45) if config.table_diameter_m is not None else 1.20
    )
    ratio = (
        _clamp(config.tray_diameter_ratio, 0.55, 0.72)
        if config.tray_diameter_ratio is not None
        else 0.667
    )
    height = (
        _clamp(config.table_height_m, 0.68, 0.78) if config.table_height_m is not None else 0.72
    )

    radius = diameter * 0.5
    tray_radius = diameter * ratio * 0.5
    hinge_radius = radius - HINGE_INSET
    top_z = height - TOP_T * 0.5
    under_z = height - TOP_T
    frame_z = under_z - FRAME_T * 0.5
    hinge_z = under_z - 0.052
    support_drop = hinge_z - 0.012
    bearing_radius = _clamp(tray_radius * 0.16, 0.050, 0.090)
    tray_thick = 0.016
    # Every host bearing feature tops out here, so one tray mount height fits
    # all eight trays; the recessed tray drops the whole stack into its pocket.
    bearing_top = height + BEARING_RISE
    shelf_radius = tray_radius * 0.60
    if config.tray_build == "flush_recessed":
        bearing_top = height - TOP_T + 0.012 + 0.014
    tray_mount = bearing_top + TRAY_GAP
    # The foot pad, not the tube, is the outermost point that swings inward.
    foot_reach = support_drop - 0.008
    floor_radius = 0.090
    if config.tray_build == "two_tier":
        floor_radius = max(floor_radius, shelf_radius + 0.060)
    leg_fold = math.asin(_clamp((hinge_radius - floor_radius) / max(foot_reach, 0.05), 0.15, 0.95))

    n = int(config.support_count)
    angles = tuple(2.0 * math.pi * i / n for i in range(n))

    return ResolvedConfig(
        tray_build=config.tray_build,
        bearing_build=config.bearing_build,
        base_build=config.base_build,
        support_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        table_diameter_m=diameter,
        tray_diameter_ratio=ratio,
        table_height_m=height,
        table_radius_m=radius,
        tray_radius_m=tray_radius,
        hinge_radius_m=hinge_radius,
        top_z=top_z,
        under_z=under_z,
        frame_z=frame_z,
        hinge_z=hinge_z,
        support_drop_m=support_drop,
        bearing_radius_m=bearing_radius,
        bearing_top_z=bearing_top,
        tray_mount_z=tray_mount,
        leg_fold_rad=leg_fold,
        shelf_radius_m=shelf_radius,
        tray_thick_m=tray_thick,
        angles=angles,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("tray_build", config.tray_build),
        ("bearing_build", config.bearing_build),
        ("base_build", config.base_build),
        ("support_count", config.support_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --- geometry helpers -------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"ft4_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"ft4_{r.palette_style}_{key}"
    return mats


def _ring_profile(inner: float, outer: float, height: float) -> LatheGeometry:
    """Lathed annulus, so a race or rim is a real ring rather than a disc."""
    return LatheGeometry(
        [(inner, 0.0), (outer, 0.0), (outer, height), (inner, height), (inner, 0.0)],
        segments=48,
    )


def _sloped_bar(part, p0, p1, width: float, thick: float, material: str, name: str) -> None:
    """Box beam running from p0 to p1 in the part's own frame."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    yaw = math.atan2(dy, dx)
    pitch = -math.atan2(dz, math.hypot(dx, dy))
    part.visual(
        Box((length, width, thick)),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _pedestal_foot_shoulder(
    part,
    *,
    width: float,
    inner_height: float,
    outer_height: float,
    material: str,
    name: str,
) -> None:
    """Make the cast-in shoulder that blends a radial foot into the hub.

    The foot parts are mounted at the hub radius, so starting the long arm at
    that tangent point leaves a visually sharp seam.  This shallow tapered
    socket overlaps the hub by only 4 mm, then feathers into the arm.  It
    keeps the load path readable without turning the separate support part
    into a large penetrating block.
    """
    profile = [
        (-0.004, -inner_height * 0.5),
        (0.010, -inner_height * 0.5),
        (0.058, -outer_height * 0.5),
        (0.058, outer_height * 0.5),
        (0.010, inner_height * 0.5),
        (-0.004, inner_height * 0.5),
    ]
    shoulder = ExtrudeGeometry(profile, width, center=True)
    shoulder = shoulder.rotate_x(math.pi / 2.0)
    part.visual(
        mesh_from_geometry(shoulder, f"{name}_mesh"),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _wedge_polygon(radius: float, start: float, end: float, segments: int = 12):
    points = [(0.0, 0.0)]
    for i in range(segments + 1):
        a = start + (end - start) * i / segments
        points.append((radius * math.cos(a), radius * math.sin(a)))
    return points


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    child_axis: tuple[float, float, float] = (0.0, 1.0, 0.0),
    child_radial: tuple[float, float, float] = (1.0, 0.0, 0.0),
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    meta: dict | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=child_axis, radial=child_radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


# --- tabletop and its per-tray host feature ---------------------------------
def _build_tabletop(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    top = model.part("tabletop", meta={"role": "tabletop"})
    kind = r.tray_build

    # The slab is a ring when the tray drops into a pocket, a full disc otherwise.
    if kind == "flush_recessed":
        pocket_r = r.tray_radius_m + 0.006
        top.visual(
            mesh_from_geometry(
                _ring_profile(pocket_r, r.table_radius_m, TOP_T),
                "tabletop_slab_ring_mesh",
            ),
            origin=Origin(xyz=(0.0, 0.0, r.under_z)),
            material=mats["wood"],
            name=f"tray_build__{kind}__round_top", material_class_id=("wood.oak" if r.palette_style in {"pale_oak", "ivory", "graphite"} else "wood.walnut_dark"),
        )
        # Pocket floor the recessed tray sits in, plus its bearing lip.
        top.visual(
            Cylinder(radius=pocket_r + 0.004, length=0.012),
            origin=Origin(xyz=(0.0, 0.0, r.under_z + 0.006 - MOUNT)),
            material=mats["wood"],
            name=f"tray_build__{kind}__pocket_floor", material_class_id=("wood.oak" if r.palette_style in {"pale_oak", "ivory", "graphite"} else "wood.walnut_dark"),
        )
        top.visual(
            mesh_from_geometry(
                _ring_profile(pocket_r - 0.010, pocket_r, 0.010),
                "bearing_lip_mesh",
            ),
            origin=Origin(xyz=(0.0, 0.0, r.under_z + 0.012 - MOUNT)),
            material=mats["metal"],
            name=f"tray_build__{kind}__bearing_lip", material_class_id="metal.stainless_matte",
        )
    else:
        top.visual(
            Cylinder(radius=r.table_radius_m, length=TOP_T),
            origin=Origin(xyz=(0.0, 0.0, r.top_z)),
            material=mats["wood"],
            name=f"tray_build__{kind}__round_top", material_class_id=("wood.oak" if r.palette_style in {"pale_oak", "ivory", "graphite"} else "wood.walnut_dark"),
        )
    top.visual(
        mesh_from_geometry(
            _ring_profile(r.table_radius_m - 0.006, r.table_radius_m + 0.001, EDGE_H),
            "edge_band_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.under_z - EDGE_H + 0.004)),
        material=mats["edge"],
        name="outer_edge_band", material_class_id="wood.veneer_panel",
    )
    top.visual(
        mesh_from_geometry(
            _ring_profile(r.table_radius_m - 0.115, r.table_radius_m - 0.085, APRON_H),
            "circular_apron_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.under_z - APRON_H + MOUNT)),
        material=mats["wood"],
        name="circular_apron", material_class_id=("wood.oak" if r.palette_style in {"pale_oak", "ivory", "graphite"} else "wood.walnut_dark"),
    )

    # Radial frame rails tie the centre bearing out to every support mount.
    for i, theta in enumerate(r.angles):
        length = r.hinge_radius_m + 0.060
        top.visual(
            Box((length, 0.038, FRAME_T)),
            origin=Origin(
                xyz=(
                    length * 0.5 * math.cos(theta),
                    length * 0.5 * math.sin(theta),
                    r.frame_z,
                ),
                rpy=(0.0, 0.0, theta),
            ),
            material=mats["metal"],
            name=f"frame_rail_{i}", material_class_id="metal.paint_coated",
        )

    if kind == "two_tier":
        shelf_r = r.tray_radius_m * 0.60
        top.visual(
            Cylinder(radius=shelf_r, length=0.020),
            origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.100)),
            material=mats["wood"],
            name=f"tray_build__{kind}__lower_shelf_top", material_class_id=("wood.oak" if r.palette_style in {"pale_oak", "ivory", "graphite"} else "wood.walnut_dark"),
        )
        top.visual(
            mesh_from_geometry(
                _ring_profile(shelf_r - 0.008, shelf_r + 0.002, 0.014), "shelf_band_mesh"
            ),
            origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.107)),
            material=mats["edge"],
            name=f"tray_build__{kind}__lower_shelf_edge_band", material_class_id="wood.veneer_panel",
        )
        top.visual(
            Cylinder(radius=r.bearing_radius_m * 0.7, length=0.056),
            origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.062)),
            material=mats["metal"],
            name=f"tray_build__{kind}__shelf_stem", material_class_id="metal.paint_coated",
        )
    return top


# --- bearing candidates -----------------------------------------------------
def _bearing_pedestal_host(top, r: ResolvedConfig, mats) -> None:
    """Central pedestal and flat race that three of the four bearings share."""
    top.visual(
        Cylinder(radius=r.bearing_radius_m, length=0.094),
        origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.047 + MOUNT)),
        material=mats["metal"],
        name="bearing_pedestal", material_class_id="metal.paint_coated",
    )
    top.visual(
        Cylinder(radius=r.bearing_radius_m * 0.86, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.012)),
        material=mats["steel"],
        name="bearing_race", material_class_id="metal.stainless_matte",
    )


def _bearing_build_race_and_plate_build(top, tray, r: ResolvedConfig, mats) -> None:
    """Plain flat race carrying the tray's bearing plate directly, as in 001."""
    _bearing_pedestal_host(top, r, mats)


def _bearing_build_ring_and_hub_build(top, tray, r: ResolvedConfig, mats) -> None:
    """Wide annular race on a short column, met by a spoked tray hub plate."""
    race_r = r.tray_radius_m * 0.62
    top.visual(
        Cylinder(radius=r.bearing_radius_m * 0.55, length=0.070),
        origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.035 + MOUNT)),
        material=mats["metal"],
        name="bearing_build__ring_and_hub__bearing_column", material_class_id="metal.paint_coated",
    )
    top.visual(
        mesh_from_geometry(_ring_profile(race_r - 0.020, race_r, 0.020), "bearing_ring_mesh"),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.020)),
        material=mats["steel"],
        name="bearing_build__ring_and_hub__bearing_ring", material_class_id="metal.stainless_matte",
    )
    for i in range(6):
        a = 2.0 * math.pi * i / 6.0
        top.visual(
            Box((race_r - r.bearing_radius_m * 0.5, 0.026, 0.010)),
            origin=Origin(
                xyz=(
                    (race_r + r.bearing_radius_m * 0.5) * 0.5 * math.cos(a),
                    (race_r + r.bearing_radius_m * 0.5) * 0.5 * math.sin(a),
                    r.bearing_top_z - 0.018,
                ),
                rpy=(0.0, 0.0, a),
            ),
            material=mats["metal"],
            name=f"bearing_build__ring_and_hub__race_spoke_{i}", material_class_id="metal.paint_coated",
        )
    top.visual(
        Cylinder(radius=r.bearing_radius_m * 0.55, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.015)),
        material=mats["steel"],
        name="bearing_build__ring_and_hub__centre_boss", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        mesh_from_geometry(_ring_profile(race_r - 0.024, race_r + 0.004, 0.010), "hub_plate_mesh"),
        origin=Origin(xyz=(0.0, 0.0, 0.001)),
        material=mats["steel"],
        name="bearing_build__ring_and_hub__hub_plate", material_class_id="metal.stainless_matte",
    )
    for i in range(4):
        a = 2.0 * math.pi * i / 4.0
        tray.visual(
            Box((race_r, 0.020, 0.008)),
            origin=Origin(
                xyz=(race_r * 0.5 * math.cos(a), race_r * 0.5 * math.sin(a), 0.005),
                rpy=(0.0, 0.0, a),
            ),
            material=mats["steel"],
            name=f"bearing_build__ring_and_hub__hub_spoke_{i}", material_class_id="metal.stainless_matte",
        )


def _bearing_build_roller_retainer_build(top, tray, r: ResolvedConfig, mats) -> None:
    """Caged rollers running between the race and a tray-side track."""
    _bearing_pedestal_host(top, r, mats)
    retain_r = r.bearing_radius_m + 0.030
    top.visual(
        mesh_from_geometry(
            _ring_profile(retain_r - 0.014, retain_r, 0.014), "roller_retainer_mesh"
        ),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.020)),
        material=mats["steel"],
        name="bearing_build__roller_retainer__roller_retainer_ring", material_class_id="metal.stainless_matte",
    )
    for i in range(12):
        a = 2.0 * math.pi * i / 12.0
        top.visual(
            Sphere(radius=0.006),
            origin=Origin(
                xyz=(
                    (retain_r - 0.007) * math.cos(a),
                    (retain_r - 0.007) * math.sin(a),
                    r.bearing_top_z - 0.006,
                )
            ),
            material=mats["accent"],
            name=f"bearing_build__roller_retainer__roller_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"pale_oak", "walnut", "ivory"} else "metal.stainless_matte"),
        )
    top.visual(
        Box((retain_r, 0.020, 0.006)),
        origin=Origin(xyz=(retain_r * 0.5, 0.0, r.bearing_top_z - 0.017)),
        material=mats["steel"],
        name="bearing_build__roller_retainer__retainer_spoke", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        mesh_from_geometry(
            _ring_profile(retain_r - 0.016, retain_r + 0.004, 0.008), "roller_track_mesh"
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.001)),
        material=mats["steel"],
        name="bearing_build__roller_retainer__roller_track", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        Cylinder(radius=retain_r - 0.014, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, 0.0025)),
        material=mats["steel"],
        name="bearing_build__roller_retainer__track_web", material_class_id="metal.stainless_matte",
    )


def _bearing_build_detent_index_build(top, tray, r: ResolvedConfig, mats) -> None:
    """Pocketed detent ring indexed by a spring pin carried on the tray."""
    _bearing_pedestal_host(top, r, mats)
    detent_r = r.tray_radius_m * 0.55
    top.visual(
        mesh_from_geometry(_ring_profile(detent_r - 0.018, detent_r, 0.024), "detent_ring_mesh"),
        origin=Origin(xyz=(0.0, 0.0, r.bearing_top_z - 0.024)),
        material=mats["steel"],
        name="bearing_build__detent_index__detent_ring", material_class_id="metal.stainless_matte",
    )
    for i in range(12):
        a = 2.0 * math.pi * i / 12.0
        top.visual(
            Cylinder(radius=0.0055, length=0.010),
            origin=Origin(
                xyz=(
                    (detent_r - 0.009) * math.cos(a),
                    (detent_r - 0.009) * math.sin(a),
                    r.bearing_top_z - 0.011,
                )
            ),
            material=mats["accent"],
            name=f"bearing_build__detent_index__detent_pocket_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"pale_oak", "walnut", "ivory"} else "metal.stainless_matte"),
        )
    top.visual(
        Box((detent_r, 0.022, 0.008)),
        origin=Origin(xyz=(detent_r * 0.5, 0.0, r.bearing_top_z - 0.020)),
        material=mats["steel"],
        name="bearing_build__detent_index__detent_spoke", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        Box((0.030, 0.024, 0.020)),
        origin=Origin(xyz=(detent_r - 0.009, 0.0, 0.011)),
        material=mats["steel"],
        name="bearing_build__detent_index__spring_pin_housing", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        Cylinder(radius=0.0050, length=0.010),
        origin=Origin(xyz=(detent_r - 0.009, 0.0, 0.005)),
        material=mats["accent"],
        name="bearing_build__detent_index__spring_pin_tip", material_class_id=("metal.brass_aged" if r.palette_style in {"pale_oak", "walnut", "ivory"} else "metal.stainless_matte"),
    )
    tray.visual(
        Cylinder(radius=0.0045, length=0.006),
        origin=Origin(xyz=(detent_r - 0.009, 0.0, 0.024)),
        material=mats["steel"],
        name="bearing_build__detent_index__pin_set_screw", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        Box((detent_r, 0.018, 0.006)),
        origin=Origin(xyz=(detent_r * 0.5, 0.0, 0.014)),
        material=mats["steel"],
        name="bearing_build__detent_index__pin_spoke", material_class_id="metal.stainless_matte",
    )


_BEARING_BUILDERS = {
    "race_and_plate": _bearing_build_race_and_plate_build,
    "ring_and_hub": _bearing_build_ring_and_hub_build,
    "roller_retainer": _bearing_build_roller_retainer_build,
    "detent_index": _bearing_build_detent_index_build,
}


def _build_bearing(top, tray, r: ResolvedConfig, mats: dict[str, str]) -> None:
    _BEARING_BUILDERS[r.bearing_build](top, tray, r, mats)


# --- turntable tray candidates ----------------------------------------------
def _tray_common(tray, r: ResolvedConfig, mats: dict[str, str], kind: str) -> None:
    """Bearing plate and centre cap every tray shares."""
    tray.visual(
        Cylinder(radius=r.bearing_radius_m * 0.92, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, 0.004)),
        material=mats["steel"],
        name="bearing_plate", material_class_id="metal.stainless_matte",
    )
    tray.visual(
        Cylinder(radius=r.tray_radius_m * 0.085, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m - 0.002)),
        material=mats["accent"],
        name="center_cap", material_class_id=("metal.brass_aged" if r.palette_style in {"pale_oak", "walnut", "ivory"} else "metal.stainless_matte"),
    )


def _tray_disc(tray, r: ResolvedConfig, mats: dict[str, str], kind: str, radius: float) -> None:
    tray.visual(
        Cylinder(radius=radius, length=r.tray_thick_m),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m * 0.5)),
        material=mats["tray"],
        name=f"tray_build__{kind}__tray_base", material_class_id="wood.polished_varnished",
    )
    tray.visual(
        mesh_from_geometry(
            _ring_profile(radius - 0.010, radius + 0.002, r.tray_thick_m + 0.002),
            f"tray_seam_mesh_{kind}",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["seam"],
        name=f"tray_build__{kind}__edge_seam", material_class_id="wood.patterned_decorative",
    )


def _tray_build_woven_lattice_build(tray, r, mats):
    _tray_disc(tray, r, mats, "woven_lattice", r.tray_radius_m)
    lattice_r = r.tray_radius_m * 0.94
    step = lattice_r / 5.0
    for axis_index, yaw in enumerate((0.0, math.pi / 2.0)):
        for line_index in range(-4, 5):
            offset = line_index * step
            chord = 2.0 * math.sqrt(max(lattice_r * lattice_r - offset * offset, 1e-6))
            x, y = (0.0, offset) if axis_index == 0 else (offset, 0.0)
            tray.visual(
                Box((chord, 0.004, 0.003)),
                origin=Origin(xyz=(x, y, r.tray_thick_m - 0.001), rpy=(0.0, 0.0, yaw)),
                material=mats["seam"],
                name=f"tray_build__woven_lattice__weave_{axis_index}_{line_index + 4}", material_class_id="wood.woven_plant_fiber",
            )


def _tray_build_flush_recessed_build(tray, r, mats):
    _tray_disc(tray, r, mats, "flush_recessed", r.tray_radius_m)
    # A shallow finger notch is the only way to lift a flush tray out.
    tray.visual(
        Cylinder(radius=r.tray_radius_m * 0.10, length=0.005),
        origin=Origin(xyz=(r.tray_radius_m * 0.62, 0.0, r.tray_thick_m - 0.001)),
        material=mats["seam"],
        name="tray_build__flush_recessed__finger_notch", material_class_id="wood.patterned_decorative",
    )
    tray.visual(
        Box((r.tray_radius_m * 0.62, 0.020, 0.004)),
        origin=Origin(xyz=(r.tray_radius_m * 0.31, 0.0, r.tray_thick_m - 0.001)),
        material=mats["seam"],
        name="tray_build__flush_recessed__notch_spoke", material_class_id="wood.patterned_decorative",
    )


def _tray_build_raised_guard_rim_build(tray, r, mats):
    _tray_disc(tray, r, mats, "raised_guard_rim", r.tray_radius_m)
    tray.visual(
        mesh_from_geometry(
            _ring_profile(r.tray_radius_m - 0.016, r.tray_radius_m, 0.040),
            "guard_rim_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m - MOUNT)),
        material=mats["tray"],
        name="tray_build__raised_guard_rim__retaining_rim", material_class_id="wood.polished_varnished",
    )
    tray.visual(
        mesh_from_geometry(
            _ring_profile(r.tray_radius_m - 0.018, r.tray_radius_m - 0.014, 0.008),
            "rim_inlay_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m + 0.026)),
        material=mats["accent"],
        name="tray_build__raised_guard_rim__rim_inlay", material_class_id=("metal.brass_aged" if r.palette_style in {"pale_oak", "walnut", "ivory"} else "metal.stainless_matte"),
    )


def _tray_build_two_tier_build(tray, r, mats):
    _tray_disc(tray, r, mats, "two_tier", r.tray_radius_m)
    upper_r = r.tray_radius_m * 0.58
    tray.visual(
        Cylinder(radius=upper_r, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m + 0.075)),
        material=mats["tray"],
        name="tray_build__two_tier__upper_tier", material_class_id="wood.polished_varnished",
    )
    tray.visual(
        mesh_from_geometry(
            _ring_profile(upper_r - 0.008, upper_r + 0.002, 0.012),
            "upper_tier_band_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m + 0.073)),
        material=mats["edge"],
        name="tray_build__two_tier__upper_tier_band", material_class_id="wood.veneer_panel",
    )
    tray.visual(
        Cylinder(radius=r.tray_radius_m * 0.10, length=0.078),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m + 0.037)),
        material=mats["metal"],
        name="tray_build__two_tier__tier_post", material_class_id="metal.paint_coated",
    )


def _tray_build_segmented_wedge_build(tray, r, mats):
    sectors = 6
    hub_r = r.tray_radius_m * 0.22
    tray.visual(
        Cylinder(radius=hub_r, length=r.tray_thick_m),
        origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m * 0.5)),
        material=mats["seam"],
        name="tray_build__segmented_wedge__sector_hub", material_class_id="wood.patterned_decorative",
    )
    for i in range(sectors):
        start = 2.0 * math.pi * i / sectors + 0.030
        end = 2.0 * math.pi * (i + 1) / sectors - 0.030
        tray.visual(
            mesh_from_geometry(
                ExtrudeGeometry(
                    _wedge_polygon(r.tray_radius_m, start, end), r.tray_thick_m, center=True
                ),
                f"tray_sector_mesh_{i}",
            ),
            origin=Origin(xyz=(0.0, 0.0, r.tray_thick_m * 0.5)),
            material=mats["tray"],
            name=f"tray_build__segmented_wedge__sector_{i}", material_class_id="wood.polished_varnished",
        )
    tray.visual(
        mesh_from_geometry(
            _ring_profile(r.tray_radius_m - 0.010, r.tray_radius_m + 0.002, r.tray_thick_m + 0.002),
            "tray_seam_mesh_segmented_wedge",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["seam"],
        name="tray_build__segmented_wedge__edge_seam", material_class_id="wood.patterned_decorative",
    )


_TRAY_BUILDERS = {
    "woven_lattice": _tray_build_woven_lattice_build,
    "flush_recessed": _tray_build_flush_recessed_build,
    "raised_guard_rim": _tray_build_raised_guard_rim_build,
    "two_tier": _tray_build_two_tier_build,
    "segmented_wedge": _tray_build_segmented_wedge_build,
}


def _build_tray(model: ArticulatedObject, top, r: ResolvedConfig, mats: dict[str, str]):
    tray = model.part(
        f"tray_build__{r.tray_build}__turntable_tray",
        meta={"role": "turntable_tray"},
    )
    _TRAY_BUILDERS[r.tray_build](tray, r, mats)
    _tray_common(tray, r, mats, r.tray_build)
    _axis_joint(
        model,
        name="tabletop_to_turntable_tray",
        parent=top,
        child=tray,
        point=(0.0, 0.0, r.tray_mount_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        child_axis=(0.0, 0.0, 1.0),
        child_radial=(1.0, 0.0, 0.0),
        lower=-math.pi,
        upper=math.pi,
        effort=8.0,
        velocity=2.5,
        meta={"positive_motion": "spins the lazy-susan tray anticlockwise"},
    )
    return tray


# --- base candidates --------------------------------------------------------
def _base_build_folding_legs_build(model, top, r: ResolvedConfig, mats) -> list:
    members = []
    for i, theta in enumerate(r.angles):
        hx = r.hinge_radius_m * math.cos(theta)
        hy = r.hinge_radius_m * math.sin(theta)
        # Fork-and-pin bracket: two ears straddle the leg barrel.
        top.visual(
            Box((0.105, 0.072, 0.020)),
            origin=Origin(xyz=(hx, hy, r.under_z - 0.014), rpy=(0.0, 0.0, theta)),
            material=mats["metal"],
            name=f"hinge_plate_{i}", material_class_id="metal.paint_coated",
        )
        for ear, sy in enumerate((-1.0, 1.0)):
            ex = hx - sy * (YOKE_Y + 0.005) * math.sin(theta)
            ey = hy + sy * (YOKE_Y + 0.005) * math.cos(theta)
            top.visual(
                Box((0.056, 0.010, 0.052)),
                origin=Origin(xyz=(ex, ey, r.hinge_z + 0.010), rpy=(0.0, 0.0, theta)),
                material=mats["metal"],
                name=f"hinge_ear_{i}_{ear}", material_class_id="metal.paint_coated",
            )
        leg = model.part(
            f"base_build__folding_legs__member_{i}",
            meta={"role": "support_member", "index": i},
        )
        leg.visual(
            Cylinder(radius=0.014, length=2.0 * (YOKE_Y + 0.005) - 0.011),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name=f"base_build__folding_legs__hinge_barrel_{i}", material_class_id="metal.paint_coated",
        )
        leg.visual(
            Box((0.042, 0.042, 0.055)),
            origin=Origin(xyz=(0.0, 0.0, -0.026)),
            material=mats["steel"],
            name=f"base_build__folding_legs__upper_collar_{i}", material_class_id="metal.stainless_matte",
        )
        tube_len = r.support_drop_m - 0.070
        leg.visual(
            Box((0.032, 0.032, tube_len)),
            origin=Origin(xyz=(0.0, 0.0, -0.050 - tube_len * 0.5)),
            material=mats["metal"],
            name=f"base_build__folding_legs__leg_tube_{i}", material_class_id="metal.paint_coated",
        )
        leg.visual(
            Box((0.038, 0.038, 0.024)),
            origin=Origin(xyz=(0.0, 0.0, -r.support_drop_m + 0.008)),
            material=mats["rubber"],
            name=f"base_build__folding_legs__foot_pad_{i}", material_class_id="rubber.smooth_plain",
        )
        _axis_joint(
            model,
            name=f"tabletop_to_support_member_{i}",
            parent=top,
            child=leg,
            point=(hx, hy, r.hinge_z),
            axis=(-math.sin(theta), math.cos(theta), 0.0),
            radial=(math.cos(theta), math.sin(theta), 0.0),
            lower=0.0,
            upper=r.leg_fold_rad,
            effort=45.0,
            velocity=1.2,
            meta={"positive_motion": "folds the leg inward under the top"},
        )
        members.append(leg)
    return members


def _pedestal_common(top, r: ResolvedConfig, mats, kind: str, column_r: float) -> float:
    """Central column hanging from the underframe; returns the hub top height."""
    hub_z = 0.075
    column_h = r.hinge_z - hub_z
    top.visual(
        Box((0.180, 0.180, 0.016)),
        origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.036)),
        material=mats["metal"],
        name=f"base_build__{kind}__mounting_plate", material_class_id="metal.paint_coated",
    )
    top.visual(
        Cylinder(radius=column_r * 1.30, length=0.030),
        origin=Origin(xyz=(0.0, 0.0, r.under_z - 0.055)),
        material=mats["metal"],
        name=f"base_build__{kind}__column_collar", material_class_id="metal.paint_coated",
    )
    top.visual(
        mesh_from_geometry(
            LatheGeometry(
                [
                    (0.0, 0.0),
                    (column_r, 0.0),
                    (column_r * 0.88, column_h * 0.5),
                    (column_r, column_h),
                    (0.0, column_h),
                ],
                segments=36,
            ),
            f"pedestal_column_mesh_{kind}",
        ),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=mats["metal"],
        name=f"base_build__{kind}__central_column", material_class_id="metal.paint_coated",
    )
    return hub_z


def _base_build_pedestal_column_build(model, top, r: ResolvedConfig, mats) -> list:
    members = []
    column_r = 0.062
    hub_z = _pedestal_common(top, r, mats, "pedestal_column", column_r)
    top.visual(
        Cylinder(radius=column_r * 1.55, length=0.040),
        origin=Origin(xyz=(0.0, 0.0, hub_z - 0.004)),
        material=mats["metal"],
        name="base_build__pedestal_column__base_hub", material_class_id="metal.paint_coated",
    )
    attach_r = column_r * 1.55
    attach_z = hub_z - 0.008
    for i, theta in enumerate(r.angles):
        foot = model.part(
            f"base_build__pedestal_column__member_{i}",
            meta={"role": "support_member", "index": i},
        )
        reach = r.table_radius_m * 0.46 - attach_r
        # A tapered cast socket makes the radial foot read as one load path
        # into the column hub instead of meeting it at a knife-edge tangent.
        _pedestal_foot_shoulder(
            foot,
            width=0.094,
            inner_height=0.046,
            outer_height=0.034,
            material=mats["metal"],
            name=f"base_build__pedestal_column__hub_shoulder_{i}",
        )
        # A cast lobe slopes from that shoulder down to its floor glide.
        _sloped_bar(
            foot,
            (0.0005, 0.0, 0.0),
            (reach, 0.0, 0.030 - attach_z),
            0.070,
            0.030,
            mats["metal"],
            f"base_build__pedestal_column__lobe_arm_{i}",
        )
        foot.visual(
            Box((0.096, 0.076, 0.026)),
            origin=Origin(xyz=(reach, 0.0, 0.026 - attach_z)),
            material=mats["metal"],
            name=f"base_build__pedestal_column__lobe_pad_{i}", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Cylinder(radius=0.030, length=0.016),
            origin=Origin(xyz=(reach, 0.0, 0.008 - attach_z)),
            material=mats["rubber"],
            name=f"base_build__pedestal_column__foot_glide_{i}", material_class_id="rubber.smooth_plain",
        )
        model.articulation(
            f"tabletop_to_support_member_{i}",
            ArticulationType.FIXED,
            parent=top,
            child=foot,
            origin=Origin(
                xyz=(attach_r * math.cos(theta), attach_r * math.sin(theta), attach_z),
                rpy=(0.0, 0.0, theta),
            ),
            meta={"mechanism": "lobe cast into the pedestal hub"},
        )
        members.append(foot)
    return members


def _base_build_tripod_pedestal_build(model, top, r: ResolvedConfig, mats) -> list:
    members = []
    column_r = 0.050
    hub_z = _pedestal_common(top, r, mats, "tripod_pedestal", column_r)
    top.visual(
        mesh_from_geometry(
            LatheGeometry(
                [(0.0, 0.0), (column_r * 1.7, 0.0), (column_r * 1.5, 0.034), (0.0, 0.040)],
                segments=30,
            ),
            "tripod_hub_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, hub_z - 0.014)),
        material=mats["metal"],
        name="base_build__tripod_pedestal__base_hub", material_class_id="metal.paint_coated",
    )
    attach_r = column_r * 1.70
    attach_z = hub_z - 0.010
    for i, theta in enumerate(r.angles):
        foot = model.part(
            f"base_build__tripod_pedestal__member_{i}",
            meta={"role": "support_member", "index": i},
        )
        reach = r.table_radius_m * 0.52 - attach_r
        # Give the tapered cast foot a short socket/shoulder at the column;
        # the old tangent-only start made the connection look detached.
        _pedestal_foot_shoulder(
            foot,
            width=0.080,
            inner_height=0.043,
            outer_height=0.030,
            material=mats["metal"],
            name=f"base_build__tripod_pedestal__hub_shoulder_{i}",
        )
        # A slender cast foot sweeps from the shoulder out to the floor.
        _sloped_bar(
            foot,
            (0.0005, 0.0, 0.0),
            (reach, 0.0, 0.024 - attach_z),
            0.052,
            0.026,
            mats["metal"],
            f"base_build__tripod_pedestal__cast_foot_{i}",
        )
        foot.visual(
            Box((0.070, 0.056, 0.022)),
            origin=Origin(xyz=(reach, 0.0, 0.022 - attach_z)),
            material=mats["metal"],
            name=f"base_build__tripod_pedestal__toe_pad_{i}", material_class_id="metal.paint_coated",
        )
        foot.visual(
            Cylinder(radius=0.024, length=0.016),
            origin=Origin(xyz=(reach, 0.0, 0.008 - attach_z)),
            material=mats["rubber"],
            name=f"base_build__tripod_pedestal__foot_glide_{i}", material_class_id="rubber.smooth_plain",
        )
        model.articulation(
            f"tabletop_to_support_member_{i}",
            ArticulationType.FIXED,
            parent=top,
            child=foot,
            origin=Origin(
                xyz=(attach_r * math.cos(theta), attach_r * math.sin(theta), attach_z),
                rpy=(0.0, 0.0, theta),
            ),
            meta={"mechanism": "cast foot radiating from the pedestal hub"},
        )
        members.append(foot)
    return members


_BASE_BUILDERS = {
    "folding_legs": _base_build_folding_legs_build,
    "pedestal_column": _base_build_pedestal_column_build,
    "tripod_pedestal": _base_build_tripod_pedestal_build,
}


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_table4(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_table4",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "vertical-axis lazy-susan turntable on a round table",
        },
    )
    mats = _materials(model, r)
    top = _build_tabletop(model, r, mats)
    tray = _build_tray(model, top, r, mats)
    _build_bearing(top, tray, r, mats)
    _BASE_BUILDERS[r.base_build](model, top, r, mats)

    if r.base_build == "folding_legs":
        leg_joints = [f"tabletop_to_support_member_{i}" for i in range(r.support_count)]
        deployed = {name: 0.0 for name in leg_joints}
        deployed["tabletop_to_turntable_tray"] = 0.0
        folded = {name: r.leg_fold_rad for name in leg_joints}
        folded["tabletop_to_turntable_tray"] = math.pi * 0.5
        model.meta["risk_poses"] = (deployed, folded)
        model.meta["coupled_joint_pairs"] = tuple(
            ("tabletop_to_turntable_tray", name) for name in leg_joints
        )
    return model


def build_seeded_picturex_0611_folding_table4(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_table4(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_table4_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    tops = _parts_by_role(model, "tabletop")
    trays = _parts_by_role(model, "turntable_tray")
    members = _parts_by_role(model, "support_member")
    joints = {j.name: j for j in model.articulations}
    tray_joint = joints.get("tabletop_to_turntable_tray")

    ctx.check(
        "category_anchor: the turntable spins on a vertical axis in the tabletop",
        len(tops) == 1
        and len(trays) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "tabletop"
        and tray_joint is not None
        and tray_joint.articulation_type == ArticulationType.REVOLUTE
        and tray_joint.parent == "tabletop"
        and tuple(round(abs(v), 6) for v in tray_joint.axis) == (0.0, 0.0, 1.0)
        and tray_joint.motion_limits is not None
        and tray_joint.motion_limits.upper - tray_joint.motion_limits.lower > 6.0,
        details=f"trays={len(trays)} joint={getattr(tray_joint, 'name', None)}",
    )

    # Preflight never materialises meshes, so every AABB below is read from a
    # primitive element.
    if r.base_build == "folding_legs":
        foot_elems = [f"base_build__folding_legs__foot_pad_{i}" for i in range(r.support_count)]
    elif r.base_build == "pedestal_column":
        foot_elems = [
            f"base_build__pedestal_column__foot_glide_{i}" for i in range(r.support_count)
        ]
    else:
        foot_elems = [
            f"base_build__tripod_pedestal__foot_glide_{i}" for i in range(r.support_count)
        ]
    floor_ok = bool(members)
    bottoms = []
    for member in members:
        best = None
        for elem in foot_elems:
            box = ctx.part_element_world_aabb(member, elem=elem)
            if box is not None:
                best = box[0][2] if best is None else min(best, box[0][2])
        bottoms.append(None if best is None else round(best, 4))
        if best is None or best > 0.030 or best < -0.012:
            floor_ok = False
    ctx.check(
        "category_anchor: the base carries the top at seating height",
        len(members) == r.support_count and floor_ok and 0.68 <= r.table_height_m <= 0.78,
        details=f"members={len(members)} bottoms={bottoms} height={r.table_height_m}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    tray_marker = {
        "woven_lattice": "woven_lattice__weave_",
        "flush_recessed": "flush_recessed__bearing_lip",
        "raised_guard_rim": "raised_guard_rim__retaining_rim",
        "two_tier": "two_tier__lower_shelf_top",
        "segmented_wedge": "segmented_wedge__sector_hub",
    }[r.tray_build]
    ctx.check(
        "category_anchor: tray_build identity",
        any(tray_marker in n for n in visual_names)
        and f"tray_build__{r.tray_build}__turntable_tray" == trays[0].name,
        details=f"tray_build={r.tray_build}",
    )

    bearing_marker = {
        "race_and_plate": "bearing_race",
        "ring_and_hub": "bearing_build__ring_and_hub__bearing_ring",
        "roller_retainer": "bearing_build__roller_retainer__roller_track",
        "detent_index": "bearing_build__detent_index__spring_pin_tip",
    }[r.bearing_build]
    ctx.check(
        "category_anchor: bearing_build identity",
        any(bearing_marker in n for n in visual_names),
        details=f"bearing_build={r.bearing_build}",
    )

    base_marker = {
        "folding_legs": "folding_legs__leg_tube_",
        "pedestal_column": "pedestal_column__lobe_arm_",
        "tripod_pedestal": "tripod_pedestal__cast_foot_",
    }[r.base_build]
    ctx.check(
        "category_anchor: base_build identity",
        any(base_marker in n for n in visual_names),
        details=f"base_build={r.base_build}",
    )

    # The tray really turns on the bearing rather than being fixed to the top.
    pad_elem = "center_cap"
    rest = ctx.part_element_world_aabb(trays[0], elem=pad_elem)
    probe = f"tray_build__{r.tray_build}__edge_seam"
    with ctx.pose({tray_joint: math.pi * 0.5}):
        turned = ctx.part_element_world_aabb(trays[0], elem=pad_elem)
    ctx.check(
        "the turntable stays centred and clear of the tabletop rim",
        rest is not None
        and turned is not None
        and abs(rest[0][0] - turned[0][0]) < 1e-3
        and abs(rest[0][1] - turned[0][1]) < 1e-3
        and r.tray_radius_m < r.table_radius_m - 0.090
        and probe in visual_names,
        details=f"rest={rest} turned={turned} tray_r={r.tray_radius_m} top_r={r.table_radius_m}",
    )

    ctx.check(
        "support members are pitched evenly around the hinge circle",
        len(r.angles) == r.support_count
        and r.hinge_radius_m > 0.30
        and 2.0 * r.hinge_radius_m * math.sin(math.pi / r.support_count) > 0.090,
        details=f"angles={r.angles} hinge_r={r.hinge_radius_m}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "smallest_top_widest_tray_three_legs",
        {
            "tray_build": "raised_guard_rim",
            "bearing_build": "detent_index",
            "base_build": "folding_legs",
            "support_count": 3,
            "table_diameter_m": 1.00,
            "tray_diameter_ratio": 0.72,
            "table_height_m": 0.68,
        },
        reason="smallest top with the largest tray and the fewest legs at the lowest height",
    ),
    corner_case(
        "largest_top_smallest_tray_six_legs",
        {
            "tray_build": "flush_recessed",
            "bearing_build": "ring_and_hub",
            "base_build": "folding_legs",
            "support_count": 6,
            "table_diameter_m": 1.45,
            "tray_diameter_ratio": 0.55,
            "table_height_m": 0.78,
        },
        reason="largest envelope: six folding legs around the widest annular race",
    ),
    corner_case(
        "tight_pedestal_two_tier",
        {
            "tray_build": "two_tier",
            "bearing_build": "roller_retainer",
            "base_build": "pedestal_column",
            "support_count": 3,
            "table_diameter_m": 1.00,
            "tray_diameter_ratio": 0.72,
            "table_height_m": 0.68,
        },
        reason="lowest table with the tallest two-tier tray over the shortest pedestal",
    ),
    corner_case(
        "tripod_segmented_six_feet",
        {
            "tray_build": "segmented_wedge",
            "bearing_build": "race_and_plate",
            "base_build": "tripod_pedestal",
            "support_count": 6,
            "table_diameter_m": 1.45,
            "tray_diameter_ratio": 0.55,
            "table_height_m": 0.78,
        },
        reason="six cast feet under the tallest column with a sectored tray",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_folding_table4",
    "build_seeded_picturex_0611_folding_table4",
    "run_picturex_0611_folding_table4_tests",
]
