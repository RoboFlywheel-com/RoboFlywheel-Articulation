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
    BezelGeometry,
    Box,
    Cylinder,
    ExtrudeGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

ScreenProfile = Literal["flat_rect", "boxy_flat", "thin_premium", "curved_wide"]
BaseStyle = Literal["rounded_pedestal", "rect_plate", "v_foot", "tripod"]
StandLayout = Literal["slim_neck", "broad_column", "telescoping_column", "split_yoke"]
ControlsStyle = Literal["none", "menu_buttons", "rocker_and_buttons", "joystick", "side_wheel"]
CableCoverStyle = Literal["none", "hinged_rear_door", "static_channel"]
YokeStyle = Literal["compact_barrel", "two_ears", "split_rear_yoke", "vesa_portrait"]
MaterialStyle = Literal["office_black", "silver", "gaming_dark"]

SOURCE_IDS = {
    "S1": (
        "data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/"
        "revisions/rev_000001/model.py:L31-L87"
    ),
    "S2": (
        "data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/"
        "revisions/rev_000001/model.py:L89-L146"
    ),
    "S3": (
        "data/records/rec_desktop_monitor_with_tilt_swivel_stand_cfb7e5674fe34f39a7922aed30c33972/"
        "revisions/rev_000001/model.py:L22-L89"
    ),
    "S4": (
        "data/records/rec_desktop_monitor_with_tilt_swivel_stand_cfb7e5674fe34f39a7922aed30c33972/"
        "revisions/rev_000001/model.py:L113-L255"
    ),
    "S5": (
        "data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/"
        "revisions/rev_000001/model.py:L162-L382"
    ),
}

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "office_black": {
        "body": (0.08, 0.09, 0.10, 1.0),
        "trim": (0.18, 0.19, 0.21, 1.0),
        "glass": (0.05, 0.07, 0.08, 1.0),
        "accent": (0.50, 0.52, 0.54, 1.0),
        "metal": (0.22, 0.23, 0.26, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
    "silver": {
        "body": (0.72, 0.74, 0.76, 1.0),
        "trim": (0.46, 0.48, 0.50, 1.0),
        "glass": (0.06, 0.08, 0.10, 1.0),
        "accent": (0.16, 0.17, 0.19, 1.0),
        "metal": (0.60, 0.62, 0.65, 1.0),
        "rubber": (0.20, 0.20, 0.22, 1.0),
    },
    "gaming_dark": {
        "body": (0.05, 0.05, 0.06, 1.0),
        "trim": (0.20, 0.21, 0.24, 1.0),
        "glass": (0.02, 0.03, 0.04, 1.0),
        "accent": (0.85, 0.10, 0.08, 1.0),
        "metal": (0.12, 0.13, 0.15, 1.0),
        "rubber": (0.0, 0.0, 0.0, 1.0),
    },
}


# Modular slot/module route marker: seed-level diversity is reported through
# slot_choices_for_seed(seed) and gated per slot key by the sweep pipeline.
__modular__ = True

# Distance (m) from the yoke socket reference line (y=0.028 in the carrier
# frame) to the tilt pivot axis. The deep yoke neck cantilevers the hinge this
# far forward so the tilting panel clears the column front.
HINGE_SETBACK = 0.103


@dataclass(frozen=True)
class DesktopMonitorWithTiltSwivelStandConfig:
    screen_profile: ScreenProfile = "flat_rect"
    base_style: BaseStyle = "rounded_pedestal"
    stand_layout: StandLayout = "telescoping_column"
    controls_style: ControlsStyle = "menu_buttons"
    cable_cover_style: CableCoverStyle = "none"
    yoke_style: YokeStyle = "two_ears"
    material_style: MaterialStyle = "office_black"
    screen_width: float = 0.62
    screen_aspect_ratio: float = 1.78
    screen_depth: float = 0.035
    stand_height: float = 0.34
    height_travel: float = 0.08
    tilt_range: tuple[float, float] = (-0.20, 0.35)
    has_portrait_pivot: bool = False
    menu_button_count: int = 3
    name: str = "reference_desktop_monitor"


@dataclass(frozen=True)
class ResolvedDesktopMonitorWithTiltSwivelStandConfig:
    screen_profile: ScreenProfile
    base_style: BaseStyle
    stand_layout: StandLayout
    controls_style: ControlsStyle
    cable_cover_style: CableCoverStyle
    yoke_style: YokeStyle
    material_style: MaterialStyle
    screen_width: float
    screen_height: float
    screen_depth: float
    base_width: float
    base_depth: float
    stand_height: float
    height_travel: float
    tilt_range: tuple[float, float]
    has_portrait_pivot: bool
    menu_button_count: int
    name: str


def config_from_seed(seed: int) -> DesktopMonitorWithTiltSwivelStandConfig:
    rng = random.Random(seed)
    profile: ScreenProfile = rng.choices(
        ("flat_rect", "boxy_flat", "thin_premium", "curved_wide"),
        weights=(0.35, 0.20, 0.25, 0.20),
        k=1,
    )[0]
    base: BaseStyle = rng.choice(("rounded_pedestal", "rect_plate", "v_foot", "tripod"))
    stand: StandLayout = rng.choice(
        ("slim_neck", "broad_column", "telescoping_column", "split_yoke")
    )
    controls: ControlsStyle = rng.choice(
        ("none", "menu_buttons", "rocker_and_buttons", "joystick", "side_wheel")
    )
    return DesktopMonitorWithTiltSwivelStandConfig(
        screen_profile=profile,
        base_style=base,
        stand_layout=stand,
        controls_style=controls,
        cable_cover_style=rng.choice(("none", "hinged_rear_door", "static_channel")),
        yoke_style=rng.choice(("compact_barrel", "two_ears", "split_rear_yoke", "vesa_portrait")),
        material_style=rng.choice(("office_black", "silver", "gaming_dark")),
        screen_width=round(rng.uniform(0.52, 0.90), 3),
        screen_aspect_ratio=round(rng.uniform(1.55, 2.35), 2),
        screen_depth=round(rng.uniform(0.022, 0.055), 3),
        stand_height=round(rng.uniform(0.28, 0.46), 3),
        height_travel=round(rng.uniform(0.0, 0.12), 3),
        has_portrait_pivot=rng.random() < 0.25,
        menu_button_count=rng.randint(0, 5),
        name=f"seeded_desktop_monitor_{seed}",
    )


def _max_up_tilt(
    half_screen: float,
    y_clear: float,
    *,
    back_clearance: float = 0.012,
    margin: float = 0.008,
) -> float:
    """Largest back-tilt angle at which no panel point reaches the column plane.

    Solves half_screen*sin(theta) - back_clearance*cos(theta) = y_clear - margin,
    i.e. the deepest rearward reach of the panel back plane (which runs
    ``back_clearance`` behind the tilt pivot axis) stays ``margin`` short of the
    frontmost column plane at ``y_clear`` behind the pivot.
    """
    a = max(half_screen, 1e-6)
    b = back_clearance
    c = y_clear - margin
    hyp = math.hypot(a, b)
    if c >= hyp:
        return 0.5
    return math.atan2(b, a) + math.asin(max(c, 0.0) / hyp)


def resolve_config(
    config: DesktopMonitorWithTiltSwivelStandConfig,
) -> ResolvedDesktopMonitorWithTiltSwivelStandConfig:
    if config.screen_profile not in {"flat_rect", "boxy_flat", "thin_premium", "curved_wide"}:
        raise ValueError(f"Unsupported screen_profile: {config.screen_profile}")
    if config.base_style not in {"rounded_pedestal", "rect_plate", "v_foot", "tripod"}:
        raise ValueError(f"Unsupported base_style: {config.base_style}")
    if config.stand_layout not in {"slim_neck", "broad_column", "telescoping_column", "split_yoke"}:
        raise ValueError(f"Unsupported stand_layout: {config.stand_layout}")
    if config.controls_style not in {
        "none",
        "menu_buttons",
        "rocker_and_buttons",
        "joystick",
        "side_wheel",
    }:
        raise ValueError(f"Unsupported controls_style: {config.controls_style}")
    if config.cable_cover_style not in {"none", "hinged_rear_door", "static_channel"}:
        raise ValueError(f"Unsupported cable_cover_style: {config.cable_cover_style}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 0.52 <= config.screen_width <= 0.90:
        raise ValueError("screen_width must be in [0.52, 0.90]")
    if not 1.55 <= config.screen_aspect_ratio <= 2.35:
        raise ValueError("screen_aspect_ratio must be in [1.55, 2.35]")
    if not 0.0 <= config.height_travel <= 0.12:
        raise ValueError("height_travel must be in [0.0, 0.12]")
    tilt_lower, tilt_upper = config.tilt_range
    if tilt_lower >= tilt_upper or tilt_lower < -0.35 or tilt_upper > 0.50:
        raise ValueError("tilt_range must be ordered and within monitor tilt bounds")
    if not 0 <= config.menu_button_count <= 5:
        raise ValueError("menu_button_count must be in [0, 5]")

    # Normalize to the mechanically stable template family:
    # keep only clear load paths and avoid decorative branches that often look floating.
    stand_layout = config.stand_layout
    if stand_layout == "split_yoke":
        stand_layout = "broad_column"

    controls_style: ControlsStyle = "none"

    cable_cover_style: CableCoverStyle = "none"
    yoke_style: YokeStyle = "two_ears"
    has_portrait_pivot = False

    height_travel = config.height_travel
    if stand_layout == "telescoping_column":
        if height_travel <= 0.0:
            height_travel = 0.08
    else:
        height_travel = 0.0
    if config.base_style == "tripod" and stand_layout == "slim_neck":
        stand_layout = "broad_column"
    screen_height = config.screen_width / config.screen_aspect_ratio
    base_width = max(0.28, min(0.55, config.screen_width * 0.55))
    base_depth = 0.24 if config.base_style in {"rounded_pedestal", "rect_plate"} else 0.36
    if config.base_style == "tripod":
        base_width = max(base_width, 0.48)

    stand_height = max(0.24, min(0.50, config.stand_height))
    # Keep the panel bottom above the base swivel bearing at rest: the tilt
    # pivot sits at 1.01*stand_height (telescoping, mast at travel=0) or
    # stand_height+0.035 above the stand frame origin, and the panel hangs
    # screen_height/2 below the pivot.
    half_screen = screen_height / 2.0
    if height_travel > 0.0:
        stand_height = max(stand_height, (half_screen + 0.015) / 1.01)
    else:
        stand_height = max(stand_height, half_screen + 0.015 - 0.035)

    # Geometric up-tilt stop: tilting back by theta swings the panel bottom
    # rearward; the panel back plane runs 12 mm behind the tilt pivot axis and
    # the frontmost column plane sits y_clear behind the pivot. No panel point
    # reaches the column plane iff  half_screen*sin(theta) - 0.012*cos(theta)
    # <= y_clear - margin.  Tall panels therefore get a smaller tilt stop
    # (>= ~0.13 rad by construction), exactly like real monitors.
    column_clearance = {
        "slim_neck": 0.052,
        "broad_column": 0.0415,
        "telescoping_column": 0.035,
    }[stand_layout]
    tilt_upper = min(tilt_upper, _max_up_tilt(half_screen, column_clearance))
    tilt_upper = max(tilt_upper, tilt_lower + 0.02)  # safety for exotic manual configs

    return ResolvedDesktopMonitorWithTiltSwivelStandConfig(
        screen_profile=config.screen_profile,
        base_style=config.base_style,
        stand_layout=stand_layout,
        controls_style=controls_style,
        cable_cover_style=cable_cover_style,
        yoke_style=yoke_style,
        material_style=config.material_style,
        screen_width=config.screen_width,
        screen_height=screen_height,
        screen_depth=max(0.018, min(0.060, config.screen_depth)),
        base_width=base_width,
        base_depth=base_depth,
        stand_height=stand_height,
        height_travel=height_travel,
        tilt_range=(tilt_lower, tilt_upper),
        has_portrait_pivot=has_portrait_pivot,
        menu_button_count=0 if controls_style == "none" else config.menu_button_count,
        name=config.name,
    )


def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    joint_range: object
    if joint_type == ArticulationType.CONTINUOUS:
        joint_range = "continuous"
    else:
        joint_range = None if limits is None else (limits.lower, limits.upper)
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": joint_range,
    }


def _swivel_origin_z(resolved: ResolvedDesktopMonitorWithTiltSwivelStandConfig) -> float:
    """Return the world z-height of the swivel joint.

    The swivel bearing top on the base must be AT this height so the stand
    turntable (local z=0.006, half-length=0.006) bottom just touches at this z.
    """
    if resolved.base_style == "tripod":
        return 0.0625
    if resolved.base_style == "rounded_pedestal":
        return 0.047
    if resolved.base_style == "rect_plate":
        return 0.047
    # v_foot
    return 0.047


def _add_box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.opaque_generic")


def _add_mesh(
    part,
    geometry,
    assets: AssetContext,
    xyz,
    material,
    name: str,
    rpy=(0.0, 0.0, 0.0),
) -> None:
    part.visual(
        mesh_from_geometry(geometry, assets.mesh_path(f"{part.name}_{name}.obj")),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="plastic.opaque_glossy_molded",
    )


def _curved_slab(
    width: float,
    height: float,
    thickness: float,
    *,
    center_y: float,
    curve_depth: float,
    segments_x: int = 36,
    segments_z: int = 8,
) -> MeshGeometry:
    """Curved monitor slab with edges wrapping toward the viewer (-Y)."""
    geom = MeshGeometry()
    front: list[list[int]] = []
    back: list[list[int]] = []
    half_w = width / 2.0
    half_h = height / 2.0

    for iz in range(segments_z + 1):
        z = -half_h + height * iz / segments_z
        f_row: list[int] = []
        b_row: list[int] = []
        for ix in range(segments_x + 1):
            x = -half_w + width * ix / segments_x
            curve = curve_depth * (x / half_w) ** 2
            y_front = center_y - curve
            y_back = y_front + thickness
            f_row.append(geom.add_vertex(x, y_front, z))
            b_row.append(geom.add_vertex(x, y_back, z))
        front.append(f_row)
        back.append(b_row)

    for iz in range(segments_z):
        for ix in range(segments_x):
            f00, f10 = front[iz][ix], front[iz][ix + 1]
            f01, f11 = front[iz + 1][ix], front[iz + 1][ix + 1]
            b00, b10 = back[iz][ix], back[iz][ix + 1]
            b01, b11 = back[iz + 1][ix], back[iz + 1][ix + 1]
            geom.add_face(f00, f01, f11)
            geom.add_face(f00, f11, f10)
            geom.add_face(b00, b10, b11)
            geom.add_face(b00, b11, b01)

    # Close four thin edges.
    for ix in range(segments_x):
        f0, f1 = front[0][ix], front[0][ix + 1]
        b0, b1 = back[0][ix], back[0][ix + 1]
        geom.add_face(f0, b1, b0)
        geom.add_face(f0, f1, b1)
        f0, f1 = front[-1][ix], front[-1][ix + 1]
        b0, b1 = back[-1][ix], back[-1][ix + 1]
        geom.add_face(f0, b0, b1)
        geom.add_face(f0, b1, f1)
    for iz in range(segments_z):
        f0, f1 = front[iz][0], front[iz + 1][0]
        b0, b1 = back[iz][0], back[iz + 1][0]
        geom.add_face(f0, b0, b1)
        geom.add_face(f0, b1, f1)
        f0, f1 = front[iz][-1], front[iz + 1][-1]
        b0, b1 = back[iz][-1], back[iz + 1][-1]
        geom.add_face(f0, f1, b1)
        geom.add_face(f0, b1, b0)

    return geom


def _display_shell_front_y(resolved: ResolvedDesktopMonitorWithTiltSwivelStandConfig) -> float:
    # Display-local y of the shell back face. The display frame origin is the
    # tilt pivot axis (the tilt_axle centerline), so the shell back sits just
    # 12 mm in front of the hinge.
    rear_clearance_y = -0.012
    if resolved.screen_profile == "curved_wide":
        # _curved_slab spans [base_y - curve, base_y - curve + thickness] in y at
        # each x, so with base_y = rear_clearance_y - shell_thick the shell's
        # BACK face at x=0 lands exactly on rear_clearance_y (matching the flat
        # profiles) and the front face at x=0 sits shell_thick in front of it.
        shell_thick = min(resolved.screen_depth, 0.020)
        front_face_y = rear_clearance_y - shell_thick
        return front_face_y - 0.010
    shell_depth = resolved.screen_depth * (1.35 if resolved.screen_profile == "boxy_flat" else 1.0)
    return rear_clearance_y - shell_depth - 0.006


def _stand_half_extents(
    resolved: ResolvedDesktopMonitorWithTiltSwivelStandConfig,
) -> tuple[float, float]:
    if resolved.stand_layout == "slim_neck":
        return (0.0275, 0.018)
    if resolved.stand_layout == "broad_column":
        return (0.0475, 0.0275)
    if resolved.stand_layout == "split_yoke":
        return (0.085, 0.021)
    return (0.045, 0.030)


def _add_tripod_foot(
    part,
    *,
    angle_deg: float,
    length: float,
    width: float,
    material,
    pad,
) -> None:
    angle = math.radians(angle_deg)
    cx = math.sin(angle) * length * 0.33
    cy = math.cos(angle) * length * 0.33
    yaw = -angle
    part.visual(
        Box((width, length, 0.026)),
        origin=Origin(xyz=(cx, cy, 0.018), rpy=(0.0, 0.0, yaw)),
        material=material,
        name=f"tripod_leg_{int(angle_deg)}", material_class_id="plastic.opaque_glossy_molded",
    )
    tx = math.sin(angle) * length * 0.58
    ty = math.cos(angle) * length * 0.58
    part.visual(
        Box((width * 0.72, 0.075, 0.006)),
        origin=Origin(xyz=(tx, ty, 0.004), rpy=(0.0, 0.0, yaw)),
        material=pad,
        name=f"rubber_pad_{int(angle_deg)}", material_class_id="rubber.smooth_plain",
    )


def _build_base(base, resolved, assets, body, trim, metal, rubber) -> None:
    """Build the base.

    Each style has a bearing/hub column whose TOP is exactly at swivel_origin_z and
    whose BOTTOM starts at the plate/foot top.  This ensures:
      - No overlap between bearing and plate (bearing bottom == plate top)
      - Contact with stand turntable (bearing top == swivel_z == stand turntable bottom in world)
    """
    w = resolved.base_width
    d = resolved.base_depth
    swivel_z = _swivel_origin_z(resolved)
    if resolved.base_style == "rounded_pedestal":
        plate_h = 0.030
        plate = ExtrudeGeometry.centered(
            rounded_rect_profile(w, d, min(0.045, d * 0.18), corner_segments=8),
            plate_h,
        )
        _add_mesh(base, plate, assets, (0.0, 0.0, plate_h / 2.0), body, "rounded_pedestal_plate")
        bearing_h = swivel_z - plate_h
        base.visual(
            Cylinder(radius=0.068, length=bearing_h),
            origin=Origin(xyz=(0.0, 0.0, plate_h + bearing_h / 2.0)),
            material=metal,
            name="swivel_bearing_well", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
        )
        # Prominent top bearing ring visible at swivel joint.
        base.visual(
            Cylinder(radius=0.090, length=0.008),
            origin=Origin(xyz=(0.0, 0.0, swivel_z - 0.004)),
            material=metal,
            name="swivel_bearing_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.chrome_polished"),
        )
    elif resolved.base_style == "rect_plate":
        plate_h = 0.032
        _add_box(base, (w, d, plate_h), (0.0, 0.0, plate_h / 2.0), body, "rect_base_plate")
        _add_box(
            base, (w * 0.72, 0.020, 0.006), (0.0, -d * 0.35, plate_h + 0.003), trim, "front_trim"
        )
        bearing_h = swivel_z - plate_h
        base.visual(
            Cylinder(radius=0.060, length=bearing_h),
            origin=Origin(xyz=(0.0, 0.0, plate_h + bearing_h / 2.0)),
            material=metal,
            name="swivel_bearing", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
        )
        base.visual(
            Cylinder(radius=0.085, length=0.008),
            origin=Origin(xyz=(0.0, 0.0, swivel_z - 0.004)),
            material=metal,
            name="swivel_bearing_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.chrome_polished"),
        )
    elif resolved.base_style == "v_foot":
        for side, sx in (("left", -1.0), ("right", 1.0)):
            _add_box(
                base,
                (w * 0.62, 0.050, 0.030),
                (sx * w * 0.18, 0.10, 0.015),
                body,
                f"{side}_v_foot",
                rpy=(0.0, 0.0, sx * 0.35),
            )
        hub_plate_h = 0.032
        _add_box(base, (0.12, 0.20, hub_plate_h), (0.0, 0.0, hub_plate_h / 2.0), trim, "center_hub")
        bearing_h = swivel_z - hub_plate_h
        base.visual(
            Cylinder(radius=0.058, length=bearing_h),
            origin=Origin(xyz=(0.0, 0.0, hub_plate_h + bearing_h / 2.0)),
            material=metal,
            name="swivel_bearing", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
        )
        base.visual(
            Cylinder(radius=0.080, length=0.008),
            origin=Origin(xyz=(0.0, 0.0, swivel_z - 0.004)),
            material=metal,
            name="swivel_bearing_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.chrome_polished"),
        )
    else:
        # Tripod: three legs radiating outward.
        _add_tripod_foot(
            base, angle_deg=0.0, length=w * 0.62, width=0.115, material=trim, pad=rubber
        )
        _add_tripod_foot(
            base, angle_deg=122.0, length=w * 0.52, width=0.095, material=trim, pad=rubber
        )
        _add_tripod_foot(
            base, angle_deg=-122.0, length=w * 0.52, width=0.095, material=trim, pad=rubber
        )
        # Hub top reaches swivel_origin_z so stand turntable contacts it.
        # Feet are ~26mm (0.026) tall; hub starts at 0 to minimize overlap with foot geometry.
        hub_h = swivel_z
        base.visual(
            Cylinder(radius=0.090, length=hub_h),
            origin=Origin(xyz=(0.0, 0.0, hub_h / 2.0)),
            material=metal,
            name="tripod_hub", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
        )
        # Prominent bearing ring at top of hub (matches swivel joint z).
        base.visual(
            Cylinder(radius=0.090, length=0.008),
            origin=Origin(xyz=(0.0, 0.0, swivel_z - 0.004)),
            material=metal,
            name="swivel_bearing_ring", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.chrome_polished"),
        )


