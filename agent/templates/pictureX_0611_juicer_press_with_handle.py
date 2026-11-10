# SPDX-License-Identifier: Apache-2.0

"""Manual bench citrus press (0611 / juicer_press_with_handle).

Design-backed rebuild.  Artifacts:

  * ``articraft_template_authoring/source_maps/pictureX_0611_juicer_press_with_handle.md``
  * ``articraft_template_authoring/designs/pictureX_0611_juicer_press_with_handle.json``
    (filled by ``scripts/design_fill/pictureX_0611_juicer_press_with_handle.py``)

Frame convention
----------------
``z = 0`` is the bench top: the frame's base block stands on it and everything that
belongs *under* the bench (foot pads, the clamp throat and jaw) goes negative.  The press
faces ``+X`` — every operator member (lever grip, side crank, handwheel knob) reaches
toward ``+X`` — which is one of the two octants the shared preview camera (+X / -Y) sees.
The cup / strainer / ram share one vertical axis at ``(0, cup_y_m)``.

The whole machine is derived bottom-up from that axis:

    base_height_m -> deck_lift_m (catch_deck) -> cup_seat_z_m -> cup_top_z_m
      -> head_gap_m (from ram_travel_m, so the head always clears the strainer plate
         by press_clear_m at FULL stroke and by head_gap_m at rest)
      -> ram_origin_z_m -> beam_top_z_m -> beam_bottom_z_m -> column/post length

so a change to the cup, the deck or the stroke moves the beam, the columns and the
actuator pivot together instead of leaving a hard-coded gantry height behind.

Deliberate deviations from the source pool (all recorded in the SourceMap)
------------------------------------------------------------------------
1. Every pool record wraps its mechanism interfaces in ``ctx.allow_overlap`` (7 calls in
   the C-frame fork, 12 in the rack-and-pinion fork).  That call is blocked for
   Design-backed templates, so this template cuts the openings the sources only asserted:
   a real bearing bore for the lever pin, a real rack/pinion window through the beam, a
   real bored nut housing, and a real clamp-screw bore.
2. ``c_arch_throat`` puts the lever pivot on a bearing lug on the throat arm's FRONT face
   rather than on the column front face above the arm (source
   ``c_frame_lever_refill`` L423-L438).  The source's placement drives the lever arm and
   the dog-link straight through the 58 mm-wide throat arm — its own comment says a
   production casting "would have a guide slot there" — and a slot wide enough for the
   link through an arm that narrow severs the arm from the ram boss.  Mounting the pivot
   on the arm's front face puts the whole linkage in a free plane ahead of the beam,
   which is exactly what the twin-post origin does, and removes five of the seven
   allowances in one move.  The source's other C-arch facts are kept: one welded body,
   rear column, forward throat arm, guide boss, single bore, and the column standing
   proud of the arm.
3. The gear pair is built in MILLIMETRES and meshed with ``unit_scale=0.001``; the pool
   authors it at metre scale, where OCC's absolute tolerances make an involute gear
   non-watertight and prone to tessellating into disconnected islands.
4. The clamp's gusset ribs move from under the mounting plate (source L64-L82, where they
   sit inside the volume the bench slab occupies) to the outboard face of the throat wall,
   tying wall to jaw entirely clear of the throat.  Same element, real load path.
5. Cup / strainer lift limits and the lever's swing limit are DERIVED from the press-head
   envelope rather than copied (source: 0.080 / 0.055 fixed), because the source values
   drive the rising cup rim and strainer plate straight into the raised press head.
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
    Box,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    RackGear,
    Sphere,
    SpurGear,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
    tube_from_spline_points,
    wire_from_points,
)

# --------------------------------------------------------------------------- #
# Domain
# --------------------------------------------------------------------------- #
FrameStyle = Literal["twin_post_column", "c_arch_throat"]
MountStyle = Literal["corner_foot_pads", "bench_clamp_bracket"]
ActuatorStyle = Literal["lever_linkage", "rack_pinion_crank", "screw_handwheel"]
CatchDeck = Literal["flat_drip_disc", "raised_pedestal_boss"]
GripStyle = Literal["ball_knob", "sleeve_and_ball", "tee_bar_knobs"]
PaletteStyle = Literal[
    "chrome_bench",
    "cast_iron_black",
    "enamel_red",
    "brass_kitchen",
    "stainless_pro",
]

FRAME_STYLES: tuple[FrameStyle, ...] = ("twin_post_column", "c_arch_throat")
MOUNT_STYLES: tuple[MountStyle, ...] = ("corner_foot_pads", "bench_clamp_bracket")
ACTUATOR_STYLES: tuple[ActuatorStyle, ...] = (
    "lever_linkage",
    "rack_pinion_crank",
    "screw_handwheel",
)
CATCH_DECKS: tuple[CatchDeck, ...] = ("flat_drip_disc", "raised_pedestal_boss")
GRIP_STYLES: tuple[GripStyle, ...] = ("ball_knob", "sleeve_and_ball", "tee_bar_knobs")
BASE_SUPPORT_COUNTS: tuple[int, ...] = (3, 4, 5, 6)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "chrome_bench",
    "cast_iron_black",
    "enamel_red",
    "brass_kitchen",
    "stainless_pro",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot(
            "frame_style",
            FRAME_STYLES,
            role="source-backed standing frame and ram guide beam",
        ),
        component_slot(
            "mount_style",
            MOUNT_STYLES,
            role="source-backed base support / bench interface",
        ),
        component_slot(
            "actuator_style",
            ACTUATOR_STYLES,
            role="source-backed operator actuator driving the ram",
        ),
        component_slot(
            "catch_deck",
            CATCH_DECKS,
            role="source-backed cup seating deck on the base",
        ),
        component_slot(
            "grip_style",
            GRIP_STYLES,
            role="source-backed operator hand interface at the actuator tip",
        ),
        multiplicity_slot(
            "base_support_count",
            BASE_SUPPORT_COUNTS,
            role="repeated base support element per mount candidate",
            item_slot="mount_style",
        ),
    )
)

# Palette keys: frame casting, deck/vessel stainless, bright chrome hardware,
# dark rubber, and a hand-grip accent.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # Light-metal palettes are held under ~0.6 albedo on the large frame and vessel
    # faces: the shared preview/gallery rig keys at 45 * dist**2 with view_transform
    # "Standard" and no tonemap, so a flat face turned toward the key clips to pure
    # white above roughly 0.6 and the whole press renders as a featureless slab.
    "chrome_bench": {
        "frame": (0.46, 0.48, 0.50, 1.0),
        "vessel": (0.52, 0.54, 0.55, 1.0),
        "chrome": (0.58, 0.60, 0.62, 1.0),
        "rubber": (0.055, 0.060, 0.063, 1.0),
        "grip": (0.30, 0.32, 0.34, 1.0),
    },
    "cast_iron_black": {
        "frame": (0.17, 0.18, 0.19, 1.0),
        "vessel": (0.70, 0.72, 0.73, 1.0),
        "chrome": (0.78, 0.80, 0.82, 1.0),
        "rubber": (0.05, 0.05, 0.055, 1.0),
        "grip": (0.09, 0.10, 0.11, 1.0),
    },
    "enamel_red": {
        "frame": (0.61, 0.10, 0.09, 1.0),
        "vessel": (0.76, 0.78, 0.79, 1.0),
        "chrome": (0.85, 0.87, 0.88, 1.0),
        "rubber": (0.06, 0.06, 0.065, 1.0),
        "grip": (0.13, 0.13, 0.14, 1.0),
    },
    "brass_kitchen": {
        "frame": (0.55, 0.43, 0.16, 1.0),
        "vessel": (0.72, 0.74, 0.74, 1.0),
        "chrome": (0.80, 0.70, 0.36, 1.0),
        "rubber": (0.07, 0.06, 0.055, 1.0),
        "grip": (0.24, 0.16, 0.08, 1.0),
    },
    "stainless_pro": {
        "frame": (0.42, 0.44, 0.46, 1.0),
        "vessel": (0.53, 0.55, 0.56, 1.0),
        "chrome": (0.58, 0.59, 0.60, 1.0),
        "rubber": (0.08, 0.085, 0.09, 1.0),
        "grip": (0.20, 0.34, 0.52, 1.0),
    },
}

# Source cup / strainer profiles are quoted at their source radii and then scaled by
# `cup_scale_r_m` / `cup_scale_z`; 0.066 and 0.133 are the source cup's own rim radius
# and height, so the identity scale reproduces the pool geometry exactly.
_SRC_CUP_RIM_R = 0.066
_SRC_CUP_H = 0.133
_SRC_RAM_REACH = 0.232

_CUP_OUTER = (
    (0.034, 0.000),
    (0.040, 0.012),
    (0.046, 0.026),
    (0.051, 0.074),
    (0.058, 0.111),
    (0.064, 0.127),
    (0.066, 0.133),
)
_CUP_INNER = (
    (0.000, 0.004),
    (0.031, 0.008),
    (0.036, 0.016),
    (0.042, 0.028),
    (0.047, 0.073),
    (0.054, 0.105),
    (0.043, 0.105),
    (0.043, 0.109),
    (0.057, 0.112),
    (0.060, 0.125),
    (0.063, 0.131),
)
_STRAINER_OUTER = (
    (0.043, 0.000),
    (0.047, 0.006),
    (0.052, 0.014),
    (0.058, 0.024),
)
_STRAINER_INNER = (
    (0.039, 0.002),
    (0.043, 0.007),
    (0.048, 0.014),
    (0.054, 0.022),
)
# Perforation rings, source `((0.011, 8), (0.022, 12), (0.033, 18))` on a 0.041 plate:
# radius fractions 0.268 / 0.537 / 0.805 of the plate radius.
_RING_COUNTS = (8, 12, 18, 24)
_RING_FRAC_LO = 0.268
_RING_FRAC_HI = 0.805

# Source ram profile (17 points), expressed as (radius key, z).  Radius keys are
# multiples of the guided shaft radius for the shaft/collar band and of the press-head
# radius for the bell; z is scaled by `ram_z_scale`.  Source: shaft 0.009, collar 0.018,
# head 0.050.
# (shaft-radius multiple, collar flag, z); the collar radius is derived per actuator
# because the rack-and-pinion fork needs the rack teeth to stand proud of it.
_RAM_SHAFT_BAND = (
    (1.00, False, -0.072),
    (0.00, True, -0.080),
    (0.00, True, -0.101),
    (1.11, False, -0.111),
    (1.11, False, -0.135),
    (1.67, False, -0.142),
)
_RAM_HEAD_BAND = (
    (0.76, -0.158),
    (1.00, -0.178),
    (0.92, -0.193),
    (0.54, -0.211),
    (0.20, -0.226),
    (0.00, -0.232),
)
_RAM_COLLAR_Z = -0.0905  # collar mid-station, source (-0.080 .. -0.101)

# Lever arm spline fractions, source (0, 0.084, 0.170, 0.245) / 0.245 with the drop
# ratio easing from 0.476 to 0.490 along the arm.
_ARM_FRACS = (0.0, 0.343, 0.694, 1.0)
_ARM_DROP_EASE = (0.0, 0.970, 0.985, 1.0)
_LINK_PIN_FRAC = 0.196  # source pin at 0.048 / 0.245 along the arm


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, allowed):
    return value if value in allowed else allowed[0]


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Config:
    frame_style: FrameStyle = "twin_post_column"
    mount_style: MountStyle = "corner_foot_pads"
    actuator_style: ActuatorStyle = "lever_linkage"
    catch_deck: CatchDeck = "flat_drip_disc"
    grip_style: GripStyle = "sleeve_and_ball"
    base_support_count: int = 4
    palette_style: PaletteStyle = "chrome_bench"

    # shared frame / stack
    base_width_m: float = 0.230
    base_depth_m: float = 0.180
    base_height_m: float = 0.048
    beam_height_m: float = 0.046
    deck_margin_m: float = 0.0030

    # cup / strainer / ram core
    cup_rim_ratio: float = 0.846
    cup_height_m: float = 0.133
    ram_travel_m: float = 0.040
    press_head_ratio: float = 0.757
    ram_reach_m: float = 0.256
    strainer_ring_count: int = 3

    # frame_style = twin_post_column
    post_radius_m: float = 0.0085
    post_span_ratio: float = 0.626

    # frame_style = c_arch_throat
    column_depth_m: float = 0.046

    # catch_deck = raised_pedestal_boss
    pedestal_h_m: float = 0.032

    # mount_style = corner_foot_pads
    foot_radius_m: float = 0.012

    # mount_style = bench_clamp_bracket
    clamp_throat_h_m: float = 0.050
    clamp_screw_r_m: float = 0.0090

    # actuator_style = lever_linkage
    lever_reach_m: float = 0.245
    lever_drop_ratio: float = 0.490

    # actuator_style = rack_pinion_crank
    gear_module_mm: float = 2.0
    crank_reach_m: float = 0.110

    # actuator_style = screw_handwheel
    handwheel_r_m: float = 0.078
    wheel_spoke_pairs: int = 2

    # grip_style
    grip_len_m: float = 0.075
    knob_r_m: float = 0.0100

    name: str = "pictureX_0611_juicer_press_with_handle"


@dataclass(frozen=True)
class ResolvedConfig:
    frame_style: FrameStyle
    mount_style: MountStyle
    actuator_style: ActuatorStyle
    catch_deck: CatchDeck
    grip_style: GripStyle
    base_support_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]

    # independent, clamped
    base_width_m: float
    base_depth_m: float
    base_height_m: float
    beam_height_m: float
    deck_margin_m: float
    cup_rim_ratio: float
    cup_height_m: float
    ram_travel_m: float
    press_head_ratio: float
    ram_reach_m: float
    strainer_ring_count: int
    post_radius_m: float
    post_span_ratio: float
    column_depth_m: float
    pedestal_h_m: float
    foot_radius_m: float
    clamp_throat_h_m: float
    clamp_screw_r_m: float
    lever_reach_m: float
    lever_drop_ratio: float
    gear_module_mm: float
    crank_reach_m: float
    handwheel_r_m: float
    wheel_spoke_pairs: int
    grip_len_m: float
    knob_r_m: float

    # derived — base and deck
    base_hx_m: float
    base_hy_front_m: float
    base_hy_back_m: float
    cup_rim_r_m: float
    cup_y_m: float
    deck_r_m: float
    deck_disc_h_m: float
    pedestal_r_m: float
    deck_lift_m: float
    cup_seat_z_m: float

    # derived — vessels
    cup_scale_r: float
    cup_scale_z: float
    cup_top_z_m: float
    stack_top_z_m: float
    strainer_h_m: float
    strainer_drop_m: float
    strainer_seat_local_m: float
    strainer_plate_r_m: float
    strainer_plate_t_m: float
    strainer_hole_r_m: float
    lift_limit_m: float

    # derived — ram
    head_dip_m: float
    press_clear_m: float
    press_head_r_m: float
    ram_shaft_r_m: float
    ram_collar_r_m: float
    ram_bore_r_m: float
    ram_z_scale: float
    head_gap_m: float
    ram_tip_rest_z_m: float
    ram_origin_z_m: float
    ram_cap_z0_m: float
    ram_cap_z1_m: float
    ram_collar_z_m: float
    screw_thread_r_m: float
    screw_len_m: float
    thread_step_m: float
    thread_start_z_m: float
    guide_drop_m: float

    # derived — beam / frame
    beam_top_z_m: float
    beam_bottom_z_m: float
    beam_depth_m: float
    beam_y_m: float
    beam_front_y_m: float
    beam_back_y_m: float
    beam_hx_m: float
    boss_r_m: float
    boss_top_z_m: float
    post_x_m: float
    post_y_m: float
    post_len_m: float
    column_w_m: float
    column_front_y_m: float
    column_back_y_m: float
    column_top_z_m: float
    arm_front_y_m: float

    # derived — lever mechanism
    mech_y_m: float
    pivot_x_m: float
    pivot_z_m: float
    lever_pin_r_m: float
    lever_pin_len_m: float
    arm_r_m: float
    link_r_m: float
    link_pin_local: tuple[float, float, float]
    link_knee_local: tuple[float, float, float]
    link_end_local: tuple[float, float, float]
    lever_lower_rad: float
    lever_upper_rad: float
    link_swing_rad: float
    bearing_r_m: float
    bearing_y0_m: float
    bearing_y1_m: float

    # derived — rack and pinion
    gear_module_m: float
    pinion_teeth: int
    pinion_r0_m: float
    pinion_ra_m: float
    pinion_width_m: float
    pinion_x_m: float
    pinion_z_m: float
    pinion_shaft_r_m: float
    rack_x0_m: float
    gear_backlash_m: float
    rack_h_m: float
    rack_z0_m: float
    rack_len_m: float
    crank_hub_y_m: float
    crank_upper_rad: float

    # derived — screw handwheel
    nut_h_m: float
    nut_outer_r_m: float
    nut_bore_r_m: float
    wheel_origin_z_m: float
    wheel_hub_r_m: float
    wheel_hub_h_m: float
    wheel_rim_t_m: float
    wheel_rim_h_m: float
    wheel_knob_r_frac: float
    wheel_stem_h_m: float

    # derived — mount
    foot_h_m: float
    foot_stations: tuple[tuple[float, float], ...]
    clamp_w_m: float
    clamp_wall_t_m: float
    clamp_jaw_t_m: float
    clamp_jaw_depth_m: float
    clamp_jaw_z1_m: float
    clamp_rib_reach_m: float
    clamp_rib_t_m: float
    clamp_rib_x: tuple[float, ...]
    clamp_screw_y_m: float
    clamp_screw_len_m: float
    clamp_pad_r_m: float

    # derived — grip
    grip_sleeve_r_m: float
    tee_half_m: float

    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x4A55_4943_4552)
    return Config(
        frame_style=choices["frame_style"],
        mount_style=choices["mount_style"],
        actuator_style=choices["actuator_style"],
        catch_deck=choices["catch_deck"],
        grip_style=choices["grip_style"],
        base_support_count=int(choices["base_support_count"]),
        palette_style=rng.choice(PALETTE_STYLES),
        base_width_m=round(rng.uniform(0.205, 0.275), 5),
        base_depth_m=round(rng.uniform(0.145, 0.210), 5),
        base_height_m=round(rng.uniform(0.034, 0.062), 5),
        beam_height_m=round(rng.uniform(0.038, 0.060), 5),
        deck_margin_m=round(rng.uniform(0.0015, 0.0075), 5),
        cup_rim_ratio=round(rng.uniform(0.58, 0.86), 4),
        cup_height_m=round(rng.uniform(0.108, 0.166), 5),
        ram_travel_m=round(rng.uniform(0.026, 0.046), 5),
        press_head_ratio=round(rng.uniform(0.55, 0.78), 4),
        ram_reach_m=round(rng.uniform(0.245, 0.320), 5),
        strainer_ring_count=rng.choice((2, 3, 4)),
        post_radius_m=round(rng.uniform(0.0068, 0.0115), 5),
        post_span_ratio=round(rng.uniform(0.52, 0.78), 4),
        column_depth_m=round(rng.uniform(0.034, 0.064), 5),
        pedestal_h_m=round(rng.uniform(0.016, 0.048), 5),
        foot_radius_m=round(rng.uniform(0.009, 0.018), 5),
        clamp_throat_h_m=round(rng.uniform(0.038, 0.086), 5),
        clamp_screw_r_m=round(rng.uniform(0.0070, 0.0120), 5),
        lever_reach_m=round(rng.uniform(0.200, 0.300), 5),
        lever_drop_ratio=round(rng.uniform(0.34, 0.62), 4),
        gear_module_mm=round(rng.uniform(1.6, 2.6), 4),
        crank_reach_m=round(rng.uniform(0.072, 0.132), 5),
        handwheel_r_m=round(rng.uniform(0.060, 0.094), 5),
        wheel_spoke_pairs=rng.choice((2, 3, 4)),
        grip_len_m=round(rng.uniform(0.052, 0.092), 5),
        knob_r_m=round(rng.uniform(0.0085, 0.0160), 5),
        name=f"seeded_juicer_press_{seed}",
    )


def _foot_stations(count: int, hx: float, hy: float) -> tuple[tuple[float, float], ...]:
    """Base-underside pad stations, index-general from the origin anchor's
    ``enumerate(((-0.090, -0.064), ...))`` corner loop (L249-L260).

    N=4 reproduces the source rectangle; the other counts walk the same inset
    perimeter — a rear-apex tripod at 3, corners plus a front pad at 5, corners plus
    both side mid-points at 6."""

    corners = ((-hx, -hy), (-hx, hy), (hx, -hy), (hx, hy))
    if count <= 3:
        return ((-hx, -hy), (hx, -hy), (0.0, hy))
    if count == 4:
        return corners
    if count == 5:
        return corners + ((0.0, -hy),)
    return corners + ((0.0, -hy), (0.0, hy))


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()

    frame_style = _pick(cfg.frame_style, FRAME_STYLES)
    mount_style = _pick(cfg.mount_style, MOUNT_STYLES)
    actuator_style = _pick(cfg.actuator_style, ACTUATOR_STYLES)
    catch_deck = _pick(cfg.catch_deck, CATCH_DECKS)
    grip_style = _pick(cfg.grip_style, GRIP_STYLES)
    base_support_count = int(_pick(int(cfg.base_support_count), BASE_SUPPORT_COUNTS))
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    base_w = _clamp(cfg.base_width_m, 0.205, 0.275)
    base_d = _clamp(cfg.base_depth_m, 0.145, 0.210)
    base_h = _clamp(cfg.base_height_m, 0.034, 0.062)
    beam_h = _clamp(cfg.beam_height_m, 0.038, 0.060)
    deck_margin = _clamp(cfg.deck_margin_m, 0.0015, 0.0075)
    cup_rim_ratio = _clamp(cfg.cup_rim_ratio, 0.58, 0.86)
    cup_height = _clamp(cfg.cup_height_m, 0.108, 0.166)
    ram_travel = _clamp(cfg.ram_travel_m, 0.026, 0.046)
    head_ratio = _clamp(cfg.press_head_ratio, 0.55, 0.78)
    ram_reach = _clamp(cfg.ram_reach_m, 0.245, 0.320)
    ring_count = int(_pick(int(cfg.strainer_ring_count), (2, 3, 4)))
    post_r = _clamp(cfg.post_radius_m, 0.0068, 0.0115)
    post_span_ratio = _clamp(cfg.post_span_ratio, 0.52, 0.78)
    column_depth = _clamp(cfg.column_depth_m, 0.034, 0.064)
    pedestal_h = _clamp(cfg.pedestal_h_m, 0.016, 0.048)
    foot_r = _clamp(cfg.foot_radius_m, 0.009, 0.018)
    clamp_throat_h = _clamp(cfg.clamp_throat_h_m, 0.038, 0.086)
    clamp_screw_r = _clamp(cfg.clamp_screw_r_m, 0.0070, 0.0120)
    lever_reach = _clamp(cfg.lever_reach_m, 0.200, 0.300)
    lever_drop = _clamp(cfg.lever_drop_ratio, 0.34, 0.62)
    module_mm = _clamp(cfg.gear_module_mm, 1.6, 2.6)
    crank_reach = _clamp(cfg.crank_reach_m, 0.072, 0.132)
    wheel_r = _clamp(cfg.handwheel_r_m, 0.060, 0.094)
    spoke_pairs = int(_pick(int(cfg.wheel_spoke_pairs), (2, 3, 4)))
    grip_len = _clamp(cfg.grip_len_m, 0.052, 0.092)
    knob_r = _clamp(cfg.knob_r_m, 0.0085, 0.0160)

    # ---- base footprint and cup station -----------------------------------
    base_hx = base_w / 2.0
    base_hy = base_d / 2.0
    # The cup must sit inside the base in both axes with room for the deck disc; its
    # radius is therefore a ratio of the free half-span rather than a free length.
    cup_span = min(base_hx, base_hy) - 0.012
    cup_rim_r = cup_rim_ratio * cup_span
    cup_slack = base_hy - cup_rim_r - 0.004
    cup_y = -0.70 * cup_slack  # forward offset, source cup_y = -0.018 on a 0.180 base
    deck_r = cup_rim_r + deck_margin
    deck_disc_h = 0.0055 + 0.45 * deck_margin
    pedestal_r = deck_r * 1.08  # source boss 0.074 over a 0.068 disc

    deck_lift = deck_disc_h if catch_deck == "flat_drip_disc" else pedestal_h + deck_disc_h
    cup_seat_z = base_h + deck_lift

    # ---- vessels -----------------------------------------------------------
    cup_scale_r = cup_rim_r / _SRC_CUP_RIM_R
    cup_scale_z = cup_height / _SRC_CUP_H
    cup_top_z = cup_seat_z + cup_height
    strainer_h = 0.024 * cup_scale_r
    # The source cup carries a rolled lip notch at inner z 0.105-0.109 where the bore
    # steps in to 0.043; that notch IS the strainer seat, so seating there keeps the
    # strainer rim against the cup wall for every independent radial/axial scale.
    strainer_seat_local = 0.109 * cup_scale_z
    strainer_top_z = cup_seat_z + strainer_seat_local + strainer_h
    stack_top_z = max(cup_top_z, strainer_top_z)
    strainer_drop = stack_top_z - (cup_seat_z + strainer_seat_local)
    strainer_plate_r = 0.041 * cup_scale_r
    strainer_plate_t = 0.0022 * cup_scale_r
    strainer_hole_r = 0.00145 * cup_scale_r

    # ---- ram ---------------------------------------------------------------
    press_head_r = head_ratio * cup_rim_r
    ram_shaft_r = _clamp(0.18 * press_head_r, 0.0068, 0.0115)
    ram_collar_r = (2.0 if actuator_style == "lever_linkage" else 1.35) * ram_shaft_r
    screw_thread_r = ram_shaft_r * 1.22
    ram_bore_r = ram_shaft_r + 0.0008
    ram_z_scale = ram_reach / _SRC_RAM_REACH

    # The category invariant, expressed as one clearance budget.  head_dip is how far the
    # bell head drops BELOW the strainer/cup rim plane at full stroke — that is the
    # "ram descends into the cup" reading — and press_clear is what is left between the
    # tip and the perforated plate at that same stroke.  The rest gap follows from the two.
    head_dip = min(0.008, 0.45 * (strainer_drop - strainer_plate_t))
    press_clear = strainer_drop - strainer_plate_t - head_dip
    head_gap = ram_travel - head_dip
    ram_tip_rest_z = stack_top_z + head_gap
    ram_origin_z = ram_tip_rest_z + ram_reach
    ram_cap_z0 = ram_travel + 0.006  # the guided head never enters the beam bore
    ram_cap_z1 = ram_cap_z0 + 0.024 * ram_z_scale
    ram_collar_z = ram_origin_z + _RAM_COLLAR_Z * ram_z_scale

    # Vessel removal travel.  The cup and the strainer are serial, so a coupled pose can
    # raise the plate by 2 * lift while the ram is at full stroke; the travel is therefore
    # spent out of the same press_clear budget, leaving at most 3 mm of tip contact in that
    # pose — inside the 5 mm penetration gate.  Fully withdrawing the cup needs the ram
    # raised first, which is the machine's real operating sequence.
    lift_limit = max(0.006, 0.5 * (press_clear + 0.0030))

    # ---- beam --------------------------------------------------------------
    beam_top_z = ram_origin_z - 0.010
    beam_bottom_z = beam_top_z - beam_h
    beam_depth = 0.42 * base_d
    boss_r = ram_bore_r + 0.011
    boss_top_z = beam_top_z + 0.012
    # C-arch guide boss depth under the throat arm, source L63-L69: a 0.025 boss under a
    # 0.050 arm whose MID-PLANE is the ram origin, so the source hangs 0.050 of bore below
    # the origin against a 0.072 plain-shaft band (source ram L137-L161: the shaft runs at
    # one radius down to z = -0.072 and only then flares into the linkage collar).  Here
    # the origin sits 0.010 under the beam TOP, so the whole beam height already hangs
    # below it; a fixed 0.022 boss then reaches past the end of the plain shaft and the
    # collar flare is swallowed by the bore at the REST pose.  The bore is a running fit on
    # the plain shaft, so the boss can only be as deep as that band leaves free.
    shaft_band_drop = -_RAM_SHAFT_BAND[0][2] * ram_z_scale
    guide_drop = _clamp((beam_bottom_z - ram_origin_z) + shaft_band_drop - 0.0020, 0.0035, 0.022)
    # The coarse thread must stay clear of the beam's guide bore over the WHOLE stroke,
    # not just at rest: the bore is a running fit on the plain shaft, so a thread that
    # descends into it reads as the screw grinding through its own guide.
    thread_start_z = ram_travel + 0.006
    # The beam's front face stands ahead of the ram guide boss so the boss is contained in
    # the beam instead of protruding into the actuator's plane.  Source: the crosshead is a
    # bar unioned with a 70 mm ram boss, and the bore only has material because of it.
    beam_front_y = cup_y - boss_r - 0.004
    beam_y = beam_front_y + beam_depth / 2.0
    beam_back_y = beam_front_y + beam_depth

    # twin-post columns: outboard of the cup rim, inboard of the base edge
    post_y = beam_front_y + 0.75 * beam_depth
    post_clear_x = math.sqrt(max(0.0, (cup_rim_r + post_r + 0.004) ** 2 - (post_y - cup_y) ** 2))
    post_x = max(post_span_ratio * base_hx, post_clear_x)
    post_x = min(post_x, base_hx - post_r - 0.005)
    post_len = (beam_bottom_z + 0.008) - (base_h - 0.006)

    # C-arch: rear column clears the cup rim, throat arm reaches forward over it
    column_w = 0.25 * base_w
    column_front_y = cup_y + cup_rim_r + 0.006
    column_back_y = column_front_y + column_depth
    column_top_z = beam_top_z + 0.026
    arm_front_y = cup_y - boss_r - 0.008

    if frame_style == "twin_post_column":
        beam_hx = max(0.3825 * base_w, post_x + post_r + 0.004)
        base_hy_back = base_hy
    else:
        beam_hx = column_w / 2.0
        beam_front_y = arm_front_y
        beam_y = 0.5 * (arm_front_y + column_back_y)
        beam_back_y = column_back_y
        base_hy_back = max(base_hy, column_back_y + 0.006)

    # ---- rack and pinion ---------------------------------------------------
    gear_module_m = module_mm / 1000.0
    # A pitch radius under travel/2 would sweep the crank past 2 rad and carry the grip
    # back into the beam envelope, so the target radius is derived from the stroke and
    # the tooth count follows from the module.
    r0_target = max(0.019, ram_travel / 2.0)
    pinion_teeth = max(11, int(math.ceil(2.0 * r0_target / gear_module_m)))
    pinion_r0 = gear_module_m * pinion_teeth / 2.0
    pinion_ra = pinion_r0 + gear_module_m
    pinion_width = 7.0 * gear_module_m
    rack_h = 2.0 * gear_module_m
    rack_x0 = ram_shaft_r - 0.0005 + rack_h + 1.25 * gear_module_m
    gear_backlash = 0.5 * gear_module_m
    pinion_x = rack_x0 + pinion_r0 + gear_backlash
    pinion_z = 0.5 * (beam_bottom_z + beam_top_z)
    pinion_shaft_r = max(0.0045, 0.30 * pinion_r0)
    rack_z0 = -(0.010 + beam_h / 2.0 + 0.045)
    rack_len = 0.078 + ram_travel
    crank_hub_y = beam_back_y + 0.026
    crank_upper = ram_travel / pinion_r0

    if frame_style == "c_arch_throat" and actuator_style == "rack_pinion_crank":
        # host adaptation: the throat arm grows a gear head wide enough to carry the
        # pinion window and its bearing boss
        beam_hx = max(beam_hx, pinion_x + pinion_ra + 0.012)

    # ---- screw handwheel ---------------------------------------------------
    # tall enough that the thread band is inside the nut at rest and still inside it at
    # full stroke (source housing 0.042 over a 0.055 stroke)
    nut_h = 0.020 + ram_travel
    nut_outer_r = screw_thread_r * 1.55 + 0.005
    nut_bore_r = screw_thread_r + 0.0012
    wheel_origin_z = beam_top_z + nut_h
    wheel_hub_r = max(nut_outer_r * 1.10, screw_thread_r + 0.008)
    wheel_hub_h = 0.034
    wheel_rim_t = 0.017 * (wheel_r / 0.078)
    wheel_rim_h = 0.012
    wheel_knob_r_frac = 0.88
    wheel_stem_h = 0.040
    screw_len = (wheel_origin_z - ram_origin_z) + 0.80 * wheel_hub_h

    # ---- lever mechanism ---------------------------------------------------
    arm_r = _clamp(0.029 * lever_reach, 0.0055, 0.0098)
    link_r = 0.72 * arm_r
    lever_pin_r = min(arm_r * 1.45, beam_h / 2.0 - 0.005)
    lever_pin_len = 0.044 * (base_w / 0.230)
    pivot_x = -0.16 * base_w
    pivot_z = beam_top_z - beam_h / 2.0
    pin_drop = _LINK_PIN_FRAC * lever_reach * lever_drop
    pin_z = pivot_z - pin_drop
    # The whole lever mechanism runs in one plane ahead of the beam's front face.  Because
    # the guide boss is contained inside the beam, that single rule clears the beam, the
    # boss and the C-arch's throat arm at once.
    mech_y = beam_front_y - arm_r - 0.005

    link_pin_local = (
        _LINK_PIN_FRAC * lever_reach,
        0.0,
        -_LINK_PIN_FRAC * lever_reach * lever_drop,
    )
    # The dog-link drops straight down in the mechanism plane until it is below every
    # near-axis frame feature, then turns in to the ram collar: a real dog-leg, which is
    # what the source names it and what keeps it out of the beam without pushing the whole
    # handle forward.
    knee_drop = guide_drop if frame_style == "c_arch_throat" else 0.0
    link_knee_z = beam_bottom_z - knee_drop - link_r - 0.005
    link_knee_z = min(link_knee_z, ram_collar_z + 0.012)
    pin_world_x = pivot_x + link_pin_local[0]
    azimuth_x = pin_world_x
    azimuth_y = mech_y - cup_y
    azimuth_n = math.hypot(azimuth_x, azimuth_y) or 1.0
    end_r = ram_collar_r + link_r - 0.0008
    link_end_world = (
        end_r * azimuth_x / azimuth_n,
        cup_y + end_r * azimuth_y / azimuth_n,
        ram_collar_z,
    )
    link_knee_local = (0.0, 0.0, link_knee_z - pin_z)
    link_end_local = (
        link_end_world[0] - pin_world_x,
        link_end_world[1] - mech_y,
        link_end_world[2] - pin_z,
    )

    # Lever swing limits, both derived from real stops rather than copied.
    # Down limit: the grip tip must stay off the bench.
    alpha = math.atan2(lever_drop, 1.0)
    tip_reach = lever_reach + grip_len + knob_r
    ratio = _clamp((pivot_z - 0.018) / max(tip_reach, 1e-6), -1.0, 1.0)
    lever_upper = _clamp(math.asin(ratio) - alpha, 0.16, 0.42)
    # Up limit: raising the lever swings the dog-link's lower leg up, and that leg is the
    # only member that reaches back behind the beam's front face to find the ram collar.
    # The stop is where the first point of that leg to cross the beam face would reach the
    # beam's underside — i.e. the linkage bottoms on the beam, which is a real stop.
    end_y_local = link_end_local[1]
    cross_f = _clamp((beam_front_y - link_r - mech_y) / max(end_y_local, 1e-6), 0.0, 1.0)
    guard_x = link_pin_local[0] + cross_f * link_end_local[0]
    guard_z = (
        link_pin_local[2] + link_knee_local[2] + cross_f * (link_end_local[2] - link_knee_local[2])
    )
    guard_r = math.hypot(guard_x, guard_z) or 1e-6
    guard_phi = math.atan2(guard_z, guard_x)
    guard_u = _clamp(((beam_bottom_z - 0.004 - link_r) - pivot_z) / guard_r, -1.0, 1.0)
    lever_lower = _clamp(guard_phi - math.asin(guard_u), -0.56, -0.05)
    link_swing = 0.16

    bearing_r = lever_pin_r + 0.006
    bearing_y0 = mech_y + arm_r + 0.002
    bearing_y1 = mech_y + lever_pin_len - 0.6 * arm_r + 0.003

    # ---- mount -------------------------------------------------------------
    foot_h = 0.006 + 0.16 * foot_r
    foot_inset = foot_r + 0.013
    foot_stations = _foot_stations(
        base_support_count,
        max(0.010, base_hx - foot_inset),
        max(0.010, base_hy - foot_inset),
    )
    clamp_w = 0.74 * base_w
    clamp_wall_t = 0.078 * base_w
    clamp_jaw_t = 0.061 * base_w
    clamp_jaw_depth = 0.53 * base_d
    clamp_jaw_z1 = -clamp_throat_h
    clamp_rib_reach = 0.22 * base_d
    clamp_rib_t = 0.020 * base_w
    rib_pitch = clamp_w * 0.82 / max(1, base_support_count - 1)
    clamp_rib_x = tuple(
        (index - (base_support_count - 1) / 2.0) * rib_pitch for index in range(base_support_count)
    )
    clamp_screw_y = base_hy_back - clamp_jaw_depth + 0.32 * clamp_jaw_depth
    clamp_screw_len = 0.55 * clamp_throat_h
    clamp_pad_r = clamp_screw_r * 2.0

    grip_sleeve_r = knob_r * 0.92
    tee_half = 0.5 * (0.048 + 0.34 * grip_len)

    return ResolvedConfig(
        frame_style=frame_style,
        mount_style=mount_style,
        actuator_style=actuator_style,
        catch_deck=catch_deck,
        grip_style=grip_style,
        base_support_count=base_support_count,
        palette_style=palette_style,
        palette=PALETTES[palette_style],
        base_width_m=base_w,
        base_depth_m=base_d,
        base_height_m=base_h,
        beam_height_m=beam_h,
        deck_margin_m=deck_margin,
        cup_rim_ratio=cup_rim_ratio,
        cup_height_m=cup_height,
        ram_travel_m=ram_travel,
        press_head_ratio=head_ratio,
        ram_reach_m=ram_reach,
        strainer_ring_count=ring_count,
        post_radius_m=post_r,
        post_span_ratio=post_span_ratio,
        column_depth_m=column_depth,
        pedestal_h_m=pedestal_h,
        foot_radius_m=foot_r,
        clamp_throat_h_m=clamp_throat_h,
        clamp_screw_r_m=clamp_screw_r,
        lever_reach_m=lever_reach,
        lever_drop_ratio=lever_drop,
        gear_module_mm=module_mm,
        crank_reach_m=crank_reach,
        handwheel_r_m=wheel_r,
        wheel_spoke_pairs=spoke_pairs,
        grip_len_m=grip_len,
        knob_r_m=knob_r,
        base_hx_m=base_hx,
        base_hy_front_m=base_hy,
        base_hy_back_m=base_hy_back,
        cup_rim_r_m=cup_rim_r,
        cup_y_m=cup_y,
        deck_r_m=deck_r,
        deck_disc_h_m=deck_disc_h,
        pedestal_r_m=pedestal_r,
        deck_lift_m=deck_lift,
        cup_seat_z_m=cup_seat_z,
        cup_scale_r=cup_scale_r,
        cup_scale_z=cup_scale_z,
        cup_top_z_m=cup_top_z,
        stack_top_z_m=stack_top_z,
        strainer_h_m=strainer_h,
        strainer_drop_m=strainer_drop,
        strainer_seat_local_m=strainer_seat_local,
        strainer_plate_r_m=strainer_plate_r,
        strainer_plate_t_m=strainer_plate_t,
        strainer_hole_r_m=strainer_hole_r,
        lift_limit_m=lift_limit,
        head_dip_m=head_dip,
        press_clear_m=press_clear,
        press_head_r_m=press_head_r,
        ram_shaft_r_m=ram_shaft_r,
        ram_collar_r_m=ram_collar_r,
        ram_bore_r_m=ram_bore_r,
        ram_z_scale=ram_z_scale,
        head_gap_m=head_gap,
        ram_tip_rest_z_m=ram_tip_rest_z,
        ram_origin_z_m=ram_origin_z,
        ram_cap_z0_m=ram_cap_z0,
        ram_cap_z1_m=ram_cap_z1,
        ram_collar_z_m=ram_collar_z,
        screw_thread_r_m=screw_thread_r,
        screw_len_m=screw_len,
        thread_step_m=0.004 * ram_z_scale,
        thread_start_z_m=thread_start_z,
        guide_drop_m=guide_drop,
        beam_top_z_m=beam_top_z,
        beam_bottom_z_m=beam_bottom_z,
        beam_depth_m=beam_depth,
        beam_y_m=beam_y,
        beam_front_y_m=beam_front_y,
        beam_back_y_m=beam_back_y,
        beam_hx_m=beam_hx,
        boss_r_m=boss_r,
        boss_top_z_m=boss_top_z,
        post_x_m=post_x,
        post_y_m=post_y,
        post_len_m=post_len,
        column_w_m=column_w,
        column_front_y_m=column_front_y,
        column_back_y_m=column_back_y,
        column_top_z_m=column_top_z,
        arm_front_y_m=arm_front_y,
        mech_y_m=mech_y,
        pivot_x_m=pivot_x,
        pivot_z_m=pivot_z,
        lever_pin_r_m=lever_pin_r,
        lever_pin_len_m=lever_pin_len,
        arm_r_m=arm_r,
        link_r_m=link_r,
        link_pin_local=link_pin_local,
        link_knee_local=link_knee_local,
        link_end_local=link_end_local,
        lever_lower_rad=lever_lower,
        lever_upper_rad=lever_upper,
        link_swing_rad=link_swing,
        bearing_r_m=bearing_r,
        bearing_y0_m=bearing_y0,
        bearing_y1_m=bearing_y1,
        gear_module_m=gear_module_m,
        pinion_teeth=pinion_teeth,
        pinion_r0_m=pinion_r0,
        pinion_ra_m=pinion_ra,
        pinion_width_m=pinion_width,
        pinion_x_m=pinion_x,
        pinion_z_m=pinion_z,
        pinion_shaft_r_m=pinion_shaft_r,
        rack_x0_m=rack_x0,
        gear_backlash_m=gear_backlash,
        rack_h_m=rack_h,
        rack_z0_m=rack_z0,
        rack_len_m=rack_len,
        crank_hub_y_m=crank_hub_y,
        crank_upper_rad=crank_upper,
        nut_h_m=nut_h,
        nut_outer_r_m=nut_outer_r,
        nut_bore_r_m=nut_bore_r,
        wheel_origin_z_m=wheel_origin_z,
        wheel_hub_r_m=wheel_hub_r,
        wheel_hub_h_m=wheel_hub_h,
        wheel_rim_t_m=wheel_rim_t,
        wheel_rim_h_m=wheel_rim_h,
        wheel_knob_r_frac=wheel_knob_r_frac,
        wheel_stem_h_m=wheel_stem_h,
        foot_h_m=foot_h,
        foot_stations=foot_stations,
        clamp_w_m=clamp_w,
        clamp_wall_t_m=clamp_wall_t,
        clamp_jaw_t_m=clamp_jaw_t,
        clamp_jaw_depth_m=clamp_jaw_depth,
        clamp_jaw_z1_m=clamp_jaw_z1,
        clamp_rib_reach_m=clamp_rib_reach,
        clamp_rib_t_m=clamp_rib_t,
        clamp_rib_x=clamp_rib_x,
        clamp_screw_y_m=clamp_screw_y,
        clamp_screw_len_m=clamp_screw_len,
        clamp_pad_r_m=clamp_pad_r,
        grip_sleeve_r_m=grip_sleeve_r,
        tee_half_m=tee_half,
        name=cfg.name,
    )


def slot_choices_for_config(r: ResolvedConfig) -> dict[str, object]:
    return {
        "frame_style": r.frame_style,
        "mount_style": r.mount_style,
        "actuator_style": r.actuator_style,
        "catch_deck": r.catch_deck,
        "grip_style": r.grip_style,
        "base_support_count": r.base_support_count,
    }


def slot_choices_for_seed(seed: int) -> dict[str, object]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Shared geometry: cup, strainer, ram
# --------------------------------------------------------------------------- #
def _scaled_profile(
    profile: tuple[tuple[float, float], ...], sr: float, sz: float
) -> list[tuple[float, float]]:
    return [(radius * sr, z * sz) for radius, z in profile]


def _cup_geometry(r: ResolvedConfig) -> LatheGeometry:
    """Source `_cup_geometry` (origin anchor L66-L94): a shell lathe with an 11-point
    inner and a 7-point outer profile, so the collector cup is a real thin-wall vessel
    with a rolled lip rather than a solid of revolution."""

    return LatheGeometry.from_shell_profiles(
        _scaled_profile(_CUP_OUTER, r.cup_scale_r, r.cup_scale_z),
        _scaled_profile(_CUP_INNER, r.cup_scale_r, r.cup_scale_z),
        segments=56,
        start_cap="flat",
        end_cap="round",
        lip_samples=8,
    )


def _strainer_shell_geometry(r: ResolvedConfig) -> LatheGeometry:
    """Source `_strainer_shell_geometry` (origin anchor L97-L115)."""

    return LatheGeometry.from_shell_profiles(
        _scaled_profile(_STRAINER_OUTER, r.cup_scale_r, r.cup_scale_r),
        _scaled_profile(_STRAINER_INNER, r.cup_scale_r, r.cup_scale_r),
        segments=56,
        start_cap="flat",
        end_cap="round",
        lip_samples=7,
    )


def _perforated_strainer_plate(r: ResolvedConfig) -> cq.Workplane:
    """Source `_perforated_strainer_plate` (origin anchor L118-L134): a disc pierced by
    concentric hole rings.  The perforation is the category's recognisability anchor, so
    it stays a real boolean cut; `strainer_ring_count` moves the source's three rings to
    two or four with the same radial spread."""

    plate = cq.Workplane("XY").circle(r.strainer_plate_r_m).extrude(r.strainer_plate_t_m)
    rings = int(r.strainer_ring_count)
    for index in range(rings):
        frac = (
            _RING_FRAC_LO
            if rings == 1
            else _RING_FRAC_LO + (_RING_FRAC_HI - _RING_FRAC_LO) * index / (rings - 1)
        )
        radius = frac * r.strainer_plate_r_m
        count = _RING_COUNTS[min(index, len(_RING_COUNTS) - 1)]
        for step in range(count):
            angle = math.tau * step / count
            cutter = (
                cq.Workplane("XY")
                .center(radius * math.cos(angle), radius * math.sin(angle))
                .circle(r.strainer_hole_r_m)
                .extrude(r.strainer_plate_t_m * 3.0)
                .translate((0.0, 0.0, -r.strainer_plate_t_m))
            )
            plate = plate.cut(cutter)
    return plate


def _ram_profile(r: ResolvedConfig) -> list[tuple[float, float]]:
    """One continuous turned ram, source `_ram_geometry` (origin anchor L137-L161).

    The head cap is lifted to `ram_cap_z0_m` so the guided head never re-enters the beam
    bore at full stroke — the source cap is 1.5 mm wider than its own bore and dips into
    it, which reads as a part-to-part penetration here."""

    sr = r.ram_shaft_r_m
    hr = r.press_head_r_m
    uz = r.ram_z_scale
    points: list[tuple[float, float]] = []

    if r.actuator_style == "screw_handwheel":
        # coarse thread band, source screw fork L148-L171: alternating turned steps.  It
        # starts above the guide boss so the beam bore still runs on the plain shaft and
        # carries the ram; the nut housing above the beam is bored for the thread.
        points.append((0.0, r.screw_len_m))
        z = r.screw_len_m
        step = max(0.0025, r.thread_step_m)
        high = True
        while z > r.thread_start_z_m + step:
            points.append((r.screw_thread_r_m if high else sr, z))
            z -= step
            high = not high
        points.append((sr, r.thread_start_z_m))
    else:
        points.extend(
            [
                (0.0, r.ram_cap_z1_m),
                (sr, r.ram_cap_z1_m),
                (sr * 1.45, r.ram_cap_z1_m - 0.008 * uz),
                (sr * 1.45, r.ram_cap_z0_m + 0.006 * uz),
                (sr, r.ram_cap_z0_m),
            ]
        )

    for key, is_collar, z in _RAM_SHAFT_BAND:
        points.append((r.ram_collar_r_m if is_collar else key * sr, z * uz))
    for key, z in _RAM_HEAD_BAND:
        points.append((key * hr, z * uz))
    # normalise the collar band to the derived collar station
    return points


def _ram_geometry(r: ResolvedConfig) -> LatheGeometry:
    return LatheGeometry(_ram_profile(r), segments=64)


def _rack_solid(r: ResolvedConfig) -> cq.Workplane:
    """Toothed rack on the ram's +X flank, source `_rack_mesh` (rack fork L185-L194).

    Built in millimetres: `RackGear` defaults to length +X / teeth +Y / width +Z, so a
    +90 deg turn about Y followed by -90 deg about Z puts length on +Z and teeth on +X.
    The pitch line lands on local x = 0."""

    scale = 1000.0
    rack = RackGear(
        module=r.gear_module_m * scale,
        length=r.rack_len_m * scale,
        width=r.pinion_width_m * scale,
        height=r.rack_h_m * scale,
    )
    solid = cq.Workplane("XY").newObject([rack.build()])
    solid = solid.rotate((0, 0, 0), (0, 1, 0), 90).rotate((0, 0, 0), (0, 0, 1), -90)
    return solid.translate((0.0, r.pinion_width_m * scale / 2.0, r.rack_len_m * scale))


def _pinion_solid(r: ResolvedConfig) -> cq.Workplane:
    """Involute pinion, source `_pinion_mesh` (rack fork L197-L203).

    Built in millimetres and bored separately: `build()` is called bare because passing
    `bore_d` returns a compound with stray construction solids, and a metre-scale
    involute gear is not watertight."""

    scale = 1000.0
    gear = SpurGear(
        module=r.gear_module_m * scale,
        teeth_number=int(r.pinion_teeth),
        width=r.pinion_width_m * scale,
    )
    solid = cq.Workplane("XY").newObject([gear.build()])
    bore = (
        cq.Workplane("XY")
        .circle(r.pinion_shaft_r_m * scale * 0.98)
        .extrude(r.pinion_width_m * scale * 2.0)
        .translate((0.0, 0.0, -r.pinion_width_m * scale * 0.5))
    )
    solid = solid.cut(bore)
    # centre on the gear's own mid-plane, then stand the axis up on +Y
    solid = solid.translate((0.0, 0.0, -r.pinion_width_m * scale / 2.0))
    return solid.rotate((0, 0, 0), (1, 0, 0), -90)


# --------------------------------------------------------------------------- #
# frame_style
# --------------------------------------------------------------------------- #
def _beam_solid(r: ResolvedConfig) -> cq.Workplane:
    """Upper beam shared by both frames: a filleted bar spanning the frame's columns,
    unioned with the ram guide boss.  Source `_upper_crosshead` (origin anchor L42-L63)
    and the C-frame's throat arm plus guide boss (c_frame fork L54-L69)."""

    if r.frame_style == "twin_post_column":
        y0, y1 = r.beam_front_y_m, r.beam_back_y_m
    else:
        y0, y1 = r.arm_front_y_m, r.column_back_y_m
    depth = y1 - y0
    bar = (
        cq.Workplane("XY")
        .box(2.0 * r.beam_hx_m, depth, r.beam_height_m)
        .edges("|Z")
        .fillet(min(0.009, 0.24 * depth, 0.24 * r.beam_hx_m))
        .translate((0.0, 0.5 * (y0 + y1), 0.5 * (r.beam_bottom_z_m + r.beam_top_z_m)))
    )
    boss = (
        cq.Workplane("XY")
        .center(0.0, r.cup_y_m)
        .circle(r.boss_r_m)
        .extrude(r.boss_top_z_m - r.beam_bottom_z_m)
        .translate((0.0, 0.0, r.beam_bottom_z_m))
    )
    return bar.union(boss)


