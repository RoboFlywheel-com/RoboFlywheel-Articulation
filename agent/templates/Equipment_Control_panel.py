# SPDX-License-Identifier: Apache-2.0

"""Control panel — modular procedural template (SEGMENT 3).

A control panel is a rigid housing carried by some MOUNT mechanism, with a
cluster of real articulated human-machine CONTROLs on its front face (or side
wall) and a cluster of purely-decorative READOUT visuals (LCD / gauge / LEDs).

Three slots + two multiplicity axes (derived from 13 5-star sources — 3
device-archetype parents + 10 picture-subcat forks in the articraft_data repo):

  Slot A  mount    : pendant_rod | rail_clamp | conduit_wall | wall_backplate
                     (decides the root part + the single FIXED seat to housing)
  Slot B  control  : round_push_buttons | rotary_disconnect_handle |
                     rotary_selector_knob | toggle_switch_bank | mushroom_estop
                     (the hero non-FIXED joint(s) live here)
  Slot C  readout  : none | rect_lcd_with_leds | digital_display_window |
                     analog_round_gauge | lcd_led_vent_cluster
                     (pure housing-fixed visuals, no joint)

  multiplicity 1 : button_count  (round_push_buttons row, N in [2,12])
  multiplicity 2 : switch_count  (toggle_switch_bank,    M in [2, 6])

Unified frame (the P2/variant convention — all forks already share it):
  +X = width (left-right)   +Y = depth, front face normal (+Y)   +Z = up
  The housing local origin is on its BACK face (back at y=0, front at y=d),
  so FACE_Y = HOUSING_D; this keeps every housing-attached joint's child link
  local origin within tol of a real housing surface (the origin-far check
  measures the child's local (0,0,0) to its own mesh surface).

Adopted source map (paths relative to the articraft_data repo root):
  S1  P1 c28c270c  pendant_rod + push buttons (PRISMATIC -X) + side toggle
  S2  P2 647d2061  rail_clamp + push buttons (PRISMATIC -Y) + rect_lcd_with_leds
  S3  P3 ab3b9f65  conduit_wall + rotary_disconnect_handle (REVOLUTE +X) + digital window
  S4  ...mountA_backplate   wall_backplate (flat plate + 4 keyhole tabs)
  S5  ...mountA_railN       rail_clamp on a large enclosure body
  S6  ...ctrlB_rotaryknob   rotary_selector_knob (KnobGeometry, REVOLUTE +Y)
  S7  ...ctrlB_togglebank   toggle_switch_bank (REVOLUTE +X, SWITCH_COUNT)
  S8  ...ctrlB_mushroom     mushroom_estop (lathe cap, PRISMATIC -X deep latch)
  S9  ...ctrlB_pushbtn_railrotary  round_push_buttons cross-body on P3
  S10 ...readC_gauge        analog_round_gauge (rim+dial+11 ticks+needle+hub)
  S11 ...readC_lcdrow       lcd_led_vent_cluster (LCD + LED row + vent column)
  S12 ...N3_buttons         multiplicity copy-logic N=3 (button_{i} + slide_{i})
  S13 ...N6_buttons         multiplicity copy-logic N=6 (the clean for-loop)

HARD RULES honoured:
  1. Every decoration is `parent.visual(...)` — no FIXED joints for decor.
  2. Every non-FIXED joint declares a MatingContract to real visuals.
  3. Structure is derived from the declared 5-star sources (no Lathe/mesh
     hero shapes downgraded: mushroom cap = LatheGeometry, knob = KnobGeometry).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot vocabularies
# --------------------------------------------------------------------------- #
MountStyle = Literal["pendant_rod", "rail_clamp", "conduit_wall", "wall_backplate"]
ControlStyle = Literal[
    "round_push_buttons",
    "rotary_disconnect_handle",
    "rotary_selector_knob",
    "toggle_switch_bank",
    "mushroom_estop",
]
ReadoutStyle = Literal[
    "none",
    "rect_lcd_with_leds",
    "digital_display_window",
    "analog_round_gauge",
    "lcd_led_vent_cluster",
]
PaletteStyle = Literal[
    "industrial_gray",
    "cast_steel_dark",
    "panel_plastic_beige",
    "safety_yellow_black",
    "navy_industrial",
    "stainless_clean",
]

MOUNT_STYLES: tuple[MountStyle, ...] = (
    "pendant_rod",
    "rail_clamp",
    "conduit_wall",
    "wall_backplate",
)
CONTROL_STYLES: tuple[ControlStyle, ...] = (
    "round_push_buttons",
    "rotary_disconnect_handle",
    "rotary_selector_knob",
    "toggle_switch_bank",
    "mushroom_estop",
)
READOUT_STYLES: tuple[ReadoutStyle, ...] = (
    "none",
    "rect_lcd_with_leds",
    "digital_display_window",
    "analog_round_gauge",
    "lcd_led_vent_cluster",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "industrial_gray",
    "cast_steel_dark",
    "panel_plastic_beige",
    "safety_yellow_black",
    "navy_industrial",
    "stainless_clean",
)

# Multiplicity ranges (spec §Multiplicity).
BTN_N_MIN, BTN_N_MAX = 2, 12
SW_N_MIN, SW_N_MAX = 2, 6
# Small N high-frequency, large N rare tail.
BTN_WEIGHTS = (0.16, 0.20, 0.18, 0.14, 0.10, 0.08, 0.05, 0.04, 0.02, 0.02, 0.01)
SW_WEIGHTS = (0.34, 0.30, 0.20, 0.10, 0.06)

# --------------------------------------------------------------------------- #
# Palettes — 6 realistic colorways drawn from the 5-star sources.
# Roles: shell, trim, metal, mount, control, display, led, hot, dial, pointer.
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "industrial_gray": {
        "shell": (0.55, 0.57, 0.60, 1.0),
        "trim": (0.30, 0.31, 0.34, 1.0),
        "metal": (0.66, 0.68, 0.71, 1.0),
        "mount": (0.40, 0.42, 0.45, 1.0),
        "control": (0.20, 0.20, 0.22, 1.0),
        "display": (0.06, 0.09, 0.10, 1.0),
        "led": (0.85, 0.25, 0.20, 1.0),
        "hot": (0.78, 0.03, 0.025, 1.0),
        "dial": (0.88, 0.88, 0.85, 1.0),
        "pointer": (0.92, 0.20, 0.18, 1.0),
    },
    "cast_steel_dark": {
        "shell": (0.30, 0.31, 0.33, 1.0),
        "trim": (0.18, 0.19, 0.20, 1.0),
        "metal": (0.55, 0.56, 0.58, 1.0),
        "mount": (0.45, 0.46, 0.48, 1.0),
        "control": (0.09, 0.09, 0.10, 1.0),
        "display": (0.10, 0.16, 0.14, 1.0),
        "led": (0.30, 0.85, 0.45, 1.0),
        "hot": (0.80, 0.05, 0.04, 1.0),
        "dial": (0.82, 0.82, 0.80, 1.0),
        "pointer": (0.95, 0.85, 0.30, 1.0),
    },
    "panel_plastic_beige": {
        "shell": (0.74, 0.74, 0.71, 1.0),
        "trim": (0.40, 0.40, 0.38, 1.0),
        "metal": (0.18, 0.18, 0.19, 1.0),
        "mount": (0.55, 0.55, 0.52, 1.0),
        "control": (0.58, 0.58, 0.56, 1.0),
        "display": (0.16, 0.20, 0.18, 1.0),
        "led": (0.90, 0.55, 0.15, 1.0),
        "hot": (0.78, 0.04, 0.03, 1.0),
        "dial": (0.92, 0.91, 0.86, 1.0),
        "pointer": (0.20, 0.20, 0.20, 1.0),
    },
    "safety_yellow_black": {
        "shell": (0.16, 0.16, 0.17, 1.0),
        "trim": (0.92, 0.78, 0.10, 1.0),
        "metal": (0.55, 0.56, 0.58, 1.0),
        "mount": (0.10, 0.10, 0.10, 1.0),
        "control": (0.92, 0.78, 0.10, 1.0),
        "display": (0.05, 0.07, 0.06, 1.0),
        "led": (0.95, 0.85, 0.10, 1.0),
        "hot": (0.85, 0.10, 0.05, 1.0),
        "dial": (0.95, 0.92, 0.80, 1.0),
        "pointer": (0.05, 0.05, 0.05, 1.0),
    },
    "navy_industrial": {
        "shell": (0.20, 0.27, 0.38, 1.0),
        "trim": (0.12, 0.16, 0.24, 1.0),
        "metal": (0.60, 0.63, 0.68, 1.0),
        "mount": (0.30, 0.34, 0.42, 1.0),
        "control": (0.85, 0.86, 0.88, 1.0),
        "display": (0.05, 0.12, 0.16, 1.0),
        "led": (0.30, 0.80, 0.95, 1.0),
        "hot": (0.85, 0.20, 0.15, 1.0),
        "dial": (0.90, 0.92, 0.95, 1.0),
        "pointer": (0.95, 0.35, 0.20, 1.0),
    },
    "stainless_clean": {
        "shell": (0.78, 0.79, 0.80, 1.0),
        "trim": (0.45, 0.46, 0.48, 1.0),
        "metal": (0.88, 0.89, 0.90, 1.0),
        "mount": (0.62, 0.63, 0.65, 1.0),
        "control": (0.25, 0.25, 0.27, 1.0),
        "display": (0.08, 0.10, 0.12, 1.0),
        "led": (0.20, 0.75, 0.40, 1.0),
        "hot": (0.80, 0.06, 0.05, 1.0),
        "dial": (0.95, 0.95, 0.94, 1.0),
        "pointer": (0.10, 0.10, 0.10, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Nominal dimensions (meters).
# --------------------------------------------------------------------------- #
HOUSING_W0 = 0.200
HOUSING_H0 = 0.240
HOUSING_D = 0.085
HOUSING_CORNER = 0.012
EDGE_MARGIN = 0.024

# round_push_buttons
BTN_R = 0.011
BTN_CAP_H = 0.006
BTN_COLLAR_R = 0.014
BTN_COLLAR_H = 0.004
BTN_PLUNGER_R = 0.0075
BTN_PLUNGER_L = 0.014
BTN_TRAVEL = 0.006
BTN_PITCH0 = 0.040

# toggle_switch_bank
SW_SHANK_R = 0.0030
SW_BALL_R = 0.0033
SW_STEM_R = 0.0018
SW_STEM_L = 0.020
SW_SOCKET_OUT_R = 0.0060
SW_SOCKET_IN_R = 0.0042
SW_SOCKET_H = 0.0024
SW_DX0 = 0.024
SW_THROW = 0.45

# rotary_selector_knob
KNOB_D = 0.030
KNOB_H = 0.014
KNOB_STEM_R = 0.0040
KNOB_STEM_L = 0.012
KNOB_TURN = math.radians(135.0)

# mushroom_estop
ESTOP_GUARD_R = 0.0265
ESTOP_GUARD_H = 0.0060
ESTOP_GASKET_R = 0.0185
ESTOP_GASKET_H = 0.0040
ESTOP_CAP_R = 0.0245
ESTOP_CAP_H = 0.0250
ESTOP_TRAVEL = 0.0120

# rotary_disconnect_handle
OP_Z = 0.000
FLANGE_R = 0.030
FLANGE_PROUD = 0.014
SHAFT_R = 0.010
SHAFT_LEN = 0.020
LEVER_LEN = 0.090
LEVER_W = 0.026
LEVER_TH = 0.016
HANDLE_THROW = math.radians(160.0)


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ControlPanelConfig:
    mount_style: MountStyle | None = None
    control_style: ControlStyle | None = None
    readout_style: ReadoutStyle | None = None
    button_count: int | None = None
    switch_count: int | None = None
    palette_style: PaletteStyle = "industrial_gray"
    housing_w_scale: float = 1.0
    housing_h_scale: float = 1.0
    name: str = "control_panel"


@dataclass(frozen=True)
class ResolvedControlPanelConfig:
    mount_style: MountStyle
    control_style: ControlStyle
    readout_style: ReadoutStyle
    button_count: int
    switch_count: int
    palette_style: PaletteStyle
    # Concrete geometry.
    w: float
    h: float
    d: float
    corner: float
    face_y: float
    control_cz: float
    readout_cz: float
    button_pitch: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> ControlPanelConfig:
    """Deterministic procedural sampling for every seed (seed=0 is not special)."""
    rng = random.Random(seed)
    return ControlPanelConfig(
        mount_style=rng.choice(MOUNT_STYLES),
        control_style=rng.choice(CONTROL_STYLES),
        readout_style=rng.choice(READOUT_STYLES),
        button_count=rng.choices(range(BTN_N_MIN, BTN_N_MAX + 1), weights=BTN_WEIGHTS, k=1)[0],
        switch_count=rng.choices(range(SW_N_MIN, SW_N_MAX + 1), weights=SW_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        housing_w_scale=round(rng.uniform(0.85, 1.25), 4),
        housing_h_scale=round(rng.uniform(0.85, 1.25), 4),
        name=f"seeded_control_panel_{seed}",
    )


def resolve_config(config: ControlPanelConfig | None = None) -> ResolvedControlPanelConfig:
    cfg = config or ControlPanelConfig()

    mount_style = _pick(cfg.mount_style, MOUNT_STYLES)
    control_style = _pick(cfg.control_style, CONTROL_STYLES)
    readout_style = _pick(cfg.readout_style, READOUT_STYLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    button_count = int(cfg.button_count) if cfg.button_count is not None else 4
    button_count = int(_clamp(button_count, BTN_N_MIN, BTN_N_MAX))
    switch_count = int(cfg.switch_count) if cfg.switch_count is not None else 3
    switch_count = int(_clamp(switch_count, SW_N_MIN, SW_N_MAX))

    w = HOUSING_W0 * _clamp(cfg.housing_w_scale, 0.85, 1.25)
    h = HOUSING_H0 * _clamp(cfg.housing_h_scale, 0.85, 1.25)
    d = HOUSING_D

    # --- Multiplicity layout: derive pitch and widen housing to fit the row. ---
    button_pitch = BTN_PITCH0
    if control_style == "round_push_buttons":
        # Pitch must keep neighbouring caps from touching.
        min_pitch = 2.0 * BTN_R + 0.006
        button_pitch = max(min_pitch, BTN_PITCH0)
        row_w = (button_count - 1) * button_pitch + 2.0 * BTN_COLLAR_R + 2.0 * EDGE_MARGIN
        w = max(w, row_w)
    elif control_style == "toggle_switch_bank":
        row_w = (switch_count - 1) * SW_DX0 + 2.0 * SW_SOCKET_OUT_R + 2.0 * EDGE_MARGIN
        w = max(w, row_w)

    return ResolvedControlPanelConfig(
        mount_style=mount_style,
        control_style=control_style,
        readout_style=readout_style,
        button_count=button_count,
        switch_count=switch_count,
        palette_style=palette_style,
        w=w,
        h=h,
        d=d,
        corner=min(HOUSING_CORNER, 0.45 * min(w, h)),
        # Housing local origin sits on the BACK face: back at y=0, front at y=d.
        # This keeps every housing-attached joint's child/parent origin near a
        # real housing surface (the origin-far check measures the child link's
        # local (0,0,0) to the child mesh surface).
        face_y=d,
        control_cz=-h * 0.18,
        readout_cz=h * 0.22,
        button_pitch=button_pitch,
        name=cfg.name or "control_panel",
    )


def with_overrides(config: ControlPanelConfig, **kwargs: object) -> ControlPanelConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ControlPanelConfig | ResolvedControlPanelConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedControlPanelConfig) else resolve_config(config)
    if r.control_style == "round_push_buttons":
        mult = f"btn_n{r.button_count}"
    elif r.control_style == "toggle_switch_bank":
        mult = f"sw_n{r.switch_count}"
    else:
        mult = "single"
    return (
        ("mount", r.mount_style),
        ("control", r.control_style),
        ("readout", r.readout_style),
        ("multiplicity", mult),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Housing (always present, centered at the world origin).
# --------------------------------------------------------------------------- #
def _build_housing(housing, r: ResolvedControlPanelConfig, mats) -> None:
    profile = rounded_rect_profile(r.w, r.d, r.corner, corner_segments=8)
    shell = ExtrudeGeometry(profile, r.h, center=True)
    # Shift so the housing spans y in [0, d] (local origin on the back face).
    shell = shell.translate(0.0, r.d / 2.0, 0.0)
    housing.visual(
        mesh_from_geometry(shell, "housing_shell"), material=mats["shell"], name="housing_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic")
    )
    housing.inertial = Inertial.from_geometry(
        Box((r.w, r.d, r.h)), mass=2.4, origin=Origin(xyz=(0.0, r.d / 2.0, 0.0))
    )


# --------------------------------------------------------------------------- #
# MOUNT modules (Slot A). Each establishes the root part + a single FIXED seat.
# FIXED mount joints are mechanically rigid; mating is grandfathered (the parts
# carry real geometric contact, verified by fail_if_isolated_parts).
# --------------------------------------------------------------------------- #
def _mount_pendant_rod(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Vertical steel suspension rod is the root; the box hangs captive on it."""
    rod_len = r.h + 0.30
    rod = model.part("support_rod")
    rod.visual(
        Cylinder(radius=0.005, length=rod_len),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["metal"],
        name="rod_shaft", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
    )
    rod.inertial = Inertial.from_geometry(
        Cylinder(radius=0.005, length=rod_len), mass=0.4, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    # Top / bottom cable glands on the housing where the rod enters (decor visuals).
    for sgn, nm in ((1.0, "top_gland"), (-1.0, "bottom_gland")):
        housing.visual(
            Cylinder(radius=0.010, length=0.024),
            origin=Origin(xyz=(0.0, 0.0, sgn * (r.h / 2.0 - 0.004))),
            material=mats["mount"],
            name=nm, material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "panel_plastic_beige", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.cast_iron_bare"),
        )
    model.articulation(
        "rod_to_housing",
        ArticulationType.FIXED,
        parent=rod,
        child=housing,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )


def _mount_rail_clamp(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Housing is root; a rear clamp seats two independent horizontal rails."""
    clamp_y = -0.011  # behind the housing back face (y=0), overlapping it
    housing.visual(
        Box((min(0.060, r.w * 0.4), 0.022, 0.070)),
        origin=Origin(xyz=(0.0, clamp_y, 0.0)),
        material=mats["mount"],
        name="rear_clamp", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "panel_plastic_beige", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.cast_iron_bare"),
    )
    rail_len = r.w + 0.16
    rail_y = -0.016
    for nm, z in (("rail_top", 0.020), ("rail_bottom", -0.020)):
        rail = model.part(nm)
        rail.visual(
            Cylinder(radius=0.0055, length=rail_len),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"{nm}_bar", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
        )
        rail.inertial = Inertial.from_geometry(
            Cylinder(radius=0.0055, length=rail_len),
            mass=0.2,
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        )
        model.articulation(
            f"clamp_to_{nm}",
            ArticulationType.FIXED,
            parent=housing,
            child=rail,
            origin=Origin(xyz=(0.0, rail_y, z)),
        )


def _mount_conduit_wall(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Vertical conduit run is the root; a back-mount stud bolts the housing on."""
    base = model.part("base")
    pipe_len = r.h + 0.42
    conduit_y = -0.040  # vertical pipe run behind the housing back face (y=0)
    for i, dx in enumerate((-0.055, -0.018, 0.018, 0.055)):
        base.visual(
            Cylinder(radius=0.012, length=pipe_len),
            origin=Origin(xyz=(dx, conduit_y, 0.0)),
            material=mats["mount"],
            name=f"conduit_run_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"industrial_gray", "panel_plastic_beige", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
        )
    # Horizontal strap tying the pipes together behind the housing.
    base.visual(
        Box((0.150, 0.012, 0.040)),
        origin=Origin(xyz=(0.0, -0.026, r.h / 2.0 - 0.030)),
        material=mats["mount"],
        name="conduit_strap", material_class_id=("metal.steel_galvanized" if r.palette_style in {"industrial_gray", "panel_plastic_beige", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
    )
    # Back-mount stud reaching forward to the housing back face so the FIXED
    # joint origin (0,0,0) lands on real base geometry; bolted into the rear.
    base.visual(
        Cylinder(radius=0.012, length=0.052),
        origin=Origin(xyz=(0.0, -0.020, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["mount"],
        name="mount_stud", material_class_id=("metal.steel_galvanized" if r.palette_style in {"industrial_gray", "panel_plastic_beige", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
    )
    base.inertial = Inertial.from_geometry(
        Box((0.14, 0.05, pipe_len)), mass=0.9, origin=Origin(xyz=(0.0, conduit_y, 0.0))
    )
    model.articulation(
        "base_to_housing",
        ArticulationType.FIXED,
        parent=base,
        child=housing,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )


def _mount_wall_backplate(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Housing is root; a flat back-plate with 4 keyhole bosses sits flush."""
    plate_w = r.w * 0.92
    plate_h = r.h * 0.92
    back_plate = model.part("back_plate")
    # Plate authored with its contact plane at y=0 (local), extending -Y.
    back_plate.visual(
        Box((plate_w, 0.006, plate_h)),
        origin=Origin(xyz=(0.0, -0.003, 0.0)),
        material=mats["mount"],
        name="wall_back_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "panel_plastic_beige", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.cast_iron_bare"),
    )
    tx = plate_w / 2.0 - 0.014
    tz = plate_h / 2.0 - 0.014
    for i, (x, z) in enumerate(((-tx, tz), (tx, tz), (-tx, -tz), (tx, -tz))):
        back_plate.visual(
            Cylinder(radius=0.0068, length=0.005),
            origin=Origin(xyz=(x, -0.0085, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name=f"mounting_tab_{i}", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
        )
    back_plate.inertial = Inertial.from_geometry(
        Box((plate_w, 0.012, plate_h)), mass=0.5, origin=Origin(xyz=(0.0, -0.006, 0.0))
    )
    model.articulation(
        "housing_to_back_plate",
        ArticulationType.FIXED,
        parent=housing,
        child=back_plate,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )


_MOUNT_BUILDERS = {
    "pendant_rod": _mount_pendant_rod,
    "rail_clamp": _mount_rail_clamp,
    "conduit_wall": _mount_conduit_wall,
    "wall_backplate": _mount_wall_backplate,
}


# --------------------------------------------------------------------------- #
# CONTROL modules (Slot B) — the hero non-FIXED joint(s) parent to the housing.
# Every joint declares a MatingContract to real visuals.
# --------------------------------------------------------------------------- #
def _control_round_push_buttons(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """N momentary push buttons; each a captive plunger PRISMATIC -Y into the face."""
    n = r.button_count
    cz = r.control_cz
    for i in range(n):
        bx = (i - (n - 1) / 2.0) * r.button_pitch
        btn = model.part(f"button_{i}")
        # Plunger barrel runs back into the housing (captured); cap+collar proud.
        btn.visual(
            Cylinder(radius=BTN_PLUNGER_R, length=BTN_PLUNGER_L),
            origin=Origin(xyz=(0.0, -BTN_PLUNGER_L / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["control"],
            name=f"button_{i}_plunger", material_class_id="plastic.opaque_glossy_molded",
        )
        btn.visual(
            Cylinder(radius=BTN_COLLAR_R, length=BTN_COLLAR_H),
            origin=Origin(xyz=(0.0, BTN_COLLAR_H / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["trim"],
            name=f"button_{i}_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
        )
        btn.visual(
            Cylinder(radius=BTN_R, length=BTN_CAP_H),
            origin=Origin(xyz=(0.0, BTN_CAP_H / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["control"],
            name=f"button_{i}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        btn.visual(
            Sphere(radius=BTN_R),
            origin=Origin(xyz=(0.0, BTN_CAP_H, 0.0)),
            material=mats["control"],
            name=f"button_{i}_dome", material_class_id="plastic.opaque_glossy_molded",
        )
        btn.inertial = Inertial.from_geometry(
            Box((2.0 * BTN_COLLAR_R, BTN_PLUNGER_L, 2.0 * BTN_COLLAR_R)),
            mass=0.02,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"button_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=btn,
            origin=Origin(xyz=(bx, r.face_y, cz)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=0.05, lower=0.0, upper=BTN_TRAVEL),
            mating=MatingContract(
                parent_face_geometry="housing_shell",
                parent_face_side="positive_y",
                child_face_geometry=f"button_{i}_cap",
                child_face_side="negative_y",
                contact_tol=0.0020,
            ),
        )


def _control_toggle_switch_bank(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """M small toggle bats, each pivoting REVOLUTE +X in a fixed bushing socket."""
    m = r.switch_count
    cz = r.control_cz
    for idx in range(m):
        sx = (idx - (m - 1) / 2.0) * SW_DX0
        # Fixed bushing socket (housing decor ring) around the toggle.
        housing.visual(
            Cylinder(radius=SW_SOCKET_OUT_R, length=SW_SOCKET_H),
            origin=Origin(xyz=(sx, r.face_y - 0.001, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["trim"],
            name=f"switch_socket_{idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
        )
        sw = model.part(f"switch_{idx}")
        # Shank back face embeds ~1.5 mm into the face: contact for isolated-parts
        # (tol 1e-6) while staying within the mating-gap tol (0.002).
        sw.visual(
            Cylinder(radius=SW_SHANK_R, length=0.005),
            origin=Origin(xyz=(0.0, 0.001, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["control"],
            name=f"switch_{idx}_shank", material_class_id="plastic.opaque_glossy_molded",
        )
        sw.visual(
            Sphere(radius=SW_BALL_R),
            origin=Origin(xyz=(0.0, SW_BALL_R, 0.0)),
            material=mats["control"],
            name=f"switch_{idx}_ball", material_class_id="plastic.opaque_glossy_molded",
        )
        sw.visual(
            Cylinder(radius=SW_STEM_R, length=SW_STEM_L),
            origin=Origin(
                xyz=(0.0, SW_BALL_R + SW_STEM_L / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["metal"],
            name=f"switch_{idx}_stem", material_class_id=("metal.chrome_polished" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
        )
        sw.visual(
            Sphere(radius=SW_STEM_R * 1.4),
            origin=Origin(xyz=(0.0, SW_BALL_R + SW_STEM_L, 0.0)),
            material=mats["metal"],
            name=f"switch_{idx}_tip", material_class_id=("metal.chrome_polished" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
        )
        sw.inertial = Inertial.from_geometry(
            Box((2.0 * SW_BALL_R, SW_BALL_R + SW_STEM_L, 2.0 * SW_BALL_R)),
            mass=0.006,
            origin=Origin(xyz=(0.0, (SW_BALL_R + SW_STEM_L) / 2.0, 0.0)),
        )
        model.articulation(
            f"housing_to_switch_{idx}",
            ArticulationType.REVOLUTE,
            parent=housing,
            child=sw,
            origin=Origin(xyz=(sx, r.face_y, cz)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=0.30, velocity=2.5, lower=-SW_THROW, upper=SW_THROW),
            mating=MatingContract(
                parent_face_geometry="housing_shell",
                parent_face_side="positive_y",
                child_face_geometry=f"switch_{idx}_shank",
                child_face_side="negative_y",
                contact_tol=0.0020,
            ),
        )


def _control_rotary_selector_knob(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Single knurled selector knob rotating REVOLUTE +Y about the face normal."""
    cz = r.control_cz
    selector = model.part("selector_knob")
    knob = KnobGeometry(
        KNOB_D,
        KNOB_H,
        body_style="cylindrical",
        edge_radius=0.0008,
        grip=KnobGrip(style="knurled", count=36, depth=0.0008, helix_angle_deg=22.0),
        center=False,
    )
    knob.rotate_x(-math.pi / 2.0)  # lathe +Z -> +Y; mounting face stays at y=0
    selector.visual(
        mesh_from_geometry(knob, "selector_knob_shell"),
        material=mats["control"],
        name="selector_knob_shell", material_class_id="plastic.patterned_textured",
    )
    # Hidden retaining stem running back through the face.
    selector.visual(
        Cylinder(radius=KNOB_STEM_R, length=KNOB_STEM_L),
        origin=Origin(xyz=(0.0, -KNOB_STEM_L / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["control"],
        name="selector_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    # Contrasting pointer mark on the knob crown (off-axis so rotation is visible).
    selector.visual(
        Box((0.0024, 0.0010, 0.010)),
        origin=Origin(xyz=(0.0, KNOB_H + 0.0005, 0.006)),
        material=mats["pointer"],
        name="pointer_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    selector.inertial = Inertial.from_geometry(
        Cylinder(radius=KNOB_D / 2.0, length=KNOB_H + KNOB_STEM_L),
        mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "turn_selector",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=selector,
        origin=Origin(xyz=(0.0, r.face_y, cz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.35, velocity=4.0, lower=-KNOB_TURN, upper=KNOB_TURN),
        mating=MatingContract(
            parent_face_geometry="housing_shell",
            parent_face_side="positive_y",
            child_face_geometry="selector_knob_shell",
            child_face_side="negative_y",
            contact_tol=0.0020,
        ),
    )


def _control_mushroom_estop(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Single large e-stop: guard + gasket + lathed mushroom cap, PRISMATIC -Y deep latch."""
    cz = r.control_cz
    e = -0.0012  # embed the guard base into the face so isolated-parts sees contact
    estop = model.part("emergency_stop")
    estop.visual(
        Cylinder(radius=ESTOP_GUARD_R, length=ESTOP_GUARD_H),
        origin=Origin(xyz=(0.0, e + ESTOP_GUARD_H / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="safety_guard", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
    )
    estop.visual(
        Cylinder(radius=ESTOP_GASKET_R, length=ESTOP_GASKET_H),
        origin=Origin(
            xyz=(0.0, e + ESTOP_GUARD_H + ESTOP_GASKET_H / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)
        ),
        material=mats["control"],
        name="retaining_gasket", material_class_id="rubber.smooth_plain",
    )
    # Lathed red mushroom cap (radius, z) revolved about +Z, then rotated to +Y.
    cap_profile = [
        (0.0000, 0.0000),
        (0.0130, 0.0000),
        (0.0170, 0.0020),
        (0.0215, 0.0050),
        (ESTOP_CAP_R, 0.0090),
        (ESTOP_CAP_R, 0.0150),
        (0.0230, 0.0185),
        (0.0185, 0.0215),
        (0.0110, 0.0235),
        (0.0000, ESTOP_CAP_H),
    ]
    cap = LatheGeometry(cap_profile, segments=28)
    cap.rotate_x(-math.pi / 2.0)
    cap.translate(0.0, e + ESTOP_GUARD_H + ESTOP_GASKET_H, 0.0)
    estop.visual(mesh_from_geometry(cap, "mushroom_cap"), material=mats["hot"], name="mushroom_cap", material_class_id="plastic.opaque_glossy_molded")
    estop.inertial = Inertial.from_geometry(
        Cylinder(radius=ESTOP_GUARD_R, length=ESTOP_GUARD_H + ESTOP_CAP_H),
        mass=0.05,
        origin=Origin(
            xyz=(0.0, (ESTOP_GUARD_H + ESTOP_CAP_H) / 2.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)
        ),
    )
    model.articulation(
        "housing_to_emergency_stop",
        ArticulationType.PRISMATIC,
        parent=housing,
        child=estop,
        origin=Origin(xyz=(0.0, r.face_y, cz)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.05, lower=0.0, upper=ESTOP_TRAVEL),
        mating=MatingContract(
            parent_face_geometry="housing_shell",
            parent_face_side="positive_y",
            child_face_geometry="safety_guard",
            child_face_side="negative_y",
            contact_tol=0.0020,
        ),
    )


def _control_rotary_disconnect_handle(model, r: ResolvedControlPanelConfig, housing, mats) -> None:
    """Side-mounted rotary disconnect: operator flange/shaft on the -X wall, a
    throw lever rotating REVOLUTE +X (OFF down -> ON up)."""
    op_x = -r.w / 2.0
    op_y = r.d / 2.0  # mid-depth of the side wall
    # Operator base = flange + shaft stub, fixed visuals on the housing -X wall.
    # The flange embeds 3 mm into the wall so it is solidly part of the housing
    # body (not a boundary-touching island).
    flange_len = FLANGE_PROUD + 0.003
    housing.visual(
        Cylinder(radius=FLANGE_R, length=flange_len),
        origin=Origin(
            xyz=(op_x - FLANGE_PROUD / 2.0 + 0.0015, op_y, OP_Z), rpy=(0.0, math.pi / 2.0, 0.0)
        ),
        material=mats["metal"],
        name="operator_flange", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
    )
    shaft_outer_x = op_x - FLANGE_PROUD - SHAFT_LEN
    housing.visual(
        Cylinder(radius=SHAFT_R, length=SHAFT_LEN),
        origin=Origin(
            xyz=(op_x - FLANGE_PROUD - SHAFT_LEN / 2.0, op_y, OP_Z), rpy=(0.0, math.pi / 2.0, 0.0)
        ),
        material=mats["metal"],
        name="operator_shaft", material_class_id=("metal.steel_bare" if r.palette_style in {"industrial_gray", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "metal.blackened_gunmetal"),
    )
    handle = model.part("handle")
    # Hub authored from x=0 (inner face, meets shaft tip) outward to -X.
    handle.visual(
        Cylinder(radius=0.016, length=0.020),
        origin=Origin(xyz=(-0.010, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["control"],
        name="disconnect_handle", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.visual(
        Box((LEVER_TH, LEVER_W, LEVER_LEN)),
        origin=Origin(xyz=(-0.014, 0.0, -LEVER_LEN / 2.0)),
        material=mats["control"],
        name="handle_lever", material_class_id="plastic.opaque_glossy_molded",
    )
    handle.visual(
        Cylinder(radius=0.013, length=0.016),
        origin=Origin(xyz=(-0.014, 0.0, -LEVER_LEN), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["trim"],
        name="handle_grip", material_class_id="rubber.smooth_plain",
    )
    handle.inertial = Inertial.from_geometry(
        Box((0.030, LEVER_W, LEVER_LEN)),
        mass=0.06,
        origin=Origin(xyz=(-0.012, 0.0, -LEVER_LEN / 2.0)),
    )
    model.articulation(
        "operator_handle",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=handle,
        # Origin 1 mm inside the shaft tip so the hub overlaps it (real contact).
        origin=Origin(xyz=(shaft_outer_x + 0.001, op_y, OP_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=HANDLE_THROW),
        mating=MatingContract(
            parent_face_geometry="operator_shaft",
            parent_face_side="negative_x",
            child_face_geometry="disconnect_handle",
            child_face_side="positive_x",
            contact_tol=0.0025,
        ),
    )


_CONTROL_BUILDERS = {
    "round_push_buttons": _control_round_push_buttons,
    "rotary_disconnect_handle": _control_rotary_disconnect_handle,
    "rotary_selector_knob": _control_rotary_selector_knob,
    "toggle_switch_bank": _control_toggle_switch_bank,
    "mushroom_estop": _control_mushroom_estop,
}


# --------------------------------------------------------------------------- #
# READOUT modules (Slot C) — pure housing-fixed visuals (Rule 1), no joints.
# All visuals embed ~0.5mm into the front face so they are never floating
# islands within the housing part.
# --------------------------------------------------------------------------- #
def _readout_none(housing, r: ResolvedControlPanelConfig, mats) -> None:
    return None


def _readout_rect_lcd_with_leds(housing, r: ResolvedControlPanelConfig, mats) -> None:
    cz = r.readout_cz
    dw = min(0.060, r.w * 0.45)
    dh = 0.040
    fy = r.face_y
    housing.visual(
        Box((dw + 0.008, 0.004, dh + 0.008)),
        origin=Origin(xyz=(0.0, fy, cz)),
        material=mats["trim"],
        name="display_bezel", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
    )
    housing.visual(
        Box((dw, 0.005, dh)),
        origin=Origin(xyz=(0.0, fy + 0.0015, cz)),
        material=mats["display"],
        name="display_glass", material_class_id="glass.smoked_tinted",
    )
    for k in (-1, 0, 1):
        housing.visual(
            Sphere(radius=0.0035),
            origin=Origin(xyz=(k * 0.010, fy, cz + dh / 2.0 + 0.008)),
            material=mats["led"],
            name=f"led_{k + 1}", material_class_id="tech.emissive_surface",
        )
    for i in range(4):
        housing.visual(
            Box((0.014, 0.004, 0.0022)),
            origin=Origin(xyz=(-dw / 2.0 - 0.012, fy, cz + 0.006 - i * 0.006)),
            material=mats["trim"],
            name=f"vent_slot_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
        )


def _readout_digital_display_window(housing, r: ResolvedControlPanelConfig, mats) -> None:
    cz = r.readout_cz
    dw = min(0.150, r.w - 0.04)
    dh = 0.060
    fy = r.face_y
    housing.visual(
        Box((dw + 0.010, 0.004, dh + 0.010)),
        origin=Origin(xyz=(0.0, fy, cz)),
        material=mats["trim"],
        name="display_bezel", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
    )
    housing.visual(
        Box((dw, 0.006, dh)),
        origin=Origin(xyz=(0.0, fy + 0.0015, cz)),
        material=mats["display"],
        name="display_glass", material_class_id="glass.smoked_tinted",
    )


def _readout_analog_round_gauge(housing, r: ResolvedControlPanelConfig, mats) -> None:
    cz = r.readout_cz
    fy = r.face_y
    rim_r = 0.022
    face_r = 0.0165
    housing.visual(
        Cylinder(radius=rim_r, length=0.005),
        origin=Origin(xyz=(0.0, fy, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="gauge_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
    )
    housing.visual(
        Cylinder(radius=face_r, length=0.0018),
        origin=Origin(xyz=(0.0, fy + 0.0028, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dial"],
        name="gauge_dial", material_class_id="plastic.opaque_generic",
    )
    for idx in range(11):
        ang = math.radians(-125.0 + idx * (250.0 / 10.0))
        rr = face_r - 0.0025
        housing.visual(
            Box((0.0008, 0.0016, 0.0038)),
            origin=Origin(
                xyz=(rr * math.sin(ang), fy + 0.0036, cz + rr * math.cos(ang)),
                rpy=(0.0, -ang, 0.0),
            ),
            material=mats["trim"],
            name=f"gauge_tick_{idx}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    housing.visual(
        Box((0.0016, 0.0014, 0.011)),
        origin=Origin(xyz=(0.0012, fy + 0.0040, cz + 0.0035), rpy=(0.0, -0.6, 0.0)),
        material=mats["pointer"],
        name="gauge_needle", material_class_id="metal.paint_coated",
    )
    housing.visual(
        Cylinder(radius=0.0020, length=0.0026),
        origin=Origin(xyz=(0.0, fy + 0.0040, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["trim"],
        name="gauge_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
    )


def _readout_lcd_led_vent_cluster(housing, r: ResolvedControlPanelConfig, mats) -> None:
    cz = r.readout_cz
    fy = r.face_y
    dw = min(0.058, r.w * 0.42)
    dh = 0.030
    housing.visual(
        Box((dw + 0.008, 0.004, dh + 0.008)),
        origin=Origin(xyz=(0.0, fy, cz + 0.006)),
        material=mats["trim"],
        name="lcd_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
    )
    housing.visual(
        Box((dw, 0.005, dh)),
        origin=Origin(xyz=(0.0, fy + 0.0015, cz + 0.006)),
        material=mats["display"],
        name="lcd_glass", material_class_id="glass.smoked_tinted",
    )
    for i in range(3):
        housing.visual(
            Sphere(radius=0.0036),
            origin=Origin(xyz=(-0.012 + i * 0.012, fy, cz - dh / 2.0 - 0.004)),
            material=mats["led"],
            name=f"indicator_led_{i}", material_class_id="tech.emissive_surface",
        )
    for i in range(4):
        housing.visual(
            Box((0.0024, 0.004, 0.012)),
            origin=Origin(xyz=(dw / 2.0 + 0.010 + i * 0.0042, fy, cz + 0.006)),
            material=mats["trim"],
            name=f"vent_slot_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"industrial_gray", "cast_steel_dark", "safety_yellow_black", "navy_industrial", "stainless_clean"} else "plastic.opaque_generic"),
        )


_READOUT_BUILDERS = {
    "none": _readout_none,
    "rect_lcd_with_leds": _readout_rect_lcd_with_leds,
    "digital_display_window": _readout_digital_display_window,
    "analog_round_gauge": _readout_analog_round_gauge,
    "lcd_led_vent_cluster": _readout_lcd_led_vent_cluster,
}


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_control_panel(
    config: ControlPanelConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        role: model.material(f"cp_{role}_{r.palette_style}", rgba=rgba)
        for role, rgba in PALETTES[r.palette_style].items()
    }

    housing = model.part("housing")
    _build_housing(housing, r, mats)
    _MOUNT_BUILDERS[r.mount_style](model, r, housing, mats)
    _READOUT_BUILDERS[r.readout_style](housing, r, mats)
    _CONTROL_BUILDERS[r.control_style](model, r, housing, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_control_panel(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_control_panel(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _declare_allowances(ctx, model, r: ResolvedControlPanelConfig) -> None:
    housing = model.get_part("housing")
    # ---- Mount captures / seats. ----
    if r.mount_style == "pendant_rod":
        rod = model.get_part("support_rod")
        for elem in ("housing_shell", "top_gland", "bottom_gland"):
            ctx.allow_overlap(
                housing,
                rod,
                elem_a=elem,
                elem_b="rod_shaft",
                reason="The suspension rod passes captive through the housing and cable glands.",
            )
    elif r.mount_style == "rail_clamp":
        for nm in ("rail_top", "rail_bottom"):
            ctx.allow_overlap(
                housing,
                model.get_part(nm),
                elem_a="rear_clamp",
                elem_b=f"{nm}_bar",
                reason=f"The {nm} is seated in the rear clamp groove.",
            )
    elif r.mount_style == "conduit_wall":
        base = model.get_part("base")
        ctx.allow_overlap(
            base,
            housing,
            elem_a="mount_stud",
            elem_b="housing_shell",
            reason="The conduit back-mount stud bolts into the enclosure rear.",
        )
    elif r.mount_style == "wall_backplate":
        ctx.allow_overlap(
            housing,
            model.get_part("back_plate"),
            reason="The flat back-plate seats flush against the housing rear rim.",
        )
    # ---- Control captures. ----
    if r.control_style == "round_push_buttons":
        for i in range(r.button_count):
            ctx.allow_overlap(
                housing,
                model.get_part(f"button_{i}"),
                elem_a="housing_shell",
                elem_b=f"button_{i}_plunger",
                reason="The button plunger is captured inside the housing bore.",
            )
    elif r.control_style == "rotary_selector_knob":
        ctx.allow_overlap(
            housing,
            model.get_part("selector_knob"),
            elem_a="housing_shell",
            elem_b="selector_stem",
            reason="The selector retaining stem passes back through the panel face.",
        )
    elif r.control_style == "mushroom_estop":
        ctx.allow_overlap(
            housing,
            model.get_part("emergency_stop"),
            elem_a="housing_shell",
            elem_b="safety_guard",
            reason="The e-stop guard seats against / latches into the panel face.",
        )
    elif r.control_style == "toggle_switch_bank":
        for i in range(r.switch_count):
            ctx.allow_overlap(
                housing,
                model.get_part(f"switch_{i}"),
                elem_a="housing_shell",
                elem_b=f"switch_{i}_shank",
                reason="The toggle shank embeds into the panel-face bushing.",
            )
    elif r.control_style == "rotary_disconnect_handle":
        ctx.allow_overlap(
            housing,
            model.get_part("handle"),
            elem_a="operator_shaft",
            elem_b="disconnect_handle",
            reason="The handle hub is captured on the operator shaft it rotates on.",
        )


def run_control_panel_tests(
    object_model: ArticulatedObject,
    config: ControlPanelConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("housing")

    _declare_allowances(ctx, object_model, r)

    # ---- Compiler-owned baseline stack. ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Single connected root. ----
    roots = object_model.root_parts()
    expected_root = {
        "pendant_rod": "support_rod",
        "rail_clamp": "housing",
        "conduit_wall": "base",
        "wall_backplate": "housing",
    }[r.mount_style]
    ctx.check(
        "single root matches the mount style",
        len(roots) == 1 and roots[0].name == expected_root,
        details=f"roots={[p.name for p in roots]} expected={expected_root}",
    )

    # ---- Control hero joint topology + actuation. ----
    if r.control_style == "round_push_buttons":
        j0 = object_model.get_articulation("button_slide_0")
        ctx.check(
            "push buttons are PRISMATIC -Y",
            j0.articulation_type == ArticulationType.PRISMATIC and abs(j0.axis[1]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        ctx.check(
            "button_count parts emitted",
            all(
                any(p.name == f"button_{i}" for p in object_model.parts)
                for i in range(r.button_count)
            ),
            details=f"button_count={r.button_count}",
        )
        btn = object_model.get_part("button_0")
        rest = ctx.part_world_position(btn)
        with ctx.pose({j0: BTN_TRAVEL}):
            pressed = ctx.part_world_position(btn)
        if rest is not None and pressed is not None:
            ctx.check(
                "pressing button_0 moves it into the face (-Y)",
                pressed[1] < rest[1] - 0.0015,
                details=f"rest={rest} pressed={pressed}",
            )
    elif r.control_style == "toggle_switch_bank":
        j0 = object_model.get_articulation("housing_to_switch_0")
        ctx.check(
            "toggles are REVOLUTE +X",
            j0.articulation_type == ArticulationType.REVOLUTE and abs(j0.axis[0]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        ctx.check(
            "switch_count parts emitted",
            all(
                any(p.name == f"switch_{i}" for p in object_model.parts)
                for i in range(r.switch_count)
            ),
            details=f"switch_count={r.switch_count}",
        )
        sw = object_model.get_part("switch_0")
        rest = ctx.part_world_aabb(sw)
        with ctx.pose({j0: SW_THROW}):
            tilted = ctx.part_world_aabb(sw)
        if rest is not None and tilted is not None:
            ctx.check(
                "toggling switch_0 raises the bat tip",
                tilted[1][2] > rest[1][2] + 0.001,
                details=f"rest={rest} tilted={tilted}",
            )
    elif r.control_style == "rotary_selector_knob":
        j = object_model.get_articulation("turn_selector")
        ctx.check(
            "selector knob is REVOLUTE +Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        sel = object_model.get_part("selector_knob")
        rest = ctx.part_element_world_aabb(sel, elem="pointer_mark")
        with ctx.pose({j: KNOB_TURN}):
            turned = ctx.part_element_world_aabb(sel, elem="pointer_mark")
        if rest is not None and turned is not None:
            ctx.check(
                "turning the knob sweeps the pointer mark in X",
                abs(turned[1][0] - rest[1][0]) > 0.002 or abs(turned[0][0] - rest[0][0]) > 0.002,
                details=f"rest={rest} turned={turned}",
            )
    elif r.control_style == "mushroom_estop":
        j = object_model.get_articulation("housing_to_emergency_stop")
        ctx.check(
            "e-stop is PRISMATIC -Y with a deep latch travel",
            j.articulation_type == ArticulationType.PRISMATIC
            and abs(j.axis[1]) > 0.99
            and j.motion_limits is not None
            and j.motion_limits.upper is not None
            and j.motion_limits.upper >= 0.010,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} "
            f"upper={getattr(j.motion_limits, 'upper', None)}",
        )
    else:  # rotary_disconnect_handle
        j = object_model.get_articulation("operator_handle")
        ctx.check(
            "disconnect handle is REVOLUTE +X with a large throw",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[0]) > 0.99
            and j.motion_limits is not None
            and (j.motion_limits.upper - j.motion_limits.lower) > math.radians(80.0),
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        handle = object_model.get_part("handle")
        off = ctx.part_world_aabb(handle)
        with ctx.pose({j: j.motion_limits.upper}):
            on = ctx.part_world_aabb(handle)
        if off is not None and on is not None:
            ctx.check(
                "throwing the handle to ON raises the lever",
                on[1][2] > off[1][2] + 0.02,
                details=f"off={off} on={on}",
            )

    # ---- Readout is pure housing-fixed visuals (no extra parts / joints). ----
    if r.readout_style != "none":
        readout_visuals = {
            "rect_lcd_with_leds": "display_glass",
            "digital_display_window": "display_glass",
            "analog_round_gauge": "gauge_dial",
            "lcd_led_vent_cluster": "lcd_glass",
        }[r.readout_style]
        ctx.check(
            "readout glass/dial is a housing-fixed visual",
            any(v.name == readout_visuals for v in housing.visuals),
            details=f"readout={r.readout_style}",
        )

    # ---- Housing footprint stays a realistic panel envelope. ----
    aabb = ctx.part_world_aabb(housing)
    if aabb is not None:
        x_size = aabb[1][0] - aabb[0][0]
        z_size = aabb[1][2] - aabb[0][2]
        ctx.check(
            "housing reads as a control panel envelope",
            0.12 <= x_size <= 0.70 and 0.16 <= z_size <= 0.34,
            details=f"x={x_size:.4f} z={z_size:.4f}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ControlPanelConfig",
    "ResolvedControlPanelConfig",
    "build_control_panel",
    "build_seeded_control_panel",
    "config_from_seed",
    "resolve_config",
    "run_control_panel_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
