# SPDX-License-Identifier: Apache-2.0

"""Technology / Audio_Device — retro radio, tabletop cabinet and boombox family.

One enclosure part carries the front speaker field, the tuning dial and the top
bay.  A control deck, a carry handle and an antenna module mount on that
enclosure through explicit plane/axis interfaces.

Frame: +X = cabinet width, -Y = the front face the preview camera looks at,
+Z = up with the cabinet standing on z = 0.

Every dimension that could make two neighbouring controls touch is derived:
the control pitch comes from the selected cap footprint, the deck footprint
comes from the pitch times the multiplicity, and the cabinet width/height come
from the deck footprint.  Nothing in this file caps the multiplicity to hide a
collision.
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
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    PlaneInterface,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    TorusGeometry,
    component_slot,
    corner_case,
    mate_axes,
    mate_planes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    rounded_rect_profile,
    sweep_profile_along_spline,
)

__preview_front_axis__ = "-y"

CabinetForm = Literal[
    "landscape_cabinet",
    "portable_slab",
    "tombstone_upright",
    "boombox_slab",
]
GrilleStyle = Literal["horizontal_ribbed", "perforated_mesh", "vertical_bar"]
SpeakerLayout = Literal["single_field", "dual_stereo"]
ControlDeck = Literal["rotary_knob_bank", "push_button_row", "transport_key_deck"]
CarryHandle = Literal["molded_top_lip", "fixed_bail", "folding_bail"]
AntennaModule = Literal["no_antenna", "side_swivel_whip", "rear_telescoping_mast"]

_CABINET_FORMS: tuple[str, ...] = (
    "landscape_cabinet",
    "portable_slab",
    "tombstone_upright",
    "boombox_slab",
)
_GRILLE_STYLES: tuple[str, ...] = ("horizontal_ribbed", "perforated_mesh", "vertical_bar")
_SPEAKER_LAYOUTS: tuple[str, ...] = ("single_field", "dual_stereo")
_CONTROL_DECKS: tuple[str, ...] = (
    "rotary_knob_bank",
    "push_button_row",
    "transport_key_deck",
)
_CARRY_HANDLES: tuple[str, ...] = ("molded_top_lip", "fixed_bail", "folding_bail")
_ANTENNA_MODULES: tuple[str, ...] = (
    "no_antenna",
    "side_swivel_whip",
    "rear_telescoping_mast",
)
_CONTROL_COUNTS: tuple[int, ...] = (2, 3, 4, 5, 6, 8)

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("cabinet_form", _CABINET_FORMS),
        component_slot("grille_style", _GRILLE_STYLES),
        component_slot("speaker_layout", _SPEAKER_LAYOUTS),
        component_slot("control_deck", _CONTROL_DECKS),
        component_slot("carry_handle", _CARRY_HANDLES),
        component_slot("antenna_module", _ANTENNA_MODULES),
        multiplicity_slot("control_count", _CONTROL_COUNTS, item_slot="control_deck"),
    )
)

RGBA = tuple[float, float, float, float]
_PALETTES: tuple[dict[str, RGBA], ...] = (
    {
        "shell": (0.62, 0.25, 0.12, 1.0),
        "shell_dark": (0.34, 0.13, 0.06, 1.0),
        "trim": (0.20, 0.10, 0.05, 1.0),
        "grille": (0.90, 0.84, 0.66, 1.0),
        "backdrop": (0.03, 0.03, 0.03, 1.0),
        "dial": (0.89, 0.80, 0.58, 1.0),
        "ink": (0.09, 0.08, 0.06, 1.0),
        "accent": (0.78, 0.06, 0.04, 1.0),
        "metal": (0.86, 0.86, 0.82, 1.0),
        "cap": (0.90, 0.85, 0.70, 1.0),
    },
    {
        "shell": (0.72, 0.52, 0.34, 1.0),
        "shell_dark": (0.55, 0.38, 0.24, 1.0),
        "trim": (0.36, 0.24, 0.14, 1.0),
        "grille": (0.10, 0.10, 0.10, 1.0),
        "backdrop": (0.02, 0.02, 0.02, 1.0),
        "dial": (0.86, 0.79, 0.66, 1.0),
        "ink": (0.13, 0.11, 0.09, 1.0),
        "accent": (0.86, 0.62, 0.25, 1.0),
        "metal": (0.86, 0.62, 0.25, 1.0),
        "cap": (0.86, 0.79, 0.66, 1.0),
    },
    {
        "shell": (0.80, 0.82, 0.85, 1.0),
        "shell_dark": (0.55, 0.57, 0.61, 1.0),
        "trim": (0.13, 0.14, 0.16, 1.0),
        "grille": (0.08, 0.08, 0.09, 1.0),
        "backdrop": (0.03, 0.03, 0.04, 1.0),
        "dial": (0.35, 0.95, 0.50, 1.0),
        "ink": (0.05, 0.06, 0.07, 1.0),
        "accent": (0.18, 0.42, 0.88, 1.0),
        "metal": (0.74, 0.76, 0.80, 1.0),
        "cap": (0.87, 0.87, 0.85, 1.0),
    },
    {
        "shell": (0.38, 0.20, 0.10, 1.0),
        "shell_dark": (0.22, 0.10, 0.05, 1.0),
        "trim": (0.10, 0.06, 0.03, 1.0),
        "grille": (0.83, 0.78, 0.59, 1.0),
        "backdrop": (0.02, 0.02, 0.02, 1.0),
        "dial": (0.90, 0.86, 0.74, 1.0),
        "ink": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.80, 0.12, 0.10, 1.0),
        "metal": (0.78, 0.79, 0.82, 1.0),
        "cap": (0.88, 0.84, 0.72, 1.0),
    },
)

# ---------------------------------------------------------------------------
# Fixed assembly constants (metres).
# ---------------------------------------------------------------------------
_CONTROL_GAP = 0.006  # guaranteed air between neighbouring control caps
_DECK_MARGIN_U = 0.010  # deck plate margin beyond the control row
_DECK_EMBED = 0.0008  # deck plate depth buried in the cabinet shell
_DECK_WEB_T = 0.0016  # substrate web thickness behind the control wells
_HOLE_CLEARANCE = 0.0008  # radial clearance of a control inside its deck opening
_MIN_PRESSED_PROTRUSION = 0.0008  # cap thickness still visible at full press
_MIN_TOP_BAY_W = 0.260
_SADDLE_DEPTH = 0.026
_SADDLE_HALF_W = 0.014
_HANDLE_SPAN_INSET = 0.150
_ANTENNA_EDGE_INSET = 0.024
_DIAL_HEIGHT = 0.042
_AUX_KNOB_DIAMETER = 0.028
_SKIRT_RATIO = 1.16
_KNOB_HEIGHT_RATIO = 0.46
_KNOB_RECESS = 0.0015
_BUTTON_HEIGHT = 0.009
_BUTTON_RECESS = 0.0020
_KEY_HEIGHT = 0.008
_KEY_RECESS = 0.0025
_ROD_RADIUS = 0.0021
_ROD_BORE = 0.0026
_ROD_INSERTION = 0.018


@dataclass(frozen=True)
class Config:
    cabinet_form: CabinetForm = "landscape_cabinet"
    grille_style: GrilleStyle = "horizontal_ribbed"
    speaker_layout: SpeakerLayout = "single_field"
    control_deck: ControlDeck = "rotary_knob_bank"
    carry_handle: CarryHandle = "molded_top_lip"
    antenna_module: AntennaModule = "no_antenna"
    control_count: int = 2
    landscape_width_m: float | None = None
    landscape_height_ratio: float | None = None
    portable_width_m: float | None = None
    portable_corner_radius_m: float | None = None
    tombstone_width_m: float | None = None
    tombstone_height_ratio: float | None = None
    boombox_width_m: float | None = None
    boombox_corner_radius_m: float | None = None
    rib_pitch_m: float | None = None
    mesh_hole_pitch_m: float | None = None
    bar_pitch_m: float | None = None
    single_field_width_ratio: float | None = None
    stereo_field_gap_m: float | None = None
    knob_diameter_m: float | None = None
    button_width_m: float | None = None
    button_travel_m: float | None = None
    transport_key_width_m: float | None = None
    transport_key_travel_m: float | None = None
    top_lip_height_m: float | None = None
    fixed_bail_rise_m: float | None = None
    folding_bail_rise_m: float | None = None
    folding_bail_angle_rad: float | None = None
    blank_badge_width_m: float | None = None
    whip_mast_length_m: float | None = None
    whip_travel_m: float | None = None
    mast_length_m: float | None = None
    mast_travel_m: float | None = None
    palette: int = 0
    name: str = "Technology_Audio_Device"


@dataclass(frozen=True)
class ResolvedConfig:
    cabinet_form: CabinetForm
    grille_style: GrilleStyle
    speaker_layout: SpeakerLayout
    control_deck: ControlDeck
    carry_handle: CarryHandle
    antenna_module: AntennaModule
    control_count: int
    landscape_width_m: float
    landscape_height_ratio: float
    portable_width_m: float
    portable_corner_radius_m: float
    tombstone_width_m: float
    tombstone_height_ratio: float
    boombox_width_m: float
    boombox_corner_radius_m: float
    rib_pitch_m: float
    mesh_hole_pitch_m: float
    bar_pitch_m: float
    single_field_width_ratio: float
    stereo_field_gap_m: float
    knob_diameter_m: float
    button_width_m: float
    button_travel_m: float
    transport_key_width_m: float
    transport_key_travel_m: float
    top_lip_height_m: float
    fixed_bail_rise_m: float
    folding_bail_rise_m: float
    folding_bail_angle_rad: float
    blank_badge_width_m: float
    whip_mast_length_m: float
    whip_travel_m: float
    mast_length_m: float
    mast_travel_m: float
    palette: int
    name: str
    # derived cabinet geometry
    cabinet_width_m: float
    cabinet_depth_m: float
    cabinet_height_m: float
    cabinet_corner_radius_m: float
    front_inset_m: float
    straight_height_m: float
    top_bay_width_m: float
    # derived control geometry
    deck_face: str
    control_cap_u_m: float
    control_cap_v_m: float
    control_cap_height_m: float
    control_recess_m: float
    control_travel_m: float
    control_pitch_m: float
    control_row_width_m: float
    deck_width_m: float
    deck_height_m: float
    deck_plate_thickness_m: float
    deck_face_offset_m: float
    deck_center_z_m: float
    deck_center_y_m: float
    aux_knob_offset_u_m: float
    # derived front layout
    field_count: int
    field_width_m: float
    field_height_m: float
    field_offset_m: float
    grille_center_z_m: float
    dial_center_z_m: float
    dial_width_m: float
    # derived top layout
    handle_span_m: float
    handle_seat_y_m: float
    handle_rise_m: float
    antenna_x_m: float
    antenna_y_m: float
    antenna_socket_z_m: float
    antenna_mast_length_m: float
    antenna_travel_m: float


def _bounded(value: float | None, default: float, lower: float, upper: float) -> float:
    selected = default if value is None else float(value)
    if not lower - 1e-9 <= selected <= upper + 1e-9:
        raise ValueError(f"value {selected} outside [{lower}, {upper}]")
    return selected


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    index = int(seed)
    # The multiplicity slot and its item slot use a strict positional
    # decomposition so every control_deck x control_count pair is reachable in
    # the first 18 seeds.  The remaining slots use co-prime strides so a
    # 36-seed cumulative sweep still exercises every candidate of every slot
    # instead of walking one slot at a time.
    control_count = _CONTROL_COUNTS[index % len(_CONTROL_COUNTS)]
    control_deck = _CONTROL_DECKS[(index // len(_CONTROL_COUNTS)) % len(_CONTROL_DECKS)]
    cabinet_form = _CABINET_FORMS[index % len(_CABINET_FORMS)]
    grille_style = _GRILLE_STYLES[(index // 2) % len(_GRILLE_STYLES)]
    speaker_layout = _SPEAKER_LAYOUTS[(index // 5) % len(_SPEAKER_LAYOUTS)]
    carry_handle = _CARRY_HANDLES[(index // 4) % len(_CARRY_HANDLES)]
    antenna_module = _ANTENNA_MODULES[(index // 7) % len(_ANTENNA_MODULES)]
    return Config(
        cabinet_form=cabinet_form,
        grille_style=grille_style,
        speaker_layout=speaker_layout,
        control_deck=control_deck,
        carry_handle=carry_handle,
        antenna_module=antenna_module,
        control_count=control_count,
        landscape_width_m=round(rng.uniform(0.400, 0.620), 4),
        landscape_height_ratio=round(rng.uniform(0.44, 0.58), 4),
        portable_width_m=round(rng.uniform(0.260, 0.360), 4),
        portable_corner_radius_m=round(rng.uniform(0.014, 0.030), 4),
        tombstone_width_m=round(rng.uniform(0.300, 0.400), 4),
        tombstone_height_ratio=round(rng.uniform(1.20, 1.55), 4),
        boombox_width_m=round(rng.uniform(0.280, 0.420), 4),
        boombox_corner_radius_m=round(rng.uniform(0.022, 0.046), 4),
        rib_pitch_m=round(rng.uniform(0.0060, 0.0130), 4),
        mesh_hole_pitch_m=round(rng.uniform(0.0080, 0.0140), 4),
        bar_pitch_m=round(rng.uniform(0.0090, 0.0180), 4),
        single_field_width_ratio=round(rng.uniform(0.62, 0.86), 4),
        stereo_field_gap_m=round(rng.uniform(0.020, 0.070), 4),
        knob_diameter_m=round(rng.uniform(0.030, 0.056), 4),
        button_width_m=round(rng.uniform(0.018, 0.032), 4),
        button_travel_m=round(rng.uniform(0.0020, 0.0042), 4),
        transport_key_width_m=round(rng.uniform(0.011, 0.020), 4),
        transport_key_travel_m=round(rng.uniform(0.0018, 0.0035), 4),
        top_lip_height_m=round(rng.uniform(0.004, 0.012), 4),
        fixed_bail_rise_m=round(rng.uniform(0.055, 0.115), 4),
        folding_bail_rise_m=round(rng.uniform(0.050, 0.100), 4),
        folding_bail_angle_rad=round(rng.uniform(1.05, 1.57), 4),
        blank_badge_width_m=round(rng.uniform(0.020, 0.050), 4),
        whip_mast_length_m=round(rng.uniform(0.070, 0.130), 4),
        whip_travel_m=round(rng.uniform(0.030, 0.075), 4),
        mast_length_m=round(rng.uniform(0.090, 0.160), 4),
        mast_travel_m=round(rng.uniform(0.035, 0.085), 4),
        palette=rng.randrange(len(_PALETTES)),
        name=f"Technology_Audio_Device_seed_{seed}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    if config.cabinet_form not in _CABINET_FORMS:
        raise ValueError(f"unsupported cabinet_form: {config.cabinet_form}")
    if config.grille_style not in _GRILLE_STYLES:
        raise ValueError(f"unsupported grille_style: {config.grille_style}")
    if config.speaker_layout not in _SPEAKER_LAYOUTS:
        raise ValueError(f"unsupported speaker_layout: {config.speaker_layout}")
    if config.control_deck not in _CONTROL_DECKS:
        raise ValueError(f"unsupported control_deck: {config.control_deck}")
    if config.carry_handle not in _CARRY_HANDLES:
        raise ValueError(f"unsupported carry_handle: {config.carry_handle}")
    if config.antenna_module not in _ANTENNA_MODULES:
        raise ValueError(f"unsupported antenna_module: {config.antenna_module}")
    if int(config.control_count) not in _CONTROL_COUNTS:
        raise ValueError(f"control_count must be one of {_CONTROL_COUNTS}")

    control_count = int(config.control_count)
    landscape_width = _bounded(config.landscape_width_m, 0.510, 0.400, 0.620)
    landscape_ratio = _bounded(config.landscape_height_ratio, 0.51, 0.44, 0.58)
    portable_width = _bounded(config.portable_width_m, 0.310, 0.260, 0.360)
    portable_radius = _bounded(config.portable_corner_radius_m, 0.022, 0.014, 0.030)
    tombstone_width = _bounded(config.tombstone_width_m, 0.350, 0.300, 0.400)
    tombstone_ratio = _bounded(config.tombstone_height_ratio, 1.37, 1.20, 1.55)
    boombox_width = _bounded(config.boombox_width_m, 0.350, 0.280, 0.420)
    boombox_radius = _bounded(config.boombox_corner_radius_m, 0.034, 0.022, 0.046)
    rib_pitch = _bounded(config.rib_pitch_m, 0.0095, 0.0060, 0.0130)
    mesh_pitch = _bounded(config.mesh_hole_pitch_m, 0.0110, 0.0080, 0.0140)
    bar_pitch = _bounded(config.bar_pitch_m, 0.0135, 0.0090, 0.0180)
    single_ratio = _bounded(config.single_field_width_ratio, 0.74, 0.62, 0.86)
    stereo_gap = _bounded(config.stereo_field_gap_m, 0.045, 0.020, 0.070)
    knob_diameter = _bounded(config.knob_diameter_m, 0.043, 0.030, 0.056)
    button_width = _bounded(config.button_width_m, 0.025, 0.018, 0.032)
    button_travel = _bounded(config.button_travel_m, 0.0031, 0.0020, 0.0042)
    key_width = _bounded(config.transport_key_width_m, 0.0155, 0.011, 0.020)
    key_travel = _bounded(config.transport_key_travel_m, 0.0026, 0.0018, 0.0035)
    top_lip_height = _bounded(config.top_lip_height_m, 0.008, 0.004, 0.012)
    fixed_rise = _bounded(config.fixed_bail_rise_m, 0.085, 0.055, 0.115)
    folding_rise = _bounded(config.folding_bail_rise_m, 0.075, 0.050, 0.100)
    folding_angle = _bounded(config.folding_bail_angle_rad, 1.31, 1.05, 1.57)
    badge_width = _bounded(config.blank_badge_width_m, 0.035, 0.020, 0.050)
    whip_mast = _bounded(config.whip_mast_length_m, 0.100, 0.070, 0.130)
    whip_travel = _bounded(config.whip_travel_m, 0.0525, 0.030, 0.075)
    mast_length = _bounded(config.mast_length_m, 0.125, 0.090, 0.160)
    mast_travel = _bounded(config.mast_travel_m, 0.060, 0.035, 0.085)

    # --- control cap footprint, pitch and deck footprint -------------------
    aux_skirt = _AUX_KNOB_DIAMETER * _SKIRT_RATIO
    if config.control_deck == "rotary_knob_bank":
        cap_u = knob_diameter * _SKIRT_RATIO
        cap_v = cap_u
        cap_height = knob_diameter * _KNOB_HEIGHT_RATIO
        recess = _KNOB_RECESS
        travel = 0.0
        deck_face = "front"
        aux_offset = 0.0
    elif config.control_deck == "push_button_row":
        cap_u = button_width
        cap_v = max(0.013, button_width * 0.62)
        cap_height = _BUTTON_HEIGHT
        recess = _BUTTON_RECESS
        travel = button_travel
        deck_face = "top"
        aux_offset = 0.0
    else:
        cap_u = key_width
        cap_v = max(0.010, key_width * 0.85)
        cap_height = _KEY_HEIGHT
        recess = _KEY_RECESS
        travel = key_travel
        deck_face = "front"
        aux_offset = 0.0

    pitch = cap_u + _CONTROL_GAP
    row_width = control_count * pitch
    if config.control_deck == "transport_key_deck":
        aux_offset = row_width / 2.0 + 0.012 + aux_skirt / 2.0
        deck_width = row_width + 2.0 * (aux_skirt + 0.012) + 2.0 * _DECK_MARGIN_U
        deck_height = max(cap_v + 0.014, aux_skirt + 0.012)
    else:
        deck_width = row_width + 2.0 * _DECK_MARGIN_U
        deck_height = cap_v + 0.016

    # The plate must be thick enough that a fully pressed cap still stops
    # inside its own opening instead of diving into the cabinet shell.
    plate_thickness = max(recess + travel, _KNOB_RECESS) + 0.0015 + _DECK_EMBED
    face_offset = plate_thickness - _DECK_EMBED

    # --- cabinet envelope -------------------------------------------------
    if config.cabinet_form == "boombox_slab":
        front_inset = boombox_radius + 0.014
    else:
        front_inset = 0.026
    front_need = deck_width + 2.0 * front_inset + 0.010 if deck_face == "front" else 0.0
    top_need = max(_MIN_TOP_BAY_W, deck_width + 0.050 if deck_face == "top" else 0.0)

    if config.cabinet_form == "landscape_cabinet":
        nominal_w, nominal_d = landscape_width, 0.200
        nominal_h = landscape_width * landscape_ratio
        corner_radius = 0.030
    elif config.cabinet_form == "portable_slab":
        nominal_w, nominal_d = portable_width, 0.100
        nominal_h = portable_width * 0.54
        corner_radius = portable_radius
    elif config.cabinet_form == "tombstone_upright":
        nominal_w, nominal_d = tombstone_width, 0.200
        nominal_h = tombstone_width * tombstone_ratio
        corner_radius = 0.016
    else:
        nominal_w, nominal_d = boombox_width, 0.205
        nominal_h = boombox_width * 0.52
        corner_radius = boombox_radius

    if config.cabinet_form == "tombstone_upright":
        top_bay_width = top_need
        cabinet_width = max(nominal_w, front_need, top_bay_width + 0.090)
    elif config.cabinet_form == "boombox_slab":
        cabinet_width = max(nominal_w, front_need, top_need + 2.0 * corner_radius)
        top_bay_width = cabinet_width - 2.0 * corner_radius
    else:
        cabinet_width = max(nominal_w, front_need, top_need)
        top_bay_width = cabinet_width

    depth_need = deck_height + 0.060 if deck_face == "top" else 0.0
    if config.cabinet_form == "boombox_slab":
        depth_need += 2.0 * corner_radius
    cabinet_depth = max(nominal_d, depth_need, 0.098)

    # --- front face stack -------------------------------------------------
    usable_w = cabinet_width - 2.0 * front_inset
    if config.speaker_layout == "single_field":
        field_count = 1
        field_width = min(usable_w, cabinet_width * single_ratio)
        field_offset = 0.0
    else:
        field_count = 2
        field_width = max(0.055, (usable_w - stereo_gap) / 2.0)
        field_offset = (stereo_gap + field_width) / 2.0
    # The front face is a stack: bottom margin, optional deck, tuning dial,
    # speaker field, top margin.  The cabinet's own height parameter drives the
    # speaker field height; everything else is fixed by the parts it carries.
    fixed_stack = 0.012 + _DIAL_HEIGHT + 0.014 + 0.016
    if deck_face == "front":
        fixed_stack += deck_height + 0.014

    if config.cabinet_form == "tombstone_upright":
        arch_radius = cabinet_width / 2.0
        arch_rise = math.sqrt(max(1e-6, arch_radius * arch_radius - (top_bay_width / 2.0) ** 2))
        nominal_usable = max(nominal_h - arch_rise, 0.10)
    else:
        arch_rise = 0.0
        nominal_usable = nominal_h

    usable_height = max(nominal_usable, fixed_stack + 0.055)
    field_height = min(max(usable_height - fixed_stack, 0.055), 0.300)
    pad = usable_height - fixed_stack - field_height

    cursor = 0.012 + pad * 0.35
    deck_center_z = 0.0
    if deck_face == "front":
        deck_center_z = cursor + deck_height / 2.0
        cursor += deck_height + 0.014
    dial_center_z = cursor + _DIAL_HEIGHT / 2.0
    cursor += _DIAL_HEIGHT + 0.014
    grille_center_z = cursor + field_height / 2.0
    straight_height = usable_height
    cabinet_height = usable_height + arch_rise

    dial_width = max(0.100, min(cabinet_width - 2.0 * front_inset - 0.020, 0.340))

    # --- top bay layout ---------------------------------------------------
    handle_seat_y = cabinet_depth / 2.0 - 0.014 - _SADDLE_DEPTH / 2.0
    handle_span = top_bay_width - _HANDLE_SPAN_INSET
    antenna_x = top_bay_width / 2.0 - _ANTENNA_EDGE_INSET
    antenna_y = cabinet_depth / 2.0 - _ANTENNA_EDGE_INSET
    antenna_socket_z = cabinet_height + 0.0135
    deck_center_y = -cabinet_depth / 2.0 + 0.012 + deck_height / 2.0

    if config.antenna_module == "side_swivel_whip":
        antenna_travel = whip_travel
        antenna_mast = max(whip_mast, _ROD_INSERTION + whip_travel + 0.010)
    elif config.antenna_module == "rear_telescoping_mast":
        antenna_travel = mast_travel
        antenna_mast = max(mast_length, _ROD_INSERTION + mast_travel + 0.010)
    else:
        antenna_travel = 0.0
        antenna_mast = 0.0

    handle_rise = fixed_rise if config.carry_handle == "fixed_bail" else folding_rise

    return ResolvedConfig(
        cabinet_form=config.cabinet_form,
        grille_style=config.grille_style,
        speaker_layout=config.speaker_layout,
        control_deck=config.control_deck,
        carry_handle=config.carry_handle,
        antenna_module=config.antenna_module,
        control_count=control_count,
        landscape_width_m=landscape_width,
        landscape_height_ratio=landscape_ratio,
        portable_width_m=portable_width,
        portable_corner_radius_m=portable_radius,
        tombstone_width_m=tombstone_width,
        tombstone_height_ratio=tombstone_ratio,
        boombox_width_m=boombox_width,
        boombox_corner_radius_m=boombox_radius,
        rib_pitch_m=rib_pitch,
        mesh_hole_pitch_m=mesh_pitch,
        bar_pitch_m=bar_pitch,
        single_field_width_ratio=single_ratio,
        stereo_field_gap_m=stereo_gap,
        knob_diameter_m=knob_diameter,
        button_width_m=button_width,
        button_travel_m=button_travel,
        transport_key_width_m=key_width,
        transport_key_travel_m=key_travel,
        top_lip_height_m=top_lip_height,
        fixed_bail_rise_m=fixed_rise,
        folding_bail_rise_m=folding_rise,
        folding_bail_angle_rad=folding_angle,
        blank_badge_width_m=badge_width,
        whip_mast_length_m=whip_mast,
        whip_travel_m=whip_travel,
        mast_length_m=mast_length,
        mast_travel_m=mast_travel,
        palette=int(config.palette) % len(_PALETTES),
        name=config.name,
        cabinet_width_m=cabinet_width,
        cabinet_depth_m=cabinet_depth,
        cabinet_height_m=cabinet_height,
        cabinet_corner_radius_m=corner_radius,
        front_inset_m=front_inset,
        straight_height_m=straight_height,
        top_bay_width_m=top_bay_width,
        deck_face=deck_face,
        control_cap_u_m=cap_u,
        control_cap_v_m=cap_v,
        control_cap_height_m=cap_height,
        control_recess_m=recess,
        control_travel_m=travel,
        control_pitch_m=pitch,
        control_row_width_m=row_width,
        deck_width_m=deck_width,
        deck_height_m=deck_height,
        deck_plate_thickness_m=plate_thickness,
        deck_face_offset_m=face_offset,
        deck_center_z_m=deck_center_z,
        deck_center_y_m=deck_center_y,
        aux_knob_offset_u_m=aux_offset,
        field_count=field_count,
        field_width_m=field_width,
        field_height_m=field_height,
        field_offset_m=field_offset,
        grille_center_z_m=grille_center_z,
        dial_center_z_m=dial_center_z,
        dial_width_m=dial_width,
        handle_span_m=handle_span,
        handle_seat_y_m=handle_seat_y,
        handle_rise_m=handle_rise,
        antenna_x_m=antenna_x,
        antenna_y_m=antenna_y,
        antenna_socket_z_m=antenna_socket_z,
        antenna_mast_length_m=antenna_mast,
        antenna_travel_m=antenna_travel,
    )


# ---------------------------------------------------------------------------
# Small geometry helpers.
# ---------------------------------------------------------------------------


def _materials(model: ArticulatedObject, palette: int):
    colors = _PALETTES[palette]
    return {name: model.material(name, rgba=rgba) for name, rgba in colors.items()}


def _circle_profile(radius: float, segments: int = 22):
    return [
        (
            radius * math.cos(2.0 * math.pi * index / segments),
            radius * math.sin(2.0 * math.pi * index / segments),
        )
        for index in range(segments)
    ]


def _box_mesh(size, center=(0.0, 0.0, 0.0)):
    geometry = BoxGeometry(tuple(float(value) for value in size))
    geometry.translate(float(center[0]), float(center[1]), float(center[2]))
    return geometry


def _merge(pieces):
    base = pieces[0]
    for extra in pieces[1:]:
        base.merge(extra)
    return base


def _prism_z(profile, z0: float, z1: float):
    return LoftGeometry(
        (
            [(x, y, z0) for x, y in profile],
            [(x, y, z1) for x, y in profile],
        ),
        cap=True,
        closed=True,
    )


def _front_prism(profile_xz, depth: float):
    """Extrude a front silhouette (x, height) along depth, front face at -Y."""

    geometry = LoftGeometry(
        (
            [(x, z, 0.0) for x, z in profile_xz],
            [(x, z, depth) for x, z in profile_xz],
        ),
        cap=True,
        closed=True,
    )
    geometry.rotate_x(math.pi / 2.0)
    geometry.translate(0.0, depth / 2.0, 0.0)
    return geometry


def _annular_prism(outer_radius: float, bore_radius: float, z0: float, z1: float):
    """A genuinely hollow tube: the bore is empty for FCL and for volume QC."""

    outer = _circle_profile(outer_radius, 24)
    inner = _circle_profile(bore_radius, 24)
    rings = (
        [(x, y, z0) for x, y in outer],
        [(x, y, z1) for x, y in outer],
        [(x, y, z1) for x, y in inner],
        [(x, y, z0) for x, y in inner],
        [(x, y, z0) for x, y in outer],
    )
    return LoftGeometry(rings, cap=False, closed=True)


def _speaker_fields(r: ResolvedConfig):
    if r.field_count == 1:
        return ((0.0, r.field_width_m),)
    return ((-r.field_offset_m, r.field_width_m), (r.field_offset_m, r.field_width_m))


def _deck_local(r: ResolvedConfig, u: float, v: float, t: float):
    """Map a deck surface coordinate to the deck part's local frame."""

    if r.deck_face == "front":
        return (u, -t, v)
    return (u, v, t)


