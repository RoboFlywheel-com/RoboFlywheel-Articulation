# SPDX-License-Identifier: Apache-2.0

"""Walk-behind seed planter (row seeder) modular template.

Sourced from ``articraft_template_authoring/specs_modular_v1/seeder.md`` and the
``pictureX/0611/seeder`` 5-star pool (3 picture anchors + 14 slot-fork variants),
all synced under ``data/records/rec_0611_seeder_var_*`` and
``rec_picturex_0611__seeder__00{1,2,3}``.

All 17 samples share ONE kinematic skeleton: a single root ``chassis`` part that
inlines every non-moving element (side rails, cross members, transverse axle(s),
tapered open hopper mesh, seed throat/chute tubes, metering cheeks + shaft, furrow
opener + soil tools, twin bent push-handle tubes, depth pivot bracket), plus four
moving children on ``+Y`` axes:

  * ``wheel_a`` / ``wheel_b`` — two ground wheels (CONTINUOUS). ``wheel_layout``
    (Slot C, 2) sets whether they are tandem (fore/aft on centerline) or
    side_by_side (twin coaxial on one front axle).
  * ``meter_rotor`` — one seed-metering rotor (CONTINUOUS). ``meter_form``
    (Slot A, 5 — the primary ③ form family) sets the rotor geometry.
  * ``depth_lever`` — one furrow-depth lever (REVOLUTE, bounded).

``opener_form`` (Slot B, 4) is a ③ family of the fixed soil tool inlined per row;
``row_count`` (multiplicity N in {1,2,3,4,6}) replicates the hopper->chute->opener
lane laterally in Y (Rule 1: lanes do not move); ``drive_detail`` (④, 3) welds a
host-conformal drive dressing onto the meter cheeks. Diversity is ③/④/⑤/⑥ +
multiplicity — the skeleton and the 4 joint types are source-locked (single).

Capture joints (wheel hub on axle, rotor hub on shaft, lever sleeve on pivot) are
pin-through-hub, so they omit ``MatingContract`` (grandfathered) and are guarded
by element-scoped ``allow_overlap`` mirroring each source record's run_tests.
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
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TireGeometry,
    TireSidewall,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

MeterForm = Literal[
    "vane_paddle", "finger_paddle", "pocket_plate", "fluted_roller", "perforated_plate"
]
OpenerForm = Literal["hoe_shank", "forged_shoe", "runner_shoe", "double_disc"]
WheelLayout = Literal["tandem", "side_by_side"]
DriveDetail = Literal["chain_guard", "belt_cover", "direct_pin"]
PaletteStyle = Literal[
    "classic_blue_green", "safety_orange", "farm_green_yellow", "oxide_red", "teal_industrial"
]

METER_FORMS: tuple[MeterForm, ...] = (
    "vane_paddle",
    "finger_paddle",
    "pocket_plate",
    "fluted_roller",
    "perforated_plate",
)
OPENER_FORMS: tuple[OpenerForm, ...] = ("hoe_shank", "forged_shoe", "runner_shoe", "double_disc")
WHEEL_LAYOUTS: tuple[WheelLayout, ...] = ("tandem", "side_by_side")
DRIVE_DETAILS: tuple[DriveDetail, ...] = ("chain_guard", "belt_cover", "direct_pin")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_blue_green",
    "safety_orange",
    "farm_green_yellow",
    "oxide_red",
    "teal_industrial",
)

ROW_COUNTS: tuple[int, ...] = (1, 2, 3, 4, 6)
# small-N heavy (spec §8): N=1 dominant, N=2 common, {3,4} occasional, 6 rare.
ROW_COUNT_WEIGHTS: tuple[float, ...] = (0.42, 0.28, 0.14, 0.11, 0.05)
N_MIN, N_MAX = 1, 6

# ---------------------------------------------------------------------------
# Palette (⑥). Keys: frame / hopper / wheel / tire / steel / dark / grip / accent.
# Colorways read from the anchors (001 blue/green, 002 orange, 003 green/yellow)
# plus two realistic farm companions.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_blue_green": {
        "frame": (0.10, 0.58, 0.34, 1.0),
        "hopper": (0.055, 0.22, 0.62, 1.0),
        "wheel": (0.17, 0.18, 0.18, 1.0),
        "tire": (0.03, 0.03, 0.03, 1.0),
        "steel": (0.62, 0.65, 0.67, 1.0),
        "dark": (0.10, 0.11, 0.11, 1.0),
        "grip": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.45, 0.16, 0.10, 1.0),
    },
    "safety_orange": {
        "frame": (0.94, 0.49, 0.015, 1.0),
        "hopper": (0.94, 0.49, 0.015, 1.0),
        "wheel": (0.20, 0.22, 0.22, 1.0),
        "tire": (0.035, 0.038, 0.040, 1.0),
        "steel": (0.64, 0.67, 0.68, 1.0),
        "dark": (0.72, 0.28, 0.010, 1.0),
        "grip": (0.03, 0.03, 0.032, 1.0),
        "accent": (0.72, 0.28, 0.010, 1.0),
    },
    "farm_green_yellow": {
        "frame": (0.08, 0.29, 0.20, 1.0),
        "hopper": (0.91, 0.25, 0.035, 1.0),
        "wheel": (0.58, 0.61, 0.59, 1.0),
        "tire": (0.025, 0.026, 0.024, 1.0),
        "steel": (0.58, 0.61, 0.59, 1.0),
        "dark": (0.10, 0.12, 0.11, 1.0),
        "grip": (0.035, 0.040, 0.036, 1.0),
        "accent": (0.72, 0.70, 0.08, 1.0),
    },
    "oxide_red": {
        "frame": (0.55, 0.16, 0.11, 1.0),
        "hopper": (0.86, 0.82, 0.72, 1.0),
        "wheel": (0.16, 0.16, 0.17, 1.0),
        "tire": (0.03, 0.03, 0.03, 1.0),
        "steel": (0.60, 0.62, 0.63, 1.0),
        "dark": (0.12, 0.10, 0.10, 1.0),
        "grip": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.24, 0.22, 0.22, 1.0),
    },
    "teal_industrial": {
        "frame": (0.03, 0.42, 0.44, 1.0),
        "hopper": (0.86, 0.72, 0.10, 1.0),
        "wheel": (0.15, 0.16, 0.17, 1.0),
        "tire": (0.03, 0.03, 0.03, 1.0),
        "steel": (0.60, 0.63, 0.64, 1.0),
        "dark": (0.10, 0.12, 0.12, 1.0),
        "grip": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.85, 0.72, 0.10, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Canonical dimensions (meters). Front = +X, Z up, Y lateral. Real-world scale
# from the anchors (wheel r ~0.18-0.36, hopper ~0.24, handles rise ~1.1).
# ---------------------------------------------------------------------------
_WHEEL_R = 0.180
_WHEEL_W = 0.030
_RAIL_Y = 0.110  # side-rail lateral offset (rails inboard of the wheels)
_RAIL_W = 0.026
_RAIL_H = 0.050
_WORKING_X = 0.14  # |x| bound of the hopper/chute/opener working zone
_HOPPER_H = 0.200
_HOPPER_BASE_DZ = 0.140  # hopper floor above beam_z
_METER_R = 0.046
_METER_Y = -0.160  # meter rotor is side-mounted (anchors 001/003 mount it aside)
_LEVER_Y = 0.150  # depth lever on the opposite side
_HANDLE_RISE = 0.86


@dataclass(frozen=True)
class SeederConfig:
    meter_form: MeterForm | None = None
    opener_form: OpenerForm | None = None
    wheel_layout: WheelLayout | None = None
    drive_detail: DriveDetail | None = None
    row_count: int | None = None
    palette_style: PaletteStyle = "classic_blue_green"
    wheel_radius_scale: float = 1.0
    hopper_scale: float = 1.0
    handle_height_scale: float = 1.0
    meter_radius_scale: float = 1.0
    depth_travel_scale: float = 1.0
    name: str = "seeder"


@dataclass(frozen=True)
class ResolvedSeederConfig:
    meter_form: MeterForm
    opener_form: OpenerForm
    wheel_layout: WheelLayout
    drive_detail: DriveDetail
    row_count: int
    palette_style: PaletteStyle
    # concrete geometry
    wheel_r: float
    wheel_w: float
    beam_z: float
    front_x: float
    rear_x: float
    axle_x: float  # side_by_side front axle x
    side_wheel_y: float
    hopper_h: float
    hopper_base_z: float
    hopper_half_x: float
    hopper_half_y: float
    meter_r: float
    row_spacing: float
    handle_rise: float
    depth_upper: float
    depth_lower: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> SeederConfig:
    rng = random.Random(seed)
    return SeederConfig(
        meter_form=rng.choice(METER_FORMS),
        opener_form=rng.choice(OPENER_FORMS),
        wheel_layout=rng.choice(WHEEL_LAYOUTS),
        drive_detail=rng.choice(DRIVE_DETAILS),
        row_count=rng.choices(ROW_COUNTS, weights=ROW_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_radius_scale=round(rng.uniform(0.85, 1.25), 4),
        hopper_scale=round(rng.uniform(0.88, 1.15), 4),
        handle_height_scale=round(rng.uniform(0.88, 1.18), 4),
        meter_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        depth_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_seeder_{seed}",
    )


def resolve_config(config: SeederConfig | None = None) -> ResolvedSeederConfig:
    cfg = config or SeederConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    meter_form = _pick(cfg.meter_form, METER_FORMS)
    opener_form = _pick(cfg.opener_form, OPENER_FORMS)
    wheel_layout = _pick(cfg.wheel_layout, WHEEL_LAYOUTS)
    drive_detail = _pick(cfg.drive_detail, DRIVE_DETAILS)

    row_count = int(cfg.row_count) if cfg.row_count is not None else 1
    row_count = int(_clamp(row_count, N_MIN, N_MAX))

    wr_scale = _clamp(cfg.wheel_radius_scale, 0.85, 1.25)
    hop_scale = _clamp(cfg.hopper_scale, 0.88, 1.15)
    hh_scale = _clamp(cfg.handle_height_scale, 0.88, 1.18)
    mr_scale = _clamp(cfg.meter_radius_scale, 0.88, 1.15)
    dt_scale = _clamp(cfg.depth_travel_scale, 0.85, 1.15)

    wheel_r = _WHEEL_R * wr_scale
    beam_z = wheel_r  # rails ride at axle height
    hopper_h = _HOPPER_H * hop_scale
    hopper_base_z = beam_z + _HOPPER_BASE_DZ
    hopper_half_x = 0.11 * hop_scale
    hopper_half_y = 0.095 * hop_scale
    meter_r = _METER_R * mr_scale

    # --- clearance inequality: wheel disc X-band must clear the working zone. ---
    # back-reach of a wheel = center_x - wheel_r must stay >= working_x + margin.
    margin = 0.06
    front_x = wheel_r + _WORKING_X + margin  # tandem front / general
    rear_x = -(wheel_r + _WORKING_X + margin)  # tandem rear
    axle_x = wheel_r + _WORKING_X + margin  # side_by_side front axle
    # --- clearance inequality: side rails inboard of the side_by_side wheels. ---
    side_wheel_y = _RAIL_Y + _RAIL_W / 2.0 + _WHEEL_W / 2.0 + 0.030

    # row spacing: lanes must not overlap laterally (2*hopper_half_y + gap).
    row_spacing = max(2.0 * hopper_half_y + 0.045, 0.17)

    depth_upper = _clamp(0.40 * dt_scale, 0.25, 0.50)
    depth_lower = -_clamp(0.32 * dt_scale, 0.22, 0.42)

    return ResolvedSeederConfig(
        meter_form=meter_form,
        opener_form=opener_form,
        wheel_layout=wheel_layout,
        drive_detail=drive_detail,
        row_count=row_count,
        palette_style=palette_style,
        wheel_r=wheel_r,
        wheel_w=_WHEEL_W,
        beam_z=beam_z,
        front_x=front_x,
        rear_x=rear_x,
        axle_x=axle_x,
        side_wheel_y=side_wheel_y,
        hopper_h=hopper_h,
        hopper_base_z=hopper_base_z,
        hopper_half_x=hopper_half_x,
        hopper_half_y=hopper_half_y,
        meter_r=meter_r,
        row_spacing=row_spacing,
        handle_rise=_HANDLE_RISE * hh_scale,
        depth_upper=depth_upper,
        depth_lower=depth_lower,
        name=cfg.name or "seeder",
    )


def with_overrides(config: SeederConfig, **kwargs: object) -> SeederConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SeederConfig | ResolvedSeederConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSeederConfig) else resolve_config(config)
    return (
        ("meter_form", r.meter_form),
        ("opener_form", r.opener_form),
        ("wheel_layout", r.wheel_layout),
        ("drive_detail", r.drive_detail),
        ("row_count", f"n{r.row_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared mesh helpers (built ONCE per build, instanced across rows — §7.5).
# ---------------------------------------------------------------------------
def _tube(points, radius: float, name: str, assets=None):
    return mesh_from_geometry(
        tube_from_spline_points(
            points, radius=radius, samples_per_segment=10, radial_segments=14, cap_ends=True
        ),
        name,
    )


def _hopper_solid(r: ResolvedSeederConfig) -> cq.Workplane:
    """Open, thin-walled tapered seed bin authored around the local origin."""
    hx, hy, h = r.hopper_half_x, r.hopper_half_y, r.hopper_h
    outer = (
        cq.Workplane("XY")
        .rect(2 * hx * 0.62, 2 * hy * 0.62)
        .workplane(offset=h)
        .rect(2 * hx, 2 * hy)
        .loft(combine=True)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=0.014)
        .rect(2 * hx * 0.62 - 0.028, 2 * hy * 0.62 - 0.028)
        .workplane(offset=h + 0.008)
        .rect(2 * hx - 0.026, 2 * hy - 0.026)
        .loft(combine=True)
    )
    return outer.cut(inner)


def _wheel_mesh(r: ResolvedSeederConfig, name: str):
    """WheelGeometry hero mesh (authored about local X; yawed +90 at placement)."""
    rad = r.wheel_r
    return mesh_from_geometry(
        WheelGeometry(
            rad * 0.90,
            r.wheel_w * 0.66,
            rim=WheelRim(
                inner_radius=rad * 0.90 - max(0.026, rad * 0.085),
                flange_height=max(0.004, rad * 0.016),
                flange_thickness=0.003,
                bead_seat_depth=0.002,
            ),
            hub=WheelHub(radius=max(0.024, rad * 0.13), width=r.wheel_w, cap_style="flat"),
            face=WheelFace(dish_depth=0.003, front_inset=0.0015, rear_inset=0.0015),
            spokes=WheelSpokes(
                style="straight",
                count=8,
                thickness=max(0.0035, rad * 0.014),
                window_radius=max(0.007, rad * 0.026),
            ),
            bore=WheelBore(style="round", diameter=0.016),
        ),
        name,
    )


def _tire_mesh(r: ResolvedSeederConfig, name: str):
    rad = r.wheel_r
    return mesh_from_geometry(
        TireGeometry(
            rad,
            r.wheel_w,
            inner_radius=rad * 0.90,
            sidewall=TireSidewall(style="rounded", bulge=0.02),
        ),
        name,
    )


# ---------------------------------------------------------------------------
# Meter rotor forms (Slot A — CONTINUOUS +Y child, all captured on meter_shaft).
# Authored around the rotor-local origin; rotor axis = Y (hubs use rpy=(pi/2,0,0)).
# Every form emits a `meter_hub` (bearing on shaft) and a `meter_lug` motion marker.
# ---------------------------------------------------------------------------
def _emit_meter_hub(rotor, r, mats):
    # Length 0.060 > every rotor body width (<=0.046) so the hub protrudes past
    # the body end faces on both sides -> its side surface crosses those faces
    # (connected, no enclosed island) and gives the shaft a real bearing bore.
    rotor.visual(
        Cylinder(radius=max(0.013, r.meter_r * 0.32), length=0.060),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="meter_hub", material_class_id="metal.blackened_gunmetal",
    )


def _emit_meter_lug(rotor, r, mats):
    rr = r.meter_r * 0.92
    rotor.visual(
        Box((0.022, 0.016, 0.014)),
        origin=Origin(xyz=(rr, 0.0, 0.0)),
        material=mats["dark"],
        name="meter_lug", material_class_id="metal.blackened_gunmetal",
    )


def _build_meter_vane_paddle(rotor, r, mats, *, assets):
    # 002 L427-453: core cylinder + 8 radial box paddles.
    rotor.visual(
        Cylinder(radius=r.meter_r * 0.62, length=0.044),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="meter_core", material_class_id="metal.paint_coated",
    )
    _emit_meter_hub(rotor, r, mats)
    for i in range(8):
        a = 2.0 * math.pi * i / 8.0
        rr = r.meter_r * 0.86
        rotor.visual(
            Box((0.026, 0.042, 0.010)),
            origin=Origin(xyz=(rr * math.cos(a), 0.0, rr * math.sin(a)), rpy=(0.0, -a, 0.0)),
            material=mats["frame"],
            name=f"meter_paddle_{i}", material_class_id="metal.paint_coated",
        )
    _emit_meter_lug(rotor, r, mats)


def _build_meter_finger_paddle(rotor, r, mats, *, assets):
    # 001 L354-374: hub + 6 spoke fingers + paddle tips.
    rotor.visual(
        Cylinder(radius=r.meter_r * 0.52, length=0.020),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hopper"],
        name="meter_core", material_class_id="metal.paint_coated",
    )
    _emit_meter_hub(rotor, r, mats)
    for i in range(6):
        a = i * math.pi / 3.0
        rr = r.meter_r * 0.55
        rotor.visual(
            Box((r.meter_r * 1.05, 0.014, 0.009)),
            origin=Origin(xyz=(rr * math.cos(a), 0.0, rr * math.sin(a)), rpy=(0.0, -a, 0.0)),
            material=mats["dark"],
            name=f"meter_finger_{i}", material_class_id="metal.blackened_gunmetal",
        )
        rr2 = r.meter_r * 1.02
        rotor.visual(
            Box((0.016, 0.016, 0.016)),
            origin=Origin(xyz=(rr2 * math.cos(a), 0.0, rr2 * math.sin(a)), rpy=(0.0, -a, 0.0)),
            material=mats["hopper"],
            name=f"meter_tip_{i}", material_class_id="metal.paint_coated",
        )
    _emit_meter_lug(rotor, r, mats)


def _build_meter_pocket_plate(rotor, r, mats, *, assets):
    # 003 L384-409: flat seed-plate disc + hub + sphere seed pockets + lug.
    rotor.visual(
        Cylinder(radius=r.meter_r, length=0.012),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="meter_disk", material_class_id="metal.steel_bare",
    )
    _emit_meter_hub(rotor, r, mats)
    rr = r.meter_r * 0.62
    for i, a in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
        rotor.visual(
            Sphere(radius=0.011),
            origin=Origin(xyz=(rr * math.cos(a), -0.008, rr * math.sin(a))),
            material=mats["dark"],
            name=f"seed_pocket_{i}", material_class_id="metal.blackened_gunmetal",
        )
    _emit_meter_lug(rotor, r, mats)


def _build_meter_fluted_roller(rotor, r, mats, *, assets):
    # fork metering_fluted_roller: transverse roller + 10 rounded flutes.
    core_r = r.meter_r * 0.63
    flute_cr = r.meter_r * 0.70
    flute_r = r.meter_r * 0.155
    length = 0.046
    roller = cq.Workplane("XZ").circle(core_r).extrude(length / 2.0, both=True)
    for i in range(10):
        a = 2.0 * math.pi * i / 10.0
        flute = (
            cq.Workplane("XZ")
            .center(flute_cr * math.cos(a), flute_cr * math.sin(a))
            .circle(flute_r)
            .extrude(length / 2.0, both=True)
        )
        roller = roller.union(flute)
    rotor.visual(
        mesh_from_cadquery(roller, "seeder_fluted_roller", tolerance=0.0006, assets=assets),
        material=mats["steel"],
        name="fluted_roller", material_class_id="metal.steel_bare",
    )
    _emit_meter_hub(rotor, r, mats)
    _emit_meter_lug(rotor, r, mats)


def _build_meter_perforated_plate(rotor, r, mats, *, assets):
    # fork metering_perforated_seed_plate: cast plate with a ring of drilled holes.
    plate = cq.Workplane("XZ").circle(r.meter_r).extrude(0.007, both=True)
    hole_ring = r.meter_r * 0.66
    for i in range(10):
        a = 2.0 * math.pi * i / 10.0
        hole = (
            cq.Workplane("XZ")
            .center(hole_ring * math.cos(a), hole_ring * math.sin(a))
            .circle(r.meter_r * 0.12)
            .extrude(0.02, both=True)
        )
        plate = plate.cut(hole)
    rotor.visual(
        mesh_from_cadquery(plate, "seeder_perforated_plate", tolerance=0.0006, assets=assets),
        material=mats["steel"],
        name="perforated_plate", material_class_id="metal.patterned_sheet_panel",
    )
    _emit_meter_hub(rotor, r, mats)
    _emit_meter_lug(rotor, r, mats)


_METER_BUILDERS = {
    "vane_paddle": _build_meter_vane_paddle,
    "finger_paddle": _build_meter_finger_paddle,
    "pocket_plate": _build_meter_pocket_plate,
    "fluted_roller": _build_meter_fluted_roller,
    "perforated_plate": _build_meter_perforated_plate,
}


# ---------------------------------------------------------------------------
# Opener forms (Slot B — fixed inline visuals on chassis, per row). Each builder
# gets a prebuilt (or None) shared cadquery mesh geometry and places it at the
# lane. Meshes are tessellated once in build_seeder and reused across rows.
# ---------------------------------------------------------------------------
def _hoe_blade_solid() -> cq.Workplane:
    # 002 L74-88 furrow blade.
    return (
        cq.Workplane("XZ")
        .polyline([(-0.060, 0.155), (-0.020, 0.012), (0.040, 0.060), (0.030, 0.150)])
        .close()
        .extrude(0.026, both=True)
    )


def _forged_opener_solid() -> cq.Workplane:
    # 003 L70-88 forged furrow opener.
    return (
        cq.Workplane("XZ")
        .polyline(
            [
                (-0.030, 0.235),
                (0.030, 0.235),
                (0.073, 0.092),
                (0.102, 0.010),
                (0.052, 0.000),
                (0.006, 0.078),
            ]
        )
        .close()
        .extrude(0.022, both=True)
    )


def _runner_boot_solid() -> cq.Workplane:
    # fork runner_shoe: long low runner boot carrying the seed outlet.
    runner = (
        cq.Workplane("XZ")
        .polyline(
            [(-0.135, 0.012), (0.080, 0.012), (0.100, 0.030), (-0.095, 0.045), (-0.135, 0.070)]
        )
        .close()
        .extrude(0.032, both=True)
    )
    boot = cq.Workplane("XY").rect(0.056, 0.056).extrude(0.120).translate((0.018, 0.0, 0.030))
    void = cq.Workplane("XY").rect(0.034, 0.034).extrude(0.135).translate((0.018, 0.0, 0.022))
    return runner.union(boot).cut(void)


def _disc_solid() -> cq.Workplane:
    # fork double_disc: one dished opener disc (built once, placed twice toe-in).
    return (
        cq.Workplane("XY")
        .circle(0.088)
        .workplane(offset=0.0022)
        .circle(0.092)
        .workplane(offset=0.0022)
        .circle(0.088)
        .loft(combine=True)
        .rotate((0, 0, 0), (1, 0, 0), 90.0)
    )


def _build_opener_meshes(r: ResolvedSeederConfig, assets):
    """Tessellate the opener geometry ONCE; returned meshes are instanced per row."""
    f = r.opener_form
    if f == "hoe_shank":
        return {"blade": mesh_from_cadquery(_hoe_blade_solid(), "seeder_hoe_blade", tolerance=0.0007, assets=assets)}
    if f == "forged_shoe":
        return {"opener": mesh_from_cadquery(_forged_opener_solid(), "seeder_forged_opener", tolerance=0.0007, assets=assets)}
    if f == "runner_shoe":
        return {"boot": mesh_from_cadquery(_runner_boot_solid(), "seeder_runner_boot", tolerance=0.0008, assets=assets)}
    # double_disc
    return {"disc": mesh_from_cadquery(_disc_solid(), "seeder_opener_disc", tolerance=0.0007, assets=assets)}


def _emit_opener(chassis, r, mats, meshes, *, x0: float, row_y: float, i: int):
    """Inline the chosen soil tool for lane i. Top of the tool overlaps the chute
    bottom (z ~ 0.14) so it is welded to the connected chassis chain (no island)."""
    f = r.opener_form
    if f == "hoe_shank":
        chassis.visual(
            Box((0.036, 0.046, 0.170)),
            origin=Origin(xyz=(x0, row_y, 0.115)),
            material=mats["dark"],
            name=f"opener_shank_{i}", material_class_id="metal.blackened_gunmetal",
        )
        chassis.visual(
            meshes["blade"],
            origin=Origin(xyz=(x0, row_y, 0.010)),
            material=mats["steel"],
            name=f"furrow_blade_{i}", material_class_id="metal.steel_bare",
        )
        chassis.visual(
            Box((0.150, 0.048, 0.014)),
            origin=Origin(xyz=(x0 + 0.050, row_y, 0.040)),
            material=mats["steel"],
            name=f"covering_shoe_{i}", material_class_id="metal.steel_bare",
        )
    elif f == "forged_shoe":
        chassis.visual(
            Box((0.036, 0.046, 0.150)),
            origin=Origin(xyz=(x0, row_y, 0.150)),
            material=mats["frame"],
            name=f"opener_shank_{i}", material_class_id="metal.paint_coated",
        )
        chassis.visual(
            meshes["opener"],
            origin=Origin(xyz=(x0, row_y, 0.0)),
            material=mats["dark"],
            name=f"forged_opener_{i}", material_class_id="metal.blackened_gunmetal",
        )
        # trailing soil knife; overlaps the shank (fixed-z datum) so it stays
        # welded regardless of wheel_radius_scale (the toolbar z scales, this
        # doesn't -> anchor to the shank, not the toolbar).
        chassis.visual(
            Box((0.130, 0.030, 0.045)),
            origin=Origin(xyz=(x0 - 0.055, row_y, 0.130)),
            material=mats["steel"],
            name=f"soil_blade_{i}", material_class_id="metal.steel_bare",
        )
    elif f == "runner_shoe":
        chassis.visual(
            Box((0.040, 0.048, 0.150)),
            origin=Origin(xyz=(x0, row_y, 0.145)),
            material=mats["dark"],
            name=f"opener_shank_{i}", material_class_id="metal.blackened_gunmetal",
        )
        chassis.visual(
            meshes["boot"],
            origin=Origin(xyz=(x0, row_y, 0.0)),
            material=mats["dark"],
            name=f"runner_boot_{i}", material_class_id="metal.blackened_gunmetal",
        )
    else:  # double_disc
        # shank straddles both discs in Y (width 0.092 >= 2*disc offset) so the
        # discs weld to it (no island) and it reads as the disc hanger.
        chassis.visual(
            Box((0.036, 0.092, 0.170)),
            origin=Origin(xyz=(x0, row_y, 0.185)),
            material=mats["frame"],
            name=f"opener_shank_{i}", material_class_id="metal.paint_coated",
        )
        for side, dy, toe in ((0, -0.034, 8.0), (1, 0.034, -8.0)):
            chassis.visual(
                meshes["disc"],
                origin=Origin(xyz=(x0, row_y + dy, 0.092), rpy=(0.0, 0.0, math.radians(toe))),
                material=mats["steel"],
                name=f"opener_disc_{i}_{side}", material_class_id="metal.steel_bare",
            )


# ---------------------------------------------------------------------------
# Chassis (root) — rails, crossmembers, axle(s), lanes, meter mount, handles,
# depth pivot, drive detail. Returns wheel joint origins for the caller.
# ---------------------------------------------------------------------------
def _emit_chassis(model, r, mats, opener_meshes, *, assets):
    chassis = model.part("chassis")
    beam_z = r.beam_z

    # extent of the chassis in X depends on the wheel layout.
    if r.wheel_layout == "tandem":
        rail_x0, rail_x1 = r.rear_x - 0.06, r.front_x + 0.06
    else:
        rail_x0, rail_x1 = -0.34, r.axle_x + 0.07
    rail_cx = 0.5 * (rail_x0 + rail_x1)
    rail_len = rail_x1 - rail_x0

    # two longitudinal side rails.
    for s, sign in enumerate((-1.0, 1.0)):
        chassis.visual(
            Box((rail_len, _RAIL_W, _RAIL_H)),
            origin=Origin(xyz=(rail_cx, sign * _RAIL_Y, beam_z)),
            material=mats["frame"],
            name=f"side_rail_{s}", material_class_id="metal.paint_coated",
        )
    # transverse crossmembers tying the rails (span full width). Kept in the
    # central x-band so they never intersect the wheels (back-reach >= 0.20).
    cross_w = 2 * _RAIL_Y + _RAIL_W
    cross_xs = (-0.10, 0.02, 0.12)
    for i, cx in enumerate(cross_xs):
        chassis.visual(
            Box((0.060, cross_w, _RAIL_H)),
            origin=Origin(xyz=(cx, 0.0, beam_z)),
            material=mats["frame"],
            name=f"crossmember_{i}", material_class_id="metal.paint_coated",
        )

    # ---- wheels + axles (Slot C). The transverse axle ends inside both rails
    # (support) and passes through the wheel hub (captured pin, allow_overlap).
    # No separate bracket -> no box intruding on the wheel disc. ----
    if r.wheel_layout == "tandem":
        wheel_origins = [(r.front_x, 0.0, r.wheel_r), (r.rear_x, 0.0, r.wheel_r)]
        for i, (wx, _, wz) in enumerate(wheel_origins):
            chassis.visual(
                Cylinder(radius=0.010, length=2 * _RAIL_Y + _RAIL_W),
                origin=Origin(xyz=(wx, 0.0, wz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["steel"],
                name=f"axle_{i}", material_class_id="metal.steel_bare",
            )
    else:
        wheel_origins = [
            (r.axle_x, -r.side_wheel_y, r.wheel_r),
            (r.axle_x, r.side_wheel_y, r.wheel_r),
        ]
        chassis.visual(
            Cylinder(radius=0.010, length=2 * r.side_wheel_y + _RAIL_W),
            origin=Origin(xyz=(r.axle_x, 0.0, r.wheel_r), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["steel"],
            name="axle_0", material_class_id="metal.steel_bare",
        )

    # ---- seeding lanes (row multiplicity). Each lane is a connected vertical
    # chain rooted on the central crossmember: mast -> hopper -> throat -> chute
    # -> opener. Hopper mesh is instanced (same geometry) across lanes. ----
    hopper_mesh = mesh_from_cadquery(_hopper_solid(r), "seeder_hopper_shell", tolerance=0.0009, assets=assets)
    n = r.row_count
    y0 = -0.5 * (n - 1) * r.row_spacing
    hopper_x = -0.02
    opener_x = 0.03
    # Full-width transverse toolbar: every lane mast sits on it, and it overlaps
    # the central crossmember, so all lanes join the connected chassis tree for
    # any row_count (2_row fork L283-290 `row_toolbar`).
    row_span_y = (n - 1) * r.row_spacing + 2 * r.hopper_half_y + 0.06
    chassis.visual(
        Box((0.090, row_span_y, _RAIL_H)),
        origin=Origin(xyz=(hopper_x, 0.0, beam_z)),
        material=mats["frame"],
        name="row_toolbar", material_class_id="metal.paint_coated",
    )
    for i in range(n):
        row_y = y0 + i * r.row_spacing
        # mast from crossmember up to hopper floor.
        chassis.visual(
            Box((0.075, 0.085, _HOPPER_BASE_DZ + 0.03)),
            origin=Origin(xyz=(hopper_x, row_y, beam_z + _HOPPER_BASE_DZ / 2.0)),
            material=mats["frame"],
            name=f"lane_mast_{i}", material_class_id="metal.paint_coated",
        )
        chassis.visual(
            hopper_mesh,
            origin=Origin(xyz=(hopper_x, row_y, r.hopper_base_z)),
            material=mats["hopper"],
            name=f"hopper_{i}", material_class_id="metal.paint_coated",
        )
        # seed throat + chute descending to the opener.
        chassis.visual(
            _tube(
                [
                    (hopper_x, row_y, r.hopper_base_z + 0.02),
                    (-0.005, row_y, beam_z + 0.06),
                    (opener_x, row_y, 0.15),
                ],
                0.017,
                f"seed_chute_{i}",
                assets,
            ),
            material=mats["dark"],
            name=f"seed_chute_{i}", material_class_id="metal.blackened_gunmetal",
        )
        _emit_opener(chassis, r, mats, opener_meshes, x0=opener_x, row_y=row_y, i=i)

    # Lateral span of the seeding lanes; the meter and lever mounts sit OUTBOARD
    # of the outer lane (in Y) and BEHIND the hopper masts (x=-0.13), so they
    # never intersect a lane for any row_count.
    half_span = 0.5 * (n - 1) * r.row_spacing

    # ---- meter mount: two cheek plates straddling the side-mounted rotor, an
    # arm to the near (-Y) rail, and the captured transverse shaft. ----
    meter_x = -0.13
    meter_z = beam_z + 0.06
    inner_cheek_y = -(half_span + r.hopper_half_y + 0.07)
    outer_cheek_y = inner_cheek_y - 0.09
    rotor_y = inner_cheek_y - 0.045
    for i, cy in enumerate((inner_cheek_y, outer_cheek_y)):
        chassis.visual(
            Box((0.11, 0.012, 0.12)),
            origin=Origin(xyz=(meter_x, cy, meter_z)),
            material=mats["frame"],
            name=f"meter_cheek_{i}", material_class_id="metal.paint_coated",
        )
    # arm tying the inner cheek in to the near rail (spans the outboard gap).
    arm_lo, arm_hi = inner_cheek_y - 0.01, -(_RAIL_Y - 0.02)
    chassis.visual(
        Box((0.05, arm_hi - arm_lo, 0.08)),
        origin=Origin(xyz=(meter_x, 0.5 * (arm_lo + arm_hi), beam_z + 0.005)),
        material=mats["frame"],
        name="meter_arm", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        Cylinder(radius=0.007, length=0.13),
        origin=Origin(xyz=(meter_x, rotor_y, meter_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="meter_shaft", material_class_id="metal.steel_bare",
    )
    meter_origin = (meter_x, rotor_y, meter_z)

    # ---- depth pivot: long transverse pin on the far (+Y) side, held by an arm
    # to the +Y rail; the lever sleeve captures the pin's outboard end. ----
    lever_x = -0.13
    lever_z = beam_z + 0.06
    lever_ref = half_span + r.hopper_half_y + 0.07
    larm_lo, larm_hi = _RAIL_Y - 0.02, lever_ref - 0.02
    chassis.visual(
        Box((0.05, larm_hi - larm_lo, 0.09)),
        origin=Origin(xyz=(lever_x, 0.5 * (larm_lo + larm_hi), beam_z + 0.015)),
        material=mats["frame"],
        name="depth_arm", material_class_id="metal.paint_coated",
    )
    chassis.visual(
        Cylinder(radius=0.012, length=0.10),
        origin=Origin(xyz=(lever_x, lever_ref - 0.02, lever_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="depth_pivot", material_class_id="metal.steel_bare",
    )
    lever_origin = (lever_x, lever_ref, lever_z)

    # ---- twin bent push handles + grips + tie (trailing to -X, rising in Z). ----
    handle_base_x = rail_x0 + 0.10
    tip_x = rail_x0 - 0.32
    tip_z = beam_z + r.handle_rise
    for s, sign in enumerate((-1.0, 1.0)):
        hy = sign * _RAIL_Y
        chassis.visual(
            _tube(
                [
                    (handle_base_x, hy, beam_z),
                    (handle_base_x - 0.18, hy, beam_z + 0.35 * r.handle_rise),
                    (tip_x + 0.10, hy, beam_z + 0.80 * r.handle_rise),
                    (tip_x, hy, tip_z),
                ],
                0.013,
                f"handle_rail_{s}",
                assets,
            ),
            material=mats["frame"],
            name=f"handle_rail_{s}", material_class_id="metal.paint_coated",
        )
        chassis.visual(
            _tube(
                [(tip_x, hy, tip_z), (tip_x - 0.06, hy, tip_z + 0.02)],
                0.016,
                f"handle_grip_{s}",
                assets,
            ),
            material=mats["grip"],
            name=f"handle_grip_{s}", material_class_id="rubber.smooth_plain",
        )
    chassis.visual(
        Cylinder(radius=0.013, length=2 * _RAIL_Y),
        origin=Origin(xyz=(tip_x + 0.02, 0.0, tip_z - 0.01), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="handle_tie", material_class_id="metal.paint_coated",
    )

    # ---- drive detail (④): host-conformal dressing welded on the outer meter
    # cheek (outboard + behind masts -> always clear of the lanes). ----
    if r.drive_detail == "chain_guard":
        chassis.visual(
            _tube(
                [
                    (meter_x + 0.03, outer_cheek_y, meter_z - 0.03),
                    (meter_x - 0.05, outer_cheek_y, meter_z - 0.10),
                    (meter_x - 0.11, outer_cheek_y, meter_z - 0.14),
                ],
                0.008,
                "meter_drive_guard",
                assets,
            ),
            material=mats["accent"],
            name="drive_detail", material_class_id="metal.paint_coated",
        )
    elif r.drive_detail == "belt_cover":
        chassis.visual(
            Box((0.11, 0.010, 0.11)),
            origin=Origin(xyz=(meter_x, outer_cheek_y - 0.010, meter_z)),
            material=mats["accent"],
            name="drive_detail", material_class_id="metal.paint_coated",
        )
    else:  # direct_pin
        chassis.visual(
            Cylinder(radius=0.010, length=0.05),
            origin=Origin(
                xyz=(meter_x, outer_cheek_y - 0.03, meter_z), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["accent"],
            name="drive_detail", material_class_id="metal.paint_coated",
        )

    chassis.inertial = Inertial.from_geometry(
        Box((rail_len, 2 * _RAIL_Y + 0.1, beam_z + r.handle_rise)),
        mass=14.0,
        origin=Origin(xyz=(rail_cx, 0.0, 0.5 * (beam_z + r.handle_rise))),
    )
    return chassis, wheel_origins, meter_origin, lever_origin


def _emit_wheel(model, r, mats, name: str):
    wheel = model.part(name)
    wheel.visual(
        _wheel_mesh(r, f"{name}_spoked"),
        origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["wheel"],
        name="spoked_wheel", material_class_id="metal.paint_coated",
    )
    wheel.visual(
        _tire_mesh(r, f"{name}_tire"),
        origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)),
        material=mats["tire"],
        name="tire", material_class_id="rubber.directional_grooved",
    )
    # small drive pin makes rotation legible + is the motion-test marker.
    wheel.visual(
        Cylinder(radius=0.006, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, r.wheel_r * 0.78), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="drive_pin", material_class_id="metal.blackened_gunmetal",
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_r, length=r.wheel_w),
        mass=1.4,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    return wheel


def _emit_depth_lever(model, r, mats, *, assets):
    lever = model.part("depth_lever")
    lever.visual(
        Cylinder(radius=0.017, length=0.030),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="lever_sleeve", material_class_id="metal.blackened_gunmetal",
    )
    lever.visual(
        _tube(
            [(0.0, 0.0, 0.0), (-0.03, 0.0, 0.08), (0.0, 0.0, 0.155)],
            0.008,
            "seeder_depth_arm",
            assets,
        ),
        material=mats["frame"],
        name="lever_arm", material_class_id="metal.paint_coated",
    )
    lever.visual(
        Sphere(radius=0.015),
        origin=Origin(xyz=(0.0, 0.0, 0.155)),
        material=mats["grip"],
        name="lever_grip", material_class_id="rubber.smooth_plain",
    )
    lever.inertial = Inertial.from_geometry(
        Box((0.12, 0.03, 0.18)),
        mass=0.25,
        origin=Origin(xyz=(-0.01, 0.0, 0.08)),
    )
    return lever


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_seeder(
    config: SeederConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"seeder_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    opener_meshes = _build_opener_meshes(r, assets)
    chassis, wheel_origins, meter_origin, lever_origin = _emit_chassis(
        model, r, mats, opener_meshes, assets=assets
    )

    # ---- wheels (Slot C) ----
    wheel_a = _emit_wheel(model, r, mats, "wheel_a")
    wheel_b = _emit_wheel(model, r, mats, "wheel_b")
    for wheel, name, origin in (
        (wheel_a, "wheel_a_spin", wheel_origins[0]),
        (wheel_b, "wheel_b_spin", wheel_origins[1]),
    ):
        model.articulation(
            name,
            ArticulationType.CONTINUOUS,
            parent=chassis,
            child=wheel,
            origin=Origin(xyz=origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=20.0),
        )

    # ---- metering rotor (Slot A) ----
    meter_rotor = model.part("meter_rotor")
    _METER_BUILDERS[r.meter_form](meter_rotor, r, mats, assets=assets)
    model.articulation(
        "meter_spin",
        ArticulationType.CONTINUOUS,
        parent=chassis,
        child=meter_rotor,
        origin=Origin(xyz=meter_origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=10.0),
    )

    # ---- depth lever (REVOLUTE) ----
    depth_lever = _emit_depth_lever(model, r, mats, assets=assets)
    model.articulation(
        "depth_adjust",
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=depth_lever,
        origin=Origin(xyz=lever_origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=1.5, lower=r.depth_lower, upper=r.depth_upper
        ),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_seeder(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_seeder(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_seeder_tests(object_model: ArticulatedObject, config: SeederConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    chassis = object_model.get_part("chassis")
    wheel_a = object_model.get_part("wheel_a")
    wheel_b = object_model.get_part("wheel_b")
    meter_rotor = object_model.get_part("meter_rotor")
    depth_lever = object_model.get_part("depth_lever")

    # ---- captured-pin allowances (element-scoped, mirroring the anchors). ----
    axle_a = "axle_0"
    axle_b = "axle_0" if r.wheel_layout == "side_by_side" else "axle_1"
    for wheel, axle in ((wheel_a, axle_a), (wheel_b, axle_b)):
        ctx.allow_overlap(
            wheel,
            chassis,
            elem_a="spoked_wheel",
            elem_b=axle,
            reason="The wheel hub is intentionally captured on its fixed axle.",
        )
    # The transverse shaft passes through the rotor center, grazing every hub /
    # core / radial-arm root; the pivot pin threads the lever sleeve + arm root.
    # Scope the captured-pin allowance to each child element vs that one shaft/pin.
    for v in meter_rotor.visuals:
        ctx.allow_overlap(
            meter_rotor,
            chassis,
            elem_a=v.name,
            elem_b="meter_shaft",
            reason="The metering rotor is captured on the fixed transverse shaft.",
        )
    for v in depth_lever.visuals:
        ctx.allow_overlap(
            depth_lever,
            chassis,
            elem_a=v.name,
            elem_b="depth_pivot",
            reason="The depth lever pivots on a captured steel pin.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- topology: source-locked single skeleton (5 parts / 4 joints). ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "single source-locked skeleton (chassis + 2 wheels + meter + lever)",
        part_names == {"chassis", "wheel_a", "wheel_b", "meter_rotor", "depth_lever"},
        details=str(sorted(part_names)),
    )
    joints = {j.name: j for j in object_model.articulations}
    ctx.check(
        "four joints: 3 CONTINUOUS +Y + 1 REVOLUTE +Y",
        set(joints) == {"wheel_a_spin", "wheel_b_spin", "meter_spin", "depth_adjust"}
        and all(
            joints[n].articulation_type == ArticulationType.CONTINUOUS
            for n in ("wheel_a_spin", "wheel_b_spin", "meter_spin")
        )
        and joints["depth_adjust"].articulation_type == ArticulationType.REVOLUTE
        and all(tuple(j.axis) == (0.0, 1.0, 0.0) for j in joints.values()),
        details=str({n: (j.articulation_type, tuple(j.axis)) for n, j in joints.items()}),
    )
    ctx.check(
        "depth lever has bounded travel",
        joints["depth_adjust"].motion_limits is not None
        and joints["depth_adjust"].motion_limits.lower < 0 < joints["depth_adjust"].motion_limits.upper,
        details=str(joints["depth_adjust"].motion_limits),
    )

    # ---- N seeding lanes inlined on chassis (Rule 1, no joints). ----
    hoppers = [v.name for v in chassis.visuals if v.name.startswith("hopper_")]
    ctx.check(
        "N hopper lanes inlined on chassis",
        len(hoppers) == r.row_count,
        details=f"hoppers={sorted(hoppers)} expected N={r.row_count}",
    )

    # ---- wheels near the ground (support sanity). ----
    for name, wheel in (("wheel_a", wheel_a), ("wheel_b", wheel_b)):
        box = ctx.part_world_aabb(wheel)
        if box is not None:
            ctx.check(f"{name} rests on the soil plane", box[0][2] < 0.02, details=f"z_min={box[0][2]:.4f}")

    # ---- Rule 5: dynamic collision across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- targeted motion per mechanism. ----
    def _center(part, elem):
        aabb = ctx.part_element_world_aabb(part, elem=elem)
        return None if aabb is None else tuple((aabb[0][i] + aabb[1][i]) * 0.5 for i in range(3))

    for name, wheel in (("wheel_a_spin", wheel_a), ("wheel_b_spin", wheel_b)):
        rest = _center(wheel, "drive_pin")
        with ctx.pose({name: math.pi / 2.0}):
            turned = _center(wheel, "drive_pin")
        ctx.check(
            f"{name} rotates the wheel",
            rest is not None
            and turned is not None
            and (abs(turned[0] - rest[0]) > 0.05 or abs(turned[2] - rest[2]) > 0.05),
            details=f"rest={rest} turned={turned}",
        )

    m_rest = _center(meter_rotor, "meter_lug")
    with ctx.pose({"meter_spin": math.pi / 2.0}):
        m_turn = _center(meter_rotor, "meter_lug")
    ctx.check(
        "meter rotor rotates",
        m_rest is not None
        and m_turn is not None
        and (abs(m_turn[0] - m_rest[0]) > 0.02 or abs(m_turn[2] - m_rest[2]) > 0.02),
        details=f"rest={m_rest} turned={m_turn}",
    )

    with ctx.pose({"depth_adjust": r.depth_lower}):
        g_lo = _center(depth_lever, "lever_grip")
    with ctx.pose({"depth_adjust": r.depth_upper}):
        g_hi = _center(depth_lever, "lever_grip")
    ctx.check(
        "depth lever sweeps a visible arc",
        g_lo is not None and g_hi is not None and abs(g_hi[0] - g_lo[0]) > 0.03,
        details=f"low={g_lo} high={g_hi}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SeederConfig",
    "ResolvedSeederConfig",
    "build_seeder",
    "build_seeded_seeder",
    "config_from_seed",
    "resolve_config",
    "run_seeder_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