def _bearing_lug_solid(r: ResolvedConfig) -> cq.Workplane:
    """Lever pivot bearing: a bored bushing standing proud of the beam's front face on a
    short web.  Source `pivot_bearing` (origin anchor L239-L247) is exactly this cylinder
    projecting forward of the crosshead; the bore is new (the source lets the pin sit
    inside solid metal and allows the overlap)."""

    length = r.bearing_y1_m - r.bearing_y0_m
    tube = (
        cq.Workplane("XZ")
        .center(r.pivot_x_m, r.pivot_z_m)
        .circle(r.bearing_r_m)
        .extrude(-length)
        .translate((0.0, r.bearing_y0_m, 0.0))
    )
    web_y1 = r.beam_front_y_m + 0.008
    web_y0 = min(r.bearing_y1_m - 0.002, web_y1 - 0.001)
    if web_y1 - web_y0 > 0.0015:
        web = (
            cq.Workplane("XY")
            .box(2.0 * r.bearing_r_m, web_y1 - web_y0, 2.0 * r.bearing_r_m)
            .translate((r.pivot_x_m, 0.5 * (web_y0 + web_y1), r.pivot_z_m))
        )
        tube = tube.union(web)
    return tube


def _frame_style_twin_post_column_build(r: ResolvedConfig) -> cq.Workplane:
    """Open twin-post gantry, source origin anchor L24-L39 / L42-L63 / L209-L247: a
    two-tier filleted cast base, two chrome guide posts standing at +/-x outboard of the
    cup, and the bored crosshead bridging their tops."""

    lower_h = 0.36 * r.base_height_m
    lower = (
        cq.Workplane("XY")
        .box(r.base_width_m, r.base_depth_m, lower_h)
        .edges("|Z")
        .fillet(0.006)
        .translate((0.0, 0.0, lower_h / 2.0))
    )
    upper_h = r.base_height_m - lower_h
    upper = (
        cq.Workplane("XY")
        .box(0.878 * r.base_width_m, 0.844 * r.base_depth_m, upper_h)
        .edges("|Z")
        .fillet(0.007)
        .translate((0.0, 0.0, lower_h + upper_h / 2.0))
    )
    body = lower.union(upper)
    for x_pos in (-r.post_x_m, r.post_x_m):
        post = (
            cq.Workplane("XY")
            .center(x_pos, r.post_y_m)
            .circle(r.post_radius_m)
            .extrude(r.post_len_m)
            .translate((0.0, 0.0, r.base_height_m - 0.006))
        )
        body = body.union(post)
    return body.union(_beam_solid(r))


