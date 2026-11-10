# SPDX-License-Identifier: Apache-2.0

"""Modular template for category `music_stand1` — adjustable sheet-music stand.

Slot graph (linear chain):

    base_form -> [height_stages: N x PRISMATIC(+Z) stages, per-stage lock knob] -> desk_form (REVOLUTE +X)

Slots:
  * ``base_form``: round_pedestal | folding_tripod | weighted_wide_disk
  * ``desk_form``: solid_tray | perforated_panel | wire_frame | split_folding_leaves
  * ``height_stages``: 1 | 2 | 3 telescoping prismatic stages (multiplicity axis).
  * ``palette_style``: matte_black_walnut | all_black_steel | dark_hardware_wood
    | industrial_gray.

Sources: origin 001 (S1) / 002 (S2) / 003 (S3) + 7 forked variants under
``data/records/rec_0611_music_stand1_var_*``.
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
    Box,
    Cylinder,
    ExtrudeWithHolesGeometry,
    Inertial,
    KnobGeometry,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

BaseForm = Literal["round_pedestal", "folding_tripod", "weighted_wide_disk"]
DeskForm = Literal["solid_tray", "perforated_panel", "wire_frame", "split_folding_leaves"]
PaletteStyle = Literal[
    "matte_black_walnut",
    "all_black_steel",
    "dark_hardware_wood",
    "industrial_gray",
]

BASE_FORMS: tuple[BaseForm, ...] = (
    "round_pedestal",
    "folding_tripod",
    "weighted_wide_disk",
)
DESK_FORMS: tuple[DeskForm, ...] = (
    "solid_tray",
    "perforated_panel",
    "wire_frame",
    "split_folding_leaves",
)
PALETTES_KEYS: tuple[PaletteStyle, ...] = (
    "matte_black_walnut",
    "all_black_steel",
    "dark_hardware_wood",
    "industrial_gray",
)

N_STAGES_MIN = 1
N_STAGES_MAX = 3
N_STAGES_WEIGHTS = (0.30, 0.45, 0.25)  # N=1, N=2, N=3


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_black_walnut": {
        "base": (0.035, 0.035, 0.038, 1.0),
        "column": (0.045, 0.045, 0.050, 1.0),
        "hardware": (0.19, 0.19, 0.20, 1.0),
        "accent": (0.38, 0.19, 0.16, 1.0),
        "rubber": (0.018, 0.018, 0.020, 1.0),
        "desk": (0.43, 0.205, 0.105, 1.0),
        "desk_dark": (0.235, 0.095, 0.045, 1.0),
    },
    "all_black_steel": {
        "base": (0.025, 0.028, 0.032, 1.0),
        "column": (0.030, 0.030, 0.035, 1.0),
        "hardware": (0.055, 0.058, 0.064, 1.0),
        "accent": (0.070, 0.070, 0.075, 1.0),
        "rubber": (0.018, 0.019, 0.022, 1.0),
        "desk": (0.030, 0.030, 0.035, 1.0),
        "desk_dark": (0.055, 0.058, 0.064, 1.0),
    },
    "dark_hardware_wood": {
        "base": (0.045, 0.050, 0.055, 1.0),
        "column": (0.070, 0.070, 0.078, 1.0),
        "hardware": (0.095, 0.105, 0.115, 1.0),
        "accent": (0.140, 0.100, 0.070, 1.0),
        "rubber": (0.012, 0.014, 0.016, 1.0),
        "desk": (0.36, 0.22, 0.12, 1.0),
        "desk_dark": (0.20, 0.10, 0.05, 1.0),
    },
    "industrial_gray": {
        "base": (0.28, 0.29, 0.30, 1.0),
        "column": (0.32, 0.33, 0.34, 1.0),
        "hardware": (0.18, 0.19, 0.20, 1.0),
        "accent": (0.42, 0.44, 0.46, 1.0),
        "rubber": (0.020, 0.020, 0.022, 1.0),
        "desk": (0.24, 0.25, 0.26, 1.0),
        "desk_dark": (0.14, 0.15, 0.16, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MusicStand1Config:
    base_form: BaseForm | None = None
    desk_form: DeskForm | None = None
    height_stages: int | None = None
    palette_style: PaletteStyle | None = None
    desk_width_scale: float = 1.0
    desk_height_scale: float = 1.0
    column_length_scale: float = 1.0
    stage_travel_scale: float = 1.0
    base_scale: float = 1.0
    tilt_range: float = 0.42
    name: str = "music_stand1"
    seed: int = 0


@dataclass(frozen=True)
class ResolvedMusicStand1Config:
    base_form: BaseForm
    desk_form: DeskForm
    height_stages: int
    palette_style: PaletteStyle
    desk_width_scale: float
    desk_height_scale: float
    column_length_scale: float
    stage_travel_scale: float
    base_scale: float
    tilt_range: float
    # Concrete derived (single source of truth):
    base_top_z: float  # z at which the outermost tube ends (top of base collar)
    stage_length: float  # length of each telescoping stage
    stage_travel: float  # PRISMATIC upper limit per stage
    stage_outer_r0: float  # outermost tube outer radius
    tube_wall: float  # wall thickness for annular tubes
    lock_offset: float  # distance from stage tube center to lock stem center
    desk_width: float
    desk_height: float
    desk_thickness: float
    name: str
    seed: int


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> MusicStand1Config:
    rng = random.Random(seed)
    return MusicStand1Config(
        base_form=rng.choice(BASE_FORMS),
        desk_form=rng.choice(DESK_FORMS),
        height_stages=rng.choices((1, 2, 3), weights=N_STAGES_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTES_KEYS),
        desk_width_scale=round(rng.uniform(0.90, 1.12), 4),
        desk_height_scale=round(rng.uniform(0.90, 1.12), 4),
        column_length_scale=round(rng.uniform(0.90, 1.12), 4),
        stage_travel_scale=round(rng.uniform(0.88, 1.08), 4),
        base_scale=round(rng.uniform(0.92, 1.12), 4),
        tilt_range=round(rng.uniform(0.34, 0.48), 4),
        name=f"seeded_music_stand1_{seed}",
        seed=seed,
    )


def resolve_config(
    config: MusicStand1Config | ResolvedMusicStand1Config | None = None,
) -> ResolvedMusicStand1Config:
    if isinstance(config, ResolvedMusicStand1Config):
        return config
    cfg = config or MusicStand1Config()
    palette = _pick(cfg.palette_style, PALETTES_KEYS)
    base_form = _pick(cfg.base_form, BASE_FORMS)
    desk_form = _pick(cfg.desk_form, DESK_FORMS)
    n = int(cfg.height_stages) if cfg.height_stages is not None else 2
    n = int(_clamp(n, N_STAGES_MIN, N_STAGES_MAX))

    dw = _clamp(cfg.desk_width_scale, 0.85, 1.15)
    dh = _clamp(cfg.desk_height_scale, 0.85, 1.15)
    cls_ = _clamp(cfg.column_length_scale, 0.85, 1.15)
    sts = _clamp(cfg.stage_travel_scale, 0.85, 1.10)
    bs = _clamp(cfg.base_scale, 0.88, 1.15)
    tilt = _clamp(cfg.tilt_range, 0.28, 0.50)

    # Column geometry: base outer tube top ends at base_top_z; each stage adds
    # a shorter stage above.
    base_top_z = 0.620 * cls_
    stage_length = 0.560 * cls_  # length of each stage tube
    # Retention overlap must be >= 0.055 m; travel <= stage_length - 0.055 - epsilon.
    max_travel = max(0.04, stage_length - 0.075)
    stage_travel = _clamp(0.180 * sts, 0.06, max_travel)

    stage_outer_r0 = 0.0115  # matches S1 outer_tube outer radius; child stages are thinner
    tube_wall = 0.0025

    # Lock knob sits radially at collar edge + a small offset. Y-negative side.
    # Chosen so the stem visibly overlaps the collar rim (captured pin).
    lock_offset = 0.014

    # Desk geometry (rounded plate). S1 baseline 0.460 x 0.330.
    desk_width = 0.460 * dw
    desk_height = 0.330 * dh
    desk_thickness = 0.014

    return ResolvedMusicStand1Config(
        base_form=base_form,
        desk_form=desk_form,
        height_stages=n,
        palette_style=palette,
        desk_width_scale=dw,
        desk_height_scale=dh,
        column_length_scale=cls_,
        stage_travel_scale=sts,
        base_scale=bs,
        tilt_range=tilt,
        base_top_z=base_top_z,
        stage_length=stage_length,
        stage_travel=stage_travel,
        stage_outer_r0=stage_outer_r0,
        tube_wall=tube_wall,
        lock_offset=lock_offset,
        desk_width=desk_width,
        desk_height=desk_height,
        desk_thickness=desk_thickness,
        name=cfg.name or "music_stand1",
        seed=cfg.seed,
    )


def slot_choices_for_config(
    config: MusicStand1Config | ResolvedMusicStand1Config,
) -> tuple[tuple[str, str], ...]:
    r = resolve_config(config)
    return (
        ("base_form", r.base_form),
        ("desk_form", r.desk_form),
        ("height_stages", f"n{r.height_stages}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _annular_tube(inner_r: float, outer_r: float, z_min: float, z_max: float) -> LatheGeometry:
    return LatheGeometry(
        [
            (inner_r, z_min),
            (outer_r, z_min),
            (outer_r, z_max),
            (inner_r, z_max),
        ],
        segments=40,
        closed=True,
    )


def _shift_profile(profile, dx, dy):
    return [(x + dx, y + dy) for x, y in profile]


def _desk_plate_geometry(width: float, height: float, thickness: float) -> ExtrudeWithHolesGeometry:
    outer = rounded_rect_profile(width, height, min(0.034, height * 0.10), corner_segments=10)
    slot = rounded_rect_profile(width * 0.36, 0.011, 0.0055, corner_segments=8)
    plate = ExtrudeWithHolesGeometry(
        outer,
        [
            _shift_profile(slot, 0.0, -height * 0.10),
            _shift_profile(slot, 0.0, height * 0.10),
        ],
        thickness,
        center=True,
    )
    return plate.rotate_x(math.pi / 2.0)


def _perforated_panel_geometry(
    width: float, height: float, thickness: float
) -> ExtrudeWithHolesGeometry:
    outer = rounded_rect_profile(width, height, 0.012, corner_segments=10)
    holes = []
    # Rows of slots
    rows = 4
    cols = 6
    slot_w = width / (cols + 3) * 1.4
    slot_h = height / (rows + 6) * 1.5
    for r_i in range(rows):
        z = -height * 0.35 + (r_i + 0.5) * (height * 0.72 / rows)
        row_offset = (slot_w * 0.5) if (r_i % 2) else 0.0
        for c in range(cols):
            x = -width * 0.4 + (c + 0.5) * (width * 0.80 / cols) + row_offset - slot_w * 0.5
            if abs(x) > width * 0.42:
                continue
            slot = rounded_rect_profile(
                slot_w, slot_h, min(slot_h, slot_w) * 0.35, corner_segments=6
            )
            holes.append(_shift_profile(slot, x, z))
    plate = ExtrudeWithHolesGeometry(outer, holes, thickness, center=True)
    return plate.rotate_x(math.pi / 2.0)


# ---------------------------------------------------------------------------
# Base builders
# ---------------------------------------------------------------------------
def _build_round_pedestal(model, r: ResolvedMusicStand1Config, mats) -> None:
    base = model.part("base")
    disc_r = 0.151 * r.base_scale
    disc_h = 0.065 * r.base_scale
    weighted_base = LatheGeometry(
        [
            (0.000, 0.006),
            (disc_r * 0.875, 0.006),
            (disc_r, 0.012),
            (disc_r * 1.0, 0.024),
            (disc_r * 0.94, 0.040),
            (disc_r * 0.74, 0.055),
            (disc_r * 0.22, disc_h),
            (0.000, disc_h),
        ],
        segments=48,
        closed=True,
    )
    base.visual(
        mesh_from_geometry(weighted_base, "weighted_base"),
        material=mats["base"],
        name="weighted_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
    )
    base.visual(
        Cylinder(radius=disc_r * 0.875, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["rubber"],
        name="rubber_foot", material_class_id="rubber.smooth_plain",
    )
    _emit_column_socket_and_outer_tube(base, r, mats, socket_z0=disc_h)
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=disc_r, length=disc_h),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, disc_h / 2.0)),
    )


def _build_weighted_wide_disk(model, r: ResolvedMusicStand1Config, mats) -> None:
    base = model.part("base")
    disc_r = 0.185 * r.base_scale
    disc_h = 0.048 * r.base_scale
    weighted_base = LatheGeometry(
        [
            (0.000, 0.006),
            (disc_r * 0.9, 0.006),
            (disc_r, 0.014),
            (disc_r, 0.030),
            (disc_r * 0.90, disc_h),
            (0.000, disc_h),
        ],
        segments=48,
        closed=True,
    )
    base.visual(
        mesh_from_geometry(weighted_base, "wide_weighted_base"),
        material=mats["base"],
        name="weighted_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
    )
    base.visual(
        Cylinder(radius=disc_r * 0.90, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
        material=mats["rubber"],
        name="rubber_foot", material_class_id="rubber.smooth_plain",
    )
    _emit_column_socket_and_outer_tube(base, r, mats, socket_z0=disc_h)
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=disc_r, length=disc_h),
        mass=5.0,
        origin=Origin(xyz=(0.0, 0.0, disc_h / 2.0)),
    )


def _build_folding_tripod(model, r: ResolvedMusicStand1Config, mats) -> None:
    base = model.part("base")
    hub_r = 0.038 * r.base_scale
    hub_h = 0.060
    hub_z = 0.150
    base.visual(
        Cylinder(radius=hub_r, length=hub_h),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=mats["base"],
        name="tripod_hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
    )
    # Small skirt above the hub so the outer tube socket welds to real geometry.
    base.visual(
        Cylinder(radius=0.024, length=0.036),
        origin=Origin(xyz=(0.0, 0.0, hub_z + hub_h / 2.0 + 0.018)),
        material=mats["hardware"],
        name="post_socket", material_class_id="metal.blackened_gunmetal",
    )
    # Leg bracket cheeks.
    leg_azimuths = (0.0, 2.0 * math.pi / 3.0, 4.0 * math.pi / 3.0)
    for i, az in enumerate(leg_azimuths):
        c = math.cos(az)
        s = math.sin(az)
        # Two clevis cheeks straddling the hinge pin axis.
        for side, tangent in enumerate((-0.014, 0.014)):
            base.visual(
                Box((0.028, 0.006, 0.028)),
                origin=Origin(
                    xyz=(hub_r * c - s * tangent, hub_r * s + c * tangent, hub_z),
                    rpy=(0.0, 0.0, az),
                ),
                material=mats["hardware"],
                name=f"leg_bracket_{i}_{side}", material_class_id="metal.blackened_gunmetal",
            )
    # Column outer tube starts at the top of the hub.
    _emit_column_socket_and_outer_tube(base, r, mats, socket_z0=hub_z + hub_h / 2.0 + 0.036)
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=hub_r, length=hub_h),
        mass=0.7,
        origin=Origin(xyz=(0.0, 0.0, hub_z + hub_h / 2.0)),
    )
    # Legs.
    for i, az in enumerate(leg_azimuths):
        leg = model.part(f"tripod_leg_{i}")
        # Hinge barrel (local X = pin axis after joint rpy).
        leg.visual(
            Cylinder(radius=0.008, length=0.028),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"],
            name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
        )
        # Leg tube extends radially outward and down: from the hinge origin
        # (0,0,0) to (end_x, 0, end_z). We author the tube starting slightly
        # embedded in the hinge_barrel so it welds.
        leg_len = 0.42 * r.base_scale
        end_x = leg_len * math.cos(0.60)
        end_z = -leg_len * math.sin(0.60)
        # Nudge the tube start outward (leg-local +X) so it exits the hub cleanly
        # after the yaw rotation (adjacent legs otherwise dip into the hub curve).
        start_x = 0.020
        start_z = 0.0
        mid_x = (start_x + end_x) / 2.0
        mid_z = (start_z + end_z) / 2.0
        # Cylinder/Box default long axis is Z; rotate about Y so length points
        # from origin toward the end point.
        pitch = math.atan2(end_x - start_x, end_z - start_z)
        leg.visual(
            Box((0.012, 0.010, leg_len)),
            origin=Origin(xyz=(mid_x, 0.0, mid_z), rpy=(0.0, pitch, 0.0)),
            material=mats["base"],
            name="leg_tube", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
        )
        # Foot at the end, overlapping the leg tube end so it stays connected.
        leg.visual(
            Sphere(radius=0.014),
            origin=Origin(xyz=(end_x, 0.0, end_z)),
            material=mats["rubber"],
            name="rubber_foot", material_class_id="rubber.smooth_plain",
        )
        leg.inertial = Inertial.from_geometry(
            Box((0.020, 0.020, leg_len)),
            mass=0.25,
            origin=Origin(xyz=(mid_x, 0.0, mid_z)),
        )
        model.articulation(
            f"leg_hinge_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leg,
            origin=Origin(
                xyz=(hub_r * math.cos(az), hub_r * math.sin(az), hub_z), rpy=(0.0, 0.0, az)
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=18.0, velocity=2.0, lower=-0.55, upper=0.20),
            # No MatingContract — the leg hinge barrel is captured between clevis
            # cheeks (a pin-in-bore fit), proven via element-scoped allow_overlap.
        )


def _emit_column_socket_and_outer_tube(
    base, r: ResolvedMusicStand1Config, mats, *, socket_z0: float
) -> None:
    """Attach the outermost telescoping tube to the base at socket_z0. Adds a
    short socket and the outer tube ending at r.base_top_z."""
    # Socket collar above the base, welded to the base geometry. The stub
    # embeds a few mm into the source geometry so it welds to the supporting
    # part (hub / weighted disc / post socket).
    stub_center_z = socket_z0 + 0.036  # length/2 - small embed into supporting geometry
    base.visual(
        Cylinder(radius=0.022, length=0.080),
        origin=Origin(xyz=(0.0, 0.0, stub_center_z)),
        material=mats["column"],
        name="post_socket_stub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
    )
    # Outer tube starts inside the stub top for connectivity.
    z_min = stub_center_z + 0.030  # embeds into stub top by 0.010
    z_max = max(z_min + 0.20, r.base_top_z)
    base.visual(
        mesh_from_geometry(
            _annular_tube(0.0090, r.stage_outer_r0, z_min, z_max),
            "outer_tube",
        ),
        material=mats["base"],
        name="outer_tube", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
    )
    # Top collar at the tube top (where the lock knob mounts and where stage 0 pivots out).
    base.visual(
        mesh_from_geometry(
            _annular_tube(0.0085, 0.0170, z_max - 0.020, z_max),
            "outer_collar",
        ),
        material=mats["hardware"],
        name="outer_collar", material_class_id="metal.blackened_gunmetal",
    )
    # Record the actual top for _emit_stages to use.
    base._music_stand1_top_z = z_max  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Telescoping stages + lock knobs
# ---------------------------------------------------------------------------
def _emit_stages(model, r: ResolvedMusicStand1Config, mats):
    """Emit N telescoping stages + N lock-knob parts. Returns the topmost stage part."""
    base = model.get_part("base")
    parent_part = base
    parent_outer_r = r.stage_outer_r0
    parent_top_z = getattr(base, "_music_stand1_top_z", r.base_top_z)
    parent_top_z - r.stage_length  # for base, approximate
    n = r.height_stages

    for i in range(n):
        child_name = f"stage_{i}" if i < n - 1 else "upper_post"
        stage = model.part(child_name)
        # Child tube: outer radius shrinks each stage.
        child_outer_r = max(0.005, parent_outer_r - 0.0020)
        child_inner_r = max(0.003, child_outer_r - r.tube_wall)
        # Stage authored so that its tube spans [-r.stage_travel - retention, r.stage_length - retention]
        # We author child tube from z_min to z_max in the STAGE's local frame; the
        # stage rests when the joint value = 0 and rises with q>0.
        stage_z_min = -0.240  # deep insertion below the joint origin (rest overlap)
        stage_z_max = stage_z_min + r.stage_length
        stage.visual(
            mesh_from_geometry(
                _annular_tube(child_inner_r, child_outer_r, stage_z_min, stage_z_max),
                f"{child_name}_tube",
            ),
            material=mats["column"],
            name=f"{child_name}_tube", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"matte_black_walnut", "all_black_steel", "dark_hardware_wood"} else "metal.paint_coated"),
        )
        # Top collar of the child (where the NEXT lock knob will sit, or the desk hinge for top).
        collar_top_z = stage_z_max
        collar_bot_z = collar_top_z - 0.026
        stage.visual(
            mesh_from_geometry(
                _annular_tube(child_inner_r, 0.014, collar_bot_z, collar_top_z),
                f"{child_name}_top_collar",
            ),
            material=mats["hardware"],
            name=f"{child_name}_top_collar", material_class_id="metal.blackened_gunmetal",
        )
        stage.inertial = Inertial.from_geometry(
            Cylinder(radius=child_outer_r, length=r.stage_length),
            mass=0.24,
            origin=Origin(xyz=(0.0, 0.0, (stage_z_min + stage_z_max) / 2.0)),
        )
        # Joint: PRISMATIC +Z at the parent's top collar center.
        joint_origin_z = parent_top_z
        joint_name = f"height_stage_{i}"
        # For i>0, joint origin is expressed in the parent stage's LOCAL frame:
        # the parent stage's tube top is at stage_z_max in its own frame.
        if i == 0:
            local_origin_z = joint_origin_z  # base is the world root; local = world.
        else:
            local_origin_z = stage_z_max  # top of parent stage's tube in parent-local
        model.articulation(
            joint_name,
            ArticulationType.PRISMATIC,
            parent=parent_part,
            child=stage,
            origin=Origin(xyz=(0.0, 0.0, local_origin_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=60.0,
                velocity=0.16,
                lower=0.0,
                upper=r.stage_travel,
            ),
            # No MatingContract on telescoping joints: the tubes are concentric
            # and axially overlap, there's no discrete mating face. Captured-fit
            # is proven via element-scoped allow_overlap in run_tests.
        )
        # Lock knob for this stage on the PARENT (locks the child in place).
        # z_at_collar is expressed in the parent_part's LOCAL frame.
        knob_local_z = (
            joint_origin_z if i == 0 else stage_z_max
        )  # base is root; stages: top-of-tube.
        _emit_lock_knob(model, r, mats, index=i, parent_part=parent_part, z_at_collar=knob_local_z)

        parent_part = stage
        parent_outer_r = child_outer_r
        # For the next iteration: parent top = end of child tube in stage-local frame,
        # transformed by joint origin. When q=0 the child is at rest so its top face
        # sits at joint_origin_z + stage_z_max.
        parent_top_z = joint_origin_z + stage_z_max
    return parent_part, parent_top_z


def _emit_lock_knob(
    model, r: ResolvedMusicStand1Config, mats, *, index: int, parent_part, z_at_collar: float
) -> None:
    """Attach a revolute lock knob (about local Y) on the parent_part's collar
    at height z_at_collar. The knob's stem seats onto the collar surface."""
    knob = model.part(f"lock_knob_{index}")
    # Stem (into the collar) and knob body outside on -Y side.
    knob.visual(
        Cylinder(radius=0.0035, length=0.012),
        origin=Origin(xyz=(0.0, -0.006, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="lock_stem", material_class_id="metal.blackened_gunmetal",
    )
    knob.visual(
        mesh_from_geometry(
            KnobGeometry(
                0.024,
                0.014,
                body_style="lobed",
                base_diameter=0.017,
                top_diameter=0.022,
                edge_radius=0.001,
            ),
            f"lock_knob_body_{index}",
        ),
        origin=Origin(xyz=(0.0, -0.018, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="lock_knob_body", material_class_id="metal.blackened_gunmetal",
    )
    knob.inertial = Inertial.from_geometry(
        Cylinder(radius=0.012, length=0.024),
        mass=0.024,
        origin=Origin(xyz=(0.0, -0.014, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    # z_at_collar must be in the parent_part's LOCAL frame. When parent is base,
    # z_at_collar is already world/base-local. When parent is a stage, we must
    # pass the stage-local top-collar center z.
    # No MatingContract — captured stem/collar is proven via allow_overlap.
    model.articulation(
        f"lock_knob_turn_{index}",
        ArticulationType.REVOLUTE,
        parent=parent_part,
        child=knob,
        origin=Origin(xyz=(0.0, -r.lock_offset, z_at_collar - 0.005)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=4.0, lower=-math.pi, upper=math.pi),
    )


# ---------------------------------------------------------------------------
# Desk builders
# ---------------------------------------------------------------------------
def _emit_desk_common_hinge_and_lip(desk, r: ResolvedMusicStand1Config, mats) -> None:
    """Add the rear hinge barrel + rear bracket + front sheet-shelf lip common
    to every desk form. Desk-local frame: hinge pivot at origin."""
    # Rear bracket that anchors the hinge barrel to the panel above.
    desk.visual(
        Box((0.060, 0.018, 0.090)),
        origin=Origin(xyz=(0.0, 0.015, 0.045)),
        material=mats["hardware"],
        name="rear_bracket", material_class_id="metal.blackened_gunmetal",
    )
    desk.visual(
        Cylinder(radius=0.0110, length=0.050),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    # Front sheet shelf lip (universal decoration).
    desk.visual(
        Box((r.desk_width * 0.92, 0.045, 0.009)),
        origin=Origin(xyz=(0.0, -0.025, 0.019)),
        material=mats["desk"],
        name="sheet_shelf", material_class_id=("wood.walnut_dark" if r.palette_style in {"matte_black_walnut", "dark_hardware_wood"} else "metal.blackened_gunmetal"),
    )
    desk.visual(
        Box((r.desk_width * 0.92, 0.006, 0.028)),
        origin=Origin(xyz=(0.0, -0.045, 0.028)),
        material=mats["desk"],
        name="sheet_lip", material_class_id=("wood.walnut_dark" if r.palette_style in {"matte_black_walnut", "dark_hardware_wood"} else "metal.blackened_gunmetal"),
    )


def _build_solid_tray_desk(model, r: ResolvedMusicStand1Config, mats) -> None:
    desk = model.part("desk")
    desk.visual(
        mesh_from_geometry(
            _desk_plate_geometry(r.desk_width, r.desk_height, r.desk_thickness),
            "solid_tray_plate",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0 + 0.015)),
        material=mats["desk"],
        name="desk_plate", material_class_id=("wood.walnut_dark" if r.palette_style in {"matte_black_walnut", "dark_hardware_wood"} else "metal.blackened_gunmetal"),
    )
    # Wood-grain decoration (record_only ④).
    for i, (x_frac, z_frac, w_frac) in enumerate(
        [
            (-0.026, 0.94, 0.85),
            (0.040, 0.83, 0.73),
            (-0.048, 0.34, 0.78),
            (0.056, 0.23, 0.66),
            (-0.022, 0.14, 0.88),
        ]
    ):
        # wood grain embeds through the plate face so it welds unambiguously.
        desk.visual(
            Box((r.desk_width * w_frac, 0.006, 0.0014)),
            origin=Origin(
                xyz=(
                    r.desk_width * x_frac,
                    -0.004,
                    r.desk_height * (z_frac - 0.5) + 0.015 + r.desk_height / 2.0,
                )
            ),
            material=mats["desk_dark"],
            name=f"wood_grain_{i}", material_class_id=("wood.patterned_decorative" if r.palette_style in {"matte_black_walnut", "dark_hardware_wood"} else "metal.blackened_gunmetal"),
        )
    _emit_desk_common_hinge_and_lip(desk, r, mats)
    desk.inertial = Inertial.from_geometry(
        Box((r.desk_width, 0.05, r.desk_height)),
        mass=1.15,
        origin=Origin(xyz=(0.0, -0.004, r.desk_height / 2.0 + 0.015)),
    )


def _build_perforated_panel_desk(model, r: ResolvedMusicStand1Config, mats) -> None:
    desk = model.part("desk")
    desk.visual(
        mesh_from_geometry(
            _perforated_panel_geometry(r.desk_width, r.desk_height, r.desk_thickness),
            "perforated_panel_plate",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0 + 0.015)),
        material=mats["desk"],
        name="desk_plate", material_class_id=("wood.patterned_decorative" if r.palette_style in {"matte_black_walnut", "dark_hardware_wood"} else "metal.patterned_sheet_panel"),
    )
    _emit_desk_common_hinge_and_lip(desk, r, mats)
    desk.inertial = Inertial.from_geometry(
        Box((r.desk_width, 0.05, r.desk_height)),
        mass=0.9,
        origin=Origin(xyz=(0.0, -0.004, r.desk_height / 2.0 + 0.015)),
    )


def _build_wire_frame_desk(model, r: ResolvedMusicStand1Config, mats) -> None:
    desk = model.part("desk")
    # Frame rectangle — starts at desk-local z=0 so the hinge_barrel + rear
    # bracket + sheet lip stay welded to the lower rail.
    w = r.desk_width
    h = r.desk_height
    z0 = 0.0  # bottom rail at desk-local z=0 (right on the hinge line)
    z_top = z0 + h - 0.020

    # Long rails.
    def _beam(part, start, end, section, name):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        dz = end[2] - start[2]
        length = math.sqrt(dx * dx + dy * dy + dz * dz)
        yaw = math.atan2(dy, dx)
        pitch = math.atan2(math.sqrt(dx * dx + dy * dy), max(dz, 1e-6))
        cx = (start[0] + end[0]) / 2.0
        cy = (start[1] + end[1]) / 2.0
        cz = (start[2] + end[2]) / 2.0
        part.visual(
            Box((section[0], section[1], length)),
            origin=Origin(xyz=(cx, cy, cz), rpy=(0.0, pitch, yaw)),
            material=mats["column"],
            name=name, material_class_id="metal.paint_coated",
        )

    xL = -w / 2.0 * 0.96
    xR = w / 2.0 * 0.96
    _beam(desk, (xL, 0.0, z0), (xR, 0.0, z0), (0.010, 0.008), "lower_rail")
    _beam(desk, (xL, 0.0, z_top), (xR, 0.0, z_top), (0.009, 0.007), "upper_rail")
    _beam(desk, (xL, 0.0, z0), (xL, 0.0, z_top), (0.009, 0.007), "left_rail")
    _beam(desk, (xR, 0.0, z0), (xR, 0.0, z_top), (0.009, 0.007), "right_rail")
    for k, zf in enumerate((0.25, 0.50, 0.75)):
        zz = z0 + (z_top - z0) * zf
        _beam(
            desk, (xL * 0.98, 0.0, zz), (xR * 0.98, 0.0, zz), (0.008, 0.006), f"horizontal_rail_{k}"
        )
    _beam(desk, (0.0, 0.0, z0), (0.0, 0.0, z_top), (0.011, 0.008), "center_spine")
    _emit_desk_common_hinge_and_lip(desk, r, mats)
    desk.inertial = Inertial.from_geometry(
        Box((w, 0.05, h)),
        mass=0.6,
        origin=Origin(xyz=(0.0, 0.0, (z0 + z_top) / 2.0)),
    )


def _build_split_folding_leaves_desk(model, r: ResolvedMusicStand1Config, mats) -> None:
    desk = model.part("desk")
    # Two mirrored half-panels meeting at x=0, each half is a rounded rectangle.
    half_w = r.desk_width / 2.0
    for sign, tag in ((-1.0, "left"), (1.0, "right")):
        desk.visual(
            mesh_from_geometry(
                _desk_plate_geometry(half_w * 0.98, r.desk_height, r.desk_thickness),
                f"leaf_plate_{tag}",
            ),
            origin=Origin(xyz=(sign * half_w / 2.0, 0.0, r.desk_height / 2.0 + 0.015)),
            material=mats["desk"],
            name=f"leaf_{tag}", material_class_id=("wood.walnut_dark" if r.palette_style in {"matte_black_walnut", "dark_hardware_wood"} else "metal.blackened_gunmetal"),
        )
    # Central spine that unifies the two leaves.
    desk.visual(
        Box((0.020, 0.014, r.desk_height * 0.92)),
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0 + 0.015)),
        material=mats["hardware"],
        name="center_spine", material_class_id="metal.blackened_gunmetal",
    )
    _emit_desk_common_hinge_and_lip(desk, r, mats)
    desk.inertial = Inertial.from_geometry(
        Box((r.desk_width, 0.05, r.desk_height)),
        mass=1.0,
        origin=Origin(xyz=(0.0, -0.004, r.desk_height / 2.0 + 0.015)),
    )


_BASE_BUILDERS = {
    "round_pedestal": _build_round_pedestal,
    "folding_tripod": _build_folding_tripod,
    "weighted_wide_disk": _build_weighted_wide_disk,
}
_DESK_BUILDERS = {
    "solid_tray": _build_solid_tray_desk,
    "perforated_panel": _build_perforated_panel_desk,
    "wire_frame": _build_wire_frame_desk,
    "split_folding_leaves": _build_split_folding_leaves_desk,
}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_music_stand1(
    config: MusicStand1Config | ResolvedMusicStand1Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, meta={"category": "music_stand1"})
    if assets is not None:
        model.set_assets(assets)
    mats = {
        key: model.material(f"music_stand1_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    _BASE_BUILDERS[r.base_form](model, r, mats)
    top_stage, top_z = _emit_stages(model, r, mats)

    _DESK_BUILDERS[r.desk_form](model, r, mats)
    desk = model.get_part("desk")

    # Desk tilt REVOLUTE about +X. Desk hinge at desk-local (0,0,0); joint
    # origin at top of the top_stage tube in top_stage-LOCAL frame.
    # For every stage part, stage_z_max is the top of its tube (see _emit_stages).
    STAGE_Z_MAX_LOCAL = 0.560 * r.column_length_scale + (
        -0.240
    )  # matches _emit_stages: stage_z_min + stage_length
    model.articulation(
        "desk_tilt",
        ArticulationType.REVOLUTE,
        parent=top_stage,
        child=desk,
        origin=Origin(xyz=(0.0, 0.0, STAGE_Z_MAX_LOCAL), rpy=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=14.0,
            velocity=1.2,
            lower=-r.tilt_range,
            upper=r.tilt_range,
        ),
        # No MatingContract — the hinge barrel is captured on the collar (a
        # pin-in-bore fit), proven via element-scoped allow_overlap in run_tests.
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_music_stand1(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_music_stand1(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_music_stand1_tests(
    object_model: ArticulatedObject,
    config: MusicStand1Config | ResolvedMusicStand1Config | None = None,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    # ---- Captured-pin / telescope allowances (element-scoped). ----
    base = object_model.get_part("base")
    # Telescoping tube captures.
    for i in range(r.height_stages):
        child_name = f"stage_{i}" if i < r.height_stages - 1 else "upper_post"
        child = object_model.get_part(child_name)
        parent_name = (
            "base"
            if i == 0
            else (f"stage_{i - 1}" if i - 1 < r.height_stages - 1 else "upper_post")
        )
        parent = object_model.get_part(parent_name)
        parent_tube_name = "outer_tube" if i == 0 else f"stage_{i - 1}_tube"
        ctx.allow_overlap(
            child,
            parent,
            elem_a=f"{child_name}_tube",
            elem_b=parent_tube_name,
            reason=f"stage {i} inner tube is captured inside the parent's outer tube (telescoping fit).",
        )
        ctx.allow_overlap(
            child,
            parent,
            elem_a=f"{child_name}_tube",
            elem_b="outer_collar" if i == 0 else f"stage_{i - 1}_top_collar",
            reason=f"stage {i} inner tube passes through the parent's top collar bore.",
        )
    # Lock knobs: captured stems.
    for i in range(r.height_stages):
        parent_name = (
            "base"
            if i == 0
            else (f"stage_{i - 1}" if i - 1 < r.height_stages - 1 else "upper_post")
        )
        parent = object_model.get_part(parent_name)
        knob = object_model.get_part(f"lock_knob_{i}")
        collar_name = "outer_collar" if i == 0 else f"stage_{i - 1}_top_collar"
        ctx.allow_overlap(
            knob,
            parent,
            elem_a="lock_stem",
            elem_b=collar_name,
            reason=f"lock knob {i} stem is captured inside the collar bore.",
        )
    # Desk tilt hinge captured pin.
    top_stage = object_model.get_part("upper_post")
    desk = object_model.get_part("desk")
    ctx.allow_overlap(
        desk,
        top_stage,
        elem_a="hinge_barrel",
        elem_b=f"{top_stage.name}_top_collar",
        reason="desk hinge barrel is captured on the top-collar tilt pin.",
    )
    ctx.allow_overlap(
        desk,
        top_stage,
        elem_a="hinge_barrel",
        elem_b=f"{top_stage.name}_tube",
        reason="desk hinge barrel wraps the top of the topmost column tube (captured tilt pin).",
    )
    ctx.allow_overlap(
        desk,
        top_stage,
        elem_a="rear_bracket",
        elem_b=f"{top_stage.name}_top_collar",
        reason="desk rear bracket rides on the top collar through the tilt range.",
    )
    ctx.allow_overlap(
        desk,
        top_stage,
        elem_a="rear_bracket",
        elem_b=f"{top_stage.name}_tube",
        reason="desk rear bracket clamps the top of the topmost column tube.",
    )
    # Wire-frame desk: the frame's lower_rail sits at desk-local z=0, so it
    # brushes the top of the column tube/collar (the whole desk mounts on the
    # column tilt pin here).
    if r.desk_form == "wire_frame":
        for elem in ("lower_rail", "center_spine", "left_rail", "right_rail"):
            ctx.allow_overlap(
                desk,
                top_stage,
                elem_a=elem,
                elem_b=f"{top_stage.name}_top_collar",
                reason=f"wire-frame desk {elem} clamps around the tilt-pin collar.",
            )
            ctx.allow_overlap(
                desk,
                top_stage,
                elem_a=elem,
                elem_b=f"{top_stage.name}_tube",
                reason=f"wire-frame desk {elem} welds to the top of the column tube.",
            )
    # Folding tripod leg hinges.
    if r.base_form == "folding_tripod":
        # Fully-folded configs bring the three leg tubes into the column region.
        # Model them as an allowed-collision folded stack (real music stands fold
        # the legs against the column for storage).
        for i in range(3):
            for j in range(i + 1, 3):
                ctx.allow_overlap(
                    object_model.get_part(f"tripod_leg_{i}"),
                    object_model.get_part(f"tripod_leg_{j}"),
                    reason=("folded tripod legs stack against the column (stored config)."),
                )
        for i in range(3):
            leg = object_model.get_part(f"tripod_leg_{i}")
            for side in range(2):
                ctx.allow_overlap(
                    leg,
                    base,
                    elem_a="hinge_barrel",
                    elem_b=f"leg_bracket_{i}_{side}",
                    reason=f"leg {i} hinge barrel is captured between clevis cheeks.",
                )
            ctx.allow_overlap(
                leg,
                base,
                elem_a="hinge_barrel",
                elem_b="tripod_hub",
                reason=f"leg {i} hinge barrel is welded against the tripod hub.",
            )
            ctx.allow_overlap(
                leg,
                base,
                elem_a="leg_tube",
                elem_b="tripod_hub",
                reason=f"leg {i} tube exits the hub through its side; the folded stow position keeps the tube pressed against the hub curve.",
            )
            ctx.allow_overlap(
                leg,
                base,
                elem_a="leg_tube",
                elem_b="post_socket_stub",
                reason=f"folded leg {i} tube brushes the column socket (stored config).",
            )

    # ---- Baseline gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("base part present", "base" in part_names)
    ctx.check("desk part present", "desk" in part_names)
    expected_stage_parts = {"upper_post"}
    for i in range(r.height_stages - 1):
        expected_stage_parts.add(f"stage_{i}")
    ctx.check(
        "N stage parts present",
        expected_stage_parts <= part_names,
        details=f"expected>={sorted(expected_stage_parts)} got={sorted(part_names)}",
    )
    ctx.check(
        "lock knob parts present",
        all(f"lock_knob_{i}" in part_names for i in range(r.height_stages)),
    )
    joint_names = {j.name for j in object_model.articulations}
    for i in range(r.height_stages):
        ctx.check(
            f"height_stage_{i} PRISMATIC +Z",
            object_model.get_articulation(f"height_stage_{i}").articulation_type
            == ArticulationType.PRISMATIC,
        )
    ctx.check(
        "desk_tilt REVOLUTE",
        object_model.get_articulation("desk_tilt").articulation_type == ArticulationType.REVOLUTE,
    )
    if r.base_form == "folding_tripod":
        ctx.check(
            "three tripod legs with hinges",
            all(
                f"tripod_leg_{i}" in part_names and f"leg_hinge_{i}" in joint_names
                for i in range(3)
            ),
        )

    # ---- Slot choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Height actuation raises the topmost stage. ----
    top_stage_part = object_model.get_part("upper_post")
    p0 = ctx.part_world_position(top_stage_part)
    poses = {}
    for i in range(r.height_stages):
        poses[object_model.get_articulation(f"height_stage_{i}")] = r.stage_travel * 0.9
    with ctx.pose(poses):
        p1 = ctx.part_world_position(top_stage_part)
    if p0 is not None and p1 is not None:
        ctx.check(
            "column extends upward when all stages actuate",
            p1[2] > p0[2] + max(0.03, r.stage_travel * 0.5),
            details=f"rest_z={p0[2]:.3f} raised_z={p1[2]:.3f}",
        )

    # ---- Desk tilt sweeps in Y. ----
    desk_tilt = object_model.get_articulation("desk_tilt")
    with ctx.pose({desk_tilt: -r.tilt_range * 0.85}):
        aabb_back = ctx.part_world_aabb(desk)
    with ctx.pose({desk_tilt: r.tilt_range * 0.85}):
        aabb_fwd = ctx.part_world_aabb(desk)
    if aabb_back is not None and aabb_fwd is not None:
        y_back = (aabb_back[0][1] + aabb_back[1][1]) * 0.5
        y_fwd = (aabb_fwd[0][1] + aabb_fwd[1][1]) * 0.5
        ctx.check(
            "desk tilt sweeps the reading face in Y",
            abs(y_back - y_fwd) > 0.02,
            details=f"y_back={y_back:.3f} y_fwd={y_fwd:.3f}",
        )

    # ---- Stand touches the ground (via base disc or via a tripod foot). ----
    ground_parts = [base]
    if r.base_form == "folding_tripod":
        ground_parts.extend(object_model.get_part(f"tripod_leg_{i}") for i in range(3))
    ground_z_min = None
    for gp in ground_parts:
        aabb = ctx.part_world_aabb(gp)
        if aabb is not None:
            z0 = aabb[0][2]
            ground_z_min = z0 if ground_z_min is None else min(ground_z_min, z0)
    if ground_z_min is not None:
        ctx.check(
            "stand touches ground",
            ground_z_min < 0.05,
            details=f"z_min={ground_z_min:.4f}",
        )

    return ctx.report()


__all__ = [
    "MusicStand1Config",
    "ResolvedMusicStand1Config",
    "build_music_stand1",
    "build_seeded_music_stand1",
    "config_from_seed",
    "resolve_config",
    "run_music_stand1_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