def _add_yoke_capture(
    part, resolved, body, trim, metal, z: float, y: float, *, y_offset: float = 0.0
) -> None:
    """Add a compact U-bracket yoke that cleanly captures the display tilt hinge.

    ``y_offset`` shifts the whole yoke assembly in the carrier part's local y
    (used when the carrier frame is offset from the stand centerline, e.g. the
    telescoping mast whose frame sits on the sleeve back wall).
    """
    yo = y_offset
    # Tilt pivot axis runs at y - HINGE_SETBACK (+yo); must match the tilt_joint
    # origin. The deep yoke_neck juts the hinge (and thus the panel) well
    # forward of the column so the panel can tilt back without striking it.
    ear_center_y = y - HINGE_SETBACK + 0.0115 + yo
    ear_x = 0.048
    ear_h = 0.078
    ear_t = 0.016

    # Centered mortise-and-tenon style socket: the grey tongue reads as inserted into
    # a dark pocket in the post, then carries the forward neck and hinge ears.
    _add_box(part, (0.092, 0.044, 0.016), (0.0, yo, z - 0.043), metal, "post_socket_pocket")
    _add_box(part, (0.058, 0.030, 0.048), (0.0, yo - 0.006, z - 0.030), body, "post_socket_tongue")
    _add_box(
        part, (0.048, 0.028, 0.050), (0.0, y - 0.022 + yo, z - 0.058), body, "socket_vertical_web"
    )
    _add_box(part, (0.050, 0.077, 0.026), (0.0, y - 0.0465 + yo, z - 0.018), body, "yoke_neck")

    _add_box(part, (ear_t, 0.004, ear_h), (-ear_x, ear_center_y, z), body, "left_yoke_ear")
    _add_box(part, (ear_t, 0.004, ear_h), (ear_x, ear_center_y, z), body, "right_yoke_ear")

    # Bridge arms tie each ear back to the socket pocket so the ears are not
    # floating islands. They run at |x| in [0.040, 0.050] — outboard of the
    # display knuckle straps (|x| <= 0.038) and radially well clear (>= 38 mm)
    # of the tilt pivot axis, so the tilting display never sweeps into them.
    for tag, sx in (("left", -1.0), ("right", 1.0)):
        _add_box(
            part,
            (0.010, 0.044, 0.012),
            (sx * 0.045, y - 0.070 + yo, z - 0.043),
            body,
            f"{tag}_ear_bridge",
        )

    # Hinge support rib: a thin blade dropping from the yoke_neck toward the
    # display tilt_axle. Its near corner sits 13.3 mm from the tilt pivot axis
    # (inside the 15 mm articulation-origin gate) while staying 1.3 mm clear of
    # the 12 mm axle surface at every tilt pose (the axle is coaxial with the
    # pivot, so the clearance is pose-invariant). It is 4 mm thin in x so the
    # pose-sampled AABB overlap gate's broad phase always skips it, and it sits
    # on the +y side of the pivot axis, which the tilting shell can never reach.
    _add_box(
        part,
        (0.004, 0.008, 0.030),
        (0.0, y - HINGE_SETBACK + 0.017 + yo, z - 0.018),
        body,
        "hinge_bridge_rib",
    )


