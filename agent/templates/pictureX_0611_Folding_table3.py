# SPDX-License-Identifier: Apache-2.0

"""Self-contained wooden drop-leaf folding dining table template.

One rigid ``table_center`` root carries the fixed centre strip of the tabletop,
its segmented apron and every mounting bracket.  Two ``drop_leaf`` parts are
REVOLUTE children of the centre, hinged on the two seams at +/-``hinge_x``; q=0
is deployed and coplanar with the centre, q=pi/2 is folded straight down.

``top_profile`` only changes the plan outline the centre strip and both leaves
are cut from.  ``support_system`` is one structural family of collapsible leg
systems -- ``corner_fold_legs`` and ``center_pedestal`` hinge off the centre,
the four trestle candidates hinge off a leaf underside and fold with it, exactly
as in their sources.  ``leaf_stay`` is an independent per-leaf stay mounted in
the centre apron that reaches out under the leaf; each stay MIMICs its own leaf
hinge, so the stay is deployed exactly when its leaf is down-locked and stows
back inside the apron as the leaf folds.

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
    LoftGeometry,
    Mimic,
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

TopProfile = Literal["round_arc", "ellipse_oval", "racetrack", "d_leaf_rect"]
SupportSystem = Literal[
    "corner_fold_legs",
    "narrow_u_trestle",
    "broad_end_trestle",
    "x_braced_trestle",
    "splayed_aframe",
    "center_pedestal",
]
LeafStay = Literal["prop_arm", "slide_rail", "scissor_link"]
PaletteStyle = Literal["warm_oak", "walnut", "ash_white", "black_stain"]

TOP_PROFILES: tuple[TopProfile, ...] = ("round_arc", "ellipse_oval", "racetrack", "d_leaf_rect")
SUPPORT_SYSTEMS: tuple[SupportSystem, ...] = (
    "corner_fold_legs",
    "narrow_u_trestle",
    "broad_end_trestle",
    "x_braced_trestle",
    "splayed_aframe",
    "center_pedestal",
)
LEAF_STAYS: tuple[LeafStay, ...] = ("prop_arm", "slide_rail", "scissor_link")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("warm_oak", "walnut", "ash_white", "black_stain")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("top_profile", TOP_PROFILES),
        component_slot("support_system", SUPPORT_SYSTEMS),
        component_slot("leaf_stay", LEAF_STAYS),
        multiplicity_slot("stay_per_leaf", (1, 2, 3), item_slot="leaf_stay"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_oak": {
        "wood": (0.66, 0.38, 0.19, 1.0),
        "wood_top": (0.76, 0.49, 0.28, 1.0),
        "wood_edge": (0.56, 0.30, 0.14, 1.0),
        "steel": (0.055, 0.060, 0.058, 1.0),
        "hardware": (0.12, 0.13, 0.12, 1.0),
        "rubber": (0.035, 0.036, 0.034, 1.0),
    },
    "walnut": {
        "wood": (0.36, 0.23, 0.15, 1.0),
        "wood_top": (0.45, 0.30, 0.20, 1.0),
        "wood_edge": (0.27, 0.17, 0.11, 1.0),
        "steel": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.17, 0.17, 0.18, 1.0),
        "rubber": (0.04, 0.04, 0.04, 1.0),
    },
    "ash_white": {
        "wood": (0.83, 0.79, 0.71, 1.0),
        "wood_top": (0.90, 0.87, 0.80, 1.0),
        "wood_edge": (0.72, 0.68, 0.60, 1.0),
        "steel": (0.30, 0.31, 0.32, 1.0),
        "hardware": (0.45, 0.46, 0.47, 1.0),
        "rubber": (0.08, 0.08, 0.08, 1.0),
    },
    "black_stain": {
        "wood": (0.16, 0.15, 0.15, 1.0),
        "wood_top": (0.22, 0.21, 0.20, 1.0),
        "wood_edge": (0.11, 0.10, 0.10, 1.0),
        "steel": (0.06, 0.06, 0.07, 1.0),
        "hardware": (0.34, 0.35, 0.36, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
}

TOP_T = 0.036            # tabletop slab thickness
SEAM = 0.003             # visible hinge seam between centre strip and leaf
APRON_H = 0.075          # apron rail height under the centre strip
APRON_W = 0.026          # apron rail thickness across X
LEAF_FOLD = math.pi / 2.0
STAY_DROP = 0.055        # leaf-local depth of the stay pivot under the top
STAY_HUB_H = 0.036       # stay pivot hub length along its own rotation axis
STAY_INBOARD = 0.050     # a deployed stay stops this far outboard of the seam,
                         # so nothing on a leaf ever swings in over the centre
APRON_INSET = 0.075      # apron outer face inboard of the seam, clear of
                         # everything a folded leaf carries down past it
STAY_CLEAR = 0.002       # gap the folded stay keeps below its own leaf slab
STAY_BOSS_H = 0.0195     # bearing height of the stay boss above the pivot axis
LEAF_FRAME_DROP = 0.045  # depth of every leaf-mounted support hinge below the top
TRESTLE_STOW = LEAF_FOLD  # trestle folds exactly flat under its leaf
HINGE_DROP = 0.030       # butt-hinge axis sits this far under the tabletop
HINGE_SEGS = 5           # alternating knuckle segments across the seam
PAD_GAP = 0.0005         # stay foot stands this far off the apron: real contact
MOUNT = 0.0008           # intra-part embedment so one part stays one island
RAIL_BODY = 0.048        # slide rail bar length riding in its carrier guide
RAIL_START = 0.012       # rail bar starts clear of the guide back stop
YOKE_Y = 0.026           # half spacing of every bearing yoke cheek
STAY_PIN_L = 0.038       # stay pivot pin stays inside its yoke cheeks


@dataclass(frozen=True)
class Config:
    top_profile: TopProfile = "round_arc"
    support_system: SupportSystem = "corner_fold_legs"
    leaf_stay: LeafStay = "prop_arm"
    stay_per_leaf: int = 2
    top_length_m: float | None = None
    top_width_m: float | None = None
    center_width_ratio: float | None = None
    table_height_m: float | None = None
    palette_style: PaletteStyle = "warm_oak"
    name: str = "pictureX_0611_Folding_table3"


@dataclass(frozen=True)
class ResolvedConfig:
    top_profile: TopProfile
    support_system: SupportSystem
    leaf_stay: LeafStay
    stay_per_leaf: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    top_length_m: float
    top_width_m: float
    center_width_ratio: float
    table_height_m: float
    hinge_x_m: float
    prof_rx: float
    prof_ry: float
    prof_hs: float
    prof_dr: float
    x_max: float
    leaf_reach_m: float
    top_z: float
    under_z: float
    apron_bot_z: float
    y_end_m: float
    stay_arm_m: float
    stay_pivot_u: float
    stay_stow_rad: float
    stay_travel_m: float
    stay_y: tuple[float, ...]
    stay_unit_total: int
    support_member_count: int
    leg_pivot_x: float
    leg_pivot_y: float
    leg_pivot_z: float
    leg_len_m: float
    leg_fold_rad: float
    frame_drop_m: float
    frame_u_m: float
    frame_half_m: float
    ped_radius_m: float
    ped_top_z: float
    ped_hub_z: float
    ped_arm_m: float
    ped_fold_rad: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x0F73_1103)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        top_profile=choices["top_profile"],
        support_system=choices["support_system"],
        leaf_stay=choices["leaf_stay"],
        stay_per_leaf=choices["stay_per_leaf"],
        top_length_m=round(rng.uniform(0.82, 1.10), 4),
        top_width_m=round(rng.uniform(0.98, 1.32), 4),
        center_width_ratio=round(rng.uniform(0.28, 0.40), 4),
        table_height_m=round(rng.uniform(0.700, 0.780), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"folding_table3_seed_{int(seed)}",
    )


def _outline_half_length(
    kind: str, rx: float, ry: float, hs: float, dr: float, hinge_x: float, x: float
) -> float:
    """Half extent along Y of the deployed top at plan station ``x``."""
    ax = abs(float(x))
    if kind == "round_arc":
        return math.sqrt(max(rx * rx - ax * ax, 0.0))
    if kind == "ellipse_oval":
        return ry * math.sqrt(max(1.0 - (ax / rx) ** 2, 0.0))
    if kind == "racetrack":
        if ax <= hs:
            return ry
        return math.sqrt(max(ry * ry - (ax - hs) ** 2, 0.0))
    if ax <= hinge_x:
        return ry
    return math.sqrt(max(dr * dr - (ax - hinge_x) ** 2, 0.0))


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "top_profile": config.top_profile,
            "support_system": config.support_system,
            "leaf_stay": config.leaf_stay,
            "stay_per_leaf": config.stay_per_leaf,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.top_length_m is not None and not 0.82 <= float(config.top_length_m) <= 1.10:
        raise ValueError("top_length_m must be in [0.82, 1.10]")
    if config.top_width_m is not None and not 0.98 <= float(config.top_width_m) <= 1.32:
        raise ValueError("top_width_m must be in [0.98, 1.32]")
    if config.center_width_ratio is not None and not (
        0.28 <= float(config.center_width_ratio) <= 0.40
    ):
        raise ValueError("center_width_ratio must be in [0.28, 0.40]")
    if config.table_height_m is not None and not 0.700 <= float(config.table_height_m) <= 0.780:
        raise ValueError("table_height_m must be in [0.700, 0.780]")

    length = _clamp(config.top_length_m, 0.82, 1.10) if config.top_length_m is not None else 0.94
    width = _clamp(config.top_width_m, 0.98, 1.32) if config.top_width_m is not None else 1.14
    ratio = (
        _clamp(config.center_width_ratio, 0.28, 0.40)
        if config.center_width_ratio is not None
        else 0.32
    )
    height = (
        _clamp(config.table_height_m, 0.700, 0.780)
        if config.table_height_m is not None
        else 0.742
    )

    hinge_x = width * ratio * 0.5

    kind = config.top_profile
    if kind == "round_arc":
        rx = ry = 0.5 * math.sqrt(width * length)
        hs = 0.0
        dr = 0.0
        x_max = rx
    elif kind == "ellipse_oval":
        rx = width * 0.5
        ry = length * 0.5
        hs = 0.0
        dr = 0.0
        x_max = rx
    elif kind == "racetrack":
        rx = width * 0.5
        ry = min(length, width * 0.96) * 0.5
        hs = rx - ry
        dr = 0.0
        x_max = rx
    else:  # d_leaf_rect
        rx = width * 0.5
        ry = length * 0.5
        hs = 0.0
        dr = min(width * 0.5 - hinge_x, length * 0.5)
        x_max = hinge_x + dr

    reach = x_max - hinge_x
    top_z = height - TOP_T * 0.5
    under_z = height - TOP_T
    apron_bot = under_z - APRON_H
    y_end = 0.86 * _outline_half_length(kind, rx, ry, hs, dr, hinge_x, hinge_x * 0.5)

    # A leaf-mounted bracket: it swings inboard off the leaf and bears on the
    # outer face of the centre apron, so it never enters the space the folding
    # legs sweep through under the centre.
    stay_pivot_u = _clamp(0.30 * reach, 0.150, 0.200)
    stay_arm = stay_pivot_u - STAY_INBOARD
    stay_travel = stay_arm - RAIL_BODY - RAIL_START - 0.004
    # A folded stay must stay clear of its own leaf slab, so its stow angle
    # comes straight from the arm length and the depth it hangs at.
    stay_stow = math.asin(
        _clamp((STAY_DROP - TOP_T * 0.5 - 0.010 - STAY_CLEAR) / stay_arm, 0.10, 0.34)
    )
    n_stay = int(config.stay_per_leaf)
    band = min(
        0.15 * length,
        y_end - 0.170,
        _outline_half_length(kind, rx, ry, hs, dr, hinge_x, hinge_x + stay_pivot_u)
        - 0.050,
    )
    if n_stay == 1:
        stations: tuple[float, ...] = (0.0,)
    elif n_stay == 2:
        stations = (-band * 0.72, band * 0.72)
    else:
        stations = (-band, 0.0, band)

    counts = {
        "corner_fold_legs": 4,
        "narrow_u_trestle": 2,
        "broad_end_trestle": 2,
        "x_braced_trestle": 2,
        "splayed_aframe": 2,
        "center_pedestal": 3,
    }
    member_count = counts[config.support_system]

    leg_px = hinge_x - 0.100
    leg_py = y_end - 0.060
    leg_pz = under_z - 0.102
    leg_len = leg_pz - 0.012
    leg_fold = _clamp(
        math.asin(_clamp((2.0 * leg_py - 0.075) / leg_len, 0.05, 0.98)), 0.60, 1.30
    )

    frame_drop = top_z - LEAF_FRAME_DROP - 0.014
    # The leaf-mounted support hinge sits outboard of the stay envelope, so a
    # saddle never shares a station with a deployed stay.
    frame_u = _clamp(0.62 * reach, 0.230, 0.330)
    frame_half = (
        _outline_half_length(kind, rx, ry, hs, dr, hinge_x, hinge_x + frame_u) - 0.035
    )


    ped_r = _clamp(hinge_x - 0.105, 0.020, 0.065)
    ped_top = under_z - 0.115
    ped_hub = 0.058
    ped_arm = _clamp(0.26 + 0.20 * (width - 0.98), 0.26, 0.34)
    ped_fold = math.acos(_clamp((hinge_x - 0.060) / ped_arm, 0.02, 0.90))

    return ResolvedConfig(
        top_profile=config.top_profile,
        support_system=config.support_system,
        leaf_stay=config.leaf_stay,
        stay_per_leaf=n_stay,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        top_length_m=length,
        top_width_m=width,
        center_width_ratio=ratio,
        table_height_m=height,
        hinge_x_m=hinge_x,
        prof_rx=rx,
        prof_ry=ry,
        prof_hs=hs,
        prof_dr=dr,
        x_max=x_max,
        leaf_reach_m=reach,
        top_z=top_z,
        under_z=under_z,
        apron_bot_z=apron_bot,
        y_end_m=y_end,
        stay_arm_m=stay_arm,
        stay_pivot_u=stay_pivot_u,
        stay_stow_rad=stay_stow,
        stay_travel_m=stay_travel,
        stay_y=tuple(stations),
        stay_unit_total=2 * n_stay,
        support_member_count=member_count,
        leg_pivot_x=leg_px,
        leg_pivot_y=leg_py,
        leg_pivot_z=leg_pz,
        leg_len_m=leg_len,
        leg_fold_rad=leg_fold,
        frame_drop_m=frame_drop,
        frame_u_m=frame_u,
        frame_half_m=max(frame_half, 0.030),
        ped_radius_m=ped_r,
        ped_top_z=ped_top,
        ped_hub_z=ped_hub,
        ped_arm_m=ped_arm,
        ped_fold_rad=ped_fold,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("top_profile", config.top_profile),
        ("support_system", config.support_system),
        ("leaf_stay", config.leaf_stay),
        ("stay_per_leaf", config.stay_per_leaf),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _half_length(r: ResolvedConfig, x: float) -> float:
    return _outline_half_length(
        r.top_profile, r.prof_rx, r.prof_ry, r.prof_hs, r.prof_dr, r.hinge_x_m, x
    )


def _center_polygon(r: ResolvedConfig, segments: int = 40) -> list[tuple[float, float]]:
    hx = r.hinge_x_m
    xs = [-hx + 2.0 * hx * i / segments for i in range(segments + 1)]
    top = [(x, _half_length(r, x)) for x in xs]
    bottom = [(x, -_half_length(r, x)) for x in reversed(xs)]
    return top + bottom


def _leaf_polygon(r: ResolvedConfig, segments: int = 46) -> list[tuple[float, float]]:
    hx = r.hinge_x_m
    span = r.leaf_reach_m - SEAM
    us = [SEAM + span * i / segments for i in range(segments + 1)]
    top = [(u, _half_length(r, hx + u)) for u in us]
    bottom = [(u, -_half_length(r, hx + u)) for u in reversed(us)]
    return top + bottom[1:]


# --- small builders ---------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"ft3_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"ft3_{r.palette_style}_{key}"
    return mats


def _tube(part, p0, p1, radius: float, material: str, name: str) -> None:
    vx, vy, vz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(vx * vx + vy * vy + vz * vz)
    horiz = math.hypot(vx, vy)
    yaw = math.atan2(vy, vx) if horiz > 1e-12 else 0.0
    pitch = math.atan2(horiz, vz)
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(
            xyz=((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5),
            rpy=(0.0, pitch, yaw),
        ),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _square_loop(cx: float, cy: float, z: float, width: float):
    h = width * 0.5
    return [(cx - h, cy - h, z), (cx + h, cy - h, z), (cx + h, cy + h, z), (cx - h, cy + h, z)]


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
    mimic: Mimic | None = None,
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
        mimic=mimic,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


# --- centre section ---------------------------------------------------------
def _build_center(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    center = model.part("table_center", meta={"role": "table_center"})
    center.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_center_polygon(r), TOP_T, center=True),
            f"top_profile__{r.top_profile}__center_slab_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.top_z)),
        material=mats["wood_top"],
        name=f"top_profile__{r.top_profile}__center_slab", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
    )

    hx = r.hinge_x_m
    y_end = r.y_end_m
    apron_x = hx - APRON_INSET - APRON_W * 0.5
    for side_index, sx in enumerate((-1.0, 1.0)):
        center.visual(
            Box((APRON_W, 2.0 * y_end - 0.002, APRON_H)),
            origin=Origin(xyz=(sx * apron_x, 0.0, r.under_z - APRON_H * 0.5 + MOUNT)),
            material=mats["wood"],
            name=f"side_apron_{side_index}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
        )
    for end_index, sy in enumerate((-1.0, 1.0)):
        center.visual(
            Box((2.0 * apron_x + APRON_W, APRON_W, APRON_H)),
            origin=Origin(
                xyz=(0.0, sy * (y_end - APRON_W * 0.5), r.under_z - APRON_H * 0.5 + MOUNT)
            ),
            material=mats["wood"],
            name=f"cross_apron_{end_index}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
        )
    center.visual(
        Box((0.030, 2.0 * y_end - 0.004, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, r.apron_bot_z + 0.018)),
        material=mats["steel"],
        name="center_tie_rail", material_class_id="metal.steel_bare",
    )

    # Alternating butt-hinge knuckles: the centre owns the even segments, each
    # leaf the odd ones, so consecutive knuckles meet end to end on one axis.
    seg = 1.24 * y_end / HINGE_SEGS
    hinge_z = r.top_z - HINGE_DROP
    for side_index, sx in enumerate((-1.0, 1.0)):
        for index in range(0, HINGE_SEGS, 2):
            y = -0.62 * y_end + seg * (index + 0.5)
            center.visual(
                Cylinder(radius=0.009, length=seg - 0.001),
                origin=Origin(xyz=(sx * hx, y, hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["hardware"],
                name=f"root_hinge_knuckle_{side_index}_{index}", material_class_id="metal.steel_bare",
            )
            center.visual(
                Box((0.046, seg - 0.001, 0.008)),
                origin=Origin(
                    xyz=(sx * (hx - 0.025), y, hinge_z + 0.009)
                ),
                material=mats["hardware"],
                name=f"root_hinge_plate_{side_index}_{index}", material_class_id="metal.steel_bare",
            )
            center.visual(
                Box((0.020, seg - 0.001, HINGE_DROP - 0.013 + MOUNT)),
                origin=Origin(
                    xyz=(
                        sx * (hx - 0.014),
                        y,
                        hinge_z + 0.013 + (HINGE_DROP - 0.013 + MOUNT) * 0.5,
                    )
                ),
                material=mats["hardware"],
                name=f"root_hinge_web_{side_index}_{index}", material_class_id="metal.steel_bare",
            )
    return center


def _build_leaf(
    model: ArticulatedObject, center, r: ResolvedConfig, mats: dict[str, str], index: int
):
    side = 1.0 if index == 0 else -1.0
    leaf = model.part(
        f"top_profile__{r.top_profile}__drop_leaf_{index}",
        meta={"role": "drop_leaf", "index": index},
    )
    # The leaf frame is the hinge axis, HINGE_DROP below the tabletop plane.
    leaf.visual(
        mesh_from_geometry(
            ExtrudeGeometry(_leaf_polygon(r), TOP_T, center=True),
            f"top_profile__{r.top_profile}__leaf_slab_mesh_{index}",
        ),
        origin=Origin(xyz=(0.0, 0.0, HINGE_DROP)),
        material=mats["wood_top"],
        name=f"top_profile__{r.top_profile}__leaf_slab_{index}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
    )
    y_end = r.y_end_m
    seg = 1.24 * y_end / HINGE_SEGS
    for hinge_index in range(1, HINGE_SEGS, 2):
        y = -0.62 * y_end + seg * (hinge_index + 0.5)
        leaf.visual(
            Cylinder(radius=0.009, length=seg - 0.001),
            origin=Origin(xyz=(0.0, y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"leaf_hinge_knuckle_{index}_{hinge_index}", material_class_id="metal.steel_bare",
        )
        leaf.visual(
            Box((0.030, seg - 0.001, 0.008)),
            origin=Origin(xyz=(0.017, y, 0.009)),
            material=mats["hardware"],
            name=f"leaf_hinge_plate_{index}_{hinge_index}", material_class_id="metal.steel_bare",
        )
        leaf.visual(
            Box((0.020, seg - 0.001, HINGE_DROP - 0.013 + MOUNT)),
            origin=Origin(
                xyz=(0.014, y, 0.013 + (HINGE_DROP - 0.013 + MOUNT) * 0.5)
            ),
            material=mats["hardware"],
            name=f"leaf_hinge_web_{index}_{hinge_index}", material_class_id="metal.steel_bare",
        )
    # The batten sits outboard of the support station so a stored trestle
    # crossbar never meets it.
    batten_lo = r.frame_u_m + 0.030
    batten_hi = max(r.leaf_reach_m - 0.020, batten_lo + 0.020)
    batten_u = (batten_lo + batten_hi) * 0.5
    leaf.visual(
        Box((batten_hi - batten_lo, 0.040, 0.030)),
        origin=Origin(xyz=(batten_u, 0.0, HINGE_DROP - TOP_T * 0.5 - 0.015 + MOUNT)),
        material=mats["wood_edge"],
        name=f"leaf_batten_{index}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
    )
    _axis_joint(
        model,
        name=f"center_to_leaf_{index}",
        parent=center,
        child=leaf,
        point=(side * r.hinge_x_m, 0.0, r.top_z - HINGE_DROP),
        axis=(0.0, side, 0.0),
        radial=(side, 0.0, 0.0),
        lower=0.0,
        upper=LEAF_FOLD,
        effort=48.0,
        velocity=1.0,
        meta={"positive_motion": f"folds drop leaf {index} straight down"},
    )
    return leaf


# --- support candidates -----------------------------------------------------
def _support_system_corner_fold_legs_build(
    model: ArticulatedObject, center, leaves, r: ResolvedConfig, mats: dict[str, str]
) -> list:
    members = []
    stations = (
        (-r.leg_pivot_x, r.leg_pivot_y),
        (r.leg_pivot_x, r.leg_pivot_y),
        (-r.leg_pivot_x, -r.leg_pivot_y),
        (r.leg_pivot_x, -r.leg_pivot_y),
    )
    for k, (px, py) in enumerate(stations):
        leg = model.part(
            f"support_system__corner_fold_legs__member_{k}",
            meta={"role": "support_member", "index": k},
        )
        loft = LoftGeometry(
            [
                _square_loop(0.0, 0.0, -0.010, 0.050),
                _square_loop(0.0, 0.0, -r.leg_len_m * 0.45, 0.042),
                _square_loop(0.0, 0.0, -r.leg_len_m, 0.032),
            ],
            cap=True,
            closed=True,
        )
        leg.visual(
            mesh_from_geometry(loft, f"corner_leg_mesh_{k}"),
            material=mats["wood"],
            name=f"support_system__corner_fold_legs__wood_leg_{k}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
        )
        leg.visual(
            Cylinder(radius=0.011, length=0.052),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"support_system__corner_fold_legs__pivot_barrel_{k}", material_class_id="metal.steel_bare",
        )
        leg.visual(
            Box((0.034, 0.034, 0.040)),
            origin=Origin(xyz=(0.0, 0.0, -0.016)),
            material=mats["steel"],
            name=f"support_system__corner_fold_legs__pivot_web_{k}", material_class_id="metal.steel_bare",
        )
        _tube(
            leg,
            (0.0, 0.0, -0.020),
            (0.0, 0.0, -r.leg_len_m * 0.42),
            0.006,
            mats["steel"],
            f"support_system__corner_fold_legs__locking_brace_{k}",
        )
        leg.visual(
            Box((0.040, 0.040, 0.014)),
            origin=Origin(xyz=(0.0, 0.0, -r.leg_len_m - 0.004)),
            material=mats["rubber"],
            name=f"support_system__corner_fold_legs__foot_pad_{k}", material_class_id="rubber.smooth_plain",
        )
        # Bearing yoke: two cheeks straddle the pivot barrel with a 1 mm running
        # clearance, so the leg turns in a real bearing instead of a solid block.
        for cheek, sx in enumerate((-1.0, 1.0)):
            center.visual(
                Box((0.010, 0.058, 0.046)),
                origin=Origin(xyz=(px + sx * 0.0315, py, r.leg_pivot_z)),
                material=mats["steel"],
                name=f"leg_bearing_cheek_{k}_{cheek}", material_class_id="metal.steel_bare",
            )
        riser_bot = r.leg_pivot_z + 0.016
        riser_h = r.under_z + 0.006 - riser_bot
        center.visual(
            Box((0.070, 0.034, riser_h)),
            origin=Origin(xyz=(px, py, riser_bot + riser_h * 0.5)),
            material=mats["steel"],
            name=f"leg_bearing_riser_{k}", material_class_id="metal.steel_bare",
        )
        _axis_joint(
            model,
            name=f"center_to_support_member_{k}",
            parent=center,
            child=leg,
            point=(px, py, r.leg_pivot_z),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, -1.0, 0.0),
            lower=-r.leg_fold_rad,
            upper=0.0,
            effort=60.0,
            velocity=1.0,
            meta={"positive_motion": "swings the folded leg back down to the floor"},
        )
        members.append(leg)
    return members


def _trestle_tubes(frame, r: ResolvedConfig, mats: dict[str, str], kind: str, k: int) -> float:
    """Round-tube trestle geometry in the frame's own hinge-centred frame."""
    drop = r.frame_drop_m
    y_end = r.y_end_m
    steel = mats["steel"]
    prefix = f"support_system__{kind}__"
    if kind == "narrow_u_trestle":
        top_y = 0.62 * y_end
        foot_y = 0.78 * y_end
        _tube(
            frame, (0.0, -top_y, 0.0), (0.0, top_y, 0.0), 0.013, steel,
            f"{prefix}hinge_crossbar_{k}",
        )
        for i, sy in enumerate((-1.0, 1.0)):
            _tube(
                frame, (0.0, sy * top_y, 0.0), (0.010, sy * foot_y, -drop), 0.011, steel,
                f"{prefix}side_tube_{k}_{i}",
            )
        t = 0.57
        _tube(
            frame,
            (0.010 * t, -(top_y + (foot_y - top_y) * t), -drop * t),
            (0.010 * t, top_y + (foot_y - top_y) * t, -drop * t),
            0.0085, steel, f"{prefix}lower_stretcher_{k}",
        )
        feet_y = (-foot_y, foot_y)
        foot_x = 0.010
    elif kind == "broad_end_trestle":
        top_y = 0.86 * y_end
        foot_y = top_y
        _tube(
            frame, (0.0, -top_y, 0.0), (0.0, top_y, 0.0), 0.013, steel,
            f"{prefix}hinge_crossbar_{k}",
        )
        for i, sy in enumerate((-1.0, 1.0)):
            _tube(
                frame, (0.0, sy * top_y, 0.0), (0.0, sy * top_y, -drop), 0.013, steel,
                f"{prefix}side_tube_{k}_{i}",
            )
        _tube(
            frame, (0.0, -top_y, -drop * 0.62), (0.0, top_y, -drop * 0.62), 0.0085, steel,
            f"{prefix}lower_stretcher_{k}",
        )
        feet_y = (-foot_y, foot_y)
        foot_x = 0.0
    elif kind == "x_braced_trestle":
        top_y = 0.62 * y_end
        foot_y = 0.80 * y_end
        _tube(
            frame, (0.0, -top_y, 0.0), (0.0, top_y, 0.0), 0.013, steel,
            f"{prefix}hinge_crossbar_{k}",
        )
        _tube(frame, (0.0, -top_y, 0.0), (0.010, foot_y, -drop), 0.011, steel, f"{prefix}x_leg_{k}_0")
        _tube(frame, (0.0, top_y, 0.0), (0.010, -foot_y, -drop), 0.011, steel, f"{prefix}x_leg_{k}_1")
        t_cross = top_y / (top_y + foot_y)
        px = 0.010 * t_cross
        pz = -drop * t_cross
        frame.visual(
            Cylinder(radius=0.007, length=0.028),
            origin=Origin(xyz=(px, 0.0, pz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=steel,
            name=f"{prefix}pivot_pin_{k}", material_class_id="metal.steel_bare",
        )
        for side, dx in enumerate((-0.013, 0.013)):
            frame.visual(
                Sphere(radius=0.009),
                origin=Origin(xyz=(px + dx, 0.0, pz)),
                material=steel,
                name=f"{prefix}pivot_cap_{k}_{side}", material_class_id="metal.steel_bare",
            )
        t = 0.74
        _tube(
            frame,
            (0.010 * t, -(top_y + (foot_y - top_y) * t), -drop * t),
            (0.010 * t, top_y + (foot_y - top_y) * t, -drop * t),
            0.0085, steel, f"{prefix}lower_stretcher_{k}",
        )
        feet_y = (-foot_y, foot_y)
        foot_x = 0.010
    else:  # splayed_aframe
        top_y = 0.55 * y_end
        foot_y = 0.98 * y_end
        _tube(
            frame, (0.0, -top_y, 0.0), (0.0, top_y, 0.0), 0.013, steel,
            f"{prefix}hinge_crossbar_{k}",
        )
        for i, sy in enumerate((-1.0, 1.0)):
            _tube(
                frame, (0.0, sy * top_y, 0.0), (0.008, sy * foot_y, -drop), 0.011, steel,
                f"{prefix}aframe_leg_{k}_{i}",
            )
            frame.visual(
                Cylinder(radius=0.016, length=0.032),
                origin=Origin(xyz=(0.0, sy * top_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=steel,
                name=f"{prefix}hinge_socket_{k}_{i}", material_class_id="metal.steel_bare",
            )
        t = 0.50
        sy_mid = top_y + (foot_y - top_y) * t
        _tube(
            frame,
            (0.008 * t, -sy_mid, -drop * t),
            (0.008 * t, sy_mid, -drop * t),
            0.009, steel, f"{prefix}cross_stretcher_{k}",
        )
        for i, sy in enumerate((-1.0, 1.0)):
            _tube(
                frame,
                (0.008 * t, sy * sy_mid, -drop * t),
                (0.008, sy * foot_y, -drop),
                0.007, steel, f"{prefix}diagonal_brace_{k}_{i}",
            )
        feet_y = (-foot_y, foot_y)
        foot_x = 0.008

    for i, y in enumerate(feet_y):
        _tube(
            frame,
            (foot_x - 0.042, y, -drop),
            (foot_x + 0.042, y, -drop),
            0.013, steel, f"{prefix}foot_bar_{k}_{i}",
        )
        for cap_index, x in enumerate((foot_x - 0.042, foot_x + 0.042)):
            frame.visual(
                Sphere(radius=0.0145),
                origin=Origin(xyz=(x, y, -drop)),
                material=mats["rubber"],
                name=f"{prefix}foot_cap_{k}_{i}_{cap_index}", material_class_id="rubber.smooth_plain",
            )
    # Pin boss for the locking brace: two cheeks with the brace eye between them.
    boss_z = -drop * 0.30
    for cheek, sy in enumerate((-1.0, 1.0)):
        frame.visual(
            Cylinder(radius=0.014, length=0.010),
            origin=Origin(xyz=(0.006, sy * YOKE_Y, boss_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=steel,
            name=f"{prefix}brace_mount_{k}_{cheek}", material_class_id="metal.steel_bare",
        )
    # The yoke web sits BEHIND the pin, clear of the brace bar's whole sweep.
    frame.visual(
        Box((0.010, 2.0 * YOKE_Y + 0.010, 0.028)),
        origin=Origin(xyz=(-0.011, 0.0, boss_z)),
        material=steel,
        name=f"{prefix}brace_boss_web_{k}", material_class_id="metal.steel_bare",
    )
    for strut, sy in enumerate((-1.0, 1.0)):
        _tube(
            frame,
            (0.0, sy * YOKE_Y, 0.0),
            (-0.011, sy * YOKE_Y, boss_z),
            0.007, steel, f"{prefix}brace_boss_strut_{k}_{strut}",
        )
    return top_y


def _build_trestle_support(
    model: ArticulatedObject, center, leaves, r: ResolvedConfig, mats: dict[str, str], kind: str
) -> list:
    members = []
    tube_r = 0.013
    saddle_bottom = HINGE_DROP - (LEAF_FRAME_DROP - tube_r - 0.0005)
    saddle_top = HINGE_DROP - TOP_T * 0.5 + MOUNT
    saddle_h = saddle_top - saddle_bottom
    saddle_cz = (saddle_top + saddle_bottom) * 0.5
    for k, leaf in enumerate(leaves):
        frame = model.part(
            f"support_system__{kind}__member_{k}",
            meta={"role": "support_member", "index": k},
        )
        crossbar_half = _trestle_tubes(frame, r, mats, kind, k)
        for s_index, sy in enumerate((-1.0, 1.0)):
            leaf.visual(
                Box((0.030, 0.052, saddle_h)),
                origin=Origin(
                    xyz=(r.frame_u_m, sy * min(0.85 * crossbar_half, r.frame_half_m), saddle_cz)
                ),
                material=mats["steel"],
                name=f"support_system__{kind}__frame_saddle_{k}_{s_index}", material_class_id="metal.steel_bare",
            )
        _axis_joint(
            model,
            name=f"leaf_{k}_to_support_member_{k}",
            parent=leaf,
            child=frame,
            point=(r.frame_u_m, 0.0, HINGE_DROP - LEAF_FRAME_DROP),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            lower=-TRESTLE_STOW,
            upper=0.0,
            effort=55.0,
            velocity=1.2,
            mimic=Mimic(
                joint=f"center_to_leaf_{k}", multiplier=-TRESTLE_STOW / LEAF_FOLD, offset=0.0
            ),
            meta={"positive_motion": "swings the stored trestle back down to the floor"},
        )
        brace = model.part(
            f"support_system__{kind}__brace_{k}",
            meta={"role": "support_brace", "index": k},
        )
        brace.visual(
            Cylinder(radius=0.010, length=2.0 * YOKE_Y - 0.011),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"support_system__{kind}__brace_eye_{k}", material_class_id="metal.steel_bare",
        )
        _tube(
            brace,
            (0.0, 0.0, 0.0),
            (0.062, 0.0, -0.150),
            0.006,
            mats["steel"],
            f"support_system__{kind}__brace_bar_{k}",
        )
        brace.visual(
            Box((0.024, 0.018, 0.030)),
            origin=Origin(xyz=(0.062, 0.0, -0.150)),
            material=mats["steel"],
            name=f"support_system__{kind}__locking_tab_{k}", material_class_id="metal.steel_bare",
        )
        _axis_joint(
            model,
            name=f"support_member_{k}_to_brace_{k}",
            parent=frame,
            child=brace,
            point=(0.006, 0.0, -r.frame_drop_m * 0.30),
            axis=(0.0, 1.0, 0.0),
            radial=(1.0, 0.0, 0.0),
            lower=-1.25,
            upper=0.0,
            effort=12.0,
            velocity=1.6,
            mimic=Mimic(
                joint=f"center_to_leaf_{k}", multiplier=1.25 / LEAF_FOLD, offset=-1.25
            ),
            meta={"positive_motion": "swings the locking brace out of its stored clip"},
        )
        members.append(frame)
    return members


def _support_system_center_pedestal_build(
    model: ArticulatedObject, center, leaves, r: ResolvedConfig, mats: dict[str, str]
) -> list:
    members = []
    y_end = r.y_end_m
    rp = r.ped_radius_m
    column_h = r.ped_top_z - r.ped_hub_z
    profile = [
        (0.0, 0.0),
        (rp * 1.45, 0.0),
        (rp * 1.45, 0.022),
        (rp, 0.060),
        (rp * 0.92, column_h * 0.55),
        (rp, column_h - 0.012),
        (rp * 1.25, column_h),
        (0.0, column_h),
    ]
    center.visual(
        mesh_from_geometry(LatheGeometry(profile, segments=36), "pedestal_column_mesh"),
        origin=Origin(xyz=(0.0, 0.0, r.ped_hub_z)),
        material=mats["steel"],
        name="support_system__center_pedestal__column", material_class_id="metal.steel_bare",
    )
    for i, sy in enumerate((-1.0, 1.0)):
        center.visual(
            Box((rp * 1.4, 0.036, r.under_z - r.ped_top_z + 0.014)),
            origin=Origin(xyz=(0.0, sy * 0.52 * y_end, (r.ped_top_z + r.under_z) * 0.5)),
            material=mats["steel"],
            name=f"pedestal_riser_{i}", material_class_id="metal.steel_bare",
        )
    center.visual(
        Box((rp * 1.4, 1.06 * y_end, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, r.ped_top_z - 0.004)),
        material=mats["steel"],
        name="pedestal_head_plate", material_class_id="metal.steel_bare",
    )
    for k in range(3):
        theta = 2.0 * math.pi * k / 3.0
        hub_r = rp * 1.45 + 0.014
        hub_x = hub_r * math.cos(theta)
        hub_y = hub_r * math.sin(theta)
        for cheek, sy in enumerate((-1.0, 1.0)):
            center.visual(
                Box((0.044, 0.010, 0.048)),
                origin=Origin(
                    xyz=(
                        hub_x - sy * 0.0295 * math.sin(theta) - 0.014 * math.cos(theta),
                        hub_y + sy * 0.0295 * math.cos(theta) - 0.014 * math.sin(theta),
                        r.ped_hub_z,
                    ),
                    rpy=(0.0, 0.0, theta),
                ),
                material=mats["steel"],
                name=f"pedestal_hub_cheek_{k}_{cheek}", material_class_id="metal.steel_bare",
            )
        foot = model.part(
            f"support_system__center_pedestal__member_{k}",
            meta={"role": "support_member", "index": k},
        )
        arm = r.ped_arm_m
        loft = LoftGeometry(
            [
                _square_loop(0.010, 0.0, 0.0, 0.038),
                _square_loop(arm * 0.45, 0.0, -0.014, 0.032),
                _square_loop(arm, 0.0, -0.028, 0.026),
            ],
            cap=True,
            closed=True,
        )
        foot.visual(
            mesh_from_geometry(loft, f"pedestal_foot_arm_mesh_{k}"),
            material=mats["steel"],
            name=f"support_system__center_pedestal__foot_arm_{k}", material_class_id="metal.steel_bare",
        )
        foot.visual(
            Cylinder(radius=0.011, length=0.048),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"support_system__center_pedestal__hinge_knuckle_{k}", material_class_id="metal.steel_bare",
        )
        pad_top = -0.018
        pad_bottom = -(r.ped_hub_z - 0.012)
        foot.visual(
            Box((0.046, 0.046, pad_top - pad_bottom)),
            origin=Origin(xyz=(arm - 0.014, 0.0, (pad_top + pad_bottom) * 0.5)),
            material=mats["steel"],
            name=f"support_system__center_pedestal__floor_pad_{k}", material_class_id="metal.steel_bare",
        )
        foot.visual(
            Cylinder(radius=0.019, length=0.012),
            origin=Origin(xyz=(arm - 0.014, 0.0, pad_bottom + 0.002)),
            material=mats["rubber"],
            name=f"support_system__center_pedestal__foot_cap_{k}", material_class_id="rubber.smooth_plain",
        )
        _tube(
            foot,
            (0.008, 0.0, -0.004),
            (arm * 0.55, 0.0, -0.044),
            0.005,
            mats["steel"],
            f"support_system__center_pedestal__locking_brace_{k}",
        )
        _axis_joint(
            model,
            name=f"center_to_support_member_{k}",
            parent=center,
            child=foot,
            point=(hub_x, hub_y, r.ped_hub_z),
            axis=(-math.sin(theta), math.cos(theta), 0.0),
            radial=(math.cos(theta), math.sin(theta), 0.0),
            lower=-r.ped_fold_rad,
            upper=0.0,
            effort=55.0,
            velocity=1.0,
            meta={"positive_motion": "folds the pedestal foot up against the column"},
        )
        members.append(foot)
    return members


_TRESTLE_KINDS = ("narrow_u_trestle", "broad_end_trestle", "x_braced_trestle", "splayed_aframe")


def _support_system_narrow_u_trestle_build(model, center, leaves, r, mats):
    return _build_trestle_support(model, center, leaves, r, mats, "narrow_u_trestle")


def _support_system_broad_end_trestle_build(model, center, leaves, r, mats):
    return _build_trestle_support(model, center, leaves, r, mats, "broad_end_trestle")


def _support_system_x_braced_trestle_build(model, center, leaves, r, mats):
    return _build_trestle_support(model, center, leaves, r, mats, "x_braced_trestle")


def _support_system_splayed_aframe_build(model, center, leaves, r, mats):
    return _build_trestle_support(model, center, leaves, r, mats, "splayed_aframe")


_SUPPORT_BUILDERS = {
    "corner_fold_legs": _support_system_corner_fold_legs_build,
    "narrow_u_trestle": _support_system_narrow_u_trestle_build,
    "broad_end_trestle": _support_system_broad_end_trestle_build,
    "x_braced_trestle": _support_system_x_braced_trestle_build,
    "splayed_aframe": _support_system_splayed_aframe_build,
    "center_pedestal": _support_system_center_pedestal_build,
}


# --- leaf stay candidates ---------------------------------------------------
# Every stay hangs from its own leaf and reaches INBOARD to bear on the outer
# face of the centre apron.  Its local +X therefore points toward the seam, and
# its whole envelope stays outboard of the space the folding legs sweep.
def _leaf_stay_prop_arm_build(stay, r: ResolvedConfig, mats: dict[str, str], tag: str) -> None:
    arm = r.stay_arm_m
    stay.visual(
        Box((arm, 0.030, 0.020)),
        origin=Origin(xyz=(arm * 0.5, 0.0, 0.0)),
        material=mats["steel"],
        name=f"leaf_stay__prop_arm__arm_bar_{tag}", material_class_id="metal.steel_bare",
    )
    stay.visual(
        Cylinder(radius=0.019, length=STAY_HUB_H),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name=f"leaf_stay__prop_arm__pivot_hub_{tag}", material_class_id="metal.steel_bare",
    )
    stay.visual(
        Box((0.014, 0.036, 0.020)),
        origin=Origin(xyz=(arm - 0.007, 0.0, 0.0)),
        material=mats["steel"],
        name=f"leaf_stay__prop_arm__contact_pad_{tag}", material_class_id="metal.steel_bare",
    )


def _leaf_stay_scissor_link_build(stay, r: ResolvedConfig, mats: dict[str, str], tag: str) -> None:
    arm = r.stay_arm_m
    tip_x = arm - 0.014
    half = 0.009
    for i, sy in enumerate((-1.0, 1.0)):
        _tube(
            stay,
            (0.0, sy * half, -0.009),
            (tip_x, -sy * half, 0.009),
            0.007,
            mats["steel"],
            f"leaf_stay__scissor_link__scissor_arm_{tag}_{i}",
        )
    mid = (tip_x * 0.5, 0.0, 0.0)
    stay.visual(
        Cylinder(radius=0.019, length=STAY_HUB_H),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name=f"leaf_stay__scissor_link__pivot_hub_{tag}", material_class_id="metal.steel_bare",
    )
    stay.visual(
        Cylinder(radius=0.009, length=STAY_PIN_L),
        origin=Origin(xyz=mid, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name=f"leaf_stay__scissor_link__pivot_pin_{tag}", material_class_id="metal.steel_bare",
    )
    for i, sy in enumerate((-0.009, 0.009)):
        stay.visual(
            Cylinder(radius=0.012, length=0.006),
            origin=Origin(xyz=(mid[0], sy, mid[2]), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"leaf_stay__scissor_link__pivot_washer_{tag}_{i}", material_class_id="metal.steel_bare",
        )
    for i, (bx, by, bz) in enumerate(
        (
            (0.0, -half, -0.013),
            (0.0, half, -0.013),
            (tip_x, -half, 0.013),
            (tip_x, half, 0.013),
        )
    ):
        stay.visual(
            Box((0.024, 0.014, 0.016)),
            origin=Origin(xyz=(bx, by, bz)),
            material=mats["steel"],
            name=f"leaf_stay__scissor_link__end_bracket_{tag}_{i}", material_class_id="metal.steel_bare",
        )
    stay.visual(
        Box((0.014, 0.036, 0.020)),
        origin=Origin(xyz=(arm - 0.007, 0.0, 0.0)),
        material=mats["steel"],
        name=f"leaf_stay__scissor_link__contact_pad_{tag}", material_class_id="metal.steel_bare",
    )


def _leaf_stay_slide_rail_build(stay, r: ResolvedConfig, mats: dict[str, str], tag: str) -> None:
    """The pull-out bar itself; it rides in the carrier guide along +X."""
    stay.visual(
        Box((RAIL_BODY, 0.020, 0.022)),
        origin=Origin(xyz=(RAIL_START + RAIL_BODY * 0.5, 0.0, 0.0)),
        material=mats["wood"],
        name=f"leaf_stay__slide_rail__rail_bar_{tag}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
    )
    stay.visual(
        Box((0.014, 0.019, 0.021)),
        origin=Origin(xyz=(RAIL_START + RAIL_BODY - 0.007, 0.0, 0.0)),
        material=mats["wood_edge"],
        name=f"leaf_stay__slide_rail__rail_stop_{tag}", material_class_id=("wood.mahogany_teak_dark" if r.palette_style in {"warm_oak", "walnut", "black_stain"} else "wood.natural_generic"),
    )
    stay.visual(
        Box((0.012, 0.019, 0.020)),
        origin=Origin(xyz=(RAIL_START + RAIL_BODY - 0.002, 0.0, 0.0)),
        material=mats["steel"],
        name=f"leaf_stay__slide_rail__contact_pad_{tag}", material_class_id="metal.steel_bare",
    )
    for i, dx in enumerate((-0.020, 0.014)):
        stay.visual(
            Cylinder(radius=0.005, length=0.006),
            origin=Origin(xyz=(RAIL_START + RAIL_BODY * 0.5 + dx, 0.0, 0.010)),
            material=mats["steel"],
            name=f"leaf_stay__slide_rail__rail_screw_{tag}_{i}", material_class_id="metal.steel_bare",
        )


def _build_leaf_stays(
    model: ArticulatedObject, center, leaves, r: ResolvedConfig, mats: dict[str, str]
) -> list:
    units = []
    for side_index, leaf in enumerate(leaves):
        for j, y in enumerate(r.stay_y):
            tag = f"{side_index}_{j}"
            # Boss let into the leaf underside; the stay bears up against it.
            # Yoke cheeks straddle the stay hub so the pivot axis runs through
            # real hardware on the leaf, not past the bottom of a solid block.
            boss_bot = HINGE_DROP - STAY_DROP - 0.021
            boss_top = HINGE_DROP - TOP_T * 0.5 + MOUNT
            for cheek, sy in enumerate((-1.0, 1.0)):
                leaf.visual(
                    Box((0.052, 0.010, boss_top - boss_bot)),
                    origin=Origin(
                        xyz=(r.stay_pivot_u, y + sy * 0.024, (boss_bot + boss_top) * 0.5)
                    ),
                    material=mats["steel"],
                    name=f"stay_bracket_boss_{tag}_{cheek}", material_class_id="metal.steel_bare",
                )
            leaf.visual(
                Box((0.052, 0.058, 0.010)),
                origin=Origin(
                    xyz=(r.stay_pivot_u, y, boss_top - 0.005)
                ),
                material=mats["steel"],
                name=f"stay_bracket_web_{tag}", material_class_id="metal.steel_bare",
            )
            point = (r.stay_pivot_u, y, HINGE_DROP - STAY_DROP)
            stay = model.part(
                f"leaf_stay__{r.leaf_stay}__unit_{tag}",
                meta={"role": "leaf_stay_unit", "index": len(units)},
            )
            if r.leaf_stay == "slide_rail":
                _leaf_stay_slide_rail_build(stay, r, mats, tag)
                # Guide let into the leaf underside, straddling the rail bar.
                guide_len = RAIL_START + r.stay_travel_m + 0.030
                for i, sy in enumerate((-1.0, 1.0)):
                    leaf.visual(
                        Box((guide_len, 0.009, 0.038)),
                        origin=Origin(
                            xyz=(
                                r.stay_pivot_u - guide_len * 0.5,
                                y + sy * 0.0142,
                                HINGE_DROP - STAY_DROP,
                            )
                        ),
                        material=mats["steel"],
                        name=f"stay_guide_cheek_{tag}_{i}", material_class_id="metal.steel_bare",
                    )
                leaf.visual(
                    Box((guide_len, 0.040, 0.008)),
                    origin=Origin(
                        xyz=(
                            r.stay_pivot_u - guide_len * 0.5,
                            y,
                            HINGE_DROP - STAY_DROP - 0.0148,
                        )
                    ),
                    material=mats["steel"],
                    name=f"stay_guide_floor_{tag}", material_class_id="metal.steel_bare",
                )
                model.articulation(
                    f"leaf_{side_index}_to_leaf_stay_{j}",
                    ArticulationType.PRISMATIC,
                    parent=leaf,
                    child=stay,
                    origin=Origin(xyz=point, rpy=(0.0, 0.0, math.pi)),
                    axis=(1.0, 0.0, 0.0),
                    motion_limits=MotionLimits(
                        lower=0.0, upper=r.stay_travel_m, effort=90.0, velocity=0.25
                    ),
                    meta={"positive_motion": "runs the leaf rail out toward the seam"},
                )
            else:
                if r.leaf_stay == "prop_arm":
                    _leaf_stay_prop_arm_build(stay, r, mats, tag)
                else:
                    _leaf_stay_scissor_link_build(stay, r, mats, tag)
                _axis_joint(
                    model,
                    name=f"leaf_{side_index}_to_leaf_stay_{j}",
                    parent=leaf,
                    child=stay,
                    point=point,
                    axis=(0.0, 1.0, 0.0),
                    radial=(-1.0, 0.0, 0.0),
                    lower=0.0,
                    upper=r.stay_stow_rad,
                    effort=25.0,
                    velocity=1.5,
                    meta={"positive_motion": "folds the leaf stay up under its leaf"},
                )
            units.append(stay)
    return units


# --- assembly ---------------------------------------------------------------
def build_picturex_0611_folding_table3(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_Folding_table3",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "two hinged drop leaves over a collapsible support system",
        },
    )
    mats = _materials(model, r)
    center = _build_center(model, r, mats)
    leaves = [_build_leaf(model, center, r, mats, index) for index in range(2)]
    _SUPPORT_BUILDERS[r.support_system](model, center, leaves, r, mats)
    _build_leaf_stays(model, center, leaves, r, mats)

    leaf_joints = [f"center_to_leaf_{i}" for i in range(2)]
    if r.support_system in _TRESTLE_KINDS:
        support_joints = [f"leaf_{k}_to_support_member_{k}" for k in range(2)]
        brace_joints = [f"support_member_{k}_to_brace_{k}" for k in range(2)]
    else:
        support_joints = [
            f"center_to_support_member_{k}" for k in range(r.support_member_count)
        ]
        brace_joints = []

    by_name = {j.name: j for j in model.articulations}
    deployed = {name: 0.0 for name in leaf_joints + support_joints + brace_joints}
    folded_leaves = dict(deployed)
    for name in leaf_joints:
        folded_leaves[name] = LEAF_FOLD
    stored = dict(folded_leaves)
    for name in support_joints:
        limits = by_name[name].motion_limits
        stored[name] = limits.lower if limits.lower != 0.0 else limits.upper
    model.meta["risk_poses"] = (deployed, folded_leaves, stored)
    model.meta["coupled_joint_pairs"] = tuple(
        (leaf_joints[k % 2], name) for k, name in enumerate(support_joints)
    )
    return model


def build_seeded_picturex_0611_folding_table3(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_folding_table3(config_from_seed(seed), assets=assets)


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_folding_table3_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    centers = _parts_by_role(model, "table_center")
    leaves = _parts_by_role(model, "drop_leaf")
    members = _parts_by_role(model, "support_member")
    stays = _parts_by_role(model, "leaf_stay_unit")
    joints = {j.name: j for j in model.articulations}
    leaf_joints = [joints.get(f"center_to_leaf_{i}") for i in range(2)]

    ctx.check(
        "category_anchor: both drop leaves fold on real hinges",
        len(centers) == 1
        and len(leaves) == 2
        and bool(model.root_parts())
        and model.root_parts()[0].name == "table_center"
        and all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and j.parent == "table_center"
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and abs(j.motion_limits.upper - LEAF_FOLD) < 1e-6
            for j in leaf_joints
        ),
        details=f"leaves={len(leaves)} joints={[getattr(j, 'name', None) for j in leaf_joints]}",
    )

    if r.support_system in _TRESTLE_KINDS:
        support_joints = [joints.get(f"leaf_{k}_to_support_member_{k}") for k in range(2)]
        expected_parent = {f"top_profile__{r.top_profile}__drop_leaf_{k}" for k in range(2)}
    else:
        support_joints = [
            joints.get(f"center_to_support_member_{k}") for k in range(r.support_member_count)
        ]
        expected_parent = {"table_center"}

    # Preflight never materialises meshes, so every AABB here is read from a
    # primitive element rather than a lofted/extruded one.
    foot_elems = {
        "corner_fold_legs": [f"support_system__corner_fold_legs__foot_pad_{k}" for k in range(4)],
        "center_pedestal": [
            f"support_system__center_pedestal__foot_cap_{k}" for k in range(3)
        ],
    }.get(
        r.support_system,
        [
            f"support_system__{r.support_system}__foot_cap_{k}_{i}_{c}"
            for k in range(2)
            for i in range(2)
            for c in range(2)
        ],
    )
    floor_ok = bool(members)
    floor_detail = []
    for member in members:
        best = None
        for elem in foot_elems:
            box = ctx.part_element_world_aabb(member, elem=elem)
            if box is not None:
                best = box[0][2] if best is None else min(best, box[0][2])
        floor_detail.append(None if best is None else round(best, 4))
        if best is None or best > 0.035 or best < -0.015:
            floor_ok = False

    ctx.check(
        "category_anchor: the support system stands the table on the floor",
        len(members) == r.support_member_count
        and floor_ok
        and all(
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and j.parent in expected_parent
            and j.motion_limits is not None
            and abs(j.motion_limits.upper - j.motion_limits.lower) > 0.5
            for j in support_joints
        ),
        details=f"members={len(members)} bottoms={floor_detail}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    profile_ok = {
        "round_arc": abs(r.prof_rx - r.prof_ry) < 1e-9 and r.prof_hs == 0.0 and r.prof_dr == 0.0,
        "ellipse_oval": (
            r.prof_hs == 0.0
            and r.prof_dr == 0.0
            and abs(r.prof_rx - r.top_width_m * 0.5) < 1e-9
        ),
        "racetrack": r.prof_hs > 0.0,
        "d_leaf_rect": r.prof_dr > 0.0,
    }[r.top_profile]
    ctx.check(
        "category_anchor: top_profile identity",
        profile_ok
        and f"top_profile__{r.top_profile}__center_slab" in visual_names
        and all(
            f"top_profile__{r.top_profile}__leaf_slab_{i}" in visual_names for i in range(2)
        ),
        details=(
            f"top_profile={r.top_profile} rx={r.prof_rx} ry={r.prof_ry} "
            f"hs={r.prof_hs} dr={r.prof_dr}"
        ),
    )

    support_marker = {
        "corner_fold_legs": "corner_fold_legs__wood_leg_",
        "narrow_u_trestle": "narrow_u_trestle__lower_stretcher_",
        "broad_end_trestle": "broad_end_trestle__side_tube_",
        "x_braced_trestle": "x_braced_trestle__pivot_pin_",
        "splayed_aframe": "splayed_aframe__diagonal_brace_",
        "center_pedestal": "center_pedestal__foot_arm_",
    }[r.support_system]
    ctx.check(
        "category_anchor: support_system identity",
        any(support_marker in n for n in visual_names),
        details=f"support_system={r.support_system}",
    )

    stay_marker = {
        "prop_arm": "prop_arm__contact_pad_",
        "slide_rail": "slide_rail__rail_stop_",
        "scissor_link": "scissor_link__pivot_washer_",
    }[r.leaf_stay]
    ctx.check(
        "category_anchor: leaf_stay identity",
        len(stays) == r.stay_unit_total and any(stay_marker in n for n in visual_names),
        details=f"leaf_stay={r.leaf_stay} units={len(stays)}",
    )

    stay_link_ok = True
    leaf_names = [f"top_profile__{r.top_profile}__drop_leaf_{i}" for i in range(2)]
    want = (
        ArticulationType.PRISMATIC
        if r.leaf_stay == "slide_rail"
        else ArticulationType.REVOLUTE
    )
    for side_index in range(2):
        for j in range(r.stay_per_leaf):
            joint = joints.get(f"leaf_{side_index}_to_leaf_stay_{j}")
            if (
                joint is None
                or joint.parent != leaf_names[side_index]
                or joint.articulation_type != want
                or joint.motion_limits is None
                or abs(joint.motion_limits.upper - joint.motion_limits.lower) < 0.02
            ):
                stay_link_ok = False
    ctx.check(
        "each leaf stay works on its own leaf",
        stay_link_ok,
        details=f"stay_per_leaf={r.stay_per_leaf} kind={r.leaf_stay}",
    )

    # A deployed stay reaches toward the seam but always stops outboard of it,
    # so nothing carried on a leaf can swing in over the centre section.
    pad_elem = f"leaf_stay__{r.leaf_stay}__contact_pad_0_0"
    stay_joint = joints.get("leaf_0_to_leaf_stay_0")
    # q=0 is the deployed pose for the swinging stays; the rail deploys at full travel.
    deployed = r.stay_travel_m if r.leaf_stay == "slide_rail" else 0.0
    with ctx.pose({stay_joint: deployed}):
        pad_box = ctx.part_element_world_aabb(stays[0], elem=pad_elem)
    reach_in = r.hinge_x_m + STAY_INBOARD
    ctx.check(
        "the deployed leaf stay reaches the seam without crossing it",
        pad_box is not None
        and abs(pad_box[0][0] - reach_in) <= 0.004
        and pad_box[0][0] > r.hinge_x_m + 0.020
        and pad_box[1][2] < r.under_z,
        details=f"pad={pad_box} reach_in={reach_in} hinge_x={r.hinge_x_m}",
    )

    leaf = leaves[0]
    batten = "leaf_batten_0"
    rest = ctx.part_element_world_aabb(leaf, elem=batten)
    with ctx.pose({leaf_joints[0]: LEAF_FOLD}):
        folded = ctx.part_element_world_aabb(leaf, elem=batten)
    ctx.check(
        "leaf 0 folds straight down",
        rest is not None
        and folded is not None
        and folded[0][2] < rest[0][2] - r.leaf_reach_m * 0.40
        and folded[1][0] < rest[1][0] - r.leaf_reach_m * 0.40,
        details=f"rest={rest} folded={folded} hinge_x={r.hinge_x_m}",
    )

    ctx.check(
        "stay stations are pitched along the seam and clear the support station",
        len(r.stay_y) == r.stay_per_leaf
        and all(abs(y) <= 0.15 * r.top_length_m + 1e-9 for y in r.stay_y)
        and r.stay_pivot_u + 0.030 < r.frame_u_m
        and r.leaf_reach_m > 0.24,
        details=f"stay_y={r.stay_y} pivot_u={r.stay_pivot_u} frame_u={r.frame_u_m}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "narrow_center_widest_top_pedestal",
        {
            "top_profile": "round_arc",
            "support_system": "center_pedestal",
            "leaf_stay": "slide_rail",
            "stay_per_leaf": 3,
            "top_length_m": 0.82,
            "top_width_m": 1.32,
            "center_width_ratio": 0.28,
            "table_height_m": 0.700,
        },
        reason=(
            "narrowest centre strip with the longest leaves, three slide rails and "
            "the pedestal head all inside it"
        ),
    ),
    corner_case(
        "widest_center_shortest_leaf_corner_legs",
        {
            "top_profile": "d_leaf_rect",
            "support_system": "corner_fold_legs",
            "leaf_stay": "prop_arm",
            "stay_per_leaf": 1,
            "top_length_m": 1.10,
            "top_width_m": 0.98,
            "center_width_ratio": 0.40,
            "table_height_m": 0.780,
        },
        reason="widest centre spine and shortest D leaf on four corner legs with one prop arm",
    ),
    corner_case(
        "racetrack_broad_trestle_three_scissors",
        {
            "top_profile": "racetrack",
            "support_system": "broad_end_trestle",
            "leaf_stay": "scissor_link",
            "stay_per_leaf": 3,
            "top_length_m": 1.10,
            "top_width_m": 1.32,
            "center_width_ratio": 0.28,
            "table_height_m": 0.780,
        },
        reason="largest envelope: broad trestles on both leaves with three scissor stays each",
    ),
    corner_case(
        "splayed_aframe_tight_center",
        {
            "top_profile": "ellipse_oval",
            "support_system": "splayed_aframe",
            "leaf_stay": "slide_rail",
            "stay_per_leaf": 2,
            "top_length_m": 0.82,
            "top_width_m": 0.98,
            "center_width_ratio": 0.28,
            "table_height_m": 0.700,
        },
        reason=(
            "smallest table: widest A-frame splay under the shortest leaf with rails "
            "retracting into the tightest apron"
        ),
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
    "build_picturex_0611_folding_table3",
    "build_seeded_picturex_0611_folding_table3",
    "run_picturex_0611_folding_table3_tests",
]
