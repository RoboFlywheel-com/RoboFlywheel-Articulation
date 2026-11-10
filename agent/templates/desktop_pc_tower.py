# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

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

CaseForm = Literal[
    "mid_tower",
    "full_tower",
    "mini_itx_cube",
    "sff_htpc",
    "rackmount_tower",
    "nas_tower",
    "open_frame",
]
AccessLayout = Literal[
    "side_hinged",
    "front_hinged",
    "side_and_front",
    "top_hinged",
    "top_sliding",
    "multi_panel",
]
FrontBayLayout = Literal[
    "none",
    "single_optical",
    "dual_optical",
    "hot_swap_stack",
    "mesh_door",
    "solid_bezel",
]
SidePanelStyle = Literal["solid_steel", "tempered_glass", "framed_glass", "open_frame"]
VentStyle = Literal["front_mesh", "vertical_slots", "side_ribs", "top_filter", "minimal"]
IoStyle = Literal["power_button_only", "top_io_cluster", "status_light_strip", "gaming_rgb"]
TopAccessStyle = Literal["none", "hinged_filter", "sliding_lid"]
DriveCageStyle = Literal["none", "swing_out_shelves"]
MaterialStyle = Literal["black_gaming", "white_workstation", "nas_black", "clear_gray_lab"]

SOURCE_IDS = {
    "S2": "data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L70-L309",
    "S4": "data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L368-L440",
    "S6": (
        "data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/"
        "revisions/rev_000001/model.py:L34-L142"
    ),
    "S8": (
        "data/records/rec_desktop_pc_tower_42f2ff19b3f346b0b72b16faae6ef3cb/"
        "revisions/rev_000001/model.py:L152-L271"
    ),
}

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_gaming": {
        "case": (0.035, 0.040, 0.046, 1.0),
        "trim": (0.14, 0.15, 0.16, 1.0),
        "drawer": (0.055, 0.058, 0.064, 1.0),
        "rail": (0.38, 0.39, 0.40, 1.0),
        "accent": (0.00, 0.48, 0.72, 1.0),
        "cavity": (0.018, 0.020, 0.024, 1.0),
    },
    "white_workstation": {
        "case": (0.55, 0.55, 0.52, 1.0),
        "trim": (0.31, 0.32, 0.34, 1.0),
        "drawer": (0.20, 0.21, 0.23, 1.0),
        "rail": (0.48, 0.49, 0.50, 1.0),
        "accent": (0.02, 0.50, 0.72, 1.0),
        "cavity": (0.060, 0.064, 0.070, 1.0),
    },
    "nas_black": {
        "case": (0.050, 0.052, 0.058, 1.0),
        "trim": (0.18, 0.19, 0.20, 1.0),
        "drawer": (0.070, 0.072, 0.080, 1.0),
        "rail": (0.43, 0.44, 0.45, 1.0),
        "accent": (0.06, 0.42, 0.90, 1.0),
        "cavity": (0.025, 0.027, 0.031, 1.0),
    },
    "clear_gray_lab": {
        "case": (0.46, 0.46, 0.42, 0.34),
        "trim": (0.31, 0.32, 0.34, 1.0),
        "drawer": (0.26, 0.27, 0.29, 1.0),
        "rail": (0.42, 0.43, 0.44, 1.0),
        "accent": (0.02, 0.48, 0.68, 1.0),
        "cavity": (0.035, 0.038, 0.042, 1.0),
    },
}


@dataclass(frozen=True)
class DesktopPcTowerConfig:
    case_form: CaseForm = "nas_tower"
    access_layout: AccessLayout = "front_hinged"
    front_bay_layout: FrontBayLayout = "hot_swap_stack"
    side_panel_style: SidePanelStyle = "solid_steel"
    vent_style: VentStyle = "side_ribs"
    io_style: IoStyle = "status_light_strip"
    top_access_style: TopAccessStyle = "none"
    drive_cage_style: DriveCageStyle = "none"
    material_style: MaterialStyle = "nas_black"
    case_height: float = 0.56
    case_width: float = 0.30
    case_depth: float = 0.52
    drive_tray_count: int = 4
    tray_travel: float = 0.14
    drawer_height: float = 0.064
    drawer_width_ratio: float = 0.74
    drawer_depth_ratio: float = 0.64
    status_light_count: int = 3
    name: str = "reference_desktop_pc_tower"