def _frame_style_c_arch_throat_build(r: ResolvedConfig) -> cq.Workplane:
    """One cast C-arch, source c_frame fork L29-L92: a solid base, a single rear column
    whose front face is set to clear the cup rim, a throat arm cantilevered forward over
    the cup, a guide boss under the arm front, and one bore through arm and boss.  The
    column stands proud of the arm exactly as the source's does."""

    depth = r.base_hy_back_m + r.base_hy_front_m
    base = (
        cq.Workplane("XY")
        .box(r.base_width_m, depth, r.base_height_m)
        .edges("|Z")
        .fillet(0.008)
        .translate(
            (
                0.0,
                0.5 * (r.base_hy_back_m - r.base_hy_front_m),
                r.base_height_m / 2.0,
            )
        )
    )
    col_z0 = r.base_height_m - 0.008
    column = (
        cq.Workplane("XY")
        .box(
            r.column_w_m,
            r.column_back_y_m - r.column_front_y_m,
            r.column_top_z_m - col_z0,
        )
        .edges("|Z")
        .fillet(min(0.006, 0.24 * r.column_depth_m))
        .translate(
            (
                0.0,
                0.5 * (r.column_front_y_m + r.column_back_y_m),
                0.5 * (col_z0 + r.column_top_z_m),
            )
        )
    )
    guide = (
        cq.Workplane("XY")
        .center(0.0, r.cup_y_m)
        .circle(r.boss_r_m * 1.24)
        .extrude(r.guide_drop_m)
        .translate((0.0, 0.0, r.beam_bottom_z_m - r.guide_drop_m))
    )
    return base.union(column).union(_beam_solid(r)).union(guide)


