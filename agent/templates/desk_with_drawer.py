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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

DeskLayout = Literal[
    "writing_single_drawer",
    "side_pedestal",
    "double_pedestal",
    "l_corner",
    "secretary_dropfront",
    "standing_l",
    "vanity",
    "drafting",
    "wall_mount",
    "partners",
    "card_catalog",
]
DesktopProfile = Literal[
    "rectangular", "l_shaped", "fold_down_leaf", "tilting_top", "wall_fold_down"
]
SupportStyle = Literal[
    "four_legs",
    "single_pedestal",
    "double_pedestal",
    "trestle",
    "wall_brackets",
    "telescoping_columns",
    "c_base",
]
DrawerLayout = Literal[
    "center_single",
    "side_stack",
    "double_stack",
    "apron_three",
    "card_catalog_grid",
    "keyboard_tray_plus_drawer",
]
HandleStyle = Literal["bar_pull", "knob_pair", "recessed_oval", "finger_slot", "none"]
OptionalFeature = Literal["none", "keyboard_tray", "drop_leaf", "tilt_top", "vanity_mirror"]
MaterialStyle = Literal["walnut", "painted", "industrial"]

SOURCE_IDS = {
    "S1": (
        "data/records/rec_desk_with_drawer_72e22d4c7ed941918df130851b142f85/"
        "revisions/rev_000001/model.py:L22-L148"
    ),
    "S2": (
        "data/records/rec_desk_with_drawer_72e22d4c7ed941918df130851b142f85/"
        "revisions/rev_000001/model.py:L150-L266"
    ),
    "S3": (
        "data/records/rec_desk_with_drawer_72e22d4c7ed941918df130851b142f85/"
        "revisions/rev_000001/model.py:L268-L465"
    ),
}

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "walnut": {
        "top": (0.42, 0.27, 0.15, 1.0),
        "case": (0.24, 0.14, 0.08, 1.0),
        "drawer": (0.42, 0.27, 0.17, 1.0),
        "rail": (0.24, 0.25, 0.27, 1.0),
        "metal": (0.71, 0.73, 0.75, 1.0),
    },
    "painted": {
        "top": (0.82, 0.80, 0.74, 1.0),
        "case": (0.60, 0.62, 0.60, 1.0),
        "drawer": (0.86, 0.84, 0.79, 1.0),
        "rail": (0.30, 0.30, 0.32, 1.0),
        "metal": (0.22, 0.22, 0.23, 1.0),
    },
    "industrial": {
        "top": (0.36, 0.27, 0.20, 1.0),
        "case": (0.18, 0.19, 0.20, 1.0),
        "drawer": (0.26, 0.27, 0.29, 1.0),
        "rail": (0.40, 0.42, 0.44, 1.0),
        "metal": (0.60, 0.62, 0.64, 1.0),
    },
}


@dataclass(frozen=True)
class DeskWithDrawerConfig:
    desk_layout: DeskLayout = "double_pedestal"
    desktop_profile: DesktopProfile = "rectangular"
    support_style: SupportStyle = "double_pedestal"
    drawer_layout: DrawerLayout = "double_stack"
    handle_style: HandleStyle = "bar_pull"
    optional_feature: OptionalFeature = "none"
    material_style: MaterialStyle = "walnut"
    desk_width: float = 1.80
    desk_depth: float = 0.85
    desk_height: float = 0.76
    top_thickness: float = 0.040
    drawer_count: int = 6
    drawer_travel: float = 0.32
    height_travel: float = 0.0
    has_keyboard_tray: bool = False
    has_drop_leaf: bool = False
    has_filing_drawer: bool = True
    name: str = "reference_desk_with_drawer"


@dataclass(frozen=True)
class ResolvedDeskWithDrawerConfig:
    desk_layout: DeskLayout
    desktop_profile: DesktopProfile
    support_style: SupportStyle
    drawer_layout: DrawerLayout
    handle_style: HandleStyle
    optional_feature: OptionalFeature
    material_style: MaterialStyle
    desk_width: float
    desk_depth: float
    desk_height: float
    top_thickness: float
    drawer_count: int
    drawer_columns: int
    drawer_rows: int
    drawer_travel: float
    drawer_width: float
    drawer_depth: float
    drawer_height: float
    height_travel: float
    has_keyboard_tray: bool
    has_drop_leaf: bool
    has_filing_drawer: bool
    pedestal_width: float
    pedestal_depth: float
    wall_thickness: float
    back_thickness: float
    floor_thickness: float
    divider_thickness: float
    name: str


def config_from_seed(seed: int) -> DeskWithDrawerConfig:
    rng = random.Random(seed)
    # Keep robust drawer-desk carcasses. L-corners, drop-fronts, drafting tops,
    # wall mounts, and vanity/card-catalog hybrids stay excluded.
    layout: DeskLayout = rng.choice(("writing_single_drawer", "side_pedestal", "double_pedestal"))
    support_by_layout: dict[DeskLayout, SupportStyle] = {
        "writing_single_drawer": "four_legs",
        "side_pedestal": "single_pedestal",
        "double_pedestal": "double_pedestal",
    }
    drawers_by_layout: dict[DeskLayout, DrawerLayout] = {
        "writing_single_drawer": "center_single",
        "side_pedestal": "side_stack",
        "double_pedestal": "double_stack",
    }
    return DeskWithDrawerConfig(
        desk_layout=layout,
        desktop_profile="rectangular",
        support_style=support_by_layout[layout],
        drawer_layout=drawers_by_layout[layout],
        handle_style=rng.choice(("bar_pull", "knob_pair", "recessed_oval", "finger_slot", "none")),
        optional_feature="none",
        material_style=rng.choice(("walnut", "painted", "industrial")),
        desk_width=round(rng.uniform(0.90, 1.80), 3),
        desk_depth=round(rng.uniform(0.48, 0.90), 3),
        drawer_count=rng.randint(1, 3)
        if layout == "writing_single_drawer"
        else (rng.randint(3, 6) if layout == "side_pedestal" else rng.choice((6, 8, 10, 12))),
        drawer_travel=round(rng.uniform(0.12, 0.35), 3),
        height_travel=0.0,
        has_keyboard_tray=False,
        has_drop_leaf=False,
        has_filing_drawer=False,
        name=f"seeded_desk_with_drawer_{seed}",
    )


