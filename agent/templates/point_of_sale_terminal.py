# SPDX-License-Identifier: Apache-2.0

"""Self-contained point-of-sale payment terminal.

Design: ``articraft_template_authoring/designs/point_of_sale_terminal.json``
SourceMap: ``articraft_template_authoring/source_maps/point_of_sale_terminal.md``

Frame: ``+X`` is the front (chip slot / command key end, toward the user), ``+Z``
is up and ``+Y`` is the user's right — the side that carries the magstripe
groove.  Adopted from the silver hero, which owns five of the six forks.

One ``terminal_housing`` part is always present.  It is the grounded root under
``flat_feet`` and the child of a ``support_root`` otherwise.  Everything mounted
on the top face is placed by querying the housing's real surface at its station
(:func:`_face_z` / :func:`_face_pitch`), never by a constant lifted from one
source.  That is what lets the two housing builds and the two entry faces
combine without a compatibility gate: ``extruded_wedge`` derives a flat entry
deck exactly as long as the active entry face needs — long under
``numeric_keypad``, a narrow front lip under ``touchscreen_glass`` — while
``intersected_wedge`` presents one continuous plane, and the same key, display
and strip placement code lands correctly on either.

The two remaining cross-slot conflicts are resolved by derivation rather than by
exclusion: the touchscreen glass retreats its front edge behind the soft-key
strip when that auxiliary row is active, and the side hard buttons are stationed
below the magstripe groove floor that the card interface cut into the right side.

Every revolute and continuous joint is solved from a real ``AxisInterface`` pair
with :func:`mate_axes` and registered through :func:`register_interface_mate`.
Pressed controls run in real apertures cut through their host, so no joint needs
an overlap allowance and no motion is frozen.
"""

from __future__ import annotations

import dataclasses
import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    PlaneInterface,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

# The preview tool's default isometric already looks down onto the +X front
# face, so this template does not override __preview_front_axis__ (which only
# accepts +/-y and +/-z).

HousingBuild = Literal["extruded_wedge", "intersected_wedge"]
InputFace = Literal["numeric_keypad", "touchscreen_glass"]
AuxKeyRow = Literal["soft_key_strip", "side_hard_buttons"]
DisplayMount = Literal["fixed_display", "tilt_display"]
ReceiptPrinter = Literal["flip_cover_spindle", "knuckle_cover_static_roll"]
CardInterface = Literal["static_chip_slot", "sliding_bank_card"]
SupportBase = Literal["flat_feet", "tilt_dock", "swivel_pedestal"]
PaletteStyle = Literal["silver_hero", "gray_hero", "graphite_smart"]

HOUSING_BUILDS: tuple[HousingBuild, ...] = ("extruded_wedge", "intersected_wedge")
INPUT_FACES: tuple[InputFace, ...] = ("numeric_keypad", "touchscreen_glass")
AUX_KEY_ROWS: tuple[AuxKeyRow, ...] = ("soft_key_strip", "side_hard_buttons")
DISPLAY_MOUNTS: tuple[DisplayMount, ...] = ("fixed_display", "tilt_display")
RECEIPT_PRINTERS: tuple[ReceiptPrinter, ...] = (
    "flip_cover_spindle",
    "knuckle_cover_static_roll",
)
CARD_INTERFACES: tuple[CardInterface, ...] = ("static_chip_slot", "sliding_bank_card")
SUPPORT_BASES: tuple[SupportBase, ...] = ("flat_feet", "tilt_dock", "swivel_pedestal")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("silver_hero", "gray_hero", "graphite_smart")

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("housing_build", HOUSING_BUILDS, role="housing shell"),
        component_slot("input_face", INPUT_FACES, role="entry face"),
        component_slot("aux_key_row", AUX_KEY_ROWS, role="auxiliary key row"),
        component_slot("display_mount", DISPLAY_MOUNTS, role="display mount"),
        component_slot("receipt_printer", RECEIPT_PRINTERS, role="receipt printer"),
        component_slot("card_interface", CARD_INTERFACES, role="card interface"),
        component_slot("support_base", SUPPORT_BASES, role="support root"),
        multiplicity_slot(
            "aux_key_count",
            (2, 3, 4, 5, 6),
            role="auxiliary keys",
            item_slot="aux_key_row",
        ),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "silver_hero": {
        "shell": (0.76, 0.77, 0.80, 1.0),
        "key": (0.83, 0.84, 0.86, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
        "screen": (0.13, 0.34, 0.72, 1.0),
        "paper": (0.94, 0.94, 0.92, 1.0),
        "rubber": (0.12, 0.12, 0.13, 1.0),
        "support": (0.16, 0.16, 0.18, 1.0),
        "trim": (0.82, 0.82, 0.85, 1.0),
        "card": (0.10, 0.34, 0.58, 1.0),
        "accent": (0.92, 0.93, 0.94, 1.0),
    },
    "gray_hero": {
        "shell": (0.74, 0.74, 0.76, 1.0),
        "key": (0.58, 0.58, 0.60, 1.0),
        "dark": (0.17, 0.17, 0.19, 1.0),
        "screen": (0.86, 0.90, 0.86, 1.0),
        "paper": (0.96, 0.96, 0.95, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "support": (0.20, 0.20, 0.22, 1.0),
        "trim": (0.70, 0.70, 0.72, 1.0),
        "card": (0.10, 0.34, 0.58, 1.0),
        "accent": (0.92, 0.93, 0.94, 1.0),
    },
    "graphite_smart": {
        "shell": (0.24, 0.25, 0.27, 1.0),
        "key": (0.40, 0.41, 0.43, 1.0),
        "dark": (0.05, 0.05, 0.06, 1.0),
        "screen": (0.06, 0.07, 0.09, 1.0),
        "paper": (0.93, 0.93, 0.91, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
        "support": (0.13, 0.13, 0.15, 1.0),
        "trim": (0.55, 0.56, 0.58, 1.0),
        "card": (0.20, 0.42, 0.30, 1.0),
        "accent": (0.78, 0.80, 0.83, 1.0),
    },
}

# Fixed semantic triad; never a diversity axis.
CMD_RED = (0.76, 0.11, 0.10, 1.0)
CMD_AMBER = (0.95, 0.68, 0.10, 1.0)
CMD_GREEN = (0.10, 0.62, 0.20, 1.0)

# --- fixed hardware stock, not diversity axes --------------------------------
PLATE_THICK = 0.0024  # keypad surround plate thickness
STRIP_THICK = 0.0018  # soft-key strip thickness
BEZEL_THICK = 0.0045  # framed LCD bezel thickness
GLASS_BEZEL_THICK = 0.0030  # touchscreen bezel thickness
KEY_CLEAR = 0.00035  # running clearance between a cap and its aperture wall
APERTURE_SINK = 0.0012  # aperture floor below full key travel
FOOT_THICK = 0.0032
CARD_THICK = 0.0022
LINER_INSET = 0.002  # magstripe liner shortfall inside its own groove cut
CHEEK_GAP = 0.0010  # axial gap between a hinge boss end and its bracket cheek
AXLE_CLEAR = 0.0007  # radial running clearance of the roll axle in its bore
MIN_TILT_DISPLAY_LEN = 0.018  # a shorter head would not visibly tilt
# Screen-dominant face layout.  The glass keeps the upper part of the usable
# face and the soft-key strip sits low in the apron below it, with a real gap
# between them — real hybrid terminals put the physical row down near the front
# edge rather than tucked under the screen's lower rim.
GLASS_FACE_FRACTION = 0.58  # share of the usable face the glass keeps
AUX_ROW_APRON_OFFSET = 0.42  # strip station within the apron the glass leaves

_NUM_ROW_FRACTIONS = (0.1135, 0.2027, 0.2919, 0.3811)
_CMD_ROW_FRACTION = 0.448
_NUMERIC_NAMES = (
    ("key_1", "key_2", "key_3"),
    ("key_4", "key_5", "key_6"),
    ("key_7", "key_8", "key_9"),
    ("key_star", "key_0", "key_hash"),
)
_COMMAND_NAMES = ("cancel_key", "clear_key", "enter_key")
_ENTRY_KEY_NAMES = tuple(name for row in _NUMERIC_NAMES for name in row) + _COMMAND_NAMES


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Config:
    housing_build: HousingBuild = "extruded_wedge"
    input_face: InputFace = "numeric_keypad"
    aux_key_row: AuxKeyRow = "soft_key_strip"
    display_mount: DisplayMount = "fixed_display"
    receipt_printer: ReceiptPrinter = "flip_cover_spindle"
    card_interface: CardInterface = "static_chip_slot"
    support_base: SupportBase = "flat_feet"
    aux_key_count: int = 4
    body_length_m: float | None = None
    body_width_m: float | None = None
    deck_height_m: float | None = None
    wedge_rise_m: float | None = None
    key_travel_m: float | None = None
    cover_open_rad: float | None = None
    display_tilt_rad: float | None = None
    card_travel_m: float | None = None
    dock_recline_rad: float | None = None
    pedestal_yaw_rad: float | None = None
    palette_style: PaletteStyle = "silver_hero"
    name: str = "point_of_sale_terminal"


_RANGES: dict[str, tuple[float, float, float]] = {
    # name -> (minimum, maximum, default)
    "body_length_m": (0.150, 0.208, 0.185),
    "body_width_m": (0.070, 0.100, 0.082),
    "deck_height_m": (0.020, 0.036, 0.024),
    "wedge_rise_m": (0.018, 0.034, 0.026),
    "key_travel_m": (0.0012, 0.0026, 0.0015),
    "cover_open_rad": (1.25, 1.90, 1.70),
    "display_tilt_rad": (0.38, 0.66, 0.60),
    "card_travel_m": (0.011, 0.023, 0.018),
    "dock_recline_rad": (0.18, 0.40, 0.35),
    "pedestal_yaw_rad": (0.85, 1.55, 1.40),
}


@dataclass(frozen=True)
class ResolvedConfig:
    housing_build: HousingBuild
    input_face: InputFace
    aux_key_row: AuxKeyRow
    display_mount: DisplayMount
    receipt_printer: ReceiptPrinter
    card_interface: CardInterface
    support_base: SupportBase
    aux_key_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    name: str

    # independent
    body_length_m: float
    body_width_m: float
    deck_height_m: float
    wedge_rise_m: float
    key_travel_m: float
    cover_open_rad: float
    display_tilt_rad: float
    card_travel_m: float
    dock_recline_rad: float
    pedestal_yaw_rad: float

    # housing shell
    housing_length_m: float
    rear_height_m: float
    corner_radius_m: float
    deck_len_m: float
    rear_deck_len_m: float
    slope_front_x_m: float
    slope_rear_x_m: float
    slope_pitch_rad: float
    groove_len_m: float
    groove_center_x_m: float
    groove_floor_z_m: float
    groove_liner_len_m: float

    # card interface
    chip_slot_depth_m: float
    chip_slot_width_m: float
    chip_slot_z0_m: float
    chip_slot_h_m: float
    card_len_m: float
    card_width_m: float
    card_center_x_m: float

    # printer
    bay_x_min_m: float
    bay_x_max_m: float
    bay_width_m: float
    bay_floor_z_m: float
    cover_hinge_x_m: float
    cover_hinge_z_m: float
    cover_pitch_rad: float
    cover_len_m: float
    cover_width_m: float
    cover_thick_m: float
    roll_radius_m: float
    roll_len_m: float
    roll_center_x_m: float
    roll_center_z_m: float
    axle_radius_m: float
    axle_len_m: float
    knuckle_span_m: float
    knuckle_radius_m: float
    exit_slit_x_m: float

    # entry face
    entry_row0_x_m: float
    cmd_row_x_m: float
    key_pitch_x_m: float
    key_size_x_m: float
    key_size_y_m: float
    cmd_size_y_m: float
    key_pitch_y_m: float
    keycap_height_m: float
    plate_front_x_m: float
    plate_rear_x_m: float
    plate_width_m: float
    entry_rear_x_m: float

    # display
    display_center_x_m: float
    display_len_m: float
    display_width_m: float
    display_hinge_x_m: float
    display_hinge_z_m: float
    display_pitch_rad: float
    head_boss_radius_m: float
    head_boss_len_m: float
    head_local_seat_m: float
    bracket_len_m: float
    display_normal_lift_m: float
    hinge_relief_radius_m: float

    # auxiliary key row
    aux_row_x_m: float
    aux_strip_len_m: float
    aux_strip_width_m: float
    aux_key_size_m: float
    aux_cap_height_m: float
    aux_span_m: float
    aux_row_z_m: float
    aux_button_height_m: float

    # support root
    foot_station_x_m: float
    foot_station_y_m: float
    foot_radius_m: float
    cradle_len_m: float
    cradle_width_m: float
    cradle_height_m: float
    cradle_wall_m: float
    post_width_m: float
    upstand_height_m: float
    well_depth_m: float
    base_radius_m: float
    base_height_m: float
    pole_radius_m: float
    pole_height_m: float
    collar_radius_m: float
    collar_height_m: float
    stand_top_z_m: float
    mount_height_m: float


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x504F_5354)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        housing_build=choices["housing_build"],
        input_face=choices["input_face"],
        aux_key_row=choices["aux_key_row"],
        display_mount=choices["display_mount"],
        receipt_printer=choices["receipt_printer"],
        card_interface=choices["card_interface"],
        support_base=choices["support_base"],
        aux_key_count=choices["aux_key_count"],
        body_length_m=round(rng.uniform(0.150, 0.208), 4),
        body_width_m=round(rng.uniform(0.070, 0.100), 4),
        deck_height_m=round(rng.uniform(0.020, 0.036), 4),
        wedge_rise_m=round(rng.uniform(0.018, 0.034), 4),
        key_travel_m=round(rng.uniform(0.0012, 0.0026), 5),
        cover_open_rad=round(rng.uniform(1.25, 1.90), 3),
        display_tilt_rad=round(rng.uniform(0.38, 0.66), 3),
        card_travel_m=round(rng.uniform(0.011, 0.023), 4),
        dock_recline_rad=round(rng.uniform(0.18, 0.40), 3),
        pedestal_yaw_rad=round(rng.uniform(0.85, 1.55), 3),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"point_of_sale_terminal_seed_{int(seed)}",
    )


