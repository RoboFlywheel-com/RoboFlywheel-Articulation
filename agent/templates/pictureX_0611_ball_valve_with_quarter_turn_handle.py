# SPDX-License-Identifier: Apache-2.0

"""pictureX/0611/ball_valve_with_quarter_turn_handle — modular template.

Identity: a quarter-turn ball valve. Two parts (`valve_body` grounded,
`valve_rotor`) joined by a single REVOLUTE `body_to_rotor` (axis +z, [0, pi/2]).
Geometry is CadQuery boolean solids (the ported ball is a bored sphere, never a
box/cylinder downgrade — AUTHORING Rule 3), adapted from the 15 5-star sources
listed in specs_modular_v1/pictureX_0611_ball_valve_with_quarter_turn_handle.md.

Slots (flat enum-driven modular build; `__modular__` reports the per-slot picks):
  A body_form     : inline_2way / lport_3way / tport_3way / angle_body   (ball bore)
  B connection_ends: threaded / flanged / compression / hose_barb / solder
  C handle        : straight_lever / tee_bar / oval_loop / lockable_lever
  D stem_mount    : integral_gland / iso5211_pad / extended_stem  (sets gland_top_z)
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
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BodyForm = Literal["inline_2way", "lport_3way", "tport_3way", "angle_body"]
ConnectionEnds = Literal["threaded", "flanged", "compression", "hose_barb", "solder"]
Handle = Literal["straight_lever", "tee_bar", "oval_loop", "lockable_lever"]
StemMount = Literal["integral_gland", "iso5211_pad", "extended_stem"]
PaletteStyle = Literal[
    "stainless_blue", "brass_red", "pvc_yellow", "castiron_black", "stainless_red"
]

BODY_FORMS: tuple[BodyForm, ...] = ("inline_2way", "lport_3way", "tport_3way", "angle_body")
CONNECTION_ENDS: tuple[ConnectionEnds, ...] = (
    "threaded", "flanged", "compression", "hose_barb", "solder",
)
HANDLES: tuple[Handle, ...] = ("straight_lever", "tee_bar", "oval_loop", "lockable_lever")
STEM_MOUNTS: tuple[StemMount, ...] = ("integral_gland", "iso5211_pad", "extended_stem")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "stainless_blue", "brass_red", "pvc_yellow", "castiron_black", "stainless_red",
)
FLANGE_BOLT_COUNTS: tuple[int, ...] = (4, 6, 8, 12)

RGBA = tuple[float, float, float, float]

# ⑥ palette: {stainless/brass/PVC/cast-iron} body x {blue/red/yellow/black} grip.
# Observed across the 5-star pool (blue parent grip, red gear-probe rim, and the
# stainless/brass/cast-iron/PVC body finishes noted in the source-map §6-axis row).
PALETTES: dict[PaletteStyle, dict[str, RGBA]] = {
    "stainless_blue": {
        "body": (0.78, 0.80, 0.80, 1.0), "body2": (0.64, 0.67, 0.68, 1.0),
        "dark": (0.25, 0.27, 0.28, 1.0), "ptfe": (0.90, 0.88, 0.79, 1.0),
        "packing": (0.09, 0.10, 0.10, 1.0), "grip": (0.03, 0.16, 0.48, 1.0),
    },
    "brass_red": {
        "body": (0.80, 0.63, 0.24, 1.0), "body2": (0.68, 0.52, 0.20, 1.0),
        "dark": (0.30, 0.22, 0.08, 1.0), "ptfe": (0.92, 0.90, 0.82, 1.0),
        "packing": (0.10, 0.09, 0.08, 1.0), "grip": (0.74, 0.10, 0.09, 1.0),
    },
    "pvc_yellow": {
        "body": (0.86, 0.86, 0.82, 1.0), "body2": (0.72, 0.73, 0.70, 1.0),
        "dark": (0.30, 0.31, 0.30, 1.0), "ptfe": (0.93, 0.92, 0.86, 1.0),
        "packing": (0.12, 0.12, 0.12, 1.0), "grip": (0.92, 0.78, 0.10, 1.0),
    },
    "castiron_black": {
        "body": (0.34, 0.35, 0.36, 1.0), "body2": (0.28, 0.29, 0.30, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0), "ptfe": (0.88, 0.86, 0.78, 1.0),
        "packing": (0.08, 0.08, 0.08, 1.0), "grip": (0.05, 0.05, 0.05, 1.0),
    },
    "stainless_red": {
        "body": (0.70, 0.72, 0.73, 1.0), "body2": (0.60, 0.62, 0.63, 1.0),
        "dark": (0.24, 0.26, 0.27, 1.0), "ptfe": (0.90, 0.88, 0.79, 1.0),
        "packing": (0.09, 0.10, 0.10, 1.0), "grip": (0.78, 0.12, 0.10, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Standardized DN15 hardware constants (meters), lifted from origin __001.
# The ball / bore / seat / chamber numbers are FIXED (Contract 2c: standardized
# hardware) so the sub-mm PTFE seat<->ball seal contact stays intact across every
# slot combo; ⑤ size is record_only. Only body_hex_across and lever_length vary.
# ---------------------------------------------------------------------------
_BORE_R = 0.0100        # ball through-bore radius
_BORE_CUT_R = 0.0107    # body through-bore radius (bore + wall clearance)
_BALL_R = 0.0185        # ported ball radius
_CHAMBER_CUT_R = 0.0206 # spherical cavity cut from the body
_CHAMBER_R = 0.034      # body chamber outer sphere radius
_SEAT_OUTER = 0.0180
_SEAT_INNER = 0.0105
_HUB_R = 0.0115
_STEM_R = 0.00425
_GLAND_DECK_Z = 0.071   # integral-gland deck height (origin hub base z)
_COLUMN_RISE = 0.060    # extended-stem column rise
_ISO_PAD_TOP = 0.077    # iso 5211 pad top height


# ---------------------------------------------------------------------------
# CadQuery helpers (shared with the 5-star sources).
# ---------------------------------------------------------------------------
def _cylinder_x(x0: float, length: float, radius: float) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x0, 0.0, 0.0)).circle(radius).extrude(length)


def _annulus_x(x0: float, length: float, outer_radius: float, inner_radius: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ", origin=(x0, 0.0, 0.0))
        .circle(outer_radius).circle(inner_radius).extrude(length)
    )


def _hex_x(x0: float, length: float, diameter: float) -> cq.Workplane:
    return cq.Workplane("YZ", origin=(x0, 0.0, 0.0)).polygon(6, diameter).extrude(length)


def _cylinder_y(y0: float, length: float, radius: float) -> cq.Workplane:
    return cq.Workplane("XZ", origin=(0.0, y0, 0.0)).circle(radius).extrude(length)


def _hex_y(y0: float, length: float, diameter: float) -> cq.Workplane:
    return cq.Workplane("XZ", origin=(0.0, y0, 0.0)).polygon(6, diameter).extrude(length)


def _annulus_z(z0: float, height: float, outer_radius: float, inner_radius: float) -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, z0))
        .circle(outer_radius).circle(inner_radius).extrude(height)
    )


def _hex_z(z0: float, height: float, diameter: float, bore_radius: float | None = None) -> cq.Workplane:
    shape = cq.Workplane("XY", origin=(0.0, 0.0, z0)).polygon(6, diameter)
    if bore_radius is not None:
        shape = shape.circle(bore_radius)
    return shape.extrude(height)


def _thread_rings_x(start_x: float, step: float, count: int, thickness: float) -> cq.Workplane:
    rings = _annulus_x(start_x, thickness, 0.0146, 0.0107)
    for i in range(1, count):
        rings = rings.union(_annulus_x(start_x + i * step, thickness, 0.0146, 0.0107))
    return rings


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PictureX0611BallValveConfig:
    body_form: BodyForm = "inline_2way"
    connection_ends: ConnectionEnds = "threaded"
    handle: Handle = "straight_lever"
    stem_mount: StemMount = "integral_gland"
    palette_style: PaletteStyle = "stainless_blue"
    flange_bolt_hole_count: int = 4
    body_hex_across: float = 0.057
    lever_length: float = 0.151
    name: str = "pictureX_0611_ball_valve_with_quarter_turn_handle"


@dataclass(frozen=True)
class ResolvedPictureX0611BallValveConfig:
    body_form: BodyForm
    connection_ends: ConnectionEnds
    handle: Handle
    stem_mount: StemMount
    palette_style: PaletteStyle
    flange_bolt_hole_count: int
    body_hex_across: float
    lever_length: float
    gland_top_z: float
    name: str


def config_from_seed(seed: int) -> PictureX0611BallValveConfig:
    rng = random.Random(seed)
    return PictureX0611BallValveConfig(
        body_form=rng.choice(BODY_FORMS),
        connection_ends=rng.choice(CONNECTION_ENDS),
        handle=rng.choice(HANDLES),
        stem_mount=rng.choice(STEM_MOUNTS),
        palette_style=rng.choice(PALETTE_STYLES),
        flange_bolt_hole_count=rng.choice(FLANGE_BOLT_COUNTS),
        body_hex_across=round(rng.uniform(0.052, 0.062), 4),
        lever_length=round(rng.uniform(0.110, 0.170), 4),
        name=f"pictureX_0611_ball_valve_seed_{seed}",
    )


def _mount_deck_z(stem_mount: StemMount) -> float:
    if stem_mount == "extended_stem":
        return 0.065 + _COLUMN_RISE
    if stem_mount == "iso5211_pad":
        return _ISO_PAD_TOP
    return _GLAND_DECK_Z


def resolve_config(config: PictureX0611BallValveConfig) -> ResolvedPictureX0611BallValveConfig:
    n = config.flange_bolt_hole_count if config.flange_bolt_hole_count in FLANGE_BOLT_COUNTS else 4
    return ResolvedPictureX0611BallValveConfig(
        body_form=config.body_form,
        connection_ends=config.connection_ends,
        handle=config.handle,
        stem_mount=config.stem_mount,
        palette_style=config.palette_style,
        flange_bolt_hole_count=n,
        body_hex_across=clamp(config.body_hex_across, 0.050, 0.064),
        lever_length=clamp(config.lever_length, 0.100, 0.180),
        gland_top_z=_mount_deck_z(config.stem_mount),
        name=config.name,
    )


def slot_choices_for_config(r: ResolvedPictureX0611BallValveConfig) -> list[tuple[str, str]]:
    choices = [
        ("body_form", r.body_form),
        ("connection_ends", r.connection_ends),
        ("handle", r.handle),
        ("stem_mount", r.stem_mount),
        ("palette_style", r.palette_style),
    ]
    if r.connection_ends == "flanged":
        choices.append(("flange_bolt_hole_count", str(r.flange_bolt_hole_count)))
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------
def _material_set(model: ArticulatedObject, palette_style: PaletteStyle) -> dict[str, object]:
    palette = PALETTES[palette_style]
    return {k: model.material(f"{palette_style}_{k}", rgba=v) for k, v in palette.items()}


def _vis(part, solid: cq.Workplane, name: str, material, tol: float = 0.00035, atol: float = 0.07) -> None:
    part.visual(
        mesh_from_cadquery(solid, name, tolerance=tol, angular_tolerance=atol),
        material=material,
        name=name, material_class_id="metal.stainless_matte",
    )


def _build_body_casting(body, r: ResolvedPictureX0611BallValveConfig, mats) -> None:
    """Body form A: main casting + end cap, with the chamber + bore(s) cut."""
    hexd = r.body_hex_across
    if r.body_form == "angle_body":
        # 90-degree elbow: central chamber + X inlet + Y outlet (var_angle_body L173-193).
        main = cq.Workplane("XY").sphere(_CHAMBER_R)
        main = main.union(_cylinder_x(-0.039, 0.042, 0.030))
        main = main.union(_cylinder_y(0.0, 0.050, 0.027))
        main = main.union(_hex_y(-0.005, 0.038, hexd))
        main = main.union(
            cq.Workplane("XY", origin=(0.0, 0.0, 0.017)).circle(0.0145).extrude(0.034)
        )
        main = main.cut(_cylinder_x(-0.090, 0.095, _BORE_CUT_R))
        main = main.cut(_cylinder_y(0.005, 0.060, _BORE_CUT_R))
        main = main.cut(cq.Workplane("XY").sphere(_CHAMBER_CUT_R))
        main = main.cut(cq.Workplane("XY").circle(0.0051).extrude(0.080))
        _vis(body, main, "main_body", mats["body"])
        # short X inlet end cap
        cap = _hex_x(-0.055, 0.040, hexd + 0.004)
        cap = cap.union(_cylinder_x(-0.058, 0.044, 0.0292))
        cap = cap.cut(_cylinder_x(-0.065, 0.060, _BORE_CUT_R))
        _vis(body, cap, "end_cap", mats["body2"])
        return

    # inline / lport / tport share the origin main casting (origin L119-142).
    main = _cylinder_x(-0.039, 0.081, 0.030)
    main = main.union(cq.Workplane("XY").sphere(_CHAMBER_R))
    main = main.union(_hex_x(0.031, 0.043, hexd))
    main = main.union(_cylinder_x(0.034, 0.047, 0.0277))
    main = main.union(
        cq.Workplane("XY", origin=(0.0, 0.0, 0.017)).circle(0.0145).extrude(0.034)
    )
    if r.body_form == "lport_3way":
        main = main.union(_hex_y(-0.001, 0.040, hexd))
        main = main.union(_cylinder_y(0.0, 0.048, 0.0277))
    elif r.body_form == "tport_3way":
        main = main.union(_hex_y(0.006, 0.038, hexd - 0.004))
        main = main.union(_cylinder_y(0.0, 0.047, 0.025))
    # bores
    main = main.cut(_cylinder_x(-0.090, 0.180, _BORE_CUT_R))
    if r.body_form in ("lport_3way", "tport_3way"):
        main = main.cut(_cylinder_y(0.006, 0.090, _BORE_CUT_R))
    main = main.cut(cq.Workplane("XY").sphere(_CHAMBER_CUT_R))
    main = main.cut(cq.Workplane("XY").circle(0.0051).extrude(0.080))
    _vis(body, main, "main_body", mats["body"])

    end_cap = _hex_x(-0.081, 0.047, hexd + 0.004)
    end_cap = end_cap.union(_cylinder_x(-0.084, 0.050, 0.0292))
    end_cap = end_cap.cut(_cylinder_x(-0.091, 0.064, _BORE_CUT_R))
    _vis(body, end_cap, "end_cap", mats["body2"])


def _build_seats(body, mats) -> None:
    """PTFE seat rings that locally bear on the ball (origin L229-248)."""
    _vis(body, _annulus_x(-0.0180, 0.0030, _SEAT_OUTER, _SEAT_INNER), "seat_left", mats["ptfe"], 0.00025, 0.06)
    _vis(body, _annulus_x(0.0150, 0.0030, _SEAT_OUTER, _SEAT_INNER), "seat_right", mats["ptfe"], 0.00025, 0.06)


def _build_ends(body, r: ResolvedPictureX0611BallValveConfig, mats) -> None:
    """Connection ends B."""
    ends = r.connection_ends
    # angle body only has one X port (right side is the Y outlet); still put a
    # port treatment on the X inlet + (for non-angle) both sides.
    sides = [("left", -0.085, -1.0), ("right", 0.078, 1.0)]
    if r.body_form == "angle_body":
        sides = [("left", -0.058, -1.0)]  # short X inlet face of the elbow

    if ends == "threaded":
        for name, x0, sign in sides:
            # raised port lip overlapping the casting + internal thread rings
            # seated inside the bore (origin L161-203), both derived from x0.
            lip_x = x0 - 0.001 if sign > 0 else x0 - 0.002
            _vis(body, _annulus_x(lip_x, 0.0035, 0.0300, 0.0107), f"{name}_port_lip", mats["body"], 0.00025, 0.06)
            thr_start = (x0 - 0.028) if sign > 0 else (x0 + 0.006)
            _vis(body, _thread_rings_x(thr_start, 0.0043, 6, 0.00135), f"{name}_threads", mats["dark"], 0.00022, 0.06)
    elif ends == "flanged":
        n = r.flange_bolt_hole_count
        for name, x0, sign in sides:
            fx = x0 - 0.008 if sign < 0 else x0 - 0.002  # overlap the casting (no island)
            _vis(body, _flange_disc_x(fx, 0.010, 0.040, 0.0107, n, 0.0028, 0.030), f"{name}_flange", mats["body2"], 0.00028, 0.07)
    elif ends == "compression":
        for name, x0, sign in sides:
            nut_x = x0 - 0.002 * sign
            _vis(body, _hex_x(nut_x, 0.012, 0.030), f"{name}_comp_nut", mats["body2"], 0.00028, 0.06)
            fer_x = nut_x + 0.012 * sign if sign > 0 else nut_x - 0.008
            _vis(body, _annulus_x(fer_x, 0.008, 0.012, 0.0088), f"{name}_ferrule", mats["dark"], 0.00025, 0.06)
            stub_x = fer_x + 0.008 * sign if sign > 0 else fer_x - 0.014
            _vis(body, _annulus_x(stub_x, 0.014, 0.0088, 0.0068), f"{name}_stub", mats["body"], 0.00025, 0.06)
    elif ends == "hose_barb":
        for name, x0, sign in sides:
            _vis(body, _barb_spigot_x(x0, sign), f"{name}_barb", mats["body"], 0.0003, 0.07)
    elif ends == "solder":
        for name, x0, sign in sides:
            cup_x = x0 - 0.006 if sign < 0 else x0
            _vis(body, _annulus_x(cup_x, 0.017, 0.0160, 0.0120), f"{name}_solder_cup", mats["body"], 0.0003, 0.06)


def _flange_disc_x(x0, thickness, outer_r, bore_r, bolt_count, hole_r, circle_d) -> cq.Workplane:
    """Raised-face flange disc with N bolt holes on a bolt circle (var_flanged_ends L69-114)."""
    flange = _annulus_x(x0, thickness, outer_r, bore_r)
    bolt_circle_r = circle_d / 2.0
    for i in range(bolt_count):
        ang = 2.0 * math.pi * i / bolt_count
        y = bolt_circle_r * math.cos(ang)
        z = bolt_circle_r * math.sin(ang)
        hole = cq.Workplane("YZ", origin=(x0 - 0.001, y, z)).circle(hole_r).extrude(thickness + 0.002)
        flange = flange.cut(hole)
    return flange


def _barb_spigot_x(x0: float, sign: float) -> cq.Workplane:
    """Barbed hose spigot: stacked ridges (var_hose_barb_ends L69-117). Starts
    ~6mm inside the port face so it contacts the casting (no island)."""
    start = x0 - 0.006 if sign > 0 else x0 - 0.024
    spigot = _annulus_x(start, 0.030, 0.011, 0.0068)
    for i in range(3):
        spigot = spigot.union(_annulus_x(start + 0.008 + i * 0.008, 0.004, 0.014, 0.0068))
    return spigot


def _build_mount(body, r: ResolvedPictureX0611BallValveConfig, mats) -> None:
    """Stem/bonnet D. Sets up the gland stack; deck top = r.gland_top_z where the
    hub seats (single-sourced via _mount_deck_z). Adds a flat stem_collar whose
    top face the MatingContract pins the rotor hub to."""
    deck = r.gland_top_z
    # common packing gland (origin L250-279)
    _vis(body, _annulus_z(0.0415, 0.0050, 0.0090, 0.00465), "stem_packing", mats["packing"], 0.00022, 0.06)
    _vis(body, _hex_z(0.0460, 0.0150, 0.0270, 0.00515), "gland_nut", mats["body"], 0.00025, 0.06)
    _vis(body, _annulus_z(0.0610, 0.0040, 0.0140, 0.00515), "gland_washer", mats["dark"], 0.00022, 0.06)

    if r.stem_mount == "extended_stem":
        # tall standoff column bridging washer_top(0.065) up to the deck.
        _vis(body, _annulus_z(0.0650, deck - 0.0650, 0.0140, 0.0055), "standoff_column", mats["body2"], 0.0003, 0.06)
        _vis(body, _annulus_z(deck - 0.012, 0.012, 0.0130, 0.0055), "stem_bushing", mats["dark"], 0.00025, 0.06)
    elif r.stem_mount == "iso5211_pad":
        # bonnet neck (washer_top up to pad bottom) + ISO 5211 pad + 4 bolt holes.
        pad_bot = deck - 0.007
        _vis(body, _annulus_z(0.0650, pad_bot - 0.0650, 0.0150, 0.0055), "bonnet_neck", mats["dark"], 0.00025, 0.06)
        pad = _annulus_z(pad_bot, 0.007, 0.033, 0.005)
        for i in range(4):
            ang = math.pi / 4.0 + i * math.pi / 2.0
            bx, by = 0.024 * math.cos(ang), 0.024 * math.sin(ang)
            pad = pad.cut(
                cq.Workplane("XY", origin=(bx, by, pad_bot - 0.001)).circle(0.0025).extrude(0.009)
            )
        _vis(body, pad, "iso_mounting_pad", mats["body2"], 0.0003, 0.07)

    # quarter-turn stop plate with two lugs (origin L281-301). Overlaps the deck
    # element below and the collar above so it stays connected.
    stop = _annulus_z(deck - 0.008, 0.0060, 0.0170, 0.0055)
    stop = stop.union(cq.Workplane("XY").box(0.013, 0.008, 0.004).translate((0.016, -0.011, deck - 0.005)))
    stop = stop.union(cq.Workplane("XY").box(0.008, 0.013, 0.004).translate((-0.011, 0.016, deck - 0.005)))
    _vis(body, stop, "stop_plate", mats["body2"], 0.00025, 0.07)

    # flat thrust collar: its +z face is the hub seat (MatingContract target);
    # overlaps the stop_plate below it.
    _vis(body, _annulus_z(deck - 0.006, 0.0060, 0.0140, 0.0055), "stem_collar", mats["dark"], 0.00022, 0.06)

    if r.handle == "lockable_lever":
        # two body lockout ears with padlock holes (var_lockable_lever L307-337).
        # Rooted down into the stop_plate/collar (radius ~0.017) so no island.
        for name, ang in (("open", 0.0), ("closed", math.pi / 2.0)):
            ex, ey = 0.017 * math.cos(ang), 0.017 * math.sin(ang)
            ear = cq.Workplane("XY", origin=(ex, ey, deck + 0.002)).box(0.008, 0.006, 0.020)
            ear = ear.cut(
                cq.Workplane("XZ", origin=(ex, ey - 0.006, deck + 0.008)).circle(0.0018).extrude(0.014)
            )
            _vis(body, ear, f"lockout_ear_{name}", mats["body2"], 0.00022, 0.07)


def _build_ball(rotor, body_form: BodyForm, mats) -> None:
    """Ported ball A: a bored sphere (Rule 3 — never a box)."""
    ball = cq.Workplane("XY").sphere(_BALL_R)
    if body_form == "inline_2way":
        ball = ball.cut(_cylinder_x(-0.024, 0.048, _BORE_R))
    elif body_form == "lport_3way":
        ball = ball.cut(_cylinder_x(-0.024, 0.029, _BORE_R))
        ball = ball.cut(_cylinder_y(0.005, 0.029, _BORE_R))
    elif body_form == "tport_3way":
        ball = ball.cut(_cylinder_x(-0.024, 0.048, _BORE_R))
        ball = ball.cut(_cylinder_y(0.0, 0.024, _BORE_R))
    else:  # angle_body
        ball = ball.cut(_cylinder_x(-0.024, 0.028, _BORE_R))
        ball = ball.cut(_cylinder_y(0.004, 0.028, _BORE_R))
    _vis(rotor, ball, "ball", mats["body"], 0.00028, 0.055)


def _build_rotor(rotor, r: ResolvedPictureX0611BallValveConfig, mats) -> None:
    """Rotor: ball + stem + hub + handle op + grip + stop tab + retaining nut."""
    _build_ball(rotor, r.body_form, mats)
    hub_z = r.gland_top_z

    # stem from ball up to the hub, with a square drive lug (origin L340-357).
    stem = cq.Workplane("XY", origin=(0.0, 0.0, 0.0140)).circle(_STEM_R).extrude(hub_z - 0.0100)
    stem = stem.union(cq.Workplane("XY").box(0.0080, 0.0080, 0.0200).translate((0.0, 0.0, hub_z - 0.020)))
    _vis(rotor, stem, "stem", mats["dark"], 0.0002, 0.055)

    # hub seats on the body stem_collar (bottom face -z at hub_z).
    _vis(rotor, cq.Workplane("XY", origin=(0.0, 0.0, hub_z)).circle(_HUB_R).extrude(0.0080), "handle_hub", mats["body2"], 0.00022, 0.06)

    _build_handle_op(rotor, r, mats, hub_z)

    # downward stop tang sweeping between the fixed stop-plate lugs (origin L423-437).
    _vis(rotor, cq.Workplane("XY").box(0.011, 0.007, 0.010).translate((0.014, 0.0, hub_z + 0.002)), "stop_tab", mats["dark"], 0.0002, 0.07)
    # stem retaining nut seated on the hub top (origin L439-448); overlaps the
    # hub so it stays connected under every handle op.
    _vis(rotor, _hex_z(hub_z + 0.005, 0.0090, 0.0160), "retaining_nut", mats["body"], 0.00022, 0.06)


def _build_handle_op(rotor, r: ResolvedPictureX0611BallValveConfig, mats, hub_z: float) -> None:
    """Handle C: the operator geometry + colored grip, mounted on the hub."""
    handle = r.handle
    llen = r.lever_length
    lz = hub_z + 0.007  # lever body sits just above the hub

    if handle in ("straight_lever", "lockable_lever"):
        # stamped tapered lever (origin L372-403), scaled to lever_length.
        sx = llen / 0.151
        profile = [
            (-0.010, lz), (0.014, lz), (0.040 * sx, lz + 0.012), (0.151 * sx, lz + 0.012),
            (0.151 * sx, lz + 0.019), (0.039 * sx, lz + 0.019), (0.012, lz + 0.008), (-0.010, lz + 0.008),
        ]
        lever = cq.Workplane("XZ").polyline(profile).close().extrude(0.0140, both=True)
        lever = lever.cut(cq.Workplane("XZ", origin=(0.030, 0.0, lz + 0.013)).circle(0.0028).extrude(0.024, both=True))
        _vis(rotor, lever, "handle_op", mats["body2"], 0.00025, 0.07)
        # blue/red/... vinyl grip sleeve over the lever tip.
        grip = cq.Workplane("XY", origin=(0.101 * sx, 0.0, lz + 0.010)).slot2D(0.124 * sx, 0.023).extrude(0.0115)
        _vis(rotor, grip, "grip", mats["grip"], 0.00025, 0.055)
        if handle == "lockable_lever":
            # lockout lug hanging down to meet the body ears.
            _vis(rotor, cq.Workplane("XY").box(0.006, 0.006, 0.014).translate((0.020, 0.0, hub_z + 0.006)), "lockout_lug", mats["dark"], 0.0002, 0.07)
    elif handle == "tee_bar":
        # Y-axis crossbar forming a T with the stem (var_tee_handle L374-403).
        # (cadquery "XZ" normal is -Y; translate to center the bar on the axis.)
        cbar_z = lz + 0.004
        clen = clamp(llen * 0.6, 0.070, 0.110)
        crossbar = cq.Workplane("XZ", origin=(0.0, 0.0, cbar_z)).circle(0.006).extrude(clen).translate((0.0, clen / 2.0, 0.0))
        _vis(rotor, crossbar, "handle_op", mats["body2"], 0.00025, 0.06)
        cap = cq.Workplane("XZ", origin=(0.0, 0.0, cbar_z)).circle(0.0075).extrude(0.011)
        _vis(rotor, cap.translate((0.0, clen / 2.0, 0.0)), "grip", mats["grip"], 0.00025, 0.06)
        _vis(rotor, cap.translate((0.0, -clen / 2.0 + 0.011, 0.0)), "grip2", mats["grip"], 0.00025, 0.06)
    else:  # oval_loop
        # flat elongated loop plate seated on the hub top (var_oval_lever L372-391).
        oz = hub_z + 0.004  # overlaps the hub (top at hub_z+0.008)
        oval_cx = clamp(llen * 0.30, 0.038, 0.060)
        rx, ry = oval_cx, 0.020
        plate = cq.Workplane("XY", origin=(oval_cx, 0.0, oz)).ellipse(rx, ry).extrude(0.010)
        plate = plate.cut(cq.Workplane("XY", origin=(oval_cx, 0.0, oz - 0.001)).ellipse(rx - 0.010, ry - 0.008).extrude(0.012))
        _vis(rotor, plate, "handle_op", mats["grip"], 0.00028, 0.055)
        _vis(rotor, cq.Workplane("XY", origin=(0.010, 0.0, oz)).circle(0.010).extrude(0.010), "grip", mats["grip"], 0.00025, 0.06)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_pictureX_0611_ball_valve_with_quarter_turn_handle(
    config: PictureX0611BallValveConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or PictureX0611BallValveConfig())
    model = ArticulatedObject(name=r.name, assets=assets, meta={"subcategory": "ball_valve_with_quarter_turn_handle"})
    mats = _material_set(model, r.palette_style)

    body = model.part("valve_body", meta={"port_axis": "x"})
    _build_body_casting(body, r, mats)
    _build_ends(body, r, mats)
    _build_seats(body, mats)
    _build_mount(body, r, mats)

    rotor = model.part("valve_rotor", meta={"open_pose": 0.0, "closed_pose": math.pi / 2.0})
    _build_rotor(rotor, r, mats)

    model.articulation(
        "body_to_rotor",
        ArticulationType.REVOLUTE,
        parent=body,
        child=rotor,
        origin=Origin(),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=18.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0),
        mating=MatingContract(
            parent_face_geometry="stem_collar",
            parent_face_side="positive_z",
            child_face_geometry="handle_hub",
            child_face_side="negative_z",
            contact_tol=0.0016,
        ),
        meta={
            "type": "revolute",
            "axis": (0.0, 0.0, 1.0),
            "origin": (0.0, 0.0, 0.0),
            "range": (0.0, math.pi / 2.0),
            "positive_motion": "turns lever from pipe-parallel (+X) open toward +Y closed",
        },
    )
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pictureX_0611_ball_valve_with_quarter_turn_handle(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_ball_valve_with_quarter_turn_handle(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _aabb_center(bounds):
    if bounds is None:
        return None
    lo, hi = bounds
    return tuple((lo[i] + hi[i]) * 0.5 for i in range(3))


def run_pictureX_0611_ball_valve_with_quarter_turn_handle_tests(
    object_model: ArticulatedObject, config: PictureX0611BallValveConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("two-part topology", part_names == {"valve_body", "valve_rotor"}, details=str(sorted(part_names)))
    ctx.check("single body_to_rotor joint", joint_names == {"body_to_rotor"}, details=str(sorted(joint_names)))

    body = object_model.get_part("valve_body")
    rotor = object_model.get_part("valve_rotor")
    joint = object_model.get_articulation("body_to_rotor")
    rotor_visuals = {v.name for v in rotor.visuals}
    body_visuals = {v.name for v in body.visuals}

    ctx.check(
        "quarter-turn revolute identity",
        joint.articulation_type == ArticulationType.REVOLUTE
        and joint.axis == (0.0, 0.0, 1.0)
        and joint.motion_limits is not None
        and joint.motion_limits.lower == 0.0
        and abs((joint.motion_limits.upper or 0.0) - math.pi / 2.0) < 1e-9,
        details=str(joint.motion_limits),
    )
    ctx.check(
        "moving ball train present",
        {"ball", "stem", "handle_hub", "handle_op", "grip", "stop_tab", "retaining_nut"}.issubset(rotor_visuals),
        details=str(sorted(rotor_visuals)),
    )
    ctx.check(
        "body casting + seats + gland present",
        {"main_body", "end_cap", "seat_left", "seat_right", "gland_nut", "stop_plate", "stem_collar"}.issubset(body_visuals),
        details=str(sorted(body_visuals)),
    )
    # palette drives every material; grip uses the palette grip color.
    grip_mat = getattr(rotor.get_visual("grip").material, "name", "")
    ctx.check("grip material from palette", grip_mat == f"{r.palette_style}_grip", details=grip_mat)

    choices = dict(object_model.meta.get("slot_choices", ()))
    for key in ("body_form", "connection_ends", "handle", "stem_mount", "palette_style"):
        ctx.check(f"slot {key} recorded", key in choices, details=str(choices))

    # The ball rotates inside the machined body chamber (ball-in-socket) and the
    # stem shaft rotates within the body neck / gland / bonnet bore stack
    # (pin-through-sleeve): every concave bore FCL decomposes fills around the
    # rotating member. Element-scoped allowances, one per real bore, at every pose.
    chamber_elems = ("main_body", "end_cap", "seat_left", "seat_right")
    stem_bore_elems = (
        "main_body", "gland_nut", "stem_packing", "gland_washer", "stem_collar",
        "stop_plate", "standoff_column", "stem_bushing", "bonnet_neck", "iso_mounting_pad",
    )
    for elem in chamber_elems:
        if elem in body_visuals:
            ctx.allow_overlap(body, rotor, elem_a=elem, elem_b="ball",
                              reason="ported ball rotates within the body chamber (ball-in-socket).")
    for elem in stem_bore_elems:
        if elem in body_visuals:
            ctx.allow_overlap(body, rotor, elem_a=elem, elem_b="stem",
                              reason="stem shaft rotates within the machined body bore (pin-through-sleeve).")
    ctx.allow_overlap(body, rotor, elem_a="stop_plate", elem_b="stop_tab",
                      reason="quarter-turn stop tang sweeps between the fixed stop-plate lugs.")
    if r.handle == "lockable_lever":
        for ear in ("lockout_ear_open", "lockout_ear_closed"):
            if ear in body_visuals:
                ctx.allow_overlap(body, rotor, elem_a=ear, elem_b="lockout_lug",
                                  reason="lockout lug registers against the body lockout ears (padlock capture).")

    ctx.expect_contact(body, rotor, elem_a="seat_left", elem_b="ball", contact_tol=0.0008, name="left seat bears on ball")
    ctx.expect_contact(body, rotor, elem_a="seat_right", elem_b="ball", contact_tol=0.0008, name="right seat bears on ball")

    # Motion semantics: the off-axis stop tang (at +X when open) swings toward +Y
    # after a positive quarter turn, and stays at the same height (rotation ⟂ z).
    open_tab = _aabb_center(ctx.part_element_world_aabb(rotor, elem="stop_tab"))
    with ctx.pose({joint: math.pi / 2.0}):
        closed_tab = _aabb_center(ctx.part_element_world_aabb(rotor, elem="stop_tab"))
    ctx.check(
        "handle executes one positive quarter turn",
        open_tab is not None and closed_tab is not None
        and open_tab[0] > 0.006 and closed_tab[1] > 0.006
        and closed_tab[1] > open_tab[1] and open_tab[0] > closed_tab[0]
        and abs(open_tab[2] - closed_tab[2]) < 0.002,
        details=f"open={open_tab} closed={closed_tab}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)
    return ctx.report()