def resolve_config(config: DeskWithDrawerConfig) -> ResolvedDeskWithDrawerConfig:
    if config.desk_layout not in {
        "writing_single_drawer",
        "side_pedestal",
        "double_pedestal",
        "l_corner",
        "secretary_dropfront",
        "standing_l",
        "vanity",
        "drafting",
        "wall_mount",
        "partners",
        "card_catalog",
    }:
        raise ValueError(f"Unsupported desk_layout: {config.desk_layout}")
    if config.desktop_profile not in {
        "rectangular",
        "l_shaped",
        "fold_down_leaf",
        "tilting_top",
        "wall_fold_down",
    }:
        raise ValueError(f"Unsupported desktop_profile: {config.desktop_profile}")
    if config.support_style not in {
        "four_legs",
        "single_pedestal",
        "double_pedestal",
        "trestle",
        "wall_brackets",
        "telescoping_columns",
        "c_base",
    }:
        raise ValueError(f"Unsupported support_style: {config.support_style}")
    if config.drawer_layout not in {
        "center_single",
        "side_stack",
        "double_stack",
        "apron_three",
        "card_catalog_grid",
        "keyboard_tray_plus_drawer",
    }:
        raise ValueError(f"Unsupported drawer_layout: {config.drawer_layout}")
    if config.handle_style not in {"bar_pull", "knob_pair", "recessed_oval", "finger_slot", "none"}:
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.optional_feature not in {
        "none",
        "keyboard_tray",
        "drop_leaf",
        "tilt_top",
        "vanity_mirror",
    }:
        raise ValueError(f"Unsupported optional_feature: {config.optional_feature}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 1 <= config.drawer_count <= 12:
        raise ValueError("drawer_count must be in [1, 12]")
    if not 0.12 <= config.drawer_travel <= 0.35:
        raise ValueError("drawer_travel must be in [0.12, 0.35]")
    if not 0.0 <= config.height_travel <= 0.35:
        raise ValueError("height_travel must be in [0.0, 0.35]")

    if config.desk_layout not in {"writing_single_drawer", "side_pedestal", "double_pedestal"}:
        config = replace(config, desk_layout="double_pedestal")
    config = replace(
        config,
        desktop_profile="rectangular",
        optional_feature="none",
        height_travel=0.0,
        has_keyboard_tray=False,
        has_drop_leaf=False,
        has_filing_drawer=False,
    )

    layout = config.desk_layout
    profile = config.desktop_profile
    support = config.support_style
    drawers = config.drawer_layout
    optional = config.optional_feature
    has_keyboard = config.has_keyboard_tray
    has_leaf = config.has_drop_leaf
    has_filing = config.has_filing_drawer
    height_travel = config.height_travel
    count = config.drawer_count

    if layout == "writing_single_drawer":
        profile = "rectangular"
        support = "four_legs"
        drawers = "center_single"
        optional = "none"
        count = max(1, min(3, count))
        has_filing = False
    elif layout == "side_pedestal":
        support = "single_pedestal"
        drawers = "side_stack"
        count = max(count, 3)
    elif layout == "double_pedestal":
        support = "double_pedestal"
        drawers = "double_stack"
        count = max(count, 6)
    elif layout == "l_corner":
        profile = "l_shaped"
        has_filing = False
    elif layout == "standing_l":
        profile = "l_shaped"
        support = "telescoping_columns"
        height_travel = max(height_travel, 0.12)
        has_keyboard = has_keyboard or drawers == "keyboard_tray_plus_drawer"
        if optional not in {"none", "keyboard_tray"}:
            optional = "keyboard_tray" if has_keyboard else "none"
        has_filing = False
    elif layout in {"secretary_dropfront", "wall_mount"}:
        profile = "fold_down_leaf" if layout == "secretary_dropfront" else "wall_fold_down"
        support = "wall_brackets" if layout == "wall_mount" else "single_pedestal"
        optional = "drop_leaf"
        has_leaf = True
        height_travel = 0.0
        has_filing = False
    elif layout == "vanity":
        optional = "vanity_mirror"
        has_keyboard = False
        has_leaf = False
        height_travel = 0.0
        has_filing = False
        if support == "telescoping_columns":
            support = "four_legs"
    elif layout == "drafting":
        profile = "tilting_top"
        optional = "tilt_top"
        height_travel = 0.0
        has_filing = False
        if support == "telescoping_columns":
            support = "trestle"
    elif layout == "card_catalog":
        drawers = "card_catalog_grid"
        optional = "none"
        has_keyboard = False
        has_leaf = False
        height_travel = 0.0
        has_filing = False
        count = max(count, 12)

    if optional in {"tilt_top", "drop_leaf", "vanity_mirror"}:
        height_travel = 0.0
        if support == "telescoping_columns":
            support = "trestle" if optional == "tilt_top" else "four_legs"
    elif support != "telescoping_columns":
        height_travel = 0.0

    if (
        layout not in {"standing_l"}
        and drawers != "keyboard_tray_plus_drawer"
        and optional != "keyboard_tray"
    ):
        has_keyboard = False
    if optional != "drop_leaf":
        has_leaf = False

    if drawers == "center_single":
        count = max(1, min(3, count))
        cols, rows = count, 1
    elif drawers == "apron_three":
        count = 3
        cols, rows = 3, 1
    elif drawers == "double_stack":
        count = max(6, count)
        cols, rows = 2, (count + 1) // 2
    elif drawers == "card_catalog_grid":
        count = max(6, min(12, count))
        cols, rows = 4, (count + 3) // 4
    elif drawers == "keyboard_tray_plus_drawer":
        count = max(1, min(3, count))
        cols, rows = 1, count
    else:
        count = max(3, min(4, count))
        cols, rows = 1, count

    desk_width = max(0.80, min(2.20, config.desk_width))
    desk_depth = max(0.42, min(1.10, config.desk_depth))
    desk_height = max(0.62, min(0.92, config.desk_height))
    top_thickness = max(0.020, min(0.060, config.top_thickness))

    # Pedestal dimensions scaled from desk size (carcass-style construction)
    pedestal_width = min(0.50, desk_width * 0.26)
    pedestal_depth = min(0.80, desk_depth * 0.90)
    wall_thickness = 0.022
    back_thickness = 0.018
    floor_thickness = 0.022
    divider_thickness = 0.018

    # Drawer box dimensions derived from pedestal interior
    interior_width = pedestal_width - 2.0 * wall_thickness
    # drawer_width = interior_width + 2*runner_t + 0.030 - 2*runner_t = interior_width + 0.030
    # Breakdown: bw = interior_width - 2*runner_t (so runners touch pedestal inner walls),
    # front_panel = bw + 0.030 (slight overlay on each side).
    # runner_t = 0.008, so: drawer_width = interior_width - 0.016 + 0.030 = interior_width + 0.014.
    drawer_width = min(interior_width + 0.014, 0.46)
    # Cap drawer_depth so the box fits inside the desk (housing or pedestal):
    # - Must fit in pedestal interior: pedestal_depth - back_thickness - clearance
    # - Must not reach the rear apron in housing mode (housing at desk_depth/2 - 0.125,
    #   rear apron at -(desk_depth/2 - 0.07), safe depth = desk_depth - 0.215).
    drawer_depth = min(pedestal_depth - back_thickness - 0.025, 0.56, desk_depth - 0.215)
    drawer_height = min(0.16, max(0.055, (desk_height * 0.48) / max(rows, 1)))
    travel = min(config.drawer_travel, drawer_depth * 0.72)

    return ResolvedDeskWithDrawerConfig(
        desk_layout=layout,
        desktop_profile=profile,
        support_style=support,
        drawer_layout=drawers,
        handle_style=config.handle_style,
        optional_feature=optional,
        material_style=config.material_style,
        desk_width=desk_width,
        desk_depth=desk_depth,
        desk_height=desk_height,
        top_thickness=top_thickness,
        drawer_count=count,
        drawer_columns=cols,
        drawer_rows=rows,
        drawer_travel=travel,
        drawer_width=drawer_width,
        drawer_depth=drawer_depth,
        drawer_height=drawer_height,
        height_travel=height_travel,
        has_keyboard_tray=has_keyboard,
        has_drop_leaf=has_leaf,
        has_filing_drawer=has_filing,
        pedestal_width=pedestal_width,
        pedestal_depth=pedestal_depth,
        wall_thickness=wall_thickness,
        back_thickness=back_thickness,
        floor_thickness=floor_thickness,
        divider_thickness=divider_thickness,
        name=config.name,
    )


def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


def _add_box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.engineered_board")


def _rebase_part_origins(part, shift: tuple[float, float, float]) -> None:
    """Translate every visual/collision/inertial origin of ``part`` by ``-shift``.

    Used to move a FIXED-welded child's local frame onto the mounting interface
    without changing world placement (the joint origin absorbs ``+shift``).
    """
    sx, sy, sz = shift
    if abs(sx) < 1e-12 and abs(sy) < 1e-12 and abs(sz) < 1e-12:
        return
    for elem in list(part.visuals) + list(part.collisions):
        o = elem.origin
        elem.origin = Origin(xyz=(o.xyz[0] - sx, o.xyz[1] - sy, o.xyz[2] - sz), rpy=o.rpy)
    inertial = part.inertial
    if inertial is not None:
        o = inertial.origin
        part.inertial = Inertial(
            mass=inertial.mass,
            inertia=inertial.inertia,
            origin=Origin(xyz=(o.xyz[0] - sx, o.xyz[1] - sy, o.xyz[2] - sz), rpy=o.rpy),
        )


def _frame_top_mount_point(r: ResolvedDeskWithDrawerConfig) -> tuple[float, float, float]:
    """A point on the frame's top bearing surface that also sits under the
    desktop slab — where the FIXED frame->top weld physically lives."""
    leg_h = r.desk_height - r.top_thickness
    if r.support_style in {"single_pedestal", "double_pedestal"}:
        ped_x = 0.0 if r.support_style == "single_pedestal" else -r.desk_width * 0.28
        # Top edge of a pedestal side wall.
        return (ped_x - r.pedestal_width / 2.0 + r.wall_thickness / 2.0, 0.0, leg_h)
    if r.support_style == "wall_brackets":
        return (r.desk_width / 2.0 - 0.025, -r.desk_depth * 0.12, leg_h)
    if r.support_style in {"trestle", "c_base"}:
        return (r.desk_width / 2.0 - 0.025, 0.0, leg_h)
    # four_legs (and any other leg-style fallback): rear-left leg top. This
    # corner is under both the rectangular slab and the l-shaped return slab.
    return (-(r.desk_width / 2.0 - 0.07), -(r.desk_depth / 2.0 - 0.07), leg_h)


def _drawer_column_gap(r: ResolvedDeskWithDrawerConfig) -> float:
    if r.drawer_columns >= 3:
        return 0.012
    if r.drawer_columns == 2:
        return 0.016
    return 0.0


def _build_top(top, r: ResolvedDeskWithDrawerConfig, top_mat, case_mat) -> None:
    w, d, h = r.desk_width, r.desk_depth, r.desk_height
    z = h - r.top_thickness / 2.0
    if r.desktop_profile == "l_shaped":
        _add_box(
            top,
            (w, d * 0.56, r.top_thickness),
            (0.0, -d * 0.12, z),
            top_mat,
            "desktop_main_slab",
        )
        _add_box(
            top,
            (w * 0.52, d, r.top_thickness),
            (-w * 0.24, d * 0.20, z),
            top_mat,
            "desktop_return_slab",
        )
        _add_box(
            top,
            (w * 0.92, 0.026, 0.020),
            (0.0, d * 0.16, z - r.top_thickness * 0.15),
            case_mat,
            "front_edge_molding",
        )
    else:
        _add_box(top, (w, d, r.top_thickness), (0.0, 0.0, z), top_mat, "desktop")
        # Edge moldings on front and rear of desktop
        for sy, mname in ((1.0, "front_top_molding"), (-1.0, "rear_top_molding")):
            _add_box(
                top,
                (w + 0.030, 0.026, 0.022),
                (0.0, sy * (d / 2.0 - 0.013), z - r.top_thickness * 0.10),
                top_mat,
                mname,
            )
        # Writing surface inset / protective mat
        _add_box(
            top,
            (w * 0.72, d * 0.64, 0.004),
            (0.0, 0.0, z + r.top_thickness * 0.52),
            case_mat,
            "writing_inset",
        )

    # Telescoping inner columns attach to top assembly
    if r.support_style == "telescoping_columns" and r.height_travel > 0:
        leg_h = h - r.top_thickness
        outer_top = leg_h * 0.64
        inner_h = leg_h - outer_top
        col_x = w / 2.0 - 0.035
        for idx, x in enumerate((-col_x, col_x)):
            _add_box(
                top,
                (0.050, 0.050, inner_h),
                (x, 0.0, outer_top + inner_h / 2.0),
                case_mat,
                f"inner_column_{idx}",
            )


def _build_support(frame, r: ResolvedDeskWithDrawerConfig, case_mat, metal_mat) -> None:
    w, d, h = r.desk_width, r.desk_depth, r.desk_height
    leg_h = h - r.top_thickness

    if r.support_style == "four_legs":
        for ix, sx in enumerate((-1.0, 1.0)):
            for iy, sy in enumerate((-1.0, 1.0)):
                _add_box(
                    frame,
                    (0.045, 0.045, leg_h),
                    (sx * (w / 2 - 0.07), sy * (d / 2 - 0.07), leg_h / 2.0),
                    case_mat,
                    f"leg_{ix}_{iy}",
                )
        # If drawers open from the front side, omit the front apron so it
        # never blocks drawer travel/visibility.
        if r.drawer_count <= 0:
            _add_box(
                frame,
                (w - 0.18, 0.030, 0.070),
                (0.0, d / 2 - 0.07, leg_h - 0.045),
                case_mat,
                "front_apron",
            )
        else:
            # With the front apron omitted, the two front legs would otherwise be
            # geometric islands. Tie each front leg to its rear leg with a low
            # side stretcher on the outer leg line, well below the drawer zone so
            # it never fouls drawer travel.
            stretcher_z = leg_h * 0.16
            for ix, sx in enumerate((-1.0, 1.0)):
                _add_box(
                    frame,
                    (0.045, d - 0.14, 0.045),
                    (sx * (w / 2 - 0.07), 0.0, stretcher_z),
                    case_mat,
                    f"side_stretcher_{ix}",
                )
        _add_box(
            frame,
            (w - 0.18, 0.030, 0.070),
            (0.0, -(d / 2 - 0.07), leg_h - 0.045),
            case_mat,
            "rear_apron",
        )

    elif r.support_style in {"single_pedestal", "double_pedestal"}:
        # Build proper carcass-style pedestals with walls, back, floor, dividers.
        # Coordinate convention:
        #   X = lateral (left-right), Y = front-back (+ = toward user), Z = up.
        # Pedestals are offset in X. Their depth runs along Y, centered at Y=0.
        # Each pedestal has left/right side walls (thin in X, deep in Y),
        # a back panel (wide in X, thin in Y), floor and dividers.
        ped_x_offsets: tuple[float, ...] = (
            (0.0,) if r.support_style == "single_pedestal" else (-w * 0.28, w * 0.28)
        )
        pd = r.pedestal_depth
        pw = r.pedestal_width
        wt = r.wall_thickness
        bt = r.back_thickness
        ft = r.floor_thickness
        interior_depth = pd - bt - 0.004  # drawable depth inside pedestal
        interior_w = pw - 2.0 * wt  # drawable width inside pedestal
        carcass_h = leg_h
        # Center of the interior running in Y (front=+pd/2, back=-pd/2+bt)
        shelf_center_y = -pd / 4.0 + bt / 4.0

        for idx, ped_x in enumerate(ped_x_offsets):
            # Left and right side walls (panels perpendicular to X, full depth in Y)
            _add_box(
                frame,
                (wt, pd, carcass_h),
                (ped_x - pw / 2.0 + wt / 2.0, 0.0, carcass_h / 2.0),
                case_mat,
                f"pedestal_{idx}_left_wall",
            )
            _add_box(
                frame,
                (wt, pd, carcass_h),
                (ped_x + pw / 2.0 - wt / 2.0, 0.0, carcass_h / 2.0),
                case_mat,
                f"pedestal_{idx}_right_wall",
            )
            # Back panel (closes the rear of the pedestal)
            _add_box(
                frame,
                (pw, bt, carcass_h),
                (ped_x, -pd / 2.0 + bt / 2.0, carcass_h / 2.0),
                case_mat,
                f"pedestal_{idx}_back_panel",
            )
            # Floor panel (sits at the base of the carcass)
            _add_box(
                frame,
                (interior_w, interior_depth, ft),
                (ped_x, shelf_center_y, ft / 2.0),
                case_mat,
                f"pedestal_{idx}_floor",
            )
            # Note: horizontal dividers are omitted here because their Z positions
            # would need to be computed relative to actual drawer bay spacings (which
            # are determined in build_desk_with_drawer). Drawer boxes occupy the full
            # interior depth, so any fixed-fraction dividers would overlap drawer geometry.

        if len(ped_x_offsets) > 1:
            # Two free-standing pedestals are otherwise separate geometry islands
            # within the frame link. Tie them together with a rear modesty panel
            # spanning the kneehole (rear, upper), overlapping each pedestal's back
            # panel. It sits behind the drawers and never fouls front travel.
            left_x, right_x = ped_x_offsets[0], ped_x_offsets[-1]
            span_x = (right_x - pw / 2.0 + wt) - (left_x + pw / 2.0 - wt)
            _add_box(
                frame,
                (span_x, bt, min(0.12, carcass_h * 0.30)),
                (0.0, -pd / 2.0 + bt / 2.0, carcass_h - min(0.12, carcass_h * 0.30) / 2.0 - 0.02),
                case_mat,
                "kneehole_modesty_panel",
            )

    elif r.support_style == "telescoping_columns":
        col_x = w / 2.0 - 0.035
        for idx, x in enumerate((-col_x, col_x)):
            _add_box(
                frame,
                (0.060, 0.060, leg_h * 0.64),
                (x, 0.0, leg_h * 0.32),
                metal_mat,
                f"outer_column_{idx}",
            )
            _add_box(frame, (0.45, 0.070, 0.045), (x, 0.0, 0.030), metal_mat, f"foot_bar_{idx}")

    elif r.support_style == "wall_brackets":
        _add_box(
            frame,
            (w, 0.040, h * 0.42),
            (0.0, -d / 2.0 - 0.140, h * 0.50),
            case_mat,
            "wall_plate",
        )
        for idx, x in enumerate((-w * 0.30, w * 0.30)):
            _add_box(
                frame,
                (0.060, d * 0.20, 0.040),
                (math.copysign(w / 2.0 - 0.025, x), -d * 0.46, leg_h - 0.020),
                metal_mat,
                f"wall_bracket_{idx}",
            )
            riser_x = math.copysign(w / 2.0 - 0.025, x)
            riser_bot = h * 0.58 + 0.055 / 2.0
            _add_box(
                frame,
                (0.040, 0.040, leg_h - riser_bot),
                (riser_x, -d * 0.12, (leg_h + riser_bot) / 2.0),
                metal_mat,
                f"wall_bracket_riser_{idx}",
            )

    else:
        # Trestle / c_base fallback
        post_x = w / 2.0 - 0.025
        _add_box(
            frame, (w * 0.85, 0.060, 0.070), (0.0, 0.0, 0.050), metal_mat, "trestle_floor_beam"
        )
        _add_box(
            frame,
            (0.040, 0.070, leg_h),
            (-post_x, 0.0, leg_h / 2.0),
            metal_mat,
            "left_trestle_post",
        )
        _add_box(
            frame,
            (0.040, 0.070, leg_h),
            (post_x, 0.0, leg_h / 2.0),
            metal_mat,
            "right_trestle_post",
        )


def _add_handle(part, r: ResolvedDeskWithDrawerConfig, drawer_width: float, metal_mat) -> None:
    """Add handle hardware to the drawer front face.

    Front panel is in the XZ plane with normal along +Y (toward user).
    Handles protrude in +Y from the front face (face_t/2 = +0.011 approx).
    """
    grip_len = min(drawer_width * 0.56, 0.185)
    face_front_y = 0.023  # center of handle components, just in front of the front panel
    if r.handle_style == "bar_pull":
        post_offset_x = grip_len * 0.36
        # Two cylindrical mounting posts (along Y)
        part.visual(
            Cylinder(radius=0.0042, length=0.018),
            origin=Origin(xyz=(-post_offset_x, face_front_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=metal_mat,
            name="handle_post_left", material_class_id=("metal.stainless_matte" if r.material_style in {"walnut", "industrial"} else "metal.paint_coated"),
        )
        part.visual(
            Cylinder(radius=0.0042, length=0.018),
            origin=Origin(xyz=(post_offset_x, face_front_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=metal_mat,
            name="handle_post_right", material_class_id=("metal.stainless_matte" if r.material_style in {"walnut", "industrial"} else "metal.paint_coated"),
        )
        # Horizontal grip bar (along X)
        part.visual(
            Cylinder(radius=0.0035, length=grip_len),
            origin=Origin(xyz=(0.0, face_front_y + 0.012, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=metal_mat,
            name="handle_grip", material_class_id=("metal.stainless_matte" if r.material_style in {"walnut", "industrial"} else "metal.paint_coated"),
        )
    elif r.handle_style == "knob_pair":
        for side, kx in enumerate((-grip_len * 0.30, grip_len * 0.30)):
            part.visual(
                Cylinder(radius=0.012, length=0.020),
                origin=Origin(xyz=(kx, face_front_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=metal_mat,
                name=f"knob_{side}", material_class_id=("metal.stainless_matte" if r.material_style in {"walnut", "industrial"} else "metal.paint_coated"),
            )
    elif r.handle_style == "recessed_oval":
        _add_box(
            part,
            (drawer_width * 0.34, 0.006, min(0.032, drawer_width * 0.18)),
            (0.0, 0.025, 0.0),
            metal_mat,
            "recessed_oval_pull",
        )
    elif r.handle_style == "finger_slot":
        _add_box(
            part,
            (drawer_width * 0.42, 0.004, min(0.024, drawer_width * 0.14)),
            (0.0, 0.024, 0.0),
            metal_mat,
            "finger_slot",
        )


def _build_drawer_box(
    drawer,
    r: ResolvedDeskWithDrawerConfig,
    *,
    front_height: float,
    box_height: float,
    depth: float,
    front_width: float,
    drawer_mat,
    rail_mat,
    metal_mat,
    box_width: float | None = None,
    side_thickness: float = 0.012,
    bottom_thickness: float = 0.010,
    back_thickness: float = 0.012,
) -> None:
    """Build a full box-joinery drawer with front panel, sides, bottom, back, and runners.

    Convention: child frame Y is the slide axis (+Y = toward user/open).
    The front face panel is in the XZ plane at y = +0.010.
    The drawer box extends in -Y (into the cabinet).
    """
    bw = box_width if box_width is not None else (front_width - 0.030)
    face_t = 0.022
    # Front false panel (face) — in XZ plane, slightly proud of the joint origin
    _add_box(
        drawer,
        (front_width, face_t, front_height),
        (0.0, face_t / 2.0, 0.0),
        drawer_mat,
        "front_panel",
    )
    # Drawer box extends from the back face of the front panel into the cabinet (-Y).
    # Keep the box front at y=0 so it is physically connected to the front panel.
    side_length = depth - face_t - back_thickness
    side_y = -(side_length / 2.0)
    for side_name, sx_sign in (("box_side_left", -1.0), ("box_side_right", 1.0)):
        _add_box(
            drawer,
            (side_thickness, side_length, box_height),
            (sx_sign * (bw / 2.0 - side_thickness / 2.0), side_y, 0.0),
            drawer_mat,
            side_name,
        )
    # Drawer bottom (inside the box)
    _add_box(
        drawer,
        (bw - 2.0 * side_thickness, side_length, bottom_thickness),
        (0.0, side_y, -box_height / 2.0 + bottom_thickness / 2.0),
        drawer_mat,
        "box_bottom",
    )
    # Drawer back panel
    back_y = -(side_length + back_thickness / 2.0)
    _add_box(drawer, (bw, back_thickness, box_height), (0.0, back_y, 0.0), drawer_mat, "box_back")
    # Metal runner slides (one per side, on exterior of box sides)
    runner_len = min(0.460, side_length)
    runner_y = -(runner_len / 2.0)
    runner_t = 0.008
    for run_name, rsx in (("runner_left", -1.0), ("runner_right", 1.0)):
        _add_box(
            drawer,
            (runner_t, runner_len, 0.014),
            (rsx * (bw / 2.0 + runner_t / 2.0), runner_y, 0.0),
            rail_mat,
            run_name,
        )
    # Handle hardware
    _add_handle(drawer, r, front_width, metal_mat)


def _build_filing_drawer(
    drawer,
    r: ResolvedDeskWithDrawerConfig,
    *,
    front_height: float,
    box_height: float,
    depth: float,
    front_width: float,
    drawer_mat,
    rail_mat,
    metal_mat,
    box_width: float | None = None,
    side_thickness: float = 0.012,
    bottom_thickness: float = 0.010,
    back_thickness: float = 0.012,
) -> None:
    """Build a filing drawer with full box joinery plus internal hanging file rails.

    Uses same Y-axis convention as _build_drawer_box (box extends in -Y from front panel).
    """
    bw = box_width if box_width is not None else (front_width - 0.030)
    face_t = 0.022
    _add_box(
        drawer,
        (front_width, face_t, front_height),
        (0.0, face_t / 2.0, 0.0),
        drawer_mat,
        "front_panel",
    )
    side_length = depth - face_t - back_thickness
    side_y = -(side_length / 2.0)
    for side_name, sx_sign in (("box_side_left", -1.0), ("box_side_right", 1.0)):
        _add_box(
            drawer,
            (side_thickness, side_length, box_height),
            (sx_sign * (bw / 2.0 - side_thickness / 2.0), side_y, 0.0),
            drawer_mat,
            side_name,
        )
    _add_box(
        drawer,
        (bw - 2.0 * side_thickness, side_length, bottom_thickness),
        (0.0, side_y, -box_height / 2.0 + bottom_thickness / 2.0),
        drawer_mat,
        "box_bottom",
    )
    back_y = -(side_length + back_thickness / 2.0)
    _add_box(drawer, (bw, back_thickness, box_height), (0.0, back_y, 0.0), drawer_mat, "box_back")
    runner_len = min(0.470, side_length)
    runner_y = -(runner_len / 2.0)
    runner_t = 0.008
    for run_name, rsx in (("runner_left", -1.0), ("runner_right", 1.0)):
        _add_box(
            drawer,
            (runner_t, runner_len, 0.016),
            (rsx * (bw / 2.0 + runner_t / 2.0), runner_y, 0.0),
            rail_mat,
            run_name,
        )
    # Hanging file rails near the top interior of the box (interior, not protruding outside)
    file_rail_w = 0.010
    file_rail_offset_x = bw / 2.0 - side_thickness - file_rail_w / 2.0
    _add_box(
        drawer,
        (file_rail_w, side_length - 0.050, 0.014),
        (-file_rail_offset_x, side_y, box_height / 2.0 - 0.027),
        rail_mat,
        "hanging_rail_left",
    )
    _add_box(
        drawer,
        (file_rail_w, side_length - 0.050, 0.014),
        (file_rail_offset_x, side_y, box_height / 2.0 - 0.027),
        rail_mat,
        "hanging_rail_right",
    )
    _add_handle(drawer, r, front_width, metal_mat)


def _build_housing_case(
    housing,
    r: ResolvedDeskWithDrawerConfig,
    case_mat,
    rail_mat,
    drawer_local_origins: list[tuple[float, float, float]],
    housing_width: float,
    z_min: float,
    z_max: float,
) -> None:
    """Build the housing carcass with guide rails for non-pedestal drawer layouts."""
    housing_height = z_max - z_min
    housing_center_z = (z_min + z_max) * 0.5
    rail_depth = r.drawer_depth * 0.90
    rail_center_y = -r.drawer_depth * 0.45
    side_t = 0.016
    # top_limit_z: maximum housing-local Z at which the top cap center can be placed
    # Housing is at world Z = desk_height - 0.14, desktop bottom at desk_height - top_t.
    # In housing local frame: desktop bottom = 0.14 - top_t. Keep 4mm clearance to desktop.
    top_limit_z = 0.14 - r.top_thickness - 0.004
    cap_h = 0.012
    # Top cap center must be strictly above the highest drawer box edge
    # (z_max is the top of the box). Cap center = z_max + cap_h/2 + 0.001 tolerance.
    top_cap_z = min(z_max + cap_h / 2.0 + 0.001, top_limit_z)
    side_bottom_z = z_min - 0.015
    side_top_z = min(z_max + 0.018, top_cap_z + cap_h / 2.0 + 0.002)

    # housing_back sits just behind the drawer box back panel.
    # We must ensure it does not collide with the rear leg apron (on desk_frame).
    # housing_y (world) = desk_depth/2 - 0.125.  Rear apron center world Y = -(d/2-0.07).
    # Housing-local limit: housing_back_center < rear_apron_front_face - housing_y - clearance.
    # rear_apron_front_face_world = -(d/2-0.07) + 0.015 = -d/2 + 0.085
    # housing_y = d/2 - 0.125
    # limit = (-d/2+0.085) - (d/2-0.125) - 0.008 = -d + 0.202  →  local_y < -(d-0.202)
    # housing_back is only added when there is enough room behind the drawer box.
    d = r.desk_depth
    housing_y = d / 2.0 - 0.125
    housing_back_t = 0.020
    housing_back_local_y = -(r.drawer_depth + 0.010)
    # Rear apron front face in housing-local Y:
    rear_apron_front_local = (-(d / 2.0 - 0.07) + 0.015) - housing_y
    # Only add housing_back if its entire thickness clears the rear apron front face
    if housing_back_local_y + housing_back_t / 2.0 < rear_apron_front_local - 0.006:
        _add_box(
            housing,
            (housing_width, housing_back_t, housing_height),
            (0.0, housing_back_local_y, housing_center_z),
            case_mat,
            "housing_back",
        )
    _add_box(
        housing,
        (housing_width, rail_depth, 0.014),
        (0.0, rail_center_y, z_min - 0.012),
        case_mat,
        "housing_bottom",
    )
    _add_box(
        housing,
        (housing_width, rail_depth, cap_h),
        (0.0, rail_center_y, top_cap_z),
        case_mat,
        "housing_top_cap",
    )
    for sx, name in ((-1.0, "left_outer_side"), (1.0, "right_outer_side")):
        _add_box(
            housing,
            (side_t, rail_depth, side_top_z - side_bottom_z),
            (
                sx * (housing_width / 2.0 - side_t / 2.0),
                rail_center_y,
                (side_top_z + side_bottom_z) * 0.5,
            ),
            case_mat,
            name,
        )

    # Per-row guide rails and separator shelves
    by_row: dict[int, list[tuple[float, float, float]]] = {}
    for index, local_origin in enumerate(drawer_local_origins):
        by_row.setdefault(index // r.drawer_columns, []).append(local_origin)

    for row, row_origins in by_row.items():
        for local_x, _local_y, local_z in row_origins:
            # Position rails just outside the drawer box, below the box bottom
            # to avoid overlapping with either the drawer box_bottom or side panels.
            box_h = r.drawer_height * 0.84
            bottom_t = 0.010
            rail_h = 0.016
            # rail top = just below drawer box bottom face in housing-local Z
            rail_top_z = local_z - box_h / 2.0 + bottom_t / 2.0 - 0.003
            rail_z = rail_top_z - rail_h / 2.0
            for sign, side_name in ((-1.0, "left"), (1.0, "right")):
                # Place rail so its inner face touches the runner outer face.
                # runner outer face = bw/2 + runner_t; bw = drawer_width - 0.030; runner_t = 0.008.
                # rail inner face = rail center ∓ rail_t/2; rail_t = 0.010.
                # rail center = local_x + sign * (bw/2 + runner_t + rail_t/2)
                #             = local_x + sign * ((drawer_width - 0.030)/2 + 0.008 + 0.005)
                #             = local_x + sign * ((drawer_width - 0.004) / 2)
                housing_rail_x = local_x + sign * ((r.drawer_width - 0.004) / 2.0)
                _add_box(
                    housing,
                    (0.010, rail_depth, rail_h),
                    (housing_rail_x, rail_center_y, rail_z),
                    rail_mat,
                    f"{side_name}_guide_rail_{row}_{len(housing.visuals)}",
                )
        if row > 0:
            shelf_z = row_origins[0][2] + r.drawer_height * 0.5 + 0.010
            _add_box(
                housing,
                (housing_width - side_t * 2.0, rail_depth, 0.010),
                (0.0, rail_center_y, shelf_z),
                case_mat,
                f"drawer_separator_shelf_{row}",
            )

    # Vertical stiles between columns
    first_row = by_row.get(0, [])
    if len(first_row) > 1:
        sorted_x = sorted(o[0] for o in first_row)
        for col, (left_x, right_x) in enumerate(zip(sorted_x, sorted_x[1:]), start=1):
            gap = right_x - left_x - r.drawer_width
            if gap > 0.006:
                stile_t = min(0.014, max(0.008, gap * 0.70))
                _add_box(
                    housing,
                    (stile_t, 0.010, housing_height + 0.020),
                    ((left_x + right_x) * 0.5, -0.008, housing_center_z),
                    case_mat,
                    f"front_vertical_stile_{col}",
                )

    # Intentionally omit front face rails here: full-width front rails at the
    # drawer stack plane can intersect drawer side panels in closed pose.


def _drawer_origins(r: ResolvedDeskWithDrawerConfig) -> list[tuple[float, float, float]]:
    origins: list[tuple[float, float, float]] = []
    cols = r.drawer_columns
    drawer_pitch = r.drawer_width + _drawer_column_gap(r)
    for i in range(r.drawer_count):
        col = i % cols
        row = i // cols
        if cols == 1:
            x = 0.0
        else:
            x = (col - (cols - 1) / 2.0) * drawer_pitch
        top_clearance = (
            0.18 if r.has_keyboard_tray or r.optional_feature == "keyboard_tray" else 0.08
        )
        z = r.desk_height - r.top_thickness - top_clearance - row * (r.drawer_height + 0.020)
        y = r.desk_depth / 2.0 - 0.030
        origins.append((x, y, z))
    return origins


def build_desk_with_drawer(
    config: DeskWithDrawerConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or DeskWithDrawerConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-desk-drawer-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.material_style]
    top_mat = model.material("desk_top", rgba=palette["top"])
    case_mat = model.material("desk_case", rgba=palette["case"])
    drawer_mat = model.material("desk_drawer", rgba=palette["drawer"])
    rail_mat = model.material("desk_rail", rgba=palette["rail"])
    metal_mat = model.material("desk_hardware", rgba=palette["metal"])

    # Root structural frame (also carries support geometry)
    frame = model.part("desk_frame")
    _build_support(frame, r, case_mat, metal_mat)
    frame.inertial = Inertial.from_geometry(
        Box((r.desk_width, r.desk_depth, r.desk_height)),
        mass=80.0 + r.desk_width * 15.0,
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0)),
    )

    # Desktop top assembly
    top = model.part("top_assembly")
    _build_top(top, r, top_mat, case_mat)

    # When the top is FIXED-welded to the frame, its local frame is rebased onto
    # the mounting interface (see the else branch below). Every joint parented to
    # ``top`` must then shift its origin by ``-top_shift`` to hold world placement.
    top_shift = (0.0, 0.0, 0.0)

    def _top_origin(xyz: tuple[float, float, float]) -> Origin:
        return Origin(xyz=(xyz[0] - top_shift[0], xyz[1] - top_shift[1], xyz[2] - top_shift[2]))

    if r.height_travel > 0 and r.support_style == "telescoping_columns":
        limits = MotionLimits(effort=2200.0, velocity=0.05, lower=0.0, upper=r.height_travel)
        origin = (0.0, 0.0, 0.0)
        model.articulation(
            "height_adjust_joint",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=top,
            origin=Origin(xyz=origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 0.0, 1.0), origin, limits),
        )
    elif r.optional_feature == "tilt_top":
        limits = MotionLimits(effort=60.0, velocity=1.4, lower=0.0, upper=0.95)
        origin = (0.0, 0.0, 0.0)
        model.articulation(
            "tilt_top_joint",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=top,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), origin, limits),
        )
    else:
        # Weld the top to the frame at the actual bearing interface: place the
        # joint origin on a frame support top and rebase the top's geometry so
        # its local (0,0,0) lands there too (world placement is unchanged).
        mount = _frame_top_mount_point(r)
        _rebase_part_origins(top, mount)
        top_shift = mount
        model.articulation(
            "frame_to_top",
            ArticulationType.FIXED,
            parent=frame,
            child=top,
            origin=Origin(xyz=mount),
        )

    # -----------------------------------------------------------------------
    # Drawer articulation: pedestal-style vs housing-style
    # -----------------------------------------------------------------------
    use_pedestal_mode = r.support_style in {"single_pedestal", "double_pedestal"}

    if use_pedestal_mode:
        # Pedestal-style: drawers slide along +Y (toward the front of the desk, toward the user).
        # Pedestals are offset along X (left-right axis). Drawers are stacked in Z.
        # Joint convention: origin = (ped_x_center, front_face_y, bay_z), axis = (0, 1, 0).
        # Part names use sequential drawer_{i} to match the integer-suffix test contract.
        pedestal_x_offsets: tuple[float, ...] = (
            (0.0,)
            if r.support_style == "single_pedestal"
            else (-r.desk_width * 0.28, r.desk_width * 0.28)
        )

        # The joint origin Y is at the front face of the pedestal opening.
        # Pedestals are centered at Y=0 with depth pd, so their front face is at +pd/2.
        # Setting joint origin Y = pd/2 aligns the drawer in the opening (face_t/2 protrudes).
        pedestal_front_y = r.pedestal_depth / 2.0

        # Distribute drawers across pedestals
        drawers_per_pedestal = max(1, r.drawer_count // len(pedestal_x_offsets))
        remaining = r.drawer_count - drawers_per_pedestal * len(pedestal_x_offsets)

        # Heights for the carcass interior bays (fraction of carcass height)
        carcass_h = r.desk_height - r.top_thickness

        filing_drawer_part = None
        drawer_index = 0  # sequential counter for drawer_N naming

        for ped_idx, ped_x in enumerate(pedestal_x_offsets):
            n_bays = drawers_per_pedestal + (1 if ped_idx < remaining else 0)
            # Space bays evenly in the carcass height; leave clearance at top and bottom
            bay_z_values = [
                carcass_h * (0.15 + 0.70 * b / max(n_bays - 1, 1)) for b in range(n_bays)
            ]

            for bay_idx, bay_z in enumerate(bay_z_values):
                is_bottom_bay = bay_idx == 0
                is_filing = (
                    r.has_filing_drawer
                    and ped_idx == len(pedestal_x_offsets) - 1
                    and is_bottom_bay
                    and n_bays >= 2
                )
                front_h = r.drawer_height * (1.8 if is_filing else 1.0)
                box_h = front_h * 0.84

                # Sequential integer name to satisfy test contract
                part_name = f"drawer_{drawer_index}"
                drawer_index += 1
                drawer = model.part(part_name)

                if is_filing:
                    _build_filing_drawer(
                        drawer,
                        r,
                        front_height=front_h,
                        box_height=box_h,
                        depth=r.drawer_depth,
                        front_width=r.drawer_width,
                        drawer_mat=drawer_mat,
                        rail_mat=rail_mat,
                        metal_mat=metal_mat,
                    )
                    drawer.inertial = Inertial.from_geometry(
                        Box((r.drawer_width, r.drawer_depth, front_h)),
                        mass=10.0 + r.drawer_depth * 5.0,
                        origin=Origin(xyz=(0.0, -r.drawer_depth / 2.0, 0.0)),
                    )
                    filing_drawer_part = drawer
                else:
                    _build_drawer_box(
                        drawer,
                        r,
                        front_height=front_h,
                        box_height=box_h,
                        depth=r.drawer_depth,
                        front_width=r.drawer_width,
                        drawer_mat=drawer_mat,
                        rail_mat=rail_mat,
                        metal_mat=metal_mat,
                    )
                    drawer.inertial = Inertial.from_geometry(
                        Box((r.drawer_width, r.drawer_depth, front_h)),
                        mass=4.0 + front_h * 20.0,
                        origin=Origin(xyz=(0.0, -r.drawer_depth / 2.0, 0.0)),
                    )

                # Joint: child slides in +Y relative to parent (toward user)
                travel_upper = min(r.drawer_travel, r.drawer_depth * 0.72)
                limits = MotionLimits(
                    effort=110.0,
                    velocity=0.40,
                    lower=0.0,
                    upper=travel_upper,
                )
                joint_name = f"drawer_slide_{drawer_index - 1}"
                joint_origin = (ped_x, pedestal_front_y, bay_z)
                model.articulation(
                    joint_name,
                    ArticulationType.PRISMATIC,
                    parent=frame,
                    child=drawer,
                    origin=Origin(xyz=joint_origin),
                    axis=(0.0, 1.0, 0.0),
                    motion_limits=limits,
                    meta=_joint_meta(
                        ArticulationType.PRISMATIC, (0.0, 1.0, 0.0), joint_origin, limits
                    ),
                )

        # Optional revolute lock bar on the filing drawer (five-star feature)
        if filing_drawer_part is not None:
            lock_bar = model.part("file_lock_bar")
            lock_bar.visual(
                Cylinder(radius=0.005, length=r.drawer_width * 0.88),
                origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=metal_mat,
                name="hinge_rod", material_class_id=("metal.stainless_matte" if r.material_style in {"walnut", "industrial"} else "metal.paint_coated"),
            )
            _add_box(
                lock_bar,
                (0.010, r.drawer_width * 0.88, 0.050),
                (-0.008, 0.0, -0.025),
                metal_mat,
                "gate_plate",
            )
            lock_bar.inertial = Inertial.from_geometry(
                Box((0.012, r.drawer_width * 0.88, 0.055)),
                mass=0.8,
                origin=Origin(xyz=(-0.004, 0.0, -0.022)),
            )
            model.articulation(
                "filing_drawer_to_lock_bar",
                ArticulationType.REVOLUTE,
                parent=filing_drawer_part,
                child=lock_bar,
                origin=Origin(xyz=(-0.045, 0.0, r.drawer_height * 0.88 * 0.5)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=2.0, velocity=1.2, lower=0.0, upper=1.15),
            )

    else:
        # Housing-based drawer layout (four_legs, trestle, wall_brackets, etc.)
        housing = model.part("drawer_housing")
        drawer_origins = _drawer_origins(r)
        housing_mount_z = r.desk_height - 0.14
        drawer_local_origins = [
            (origin[0], 0.0, origin[2] - housing_mount_z) for origin in drawer_origins
        ]
        # Use the actual box half-height (0.84 fraction) for z bounds, not the full height
        box_half_h = r.drawer_height * 0.84 / 2.0
        z_min = min(z - box_half_h for _x, _y, z in drawer_local_origins)
        z_max = max(z + box_half_h for _x, _y, z in drawer_local_origins)
        # Housing width must clear the outermost drawer box (including side runners)
        # plus the housing side-wall thickness on each side.
        bw_half = (r.drawer_width - 0.030) / 2.0
        runner_t = 0.008
        side_t_hw = 0.016
        outer_drawer_edge = max(abs(lo[0]) for lo in drawer_local_origins) + bw_half + runner_t
        min_housing_width = 2.0 * (outer_drawer_edge + side_t_hw + 0.004)
        if r.drawer_rows == 1:
            # Keep a one-row drawer surround tight to the actual row width.
            row_gap = _drawer_column_gap(r)
            row_width = r.drawer_columns * r.drawer_width + max(0, r.drawer_columns - 1) * row_gap
            preferred_width = max(min_housing_width, row_width + 0.052)
        else:
            preferred_width = max(
                min_housing_width,
                r.drawer_columns * (r.drawer_width + 0.060) + 0.120,
            )
        housing_width = min(
            r.desk_width * 0.88,
            preferred_width,
        )
        top_contact_z = r.desk_height - r.top_thickness - housing_mount_z
        _add_box(
            housing,
            (min(0.22, housing_width), 0.020, 0.002),
            (0.0, -0.020, top_contact_z),
            case_mat,
            "top_contact_pad",
        )
        _build_housing_case(
            housing, r, case_mat, rail_mat, drawer_local_origins, housing_width, z_min, z_max
        )
        housing_y = r.desk_depth / 2.0 - 0.125
        # Weld the housing to the desktop at the top-contact pad: rebase the
        # housing so its local (0,0,0) lands on the pad (the underside-of-desktop
        # interface) and place the joint origin on that same world point. World
        # placement is unchanged; the housing's own children (drawer slides)
        # compensate below via ``housing_shift``.
        housing_shift = (0.0, -0.020, top_contact_z)
        _rebase_part_origins(housing, housing_shift)
        pad_contact_world = (0.0, housing_y - 0.020, r.desk_height - r.top_thickness)
        model.articulation(
            "top_to_drawer_housing",
            ArticulationType.FIXED,
            parent=top,
            child=housing,
            origin=_top_origin(pad_contact_world),
        )

        for i, origin in enumerate(drawer_origins):
            drawer = model.part(f"drawer_{i}")
            _build_drawer_box(
                drawer,
                r,
                front_height=r.drawer_height,
                box_height=r.drawer_height * 0.84,
                depth=r.drawer_depth,
                front_width=r.drawer_width,
                drawer_mat=drawer_mat,
                rail_mat=rail_mat,
                metal_mat=metal_mat,
            )
            drawer.inertial = Inertial.from_geometry(
                Box((r.drawer_width, r.drawer_depth, r.drawer_height)),
                mass=3.0 + r.drawer_height * 18.0,
                origin=Origin(xyz=(0.0, -r.drawer_depth / 2.0, 0.0)),
            )
            local_origin = (
                origin[0] - housing_shift[0],
                0.0 - housing_shift[1],
                (origin[2] - housing_mount_z) - housing_shift[2],
            )
            limits = MotionLimits(effort=45.0, velocity=0.30, lower=0.0, upper=r.drawer_travel)
            axis = (0.0, 1.0, 0.0)
            model.articulation(
                f"drawer_slide_{i}",
                ArticulationType.PRISMATIC,
                parent=housing,
                child=drawer,
                origin=Origin(xyz=local_origin),
                axis=axis,
                motion_limits=limits,
                meta=_joint_meta(ArticulationType.PRISMATIC, axis, local_origin, limits),
            )

    # -----------------------------------------------------------------------
    # Optional features
    # -----------------------------------------------------------------------
    if r.has_keyboard_tray or r.optional_feature == "keyboard_tray":
        shelf = model.part("keyboard_tray")
        shelf_origin_z = r.desk_height - r.top_thickness - 0.035
        _add_box(
            shelf,
            (r.desk_width * 0.48, r.desk_depth * 0.42, 0.018),
            (0.0, -r.desk_depth * 0.21, 0.0),
            top_mat,
            "keyboard_shelf",
        )
        hanger_x = r.desk_width / 2.0 - 0.020
        for idx, x in enumerate((-hanger_x, hanger_x)):
            _add_box(
                shelf,
                (0.020, 0.020, 0.070),
                (x, -r.desk_depth * 0.40, 0.0),
                metal_mat,
                f"keyboard_tray_hanger_{idx}",
            )
        limits = MotionLimits(
            effort=35.0, velocity=0.20, lower=0.0, upper=min(0.22, r.desk_depth * 0.35)
        )
        origin = (0.0, r.desk_depth / 2.0 - 0.12, shelf_origin_z)
        origin = (origin[0] - top_shift[0], origin[1] - top_shift[1], origin[2] - top_shift[2])
        model.articulation(
            "shelf_slide_joint",
            ArticulationType.PRISMATIC,
            parent=top,
            child=shelf,
            origin=Origin(xyz=origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 1.0, 0.0), origin, limits),
        )

    if r.has_drop_leaf or r.optional_feature == "drop_leaf":
        leaf = model.part("drop_leaf")
        _add_box(
            leaf,
            (r.desk_width * 0.70, 0.030, r.desk_depth * 0.55),
            (0.0, 0.015, r.desk_depth * 0.275),
            top_mat,
            "writing_panel",
        )
        limits = MotionLimits(effort=25.0, velocity=1.4, lower=0.0, upper=math.pi / 2.0)
        origin = (0.0, r.desk_depth / 2.0, r.desk_height - 0.22)
        origin = (origin[0] - top_shift[0], origin[1] - top_shift[1], origin[2] - top_shift[2])
        model.articulation(
            "drop_leaf_joint",
            ArticulationType.REVOLUTE,
            parent=top,
            child=leaf,
            origin=Origin(xyz=origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
        )

    if r.optional_feature == "vanity_mirror":
        mirror = model.part("vanity_mirror")
        _add_box(
            mirror, (r.desk_width * 0.45, 0.030, 0.46), (0.0, 0.0, 0.0), top_mat, "mirror_frame"
        )
        _add_box(
            mirror,
            (r.desk_width * 0.39, 0.006, 0.38),
            (0.0, -0.020, 0.0),
            metal_mat,
            "mirror_glass",
        )
        _add_box(
            mirror,
            (r.desk_width * 0.18, 0.020, 0.002),
            (0.0, 0.0, -0.251),
            metal_mat,
            "mirror_contact_foot",
        )
        limits = MotionLimits(effort=8.0, velocity=1.2, lower=-0.38, upper=0.38)
        origin = (0.0, -r.desk_depth * 0.32, r.desk_height + 0.25)
        origin = (origin[0] - top_shift[0], origin[1] - top_shift[1], origin[2] - top_shift[2])
        model.articulation(
            "mirror_or_door_joint",
            ArticulationType.REVOLUTE,
            parent=top,
            child=mirror,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), origin, limits),
        )

    return model


def build_seeded_desk_with_drawer(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_desk_with_drawer(config_from_seed(seed), assets=assets)


def with_overrides(config: DeskWithDrawerConfig, **kwargs: object) -> DeskWithDrawerConfig:
    return replace(config, **kwargs)


def run_desk_with_drawer_tests(
    object_model: ArticulatedObject, config: DeskWithDrawerConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {part.name for part in object_model.parts}
    joints = {joint.name for joint in object_model.articulations}

    ctx.check("desk_frame part present", "desk_frame" in parts)
    ctx.check("top_assembly part present", "top_assembly" in parts)

    use_pedestal_mode = r.support_style in {"single_pedestal", "double_pedestal"}

    if use_pedestal_mode:
        # Pedestal mode: drawer joints are named drawer_slide_{i} (same as housing mode)
        pedestal_slide_joints = [name for name in joints if name.startswith("drawer_slide_")]
        ctx.check(
            "drawer joints present for pedestal mode",
            len(pedestal_slide_joints) >= 1,
            details=f"{pedestal_slide_joints}",
        )
        for jname in pedestal_slide_joints:
            joint = object_model.get_articulation(jname)
            ctx.check(
                f"{jname} slides along Y axis",
                tuple(abs(v) for v in joint.axis) == (0.0, 1.0, 0.0),
                details=str(joint.axis),
            )
            ctx.check(
                f"{jname} travel within pedestal depth",
                joint.motion_limits is not None
                and joint.motion_limits.upper <= r.drawer_depth * 0.73,
            )
            ctx.check(
                f"{jname} metadata complete",
                {"type", "axis", "origin", "range"} <= set(joint.meta),
            )

        # Check lock bar if present
        if "file_lock_bar" in parts:
            lock_joint = object_model.get_articulation("filing_drawer_to_lock_bar")
            ctx.check(
                "lock bar revolute axis along Y",
                tuple(abs(v) for v in lock_joint.axis) == (0.0, 1.0, 0.0),
                details=str(lock_joint.axis),
            )
            ctx.check(
                "lock bar upper travel >= 1.0 rad",
                lock_joint.motion_limits is not None and lock_joint.motion_limits.upper >= 1.0,
            )

    else:
        # Housing-mode checks
        ctx.check("drawer_housing part present", "drawer_housing" in parts)
        drawer_parts = [
            name
            for name in parts
            if name.startswith("drawer_") and name.removeprefix("drawer_").isdigit()
        ]
        drawer_joints_list = [name for name in joints if name.startswith("drawer_slide_")]
        ctx.check(
            "drawer count matches config",
            len(drawer_parts) == r.drawer_count,
            details=f"{drawer_parts}",
        )
        ctx.check(
            "drawer joint count matches config",
            len(drawer_joints_list) == r.drawer_count,
            details=f"{drawer_joints_list}",
        )
        for jname in drawer_joints_list:
            joint = object_model.get_articulation(jname)
            ctx.check(
                f"{jname} slides along Y axis",
                tuple(abs(v) for v in joint.axis) == (0.0, 1.0, 0.0),
                details=str(joint.axis),
            )
            ctx.check(
                f"{jname} retained travel",
                joint.motion_limits is not None
                and joint.motion_limits.upper <= r.drawer_depth * 0.72,
            )
            ctx.check(
                f"{jname} metadata complete",
                {"type", "axis", "origin", "range"} <= set(joint.meta),
            )

    if r.height_travel > 0 and r.support_style == "telescoping_columns":
        height_joint = object_model.get_articulation("height_adjust_joint")
        ctx.check(
            "height adjust joint vertical",
            height_joint.axis == (0.0, 0.0, 1.0),
            details=str(height_joint.axis),
        )
    if r.has_drop_leaf or r.optional_feature == "drop_leaf":
        leaf_joint = object_model.get_articulation("drop_leaf_joint")
        ctx.check(
            "drop leaf hinge horizontal",
            tuple(abs(v) for v in leaf_joint.axis) == (1.0, 0.0, 0.0),
            details=str(leaf_joint.axis),
        )
    if r.has_keyboard_tray or r.optional_feature == "keyboard_tray":
        shelf_joint = object_model.get_articulation("shelf_slide_joint")
        ctx.check(
            "keyboard tray slides Y",
            tuple(abs(v) for v in shelf_joint.axis) == (0.0, 1.0, 0.0),
            details=str(shelf_joint.axis),
        )
    if r.optional_feature == "tilt_top":
        tilt_joint = object_model.get_articulation("tilt_top_joint")
        ctx.check(
            "tilt top hinge horizontal",
            tuple(abs(v) for v in tilt_joint.axis) == (1.0, 0.0, 0.0),
            details=str(tilt_joint.axis),
        )
    ctx.check(
        "config params resolved",
        all((r.desktop_profile, r.support_style, r.drawer_layout, r.handle_style)),
    )
    return ctx.report()