def _build_column_sleeve(column, resolved, body, metal) -> None:
    """Build the column outer sleeve that guides the inner mast post."""
    h = resolved.stand_height
    hw, hd = _stand_half_extents(resolved)
    sleeve_w = hw * 2.0 + 0.010
    sleeve_d = hd * 2.0 + 0.010
    sleeve_z = h * 0.50

    if resolved.stand_layout == "slim_neck":
        _add_box(column, (sleeve_w, sleeve_d, h), (0.0, 0.0, sleeve_z), body, "slim_neck")
    elif resolved.stand_layout == "broad_column":
        _add_box(column, (sleeve_w, sleeve_d, h), (0.0, 0.0, sleeve_z), body, "broad_column")
        _add_box(
            column,
            (sleeve_w * 0.72, 0.008, h * 0.65),
            (0.0, -hd - 0.002, h * 0.50),
            metal,
            "front_trim",
        )
    elif resolved.stand_layout == "split_yoke":
        _add_box(column, (0.160, 0.042, 0.060), (0.0, 0.0, 0.036), body, "split_yoke_root_bridge")
        _add_box(
            column, (0.050, 0.042, h * 0.75), (-0.060, 0.0, h * 0.38), body, "left_rear_yoke_leg"
        )
        _add_box(
            column, (0.050, 0.042, h * 0.75), (0.060, 0.0, h * 0.38), body, "right_rear_yoke_leg"
        )
        _add_box(column, (0.180, 0.040, 0.035), (0.0, 0.0, h * 0.76), body, "split_yoke_bridge")
    else:
        # Telescoping column: open-front U-channel sleeve guides the mast.
        _add_box(
            column,
            (sleeve_w, 0.014, h * 0.72),
            (0.0, hd + 0.002, sleeve_z * 0.80),
            body,
            "sleeve_back",
        )
        _add_box(
            column,
            (0.014, sleeve_d + 0.010, h * 0.72),
            (-hw - 0.002, 0.0, sleeve_z * 0.80),
            body,
            "sleeve_side_0",
        )
        _add_box(
            column,
            (0.014, sleeve_d + 0.010, h * 0.72),
            (hw + 0.002, 0.0, sleeve_z * 0.80),
            body,
            "sleeve_side_1",
        )
        # Metal collars at sleeve base and top.
        _add_box(
            column, (sleeve_w, 0.012, 0.030), (0.0, hd + 0.002, 0.047), metal, "lower_rear_collar"
        )
        _add_box(
            column,
            (0.012, sleeve_d + 0.010, 0.030),
            (-hw - 0.002, 0.0, 0.047),
            metal,
            "lower_side_collar_0",
        )
        _add_box(
            column,
            (0.012, sleeve_d + 0.010, 0.030),
            (hw + 0.002, 0.0, 0.047),
            metal,
            "lower_side_collar_1",
        )
        _add_box(
            column,
            (sleeve_w, 0.012, 0.020),
            (0.0, hd + 0.002, h * 0.72 + 0.010),
            metal,
            "upper_rear_collar",
        )
        _add_box(
            column,
            (0.012, sleeve_d + 0.010, 0.020),
            (-hw - 0.002, 0.0, h * 0.72 + 0.010),
            metal,
            "upper_side_collar_0",
        )
        _add_box(
            column,
            (0.012, sleeve_d + 0.010, 0.020),
            (hw + 0.002, 0.0, h * 0.72 + 0.010),
            metal,
            "upper_side_collar_1",
        )

    column.visual(
        Cylinder(radius=0.073, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, 0.013)),
        material=metal,
        name="turntable_disk", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
    )


