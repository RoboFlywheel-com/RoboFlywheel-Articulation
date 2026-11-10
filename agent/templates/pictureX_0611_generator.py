# SPDX-License-Identifier: Apache-2.0

"""Self-contained hand-driven demonstration generator template.

The grounded ``frame`` part carries two parallel +y shaft lines on open saddle
bearings — the input line at ``-centre_distance/2`` and the armature line at
``+centre_distance/2``.  Each saddle is a real cheek-and-pad bearing that the
shaft rests in with a 1 mm running clearance, so no shaft is ever driven into a
solid standard.  The ``input`` part turns CONTINUOUS on the first line and the
``rotor`` part turns CONTINUOUS on the second, mimic-coupled at the ratio of the
two wheel radii, which are themselves derived from the shaft centre distance.

Three slots vary without touching that chain: ``drive_input`` (offset crank with
a spinning grip, twin opposed cranks, spoked handwheel, rimmed flywheel),
``transmission`` (jackshaft pulley train, meshed spur pair, paired pulleys with
the flexible belt intentionally omitted, an upper idler wheel,
friction wheels with a PRISMATIC tension carrier, right-angle bevel transfer)
and ``stator_form`` (open pole pieces,
slotted U-bridge, twin magnet posts, bolted gearbox side plate).
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
    Mimic,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

DriveInput = Literal["crank_handle", "dual_crank", "handwheel_input", "flywheel_input"]
Transmission = Literal[
    "shaft_pulley_train",
    "spur_gear_pair",
    "belt_two_pulley",
    "idler_tension_pulley",
    "friction_wheel",
    "bevel_gear",
]
StatorForm = Literal[
    "open_pole_stator",
    "slotted_stator_bridge",
    "twin_magnet_posts",
    "gearbox_side_plate",
]
PaletteStyle = Literal["works_green", "lab_grey", "brass_demo", "red_frame"]

DRIVE_INPUTS: tuple[DriveInput, ...] = (
    "crank_handle",
    "dual_crank",
    "handwheel_input",
    "flywheel_input",
)
TRANSMISSIONS: tuple[Transmission, ...] = (
    "shaft_pulley_train",
    "spur_gear_pair",
    "belt_two_pulley",
    "idler_tension_pulley",
    "friction_wheel",
    "bevel_gear",
)
STATOR_FORMS: tuple[StatorForm, ...] = (
    "open_pole_stator",
    "slotted_stator_bridge",
    "twin_magnet_posts",
    "gearbox_side_plate",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "works_green",
    "lab_grey",
    "brass_demo",
    "red_frame",
)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("drive_input", DRIVE_INPUTS),
        component_slot("transmission", TRANSMISSIONS),
        component_slot("stator_form", STATOR_FORMS),
        multiplicity_slot("coil_count", (1, 2, 3), item_slot="stator_form"),
        multiplicity_slot("terminal_count", (2, 3, 4), item_slot="stator_form"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "works_green": {
        "frame": (0.18, 0.38, 0.28, 1.0),
        "steel": (0.72, 0.74, 0.76, 1.0),
        "dark": (0.14, 0.15, 0.16, 1.0),
        "copper": (0.72, 0.44, 0.20, 1.0),
        "accent": (0.86, 0.72, 0.24, 1.0),
    },
    "lab_grey": {
        "frame": (0.52, 0.54, 0.56, 1.0),
        "steel": (0.80, 0.81, 0.82, 1.0),
        "dark": (0.18, 0.19, 0.20, 1.0),
        "copper": (0.74, 0.46, 0.22, 1.0),
        "accent": (0.24, 0.50, 0.76, 1.0),
    },
    "brass_demo": {
        "frame": (0.62, 0.50, 0.24, 1.0),
        "steel": (0.84, 0.85, 0.86, 1.0),
        "dark": (0.16, 0.14, 0.12, 1.0),
        "copper": (0.78, 0.50, 0.24, 1.0),
        "accent": (0.90, 0.84, 0.40, 1.0),
    },
    "red_frame": {
        "frame": (0.62, 0.18, 0.16, 1.0),
        "steel": (0.78, 0.79, 0.80, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0),
        "copper": (0.72, 0.44, 0.20, 1.0),
        "accent": (0.90, 0.88, 0.84, 1.0),
    },
}


# Fixed manufacturing cross-sections (surface detail, not core/raw).
BASE_T = 0.010
STAND_Y = 0.030
STAND_HALF_T = 0.004
SHAFT_R = 0.005
WHEEL_Y = STAND_Y + 0.016
WHEEL_HALF_T = 0.005
CRANK_Y = -(STAND_Y + 0.026)
GRIP_R = 0.009
WHEEL_GAP = 0.004
FIT_GAP = 0.001

# (drive wheel fraction, driven wheel fraction) of the shaft centre distance.
WHEEL_FRACTIONS: dict[Transmission, tuple[float, float]] = {
    "shaft_pulley_train": (0.18, 0.16),
    "spur_gear_pair": (0.42, 0.24),
    "belt_two_pulley": (0.30, 0.14),
    "idler_tension_pulley": (0.28, 0.13),
    "friction_wheel": (0.38, 0.26),
    "bevel_gear": (0.20, 0.16),
}
WHEEL_HEAD_ROOM = 0.024   # every wheel keeps this much air under it above the base


@dataclass(frozen=True)
class Config:
    drive_input: DriveInput = "crank_handle"
    transmission: Transmission = "belt_two_pulley"
    stator_form: StatorForm = "open_pole_stator"
    coil_count: int = 2
    terminal_count: int = 2
    shaft_height_m: float | None = None
    centre_distance_m: float | None = None
    rotor_radius_m: float | None = None
    palette_style: PaletteStyle = "works_green"
    name: str = "pictureX_0611_generator"


@dataclass(frozen=True)
class ResolvedConfig:
    drive_input: DriveInput
    transmission: Transmission
    stator_form: StatorForm
    coil_count: int
    terminal_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    shaft_height_m: float
    centre_distance_m: float
    rotor_radius_m: float
    input_x_m: float
    rotor_x_m: float
    drive_wheel_radius_m: float
    driven_wheel_radius_m: float
    drive_ratio: float
    crank_radius_m: float
    coil_pitch_rad: float
    terminal_span_m: float
    terminal_pitch_m: float
    pole_gap_m: float
    base_x0_m: float
    base_x1_m: float
    stand_top_z_m: float
    input_shaft_y0_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x77_C1_3E_45)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        drive_input=choices["drive_input"],
        transmission=choices["transmission"],
        stator_form=choices["stator_form"],
        coil_count=choices["coil_count"],
        terminal_count=choices["terminal_count"],
        shaft_height_m=round(rng.uniform(0.055, 0.100), 4),
        centre_distance_m=round(rng.uniform(0.075, 0.130), 4),
        rotor_radius_m=round(rng.uniform(0.018, 0.032), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"generator_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "drive_input": config.drive_input,
            "transmission": config.transmission,
            "stator_form": config.stator_form,
            "coil_count": config.coil_count,
            "terminal_count": config.terminal_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.shaft_height_m is not None and not 0.055 <= float(config.shaft_height_m) <= 0.100:
        raise ValueError("shaft_height_m must be in [0.055, 0.100]")
    if (
        config.centre_distance_m is not None
        and not 0.075 <= float(config.centre_distance_m) <= 0.130
    ):
        raise ValueError("centre_distance_m must be in [0.075, 0.130]")
    if config.rotor_radius_m is not None and not 0.018 <= float(config.rotor_radius_m) <= 0.032:
        raise ValueError("rotor_radius_m must be in [0.018, 0.032]")

    height = (
        _clamp(config.shaft_height_m, 0.055, 0.100)
        if config.shaft_height_m is not None
        else 0.075
    )
    centre = (
        _clamp(config.centre_distance_m, 0.075, 0.130)
        if config.centre_distance_m is not None
        else 0.100
    )
    rotor_r = (
        _clamp(config.rotor_radius_m, 0.018, 0.032)
        if config.rotor_radius_m is not None
        else 0.024
    )

    drive_frac, driven_frac = WHEEL_FRACTIONS[config.transmission]
    head = height - WHEEL_HEAD_ROOM
    drive_r = min(drive_frac * centre, head)
    driven_r = min(driven_frac * centre - 0.5 * WHEEL_GAP, head)
    ratio = drive_r / driven_r
    coils = int(config.coil_count)
    terminals = int(config.terminal_count)
    span = 0.050
    shaft_y0 = CRANK_Y + {
        "crank_handle": -0.036,
        "dual_crank": -0.096,
        "handwheel_input": -0.012,
        "flywheel_input": -0.062,
    }[config.drive_input]
    return ResolvedConfig(
        drive_input=config.drive_input,
        transmission=config.transmission,
        stator_form=config.stator_form,
        coil_count=coils,
        terminal_count=terminals,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        shaft_height_m=height,
        centre_distance_m=centre,
        rotor_radius_m=rotor_r,
        input_x_m=-0.5 * centre,
        rotor_x_m=0.5 * centre,
        drive_wheel_radius_m=drive_r,
        driven_wheel_radius_m=driven_r,
        drive_ratio=ratio,
        crank_radius_m=0.36 * height,
        coil_pitch_rad=2.0 * math.pi / coils,
        terminal_span_m=span,
        terminal_pitch_m=span / max(1, terminals - 1),
        pole_gap_m=rotor_r + 0.005,
        base_x0_m=-0.5 * centre - 0.030,
        base_x1_m=0.5 * centre + 0.060,
        stand_top_z_m=height - 0.013,
        input_shaft_y0_m=shaft_y0,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("drive_input", config.drive_input),
        ("transmission", config.transmission),
        ("stator_form", config.stator_form),
        ("coil_count", config.coil_count),
        ("terminal_count", config.terminal_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"gen_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def _local_origin(
    origin: Origin | None, offset: tuple[float, float, float]
) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _disc_y(part, offset, x, y, z, radius, thickness, material, name) -> None:
    """A wheel on a +y axis — a body of revolution, so rotation sweeps nothing new."""
    part.visual(
        Cylinder(radius=radius, length=thickness),
        origin=_local_origin(
            Origin(xyz=(x, y, z), rpy=(math.pi / 2.0, 0.0, 0.0)), offset
        ),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _saddle(
    part, offset, r: ResolvedConfig, axis_x: float, stand_y: float, mats, name: str
) -> None:
    """Open cheek-and-pad bearing: the shaft rests in it with a 1 mm running gap."""
    z = r.shaft_height_m
    for cheek_index, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.006, 2.0 * STAND_HALF_T, 0.028)),
            origin=_local_origin(
                Origin(xyz=(axis_x + sx * 0.010, stand_y, z - 0.001)), offset
            ),
            material=mats["steel"],
            name=f"{name}__cheek_{cheek_index}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Box((0.026, 2.0 * STAND_HALF_T, 0.006)),
        origin=_local_origin(Origin(xyz=(axis_x, stand_y, z - 0.0075)), offset),
        material=mats["steel"],
        name=f"{name}__pad", material_class_id="metal.steel_bare",
    )


def _frame_common(host, r: ResolvedConfig, mats: dict[str, str]) -> None:
    host.visual(
        Box((r.base_x1_m - r.base_x0_m, 2.0 * (STAND_Y + 0.010), BASE_T)),
        origin=Origin(xyz=(0.5 * (r.base_x0_m + r.base_x1_m), 0.0, 0.5 * BASE_T)),
        material=mats["frame"],
        name="frame__base_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    for stand_index, sy in enumerate((-1.0, 1.0)):
        host.visual(
            Box(
                (
                    r.centre_distance_m + 0.040,
                    2.0 * STAND_HALF_T,
                    r.stand_top_z_m - 0.008,
                )
            ),
            origin=Origin(
                xyz=(0.0, sy * STAND_Y, 0.5 * (0.008 + r.stand_top_z_m))
            ),
            material=mats["frame"],
            name=f"frame__standard_{stand_index}", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
        )
        _saddle(
            host,
            (0.0, 0.0, 0.0),
            r,
            r.input_x_m,
            sy * STAND_Y,
            mats,
            f"frame__input_saddle_{stand_index}",
        )
        _saddle(
            host,
            (0.0, 0.0, 0.0),
            r,
            r.rotor_x_m,
            sy * STAND_Y,
            mats,
            f"frame__rotor_saddle_{stand_index}",
        )


def _stator_column(host, r: ResolvedConfig, mats, x: float, top_z: float, name: str) -> None:
    """A column from the base up to a stator feature, at the armature plane."""
    host.visual(
        Box((0.012, 0.026, top_z - 0.008)),
        origin=Origin(xyz=(x, 0.0, 0.5 * (0.008 + top_z))),
        material=mats["frame"],
        name=name, material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )


def _coils_and_terminals(frame, rotor, rotor_offset, r: ResolvedConfig, mats) -> None:
    """Coil packs on the armature and terminal posts on the base pad."""
    pack = 0.34 * r.rotor_radius_m
    for k in range(r.coil_count):
        angle = k * r.coil_pitch_rad
        radius = 0.52 * r.rotor_radius_m
        rotor.visual(
            Box((pack, 0.024, pack)),
            origin=_local_origin(
                Origin(
                    xyz=(
                        r.rotor_x_m + radius * math.cos(angle),
                        0.0,
                        r.shaft_height_m + radius * math.sin(angle),
                    ),
                    rpy=(0.0, -angle, 0.0),
                ),
                rotor_offset,
            ),
            material=mats["copper"],
            name=f"stator_form__coil_pack_{k}", material_class_id="metal.copper_bare",
        )
    pad_x = r.rotor_x_m + 0.040
    frame.visual(
        Box((0.020, r.terminal_span_m + 0.016, 0.006)),
        origin=Origin(xyz=(pad_x, 0.0, BASE_T + 0.003)),
        material=mats["dark"],
        name="stator_form__terminal_pad", material_class_id="plastic.opaque_generic",
    )
    for k in range(r.terminal_count):
        y = -0.5 * r.terminal_span_m + k * r.terminal_pitch_m
        frame.visual(
            Cylinder(radius=0.0035, length=0.016),
            origin=Origin(xyz=(pad_x, y, BASE_T + 0.012)),
            material=mats["steel"],
            name=f"stator_form__terminal_post_{k}", material_class_id="metal.steel_bare",
        )
        frame.visual(
            Cylinder(radius=0.0055, length=0.006),
            origin=Origin(xyz=(pad_x, y, BASE_T + 0.021)),
            material=mats["accent"],
            name=f"stator_form__terminal_cap_{k}", material_class_id=("metal.brass_polished" if r.palette_style in {"works_green", "brass_demo"} else "plastic.opaque_glossy_molded"),
        )


# --- stator candidates ----------------------------------------------------------
def _stator_form_open_pole_stator_build(frame, rotor, rotor_offset, r: ResolvedConfig, mats) -> None:
    for pole_index, sx in enumerate((-1.0, 1.0)):
        x = r.rotor_x_m + sx * (r.pole_gap_m + 0.006)
        _stator_column(
            frame, r, mats, x, r.shaft_height_m, f"stator_form__open_pole_stator__column_{pole_index}"
        )
        frame.visual(
            Box((0.010, 0.030, 0.036)),
            origin=Origin(xyz=(x, 0.0, r.shaft_height_m)),
            material=mats["steel"],
            name=f"stator_form__open_pole_stator__pole_shoe_{pole_index}", material_class_id="metal.steel_bare",
        )
    _coils_and_terminals(frame, rotor, rotor_offset, r, mats)


def _stator_form_slotted_stator_bridge_build(
    frame, rotor, rotor_offset, r: ResolvedConfig, mats
) -> None:
    top_z = r.shaft_height_m + r.pole_gap_m + 0.012
    for leg_index, sx in enumerate((-1.0, 1.0)):
        x = r.rotor_x_m + sx * (r.pole_gap_m + 0.006)
        _stator_column(
            frame, r, mats, x, top_z,
            f"stator_form__slotted_stator_bridge__leg_{leg_index}",
        )
        frame.visual(
            Box((0.012, 0.028, 0.030)),
            origin=Origin(
                xyz=(r.rotor_x_m + sx * (r.pole_gap_m + 0.006), 0.0, r.shaft_height_m)
            ),
            material=mats["steel"],
            name=f"stator_form__slotted_stator_bridge__pole_pad_{leg_index}", material_class_id="metal.steel_bare",
        )
    frame.visual(
        Box((2.0 * (r.pole_gap_m + 0.012), 0.028, 0.012)),
        origin=Origin(xyz=(r.rotor_x_m, 0.0, top_z - 0.006)),
        material=mats["steel"],
        name="stator_form__slotted_stator_bridge__bridge", material_class_id="metal.steel_bare",
    )
    for slot_index in (-1, 0, 1):
        frame.visual(
            Box((0.006, 0.030, 0.006)),
            origin=Origin(
                xyz=(r.rotor_x_m + slot_index * 0.014, 0.0, top_z + 0.003)
            ),
            material=mats["dark"],
            name=f"stator_form__slotted_stator_bridge__slot_rib_{slot_index + 1}", material_class_id="metal.blackened_gunmetal",
        )
    _coils_and_terminals(frame, rotor, rotor_offset, r, mats)


def _stator_form_twin_magnet_posts_build(
    frame, rotor, rotor_offset, r: ResolvedConfig, mats
) -> None:
    top_z = r.shaft_height_m + r.rotor_radius_m + 0.020
    for post_index, sx in enumerate((-1.0, 1.0)):
        x = r.rotor_x_m + sx * (r.pole_gap_m + 0.008)
        frame.visual(
            Box((0.016, 0.030, top_z - 0.008)),
            origin=Origin(xyz=(x, 0.0, 0.5 * (0.008 + top_z))),
            material=mats["dark"],
            name=f"stator_form__twin_magnet_posts__magnet_post_{post_index}", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Box((0.014, 0.026, 0.032)),
            origin=Origin(
                xyz=(r.rotor_x_m + sx * (r.pole_gap_m + 0.007), 0.0, r.shaft_height_m)
            ),
            material=mats["steel"],
            name=f"stator_form__twin_magnet_posts__pole_pad_{post_index}", material_class_id="metal.steel_bare",
        )
    _coils_and_terminals(frame, rotor, rotor_offset, r, mats)


def _stator_form_gearbox_side_plate_build(
    frame, rotor, rotor_offset, r: ResolvedConfig, mats
) -> None:
    # Keep the enclosure behind the exposed transmission plane so the pulley
    # rims and belt contacts remain readable from the operating side.
    plate_y = WHEEL_Y - 0.014
    frame.visual(
        Box((r.centre_distance_m + 0.050, 0.006, r.shaft_height_m + 0.034)),
        origin=Origin(xyz=(0.0, plate_y, 0.5 * (r.shaft_height_m + 0.034) + 0.004)),
        material=mats["frame"],
        name="stator_form__gearbox_side_plate__side_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    frame.visual(
        Box((0.024, plate_y - STAND_Y + 0.014, 0.012)),
        origin=Origin(
            xyz=(0.0, 0.5 * (STAND_Y + plate_y) - 0.002, BASE_T + 0.002)
        ),
        material=mats["frame"],
        name="stator_form__gearbox_side_plate__plate_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    for boss_index in range(4):
        angle = boss_index * math.pi / 2.0 + math.pi / 4.0
        frame.visual(
            Cylinder(radius=0.005, length=0.006),
            origin=Origin(
                xyz=(
                    r.rotor_x_m + 0.040 * math.cos(angle),
                    plate_y - 0.005,
                    r.shaft_height_m + 0.040 * math.sin(angle),
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["steel"],
            name=f"stator_form__gearbox_side_plate__cover_bolt_{boss_index}", material_class_id="metal.steel_bare",
        )
    for pole_index, sx in enumerate((-1.0, 1.0)):
        x = r.rotor_x_m + sx * (r.pole_gap_m + 0.006)
        _stator_column(
            frame, r, mats, x, r.shaft_height_m,
            f"stator_form__gearbox_side_plate__pole_column_{pole_index}",
        )
        frame.visual(
            Box((0.010, 0.028, 0.034)),
            origin=Origin(xyz=(x, 0.0, r.shaft_height_m)),
            material=mats["steel"],
            name=f"stator_form__gearbox_side_plate__pole_ring_{pole_index}", material_class_id="metal.steel_bare",
        )
    _coils_and_terminals(frame, rotor, rotor_offset, r, mats)


_STATOR_FORM_BUILDERS = {
    "open_pole_stator": _stator_form_open_pole_stator_build,
    "slotted_stator_bridge": _stator_form_slotted_stator_bridge_build,
    "twin_magnet_posts": _stator_form_twin_magnet_posts_build,
    "gearbox_side_plate": _stator_form_gearbox_side_plate_build,
}


# --- drive input candidates -----------------------------------------------------
def _crank_web(
    part, offset, r: ResolvedConfig, mats, y: float, phase: float, index: int,
    sign: float = -1.0,
):
    """One offset crank web plus the pin its grip spins on."""
    cr = r.crank_radius_m
    cx = r.input_x_m + cr * math.cos(phase)
    cz = r.shaft_height_m + cr * math.sin(phase)
    part.visual(
        Box((cr + 0.020, 0.010, 0.014)),
        origin=_local_origin(
            Origin(
                xyz=(
                    r.input_x_m + 0.5 * cr * math.cos(phase),
                    y,
                    r.shaft_height_m + 0.5 * cr * math.sin(phase),
                ),
                rpy=(0.0, -phase, 0.0),
            ),
            offset,
        ),
        material=mats["steel"],
        name=f"drive_input__crank_web_{index}", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.004, length=0.014),
        origin=_local_origin(
            Origin(
                xyz=(cx, y + sign * 0.009, cz),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            offset,
        ),
        material=mats["steel"],
        name=f"drive_input__crank_pin_{index}", material_class_id="metal.steel_bare",
    )
    return (cx, y + sign * 0.029, cz)


def _grip_part(model, input_part, r: ResolvedConfig, mats, pin, index: int):
    grip = model.part(f"drive_input__grip_{index}", meta={"role": "grip"})
    grip.visual(
        Cylinder(radius=GRIP_R, length=0.024),
        origin=_local_origin(
            Origin(xyz=pin, rpy=(math.pi / 2.0, 0.0, 0.0)), pin
        ),
        material=mats["dark"],
        name=f"drive_input__grip_sleeve_{index}", material_class_id="rubber.smooth_plain",
    )
    grip.visual(
        Cylinder(radius=GRIP_R + 0.002, length=0.004),
        origin=_local_origin(
            Origin(
                xyz=(
                    pin[0],
                    pin[1] + (0.012 if pin[1] > 0.0 else -0.012),
                    pin[2],
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            pin,
        ),
        material=mats["steel"],
        name=f"drive_input__grip_collar_{index}", material_class_id="metal.steel_bare",
    )
    input_origin = (r.input_x_m, 0.0, r.shaft_height_m)
    provider = AxisInterface(
        name=f"crank_pin_axis_{index}",
        point=tuple(pin[i] - input_origin[i] for i in range(3)),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name=f"grip_axis_{index}", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        f"input_to_grip_{index}",
        ArticulationType.CONTINUOUS,
        parent=input_part,
        child=grip,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=4.0, velocity=12.0),
        meta={"positive_motion": "the grip spins freely on its crank pin"},
    )
    register_interface_mate(model, f"input_to_grip_{index}", mate)
    return grip


def _drive_input_crank_handle_build(model, frame, input_part, offset, r, mats):
    pin = _crank_web(input_part, offset, r, mats, CRANK_Y, 0.0, 0)
    return (_grip_part(model, input_part, r, mats, pin, 0),)


def _drive_input_dual_crank_build(model, frame, input_part, offset, r, mats):
    grips = []
    for index, (y, phase, sign) in enumerate(
        ((CRANK_Y, 0.0, -1.0), (CRANK_Y - 0.062, math.pi, -1.0))
    ):
        pin = _crank_web(input_part, offset, r, mats, y, phase, index, sign)
        grips.append(_grip_part(model, input_part, r, mats, pin, index))
    return tuple(grips)


def _drive_input_handwheel_input_build(model, frame, input_part, offset, r, mats):
    rim = 0.46 * r.shaft_height_m
    _disc_y(
        input_part, offset, r.input_x_m, CRANK_Y, r.shaft_height_m, rim, 0.008,
        mats["dark"],
        "drive_input__handwheel_rim",
    )
    _disc_y(
        input_part, offset, r.input_x_m, CRANK_Y, r.shaft_height_m, 0.014, 0.016,
        mats["steel"],
        "drive_input__handwheel_hub",
    )
    for k in range(4):
        angle = k * math.pi / 4.0
        input_part.visual(
            Box((2.0 * rim - 0.010, 0.008, 0.007)),
            origin=_local_origin(
                Origin(
                    xyz=(r.input_x_m, CRANK_Y, r.shaft_height_m),
                    rpy=(0.0, angle, 0.0),
                ),
                offset,
            ),
            material=mats["steel"],
            name=f"drive_input__handwheel_spoke_{k}", material_class_id="metal.steel_bare",
        )
    return ()


def _drive_input_flywheel_input_build(model, frame, input_part, offset, r, mats):
    rim = 0.46 * r.shaft_height_m
    _disc_y(
        input_part, offset, r.input_x_m, CRANK_Y - 0.050, r.shaft_height_m, rim,
        0.014, mats["dark"],
        "drive_input__flywheel_rim",
    )
    _disc_y(
        input_part, offset, r.input_x_m, CRANK_Y - 0.050, r.shaft_height_m, 0.016,
        0.024, mats["steel"],
        "drive_input__flywheel_hub",
    )
    pin = _crank_web(input_part, offset, r, mats, CRANK_Y + 0.014, 0.0, 0)
    input_part.visual(
        Cylinder(radius=0.006, length=0.008),
        origin=_local_origin(
            Origin(
                xyz=(pin[0], CRANK_Y + 0.010, pin[2]),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            offset,
        ),
        material=mats["steel"],
        name="drive_input__flywheel_crank_pin", material_class_id="metal.steel_bare",
    )
    return (_grip_part(model, input_part, r, mats, pin, 0),)


_DRIVE_INPUT_BUILDERS = {
    "crank_handle": _drive_input_crank_handle_build,
    "dual_crank": _drive_input_dual_crank_build,
    "handwheel_input": _drive_input_handwheel_input_build,
    "flywheel_input": _drive_input_flywheel_input_build,
}


# --- transmission candidates ----------------------------------------------------
def _transfer_part(model, frame, r: ResolvedConfig, mats, name: str, point, axis, mimic_mult):
    part = model.part(name, meta={"role": "transfer"})
    provider = AxisInterface(
        name="transfer_axis", point=point, axis=axis, radial=(0.0, 0.0, 1.0)
    )
    consumer = AxisInterface(name="transfer_pivot_axis", axis=axis, radial=(0.0, 0.0, 1.0))
    mate = mate_axes(provider, consumer)
    joint = f"frame_to_{name.split('__')[-1]}"
    model.articulation(
        joint,
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=20.0, velocity=20.0),
        mimic=Mimic(joint="frame_to_input", multiplier=mimic_mult, offset=0.0),
        meta={"positive_motion": "the transfer member follows the input at its own ratio"},
    )
    register_interface_mate(model, joint, mate)
    return part, joint


def _transmission_shaft_pulley_train_build(model, frame, r, mats):
    prefix = "transmission__shaft_pulley_train"
    jack_r = 0.20 * r.centre_distance_m
    point = (0.0, WHEEL_Y, r.shaft_height_m)
    part, _ = _transfer_part(
        model, frame, r, mats, f"{prefix}__jackshaft", point, (0.0, 1.0, 0.0),
        -r.drive_wheel_radius_m / jack_r,
    )
    _disc_y(part, point, 0.0, WHEEL_Y, r.shaft_height_m, jack_r, 0.010, mats["steel"],
            f"{prefix}__jack_pulley")
    _disc_y(part, point, 0.0, WHEEL_Y, r.shaft_height_m, SHAFT_R, 0.040, mats["steel"],
            f"{prefix}__jack_shaft")
    _saddle(frame, (0.0, 0.0, 0.0), r, 0.0, STAND_Y, mats, f"{prefix}__jack_saddle")
    frame.visual(
        Box((0.030, 2.0 * STAND_HALF_T, r.stand_top_z_m - 0.008)),
        origin=Origin(xyz=(0.0, STAND_Y, 0.5 * (0.008 + r.stand_top_z_m))),
        material=mats["frame"],
        name=f"{prefix}__jack_standard", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    return (part,)


def _transmission_spur_gear_pair_build(model, frame, r, mats):
    prefix = "transmission__spur_gear_pair"
    spine_y = WHEEL_Y + 0.016
    spine_z = r.stand_top_z_m - 0.010
    frame.visual(
        Box((r.centre_distance_m, 0.012, 0.012)),
        origin=Origin(xyz=(0.0, spine_y, spine_z)),
        material=mats["frame"],
        name=f"{prefix}__gear_case_spine", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    frame.visual(
        Box((0.016, spine_y - STAND_Y + 0.014, 0.030)),
        origin=Origin(xyz=(0.0, 0.5 * (STAND_Y + spine_y) + 0.003, spine_z)),
        material=mats["frame"],
        name=f"{prefix}__gear_case_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    for stud_index in range(8):
        x = -0.5 * r.centre_distance_m + (stud_index + 0.5) * r.centre_distance_m / 8.0
        frame.visual(
            Box((0.006, 0.008, 0.014)),
            origin=Origin(xyz=(x, spine_y, spine_z + 0.010)),
            material=mats["dark"],
            name=f"{prefix}__gear_case_stud_{stud_index}", material_class_id="metal.blackened_gunmetal",
        )
    return ()


def _transmission_belt_two_pulley_build(model, frame, r, mats):
    return ()


def _transmission_idler_tension_pulley_build(model, frame, r, mats):
    prefix = "transmission__idler_tension_pulley"
    idler_r = 0.07 * r.centre_distance_m
    idler_z = (
        r.shaft_height_m
        + max(r.drive_wheel_radius_m, r.driven_wheel_radius_m)
        + 0.010
        + idler_r
    )
    point = (0.0, WHEEL_Y, idler_z)
    part, _ = _transfer_part(
        model, frame, r, mats, f"{prefix}__idler", point, (0.0, 1.0, 0.0),
        -r.drive_wheel_radius_m / idler_r,
    )
    _disc_y(
        part, point, 0.0, WHEEL_Y, idler_z, idler_r, 0.010, mats["steel"],
        f"{prefix}__idler_wheel",
    )
    _disc_y(
        part, point, 0.0, WHEEL_Y, idler_z, 0.006, 0.022, mats["dark"],
        f"{prefix}__idler_hub",
    )
    frame.visual(
        Box((0.012, 2.0 * STAND_HALF_T, idler_z - r.stand_top_z_m + 0.020)),
        origin=Origin(
            xyz=(0.0, STAND_Y, 0.5 * (r.stand_top_z_m - 0.020 + idler_z))
        ),
        material=mats["frame"],
        name=f"{prefix}__idler_post", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    arm_y1 = WHEEL_Y - 0.006
    frame.visual(
        Box((0.014, arm_y1 - (STAND_Y - 0.004), 0.014)),
        origin=Origin(xyz=(0.0, 0.5 * (STAND_Y - 0.004 + arm_y1), idler_z)),
        material=mats["frame"],
        name=f"{prefix}__idler_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    return (part,)


def _transmission_friction_wheel_build(model, frame, r, mats):
    prefix = "transmission__friction_wheel"
    rail_z = r.shaft_height_m + r.drive_wheel_radius_m + 0.022
    for rail_index, sy in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.100, 0.006, 0.006)),
            origin=Origin(xyz=(0.0, WHEEL_Y + sy * 0.011, rail_z)),
            material=mats["frame"],
            name=f"{prefix}__slide_rail_{rail_index}", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
        )
    for post_index, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.012, 2.0 * STAND_HALF_T, rail_z - r.stand_top_z_m + 0.016)),
            origin=Origin(
                xyz=(sx * 0.042, STAND_Y, 0.5 * (r.stand_top_z_m - 0.016 + rail_z))
            ),
            material=mats["frame"],
            name=f"{prefix}__slide_post_{post_index}", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
        )
        frame.visual(
            Box((0.012, WHEEL_Y - STAND_Y + 0.020, 0.010)),
            origin=Origin(xyz=(sx * 0.042, 0.5 * (STAND_Y + WHEEL_Y), rail_z)),
            material=mats["frame"],
            name=f"{prefix}__slide_bracket_{post_index}", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
        )
    carrier = model.part(f"{prefix}__tension_carrier", meta={"role": "transfer"})
    carrier_offset = (0.0, WHEEL_Y, rail_z)
    carrier.visual(
        Box((0.024, 0.020, 0.010)),
        origin=_local_origin(Origin(xyz=(0.0, WHEEL_Y, rail_z)), carrier_offset),
        material=mats["steel"],
        name=f"{prefix}__carrier_block", material_class_id="metal.steel_bare",
    )
    carrier.visual(
        Cylinder(radius=0.008, length=0.012),
        origin=_local_origin(
            Origin(
                xyz=(0.0, WHEEL_Y, rail_z - 0.012),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            carrier_offset,
        ),
        material=mats["dark"],
        name=f"{prefix}__tension_roller", material_class_id="rubber.smooth_plain",
    )
    model.articulation(
        "frame_to_tension_carrier",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carrier,
        origin=Origin(xyz=(0.0, WHEEL_Y, rail_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.2, lower=-0.020, upper=0.020),
        motion_properties=MotionProperties(damping=1.0, friction=0.6),
        meta={"positive_motion": "slides the tension carrier along its rail"},
    )
    return (carrier,)


def _transmission_bevel_gear_build(model, frame, r, mats):
    prefix = "transmission__bevel_gear"
    bevel_r = 0.16 * r.centre_distance_m
    point = (0.0, WHEEL_Y, r.shaft_height_m)
    part, _ = _transfer_part(
        model, frame, r, mats, f"{prefix}__bevel_transfer", point, (1.0, 0.0, 0.0),
        -r.drive_wheel_radius_m / bevel_r,
    )
    part.visual(
        Cylinder(radius=bevel_r, length=0.010),
        origin=_local_origin(
            Origin(
                xyz=(0.0, WHEEL_Y, r.shaft_height_m),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            point,
        ),
        material=mats["steel"],
        name=f"{prefix}__bevel_crown", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=0.008, length=0.040),
        origin=_local_origin(
            Origin(
                xyz=(0.0, WHEEL_Y, r.shaft_height_m),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            point,
        ),
        material=mats["dark"],
        name=f"{prefix}__bevel_shaft", material_class_id="metal.blackened_gunmetal",
    )
    bar_z = r.shaft_height_m - bevel_r - 0.010
    frame.visual(
        Box((0.076, 0.014, 0.008)),
        origin=Origin(xyz=(0.0, WHEEL_Y, bar_z)),
        material=mats["frame"],
        name=f"{prefix}__bevel_saddle", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    for cheek_index, sx in enumerate((-1.0, 1.0)):
        top_z = r.shaft_height_m - 0.0075
        frame.visual(
            Box((0.012, 0.014, top_z - bar_z)),
            origin=Origin(xyz=(sx * 0.015, WHEEL_Y, 0.5 * (bar_z + top_z))),
            material=mats["frame"],
            name=f"{prefix}__bevel_cheek_{cheek_index}", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
        )
    frame.visual(
        Box((0.014, WHEEL_Y - STAND_Y + 0.020, 0.008)),
        origin=Origin(xyz=(0.0, 0.5 * (STAND_Y + WHEEL_Y), bar_z)),
        material=mats["frame"],
        name=f"{prefix}__bevel_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    frame.visual(
        Box((0.014, 2.0 * STAND_HALF_T, max(0.008, bar_z - r.stand_top_z_m + 0.020))),
        origin=Origin(
            xyz=(0.0, STAND_Y, 0.5 * (r.stand_top_z_m - 0.020 + bar_z))
        ),
        material=mats["frame"],
        name=f"{prefix}__bevel_post", material_class_id=("metal.paint_coated" if r.palette_style in {"works_green", "lab_grey", "red_frame"} else "metal.brass_aged"),
    )
    return (part,)


_TRANSMISSION_BUILDERS = {
    "shaft_pulley_train": _transmission_shaft_pulley_train_build,
    "spur_gear_pair": _transmission_spur_gear_pair_build,
    "belt_two_pulley": _transmission_belt_two_pulley_build,
    "idler_tension_pulley": _transmission_idler_tension_pulley_build,
    "friction_wheel": _transmission_friction_wheel_build,
    "bevel_gear": _transmission_bevel_gear_build,
}


# --- assembly -------------------------------------------------------------------
def _build_input(model, frame, r: ResolvedConfig, mats):
    point = (r.input_x_m, 0.0, r.shaft_height_m)
    part = model.part("input", meta={"role": "input"})
    shaft_y0 = r.input_shaft_y0_m
    shaft_y1 = WHEEL_Y + 0.010
    part.visual(
        Cylinder(radius=SHAFT_R, length=shaft_y1 - shaft_y0),
        origin=_local_origin(
            Origin(
                xyz=(
                    r.input_x_m,
                    0.5 * (shaft_y0 + shaft_y1),
                    r.shaft_height_m,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            point,
        ),
        material=mats["steel"],
        name="input__shaft", material_class_id="metal.steel_bare",
    )
    _disc_y(
        part, point, r.input_x_m, WHEEL_Y, r.shaft_height_m, r.drive_wheel_radius_m,
        2.0 * WHEEL_HALF_T, mats["steel"], "input__drive_wheel",
    )
    _disc_y(
        part, point, r.input_x_m, WHEEL_Y, r.shaft_height_m,
        r.drive_wheel_radius_m * 0.35,
        2.0 * WHEEL_HALF_T + 0.006, mats["dark"], "input__drive_hub",
    )
    provider = AxisInterface(
        name="transfer_axis", point=point, axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    consumer = AxisInterface(name="input_axis", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        "frame_to_input",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=part,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=25.0, velocity=15.0),
        motion_properties=MotionProperties(damping=0.05, friction=0.03),
        meta={"positive_motion": "cranks the input shaft"},
    )
    register_interface_mate(model, "frame_to_input", mate)
    return part, point


def _build_rotor(model, frame, r: ResolvedConfig, mats):
    point = (r.rotor_x_m, 0.0, r.shaft_height_m)
    rotor = model.part("rotor", meta={"role": "rotor"})
    shaft_y0 = -(STAND_Y + 0.012)
    shaft_y1 = WHEEL_Y + 0.010
    rotor.visual(
        Cylinder(radius=SHAFT_R, length=shaft_y1 - shaft_y0),
        origin=_local_origin(
            Origin(
                xyz=(
                    r.rotor_x_m,
                    0.5 * (shaft_y0 + shaft_y1),
                    r.shaft_height_m,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            point,
        ),
        material=mats["steel"],
        name="rotor__shaft", material_class_id="metal.steel_bare",
    )
    _disc_y(
        rotor, point, r.rotor_x_m, 0.0, r.shaft_height_m, r.rotor_radius_m,
        0.020, mats["steel"],
        "rotor__armature_core",
    )
    _disc_y(
        rotor, point, r.rotor_x_m, WHEEL_Y, r.shaft_height_m,
        r.driven_wheel_radius_m,
        2.0 * WHEEL_HALF_T, mats["steel"], "rotor__driven_wheel",
    )
    provider = AxisInterface(
        name="armature_axis", point=point, axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0)
    )
    consumer = AxisInterface(name="rotor_axis", axis=(0.0, 1.0, 0.0), radial=(1.0, 0.0, 0.0))
    mate = mate_axes(provider, consumer)
    model.articulation(
        "frame_to_rotor",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=rotor,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=20.0, velocity=40.0),
        mimic=Mimic(joint="frame_to_input", multiplier=-r.drive_ratio, offset=0.0),
        meta={"positive_motion": "spins the armature at the wheel ratio"},
    )
    register_interface_mate(model, "frame_to_rotor", mate)
    return rotor, point


def build_pictureX_0611_generator(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_generator",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "hand input driving an armature through a visible transmission",
        },
    )
    mats = _materials(model, r)
    frame = model.part("frame", meta={"role": "frame"})
    _frame_common(frame, r, mats)
    input_part, input_offset = _build_input(model, frame, r, mats)
    rotor, rotor_offset = _build_rotor(model, frame, r, mats)
    _DRIVE_INPUT_BUILDERS[r.drive_input](model, frame, input_part, input_offset, r, mats)
    _TRANSMISSION_BUILDERS[r.transmission](model, frame, r, mats)
    _STATOR_FORM_BUILDERS[r.stator_form](frame, rotor, rotor_offset, r, mats)

    risk: list[dict[str, float]] = [
        {"frame_to_input": 0.0},
        {"frame_to_input": math.pi / 2.0},
        {"frame_to_input": math.pi},
        {"frame_to_input": -math.pi / 2.0},
    ]
    if r.transmission == "friction_wheel":
        risk[1]["frame_to_tension_carrier"] = 0.020
        risk[3]["frame_to_tension_carrier"] = -0.020
    model.meta["risk_poses"] = tuple(risk)
    return model


def build_seeded_pictureX_0611_generator(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_generator(config_from_seed(seed), assets=assets)


# --- authored tests --------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_pictureX_0611_generator_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    frames = _parts_by_role(model, "frame")
    inputs = _parts_by_role(model, "input")
    rotors = _parts_by_role(model, "rotor")
    grips = _parts_by_role(model, "grip")
    transfers = _parts_by_role(model, "transfer")
    joints = {j.name: j for j in model.articulations}
    rotor_joint = joints.get("frame_to_rotor")
    input_joint = joints.get("frame_to_input")

    ctx.check(
        "category_anchor: a hand input turns an armature on a second shaft line of a grounded frame",
        len(frames) == 1
        and len(inputs) == 1
        and len(rotors) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "frame"
        and input_joint is not None
        and input_joint.articulation_type == ArticulationType.CONTINUOUS
        and input_joint.parent == "frame"
        and rotor_joint is not None
        and rotor_joint.articulation_type == ArticulationType.CONTINUOUS
        and tuple(round(abs(v), 6) for v in rotor_joint.axis) == (0.0, 1.0, 0.0)
        and rotor_joint.parent == "frame"
        and rotor_joint.child == "rotor",
        details=(
            f"frames={len(frames)} inputs={len(inputs)} rotors={len(rotors)} "
            f"grips={len(grips)} transfers={len(transfers)} joints={sorted(joints)}"
        ),
    )

    ctx.check(
        "category_anchor: the armature turns inside the stator air gap at the wheel ratio",
        rotor_joint is not None
        and rotor_joint.mimic is not None
        and abs(rotor_joint.mimic.multiplier + r.drive_ratio) < 1e-9
        and abs(r.drive_ratio - r.drive_wheel_radius_m / r.driven_wheel_radius_m) < 1e-9
        and r.driven_wheel_radius_m > 0.006
        and abs(r.input_x_m - -0.5 * r.centre_distance_m) < 1e-9
        and abs(r.rotor_x_m - 0.5 * r.centre_distance_m) < 1e-9
        and abs(r.pole_gap_m - (r.rotor_radius_m + 0.005)) < 1e-9
        and r.crank_radius_m + GRIP_R + 0.006 < r.shaft_height_m
        and r.stand_top_z_m < r.shaft_height_m - SHAFT_R - 0.006,
        details=(
            f"ratio={r.drive_ratio} wheels=({r.drive_wheel_radius_m}, "
            f"{r.driven_wheel_radius_m}) pole_gap={r.pole_gap_m} "
            f"crank={r.crank_radius_m} stand_top={r.stand_top_z_m}"
        ),
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}

    def count(fragment: str) -> int:
        return sum(1 for n in visual_names if fragment in n)

    if r.drive_input == "crank_handle":
        input_ok = len(grips) == 1 and count("drive_input__crank_web_") == 1
    elif r.drive_input == "dual_crank":
        input_ok = len(grips) == 2 and count("drive_input__crank_web_") == 2
    elif r.drive_input == "handwheel_input":
        input_ok = (
            len(grips) == 0
            and count("drive_input__handwheel_spoke_") == 4
            and any("drive_input__handwheel_rim" in n for n in visual_names)
        )
    else:
        input_ok = (
            len(grips) == 1
            and any("drive_input__flywheel_rim" in n for n in visual_names)
            and any("drive_input__flywheel_crank_pin" in n for n in visual_names)
        )
    ctx.check(
        "category_anchor: drive_input identity",
        input_ok and any("input__drive_wheel" in n for n in visual_names),
        details=f"drive_input={r.drive_input} grips={len(grips)}",
    )

    if r.transmission == "shaft_pulley_train":
        trans_ok = len(transfers) == 1 and any(
            "shaft_pulley_train__jack_pulley" in n for n in visual_names
        )
    elif r.transmission == "spur_gear_pair":
        trans_ok = len(transfers) == 0 and count("spur_gear_pair__gear_case_stud_") == 8
    elif r.transmission == "belt_two_pulley":
        trans_ok = len(transfers) == 0 and count("__belt_") == 0
    elif r.transmission == "idler_tension_pulley":
        trans_ok = (
            len(transfers) == 1
            and count("__belt_") == 0
            and any("idler_tension_pulley__idler_wheel" in n for n in visual_names)
        )
    elif r.transmission == "friction_wheel":
        slide = joints.get("frame_to_tension_carrier")
        trans_ok = (
            len(transfers) == 1
            and slide is not None
            and slide.articulation_type == ArticulationType.PRISMATIC
            and any("friction_wheel__tension_roller" in n for n in visual_names)
        )
    else:
        trans_ok = len(transfers) == 1 and any(
            "bevel_gear__bevel_crown" in n for n in visual_names
        )

    ctx.check(
        "category_anchor: transmission identity",
        trans_ok and any("rotor__driven_wheel" in n for n in visual_names),
        details=f"transmission={r.transmission} transfers={len(transfers)}",
    )

    stator_ok = {
        "open_pole_stator": count("open_pole_stator__pole_shoe_") == 2,
        "slotted_stator_bridge": count("slotted_stator_bridge__slot_rib_") == 3
        and any("slotted_stator_bridge__bridge" in n for n in visual_names),
        "twin_magnet_posts": count("twin_magnet_posts__magnet_post_") == 2,
        "gearbox_side_plate": count("gearbox_side_plate__cover_bolt_") == 4
        and any("gearbox_side_plate__side_plate" in n for n in visual_names),
    }[r.stator_form]
    ctx.check(
        "category_anchor: stator_form identity",
        stator_ok
        and count("stator_form__coil_pack_") == r.coil_count
        and count("stator_form__terminal_cap_") == r.terminal_count
        and count("stator_form__terminal_post_") == r.terminal_count,
        details=(
            f"stator_form={r.stator_form} coils={r.coil_count} "
            f"terminals={r.terminal_count}"
        ),
    )

    # Motion evidence: cranking the input really carries the armature round with it.
    rest = ctx.part_element_world_aabb(rotors[0], elem="stator_form__coil_pack_0")
    with ctx.pose({input_joint: 0.7}):
        turned = ctx.part_element_world_aabb(rotors[0], elem="stator_form__coil_pack_0")
    ctx.check(
        "cranking the input carries the armature coil round the rotor axis",
        rest is not None
        and turned is not None
        and max(
            abs(turned[0][0] - rest[0][0]), abs(turned[0][2] - rest[0][2])
        )
        > 0.05 * r.rotor_radius_m,
        details=f"rest={rest} turned={turned}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_frame_max_coils_bevel",
        {
            "drive_input": "dual_crank",
            "transmission": "bevel_gear",
            "stator_form": "slotted_stator_bridge",
            "coil_count": 3,
            "terminal_count": 4,
            "shaft_height_m": 0.055,
            "centre_distance_m": 0.075,
            "rotor_radius_m": 0.032,
        },
        reason="the shortest frame and closest shafts with the biggest armature, three coils "
        "and the right-angle transfer",
    ),
    corner_case(
        "max_frame_friction_flywheel",
        {
            "drive_input": "flywheel_input",
            "transmission": "friction_wheel",
            "stator_form": "twin_magnet_posts",
            "coil_count": 1,
            "terminal_count": 2,
            "shaft_height_m": 0.100,
            "centre_distance_m": 0.130,
            "rotor_radius_m": 0.018,
        },
        reason="the tallest frame and widest shaft spacing with the largest friction wheels "
        "and the flywheel input",
    ),
    corner_case(
        "max_frame_idler_handwheel",
        {
            "drive_input": "handwheel_input",
            "transmission": "idler_tension_pulley",
            "stator_form": "gearbox_side_plate",
            "coil_count": 3,
            "terminal_count": 4,
            "shaft_height_m": 0.100,
            "centre_distance_m": 0.130,
            "rotor_radius_m": 0.032,
        },
        reason="the tallest idler post over the longest belt run behind the side plate",
    ),
    corner_case(
        "min_frame_jackshaft_crank",
        {
            "drive_input": "crank_handle",
            "transmission": "shaft_pulley_train",
            "stator_form": "open_pole_stator",
            "coil_count": 1,
            "terminal_count": 2,
            "shaft_height_m": 0.055,
            "centre_distance_m": 0.075,
            "rotor_radius_m": 0.018,
        },
        reason="the tightest jackshaft train in the smallest frame",
    ),
    corner_case(
        "max_frame_spur_dual_crank",
        {
            "drive_input": "dual_crank",
            "transmission": "spur_gear_pair",
            "stator_form": "open_pole_stator",
            "coil_count": 2,
            "terminal_count": 3,
            "shaft_height_m": 0.100,
            "centre_distance_m": 0.130,
            "rotor_radius_m": 0.032,
        },
        reason="the largest meshing spur pair with two cranks on the widest frame",
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
    "build_pictureX_0611_generator",
    "build_seeded_pictureX_0611_generator",
    "run_pictureX_0611_generator_tests",
]
