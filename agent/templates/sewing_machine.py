# SPDX-License-Identifier: Apache-2.0

"""Sewing machine — modular procedural template.

Mixed topology: a grounded ``machine_form`` (base + C-head) carries a rotary
``drive_mechanism`` (balance handwheel + optional treadle / hand crank / motor)
and ``head_controls`` (needle bar is core; optional dials / take-up lever). Two
skeleton families gate legal combinations:

* molded family (compact_bench / free_arm) — plastic C-body, side handwheel,
  domestic dial controls; drives ∈ {electric_handwheel, hand_crank}.
* cast family (treadle_table / industrial_table) — cast-iron head on a
  cabinet/stand or steel power table, sparse controls; drives ∈ {foot_treadle,
  underslung_motor}.

Slots (recorded in ``model.meta["slot_choices"]``):

* Slot A ``machine_form``     — compact_bench / free_arm / treadle_table / industrial_table
* Slot B ``drive_mechanism``  — electric_handwheel / hand_crank / foot_treadle / underslung_motor
* Slot C ``head_controls``    — domestic_full / domestic_takeup / bare_mechanical
* multiplicity ``drawer_count`` — cabinet drawers on treadle_table (N∈[2,6])

Every module factory adapts a real 5-star source record (parent A treadle,
parent B compact, and the six verified fork variants). ``config_from_seed`` is
deterministic procedural sampling for every seed including seed 0.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from agent.templates._modular import mount_fixed
from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    CapsuleGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobRelief,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    TorusGeometry,
    WheelBore,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------- slots
MachineForm = Literal["compact_bench", "free_arm", "treadle_table", "industrial_table"]
DriveMechanism = Literal["electric_handwheel", "hand_crank", "foot_treadle", "underslung_motor"]
HeadControls = Literal["domestic_full", "domestic_takeup", "bare_mechanical"]
PaletteTheme = Literal["white", "mint", "cream", "cast", "industrial"]

FORM_MODULES: tuple[MachineForm, ...] = (
    "compact_bench",
    "free_arm",
    "treadle_table",
    "industrial_table",
)
MOLDED_FORMS = ("compact_bench", "free_arm")
CAST_FORMS = ("treadle_table", "industrial_table")
MOLDED_DRIVES = ("electric_handwheel", "hand_crank")
MOLDED_CONTROLS = ("domestic_full", "domestic_takeup")


# ----------------------------------------------------------------- materials
BASE_MATERIALS: dict[str, tuple[float, float, float, float]] = {
    # molded family
    "body_white": (0.955, 0.955, 0.945, 1.0),
    "trim_white": (0.92, 0.92, 0.91, 1.0),
    "paisley_blue": (0.72, 0.80, 0.92, 1.0),
    "steel_silver": (0.72, 0.73, 0.75, 1.0),
    "chrome": (0.83, 0.85, 0.88, 1.0),
    "dark_gray": (0.20, 0.20, 0.22, 1.0),
    "light_gray": (0.82, 0.82, 0.84, 1.0),
    "rubber_gray": (0.35, 0.35, 0.36, 1.0),
    "tray_white": (0.94, 0.94, 0.93, 1.0),
    # cast family
    "cast_iron_black": (0.10, 0.10, 0.11, 1.0),
    "head_black_japanned": (0.05, 0.05, 0.06, 1.0),
    "oak_wood": (0.45, 0.28, 0.14, 1.0),
    "dark_stained_wood": (0.30, 0.17, 0.09, 1.0),
    "nickel_plate": (0.75, 0.76, 0.78, 1.0),
    "gold_decal": (0.80, 0.62, 0.20, 1.0),
    # industrial family
    "steel_frame": (0.28, 0.28, 0.30, 1.0),
    "laminate_white": (0.82, 0.82, 0.80, 1.0),
    "motor_enamel": (0.30, 0.40, 0.32, 1.0),
    "belt_rubber": (0.10, 0.10, 0.10, 1.0),
    "foot_pad": (0.15, 0.15, 0.15, 1.0),
}

# molded palette themes override the plastic body + accent panel colours only.
MOLDED_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "white": {},
    "mint": {
        "body_white": (0.88, 0.95, 0.90, 1.0),
        "trim_white": (0.84, 0.92, 0.87, 1.0),
        "paisley_blue": (0.55, 0.78, 0.68, 1.0),
    },
    "cream": {
        "body_white": (0.96, 0.93, 0.84, 1.0),
        "trim_white": (0.93, 0.90, 0.80, 1.0),
        "paisley_blue": (0.85, 0.72, 0.55, 1.0),
    },
}


# ---------------------------------------------------------------- dimensions
# Molded family (parent B / free-arm fork).
M_BED_TOP = 0.062
M_HEAD_BOTTOM = 0.115
M_PLATE_TOP = 0.0645
M_NEEDLE_X = -0.145
M_NEEDLE_Y = -0.018
M_PRESSER_Y = 0.004
# Free-arm sub-dims.
FA_ARM_LENGTH = 0.300
FA_ARM_WIDTH = 0.080
FA_ARM_HEIGHT = 0.052
FA_ARM_CENTER_X = -0.040
FA_ARM_CENTER_Z = M_BED_TOP - FA_ARM_HEIGHT / 2.0
FA_TRAY_LENGTH = 0.190
FA_TRAY_WIDTH = 0.155
FA_TRAY_THICKNESS = 0.006
# Tray right edge kept clear of the C-body pillar left face (x=0.100): tray
# spans center ± FA_TRAY_LENGTH/2, so center=-0.006 → x_max=0.089 (~11mm gap).
FA_TRAY_CENTER_X = -0.006
FA_TRAY_CENTER_Z = M_BED_TOP + FA_TRAY_THICKNESS / 2.0

# Treadle family (parent A).
A_TOP_Z0, A_TOP_Z1 = 0.725, 0.760
A_TOP_SIZE = (0.92, 0.46, 0.035)
A_CAB_XC = 0.38
A_CAB_Z0, A_CAB_Z1 = 0.527, 0.727
A_ARM_Z = 0.972
A_WHEEL_C = (0.245, 0.02, 0.38)
A_HANDWHEEL_X = 0.2475
A_PIVOT = (0.0, 0.04, 0.11)
A_NEEDLE_X, A_NEEDLE_JOINT_Z = -0.085, 0.86
A_NEEDLE_TRAVEL = 0.011
DRAWER_TRAVEL = 0.20

# Industrial family (K-leg power table fork).
I_TABLE_TOP_Z = 0.790
I_TABLE_THICK = 0.038
I_TABLE_W = 1.08
I_TABLE_D = 0.55
I_BED_XC = 0.05
I_BED_SIZE = (0.40, 0.19, I_TABLE_THICK)
I_ARM_Z = 0.972
I_HANDWHEEL_X = 0.250
I_NEEDLE_X = -0.085
I_NEEDLE_JOINT_Z = 0.867
I_NEEDLE_TRAVEL = 0.011
I_STITCH_PLATE_Z = 0.791
I_LEG_TUBE = 0.040
I_FRAME_HY = 0.22
I_MOTOR_CX = 0.30
I_MOTOR_CY = 0.06
I_MOTOR_CZ = 0.60
I_MOTOR_SIZE = (0.20, 0.14, 0.14)
I_PULLEY_CZ = 0.52
I_PULLEY_R = 0.030
I_PULLEY_W = 0.022


@dataclass(frozen=True)
class SewingMachineConfig:
    machine_form: MachineForm | None = None
    drive_mechanism: DriveMechanism | None = None
    head_controls: HeadControls | None = None
    palette_theme: PaletteTheme = "white"
    drawer_count: int = 0
    molded_bed_depth_scale: float = 1.0
    industrial_table_width_scale: float = 1.0
    needle_travel_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedSewingMachineConfig:
    machine_form: MachineForm
    drive_mechanism: DriveMechanism
    head_controls: HeadControls
    palette_theme: PaletteTheme
    drawer_count: int
    molded_bed_depth_scale: float
    industrial_table_width_scale: float
    needle_travel_scale: float
    # derived
    family: str  # "molded" | "cast"
    drawers: tuple[tuple[str, float, float, float], ...]  # (name, xc, z_base, drawer_h)
    materials: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _weighted_drawer_count(rng: random.Random) -> int:
    # Product domain [2,6]; small N frequent, N=6 rare (source N samples 2,3,6).
    roll = rng.random()
    if roll < 0.35:
        return 2
    if roll < 0.68:
        return 3
    if roll < 0.84:
        return 4
    if roll < 0.94:
        return 5
    return 6


def config_from_seed(seed: int) -> SewingMachineConfig:
    """Deterministic procedural sampling for every seed (seed 0 not special)."""
    rng = random.Random(seed)
    form: MachineForm = rng.choice(FORM_MODULES)  # type: ignore[assignment]
    if form in MOLDED_FORMS:
        drive: DriveMechanism = rng.choice(MOLDED_DRIVES)  # type: ignore[assignment]
        controls: HeadControls = rng.choice(MOLDED_CONTROLS)  # type: ignore[assignment]
        palette: PaletteTheme = rng.choice(("white", "mint", "cream"))  # type: ignore[assignment]
        drawer_count = 0
    elif form == "treadle_table":
        drive = "foot_treadle"
        controls = "bare_mechanical"
        palette = "cast"
        drawer_count = _weighted_drawer_count(rng)
    else:  # industrial_table
        drive = "underslung_motor"
        controls = "bare_mechanical"
        palette = "industrial"
        drawer_count = 0
    return SewingMachineConfig(
        machine_form=form,
        drive_mechanism=drive,
        head_controls=controls,
        palette_theme=palette,
        drawer_count=drawer_count,
        molded_bed_depth_scale=round(rng.uniform(0.92, 1.12), 4),
        industrial_table_width_scale=round(rng.uniform(0.95, 1.10), 4),
        needle_travel_scale=round(rng.uniform(0.85, 1.18), 4),
    )


def _resolve_drawers(count: int) -> tuple[tuple[str, float, float, float], ...]:
    if count <= 0:
        return ()
    interior_bottom = A_CAB_Z0 + 0.012
    interior_top = A_CAB_Z1 - 0.012
    interior_h = interior_top - interior_bottom
    per_col = math.ceil(count / 2.0)
    slot_h = interior_h / per_col
    drawer_h = _clamp(min(0.082, slot_h - 0.008), 0.030, 0.082)
    left_count = math.ceil(count / 2.0)
    right_count = count - left_count
    drawers: list[tuple[str, float, float, float]] = []
    for xc, col_count in ((-A_CAB_XC, left_count), (A_CAB_XC, right_count)):
        for j in range(col_count):
            z_base = interior_bottom + j * slot_h + (slot_h - drawer_h) * 0.5
            drawers.append((f"drawer_{len(drawers)}", xc, z_base, drawer_h))
    return tuple(drawers)


def resolve_config(config: SewingMachineConfig) -> ResolvedSewingMachineConfig:
    form = config.machine_form or "compact_bench"
    if form not in FORM_MODULES:
        raise ValueError(f"Unsupported machine_form: {form!r}")
    family = "molded" if form in MOLDED_FORMS else "cast"

    drive = config.drive_mechanism
    controls = config.head_controls
    palette = config.palette_theme
    if family == "molded":
        drive = drive or "electric_handwheel"
        controls = controls or "domestic_full"
        if drive not in MOLDED_DRIVES:
            raise ValueError(f"drive {drive!r} illegal for molded form {form!r}")
        if controls not in MOLDED_CONTROLS:
            raise ValueError(f"controls {controls!r} illegal for molded form {form!r}")
        if palette not in ("white", "mint", "cream"):
            palette = "white"
    else:
        drive = "foot_treadle" if form == "treadle_table" else "underslung_motor"
        controls = "bare_mechanical"
        palette = "cast" if form == "treadle_table" else "industrial"

    drawer_count = int(config.drawer_count) if form == "treadle_table" else 0
    if form == "treadle_table":
        drawer_count = max(2, min(6, drawer_count or 3))
    drawers = _resolve_drawers(drawer_count)

    materials = dict(BASE_MATERIALS)
    if family == "molded":
        for name, rgba in MOLDED_PALETTES.get(palette, {}).items():
            materials[name] = rgba

    return ResolvedSewingMachineConfig(
        machine_form=form,
        drive_mechanism=drive,  # type: ignore[arg-type]
        head_controls=controls,  # type: ignore[arg-type]
        palette_theme=palette,  # type: ignore[arg-type]
        drawer_count=drawer_count,
        molded_bed_depth_scale=_clamp(config.molded_bed_depth_scale, 0.92, 1.12),
        industrial_table_width_scale=_clamp(config.industrial_table_width_scale, 0.95, 1.10),
        needle_travel_scale=_clamp(config.needle_travel_scale, 0.85, 1.18),
        family=family,
        drawers=drawers,
        materials=materials,
    )


# ============================================================ cadquery shapes
def _filleted(shape: cq.Workplane, selector: str, radii: tuple[float, ...]) -> cq.Workplane:
    for radius in radii:
        try:
            return shape.edges(selector).fillet(radius)
        except Exception:  # noqa: BLE001 - fillet is best-effort cosmetic
            continue
    return shape


def _flat_bed_shape(depth: float) -> cq.Workplane:
    bed = cq.Workplane("XY").box(0.400, depth, 0.052)
    bed = _filleted(bed, "|Z", (0.012, 0.008))
    bed = _filleted(bed, ">Z", (0.004, 0.002))
    return bed.translate((0.0, 0.0, 0.036))


def _free_arm_shape(width: float) -> cq.Workplane:
    arm = cq.Workplane("XY").box(FA_ARM_LENGTH, width, FA_ARM_HEIGHT)
    arm = _filleted(arm, "|Z", (0.025, 0.022, 0.018))
    arm = _filleted(arm, ">Z", (0.008, 0.006, 0.004))
    arm = _filleted(arm, "<Z", (0.008, 0.006, 0.004))
    return arm.translate((FA_ARM_CENTER_X, 0.0, FA_ARM_CENTER_Z))


def _molded_body_shape() -> cq.Workplane:
    # Pillar extends down to z=0.056 so the fused C-body penetrates the bed top
    # (~0.062) — the two are one grounded chassis part and must share geometry.
    pillar = cq.Workplane("XY").box(0.100, 0.150, 0.244).translate((0.150, 0.0, 0.178))
    arm = cq.Workplane("XY").box(0.330, 0.120, 0.088).translate((0.035, 0.0, 0.256))
    head = cq.Workplane("XY").box(0.105, 0.140, 0.185).translate((-0.1475, 0.0, 0.2075))
    body = pillar.union(arm).union(head)
    return _filleted(body, "|Y", (0.012, 0.008, 0.005))


def _art_panel_shape() -> cq.Workplane:
    panel = cq.Workplane("XZ").box(0.088, 0.205, 0.0015)
    dial_hole = cq.Workplane("XZ").center(-0.002, 0.030).circle(0.0305).extrude(0.02, both=True)
    lever_hole = cq.Workplane("XZ").center(-0.002, -0.045).rect(0.018, 0.040).extrude(0.02, both=True)
    return panel.cut(dial_hole).cut(lever_hole)


def _foot_sole_shape() -> cq.Workplane:
    sole = cq.Workplane("XY").box(0.016, 0.034, 0.0042)
    sole = _filleted(sole, "|Z", (0.004, 0.002))
    slot = cq.Workplane("XY").center(0.0, -0.008).rect(0.0045, 0.012).extrude(0.02, both=True)
    return sole.cut(slot)


def _paddle_shape() -> cq.Workplane:
    paddle = cq.Workplane("XY").box(0.020, 0.012, 0.034)
    return _filleted(paddle, "|Y", (0.004, 0.002))


def _tray_shape() -> cq.Workplane:
    plate = cq.Workplane("XY").box(FA_TRAY_LENGTH, FA_TRAY_WIDTH, FA_TRAY_THICKNESS)
    plate = _filleted(plate, "|Z", (0.008, 0.006))
    plate = _filleted(plate, ">Z", (0.002, 0.001))
    plate = _filleted(plate, "<Z", (0.002, 0.001))
    lip = (
        cq.Workplane("XY")
        .box(0.055, 0.008, 0.005)
        .translate((0.0, -(FA_TRAY_WIDTH / 2.0 - 0.004), FA_TRAY_THICKNESS / 2.0 + 0.0025))
    )
    lip = _filleted(lip, "|Z", (0.003, 0.002))
    return plate.union(lip)


def _takeup_lever_shape() -> cq.Workplane:
    hub = cq.Workplane("YZ").circle(0.005).extrude(0.004, both=True)
    arm = cq.Workplane("XZ").rect(0.004, 0.0025).extrude(0.034)
    eye_ring = (
        cq.Workplane("XZ").workplane(offset=0.034).circle(0.0048).circle(0.0018).extrude(0.0025)
    )
    return hub.union(arm).union(eye_ring)


def _shift(profile: list[tuple[float, float]], dx: float, dy: float) -> list[tuple[float, float]]:
    return [(x + dx, y + dy) for x, y in profile]


def _circle_pts(cx: float, cy: float, radius: float, n: int = 24) -> list[tuple[float, float]]:
    return [
        (cx + radius * math.cos(2.0 * math.pi * i / n), cy + radius * math.sin(2.0 * math.pi * i / n))
        for i in range(n)
    ]


# ============================================================ molded shared
def _build_molded_body(model: ArticulatedObject) -> Part:
    # The C-body is rigid structure fused into the single grounded ``chassis``
    # part (bed + pillar + arm + head), not a FIXED-jointed child: authoring it
    # in absolute coords under a FIXED joint would double its world offset.
    body = model.get_part("chassis")
    body.visual(
        mesh_from_cadquery(_molded_body_shape(), "body_shell"),
        material="body_white",
        name="body_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        mesh_from_cadquery(_art_panel_shape(), "front_art_panel"),
        origin=Origin(xyz=(0.152, -0.0752, 0.175)),
        material="paisley_blue",
        name="front_art_panel", material_class_id="plastic.patterned_textured",
    )
    body.visual(
        Box((0.006, 0.0014, 0.100)),
        origin=Origin(xyz=(-0.170, -0.0702, 0.235)),
        material="dark_gray",
        name="takeup_slot", material_class_id="plastic.opaque_generic",
    )
    body.visual(
        Cylinder(radius=0.0035, length=0.040),
        origin=Origin(xyz=(0.155, 0.010, 0.316)),
        material="trim_white",
        name="spool_pin", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Cylinder(radius=0.0025, length=0.026),
        origin=Origin(xyz=(0.105, 0.010, 0.309)),
        material="chrome",
        name="bobbin_winder_spindle", material_class_id="metal.chrome_polished",
    )
    body.visual(
        Cylinder(radius=0.0045, length=0.010),
        origin=Origin(xyz=(0.128, 0.010, 0.301)),
        material="trim_white",
        name="winder_stopper", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((0.016, 0.012, 0.010)),
        origin=Origin(xyz=(-0.085, 0.0, 0.303)),
        material="light_gray",
        name="thread_guide", material_class_id="plastic.opaque_glossy_molded",
    )
    return body


def _build_molded_needle_and_presser(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    body = model.get_part("chassis")
    needle_bar = model.part("needle_bar")
    needle_bar.visual(
        Cylinder(radius=0.0038, length=0.060),
        origin=Origin(xyz=(0.0, 0.0, 0.015)),
        material="chrome",
        name="needle_bar_shaft", material_class_id="metal.chrome_polished",
    )
    needle_bar.visual(
        Box((0.011, 0.011, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, -0.020)),
        material="steel_silver",
        name="needle_clamp", material_class_id="metal.stainless_matte",
    )
    needle_bar.visual(
        Cylinder(radius=0.0007, length=0.020),
        origin=Origin(xyz=(0.0, 0.0, -0.035)),
        material="chrome",
        name="needle", material_class_id="metal.chrome_polished",
    )
    s = r.needle_travel_scale
    model.articulation(
        "needle_stroke",
        ArticulationType.PRISMATIC,
        parent=body,
        child=needle_bar,
        origin=Origin(xyz=(M_NEEDLE_X, M_NEEDLE_Y, M_HEAD_BOTTOM)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.5, lower=-0.0045 * s, upper=0.010 * s),
    )

    presser_foot = model.part("presser_foot")
    presser_foot.visual(
        Cylinder(radius=0.0032, length=0.070),
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
        material="chrome",
        name="presser_bar_shaft", material_class_id="metal.chrome_polished",
    )
    presser_foot.visual(
        Box((0.008, 0.010, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, -0.038)),
        material="steel_silver",
        name="foot_shank", material_class_id="metal.stainless_matte",
    )
    presser_foot.visual(
        mesh_from_cadquery(_foot_sole_shape(), "foot_sole"),
        origin=Origin(xyz=(0.0, -0.014, -0.0479)),
        material="steel_silver",
        name="foot_sole", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "presser_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=presser_foot,
        origin=Origin(xyz=(M_NEEDLE_X, M_PRESSER_Y, M_HEAD_BOTTOM)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.2, lower=0.0, upper=0.007),
    )


# ============================================================ Slot A forms
def _build_compact_bench(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    depth = 0.170 * r.molded_bed_depth_scale
    bed = model.part("chassis")
    bed.visual(mesh_from_cadquery(_flat_bed_shape(depth), "bed_shell"), material="body_white", name="bed_shell", material_class_id="plastic.opaque_glossy_molded")
    fy = 0.060 * r.molded_bed_depth_scale
    for i, (px, py) in enumerate(((-0.175, -fy), (0.175, -fy), (-0.175, fy), (0.175, fy))):
        bed.visual(
            Cylinder(radius=0.011, length=0.012),
            origin=Origin(xyz=(px, py, 0.006)),
            material="rubber_gray",
            name=f"foot_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    bed.visual(
        Box((0.095, 0.060, 0.0025)),
        origin=Origin(xyz=(M_NEEDLE_X, -0.010, 0.06325)),
        material="steel_silver",
        name="needle_plate", material_class_id="metal.stainless_matte",
    )
    bed.visual(
        Box((0.028, 0.014, 0.0008)),
        origin=Origin(xyz=(M_NEEDLE_X, M_NEEDLE_Y, 0.0644)),
        material="dark_gray",
        name="feed_dog", material_class_id="metal.stainless_matte",
    )
    bed.visual(
        Box((0.070, 0.026, 0.0016)),
        origin=Origin(xyz=(-0.100, -0.058, 0.0626)),
        material="light_gray",
        name="bobbin_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    _build_molded_body(model)
    _build_molded_needle_and_presser(model, r)


def _build_free_arm(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    width = FA_ARM_WIDTH * r.molded_bed_depth_scale
    bed = model.part("chassis")
    bed.visual(mesh_from_cadquery(_free_arm_shape(width), "bed_shell"), material="body_white", name="bed_shell", material_class_id="plastic.opaque_glossy_molded")
    fy = 0.028 * r.molded_bed_depth_scale
    for i, (px, py) in enumerate(
        (
            (FA_ARM_CENTER_X + 0.120, -fy),
            (FA_ARM_CENTER_X + 0.120, fy),
            (FA_ARM_CENTER_X - 0.120, -fy),
            (FA_ARM_CENTER_X - 0.120, fy),
        )
    ):
        bed.visual(
            Cylinder(radius=0.011, length=0.012),
            origin=Origin(xyz=(px, py, 0.006)),
            material="rubber_gray",
            name=f"foot_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    bed.visual(
        Box((0.080, 0.058, 0.0025)),
        origin=Origin(xyz=(M_NEEDLE_X, -0.005, M_BED_TOP + 0.00125)),
        material="steel_silver",
        name="needle_plate", material_class_id="metal.stainless_matte",
    )
    bed.visual(
        Box((0.028, 0.014, 0.0008)),
        origin=Origin(xyz=(M_NEEDLE_X, M_NEEDLE_Y, M_PLATE_TOP - 0.0004 + 0.0008)),
        material="dark_gray",
        name="feed_dog", material_class_id="metal.stainless_matte",
    )
    bed.visual(
        Box((0.048, 0.002, 0.030)),
        origin=Origin(xyz=(M_NEEDLE_X, -(width / 2.0 + 0.001), FA_ARM_CENTER_Z)),
        material="light_gray",
        name="bobbin_cover", material_class_id="plastic.opaque_glossy_molded",
    )
    # Removable accessory tray that slides off the free arm toward the front.
    tray = model.part("accessory_tray")
    tray.visual(mesh_from_cadquery(_tray_shape(), "tray_plate"), material="tray_white", name="tray_plate", material_class_id="plastic.opaque_glossy_molded")
    model.articulation(
        "tray_slide",
        ArticulationType.PRISMATIC,
        parent=bed,
        child=tray,
        origin=Origin(xyz=(FA_TRAY_CENTER_X, 0.0, FA_TRAY_CENTER_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.3, lower=0.0, upper=0.160),
    )
    _build_molded_body(model)
    _build_molded_needle_and_presser(model, r)


def _build_cast_head(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> Part:
    """Cast-iron C-head (bed/pillar/arm/nose/faceplate/stitch plate) for treadle+industrial.

    The head is rigid structure fused into the single grounded ``chassis`` part
    (with the stand/table/frame), never a FIXED-jointed child — authoring it in
    absolute coords under a FIXED joint would double its world offset.
    """
    is_industrial = r.machine_form == "industrial_table"
    head = model.get_part("chassis")
    if is_industrial:
        head.visual(
            Box(I_BED_SIZE),
            origin=Origin(xyz=(I_BED_XC, 0.0, I_TABLE_TOP_Z - I_TABLE_THICK / 2.0)),
            material="head_black_japanned",
            name="bed", material_class_id="metal.paint_coated",
        )
        pillar_geom = ExtrudeGeometry.from_z0(rounded_rect_profile(0.080, 0.110, 0.02), 0.200)
        head.visual(
            mesh_from_geometry(pillar_geom, "pillar"),
            origin=Origin(xyz=(0.19, 0.0, I_TABLE_TOP_Z)),
            material="head_black_japanned",
            name="pillar", material_class_id="metal.paint_coated",
        )
        stitch_plate_z = I_STITCH_PLATE_Z
    else:
        head.visual(
            Box((0.36, 0.17, 0.024)),
            origin=Origin(xyz=(0.05, 0.0, 0.772)),
            material="head_black_japanned",
            name="bed", material_class_id="metal.paint_coated",
        )
        pillar_geom = ExtrudeGeometry.from_z0(rounded_rect_profile(0.075, 0.105, 0.02), 0.223)
        head.visual(
            mesh_from_geometry(pillar_geom, "pillar"),
            origin=Origin(xyz=(0.19, 0.0, 0.782)),
            material="head_black_japanned",
            name="pillar", material_class_id="metal.paint_coated",
        )
        stitch_plate_z = 0.785
    arm_geom = CapsuleGeometry(0.033 if not is_industrial else 0.034, 0.24).rotate_y(math.pi / 2.0)
    head.visual(
        mesh_from_geometry(arm_geom, "head_arm"),
        origin=Origin(xyz=(0.05, 0.0, A_ARM_Z)),
        material="head_black_japanned",
        name="arm", material_class_id="metal.paint_coated",
    )
    head.visual(
        Box((0.06, 0.062, 0.13)),
        origin=Origin(xyz=(A_NEEDLE_X, 0.0, 0.925)),
        material="head_black_japanned",
        name="nose", material_class_id="metal.paint_coated",
    )
    head.visual(
        Box((0.005, 0.05, 0.11)),
        origin=Origin(xyz=(-0.116, 0.0, 0.925)),
        material="nickel_plate",
        name="faceplate", material_class_id="metal.chrome_polished",
    )
    head.visual(
        Cylinder(radius=0.011, length=0.012),
        origin=Origin(xyz=(A_NEEDLE_X, -0.036, 0.94), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="nickel_plate",
        name="tension_knob", material_class_id="metal.chrome_polished",
    )
    plate_geom = ExtrudeWithHolesGeometry(
        rounded_rect_profile(0.07, 0.05, 0.008),
        [_circle_pts(-0.005, 0.0, 0.004)],
        0.003,
        center=True,
    )
    head.visual(
        mesh_from_geometry(plate_geom, "stitch_plate"),
        origin=Origin(xyz=(-0.08, 0.0, stitch_plate_z)),
        material="nickel_plate",
        name="stitch_plate", material_class_id="metal.chrome_polished",
    )
    head.visual(
        Box((0.04, 0.05, 0.0025)),
        origin=Origin(xyz=(-0.025, 0.0, stitch_plate_z)),
        material="nickel_plate",
        name="slide_plate", material_class_id="metal.chrome_polished",
    )
    head.visual(
        Cylinder(radius=0.003, length=0.05),
        origin=Origin(xyz=(0.14, 0.0, 1.025)),
        material="nickel_plate",
        name="spool_pin", material_class_id="metal.chrome_polished",
    )
    head.visual(
        Cylinder(radius=0.0032, length=0.08),
        origin=Origin(xyz=(-0.065, 0.012, 0.836)),
        material="nickel_plate",
        name="presser_bar", material_class_id="metal.chrome_polished",
    )
    head.visual(
        Box((0.028, 0.018, 0.004)),
        origin=Origin(xyz=(-0.065, 0.012, stitch_plate_z + (0.002 if is_industrial else 0.0))),
        material="nickel_plate",
        name="presser_foot", material_class_id="metal.chrome_polished",
    )
    if not is_industrial:
        head.visual(
            Box((0.14, 0.003, 0.028)),
            origin=Origin(xyz=(0.04, -0.0325, A_ARM_Z)),
            material="gold_decal",
            name="arm_decal", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        head.visual(
            Box((0.10, 0.05, 0.002)),
            origin=Origin(xyz=(0.05, -0.05, 0.7845)),
            material="gold_decal",
            name="bed_decal", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
    return head


def _build_cast_needle_bar(
    model: ArticulatedObject, r: ResolvedSewingMachineConfig, head: Part, joint_z: float, travel: float
) -> None:
    needle_bar = model.part("needle_bar")
    needle_bar.visual(
        Cylinder(radius=0.0035, length=0.11),
        origin=Origin(xyz=(0.0, 0.0, 0.02)),
        material="nickel_plate",
        name="bar", material_class_id="metal.chrome_polished",
    )
    needle_bar.visual(
        Cylinder(radius=0.006, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, -0.040)),
        material="nickel_plate",
        name="clamp", material_class_id="metal.chrome_polished",
    )
    needle_bar.visual(
        Cylinder(radius=0.0012, length=0.022),
        origin=Origin(xyz=(0.0, 0.0, -0.0525)),
        material="nickel_plate",
        name="needle", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "head_to_needle_bar",
        ArticulationType.PRISMATIC,
        parent=head,
        child=needle_bar,
        origin=Origin(xyz=(A_NEEDLE_X, 0.0, joint_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.5, lower=0.0, upper=travel * r.needle_travel_scale),
    )


def _add_drawer(
    model: ArticulatedObject, table: Part, name: str, xc: float, z_base: float, h: float
) -> None:
    drawer = model.part(name)
    wall_h = max(0.030, h - 0.024)
    wall_cz = 0.008 + wall_h / 2.0
    drawer.visual(
        Box((0.14, 0.014, h)),
        origin=Origin(xyz=(0.0, -0.007, h / 2.0)),
        material="dark_stained_wood",
        name="front_panel", material_class_id="wood.walnut_dark",
    )
    drawer.visual(
        Cylinder(radius=min(0.030, h * 0.40), length=0.008),
        origin=Origin(xyz=(0.0, -0.017, h / 2.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_stained_wood",
        name="medallion", material_class_id="wood.walnut_dark",
    )
    drawer.visual(
        Cylinder(radius=0.005, length=0.012),
        origin=Origin(xyz=(0.0, -0.025, h / 2.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_stained_wood",
        name="knob_stem", material_class_id="wood.walnut_dark",
    )
    drawer.visual(
        Cylinder(radius=0.011, length=0.010),
        origin=Origin(xyz=(0.0, -0.034, h / 2.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_stained_wood",
        name="knob", material_class_id="wood.walnut_dark",
    )
    drawer.visual(
        Box((0.126, 0.344, 0.008)),
        origin=Origin(xyz=(0.0, 0.170, 0.004)),
        material="oak_wood",
        name="bottom", material_class_id="wood.oak",
    )
    for i, wx in enumerate((-0.058, 0.058)):
        drawer.visual(
            Box((0.010, 0.344, wall_h)),
            origin=Origin(xyz=(wx, 0.170, wall_cz)),
            material="oak_wood",
            name=f"side_wall_{i}", material_class_id="wood.oak",
        )
    drawer.visual(
        Box((0.126, 0.010, wall_h)),
        origin=Origin(xyz=(0.0, 0.337, wall_cz)),
        material="oak_wood",
        name="back_wall", material_class_id="wood.oak",
    )
    model.articulation(
        f"table_to_{name}",
        ArticulationType.PRISMATIC,
        parent=table,
        child=drawer,
        origin=Origin(xyz=(xc, -0.21, z_base)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.3, lower=0.0, upper=DRAWER_TRAVEL),
    )


def _build_treadle_table(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    # Single grounded chassis fuses the iron stand, oak table+cabinets and the
    # cast head; only real mechanisms (band wheel, treadle, handwheel, needle
    # bar, drawers) are jointed children.
    stand = model.part("chassis")
    for side, sx in enumerate((-0.31, 0.31)):
        legs = tube_from_spline_points(
            [
                (sx, -0.19, 0.505),
                (sx, -0.15, 0.43),
                (sx, -0.088, 0.30),
                (sx, -0.10, 0.175),
                (sx, -0.155, 0.06),
                (sx, -0.175, 0.028),
            ],
            radius=0.014,
            up_hint=(1.0, 0.0, 0.0),
        )
        legs.merge(
            tube_from_spline_points(
                [
                    (sx, 0.19, 0.505),
                    (sx, 0.15, 0.43),
                    (sx, 0.088, 0.30),
                    (sx, 0.10, 0.175),
                    (sx, 0.155, 0.06),
                    (sx, 0.175, 0.028),
                ],
                radius=0.014,
                up_hint=(1.0, 0.0, 0.0),
            )
        )
        for fy in (-0.175, 0.175):
            legs.merge(CylinderGeometry(0.018, 0.02).rotate_y(math.pi / 2.0).translate(sx, fy, 0.018))
        stand.visual(mesh_from_geometry(legs, f"side_frame_{side}"), material="cast_iron_black", name=f"side_frame_{side}", material_class_id="metal.cast_iron_bare")
        stand.visual(
            Box((0.035, 0.42, 0.03)),
            origin=Origin(xyz=(sx, 0.0, 0.512)),
            material="cast_iron_black",
            name=f"top_rail_{side}", material_class_id="metal.cast_iron_bare",
        )
        stand.visual(
            Box((0.03, 0.36, 0.025)),
            origin=Origin(xyz=(sx, 0.0, 0.10)),
            material="cast_iron_black",
            name=f"bottom_rail_{side}", material_class_id="metal.cast_iron_bare",
        )
        stand.visual(
            Cylinder(radius=0.012, length=0.025),
            origin=Origin(xyz=(math.copysign(0.2875, sx), A_PIVOT[1], A_PIVOT[2]), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="cast_iron_black",
            name=f"pivot_boss_{side}", material_class_id="metal.cast_iron_bare",
        )
    stand.visual(
        Cylinder(radius=0.011, length=0.63),
        origin=Origin(xyz=(0.0, 0.16, 0.495), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="cast_iron_black",
        name="rear_top_brace", material_class_id="metal.cast_iron_bare",
    )
    for i, by in enumerate((-0.0965, 0.0965)):
        stand.visual(
            Cylinder(radius=0.011, length=0.64),
            origin=Origin(xyz=(0.0, by, 0.20), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="cast_iron_black",
            name=f"lower_brace_{i}", material_class_id="metal.cast_iron_bare",
        )
    stand.visual(
        Box((0.022, 0.30, 0.028)),
        origin=Origin(xyz=(0.31, 0.02, 0.38)),
        material="cast_iron_black",
        name="wheel_support_bar", material_class_id="metal.cast_iron_bare",
    )
    stand.visual(
        Cylinder(radius=0.014, length=0.03),
        origin=Origin(xyz=(0.29, A_WHEEL_C[1], A_WHEEL_C[2]), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="cast_iron_black",
        name="bearing_boss", material_class_id="metal.cast_iron_bare",
    )

    table = stand  # same fused chassis part
    table.visual(
        Box(A_TOP_SIZE),
        origin=Origin(xyz=(0.0, 0.0, 0.5 * (A_TOP_Z0 + A_TOP_Z1))),
        material="oak_wood",
        name="tabletop", material_class_id="wood.oak",
    )
    table.visual(
        Box((0.61, 0.018, 0.10)),
        origin=Origin(xyz=(0.0, 0.195, 0.677)),
        material="dark_stained_wood",
        name="rear_apron", material_class_id="wood.walnut_dark",
    )
    table.visual(
        Box((0.61, 0.018, 0.047)),
        origin=Origin(xyz=(0.0, -0.195, 0.7035)),
        material="dark_stained_wood",
        name="front_rail", material_class_id="wood.walnut_dark",
    )

    def add_cabinet(prefix: str, xc: float) -> None:
        zc = 0.5 * (A_CAB_Z0 + A_CAB_Z1)
        for i, wx in enumerate((xc - 0.074, xc + 0.074)):
            table.visual(
                Box((0.012, 0.42, A_CAB_Z1 - A_CAB_Z0)),
                origin=Origin(xyz=(wx, 0.0, zc)),
                material="dark_stained_wood",
                name=f"{prefix}_wall_{i}", material_class_id="wood.walnut_dark",
            )
        table.visual(
            Box((0.144, 0.012, A_CAB_Z1 - A_CAB_Z0)),
            origin=Origin(xyz=(xc, 0.204, zc)),
            material="dark_stained_wood",
            name=f"{prefix}_back", material_class_id="wood.walnut_dark",
        )
        table.visual(
            Box((0.144, 0.414, 0.012)),
            origin=Origin(xyz=(xc, -0.003, A_CAB_Z0 + 0.006)),
            material="dark_stained_wood",
            name=f"{prefix}_floor", material_class_id="wood.walnut_dark",
        )
        table.visual(
            Box((0.144, 0.414, 0.012)),
            origin=Origin(xyz=(xc, -0.003, A_CAB_Z1 - 0.006)),
            material="dark_stained_wood",
            name=f"{prefix}_ceiling", material_class_id="wood.walnut_dark",
        )

    add_cabinet("left_cabinet", -A_CAB_XC)
    add_cabinet("right_cabinet", A_CAB_XC)

    head = _build_cast_head(model, r)
    _build_cast_needle_bar(model, r, head, A_NEEDLE_JOINT_Z, A_NEEDLE_TRAVEL)

    for name, xc, z_base, h in r.drawers:
        _add_drawer(model, table, name, xc, z_base, h)


def _build_industrial_table(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    frame_hx = 0.46 * r.industrial_table_width_scale
    table_w = I_TABLE_W * r.industrial_table_width_scale
    leg_h = I_TABLE_TOP_Z - I_TABLE_THICK

    # Single grounded chassis fuses the steel K-frame, the flat power table and
    # the cast head (and, via the drive module, the under-slung motor). Only the
    # handwheel, needle bar, motor pulley and V-belt are jointed children.
    k_frame = model.part("chassis")
    for side, sx in enumerate((-frame_hx, frame_hx)):
        for end, ey in enumerate((-I_FRAME_HY, I_FRAME_HY)):
            k_frame.visual(
                Box((I_LEG_TUBE, I_LEG_TUBE, leg_h)),
                origin=Origin(xyz=(sx, ey, leg_h / 2.0)),
                material="steel_frame",
                name=f"leg_{side}_{end}", material_class_id="metal.steel_bare",
            )
            k_frame.visual(
                Cylinder(radius=0.022, length=0.008),
                origin=Origin(xyz=(sx, ey, 0.004)),
                material="foot_pad",
                name=f"foot_{side}_{end}", material_class_id="rubber.smooth_plain",
            )
        k_frame.visual(
            Box((I_LEG_TUBE, 2.0 * I_FRAME_HY, I_LEG_TUBE)),
            origin=Origin(xyz=(sx, 0.0, leg_h - I_LEG_TUBE / 2.0)),
            material="steel_frame",
            name=f"top_rail_{side}", material_class_id="metal.steel_bare",
        )
        k_frame.visual(
            Box((I_LEG_TUBE, 2.0 * I_FRAME_HY, I_LEG_TUBE)),
            origin=Origin(xyz=(sx, 0.0, 0.18)),
            material="steel_frame",
            name=f"lower_stretcher_{side}", material_class_id="metal.steel_bare",
        )
        brace_len = math.sqrt((2.0 * I_FRAME_HY) ** 2 + (leg_h - 0.18 - I_LEG_TUBE) ** 2)
        brace_angle = math.atan2(leg_h - 0.18 - I_LEG_TUBE, 2.0 * I_FRAME_HY)
        k_frame.visual(
            Box((I_LEG_TUBE * 0.75, brace_len, I_LEG_TUBE * 0.75)),
            origin=Origin(xyz=(sx, 0.0, 0.5 * (0.18 + leg_h)), rpy=(brace_angle, 0.0, 0.0)),
            material="steel_frame",
            name=f"k_brace_{side}", material_class_id="metal.steel_bare",
        )
    for i, cz in enumerate((0.18, 0.38)):
        k_frame.visual(
            Box((2.0 * frame_hx, I_LEG_TUBE, I_LEG_TUBE)),
            origin=Origin(xyz=(0.0, -I_FRAME_HY, cz)),
            material="steel_frame",
            name=f"front_cross_{i}", material_class_id="metal.steel_bare",
        )
        k_frame.visual(
            Box((2.0 * frame_hx, I_LEG_TUBE, I_LEG_TUBE)),
            origin=Origin(xyz=(0.0, I_FRAME_HY, cz)),
            material="steel_frame",
            name=f"rear_cross_{i}", material_class_id="metal.steel_bare",
        )

    table = k_frame  # same fused chassis part
    table_profile = rounded_rect_profile(table_w, I_TABLE_D, 0.015)
    cutout = _shift(rounded_rect_profile(I_BED_SIZE[0] + 0.004, I_BED_SIZE[1] + 0.004, 0.006), I_BED_XC, 0.0)
    table_top_geom = ExtrudeWithHolesGeometry(table_profile, [cutout], I_TABLE_THICK, center=True)
    table.visual(
        mesh_from_geometry(table_top_geom, "tabletop"),
        origin=Origin(xyz=(0.0, 0.0, I_TABLE_TOP_Z - I_TABLE_THICK / 2.0)),
        material="laminate_white",
        name="tabletop", material_class_id="plastic.opaque_glossy_molded",
    )

    head = _build_cast_head(model, r)
    _build_cast_needle_bar(model, r, head, I_NEEDLE_JOINT_Z, I_NEEDLE_TRAVEL)


# ============================================================ Slot B drives
def _build_molded_handwheel(model: ArticulatedObject) -> Part:
    body = model.get_part("chassis")
    handwheel = model.part("handwheel")
    wheel_geo = KnobGeometry(
        0.080,
        0.020,
        body_style="cylindrical",
        edge_radius=0.0015,
        grip=KnobGrip(style="ribbed", count=36, depth=0.0006, width=0.0018),
        body_reliefs=(KnobRelief(style="top_recess", width=0.046, depth=0.004),),
        center=False,
    )
    handwheel.visual(
        mesh_from_geometry(wheel_geo, "handwheel_cap"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="body_white",
        name="handwheel_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    handwheel.visual(
        Cylinder(radius=0.008, length=0.028),
        origin=Origin(xyz=(-0.012, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="chrome",
        name="handwheel_shaft", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "handwheel_spin",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=handwheel,
        origin=Origin(xyz=(0.200, 0.0, 0.2565)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=8.0),
    )
    return handwheel


def _build_electric_handwheel(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    _build_molded_handwheel(model)


def _build_hand_crank(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    handwheel = _build_molded_handwheel(model)
    crank_arm = model.part("crank_arm")
    crank_arm.visual(
        Cylinder(radius=0.012, length=0.008),
        origin=Origin(xyz=(0.022, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="steel_silver",
        name="crank_hub", material_class_id="metal.stainless_matte",
    )
    crank_arm.visual(
        Box((0.004, 0.010, 0.050)),
        origin=Origin(xyz=(0.022, 0.0, 0.028)),
        material="steel_silver",
        name="crank_bar", material_class_id="metal.stainless_matte",
    )
    crank_arm.visual(
        Cylinder(radius=0.003, length=0.016),
        origin=Origin(xyz=(0.022, 0.0, 0.055), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="chrome",
        name="grip_pin", material_class_id="metal.chrome_polished",
    )
    # Genuine FIXED joint: the crank hub is bolted onto the spinning handwheel
    # face. Single-source the mount with mount_fixed so the joint origin lands on
    # the handwheel cap (parent) and on the hub (child) — must be wired before
    # crank_grip references crank_arm, or the rebase would shift that subtree.
    mount_fixed(
        model,
        joint_name="crank_arm_mount",
        parent=handwheel,
        child=crank_arm,
        parent_anchor=(0.018, 0.0, 0.0),
        child_anchor=(0.022, 0.0, 0.0),
    )

    crank_grip = model.part("crank_grip")
    crank_grip.visual(
        Cylinder(radius=0.009, length=0.028),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="dark_gray",
        name="grip_barrel", material_class_id="rubber.smooth_plain",
    )
    crank_grip.visual(
        Box((0.024, 0.006, 0.003)),
        origin=Origin(xyz=(0.0, 0.011, 0.0)),
        material="dark_gray",
        name="grip_ridge", material_class_id="rubber.smooth_plain",
    )
    model.articulation(
        "crank_grip_spin",
        ArticulationType.CONTINUOUS,
        parent=crank_arm,
        child=crank_grip,
        # crank_arm visuals were rebased by -(0.022,0,0) by mount_fixed, so the
        # grip pin (authored at local x=0.022) now sits at local x=0.
        origin=Origin(xyz=(0.0, 0.0, 0.055)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=10.0),
    )


def _build_balance_handwheel(model: ArticulatedObject, handwheel_x: float) -> Part:
    head = model.get_part("chassis")
    handwheel = model.part("handwheel")
    hw_geom = WheelGeometry(
        0.088,
        0.024,
        rim=WheelRim(inner_radius=0.072),
        hub=WheelHub(radius=0.015, width=0.028, cap_style="domed"),
        spokes=WheelSpokes(style="straight", count=6, thickness=0.005, window_radius=0.008),
        bore=WheelBore(style="round", diameter=0.008),
    )
    handwheel.visual(mesh_from_geometry(hw_geom, "handwheel"), material="nickel_plate", name="wheel", material_class_id="metal.chrome_polished")
    handwheel.visual(
        Cylinder(radius=0.007, length=0.038),
        origin=Origin(xyz=(-0.019, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="nickel_plate",
        name="axle", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "head_to_handwheel",
        ArticulationType.CONTINUOUS,
        parent=head,
        child=handwheel,
        origin=Origin(xyz=(handwheel_x, 0.0, A_ARM_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=20.0),
    )
    return handwheel


def _build_foot_treadle(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    _build_balance_handwheel(model, A_HANDWHEEL_X)
    stand = model.get_part("chassis")

    band_wheel = model.part("band_wheel")
    bw_geom = WheelGeometry(
        0.15,
        0.026,
        rim=WheelRim(inner_radius=0.132),
        hub=WheelHub(radius=0.018, width=0.032, cap_style="flat"),
        spokes=WheelSpokes(style="straight", count=6, thickness=0.006, window_radius=0.010),
        bore=WheelBore(style="round", diameter=0.012),
    )
    band_wheel.visual(mesh_from_geometry(bw_geom, "band_wheel"), material="cast_iron_black", name="wheel", material_class_id="metal.cast_iron_bare")
    band_wheel.visual(
        Cylinder(radius=0.008, length=0.052),
        origin=Origin(xyz=(0.026, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="cast_iron_black",
        name="axle", material_class_id="metal.cast_iron_bare",
    )
    band_wheel.visual(
        Box((0.008, 0.018, 0.072)),
        origin=Origin(xyz=(-0.009, 0.0, -0.0275)),
        material="cast_iron_black",
        name="crank_arm", material_class_id="metal.cast_iron_bare",
    )
    band_wheel.visual(
        Cylinder(radius=0.0055, length=0.03),
        origin=Origin(xyz=(-0.026, 0.0, -0.055), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="cast_iron_black",
        name="crank_pin", material_class_id="metal.cast_iron_bare",
    )
    model.articulation(
        "stand_to_band_wheel",
        ArticulationType.CONTINUOUS,
        parent=stand,
        child=band_wheel,
        origin=Origin(xyz=A_WHEEL_C),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=25.0),
    )

    treadle = model.part("treadle_pedal")
    lattice = ExtrudeWithHolesGeometry(
        rounded_rect_profile(0.50, 0.24, 0.02),
        [
            _shift(rounded_rect_profile(0.12, 0.055, 0.015), dx, dy)
            for dx in (-0.16, 0.0, 0.16)
            for dy in (-0.0625, 0.0625)
        ],
        0.010,
        center=True,
    )
    treadle.visual(
        mesh_from_geometry(lattice, "pedal_lattice"),
        origin=Origin(xyz=(0.0, -0.06, 0.0)),
        material="cast_iron_black",
        name="pedal_plate", material_class_id="metal.cast_iron_bare",
    )
    treadle.visual(
        Cylinder(radius=0.008, length=0.50),
        origin=Origin(xyz=(0.0, -0.17, 0.012), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="cast_iron_black",
        name="toe_bar", material_class_id="metal.cast_iron_bare",
    )
    for i, px in enumerate((-0.2625, 0.2625)):
        treadle.visual(
            Cylinder(radius=0.008, length=0.055),
            origin=Origin(xyz=(px, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="cast_iron_black",
            name=f"pivot_pin_{i}", material_class_id="metal.cast_iron_bare",
        )
    rod = tube_from_spline_points(
        [(0.21, 0.045, 0.004), (0.214, 0.03, 0.06), (0.219, -0.005, 0.15), (0.221, -0.02, 0.202)],
        radius=0.006,
        up_hint=(1.0, 0.0, 0.0),
    )
    treadle.visual(mesh_from_geometry(rod, "pitman_rod"), material="cast_iron_black", name="pitman_rod", material_class_id="metal.cast_iron_bare")
    eye = TorusGeometry(0.0115, 0.0035).rotate_y(math.pi / 2.0)
    treadle.visual(
        mesh_from_geometry(eye, "pitman_eye"),
        origin=Origin(xyz=(0.221, -0.02, 0.215)),
        material="cast_iron_black",
        name="pitman_eye", material_class_id="metal.cast_iron_bare",
    )
    model.articulation(
        "stand_to_treadle",
        ArticulationType.REVOLUTE,
        parent=stand,
        child=treadle,
        origin=Origin(xyz=A_PIVOT),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=3.0, lower=-0.22, upper=0.22),
    )


def _build_underslung_motor(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    _build_balance_handwheel(model, I_HANDWHEEL_X)
    table = model.get_part("chassis")

    # Motor housing is rigid structure fused into the chassis (bolted under the
    # table via the hanger bracket); only the pulley and belt are separate.
    motor = model.get_part("chassis")
    motor.visual(
        Box(I_MOTOR_SIZE),
        origin=Origin(xyz=(I_MOTOR_CX, I_MOTOR_CY, I_MOTOR_CZ)),
        material="motor_enamel",
        name="motor_body", material_class_id="metal.paint_coated",
    )
    motor_left = I_MOTOR_CX - I_MOTOR_SIZE[0] / 2.0
    motor.visual(
        Cylinder(radius=0.055, length=0.03),
        origin=Origin(xyz=(motor_left - 0.015, I_MOTOR_CY, I_MOTOR_CZ), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="motor_enamel",
        name="end_bell", material_class_id="metal.paint_coated",
    )
    motor.visual(
        Box((0.24, 0.16, 0.006)),
        origin=Origin(xyz=(I_MOTOR_CX, I_MOTOR_CY, I_MOTOR_CZ + I_MOTOR_SIZE[2] / 2.0 + 0.003)),
        material="steel_frame",
        name="mount_plate", material_class_id="metal.steel_bare",
    )
    shaft_left = motor_left - 0.030
    shaft_len = I_HANDWHEEL_X - shaft_left
    motor.visual(
        Cylinder(radius=0.008, length=shaft_len),
        origin=Origin(xyz=(shaft_left + shaft_len / 2.0, I_MOTOR_CY, I_MOTOR_CZ), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="nickel_plate",
        name="shaft", material_class_id="metal.chrome_polished",
    )
    # Hanger bracket bridging the motor mount plate up to the table underside so
    # the FIXED joint origin lands on real geometry on both sides.
    _table_under_z = I_TABLE_TOP_Z - I_TABLE_THICK
    _mount_top_z = I_MOTOR_CZ + I_MOTOR_SIZE[2] / 2.0 + 0.006
    motor.visual(
        Box((0.030, 0.030, _table_under_z - _mount_top_z + 0.004)),
        origin=Origin(xyz=(I_MOTOR_CX, I_MOTOR_CY, 0.5 * (_mount_top_z + _table_under_z))),
        material="steel_frame",
        name="motor_hanger", material_class_id="metal.steel_bare",
    )

    pulley = model.part("motor_pulley")
    pulley.visual(
        Cylinder(radius=I_PULLEY_R, length=I_PULLEY_W),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="nickel_plate",
        name="pulley_body", material_class_id="metal.chrome_polished",
    )
    pulley.visual(
        Cylinder(radius=I_PULLEY_R - 0.005, length=I_PULLEY_W + 0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="steel_frame",
        name="pulley_groove", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "motor_to_pulley",
        ArticulationType.CONTINUOUS,
        parent=motor,
        child=pulley,
        origin=Origin(xyz=(I_HANDWHEEL_X, I_MOTOR_CY, I_PULLEY_CZ)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=30.0),
    )

    belt = model.part("v_belt")
    hw_r = 0.088
    pr = I_PULLEY_R
    belt_points = [
        (I_HANDWHEEL_X, I_MOTOR_CY + pr, I_PULLEY_CZ),
        (I_HANDWHEEL_X, I_MOTOR_CY + 0.5 * (pr + hw_r), 0.5 * (I_PULLEY_CZ + A_ARM_Z)),
        (I_HANDWHEEL_X, hw_r, A_ARM_Z),
        (I_HANDWHEEL_X, 0.65 * hw_r, A_ARM_Z + 0.75 * hw_r),
        (I_HANDWHEEL_X, 0.0, A_ARM_Z + hw_r),
        (I_HANDWHEEL_X, -0.65 * hw_r, A_ARM_Z + 0.75 * hw_r),
        (I_HANDWHEEL_X, -hw_r, A_ARM_Z),
        (I_HANDWHEEL_X, -0.5 * (pr + hw_r), 0.5 * (I_PULLEY_CZ + A_ARM_Z)),
        (I_HANDWHEEL_X, -(I_MOTOR_CY + pr), I_PULLEY_CZ),
        (I_HANDWHEEL_X, -0.5 * pr, I_PULLEY_CZ - 0.85 * pr),
        (I_HANDWHEEL_X, 0.0, I_PULLEY_CZ - pr),
        (I_HANDWHEEL_X, 0.5 * pr, I_PULLEY_CZ - 0.85 * pr),
    ]
    belt_geom = tube_from_spline_points(belt_points, radius=0.004, closed_spline=True, up_hint=(1.0, 0.0, 0.0))
    belt.visual(mesh_from_geometry(belt_geom, "belt_loop"), material="belt_rubber", name="belt_loop", material_class_id="rubber.smooth_plain")
    # The V-belt is the one genuine remaining FIXED joint: a static loop that
    # wraps the (moving) handwheel and pulley. Single-source its placement with
    # mount_fixed at the pulley-top belt control point, which sits ~10mm below
    # the fused motor housing (chassis) so the joint origin lands on real
    # geometry on BOTH sides while the belt stays exactly where it was authored.
    belt_anchor = (I_HANDWHEEL_X, I_MOTOR_CY + pr, I_PULLEY_CZ)
    mount_fixed(
        model,
        joint_name="chassis_to_belt",
        parent=table,
        child=belt,
        parent_anchor=belt_anchor,
        child_anchor=belt_anchor,
    )


# ============================================================ Slot C controls
def _build_stitch_dial(model: ArticulatedObject, body: Part) -> None:
    stitch_dial = model.part("stitch_dial")
    dial_geo = KnobGeometry(
        0.056,
        0.017,
        body_style="cylindrical",
        edge_radius=0.0012,
        grip=KnobGrip(style="fluted", count=22, depth=0.0012),
        indicator=KnobIndicator(style="line", mode="engraved", depth=0.0008),
        center=False,
    )
    stitch_dial.visual(
        mesh_from_geometry(dial_geo, "stitch_dial_cap"),
        origin=Origin(xyz=(0.0, -0.0016, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="body_white",
        name="stitch_dial_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    stitch_dial.visual(
        Cylinder(radius=0.006, length=0.022),
        origin=Origin(xyz=(0.0, 0.008, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="chrome",
        name="stitch_dial_shaft", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "stitch_select",
        ArticulationType.REVOLUTE,
        parent=body,
        child=stitch_dial,
        origin=Origin(xyz=(0.150, -0.075, 0.205)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=-math.pi, upper=math.pi),
    )


def _build_tension_dial(model: ArticulatedObject, body: Part) -> None:
    tension_dial = model.part("tension_dial")
    tension_geo = KnobGeometry(
        0.030,
        0.009,
        body_style="cylindrical",
        edge_radius=0.0008,
        grip=KnobGrip(style="fluted", count=18, depth=0.0007),
        indicator=KnobIndicator(style="dot", mode="raised", angle_deg=0.0),
        center=False,
    )
    tension_dial.visual(
        mesh_from_geometry(tension_geo, "tension_dial_cap"),
        origin=Origin(xyz=(0.0, -0.0004, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="body_white",
        name="tension_dial_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    tension_dial.visual(
        Cylinder(radius=0.004, length=0.016),
        origin=Origin(xyz=(0.0, 0.006, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="chrome",
        name="tension_dial_shaft", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "tension_adjust",
        ArticulationType.REVOLUTE,
        parent=body,
        child=tension_dial,
        origin=Origin(xyz=(-0.130, -0.070, 0.215)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=4.0, lower=-math.pi, upper=math.pi),
    )


def _build_domestic_full(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    body = model.get_part("chassis")
    _build_stitch_dial(model, body)
    reverse_lever = model.part("reverse_lever")
    reverse_lever.visual(
        mesh_from_cadquery(_paddle_shape(), "reverse_lever_paddle"),
        origin=Origin(xyz=(0.0, -0.011, 0.0)),
        material="trim_white",
        name="reverse_lever_paddle", material_class_id="plastic.opaque_glossy_molded",
    )
    reverse_lever.visual(
        Box((0.012, 0.016, 0.020)),
        origin=Origin(xyz=(0.0, 0.002, 0.0)),
        material="trim_white",
        name="reverse_lever_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        "reverse_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=reverse_lever,
        origin=Origin(xyz=(0.150, -0.075, 0.130)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=0.1, lower=0.0, upper=0.008),
    )
    _build_tension_dial(model, body)


def _build_domestic_takeup(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    body = model.get_part("chassis")
    _build_stitch_dial(model, body)
    _build_tension_dial(model, body)
    take_up_lever = model.part("take_up_lever")
    take_up_lever.visual(
        mesh_from_cadquery(_takeup_lever_shape(), "takeup_lever_arm"),
        material="chrome",
        name="takeup_lever_arm", material_class_id="metal.chrome_polished",
    )
    model.articulation(
        "takeup_oscillate",
        ArticulationType.REVOLUTE,
        parent=body,
        child=take_up_lever,
        origin=Origin(xyz=(-0.170, -0.072, 0.278)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=6.0, lower=-0.50, upper=0.50),
    )


def _build_bare_mechanical(model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    # Cast machines expose no extra articulated front controls; the tension knob,
    # presser bar and presser foot are already head visuals emitted by Slot A.
    return


FORM_FACTORIES = {
    "compact_bench": _build_compact_bench,
    "free_arm": _build_free_arm,
    "treadle_table": _build_treadle_table,
    "industrial_table": _build_industrial_table,
}
DRIVE_FACTORIES = {
    "electric_handwheel": _build_electric_handwheel,
    "hand_crank": _build_hand_crank,
    "foot_treadle": _build_foot_treadle,
    "underslung_motor": _build_underslung_motor,
}
CONTROL_FACTORIES = {
    "domestic_full": _build_domestic_full,
    "domestic_takeup": _build_domestic_takeup,
    "bare_mechanical": _build_bare_mechanical,
}


def build_sewing_machine(
    config: SewingMachineConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="sewing_machine", assets=assets)
    for name, rgba in r.materials.items():
        model.material(name, rgba=rgba)

    FORM_FACTORIES[r.machine_form](model, r)
    DRIVE_FACTORIES[r.drive_mechanism](model, r)
    CONTROL_FACTORIES[r.head_controls](model, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sewing_machine(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_sewing_machine(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedSewingMachineConfig) -> list[tuple[str, str]]:
    choices = [
        ("machine_form", r.machine_form),
        ("drive_mechanism", r.drive_mechanism),
        ("head_controls", r.head_controls),
    ]
    if r.machine_form == "treadle_table":
        choices.append(("drawer_count", f"n{r.drawer_count}"))
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# =============================================================== tests
def _visual_names(part: Part) -> set[str]:
    return {v.name for v in part.visuals if v.name is not None}


def _has_visual(part: Part, name: str) -> bool:
    return name in _visual_names(part)


def _allow(ctx: TestContext, model: ArticulatedObject, a: str, b: str, ea: str, eb: str, reason: str) -> None:
    names = {p.name for p in model.parts}
    if a in names and b in names:
        pa, pb = model.get_part(a), model.get_part(b)
        if _has_visual(pa, ea) and _has_visual(pb, eb):
            ctx.allow_overlap(pa, pb, elem_a=ea, elem_b=eb, reason=reason)


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedSewingMachineConfig) -> None:
    # Drawers slide out on their runners and lose contact with the stand.
    for p in model.parts:
        if p.name.startswith("drawer_"):
            ctx.allow_isolated_part(
                p,
                reason="drawer slides out on its runners and loses contact with the stand/table",
            )
    # The rigid structure (bed/body or stand/table/head/frame/motor) is fused
    # into one ``chassis`` part, so captured moving shafts overlap chassis bores.
    if r.machine_form == "free_arm":
        names = {p.name for p in model.parts}
        if "accessory_tray" in names:
            ctx.allow_isolated_part(
                model.get_part("accessory_tray"),
                reason="accessory tray slides off the front of the free-arm bed and loses contact",
            )
    if r.family == "molded":
        _allow(ctx, model, "chassis", "handwheel", "body_shell", "handwheel_shaft", "handwheel shaft captured in the pillar bushing bore")
        _allow(ctx, model, "chassis", "needle_bar", "body_shell", "needle_bar_shaft", "needle bar slides in the head bushing")
        _allow(ctx, model, "chassis", "presser_foot", "body_shell", "presser_bar_shaft", "presser bar slides in the head bushing")
        _allow(ctx, model, "chassis", "stitch_dial", "body_shell", "stitch_dial_shaft", "stitch dial shaft captured in the pillar bore")
        _allow(ctx, model, "chassis", "reverse_lever", "body_shell", "reverse_lever_stem", "reverse lever stem slides in the pillar slot")
        _allow(ctx, model, "chassis", "tension_dial", "body_shell", "tension_dial_shaft", "tension dial shaft captured in the head bore")
        # take-up lever oscillates on a head-front boss; its arm sweeps through
        # the takeup slot on the C-body face (captured pivot overlap).
        _allow(ctx, model, "chassis", "take_up_lever", "body_shell", "takeup_lever_arm", "take-up lever sweeps through the head-front takeup slot")
        _allow(ctx, model, "chassis", "take_up_lever", "takeup_slot", "takeup_lever_arm", "take-up lever eye travels within the takeup slot")
        # hand crank grip/pin capture + hub-on-wheel.
        _allow(ctx, model, "handwheel", "crank_arm", "handwheel_cap", "crank_hub", "crank hub bolted to the handwheel face")
        _allow(ctx, model, "crank_arm", "crank_grip", "grip_pin", "grip_barrel", "grip barrel encloses the crank pin bearing")
        _allow(ctx, model, "crank_arm", "crank_grip", "crank_bar", "grip_barrel", "grip barrel surrounds the arm end at the pin")
    else:
        # cast captured shafts inside the fused chassis head.
        _allow(ctx, model, "handwheel", "chassis", "axle", "pillar", "handwheel axle seated in the pillar bearing bore")
        _allow(ctx, model, "needle_bar", "chassis", "bar", "nose", "needle bar slides inside the head nose bore")
        if r.machine_form == "treadle_table":
            _allow(ctx, model, "band_wheel", "chassis", "axle", "bearing_boss", "band-wheel axle captured by the stand bearing boss")
            for i in range(2):
                _allow(ctx, model, "treadle_pedal", "chassis", f"pivot_pin_{i}", f"pivot_boss_{i}", "treadle pivot pin seated in the frame boss")
            # pitman eye rides the crank pin (coupled treadle drive; independent QC phases interpenetrate).
            for pe in ("pitman_eye", "pitman_rod"):
                for we in ("crank_pin", "crank_arm", "wheel"):
                    _allow(ctx, model, "treadle_pedal", "band_wheel", pe, we, "pitman eye/rod rides the band-wheel crank pin through the coupled treadle cycle")
        else:  # industrial
            _allow(ctx, model, "handwheel", "v_belt", "wheel", "belt_loop", "V-belt wraps the handwheel rim")
            _allow(ctx, model, "motor_pulley", "v_belt", "pulley_body", "belt_loop", "V-belt wraps the motor pulley")
            _allow(ctx, model, "motor_pulley", "v_belt", "pulley_groove", "belt_loop", "V-belt seats in the pulley V-groove")
            _allow(ctx, model, "chassis", "motor_pulley", "motor_body", "pulley_groove", "pulley groove recessed near the motor shaft")
            _allow(ctx, model, "chassis", "motor_pulley", "motor_body", "pulley_body", "pulley mounted on the motor shaft stub")
            _allow(ctx, model, "chassis", "v_belt", "mount_plate", "belt_loop", "belt passes near the motor mount bracket")
            _allow(ctx, model, "chassis", "v_belt", "motor_body", "belt_loop", "belt run passes near the motor body")
            _allow(ctx, model, "chassis", "v_belt", "tabletop", "belt_loop", "belt passes through the table bed cutout")


def run_sewing_machine_tests(
    object_model: ArticulatedObject, config: SewingMachineConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    arts = {j.name: j for j in object_model.articulations}

    # --- category identity ------------------------------------------------
    ctx.check("needle_bar_present", "needle_bar" in parts)
    needle_joint = arts.get("needle_stroke") or arts.get("head_to_needle_bar")
    ctx.check(
        "needle_is_prismatic",
        needle_joint is not None and needle_joint.articulation_type == ArticulationType.PRISMATIC,
    )
    ctx.check("handwheel_present", "handwheel" in parts)
    hw_joint = arts.get("handwheel_spin") or arts.get("head_to_handwheel")
    ctx.check(
        "handwheel_spins_continuously_about_x",
        hw_joint is not None
        and hw_joint.articulation_type == ArticulationType.CONTINUOUS
        and abs(hw_joint.axis[0]) == 1.0,
    )
    # The grounded chassis fuses the C-head; identity = chassis carries either
    # the molded body shell or the cast head nose.
    ctx.check("chassis_grounded", "chassis" in parts)
    chassis = object_model.get_part("chassis") if "chassis" in parts else None
    ctx.check(
        "c_head_present",
        chassis is not None and (_has_visual(chassis, "body_shell") or _has_visual(chassis, "nose")),
    )

    # --- form-specific structure -----------------------------------------
    if r.machine_form == "free_arm":
        ctx.check("free_arm_tray_present", "accessory_tray" in parts)
    if r.machine_form == "treadle_table":
        ctx.check("treadle_pedal_present", "treadle_pedal" in parts)
        ctx.check("band_wheel_present", "band_wheel" in parts)
        drawer_parts = [p for p in parts if p.startswith("drawer_")]
        ctx.check(
            "drawer_count_matches_multiplicity",
            len(drawer_parts) == r.drawer_count,
            details=f"expected {r.drawer_count} drawers, got {len(drawer_parts)}",
        )
    if r.machine_form == "industrial_table":
        ctx.check(
            "motor_and_belt_present",
            {"motor_pulley", "v_belt"} <= parts
            and chassis is not None
            and _has_visual(chassis, "motor_body"),
        )
    if r.drive_mechanism == "hand_crank":
        ctx.check("crank_grip_present", "crank_grip" in parts)
    if r.head_controls == "domestic_full":
        ctx.check("domestic_full_controls", {"stitch_dial", "reverse_lever", "tension_dial"} <= parts)
    if r.head_controls == "domestic_takeup":
        ctx.check("takeup_controls", {"stitch_dial", "tension_dial", "take_up_lever"} <= parts)

    # --- targeted motion checks (Rule 5) ---------------------------------
    needle_bar = object_model.get_part("needle_bar")
    needle_elem = "needle"
    rest_needle = ctx.part_element_world_aabb(needle_bar, elem=needle_elem)
    if needle_joint is not None and rest_needle is not None:
        # Positive q lowers the needle for cast heads, negative for molded heads.
        low_q = needle_joint.motion_limits.upper if r.family == "cast" else needle_joint.motion_limits.lower
        if low_q is not None:
            with ctx.pose({needle_joint.name: float(low_q)}):
                low_needle = ctx.part_element_world_aabb(needle_bar, elem=needle_elem)
                ctx.check(
                    "needle_descends_toward_plate",
                    low_needle is not None and low_needle[0][2] < rest_needle[0][2] - 0.002,
                    details=f"rest={rest_needle}, low={low_needle}",
                )

    if r.family == "molded" and "presser_foot" in parts:
        presser = object_model.get_part("presser_foot")
        rest_sole = ctx.part_element_world_aabb(presser, elem="foot_sole")
        with ctx.pose({"presser_lift": 0.007}):
            lifted = ctx.part_element_world_aabb(presser, elem="foot_sole")
            ctx.check(
                "presser_foot_lifts",
                rest_sole is not None and lifted is not None and lifted[0][2] > rest_sole[0][2] + 0.004,
                details=f"rest={rest_sole}, lifted={lifted}",
            )

    if r.drive_mechanism == "foot_treadle":
        treadle = object_model.get_part("treadle_pedal")
        rest_plate = ctx.part_element_world_aabb(treadle, elem="pedal_plate")
        with ctx.pose({"stand_to_treadle": 0.18}):
            down_plate = ctx.part_element_world_aabb(treadle, elem="pedal_plate")
            ctx.check(
                "treadle_toe_rocks_down_above_floor",
                rest_plate is not None
                and down_plate is not None
                and (rest_plate[0][2] - down_plate[0][2]) > 0.012
                and down_plate[0][2] > 0.005,
                details=f"rest={rest_plate}, down={down_plate}",
            )
        band_wheel = object_model.get_part("band_wheel")
        pin_rest = ctx.part_element_world_aabb(band_wheel, elem="crank_pin")
        with ctx.pose({"stand_to_band_wheel": math.pi}):
            pin_up = ctx.part_element_world_aabb(band_wheel, elem="crank_pin")
            ctx.check(
                "band_wheel_crank_pin_orbits",
                pin_rest is not None and pin_up is not None and (pin_up[0][2] - pin_rest[0][2]) > 0.05,
                details=f"rest={pin_rest}, up={pin_up}",
            )

    if r.drive_mechanism == "hand_crank":
        grip = object_model.get_part("crank_grip")
        rest_ridge = ctx.part_element_world_aabb(grip, elem="grip_ridge")
        with ctx.pose({"crank_grip_spin": math.pi / 2.0}):
            spun = ctx.part_element_world_aabb(grip, elem="grip_ridge")
            ctx.check(
                "crank_grip_spins_on_pin",
                rest_ridge is not None and spun is not None and abs(spun[1][1] - rest_ridge[1][1]) > 0.004,
                details=f"rest={rest_ridge}, spun={spun}",
            )

    if r.drive_mechanism == "underslung_motor":
        pulley_joint = arts.get("motor_to_pulley")
        ctx.check(
            "motor_pulley_continuous",
            pulley_joint is not None and pulley_joint.articulation_type == ArticulationType.CONTINUOUS,
        )

    if r.machine_form == "free_arm" and "accessory_tray" in parts:
        tray = object_model.get_part("accessory_tray")
        rest_tray = ctx.part_world_position(tray)
        with ctx.pose({"tray_slide": 0.140}):
            off_tray = ctx.part_world_position(tray)
            ctx.check(
                "accessory_tray_slides_off_front",
                rest_tray is not None and off_tray is not None and off_tray[1] < rest_tray[1] - 0.10,
                details=f"rest={rest_tray}, off={off_tray}",
            )

    if r.machine_form == "treadle_table" and r.drawers:
        first = r.drawers[0][0]
        drawer = object_model.get_part(first)
        rest_d = ctx.part_world_aabb(drawer)
        with ctx.pose({f"table_to_{first}": DRAWER_TRAVEL}):
            open_d = ctx.part_world_aabb(drawer)
            ctx.check(
                "drawer_pulls_out_front",
                rest_d is not None and open_d is not None and (rest_d[0][1] - open_d[0][1]) > 0.15,
                details=f"rest={rest_d}, open={open_d}",
            )

    # --- full sampled-pose collision sweep (Rule 5) ----------------------
    movable = sum(
        1
        for j in object_model.articulations
        if j.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC, ArticulationType.CONTINUOUS)
    )
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=32 if movable > 6 else 64,
        ignore_fixed=True,
    )
    return ctx.report()


__all__ = [
    "DriveMechanism",
    "HeadControls",
    "MachineForm",
    "PaletteTheme",
    "ResolvedSewingMachineConfig",
    "SewingMachineConfig",
    "__modular__",
    "build_seeded_sewing_machine",
    "build_sewing_machine",
    "config_from_seed",
    "resolve_config",
    "run_sewing_machine_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