def _deck_normal(r: ResolvedConfig):
    return (0.0, -1.0, 0.0) if r.deck_face == "front" else (0.0, 0.0, 1.0)


def _deck_child_rpy(r: ResolvedConfig):
    return (math.pi / 2.0, 0.0, 0.0) if r.deck_face == "front" else (0.0, 0.0, 0.0)


def _control_offsets(r: ResolvedConfig):
    return tuple(
        (index - (r.control_count - 1) / 2.0) * r.control_pitch_m
        for index in range(r.control_count)
    )


# ---------------------------------------------------------------------------
# Cabinet forms.
# ---------------------------------------------------------------------------


def _cabinet_form_landscape_cabinet_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "cabinet_form__landscape_cabinet"
    width, height, depth = r.cabinet_width_m, r.cabinet_height_m, r.cabinet_depth_m
    radius = min(r.cabinet_corner_radius_m, 0.24 * min(width, height))
    profile = [
        (x, y + height / 2.0)
        for x, y in rounded_rect_profile(width, height, radius, corner_segments=6)
    ]
    cabinet.visual(
        mesh_from_geometry(_front_prism(profile, depth), f"{tag}__shell"),
        material=mats["shell"],
        name=f"{tag}__shell", material_class_id="wood.polished_varnished",
    )
    # Plinth rail and top cap moulding: the tabletop cabinet reads as furniture.
    # Both stand 1.5 mm proud of the shell so they weld to its surface instead
    # of floating inside it as separate geometry islands.
    cabinet.visual(
        Box((width + 0.003, depth + 0.003, 0.014)),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["shell_dark"],
        name=f"{tag}__plinth_rail", material_class_id="wood.walnut_dark",
    )
    cabinet.visual(
        Box((width + 0.003, depth + 0.003, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, height - 0.004)),
        material=mats["shell_dark"],
        name=f"{tag}__top_cap", material_class_id="wood.walnut_dark",
    )
    grain = _merge(
        [
            _box_mesh(
                (0.006, depth * 0.72, 0.0016),
                (
                    -width / 2.0 + 0.030 + index * (width - 0.060) / 9.0,
                    0.0,
                    height + 0.0004,
                ),
            )
            for index in range(10)
        ]
    )
    cabinet.visual(
        mesh_from_geometry(grain, f"{tag}__top_grain"),
        material=mats["trim"],
        name=f"{tag}__top_grain", material_class_id="wood.patterned_decorative",
    )


