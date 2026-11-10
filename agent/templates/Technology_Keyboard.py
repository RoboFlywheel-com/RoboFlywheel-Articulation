# SPDX-License-Identifier: Apache-2.0

"""Source-backed desktop keyboard template.

The reviewed source pool supplies four enclosure families, a repeated sculpted
key construction, a rotary media control, and folding rear feet. Key count is
an index-general multiplicity: source counts anchor the placement sequence,
while intermediate counts progressively fill valid optional positions.

Coordinates: X = width, Y = rear, Z = up.
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
    MeshGeometry,
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

ChassisFamily = Literal[
    "tapered_low_profile",
    "recessed_well_slab",
    "stepped_high_profile",
    "tented_split",
]
KeyArray = Literal["sculpted_prismatic_keys"]
ControlModule = Literal["plain_deck", "rotary_media_knob"]
SupportModule = Literal["fixed_pads", "flip_tilt_feet"]

_CHASSIS = (
    "tapered_low_profile",
    "recessed_well_slab",
    "stepped_high_profile",
    "tented_split",
)
_CONTROLS = ("plain_deck", "rotary_media_knob")
_SUPPORTS = ("fixed_pads", "flip_tilt_feet")
_KEY_COUNTS = (61, 68, 75, 82, 87, 93, 98, 104)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("chassis_family", _CHASSIS),
        component_slot("key_array", ("sculpted_prismatic_keys",)),
        component_slot("control_module", _CONTROLS),
        component_slot("support_module", _SUPPORTS),
        multiplicity_slot("key_count", _KEY_COUNTS, item_slot="key_array"),
    )
)

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {
        "case": (0.94, 0.95, 0.94, 1.0),
        "key": (0.985, 0.985, 0.975, 1.0),
        "legend": (0.42, 0.44, 0.46, 1.0),
        "metal": (0.70, 0.72, 0.74, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
    },
    {
        "case": (0.08, 0.09, 0.11, 1.0),
        "key": (0.15, 0.16, 0.18, 1.0),
        "legend": (0.78, 0.79, 0.80, 1.0),
        "metal": (0.58, 0.60, 0.64, 1.0),
        "rubber": (0.04, 0.04, 0.05, 1.0),
    },
    {
        "case": (0.22, 0.25, 0.30, 1.0),
        "key": (0.82, 0.84, 0.86, 1.0),
        "legend": (0.20, 0.21, 0.23, 1.0),
        "metal": (0.78, 0.64, 0.30, 1.0),
        "rubber": (0.08, 0.09, 0.10, 1.0),
    },
)

_KEY_GAP = 0.0022
_KEY_DEPTH_RATIO = 0.84
_KEY_HEIGHT = 0.0048
_KEY_CLEARANCE = 0.0007
_BORDER = 0.012


@dataclass(frozen=True)
class Config:
    chassis_family: ChassisFamily = "tapered_low_profile"
    key_array: KeyArray = "sculpted_prismatic_keys"
    control_module: ControlModule = "plain_deck"
    support_module: SupportModule = "fixed_pads"
    key_count: int = 87
    low_profile_depth_m: float | None = None
    well_depth_m: float | None = None
    high_profile_height_m: float | None = None
    tent_angle_rad: float | None = None
    key_pitch_m: float | None = None
    key_travel_m: float | None = None
    knob_diameter_m: float | None = None
    foot_angle_rad: float | None = None
    palette: int = 0
    name: str = "Technology_Keyboard"


@dataclass(frozen=True)
class ResolvedConfig:
    chassis_family: ChassisFamily
    key_array: KeyArray
    control_module: ControlModule
    support_module: SupportModule
    key_count: int
    low_profile_depth_m: float
    well_depth_m: float
    high_profile_height_m: float
    tent_angle_rad: float
    key_pitch_m: float
    key_travel_m: float
    knob_diameter_m: float
    foot_angle_rad: float
    palette: int
    name: str
    case_width_m: float
    case_depth_m: float
    deck_z_m: float
    layout: tuple[tuple[str, float, float, float], ...]


def _clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def _pick(value: float | None, default: float) -> float:
    return default if value is None else float(value)


def _row(
    labels: list[tuple[str, float]],
    *,
    y: float,
    pitch: float,
) -> list[tuple[str, float, float, float]]:
    span = sum(width for _, width in labels)
    cursor = -span * pitch / 2.0
    result = []
    for label, width in labels:
        result.append((label, cursor + width * pitch / 2.0, y, width))
        cursor += width * pitch
    return result


def _layout_for_count(count: int, pitch: float) -> tuple[tuple[str, float, float, float], ...]:
    """Grow a valid keyboard layout through reviewed optional position groups."""

    base_rows = (
        [("`", 1.0)]
        + [(str(i), 1.0) for i in range(1, 10)]
        + [("0", 1.0), ("-", 1.0), ("=", 1.0), ("BACK", 2.0)],
        [("TAB", 1.5)] + [(ch, 1.0) for ch in "QWERTYUIOP"] + [("[", 1.0), ("]", 1.0), ("\\", 1.5)],
        [("CAPS", 1.75)]
        + [(ch, 1.0) for ch in "ASDFGHJKL"]
        + [(";", 1.0), ("'", 1.0), ("ENTER", 2.25)],
        [("SHIFT", 2.25)]
        + [(ch, 1.0) for ch in "ZXCVBNM"]
        + [(",", 1.0), (".", 1.0), ("/", 1.0), ("SHIFT", 2.75)],
        [
            ("CTRL", 1.25),
            ("OS", 1.25),
            ("ALT", 1.25),
            ("SPACE", 6.25),
            ("ALT", 1.25),
            ("FN", 1.25),
            ("MENU", 1.25),
            ("CTRL", 1.25),
        ],
    )
    positions: list[tuple[str, float, float, float]] = []
    for index, labels in enumerate(base_rows):
        positions.extend(_row(labels, y=(2.0 - index) * pitch, pitch=pitch))
    assert len(positions) == 61

    function = [(f"F{i}", (-7.5 + i) * pitch, 3.15 * pitch, 1.0) for i in range(16)]
    right_x = max(item[1] + item[3] * pitch / 2.0 for item in positions) + 1.25 * pitch
    navigation = [
        (label, right_x + col * pitch, (2.0 - row) * pitch, 1.0)
        for row, labels in enumerate(
            (("INS", "HOME", "PGUP"), ("DEL", "END", "PGDN"), ("UP",), ("LEFT", "DOWN", "RIGHT"))
        )
        for col, label in enumerate(labels)
    ]
    tkl_optional = function + navigation
    if count <= 87:
        positions.extend(tkl_optional[: count - 61])
        return tuple(positions)

    positions.extend(tkl_optional)
    if count <= 93:
        left_x = min(item[1] - item[3] * pitch / 2.0 for item in positions) - 1.1 * pitch
        macro = [(f"G{i + 1}", left_x, (3.0 - i) * pitch, 1.0) for i in range(6)]
        positions.extend(macro[: count - 87])
        return tuple(positions)

    num_x = max(item[1] + item[3] * pitch / 2.0 for item in positions) + 1.6 * pitch
    numpad_grid = (
        ("NUM", "/", "*", "-"),
        ("7", "8", "9", "+"),
        ("4", "5", "6"),
        ("1", "2", "3", "ENTER"),
        ("0", "."),
    )
    numpad = []
    for row, labels in enumerate(numpad_grid):
        for col, label in enumerate(labels):
            width = 2.0 if row == 4 and col == 0 else 1.0
            numpad.append((f"NUM_{label}", num_x + col * pitch, (1.7 - row) * pitch, width))
    positions.extend(numpad[: count - 87])
    return tuple(positions)


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    index = int(seed)
    key_count = _KEY_COUNTS[index % len(_KEY_COUNTS)]
    index //= len(_KEY_COUNTS)
    support = _SUPPORTS[index % len(_SUPPORTS)]
    index //= len(_SUPPORTS)
    control = _CONTROLS[index % len(_CONTROLS)]
    index //= len(_CONTROLS)
    chassis = _CHASSIS[index % len(_CHASSIS)]
    return Config(
        chassis_family=chassis,
        control_module=control,
        support_module=support,
        key_count=key_count,
        low_profile_depth_m=round(rng.uniform(0.108, 0.142), 4),
        well_depth_m=round(rng.uniform(0.003, 0.007), 4),
        high_profile_height_m=round(rng.uniform(0.024, 0.034), 4),
        tent_angle_rad=round(rng.uniform(0.07, 0.16), 4),
        key_pitch_m=round(rng.uniform(0.0175, 0.0200), 4),
        key_travel_m=round(rng.uniform(0.0010, 0.0020), 4),
        knob_diameter_m=round(rng.uniform(0.014, 0.022), 4),
        foot_angle_rad=round(rng.uniform(0.35, 0.65), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"Technology_Keyboard_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    if config.chassis_family not in _CHASSIS:
        raise ValueError(f"unsupported chassis_family: {config.chassis_family}")
    if config.control_module not in _CONTROLS:
        raise ValueError(f"unsupported control_module: {config.control_module}")
    if config.support_module not in _SUPPORTS:
        raise ValueError(f"unsupported support_module: {config.support_module}")
    if int(config.key_count) not in _KEY_COUNTS:
        raise ValueError(f"key_count must be one of {_KEY_COUNTS}")
    pitch = _clamp(_pick(config.key_pitch_m, 0.0185), 0.0175, 0.0200)
    uncentered_layout = _layout_for_count(int(config.key_count), pitch)
    raw_min_x = min(x - width * pitch / 2.0 for _, x, _, width in uncentered_layout)
    raw_max_x = max(x + width * pitch / 2.0 for _, x, _, width in uncentered_layout)
    raw_min_y = min(y - pitch * _KEY_DEPTH_RATIO / 2.0 for _, _, y, _ in uncentered_layout)
    raw_max_y = max(y + pitch * _KEY_DEPTH_RATIO / 2.0 for _, _, y, _ in uncentered_layout)
    center_x = (raw_min_x + raw_max_x) / 2.0
    center_y = (raw_min_y + raw_max_y) / 2.0
    layout = tuple(
        (label, x - center_x, y - center_y, width) for label, x, y, width in uncentered_layout
    )
    min_x = min(x - width * pitch / 2.0 for _, x, _, width in layout)
    max_x = max(x + width * pitch / 2.0 for _, x, _, width in layout)
    min_y = min(y - pitch * _KEY_DEPTH_RATIO / 2.0 for _, _, y, _ in layout)
    max_y = max(y + pitch * _KEY_DEPTH_RATIO / 2.0 for _, _, y, _ in layout)
    control_extra = 0.024 if config.control_module == "rotary_media_knob" else 0.0
    width = max_x - min_x + 2.0 * _BORDER + control_extra
    required_depth = max_y - min_y + 2.0 * _BORDER
    if config.chassis_family == "tapered_low_profile":
        depth = max(
            _clamp(_pick(config.low_profile_depth_m, 0.125), 0.108, 0.142),
            required_depth,
        )
        deck_z = 0.010
    elif config.chassis_family == "stepped_high_profile":
        depth = max(required_depth, 0.125)
        deck_z = _clamp(_pick(config.high_profile_height_m, 0.029), 0.024, 0.034)
    else:
        depth = max(required_depth, 0.118)
        deck_z = (
            0.014
            if config.chassis_family == "recessed_well_slab"
            else 0.0045 * (1.0 + math.cos(_clamp(_pick(config.tent_angle_rad, 0.105), 0.07, 0.16)))
        )
    return ResolvedConfig(
        chassis_family=config.chassis_family,
        key_array=config.key_array,
        control_module=config.control_module,
        support_module=config.support_module,
        key_count=int(config.key_count),
        low_profile_depth_m=_clamp(_pick(config.low_profile_depth_m, 0.125), 0.108, 0.142),
        well_depth_m=_clamp(_pick(config.well_depth_m, 0.005), 0.003, 0.007),
        high_profile_height_m=_clamp(_pick(config.high_profile_height_m, 0.029), 0.024, 0.034),
        tent_angle_rad=_clamp(_pick(config.tent_angle_rad, 0.105), 0.07, 0.16),
        key_pitch_m=pitch,
        key_travel_m=_clamp(_pick(config.key_travel_m, 0.0015), 0.0010, 0.0020),
        knob_diameter_m=_clamp(_pick(config.knob_diameter_m, 0.018), 0.014, 0.022),
        foot_angle_rad=_clamp(_pick(config.foot_angle_rad, 0.52), 0.35, 0.65),
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        case_width_m=width,
        case_depth_m=depth,
        deck_z_m=deck_z,
        layout=layout,
    )


def _materials(model: ArticulatedObject, palette: int):
    colors = _PALETTES[palette]
    return {
        name: model.material(f"keyboard_{palette}_{name}", rgba=rgba)
        for name, rgba in colors.items()
    }


def _box(part, size, xyz, material, name, *, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Box(tuple(float(v) for v in size)),
        origin=Origin(xyz=tuple(float(v) for v in xyz), rpy=rpy),
        material=material,
        name=name, material_class_id="plastic.opaque_glossy_molded",
    )


def _tapered_shell(width: float, depth: float, front_z: float, rear_z: float):
    half_w, half_d = width / 2.0, depth / 2.0
    geometry = MeshGeometry()
    points = (
        (-half_w, -half_d, 0.0),
        (half_w, -half_d, 0.0),
        (half_w, half_d, 0.0),
        (-half_w, half_d, 0.0),
        (-half_w, -half_d, front_z),
        (half_w, -half_d, front_z),
        (half_w, half_d, rear_z),
        (-half_w, half_d, rear_z),
    )
    ids = [geometry.add_vertex(*point) for point in points]
    for a, b, c, d in (
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ):
        geometry.add_face(ids[a], ids[b], ids[c])
        geometry.add_face(ids[a], ids[c], ids[d])
    return mesh_from_geometry(geometry, "keyboard_tapered_shell")


def _chassis_family_tapered_low_profile_build(chassis, r: ResolvedConfig, mats) -> None:
    tag = "chassis_family__tapered_low_profile"
    chassis.visual(
        _tapered_shell(r.case_width_m, r.case_depth_m, 0.006, 0.014),
        material=mats["case"],
        name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded",
    )
    _box(
        chassis,
        (r.case_width_m - 0.028, 0.006, 0.006),
        (0.0, r.case_depth_m / 2.0 - 0.006, 0.016),
        mats["case"],
        f"{tag}__raised_back_edge",
    )


def _chassis_family_recessed_well_slab_build(chassis, r: ResolvedConfig, mats) -> None:
    tag = "chassis_family__recessed_well_slab"
    _box(
        chassis,
        (r.case_width_m, r.case_depth_m, 0.014),
        (0.0, 0.0, 0.007),
        mats["case"],
        f"{tag}__slab",
    )
    rim_h = r.well_depth_m + 0.004
    for side, x in (
        ("left", -r.case_width_m / 2 + _BORDER / 2),
        ("right", r.case_width_m / 2 - _BORDER / 2),
    ):
        _box(
            chassis,
            (_BORDER, r.case_depth_m, rim_h),
            (x, 0.0, 0.014 + rim_h / 2),
            mats["case"],
            f"{tag}__rim_{side}",
        )
    for side, y in (
        ("front", -r.case_depth_m / 2 + _BORDER / 2),
        ("rear", r.case_depth_m / 2 - _BORDER / 2),
    ):
        _box(
            chassis,
            (r.case_width_m, _BORDER, rim_h),
            (0.0, y, 0.014 + rim_h / 2),
            mats["case"],
            f"{tag}__rim_{side}",
        )


def _chassis_family_stepped_high_profile_build(chassis, r: ResolvedConfig, mats) -> None:
    tag = "chassis_family__stepped_high_profile"
    height = r.high_profile_height_m
    _box(
        chassis,
        (r.case_width_m, r.case_depth_m, height),
        (0.0, 0.0, height / 2),
        mats["case"],
        f"{tag}__body",
    )
    groove_z = height * 0.58
    for side, x in (("left", -r.case_width_m / 2 - 0.0005), ("right", r.case_width_m / 2 + 0.0005)):
        _box(
            chassis,
            (0.001, r.case_depth_m - 0.006, 0.002),
            (x, 0.0, groove_z),
            mats["metal"],
            f"{tag}__groove_{side}",
        )
    rim_h = 0.012
    for side, x in (
        ("left", -r.case_width_m / 2 + _BORDER / 2),
        ("right", r.case_width_m / 2 - _BORDER / 2),
    ):
        _box(
            chassis,
            (_BORDER, r.case_depth_m, rim_h),
            (x, 0.0, height + rim_h / 2),
            mats["case"],
            f"{tag}__deep_rim_{side}",
        )
    for side, y in (
        ("front", -r.case_depth_m / 2 + _BORDER / 2),
        ("rear", r.case_depth_m / 2 - _BORDER / 2),
    ):
        _box(
            chassis,
            (r.case_width_m, _BORDER, rim_h),
            (0.0, y, height + rim_h / 2),
            mats["case"],
            f"{tag}__deep_rim_{side}",
        )


def _chassis_family_tented_split_build(chassis, r: ResolvedConfig, mats) -> None:
    tag = "chassis_family__tented_split"
    half = r.case_width_m / 2.0
    rise = half * math.sin(r.tent_angle_rad)
    for side, sign in (("left", -1.0), ("right", 1.0)):
        x = (-1.0 if side == "left" else 1.0) * half / 2.0
        _box(
            chassis,
            (half, r.case_depth_m, 0.009),
            (x, 0.0, 0.0045 + rise / 2.0),
            mats["case"],
            f"{tag}__half_{side}",
            rpy=(0.0, sign * r.tent_angle_rad, 0.0),
        )
        _box(
            chassis,
            (half - 0.022, 0.006, 0.006),
            (x, r.case_depth_m / 2 - 0.006, 0.012 + rise / 2.0),
            mats["case"],
            f"{tag}__rear_edge_{side}",
            rpy=(0.0, sign * r.tent_angle_rad, 0.0),
        )
    bridge_height = rise + 0.003
    _box(
        chassis,
        (0.022, r.case_depth_m, bridge_height),
        (0.0, 0.0, bridge_height / 2.0),
        mats["case"],
        f"{tag}__central_bridge",
    )


_CHASSIS_BUILDERS = {
    "tapered_low_profile": _chassis_family_tapered_low_profile_build,
    "recessed_well_slab": _chassis_family_recessed_well_slab_build,
    "stepped_high_profile": _chassis_family_stepped_high_profile_build,
    "tented_split": _chassis_family_tented_split_build,
}


def _surface_local(r: ResolvedConfig, x: float, y: float) -> tuple[float, float]:
    if r.chassis_family == "tapered_low_profile":
        t = _clamp(y / r.case_depth_m + 0.5, 0.0, 1.0)
        return (0.006 + 0.008 * t - r.deck_z_m, 0.0)
    if r.chassis_family == "tented_split":
        inner = r.case_width_m / 2.0 - abs(x)
        return (
            max(inner, 0.0) * math.sin(r.tent_angle_rad),
            -r.tent_angle_rad if x < 0 else r.tent_angle_rad,
        )
    return (0.0, 0.0)


def _keycap_mesh(width_u: float, pitch: float):
    width = width_u * pitch - _KEY_GAP
    depth = pitch * _KEY_DEPTH_RATIO
    lower = rounded_rect_profile(width, depth, radius=min(0.0022, width * 0.15), corner_segments=5)
    upper = rounded_rect_profile(
        width - 0.0014, depth - 0.0012, radius=min(0.0018, width * 0.14), corner_segments=5
    )
    return mesh_from_geometry(
        LoftGeometry(
            (
                [(x, y, 0.0) for x, y in lower],
                [(x, y, _KEY_HEIGHT) for x, y in upper],
            ),
            cap=True,
            closed=True,
        ),
        f"keyboard_keycap_{width_u:g}u",
    )


def _key_array_sculpted_prismatic_keys_build(model, chassis, r: ResolvedConfig, mats) -> None:
    tag = "key_array__sculpted_prismatic_keys"
    keybed = model.part(
        "keybed", meta={"role": "keybed", "slot": "key_array", "candidate": r.key_array}
    )
    provider = PlaneInterface(
        name="chassis_family.key_deck",
        point=(0.0, 0.0, r.deck_z_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.case_width_m - 0.010, r.case_depth_m - 0.010),
    )
    consumer = PlaneInterface(
        name="key_array.keybed_mount",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.case_width_m - 0.018, r.case_depth_m - 0.018),
    )
    mate = mate_planes(provider, consumer)
    model.articulation(
        f"{tag}__fixed_mount",
        ArticulationType.FIXED,
        parent=chassis,
        child=keybed,
        origin=mate.origin,
    )
    plate_top = min(_surface_local(r, x, y)[0] for _, x, y, _ in r.layout) - 0.0002
    _box(
        keybed,
        (r.case_width_m - 0.018, r.case_depth_m - 0.018, 0.0010),
        (0.0, 0.0, plate_top - 0.0005),
        mats["case"],
        f"{tag}__switch_plate",
    )

    widths = {width for _, _, _, width in r.layout}
    meshes = {width: _keycap_mesh(width, r.key_pitch_m) for width in widths}
    for index, (_label, x, y, width) in enumerate(r.layout):
        surface_z, tilt = _surface_local(r, x, y)
        z = surface_z + _KEY_CLEARANCE
        origin = Origin(xyz=(x, y, z), rpy=(0.0, tilt, 0.0))
        key = model.part(
            f"{tag}__press_key_{index:03d}",
            meta={"role": "key_press", "slot": "key_array", "candidate": r.key_array},
        )
        key.visual(meshes[width], material=mats["key"], name=f"{tag}__cap", material_class_id="plastic.opaque_glossy_molded")
        _box(
            key,
            (min(width * r.key_pitch_m * 0.45, 0.007), 0.0010, 0.00018),
            (0.0, -0.001, _KEY_HEIGHT + 0.00009),
            mats["legend"],
            f"{tag}__legend",
        )
        plunger_height = z - plate_top - 0.0001
        _box(
            key,
            (
                min(width * r.key_pitch_m * 0.42, 0.006),
                0.0045,
                plunger_height,
            ),
            (0.0, 0.0, -plunger_height / 2.0),
            mats["key"],
            f"{tag}__plunger",
        )
        model.articulation(
            f"{tag}__press_joint_{index:03d}",
            ArticulationType.PRISMATIC,
            parent=keybed,
            child=key,
            origin=origin,
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=1.2, velocity=0.08, lower=0.0, upper=r.key_travel_m),
            meta={"motion_qc_repeat_group": "key_press"},
        )


def _control_module_plain_deck_build(model, chassis, r: ResolvedConfig, mats) -> None:
    model.meta["plain_control_deck"] = True


def _control_module_rotary_media_knob_build(model, chassis, r: ResolvedConfig, mats) -> None:
    tag = "control_module__rotary_media_knob"
    radius = r.knob_diameter_m / 2.0
    height = 0.009
    x = r.case_width_m / 2.0 - radius - 0.006
    y = r.case_depth_m / 2.0 - radius - 0.006
    deck = r.deck_z_m + _surface_local(r, x, y)[0]
    slope_delta = radius * math.sin(r.tent_angle_rad) if r.chassis_family == "tented_split" else 0.0
    boss_embed = slope_delta + (0.0002 if r.chassis_family == "tented_split" else 0.0)
    boss_h = 0.0024 + slope_delta if r.chassis_family == "tented_split" else 0.0018
    boss_top = deck - boss_embed + boss_h
    chassis.visual(
        Cylinder(radius=radius + 0.002, length=boss_h),
        origin=Origin(xyz=(x, y, deck - boss_embed + boss_h / 2.0)),
        material=mats["case"],
        name=f"{tag}__boss", material_class_id="plastic.opaque_glossy_molded",
    )
    knob = model.part(
        "media_knob",
        meta={"role": "media_knob", "slot": "control_module", "candidate": r.control_module},
    )
    knob.visual(
        Cylinder(radius=radius, length=height),
        origin=Origin(xyz=(0.0, 0.0, height / 2.0)),
        material=mats["metal"],
        name=f"{tag}__body", material_class_id="metal.aluminum_bare",
    )
    knob.visual(
        Box((0.0015, radius * 0.72, 0.0005)),
        origin=Origin(xyz=(0.0, radius * 0.18, height + 0.00025)),
        material=mats["legend"],
        name=f"{tag}__indicator", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    provider = AxisInterface(
        name="chassis.control_axis",
        point=(x, y, boss_top),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=radius + 0.002,
    )
    consumer = AxisInterface(
        name="control_module.knob_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=radius,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__joint"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=chassis,
        child=knob,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=0.5, velocity=5.0, lower=-math.pi, upper=math.pi),
    )
    register_interface_mate(model, joint, mate)


def _support_module_fixed_pads_build(model, chassis, r: ResolvedConfig, mats) -> None:
    tag = "support_module__fixed_pads"
    for index, x in enumerate((-r.case_width_m * 0.34, r.case_width_m * 0.34)):
        mount_height = (
            r.deck_z_m + max(_surface_local(r, x, -r.case_depth_m * 0.34)[0], 0.0)
            if r.chassis_family == "tented_split"
            else 0.0
        )
        pad_height = 0.003 + mount_height
        _box(
            chassis,
            (0.026, 0.012, pad_height),
            (x, -r.case_depth_m * 0.34, -0.0015 + pad_height / 2.0),
            mats["rubber"],
            f"{tag}__pad_{index}",
        )


def _support_module_flip_tilt_feet_build(model, chassis, r: ResolvedConfig, mats) -> None:
    tag = "support_module__flip_tilt_feet"
    pivot_y = r.case_depth_m / 2.0 - 0.014
    for index, x in enumerate((-r.case_width_m * 0.30, r.case_width_m * 0.30)):
        pivot_depth = 0.002
        mount_height = (
            r.deck_z_m + max(_surface_local(r, x, pivot_y)[0], 0.0)
            if r.chassis_family == "tented_split"
            else 0.0
        )
        pad_h = pivot_depth + mount_height
        _box(
            chassis,
            (0.026, 0.016, pad_h),
            (x, pivot_y, (mount_height - pivot_depth) / 2.0),
            mats["rubber"],
            f"{tag}__hinge_pad_{index}",
        )
        foot = model.part(
            f"tilt_foot_{index}",
            meta={"role": "tilt_foot", "slot": "support_module", "candidate": r.support_module},
        )
        _box(foot, (0.012, 0.034, 0.003), (0.0, -0.017, -0.0015), mats["rubber"], f"{tag}__leg")
        provider = AxisInterface(
            name=f"chassis.foot_axis_{index}",
            point=(x, pivot_y, -pivot_depth),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=0.0024,
        )
        consumer = AxisInterface(
            name=f"support_module.foot_axis_{index}",
            point=(0.0, 0.0, 0.0),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=0.0020,
        )
        mate = mate_axes(provider, consumer, require_fit=True)
        joint = f"{tag}__joint_{index}"
        model.articulation(
            joint,
            ArticulationType.REVOLUTE,
            parent=chassis,
            child=foot,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=r.foot_angle_rad),
        )
        register_interface_mate(model, joint, mate)


_CONTROL_BUILDERS = {
    "plain_deck": _control_module_plain_deck_build,
    "rotary_media_knob": _control_module_rotary_media_knob_build,
}
_SUPPORT_BUILDERS = {
    "fixed_pads": _support_module_fixed_pads_build,
    "flip_tilt_feet": _support_module_flip_tilt_feet_build,
}


def build_keyboard(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    chassis = model.part(
        "keyboard_chassis",
        meta={"role": "keyboard_chassis", "slot": "chassis_family", "candidate": r.chassis_family},
    )
    _CHASSIS_BUILDERS[r.chassis_family](chassis, r, mats)
    _key_array_sculpted_prismatic_keys_build(model, chassis, r, mats)
    _CONTROL_BUILDERS[r.control_module](model, chassis, r, mats)
    _SUPPORT_BUILDERS[r.support_module](model, chassis, r, mats)
    model.meta["slot_choices"] = (
        ("chassis_family", r.chassis_family),
        ("key_array", r.key_array),
        ("control_module", r.control_module),
        ("support_module", r.support_module),
        ("key_count", str(r.key_count)),
    )
    model.meta["key_count_actual"] = r.key_count
    return model


def build_seeded_keyboard(seed: int) -> ArticulatedObject:
    return build_keyboard(config_from_seed(seed))


def run_keyboard_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[object]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part)
    ctx.check(
        "category_anchor: keyboard is wider than deep",
        r.case_width_m > r.case_depth_m * 1.8,
        details=f"width={r.case_width_m:.4f} depth={r.case_depth_m:.4f}",
    )
    ctx.check(
        "category_anchor: key count matches multiplicity",
        int(object_model.meta.get("key_count_actual", 0)) == r.key_count
        and len(r.layout) == r.key_count,
        details=f"actual={object_model.meta.get('key_count_actual')} expected={r.key_count}",
    )
    press_keys = roles.get("key_press", [])
    press_joints = [
        j
        for j in object_model.articulations
        if "key_array__sculpted_prismatic_keys__press_joint_" in j.name
    ]
    moved = True
    for joint in press_joints:
        part = object_model.get_part(joint.child)
        rest = ctx.part_world_position(part)
        with ctx.pose({joint: r.key_travel_m}):
            pressed = ctx.part_world_position(part)
        moved = (
            moved
            and rest is not None
            and pressed is not None
            and pressed[2] < rest[2] - r.key_travel_m * 0.45
        )
    ctx.check(
        "category_anchor: every key presses toward the deck",
        len(press_keys) == r.key_count and len(press_joints) == r.key_count and moved,
        details=f"parts={len(press_keys)} joints={len(press_joints)}",
    )
    if r.control_module == "rotary_media_knob":
        knobs = roles.get("media_knob", [])
        joint = object_model.get_articulation("control_module__rotary_media_knob__joint")
        ctx.check(
            "category_anchor: media knob rotates on its deck boss",
            len(knobs) == 1 and joint.axis == (0.0, 0.0, 1.0),
            details=f"knobs={len(knobs)} axis={joint.axis}",
        )
    if r.support_module == "flip_tilt_feet":
        feet = roles.get("tilt_foot", [])
        downward = True
        for index, foot in enumerate(feet):
            joint = object_model.get_articulation(f"support_module__flip_tilt_feet__joint_{index}")
            rest = ctx.part_world_aabb(foot)
            with ctx.pose({joint: r.foot_angle_rad}):
                deployed = ctx.part_world_aabb(foot)
            downward = (
                downward
                and rest is not None
                and deployed is not None
                and deployed[0][2] < rest[0][2] - 0.004
            )
        ctx.check(
            "category_anchor: paired tilt feet deploy below the chassis",
            len(feet) == 2 and downward,
            details=f"feet={len(feet)}",
        )
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)
    return ctx.report()


run_keyboard_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "wide_full_size_high_profile_knob_feet",
        {
            "chassis_family": "stepped_high_profile",
            "key_array": "sculpted_prismatic_keys",
            "control_module": "rotary_media_knob",
            "support_module": "flip_tilt_feet",
            "key_count": 104,
            "high_profile_height_m": 0.034,
            "key_pitch_m": 0.0200,
            "key_travel_m": 0.0020,
            "knob_diameter_m": 0.022,
            "foot_angle_rad": 0.65,
        },
        reason="largest repeated layout with the deepest case and both moving accessories",
    ),
    corner_case(
        "compact_tented_min_pitch",
        {
            "chassis_family": "tented_split",
            "key_array": "sculpted_prismatic_keys",
            "control_module": "plain_deck",
            "support_module": "fixed_pads",
            "key_count": 61,
            "tent_angle_rad": 0.16,
            "key_pitch_m": 0.0175,
            "key_travel_m": 0.0010,
        },
        reason="smallest key field on the steepest source-backed split surface",
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_keyboard",
    "build_seeded_keyboard",
    "config_from_seed",
    "resolve_config",
    "run_keyboard_tests",
]