_FRAME_BUILDERS = {
    "twin_post_column": _frame_style_twin_post_column_build,
    "c_arch_throat": _frame_style_c_arch_throat_build,
}


# --------------------------------------------------------------------------- #
# catch_deck
# --------------------------------------------------------------------------- #
def _catch_deck_flat_drip_disc_build(r: ResolvedConfig) -> list[tuple[str, object, Origin]]:
    """A single polished drip disc laid straight on the base top, source origin anchor
    L221-L226 (`Cylinder(radius=0.068, length=0.007)` at z = 0.0515)."""

    return [
        (
            "deck_disc",
            Cylinder(radius=r.deck_r_m, length=r.deck_disc_h_m + 0.0006),
            Origin(
                xyz=(
                    0.0,
                    r.cup_y_m,
                    r.base_height_m + (r.deck_disc_h_m - 0.0006) / 2.0,
                )
            ),
        )
    ]


def _catch_deck_raised_pedestal_boss_build(
    r: ResolvedConfig,
) -> list[tuple[str, object, Origin]]:
    """A stepped pedestal: a tall circular boss rising out of the base carrying the drip
    disc on top, source bench-clamp fork L41-L46 (`circle(0.074).extrude(0.032)`) with the
    disc of L318-L323 capping it."""

    return [
        (
            "pedestal_boss",
            Cylinder(radius=r.pedestal_r_m, length=r.pedestal_h_m + 0.0006),
            Origin(
                xyz=(
                    0.0,
                    r.cup_y_m,
                    r.base_height_m + (r.pedestal_h_m - 0.0006) / 2.0,
                )
            ),
        ),
        (
            "deck_disc",
            Cylinder(radius=r.deck_r_m, length=r.deck_disc_h_m + 0.0006),
            Origin(
                xyz=(
                    0.0,
                    r.cup_y_m,
                    r.base_height_m + r.pedestal_h_m + (r.deck_disc_h_m - 0.0006) / 2.0,
                )
            ),
        ),
    ]