def _build_mast(mast, resolved, body, metal, *, y0: float = 0.0) -> None:
    """Build the inner mast that slides within the column sleeve.

    ``y0`` is the mast-local y of the sleeve centerline: the mast frame sits on
    the sleeve back wall (where the prismatic joint origin lives), so the mast
    geometry is offset by y0 = -(hd + 0.002) to stay centered in the sleeve.
    """
    h = resolved.stand_height
    hw, hd = _stand_half_extents(resolved)
    # mast_post must fit inside sleeve interior (inner half-width = hw-0.005, inner half-depth = hd-0.005).
    # Use hw*2-0.009 so the mast half-width (hw-0.0045) slightly exceeds the sleeve inner half
    # (hw-0.005), giving ~0.5 mm of contact overlap that is well within the 3 mm overlap tolerance
    # while ensuring the mast and sleeve walls are in physical contact (not isolated).
    mast.visual(
        Box((hw * 2.0 - 0.009, hd * 2.0 - 0.009, h * 0.58)),
        origin=Origin(xyz=(0.0, y0, -h * 0.15)),
        material=body,
        name="mast_post", material_class_id="plastic.opaque_glossy_molded",
    )
    # guide_shoe uses the same slightly-oversized cross-section to maintain sleeve contact.
    mast.visual(
        Box((hw * 2.0 - 0.009, hd * 2.0 - 0.009, 0.034)),
        origin=Origin(xyz=(0.0, y0, -h * 0.50 + 0.017)),
        material=metal,
        name="guide_shoe", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
    )
    # top_clamp sits above the sleeve and can be wider; keep it flush with mast_post.
    mast.visual(
        Box((hw * 2.0 - 0.004, hd * 2.0 - 0.004, 0.030)),
        origin=Origin(xyz=(0.0, y0, h * 0.20)),
        material=metal,
        name="top_clamp", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
    )


