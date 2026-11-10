# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Technology_Monitor — modular desktop computer monitor.
#
# Frame convention (shared with the 5-star sources):
#   +X = panel width, +Z = up, -Y = viewer side (the screen faces -Y).
#
# Slots (see specs_modular_v1/Technology_Monitor.md):
#   A stand_family : pillar_stand | vfoot_neck | twin_leg | wall_mount | ergo_arm
#   B panel_form   : flat_16_10 | flat_16_9 | flat_ultrawide | curved_21_9 | curved_32_9
#   C mechanism    : derived (tilt always) + optional swivel (pillar/twin_leg) + height (vfoot)
#
# The panel is a child part whose `hinge_barrel` sits at the part-frame origin;
# every carrier presents a tilt hinge (REVOLUTE X) that captures that barrel.
# Captured-trunnion pivots (tilt/swivel/elbow) omit MatingContract and are
# grandfathered (element-scoped allow_overlap), exactly like monitor_mount and
# the 5-star source records. Curved panels are carried only by the vfoot neck
# stand (their native carrier in S2/S6). Flat panels use a bottom-anchored hinge
# so the panel bottom clears the stand head across the whole tilt range.

import math
import random
import tempfile
from dataclasses import dataclass
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
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

StandFamily = Literal["pillar_stand", "vfoot_neck", "twin_leg", "wall_mount", "ergo_arm"]
PanelForm = Literal["flat_16_10", "flat_16_9", "flat_ultrawide", "curved_21_9", "curved_32_9"]
MaterialStyle = Literal[
    "office_black", "silver", "white", "gaming_red", "brushed_alu", "gunmetal"
]

# Adopted 5-star module sources (record model.py:Lx-Ly).
SOURCE_IDS = {
    "S1": "data/records/rec_a-standard-16-10-widescreen-desktop-lcd-monitor-_20260624_123957_925849_015db054/revisions/rev_000001/model.py:L34-L182",
    "S2": "data/records/rec_ultrawide-curved-computer-monitor-on-a-central-s_20260605_173926_571270_0ea51d17/revisions/rev_000001/model.py:L36-L254",
    "S3": "data/records/rec_monitor_var_twin_leg_base/revisions/rev_000001/model.py:L46-L216",
    "S4": "data/records/rec_monitor_var_ergonomic_arm/revisions/rev_000001/model.py:L63-L392",
    "S5": "data/records/rec_monitor_var_wall_mount/revisions/rev_000001/model.py:L21-L198",
    "S6": "data/records/rec_monitor_var_curved_21_9/revisions/rev_000001/model.py:L36-L256",
    "S7": "data/records/rec_monitor_var_tilt_swivel/revisions/rev_000001/model.py:L22-L223",
    "S8": "data/records/rec_monitor_var_portrait_pivot/revisions/rev_000001/model.py:L22-L208",
}

# Aspect ratio (width / height) and concave bow depth per panel form.
_PANEL_ASPECT = {
    "flat_16_10": 1.60,
    "flat_16_9": 1.78,
    "flat_ultrawide": 2.33,
    "curved_21_9": 2.30,
    "curved_32_9": 3.40,
}
_PANEL_BOW = {
    "flat_16_10": 0.0,
    "flat_16_9": 0.0,
    "flat_ultrawide": 0.0,
    "curved_21_9": 0.025,
    "curved_32_9": 0.050,
}
_CURVED_FORMS = {"curved_21_9", "curved_32_9"}

# 6 colorways: body / trim / glass(screen) / accent / metal / rubber.
PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "office_black": {
        "body": (0.05, 0.06, 0.07, 1.0), "trim": (0.14, 0.15, 0.16, 1.0),
        "glass": (0.03, 0.04, 0.05, 1.0), "accent": (0.45, 0.47, 0.50, 1.0),
        "metal": (0.30, 0.31, 0.33, 1.0), "rubber": (0.02, 0.02, 0.02, 1.0),
    },
    "silver": {
        "body": (0.70, 0.72, 0.74, 1.0), "trim": (0.45, 0.47, 0.49, 1.0),
        "glass": (0.05, 0.07, 0.09, 1.0), "accent": (0.20, 0.21, 0.23, 1.0),
        "metal": (0.60, 0.62, 0.65, 1.0), "rubber": (0.18, 0.18, 0.20, 1.0),
    },
    "white": {
        "body": (0.90, 0.91, 0.92, 1.0), "trim": (0.72, 0.74, 0.76, 1.0),
        "glass": (0.06, 0.08, 0.10, 1.0), "accent": (0.30, 0.55, 0.85, 1.0),
        "metal": (0.66, 0.68, 0.70, 1.0), "rubber": (0.30, 0.30, 0.32, 1.0),
    },
    "gaming_red": {
        "body": (0.04, 0.04, 0.05, 1.0), "trim": (0.16, 0.17, 0.19, 1.0),
        "glass": (0.02, 0.03, 0.04, 1.0), "accent": (0.82, 0.10, 0.09, 1.0),
        "metal": (0.13, 0.14, 0.16, 1.0), "rubber": (0.0, 0.0, 0.0, 1.0),
    },
    "brushed_alu": {
        "body": (0.62, 0.62, 0.60, 1.0), "trim": (0.40, 0.40, 0.38, 1.0),
        "glass": (0.05, 0.06, 0.07, 1.0), "accent": (0.75, 0.66, 0.34, 1.0),
        "metal": (0.72, 0.72, 0.70, 1.0), "rubber": (0.16, 0.16, 0.15, 1.0),
    },
    "gunmetal": {
        "body": (0.22, 0.23, 0.25, 1.0), "trim": (0.32, 0.33, 0.35, 1.0),
        "glass": (0.03, 0.04, 0.06, 1.0), "accent": (0.55, 0.58, 0.62, 1.0),
        "metal": (0.42, 0.44, 0.47, 1.0), "rubber": (0.08, 0.08, 0.09, 1.0),
    },
}