def _cabinet_form_portable_slab_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "cabinet_form__portable_slab"
    width, height, depth = r.cabinet_width_m, r.cabinet_height_m, r.cabinet_depth_m
    radius = min(r.cabinet_corner_radius_m, 0.32 * min(width, height))
    profile = [
        (x, y + height / 2.0)
        for x, y in rounded_rect_profile(width, height, radius, corner_segments=8)
    ]
    cabinet.visual(
        mesh_from_geometry(_front_prism(profile, depth), f"{tag}__shell"),
        material=mats["shell"],
        name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # Shallow raised control ledge along the top face, as on the tan portable.
    cabinet.visual(
        Box((width - 0.048, depth * 0.62, 0.005)),
        origin=Origin(xyz=(0.0, -depth * 0.13, height - 0.001)),
        material=mats["shell_dark"],
        name=f"{tag}__top_ledge", material_class_id="plastic.opaque_glossy_molded",
    )
    for side, sign in enumerate((-1.0, 1.0)):
        cabinet.visual(
            Box((0.010, depth * 0.55, height * 0.42)),
            origin=Origin(xyz=(sign * (width / 2.0 - 0.003), 0.0, height * 0.50)),
            material=mats["shell_dark"],
            name=f"{tag}__side_pad_{side}", material_class_id="rubber.smooth_plain",
        )


def _tombstone_profile(r: ResolvedConfig, segments: int = 12):
    width = r.cabinet_width_m
    height = r.cabinet_height_m
    straight = r.straight_height_m
    arch_radius = width / 2.0
    cosine = min(1.0, max(0.0, (r.top_bay_width_m / 2.0) / arch_radius))
    limit = math.acos(cosine)
    points = [(-width / 2.0, 0.0), (width / 2.0, 0.0)]
    for index in range(segments + 1):
        angle = limit * index / segments
        points.append((arch_radius * math.cos(angle), straight + arch_radius * math.sin(angle)))
    for index in range(segments + 1):
        angle = math.pi - limit + limit * index / segments
        points.append((arch_radius * math.cos(angle), straight + arch_radius * math.sin(angle)))
    points.append((-width / 2.0, straight))
    # Guard the flat crown against a degenerate zero-length span.
    points[len(points) - segments - 3] = (r.top_bay_width_m / 2.0, height)
    return points


def _cabinet_form_tombstone_upright_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "cabinet_form__tombstone_upright"
    width, depth = r.cabinet_width_m, r.cabinet_depth_m
    cabinet.visual(
        mesh_from_geometry(_front_prism(_tombstone_profile(r), depth), f"{tag}__shell"),
        material=mats["shell"],
        name=f"{tag}__shell", material_class_id="wood.polished_varnished",
    )
    cabinet.visual(
        Box((width + 0.003, depth + 0.003, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, 0.011)),
        material=mats["shell_dark"],
        name=f"{tag}__base_moulding", material_class_id="wood.walnut_dark",
    )
    side_trim = _merge(
        [
            _box_mesh(
                (0.0018, depth * 0.70, 0.006),
                (
                    sign * (width / 2.0 - 0.0004),
                    0.0,
                    r.straight_height_m * (0.18 + 0.20 * index),
                ),
            )
            for index in range(4)
            for sign in (-1.0, 1.0)
        ]
    )
    cabinet.visual(
        mesh_from_geometry(side_trim, f"{tag}__side_trim"),
        material=mats["trim"],
        name=f"{tag}__side_trim", material_class_id="wood.patterned_decorative",
    )
    cabinet.visual(
        Box((r.top_bay_width_m - 0.014, depth + 0.003, 0.007)),
        origin=Origin(xyz=(0.0, 0.0, r.cabinet_height_m - 0.0025)),
        material=mats["shell_dark"],
        name=f"{tag}__crown_platform", material_class_id="wood.walnut_dark",
    )


def _cabinet_form_boombox_slab_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "cabinet_form__boombox_slab"
    width, height, depth = r.cabinet_width_m, r.cabinet_height_m, r.cabinet_depth_m
    radius = min(r.cabinet_corner_radius_m, 0.45 * min(width, depth))
    plan = rounded_rect_profile(width, depth, radius, corner_segments=7)
    cabinet.visual(
        mesh_from_geometry(_prism_z(plan, 0.010, height), f"{tag}__shell"),
        material=mats["shell"],
        name=f"{tag}__shell", material_class_id="plastic.opaque_glossy_molded",
    )
    pads = []
    for x_sign, y_sign in ((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0)):
        pad = CylinderGeometry(0.013, 0.012, radial_segments=16)
        pad.translate(
            x_sign * (width / 2.0 - 0.040),
            y_sign * (depth / 2.0 - 0.034),
            0.006,
        )
        pads.append(pad)
    cabinet.visual(
        mesh_from_geometry(_merge(pads), f"{tag}__feet"),
        material=mats["trim"],
        name=f"{tag}__feet", material_class_id="rubber.smooth_plain",
    )
    cabinet.visual(
        Box((r.top_bay_width_m + 0.003, depth - 2.0 * radius - 0.006, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, height - 0.002)),
        material=mats["shell_dark"],
        name=f"{tag}__deck_lip", material_class_id="plastic.opaque_glossy_molded",
    )
    cabinet.visual(
        Box((0.014, 0.010, height * 0.34)),
        origin=Origin(xyz=(0.0, depth / 2.0 - 0.004, height * 0.42)),
        material=mats["shell_dark"],
        name=f"{tag}__rear_bass_port", material_class_id="plastic.opaque_glossy_molded",
    )


_CABINET_BUILDERS = {
    "landscape_cabinet": _cabinet_form_landscape_cabinet_build,
    "portable_slab": _cabinet_form_portable_slab_build,
    "tombstone_upright": _cabinet_form_tombstone_upright_build,
    "boombox_slab": _cabinet_form_boombox_slab_build,
}


# ---------------------------------------------------------------------------
# Speaker layout: how many acoustic fields the front face carries.
# ---------------------------------------------------------------------------


def _speaker_field_backdrop(cabinet, r: ResolvedConfig, mats, tag: str) -> None:
    front_y = -r.cabinet_depth_m / 2.0
    for index, (center_x, width) in enumerate(_speaker_fields(r)):
        cabinet.visual(
            Box((width + 0.012, 0.010, r.field_height_m + 0.012)),
            origin=Origin(xyz=(center_x, front_y + 0.004, r.grille_center_z_m)),
            material=mats["trim"],
            name=f"{tag}__field_bezel_{index}", material_class_id="metal.blackened_gunmetal",
        )
        cabinet.visual(
            Cylinder(
                radius=0.42 * min(width, r.field_height_m),
                length=0.008,
            ),
            origin=Origin(
                xyz=(center_x, front_y + 0.002, r.grille_center_z_m),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["backdrop"],
            name=f"{tag}__cone_{index}", material_class_id="paper.plain_sheet",
        )


def _speaker_layout_single_field_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "speaker_layout__single_field"
    _speaker_field_backdrop(cabinet, r, mats, tag)
    front_y = -r.cabinet_depth_m / 2.0
    cabinet.visual(
        Box((r.field_width_m * 0.30, 0.006, 0.0035)),
        origin=Origin(
            xyz=(
                0.0,
                front_y + 0.001,
                r.grille_center_z_m - r.field_height_m / 2.0 - 0.008,
            )
        ),
        material=mats["metal"],
        name=f"{tag}__badge_bar", material_class_id="metal.brushed_silver",
    )


def _speaker_layout_dual_stereo_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "speaker_layout__dual_stereo"
    _speaker_field_backdrop(cabinet, r, mats, tag)
    front_y = -r.cabinet_depth_m / 2.0
    cabinet.visual(
        Box((max(0.008, r.stereo_field_gap_m - 0.010), 0.008, r.field_height_m * 0.86)),
        origin=Origin(xyz=(0.0, front_y + 0.002, r.grille_center_z_m)),
        material=mats["shell_dark"],
        name=f"{tag}__center_spine", material_class_id="plastic.opaque_glossy_molded",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        cabinet.visual(
            Box((0.0055, 0.006, r.field_height_m * 0.20)),
            origin=Origin(
                xyz=(
                    sign * (r.field_offset_m + r.field_width_m / 2.0 + 0.004),
                    front_y + 0.001,
                    r.grille_center_z_m,
                )
            ),
            material=mats["metal"],
            name=f"{tag}__channel_mark_{index}", material_class_id="metal.brushed_silver",
        )


_SPEAKER_BUILDERS = {
    "single_field": _speaker_layout_single_field_build,
    "dual_stereo": _speaker_layout_dual_stereo_build,
}


# ---------------------------------------------------------------------------
# Grille styles: what fills each speaker field.
# ---------------------------------------------------------------------------


def _grille_frame(width: float, height: float):
    rail = 0.006
    return [
        _box_mesh((width, 0.008, rail), (0.0, -0.003, height / 2.0 - rail / 2.0)),
        _box_mesh((width, 0.008, rail), (0.0, -0.003, -height / 2.0 + rail / 2.0)),
        _box_mesh((rail, 0.008, height), (-width / 2.0 + rail / 2.0, -0.003, 0.0)),
        _box_mesh((rail, 0.008, height), (width / 2.0 - rail / 2.0, -0.003, 0.0)),
    ]


def _grille_style_horizontal_ribbed_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "grille_style__horizontal_ribbed"
    front_y = -r.cabinet_depth_m / 2.0
    for index, (center_x, width) in enumerate(_speaker_fields(r)):
        inner_h = r.field_height_m - 0.016
        count = max(3, min(34, int(inner_h / r.rib_pitch_m)))
        step = inner_h / count
        pieces = _grille_frame(width, r.field_height_m)
        for rib in range(count):
            z = -inner_h / 2.0 + step * (rib + 0.5)
            pieces.append(_box_mesh((width - 0.014, 0.006, step * 0.52), (0.0, -0.0035, z)))
        cabinet.visual(
            mesh_from_geometry(_merge(pieces), f"{tag}__field_{index}"),
            origin=Origin(xyz=(center_x, front_y + 0.001, r.grille_center_z_m)),
            material=mats["grille"],
            name=f"{tag}__field_{index}", material_class_id="fabric.corduroy_ribbed",
        )


def _grille_style_perforated_mesh_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "grille_style__perforated_mesh"
    front_y = -r.cabinet_depth_m / 2.0
    for index, (center_x, width) in enumerate(_speaker_fields(r)):
        inner_w = width - 0.016
        inner_h = r.field_height_m - 0.016
        pitch = r.mesh_hole_pitch_m
        columns = max(3, min(40, int(inner_w / pitch)))
        rows = max(3, min(30, int(inner_h / pitch)))
        col_step = inner_w / columns
        row_step = inner_h / rows
        strip = min(0.0022, col_step * 0.34)
        pieces = _grille_frame(width, r.field_height_m)
        for column in range(columns + 1):
            x = -inner_w / 2.0 + col_step * column
            pieces.append(_box_mesh((strip, 0.005, inner_h), (x, -0.0030, 0.0)))
        for row in range(rows + 1):
            z = -inner_h / 2.0 + row_step * row
            pieces.append(_box_mesh((inner_w, 0.005, strip), (0.0, -0.0030, z)))
        cabinet.visual(
            mesh_from_geometry(_merge(pieces), f"{tag}__field_{index}"),
            origin=Origin(xyz=(center_x, front_y + 0.001, r.grille_center_z_m)),
            material=mats["grille"],
            name=f"{tag}__field_{index}", material_class_id="fabric.open_mesh",
        )


def _grille_style_vertical_bar_build(cabinet, r: ResolvedConfig, mats) -> None:
    tag = "grille_style__vertical_bar"
    front_y = -r.cabinet_depth_m / 2.0
    for index, (center_x, width) in enumerate(_speaker_fields(r)):
        inner_w = width - 0.016
        count = max(3, min(46, int(inner_w / r.bar_pitch_m)))
        step = inner_w / count
        pieces = _grille_frame(width, r.field_height_m)
        for bar in range(count):
            x = -inner_w / 2.0 + step * (bar + 0.5)
            pieces.append(
                _box_mesh(
                    (step * 0.46, 0.006, r.field_height_m - 0.014),
                    (x, -0.0035, 0.0),
                )
            )
        cabinet.visual(
            mesh_from_geometry(_merge(pieces), f"{tag}__field_{index}"),
            origin=Origin(xyz=(center_x, front_y + 0.001, r.grille_center_z_m)),
            material=mats["grille"],
            name=f"{tag}__field_{index}", material_class_id="fabric.webbing",
        )


_GRILLE_BUILDERS = {
    "horizontal_ribbed": _grille_style_horizontal_ribbed_build,
    "perforated_mesh": _grille_style_perforated_mesh_build,
    "vertical_bar": _grille_style_vertical_bar_build,
}


# ---------------------------------------------------------------------------
# Shared front tuning dial (host geometry, not a slot).
# ---------------------------------------------------------------------------


def _add_tuning_dial(cabinet, r: ResolvedConfig, mats) -> None:
    tag = f"cabinet_form__{r.cabinet_form}"
    front_y = -r.cabinet_depth_m / 2.0
    width = r.dial_width_m
    cabinet.visual(
        Box((width, 0.010, _DIAL_HEIGHT)),
        origin=Origin(xyz=(0.0, front_y + 0.003, r.dial_center_z_m)),
        material=mats["trim"],
        name=f"{tag}__dial_bezel", material_class_id="metal.blackened_gunmetal",
    )
    cabinet.visual(
        Box((width - 0.012, 0.005, _DIAL_HEIGHT - 0.010)),
        origin=Origin(xyz=(0.0, front_y - 0.0025, r.dial_center_z_m)),
        material=mats["dial"],
        name=f"{tag}__dial_face", material_class_id="plastic.opaque_glossy_molded",
    )
    ticks = []
    span = width - 0.030
    for index in range(13):
        x = -span / 2.0 + span * index / 12.0
        tall = 0.016 if index % 3 == 0 else 0.009
        ticks.append(_box_mesh((0.0016, 0.004, tall), (x, -0.0055, 0.006)))
        ticks.append(_box_mesh((0.0016, 0.004, tall * 0.8), (x, -0.0055, -0.010)))
    ticks.append(_box_mesh((span, 0.004, 0.0014), (0.0, -0.0055, 0.016)))
    geometry = _merge(ticks)
    cabinet.visual(
        mesh_from_geometry(geometry, f"{tag}__dial_scale"),
        origin=Origin(xyz=(0.0, front_y - 0.0005, r.dial_center_z_m)),
        material=mats["ink"],
        name=f"{tag}__dial_scale", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    cabinet.visual(
        Box((0.0035, 0.005, _DIAL_HEIGHT - 0.008)),
        origin=Origin(xyz=(span * 0.18, front_y - 0.0058, r.dial_center_z_m)),
        material=mats["accent"],
        name=f"{tag}__dial_pointer", material_class_id="plastic.opaque_glossy_molded",
    )


# ---------------------------------------------------------------------------
# Control deck: the pressable / rotatable module and its host opening plate.
# ---------------------------------------------------------------------------


def _control_bay_interface(r: ResolvedConfig) -> PlaneInterface:
    if r.deck_face == "front":
        return PlaneInterface(
            name="cabinet_form.control_bay",
            point=(0.0, -r.cabinet_depth_m / 2.0, r.deck_center_z_m),
            normal=(0.0, -1.0, 0.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(
                r.cabinet_width_m - 2.0 * r.front_inset_m,
                r.deck_height_m + 0.020,
            ),
        )
    return PlaneInterface(
        name="cabinet_form.control_bay",
        point=(0.0, r.deck_center_y_m, r.cabinet_height_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.top_bay_width_m - 0.020, r.deck_height_m + 0.020),
    )


def _deck_mount_interface(r: ResolvedConfig) -> PlaneInterface:
    normal = (0.0, 1.0, 0.0) if r.deck_face == "front" else (0.0, 0.0, -1.0)
    return PlaneInterface(
        name="control_deck.deck_mount",
        point=(0.0, 0.0, 0.0),
        normal=normal,
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.deck_width_m, r.deck_height_m),
    )


def _control_openings(r: ResolvedConfig):
    """(u, v, kind, size_u, size_v) for every opening cut in the deck plate."""

    rows = []
    for u in _control_offsets(r):
        if r.control_deck == "rotary_knob_bank":
            rows.append((u, 0.0, "round", r.control_cap_u_m, r.control_cap_v_m))
        else:
            rows.append((u, 0.0, "rect", r.control_cap_u_m, r.control_cap_v_m))
    if r.control_deck == "transport_key_deck":
        aux = _AUX_KNOB_DIAMETER * _SKIRT_RATIO
        for sign in (-1.0, 1.0):
            rows.append((sign * r.aux_knob_offset_u_m, 0.0, "round", aux, aux))
    return tuple(rows)


def _deck_box_size(r: ResolvedConfig, size_u: float, size_v: float, size_t: float):
    if r.deck_face == "front":
        return (size_u, size_t, size_v)
    return (size_u, size_v, size_t)


def _add_deck_plate(deck, r: ResolvedConfig, mats, tag: str) -> None:
    """Rails and separators leave one real opening per control.

    The openings are formed by construction rather than by a boolean cut, so
    every control passes through its host plate instead of intersecting it.
    """

    openings = sorted(_control_openings(r), key=lambda row: row[0])
    opening_v = max(row[4] for row in openings) + 2.0 * _HOLE_CLEARANCE
    rail_v = (r.deck_height_m - opening_v) / 2.0
    plate_t = r.deck_plate_thickness_m
    center_t = (r.deck_face_offset_m - _DECK_EMBED) / 2.0
    # Substrate web behind every well.  The plate is thick enough that a fully
    # pressed cap still stops _WEB_CLEARANCE above it, so it never becomes a
    # travel stop, but it is what the deck is actually bolted to.
    deck.visual(
        Box(_deck_box_size(r, r.deck_width_m, r.deck_height_m, _DECK_WEB_T)),
        origin=Origin(xyz=_deck_local(r, 0.0, 0.0, -_DECK_EMBED + _DECK_WEB_T / 2.0)),
        material=mats["trim"],
        name=f"{tag}__deck_web", material_class_id="tech.control_interface",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        deck.visual(
            Box(_deck_box_size(r, r.deck_width_m, rail_v, plate_t)),
            origin=Origin(
                xyz=_deck_local(r, 0.0, sign * (r.deck_height_m - rail_v) / 2.0, center_t)
            ),
            material=mats["trim"],
            name=f"{tag}__deck_rail_{index}", material_class_id="tech.control_interface",
        )
    edges: list[tuple[float, float]] = []
    cursor = -r.deck_width_m / 2.0
    for u, _v, _kind, size_u, _size_v in openings:
        left = u - size_u / 2.0 - _HOLE_CLEARANCE
        edges.append((cursor, left))
        cursor = u + size_u / 2.0 + _HOLE_CLEARANCE
    edges.append((cursor, r.deck_width_m / 2.0))
    for index, (start, end) in enumerate(edges):
        width = end - start
        if width <= 0.0008:
            continue
        deck.visual(
            Box(_deck_box_size(r, width, r.deck_height_m, plate_t)),
            origin=Origin(xyz=_deck_local(r, (start + end) / 2.0, 0.0, center_t)),
            material=mats["trim"],
            name=f"{tag}__deck_separator_{index}", material_class_id="tech.control_interface",
        )


def _mount_control_deck(model: ArticulatedObject, cabinet, r: ResolvedConfig, mats):
    tag = f"control_deck__{r.control_deck}"
    deck = model.part(
        "control_deck",
        meta={
            "role": "control_deck",
            "slot": "control_deck",
            "candidate": r.control_deck,
        },
    )
    _add_deck_plate(deck, r, mats, tag)
    mate = mate_planes(_control_bay_interface(r), _deck_mount_interface(r))
    model.articulation(
        f"{tag}__deck_mount",
        ArticulationType.FIXED,
        parent=cabinet,
        child=deck,
        origin=mate.origin,
    )
    return deck


def _knob_mesh(diameter: float, height: float, name: str):
    skirt_r = diameter * _SKIRT_RATIO / 2.0
    body_r = diameter / 2.0
    pieces = [CylinderGeometry(skirt_r, 0.005, radial_segments=22)]
    pieces[0].translate(0.0, 0.0, 0.0025)
    body = CylinderGeometry(body_r, height, radial_segments=22)
    body.translate(0.0, 0.0, height / 2.0)
    pieces.append(body)
    for index in range(14):
        angle = 2.0 * math.pi * index / 14.0
        flute = BoxGeometry((0.0018, body_r * 0.30, height * 0.80))
        flute.rotate_z(angle)
        flute.translate(
            body_r * 0.94 * math.cos(angle),
            body_r * 0.94 * math.sin(angle),
            height * 0.42,
        )
        pieces.append(flute)
    return mesh_from_geometry(_merge(pieces), name)


def _add_rotary_knob(
    model: ArticulatedObject,
    deck,
    r: ResolvedConfig,
    mats,
    *,
    tag: str,
    index: int,
    u: float,
    diameter: float,
    height: float,
    recess: float,
    knob_mesh,
):
    knob = model.part(
        f"{tag}__knob_{index:02d}",
        meta={
            "role": "rotary_knob",
            "slot": "control_deck",
            "candidate": r.control_deck,
        },
    )
    knob.visual(knob_mesh, material=mats["metal"], name=f"{tag}__knob_body_{index:02d}", material_class_id="metal.aluminum_bare")
    knob.visual(
        Box((0.0026, diameter * 0.34, 0.0018)),
        origin=Origin(xyz=(0.0, diameter * 0.20, height + 0.0005)),
        material=mats["accent"],
        name=f"{tag}__knob_mark_{index:02d}", material_class_id="plastic.opaque_glossy_molded",
    )
    seat = r.deck_face_offset_m - recess
    provider = AxisInterface(
        name="control_deck.knob_axis",
        point=_deck_local(r, u, 0.0, seat),
        axis=_deck_normal(r),
        radial=(0.0, 0.0, 1.0) if r.deck_face == "front" else (0.0, 1.0, 0.0),
        radius=diameter * _SKIRT_RATIO / 2.0 + _HOLE_CLEARANCE,
    )
    consumer = AxisInterface(
        name="control_deck.knob_shaft",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(0.0, 1.0, 0.0),
        radius=diameter * _SKIRT_RATIO / 2.0,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__knob_joint_{index:02d}"
    model.articulation(
        joint,
        ArticulationType.CONTINUOUS,
        parent=deck,
        child=knob,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=0.6, velocity=6.0),
    )
    register_interface_mate(model, joint, mate)


def _add_press_control(
    model: ArticulatedObject,
    deck,
    r: ResolvedConfig,
    mats,
    *,
    tag: str,
    index: int,
    u: float,
    cap_mesh,
):
    cap = model.part(
        f"{tag}__key_{index:02d}",
        meta={
            "role": "press_button",
            "slot": "control_deck",
            "candidate": r.control_deck,
        },
    )
    cap.visual(cap_mesh, material=mats["cap"], name=f"{tag}__cap_{index:02d}", material_class_id="plastic.opaque_glossy_molded")
    bars = 1 + index % 3
    for bar in range(bars):
        cap.visual(
            Box((r.control_cap_u_m * 0.42, 0.0008, 0.0008)),
            origin=Origin(
                xyz=(
                    0.0,
                    (bar - (bars - 1) / 2.0) * 0.0016,
                    r.control_cap_height_m + 0.0002,
                )
            ),
            material=mats["ink"],
            name=f"{tag}__legend_{index:02d}_{bar}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    seat = r.deck_face_offset_m - r.control_recess_m
    model.articulation(
        f"{tag}__press_joint_{index:02d}",
        ArticulationType.PRISMATIC,
        parent=deck,
        child=cap,
        origin=Origin(xyz=_deck_local(r, u, 0.0, seat), rpy=_deck_child_rpy(r)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.08, lower=0.0, upper=r.control_travel_m),
        meta={"motion_qc_repeat_group": "audio_control_press"},
    )


def _press_cap_mesh(r: ResolvedConfig, name: str):
    profile = rounded_rect_profile(
        r.control_cap_u_m,
        r.control_cap_v_m,
        min(0.0024, 0.24 * min(r.control_cap_u_m, r.control_cap_v_m)),
        corner_segments=5,
    )
    return mesh_from_geometry(_prism_z(profile, 0.0, r.control_cap_height_m), name)


def _control_deck_rotary_knob_bank_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
):
    tag = "control_deck__rotary_knob_bank"
    deck = _mount_control_deck(model, cabinet, r, mats)
    knob_mesh = _knob_mesh(r.knob_diameter_m, r.control_cap_height_m, f"{tag}__knob_body")
    for index, u in enumerate(_control_offsets(r)):
        _add_rotary_knob(
            model,
            deck,
            r,
            mats,
            tag=tag,
            index=index,
            u=u,
            diameter=r.knob_diameter_m,
            height=r.control_cap_height_m,
            recess=r.control_recess_m,
            knob_mesh=knob_mesh,
        )
    return deck


def _control_deck_push_button_row_build(model: ArticulatedObject, cabinet, r: ResolvedConfig, mats):
    tag = "control_deck__push_button_row"
    deck = _mount_control_deck(model, cabinet, r, mats)
    cap_mesh = _press_cap_mesh(r, f"{tag}__cap")
    for index, u in enumerate(_control_offsets(r)):
        _add_press_control(model, deck, r, mats, tag=tag, index=index, u=u, cap_mesh=cap_mesh)
    return deck


def _control_deck_transport_key_deck_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
):
    tag = "control_deck__transport_key_deck"
    deck = _mount_control_deck(model, cabinet, r, mats)
    cap_mesh = _press_cap_mesh(r, f"{tag}__cap")
    for index, u in enumerate(_control_offsets(r)):
        _add_press_control(model, deck, r, mats, tag=tag, index=index, u=u, cap_mesh=cap_mesh)
    aux_height = _AUX_KNOB_DIAMETER * _KNOB_HEIGHT_RATIO
    aux_mesh = _knob_mesh(_AUX_KNOB_DIAMETER, aux_height, f"{tag}__aux_knob_body")
    for index, sign in enumerate((-1.0, 1.0)):
        _add_rotary_knob(
            model,
            deck,
            r,
            mats,
            tag=tag,
            index=index,
            u=sign * r.aux_knob_offset_u_m,
            diameter=_AUX_KNOB_DIAMETER,
            height=aux_height,
            recess=_KNOB_RECESS,
            knob_mesh=aux_mesh,
        )
    return deck


_CONTROL_BUILDERS = {
    "rotary_knob_bank": _control_deck_rotary_knob_bank_build,
    "push_button_row": _control_deck_push_button_row_build,
    "transport_key_deck": _control_deck_transport_key_deck_build,
}


# ---------------------------------------------------------------------------
# Carry handle.
# ---------------------------------------------------------------------------


def _handle_seat_interface(r: ResolvedConfig) -> PlaneInterface:
    return PlaneInterface(
        name="cabinet_form.handle_seat",
        point=(0.0, r.handle_seat_y_m, r.cabinet_height_m),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.top_bay_width_m - 0.018, _SADDLE_DEPTH + 0.012),
    )


def _bail_arch_mesh(span: float, rise: float, name: str, base_z: float = 0.024):
    half = span / 2.0
    path = [
        (-half, 0.0, base_z),
        (-half * 0.62, 0.0, base_z + (rise - base_z) * 0.80),
        (0.0, 0.0, rise),
        (half * 0.62, 0.0, base_z + (rise - base_z) * 0.80),
        (half, 0.0, base_z),
    ]
    geometry = sweep_profile_along_spline(
        path,
        profile=rounded_rect_profile(0.013, 0.009, 0.003, corner_segments=3),
        samples_per_segment=8,
        spline="catmull_rom",
        cap_profile=True,
    )
    return mesh_from_geometry(geometry, name)


def _carry_handle_molded_top_lip_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
) -> None:
    tag = "carry_handle__molded_top_lip"
    cabinet.visual(
        Box(
            (
                r.top_bay_width_m - 0.040,
                0.016,
                r.top_lip_height_m,
            )
        ),
        origin=Origin(
            xyz=(
                0.0,
                r.handle_seat_y_m,
                r.cabinet_height_m - 0.002 + r.top_lip_height_m / 2.0,
            )
        ),
        material=mats["shell_dark"],
        name=f"{tag}__rear_lip", material_class_id="plastic.opaque_glossy_molded",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        cabinet.visual(
            Box((0.020, _SADDLE_DEPTH, r.top_lip_height_m * 0.7)),
            origin=Origin(
                xyz=(
                    sign * (r.top_bay_width_m / 2.0 - 0.030),
                    r.handle_seat_y_m - 0.020,
                    r.cabinet_height_m - 0.002 + r.top_lip_height_m * 0.35,
                )
            ),
            material=mats["trim"],
            name=f"{tag}__grip_pad_{index}", material_class_id="rubber.smooth_plain",
        )


def _carry_handle_fixed_bail_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
) -> None:
    tag = "carry_handle__fixed_bail"
    handle = model.part(
        "carry_handle",
        meta={"role": "carry_handle", "slot": "carry_handle", "candidate": r.carry_handle},
    )
    # The handle's own frame origin sits in its left saddle, so the fixed mount
    # is solved at a real seated foot rather than in mid-air under the arch.
    span = r.handle_span_m
    for index, offset in enumerate((0.0, span)):
        handle.visual(
            Box((2.0 * _SADDLE_HALF_W, _SADDLE_DEPTH, 0.040)),
            origin=Origin(xyz=(offset, 0.0, 0.020 - 0.0008)),
            material=mats["shell"],
            name=f"{tag}__saddle_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    arch = _bail_arch_mesh(span, r.handle_rise_m, f"{tag}__arch")
    handle.visual(
        arch,
        origin=Origin(xyz=(span / 2.0, 0.0, 0.0)),
        material=mats["shell"],
        name=f"{tag}__arch", material_class_id="metal.paint_coated",
    )
    consumer = PlaneInterface(
        name="carry_handle.seat_mount",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(2.0 * _SADDLE_HALF_W, _SADDLE_DEPTH),
    )
    mate = mate_planes(_handle_seat_interface(r), consumer, uv=(-span / 2.0, 0.0))
    model.articulation(
        f"{tag}__seat_joint",
        ArticulationType.FIXED,
        parent=cabinet,
        child=handle,
        origin=mate.origin,
    )


def _carry_handle_folding_bail_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
) -> None:
    tag = "carry_handle__folding_bail"
    half = r.handle_span_m / 2.0
    hinge_z = r.cabinet_height_m + 0.016
    for index, sign in enumerate((-1.0, 1.0)):
        cabinet.visual(
            Box((0.018, 0.022, 0.024)),
            origin=Origin(
                xyz=(
                    sign * (half + 0.019),
                    r.handle_seat_y_m,
                    r.cabinet_height_m + 0.008,
                )
            ),
            material=mats["shell_dark"],
            name=f"{tag}__pivot_pedestal_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        cabinet.visual(
            Cylinder(radius=0.012, length=0.020),
            origin=Origin(
                xyz=(sign * (half + 0.016), r.handle_seat_y_m, hinge_z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["trim"],
            name=f"{tag}__pivot_boss_{index}", material_class_id="metal.blackened_gunmetal",
        )
    handle = model.part(
        "carry_handle",
        meta={"role": "carry_handle", "slot": "carry_handle", "candidate": r.carry_handle},
    )
    for index, sign in enumerate((-1.0, 1.0)):
        handle.visual(
            Cylinder(radius=0.010, length=0.014),
            origin=Origin(xyz=(sign * half, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"{tag}__knuckle_{index}", material_class_id="metal.aluminum_bare",
        )
    handle.visual(
        _bail_arch_mesh(r.handle_span_m, r.handle_rise_m, f"{tag}__arch", base_z=0.004),
        material=mats["shell_dark"],
        name=f"{tag}__arch", material_class_id="metal.paint_coated",
    )
    provider = AxisInterface(
        name="cabinet_form.handle_hinge",
        point=(0.0, r.handle_seat_y_m, hinge_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.012,
    )
    consumer = AxisInterface(
        name="carry_handle.hinge_axis",
        point=(0.0, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.010,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    joint = f"{tag}__hinge_joint"
    model.articulation(
        joint,
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=handle,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=3.0,
            velocity=2.0,
            lower=-r.folding_bail_angle_rad,
            upper=0.0,
        ),
    )
    register_interface_mate(model, joint, mate)


_HANDLE_BUILDERS = {
    "molded_top_lip": _carry_handle_molded_top_lip_build,
    "fixed_bail": _carry_handle_fixed_bail_build,
    "folding_bail": _carry_handle_folding_bail_build,
}


# ---------------------------------------------------------------------------
# Antenna module.
# ---------------------------------------------------------------------------


def _antenna_socket_boss(cabinet, r: ResolvedConfig, mats, tag: str) -> None:
    # The boss top stops 8 mm below the swivel centre so the coaxial knuckle
    # only grazes it; a rotating knuckle that is coaxial with its own hinge
    # sweeps no new volume.
    cabinet.visual(
        Cylinder(radius=0.010, length=0.014),
        origin=Origin(xyz=(r.antenna_x_m, r.antenna_y_m, r.cabinet_height_m - 0.001)),
        material=mats["trim"],
        name=f"{tag}__socket_boss", material_class_id="metal.blackened_gunmetal",
    )


def _hollow_mast_mesh(length: float, outer: float, bore: float, name: str):
    return mesh_from_geometry(_annular_prism(outer, bore, 0.0, length), name)


def _build_telescoping_antenna(
    model: ArticulatedObject,
    cabinet,
    r: ResolvedConfig,
    mats,
    *,
    tag: str,
    swivel_axis: tuple[float, float, float],
    knuckle_rpy: tuple[float, float, float],
    stepped: bool,
) -> None:
    _antenna_socket_boss(cabinet, r, mats, tag)
    base = model.part(
        f"{tag}__base",
        meta={
            "role": "antenna_base",
            "slot": "antenna_module",
            "candidate": r.antenna_module,
        },
    )
    # The knuckle is a cylinder about the swivel axis itself, so raking it does
    # not sweep it into the cabinet boss it sits on.
    base.visual(
        Cylinder(radius=0.008, length=0.017),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=knuckle_rpy),
        material=mats["trim"],
        name=f"{tag}__knuckle", material_class_id="metal.blackened_gunmetal",
    )
    mast_base = 0.004
    mast_length = r.antenna_mast_length_m
    base.visual(
        _hollow_mast_mesh(mast_length, 0.0060, _ROD_BORE, f"{tag}__mast_tube"),
        origin=Origin(xyz=(0.0, 0.0, mast_base)),
        material=mats["metal"],
        name=f"{tag}__mast_tube", material_class_id="metal.stainless_matte",
    )
    if stepped:
        base.visual(
            _hollow_mast_mesh(0.022, 0.0080, _ROD_BORE, f"{tag}__mast_collar"),
            origin=Origin(xyz=(0.0, 0.0, mast_base + 0.002)),
            material=mats["metal"],
            name=f"{tag}__mast_collar", material_class_id="metal.stainless_matte",
        )
    else:
        base.visual(
            mesh_from_geometry(
                TorusGeometry(
                    radius=0.0068,
                    tube=0.0013,
                    radial_segments=10,
                    tubular_segments=20,
                ),
                f"{tag}__mast_lip",
            ),
            origin=Origin(xyz=(0.0, 0.0, mast_base + mast_length - 0.0012)),
            material=mats["metal"],
            name=f"{tag}__mast_lip", material_class_id="metal.stainless_matte",
        )

    provider = AxisInterface(
        name="cabinet_form.antenna_socket",
        point=(r.antenna_x_m, r.antenna_y_m, r.antenna_socket_z_m),
        axis=swivel_axis,
        radial=(0.0, 0.0, 1.0),
        radius=0.010,
    )
    consumer = AxisInterface(
        name="antenna_module.socket_mount",
        point=(0.0, 0.0, 0.0),
        axis=swivel_axis,
        radial=(0.0, 0.0, 1.0),
        radius=0.008,
    )
    mate = mate_axes(provider, consumer, require_fit=True)
    swivel = f"{tag}__swivel_joint"
    model.articulation(
        swivel,
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=base,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.radians(85.0)),
    )
    register_interface_mate(model, swivel, mate)

    rod = model.part(
        f"{tag}__rod",
        meta={
            "role": "antenna_rod",
            "slot": "antenna_module",
            "candidate": r.antenna_module,
        },
    )
    travel = r.antenna_travel_m
    rod_length = travel + _ROD_INSERTION + 0.030
    rod.visual(
        Cylinder(radius=_ROD_RADIUS, length=rod_length),
        origin=Origin(xyz=(0.0, 0.0, rod_length / 2.0 - _ROD_INSERTION)),
        material=mats["metal"],
        name=f"{tag}__rod_shaft", material_class_id="metal.stainless_matte",
    )
    if stepped:
        rod.visual(
            Cylinder(radius=0.0035, length=0.007),
            origin=Origin(xyz=(0.0, 0.0, rod_length - _ROD_INSERTION)),
            material=mats["trim"],
            name=f"{tag}__rod_tip", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        rod.visual(
            Sphere(radius=0.0035),
            origin=Origin(xyz=(0.0, 0.0, rod_length - _ROD_INSERTION)),
            material=mats["trim"],
            name=f"{tag}__rod_tip", material_class_id="plastic.opaque_glossy_molded",
        )
    rod_provider = AxisInterface(
        name="antenna_module.slide_bore",
        point=(0.0, 0.0, mast_base + mast_length),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_ROD_BORE,
    )
    rod_consumer = AxisInterface(
        name="antenna_module.rod_axis",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_ROD_RADIUS,
    )
    rod_mate = mate_axes(rod_provider, rod_consumer, require_fit=True)
    extend = f"{tag}__extend_joint"
    model.articulation(
        extend,
        ArticulationType.PRISMATIC,
        parent=base,
        child=rod,
        origin=rod_mate.origin,
        axis=rod_mate.axis,
        motion_limits=MotionLimits(effort=1.0, velocity=0.2, lower=-travel, upper=0.0),
    )
    register_interface_mate(model, extend, rod_mate)


def _antenna_module_no_antenna_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
) -> None:
    tag = "antenna_module__no_antenna"
    badge_x = min(
        r.antenna_x_m,
        r.top_bay_width_m / 2.0 - r.blank_badge_width_m / 2.0 - 0.008,
    )
    cabinet.visual(
        Box((r.blank_badge_width_m, 0.016, 0.004)),
        origin=Origin(xyz=(badge_x, r.antenna_y_m, r.cabinet_height_m - 0.0005)),
        material=mats["metal"],
        name=f"{tag}__blank_badge", material_class_id="metal.brushed_silver",
    )


def _antenna_module_side_swivel_whip_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
) -> None:
    _build_telescoping_antenna(
        model,
        cabinet,
        r,
        mats,
        tag="antenna_module__side_swivel_whip",
        swivel_axis=(0.0, 1.0, 0.0),
        knuckle_rpy=(-math.pi / 2.0, 0.0, 0.0),
        stepped=False,
    )


def _antenna_module_rear_telescoping_mast_build(
    model: ArticulatedObject, cabinet, r: ResolvedConfig, mats
) -> None:
    _build_telescoping_antenna(
        model,
        cabinet,
        r,
        mats,
        tag="antenna_module__rear_telescoping_mast",
        swivel_axis=(-1.0, 0.0, 0.0),
        knuckle_rpy=(0.0, math.pi / 2.0, 0.0),
        stepped=True,
    )


_ANTENNA_BUILDERS = {
    "no_antenna": _antenna_module_no_antenna_build,
    "side_swivel_whip": _antenna_module_side_swivel_whip_build,
    "rear_telescoping_mast": _antenna_module_rear_telescoping_mast_build,
}


# ---------------------------------------------------------------------------
# Assembly.
# ---------------------------------------------------------------------------


def build_audio_device(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette)
    cabinet = model.part(
        "cabinet",
        meta={
            "role": "cabinet_body",
            "slot": "cabinet_form",
            "candidate": r.cabinet_form,
        },
    )
    _CABINET_BUILDERS[r.cabinet_form](cabinet, r, mats)
    _SPEAKER_BUILDERS[r.speaker_layout](cabinet, r, mats)
    _GRILLE_BUILDERS[r.grille_style](cabinet, r, mats)
    _add_tuning_dial(cabinet, r, mats)
    _CONTROL_BUILDERS[r.control_deck](model, cabinet, r, mats)
    _HANDLE_BUILDERS[r.carry_handle](model, cabinet, r, mats)
    _ANTENNA_BUILDERS[r.antenna_module](model, cabinet, r, mats)
    model.meta["slot_choices"] = (
        ("cabinet_form", r.cabinet_form),
        ("grille_style", r.grille_style),
        ("speaker_layout", r.speaker_layout),
        ("control_deck", r.control_deck),
        ("carry_handle", r.carry_handle),
        ("antenna_module", r.antenna_module),
        ("control_count", str(r.control_count)),
    )
    model.meta["control_count_actual"] = r.control_count
    return model


def build_seeded_audio_device(seed: int) -> ArticulatedObject:
    return build_audio_device(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Author tests / category anchors.
# ---------------------------------------------------------------------------


def _opening_frame(r: ResolvedConfig, rest, size_u: float, size_v: float, recess: float, name: str):
    normal = _deck_normal(r)
    point = tuple(rest[axis] + normal[axis] * recess for axis in range(3))
    tangent_u = (1.0, 0.0, 0.0)
    return PlaneInterface(
        name=name,
        point=point,
        normal=normal,
        tangent_u=tangent_u,
        extent=(
            size_u + 2.0 * _HOLE_CLEARANCE,
            size_v + 2.0 * _HOLE_CLEARANCE,
        ),
    )


def run_audio_device_tests(object_model: ArticulatedObject, config: Config) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roles: dict[str, list[object]] = {}
    for part in object_model.parts:
        role = str(getattr(part, "meta", {}).get("role") or "")
        if role:
            roles.setdefault(role, []).append(part)

    cabinet = object_model.get_part("cabinet")
    cabinet_aabb = ctx.part_world_aabb(cabinet)

    # --- identity: one enclosure carrying the front speaker field(s) -------
    field_names = [
        visual.name
        for visual in cabinet.visuals
        if str(visual.name).startswith(f"grille_style__{r.grille_style}__field_")
    ]
    field_ok = len(field_names) == r.field_count
    field_front = True
    field_span = 0.0
    for name in field_names:
        box = ctx.part_element_world_aabb(cabinet, elem=name)
        if box is None:
            field_front = False
            continue
        field_span += box[1][0] - box[0][0]
        if box[0][1] > -r.cabinet_depth_m / 2.0 + 0.002:
            field_front = False
    ctx.check(
        "category_anchor: cabinet carries a front speaker grille field",
        len(roles.get("cabinet_body", [])) == 1
        and field_ok
        and field_front
        and cabinet_aabb is not None
        and field_span > 0.35 * (cabinet_aabb[1][0] - cabinet_aabb[0][0]),
        details=(
            f"fields={len(field_names)} expected={r.field_count} "
            f"span={field_span:.4f} front_ok={field_front}"
        ),
    )

    # --- surface relation for every deck control --------------------------
    deck_parts = roles.get("control_deck", [])
    controls = roles.get("press_button", []) + roles.get("rotary_knob", [])
    joint_by_child = {}
    for joint in object_model.articulations:
        joint_by_child[str(joint.child)] = joint
    surface_ok = len(deck_parts) == 1 and bool(controls)
    for part in controls:
        joint = joint_by_child.get(part.name)
        if joint is None:
            surface_ok = False
            continue
        rest = ctx.part_world_position(part)
        if rest is None:
            surface_ok = False
            continue
        is_knob = str(getattr(part, "meta", {}).get("role")) == "rotary_knob"
        if is_knob:
            elem = part.visuals[0].name
            box = ctx.part_element_world_aabb(part, elem=elem)
            size_u = 0.0 if box is None else box[1][0] - box[0][0]
            size_v = size_u
            recess = _KNOB_RECESS
            cap_height = (
                r.control_cap_height_m
                if r.control_deck == "rotary_knob_bank"
                else _AUX_KNOB_DIAMETER * _KNOB_HEIGHT_RATIO
            )
            travel = 0.0
        else:
            elem = f"{part.name.rsplit('__key_', 1)[0]}__cap_{part.name[-2:]}"
            size_u = r.control_cap_u_m
            size_v = r.control_cap_v_m
            recess = r.control_recess_m
            cap_height = r.control_cap_height_m
            travel = r.control_travel_m
        frame = _opening_frame(r, rest, size_u, size_v, recess, f"{part.name}.opening")
        surface_ok = bool(
            surface_ok
            and ctx.expect_normal_band(
                part,
                frame=frame,
                minimum=-recess - 0.0002,
                maximum=cap_height - recess + 0.0006,
                elem=elem,
                name=f"surface_relation: {part.name} sits in its exposure band",
            )
            and ctx.expect_footprint_within(
                part,
                frame=frame,
                margin=0.0,
                elem=elem,
                name=f"surface_relation: {part.name} footprint fits its opening",
            )
        )
        if travel > 0.0:
            with ctx.pose({joint: travel}):
                surface_ok = bool(
                    surface_ok
                    and ctx.expect_normal_band(
                        part,
                        frame=frame,
                        minimum=-recess - travel - 0.0002,
                        maximum=cap_height - recess - travel + 0.0006,
                        minimum_protrusion=_MIN_PRESSED_PROTRUSION,
                        elem=elem,
                        name=(f"surface_relation: {part.name} still protrudes at full press"),
                    )
                    and ctx.expect_footprint_within(
                        part,
                        frame=frame,
                        margin=0.0,
                        elem=elem,
                        name=(f"surface_relation: {part.name} stays in its opening when pressed"),
                    )
                )
    ctx.check(
        "category_anchor: every deck control stays inside its opening and proud of the deck",
        surface_ok and len(controls) >= r.control_count,
        details=f"controls={len(controls)} decks={len(deck_parts)}",
    )

    # --- neighbouring controls never share space --------------------------
    row = [part for part in controls if "__knob_" in part.name or "__key_" in part.name]
    boxes = []
    for part in row:
        box = ctx.part_world_aabb(part)
        if box is not None:
            boxes.append(box)
    boxes.sort(key=lambda item: item[0][0])
    min_gap = 1.0
    for left, right in zip(boxes, boxes[1:]):
        min_gap = min(min_gap, right[0][0] - left[1][0])
    ctx.check(
        "deck controls keep a real air gap between neighbours",
        len(boxes) >= 2 and min_gap > 0.0015,
        details=f"min_gap={min_gap:.5f} controls={len(boxes)}",
    )

    knobs = roles.get("rotary_knob", [])
    if knobs:
        spin_ok = True
        for part in knobs:
            joint = joint_by_child.get(part.name)
            joint_kind = str(
                getattr(joint.articulation_type, "value", joint.articulation_type)
                if joint is not None
                else ""
            ).lower()
            if joint is None or "continuous" not in joint_kind:
                spin_ok = False
                continue
            mark = [visual.name for visual in part.visuals if "__knob_mark_" in visual.name]
            if not mark:
                spin_ok = False
                continue
            rest = ctx.part_element_world_aabb(part, elem=mark[0])
            with ctx.pose({joint: math.pi}):
                turned = ctx.part_element_world_aabb(part, elem=mark[0])
            if rest is None or turned is None:
                spin_ok = False
                continue
            moved = max(
                abs(
                    0.5 * (rest[0][axis] + rest[1][axis])
                    - 0.5 * (turned[0][axis] + turned[1][axis])
                )
                for axis in range(3)
            )
            spin_ok = spin_ok and moved > 0.0025 and tuple(joint.axis) == (0.0, 0.0, 1.0)
        ctx.check(
            "category_anchor: every rotary knob turns about its own front-facing axis",
            spin_ok,
            details=f"knobs={len(knobs)}",
        )

    presses = roles.get("press_button", [])
    if presses:
        press_ok = True
        for part in presses:
            joint = joint_by_child.get(part.name)
            if joint is None:
                press_ok = False
                continue
            rest = ctx.part_world_position(part)
            with ctx.pose({joint: r.control_travel_m}):
                pressed = ctx.part_world_position(part)
            if rest is None or pressed is None:
                press_ok = False
                continue
            travelled = math.dist(rest, pressed)
            press_ok = (
                press_ok
                and travelled > r.control_travel_m * 0.8
                and tuple(joint.axis) == (0.0, 0.0, -1.0)
            )
        ctx.check(
            "category_anchor: every press control has independent inward travel",
            press_ok and len(presses) == r.control_count,
            details=f"presses={len(presses)} expected={r.control_count}",
        )

    # --- carry feature ----------------------------------------------------
    handles = roles.get("carry_handle", [])
    if handles:
        handle = handles[0]
        handle_aabb = ctx.part_world_aabb(handle)
        carry_ok = (
            handle_aabb is not None
            and cabinet_aabb is not None
            and handle_aabb[1][2] > cabinet_aabb[1][2] + 0.020
            and handle_aabb[1][0] - handle_aabb[0][0] > 0.5 * r.handle_span_m
        )
        if r.carry_handle == "folding_bail":
            joint = object_model.get_articulation("carry_handle__folding_bail__hinge_joint")
            with ctx.pose({joint: -r.folding_bail_angle_rad}):
                folded = ctx.part_world_aabb(handle)
            carry_ok = bool(
                carry_ok
                and folded is not None
                and handle_aabb is not None
                and folded[1][2] < handle_aabb[1][2] - 0.020
                and folded[1][1] > handle_aabb[1][1] + 0.020
            )
        ctx.check(
            "category_anchor: cabinet top provides a carry feature",
            carry_ok,
            details=f"handle={handle_aabb}",
        )
    else:
        lip_names = [
            visual.name
            for visual in cabinet.visuals
            if str(visual.name).startswith("carry_handle__molded_top_lip__")
        ]
        lip_box = ctx.part_element_world_aabb(cabinet, elem=lip_names[0]) if lip_names else None
        ctx.check(
            "category_anchor: cabinet top provides a carry feature",
            len(lip_names) >= 3 and lip_box is not None and lip_box[1][2] > r.cabinet_height_m,
            details=f"lip_visuals={len(lip_names)}",
        )

    # --- antenna ----------------------------------------------------------
    bases = roles.get("antenna_base", [])
    rods = roles.get("antenna_rod", [])
    if bases and rods:
        tag = f"antenna_module__{r.antenna_module}"
        swivel = object_model.get_articulation(f"{tag}__swivel_joint")
        extend = object_model.get_articulation(f"{tag}__extend_joint")
        rest_tip = ctx.part_world_aabb(rods[0])
        with ctx.pose({extend: -r.antenna_travel_m}):
            collapsed_tip = ctx.part_world_aabb(rods[0])
        with ctx.pose({swivel: math.radians(80.0)}):
            raked = ctx.part_world_position(bases[0])
        rest_base = ctx.part_world_position(bases[0])
        expected_axis = (
            (0.0, 1.0, 0.0) if r.antenna_module == "side_swivel_whip" else (-1.0, 0.0, 0.0)
        )
        antenna_ok = bool(
            len(bases) == 1
            and len(rods) == 1
            and rest_tip is not None
            and collapsed_tip is not None
            and rest_tip[1][2] - collapsed_tip[1][2] > r.antenna_travel_m * 0.8
            and tuple(swivel.axis) == expected_axis
            and tuple(extend.axis) == (0.0, 0.0, 1.0)
            and raked is not None
            and rest_base is not None
            and math.dist(raked, rest_base) < 1e-6
        )
        ctx.check(
            "category_anchor: antenna module matches its cabinet mounting",
            antenna_ok,
            details=f"travel={r.antenna_travel_m} axis={tuple(swivel.axis)}",
        )
    else:
        badge = ctx.part_element_world_aabb(cabinet, elem="antenna_module__no_antenna__blank_badge")
        ctx.check(
            "category_anchor: antenna module matches its cabinet mounting",
            not bases and not rods and badge is not None and badge[1][2] > r.cabinet_height_m,
            details=f"badge={badge}",
        )

    return ctx.report()


run_audio_device_tests.__test__ = False


TEMPLATE_CORNERS = (
    corner_case(
        "tombstone_transport_max_folding_rear_mast",
        {
            "cabinet_form": "tombstone_upright",
            "grille_style": "vertical_bar",
            "speaker_layout": "dual_stereo",
            "control_deck": "transport_key_deck",
            "carry_handle": "folding_bail",
            "antenna_module": "rear_telescoping_mast",
            "control_count": 8,
            "tombstone_width_m": 0.300,
            "transport_key_width_m": 0.020,
            "transport_key_travel_m": 0.0035,
            "stereo_field_gap_m": 0.070,
            "folding_bail_rise_m": 0.100,
            "folding_bail_angle_rad": 1.57,
            "mast_length_m": 0.090,
            "mast_travel_m": 0.085,
        },
        reason=(
            "narrowest arched crown must host the widest recessed key deck while the "
            "folding bail and the rear mast both rake over the rear of the top bay"
        ),
    ),
    corner_case(
        "portable_knob_bank_max_fixed_bail_whip",
        {
            "cabinet_form": "portable_slab",
            "grille_style": "perforated_mesh",
            "speaker_layout": "single_field",
            "control_deck": "rotary_knob_bank",
            "carry_handle": "fixed_bail",
            "antenna_module": "side_swivel_whip",
            "control_count": 8,
            "portable_width_m": 0.260,
            "portable_corner_radius_m": 0.030,
            "knob_diameter_m": 0.056,
            "mesh_hole_pitch_m": 0.0080,
            "single_field_width_ratio": 0.86,
            "fixed_bail_rise_m": 0.115,
            "whip_mast_length_m": 0.070,
            "whip_travel_m": 0.075,
        },
        reason=(
            "smallest nominal enclosure forced to grow for eight of the largest knobs "
            "while a full-height fixed bail and a side-raking whip share the top"
        ),
    ),
    corner_case(
        "boombox_button_row_max_travel_folding_bail",
        {
            "cabinet_form": "boombox_slab",
            "grille_style": "horizontal_ribbed",
            "speaker_layout": "dual_stereo",
            "control_deck": "push_button_row",
            "carry_handle": "folding_bail",
            "antenna_module": "rear_telescoping_mast",
            "control_count": 8,
            "boombox_width_m": 0.280,
            "boombox_corner_radius_m": 0.046,
            "button_width_m": 0.032,
            "button_travel_m": 0.0042,
            "rib_pitch_m": 0.0060,
            "folding_bail_angle_rad": 1.57,
            "mast_travel_m": 0.085,
        },
        reason=(
            "top-mounted key row at maximum count and travel competes with the folding "
            "bail seat and the antenna socket on the smallest rounded top deck"
        ),
    ),
    corner_case(
        "landscape_min_deck_open_top",
        {
            "cabinet_form": "landscape_cabinet",
            "grille_style": "vertical_bar",
            "speaker_layout": "dual_stereo",
            "control_deck": "transport_key_deck",
            "carry_handle": "molded_top_lip",
            "antenna_module": "no_antenna",
            "control_count": 2,
            "landscape_width_m": 0.620,
            "landscape_height_ratio": 0.44,
            "bar_pitch_m": 0.0090,
            "stereo_field_gap_m": 0.020,
            "transport_key_width_m": 0.011,
            "top_lip_height_m": 0.012,
            "blank_badge_width_m": 0.050,
        },
        reason=(
            "widest, shallowest cabinet with the smallest control deck checks that the "
            "front stack and dense stereo grille still fill the front face"
        ),
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_audio_device",
    "build_seeded_audio_device",
    "config_from_seed",
    "resolve_config",
    "run_audio_device_tests",
]
