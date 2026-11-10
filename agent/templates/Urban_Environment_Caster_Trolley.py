# SPDX-License-Identifier: Apache-2.0

"""Caster trolley / wheeled service cart modular template.

NOTE on the slug: ``caster_trolley`` = a **wheeled service / utility cart**: a
horizontal load surface (flat deck / stacked open trays / wire-mesh shelf stack
/ straight-walled utility wire bin) carried on a wheeled chassis that rides on
**N swivel casters** and is pushed via a tubular handle / upright. NOT a drawn
wagon (no draft pole, no big fixed/steered front axle), NOT a tipping barrow (the
load surface does not tilt), NOT a 2-fixed-wheel hand truck, NOT a powered AGV.

Neighbor boundary: the chrome **tapered wire-basket supermarket shopping
trolley** (nesting splayed basket, fold-down child seat, low chrome push-bar,
chrome colorway) is OUT of scope -> split into its own 小类 ``Caster Trolley2``.
A straight-walled warehouse wire bin is in scope; the tapered nesting
supermarket basket is not.

The **defining articulation** (per the user's authoritative final decision) is an
ALL-RIGID caster layout: there are **NO swivel casters anywhere**. Every wheel
mount is RIGID — ``load_surface_to_caster_yoke_{i}`` is **FIXED** for all i (no
kingpin / swivel joint anywhere) — and each wheel simply **rolls CONTINUOUSLY
about its own transverse axle through the wheel center** (roll, CONTINUOUS +Y).
The roll joint is the category-identity motion and is present on every caster of
every seed. This joint config is UNIFORM across all casters and all seeds.

Wheel APPEARANCE varies via a per-seed ``wheel_style`` axis (``solid_rubber`` /
``poly_hard`` / ``pneumatic_tread`` / ``cast_spoked``): the wheel GEOMETRY and
material change with the style, but the joint stays fixed-mount + center-roll
regardless of type. ``deck_bottom_z`` is recomputed as ``2*wheel_r + clearance``
per style so the wheel always lands on the ground (bottom z≈0).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Urban_Environment_Caster_Trolley.md`` and the
``Caster trolley`` 5-star pool (5 parents + converged fork variants).

Structure (pattern = ``mixed``): a single root **load_surface** part (Slot A)
holds the load-bearing shell; everything else parents directly to it as parallel
children:

  * Slot A ``load_surface`` (4): flat_platform_deck / stacked_open_trays /
    wire_mesh_shelf_stack / utility_wire_bin. The root part. Tray / shelf tiers
    attach as FIXED children; the utility_wire_bin lattice (floor / 4 vertical
    walls / rim) is inline on the tubular chassis root (Rule 1).
  * Slot B ``handle_upright`` (3 base + folding sub-axis): tall_inverted_U_one_end
    / handle_both_ends / full_cage_uprights, plus the fixed<->folding sub-axis
    realized as folding_handle. Mounts FIXED on the root top/back edge, except
    folding_handle (REVOLUTE -Y hinge at the root top).
  * Slot C caster ring (N in [3, 8]): the **primary multiplicity axis**, count =
    ``len(positions)``. Each caster = ``caster_yoke_{i}`` (ALL FIXED rigid
    down-bracket, no kingpin) + ``caster_wheel_{i}`` (roll CONTINUOUS +Y through
    the wheel center; geometry per ``wheel_style``). Encoded into the slot_choice
    tuple as ``("caster_count", f"n{N}")``. Wheel appearance is the separate
    ``("wheel_style", <style>)`` slot_choice axis.
  * Slot C tier ring (N in [2, 6], conditional): active only for
    wire_mesh_shelf_stack; each ``shelf_{si}`` FIXED. Encoded as
    ``("tier_count", f"t{N}")``.

Compatibility (spec §9 / compatibility matrix):
  * full_cage_uprights REQUIRES wire_mesh_shelf_stack (the frame posts ARE the
    upright); on deck/tray/utility_wire_bin it degrades to tall_inverted_U_one_end.
  * utility_wire_bin has a planar top rim -> compatible with tall_inverted_U_one_end
    / handle_both_ends / folding_handle (NOT full_cage: no shelf frame posts).
  * tier_count is active only for wire_mesh_shelf_stack; deck/tray/bin fix
    their internal tiers by module.

All wheel-roll / hinge fits are captured geometry, so those
joints omit ``MatingContract`` (grandfathered, mechanical pivots) and are
guarded by the flat 0.015 m articulation-origin baseline plus element-scoped
``allow_overlap`` (mirroring each source's run_tests block). Tubular handle /
post frames use cadquery-swept tube meshes, the utility_wire_bin lattice uses
``tube_from_spline_points`` grid-loop wire meshes, and wheels use WheelGeometry /
TireGeometry meshes (no Box/Cylinder downgrade, Rule 3).
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
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    TireTread,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

LoadSurface = Literal[
    "flat_platform_deck",
    "stacked_open_trays",
    "wire_mesh_shelf_stack",
    "utility_wire_bin",
]
HandleUpright = Literal[
    "tall_inverted_U_one_end",
    "handle_both_ends",
    "full_cage_uprights",
    "folding_handle",
]
PaletteStyle = Literal[
    "warehouse_steel",
    "galvanized",
    "black_rollcage",
    "industrial_blue_wood",
]
# Wheel APPEARANCE axis (per-seed): 4 realistic cart/caster wheel types. The
# JOINT is identical (fixed mount + center roll) for every type; only the wheel
# geometry + material differ.
WheelStyle = Literal[
    "solid_rubber",
    "poly_hard",
    "pneumatic_tread",
    "cast_spoked",
]

LOAD_SURFACES: tuple[LoadSurface, ...] = (
    "flat_platform_deck",
    "stacked_open_trays",
    "wire_mesh_shelf_stack",
    "utility_wire_bin",
)
HANDLE_UPRIGHTS: tuple[HandleUpright, ...] = (
    "tall_inverted_U_one_end",
    "handle_both_ends",
    "full_cage_uprights",
    "folding_handle",
)
# Exactly 4 realistic colorways (spec §palette). The supermarket ``chrome_supermarket``
# colorway was removed with the supermarket seed (-> ``Caster Trolley2``).
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warehouse_steel",
    "galvanized",
    "black_rollcage",
    "industrial_blue_wood",
)

# --- Wheel-type appearance axis (spec §wheel_style). Joint is identical for all;
# only the wheel geometry (radius/width/tread/hub/spokes) + material change. ---
WHEEL_STYLES: tuple[WheelStyle, ...] = (
    "solid_rubber",
    "poly_hard",
    "cast_spoked",
)


@dataclass(frozen=True)
class _WheelStyleSpec:
    """Per-style wheel geometry knobs. ``kind`` selects the build path:
    ``"tire"`` = metal rim (WheelGeometry) + rubber tire (TireGeometry);
    ``"spoked"`` = a single cast-metal spoked/holed disc (WheelGeometry)."""
    kind: str  # "tire" | "spoked"
    r_factor: float  # radius multiplier on the base wheel_r
    w_factor: float  # width multiplier on the base wheel_w
    tread_style: str = "none"  # TireTread.style
    tread_depth: float = 0.0
    sidewall_bulge: float = 0.020
    hub_cap: str = "domed"  # WheelHub.cap_style
    spoke_style: str = "solid_slots"  # WheelSpokes.style (spoked kind only)
    spoke_count: int = 5


_WHEEL_STYLE_SPECS: dict[str, _WheelStyleSpec] = {
    # Smooth solid rubber tire on a metal hub, medium width, no tread.
    "solid_rubber": _WheelStyleSpec(
        kind="tire", r_factor=1.00, w_factor=1.00,
        tread_style="none", tread_depth=0.0, sidewall_bulge=0.020, hub_cap="domed",
    ),
    # Hard polyurethane/nylon wheel: narrower, lighter, slightly smaller, one
    # thin circumferential rib.
    "poly_hard": _WheelStyleSpec(
        kind="tire", r_factor=0.90, w_factor=0.72,
        tread_style="rib", tread_depth=0.0012, sidewall_bulge=0.006, hub_cap="domed",
    ),
    # Larger air-tire hand-truck wheel: wider, fatter sidewall, MODEST
    # circumferential tread (shallow — not deep off-road lugs).
    "pneumatic_tread": _WheelStyleSpec(
        kind="tire", r_factor=1.20, w_factor=1.35,
        tread_style="circumferential", tread_depth=0.0045, sidewall_bulge=0.032, hub_cap="domed",
    ),
    # Cast steel/iron wheel with a spoked/slotted (holed) disc, harder/darker.
    "cast_spoked": _WheelStyleSpec(
        kind="spoked", r_factor=1.00, w_factor=0.80,
        hub_cap="flat", spoke_style="straight", spoke_count=6,
    ),
}

# --- Caster ring multiplicity (primary axis, spec §axis 1). ---
# Weighted: 4 (standard 4-corner) highest; 3/6 common; 5/7/8 long tail.
N_CASTER_MIN, N_CASTER_MAX = 3, 8
_CASTER_COUNT_CHOICES = (3, 4, 5, 6, 7, 8)
_CASTER_COUNT_WEIGHTS = (0.18, 0.38, 0.08, 0.18, 0.09, 0.09)

# --- Shelf tier multiplicity (secondary axis, shelf only, spec §axis 2). ---
N_TIER_MIN, N_TIER_MAX = 2, 6
_TIER_COUNT_CHOICES = (2, 3, 4, 5, 6)
_TIER_COUNT_WEIGHTS = (0.12, 0.32, 0.32, 0.14, 0.10)

# full_cage requires the shelf frame; on deck/tray/utility_wire_bin it degrades
# to tall_inverted_U_one_end. (No basket-specific handle exclusion: the removed
# supermarket ``low_basket_handle`` push-bar / ``_BASKET_FORBIDDEN_HANDLES`` gate
# left with the supermarket seed. The utility_wire_bin has a planar rim so
# folding_handle is fine on it.)
_SHELF_ONLY_HANDLES: tuple[HandleUpright, ...] = ("full_cage_uprights",)

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Spec defaults: ~0.85 long, ~0.52 wide,
# deck ~0.16 above the floor on the casters.
# ---------------------------------------------------------------------------
_DECK_LEN = 0.840  # root length (X)
_DECK_WID = 0.520  # root width (Y)
_DECK_T = 0.026  # deck slab thickness
_DECK_LIP = 0.024  # rolled edge lip height

# Caster geometry.
_WHEEL_R = 0.052
_WHEEL_W = 0.034
# Metal-rim (WheelGeometry) fixed width + hub width. Kept independent of the
# per-style tire width so the rim disc/hub never splits into a disconnected mesh
# component (island); only the TIRE width varies with wheel_style.
_RIM_WIDTH = 0.0234
_RIM_HUB_WIDTH = 0.017
_FORK_DROP = 0.0  # ZERO trail: kingpin/pivot axis passes through the wheel center
#                  so a swivel caster pivots the wheel in place (normal centered
#                  wheel) instead of orbiting the wheel around an offset kingpin.
_CLEARANCE = 0.012  # gap between wheel top and the root underside
_CASTER_INSET = 0.090  # inset of caster positions from the footprint edge

# Handle geometry.
_HANDLE_TUBE_R = 0.014
_HANDLE_RISE = 0.620  # grip height above the deck top
_HANDLE_REACH = 0.090

# Tray / shelf.
_TRAY_GAP = 0.150  # vertical gap between stacked trays
_TRAY_WALL = 0.010
_TRAY_LIP = 0.040
_SHELF_FRAME_H = 0.860  # shelf-stack post height
_SHELF_T = 0.010

# Utility wire bin (straight-walled RECTANGULAR warehouse wire cage on a tubular
# chassis — NOT a tapered supermarket basket; walls vertical, footprint constant
# in Z). Adapted from rec_caster_trolley_var_deck_to_basket.
_BIN_FRAME_SEC = 0.030  # rectangular chassis-frame tube section (square)
_BIN_HEIGHT = 0.300  # bin wall height (Z), walls straight & vertical
_BIN_INSET = 0.018  # bin footprint inset from the frame edge
_BIN_WIRE_R = 0.0026  # mesh wire radius
_BIN_WIRE_SPACING = 0.070  # ~70 mm lattice grid pitch (coarsened for compile cost)
_BIN_RIM_R = 0.006  # top rim rail tube radius

_FOLD_OPEN = 1.50  # folding-handle hinge upper limit (rad)


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class CasterTrolleyConfig:
    load_surface: LoadSurface | None = None
    handle_upright: HandleUpright | None = None
    caster_count: int | None = None
    tier_count: int | None = None
    palette_style: PaletteStyle = "warehouse_steel"
    wheel_style: WheelStyle = "solid_rubber"
    deck_len_scale: float = 1.0
    deck_wid_scale: float = 1.0
    handle_height_scale: float = 1.0
    wheel_radius_scale: float = 1.0
    name: str = "caster_trolley"


@dataclass(frozen=True)
class ResolvedCasterTrolleyConfig:
    load_surface: LoadSurface
    handle_upright: HandleUpright
    caster_count: int
    tier_count: int  # meaningful only for wire_mesh_shelf_stack
    palette_style: PaletteStyle
    wheel_style: WheelStyle
    # Derived / scaled geometry.
    deck_len: float
    deck_wid: float
    wheel_r: float
    wheel_w: float
    deck_bottom_z: float  # root underside height above the floor (= 2*wheel_r + clearance)
    caster_inset: float
    handle_rise: float
    name: str

    @property
    def deck_top_z(self) -> float:
        return self.deck_bottom_z + _DECK_T


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CasterTrolleyConfig:
    rng = random.Random(seed)
    load_surface = rng.choice(LOAD_SURFACES)
    handle = rng.choice(HANDLE_UPRIGHTS)
    caster_count = rng.choices(_CASTER_COUNT_CHOICES, weights=_CASTER_COUNT_WEIGHTS, k=1)[0]
    tier_count = rng.choices(_TIER_COUNT_CHOICES, weights=_TIER_COUNT_WEIGHTS, k=1)[0]
    wheel_style = rng.choice(WHEEL_STYLES)
    return CasterTrolleyConfig(
        load_surface=load_surface,
        handle_upright=handle,
        caster_count=caster_count,
        tier_count=tier_count,
        palette_style=rng.choice(PALETTE_STYLES),
        wheel_style=wheel_style,
        deck_len_scale=round(rng.uniform(0.85, 1.15), 4),
        deck_wid_scale=round(rng.uniform(0.85, 1.15), 4),
        handle_height_scale=round(rng.uniform(0.85, 1.20), 4),
        wheel_radius_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_caster_trolley_{seed}",
    )


def resolve_config(
    config: CasterTrolleyConfig | None = None,
) -> ResolvedCasterTrolleyConfig:
    cfg = config or CasterTrolleyConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    load_surface = _pick(cfg.load_surface, LOAD_SURFACES)
    handle = _pick(cfg.handle_upright, HANDLE_UPRIGHTS)
    wheel_style = _pick(cfg.wheel_style, WHEEL_STYLES)

    # --- Compatibility gating (spec §9). ---
    # full_cage requires the shelf frame; on deck/tray/utility_wire_bin it degrades.
    # (utility_wire_bin keeps folding_handle: it has a planar top rim to hinge on.)
    if handle in _SHELF_ONLY_HANDLES and load_surface != "wire_mesh_shelf_stack":
        handle = "tall_inverted_U_one_end"

    # --- caster_count: clamp. ---
    caster_count = int(cfg.caster_count) if cfg.caster_count is not None else 4
    caster_count = int(_clamp(caster_count, N_CASTER_MIN, N_CASTER_MAX))

    # --- tier_count: clamp; fixed by module for non-shelf surfaces. ---
    tier_count = int(cfg.tier_count) if cfg.tier_count is not None else 4
    tier_count = int(_clamp(tier_count, N_TIER_MIN, N_TIER_MAX))
    if load_surface != "wire_mesh_shelf_stack":
        tier_count = 0  # not exposed; internal tiers are module-fixed

    # --- continuous scales. ---
    len_scale = _clamp(cfg.deck_len_scale, 0.85, 1.15)
    wid_scale = _clamp(cfg.deck_wid_scale, 0.85, 1.15)
    h_scale = _clamp(cfg.handle_height_scale, 0.85, 1.20)
    wr_scale = _clamp(cfg.wheel_radius_scale, 0.85, 1.20)

    deck_len = _DECK_LEN * len_scale
    deck_wid = _DECK_WID * wid_scale
    # Wheel geometry scaled by the chosen wheel_style (radius/width factors) so the
    # different wheel TYPES read as different sizes; the joint stays identical.
    wstyle = _WHEEL_STYLE_SPECS[wheel_style]
    wheel_r = _WHEEL_R * wr_scale * wstyle.r_factor
    wheel_w = _WHEEL_W * wstyle.w_factor

    # deck_bottom_z derived so the root rides above the wheels (spec equation).
    # Recomputed per style radius so every wheel type still lands at ground z~=0.
    deck_bottom_z = 2.0 * wheel_r + _CLEARANCE

    # caster_inset kept so positions stay inside the footprint.
    caster_inset = min(_CASTER_INSET, 0.30 * deck_len, 0.30 * deck_wid)

    handle_rise = _HANDLE_RISE * h_scale

    return ResolvedCasterTrolleyConfig(
        load_surface=load_surface,
        handle_upright=handle,
        caster_count=caster_count,
        tier_count=tier_count,
        palette_style=palette_style,
        wheel_style=wheel_style,
        deck_len=deck_len,
        deck_wid=deck_wid,
        wheel_r=wheel_r,
        wheel_w=wheel_w,
        deck_bottom_z=deck_bottom_z,
        caster_inset=caster_inset,
        handle_rise=handle_rise,
        name=cfg.name or "caster_trolley",
    )


def with_overrides(config: CasterTrolleyConfig, **kwargs: object) -> CasterTrolleyConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CasterTrolleyConfig | ResolvedCasterTrolleyConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCasterTrolleyConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("load_surface", r.load_surface),
        ("handle_upright", r.handle_upright),
        ("caster_count", f"n{r.caster_count}"),
        ("wheel_style", r.wheel_style),
    ]
    if r.load_surface == "wire_mesh_shelf_stack":
        choices.append(("tier_count", f"t{r.tier_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Caster positions (count = len(positions); spec §axis 1 placement).
# ===========================================================================
def _caster_positions(r: ResolvedCasterTrolleyConfig) -> list[tuple[float, float]]:
    """Return N (cx, cy) kingpin positions on the root underside, all inside the
    footprint. N=4 -> 4 corners; N=3 -> handle-end pair + 1 central rear; N=6 ->
    front/mid/rear pairs; generic even N -> M pairs along X; generic odd N ->
    pairs + 1 centerline rear."""
    n = r.caster_count
    hx = r.deck_len / 2.0 - r.caster_inset
    hy = r.deck_wid / 2.0 - r.caster_inset

    if n == 3:
        return [(hx, hy), (hx, -hy), (-hx, 0.0)]
    if n == 4:
        return [(sx * hx, sy * hy) for sx in (1.0, -1.0) for sy in (1.0, -1.0)]

    pairs = n // 2
    odd = n % 2 == 1
    xs = [hx - (2.0 * hx) * (k / (pairs - 1)) for k in range(pairs)] if pairs > 1 else [0.0]
    positions: list[tuple[float, float]] = []
    for x in xs:
        positions.append((x, hy))
        positions.append((x, -hy))
    if odd:
        # Extra centerline caster placed in the GAP between the first two pair
        # rows (not on a pair-row X): a caster sharing a corner pair's X would let
        # its swiveling wheel sweep into the corner wheel (large-wheel/narrow-deck
        # seeds). At y=0, midway between rows, it clears every neighbor.
        mid_x = (xs[0] + xs[1]) / 2.0 if pairs >= 2 else 0.0
        positions.append((mid_x, 0.0))
    return positions[:n]


# ===========================================================================
# Caster geometry (shared across all Slot A surfaces).
# ===========================================================================
def _fork_visuals(r: ResolvedCasterTrolleyConfig):
    """RIGID caster yoke (no swivel): top mount plate + short stem + centered
    crown above the wheel, plus the two side fork legs and a slim axle pin.
    Zero trail (_FORK_DROP=0) so the axle sits directly under the mount and the
    wheel rolls about its own center. Authored in the fork-local frame: mount
    plate at the top (z=0 region), wheel axle at (-fork_drop, 0, axle_z) with
    fork_drop=0 (so the roll-joint origin passes through the wheel center).
    The yoke deliberately leaves the wheel envelope open; only the axle pin runs
    through the wheel bore."""
    axle_z = -r.deck_bottom_z + r.wheel_r  # so wheel bottom lands at world z~0
    leg_x = -_FORK_DROP
    wheel_top_z = axle_z + r.wheel_r
    leg_t = 0.010
    side_gap = 0.006
    half_w = r.wheel_w / 2.0 + side_gap + leg_t / 2.0

    crown_h = 0.006
    crown_z = wheel_top_z + side_gap + crown_h / 2.0
    crown_span_y = 2.0 * half_w + leg_t

    # Short neck from the plate down to the crown. It stops above the wheel top,
    # avoiding the previous center strut that pierced the rolling wheel.
    neck_top = -0.008
    neck_bot = crown_z + crown_h / 2.0
    leg_top = crown_z
    leg_bot = axle_z - 0.018

    # Axle pin through the wheel bore. Match WheelGeometry's default bore radius
    # for the active wheel style so the wheel is physically captured without the
    # fork body entering the rolling tire/rim volume.
    wheel_geom_r = (
        r.wheel_r
        if _WHEEL_STYLE_SPECS[r.wheel_style].kind == "spoked"
        else r.wheel_r - 0.010
    )
    axle_pin_r = max(wheel_geom_r * 0.18, 0.004) * 0.5
    return [
        (Box((0.060, 0.060, 0.008)), Origin(xyz=(0.0, 0.0, -0.004)), "mount_plate"),
        (Cylinder(radius=0.012, length=0.034), Origin(xyz=(0.0, 0.0, 0.009)), "mount_boss"),
        (Box((0.040, crown_span_y, crown_h)), Origin(xyz=(leg_x, 0.0, crown_z)), "top_crown"),
        (
            Box((0.026, 0.032, abs(neck_top - neck_bot))),
            Origin(xyz=(leg_x, 0.0, (neck_top + neck_bot) / 2.0)),
            "upper_neck",
        ),
        (
            Box((0.034, leg_t, abs(leg_top - leg_bot))),
            Origin(xyz=(leg_x, half_w, (leg_top + leg_bot) / 2.0)),
            "fork_leg_pos",
        ),
        (
            Box((0.034, leg_t, abs(leg_top - leg_bot))),
            Origin(xyz=(leg_x, -half_w, (leg_top + leg_bot) / 2.0)),
            "fork_leg_neg",
        ),
        (
            Cylinder(radius=axle_pin_r, length=crown_span_y),
            Origin(xyz=(leg_x, 0.0, axle_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            "axle_pin",
        ),
    ]


def _wheel_visuals(r: ResolvedCasterTrolleyConfig, mats, assets):
    """Build the wheel visuals for the chosen ``wheel_style``. Returns a list of
    ``(mesh, material, name)`` tuples applied to the ``caster_wheel_{i}`` part.
    No Box/Cylinder downgrade (Rule 3).

      * tire styles (solid_rubber / poly_hard / pneumatic_tread): a metal rim
        (WheelGeometry) + a rubber tire (TireGeometry) whose tread/width/sidewall
        follow the style spec.
      * spoked style (cast_spoked): a single cast-metal spoked/slotted disc
        (WheelGeometry with WheelSpokes) — no rubber tire."""
    spec = _WHEEL_STYLE_SPECS[r.wheel_style]
    if spec.kind == "spoked":
        wheel = WheelGeometry(
            r.wheel_r,
            r.wheel_w,
            rim=WheelRim(flange_height=0.003, flange_thickness=0.0025),
            hub=WheelHub(radius=max(r.wheel_r * 0.20, 0.010), width=r.wheel_w * 0.60, cap_style=spec.hub_cap),
            # window_radius=0 -> use the module's safe default slot width (a large
            # explicit window makes the slot cutters degenerate -> BRep failure);
            # a set disc thickness keeps the spoked disc solid.
            spokes=WheelSpokes(
                style=spec.spoke_style, count=spec.spoke_count,
                window_radius=0.0, thickness=r.wheel_w * 0.35,
            ),
            center=True,
        )
        return [(mesh_from_geometry(wheel, "spoked_wheel"), mats["wheel_metal"], "spoked_wheel")]

    # Metal rim/hub: FIXED width (radius still scales with the wheel). A rim whose
    # WIDTH tracks a very wide or very narrow tire makes the WheelGeometry disc/hub
    # split into a disconnected mesh component (island) that the tire fails to
    # bridge; a fixed proven-good width (domed hub) stays a single connected body
    # for every tire width/radius. The tire (below) carries the style width.
    rim = WheelGeometry(
        r.wheel_r - 0.010,
        _RIM_WIDTH,
        rim=WheelRim(flange_height=0.004, flange_thickness=0.003),
        hub=WheelHub(radius=0.012, width=_RIM_HUB_WIDTH, cap_style="domed"),
        center=True,
    )
    rim_mesh = mesh_from_geometry(rim, "caster_rim")
    tire = TireGeometry(
        r.wheel_r,
        r.wheel_w,
        inner_radius=r.wheel_r - 0.012,
        carcass=TireCarcass(belt_width_ratio=0.72, sidewall_bulge=spec.sidewall_bulge),
        tread=(
            TireTread(style="none")
            if spec.tread_style == "none"
            else TireTread(style=spec.tread_style, depth=spec.tread_depth)
        ),
        sidewall=TireSidewall(style="rounded", bulge=spec.sidewall_bulge),
        shoulder=TireShoulder(width=0.005, radius=0.003),
    )
    tire_mesh = mesh_from_geometry(tire, "caster_tire")
    return [
        (rim_mesh, mats["wheel_rim"], "rim"),
        (tire_mesh, mats["wheel_surface"], "tire"),
    ]


def _build_casters(model, r, mats, root, *, assets) -> None:
    """Emit N ALL-RIGID casters (per the user's final decision — NO swivels).
    Each caster = ``caster_yoke_{i}`` on a FIXED rigid down-bracket mount (no
    kingpin) + ``caster_wheel_{i}`` that rolls CONTINUOUS about its transverse Y
    axle through the wheel center. Uniform joint config across all casters and
    seeds; only the wheel GEOMETRY varies with ``wheel_style``."""
    fork_visuals = _fork_visuals(r)
    wheel_visuals = _wheel_visuals(r, mats, assets)
    axle_z = -r.deck_bottom_z + r.wheel_r
    leg_x = -_FORK_DROP  # 0.0 -> axle (and roll-joint origin) under the mount center
    for i, (cx, cy) in enumerate(_caster_positions(r)):
        fork = model.part(f"caster_yoke_{i}")
        for geometry, origin, suffix in fork_visuals:
            fork.visual(geometry, origin=origin, material=mats["accent"], name=f"{suffix}_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"))
        fork.inertial = Inertial.from_geometry(
            Box((0.06, 0.06, r.deck_bottom_z)),
            mass=0.4,
            origin=Origin(xyz=(leg_x / 2.0, 0.0, -r.deck_bottom_z / 2.0)),
        )
        wheel = model.part(f"caster_wheel_{i}")
        # WheelGeometry/TireGeometry are authored with their axle along local X;
        # rotate about Z so local +X aligns with the roll joint's transverse +Y.
        for mesh, material, suffix in wheel_visuals:
            wheel.visual(
                mesh,
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, math.pi / 2.0)),
                material=material,
                name=f"{suffix}_{i}", material_class_id=("metal.cast_iron_bare" if r.wheel_style in {"solid_rubber", "pneumatic_tread", "cast_spoked"} else "plastic.opaque_glossy_molded"),
            )
        wheel.inertial = Inertial.from_geometry(
            Box((2 * r.wheel_r, r.wheel_w, 2 * r.wheel_r)),
            mass=0.5,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        # Yoke mount: root underside -> yoke, RIGID (FIXED) for EVERY caster.
        # No kingpin / swivel joint anywhere.
        model.articulation(
            f"{root.name}_to_caster_yoke_{i}",
            ArticulationType.FIXED,
            parent=root,
            child=fork,
            origin=Origin(xyz=(cx, cy, r.deck_bottom_z)),
        )
        # Roll: yoke -> wheel, CONTINUOUS about transverse Y through the wheel
        # center (leg_x=0 -> origin X=0 = center). DEFINING MOTION.
        model.articulation(
            f"caster_spin_{i}",
            ArticulationType.CONTINUOUS,
            parent=fork,
            child=wheel,
            origin=Origin(xyz=(leg_x, 0.0, axle_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=20.0),
        )


# ===========================================================================
# Tubular handle helpers (cadquery swept tubes — no Cylinder downgrade).
# ===========================================================================
def _swept_tube(pts, radius, name, assets):
    """Sweep a circular profile of `radius` along the spline through `pts`."""
    wire_pts = [cq.Vector(*p) for p in pts]
    spline_edge = cq.Edge.makeSpline(wire_pts)
    wire = cq.Wire.assembleEdges([spline_edge])
    start = wire_pts[0]
    tan = spline_edge.tangentAt(0.0)
    tube = (
        cq.Workplane(cq.Plane(origin=start.toTuple(), normal=tan.toTuple()))
        .circle(radius)
        .sweep(cq.Workplane(obj=wire), transition="round")
    )
    return tube


def _inverted_u_tube(r, *, rise, name, assets, cross_rails=2):
    """An inverted-U push handle authored in the HANDLE-LOCAL frame: the +Y
    upright foot sits at the part origin (0, +half, 0); both uprights rise in +Z,
    bow over to a grip at the top. (0,0,0) lies on the +Y mount boss so the
    FIXED-joint origin is on real handle geometry. Returns mesh."""
    half = r.deck_wid / 2.0 - 0.040
    z_top = rise
    pts = [
        (0.0, half, 0.0),
        (0.0, half, 0.55 * rise),
        (0.0, 0.0, z_top),  # grip center top
        (0.0, -half, 0.55 * rise),
        (0.0, -half, 0.0),
    ]
    tube = _swept_tube(pts, _HANDLE_TUBE_R, name, assets)
    # Mount bosses where each upright meets the deck top (and at the origin).
    for sy in (half, -half):
        boss = (
            cq.Workplane("XY", origin=(0.0, sy, 0.010))
            .circle(_HANDLE_TUBE_R + 0.005)
            .extrude(0.026, both=True)
        )
        tube = tube.union(boss)
    # Foot rail tying the two uprights along the mount line so handle-local
    # (0,0,0) lies on real geometry (joint-origin baseline + isolation contact).
    # Extends just past each upright so it solidly fuses both feet into one body.
    foot = cq.Workplane("XZ", origin=(0.0, 0.0, _HANDLE_TUBE_R)).circle(
        _HANDLE_TUBE_R
    ).extrude(half + 0.012, both=True)
    tube = tube.union(foot)
    # Ladder cross rails between the uprights. Built as boxes (reliable fusion;
    # thin cylinders tangentially touching the legs can fail the boolean and
    # leave a disconnected island). Each spans just past both legs.
    # The spline legs bulge outward (up to ~half+0.05) between control points, so
    # the rails must span well past `half` to always cross the leg tubes.
    for k in range(cross_rails):
        frac = 0.22 + 0.24 * (k / max(1, cross_rails - 1)) if cross_rails > 1 else 0.34
        rz = frac * rise
        rail = cq.Workplane("XY", origin=(0.0, 0.0, rz)).box(
            2.2 * _HANDLE_TUBE_R, 2.0 * (half + 0.060), 1.6 * _HANDLE_TUBE_R
        )
        tube = tube.union(rail)
    return mesh_from_cadquery(tube, name, assets=assets)


# ===========================================================================
# Slot A: load surfaces (root part).
# ===========================================================================
def _deck_mesh(r: ResolvedCasterTrolleyConfig, assets):
    """Flat platform deck: a slab + rolled-edge lips around the perimeter."""
    z0 = r.deck_bottom_z
    slab = cq.Workplane("XY", origin=(0, 0, z0 + _DECK_T / 2.0)).box(
        r.deck_len, r.deck_wid, _DECK_T
    )
    try:
        slab = slab.edges("|Z").fillet(0.012)
    except Exception:
        pass
    # Rolled edge lip around the perimeter.
    lip_outer = cq.Workplane("XY", origin=(0, 0, z0 + _DECK_T + _DECK_LIP / 2.0)).box(
        r.deck_len, r.deck_wid, _DECK_LIP
    )
    lip_inner = cq.Workplane("XY", origin=(0, 0, z0 + _DECK_T + _DECK_LIP / 2.0 + 0.001)).box(
        r.deck_len - 2 * 0.018, r.deck_wid - 2 * 0.018, _DECK_LIP + 0.004
    )
    lip = lip_outer.cut(lip_inner)
    return mesh_from_cadquery(slab.union(lip), "deck_slab", assets=assets)


def _build_flat_platform_deck(model, r, mats, *, assets):
    root = model.part("load_surface")
    root.visual(_deck_mesh(r, assets), material=mats["deck"], name="deck_slab", material_class_id=("metal.paint_coated" if r.palette_style in {"warehouse_steel", "galvanized", "black_rollcage"} else "wood.natural_generic"))
    root.inertial = Inertial.from_geometry(
        Box((r.deck_len, r.deck_wid, _DECK_T + _DECK_LIP)),
        mass=14.0,
        origin=Origin(xyz=(0.0, 0.0, r.deck_bottom_z + _DECK_T)),
    )
    return root


def _tray_mesh(r: ResolvedCasterTrolleyConfig, assets, *, z_base, name):
    """A shallow tray pan: floor + 4 raised lips, as one fused solid."""
    pan_l = r.deck_len
    pan_w = r.deck_wid
    floor = cq.Workplane("XY", origin=(0, 0, z_base + _TRAY_WALL / 2.0)).box(
        pan_l, pan_w, _TRAY_WALL
    )
    lip_outer = cq.Workplane("XY", origin=(0, 0, z_base + _TRAY_LIP / 2.0)).box(
        pan_l, pan_w, _TRAY_LIP
    )
    lip_inner = cq.Workplane("XY", origin=(0, 0, z_base + _TRAY_LIP / 2.0 + _TRAY_WALL)).box(
        pan_l - 2 * _TRAY_WALL, pan_w - 2 * _TRAY_WALL, _TRAY_LIP
    )
    pan = floor.union(lip_outer.cut(lip_inner))
    try:
        pan = pan.edges("|Z").fillet(0.010)
    except Exception:
        pass
    return mesh_from_cadquery(pan, name, assets=assets)


# Corner-leg footprint inset (legs sit just inside the tray lip so the post
# overlaps the lip wall and fuses into the pan).
_TRAY_LEG_INSET = 0.026
_TRAY_LEG_R = 0.013


def _tray_leg_xy(r: ResolvedCasterTrolleyConfig) -> list[tuple[float, float]]:
    hx = r.deck_len / 2.0 - _TRAY_LEG_INSET
    hy = r.deck_wid / 2.0 - _TRAY_LEG_INSET
    return [(sx * hx, sy * hy) for sx in (-1.0, 1.0) for sy in (-1.0, 1.0)]


def _tray_frame_mesh(r: ResolvedCasterTrolleyConfig, assets, *, z_base, z_top, name):
    """Lower-tray module emitted as ONE fused solid: pan floor + 4 lips + 4
    corner posts rising from inside the pan to ``z_top`` + a top perimeter rail
    tying all four post tops. Posts are inset so they overlap the pan lips, and
    they extend down to the pan floor, so every sub-feature shares solid material
    -> no disconnected geometry island inside the root part."""
    pan_l = r.deck_len
    pan_w = r.deck_wid
    # Pan floor + raised perimeter lip (shallow tray).
    floor = cq.Workplane("XY", origin=(0, 0, z_base + _TRAY_WALL / 2.0)).box(
        pan_l, pan_w, _TRAY_WALL
    )
    lip_outer = cq.Workplane("XY", origin=(0, 0, z_base + _TRAY_LIP / 2.0)).box(
        pan_l, pan_w, _TRAY_LIP
    )
    lip_inner = cq.Workplane("XY", origin=(0, 0, z_base + _TRAY_LIP / 2.0 + _TRAY_WALL)).box(
        pan_l - 2 * _TRAY_WALL, pan_w - 2 * _TRAY_WALL, _TRAY_LIP
    )
    result = floor.union(lip_outer.cut(lip_inner))
    # Corner posts: penetrate the FULL floor slab (start below z_base) and rise to
    # the upper-tray level. The large square-section overlap with the solid floor
    # box guarantees a robust boolean weld (thin tangential overlaps can split the
    # union into separate shells -> disconnected islands).
    post_z0 = z_base  # from the floor underside up; spans the full floor thickness
    post_z1 = z_top
    legs = _tray_leg_xy(r)
    for cx, cy in legs:
        post = (
            cq.Workplane("XY", origin=(cx, cy, (post_z0 + post_z1) / 2.0))
            .box(2.0 * _TRAY_LEG_R, 2.0 * _TRAY_LEG_R, post_z1 - post_z0)
        )
        result = result.union(post)
    # Top perimeter rail connecting the four post tops. Centered ON the post-top
    # centers (full overlap with each post box) so every post is fused into the
    # one body up top even if a floor weld were marginal.
    hx = r.deck_len / 2.0 - _TRAY_LEG_INSET
    hy = r.deck_wid / 2.0 - _TRAY_LEG_INSET
    rail_z = z_top - _TRAY_LEG_R
    rail_t = 0.016
    # Two rails along X (front/back) + two along Y, built as overlapping boxes that
    # bridge post-to-post; each spans past both posts so it solidly intersects them.
    for sy in (-hy, hy):
        result = result.union(
            cq.Workplane("XY", origin=(0.0, sy, rail_z)).box(
                2.0 * hx + 2.0 * _TRAY_LEG_R, rail_t, rail_t
            )
        )
    for sx in (-hx, hx):
        result = result.union(
            cq.Workplane("XY", origin=(sx, 0.0, rail_z)).box(
                rail_t, 2.0 * hy + 2.0 * _TRAY_LEG_R, rail_t
            )
        )
    return mesh_from_cadquery(result, name, assets=assets)


def _build_stacked_open_trays(model, r, mats, *, assets):
    root = model.part("load_surface")
    z_lower = r.deck_bottom_z
    z_upper = z_lower + _TRAY_GAP
    # Lower pan + corner posts + top rail emitted as ONE fused solid so the root
    # part is a single connected body (no floating pan / disconnected legs).
    root.visual(
        _tray_frame_mesh(
            r, assets, z_base=z_lower, z_top=z_upper + _TRAY_WALL, name="lower_tray_frame"
        ),
        material=mats["deck"],
        name="lower_tray", material_class_id=("metal.paint_coated" if r.palette_style in {"warehouse_steel", "galvanized", "black_rollcage"} else "wood.natural_generic"),
    )
    root.inertial = Inertial.from_geometry(
        Box((r.deck_len, r.deck_wid, z_upper + _TRAY_LIP - z_lower)),
        mass=12.0,
        origin=Origin(xyz=(0.0, 0.0, (z_lower + z_upper) / 2.0 + _TRAY_LIP)),
    )
    # Upper tray = FIXED child (separate ref frame; spec lower_to_upper FIXED).
    # The upper tray carries its OWN short corner stubs that drop down onto the
    # lower-tray post tops, so the child part is self-connected AND the FIXED
    # joint origin (on a post top) sits within tol of both bodies' geometry.
    upper = model.part("upper_tray")
    upper.visual(
        _upper_tray_mesh(r, assets, name="upper_tray"),
        material=mats["deck"],
        name="upper_tray", material_class_id=("metal.paint_coated" if r.palette_style in {"warehouse_steel", "galvanized", "black_rollcage"} else "wood.natural_generic"),
    )
    upper.inertial = Inertial.from_geometry(
        Box((r.deck_len, r.deck_wid, _TRAY_LIP + 0.024)),
        mass=4.0,
        origin=Origin(xyz=(0.0, 0.0, _TRAY_LIP / 2.0)),
    )
    # Anchor on a corner post top: the lower-tray post (parent) spans up through
    # z_upper at this (cx, cy), and the upper-tray corner stub (child) is centered
    # on the same (cx, cy) about its own z=0, so the FIXED-joint origin sits within
    # tol of real geometry on BOTH sides.
    leg_x, leg_y = _tray_leg_xy(r)[-1]  # one corner (+x, +y)
    model.articulation(
        "lower_to_upper",
        ArticulationType.FIXED,
        parent=root,
        child=upper,
        origin=Origin(xyz=(leg_x, leg_y, z_upper)),
    )
    return root


def _upper_tray_mesh(r: ResolvedCasterTrolleyConfig, assets, *, name):
    """Upper tray pan authored in the child-local frame (origin at z=0 = the
    upper-tray seating plane). The pan floor sits at the origin plane and short
    corner stubs drop a touch below it so the FIXED-joint origin (z=0) lands on
    solid child geometry that also overlaps the lower-tray post tops."""
    pan_l = r.deck_len
    pan_w = r.deck_wid
    # Corner-anchor shift: the FIXED joint mounts this child at the (+x,+y) corner
    # post, which puts the child's LOCAL (0,0,0) on that world corner. Offsetting
    # all geometry by (-mx,-my) makes the (+,+) stub land at local (0,0) (on the
    # mounted post -> child_distance≈0) while the pan CENTER lands at local
    # (-mx,-my) so it renders at world (0,0) = frame center (not cantilevered).
    mx, my = _tray_leg_xy(r)[-1]  # (+hx, +hy) mount corner
    floor = cq.Workplane("XY", origin=(-mx, -my, _TRAY_WALL / 2.0)).box(
        pan_l, pan_w, _TRAY_WALL
    )
    lip_outer = cq.Workplane("XY", origin=(-mx, -my, _TRAY_LIP / 2.0)).box(
        pan_l, pan_w, _TRAY_LIP
    )
    lip_inner = cq.Workplane("XY", origin=(-mx, -my, _TRAY_LIP / 2.0 + _TRAY_WALL)).box(
        pan_l - 2 * _TRAY_WALL, pan_w - 2 * _TRAY_WALL, _TRAY_LIP
    )
    result = floor.union(lip_outer.cut(lip_inner))
    # Corner stubs hanging below the pan floor onto the lower-tray post tops, so
    # the child geometry straddles its z=0 mount plane (origin baseline) and
    # overlaps the supporting posts. Shifted by (-mx,-my) so the (+,+) stub sits
    # at local (0,0) and the other 3 land on the other 3 posts.
    for cx, cy in _tray_leg_xy(r):
        stub = (
            cq.Workplane("XY", origin=(cx - mx, cy - my, -0.010))
            .circle(_TRAY_LEG_R)
            .extrude(0.024)
        )
        result = result.union(stub)
    return mesh_from_cadquery(result, name, assets=assets)


_SHELF_POST_R = 0.014  # half-section of the (square) corner post
_SHELF_RAIL_T = 0.016  # perimeter-rail section


def _shelf_frame_mesh(r: ResolvedCasterTrolleyConfig, assets):
    """Tall frame emitted as ONE fused solid: a base plate + 4 corner posts +
    top/mid/bottom perimeter rails. Posts and rails are box sections with strong
    volumetric overlap (post centers lie ON the rail lines, posts penetrate the
    base plate), so the whole frame is a single connected body — thin tangential
    cylinder unions split into disconnected islands."""
    hx = r.deck_len / 2.0 - 0.030
    hy = r.deck_wid / 2.0 - 0.030
    z0 = r.deck_bottom_z
    z1 = z0 + _SHELF_FRAME_H
    # Base plate (the posts will penetrate into it).
    result = cq.Workplane("XY", origin=(0, 0, z0 + 0.004)).box(
        2 * hx + 0.020, 2 * hy + 0.020, 0.012
    )
    corners = [(-hx, -hy), (-hx, hy), (hx, hy), (hx, -hy)]
    for cx, cy in corners:
        post = cq.Workplane("XY", origin=(cx, cy, (z0 + z1) / 2.0)).box(
            2.0 * _SHELF_POST_R, 2.0 * _SHELF_POST_R, z1 - z0
        )
        result = result.union(post)
    # Perimeter rails at several heights; each rail is a box centered on a post
    # line, spanning past both posts so it fully overlaps them.
    for z_bar in (z0 + 0.040, z0 + _SHELF_FRAME_H / 2.0, z1 - 0.010):
        for sy in (-hy, hy):
            result = result.union(
                cq.Workplane("XY", origin=(0.0, sy, z_bar)).box(
                    2.0 * hx + 2.0 * _SHELF_POST_R, _SHELF_RAIL_T, _SHELF_RAIL_T
                )
            )
        for sx in (-hx, hx):
            result = result.union(
                cq.Workplane("XY", origin=(sx, 0.0, z_bar)).box(
                    _SHELF_RAIL_T, 2.0 * hy + 2.0 * _SHELF_POST_R, _SHELF_RAIL_T
                )
            )
    return mesh_from_cadquery(result, "shelf_frame", assets=assets)


def _shelf_pan_mesh(r: ResolvedCasterTrolleyConfig, assets):
    """One wire-mesh shelf pan: a thin plate + a rear lip.

    Corner-anchor shift: every shelf FIXED-joint mounts at the SAME (post_x,post_y)
    corner (different z), which lands the child LOCAL (0,0,0) on that world corner.
    Offsetting the pan by (-post_x,-post_y) puts its local origin on the mount
    corner (child_distance small) and renders the pan CENTERED on the frame."""
    hx = r.deck_len / 2.0 - 0.034
    hy = r.deck_wid / 2.0 - 0.034
    post_x = r.deck_len / 2.0 - 0.030
    post_y = r.deck_wid / 2.0 - 0.030
    plate = cq.Workplane("XY", origin=(-post_x, -post_y, _SHELF_T / 2.0)).box(
        2 * hx, 2 * hy, _SHELF_T
    )
    lip = cq.Workplane("XY", origin=(-post_x, -hy + 0.006 - post_y, _SHELF_T + 0.010)).box(
        2 * hx, 0.012, 0.024
    )
    return mesh_from_cadquery(plate.union(lip), "shelf_pan", assets=assets)


def _build_wire_mesh_shelf_stack(model, r, mats, *, assets):
    root = model.part("load_surface")
    root.visual(_shelf_frame_mesh(r, assets), material=mats["accent"], name="shelf_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"))
    root.inertial = Inertial.from_geometry(
        Box((r.deck_len, r.deck_wid, _SHELF_FRAME_H)),
        mass=16.0,
        origin=Origin(xyz=(0.0, 0.0, r.deck_bottom_z + _SHELF_FRAME_H / 2.0)),
    )
    # N shelves as FIXED children, evenly spaced between base and top.
    n = r.tier_count
    shelf_mesh = _shelf_pan_mesh(r, assets)
    z0 = r.deck_bottom_z + 0.040
    z1 = r.deck_bottom_z + _SHELF_FRAME_H - 0.040
    for si in range(n):
        frac = si / max(1, n - 1) if n > 1 else 0.0
        sz = z0 + frac * (z1 - z0)
        shelf = model.part(f"shelf_{si}")
        shelf.visual(shelf_mesh, material=mats["deck"], name=f"shelf_pan_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"warehouse_steel", "galvanized", "black_rollcage"} else "wood.natural_generic"))
        shelf.inertial = Inertial.from_geometry(
            Box((r.deck_len - 0.06, r.deck_wid - 0.06, _SHELF_T)),
            mass=2.0,
            origin=Origin(xyz=(0.0, 0.0, _SHELF_T / 2.0)),
        )
        # Anchor on a corner post (real frame geometry) so the joint origin sits
        # within tol of both the post (parent) and the shelf plate (child).
        post_x = r.deck_len / 2.0 - 0.030
        post_y = r.deck_wid / 2.0 - 0.030
        model.articulation(
            f"frame_to_shelf_{si}",
            ArticulationType.FIXED,
            parent=root,
            child=shelf,
            origin=Origin(xyz=(post_x, post_y, sz)),
        )
    return root


# --- Utility wire bin (straight-walled rectangular warehouse cage). -----------
# Wire-lattice helpers ported from rec_caster_trolley_var_deck_to_basket
# (``_build_floor_mesh`` / ``_build_wall_mesh`` / ``_build_rim_mesh``): a grid of
# straight ``tube_from_spline_points`` wires merged into a single MeshGeometry.
# Walls are VERTICAL and the footprint is constant in Z (no supermarket taper).
def _straight_wire(p0, p1, *, radius=_BIN_WIRE_R, radial_segments=6):
    return tube_from_spline_points(
        [p0, p1], radius=radius, samples_per_segment=1,
        radial_segments=radial_segments, cap_ends=True,
    )


def _bin_grid(start, end, spacing):
    n = max(int(round((end - start) / spacing)) + 1, 2)
    step = (end - start) / (n - 1)
    return [start + i * step for i in range(n)]


def _bin_dims(r: ResolvedCasterTrolleyConfig):
    """(floor_z, rim_z, bx_min, bx_max, by_min, by_max) for the bin lattice."""
    floor_z = r.deck_bottom_z + _BIN_FRAME_SEC  # sits on the tubular frame top
    rim_z = floor_z + _BIN_HEIGHT
    bx = r.deck_len / 2.0 - _BIN_INSET
    by = r.deck_wid / 2.0 - _BIN_INSET
    return floor_z, rim_z, -bx, bx, -by, by


def _bin_frame_mesh(r: ResolvedCasterTrolleyConfig, assets):
    """Rectangular tubular chassis: perimeter rails + a cross member under every
    caster X so each swivel mount lands on real frame geometry. Built as fused
    box sections (= rectangular tube) -> one connected root body."""
    s = _BIN_FRAME_SEC
    hx = r.deck_len / 2.0 - s / 2.0
    hy = r.deck_wid / 2.0 - s / 2.0
    zc = r.deck_bottom_z + s / 2.0  # bottom face at deck_bottom_z (caster mount z)
    result = None
    # Long rails (along X at ±Y).
    for sy in (-hy, hy):
        box = cq.Workplane("XY", origin=(0.0, sy, zc)).box(2 * hx + s, s, s)
        result = box if result is None else result.union(box)
    # Short rails (along Y at ±X).
    for sx in (-hx, hx):
        result = result.union(cq.Workplane("XY", origin=(sx, 0.0, zc)).box(s, 2 * hy + s, s))
    # Cross members at each unique caster X (span full Y so any caster Y is on it).
    xs = sorted({round(cx, 4) for cx, _cy in _caster_positions(r)})
    for cx in xs:
        if abs(abs(cx) - hx) < 1.5e-3:
            continue  # already covered by a short rail
        result = result.union(cq.Workplane("XY", origin=(cx, 0.0, zc)).box(s, 2 * hy + s, s))
    return mesh_from_cadquery(result, "bin_frame", assets=assets)


def _bin_floor_mesh(*, x_min, x_max, y_min, y_max, z):
    floor = MeshGeometry()
    edge_r = _BIN_WIRE_R * 1.4
    for y in (y_min, y_max):
        floor.merge(_straight_wire((x_min, y, z), (x_max, y, z), radius=edge_r, radial_segments=8))
    for x in (x_min, x_max):
        floor.merge(_straight_wire((x, y_min, z), (x, y_max, z), radius=edge_r, radial_segments=8))
    for y in _bin_grid(y_min, y_max, _BIN_WIRE_SPACING)[1:-1]:
        floor.merge(_straight_wire((x_min, y, z), (x_max, y, z)))
    for x in _bin_grid(x_min, x_max, _BIN_WIRE_SPACING)[1:-1]:
        floor.merge(_straight_wire((x, y_min, z), (x, y_max, z)))
    return floor


def _bin_wall_mesh(*, span_axis, normal_pos, span_min, span_max, z_min, z_max):
    wall = MeshGeometry()
    z_positions = _bin_grid(z_min, z_max, _BIN_WIRE_SPACING)
    span_positions = _bin_grid(span_min, span_max, _BIN_WIRE_SPACING)
    for z in z_positions:  # horizontal wires
        if span_axis == "x":
            wall.merge(_straight_wire((span_min, normal_pos, z), (span_max, normal_pos, z)))
        else:
            wall.merge(_straight_wire((normal_pos, span_min, z), (normal_pos, span_max, z)))
    for p in span_positions:  # vertical wires
        if span_axis == "x":
            wall.merge(_straight_wire((p, normal_pos, z_min), (p, normal_pos, z_max)))
        else:
            wall.merge(_straight_wire((normal_pos, p, z_min), (normal_pos, p, z_max)))
    return wall


def _bin_rim_mesh(*, x_min, x_max, y_min, y_max, z):
    rim = MeshGeometry()
    for y in (y_min, y_max):
        rim.merge(_straight_wire((x_min, y, z), (x_max, y, z), radius=_BIN_RIM_R, radial_segments=10))
    for x in (x_min, x_max):
        rim.merge(_straight_wire((x, y_min, z), (x, y_max, z), radius=_BIN_RIM_R, radial_segments=10))
    return rim


def _build_utility_wire_bin(model, r, mats, *, assets):
    """Straight-walled rectangular wire-mesh warehouse bin on a tubular chassis
    root: rectangular tube frame rails + inline wire-mesh floor + 4 vertical
    walls + top rim rail. Walls vertical, footprint constant in Z."""
    root = model.part("load_surface")
    floor_z, rim_z, bx_min, bx_max, by_min, by_max = _bin_dims(r)
    # Tubular chassis frame (root structure; carries the casters).
    root.visual(_bin_frame_mesh(r, assets), material=mats["accent"], name="bin_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"))
    # Inline wire-mesh floor.
    root.visual(
        mesh_from_geometry(
            _bin_floor_mesh(x_min=bx_min, x_max=bx_max, y_min=by_min, y_max=by_max, z=floor_z),
            "bin_floor",
        ),
        material=mats["deck"],
        name="bin_floor", material_class_id="metal.mesh_chainmail",
    )
    # 4 STRAIGHT VERTICAL walls (long sides at ±Y, short sides at ±X).
    wall_configs = [
        ("x", by_max, bx_min, bx_max, "bin_wall_front"),
        ("x", by_min, bx_min, bx_max, "bin_wall_rear"),
        ("y", bx_max, by_min, by_max, "bin_wall_right"),
        ("y", bx_min, by_min, by_max, "bin_wall_left"),
    ]
    for span_axis, normal_pos, span_min, span_max, wall_name in wall_configs:
        root.visual(
            mesh_from_geometry(
                _bin_wall_mesh(
                    span_axis=span_axis, normal_pos=normal_pos,
                    span_min=span_min, span_max=span_max, z_min=floor_z, z_max=rim_z,
                ),
                wall_name,
            ),
            material=mats["deck"],
            name=wall_name, material_class_id="metal.mesh_chainmail",
        )
    # Top rim rail.
    root.visual(
        mesh_from_geometry(
            _bin_rim_mesh(x_min=bx_min, x_max=bx_max, y_min=by_min, y_max=by_max, z=rim_z),
            "bin_rim",
        ),
        material=mats["accent"],
        name="bin_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"),
    )
    root.inertial = Inertial.from_geometry(
        Box((r.deck_len, r.deck_wid, _BIN_FRAME_SEC + _BIN_HEIGHT)),
        mass=12.0,
        origin=Origin(xyz=(0.0, 0.0, r.deck_bottom_z + (_BIN_FRAME_SEC + _BIN_HEIGHT) / 2.0)),
    )
    return root


_LOAD_BUILDERS = {
    "flat_platform_deck": _build_flat_platform_deck,
    "stacked_open_trays": _build_stacked_open_trays,
    "wire_mesh_shelf_stack": _build_wire_mesh_shelf_stack,
    "utility_wire_bin": _build_utility_wire_bin,
}


# ===========================================================================
# Slot B: handle / upright.
# ===========================================================================
def _handle_top_z(r: ResolvedCasterTrolleyConfig) -> float:
    """Z of the deck top where the +X handle mounts (surface that anchors it)."""
    if r.load_surface == "stacked_open_trays":
        # Corner-leg top (real root geometry; the cleat bridges to it).
        return r.deck_bottom_z + _TRAY_GAP + _TRAY_WALL
    if r.load_surface == "utility_wire_bin":
        # Mount on the bin's top rim rail (planar rim; real root geometry).
        return r.deck_bottom_z + _BIN_FRAME_SEC + _BIN_HEIGHT
    if r.load_surface == "wire_mesh_shelf_stack":
        # Mount on the shelf-frame top (the posts/top loop are the upright).
        return r.deck_bottom_z + _SHELF_FRAME_H
    return r.deck_top_z


def _handle_mount_cleat(root, r, mats, *, x_end, z_base, sx=1.0, name="handle_mount_cleat"):
    """Drop a short cross cleat on the ROOT at the handle mount line so the
    handle feet always rest on real root geometry and the FIXED-joint origin sits
    on the root (works for trays/bin/shelf where the root top is sparse). The
    cleat spans the mount width (Y) and reaches OUT to the nearest short edge (X,
    direction ``sx``) and drops below ``z_base`` so it always overlaps the
    perimeter root geometry (deck lip / tray rail / bin rim / shelf top loop)
    and never floats over the open top cavity."""
    half = r.deck_wid / 2.0 - 0.040
    # Straddle z_base modestly: drop just below it to bite the rim/loop/rail band
    # (all those root features sit at z_base) without punching down to wheel level
    # on the flat deck (z_base = deck top). Bottom at z_base - 0.018.
    cleat_h = 0.034
    cleat_top = z_base + 0.016
    cleat_z = cleat_top - cleat_h / 2.0  # bottom = z_base - 0.018
    x_edge = sx * (r.deck_len / 2.0)
    cleat_len_x = abs(x_edge - x_end) + 0.070
    cx = (x_end + x_edge) / 2.0
    root.visual(
        Box((cleat_len_x, 2.0 * half + 0.030, cleat_h)),
        origin=Origin(xyz=(cx, 0.0, cleat_z)),
        material=mats["accent"],
        name=name, material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"),
    )


def _build_tall_inverted_U(model, r, mats, root, *, assets) -> list[str]:
    """One tall inverted-U push handle at the +X end (FIXED)."""
    z_base = _handle_top_z(r)
    x_end = r.deck_len / 2.0 - 0.060
    _handle_mount_cleat(root, r, mats, x_end=x_end, z_base=z_base)
    handle = model.part("push_handle")
    mesh = _inverted_u_tube(r, rise=r.handle_rise, name="push_handle", assets=assets, cross_rails=2)
    handle.visual(mesh, material=mats["accent"], name="push_handle_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"))
    handle.inertial = Inertial.from_geometry(
        Box((0.08, r.deck_wid, r.handle_rise)),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, r.handle_rise / 2.0)),
    )
    # Joint origin = mount-line center (= handle-local (0,0,0)) on the deck top.
    model.articulation(
        f"{root.name}_to_push_handle",
        ArticulationType.FIXED,
        parent=root,
        child=handle,
        origin=Origin(xyz=(x_end, 0.0, z_base)),
    )
    return ["push_handle"]


def _build_handle_both_ends(model, r, mats, root, *, assets) -> list[str]:
    """An inverted-U handle at BOTH short ends (FIXED ×2)."""
    z_base = _handle_top_z(r)
    names: list[str] = []
    for sx, tag in ((1.0, "front"), (-1.0, "rear")):
        x_end = sx * (r.deck_len / 2.0 - 0.060)
        # Edge-reaching cleat (overlaps the perimeter root geometry) so the end
        # frame's feet rest on a connected body, not a floating box.
        _handle_mount_cleat(
            root, r, mats, x_end=x_end, z_base=z_base, sx=sx,
            name=f"end_mount_cleat_{tag}",
        )
        part = model.part(f"end_frame_{tag}")
        mesh = _inverted_u_tube(
            r, rise=r.handle_rise * 0.85, name=f"end_frame_{tag}", assets=assets,
            cross_rails=1,
        )
        part.visual(mesh, material=mats["accent"], name=f"end_frame_{tag}_tube", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"))
        part.inertial = Inertial.from_geometry(
            Box((0.08, r.deck_wid, r.handle_rise)),
            mass=1.6,
            origin=Origin(xyz=(0.0, 0.0, r.handle_rise / 2.0)),
        )
        model.articulation(
            f"{root.name}_to_end_frame_{tag}",
            ArticulationType.FIXED,
            parent=root,
            child=part,
            origin=Origin(xyz=(x_end, 0.0, z_base)),
        )
        names.append(f"end_frame_{tag}")
    return names


def _mesh_panel_mesh(r: ResolvedCasterTrolleyConfig, assets, *, length, along_x, name):
    """A flat mesh panel authored centered at local (0,0,0): spans `length` along
    its in-plane axis and rises in Z (full frame height). Grid of holes cut for a
    perforated-mesh look. Used for cage side/back panels."""
    z_span = _SHELF_FRAME_H - 0.040
    thick = 0.006
    # Authored so local (0,0,0) is one END of the panel (a frame post), with the
    # panel extending in -(in-plane axis). The post line carries the FIXED origin.
    if along_x:
        plate = cq.Workplane("XY", origin=(-length / 2.0, 0, 0)).box(length, thick, z_span)
    else:
        plate = cq.Workplane("XY", origin=(0, -length / 2.0, 0)).box(thick, length, z_span)
    # Perforation grid.
    pitch = 0.060
    n_along = max(2, int(length // pitch))
    n_z = max(2, int(z_span // pitch))
    a0 = -((n_along - 1) * pitch) / 2.0
    z0 = -((n_z - 1) * pitch) / 2.0
    for ia in range(n_along):
        for iz in range(n_z):
            a = a0 + ia * pitch
            zz = z0 + iz * pitch
            if along_x:
                hole = cq.Workplane("XZ", origin=(a, 0, zz)).circle(0.014).extrude(
                    thick, both=True
                )
            else:
                hole = cq.Workplane("YZ", origin=(0, a, zz)).circle(0.014).extrude(
                    thick, both=True
                )
            plate = plate.cut(hole)
    return mesh_from_cadquery(plate, name, assets=assets)


def _build_full_cage(model, r, mats, root, *, assets) -> list[str]:
    """Full-height wire-mesh cage panels (back + 2 sides), front open. The posts
    belong to the shelf frame (root). Requires wire_mesh_shelf_stack."""
    hx = r.deck_len / 2.0 - 0.030
    hy = r.deck_wid / 2.0 - 0.030
    cz = r.deck_bottom_z + _SHELF_FRAME_H / 2.0
    names: list[str] = []
    # Each panel anchored at a frame-post corner (local (0,0,0)); the panel
    # extends along -(in-plane axis) toward the opposite post.
    # (tag, post xy, along_x, length).
    specs = [
        ("back", (-hx, hy), False, 2.0 * hy),
        ("side_left", (hx, hy), True, 2.0 * hx),
        ("side_right", (hx, -hy), True, 2.0 * hx),
    ]
    for tag, (cx, cy), along_x, length in specs:
        part = model.part(f"cage_{tag}")
        part.visual(
            _mesh_panel_mesh(r, assets, length=length, along_x=along_x, name=f"cage_{tag}"),
            material=mats["wheel_rim"],
            name=f"cage_{tag}_panel", material_class_id="metal.patterned_sheet_panel",
        )
        part.inertial = Inertial.from_geometry(
            Box((length if along_x else 0.02, 0.02 if along_x else length, _SHELF_FRAME_H)),
            mass=1.2,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"{root.name}_to_cage_{tag}",
            ArticulationType.FIXED,
            parent=root,
            child=part,
            origin=Origin(xyz=(cx, cy, cz)),
        )
        names.append(f"cage_{tag}")
    return names


def _folding_handle_mesh(r: ResolvedCasterTrolleyConfig, assets):
    """Folding inverted-U handle authored in the HINGE-local frame: the pivot is
    at the part origin (0,0,0); the U rises in +Z and the legs splay in ±Y."""
    half = r.deck_wid / 2.0 - 0.040
    rise = r.handle_rise
    pts = [
        (0.0, half, 0.0),
        (0.0, half, 0.55 * rise),
        (0.0, 0.0, rise),
        (0.0, -half, 0.55 * rise),
        (0.0, -half, 0.0),
    ]
    tube = _swept_tube(pts, _HANDLE_TUBE_R, "folding_handle", assets)
    # Pivot foot bar: a single box section spanning the full Y width at the hinge
    # line (z=0), straddling both U-leg feet and the barrels. This one solid box
    # guarantees both legs + pivot geometry are one connected body (thin tangential
    # cylinders can split the union into disconnected islands). Its X/Z section is
    # kept small (half-section 0.012 m) so the box SURFACE passes within the 0.015
    # articulation-origin baseline of the hinge local origin (0,0,0).
    foot_sec = 0.024
    foot = cq.Workplane("XY", origin=(0.0, 0.0, 0.0)).box(
        foot_sec, 2.0 * half + 2.0 * _HANDLE_TUBE_R, foot_sec
    )
    tube = tube.union(foot)
    # Hinge barrels at the captured ±Y pivot ends (deck brackets capture these).
    # No center barrel: a fat center barrel would enclose the slim foot bar and
    # push the nearest child surface past the 0.015 origin baseline at (0,0,0).
    for sy in (half, -half):
        barrel = (
            cq.Workplane("XZ", origin=(0.0, sy, 0.0))
            .circle(_HANDLE_TUBE_R + 0.004)
            .extrude(0.018, both=True)
        )
        tube = tube.union(barrel)
    # One cross rail tying the two uprights mid-height, as a box that fully spans
    # and overlaps both legs.
    rail = cq.Workplane("XY", origin=(0.0, 0.0, 0.45 * rise)).box(
        2.4 * _HANDLE_TUBE_R, 2.0 * half + 2.0 * _HANDLE_TUBE_R, 2.4 * _HANDLE_TUBE_R
    )
    tube = tube.union(rail)
    return mesh_from_cadquery(tube, "folding_handle", assets=assets)


def _build_folding_handle(model, r, mats, root, *, assets) -> list[str]:
    """Folding push handle on a REVOLUTE -Y hinge at the deck top +X end."""
    z_base = _handle_top_z(r)
    x_end = r.deck_len / 2.0 - 0.060
    hinge_y = r.deck_wid / 2.0 - 0.040
    _handle_mount_cleat(root, r, mats, x_end=x_end, z_base=z_base)
    # Deck-side hinge brackets / barrels (real anchoring visuals on the root).
    for sy_i, sy in enumerate((hinge_y, -hinge_y)):
        root.visual(
            Box((0.030, 0.018, 0.024)),
            origin=Origin(xyz=(x_end, sy, z_base + 0.010)),
            material=mats["accent"],
            name=f"fold_hinge_bracket_{sy_i}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"),
        )
        root.visual(
            Cylinder(radius=0.006, length=0.024),
            origin=Origin(xyz=(x_end, sy, z_base + 0.014), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name=f"fold_hinge_barrel_{sy_i}", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"),
        )
    handle = model.part("push_handle")
    mesh = _folding_handle_mesh(r, assets)
    handle.visual(mesh, material=mats["accent"], name="push_handle_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"galvanized", "black_rollcage", "industrial_blue_wood"} else "metal.steel_bare"))
    handle.inertial = Inertial.from_geometry(
        Box((0.06, r.deck_wid, r.handle_rise)),
        mass=1.6,
        origin=Origin(xyz=(0.0, 0.0, r.handle_rise / 2.0)),
    )
    model.articulation(
        f"{root.name}_to_push_handle",
        ArticulationType.REVOLUTE,
        parent=root,
        child=handle,
        origin=Origin(xyz=(x_end, 0.0, z_base + 0.014)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=_FOLD_OPEN),
    )
    return ["push_handle"]


_HANDLE_BUILDERS = {
    "tall_inverted_U_one_end": _build_tall_inverted_U,
    "handle_both_ends": _build_handle_both_ends,
    "full_cage_uprights": _build_full_cage,
    "folding_handle": _build_folding_handle,
}


# ===========================================================================
# Build
# ===========================================================================
def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    """4 realistic colorways (spec §palette block). Keys: deck, accent, wheel,
    wheel_rim. (chrome_supermarket removed with the supermarket seed.)"""
    presets: dict[str, dict[str, tuple[float, float, float, float]]] = {
        "warehouse_steel": {
            "deck": (0.62, 0.63, 0.65, 1.0),
            "accent": (0.70, 0.71, 0.73, 1.0),
            "wheel": (0.10, 0.10, 0.11, 1.0),
            "wheel_rim": (0.78, 0.79, 0.81, 1.0),
        },
        "galvanized": {
            "deck": (0.66, 0.67, 0.69, 1.0),
            "accent": (0.60, 0.61, 0.63, 1.0),
            "wheel": (0.12, 0.12, 0.13, 1.0),
            "wheel_rim": (0.78, 0.79, 0.80, 1.0),
        },
        "black_rollcage": {
            "deck": (0.45, 0.46, 0.48, 1.0),
            "accent": (0.13, 0.13, 0.15, 1.0),
            "wheel": (0.06, 0.06, 0.07, 1.0),
            "wheel_rim": (0.30, 0.31, 0.33, 1.0),
        },
        "industrial_blue_wood": {
            "deck": (0.55, 0.45, 0.32, 1.0),
            "accent": (0.28, 0.36, 0.52, 1.0),
            "wheel": (0.62, 0.14, 0.13, 1.0),
            "wheel_rim": (0.30, 0.32, 0.36, 1.0),
        },
    }
    return presets[style]


def _wheel_style_rgba(
    style: WheelStyle, pal: dict[str, tuple[float, float, float, float]]
) -> dict[str, tuple[float, float, float, float]]:
    """Wheel appearance material colors per ``wheel_style``. ``surface`` = the
    tire/tread band (tire styles); ``metal`` = the rim/hub or the cast disc."""
    if style == "poly_hard":
        # Hard poly/nylon: light off-white/gray, not black rubber.
        return {"surface": (0.82, 0.82, 0.85, 1.0), "metal": pal["wheel_rim"]}
    if style == "pneumatic_tread":
        # Air tire: deep matte black rubber.
        return {"surface": (0.07, 0.07, 0.08, 1.0), "metal": pal["wheel_rim"]}
    if style == "cast_spoked":
        # Cast steel/iron: dark hard metal for the whole spoked disc.
        return {"surface": (0.20, 0.20, 0.22, 1.0), "metal": (0.20, 0.20, 0.22, 1.0)}
    # solid_rubber: standard dark rubber on the palette rim.
    return {"surface": pal["wheel"], "metal": pal["wheel_rim"]}


def build_caster_trolley(
    config: CasterTrolleyConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = _palette_rgba(r.palette_style)
    mats = {
        key: model.material(f"caster_trolley_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }
    # Wheel-appearance materials keyed off the chosen wheel_style (independent of
    # the body palette): the tire/tread surface + the rim/cast-disc metal.
    wrgba = _wheel_style_rgba(r.wheel_style, pal)
    mats["wheel_surface"] = model.material(
        f"caster_trolley_wheelsurf_{r.wheel_style}", rgba=wrgba["surface"]
    )
    mats["wheel_metal"] = model.material(
        f"caster_trolley_wheelmetal_{r.wheel_style}", rgba=wrgba["metal"]
    )

    # --- Slot A: load surface (root). ---
    root = _LOAD_BUILDERS[r.load_surface](model, r, mats, assets=assets)

    # --- Slot B: handle / upright. ---
    _HANDLE_BUILDERS[r.handle_upright](model, r, mats, root, assets=assets)

    # --- Slot C: caster ring (all-rigid mounts + the defining center-roll). ---
    _build_casters(model, r, mats, root, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_caster_trolley(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_caster_trolley(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_caster_trolley_tests(
    object_model: ArticulatedObject,
    config: CasterTrolleyConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    root = object_model.get_part("load_surface")
    n = r.caster_count

    # ---- Captured-pin / swivel-bearing allowances (element-scoped). ----
    for i in range(n):
        yoke = object_model.get_part(f"caster_yoke_{i}")
        wheel = object_model.get_part(f"caster_wheel_{i}")
        for wheel_elem in (f"rim_{i}", f"tire_{i}", f"spoked_wheel_{i}"):
            if any(v.name == wheel_elem for v in wheel.visuals):
                ctx.allow_overlap(
                    yoke,
                    wheel,
                    elem_a=f"axle_pin_{i}",
                    elem_b=wheel_elem,
                    reason=(
                        "The slim caster axle pin is captured inside the wheel bore; "
                        "fork legs and crown remain outside the wheel envelope."
                    ),
                )
        ctx.allow_overlap(
            root, yoke,
            reason="The rigid caster mount plate is seated up against the root underside.",
        )

    # Handle mount overlap (bolted boss seated into the deck top).
    handle_parts: list[str] = []
    if r.handle_upright == "tall_inverted_U_one_end":
        handle_parts = ["push_handle"]
    elif r.handle_upright == "handle_both_ends":
        handle_parts = ["end_frame_front", "end_frame_rear"]
    elif r.handle_upright == "full_cage_uprights":
        handle_parts = ["cage_back", "cage_side_left", "cage_side_right"]
    elif r.handle_upright == "folding_handle":
        handle_parts = ["push_handle"]
    for hp in handle_parts:
        ctx.allow_overlap(
            root, object_model.get_part(hp),
            reason="The upright/handle mounting boss/panel is seated against the root frame at its mount.",
        )

    if r.handle_upright == "folding_handle":
        handle = object_model.get_part("push_handle")
        for sy_i in range(2):
            ctx.allow_overlap(
                root, handle,
                reason="The folding-handle hinge pin is captured inside the deck hinge barrel.",
            )

    if r.load_surface == "stacked_open_trays":
        ctx.allow_overlap(
            root, object_model.get_part("upper_tray"),
            reason="The upper tray seats on the corner legs of the lower tray frame.",
        )
        # The handle/upright rises past the upper-tray rim at the mount end.
        upper = object_model.get_part("upper_tray")
        for hp in handle_parts:
            ctx.allow_overlap(
                object_model.get_part(hp), upper,
                reason="The push handle/upright base passes the upper tray rim at the mount end.",
            )

    if r.load_surface == "wire_mesh_shelf_stack":
        for si in range(r.tier_count):
            shelf = object_model.get_part(f"shelf_{si}")
            ctx.allow_overlap(
                root, shelf,
                reason="The shelf pan rests on / is captured by the frame mid rails.",
            )
            # The push handle / end frames / folding handle rise through the
            # shelf level at the mount end (the frame posts pass the shelves).
            for hp in handle_parts:
                ctx.allow_overlap(
                    object_model.get_part(hp), shelf,
                    reason="The upright/handle passes the shelf level at the mount end (frame post line).",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_parts_overlap_in_sampled_poses(name="no_overlap_in_sampled_poses")
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: root present, cart-sized, rides above the wheels. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("load_surface root present", "load_surface" in part_names, details=str(sorted(part_names)))
    root_aabb = ctx.part_world_aabb(root)
    ctx.check("root has world AABB", root_aabb is not None, details=f"{root_aabb}")
    if root_aabb is not None:
        (rmn, rmx) = root_aabb
        ext_x = rmx[0] - rmn[0]
        ctx.check(
            "load surface is roughly cart-sized (X)",
            0.55 < ext_x < 1.30,
            details=f"ext_x={ext_x:.3f}",
        )
        ctx.check(
            "root underside rides above the wheels",
            rmn[2] > r.wheel_r * 0.5,
            details=f"root_z_min={rmn[2]:.4f}, deck_bottom_z={r.deck_bottom_z:.3f}",
        )

    # ---- Casters: ALL-RIGID mounts + center-roll topology + ground contact. ----
    # (User's authoritative decision: NO swivel casters anywhere. Every yoke mount
    # is FIXED; every wheel rolls CONTINUOUS about its Y axle through its center.)
    ctx.check(
        "caster count is len(positions)-driven",
        len(_caster_positions(r)) == n,
        details=f"positions={len(_caster_positions(r))}, N={n}",
    )
    yoke_joints = [object_model.get_articulation(f"load_surface_to_caster_yoke_{i}") for i in range(n)]
    roll_joints = [object_model.get_articulation(f"caster_spin_{i}") for i in range(n)]
    # Every yoke mount is RIGID (FIXED) — no swivel/kingpin joint anywhere.
    for i, yj in enumerate(yoke_joints):
        ctx.check(
            f"caster {i} yoke mount is RIGID (FIXED, no swivel)",
            str(yj.articulation_type).upper().endswith("FIXED"),
            details=f"type={yj.articulation_type}",
        )
    n_continuous_z_yokes = sum(
        1 for yj in yoke_joints
        if str(yj.articulation_type).upper().endswith("CONTINUOUS")
    )
    ctx.check(
        "NO swivel yoke mounts anywhere (zero CONTINUOUS yoke joints)",
        n_continuous_z_yokes == 0,
        details=f"continuous_yoke_joints={n_continuous_z_yokes}, N={n}",
    )
    # Every wheel rolls CONTINUOUS about its transverse Y axle, and the roll-joint
    # origin passes through the wheel center (zero trail: origin X == 0).
    for i, rj in enumerate(roll_joints):
        ctx.check(
            f"caster wheel {i} rolls about its Y axle (CONTINUOUS)",
            abs(rj.axis[1]) > 0.99 and str(rj.articulation_type).upper().endswith("CONTINUOUS"),
            details=f"axis={rj.axis}, type={rj.articulation_type}",
        )
        ctx.check(
            f"caster {i} roll origin passes through the wheel center (zero trail)",
            abs(rj.origin.xyz[0]) < 1e-6 and abs(rj.origin.xyz[1]) < 1e-6,
            details=f"roll_origin_xyz={tuple(rj.origin.xyz)}",
        )
    # All wheels reach the ground plane (z ~= 0).
    for i in range(n):
        wheel = object_model.get_part(f"caster_wheel_{i}")
        wheel_visuals_are_y_aligned = all(
            abs(v.origin.rpy[0]) < 1e-6
            and abs(v.origin.rpy[1]) < 1e-6
            and abs(abs(v.origin.rpy[2]) - math.pi / 2.0) < 1e-6
            for v in wheel.visuals
        )
        ctx.check(
            f"caster wheel {i} visual axle aligns with roll joint Y axis",
            wheel_visuals_are_y_aligned,
            details=f"visual_rpys={[tuple(v.origin.rpy) for v in wheel.visuals]}",
        )
        w_aabb = ctx.part_world_aabb(wheel)
        ctx.check(
            f"caster wheel {i} reaches the ground plane",
            w_aabb is not None and abs(w_aabb[0][2]) < 0.025,
            details=f"wheel_z_min={None if w_aabb is None else w_aabb[0][2]}",
        )

    # ---- Wheel-TYPE (appearance) diversity axis: geometry reflects wheel_style. ----
    ctx.check(
        "wheel_style is one of the 4 realistic wheel types",
        r.wheel_style in WHEEL_STYLES,
        details=f"wheel_style={r.wheel_style}, styles={WHEEL_STYLES}",
    )
    spec = _WHEEL_STYLE_SPECS[r.wheel_style]
    w0 = object_model.get_part("caster_wheel_0")
    w0_vis = {v.name for v in w0.visuals}
    if spec.kind == "spoked":
        # cast_spoked: a single spoked/slotted cast-metal disc, NO rubber tire band.
        ctx.check(
            "cast_spoked wheel is a spoked metal disc (no rubber tire)",
            any(nm.startswith("spoked_wheel") for nm in w0_vis)
            and not any(nm.startswith("tire") for nm in w0_vis),
            details=f"visuals={sorted(w0_vis)}",
        )
    else:
        # tire styles carry a metal rim + a rubber tire band.
        ctx.check(
            f"{r.wheel_style} wheel has a rubber tire band on a metal rim",
            any(nm.startswith("tire") for nm in w0_vis)
            and any(nm.startswith("rim") for nm in w0_vis),
            details=f"visuals={sorted(w0_vis)}",
        )
    if r.wheel_style == "pneumatic_tread":
        ctx.check(
            "pneumatic wheel is fatter/wider than the baseline",
            r.wheel_w > _WHEEL_W + 1e-6 and spec.tread_style != "none",
            details=f"wheel_w={r.wheel_w:.4f} vs base={_WHEEL_W:.4f}, tread={spec.tread_style}",
        )
    if r.wheel_style == "poly_hard":
        ctx.check(
            "poly wheel is narrower than the baseline",
            r.wheel_w < _WHEEL_W - 1e-6,
            details=f"wheel_w={r.wheel_w:.4f} vs base={_WHEEL_W:.4f}",
        )

    # ---- Handle / upright present and reaches above the load surface. ----
    if r.handle_upright in ("tall_inverted_U_one_end", "folding_handle"):
        handle = object_model.get_part("push_handle")
        h_aabb = ctx.part_world_aabb(handle)
        ctx.check("push handle present", h_aabb is not None, details=f"{h_aabb}")
        if h_aabb is not None and root_aabb is not None:
            ctx.check(
                "handle rises above the load surface top",
                h_aabb[1][2] > root_aabb[1][2] + 0.05,
                details=f"handle_top={h_aabb[1][2]:.3f}, root_top={root_aabb[1][2]:.3f}",
            )
    if r.handle_upright == "folding_handle":
        j = object_model.get_articulation("load_surface_to_push_handle")
        ctx.check(
            "folding handle is REVOLUTE about -Y",
            str(j.articulation_type).upper().endswith("REVOLUTE") and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type}, axis={j.axis}",
        )
        lim = j.motion_limits
        ctx.check(
            "folding hinge range [0, <=1.5]",
            lim is not None and lim.lower == 0.0 and lim.upper is not None and lim.upper <= 1.5 + 1e-6,
            details=f"limits=({None if lim is None else lim.lower},{None if lim is None else lim.upper})",
        )
        # The handle folds (its AABB top drops when actuated toward flat).
        handle = object_model.get_part("push_handle")
        up = ctx.part_world_aabb(handle)
        with ctx.pose({j: _FOLD_OPEN * 0.9}):
            folded = ctx.part_world_aabb(handle)
        if up is not None and folded is not None:
            ctx.check(
                "folding the handle lowers it toward flat",
                folded[1][2] < up[1][2] - 0.05,
                details=f"upright_top={up[1][2]:.3f}, folded_top={folded[1][2]:.3f}",
            )

    # ---- Compatibility matrix enforced. ----
    if r.handle_upright == "full_cage_uprights":
        ctx.check(
            "full_cage only on wire_mesh_shelf_stack",
            r.load_surface == "wire_mesh_shelf_stack",
            details=f"load_surface={r.load_surface}",
        )
    # Palette is one of exactly 4 realistic colorways (supermarket chrome removed).
    ctx.check(
        "palette_style is one of the 4 realistic colorways",
        r.palette_style in PALETTE_STYLES and len(PALETTE_STYLES) == 4,
        details=f"palette={r.palette_style}, styles={PALETTE_STYLES}",
    )

    # ---- utility_wire_bin: straight-walled rectangular wire cage present. ----
    if r.load_surface == "utility_wire_bin":
        ctx.check(
            "full_cage degrades off utility_wire_bin",
            r.handle_upright != "full_cage_uprights",
            details=f"handle={r.handle_upright}",
        )
        bin_vis = {v.name for v in root.visuals}
        for elem in ("bin_frame", "bin_floor", "bin_wall_front", "bin_wall_rear",
                     "bin_wall_left", "bin_wall_right", "bin_rim"):
            ctx.check(
                f"utility_wire_bin has {elem}",
                elem in bin_vis,
                details=f"visuals={sorted(bin_vis)}",
            )
        # Walls are straight & vertical: floor footprint == rim footprint (no taper).
        floor_aabb = ctx.part_element_world_aabb(root, elem="bin_floor")
        rim_aabb = ctx.part_element_world_aabb(root, elem="bin_rim")
        if floor_aabb is not None and rim_aabb is not None:
            fx = floor_aabb[1][0] - floor_aabb[0][0]
            rx = rim_aabb[1][0] - rim_aabb[0][0]
            ctx.check(
                "bin walls vertical (constant footprint, not tapered)",
                abs(fx - rx) < 0.02 and rim_aabb[1][2] > floor_aabb[1][2] + 0.20,
                details=f"floor_x={fx:.3f}, rim_x={rx:.3f}, floor_top={floor_aabb[1][2]:.3f}, rim={rim_aabb[1][2]:.3f}",
            )

    # ---- Shelf tier multiplicity (shelf only). ----
    if r.load_surface == "wire_mesh_shelf_stack":
        shelf_parts = [p.name for p in object_model.parts if p.name.startswith("shelf_")]
        ctx.check(
            "tier_count shelves authored",
            len(shelf_parts) == r.tier_count,
            details=f"shelves={sorted(shelf_parts)} expected t={r.tier_count}",
        )
    else:
        # tier_count not exposed on non-shelf surfaces (no orphan shelf joints).
        orphan = [p.name for p in object_model.parts if p.name.startswith("shelf_")]
        ctx.check(
            "no orphan shelves on non-shelf surfaces",
            len(orphan) == 0,
            details=f"orphan_shelves={orphan}",
        )

    # ---- slot_choices recorded with multiplicity encoded. ----
    ctx.check(
        "slot_choices recorded with caster/tier counts encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "CasterTrolleyConfig",
    "ResolvedCasterTrolleyConfig",
    "build_caster_trolley",
    "build_seeded_caster_trolley",
    "config_from_seed",
    "resolve_config",
    "run_caster_trolley_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