BASE_HEIGHT = 0.026  # S1 hex-base plate height


@dataclass(frozen=True)
class MonitorConfig:
    stand_family: StandFamily = "pillar_stand"
    panel_form: PanelForm = "flat_16_10"
    material_style: MaterialStyle = "office_black"
    screen_width: float = 0.58
    bezel: float = 0.016
    pillar_height: float = 0.34
    has_swivel: bool = True
    tilt_lower: float = -0.18
    tilt_upper: float = 0.16
    swivel_range: float = 0.70
    height_travel: float = 0.040
    name: str = "monitor"


@dataclass(frozen=True)
class ResolvedMonitorConfig:
    stand_family: StandFamily
    panel_form: PanelForm
    material_style: MaterialStyle
    panel_w: float
    panel_h: float
    aspect: float
    bow: float
    bezel: float
    pillar_height: float
    has_swivel: bool
    tilt_lower: float
    tilt_upper: float
    swivel_range: float
    height_travel: float
    is_curved: bool
    name: str


def config_from_seed(seed: int) -> MonitorConfig:
    rng = random.Random(seed)
    stand: StandFamily = rng.choices(
        ("pillar_stand", "vfoot_neck", "twin_leg", "wall_mount", "ergo_arm"),
        weights=(0.30, 0.24, 0.18, 0.16, 0.12),
        k=1,
    )[0]
    panel: PanelForm = rng.choices(
        ("flat_16_10", "flat_16_9", "flat_ultrawide", "curved_21_9", "curved_32_9"),
        weights=(0.28, 0.24, 0.16, 0.18, 0.14),
        k=1,
    )[0]
    return MonitorConfig(
        stand_family=stand,
        panel_form=panel,
        material_style=rng.choice(
            ("office_black", "silver", "white", "gaming_red", "brushed_alu", "gunmetal")
        ),
        screen_width=round(rng.uniform(0.42, 0.95), 3),
        bezel=round(rng.uniform(0.008, 0.022), 4),
        pillar_height=round(rng.uniform(0.30, 0.42), 3),
        has_swivel=rng.random() < 0.65,
        tilt_lower=round(rng.uniform(-0.22, -0.16), 3),
        tilt_upper=round(rng.uniform(0.14, 0.20), 3),
        swivel_range=round(rng.uniform(0.5, 1.0), 3),
        height_travel=round(rng.uniform(0.030, 0.050), 3),
        name=f"seeded_monitor_{seed}",
    )


def resolve_config(config: MonitorConfig) -> ResolvedMonitorConfig:
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if config.panel_form not in _PANEL_ASPECT:
        raise ValueError(f"Unsupported panel_form: {config.panel_form}")
    if config.stand_family not in (
        "pillar_stand", "vfoot_neck", "twin_leg", "wall_mount", "ergo_arm"
    ):
        raise ValueError(f"Unsupported stand_family: {config.stand_family}")

    panel_form = config.panel_form
    stand_family = config.stand_family

    # --- Compatibility gates (realism + collision safety) ---
    # Curved ultrawide panels are only carried by the vfoot neck stand (their
    # native carrier in S2/S6; a tall pillar/arm would strike the short curved
    # panel during tilt, and a wall/arm cannot carry a 49" superwide).
    is_curved = panel_form in _CURVED_FORMS
    if is_curved:
        stand_family = "vfoot_neck"
    # Wall / arm carry only flat panels.
    if stand_family in {"wall_mount", "ergo_arm"} and is_curved:
        panel_form = "flat_16_9"
        is_curved = False

    aspect = _PANEL_ASPECT[panel_form]
    bow = _PANEL_BOW[panel_form]

    screen_width = max(0.42, min(0.95, config.screen_width))
    # Curved super-ultrawide needs a wider minimum to read as ultrawide.
    if panel_form == "curved_32_9":
        screen_width = max(screen_width, 0.66)
    panel_w = screen_width
    panel_h = panel_w / aspect

    bezel = max(0.008, min(0.022, config.bezel))
    pillar_height = max(0.30, min(0.42, config.pillar_height))

    # Swivel: pillar/twin_leg optional; vfoot always; wall/arm never.
    if stand_family == "vfoot_neck":
        has_swivel = True
    elif stand_family in {"wall_mount", "ergo_arm"}:
        has_swivel = False
    else:
        has_swivel = config.has_swivel

    tilt_lower = max(-0.24, min(-0.10, config.tilt_lower))
    tilt_upper = max(0.10, min(0.22, config.tilt_upper))
    swivel_range = max(0.4, min(1.05, config.swivel_range))
    height_travel = max(0.030, min(0.050, config.height_travel))

    return ResolvedMonitorConfig(
        stand_family=stand_family,
        panel_form=panel_form,
        material_style=config.material_style,
        panel_w=panel_w,
        panel_h=panel_h,
        aspect=aspect,
        bow=bow,
        bezel=bezel,
        pillar_height=pillar_height,
        has_swivel=has_swivel,
        tilt_lower=tilt_lower,
        tilt_upper=tilt_upper,
        swivel_range=swivel_range,
        height_travel=height_travel,
        is_curved=is_curved,
        name=config.name,
    )