@dataclass(frozen=True)
class ResolvedDesktopPcTowerConfig:
    case_form: CaseForm
    access_layout: AccessLayout
    front_bay_layout: FrontBayLayout
    side_panel_style: SidePanelStyle
    vent_style: VentStyle
    io_style: IoStyle
    top_access_style: TopAccessStyle
    drive_cage_style: DriveCageStyle
    material_style: MaterialStyle
    case_height: float
    case_width: float
    case_depth: float
    drive_tray_count: int
    tray_travel: float
    drawer_height: float
    drawer_width: float
    drawer_depth: float
    drawer_pitch: float
    bay_top_z: float
    status_light_count: int
    name: str


def config_from_seed(seed: int) -> DesktopPcTowerConfig:
    rng = random.Random(seed)
    tray_count = rng.randint(2, 7)
    drawer_height = round(rng.uniform(0.044, 0.075), 3)
    min_height = 0.16 + tray_count * (drawer_height + 0.010)
    return DesktopPcTowerConfig(
        case_form=rng.choice(("nas_tower", "mini_itx_cube", "mid_tower", "rackmount_tower")),
        access_layout="front_hinged",
        front_bay_layout="hot_swap_stack",
        side_panel_style="solid_steel",
        vent_style=rng.choice(("side_ribs", "front_mesh", "top_filter", "minimal")),
        io_style=rng.choice(("status_light_strip", "power_button_only", "top_io_cluster")),
        top_access_style="none",
        drive_cage_style="none",
        material_style=rng.choice(
            ("black_gaming", "white_workstation", "nas_black", "clear_gray_lab")
        ),
        case_height=round(rng.uniform(min_height, min(0.92, min_height + 0.28)), 3),
        case_width=round(rng.uniform(0.26, 0.48), 3),
        case_depth=round(rng.uniform(0.42, 0.66), 3),
        drive_tray_count=tray_count,
        tray_travel=round(rng.uniform(0.10, 0.22), 3),
        drawer_height=drawer_height,
        drawer_width_ratio=round(rng.uniform(0.62, 0.80), 3),
        drawer_depth_ratio=round(rng.uniform(0.55, 0.72), 3),
        status_light_count=rng.randint(2, 5),
        name=f"seeded_desktop_pc_tower_{seed}",
    )


def resolve_config(config: DesktopPcTowerConfig) -> ResolvedDesktopPcTowerConfig:
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 0.24 <= config.case_width <= 0.55:
        raise ValueError("case_width must be in [0.24, 0.55]")
    if not 0.38 <= config.case_depth <= 0.70:
        raise ValueError("case_depth must be in [0.38, 0.70]")
    if not 2 <= config.drive_tray_count <= 8:
        raise ValueError("drive_tray_count must be in [2, 8]")
    if not 0.035 <= config.drawer_height <= 0.090:
        raise ValueError("drawer_height must be in [0.035, 0.090]")
    if not 0.55 <= config.drawer_width_ratio <= 0.84:
        raise ValueError("drawer_width_ratio must be in [0.55, 0.84]")
    if not 0.48 <= config.drawer_depth_ratio <= 0.76:
        raise ValueError("drawer_depth_ratio must be in [0.48, 0.76]")
    if not 0.08 <= config.tray_travel <= 0.24:
        raise ValueError("tray_travel must be in [0.08, 0.24]")

    count = int(config.drive_tray_count)
    width = float(config.case_width)
    depth = float(config.case_depth)
    drawer_h = float(config.drawer_height)
    drawer_pitch = drawer_h + max(0.010, drawer_h * 0.22)
    top_margin = max(0.060, drawer_h * 0.95)
    bottom_clearance = max(0.090, drawer_h * 1.40)
    required_height = top_margin + bottom_clearance + (count - 1) * drawer_pitch + drawer_h
    height = max(float(config.case_height), required_height)
    height = min(0.95, height)
    if height < required_height:
        drawer_pitch = max(
            drawer_h + 0.006,
            (height - top_margin - bottom_clearance - drawer_h) / max(1, count - 1),
        )

    drawer_w = min(width * float(config.drawer_width_ratio), width - 0.085)
    drawer_d = min(depth * float(config.drawer_depth_ratio), depth - 0.090)
    tray_travel = min(float(config.tray_travel), depth * 0.42)
    bay_top_z = height - top_margin - drawer_h * 0.50

    return ResolvedDesktopPcTowerConfig(
        case_form="nas_tower",
        access_layout="front_hinged",
        front_bay_layout="hot_swap_stack",
        side_panel_style="solid_steel",
        vent_style=config.vent_style,
        io_style=config.io_style,
        top_access_style="none",
        drive_cage_style="none",
        material_style=config.material_style,
        case_height=height,
        case_width=width,
        case_depth=depth,
        drive_tray_count=count,
        tray_travel=tray_travel,
        drawer_height=drawer_h,
        drawer_width=drawer_w,
        drawer_depth=drawer_d,
        drawer_pitch=drawer_pitch,
        bay_top_z=bay_top_z,
        status_light_count=max(0, min(6, int(config.status_light_count))),
        name=config.name,
    )


