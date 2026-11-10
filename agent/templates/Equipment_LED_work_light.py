# SPDX-License-Identifier: Apache-2.0

"""Portable rechargeable LED work / flood light modular template.

A static support mechanism (``mount``) lifts a rectangular / round LED flood
``head`` off the ground; the head tilts up and down about a horizontal left-right
(Y) axis (REVOLUTE). The head face is a glass diffuser + black bezel + LED array,
usually with a yellow battery pack and a U-shaped carry handle. The primary
mechanism is always the head tilt; mount and head slots may add folding legs
(REVOLUTE), a hanging hook (REVOLUTE), a pan turntable (REVOLUTE-Z) or a lifting
mast (PRISMATIC-Z).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Equipment_LED_work_light.md`` and the
``picture/Equipment/LED work light`` 5-star sample family (1 parent + 9 slot
forks), read from the ``articraft_data`` repo (workbench-only forks).

Slot graph (pattern = ``mixed``), a serial chain mount -> head + a panel form
axis + a led-count multiplicity axis:

  * ``mount_style`` (4): h_frame_stand / folding_aframe / tripod_mast /
    handheld_hook -- the ground structure. folding_aframe adds 2 leg REVOLUTE-Y
    fold joints; handheld_hook adds 1 hook REVOLUTE-Y; the others add none.
  * ``head_style`` (3): side_tilt (1 REVOLUTE-Y, head hangs straight off the
    mount) / tilt_pan_yoke (REVOLUTE-Z pan + REVOLUTE-Y tilt via a ``u_yoke``
    part, battery removed) / telescope_tilt (PRISMATIC-Z lift + REVOLUTE-Y tilt
    via an ``inner_mast`` part).
  * ``panel_style`` (3): rect_flood (rectangular tub + Box LED grid) /
    cob_round_disc (lathe round cup + concentric LED rings) / dual_flood_bar
    (two side-by-side housings on a shared crossbar).
  * ``led_count`` (rows x cols, rect_flood only): a multiplicity axis -- N Box
    LED dots inlined as non-moving visuals (Rule 1) on ``light_head``.

All pivot bearings are captured-pin / sleeve geometry (boss-in-cradle, pin
through sleeve, sliding mast in sleeve), so those joints omit ``MatingContract``
(grandfathered) and are guarded by the flat articulation-origin baseline +
element-scoped ``allow_overlap`` mirroring each source record's run_tests block.

Compatibility gating (resolve_config, spec compatibility matrix):
  * ``dual_flood_bar`` x ``telescope_tilt`` -> the twin-head mass on a lifting
    arm risks CoM / intersection, so the panel degrades to ``rect_flood``.
  * ``tilt_pan_yoke`` removes the head ``battery_pack`` / ``battery_port_panel``
    to clear the U-yoke hollow.
  * ``cob_round_disc`` forces a square head (``head_h == head_w``).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
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

MountStyle = Literal["h_frame_stand", "folding_aframe", "tripod_mast", "handheld_hook"]
HeadStyle = Literal["side_tilt", "tilt_pan_yoke", "telescope_tilt"]
PanelStyle = Literal["rect_flood", "cob_round_disc", "dual_flood_bar"]
PaletteStyle = Literal[
    "safety_yellow",
    "hi_vis_orange",
    "contractor_blue",
    "industrial_red",
    "gunmetal_gray",
    "lime_green",
]

MOUNT_STYLES: tuple[MountStyle, ...] = (
    "h_frame_stand",
    "folding_aframe",
    "tripod_mast",
    "handheld_hook",
)
HEAD_STYLES: tuple[HeadStyle, ...] = ("side_tilt", "tilt_pan_yoke", "telescope_tilt")
PANEL_STYLES: tuple[PanelStyle, ...] = (
    "rect_flood",
    "cob_round_disc",
    "dual_flood_bar",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_yellow",
    "hi_vis_orange",
    "contractor_blue",
    "industrial_red",
    "gunmetal_gray",
    "lime_green",
)

# Per-mount central node height (where the shared support column/neck attaches).
MOUNT_COLUMN_BASE_Z: dict[str, float] = {
    "h_frame_stand": 0.018,
    "folding_aframe": 0.060,
    "tripod_mast": 0.045,
    "handheld_hook": 0.064,
}

# Realistic jobsite-flood colorways. ``frame`` is the painted tube / stand /
# handle / battery; the rest are the black housing, rubber, white diffuser, LED
# tint, and steel hardware (drawn from the 5-star ``safety_yellow`` base).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_yellow": {
        "frame": (0.96, 0.78, 0.06, 1.0),
        "housing": (0.10, 0.10, 0.11, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "glass": (0.93, 0.94, 0.90, 1.0),
        "led": (0.80, 0.84, 0.70, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
    },
    "hi_vis_orange": {
        "frame": (0.95, 0.45, 0.05, 1.0),
        "housing": (0.09, 0.09, 0.10, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "glass": (0.94, 0.93, 0.88, 1.0),
        "led": (0.85, 0.82, 0.66, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
    },
    "contractor_blue": {
        "frame": (0.10, 0.34, 0.66, 1.0),
        "housing": (0.08, 0.08, 0.09, 1.0),
        "rubber": (0.05, 0.05, 0.06, 1.0),
        "glass": (0.92, 0.94, 0.95, 1.0),
        "led": (0.80, 0.86, 0.82, 1.0),
        "steel": (0.58, 0.60, 0.63, 1.0),
    },
    "industrial_red": {
        "frame": (0.74, 0.10, 0.10, 1.0),
        "housing": (0.10, 0.09, 0.09, 1.0),
        "rubber": (0.06, 0.05, 0.05, 1.0),
        "glass": (0.95, 0.93, 0.90, 1.0),
        "led": (0.86, 0.80, 0.68, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
    },
    "gunmetal_gray": {
        "frame": (0.42, 0.44, 0.47, 1.0),
        "housing": (0.13, 0.13, 0.14, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
        "glass": (0.90, 0.92, 0.94, 1.0),
        "led": (0.82, 0.86, 0.84, 1.0),
        "steel": (0.62, 0.64, 0.67, 1.0),
    },
    "lime_green": {
        "frame": (0.46, 0.72, 0.10, 1.0),
        "housing": (0.09, 0.10, 0.09, 1.0),
        "rubber": (0.05, 0.06, 0.05, 1.0),
        "glass": (0.93, 0.95, 0.90, 1.0),
        "led": (0.84, 0.88, 0.70, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Shared real-world dimensions (meters), from the parent record.
# ---------------------------------------------------------------------------
HEAD_D = 0.055  # housing depth (front-to-back, Z in head frame)
GLASS_INSET = 0.018  # bezel border around the glass on each side
FRAME_T = 0.010  # bezel frame wall thickness
PIVOT_R = 0.012  # side pivot boss radius
UPRIGHT_R = 0.010  # painted upright tube radius
TUBE_R = 0.012  # painted base tube radius
FOOT_R = 0.020  # rubber foot radius

LED_RING_COUNTS = (1, 8, 14, 20)  # cob concentric rings (43 emitters)
DUAL_LED_ROWS = 5
DUAL_LED_COLS = 4
DUAL_HOUSING_GAP = 0.018

N_ROWS_MIN, N_ROWS_MAX = 3, 10
N_COLS_MIN, N_COLS_MAX = 3, 12
N_MAX = 120


@dataclass(frozen=True)
class LedWorkLightConfig:
    mount_style: MountStyle | None = None
    head_style: HeadStyle | None = None
    panel_style: PanelStyle | None = None
    led_rows: int | None = None
    led_cols: int | None = None
    palette_style: PaletteStyle = "safety_yellow"
    pivot_z_scale: float = 1.0
    mast_travel: float = 0.055
    tilt_range: float = 0.70
    head_w: float = 0.220
    head_h: float = 0.175
    name: str = "led_work_light"


@dataclass(frozen=True)
class ResolvedLedWorkLightConfig:
    mount_style: MountStyle
    head_style: HeadStyle
    panel_style: PanelStyle
    led_rows: int
    led_cols: int
    palette_style: PaletteStyle
    column_base_z: float
    pivot_z: float
    mast_travel: float
    tilt_range: float
    head_w: float
    head_h: float
    keep_battery: bool
    name: str

    @property
    def head_r(self) -> float:
        return self.head_w / 2.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> LedWorkLightConfig:
    rng = random.Random(seed)
    return LedWorkLightConfig(
        mount_style=rng.choice(MOUNT_STYLES),
        head_style=rng.choice(HEAD_STYLES),
        panel_style=rng.choice(PANEL_STYLES),
        led_rows=rng.randint(N_ROWS_MIN, N_ROWS_MAX),
        led_cols=rng.randint(N_COLS_MIN, N_COLS_MAX),
        palette_style=rng.choice(PALETTE_STYLES),
        pivot_z_scale=round(rng.uniform(0.85, 1.35), 4),
        mast_travel=round(rng.uniform(0.040, 0.075), 4),
        tilt_range=round(rng.uniform(0.50, 0.80), 4),
        head_w=round(rng.uniform(0.18, 0.26), 4),
        head_h=round(rng.uniform(0.18, 0.26), 4),
        name=f"seeded_led_work_light_{seed}",
    )


def resolve_config(
    config: LedWorkLightConfig | None = None,
) -> ResolvedLedWorkLightConfig:
    cfg = config or LedWorkLightConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    mount_style = _pick(cfg.mount_style, MOUNT_STYLES)
    head_style = _pick(cfg.head_style, HEAD_STYLES)
    panel_style = _pick(cfg.panel_style, PANEL_STYLES)

    # --- Compatibility gating. ---
    # (1) twin head on a lifting mast risks CoM / intersection -> degrade panel.
    if panel_style == "dual_flood_bar" and head_style == "telescope_tilt":
        panel_style = "rect_flood"
    # (2) tilt_pan clears the U-yoke hollow and telescope clears the central
    #     sliding pole, so both remove the rear battery; side_tilt keeps it.
    keep_battery = head_style == "side_tilt"

    head_w = _clamp(cfg.head_w, 0.18, 0.26)
    if panel_style == "cob_round_disc":
        head_h = head_w  # round head is square in elevation
    else:
        head_h = _clamp(cfg.head_h, 0.18, 0.26)

    led_rows = int(
        _clamp(int(cfg.led_rows if cfg.led_rows is not None else 5), N_ROWS_MIN, N_ROWS_MAX)
    )
    led_cols = int(
        _clamp(int(cfg.led_cols if cfg.led_cols is not None else 8), N_COLS_MIN, N_COLS_MAX)
    )
    # Cap total LED count by trimming columns (keeps the row pitch readable).
    while led_rows * led_cols > N_MAX and led_cols > N_COLS_MIN:
        led_cols -= 1

    column_base_z = MOUNT_COLUMN_BASE_Z[mount_style]
    # tilt_pan needs a taller pivot so the head clears the U-yoke sitting under
    # it; side_tilt / telescope hang the head straight off outboard supports.
    pivot_floor = column_base_z + (0.140 if head_style == "tilt_pan_yoke" else 0.090)
    pivot_z = _clamp(0.150 * _clamp(cfg.pivot_z_scale, 0.85, 1.35), pivot_floor, 0.245)

    mast_travel = _clamp(cfg.mast_travel, 0.040, 0.075)
    tilt_range = _clamp(cfg.tilt_range, 0.50, 0.80)

    return ResolvedLedWorkLightConfig(
        mount_style=mount_style,
        head_style=head_style,
        panel_style=panel_style,
        led_rows=led_rows,
        led_cols=led_cols,
        palette_style=palette_style,
        column_base_z=column_base_z,
        pivot_z=pivot_z,
        mast_travel=mast_travel,
        tilt_range=tilt_range,
        head_w=head_w,
        head_h=head_h,
        keep_battery=keep_battery,
        name=cfg.name or "led_work_light",
    )


def slot_choices_for_config(
    config: LedWorkLightConfig | ResolvedLedWorkLightConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedLedWorkLightConfig) else resolve_config(config)
    led_choice = f"r{r.led_rows}c{r.led_cols}" if r.panel_style == "rect_flood" else "fixed"
    return (
        ("mount", r.mount_style),
        ("head", r.head_style),
        ("panel", r.panel_style),
        ("led_count", led_choice),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Mesh helpers (mirroring the source records, primitive types preserved).
# ---------------------------------------------------------------------------
def _tube(points, radius, name, *, segments=18):
    return mesh_from_geometry(
        tube_from_spline_points(
            points,
            radius=radius,
            samples_per_segment=14,
            radial_segments=segments,
            cap_ends=True,
        ),
        name,
    )


def _lathe(profile, name, *, segments=96):
    return mesh_from_geometry(LatheGeometry(profile, segments=segments, closed=True), name)


def _open_tube(radius_outer, radius_inner, height, name, *, assets):
    """CadQuery open-ended annular sleeve, authored upright along local +Z."""
    sleeve = cq.Workplane("XY").circle(radius_outer).circle(radius_inner).extrude(height)
    return mesh_from_cadquery(sleeve, name, assets=assets, tolerance=0.0006, angular_tolerance=0.08)


# ===========================================================================
# MOUNT modules (Slot A). Each emits the ground structure on ``stand`` and any
# mount-local joints, then returns the central-node height where the shared
# support column attaches.
# ===========================================================================
def _build_h_frame_stand(model, stand, r, mats, *, assets) -> float:
    base_len, base_span = 0.260, 0.210
    half_span, half_len = base_span / 2.0, base_len / 2.0
    rail_lift, foot_inset = 0.018, 0.026
    for sign, tag in ((1.0, "pos_y"), (-1.0, "neg_y")):
        y = sign * half_span
        rail_pts = [
            (-half_len + foot_inset, y, 0.006),
            (-half_len + 0.060, y, rail_lift),
            (half_len - 0.060, y, rail_lift),
            (half_len - foot_inset, y, 0.006),
        ]
        stand.visual(
            _tube(rail_pts, TUBE_R, f"side_rail_{tag}"),
            material=mats["frame"],
            name=f"side_rail_{tag}", material_class_id="metal.paint_coated",
        )
    cross_pts = [(0.0, -half_span, rail_lift), (0.0, 0.0, rail_lift), (0.0, half_span, rail_lift)]
    stand.visual(
        _tube(cross_pts, TUBE_R, "base_cross_member"),
        material=mats["frame"],
        name="base_cross_member", material_class_id="metal.paint_coated",
    )
    for sx, sy, tag in ((1.0, 1.0, "fr"), (1.0, -1.0, "br"), (-1.0, 1.0, "fl"), (-1.0, -1.0, "bl")):
        stand.visual(
            Cylinder(radius=FOOT_R, length=0.052),
            origin=Origin(
                xyz=(sx * (half_len - foot_inset), sy * half_span, 0.006),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["rubber"],
            name=f"foot_{tag}", material_class_id="rubber.smooth_plain",
        )
    return rail_lift


def _build_folding_aframe(model, stand, r, mats, *, assets) -> float:
    apex_z = MOUNT_COLUMN_BASE_Z["folding_aframe"]
    base_len, base_span = 0.285, 0.230
    half_span, half_len = base_span / 2.0, base_len / 2.0
    upright_top_y = r.head_w / 2.0 + 0.018
    pin_outer_y = upright_top_y + 0.030
    cross_pts = [(0.0, -pin_outer_y, apex_z), (0.0, 0.0, apex_z), (0.0, pin_outer_y, apex_z)]
    stand.visual(
        _tube(cross_pts, TUBE_R, "apex_crossbar"), material=mats["frame"], name="apex_crossbar", material_class_id="metal.paint_coated"
    )
    hinge_x = 0.030
    for i, sx in enumerate((1.0, -1.0)):
        stand.visual(
            _tube(
                [
                    (0.0, -pin_outer_y, apex_z),
                    (sx * hinge_x, -pin_outer_y, apex_z),
                    (sx * hinge_x, pin_outer_y, apex_z),
                    (0.0, pin_outer_y, apex_z),
                ],
                0.008,
                f"leg_pin_{i}",
                segments=16,
            ),
            material=mats["steel"],
            name=f"leg_pin_{i}", material_class_id="metal.stainless_matte",
        )
    # Two folding legs (jointed children) that splay to the ground.
    for i, sx in enumerate((1.0, -1.0)):
        leg = model.part(f"folding_leg_{i}")
        leg.visual(
            Cylinder(radius=0.014, length=2.0 * upright_top_y + 0.012),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["frame"],
            name="hinge_barrel", material_class_id="metal.paint_coated",
        )
        local_foot_x = sx * (half_len - 0.014) - sx * hinge_x
        local_foot_z = TUBE_R - apex_z
        strut_root_z = -0.019
        for j, sy in enumerate((1.0, -1.0)):
            strut_pts = [
                (0.0, sy * (upright_top_y - 0.020), strut_root_z),
                (
                    0.50 * local_foot_x,
                    sy * (half_span - 0.030),
                    strut_root_z + 0.50 * (local_foot_z - strut_root_z),
                ),
                (local_foot_x, sy * (half_span - 0.018), local_foot_z),
            ]
            leg.visual(
                _tube(strut_pts, TUBE_R * 0.78, f"leg_{i}_strut_{j}"),
                material=mats["frame"],
                name=f"side_strut_{j}", material_class_id="metal.paint_coated",
            )
        foot_pts = [
            (local_foot_x, -half_span + 0.012, local_foot_z),
            (local_foot_x, 0.0, local_foot_z),
            (local_foot_x, half_span - 0.012, local_foot_z),
        ]
        leg.visual(
            _tube(foot_pts, TUBE_R, f"leg_{i}_foot_bar"), material=mats["frame"], name="foot_bar", material_class_id="metal.paint_coated"
        )
        for j, sy in enumerate((1.0, -1.0)):
            leg.visual(
                Cylinder(radius=FOOT_R, length=0.042),
                origin=Origin(
                    xyz=(local_foot_x, sy * (half_span - 0.008), local_foot_z),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["rubber"],
                name=f"rubber_foot_{j}", material_class_id="rubber.smooth_plain",
            )
        model.articulation(
            f"stand_to_leg_{i}",
            ArticulationType.REVOLUTE,
            parent=stand,
            child=leg,
            origin=Origin(xyz=(sx * hinge_x, 0.0, apex_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=-0.35, upper=0.55),
        )
    return apex_z


def _build_tripod_mast(model, stand, r, mats, *, assets) -> float:
    hub_z = 0.035
    column_base_z = MOUNT_COLUMN_BASE_Z["tripod_mast"]
    tripod_radius, leg_r, foot_r = 0.165, 0.010, 0.017
    stand.visual(
        Cylinder(radius=0.028, length=0.028),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=mats["frame"],
        name="hub_collar", material_class_id="metal.paint_coated",
    )
    for i in range(3):
        angle = math.radians(90.0 + i * 120.0)
        ca, sa = math.cos(angle), math.sin(angle)
        leg_pts = [
            (ca * 0.018, sa * 0.018, hub_z - 0.004),
            (ca * 0.070, sa * 0.070, 0.024),
            (ca * (tripod_radius - 0.030), sa * (tripod_radius - 0.030), 0.014),
            (ca * tripod_radius, sa * tripod_radius, 0.012),
        ]
        stand.visual(_tube(leg_pts, leg_r, f"leg_{i}"), material=mats["frame"], name=f"leg_{i}", material_class_id="metal.paint_coated")
        stand.visual(
            Cylinder(radius=foot_r, length=0.046),
            origin=Origin(
                xyz=(ca * tripod_radius, sa * tripod_radius, 0.012), rpy=(0.0, math.pi / 2.0, angle)
            ),
            material=mats["rubber"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )
    # Short central mast rising from the hub up to the column base.
    stand.visual(
        Cylinder(radius=UPRIGHT_R + 0.002, length=column_base_z - hub_z + 0.020),
        origin=Origin(xyz=(0.0, 0.0, (column_base_z + hub_z) / 2.0)),
        material=mats["frame"],
        name="mast", material_class_id="metal.paint_coated",
    )
    return column_base_z


def _build_handheld_hook(model, stand, r, mats, *, assets) -> float:
    body_x, body_y, body_z = 0.120, 0.270, 0.060
    column_base_z = MOUNT_COLUMN_BASE_Z["handheld_hook"]
    stand.visual(
        Box((body_x, body_y, body_z)),
        origin=Origin(xyz=(0.0, 0.0, body_z / 2.0)),
        material=mats["frame"],
        name="base_shell", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Box((0.072, 0.150, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, body_z + 0.004)),
        material=mats["frame"],
        name="top_saddle", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Box((0.038, 0.085, 0.004)),
        origin=Origin(xyz=(-0.036, 0.0, body_z + 0.015)),
        material=mats["housing"],
        name="control_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    stand.visual(
        Cylinder(radius=0.014, length=0.006),
        origin=Origin(xyz=(-0.036, 0.0, body_z + 0.020)),
        material=mats["rubber"],
        name="power_button", material_class_id="rubber.smooth_plain",
    )
    stand.visual(
        Box((0.032, 0.145, 0.024)),
        origin=Origin(xyz=(-body_x / 2.0 - 0.006, 0.0, 0.018)),
        material=mats["rubber"],
        name="rear_stand_foot", material_class_id="rubber.smooth_plain",
    )
    stand.visual(
        Box((0.024, 0.120, 0.014)),
        origin=Origin(xyz=(body_x / 2.0 - 0.015, 0.0, 0.007)),
        material=mats["rubber"],
        name="front_rubber_pad", material_class_id="rubber.smooth_plain",
    )
    hook_hinge_x = -body_x / 2.0 - 0.008
    hook_hinge_z = body_z - 0.008
    for i, sign in enumerate((-1.0, 1.0)):
        stand.visual(
            Box((0.024, 0.018, 0.032)),
            origin=Origin(xyz=(hook_hinge_x, sign * 0.048, hook_hinge_z)),
            material=mats["frame"],
            name=f"hook_lug_{i}", material_class_id="metal.paint_coated",
        )
        stand.visual(
            Cylinder(radius=0.006, length=0.020),
            origin=Origin(
                xyz=(hook_hinge_x, sign * 0.063, hook_hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["steel"],
            name=f"hook_pin_cap_{i}", material_class_id="metal.stainless_matte",
        )
    # Fold-out hanging hook (jointed child).
    hook = model.part("hanging_hook")
    hook.visual(
        Cylinder(radius=0.006, length=0.108),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="hook_hinge_barrel", material_class_id="metal.stainless_matte",
    )
    hook_pts = [
        (0.000, -0.030, 0.000),
        (-0.035, -0.036, -0.010),
        (-0.095, 0.000, -0.076),
        (-0.035, 0.036, -0.010),
        (0.000, 0.030, 0.000),
    ]
    hook.visual(
        _tube(hook_pts, 0.0055, "folding_hook", segments=18),
        material=mats["steel"],
        name="folding_hook", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "stand_to_hook",
        ArticulationType.REVOLUTE,
        parent=stand,
        child=hook,
        origin=Origin(xyz=(hook_hinge_x, 0.0, hook_hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.5, lower=0.0, upper=1.65),
    )
    return column_base_z


_MOUNT_BUILDERS = {
    "h_frame_stand": _build_h_frame_stand,
    "folding_aframe": _build_folding_aframe,
    "tripod_mast": _build_tripod_mast,
    "handheld_hook": _build_handheld_hook,
}


def _emit_support_pedestal(stand, r, mats, column_base_z) -> None:
    """A short central pedestal seating on the mount node; the head-chain
    column / neck roots into it (keeps the support connected, no island)."""
    stand.visual(
        Cylinder(radius=0.013, length=0.026),
        origin=Origin(xyz=(0.0, 0.0, column_base_z + 0.003)),
        material=mats["frame"],
        name="support_pedestal", material_class_id="metal.paint_coated",
    )


# ===========================================================================
# PANEL modules (Slot C). Emit the flood-head face geometry (housing / bezel /
# glass / LED array) inline on the ``light_head`` part (Rule 1: no joints).
# ===========================================================================
def _emit_rect_flood(head, r, mats, *, assets) -> None:
    head_h, head_w = r.head_h, r.head_w
    back_z = -HEAD_D / 2.0
    front_z = HEAD_D / 2.0
    wall_d = HEAD_D - 0.006
    head.visual(
        Box((head_h, head_w, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, back_z + 0.005)),
        material=mats["housing"],
        name="housing_back", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((FRAME_T, head_w, wall_d)),
        origin=Origin(xyz=(head_h / 2.0 - FRAME_T / 2.0, 0.0, 0.0)),
        material=mats["housing"],
        name="housing_wall_top", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((FRAME_T, head_w, wall_d)),
        origin=Origin(xyz=(-head_h / 2.0 + FRAME_T / 2.0, 0.0, 0.0)),
        material=mats["housing"],
        name="housing_wall_bottom", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((head_h, FRAME_T, wall_d)),
        origin=Origin(xyz=(0.0, head_w / 2.0 - FRAME_T / 2.0, 0.0)),
        material=mats["housing"],
        name="housing_wall_left", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((head_h, FRAME_T, wall_d)),
        origin=Origin(xyz=(0.0, -head_w / 2.0 + FRAME_T / 2.0, 0.0)),
        material=mats["housing"],
        name="housing_wall_right", material_class_id="plastic.opaque_glossy_molded",
    )
    bezel_t = 0.006
    glass_w = head_w - 2.0 * GLASS_INSET
    glass_h = head_h - 2.0 * GLASS_INSET
    head.visual(
        Box((GLASS_INSET, head_w, bezel_t)),
        origin=Origin(xyz=(head_h / 2.0 - GLASS_INSET / 2.0, 0.0, front_z - bezel_t / 2.0)),
        material=mats["housing"],
        name="bezel_top", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((GLASS_INSET, head_w, bezel_t)),
        origin=Origin(xyz=(-head_h / 2.0 + GLASS_INSET / 2.0, 0.0, front_z - bezel_t / 2.0)),
        material=mats["housing"],
        name="bezel_bottom", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((glass_h, GLASS_INSET, bezel_t)),
        origin=Origin(xyz=(0.0, head_w / 2.0 - GLASS_INSET / 2.0, front_z - bezel_t / 2.0)),
        material=mats["housing"],
        name="bezel_left", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((glass_h, GLASS_INSET, bezel_t)),
        origin=Origin(xyz=(0.0, -head_w / 2.0 + GLASS_INSET / 2.0, front_z - bezel_t / 2.0)),
        material=mats["housing"],
        name="bezel_right", material_class_id="plastic.opaque_glossy_molded",
    )
    glass_z = front_z - bezel_t - 0.004
    head.visual(
        Box((glass_h + 0.008, glass_w + 0.008, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, glass_z)),
        material=mats["glass"],
        name="led_glass_panel", material_class_id="glass.frosted_smooth",
    )
    led_size = 0.009
    led_z = glass_z + 0.004
    margin = 0.012
    span_x = glass_h - 2.0 * margin
    span_y = glass_w - 2.0 * margin
    rows, cols = r.led_rows, r.led_cols
    for row in range(rows):
        px = 0.0 if rows == 1 else -span_x / 2.0 + span_x * row / (rows - 1)
        for col in range(cols):
            py = 0.0 if cols == 1 else -span_y / 2.0 + span_y * col / (cols - 1)
            head.visual(
                Box((led_size, led_size, 0.0025)),
                origin=Origin(xyz=(px, py, led_z)),
                material=mats["led"],
                name=f"led_{row}_{col}", material_class_id="tech.emissive_surface",
            )


def _emit_cob_round(head, r, mats, *, assets) -> None:
    head_r = r.head_r
    glass_inset = 0.020
    glass_r = head_r - glass_inset
    back_z = -HEAD_D / 2.0
    front_z = HEAD_D / 2.0
    housing_profile = [
        (0.000, back_z),
        (0.636 * head_r, back_z),
        (0.873 * head_r, back_z + 0.004),
        (head_r - 0.004, -0.010),
        (head_r, 0.004),
        (head_r, front_z - 0.004),
        (head_r - 0.004, front_z),
        (glass_r + 0.006, front_z),
        (glass_r + 0.006, front_z - 0.010),
        (0.673 * head_r, back_z + 0.010),
        (0.000, back_z + 0.010),
    ]
    head.visual(
        _lathe(housing_profile, "round_housing_shell"),
        material=mats["housing"],
        name="round_housing_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    bezel_profile = [
        (glass_r - 0.004, front_z - 0.004),
        (head_r - 0.006, front_z - 0.004),
        (head_r, front_z - 0.001),
        (head_r, front_z + 0.004),
        (head_r - 0.006, front_z + 0.007),
        (glass_r - 0.004, front_z + 0.007),
        (glass_r - 0.008, front_z + 0.003),
        (glass_r - 0.008, front_z - 0.001),
    ]
    head.visual(_lathe(bezel_profile, "ring_bezel"), material=mats["housing"], name="ring_bezel", material_class_id="plastic.opaque_glossy_molded")
    glass_z = front_z - 0.002
    head.visual(
        Cylinder(radius=glass_r - 0.001, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, glass_z)),
        material=mats["glass"],
        name="round_glass_panel", material_class_id="glass.frosted_smooth",
    )
    head.visual(
        Cylinder(radius=glass_r - 0.020, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, glass_z + 0.0035)),
        material=mats["steel"],
        name="cob_carrier_disc", material_class_id="metal.stainless_matte",
    )
    ring_radii = (0.0, glass_r * 0.244, glass_r * 0.500, glass_r * 0.733)
    led_z = glass_z + 0.0060
    led_index = 0
    for ring_i, count in enumerate(LED_RING_COUNTS):
        radius = ring_radii[ring_i]
        for i in range(count):
            angle = 0.0 if count == 1 else (2.0 * math.pi * i / count)
            head.visual(
                Cylinder(radius=0.0033, length=0.0024),
                origin=Origin(xyz=(radius * math.cos(angle), radius * math.sin(angle), led_z)),
                material=mats["led"],
                name=f"led_{led_index}", material_class_id="tech.emissive_surface",
            )
            led_index += 1


def _emit_dual_flood(head, r, mats, *, assets) -> None:
    head_h, head_w = r.head_h, r.head_w
    flood_w = (head_w - DUAL_HOUSING_GAP) / 2.0
    back_z = -HEAD_D / 2.0
    front_z = HEAD_D / 2.0
    wall_d = HEAD_D - 0.006
    bezel_t = 0.006
    # One shared crossbar/axle spanning both housings (single tilt unit).
    head.visual(
        Cylinder(radius=0.008, length=head_w - 0.004),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="shared_crossbar", material_class_id="metal.stainless_matte",
    )
    flood_centers = [(i - 0.5) * (flood_w + DUAL_HOUSING_GAP) for i in range(2)]
    for index, center_y in enumerate(flood_centers):
        glass_w = flood_w - 2.0 * GLASS_INSET
        glass_h = head_h - 2.0 * GLASS_INSET
        glass_z = front_z - bezel_t - 0.004
        head.visual(
            Box((head_h, flood_w, 0.010)),
            origin=Origin(xyz=(0.0, center_y, back_z + 0.005)),
            material=mats["housing"],
            name=f"housing_back_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((FRAME_T, flood_w, wall_d)),
            origin=Origin(xyz=(head_h / 2.0 - FRAME_T / 2.0, center_y, 0.0)),
            material=mats["housing"],
            name=f"housing_wall_top_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((FRAME_T, flood_w, wall_d)),
            origin=Origin(xyz=(-head_h / 2.0 + FRAME_T / 2.0, center_y, 0.0)),
            material=mats["housing"],
            name=f"housing_wall_bottom_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((head_h, FRAME_T, wall_d)),
            origin=Origin(xyz=(0.0, center_y + flood_w / 2.0 - FRAME_T / 2.0, 0.0)),
            material=mats["housing"],
            name=f"housing_wall_outer_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((head_h, FRAME_T, wall_d)),
            origin=Origin(xyz=(0.0, center_y - flood_w / 2.0 + FRAME_T / 2.0, 0.0)),
            material=mats["housing"],
            name=f"housing_wall_inner_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((GLASS_INSET, flood_w, bezel_t)),
            origin=Origin(
                xyz=(head_h / 2.0 - GLASS_INSET / 2.0, center_y, front_z - bezel_t / 2.0)
            ),
            material=mats["housing"],
            name=f"bezel_top_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((GLASS_INSET, flood_w, bezel_t)),
            origin=Origin(
                xyz=(-head_h / 2.0 + GLASS_INSET / 2.0, center_y, front_z - bezel_t / 2.0)
            ),
            material=mats["housing"],
            name=f"bezel_bottom_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((glass_h, GLASS_INSET, bezel_t)),
            origin=Origin(
                xyz=(0.0, center_y + flood_w / 2.0 - GLASS_INSET / 2.0, front_z - bezel_t / 2.0)
            ),
            material=mats["housing"],
            name=f"bezel_outer_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((glass_h, GLASS_INSET, bezel_t)),
            origin=Origin(
                xyz=(0.0, center_y - flood_w / 2.0 + GLASS_INSET / 2.0, front_z - bezel_t / 2.0)
            ),
            material=mats["housing"],
            name=f"bezel_inner_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        head.visual(
            Box((glass_h + 0.008, glass_w + 0.008, 0.010)),
            origin=Origin(xyz=(0.0, center_y, glass_z)),
            material=mats["glass"],
            name=f"led_glass_panel_{index}", material_class_id="glass.frosted_smooth",
        )
        led_size = 0.0075
        led_z = glass_z + 0.004
        margin = 0.010
        span_x = glass_h - 2.0 * margin
        span_y = glass_w - 2.0 * margin
        for row in range(DUAL_LED_ROWS):
            px = -span_x / 2.0 + span_x * row / (DUAL_LED_ROWS - 1)
            for col in range(DUAL_LED_COLS):
                py = center_y - span_y / 2.0 + span_y * col / (DUAL_LED_COLS - 1)
                head.visual(
                    Box((led_size, led_size, 0.0025)),
                    origin=Origin(xyz=(px, py, led_z)),
                    material=mats["led"],
                    name=f"led_{index}_{row}_{col}", material_class_id="tech.emissive_surface",
                )
        screw_x = head_h / 2.0 - 0.010
        screw_y = flood_w / 2.0 - 0.010
        for corner, sx, sy in ((0, 1.0, 1.0), (1, 1.0, -1.0), (2, -1.0, 1.0), (3, -1.0, -1.0)):
            head.visual(
                Cylinder(radius=0.0032, length=0.0018),
                origin=Origin(xyz=(sx * screw_x, center_y + sy * screw_y, front_z + 0.0009)),
                material=mats["steel"],
                name=f"bezel_screw_{index}_{corner}", material_class_id="metal.stainless_matte",
            )


_PANEL_BUILDERS = {
    "rect_flood": _emit_rect_flood,
    "cob_round_disc": _emit_cob_round,
    "dual_flood_bar": _emit_dual_flood,
}

# Which housing-top visual the carry handle roots into (for connectivity).
_HANDLE_ROOT_VISUAL = {
    "rect_flood": "housing_wall_top",
    "cob_round_disc": "round_housing_shell",
    "dual_flood_bar": "housing_wall_top_0",
}


def _emit_head_common(head, r, mats, *, boss_y, boss_len) -> None:
    """Shared head furniture: side pivot bosses, battery pack, carry handle."""
    head_h, head_w = r.head_h, r.head_w
    back_z = -HEAD_D / 2.0
    for sign, tag in ((1.0, "pos_y"), (-1.0, "neg_y")):
        head.visual(
            Cylinder(radius=PIVOT_R, length=boss_len),
            origin=Origin(xyz=(0.0, sign * boss_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name=f"pivot_boss_{tag}", material_class_id="metal.stainless_matte",
        )
    # Internal tilt shaft through the head center: ties the two bosses together
    # and gives the pivot joint origin real child geometry at (0, 0, 0).
    head.visual(
        Cylinder(radius=0.006, length=2.0 * boss_y),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="pivot_shaft", material_class_id="metal.stainless_matte",
    )
    if r.keep_battery:
        batt_w, batt_depth = 0.150, 0.050
        batt_z = back_z - batt_depth / 2.0 + 0.006
        head.visual(
            Box((0.090, batt_w, batt_depth)),
            origin=Origin(xyz=(-0.030, 0.0, batt_z)),
            material=mats["frame"],
            name="battery_pack", material_class_id="metal.paint_coated",
        )
        head.visual(
            Box((0.030, 0.060, 0.010)),
            origin=Origin(xyz=(-0.030, 0.0, batt_z - batt_depth / 2.0 - 0.004)),
            material=mats["housing"],
            name="battery_port_panel", material_class_id="plastic.opaque_glossy_molded",
        )
    # U-shaped carry handle + rubber grip rising from the head top.
    h_rise, h_arc = 0.105, 0.060
    if r.panel_style == "cob_round_disc":
        root_x = r.head_r * 0.67
        root_y = r.head_r * 0.745
        htop = head_h / 2.0
        handle_pts = [
            (root_x, root_y, -0.004),
            (htop + h_rise * 0.55, root_y * 0.85, h_arc * 0.55),
            (htop + h_rise, 0.0, h_arc),
            (htop + h_rise * 0.55, -root_y * 0.85, h_arc * 0.55),
            (root_x, -root_y, -0.004),
        ]
    else:
        htop = head_h / 2.0
        handle_pts = [
            (htop - 0.004, head_w / 2.0 - 0.018, -0.004),
            (htop + h_rise * 0.55, head_w / 2.0 - 0.030, h_arc * 0.55),
            (htop + h_rise, 0.0, h_arc),
            (htop + h_rise * 0.55, -head_w / 2.0 + 0.030, h_arc * 0.55),
            (htop - 0.004, -head_w / 2.0 + 0.018, -0.004),
        ]
    head.visual(
        _tube(handle_pts, 0.010, "carry_handle", segments=20),
        material=mats["frame"],
        name="carry_handle", material_class_id="metal.paint_coated",
    )
    grip_pts = [
        (htop + h_rise - 0.002, 0.045, h_arc + 0.001),
        (htop + h_rise + 0.002, 0.0, h_arc + 0.002),
        (htop + h_rise - 0.002, -0.045, h_arc + 0.001),
    ]
    head.visual(
        _tube(grip_pts, 0.015, "handle_grip", segments=20),
        material=mats["rubber"],
        name="handle_grip", material_class_id="rubber.smooth_plain",
    )


def _build_head(model, r, mats, *, boss_y, boss_len, assets) -> object:
    head = model.part("light_head")
    _PANEL_BUILDERS[r.panel_style](head, r, mats, assets=assets)
    _emit_head_common(head, r, mats, boss_y=boss_y, boss_len=boss_len)
    return head


# ===========================================================================
# HEAD modules (Slot B). Emit the neck on ``stand`` (+ any intermediate part),
# build the head, and wire the pivot joint chain.
# ===========================================================================
def _build_side_tilt(model, stand, r, mats, column_base_z, *, assets) -> None:
    pivot_z = r.pivot_z
    arm_top_y = r.head_w / 2.0 + 0.018
    # Root the uprights outboard of the wide rear battery box (half-width 0.075)
    # so they never flare through it; a base crossbar ties them to the pedestal.
    shoulder_y = max(0.092, r.head_w / 2.0 - 0.005)
    stand.visual(
        Cylinder(radius=0.010, length=2.0 * shoulder_y),
        origin=Origin(xyz=(0.0, 0.0, column_base_z + 0.006), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="shoulder_crossbar", material_class_id="metal.paint_coated",
    )
    for sign, tag in ((1.0, "pos_y"), (-1.0, "neg_y")):
        up_pts = [
            (0.0, sign * shoulder_y, column_base_z + 0.006),
            (0.0, sign * shoulder_y, pivot_z - 0.050),
            (0.0, sign * arm_top_y, pivot_z - 0.034),
            (0.0, sign * arm_top_y, pivot_z),
        ]
        stand.visual(
            _tube(up_pts, UPRIGHT_R, f"upright_{tag}"),
            material=mats["frame"],
            name=f"upright_{tag}", material_class_id="metal.paint_coated",
        )
        stand.visual(
            Cylinder(radius=0.013, length=0.010),
            origin=Origin(
                xyz=(0.0, sign * (arm_top_y + 0.006), pivot_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["housing"],
            name=f"pivot_knob_{tag}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Through pivot axle bridging the two arm tops -> real stand geometry at the
    # joint origin (0, 0, pivot_z); it passes through the head pivot bore.
    stand.visual(
        Cylinder(radius=0.006, length=2.0 * arm_top_y + 0.020),
        origin=Origin(xyz=(0.0, 0.0, pivot_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="pivot_axle", material_class_id="metal.stainless_matte",
    )
    head = _build_head(model, r, mats, boss_y=r.head_w / 2.0 + 0.004, boss_len=0.046, assets=assets)
    model.articulation(
        "stand_to_head",
        ArticulationType.REVOLUTE,
        parent=stand,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=-r.tilt_range, upper=r.tilt_range
        ),
    )


def _build_tilt_pan_yoke(model, stand, r, mats, column_base_z, *, assets) -> None:
    pivot_z = r.pivot_z
    pan_z = column_base_z + 0.025
    tilt_z_in_yoke = pivot_z - pan_z
    # The behind-head yoke structure (crossbar / center post) sits at this yoke
    # height, well below the head's rear wall (head-local z = -0.046).
    z_low = tilt_z_in_yoke - 0.046
    # Fixed central pan post + bearing on the stand.
    stand.visual(
        Cylinder(radius=0.014, length=pan_z - column_base_z),
        origin=Origin(xyz=(0.0, 0.0, (pan_z + column_base_z) / 2.0)),
        material=mats["frame"],
        name="vertical_post", material_class_id="metal.paint_coated",
    )
    stand.visual(
        Cylinder(radius=0.028, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, pan_z - 0.006)),
        material=mats["housing"],
        name="pan_bearing_top", material_class_id="plastic.opaque_glossy_molded",
    )
    # Panning U-yoke (intermediate part); local origin on the bearing plane.
    yoke = model.part("u_yoke")
    yoke.visual(
        Cylinder(radius=0.032, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material=mats["housing"],
        name="yoke_turntable", material_class_id="plastic.opaque_glossy_molded",
    )
    yoke.visual(
        Cylinder(radius=0.020, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.018)),
        material=mats["frame"],
        name="support_socket", material_class_id="metal.paint_coated",
    )
    yoke.visual(
        Cylinder(radius=UPRIGHT_R, length=z_low - 0.020),
        origin=Origin(xyz=(0.0, 0.0, 0.020 + (z_low - 0.020) / 2.0)),
        material=mats["frame"],
        name="center_post", material_class_id="metal.paint_coated",
    )
    fork_half = r.head_w / 2.0 + 0.024
    yoke.visual(
        Cylinder(radius=0.0075, length=2.0 * fork_half),
        origin=Origin(xyz=(0.0, 0.0, z_low), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="lower_fork_crossbar", material_class_id="metal.paint_coated",
    )
    for sign, tag in ((1.0, "pos_y"), (-1.0, "neg_y")):
        y = sign * fork_half
        # Run behind the head at z_low to the outboard line, then rise vertically
        # outboard of the head side wall up to the cheek/boss line.
        yoke.visual(
            _tube(
                [
                    (0.0, sign * 0.018, z_low),
                    (0.0, y, z_low),
                    (0.0, y, tilt_z_in_yoke - 0.006),
                    (0.0, y, tilt_z_in_yoke + 0.018),
                ],
                0.008,
                f"fork_arm_{tag}",
                segments=18,
            ),
            material=mats["frame"],
            name=f"fork_arm_{tag}", material_class_id="metal.paint_coated",
        )
        yoke.visual(
            Box((0.046, 0.014, 0.040)),
            origin=Origin(xyz=(0.0, y, tilt_z_in_yoke)),
            material=mats["frame"],
            name=f"pivot_cheek_{tag}", material_class_id="metal.paint_coated",
        )
        yoke.visual(
            Cylinder(radius=0.015, length=0.010),
            origin=Origin(
                xyz=(0.0, sign * (fork_half + 0.010), tilt_z_in_yoke), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["housing"],
            name=f"pivot_knob_{tag}", material_class_id="plastic.opaque_glossy_molded",
        )
    yoke.visual(
        Cylinder(radius=0.006, length=2.0 * fork_half + 0.028),
        origin=Origin(xyz=(0.0, 0.0, tilt_z_in_yoke), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="pivot_axle", material_class_id="metal.stainless_matte",
    )
    head = _build_head(model, r, mats, boss_y=r.head_w / 2.0 + 0.012, boss_len=0.032, assets=assets)
    model.articulation(
        "stand_to_yoke",
        ArticulationType.REVOLUTE,
        parent=stand,
        child=yoke,
        origin=Origin(xyz=(0.0, 0.0, pan_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-math.pi, upper=math.pi),
    )
    model.articulation(
        "yoke_to_head",
        ArticulationType.REVOLUTE,
        parent=yoke,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, tilt_z_in_yoke)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=-r.tilt_range, upper=r.tilt_range
        ),
    )


def _build_telescope_tilt(model, stand, r, mats, column_base_z, *, assets) -> None:
    pivot_z = r.pivot_z
    rise = pivot_z - column_base_z
    # Keep the sleeve short so the taller mast section gives the behind-head yoke
    # arms room to route above the sleeve mouth (rise >= 0.090 guarantees this).
    sleeve_h = column_base_z + 0.35 * rise
    pivot_local_z = pivot_z - sleeve_h
    upright_top_y = r.head_w / 2.0 + 0.018
    # Fixed central outer sleeve (telescoping guide) + clamp on the stand.
    stand.visual(
        _open_tube(0.020, 0.0115, sleeve_h - column_base_z, "outer_sleeve", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, column_base_z)),
        material=mats["frame"],
        name="outer_sleeve", material_class_id="metal.paint_coated",
    )
    stand.visual(
        _open_tube(0.024, 0.0115, 0.014, "mast_clamp", assets=assets),
        origin=Origin(xyz=(0.0, 0.0, sleeve_h - 0.020)),
        material=mats["housing"],
        name="mast_clamp", material_class_id="plastic.opaque_glossy_molded",
    )
    stand.visual(
        Cylinder(radius=0.007, length=0.030),
        origin=Origin(xyz=(0.030, 0.0, sleeve_h - 0.013), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["rubber"],
        name="clamp_knob", material_class_id="rubber.smooth_plain",
    )
    # Telescoping inner mast: a central sliding pole + a top yoke that captures
    # the head boss. Frame origin at the sleeve mouth (the prismatic datum). The
    # pole bottom sits just inside the pedestal (above the mount node + ground).
    mast = model.part("inner_mast")
    mast_bottom_z = (column_base_z + 0.014) - sleeve_h
    mast.visual(
        Cylinder(radius=0.011, length=pivot_local_z - mast_bottom_z),
        origin=Origin(xyz=(0.0, 0.0, (pivot_local_z + mast_bottom_z) / 2.0)),
        material=mats["frame"],
        name="mast_pole", material_class_id="metal.paint_coated",
    )
    # Run each yoke arm out behind the head (head-local z = -0.044, below the
    # rear wall) to the outboard line, then up to the boss/cheek line.
    arm_low = pivot_local_z - 0.044
    for sign, tag in ((1.0, "pos_y"), (-1.0, "neg_y")):
        y = sign * upright_top_y
        mast.visual(
            _tube(
                [
                    (0.0, sign * 0.010, arm_low),
                    (0.0, y, arm_low),
                    (0.0, y, pivot_local_z - 0.006),
                    (0.0, y, pivot_local_z),
                ],
                0.008,
                f"yoke_arm_{tag}",
                segments=18,
            ),
            material=mats["frame"],
            name=f"yoke_arm_{tag}", material_class_id="metal.paint_coated",
        )
        mast.visual(
            Cylinder(radius=0.013, length=0.010),
            origin=Origin(
                xyz=(0.0, sign * (upright_top_y + 0.006), pivot_local_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["housing"],
            name=f"pivot_knob_{tag}", material_class_id="plastic.opaque_glossy_molded",
        )
    mast.visual(
        Cylinder(radius=0.006, length=2.0 * upright_top_y + 0.020),
        origin=Origin(xyz=(0.0, 0.0, pivot_local_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="pivot_axle", material_class_id="metal.stainless_matte",
    )
    head = _build_head(model, r, mats, boss_y=r.head_w / 2.0 + 0.004, boss_len=0.046, assets=assets)
    model.articulation(
        "stand_to_mast",
        ArticulationType.PRISMATIC,
        parent=stand,
        child=mast,
        origin=Origin(xyz=(0.0, 0.0, sleeve_h)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.25, lower=0.0, upper=r.mast_travel),
    )
    model.articulation(
        "mast_to_head",
        ArticulationType.REVOLUTE,
        parent=mast,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, pivot_local_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=-r.tilt_range, upper=r.tilt_range
        ),
    )


_HEAD_BUILDERS = {
    "side_tilt": _build_side_tilt,
    "tilt_pan_yoke": _build_tilt_pan_yoke,
    "telescope_tilt": _build_telescope_tilt,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_led_work_light(
    config: LedWorkLightConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"lwl_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    stand = model.part("stand_frame")
    column_base_z = _MOUNT_BUILDERS[r.mount_style](model, stand, r, mats, assets=assets)
    _emit_support_pedestal(stand, r, mats, column_base_z)
    _HEAD_BUILDERS[r.head_style](model, stand, r, mats, column_base_z, assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_led_work_light(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_led_work_light(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _side_wall_elems(panel_style: str) -> tuple[str, ...]:
    """Head side-face visuals a Y through-axle passes through (panel-dependent)."""
    if panel_style == "rect_flood":
        return ("housing_wall_left", "housing_wall_right")
    if panel_style == "cob_round_disc":
        return ("round_housing_shell",)
    return (  # dual_flood_bar
        "housing_wall_outer_0",
        "housing_wall_outer_1",
        "housing_wall_inner_0",
        "housing_wall_inner_1",
        "shared_crossbar",
    )


def _back_face_elem(panel_style: str) -> str:
    """Head rear-face visual the central mast pole enters from behind."""
    return "round_housing_shell" if panel_style == "cob_round_disc" else "housing_back"


def run_led_work_light_tests(
    object_model: ArticulatedObject,
    config: LedWorkLightConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    stand = object_model.get_part("stand_frame")
    head = object_model.get_part("light_head")

    ctx.allow_isolated_part(
        head,
        reason="light head tilts/extends clear of the stand and loses contact",
    )
    if "inner_mast" in {p.name for p in object_model.parts}:
        ctx.allow_isolated_part(
            object_model.get_part("inner_mast"),
            reason="inner mast rises out of the stand tube and loses contact",
        )

    # ---- Mount-local captured-pin allowances. ----
    if r.mount_style == "folding_aframe":
        for i in range(2):
            leg = object_model.get_part(f"folding_leg_{i}")
            ctx.allow_overlap(
                stand,
                leg,
                elem_a=f"leg_pin_{i}",
                elem_b="hinge_barrel",
                reason="The folding leg barrel is captured around the visible apex hinge pin.",
            )
    elif r.mount_style == "handheld_hook":
        hook = object_model.get_part("hanging_hook")
        for i in range(2):
            ctx.allow_overlap(
                hook,
                stand,
                elem_a="hook_hinge_barrel",
                elem_b=f"hook_lug_{i}",
                reason="The fold-out hook hinge barrel is captured in the molded rear lug.",
            )

    # ---- Head-chain pivot capture allowances. ----
    # Light head sweeps close past the stand clamp knob at the tilt extreme
    # (mast-mounted head on any mount style).
    if any(v.name == "clamp_knob" for v in stand.visuals):
        ctx.allow_overlap(
            head,
            stand,
            elem_a="housing_back",
            elem_b="clamp_knob",
            reason="Light head housing sweeps close past the stand clamp knob at the tilt extreme.",
        )
    if r.head_style == "side_tilt":
        for tag in ("pos_y", "neg_y"):
            ctx.allow_overlap(
                head,
                stand,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"upright_{tag}",
                reason="Pivot boss is captured inside the upright top to form the tilt bearing.",
            )
            ctx.allow_overlap(
                head,
                stand,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"pivot_knob_{tag}",
                reason="Pivot bolt head seats into the boss face.",
            )
            ctx.allow_overlap(
                head,
                stand,
                elem_a=f"pivot_boss_{tag}",
                elem_b="pivot_axle",
                reason="Pivot axle passes through the pivot boss bore.",
            )
        ctx.allow_overlap(
            head,
            stand,
            elem_a="pivot_shaft",
            elem_b="pivot_axle",
            reason="The stand pivot axle is sleeved through the head tilt shaft.",
        )
        for wall in _side_wall_elems(r.panel_style):
            ctx.allow_overlap(
                stand,
                head,
                elem_a="pivot_axle",
                elem_b=wall,
                reason="The through-axle passes the molded head side wall at the pivot bore.",
            )
    elif r.head_style == "tilt_pan_yoke":
        yoke = object_model.get_part("u_yoke")
        for tag in ("pos_y", "neg_y"):
            ctx.allow_overlap(
                head,
                yoke,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"pivot_cheek_{tag}",
                reason="Pivot boss passes through the yoke cheek (tilt bearing).",
            )
            ctx.allow_overlap(
                head,
                yoke,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"fork_arm_{tag}",
                reason="Pivot boss is captured alongside the yoke fork arm (tilt bearing).",
            )
            ctx.allow_overlap(
                head,
                yoke,
                elem_a=f"pivot_boss_{tag}",
                elem_b="pivot_axle",
                reason="Pivot axle passes through the pivot boss bore.",
            )
            ctx.allow_overlap(
                head,
                yoke,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"pivot_knob_{tag}",
                reason="Pivot bolt head seats into the boss face.",
            )
        ctx.allow_overlap(
            head,
            yoke,
            elem_a="pivot_shaft",
            elem_b="pivot_axle",
            reason="The yoke pivot axle is sleeved through the head tilt shaft.",
        )
        for wall in _side_wall_elems(r.panel_style):
            ctx.allow_overlap(
                yoke,
                head,
                elem_a="pivot_axle",
                elem_b=wall,
                reason="The through-axle passes the molded head side wall at the pivot bore.",
            )
    else:  # telescope_tilt
        mast = object_model.get_part("inner_mast")
        for tag in ("pos_y", "neg_y"):
            ctx.allow_overlap(
                head,
                mast,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"yoke_arm_{tag}",
                reason="Pivot boss captured by the mast yoke arm (tilt bearing).",
            )
            ctx.allow_overlap(
                head,
                mast,
                elem_a="pivot_shaft",
                elem_b=f"yoke_arm_{tag}",
                reason="The head tilt shaft is cradled by the mast yoke arm.",
            )
            ctx.allow_overlap(
                head,
                mast,
                elem_a=f"pivot_boss_{tag}",
                elem_b="pivot_axle",
                reason="Pivot axle passes through the pivot boss bore.",
            )
            ctx.allow_overlap(
                head,
                mast,
                elem_a=f"pivot_boss_{tag}",
                elem_b=f"pivot_knob_{tag}",
                reason="Pivot bolt head seats into the boss face.",
            )
        ctx.allow_overlap(
            mast,
            stand,
            elem_a="mast_pole",
            elem_b="outer_sleeve",
            reason="The inner mast pole slides inside the fixed outer sleeve.",
        )
        ctx.allow_overlap(
            mast,
            stand,
            elem_a="mast_pole",
            elem_b="mast_clamp",
            reason="The inner mast pole passes through the clamp collar.",
        )
        ctx.allow_overlap(
            mast,
            stand,
            elem_a="mast_pole",
            elem_b="support_pedestal",
            reason="The inner mast pole seats into the support pedestal at rest.",
        )
        ctx.allow_overlap(
            mast,
            head,
            elem_a="mast_pole",
            elem_b=_back_face_elem(r.panel_style),
            reason="The central mast pole enters the head from behind to reach the pivot.",
        )
        ctx.allow_overlap(
            head,
            mast,
            elem_a="pivot_shaft",
            elem_b="mast_pole",
            reason="The head tilt shaft meets the mast pole at the pivot center.",
        )
        ctx.allow_overlap(
            head,
            mast,
            elem_a="pivot_shaft",
            elem_b="pivot_axle",
            reason="The mast pivot axle is sleeved through the head tilt shaft.",
        )
        for wall in _side_wall_elems(r.panel_style):
            ctx.allow_overlap(
                mast,
                head,
                elem_a="pivot_axle",
                elem_b=wall,
                reason="The through-axle passes the molded head side wall at the pivot bore.",
            )

    # ---- Baseline structural / connectivity gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / topology checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("stand_frame present", "stand_frame" in part_names)
    ctx.check("light_head present", "light_head" in part_names)

    tilt_joint_name = {
        "side_tilt": "stand_to_head",
        "tilt_pan_yoke": "yoke_to_head",
        "telescope_tilt": "mast_to_head",
    }[r.head_style]
    tilt = object_model.get_articulation(tilt_joint_name)
    ax = tuple(round(a, 6) for a in tilt.axis)
    ctx.check(
        "head tilt is REVOLUTE about Y",
        tilt.articulation_type == ArticulationType.REVOLUTE
        and abs(ax[1]) == 1.0
        and ax[0] == 0.0
        and ax[2] == 0.0,
        details=f"type={tilt.articulation_type} axis={ax}",
    )

    if r.head_style == "tilt_pan_yoke":
        pan = object_model.get_articulation("stand_to_yoke")
        pax = tuple(round(a, 6) for a in pan.axis)
        ctx.check(
            "pan joint is REVOLUTE about Z",
            pan.articulation_type == ArticulationType.REVOLUTE and pax == (0.0, 0.0, 1.0),
            details=f"axis={pax}",
        )
        head_visuals = {v.name for v in head.visuals}
        ctx.check(
            "tilt_pan removes the rear battery",
            "battery_pack" not in head_visuals and "battery_port_panel" not in head_visuals,
            details=str(sorted(head_visuals)[:6]),
        )
    elif r.head_style == "telescope_tilt":
        lift = object_model.get_articulation("stand_to_mast")
        lax = tuple(round(a, 6) for a in lift.axis)
        ctx.check(
            "lift joint is PRISMATIC about Z",
            lift.articulation_type == ArticulationType.PRISMATIC and lax == (0.0, 0.0, 1.0),
            details=f"axis={lax}",
        )

    # Panel-specific LED population.
    head_visuals = {v.name for v in head.visuals}

    def _led_parts(name: str) -> list[str] | None:
        parts = name.split("_")
        if parts[0] != "led" or len(parts) < 2 or not all(p.isdigit() for p in parts[1:]):
            return None
        return parts

    if r.panel_style == "rect_flood":
        expected = r.led_rows * r.led_cols
        got = sum(1 for n in head_visuals if (_led_parts(n) or []) and len(_led_parts(n)) == 3)
        ctx.check(
            "rect LED grid count matches led_count",
            got == expected,
            details=f"got={got} expected={expected}",
        )
        ctx.check("led_glass_panel present", "led_glass_panel" in head_visuals)
    elif r.panel_style == "cob_round_disc":
        got = sum(1 for n in head_visuals if (_led_parts(n) or []) and len(_led_parts(n)) == 2)
        ctx.check(
            "cob concentric LED count matches rings",
            got == sum(LED_RING_COUNTS),
            details=f"got={got}",
        )
        ctx.check("round_glass_panel present", "round_glass_panel" in head_visuals)
    else:  # dual_flood_bar
        ctx.check(
            "two dual glass panels present",
            "led_glass_panel_0" in head_visuals and "led_glass_panel_1" in head_visuals,
        )
        ctx.check("shared crossbar present", "shared_crossbar" in head_visuals)

    # ---- Tilt actually raises the LED face. ----
    glass_elem = {
        "rect_flood": "led_glass_panel",
        "cob_round_disc": "round_glass_panel",
        "dual_flood_bar": "led_glass_panel_0",
    }[r.panel_style]
    rest = ctx.part_element_world_aabb(head, elem=glass_elem)
    with ctx.pose({tilt: r.tilt_range * 0.8}):
        up = ctx.part_element_world_aabb(head, elem=glass_elem)
    if rest is not None and up is not None:
        ctx.check(
            "positive tilt raises the LED face",
            up[1][2] > rest[1][2] + 0.005,
            details=f"rest_top={rest[1][2]:.4f} up_top={up[1][2]:.4f}",
        )

    # ---- The assembly sits near the ground (lowest of any part). ----
    z_mins = [
        b[0][2] for b in (ctx.part_world_aabb(p) for p in object_model.parts) if b is not None
    ]
    if z_mins:
        ctx.check(
            "assembly rests near the ground", min(z_mins) < 0.03, details=f"z_min={min(z_mins):.4f}"
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "LedWorkLightConfig",
    "ResolvedLedWorkLightConfig",
    "build_led_work_light",
    "build_seeded_led_work_light",
    "config_from_seed",
    "resolve_config",
    "run_led_work_light_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