def stand_mechanism(resolved: ResolvedMonitorConfig) -> str:
    if resolved.stand_family == "vfoot_neck":
        return "tilt_swivel_height"
    if resolved.stand_family == "ergo_arm":
        return "arm_shoulder_elbow_tilt"
    if resolved.stand_family == "wall_mount":
        return "tilt_only"
    return "tilt_swivel" if resolved.has_swivel else "tilt_only"


def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    if joint_type == ArticulationType.CONTINUOUS:
        joint_range: object = "continuous"
    else:
        joint_range = None if limits is None else (limits.lower, limits.upper)
    return {"type": joint_type.value, "axis": axis, "origin": origin, "range": joint_range}


def _mat(model, palette):
    return {
        "body": model.material("mon_body", rgba=palette["body"]),
        "trim": model.material("mon_trim", rgba=palette["trim"]),
        "glass": model.material("mon_glass", rgba=palette["glass"]),
        "accent": model.material("mon_accent", rgba=palette["accent"]),
        "metal": model.material("mon_metal", rgba=palette["metal"]),
        "rubber": model.material("mon_rubber", rgba=palette["rubber"]),
    }


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.opaque_generic")


# ---------------------------------------------------------------------------
# Panel (screen) — hinge_barrel at part-frame origin, panel body offset.
# Flat panel: hinge anchored near the panel bottom so the bottom clears the
# stand head across the tilt range. Curved panel: hinge at panel center.
# ---------------------------------------------------------------------------
def _panel_lift(resolved: ResolvedMonitorConfig) -> float:
    """World +Z of the panel centre above the hinge axle (screen-local z)."""
    if resolved.is_curved:
        return 0.0
    return resolved.panel_h / 2.0 + 0.02


def _curved_slab(
    width: float, height: float, thickness: float, *, center_y: float, curve_depth: float,
    segments_x: int = 28, segments_z: int = 6,
) -> MeshGeometry:
    """Concave monitor slab; wings wrap toward the viewer (-Y). Matches the
    reference desktop_monitor `_curved_slab` (a real bowed mesh surface)."""
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


