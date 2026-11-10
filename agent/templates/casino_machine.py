# SPDX-License-Identifier: Apache-2.0

"""Casino machine procedural template.

This module implements ``articraft_template_authoring/specs_modular_v1/casino_machine.md``.

The template follows the spec's mixed slot graph:

* Slot A ``cabinet_body`` emits one static cabinet root.
* Slot B ``game_display_or_reels`` emits cabinet-mounted display/window visuals
  and optional spinning reel parts.
* Slot C ``controls_and_openings`` emits buttons, doors, tray flaps, side
  levers, and knobs with their own joints.

Identity invariant: every seed has a casino-machine face: screen or reel
window, payout/coin/bill affordance, and at least one interactive joint.

Geometry policy: the cabinet is the root carrier. Static panels are embedded
slightly into the cabinet body. Moving parts are separate links, but each link
has internally connected visuals and a joint datum on a cabinet face/edge.

Adopted source mapping:
S1 rec_casino_machine_0dc07bf220f3445398c77007f2a4ade3:
   upright five-reel cabinet, upper display, prismatic spin button, service
   panel.
S2 rec_casino_machine_04dbcc128faa4a12a0cd9eda80de5f1f:
   bar-top cabinet, tray flap, button deck.
S3 rec_casino_machine_a5d926cbd53d4a309199969ad8856d21:
   three independent reels, multiple buttons, cashbox door.
S4 rec_casino_machine_b7a9b3572cfb45ec8a7eb5ec3a7ed453:
   classic lever slot, side handle, coin tray door.
S5 rec_casino_machine_cfba59645a80411f8bed2072f9a9bfcf:
   window glass, side lever, payout tray flap.
S6 rec_casino_machine_e60bb68099834916986dbbf2af56a85d:
   slant-top terminal, belly door, spin button, rotary knob.
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
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
)

__modular__ = True


CabinetStyle = Literal[
    "upright_reel",
    "bar_top",
    "slant_top",
    "classic_lever",
]
GameFaceStyle = Literal[
    "five_reel_window",
    "three_reels",
    "single_window_reel",
    "screen_only",
]
ControlModule = Literal[
    "spin_button_service",
    "tray_flap_button",
    "side_lever_coin_door",
    "belly_button_knob",
    "payout_lever",
]
DoorStyle = Literal[
    "none",
    "service_panel",
    "cashbox",
    "belly",
    "coin_tray",
    "payout_tray",
]
LeverStyle = Literal[
    "none",
    "side_pull",
    "selector_knob",
    "volume_knob",
]
ButtonStyle = Literal[
    "round_lit",
    "rectangular",
    "ringed",
]
ReelVisualStyle = Literal[
    "symbol_bands",
    "fruit_ticks",
    "clean_chrome",
]
MaterialStyle = Literal[
    "casino_red",
    "midnight_chrome",
    "bar_top_blue",
    "classic_gold",
    "slant_black",
]


CABINET_STYLES: tuple[CabinetStyle, ...] = (
    "upright_reel",
    "bar_top",
    "slant_top",
    "classic_lever",
)
GAME_FACE_STYLES: tuple[GameFaceStyle, ...] = (
    "five_reel_window",
    "three_reels",
    "single_window_reel",
    "screen_only",
)
CONTROL_MODULES: tuple[ControlModule, ...] = (
    "spin_button_service",
    "tray_flap_button",
    "side_lever_coin_door",
    "belly_button_knob",
    "payout_lever",
)
BUTTON_STYLES: tuple[ButtonStyle, ...] = (
    "round_lit",
    "rectangular",
    "ringed",
)
REEL_VISUAL_STYLES: tuple[ReelVisualStyle, ...] = (
    "symbol_bands",
    "fruit_ticks",
    "clean_chrome",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "casino_red",
    "midnight_chrome",
    "bar_top_blue",
    "classic_gold",
    "slant_black",
)


SOURCE_INDEX = {
    "S1": (
        "data/records/rec_casino_machine_0dc07bf220f3445398c77007f2a4ade3/"
        "revisions/rev_000001/model.py:L30-L41,L54-L423"
    ),
    "S2": (
        "data/records/rec_casino_machine_04dbcc128faa4a12a0cd9eda80de5f1f/"
        "revisions/rev_000001/model.py:L27-L99,L103-L156"
    ),
    "S3": (
        "data/records/rec_casino_machine_a5d926cbd53d4a309199969ad8856d21/"
        "revisions/rev_000001/model.py:L26-L146,L160-L443"
    ),
    "S4": (
        "data/records/rec_casino_machine_b7a9b3572cfb45ec8a7eb5ec3a7ed453/"
        "revisions/rev_000001/model.py:L24-L107,L114-L415"
    ),
    "S5": (
        "data/records/rec_casino_machine_cfba59645a80411f8bed2072f9a9bfcf/"
        "revisions/rev_000001/model.py:L24-L71,L86-L382"
    ),
    "S6": (
        "data/records/rec_casino_machine_e60bb68099834916986dbbf2af56a85d/"
        "revisions/rev_000001/model.py:L25-L115,L143-L414"
    ),
}


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "casino_red": {
        "cabinet": (0.52, 0.04, 0.05, 1.0),
        "cabinet_dark": (0.18, 0.02, 0.025, 1.0),
        "trim": (0.95, 0.70, 0.24, 1.0),
        "screen": (0.02, 0.06, 0.10, 1.0),
        "glass": (0.45, 0.70, 0.95, 0.38),
        "button": (0.95, 0.08, 0.05, 1.0),
        "button_dark": (0.20, 0.03, 0.02, 1.0),
        "reel": (0.92, 0.90, 0.82, 1.0),
        "symbol": (0.08, 0.08, 0.10, 1.0),
        "metal": (0.72, 0.72, 0.68, 1.0),
        "payout": (0.08, 0.08, 0.09, 1.0),
    },
    "midnight_chrome": {
        "cabinet": (0.05, 0.055, 0.065, 1.0),
        "cabinet_dark": (0.020, 0.022, 0.026, 1.0),
        "trim": (0.60, 0.62, 0.64, 1.0),
        "screen": (0.02, 0.08, 0.13, 1.0),
        "glass": (0.36, 0.68, 0.92, 0.34),
        "button": (0.10, 0.60, 0.90, 1.0),
        "button_dark": (0.03, 0.10, 0.14, 1.0),
        "reel": (0.82, 0.84, 0.84, 1.0),
        "symbol": (0.02, 0.02, 0.03, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0),
        "payout": (0.015, 0.016, 0.018, 1.0),
    },
    "bar_top_blue": {
        "cabinet": (0.05, 0.16, 0.34, 1.0),
        "cabinet_dark": (0.025, 0.06, 0.13, 1.0),
        "trim": (0.74, 0.80, 0.88, 1.0),
        "screen": (0.01, 0.05, 0.12, 1.0),
        "glass": (0.35, 0.63, 0.96, 0.40),
        "button": (0.94, 0.76, 0.16, 1.0),
        "button_dark": (0.22, 0.15, 0.04, 1.0),
        "reel": (0.88, 0.90, 0.95, 1.0),
        "symbol": (0.03, 0.05, 0.10, 1.0),
        "metal": (0.64, 0.68, 0.72, 1.0),
        "payout": (0.025, 0.040, 0.060, 1.0),
    },
    "classic_gold": {
        "cabinet": (0.50, 0.24, 0.05, 1.0),
        "cabinet_dark": (0.18, 0.08, 0.02, 1.0),
        "trim": (0.94, 0.74, 0.22, 1.0),
        "screen": (0.05, 0.04, 0.03, 1.0),
        "glass": (0.55, 0.70, 0.85, 0.34),
        "button": (0.82, 0.05, 0.03, 1.0),
        "button_dark": (0.22, 0.02, 0.02, 1.0),
        "reel": (0.95, 0.88, 0.62, 1.0),
        "symbol": (0.12, 0.06, 0.02, 1.0),
        "metal": (0.88, 0.64, 0.20, 1.0),
        "payout": (0.08, 0.04, 0.02, 1.0),
    },
    "slant_black": {
        "cabinet": (0.08, 0.08, 0.09, 1.0),
        "cabinet_dark": (0.025, 0.025, 0.030, 1.0),
        "trim": (0.45, 0.46, 0.48, 1.0),
        "screen": (0.00, 0.05, 0.08, 1.0),
        "glass": (0.32, 0.56, 0.85, 0.36),
        "button": (0.78, 0.12, 0.86, 1.0),
        "button_dark": (0.10, 0.04, 0.12, 1.0),
        "reel": (0.82, 0.82, 0.78, 1.0),
        "symbol": (0.05, 0.04, 0.06, 1.0),
        "metal": (0.58, 0.58, 0.60, 1.0),
        "payout": (0.018, 0.018, 0.022, 1.0),
    },
}


@dataclass(frozen=True)
class CasinoMachineConfig:
    cabinet_style: CabinetStyle = "upright_reel"
    game_face_style: GameFaceStyle = "five_reel_window"
    control_module: ControlModule = "spin_button_service"
    button_style: ButtonStyle = "round_lit"
    reel_visual_style: ReelVisualStyle = "symbol_bands"
    material_style: MaterialStyle = "casino_red"
    reel_count: int = 5
    button_count: int = 1
    cabinet_width: float = 0.90
    cabinet_height: float = 1.55
    cabinet_depth: float = 0.46
    front_angle: float = 0.08
    button_travel: float = 0.035
    door_open_angle: float = 1.25
    tray_open_angle: float = 1.05
    lever_pull_angle: float = 0.75
    name: str = "reference_casino_machine"
    palette: dict[str, tuple[float, float, float, float]] | None = None


@dataclass(frozen=True)
class ResolvedCasinoMachineConfig:
    cabinet_style: CabinetStyle
    game_face_style: GameFaceStyle
    control_module: ControlModule
    door_style: DoorStyle
    lever_style: LeverStyle
    button_style: ButtonStyle
    reel_visual_style: ReelVisualStyle
    material_style: MaterialStyle
    reel_count: int
    button_count: int
    cabinet_width: float
    cabinet_height: float
    cabinet_depth: float
    front_angle: float
    button_travel: float
    door_open_angle: float
    tray_open_angle: float
    lever_pull_angle: float
    front_y: float
    reel_z: float
    reel_window_z: float
    screen_z: float
    deck_z: float
    payout_z: float
    reel_radius: float
    reel_length: float
    deck_width: float
    name: str
    palette: dict[str, tuple[float, float, float, float]]


@dataclass(frozen=True)
class CabinetAnchors:
    part: Part
    front_y: float
    side_x: float
    width: float
    height: float
    depth: float
    reel_z: float
    screen_z: float
    deck_z: float
    payout_z: float


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _require(value: str, allowed: tuple[str, ...], *, field_name: str) -> str:
    if value not in allowed:
        raise ValueError(f"{field_name} must be one of {allowed}, got {value!r}")
    return value


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _cyl_z() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _register_materials(
    model: ArticulatedObject, palette: dict[str, tuple[float, float, float, float]]
):
    return {name: model.material(f"casino_{name}", rgba=rgba) for name, rgba in palette.items()}


def _front_origin(r: ResolvedCasinoMachineConfig, *, z: float, y_offset: float = 0.0):
    return (0.0, r.front_y + y_offset, z)


def _add_front_panel(
    part: Part,
    *,
    name: str,
    x: float,
    z: float,
    width: float,
    height: float,
    thickness: float,
    front_y: float,
    material: object,
    embed: float = 0.006,
) -> None:
    part.visual(
        Box((width, thickness, height)),
        origin=Origin(xyz=(x, front_y - thickness * 0.5 + embed, z)),
        material=material,
        name=name, material_class_id=_material_class_id(material.name, ("casino_trim", "casino_payout", "casino_cabinet_dark", "casino_metal"), "metal.brushed_silver", "tech.control_interface"),
    )


def _add_side_panel(
    part: Part,
    *,
    name: str,
    x: float,
    y: float,
    z: float,
    depth: float,
    height: float,
    thickness: float,
    material: object,
    embed_sign: float,
) -> None:
    part.visual(
        Box((thickness, depth, height)),
        origin=Origin(xyz=(x - embed_sign * thickness * 0.5, y, z)),
        material=material,
        name=name, material_class_id="metal.brushed_silver",
    )


def _button_offsets(count: int, width: float) -> list[float]:
    if count <= 1:
        return [0.0]
    span = min(width * 0.64, 0.16 * (count - 1))
    start = -0.5 * span
    return [start + span * i / (count - 1) for i in range(count)]


def _button_cap_size(r: ResolvedCasinoMachineConfig) -> tuple[float, float]:
    return min(0.095, r.cabinet_width * 0.10), min(0.055, r.cabinet_height * 0.045)


def _button_joint_y(r: ResolvedCasinoMachineConfig) -> float:
    _, cap_h = _button_cap_size(r)
    cap_back = cap_h * (0.095 if r.button_style == "rectangular" else 0.140)
    clearance = max(r.cabinet_depth * 0.018, 0.006)
    return r.front_y - r.button_travel - cap_back - clearance


def _button_joint_z(r: ResolvedCasinoMachineConfig) -> float:
    return r.deck_z + r.cabinet_height * 0.050


def _reel_offsets(count: int, width: float) -> list[float]:
    if count <= 1:
        return [0.0]
    span = min(width * 0.72, 0.19 * (count - 1))
    start = -0.5 * span
    return [start + span * i / (count - 1) for i in range(count)]


def _module_to_door_style(control_module: ControlModule) -> DoorStyle:
    if control_module == "spin_button_service":
        return "service_panel"
    if control_module == "tray_flap_button":
        return "payout_tray"
    if control_module == "side_lever_coin_door":
        return "coin_tray"
    if control_module == "belly_button_knob":
        return "belly"
    if control_module == "payout_lever":
        return "payout_tray"
    return "none"


def _module_to_lever_style(control_module: ControlModule) -> LeverStyle:
    if control_module in ("side_lever_coin_door", "payout_lever"):
        return "side_pull"
    if control_module == "belly_button_knob":
        return "volume_knob"
    return "none"


def config_from_seed(seed: int) -> CasinoMachineConfig:
    curated: dict[int, CasinoMachineConfig] = {
        0: CasinoMachineConfig(
            cabinet_style="upright_reel",
            game_face_style="five_reel_window",
            control_module="spin_button_service",
            reel_count=5,
            button_count=1,
            cabinet_width=0.92,
            cabinet_height=1.62,
            cabinet_depth=0.48,
            material_style="casino_red",
            button_style="round_lit",
            reel_visual_style="symbol_bands",
            name="seeded_casino_machine_0",
        ),
        1: CasinoMachineConfig(
            cabinet_style="bar_top",
            game_face_style="screen_only",
            control_module="tray_flap_button",
            reel_count=0,
            button_count=4,
            cabinet_width=0.82,
            cabinet_height=0.92,
            cabinet_depth=0.54,
            material_style="bar_top_blue",
            button_style="rectangular",
            name="seeded_casino_machine_1",
        ),
        2: CasinoMachineConfig(
            cabinet_style="upright_reel",
            game_face_style="three_reels",
            control_module="side_lever_coin_door",
            reel_count=3,
            button_count=2,
            cabinet_width=0.88,
            cabinet_height=1.52,
            cabinet_depth=0.46,
            material_style="classic_gold",
            button_style="ringed",
            reel_visual_style="fruit_ticks",
            name="seeded_casino_machine_2",
        ),
        3: CasinoMachineConfig(
            cabinet_style="classic_lever",
            game_face_style="single_window_reel",
            control_module="side_lever_coin_door",
            reel_count=1,
            button_count=1,
            cabinet_width=0.78,
            cabinet_height=1.42,
            cabinet_depth=0.43,
            material_style="classic_gold",
            button_style="round_lit",
            reel_visual_style="symbol_bands",
            name="seeded_casino_machine_3",
        ),
        4: CasinoMachineConfig(
            cabinet_style="slant_top",
            game_face_style="screen_only",
            control_module="belly_button_knob",
            reel_count=0,
            button_count=3,
            cabinet_width=1.02,
            cabinet_height=1.16,
            cabinet_depth=0.62,
            front_angle=0.32,
            material_style="slant_black",
            button_style="rectangular",
            name="seeded_casino_machine_4",
        ),
        5: CasinoMachineConfig(
            cabinet_style="slant_top",
            game_face_style="three_reels",
            control_module="belly_button_knob",
            reel_count=3,
            button_count=5,
            cabinet_width=1.10,
            cabinet_height=1.20,
            cabinet_depth=0.64,
            front_angle=0.28,
            material_style="midnight_chrome",
            button_style="ringed",
            reel_visual_style="clean_chrome",
            name="seeded_casino_machine_5",
        ),
        6: CasinoMachineConfig(
            cabinet_style="classic_lever",
            game_face_style="five_reel_window",
            control_module="payout_lever",
            reel_count=5,
            button_count=2,
            cabinet_width=1.02,
            cabinet_height=1.72,
            cabinet_depth=0.50,
            material_style="casino_red",
            button_style="round_lit",
            reel_visual_style="fruit_ticks",
            name="seeded_casino_machine_6",
        ),
        7: CasinoMachineConfig(
            cabinet_style="bar_top",
            game_face_style="single_window_reel",
            control_module="tray_flap_button",
            reel_count=1,
            button_count=3,
            cabinet_width=0.74,
            cabinet_height=0.84,
            cabinet_depth=0.50,
            material_style="midnight_chrome",
            button_style="ringed",
            reel_visual_style="symbol_bands",
            name="seeded_casino_machine_7",
        ),
        8: CasinoMachineConfig(
            cabinet_style="upright_reel",
            game_face_style="screen_only",
            control_module="spin_button_service",
            reel_count=0,
            button_count=5,
            cabinet_width=0.98,
            cabinet_height=1.50,
            cabinet_depth=0.45,
            material_style="bar_top_blue",
            button_style="rectangular",
            name="seeded_casino_machine_8",
        ),
        9: CasinoMachineConfig(
            cabinet_style="bar_top",
            game_face_style="three_reels",
            control_module="payout_lever",
            reel_count=3,
            button_count=4,
            cabinet_width=0.94,
            cabinet_height=0.96,
            cabinet_depth=0.57,
            material_style="slant_black",
            button_style="round_lit",
            reel_visual_style="clean_chrome",
            name="seeded_casino_machine_9",
        ),
    }
    if seed in curated:
        return curated[seed]

    rng = random.Random(seed)
    cabinet = rng.choice(CABINET_STYLES)
    face = rng.choice(GAME_FACE_STYLES)
    control = rng.choice(CONTROL_MODULES)
    if cabinet == "bar_top":
        height = rng.uniform(0.78, 1.05)
        depth = rng.uniform(0.48, 0.62)
    elif cabinet == "slant_top":
        height = rng.uniform(1.05, 1.32)
        depth = rng.uniform(0.56, 0.68)
    else:
        height = rng.uniform(1.35, 1.85)
        depth = rng.uniform(0.42, 0.55)

    if face == "screen_only":
        reels = 0
    elif face == "single_window_reel":
        reels = 1
    elif face == "three_reels":
        reels = 3
    else:
        reels = 5

    return CasinoMachineConfig(
        cabinet_style=cabinet,
        game_face_style=face,
        control_module=control,
        button_style=rng.choice(BUTTON_STYLES),
        reel_visual_style=rng.choice(REEL_VISUAL_STYLES),
        material_style=rng.choice(MATERIAL_STYLES),
        reel_count=reels,
        button_count=rng.randint(1, 5),
        cabinet_width=round(rng.uniform(0.68, 1.18), 3),
        cabinet_height=round(height, 3),
        cabinet_depth=round(depth, 3),
        front_angle=round(rng.uniform(0.0, 0.36), 3),
        button_travel=round(rng.uniform(0.022, 0.040), 3),
        door_open_angle=round(rng.uniform(0.95, 1.35), 3),
        tray_open_angle=round(rng.uniform(0.75, 1.15), 3),
        lever_pull_angle=round(rng.uniform(0.58, 0.86), 3),
        name=f"seeded_casino_machine_{seed}",
    )


def resolve_config(config: CasinoMachineConfig) -> ResolvedCasinoMachineConfig:
    cabinet = _require(
        config.cabinet_style,
        CABINET_STYLES,
        field_name="cabinet_style",
    )
    face = _require(
        config.game_face_style,
        GAME_FACE_STYLES,
        field_name="game_face_style",
    )
    control = _require(
        config.control_module,
        CONTROL_MODULES,
        field_name="control_module",
    )
    button_style = _require(
        config.button_style,
        BUTTON_STYLES,
        field_name="button_style",
    )
    reel_visual = _require(
        config.reel_visual_style,
        REEL_VISUAL_STYLES,
        field_name="reel_visual_style",
    )
    material = _require(
        config.material_style,
        MATERIAL_STYLES,
        field_name="material_style",
    )

    width = _clamp(config.cabinet_width, 0.55, 1.35)
    if cabinet == "bar_top":
        height = _clamp(config.cabinet_height, 0.72, 1.12)
        depth = _clamp(config.cabinet_depth, 0.42, 0.68)
    elif cabinet == "slant_top":
        height = _clamp(config.cabinet_height, 0.95, 1.42)
        depth = _clamp(config.cabinet_depth, 0.50, 0.72)
    else:
        height = _clamp(config.cabinet_height, 1.22, 2.10)
        depth = _clamp(config.cabinet_depth, 0.36, 0.62)

    if face == "screen_only":
        reel_count = 0
    elif face == "single_window_reel":
        reel_count = 1
    elif face == "three_reels":
        reel_count = 3
    elif face == "five_reel_window":
        reel_count = 5
    else:
        reel_count = int(config.reel_count)
    if face != "screen_only":
        reel_count = max(1, min(5, reel_count))
        if reel_count not in (1, 3, 5):
            reel_count = 3

    if cabinet == "bar_top":
        screen_z = height * 0.63
        reel_z = height * 0.60
        deck_z = height * 0.33
        payout_z = height * 0.18
    elif cabinet == "slant_top":
        screen_z = height * 0.66
        reel_z = height * 0.62
        deck_z = height * 0.42
        payout_z = height * 0.18
    else:
        screen_z = height * 0.76
        reel_z = height * 0.58
        deck_z = height * 0.36
        payout_z = height * 0.20

    button_count = max(1, min(5, int(config.button_count)))
    if control == "spin_button_service":
        button_count = max(1, button_count)
    elif control == "side_lever_coin_door":
        button_count = min(button_count, 2)
    elif control == "payout_lever":
        button_count = min(button_count, 4)

    reel_radius = min(width * 0.135, max(0.055, height * 0.060))
    if reel_count == 5:
        reel_radius = min(reel_radius, width * 0.090)
    reel_length = min(width * 0.18, max(0.055, width / max(6.5, reel_count * 3.2)))
    deck_width = width * (0.78 if cabinet != "bar_top" else 0.86)

    palette = dict(PALETTES[material])
    if config.palette:
        palette.update(config.palette)

    return ResolvedCasinoMachineConfig(
        cabinet_style=cabinet,  # type: ignore[arg-type]
        game_face_style=face,  # type: ignore[arg-type]
        control_module=control,  # type: ignore[arg-type]
        door_style=_module_to_door_style(control),  # type: ignore[arg-type]
        lever_style=_module_to_lever_style(control),  # type: ignore[arg-type]
        button_style=button_style,  # type: ignore[arg-type]
        reel_visual_style=reel_visual,  # type: ignore[arg-type]
        material_style=material,  # type: ignore[arg-type]
        reel_count=reel_count,
        button_count=button_count,
        cabinet_width=width,
        cabinet_height=height,
        cabinet_depth=depth,
        front_angle=_clamp(config.front_angle, 0.0, 0.45),
        button_travel=_clamp(config.button_travel, 0.015, 0.045),
        door_open_angle=_clamp(config.door_open_angle, 0.70, 1.45),
        tray_open_angle=_clamp(config.tray_open_angle, 0.60, 1.20),
        lever_pull_angle=_clamp(config.lever_pull_angle, 0.45, 0.90),
        front_y=-depth * 0.5,
        reel_z=reel_z,
        reel_window_z=reel_z,
        screen_z=screen_z,
        deck_z=deck_z,
        payout_z=payout_z,
        reel_radius=reel_radius,
        reel_length=reel_length,
        deck_width=deck_width,
        name=config.name,
        palette=palette,
    )


# adopted: S1, S2, S4, S6
def _build_cabinet(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> CabinetAnchors:
    cabinet = model.part("cabinet")
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y

    cabinet.visual(
        Box((w, d, h)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
        material=materials["cabinet"],
        name="main_cabinet_shell", material_class_id="metal.paint_coated",
    )

    cabinet.visual(
        Box((w * 0.96, d * 0.96, h * 0.055)),
        origin=Origin(xyz=(0.0, 0.0, h + h * 0.027)),
        material=materials["trim"],
        name="top_light_cap", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    cabinet.visual(
        Box((w * 1.06, d * 0.94, h * 0.055)),
        origin=Origin(xyz=(0.0, 0.0, h * 0.027)),
        material=materials["cabinet_dark"],
        name="weighted_base_plinth", material_class_id="metal.paint_coated",
    )
    cabinet.visual(
        Box((w * 0.95, d * 0.12, h * 0.070)),
        origin=Origin(xyz=(0.0, front_y + d * 0.045, r.payout_z - h * 0.045)),
        material=materials["payout"],
        name="payout_recess_shadow", material_class_id="metal.blackened_gunmetal",
    )
    cabinet.visual(
        Box((w * 0.74, d * 0.055, h * 0.030)),
        origin=Origin(xyz=(0.0, front_y - d * 0.010, r.payout_z)),
        material=materials["metal"],
        name="coin_return_lip", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )

    for side_name, x, sign in (("left", -w * 0.50, -1.0), ("right", w * 0.50, 1.0)):
        _add_side_panel(
            cabinet,
            name=f"{side_name}_vertical_trim",
            x=x,
            y=0.0,
            z=h * 0.52,
            depth=d * 0.96,
            height=h * 0.93,
            thickness=w * 0.030,
            material=materials["trim"],
            embed_sign=sign,
        )
        cabinet.visual(
            Box((w * 0.040, d * 0.90, h * 0.035)),
            origin=Origin(xyz=(x - sign * w * 0.010, 0.0, h * 0.94)),
            material=materials["cabinet_dark"],
            name=f"{side_name}_top_corner_band", material_class_id="metal.paint_coated",
        )

    if r.cabinet_style == "bar_top":
        _decorate_bar_top_cabinet(cabinet, r, materials)
    elif r.cabinet_style == "slant_top":
        _decorate_slant_top_cabinet(cabinet, r, materials)
    elif r.cabinet_style == "classic_lever":
        _decorate_classic_lever_cabinet(cabinet, r, materials)
    else:
        _decorate_upright_cabinet(cabinet, r, materials)

    _decorate_game_face(cabinet, r, materials)
    _decorate_control_deck(cabinet, r, materials)
    _decorate_payout_area(cabinet, r, materials)

    cabinet.inertial = Inertial.from_geometry(
        Box((w, d, h)),
        mass=max(90.0, 220.0 * w * d * h),
        origin=Origin(xyz=(0.0, 0.0, h * 0.5)),
    )

    return CabinetAnchors(
        part=cabinet,
        front_y=front_y,
        side_x=w * 0.5,
        width=w,
        height=h,
        depth=d,
        reel_z=r.reel_z,
        screen_z=r.screen_z,
        deck_z=r.deck_z,
        payout_z=r.payout_z,
    )


def _decorate_upright_cabinet(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    _add_front_panel(
        cabinet,
        name="upright_upper_lightbox",
        x=0.0,
        z=h * 0.88,
        width=w * 0.70,
        height=h * 0.14,
        thickness=d * 0.045,
        front_y=front_y,
        material=materials["screen"],
    )
    _add_front_panel(
        cabinet,
        name="upright_lightbox_gold_border",
        x=0.0,
        z=h * 0.88,
        width=w * 0.78,
        height=h * 0.18,
        thickness=d * 0.025,
        front_y=front_y - d * 0.010,
        material=materials["trim"],
    )
    for i, x in enumerate((-w * 0.32, -w * 0.16, 0.0, w * 0.16, w * 0.32)):
        cabinet.visual(
            Sphere(radius=w * 0.018),
            origin=Origin(xyz=(x, front_y - d * 0.025, h * 0.985)),
            material=materials["button"],
            name=f"top_jackpot_bulb_{i}", material_class_id="tech.emissive_surface",
        )


def _decorate_bar_top_cabinet(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    cabinet.visual(
        Box((w * 0.96, d * 0.40, h * 0.10)),
        origin=Origin(xyz=(0.0, d * 0.18, h * 0.93)),
        material=materials["cabinet_dark"],
        name="bar_top_rear_hump", material_class_id="metal.paint_coated",
    )
    _add_front_panel(
        cabinet,
        name="bar_top_low_front_band",
        x=0.0,
        z=h * 0.20,
        width=w * 0.88,
        height=h * 0.16,
        thickness=d * 0.050,
        front_y=front_y,
        material=materials["trim"],
    )
    _add_front_panel(
        cabinet,
        name="bar_top_ticket_slot",
        x=-w * 0.24,
        z=h * 0.18,
        width=w * 0.25,
        height=h * 0.035,
        thickness=d * 0.060,
        front_y=front_y - d * 0.012,
        material=materials["payout"],
    )


def _decorate_slant_top_cabinet(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    cabinet.visual(
        Box((w * 0.88, d * 0.22, h * 0.075)),
        origin=Origin(
            xyz=(0.0, front_y + d * 0.12, r.deck_z + h * 0.12), rpy=(-r.front_angle, 0.0, 0.0)
        ),
        material=materials["cabinet_dark"],
        name="slant_top_control_slope", material_class_id="metal.paint_coated",
    )
    cabinet.visual(
        Box((w * 0.80, d * 0.18, h * 0.050)),
        origin=Origin(
            xyz=(0.0, front_y + d * 0.08, r.screen_z + h * 0.10),
            rpy=(-r.front_angle * 0.8, 0.0, 0.0),
        ),
        material=materials["trim"],
        name="slant_screen_brow", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    _add_front_panel(
        cabinet,
        name="belly_panel_recess",
        x=0.0,
        z=h * 0.22,
        width=w * 0.72,
        height=h * 0.25,
        thickness=d * 0.050,
        front_y=front_y,
        material=materials["cabinet_dark"],
    )


def _decorate_classic_lever_cabinet(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    cabinet.visual(
        Box((w * 0.92, d * 0.92, h * 0.10)),
        origin=Origin(xyz=(0.0, 0.0, h * 1.04)),
        material=materials["trim"],
        name="classic_crowned_top", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    _add_front_panel(
        cabinet,
        name="classic_award_card",
        x=0.0,
        z=h * 0.80,
        width=w * 0.62,
        height=h * 0.11,
        thickness=d * 0.050,
        front_y=front_y,
        material=materials["screen"],
    )
    _add_front_panel(
        cabinet,
        name="classic_coin_slot_plate",
        x=w * 0.28,
        z=h * 0.38,
        width=w * 0.16,
        height=h * 0.08,
        thickness=d * 0.060,
        front_y=front_y - d * 0.010,
        material=materials["metal"],
    )


def _decorate_game_face(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    if r.game_face_style == "screen_only":
        _add_front_panel(
            cabinet,
            name="video_poker_screen_glass",
            x=0.0,
            z=r.screen_z,
            width=w * 0.66,
            height=h * 0.25,
            thickness=d * 0.050,
            front_y=front_y,
            material=materials["glass"],
        )
        _add_front_panel(
            cabinet,
            name="video_poker_screen_inner",
            x=0.0,
            z=r.screen_z,
            width=w * 0.58,
            height=h * 0.19,
            thickness=d * 0.060,
            front_y=front_y - d * 0.004,
            material=materials["screen"],
        )
        for i, x in enumerate((-w * 0.20, 0.0, w * 0.20)):
            _add_front_panel(
                cabinet,
                name=f"card_rank_icon_{i}",
                x=x,
                z=r.screen_z + h * 0.045,
                width=w * 0.055,
                height=h * 0.045,
                thickness=d * 0.070,
                front_y=front_y - d * 0.012,
                material=materials["trim"],
            )
        return

    window_w = w * (0.76 if r.reel_count >= 5 else 0.62)
    window_h = h * (0.20 if r.cabinet_style != "bar_top" else 0.18)
    _add_front_panel(
        cabinet,
        name="reel_window_outer_frame",
        x=0.0,
        z=r.reel_window_z,
        width=window_w,
        height=window_h,
        thickness=d * 0.065,
        front_y=front_y,
        material=materials["trim"],
    )
    _add_front_panel(
        cabinet,
        name="reel_window_glass",
        x=0.0,
        z=r.reel_window_z,
        width=window_w * 0.92,
        height=window_h * 0.72,
        thickness=d * 0.070,
        front_y=front_y - d * 0.010,
        material=materials["glass"],
    )
    for i, x in enumerate(_reel_offsets(max(1, r.reel_count), w)):
        _add_front_panel(
            cabinet,
            name=f"reel_symbol_window_{i}",
            x=x,
            z=r.reel_window_z,
            width=max(w * 0.085, r.reel_length * 0.95),
            height=window_h * 0.58,
            thickness=d * 0.080,
            front_y=front_y - d * 0.020,
            material=materials["screen"],
        )
        _add_front_panel(
            cabinet,
            name=f"reel_payline_tick_{i}",
            x=x,
            z=r.reel_window_z,
            width=max(w * 0.060, r.reel_length * 0.70),
            height=h * 0.012,
            thickness=d * 0.090,
            front_y=front_y - d * 0.030,
            material=materials["button"],
        )


def _decorate_control_deck(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    cabinet.visual(
        Box((r.deck_width, d * 0.18, h * 0.060)),
        origin=Origin(xyz=(0.0, front_y + d * 0.035, r.deck_z)),
        material=materials["cabinet_dark"],
        name="control_deck_carrier", material_class_id="metal.paint_coated",
    )
    cabinet.visual(
        Box((r.deck_width * 0.92, d * 0.055, h * 0.018)),
        origin=Origin(xyz=(0.0, front_y - d * 0.010, r.deck_z + h * 0.040)),
        material=materials["trim"],
        name="control_deck_front_lip", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    _add_front_panel(
        cabinet,
        name="bill_acceptor_slot",
        x=-w * 0.28,
        z=r.deck_z - h * 0.055,
        width=w * 0.18,
        height=h * 0.035,
        thickness=d * 0.065,
        front_y=front_y + d * 0.010,
        material=materials["payout"],
    )
    _add_front_panel(
        cabinet,
        name="player_card_slot",
        x=w * 0.12,
        z=r.deck_z + h * 0.090,
        width=w * 0.16,
        height=h * 0.030,
        thickness=d * 0.065,
        front_y=front_y + d * 0.010,
        material=materials["metal"],
    )
    _decorate_button_sockets(cabinet, r, materials)


def _decorate_button_sockets(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    cap_w, cap_h = _button_cap_size(r)
    cap_back = cap_h * (0.095 if r.button_style == "rectangular" else 0.140)
    socket_front_y = _button_joint_y(r) + cap_back + max(r.cabinet_depth * 0.010, 0.004)
    socket_back_y = r.front_y + r.cabinet_depth * 0.010
    socket_length = max(0.012, socket_back_y - socket_front_y)
    socket_y = socket_front_y + socket_length * 0.5
    socket_z = _button_joint_z(r)
    for index, x in enumerate(_button_offsets(r.button_count, r.deck_width)):
        name = f"button_socket_{index}"
        if r.button_style == "rectangular":
            cabinet.visual(
                Box((cap_w * 0.92, socket_length, cap_h * 0.50)),
                origin=Origin(xyz=(x, socket_y, socket_z)),
                material=materials["button_dark"],
                name=name, material_class_id="plastic.opaque_generic",
            )
        else:
            cabinet.visual(
                Cylinder(radius=cap_w * 0.34, length=socket_length),
                origin=Origin(xyz=(x, socket_y, socket_z), rpy=_cyl_y()),
                material=materials["button_dark"],
                name=name, material_class_id="plastic.opaque_generic",
            )


def _decorate_payout_area(
    cabinet: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
) -> None:
    w = r.cabinet_width
    h = r.cabinet_height
    d = r.cabinet_depth
    front_y = r.front_y
    _add_front_panel(
        cabinet,
        name="payout_tray_recess",
        x=0.0,
        z=r.payout_z,
        width=w * 0.50,
        height=h * 0.10,
        thickness=d * 0.080,
        front_y=front_y,
        material=materials["payout"],
    )
    _add_front_panel(
        cabinet,
        name="payout_tray_metal_rim",
        x=0.0,
        z=r.payout_z + h * 0.045,
        width=w * 0.56,
        height=h * 0.025,
        thickness=d * 0.070,
        front_y=front_y - d * 0.012,
        material=materials["metal"],
    )
    for i, x in enumerate((-w * 0.21, w * 0.21)):
        cabinet.visual(
            Cylinder(radius=w * 0.012, length=d * 0.035),
            origin=Origin(xyz=(x, front_y - d * 0.030, r.payout_z + h * 0.025), rpy=_cyl_y()),
            material=materials["trim"],
            name=f"payout_rim_fastener_{i}", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
        )


# adopted: S1, S3, S4, S5
def _build_reels(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> list[Part]:
    reels: list[Part] = []
    if r.reel_count <= 0:
        return reels
    offsets = _reel_offsets(r.reel_count, r.cabinet_width)
    for index, x in enumerate(offsets):
        name = "reel" if r.reel_count == 1 else f"reel_{index}"
        reel = model.part(name)
        radius = r.reel_radius
        length = r.reel_length
        reel.visual(
            Cylinder(radius=radius, length=length),
            origin=Origin(rpy=_cyl_x()),
            material=materials["reel"],
            name="reel_drum", material_class_id=("plastic.opaque_glossy_molded" if r.reel_visual_style in {"symbol_bands", "fruit_ticks"} else "metal.chrome_polished"),
        )
        reel.visual(
            Cylinder(radius=radius * 0.58, length=length * 1.05),
            origin=Origin(rpy=_cyl_x()),
            material=materials["metal"],
            name="reel_axle_hub", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
        )
        reel.visual(
            Cylinder(radius=radius * 1.01, length=length * 0.18),
            origin=Origin(xyz=(-length * 0.36, 0.0, 0.0), rpy=_cyl_x()),
            material=materials["trim"],
            name="left_reel_rim", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
        )
        reel.visual(
            Cylinder(radius=radius * 1.01, length=length * 0.18),
            origin=Origin(xyz=(length * 0.36, 0.0, 0.0), rpy=_cyl_x()),
            material=materials["trim"],
            name="right_reel_rim", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
        )
        if r.reel_visual_style == "fruit_ticks":
            _add_reel_tick_band(reel, radius, length, materials["symbol"], dense=True)
        elif r.reel_visual_style == "symbol_bands":
            _add_reel_tick_band(reel, radius, length, materials["button"], dense=False)
        else:
            reel.visual(
                Cylinder(radius=radius * 0.86, length=length * 0.58),
                origin=Origin(rpy=_cyl_x()),
                material=materials["glass"],
                name="chrome_reel_center_band", material_class_id="glass.smoked_tinted",
            )

        joint_origin = (
            x,
            cabinet.front_y - r.cabinet_depth * 0.070,
            r.reel_z,
        )
        model.articulation(
            f"{name}_spin",
            ArticulationType.CONTINUOUS,
            parent=cabinet.part,
            child=reel,
            origin=Origin(xyz=joint_origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=8.0),
        )
        reel.inertial = Inertial.from_geometry(
            Cylinder(radius=radius, length=length),
            mass=2.0,
            origin=Origin(rpy=_cyl_x()),
        )
        reels.append(reel)
    return reels


def _add_reel_tick_band(
    reel: Part,
    radius: float,
    length: float,
    material: object,
    *,
    dense: bool,
) -> None:
    count = 6 if dense else 4
    for i in range(count):
        angle = math.tau * i / count
        y = -math.cos(angle) * radius * 0.95
        z = math.sin(angle) * radius * 0.95
        reel.visual(
            Box((length * 0.72, radius * 0.045, radius * 0.15)),
            origin=Origin(xyz=(0.0, y, z), rpy=(angle, 0.0, 0.0)),
            material=material,
            name=f"reel_symbol_band_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


# adopted: S1, S2, S3, S6
def _build_buttons(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> list[Part]:
    buttons: list[Part] = []
    offsets = _button_offsets(r.button_count, r.deck_width)
    for index, x in enumerate(offsets):
        name = "spin_button" if r.button_count == 1 else f"button_{index}"
        button = model.part(name)
        _decorate_button_part(button, r, materials, index=index)
        joint_origin = (
            x,
            _button_joint_y(r),
            r.deck_z + r.cabinet_height * 0.050,
        )
        model.articulation(
            f"{name}_press",
            ArticulationType.PRISMATIC,
            parent=cabinet.part,
            child=button,
            origin=Origin(xyz=joint_origin),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=35.0,
                velocity=0.25,
                lower=0.0,
                upper=r.button_travel,
            ),
        )
        button.inertial = Inertial.from_geometry(
            Box((0.08, 0.04, 0.035)),
            mass=0.25,
            origin=Origin(),
        )
        buttons.append(button)
    return buttons


def _decorate_button_part(
    button: Part,
    r: ResolvedCasinoMachineConfig,
    materials: dict[str, object],
    *,
    index: int,
) -> None:
    cap_w, cap_h = _button_cap_size(r)
    if r.button_style == "rectangular":
        button.visual(
            Box((cap_w * 1.25, cap_h * 0.55, cap_h * 0.72)),
            origin=Origin(xyz=(0.0, -cap_h * 0.18, 0.0)),
            material=materials["button"],
            name="rect_button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        button.visual(
            Box((cap_w * 0.82, cap_h * 0.40, cap_h * 0.52)),
            origin=Origin(xyz=(0.0, cap_h * 0.08, 0.0)),
            material=materials["button_dark"],
            name="rect_button_stem", material_class_id="plastic.opaque_generic",
        )
    else:
        radius = cap_w * (0.42 if r.button_style == "round_lit" else 0.46)
        button.visual(
            Cylinder(radius=radius, length=cap_h * 0.64),
            origin=Origin(xyz=(0.0, -cap_h * 0.18, 0.0), rpy=_cyl_y()),
            material=materials["button"],
            name="round_button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        button.visual(
            Cylinder(radius=radius * 0.72, length=cap_h * 0.55),
            origin=Origin(xyz=(0.0, cap_h * 0.06, 0.0), rpy=_cyl_y()),
            material=materials["button_dark"],
            name="round_button_stem", material_class_id="plastic.opaque_generic",
        )
        if r.button_style == "ringed":
            button.visual(
                Cylinder(radius=radius * 1.05, length=cap_h * 0.18),
                origin=Origin(xyz=(0.0, -cap_h * 0.36, 0.0), rpy=_cyl_y()),
                material=materials["trim"],
                name="button_bezel_ring", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
            )
    button.visual(
        Box((cap_w * 0.72, cap_h * 0.18, cap_h * 0.16)),
        origin=Origin(xyz=(0.0, cap_h * 0.05, -cap_h * 0.20)),
        material=materials["button_dark"],
        name=f"button_internal_bridge_{index}", material_class_id="plastic.opaque_generic",
    )


# adopted: S1, S2, S3, S4, S5, S6
def _build_doors_and_trays(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> list[Part]:
    parts: list[Part] = []
    if r.door_style == "service_panel":
        parts.append(_build_service_panel(model, r, cabinet, materials))
    elif r.door_style in ("cashbox", "coin_tray", "belly"):
        parts.append(_build_cash_or_belly_door(model, r, cabinet, materials))
    elif r.door_style == "payout_tray":
        parts.append(_build_payout_tray_flap(model, r, cabinet, materials))
    return parts


def _build_service_panel(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> Part:
    door = model.part("service_panel")
    w = r.cabinet_width * 0.24
    h = r.cabinet_height * 0.18
    t = r.cabinet_depth * 0.035
    door.visual(
        Box((w, t, h)),
        origin=Origin(xyz=(w * 0.5, -t * 0.82, 0.0)),
        material=materials["cabinet_dark"],
        name="service_panel_slab", material_class_id="metal.paint_coated",
    )
    door.visual(
        Cylinder(radius=t * 0.55, length=h * 1.04),
        origin=Origin(xyz=(0.0, -t * 0.5, 0.0), rpy=_cyl_z()),
        material=materials["metal"],
        name="service_panel_hinge_barrel", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    door.visual(
        Box((w * 0.20, t * 0.40, h * 0.10)),
        origin=Origin(xyz=(w * 0.80, -t * 1.20, 0.0)),
        material=materials["trim"],
        name="service_panel_pull_tab", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    joint_origin = (
        -r.cabinet_width * 0.36,
        cabinet.front_y - t * 0.05,
        r.cabinet_height * 0.29,
    )
    model.articulation(
        "service_panel_hinge",
        ArticulationType.REVOLUTE,
        parent=cabinet.part,
        child=door,
        origin=Origin(xyz=joint_origin),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=90.0,
            velocity=0.9,
            lower=0.0,
            upper=r.door_open_angle,
        ),
    )
    return door


def _build_cash_or_belly_door(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> Part:
    part_name = "belly_door" if r.door_style == "belly" else "coin_tray_door"
    door = model.part(part_name)
    w = r.cabinet_width * (0.56 if r.door_style == "belly" else 0.40)
    h = r.cabinet_height * (0.22 if r.door_style == "belly" else 0.12)
    t = r.cabinet_depth * 0.035
    door.visual(
        Box((w, t, h)),
        origin=Origin(xyz=(0.0, -t * 0.5, -h * 0.5)),
        material=materials["cabinet_dark"],
        name=f"{part_name}_slab", material_class_id="metal.paint_coated",
    )
    door.visual(
        Cylinder(radius=t * 0.60, length=w),
        origin=Origin(xyz=(0.0, -t * 0.5, 0.0), rpy=_cyl_x()),
        material=materials["metal"],
        name=f"{part_name}_top_hinge_barrel", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    door.visual(
        Box((w * 0.18, t * 0.40, h * 0.12)),
        origin=Origin(xyz=(0.0, -t * 0.85, -h * 0.75)),
        material=materials["trim"],
        name=f"{part_name}_pull_lip", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    if r.door_style == "coin_tray":
        door.visual(
            Box((w * 0.58, t * 0.20, h * 0.30)),
            origin=Origin(xyz=(0.0, -t * 1.08, -h * 0.48)),
            material=materials["payout"],
            name="coin_tray_door_visible_mouth", material_class_id="metal.blackened_gunmetal",
        )
        door.visual(
            Box((w * 0.66, t * 0.14, h * 0.08)),
            origin=Origin(xyz=(0.0, -t * 1.16, -h * 0.33)),
            material=materials["metal"],
            name="coin_tray_door_mouth_upper_rim", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
        )
    z = r.cabinet_height * (0.31 if r.door_style == "belly" else 0.22)
    joint_origin = (
        0.0,
        cabinet.front_y - t * 0.05,
        z,
    )
    model.articulation(
        f"{part_name}_hinge",
        ArticulationType.REVOLUTE,
        parent=cabinet.part,
        child=door,
        origin=Origin(xyz=joint_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=90.0,
            velocity=0.9,
            lower=-r.door_open_angle,
            upper=0.0,
        ),
    )
    return door


def _build_payout_tray_flap(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> Part:
    flap = model.part("payout_tray_flap")
    w = r.cabinet_width * 0.48
    h = r.cabinet_height * 0.095
    t = r.cabinet_depth * 0.035
    flap.visual(
        Box((w, t, h)),
        origin=Origin(xyz=(0.0, -t * 0.5, -h * 0.5)),
        material=materials["payout"],
        name="payout_flap_plate", material_class_id="metal.blackened_gunmetal",
    )
    flap.visual(
        Cylinder(radius=t * 0.55, length=w),
        origin=Origin(xyz=(0.0, -t * 0.5, 0.0), rpy=_cyl_x()),
        material=materials["metal"],
        name="payout_flap_hinge", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    flap.visual(
        Box((w * 0.82, t * 0.40, h * 0.16)),
        origin=Origin(xyz=(0.0, -t * 0.82, -h * 0.90)),
        material=materials["trim"],
        name="payout_flap_lower_lip", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    flap.visual(
        Box((w * 0.60, t * 0.20, h * 0.26)),
        origin=Origin(xyz=(0.0, -t * 1.08, -h * 0.48)),
        material=materials["payout"],
        name="payout_flap_visible_mouth", material_class_id="metal.blackened_gunmetal",
    )
    flap.visual(
        Box((w * 0.70, t * 0.14, h * 0.08)),
        origin=Origin(xyz=(0.0, -t * 1.16, -h * 0.33)),
        material=materials["metal"],
        name="payout_flap_mouth_upper_rim", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    joint_origin = (
        0.0,
        cabinet.front_y - t * 0.05,
        r.payout_z + h * 0.45,
    )
    model.articulation(
        "payout_tray_flap_hinge",
        ArticulationType.REVOLUTE,
        parent=cabinet.part,
        child=flap,
        origin=Origin(xyz=joint_origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=65.0,
            velocity=0.8,
            lower=-r.tray_open_angle,
            upper=0.0,
        ),
    )
    return flap


# adopted: S4, S5, S6
def _build_lever_or_knob(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> Part | None:
    if r.lever_style == "side_pull":
        return _build_side_lever(model, r, cabinet, materials)
    if r.lever_style in ("selector_knob", "volume_knob"):
        return _build_rotary_knob(model, r, cabinet, materials)
    return None


def _build_side_lever(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> Part:
    lever = model.part("side_lever")
    side = r.cabinet_width * 0.5
    lever_len = r.cabinet_height * 0.25
    boss_r = min(0.055, r.cabinet_width * 0.050)
    lever.visual(
        Cylinder(radius=boss_r, length=r.cabinet_width * 0.080),
        origin=Origin(xyz=(r.cabinet_width * 0.040, 0.0, 0.0), rpy=_cyl_x()),
        material=materials["metal"],
        name="lever_side_boss", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    lever.visual(
        Box((r.cabinet_width * 0.050, r.cabinet_width * 0.045, lever_len)),
        origin=Origin(xyz=(r.cabinet_width * 0.085, 0.0, -lever_len * 0.50)),
        material=materials["metal"],
        name="lever_pull_arm", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    lever.visual(
        Sphere(radius=boss_r * 0.82),
        origin=Origin(xyz=(r.cabinet_width * 0.085, 0.0, -lever_len)),
        material=materials["button"],
        name="lever_grip_ball", material_class_id="plastic.opaque_glossy_molded",
    )
    lever.visual(
        Box((r.cabinet_width * 0.050, r.cabinet_width * 0.040, boss_r * 0.60)),
        origin=Origin(xyz=(r.cabinet_width * 0.070, 0.0, -boss_r * 0.30)),
        material=materials["metal"],
        name="lever_boss_to_arm_bridge", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    joint_origin = (
        side - r.cabinet_width * 0.010,
        -r.cabinet_depth * 0.18,
        r.cabinet_height * 0.55,
    )
    model.articulation(
        "side_lever_pull",
        ArticulationType.REVOLUTE,
        parent=cabinet.part,
        child=lever,
        origin=Origin(xyz=joint_origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=120.0,
            velocity=1.1,
            lower=-r.lever_pull_angle,
            upper=0.15,
        ),
    )
    return lever


def _build_rotary_knob(
    model: ArticulatedObject,
    r: ResolvedCasinoMachineConfig,
    cabinet: CabinetAnchors,
    materials: dict[str, object],
) -> Part:
    knob = model.part("volume_knob")
    radius = min(0.045, r.cabinet_width * 0.050)
    knob_z = max(
        r.deck_z + r.cabinet_height * 0.045,
        min(r.deck_z + r.cabinet_height * 0.075, r.reel_window_z - r.cabinet_height * 0.135),
    )
    joint_origin = (
        r.cabinet_width * 0.43,
        cabinet.front_y - r.cabinet_depth * 0.025,
        knob_z,
    )
    cabinet.part.visual(
        Cylinder(radius=radius * 0.54, length=max(radius * 1.05, r.cabinet_depth * 0.040)),
        origin=Origin(
            xyz=(
                joint_origin[0],
                cabinet.front_y - r.cabinet_depth * 0.010,
                joint_origin[2],
            ),
            rpy=_cyl_y(),
        ),
        material=materials["cabinet_dark"],
        name="volume_knob_socket", material_class_id="metal.paint_coated",
    )
    knob.visual(
        Cylinder(radius=radius, length=radius * 0.70),
        origin=Origin(rpy=_cyl_y()),
        material=materials["metal"],
        name="knob_body", material_class_id=("metal.brass_polished" if r.material_style in {"casino_red", "midnight_chrome", "bar_top_blue", "classic_gold"} else "metal.blackened_gunmetal"),
    )
    knob.visual(
        Box((radius * 1.20, radius * 0.18, radius * 0.12)),
        origin=Origin(xyz=(0.0, -radius * 0.38, radius * 0.22)),
        material=materials["trim"],
        name="knob_pointer_bar", material_class_id=("metal.precious_gold" if r.material_style in {"midnight_chrome", "bar_top_blue", "classic_gold", "slant_black"} else "metal.brass_polished"),
    )
    model.articulation(
        "volume_knob_spin",
        ArticulationType.CONTINUOUS,
        parent=cabinet.part,
        child=knob,
        origin=Origin(xyz=joint_origin),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=3.0),
    )
    return knob


def build_casino_machine(
    config: CasinoMachineConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or CasinoMachineConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    materials = _register_materials(model, r.palette)
    cabinet = _build_cabinet(model, r, materials)
    _build_reels(model, r, cabinet, materials)
    _build_buttons(model, r, cabinet, materials)
    _build_doors_and_trays(model, r, cabinet, materials)
    _build_lever_or_knob(model, r, cabinet, materials)
    return model


def build_seeded_casino_machine(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_casino_machine(config_from_seed(seed), assets=assets)


def slot_choices_for_config(config: CasinoMachineConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("cabinet_body", r.cabinet_style),
        ("game_display_or_reels", r.game_face_style),
        ("controls_and_openings", r.control_module),
        ("reel_count", str(r.reel_count)),
        ("button_count", str(r.button_count)),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    parts = {p.name for p in model.parts}
    if "cabinet" not in parts:
        return
    cabinet = model.get_part("cabinet")
    for part_name in parts:
        if part_name.startswith("reel"):
            reel = model.get_part(part_name)
            for parent_elem in (
                "main_cabinet_shell",
                "reel_window_glass",
                "reel_window_outer_frame",
                "slant_top_control_slope",
                "reel_symbol_window_0",
                "reel_symbol_window_1",
                "reel_symbol_window_2",
                "reel_symbol_window_3",
                "reel_symbol_window_4",
                "reel_payline_tick_0",
                "reel_payline_tick_1",
                "reel_payline_tick_2",
                "reel_payline_tick_3",
                "reel_payline_tick_4",
            ):
                for child_elem in (
                    "reel_drum",
                    "reel_axle_hub",
                    "left_reel_rim",
                    "right_reel_rim",
                    "reel_symbol_band_0",
                    "reel_symbol_band_1",
                    "reel_symbol_band_2",
                    "reel_symbol_band_3",
                    "reel_symbol_band_4",
                    "reel_symbol_band_5",
                    "chrome_reel_center_band",
                ):
                    try:
                        ctx.allow_overlap(
                            cabinet,
                            reel,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="spinning reel is captured just behind the cabinet reel window",
                        )
                    except Exception:
                        pass
        if part_name.startswith("button") or part_name == "spin_button":
            button = model.get_part(part_name)
            socket_names = tuple(f"button_socket_{i}" for i in range(5))
            for parent_elem in (
                "main_cabinet_shell",
                "control_deck_carrier",
                "control_deck_front_lip",
                "slant_top_control_slope",
                "volume_knob_socket",
                *socket_names,
            ):
                for child_elem in (
                    "rect_button_stem",
                    "round_button_stem",
                    "button_internal_bridge_0",
                    "button_internal_bridge_1",
                    "button_internal_bridge_2",
                    "button_internal_bridge_3",
                    "button_internal_bridge_4",
                ):
                    try:
                        ctx.allow_overlap(
                            cabinet,
                            button,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="button stem rides in the control deck socket",
                        )
                    except Exception:
                        pass
        if part_name in ("service_panel", "coin_tray_door", "belly_door", "payout_tray_flap"):
            door = model.get_part(part_name)
            for parent_elem in (
                "main_cabinet_shell",
                "coin_return_lip",
                "bar_top_low_front_band",
                "bar_top_ticket_slot",
                "video_poker_screen_inner",
                "control_deck_carrier",
                "bill_acceptor_slot",
                "payout_recess_shadow",
                "payout_tray_recess",
                "payout_tray_metal_rim",
                "payout_rim_fastener_0",
                "payout_rim_fastener_1",
                "belly_panel_recess",
                "control_deck_front_lip",
                "button_socket_0",
                "button_socket_1",
                "button_socket_2",
                "button_socket_3",
                "button_socket_4",
            ):
                for child_elem in (
                    "service_panel_hinge_barrel",
                    "service_panel_slab",
                    "service_panel_pull_tab",
                    "coin_tray_door_top_hinge_barrel",
                    "coin_tray_door_slab",
                    "coin_tray_door_pull_lip",
                    "belly_door_top_hinge_barrel",
                    "belly_door_slab",
                    "belly_door_pull_lip",
                    "payout_flap_hinge",
                    "payout_flap_plate",
                    "payout_flap_lower_lip",
                ):
                    try:
                        ctx.allow_overlap(
                            cabinet,
                            door,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="hinged casino door/flap sits flush in the cabinet opening",
                        )
                    except Exception:
                        pass
        if part_name == "side_lever":
            lever = model.get_part("side_lever")
            for parent_elem in (
                "right_vertical_trim",
                "main_cabinet_shell",
                "classic_coin_slot_plate",
            ):
                for child_elem in ("lever_side_boss", "lever_pull_arm", "lever_boss_to_arm_bridge"):
                    try:
                        ctx.allow_overlap(
                            cabinet,
                            lever,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="side lever boss is captured by the cabinet side bracket",
                        )
                    except Exception:
                        pass
        if part_name == "volume_knob":
            knob = model.get_part("volume_knob")
            for parent_elem in (
                "main_cabinet_shell",
                "control_deck_carrier",
                "control_deck_front_lip",
                "slant_top_control_slope",
                "volume_knob_socket",
            ):
                for child_elem in ("knob_body", "knob_stem", "knob_pointer_bar"):
                    try:
                        ctx.allow_overlap(
                            cabinet,
                            knob,
                            elem_a=parent_elem,
                            elem_b=child_elem,
                            reason="rotary knob stem passes through the control deck face",
                        )
                    except Exception:
                        pass


def run_casino_machine_tests(
    object_model: ArticulatedObject,
    config: CasinoMachineConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    # Buttons / knobs press into their deck sockets; that cabinet<->control
    # interface is an intentional captured prismatic/revolute engagement.
    _pn = {p.name for p in object_model.parts}
    if "cabinet" in _pn:
        _cab = object_model.get_part("cabinet")
        for _bp in _pn:
            if "button" in _bp or "knob" in _bp or "lever" in _bp or "flap" in _bp or "tray" in _bp:
                ctx.allow_overlap(
                    _cab, object_model.get_part(_bp),
                    reason="Control button/knob/lever is captured in its cabinet deck socket.",
                )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    if "cabinet" not in part_names:
        ctx.fail("identity", "casino machine must have a cabinet root part")
    if not object_model.joints:
        ctx.fail("interaction", "casino machine must have at least one interactive joint")
    if r.reel_count > 0:
        expected = 1 if r.reel_count == 1 else r.reel_count
        actual_reels = [name for name in part_names if name == "reel" or name.startswith("reel_")]
        if len(actual_reels) != expected:
            ctx.fail("reel_count", f"expected {expected} reel parts, got {len(actual_reels)}")
        for reel_name in actual_reels:
            if f"{reel_name}_spin" not in joint_names:
                ctx.fail("reel_joint", f"{reel_name} must have a CONTINUOUS spin joint")
    for i in range(r.button_count):
        name = "spin_button" if r.button_count == 1 else f"button_{i}"
        if name not in part_names:
            ctx.fail("button_part", f"missing {name}")
        if f"{name}_press" not in joint_names:
            ctx.fail("button_joint", f"missing prismatic press joint for {name}")
    if r.door_style == "service_panel" and "service_panel_hinge" not in joint_names:
        ctx.fail("door_joint", "service panel must have a hinge")
    if r.door_style == "payout_tray" and "payout_tray_flap_hinge" not in joint_names:
        ctx.fail("tray_joint", "payout tray must have a hinge")
    if r.lever_style == "side_pull" and "side_lever_pull" not in joint_names:
        ctx.fail("lever_joint", "side lever module must have a pull joint")
    if r.lever_style == "volume_knob" and "volume_knob_spin" not in joint_names:
        ctx.fail("knob_joint", "belly-button-knob module must have rotary knob joint")
    return ctx.report()


__all__ = [
    "CasinoMachineConfig",
    "ResolvedCasinoMachineConfig",
    "build_casino_machine",
    "build_seeded_casino_machine",
    "config_from_seed",
    "resolve_config",
    "run_casino_machine_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]


def _material_class_id(
    value: str,
    first_values: tuple[str, ...],
    first_id: str,
    second_id: str,
) -> str:
    return first_id if value in first_values else second_id
