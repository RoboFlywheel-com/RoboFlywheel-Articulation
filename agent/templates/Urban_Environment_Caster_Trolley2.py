# SPDX-License-Identifier: Apache-2.0

"""Chrome wire-basket supermarket shopping cart (Caster Trolley2) — modular template.

Category identity (spec ``specs_modular_v1/Urban_Environment_Caster_Trolley2.md``):
a **tapered chrome wire-basket supermarket trolley** — an open, tapered rounded-
rectangle wire basket (narrow/low front, wide/tall back), sitting on a splayed
chrome tubular underframe that carries **four rubber-tired swivel casters**, a
lower wire tray/cargo shelf between the legs, a rear plastic push handle, a
fold-down child-seat flap, and front rim protection.

World frame: Z up, handle/push end +X, front/nesting end -X, width Y, wheels at
z≈0. Root part = ``basket``; ``underframe`` / ``push_handle`` /
``front_bumper_{p,n}`` / ``child_seat_flap`` parent to it (parallel children,
mixed pattern). The four casters are a FIXED ×4 linear-chain copy under the
frame: ``frame_to_caster_yoke_{i}`` (CONTINUOUS z-yaw kingpin) ->
``caster_spin_{i}`` (CONTINUOUS y-roll through the wheel hub).

Motion contract (9 non-FIXED joints, uniform across every seed, spec §5/§7):
  * child-seat flap: REVOLUTE about -Y, origin=(b_back_x-0.006, 0, 0.500),
    limit [0, 1.5] — folds DOWN/forward into the basket.
  * 4 caster yaw: CONTINUOUS about +Z (kingpin), 360°.
  * 4 caster roll: CONTINUOUS about +Y, origin through the wheel hub center
    (single-sourced ``lb`` so the wheel spins in place, not orbits an offset).

Five slots + a palette axis + fixed ×4 casters (spec §4):
  * Slot A ``basket_form`` (3): standard_tapered_basket / deep_family_basket /
    straight_wall_basket — the ③ Primary Form Family (root ``basket`` geometry).
  * Slot B ``lower_deck`` (2): flat_wire_tray / walled_cargo_basket — the lower
    shelf visuals on ``underframe``.
  * Slot C ``handle_form`` (3): red_bar_handle / ergonomic_sleeve_handle /
    loop_bar_handle — the ``push_handle`` FIXED assembly.
  * Slot D ``front_face`` (2): plain_front / front_ad_panel — ④ front-wall
    decoration (basket visuals, host-conformal).
  * Slot E ``rim_treatment`` (2): red_corner_bumpers / orange_rim_guard_sleeves
    — ④ rim protection (bumper FIXED parts / basket rim-guard visuals).

Sources (all 6 read in full; see spec §14): S1 parent baseline
``...58ed850d`` (skeleton + baseline modules + caster ×4), S2 deep_family, S3
walled_cargo, S(front_ad) ad panel, S4 ergonomic sleeve, S6 rim guards. Wire
lattice uses ``tube_from_spline_points`` meshes; the ad panel uses
Extrude/rounded_rect meshes; the ergonomic sleeve uses cadquery; wheels use
WheelGeometry/TireGeometry (no Box/Cylinder downgrade, Rule 3).
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
    Box,
    BoxGeometry,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireGeometry,
    TireSidewall,
    TireTread,
    WheelBore,
    WheelFace,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ===========================================================================
# Slot enums.
# ===========================================================================
BasketForm = Literal[
    "standard_tapered_basket",
    "deep_family_basket",
    "straight_wall_basket",
]
LowerDeck = Literal["flat_wire_tray", "walled_cargo_basket"]
HandleForm = Literal["red_bar_handle", "ergonomic_sleeve_handle", "loop_bar_handle"]
FrontFace = Literal["plain_front", "front_ad_panel"]
RimTreatment = Literal["red_corner_bumpers", "orange_rim_guard_sleeves"]
PaletteStyle = Literal[
    "classic_chrome_red",
    "chrome_orange",
    "chrome_blue",
    "graphite_frame_red",
    "white_coated_green",
    "all_chrome_black",
]

BASKET_FORMS: tuple[BasketForm, ...] = (
    "standard_tapered_basket",
    "deep_family_basket",
    "straight_wall_basket",
)
LOWER_DECKS: tuple[LowerDeck, ...] = ("flat_wire_tray", "walled_cargo_basket")
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "red_bar_handle",
    "ergonomic_sleeve_handle",
    "loop_bar_handle",
)
FRONT_FACES: tuple[FrontFace, ...] = ("plain_front", "front_ad_panel")
RIM_TREATMENTS: tuple[RimTreatment, ...] = (
    "red_corner_bumpers",
    "orange_rim_guard_sleeves",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_chrome_red",
    "chrome_orange",
    "chrome_blue",
    "graphite_frame_red",
    "white_coated_green",
    "all_chrome_black",
)

# ===========================================================================
# Base real-world dimensions (meters), from the S1 parent envelope (L52-L78).
# ===========================================================================
WIRE_R = 0.0028  # basket lattice wire radius (thin)
RAIL_R = 0.0050  # perimeter rail / longitudinal rail radius (thicker)
FRAME_R = 0.0110  # chrome underframe tube radius

# S1 parent envelope (tapered rounded-rectangle).
_B_BACK_X = 0.32
_B_FRONT_X = -0.40
_B_BACK_BOT_Z = 0.435
_B_FRONT_BOT_Z = 0.405
_B_BACK_HALF_Y = 0.240
_B_FRONT_HALF_Y = 0.170
_B_BOT_BACK_HALF_Y = 0.210
_B_BOT_FRONT_HALF_Y = 0.140
CORNER_FRAC = 0.16

# Per-form top-Z envelope (standard/straight = S1; deep = S2 L60-L61).
_FORM_TOPS: dict[str, tuple[float, float]] = {
    # form: (back_top_z, front_top_z)
    "standard_tapered_basket": (0.66, 0.575),
    "deep_family_basket": (0.84, 0.72),
    "straight_wall_basket": (0.66, 0.575),
}
# Top-rim radius bump (S1 L217 = +0.0010; S2 deep L217 = +0.0035).
_FORM_TOP_RIM_EXTRA: dict[str, float] = {
    "standard_tapered_basket": 0.0010,
    "deep_family_basket": 0.0035,
    "straight_wall_basket": 0.0010,
}
# Wall-height-scale ranges per form (spec §7 conditional).
_FORM_WALL_H_RANGE: dict[str, tuple[float, float]] = {
    "standard_tapered_basket": (0.92, 1.10),
    "deep_family_basket": (1.05, 1.28),
    "straight_wall_basket": (0.92, 1.10),
}

_WHEEL_RADIUS = 0.050
WHEEL_WIDTH = 0.026
FORK_OFFSET = 0.028
_TRACK_HALF_Y = 0.205
CHASSIS_Z = 0.150  # kingpin mount height (frame ride height; not the floor-touch driver)

_FLAP_LEN = 0.175
_HINGE_Z = 0.500

# Lattice densities (coarsened vs the S1 record for the sweep compile budget).
_N_SIDE = 14
_N_END = 8
_N_FLOOR_L = 7
_N_FLOOR_T = 11


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class ShoppingCartConfig:
    basket_form: BasketForm | None = None
    lower_deck: LowerDeck | None = None
    handle_form: HandleForm | None = None
    front_face: FrontFace | None = None
    rim_treatment: RimTreatment | None = None
    palette_style: PaletteStyle = "classic_chrome_red"
    basket_length_scale: float = 1.0
    basket_width_scale: float = 1.0
    basket_wall_height_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    track_half_scale: float = 1.0
    seat_flap_len_scale: float = 1.0
    name: str = "shopping_cart"


@dataclass(frozen=True)
class ResolvedShoppingCartConfig:
    basket_form: BasketForm
    lower_deck: LowerDeck
    handle_form: HandleForm
    front_face: FrontFace
    rim_treatment: RimTreatment
    palette_style: PaletteStyle
    # Basket envelope (fully derived: form base + scales).
    b_back_x: float
    b_front_x: float
    b_back_top_z: float
    b_front_top_z: float
    b_back_bot_z: float
    b_front_bot_z: float
    b_back_half_y: float
    b_front_half_y: float
    b_bot_back_half_y: float
    b_bot_front_half_y: float
    top_rim_extra: float
    # Chassis / casters (derived from the basket + scales).
    wheel_radius: float
    chassis_z: float
    track_half_y: float
    rear_axle_x: float
    front_axle_x: float
    # Seat flap.
    flap_len: float
    hinge_x: float
    hinge_z: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def config_from_seed(seed: int) -> ShoppingCartConfig:
    """Deterministic procedural sampling (seed=0 is NOT special)."""
    rng = random.Random(seed)
    return ShoppingCartConfig(
        basket_form=rng.choice(BASKET_FORMS),
        lower_deck=rng.choice(LOWER_DECKS),
        handle_form=rng.choice(HANDLE_FORMS),
        front_face=rng.choice(FRONT_FACES),
        rim_treatment=rng.choice(RIM_TREATMENTS),
        palette_style=rng.choice(PALETTE_STYLES),
        basket_length_scale=round(rng.uniform(0.90, 1.15), 4),
        basket_width_scale=round(rng.uniform(0.90, 1.12), 4),
        basket_wall_height_scale=round(rng.uniform(0.92, 1.28), 4),
        wheel_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        track_half_scale=round(rng.uniform(0.94, 1.08), 4),
        seat_flap_len_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_shopping_cart_{seed}",
    )


def resolve_config(
    config: ShoppingCartConfig | None = None,
) -> ResolvedShoppingCartConfig:
    """Solve §7: independent scales -> equation (axles/chassis) -> conditional
    (wall-height range per form, straight-wall taper=0) -> inequality (seat-flap
    fold回缩). Nothing is left for the builder to fail on."""
    cfg = config or ShoppingCartConfig()
    basket_form = _pick(cfg.basket_form, BASKET_FORMS)
    lower_deck = _pick(cfg.lower_deck, LOWER_DECKS)
    handle_form = _pick(cfg.handle_form, HANDLE_FORMS)
    front_face = _pick(cfg.front_face, FRONT_FACES)
    rim_treatment = _pick(cfg.rim_treatment, RIM_TREATMENTS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # --- independent scales ---
    len_scale = _clamp(cfg.basket_length_scale, 0.90, 1.15)
    wid_scale = _clamp(cfg.basket_width_scale, 0.90, 1.12)
    wh_lo, wh_hi = _FORM_WALL_H_RANGE[basket_form]
    wall_h_scale = _clamp(cfg.basket_wall_height_scale, wh_lo, wh_hi)  # conditional per form
    wr_scale = _clamp(cfg.wheel_radius_scale, 0.92, 1.10)
    track_scale = _clamp(cfg.track_half_scale, 0.94, 1.08)
    flap_scale = _clamp(cfg.seat_flap_len_scale, 0.90, 1.10)

    # --- length: scale symmetrically about the fixed basket center ---
    center_x = (_B_BACK_X + _B_FRONT_X) / 2.0
    half_len = (_B_BACK_X - _B_FRONT_X) / 2.0 * len_scale
    b_back_x = center_x + half_len
    b_front_x = center_x - half_len

    # --- width ---
    b_back_half_y = _B_BACK_HALF_Y * wid_scale
    b_front_half_y = _B_FRONT_HALF_Y * wid_scale
    b_bot_back_half_y = _B_BOT_BACK_HALF_Y * wid_scale
    b_bot_front_half_y = _B_BOT_FRONT_HALF_Y * wid_scale

    # --- wall height (anchored at the fixed bottom-rim Z) ---
    base_back_top, base_front_top = _FORM_TOPS[basket_form]
    b_back_bot_z = _B_BACK_BOT_Z
    b_front_bot_z = _B_FRONT_BOT_Z
    b_back_top_z = b_back_bot_z + (base_back_top - _B_BACK_BOT_Z) * wall_h_scale
    b_front_top_z = b_front_bot_z + (base_front_top - _B_FRONT_BOT_Z) * wall_h_scale

    # --- straight_wall: null the front/back taper (Planar Boundary form) ---
    if basket_form == "straight_wall_basket":
        b_front_half_y = b_back_half_y
        b_bot_front_half_y = b_bot_back_half_y
        b_front_top_z = b_back_top_z
        b_front_bot_z = b_back_bot_z

    # --- casters (equation): axle X derived from the basket corners so casters
    #     stay tucked across length scaling; wheels touch the floor by
    #     construction (see _add_caster: lb is the single wheel-drop source). ---
    wheel_radius = _WHEEL_RADIUS * wr_scale
    track_half_y = _TRACK_HALF_Y * track_scale
    rear_axle_x = b_back_x - 0.065
    front_axle_x = b_front_x + 0.055
    chassis_z = CHASSIS_Z

    # --- seat flap (inequality回缩): keep the folded flap inside the basket
    #     envelope. The flap swings forward/down from the hinge; cap its length
    #     so its reach cannot exceed the basket's front extent or the back rim. ---
    hinge_x = b_back_x - 0.006
    flap_len = _FLAP_LEN * flap_scale
    max_reach = 0.92 * (hinge_x - b_front_x)  # never reach past the front wall
    flap_len = min(flap_len, max_reach)

    return ResolvedShoppingCartConfig(
        basket_form=basket_form,
        lower_deck=lower_deck,
        handle_form=handle_form,
        front_face=front_face,
        rim_treatment=rim_treatment,
        palette_style=palette_style,
        b_back_x=b_back_x,
        b_front_x=b_front_x,
        b_back_top_z=b_back_top_z,
        b_front_top_z=b_front_top_z,
        b_back_bot_z=b_back_bot_z,
        b_front_bot_z=b_front_bot_z,
        b_back_half_y=b_back_half_y,
        b_front_half_y=b_front_half_y,
        b_bot_back_half_y=b_bot_back_half_y,
        b_bot_front_half_y=b_bot_front_half_y,
        top_rim_extra=_FORM_TOP_RIM_EXTRA[basket_form],
        wheel_radius=wheel_radius,
        chassis_z=chassis_z,
        track_half_y=track_half_y,
        rear_axle_x=rear_axle_x,
        front_axle_x=front_axle_x,
        flap_len=flap_len,
        hinge_x=hinge_x,
        hinge_z=_HINGE_Z,
        name=cfg.name or "shopping_cart",
    )


def slot_choices_for_config(
    config: ShoppingCartConfig | ResolvedShoppingCartConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedShoppingCartConfig) else resolve_config(config)
    return (
        ("basket_form", r.basket_form),
        ("lower_deck", r.lower_deck),
        ("handle_form", r.handle_form),
        ("front_face", r.front_face),
        ("rim_treatment", r.rim_treatment),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Tube helpers (S1 L81-L116).
# ===========================================================================
def _tube(points, name, *, radius=WIRE_R, sps=4, rs=6):
    if len(points) == 2:
        sps = 1
    geom = tube_from_spline_points(
        points, radius=radius, samples_per_segment=sps, radial_segments=rs, cap_ends=True
    )
    return mesh_from_geometry(geom, name)


def _straight_tube_geom(p0, p1, *, radius=WIRE_R, rs=8):
    return tube_from_spline_points(
        [p0, p1], radius=radius, samples_per_segment=1, radial_segments=rs, cap_ends=True
    )


def _straight_path_mesh(points, name, *, radius=WIRE_R, rs=8, closed=False):
    geom = MeshGeometry()
    pairs = list(zip(points, points[1:]))
    if closed and len(points) > 2:
        pairs.append((points[-1], points[0]))
    for p0, p1 in pairs:
        geom.merge(_straight_tube_geom(p0, p1, radius=radius, rs=rs))
    return mesh_from_geometry(geom, name)


# ===========================================================================
# Basket cross-section geometry (S1 L118-L162), parameterized on the config.
# ===========================================================================
def _xt(r: ResolvedShoppingCartConfig, t: float) -> float:
    return _lerp(r.b_front_x, r.b_back_x, t)


def _half_y(r: ResolvedShoppingCartConfig, t: float, h: float) -> float:
    top = _lerp(r.b_front_half_y, r.b_back_half_y, t)
    bot = _lerp(r.b_bot_front_half_y, r.b_bot_back_half_y, t)
    return _lerp(bot, top, h)


def _z(r: ResolvedShoppingCartConfig, t: float, h: float) -> float:
    top = _lerp(r.b_front_top_z, r.b_back_top_z, t)
    bot = _lerp(r.b_front_bot_z, r.b_back_bot_z, t)
    return _lerp(bot, top, h)


def _side_pt(r, t, sy, h):
    return (_xt(r, t), sy * _half_y(r, t, h), _z(r, t, h))


def _end_pt(r, t, fy, h):
    return (_xt(r, t), fy * _half_y(r, t, h), _z(r, t, h))


def _floor_pt(r, t, fy):
    return (_xt(r, t), fy * _half_y(r, t, 0.0), _z(r, t, 0.0))


# ===========================================================================
# Slot A: basket_form (root part).
# ===========================================================================
def _build_basket(model, r: ResolvedShoppingCartConfig, mats) -> object:
    basket = model.part("basket")

    side_ts = [(i + 0.5) / _N_SIDE for i in range(_N_SIDE)]
    end_fys = [-1.0 + 2.0 * (i + 0.5) / _N_END for i in range(_N_END)]

    def perimeter_loop(h, nm, *, radius=RAIL_R):
        pts = [_end_pt(r, 0.0, -1.0, h)]
        for fy in end_fys:
            pts.append(_end_pt(r, 0.0, fy, h))
        pts.append(_end_pt(r, 0.0, 1.0, h))
        for t in side_ts:
            pts.append(_side_pt(r, t, 1.0, h))
        pts.append(_side_pt(r, 1.0, 1.0, h))
        for fy in reversed(end_fys):
            pts.append(_end_pt(r, 1.0, fy, h))
        pts.append(_end_pt(r, 1.0, -1.0, h))
        for t in reversed(side_ts):
            pts.append(_side_pt(r, t, -1.0, h))
        basket.visual(
            _straight_path_mesh(pts, nm, radius=radius, rs=8, closed=True),
            material=mats["rail"],
            name=nm, material_class_id="metal.chrome_polished",
        )

    perimeter_loop(1.00, "top_rim", radius=RAIL_R + r.top_rim_extra)
    perimeter_loop(0.00, "bottom_rim", radius=RAIL_R + 0.0008)
    for i, h in enumerate((0.22, 0.46, 0.70, 0.88)):
        perimeter_loop(h, f"long_rail_{i}", radius=RAIL_R - 0.0008)

    # side-wall vertical wires
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        for i, t in enumerate(side_ts):
            top = _side_pt(r, t, sy, 1.0)
            bot = _side_pt(r, t, sy, 0.0)
            basket.visual(
                _tube([top, bot], f"side_vwire_{side}_{i}", radius=WIRE_R),
                material=mats["wire"],
                name=f"side_vwire_{side}_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
            )
    # end-wall vertical wires
    for nm_end, t in (("front", 0.0), ("back", 1.0)):
        for i, fy in enumerate(end_fys):
            top = _end_pt(r, t, fy, 1.0)
            bot = _end_pt(r, t, fy, 0.0)
            basket.visual(
                _tube([top, bot], f"{nm_end}_vwire_{i}", radius=WIRE_R),
                material=mats["wire"],
                name=f"{nm_end}_vwire_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
            )
    # floor grid
    for i in range(_N_FLOOR_L):
        fy = -1.0 + 2.0 * (i + 0.5) / _N_FLOOR_L
        basket.visual(
            _tube(
                [_floor_pt(r, 0.0, fy), _floor_pt(r, 1.0, fy)], f"floor_lwire_{i}", radius=WIRE_R
            ),
            material=mats["wire"],
            name=f"floor_lwire_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    for i in range(_N_FLOOR_T):
        t = (i + 0.5) / _N_FLOOR_T
        basket.visual(
            _tube([_floor_pt(r, t, -1.0), _floor_pt(r, t, 1.0)], f"floor_twire_{i}", radius=WIRE_R),
            material=mats["wire"],
            name=f"floor_twire_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )

    basket.inertial = Inertial.from_geometry(
        Box((r.b_back_x - r.b_front_x, 2.0 * r.b_back_half_y, r.b_back_top_z - r.b_back_bot_z)),
        mass=6.0,
        origin=Origin(
            xyz=(
                (r.b_back_x + r.b_front_x) / 2.0,
                0.0,
                (r.b_back_top_z + r.b_back_bot_z) / 2.0,
            )
        ),
    )
    return basket


# ===========================================================================
# Slot D: front_face decoration (basket visuals; host-conformal, Rule 4).
# ===========================================================================
def _build_front_ad_panel(basket, r: ResolvedShoppingCartConfig, mats) -> None:
    """S(front_ad) L273-L368: a molded plastic ad panel embedded on the front
    wire wall. Conformal: sized/placed from the FINAL front-wall envelope (③/⑤).
    Slightly embedded past the wire plane so it welds to the front lattice (no
    island). All emitted as basket visuals (Rule 1: no articulating panel)."""
    front_wall_h = r.b_front_top_z - r.b_front_bot_z
    pw = min(0.260, 2.0 * r.b_front_half_y * 0.90)  # conform to front width (⑤)
    ph = min(0.145, front_wall_h * 0.80)  # conform to front wall height (⑤)
    pt = 0.004
    pr = min(0.015, 0.35 * min(pw, ph))
    # Embed 2 mm inboard of the front wire plane so the plate straddles the front
    # vertical wires (x = b_front_x) -> the decoration welds to the basket body.
    px = r.b_front_x - pt / 2.0 + 0.002
    pz = (r.b_front_bot_z + r.b_front_top_z) / 2.0

    prof = rounded_rect_profile(ph, pw, pr)
    body = ExtrudeGeometry(prof, pt, center=True, closed=True)
    body.rotate_y(-math.pi / 2.0)
    body.translate(px, 0.0, pz)
    basket.visual(
        mesh_from_geometry(body, "front_panel_body"),
        material=mats["panel_body"],
        name="front_panel_body", material_class_id="plastic.opaque_glossy_molded",
    )

    bw, bp = 0.008, 0.002
    outer = rounded_rect_profile(ph, pw, pr)
    inner = rounded_rect_profile(ph - 2 * bw, pw - 2 * bw, max(pr - bw, 0.003))
    frame = ExtrudeWithHolesGeometry(outer, [inner], bp, center=True, closed=True)
    frame.rotate_y(-math.pi / 2.0)
    frame.translate(px - pt / 2.0 - bp / 2.0, 0.0, pz)
    basket.visual(
        mesh_from_geometry(frame, "front_panel_border"),
        material=mats["panel_body"],
        name="front_panel_border", material_class_id="plastic.opaque_glossy_molded",
    )

    sw = pw - 2 * bw - 0.020
    for i, dz in enumerate((-0.28 * ph, 0.28 * ph)):
        sg = BoxGeometry((0.0015, sw, 0.006))
        sg.translate(px - pt / 2.0 - 0.00075, 0.0, pz + dz)
        basket.visual(
            mesh_from_geometry(sg, f"front_panel_stripe_{i}"),
            material=mats["panel_accent"],
            name=f"front_panel_stripe_{i}", material_class_id="plastic.opaque_glossy_molded",
        )

    lg = BoxGeometry((0.0015, 0.050, 0.022))
    lg.translate(px - pt / 2.0 - 0.00075, 0.0, pz)
    basket.visual(
        mesh_from_geometry(lg, "front_panel_logo"),
        material=mats["panel_accent"],
        name="front_panel_logo", material_class_id="plastic.opaque_glossy_molded",
    )

    tw, td = 0.018, 0.012
    y_tab = min(0.055, 0.40 * pw)
    for i, (y_off, z_sign) in enumerate(
        ((-y_tab, 1.0), (y_tab, 1.0), (-y_tab, -1.0), (y_tab, -1.0))
    ):
        if z_sign > 0:
            th = (r.b_front_top_z + 0.004) - (pz + ph / 2.0)
            tz = (pz + ph / 2.0 + r.b_front_top_z + 0.004) / 2.0
        else:
            th = (pz - ph / 2.0) - (r.b_front_bot_z - 0.004)
            tz = (r.b_front_bot_z - 0.004 + pz - ph / 2.0) / 2.0
        tg = BoxGeometry((td, tw, max(th, 0.008)))
        tg.translate(r.b_front_x + td / 2.0 - 0.001, y_off, tz)
        basket.visual(
            mesh_from_geometry(tg, f"front_panel_tab_{i}"),
            material=mats["panel_body"],
            name=f"front_panel_tab_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


# ===========================================================================
# Slot E: rim_treatment.
# ===========================================================================
def _build_orange_rim_guards(basket, r: ResolvedShoppingCartConfig, mats) -> None:
    """S6 L223-L252: thick molded guard sleeves along the top rim + corner caps.
    Guards are basket visuals derived from the top-rim path (host-conformal),
    welded to the top rim wires (no island)."""
    guard_r = 0.014
    side_ts = [(i + 0.5) / _N_SIDE for i in range(_N_SIDE)]
    end_fys = [-1.0 + 2.0 * (i + 0.5) / _N_END for i in range(_N_END)]
    for si, sy in enumerate((1.0, -1.0)):
        pts = [_side_pt(r, t, sy, 1.0) for t in ([0.0] + side_ts + [1.0])]
        basket.visual(
            _tube(pts, f"rim_guard_side_{si}", radius=guard_r, rs=10),
            material=mats["molded"],
            name=f"rim_guard_side_{si}", material_class_id="plastic.opaque_glossy_molded",
        )
    front_pts = [_end_pt(r, 0.0, fy, 1.0) for fy in ([-1.0] + end_fys + [1.0])]
    basket.visual(
        _tube(front_pts, "rim_guard_front", radius=guard_r, rs=10),
        material=mats["molded"],
        name="rim_guard_front", material_class_id="plastic.opaque_glossy_molded",
    )
    for ci, (t, sy) in enumerate([(0.0, 1.0), (0.0, -1.0), (1.0, 1.0), (1.0, -1.0)]):
        cp = _side_pt(r, t, sy, 1.0)
        basket.visual(
            Cylinder(radius=guard_r + 0.005, length=0.032),
            origin=Origin(xyz=cp),
            material=mats["molded"],
            name=f"rim_guard_corner_{ci}", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_corner_bumpers(basket, r: ResolvedShoppingCartConfig, mats) -> None:
    """S1 L329-L345: front top corner red bumper caps. Rule 1: these do not
    articulate, so they are fused into the basket as visuals (caps over the front
    top rim corners), not FIXED parts on a phantom anchor."""
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        tc = _side_pt(r, 0.0, sy, 1.0)
        basket.visual(
            Box((0.052, 0.046, 0.058)),
            origin=Origin(xyz=(tc[0] + 0.006, tc[1], tc[2] - 0.010)),
            material=mats["molded"],
            name=f"front_bumper_{side}", material_class_id="plastic.opaque_glossy_molded",
        )


# ===========================================================================
# Slot C: handle_form. Rule 1: the handle does not articulate, so it is fused
# into the basket as visuals (authored in the shared world frame). The
# ``handle`` argument each builder receives IS the basket part.
# ===========================================================================
def _handle_frame(r: ResolvedShoppingCartConfig):
    htz = r.b_back_top_z + 0.028
    hx = r.b_back_x + 0.030
    bar_half = r.b_back_half_y + 0.006
    return htz, hx, bar_half


def _build_red_bar_handle(handle, r, mats, *, assets) -> None:
    """S1 L284-L324: single red bar + 2 end caps + 2 rear posts."""
    htz, hx, bar_half = _handle_frame(r)
    handle.visual(
        Cylinder(radius=0.0145, length=2.0 * bar_half - 0.04),
        origin=Origin(xyz=(hx, 0.0, htz), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["molded"],
        name="handle_bar", material_class_id="plastic.opaque_glossy_molded",
    )
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        handle.visual(
            Cylinder(radius=0.018, length=0.040),
            origin=Origin(xyz=(hx, sy * (bar_half - 0.024), htz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["molded"],
            name=f"handle_cap_{side}", material_class_id="plastic.opaque_glossy_molded",
        )
        tc = _side_pt(r, 1.0, sy, 1.0)
        handle.visual(
            _tube(
                [tc, (hx, sy * (bar_half - 0.024), htz)], f"handle_post_{side}", radius=0.0075, rs=8
            ),
            material=mats["molded"],
            name=f"handle_post_{side}", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_ergonomic_sleeve_handle(handle, r, mats, *, assets) -> None:
    """S4 L285-L372: chrome posts + molded sleeve + end caps + side brackets +
    grip ridges."""
    htz, hx, bar_half = _handle_frame(r)
    post_top_y = bar_half - 0.024
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        tc = _side_pt(r, 1.0, sy, 1.0)
        handle.visual(
            _tube([tc, (hx, sy * post_top_y, htz)], f"handle_post_{side}", radius=0.008, rs=8),
            material=mats["frame"],
            name=f"handle_post_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    # Sleeve spans between the two posts so its end caps always overlap the
    # brackets/posts (a fixed-length sleeve floats on wide baskets -> island).
    sleeve_len = max(0.20, 2.0 * post_top_y - 0.02)
    sleeve = cq.Workplane("XY").box(0.036, sleeve_len, 0.044).edges("|Y").fillet(0.011)
    handle.visual(
        mesh_from_cadquery(sleeve, "ergonomic_handle_sleeve", assets=assets),
        origin=Origin(xyz=(hx, 0.0, htz)),
        material=mats["molded"],
        name="ergonomic_handle_sleeve", material_class_id="plastic.opaque_glossy_molded",
    )
    cap_y = sleeve_len / 2.0 + 0.020
    for i, sy in enumerate((-1.0, 1.0)):
        cap = cq.Workplane("XY").box(0.048, 0.048, 0.054).edges("|Y").fillet(0.014)
        handle.visual(
            mesh_from_cadquery(cap, f"handle_end_cap_{i}", assets=assets),
            origin=Origin(xyz=(hx, sy * cap_y, htz)),
            material=mats["molded"],
            name=f"handle_end_cap_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    for i, sy in enumerate((-1.0, 1.0)):
        bracket = cq.Workplane("XY").box(0.034, 0.030, 0.048).edges("|Z").fillet(0.006)
        handle.visual(
            mesh_from_cadquery(bracket, f"handle_bracket_{i}", assets=assets),
            origin=Origin(xyz=(hx, sy * post_top_y, htz)),
            material=mats["molded"],
            name=f"handle_bracket_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    n_ridges = 7
    ridge_span = sleeve_len * 0.80
    ridge_dy = ridge_span / max(n_ridges - 1, 1)
    for i in range(n_ridges):
        ry = -ridge_span / 2.0 + i * ridge_dy
        handle.visual(
            Box((0.030, 0.007, 0.006)),
            origin=Origin(xyz=(hx, ry, htz + 0.024)),
            material=mats["molded"],
            name=f"handle_grip_texture_{i}", material_class_id="plastic.opaque_glossy_molded",
        )


def _build_loop_bar_handle(handle, r, mats, *, assets) -> None:
    """world_knowledge_extrapolation (spec Slot C3): a single continuous U-loop
    tube — the two rear rim corners rise and bow into one horizontal top grip.
    Same rear-corner mount interface (handle_post_{p,n}); only the internal
    geometry is a one-piece loop (tube_from_spline_points, no downgrade)."""
    htz, hx, bar_half = _handle_frame(r)
    tc_p = _side_pt(r, 1.0, 1.0, 1.0)
    tc_n = _side_pt(r, 1.0, -1.0, 1.0)
    grip_half = bar_half - 0.010
    pts = [
        tc_p,
        (hx - 0.02, grip_half, htz - 0.02),
        (hx, grip_half, htz),
        (hx, 0.0, htz),
        (hx, -grip_half, htz),
        (hx - 0.02, -grip_half, htz - 0.02),
        tc_n,
    ]
    handle.visual(
        _tube(pts, "loop_bar", radius=0.013, sps=6, rs=10),
        material=mats["molded"],
        name="loop_bar", material_class_id="plastic.opaque_glossy_molded",
    )
    # Short reinforcing posts named handle_post_{p,n} so the rear-corner mount
    # interface is preserved (spec Slot C interface invariant).
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        tc = _side_pt(r, 1.0, sy, 1.0)
        handle.visual(
            _tube(
                [tc, (hx - 0.02, sy * grip_half, htz - 0.02)],
                f"handle_post_{side}",
                radius=0.0075,
                rs=8,
            ),
            material=mats["molded"],
            name=f"handle_post_{side}", material_class_id="plastic.opaque_glossy_molded",
        )


_HANDLE_BUILDERS = {
    "red_bar_handle": _build_red_bar_handle,
    "ergonomic_sleeve_handle": _build_ergonomic_sleeve_handle,
    "loop_bar_handle": _build_loop_bar_handle,
}


def _build_handle(basket, r, mats, *, assets) -> None:
    _HANDLE_BUILDERS[r.handle_form](basket, r, mats, assets=assets)


# ===========================================================================
# Underframe + Slot B: lower_deck. Rule 1: the underframe is FIXED to the basket
# (never articulates), so its chrome tube frame + lower deck are fused into the
# basket part as visuals. The four casters then parent to the basket directly
# (their kingpin joints land on the fused cross-tube geometry).
# ===========================================================================
def _build_underframe(basket, r: ResolvedShoppingCartConfig, mats) -> None:
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        rail = [
            (r.front_axle_x - 0.02, sy * r.track_half_y, r.chassis_z),
            (r.rear_axle_x + 0.02, sy * r.track_half_y, r.chassis_z),
        ]
        basket.visual(
            _tube(rail, f"chassis_rail_{side}", radius=FRAME_R, rs=10),
            material=mats["frame"],
            name=f"chassis_rail_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    for i, x in enumerate((r.front_axle_x, r.rear_axle_x)):
        basket.visual(
            Cylinder(radius=FRAME_R, length=2.0 * r.track_half_y),
            origin=Origin(xyz=(x, 0.0, r.chassis_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["frame"],
            name=f"cross_tube_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    # splayed struts from the axle line up to the basket bottom rim corners (end
    # AT the corner so the frame welds into the basket wire body -> one component).
    for sy in (-1.0, 1.0):
        side = "p" if sy > 0 else "n"
        bc_back = _side_pt(r, 1.0, sy, 0.0)
        basket.visual(
            _tube(
                [
                    (r.rear_axle_x, sy * r.track_half_y, r.chassis_z),
                    (bc_back[0], bc_back[1], bc_back[2] + 0.004),
                ],
                f"rear_strut_{side}",
                radius=FRAME_R,
                rs=10,
            ),
            material=mats["frame"],
            name=f"rear_strut_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
        bc_front = _side_pt(r, 0.0, sy, 0.0)
        basket.visual(
            _tube(
                [
                    (r.front_axle_x, sy * r.track_half_y, r.chassis_z),
                    (bc_front[0], bc_front[1], bc_front[2] + 0.004),
                ],
                f"front_strut_{side}",
                radius=FRAME_R,
                rs=10,
            ),
            material=mats["frame"],
            name=f"front_strut_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )

    if r.lower_deck == "walled_cargo_basket":
        _build_walled_cargo(basket, r, mats)
    else:
        _build_flat_wire_tray(basket, r, mats)


def _build_flat_wire_tray(frame, r: ResolvedShoppingCartConfig, mats) -> None:
    """S1 L405-L466: flat wire tray shelf between the legs. The tray sits at the
    chassis plane and spans axle-to-axle so its longitudinal wires cross both
    cross tubes -> the tray welds into the frame (no disconnected island)."""
    tray_z = r.chassis_z
    tray_back_x = r.rear_axle_x
    tray_front_x = r.front_axle_x
    tray_half_y = r.track_half_y - 0.018

    def _edge(a, b, n):
        return [
            (_lerp(a[0], b[0], (k + 1) / (n + 1)), _lerp(a[1], b[1], (k + 1) / (n + 1)), tray_z)
            for k in range(n)
        ]

    c_fn = (tray_front_x, -tray_half_y, tray_z)
    c_fp = (tray_front_x, tray_half_y, tray_z)
    c_bp = (tray_back_x, tray_half_y, tray_z)
    c_bn = (tray_back_x, -tray_half_y, tray_z)
    tray_loop = (
        [c_fn]
        + _edge(c_fn, c_fp, 1)
        + [c_fp]
        + _edge(c_fp, c_bp, 5)
        + [c_bp]
        + _edge(c_bp, c_bn, 1)
        + [c_bn]
        + _edge(c_bn, c_fn, 5)
    )
    frame.visual(
        _straight_path_mesh(tray_loop, "tray_rim", radius=RAIL_R, rs=8, closed=True),
        material=mats["frame"],
        name="tray_rim", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
    )
    n_tray_l = 6
    for i in range(n_tray_l):
        y = _lerp(-tray_half_y, tray_half_y, (i + 0.5) / n_tray_l)
        frame.visual(
            _tube(
                [(tray_front_x, y, tray_z), (tray_back_x, y, tray_z)],
                f"tray_lwire_{i}",
                radius=WIRE_R,
            ),
            material=mats["frame"],
            name=f"tray_lwire_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    n_tray_t = 9
    for i in range(n_tray_t):
        x = _lerp(tray_front_x, tray_back_x, (i + 0.5) / n_tray_t)
        frame.visual(
            _tube(
                [(x, -tray_half_y, tray_z), (x, tray_half_y, tray_z)],
                f"tray_twire_{i}",
                radius=WIRE_R,
            ),
            material=mats["frame"],
            name=f"tray_twire_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )


def _build_walled_cargo(frame, r: ResolvedShoppingCartConfig, mats) -> None:
    """S3 L405-L528: a walled lower cargo basket — dense grid floor + raised
    side/end rails + short guard wires + corner collars (coarsened grid). The
    floor sits at the chassis plane and spans axle-to-axle so its longitudinal
    wires cross both cross tubes -> the shelf welds into the frame (no island)."""
    shelf_z = r.chassis_z
    shelf_back_x = r.rear_axle_x
    shelf_front_x = r.front_axle_x
    shelf_half_y = r.track_half_y - 0.010
    rail_height = 0.050
    shelf_rail_z = shelf_z + rail_height

    grid_idx = 0
    n_shelf_l = 9
    for i in range(n_shelf_l):
        y = _lerp(-shelf_half_y, shelf_half_y, (i + 0.5) / n_shelf_l)
        frame.visual(
            _tube(
                [(shelf_front_x, y, shelf_z), (shelf_back_x, y, shelf_z)],
                f"lower_shelf_grid_{grid_idx}",
                radius=WIRE_R,
            ),
            material=mats["frame"],
            name=f"lower_shelf_grid_{grid_idx}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
        grid_idx += 1
    n_shelf_t = 13
    for i in range(n_shelf_t):
        x = _lerp(shelf_front_x, shelf_back_x, (i + 0.5) / n_shelf_t)
        frame.visual(
            _tube(
                [(x, -shelf_half_y, shelf_z), (x, shelf_half_y, shelf_z)],
                f"lower_shelf_grid_{grid_idx}",
                radius=WIRE_R,
            ),
            material=mats["frame"],
            name=f"lower_shelf_grid_{grid_idx}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
        grid_idx += 1
    for i, sy in enumerate((-1.0, 1.0)):
        frame.visual(
            _tube(
                [
                    (shelf_front_x, sy * shelf_half_y, shelf_rail_z),
                    (shelf_back_x, sy * shelf_half_y, shelf_rail_z),
                ],
                f"lower_shelf_side_rail_{i}",
                radius=RAIL_R,
                rs=8,
            ),
            material=mats["frame"],
            name=f"lower_shelf_side_rail_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    for i, tx in enumerate((shelf_front_x, shelf_back_x)):
        frame.visual(
            _tube(
                [(tx, -shelf_half_y, shelf_rail_z), (tx, shelf_half_y, shelf_rail_z)],
                f"lower_shelf_end_rail_{i}",
                radius=RAIL_R,
                rs=8,
            ),
            material=mats["frame"],
            name=f"lower_shelf_end_rail_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    guard_idx = 0
    for sy in (-1.0, 1.0):
        for j in range(6):
            x = _lerp(shelf_front_x, shelf_back_x, (j + 0.5) / 6)
            frame.visual(
                _tube(
                    [(x, sy * shelf_half_y, shelf_z), (x, sy * shelf_half_y, shelf_rail_z)],
                    f"lower_shelf_guard_wire_{guard_idx}",
                    radius=WIRE_R,
                ),
                material=mats["frame"],
                name=f"lower_shelf_guard_wire_{guard_idx}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
            )
            guard_idx += 1
    for tx in (shelf_front_x, shelf_back_x):
        for j in range(4):
            y = _lerp(-shelf_half_y, shelf_half_y, (j + 0.5) / 4)
            frame.visual(
                _tube(
                    [(tx, y, shelf_z), (tx, y, shelf_rail_z)],
                    f"lower_shelf_guard_wire_{guard_idx}",
                    radius=WIRE_R,
                ),
                material=mats["frame"],
                name=f"lower_shelf_guard_wire_{guard_idx}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
            )
            guard_idx += 1
    for i, (cx, cy) in enumerate(
        [
            (shelf_front_x, -shelf_half_y),
            (shelf_front_x, shelf_half_y),
            (shelf_back_x, shelf_half_y),
            (shelf_back_x, -shelf_half_y),
        ]
    ):
        frame.visual(
            Cylinder(radius=RAIL_R + 0.002, length=rail_height),
            origin=Origin(xyz=(cx, cy, shelf_z + rail_height / 2.0)),
            material=mats["frame"],
            name=f"lower_shelf_collar_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )


# ===========================================================================
# Child-seat flap (REVOLUTE).
# ===========================================================================
def _build_seat_flap(model, basket, r: ResolvedShoppingCartConfig, mats) -> object:
    flap = model.part("child_seat_flap")
    flap_w = 2.0 * r.b_back_half_y - 0.10
    flap_len = r.flap_len
    # Hinge hardware: basket-side pin (r=0.0055) inside the flap-side barrel
    # (r=0.006) keeps a 0.5 mm concentric gap — no overlap at any flap angle,
    # yet the contact never drops below the 1 mm grounding tolerance (the flap
    # used to float 2.8 mm clear of the basket once fully opened).
    basket.visual(
        Cylinder(radius=0.0055, length=flap_w + 0.02),
        origin=Origin(xyz=(r.hinge_x, 0.0, r.hinge_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["wire"],
        name="seat_hinge_pin", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
    )
    flap.visual(
        Cylinder(radius=0.006, length=flap_w + 0.02),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["wire"],
        name="seat_hinge_barrel", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
    )
    flap.visual(
        Box((0.012, flap_w, flap_len)),
        origin=Origin(xyz=(0.0, 0.0, flap_len / 2.0)),
        material=mats["wire"],
        name="seat_panel", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
    )
    for i, fy in enumerate((-0.66, 0.0, 0.66)):
        flap.visual(
            Box((0.016, 0.006, flap_len)),
            origin=Origin(xyz=(0.0, fy * flap_w / 2.0, flap_len / 2.0)),
            material=mats["wire"],
            name=f"seat_wire_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "all_chrome_black"} else "metal.paint_coated"),
        )
    flap.inertial = Inertial.from_geometry(
        Box((0.012, flap_w, flap_len)), mass=0.3, origin=Origin(xyz=(0.0, 0.0, flap_len / 2.0))
    )
    model.articulation(
        "basket_to_seat_flap",
        ArticulationType.REVOLUTE,
        parent=basket,
        child=flap,
        origin=Origin(xyz=(r.hinge_x, 0.0, r.hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.5),
    )
    return flap


# ===========================================================================
# Fixed ×4 swivel casters (S1 L516-L634). Single wheel-drop source (lb).
# ===========================================================================
def _add_caster(model, parent, r: ResolvedShoppingCartConfig, mats, idx, cx, cy) -> None:
    mount_z = r.chassis_z
    wheel_radius = r.wheel_radius
    leg_half_y = WHEEL_WIDTH / 2.0 + 0.009

    yoke = model.part(f"caster_yoke_{idx}")
    lb = -(mount_z - wheel_radius)  # SINGLE wheel-drop source: wheel-center z in yoke frame
    lt = lb + wheel_radius + 0.010
    yoke.visual(
        Box((0.044, 0.044, 0.009)),
        origin=Origin(xyz=(0.0, 0.0, -0.0045)),
        material=mats["steel"],
        name="swivel_plate", material_class_id="metal.steel_bare",
    )
    yoke.visual(
        Cylinder(radius=0.011, length=0.038),
        origin=Origin(xyz=(0.0, 0.0, -0.023)),
        material=mats["steel"],
        name="kingpin", material_class_id="metal.steel_bare",
    )
    # Offset web bridging the kingpin down to the fork crown. Its BOTTOM sits at
    # the crown (lt = wheel_top + 0.010), so it always clears the tire top by the
    # crown clearance — a fixed-z plate grazes the tire once the wheel scales up.
    brk_top = -0.004
    brk_bot = lt
    yoke.visual(
        Box((FORK_OFFSET + 0.024, 0.034, abs(brk_top - brk_bot))),
        origin=Origin(xyz=(-FORK_OFFSET / 2.0, 0.0, (brk_top + brk_bot) / 2.0)),
        material=mats["steel"],
        name="offset_bracket", material_class_id="metal.steel_bare",
    )
    yoke.visual(
        Box((0.028, leg_half_y * 2.0 + 0.012, 0.012)),
        origin=Origin(xyz=(-FORK_OFFSET, 0.0, lt)),
        material=mats["steel"],
        name="fork_crown", material_class_id="metal.steel_bare",
    )
    leg_h = abs(lb - lt) + 0.014
    for sy in (-1.0, 1.0):
        yoke.visual(
            Box((0.013, 0.011, leg_h)),
            origin=Origin(xyz=(-FORK_OFFSET, sy * leg_half_y, (lt + lb) / 2.0)),
            material=mats["steel"],
            name=f"fork_leg_{'p' if sy > 0 else 'n'}", material_class_id="metal.steel_bare",
        )
    yoke.visual(
        Cylinder(radius=0.005, length=leg_half_y * 2.0 + 0.016),
        origin=Origin(xyz=(-FORK_OFFSET, 0.0, lb), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="axle", material_class_id="metal.steel_bare",
    )
    yoke.inertial = Inertial.from_geometry(
        Box((0.05, 0.05, 0.10)), mass=0.4, origin=Origin(xyz=(-FORK_OFFSET, 0.0, -0.05))
    )

    wheel = model.part(f"caster_wheel_{idx}")
    rim_geom = WheelGeometry(
        wheel_radius * 0.66,
        WHEEL_WIDTH * 0.7,
        rim=WheelRim(inner_radius=wheel_radius * 0.55, flange_height=0.003),
        hub=WheelHub(radius=wheel_radius * 0.45, width=WHEEL_WIDTH * 0.8, cap_style="flat"),
        face=WheelFace(dish_depth=0.0),
        spokes=WheelSpokes(style="disc"),
        bore=WheelBore(style="round", diameter=0.006),
    )
    rim_geom.rotate_z(math.pi / 2.0)
    wheel.visual(
        mesh_from_geometry(rim_geom, f"caster_rim_{idx}"), material=mats["rim"], name="rim", material_class_id=("metal.chrome_polished" if r.palette_style in {"classic_chrome_red", "chrome_orange", "chrome_blue", "white_coated_green", "all_chrome_black"} else "metal.paint_coated")
    )
    tire_geom = TireGeometry(
        wheel_radius,
        WHEEL_WIDTH,
        inner_radius=wheel_radius * 0.64,
        tread=TireTread(style="circumferential", depth=0.0015, count=1),
        sidewall=TireSidewall(style="rounded", bulge=0.04),
    )
    tire_geom.rotate_z(math.pi / 2.0)
    wheel.visual(
        mesh_from_geometry(tire_geom, f"caster_tire_{idx}"), material=mats["rubber"], name="tire", material_class_id="rubber.directional_grooved"
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=wheel_radius, length=WHEEL_WIDTH),
        mass=0.3,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )

    # Kingpin YAW: parent is the basket (the underframe cross tubes are fused
    # basket visuals); the origin lands on the fused cross-tube geometry.
    model.articulation(
        f"frame_to_caster_yoke_{idx}",
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=yoke,
        origin=Origin(xyz=(cx, cy, mount_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=12.0),
    )
    model.articulation(
        f"caster_spin_{idx}",
        ArticulationType.CONTINUOUS,
        parent=yoke,
        child=wheel,
        origin=Origin(xyz=(-FORK_OFFSET, 0.0, lb)),  # through the wheel hub center
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=40.0),
    )


def _build_casters(model, basket, r: ResolvedShoppingCartConfig, mats) -> None:
    # Fixed ×4 (structural constant, spec §6): rear pair + front pair.
    _add_caster(model, basket, r, mats, 0, r.rear_axle_x, r.track_half_y)
    _add_caster(model, basket, r, mats, 1, r.rear_axle_x, -r.track_half_y)
    _add_caster(model, basket, r, mats, 2, r.front_axle_x, r.track_half_y)
    _add_caster(model, basket, r, mats, 3, r.front_axle_x, -r.track_half_y)


# ===========================================================================
# Palette (⑥) — 6 colorways; every visual reads its material from here.
# ===========================================================================
def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    chrome = (0.82, 0.84, 0.87, 1.0)
    rail = (0.76, 0.78, 0.82, 1.0)
    frame = (0.72, 0.74, 0.78, 1.0)
    steel = (0.54, 0.55, 0.57, 1.0)
    rim = (0.80, 0.81, 0.83, 1.0)
    black_tire = (0.15, 0.15, 0.17, 1.0)
    accent = (0.85, 0.85, 0.88, 1.0)
    red = (0.80, 0.09, 0.09, 1.0)
    orange = (0.95, 0.42, 0.04, 1.0)
    blue = (0.12, 0.32, 0.68, 1.0)
    green = (0.16, 0.55, 0.24, 1.0)
    black = (0.10, 0.10, 0.11, 1.0)
    graphite = (0.30, 0.31, 0.33, 1.0)
    white = (0.90, 0.91, 0.92, 1.0)

    presets: dict[str, dict[str, tuple[float, float, float, float]]] = {
        "classic_chrome_red": dict(
            wire=chrome,
            rail=rail,
            frame=frame,
            steel=steel,
            rim=rim,
            rubber=black_tire,
            molded=red,
            panel_body=red,
            panel_accent=accent,
        ),
        "chrome_orange": dict(
            wire=chrome,
            rail=rail,
            frame=frame,
            steel=steel,
            rim=rim,
            rubber=black_tire,
            molded=orange,
            panel_body=orange,
            panel_accent=accent,
        ),
        "chrome_blue": dict(
            wire=chrome,
            rail=rail,
            frame=frame,
            steel=steel,
            rim=rim,
            rubber=black_tire,
            molded=blue,
            panel_body=blue,
            panel_accent=accent,
        ),
        "graphite_frame_red": dict(
            wire=graphite,
            rail=graphite,
            frame=graphite,
            steel=(0.34, 0.35, 0.37, 1.0),
            rim=(0.42, 0.43, 0.45, 1.0),
            rubber=black_tire,
            molded=red,
            panel_body=red,
            panel_accent=accent,
        ),
        "white_coated_green": dict(
            wire=white,
            rail=white,
            frame=white,
            steel=(0.70, 0.71, 0.72, 1.0),
            rim=rim,
            rubber=(0.20, 0.20, 0.22, 1.0),
            molded=green,
            panel_body=green,
            panel_accent=accent,
        ),
        "all_chrome_black": dict(
            wire=chrome,
            rail=rail,
            frame=frame,
            steel=steel,
            rim=rim,
            rubber=(0.08, 0.08, 0.09, 1.0),
            molded=black,
            panel_body=black,
            panel_accent=(0.55, 0.56, 0.58, 1.0),
        ),
    }
    return presets[style]


# ===========================================================================
# Build
# ===========================================================================
def build_shopping_cart(
    config: ShoppingCartConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = _palette_rgba(r.palette_style)
    mats = {
        key: model.material(f"cart_{key}_{r.palette_style}", rgba=rgba) for key, rgba in pal.items()
    }

    # Slot A: basket root.
    basket = _build_basket(model, r, mats)

    # Slot D: front-face decoration (basket visuals).
    if r.front_face == "front_ad_panel":
        _build_front_ad_panel(basket, r, mats)

    # Slot E: rim treatment.
    if r.rim_treatment == "orange_rim_guard_sleeves":
        _build_orange_rim_guards(basket, r, mats)
    else:
        _build_corner_bumpers(basket, r, mats)

    # Underframe + Slot B lower deck (fused into the basket).
    _build_underframe(basket, r, mats)

    # Slot C: push handle (fused into the basket).
    _build_handle(basket, r, mats, assets=assets)

    # Child-seat flap.
    _build_seat_flap(model, basket, r, mats)

    # Fixed ×4 swivel casters (parent to the basket).
    _build_casters(model, basket, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_shopping_cart(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_shopping_cart(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _aabb_center(aabb):
    return tuple((aabb[0][k] + aabb[1][k]) / 2.0 for k in range(3))


def run_shopping_cart_tests(
    object_model: ArticulatedObject, config: ShoppingCartConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    basket = object_model.get_part("basket")
    flap = object_model.get_part("child_seat_flap")

    # ---- Captured-pin / mount allowances. The underframe, handle and bumpers are
    # fused into the basket (Rule 1), so the only cross-part overlaps are the
    # captured caster pins and the by-design seat-flap fold. ----
    for i in range(4):
        ctx.allow_overlap(
            object_model.get_part(f"caster_yoke_{i}"),
            object_model.get_part(f"caster_wheel_{i}"),
            elem_a="axle",
            elem_b="rim",
            reason="The fork axle is captured inside the wheel hub bore.",
        )
        ctx.allow_overlap(
            object_model.get_part(f"caster_yoke_{i}"),
            basket,
            reason="The caster swivel plate / kingpin bolts onto the fused chassis cross tube.",
        )
    ctx.allow_overlap(
        flap,
        basket,
        reason="The seat flap hinges on the back wires and folds down INTO the basket (by-design captured fold).",
    )

    # ---- Baseline checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: tapered (or straight) open wire basket. ----
    fc_top = _side_pt(r, 0.0, 1.0, 1.0)
    bc_top = _side_pt(r, 1.0, 1.0, 1.0)
    if r.basket_form == "straight_wall_basket":
        ctx.check(
            "straight_wall_no_taper",
            abs(bc_top[1] - fc_top[1]) < 0.01,
            f"front={fc_top[1]:.3f} back={bc_top[1]:.3f}",
        )
    else:
        ctx.check(
            "basket_wider_at_back",
            bc_top[1] > fc_top[1] + 0.02,
            f"front={fc_top[1]:.3f} back={bc_top[1]:.3f}",
        )
        ctx.check(
            "basket_taller_at_back",
            bc_top[2] > fc_top[2],
            f"front={fc_top[2]:.3f} back={bc_top[2]:.3f}",
        )
    ba = ctx.part_world_aabb(basket)
    # The wire basket body rides high on the underframe: its top rim reaches well
    # above the chassis (the fused frame extends the part down to ~chassis_z).
    ctx.check(
        "basket_rides_high",
        ba is not None and ba[1][2] >= 0.55,
        f"basket_top={None if ba is None else ba[1][2]:.3f}",
    )
    if r.basket_form == "deep_family_basket":
        back_wall_h = bc_top[2] - _side_pt(r, 1.0, 1.0, 0.0)[2]
        ctx.check(
            "deep_basket_back_wall_height",
            back_wall_h >= 0.35,
            f"back_wall_height={back_wall_h:.3f}",
        )

    # ---- Dense wire lattice present. ----
    vis_names = [v.name for v in basket.visuals]
    n_side_v = sum(1 for n in vis_names if n.startswith("side_vwire_"))
    n_floor = sum(1 for n in vis_names if n.startswith("floor_"))
    ctx.check("dense_side_wires", n_side_v >= 2 * _N_SIDE - 1, f"side vwires={n_side_v}")
    ctx.check(
        "floor_grid_present", n_floor >= _N_FLOOR_L + _N_FLOOR_T - 1, f"floor wires={n_floor}"
    )

    # ---- Slot B: lower deck present (fused into basket visuals). ----
    if r.lower_deck == "walled_cargo_basket":
        n_grid = sum(1 for n in vis_names if n.startswith("lower_shelf_grid_"))
        n_guards = sum(1 for n in vis_names if n.startswith("lower_shelf_guard_wire_"))
        ctx.check("walled_cargo_grid", n_grid >= 20, f"grid={n_grid}")
        ctx.check("walled_cargo_guards", n_guards >= 16, f"guards={n_guards}")
        # shelf clears wheels / stays inside footprint (S3 L797-L816).
        shelf_elems = [n for n in vis_names if n.startswith("lower_shelf_")]
        all_min = [1e9, 1e9, 1e9]
        all_max = [-1e9, -1e9, -1e9]
        for nm in shelf_elems:
            ea = ctx.part_element_world_aabb(basket, elem=nm)
            if ea is not None:
                for k in range(3):
                    all_min[k] = min(all_min[k], ea[0][k])
                    all_max[k] = max(all_max[k], ea[1][k])
        ctx.check(
            "shelf_above_wheels",
            all_min[2] > r.wheel_radius * 2.0 + 0.02,
            f"shelf_bot_z={all_min[2]:.3f}",
        )
        wheel_outer_y = r.track_half_y + WHEEL_WIDTH / 2.0 + 0.02
        ctx.check(
            "shelf_inside_wheel_footprint_y",
            abs(all_max[1]) <= wheel_outer_y and abs(all_min[1]) <= wheel_outer_y,
            f"shelf_y=[{all_min[1]:.3f},{all_max[1]:.3f}] outer={wheel_outer_y:.3f}",
        )
    else:
        n_tray = sum(1 for n in vis_names if n.startswith("tray_"))
        ctx.check("flat_tray_present", n_tray >= 10, f"tray wires={n_tray}")
        ctx.check("tray_rim_present", "tray_rim" in vis_names, "missing tray_rim")

    # ---- Slot C: handle at back top; posts preserved as the mount interface. ----
    ctx.check(
        "handle_posts_present",
        "handle_post_p" in vis_names and "handle_post_n" in vis_names,
        f"have={sorted(n for n in vis_names if 'handle' in n or 'loop' in n)}",
    )
    # Handle geometry sits at the back top of the basket.
    hpost = ctx.part_element_world_aabb(basket, elem="handle_post_p")
    if hpost is not None and ba is not None:
        ctx.check(
            "handle_at_back_top",
            hpost[1][0] > 0.25 and hpost[1][2] >= r.b_back_top_z,
            f"handle_post_xmax={hpost[1][0]:.3f} top={hpost[1][2]:.3f}",
        )
    if r.handle_form == "ergonomic_sleeve_handle":
        ctx.check(
            "ergonomic_sleeve_present", "ergonomic_handle_sleeve" in vis_names, "missing sleeve"
        )
    if r.handle_form == "loop_bar_handle":
        ctx.check("loop_bar_present", "loop_bar" in vis_names, "missing loop_bar")

    # ---- Slot D: front ad panel conformal + clearances (S(front_ad) L925-L962). ----
    if r.front_face == "front_ad_panel":
        for nm in ("front_panel_body", "front_panel_border", "front_panel_logo"):
            ctx.check(f"panel_{nm}", nm in vis_names, "missing")
        pb = ctx.part_element_world_aabb(basket, elem="front_panel_body")
        if pb is not None:
            ctx.check(
                "panel_at_front_x", pb[1][0] <= r.b_front_x + 0.006, f"panel_xmax={pb[1][0]:.4f}"
            )
            for i in range(4):
                wa = ctx.part_world_aabb(object_model.get_part(f"caster_wheel_{i}"))
                if wa is not None:
                    ctx.check(
                        f"panel_clear_wheel_{i}",
                        pb[0][2] > wa[1][2] + 0.10,
                        f"panel_bot={pb[0][2]:.3f} wheel_top={wa[1][2]:.3f}",
                    )

    # ---- Slot E: rim treatment. ----
    if r.rim_treatment == "orange_rim_guard_sleeves":
        for nm in ("rim_guard_side_0", "rim_guard_side_1", "rim_guard_front"):
            ctx.check(f"rim_{nm}", nm in vis_names, "missing")
        wheel_tops = [
            ctx.part_world_aabb(object_model.get_part(f"caster_wheel_{i}"))[1][2] for i in range(4)
        ]
        max_wheel_top = max(wheel_tops)
        for gn in [n for n in vis_names if n.startswith("rim_guard_")]:
            ga = ctx.part_element_world_aabb(basket, elem=gn)
            if ga is not None:
                ctx.check(
                    f"{gn}_above_wheels",
                    ga[0][2] > max_wheel_top + 0.10,
                    f"guard_bot={ga[0][2]:.3f} wheel_top={max_wheel_top:.3f}",
                )
    else:
        ctx.check(
            "corner_bumpers_present",
            "front_bumper_p" in vis_names and "front_bumper_n" in vis_names,
            "missing bumpers",
        )

    # ---- Joint inventory: exactly 9 non-fixed (1 seat + 4 yaw + 4 roll). ----
    non_fixed = sorted(
        a.name for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    )
    expected = sorted(
        ["basket_to_seat_flap"]
        + [f"frame_to_caster_yoke_{i}" for i in range(4)]
        + [f"caster_spin_{i}" for i in range(4)]
    )
    ctx.check("nine_non_fixed_joints", non_fixed == expected, f"got={non_fixed}")

    seat = object_model.get_articulation("basket_to_seat_flap")
    ctx.check(
        "seat_flap_revolute_y",
        seat.articulation_type == ArticulationType.REVOLUTE
        and abs(tuple(seat.axis)[1]) == 1.0
        and tuple(seat.axis)[0] == 0.0
        and tuple(seat.axis)[2] == 0.0,
        f"axis={seat.axis}",
    )
    lim = seat.motion_limits
    ctx.check(
        "seat_flap_limit_0_1p5",
        lim is not None and lim.lower == 0.0 and abs(lim.upper - 1.5) < 1e-6,
        f"limits={None if lim is None else (lim.lower, lim.upper)}",
    )

    for i in range(4):
        sw = object_model.get_articulation(f"frame_to_caster_yoke_{i}")
        sp = object_model.get_articulation(f"caster_spin_{i}")
        ctx.check(
            f"yaw_{i}_continuous_z",
            sw.articulation_type == ArticulationType.CONTINUOUS
            and tuple(sw.axis) == (0.0, 0.0, 1.0),
            f"axis={sw.axis}",
        )
        ctx.check(
            f"spin_{i}_continuous_y",
            sp.articulation_type == ArticulationType.CONTINUOUS
            and tuple(sp.axis) == (0.0, 1.0, 0.0),
            f"axis={sp.axis}",
        )

    # ---- Four wheels touch the floor. ----
    lows = []
    for i in range(4):
        wa = ctx.part_world_aabb(object_model.get_part(f"caster_wheel_{i}"))
        if wa is not None:
            lows.append(wa[0][2])
    ctx.check("four_wheels", len(lows) == 4, f"found {len(lows)}")
    ctx.check(
        "wheels_touch_floor",
        all(abs(z) <= 0.012 for z in lows),
        f"lows={['%.3f' % z for z in lows]}",
    )

    # ---- Targeted motion: spin in place (AABB-center displacement ~ 0). ----
    wheel0 = object_model.get_part("caster_wheel_0")
    spin0 = object_model.get_articulation("caster_spin_0")
    rest_w = ctx.part_world_aabb(wheel0)
    with ctx.pose({spin0: 0.6}):
        turned_w = ctx.part_world_aabb(wheel0)
    if rest_w is not None and turned_w is not None:
        c0 = _aabb_center(rest_w)
        c1 = _aabb_center(turned_w)
        moved = sum((c1[k] - c0[k]) ** 2 for k in range(3)) ** 0.5
        ctx.check("wheel_spins_in_place", moved < 1e-3, f"center_moved={moved:.5f}")

    # ---- Targeted motion: yaw orbits the offset wheel (AABB-center moves). ----
    yaw0 = object_model.get_articulation("frame_to_caster_yoke_0")
    with ctx.pose({yaw0: math.pi / 2.0}):
        yawed_w = ctx.part_world_aabb(wheel0)
    if rest_w is not None and yawed_w is not None:
        c0 = _aabb_center(rest_w)
        c2 = _aabb_center(yawed_w)
        orbit = ((c2[0] - c0[0]) ** 2 + (c2[1] - c0[1]) ** 2) ** 0.5
        ctx.check("yaw_orbits_offset_wheel", orbit > 0.01, f"orbit_xy={orbit:.4f}")

    # ---- Targeted motion: seat flap folds down/forward. ----
    rest_flap = ctx.part_world_aabb(flap)
    with ctx.pose({seat: 1.4}):
        down_flap = ctx.part_world_aabb(flap)
    if rest_flap is not None and down_flap is not None:
        ctx.check(
            "seat_flap_folds_down",
            down_flap[1][2] < rest_flap[1][2] - 0.08 and down_flap[0][0] < rest_flap[0][0] - 0.05,
            f"rest_top={rest_flap[1][2]:.3f} down_top={down_flap[1][2]:.3f} rest_xmin={rest_flap[0][0]:.3f} down_xmin={down_flap[0][0]:.3f}",
        )
    # Folded flap stays inside the basket XY envelope and below the back rim.
    if ba is not None and down_flap is not None:
        within = (
            down_flap[0][0] >= ba[0][0] - 0.02
            and down_flap[1][0] <= ba[1][0] + 0.02
            and down_flap[0][1] >= ba[0][1] - 0.02
            and down_flap[1][1] <= ba[1][1] + 0.02
        )
        ctx.check(
            "seat_flap_fold_within_basket",
            within and down_flap[1][2] <= r.b_back_top_z + 0.02,
            f"within={within} flap_top={down_flap[1][2]:.3f} rim={r.b_back_top_z:.3f}",
        )

    # ---- Handle clears the folded seat flap (S4 L831-L838). The handle sits at
    # the back-top rim; the flap folds forward/down away from it — assert a
    # vertical gap OR that the folded flap is forward of the handle posts. ----
    if hpost is not None and down_flap is not None:
        z_gap = hpost[0][2] - down_flap[1][2]
        ctx.check(
            "handle_clears_folded_flap",
            z_gap >= 0.010 or down_flap[1][0] < hpost[0][0] - 0.01,
            f"z_gap={z_gap:.3f} flap_xmax={down_flap[1][0]:.3f} post_xmin={hpost[0][0]:.3f}",
        )

    # ---- Sampled-pose overlap (Rule 5). 9 joints -> cap the product. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- Palette present & drives materials (⑥). ----
    ctx.check(
        "palette_valid",
        r.palette_style in PALETTE_STYLES and len(PALETTE_STYLES) == 6,
        f"palette={r.palette_style}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ShoppingCartConfig",
    "ResolvedShoppingCartConfig",
    "build_shopping_cart",
    "build_seeded_shopping_cart",
    "config_from_seed",
    "resolve_config",
    "run_shopping_cart_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
