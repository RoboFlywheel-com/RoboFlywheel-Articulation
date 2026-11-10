# SPDX-License-Identifier: Apache-2.0

"""Wall-mounted kitchen chimney range hood (cooker extractor hood) modular template.

NOTE on the slug name: "hood" here = **wall-mounted kitchen chimney range hood /
cooker extractor hood**, NOT a garment hood, an air conditioner (``air_conditioner``
has its own slug), or an air purifier / exhaust fan (``vent`` has its own slug).
The structure family is a wall-mounted extractor canopy: a steel/glass ``canopy``
shell (root, sitting against the wall at y=-0.25, bottom-plate underside at z=0)
with an integrated bottom plate + cavity + duct interface, a head-top telescoping
``chimney`` riding on a fixed ``lower_duct``, a grease ``filter`` in the cavity,
and a front-fascia ``control`` -- plus the **shared defining motion: a blower
``blower_fan`` rotor that spins CONTINUOUS about the vertical axis** (present on
every candidate, behind the filter).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Hood.md`` and the
``picture/Kitchen/Hood`` 5-star sample pool (1 parent + 7 slot-fork variants),
all synced under ``data/records/`` (rating=5).

Structure (pattern = ``mixed``): a single root ``canopy`` part (shell mesh chosen
by ``canopy_form``), with four module axes attaching as parallel children /
inline visuals, plus the always-present blower fan:

  * ``canopy_form`` (3): t_box / pyramid / curved_glass -- the shell mesh
    footprint + the control mounting frame (pyramid uses a sloped front face so
    the control axis/origin/rpy is recomputed -- the A x D coupling).
  * ``chimney`` (2): single_telescope (1 PRISMATIC +Z) / dual_telescope
    (2 PRISMATIC +Z in a linear chain, sleeve_1 parented to sleeve_0).
  * ``filter`` (3): fixed_mesh (inline visual, no joint, Rule 1) / hinged
    (1 REVOLUTE +X flip-down) / dual_baffle (N x FIXED removable baffles).
  * ``filter_count`` (N in [1,4]): a multiplicity axis -- N side-by-side baffle
    panels (FIXED copies on support rails). Only meaningful for dual_baffle;
    fixed_mesh / hinged force N=1. N is encoded into the slot_choice tuple as
    ``("filter_count", f"n{N}")``.
  * ``control`` (3): push_button (1 PRISMATIC into fascia) / rotary_knob
    (1 REVOLUTE about +Y) / slider (1 PRISMATIC along +X).

The ``blower_fan`` CONTINUOUS spin is the shared spine -- it is NOT encoded into
slot_choice (every candidate has it, so it has no discriminating power), but it
guarantees >=1 non-fixed joint on every combination.

All captured interfaces (fan_shaft-in-housing, guide_pad-on-duct,
hinge_knuckle-on-shell, button/knob/slider-stem-through-shell, baffle-on-rail)
are captured-fit / captured-slide / captured-pin geometry, so those joints omit
``MatingContract`` (grandfathered) and are guarded by the flat articulation-origin
baseline + element-scoped ``allow_overlap`` (mirroring each source record's
run_tests block).

Compatibility gating (resolve_config, spec section 9):
  * N>1 only when filter=dual_baffle (fixed_mesh / hinged have no side-by-side
    copy semantics) -> N clamped to 1 otherwise.
  * pyramid x control: pyramid's fascia is a sloped face, so the control
    origin/axis/rpy are recomputed onto the slope (A x D coupling).
  * curved_glass x dual_telescope: the slim body + lower duct top tighten the
    second-stage insertion margin -> chimney travel upper is held lower.

PERFORMANCE: kitchen-appliance meshes can SIGKILL on wall-time. cadquery shells
use raised tessellation tolerance/angular_tolerance, the baffle louver count is
kept coarse, and there is no boolean-union of many small parts.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    FanRotorGeometry,
    FanRotorHub,
    Inertial,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    KnobSkirt,
    LoftSection,
    MotionLimits,
    Origin,
    SectionLoftSpec,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    section_loft,
)

__modular__ = True

CanopyForm = Literal["t_box", "pyramid", "curved_glass"]
Chimney = Literal["single_telescope", "dual_telescope"]
Filter = Literal["fixed_mesh", "hinged", "dual_baffle"]
Control = Literal["push_button", "rotary_knob", "slider"]
PaletteStyle = Literal[
    "brushed_stainless", "glossy_black", "black_glass", "white_steel", "inox_glass"
]

CANOPY_FORMS: tuple[CanopyForm, ...] = ("t_box", "pyramid", "curved_glass")
CHIMNEYS: tuple[Chimney, ...] = ("single_telescope", "dual_telescope")
FILTERS: tuple[Filter, ...] = ("fixed_mesh", "hinged", "dual_baffle")
CONTROLS: tuple[Control, ...] = ("push_button", "rotary_knob", "slider")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_stainless",
    "glossy_black",
    "black_glass",
    "white_steel",
    "inox_glass",
)

N_MIN = 1
N_MAX = 4
# filter_count sampling weights (spec section 8: 1 high-frequency, 2 common,
# 3-4 long tail).
FILTER_COUNT_WEIGHTS = (0.50, 0.30, 0.13, 0.07)

# Raised mesh tolerances keep the appliance meshes light (perf: avoid SIGKILL
# on wall-time). The shell/duct/baffle cadquery solids do not need fine facets.
MESH_TOL = 0.0025
MESH_ANG = 0.45

# ---------------------------------------------------------------------------
# Palettes (per-seed; NOT a slot_choice). Observed across the 5-star pool +
# stainless-family extrapolations.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_stainless": {
        "shell": (0.74, 0.75, 0.77, 1.0),
        "duct": (0.70, 0.71, 0.73, 1.0),
        "filter": (0.20, 0.21, 0.23, 1.0),
        "glass": (0.16, 0.20, 0.24, 0.55),
        "lamp": (1.0, 0.96, 0.80, 1.0),
        "motor": (0.30, 0.31, 0.33, 1.0),
        "fan": (0.44, 0.45, 0.48, 1.0),
        "button": (0.86, 0.87, 0.88, 1.0),
        "logo": (0.78, 0.10, 0.08, 1.0),
        "amber": (0.95, 0.78, 0.18, 1.0),
    },
    "glossy_black": {
        "shell": (0.10, 0.10, 0.11, 1.0),
        "duct": (0.14, 0.14, 0.15, 1.0),
        "filter": (0.06, 0.06, 0.07, 1.0),
        "glass": (0.08, 0.09, 0.10, 0.55),
        "lamp": (1.0, 0.96, 0.80, 1.0),
        "motor": (0.20, 0.20, 0.21, 1.0),
        "fan": (0.30, 0.30, 0.32, 1.0),
        "button": (0.55, 0.56, 0.57, 1.0),
        "logo": (0.85, 0.16, 0.12, 1.0),
        "amber": (0.95, 0.78, 0.18, 1.0),
    },
    "black_glass": {
        "shell": (0.18, 0.18, 0.20, 1.0),
        "duct": (0.22, 0.22, 0.24, 1.0),
        "filter": (0.18, 0.19, 0.21, 1.0),
        "glass": (0.10, 0.13, 0.15, 0.55),
        "lamp": (1.0, 0.96, 0.80, 1.0),
        "motor": (0.26, 0.27, 0.28, 1.0),
        "fan": (0.40, 0.41, 0.43, 1.0),
        "button": (0.72, 0.73, 0.74, 1.0),
        "logo": (0.80, 0.12, 0.10, 1.0),
        "amber": (0.95, 0.78, 0.18, 1.0),
    },
    "white_steel": {
        "shell": (0.92, 0.92, 0.93, 1.0),
        "duct": (0.84, 0.85, 0.86, 1.0),
        "filter": (0.80, 0.81, 0.83, 1.0),
        "glass": (0.62, 0.68, 0.72, 0.55),
        "lamp": (1.0, 0.97, 0.86, 1.0),
        "motor": (0.55, 0.56, 0.58, 1.0),
        "fan": (0.72, 0.73, 0.75, 1.0),
        "button": (0.60, 0.61, 0.62, 1.0),
        "logo": (0.78, 0.10, 0.08, 1.0),
        "amber": (0.95, 0.78, 0.18, 1.0),
    },
    "inox_glass": {
        "shell": (0.70, 0.72, 0.75, 1.0),
        "duct": (0.66, 0.68, 0.71, 1.0),
        "filter": (0.74, 0.76, 0.79, 1.0),
        "glass": (0.40, 0.52, 0.60, 0.50),
        "lamp": (1.0, 0.96, 0.80, 1.0),
        "motor": (0.32, 0.33, 0.35, 1.0),
        "fan": (0.50, 0.51, 0.54, 1.0),
        "button": (0.80, 0.81, 0.83, 1.0),
        "logo": (0.20, 0.36, 0.55, 1.0),
        "amber": (0.95, 0.78, 0.18, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). X = width, Y = depth (wall at y=-0.25),
# Z = up (canopy bottom-plate underside at z=0). All shared with the parent
# (e562777f) baseline unless a canopy_form overrides per-form below.
# ---------------------------------------------------------------------------
# t_box canopy
CANOPY_W = 0.90
CANOPY_D = 0.50
CANOPY_BOX_H = 0.12
SKIRT_H = 0.06
SKIRT_BOT_W = 0.66
SKIRT_BOT_D = 0.38
PLATE_T = 0.005
WALL = 0.003
CANOPY_TOP = SKIRT_H + CANOPY_BOX_H  # 0.18

# pyramid canopy
PYR_H = 0.28
PYR_TOP_W = 0.34
PYR_TOP_D = 0.30
PYR_TOP_CY = -0.10

# curved_glass canopy (slim body + glass visor)
BODY_W = 0.90
BODY_D = 0.20
BODY_H = 0.14
BODY_Z0 = 0.30
BODY_Y_BACK = -0.25
GLASS_T = 0.008
GLASS_CURVE = (
    (-0.05, 0.30),
    (-0.01, 0.26),
    (0.04, 0.21),
    (0.09, 0.16),
    (0.14, 0.11),
    (0.19, 0.07),
    (0.25, 0.04),
)

# Filter cutout / panel (shared)
FILTER_OPEN_W = 0.42
FILTER_OPEN_D = 0.28
FILTER_PANEL_W = 0.46
FILTER_PANEL_D = 0.32
FILTER_PANEL_T = 0.004

# Lamps
LAMP_X = 0.26
LAMP_HOLE_R = 0.035
LAMP_LENS_R = 0.036
LAMP_LENS_T = 0.006

# Chimney duct (shared)
DUCT_Y = -0.10
DUCT_W = 0.32
DUCT_D = 0.28
DUCT_WALL = 0.003
DUCT_HOLE_W = 0.26
DUCT_HOLE_D = 0.22

# Telescoping sleeve (shared). Inner stage = sleeve_0; dual outer = sleeve_1.
SLEEVE_W = 0.336
SLEEVE_D = 0.296
SLEEVE_WALL = 0.005
SLEEVE_LEN = 0.45
SLEEVE2_W = 0.352
SLEEVE2_D = 0.312
SLIDE_TRAVEL = 0.35
PAD_T = 0.004
PAD_Z = 0.035
PAD_LEN = 0.08

# Blower fan
FAN_R = 0.085
FAN_HUB_R = 0.024
FAN_T = 0.016
SHAFT_R = 0.008
SHAFT_LEN = 0.092
HOUSING_R = 0.10

# Buttons / control
BTN_R = 0.006
BTN_LEN = 0.008
BTN_TRAVEL = 0.004

# Knob
KNOB_D = 0.042
KNOB_H = 0.022
KNOB_X = 0.060
ESCUTCHEON_R = 0.026
ESCUTCHEON_T = 0.004
KNOB_OPEN = math.radians(270.0)

# Slider
SLIDER_TRACK_W = 0.080
SLIDER_TRACK_H = 0.010
SLIDER_TRACK_DEPTH = 0.003
SLIDER_TAB_W = 0.022
SLIDER_TAB_H = 0.014
SLIDER_TAB_D = 0.008
SLIDER_STEM_W = 0.010
SLIDER_STEM_H = 0.008
SLIDER_STEM_LEN = 0.006
SLIDER_TRAVEL = 0.060

# Baffle filter (dual_baffle / multiplicity)
BAFFLE_W = 0.210
BAFFLE_D = 0.300
BAFFLE_T = 0.016
BAFFLE_GAP = 0.012
BAFFLE_FRAME = 0.008
BAFFLE_PLATE_T = 0.001
RAIL_W = 0.010
RAIL_T = 0.003


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config / ResolvedConfig
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class HoodConfig:
    canopy_form: CanopyForm | None = None
    chimney: Chimney | None = None
    filter: Filter | None = None
    control: Control | None = None
    filter_count: int | None = None
    palette_style: PaletteStyle = "brushed_stainless"
    canopy_width_scale: float = 1.0
    canopy_depth_scale: float = 1.0
    canopy_height_scale: float = 1.0
    chimney_travel_scale: float = 1.0
    fan_radius_scale: float = 1.0
    hinge_open_angle_scale: float = 1.0
    knob_open_angle_scale: float = 1.0
    slider_travel_scale: float = 1.0
    button_travel_scale: float = 1.0
    baffle_spacing_scale: float = 1.0
    name: str = "hood"


@dataclass(frozen=True)
class ResolvedHoodConfig:
    canopy_form: CanopyForm
    chimney: Chimney
    filter: Filter
    control: Control
    filter_count: int
    palette_style: PaletteStyle
    # Scales (clamped).
    width_scale: float
    depth_scale: float
    height_scale: float
    chimney_travel: float  # per-stage prismatic upper
    fan_r: float
    hinge_open: float
    knob_open: float
    slider_travel: float
    button_travel: float
    baffle_pitch: float
    baffle_w: float
    baffle_d: float
    # Derived geometry shared across forms.
    fascia_front_y: float  # control mounting plane Y (vertical-face forms)
    fan_cy: float  # fan center Y (curved_glass mounts behind the slim body)
    fan_z: float
    name: str

    @property
    def is_curved(self) -> bool:
        return self.canopy_form == "curved_glass"

    @property
    def is_pyramid(self) -> bool:
        return self.canopy_form == "pyramid"


def config_from_seed(seed: int) -> HoodConfig:
    rng = random.Random(seed)
    return HoodConfig(
        canopy_form=rng.choice(CANOPY_FORMS),
        chimney=rng.choice(CHIMNEYS),
        filter=rng.choice(FILTERS),
        control=rng.choice(CONTROLS),
        filter_count=rng.choices((1, 2, 3, 4), weights=FILTER_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        canopy_width_scale=round(rng.uniform(0.85, 1.15), 4),
        canopy_depth_scale=round(rng.uniform(0.88, 1.12), 4),
        canopy_height_scale=round(rng.uniform(0.88, 1.15), 4),
        chimney_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        fan_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        hinge_open_angle_scale=round(rng.uniform(0.85, 1.05), 4),
        knob_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        slider_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        button_travel_scale=round(rng.uniform(0.80, 1.20), 4),
        baffle_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_hood_{seed}",
    )


def resolve_config(config: HoodConfig | None = None) -> ResolvedHoodConfig:
    cfg = config or HoodConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    canopy_form = _pick(cfg.canopy_form, CANOPY_FORMS)
    chimney = _pick(cfg.chimney, CHIMNEYS)
    filt = _pick(cfg.filter, FILTERS)
    control = _pick(cfg.control, CONTROLS)

    filter_count = int(cfg.filter_count) if cfg.filter_count is not None else 1
    filter_count = int(_clamp(filter_count, N_MIN, N_MAX))

    # --- Compatibility gating (spec section 9). ---
    # (1) N>1 only with dual_baffle: fixed_mesh / hinged are single filters.
    if filt != "dual_baffle":
        filter_count = 1

    width_scale = _clamp(cfg.canopy_width_scale, 0.85, 1.15)
    depth_scale = _clamp(cfg.canopy_depth_scale, 0.88, 1.12)
    height_scale = _clamp(cfg.canopy_height_scale, 0.88, 1.15)
    travel_scale = _clamp(cfg.chimney_travel_scale, 0.85, 1.15)
    fan_scale = _clamp(cfg.fan_radius_scale, 0.90, 1.10)
    hinge_scale = _clamp(cfg.hinge_open_angle_scale, 0.85, 1.05)
    knob_scale = _clamp(cfg.knob_open_angle_scale, 0.85, 1.10)
    slider_scale = _clamp(cfg.slider_travel_scale, 0.85, 1.10)
    button_scale = _clamp(cfg.button_travel_scale, 0.80, 1.20)
    spacing_scale = _clamp(cfg.baffle_spacing_scale, 0.90, 1.10)

    # --- Per-form fan baseline + mounting plane. ---
    if canopy_form == "curved_glass":
        fan_r_base = 0.050
        fan_cy = (BODY_Y_BACK + (BODY_Y_BACK + BODY_D)) / 2.0  # -0.15
        fan_z = BODY_Z0 + 0.035
        # Track the body's DEPTH-SCALED front face (not the nominal one) so the
        # control mounting plane stays on the actual wall and static front
        # decorations embed into it (else they float when depth_scale != 1).
        fascia_front_y = (BODY_Y_BACK + BODY_D * depth_scale) + 0.001  # body front face
    elif canopy_form == "pyramid":
        fan_r_base = 0.085
        fan_cy = 0.0
        fan_z = 0.045
        fascia_front_y = CANOPY_D / 2.0  # nominal; control recomputed onto slope
    else:  # t_box
        fan_r_base = 0.085
        fan_cy = 0.0
        fan_z = 0.045
        fascia_front_y = (CANOPY_D * depth_scale) / 2.0
    fan_r = fan_r_base * fan_scale

    # --- chimney travel: curved_glass x dual_telescope tightens insertion. ---
    chimney_travel = SLIDE_TRAVEL * travel_scale
    if canopy_form == "curved_glass" and chimney == "dual_telescope":
        chimney_travel = min(chimney_travel, SLIDE_TRAVEL)

    hinge_open = _clamp((math.pi / 2.0) * hinge_scale, 1.0, math.pi * 0.55)
    knob_open = _clamp(KNOB_OPEN * knob_scale, 1.0, math.pi * 1.6)
    slider_travel = _clamp(SLIDER_TRAVEL * slider_scale, 0.040, 0.075)
    button_travel = _clamp(BTN_TRAVEL * button_scale, 0.0025, 0.006)

    # --- baffle width + pitch: N baffles must fit inside the bottom-plate
    # filter opening (curved_glass uses a depth-limited 0.12 opening, so its
    # baffle depth is clamped too). Baffle width shrinks with N so the row sits
    # entirely within the opening (no poking under the solid plate). ---
    n = filter_count
    open_w = FILTER_OPEN_W
    open_d = FILTER_OPEN_D if canopy_form != "curved_glass" else 0.12
    margin = 0.010
    usable_w = open_w - 2.0 * margin
    # Per-baffle width = usable / N minus an inter-baffle gap.
    gap = BAFFLE_GAP * spacing_scale
    baffle_w = (usable_w - (n - 1) * gap) / n
    baffle_w = _clamp(baffle_w, 0.045, BAFFLE_W)
    baffle_d = _clamp(open_d - 2.0 * margin, 0.060, BAFFLE_D)
    baffle_pitch = baffle_w + gap

    return ResolvedHoodConfig(
        canopy_form=canopy_form,
        chimney=chimney,
        filter=filt,
        control=control,
        filter_count=filter_count,
        palette_style=palette_style,
        width_scale=width_scale,
        depth_scale=depth_scale,
        height_scale=height_scale,
        chimney_travel=chimney_travel,
        fan_r=fan_r,
        hinge_open=hinge_open,
        knob_open=knob_open,
        slider_travel=slider_travel,
        button_travel=button_travel,
        baffle_pitch=baffle_pitch,
        baffle_w=baffle_w,
        baffle_d=baffle_d,
        fascia_front_y=fascia_front_y,
        fan_cy=fan_cy,
        fan_z=fan_z,
        name=cfg.name or "hood",
    )


def with_overrides(config: HoodConfig, **kwargs: object) -> HoodConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: HoodConfig | ResolvedHoodConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedHoodConfig) else resolve_config(config)
    return (
        ("canopy_form", r.canopy_form),
        ("chimney", r.chimney),
        ("filter", r.filter),
        ("control", r.control),
        ("filter_count", f"n{r.filter_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Pyramid front-face geometry (A x D coupling). The sloped front face's inward
# normal carries the control axis; _front_y_at_z interpolates the surface Y.
# ---------------------------------------------------------------------------
class _PyramidFace:
    """Resolved sloped-front-face math for a (possibly scaled) pyramid."""

    def __init__(self, r: ResolvedHoodConfig):
        self.h = PYR_H * r.height_scale
        self.bottom_d = CANOPY_D * r.depth_scale
        top_front_y = PYR_TOP_CY + PYR_TOP_D / 2.0  # +0.05
        self.front_dy = top_front_y - self.bottom_d / 2.0  # negative (setback)
        face_len = math.sqrt(self.front_dy**2 + self.h**2)
        self.front_ny = self.h / face_len
        self.front_nz = -self.front_dy / face_len
        self.tilt_from_y = math.atan2(-self.front_dy, self.h)
        self.tilt_from_z = math.pi / 2.0 - self.tilt_from_y

    def front_y_at_z(self, z: float) -> float:
        return self.bottom_d / 2.0 + (z / self.h) * self.front_dy


# ---------------------------------------------------------------------------
# cadquery shell helpers (canopy_form). Raised mesh tolerances keep meshes light.
# ---------------------------------------------------------------------------
def _rect_tube(width: float, depth: float, wall: float, length: float) -> cq.Workplane:
    """Open-ended thin-walled rectangular duct along +Z (z 0..length)."""
    outer = cq.Workplane("XY").rect(width, depth).extrude(length)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=-0.01)
        .rect(width - 2 * wall, depth - 2 * wall)
        .extrude(length + 0.02)
    )
    return outer.cut(inner)


def _t_box_shell(r: ResolvedHoodConfig) -> cq.Workplane:
    """Hollow t_box canopy: tapered skirt + fascia box + integrated bottom plate."""
    w = CANOPY_W * r.width_scale
    d = CANOPY_D * r.depth_scale
    box_h = CANOPY_BOX_H * r.height_scale
    skirt_h = SKIRT_H * r.height_scale
    sk_bw = SKIRT_BOT_W * r.width_scale
    sk_bd = SKIRT_BOT_D * r.depth_scale
    canopy_top = skirt_h + box_h
    outer = (
        cq.Workplane("XY")
        .rect(sk_bw, sk_bd)
        .workplane(offset=skirt_h)
        .rect(w, d)
        .workplane(offset=box_h)
        .rect(w, d)
        .loft(ruled=True)
    )
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=PLATE_T)
        .rect(sk_bw - 0.012, sk_bd - 0.012)
        .workplane(offset=skirt_h - PLATE_T + 0.0005)
        .rect(w - 2 * WALL, d - 2 * WALL)
        .workplane(offset=box_h - WALL - 0.0005)
        .rect(w - 2 * WALL, d - 2 * WALL)
        .loft(ruled=True)
    )
    shell = outer.cut(cavity)
    shell = shell.cut(
        cq.Workplane("XY").workplane(offset=-0.01).rect(FILTER_OPEN_W, FILTER_OPEN_D).extrude(0.03)
    )
    for sx in (-1.0, 1.0):
        shell = shell.cut(
            cq.Workplane("XY")
            .workplane(offset=-0.01)
            .center(sx * LAMP_X, 0.0)
            .circle(LAMP_HOLE_R)
            .extrude(0.03)
        )
    shell = shell.cut(
        cq.Workplane("XY")
        .workplane(offset=canopy_top - 0.01)
        .center(0.0, DUCT_Y)
        .rect(DUCT_HOLE_W, DUCT_HOLE_D)
        .extrude(0.02)
    )
    return shell


def _pyramid_shell(r: ResolvedHoodConfig) -> cq.Workplane:
    """Hollow truncated-pyramid canopy shell with bottom plate + cutouts."""
    w = CANOPY_W * r.width_scale
    d = CANOPY_D * r.depth_scale
    h = PYR_H * r.height_scale
    outer = (
        cq.Workplane("XY")
        .rect(w, d)
        .workplane(offset=h)
        .center(0.0, PYR_TOP_CY)
        .rect(PYR_TOP_W, PYR_TOP_D)
        .loft(ruled=True)
    )
    cavity_h = h - PLATE_T - WALL
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=PLATE_T)
        .rect(w - 2 * WALL, d - 2 * WALL)
        .workplane(offset=cavity_h)
        .center(0.0, PYR_TOP_CY)
        .rect(PYR_TOP_W - 2 * WALL, PYR_TOP_D - 2 * WALL)
        .loft(ruled=True)
    )
    shell = outer.cut(cavity)
    shell = shell.cut(
        cq.Workplane("XY").workplane(offset=-0.01).rect(FILTER_OPEN_W, FILTER_OPEN_D).extrude(0.03)
    )
    for sx in (-1.0, 1.0):
        shell = shell.cut(
            cq.Workplane("XY")
            .workplane(offset=-0.01)
            .center(sx * LAMP_X, 0.0)
            .circle(LAMP_HOLE_R)
            .extrude(0.03)
        )
    shell = shell.cut(
        cq.Workplane("XY")
        .workplane(offset=h - 0.01)
        .center(0.0, DUCT_Y)
        .rect(DUCT_HOLE_W, DUCT_HOLE_D)
        .extrude(0.02)
    )
    return shell


def _metal_body_shell(r: ResolvedHoodConfig) -> cq.Workplane:
    """Hollow slim stainless body (curved_glass), centered at local origin."""
    w = BODY_W * r.width_scale
    d = BODY_D * r.depth_scale
    h = BODY_H * r.height_scale
    outer = cq.Workplane("XY").box(w, d, h)
    cavity = cq.Workplane("XY").box(w - 2 * WALL, d - 2 * WALL, h - 2 * WALL)
    body = outer.cut(cavity)
    body = body.cut(
        cq.Workplane("XY")
        .workplane(offset=-h / 2.0 - 0.01)
        .rect(FILTER_OPEN_W, 0.12)
        .extrude(WALL + 0.02)
    )
    for sx in (-1.0, 1.0):
        body = body.cut(
            cq.Workplane("XY")
            .workplane(offset=-h / 2.0 - 0.01)
            .center(sx * 0.30, 0.0)
            .circle(0.028)
            .extrude(WALL + 0.02)
        )
    body = body.cut(
        cq.Workplane("XY").workplane(offset=h / 2.0 - 0.01).rect(DUCT_HOLE_W, DUCT_HOLE_D).extrude(0.02)
    )
    return body


def _glass_visor_geometry(r: ResolvedHoodConfig):
    """Curved tempered-glass visor as a section loft following the concave YZ
    curve. Width scales with the body; the curve profile is fixed."""
    hw = (BODY_W * r.width_scale) / 2.0
    ht = GLASS_T / 2.0
    n = len(GLASS_CURVE)
    sections = []
    for i in range(n):
        y, z = GLASS_CURVE[i]
        if i < n - 1:
            dy = GLASS_CURVE[i + 1][0] - y
            dz = GLASS_CURVE[i + 1][1] - z
        else:
            dy = y - GLASS_CURVE[i - 1][0]
            dz = z - GLASS_CURVE[i - 1][1]
        length = math.sqrt(dy * dy + dz * dz)
        ty, tz = dy / length, dz / length
        ny, nz = -tz, ty
        pts = (
            (-hw, y + ny * ht, z + nz * ht),
            (hw, y + ny * ht, z + nz * ht),
            (hw, y - ny * ht, z - nz * ht),
            (-hw, y - ny * ht, z - nz * ht),
        )
        sections.append(LoftSection(points=tuple(pts)))
    return section_loft(SectionLoftSpec(sections=tuple(sections), cap=True, solid=True))


# ---------------------------------------------------------------------------
# Canopy (root). Shared inline decorations + form-specific shell.
# ---------------------------------------------------------------------------
def _canopy_top_z(r: ResolvedHoodConfig) -> float:
    """Z of the canopy top plate (duct seats here) for the active form."""
    if r.canopy_form == "curved_glass":
        return BODY_Z0 + BODY_H * r.height_scale
    if r.canopy_form == "pyramid":
        return PYR_H * r.height_scale
    return (SKIRT_H + CANOPY_BOX_H) * r.height_scale


def _bottom_plate_z(r: ResolvedHoodConfig) -> float:
    """Z of the bottom-plate top surface where the filter / lamps recess sit."""
    if r.canopy_form == "curved_glass":
        return BODY_Z0 + WALL
    return PLATE_T


def _build_canopy(model: ArticulatedObject, r: ResolvedHoodConfig, mats) -> ArticulatedObject:
    canopy = model.part("canopy")
    body_cy = r.fan_cy if r.canopy_form == "curved_glass" else 0.0
    canopy_top = _canopy_top_z(r)
    plate_z = _bottom_plate_z(r)

    # --- form-specific shell mesh ---
    if r.canopy_form == "t_box":
        canopy.visual(
            mesh_from_cadquery(
                _t_box_shell(r), "canopy_shell", tolerance=MESH_TOL, angular_tolerance=MESH_ANG
            ),
            material=mats["shell"],
            name="canopy_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
        )
    elif r.canopy_form == "pyramid":
        canopy.visual(
            mesh_from_cadquery(
                _pyramid_shell(r), "canopy_shell", tolerance=MESH_TOL, angular_tolerance=MESH_ANG
            ),
            material=mats["shell"],
            name="canopy_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
        )
    else:  # curved_glass: slim body + glass visor (body named "canopy_shell"
        # so captured allow_overlaps + tests reference one shell name everywhere).
        canopy.visual(
            mesh_from_cadquery(
                _metal_body_shell(r), "canopy_shell", tolerance=MESH_TOL, angular_tolerance=MESH_ANG
            ),
            origin=Origin(xyz=(0.0, body_cy, BODY_Z0 + BODY_H * r.height_scale / 2.0)),
            material=mats["shell"],
            name="canopy_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
        )
        # Anchor the (fixed-profile) glass visor to the body's scaled front face:
        # when depth_scale<1 the body recedes but the GLASS_CURVE back stays at
        # -0.05, opening a gap that splits the assembly into two clusters. Offset
        # the visor in Y so its back edge always embeds into the body front wall.
        body_front = BODY_Y_BACK + BODY_D * r.depth_scale
        visor_dy = (body_front - WALL / 2.0) - GLASS_CURVE[0][0]
        canopy.visual(
            mesh_from_geometry(_glass_visor_geometry(r), "glass_visor"),
            origin=Origin(xyz=(0.0, visor_dy, 0.0)),
            material=mats["glass"],
            name="glass_visor", material_class_id=("glass.smoked_tinted" if r.palette_style in {"brushed_stainless", "glossy_black", "black_glass", "inox_glass"} else "glass.clear_transparent"),
        )
        # Front-fascia connective spine: one solid bar embedded across the body
        # front wall, spanning the full body height. It physically unifies the
        # otherwise-fragile slim-body cluster -- the body wall, the visor top
        # edge, the lamps, and every front-mounted decoration/control all embed
        # into it, so the curved_glass canopy is one connected solid (no
        # cascading islands under the strict mesh-connectivity gate).
        body_h = BODY_H * r.height_scale
        # The spine embeds into the front wall (flush, NOT proud, so it never
        # collides the proud moving controls) and unifies the slim-body cluster:
        # body wall + visor top + lamps + the static front decorations all reach
        # it. Static front items are themselves embedded into the wall (below).
        canopy.visual(
            Box((BODY_W * r.width_scale - 0.02, 0.012, body_h)),
            origin=Origin(
                xyz=(0.0, body_front - 0.004, BODY_Z0 + body_h / 2.0)
            ),
            material=mats["shell"],
            name="fascia_spine", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
        )

    # --- fixed lower chimney duct (rises to ~1.07 m). ---
    duct_top = 1.07
    duct_z0 = canopy_top - 0.002
    duct_len = max(0.40, duct_top - duct_z0)
    canopy.visual(
        mesh_from_cadquery(
            _rect_tube(DUCT_W, DUCT_D, DUCT_WALL, duct_len),
            "lower_duct",
            tolerance=MESH_TOL,
            angular_tolerance=MESH_ANG,
        ),
        origin=Origin(xyz=(0.0, DUCT_Y, duct_z0)),
        material=mats["duct"],
        name="lower_duct", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
    )
    # --- duct centering boss at the sleeve seat plane: a thin solid spider that
    # anchors the canopy->sleeve_0 PRISMATIC joint origin (0, DUCT_Y, seat_z) on
    # real geometry (the hollow duct center would otherwise leave the origin in
    # air). The sleeve slides up away from it for q>0. ---
    # The boss spans the full duct interior so its X ends butt against the duct
    # inner walls (a boundary touch -> connected, not an island).
    seat_z = _sleeve_seat_z(r)
    canopy.visual(
        Box((DUCT_W - 2 * DUCT_WALL + 0.001, DUCT_WALL * 2.0, 0.012)),
        origin=Origin(xyz=(0.0, DUCT_Y, seat_z)),
        material=mats["duct"],
        name="duct_centering_boss", material_class_id="metal.blackened_gunmetal",
    )

    # --- two recessed LED lamps near the outer ends. ---
    for i, sx in enumerate((-1.0, 1.0)):
        canopy.visual(
            Cylinder(radius=LAMP_LENS_R, length=LAMP_LENS_T),
            origin=Origin(xyz=(sx * LAMP_X, body_cy, plate_z + 0.002)),
            material=mats["lamp"],
            name=f"lamp_lens_{i}", material_class_id="tech.emissive_surface",
        )

    # --- blower motor housing hanging from the canopy top plate. ---
    # The housing must sit ABOVE the filter/baffle plane: for curved_glass the
    # bottom plate is high (z~0.30), so a housing dropped to the plate would
    # interpenetrate the recessed baffles. Hang it down only to just above the
    # fan rotor (which is above the filter), keeping the captured fan_shaft
    # overlap intact.
    if r.canopy_form == "curved_glass":
        housing_z0 = r.fan_z + FAN_T / 2.0 + 0.006
    else:
        housing_z0 = 0.105
    housing_z1 = canopy_top - 0.001
    canopy.visual(
        Cylinder(radius=HOUSING_R if r.canopy_form != "curved_glass" else 0.06,
                 length=max(0.02, housing_z1 - housing_z0)),
        origin=Origin(xyz=(0.0, body_cy, (housing_z0 + housing_z1) / 2.0)),
        material=mats["motor"],
        name="motor_housing", material_class_id="metal.blackened_gunmetal",
    )
    # For curved_glass the housing hangs in the slim-body cavity directly under
    # the exhaust hole (the top wall is cut away there), so it would otherwise
    # float. Add a mounting web that spans from the housing OUT to the surviving
    # top-wall material on both sides of the exhaust hole (|X| > DUCT_HOLE_W/2),
    # tying the motor cluster into the body solid.
    if r.canopy_form == "curved_glass":
        web_z = housing_z1 - 0.006
        web_span = DUCT_HOLE_W + 0.06  # reach ~0.03 past the hole edge into wall
        canopy.visual(
            Box((web_span, 0.020, 0.010)),
            origin=Origin(xyz=(0.0, body_cy, web_z)),
            material=mats["motor"],
            name="motor_mount_web", material_class_id="metal.blackened_gunmetal",
        )
    # --- motor spindle stub reaching down from the housing to the fan plane,
    # so the fan joint origin (0, fan_cy, fan_z) lands on real parent geometry
    # (the rotor hub spins on this spindle). ---
    spindle_top = housing_z0 + 0.005
    spindle_len = max(0.02, spindle_top - r.fan_z + 0.006)
    canopy.visual(
        Cylinder(radius=SHAFT_R + 0.003, length=spindle_len),
        origin=Origin(xyz=(0.0, body_cy, spindle_top - spindle_len / 2.0)),
        material=mats["motor"],
        name="motor_spindle", material_class_id="metal.blackened_gunmetal",
    )

    # --- small brand logo + amber indicator (inline, on the fascia plane). ---
    _emit_fascia_marks(canopy, r, mats)

    canopy.inertial = Inertial.from_geometry(
        Box((CANOPY_W * r.width_scale, CANOPY_D * r.depth_scale, max(0.12, canopy_top))),
        mass=6.0,
        origin=Origin(xyz=(0.0, body_cy, canopy_top / 2.0)),
    )
    return canopy


def _emit_fascia_marks(canopy, r: ResolvedHoodConfig, mats) -> None:
    """Brand logo + amber indicator, placed on the active form's front face."""
    if r.canopy_form == "pyramid":
        face = _PyramidFace(r)
        logo_z = 0.15
        logo_y = face.front_y_at_z(logo_z) + 0.001
        canopy.visual(
            Box((0.040, 0.002, 0.011)),
            origin=Origin(xyz=(0.0, logo_y, logo_z), rpy=(face.tilt_from_y, 0.0, 0.0)),
            material=mats["logo"],
            name="brand_logo", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        ind_z = 0.08
        ind_y = face.front_y_at_z(ind_z) + 0.001
        canopy.visual(
            Box((0.008, 0.002, 0.008)),
            origin=Origin(xyz=(-0.055, ind_y, ind_z), rpy=(face.tilt_from_y, 0.0, 0.0)),
            material=mats["amber"],
            name="indicator_lamp", material_class_id="tech.emissive_surface",
        )
        return
    if r.canopy_form == "curved_glass":
        # Embed the marks INTO the slim-body front wall (thickness WALL) so they
        # reliably contact the body solid (avoid hair-gap islands), still proud.
        front_y = (BODY_Y_BACK + BODY_D * r.depth_scale) - WALL / 2.0
        logo_z = BODY_Z0 + 0.10
        ind_z = BODY_Z0 + BODY_H * r.height_scale / 2.0
    else:
        front_y = (CANOPY_D * r.depth_scale) / 2.0 + 0.0005
        logo_z = SKIRT_H + 0.088
        ind_z = SKIRT_H + 0.055
    canopy.visual(
        Box((0.040, 0.002, 0.011)),
        origin=Origin(xyz=(0.0, front_y, logo_z)),
        material=mats["logo"],
        name="brand_logo", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    canopy.visual(
        Box((0.008, 0.002, 0.008)),
        origin=Origin(xyz=(-0.055, front_y, ind_z)),
        material=mats["amber"],
        name="indicator_lamp", material_class_id="tech.emissive_surface",
    )


# ---------------------------------------------------------------------------
# Shared blower fan (CONTINUOUS spin) -- the defining motion, every candidate.
# ---------------------------------------------------------------------------
def _build_blower_fan(model: ArticulatedObject, r: ResolvedHoodConfig, canopy, mats) -> None:
    fan = model.part("blower_fan")
    rotor_geom = FanRotorGeometry(
        r.fan_r,
        min(FAN_HUB_R, r.fan_r * 0.5),
        6,
        thickness=FAN_T,
        blade_pitch_deg=30.0,
        blade_sweep_deg=22.0,
        hub=FanRotorHub(style="capped"),
    )
    fan.visual(mesh_from_geometry(rotor_geom, "fan_rotor"), material=mats["fan"], name="fan_rotor", material_class_id=("metal.aluminum_bare" if r.palette_style in {"brushed_stainless", "white_steel", "inox_glass"} else "metal.blackened_gunmetal"))
    shaft_len = SHAFT_LEN if r.canopy_form != "curved_glass" else 0.065
    fan.visual(
        Cylinder(radius=SHAFT_R, length=shaft_len),
        origin=Origin(xyz=(0.0, 0.0, shaft_len / 2.0)),
        material=mats["motor"],
        name="fan_shaft", material_class_id="metal.blackened_gunmetal",
    )
    fan.inertial = Inertial.from_geometry(
        Cylinder(radius=r.fan_r, length=FAN_T),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    model.articulation(
        "canopy_to_blower_fan",
        ArticulationType.CONTINUOUS,
        parent=canopy,
        child=fan,
        origin=Origin(xyz=(0.0, r.fan_cy, r.fan_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=30.0),
    )


# ---------------------------------------------------------------------------
# Chimney slot.
# ---------------------------------------------------------------------------
def _sleeve_seat_z(r: ResolvedHoodConfig) -> float:
    """Sleeve bottom-seat Z at q=0. Curved_glass seats higher (lower duct top)."""
    return 0.72 if r.canopy_form == "curved_glass" else 0.65


def _emit_sleeve_stage(
    model, r, *, stage_idx, parent_part, parent_ow, parent_od, joint_name, joint_origin, mats
):
    if stage_idx == 0:
        sw, sd = SLEEVE_W, SLEEVE_D
    else:
        sw, sd = SLEEVE2_W, SLEEVE2_D
    sleeve = model.part(f"sleeve_{stage_idx}")
    sleeve.visual(
        mesh_from_cadquery(
            _rect_tube(sw, sd, SLEEVE_WALL, SLEEVE_LEN),
            f"sleeve_shell_{stage_idx}",
            tolerance=MESH_TOL,
            angular_tolerance=MESH_ANG,
        ),
        material=mats["shell"],
        name=f"sleeve_shell_{stage_idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
    )
    inner_w = sw - 2 * SLEEVE_WALL
    inner_d = sd - 2 * SLEEVE_WALL
    pad_x = (inner_w / 2.0 + parent_ow / 2.0) / 2.0
    pad_y = (inner_d / 2.0 + parent_od / 2.0) / 2.0
    pad_specs = (
        ((pad_x, 0.0, PAD_Z), (PAD_T, PAD_LEN, 0.03)),
        ((-pad_x, 0.0, PAD_Z), (PAD_T, PAD_LEN, 0.03)),
        ((0.0, pad_y, PAD_Z), (PAD_LEN, PAD_T, 0.03)),
        ((0.0, -pad_y, PAD_Z), (PAD_LEN, PAD_T, 0.03)),
    )
    for j, (pxyz, psize) in enumerate(pad_specs):
        sleeve.visual(
            Box(psize), origin=Origin(xyz=pxyz), material=mats["motor"], name=f"guide_pad_{stage_idx}_{j}", material_class_id="rubber.smooth_plain"
        )
    # Centering boss at the sleeve base (local z=0): a thin solid cross-strip
    # that anchors this sleeve's PRISMATIC joint origin (which is at the sleeve
    # base, the hollow tube center) on real geometry for both the parent and
    # the child distance checks.
    # Boss spans the sleeve interior so its X ends butt the sleeve inner walls
    # (boundary touch -> connected, not an island).
    sleeve.visual(
        Box((inner_w + 0.001, SLEEVE_WALL * 2.0, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material=mats["motor"],
        name=f"sleeve_centering_boss_{stage_idx}", material_class_id="metal.blackened_gunmetal",
    )
    sleeve.inertial = Inertial.from_geometry(
        Box((sw, sd, SLEEVE_LEN)), mass=0.8, origin=Origin(xyz=(0.0, 0.0, SLEEVE_LEN / 2.0))
    )
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=parent_part,
        child=sleeve,
        origin=joint_origin,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.2, lower=0.0, upper=r.chimney_travel),
    )
    return sleeve


def _build_chimney(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    seat_z = _sleeve_seat_z(r)
    if r.chimney == "single_telescope":
        _emit_sleeve_stage(
            model, r, stage_idx=0, parent_part=canopy, parent_ow=DUCT_W, parent_od=DUCT_D,
            joint_name="canopy_to_sleeve_0", joint_origin=Origin(xyz=(0.0, DUCT_Y, seat_z)), mats=mats,
        )
    else:  # dual_telescope: PRISMATIC linear chain, sleeve_1 parented to sleeve_0.
        s0 = _emit_sleeve_stage(
            model, r, stage_idx=0, parent_part=canopy, parent_ow=DUCT_W, parent_od=DUCT_D,
            joint_name="canopy_to_sleeve_0", joint_origin=Origin(xyz=(0.0, DUCT_Y, seat_z)), mats=mats,
        )
        _emit_sleeve_stage(
            model, r, stage_idx=1, parent_part=s0, parent_ow=SLEEVE_W, parent_od=SLEEVE_D,
            joint_name="sleeve_0_to_sleeve_1", joint_origin=Origin(xyz=(0.0, 0.0, 0.0)), mats=mats,
        )


# ---------------------------------------------------------------------------
# Filter slot.
# ---------------------------------------------------------------------------
def _slotted_filter_panel_cq(w: float, d: float, t: float, nx: int = 8, ny: int = 6) -> cq.Workplane:
    """Slotted aluminium grease-filter panel: a thin frame box with a coarse
    grid of rectangular slot cuts (the recessed-slot grease-mesh look). Built
    centered at origin. Uses a single pushPoints extrude+cut so the slot count
    stays light on wall-time (perf)."""
    frame = 0.014
    iw = w - 2 * frame
    idp = d - 2 * frame
    panel = cq.Workplane("XY").box(w, d, t)
    sx = iw / nx
    sy = idp / ny
    sw = sx * 0.62
    sd = sy * 0.55
    centers = [
        (-iw / 2.0 + (i + 0.5) * sx, -idp / 2.0 + (j + 0.5) * sy)
        for i in range(nx)
        for j in range(ny)
    ]
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=-t / 2.0 - 0.01)
        .pushPoints(centers)
        .rect(sw, sd)
        .extrude(t + 0.02)
    )
    return panel.cut(cutter)


def _emit_fixed_mesh(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    """fixed_mesh: a single inline filter panel (Rule 1, no joint)."""
    body_cy = r.fan_cy if r.canopy_form == "curved_glass" else 0.0
    plate_z = _bottom_plate_z(r)
    canopy.visual(
        mesh_from_cadquery(
            _slotted_filter_panel_cq(FILTER_PANEL_W, FILTER_PANEL_D, FILTER_PANEL_T),
            "filter_mesh_panel",
            tolerance=MESH_TOL,
            angular_tolerance=MESH_ANG,
        ),
        origin=Origin(xyz=(0.0, body_cy, plate_z + FILTER_PANEL_T / 2.0 + 0.001)),
        material=mats["filter"],
        name="filter_mesh_panel", material_class_id="metal.mesh_chainmail",
    )


def _emit_hinged_filter(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    """hinged: a grease_filter panel that flips down on a +X REVOLUTE hinge.

    The part frame sits on the front hinge line; the panel extends in -Y.
    """
    plate_z = _bottom_plate_z(r)
    # The filter opening (and therefore the panel + hinge line) must fit the
    # active form's bottom plate. curved_glass has a slim body centered at
    # body_cy with a shallow 0.12-deep opening, so the panel is depth-limited
    # and the hinge line is anchored at the front edge of THAT opening (mirrors
    # _emit_fixed_mesh / _emit_dual_baffle). t_box / pyramid keep the full-depth
    # opening centered at Y=0.
    if r.canopy_form == "curved_glass":
        body_cy = r.fan_cy
        panel_d = 0.12
        panel_w = FILTER_OPEN_W
        hinge_y = body_cy + panel_d / 2.0  # front edge of the slim-body opening
        panel_cy = body_cy
    else:
        body_cy = 0.0
        panel_d = FILTER_PANEL_D
        panel_w = FILTER_PANEL_W
        hinge_y = FILTER_PANEL_D / 2.0
        panel_cy = 0.0
    grease = model.part("grease_filter")
    grease.visual(
        mesh_from_cadquery(
            _slotted_filter_panel_cq(panel_w, panel_d, FILTER_PANEL_T),
            "filter_mesh_panel",
            tolerance=MESH_TOL,
            angular_tolerance=MESH_ANG,
        ),
        origin=Origin(xyz=(0.0, panel_cy - hinge_y, 0.0)),
        material=mats["filter"],
        name="filter_mesh_panel", material_class_id="metal.mesh_chainmail",
    )
    # Three hinge knuckles along the front edge (at the part-local origin line),
    # captured against the canopy bottom-plate edge.
    knuckle_x = min(0.16, panel_w / 2.0 - 0.02)
    for i, hx in enumerate((-knuckle_x, 0.0, knuckle_x)):
        grease.visual(
            Cylinder(radius=0.006, length=0.025),
            origin=Origin(xyz=(hx, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["motor"],
            name=f"hinge_knuckle_{i}", material_class_id="metal.blackened_gunmetal",
        )
    grease.inertial = Inertial.from_geometry(
        Box((panel_w, panel_d, FILTER_PANEL_T)),
        mass=0.3,
        origin=Origin(xyz=(0.0, panel_cy - hinge_y, 0.0)),
    )
    model.articulation(
        "canopy_to_grease_filter",
        ArticulationType.REVOLUTE,
        parent=canopy,
        child=grease,
        origin=Origin(xyz=(0.0, hinge_y, plate_z + 0.001)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.5, lower=0.0, upper=r.hinge_open),
    )


def _baffle_panel_cq(w: float, d: float, t: float) -> cq.Workplane:
    """Removable baffle filter panel: frame + parallel louver strips + bottom
    plate + central cross-bar. Built centered at origin. Louver count kept
    coarse (perf)."""
    fw = BAFFLE_FRAME
    inner_w = w - 2 * fw
    inner_d = d - 2 * fw
    baffle_thick = 0.0012
    outer = cq.Workplane("XY").rect(w, d).extrude(t)
    hollow = (
        cq.Workplane("XY").workplane(offset=-0.001).rect(inner_w, inner_d).extrude(t + 0.002)
    )
    frame = outer.cut(hollow)
    bottom = cq.Workplane("XY").rect(w - 0.002, d - 0.002).extrude(BAFFLE_PLATE_T)
    cross = cq.Workplane("XY").rect(inner_w, fw * 0.7).extrude(t * 0.55)
    result = frame.union(bottom).union(cross)
    num_baffles = 5  # coarse louver count for mesh weight
    spacing = inner_w / (num_baffles + 1)
    for i in range(1, num_baffles + 1):
        x = -inner_w / 2.0 + i * spacing
        strip = (
            cq.Workplane("XY")
            .workplane(offset=BAFFLE_PLATE_T)
            .center(x, 0.0)
            .rect(baffle_thick, inner_d - 0.004)
            .extrude(t * 0.80)
        )
        result = result.union(strip)
    return result.translate((0.0, 0.0, -t / 2.0))


def _emit_dual_baffle(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    """dual_baffle (filter_count multiplicity): N side-by-side removable baffle
    panels, each FIXED to the canopy and resting on support rails. Absolute
    placement x = (i - (N-1)/2) * pitch so the layout is N-invariant. Baffle
    width/depth shrink with N (resolve_config) so the row sits inside the
    bottom-plate filter opening."""
    n = r.filter_count
    pitch = r.baffle_pitch
    bw = r.baffle_w
    bd = r.baffle_d
    body_cy = r.fan_cy if r.canopy_form == "curved_glass" else 0.0
    plate_z = _bottom_plate_z(r)
    rail_z = plate_z + RAIL_T / 2.0
    filter_z = plate_z + RAIL_T + BAFFLE_T / 2.0
    rail_half_d = (bd - RAIL_W) / 2.0
    rail_len = bw - 0.002
    x0 = -0.5 * (n - 1) * pitch
    # The bottom-plate filter opening (the rails/cross sit inside this hole and
    # must bridge to the surviving plate material at its Y edges, else they read
    # as a disconnected island inside the canopy part). Span the cross-support
    # past the opening depth so each end bites into the plate.
    open_d = FILTER_OPEN_D if r.canopy_form != "curved_glass" else 0.12
    cross_d = open_d + 2.0 * RAIL_W  # reach RAIL_W into the plate on each side

    # N-1 dividers between adjacent baffles (inline canopy visuals over the rim).
    for i in range(n - 1):
        xd = x0 + (i + 0.5) * pitch
        canopy.visual(
            Box((max(0.005, pitch - bw + 0.004), bd + 0.004, BAFFLE_T)),
            origin=Origin(xyz=(xd, body_cy, plate_z + BAFFLE_T / 2.0)),
            material=mats["shell"],
            name=f"filter_divider_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
        )

    for i in range(n):
        cx = x0 + i * pitch
        fp = model.part(f"filter_{i}")
        fp.visual(
            mesh_from_cadquery(
                _baffle_panel_cq(bw, bd, BAFFLE_T),
                f"baffle_panel_{i}",
                tolerance=MESH_TOL,
                angular_tolerance=MESH_ANG,
            ),
            material=mats["filter"],
            name=f"baffle_panel_{i}", material_class_id="metal.patterned_sheet_panel",
        )
        fp.inertial = Inertial.from_geometry(
            Box((bw, bd, BAFFLE_T)), mass=0.25, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
        # Two support rails per baffle (front + back), on the canopy.
        for ri, ry_sign in enumerate((-1.0, 1.0)):
            canopy.visual(
                Box((rail_len, RAIL_W, RAIL_T)),
                origin=Origin(xyz=(cx, body_cy + ry_sign * rail_half_d, rail_z)),
                material=mats["shell"],
                name=f"filter_rail_{i}_{ri}", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
            )
        # Central cross-support spanning the two rails under the baffle center
        # AND bridging to the surviving bottom-plate material at the opening's
        # front/back edges, so the FIXED joint origin (cx, body_cy, filter_z)
        # lands on real canopy geometry, the baffle is visibly supported at its
        # center, and the rail assembly is a connected solid (not a floating
        # island inside the filter opening).
        canopy.visual(
            Box((RAIL_W, cross_d, RAIL_T)),
            origin=Origin(xyz=(cx, body_cy, rail_z)),
            material=mats["shell"],
            name=f"filter_cross_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"glossy_black", "black_glass", "white_steel", "inox_glass"} else "metal.brushed_silver"),
        )
        model.articulation(
            f"canopy_to_filter_{i}",
            ArticulationType.FIXED,
            parent=canopy,
            child=fp,
            origin=Origin(xyz=(cx, body_cy, filter_z)),
        )


# ---------------------------------------------------------------------------
# Control slot. push_button / rotary_knob / slider. The mounting frame is
# resolved per canopy_form (A x D coupling for pyramid's sloped face).
# ---------------------------------------------------------------------------
def _control_frame(r: ResolvedHoodConfig, z: float):
    """Return (origin_y, rpy, inward_axis) for a control at height z on the
    active form's front face."""
    if r.canopy_form == "pyramid":
        face = _PyramidFace(r)
        return face.front_y_at_z(z), (face.tilt_from_z, 0.0, 0.0), (0.0, -face.front_ny, -face.front_nz), face
    # vertical front face (t_box / curved_glass)
    return r.fascia_front_y, (math.pi / 2.0, 0.0, 0.0), (0.0, -1.0, 0.0), None


def _emit_push_button(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    """push_button: 1 articulated power button (presses into the fascia) + 4
    static inline buttons."""
    if r.canopy_form == "curved_glass":
        btn_z = BODY_Z0 + BODY_H * r.height_scale / 2.0
    elif r.canopy_form == "pyramid":
        btn_z = 0.08
    else:
        btn_z = SKIRT_H + 0.055
    front_y, rpy, axis, _ = _control_frame(r, btn_z)

    # Four static control buttons (inline on canopy, Rule 1).
    for i, bx in enumerate((-0.030, -0.005, 0.020, 0.045)):
        canopy.visual(
            Cylinder(radius=BTN_R, length=BTN_LEN),
            origin=Origin(xyz=(bx, front_y + 0.0005, btn_z), rpy=rpy),
            material=mats["button"],
            name=f"button_{i}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black", "black_glass", "white_steel"} else "metal.chrome_polished"),
        )
    # Articulated power button.
    button = model.part("power_button")
    button.visual(
        Cylinder(radius=BTN_R, length=BTN_LEN),
        origin=Origin(rpy=rpy),
        material=mats["button"],
        name="button_cap", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black", "black_glass", "white_steel"} else "metal.chrome_polished"),
    )
    button.inertial = Inertial.from_geometry(
        Cylinder(radius=BTN_R, length=BTN_LEN), mass=0.01, origin=Origin()
    )
    model.articulation(
        "canopy_to_power_button",
        ArticulationType.PRISMATIC,
        parent=canopy,
        child=button,
        origin=Origin(xyz=(0.070, front_y + 0.0005, btn_z)),
        axis=axis,
        motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=r.button_travel),
    )


def _emit_rotary_knob(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    """rotary_knob: 1 knurled knob rotating about +Y through an escutcheon ring."""
    if r.canopy_form == "curved_glass":
        knob_z = BODY_Z0 + BODY_H * r.height_scale / 2.0
    elif r.canopy_form == "pyramid":
        knob_z = 0.10
    else:
        knob_z = SKIRT_H + 0.055
    front_y, rpy, _, face = _control_frame(r, knob_z)

    # Escutcheon bezel ring on the canopy (real anchoring visual).
    canopy.visual(
        Cylinder(radius=ESCUTCHEON_R, length=ESCUTCHEON_T),
        origin=Origin(xyz=(KNOB_X, front_y + ESCUTCHEON_T / 2.0, knob_z), rpy=rpy),
        material=mats["button"],
        name="knob_escutcheon", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black", "black_glass", "white_steel"} else "metal.chrome_polished"),
    )
    knob_geom = KnobGeometry(
        KNOB_D,
        KNOB_H,
        body_style="skirted",
        top_diameter=KNOB_D * 0.80,
        skirt=KnobSkirt(KNOB_D * 1.12, KNOB_H * 0.27, flare=0.08, chamfer=0.0012),
        # Grip count kept coarse (perf: knob ctor cost scales with knurl count).
        grip=KnobGrip(style="knurled", count=16, depth=0.0008, helix_angle_deg=20.0),
        indicator=KnobIndicator(style="dot", mode="raised", angle_deg=0.0),
    )
    speed_knob = model.part("speed_knob")
    speed_knob.visual(
        mesh_from_geometry(knob_geom, "knob_body"),
        origin=Origin(rpy=rpy),
        material=mats["button"],
        name="knob_body", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black", "black_glass", "white_steel"} else "metal.chrome_polished"),
    )
    speed_knob.inertial = Inertial.from_geometry(
        Cylinder(radius=KNOB_D / 2.0, length=KNOB_H), mass=0.03, origin=Origin()
    )
    model.articulation(
        "canopy_to_speed_knob",
        ArticulationType.REVOLUTE,
        parent=canopy,
        child=speed_knob,
        origin=Origin(xyz=(KNOB_X, front_y, knob_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=r.knob_open),
    )


def _emit_slider(model, r: ResolvedHoodConfig, canopy, mats) -> None:
    """slider: 1 low/med/high tab sliding along +X through a track slot."""
    if r.canopy_form == "curved_glass":
        slider_z = BODY_Z0 + BODY_H * r.height_scale / 2.0
    elif r.canopy_form == "pyramid":
        slider_z = 0.10
    else:
        slider_z = SKIRT_H + 0.055
    front_y, rpy, _, face = _control_frame(r, slider_z)
    x0 = -r.slider_travel / 2.0

    # A x D coupling: on the pyramid's sloped front face the cap spans a band of
    # Z over which the surface recedes in Y, so a cap mounted at the face Y for
    # the center Z would bury its lower edge in the shell. Stand the cap proud of
    # the frontmost (lowest) point of the face it spans; the stem is lengthened to
    # still reach back through the shell (captured-slide, allow_overlap). Vertical
    # faces (t_box / curved_glass) need no standoff.
    if face is not None:
        cap_standoff = (face.front_y_at_z(slider_z - SLIDER_TAB_H / 2.0) - front_y) + 0.001
        cap_standoff = max(0.0, cap_standoff)
    elif r.canopy_form == "curved_glass":
        # The slim glass body has a thin front wall + the flush fascia spine just
        # inside it; stand the cap clearly proud so it never buries into them.
        cap_standoff = 0.004
    else:
        cap_standoff = 0.0

    # Track slot recessed into the fascia (real anchoring visual).
    canopy.visual(
        Box((SLIDER_TRACK_W, SLIDER_TRACK_DEPTH, SLIDER_TRACK_H)),
        origin=Origin(xyz=(0.0, front_y - SLIDER_TRACK_DEPTH / 2.0, slider_z)),
        material=mats["motor"],
        name="slider_track", material_class_id="metal.blackened_gunmetal",
    )
    # low/med/high index ticks sit just above the track and overhang DOWN onto
    # it so each tick AABB touches the track (no floating-island markers). They
    # straddle the track Y so they bridge to it regardless of cap_standoff.
    tick_z = slider_z + SLIDER_TRACK_H / 2.0 + 0.004
    tick_h = 0.012
    for i, tx in enumerate((x0, 0.0, x0 + r.slider_travel)):
        canopy.visual(
            Box((0.004, SLIDER_TRACK_DEPTH + 0.002, tick_h)),
            origin=Origin(xyz=(tx, front_y - SLIDER_TRACK_DEPTH / 2.0, tick_z)),
            material=mats["motor"],
            name=f"slider_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    slider = model.part("slider_tab")
    slider.visual(
        Box((SLIDER_TAB_W, SLIDER_TAB_D, SLIDER_TAB_H)),
        origin=Origin(xyz=(0.0, cap_standoff + SLIDER_TAB_D / 2.0, 0.0)),
        material=mats["button"],
        name="slider_cap", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black", "black_glass", "white_steel"} else "metal.chrome_polished"),
    )
    # Stem bridges from the cap back through the fascia wall (lengthened by the
    # standoff so it still reaches the shell for the captured-slide overlap).
    stem_len = SLIDER_STEM_LEN + cap_standoff
    slider.visual(
        Box((SLIDER_STEM_W, stem_len, SLIDER_STEM_H)),
        origin=Origin(xyz=(0.0, cap_standoff - stem_len / 2.0, 0.0)),
        material=mats["motor"],
        name="slider_stem", material_class_id="metal.blackened_gunmetal",
    )
    slider.inertial = Inertial.from_geometry(
        Box((SLIDER_TAB_W, SLIDER_TAB_D + stem_len, SLIDER_TAB_H)),
        mass=0.02,
        origin=Origin(),
    )
    model.articulation(
        "canopy_to_slider_tab",
        ArticulationType.PRISMATIC,
        parent=canopy,
        child=slider,
        origin=Origin(xyz=(x0, front_y + 0.001, slider_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.1, lower=0.0, upper=r.slider_travel),
    )


_FILTER_BUILDERS = {
    "fixed_mesh": _emit_fixed_mesh,
    "hinged": _emit_hinged_filter,
    "dual_baffle": _emit_dual_baffle,
}
_CONTROL_BUILDERS = {
    "push_button": _emit_push_button,
    "rotary_knob": _emit_rotary_knob,
    "slider": _emit_slider,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_hood(
    config: HoodConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"hood_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    canopy = _build_canopy(model, r, mats)
    _build_blower_fan(model, r, canopy, mats)
    _build_chimney(model, r, canopy, mats)
    _FILTER_BUILDERS[r.filter](model, r, canopy, mats)
    _CONTROL_BUILDERS[r.control](model, r, canopy, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hood(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_hood(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _joint_parent_name(joint) -> str:
    """The articulation parent may be a Part or a part-name string."""
    parent = joint.parent
    return parent.name if hasattr(parent, "name") else str(parent)


def run_hood_tests(object_model: ArticulatedObject, config: HoodConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    canopy = object_model.get_part("canopy")
    fan = object_model.get_part("blower_fan")

    # ---- Captured-interface allowances (element-scoped). ----
    # Shared blower fan shaft captured in the motor housing + spindle.
    ctx.allow_overlap(
        fan, canopy, elem_a="fan_shaft", elem_b="motor_housing",
        reason="The rotor shaft is captured inside the blower motor housing.",
    )
    ctx.allow_overlap(
        fan, canopy, elem_a="fan_shaft", elem_b="motor_spindle",
        reason="The rotor shaft runs up over the motor spindle stub.",
    )
    ctx.allow_overlap(
        fan, canopy, elem_a="fan_rotor", elem_b="motor_spindle",
        reason="The rotor hub spins on the central motor spindle.",
    )
    if r.canopy_form == "curved_glass":
        ctx.allow_overlap(
            fan, canopy, elem_a="fan_rotor", elem_b="motor_housing",
            reason="The slim-body fan rotor is nested inside the motor housing proxy.",
        )

    # Chimney captured pads + seated centering bosses.
    sleeve0 = object_model.get_part("sleeve_0")
    # The fully-extended chimney sleeve leaves the duct mouth entirely.
    for sleeve_name in ("sleeve_0", "sleeve_1"):
        if sleeve_name in {p.name for p in object_model.parts}:
            ctx.allow_isolated_part(
                object_model.get_part(sleeve_name),
                reason="extended chimney sleeve rises clear of the duct and loses contact",
            )
    for j in range(4):
        ctx.allow_overlap(
            sleeve0, canopy, elem_a=f"guide_pad_0_{j}", elem_b="lower_duct",
            reason="Stage-0 guide pads grip the lower duct wall to carry the sleeve.",
        )
    ctx.allow_overlap(
        sleeve0, canopy, elem_a="sleeve_centering_boss_0", elem_b="duct_centering_boss",
        reason="The sleeve_0 centering boss seats on the duct centering boss at rest.",
    )
    ctx.allow_overlap(
        sleeve0, canopy, elem_a="sleeve_centering_boss_0", elem_b="lower_duct",
        reason="The sleeve_0 centering boss spans the sleeve interior and brushes the duct wall.",
    )
    if r.chimney == "dual_telescope":
        sleeve1 = object_model.get_part("sleeve_1")
        for j in range(4):
            ctx.allow_overlap(
                sleeve1, sleeve0, elem_a=f"guide_pad_1_{j}", elem_b="sleeve_shell_0",
                reason="Stage-1 guide pads grip the stage-0 outer shell.",
            )
        ctx.allow_overlap(
            sleeve0, sleeve1, elem_a="sleeve_shell_0", elem_b="sleeve_shell_1",
            reason="Dual-stage telescoping sleeves are concentrically nested at rest.",
        )
        ctx.allow_overlap(
            sleeve1, sleeve0, elem_a="sleeve_centering_boss_1", elem_b="sleeve_centering_boss_0",
            reason="The sleeve_1 centering boss seats on the sleeve_0 centering boss at rest.",
        )
        ctx.allow_overlap(
            sleeve1, sleeve0, elem_a="sleeve_centering_boss_1", elem_b="sleeve_shell_0",
            reason="The sleeve_1 centering boss spans its interior and brushes the sleeve_0 wall.",
        )
        ctx.allow_overlap(
            sleeve1, canopy, elem_a="sleeve_centering_boss_1", elem_b="duct_centering_boss",
            reason="The nested sleeve_1 centering boss overlaps the duct boss at rest.",
        )
        ctx.allow_overlap(
            sleeve1, canopy, elem_a="sleeve_centering_boss_1", elem_b="lower_duct",
            reason="The nested sleeve_1 centering boss brushes the lower duct wall at rest.",
        )

    # Filter captured interfaces.
    if r.filter == "hinged":
        grease = object_model.get_part("grease_filter")
        for i in range(3):
            ctx.allow_overlap(
                grease, canopy, elem_a=f"hinge_knuckle_{i}", elem_b="canopy_shell",
                reason="Hinge knuckles seat at the canopy bottom-plate edge.",
            )
        ctx.allow_overlap(
            grease, canopy,
            reason="Closed grease filter sits flat in the cavity against the bottom plate.",
        )
    elif r.filter == "dual_baffle":
        for i in range(r.filter_count):
            fp = object_model.get_part(f"filter_{i}")
            for ri in range(2):
                ctx.allow_overlap(
                    fp, canopy, elem_a=f"baffle_panel_{i}", elem_b=f"filter_rail_{i}_{ri}",
                    reason=f"Baffle panel {i} rests on its support rail {ri}.",
                )

    # Control captured interfaces. On curved_glass the fascia includes the flush
    # connective spine embedded in the thin front wall, so the captured control
    # body passes through it exactly as it passes through canopy_shell.
    is_cg = r.canopy_form == "curved_glass"
    if r.control == "push_button":
        button = object_model.get_part("power_button")
        ctx.allow_overlap(
            button, canopy, elem_a="button_cap", elem_b="canopy_shell",
            reason="The push-button cap passes through the fascia wall like a button stem.",
        )
        if is_cg:
            ctx.allow_overlap(
                button, canopy, elem_a="button_cap", elem_b="fascia_spine",
                reason="The push-button cap passes through the slim-body fascia spine.",
            )
    elif r.control == "rotary_knob":
        knob = object_model.get_part("speed_knob")
        ctx.allow_overlap(
            knob, canopy, elem_a="knob_body", elem_b="canopy_shell",
            reason="The knob body passes through the fascia wall and rotates on its shaft.",
        )
        ctx.allow_overlap(
            knob, canopy, elem_a="knob_body", elem_b="knob_escutcheon",
            reason="The knob body protrudes through the escutcheon bezel ring.",
        )
        if is_cg:
            ctx.allow_overlap(
                knob, canopy, elem_a="knob_body", elem_b="fascia_spine",
                reason="The knob body passes through the slim-body fascia spine.",
            )
    else:  # slider
        slider = object_model.get_part("slider_tab")
        ctx.allow_overlap(
            slider, canopy, elem_a="slider_stem", elem_b="canopy_shell",
            reason="The slider stem passes through the track slot in the fascia.",
        )
        ctx.allow_overlap(
            slider, canopy, elem_a="slider_stem", elem_b="slider_track",
            reason="The slider stem rides inside the recessed track.",
        )
        if is_cg:
            ctx.allow_overlap(
                slider, canopy, elem_a="slider_stem", elem_b="fascia_spine",
                reason="The slider stem passes through the slim-body fascia spine.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("canopy root present", "canopy" in part_names, details=str(sorted(part_names)))

    # Canopy underside reference. t_box / pyramid bottom plate sits at z=0;
    # curved_glass is a higher wall-mounted visor whose lowest point is the
    # glass visor tip (~0.04 m), so it is not held to z=0.
    bb = ctx.part_world_aabb(canopy)
    if bb is not None:
        if r.canopy_form == "curved_glass":
            ctx.check(
                "curved_glass visor sweeps down to a low front tip",
                bb[0][2] < 0.10,
                details=f"z_min={bb[0][2]:.4f}",
            )
        else:
            ctx.check(
                "canopy bottom-plate underside is at z=0",
                abs(bb[0][2]) < 0.01,
                details=f"z_min={bb[0][2]:.4f}",
            )

    # ---- Shared blower fan: CONTINUOUS vertical spin. ----
    spin = object_model.get_articulation("canopy_to_blower_fan")
    ctx.check(
        "blower fan is CONTINUOUS about the vertical axis (shared defining motion)",
        spin.articulation_type == ArticulationType.CONTINUOUS
        and abs(spin.axis[2]) > 0.99
        and (spin.motion_limits is None or spin.motion_limits.lower is None),
        details=f"type={spin.articulation_type}, axis={tuple(spin.axis)}",
    )
    fbb = ctx.part_world_aabb(fan)
    if fbb is not None:
        ctx.check(
            "rotor blades reach a visible radius off the spin axis",
            (fbb[1][0] - fbb[0][0]) > 2.0 * r.fan_r * 0.85,
            details=f"fan aabb={fbb}",
        )

    # ---- Chimney: PRISMATIC +Z, retained insertion, upward travel. ----
    j0 = object_model.get_articulation("canopy_to_sleeve_0")
    ctx.check(
        "chimney sleeve_0 is PRISMATIC about +Z",
        j0.articulation_type == ArticulationType.PRISMATIC and abs(j0.axis[2]) > 0.99,
        details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
    )
    sleeve0 = object_model.get_part("sleeve_0")
    rest_pos = ctx.part_world_position(sleeve0)
    with ctx.pose({j0: r.chimney_travel}):
        ext_pos = ctx.part_world_position(sleeve0)
    if rest_pos is not None and ext_pos is not None:
        ctx.check(
            "sleeve_0 extends straight up by its travel",
            abs((ext_pos[2] - rest_pos[2]) - r.chimney_travel) < 1e-6
            and abs(ext_pos[0] - rest_pos[0]) < 1e-6
            and abs(ext_pos[1] - rest_pos[1]) < 1e-6,
            details=f"rest={rest_pos}, ext={ext_pos}",
        )
    ctx.expect_overlap(
        canopy, sleeve0, axes="z", elem_a="lower_duct", elem_b="sleeve_shell_0",
        min_overlap=0.20, name="closed sleeve_0 overlaps the lower duct",
    )
    if r.chimney == "dual_telescope":
        j1 = object_model.get_articulation("sleeve_0_to_sleeve_1")
        ctx.check(
            "dual chimney: sleeve_1 is a PRISMATIC child of sleeve_0 (linear chain)",
            j1.articulation_type == ArticulationType.PRISMATIC
            and abs(j1.axis[2]) > 0.99
            and _joint_parent_name(j1) == "sleeve_0",
            details=f"type={j1.articulation_type} axis={tuple(j1.axis)} parent={_joint_parent_name(j1)}",
        )

    # ---- Filter joint topology. ----
    if r.filter == "fixed_mesh":
        ctx.check(
            "fixed_mesh filter is an inline canopy visual (Rule 1, no joint)",
            any(v.name == "filter_mesh_panel" for v in canopy.visuals),
            details="filter_mesh_panel missing from canopy",
        )
    elif r.filter == "hinged":
        jf = object_model.get_articulation("canopy_to_grease_filter")
        ctx.check(
            "hinged filter is REVOLUTE about +X",
            jf.articulation_type == ArticulationType.REVOLUTE and abs(jf.axis[0]) > 0.99,
            details=f"type={jf.articulation_type} axis={tuple(jf.axis)}",
        )
        grease = object_model.get_part("grease_filter")
        closed = ctx.part_world_aabb(grease)
        with ctx.pose({jf: r.hinge_open * 0.8}):
            opened = ctx.part_world_aabb(grease)
        if closed is not None and opened is not None:
            ctx.check(
                "hinged filter flips down (rear edge drops)",
                opened[0][2] < closed[0][2] - 0.02,
                details=f"closed_zmin={closed[0][2]:.3f} open_zmin={opened[0][2]:.3f}",
            )
    else:  # dual_baffle
        ctx.check(
            f"dual_baffle has N={r.filter_count} FIXED baffle parts",
            all(f"filter_{i}" in part_names for i in range(r.filter_count)),
            details=str(sorted(p for p in part_names if p.startswith("filter_"))),
        )
        for i in range(r.filter_count):
            art = object_model.get_articulation(f"canopy_to_filter_{i}")
            ctx.check(
                f"filter_{i} is FIXED to the canopy",
                art.articulation_type == ArticulationType.FIXED,
                details=f"type={art.articulation_type}",
            )
        # Side-by-side: no X overlap between adjacent baffles.
        if r.filter_count >= 2:
            f0 = ctx.part_world_aabb(object_model.get_part("filter_0"))
            f1 = ctx.part_world_aabb(object_model.get_part("filter_1"))
            if f0 is not None and f1 is not None:
                ctx.check(
                    "adjacent baffle panels are separated along X (no X overlap)",
                    (f1[0][0] - f0[1][0]) > 0.002,
                    details=f"f0 xmax={f0[1][0]:.3f} f1 xmin={f1[0][0]:.3f}",
                )

    # ---- Control joint topology + actuation. ----
    if r.control == "push_button":
        jb = object_model.get_articulation("canopy_to_power_button")
        ctx.check(
            "push_button is PRISMATIC into the fascia",
            jb.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={jb.articulation_type} axis={tuple(jb.axis)}",
        )
        if r.canopy_form == "pyramid":
            face = _PyramidFace(r)
            ctx.check(
                "pyramid power button axis is the inward normal of the sloped face (A x D)",
                abs(jb.axis[1] - (-face.front_ny)) < 1e-6 and abs(jb.axis[2] - (-face.front_nz)) < 1e-6,
                details=f"axis={tuple(jb.axis)} expected=(0,{-face.front_ny:.3f},{-face.front_nz:.3f})",
            )
        else:
            ctx.check(
                "vertical-face power button axis is -Y",
                abs(jb.axis[1] + 1.0) < 1e-6,
                details=f"axis={tuple(jb.axis)}",
            )
        button = object_model.get_part("power_button")
        p0 = ctx.part_world_position(button)
        with ctx.pose({jb: r.button_travel}):
            p1 = ctx.part_world_position(button)
        if p0 is not None and p1 is not None:
            moved = math.sqrt(sum((p1[k] - p0[k]) ** 2 for k in range(3)))
            ctx.check(
                "pressing the power button presses it inward by its travel",
                abs(moved - r.button_travel) < 0.0015,
                details=f"moved={moved:.4f} travel={r.button_travel:.4f}",
            )
    elif r.control == "rotary_knob":
        jk = object_model.get_articulation("canopy_to_speed_knob")
        ctx.check(
            "rotary_knob is REVOLUTE about +Y",
            jk.articulation_type == ArticulationType.REVOLUTE and abs(jk.axis[1]) > 0.99,
            details=f"type={jk.articulation_type} axis={tuple(jk.axis)}",
        )
        knob = object_model.get_part("speed_knob")
        p0 = ctx.part_world_position(knob)
        with ctx.pose({jk: r.knob_open}):
            p1 = ctx.part_world_position(knob)
        if p0 is not None and p1 is not None:
            ctx.check(
                "knob stays at its mount position when rotated (no drift)",
                all(abs(p0[k] - p1[k]) < 1e-6 for k in range(3)),
                details=f"rest={p0}, turned={p1}",
            )
    else:  # slider
        js = object_model.get_articulation("canopy_to_slider_tab")
        ctx.check(
            "slider is PRISMATIC about +X",
            js.articulation_type == ArticulationType.PRISMATIC and abs(js.axis[0]) > 0.99,
            details=f"type={js.articulation_type} axis={tuple(js.axis)}",
        )
        slider = object_model.get_part("slider_tab")
        p0 = ctx.part_world_position(slider)
        with ctx.pose({js: r.slider_travel}):
            p1 = ctx.part_world_position(slider)
        if p0 is not None and p1 is not None:
            ctx.check(
                "slider translates along +X by its travel",
                abs((p1[0] - p0[0]) - r.slider_travel) < 1e-6,
                details=f"rest={p0}, slid={p1}",
            )

    # ---- slot_choices recorded with N encoded. ----
    ctx.check(
        "slot_choices recorded with filter_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "HoodConfig",
    "ResolvedHoodConfig",
    "build_hood",
    "build_seeded_hood",
    "config_from_seed",
    "resolve_config",
    "run_hood_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