def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


def _add_box(part, size, xyz, material, name: str) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.paint_coated")


def _center(aabb: tuple[tuple[float, float, float], tuple[float, float, float]] | None):
    if aabb is None:
        return None
    mins, maxs = aabb
    return tuple((lo + hi) * 0.5 for lo, hi in zip(mins, maxs))


def _drawer_z(r: ResolvedDesktopPcTowerConfig, index: int) -> float:
    return r.bay_top_z - index * r.drawer_pitch


def _build_chassis(chassis, r, case, trim, rail, accent, cavity) -> None:
    w, d, h = r.case_width, r.case_depth, r.case_height
    wall_t = min(0.018, max(0.010, w * 0.040))
    face_t = min(0.018, max(0.010, d * 0.028))
    top_t = max(0.012, wall_t * 0.85)
    floor_t = max(0.014, wall_t * 0.95)

    _add_box(chassis, (w, d, floor_t), (0.0, 0.0, floor_t * 0.5), case, "bottom_wall")
    _add_box(chassis, (w, d, top_t), (0.0, 0.0, h - top_t * 0.5), case, "top_wall")
    _add_box(chassis, (wall_t, d, h), (-w * 0.5 + wall_t * 0.5, 0.0, h * 0.5), case, "left_wall")
    _add_box(chassis, (wall_t, d, h), (w * 0.5 - wall_t * 0.5, 0.0, h * 0.5), case, "right_wall")
    _add_box(chassis, (w, face_t, h), (0.0, -d * 0.5 + face_t * 0.5, h * 0.5), case, "rear_wall")

    post_w = max(wall_t, (w - r.drawer_width) * 0.45)
    front_y = d * 0.5 - face_t * 0.5
    _add_box(
        chassis,
        (post_w, face_t, h),
        (-w * 0.5 + post_w * 0.5, front_y, h * 0.5),
        trim,
        "front_left_post",
    )
    _add_box(
        chassis,
        (post_w, face_t, h),
        (w * 0.5 - post_w * 0.5, front_y, h * 0.5),
        trim,
        "front_right_post",
    )
    _add_box(
        chassis,
        (w - 2 * post_w, face_t, floor_t * 1.45),
        (0.0, front_y, floor_t * 0.72),
        trim,
        "front_sill",
    )
    _add_box(
        chassis,
        (w - 2 * post_w, face_t, top_t * 1.60),
        (0.0, front_y, h - top_t * 0.80),
        trim,
        "front_header",
    )

    bay_depth = max(0.060, d - face_t * 3.2)
    bay_y = -d * 0.5 + face_t + bay_depth * 0.5
    for i in range(r.drive_tray_count):
        z = _drawer_z(r, i)
        shelf_z = z - r.drawer_height * 0.55
        _add_box(
            chassis,
            (r.drawer_width + 0.020, bay_depth, 0.004),
            (0.0, bay_y, shelf_z),
            rail,
            f"guide_floor_{i}",
        )
        for side, sx in (("left", -1.0), ("right", 1.0)):
            guide_x = sx * (r.drawer_width * 0.45 + 0.0035)
            _add_box(
                chassis,
                (0.009, bay_depth, max(0.009, r.drawer_height * 0.18)),
                (guide_x, bay_y, z - r.drawer_height * 0.26),
                rail,
                f"guide_side_{i}_{side}",
            )
        if i < r.drive_tray_count - 1:
            divider_z = z - r.drawer_pitch * 0.5
            _add_box(
                chassis,
                (w - 2 * post_w, face_t, 0.006),
                (0.0, front_y, divider_z),
                trim,
                f"bay_divider_{i}",
            )

    cavity_h = max(
        0.035, _drawer_z(r, r.drive_tray_count - 1) - r.drawer_height * 0.5 - floor_t * 2.2
    )
    if cavity_h > 0.040:
        _add_box(
            chassis,
            (w - 2 * post_w, face_t, cavity_h),
            (0.0, front_y, floor_t * 1.25 + cavity_h * 0.5),
            cavity,
            "lower_open_cavity_back",
        )

    if r.vent_style in {"side_ribs", "vertical_slots"}:
        for i in range(max(5, r.drive_tray_count + 2)):
            _add_box(
                chassis,
                (0.004, d * 0.30, 0.010),
                (w * 0.5 + 0.002, -d * 0.08, h * (0.30 + i * 0.045)),
                accent,
                f"side_vent_{i}",
            )
    elif r.vent_style == "front_mesh":
        for suffix, x in (("left", -w * 0.5 + post_w * 0.55), ("right", w * 0.5 - post_w * 0.55)):
            _add_box(
                chassis,
                (0.008, 0.004, h * 0.30),
                (x, d * 0.5 + 0.002, h * 0.30),
                accent,
                f"front_rgb_{suffix}",
            )
    elif r.vent_style == "top_filter":
        for i in range(6):
            _add_box(
                chassis,
                (w * 0.42, 0.006, 0.004),
                (0.0, -d * 0.12 + i * d * 0.040, h + 0.002),
                accent,
                f"top_vent_rib_{i}",
            )

    if r.io_style in {"status_light_strip", "gaming_rgb"}:
        strip_z = min(h - top_t * 2.0, max(floor_t * 3.0, r.bay_top_z + r.drawer_height * 0.45))
        _add_box(
            chassis,
            (0.018, 0.006, 0.10),
            (-w * 0.5 + post_w * 0.50, d * 0.5 + 0.002, strip_z),
            trim,
            "status_strip",
        )
        for i in range(r.status_light_count):
            _add_box(
                chassis,
                (0.014, 0.005, 0.014),
                (
                    -w * 0.5 + post_w * 0.50,
                    d * 0.5 + 0.005,
                    strip_z + (i - r.status_light_count / 2) * 0.020,
                ),
                accent,
                f"status_light_{i}",
            )

    if r.io_style in {"top_io_cluster", "power_button_only", "gaming_rgb"}:
        chassis.visual(
            Cylinder(radius=max(0.010, w * 0.025), length=0.006),
            origin=Origin(xyz=(w * 0.28, d * 0.18, h + 0.003)),
            material=accent,
            name="power_button", material_class_id="tech.control_interface",
        )

    for idx, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        _add_box(
            chassis,
            (0.035, 0.035, 0.012),
            (sx * w * 0.32, sy * d * 0.36, 0.006),
            trim,
            f"foot_{idx}",
        )