_DECK_BUILDERS = {
    "flat_drip_disc": _catch_deck_flat_drip_disc_build,
    "raised_pedestal_boss": _catch_deck_raised_pedestal_boss_build,
}


# --------------------------------------------------------------------------- #
# mount_style
# --------------------------------------------------------------------------- #
def _clamp_bracket_solids(r: ResolvedConfig) -> list[tuple[str, cq.Workplane]]:
    """C-clamp bracket hanging under the base, source bench-clamp fork L29-L97.

    The bench slab is gripped between the base underside (z = 0) and the jaw; the throat
    wall is the back stop.  The gussets tie wall to jaw on the OUTBOARD face so nothing
    reaches into the throat."""

    hy = r.base_hy_back_m
    wall_y0 = hy - r.clamp_wall_t_m
    jaw_z0 = r.clamp_jaw_z1_m - r.clamp_jaw_t_m
    solids: list[tuple[str, cq.Workplane]] = []

    wall = (
        cq.Workplane("XY")
        .box(r.clamp_w_m, r.clamp_wall_t_m, 0.004 - jaw_z0)
        .edges("|Y")
        .fillet(0.004)
        .translate((0.0, wall_y0 + r.clamp_wall_t_m / 2.0, 0.5 * (jaw_z0 + 0.004)))
    )

    jaw_y0 = hy - r.clamp_jaw_depth_m
    jaw_y1 = hy + r.clamp_rib_reach_m
    jaw = (
        cq.Workplane("XY")
        .box(0.72 * r.clamp_w_m, jaw_y1 - jaw_y0, r.clamp_jaw_t_m)
        .edges("|Z")
        .fillet(0.004)
        .translate((0.0, 0.5 * (jaw_y0 + jaw_y1), r.clamp_jaw_z1_m - r.clamp_jaw_t_m / 2.0))
    )
    bore = (
        cq.Workplane("XY")
        .center(0.0, r.clamp_screw_y_m)
        .circle(r.clamp_screw_r_m + 0.0008)
        .extrude(r.clamp_jaw_t_m * 3.0)
        .translate((0.0, 0.0, jaw_z0 - r.clamp_jaw_t_m))
    )
    solids.append(("throat_and_jaw", wall.union(jaw.cut(bore))))

    for index, x_pos in enumerate(r.clamp_rib_x):
        rib = (
            cq.Workplane("YZ")
            .moveTo(hy - 0.6 * r.clamp_wall_t_m, 0.0)
            .lineTo(hy + r.clamp_rib_reach_m, 0.0)
            .lineTo(hy - 0.6 * r.clamp_wall_t_m, jaw_z0 + 0.001)
            .close()
            .extrude(r.clamp_rib_t_m)
            .translate((x_pos - r.clamp_rib_t_m / 2.0, 0.0, 0.0))
        )
        solids.append((f"gusset_rib_{index}", rib))
    return solids


def _clamp_screw_solid(r: ResolvedConfig) -> cq.Workplane:
    """Clamping screw with a T-handle crossbar and two ball knobs, source bench-clamp
    fork L249-L276.  Local origin is on the rotation axis at the jaw top."""

    bar_h = r.clamp_screw_r_m * 1.25
    # The crossbar's TOP face clears the jaw underside; the source's own handle sits below
    # the jaw and the jaw is the part the screw turns in.
    handle_z = -(r.clamp_jaw_t_m + 0.004 + bar_h)
    rod = (
        cq.Workplane("XY")
        .circle(r.clamp_screw_r_m)
        .extrude(r.clamp_screw_len_m - handle_z)
        .translate((0.0, 0.0, handle_z))
    )
    handle = (
        cq.Workplane("XY")
        .box(8.0 * r.clamp_screw_r_m, bar_h, bar_h)
        .edges("|Z")
        .fillet(bar_h * 0.28)
        .translate((0.0, 0.0, handle_z + bar_h / 2.0))
    )
    body = rod.union(handle)
    for sign in (-1.0, 1.0):
        knob = (
            cq.Workplane("XY")
            .sphere(bar_h * 0.78)
            .translate((sign * 4.0 * r.clamp_screw_r_m, 0.0, handle_z + bar_h / 2.0))
        )
        body = body.union(knob)
    return body


# --------------------------------------------------------------------------- #
# actuator_style geometry helpers
# --------------------------------------------------------------------------- #
def _lever_arm_geometry(r: ResolvedConfig):
    """Spline-swept lever arm, source `_lever_arm_geometry` (origin anchor L164-L176):
    four control points falling toward the operator with a slight easing."""

    points = [
        (
            frac * r.lever_reach_m,
            0.0,
            -frac * r.lever_reach_m * r.lever_drop_ratio * ease,
        )
        for frac, ease in zip(_ARM_FRACS, _ARM_DROP_EASE)
    ]
    return tube_from_spline_points(
        points,
        radius=r.arm_r_m,
        samples_per_segment=10,
        radial_segments=18,
        cap_ends=True,
    )


def _linkage_geometry(r: ResolvedConfig):
    """Pinned dog-link from the lever arm down to the ram collar, source
    `_linkage_geometry` (origin anchor L179-L190).  The end points are DERIVED from the
    actual pin and collar stations instead of the source's fixed offsets, because the
    collar station moves with the beam height and the ram scale."""

    knee = r.link_knee_local
    end = r.link_end_local
    start = (0.0, 0.0, -0.85 * r.arm_r_m)
    return wire_from_points(
        [start, knee, end],
        radius=r.link_r_m,
        radial_segments=16,
        cap_ends=True,
        corner_mode="miter",
    )


def _handwheel_solid(r: ResolvedConfig) -> cq.Workplane:
    """Spoked handwheel, source screw fork `_handwheel_geometry` (L188-L212): a rim ring
    unioned with a hub and crossing spoke bars, plus a knob stem near the rim.  The hub is
    bored here so the screw runs through it instead of inside it."""

    rim_z0 = r.wheel_hub_h_m - r.wheel_rim_h_m
    ring = (
        cq.Workplane("XY")
        .circle(r.handwheel_r_m)
        .circle(r.handwheel_r_m - r.wheel_rim_t_m)
        .extrude(r.wheel_rim_h_m)
        .translate((0.0, 0.0, rim_z0))
    )
    hub = (
        cq.Workplane("XY")
        .circle(r.wheel_hub_r_m)
        .extrude(r.wheel_hub_h_m + 0.0006)
        .translate((0.0, 0.0, -0.0006))
    )
    wheel = ring.union(hub)
    spoke_t = max(0.008, 0.13 * r.wheel_hub_r_m)
    for index in range(int(r.wheel_spoke_pairs)):
        angle = 180.0 * index / max(1, int(r.wheel_spoke_pairs))
        spoke = (
            cq.Workplane("XY")
            .box(2.0 * (r.handwheel_r_m - r.wheel_rim_t_m * 0.4), spoke_t, spoke_t)
            .translate((0.0, 0.0, rim_z0 + r.wheel_rim_h_m / 2.0))
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle)
        )
        wheel = wheel.union(spoke)
    stem = (
        cq.Workplane("XY")
        .center(r.wheel_knob_r_frac * r.handwheel_r_m, 0.0)
        .circle(max(0.0042, 0.30 * r.knob_r_m))
        .extrude(r.wheel_stem_h_m)
        .translate((0.0, 0.0, rim_z0))
    )
    wheel = wheel.union(stem)
    bore = (
        cq.Workplane("XY")
        .circle(r.nut_bore_r_m)
        .extrude(r.wheel_hub_h_m * 3.0)
        .translate((0.0, 0.0, -r.wheel_hub_h_m))
    )
    return wheel.cut(bore)


