# SPDX-License-Identifier: Apache-2.0

"""Source-backed handheld remote-control template.

The reviewed source pool contributes enclosure, primary-control, repeated-button,
and protective-cover components independently.  Variant records contribute only
their changed component; unchanged parent components are reused through the
ordinary functions below.

Coordinates: X = body width, Y = body length (top toward +Y), Z = front.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    LoftGeometry,
    MotionLimits,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    rounded_rect_profile,
)

__preview_front_axis__ = "-y"

EnclosureFamily = Literal[
    "rounded_thermostat",
    "ergonomic_waisted",
    "slim_wand",
    "tapered_wand",
]
PrimaryControl = Literal["directional_pad", "volume_rocker", "jog_wheel"]
ButtonArray = Literal["media_round_grid", "numeric_square_grid"]
CoverModule = Literal["open_face", "flip_cover", "slide_cover"]

_ENCLOSURES = (
    "rounded_thermostat",
    "ergonomic_waisted",
    "slim_wand",
    "tapered_wand",
)
_PRIMARY_CONTROLS = ("directional_pad", "volume_rocker", "jog_wheel")
_BUTTON_ARRAYS = ("media_round_grid", "numeric_square_grid")
_COVERS = ("open_face", "flip_cover", "slide_cover")
_BUTTON_COUNTS = (4, 8, 12)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("enclosure_family", _ENCLOSURES),
        component_slot("primary_control", _PRIMARY_CONTROLS),
        component_slot("button_array", _BUTTON_ARRAYS),
        component_slot("cover_module", _COVERS),
        multiplicity_slot("button_count", _BUTTON_COUNTS, item_slot="button_array"),
    )
)

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {
        "shell": (0.035, 0.038, 0.043, 1.0),
        "trim": (0.12, 0.13, 0.15, 1.0),
        "button": (0.33, 0.35, 0.37, 1.0),
        "legend": (0.88, 0.89, 0.86, 1.0),
        "screen": (1.0, 0.31, 0.08, 1.0),
        "cover": (0.17, 0.18, 0.20, 1.0),
    },
    {
        "shell": (0.80, 0.81, 0.78, 1.0),
        "trim": (0.36, 0.38, 0.40, 1.0),
        "button": (0.14, 0.15, 0.17, 1.0),
        "legend": (0.91, 0.91, 0.88, 1.0),
        "screen": (0.32, 0.72, 0.78, 1.0),
        "cover": (0.54, 0.55, 0.57, 1.0),
    },
    {
        "shell": (0.12, 0.16, 0.23, 1.0),
        "trim": (0.22, 0.27, 0.34, 1.0),
        "button": (0.63, 0.65, 0.68, 1.0),
        "legend": (0.12, 0.13, 0.15, 1.0),
        "screen": (0.64, 0.87, 0.93, 1.0),
        "cover": (0.25, 0.30, 0.38, 1.0),
    },
)

_BODY_THICKNESS = 0.014
_CARRIER_THICKNESS = 0.0012
_BUTTON_HEIGHT = 0.0026
_BUTTON_GAP = 0.0004


@dataclass(frozen=True)
class Config:
    enclosure_family: EnclosureFamily = "rounded_thermostat"
    primary_control: PrimaryControl = "directional_pad"
    button_array: ButtonArray = "media_round_grid"
    cover_module: CoverModule = "open_face"
    button_count: int = 8
    thermostat_width_m: float | None = None
    waist_ratio: float | None = None
    wand_width_m: float | None = None
    taper_ratio: float | None = None
    dpad_diameter_m: float | None = None
    dpad_travel_m: float | None = None
    rocker_diameter_m: float | None = None
    rocker_angle_rad: float | None = None
    jog_diameter_m: float | None = None
    media_button_diameter_m: float | None = None
    media_button_travel_m: float | None = None
    numeric_key_width_m: float | None = None
    numeric_key_travel_m: float | None = None
    flip_cover_angle_rad: float | None = None
    slide_cover_travel_m: float | None = None
    palette: int = 0
    name: str = "Technology_Remote_Control"


@dataclass(frozen=True)
class ResolvedConfig:
    enclosure_family: EnclosureFamily
    primary_control: PrimaryControl
    button_array: ButtonArray
    cover_module: CoverModule
    button_count: int
    thermostat_width_m: float
    waist_ratio: float
    wand_width_m: float
    taper_ratio: float
    dpad_diameter_m: float
    dpad_travel_m: float
    rocker_diameter_m: float
    rocker_angle_rad: float
    jog_diameter_m: float
    media_button_diameter_m: float
    media_button_travel_m: float
    numeric_key_width_m: float
    numeric_key_travel_m: float
    flip_cover_angle_rad: float
    slide_cover_travel_m: float
    palette: int
    name: str
    body_width_m: float
    body_length_m: float
    body_top_z_m: float
    primary_center_y_m: float
    primary_boss_radius_m: float
    button_pitch_x_m: float
    button_pitch_y_m: float
    button_bed_width_m: float
    button_bed_length_m: float
    button_bed_center_y_m: float
    cover_width_m: float
    cover_length_m: float
    rail_spacing_m: float


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def _bounded(value: float | None, default: float, lower: float, upper: float) -> float:
    selected = _pick(value, default)
    if not lower <= selected <= upper:
        raise ValueError(f"value {selected} outside [{lower}, {upper}]")
    return selected


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    index = int(seed)
    button_count = _BUTTON_COUNTS[index % len(_BUTTON_COUNTS)]
    index //= len(_BUTTON_COUNTS)
    button_array = _BUTTON_ARRAYS[index % len(_BUTTON_ARRAYS)]
    index //= len(_BUTTON_ARRAYS)
    cover_module = _COVERS[index % len(_COVERS)]
    index //= len(_COVERS)
    primary_control = _PRIMARY_CONTROLS[index % len(_PRIMARY_CONTROLS)]
    index //= len(_PRIMARY_CONTROLS)
    enclosure_family = _ENCLOSURES[index % len(_ENCLOSURES)]
    return Config(
        enclosure_family=enclosure_family,
        primary_control=primary_control,
        button_array=button_array,
        cover_module=cover_module,
        button_count=button_count,
        thermostat_width_m=round(rng.uniform(0.062, 0.072), 4),
        waist_ratio=round(rng.uniform(0.72, 0.84), 4),
        wand_width_m=round(rng.uniform(0.050, 0.060), 4),
        taper_ratio=round(rng.uniform(0.68, 0.82), 4),
        dpad_diameter_m=round(rng.uniform(0.038, 0.048), 4),
        dpad_travel_m=round(rng.uniform(0.0010, 0.0018), 4),
        rocker_diameter_m=round(rng.uniform(0.026, 0.034), 4),
        rocker_angle_rad=round(rng.uniform(0.14, 0.22), 4),
        jog_diameter_m=round(rng.uniform(0.028, 0.036), 4),
        media_button_diameter_m=round(rng.uniform(0.009, 0.012), 4),
        media_button_travel_m=round(rng.uniform(0.0008, 0.0014), 4),
        numeric_key_width_m=round(rng.uniform(0.009, 0.012), 4),
        numeric_key_travel_m=round(rng.uniform(0.0008, 0.0014), 4),
        flip_cover_angle_rad=round(rng.uniform(1.55, 1.85), 4),
        slide_cover_travel_m=round(rng.uniform(0.050, 0.070), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"Technology_Remote_Control_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    if config.enclosure_family not in _ENCLOSURES:
        raise ValueError(f"unsupported enclosure_family: {config.enclosure_family}")
    if config.primary_control not in _PRIMARY_CONTROLS:
        raise ValueError(f"unsupported primary_control: {config.primary_control}")
    if config.button_array not in _BUTTON_ARRAYS:
        raise ValueError(f"unsupported button_array: {config.button_array}")
    if config.cover_module not in _COVERS:
        raise ValueError(f"unsupported cover_module: {config.cover_module}")
    if int(config.button_count) not in _BUTTON_COUNTS:
        raise ValueError(f"button_count must be one of {_BUTTON_COUNTS}")

    thermostat_width = _bounded(config.thermostat_width_m, 0.067, 0.062, 0.072)
    waist_ratio = _bounded(config.waist_ratio, 0.78, 0.72, 0.84)
    wand_width = _bounded(config.wand_width_m, 0.055, 0.050, 0.060)
    taper_ratio = _bounded(config.taper_ratio, 0.75, 0.68, 0.82)
    dpad_diameter = _bounded(config.dpad_diameter_m, 0.043, 0.038, 0.048)
    dpad_travel = _bounded(config.dpad_travel_m, 0.0014, 0.0010, 0.0018)
    rocker_diameter = _bounded(config.rocker_diameter_m, 0.030, 0.026, 0.034)
    rocker_angle = _bounded(config.rocker_angle_rad, 0.18, 0.14, 0.22)
    jog_diameter = _bounded(config.jog_diameter_m, 0.032, 0.028, 0.036)
    media_diameter = _bounded(config.media_button_diameter_m, 0.0105, 0.009, 0.012)
    media_travel = _bounded(config.media_button_travel_m, 0.0011, 0.0008, 0.0014)
    numeric_width = _bounded(config.numeric_key_width_m, 0.0105, 0.009, 0.012)
    numeric_travel = _bounded(config.numeric_key_travel_m, 0.0011, 0.0008, 0.0014)
    flip_angle = _bounded(config.flip_cover_angle_rad, 1.72, 1.55, 1.85)
    slide_travel = _bounded(config.slide_cover_travel_m, 0.060, 0.050, 0.070)

    if config.enclosure_family == "rounded_thermostat":
        nominal_body_width = thermostat_width
        adaptation_base_width = 0.062
    elif config.enclosure_family == "ergonomic_waisted":
        nominal_body_width = 0.070
        adaptation_base_width = 0.070
    elif config.enclosure_family == "slim_wand":
        nominal_body_width = wand_width
        adaptation_base_width = 0.050
    else:
        nominal_body_width = 0.068
        adaptation_base_width = 0.068

    cap_size = media_diameter if config.button_array == "media_round_grid" else numeric_width
    pitch_x = cap_size + 0.005
    pitch_y = cap_size + 0.006
    rows = math.ceil(int(config.button_count) / 3)
    bed_width = 3.0 * pitch_x + 0.006
    bed_length = rows * pitch_y + 0.010
    selected_control_diameter = (
        dpad_diameter
        if config.primary_control == "directional_pad"
        else rocker_diameter
        if config.primary_control == "volume_rocker"
        else jog_diameter
    )
    required_host_width = max(bed_width + 0.006, selected_control_diameter + 0.011)
    local_shoulder_growth = max(0.0, required_host_width - adaptation_base_width)
    body_width = nominal_body_width + local_shoulder_growth
    body_length = 0.120 + bed_length
    primary_center_y = body_length / 2.0 - 0.062
    bed_center_y = primary_center_y - 0.038 - bed_length / 2.0
    primary_radius = (
        dpad_diameter / 2.0
        if config.primary_control == "directional_pad"
        else rocker_diameter / 2.0
        if config.primary_control == "volume_rocker"
        else jog_diameter / 2.0
    )
    cover_width = min(body_width - 0.008, max(bed_width + 0.004, primary_radius * 1.6))
    cover_length = bed_length + 0.010

    return ResolvedConfig(
        enclosure_family=config.enclosure_family,
        primary_control=config.primary_control,
        button_array=config.button_array,
        cover_module=config.cover_module,
        button_count=int(config.button_count),
        thermostat_width_m=thermostat_width,
        waist_ratio=waist_ratio,
        wand_width_m=wand_width,
        taper_ratio=taper_ratio,
        dpad_diameter_m=dpad_diameter,
        dpad_travel_m=dpad_travel,
        rocker_diameter_m=rocker_diameter,
        rocker_angle_rad=rocker_angle,
        jog_diameter_m=jog_diameter,
        media_button_diameter_m=media_diameter,
        media_button_travel_m=media_travel,
        numeric_key_width_m=numeric_width,
        numeric_key_travel_m=numeric_travel,
        flip_cover_angle_rad=flip_angle,
        slide_cover_travel_m=slide_travel,
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        body_width_m=body_width,
        body_length_m=body_length,
        body_top_z_m=_BODY_THICKNESS / 2.0,
        primary_center_y_m=primary_center_y,
        primary_boss_radius_m=primary_radius + 0.0025,
        button_pitch_x_m=pitch_x,
        button_pitch_y_m=pitch_y,
        button_bed_width_m=bed_width,
        button_bed_length_m=bed_length,
        button_bed_center_y_m=bed_center_y,
        cover_width_m=cover_width,
        cover_length_m=cover_length,
        rail_spacing_m=cover_width / 2.0 - 0.002,
    )


def _materials(model: ArticulatedObject, palette: int):
    colors = _PALETTES[palette]
    return {name: model.material(name, rgba=rgba) for name, rgba in colors.items()}


def _prism(profile, z0: float, z1: float, name: str):
    return mesh_from_geometry(
        LoftGeometry(
            (
                [(x, y, z0) for x, y in profile],
                [(x, y, z1) for x, y in profile],
            ),
            cap=True,
            closed=True,
        ),
        name,
    )


def _body_mesh(profile, name: str):
    return _prism(profile, -_BODY_THICKNESS / 2.0, _BODY_THICKNESS / 2.0, name)


def _enclosure_family_rounded_thermostat_build(body, r: ResolvedConfig, mats) -> None:
    tag = "enclosure_family__rounded_thermostat"
    profile = rounded_rect_profile(
        r.body_width_m, r.body_length_m, radius=min(0.012, r.body_width_m * 0.20), corner_segments=8
    )
    body.visual(_body_mesh(profile, f"{tag}__shell"), material=mats["shell"], name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded")
    screen_w = r.body_width_m - 0.016
    screen_y = r.body_length_m / 2.0 - 0.030
    body.visual(
        Box((screen_w, 0.031, 0.0008)),
        origin=Origin(xyz=(0.0, screen_y, r.body_top_z_m + 0.0004)),
        material=mats["trim"],
        name=f"{tag}__lcd_bezel", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((screen_w - 0.004, 0.027, 0.0007)),
        origin=Origin(xyz=(0.0, screen_y, r.body_top_z_m + 0.00115)),
        material=mats["screen"],
        name=f"{tag}__lcd_glass", material_class_id="tech.emissive_surface",
    )


def _enclosure_family_ergonomic_waisted_build(body, r: ResolvedConfig, mats) -> None:
    tag = "enclosure_family__ergonomic_waisted"
    hw = r.body_width_m / 2.0
    hh = r.body_length_m / 2.0
    waist = hw * r.waist_ratio
    profile = (
        (-hw * 0.72, -hh),
        (hw * 0.72, -hh),
        (hw, -hh * 0.70),
        (hw * 0.92, -hh * 0.28),
        (waist, 0.0),
        (hw * 0.94, hh * 0.30),
        (hw, hh * 0.72),
        (hw * 0.70, hh),
        (-hw * 0.70, hh),
        (-hw, hh * 0.72),
        (-hw * 0.94, hh * 0.30),
        (-waist, 0.0),
        (-hw * 0.92, -hh * 0.28),
        (-hw, -hh * 0.70),
    )
    body.visual(_body_mesh(profile, f"{tag}__shell"), material=mats["shell"], name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(
        Box((r.body_width_m - 0.022, 0.026, 0.0008)),
        origin=Origin(
            xyz=(0.0, r.body_length_m / 2.0 - 0.030, r.body_top_z_m + 0.0004)
        ),
        material=mats["screen"],
        name=f"{tag}__display", material_class_id="tech.emissive_surface",
    )


def _enclosure_family_slim_wand_build(body, r: ResolvedConfig, mats) -> None:
    tag = "enclosure_family__slim_wand"
    profile = rounded_rect_profile(
        r.body_width_m, r.body_length_m, radius=r.body_width_m * 0.34, corner_segments=10
    )
    body.visual(_body_mesh(profile, f"{tag}__shell"), material=mats["shell"], name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(
        Box((r.body_width_m - 0.018, 0.006, 0.0007)),
        origin=Origin(
            xyz=(0.0, r.body_length_m / 2.0 - 0.020, r.body_top_z_m + 0.00035)
        ),
        material=mats["trim"],
        name=f"{tag}__infrared_window", material_class_id="glass.smoked_tinted",
    )


def _enclosure_family_tapered_wand_build(body, r: ResolvedConfig, mats) -> None:
    tag = "enclosure_family__tapered_wand"
    hh = r.body_length_m / 2.0
    wide = r.body_width_m / 2.0
    narrow = wide * r.taper_ratio
    profile = (
        (-narrow * 0.68, -hh),
        (narrow * 0.68, -hh),
        (narrow, -hh + 0.010),
        (wide, hh - 0.012),
        (wide * 0.70, hh),
        (-wide * 0.70, hh),
        (-wide, hh - 0.012),
        (-narrow, -hh + 0.010),
    )
    body.visual(_body_mesh(profile, f"{tag}__shell"), material=mats["shell"], name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(
        Box((r.body_width_m - 0.020, 0.005, 0.0007)),
        origin=Origin(
            xyz=(0.0, r.body_length_m / 2.0 - 0.020, r.body_top_z_m + 0.00035)
        ),
        material=mats["trim"],
        name=f"{tag}__infrared_window", material_class_id="glass.smoked_tinted",
    )


_ENCLOSURE_BUILDERS = {
    "rounded_thermostat": _enclosure_family_rounded_thermostat_build,
    "ergonomic_waisted": _enclosure_family_ergonomic_waisted_build,
    "slim_wand": _enclosure_family_slim_wand_build,
    "tapered_wand": _enclosure_family_tapered_wand_build,
}


def _fixed_carrier(
    model: ArticulatedObject,
    body,
    r: ResolvedConfig,
    *,
    slot: str,
    candidate: str,
    role: str,
    center_y: float,
    extent: tuple[float, float],
    consumer_point: tuple[float, float, float] = (0.0, 0.0, 0.0),
):
    part = model.part(
        role,
        meta={"role": role, "slot": slot, "candidate": candidate},
    )
    provider = PlaneInterface(
        name=f"enclosure_family.{slot}_mount",
        point=(
            consumer_point[0],
            center_y + consumer_point[1],
            r.body_top_z_m + consumer_point[2],
        ),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.body_width_m - 0.006, min(r.body_length_m - 0.010, extent[1] + 0.010)),
    )
    consumer = PlaneInterface(
        name=f"{slot}.mount_plane",
        point=consumer_point,
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=extent,
    )
    mate = mate_planes(provider, consumer)
    model.articulation(
        f"{slot}__{candidate}__fixed_mount",
        ArticulationType.FIXED,
        parent=body,
        child=part,
        origin=mate.origin,
    )
    return part


def _sector_profile(inner: float, outer: float, start: float, end: float):
    points = []
    for index in range(9):
        angle = start + (end - start) * index / 8.0
        points.append((outer * math.cos(angle), outer * math.sin(angle)))
    for index in range(8, -1, -1):
        angle = start + (end - start) * index / 8.0
        points.append((inner * math.cos(angle), inner * math.sin(angle)))
    return tuple(points)


def _primary_control_directional_pad_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    tag = "primary_control__directional_pad"
    diameter = r.dpad_diameter_m
    carrier = _fixed_carrier(
        model,
        body,
        r,
        slot="primary_control",
        candidate=r.primary_control,
        role="primary_carrier",
        center_y=r.primary_center_y_m,
        extent=(diameter + 0.005, diameter + 0.005),
    )
    carrier.visual(
        Cylinder(radius=diameter / 2.0 + 0.002, length=_CARRIER_THICKNESS),
        origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS / 2.0)),
        material=mats["trim"],
        name=f"{tag}__well", material_class_id="plastic.opaque_glossy_molded",
    )
    inner = diameter * 0.18
    outer = diameter * 0.46
    sectors = (
        ("up", math.radians(48), math.radians(132)),
        ("left", math.radians(138), math.radians(222)),
        ("down", math.radians(228), math.radians(312)),
        ("right", math.radians(-42), math.radians(42)),
    )
    for index, (label, start, end) in enumerate(sectors):
        button = model.part(
            f"{tag}__button_{label}",
            meta={"role": "directional_button", "slot": "primary_control", "candidate": r.primary_control},
        )
        button.visual(
            _prism(
                _sector_profile(inner, outer, start, end),
                0.0,
                _BUTTON_HEIGHT,
                f"{tag}__{label}_cap",
            ),
            material=mats["button"],
            name=f"{tag}__{label}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"{tag}__press_joint_{index}",
            ArticulationType.PRISMATIC,
            parent=carrier,
            child=button,
            origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS + _BUTTON_GAP)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=1.0, velocity=0.08, lower=0.0, upper=r.dpad_travel_m
            ),
            meta={"motion_qc_repeat_group": "directional_press"},
        )
    center = model.part(
        f"{tag}__button_mode",
        meta={"role": "directional_button", "slot": "primary_control", "candidate": r.primary_control},
    )
    center.visual(
        Cylinder(radius=inner * 0.86, length=_BUTTON_HEIGHT),
        origin=Origin(xyz=(0.0, 0.0, _BUTTON_HEIGHT / 2.0)),
        material=mats["button"],
        name=f"{tag}__mode_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    center.visual(
        Box((inner * 0.75, 0.0007, 0.0003)),
        origin=Origin(xyz=(0.0, 0.0, _BUTTON_HEIGHT + 0.00015)),
        material=mats["legend"],
        name=f"{tag}__mode_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    model.articulation(
        f"{tag}__press_joint_4",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=center,
        origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS + _BUTTON_GAP)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=0.08, lower=0.0, upper=r.dpad_travel_m
        ),
        meta={"motion_qc_repeat_group": "directional_press"},
    )


def _primary_control_volume_rocker_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    tag = "primary_control__volume_rocker"
    radius = r.rocker_diameter_m / 2.0
    carrier = _fixed_carrier(
        model,
        body,
        r,
        slot="primary_control",
        candidate=r.primary_control,
        role="primary_carrier",
        center_y=r.primary_center_y_m,
        extent=(r.rocker_diameter_m + 0.006, r.rocker_diameter_m + 0.006),
    )
    carrier.visual(
        Cylinder(radius=radius + 0.0025, length=_CARRIER_THICKNESS),
        origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS / 2.0)),
        material=mats["trim"],
        name=f"{tag}__well", material_class_id="plastic.opaque_glossy_molded",
    )
    for sign in (-1.0, 1.0):
        carrier.visual(
            Cylinder(radius=0.0022, length=0.004),
            origin=Origin(
                xyz=(sign * (radius + 0.001), 0.0, 0.0034),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["trim"],
            name=f"{tag}__axis_boss_{'left' if sign < 0 else 'right'}", material_class_id="plastic.opaque_glossy_molded",
        )
    rocker = model.part(
        f"{tag}__wheel",
        meta={"role": "volume_rocker", "slot": "primary_control", "candidate": r.primary_control},
    )
    rocker.visual(
        Cylinder(radius=radius, length=0.0032),
        material=mats["button"],
        name=f"{tag}__disc", material_class_id="plastic.opaque_glossy_molded",
    )
    rocker.visual(
        Box((radius * 0.75, 0.0010, 0.0035)),
        origin=Origin(xyz=(0.0, radius * 0.28, 0.0012)),
        material=mats["legend"],
        name=f"{tag}__plus_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    provider = AxisInterface(
        name="primary_carrier.rocker_axis",
        point=(0.0, 0.0, 0.0034),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0022,
    )
    consumer = AxisInterface(
        name="primary_control.rotation_axis",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0018,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__joint"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=carrier,
        child=rocker,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=1.5,
            velocity=1.5,
            lower=-r.rocker_angle_rad,
            upper=r.rocker_angle_rad,
        ),
    )
    register_interface_mate(model, joint, mate)


def _primary_control_jog_wheel_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    tag = "primary_control__jog_wheel"
    radius = r.jog_diameter_m / 2.0
    carrier = _fixed_carrier(
        model,
        body,
        r,
        slot="primary_control",
        candidate=r.primary_control,
        role="primary_carrier",
        center_y=r.primary_center_y_m,
        extent=(r.jog_diameter_m + 0.006, r.jog_diameter_m + 0.006),
    )
    carrier.visual(
        Cylinder(radius=radius + 0.0025, length=_CARRIER_THICKNESS),
        origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS / 2.0)),
        material=mats["trim"],
        name=f"{tag}__well", material_class_id="plastic.opaque_glossy_molded",
    )
    carrier.visual(
        Cylinder(radius=0.0030, length=0.0020),
        origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS + 0.0010)),
        material=mats["trim"],
        name=f"{tag}__axis_boss", material_class_id="plastic.opaque_glossy_molded",
    )
    wheel = model.part(
        f"{tag}__wheel",
        meta={"role": "jog_wheel", "slot": "primary_control", "candidate": r.primary_control},
    )
    wheel.visual(
        Cylinder(radius=radius, length=0.0032),
        origin=Origin(xyz=(0.0, 0.0, 0.0016)),
        material=mats["button"],
        name=f"{tag}__disc", material_class_id="plastic.opaque_glossy_molded",
    )
    wheel.visual(
        Cylinder(radius=radius * 0.34, length=0.0040),
        origin=Origin(xyz=(0.0, 0.0, 0.0020)),
        material=mats["trim"],
        name=f"{tag}__hub", material_class_id="plastic.opaque_glossy_molded",
    )
    for index in range(16):
        angle = 2.0 * math.pi * index / 16.0
        wheel.visual(
            Box((0.0010, radius * 0.28, 0.0035)),
            origin=Origin(
                xyz=(
                    radius * 0.82 * math.cos(angle),
                    radius * 0.82 * math.sin(angle),
                    0.00175,
                ),
                rpy=(0.0, 0.0, angle),
            ),
            material=mats["button"],
            name=f"{tag}__knurl_{index:02d}", material_class_id="plastic.opaque_glossy_molded",
        )
    provider = AxisInterface(
        name="primary_carrier.jog_axis",
        point=(0.0, 0.0, _CARRIER_THICKNESS + 0.0020),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0030,
    )
    consumer = AxisInterface(
        name="primary_control.rotation_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0025,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__joint"
    model.articulation(
        joint,
        ArticulationType.CONTINUOUS,
        parent=carrier,
        child=wheel,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=0.8, velocity=4.0),
    )
    register_interface_mate(model, joint, mate)


_PRIMARY_BUILDERS = {
    "directional_pad": _primary_control_directional_pad_build,
    "volume_rocker": _primary_control_volume_rocker_build,
    "jog_wheel": _primary_control_jog_wheel_build,
}


def _button_positions(r: ResolvedConfig):
    rows = math.ceil(r.button_count / 3)
    positions = []
    remaining = r.button_count
    for row in range(rows):
        count = min(3, remaining)
        for column in range(count):
            x = (column - (count - 1) / 2.0) * r.button_pitch_x_m
            y = (rows - 1) * r.button_pitch_y_m / 2.0 - row * r.button_pitch_y_m
            positions.append((x, y))
        remaining -= count
    return tuple(positions)


def _build_button_array(
    model: ArticulatedObject,
    body,
    r: ResolvedConfig,
    mats,
    *,
    candidate: str,
    rounded: bool,
) -> None:
    tag = f"button_array__{candidate}"
    bed = _fixed_carrier(
        model,
        body,
        r,
        slot="button_array",
        candidate=candidate,
        role="button_bed",
        center_y=r.button_bed_center_y_m,
        extent=(r.button_bed_width_m, r.button_bed_length_m),
    )
    bed.visual(
        Box((r.button_bed_width_m, r.button_bed_length_m, _CARRIER_THICKNESS)),
        origin=Origin(xyz=(0.0, 0.0, _CARRIER_THICKNESS / 2.0)),
        material=mats["trim"],
        name=f"{tag}__recess_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    size = r.media_button_diameter_m if rounded else r.numeric_key_width_m
    travel = r.media_button_travel_m if rounded else r.numeric_key_travel_m
    for index, (x, y) in enumerate(_button_positions(r)):
        button = model.part(
            f"{tag}__button_{index:02d}",
            meta={"role": "press_button", "slot": "button_array", "candidate": candidate},
        )
        if rounded:
            button.visual(
                Cylinder(radius=size / 2.0, length=_BUTTON_HEIGHT),
                origin=Origin(xyz=(0.0, 0.0, _BUTTON_HEIGHT / 2.0)),
                material=mats["button"],
                name=f"{tag}__round_cap", material_class_id="plastic.opaque_glossy_molded",
            )
            button.visual(
                Cylinder(radius=size * 0.09, length=0.00035),
                origin=Origin(xyz=(0.0, 0.0, _BUTTON_HEIGHT + 0.000175)),
                material=mats["legend"],
                name=f"{tag}__media_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
        else:
            cap_profile = rounded_rect_profile(size, size, radius=size * 0.20, corner_segments=5)
            button.visual(
                _prism(cap_profile, 0.0, _BUTTON_HEIGHT, f"{tag}__square_cap"),
                material=mats["button"],
                name=f"{tag}__square_cap", material_class_id="plastic.opaque_glossy_molded",
            )
            bar_count = 1 + index % 3
            for bar in range(bar_count):
                button.visual(
                    Box((size * 0.48, 0.00045, 0.00025)),
                    origin=Origin(
                        xyz=(
                            0.0,
                            (bar - (bar_count - 1) / 2.0) * 0.0012,
                            _BUTTON_HEIGHT + 0.000125,
                        )
                    ),
                    material=mats["legend"],
                    name=f"{tag}__digit_bar_{bar}", appearance_only=AppearanceOnlySpec(kind="overlay"),
                )
        model.articulation(
            f"{tag}__press_joint_{index:02d}",
            ArticulationType.PRISMATIC,
            parent=bed,
            child=button,
            origin=Origin(xyz=(x, y, _CARRIER_THICKNESS + _BUTTON_GAP)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=1.0, velocity=0.08, lower=0.0, upper=travel),
            meta={"motion_qc_repeat_group": "remote_button_press"},
        )


def _button_array_media_round_grid_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    _build_button_array(
        model, body, r, mats, candidate="media_round_grid", rounded=True
    )


def _button_array_numeric_square_grid_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    _build_button_array(
        model, body, r, mats, candidate="numeric_square_grid", rounded=False
    )


_BUTTON_BUILDERS = {
    "media_round_grid": _button_array_media_round_grid_build,
    "numeric_square_grid": _button_array_numeric_square_grid_build,
}


def _cover_carrier(model: ArticulatedObject, body, r: ResolvedConfig):
    if r.cover_module == "open_face":
        anchor = (0.0, -r.cover_length_m / 2.0 + 0.0015, 0.0)
    elif r.cover_module == "flip_cover":
        anchor = (0.0, r.cover_length_m / 2.0, 0.0)
    else:
        anchor = (-r.rail_spacing_m, 0.0, 0.0)
    mount = _fixed_carrier(
        model,
        body,
        r,
        slot="cover_module",
        candidate=r.cover_module,
        role="cover_mount",
        center_y=r.button_bed_center_y_m,
        extent=(r.cover_width_m, r.cover_length_m),
        consumer_point=anchor,
    )
    mount.visual(
        Box((r.cover_width_m, r.cover_length_m, 0.0006)),
        origin=Origin(xyz=(0.0, 0.0, 0.0003)),
        material="trim",
        name=f"cover_module__{r.cover_module}__support_recess", material_class_id="plastic.opaque_glossy_molded",
    )
    return mount


def _cover_module_open_face_build(model: ArticulatedObject, body, r: ResolvedConfig, mats) -> None:
    tag = "cover_module__open_face"
    mount = _cover_carrier(model, body, r)
    mount.visual(
        Box((r.cover_width_m, 0.0030, 0.0010)),
        origin=Origin(xyz=(0.0, -r.cover_length_m / 2.0 + 0.0015, 0.0005)),
        material=mats["trim"],
        name=f"{tag}__lower_bezel", material_class_id="plastic.opaque_glossy_molded",
    )


def _cover_module_flip_cover_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    tag = "cover_module__flip_cover"
    mount = _cover_carrier(model, body, r)
    hinge_y = r.cover_length_m / 2.0
    hinge_z = 0.008
    mount.visual(
        Box((min(r.cover_width_m * 0.45, 0.025), 0.006, hinge_z)),
        origin=Origin(xyz=(0.0, hinge_y, hinge_z / 2.0)),
        material=mats["trim"],
        name=f"{tag}__hinge_boss", material_class_id="plastic.opaque_glossy_molded",
    )
    mount.visual(
        Cylinder(radius=0.0024, length=min(r.cover_width_m * 0.72, 0.035)),
        origin=Origin(xyz=(0.0, hinge_y, hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["trim"],
        name=f"{tag}__knuckle", material_class_id="plastic.opaque_glossy_molded",
    )
    cover = model.part(
        f"{tag}__panel",
        meta={"role": "protective_cover", "slot": "cover_module", "candidate": r.cover_module},
    )
    panel_profile = rounded_rect_profile(
        r.cover_width_m, r.cover_length_m, radius=0.005, corner_segments=6
    )
    shifted = tuple((x, y - r.cover_length_m / 2.0) for x, y in panel_profile)
    cover.visual(
        _prism(shifted, 0.0, 0.0020, f"{tag}__panel_shell"),
        material=mats["cover"],
        name=f"{tag}__panel_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    cover.visual(
        Box((r.cover_width_m * 0.42, 0.0020, 0.0007)),
        origin=Origin(xyz=(0.0, -r.cover_length_m + 0.010, 0.00235)),
        material=mats["trim"],
        name=f"{tag}__finger_ridge", material_class_id="plastic.opaque_glossy_molded",
    )
    provider = AxisInterface(
        name="cover_mount.hinge_axis",
        point=(0.0, hinge_y, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0024,
    )
    consumer = AxisInterface(
        name="cover_module.hinge_axis",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0020,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__joint"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=mount,
        child=cover,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=2.0, velocity=1.5, lower=-r.flip_cover_angle_rad, upper=0.0
        ),
    )
    register_interface_mate(model, joint, mate)


def _cover_module_slide_cover_build(
    model: ArticulatedObject, body, r: ResolvedConfig, mats
) -> None:
    tag = "cover_module__slide_cover"
    mount = _cover_carrier(model, body, r)
    rail_h = 0.008
    rail_run = r.cover_length_m + r.slide_cover_travel_m
    for index, x in enumerate((-r.rail_spacing_m, r.rail_spacing_m)):
        mount.visual(
            Box((0.0030, rail_run, rail_h)),
            origin=Origin(xyz=(x, r.slide_cover_travel_m / 2.0, rail_h / 2.0)),
            material=mats["trim"],
            name=f"{tag}__rail_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    mount.visual(
        Box((r.cover_width_m, 0.0030, rail_h)),
        origin=Origin(xyz=(0.0, -r.cover_length_m / 2.0 + 0.0015, rail_h / 2.0)),
        material=mats["trim"],
        name=f"{tag}__rail_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    cover = model.part(
        f"{tag}__panel",
        meta={"role": "protective_cover", "slot": "cover_module", "candidate": r.cover_module},
    )
    cover.visual(
        Box((r.cover_width_m, r.cover_length_m, 0.0020)),
        origin=Origin(xyz=(0.0, 0.0, 0.0010)),
        material=mats["cover"],
        name=f"{tag}__panel_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    cover.visual(
        Box((r.cover_width_m * 0.45, 0.0020, 0.0008)),
        origin=Origin(xyz=(0.0, -r.cover_length_m * 0.30, 0.0024)),
        material=mats["trim"],
        name=f"{tag}__finger_ridge", material_class_id="plastic.opaque_glossy_molded",
    )
    model.articulation(
        f"{tag}__joint",
        ArticulationType.PRISMATIC,
        parent=mount,
        child=cover,
        origin=Origin(xyz=(0.0, 0.0, rail_h - 0.0002)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0,
            velocity=0.12,
            lower=0.0,
            upper=r.slide_cover_travel_m,
        ),
    )


_COVER_BUILDERS = {
    "open_face": _cover_module_open_face_build,
    "flip_cover": _cover_module_flip_cover_build,
    "slide_cover": _cover_module_slide_cover_build,
}


def build_remote_control(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    body = model.part(
        "remote_body",
        meta={
            "role": "remote_body",
            "slot": "enclosure_family",
            "candidate": r.enclosure_family,
        },
    )
    _ENCLOSURE_BUILDERS[r.enclosure_family](body, r, mats)
    _PRIMARY_BUILDERS[r.primary_control](model, body, r, mats)
    _BUTTON_BUILDERS[r.button_array](model, body, r, mats)
    _COVER_BUILDERS[r.cover_module](model, body, r, mats)
    model.meta["slot_choices"] = (
        ("enclosure_family", r.enclosure_family),
        ("primary_control", r.primary_control),
        ("button_array", r.button_array),
        ("cover_module", r.cover_module),
        ("button_count", str(r.button_count)),
    )
    model.meta["button_count_actual"] = r.button_count
    return model


def build_seeded_remote_control(seed: int) -> ArticulatedObject:
    return build_remote_control(config_from_seed(seed))


def run_remote_control_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[object]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part)

    body = object_model.get_part("remote_body")
    body_aabb = ctx.part_world_aabb(body)
    body_size = tuple(body_aabb[1][i] - body_aabb[0][i] for i in range(3))
    ctx.check(
        "category_anchor: remote body is handheld and front-faced",
        len(roles.get("remote_body", [])) == 1
        and body_size[1] > body_size[0] * 2.2
        and body_size[2] < 0.025,
        details=f"body_size={body_size}",
    )
    buttons = roles.get("press_button", [])
    ctx.check(
        "category_anchor: repeated button count matches multiplicity",
        len(buttons) == r.button_count
        and int(object_model.meta.get("button_count_actual", 0)) == r.button_count,
        details=f"parts={len(buttons)} expected={r.button_count}",
    )

    moving_buttons = roles.get("press_button", []) + roles.get("directional_button", [])
    all_press = True
    for button in moving_buttons:
        joints = [joint for joint in object_model.articulations if joint.child == button.name]
        if len(joints) != 1:
            all_press = False
            continue
        joint = joints[0]
        rest = ctx.part_world_position(button)
        upper = float(joint.motion_limits.upper or 0.0)
        with ctx.pose({joint: upper}):
            pressed = ctx.part_world_position(button)
        all_press = (
            all_press
            and rest is not None
            and pressed is not None
            and pressed[2] < rest[2] - upper * 0.45
        )
    ctx.check(
        "category_anchor: every visible button has independent press travel",
        len(moving_buttons) >= r.button_count and all_press,
        details=f"moving_buttons={len(moving_buttons)}",
    )

    if r.primary_control == "directional_pad":
        ctx.check(
            "category_anchor: directional pad has four sectors and center mode key",
            len(roles.get("primary_carrier", [])) == 1
            and len(roles.get("directional_button", [])) == 5,
            details=f"directional_buttons={len(roles.get('directional_button', []))}",
        )
    elif r.primary_control == "volume_rocker":
        joint = object_model.get_articulation("primary_control__volume_rocker__joint")
        ctx.check(
            "category_anchor: volume rocker tilts on its visible boss",
            len(roles.get("volume_rocker", [])) == 1
            and tuple(joint.axis) == (1.0, 0.0, 0.0),
            details=f"axis={joint.axis}",
        )
    else:
        joint = object_model.get_articulation("primary_control__jog_wheel__joint")
        ctx.check(
            "category_anchor: jog wheel spins about the front-face normal",
            len(roles.get("jog_wheel", [])) == 1
            and tuple(joint.axis) == (0.0, 0.0, 1.0),
            details=f"axis={joint.axis}",
        )

    if r.cover_module == "flip_cover":
        cover = roles.get("protective_cover", [None])[0]
        joint = object_model.get_articulation("cover_module__flip_cover__joint")
        closed = ctx.part_world_aabb(cover)
        with ctx.pose({joint: -r.flip_cover_angle_rad}):
            opened = ctx.part_world_aabb(cover)
        ctx.check(
            "category_anchor: flip cover opens away from the button field",
            cover is not None
            and closed is not None
            and opened is not None
            and opened[1][2] > closed[1][2] + 0.010,
            details=f"closed_z={closed[1][2] if closed else None} opened_z={opened[1][2] if opened else None}",
        )
    elif r.cover_module == "slide_cover":
        cover = roles.get("protective_cover", [None])[0]
        joint = object_model.get_articulation("cover_module__slide_cover__joint")
        closed = ctx.part_world_position(cover)
        with ctx.pose({joint: r.slide_cover_travel_m}):
            opened = ctx.part_world_position(cover)
        ctx.check(
            "category_anchor: slide cover travels on visible longitudinal rails",
            cover is not None
            and closed is not None
            and opened is not None
            and opened[1] > closed[1] + r.slide_cover_travel_m * 0.8,
            details=f"closed={closed} opened={opened}",
        )
    return ctx.report()


run_remote_control_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "waisted_dpad_numeric_max_flip",
        {
            "enclosure_family": "ergonomic_waisted",
            "primary_control": "directional_pad",
            "button_array": "numeric_square_grid",
            "cover_module": "flip_cover",
            "button_count": 12,
            "waist_ratio": 0.72,
            "dpad_diameter_m": 0.048,
            "dpad_travel_m": 0.0018,
            "numeric_key_width_m": 0.012,
            "numeric_key_travel_m": 0.0014,
            "flip_cover_angle_rad": 1.85,
        },
        reason="narrowest waist with largest directional pad, keypad, and flip-cover envelope",
    ),
    corner_case(
        "tapered_jog_media_max_slide",
        {
            "enclosure_family": "tapered_wand",
            "primary_control": "jog_wheel",
            "button_array": "media_round_grid",
            "cover_module": "slide_cover",
            "button_count": 12,
            "taper_ratio": 0.68,
            "jog_diameter_m": 0.036,
            "media_button_diameter_m": 0.012,
            "media_button_travel_m": 0.0014,
            "slide_cover_travel_m": 0.070,
        },
        reason="narrowest tapered tail with the largest spinning control and longest rail travel",
    ),
    corner_case(
        "slim_rocker_numeric_min_open",
        {
            "enclosure_family": "slim_wand",
            "primary_control": "volume_rocker",
            "button_array": "numeric_square_grid",
            "cover_module": "open_face",
            "button_count": 4,
            "wand_width_m": 0.050,
            "rocker_diameter_m": 0.034,
            "rocker_angle_rad": 0.22,
            "numeric_key_width_m": 0.012,
        },
        reason="minimum host width with largest tilting rocker and asymmetric four-key grid",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_remote_control",
    "build_seeded_remote_control",
    "config_from_seed",
    "resolve_config",
    "run_remote_control_tests",
]
