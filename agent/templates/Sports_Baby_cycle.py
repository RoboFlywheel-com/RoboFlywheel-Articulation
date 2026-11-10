# SPDX-License-Identifier: Apache-2.0

"""Baby cycle (toddler balance / ride-on trike) modular template.

A toddler ride-on: a white tubular **frame** (root) carries a FIXED saddle, a
REVOLUTE **steering** assembly (handlebar + fork) about a raked head tube, and
2-4 CONTINUOUS-rolling wheels. Front wheel(s) are children of the steering part
(so they turn with the bars); rear wheel(s) are children of the frame.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Sports_Baby_cycle.md`` and the 9 5-star
``baby_cycle`` samples synced under ``data/records/`` (parent trike + 8 slot
forks). All sources share one helper skeleton (``_swept_tube`` / ``_cyl_between``
/ ``_spin_origin`` / wheel helper / fork / handlebar) and one articulation
topology: steering REVOLUTE (raked head-tube axis, +/-pi/4) + per-wheel
CONTINUOUS roll (local X axle, effort 2 / velocity 20) + saddle FIXED.

Pattern = ``mixed``: ``frame`` (root) with parallel children
``saddle`` / ``steering`` and a wheel multiplicity axis (front wheels parent =
steering, rear wheels parent = frame). Module axes:

  * ``frame_form`` (3): step_through_loop / crossbar_diamond / twin_beam_deck.
  * ``foot_interface`` (3): none_balance / front_pedals / footrest_pegs.
  * ``handlebar_form`` (3): swept_riser / t_bar_straight / ape_hanger_loop.
  * ``wheel_arrangement`` (N in [2,4]): n2 (1f1r inline) / n3 (1f2r trike) /
    n4 (2f2r quad). Encoded into the slot tuple as ``("wheel_arrangement",
    f"n{N}")``; front/rear split + track derive from N.

Compatibility gating (resolve_config, spec reject cases 2 / §9):
  * ``front_pedals`` needs a single front wheel (opposed cranks cannot share a
    transverse dual-front axle) -> with front_count==2, foot degrades to
    ``none_balance``. inline (n2) x front_pedals is also gated off (tippy per
    source map) -> degrades to ``none_balance``.

Captured-pin / seated overlaps are element-scoped ``allow_overlap`` at the
mounting interfaces (frame<->saddle, frame<->steering fork-in-head-tube,
steering<->front wheel, frame<->rear wheel, plus per-foot boss overlaps),
mirroring each source record's run_tests block.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

FrameForm = Literal["step_through_loop", "crossbar_diamond", "twin_beam_deck"]
FootInterface = Literal["none_balance", "front_pedals", "footrest_pegs"]
HandlebarForm = Literal["swept_riser", "t_bar_straight", "ape_hanger_loop"]
WheelArrangement = Literal["n2", "n3", "n4"]
PaletteStyle = Literal[
    "classic_white_blue",
    "candy_pink_cream",
    "mint_green_natural",
    "sunshine_yellow_red",
    "sky_blue_chrome",
    "charcoal_lime_sport",
]

FRAME_FORMS: tuple[FrameForm, ...] = (
    "step_through_loop",
    "crossbar_diamond",
    "twin_beam_deck",
)
FOOT_INTERFACES: tuple[FootInterface, ...] = (
    "none_balance",
    "front_pedals",
    "footrest_pegs",
)
HANDLEBAR_FORMS: tuple[HandlebarForm, ...] = (
    "swept_riser",
    "t_bar_straight",
    "ape_hanger_loop",
)
WHEEL_ARRANGEMENTS: tuple[WheelArrangement, ...] = ("n2", "n3", "n4")
# N sampling weights (spec §8: trike n3 most common, inline n2 next, quad n4 tail).
WHEEL_WEIGHTS = (0.30, 0.50, 0.20)  # aligned to (n2, n3, n4)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_white_blue",
    "candy_pink_cream",
    "mint_green_natural",
    "sunshine_yellow_red",
    "sky_blue_chrome",
    "charcoal_lime_sport",
)

# (front_count, rear_count) for each N arrangement.
_SPLIT: dict[WheelArrangement, tuple[int, int]] = {
    "n2": (1, 1),
    "n3": (1, 2),
    "n4": (2, 2),
}

# Palette word-list: frame / accent (saddle, bar, fork) / hub (wheel disc) /
# grip / marker / steel (pedal crank). Tire is always near-black.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_white_blue": {
        "frame": (0.95, 0.95, 0.96, 1.0),
        "accent": (0.16, 0.55, 0.80, 1.0),
        "hub": (0.13, 0.48, 0.74, 1.0),
        "grip": (0.20, 0.60, 0.84, 1.0),
        "marker": (0.10, 0.40, 0.66, 1.0),
        "steel": (0.72, 0.73, 0.74, 1.0),
        "tire": (0.10, 0.10, 0.11, 1.0),
    },
    "candy_pink_cream": {
        "frame": (0.97, 0.93, 0.90, 1.0),
        "accent": (0.92, 0.45, 0.62, 1.0),
        "hub": (0.84, 0.36, 0.55, 1.0),
        "grip": (0.95, 0.55, 0.70, 1.0),
        "marker": (0.74, 0.28, 0.46, 1.0),
        "steel": (0.80, 0.78, 0.76, 1.0),
        "tire": (0.11, 0.10, 0.10, 1.0),
    },
    "mint_green_natural": {
        "frame": (0.74, 0.88, 0.78, 1.0),
        "accent": (0.78, 0.62, 0.42, 1.0),
        "hub": (0.62, 0.48, 0.32, 1.0),
        "grip": (0.86, 0.72, 0.52, 1.0),
        "marker": (0.50, 0.38, 0.24, 1.0),
        "steel": (0.70, 0.72, 0.70, 1.0),
        "tire": (0.10, 0.11, 0.10, 1.0),
    },
    "sunshine_yellow_red": {
        "frame": (0.97, 0.82, 0.18, 1.0),
        "accent": (0.86, 0.20, 0.18, 1.0),
        "hub": (0.74, 0.14, 0.13, 1.0),
        "grip": (0.92, 0.30, 0.24, 1.0),
        "marker": (0.62, 0.10, 0.10, 1.0),
        "steel": (0.74, 0.73, 0.70, 1.0),
        "tire": (0.11, 0.10, 0.10, 1.0),
    },
    "sky_blue_chrome": {
        "frame": (0.55, 0.78, 0.92, 1.0),
        "accent": (0.80, 0.82, 0.85, 1.0),
        "hub": (0.66, 0.68, 0.72, 1.0),
        "grip": (0.72, 0.76, 0.82, 1.0),
        "marker": (0.40, 0.44, 0.50, 1.0),
        "steel": (0.82, 0.83, 0.85, 1.0),
        "tire": (0.10, 0.10, 0.11, 1.0),
    },
    "charcoal_lime_sport": {
        "frame": (0.20, 0.21, 0.23, 1.0),
        "accent": (0.62, 0.86, 0.16, 1.0),
        "hub": (0.50, 0.72, 0.12, 1.0),
        "grip": (0.70, 0.92, 0.24, 1.0),
        "marker": (0.40, 0.58, 0.10, 1.0),
        "steel": (0.58, 0.60, 0.62, 1.0),
        "tire": (0.09, 0.09, 0.10, 1.0),
    },
}

# ---- nominal dimensions (meters), from the 5-star sources ----
WHEEL_RADIUS = 0.060
TIRE_WIDTH = 0.034
HUB_RADIUS = 0.040
DISC_HALF = 0.013

# Front axle carries real trail: it sits well ahead of the raked head-tube axis
# so steering always sweeps the front contact line clearly sideways (the fork
# crown/blades are derived from this, so the front end stays connected).
FRONT_AXLE_Y0 = 0.255
REAR_AXLE_Y0 = -0.165

FRONT_HALF_TRACK0 = 0.095
REAR_HALF_TRACK0 = 0.115

# Steering head nominal (raked): axis tilts in the Y-Z plane.
HEAD_TOP0 = (0.0, 0.150, 0.205)
HEAD_BOT0 = (0.0, 0.188, 0.090)

# Pedal crank dims (S6).
CRANK_LENGTH = 0.045
CRANK_ARM_R = 0.005
PEDAL_R = 0.010
PEDAL_LEN = 0.032
CRANK_SIDE_X = 0.035

# Twin-beam rail half-spacing (S5).
RAIL_X = 0.048


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


@dataclass(frozen=True)
class BabyCycleConfig:
    frame_form: FrameForm | None = None
    foot_interface: FootInterface | None = None
    handlebar_form: HandlebarForm | None = None
    wheel_arrangement: WheelArrangement | None = None
    palette_style: PaletteStyle = "classic_white_blue"
    wheel_radius_scale: float = 1.0
    steer_rake_scale: float = 1.0
    frame_length_scale: float = 1.0
    front_half_track: float = FRONT_HALF_TRACK0
    rear_half_track: float = REAR_HALF_TRACK0
    name: str = "baby_cycle"


@dataclass(frozen=True)
class ResolvedBabyCycleConfig:
    frame_form: FrameForm
    foot_interface: FootInterface
    handlebar_form: HandlebarForm
    wheel_arrangement: WheelArrangement
    palette_style: PaletteStyle
    front_count: int
    rear_count: int
    # concrete geometry
    wheel_radius: float
    axle_z: float
    front_axle_y: float
    rear_axle_y: float
    front_half_track: float
    rear_half_track: float
    head_top: tuple[float, float, float]
    head_bot: tuple[float, float, float]
    steer_axis: tuple[float, float, float]
    name: str

    @property
    def wheel_count(self) -> int:
        return self.front_count + self.rear_count


def config_from_seed(seed: int) -> BabyCycleConfig:
    rng = random.Random(seed)
    return BabyCycleConfig(
        wheel_arrangement=rng.choices(WHEEL_ARRANGEMENTS, weights=WHEEL_WEIGHTS, k=1)[0],
        frame_form=rng.choice(FRAME_FORMS),
        foot_interface=rng.choice(FOOT_INTERFACES),
        handlebar_form=rng.choice(HANDLEBAR_FORMS),
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_radius_scale=round(rng.uniform(0.85, 1.15), 4),
        steer_rake_scale=round(rng.uniform(0.90, 1.10), 4),
        frame_length_scale=round(rng.uniform(0.92, 1.10), 4),
        front_half_track=round(rng.uniform(0.080, 0.110), 4),
        rear_half_track=round(rng.uniform(0.095, 0.130), 4),
        name=f"seeded_baby_cycle_{seed}",
    )


def resolve_config(config: BabyCycleConfig | None = None) -> ResolvedBabyCycleConfig:
    cfg = config or BabyCycleConfig()

    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    frame_form = _pick(cfg.frame_form, FRAME_FORMS)
    handlebar_form = _pick(cfg.handlebar_form, HANDLEBAR_FORMS)
    arrangement = _pick(cfg.wheel_arrangement, WHEEL_ARRANGEMENTS)
    front_count, rear_count = _SPLIT[arrangement]

    foot_interface = _pick(cfg.foot_interface, FOOT_INTERFACES)
    # Gate: opposed front cranks require exactly one front wheel; inline (n2)
    # is excluded from the pedal combo per source map (tippy).
    if foot_interface == "front_pedals" and (front_count != 1 or arrangement == "n2"):
        foot_interface = "none_balance"

    # --- continuous scales ---
    radius_scale = _clamp(cfg.wheel_radius_scale, 0.85, 1.15)
    rake_scale = _clamp(cfg.steer_rake_scale, 0.90, 1.10)
    length_scale = _clamp(cfg.frame_length_scale, 0.92, 1.10)

    wheel_radius = WHEEL_RADIUS * radius_scale
    axle_z = wheel_radius  # wheel bottom rests on z=0

    front_axle_y = FRONT_AXLE_Y0 * length_scale
    rear_axle_y = REAR_AXLE_Y0 * length_scale

    # Rake: tilt the head tube by scaling the bottom-vs-top Y separation about
    # the top node, keeping HEAD_TOP fixed.
    head_top = HEAD_TOP0
    bot_dy = (HEAD_BOT0[1] - HEAD_TOP0[1]) * rake_scale
    head_bot = (HEAD_BOT0[0], HEAD_TOP0[1] + bot_dy, HEAD_BOT0[2])
    _dy = head_top[1] - head_bot[1]
    _dz = head_top[2] - head_bot[2]
    _dn = math.hypot(_dy, _dz)
    steer_axis = (0.0, _dy / _dn, _dz / _dn)

    # --- track clearance inequalities ---
    front_half_track = _clamp(cfg.front_half_track, 0.080, 0.110)
    rear_half_track = _clamp(cfg.rear_half_track, 0.095, 0.130)
    # Dual wheels must not let their hubs/tires interpenetrate: half-track must
    # exceed half the tire width plus a gap.
    min_half = TIRE_WIDTH / 2.0 + 0.012
    if front_count == 2:
        front_half_track = max(front_half_track, min_half)
    if rear_count == 2:
        rear_half_track = max(rear_half_track, min_half)

    return ResolvedBabyCycleConfig(
        frame_form=frame_form,
        foot_interface=foot_interface,
        handlebar_form=handlebar_form,
        wheel_arrangement=arrangement,
        palette_style=palette_style,
        front_count=front_count,
        rear_count=rear_count,
        wheel_radius=wheel_radius,
        axle_z=axle_z,
        front_axle_y=front_axle_y,
        rear_axle_y=rear_axle_y,
        front_half_track=front_half_track,
        rear_half_track=rear_half_track,
        head_top=head_top,
        head_bot=head_bot,
        steer_axis=steer_axis,
        name=cfg.name or "baby_cycle",
    )


def with_overrides(config: BabyCycleConfig, **kwargs: object) -> BabyCycleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: BabyCycleConfig | ResolvedBabyCycleConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedBabyCycleConfig) else resolve_config(config)
    return (
        ("frame_form", r.frame_form),
        ("foot_interface", r.foot_interface),
        ("handlebar_form", r.handlebar_form),
        ("wheel_arrangement", f"n{r.wheel_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (shared across all sources).
# ---------------------------------------------------------------------------
def _spin_origin() -> Origin:
    return Origin(rpy=(0.0, math.pi / 2.0, 0.0))


def _swept_tube(points, radius: float, offset=(0.0, 0.0, 0.0)) -> cq.Workplane:
    ox, oy, oz = offset
    pts = [(p[0] - ox, p[1] - oy, p[2] - oz) for p in points]
    path = cq.Workplane("XY").spline([cq.Vector(*p) for p in pts])
    start = pts[0]
    nxt = pts[1]
    tangent = cq.Vector(nxt[0] - start[0], nxt[1] - start[1], nxt[2] - start[2]).normalized()
    profile = cq.Workplane(
        cq.Plane(origin=start, normal=(tangent.x, tangent.y, tangent.z))
    ).circle(radius)
    return profile.sweep(path, transition="round")


def _cyl_between(a, b, radius, offset=(0.0, 0.0, 0.0)) -> cq.Workplane:
    ox, oy, oz = offset
    ax, ay, az = a[0] - ox, a[1] - oy, a[2] - oz
    bx, by, bz = b[0] - ox, b[1] - oy, b[2] - oz
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    cyl = cq.Workplane("XY").circle(radius).extrude(length)
    elev = math.degrees(math.asin(max(-1.0, min(1.0, dz / length))))
    azim = math.degrees(math.atan2(dy, dx))
    cyl = cyl.rotate((0, 0, 0), (0, 1, 0), 90.0 - elev)
    cyl = cyl.rotate((0, 0, 0), (0, 0, 1), azim)
    return cyl.translate((ax, ay, az))


# ---------------------------------------------------------------------------
# Frame meshes (Slot B). Each returns (mesh-or-list-of-(mesh,name), saddle_xyz).
# ---------------------------------------------------------------------------
def _frame_step_through(r: ResolvedBabyCycleConfig, assets):
    """Low single-tube step-through loop (S1 parent)."""
    az = r.axle_z
    ry = r.rear_axle_y
    backbone = _swept_tube(
        [
            (0.0, 0.165, 0.150),
            (0.0, 0.140, 0.120),
            (0.0, 0.070, 0.100),
            (0.0, -0.020, 0.092),
            (0.0, -0.110, 0.090),
            (0.0, ry, 0.083),
        ],
        radius=0.018,
    )
    frame = backbone.add(_cyl_between(r.head_bot, r.head_top, 0.022))
    frame = _add_rear_structure(frame, r)
    # Saddle seats behind the head on the backbone (tube top ~0.110-0.112). A
    # single centerline rear wheel reaches forward, so move the saddle ahead of
    # it (still y<0) in that case; a dual rear axle leaves the centerline clear.
    # The backbone tapers from ~0.110 (top) up front to ~0.108 at y=-0.085, so
    # seat the saddle base on the tube top at whichever y it lands.
    if r.rear_count == 1:
        saddle_y, saddle_z = -0.020, 0.109
    else:
        saddle_y, saddle_z = -0.085, 0.107
    return [(mesh_from_cadquery(frame, "frame_tube", assets=assets), "frame_tube")], (
        0.0,
        saddle_y,
        saddle_z,
    )


def _frame_crossbar(r: ResolvedBabyCycleConfig, assets):
    """Closed diamond side profile (S4)."""
    az = r.axle_z
    tt_front = (0.0, 0.153, 0.196)
    dt_top = (0.0, 0.186, 0.094)
    bb = (0.0, 0.010, 0.072)
    sc = (0.0, -0.110, 0.188)
    seat_post_top = (0.0, -0.112, 0.222)

    head = _cyl_between(r.head_bot, r.head_top, 0.022)
    frame = (
        head.add(_cyl_between(tt_front, sc, 0.016))
        .add(_cyl_between(dt_top, bb, 0.016))
        .add(_cyl_between(bb, sc, 0.015))
        .add(_cyl_between(sc, seat_post_top, 0.013))
    )
    # Chain + seat stays handled by rear structure helper; bottom bracket / seat
    # cluster anchors for stays:
    frame = _add_rear_structure(frame, r, lower_anchor=bb, upper_anchor=sc)
    return [(mesh_from_cadquery(frame, "frame_tube", assets=assets), "frame_tube")], seat_post_top


def _frame_twin_beam(r: ResolvedBabyCycleConfig, assets):
    """Two mirrored parallel side rails + flat deck (S5)."""
    az = r.axle_z
    ry = r.rear_axle_y

    def rail_path(sign: int):
        sx = sign * RAIL_X
        return [
            (0.0, 0.182, 0.095),
            (sign * 0.026, 0.155, 0.108),
            (sx, 0.120, 0.112),
            (sx, 0.050, 0.096),
            (sx, -0.040, 0.090),
            (sx, -0.120, 0.086),
            (sx, ry, 0.083),
        ]

    visuals: list[tuple[object, str]] = []
    for i, sign in enumerate((1, -1)):
        rail = _swept_tube(rail_path(sign), radius=0.014)
        visuals.append((mesh_from_cadquery(rail, f"rail_{i}", assets=assets), f"rail_{i}"))

    # Structural members (head tube, cross-braces, rear axle structure).
    s = _cyl_between(r.head_bot, r.head_top, 0.022)
    s = s.add(_cyl_between((-RAIL_X, 0.120, 0.112), (RAIL_X, 0.120, 0.112), 0.010))
    s = s.add(_cyl_between((-RAIL_X, -0.040, 0.090), (RAIL_X, -0.040, 0.090), 0.009))
    s = s.add(_cyl_between((-RAIL_X, -0.120, 0.086), (RAIL_X, -0.120, 0.086), 0.009))
    s = _add_rear_structure(
        s, r, rail_anchor_x=RAIL_X, lower_anchor=None, upper_anchor=None
    )
    visuals.append((mesh_from_cadquery(s, "frame_structure", assets=assets), "frame_structure"))

    # Flat deck plate on top of the rails.
    deck_width = 2.0 * RAIL_X + 0.004
    plate = (
        cq.Workplane("XY")
        .rect(deck_width, 0.130)
        .extrude(0.007)
        .translate((0.0, -0.058, 0.098))
    )
    visuals.append((mesh_from_cadquery(plate, "deck_plate", assets=assets), "deck_plate"))
    # Saddle base seated flush on the deck plate top (z=0.098+0.007=0.105). A
    # single centerline rear wheel reaches forward onto the deck, so slide the
    # saddle ahead of it (still y<0); dual rear wheels leave the centerline open.
    saddle_y = -0.030 if r.rear_count == 1 else -0.065
    return visuals, (0.0, saddle_y, 0.104)


def _add_rear_structure(
    frame: cq.Workplane,
    r: ResolvedBabyCycleConfig,
    *,
    lower_anchor=None,
    upper_anchor=None,
    rail_anchor_x: float | None = None,
):
    """Add the rear axle bridge + stays, derived from rear_count.

    rear_count == 2: transverse axle bridge spanning +/-rear_half_track + stays.
    rear_count == 1: short centerline dropout stub + converging stays.
    """
    az = r.axle_z
    ry = r.rear_axle_y
    ht = r.rear_half_track
    backbone_end = (0.0, ry, 0.083)

    if r.rear_count == 2:
        frame = frame.add(
            _cyl_between((-ht, ry, az), (ht, ry, az), 0.012)
        )
        for sx in (-ht, ht):
            if rail_anchor_x is not None:
                src = (math.copysign(rail_anchor_x, sx), ry, 0.083)
            elif lower_anchor is not None:
                src = lower_anchor
            else:
                src = backbone_end
            frame = frame.add(_cyl_between(src, (sx, ry, az), 0.011))
            if upper_anchor is not None:
                frame = frame.add(_cyl_between(upper_anchor, (sx, ry, az), 0.010))
    else:
        # centerline rear wheel: converging stays + short cross-stub.
        if lower_anchor is not None:
            conv_src = lower_anchor
        elif rail_anchor_x is not None:
            conv_src = None
        else:
            conv_src = (0.0, -0.110, 0.090)
        if rail_anchor_x is not None:
            for sign in (1, -1):
                frame = frame.add(
                    _cyl_between(
                        (sign * rail_anchor_x, -0.120, 0.086), (sign * 0.026, ry, az), 0.011
                    )
                )
        else:
            for sx in (-0.024, 0.024):
                frame = frame.add(_cyl_between(conv_src, (sx, ry, az), 0.011))
        frame = frame.add(_cyl_between((-0.032, ry, az), (0.032, ry, az), 0.008))
        if upper_anchor is not None:
            for sx in (-0.024, 0.024):
                frame = frame.add(_cyl_between(upper_anchor, (sx, ry, az), 0.010))
    return frame


_FRAME_BUILDERS = {
    "step_through_loop": _frame_step_through,
    "crossbar_diamond": _frame_crossbar,
    "twin_beam_deck": _frame_twin_beam,
}


# ---------------------------------------------------------------------------
# Fork + handlebar meshes (Slot D + front split). Authored in world coords,
# shifted into the steering local frame by `offset` (= HEAD_BOT).
# ---------------------------------------------------------------------------
def _fork_mesh(r: ResolvedBabyCycleConfig, offset, assets):
    hb = r.head_bot
    az = r.axle_z
    fy = r.front_axle_y
    stem = _cyl_between(
        (0.0, 0.150, 0.252),
        (hb[0], hb[1] + 0.018, hb[2] - 0.010),
        0.014,
        offset=offset,
    )
    fork = stem
    crown = (0.0, fy - 0.040, az + 0.085)
    fork = fork.add(
        _cyl_between((hb[0], hb[1] + 0.018, hb[2] - 0.010), crown, 0.012, offset=offset)
    )
    if r.front_count == 2:
        ht = r.front_half_track
        for sx in (-ht, ht):
            fork = fork.add(_cyl_between(crown, (sx, fy, az), 0.010, offset=offset))
        fork = fork.add(
            _cyl_between((-ht - 0.012, fy, az), (ht + 0.012, fy, az), 0.008, offset=offset)
        )
    else:
        for sx in (-0.020, 0.020):
            fork = fork.add(_cyl_between(crown, (sx, fy, az), 0.010, offset=offset))
        fork = fork.add(
            _cyl_between((-0.030, fy, az), (0.030, fy, az), 0.008, offset=offset)
        )
    return mesh_from_cadquery(fork, "fork", assets=assets)


def _handlebar_swept(offset, assets):
    bar = _swept_tube(
        [
            (-0.135, 0.150, 0.235),
            (-0.080, 0.140, 0.250),
            (-0.030, 0.150, 0.256),
            (0.030, 0.150, 0.256),
            (0.080, 0.140, 0.250),
            (0.135, 0.150, 0.235),
        ],
        radius=0.013,
        offset=offset,
    )
    return mesh_from_cadquery(bar, "handlebar_bar", assets=assets)


def _handlebar_tbar(offset, assets):
    bar = _cyl_between((-0.135, 0.150, 0.252), (0.135, 0.150, 0.252), radius=0.012, offset=offset)
    clamp = _cyl_between((0.0, 0.150, 0.242), (0.0, 0.150, 0.262), radius=0.016, offset=offset)
    return mesh_from_cadquery(bar.add(clamp), "tbar_crossbar", assets=assets)


def _handlebar_apehanger(offset, assets):
    bar = _swept_tube(
        [
            (-0.042, 0.082, 0.400),
            (-0.085, 0.100, 0.410),
            (-0.108, 0.128, 0.395),
            (-0.080, 0.145, 0.340),
            (-0.040, 0.150, 0.285),
            (0.000, 0.150, 0.258),
            (0.040, 0.150, 0.285),
            (0.080, 0.145, 0.340),
            (0.108, 0.128, 0.395),
            (0.085, 0.100, 0.410),
            (0.042, 0.082, 0.400),
        ],
        radius=0.011,
        offset=offset,
    )
    return mesh_from_cadquery(bar, "handlebar_bar", assets=assets)


def _build_steering(model, r: ResolvedBabyCycleConfig, mats, assets):
    steer = model.part("steering")
    hb = r.head_bot
    steer.visual(_fork_mesh(r, hb, assets), material=mats["accent"], name="fork", material_class_id=("metal.chrome_polished" if r.palette_style == "sky_blue_chrome" else "metal.paint_coated"))

    if r.handlebar_form == "t_bar_straight":
        steer.visual(_handlebar_tbar(hb, assets), material=mats["accent"], name="tbar_crossbar", material_class_id=("metal.chrome_polished" if r.palette_style == "sky_blue_chrome" else "metal.paint_coated"))
        grip_angle = math.radians(12)
        grip_len = 0.050
        for i, sx in enumerate((-1, 1)):
            cx = sx * (0.135 + grip_len / 2.0 * math.cos(grip_angle))
            cy = 0.150 - grip_len / 2.0 * math.sin(grip_angle)
            steer.visual(
                Cylinder(radius=0.018, length=grip_len),
                origin=Origin(
                    xyz=(cx, cy - hb[1], 0.252 - hb[2]),
                    rpy=(0.0, math.pi / 2.0, -sx * grip_angle),
                ),
                material=mats["grip"],
                name=f"grip_{i}", material_class_id="rubber.smooth_plain",
            )
    elif r.handlebar_form == "ape_hanger_loop":
        steer.visual(
            _handlebar_apehanger(hb, assets), material=mats["accent"], name="handlebar_bar", material_class_id=("metal.chrome_polished" if r.palette_style == "sky_blue_chrome" else "metal.paint_coated")
        )
        for i, sx in enumerate((-0.042, 0.042)):
            steer.visual(
                Cylinder(radius=0.016, length=0.045),
                origin=Origin(
                    xyz=(sx, 0.082 - hb[1], 0.400 - hb[2]), rpy=(0.0, math.pi / 2.0, 0.0)
                ),
                material=mats["grip"],
                name=f"grip_{i}", material_class_id="rubber.smooth_plain",
            )
    else:  # swept_riser
        steer.visual(
            _handlebar_swept(hb, assets), material=mats["accent"], name="handlebar_bar", material_class_id=("metal.chrome_polished" if r.palette_style == "sky_blue_chrome" else "metal.paint_coated")
        )
        for i, sx in enumerate((-0.118, 0.118)):
            steer.visual(
                Cylinder(radius=0.018, length=0.050),
                origin=Origin(
                    xyz=(sx, 0.150 - hb[1], 0.236 - hb[2]), rpy=(0.0, math.pi / 2.0, 0.0)
                ),
                material=mats["grip"],
                name=f"grip_{i}", material_class_id="rubber.smooth_plain",
            )

    steer.inertial = Inertial.from_geometry(
        Box((0.27, 0.12, 0.22)),
        mass=0.45,
        origin=Origin(xyz=(0.0, 0.16 - hb[1], 0.16 - hb[2])),
    )
    model.articulation(
        "steering",
        ArticulationType.REVOLUTE,
        parent=model.get_part("frame"),
        child=steer,
        origin=Origin(xyz=hb),
        axis=r.steer_axis,
        motion_limits=MotionLimits(
            effort=4.0, velocity=4.0, lower=-math.pi / 4.0, upper=math.pi / 4.0
        ),
    )
    return steer


# ---------------------------------------------------------------------------
# Saddle + wheels.
# ---------------------------------------------------------------------------
def _saddle_mesh(assets):
    # Compact saddle pad: kept short in Y so it clears a single, forward-reaching
    # centerline rear wheel while still seating behind the head tube (y<0).
    pad = (
        cq.Workplane("XY")
        .ellipse(0.050, 0.058)
        .workplane(offset=0.026)
        .ellipse(0.058, 0.066)
        .loft(ruled=False)
    )
    pad = pad.edges(">Z").fillet(0.016)
    return mesh_from_cadquery(pad, "saddle_pad", assets=assets)


def _build_wheel_visuals(name: str, r: ResolvedBabyCycleConfig, assets):
    wr = r.wheel_radius
    so = _spin_origin()
    tire = cq.Workplane("XY").circle(wr).circle(HUB_RADIUS - 0.002).extrude(TIRE_WIDTH)
    tire = tire.translate((0.0, 0.0, -TIRE_WIDTH / 2.0))
    disc = cq.Workplane("XY").circle(HUB_RADIUS).extrude(DISC_HALF)
    disc = disc.translate((0.0, 0.0, TIRE_WIDTH / 2.0 - DISC_HALF))
    disc = disc.union(
        cq.Workplane("XY").circle(HUB_RADIUS).extrude(DISC_HALF).translate(
            (0.0, 0.0, -TIRE_WIDTH / 2.0)
        )
    )
    disc = disc.union(
        cq.Workplane("XY").circle(0.012).extrude(TIRE_WIDTH).translate(
            (0.0, 0.0, -TIRE_WIDTH / 2.0)
        )
    )
    return (
        mesh_from_cadquery(tire, f"{name}_tire", assets=assets),
        mesh_from_cadquery(disc, f"{name}_disc", assets=assets),
        so,
    )


def _crank_pedal_pair(side_x: float, angle_rad: float, arm_name: str, pedal_name: str, assets):
    sign = 1.0 if side_x > 0 else -1.0
    hub_face_x = TIRE_WIDTH / 2.0 - 0.002
    boss_r = 0.008
    ey = CRANK_LENGTH * math.sin(angle_rad)
    ez = -CRANK_LENGTH * math.cos(angle_rad)
    boss = _cyl_between((sign * hub_face_x, 0.0, 0.0), (side_x, 0.0, 0.0), boss_r)
    arm = _cyl_between((side_x, 0.0, 0.0), (side_x, ey, ez), CRANK_ARM_R)
    arm = boss.add(arm)
    arm_mesh = mesh_from_cadquery(arm, arm_name, assets=assets)
    pedal = (
        cq.Workplane("XY").circle(PEDAL_R).extrude(PEDAL_LEN).translate((0.0, 0.0, -PEDAL_LEN / 2.0))
    )
    pedal = pedal.rotate((0, 0, 0), (0, 1, 0), 90.0).translate((side_x, ey, ez))
    pedal_mesh = mesh_from_cadquery(pedal, pedal_name, assets=assets)
    return arm_mesh, pedal_mesh


def _footrest_peg_geometry():
    boss_r, boss_len = 0.014, 0.010
    peg_r, peg_len = 0.008, 0.050
    boss = cq.Workplane("XY").circle(boss_r).extrude(boss_len)
    peg = cq.Workplane("XY").workplane(offset=boss_len).circle(peg_r).extrude(peg_len)
    return boss.union(peg)


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_baby_cycle(
    config: BabyCycleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"baby_cycle_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # ---- frame (root, Slot B) ----
    frame = model.part("frame")
    frame_visuals, saddle_xyz = _FRAME_BUILDERS[r.frame_form](r, assets)
    for mesh, name in frame_visuals:
        frame.visual(mesh, material=mats["frame"], name=name, material_class_id="metal.paint_coated")
    frame.inertial = Inertial.from_geometry(
        Box((0.26, 0.46, 0.18)), mass=1.4, origin=Origin(xyz=(0.0, 0.02, 0.10))
    )

    # ---- footrest pegs (Slot C, frame visuals, fixed) ----
    if r.foot_interface == "footrest_pegs":
        for i in range(2):
            side = 1 if i == 0 else -1
            rot_y = math.pi / 2.0 if side > 0 else -math.pi / 2.0
            frame.visual(
                mesh_from_cadquery(_footrest_peg_geometry(), f"footrest_{i}", assets=assets),
                origin=Origin(xyz=(side * 0.012, 0.0, 0.080), rpy=(0.0, rot_y, 0.0)),
                material=mats["frame"],
                name=f"footrest_{i}", material_class_id="metal.paint_coated",
            )

    # ---- saddle (FIXED to frame deck) ----
    saddle = model.part("saddle")
    saddle.visual(_saddle_mesh(assets), material=mats["accent"], name="saddle_pad", material_class_id="plastic.opaque_glossy_molded")
    saddle.inertial = Inertial.from_geometry(
        Box((0.12, 0.17, 0.06)), mass=0.15, origin=Origin(xyz=(0.0, 0.0, 0.013))
    )
    model.articulation(
        "frame_to_saddle",
        ArticulationType.FIXED,
        parent=frame,
        child=saddle,
        origin=Origin(xyz=saddle_xyz),
    )

    # ---- steering (REVOLUTE about raked head tube; owns fork + bar + grips) ----
    steer = _build_steering(model, r, mats, assets)

    # ---- wheels: front (child of steering) + rear (child of frame) ----
    hb = r.head_bot
    az = r.axle_z
    layout: list[tuple[float, float, bool]] = []  # (x_off, y_axle, is_front)
    if r.front_count == 2:
        ht = r.front_half_track
        layout.append((-ht, r.front_axle_y, True))
        layout.append((ht, r.front_axle_y, True))
    else:
        layout.append((0.0, r.front_axle_y, True))
    if r.rear_count == 2:
        ht = r.rear_half_track
        layout.append((-ht, r.rear_axle_y, False))
        layout.append((ht, r.rear_axle_y, False))
    else:
        layout.append((0.0, r.rear_axle_y, False))

    front_wheel_part = None
    for i, (x_off, y_axle, is_front) in enumerate(layout):
        wname = f"wheel_{i}"
        tire_mesh, disc_mesh, so = _build_wheel_visuals(wname, r, assets)
        wpart = model.part(wname)
        wpart.visual(tire_mesh, origin=so, material=mats["tire"], name=f"{wname}_tire", material_class_id="rubber.smooth_plain")
        wpart.visual(disc_mesh, origin=so, material=mats["hub"], name=f"{wname}_disc", material_class_id="plastic.opaque_glossy_molded")
        wpart.visual(
            Cylinder(radius=0.004, length=TIRE_WIDTH * 0.9),
            origin=Origin(xyz=(0.0, HUB_RADIUS - 0.006, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["marker"],
            name=f"{wname}_marker", material_class_id="plastic.opaque_glossy_molded",
        )
        wpart.inertial = Inertial.from_geometry(
            Cylinder(radius=r.wheel_radius, length=TIRE_WIDTH), mass=0.12, origin=so
        )
        if is_front:
            jorigin = Origin(xyz=(x_off, y_axle - hb[1], az - hb[2]))
            parent_part = steer
            if front_wheel_part is None:
                front_wheel_part = wpart
        else:
            jorigin = Origin(xyz=(x_off, y_axle, az))
            parent_part = frame
        model.articulation(
            f"{wname}_roll",
            ArticulationType.CONTINUOUS,
            parent=parent_part,
            child=wpart,
            origin=jorigin,
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=20.0),
        )

    # ---- front pedals (Slot C, visuals on front wheel, roll with it) ----
    if r.foot_interface == "front_pedals" and front_wheel_part is not None:
        for i in range(2):
            side_x = -CRANK_SIDE_X + i * 2 * CRANK_SIDE_X
            angle = i * math.pi
            arm_mesh, pedal_mesh = _crank_pedal_pair(
                side_x, angle, f"crank_{i}", f"pedal_{i}", assets
            )
            front_wheel_part.visual(arm_mesh, material=mats["steel"], name=f"crank_{i}", material_class_id="metal.steel_bare")
            front_wheel_part.visual(pedal_mesh, material=mats["accent"], name=f"pedal_{i}", material_class_id="plastic.opaque_glossy_molded")

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_baby_cycle(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_baby_cycle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_baby_cycle_tests(
    object_model: ArticulatedObject,
    config: BabyCycleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frame = object_model.get_part("frame")
    saddle = object_model.get_part("saddle")
    steer = object_model.get_part("steering")

    n = r.wheel_count
    wheels = [object_model.get_part(f"wheel_{i}") for i in range(n)]
    front_wheels = wheels[: r.front_count]
    rear_wheels = wheels[r.front_count :]

    # ---- Captured / seated overlaps (element-scoped via part pairs). ----
    ctx.allow_overlap(frame, saddle, reason="Padded saddle seated onto the frame deck.")
    ctx.allow_overlap(frame, steer, reason="Fork steerer passes down into the head tube.")
    for w in front_wheels:
        ctx.allow_overlap(frame, w, reason="Front fork/tire share the wheel cutout.")
        ctx.allow_overlap(steer, w, reason="Fork blades straddle the front tire/axle.")
    for w in rear_wheels:
        ctx.allow_overlap(frame, w, reason="Rear axle bridge captured in the wheel hub bore.")

    # ---- Saddle present, behind head, above deck, FIXED ----
    saddle_pos = ctx.part_world_position(saddle)
    ctx.check(
        "saddle sits behind the head and above the deck",
        saddle_pos is not None and saddle_pos[1] < 0.0 and saddle_pos[2] > 0.08,
        details=f"saddle_pos={saddle_pos}",
    )
    ctx.expect_contact(saddle, frame, name="saddle mounted on frame")
    saddle_joint = object_model.get_articulation("frame_to_saddle")
    ctx.check(
        "saddle joint is FIXED",
        saddle_joint is not None and saddle_joint.articulation_type == ArticulationType.FIXED,
        details=f"saddle_joint={None if saddle_joint is None else saddle_joint.articulation_type}",
    )

    # ---- Steering is REVOLUTE about the raked axis, reaches grip height ----
    steering = object_model.get_articulation("steering")
    ctx.check(
        "steering is REVOLUTE",
        steering is not None and steering.articulation_type == ArticulationType.REVOLUTE,
        details=f"steering={None if steering is None else steering.articulation_type}",
    )
    steer_aabb = ctx.part_world_aabb(steer)
    ctx.check(
        "handlebar reaches grip height",
        steer_aabb is not None and steer_aabb[1][2] > 0.22,
        details=f"steer_aabb={steer_aabb}",
    )
    ctx.expect_contact(steer, frame, name="fork/steering mounted to frame head tube")

    # ---- All wheels rest on the ground (z ~ 0) ----
    for i, w in enumerate(wheels):
        ab = ctx.part_world_aabb(w)
        ctx.check(
            f"wheel_{i} rests on ground",
            ab is not None and ab[0][2] < 0.006,
            details=f"wheel_{i}_min_z={None if ab is None else ab[0][2]}",
        )

    # ---- Wheel count matches arrangement; front centered when single ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        f"wheel count == {n}",
        all(f"wheel_{i}" in part_names for i in range(n)) and f"wheel_{n}" not in part_names,
        details=f"wheels={sorted(p for p in part_names if p.startswith('wheel_'))}",
    )
    if r.front_count == 1:
        fp = ctx.part_world_position(front_wheels[0])
        ctx.check(
            "single front wheel is centered up front",
            fp is not None and abs(fp[0]) < 0.012 and fp[1] > 0.10,
            details=f"front_pos={fp}",
        )
    else:
        fpa = ctx.part_world_position(front_wheels[0])
        fpb = ctx.part_world_position(front_wheels[1])
        ctx.check(
            "two front wheels symmetric across centerline",
            fpa is not None and fpb is not None
            and abs(fpa[0] + fpb[0]) < 0.006 and abs(fpa[0] - fpb[0]) > 0.12,
            details=f"f0={fpa}, f1={fpb}",
        )
    if r.rear_count == 2:
        rpa = ctx.part_world_position(rear_wheels[0])
        rpb = ctx.part_world_position(rear_wheels[1])
        ctx.check(
            "two rear wheels symmetric across centerline",
            rpa is not None and rpb is not None
            and abs(rpa[0] + rpb[0]) < 0.006 and abs(rpa[0] - rpb[0]) > 0.14,
            details=f"r0={rpa}, r1={rpb}",
        )

    # ---- Steering swings the front assembly sideways ----
    # Steering rotates the whole front assembly about the raked head-tube
    # (king-pin) axis, which lies on the centerline (x=0). The faithful probe
    # is the front-axle centerline = the midpoint of the front wheel(s); a
    # single off-axis wheel of a dual-wheel rig sweeps an asymmetric arc about
    # that shared axis, so probing one corner is the wrong rigid-body reference.
    def _front_center_x() -> float:
        xs = [ctx.part_world_position(w)[0] for w in front_wheels]
        return sum(xs) / len(xs)

    front_x0 = _front_center_x()
    with ctx.pose({steering: math.pi / 4.0}):
        front_x_left = _front_center_x()
    with ctx.pose({steering: -math.pi / 4.0}):
        front_x_right = _front_center_x()
    ctx.check(
        "steering swings the front wheel sideways",
        abs(front_x_left - front_x0) > 0.012 and abs(front_x_right - front_x0) > 0.012
        and (front_x_left - front_x0) * (front_x_right - front_x0) < 0,
        details=f"x0={front_x0}, left={front_x_left}, right={front_x_right}",
    )

    # ---- Each wheel rolls about its axle: the off-center marker moves ----
    for i, w in enumerate(wheels):
        roll = object_model.get_articulation(f"wheel_{i}_roll")
        m0 = ctx.part_element_world_aabb(w, elem=f"wheel_{i}_marker")
        with ctx.pose({roll: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(w, elem=f"wheel_{i}_marker")
        c0 = None if m0 is None else (0.5 * (m0[0][1] + m0[1][1]), 0.5 * (m0[0][2] + m0[1][2]))
        c1 = None if m1 is None else (0.5 * (m1[0][1] + m1[1][1]), 0.5 * (m1[0][2] + m1[1][2]))
        moved = (
            c0 is not None and c1 is not None
            and (abs(c0[0] - c1[0]) > 0.01 or abs(c0[1] - c1[1]) > 0.01)
        )
        ctx.check(
            f"wheel_{i} marker moves when the wheel rolls",
            moved,
            details=f"marker_center rest={c0}, quarter_turn={c1}",
        )

    # ---- Foot interface gating respected ----
    if r.foot_interface == "front_pedals":
        ctx.check(
            "front_pedals only with a single front wheel",
            r.front_count == 1,
            details=f"front_count={r.front_count}",
        )
        ctx.check(
            "pedal cranks present on front wheel",
            f"crank_0" in {v.name for v in front_wheels[0].visuals},
            details=str([v.name for v in front_wheels[0].visuals]),
        )
    elif r.foot_interface == "footrest_pegs":
        ctx.check(
            "footrest pegs present on frame",
            {"footrest_0", "footrest_1"}.issubset({v.name for v in frame.visuals}),
            details=str([v.name for v in frame.visuals]),
        )

    # ---- slot_choices recorded with N encoded ----
    ctx.check(
        "slot_choices recorded with wheel arrangement encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "BabyCycleConfig",
    "ResolvedBabyCycleConfig",
    "build_baby_cycle",
    "build_seeded_baby_cycle",
    "config_from_seed",
    "resolve_config",
    "run_baby_cycle_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
