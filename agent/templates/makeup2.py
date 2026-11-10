# SPDX-License-Identifier: Apache-2.0

"""Source-backed hard-shell hinged makeup compacts / eyeshadow palettes.

Category identity (see ``source_maps/makeup2.md``): a moulded outer case whose rim land
carries a rear-hinged mirror lid opening to roughly 100 degrees, an N-well pressed
cosmetic pan grid held by one or more articulated carriers inside the case, and optional
front closure hardware.

Frame convention: +X is case width, +Y is the rear (hinge) side, -Y is the front
(thumb / latch side), +Z is up and the case bottom sits at z = 0.  Every joint uses
``q = 0`` for the fully closed / latched / seated pose.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
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
    mesh_from_cadquery,
    multiplicity_slot,
    register_interface_mate,
)

CaseForm = Literal["rounded_rect", "round", "clover"]
TrayTopology = Literal["single_tray", "double_stacked_carrier", "fan_out_carrier"]
Closure = Literal["hinge_only", "push_latch", "over_center_latch"]
WellProfile = Literal["round_pan", "rounded_rect_pan"]


TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("case_form", ("rounded_rect", "round", "clover")),
        component_slot(
            "tray_topology",
            ("single_tray", "double_stacked_carrier", "fan_out_carrier"),
        ),
        component_slot("closure", ("hinge_only", "push_latch", "over_center_latch")),
        component_slot("well_profile", ("round_pan", "rounded_rect_pan")),
        multiplicity_slot("well_count", (2, 4, 6, 8), item_slot="well_profile"),
    )
)

# --- fixed manufacturing constants (not structural degrees of freedom) -------

_CARRIER_SIDE_CLEAR_M = 0.0004
_CARRIER_REAR_GAP_M = 0.0004
_CARRIER_TOP_GAP_M = 0.0004
_LID_REAR_GAP_M = 0.0011
_SEAT_BITE_M = 0.00022
_AXIAL_BITE_M = 0.00016
_RIM_TOP_CLEAR_M = 0.0028
_FIELD_MARGIN_M = 0.0016
_MIN_TIER_GAP_M = 0.0009
_HUB_WALL_M = 0.0011
_BORE_CLEAR_M = 0.0003
_HINGE_WIDTH_TARGET = 0.55
_SEAT_PAD_H_M = 0.0007
_FORM_INSCRIBE = {"rounded_rect": 0.90, "round": 0.68, "clover": 0.72}

_PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "translucent_navy": {
        "shell": (0.055, 0.105, 0.290, 1.0),
        "accent": (0.130, 0.400, 0.760, 1.0),
        "hardware": (0.055, 0.085, 0.190, 1.0),
        "pan": (0.600, 0.655, 0.720, 1.0),
        "mirror": (0.790, 0.885, 0.955, 1.0),
    },
    "champagne_gold": {
        "shell": (0.760, 0.560, 0.245, 1.0),
        "accent": (0.930, 0.780, 0.430, 1.0),
        "hardware": (0.520, 0.350, 0.130, 1.0),
        "pan": (0.660, 0.640, 0.600, 1.0),
        "mirror": (0.760, 0.820, 0.845, 1.0),
    },
    "matte_charcoal": {
        "shell": (0.115, 0.115, 0.125, 1.0),
        "accent": (0.420, 0.430, 0.450, 1.0),
        "hardware": (0.230, 0.235, 0.245, 1.0),
        "pan": (0.480, 0.500, 0.530, 1.0),
        "mirror": (0.800, 0.860, 0.900, 1.0),
    },
    "rose_lacquer": {
        "shell": (0.680, 0.290, 0.330, 1.0),
        "accent": (0.905, 0.640, 0.640, 1.0),
        "hardware": (0.470, 0.180, 0.220, 1.0),
        "pan": (0.640, 0.605, 0.580, 1.0),
        "mirror": (0.820, 0.870, 0.905, 1.0),
    },
    "pearl_ivory": {
        "shell": (0.905, 0.880, 0.830, 1.0),
        "accent": (0.700, 0.660, 0.580, 1.0),
        "hardware": (0.560, 0.545, 0.510, 1.0),
        "pan": (0.560, 0.580, 0.610, 1.0),
        "mirror": (0.790, 0.855, 0.895, 1.0),
    },
    "emerald_enamel": {
        "shell": (0.055, 0.255, 0.190, 1.0),
        "accent": (0.760, 0.665, 0.330, 1.0),
        "hardware": (0.470, 0.400, 0.180, 1.0),
        "pan": (0.590, 0.620, 0.640, 1.0),
        "mirror": (0.800, 0.870, 0.900, 1.0),
    },
}
_PALETTE_NAMES = tuple(_PALETTES)

_POWDER_SHADES: tuple[tuple[str, tuple[float, float, float, float]], ...] = (
    ("warm_ivory_powder", (0.945, 0.870, 0.780, 1.0)),
    ("rose_beige_powder", (0.905, 0.720, 0.680, 1.0)),
    ("soft_peach_powder", (0.925, 0.780, 0.660, 1.0)),
    ("deep_bronze_powder", (0.700, 0.470, 0.360, 1.0)),
    ("soft_mauve_powder", (0.760, 0.560, 0.560, 1.0)),
    ("espresso_powder", (0.230, 0.150, 0.110, 1.0)),
    ("charcoal_powder", (0.130, 0.125, 0.125, 1.0)),
    ("champagne_shimmer_powder", (0.860, 0.760, 0.520, 1.0)),
)

_RANGES: dict[str, tuple[float, float]] = {
    "case_width_m": (0.070, 0.104),
    "case_depth_ratio": (0.82, 1.00),
    "case_height_m": (0.022, 0.034),
    "wall_thickness_m": (0.0018, 0.0034),
    "lid_open_rad": (1.66, 2.00),
    "clover_lobe_ratio": (0.28, 0.42),
    "well_diameter_ratio": (0.55, 0.86),
    "well_depth_m": (0.0016, 0.0030),
    "carrier_lift_rad": (0.80, 1.45),
    "tier_gap_ratio": (0.25, 0.40),
    "fan_angle_rad": (0.55, 1.20),
    "leaf_sector_ratio": (0.56, 0.82),
    "thumb_notch_ratio": (0.16, 0.34),
    "latch_travel_m": (0.0014, 0.0032),
    "toggle_lever_rad": (0.55, 1.10),
}

_DEFAULTS: dict[str, float] = {
    "case_width_m": 0.086,
    "case_depth_ratio": 0.88,
    "case_height_m": 0.027,
    "wall_thickness_m": 0.0025,
    "lid_open_rad": 1.80,
    "clover_lobe_ratio": 0.34,
    "well_diameter_ratio": 0.74,
    "well_depth_m": 0.0022,
    "carrier_lift_rad": 1.10,
    "tier_gap_ratio": 0.32,
    "fan_angle_rad": 0.90,
    "leaf_sector_ratio": 0.70,
    "thumb_notch_ratio": 0.24,
    "latch_travel_m": 0.0022,
    "toggle_lever_rad": 0.80,
}


@dataclass(frozen=True)
class Config:
    case_form: CaseForm = "rounded_rect"
    tray_topology: TrayTopology = "single_tray"
    closure: Closure = "hinge_only"
    well_profile: WellProfile = "round_pan"
    well_count: int = 4
    case_width_m: float | None = None
    case_depth_ratio: float | None = None
    case_height_m: float | None = None
    wall_thickness_m: float | None = None
    lid_open_rad: float | None = None
    clover_lobe_ratio: float | None = None
    well_diameter_ratio: float | None = None
    well_depth_m: float | None = None
    carrier_lift_rad: float | None = None
    tier_gap_ratio: float | None = None
    fan_angle_rad: float | None = None
    leaf_sector_ratio: float | None = None
    thumb_notch_ratio: float | None = None
    latch_travel_m: float | None = None
    toggle_lever_rad: float | None = None
    palette: str = "translucent_navy"
    name: str = "makeup2"


@dataclass(frozen=True)
class ResolvedConfig:
    case_form: CaseForm
    tray_topology: TrayTopology
    closure: Closure
    well_profile: WellProfile
    well_count: int
    case_width_m: float
    case_depth_ratio: float
    case_height_m: float
    wall_thickness_m: float
    lid_open_rad: float
    clover_lobe_ratio: float
    well_diameter_ratio: float
    well_depth_m: float
    carrier_lift_rad: float
    tier_gap_ratio: float
    fan_angle_rad: float
    leaf_sector_ratio: float
    thumb_notch_ratio: float
    latch_travel_m: float
    toggle_lever_rad: float
    case_depth_m: float
    corner_fillet_m: float
    rim_seat_width_m: float
    floor_thickness_m: float
    cavity_width_m: float
    cavity_depth_m: float
    ledge_width_m: float
    hinge_knuckle_radius_m: float
    hinge_barrel_radius_m: float
    hinge_knuckle_len_m: float
    hinge_knuckle_x_m: float
    hinge_axis_y_m: float
    hinge_axis_z_m: float
    lid_seat_dz_m: float
    lid_rim_width_m: float
    lid_pocket_depth_m: float
    lid_back_thickness_m: float
    lid_thickness_m: float
    mirror_thickness_m: float
    carrier_count: int
    carrier_thickness_m: float
    well_depth_eff_m: float
    carrier_free_h_m: float
    carrier_gap_m: float
    carrier_seat_z_m: tuple[float, ...]
    open_inset_m: tuple[float, ...]
    carrier_inset_m: tuple[float, ...]
    carrier_width_m: tuple[float, ...]
    carrier_depth_m: tuple[float, ...]
    carrier_hinge_y_m: tuple[float, ...]
    carrier_axis_z_m: tuple[float, ...]
    carrier_knuckle_radius_m: float
    carrier_barrel_radius_m: float
    carrier_knuckle_len_m: float
    carrier_knuckle_x_m: tuple[float, ...]
    carrier_outline_m: tuple[tuple[tuple[float, float], ...], ...]
    carrier_field_m: tuple[tuple[float, float, float], ...]
    turntable_radius_m: float
    leaf_radius_m: float
    leaf_half_angle_rad: float
    leaf_ring_radius_m: float
    boss_r0_m: float
    boss_r1_m: float
    boss_r2_m: float
    wells_per_carrier: tuple[int, ...]
    pan_radius_m: float
    pan_height_m: float
    recess_radius_m: float
    powder_height_m: float
    closure_actuator_count: int
    notch_width_m: float
    notch_depth_m: float
    notch_height_m: float
    latch_axis_z_m: float
    latch_housing_out_m: float
    latch_housing_w_m: float
    latch_housing_h_m: float
    latch_throat_w_m: float
    latch_throat_h_m: float
    latch_throat_len_m: float
    latch_flange_w_m: float
    latch_flange_h_m: float
    latch_flange_t_m: float
    latch_chamber_len_m: float
    toggle_axis_y_m: float
    toggle_axis_z_m: float
    toggle_hub_radius_m: float
    toggle_cheek_x_m: float
    toggle_cheek_len_m: float
    toggle_arm_len_m: float
    toggle_arm_thickness_m: float
    keeper_out_m: float
    keeper_drop_m: float
    palette: str
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x4D3B21)

    def pick(name: str) -> float:
        low, high = _RANGES[name]
        return round(rng.uniform(low, high), 5)

    return Config(
        case_form=choices["case_form"],
        tray_topology=choices["tray_topology"],
        closure=choices["closure"],
        well_profile=choices["well_profile"],
        well_count=int(choices["well_count"]),
        case_width_m=pick("case_width_m"),
        case_depth_ratio=pick("case_depth_ratio"),
        case_height_m=pick("case_height_m"),
        wall_thickness_m=pick("wall_thickness_m"),
        lid_open_rad=pick("lid_open_rad"),
        clover_lobe_ratio=pick("clover_lobe_ratio"),
        well_diameter_ratio=pick("well_diameter_ratio"),
        well_depth_m=pick("well_depth_m"),
        carrier_lift_rad=pick("carrier_lift_rad"),
        tier_gap_ratio=pick("tier_gap_ratio"),
        fan_angle_rad=pick("fan_angle_rad"),
        leaf_sector_ratio=pick("leaf_sector_ratio"),
        thumb_notch_ratio=pick("thumb_notch_ratio"),
        latch_travel_m=pick("latch_travel_m"),
        toggle_lever_rad=pick("toggle_lever_rad"),
        palette=_PALETTE_NAMES[rng.randrange(len(_PALETTE_NAMES))],
    )


def _clamp(value: float, low: float, high: float) -> float:
    return low if value < low else (high if value > high else value)


def _grid_shape(count: int) -> tuple[int, int]:
    table = {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 5: (3, 2), 6: (3, 2), 7: (4, 2)}
    return table.get(int(count), (4, 2))


def _split_wells(total: int, carriers: int) -> tuple[int, ...]:
    base = total // carriers
    extra = total - base * carriers
    return tuple(base + (1 if index < extra else 0) for index in range(carriers))


def _profile_half_width(
    form: str,
    width: float,
    depth: float,
    y: float,
    lobe_ratio: float,
) -> float:
    """Half X extent of a case/carrier profile at signed depth station ``y``."""

    half_w = 0.5 * max(width, 2e-4)
    half_d = 0.5 * max(depth, 2e-4)
    ay = abs(float(y))
    if ay >= half_d:
        return 0.0
    if form == "round":
        return half_w * math.sqrt(max(1.0 - (ay / half_d) ** 2, 0.0))
    if form == "clover":
        lobe_r = min(lobe_ratio * 2.0 * half_w, 0.96 * half_w, 0.96 * half_d)
        lobe_r = max(lobe_r, 0.52 * min(half_w, half_d))
        off_x = max(half_w - lobe_r, 3e-4)
        off_y = max(half_d - lobe_r, 3e-4)
        best = off_x if ay <= half_d else 0.0
        if ay <= off_y:
            best = max(best, half_w)
        for sign in (-1.0, 1.0):
            dy = ay - sign * off_y
            if abs(dy) < lobe_r:
                best = max(best, off_x + math.sqrt(lobe_r * lobe_r - dy * dy))
        return best
    fillet = min(0.155 * min(2.0 * half_w, 2.0 * half_d), 0.96 * min(half_w, half_d))
    flat = half_d - fillet
    if ay <= flat:
        return half_w
    dy = ay - flat
    return half_w - fillet + math.sqrt(max(fillet * fillet - dy * dy, 0.0))


def _hinge_station(
    form: str,
    width: float,
    depth: float,
    lobe_ratio: float,
    y_want: float,
    knuckle_len: float,
) -> tuple[float, float]:
    """Move a rear hinge line forward until the profile is wide enough to carry it."""

    target = _HINGE_WIDTH_TARGET * 0.5 * width
    y = min(y_want, 0.5 * depth - 1e-4)
    for step in range(41):
        candidate = y * (1.0 - step / 40.0)
        half = _profile_half_width(form, width, depth, candidate, lobe_ratio)
        if half >= target:
            knuckle_x = max(half - 0.5 * knuckle_len - 0.0004, 0.62 * knuckle_len)
            return candidate, knuckle_x
    half = _profile_half_width(form, width, depth, 0.0, lobe_ratio)
    return 0.0, max(half - 0.5 * knuckle_len - 0.0004, 0.62 * knuckle_len)


def _carrier_outline_rows(
    form: str,
    *,
    case_width: float,
    case_depth: float,
    open_inset: float,
    carrier_width: float,
    carrier_depth: float,
    hinge_y: float,
    rear_gap: float,
    reach: float,
    lift: float,
    lobe_ratio: float,
    clear: float = 0.0006,
    samples: int = 30,
) -> tuple[tuple[float, float], ...]:
    """Half width of a swing-up carrier at every depth station behind its hinge.

    A plate hinged at the rear moves *backwards* as it lifts (its station at depth ``s``
    lands at ``hinge_y - s*cos(q)``), so the case opening it has to pass through is the
    opening measured at the fully raised angle.  Clipping the plate outline against that
    opening is the host adaptation that lets a rounded, round or clover case swing the
    same tray without a single overlap allowance.
    """

    cos_lift = math.cos(_clamp(lift, 0.0, 0.5 * math.pi))
    open_w = max(case_width - 2.0 * open_inset, 0.010)
    open_d = max(case_depth - 2.0 * open_inset, 0.010)
    own_limit = 0.5 * carrier_depth - 1e-6
    rows: list[tuple[float, float]] = []
    for step in range(samples + 1):
        s = rear_gap + (reach - rear_gap) * step / samples
        own_y = _clamp(hinge_y - s, -own_limit, own_limit)
        own = _profile_half_width(form, carrier_width, carrier_depth, own_y, lobe_ratio)
        swept = _profile_half_width(form, open_w, open_d, hinge_y - s * cos_lift, lobe_ratio)
        rows.append((s, max(min(own, swept - clear), 0.0007)))
    return tuple(rows)


def _carrier_field_from_outline(
    rows: tuple[tuple[float, float], ...], hinge_y: float, margin: float
) -> tuple[float, float, float]:
    """Largest well field the clipped carrier outline can host: (center_y, half_w, half_d)."""

    max_h = max(h for _, h in rows)
    best: tuple[float, float, float, float] | None = None
    for fraction in (0.96, 0.92, 0.88, 0.82, 0.74, 0.66, 0.58):
        threshold = fraction * max_h
        run: list[float] = []
        longest: list[float] = []
        for s, h in rows:
            if h >= threshold:
                run.append(s)
                if len(run) > len(longest):
                    longest = list(run)
            else:
                run = []
        if len(longest) < 2:
            continue
        half_w = threshold - margin
        half_d = 0.5 * (longest[-1] - longest[0]) - margin
        if half_w <= 0.0026 or half_d <= 0.0026:
            continue
        area = half_w * half_d
        if best is None or area > best[0]:
            best = (area, hinge_y - 0.5 * (longest[0] + longest[-1]), half_w, half_d)
    if best is None:
        return (hinge_y - 0.5 * (rows[0][0] + rows[-1][0]), 0.0026, 0.0026)
    return (best[1], best[2], best[3])


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    config = Config() if config is None else config
    TEMPLATE_DOMAIN.validate(
        {
            "case_form": config.case_form,
            "tray_topology": config.tray_topology,
            "closure": config.closure,
            "well_profile": config.well_profile,
            "well_count": int(config.well_count),
        }
    )
    values: dict[str, float] = {}
    for name, fallback in _DEFAULTS.items():
        raw = getattr(config, name)
        value = float(fallback if raw is None else raw)
        low, high = _RANGES[name]
        if not low - 1e-9 <= value <= high + 1e-9:
            raise ValueError(f"{name} must be in [{low}, {high}], got {value}")
        values[name] = value
    if config.palette not in _PALETTES:
        raise ValueError(f"palette must be one of {sorted(_PALETTES)}, got {config.palette!r}")

    form = config.case_form
    lobe = values["clover_lobe_ratio"]
    width = values["case_width_m"]
    depth = width * values["case_depth_ratio"]
    height = values["case_height_m"]
    wall = values["wall_thickness_m"]

    corner_fillet = 0.155 * min(width, depth)
    rim_seat = wall + 0.0022
    floor_t = 0.0022 + 0.35 * wall
    cavity_w = width - 2.0 * rim_seat
    cavity_d = depth - 2.0 * rim_seat

    # ---- lid hinge ------------------------------------------------------
    knuckle_r = _clamp(0.105 * height, 0.0021, 0.0032)
    barrel_r = knuckle_r - 0.00035
    knuckle_len = _clamp(0.115 * width, 0.0068, 0.0135)
    hinge_y, knuckle_x = _hinge_station(
        form, width, depth, lobe, depth / 2.0 - rim_seat + knuckle_r, knuckle_len
    )
    hinge_z = height + 0.35 * knuckle_r
    lid_seat_dz = height - hinge_z
    lid_rim_w = rim_seat - 0.0008
    lid_pocket_depth = _clamp(0.105 * height, 0.0020, 0.0036)
    lid_back_t = _clamp(0.095 * height, 0.0018, 0.0032)
    lid_thickness = lid_pocket_depth + lid_back_t

    # ---- carrier stack budget ------------------------------------------
    fan_out = config.tray_topology == "fan_out_carrier"
    carrier_count = 1 if config.tray_topology == "single_tray" else 2
    avail = height - floor_t - _RIM_TOP_CLEAR_M
    want_t = values["well_depth_m"] + 0.0012
    if carrier_count == 1:
        max_t = avail - 2.0 * _MIN_TIER_GAP_M
    elif fan_out:
        max_t = (avail - 3.0 * _MIN_TIER_GAP_M) / 2.0
    else:
        max_t = (avail - 3.0 * 0.00055) / 3.26
    carrier_t = max(0.0018, min(want_t, max_t))
    well_depth_eff = max(carrier_t - 0.0012, 0.0006)
    free_h = max(avail - carrier_count * carrier_t, (carrier_count + 1) * _MIN_TIER_GAP_M)
    carrier_knuckle_r = _clamp(0.42 * carrier_t, 0.0011, 0.0021)
    carrier_barrel_r = carrier_knuckle_r - 0.00025
    lift_gap_min = _CARRIER_TOP_GAP_M + carrier_barrel_r + 0.0004

    if carrier_count == 1:
        gap = max(0.5 * free_h, _MIN_TIER_GAP_M)
        seat_z = (floor_t + gap,)
    elif fan_out:
        gap = max(free_h / 3.0, _MIN_TIER_GAP_M)
        seat_z = (floor_t + gap, floor_t + gap + carrier_t + gap)
    else:
        gap = max(free_h * values["tier_gap_ratio"], lift_gap_min)
        top = free_h - 2.0 * gap
        if top < _MIN_TIER_GAP_M:
            gap = max((free_h - _MIN_TIER_GAP_M) / 2.0, lift_gap_min)
        seat_z = (floor_t + gap, floor_t + gap + carrier_t + gap)

    ledge_w = carrier_t + 0.0016 if not fan_out else 0.0
    if fan_out:
        open_inset = tuple(rim_seat for _ in range(carrier_count))
    else:
        open_inset = tuple(
            rim_seat + ledge_w * (carrier_count - 1 - index) for index in range(carrier_count)
        )
    carrier_inset = tuple(item + _CARRIER_SIDE_CLEAR_M for item in open_inset)
    carrier_w = tuple(max(width - 2.0 * item, 0.014) for item in carrier_inset)
    carrier_d = tuple(max(depth - 2.0 * item, 0.012) for item in carrier_inset)
    carrier_knuckle_len = _clamp(0.10 * width, 0.0055, 0.0105)

    # The carrier hinge hardware must stay clear of the lid hinge hardware in X and Y,
    # so both hinge lines can share the same rear region without a swept collision.
    carrier_x_limit = knuckle_x - 0.5 * knuckle_len + 0.5 * carrier_knuckle_len - 0.0006
    carrier_y_limit = hinge_y - knuckle_r - 0.0008
    hinge_ys: list[float] = []
    knuckle_xs: list[float] = []
    for index in range(carrier_count):
        want_y = min(depth / 2.0 - open_inset[index] - 0.0008, carrier_y_limit)
        station_y, station_x = _hinge_station(
            form, carrier_w[index], carrier_d[index], lobe, want_y, carrier_knuckle_len
        )
        hinge_ys.append(station_y)
        knuckle_xs.append(
            max(min(station_x, carrier_x_limit), 0.5 * (carrier_knuckle_len + 0.0016))
        )
    carrier_axis_z = tuple(
        seat_z[index] + carrier_t + _CARRIER_TOP_GAP_M for index in range(carrier_count)
    )
    carrier_outline: list[tuple[tuple[float, float], ...]] = []
    carrier_field: list[tuple[float, float, float]] = []
    if not fan_out:
        for index in range(carrier_count):
            reach = depth / 2.0 - carrier_inset[index] + hinge_ys[index]
            rows_out = _carrier_outline_rows(
                form,
                case_width=width,
                case_depth=depth,
                open_inset=open_inset[index],
                carrier_width=carrier_w[index],
                carrier_depth=carrier_d[index],
                hinge_y=hinge_ys[index],
                rear_gap=_CARRIER_REAR_GAP_M,
                reach=max(reach, 0.010),
                lift=values["carrier_lift_rad"],
                lobe_ratio=lobe,
            )
            carrier_outline.append(rows_out)
            carrier_field.append(
                _carrier_field_from_outline(rows_out, hinge_ys[index], _FIELD_MARGIN_M)
            )

    # ---- fan-out turntable ---------------------------------------------
    turntable_r = max(0.5 * min(cavity_w, cavity_d), 0.010)
    boss_r0 = _clamp(0.048 * width, 0.0032, 0.0050)
    boss_r1 = boss_r0 - 0.0011
    boss_r2 = boss_r1 - 0.0010
    leaf_r = min(
        max((turntable_r - 0.0008) * values["leaf_sector_ratio"], boss_r0 + 0.0060),
        turntable_r - 0.0008,
    )
    leaf_half_angle = 1.42
    hub_edge = boss_r0 + _HUB_WALL_M
    leaf_ring_r = _clamp(
        hub_edge + 0.42 * (leaf_r - hub_edge),
        hub_edge + 0.0016,
        max(leaf_r - 0.0016, hub_edge + 0.0018),
    )

    # ---- wells ----------------------------------------------------------
    wells_per_carrier = _split_wells(int(config.well_count), carrier_count)
    ratio_well = values["well_diameter_ratio"]
    pan_candidates: list[float] = []
    if fan_out:
        for count in wells_per_carrier:
            span = 2.0 * (leaf_half_angle - 0.22)
            if count > 1:
                tangential = 2.0 * leaf_ring_r * math.sin(0.5 * span / float(count - 1))
            else:
                tangential = 2.0 * (leaf_r - leaf_ring_r)
            radial = 1.7 * min(leaf_ring_r - hub_edge, leaf_r - leaf_ring_r)
            pan_candidates.append(0.5 * ratio_well * max(min(tangential, radial), 0.0026))
    else:
        for index, count in enumerate(wells_per_carrier):
            cols, rows = _grid_shape(count)
            _, half_w, half_d = carrier_field[index]
            pan_candidates.append(
                0.5 * ratio_well * max(min(2.0 * half_w / cols, 2.0 * half_d / rows), 0.0026)
            )
    pan_r = max(min(pan_candidates), 0.0014)
    pan_h = max(0.28 * well_depth_eff, 0.00018)
    recess_r = pan_r + 0.0004
    powder_h = max(well_depth_eff - pan_h - 0.00025, 0.00025)

    # ---- closure --------------------------------------------------------
    actuator_count = 0 if config.closure == "hinge_only" else 1
    notch_w = values["thumb_notch_ratio"] * width
    notch_depth = rim_seat + 0.0006
    notch_height = _clamp(0.13 * height, 0.0018, 0.0038)

    latch_housing_h = _clamp(0.30 * height, 0.0050, 0.0100)
    latch_axis_z = height - _RIM_TOP_CLEAR_M - 0.5 * latch_housing_h
    latch_housing_w = _clamp(0.20 * width, 0.0130, 0.0220)
    latch_throat_w = latch_housing_w - 0.0060
    latch_throat_h = latch_housing_h - 0.0034
    latch_flange_w = latch_throat_w + 0.0024
    latch_flange_h = latch_throat_h + 0.0018
    latch_flange_t = 0.0010
    latch_throat_len = 0.0011
    latch_chamber_len = latch_flange_t + values["latch_travel_m"] + 0.0007
    latch_housing_out = max(
        _clamp(0.055 * depth, 0.0034, 0.0060), latch_throat_len + latch_chamber_len + 0.0008
    )

    toggle_arm_t = _clamp(0.030 * width, 0.0024, 0.0038)
    toggle_hub_r = _clamp(0.020 * width, 0.0016, 0.0026)
    toggle_axis_y = -(depth / 2.0 + 0.5 * toggle_arm_t + 0.0005)
    toggle_axis_z = _clamp(0.42 * height, 0.0070, 0.0150)
    toggle_cheek_len = 0.0022
    toggle_cheek_x = _clamp(0.075 * width, 0.0052, 0.0092)
    keeper_drop = 0.0016
    toggle_arm_len = max((height + lid_seat_dz + 0.0006) - toggle_axis_z + keeper_drop, 0.0060)
    keeper_out = toggle_arm_t + 0.0018

    return ResolvedConfig(
        case_form=form,
        tray_topology=config.tray_topology,
        closure=config.closure,
        well_profile=config.well_profile,
        well_count=int(config.well_count),
        case_width_m=width,
        case_depth_ratio=values["case_depth_ratio"],
        case_height_m=height,
        wall_thickness_m=wall,
        lid_open_rad=values["lid_open_rad"],
        clover_lobe_ratio=lobe,
        well_diameter_ratio=ratio_well,
        well_depth_m=values["well_depth_m"],
        carrier_lift_rad=values["carrier_lift_rad"],
        tier_gap_ratio=values["tier_gap_ratio"],
        fan_angle_rad=values["fan_angle_rad"],
        leaf_sector_ratio=values["leaf_sector_ratio"],
        thumb_notch_ratio=values["thumb_notch_ratio"],
        latch_travel_m=values["latch_travel_m"],
        toggle_lever_rad=values["toggle_lever_rad"],
        case_depth_m=depth,
        corner_fillet_m=corner_fillet,
        rim_seat_width_m=rim_seat,
        floor_thickness_m=floor_t,
        cavity_width_m=cavity_w,
        cavity_depth_m=cavity_d,
        ledge_width_m=ledge_w,
        hinge_knuckle_radius_m=knuckle_r,
        hinge_barrel_radius_m=barrel_r,
        hinge_knuckle_len_m=knuckle_len,
        hinge_knuckle_x_m=knuckle_x,
        hinge_axis_y_m=hinge_y,
        hinge_axis_z_m=hinge_z,
        lid_seat_dz_m=lid_seat_dz,
        lid_rim_width_m=lid_rim_w,
        lid_pocket_depth_m=lid_pocket_depth,
        lid_back_thickness_m=lid_back_t,
        lid_thickness_m=lid_thickness,
        mirror_thickness_m=0.0008,
        carrier_count=carrier_count,
        carrier_thickness_m=carrier_t,
        well_depth_eff_m=well_depth_eff,
        carrier_free_h_m=free_h,
        carrier_gap_m=gap,
        carrier_seat_z_m=seat_z,
        open_inset_m=open_inset,
        carrier_inset_m=carrier_inset,
        carrier_width_m=carrier_w,
        carrier_depth_m=carrier_d,
        carrier_hinge_y_m=tuple(hinge_ys),
        carrier_axis_z_m=carrier_axis_z,
        carrier_knuckle_radius_m=carrier_knuckle_r,
        carrier_barrel_radius_m=carrier_barrel_r,
        carrier_knuckle_len_m=carrier_knuckle_len,
        carrier_knuckle_x_m=tuple(knuckle_xs),
        carrier_outline_m=tuple(carrier_outline),
        carrier_field_m=tuple(carrier_field),
        turntable_radius_m=turntable_r,
        leaf_radius_m=leaf_r,
        leaf_half_angle_rad=leaf_half_angle,
        leaf_ring_radius_m=leaf_ring_r,
        boss_r0_m=boss_r0,
        boss_r1_m=boss_r1,
        boss_r2_m=boss_r2,
        wells_per_carrier=wells_per_carrier,
        pan_radius_m=pan_r,
        pan_height_m=pan_h,
        recess_radius_m=recess_r,
        powder_height_m=powder_h,
        closure_actuator_count=actuator_count,
        notch_width_m=notch_w,
        notch_depth_m=notch_depth,
        notch_height_m=notch_height,
        latch_axis_z_m=latch_axis_z,
        latch_housing_out_m=latch_housing_out,
        latch_housing_w_m=latch_housing_w,
        latch_housing_h_m=latch_housing_h,
        latch_throat_w_m=latch_throat_w,
        latch_throat_h_m=latch_throat_h,
        latch_throat_len_m=latch_throat_len,
        latch_flange_w_m=latch_flange_w,
        latch_flange_h_m=latch_flange_h,
        latch_flange_t_m=latch_flange_t,
        latch_chamber_len_m=latch_chamber_len,
        toggle_axis_y_m=toggle_axis_y,
        toggle_axis_z_m=toggle_axis_z,
        toggle_hub_radius_m=toggle_hub_r,
        toggle_cheek_x_m=toggle_cheek_x,
        toggle_cheek_len_m=toggle_cheek_len,
        toggle_arm_len_m=toggle_arm_len,
        toggle_arm_thickness_m=toggle_arm_t,
        keeper_out_m=keeper_out,
        keeper_drop_m=keeper_drop,
        palette=config.palette,
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def _profile_solid(
    form: str,
    width: float,
    depth: float,
    height: float,
    *,
    lobe_ratio: float,
) -> cq.Workplane:
    """One extruded case / lid / carrier profile centred on XY, z in [0, height]."""

    w = max(float(width), 2e-4)
    d = max(float(depth), 2e-4)
    h = max(float(height), 5e-5)
    if form == "round":
        return cq.Workplane("XY").ellipse(w / 2.0, d / 2.0).extrude(h)
    if form == "clover":
        lobe_r = min(lobe_ratio * w, 0.48 * w, 0.48 * d)
        lobe_r = max(lobe_r, 0.26 * min(w, d))
        off_x = max(w / 2.0 - lobe_r, 3e-4)
        off_y = max(d / 2.0 - lobe_r, 3e-4)
        # The four lobes alone define the silhouette; the filling cross is held a hair
        # inside them so no boolean ever has to resolve a tangent face pair.
        waist = min(0.0006, 0.05 * min(w, d))
        shape = cq.Workplane("XY").rect(2.0 * off_x, d - waist).extrude(h)
        shape = shape.union(cq.Workplane("XY").rect(w - waist, 2.0 * off_y).extrude(h))
        for sign_x in (-1.0, 1.0):
            for sign_y in (-1.0, 1.0):
                shape = shape.union(
                    cq.Workplane("XY")
                    .center(sign_x * off_x, sign_y * off_y)
                    .circle(lobe_r)
                    .extrude(h)
                )
        return shape.clean()
    fillet = min(0.155 * min(w, d), 0.48 * min(w, d))
    return cq.Workplane("XY").rect(w, d).extrude(h).edges("|Z").fillet(fillet)


def _x_cylinder(length: float, radius: float) -> cq.Workplane:
    return cq.Workplane("YZ").circle(max(radius, 2e-5)).extrude(max(length, 1e-4) / 2.0, both=True)


def _z_cylinder(height: float, radius: float) -> cq.Workplane:
    return cq.Workplane("XY").circle(max(radius, 2e-5)).extrude(max(height, 1e-4))


def _rounded_box(width: float, depth: float, height: float, radius: float) -> cq.Workplane:
    w = max(width, 2e-4)
    d = max(depth, 2e-4)
    h = max(height, 5e-5)
    solid = cq.Workplane("XY").box(w, d, h)
    r = min(max(radius, 0.0), 0.45 * min(w, d))
    if r > 2e-5:
        solid = solid.edges("|Z").fillet(r)
    return solid


def _trim_block(size: float, y_start: float) -> cq.Workplane:
    """A half-space cutter removing every point with local y greater than y_start."""

    return cq.Workplane("XY").box(size, size, size).translate((0.0, size / 2.0 + y_start, 0.0))


def _hinged_plate(
    form: str,
    *,
    width: float,
    depth: float,
    thickness: float,
    hinge_world_y: float,
    rear_gap: float,
    top_local_z: float,
    lobe_ratio: float,
) -> cq.Workplane:
    """A plate centred on the case in world Y, expressed in its own hinge-local frame.

    The plate is trimmed just in front of its rotation axis and hangs entirely below it,
    so no plate point ever crosses the hinge plane while the leaf swings up.
    """

    solid = _profile_solid(form, width, depth, thickness, lobe_ratio=lobe_ratio).translate(
        (0.0, -hinge_world_y, top_local_z - thickness)
    )
    block = max(width, depth) * 3.0
    return solid.cut(_trim_block(block, -rear_gap))


def _well_profile_round_pan_build(radius: float, height: float) -> cq.Workplane:
    """Circular cosmetic well body (pan, powder or recess cutter)."""

    return _z_cylinder(height, radius)


def _well_profile_rounded_rect_pan_build(radius: float, height: float) -> cq.Workplane:
    """Filleted rounded-rectangular cosmetic well body."""

    return _rounded_box(2.0 * radius, 1.64 * radius, height, 0.34 * radius).translate(
        (0.0, 0.0, height / 2.0)
    )


_WELL_BUILDERS = {
    "round_pan": _well_profile_round_pan_build,
    "rounded_rect_pan": _well_profile_rounded_rect_pan_build,
}


def _well_cutter(profile: str, radius: float, height: float) -> cq.Workplane:
    return _WELL_BUILDERS[profile](radius, height)


def _powder_solid(profile: str, radius: float, height: float) -> cq.Workplane:
    body = _well_cutter(profile, radius, height)
    top = _well_cutter(profile, max(radius - 0.0004, 0.0004), 0.00025).translate((0.0, 0.0, height))
    return body.union(top)


# ---------------------------------------------------------------------------
# Case shell
# ---------------------------------------------------------------------------


def _cavity_cutter(r: ResolvedConfig) -> cq.Workplane:
    """The real inner cavity: stepped carrier ledges, or a circular turntable well."""

    top_z = r.case_height_m + 0.004
    if r.tray_topology == "fan_out_carrier":
        return _z_cylinder(top_z - r.floor_thickness_m, r.turntable_radius_m).translate(
            (0.0, 0.0, r.floor_thickness_m)
        )
    stages: list[tuple[float, float, float]] = [
        (
            r.floor_thickness_m,
            r.carrier_seat_z_m[0] - _SEAT_PAD_H_M + 0.0002,
            r.open_inset_m[0] + r.ledge_width_m,
        )
    ]
    for index in range(r.carrier_count):
        z_low = r.carrier_seat_z_m[index] - _SEAT_PAD_H_M + 0.0002
        z_high = (
            r.carrier_seat_z_m[index + 1] - _SEAT_PAD_H_M + 0.0002
            if index + 1 < r.carrier_count
            else top_z
        )
        stages.append((z_low, z_high, r.open_inset_m[index]))
    cutter: cq.Workplane | None = None
    for z_low, z_high, inset in stages:
        piece = _profile_solid(
            r.case_form,
            r.case_width_m - 2.0 * inset,
            r.case_depth_m - 2.0 * inset,
            max(z_high - z_low, 2e-4),
            lobe_ratio=r.clover_lobe_ratio,
        ).translate((0.0, 0.0, z_low))
        cutter = piece if cutter is None else cutter.union(piece)
    assert cutter is not None
    return cutter


def _case_shell_solid(r: ResolvedConfig) -> cq.Workplane:
    shell = _profile_solid(
        r.case_form,
        r.case_width_m,
        r.case_depth_m,
        r.case_height_m,
        lobe_ratio=r.clover_lobe_ratio,
    ).cut(_cavity_cutter(r))

    # Real coaxial barrel reliefs so no moving barrel is buried in the rear rim.
    shell = shell.cut(
        _x_cylinder(
            2.0 * r.hinge_knuckle_x_m - r.hinge_knuckle_len_m + 0.0016,
            r.hinge_barrel_radius_m + 0.0004,
        ).translate((0.0, r.hinge_axis_y_m, r.hinge_axis_z_m))
    )
    if r.tray_topology != "fan_out_carrier":
        for index in range(r.carrier_count):
            shell = shell.cut(
                _x_cylinder(
                    2.0 * r.carrier_knuckle_x_m[index] - r.carrier_knuckle_len_m + 0.0014,
                    r.carrier_barrel_radius_m + 0.00035,
                ).translate((0.0, r.carrier_hinge_y_m[index], r.carrier_axis_z_m[index]))
            )
    # Front thumb relief (present for every closure candidate).
    shell = shell.cut(
        cq.Workplane("XY")
        .box(r.notch_width_m, 2.0 * r.notch_depth_m, 2.0 * r.notch_height_m)
        .translate((0.0, -r.case_depth_m / 2.0, r.case_height_m))
    )
    if r.closure == "over_center_latch":
        # A real keeper window gives the toggle hook a path onto the lid lug.
        shell = shell.cut(
            _rounded_box(
                2.0 * r.toggle_cheek_x_m - r.toggle_cheek_len_m - 0.0016,
                2.0 * (r.rim_seat_width_m + 0.0010),
                2.0 * r.notch_height_m,
                0.0004,
            ).translate((0.0, -r.case_depth_m / 2.0, r.case_height_m))
        )
    return shell


def _rim_accent_solid(r: ResolvedConfig) -> cq.Workplane:
    band = max(0.45 * r.rim_seat_width_m, 0.0007)
    thickness = 0.00075
    outer = _profile_solid(
        r.case_form,
        r.case_width_m - 0.0010,
        r.case_depth_m - 0.0010,
        thickness,
        lobe_ratio=r.clover_lobe_ratio,
    )
    inner = _profile_solid(
        r.case_form,
        r.case_width_m - 0.0010 - 2.0 * band,
        r.case_depth_m - 0.0010 - 2.0 * band,
        3.0 * thickness,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, 0.0, -thickness))
    ring = outer.cut(inner).translate((0.0, 0.0, r.case_height_m - thickness))
    return ring.cut(
        cq.Workplane("XY")
        .box(r.notch_width_m, 2.0 * r.notch_depth_m, 4.0 * thickness)
        .translate((0.0, -r.case_depth_m / 2.0, r.case_height_m))
    )


def _seat_pad_solid(r: ResolvedConfig, index: int) -> cq.Workplane:
    inset = r.open_inset_m[index]
    outer = _profile_solid(
        r.case_form,
        r.case_width_m - 2.0 * inset,
        r.case_depth_m - 2.0 * inset,
        _SEAT_PAD_H_M,
        lobe_ratio=r.clover_lobe_ratio,
    )
    inner = _profile_solid(
        r.case_form,
        r.case_width_m - 2.0 * (inset + r.ledge_width_m),
        r.case_depth_m - 2.0 * (inset + r.ledge_width_m),
        3.0 * _SEAT_PAD_H_M,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, 0.0, -_SEAT_PAD_H_M))
    return outer.cut(inner).translate(
        (0.0, 0.0, r.carrier_seat_z_m[index] - _SEAT_PAD_H_M + 0.0002)
    )


def _build_case_common(
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> None:
    form = r.case_form
    case.visual(
        mesh_from_cadquery(_case_shell_solid(r), f"case_{form}_shell", tolerance=0.00028),
        material=mats["shell"],
        name=f"case_form__{form}__shell", material_class_id="plastic.opaque_glossy_molded",
    )
    case.visual(
        mesh_from_cadquery(_rim_accent_solid(r), f"case_{form}_rim_accent", tolerance=0.00024),
        material=mats["accent"],
        name=f"case_form__{form}__rim_accent", material_class_id="plastic.opaque_glossy_molded",
    )
    knuckle_mesh = mesh_from_cadquery(
        _x_cylinder(r.hinge_knuckle_len_m, r.hinge_knuckle_radius_m),
        f"case_{form}_lid_knuckle",
        tolerance=0.00018,
    )
    for index, sign in enumerate((-1.0, 1.0)):
        case.visual(
            knuckle_mesh,
            origin=Origin(xyz=(sign * r.hinge_knuckle_x_m, r.hinge_axis_y_m, r.hinge_axis_z_m)),
            material=mats["hardware"],
            name=f"case_form__{form}__lid_knuckle_{index}", material_class_id="metal.stainless_matte",
        )


def _case_form_rounded_rect_build(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    _build_case_common(case, r, mats)


def _case_form_round_build(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    _build_case_common(case, r, mats)


def _case_form_clover_build(case: object, r: ResolvedConfig, mats: dict[str, object]) -> None:
    _build_case_common(case, r, mats)


_CASE_BUILDERS = {
    "rounded_rect": _case_form_rounded_rect_build,
    "round": _case_form_round_build,
    "clover": _case_form_clover_build,
}


# ---------------------------------------------------------------------------
# Mirror lid (shared category anchor)
# ---------------------------------------------------------------------------


def _lid_shell_solid(r: ResolvedConfig) -> cq.Workplane:
    seat = r.lid_seat_dz_m - _SEAT_BITE_M
    solid = _hinged_plate(
        r.case_form,
        width=r.case_width_m,
        depth=r.case_depth_m,
        thickness=r.lid_thickness_m + _SEAT_BITE_M,
        hinge_world_y=r.hinge_axis_y_m,
        rear_gap=_LID_REAR_GAP_M,
        top_local_z=seat + r.lid_thickness_m + _SEAT_BITE_M,
        lobe_ratio=r.clover_lobe_ratio,
    )
    pocket = _profile_solid(
        r.case_form,
        r.case_width_m - 2.0 * r.lid_rim_width_m,
        r.case_depth_m - 2.0 * r.lid_rim_width_m,
        r.lid_pocket_depth_m + 0.0012,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, -r.hinge_axis_y_m, seat - 0.0012))
    solid = solid.cut(pocket)
    # Real hinge-knuckle reliefs, exactly as the source lid frames cut them.
    for sign in (-1.0, 1.0):
        solid = solid.cut(
            _x_cylinder(
                r.hinge_knuckle_len_m + 0.0010,
                r.hinge_knuckle_radius_m + 0.00045,
            ).translate((sign * r.hinge_knuckle_x_m, 0.0, 0.0))
        )
    # No bridging neck is needed: the barrel radius exceeds the rear trim gap, so the
    # barrel already intersects the trimmed rim ring.  A wider neck would sweep outside
    # the coaxial shell relief and clip the rear rim land while opening.
    return solid.clean()


def _lid_accent_solid(r: ResolvedConfig) -> cq.Workplane:
    band = max(0.55 * r.lid_rim_width_m, 0.0008)
    thickness = 0.0007
    top_z = r.lid_seat_dz_m + r.lid_thickness_m
    outer = _profile_solid(
        r.case_form,
        r.case_width_m - 0.0014,
        r.case_depth_m - 0.0014,
        thickness,
        lobe_ratio=r.clover_lobe_ratio,
    )
    inner = _profile_solid(
        r.case_form,
        r.case_width_m - 0.0014 - 2.0 * band,
        r.case_depth_m - 0.0014 - 2.0 * band,
        3.0 * thickness,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, 0.0, -thickness))
    ring = outer.cut(inner).translate((0.0, -r.hinge_axis_y_m, top_z - 0.35 * thickness))
    block = max(r.case_width_m, r.case_depth_m) * 3.0
    return ring.cut(_trim_block(block, -_LID_REAR_GAP_M))


def _mirror_planes(r: ResolvedConfig) -> tuple[PlaneInterface, PlaneInterface]:
    factor = _FORM_INSCRIBE[r.case_form]
    pocket_w = (r.case_width_m - 2.0 * r.lid_rim_width_m) * factor
    pocket_d = (r.case_depth_m - 2.0 * r.lid_rim_width_m) * factor
    mirror_w = pocket_w - 0.0018
    mirror_d = pocket_d - 0.0018
    provider = PlaneInterface(
        name="mirror_lid.mirror_pocket",
        point=(0.0, -r.hinge_axis_y_m, r.lid_seat_dz_m + r.lid_pocket_depth_m),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(pocket_w, pocket_d),
    )
    consumer = PlaneInterface(
        name="mirror_lid.mirror_back",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(mirror_w, mirror_d),
    )
    return provider, consumer


def _build_mirror_lid(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object:
    lid = model.part(
        "mirror_lid",
        meta={
            "role": "mirror_lid",
            "rear_hinged_mirror_lid": True,
            "seats_on_rim_land": True,
            "open_rad": r.lid_open_rad,
        },
    )
    lid.visual(
        mesh_from_cadquery(_lid_shell_solid(r), "lid_frame", tolerance=0.00026),
        material=mats["shell"],
        name="lid_frame", material_class_id="plastic.opaque_glossy_molded",
    )
    lid.visual(
        mesh_from_cadquery(
            _x_cylinder(
                2.0 * r.hinge_knuckle_x_m - r.hinge_knuckle_len_m + 2.0 * _AXIAL_BITE_M,
                r.hinge_barrel_radius_m,
            ),
            "lid_barrel",
            tolerance=0.00018,
        ),
        material=mats["hardware"],
        name="lid_barrel", material_class_id="metal.stainless_matte",
    )
    provider, consumer = _mirror_planes(r)
    mate = mate_planes(provider, consumer, margin=0.0002)
    mirror_w, mirror_d = consumer.extent or (0.02, 0.02)
    mirror = _profile_solid(
        r.case_form,
        mirror_w,
        mirror_d,
        r.mirror_thickness_m,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, 0.0, -r.mirror_thickness_m))
    lid.visual(
        mesh_from_cadquery(mirror, "mirror_plate", tolerance=0.00020),
        origin=mate.origin,
        material=mats["mirror"],
        name="mirror", material_class_id="glass.mirror",
    )
    bezel_outer = _profile_solid(
        r.case_form,
        mirror_w + 0.0016,
        mirror_d + 0.0016,
        0.00055,
        lobe_ratio=r.clover_lobe_ratio,
    )
    bezel_inner = _profile_solid(
        r.case_form,
        mirror_w,
        mirror_d,
        0.0024,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, 0.0, -0.0009))
    bezel = bezel_outer.cut(bezel_inner).translate(
        (
            0.0,
            -r.hinge_axis_y_m,
            r.lid_seat_dz_m + r.lid_pocket_depth_m - r.mirror_thickness_m - 0.00055,
        )
    )
    lid.visual(
        mesh_from_cadquery(bezel, "mirror_bezel", tolerance=0.00020),
        material=mats["accent"],
        name="mirror_bezel", material_class_id="plastic.opaque_glossy_molded",
    )
    lid.visual(
        mesh_from_cadquery(_lid_accent_solid(r), "lid_edge_accent", tolerance=0.00022),
        material=mats["accent"],
        name="lid_edge", material_class_id="plastic.opaque_glossy_molded",
    )
    return lid


# ---------------------------------------------------------------------------
# Well field placement
# ---------------------------------------------------------------------------


def _grid_field(
    r: ResolvedConfig, index: int, recess_floor_z: float
) -> tuple[PlaneInterface, list[tuple[float, float, float]]]:
    count = r.wells_per_carrier[index]
    cols, rows = _grid_shape(count)
    center_y, half_w, half_d = r.carrier_field_m[index]
    pitch = min(2.0 * half_w / cols, 2.0 * half_d / rows)
    stations: list[tuple[float, float, float]] = []
    for row in range(rows):
        for col in range(cols):
            if len(stations) >= count:
                break
            stations.append(
                (
                    (col - (cols - 1) / 2.0) * pitch,
                    ((rows - 1) / 2.0 - row) * pitch,
                    0.0,
                )
            )
    field = PlaneInterface(
        name=f"tray_topology.well_field_{index}",
        point=(0.0, center_y - r.carrier_hinge_y_m[index], recess_floor_z),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(2.0 * half_w, 2.0 * half_d),
    )
    return field, stations


def _arc_field(
    r: ResolvedConfig, index: int, recess_floor_z: float
) -> tuple[PlaneInterface, list[tuple[float, float, float]]]:
    count = r.wells_per_carrier[index]
    span = 2.0 * (r.leaf_half_angle_rad - 0.22)
    stations: list[tuple[float, float, float]] = []
    for item in range(count):
        if count == 1:
            angle = -math.pi / 2.0
        else:
            angle = -math.pi / 2.0 - span / 2.0 + span * item / float(count - 1)
        stations.append(
            (
                r.leaf_ring_radius_m * math.cos(angle),
                r.leaf_ring_radius_m * math.sin(angle),
                angle + math.pi / 2.0,
            )
        )
    reach = r.leaf_ring_radius_m + r.pan_radius_m + 0.0010
    field = PlaneInterface(
        name=f"tray_topology.well_field_{index}",
        point=(0.0, 0.0, recess_floor_z),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(2.0 * reach, 2.0 * reach),
    )
    return field, stations


def _well_field(r: ResolvedConfig, index: int, recess_floor_z: float):
    if r.tray_topology == "fan_out_carrier":
        return _arc_field(r, index, recess_floor_z)
    return _grid_field(r, index, recess_floor_z)


def _pan_footprint_plane(r: ResolvedConfig) -> PlaneInterface:
    if r.well_profile == "rounded_rect_pan":
        extent = (2.0 * r.pan_radius_m, 1.64 * r.pan_radius_m)
    else:
        extent = (2.0 * r.pan_radius_m, 2.0 * r.pan_radius_m)
    return PlaneInterface(
        name="well_profile.pan_footprint",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=extent,
    )


def _recess_cutter(r: ResolvedConfig, field: PlaneInterface, stations) -> cq.Workplane:
    cutter: cq.Workplane | None = None
    for u, v, spin in stations:
        piece = _well_cutter(r.well_profile, r.recess_radius_m, r.well_depth_eff_m + 0.0008)
        if abs(spin) > 1e-6:
            piece = piece.rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(spin))
        piece = piece.translate((field.point[0] + u, field.point[1] + v, field.point[2]))
        cutter = piece if cutter is None else cutter.union(piece)
    assert cutter is not None
    return cutter


def _emit_wells(
    r: ResolvedConfig,
    carrier: object,
    first_well: int,
    field: PlaneInterface,
    stations,
    mats: dict[str, object],
    pan_mesh,
    powder_mesh,
    powder_materials,
) -> None:
    consumer = _pan_footprint_plane(r)
    for local, (u, v, spin) in enumerate(stations):
        mate = mate_planes(field, consumer, uv=(u, v), spin=spin, margin=0.0)
        well_index = first_well + local
        carrier.visual(
            pan_mesh,
            origin=mate.origin,
            material=mats["pan"],
            name=f"well_profile__{r.well_profile}__pan_{well_index}", material_class_id="metal.aluminum_bare",
        )
        carrier.visual(
            powder_mesh,
            origin=Origin(
                xyz=(
                    mate.origin.xyz[0],
                    mate.origin.xyz[1],
                    mate.origin.xyz[2] + r.pan_height_m,
                ),
                rpy=mate.origin.rpy,
            ),
            material=powder_materials[well_index % len(powder_materials)],
            name=f"well_profile__{r.well_profile}__powder_{well_index}", material_class_id="organic.wax",
        )


# ---------------------------------------------------------------------------
# Carrier topologies
# ---------------------------------------------------------------------------


def _carrier_plate_solid(r: ResolvedConfig, index: int, thickness: float) -> cq.Workplane:
    """Extrude the clipped carrier outline; z in [0, thickness], hinge at the local origin."""

    rows = r.carrier_outline_m[index]
    points = [(h, -s) for s, h in rows] + [(-h, -s) for s, h in reversed(rows)]
    return cq.Workplane("XY").polyline(points).close().extrude(max(thickness, 5e-5))


def _lifting_carrier_solid(
    r: ResolvedConfig, index: int, field: PlaneInterface, stations
) -> cq.Workplane:
    top_local = -_CARRIER_TOP_GAP_M
    plate = _carrier_plate_solid(r, index, r.carrier_thickness_m).translate(
        (0.0, 0.0, top_local - r.carrier_thickness_m)
    )
    plate = plate.cut(_recess_cutter(r, field, stations))
    for sign in (-1.0, 1.0):
        plate = plate.cut(
            _x_cylinder(
                r.carrier_knuckle_len_m + 0.0009,
                r.carrier_knuckle_radius_m + 0.0004,
            ).translate((sign * r.carrier_knuckle_x_m[index], 0.0, 0.0))
        )
    barrel = _x_cylinder(
        2.0 * r.carrier_knuckle_x_m[index] - r.carrier_knuckle_len_m + 2.0 * _AXIAL_BITE_M,
        r.carrier_barrel_radius_m,
    )
    return plate.union(barrel).clean()


def _emit_lifting_carriers(
    model: ArticulatedObject,
    case: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> list[object]:
    topology = r.tray_topology
    pan_mesh = mesh_from_cadquery(
        _well_cutter(r.well_profile, r.pan_radius_m, r.pan_height_m),
        f"pan_{r.well_profile}",
        tolerance=0.00016,
    )
    powder_mesh = mesh_from_cadquery(
        _powder_solid(r.well_profile, r.pan_radius_m - 0.00035, r.powder_height_m),
        f"powder_{r.well_profile}",
        tolerance=0.00016,
    )
    powder_materials = [model.material(name, rgba=rgba) for name, rgba in _POWDER_SHADES]
    knuckle_mesh = mesh_from_cadquery(
        _x_cylinder(r.carrier_knuckle_len_m, r.carrier_knuckle_radius_m),
        f"carrier_knuckle_{topology}",
        tolerance=0.00015,
    )
    carriers: list[object] = []
    first_well = 0
    for index in range(r.carrier_count):
        case.visual(
            mesh_from_cadquery(_seat_pad_solid(r, index), f"seat_pad_{index}", tolerance=0.00024),
            material=mats["hardware"],
            name=f"tray_topology__{topology}__seat_pad_{index}", material_class_id="metal.stainless_matte",
        )
        for side, sign in enumerate((-1.0, 1.0)):
            case.visual(
                knuckle_mesh,
                origin=Origin(
                    xyz=(
                        sign * r.carrier_knuckle_x_m[index],
                        r.carrier_hinge_y_m[index],
                        r.carrier_axis_z_m[index],
                    )
                ),
                material=mats["hardware"],
                name=f"tray_topology__{topology}__knuckle_{index}_{side}", material_class_id="metal.stainless_matte",
            )
        carrier = model.part(
            f"well_carrier_{index}",
            meta={
                "role": "well_carrier",
                "tier": index,
                "well_count": r.wells_per_carrier[index],
                "seat_z_m": r.carrier_seat_z_m[index],
                "pivot_axis": "x",
            },
        )
        field, stations = _well_field(r, index, -_CARRIER_TOP_GAP_M - r.well_depth_eff_m)
        carrier.visual(
            mesh_from_cadquery(
                _lifting_carrier_solid(r, index, field, stations),
                f"carrier_plate_{topology}_{index}",
                tolerance=0.00022,
            ),
            material=mats["shell"],
            name=f"tray_topology__{topology}__plate_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        _emit_wells(
            r,
            carrier,
            first_well,
            field,
            stations,
            mats,
            pan_mesh,
            powder_mesh,
            powder_materials,
        )
        first_well += r.wells_per_carrier[index]
        carriers.append(carrier)
    return carriers


def _tray_topology_single_tray_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> list[object]:
    return _emit_lifting_carriers(model, case, r, mats)


def _tray_topology_double_stacked_carrier_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> list[object]:
    carriers = _emit_lifting_carriers(model, case, r, mats)
    groove_z = 0.5 * (r.carrier_seat_z_m[0] + r.carrier_thickness_m + r.carrier_seat_z_m[1])
    outer = _profile_solid(
        r.case_form,
        r.case_width_m + 0.0005,
        r.case_depth_m + 0.0005,
        0.0011,
        lobe_ratio=r.clover_lobe_ratio,
    )
    inner = _profile_solid(
        r.case_form,
        r.case_width_m - 0.0016,
        r.case_depth_m - 0.0016,
        0.0033,
        lobe_ratio=r.clover_lobe_ratio,
    ).translate((0.0, 0.0, -0.0011))
    case.visual(
        mesh_from_cadquery(
            outer.cut(inner).translate((0.0, 0.0, groove_z)),
            "double_stacked_tier_band",
            tolerance=0.00022,
        ),
        material=mats["accent"],
        name="tray_topology__double_stacked_carrier__tier_band", material_class_id="plastic.opaque_glossy_molded",
    )
    return carriers


def _fan_boss_pieces(r: ResolvedConfig) -> list[tuple[str, cq.Workplane]]:
    """Stepped support boss: one thrust shoulder per leaf plus the captured top pin."""

    top_z = r.carrier_seat_z_m[1] + r.carrier_thickness_m + 0.0010
    return [
        (
            "step_0",
            _z_cylinder(
                r.carrier_seat_z_m[0] - r.floor_thickness_m + 0.0004, r.boss_r0_m
            ).translate((0.0, 0.0, r.floor_thickness_m - 0.0004)),
        ),
        (
            "step_1",
            _z_cylinder(r.carrier_seat_z_m[1] - r.carrier_seat_z_m[0], r.boss_r1_m).translate(
                (0.0, 0.0, r.carrier_seat_z_m[0])
            ),
        ),
        (
            "pin",
            _z_cylinder(top_z - r.carrier_seat_z_m[1], r.boss_r2_m).translate(
                (0.0, 0.0, r.carrier_seat_z_m[1])
            ),
        ),
    ]


def _fan_leaf_solid(r: ResolvedConfig, index: int, field: PlaneInterface, stations) -> cq.Workplane:
    radius = r.leaf_radius_m
    half = r.leaf_half_angle_rad
    base = -math.pi / 2.0
    thickness = r.carrier_thickness_m
    bottom = -_SEAT_BITE_M
    sector = (
        cq.Workplane("XY")
        .moveTo(0.0, 0.0)
        .lineTo(radius * math.cos(base - half), radius * math.sin(base - half))
        .threePointArc(
            (radius * math.cos(base), radius * math.sin(base)),
            (radius * math.cos(base + half), radius * math.sin(base + half)),
        )
        .close()
        .extrude(thickness + _SEAT_BITE_M)
        .edges("|Z")
        .fillet(0.0010)
    )
    hub_outer = (r.boss_r0_m if index == 0 else r.boss_r1_m) + _HUB_WALL_M
    leaf = sector.union(_z_cylinder(thickness + _SEAT_BITE_M, hub_outer))
    leaf = leaf.translate((0.0, 0.0, bottom))
    bore_r = (r.boss_r1_m if index == 0 else r.boss_r2_m) + _BORE_CLEAR_M
    leaf = leaf.cut(_z_cylinder(3.0 * thickness, bore_r).translate((0.0, 0.0, bottom - thickness)))
    return leaf.cut(_recess_cutter(r, field, stations)).clean()


def _tray_topology_fan_out_carrier_build(
    model: ArticulatedObject, case: object, r: ResolvedConfig, mats: dict[str, object]
) -> list[object]:
    topology = "fan_out_carrier"
    for label, solid in _fan_boss_pieces(r):
        case.visual(
            mesh_from_cadquery(solid, f"fan_out_{label}", tolerance=0.00016),
            material=mats["hardware"],
            name=f"tray_topology__{topology}__pivot_{label}", material_class_id="metal.stainless_matte",
        )
    pan_mesh = mesh_from_cadquery(
        _well_cutter(r.well_profile, r.pan_radius_m, r.pan_height_m),
        f"pan_{r.well_profile}",
        tolerance=0.00016,
    )
    powder_mesh = mesh_from_cadquery(
        _powder_solid(r.well_profile, r.pan_radius_m - 0.00035, r.powder_height_m),
        f"powder_{r.well_profile}",
        tolerance=0.00016,
    )
    powder_materials = [model.material(name, rgba=rgba) for name, rgba in _POWDER_SHADES]
    carriers: list[object] = []
    first_well = 0
    for index in range(r.carrier_count):
        carrier = model.part(
            f"well_carrier_{index}",
            meta={
                "role": "well_carrier",
                "tier": index,
                "well_count": r.wells_per_carrier[index],
                "seat_z_m": r.carrier_seat_z_m[index],
                "pivot_axis": "z",
            },
        )
        field, stations = _well_field(
            r, index, r.carrier_thickness_m - _SEAT_BITE_M - r.well_depth_eff_m
        )
        carrier.visual(
            mesh_from_cadquery(
                _fan_leaf_solid(r, index, field, stations),
                f"fan_leaf_{index}",
                tolerance=0.00022,
            ),
            material=mats["shell"],
            name=f"tray_topology__{topology}__leaf_{index}", material_class_id="plastic.opaque_glossy_molded",
        )
        _emit_wells(
            r,
            carrier,
            first_well,
            field,
            stations,
            mats,
            pan_mesh,
            powder_mesh,
            powder_materials,
        )
        first_well += r.wells_per_carrier[index]
        carriers.append(carrier)
    return carriers


_TRAY_BUILDERS = {
    "single_tray": _tray_topology_single_tray_build,
    "double_stacked_carrier": _tray_topology_double_stacked_carrier_build,
    "fan_out_carrier": _tray_topology_fan_out_carrier_build,
}


# ---------------------------------------------------------------------------
# Closure candidates
# ---------------------------------------------------------------------------


def _closure_hinge_only_build(
    model: ArticulatedObject,
    case: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object | None:
    """Friction hinge only: the front thumb relief gains a real moulded lift ramp."""

    ramp = _rounded_box(
        r.notch_width_m + 0.0032,
        0.0024,
        r.notch_height_m + 0.0018,
        0.0006,
    ).translate(
        (
            0.0,
            -(r.case_depth_m / 2.0 + 0.0012 - 0.0006),
            r.case_height_m - r.notch_height_m - 0.0013,
        )
    )
    case.visual(
        mesh_from_cadquery(ramp, "thumb_lift_ramp", tolerance=0.00018),
        material=mats["accent"],
        name="closure__hinge_only__thumb_ramp", material_class_id="plastic.opaque_glossy_molded",
    )
    return None


def _latch_housing_solid(r: ResolvedConfig) -> cq.Workplane:
    front = -r.case_depth_m / 2.0
    outer_y = front - r.latch_housing_out_m
    housing = _rounded_box(
        r.latch_housing_w_m,
        r.latch_housing_out_m + 0.0010,
        r.latch_housing_h_m,
        0.0008,
    ).translate((0.0, outer_y + 0.5 * (r.latch_housing_out_m + 0.0010), r.latch_axis_z_m))
    throat_len = r.latch_throat_len_m + 0.0014
    throat = (
        cq.Workplane("XY")
        .box(r.latch_throat_w_m, throat_len, r.latch_throat_h_m)
        .translate((0.0, outer_y - 0.0014 + throat_len / 2.0, r.latch_axis_z_m))
    )
    chamber = (
        cq.Workplane("XY")
        .box(r.latch_flange_w_m - 0.0002, r.latch_chamber_len_m, r.latch_flange_h_m - 0.0002)
        .translate(
            (
                0.0,
                outer_y + r.latch_throat_len_m + 0.5 * r.latch_chamber_len_m,
                r.latch_axis_z_m,
            )
        )
    )
    return housing.cut(throat).cut(chamber).clean()


def _latch_plunger_solid(r: ResolvedConfig) -> cq.Workplane:
    head_len = r.latch_throat_len_m + 0.0018
    head = _rounded_box(
        r.latch_throat_w_m - 0.0004, head_len, r.latch_throat_h_m - 0.0004, 0.0005
    ).translate((0.0, 0.5 * head_len - 0.0018, 0.0))
    flange = _rounded_box(
        r.latch_flange_w_m, r.latch_flange_t_m, r.latch_flange_h_m, 0.0004
    ).translate((0.0, r.latch_throat_len_m - _AXIAL_BITE_M + 0.5 * r.latch_flange_t_m, 0.0))
    return head.union(flange).clean()


def _latch_hook_solid(r: ResolvedConfig) -> cq.Workplane:
    """Lid lip hook that wraps outside the latch housing, in lid-local coordinates."""

    front = -r.case_depth_m / 2.0
    hook_t = 0.0011
    stand_off = 0.0006
    bite = max(0.6 * r.lid_rim_width_m, 0.0012)
    y_rear = front + bite
    y_fore = front - r.latch_housing_out_m - stand_off - hook_t
    bridge_depth = y_rear - y_fore
    hook_h = r.case_height_m + 0.0010 - r.latch_axis_z_m
    width = r.latch_throat_w_m + 0.0018
    bridge = _rounded_box(width, bridge_depth, 0.0010, 0.0004).translate(
        (0.0, 0.5 * (y_rear + y_fore), r.case_height_m + 0.0005)
    )
    hook = _rounded_box(width, hook_t, hook_h, 0.0004).translate(
        (0.0, y_fore + 0.5 * hook_t, r.case_height_m + 0.0010 - 0.5 * hook_h)
    )
    return bridge.union(hook).clean().translate((0.0, -r.hinge_axis_y_m, -r.hinge_axis_z_m))


def _closure_push_latch_build(
    model: ArticulatedObject,
    case: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object | None:
    case.visual(
        mesh_from_cadquery(_latch_housing_solid(r), "latch_housing", tolerance=0.00018),
        material=mats["hardware"],
        name="closure__push_latch__housing", material_class_id="metal.stainless_matte",
    )
    lid.visual(
        mesh_from_cadquery(_latch_hook_solid(r), "latch_hook", tolerance=0.00016),
        material=mats["hardware"],
        name="closure__push_latch__lid_hook", material_class_id="metal.stainless_matte",
    )
    button = model.part(
        "closure_actuator",
        meta={
            "role": "closure_actuator",
            "mechanism": "push_latch",
            "travel_m": r.latch_travel_m,
            "guided_pocket_m": r.latch_chamber_len_m,
        },
    )
    button.visual(
        mesh_from_cadquery(_latch_plunger_solid(r), "latch_plunger", tolerance=0.00016),
        material=mats["accent"],
        name="closure__push_latch__plunger", material_class_id="plastic.opaque_glossy_molded",
    )
    return button


def _toggle_fork_solid(r: ResolvedConfig) -> cq.Workplane:
    cheek = _x_cylinder(r.toggle_cheek_len_m, r.toggle_hub_radius_m + 0.0009)
    pedestal = _rounded_box(
        r.toggle_cheek_len_m,
        r.toggle_arm_thickness_m + 0.0016,
        r.toggle_axis_z_m,
        0.0004,
    ).translate((0.0, 0.0, -0.5 * r.toggle_axis_z_m))
    return cheek.union(pedestal).clean()


def _toggle_lever_solid(r: ResolvedConfig) -> cq.Workplane:
    arm_w = max(2.0 * r.toggle_cheek_x_m - r.toggle_cheek_len_m - 0.0016, 0.0040)
    hub = _x_cylinder(
        2.0 * r.toggle_cheek_x_m - r.toggle_cheek_len_m + 2.0 * _AXIAL_BITE_M,
        r.toggle_hub_radius_m,
    )
    arm = _rounded_box(arm_w, r.toggle_arm_thickness_m, r.toggle_arm_len_m, 0.0005).translate(
        (0.0, 0.0, 0.5 * r.toggle_arm_len_m)
    )
    lip_depth = r.toggle_arm_thickness_m + 0.0024
    lip = _rounded_box(arm_w, lip_depth, 0.0011, 0.0004).translate(
        (0.0, -0.0012, r.toggle_arm_len_m - 0.00055)
    )
    return hub.union(arm).union(lip).clean()


def _toggle_keeper_solid(r: ResolvedConfig) -> cq.Workplane:
    """Lid keeper lug the toggle hook captures, in lid-local coordinates."""

    front = -r.case_depth_m / 2.0
    bite = max(0.6 * r.lid_rim_width_m, 0.0012)
    lug_depth = r.keeper_out_m + bite
    lug_w = max(2.0 * r.toggle_cheek_x_m - r.toggle_cheek_len_m - 0.0032, 0.0035)
    lip_top = r.toggle_axis_z_m + r.toggle_arm_len_m
    lug = _rounded_box(lug_w, lug_depth, 0.0013, 0.0004).translate(
        (0.0, front + bite - 0.5 * lug_depth, lip_top + 0.0004 + 0.00065)
    )
    return lug.translate((0.0, -r.hinge_axis_y_m, -r.hinge_axis_z_m))


def _closure_over_center_latch_build(
    model: ArticulatedObject,
    case: object,
    lid: object,
    r: ResolvedConfig,
    mats: dict[str, object],
) -> object | None:
    fork_mesh = mesh_from_cadquery(_toggle_fork_solid(r), "toggle_fork", tolerance=0.00016)
    for side, sign in enumerate((-1.0, 1.0)):
        case.visual(
            fork_mesh,
            origin=Origin(xyz=(sign * r.toggle_cheek_x_m, r.toggle_axis_y_m, r.toggle_axis_z_m)),
            material=mats["hardware"],
            name=f"closure__over_center_latch__fork_cheek_{side}", material_class_id="metal.stainless_matte",
        )
    lid.visual(
        mesh_from_cadquery(_toggle_keeper_solid(r), "toggle_keeper", tolerance=0.00016),
        material=mats["hardware"],
        name="closure__over_center_latch__keeper", material_class_id="metal.stainless_matte",
    )
    lever = model.part(
        "closure_actuator",
        meta={
            "role": "closure_actuator",
            "mechanism": "over_center_latch",
            "release_rad": r.toggle_lever_rad,
        },
    )
    lever.visual(
        mesh_from_cadquery(_toggle_lever_solid(r), "toggle_lever", tolerance=0.00016),
        material=mats["accent"],
        name="closure__over_center_latch__lever", material_class_id="plastic.opaque_glossy_molded",
    )
    return lever


_CLOSURE_BUILDERS = {
    "hinge_only": _closure_hinge_only_build,
    "push_latch": _closure_push_latch_build,
    "over_center_latch": _closure_over_center_latch_build,
}


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    palette = _PALETTES[r.palette]
    return {key: model.material(f"{r.palette}_{key}", rgba=value) for key, value in palette.items()}


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent: object,
    child: object,
    provider: AxisInterface,
    consumer: AxisInterface,
    articulation_type: ArticulationType,
    limits: MotionLimits,
    meta: dict[str, object] | None = None,
) -> None:
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        meta=dict(meta or {}),
    )
    register_interface_mate(model, name, mate)


def build_makeup2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "makeup2",
            "slot_choices": (
                ("case_form", r.case_form),
                ("tray_topology", r.tray_topology),
                ("closure", r.closure),
                ("well_profile", r.well_profile),
                ("well_count", r.well_count),
            ),
            "source_identity": (
                "hard-shell hinged makeup compact: moulded case, rim-seated rear-hinged "
                "mirror lid, N-well pressed cosmetic pan grid on articulated carriers"
            ),
            "derived_clearances": {
                "rim_seat_width_m": r.rim_seat_width_m,
                "carrier_gap_m": r.carrier_gap_m,
                "recess_radius_m": r.recess_radius_m,
                "pan_radius_m": r.pan_radius_m,
            },
        },
    )
    mats = _materials(model, r)
    case = model.part(
        "compact_case",
        meta={
            "role": "compact_case",
            "layered_shell": True,
            "case_form": r.case_form,
            "case_width_m": r.case_width_m,
            "case_depth_m": r.case_depth_m,
            "case_height_m": r.case_height_m,
        },
    )
    _CASE_BUILDERS[r.case_form](case, r, mats)
    lid = _build_mirror_lid(model, r, mats)
    carriers = _TRAY_BUILDERS[r.tray_topology](model, case, r, mats)
    actuator = _CLOSURE_BUILDERS[r.closure](model, case, lid, r, mats)

    _axis_joint(
        model,
        name="case_to_mirror_lid",
        parent=case,
        child=lid,
        provider=AxisInterface(
            name="case_form.lid_hinge_axis",
            point=(0.0, r.hinge_axis_y_m, r.hinge_axis_z_m),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=r.hinge_knuckle_radius_m,
        ),
        consumer=AxisInterface(
            name="mirror_lid.barrel_axis",
            point=(0.0, 0.0, 0.0),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 1.0, 0.0),
            radius=r.hinge_barrel_radius_m,
        ),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.2, velocity=2.5, lower=0.0, upper=r.lid_open_rad),
        meta={"closed_position": 0.0, "mechanism": "rear friction compact hinge"},
    )

    carrier_joints: list[str] = []
    for index, carrier in enumerate(carriers):
        joint_name = f"tray_topology__{r.tray_topology}__carrier_{index}_hinge"
        carrier_joints.append(joint_name)
        if r.tray_topology == "fan_out_carrier":
            axis = (0.0, 0.0, 1.0) if index == 0 else (0.0, 0.0, -1.0)
            provider = AxisInterface(
                name=f"case_form.leaf_pivot_{index}",
                point=(0.0, 0.0, r.carrier_seat_z_m[index]),
                axis=axis,
                radial=(0.0, -1.0, 0.0),
                radius=(r.boss_r1_m if index == 0 else r.boss_r2_m) + _BORE_CLEAR_M,
            )
            consumer = AxisInterface(
                name=f"tray_topology.leaf_bore_{index}",
                point=(0.0, 0.0, 0.0),
                axis=axis,
                radial=(0.0, -1.0, 0.0),
                radius=(r.boss_r1_m if index == 0 else r.boss_r2_m),
            )
            limits = MotionLimits(effort=0.5, velocity=1.6, lower=0.0, upper=r.fan_angle_rad)
        else:
            provider = AxisInterface(
                name=f"case_form.carrier_pivot_{index}",
                point=(0.0, r.carrier_hinge_y_m[index], r.carrier_axis_z_m[index]),
                axis=(-1.0, 0.0, 0.0),
                radial=(0.0, 1.0, 0.0),
                radius=r.carrier_knuckle_radius_m,
            )
            consumer = AxisInterface(
                name=f"tray_topology.carrier_barrel_{index}",
                point=(0.0, 0.0, 0.0),
                axis=(-1.0, 0.0, 0.0),
                radial=(0.0, 1.0, 0.0),
                radius=r.carrier_barrel_radius_m,
            )
            limits = MotionLimits(effort=0.6, velocity=2.0, lower=0.0, upper=r.carrier_lift_rad)
        _axis_joint(
            model,
            name=joint_name,
            parent=case,
            child=carrier,
            provider=provider,
            consumer=consumer,
            articulation_type=ArticulationType.REVOLUTE,
            limits=limits,
            meta={"tier": index},
        )

    latch_joint: str | None = None
    latch_open: float = 0.0
    if actuator is not None and r.closure == "push_latch":
        latch_joint = "closure__push_latch__latch_press"
        latch_open = r.latch_travel_m
        _axis_joint(
            model,
            name=latch_joint,
            parent=case,
            child=actuator,
            provider=AxisInterface(
                name="case_form.latch_guide",
                point=(0.0, -(r.case_depth_m / 2.0 + r.latch_housing_out_m), r.latch_axis_z_m),
                axis=(0.0, 1.0, 0.0),
                radial=(0.0, 0.0, 1.0),
            ),
            consumer=AxisInterface(
                name="closure.plunger_guide",
                point=(0.0, 0.0, 0.0),
                axis=(0.0, 1.0, 0.0),
                radial=(0.0, 0.0, 1.0),
            ),
            articulation_type=ArticulationType.PRISMATIC,
            limits=MotionLimits(effort=2.0, velocity=0.4, lower=0.0, upper=r.latch_travel_m),
            meta={"mechanism": "push latch release", "pressed_position": r.latch_travel_m},
        )
    elif actuator is not None:
        latch_joint = "closure__over_center_latch__toggle_release"
        latch_open = r.toggle_lever_rad
        _axis_joint(
            model,
            name=latch_joint,
            parent=case,
            child=actuator,
            provider=AxisInterface(
                name="case_form.toggle_pin",
                point=(0.0, r.toggle_axis_y_m, r.toggle_axis_z_m),
                axis=(1.0, 0.0, 0.0),
                radial=(0.0, 0.0, 1.0),
                radius=r.toggle_hub_radius_m + 0.0009,
            ),
            consumer=AxisInterface(
                name="closure.toggle_hub",
                point=(0.0, 0.0, 0.0),
                axis=(1.0, 0.0, 0.0),
                radial=(0.0, 0.0, 1.0),
                radius=r.toggle_hub_radius_m,
            ),
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=1.8, velocity=2.0, lower=0.0, upper=r.toggle_lever_rad),
            meta={
                "mechanism": "over-center latch",
                "detent_positions": [0.0, r.toggle_lever_rad],
            },
        )

    interlocks: list[dict[str, object]] = [
        {
            "controller_joint": "case_to_mirror_lid",
            "controller_required_position": r.lid_open_rad,
            "dependent_joints": list(carrier_joints),
        }
    ]
    if r.tray_topology == "double_stacked_carrier":
        interlocks.append(
            {
                "controller_joint": carrier_joints[1],
                "controller_required_position": r.carrier_lift_rad,
                "dependent_joints": [carrier_joints[0]],
            }
        )
    if latch_joint is not None:
        interlocks.append(
            {
                "controller_joint": latch_joint,
                "controller_required_position": latch_open,
                "dependent_joints": ["case_to_mirror_lid"],
            }
        )
    model.meta["motion_interlocks"] = interlocks
    return model


def build_seeded_makeup2(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_makeup2(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Author tests
# ---------------------------------------------------------------------------


def _parts_by_role(model: ArticulatedObject, role: str) -> list[object]:
    return [part for part in model.parts if part.meta.get("role") == role]


def _count_visuals(parts, prefix: str) -> int:
    return sum(
        1 for part in parts for visual in part.visuals if str(visual.name).startswith(prefix)
    )


def run_makeup2_tests(model: ArticulatedObject, config: Config | None = None) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    cases = _parts_by_role(model, "compact_case")
    lids = _parts_by_role(model, "mirror_lid")
    carriers = _parts_by_role(model, "well_carrier")
    actuators = _parts_by_role(model, "closure_actuator")
    case = cases[0] if cases else None
    lid = lids[0] if lids else None
    lid_hinge = model.get_articulation("case_to_mirror_lid")
    carrier_joints = [
        model.get_articulation(f"tray_topology__{r.tray_topology}__carrier_{index}_hinge")
        for index in range(r.carrier_count)
    ]

    ctx.check(
        "category_anchor: makeup2 compact case and mirror lid identity",
        len(cases) == 1
        and len(lids) == 1
        and case is not None
        and lid is not None
        and case.meta.get("layered_shell") is True
        and lid.meta.get("seats_on_rim_land") is True
        and case.get_visual(f"case_form__{r.case_form}__shell") is not None
        and case.get_visual(f"case_form__{r.case_form}__rim_accent") is not None
        and all(
            case.get_visual(f"case_form__{r.case_form}__lid_knuckle_{side}") is not None
            for side in range(2)
        )
        and lid.get_visual("lid_frame") is not None
        and lid.get_visual("lid_barrel") is not None
        and lid.get_visual("mirror") is not None
        and lid.get_visual("mirror_bezel") is not None
        and lid_hinge is not None
        and lid_hinge.articulation_type == ArticulationType.REVOLUTE
        and tuple(lid_hinge.axis) == (-1.0, 0.0, 0.0)
        and lid_hinge.parent == "compact_case"
        and lid_hinge.child == "mirror_lid"
        and lid_hinge.motion_limits is not None
        and math.isclose(lid_hinge.motion_limits.lower, 0.0, abs_tol=1e-9)
        and lid_hinge.motion_limits.upper >= 1.60,
        details=(
            f"cases={len(cases)}, lids={len(lids)}, form={r.case_form}, open={r.lid_open_rad}"
        ),
    )
    ctx.check(
        "category_anchor: makeup2 cosmetic well carriers and pan grid",
        len(carriers) == r.carrier_count
        and all(joint is not None for joint in carrier_joints)
        and all(joint.articulation_type == ArticulationType.REVOLUTE for joint in carrier_joints)
        and all(joint.parent == "compact_case" for joint in carrier_joints)
        and all(
            carrier.get_visual(
                f"tray_topology__{r.tray_topology}__"
                + ("leaf_" if r.tray_topology == "fan_out_carrier" else "plate_")
                + str(index)
            )
            is not None
            for index, carrier in enumerate(carriers)
        )
        and sum(int(part.meta.get("well_count", 0)) for part in carriers) == r.well_count
        and _count_visuals(carriers, f"well_profile__{r.well_profile}__pan_") == r.well_count
        and _count_visuals(carriers, f"well_profile__{r.well_profile}__powder_") == r.well_count,
        details=(
            f"topology={r.tray_topology}, carriers={len(carriers)}, "
            f"wells={r.well_count}, split={r.wells_per_carrier}"
        ),
    )
    ctx.check(
        "category_anchor: makeup2 closure hardware and registered hinge axes",
        len(actuators) == r.closure_actuator_count
        and (
            r.closure != "hinge_only"
            or case.get_visual("closure__hinge_only__thumb_ramp") is not None
        )
        and (
            r.closure != "push_latch"
            or (
                case.get_visual("closure__push_latch__housing") is not None
                and lid.get_visual("closure__push_latch__lid_hook") is not None
                and model.get_articulation("closure__push_latch__latch_press").articulation_type
                == ArticulationType.PRISMATIC
            )
        )
        and (
            r.closure != "over_center_latch"
            or (
                all(
                    case.get_visual(f"closure__over_center_latch__fork_cheek_{side}") is not None
                    for side in range(2)
                )
                and lid.get_visual("closure__over_center_latch__keeper") is not None
                and model.get_articulation(
                    "closure__over_center_latch__toggle_release"
                ).articulation_type
                == ArticulationType.REVOLUTE
            )
        )
        and all(
            (joint.meta or {}).get("interface_mate") is not None for joint in model.articulations
        ),
        details=(
            f"closure={r.closure}, actuators={len(actuators)}, "
            f"joints={[joint.name for joint in model.articulations]}"
        ),
    )

    ctx.check(
        "closed lid rim ring lands entirely on the case rim land",
        0.0008 < r.lid_rim_width_m < r.rim_seat_width_m
        and r.rim_seat_width_m - r.lid_rim_width_m >= 0.0006
        and r.lid_seat_dz_m < 0.0
        and r.hinge_axis_z_m > r.case_height_m,
        details=(
            f"lid_rim={r.lid_rim_width_m}, rim_seat={r.rim_seat_width_m}, "
            f"seat_dz={r.lid_seat_dz_m}, hinge_z={r.hinge_axis_z_m}"
        ),
    )
    ctx.check(
        "every cosmetic well is a real recess holding a pan and pressed powder",
        r.recess_radius_m > r.pan_radius_m
        and r.pan_radius_m >= 0.0014
        and r.carrier_thickness_m > r.well_depth_eff_m + 0.0009
        and r.pan_height_m > 0.00015
        and r.powder_height_m > 0.0002
        and r.pan_height_m + r.powder_height_m + 0.00025 <= r.well_depth_eff_m + 1e-9,
        details=(
            f"pan_r={r.pan_radius_m}, recess_r={r.recess_radius_m}, "
            f"carrier_t={r.carrier_thickness_m}, well_depth_eff={r.well_depth_eff_m}, "
            f"pan_h={r.pan_height_m}, powder_h={r.powder_height_m}"
        ),
    )
    ctx.check(
        "hinge barrels are axially captured between real knuckles with radial relief",
        r.hinge_barrel_radius_m < r.hinge_knuckle_radius_m
        and 2.0 * r.hinge_knuckle_x_m - r.hinge_knuckle_len_m > 0.0020
        and r.carrier_barrel_radius_m < r.carrier_knuckle_radius_m
        and all(2.0 * x - r.carrier_knuckle_len_m > 0.0014 for x in r.carrier_knuckle_x_m)
        and all(
            x - 0.5 * r.carrier_knuckle_len_m + _AXIAL_BITE_M
            < r.hinge_knuckle_x_m - 0.5 * r.hinge_knuckle_len_m
            for x in r.carrier_knuckle_x_m
        ),
        details=(
            f"lid_knuckle_x={r.hinge_knuckle_x_m}, lid_len={r.hinge_knuckle_len_m}, "
            f"carrier_knuckle_x={r.carrier_knuckle_x_m}, "
            f"carrier_len={r.carrier_knuckle_len_m}"
        ),
    )
    ctx.check(
        "carriers and wells stay inside the closed case envelope with real tier gaps",
        all(seat + r.carrier_thickness_m <= r.case_height_m - 0.0005 for seat in r.carrier_seat_z_m)
        and r.carrier_seat_z_m[0] >= r.floor_thickness_m + _MIN_TIER_GAP_M - 1e-9
        and (
            r.carrier_count == 1
            or r.carrier_seat_z_m[1] - (r.carrier_seat_z_m[0] + r.carrier_thickness_m)
            >= _MIN_TIER_GAP_M - 1e-9
        )
        and all(
            axis_z + r.carrier_barrel_radius_m <= r.case_height_m for axis_z in r.carrier_axis_z_m
        ),
        details=(
            f"seats={r.carrier_seat_z_m}, axes={r.carrier_axis_z_m}, "
            f"carrier_t={r.carrier_thickness_m}, height={r.case_height_m}"
        ),
    )
    if r.tray_topology != "fan_out_carrier":
        ctx.check(
            "swing-up carriers hang below their pivot and rest on real seat pads",
            all(
                math.isclose(
                    axis_z, seat + r.carrier_thickness_m + _CARRIER_TOP_GAP_M, abs_tol=1e-9
                )
                for axis_z, seat in zip(r.carrier_axis_z_m, r.carrier_seat_z_m, strict=True)
            )
            and r.ledge_width_m > _CARRIER_SIDE_CLEAR_M + 0.0008
            and all(
                case.get_visual(f"tray_topology__{r.tray_topology}__seat_pad_{index}") is not None
                and all(
                    case.get_visual(f"tray_topology__{r.tray_topology}__knuckle_{index}_{side}")
                    is not None
                    for side in range(2)
                )
                for index in range(r.carrier_count)
            ),
            details=f"ledge={r.ledge_width_m}, axes={r.carrier_axis_z_m}",
        )
    else:
        ctx.check(
            "fan-out leaves ride a stepped support boss inside the turntable well",
            0.0 < r.boss_r2_m < r.boss_r1_m < r.boss_r0_m
            and r.leaf_radius_m <= r.turntable_radius_m - 0.0008 + 1e-9
            and r.leaf_ring_radius_m + r.pan_radius_m < r.leaf_radius_m
            and r.leaf_ring_radius_m - r.pan_radius_m > r.boss_r0_m + _HUB_WALL_M
            and all(
                case.get_visual(f"tray_topology__fan_out_carrier__pivot_{label}") is not None
                for label in ("step_0", "step_1", "pin")
            ),
            details=(
                f"boss=({r.boss_r0_m},{r.boss_r1_m},{r.boss_r2_m}), "
                f"leaf_r={r.leaf_radius_m}, turntable={r.turntable_radius_m}, "
                f"ring={r.leaf_ring_radius_m}, pan_r={r.pan_radius_m}"
            ),
        )
    if r.closure == "push_latch":
        ctx.check(
            "push latch plunger is captured by a guided pocket longer than its stroke",
            r.latch_chamber_len_m >= r.latch_flange_t_m + r.latch_travel_m + 0.0005
            and r.latch_flange_w_m > r.latch_throat_w_m
            and r.latch_flange_h_m > r.latch_throat_h_m
            and r.latch_housing_out_m >= r.latch_throat_len_m + r.latch_chamber_len_m + 0.0008
            and r.latch_axis_z_m + 0.5 * r.latch_housing_h_m
            <= r.case_height_m - _RIM_TOP_CLEAR_M + 1e-9,
            details=(
                f"chamber={r.latch_chamber_len_m}, travel={r.latch_travel_m}, "
                f"throat=({r.latch_throat_w_m},{r.latch_throat_h_m}), "
                f"flange=({r.latch_flange_w_m},{r.latch_flange_h_m}), "
                f"housing_out={r.latch_housing_out_m}"
            ),
        )
    if r.closure == "over_center_latch":
        ctx.check(
            "over-centre toggle hook reaches the lid keeper from a captured pin",
            r.toggle_hub_radius_m > 0.0
            and r.toggle_cheek_x_m > 0.5 * r.toggle_cheek_len_m
            and r.toggle_axis_z_m + r.toggle_arm_len_m > r.case_height_m
            and r.keeper_out_m > r.toggle_arm_thickness_m
            and r.toggle_axis_y_m < -0.5 * r.case_depth_m,
            details=(
                f"axis=({r.toggle_axis_y_m},{r.toggle_axis_z_m}), "
                f"arm={r.toggle_arm_len_m}, keeper_out={r.keeper_out_m}, "
                f"release={r.toggle_lever_rad}"
            ),
        )

    case_aabb = ctx.part_world_aabb(case)
    lid_closed_aabb = ctx.part_world_aabb(lid)
    ctx.check(
        "closed compact reads as one flat handheld case",
        case_aabb is not None
        and lid_closed_aabb is not None
        and lid_closed_aabb[1][2] <= case_aabb[1][2] + r.lid_thickness_m + 0.0035
        and (case_aabb[1][0] - case_aabb[0][0]) >= 1.9 * r.case_height_m,
        details=f"case={case_aabb}, lid_closed={lid_closed_aabb}",
    )
    with ctx.pose({lid_hinge: r.lid_open_rad}):
        lid_open_aabb = ctx.part_world_aabb(lid)
    ctx.check(
        "opened lid lifts the mirror clear above the case rim",
        lid_open_aabb is not None
        and case_aabb is not None
        and lid_open_aabb[1][2] > case_aabb[1][2] + 0.55 * r.case_depth_m,
        details=f"lid_open={lid_open_aabb}, case={case_aabb}",
    )
    for index, joint in enumerate(carrier_joints):
        with ctx.pose({lid_hinge: r.lid_open_rad}):
            seated = ctx.part_world_aabb(carriers[index])
        with ctx.pose({lid_hinge: r.lid_open_rad, joint: joint.motion_limits.upper}):
            moved = ctx.part_world_aabb(carriers[index])
        if r.tray_topology == "fan_out_carrier":
            ok = (
                moved is not None
                and seated is not None
                and max(abs(moved[1][0] - seated[1][0]), abs(moved[0][0] - seated[0][0]))
                > 0.12 * r.leaf_radius_m
            )
        else:
            ok = (
                moved is not None
                and seated is not None
                and moved[1][2] > seated[1][2] + 0.12 * r.carrier_depth_m[index]
            )
        ctx.check(
            f"well carrier {index} actually travels on its own registered pivot",
            ok,
            details=f"seated={seated}, moved={moved}, topology={r.tray_topology}",
        )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "clover_double_stack_over_center_max",
        {
            "case_form": "clover",
            "tray_topology": "double_stacked_carrier",
            "closure": "over_center_latch",
            "well_profile": "rounded_rect_pan",
            "well_count": 8,
            "case_width_m": 0.104,
            "case_depth_ratio": 1.00,
            "case_height_m": 0.034,
            "wall_thickness_m": 0.0034,
            "lid_open_rad": 2.00,
            "clover_lobe_ratio": 0.42,
            "well_diameter_ratio": 0.86,
            "well_depth_m": 0.0030,
            "carrier_lift_rad": 1.45,
            "tier_gap_ratio": 0.40,
            "toggle_lever_rad": 1.10,
        },
        reason="hardest host profile with two real tiers, 8 wells and a toggle latch at max size",
    ),
    corner_case(
        "clover_fan_out_push_latch_min_host",
        {
            "case_form": "clover",
            "tray_topology": "fan_out_carrier",
            "closure": "push_latch",
            "well_profile": "round_pan",
            "well_count": 8,
            "case_width_m": 0.070,
            "case_depth_ratio": 0.82,
            "case_height_m": 0.022,
            "wall_thickness_m": 0.0034,
            "lid_open_rad": 1.66,
            "clover_lobe_ratio": 0.28,
            "well_diameter_ratio": 0.86,
            "well_depth_m": 0.0030,
            "fan_angle_rad": 1.20,
            "leaf_sector_ratio": 0.82,
            "latch_travel_m": 0.0032,
        },
        reason="smallest clover host, thickest wall, deepest wells and the largest fan sweep",
    ),
    corner_case(
        "round_fan_out_over_center_two_wells",
        {
            "case_form": "round",
            "tray_topology": "fan_out_carrier",
            "closure": "over_center_latch",
            "well_profile": "rounded_rect_pan",
            "well_count": 2,
            "case_width_m": 0.098,
            "case_depth_ratio": 1.00,
            "case_height_m": 0.023,
            "wall_thickness_m": 0.0018,
            "lid_open_rad": 2.00,
            "well_diameter_ratio": 0.55,
            "well_depth_m": 0.0016,
            "fan_angle_rad": 0.55,
            "leaf_sector_ratio": 0.56,
            "toggle_lever_rad": 0.55,
        },
        reason="minimum N with the smallest leaf sector and thinnest wall on a round host",
    ),
    corner_case(
        "rounded_rect_double_stack_push_latch_shallow",
        {
            "case_form": "rounded_rect",
            "tray_topology": "double_stacked_carrier",
            "closure": "push_latch",
            "well_profile": "round_pan",
            "well_count": 8,
            "case_width_m": 0.104,
            "case_depth_ratio": 0.82,
            "case_height_m": 0.022,
            "wall_thickness_m": 0.0034,
            "lid_open_rad": 2.00,
            "well_diameter_ratio": 0.86,
            "well_depth_m": 0.0030,
            "carrier_lift_rad": 1.45,
            "tier_gap_ratio": 0.25,
            "latch_travel_m": 0.0032,
        },
        reason="shallowest two-tier stack: tier gaps, latch pocket and lid seat are all tightest",
    ),
    corner_case(
        "clover_single_tray_hinge_only_min",
        {
            "case_form": "clover",
            "tray_topology": "single_tray",
            "closure": "hinge_only",
            "well_profile": "round_pan",
            "well_count": 2,
            "case_width_m": 0.070,
            "case_depth_ratio": 0.82,
            "case_height_m": 0.022,
            "wall_thickness_m": 0.0018,
            "lid_open_rad": 1.66,
            "clover_lobe_ratio": 0.28,
            "well_diameter_ratio": 0.55,
            "well_depth_m": 0.0016,
            "carrier_lift_rad": 0.80,
            "thumb_notch_ratio": 0.34,
            "palette": "pearl_ivory",
        },
        reason="smallest source-like clover compact with the widest thumb relief",
    ),
    corner_case(
        "round_single_tray_over_center_tall",
        {
            "case_form": "round",
            "tray_topology": "single_tray",
            "closure": "over_center_latch",
            "well_profile": "rounded_rect_pan",
            "well_count": 6,
            "case_width_m": 0.076,
            "case_depth_ratio": 1.00,
            "case_height_m": 0.034,
            "wall_thickness_m": 0.0030,
            "lid_open_rad": 1.70,
            "well_diameter_ratio": 0.80,
            "well_depth_m": 0.0028,
            "carrier_lift_rad": 1.45,
            "toggle_lever_rad": 1.10,
            "palette": "emerald_enamel",
        },
        reason="tall narrow round host: longest toggle arm and deepest single-tier compartment",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_makeup2",
    "build_seeded_makeup2",
    "config_from_seed",
    "resolve_config",
    "run_makeup2_tests",
]