def _build_drawer(tray, r, drawer_mat, rail, accent, index: int) -> None:
    h = r.drawer_height
    w = r.drawer_width
    d = r.drawer_depth
    face_t = 0.014
    _add_box(tray, (w, face_t, h), (0.0, face_t * 0.5, 0.0), drawer_mat, "fascia")
    _add_box(tray, (w * 0.90, d, h * 0.70), (0.0, -d * 0.5, -h * 0.02), drawer_mat, "sled")
    for side, sx in (("left", -1.0), ("right", 1.0)):
        _add_box(
            tray,
            (0.010, d * 0.92, h * 0.22),
            (sx * w * 0.43, -d * 0.47, -h * 0.28),
            rail,
            f"runner_{side}",
        )
    _add_box(
        tray, (w * 0.38, 0.005, h * 0.16), (-w * 0.05, face_t + 0.002, 0.0), accent, "pull_recess"
    )
    _add_box(
        tray, (0.014, 0.005, h * 0.18), (w * 0.42, face_t + 0.002, h * 0.12), accent, "release_tab"
    )
    _add_box(
        tray, (0.010, 0.005, 0.010), (-w * 0.43, face_t + 0.002, h * 0.20), accent, "activity_light"
    )
    _ = index


def build_desktop_pc_tower(
    config: DesktopPcTowerConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or DesktopPcTowerConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-pc-tower-assets-")))

    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    case = model.material("pc_case", rgba=palette["case"])
    trim = model.material("pc_trim", rgba=palette["trim"])
    drawer_mat = model.material("pc_drawer", rgba=palette["drawer"])
    rail = model.material("pc_rail", rgba=palette["rail"])
    accent = model.material("pc_accent", rgba=palette["accent"])
    cavity = model.material("pc_cavity", rgba=palette["cavity"])

    chassis = model.part("chassis")
    _build_chassis(chassis, r, case, trim, rail, accent, cavity)

    for i in range(r.drive_tray_count):
        tray = model.part(f"drive_tray_{i}")
        _build_drawer(tray, r, drawer_mat, rail, accent, i)
        front_frame_t = min(0.018, max(0.010, r.case_depth * 0.028))
        drawer_face_t = 0.014
        origin = (
            0.0,
            r.case_depth * 0.5 - front_frame_t - drawer_face_t + 0.001,
            _drawer_z(r, i),
        )
        axis = (0.0, 1.0, 0.0)
        limits = MotionLimits(effort=35.0, velocity=0.35, lower=0.0, upper=r.tray_travel)
        model.articulation(
            f"drive_tray_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=chassis,
            child=tray,
            origin=Origin(xyz=origin),
            axis=axis,
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, axis, origin, limits),
        )

    return model