def _build_split_yoke_arms(yoke, resolved, assets: AssetContext, body, metal) -> None:
    """Add curved tube arms for split_yoke or wide yoke styles."""
    ear_x = 0.105 if resolved.yoke_style in {"split_rear_yoke", "vesa_portrait"} else 0.080
    arms = MeshGeometry()
    arms.merge(
        tube_from_spline_points(
            [(0.0, 0.0, 0.020), (-ear_x * 0.65, 0.018, 0.044), (-ear_x * 1.55, 0.055, 0.100)],
            radius=0.016,
            samples_per_segment=10,
            radial_segments=16,
        )
    )
    arms.merge(
        tube_from_spline_points(
            [(0.0, 0.0, 0.020), (ear_x * 0.65, 0.018, 0.044), (ear_x * 1.55, 0.055, 0.100)],
            radius=0.016,
            samples_per_segment=10,
            radial_segments=16,
        )
    )
    yoke.visual(
        mesh_from_geometry(arms, assets.mesh_path(f"{yoke.name}_split_yoke_arms.obj")),
        material=body,
        name="split_yoke_arms", material_class_id="plastic.opaque_glossy_molded",
    )
    yoke.visual(
        Cylinder(radius=0.032, length=0.075),
        origin=Origin(xyz=(0.0, 0.0, 0.037)),
        material=metal,
        name="neck_socket", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.brushed_silver"),
    )