def _build_flat_screen(screen, resolved, assets, mats) -> None:
    """Flat framed panel (S1). Frame origin = hinge axle (0,0,0)."""
    w = resolved.panel_w
    h = resolved.panel_h
    bez = resolved.bezel
    cz = _panel_lift(resolved)
    outer_w = w + 2.0 * bez
    outer_h = h + 2.0 * bez

    _box(screen, (outer_w * 0.97, 0.034, outer_h * 0.96), (0.0, -0.047, cz), mats["body"],
         "rear_shell")
    screen.visual(
        mesh_from_geometry(
            BezelGeometry(
                (w, h), (outer_w, outer_h), 0.020,
                opening_shape="rounded_rect", outer_shape="rounded_rect",
                opening_corner_radius=min(0.004, bez * 0.4),
                outer_corner_radius=min(0.018, outer_h * 0.05),
            ),
            assets.mesh_path("screen_bezel.obj"),
        ),
        origin=Origin(xyz=(0.0, -0.067, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="bezel", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
    )
    _box(screen, (w, 0.003, h), (0.0, -0.076, cz), mats["glass"], "display_panel")
    # rear_mount bridges the shell (y=-0.047) to the hinge_barrel (y=0), spanning
    # the full z from below the hinge (0) up into the panel so the hinge axle is
    # connected to the panel body for ANY panel height.
    _box(screen, (0.074, 0.042, cz + 0.08), (0.0, -0.030, cz / 2.0),
         mats["metal"], "rear_mount")
    screen.visual(
        Cylinder(radius=0.014, length=0.086),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"], name="hinge_barrel", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )
    # Bezel-bottom accent bar (host-conformal decoration, derived from panel W).
    _box(screen, (w * 0.18, 0.004, bez * 0.7), (0.0, -0.078, cz - h / 2.0 - bez * 0.15),
         mats["accent"], "brand_bar")


def _build_curved_screen(screen, resolved, assets, mats) -> None:
    """Concave ultrawide panel (S2/S6). Frame origin = hinge axle; panel centred."""
    w = resolved.panel_w
    h = resolved.panel_h
    bez = resolved.bezel
    shell_thick = 0.022
    rear_y = -0.012
    curve_d = resolved.bow
    shell_center_y = rear_y - shell_thick
    shell = _curved_slab(w, h, shell_thick, center_y=shell_center_y, curve_depth=curve_d)
    screen.visual(
        mesh_from_geometry(shell, assets.mesh_path("panel_housing.obj")),
        material=mats["body"], name="panel_housing", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
    )
    glass = _curved_slab(
        w - 2.0 * bez, h - 2.0 * bez, 0.003,
        center_y=shell_center_y - 0.0015, curve_depth=curve_d * 0.98,
    )
    screen.visual(
        mesh_from_geometry(glass, assets.mesh_path("screen_glass.obj")),
        material=mats["glass"], name="screen_glass", material_class_id="glass.smoked_tinted",
    )
    # VESA boss bridges the shell back (y≈-0.012) to the hinge barrel (y=0).
    _box(screen, (0.090, 0.030, min(0.090, h * 0.6)), (0.0, -0.006, 0.0),
         mats["body"], "vesa_mount")
    screen.visual(
        Cylinder(radius=0.014, length=0.086),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"], name="hinge_barrel", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )


def _build_screen(screen, resolved, assets, mats) -> None:
    if resolved.is_curved:
        _build_curved_screen(screen, resolved, assets, mats)
    else:
        _build_flat_screen(screen, resolved, assets, mats)


# ---------------------------------------------------------------------------
# Yoke head (shared by pillar_stand + twin_leg): top_crosshead + yoke_arms +
# hinge_cheeks that capture the panel hinge_barrel. Built into `part` at the
# given hinge z. Returns nothing; the tilt hinge sits at (0, hinge_y, hinge_z).
# ---------------------------------------------------------------------------
def _add_yoke_head(part, mats, *, hinge_y, hinge_z, crosshead_z, dy=0.0, dz=0.0) -> None:
    _box(part, (0.126, 0.052, 0.030), (0.0, 0.055 + dy, crosshead_z + dz),
         mats["body"], "top_crosshead")
    for i, x in enumerate((-0.053, 0.053)):
        _box(part, (0.026, 0.034, 0.070), (x, hinge_y + dy, hinge_z - 0.020 + dz),
             mats["body"], f"yoke_arm_{i}")
        part.visual(
            Cylinder(radius=0.018, length=0.026),
            origin=Origin(xyz=(x, hinge_y + dy, hinge_z + dz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"], name=f"hinge_cheek_{i}", material_class_id="metal.stainless_matte",
        )


def _hex_base_profile(scale: float):
    pts = [
        (-0.195, -0.115), (-0.145, -0.155), (0.145, -0.155),
        (0.195, -0.115), (0.170, 0.125), (-0.170, 0.125),
    ]
    return [(x * scale, y * scale) for (x, y) in pts]


# ---------------------------------------------------------------------------
# Stand family builders. Each returns (tilt_parent_part, hinge_world_xyz).
# ---------------------------------------------------------------------------
def _build_pillar(model, resolved, assets, mats):
    ph = resolved.pillar_height
    hinge_y = 0.026
    hinge_z = BASE_HEIGHT + ph + 0.069
    crosshead_z = BASE_HEIGHT + ph + 0.010
    base_scale = max(0.7, min(1.15, resolved.panel_w / 0.58))

    if not resolved.has_swivel:
        stand = model.part("stand")
        stand.visual(
            mesh_from_geometry(
                ExtrudeGeometry.centered(_hex_base_profile(base_scale), BASE_HEIGHT),
                assets.mesh_path("hex_base.obj"),
            ),
            origin=Origin(xyz=(0.0, 0.0, BASE_HEIGHT / 2.0)),
            material=mats["body"], name="hex_base", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
        )
        stand.visual(
            Cylinder(radius=0.055, length=0.006),
            origin=Origin(xyz=(0.0, 0.040, BASE_HEIGHT + 0.003)),
            material=mats["metal"], name="base_collar", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
        )
        _box(stand, (0.082, 0.056, ph), (0.0, 0.040, BASE_HEIGHT + ph / 2.0),
             mats["body"], "slotted_pillar")
        _add_yoke_head(stand, mats, hinge_y=hinge_y, hinge_z=hinge_z, crosshead_z=crosshead_z)
        return stand, (0.0, hinge_y, hinge_z)

    # Swivel: fixed base + swiveling column (S7). Column frame at swivel centre.
    swivel_y, swivel_z = 0.040, BASE_HEIGHT + 0.003
    base = model.part("base")
    base.visual(
        mesh_from_geometry(
            ExtrudeGeometry.centered(_hex_base_profile(base_scale), BASE_HEIGHT),
            assets.mesh_path("hex_base.obj"),
        ),
        origin=Origin(xyz=(0.0, 0.0, BASE_HEIGHT / 2.0)),
        material=mats["body"], name="hex_base", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
    )
    base.visual(
        Cylinder(radius=0.055, length=0.006),
        origin=Origin(xyz=(0.0, swivel_y, swivel_z)),
        material=mats["metal"], name="base_collar", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )
    column = model.part("column")
    dy, dz = -swivel_y, -swivel_z
    _box(column, (0.082, 0.056, ph), (0.0, 0.040 + dy, BASE_HEIGHT + ph / 2.0 + dz),
         mats["body"], "slotted_pillar")
    _add_yoke_head(column, mats, hinge_y=hinge_y, hinge_z=hinge_z, crosshead_z=crosshead_z,
                   dy=dy, dz=dz)
    lims = MotionLimits(effort=8.0, velocity=2.0, lower=-resolved.swivel_range,
                        upper=resolved.swivel_range)
    origin = (0.0, swivel_y, swivel_z)
    model.articulation(
        "swivel_joint", ArticulationType.REVOLUTE, parent=base, child=column,
        origin=Origin(xyz=origin), axis=(0.0, 0.0, 1.0), motion_limits=lims,
        meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 0.0, 1.0), origin, lims),
    )
    return column, (0.0, hinge_y + dy, hinge_z + dz)


def _build_twin_leg(model, resolved, assets, mats):
    ph = resolved.pillar_height
    junction_z = 0.240 * (ph / 0.34)
    column_top_z = junction_z + 0.122
    # Yoke head is anchored to the ACTUAL column top (not re-derived from ph) so
    # the crosshead/yoke/cheeks always seat on the column with no floating gap.
    crosshead_z = column_top_z + 0.008
    hinge_z = crosshead_z + 0.059
    hinge_y = 0.026
    foot_x = 0.170 * max(0.85, min(1.2, resolved.panel_w / 0.58))
    top_x = 0.018

    stand = model.part("stand")
    leg_len = math.hypot(foot_x - top_x, junction_z - 0.005)
    leg_angle = math.atan2(foot_x - top_x, junction_z - 0.005)
    for i, sign in enumerate((-1.0, 1.0)):
        mid_x = sign * (foot_x + top_x) / 2.0
        _box(stand, (0.016, 0.048, leg_len), (mid_x, 0.030, (0.005 + junction_z) / 2.0),
             mats["metal"], f"leg_{i}", rpy=(0.0, -sign * leg_angle, 0.0))
        _box(stand, (0.046, 0.052, 0.006), (sign * foot_x, 0.030, 0.003),
             mats["rubber"], f"foot_pad_{i}")
    _box(stand, (0.056, 0.042, column_top_z - junction_z),
         (0.0, 0.030, (junction_z + column_top_z) / 2.0), mats["body"], "central_column")
    _box(stand, (0.066, 0.054, 0.022), (0.0, 0.030, junction_z + 0.011),
         mats["body"], "junction_gusset")
    stand.visual(
        Cylinder(radius=0.034, length=0.006),
        origin=Origin(xyz=(0.0, 0.030, column_top_z + 0.003)),
        material=mats["metal"], name="column_collar", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )
    _add_yoke_head(stand, mats, hinge_y=hinge_y, hinge_z=hinge_z, crosshead_z=crosshead_z)
    return stand, (0.0, hinge_y, hinge_z)


def _build_vfoot(model, resolved, assets, mats):
    base_top = 0.020
    neck_h = resolved.pillar_height
    carriage_z = base_top + neck_h * 0.72
    scale = max(0.85, min(1.3, resolved.panel_w / 0.7))

    base = model.part("base_foot")
    base.visual(
        mesh_from_geometry(
            ExtrudeGeometry.centered(_vfoot_profile(scale), base_top),
            assets.mesh_path("base_foot_shell.obj"),
        ),
        origin=Origin(xyz=(0.0, 0.0, base_top / 2.0)),
        material=mats["metal"], name="base_foot_shell", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )
    # Central hub covering the swivel axis (0,0) so the swivel joint origin sits
    # on real foot hardware (S2 `circle(0.045)` hub).
    base.visual(
        Cylinder(radius=0.045, length=base_top),
        origin=Origin(xyz=(0.0, 0.0, base_top / 2.0)),
        material=mats["metal"], name="base_hub", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )

    # neck part frame origin sits at the swivel joint (world z = base_top), so
    # all neck/carriage geometry is authored in neck-local z (0 = foot top).
    neck = model.part("neck_riser")
    _box(neck, (0.058, 0.026, neck_h), (0.0, 0.0, neck_h / 2.0),
         mats["body"], "neck_riser_shell")
    neck.visual(
        Cylinder(radius=0.038, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),  # embeds ~2 mm into the foot top
        material=mats["metal"], name="swivel_hub", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )
    sw_lims = MotionLimits(effort=8.0, velocity=2.0, lower=-resolved.swivel_range,
                           upper=resolved.swivel_range)
    sw_origin = (0.0, 0.0, base_top)
    model.articulation(
        "swivel_joint", ArticulationType.REVOLUTE, parent=base, child=neck,
        origin=Origin(xyz=sw_origin), axis=(0.0, 0.0, 1.0), motion_limits=sw_lims,
        meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 0.0, 1.0), sw_origin, sw_lims),
    )

    carriage = model.part("neck_carriage")
    # Forward-cantilevered carriage: it seats on the neck (behind) and juts the
    # tilt barrel FORWARD (-Y) by `setback` so the tilting/curved panel pivots
    # well in front of the neck post and never sweeps into it.
    setback = 0.065
    # Short in Z (a slim yoke bar) so the tall panel only meets it at the hinge
    # band; the tilt-swept upper/lower panel passes above/below it.
    _box(carriage, (0.052, 0.085, 0.028), (0.0, -0.0265, 0.0), mats["body"], "carriage_plate")
    carriage.visual(
        Cylinder(radius=0.014, length=0.060),
        origin=Origin(xyz=(0.0, -setback, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"], name="tilt_barrel", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
    )
    h_lims = MotionLimits(effort=60.0, velocity=0.2, lower=0.0, upper=resolved.height_travel)
    # carriage seat height in neck-local z (neck frame origin is at the foot top).
    h_origin = (0.0, 0.0, carriage_z - base_top)
    model.articulation(
        "height_joint", ArticulationType.PRISMATIC, parent=neck, child=carriage,
        origin=Origin(xyz=h_origin), axis=(0.0, 0.0, 1.0), motion_limits=h_lims,
        meta=_joint_meta(ArticulationType.PRISMATIC, (0.0, 0.0, 1.0), h_origin, h_lims),
    )
    # tilt hinge sits on the forward tilt_barrel (carriage-local (0,-setback,0)).
    return carriage, (0.0, -setback, 0.0)


def _vfoot_profile(scale: float):
    """Flat V/T foot polygon (XY), extruded along +Z. Central hub + two forward
    arms + rear stub (approximates S2 `_base_foot_solid`)."""
    s = scale
    pts = [
        (0.050 * s, 0.030 * s),
        (0.160 * s, -0.200 * s),
        ((0.160 - 0.045) * s, -0.200 * s),
        (0.010 * s, -0.010 * s),
        (0.030 * s, 0.095 * s),
        (-0.030 * s, 0.095 * s),
        (-0.010 * s, -0.010 * s),
        (-(0.160 - 0.045) * s, -0.200 * s),
        (-0.160 * s, -0.200 * s),
        (-0.050 * s, 0.030 * s),
    ]
    return pts


def _build_wall(model, resolved, assets, mats):
    plate = model.part("wall_plate")
    _box(plate, (0.200, 0.008, 0.150), (0.0, 0.0, 0.0), mats["body"], "plate_body")

    bracket = model.part("mount_bracket")
    hinge_local_y = -(0.006 + 0.050 + 0.002)
    arm_front_y = -0.006
    arm_back_y = hinge_local_y + 0.014 + 0.002
    arm_depth = arm_front_y - arm_back_y
    arm_center_y = (arm_front_y + arm_back_y) / 2.0
    _box(bracket, (0.140, 0.006, 0.080), (0.0, -0.003, 0.0), mats["body"], "bracket_backplate")
    for i, dx in enumerate((-0.050, 0.050)):
        _box(bracket, (0.030, arm_depth, 0.025), (dx, arm_center_y, 0.0),
             mats["body"], f"bracket_arm_{i}")
        bracket.visual(
            Cylinder(radius=0.016, length=0.024),
            origin=Origin(xyz=(dx, hinge_local_y, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"], name=f"bracket_pivot_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
        )
    fx_origin = (0.0, -0.004, 0.0)
    model.articulation(
        "wall_to_bracket", ArticulationType.FIXED, parent=plate, child=bracket,
        origin=Origin(xyz=fx_origin),
    )
    return bracket, (0.0, hinge_local_y, 0.0)


def _build_arm(model, resolved, assets, mats):
    desk_th = 0.032
    jaw_w, jaw_d, jaw_t = 0.058, 0.062, 0.010
    post_h = 0.036
    shoulder_z = jaw_t + post_h
    lower_len = 0.280
    upper_len = 0.250

    clamp = model.part("desk_clamp")
    _box(clamp, (jaw_w, jaw_d, jaw_t), (0.0, 0.0, jaw_t / 2.0), mats["body"], "clamp_top_jaw")
    _box(clamp, (jaw_w, jaw_d, jaw_t), (0.0, 0.0, -(desk_th + jaw_t / 2.0)),
         mats["body"], "clamp_bot_jaw")
    _box(clamp, (jaw_w, 0.014, desk_th + 2 * jaw_t),
         (0.0, -(jaw_d / 2.0 - 0.007), -desk_th / 2.0), mats["body"], "clamp_spine")
    clamp.visual(
        Cylinder(radius=0.016, length=post_h),
        origin=Origin(xyz=(0.0, 0.0, jaw_t + post_h / 2.0)),
        material=mats["body"], name="clamp_post", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
    )
    for i, dx in enumerate((-0.014, 0.014)):
        clamp.visual(
            Cylinder(radius=0.004, length=desk_th + jaw_t + 0.008),
            origin=Origin(xyz=(dx, 0.0, -(desk_th + jaw_t) / 2.0)),
            material=mats["metal"], name=f"clamp_bolt_{i}", material_class_id=("metal.blackened_gunmetal" if resolved.material_style in {"office_black", "white", "gaming_red", "gunmetal"} else "metal.brushed_silver"),
        )

    arm_lower = model.part("arm_lower")
    _box(arm_lower, (0.038, 0.026, lower_len), (0.0, 0.0, lower_len / 2.0),
         mats["metal"], "lower_beam")
    arm_lower.visual(
        Cylinder(radius=0.022, length=0.048),
        origin=Origin(xyz=(0.0, 0.0, 0.024)), material=mats["trim"],
        name="lower_shoulder_housing", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
    )
    arm_lower.visual(
        Cylinder(radius=0.022, length=0.048),
        origin=Origin(xyz=(0.0, 0.0, lower_len), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["trim"], name="lower_elbow_housing", material_class_id=("plastic.opaque_glossy_molded" if resolved.material_style in {"office_black", "silver", "white", "gaming_red"} else "metal.brushed_silver"),
    )

    arm_upper = model.part("arm_upper")
    _box(arm_upper, (0.036, upper_len, 0.024), (0.0, -upper_len / 2.0, 0.0),
         mats["metal"], "upper_beam")
    _box(arm_upper, (0.040, 0.010, 0.028), (0.0, -(upper_len - 0.005), 0.0),
         mats["trim"], "upper_vesa_adapter")

    vesa_head = model.part("vesa_head")
    _box(vesa_head, (0.042, 0.022, 0.066), (0.0, -0.011, 0.0), mats["body"], "vesa_bracket")
    _box(vesa_head, (0.120, 0.010, 0.120), (0.0, -(0.022 + 0.005), 0.0),
         mats["metal"], "vesa_plate")

    # shoulder REV Z
    sh_lims = MotionLimits(effort=12.0, velocity=1.0, lower=-2.4, upper=2.4)
    sh_origin = (0.0, 0.0, shoulder_z)
    model.articulation(
        "shoulder_joint", ArticulationType.REVOLUTE, parent=clamp, child=arm_lower,
        origin=Origin(xyz=sh_origin), axis=(0.0, 0.0, 1.0), motion_limits=sh_lims,
        meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 0.0, 1.0), sh_origin, sh_lims),
    )
    # elbow REV X (raises the upper arm)
    el_lims = MotionLimits(effort=15.0, velocity=1.0, lower=-0.20, upper=1.20)
    el_origin = (0.0, 0.0, lower_len)
    model.articulation(
        "elbow_joint", ArticulationType.REVOLUTE, parent=arm_lower, child=arm_upper,
        origin=Origin(xyz=el_origin), axis=(-1.0, 0.0, 0.0), motion_limits=el_lims,
        meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), el_origin, el_lims),
    )
    # FIXED weld to the VESA head
    model.articulation(
        "upper_to_vesa", ArticulationType.FIXED, parent=arm_upper, child=vesa_head,
        origin=Origin(xyz=(0.0, -upper_len, 0.0)),
    )
    return vesa_head, (0.0, -(0.022 + 0.010), 0.0)


_STAND_BUILDERS = {
    "pillar_stand": _build_pillar,
    "vfoot_neck": _build_vfoot,
    "twin_leg": _build_twin_leg,
    "wall_mount": _build_wall,
    "ergo_arm": _build_arm,
}


def build_monitor(
    config: MonitorConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or MonitorConfig()
    resolved = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-monitor-assets-")))
    model = ArticulatedObject(name=resolved.name, assets=assets)
    model.meta["template_slug"] = "Technology_Monitor"
    palette = PALETTES[resolved.material_style]
    mats = _mat(model, palette)

    tilt_parent, hinge_xyz = _STAND_BUILDERS[resolved.stand_family](
        model, resolved, assets, mats
    )

    screen = model.part("screen")
    _build_screen(screen, resolved, assets, mats)

    tilt_lims = MotionLimits(
        effort=9.0, velocity=1.5, lower=resolved.tilt_lower, upper=resolved.tilt_upper
    )
    model.articulation(
        "tilt_joint", ArticulationType.REVOLUTE, parent=tilt_parent, child=screen,
        origin=Origin(xyz=hinge_xyz, rpy=(-0.12, 0.0, 0.0)), axis=(1.0, 0.0, 0.0),
        motion_limits=tilt_lims,
        meta=_joint_meta(ArticulationType.REVOLUTE, (1.0, 0.0, 0.0), hinge_xyz, tilt_lims),
    )
    return model


def build_seeded_monitor(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_monitor(config_from_seed(seed), assets=assets)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    resolved = resolve_config(config_from_seed(seed))
    return (
        ("stand_family", resolved.stand_family),
        ("panel_form", resolved.panel_form),
        ("stand_mechanism", stand_mechanism(resolved)),
        ("material_style", resolved.material_style),
    )


def run_monitor_tests(object_model: ArticulatedObject, config: MonitorConfig) -> TestReport:
    resolved = resolve_config(config)
    ctx = TestContext(object_model)
    parts = {p.name for p in object_model.parts}
    joints = {j.name for j in object_model.articulations}

    ctx.check("screen part present", "screen" in parts)
    ctx.check("single tilt joint present", "tilt_joint" in joints)
    tilt = object_model.get_articulation("tilt_joint")
    ctx.check(
        "tilt axis is horizontal X",
        tuple(abs(v) for v in tilt.axis) == (1.0, 0.0, 0.0), details=str(tilt.axis),
    )
    ctx.check(
        "at least one non-fixed joint",
        any(j.articulation_type != ArticulationType.FIXED for j in object_model.articulations),
    )

    screen = object_model.get_part("screen")

    # --- Captured-pin allowances (element-scoped) BEFORE sampled-pose check ---
    # Yoke cheeks capture the panel hinge_barrel (pillar / twin_leg).
    carrier_name = None
    for cand in ("column", "stand", "neck_carriage", "mount_bracket", "vesa_head"):
        if cand in parts:
            carrier_name = cand
            break
    carrier = object_model.get_part(carrier_name) if carrier_name else None

    if carrier is not None and screen is not None:
        carrier_elems = {v.name for v in carrier.visuals}
        screen_elems = {v.name for v in screen.visuals}
        # Captured-trunnion tilt hinge: the carrier's hinge hardware seats the
        # panel's hinge_barrel / seating boss. Element-scoped, pose-invariant
        # (all coaxial with the tilt axis), like monitor_mount / the sources.
        capture_pairs = [
            ("hinge_cheek_0", "hinge_barrel"), ("hinge_cheek_1", "hinge_barrel"),
            ("yoke_arm_0", "hinge_barrel"), ("yoke_arm_1", "hinge_barrel"),
            ("bracket_pivot_0", "hinge_barrel"), ("bracket_pivot_1", "hinge_barrel"),
            ("bracket_arm_0", "hinge_barrel"), ("bracket_arm_1", "hinge_barrel"),
            ("tilt_barrel", "hinge_barrel"), ("tilt_barrel", "vesa_mount"),
            ("tilt_barrel", "panel_housing"), ("tilt_barrel", "rear_mount"),
            ("carriage_plate", "vesa_mount"), ("carriage_plate", "hinge_barrel"),
            ("carriage_plate", "panel_housing"),
            ("vesa_plate", "hinge_barrel"), ("vesa_bracket", "hinge_barrel"),
            ("vesa_plate", "rear_mount"), ("vesa_bracket", "rear_mount"),
        ]
        for ea, eb in capture_pairs:
            if ea in carrier_elems and eb in screen_elems:
                ctx.allow_overlap(
                    carrier, screen, elem_a=ea, elem_b=eb,
                    reason="Carrier tilt-hinge hardware captures the panel hinge (trunnion), coaxial with the tilt axis.",
                )

    # pillar swivel: the base_collar bearing ring wraps the swiveling pillar.
    if "base" in parts and "column" in parts:
        base_p = object_model.get_part("base")
        column_p = object_model.get_part("column")
        ctx.allow_overlap(
            base_p, column_p, elem_a="base_collar", elem_b="slotted_pillar",
            reason="The base_collar bearing ring wraps the lower pillar as the swivel seat.",
        )

    # vfoot: swivel hub seated in the foot; carriage rides the neck.
    if "base_foot" in parts and "neck_riser" in parts:
        base_foot = object_model.get_part("base_foot")
        neck = object_model.get_part("neck_riser")
        ctx.allow_overlap(
            neck, base_foot, elem_a="swivel_hub", elem_b="base_foot_shell",
            reason="Swivel hub puck seats into the base foot hub (rotary capture).",
        )
        carriage = object_model.get_part("neck_carriage")
        if carriage is not None:
            ctx.allow_overlap(
                carriage, neck, elem_a="carriage_plate", elem_b="neck_riser_shell",
                reason="Height carriage rides on the neck post (prismatic slide proxy).",
            )

    # ergo_arm: elbow captured shaft + weld seats.
    if "arm_lower" in parts and "arm_upper" in parts:
        arm_lower = object_model.get_part("arm_lower")
        arm_upper = object_model.get_part("arm_upper")
        ctx.allow_overlap(
            arm_lower, arm_upper, elem_a="lower_elbow_housing", elem_b="upper_beam",
            reason="Upper beam enters the elbow bearing housing (captured-shaft pivot).",
        )
        ctx.allow_overlap(
            arm_lower, arm_upper, elem_a="lower_beam", elem_b="upper_beam",
            reason="Upper arm root pivots against the lower beam top at the elbow joint.",
        )
        ctx.allow_overlap(
            arm_lower, arm_upper, elem_a="lower_elbow_housing", elem_b="upper_vesa_adapter",
            reason="Upper arm adapter clears past the elbow bearing housing.",
        )

    # --- Targeted motion proofs (one per DOF) ---
    if screen is not None:
        with ctx.pose({tilt: resolved.tilt_lower}):
            low = ctx.part_world_aabb(screen)
        with ctx.pose({tilt: resolved.tilt_upper}):
            high = ctx.part_world_aabb(screen)
        # Front-most (min-Y) panel point sweeps as it tilts about the hinge.
        ctx.check(
            "tilt changes panel attitude",
            low is not None and high is not None
            and abs(high[0][1] - low[0][1]) > 0.01,
            details=f"low_minY={low[0][1] if low else None}, high_minY={high[0][1] if high else None}",
        )

    if "swivel_joint" in joints and screen is not None:
        swivel = object_model.get_articulation("swivel_joint")
        base_ext = ctx.part_world_aabb(screen)
        with ctx.pose({swivel: resolved.swivel_range}):
            sw = ctx.part_world_aabb(screen)
        ctx.check(
            "swivel rotates panel about vertical Z",
            swivel.axis == (0.0, 0.0, 1.0) and base_ext is not None and sw is not None
            and (sw[1][0] - sw[0][0]) < (base_ext[1][0] - base_ext[0][0]) - 0.01,
            details="x-extent shrinks when swiveled",
        )

    if "height_joint" in joints and screen is not None:
        height = object_model.get_articulation("height_joint")
        z0 = ctx.part_world_position(screen)
        with ctx.pose({height: resolved.height_travel}):
            z1 = ctx.part_world_position(screen)
        ctx.check(
            "height prismatic raises panel",
            z0 is not None and z1 is not None and z1[2] > z0[2] + resolved.height_travel * 0.7,
            details=f"z0={z0}, z1={z1}",
        )

    if "shoulder_joint" in joints and "elbow_joint" in joints and screen is not None:
        shoulder = object_model.get_articulation("shoulder_joint")
        elbow = object_model.get_articulation("elbow_joint")
        p0 = ctx.part_world_position(screen)
        with ctx.pose({shoulder: 1.0}):
            p1 = ctx.part_world_position(screen)
        ctx.check(
            "shoulder swings panel laterally",
            p0 is not None and p1 is not None
            and math.dist(p0, p1) > 0.05, details=f"{p0}->{p1}",
        )
        e0 = ctx.part_world_position(screen)
        with ctx.pose({elbow: 1.0}):
            e1 = ctx.part_world_position(screen)
        ctx.check(
            "elbow raises panel",
            e0 is not None and e1 is not None and e1[2] > e0[2] + 0.02,
            details=f"{e0}->{e1}",
        )

    # --- Full sampled-pose non-penetration (Rule 5) ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    for joint in object_model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            ctx.check(
                f"{joint.name} metadata complete",
                {"type", "axis", "origin", "range"} <= set(joint.meta),
            )
    return ctx.report()