def build_seeded_desktop_pc_tower(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_desktop_pc_tower(config_from_seed(seed), assets=assets)


def with_overrides(config: DesktopPcTowerConfig, **kwargs: object) -> DesktopPcTowerConfig:
    return replace(config, **kwargs)


def run_desktop_pc_tower_tests(
    object_model: ArticulatedObject, config: DesktopPcTowerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    chassis = object_model.get_part("chassis")
    parts = {part.name for part in object_model.parts}
    joints = {joint.name for joint in object_model.articulations}
    chassis_visuals = {visual.name for visual in chassis.visuals} if chassis is not None else set()

    ctx.check("sealed drawer tower chassis present", "chassis" in parts)
    ctx.check(
        "sealed side walls present",
        {"left_wall", "right_wall", "rear_wall", "top_wall", "bottom_wall"} <= chassis_visuals,
    )
    ctx.check(
        "front bay frame present",
        {"front_left_post", "front_right_post", "front_header", "front_sill"} <= chassis_visuals,
    )
    ctx.check(
        "drawer count matches config",
        len([p for p in parts if p.startswith("drive_tray_")]) == r.drive_tray_count,
    )
    ctx.check(
        "only drawer slide joints are moving",
        joints == {f"drive_tray_slide_{i}" for i in range(r.drive_tray_count)},
    )

    for i in range(r.drive_tray_count):
        joint = object_model.get_articulation(f"drive_tray_slide_{i}")
        tray = object_model.get_part(f"drive_tray_{i}")
        ctx.check(
            f"drive_tray_slide_{i} depth axis",
            joint.axis == (0.0, 1.0, 0.0),
            details=str(joint.axis),
        )
        ctx.check(
            f"drive_tray_slide_{i} retained travel",
            joint.motion_limits is not None and joint.motion_limits.upper <= r.case_depth * 0.45,
        )
        fascia = next((visual for visual in tray.visuals if visual.name == "fascia"), None)
        if fascia is not None:
            rest = ctx.part_element_world_aabb(tray, elem=fascia)
            with ctx.pose({joint: r.tray_travel * 0.85}):
                opened = ctx.part_element_world_aabb(tray, elem=fascia)
            rest_center = _center(rest)
            open_center = _center(opened)
            ctx.check(
                f"drive tray {i} slides outward",
                rest_center is not None
                and open_center is not None
                and open_center[1] > rest_center[1] + r.tray_travel * 0.50,
                details=f"rest={rest}, open={opened}",
            )
            ctx.expect_overlap(
                tray,
                chassis,
                axes="xz",
                min_overlap=min(r.drawer_height * 0.30, 0.020),
                name=f"drive tray {i} remains captured by bay frame",
            )

    for joint in object_model.articulations:
        ctx.check(
            f"{joint.name} metadata complete",
            isinstance(joint.meta, dict)
            and {"type", "axis", "origin", "range"} <= set(joint.meta.keys()),
        )

    return ctx.report()