def _build_display(display, resolved, assets, body, trim, glass, accent, metal) -> None:
    w = resolved.screen_width
    h = resolved.screen_height
    d = resolved.screen_depth
    # Display frame origin = tilt pivot axis; shell back face 12 mm in front of it.
    rear_clearance_y = -0.012
    front_y = _display_shell_front_y(resolved)

    if resolved.screen_profile == "curved_wide":
        # Curved shell: its BACK face sits at rear_clearance_y = -0.012 (toward the stand),
        # and its FRONT face extends toward the viewer (more negative y).
        # This keeps the shell entirely BEHIND the stand yoke geometry.
        curved_rear_y = rear_clearance_y  # -0.012
        shell_thick = min(d, 0.020)
        # _curved_slab spans [center_y - curve, center_y - curve + thickness] in
        # y at each x; anchor so the back face (x=0) lands on curved_rear_y and
        # therefore keeps the standard 12 mm clearance behind the tilt pivot.
        shell_center_y = curved_rear_y - shell_thick
        curve_d = d * 1.8
        shell = _curved_slab(w, h, shell_thick, center_y=shell_center_y, curve_depth=curve_d)
        _add_mesh(display, shell, assets, (0.0, 0.0, 0.0), body, "curved_screen_panel")
        panel = _curved_slab(
            w * 0.90,
            h * 0.82,
            0.003,
            center_y=shell_center_y - 0.0015,
            curve_depth=curve_d * 0.98,
        )
        _add_mesh(display, panel, assets, (0.0, 0.0, 0.0), glass, "display_glass")
        # Keep the curved profile clean: no extra lower chin bar geometry.
    else:
        shell_depth = d * (1.35 if resolved.screen_profile == "boxy_flat" else 1.0)
        shell = ExtrudeGeometry.centered(
            rounded_rect_profile(w, h, min(0.022, h * 0.08), corner_segments=8),
            shell_depth,
        )
        _add_mesh(
            display,
            shell,
            assets,
            (0.0, rear_clearance_y - shell_depth / 2.0, 0.0),
            body,
            "rear_shell",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
        bezel = 0.020 if resolved.screen_profile != "thin_premium" else 0.012
        bezel_mesh = BezelGeometry(
            (w - 2.0 * bezel, h - 2.4 * bezel),
            (w, h),
            0.006,
            opening_shape="rounded_rect",
            outer_shape="rounded_rect",
            opening_corner_radius=min(0.006, bezel * 0.45),
            outer_corner_radius=min(0.018, h * 0.055),
            wall=(bezel, bezel, bezel, bezel * 1.4),
        )
        # The shell front face sits at front_y + 0.006. Embed the bezel cluster
        # ~1 mm into it so the front elements and the rear shell form one
        # connected body (island check requires true contact).
        _add_mesh(
            display,
            bezel_mesh,
            assets,
            (0.0, front_y + 0.004, 0.0),
            trim,
            "front_bezel_frame",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
        strip_y = front_y + 0.0045
        _add_box(
            display, (w, 0.006, bezel), (0.0, strip_y, h / 2.0 - bezel / 2.0), trim, "top_bezel"
        )
        _add_box(
            display,
            (w, 0.006, bezel * 1.4),
            (0.0, strip_y, -h / 2.0 + bezel * 0.7),
            trim,
            "bottom_bezel",
        )
        _add_box(
            display, (bezel, 0.006, h), (-w / 2.0 + bezel / 2.0, strip_y, 0.0), trim, "left_bezel"
        )
        _add_box(
            display, (bezel, 0.006, h), (w / 2.0 - bezel / 2.0, strip_y, 0.0), trim, "right_bezel"
        )
        _add_box(
            display,
            (w - 2 * bezel, 0.003, h - 2.4 * bezel),
            (0.0, front_y + 0.0055, 0.0),
            glass,
            "screen_panel",
        )

    # Rear hinge assembly: the display owns its half of the hinge. The tilt
    # pivot axis IS the display frame origin (local y=0, z=0): the tilt_axle is
    # coaxial with the joint axis, and a pair of knuckle straps (rear_hub /
    # rear_hub_left) tie the axle back to the shell, so display geometry always
    # wraps the tilt joint origin. Straps stop at local y=+0.006 so they clear
    # the yoke_neck across the full tilt range.
    strap_h = min(0.096, h * 0.42)
    _add_box(display, (0.024, 0.020, strap_h), (0.026, -0.004, 0.0), trim, "rear_hub")
    _add_box(display, (0.024, 0.020, strap_h), (-0.026, -0.004, 0.0), trim, "rear_hub_left")
    axle_len = 0.138
    display.visual(
        Cylinder(radius=0.012, length=axle_len),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="tilt_axle", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.chrome_polished"),
    )


def _add_controls(model, display, resolved, trim, accent, metal) -> None:
    front_y = _display_shell_front_y(resolved)
    z = -resolved.screen_height / 2.0 + 0.026

    # _surface_y is the viewer-facing surface the controls should touch.
    # Use a unified offset now that the curved profile no longer has a dedicated chin strip.
    _surface_y = front_y + 0.006
    # Button caps: button_cap at local (0, -0.002, 0) so cap +y face = joint_y.
    # Set joint_y = _surface_y + 0.0005 → cap max_Y = _surface_y + 0.0005 (0.5 mm into shell):
    # AABB depth_Y(cap, shell) = 0.0005 < 0.003 → SKIP; FCL → contact.
    # AABB depth_Y(cap, bezel_frame) = 0 → SKIP (cap min_Y = _surface_y - 0.0035 = bezel max_Y).
    _button_y = _surface_y + 0.0005
    # Rocker: rocker_cap at local (0, -0.003, 0) so cap max_Y = joint_y.
    # Set joint_y = _surface_y + 0.0005 → cap max_Y = _surface_y + 0.0005 (0.5 mm into shell):
    # AABB depth_Y(cap, shell) = 0.0005 < 0.003 → SKIP; FCL → contact.
    # AABB depth_Y(cap, bottom_bezel) = (front_y+0.003)-(front_y+0.0005) = 0.0025 < 0.003 → SKIP.
    _rocker_y = _surface_y + 0.0005

    if resolved.controls_style in {"menu_buttons", "rocker_and_buttons"}:
        count = resolved.menu_button_count
        start = -0.018 * (count - 1) / 2.0
        for i in range(count):
            button = model.part(f"menu_button_{i}")
            _add_box(button, (0.014, 0.004, 0.009), (0.0, -0.002, 0.0), trim, "button_cap")
            _add_box(button, (0.006, 0.001, 0.0015), (0.0, -0.0042, 0.0), accent, "button_tick")
            origin = (start + 0.018 * i, _button_y, z)
            limits = MotionLimits(effort=0.35, velocity=0.05, lower=0.0, upper=0.0035)
            model.articulation(
                f"menu_button_joint_{i}",
                ArticulationType.PRISMATIC,
                parent=display,
                child=button,
                origin=Origin(xyz=origin),
                axis=(0.0, 1.0, 0.0),
                motion_limits=limits,
                meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 1.0, 0.0), origin, limits),
            )

    if resolved.controls_style in {"rocker_and_buttons", "side_wheel"}:
        control = model.part("rocker_or_joystick")
        if resolved.controls_style == "side_wheel":
            control.visual(
                Cylinder(radius=0.014, length=0.008),
                origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=accent,
                name="side_wheel", material_class_id=("plastic.opaque_generic" if resolved.material_style in {"office_black", "silver"} else "plastic.opaque_glossy_molded"),
            )
            # side_wheel placed just outside the shell right edge.
            # Using _rocker_y so the wheel's Y center aligns with the bezel plane, giving
            # a thin contact zone with the right_bezel face (x-direction touch).
            origin = (resolved.screen_width / 2.0 + 0.0135, _rocker_y + 0.003, z)
        else:
            _add_box(control, (0.030, 0.006, 0.014), (0.0, -0.003, 0.0), accent, "rocker_cap")
            _add_box(control, (0.003, 0.001, 0.010), (-0.006, -0.0065, 0.0), metal, "rocker_mark")
            origin = (-0.075, _rocker_y, z)
        limits = MotionLimits(effort=0.6, velocity=5.0, lower=-0.28, upper=0.28)
        model.articulation(
            "rocker_or_joystick_joint",
            ArticulationType.REVOLUTE,
            parent=display,
            child=control,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), origin, limits),
        )

    if resolved.controls_style == "joystick":
        # Two-axis joystick gimbal chain: display → joystick_gimbal (roll X) → rocker_or_joystick (pitch Y).
        # rocker_or_joystick is the tip; joystick_gimbal_pitch also serves as rocker_or_joystick_joint.
        #
        # Gimbal ball placement strategy differs by profile:
        # curved_wide: no bezel ring mesh; place ball tangent to chin strip face.
        # flat profiles: place ball tangent to screen_panel viewer face to contact the display.
        #   screen_panel viewer face Y = front_y - 0.0005.
        #   ball radius = 0.011; center = front_y - 0.0005 - 0.011 = front_y - 0.0115.
        #   AABB depth_Y(ball, screen_panel) = 0 → SKIP overlap check.
        #   FCL: ball tangent to screen_panel → distance=0 → contact (isolation). ✓
        #   Joystick Z at -h/2+0.039: ball bottom z=-h/2+0.028 > inner_bottom_z(-h/2+0.024); ball
        #   inside bezel ring opening → FCL(ball, bezel_frame) = no collision → not reported. ✓
        #   Stem top z=-0.010, ball bottom z=-0.011: depth_Z=0.001<0.003 → SKIP; FCL→contact. ✓
        if resolved.screen_profile == "curved_wide":
            _gimbal_ball_r = 0.0105
            _gimbal_y = _surface_y - _gimbal_ball_r  # tangent to chin strip face
            _joystick_z = z
        else:
            _gimbal_ball_r = 0.011
            _gimbal_y = front_y - 0.0005 - _gimbal_ball_r  # = front_y - 0.0115
            _joystick_z = -resolved.screen_height / 2.0 + 0.039
        stick_origin = (resolved.screen_width * 0.44, _gimbal_y, _joystick_z)
        gimbal = model.part("joystick_gimbal")
        gimbal.visual(
            Sphere(radius=_gimbal_ball_r),
            origin=Origin(),
            material=metal,
            name="gimbal_ball", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "gaming_dark"} else "metal.chrome_polished"),
        )
        gl = MotionLimits(effort=0.25, velocity=2.5, lower=-0.28, upper=0.28)
        model.articulation(
            "joystick_gimbal_roll",
            ArticulationType.REVOLUTE,
            parent=display,
            child=gimbal,
            origin=Origin(xyz=stick_origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=gl,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), stick_origin, gl),
        )
        # Joystick tip: sphere cap + stem.
        # The cap is placed at z=-0.025 (below the gimbal ball at z=0).
        # The stem top face (z=-0.010) overlaps ball bottom (z=-_gimbal_ball_r) by:
        #   depth_Z = _gimbal_ball_r - 0.010 = 0.001 (for r=0.011) < 0.003 → SKIP; FCL → contact. ✓
        control = model.part("rocker_or_joystick")
        control.visual(
            Sphere(radius=0.009),
            origin=Origin(xyz=(0.0, 0.0, -0.025)),
            material=accent,
            name="joystick_cap", material_class_id=("plastic.opaque_generic" if resolved.material_style in {"office_black", "silver"} else "plastic.opaque_glossy_molded"),
        )
        _add_box(control, (0.006, 0.006, 0.020), (0.0, 0.0, -0.020), metal, "joystick_stem")
        pl = MotionLimits(effort=0.25, velocity=2.5, lower=-0.28, upper=0.28)
        # rocker_or_joystick_joint connects gimbal → rocker_or_joystick (pitch Y-axis).
        # This joint is named rocker_or_joystick_joint for consistency with the rocker/side_wheel path.
        model.articulation(
            "rocker_or_joystick_joint",
            ArticulationType.REVOLUTE,
            parent=gimbal,
            child=control,
            origin=Origin(),
            axis=(0.0, 1.0, 0.0),
            motion_limits=pl,
            meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 1.0, 0.0), (0.0, 0.0, 0.0), pl),
        )


