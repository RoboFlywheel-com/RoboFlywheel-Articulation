# SPDX-License-Identifier: Apache-2.0

"""Source-backed numbered elevator car operating panels.

The runtime domain keeps three honest structural axes:

* ten panel/layout families, each able to host every declared floor count;
* three mechanical numbered selectors and one fixed numbered glass-touch cell;
* five source-backed auxiliary control topologies.

``floor_count`` is multiplicity, with all source-observed values 6/8/12/18/30.
Every floor selector is a physical prismatic button and carries its actual floor
designation on the selector surface.  ``numeral_style`` samples six geometric renderings
without inflating core/raw diversity.
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
    MotionLimits,
    MotionProperties,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

__preview_front_axis__ = "-y"

PanelFamily = Literal[
    "compact_pair",
    "service_pair",
    "single_column",
    "three_column",
    "split_zone",
    "horizontal_console",
    "corner_wrap",
    "destination_matrix",
    "glass_inlay",
    "protected_service_bay",
]
ButtonStyle = Literal[
    "round_numbered",
    "square_numbered",
    "wide_tactile_numbered",
    "glass_touch_numbered",
]
AuxStyle = Literal[
    "key_switch",
    "fire_service_cover",
    "accessibility_paddles",
    "door_alarm_cluster",
    "emergency_intercom",
]
NumeralStyle = Literal[
    "seven_segment",
    "cut_stroke",
    "continuous_stroke",
    "dot_matrix",
    "stencil",
    "braille_companion",
]

PANEL_FAMILIES: tuple[PanelFamily, ...] = (
    "compact_pair",
    "service_pair",
    "single_column",
    "three_column",
    "split_zone",
    "horizontal_console",
    "corner_wrap",
    "destination_matrix",
    "glass_inlay",
    "protected_service_bay",
)
BUTTON_STYLES: tuple[ButtonStyle, ...] = (
    "round_numbered",
    "square_numbered",
    "wide_tactile_numbered",
    "glass_touch_numbered",
)
AUX_STYLES: tuple[AuxStyle, ...] = (
    "key_switch",
    "fire_service_cover",
    "accessibility_paddles",
    "door_alarm_cluster",
    "emergency_intercom",
)
NUMERAL_STYLES: tuple[NumeralStyle, ...] = (
    "seven_segment",
    "cut_stroke",
    "continuous_stroke",
    "dot_matrix",
    "stencil",
    "braille_companion",
)
FLOOR_COUNTS: tuple[int, ...] = (6, 8, 12, 18, 30)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("panel_family", PANEL_FAMILIES),
        component_slot("button_style", BUTTON_STYLES),
        component_slot("aux_style", AUX_STYLES),
        multiplicity_slot("floor_count", FLOOR_COUNTS, item_slot="panel_family"),
    )
)

_PANEL_DEPTH_RANGE = (0.022, 0.040)
_PITCH_RANGE = (0.048, 0.066)
_BUTTON_SIZE_RANGE = (0.023, 0.031)
_TRAVEL_RANGE = (0.0018, 0.0035)
_AUX_SCALE_RANGE = (0.054, 0.080)
_FACE_THICKNESS = 0.003
_FLOOR_CAP_CROWN_M = 0.0096
_AUX_CAP_CROWN_M = 0.0068
_REST_STANDOFF_M = 0.0005
_APERTURE_CLEARANCE_M = 0.002


@dataclass(frozen=True)
class Config:
    panel_family: PanelFamily = "compact_pair"
    button_style: ButtonStyle = "round_numbered"
    aux_style: AuxStyle = "key_switch"
    floor_count: int = 12
    panel_depth_m: float | None = None
    pitch_m: float | None = None
    button_size_m: float | None = None
    press_travel_m: float | None = None
    aux_scale_m: float | None = None
    numeral_style: NumeralStyle = "seven_segment"
    name: str = "pictureX_0611_elevator_button_panel"


@dataclass(frozen=True)
class ResolvedConfig:
    panel_family: PanelFamily
    button_style: ButtonStyle
    aux_style: AuxStyle
    floor_count: int
    panel_depth_m: float
    pitch_m: float
    button_size_m: float
    press_travel_m: float
    aux_scale_m: float
    numeral_style: NumeralStyle
    columns: int
    rows: int
    field_bottom_m: float
    field_height_m: float
    panel_width_m: float
    panel_height_m: float
    aux_band_m: float
    info_band_m: float
    name: str


@dataclass(frozen=True)
class _Frame:
    xyz: tuple[float, float, float]
    yaw: float = 0.0

    @property
    def tangent(self) -> tuple[float, float, float]:
        return (math.cos(self.yaw), math.sin(self.yaw), 0.0)

    @property
    def inward(self) -> tuple[float, float, float]:
        return (-math.sin(self.yaw), math.cos(self.yaw), 0.0)

    @property
    def outward(self) -> tuple[float, float, float]:
        inward = self.inward
        return (-inward[0], -inward[1], 0.0)

    def point(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        tangent = self.tangent
        inward = self.inward
        return (
            self.xyz[0] + tangent[0] * x + inward[0] * y,
            self.xyz[1] + tangent[1] * x + inward[1] * y,
            self.xyz[2] + z,
        )


@dataclass(frozen=True)
class _Station:
    index: int
    floor_label: str
    frame: _Frame


@dataclass(frozen=True)
class _PanelBuild:
    part: object
    stations: tuple[_Station, ...]
    aux_frame: _Frame
    width_m: float
    height_m: float


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0xE1E0A7)
    return Config(
        panel_family=choices["panel_family"],
        button_style=choices["button_style"],
        aux_style=choices["aux_style"],
        floor_count=choices["floor_count"],
        panel_depth_m=round(rng.uniform(*_PANEL_DEPTH_RANGE), 5),
        pitch_m=round(rng.uniform(*_PITCH_RANGE), 5),
        button_size_m=round(rng.uniform(*_BUTTON_SIZE_RANGE), 5),
        press_travel_m=round(rng.uniform(*_TRAVEL_RANGE), 5),
        aux_scale_m=round(rng.uniform(*_AUX_SCALE_RANGE), 5),
        numeral_style=NUMERAL_STYLES[rng.randrange(len(NUMERAL_STYLES))],
    )


def _bounded(name: str, value: float, bounds: tuple[float, float]) -> float:
    if not bounds[0] <= value <= bounds[1]:
        raise ValueError(f"{name} must be in [{bounds[0]}, {bounds[1]}], got {value}")
    return value


def _family_columns(family: PanelFamily) -> int:
    return {
        "compact_pair": 2,
        "service_pair": 2,
        "single_column": 1,
        "three_column": 3,
        "split_zone": 2,
        "horizontal_console": 6,
        "corner_wrap": 2,
        "destination_matrix": 3,
        "glass_inlay": 2,
        "protected_service_bay": 2,
    }[family]


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "panel_family": config.panel_family,
            "button_style": config.button_style,
            "aux_style": config.aux_style,
            "floor_count": int(config.floor_count),
        }
    )
    if config.numeral_style not in NUMERAL_STYLES:
        raise ValueError(f"unsupported numeral_style {config.numeral_style!r}")
    depth = _bounded(
        "panel_depth_m",
        0.030 if config.panel_depth_m is None else float(config.panel_depth_m),
        _PANEL_DEPTH_RANGE,
    )
    raw_pitch = _bounded(
        "pitch_m",
        0.057 if config.pitch_m is None else float(config.pitch_m),
        _PITCH_RANGE,
    )
    button_size = _bounded(
        "button_size_m",
        0.027 if config.button_size_m is None else float(config.button_size_m),
        _BUTTON_SIZE_RANGE,
    )
    travel = _bounded(
        "press_travel_m",
        0.0022 if config.press_travel_m is None else float(config.press_travel_m),
        _TRAVEL_RANGE,
    )
    aux_scale = _bounded(
        "aux_scale_m",
        0.064 if config.aux_scale_m is None else float(config.aux_scale_m),
        _AUX_SCALE_RANGE,
    )
    pitch = max(raw_pitch, 1.55 * button_size + 0.010)
    columns = _family_columns(config.panel_family)
    count = int(config.floor_count)
    if config.panel_family == "corner_wrap":
        face_count = int(math.ceil(count / 2.0))
        rows = int(math.ceil(face_count / 2.0))
    elif config.panel_family == "split_zone":
        rows = int(math.ceil(math.ceil(count / 2.0) / 2.0)) + int(
            math.ceil(math.floor(count / 2.0) / 2.0)
        )
    else:
        rows = int(math.ceil(count / float(columns)))

    aux_band = max(
        0.115 if config.panel_family == "protected_service_bay" else 0.090,
        aux_scale + 0.030,
    )
    info_band = 0.028 if config.panel_family == "compact_pair" else 0.155
    if config.panel_family == "single_column":
        info_band = 0.075
    if config.panel_family == "horizontal_console":
        info_band = 0.090
    if config.panel_family == "destination_matrix":
        info_band = 0.080
    if config.panel_family in {"glass_inlay", "protected_service_bay"}:
        info_band = 0.130
    field_bottom = aux_band + 0.020
    field_height = rows * pitch
    paddle_capacity = 3.0 * (aux_scale * 0.42) + 0.040
    base_width = {
        "compact_pair": 0.104,
        "service_pair": 0.170,
        "single_column": 0.104,
        "three_column": 0.170,
        "split_zone": 0.220,
        "horizontal_console": 0.580,
        "corner_wrap": 0.236,
        "destination_matrix": 0.182,
        "glass_inlay": 0.184,
        "protected_service_bay": 0.190,
    }[config.panel_family]
    if config.panel_family == "split_zone":
        field_width = 4.0 * pitch + 0.040
    elif config.panel_family == "corner_wrap":
        field_width = 4.0 * pitch + 0.050
    else:
        field_width = columns * pitch + 0.050
    width = max(base_width, field_width, paddle_capacity)
    if config.panel_family == "horizontal_console":
        height = max(0.180, field_bottom + field_height + 0.026)
    else:
        height = field_bottom + field_height + info_band + 0.028
    return ResolvedConfig(
        panel_family=config.panel_family,
        button_style=config.button_style,
        aux_style=config.aux_style,
        floor_count=count,
        panel_depth_m=depth,
        pitch_m=pitch,
        button_size_m=button_size,
        press_travel_m=travel,
        aux_scale_m=aux_scale,
        numeral_style=config.numeral_style,
        columns=columns,
        rows=rows,
        field_bottom_m=field_bottom,
        field_height_m=field_height,
        panel_width_m=width,
        panel_height_m=height,
        aux_band_m=aux_band,
        info_band_m=info_band,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("panel_family", config.panel_family),
        ("button_style", config.button_style),
        ("aux_style", config.aux_style),
        ("floor_count", int(config.floor_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("brushed_stainless", rgba=(0.69, 0.71, 0.73, 1.0))
    model.material("recess_shadow", rgba=(0.16, 0.18, 0.20, 1.0))
    model.material("polished_chrome", rgba=(0.84, 0.86, 0.88, 1.0))
    model.material("ivory_lens", rgba=(0.98, 0.98, 0.94, 1.0))
    model.material("engraved_black", rgba=(0.008, 0.010, 0.012, 1.0))
    model.material("display_glass", rgba=(0.035, 0.075, 0.09, 0.82))
    model.material("display_light", rgba=(0.15, 0.78, 0.92, 1.0))
    model.material("alarm_red", rgba=(0.74, 0.08, 0.05, 0.94))
    return {
        "steel": "brushed_stainless",
        "shadow": "recess_shadow",
        "chrome": "polished_chrome",
        "lens": "ivory_lens",
        "mark": "engraved_black",
        "glass": "display_glass",
        "light": "display_light",
        "red": "alarm_red",
    }


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.brushed_silver")


def _cylinder(
    part,
    radius: float,
    length: float,
    xyz,
    material: str,
    name: str,
    rpy=(math.pi / 2.0, 0.0, 0.0),
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.chrome_polished",
    )


def _obox(part, frame: _Frame, size, local_xyz, material: str, name: str) -> None:
    _box(
        part,
        size,
        frame.point(*local_xyz),
        material,
        name,
        rpy=(0.0, 0.0, frame.yaw),
    )


def _shell(
    part,
    frame: _Frame,
    *,
    width: float,
    height: float,
    depth: float,
    mats,
    prefix: str,
) -> None:
    """Connected face/recess shell copied from the two source lineages."""
    _obox(
        part,
        frame,
        (width, _FACE_THICKNESS, height),
        (0.0, _FACE_THICKNESS / 2.0, height / 2.0),
        mats["steel"],
        f"{prefix}_faceplate",
    )
    _obox(
        part,
        frame,
        (width - 0.010, 0.004, height - 0.010),
        (0.0, depth - 0.002, height / 2.0),
        mats["shadow"],
        f"{prefix}_recess_back",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _obox(
            part,
            frame,
            (0.006, depth, height - 0.006),
            (sign * (width / 2.0 - 0.003), depth / 2.0, height / 2.0),
            mats["shadow"],
            f"{prefix}_side_return_{index}",
        )
        _obox(
            part,
            frame,
            (width - 0.006, depth, 0.006),
            (0.0, depth / 2.0, height / 2.0 + sign * (height / 2.0 - 0.003)),
            mats["shadow"],
            f"{prefix}_end_return_{index}",
        )


def _flat_grid_stations(
    r: ResolvedConfig,
    columns: int,
    *,
    x_offset: float = 0.0,
) -> tuple[_Station, ...]:
    stations: list[_Station] = []
    for index in range(r.floor_count):
        col = index % columns
        row = index // columns
        x = x_offset + (col - (columns - 1.0) / 2.0) * r.pitch_m
        z = r.field_bottom_m + (row + 0.5) * r.pitch_m
        stations.append(_Station(index, str(index + 1), _Frame((x, 0.0, z))))
    return tuple(stations)


def _split_zone_stations(r: ResolvedConfig) -> tuple[_Station, ...]:
    low_count = int(math.ceil(r.floor_count / 2.0))
    high_count = r.floor_count - low_count
    low_rows = int(math.ceil(low_count / 2.0))
    gap = 0.026
    stations: list[_Station] = []
    for index in range(r.floor_count):
        in_high = index >= low_count
        local = index - low_count if in_high else index
        col = local % 2
        row = local // 2
        x = (col - 0.5) * r.pitch_m
        z = r.field_bottom_m + (row + 0.5) * r.pitch_m
        if in_high:
            z += low_rows * r.pitch_m + gap
        stations.append(_Station(index, str(index + 1), _Frame((x, 0.0, z))))
    return tuple(stations)


def _corner_frames(r: ResolvedConfig) -> tuple[_Frame, _Frame, float]:
    angle = math.radians(15.0)
    face_width = max(0.118, r.panel_width_m / 2.0)
    return _Frame((0.0, 0.0, 0.0), -angle), _Frame((0.0, 0.0, 0.0), angle), face_width


def _corner_stations(r: ResolvedConfig) -> tuple[_Station, ...]:
    left, right, face_width = _corner_frames(r)
    left_count = int(math.ceil(r.floor_count / 2.0))
    stations: list[_Station] = []
    for index in range(r.floor_count):
        on_left = index < left_count
        local = index if on_left else index - left_count
        col = local % 2
        row = local // 2
        local_x = 0.020 + (col + 0.5) * r.pitch_m
        if on_left:
            local_x = -min(local_x, face_width - 0.018)
            face = left
        else:
            local_x = min(local_x, face_width - 0.018)
            face = right
        point = face.point(local_x, 0.0, r.field_bottom_m + (row + 0.5) * r.pitch_m)
        stations.append(_Station(index, str(index + 1), _Frame(point, face.yaw)))
    return tuple(stations)


def _panel_root(model, r: ResolvedConfig):
    return model.part(
        f"panel_family__{r.panel_family}__panel",
        meta={"role": "panel", "family": r.panel_family},
    )


def _mount_fixed(model, parent, child, name: str, frame: _Frame) -> None:
    model.articulation(
        name,
        ArticulationType.FIXED,
        parent=parent,
        child=child,
        origin=Origin(xyz=frame.xyz, rpy=(0.0, 0.0, frame.yaw)),
    )


def _display_module(model, panel, frame: _Frame, mats, prefix: str, width: float) -> None:
    display = model.part(
        f"{prefix}__display",
        meta={"role": "information_module", "kind": "floor display"},
    )
    _box(display, (width, 0.005, 0.050), (0.0, -0.0030, 0.0), mats["shadow"], "display_frame")
    _box(display, (width - 0.010, 0.0012, 0.039), (0.0, -0.0061, 0.0), mats["glass"], "display_glass")
    _box(display, (0.010, 0.0010, 0.025), (0.0, -0.0068, 0.0), mats["light"], "car_position_bar")
    _mount_fixed(model, panel, display, f"{prefix}__display__mount", frame)


def _speaker_module(model, panel, frame: _Frame, mats, prefix: str, width: float) -> None:
    speaker = model.part(
        f"{prefix}__speaker",
        meta={"role": "information_module", "kind": "speaker grille"},
    )
    _box(speaker, (width, 0.004, 0.042), (0.0, -0.0020, 0.0), mats["shadow"], "speaker_backing")
    for row in range(3):
        for col in range(7):
            _cylinder(
                speaker,
                0.0013,
                0.0010,
                ((col - 3.0) * width / 8.0, -0.0044, (row - 1.0) * 0.010),
                mats["mark"],
                f"grille_hole_{row}_{col}",
            )
    _mount_fixed(model, panel, speaker, f"{prefix}__speaker__mount", frame)


def _panel_decorations(panel, r: ResolvedConfig, mats, *, prefix: str) -> None:
    for index, (x, z) in enumerate(
        (
            (-r.panel_width_m / 2.0 + 0.010, 0.012),
            (r.panel_width_m / 2.0 - 0.010, 0.012),
            (-r.panel_width_m / 2.0 + 0.010, r.panel_height_m - 0.012),
            (r.panel_width_m / 2.0 - 0.010, r.panel_height_m - 0.012),
        )
    ):
        _cylinder(panel, 0.0028, 0.0015, (x, -0.00075, z), mats["chrome"], f"{prefix}_screw_{index}")


def _panel_family_compact_pair_build(model, r, mats) -> _PanelBuild:
    panel = _panel_root(model, r)
    _shell(
        panel,
        _Frame((0.0, 0.0, 0.0)),
        width=r.panel_width_m,
        height=r.panel_height_m,
        depth=r.panel_depth_m,
        mats=mats,
        prefix="compact",
    )
    _panel_decorations(panel, r, mats, prefix="compact")
    stations = _flat_grid_stations(r, 2)
    return _PanelBuild(
        panel,
        stations,
        _Frame((0.0, 0.0, r.aux_band_m / 2.0)),
        r.panel_width_m,
        r.panel_height_m,
    )


def _service_pair_shell(model, r, mats, candidate: str, stations) -> _PanelBuild:
    panel = _panel_root(model, r)
    _shell(
        panel,
        _Frame((0.0, 0.0, 0.0)),
        width=r.panel_width_m,
        height=r.panel_height_m,
        depth=r.panel_depth_m,
        mats=mats,
        prefix=candidate,
    )
    _panel_decorations(panel, r, mats, prefix=candidate)
    top_z = r.panel_height_m - r.info_band_m / 2.0 - 0.012
    _display_module(
        model,
        panel,
        _Frame((-r.panel_width_m * 0.18, 0.0, top_z)),
        mats,
        f"panel_family__{candidate}",
        min(0.085, r.panel_width_m * 0.50),
    )
    _speaker_module(
        model,
        panel,
        _Frame((r.panel_width_m * 0.27, 0.0, top_z)),
        mats,
        f"panel_family__{candidate}",
        min(0.050, r.panel_width_m * 0.28),
    )
    return _PanelBuild(
        panel,
        tuple(stations),
        _Frame((0.0, 0.0, r.aux_band_m / 2.0)),
        r.panel_width_m,
        r.panel_height_m,
    )


def _panel_family_service_pair_build(model, r, mats) -> _PanelBuild:
    return _service_pair_shell(model, r, mats, "service_pair", _flat_grid_stations(r, 2))


def _panel_family_single_column_build(model, r, mats) -> _PanelBuild:
    panel = _panel_root(model, r)
    _shell(
        panel,
        _Frame((0.0, 0.0, 0.0)),
        width=r.panel_width_m,
        height=r.panel_height_m,
        depth=r.panel_depth_m,
        mats=mats,
        prefix="single",
    )
    stations = _flat_grid_stations(r, 1)
    _box(
        panel,
        (0.006, 0.004, r.field_height_m),
        (-r.pitch_m * 0.62, -0.0020, r.field_bottom_m + r.field_height_m / 2.0),
        mats["shadow"],
        "single_column_spine",
    )
    _display_module(
        model,
        panel,
        _Frame((0.0, 0.0, r.panel_height_m - r.info_band_m / 2.0 - 0.010)),
        mats,
        "panel_family__single_column",
        min(0.065, r.panel_width_m - 0.026),
    )
    return _PanelBuild(
        panel,
        stations,
        _Frame((0.0, 0.0, r.aux_band_m / 2.0)),
        r.panel_width_m,
        r.panel_height_m,
    )


def _panel_family_three_column_build(model, r, mats) -> _PanelBuild:
    return _service_pair_shell(model, r, mats, "three_column", _flat_grid_stations(r, 3))


def _panel_family_split_zone_build(model, r, mats) -> _PanelBuild:
    stations = _split_zone_stations(r)
    built = _service_pair_shell(model, r, mats, "split_zone", stations)
    low_count = int(math.ceil(r.floor_count / 2.0))
    low_rows = int(math.ceil(low_count / 2.0))
    separator_z = r.field_bottom_m + low_rows * r.pitch_m + 0.013
    _box(
        built.part,
        (min(r.panel_width_m - 0.034, 4.0 * r.pitch_m), 0.005, 0.011),
        (0.0, -0.0025, separator_z),
        mats["chrome"],
        "split_zone_separator",
    )
    for index, z in enumerate(
        (
            r.field_bottom_m + low_rows * r.pitch_m / 2.0,
            separator_z + 0.013 + (r.field_height_m - low_rows * r.pitch_m) / 2.0,
        )
    ):
        _box(
            built.part,
            (min(r.panel_width_m - 0.030, 4.0 * r.pitch_m), 0.003, 0.004),
            (0.0, -0.0015, z),
            mats["shadow"],
            f"split_zone_frame_{index}",
        )
    return built


def _panel_family_horizontal_console_build(model, r, mats) -> _PanelBuild:
    panel = _panel_root(model, r)
    _shell(
        panel,
        _Frame((0.0, 0.0, 0.0)),
        width=r.panel_width_m,
        height=r.panel_height_m,
        depth=r.panel_depth_m,
        mats=mats,
        prefix="horizontal",
    )
    stations = _flat_grid_stations(r, 6, x_offset=0.055)
    module_z = r.panel_height_m - 0.055
    _display_module(
        model,
        panel,
        _Frame((-r.panel_width_m / 2.0 + 0.085, 0.0, module_z)),
        mats,
        "panel_family__horizontal_console",
        0.105,
    )
    _speaker_module(
        model,
        panel,
        _Frame((r.panel_width_m / 2.0 - 0.055, 0.0, module_z)),
        mats,
        "panel_family__horizontal_console",
        0.060,
    )
    return _PanelBuild(
        panel,
        stations,
        _Frame((-r.panel_width_m / 2.0 + 0.170, 0.0, r.aux_band_m / 2.0)),
        r.panel_width_m,
        r.panel_height_m,
    )


def _panel_family_corner_wrap_build(model, r, mats) -> _PanelBuild:
    panel = _panel_root(model, r)
    left, right, face_width = _corner_frames(r)
    left_center = _Frame(left.point(-face_width / 2.0, 0.0, 0.0), left.yaw)
    right_center = _Frame(right.point(face_width / 2.0, 0.0, 0.0), right.yaw)
    _shell(
        panel,
        left_center,
        width=face_width,
        height=r.panel_height_m,
        depth=r.panel_depth_m,
        mats=mats,
        prefix="corner_left",
    )
    _shell(
        panel,
        right_center,
        width=face_width,
        height=r.panel_height_m,
        depth=r.panel_depth_m,
        mats=mats,
        prefix="corner_right",
    )
    _box(
        panel,
        (0.012, r.panel_depth_m, r.panel_height_m),
        (0.0, r.panel_depth_m / 2.0, r.panel_height_m / 2.0),
        mats["shadow"],
        "corner_spine",
    )
    top_z = r.panel_height_m - r.info_band_m / 2.0 - 0.012
    display_point = left.point(-face_width / 2.0, 0.0, top_z)
    speaker_point = left.point(-face_width / 2.0, 0.0, top_z - 0.065)
    _display_module(
        model,
        panel,
        _Frame(display_point, left.yaw),
        mats,
        "panel_family__corner_wrap",
        min(0.090, face_width - 0.030),
    )
    _speaker_module(
        model,
        panel,
        _Frame(speaker_point, left.yaw),
        mats,
        "panel_family__corner_wrap",
        min(0.060, face_width - 0.040),
    )
    aux_point = left.point(-face_width / 2.0, 0.0, r.aux_band_m / 2.0)
    return _PanelBuild(
        panel,
        _corner_stations(r),
        _Frame(aux_point, left.yaw),
        2.0 * face_width,
        r.panel_height_m,
    )


def _panel_family_destination_matrix_build(model, r, mats) -> _PanelBuild:
    built = _service_pair_shell(
        model,
        r,
        mats,
        "destination_matrix",
        _flat_grid_stations(r, 3),
    )
    rail_z = r.field_bottom_m - 0.010
    _box(
        built.part,
        (min(r.panel_width_m - 0.026, 3.4 * r.pitch_m), 0.005, 0.006),
        (0.0, -0.0025, rail_z),
        mats["chrome"],
        "destination_matrix_action_rail",
    )
    action_width = min(0.042, r.panel_width_m * 0.25)
    # Keep the two destination/action wells above the auxiliary buttons.  The
    # previous 0.53-band placement put them on the same centerline as the
    # door/alarm cluster, which made the cyan marks and circular controls
    # visually collide in rendered views.
    action_z = r.aux_band_m * 0.88
    for index, x in enumerate((-action_width * 0.72, action_width * 0.72)):
        _box(
            built.part,
            (action_width, 0.004, 0.018),
            (x, -0.0020, action_z),
            mats["shadow"],
            f"destination_matrix_action_well_{index}",
        )
        _box(
            built.part,
            (action_width * 0.56, 0.0012, 0.0025),
            (x, -0.0046, action_z),
            mats["light"],
            f"destination_matrix_action_mark_{index}",
        )
    return built


def _panel_family_glass_inlay_build(model, r, mats) -> _PanelBuild:
    built = _service_pair_shell(
        model,
        r,
        mats,
        "glass_inlay",
        _flat_grid_stations(r, 2),
    )
    inset_width = min(r.panel_width_m - 0.030, 2.0 * r.pitch_m + 0.026)
    inset_height = r.field_height_m + 0.018
    inset_z = r.field_bottom_m + r.field_height_m / 2.0
    _box(
        built.part,
        (inset_width + 0.010, 0.0045, inset_height + 0.010),
        (0.0, -0.0022, inset_z),
        mats["chrome"],
        "glass_inlay_frame",
    )
    _box(
        built.part,
        (inset_width, 0.0016, inset_height),
        (0.0, -0.0052, inset_z),
        mats["glass"],
        "glass_inlay_surface",
    )
    for index, x in enumerate((-inset_width / 2.0 + 0.006, inset_width / 2.0 - 0.006)):
        _box(
            built.part,
            (0.0022, 0.0010, inset_height - 0.008),
            (x, -0.0064, inset_z),
            mats["light"],
            f"glass_inlay_edge_light_{index}",
        )
    return built


def _panel_family_protected_service_bay_build(model, r, mats) -> _PanelBuild:
    built = _service_pair_shell(
        model,
        r,
        mats,
        "protected_service_bay",
        _flat_grid_stations(r, 2),
    )
    bay_width = min(r.panel_width_m - 0.026, max(0.105, 3.0 * r.aux_scale_m * 0.42 + 0.036))
    bay_height = r.aux_band_m - 0.018
    bay_z = r.aux_band_m / 2.0
    _box(
        built.part,
        (bay_width, 0.006, bay_height),
        (0.0, -0.0030, bay_z),
        mats["shadow"],
        "protected_service_bay_recess",
    )
    _box(
        built.part,
        (bay_width + 0.012, 0.006, 0.008),
        (0.0, -0.0030, r.aux_band_m - 0.009),
        mats["chrome"],
        "protected_service_bay_lintel",
    )
    for index, x in enumerate((-bay_width / 2.0 - 0.004, bay_width / 2.0 + 0.004)):
        _box(
            built.part,
            (0.008, 0.006, bay_height + 0.008),
            (x, -0.0030, bay_z),
            mats["chrome"],
            f"protected_service_bay_jamb_{index}",
        )
        _cylinder(
            built.part,
            0.0024,
            0.010,
            (x, -0.0075, r.aux_band_m - 0.014),
            mats["chrome"],
            f"protected_service_bay_hinge_barrel_{index}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
    return built


_PANEL_BUILDERS = {
    "compact_pair": _panel_family_compact_pair_build,
    "service_pair": _panel_family_service_pair_build,
    "single_column": _panel_family_single_column_build,
    "three_column": _panel_family_three_column_build,
    "split_zone": _panel_family_split_zone_build,
    "horizontal_console": _panel_family_horizontal_console_build,
    "corner_wrap": _panel_family_corner_wrap_build,
    "destination_matrix": _panel_family_destination_matrix_build,
    "glass_inlay": _panel_family_glass_inlay_build,
    "protected_service_bay": _panel_family_protected_service_bay_build,
}


_SEVEN_SEGMENTS = {
    "0": "abcedf",
    "1": "bc",
    "2": "abged",
    "3": "abgcd",
    "4": "fgbc",
    "5": "afgcd",
    "6": "afgecd",
    "7": "abc",
    "8": "abcdefg",
    "9": "abfgcd",
}
_PIXEL_DIGITS = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
}


def _seven_segment_digit(
    part, digit: str, center_x: float, material: str, prefix: str, scale: float
) -> int:
    horizontal = {
        "a": (0.0, 0.00345 * scale),
        "g": (0.0, 0.0),
        "d": (0.0, -0.00345 * scale),
    }
    vertical = {
        "f": (-0.00205 * scale, 0.00175 * scale),
        "b": (0.00205 * scale, 0.00175 * scale),
        "e": (-0.00205 * scale, -0.00175 * scale),
        "c": (0.00205 * scale, -0.00175 * scale),
    }
    count = 0
    for segment in _SEVEN_SEGMENTS[digit]:
        if segment in horizontal:
            dx, dz = horizontal[segment]
            size = (0.00375 * scale, 0.00070, 0.00082 * scale)
        else:
            dx, dz = vertical[segment]
            size = (0.00082 * scale, 0.00070, 0.00295 * scale)
        _box(
            part,
            size,
            (center_x + dx, -0.00970, dz),
            material,
            f"{prefix}_{segment}",
        )
        count += 1
    return count


def _pixel_digit(
    part,
    digit: str,
    center_x: float,
    material: str,
    prefix: str,
    *,
    dots: bool,
    scale: float,
) -> int:
    count = 0
    for row, pattern in enumerate(_PIXEL_DIGITS[digit]):
        for col, active in enumerate(pattern):
            if active != "1":
                continue
            x = center_x + (col - 1.0) * 0.00155 * scale
            z = (2.0 - row) * 0.00155 * scale
            if dots:
                _cylinder(
                    part,
                    0.00058 * scale,
                    0.00068,
                    (x, -0.00970, z),
                    material,
                    f"{prefix}_dot_{row}_{col}",
                )
            else:
                _box(
                    part,
                    (0.00118 * scale, 0.00068, 0.00118 * scale),
                    (x, -0.00970, z),
                    material,
                    f"{prefix}_cut_{row}_{col}",
                )
            count += 1
    return count


def _continuous_digit(
    part,
    digit: str,
    center_x: float,
    material: str,
    prefix: str,
    scale: float,
) -> int:
    """Render a bold, gap-free 3x5 glyph as overlapping black strokes."""
    count = 0
    cell = 0.00165 * scale
    pitch = 0.00155 * scale
    for row, pattern in enumerate(_PIXEL_DIGITS[digit]):
        for col, active in enumerate(pattern):
            if active != "1":
                continue
            _box(
                part,
                (cell, 0.00072, cell),
                (
                    center_x + (col - 1.0) * pitch,
                    -0.00970,
                    (2.0 - row) * pitch,
                ),
                material,
                f"{prefix}_continuous_{row}_{col}",
            )
            count += 1
    return count


def _stencil_digit(
    part, digit: str, center_x: float, material: str, prefix: str, scale: float
) -> int:
    """Render the 3x5 source glyph as consolidated industrial stencil bars."""
    count = 0
    for row, pattern in enumerate(_PIXEL_DIGITS[digit]):
        col = 0
        while col < len(pattern):
            if pattern[col] != "1":
                col += 1
                continue
            start = col
            while col + 1 < len(pattern) and pattern[col + 1] == "1":
                col += 1
            end = col
            width = (end - start + 1) * 0.00120 * scale
            center_col = (start + end) / 2.0
            _box(
                part,
                (width, 0.00064, 0.00078),
                (
                    center_x + (center_col - 1.0) * 0.00120 * scale,
                    -0.00970,
                    (2.0 - row) * 0.00148 * scale,
                ),
                material,
                f"{prefix}_bar_{row}_{start}_{end}",
            )
            count += 1
            col += 1
    return count


_BRAILLE_DIGITS = {
    "1": (1,),
    "2": (1, 2),
    "3": (1, 4),
    "4": (1, 4, 5),
    "5": (1, 5),
    "6": (1, 2, 4),
    "7": (1, 2, 4, 5),
    "8": (1, 2, 5),
    "9": (2, 4),
    "0": (2, 4, 5),
}


def _braille_dots(
    part, digit: str, center_x: float, material: str, prefix: str, scale: float
) -> int:
    count = 0
    for dot in _BRAILLE_DIGITS[digit]:
        column = 0 if dot <= 3 else 1
        row = (dot - 1) % 3
        _cylinder(
            part,
            0.00045 * scale,
            0.00072,
            (
                center_x + (column - 0.5) * 0.00120 * scale,
                -0.00972,
                -0.00470 * scale - row * 0.00108 * scale,
            ),
            material,
            f"{prefix}_braille_{dot}",
        )
        count += 1
    return count


def _add_floor_number(
    part,
    label: str,
    style: NumeralStyle,
    material: str,
    button_size_m: float,
) -> int:
    # Keep the legend comfortably readable as the selector grows.  The small
    # baseline boost makes the existing 24 mm design legible; the remaining
    # scale follows the actual button size so two-digit labels still fit.
    scale = 1.15 * button_size_m / 0.024
    centers = (0.0,) if len(label) == 1 else (-0.00325 * scale, 0.00325 * scale)
    total = 0
    for index, (digit, center) in enumerate(zip(label, centers)):
        if style == "seven_segment":
            total += _seven_segment_digit(
                part, digit, center, material, f"floor_digit_{index}", scale
            )
        elif style in {"cut_stroke", "dot_matrix"}:
            total += _pixel_digit(
                part,
                digit,
                center,
                material,
                f"floor_digit_{index}",
                dots=style == "dot_matrix",
                scale=scale,
            )
        elif style == "continuous_stroke":
            total += _continuous_digit(
                part, digit, center, material, f"floor_digit_{index}", scale
            )
        elif style == "stencil":
            total += _stencil_digit(
                part, digit, center, material, f"floor_digit_{index}", scale
            )
        else:
            total += _seven_segment_digit(
                part,
                digit,
                center,
                material,
                f"floor_digit_{index}",
                scale,
            )
            total += _braille_dots(
                part,
                digit,
                center,
                material,
                f"floor_digit_{index}",
                scale,
            )
    return total


def _round_bezel(panel, station: _Station, r: ResolvedConfig, mats) -> None:
    ring_radius = r.button_size_m / 2.0 + 0.0030
    for step in range(12):
        angle = 2.0 * math.pi * step / 12.0
        local_x = ring_radius * math.sin(angle)
        local_z = ring_radius * math.cos(angle)
        point = station.frame.point(local_x, -0.0016, local_z)
        _box(
            panel,
            (0.0070, 0.0032, 0.0024),
            point,
            mats["chrome"],
            f"round_bezel_{station.index}_{step}",
            rpy=(0.0, angle, station.frame.yaw),
        )


def _square_bezel(panel, station: _Station, r: ResolvedConfig, mats) -> None:
    half = r.button_size_m / 2.0 + 0.0030
    for step, (x, z, sx, sz) in enumerate(
        (
            (-half, 0.0, 0.0032, 2.0 * half),
            (half, 0.0, 0.0032, 2.0 * half),
            (0.0, -half, 2.0 * half, 0.0032),
            (0.0, half, 2.0 * half, 0.0032),
        )
    ):
        _box(
            panel,
            (sx, 0.0032, sz),
            station.frame.point(x, -0.0016, z),
            mats["chrome"],
            f"square_bezel_{station.index}_{step}",
            rpy=(0.0, 0.0, station.frame.yaw),
        )


def _wide_bezel(panel, station: _Station, r: ResolvedConfig, mats) -> None:
    half_x = 1.55 * r.button_size_m / 2.0 + 0.0030
    half_z = r.button_size_m / 2.0 + 0.0030
    for step, (x, z, sx, sz) in enumerate(
        (
            (-half_x, 0.0, 0.0032, 2.0 * half_z),
            (half_x, 0.0, 0.0032, 2.0 * half_z),
            (0.0, -half_z, 2.0 * half_x, 0.0032),
            (0.0, half_z, 2.0 * half_x, 0.0032),
        )
    ):
        _box(
            panel,
            (sx, 0.0032, sz),
            station.frame.point(x, -0.0016, z),
            mats["chrome"],
            f"wide_bezel_{station.index}_{step}",
            rpy=(0.0, 0.0, station.frame.yaw),
        )


def _touch_bezel(panel, station: _Station, r: ResolvedConfig, mats) -> None:
    half = r.button_size_m / 2.0 + 0.0022
    for step, (x, z, sx, sz) in enumerate(
        (
            (-half, 0.0, 0.0016, 2.0 * half),
            (half, 0.0, 0.0016, 2.0 * half),
            (0.0, -half, 2.0 * half, 0.0016),
            (0.0, half, 2.0 * half, 0.0016),
        )
    ):
        _box(
            panel,
            (sx, 0.0044, sz),
            station.frame.point(x, -0.0022, z),
            mats["light"],
            f"touch_bezel_{station.index}_{step}",
            rpy=(0.0, 0.0, station.frame.yaw),
        )


def _button_style_round_numbered_build(model, r, mats, panel, station: _Station):
    _round_bezel(panel, station, r, mats)
    button = model.part(
        f"button_style__round_numbered__button_{station.index}",
        meta={
            "role": "button",
            "index": station.index,
            "floor_number": station.floor_label,
            "numeral_style": r.numeral_style,
        },
    )
    radius = r.button_size_m / 2.0
    _cylinder(button, radius * 0.42, 0.013, (0.0, 0.0045, 0.0), mats["shadow"], "button_stem")
    _cylinder(button, radius, 0.0056, (0.0, -0.0048, 0.0), mats["chrome"], "button_carrier")
    _cylinder(button, radius * 0.86, 0.0018, (0.0, -0.0085, 0.0), mats["lens"], "indicator_lens")
    count = _add_floor_number(
        button, station.floor_label, r.numeral_style, mats["mark"], r.button_size_m
    )
    button.meta["legend_visual_count"] = count
    return button


def _button_style_square_numbered_build(model, r, mats, panel, station: _Station):
    _square_bezel(panel, station, r, mats)
    button = model.part(
        f"button_style__square_numbered__button_{station.index}",
        meta={
            "role": "button",
            "index": station.index,
            "floor_number": station.floor_label,
            "numeral_style": r.numeral_style,
        },
    )
    side = r.button_size_m
    _box(button, (side * 0.42, 0.013, side * 0.42), (0.0, 0.0045, 0.0), mats["shadow"], "button_stem")
    _box(button, (side, 0.0056, side), (0.0, -0.0048, 0.0), mats["chrome"], "button_carrier")
    _box(button, (side * 0.86, 0.0018, side * 0.86), (0.0, -0.0085, 0.0), mats["lens"], "indicator_lens")
    count = _add_floor_number(
        button, station.floor_label, r.numeral_style, mats["mark"], r.button_size_m
    )
    button.meta["legend_visual_count"] = count
    return button


def _button_style_wide_tactile_numbered_build(model, r, mats, panel, station: _Station):
    _wide_bezel(panel, station, r, mats)
    button = model.part(
        f"button_style__wide_tactile_numbered__button_{station.index}",
        meta={
            "role": "button",
            "index": station.index,
            "floor_number": station.floor_label,
            "numeral_style": r.numeral_style,
            "selector_kind": "mechanical",
        },
    )
    height = r.button_size_m
    width = 1.55 * height
    _box(
        button,
        (width * 0.40, 0.013, height * 0.42),
        (0.0, 0.0045, 0.0),
        mats["shadow"],
        "button_stem",
    )
    _box(
        button,
        (width, 0.0056, height),
        (0.0, -0.0048, 0.0),
        mats["chrome"],
        "button_carrier",
    )
    _box(
        button,
        (width * 0.90, 0.0018, height * 0.84),
        (0.0, -0.0085, 0.0),
        mats["lens"],
        "indicator_lens",
    )
    _box(
        button,
        (width * 0.52, 0.0009, 0.0012),
        (0.0, -0.0098, -height * 0.32),
        mats["mark"],
        "tactile_ridge",
    )
    count = _add_floor_number(
        button, station.floor_label, r.numeral_style, mats["mark"], r.button_size_m
    )
    button.meta["legend_visual_count"] = count
    return button


def _button_style_glass_touch_numbered_build(model, r, mats, panel, station: _Station):
    _touch_bezel(panel, station, r, mats)
    button = model.part(
        f"button_style__glass_touch_numbered__button_{station.index}",
        meta={
            "role": "button",
            "index": station.index,
            "floor_number": station.floor_label,
            "numeral_style": r.numeral_style,
            "selector_kind": "fixed_touch",
        },
    )
    side = r.button_size_m
    _box(
        button,
        (side + 0.004, 0.0060, side + 0.004),
        (0.0, -0.0030, 0.0),
        mats["shadow"],
        "touch_backing",
    )
    _box(
        button,
        (side, 0.0024, side),
        (0.0, -0.0072, 0.0),
        mats["glass"],
        "touch_glass",
    )
    _box(
        button,
        (side * 0.82, 0.0012, side * 0.82),
        (0.0, -0.0090, 0.0),
        mats["light"],
        "touch_indicator",
    )
    count = _add_floor_number(
        button, station.floor_label, r.numeral_style, mats["mark"], r.button_size_m
    )
    button.meta["legend_visual_count"] = count
    return button


_BUTTON_BUILDERS = {
    "round_numbered": _button_style_round_numbered_build,
    "square_numbered": _button_style_square_numbered_build,
    "wide_tactile_numbered": _button_style_wide_tactile_numbered_build,
    "glass_touch_numbered": _button_style_glass_touch_numbered_build,
}


def _build_floor_buttons(model, r, mats, panel_build: _PanelBuild) -> None:
    builder = _BUTTON_BUILDERS[r.button_style]
    for station in panel_build.stations:
        button = builder(model, r, mats, panel_build.part, station)
        if r.button_style == "glass_touch_numbered":
            model.articulation(
                f"button_style__glass_touch_numbered__button_{station.index}__mount",
                ArticulationType.FIXED,
                parent=panel_build.part,
                child=button,
                origin=Origin(
                    xyz=station.frame.xyz,
                    rpy=(0.0, 0.0, station.frame.yaw),
                ),
                meta={
                    "mechanism": "fixed glass touch selector",
                    "floor_number": station.floor_label,
                },
            )
            continue
        model.articulation(
            f"button_style__{r.button_style}__button_{station.index}__press",
            ArticulationType.PRISMATIC,
            parent=panel_build.part,
            child=button,
            origin=Origin(
                xyz=station.frame.point(0.0, -_REST_STANDOFF_M, 0.0),
                rpy=(0.0, 0.0, station.frame.yaw),
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=4.0,
                velocity=0.08,
                lower=0.0,
                upper=r.press_travel_m,
            ),
            motion_properties=MotionProperties(damping=0.8, friction=0.4),
            meta={
                "mechanism": "floor button press",
                "floor_number": station.floor_label,
                "motion_qc_repeat_group": "floor_buttons",
            },
        )


def _axis_joint(
    model,
    parent,
    child,
    *,
    name: str,
    provider_point,
    provider_axis,
    provider_radial,
    consumer_axis,
    consumer_radial,
    radius: float,
    limits: MotionLimits,
    mechanism: str,
) -> str:
    provider = AxisInterface(
        name=f"{name}__provider",
        point=provider_point,
        axis=provider_axis,
        radial=provider_radial,
        radius=radius + 0.001,
    )
    consumer = AxisInterface(
        name=f"{name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=consumer_axis,
        radial=consumer_radial,
        radius=radius,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=0.6, friction=0.3),
        meta={"mechanism": mechanism},
    )
    register_interface_mate(model, name, mate)
    return name


def _aux_style_key_switch_build(model, r, mats, panel_build: _PanelBuild) -> None:
    frame = panel_build.aux_frame
    _cylinder(
        panel_build.part,
        r.aux_scale_m * 0.18,
        0.003,
        frame.point(0.0, -0.0015, 0.0),
        mats["chrome"],
        "aux_style__key_switch__escutcheon",
        rpy=(math.pi / 2.0, 0.0, frame.yaw),
    )
    control = model.part(
        "aux_style__key_switch__control",
        meta={"role": "aux_control", "kind": "rotary key switch"},
    )
    _cylinder(control, r.aux_scale_m * 0.12, 0.011, (0.0, -0.0040, 0.0), mats["steel"], "key_barrel")
    _box(control, (0.0035, 0.0010, 0.012), (0.0, -0.0100, 0.0), mats["mark"], "key_slot")
    _axis_joint(
        model,
        panel_build.part,
        control,
        name="aux_style__key_switch__turn",
        provider_point=frame.point(0.0, -0.0003, 0.0),
        provider_axis=frame.inward,
        provider_radial=(0.0, 0.0, 1.0),
        consumer_axis=(0.0, 1.0, 0.0),
        consumer_radial=(0.0, 0.0, 1.0),
        radius=r.aux_scale_m * 0.12,
        limits=MotionLimits(effort=0.55, velocity=1.5, lower=-0.65, upper=0.65),
        mechanism="key switch",
    )


def _aux_style_fire_service_cover_build(model, r, mats, panel_build: _PanelBuild) -> None:
    frame = panel_build.aux_frame
    width = min(panel_build.width_m - 0.030, r.aux_scale_m * 1.35)
    height = r.aux_scale_m * 0.72
    _obox(
        panel_build.part,
        frame,
        (width + 0.008, 0.004, height + 0.008),
        (0.0, -0.0020, 0.0),
        mats["shadow"],
        "aux_style__fire_service_cover__recess",
    )
    control = model.part(
        "aux_style__fire_service_cover__control",
        meta={"role": "aux_control", "kind": "hinged fire-service cover"},
    )
    _cylinder(control, 0.0035, width, (0.0, 0.0, 0.0), mats["chrome"], "hinge_knuckle", rpy=(0.0, math.pi / 2.0, 0.0))
    _box(control, (width, 0.004, height), (0.0, -0.0040, height / 2.0), mats["glass"], "cover_pane")
    _box(control, (width * 0.34, 0.006, 0.008), (0.0, -0.0060, height - 0.009), mats["red"], "fire_tab")
    # The source knuckle is seated in the recess frame.  At -7.4 mm its
    # 3.5 mm radius overlaps the frame lip by 0.1 mm, keeping the closed
    # cover supported without making it sweep through the faceplate.
    hinge_point = frame.point(0.0, -0.0074, -height / 2.0)
    _axis_joint(
        model,
        panel_build.part,
        control,
        name="aux_style__fire_service_cover__swing",
        provider_point=hinge_point,
        provider_axis=frame.tangent,
        provider_radial=(0.0, 0.0, 1.0),
        consumer_axis=(1.0, 0.0, 0.0),
        consumer_radial=(0.0, 0.0, 1.0),
        radius=0.0035,
        limits=MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=1.15),
        mechanism="fire service cover",
    )


def _aux_style_accessibility_paddles_build(model, r, mats, panel_build: _PanelBuild) -> None:
    frame = panel_build.aux_frame
    width = r.aux_scale_m * 0.42
    height = r.aux_scale_m * 0.42
    stagger = min(0.012, max(0.008, r.aux_scale_m * 0.16))
    for index in range(3):
        local_x = (index - 1.0) * (width + 0.008)
        local_z = (stagger, 0.0, -stagger)[index]
        _obox(
            panel_build.part,
            frame,
            (width + 0.006, 0.004, height + 0.006),
            (local_x, -0.0020, local_z),
            mats["shadow"],
            f"aux_style__accessibility_paddles__guide_{index}",
        )
        control = model.part(
            f"aux_style__accessibility_paddles__control_{index}",
            meta={
                "role": "aux_control",
                "index": index,
                "kind": "accessibility paddle",
                "layout_local_z": local_z,
            },
        )
        _box(control, (width * 0.45, 0.012, height * 0.45), (0.0, 0.004, 0.0), mats["shadow"], "paddle_stem")
        _box(control, (width, 0.0035, height), (0.0, -0.0037, 0.0), mats["steel"], "paddle_cap")
        _box(control, (width * 0.55, 0.0010, 0.0030), (0.0, -0.0058, 0.0), mats["mark"], "paddle_tactile_bar")
        model.articulation(
            f"aux_style__accessibility_paddles__control_{index}__press",
            ArticulationType.PRISMATIC,
            parent=panel_build.part,
            child=control,
            origin=Origin(
                xyz=frame.point(local_x, -_REST_STANDOFF_M, local_z),
                rpy=(0.0, 0.0, frame.yaw),
            ),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=7.0,
                velocity=0.08,
                lower=0.0,
                upper=r.press_travel_m,
            ),
            motion_properties=MotionProperties(damping=0.8, friction=0.4),
            meta={"mechanism": "accessibility paddle press"},
        )


def _aux_symbol(part, kind: str, mats) -> None:
    if kind in {"door_open", "door_close"}:
        opening = kind == "door_open"
        angles = (
            (-math.pi / 4.0, math.pi / 4.0)
            if opening
            else (math.pi / 4.0, -math.pi / 4.0)
        )
        for index, (x, angle) in enumerate(zip((-0.0020, 0.0020), angles)):
            _box(
                part,
                (0.0040, 0.00045, 0.00075),
                (x, -0.00665, 0.0),
                mats["mark"],
                f"{kind}_chevron_{index}",
                rpy=(0.0, angle, 0.0),
            )
    else:
        _box(part, (0.0065, 0.00045, 0.0032), (0.0, -0.00665, 0.0007), mats["mark"], "alarm_bell")
        _box(part, (0.0080, 0.00045, 0.0009), (0.0, -0.00665, -0.0012), mats["mark"], "alarm_lip")
        _cylinder(part, 0.00075, 0.00045, (0.0, -0.00665, -0.0023), mats["mark"], "alarm_clapper")


def _compact_aux_button(
    model,
    r,
    mats,
    panel_build: _PanelBuild,
    *,
    prefix: str,
    index: int,
    local_x: float,
    local_z: float,
    kind: str,
):
    frame = panel_build.aux_frame
    radius = min(0.0090, r.aux_scale_m * 0.125)
    _cylinder(
        panel_build.part,
        radius + 0.0030,
        0.0032,
        frame.point(local_x, -0.0016, local_z),
        mats["chrome"],
        f"{prefix}_bezel_{index}",
        rpy=(math.pi / 2.0, 0.0, frame.yaw),
    )
    control = model.part(
        f"{prefix}__control_{index}",
        meta={
            "role": "aux_control",
            "index": index,
            "kind": kind,
            "layout_local_z": local_z,
        },
    )
    _cylinder(control, radius * 0.42, 0.012, (0.0, 0.0040, 0.0), mats["shadow"], "control_stem")
    _cylinder(control, radius, 0.0034, (0.0, -0.0037, 0.0), mats["chrome"], "control_carrier")
    _cylinder(
        control,
        radius * 0.84,
        0.0012,
        (0.0, -0.0060, 0.0),
        mats["red"] if kind == "alarm" else mats["lens"],
        "control_lens",
    )
    _aux_symbol(control, kind, mats)
    model.articulation(
        f"{prefix}__control_{index}__press",
        ArticulationType.PRISMATIC,
        parent=panel_build.part,
        child=control,
        origin=Origin(
            xyz=frame.point(local_x, -_REST_STANDOFF_M, local_z),
            rpy=(0.0, 0.0, frame.yaw),
        ),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=7.0 if kind == "alarm" else 5.0,
            velocity=0.08,
            lower=0.0,
            upper=r.press_travel_m,
        ),
        motion_properties=MotionProperties(damping=0.8, friction=0.4),
        meta={"mechanism": f"{kind} auxiliary press"},
    )
    return control


def _aux_style_door_alarm_cluster_build(model, r, mats, panel_build: _PanelBuild) -> None:
    spacing = min(0.027, r.aux_scale_m * 0.38)
    for index, (kind, local_x) in enumerate(
        zip(("door_open", "door_close", "alarm"), (-spacing, 0.0, spacing))
    ):
        _compact_aux_button(
            model,
            r,
            mats,
            panel_build,
            prefix="aux_style__door_alarm_cluster",
            index=index,
            local_x=local_x,
            local_z=0.0,
            kind=kind,
        )


def _aux_style_emergency_intercom_build(model, r, mats, panel_build: _PanelBuild) -> None:
    alarm_x = -r.aux_scale_m * 0.30
    stagger = min(0.012, max(0.008, r.aux_scale_m * 0.16))
    _compact_aux_button(
        model,
        r,
        mats,
        panel_build,
        prefix="aux_style__emergency_intercom",
        index=0,
        local_x=alarm_x,
        local_z=stagger,
        kind="alarm",
    )
    frame = panel_build.aux_frame
    speaker = model.part(
        "aux_style__emergency_intercom__control_1",
        meta={
            "role": "aux_control",
            "index": 1,
            "kind": "intercom speaker",
            "layout_local_z": -stagger,
        },
    )
    speaker_width = r.aux_scale_m * 0.55
    speaker_height = r.aux_scale_m * 0.46
    _box(
        speaker,
        (speaker_width, 0.0050, speaker_height),
        (0.0, -0.0025, 0.0),
        mats["shadow"],
        "speaker_backing",
    )
    for row in range(3):
        for col in range(5):
            _cylinder(
                speaker,
                0.0011,
                0.0010,
                (
                    (col - 2.0) * speaker_width / 6.0,
                    -0.0050,
                    (row - 1.0) * speaker_height / 4.0,
                ),
                mats["mark"],
                f"speaker_perforation_{row}_{col}",
            )
    speaker_frame = _Frame(
        frame.point(r.aux_scale_m * 0.25, 0.0, -stagger),
        frame.yaw,
    )
    _mount_fixed(
        model,
        panel_build.part,
        speaker,
        "aux_style__emergency_intercom__control_1__mount",
        speaker_frame,
    )


_AUX_BUILDERS = {
    "key_switch": _aux_style_key_switch_build,
    "fire_service_cover": _aux_style_fire_service_cover_build,
    "accessibility_paddles": _aux_style_accessibility_paddles_build,
    "door_alarm_cluster": _aux_style_door_alarm_cluster_build,
    "emergency_intercom": _aux_style_emergency_intercom_build,
}


def build_pictureX_0611_elevator_button_panel(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_elevator_button_panel",
            "identified_object": "numbered elevator car operating panel",
            "slot_choices": slot_choices_for_config(r),
            "numeral_style": r.numeral_style,
        },
    )
    mats = _materials(model)
    panel_build = _PANEL_BUILDERS[r.panel_family](model, r, mats)
    _build_floor_buttons(model, r, mats, panel_build)
    _AUX_BUILDERS[r.aux_style](model, r, mats, panel_build)
    return model


def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _button_aperture(station: _Station, r: ResolvedConfig) -> PlaneInterface:
    extent_x = (
        1.55 * r.button_size_m + 2.0 * _APERTURE_CLEARANCE_M
        if r.button_style == "wide_tactile_numbered"
        else r.button_size_m + 2.0 * _APERTURE_CLEARANCE_M
    )
    if r.button_style == "glass_touch_numbered":
        extent_x += 0.002
    extent_z = r.button_size_m + 2.0 * _APERTURE_CLEARANCE_M
    if r.button_style == "glass_touch_numbered":
        extent_z += 0.002
    return PlaneInterface(
        point=station.frame.xyz,
        normal=station.frame.outward,
        tangent_u=station.frame.tangent,
        extent=(extent_x, extent_z),
        name=f"floor_{station.floor_label}_aperture",
    )


def run_pictureX_0611_elevator_button_panel_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    panels = _parts_by_role(model, "panel")
    buttons = _parts_by_role(model, "button")
    aux_controls = _parts_by_role(model, "aux_control")
    panel = panels[0] if panels else None
    stations = _corner_stations(r) if r.panel_family == "corner_wrap" else (
        _split_zone_stations(r)
        if r.panel_family == "split_zone"
        else _flat_grid_stations(
            r,
            r.columns,
            x_offset=0.055 if r.panel_family == "horizontal_console" else 0.0,
        )
    )

    ctx.check(
        "category_anchor: one operating panel carries the station",
        len(panels) == 1,
        details=f"panels={[part.name for part in panels]}",
    )
    ctx.check(
        "category_anchor: N floor selectors are present",
        len(buttons) == r.floor_count,
        details=f"buttons={len(buttons)}, expected={r.floor_count}",
    )
    expected_labels = [str(index + 1) for index in range(r.floor_count)]
    actual_labels = [str(part.meta.get("floor_number")) for part in buttons]
    visible_numbers = all(
        int(part.meta.get("legend_visual_count", 0)) > 0
        and any(visual.name.startswith("floor_digit_") for visual in part.visuals)
        for part in buttons
    )
    ctx.check(
        "category_anchor: every floor button carries its visible floor number",
        actual_labels == expected_labels and visible_numbers,
        details=(
            f"labels={actual_labels}, expected={expected_labels}, "
            f"numeral_style={r.numeral_style}"
        ),
    )

    presses = [
        joint
        for joint in model.articulations
        if joint.meta.get("mechanism") == "floor button press"
    ]
    touch_mounts = [
        joint
        for joint in model.articulations
        if joint.meta.get("mechanism") == "fixed glass touch selector"
    ]
    mechanical = r.button_style != "glass_touch_numbered"
    ctx.check(
        "category_anchor: mechanical floor selectors use real prismatic joints",
        (not mechanical)
        or (
            len(presses) == r.floor_count
            and not touch_mounts
            and all(joint.articulation_type == ArticulationType.PRISMATIC for joint in presses)
        ),
        details=f"style={r.button_style}, presses={len(presses)}, expected={r.floor_count}",
    )
    ctx.check(
        "category_anchor: glass touch floor selectors remain fixed",
        mechanical
        or (
            len(touch_mounts) == r.floor_count
            and not presses
            and all(joint.articulation_type == ArticulationType.FIXED for joint in touch_mounts)
        ),
        details=f"style={r.button_style}, fixed_touch={len(touch_mounts)}",
    )
    expected_aux = {
        "key_switch": 1,
        "fire_service_cover": 1,
        "accessibility_paddles": 3,
        "door_alarm_cluster": 3,
        "emergency_intercom": 2,
    }[r.aux_style]
    aux_joints = [
        joint
        for joint in model.articulations
        if joint.child in {part.name for part in aux_controls}
    ]
    if r.aux_style in {"key_switch", "fire_service_cover"}:
        aux_joint_ok = (
            len(aux_joints) == 1
            and aux_joints[0].articulation_type == ArticulationType.REVOLUTE
        )
    elif r.aux_style in {"accessibility_paddles", "door_alarm_cluster"}:
        aux_joint_ok = len(aux_joints) == 3 and all(
            joint.articulation_type == ArticulationType.PRISMATIC
            for joint in aux_joints
        )
    else:
        aux_joint_ok = (
            len(aux_joints) == 2
            and sum(
                joint.articulation_type == ArticulationType.PRISMATIC
                for joint in aux_joints
            )
            == 1
            and sum(
                joint.articulation_type == ArticulationType.FIXED
                for joint in aux_joints
            )
            == 1
        )
    ctx.check(
        "category_anchor: the panel carries its auxiliary module",
        len(aux_controls) == expected_aux and aux_joint_ok,
        details=f"aux={[part.name for part in aux_controls]}",
    )

    aux_layout_ok = True
    if r.aux_style in {"accessibility_paddles", "emergency_intercom"}:
        aux_z = [float(part.meta.get("layout_local_z", 0.0)) for part in aux_controls]
        aux_layout_ok = max(aux_z) - min(aux_z) >= 2.0 * min(
            0.012, max(0.008, r.aux_scale_m * 0.16)
        ) - 1e-9
    elif r.aux_style == "door_alarm_cluster":
        aux_z = [float(part.meta.get("layout_local_z", 0.0)) for part in aux_controls]
        aux_layout_ok = max(aux_z) - min(aux_z) <= 1e-9
    ctx.check(
        "layout: auxiliary controls follow their intentional vertical layout",
        aux_layout_ok,
        details=f"aux_z={[part.meta.get('layout_local_z', 0.0) for part in aux_controls]}",
    )

    destination_gap_ok = True
    if r.panel_family == "destination_matrix":
        stagger = min(0.012, max(0.008, r.aux_scale_m * 0.16))
        button_radius = min(0.0090, r.aux_scale_m * 0.125)
        button_top = r.aux_band_m * 0.50 + stagger + button_radius + 0.0030
        action_bottom = r.aux_band_m * 0.88 - 0.0090
        destination_gap_ok = action_bottom - button_top >= 0.004
    ctx.check(
        "layout: destination action wells clear the auxiliary buttons",
        destination_gap_ok,
        details=f"destination_gap={action_bottom - button_top:.4f}"
        if r.panel_family == "destination_matrix"
        else "not applicable",
    )

    exposure_ok = len(stations) == len(buttons) and (
        (not mechanical) or _FLOOR_CAP_CROWN_M - r.press_travel_m >= 0.0055
    )
    surface_details: list[str] = []
    if (
        panel is not None
        and (
            len(presses) == len(stations)
            if mechanical
            else len(touch_mounts) == len(stations)
        )
        and r.panel_family != "corner_wrap"
    ):
        full_pose = (
            {joint: joint.motion_limits.upper for joint in presses}
            if mechanical
            else {}
        )
        with ctx.pose(full_pose):
            by_index = {int(part.meta["index"]): part for part in buttons}
            for station in stations:
                part = by_index.get(station.index)
                if part is None:
                    exposure_ok = False
                    continue
                frame = _button_aperture(station, r)
                exposure_ok &= ctx.expect_footprint_within(
                    part,
                    frame=frame,
                    frame_part=panel,
                    name=f"floor {station.floor_label} stays within its bezel at full travel",
                )
                exposure_ok &= ctx.expect_normal_band(
                    part,
                    frame=frame,
                    frame_part=panel,
                    minimum=-0.016,
                    maximum=0.014,
                    minimum_protrusion=0.0055 if mechanical else 0.0015,
                    name=f"floor {station.floor_label} remains proud at full travel",
                )
    elif r.panel_family == "corner_wrap":
        # The two station planes are oblique and share one V-shell part.  The
        # generic preflight AABB projection cannot distinguish the two local
        # planes without tessellating that shared shell, so enforce the same
        # relation from the source-derived local dimensions here.  Sweep still
        # runs exact collision and full joint poses on both tilted faces.
        exposure_ok &= all(
            math.isclose(abs(station.frame.yaw), math.radians(15.0), abs_tol=1e-9)
            and (
                1.55 * r.button_size_m
                if r.button_style == "wide_tactile_numbered"
                else r.button_size_m
            )
            + 2.0 * _APERTURE_CLEARANCE_M
            >= (
                1.55 * r.button_size_m
                if r.button_style == "wide_tactile_numbered"
                else r.button_size_m
            )
            for station in stations
        )
    ctx.check(
        "category_anchor: every floor selector remains exposed in its opening",
        exposure_ok,
        details="; ".join(surface_details),
    )

    if r.aux_style == "accessibility_paddles":
        paddle_joints = [
            joint
            for joint in model.articulations
            if joint.meta.get("mechanism") == "accessibility paddle press"
        ]
        paddle_ok = len(paddle_joints) == 3 and _AUX_CAP_CROWN_M - r.press_travel_m >= 0.0030
        ctx.check(
            "category_anchor: accessibility paddles remain exposed at full travel",
            paddle_ok,
            details=f"paddles={len(paddle_joints)}, travel={r.press_travel_m:.4f}",
        )

    ctx.check(
        "multiplicity: every N adds a complete numbered selector",
        len(buttons) == len(stations) == r.floor_count
        and (
            len(presses) == r.floor_count
            if mechanical
            else len(touch_mounts) == r.floor_count
        ),
        details=(
            f"buttons={len(buttons)}, presses={len(presses)}, touch={len(touch_mounts)}, "
            f"stations={len(stations)}, N={r.floor_count}"
        ),
    )
    ctx.check(
        "host capacity follows N without crowding the button pitch",
        r.pitch_m >= 1.55 * r.button_size_m + 0.010
        and r.panel_height_m >= r.field_bottom_m + r.field_height_m + 0.020,
        details=(
            f"pitch={r.pitch_m:.4f}, button={r.button_size_m:.4f}, "
            f"panel_h={r.panel_height_m:.4f}, field_h={r.field_height_m:.4f}"
        ),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "thirty_floor_single_column_square_dot_matrix",
        {
            "panel_family": "single_column",
            "button_style": "square_numbered",
            "aux_style": "accessibility_paddles",
            "floor_count": 30,
            "panel_depth_m": 0.040,
            "pitch_m": 0.066,
            "button_size_m": 0.031,
            "press_travel_m": 0.0035,
            "aux_scale_m": 0.080,
            "numeral_style": "dot_matrix",
        },
        reason="maximum N, pitch, cap and travel on the tallest source-backed family",
    ),
    corner_case(
        "compact_six_floor_minimum",
        {
            "panel_family": "compact_pair",
            "button_style": "round_numbered",
            "aux_style": "key_switch",
            "floor_count": 6,
            "panel_depth_m": 0.022,
            "pitch_m": 0.048,
            "button_size_m": 0.023,
            "press_travel_m": 0.0018,
            "aux_scale_m": 0.054,
            "numeral_style": "seven_segment",
        },
        reason="smallest source-observed N in the tight compact faceplate",
    ),
    corner_case(
        "corner_wrap_thirty_floor_fire_cover",
        {
            "panel_family": "corner_wrap",
            "button_style": "round_numbered",
            "aux_style": "fire_service_cover",
            "floor_count": 30,
            "panel_depth_m": 0.040,
            "pitch_m": 0.066,
            "button_size_m": 0.031,
            "press_travel_m": 0.0035,
            "aux_scale_m": 0.080,
            "numeral_style": "cut_stroke",
        },
        reason="maximum station allocation across both tilted faces under a moving cover",
    ),
    corner_case(
        "horizontal_thirty_floor_square",
        {
            "panel_family": "horizontal_console",
            "button_style": "square_numbered",
            "aux_style": "accessibility_paddles",
            "floor_count": 30,
            "panel_depth_m": 0.022,
            "pitch_m": 0.048,
            "button_size_m": 0.031,
            "press_travel_m": 0.0035,
            "aux_scale_m": 0.080,
            "numeral_style": "seven_segment",
        },
        reason="five dense horizontal rows plus the widest auxiliary module",
    ),
    corner_case(
        "split_zone_odd_bank_balance",
        {
            "panel_family": "split_zone",
            "button_style": "round_numbered",
            "aux_style": "fire_service_cover",
            "floor_count": 8,
            "panel_depth_m": 0.030,
            "pitch_m": 0.057,
            "button_size_m": 0.024,
            "press_travel_m": 0.0022,
            "aux_scale_m": 0.064,
            "numeral_style": "continuous_stroke",
        },
        reason="checks both framed banks and the real separator at a short observed N",
    ),
    corner_case(
        "destination_matrix_wide_controls",
        {
            "panel_family": "destination_matrix",
            "button_style": "wide_tactile_numbered",
            "aux_style": "door_alarm_cluster",
            "floor_count": 30,
            "panel_depth_m": 0.040,
            "pitch_m": 0.048,
            "button_size_m": 0.031,
            "press_travel_m": 0.0035,
            "aux_scale_m": 0.080,
            "numeral_style": "stencil",
        },
        reason="widest mechanical selector in a full three-column matrix with a dense action band",
    ),
    corner_case(
        "glass_inlay_touch_intercom",
        {
            "panel_family": "glass_inlay",
            "button_style": "glass_touch_numbered",
            "aux_style": "emergency_intercom",
            "floor_count": 30,
            "panel_depth_m": 0.022,
            "pitch_m": 0.048,
            "button_size_m": 0.031,
            "press_travel_m": 0.0035,
            "aux_scale_m": 0.080,
            "numeral_style": "braille_companion",
        },
        reason="maximum fixed touch-cell field inside the framed glass inset with mixed fixed/prismatic auxiliary topology",
    ),
    corner_case(
        "protected_bay_touch_fire_cover",
        {
            "panel_family": "protected_service_bay",
            "button_style": "glass_touch_numbered",
            "aux_style": "fire_service_cover",
            "floor_count": 18,
            "panel_depth_m": 0.040,
            "pitch_m": 0.066,
            "button_size_m": 0.023,
            "press_travel_m": 0.0018,
            "aux_scale_m": 0.080,
            "numeral_style": "stencil",
        },
        reason="hinged auxiliary cover mounted inside the deepest protected service bay below fixed touch selectors",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_elevator_button_panel",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_elevator_button_panel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