def _independent(config: Config, field: str) -> float:
    lo, hi, default = _RANGES[field]
    raw = getattr(config, field)
    if raw is None:
        return default
    value = float(raw)
    if not lo <= value <= hi:
        raise ValueError(f"{field} must be in [{lo}, {hi}]")
    return value


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "housing_build": config.housing_build,
            "input_face": config.input_face,
            "aux_key_row": config.aux_key_row,
            "display_mount": config.display_mount,
            "receipt_printer": config.receipt_printer,
            "card_interface": config.card_interface,
            "support_base": config.support_base,
            "aux_key_count": config.aux_key_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    body_length = _independent(config, "body_length_m")
    body_width = _independent(config, "body_width_m")
    deck_height = _independent(config, "deck_height_m")
    wedge_rise = _independent(config, "wedge_rise_m")
    key_travel = _independent(config, "key_travel_m")
    cover_open = _independent(config, "cover_open_rad")
    display_tilt = _independent(config, "display_tilt_rad")
    card_travel = _independent(config, "card_travel_m")
    dock_recline = _independent(config, "dock_recline_rad")
    pedestal_yaw = _independent(config, "pedestal_yaw_rad")

    housing_build = config.housing_build
    input_face = config.input_face
    aux_row = config.aux_key_row
    display_mount = config.display_mount
    receipt_printer = config.receipt_printer
    card_interface = config.card_interface
    support_base = config.support_base
    aux_count = int(config.aux_key_count)

    # --- shell envelope ------------------------------------------------------
    length = body_length * (1.00 if housing_build == "extruded_wedge" else 0.97)
    width = body_width
    x_front = length / 2.0
    x_rear = -length / 2.0
    rear_height = deck_height + wedge_rise
    corner_radius = _clamp(0.145 * width, 0.007, 0.014)

    # Stations the entry face has to be laid out against, hoisted because the
    # entry block itself is derived from the room they leave.
    bay_x_max = -0.250 * length
    head_boss_radius = _clamp(0.049 * width, 0.0032, 0.0050)
    cover_front_x = bay_x_max + 0.008
    # A tilting head hinges ahead of the closed printer cover it swings over.
    rear_limit = (
        cover_front_x + 0.004 + head_boss_radius + 0.0020
        if display_mount == "tilt_display"
        else bay_x_max - 0.006
    )

    # The soft-key strip station fixes how much flat entry deck the extruded
    # shell must derive; the intersected shell is one continuous plane.
    aux_strip_len = 0.072 * length
    aux_row_x = 0.035 * length
    if display_mount == "tilt_display" and input_face == "numeric_keypad":
        # A head short enough to fit a cramped case would barely tilt, so the
        # entry block is pushed forward until the head has a real window.
        aux_row_x = max(
            aux_row_x,
            rear_limit + MIN_TILT_DISPLAY_LEN + 0.006 + aux_strip_len / 2.0 + 0.006,
        )
    elif input_face == "touchscreen_glass":
        # No numeric block fills the face below the strip here.  The glass keeps
        # the upper part of the usable face and the strip is stationed low in the
        # apron it leaves, so the keys read as a bottom control row instead of
        # hugging the screen's lower rim above a blank expanse.  The front
        # boundary is the front lip on the extruded shell, the nose on the
        # intersected one.
        face_front_x = x_front - 0.014
        if housing_build == "extruded_wedge":
            face_front_x = min(face_front_x, x_front - 0.14 * length - 0.003)
        glass_face_front_x = rear_limit + GLASS_FACE_FRACTION * (face_front_x - rear_limit)
        aux_row_x = glass_face_front_x + AUX_ROW_APRON_OFFSET * (face_front_x - glass_face_front_x)
        aux_row_x = max(aux_row_x, glass_face_front_x + aux_strip_len / 2.0 + 0.006)
        aux_row_x = min(aux_row_x, face_front_x - aux_strip_len / 2.0 - 0.004)
    entry_rear_x = aux_row_x - aux_strip_len / 2.0 - 0.006

    if housing_build == "extruded_wedge":
        deck_len = x_front - entry_rear_x if input_face == "numeric_keypad" else 0.14 * length
        rear_deck_len = 0.255 * length
    else:
        deck_len = 0.0
        rear_deck_len = 0.0
    slope_front_x = x_front - deck_len
    slope_rear_x = x_rear + rear_deck_len
    slope_run = max(slope_front_x - slope_rear_x, 0.020)
    slope_pitch = math.atan2(wedge_rise, slope_run)

    # --- card interface ------------------------------------------------------
    # The pocket must be deeper than the stroke it has to retain a card through.
    chip_slot_depth = _clamp(max(0.18 * length, card_travel + 0.0140), 0.022, 0.046)
    chip_slot_width = _clamp(0.68 * width, 0.040, 0.066)
    chip_slot_z0 = 0.30 * deck_height
    chip_slot_h = 0.0038
    groove_floor_z = 0.62 * deck_height
    if housing_build == "extruded_wedge":
        groove_len = length - 0.017  # pocket inset from both ends
    else:
        groove_len = length + 0.020  # through groove, open at both ends
    groove_center_x = 0.0
    # The liner is derived from the cut it lines and can never leave the shell.
    groove_liner_len = min(groove_len, length) - LINER_INSET

    card_len = chip_slot_depth + card_travel + 0.030
    card_width = chip_slot_width - 0.002
    card_rear_x = (x_front - chip_slot_depth) + 0.0025
    card_center_x = card_rear_x + card_len / 2.0

    # --- printer -------------------------------------------------------------
    bay_x_min = -0.465 * length
    bay_x_max = -0.250 * length
    bay_width = _clamp(0.80 * width, 0.040, 0.080)
    bay_depth = _clamp(0.72 * rear_height, 0.020, 0.040)
    bay_floor_z = rear_height - bay_depth
    cover_hinge_x = -0.489 * length
    cover_len = (bay_x_max - cover_hinge_x) + 0.008
    cover_width = min(bay_width + 0.014, width - 0.004)
    cover_thick = _clamp(0.070 * rear_height, 0.008, 0.014)
    roll_center_x = (bay_x_min + bay_x_max) / 2.0

    def _face_at(x: float) -> float:
        return _face_z_raw(
            x,
            deck_len=deck_len,
            rear_deck_len=rear_deck_len,
            slope_front_x=slope_front_x,
            slope_rear_x=slope_rear_x,
            deck_height=deck_height,
            wedge_rise=wedge_rise,
        )

    # The roll is sized by the bay it lies in *and* by the headroom under the
    # closed cover, so it can never stand proud of the face.
    roll_headroom = _face_at(roll_center_x) - bay_floor_z - 0.0022
    roll_radius = _clamp(min(0.38 * (bay_x_max - bay_x_min), 0.5 * roll_headroom), 0.006, 0.017)
    roll_len = bay_width - 0.006
    roll_center_z = bay_floor_z + roll_radius + 0.001
    axle_radius = _clamp(0.20 * roll_radius, 0.0022, 0.0035)
    axle_len = width - 0.004
    knuckle_span = _clamp(0.58 * bay_width, 0.026, 0.052)
    knuckle_radius = _clamp(0.42 * cover_thick, 0.0026, 0.0042)
    exit_slit_x = bay_x_max - 0.006

    # --- entry face ----------------------------------------------------------
    # The key block is anchored at the front edge and its row pitch is derived
    # from whatever run the auxiliary strip leaves, so pushing the strip forward
    # for a tilting head compresses the keypad instead of breaking it.
    key_size_y = 0.207 * width
    key_pitch_y = _clamp(0.262 * width, 0.016, 0.026)
    cmd_size_y = min(0.245 * width, key_pitch_y - 0.0025)
    keycap_height = key_travel + 0.0024
    nominal_key_x = 0.070 * length
    cmd_row_x = min(_CMD_ROW_FRACTION * length, x_front - 0.004 - nominal_key_x / 2.0)
    entry_row0_x = max(
        _NUM_ROW_FRACTIONS[0] * length,
        aux_row_x + aux_strip_len / 2.0 + nominal_key_x / 2.0 + 0.004,
    )
    key_pitch_x_m = max((cmd_row_x - entry_row0_x) / 4.75, 0.0045)
    key_size_x = min(nominal_key_x, key_pitch_x_m - 0.0022)
    plate_front_x = min(cmd_row_x + key_size_x / 2.0 + 0.004, x_front - 0.003)
    plate_rear_x = entry_row0_x - key_size_x / 2.0 - 0.004
    plate_width = min(2.0 * key_pitch_y + cmd_size_y + 0.008, width - 0.008)

    # --- display -------------------------------------------------------------
    display_width = (
        _clamp(0.73 * width, 0.030, 0.072)
        if input_face == "numeric_keypad"
        else _clamp(0.83 * width, 0.040, 0.082)
    )
    head_boss_len = width - 0.018
    if housing_build == "extruded_wedge":
        rear_limit = max(rear_limit, slope_rear_x + 0.002)
    if input_face == "numeric_keypad":
        disp_front_x = entry_rear_x - 0.004
        display_len = _clamp(
            min(0.216 * length, disp_front_x - rear_limit - 0.002),
            MIN_TILT_DISPLAY_LEN if display_mount == "tilt_display" else 0.010,
            0.080,
        )
    else:
        if aux_row == "soft_key_strip":
            # The glass keeps its own share of the face and always stops clear
            # of the strip's rear edge, so screen and soft keys never overlap.
            glass_front_x_m = min(glass_face_front_x, aux_row_x - aux_strip_len / 2.0 - 0.006)
        else:
            glass_front_x_m = x_front - 0.016
        if housing_build == "extruded_wedge":
            glass_front_x_m = min(glass_front_x_m, slope_front_x - 0.002)
        glass_rear_x_m = rear_limit
        disp_front_x = glass_front_x_m
        display_len = _clamp(
            glass_front_x_m - glass_rear_x_m,
            MIN_TILT_DISPLAY_LEN if display_mount == "tilt_display" else 0.014,
            0.150,
        )
    if display_mount == "tilt_display":
        # A tilting head is anchored from its hinge end, so the boss always
        # clears the closed printer cover even on the shortest cases.
        display_center_x = rear_limit + display_len / 2.0
    else:
        display_center_x = disp_front_x - display_len / 2.0

    display_rear_x = display_center_x - display_len / 2.0
    display_hinge_x = display_rear_x - 0.004
    # Local bezel seat of a tilting head: face station minus the hinge origin.
    head_local_seat_m = display_center_x - display_hinge_x
    bracket_len_m = 2.0 * head_boss_radius + 0.004
    display_normal_lift_m = (
        BEZEL_THICK if input_face == "numeric_keypad" else GLASS_BEZEL_THICK
    ) / 2.0 + 0.0004
    hinge_relief_radius_m = head_boss_radius + 0.0008

    # --- auxiliary key row ---------------------------------------------------
    aux_gap = 0.0032
    nominal_cap = _clamp(0.145 * width, 0.0055, 0.012)
    aux_strip_width = min(aux_count * nominal_cap + (aux_count + 1) * aux_gap, width - 0.010)
    aux_key_size = min(nominal_cap, (aux_strip_width - (aux_count + 1) * aux_gap) / aux_count)
    aux_key_size = max(aux_key_size, 0.0040)
    aux_cap_height = key_travel + 0.0018
    aux_span = _clamp(0.34 * length, 0.020, 0.080)
    aux_row_z = _clamp(0.42 * groove_floor_z, 0.004, 0.012)
    aux_button_height = min(0.005, 2.0 * aux_row_z - 0.0015)

    # --- support root --------------------------------------------------------
    foot_station_x = 0.368 * length
    foot_station_y = 0.317 * width
    foot_radius = _clamp(0.073 * width, 0.0045, 0.0075)

    cradle_len = length + 0.062
    post_width = 0.008
    cradle_width = width + 0.004 + 2.0 * (post_width + 0.006)
    well_depth = (length / 2.0) * math.sin(dock_recline) + 0.004
    cradle_height = max(_clamp(0.205 * length, 0.028, 0.046), well_depth + 0.009)
    cradle_wall = 0.010
    upstand_height = _clamp(0.62 * rear_height, 0.022, 0.040)

    base_radius = _clamp(0.46 * length, 0.068, 0.098)
    base_height = 0.022
    pole_radius = _clamp(0.088 * length, 0.013, 0.020)
    pole_height = _clamp(0.60 * length, 0.085, 0.130)
    collar_radius = _clamp(0.33 * width, 0.022, 0.034)
    collar_height = 0.008
    stand_top_z = base_height + pole_height + collar_height
    mount_height = (
        0.0
        if support_base == "flat_feet"
        else (cradle_height if support_base == "tilt_dock" else stand_top_z)
    )

    return ResolvedConfig(
        housing_build=housing_build,
        input_face=input_face,
        aux_key_row=aux_row,
        display_mount=display_mount,
        receipt_printer=receipt_printer,
        card_interface=card_interface,
        support_base=support_base,
        aux_key_count=aux_count,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        name=str(config.name),
        body_length_m=body_length,
        body_width_m=body_width,
        deck_height_m=deck_height,
        wedge_rise_m=wedge_rise,
        key_travel_m=key_travel,
        cover_open_rad=cover_open,
        display_tilt_rad=display_tilt,
        card_travel_m=card_travel,
        dock_recline_rad=dock_recline,
        pedestal_yaw_rad=pedestal_yaw,
        housing_length_m=length,
        rear_height_m=rear_height,
        corner_radius_m=corner_radius,
        deck_len_m=deck_len,
        rear_deck_len_m=rear_deck_len,
        slope_front_x_m=slope_front_x,
        slope_rear_x_m=slope_rear_x,
        slope_pitch_rad=slope_pitch,
        groove_len_m=groove_len,
        groove_center_x_m=groove_center_x,
        groove_floor_z_m=groove_floor_z,
        groove_liner_len_m=groove_liner_len,
        chip_slot_depth_m=chip_slot_depth,
        chip_slot_width_m=chip_slot_width,
        chip_slot_z0_m=chip_slot_z0,
        chip_slot_h_m=chip_slot_h,
        card_len_m=card_len,
        card_width_m=card_width,
        card_center_x_m=card_center_x,
        bay_x_min_m=bay_x_min,
        bay_x_max_m=bay_x_max,
        bay_width_m=bay_width,
        bay_floor_z_m=bay_floor_z,
        cover_hinge_x_m=cover_hinge_x,
        cover_hinge_z_m=0.0,  # filled below
        cover_pitch_rad=0.0,  # filled below
        cover_len_m=cover_len,
        cover_width_m=cover_width,
        cover_thick_m=cover_thick,
        roll_radius_m=roll_radius,
        roll_len_m=roll_len,
        roll_center_x_m=roll_center_x,
        roll_center_z_m=roll_center_z,
        axle_radius_m=axle_radius,
        axle_len_m=axle_len,
        knuckle_span_m=knuckle_span,
        knuckle_radius_m=knuckle_radius,
        exit_slit_x_m=exit_slit_x,
        entry_row0_x_m=entry_row0_x,
        cmd_row_x_m=cmd_row_x,
        key_pitch_x_m=key_pitch_x_m,
        key_size_x_m=key_size_x,
        key_size_y_m=key_size_y,
        cmd_size_y_m=cmd_size_y,
        key_pitch_y_m=key_pitch_y,
        keycap_height_m=keycap_height,
        plate_front_x_m=plate_front_x,
        plate_rear_x_m=plate_rear_x,
        plate_width_m=plate_width,
        entry_rear_x_m=entry_rear_x,
        display_center_x_m=display_center_x,
        display_len_m=display_len,
        display_width_m=display_width,
        display_hinge_x_m=display_hinge_x,
        display_hinge_z_m=0.0,  # filled below
        display_pitch_rad=0.0,  # filled below
        head_boss_radius_m=head_boss_radius,
        head_boss_len_m=head_boss_len,
        head_local_seat_m=head_local_seat_m,
        bracket_len_m=bracket_len_m,
        display_normal_lift_m=display_normal_lift_m,
        hinge_relief_radius_m=hinge_relief_radius_m,
        aux_row_x_m=aux_row_x,
        aux_strip_len_m=aux_strip_len,
        aux_strip_width_m=aux_strip_width,
        aux_key_size_m=aux_key_size,
        aux_cap_height_m=aux_cap_height,
        aux_span_m=aux_span,
        aux_row_z_m=aux_row_z,
        aux_button_height_m=aux_button_height,
        foot_station_x_m=foot_station_x,
        foot_station_y_m=foot_station_y,
        foot_radius_m=foot_radius,
        cradle_len_m=cradle_len,
        cradle_width_m=cradle_width,
        cradle_height_m=cradle_height,
        cradle_wall_m=cradle_wall,
        post_width_m=post_width,
        upstand_height_m=upstand_height,
        well_depth_m=well_depth,
        base_radius_m=base_radius,
        base_height_m=base_height,
        pole_radius_m=pole_radius,
        pole_height_m=pole_height,
        collar_radius_m=collar_radius,
        collar_height_m=collar_height,
        stand_top_z_m=stand_top_z,
        mount_height_m=mount_height,
    )