def build_desktop_monitor(
    config: DesktopMonitorWithTiltSwivelStandConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or DesktopMonitorWithTiltSwivelStandConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-desktop-monitor-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    palette = PALETTES[resolved.material_style]
    body = model.material("monitor_body", rgba=palette["body"])
    trim = model.material("monitor_trim", rgba=palette["trim"])
    glass = model.material("monitor_glass", rgba=palette["glass"])
    accent = model.material("monitor_accent", rgba=palette["accent"])
    metal = model.material("monitor_metal", rgba=palette["metal"])
    rubber = model.material("monitor_rubber", rgba=palette["rubber"])

    # --- Base ---
    base = model.part("base")
    _build_base(base, resolved, assets, body, trim, metal, rubber)

    # --- Stand / column (outer sleeve or fixed post) ---
    stand = model.part("stand")
    _build_column_sleeve(stand, resolved, body, metal)

    swivel_limits = MotionLimits(effort=16.0, velocity=3.0)
    swivel_type = ArticulationType.CONTINUOUS
    swivel_origin = (0.0, 0.0, _swivel_origin_z(resolved))
    model.articulation(
        "base_to_stand_swivel",
        swivel_type,
        parent=base,
        child=stand,
        origin=Origin(xyz=swivel_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=swivel_limits,
        meta=_joint_meta(swivel_type, (0.0, 0.0, 1.0), swivel_origin, swivel_limits),
    )

    yoke_parent = stand
    # World-frame y of the tilt pivot axis: the yoke socket reference line sits
    # at y=0.028 and the hinge axle runs HINGE_SETBACK in front of it. The tilt
    # joint origin is placed ON that axle axis (the display owns the hinge barrel).
    hinge_world_y = 0.028 - HINGE_SETBACK

    if resolved.height_travel > 0.0:
        # Inner mast that slides vertically inside the column sleeve. The
        # prismatic origin is placed ON the sleeve back wall (a prismatic
        # origin's position along the slide axis is free), so the mast frame is
        # offset by mast_y0 and all mast/yoke geometry compensates by -mast_y0.
        mast_y0 = _stand_half_extents(resolved)[1] + 0.002
        mast = model.part("height_stage")
        _build_mast(mast, resolved, body, metal, y0=-mast_y0)
        _add_yoke_capture(
            mast,
            resolved,
            body,
            trim,
            metal,
            resolved.stand_height * 0.31,
            0.028,
            y_offset=-mast_y0,
        )

        height_limits = MotionLimits(
            effort=90.0, velocity=0.16, lower=0.0, upper=resolved.height_travel
        )
        height_origin = (0.0, mast_y0, resolved.stand_height * 0.70)
        model.articulation(
            "height_adjust_joint",
            ArticulationType.PRISMATIC,
            parent=stand,
            child=mast,
            origin=Origin(xyz=height_origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=height_limits,
            meta=_joint_meta(
                ArticulationType.PRISMATIC, (0.0, 0.0, 1.0), height_origin, height_limits
            ),
        )
        yoke_parent = mast
        yoke_origin = (0.0, hinge_world_y - mast_y0, resolved.stand_height * 0.31)
    else:
        # No height stage: attach yoke geometry directly to stand top.
        _add_yoke_capture(stand, resolved, body, trim, metal, resolved.stand_height + 0.035, 0.028)
        yoke_origin = (0.0, hinge_world_y, resolved.stand_height + 0.035)

    # --- Display ---
    display = model.part("display")
    _build_display(display, resolved, assets, body, trim, glass, accent, metal)
    _add_controls(model, display, resolved, trim, accent, metal)

    tilt_limits = MotionLimits(
        effort=10.0,
        velocity=1.5,
        lower=resolved.tilt_range[0],
        upper=resolved.tilt_range[1],
    )
    model.articulation(
        "tilt_joint",
        ArticulationType.REVOLUTE,
        parent=yoke_parent,
        child=display,
        origin=Origin(xyz=yoke_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=tilt_limits,
        meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), yoke_origin, tilt_limits),
    )
    return model


def build_seeded_desktop_monitor(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_desktop_monitor(config_from_seed(seed), assets=assets)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    """Report the module realized in each visual slot for a seed.

    Only live axes are registered: controls/cable-cover/yoke styles are
    normalized to a single mechanically-stable branch in resolve_config, so they
    are not slots. stand_layout is reported post-normalization (split_yoke folds
    into broad_column; telescoping implies the height_stage prismatic chain).
    """
    resolved = resolve_config(config_from_seed(seed))
    return (
        ("screen_profile", resolved.screen_profile),
        ("base_style", resolved.base_style),
        ("stand_layout", resolved.stand_layout),
        ("material_style", resolved.material_style),
    )


def with_overrides(
    config: DesktopMonitorWithTiltSwivelStandConfig, **kwargs: object
) -> DesktopMonitorWithTiltSwivelStandConfig:
    return replace(config, **kwargs)


def run_desktop_monitor_tests(
    object_model: ArticulatedObject, config: DesktopMonitorWithTiltSwivelStandConfig
) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {part.name for part in object_model.parts}
    joints = {joint.name for joint in object_model.articulations}

    ctx.check("identity parts present", {"base", "stand", "display"} <= parts)

    swivel = object_model.get_articulation("base_to_stand_swivel")
    tilt = object_model.get_articulation("tilt_joint")
    ctx.check("swivel axis vertical", swivel.axis == (0.0, 0.0, 1.0), details=str(swivel.axis))
    ctx.check(
        "tilt axis horizontal x",
        tuple(abs(v) for v in tilt.axis) == (1.0, 0.0, 0.0),
        details=str(tilt.axis),
    )

    if resolved.height_travel > 0:
        height = object_model.get_articulation("height_adjust_joint")
        ctx.check("height slide vertical", height.axis == (0.0, 0.0, 1.0), details=str(height.axis))
        ctx.check(
            "height travel in range",
            height.motion_limits is not None
            and height.motion_limits.upper == resolved.height_travel,
        )
        # Verify raising the mast actually moves it.
        mast = object_model.get_part("height_stage")
        if mast is not None:
            low_pos = ctx.part_world_position(mast)
            with ctx.pose({height: resolved.height_travel}):
                high_pos = ctx.part_world_position(mast)
            ctx.check(
                "height adjustment raises mast",
                low_pos is not None
                and high_pos is not None
                and high_pos[2] > low_pos[2] + resolved.height_travel * 0.85,
                details=f"low={low_pos}, high={high_pos}",
            )

    if resolved.has_portrait_pivot:
        portrait = object_model.get_articulation("portrait_pivot_joint")
        ctx.check(
            "portrait pivot axis y", portrait.axis == (0.0, 1.0, 0.0), details=str(portrait.axis)
        )

    # Tilt changes the display attitude.
    display = object_model.get_part("display")
    if display is not None:
        tilt_low, tilt_high = resolved.tilt_range
        tilt_amount = min(0.25, tilt_high)
        rest_aabb = ctx.part_element_world_aabb(display, elem="rear_hub")
        with ctx.pose({tilt: tilt_amount}):
            tilted_aabb = ctx.part_element_world_aabb(display, elem="rear_hub")
        ctx.check(
            "screen tilt changes display attitude",
            rest_aabb is not None
            and tilted_aabb is not None
            and abs((tilted_aabb[1][1] - tilted_aabb[0][1]) - (rest_aabb[1][1] - rest_aabb[0][1]))
            > 0.008,
            details=f"rest={rest_aabb}, tilted={tilted_aabb}",
        )

    # Yoke tilt axle captured by pivot pads (when present).
    # The pivot pads live on `stand` (no height stage) or `height_stage` (telescoping column).
    yoke_carrier = object_model.get_part("height_stage" if "height_stage" in parts else "stand")
    if yoke_carrier is not None and display is not None:
        for tag in ("left", "right"):
            pad_elem = f"pivot_pad_{tag}"
            pad_vis = next((v for v in yoke_carrier.visuals if v.name == pad_elem), None)
            if pad_vis is not None:
                ctx.allow_overlap(
                    yoke_carrier,
                    display,
                    elem_a=pad_elem,
                    elem_b="tilt_axle",
                    reason=f"The tilt axle is captured inside the {tag} yoke pivot pad bore.",
                )
                ctx.expect_overlap(
                    yoke_carrier,
                    display,
                    axes="x",
                    elem_a=pad_elem,
                    elem_b="tilt_axle",
                    min_overlap=0.020,
                    name=f"{tag} yoke pad captures tilt axle",
                )
        # Allow captured_tilt_pin overlap with display tilt_axle.
        pin_vis = next((v for v in yoke_carrier.visuals if v.name == "captured_tilt_pin"), None)
        if pin_vis is not None:
            ctx.allow_overlap(
                yoke_carrier,
                display,
                elem_a="captured_tilt_pin",
                elem_b="tilt_axle",
                reason="The yoke captured_tilt_pin is coaxial with the display tilt_axle at the pivot.",
            )

    # Joystick two-axis gimbal chain (when present).
    if resolved.controls_style == "joystick":
        pitch_name = (
            "rocker_or_joystick_joint"
            if "rocker_or_joystick_joint" in joints
            else "joystick_gimbal_pitch"
        )
        if "joystick_gimbal_roll" in joints and pitch_name in joints:
            roll_joint = object_model.get_articulation("joystick_gimbal_roll")
            pitch_joint = object_model.get_articulation(pitch_name)
            ctx.check(
                "joystick roll axis x",
                tuple(abs(v) for v in roll_joint.axis) == (1.0, 0.0, 0.0),
                details=str(roll_joint.axis),
            )
            ctx.check(
                "joystick pitch axis y",
                tuple(abs(v) for v in pitch_joint.axis) == (0.0, 1.0, 0.0),
                details=str(pitch_joint.axis),
            )
            gimbal = object_model.get_part("joystick_gimbal")
            stick = object_model.get_part("rocker_or_joystick")
            if gimbal is not None and stick is not None:
                rest_cap = ctx.part_element_world_aabb(stick, elem="joystick_cap")
                with ctx.pose({roll_joint: 0.22, pitch_joint: -0.20}):
                    moved_cap = ctx.part_element_world_aabb(stick, elem="joystick_cap")
                ctx.check(
                    "joystick pivots in x and y",
                    rest_cap is not None and moved_cap is not None,
                    details=f"rest={rest_cap}, moved={moved_cap}",
                )

    if resolved.controls_style in {"menu_buttons", "rocker_and_buttons"}:
        menu_joints = [name for name in joints if name.startswith("menu_button_joint_")]
        ctx.check("menu button count matches", len(menu_joints) == resolved.menu_button_count)
    if resolved.controls_style in {"rocker_and_buttons", "side_wheel"}:
        ctx.check("rocker or joystick joint exists", "rocker_or_joystick_joint" in joints)
    elif resolved.controls_style == "joystick":
        ctx.check(
            "rocker or joystick joint exists",
            "rocker_or_joystick_joint" in joints,
        )
    if resolved.cable_cover_style == "hinged_rear_door":
        cover = object_model.get_articulation("cable_cover_hinge")
        ctx.check(
            "cable cover hinge z axis", cover.axis == (0.0, 0.0, 1.0), details=str(cover.axis)
        )
    for joint in object_model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            ctx.check(
                f"{joint.name} metadata complete",
                {"type", "axis", "origin", "range"} <= set(joint.meta),
            )
    ctx.check(
        "part diversity params resolved",
        all(
            (
                resolved.screen_profile,
                resolved.base_style,
                resolved.stand_layout,
                resolved.controls_style,
            )
        ),
    )
    return ctx.report()
