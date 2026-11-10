# SPDX-License-Identifier: Apache-2.0

"""Self-contained Urban Environment / Tilt Truck2 template.

A poly **tilt truck** (tilt cart / dump cart): a hollow molded HDPE hopper that
tilts forward about a lateral trunnion axis carried by a steel chassis, held
down in the transport pose by a retaining latch, rolling on two large fixed main
wheels at the dump end and two swivel casters at the push end, with a tubular
push handle.

The tilt joint and its latch are the subcategory identity mechanisms; they are
present in every combination.  Five structural slots vary around that shared
core:

``hopper_form``   the molded tub section family (rounded wedge / U-nose scoop /
                  V-nose spout / barrel side / chamfered octagon)
``latch``         the retaining mechanism (gravity hook / C-throat claw /
                  over-centre side lever / foot-pedal release linkage)
``push_handle``   rear hoop / side grab rails / fold-down hoop (revolute)
``chassis``       welded box-rail deck / bent tube frame / forklift pockets
``caster``        plain swivel caster / swivel caster with a step-on brake

``deck_bearer_count`` is a structural multiplicity on ``chassis``: the transverse
steel bearers the tub floor seats on.

Every revolute/continuous joint is solved with ``mate_axes`` and registered with
``register_interface_mate``.  The template emits **no** ``allow_overlap``: every
pin/bore fit is a clevis or a sub-tolerance axial lap.  ``motion_interlocks``
declares the real operation order (the hopper cannot tilt until the latch is
released, and the foot pedal only travels with the latch released).

Source evidence: ``articraft_data/picture_expansion/template_source_maps/
Urban_Environment__Tilt_Truck2.md``.
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
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    tube_from_spline_points,
)

HopperForm = Literal[
    "rounded_wedge",
    "u_nose_scoop",
    "v_nose_spout",
    "barrel_side",
    "chamfered_octagon",
]
Latch = Literal[
    "gravity_hook",
    "c_throat_claw",
    "overcenter_side_lever",
    "foot_pedal_release",
]
PushHandle = Literal["rear_loop", "side_rails", "folding_hoop"]
Chassis = Literal["box_rail_deck", "tube_frame", "fork_pockets", "molded_underbody"]
Caster = Literal["plain_swivel", "braked_swivel"]
PaletteStyle = Literal["commercial_black", "safety_yellow", "utility_blue", "charcoal"]

HOPPER_FORMS: tuple[HopperForm, ...] = (
    "rounded_wedge",
    "u_nose_scoop",
    "v_nose_spout",
    "barrel_side",
    "chamfered_octagon",
)
LATCHES: tuple[Latch, ...] = (
    "gravity_hook",
    "c_throat_claw",
    "overcenter_side_lever",
    "foot_pedal_release",
)
PUSH_HANDLES: tuple[PushHandle, ...] = ("rear_loop", "side_rails", "folding_hoop")
CHASSIS_KINDS: tuple[Chassis, ...] = (
    "box_rail_deck",
    "tube_frame",
    "fork_pockets",
    "molded_underbody",
)
CASTERS: tuple[Caster, ...] = ("plain_swivel", "braked_swivel")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "commercial_black",
    "safety_yellow",
    "utility_blue",
    "charcoal",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("hopper_form", HOPPER_FORMS),
        component_slot("latch", LATCHES),
        component_slot("push_handle", PUSH_HANDLES),
        component_slot("chassis", CHASSIS_KINDS),
        component_slot("caster", CASTERS),
        multiplicity_slot("deck_bearer_count", (2, 3, 4), item_slot="chassis"),
    )
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "commercial_black": {
        "hopper": (0.085, 0.088, 0.095, 1.0),
        "hopper_rib": (0.065, 0.068, 0.074, 1.0),
        "frame": (0.60, 0.085, 0.105, 1.0),
        "steel": (0.24, 0.25, 0.26, 1.0),
        "zinc": (0.70, 0.72, 0.74, 1.0),
        "tire": (0.055, 0.058, 0.062, 1.0),
        "rim": (0.30, 0.31, 0.32, 1.0),
        "caster_tread": (0.70, 0.11, 0.13, 1.0),
    },
    "safety_yellow": {
        "hopper": (0.97, 0.74, 0.06, 1.0),
        "hopper_rib": (0.85, 0.64, 0.05, 1.0),
        "frame": (0.09, 0.09, 0.10, 1.0),
        "steel": (0.20, 0.21, 0.22, 1.0),
        "zinc": (0.74, 0.76, 0.78, 1.0),
        "tire": (0.07, 0.07, 0.075, 1.0),
        "rim": (0.80, 0.81, 0.80, 1.0),
        "caster_tread": (0.40, 0.40, 0.42, 1.0),
    },
    "utility_blue": {
        "hopper": (0.20, 0.44, 0.71, 1.0),
        "hopper_rib": (0.15, 0.35, 0.60, 1.0),
        "frame": (0.11, 0.12, 0.13, 1.0),
        "steel": (0.20, 0.21, 0.23, 1.0),
        "zinc": (0.70, 0.72, 0.75, 1.0),
        "tire": (0.07, 0.07, 0.08, 1.0),
        "rim": (0.55, 0.57, 0.60, 1.0),
        "caster_tread": (0.26, 0.27, 0.29, 1.0),
    },
    "charcoal": {
        "hopper": (0.235, 0.245, 0.255, 1.0),
        "hopper_rib": (0.200, 0.210, 0.220, 1.0),
        "frame": (0.170, 0.175, 0.185, 1.0),
        "steel": (0.30, 0.31, 0.32, 1.0),
        "zinc": (0.735, 0.750, 0.775, 1.0),
        "tire": (0.070, 0.070, 0.075, 1.0),
        "rim": (0.215, 0.222, 0.232, 1.0),
        "caster_tread": (0.600, 0.145, 0.115, 1.0),
    },
}

# --- fixed cross-section constants (continuous detail, not core/raw) ---------
N_SEG = 44  # points per hopper plan section
WALL_T = 0.011  # molded HDPE wall thickness
RIM_TUBE_R = 0.016  # rolled rim lip tube radius
# Mount lap: parts overlap their host along ONE axis by less than the 5 mm
# collision tolerance, so QC reads them as connected contact, never an overlap.
LAP = 0.0008
KEEPER_R = 0.009  # transverse latch keeper bar radius
MAIN_HUB_EXTEND = 0.012  # main wheel hub sleeve proud of each tyre face
CASTER_HUB_EXTEND = 0.006  # caster wheel hub boss proud of each tread face
LATCH_PLATE_HALF = 0.007  # latch plate half thickness
LATCH_OPEN = 0.90
LATCH_LOCKED = -0.10  # over-centre lever only
THROAT_GAP = 0.006  # C-throat clearance around the keeper bar
OVERCENTRE_THROAT_GAP = 0.018  # the over-centre jaw needs room to swing past
PEDAL_MAX = 0.42
BRAKE_MAX = 0.26
HANDLE_FOLD_MAX = 1.42
# Fraction of the tub floor half-width the molded underbody apron is allowed to
# fall to before its side run is considered ended.  Everything the frameless
# chassis carries inside the apron must stay inboard of that face.
APRON_SIDE_FRAC = 0.92

HOPPER_LENGTH_RANGE = (1.50, 1.85)
HOPPER_WIDTH_RANGE = (0.78, 0.95)
HOPPER_DEPTH_RANGE = (0.55, 0.86)
MAIN_WHEEL_RADIUS_RANGE = (0.125, 0.165)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Config:
    hopper_form: HopperForm = "rounded_wedge"
    latch: Latch = "gravity_hook"
    push_handle: PushHandle = "rear_loop"
    chassis: Chassis = "box_rail_deck"
    caster: Caster = "plain_swivel"
    deck_bearer_count: int = 3
    hopper_length_m: float | None = None
    hopper_width_m: float | None = None
    hopper_depth_m: float | None = None
    main_wheel_radius_m: float | None = None
    palette_style: PaletteStyle = "commercial_black"
    name: str = "Urban_Environment_Tilt_Truck2"


@dataclass(frozen=True)
class ResolvedConfig:
    hopper_form: HopperForm
    latch: Latch
    push_handle: PushHandle
    chassis: Chassis
    caster: Caster
    frameless: bool
    deck_bearer_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # independent
    hopper_length_m: float
    hopper_width_m: float
    hopper_depth_m: float
    main_wheel_radius_m: float
    # derived hopper envelope
    hw_rim: float
    hw_floor: float
    trunnion_x: float
    trunnion_z: float
    floor_z: float
    rim_z: float
    x_rim_front: float
    x_rim_rear: float
    x_floor_front: float
    x_floor_rear: float
    tilt_max_rad: float
    # derived chassis
    rail_z0: float
    rail_z1: float
    rail_y_in: float
    rail_y_out: float
    frame_x0: float
    frame_x1: float
    axle_x: float
    wheel_y: float
    wheel_half_width: float
    bearer_x: tuple[float, ...]
    bearer_half_y: float
    rear_beam_x: float
    rear_beam_half_y: float
    spine_y: float
    # molded underbody apron (frameless tier only)
    skirt_z0: float
    apron_x0: float
    apron_x1: float
    apron_inner_y: float
    # derived caster
    caster_x: float
    caster_y: float
    caster_swivel_z: float
    caster_radius: float
    caster_half_width: float
    caster_trail: float
    caster_axle_local_z: float
    # derived latch
    keeper_x: float
    keeper_z: float
    keeper_half_span: float
    latch_pivot_x: float
    latch_pivot_y: float
    latch_pivot_z: float
    latch_dx: float
    latch_dz: float
    latch_lower: float
    latch_upper: float
    # derived handle
    handle_x: float
    handle_y: float
    handle_top_z: float
    handle_hinge_z: float
    # derived trunnion hardware
    channel_y_in: float
    channel_y_out: float
    bracket_y0: float
    bracket_y1: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _check_range(value: float | None, lo: float, hi: float, label: str) -> None:
    if value is not None and not lo <= float(value) <= hi:
        raise ValueError(f"{label} must be in [{lo}, {hi}]")


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x71_17_2C_A2)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        hopper_form=choices["hopper_form"],
        latch=choices["latch"],
        push_handle=choices["push_handle"],
        chassis=choices["chassis"],
        caster=choices["caster"],
        deck_bearer_count=choices["deck_bearer_count"],
        hopper_length_m=round(rng.uniform(*HOPPER_LENGTH_RANGE), 4),
        hopper_width_m=round(rng.uniform(*HOPPER_WIDTH_RANGE), 4),
        hopper_depth_m=round(rng.uniform(*HOPPER_DEPTH_RANGE), 4),
        main_wheel_radius_m=round(rng.uniform(*MAIN_WHEEL_RADIUS_RANGE), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"tilt_truck2_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "hopper_form": config.hopper_form,
            "latch": config.latch,
            "push_handle": config.push_handle,
            "chassis": config.chassis,
            "caster": config.caster,
            "deck_bearer_count": config.deck_bearer_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    _check_range(config.hopper_length_m, *HOPPER_LENGTH_RANGE, label="hopper_length_m")
    _check_range(config.hopper_width_m, *HOPPER_WIDTH_RANGE, label="hopper_width_m")
    _check_range(config.hopper_depth_m, *HOPPER_DEPTH_RANGE, label="hopper_depth_m")
    _check_range(
        config.main_wheel_radius_m, *MAIN_WHEEL_RADIUS_RANGE, label="main_wheel_radius_m"
    )

    length = 1.66 if config.hopper_length_m is None else float(config.hopper_length_m)
    width = 0.86 if config.hopper_width_m is None else float(config.hopper_width_m)
    depth = 0.80 if config.hopper_depth_m is None else float(config.hopper_depth_m)
    wheel_r = (
        0.142 if config.main_wheel_radius_m is None else float(config.main_wheel_radius_m)
    )

    # --- hopper envelope (world frame; +X = dump nose, +Z up, ground z = 0) ---
    hw_rim = 0.500 * width
    hw_floor = 0.330 * width
    trunnion_x = 0.425 * length
    x_rim_front = trunnion_x + 0.075 * length
    x_rim_rear = trunnion_x - 0.925 * length
    x_floor_front = trunnion_x - 0.130 * length
    x_floor_rear = trunnion_x - 0.820 * length
    floor_z = wheel_r + 0.105
    rim_z = floor_z + depth
    trunnion_z = floor_z + 0.040
    # A deeper tub carries its discharge lip higher, so it needs more rotation to
    # bring that lip down to pouring height: the dump stroke derives from depth.
    span = HOPPER_DEPTH_RANGE[1] - HOPPER_DEPTH_RANGE[0]
    tilt_max = 0.90 + 0.30 * (depth - HOPPER_DEPTH_RANGE[0]) / span

    # --- chassis ---------------------------------------------------------
    # The frameless tier (003/004) carries no exposed ladder: the molded body
    # forms the underbody, so the chassis shrinks to a compact bolt-on subframe
    # tucked inside the tub plan silhouette and hidden by the molded apron.
    frameless = config.chassis == "molded_underbody"
    rail_z1 = floor_z - 0.026
    rail_z0 = rail_z1 - 0.055
    rail_y_out = 0.360 * width
    rail_y_in = 0.300 * width
    axle_x = trunnion_x - 0.090 * length
    frame_x1 = trunnion_x + (0.030 if frameless else 0.065)
    wheel_y = 0.485 * width
    wheel_half_width = 0.260 * wheel_r

    latch_dx = 0.105
    latch_dz = 0.085
    if frameless:
        # No frame tail to hang the latch clevis off: the rear mount is pulled
        # in as far as the swept latch claw still clears the molded rear wall,
        # which leans backwards as it rises.  That derived stop, not a magic
        # constant, sets how far the frameless chassis reaches behind the tub.
        claw_reach = math.hypot(latch_dx, latch_dz) + 0.020
        claw_rise = 0.045
        wall_lean = (x_floor_rear - x_rim_rear) / depth
        wall_x_at_claw = x_floor_rear - claw_rise * wall_lean
        latch_pivot_x = wall_x_at_claw - claw_reach - 0.012
        rear_beam_x = latch_pivot_x - 0.040
        frame_x0 = min(rear_beam_x - 0.030, x_rim_rear - 0.030)
        rear_beam_x = frame_x0 + 0.030
        latch_pivot_x = rear_beam_x + 0.040
    else:
        frame_x0 = x_rim_rear - 0.130
        rear_beam_x = frame_x0 + 0.030
        latch_pivot_x = rear_beam_x + 0.040
    rear_beam_half_y = hw_rim + 0.075

    # Molded underbody apron: the tub's outer side wall carried on down past the
    # pan.  Its inner face is the hard lateral bound for every chassis element
    # that lives inside it, so the subframe track and the bearer span derive
    # from the same number.
    apron_inner_y = APRON_SIDE_FRAC * hw_floor - WALL_T
    skirt_z0 = rail_z0 - 0.008
    apron_x0 = x_rim_rear + 0.030
    apron_x1 = x_floor_front
    if frameless:
        bearer_half_y = apron_inner_y - 0.006
        spine_y = apron_inner_y - 0.045
    else:
        bearer_half_y = rail_y_out - 0.005
        spine_y = rail_y_in

    bearer_lo = x_floor_rear + 0.090
    bearer_hi = x_floor_front - 0.090
    n_bearer = int(config.deck_bearer_count)
    if n_bearer < 2:
        bearer_x = (0.5 * (bearer_lo + bearer_hi),)
    else:
        step = (bearer_hi - bearer_lo) / (n_bearer - 1)
        bearer_x = tuple(bearer_lo + step * i for i in range(n_bearer))

    # --- casters ---------------------------------------------------------
    caster_x = x_rim_rear + 0.140 * length
    # host adaptation: the frameless tier bolts its casters to pads under the
    # molded pan, inboard of the apron, instead of under outboard frame rails
    caster_y = spine_y if frameless else 0.300 * width
    caster_swivel_z = rail_z0 - 0.020
    caster_radius = 0.300 * caster_swivel_z
    caster_half_width = 0.300 * caster_radius
    caster_trail = 0.500 * caster_radius
    caster_axle_local_z = caster_radius - caster_swivel_z

    # --- latch -----------------------------------------------------------
    latch_pivot_z = rail_z1 + 0.022
    keeper_x = latch_pivot_x + latch_dx
    keeper_z = latch_pivot_z + latch_dz
    if config.latch == "overcenter_side_lever":
        latch_pivot_y = rail_y_out + 0.042
        keeper_half_span = latch_pivot_y + 0.030
        latch_lower, latch_upper = LATCH_LOCKED, 1.00
    else:
        latch_pivot_y = 0.0
        keeper_half_span = 0.060
        latch_lower, latch_upper = 0.0, LATCH_OPEN

    # --- push handle -----------------------------------------------------
    handle_x = rear_beam_x
    handle_y = hw_rim + 0.055
    handle_top_z = rim_z + 0.100
    handle_hinge_z = rail_z1 + 0.075

    # --- trunnion hardware ------------------------------------------------
    channel_y_in = hw_floor + 0.002
    channel_y_out = hw_floor + 0.022
    bracket_y0 = channel_y_out + 0.007
    bracket_y1 = bracket_y0 + 0.016

    return ResolvedConfig(
        hopper_form=config.hopper_form,
        latch=config.latch,
        push_handle=config.push_handle,
        chassis=config.chassis,
        caster=config.caster,
        frameless=frameless,
        deck_bearer_count=n_bearer,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        hopper_length_m=length,
        hopper_width_m=width,
        hopper_depth_m=depth,
        main_wheel_radius_m=wheel_r,
        hw_rim=hw_rim,
        hw_floor=hw_floor,
        trunnion_x=trunnion_x,
        trunnion_z=trunnion_z,
        floor_z=floor_z,
        rim_z=rim_z,
        x_rim_front=x_rim_front,
        x_rim_rear=x_rim_rear,
        x_floor_front=x_floor_front,
        x_floor_rear=x_floor_rear,
        tilt_max_rad=tilt_max,
        rail_z0=rail_z0,
        rail_z1=rail_z1,
        rail_y_in=rail_y_in,
        rail_y_out=rail_y_out,
        frame_x0=frame_x0,
        frame_x1=frame_x1,
        axle_x=axle_x,
        wheel_y=wheel_y,
        wheel_half_width=wheel_half_width,
        bearer_x=bearer_x,
        bearer_half_y=bearer_half_y,
        rear_beam_x=rear_beam_x,
        rear_beam_half_y=rear_beam_half_y,
        spine_y=spine_y,
        skirt_z0=skirt_z0,
        apron_x0=apron_x0,
        apron_x1=apron_x1,
        apron_inner_y=apron_inner_y,
        caster_x=caster_x,
        caster_y=caster_y,
        caster_swivel_z=caster_swivel_z,
        caster_radius=caster_radius,
        caster_half_width=caster_half_width,
        caster_trail=caster_trail,
        caster_axle_local_z=caster_axle_local_z,
        keeper_x=keeper_x,
        keeper_z=keeper_z,
        keeper_half_span=keeper_half_span,
        latch_pivot_x=latch_pivot_x,
        latch_pivot_y=latch_pivot_y,
        latch_pivot_z=latch_pivot_z,
        latch_dx=latch_dx,
        latch_dz=latch_dz,
        latch_lower=latch_lower,
        latch_upper=latch_upper,
        handle_x=handle_x,
        handle_y=handle_y,
        handle_top_z=handle_top_z,
        handle_hinge_z=handle_hinge_z,
        channel_y_in=channel_y_in,
        channel_y_out=channel_y_out,
        bracket_y0=bracket_y0,
        bracket_y1=bracket_y1,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("hopper_form", config.hopper_form),
        ("latch", config.latch),
        ("push_handle", config.push_handle),
        ("chassis", config.chassis),
        ("caster", config.caster),
        ("deck_bearer_count", config.deck_bearer_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Generic geometry helpers
# ---------------------------------------------------------------------------


def _arc(cx: float, cy: float, r: float, a0: float, a1: float, n: int):
    return [
        (cx + r * math.cos(a0 + (a1 - a0) * k / n), cy + r * math.sin(a0 + (a1 - a0) * k / n))
        for k in range(n + 1)
    ]


def _line(p0, p1, n: int):
    return [
        (p0[0] + (p1[0] - p0[0]) * k / n, p0[1] + (p1[1] - p0[1]) * k / n) for k in range(n + 1)
    ]


def _resample_closed(points, count: int):
    """Uniform arc-length resample of a closed polygon, preserving the start."""
    pts = list(points)
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    n = len(pts)
    lengths = [0.0]
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        lengths.append(lengths[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    total = lengths[-1]
    out = []
    j = 0
    for k in range(count):
        target = total * k / count
        while j < n and lengths[j + 1] < target:
            j += 1
        seg = lengths[j + 1] - lengths[j]
        t = 0.0 if seg <= 1e-12 else (target - lengths[j]) / seg
        a = pts[j % n]
        b = pts[(j + 1) % n]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def _polygon_area(points) -> float:
    area = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        area += x0 * y1 - x1 * y0
    return 0.5 * area


def _revolved_y(profile, name: str, segments: int = 28):
    """Solid of revolution about the local +Y spin axis (wheels and tyres)."""
    return mesh_from_geometry(
        LatheGeometry(list(profile), segments=segments, closed=True).rotate_x(math.pi / 2.0),
        name,
    )


# ---------------------------------------------------------------------------
# hopper_form candidates: one plan-section generator per structural family
# ---------------------------------------------------------------------------


def _hopper_form_rounded_wedge_build(xr: float, xf: float, hw: float, r: float):
    """004/002 baseline: rounded-rectangle molded section."""
    r = _clamp(r, 0.012, min(0.40 * (xf - xr), 0.75 * hw))
    pts = []
    pts += _line((xf, 0.0), (xf, hw - r), 3)
    pts += _arc(xf - r, hw - r, r, 0.0, math.pi / 2.0, 5)
    pts += _line((xf - r, hw), (xr + r, hw), 6)
    pts += _arc(xr + r, hw - r, r, math.pi / 2.0, math.pi, 5)
    pts += _line((xr, hw - r), (xr, -(hw - r)), 4)
    pts += _arc(xr + r, -(hw - r), r, math.pi, 1.5 * math.pi, 5)
    pts += _line((xr + r, -hw), (xf - r, -hw), 6)
    pts += _arc(xf - r, -(hw - r), r, 1.5 * math.pi, 2.0 * math.pi, 5)
    return pts


def _hopper_form_u_nose_scoop_build(xr: float, xf: float, hw: float, r: float):
    """rounded_nose fork: flat rear, straight sides, continuous semicircular nose."""
    r = _clamp(r, 0.012, min(0.30 * (xf - xr), 0.70 * hw))
    ucx = xf - hw
    min_ucx = xr + r + 0.06 * (xf - xr)
    if ucx < min_ucx:
        ucx = min_ucx
        hw_nose = max(0.02, xf - ucx)
    else:
        hw_nose = hw
    pts = []
    pts += _arc(ucx, 0.0, hw_nose, 0.0, math.pi / 2.0, 8)
    pts += _line((ucx, hw_nose), (ucx, hw), 1)
    pts += _line((ucx, hw), (xr + r, hw), 6)
    pts += _arc(xr + r, hw - r, r, math.pi / 2.0, math.pi, 5)
    pts += _line((xr, hw - r), (xr, -(hw - r)), 4)
    pts += _arc(xr + r, -(hw - r), r, math.pi, 1.5 * math.pi, 5)
    pts += _line((xr + r, -hw), (ucx, -hw), 6)
    pts += _line((ucx, -hw), (ucx, -hw_nose), 1)
    pts += _arc(ucx, 0.0, hw_nose, 1.5 * math.pi, 2.0 * math.pi, 8)
    return pts


def _hopper_form_v_nose_spout_build(xr: float, xf: float, hw: float, r: float):
    """vnose fork: broad load bay converging into a narrow rounded pouring spout."""
    r = _clamp(r, 0.012, min(0.25 * (xf - xr), 0.70 * hw))
    nose_hw = max(0.030, 0.32 * hw)
    nose_r = _clamp(0.45 * nose_hw, 0.010, 0.9 * nose_hw)
    span = max(1e-6, xf - xr)

    def side(x: float) -> float:
        t = _clamp((x - xr) / span, 0.0, 1.0)
        taper = t**4
        return hw * (1.0 - taper) + nose_hw * taper

    pts = []
    pts += _line((xf, 0.0), (xf, nose_hw - nose_r), 2)
    pts += _arc(xf - nose_r, nose_hw - nose_r, nose_r, 0.0, math.pi / 2.0, 4)
    upper = [xf - nose_r - (xf - nose_r - (xr + r)) * k / 8.0 for k in range(9)]
    pts += [(x, side(x)) for x in upper]
    pts += _arc(xr + r, hw - r, r, math.pi / 2.0, math.pi, 4)
    pts += _line((xr, hw - r), (xr, -(hw - r)), 4)
    pts += _arc(xr + r, -(hw - r), r, math.pi, 1.5 * math.pi, 4)
    pts += [(x, -side(x)) for x in reversed(upper)]
    pts += _arc(xf - nose_r, -(nose_hw - nose_r), nose_r, 1.5 * math.pi, 2.0 * math.pi, 4)
    return pts


def _hopper_form_barrel_side_build(xr: float, xf: float, hw: float, r: float):
    """barrel_side fork: rounded wedge whose long side walls bow convexly outward."""
    r = _clamp(r, 0.012, min(0.40 * (xf - xr), 0.75 * hw))
    bow = 0.055 * hw

    def bowed(x: float) -> float:
        t = _clamp((x - (xr + r)) / max(1e-6, (xf - r) - (xr + r)), 0.0, 1.0)
        return hw + bow * math.sin(math.pi * t)

    xs = [(xf - r) - ((xf - r) - (xr + r)) * k / 8.0 for k in range(9)]
    pts = []
    pts += _line((xf, 0.0), (xf, hw - r), 3)
    pts += _arc(xf - r, hw - r, r, 0.0, math.pi / 2.0, 5)
    pts += [(x, bowed(x)) for x in xs]
    pts += _arc(xr + r, hw - r, r, math.pi / 2.0, math.pi, 5)
    pts += _line((xr, hw - r), (xr, -(hw - r)), 4)
    pts += _arc(xr + r, -(hw - r), r, math.pi, 1.5 * math.pi, 5)
    pts += [(x, -bowed(x)) for x in reversed(xs)]
    pts += _arc(xf - r, -(hw - r), r, 1.5 * math.pi, 2.0 * math.pi, 5)
    return pts


def _hopper_form_chamfered_octagon_build(xr: float, xf: float, hw: float, r: float):
    """chamfered_octagonal fork: true eight-sided section with 45-degree facets."""
    c = _clamp(2.0 * r, 0.015, min(0.42 * (xf - xr), 0.85 * hw))
    corners = [
        (xf, 0.0),
        (xf, hw - c),
        (xf - c, hw),
        (xr + c, hw),
        (xr, hw - c),
        (xr, -(hw - c)),
        (xr + c, -hw),
        (xf - c, -hw),
        (xf, -(hw - c)),
    ]
    pts = []
    for a, b in zip(corners, corners[1:]):
        pts += _line(a, b, 4)
    return pts


_HOPPER_PLAN_BUILDERS = {
    "rounded_wedge": _hopper_form_rounded_wedge_build,
    "u_nose_scoop": _hopper_form_u_nose_scoop_build,
    "v_nose_spout": _hopper_form_v_nose_spout_build,
    "barrel_side": _hopper_form_barrel_side_build,
    "chamfered_octagon": _hopper_form_chamfered_octagon_build,
}


def _hopper_section_descriptor(r: ResolvedConfig, t: float) -> tuple[float, float, float, float]:
    """Shared height descriptor: (x_rear, x_front, half_width, corner_radius)."""
    t = _clamp(t, 0.0, 1.0)
    xr = r.x_floor_rear + (r.x_rim_rear - r.x_floor_rear) * t
    xf = r.x_floor_front + (r.x_rim_front - r.x_floor_front) * t
    hw = r.hw_floor + (r.hw_rim - r.hw_floor) * t
    if r.hopper_form == "barrel_side":
        # the belly peaks above the frame rail zone, keeping the lower walls narrow
        bulge = 1.0 + 0.135 * math.sin(math.pi * (t**0.75))
        hw *= bulge
        xr -= 0.030 * (bulge - 1.0) * (xf - xr)
        xf += 0.030 * (bulge - 1.0) * (xf - xr)
    return xr, xf, hw, 0.30 * hw


def _hopper_plan(r: ResolvedConfig, t: float, inset: float):
    xr, xf, hw, corner = _hopper_section_descriptor(r, t)
    xr += inset
    xf -= inset
    hw -= inset
    corner = max(0.010, corner - inset)
    hw = max(0.030, hw)
    if xf - xr < 0.10:
        mid = 0.5 * (xr + xf)
        xr, xf = mid - 0.05, mid + 0.05
    dense = _HOPPER_PLAN_BUILDERS[r.hopper_form](xr, xf, hw, corner)
    return _resample_closed(dense, N_SEG)


def _side_wall_point(r: ResolvedConfig, t: float, x_frac: float) -> tuple[float, float]:
    """Outer wall point on the +y side at a longitudinal fraction of the section."""
    pts = _hopper_plan(r, t, 0.0)
    xs = [p[0] for p in pts]
    target = min(xs) + (max(xs) - min(xs)) * x_frac
    best = None
    for px, py in pts:
        if py <= 0.0:
            continue
        key = (abs(px - target), -py)
        if best is None or key < best[0]:
            best = (key, px, py)
    if best is None:
        return target, 0.5 * (max(xs) - min(xs))
    return best[1], best[2]


def _rear_wall_point(r: ResolvedConfig, t: float, y_frac: float) -> tuple[float, float]:
    """Outer wall point on the rear (-x) face at a lateral fraction of the section."""
    pts = _hopper_plan(r, t, 0.0)
    xs = [p[0] for p in pts]
    mid = 0.5 * (min(xs) + max(xs))
    target = max(abs(p[1]) for p in pts) * y_frac
    best = None
    for px, py in pts:
        if px > mid or py * y_frac < 0.0:
            continue
        key = (abs(py - target), px)
        if best is None or key < best[0]:
            best = (key, px, py)
    if best is None:
        return min(xs), target
    return best[1], best[2]


_OUTER_T = (0.0, 0.22, 0.48, 0.74, 1.0)


def _inner_t(r: ResolvedConfig) -> tuple[float, ...]:
    t0 = _clamp(WALL_T / r.hopper_depth_m, 0.005, 0.20)
    return (t0, t0 + (1.0 - t0) * 0.28, t0 + (1.0 - t0) * 0.55, t0 + (1.0 - t0) * 0.80, 1.0)


def _tub_mesh(r: ResolvedConfig) -> tuple[MeshGeometry, float, float]:
    """Hollow open-top molded tub: outer skin, floor, inner cavity skin, rim band.

    Returns the mesh plus (cavity volume, shell volume) measured from the same
    section stacks, so the author tests can prove the tub is not a solid block.
    """
    mesh = MeshGeometry()
    zt = r.trunnion_z

    outer_rings = []
    for t in _OUTER_T:
        z = r.floor_z + r.hopper_depth_m * t - zt
        outer_rings.append((z, _hopper_plan(r, t, 0.0)))
    inner_rings = []
    for t in _inner_t(r):
        z = r.floor_z + r.hopper_depth_m * t - zt
        inner_rings.append((z, _hopper_plan(r, t, WALL_T)))

    def add_ring(ring) -> int:
        z, pts = ring
        base = len(mesh.vertices)
        for x, y in pts:
            mesh.add_vertex(x - r.trunnion_x, y, z)
        return base

    outer_base = [add_ring(ring) for ring in outer_rings]
    inner_base = [add_ring(ring) for ring in inner_rings]

    def band(b0: int, b1: int, flip: bool) -> None:
        for i in range(N_SEG):
            j = (i + 1) % N_SEG
            a, b, c, d = b0 + i, b0 + j, b1 + j, b1 + i
            if flip:
                mesh.add_face(a, c, b)
                mesh.add_face(a, d, c)
            else:
                mesh.add_face(a, b, c)
                mesh.add_face(a, c, d)

    for k in range(len(outer_base) - 1):
        band(outer_base[k], outer_base[k + 1], flip=False)
    for k in range(len(inner_base) - 1):
        band(inner_base[k], inner_base[k + 1], flip=True)
    # rim band closes the wall between the outer and inner top rings
    band(outer_base[-1], inner_base[-1], flip=True)

    def cap(base: int, ring, up: bool) -> None:
        z, pts = ring
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        centre = mesh.add_vertex(cx - r.trunnion_x, cy, z)
        for i in range(N_SEG):
            j = (i + 1) % N_SEG
            if up:
                mesh.add_face(centre, base + i, base + j)
            else:
                mesh.add_face(centre, base + j, base + i)

    cap(outer_base[0], outer_rings[0], up=False)  # outer floor underside
    cap(inner_base[0], inner_rings[0], up=True)  # cavity floor

    def prism_volume(rings) -> float:
        total = 0.0
        for (z0, p0), (z1, p1) in zip(rings, rings[1:]):
            a0 = abs(_polygon_area(p0))
            a1 = abs(_polygon_area(p1))
            total += (z1 - z0) * (a0 + a1 + math.sqrt(a0 * a1)) / 3.0
        return total

    outer_volume = prism_volume(outer_rings)
    cavity_volume = prism_volume(inner_rings)
    return mesh, cavity_volume, outer_volume - cavity_volume


def _apron_side_chain(r: ResolvedConfig) -> list[tuple[float, float]]:
    """+y side run of the molded underbody apron, taken from the active form.

    The apron is the tub's own outer side wall carried on down past the pan, so
    its plan comes from the *active* ``hopper_form`` plan builder rather than a
    hardcoded rectangle: a V-nose apron tapers, a barrel apron bows, an octagon
    apron keeps its facets.  Only the near-full-width side run is kept; where
    the plan turns in at the ends the molded body is already narrower than the
    subframe track and there is nothing left to hide.
    """
    hw = r.hw_floor
    dense = _HOPPER_PLAN_BUILDERS[r.hopper_form](r.apron_x0, r.apron_x1, hw, 0.30 * hw)
    pts = _resample_closed(dense, N_SEG)
    best: list[tuple[float, float]] = []
    for frac in (APRON_SIDE_FRAC, 0.80, 0.60, 0.40):
        thresh = frac * hw
        run: list[tuple[float, float]] = []
        for p in pts + pts:  # cyclic scan: the +y run may straddle the seam
            if p[1] >= thresh and len(run) < N_SEG:
                run.append(p)
            else:
                if len(run) > len(best):
                    best = run
                run = []
        if len(run) > len(best):
            best = run
        if len(best) >= 4:
            break
    if len(best) < 4:
        best = [
            (r.apron_x0 + 0.05, hw),
            (0.5 * (r.apron_x0 + r.apron_x1), hw),
            (r.apron_x1 - 0.05, hw),
            (r.apron_x1 - 0.02, hw),
        ]
    # The apron wall is never allowed inboard of the clearance line the subframe
    # track and the bearer span were derived from.
    floor_y = APRON_SIDE_FRAC * hw
    return [(x, max(y, floor_y)) for x, y in best]


def _underbody_apron_mesh(r: ResolvedConfig, chain, side: float) -> MeshGeometry:
    """One closed molded side apron: outer skin, inner skin, top and bottom rims."""
    mesh = MeshGeometry()
    zt = r.trunnion_z
    z_top = r.floor_z - zt
    z_bot = r.skirt_z0 - zt
    out_top, out_bot, in_top, in_bot = [], [], [], []
    for x, y in chain:
        xo = x - r.trunnion_x
        yo = side * y
        yi = side * (y - WALL_T)
        out_top.append(mesh.add_vertex(xo, yo, z_top))
        out_bot.append(mesh.add_vertex(xo, yo, z_bot))
        in_top.append(mesh.add_vertex(xo, yi, z_top))
        in_bot.append(mesh.add_vertex(xo, yi, z_bot))

    def quad(a: int, b: int, c: int, d: int) -> None:
        mesh.add_face(a, b, c)
        mesh.add_face(a, c, d)

    n = len(chain)
    for i in range(n - 1):
        j = i + 1
        quad(out_top[i], out_bot[i], out_bot[j], out_top[j])
        quad(in_top[j], in_bot[j], in_bot[i], in_top[i])
        quad(out_top[i], out_top[j], in_top[j], in_top[i])
        quad(out_bot[j], out_bot[i], in_bot[i], in_bot[j])
    quad(out_top[0], in_top[0], in_bot[0], out_bot[0])
    quad(out_bot[n - 1], in_bot[n - 1], in_top[n - 1], out_top[n - 1])
    return mesh


def _build_hopper(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    hopper = model.part("hopper", meta={"role": "hopper"})
    form = r.hopper_form
    tub, cavity_volume, shell_volume = _tub_mesh(r)
    hopper.visual(
        mesh_from_geometry(tub, f"hopper_form__{form}__tub_shell"),
        material=mats["hopper"],
        name=f"hopper_form__{form}__tub_shell", material_class_id="plastic.opaque_glossy_molded",
    )

    # rolled rim lip
    rim_ring = _hopper_plan(r, 1.0, RIM_TUBE_R * 0.4)
    rim_pts = [
        (x - r.trunnion_x, y, r.rim_z - r.trunnion_z)
        for x, y in rim_ring[:: max(1, N_SEG // 22)]
    ]
    hopper.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                rim_pts,
                radius=RIM_TUBE_R,
                samples_per_segment=2,
                radial_segments=8,
                closed_spline=True,
            ),
            f"hopper_form__{form}__rim_lip",
        ),
        material=mats["hopper"],
        name=f"hopper_form__{form}__rim_lip", material_class_id="plastic.opaque_glossy_molded",
    )

    # Frameless tier host adaptation: the molded body forms the underbody, so
    # the tub's side wall carries on down past the pan as a closed apron that
    # covers the whole subframe band in side view.
    if r.frameless:
        chain = _apron_side_chain(r)
        for idx, side in enumerate((1.0, -1.0)):
            hopper.visual(
                mesh_from_geometry(
                    _underbody_apron_mesh(r, chain, side),
                    f"hopper_form__{form}__underbody_apron_{idx}",
                ),
                material=mats["hopper"],
                name=f"hopper_form__{form}__underbody_apron_{idx}", material_class_id="plastic.opaque_glossy_molded",
            )

    # molded vertical stiffener beads on both side walls
    rib_t = (0.10, 0.35, 0.62, 0.88)
    for idx, tx in enumerate((0.28, 0.50, 0.72)):
        for side_idx, side in enumerate((1.0, -1.0)):
            pts = []
            for t in rib_t:
                x, y = _side_wall_point(r, t, tx)
                pts.append(
                    (
                        x - r.trunnion_x,
                        side * (y - 0.004),
                        r.floor_z + r.hopper_depth_m * t - r.trunnion_z,
                    )
                )
            hopper.visual(
                mesh_from_geometry(
                    tube_from_spline_points(
                        pts, radius=0.012, samples_per_segment=3, radial_segments=8
                    ),
                    f"hopper_form__{form}__side_rib_{idx}_{side_idx}",
                ),
                material=mats["hopper_rib"],
                name=f"hopper_form__{form}__side_rib_{idx}_{side_idx}", material_class_id="plastic.opaque_glossy_molded",
            )

    # rear-wall beads
    for idx, ry in enumerate((-0.34, 0.34)):
        pts = []
        for t in rib_t:
            x, y = _rear_wall_point(r, t, ry)
            pts.append(
                (
                    x - r.trunnion_x + 0.006,
                    y,
                    r.floor_z + r.hopper_depth_m * t - r.trunnion_z,
                )
            )
        hopper.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    pts, radius=0.011, samples_per_segment=3, radial_segments=8
                ),
                f"hopper_form__{form}__rear_rib_{idx}",
            ),
            material=mats["hopper_rib"],
            name=f"hopper_form__{form}__rear_rib_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )

    # steel side channels carrying the trunnion pins forward of the tub
    channel_z0 = r.floor_z + 0.002
    channel_z1 = r.floor_z + 0.078
    channel_x0 = r.x_floor_rear + 0.16
    for idx, side in enumerate((1.0, -1.0)):
        hopper.visual(
            Box(
                (
                    r.trunnion_x - channel_x0,
                    r.channel_y_out - r.channel_y_in,
                    channel_z1 - channel_z0,
                )
            ),
            origin=Origin(
                xyz=(
                    0.5 * (channel_x0 + r.trunnion_x) - r.trunnion_x,
                    side * 0.5 * (r.channel_y_in + r.channel_y_out),
                    0.5 * (channel_z0 + channel_z1) - r.trunnion_z,
                )
            ),
            material=mats["steel"],
            name=f"trunnion_channel_{idx}", material_class_id="metal.steel_bare",
        )
        # molded pivot boss plus the steel trunnion pin stub
        hopper.visual(
            Cylinder(radius=0.030, length=(r.bracket_y0 - 0.004) - (r.channel_y_out - 0.014)),
            origin=Origin(
                xyz=(
                    0.0,
                    side * 0.5 * ((r.channel_y_out - 0.014) + (r.bracket_y0 - 0.004)),
                    0.0,
                ),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["hopper_rib"],
            name=f"trunnion_boss_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
        pin_lo = r.channel_y_out - 0.010
        pin_hi = r.bracket_y0 + LAP
        hopper.visual(
            Cylinder(radius=0.014, length=pin_hi - pin_lo),
            origin=Origin(
                xyz=(0.0, side * 0.5 * (pin_lo + pin_hi), 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["zinc"],
            name=f"trunnion_pin_{idx}", material_class_id="metal.steel_galvanized",
        )

    # transverse latch keeper bar on molded webs standing off the rear wall
    keeper_t = _clamp((r.keeper_z - r.floor_z) / r.hopper_depth_m, 0.0, 1.0)
    wall_x = _hopper_section_descriptor(r, keeper_t)[0]
    web_len = max(0.050, wall_x - r.keeper_x + 0.030)
    web_cx = r.keeper_x - 0.015 + 0.5 * web_len
    web_ys = [0.046, -0.046]
    if r.keeper_half_span > 0.10:
        web_ys += [r.hw_floor - 0.030, -(r.hw_floor - 0.030)]
    for idx, wy in enumerate(web_ys):
        hopper.visual(
            Box((web_len, 0.012, 0.034)),
            origin=Origin(
                xyz=(web_cx - r.trunnion_x, wy, r.keeper_z - r.trunnion_z)
            ),
            material=mats["hopper_rib"],
            name=f"keeper_web_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    hopper.visual(
        Cylinder(radius=KEEPER_R, length=2.0 * r.keeper_half_span),
        origin=Origin(
            xyz=(r.keeper_x - r.trunnion_x, 0.0, r.keeper_z - r.trunnion_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["zinc"],
        name="latch_keeper_bar", material_class_id="metal.steel_galvanized",
    )

    hopper.inertial = Inertial.from_geometry(
        Box((r.hopper_length_m, r.hopper_width_m, r.hopper_depth_m)),
        mass=52.0,
        origin=Origin(
            xyz=(
                0.5 * (r.x_rim_front + r.x_rim_rear) - r.trunnion_x,
                0.0,
                0.5 * (r.floor_z + r.rim_z) - r.trunnion_z,
            )
        ),
    )
    return hopper, cavity_volume, shell_volume


# ---------------------------------------------------------------------------
# chassis candidates
# ---------------------------------------------------------------------------


def _chassis_common(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """Trunnion brackets, main axle, caster seats, latch clevis and deck bearers."""
    kind = r.chassis
    for idx, side in enumerate((1.0, -1.0)):
        # trunnion tower plate + bearing hub
        plate_z0 = r.rail_z1 - 0.010
        plate_z1 = r.trunnion_z + 0.055
        part.visual(
            Box((0.110, r.bracket_y1 - r.bracket_y0, plate_z1 - plate_z0)),
            origin=Origin(
                xyz=(
                    r.trunnion_x,
                    side * 0.5 * (r.bracket_y0 + r.bracket_y1),
                    0.5 * (plate_z0 + plate_z1),
                )
            ),
            material=mats["steel"],
            name=f"trunnion_bracket_{idx}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=0.030, length=r.bracket_y1 - r.bracket_y0),
            origin=Origin(
                xyz=(r.trunnion_x, side * 0.5 * (r.bracket_y0 + r.bracket_y1), r.trunnion_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["zinc"],
            name=f"trunnion_hub_{idx}", material_class_id="metal.steel_galvanized",
        )
        # gusset tying the trunnion tower back to the frame rails, kept well
        # below the hopper side channel so the tub never rubs the chassis
        gy0 = min(r.spine_y, r.rail_y_in, r.bracket_y0 - 0.030)
        part.visual(
            Box((0.100, r.bracket_y1 - gy0, 0.018)),
            origin=Origin(
                xyz=(
                    r.trunnion_x,
                    side * 0.5 * (gy0 + r.bracket_y1),
                    r.rail_z1 - 0.007,
                )
            ),
            material=mats["steel"],
            name=f"trunnion_gusset_{idx}", material_class_id="metal.steel_bare",
        )
        # axle bearing block
        part.visual(
            Box((0.085, 0.024, r.rail_z1 - r.main_wheel_radius_m + 0.045)),
            origin=Origin(
                xyz=(
                    r.axle_x,
                    side * (r.rail_y_out - 0.012),
                    0.5 * (r.main_wheel_radius_m - 0.045 + r.rail_z1),
                )
            ),
            material=mats["steel"],
            name=f"axle_block_{idx}", material_class_id="metal.steel_bare",
        )
        # caster raceway seat under the rail (the frameless pad is trimmed so it
        # stays inboard of the molded apron inner face)
        seat_top = r.rail_z0 + 0.006
        seat = 0.076 if r.frameless else 0.100
        part.visual(
            Box((seat, seat, seat_top - r.caster_swivel_z)),
            origin=Origin(
                xyz=(r.caster_x, side * r.caster_y, 0.5 * (r.caster_swivel_z + seat_top))
            ),
            material=mats["steel"],
            name=f"caster_seat_{idx}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=0.032, length=0.020),
            origin=Origin(xyz=(r.caster_x, side * r.caster_y, r.caster_swivel_z + 0.010)),
            material=mats["zinc"],
            name=f"caster_raceway_{idx}", material_class_id="metal.steel_galvanized",
        )

    # transverse main axle: ends lap into the wheel hub sleeves by less than
    # the collision tolerance, so the wheels are carried without interpenetration
    axle_half = r.wheel_y - r.wheel_half_width - MAIN_HUB_EXTEND + LAP
    part.visual(
        Cylinder(radius=0.018, length=2.0 * axle_half),
        origin=Origin(
            xyz=(r.axle_x, 0.0, r.main_wheel_radius_m), rpy=(math.pi / 2.0, 0.0, 0.0)
        ),
        material=mats["zinc"],
        name="main_axle", material_class_id="metal.steel_galvanized",
    )

    # latch clevis cheeks + hinge pin bosses
    for idx, side in enumerate((1.0, -1.0)):
        part.visual(
            Box((0.048, 0.012, (r.latch_pivot_z + 0.030) - r.rail_z0)),
            origin=Origin(
                xyz=(
                    r.latch_pivot_x,
                    r.latch_pivot_y + side * 0.020,
                    0.5 * (r.rail_z0 + r.latch_pivot_z + 0.030),
                )
            ),
            material=mats["steel"],
            name=f"latch_cheek_{idx}", material_class_id="metal.steel_bare",
        )

    # rear outrigger beam: carries the push handle and closes the frame
    part.visual(
        Box((0.060, 2.0 * r.rear_beam_half_y, r.rail_z1 - r.rail_z0)),
        origin=Origin(xyz=(r.rear_beam_x, 0.0, 0.5 * (r.rail_z0 + r.rail_z1))),
        material=mats["frame"],
        name="rear_outrigger_beam", material_class_id="metal.paint_coated",
    )

    # deck bearers (multiplicity): the tub floor seats on every one of them
    bearer_z0 = r.rail_z0
    bearer_z1 = r.floor_z + LAP
    for i, bx in enumerate(r.bearer_x):
        part.visual(
            Box((0.060, 2.0 * r.bearer_half_y, bearer_z1 - bearer_z0)),
            origin=Origin(xyz=(bx, 0.0, 0.5 * (bearer_z0 + bearer_z1))),
            material=mats["steel"],
            name=f"chassis__{kind}__deck_bearer_{i}", material_class_id="metal.steel_bare",
        )


def _chassis_box_rail_deck_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """004/003 baseline: welded box side rails plus full-width cross members."""
    zc = 0.5 * (r.rail_z0 + r.rail_z1)
    h = r.rail_z1 - r.rail_z0
    for idx, side in enumerate((1.0, -1.0)):
        part.visual(
            Box((r.frame_x1 - r.frame_x0, r.rail_y_out - r.rail_y_in, h)),
            origin=Origin(
                xyz=(
                    0.5 * (r.frame_x0 + r.frame_x1),
                    side * 0.5 * (r.rail_y_in + r.rail_y_out),
                    zc,
                )
            ),
            material=mats["frame"],
            name=f"chassis__box_rail_deck__side_rail_{idx}", material_class_id="metal.paint_coated",
        )
    for idx, cx in enumerate(
        (r.frame_x1 - 0.045, 0.5 * (r.frame_x0 + r.frame_x1), r.frame_x0 + 0.030)
    ):
        part.visual(
            Box((0.060, 2.0 * r.rail_y_out, h)),
            origin=Origin(xyz=(cx, 0.0, zc)),
            material=mats["frame"],
            name=f"chassis__box_rail_deck__cross_member_{idx}", material_class_id="metal.paint_coated",
        )


def _chassis_tube_frame_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """002 fork: bent tubular steel rails with a wrap-around nose loop."""
    zc = 0.5 * (r.rail_z0 + r.rail_z1)
    for idx, side in enumerate((1.0, -1.0)):
        rail = [
            (r.frame_x0 + 0.010, side * (r.rail_y_out - 0.020), zc),
            (r.frame_x0 + 0.18, side * r.rail_y_out, zc + 0.006),
            (0.5 * (r.frame_x0 + r.frame_x1), side * r.rail_y_out, zc + 0.010),
            (r.axle_x, side * r.rail_y_out, zc),
            (r.frame_x1 - 0.010, side * (r.rail_y_out - 0.020), zc - 0.008),
        ]
        part.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    rail, radius=0.017, samples_per_segment=5, radial_segments=8
                ),
                f"chassis__tube_frame__side_rail_{idx}",
            ),
            material=mats["frame"],
            name=f"chassis__tube_frame__side_rail_{idx}", material_class_id="metal.paint_coated",
        )
        loop = [
            (r.frame_x1 - 0.010, side * (r.rail_y_out - 0.020), zc - 0.008),
            (r.frame_x1 + 0.055, side * (r.rail_y_out - 0.030), zc + 0.030),
            (r.frame_x1 + 0.030, side * (r.rail_y_out - 0.050), zc + 0.075),
            (r.axle_x + 0.040, side * (r.rail_y_out - 0.060), zc + 0.086),
        ]
        part.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    loop, radius=0.014, samples_per_segment=5, radial_segments=8
                ),
                f"chassis__tube_frame__nose_loop_{idx}",
            ),
            material=mats["frame"],
            name=f"chassis__tube_frame__nose_loop_{idx}", material_class_id="metal.paint_coated",
        )
    for idx, cx in enumerate((r.frame_x1 - 0.055, 0.5 * (r.frame_x0 + r.frame_x1))):
        part.visual(
            Cylinder(radius=0.015, length=2.0 * r.rail_y_out),
            origin=Origin(xyz=(cx, 0.0, zc), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["frame"],
            name=f"chassis__tube_frame__cross_tube_{idx}", material_class_id="metal.paint_coated",
        )
    part.visual(
        Box((0.090, 2.0 * r.rail_y_out, r.rail_z1 - r.rail_z0)),
        origin=Origin(xyz=(r.frame_x0 + 0.290, 0.0, zc)),
        material=mats["steel"],
        name="chassis__tube_frame__rear_channel", material_class_id="metal.steel_bare",
    )


def _chassis_fork_pockets_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """fork_pockets fork: two open-ended forklift tunnels tied by cross members."""
    zc = 0.5 * (r.rail_z0 + r.rail_z1)
    h = r.rail_z1 - r.rail_z0
    wall = 0.008
    pocket_half = 0.5 * (r.rail_y_out - r.rail_y_in) + 0.012
    pitch = 0.5 * (r.rail_y_in + r.rail_y_out)
    for idx, side in enumerate((1.0, -1.0)):
        cy = side * pitch
        length = r.frame_x1 - r.frame_x0
        cx = 0.5 * (r.frame_x0 + r.frame_x1)
        part.visual(
            Box((length, 2.0 * pocket_half, wall)),
            origin=Origin(xyz=(cx, cy, r.rail_z1 - 0.5 * wall)),
            material=mats["frame"],
            name=f"chassis__fork_pockets__pocket_top_{idx}", material_class_id="metal.paint_coated",
        )
        part.visual(
            Box((length, 2.0 * pocket_half, wall)),
            origin=Origin(xyz=(cx, cy, r.rail_z0 + 0.5 * wall)),
            material=mats["frame"],
            name=f"chassis__fork_pockets__pocket_bottom_{idx}", material_class_id="metal.paint_coated",
        )
        for wall_idx, wside in enumerate((1.0, -1.0)):
            part.visual(
                Box((length, wall, h)),
                origin=Origin(xyz=(cx, cy + wside * (pocket_half - 0.5 * wall), zc)),
                material=mats["frame"],
                name=f"chassis__fork_pockets__pocket_wall_{idx}_{wall_idx}", material_class_id="metal.paint_coated",
            )
    for idx, cx in enumerate(
        (r.frame_x1 - 0.045, 0.5 * (r.frame_x0 + r.frame_x1), r.frame_x0 + 0.030)
    ):
        part.visual(
            Box((0.060, 2.0 * r.rail_y_out, h)),
            origin=Origin(xyz=(cx, 0.0, zc)),
            material=mats["frame"],
            name=f"chassis__fork_pockets__cross_member_{idx}", material_class_id="metal.paint_coated",
        )


def _chassis_molded_underbody_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """003/004 frameless tier: a compact bolt-on subframe under the molded pan.

    Source: ``rec_urban_environment__tilt_truck2__003_png__claude_code``
    ``rev_000001`` -- ``RAIL_Z0/RAIL_Z1 = 0.165/0.215`` sits entirely below the
    ``MAIN_TIRE_R = 0.140`` wheel crown (0.280) and the ``Z_PAN = 0.270`` pan
    underside (``model.py:L54-L97``), and the weldment there is nothing but
    ``trunnion_upright_{i}`` / ``axle_housing_{i}`` / ``caster_pad_{i}`` /
    ``latch_cheek_{i}`` plus the rest pads (``model.py:L357-L419``).  There is
    no deck.  So this candidate drops the full-length side rails and the
    cross-member ladder entirely: two narrow longitudinal channels on a track
    inboard of the tub floor line, one caster crossbeam, one axle cradle, and
    nothing else.  The molded apron on the hopper covers the whole band.
    """
    zc = 0.5 * (r.rail_z0 + r.rail_z1)
    h = r.rail_z1 - r.rail_z0
    x_back = r.rear_beam_x
    x_front = r.frame_x1
    for idx, side in enumerate((1.0, -1.0)):
        part.visual(
            Box((x_front - x_back, 0.032, h)),
            origin=Origin(xyz=(0.5 * (x_back + x_front), side * r.spine_y, zc)),
            material=mats["steel"],
            name=f"chassis__molded_underbody__subframe_rail_{idx}", material_class_id="metal.steel_bare",
        )
    part.visual(
        Box((0.070, 2.0 * (r.spine_y + 0.030), h)),
        origin=Origin(xyz=(r.caster_x, 0.0, zc)),
        material=mats["steel"],
        name="chassis__molded_underbody__caster_crossbeam", material_class_id="metal.steel_bare",
    )
    part.visual(
        Box((0.085, 2.0 * (r.rail_y_out - 0.006), h)),
        origin=Origin(xyz=(r.axle_x, 0.0, zc)),
        material=mats["steel"],
        name="chassis__molded_underbody__axle_cradle", material_class_id="metal.steel_bare",
    )


_CHASSIS_BUILDERS = {
    "box_rail_deck": _chassis_box_rail_deck_build,
    "tube_frame": _chassis_tube_frame_build,
    "fork_pockets": _chassis_fork_pockets_build,
    "molded_underbody": _chassis_molded_underbody_build,
}


def _build_chassis(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    chassis = model.part("chassis", meta={"role": "chassis"})
    _CHASSIS_BUILDERS[r.chassis](chassis, r, mats)
    _chassis_common(chassis, r, mats)
    chassis.inertial = Inertial.from_geometry(
        Box((r.frame_x1 - r.frame_x0, 2.0 * r.rail_y_out, r.rail_z1 - r.rail_z0)),
        mass=46.0,
        origin=Origin(
            xyz=(0.5 * (r.frame_x0 + r.frame_x1), 0.0, 0.5 * (r.rail_z0 + r.rail_z1))
        ),
    )
    return chassis


# ---------------------------------------------------------------------------
# Joint helper
# ---------------------------------------------------------------------------


def _axis_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    joint_type: ArticulationType,
    lower: float | None = None,
    upper: float | None = None,
    effort: float = 60.0,
    velocity: float = 6.0,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=radial)
    mate = mate_axes(provider, consumer)
    limits = (
        MotionLimits(effort=effort, velocity=velocity)
        if lower is None
        else MotionLimits(effort=effort, velocity=velocity, lower=lower, upper=upper)
    )
    model.articulation(
        name,
        joint_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


# ---------------------------------------------------------------------------
# Running gear (shared identity core)
# ---------------------------------------------------------------------------


def _build_main_wheels(model, chassis, r: ResolvedConfig, mats: dict[str, str]) -> None:
    rad = r.main_wheel_radius_m
    hw = r.wheel_half_width
    tread = [
        (0.70 * rad, -hw + 0.004),
        (0.86 * rad, -hw),
        (0.96 * rad, -hw + 0.010),
        (rad, -hw + 0.020),
        (rad, hw - 0.020),
        (0.96 * rad, hw - 0.010),
        (0.86 * rad, hw),
        (0.70 * rad, hw - 0.004),
    ]
    disc = [
        (0.0, -0.55 * hw),
        (0.26 * rad, -0.72 * hw),
        (0.52 * rad, -0.48 * hw),
        (0.68 * rad, -0.88 * hw),
        (0.74 * rad, -0.74 * hw),
        (0.74 * rad, 0.74 * hw),
        (0.68 * rad, 0.88 * hw),
        (0.52 * rad, 0.48 * hw),
        (0.26 * rad, 0.72 * hw),
        (0.0, 0.55 * hw),
    ]
    for idx, side in enumerate((1.0, -1.0)):
        wheel = model.part(f"main_wheel_{idx}", meta={"role": "main_wheel", "index": idx})
        wheel.visual(
            _revolved_y(tread, f"main_wheel_{idx}_tire"),
            material=mats["tire"],
            name=f"main_wheel_{idx}_tire", material_class_id="rubber.smooth_plain",
        )
        wheel.visual(
            _revolved_y(disc, f"main_wheel_{idx}_rim", segments=24),
            material=mats["rim"],
            name=f"main_wheel_{idx}_rim", material_class_id="metal.paint_coated",
        )
        wheel.visual(
            Cylinder(radius=0.30 * rad, length=2.0 * (hw + MAIN_HUB_EXTEND)),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["rim"],
            name=f"main_wheel_{idx}_hub", material_class_id="metal.paint_coated",
        )
        wheel.inertial = Inertial.from_geometry(
            Cylinder(radius=rad, length=2.0 * hw),
            mass=5.0,
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        )
        _axis_joint(
            model,
            name=f"main_wheel_{idx}_roll",
            parent=chassis,
            child=wheel,
            point=(r.axle_x, side * r.wheel_y, rad),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            joint_type=ArticulationType.CONTINUOUS,
            effort=110.0,
            velocity=20.0,
        )


# ---------------------------------------------------------------------------
# caster candidates
# ---------------------------------------------------------------------------


def _caster_fork_common(fork, r: ResolvedConfig, mats: dict[str, str], kind: str) -> None:
    """Top swivel ring, kingpin and an offset fork with a real lateral wheel gap."""
    chw = r.caster_half_width
    leg_y = chw + 0.014
    leg_top = -0.006
    leg_bottom = r.caster_axle_local_z - 0.022
    leg_back = -r.caster_trail - (0.075 if kind == "braked_swivel" else 0.032)
    leg_front = -r.caster_trail + 0.030
    fork.visual(
        Cylinder(radius=0.040, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, -0.0075)),
        material=mats["zinc"],
        name=f"caster__{kind}__swivel_ring", material_class_id="metal.steel_galvanized",
    )
    fork.visual(
        Cylinder(radius=0.011, length=0.026 + LAP),
        origin=Origin(xyz=(0.0, 0.0, LAP - 0.5 * (0.026 + LAP))),
        material=mats["zinc"],
        name=f"caster__{kind}__kingpin", material_class_id="metal.steel_galvanized",
    )
    for leg, lside in enumerate((1.0, -1.0)):
        fork.visual(
            Box((leg_front - leg_back, 0.010, leg_top - leg_bottom)),
            origin=Origin(
                xyz=(
                    0.5 * (leg_back + leg_front),
                    lside * leg_y,
                    0.5 * (leg_top + leg_bottom),
                )
            ),
            material=mats["zinc"],
            name=f"caster__{kind}__fork_leg_{leg}", material_class_id="metal.steel_galvanized",
        )
        # stub axle: laps into the wheel hub boss by under the collision tolerance
        stub_lo = chw + CASTER_HUB_EXTEND - LAP
        stub_hi = leg_y + 0.006
        fork.visual(
            Cylinder(radius=0.009, length=stub_hi - stub_lo),
            origin=Origin(
                xyz=(-r.caster_trail, lside * 0.5 * (stub_lo + stub_hi), r.caster_axle_local_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["zinc"],
            name=f"caster__{kind}__fork_axle_{leg}", material_class_id="metal.steel_galvanized",
        )
    fork.inertial = Inertial.from_geometry(
        Box((0.11, 2.0 * leg_y, 0.11)),
        mass=1.1,
        origin=Origin(xyz=(-r.caster_trail, 0.0, 0.5 * (leg_top + leg_bottom))),
    )


def _caster_plain_swivel_build(model, chassis, fork, r, mats, idx: int, side: float) -> None:
    """004/003 baseline: plain bolt-on swivel caster, no brake."""
    _caster_fork_common(fork, r, mats, "plain_swivel")


def _caster_braked_swivel_build(model, chassis, fork, r, mats, idx: int, side: float) -> None:
    """caster_brake_pedals fork: a step-on brake treadle per caster.

    The treadle is one connected lever pinned between the (rearward-extended)
    fork legs: hub, twin arms, a shoe that settles onto the tyre crown at the
    applied stop, and a foot tab ahead of the shoe.  Its hub laps into each leg
    by less than the collision tolerance, so the hinge is real contact.
    """
    _caster_fork_common(fork, r, mats, "braked_swivel")
    chw = r.caster_half_width
    leg_y = chw + 0.014
    rad = r.caster_radius
    wheel_top = r.caster_axle_local_z + rad
    # the treadle pivots behind the tyre so the shoe drops radially onto its crown
    reach = rad + 0.022
    pivot = (-r.caster_trail - reach, 0.0, wheel_top + 0.024)

    brake = model.part(f"caster_brake_{idx}", meta={"role": "caster_brake", "index": idx})
    brake.visual(
        Cylinder(radius=0.008, length=2.0 * (leg_y - 0.005 + LAP)),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["zinc"],
        name=f"caster__braked_swivel__pedal_hub_{idx}", material_class_id="metal.steel_galvanized",
    )
    for arm, aside in enumerate((1.0, -1.0)):
        brake.visual(
            Box((reach + 0.030, 0.008, 0.010)),
            origin=Origin(xyz=(0.5 * (reach + 0.030), aside * (chw + 0.004), 0.0)),
            material=mats["steel"],
            name=f"caster__braked_swivel__brake_arm_{idx}_{arm}", material_class_id="metal.steel_bare",
        )
    brake.visual(
        Box((0.034, 2.0 * (chw + 0.006), 0.010)),
        origin=Origin(xyz=(reach, 0.0, 0.0)),
        material=mats["steel"],
        name=f"caster__braked_swivel__brake_shoe_{idx}", material_class_id="metal.steel_bare",
    )
    # raised tread lip: the step-on surface, kept clear of the swivel raceway
    brake.visual(
        Box((0.010, 2.0 * (chw + 0.006), 0.006)),
        origin=Origin(xyz=(reach - 0.014, 0.0, 0.006)),
        material=mats["frame"],
        name=f"caster__braked_swivel__foot_pad_{idx}", material_class_id="metal.paint_coated",
    )
    brake.inertial = Inertial.from_geometry(
        Box((reach + 0.040, 2.0 * (chw + 0.008), 0.03)),
        mass=0.22,
        origin=Origin(xyz=(0.5 * reach, 0.0, 0.0)),
    )
    _axis_joint(
        model,
        name=f"caster_brake_{idx}_pivot",
        parent=fork,
        child=brake,
        point=pivot,
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        joint_type=ArticulationType.REVOLUTE,
        lower=0.0,
        upper=BRAKE_MAX,
        effort=18.0,
        velocity=3.0,
    )


_CASTER_BUILDERS = {
    "plain_swivel": _caster_plain_swivel_build,
    "braked_swivel": _caster_braked_swivel_build,
}


def _build_casters(model, chassis, r: ResolvedConfig, mats: dict[str, str]) -> None:
    builder = _CASTER_BUILDERS[r.caster]
    rad = r.caster_radius
    chw = r.caster_half_width
    tread = [
        (0.62 * rad, -chw + 0.003),
        (0.82 * rad, -chw),
        (rad, -chw + 0.007),
        (rad, chw - 0.007),
        (0.82 * rad, chw),
        (0.62 * rad, chw - 0.003),
    ]
    boss = chw + CASTER_HUB_EXTEND
    core = [
        (0.0, -boss),
        (0.26 * rad, -boss),
        (0.40 * rad, -0.84 * chw),
        (0.62 * rad, -0.70 * chw),
        (0.62 * rad, 0.70 * chw),
        (0.40 * rad, 0.84 * chw),
        (0.26 * rad, boss),
        (0.0, boss),
    ]
    for idx, side in enumerate((1.0, -1.0)):
        fork = model.part(f"caster_fork_{idx}", meta={"role": "caster_fork", "index": idx})
        _axis_joint(
            model,
            name=f"caster_{idx}_swivel",
            parent=chassis,
            child=fork,
            point=(r.caster_x, side * r.caster_y, r.caster_swivel_z),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            joint_type=ArticulationType.CONTINUOUS,
            effort=25.0,
            velocity=12.0,
        )
        builder(model, chassis, fork, r, mats, idx, side)

        wheel = model.part(
            f"caster_wheel_{idx}", meta={"role": "caster_wheel", "index": idx}
        )
        wheel.visual(
            _revolved_y(tread, f"caster_wheel_{idx}_tread", segments=22),
            material=mats["caster_tread"],
            name=f"caster_wheel_{idx}_tread", material_class_id="rubber.smooth_plain",
        )
        wheel.visual(
            _revolved_y(core, f"caster_wheel_{idx}_core", segments=20),
            material=mats["rim"],
            name=f"caster_wheel_{idx}_core", material_class_id="metal.paint_coated",
        )
        wheel.inertial = Inertial.from_geometry(
            Cylinder(radius=rad, length=2.0 * chw),
            mass=0.55,
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        )
        _axis_joint(
            model,
            name=f"caster_{idx}_roll",
            parent=fork,
            child=wheel,
            point=(-r.caster_trail, 0.0, r.caster_axle_local_z),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            joint_type=ArticulationType.CONTINUOUS,
            effort=25.0,
            velocity=20.0,
        )


# ---------------------------------------------------------------------------
# latch candidates
# ---------------------------------------------------------------------------


def _latch_throat(part, r: ResolvedConfig, mats: dict[str, str], kind: str) -> None:
    """C-throat that captures the keeper bar with real clearance on three sides.

    The over-centre jaw swings a few degrees PAST the bar at its locked stop, so
    its throat is derived with a wider gap: the seat still clears the keeper at
    the negative limit instead of clamping through it.
    """
    dx, dz = r.latch_dx, r.latch_dz
    t = 2.0 * LATCH_PLATE_HALF
    gap = OVERCENTRE_THROAT_GAP if kind == "overcenter_side_lever" else THROAT_GAP
    off = KEEPER_R + gap
    # seat and claw run back to the web face so the C is one connected stamping
    x0 = dx - off - 0.004
    x1 = dx + 0.015
    lip_len = x1 - x0
    lip_cx = 0.5 * (x0 + x1)
    part.visual(
        Box((lip_len, t, 0.008)),
        origin=Origin(xyz=(lip_cx, 0.0, dz - off)),
        material=mats["zinc"],
        name=f"latch__{kind}__throat_seat", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Box((lip_len, t, 0.008)),
        origin=Origin(xyz=(lip_cx, 0.0, dz + off)),
        material=mats["zinc"],
        name=f"latch__{kind}__throat_claw", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Box((0.008, t, 2.0 * (off + 0.004))),
        origin=Origin(xyz=(dx - off, 0.0, dz)),
        material=mats["zinc"],
        name=f"latch__{kind}__throat_web", material_class_id="metal.steel_galvanized",
    )


def _latch_shank(part, r: ResolvedConfig, mats: dict[str, str], name: str, thick: float) -> None:
    """Plate shank from the pivot up to the throat web, stopping short of the bar."""
    dx, dz = r.latch_dx, r.latch_dz
    reach = math.hypot(dx, dz)
    length = max(0.020, reach - (KEEPER_R + 0.012))
    ang = math.atan2(dz, dx)
    cx = 0.5 * length * math.cos(ang)
    cz = 0.5 * length * math.sin(ang)
    part.visual(
        Box((length, 2.0 * LATCH_PLATE_HALF, thick)),
        origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, -ang, 0.0)),
        material=mats["zinc"],
        name=name, material_class_id="metal.steel_galvanized",
    )


def _latch_barrel(part, r: ResolvedConfig, mats: dict[str, str], kind: str) -> None:
    part.visual(
        Cylinder(radius=0.016, length=2.0 * (0.014 + LAP)),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["zinc"],
        name=f"latch__{kind}__pivot_barrel", material_class_id="metal.steel_galvanized",
    )


def _latch_gravity_hook_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """002/003 baseline: bent steel rod hook hanging on the frame hinge pin."""
    dx, dz = r.latch_dx, r.latch_dz
    _latch_barrel(part, r, mats, "gravity_hook")
    path = [
        (0.0, 0.0, 0.010),
        (0.30 * dx, 0.0, 0.34 * dz),
        (0.66 * dx, 0.0, 0.68 * dz),
        (dx - KEEPER_R - THROAT_GAP, 0.0, dz),
    ]
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                path, radius=0.0065, samples_per_segment=5, radial_segments=8
            ),
            "latch__gravity_hook__shank_rod",
        ),
        material=mats["zinc"],
        name="latch__gravity_hook__shank_rod", material_class_id="metal.steel_galvanized",
    )
    _latch_throat(part, r, mats, "gravity_hook")


def _latch_c_throat_claw_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """004 baseline: flat stamped C-throat plate hook with a release tang."""
    _latch_barrel(part, r, mats, "c_throat_claw")
    _latch_shank(part, r, mats, "latch__c_throat_claw__plate_shank", 0.024)
    part.visual(
        Box((0.052, 2.0 * LATCH_PLATE_HALF, 0.016)),
        origin=Origin(xyz=(-0.034, 0.0, 0.006), rpy=(0.0, 0.42, 0.0)),
        material=mats["zinc"],
        name="latch__c_throat_claw__release_tang", material_class_id="metal.steel_galvanized",
    )
    _latch_throat(part, r, mats, "c_throat_claw")


def _latch_overcenter_side_lever_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """overcenter fork: side hand lever whose jaw clamps the catch bar over centre."""
    _latch_barrel(part, r, mats, "overcenter_side_lever")
    _latch_shank(part, r, mats, "latch__overcenter_side_lever__jaw_arm", 0.022)
    grip_path = [
        (-0.008, 0.0, 0.008),
        (-0.060, 0.0, 0.052),
        (-0.098, 0.0, 0.108),
        (-0.104, 0.0, 0.168),
    ]
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                grip_path, radius=0.010, samples_per_segment=5, radial_segments=8
            ),
            "latch__overcenter_side_lever__lever_arm",
        ),
        material=mats["zinc"],
        name="latch__overcenter_side_lever__lever_arm", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Cylinder(radius=0.015, length=0.100),
        origin=Origin(xyz=(-0.104, -0.050, 0.168), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="latch__overcenter_side_lever__hand_grip", material_class_id="metal.paint_coated",
    )
    _latch_throat(part, r, mats, "overcenter_side_lever")


def _latch_foot_pedal_release_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """foot_pedal fork: the C-throat hook plus a rearward tail the pedal rod pushes."""
    _latch_barrel(part, r, mats, "foot_pedal_release")
    _latch_shank(part, r, mats, "latch__foot_pedal_release__plate_shank", 0.024)
    part.visual(
        Box((0.072, 2.0 * LATCH_PLATE_HALF, 0.016)),
        origin=Origin(xyz=(-0.026, 0.0, 0.012), rpy=(0.0, 0.34, 0.0)),
        material=mats["zinc"],
        name="latch__foot_pedal_release__tail_arm", material_class_id="metal.steel_galvanized",
    )
    part.visual(
        Cylinder(radius=0.009, length=0.024),
        origin=Origin(xyz=(-0.060, 0.0, 0.024), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["zinc"],
        name="latch__foot_pedal_release__tail_pad", material_class_id="metal.steel_galvanized",
    )
    _latch_throat(part, r, mats, "foot_pedal_release")


_LATCH_BUILDERS = {
    "gravity_hook": _latch_gravity_hook_build,
    "c_throat_claw": _latch_c_throat_claw_build,
    "overcenter_side_lever": _latch_overcenter_side_lever_build,
    "foot_pedal_release": _latch_foot_pedal_release_build,
}


def _build_latch(model, chassis, r: ResolvedConfig, mats: dict[str, str]) -> None:
    latch = model.part("latch", meta={"role": "latch"})
    _LATCH_BUILDERS[r.latch](latch, r, mats)
    latch.inertial = Inertial.from_geometry(
        Box((0.16, 0.03, 0.14)), mass=0.6, origin=Origin(xyz=(0.04, 0.0, 0.03))
    )
    _axis_joint(
        model,
        name="latch_pivot",
        parent=chassis,
        child=latch,
        point=(r.latch_pivot_x, r.latch_pivot_y, r.latch_pivot_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        joint_type=ArticulationType.REVOLUTE,
        lower=r.latch_lower,
        upper=r.latch_upper,
        effort=30.0,
        velocity=3.0,
    )

    if r.latch != "foot_pedal_release":
        return

    # Foot pedal release linkage: its own link, boss and push rod on the chassis.
    boss_in = 0.040
    boss_out = 0.056
    pivot = (r.rear_beam_x - 0.055, 0.5 * (boss_in + boss_out), r.rail_z1 + 0.030)
    chassis.visual(
        Cylinder(radius=0.014, length=boss_out - boss_in),
        origin=Origin(xyz=pivot, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="latch__foot_pedal_release__pedal_boss", material_class_id="metal.steel_bare",
    )
    bracket_z0 = r.rail_z1 - 0.006
    bracket_z1 = pivot[2] + 0.010
    chassis.visual(
        Box((0.075, boss_out - boss_in, bracket_z1 - bracket_z0)),
        origin=Origin(
            xyz=(
                pivot[0] + 0.030,
                0.5 * (boss_in + boss_out),
                0.5 * (bracket_z0 + bracket_z1),
            )
        ),
        material=mats["steel"],
        name="latch__foot_pedal_release__pedal_bracket", material_class_id="metal.steel_bare",
    )
    pedal = model.part("release_pedal", meta={"role": "release_pedal"})

    def p_cyl(name, radius, y0, y1, xz, material):
        pedal.visual(
            Cylinder(radius=radius, length=abs(y1 - y0)),
            origin=Origin(xyz=(xz[0], 0.5 * (y0 + y1), xz[1]), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=material,
            name=name, material_class_id="metal.steel_galvanized",
        )

    def p_box(name, size_xz, y0, y1, xz, material, rpy=(0.0, 0.0, 0.0)):
        pedal.visual(
            Box((size_xz[0], abs(y1 - y0), size_xz[1])),
            origin=Origin(xyz=(xz[0], 0.5 * (y0 + y1), xz[1]), rpy=rpy),
            material=material,
            name=name, material_class_id="metal.paint_coated",
        )

    body_y0 = -(0.008 + 0.014)
    body_y1 = -0.008
    p_cyl(
        "latch__foot_pedal_release__pedal_pin",
        0.007,
        -(0.008 + 0.026),
        -(0.008 - LAP),
        (0.0, 0.0),
        mats["zinc"],
    )
    p_cyl(
        "latch__foot_pedal_release__pedal_hub", 0.016, body_y0, body_y1, (0.0, 0.0), mats["steel"]
    )
    p_box(
        "latch__foot_pedal_release__pedal_arm",
        (0.129, 0.014),
        body_y0,
        body_y1,
        (-0.062, -0.018),
        mats["steel"],
        rpy=(0.0, -0.283, 0.0),
    )
    p_box(
        "latch__foot_pedal_release__foot_pad",
        (0.086, 0.012),
        body_y0 - 0.026,
        body_y1 + 0.026,
        (-0.134, -0.040),
        mats["frame"],
    )
    # push rod reaching forward to the latch tail pad
    p_box(
        "latch__foot_pedal_release__push_rod",
        (0.058, 0.010),
        body_y0,
        body_y1,
        (0.019, 0.011),
        mats["zinc"],
        rpy=(0.0, -0.54, 0.0),
    )
    pedal.inertial = Inertial.from_geometry(
        Box((0.22, 0.06, 0.06)), mass=0.6, origin=Origin(xyz=(-0.09, -0.015, -0.02))
    )
    _axis_joint(
        model,
        name="release_pedal_pivot",
        parent=chassis,
        child=pedal,
        point=pivot,
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        joint_type=ArticulationType.REVOLUTE,
        lower=0.0,
        upper=PEDAL_MAX,
        effort=40.0,
        velocity=3.0,
    )


# ---------------------------------------------------------------------------
# push_handle candidates
# ---------------------------------------------------------------------------


def _handle_feet(part, r: ResolvedConfig, mats: dict[str, str], kind: str) -> None:
    """Two mount feet lapping the chassis rear outrigger beam by under the tolerance."""
    for idx, side in enumerate((1.0, -1.0)):
        part.visual(
            Box((0.070, 0.070, 0.016)),
            origin=Origin(xyz=(0.0, side * r.handle_y, 0.008 - LAP)),
            material=mats["frame"],
            name=f"push_handle__{kind}__mount_foot_{idx}", material_class_id="metal.paint_coated",
        )


def _push_handle_rear_loop_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """004/001 baseline: tubular U hoop rising past the rim at the push end."""
    _handle_feet(part, r, mats, "rear_loop")
    top = r.handle_top_z - r.rail_z1
    loop = [
        (0.0, r.handle_y, 0.014),
        (-0.010, r.handle_y, 0.45 * top),
        (-0.014, r.handle_y, 0.88 * top),
        (-0.010, 0.62 * r.handle_y, top),
        (0.0, 0.0, top + 0.014),
        (-0.010, -0.62 * r.handle_y, top),
        (-0.014, -r.handle_y, 0.88 * top),
        (-0.010, -r.handle_y, 0.45 * top),
        (0.0, -r.handle_y, 0.014),
    ]
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(loop, radius=0.019, samples_per_segment=6, radial_segments=8),
            "push_handle__rear_loop__hoop_tube",
        ),
        material=mats["frame"],
        name="push_handle__rear_loop__hoop_tube", material_class_id="metal.paint_coated",
    )
    for idx, zf in enumerate((0.52, 0.78)):
        part.visual(
            Cylinder(radius=0.015, length=2.0 * (r.handle_y + 0.012)),
            origin=Origin(xyz=(-0.012, 0.0, zf * top), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["frame"],
            name=f"push_handle__rear_loop__rung_{idx}", material_class_id="metal.paint_coated",
        )


def _push_handle_side_rails_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """003 fork: longitudinal side grab rails on braced posts, no rear hoop."""
    _handle_feet(part, r, mats, "side_rails")
    grip_z = r.floor_z + 0.62 * r.hopper_depth_m - r.rail_z1
    reach = 0.42 * r.hopper_length_m
    for idx, side in enumerate((1.0, -1.0)):
        post = [
            (0.0, side * r.handle_y, 0.014),
            (0.010, side * r.handle_y, 0.55 * grip_z),
            (0.030, side * r.handle_y, grip_z),
        ]
        part.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    post, radius=0.017, samples_per_segment=5, radial_segments=8
                ),
                f"push_handle__side_rails__post_{idx}",
            ),
            material=mats["frame"],
            name=f"push_handle__side_rails__post_{idx}", material_class_id="metal.paint_coated",
        )
        rail = [
            (0.010, side * r.handle_y, grip_z - 0.010),
            (0.5 * reach, side * r.handle_y, grip_z + 0.006),
            (reach, side * r.handle_y, grip_z - 0.010),
        ]
        part.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    rail, radius=0.016, samples_per_segment=6, radial_segments=8
                ),
                f"push_handle__side_rails__grab_rail_{idx}",
            ),
            material=mats["frame"],
            name=f"push_handle__side_rails__grab_rail_{idx}", material_class_id="metal.paint_coated",
        )
        brace = [
            (0.020, side * r.handle_y, 0.30 * grip_z),
            (0.5 * reach, side * r.handle_y, grip_z - 0.006),
        ]
        part.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    brace, radius=0.012, samples_per_segment=4, radial_segments=8
                ),
                f"push_handle__side_rails__brace_{idx}",
            ),
            material=mats["frame"],
            name=f"push_handle__side_rails__brace_{idx}", material_class_id="metal.paint_coated",
        )
    # rear U tie: wraps behind the tub and joins the two side rails into one
    # grab frame (without it the left and right assemblies are separate islands)
    tie = [
        (0.028, r.handle_y, grip_z - 0.002),
        (-0.026, r.handle_y, grip_z + 0.004),
        (-0.040, 0.0, grip_z + 0.006),
        (-0.026, -r.handle_y, grip_z + 0.004),
        (0.028, -r.handle_y, grip_z - 0.002),
    ]
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(tie, radius=0.016, samples_per_segment=6, radial_segments=8),
            "push_handle__side_rails__rear_tie",
        ),
        material=mats["frame"],
        name="push_handle__side_rails__rear_tie", material_class_id="metal.paint_coated",
    )


def _push_handle_folding_hoop_build(part, r: ResolvedConfig, mats: dict[str, str]) -> None:
    """handle_folding fork: the same hoop on hinge stubs so it folds down flat."""
    top = r.handle_top_z - r.handle_hinge_z
    loop = [
        (0.0, r.handle_y, 0.0),
        (-0.010, r.handle_y, 0.45 * top),
        (-0.014, r.handle_y, 0.88 * top),
        (-0.010, 0.62 * r.handle_y, top),
        (0.0, 0.0, top + 0.014),
        (-0.010, -0.62 * r.handle_y, top),
        (-0.014, -r.handle_y, 0.88 * top),
        (-0.010, -r.handle_y, 0.45 * top),
        (0.0, -r.handle_y, 0.0),
    ]
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(loop, radius=0.019, samples_per_segment=6, radial_segments=8),
            "push_handle__folding_hoop__hoop_tube",
        ),
        material=mats["frame"],
        name="push_handle__folding_hoop__hoop_tube", material_class_id="metal.paint_coated",
    )
    part.visual(
        Cylinder(radius=0.015, length=2.0 * (r.handle_y + 0.012)),
        origin=Origin(xyz=(-0.012, 0.0, 0.62 * top), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["frame"],
        name="push_handle__folding_hoop__rung_0", material_class_id="metal.paint_coated",
    )
    for idx, side in enumerate((1.0, -1.0)):
        stub_lo = r.handle_y - 0.026
        stub_hi = r.handle_y + 0.020 + LAP
        part.visual(
            Cylinder(radius=0.011, length=stub_hi - stub_lo),
            origin=Origin(
                xyz=(0.0, side * 0.5 * (stub_lo + stub_hi), 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["zinc"],
            name=f"push_handle__folding_hoop__hinge_stub_{idx}", material_class_id="metal.steel_galvanized",
        )


_HANDLE_BUILDERS = {
    "rear_loop": _push_handle_rear_loop_build,
    "side_rails": _push_handle_side_rails_build,
    "folding_hoop": _push_handle_folding_hoop_build,
}


def _build_push_handle(model, chassis, r: ResolvedConfig, mats: dict[str, str]) -> None:
    handle = model.part("push_handle", meta={"role": "push_handle"})
    _HANDLE_BUILDERS[r.push_handle](handle, r, mats)
    handle.inertial = Inertial.from_geometry(
        Box((0.10, 2.0 * r.handle_y, 0.60)), mass=5.5, origin=Origin(xyz=(0.0, 0.0, 0.20))
    )
    if r.push_handle == "folding_hoop":
        # chassis hinge clevis: two barrels the handle stubs journal into
        for idx, side in enumerate((1.0, -1.0)):
            chassis.visual(
                Box((0.046, 0.028, r.handle_hinge_z - r.rail_z1 + 0.030)),
                origin=Origin(
                    xyz=(
                        r.handle_x,
                        side * (r.handle_y + 0.034),
                        0.5 * (r.rail_z1 + r.handle_hinge_z + 0.030),
                    )
                ),
                material=mats["frame"],
                name=f"push_handle__folding_hoop__hinge_barrel_{idx}", material_class_id="metal.paint_coated",
            )
        _axis_joint(
            model,
            name="push_handle_fold",
            parent=chassis,
            child=handle,
            point=(r.handle_x, 0.0, r.handle_hinge_z),
            axis=(0.0, -1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            joint_type=ArticulationType.REVOLUTE,
            lower=0.0,
            upper=HANDLE_FOLD_MAX,
            effort=35.0,
            velocity=2.5,
        )
    else:
        model.articulation(
            "push_handle_mount",
            ArticulationType.FIXED,
            parent=chassis,
            child=handle,
            origin=Origin(xyz=(r.handle_x, r.handle_y, r.rail_z1)),
        )
        # the FIXED origin also places the child: re-express its local geometry
        for element in handle.visuals:
            x, y, z = element.origin.xyz
            element.origin = Origin(xyz=(x, y - r.handle_y, z), rpy=element.origin.rpy)
        handle.inertial = Inertial.from_geometry(
            Box((0.10, 2.0 * r.handle_y, 0.60)),
            mass=5.5,
            origin=Origin(xyz=(0.0, -r.handle_y, 0.20)),
        )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        name = f"tilt_truck2_{r.palette_style}_{key}"
        model.material(name, rgba=rgba)
        mats[key] = name
    return mats


def build_urban_environment_tilt_truck2(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "Urban_Environment_Tilt_Truck2",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "trunnion tilt hopper + retaining latch on a four-point rolling chassis",
        },
    )
    mats = _materials(model, r)
    chassis = _build_chassis(model, r, mats)
    hopper, cavity_volume, shell_volume = _build_hopper(model, r, mats)
    model.meta["hopper_cavity_volume_m3"] = cavity_volume
    model.meta["hopper_shell_volume_m3"] = shell_volume

    _axis_joint(
        model,
        name="hopper_tilt",
        parent=chassis,
        child=hopper,
        point=(r.trunnion_x, 0.0, r.trunnion_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        joint_type=ArticulationType.REVOLUTE,
        lower=0.0,
        upper=r.tilt_max_rad,
        effort=900.0,
        velocity=1.2,
    )

    _build_main_wheels(model, chassis, r, mats)
    _build_casters(model, chassis, r, mats)
    _build_latch(model, chassis, r, mats)
    _build_push_handle(model, chassis, r, mats)

    # Real operation order: the hopper only tilts once the latch is released, and
    # the foot pedal only travels while the latch it drives is released.
    interlocks = [
        {
            "controller_joint": "latch_pivot",
            "controller_required_position": r.latch_upper,
            "dependent_joints": ["hopper_tilt"],
        }
    ]
    if r.latch == "foot_pedal_release":
        interlocks[0]["dependent_joints"] = ["hopper_tilt", "release_pedal_pivot"]
    model.meta["motion_interlocks"] = tuple(interlocks)

    risk_open = {"latch_pivot": r.latch_upper, "hopper_tilt": r.tilt_max_rad}
    risk_closed = {"latch_pivot": r.latch_lower, "hopper_tilt": 0.0}
    model.meta["risk_poses"] = (risk_closed, risk_open)
    model.meta["coupled_joint_pairs"] = (("latch_pivot", "hopper_tilt"),)
    return model


def build_seeded_urban_environment_tilt_truck2(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_urban_environment_tilt_truck2(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Authored tests
# ---------------------------------------------------------------------------


def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def _expect_touch(ctx, part_a, elem_a, part_b, elem_b, *, tol: float, name: str) -> bool:
    """Assert two named elements touch, using world AABBs on every axis.

    AABB separation keeps this check available in the preflight probe context
    (which defers exact mesh work) while still proving real seated contact:
    the boxes must not be further apart than ``tol`` on any axis.
    """
    box_a = ctx.part_element_world_aabb(part_a, elem=elem_a)
    box_b = ctx.part_element_world_aabb(part_b, elem=elem_b)
    if box_a is None or box_b is None:
        return ctx.check(name, False, details=f"missing aabb a={box_a} b={box_b}")
    gaps = [
        max(box_a[0][axis] - box_b[1][axis], box_b[0][axis] - box_a[1][axis])
        for axis in range(3)
    ]
    return ctx.check(
        name,
        max(gaps) <= tol,
        details=f"axis gaps={[round(g, 5) for g in gaps]} tol={tol} a={box_a} b={box_b}",
    )


def run_urban_environment_tilt_truck2_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    # Covers the rest pose AND every sampled motion pose, so it subsumes a
    # rest-pose-only gate.  Deferred by the preflight probe context (no exact
    # collision geometry there) and executed for real in random/corner sweep.
    ctx.fail_if_parts_overlap_in_sampled_poses()

    joints = {j.name: j for j in model.articulations}
    tilt = joints.get("hopper_tilt")
    latch_joint = joints.get("latch_pivot")
    hopper = model.get_part("hopper")
    chassis = model.get_part("chassis")

    main_wheels = _parts_by_role(model, "main_wheel")
    forks = _parts_by_role(model, "caster_fork")
    caster_wheels = _parts_by_role(model, "caster_wheel")
    handles = _parts_by_role(model, "push_handle")
    latches = _parts_by_role(model, "latch")

    def _rot_y(joint) -> bool:
        return (
            joint is not None
            and tuple(round(abs(v), 6) for v in joint.axis) == (0.0, 1.0, 0.0)
        )

    # --- category anchor: the tilting hopper on its trunnion -----------------
    ctx.check(
        "category_anchor: tilting hopper on a trunnion axis",
        len(_parts_by_role(model, "hopper")) == 1
        and len(_parts_by_role(model, "chassis")) == 1
        and model.root_parts()
        and model.root_parts()[0].name == "chassis"
        and tilt is not None
        and tilt.articulation_type == ArticulationType.REVOLUTE
        and _rot_y(tilt)
        and tilt.parent == "chassis"
        and tilt.motion_limits is not None
        and abs(float(tilt.motion_limits.lower)) < 1e-9
        and 0.85 <= float(tilt.motion_limits.upper) <= 1.25,
        details=f"tilt={tilt}",
    )

    # --- category anchor: the retaining latch --------------------------------
    keeper = ctx.part_element_world_aabb(hopper, elem="latch_keeper_bar")
    claw_elem = f"latch__{r.latch}__throat_claw"
    claw_closed = ctx.part_element_world_aabb(latches[0], elem=claw_elem)
    with ctx.pose({latch_joint: r.latch_upper}):
        claw_open = ctx.part_element_world_aabb(latches[0], elem=claw_elem)
    ctx.check(
        "category_anchor: retaining latch captures the hopper keeper",
        len(latches) == 1
        and latch_joint is not None
        and latch_joint.articulation_type == ArticulationType.REVOLUTE
        and _rot_y(latch_joint)
        and latch_joint.parent == "chassis"
        and keeper is not None
        and claw_closed is not None
        and claw_open is not None
        # closed: the claw lip sits directly over the keeper bar
        and claw_closed[0][0] < 0.5 * (keeper[0][0] + keeper[1][0]) < claw_closed[1][0]
        and claw_closed[0][2] >= keeper[1][2] - 0.004
        # released: the claw has dropped clear of the keeper
        and claw_open[1][2] < keeper[0][2] - 0.030,
        details=f"keeper={keeper} closed={claw_closed} open={claw_open}",
    )

    # --- category anchor: hollow open-top molded tub -------------------------
    cavity = float(model.meta.get("hopper_cavity_volume_m3", 0.0))
    shell = float(model.meta.get("hopper_shell_volume_m3", 0.0))
    ctx.check(
        "category_anchor: hollow open-top molded tub",
        cavity > 0.20
        and shell > 0.0
        and shell / (shell + cavity) < 0.22
        and 0.008 <= WALL_T <= 0.016,
        details=f"cavity={cavity:.4f} m3 shell={shell:.4f} m3 wall={WALL_T}",
    )

    # --- category anchor: four-point rolling stance --------------------------
    boxes = [ctx.part_world_aabb(p) for p in main_wheels + caster_wheels]
    ok_stance = len(main_wheels) == 2 and len(forks) == 2 and len(caster_wheels) == 2
    if ok_stance and all(b is not None for b in boxes):
        ok_stance = all(abs(float(b[0][2])) <= 0.005 for b in boxes)
    for idx in (0, 1):
        roll = joints.get(f"main_wheel_{idx}_roll")
        swivel = joints.get(f"caster_{idx}_swivel")
        croll = joints.get(f"caster_{idx}_roll")
        ok_stance = (
            ok_stance
            and roll is not None
            and roll.articulation_type == ArticulationType.CONTINUOUS
            and _rot_y(roll)
            and swivel is not None
            and swivel.articulation_type == ArticulationType.CONTINUOUS
            and tuple(round(abs(v), 6) for v in swivel.axis) == (0.0, 0.0, 1.0)
            and croll is not None
            and croll.articulation_type == ArticulationType.CONTINUOUS
            and _rot_y(croll)
            and croll.parent == f"caster_fork_{idx}"
        )
    ctx.check(
        "category_anchor: four-point rolling stance",
        ok_stance,
        details=f"wheel boxes={boxes}",
    )

    # --- category anchor: push handle ----------------------------------------
    handle_box = ctx.part_world_aabb(handles[0]) if handles else None
    ctx.check(
        "category_anchor: push handle at the push end",
        len(handles) == 1
        and handle_box is not None
        and float(handle_box[0][0]) < r.x_rim_rear + 0.35 * r.hopper_length_m
        and float(handle_box[1][1] - handle_box[0][1]) > 0.35,
        details=f"handle={handle_box}",
    )

    # --- category anchor: deck bearers ---------------------------------------
    bearer_boxes = [
        ctx.part_element_world_aabb(chassis, elem=f"chassis__{r.chassis}__deck_bearer_{i}")
        for i in range(r.deck_bearer_count)
    ]
    ctx.check(
        "category_anchor: deck bearers span the tub floor",
        all(b is not None for b in bearer_boxes)
        and all(
            r.x_floor_rear - 0.02 <= 0.5 * (b[0][0] + b[1][0]) <= r.x_floor_front + 0.02
            for b in bearer_boxes
        )
        and all(float(b[1][1] - b[0][1]) > 0.9 * r.hopper_width_m * 0.6 for b in bearer_boxes),
        details=f"bearers={bearer_boxes}",
    )

    # --- slot identity checks -------------------------------------------------
    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    ctx.check(
        "category_anchor: hopper_form identity",
        f"hopper_form__{r.hopper_form}__tub_shell" in visual_names,
        details=f"hopper_form={r.hopper_form}",
    )
    latch_marker = {
        "gravity_hook": "latch__gravity_hook__shank_rod",
        "c_throat_claw": "latch__c_throat_claw__release_tang",
        "overcenter_side_lever": "latch__overcenter_side_lever__hand_grip",
        "foot_pedal_release": "latch__foot_pedal_release__foot_pad",
    }[r.latch]
    ctx.check(
        "category_anchor: latch identity",
        latch_marker in visual_names
        and (r.latch != "foot_pedal_release" or len(_parts_by_role(model, "release_pedal")) == 1)
        and (
            r.latch != "overcenter_side_lever"
            or (latch_joint is not None and float(latch_joint.motion_limits.lower) < 0.0)
        ),
        details=f"latch={r.latch} marker={latch_marker}",
    )
    handle_marker = {
        "rear_loop": "push_handle__rear_loop__hoop_tube",
        "side_rails": "push_handle__side_rails__grab_rail_0",
        "folding_hoop": "push_handle__folding_hoop__hoop_tube",
    }[r.push_handle]
    ctx.check(
        "category_anchor: push_handle identity",
        handle_marker in visual_names
        and (
            (r.push_handle == "folding_hoop") == ("push_handle_fold" in joints)
        ),
        details=f"push_handle={r.push_handle}",
    )
    chassis_marker = {
        "box_rail_deck": "chassis__box_rail_deck__side_rail_0",
        "tube_frame": "chassis__tube_frame__nose_loop_0",
        "fork_pockets": "chassis__fork_pockets__pocket_top_0",
        "molded_underbody": "chassis__molded_underbody__subframe_rail_0",
    }[r.chassis]
    ctx.check(
        "category_anchor: chassis identity",
        chassis_marker in visual_names
        and (r.chassis == "molded_underbody")
        == (f"hopper_form__{r.hopper_form}__underbody_apron_0" in visual_names),
        details=f"chassis={r.chassis}",
    )

    # --- chassis visual tier: framed ladder vs molded frameless underbody -----
    chassis_box = ctx.part_world_aabb(chassis)
    if r.chassis == "molded_underbody":
        aprons = [
            ctx.part_element_world_aabb(
                hopper, elem=f"hopper_form__{r.hopper_form}__underbody_apron_{i}"
            )
            for i in (0, 1)
        ]
        detail = f"aprons={aprons}"
        ok_tier = all(b is not None for b in aprons)
        if ok_tier:
            # the apron is a thin molded wall spanning the whole subframe band
            for b in aprons:
                ok_tier = (
                    ok_tier
                    and float(b[0][2]) <= r.rail_z0 + 0.002
                    and float(b[1][2]) >= r.floor_z - 0.002
                )
            apron_in = min(
                min(abs(float(b[0][1])), abs(float(b[1][1]))) for b in aprons
            )
            apron_x_lo = min(float(b[0][0]) for b in aprons)
            apron_x_hi = max(float(b[1][0]) for b in aprons)
            # nothing the chassis carries inside the apron's shadow reaches
            # outboard of its inner face, so the side view reads frameless
            proud = []
            for element in chassis.visuals:
                box = ctx.part_element_world_aabb(chassis, elem=element.name)
                if box is None:
                    continue
                if float(box[1][0]) < apron_x_lo or float(box[0][0]) > apron_x_hi:
                    continue
                if float(box[1][2]) < r.skirt_z0 or float(box[0][2]) > r.floor_z:
                    continue
                if max(abs(float(box[0][1])), abs(float(box[1][1]))) > apron_in + 1e-6:
                    proud.append(element.name)
            ok_tier = ok_tier and not proud
            detail = (
                f"apron_in={apron_in:.4f} x=[{apron_x_lo:.3f},{apron_x_hi:.3f}] "
                f"proud={proud}"
            )
        ctx.check(
            "chassis under-structure matches its declared visual tier",
            ok_tier,
            details=detail,
        )
    else:
        ctx.check(
            "chassis under-structure matches its declared visual tier",
            chassis_box is not None
            and float(chassis_box[1][0] - chassis_box[0][0]) >= 0.95 * r.hopper_length_m,
            details=f"framed chassis span={chassis_box}",
        )
    ctx.check(
        "category_anchor: caster identity",
        (f"caster__{r.caster}__swivel_ring" in visual_names)
        and (
            (r.caster == "braked_swivel") == (len(_parts_by_role(model, "caster_brake")) == 2)
        ),
        details=f"caster={r.caster}",
    )

    # --- mechanism evidence: dumping ------------------------------------------
    rest = ctx.part_world_aabb(hopper)
    with ctx.pose({latch_joint: r.latch_upper, tilt: 0.5 * r.tilt_max_rad}):
        mid = ctx.part_world_aabb(hopper)
    with ctx.pose({latch_joint: r.latch_upper, tilt: r.tilt_max_rad}):
        dumped = ctx.part_world_aabb(hopper)
    ctx.check(
        "tilting drives the discharge lip forward and down while the tail rises",
        rest is not None
        and mid is not None
        and dumped is not None
        and float(dumped[1][0]) > float(mid[1][0]) > float(rest[1][0]) + 0.05
        and float(dumped[1][2]) > float(mid[1][2]) > float(rest[1][2]) + 0.05
        and float(dumped[0][2]) > 0.02,
        details=f"rest={rest} mid={mid} dumped={dumped}",
    )

    # --- mechanism evidence: the tub really rests on every bearer -------------
    tub_elem = f"hopper_form__{r.hopper_form}__tub_shell"
    for i in range(r.deck_bearer_count):
        _expect_touch(
            ctx,
            hopper,
            tub_elem,
            chassis,
            f"chassis__{r.chassis}__deck_bearer_{i}",
            tol=0.004,
            name=f"tub floor seats on deck bearer {i}",
        )

    # --- mechanism evidence: trunnion engagement ------------------------------
    for idx in (0, 1):
        _expect_touch(
            ctx,
            hopper,
            f"trunnion_pin_{idx}",
            chassis,
            f"trunnion_hub_{idx}",
            tol=0.003,
            name=f"trunnion pin {idx} runs in its frame bearing hub",
        )
        ctx.expect_within(
            hopper,
            chassis,
            axes="xz",
            inner_elem=f"trunnion_pin_{idx}",
            outer_elem=f"trunnion_hub_{idx}",
            margin=0.001,
            name=f"trunnion pin {idx} is concentric with its hub",
        )

    # --- mechanism evidence: casters swivel about their kingpins --------------
    for idx in (0, 1):
        swivel = joints[f"caster_{idx}_swivel"]
        p0 = ctx.part_world_position(caster_wheels[idx])
        with ctx.pose({swivel: math.pi}):
            p180 = ctx.part_world_position(caster_wheels[idx])
            box = ctx.part_world_aabb(caster_wheels[idx])
        travel = math.hypot(p0[0] - p180[0], p0[1] - p180[1])
        ctx.check(
            f"caster {idx} trails its kingpin through a half turn",
            abs(travel - 2.0 * r.caster_trail) < 0.003
            and box is not None
            and abs(float(box[0][2])) < 0.005
            and float(box[1][2]) < r.rail_z0,
            details=f"travel={travel:.4f} expected={2.0 * r.caster_trail:.4f} box={box}",
        )

    # --- optional mechanisms --------------------------------------------------
    if r.caster == "braked_swivel":
        brakes = _parts_by_role(model, "caster_brake")
        for idx, brake in enumerate(brakes):
            shoe = f"caster__braked_swivel__brake_shoe_{brake.meta['index']}"
            rest_shoe = ctx.part_element_world_aabb(brake, elem=shoe)
            with ctx.pose({joints[f"caster_brake_{brake.meta['index']}_pivot"]: BRAKE_MAX}):
                applied = ctx.part_element_world_aabb(brake, elem=shoe)
            ctx.check(
                f"caster brake {idx} drops its shoe onto the tread when applied",
                rest_shoe is not None
                and applied is not None
                and float(applied[0][2]) < float(rest_shoe[0][2]) - 0.008,
                details=f"rest={rest_shoe} applied={applied}",
            )

    if r.latch == "foot_pedal_release":
        pedal = _parts_by_role(model, "release_pedal")[0]
        pad = "latch__foot_pedal_release__foot_pad"
        rest_pad = ctx.part_element_world_aabb(pedal, elem=pad)
        with ctx.pose(
            {joints["release_pedal_pivot"]: PEDAL_MAX, latch_joint: r.latch_upper}
        ):
            pressed_pad = ctx.part_element_world_aabb(pedal, elem=pad)
        ctx.check(
            "foot pedal treads down through a real stroke",
            rest_pad is not None
            and pressed_pad is not None
            and float(pressed_pad[0][2]) < float(rest_pad[0][2]) - 0.020,
            details=f"rest={rest_pad} pressed={pressed_pad}",
        )

    if r.push_handle == "folding_hoop":
        fold = joints["push_handle_fold"]
        up = ctx.part_world_aabb(handles[0])
        with ctx.pose({fold: HANDLE_FOLD_MAX}):
            folded = ctx.part_world_aabb(handles[0])
        ctx.check(
            "fold-down handle lies back over the push end",
            up is not None
            and folded is not None
            and float(folded[1][2]) < float(up[1][2]) - 0.25
            and float(folded[0][0]) < float(up[0][0]) - 0.20
            and float(folded[0][2]) > 0.02,
            details=f"up={up} folded={folded}",
        )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_envelope_overcenter_fork_pockets",
        {
            "hopper_form": "v_nose_spout",
            "latch": "overcenter_side_lever",
            "push_handle": "side_rails",
            "chassis": "fork_pockets",
            "caster": "braked_swivel",
            "deck_bearer_count": 4,
            "hopper_length_m": 1.50,
            "hopper_width_m": 0.78,
            "hopper_depth_m": 0.55,
            "main_wheel_radius_m": 0.125,
            "palette_style": "utility_blue",
        },
        reason=(
            "smallest tub with the tightest deck: four bearers, forklift pockets, "
            "a side over-centre lever on the narrowest catch bar and braked casters"
        ),
    ),
    corner_case(
        "max_envelope_folding_tube_frame",
        {
            "hopper_form": "barrel_side",
            "latch": "foot_pedal_release",
            "push_handle": "folding_hoop",
            "chassis": "tube_frame",
            "caster": "braked_swivel",
            "deck_bearer_count": 2,
            "hopper_length_m": 1.85,
            "hopper_width_m": 0.95,
            "hopper_depth_m": 0.86,
            "main_wheel_radius_m": 0.165,
            "palette_style": "safety_yellow",
        },
        reason=(
            "largest bulged tub on the fewest bearers over a bent tube frame, with "
            "the longest dump stroke, the pedal linkage and a fold-down hoop"
        ),
    ),
    corner_case(
        "octagon_deep_tub_shallow_wheels",
        {
            "hopper_form": "chamfered_octagon",
            "latch": "c_throat_claw",
            "push_handle": "rear_loop",
            "chassis": "box_rail_deck",
            "caster": "plain_swivel",
            "deck_bearer_count": 3,
            "hopper_length_m": 1.85,
            "hopper_width_m": 0.78,
            "hopper_depth_m": 0.86,
            "main_wheel_radius_m": 0.125,
            "palette_style": "charcoal",
        },
        reason=(
            "deepest and longest tub on the narrowest track and smallest wheels: "
            "the worst case for dump-lip ground clearance and deck bearer span"
        ),
    ),
    corner_case(
        "u_nose_wide_shallow_gravity_hook",
        {
            "hopper_form": "u_nose_scoop",
            "latch": "gravity_hook",
            "push_handle": "side_rails",
            "chassis": "tube_frame",
            "caster": "plain_swivel",
            "deck_bearer_count": 4,
            "hopper_length_m": 1.50,
            "hopper_width_m": 0.95,
            "hopper_depth_m": 0.55,
            "main_wheel_radius_m": 0.165,
            "palette_style": "commercial_black",
        },
        reason=(
            "shortest and widest shallow scoop on the largest wheels: the U nose "
            "is closest to the running gear and the tub overhangs the tube frame most"
        ),
    ),
    corner_case(
        "frameless_min_envelope_vnose_overcenter",
        {
            "hopper_form": "v_nose_spout",
            "latch": "overcenter_side_lever",
            "push_handle": "side_rails",
            "chassis": "molded_underbody",
            "caster": "braked_swivel",
            "deck_bearer_count": 4,
            "hopper_length_m": 1.50,
            "hopper_width_m": 0.78,
            "hopper_depth_m": 0.55,
            "main_wheel_radius_m": 0.125,
            "palette_style": "utility_blue",
        },
        reason=(
            "frameless tier at its tightest: the narrowest tub gives the narrowest "
            "molded apron, so the subframe track, the caster pads and four cradle "
            "bearers all have to fit inside it, with the over-centre lever hinged "
            "outboard of the apron and braked casters underneath"
        ),
    ),
    corner_case(
        "frameless_max_envelope_barrel_folding",
        {
            "hopper_form": "barrel_side",
            "latch": "foot_pedal_release",
            "push_handle": "folding_hoop",
            "chassis": "molded_underbody",
            "caster": "plain_swivel",
            "deck_bearer_count": 2,
            "hopper_length_m": 1.85,
            "hopper_width_m": 0.95,
            "hopper_depth_m": 0.86,
            "main_wheel_radius_m": 0.165,
            "palette_style": "charcoal",
        },
        reason=(
            "largest bulged frameless tub on the longest dump stroke: the bowed "
            "apron sweeps furthest over the subframe while the pedal linkage and "
            "the fold-down hoop hang off the compact rear mount"
        ),
    ),
    corner_case(
        "frameless_octagon_deep_tub_small_wheels",
        {
            "hopper_form": "chamfered_octagon",
            "latch": "gravity_hook",
            "push_handle": "rear_loop",
            "chassis": "molded_underbody",
            "caster": "plain_swivel",
            "deck_bearer_count": 3,
            "hopper_length_m": 1.85,
            "hopper_width_m": 0.78,
            "hopper_depth_m": 0.86,
            "main_wheel_radius_m": 0.125,
            "palette_style": "commercial_black",
        },
        reason=(
            "deepest and longest frameless tub on the smallest wheels: the lowest "
            "apron bottom line and the longest faceted apron run, the worst case "
            "for apron-to-ground and apron-to-caster clearance"
        ),
    ),
    corner_case(
        "frameless_u_nose_wide_shallow",
        {
            "hopper_form": "u_nose_scoop",
            "latch": "c_throat_claw",
            "push_handle": "folding_hoop",
            "chassis": "molded_underbody",
            "caster": "braked_swivel",
            "deck_bearer_count": 4,
            "hopper_length_m": 1.50,
            "hopper_width_m": 0.95,
            "hopper_depth_m": 0.55,
            "main_wheel_radius_m": 0.165,
            "palette_style": "safety_yellow",
        },
        reason=(
            "shortest, widest and shallowest frameless scoop on the largest wheels: "
            "the semicircular nose cuts the apron run shortest while four cradle "
            "bearers still have to seat under the pan"
        ),
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
    "build_urban_environment_tilt_truck2",
    "build_seeded_urban_environment_tilt_truck2",
    "run_urban_environment_tilt_truck2_tests",
]