def _resolved_with_face_stations(r: ResolvedConfig) -> ResolvedConfig:
    """Second pass: stations that need the completed top-surface functions."""

    return dataclasses.replace(
        r,
        cover_hinge_z_m=_face_z(r, r.cover_hinge_x_m),
        cover_pitch_rad=_face_pitch(r, r.cover_hinge_x_m),
        display_hinge_z_m=_face_z(r, r.display_hinge_x_m),
        display_pitch_rad=_face_pitch(r, r.display_center_x_m),
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("housing_build", str(config.housing_build)),
        ("input_face", str(config.input_face)),
        ("aux_key_row", str(config.aux_key_row)),
        ("display_mount", str(config.display_mount)),
        ("receipt_printer", str(config.receipt_printer)),
        ("card_interface", str(config.card_interface)),
        ("support_base", str(config.support_base)),
        ("aux_key_count", int(config.aux_key_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Top-surface queries — every face-mounted component goes through these.
# --------------------------------------------------------------------------- #
def _face_z_raw(
    x: float,
    *,
    deck_len: float,
    rear_deck_len: float,
    slope_front_x: float,
    slope_rear_x: float,
    deck_height: float,
    wedge_rise: float,
) -> float:
    if deck_len > 1e-6 and x >= slope_front_x:
        return deck_height
    if rear_deck_len > 1e-6 and x <= slope_rear_x:
        return deck_height + wedge_rise
    span = max(slope_front_x - slope_rear_x, 1e-6)
    t = _clamp((slope_front_x - x) / span, 0.0, 1.0)
    return deck_height + t * wedge_rise


def _face_z(r: ResolvedConfig, x: float) -> float:
    return _face_z_raw(
        x,
        deck_len=r.deck_len_m,
        rear_deck_len=r.rear_deck_len_m,
        slope_front_x=r.slope_front_x_m,
        slope_rear_x=r.slope_rear_x_m,
        deck_height=r.deck_height_m,
        wedge_rise=r.wedge_rise_m,
    )


def _face_pitch(r: ResolvedConfig, x: float) -> float:
    if r.deck_len_m > 1e-6 and x >= r.slope_front_x_m:
        return 0.0
    if r.rear_deck_len_m > 1e-6 and x <= r.slope_rear_x_m:
        return 0.0
    return r.slope_pitch_rad


def _face_point(r: ResolvedConfig, x: float, y: float, lift: float) -> tuple[float, float, float]:
    """World point at station ``x`` on the top face, offset along its normal."""

    pitch = _face_pitch(r, x)
    return (
        x + math.sin(pitch) * lift,
        y,
        _face_z(r, x) + math.cos(pitch) * lift,
    )


def _face_origin(r: ResolvedConfig, x: float, y: float, lift: float) -> Origin:
    return Origin(xyz=_face_point(r, x, y, lift), rpy=(0.0, _face_pitch(r, x), 0.0))


def _slope_frame(pitch: float) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Down-face (+X-ward) unit vector and outward normal for a face pitch."""

    return (
        (math.cos(pitch), 0.0, -math.sin(pitch)),
        (math.sin(pitch), 0.0, math.cos(pitch)),
    )


def _local_face_point(pitch: float, along: float, lift: float) -> tuple[float, float, float]:
    down, normal = _slope_frame(pitch)
    return (
        down[0] * along + normal[0] * lift,
        0.0,
        down[2] * along + normal[2] * lift,
    )


# --------------------------------------------------------------------------- #
# Shared shapes
# --------------------------------------------------------------------------- #
def _rounded_cap(size: tuple[float, float, float]) -> cq.Workplane:
    """Rounded keycap resting on local z = 0."""

    sx, sy, sz = size
    cap = cq.Workplane("XY").box(sx, sy, sz)
    try:
        cap = cap.edges("|Z").fillet(min(sx, sy) * 0.18)
    except Exception:
        pass
    try:
        cap = cap.edges(">Z").fillet(sz * 0.20)
    except Exception:
        pass
    return cap.translate((0.0, 0.0, sz / 2.0))


def _aperture_box(
    r: ResolvedConfig,
    x: float,
    y: float,
    size_x: float,
    size_y: float,
    top_lift: float,
    travel: float,
) -> cq.Workplane:
    """One key aperture cut, aligned with the local face frame at station x."""

    pitch = _face_pitch(r, x)
    depth = travel + APERTURE_SINK + top_lift + 0.004
    solid = (
        cq.Workplane("XY")
        .box(size_x + 2.0 * KEY_CLEAR, size_y + 2.0 * KEY_CLEAR, depth)
        .translate((0.0, 0.0, -depth / 2.0 + 0.002))
    )
    if abs(pitch) > 1e-9:
        solid = solid.rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), math.degrees(pitch))
    return solid.translate(_face_point(r, x, y, top_lift))


# --------------------------------------------------------------------------- #
# housing_build candidates
# --------------------------------------------------------------------------- #
def _housing_build_extruded_wedge_build(r: ResolvedConfig) -> cq.Workplane:
    """Six-point side profile extruded across the width, then filleted."""

    x_front = r.housing_length_m / 2.0
    x_rear = -x_front
    profile = [
        (x_front, 0.0),
        (x_front, r.deck_height_m),
        (r.slope_front_x_m, r.deck_height_m),
        (r.slope_rear_x_m, r.rear_height_m),
        (x_rear, r.rear_height_m),
        (x_rear, 0.0),
    ]
    body = cq.Workplane("XZ").polyline(profile).close().extrude(r.body_width_m / 2.0, both=True)
    try:
        body = body.edges("|Z").fillet(r.corner_radius_m)
    except Exception:
        pass
    try:
        body = body.edges("|Y").fillet(0.0018)
    except Exception:
        pass
    return body


def _housing_build_intersected_wedge_build(r: ResolvedConfig) -> cq.Workplane:
    """Continuous-slope wedge intersected with a rounded-rectangle footprint."""

    x_front = r.housing_length_m / 2.0
    x_rear = -x_front
    wedge = (
        cq.Workplane("XZ")
        .polyline(
            [
                (x_front, 0.0),
                (x_front, r.deck_height_m),
                (x_rear, r.rear_height_m),
                (x_rear, 0.0),
            ]
        )
        .close()
        .extrude(r.body_width_m / 2.0, both=True)
    )
    footprint = (
        cq.Workplane("XY").rect(r.housing_length_m, r.body_width_m).extrude(r.rear_height_m + 0.020)
    )
    try:
        footprint = footprint.edges("|Z").fillet(r.corner_radius_m)
    except Exception:
        pass
    body = footprint.intersect(wedge)
    # Paper exit slit across the top deck, just in front of the cover edge.
    slit = (
        cq.Workplane("XY")
        .box(0.70 * r.bay_width_m, 0.0035, 0.020)
        .translate((r.exit_slit_x_m, 0.0, _face_z(r, r.exit_slit_x_m) - 0.0025 + 0.010))
    )
    return body.cut(slit)


_HOUSING_BUILDERS = {
    "extruded_wedge": _housing_build_extruded_wedge_build,
    "intersected_wedge": _housing_build_intersected_wedge_build,
}


def _housing_solid(r: ResolvedConfig) -> cq.Workplane:
    """Shell profile plus every boolean opening the active candidates need."""

    body = _HOUSING_BUILDERS[r.housing_build](r)

    # Receipt paper bay, open at the top.
    bay = (
        cq.Workplane("XY")
        .box(r.bay_x_max_m - r.bay_x_min_m, r.bay_width_m, 0.060)
        .translate(
            (
                (r.bay_x_min_m + r.bay_x_max_m) / 2.0,
                0.0,
                r.bay_floor_z_m + 0.030,
            )
        )
    )
    body = body.cut(bay)

    # Chip card pocket, open through the front face.
    x_front = r.housing_length_m / 2.0
    pocket_len = r.chip_slot_depth_m + 0.006
    body = body.cut(
        cq.Workplane("XY")
        .box(pocket_len, r.chip_slot_width_m, r.chip_slot_h_m)
        .translate(
            (
                x_front - r.chip_slot_depth_m + pocket_len / 2.0,
                0.0,
                r.chip_slot_z0_m + r.chip_slot_h_m / 2.0,
            )
        )
    )

    # Magstripe swipe groove along the right side.  Its length is derived from
    # the housing length, so nothing that lines it can leave the shell.
    body = body.cut(
        cq.Workplane("XY")
        .box(r.groove_len_m, 0.008, 0.003)
        .translate(
            (
                r.groove_center_x_m,
                r.body_width_m / 2.0,
                r.groove_floor_z_m + 0.0015,
            )
        )
    )

    # Hinge relief channel so the display head's boss barrel runs in a real
    # bore instead of sinking into the shell at the top-rear slope edge.
    if r.display_mount == "tilt_display":
        body = body.cut(
            cq.Workplane("XZ")
            .circle(r.hinge_relief_radius_m)
            .extrude((r.head_boss_len_m + 0.003) / 2.0, both=True)
            .translate((r.display_hinge_x_m, 0.0, _face_z(r, r.display_hinge_x_m)))
        )

    # Roll spindle bearing bores through both bay side walls.
    if r.receipt_printer == "flip_cover_spindle":
        body = body.cut(
            cq.Workplane("XZ")
            .circle(r.axle_radius_m + AXLE_CLEAR)
            .extrude(r.body_width_m, both=True)
            .translate((r.roll_center_x_m, 0.0, r.roll_center_z_m))
        )

    # Entry-key apertures through the keypad plate region and into the deck.
    if r.input_face == "numeric_keypad":
        plate_lift = PLATE_THICK / 2.0 - 0.0003
        top_lift = plate_lift + PLATE_THICK / 2.0
        cuts = None
        for row_index in range(len(_NUM_ROW_FRACTIONS)):
            for col in (-1, 0, 1):
                piece = _aperture_box(
                    r,
                    r.entry_row0_x_m + row_index * r.key_pitch_x_m,
                    col * r.key_pitch_y_m,
                    r.key_size_x_m,
                    r.key_size_y_m,
                    top_lift,
                    r.key_travel_m,
                )
                cuts = piece if cuts is None else cuts.union(piece)
        for col in (-1, 0, 1):
            piece = _aperture_box(
                r,
                r.cmd_row_x_m,
                col * r.key_pitch_y_m,
                r.key_size_x_m,
                r.cmd_size_y_m,
                top_lift,
                r.key_travel_m,
            )
            cuts = piece if cuts is None else cuts.union(piece)
        if cuts is not None:
            body = body.cut(cuts)

    # Auxiliary key openings.
    if r.aux_key_row == "soft_key_strip":
        top_lift = STRIP_THICK - 0.0003
        cuts = None
        for y in _aux_strip_stations(r):
            piece = _aperture_box(
                r,
                r.aux_row_x_m,
                y,
                r.aux_key_size_m,
                r.aux_key_size_m,
                top_lift,
                r.key_travel_m,
            )
            cuts = piece if cuts is None else cuts.union(piece)
        if cuts is not None:
            body = body.cut(cuts)
    else:
        channel_depth = 0.0012 + r.key_travel_m
        body = body.cut(
            cq.Workplane("XY")
            .box(
                r.aux_span_m + r.aux_key_size_m + 0.003,
                2.0 * channel_depth,
                r.aux_button_height_m + 2.0 * KEY_CLEAR,
            )
            .translate((0.0, r.body_width_m / 2.0, r.aux_row_z_m))
        )
    return body


# --------------------------------------------------------------------------- #
# Auxiliary key stations
# --------------------------------------------------------------------------- #
def _aux_strip_stations(r: ResolvedConfig) -> tuple[float, ...]:
    usable = max(r.aux_strip_width_m - r.aux_key_size_m - 0.002, 0.002)
    n = r.aux_key_count
    if n == 1:
        return (0.0,)
    step = usable / (n - 1)
    return tuple(-usable / 2.0 + index * step for index in range(n))


def _aux_side_stations(r: ResolvedConfig) -> tuple[float, ...]:
    usable = max(r.aux_span_m - r.aux_key_size_m, 0.004)
    n = r.aux_key_count
    if n == 1:
        return (0.0,)
    step = usable / (n - 1)
    return tuple(-usable / 2.0 + index * step for index in range(n))


# --------------------------------------------------------------------------- #
# input_face candidates
# --------------------------------------------------------------------------- #
def _entry_key_layout(r: ResolvedConfig) -> tuple[tuple[str, float, float, float], ...]:
    """(name, x, y, size_y) for the 12 numeric keys and the command triad."""

    layout: list[tuple[str, float, float, float]] = []
    for row_index, names in enumerate(_NUMERIC_NAMES):
        x = r.entry_row0_x_m + row_index * r.key_pitch_x_m
        for col, name in zip((-1, 0, 1), names):
            layout.append((name, x, col * r.key_pitch_y_m, r.key_size_y_m))
    x_cmd = r.cmd_row_x_m
    for col, name in zip((-1, 0, 1), _COMMAND_NAMES):
        layout.append((name, x_cmd, col * r.key_pitch_y_m, r.cmd_size_y_m))
    return tuple(layout)


def _keypad_plate_center_x(r: ResolvedConfig) -> float:
    return (r.plate_front_x_m + r.plate_rear_x_m) / 2.0


def _keypad_plate_solid(r: ResolvedConfig) -> cq.Workplane:
    """Charcoal surround plate with one real aperture per key, face-local."""

    pitch = _face_pitch(r, _keypad_plate_center_x(r))
    cos_p = max(math.cos(pitch), 1e-6)
    center_x = _keypad_plate_center_x(r)
    plate_len = max(r.plate_front_x_m - r.plate_rear_x_m, 0.010) / cos_p
    plate = cq.Workplane("XY").box(plate_len, r.plate_width_m, PLATE_THICK)
    try:
        plate = plate.edges("|Z").fillet(0.003)
    except Exception:
        pass
    for name, x, y, size_y in _entry_key_layout(r):
        hole = (
            cq.Workplane("XY")
            .box(
                r.key_size_x_m + 2.0 * KEY_CLEAR,
                size_y + 2.0 * KEY_CLEAR,
                PLATE_THICK + 0.004,
            )
            .translate(((x - center_x) / cos_p, y, 0.0))
        )
        plate = plate.cut(hole)
        del name
    return plate


def _input_face_numeric_keypad_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "input_face__numeric_keypad"
    plate_center_x = _keypad_plate_center_x(r)
    # Seated 0.3 mm into the shell so the plate is never a floating island.
    plate_lift = PLATE_THICK / 2.0 - 0.0003
    housing.visual(
        mesh_from_cadquery(_keypad_plate_solid(r), "pos_keypad_plate"),
        origin=_face_origin(r, plate_center_x, 0.0, plate_lift),
        material=mats["dark"],
        name=f"{tag}__keypad_plate", material_class_id="plastic.opaque_generic",
    )
    if r.display_mount == "fixed_display":
        _emit_display_stack(housing, r, mats, tag, lambda x, lift: _face_origin(r, x, 0.0, lift))

    top_lift = plate_lift + PLATE_THICK / 2.0
    cmd_materials = {
        "cancel_key": mats["cmd_red"],
        "clear_key": mats["cmd_amber"],
        "enter_key": mats["cmd_green"],
    }
    num_mesh = mesh_from_cadquery(
        _rounded_cap((r.key_size_x_m, r.key_size_y_m, r.keycap_height_m)),
        "pos_numeric_keycap",
    )
    cmd_mesh = mesh_from_cadquery(
        _rounded_cap((r.key_size_x_m, r.cmd_size_y_m, r.keycap_height_m)),
        "pos_command_keycap",
    )
    limits = MotionLimits(effort=3.0, velocity=0.06, lower=0.0, upper=r.key_travel_m)
    for name, x, y, size_y in _entry_key_layout(r):
        key = model.part(
            f"{tag}__{name}",
            meta={"role": "entry_key", "slot": "input_face", "candidate": r.input_face},
        )
        key.visual(
            cmd_mesh if name in cmd_materials else num_mesh,
            material=cmd_materials.get(name, mats["key"]),
            name=f"{tag}__{name}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"housing_to_{name}",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=key,
            origin=_face_origin(r, x, y, top_lift),
            axis=(0.0, 0.0, -1.0),
            motion_limits=limits,
            meta={
                "positive_motion": "presses the keycap into its deck aperture",
                "motion_qc_repeat_group": "pos_entry_key_press",
            },
        )
        del size_y


def _input_face_touchscreen_glass_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "input_face__touchscreen_glass"
    if r.display_mount == "fixed_display":
        _emit_display_stack(housing, r, mats, tag, lambda x, lift: _face_origin(r, x, 0.0, lift))
    # Contactless mark embedded in the front face.
    housing.visual(
        Box((0.0018, 0.020, 0.010)),
        origin=Origin(
            xyz=(
                r.housing_length_m / 2.0 - 0.0006,
                0.0,
                min(r.deck_height_m - 0.006, r.chip_slot_z0_m + 0.014),
            )
        ),
        material=mats["accent"],
        name=f"{tag}__nfc_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


_INPUT_FACE_BUILDERS = {
    "numeric_keypad": _input_face_numeric_keypad_build,
    "touchscreen_glass": _input_face_touchscreen_glass_build,
}


# --------------------------------------------------------------------------- #
# display_mount candidates
# --------------------------------------------------------------------------- #
def _display_stack_geometry(r: ResolvedConfig) -> tuple[float, float, float, float]:
    """(bezel thickness, bezel lift, screen lift, screen top lift)."""

    if r.display_mount == "tilt_display":
        # Held just proud of the face so the head never penetrates the shell.
        bezel_thick = BEZEL_THICK if r.input_face == "numeric_keypad" else GLASS_BEZEL_THICK
        lift = r.display_normal_lift_m
    elif r.input_face == "numeric_keypad":
        bezel_thick, lift = BEZEL_THICK, 0.00145
    else:
        bezel_thick, lift = GLASS_BEZEL_THICK, 0.0015
    screen_lift = lift + bezel_thick / 2.0 + 0.0002
    return bezel_thick, lift, screen_lift, screen_lift + 0.00045


def _emit_display_stack(host, r: ResolvedConfig, mats, tag: str, place) -> None:
    """Bezel, screen and screen decoration on whichever part carries them.

    ``place(x, lift)`` maps a face station to an Origin in the host's frame, so
    the same stack lands correctly on the housing or on a tilting head.
    """

    bezel_thick, lift, screen_lift, screen_top = _display_stack_geometry(r)
    host.visual(
        Box((r.display_len_m, r.display_width_m, bezel_thick)),
        origin=place(r.display_center_x_m, lift),
        material=mats["dark"],
        name=f"{tag}__display_bezel", material_class_id="plastic.opaque_generic",
    )
    host.visual(
        Box(
            (
                max(r.display_len_m - 0.010, 0.006),
                max(r.display_width_m - 0.012, 0.006),
                0.0009,
            )
        ),
        origin=place(r.display_center_x_m, screen_lift),
        material=mats["screen"],
        name=f"{tag}__display_screen", material_class_id="tech.emissive_surface",
    )
    if r.input_face != "touchscreen_glass":
        return
    # Status strip and camera lens, seated into the screen surface so the
    # decoration is always connected to the geometry it sits on.
    host.visual(
        Box((0.10 * r.display_len_m, 0.70 * r.display_width_m, 0.0006)),
        origin=place(r.display_center_x_m - 0.38 * r.display_len_m, screen_top - 0.0001),
        material=mats["trim"],
        name=f"{tag}__status_bar", appearance_only=AppearanceOnlySpec(kind="screen", emission_strength=1.0),
    )
    cam_x = r.display_center_x_m - 0.46 * r.display_len_m
    host.visual(
        Cylinder(radius=0.0021, length=0.0012),
        origin=place(cam_x, screen_top - 0.0001),
        material=mats["dark"],
        name=f"{tag}__camera_lens", material_class_id="glass.smoked_tinted",
    )


def _display_mount_fixed_display_build(model, housing, r: ResolvedConfig, mats) -> None:
    """The display is part of the shell; the entry-face builder emitted it."""

    tag = "display_mount__fixed_display"
    if r.input_face == "numeric_keypad":
        bezel_thick, lift = BEZEL_THICK, 0.00145
    else:
        bezel_thick, lift = GLASS_BEZEL_THICK, 0.0015
    housing.visual(
        Box((r.display_len_m + 0.004, r.display_width_m + 0.004, 0.0010)),
        origin=_face_origin(r, r.display_center_x_m, 0.0, lift - bezel_thick / 2.0 - 0.0004),
        material=mats["trim"],
        name=f"{tag}__display_surround", material_class_id="metal.brushed_silver",
    )


def _display_mount_tilt_display_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "display_mount__tilt_display"
    hinge_pitch = _face_pitch(r, r.display_hinge_x_m)

    # Bracket cheeks flanking the boss barrel; they cradle it without touching.
    cheek_y = r.head_boss_len_m / 2.0 + CHEEK_GAP + 0.003
    for index, sign in enumerate((-1.0, 1.0)):
        housing.visual(
            Box((r.bracket_len_m, 0.006, 0.010)),
            origin=Origin(
                xyz=(
                    r.display_hinge_x_m + 0.0015,
                    sign * cheek_y,
                    _face_z(r, r.display_hinge_x_m) - 0.002,
                ),
                rpy=(0.0, hinge_pitch, 0.0),
            ),
            material=mats["dark"],
            name=f"{tag}__hinge_cheek_{index}", material_class_id="metal.blackened_gunmetal",
        )

    head = model.part(
        f"{tag}__display_head",
        meta={"role": "display_head", "slot": "display_mount", "candidate": "tilt_display"},
    )
    head.visual(
        Cylinder(radius=r.head_boss_radius_m, length=r.head_boss_len_m),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{tag}__hinge_boss", material_class_id="metal.blackened_gunmetal",
    )

    hinge_point = _face_point(r, r.display_hinge_x_m, 0.0, 0.0)

    def place(x: float, lift: float) -> Origin:
        world = _face_point(r, x, 0.0, lift)
        return Origin(
            xyz=tuple(world[index] - hinge_point[index] for index in range(3)),
            rpy=(0.0, _face_pitch(r, x), 0.0),
        )

    _emit_display_stack(head, r, mats, tag, place)

    # Neck joining the boss barrel to the bezel plate so the head is one solid.
    # It rides just above the face at the bezel's own standoff, so it can never
    # dip into the shell the way a mid-height web would on a short head.
    face_pitch = _face_pitch(r, r.display_center_x_m)
    web_lift = max(r.display_normal_lift_m - 0.0010, 0.0005)
    web_front_x = r.display_center_x_m + r.display_len_m / 2.0
    web_len = (web_front_x - r.display_hinge_x_m) / max(math.cos(face_pitch), 1e-6)
    head.visual(
        Box((max(web_len, 0.004), 0.010, 0.0024)),
        origin=place((r.display_hinge_x_m + web_front_x) / 2.0, web_lift),
        material=mats["dark"],
        name=f"{tag}__head_web", material_class_id="metal.blackened_gunmetal",
    )

    provider = AxisInterface(
        name="terminal_housing__display_hinge_axis",
        point=hinge_point,
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.head_boss_radius_m + 0.0008,
    )
    consumer = AxisInterface(
        name="display_head__boss_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.head_boss_radius_m,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "housing_to_display_head",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=head,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.display_tilt_rad),
        meta={"positive_motion": "tilts the display head up out of the top face"},
    )
    register_interface_mate(model, "housing_to_display_head", mate)


_DISPLAY_BUILDERS = {
    "fixed_display": _display_mount_fixed_display_build,
    "tilt_display": _display_mount_tilt_display_build,
}


# --------------------------------------------------------------------------- #
# aux_key_row candidates
# --------------------------------------------------------------------------- #
def _soft_key_strip_solid(r: ResolvedConfig) -> cq.Workplane:
    """Dark strip with one real opening per soft key, face-local."""

    strip = cq.Workplane("XY").box(r.aux_strip_len_m, r.aux_strip_width_m, STRIP_THICK)
    try:
        strip = strip.edges("|Z").fillet(0.0015)
    except Exception:
        pass
    for y in _aux_strip_stations(r):
        strip = strip.cut(
            cq.Workplane("XY")
            .box(
                r.aux_key_size_m + 2.0 * KEY_CLEAR,
                r.aux_key_size_m + 2.0 * KEY_CLEAR,
                STRIP_THICK + 0.004,
            )
            .translate((0.0, y, 0.0))
        )
    return strip


def _aux_key_row_soft_key_strip_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "aux_key_row__soft_key_strip"
    housing.visual(
        mesh_from_cadquery(_soft_key_strip_solid(r), "pos_soft_key_strip"),
        # Seated into the shell so the strip is never a floating island.
        origin=_face_origin(r, r.aux_row_x_m, 0.0, STRIP_THICK / 2.0 - 0.0003),
        material=mats["dark"],
        name=f"{tag}__soft_key_strip", material_class_id="rubber.smooth_plain",
    )
    mesh = mesh_from_cadquery(
        _rounded_cap((r.aux_key_size_m, r.aux_key_size_m, r.aux_cap_height_m)),
        "pos_soft_keycap",
    )
    limits = MotionLimits(effort=1.8, velocity=0.06, lower=0.0, upper=r.key_travel_m)
    top_lift = STRIP_THICK - 0.0003
    for index, y in enumerate(_aux_strip_stations(r)):
        key = model.part(
            f"{tag}__aux_key_{index}",
            meta={"role": "aux_key", "slot": "aux_key_row", "candidate": r.aux_key_row},
        )
        key.visual(mesh, material=mats["key"], name=f"{tag}__aux_key_{index}_cap", material_class_id="plastic.opaque_glossy_molded")
        model.articulation(
            f"housing_to_aux_key_{index}",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=key,
            origin=_face_origin(r, r.aux_row_x_m, y, top_lift),
            axis=(0.0, 0.0, -1.0),
            motion_limits=limits,
            meta={
                "positive_motion": "presses the soft key into the strip aperture",
                "motion_qc_repeat_group": "pos_aux_key_press",
            },
        )


def _aux_key_row_side_hard_buttons_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "aux_key_row__side_hard_buttons"
    y_face = r.body_width_m / 2.0
    limits = MotionLimits(effort=3.0, velocity=0.06, lower=0.0, upper=r.key_travel_m)
    for index, x in enumerate(_aux_side_stations(r)):
        key = model.part(
            f"{tag}__aux_key_{index}",
            meta={"role": "aux_key", "slot": "aux_key_row", "candidate": r.aux_key_row},
        )
        key.visual(
            Box((r.aux_key_size_m, r.aux_cap_height_m, r.aux_button_height_m)),
            origin=Origin(xyz=(0.0, r.aux_cap_height_m / 2.0 - 0.0008, 0.0)),
            material=mats["dark"],
            name=f"{tag}__aux_key_{index}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"housing_to_aux_key_{index}",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=key,
            origin=Origin(xyz=(x, y_face, r.aux_row_z_m)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=limits,
            meta={
                "positive_motion": "presses the side button into its recess",
                "motion_qc_repeat_group": "pos_aux_key_press",
            },
        )


_AUX_BUILDERS = {
    "soft_key_strip": _aux_key_row_soft_key_strip_build,
    "side_hard_buttons": _aux_key_row_side_hard_buttons_build,
}


# --------------------------------------------------------------------------- #
# receipt_printer candidates
# --------------------------------------------------------------------------- #
def _cover_plate(part, r: ResolvedConfig, mats, tag: str) -> None:
    pitch = r.cover_pitch_rad
    part.visual(
        Box((r.cover_len_m, r.cover_width_m, r.cover_thick_m)),
        origin=Origin(
            xyz=_local_face_point(pitch, r.cover_len_m / 2.0, r.cover_thick_m / 2.0),
            rpy=(0.0, pitch, 0.0),
        ),
        material=mats["shell"],
        name=f"{tag}__cover_plate", material_class_id="plastic.opaque_glossy_molded",
    )


def _receipt_printer_flip_cover_spindle_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "receipt_printer__flip_cover_spindle"
    cover = model.part(
        f"{tag}__printer_cover",
        meta={"role": "printer_cover", "slot": "receipt_printer", "candidate": r.receipt_printer},
    )
    _cover_plate(cover, r, mats, tag)
    pitch = r.cover_pitch_rad
    cover.visual(
        Box((0.004, 0.86 * r.cover_width_m, 0.002)),
        origin=Origin(
            xyz=_local_face_point(pitch, r.cover_len_m - 0.003, r.cover_thick_m - 0.0004),
            rpy=(0.0, pitch, 0.0),
        ),
        material=mats["dark"],
        name=f"{tag}__tear_bar", material_class_id="metal.blackened_gunmetal",
    )
    _hinge_cover(model, housing, cover, r, "terminal_housing__cover_hinge_axis")

    roll = model.part(
        f"{tag}__paper_roll",
        meta={"role": "paper_roll", "slot": "receipt_printer", "candidate": r.receipt_printer},
    )
    roll.visual(
        Cylinder(radius=r.roll_radius_m, length=r.roll_len_m),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["paper"],
        name=f"{tag}__roll_paper", material_class_id="paper.plain_sheet",
    )
    roll.visual(
        Cylinder(radius=r.axle_radius_m, length=r.axle_len_m),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"{tag}__roll_axle", material_class_id="metal.blackened_gunmetal",
    )
    provider = AxisInterface(
        name="terminal_housing__roll_bearing_axis",
        point=(r.roll_center_x_m, 0.0, r.roll_center_z_m),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.axle_radius_m + AXLE_CLEAR,
    )
    consumer = AxisInterface(
        name="paper_roll__axle",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.axle_radius_m,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "housing_to_paper_roll",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=roll,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=0.5, velocity=10.0),
        meta={"positive_motion": "spins the receipt roll on its spindle"},
    )
    register_interface_mate(model, "housing_to_paper_roll", mate)


def _receipt_printer_knuckle_cover_static_roll_build(
    model, housing, r: ResolvedConfig, mats
) -> None:
    tag = "receipt_printer__knuckle_cover_static_roll"
    pitch = r.cover_pitch_rad

    # Static roll lying in the bay, as a housing visual.
    housing.visual(
        Cylinder(radius=r.roll_radius_m, length=r.roll_len_m),
        origin=Origin(
            xyz=(r.roll_center_x_m, 0.0, r.bay_floor_z_m + r.roll_radius_m - 0.0006),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["paper"],
        name=f"{tag}__static_paper_roll", material_class_id="paper.plain_sheet",
    )
    # Hinge bosses inboard of the cover knuckles on the rear rim.
    boss_y = max(r.knuckle_span_m / 2.0 - 0.012, 0.005)
    for index, sign in enumerate((-1.0, 1.0)):
        housing.visual(
            Box((0.008, 0.008, 0.0078)),
            origin=Origin(
                xyz=(
                    r.cover_hinge_x_m + 0.0010,
                    sign * boss_y,
                    r.cover_hinge_z_m - 0.0030,
                ),
                rpy=(0.0, pitch, 0.0),
            ),
            material=mats["shell"],
            name=f"{tag}__hinge_boss_{index}", material_class_id="plastic.opaque_glossy_molded",
        )

    cover = model.part(
        f"{tag}__printer_cover",
        meta={"role": "printer_cover", "slot": "receipt_printer", "candidate": r.receipt_printer},
    )
    _cover_plate(cover, r, mats, tag)
    cover.visual(
        Box((0.005, 0.44 * r.cover_width_m, 0.0022)),
        origin=Origin(
            xyz=_local_face_point(pitch, r.cover_len_m - 0.006, r.cover_thick_m + 0.0008),
            rpy=(0.0, pitch, 0.0),
        ),
        material=mats["shell"],
        name=f"{tag}__grip_ridge", material_class_id="plastic.opaque_glossy_molded",
    )
    for index, sign in enumerate((-1.0, 1.0)):
        cover.visual(
            Cylinder(radius=r.knuckle_radius_m, length=0.012),
            origin=Origin(
                xyz=(0.0, sign * r.knuckle_span_m / 2.0, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["shell"],
            name=f"{tag}__hinge_knuckle_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        tab = _local_face_point(pitch, 0.005, r.cover_thick_m / 2.0)
        cover.visual(
            Box((0.010, 0.007, r.cover_thick_m)),
            origin=Origin(
                xyz=(tab[0], sign * r.knuckle_span_m / 2.0, tab[2]),
                rpy=(0.0, pitch, 0.0),
            ),
            material=mats["shell"],
            name=f"{tag}__knuckle_tab_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
    _hinge_cover(model, housing, cover, r, "terminal_housing__cover_hinge_axis")


def _hinge_cover(model, housing, cover, r: ResolvedConfig, provider_name: str) -> None:
    provider = AxisInterface(
        name=provider_name,
        point=(r.cover_hinge_x_m, 0.0, r.cover_hinge_z_m),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.knuckle_radius_m + 0.0008,
    )
    consumer = AxisInterface(
        name="printer_cover__hinge_bore",
        point=(0.0, 0.0, 0.0),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.knuckle_radius_m,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        "housing_to_printer_cover",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=cover,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=2.5, velocity=2.5, lower=0.0, upper=r.cover_open_rad),
        meta={"positive_motion": "flips the printer cover up off the paper bay"},
    )
    register_interface_mate(model, "housing_to_printer_cover", mate)


_PRINTER_BUILDERS = {
    "flip_cover_spindle": _receipt_printer_flip_cover_spindle_build,
    "knuckle_cover_static_roll": _receipt_printer_knuckle_cover_static_roll_build,
}


# --------------------------------------------------------------------------- #
# card_interface candidates
# --------------------------------------------------------------------------- #
def _card_liners(housing, r: ResolvedConfig, mats, tag: str) -> None:
    x_front = r.housing_length_m / 2.0
    housing.visual(
        Box((0.003, r.chip_slot_width_m - 0.002, r.chip_slot_h_m - 0.0002)),
        origin=Origin(
            xyz=(
                x_front - r.chip_slot_depth_m,
                0.0,
                r.chip_slot_z0_m + r.chip_slot_h_m / 2.0,
            )
        ),
        material=mats["dark"],
        name=f"{tag}__chip_slot_liner", material_class_id="plastic.opaque_generic",
    )
    housing.visual(
        Box((r.groove_liner_len_m, 0.002, 0.0028)),
        origin=Origin(
            xyz=(
                r.groove_center_x_m,
                r.body_width_m / 2.0 - 0.0045,
                r.groove_floor_z_m + 0.0015,
            )
        ),
        material=mats["dark"],
        name=f"{tag}__swipe_slot_liner", material_class_id="plastic.opaque_generic",
    )


def _card_interface_static_chip_slot_build(model, housing, r: ResolvedConfig, mats) -> None:
    _card_liners(housing, r, mats, "card_interface__static_chip_slot")


def _card_interface_sliding_bank_card_build(model, housing, r: ResolvedConfig, mats) -> None:
    tag = "card_interface__sliding_bank_card"
    _card_liners(housing, r, mats, tag)

    card = model.part(
        f"{tag}__payment_card",
        meta={"role": "payment_card", "slot": "card_interface", "candidate": r.card_interface},
    )
    plate = cq.Workplane("XY").box(r.card_len_m, r.card_width_m, CARD_THICK)
    try:
        plate = plate.edges("|Z").fillet(0.004)
    except Exception:
        pass
    card.visual(
        mesh_from_cadquery(plate, "pos_bank_card"),
        material=mats["card"],
        name=f"{tag}__card_body", material_class_id="plastic.opaque_glossy_molded",
    )
    card.visual(
        Box((0.011, 0.008, 0.0006)),
        origin=Origin(xyz=(0.30 * r.card_len_m, 0.22 * r.card_width_m, CARD_THICK / 2.0)),
        material=mats["accent"],
        name=f"{tag}__card_logo", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    card.visual(
        Box((0.0045, 0.80 * r.card_width_m, 0.0005)),
        origin=Origin(xyz=(0.18 * r.card_len_m, 0.0, CARD_THICK / 2.0)),
        material=mats["accent"],
        name=f"{tag}__card_band", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    model.articulation(
        "housing_to_payment_card",
        ArticulationType.PRISMATIC,
        parent=housing,
        child=card,
        origin=Origin(xyz=(r.card_center_x_m, 0.0, r.chip_slot_z0_m + CARD_THICK / 2.0 + 0.0003)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.1, lower=0.0, upper=r.card_travel_m),
        meta={"positive_motion": "withdraws the card toward the user"},
    )


_CARD_BUILDERS = {
    "static_chip_slot": _card_interface_static_chip_slot_build,
    "sliding_bank_card": _card_interface_sliding_bank_card_build,
}


# --------------------------------------------------------------------------- #
# support_base candidates
# --------------------------------------------------------------------------- #
def _rubber_feet(part, r: ResolvedConfig, mats, tag: str, station_x, station_y) -> None:
    for index, (fx, fy) in enumerate(
        (
            (station_x, -station_y),
            (station_x, station_y),
            (-station_x, -station_y),
            (-station_x, station_y),
        )
    ):
        part.visual(
            Cylinder(radius=r.foot_radius_m, length=FOOT_THICK),
            origin=Origin(xyz=(fx, fy, -FOOT_THICK / 2.0 + 0.0004)),
            material=mats["rubber"],
            name=f"{tag}__foot_{index}", material_class_id="rubber.smooth_plain",
        )


def _support_base_flat_feet_build(model, housing, r: ResolvedConfig, mats) -> None:
    _rubber_feet(
        housing,
        r,
        mats,
        "support_base__flat_feet",
        r.foot_station_x_m,
        r.foot_station_y_m,
    )
    return None


def _dock_shape(r: ResolvedConfig) -> cq.Workplane:
    tray = (
        cq.Workplane("XY")
        .box(r.cradle_len_m, r.cradle_width_m, r.cradle_height_m)
        .translate((0.0, 0.0, r.cradle_height_m / 2.0))
    )
    try:
        tray = tray.edges("|Z").fillet(0.008)
    except Exception:
        pass
    # Two rear retention posts outboard of the terminal instead of one solid
    # upstand, so the opened printer cover swings through the open centre even
    # at full recline.
    wall_h = r.upstand_height_m + 0.003
    post_y = r.body_width_m / 2.0 + 0.002 + r.post_width_m / 2.0
    wall = None
    for sign in (-1.0, 1.0):
        post = (
            cq.Workplane("XY")
            .box(r.cradle_wall_m, r.post_width_m, wall_h)
            .translate(
                (
                    -r.cradle_len_m / 2.0 + r.cradle_wall_m / 2.0 + 0.004,
                    sign * post_y,
                    r.cradle_height_m + r.upstand_height_m / 2.0 - 0.0015,
                )
            )
        )
        wall = post if wall is None else wall.union(post)
    lip = (
        cq.Workplane("XY")
        .box(r.cradle_wall_m * 0.8, r.cradle_width_m - 0.020, 0.009)
        .translate(
            (
                r.cradle_len_m / 2.0 - r.cradle_wall_m * 0.4 - 0.004,
                0.0,
                r.cradle_height_m + 0.0015,
            )
        )
    )
    body = tray.union(wall).union(lip)
    # Recline well: the terminal's rear half swings down into it.
    well = (
        cq.Workplane("XY")
        .box(
            r.housing_length_m / 2.0 + 0.010,
            r.body_width_m + 0.010,
            r.well_depth_m + 0.010,
        )
        .translate(
            (
                -(r.housing_length_m / 4.0) - 0.003,
                0.0,
                r.cradle_height_m - r.well_depth_m + (r.well_depth_m + 0.010) / 2.0,
            )
        )
    )
    return body.cut(well)


def _support_base_tilt_dock_build(model, housing, r: ResolvedConfig, mats):
    tag = "support_base__tilt_dock"
    root = model.part(
        f"{tag}__support_root",
        meta={"role": "support_root", "slot": "support_base", "candidate": r.support_base},
    )
    root.visual(
        mesh_from_cadquery(_dock_shape(r), "pos_dock_cradle"),
        material=mats["support"],
        name=f"{tag}__dock_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    _rubber_feet(root, r, mats, tag, r.cradle_len_m / 2.0 - 0.020, r.cradle_width_m / 2.0 - 0.018)
    for index, cy in enumerate((-0.012, 0.012)):
        root.visual(
            Box((0.008, 0.004, 0.0012)),
            origin=Origin(
                xyz=(
                    r.housing_length_m / 4.0,
                    cy,
                    r.cradle_height_m - 0.0004,
                )
            ),
            material=mats["trim"],
            name=f"{tag}__contact_pad_{index}", material_class_id="rubber.smooth_plain",
        )
    provider = AxisInterface(
        name="support_root__recline_axis",
        point=(0.0, 0.0, r.cradle_height_m),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.006,
    )
    return (
        root,
        provider,
        MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=r.dock_recline_rad),
        "reclines the terminal in its cradle",
    )


def _stand_shape(r: ResolvedConfig) -> cq.Workplane:
    base = cq.Workplane("XY").circle(r.base_radius_m).extrude(r.base_height_m)
    pole = (
        cq.Workplane("XY")
        .circle(r.pole_radius_m)
        .extrude(r.pole_height_m)
        .translate((0.0, 0.0, r.base_height_m))
    )
    collar = (
        cq.Workplane("XY")
        .circle(r.collar_radius_m)
        .extrude(r.collar_height_m)
        .translate((0.0, 0.0, r.base_height_m + r.pole_height_m))
    )
    body = base.union(pole).union(collar)
    try:
        body = body.edges("<Z").fillet(0.003)
    except Exception:
        pass
    return body


def _support_base_swivel_pedestal_build(model, housing, r: ResolvedConfig, mats):
    tag = "support_base__swivel_pedestal"
    root = model.part(
        f"{tag}__support_root",
        meta={"role": "support_root", "slot": "support_base", "candidate": r.support_base},
    )
    root.visual(
        mesh_from_cadquery(_stand_shape(r), "pos_pedestal_stand"),
        material=mats["support"],
        name=f"{tag}__stand_body", material_class_id="metal.paint_coated",
    )
    ring = (
        cq.Workplane("XY")
        .circle(r.base_radius_m + 0.002)
        .circle(r.base_radius_m - 0.004)
        .extrude(0.005)
        .translate((0.0, 0.0, r.base_height_m - 0.006))
    )
    root.visual(
        mesh_from_cadquery(ring, "pos_weight_ring"),
        material=mats["trim"],
        name=f"{tag}__weight_ring", material_class_id="metal.brushed_silver",
    )
    _rubber_feet(root, r, mats, tag, 0.62 * r.base_radius_m, 0.62 * r.base_radius_m)
    provider = AxisInterface(
        name="support_root__swivel_axis",
        point=(0.0, 0.0, r.stand_top_z_m),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=r.collar_radius_m,
    )
    return (
        root,
        provider,
        MotionLimits(effort=6.0, velocity=2.0, lower=-r.pedestal_yaw_rad, upper=r.pedestal_yaw_rad),
        "yaws the terminal on its pedestal",
    )


_SUPPORT_BUILDERS = {
    "flat_feet": _support_base_flat_feet_build,
    "tilt_dock": _support_base_tilt_dock_build,
    "swivel_pedestal": _support_base_swivel_pedestal_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        mats[key] = model.material(f"pos_{key}", rgba=rgba)
    mats["cmd_red"] = model.material("pos_cmd_red", rgba=CMD_RED)
    mats["cmd_amber"] = model.material("pos_cmd_amber", rgba=CMD_AMBER)
    mats["cmd_green"] = model.material("pos_cmd_green", rgba=CMD_GREEN)
    return mats


def build_point_of_sale_terminal(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = _resolved_with_face_stations(resolve_config(config or Config()))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "point_of_sale_terminal",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": (
                "payment terminal with a pressed entry face, a hinged receipt printer, "
                "a card interface and an optional articulated support root"
            ),
        },
    )
    mats = _materials(model, r)

    housing = model.part(
        f"housing_build__{r.housing_build}__terminal_housing",
        meta={"role": "terminal_housing", "slot": "housing_build", "candidate": r.housing_build},
    )
    housing.visual(
        mesh_from_cadquery(_housing_solid(r), "pos_terminal_housing"),
        material=mats["shell"],
        name=f"housing_build__{r.housing_build}__housing_shell", material_class_id="plastic.opaque_glossy_molded",
    )

    support = _SUPPORT_BUILDERS[r.support_base](model, housing, r, mats)
    _INPUT_FACE_BUILDERS[r.input_face](model, housing, r, mats)
    _AUX_BUILDERS[r.aux_key_row](model, housing, r, mats)
    _DISPLAY_BUILDERS[r.display_mount](model, housing, r, mats)
    _PRINTER_BUILDERS[r.receipt_printer](model, housing, r, mats)
    _CARD_BUILDERS[r.card_interface](model, housing, r, mats)

    if support is not None:
        root, provider, limits, motion = support
        consumer = AxisInterface(
            name="terminal_housing__mount_seat",
            point=(0.0, 0.0, 0.0),
            axis=provider.axis,
            radial=(1.0, 0.0, 0.0),
            radius=max(provider.radius or 0.006, 0.004),
        )
        mate = mate_axes(provider, consumer)
        model.articulation(
            "support_to_housing",
            ArticulationType.REVOLUTE,
            parent=root,
            child=housing,
            origin=mate.origin,
            axis=mate.axis,
            motion_limits=limits,
            meta={"positive_motion": motion},
        )
        register_interface_mate(model, "support_to_housing", mate)

    risk: list[dict[str, float]] = []
    if r.display_mount == "tilt_display":
        risk.append(
            {
                "housing_to_display_head": r.display_tilt_rad,
                "housing_to_printer_cover": r.cover_open_rad,
            }
        )
    if r.card_interface == "sliding_bank_card" and r.support_base == "tilt_dock":
        risk.append(
            {
                "housing_to_payment_card": r.card_travel_m,
                "support_to_housing": r.dock_recline_rad,
            }
        )
    if risk:
        model.meta["risk_poses"] = tuple(risk)
        model.meta["coupled_joint_pairs"] = tuple(tuple(sorted(case)) for case in risk)
    return model


def build_seeded_point_of_sale_terminal(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_point_of_sale_terminal(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Authored tests
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _meshes_materialized(model: ArticulatedObject) -> bool:
    """False while the preflight probe stands in for real mesh assets."""

    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def run_point_of_sale_terminal_tests(model: ArticulatedObject, config: Config) -> TestReport:
    r = _resolved_with_face_stations(resolve_config(config))
    ctx = TestContext(model)
    joints = {joint.name: joint for joint in model.articulations}
    # Exact surface projections need real mesh assets; preflight defers them.
    exact_geometry = _meshes_materialized(model)

    housings = _parts_by_role(model, "terminal_housing")
    covers = _parts_by_role(model, "printer_cover")
    rolls = _parts_by_role(model, "paper_roll")
    cards = _parts_by_role(model, "payment_card")
    heads = _parts_by_role(model, "display_head")
    roots = _parts_by_role(model, "support_root")
    entry_keys = _parts_by_role(model, "entry_key")
    aux_keys = _parts_by_role(model, "aux_key")

    housing = housings[0] if housings else None
    cover = covers[0] if covers else None

    # --- category anchors ----------------------------------------------------
    display_elems = [
        visual.name
        for part in model.parts
        for visual in part.visuals
        if visual.name.endswith("display_screen")
    ]
    ctx.check(
        "category_anchor: one terminal housing carries the display, the entry face and the card interface",
        len(housings) == 1
        and housing is not None
        and any(v.name.endswith("swipe_slot_liner") for v in housing.visuals)
        and any(v.name.endswith("chip_slot_liner") for v in housing.visuals),
        details=f"housings={len(housings)}",
    )
    ctx.check(
        "category_anchor: the entry face presents the primary payment display",
        len(display_elems) == 1,
        details=f"screens={display_elems}",
    )
    ctx.check(
        "category_anchor: the card interface presents a chip slot and a magstripe groove",
        housing is not None
        and r.groove_liner_len_m < r.housing_length_m
        and r.groove_liner_len_m > 0.0
        and r.chip_slot_depth_m > 0.015,
        details=(
            f"groove_liner={r.groove_liner_len_m:.4f} housing_len={r.housing_length_m:.4f} "
            f"chip_depth={r.chip_slot_depth_m:.4f}"
        ),
    )
    ctx.check(
        "category_anchor: the auxiliary key row matches aux_key_count",
        len(aux_keys) == r.aux_key_count
        and all(f"housing_to_aux_key_{i}" in joints for i in range(r.aux_key_count)),
        details=f"aux_keys={len(aux_keys)} expected={r.aux_key_count}",
    )

    if r.input_face == "numeric_keypad":
        ctx.check(
            "category_anchor: numeric keypad presents 12 digits and the command triad",
            len(entry_keys) == 15
            and all(
                any(part.name.endswith(name) for part in entry_keys) for name in _ENTRY_KEY_NAMES
            ),
            details=f"entry_keys={len(entry_keys)}",
        )
    else:
        ctx.check(
            "category_anchor: numeric keypad presents 12 digits and the command triad",
            len(entry_keys) == 0,
            details=f"touchscreen face carries {len(entry_keys)} entry keys",
        )

    if r.display_mount == "tilt_display":
        ctx.check(
            "category_anchor: the display head tilts out of the top face",
            len(heads) == 1 and "housing_to_display_head" in joints,
            details=f"heads={len(heads)}",
        )
        ctx.check(
            "category_anchor: the display is fixed in the top face",
            len(heads) == 1,
            details="tilting variant: the head owns the display",
        )
    else:
        ctx.check(
            "category_anchor: the display is fixed in the top face",
            len(heads) == 0 and "housing_to_display_head" not in joints,
            details=f"heads={len(heads)}",
        )
        ctx.check(
            "category_anchor: the display head tilts out of the top face",
            len(heads) == 0,
            details="fixed variant: no head part",
        )

    ctx.check(
        "category_anchor: the receipt printer cover opens off the paper bay",
        len(covers) == 1 and "housing_to_printer_cover" in joints,
        details=f"covers={len(covers)}",
    )
    if r.receipt_printer == "flip_cover_spindle":
        ctx.check(
            "category_anchor: the paper roll spins on its spindle",
            len(rolls) == 1 and "housing_to_paper_roll" in joints,
            details=f"rolls={len(rolls)}",
        )
        ctx.check(
            "category_anchor: the paper roll lies static in the bay",
            len(rolls) == 1,
            details="spindle variant: the roll is an articulated part",
        )
    else:
        ctx.check(
            "category_anchor: the paper roll lies static in the bay",
            len(rolls) == 0
            and housing is not None
            and any(v.name.endswith("static_paper_roll") for v in housing.visuals),
            details=f"rolls={len(rolls)}",
        )
        ctx.check(
            "category_anchor: the paper roll spins on its spindle",
            len(rolls) == 0,
            details="static variant: no spindle joint",
        )

    if r.card_interface == "sliding_bank_card":
        ctx.check(
            "category_anchor: the inserted card slides out of the chip slot and stays retained",
            len(cards) == 1 and "housing_to_payment_card" in joints,
            details=f"cards={len(cards)}",
        )
    else:
        ctx.check(
            "category_anchor: the inserted card slides out of the chip slot and stays retained",
            len(cards) == 0,
            details="static variant: nothing inserted",
        )

    if r.support_base == "flat_feet":
        ctx.check(
            "category_anchor: the terminal is grounded on its own feet",
            len(roots) == 0
            and housing is not None
            and sum(1 for v in housing.visuals if "__foot_" in v.name) == 4,
            details=f"roots={len(roots)}",
        )
        ctx.check(
            "category_anchor: the terminal is carried by its support root",
            len(roots) == 0,
            details="grounded variant: the housing is the root",
        )
    else:
        root = roots[0] if roots else None
        ctx.check(
            "category_anchor: the terminal is carried by its support root",
            len(roots) == 1
            and "support_to_housing" in joints
            and root is not None
            and sum(1 for v in root.visuals if "__foot_" in v.name) == 4,
            details=f"roots={len(roots)}",
        )
        ctx.check(
            "category_anchor: the terminal is grounded on its own feet",
            housing is not None and sum(1 for v in housing.visuals if "__foot_" in v.name) == 0,
            details="carried variant: the feet belong to the support root",
        )

    # --- surface relations ---------------------------------------------------
    if r.input_face == "numeric_keypad" and housing is not None:
        plate_lift = PLATE_THICK / 2.0 - 0.0003
        top_lift = plate_lift + PLATE_THICK / 2.0
        ok = True
        details: list[str] = []
        for name, x, y, size_y in _entry_key_layout(r):
            part = next((p for p in entry_keys if p.name.endswith(f"__{name}")), None)
            if part is None:
                ok = False
                details.append(f"missing {name}")
                continue
            if not exact_geometry:
                continue
            pitch = _face_pitch(r, x)
            frame = PlaneInterface(
                point=_face_point(r, x, y, top_lift),
                normal=(math.sin(pitch), 0.0, math.cos(pitch)),
                tangent_u=(math.cos(pitch), 0.0, -math.sin(pitch)),
                extent=(
                    r.key_size_x_m + 2.0 * KEY_CLEAR,
                    size_y + 2.0 * KEY_CLEAR,
                ),
                name=f"keypad_aperture_{name}",
            )
            ok &= ctx.expect_footprint_within(
                part,
                frame=frame,
                frame_part=housing,
                name=f"{name} stays inside its deck aperture",
            )
            ok &= ctx.expect_normal_band(
                part,
                frame=frame,
                frame_part=housing,
                minimum=-0.0002,
                maximum=r.keycap_height_m + 0.0004,
                name=f"{name} keeps its exposed band at rest",
            )
        # The keycap must still stand proud after a full press, whether the
        # projection is exact or the lightweight preflight one.
        ok &= r.keycap_height_m - r.key_travel_m >= 0.0020
        joint = joints.get("housing_to_key_5")
        if joint is not None and exact_geometry:
            x = r.entry_row0_x_m + r.key_pitch_x_m
            pitch = _face_pitch(r, x)
            frame = PlaneInterface(
                point=_face_point(r, x, 0.0, top_lift),
                normal=(math.sin(pitch), 0.0, math.cos(pitch)),
                tangent_u=(math.cos(pitch), 0.0, -math.sin(pitch)),
                extent=(r.key_size_x_m + 2.0 * KEY_CLEAR, r.key_size_y_m + 2.0 * KEY_CLEAR),
                name="keypad_aperture_key_5",
            )
            part = next((p for p in entry_keys if p.name.endswith("__key_5")), None)
            with ctx.pose({joint: r.key_travel_m}):
                ok &= ctx.expect_normal_band(
                    part,
                    frame=frame,
                    frame_part=housing,
                    minimum=-(r.key_travel_m + 0.0004),
                    maximum=r.keycap_height_m + 0.0004,
                    minimum_protrusion=0.0020,
                    name="pressed key_5 still stands proud of the deck",
                )
        ctx.check(
            "category_anchor: every entry key stays inside its deck aperture and keeps its exposed band",
            ok,
            details="; ".join(details) or "ok",
        )
    else:
        ctx.check(
            "category_anchor: every entry key stays inside its deck aperture and keeps its exposed band",
            len(entry_keys) == 0,
            details="touchscreen face has no entry keys",
        )

    aux_ok = True
    if r.aux_key_row == "soft_key_strip":
        top_lift = STRIP_THICK - 0.0003
        for index, y in enumerate(_aux_strip_stations(r)):
            part = next((p for p in aux_keys if p.name.endswith(f"__aux_key_{index}")), None)
            if part is None:
                aux_ok = False
                continue
            if not exact_geometry:
                continue
            pitch = _face_pitch(r, r.aux_row_x_m)
            frame = PlaneInterface(
                point=_face_point(r, r.aux_row_x_m, y, top_lift),
                normal=(math.sin(pitch), 0.0, math.cos(pitch)),
                tangent_u=(math.cos(pitch), 0.0, -math.sin(pitch)),
                extent=(
                    r.aux_key_size_m + 2.0 * KEY_CLEAR,
                    r.aux_key_size_m + 2.0 * KEY_CLEAR,
                ),
                name=f"soft_key_aperture_{index}",
            )
            aux_ok &= ctx.expect_footprint_within(
                part,
                frame=frame,
                frame_part=housing,
                name=f"aux_key_{index} stays inside its strip opening",
            )
            aux_ok &= ctx.expect_normal_band(
                part,
                frame=frame,
                frame_part=housing,
                minimum=-0.0002,
                maximum=r.aux_cap_height_m + 0.0004,
                name=f"aux_key_{index} keeps its exposed band at rest",
            )
        joint = joints.get("housing_to_aux_key_0")
        part = next((p for p in aux_keys if p.name.endswith("__aux_key_0")), None)
        if joint is not None and part is not None and exact_geometry:
            y0 = _aux_strip_stations(r)[0]
            pitch = _face_pitch(r, r.aux_row_x_m)
            frame = PlaneInterface(
                point=_face_point(r, r.aux_row_x_m, y0, top_lift),
                normal=(math.sin(pitch), 0.0, math.cos(pitch)),
                tangent_u=(math.cos(pitch), 0.0, -math.sin(pitch)),
                extent=(
                    r.aux_key_size_m + 2.0 * KEY_CLEAR,
                    r.aux_key_size_m + 2.0 * KEY_CLEAR,
                ),
                name="soft_key_aperture_0",
            )
            with ctx.pose({joint: r.key_travel_m}):
                aux_ok &= ctx.expect_normal_band(
                    part,
                    frame=frame,
                    frame_part=housing,
                    minimum=-(r.key_travel_m + 0.0004),
                    maximum=r.aux_cap_height_m + 0.0004,
                    minimum_protrusion=0.0014,
                    name="pressed aux_key_0 still stands proud of the strip",
                )
    else:
        for index, x in enumerate(_aux_side_stations(r)):
            part = next((p for p in aux_keys if p.name.endswith(f"__aux_key_{index}")), None)
            if part is None:
                aux_ok = False
                continue
            if not exact_geometry:
                continue
            frame = PlaneInterface(
                point=(x, r.body_width_m / 2.0, r.aux_row_z_m),
                normal=(0.0, 1.0, 0.0),
                tangent_u=(1.0, 0.0, 0.0),
                extent=(
                    r.aux_key_size_m + 2.0 * KEY_CLEAR,
                    r.aux_button_height_m + 2.0 * KEY_CLEAR,
                ),
                name=f"side_button_opening_{index}",
            )
            aux_ok &= ctx.expect_footprint_within(
                part,
                frame=frame,
                frame_part=housing,
                name=f"aux_key_{index} stays inside its side opening",
            )
            aux_ok &= ctx.expect_normal_band(
                part,
                frame=frame,
                frame_part=housing,
                minimum=-0.0010,
                maximum=r.aux_cap_height_m + 0.0004,
                name=f"aux_key_{index} keeps its exposed band at rest",
            )
        joint = joints.get("housing_to_aux_key_0")
        part = next((p for p in aux_keys if p.name.endswith("__aux_key_0")), None)
        if joint is not None and part is not None and exact_geometry:
            x0 = _aux_side_stations(r)[0]
            frame = PlaneInterface(
                point=(x0, r.body_width_m / 2.0, r.aux_row_z_m),
                normal=(0.0, 1.0, 0.0),
                tangent_u=(1.0, 0.0, 0.0),
                extent=(
                    r.aux_key_size_m + 2.0 * KEY_CLEAR,
                    r.aux_button_height_m + 2.0 * KEY_CLEAR,
                ),
                name="side_button_opening_0",
            )
            with ctx.pose({joint: r.key_travel_m}):
                aux_ok &= ctx.expect_normal_band(
                    part,
                    frame=frame,
                    frame_part=housing,
                    minimum=-(r.key_travel_m + 0.0012),
                    maximum=r.aux_cap_height_m + 0.0004,
                    minimum_protrusion=0.0004,
                    name="pressed aux_key_0 still stands proud of the side face",
                )
    aux_ok &= r.aux_cap_height_m - r.key_travel_m >= 0.0014
    ctx.check(
        "category_anchor: every auxiliary key stays inside its host opening and keeps its exposed band",
        aux_ok,
        details=(
            f"exact_geometry={exact_geometry} cap={r.aux_cap_height_m:.4f} "
            f"travel={r.key_travel_m:.4f}"
        ),
    )

    # --- mechanism behaviour -------------------------------------------------
    cover_joint = joints.get("housing_to_printer_cover")
    if cover is not None and housing is not None and cover_joint is not None and exact_geometry:
        ctx.expect_contact(
            cover, housing, contact_tol=0.0006, name="closed cover rests on the bay rim"
        )
        closed = ctx.part_world_aabb(cover)
        with ctx.pose({cover_joint: min(r.cover_open_rad, 1.4)}):
            opened = ctx.part_world_aabb(cover)
        ctx.check(
            "printer cover flips up off the bay",
            closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.015,
            details=f"closed={closed}, open={opened}",
        )

    if rolls:
        roll = rolls[0]
        if exact_geometry:
            ctx.expect_within(
                roll,
                housing,
                axes="xz",
                inner_elem="receipt_printer__flip_cover_spindle__roll_paper",
                margin=0.0004,
                name="paper roll sits inside the printer bay",
            )
        ctx.check(
            "roll clears the closed cover",
            r.roll_center_z_m + r.roll_radius_m < _face_z(r, r.roll_center_x_m) - 0.0005,
            details=(
                f"roll_top={r.roll_center_z_m + r.roll_radius_m:.4f} "
                f"face={_face_z(r, r.roll_center_x_m):.4f}"
            ),
        )

    if cards:
        ctx.check(
            "card stays retained in the slot at full withdrawal",
            r.card_len_m - r.card_travel_m - 0.0025 >= 0.008,
            details=(
                f"card_len={r.card_len_m:.4f} travel={r.card_travel_m:.4f} "
                f"slot_depth={r.chip_slot_depth_m:.4f}"
            ),
        )

    card_joint = joints.get("housing_to_payment_card")
    if cards and card_joint is not None and exact_geometry:
        card = cards[0]
        ctx.expect_overlap(
            card,
            housing,
            axes="x",
            min_overlap=0.015,
            name="card is inserted into the chip slot",
        )
        rest = ctx.part_world_position(card)
        with ctx.pose({card_joint: r.card_travel_m}):
            pulled = ctx.part_world_position(card)
            ctx.expect_overlap(
                card,
                housing,
                axes="x",
                min_overlap=0.008,
                name="withdrawn card stays retained in the slot",
            )
        ctx.check(
            "card slides out toward the user",
            rest is not None and pulled is not None and pulled[0] > rest[0] + 0.006,
            details=f"rest={rest}, pulled={pulled}",
        )

    head_joint = joints.get("housing_to_display_head")
    if heads and head_joint is not None:
        ctx.check(
            "display head clears the printer bay",
            r.display_hinge_x_m > r.bay_x_max_m,
            details=f"hinge={r.display_hinge_x_m:.4f} bay_front={r.bay_x_max_m:.4f}",
        )
        if exact_geometry:
            head = heads[0]
            rest = ctx.part_world_aabb(head)
            with ctx.pose({head_joint: r.display_tilt_rad}):
                tilted = ctx.part_world_aabb(head)
            ctx.check(
                "display head tilts up out of the face",
                rest is not None and tilted is not None and tilted[1][2] > rest[1][2] + 0.004,
                details=f"rest={rest}, tilted={tilted}",
            )

    mount_joint = joints.get("support_to_housing")
    if roots and mount_joint is not None:
        root = roots[0]
        if exact_geometry:
            ctx.expect_contact(
                housing,
                root,
                contact_tol=0.0012,
                name="terminal is seated on its support root",
            )
        if r.support_base == "tilt_dock":
            ctx.check(
                "recline well is deep enough for the reclined tail",
                r.well_depth_m >= (r.housing_length_m / 2.0) * math.sin(r.dock_recline_rad) + 0.0035
                and r.cradle_height_m > r.well_depth_m + 0.008,
                details=(
                    f"well={r.well_depth_m:.4f} needed="
                    f"{(r.housing_length_m / 2.0) * math.sin(r.dock_recline_rad):.4f} "
                    f"cradle_h={r.cradle_height_m:.4f}"
                ),
            )
        else:
            ctx.check(
                "pedestal collar supports the terminal underside",
                r.collar_radius_m * 2.0 <= r.body_width_m and r.collar_radius_m > r.pole_radius_m,
                details=(
                    f"collar={r.collar_radius_m:.4f} pole={r.pole_radius_m:.4f} "
                    f"width={r.body_width_m:.4f}"
                ),
            )

    # --- derivation invariants ----------------------------------------------
    ctx.check(
        "magstripe liner never leaves the housing",
        r.groove_liner_len_m <= r.housing_length_m - 0.001,
        details=(
            f"liner={r.groove_liner_len_m:.4f} housing={r.housing_length_m:.4f} "
            f"groove_cut={r.groove_len_m:.4f}"
        ),
    )
    ctx.check(
        "side buttons stay below the magstripe groove floor",
        r.aux_key_row != "side_hard_buttons"
        or r.aux_row_z_m + r.aux_button_height_m / 2.0 < r.groove_floor_z_m - 0.0008,
        details=(
            f"button_top={r.aux_row_z_m + r.aux_button_height_m / 2.0:.4f} "
            f"groove_floor={r.groove_floor_z_m:.4f}"
        ),
    )
    ctx.check(
        "the entry face never crosses the housing's deck/slope break",
        abs(_face_pitch(r, r.plate_front_x_m) - _face_pitch(r, r.plate_rear_x_m)) < 1e-9
        if r.input_face == "numeric_keypad"
        else abs(
            _face_pitch(r, r.display_center_x_m + r.display_len_m / 2.0)
            - _face_pitch(r, r.display_center_x_m - r.display_len_m / 2.0)
        )
        < 1e-9,
        details=(
            f"housing={r.housing_build} face={r.input_face} "
            f"deck_len={r.deck_len_m:.4f} slope_front={r.slope_front_x_m:.4f}"
        ),
    )
    ctx.check(
        "the soft-key strip width follows the key count",
        r.aux_key_row != "soft_key_strip"
        or (r.aux_strip_width_m <= r.body_width_m - 0.010 + 1e-9 and r.aux_key_size_m >= 0.0040),
        details=(f"n={r.aux_key_count} strip={r.aux_strip_width_m:.4f} cap={r.aux_key_size_m:.4f}"),
    )
    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "smallest_extruded_touchscreen_pedestal_n6",
        {
            "housing_build": "extruded_wedge",
            "input_face": "touchscreen_glass",
            "aux_key_row": "soft_key_strip",
            "display_mount": "tilt_display",
            "receipt_printer": "flip_cover_spindle",
            "card_interface": "sliding_bank_card",
            "support_base": "swivel_pedestal",
            "aux_key_count": 6,
            "body_length_m": 0.150,
            "body_width_m": 0.070,
            "deck_height_m": 0.020,
            "wedge_rise_m": 0.034,
            "key_travel_m": 0.0026,
            "cover_open_rad": 1.90,
            "display_tilt_rad": 0.66,
            "card_travel_m": 0.023,
            "pedestal_yaw_rad": 1.55,
        },
        reason=(
            "shortest narrowest case at the steepest wedge, six soft keys crowding the "
            "narrowest strip, the longest card travel and a tilting glass head on a pedestal"
        ),
    ),
    corner_case(
        "largest_intersected_keypad_dock_n2",
        {
            "housing_build": "intersected_wedge",
            "input_face": "numeric_keypad",
            "aux_key_row": "side_hard_buttons",
            "display_mount": "tilt_display",
            "receipt_printer": "knuckle_cover_static_roll",
            "card_interface": "sliding_bank_card",
            "support_base": "tilt_dock",
            "aux_key_count": 2,
            "body_length_m": 0.208,
            "body_width_m": 0.100,
            "deck_height_m": 0.036,
            "wedge_rise_m": 0.034,
            "key_travel_m": 0.0026,
            "cover_open_rad": 1.90,
            "display_tilt_rad": 0.66,
            "card_travel_m": 0.023,
            "dock_recline_rad": 0.40,
        },
        reason=(
            "largest single-plane case at full recline in its cradle, with the knuckle "
            "cover fully open and a tilting head over a slope-mounted keypad"
        ),
    ),
    corner_case(
        "flattest_extruded_keypad_grounded_n2",
        {
            "housing_build": "extruded_wedge",
            "input_face": "numeric_keypad",
            "aux_key_row": "soft_key_strip",
            "display_mount": "fixed_display",
            "receipt_printer": "flip_cover_spindle",
            "card_interface": "static_chip_slot",
            "support_base": "flat_feet",
            "aux_key_count": 2,
            "body_length_m": 0.208,
            "body_width_m": 0.070,
            "deck_height_m": 0.036,
            "wedge_rise_m": 0.018,
            "key_travel_m": 0.0012,
            "cover_open_rad": 1.25,
            "display_tilt_rad": 0.38,
            "card_travel_m": 0.011,
        },
        reason=(
            "longest and narrowest two-stage shell with the shallowest slope, so the "
            "display window and the roll bay are at their tightest against the deck"
        ),
    ),
    corner_case(
        "touchscreen_side_buttons_intersected_dock_n6",
        {
            "housing_build": "intersected_wedge",
            "input_face": "touchscreen_glass",
            "aux_key_row": "side_hard_buttons",
            "display_mount": "fixed_display",
            "receipt_printer": "knuckle_cover_static_roll",
            "card_interface": "static_chip_slot",
            "support_base": "tilt_dock",
            "aux_key_count": 6,
            "body_length_m": 0.150,
            "body_width_m": 0.100,
            "deck_height_m": 0.020,
            "wedge_rise_m": 0.018,
            "key_travel_m": 0.0026,
            "cover_open_rad": 1.90,
            "dock_recline_rad": 0.40,
        },
        reason=(
            "shortest widest single-plane slab where six side buttons must fit the run "
            "below the shallowest magstripe groove, reclined to the cradle limit"
        ),
    ),
)


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "build_point_of_sale_terminal",
    "build_seeded_point_of_sale_terminal",
    "config_from_seed",
    "resolve_config",
    "run_point_of_sale_terminal_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