# --------------------------------------------------------------------------- #
# grip_style
# --------------------------------------------------------------------------- #
def _grip_frame(
    tip: tuple[float, float, float],
    along: tuple[float, float, float],
    cross: tuple[float, float, float],
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    norm = math.sqrt(sum(component * component for component in along)) or 1.0
    unit = tuple(component / norm for component in along)
    cnorm = math.sqrt(sum(component * component for component in cross)) or 1.0
    cunit = tuple(component / cnorm for component in cross)
    return unit, cunit


def _grip_visuals(
    r: ResolvedConfig,
    tip: tuple[float, float, float],
    along: tuple[float, float, float],
    cross: tuple[float, float, float],
) -> list[tuple[str, object, Origin, str]]:
    """Operator hand interface at the actuator tip.

    `along` is the arm's own outward direction at the tip and `cross` the transverse
    direction the tommy bar uses.  Every candidate overlaps the arm end so the visuals
    weld to it inside the actuator part."""

    unit, cunit = _grip_frame(tip, along, cross)
    pitch = math.asin(_clamp(-unit[2], -1.0, 1.0))
    yaw = math.atan2(unit[1], unit[0])
    cpitch = math.asin(_clamp(-cunit[2], -1.0, 1.0))
    cyaw = math.atan2(cunit[1], cunit[0])
    out: list[tuple[str, object, Origin, str]] = []

    def at(distance: float, direction) -> tuple[float, float, float]:
        return tuple(tip[i] + direction[i] * distance for i in range(3))

    if r.grip_style == "ball_knob":
        # Source rack fork L365-L378: a bare spherical knob on a plain arm end.
        out.append(
            (
                "ball_knob",
                Sphere(radius=r.knob_r_m),
                Origin(xyz=at(r.knob_r_m * 0.55, unit)),
                "grip",
            )
        )
    elif r.grip_style == "sleeve_and_ball":
        # Source origin anchor L313-L339: a coaxial turned sleeve plus a ball end cap.
        centre = at(r.grip_len_m * 0.5 - 0.004, unit)
        out.append(
            (
                "grip_sleeve",
                Cylinder(radius=r.grip_sleeve_r_m, length=r.grip_len_m),
                Origin(xyz=centre, rpy=(0.0, (math.pi / 2.0) + pitch, yaw)),
                "grip",
            )
        )
        out.append(
            (
                "grip_end_ball",
                Sphere(radius=r.knob_r_m),
                Origin(xyz=at(r.grip_len_m - 0.004 + r.knob_r_m * 0.45, unit)),
                "chrome",
            )
        )
    else:
        # Source bench-clamp fork L249-L276: a tommy bar across the arm with a ball at
        # each end.
        bar_t = r.knob_r_m * 1.25
        out.append(
            (
                "tee_crossbar",
                Box((2.0 * r.tee_half_m, bar_t, bar_t)),
                Origin(
                    xyz=at(bar_t * 0.35, unit),
                    rpy=(0.0, cpitch, cyaw),
                ),
                "grip",
            )
        )
        for index, sign in enumerate((-1.0, 1.0)):
            centre = at(bar_t * 0.35, unit)
            centre = tuple(
                centre[i] + cunit[i] * sign * (r.tee_half_m - bar_t * 0.2) for i in range(3)
            )
            out.append(
                (
                    f"tee_knob_{index}",
                    Sphere(radius=r.knob_r_m),
                    Origin(xyz=centre),
                    "chrome",
                )
            )
    return out


# --------------------------------------------------------------------------- #
# Frame assembly
# --------------------------------------------------------------------------- #
def _frame_cuts(r: ResolvedConfig, body: cq.Workplane) -> cq.Workplane:
    """Every opening a moving member actually needs, cut AFTER the frame is welded:
    the ram bore, the lever bearing bore, the rack/pinion window and shaft bore, and the
    nut-housing bore (MECHANICAL_PRIORS section 7)."""

    bore = (
        cq.Workplane("XY")
        .center(0.0, r.cup_y_m)
        .circle(r.ram_bore_r_m)
        .extrude(r.boss_top_z_m - r.beam_bottom_z_m + 0.14)
        .translate((0.0, 0.0, r.beam_bottom_z_m - 0.07))
    )
    body = body.cut(bore)

    if r.actuator_style == "lever_linkage":
        pin_bore = (
            cq.Workplane("XZ")
            .center(r.pivot_x_m, r.pivot_z_m)
            .circle(r.lever_pin_r_m + 0.0007)
            .extrude(-(r.bearing_y1_m - r.bearing_y0_m + 0.003))
            .translate((0.0, r.bearing_y0_m - 0.001, 0.0))
        )
        body = body.cut(pin_bore)
    elif r.actuator_style == "rack_pinion_crank":
        half_w = r.pinion_width_m / 2.0 + 0.002
        x0 = 0.4 * r.ram_shaft_r_m
        x1 = r.pinion_x_m + r.pinion_ra_m + 0.003
        z0 = r.beam_bottom_z_m - r.guide_drop_m - 0.002
        z1 = r.boss_top_z_m + 0.002
        window = (
            cq.Workplane("XY")
            .box(x1 - x0, 2.0 * half_w, z1 - z0)
            .translate((0.5 * (x0 + x1), r.cup_y_m, 0.5 * (z0 + z1)))
        )
        body = body.cut(window)
        shaft_bore = (
            cq.Workplane("XZ")
            .center(r.pinion_x_m, r.pinion_z_m)
            .circle(r.pinion_shaft_r_m + 0.0008)
            .extrude(-(r.crank_hub_y_m - r.cup_y_m + 0.02))
            .translate((0.0, r.cup_y_m, 0.0))
        )
        body = body.cut(shaft_bore)
    return body


def _build_frame(model: ArticulatedObject, r: ResolvedConfig):
    frame = model.part(
        "frame",
        meta={
            "role": "press_frame",
            "frame_style": r.frame_style,
            "mount_style": r.mount_style,
            "guide_column_count": 2 if r.frame_style == "twin_post_column" else 1,
        },
    )
    body = _FRAME_BUILDERS[r.frame_style](r)
    if r.actuator_style == "lever_linkage":
        body = body.union(_bearing_lug_solid(r))
    body = _frame_cuts(r, body)
    frame.visual(
        mesh_from_cadquery(body, f"frame_style__{r.frame_style}__body", tolerance=0.0018),
        material="frame",
        name=f"frame_style__{r.frame_style}__body", material_class_id=("metal.aluminum_bare" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_aged"),
    )

    for local_name, geometry, origin in _DECK_BUILDERS[r.catch_deck](r):
        frame.visual(
            geometry,
            origin=origin,
            material="vessel",
            name=f"catch_deck__{r.catch_deck}__{local_name}", material_class_id="metal.stainless_matte",
        )

    if r.actuator_style == "rack_pinion_crank":
        boss = (
            cq.Workplane("XY")
            .circle(r.pinion_shaft_r_m + 0.007)
            .circle(r.pinion_shaft_r_m + 0.0008)
            .extrude(0.0145)
            .translate((0.0, 0.0, -0.0005))
        )
        frame.visual(
            mesh_from_cadquery(
                boss,
                "actuator_style__rack_pinion_crank__pinion_bearing_boss",
                tolerance=0.0012,
            ),
            origin=Origin(
                xyz=(r.pinion_x_m, r.beam_back_y_m, r.pinion_z_m),
                rpy=(-math.pi / 2.0, 0.0, 0.0),
            ),
            material="frame",
            name="actuator_style__rack_pinion_crank__pinion_bearing_boss", material_class_id=("metal.aluminum_bare" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_aged"),
        )
    elif r.actuator_style == "screw_handwheel":
        housing = (
            cq.Workplane("XY")
            .circle(r.nut_outer_r_m)
            .circle(r.nut_bore_r_m)
            .extrude(r.nut_h_m + 0.0006)
            .translate((0.0, 0.0, -0.0006))
        )
        frame.visual(
            mesh_from_cadquery(
                housing,
                "actuator_style__screw_handwheel__nut_housing",
                tolerance=0.0012,
            ),
            origin=Origin(xyz=(0.0, r.cup_y_m, r.beam_top_z_m)),
            material="frame",
            name="actuator_style__screw_handwheel__nut_housing", material_class_id=("metal.aluminum_bare" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_aged"),
        )

    if r.mount_style == "bench_clamp_bracket":
        for local_name, solid in _clamp_bracket_solids(r):
            frame.visual(
                mesh_from_cadquery(
                    solid,
                    f"mount_style__bench_clamp_bracket__{local_name}",
                    tolerance=0.0030,
                ),
                material="frame",
                name=f"mount_style__bench_clamp_bracket__{local_name}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_aged"),
            )
    return frame


# --------------------------------------------------------------------------- #
# mount_style assembly
# --------------------------------------------------------------------------- #
def _build_mount(model: ArticulatedObject, r: ResolvedConfig, frame) -> list:
    """`corner_foot_pads` emits one rubber pad PART and one FIXED joint per station,
    exactly as the origin anchor's indexed loop does (L249-L260, L351-L358).
    `bench_clamp_bracket` emits the clamp screw on a CONTINUOUS joint (L463-L472); its
    repeated element is the gusset rib set, which lives on the frame."""

    parts: list = []
    if r.mount_style == "corner_foot_pads":
        for index, (x_pos, y_pos) in enumerate(r.foot_stations):
            foot = model.part(
                f"mount_style__corner_foot_pads__foot_{index}",
                meta={"role": "stand_foot", "foot_index": index},
            )
            foot.visual(
                Cylinder(radius=r.foot_radius_m, length=r.foot_h_m + 0.0005),
                origin=Origin(xyz=(0.0, 0.0, -(r.foot_h_m - 0.0005) / 2.0)),
                material="rubber",
                name=f"mount_style__corner_foot_pads__pad_{index}", material_class_id="rubber.smooth_plain",
            )
            model.articulation(
                f"mount_style__corner_foot_pads__frame_to_foot_{index}",
                ArticulationType.FIXED,
                parent=frame,
                child=foot,
                origin=Origin(xyz=(x_pos, y_pos, 0.0)),
                meta={"role": "bench stand-off pad"},
            )
            parts.append(foot)
        return parts

    screw = model.part(
        "mount_style__bench_clamp_bracket__clamp_screw",
        meta={"role": "clamp_screw"},
    )
    screw.visual(
        mesh_from_cadquery(
            _clamp_screw_solid(r),
            "mount_style__bench_clamp_bracket__screw_body",
            tolerance=0.0010,
        ),
        material="chrome",
        name="mount_style__bench_clamp_bracket__screw_body", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    screw.visual(
        Cylinder(radius=r.clamp_pad_r_m, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, r.clamp_screw_len_m + 0.003)),
        material="rubber",
        name="mount_style__bench_clamp_bracket__clamp_pad", material_class_id="rubber.smooth_plain",
    )
    mate = mate_axes(
        AxisInterface(
            name="frame.clamp_screw_bore",
            point=(0.0, r.clamp_screw_y_m, r.clamp_jaw_z1_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.clamp_screw_r_m + 0.0008,
        ),
        AxisInterface(
            name="clamp_screw.stem",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.clamp_screw_r_m,
        ),
    )
    joint = model.articulation(
        "mount_style__bench_clamp_bracket__frame_to_clamp_screw",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=screw,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=80.0, velocity=3.0),
        meta={"role": "continuous rotation tightens or loosens the bench clamp"},
    )
    register_interface_mate(model, joint.name, mate)
    parts.append(screw)
    return parts


# --------------------------------------------------------------------------- #
# actuator_style assembly
# --------------------------------------------------------------------------- #
def _build_lever_linkage(model: ArticulatedObject, r: ResolvedConfig, frame, ram) -> list:
    lever = model.part(
        "actuator_style__lever_linkage__lever",
        meta={"role": "press_lever", "operator_control": True},
    )
    lever.visual(
        Cylinder(radius=r.lever_pin_r_m, length=r.lever_pin_len_m),
        origin=Origin(
            xyz=(0.0, r.lever_pin_len_m / 2.0 - 0.6 * r.arm_r_m, 0.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material="chrome",
        name="actuator_style__lever_linkage__pivot_pin", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    lever.visual(
        mesh_from_geometry(_lever_arm_geometry(r), "actuator_style__lever_linkage__arm_tube"),
        material="chrome",
        name="actuator_style__lever_linkage__arm_tube", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    tip = (r.lever_reach_m, 0.0, -r.lever_reach_m * r.lever_drop_ratio)
    along = (1.0, 0.0, -r.lever_drop_ratio)
    for local_name, geometry, origin, material in _grip_visuals(r, tip, along, (0.0, 1.0, 0.0)):
        lever.visual(
            geometry,
            origin=origin,
            material=material,
            name=f"grip_style__{r.grip_style}__{local_name}", material_class_id="plastic.opaque_glossy_molded",
        )

    mate = mate_axes(
        AxisInterface(
            name="frame.lever_pivot_bore",
            point=(r.pivot_x_m, r.mech_y_m, r.pivot_z_m),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.lever_pin_r_m + 0.0007,
        ),
        AxisInterface(
            name="lever.pivot_pin",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.lever_pin_r_m,
        ),
    )
    lever_joint = model.articulation(
        "actuator_style__lever_linkage__frame_to_lever",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=lever,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=520.0,
            velocity=1.5,
            lower=r.lever_lower_rad,
            upper=r.lever_upper_rad,
        ),
        meta={"role": "positive motion pulls the long handle downward"},
    )
    register_interface_mate(model, lever_joint.name, mate)

    linkage = model.part(
        "actuator_style__lever_linkage__linkage",
        meta={"role": "drive_link"},
    )
    linkage.visual(
        mesh_from_geometry(_linkage_geometry(r), "actuator_style__lever_linkage__linkage_rod"),
        material="chrome",
        name="actuator_style__lever_linkage__linkage_rod", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    link_mate = mate_axes(
        AxisInterface(
            name="lever.link_pin",
            point=r.link_pin_local,
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.link_r_m + 0.0006,
        ),
        AxisInterface(
            name="linkage.eye",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.link_r_m,
        ),
    )
    link_joint = model.articulation(
        "actuator_style__lever_linkage__lever_to_linkage",
        ArticulationType.REVOLUTE,
        parent=lever,
        child=linkage,
        origin=link_mate.origin,
        axis=link_mate.axis,
        motion_limits=MotionLimits(
            effort=900.0,
            velocity=2.0,
            lower=-r.link_swing_rad,
            upper=r.link_swing_rad,
        ),
        meta={"role": "pin joint lets the dog-link follow the lever arc"},
    )
    register_interface_mate(model, link_joint.name, link_mate)
    return [lever, linkage]


def _build_rack_pinion_crank(model: ArticulatedObject, r: ResolvedConfig, frame, ram) -> list:
    pinion = model.part(
        "actuator_style__rack_pinion_crank__pinion",
        meta={"role": "pinion_drive", "teeth": int(r.pinion_teeth)},
    )
    pinion.visual(
        mesh_from_cadquery(
            _pinion_solid(r),
            "actuator_style__rack_pinion_crank__pinion_gear",
            tolerance=0.35,
            unit_scale=0.001,
        ),
        material="chrome",
        name="actuator_style__rack_pinion_crank__pinion_gear", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    shaft_len = (r.crank_hub_y_m + 0.012) - (r.cup_y_m - r.pinion_width_m / 2.0)
    pinion.visual(
        Cylinder(radius=r.pinion_shaft_r_m, length=shaft_len),
        origin=Origin(
            xyz=(
                0.0,
                0.5 * shaft_len - r.pinion_width_m / 2.0,
                0.0,
            ),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material="chrome",
        name="actuator_style__rack_pinion_crank__pinion_shaft", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    hub_y = r.crank_hub_y_m - r.cup_y_m
    pinion.visual(
        Cylinder(radius=r.pinion_shaft_r_m * 2.1, length=0.020),
        origin=Origin(xyz=(0.0, hub_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="chrome",
        name="actuator_style__rack_pinion_crank__crank_hub", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    arm_r = max(0.005, 0.055 * r.crank_reach_m)
    pinion.visual(
        Cylinder(radius=arm_r, length=r.crank_reach_m),
        origin=Origin(
            xyz=(r.crank_reach_m / 2.0, hub_y, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material="chrome",
        name="actuator_style__rack_pinion_crank__crank_arm", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    tip = (r.crank_reach_m, hub_y, 0.0)
    for local_name, geometry, origin, material in _grip_visuals(
        r, tip, (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)
    ):
        pinion.visual(
            geometry,
            origin=origin,
            material=material,
            name=f"grip_style__{r.grip_style}__{local_name}", material_class_id="plastic.opaque_glossy_molded",
        )

    mate = mate_axes(
        AxisInterface(
            name="frame.pinion_bearing_bore",
            point=(r.pinion_x_m, r.cup_y_m, r.pinion_z_m),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.pinion_shaft_r_m + 0.0008,
        ),
        AxisInterface(
            name="pinion.shaft",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=r.pinion_shaft_r_m,
        ),
    )
    joint = model.articulation(
        "actuator_style__rack_pinion_crank__frame_to_pinion",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=pinion,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(
            effort=520.0,
            velocity=2.0,
            lower=0.0,
            upper=r.crank_upper_rad,
        ),
        meta={"role": "side crank rotates the pinion to drive the rack ram downward"},
    )
    register_interface_mate(model, joint.name, mate)
    return [pinion]


def _build_screw_handwheel(model: ArticulatedObject, r: ResolvedConfig, frame, ram) -> list:
    wheel = model.part(
        "actuator_style__screw_handwheel__handwheel",
        meta={"role": "screw_handwheel", "operator_control": True},
    )
    wheel.visual(
        mesh_from_cadquery(
            _handwheel_solid(r),
            "actuator_style__screw_handwheel__wheel_body",
            tolerance=0.0012,
        ),
        material="frame",
        name="actuator_style__screw_handwheel__wheel_body", material_class_id=("metal.aluminum_bare" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_aged"),
    )
    tip = (
        r.wheel_knob_r_frac * r.handwheel_r_m,
        0.0,
        r.wheel_hub_h_m - r.wheel_rim_h_m + r.wheel_stem_h_m,
    )
    for local_name, geometry, origin, material in _grip_visuals(
        r, tip, (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)
    ):
        wheel.visual(
            geometry,
            origin=origin,
            material=material,
            name=f"grip_style__{r.grip_style}__{local_name}", material_class_id="plastic.opaque_glossy_molded",
        )

    mate = mate_axes(
        AxisInterface(
            name="frame.nut_housing_axis",
            point=(0.0, r.cup_y_m, r.wheel_origin_z_m),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.nut_bore_r_m,
        ),
        AxisInterface(
            name="handwheel.hub_bore",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=r.nut_bore_r_m,
        ),
    )
    joint = model.articulation(
        "actuator_style__screw_handwheel__frame_to_handwheel",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=wheel,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(effort=180.0, velocity=2.5),
        meta={"role": "operator turns the wheel about the vertical screw axis"},
    )
    register_interface_mate(model, joint.name, mate)
    return [wheel]


_ACTUATOR_BUILDERS = {
    "lever_linkage": _build_lever_linkage,
    "rack_pinion_crank": _build_rack_pinion_crank,
    "screw_handwheel": _build_screw_handwheel,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_juicer_press_with_handle(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "juicer_press_with_handle",
            "slot_choices": tuple(slot_choices_for_config(r).items()),
            "base_support_count": r.base_support_count,
            "source_pool_reviewed": "5 workbench records / rev_000001",
        },
    )
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)

    frame = _build_frame(model, r)

    cup = model.part(
        "cup",
        meta={"role": "collector_cup", "removable": True},
    )
    cup.visual(
        mesh_from_geometry(_cup_geometry(r), "cup__collector__shell"),
        material="vessel",
        name="cup__collector__shell", material_class_id="metal.stainless_matte",
    )

    strainer = model.part(
        "strainer",
        meta={"role": "strainer", "removable": True, "ring_count": r.strainer_ring_count},
    )
    strainer.visual(
        mesh_from_geometry(_strainer_shell_geometry(r), "strainer__screen__shell"),
        material="vessel",
        name="strainer__screen__shell", material_class_id="metal.stainless_matte",
    )
    strainer.visual(
        mesh_from_cadquery(
            _perforated_strainer_plate(r), "strainer__screen__plate", tolerance=0.0006
        ),
        material="vessel",
        name="strainer__screen__perforated_plate", material_class_id="metal.stainless_matte",
    )

    ram = model.part(
        "ram",
        meta={"role": "press_ram", "guided": True, "actuator_style": r.actuator_style},
    )
    ram.visual(
        mesh_from_geometry(_ram_geometry(r), "ram__press__body"),
        material="chrome",
        name="ram__press__body", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
    )
    if r.actuator_style == "rack_pinion_crank":
        ram.visual(
            mesh_from_cadquery(
                _rack_solid(r),
                "actuator_style__rack_pinion_crank__rack_teeth",
                tolerance=0.35,
                unit_scale=0.001,
            ),
            origin=Origin(xyz=(r.rack_x0_m, 0.0, r.rack_z0_m)),
            material="chrome",
            name="actuator_style__rack_pinion_crank__rack_teeth", material_class_id=("metal.chrome_polished" if r.palette_style in {"chrome_bench", "cast_iron_black", "enamel_red", "stainless_pro"} else "metal.brass_polished"),
        )

    # ---- vessel stack -----------------------------------------------------
    model.articulation(
        "frame_to_cup",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=cup,
        origin=Origin(xyz=(0.0, r.cup_y_m, r.cup_seat_z_m)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=35.0, velocity=0.20, lower=0.0, upper=r.lift_limit_m),
        meta={"role": "vertical removal from the drip deck"},
    )
    model.articulation(
        "cup_to_strainer",
        ArticulationType.PRISMATIC,
        parent=cup,
        child=strainer,
        origin=Origin(xyz=(0.0, 0.0, r.strainer_seat_local_m)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.20, lower=0.0, upper=r.lift_limit_m),
        meta={"role": "vertical removal from the collector cup"},
    )
    model.articulation(
        "frame_to_ram",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=ram,
        origin=Origin(xyz=(0.0, r.cup_y_m, r.ram_origin_z_m)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=1400.0, velocity=0.22, lower=0.0, upper=r.ram_travel_m),
        meta={"role": "guided downward pressing stroke into the cup"},
    )

    _build_mount(model, r, frame)
    _ACTUATOR_BUILDERS[r.actuator_style](model, r, frame, ram)
    return model


def build_seeded_pictureX_0611_juicer_press_with_handle(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_juicer_press_with_handle(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Authored tests
# --------------------------------------------------------------------------- #
def _meshes_materialized(model: ArticulatedObject) -> bool:
    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def _parts_by_role(model: ArticulatedObject, role: str) -> list:
    return [part for part in model.parts if part.meta.get("role") == role]


def _aabb_center(aabb):
    if aabb is None:
        return None
    low, high = aabb
    return tuple((low[index] + high[index]) / 2.0 for index in range(3))


def run_pictureX_0611_juicer_press_with_handle_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    joints = {joint.name: joint for joint in model.articulations}
    exact = _meshes_materialized(model)

    frames = _parts_by_role(model, "press_frame")
    cups = _parts_by_role(model, "collector_cup")
    strainers = _parts_by_role(model, "strainer")
    rams = _parts_by_role(model, "press_ram")
    feet = _parts_by_role(model, "stand_foot")
    clamp_screws = _parts_by_role(model, "clamp_screw")
    levers = _parts_by_role(model, "press_lever")
    links = _parts_by_role(model, "drive_link")
    pinions = _parts_by_role(model, "pinion_drive")
    wheels = _parts_by_role(model, "screw_handwheel")

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    if cups:
        ctx.allow_isolated_part(
            cups[0],
            reason=(
                "The collector cup is a removable vessel carried by its own vertical "
                "removal joint; at any lift above 0 it is off its drip deck by design "
                "(source frame_to_cup PRISMATIC 0..0.080). Its seated contact is asserted "
                "separately by 'collector cup seats on the drip deck'."
            ),
        )
    if strainers:
        ctx.allow_isolated_part(
            strainers[0],
            reason=(
                "The perforated strainer is a removable insert carried by its own vertical "
                "removal joint out of the cup mouth (source cup_to_strainer PRISMATIC "
                "0..0.055). Its nested fit is asserted separately by 'strainer nests inside "
                "the collector cup'."
            ),
        )
    ctx.fail_if_isolated_parts()
    ctx.fail_if_interface_mate_mismatch()
    if exact:
        ctx.fail_if_part_contains_disconnected_geometry_islands()
        ctx.fail_if_parts_overlap_in_current_pose()
        ctx.fail_if_articulation_origin_far_from_geometry(tol=0.030)

    # ---- category anchors --------------------------------------------------
    ctx.check(
        "bench juicer press core part set",
        len(frames) == 1
        and len(cups) == 1
        and len(strainers) == 1
        and len(rams) == 1
        and len(model.root_parts()) == 1
        and model.root_parts()[0].name == "frame",
        details=(
            f"frames={len(frames)} cups={len(cups)} strainers={len(strainers)} "
            f"rams={len(rams)} roots={[part.name for part in model.root_parts()]}"
        ),
    )

    ram_joint = joints.get("frame_to_ram")
    cup_joint = joints.get("frame_to_cup")
    strainer_joint = joints.get("cup_to_strainer")
    ctx.check(
        "cup strainer and ram ride the same vertical stack",
        ram_joint is not None
        and cup_joint is not None
        and strainer_joint is not None
        and ram_joint.articulation_type == ArticulationType.PRISMATIC
        and cup_joint.articulation_type == ArticulationType.PRISMATIC
        and strainer_joint.articulation_type == ArticulationType.PRISMATIC
        and abs(ram_joint.origin.xyz[0] - cup_joint.origin.xyz[0]) < 1e-6
        and abs(ram_joint.origin.xyz[1] - cup_joint.origin.xyz[1]) < 1e-6
        and abs(ram_joint.axis[2]) > 0.999
        and abs(cup_joint.axis[2]) > 0.999,
        details=(
            f"ram={ram_joint.origin.xyz if ram_joint else None} "
            f"cup={cup_joint.origin.xyz if cup_joint else None}"
        ),
    )

    ctx.check(
        "perforated strainer screen is present and nested in the cup mouth",
        strainers
        and strainers[0].get_visual("strainer__screen__perforated_plate") is not None
        and strainers[0].get_visual("strainer__screen__shell") is not None
        and r.strainer_plate_r_m < r.cup_rim_r_m
        and 0.0 < r.strainer_seat_local_m < r.cup_height_m,
        details=(
            f"plate_r={r.strainer_plate_r_m:.4f} cup_rim={r.cup_rim_r_m:.4f} "
            f"seat={r.strainer_seat_local_m:.4f} rings={r.strainer_ring_count}"
        ),
    )

    # The recognisability invariant: the head is clear of the strainer at rest and
    # still clear of the perforated plate at the bottom of the stroke.
    plate_top = r.cup_seat_z_m + r.strainer_seat_local_m + r.strainer_plate_t_m
    tip_full = r.ram_tip_rest_z_m - r.ram_travel_m
    ctx.check(
        "press head clears the strainer at both stroke limits",
        r.head_gap_m >= 0.010
        and tip_full > plate_top + 0.0035
        and tip_full < r.stack_top_z_m - 0.0025
        and 2.0 * r.lift_limit_m <= r.press_clear_m + 0.0035,
        details=(
            f"head_gap={r.head_gap_m:.4f} tip_rest={r.ram_tip_rest_z_m:.4f} "
            f"tip_full={tip_full:.4f} plate_top={plate_top:.4f} "
            f"stack_top={r.stack_top_z_m:.4f} travel={r.ram_travel_m:.4f} "
            f"dip={r.head_dip_m:.4f} press_clear={r.press_clear_m:.4f} "
            f"lift={r.lift_limit_m:.4f}"
        ),
    )
    ctx.check(
        "raised press head fits inside the cup and strainer mouth",
        r.press_head_r_m < 0.955 * r.cup_rim_r_m
        and r.press_head_r_m < 0.818 * r.cup_rim_r_m + 1e-9,
        details=f"head_r={r.press_head_r_m:.4f} cup_rim={r.cup_rim_r_m:.4f}",
    )

    if exact and rams and cups:
        ctx.expect_origin_distance(
            rams[0],
            cups[0],
            axes="xy",
            max_dist=0.0015,
            name="press ram is centered over the collector cup",
        )
        ctx.expect_gap(
            rams[0],
            strainers[0],
            axis="z",
            min_gap=0.012,
            max_gap=0.075,
            positive_elem="ram__press__body",
            negative_elem="strainer__screen__shell",
            name="raised press head clears the strainer",
        )
        ctx.expect_within(
            strainers[0],
            cups[0],
            axes="xy",
            inner_elem="strainer__screen__shell",
            outer_elem="cup__collector__shell",
            margin=0.0005,
            name="strainer nests inside the collector cup",
        )
        ctx.expect_contact(
            cups[0],
            frames[0],
            elem_a="cup__collector__shell",
            elem_b=f"catch_deck__{r.catch_deck}__deck_disc",
            contact_tol=0.0015,
            name="collector cup seats on the drip deck",
        )

    # ---- mount -------------------------------------------------------------
    if r.mount_style == "corner_foot_pads":
        foot_joints = [
            name
            for name in joints
            if name.startswith("mount_style__corner_foot_pads__frame_to_foot_")
        ]
        ctx.check(
            "every stand foot has its own fixed joint under the base",
            len(feet) == r.base_support_count
            and len(foot_joints) == r.base_support_count
            and all(
                joints[name].articulation_type == ArticulationType.FIXED for name in foot_joints
            )
            and all(
                abs(joints[name].origin.xyz[0]) <= r.base_hx_m + 1e-9
                and joints[name].origin.xyz[1] >= -r.base_hy_front_m - 1e-9
                and joints[name].origin.xyz[1] <= r.base_hy_back_m + 1e-9
                for name in foot_joints
            ),
            details=f"feet={len(feet)} joints={len(foot_joints)} N={r.base_support_count}",
        )
    else:
        screw_joint = joints.get("mount_style__bench_clamp_bracket__frame_to_clamp_screw")
        ribs = [
            visual
            for visual in frames[0].visuals
            if "bench_clamp_bracket__gusset_rib_" in (visual.name or "")
        ]
        ctx.check(
            "clamp screw closes the bench throat on a vertical continuous axis",
            len(clamp_screws) == 1
            and screw_joint is not None
            and screw_joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(screw_joint.axis[2]) > 0.999
            and len(ribs) == r.base_support_count
            and r.clamp_screw_len_m + 0.007 < r.clamp_throat_h_m,
            details=(
                f"screws={len(clamp_screws)} ribs={len(ribs)} "
                f"N={r.base_support_count} throat={r.clamp_throat_h_m:.4f}"
            ),
        )

    # ---- actuator ----------------------------------------------------------
    if r.actuator_style == "lever_linkage":
        lever_joint = joints.get("actuator_style__lever_linkage__frame_to_lever")
        link_joint = joints.get("actuator_style__lever_linkage__lever_to_linkage")
        ctx.check(
            "hand actuator drives the ram axis",
            len(levers) == 1
            and len(links) == 1
            and lever_joint is not None
            and link_joint is not None
            and lever_joint.articulation_type == ArticulationType.REVOLUTE
            and link_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(lever_joint.axis[1]) > 0.999
            and str(link_joint.parent) == levers[0].name,
            details=f"levers={len(levers)} links={len(links)}",
        )
        if lever_joint is not None and levers:
            grip_elem = (
                "grip_style__ball_knob__ball_knob"
                if r.grip_style == "ball_knob"
                else (
                    "grip_style__sleeve_and_ball__grip_sleeve"
                    if r.grip_style == "sleeve_and_ball"
                    else "grip_style__tee_bar_knobs__tee_crossbar"
                )
            )
            rest = _aabb_center(ctx.part_element_world_aabb(levers[0], elem=grip_elem))
            with ctx.pose({lever_joint: r.lever_upper_rad}):
                down = _aabb_center(ctx.part_element_world_aabb(levers[0], elem=grip_elem))
            ctx.check(
                "lever positive motion lowers the operator grip",
                rest is not None
                and down is not None
                and down[2] < rest[2] - 0.020
                and down[2] > 0.010,
                details=f"rest={rest} down={down}",
            )
    elif r.actuator_style == "rack_pinion_crank":
        pinion_joint = joints.get("actuator_style__rack_pinion_crank__frame_to_pinion")
        ctx.check(
            "hand actuator drives the ram axis",
            len(pinions) == 1
            and pinion_joint is not None
            and pinion_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(pinion_joint.axis[1]) > 0.999
            and rams
            and rams[0].get_visual("actuator_style__rack_pinion_crank__rack_teeth") is not None
            and abs(r.pinion_x_m - r.rack_x0_m - r.pinion_r0_m - r.gear_backlash_m) < 1e-6
            and r.pinion_ra_m > r.pinion_r0_m + r.gear_backlash_m,
            details=(
                f"pinions={len(pinions)} r0={r.pinion_r0_m:.4f} "
                f"teeth={r.pinion_teeth} module_mm={r.gear_module_mm:.3f}"
            ),
        )
        ctx.check(
            "pinion sweep matches the ram stroke",
            abs(r.crank_upper_rad * r.pinion_r0_m - r.ram_travel_m) < 1e-6
            and 0.9 < r.crank_upper_rad <= 2.0 + 1e-9,
            details=f"upper={r.crank_upper_rad:.4f} travel={r.ram_travel_m:.4f}",
        )
        if pinion_joint is not None and pinions:
            rest = _aabb_center(
                ctx.part_element_world_aabb(
                    pinions[0], elem="actuator_style__rack_pinion_crank__crank_arm"
                )
            )
            with ctx.pose({pinion_joint: r.crank_upper_rad}):
                turned = _aabb_center(
                    ctx.part_element_world_aabb(
                        pinions[0], elem="actuator_style__rack_pinion_crank__crank_arm"
                    )
                )
            ctx.check(
                "crank rotation sweeps the crank arm",
                rest is not None and turned is not None and abs(turned[0] - rest[0]) > 0.020,
                details=f"rest={rest} turned={turned}",
            )
    else:
        wheel_joint = joints.get("actuator_style__screw_handwheel__frame_to_handwheel")
        ctx.check(
            "hand actuator drives the ram axis",
            len(wheels) == 1
            and wheel_joint is not None
            and wheel_joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(wheel_joint.axis[2]) > 0.999
            and abs(wheel_joint.origin.xyz[0]) < 1e-6
            and abs(wheel_joint.origin.xyz[1] - r.cup_y_m) < 1e-6,
            details=f"wheels={len(wheels)} origin_z={r.wheel_origin_z_m:.4f}",
        )
        ctx.check(
            "the screw stays engaged in the wheel hub at full stroke",
            r.screw_len_m - r.ram_travel_m
            > (r.wheel_origin_z_m - r.ram_origin_z_m) - r.wheel_hub_h_m,
            details=(
                f"screw_len={r.screw_len_m:.4f} travel={r.ram_travel_m:.4f} "
                f"hub_h={r.wheel_hub_h_m:.4f}"
            ),
        )
        if wheel_joint is not None and wheels:
            elem = "actuator_style__screw_handwheel__wheel_body"
            rest = ctx.part_element_world_aabb(wheels[0], elem=elem)
            with ctx.pose({wheel_joint: math.pi / 2.0}):
                turned = ctx.part_element_world_aabb(wheels[0], elem=elem)
            ctx.check(
                "handwheel turns about the vertical screw axis",
                rest is not None and turned is not None and abs(rest[1][2] - turned[1][2]) < 0.002,
                details=f"rest={rest} turned={turned}",
            )

    # ---- ram stroke --------------------------------------------------------
    if ram_joint is not None and rams:
        rest = ctx.part_world_position(rams[0])
        with ctx.pose({ram_joint: r.ram_travel_m}):
            down = ctx.part_world_position(rams[0])
        ctx.check(
            "guided ram travels downward into the cup",
            rest is not None and down is not None and down[2] < rest[2] - 0.9 * r.ram_travel_m,
            details=f"rest={rest} down={down}",
        )
    if cup_joint is not None and cups:
        rest = ctx.part_world_position(cups[0])
        with ctx.pose({cup_joint: r.lift_limit_m}):
            lifted = ctx.part_world_position(cups[0])
        ctx.check(
            "collector cup lifts vertically for removal",
            rest is not None and lifted is not None and lifted[2] > rest[2] + 0.9 * r.lift_limit_m,
            details=f"rest={rest} lifted={lifted}",
        )
    if strainer_joint is not None and strainers:
        rest = ctx.part_world_position(strainers[0])
        with ctx.pose({strainer_joint: r.lift_limit_m}):
            lifted = ctx.part_world_position(strainers[0])
        ctx.check(
            "strainer lifts independently out of the cup",
            rest is not None and lifted is not None and lifted[2] > rest[2] + 0.9 * r.lift_limit_m,
            details=f"rest={rest} lifted={lifted}",
        )

    # ---- frame silhouette --------------------------------------------------
    ctx.check(
        "frame carries the beam clear above the cup on real columns",
        r.beam_bottom_z_m > r.stack_top_z_m + 0.010
        and r.post_len_m > 0.10
        and r.beam_front_y_m < r.cup_y_m
        and r.beam_back_y_m > r.cup_y_m
        and r.beam_hx_m > r.boss_r_m,
        details=(
            f"beam_bottom={r.beam_bottom_z_m:.4f} stack_top={r.stack_top_z_m:.4f} "
            f"post_len={r.post_len_m:.4f} beam_y=({r.beam_front_y_m:.4f},"
            f"{r.beam_back_y_m:.4f}) cup_y={r.cup_y_m:.4f}"
        ),
    )
    if exact and frames:
        box = ctx.part_world_aabb(frames[0])
        ctx.check(
            "press stands taller than it is wide and faces +X",
            box is not None and (box[1][2] - box[0][2]) > 0.9 * (box[1][0] - box[0][0]),
            details=f"frame_aabb={box}",
        )
    else:
        ctx.check(
            "press stands taller than it is wide and faces +X",
            r.beam_top_z_m > 0.9 * r.base_width_m,
            details=f"beam_top={r.beam_top_z_m:.4f} base_w={r.base_width_m:.4f}",
        )

    return ctx.report()


# --------------------------------------------------------------------------- #
# High-risk cross-slot corners
# --------------------------------------------------------------------------- #
TEMPLATE_CORNERS = (
    corner_case(
        "c_arch_clamped_rack_tall_pedestal",
        {
            "frame_style": "c_arch_throat",
            "mount_style": "bench_clamp_bracket",
            "actuator_style": "rack_pinion_crank",
            "catch_deck": "raised_pedestal_boss",
            "grip_style": "tee_bar_knobs",
            "base_support_count": 6,
            "base_width_m": 0.205,
            "base_depth_m": 0.210,
            "pedestal_h_m": 0.048,
            "column_depth_m": 0.064,
            "cup_rim_ratio": 0.86,
            "gear_module_mm": 1.6,
            "crank_reach_m": 0.132,
            "ram_travel_m": 0.046,
            "clamp_throat_h_m": 0.086,
        },
        reason=(
            "the narrowest base carrying the deepest rear column, the tallest pedestal "
            "and the widest gear head, with the longest crank and the widest tommy bar "
            "sweeping behind the beam and six ribs across the deepest clamp throat"
        ),
    ),
    corner_case(
        "twin_post_lever_shortest_stack",
        {
            "frame_style": "twin_post_column",
            "mount_style": "corner_foot_pads",
            "actuator_style": "lever_linkage",
            "catch_deck": "flat_drip_disc",
            "grip_style": "sleeve_and_ball",
            "base_support_count": 3,
            "base_width_m": 0.275,
            "base_depth_m": 0.145,
            "base_height_m": 0.034,
            "beam_height_m": 0.060,
            "cup_height_m": 0.108,
            "ram_reach_m": 0.245,
            "ram_travel_m": 0.026,
            "lever_reach_m": 0.300,
            "lever_drop_ratio": 0.62,
            "post_span_ratio": 0.78,
            "grip_len_m": 0.092,
            "knob_r_m": 0.0160,
        },
        reason=(
            "the shortest possible stack under the thickest beam, which is where the "
            "drive link has the least room to stay ahead of the beam face, combined "
            "with the longest and steepest lever on a tripod"
        ),
    ),
    corner_case(
        "c_arch_screw_widest_wheel",
        {
            "frame_style": "c_arch_throat",
            "mount_style": "corner_foot_pads",
            "actuator_style": "screw_handwheel",
            "catch_deck": "raised_pedestal_boss",
            "grip_style": "ball_knob",
            "base_support_count": 6,
            "handwheel_r_m": 0.094,
            "wheel_spoke_pairs": 4,
            "ram_travel_m": 0.046,
            "ram_reach_m": 0.320,
            "cup_height_m": 0.166,
            "press_head_ratio": 0.78,
            "column_depth_m": 0.034,
            "beam_height_m": 0.038,
        },
        reason=(
            "the tallest stack on the thinnest column and the thinnest beam, with the "
            "longest stroke pulling the screw furthest out of the widest handwheel hub"
        ),
    ),
    corner_case(
        "twin_post_clamp_rack_biggest_gear",
        {
            "frame_style": "twin_post_column",
            "mount_style": "bench_clamp_bracket",
            "actuator_style": "rack_pinion_crank",
            "catch_deck": "flat_drip_disc",
            "grip_style": "sleeve_and_ball",
            "base_support_count": 3,
            "gear_module_mm": 2.6,
            "ram_travel_m": 0.026,
            "beam_height_m": 0.038,
            "cup_rim_ratio": 0.58,
            "press_head_ratio": 0.55,
            "clamp_throat_h_m": 0.038,
            "clamp_screw_r_m": 0.0120,
            "base_width_m": 0.205,
        },
        reason=(
            "the coarsest gear in the thinnest beam over the smallest cup, with the "
            "fattest clamp screw in the shallowest throat and only three gussets"
        ),
    ),
)


__all__ = [
    "Config",
    "PALETTES",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_juicer_press_with_handle",
    "build_seeded_pictureX_0611_juicer_press_with_handle",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_juicer_press_with_handle_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
