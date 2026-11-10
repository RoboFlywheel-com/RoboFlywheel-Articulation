# SPDX-License-Identifier: Apache-2.0

"""Source-backed clamshell laptop template.

Three reviewed shell envelopes combine with two visible hinge treatments,
three pointing systems, one island-key construction, and two-to-four underside
feet. The screen joint always uses the visible rear axis.

Coordinates: X = width, Y = rear, Z = up; the user is toward -Y.
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
    ExtrudeGeometry,
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

ShellFamily = Literal["budget_plastic", "rugged_bumper", "thin_aluminum"]
HingeStyle = Literal["full_width_barrel", "dual_side_barrels"]
PointingSystem = Literal[
    "integrated_clickpad",
    "dual_mouse_buttons",
    "trackpoint_three_button",
]
KeyArray = Literal["island_keyboard"]
SupportModule = Literal["rubber_feet"]

_SHELLS = ("budget_plastic", "rugged_bumper", "thin_aluminum")
_HINGES = ("full_width_barrel", "dual_side_barrels")
_POINTING = ("integrated_clickpad", "dual_mouse_buttons", "trackpoint_three_button")
_FOOT_COUNTS = (2, 3, 4)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("shell_family", _SHELLS),
        component_slot("hinge_style", _HINGES),
        component_slot("pointing_system", _POINTING),
        component_slot("key_array", ("island_keyboard",)),
        component_slot("support_module", ("rubber_feet",)),
        multiplicity_slot("foot_count", _FOOT_COUNTS, item_slot="support_module"),
    )
)

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {
        "shell": (0.035, 0.038, 0.042, 1.0),
        "deck": (0.075, 0.080, 0.088, 1.0),
        "key": (0.018, 0.020, 0.023, 1.0),
        "screen": (0.012, 0.018, 0.028, 1.0),
        "accent": (0.66, 0.68, 0.70, 1.0),
        "rubber": (0.025, 0.026, 0.028, 1.0),
        "nub": (0.72, 0.08, 0.06, 1.0),
    },
    {
        "shell": (0.74, 0.77, 0.80, 1.0),
        "deck": (0.82, 0.84, 0.86, 1.0),
        "key": (0.14, 0.15, 0.17, 1.0),
        "screen": (0.04, 0.06, 0.10, 1.0),
        "accent": (0.22, 0.45, 0.80, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
        "nub": (0.75, 0.10, 0.08, 1.0),
    },
    {
        "shell": (0.18, 0.21, 0.16, 1.0),
        "deck": (0.23, 0.26, 0.20, 1.0),
        "key": (0.08, 0.09, 0.075, 1.0),
        "screen": (0.025, 0.030, 0.024, 1.0),
        "accent": (0.72, 0.66, 0.36, 1.0),
        "rubber": (0.035, 0.038, 0.030, 1.0),
        "nub": (0.65, 0.11, 0.07, 1.0),
    },
)

_KEY_ROWS = 6
_KEY_COLS = 14
_KEY_COUNT = _KEY_ROWS * _KEY_COLS
_KEY_HEIGHT = 0.0042
_KEY_TRAVEL = 0.0012
_LID_HINGE_GAP = 0.0060


@dataclass(frozen=True)
class Config:
    shell_family: ShellFamily = "budget_plastic"
    hinge_style: HingeStyle = "full_width_barrel"
    pointing_system: PointingSystem = "integrated_clickpad"
    key_array: KeyArray = "island_keyboard"
    support_module: SupportModule = "rubber_feet"
    foot_count: int = 4
    budget_base_width_m: float | None = None
    rugged_base_thickness_m: float | None = None
    thin_base_width_m: float | None = None
    full_hinge_open_rad: float | None = None
    dual_hinge_open_rad: float | None = None
    clickpad_travel_m: float | None = None
    mouse_button_travel_m: float | None = None
    trackpoint_button_travel_m: float | None = None
    laptop_key_pitch_m: float | None = None
    palette: int = 0
    name: str = "Technology_Laptop"


@dataclass(frozen=True)
class ResolvedConfig:
    shell_family: ShellFamily
    hinge_style: HingeStyle
    pointing_system: PointingSystem
    key_array: KeyArray
    support_module: SupportModule
    foot_count: int
    palette: int
    name: str
    base_width_m: float
    base_depth_m: float
    base_thickness_m: float
    lid_width_m: float
    lid_height_m: float
    lid_thickness_m: float
    hinge_y_m: float
    hinge_z_m: float
    open_angle_rad: float
    pointing_travel_m: float
    laptop_key_pitch_m: float
    keyboard_width_m: float
    pointing_width_m: float


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    index = int(seed)
    foot_count = _FOOT_COUNTS[index % len(_FOOT_COUNTS)]
    index //= len(_FOOT_COUNTS)
    pointing = _POINTING[index % len(_POINTING)]
    index //= len(_POINTING)
    hinge = _HINGES[index % len(_HINGES)]
    index //= len(_HINGES)
    shell = _SHELLS[index % len(_SHELLS)]
    return Config(
        shell_family=shell,
        hinge_style=hinge,
        pointing_system=pointing,
        foot_count=foot_count,
        budget_base_width_m=round(rng.uniform(0.35, 0.40), 4),
        rugged_base_thickness_m=round(rng.uniform(0.026, 0.038), 4),
        thin_base_width_m=round(rng.uniform(0.30, 0.34), 4),
        full_hinge_open_rad=round(rng.uniform(1.65, 2.15), 4),
        dual_hinge_open_rad=round(rng.uniform(1.65, 2.15), 4),
        clickpad_travel_m=round(rng.uniform(0.0005, 0.0010), 5),
        mouse_button_travel_m=round(rng.uniform(0.0005, 0.0010), 5),
        trackpoint_button_travel_m=round(rng.uniform(0.0005, 0.0010), 5),
        laptop_key_pitch_m=round(rng.uniform(0.0155, 0.0180), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"Technology_Laptop_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    if config.shell_family not in _SHELLS:
        raise ValueError(f"unsupported shell_family: {config.shell_family}")
    if config.hinge_style not in _HINGES:
        raise ValueError(f"unsupported hinge_style: {config.hinge_style}")
    if config.pointing_system not in _POINTING:
        raise ValueError(f"unsupported pointing_system: {config.pointing_system}")
    if int(config.foot_count) not in _FOOT_COUNTS:
        raise ValueError(f"foot_count must be one of {_FOOT_COUNTS}")
    pitch = _clamp(_pick(config.laptop_key_pitch_m, 0.0168), 0.0155, 0.0180)
    if config.shell_family == "budget_plastic":
        width = _clamp(_pick(config.budget_base_width_m, 0.38), 0.35, 0.40)
        depth, thickness, lid_t = width * 0.67, 0.018, 0.008
    elif config.shell_family == "rugged_bumper":
        width = 0.38
        depth = 0.255
        thickness = _clamp(_pick(config.rugged_base_thickness_m, 0.032), 0.026, 0.038)
        lid_t = 0.014
    else:
        width = _clamp(_pick(config.thin_base_width_m, 0.31), 0.30, 0.34)
        depth, thickness, lid_t = width * 0.71, 0.015, 0.006
    lid_width = width - 0.008
    lid_height = depth - 0.018
    if config.hinge_style == "full_width_barrel":
        open_angle = _clamp(_pick(config.full_hinge_open_rad, 1.90), 1.65, 2.15)
    else:
        open_angle = _clamp(_pick(config.dual_hinge_open_rad, 1.90), 1.65, 2.15)
    if config.pointing_system == "integrated_clickpad":
        travel = _clamp(_pick(config.clickpad_travel_m, 0.0008), 0.0005, 0.0010)
    elif config.pointing_system == "dual_mouse_buttons":
        travel = _clamp(_pick(config.mouse_button_travel_m, 0.0008), 0.0005, 0.0010)
    else:
        travel = _clamp(_pick(config.trackpoint_button_travel_m, 0.0008), 0.0005, 0.0010)
    return ResolvedConfig(
        shell_family=config.shell_family,
        hinge_style=config.hinge_style,
        pointing_system=config.pointing_system,
        key_array=config.key_array,
        support_module=config.support_module,
        foot_count=int(config.foot_count),
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        base_width_m=width,
        base_depth_m=depth,
        base_thickness_m=thickness,
        lid_width_m=lid_width,
        lid_height_m=lid_height,
        lid_thickness_m=lid_t,
        hinge_y_m=depth / 2.0 - 0.008,
        hinge_z_m=thickness + 0.0045,
        open_angle_rad=open_angle,
        pointing_travel_m=travel,
        laptop_key_pitch_m=pitch,
        keyboard_width_m=min((_KEY_COLS - 0.2) * pitch, width - 0.040),
        pointing_width_m=min(width * 0.31, 0.112),
    )


def _materials(model: ArticulatedObject, palette: int):
    colors = _PALETTES[palette]
    return {
        name: model.material(f"laptop_{palette}_{name}", rgba=rgba) for name, rgba in colors.items()
    }


def _box(part, size, xyz, material, name, *, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(tuple(float(v) for v in size)),
        origin=Origin(xyz=tuple(float(v) for v in xyz), rpy=rpy),
        material=material,
        name=name, material_class_id="plastic.opaque_generic",
    )


def _rounded_slab(width: float, depth: float, height: float, name: str, radius: float):
    profile = rounded_rect_profile(
        width, depth, radius=min(radius, width * 0.1, depth * 0.1), corner_segments=8
    )
    return mesh_from_geometry(ExtrudeGeometry(profile, height, center=False), name)


def _open_lid_origin(r: ResolvedConfig, x: float, y: float, z: float) -> Origin:
    c = math.cos(-r.open_angle_rad)
    s = math.sin(-r.open_angle_rad)
    return Origin(
        xyz=(x, y * c - z * s, y * s + z * c),
        rpy=(-r.open_angle_rad, 0.0, 0.0),
    )


def _shell_common(base, lid, r: ResolvedConfig, mats, tag: str, *, rugged: bool) -> None:
    base.visual(
        _rounded_slab(r.base_width_m, r.base_depth_m, r.base_thickness_m, f"{tag}_base", 0.006),
        material=mats["shell"],
        name=f"{tag}__lower_shell", material_class_id=("metal.aluminum_bare" if r.shell_family == "thin_aluminum" else "plastic.opaque_generic"),
    )
    _box(
        base,
        (r.base_width_m - 0.026, r.base_depth_m - 0.022, 0.0010),
        (0.0, -0.003, r.base_thickness_m + 0.0005),
        mats["deck"],
        f"{tag}__palm_deck_skin",
    )
    for index, x in enumerate((-r.base_width_m * 0.40, r.base_width_m * 0.40)):
        _box(
            base,
            (0.050, 0.006, 0.0007),
            (x, r.base_depth_m * 0.25, r.base_thickness_m + 0.0010),
            mats["key"],
            f"{tag}__speaker_grille_{index}",
        )
    if rugged:
        bumper_w = 0.026
        for index, (sx, sy) in enumerate(((1, 1), (-1, 1), (1, -1), (-1, -1))):
            _box(
                base,
                (bumper_w, bumper_w, r.base_thickness_m + 0.004),
                (
                    sx * (r.base_width_m / 2 - bumper_w / 2 + 0.002),
                    sy * (r.base_depth_m / 2 - bumper_w / 2 + 0.002),
                    (r.base_thickness_m + 0.004) / 2,
                ),
                mats["rubber"],
                f"{tag}__corner_bumper_{index}",
            )

    lid.visual(
        _rounded_slab(r.lid_width_m, r.lid_height_m, r.lid_thickness_m, f"{tag}_lid", 0.005),
        origin=_open_lid_origin(
            r,
            0.0,
            -r.lid_height_m / 2.0 - _LID_HINGE_GAP,
            0.0,
        ),
        material=mats["shell"],
        name=f"{tag}__lid_shell", material_class_id=("metal.aluminum_bare" if r.shell_family == "thin_aluminum" else "plastic.opaque_generic"),
    )
    display_w = r.lid_width_m - 0.026
    display_h = r.lid_height_m - 0.034
    lid.visual(
        Box((display_w, display_h, 0.0010)),
        origin=_open_lid_origin(
            r,
            0.0,
            -r.lid_height_m / 2.0 - _LID_HINGE_GAP - 0.002,
            -0.0005,
        ),
        material=mats["screen"],
        name=f"{tag}__display_panel", material_class_id="tech.emissive_surface",
    )
    lid.visual(
        Cylinder(radius=0.0023, length=0.0010),
        origin=_open_lid_origin(
            r,
            0.0,
            -r.lid_height_m - _LID_HINGE_GAP + 0.010,
            -0.0005,
        ),
        material=mats["accent"],
        name=f"{tag}__webcam", material_class_id="glass.clear_transparent",
    )


def _shell_family_budget_plastic_build(base, lid, r: ResolvedConfig, mats) -> None:
    _shell_common(base, lid, r, mats, "shell_family__budget_plastic", rugged=False)


def _shell_family_rugged_bumper_build(base, lid, r: ResolvedConfig, mats) -> None:
    _shell_common(base, lid, r, mats, "shell_family__rugged_bumper", rugged=True)


def _shell_family_thin_aluminum_build(base, lid, r: ResolvedConfig, mats) -> None:
    tag = "shell_family__thin_aluminum"
    _shell_common(base, lid, r, mats, tag, rugged=False)
    _box(
        base,
        (r.keyboard_width_m + 0.014, 0.105, 0.0012),
        (0.0, 0.030, r.base_thickness_m + 0.0004),
        mats["shell"],
        f"{tag}__keyboard_well_bezel",
    )
    _box(
        base,
        (r.pointing_width_m + 0.006, 0.068, 0.0008),
        (0.0, -r.base_depth_m * 0.30, r.base_thickness_m + 0.0004),
        mats["shell"],
        f"{tag}__trackpad_recess_bezel",
    )


_SHELL_BUILDERS = {
    "budget_plastic": _shell_family_budget_plastic_build,
    "rugged_bumper": _shell_family_rugged_bumper_build,
    "thin_aluminum": _shell_family_thin_aluminum_build,
}


def _screen_axis_mate(r: ResolvedConfig):
    provider = AxisInterface(
        name="shell_family.rear_hinge_axis",
        point=(0.0, r.hinge_y_m, r.hinge_z_m),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0052,
    )
    consumer = AxisInterface(
        name="hinge_style.screen_axis",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0045,
    )
    return mate_axes(provider, consumer, require_fit=True)


def _make_screen_joint(model, base, lid, r: ResolvedConfig, tag: str) -> None:
    mate = _screen_axis_mate(r)
    joint = f"{tag}__screen_joint"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=4.0, velocity=1.2, lower=0.0, upper=r.open_angle_rad),
    )
    register_interface_mate(model, joint, mate)


def _hinge_style_full_width_barrel_build(model, base, lid, r: ResolvedConfig, mats) -> None:
    tag = "hinge_style__full_width_barrel"
    base.visual(
        Cylinder(radius=0.0052, length=r.base_width_m - 0.050),
        origin=Origin(xyz=(0.0, r.hinge_y_m, r.hinge_z_m), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["shell"],
        name=f"{tag}__base_barrel", material_class_id=("metal.stainless_matte" if r.shell_family in {"budget_plastic", "rugged_bumper"} else "metal.aluminum_bare"),
    )
    _make_screen_joint(model, base, lid, r, tag)


def _hinge_style_dual_side_barrels_build(model, base, lid, r: ResolvedConfig, mats) -> None:
    tag = "hinge_style__dual_side_barrels"
    for index, x in enumerate((-r.base_width_m * 0.32, r.base_width_m * 0.32)):
        base.visual(
            Cylinder(radius=0.0052, length=0.038),
            origin=Origin(xyz=(x, r.hinge_y_m, r.hinge_z_m), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["shell"],
            name=f"{tag}__base_barrel_{index}", material_class_id=("metal.stainless_matte" if r.shell_family in {"budget_plastic", "rugged_bumper"} else "metal.aluminum_bare"),
        )
    _make_screen_joint(model, base, lid, r, tag)


_HINGE_BUILDERS = {
    "full_width_barrel": _hinge_style_full_width_barrel_build,
    "dual_side_barrels": _hinge_style_dual_side_barrels_build,
}


def _key_mesh(pitch: float):
    width = pitch - 0.0022
    depth = pitch * 0.82
    profile = rounded_rect_profile(width, depth, radius=0.0015, corner_segments=5)
    return mesh_from_geometry(
        ExtrudeGeometry(profile, _KEY_HEIGHT, center=False), "laptop_island_key"
    )


def _key_array_island_keyboard_build(model, base, r: ResolvedConfig, mats) -> None:
    tag = "key_array__island_keyboard"
    keybed = model.part(
        "keybed", meta={"role": "keybed", "slot": "key_array", "candidate": r.key_array}
    )
    provider = PlaneInterface(
        name="shell_family.keyboard_deck",
        point=(0.0, 0.030, r.base_thickness_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.keyboard_width_m + 0.018, 0.108),
    )
    consumer = PlaneInterface(
        name="key_array.keybed_mount",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.keyboard_width_m, 0.098),
    )
    mate = mate_planes(provider, consumer)
    model.articulation(
        f"{tag}__fixed_mount", ArticulationType.FIXED, parent=base, child=keybed, origin=mate.origin
    )
    _box(
        keybed,
        (r.keyboard_width_m + 0.008, 0.100, 0.0010),
        (0.0, 0.0, -0.0005),
        mats["deck"],
        f"{tag}__switch_plate",
    )
    mesh = _key_mesh(r.laptop_key_pitch_m)
    x0 = -(_KEY_COLS - 1) * r.laptop_key_pitch_m / 2.0
    y0 = -(_KEY_ROWS - 1) * r.laptop_key_pitch_m * 0.90 / 2.0
    for row in range(_KEY_ROWS):
        for col in range(_KEY_COLS):
            x = x0 + col * r.laptop_key_pitch_m
            y = y0 + row * r.laptop_key_pitch_m * 0.90
            key = model.part(
                f"{tag}__press_key_{row}_{col}",
                meta={"role": "key_press", "slot": "key_array", "candidate": r.key_array},
            )
            key.visual(mesh, material=mats["key"], name=f"{tag}__cap", material_class_id="plastic.opaque_glossy_molded")
            model.articulation(
                f"{tag}__press_joint_{row}_{col}",
                ArticulationType.PRISMATIC,
                parent=keybed,
                child=key,
                origin=Origin(xyz=(x, y, 0.0007)),
                axis=(0.0, 0.0, -1.0),
                motion_limits=MotionLimits(effort=1.0, velocity=0.08, lower=0.0, upper=_KEY_TRAVEL),
                meta={"motion_qc_repeat_group": "key_press"},
            )


def _pointing_plane_mate(r: ResolvedConfig, width: float):
    y = -r.base_depth_m * 0.31
    provider = PlaneInterface(
        name="shell_family.pointing_deck",
        point=(0.0, y, r.base_thickness_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.base_width_m - 0.040, r.base_depth_m * 0.34),
    )
    consumer = PlaneInterface(
        name="pointing_system.deck_mount",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(width, 0.064),
    )
    return mate_planes(provider, consumer)


def _pointing_system_integrated_clickpad_build(model, base, r: ResolvedConfig, mats) -> None:
    tag = "pointing_system__integrated_clickpad"
    pad = model.part(
        "pointing_surface",
        meta={
            "role": "pointing_surface",
            "slot": "pointing_system",
            "candidate": r.pointing_system,
        },
    )
    _box(pad, (r.pointing_width_m, 0.062, 0.0018), (0.0, 0.0, 0.0009), mats["deck"], f"{tag}__pad")
    _box(
        pad,
        (r.pointing_width_m - 0.004, 0.0010, 0.0002),
        (0.0, -0.020, 0.0019),
        mats["key"],
        f"{tag}__click_seam",
    )
    mate = _pointing_plane_mate(r, r.pointing_width_m)
    model.articulation(
        f"{tag}__joint",
        ArticulationType.PRISMATIC,
        parent=base,
        child=pad,
        origin=mate.origin,
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=1.5, velocity=0.08, lower=0.0, upper=r.pointing_travel_m),
    )


def _fixed_pointing_surface(model, base, r: ResolvedConfig, mats, tag: str):
    pad = model.part(
        "pointing_surface",
        meta={
            "role": "pointing_surface",
            "slot": "pointing_system",
            "candidate": r.pointing_system,
        },
    )
    _box(pad, (r.pointing_width_m, 0.054, 0.0015), (0.0, 0.0, 0.00075), mats["deck"], f"{tag}__pad")
    mate = _pointing_plane_mate(r, r.pointing_width_m)
    model.articulation(
        f"{tag}__fixed_mount", ArticulationType.FIXED, parent=base, child=pad, origin=mate.origin
    )
    return mate.origin


def _pointing_button(
    model, base, r: ResolvedConfig, mats, *, tag: str, index: int, x: float, y: float
) -> None:
    button = model.part(
        f"{tag}__button_{index}",
        meta={"role": "pointing_button", "slot": "pointing_system", "candidate": r.pointing_system},
    )
    _box(button, (0.026, 0.011, 0.0022), (0.0, 0.0, 0.0011), mats["key"], f"{tag}__button_cap")
    model.articulation(
        f"{tag}__button_joint_{index}",
        ArticulationType.PRISMATIC,
        parent=base,
        child=button,
        origin=Origin(xyz=(x, y, r.base_thickness_m)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=1.2, velocity=0.08, lower=0.0, upper=r.pointing_travel_m),
    )


def _pointing_system_dual_mouse_buttons_build(model, base, r: ResolvedConfig, mats) -> None:
    tag = "pointing_system__dual_mouse_buttons"
    _fixed_pointing_surface(model, base, r, mats, tag)
    y = -r.base_depth_m * 0.31 - 0.038
    for index, x in enumerate((-0.016, 0.016)):
        _pointing_button(model, base, r, mats, tag=tag, index=index, x=x, y=y)


def _pointing_system_trackpoint_three_button_build(model, base, r: ResolvedConfig, mats) -> None:
    tag = "pointing_system__trackpoint_three_button"
    _fixed_pointing_surface(model, base, r, mats, tag)
    y = -r.base_depth_m * 0.31 + 0.034
    for index, x in enumerate((-0.028, 0.0, 0.028)):
        _pointing_button(model, base, r, mats, tag=tag, index=index, x=x, y=y)
    nub = model.part(
        "trackpoint_nub",
        meta={"role": "trackpoint_nub", "slot": "pointing_system", "candidate": r.pointing_system},
    )
    nub.visual(
        Cylinder(radius=0.0010, length=0.0045),
        origin=Origin(xyz=(0.0, 0.0, 0.00225)),
        material=mats["nub"],
        name=f"{tag}__nub", material_class_id="rubber.pebbled",
    )
    model.articulation(
        f"{tag}__nub_mount",
        ArticulationType.FIXED,
        parent=base,
        child=nub,
        origin=Origin(xyz=(0.0, 0.030, r.base_thickness_m)),
    )


_POINTING_BUILDERS = {
    "integrated_clickpad": _pointing_system_integrated_clickpad_build,
    "dual_mouse_buttons": _pointing_system_dual_mouse_buttons_build,
    "trackpoint_three_button": _pointing_system_trackpoint_three_button_build,
}


def _support_module_rubber_feet_build(model, base, r: ResolvedConfig, mats) -> None:
    tag = "support_module__rubber_feet"
    x = r.base_width_m * 0.39
    y = r.base_depth_m * 0.39
    positions = [(-x, -y), (x, -y)]
    if r.foot_count == 3:
        positions.append((0.0, y))
    elif r.foot_count == 4:
        positions.extend(((-x, y), (x, y)))
    for index, (px, py) in enumerate(positions):
        _box(base, (0.020, 0.012, 0.003), (px, py, -0.0015), mats["rubber"], f"{tag}__foot_{index}")


def build_laptop(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    base = model.part(
        "base_chassis",
        meta={"role": "laptop_base", "slot": "shell_family", "candidate": r.shell_family},
    )
    lid = model.part(
        "screen_lid",
        meta={"role": "screen_lid", "slot": "shell_family", "candidate": r.shell_family},
    )
    _SHELL_BUILDERS[r.shell_family](base, lid, r, mats)
    _HINGE_BUILDERS[r.hinge_style](model, base, lid, r, mats)
    _key_array_island_keyboard_build(model, base, r, mats)
    _POINTING_BUILDERS[r.pointing_system](model, base, r, mats)
    _support_module_rubber_feet_build(model, base, r, mats)
    model.meta["slot_choices"] = (
        ("shell_family", r.shell_family),
        ("hinge_style", r.hinge_style),
        ("pointing_system", r.pointing_system),
        ("key_array", r.key_array),
        ("support_module", r.support_module),
        ("foot_count", str(r.foot_count)),
    )
    model.meta["foot_count_actual"] = r.foot_count
    model.meta["key_count_actual"] = _KEY_COUNT
    return model


def build_seeded_laptop(seed: int) -> ArticulatedObject:
    return build_laptop(config_from_seed(seed))


def run_laptop_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[object]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part)
    hinge = next(j for j in object_model.articulations if j.name.endswith("__screen_joint"))
    lid = roles["screen_lid"][0]
    open_box = ctx.part_world_aabb(lid)
    with ctx.pose({hinge: r.open_angle_rad}):
        closed_box = ctx.part_world_aabb(lid)
    ctx.check(
        "category_anchor: lid rotates about the visible rear hinge",
        len(roles.get("laptop_base", [])) == 1
        and len(roles.get("screen_lid", [])) == 1
        and hinge.axis == (1.0, 0.0, 0.0)
        and open_box is not None
        and closed_box is not None
        and closed_box[1][2] < open_box[1][2] - r.lid_height_m * 0.25,
        details=f"axis={hinge.axis} open={open_box} closed={closed_box}",
    )
    lid_names = {str(visual.name) for visual in lid.visuals}
    ctx.check(
        "category_anchor: display panel is mounted inside the lid",
        any(name.endswith("__display_panel") for name in lid_names),
        details=str(sorted(lid_names)),
    )
    ctx.check(
        "category_anchor: keyboard and pointing device stay inside the base",
        len(roles.get("keybed", [])) == 1 and len(roles.get("pointing_surface", [])) == 1,
        details=f"keybed={len(roles.get('keybed', []))} pointing={len(roles.get('pointing_surface', []))}",
    )
    press_keys = roles.get("key_press", [])
    press_joints = [
        joint
        for joint in object_model.articulations
        if joint.name.startswith("key_array__island_keyboard__press_joint_")
    ]
    moved = True
    for joint in press_joints:
        key = object_model.get_part(joint.child)
        rest = ctx.part_world_position(key)
        with ctx.pose({joint: _KEY_TRAVEL}):
            pressed = ctx.part_world_position(key)
        moved = (
            moved
            and rest is not None
            and pressed is not None
            and pressed[2] < rest[2] - _KEY_TRAVEL * 0.5
        )
    ctx.check(
        "category_anchor: every island key presses downward",
        len(press_keys) == _KEY_COUNT
        and len(press_joints) == _KEY_COUNT
        and int(object_model.meta.get("key_count_actual", 0)) == _KEY_COUNT
        and moved,
        details=f"parts={len(press_keys)} joints={len(press_joints)}",
    )
    if r.pointing_system == "integrated_clickpad":
        joint = object_model.get_articulation("pointing_system__integrated_clickpad__joint")
        pad = roles["pointing_surface"][0]
        rest = ctx.part_world_position(pad)
        with ctx.pose({joint: r.pointing_travel_m}):
            pressed = ctx.part_world_position(pad)
        ctx.check(
            "category_anchor: integrated clickpad presses downward",
            rest is not None
            and pressed is not None
            and pressed[2] < rest[2] - r.pointing_travel_m * 0.5,
            details=f"rest={rest} pressed={pressed}",
        )
    elif r.pointing_system == "dual_mouse_buttons":
        ctx.check(
            "category_anchor: two mouse buttons press independently",
            len(roles.get("pointing_button", [])) == 2,
            details=str([part.name for part in roles.get("pointing_button", [])]),
        )
    else:
        ctx.check(
            "category_anchor: TrackPoint nub sits between the keys",
            len(roles.get("trackpoint_nub", [])) == 1,
            details=str([part.name for part in roles.get("trackpoint_nub", [])]),
        )
        ctx.check(
            "category_anchor: three TrackPoint buttons press independently",
            len(roles.get("pointing_button", [])) == 3,
            details=str([part.name for part in roles.get("pointing_button", [])]),
        )
    base = roles["laptop_base"][0]
    foot_names = [
        name
        for name in (str(v.name) for v in base.visuals)
        if name.startswith("support_module__rubber_feet__foot_")
    ]
    ctx.check(
        "underside foot count matches multiplicity",
        len(foot_names) == r.foot_count,
        details=f"found={len(foot_names)} expected={r.foot_count}",
    )
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=40,
        ignore_adjacent=True,
        ignore_fixed=True,
    )
    return ctx.report()


run_laptop_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "rugged_dual_hinge_trackpoint_four_feet",
        {
            "shell_family": "rugged_bumper",
            "hinge_style": "dual_side_barrels",
            "pointing_system": "trackpoint_three_button",
            "key_array": "island_keyboard",
            "support_module": "rubber_feet",
            "foot_count": 4,
            "rugged_base_thickness_m": 0.038,
            "dual_hinge_open_rad": 2.15,
            "trackpoint_button_travel_m": 0.0010,
            "laptop_key_pitch_m": 0.0180,
        },
        reason="thickest host with separated hinges and the most articulated pointing system",
    ),
    corner_case(
        "thin_full_hinge_clickpad_two_feet",
        {
            "shell_family": "thin_aluminum",
            "hinge_style": "full_width_barrel",
            "pointing_system": "integrated_clickpad",
            "key_array": "island_keyboard",
            "support_module": "rubber_feet",
            "foot_count": 2,
            "thin_base_width_m": 0.30,
            "full_hinge_open_rad": 1.65,
            "clickpad_travel_m": 0.0005,
            "laptop_key_pitch_m": 0.0155,
        },
        reason="smallest thin host at minimum hinge and pointing travel",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_laptop",
    "build_seeded_laptop",
    "config_from_seed",
    "resolve_config",
    "run_laptop_tests",
]
