# SPDX-License-Identifier: Apache-2.0

"""Real-world sign modular template.

Identity: a visible information/warning/wayfinding sign. The top-level family
now spans real sign constructions rather than forcing every "sign" into a wet-
floor sandwich board: folding floor caution signs, roadside/post signs, hanging
shop blade signs, wall plaques, and table tent signs. The floor caution A-frame
keeps the legacy detailed hinge/knuckle/tether structure; the other families add
their own real-world mounting structures, plates, rails, hooks, screw caps, and
at least one plausible moving joint.

NOT an arbitrary banner sculpture or a fantasy hinged red shard. Every sampled
type must read as a manufactured sign assembly with a plausible support method.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Sign_Sign_sign.md`` and the 9 five-star
sources (2 parents + 7 slot-fork variants) under ``data/records/``.

CANONICAL apex frame (Family B, 6/9 sources): each leaf is authored in its own
local frame with the apex (hinge) line at ``z = 0``; the leaf hangs toward
``-Z``; width runs along ``Y``; the visible front face points toward ``+X``;
shell thickness runs along ``+X``. The front leaf (root) visual is pre-tilted by
``-APEX_HALF_OPEN`` about Y and the back leaf (child) by ``+APEX_HALF_OPEN`` so
the rest pose (apex_hinge q=0) is already the open A-frame stance. ``apex_hinge``
is REVOLUTE about ``+Y``: rest ``q=0`` is the open A, ``lower≈-2·apex_half_open``
folds the two leaves flat together (store), and ``upper≈0.6`` caps how far it can
splay open (a realistic A, never sweeping the front-mounted carry bail).

Structure (pattern = ``mixed``): one top-level real-world ``sign_type`` axis plus
legacy floor-sign detail slots and generic face/mount/graphics choices:

  * Top axis ``sign_type`` (5): floor_caution_a_frame / roadside_post /
    hanging_blade / wall_plaque / table_tent.

  * Slot A ``panel_profile`` (4): rounded_top (threePointArc top arc) /
    trapezoidal_tapered (straight taper + vent slots) / gabled_peaked (pentagon
    peak) / shield (arc-chain heraldic shield). Drives the leaf silhouette and
    the knuckle-Z seating function (conditional, not topology).
  * Slot B ``base_support`` (2): flush_slab (leaf bottom lands directly) /
    corner_feet (two outrigger ``*_foot_{i}`` pads per leaf, loop-emitted,
    fused into the shell — no extra joint).
  * Slot C ``handle_mechanism`` (2): fixed_grab_hole (hand-hole cut into the
    panel near the apex — no extra joint) / swing_up_bail (separate
    ``hinge_barrel`` FIXED to the front + ``carry_handle`` bail on a 2nd
    REVOLUTE ``handle_pivot``, q=0 folded flat / upper≈π/2 upright).
  * apex ``knuckle_count`` (N in [1,7]): N discrete knuckle barrels along the
    apex Y, inlined as front-leaf visuals that straddle the pin line and capture
    the back leaf (element-scoped allow_overlap + grandfathered — they share the
    one apex_hinge, no extra joint).
  * optional ``tether_chain`` (M in [2,5]): a decorative spreader chain
    front_panel -> link_0 -> ... -> link_{M-1} that dangles into the inter-leaf
    gap. Each link joint is REVOLUTE about +Y (perpendicular to the drop run) so
    the chain actually droops/flexes; the chain hangs from the front leaf only
    (no closed loop to the back leaf).

Compatibility gating (resolve_config, spec §"compatibility matrix"):
  * shield + corner_feet -> degrade base to flush_slab (the shield bottom tapers
    to a point, no full-width outrigger seat).
  * swing_up_bail + tether_chain -> mutually exclusive (avoid debugging two new
    joint chains at once); when the bail is chosen the tether is forced off.
  * N>=6 -> shorten the knuckle band length so adjacent barrels do not interpene-
    trate / overflow the panel width.

Captured-pin / spline joints (apex_hinge, knuckle captures, bail pivot, tether
links) omit ``MatingContract`` (grandfathered: pin-through-barrel / tube-on-ear
geometry doesn't fit two axis-aligned faces), guarded by the flat articulation-
origin baseline + element-scoped ``allow_overlap`` + ``expect_contact``, exactly
as each source record's run_tests does.
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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

SignType = Literal[
    "floor_caution_a_frame",
    "roadside_post",
    "hanging_blade",
    "wall_plaque",
    "table_tent",
]
PanelProfile = Literal["rounded_top", "trapezoidal_tapered", "gabled_peaked", "shield"]
BaseSupport = Literal["flush_slab", "corner_feet"]
HandleMechanism = Literal["fixed_grab_hole", "swing_up_bail"]
FaceShape = Literal["rectangle", "rounded_rect", "circle", "octagon", "arrow"]
GraphicStyle = Literal["warning", "wayfinding", "shop", "street_name", "notice"]
PaletteStyle = Literal[
    "safety_yellow",
    "safety_orange",
    "red_white",
    "hi_vis_lime",
    "black_yellow_stripe",
    "industrial_gray",
]

SIGN_TYPES: tuple[SignType, ...] = (
    "floor_caution_a_frame",
    "roadside_post",
    "hanging_blade",
    "wall_plaque",
    "table_tent",
)
PANEL_PROFILES: tuple[PanelProfile, ...] = (
    "rounded_top",
    "trapezoidal_tapered",
    "gabled_peaked",
    "shield",
)
BASE_SUPPORTS: tuple[BaseSupport, ...] = ("flush_slab", "corner_feet")
HANDLE_MECHANISMS: tuple[HandleMechanism, ...] = ("fixed_grab_hole", "swing_up_bail")
FACE_SHAPES: tuple[FaceShape, ...] = ("rectangle", "rounded_rect", "circle", "octagon", "arrow")
GRAPHIC_STYLES: tuple[GraphicStyle, ...] = (
    "warning",
    "wayfinding",
    "shop",
    "street_name",
    "notice",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_yellow",
    "safety_orange",
    "red_white",
    "hi_vis_lime",
    "black_yellow_stripe",
    "industrial_gray",
)

# Multiplicity ranges (spec "Multiplicity / Copy Logic").
N_MIN = 1
N_MAX = 7
# Knuckle-count weights: small N high-frequency, mid medium, large rare.
KNUCKLE_WEIGHTS = (0.22, 0.24, 0.24, 0.13, 0.09, 0.05, 0.03)  # N=1..7
M_MIN = 2
M_MAX = 5
TETHER_LINK_WEIGHTS = (0.36, 0.34, 0.18, 0.12)  # M=2..5
# Optional axis, but must realize >=2 distinct tether values within a 0-19 sweep
# for the module_topology_diversity per-key gate (it only fires among the ~50%
# of seeds whose handle is not swing_up_bail, so the effective realized rate is
# roughly half of this).
TETHER_ENABLED_PROB = 0.55

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Family B parent (001) drives these.
# Apex line at local z=0, leaf hangs -Z, width along Y, front face +X.
# ---------------------------------------------------------------------------
_PANEL_WIDTH = 0.300  # width across (Y)
_PANEL_HEIGHT = 0.600  # slant height of one leaf (-Z)
_PANEL_THICK = 0.018  # molded shell wall block thickness (X)
_APEX_HALF_OPEN = 0.18  # half the A-frame opening half-angle at rest (rad)

# Rounded/shield top-arc circle through (±W/2,-0.045) and (0,-0.005).
_ARC_CZ = -0.3062
_ARC_R = 0.3012

_HINGE_PIN_R = 0.006  # knuckle barrel radius
_HINGE_BAND_LEN = 0.045  # nominal knuckle band length along Y

# Gable profile.
_GABLE_PEAK_Z = -0.008
_GABLE_SHOULDER_Z = -0.065
_GABLE_INSET = 0.006

# Shield profile.
_SHIELD_STRAIGHT_FRAC = 0.48

# Hand-hole (fixed grab hole) cut.
_HANDLE_OPENING_W = 0.130
_HANDLE_OPENING_H = 0.038
_HANDLE_CENTER_Z = -0.035

# Outrigger foot pad.
_FOOT_SPREAD_Y = 0.044
_FOOT_DROP_Z = 0.020
_FOOT_THICK_X = 0.030
_FOOT_INSET_Y = 0.010
_FOOT_EMBED_Z = 0.006

# Swing-up bail handle (canonical apex frame).
_BAIL_HALF_W = 0.060  # bail half-span along Y (pivot spacing)
_BAIL_BAR_R = 0.005
_BAIL_ARCH_H = 0.060  # arch apex height above the pivot level
_BAIL_LEG_H = 0.012
_PIVOT_EAR_R = 0.008
_PIVOT_EAR_H = 0.010
_HINGE_BARREL_R = 0.012

# Tether spreader chain.
_PITCH = 0.031
_LINK_WIDTH = 0.013
_LINK_THICK = 0.004
_LINK_HOLE_R = 0.003
# Per-link revolute range (rad) about +Y, ASYMMETRIC: the chain hangs just behind
# the front leaf inner face, so a forward (+X, toward the front) swing is blocked
# by the front leaf itself (tiny _CHAIN_FWD limit) while it droops freely back into
# the widening inter-leaf gap (larger _CHAIN_DROOP). This keeps the dangle from
# ever sweeping through the front display face while still visibly flexing.
_CHAIN_FWD = 0.02  # toward the front leaf (blocked by it)
_CHAIN_DROOP = 0.14  # back into the gap (free)
# Stand the chain off the front leaf inner face into the gap so the link body
# (LINK_WIDTH wide in X) clears the tilted front shell wall through the full droop
# range rather than grazing it.
_CHAIN_STANDOFF = 0.024
_STRAP_HT_FRAC = 0.50  # chain anchor height (fraction of height below apex)

# Apex hinge travel: rest q=0 is the open A-frame; positive q opens WIDER (capped
# so the swinging back leaf never sweeps the front-mounted carry bail); negative q
# folds the two leaves flat together to store (see _build_back_leaf).
_APEX_UPPER = 0.6  # apex hinge open travel ceiling (capped, was over-wide 2.4)

# ---------------------------------------------------------------------------
# Palettes (>=3, target 4-6). Every .visual material is sourced here.
#   shell  : front leaf body / outer
#   back   : back leaf body
#   hinge  : knuckle barrels / hinge hardware / bail
#   text   : placard text bands
#   hazard : warning triangle
#   accent : ribs / placard plate / feet trim
# ---------------------------------------------------------------------------
_PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_yellow": {
        "shell": (0.94, 0.80, 0.08, 1.0),
        "back": (0.80, 0.69, 0.10, 1.0),
        "hinge": (0.08, 0.08, 0.09, 1.0),
        "text": (0.05, 0.05, 0.05, 1.0),
        "hazard": (0.80, 0.16, 0.10, 1.0),
        "accent": (0.10, 0.10, 0.10, 1.0),
    },
    "safety_orange": {
        "shell": (0.97, 0.46, 0.05, 1.0),
        "back": (0.83, 0.39, 0.06, 1.0),
        "hinge": (0.10, 0.10, 0.11, 1.0),
        "text": (0.06, 0.06, 0.06, 1.0),
        "hazard": (0.78, 0.12, 0.08, 1.0),
        "accent": (0.12, 0.12, 0.12, 1.0),
    },
    "red_white": {
        "shell": (0.82, 0.10, 0.10, 1.0),
        "back": (0.68, 0.10, 0.10, 1.0),
        "hinge": (0.12, 0.12, 0.13, 1.0),
        "text": (0.96, 0.96, 0.96, 1.0),
        "hazard": (0.97, 0.97, 0.95, 1.0),
        "accent": (0.96, 0.96, 0.96, 1.0),
    },
    "hi_vis_lime": {
        "shell": (0.74, 0.96, 0.10, 1.0),
        "back": (0.60, 0.82, 0.10, 1.0),
        "hinge": (0.10, 0.12, 0.08, 1.0),
        "text": (0.05, 0.07, 0.04, 1.0),
        "hazard": (0.85, 0.18, 0.05, 1.0),
        "accent": (0.10, 0.14, 0.06, 1.0),
    },
    "black_yellow_stripe": {
        "shell": (0.12, 0.12, 0.12, 1.0),
        "back": (0.09, 0.09, 0.09, 1.0),
        "hinge": (0.95, 0.82, 0.06, 1.0),
        "text": (0.96, 0.84, 0.08, 1.0),
        "hazard": (0.95, 0.82, 0.06, 1.0),
        "accent": (0.95, 0.82, 0.06, 1.0),
    },
    "industrial_gray": {
        "shell": (0.46, 0.47, 0.48, 1.0),
        "back": (0.38, 0.39, 0.40, 1.0),
        "hinge": (0.14, 0.14, 0.15, 1.0),
        "text": (0.05, 0.05, 0.05, 1.0),
        "hazard": (0.93, 0.78, 0.06, 1.0),
        "accent": (0.93, 0.78, 0.06, 1.0),
    },
}


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SignConfig:
    sign_type: SignType | None = None
    panel_profile: PanelProfile | None = None
    base_support: BaseSupport | None = None
    handle_mechanism: HandleMechanism | None = None
    face_shape: FaceShape | None = None
    graphic_style: GraphicStyle | None = None
    knuckle_count: int | None = None
    tether_chain_enabled: bool | None = None
    tether_link_count: int | None = None
    palette_style: PaletteStyle = "safety_yellow"
    apex_half_open: float = _APEX_HALF_OPEN
    panel_height_scale: float = 1.0
    panel_width_scale: float = 1.0
    foot_spread_scale: float = 1.0
    name: str = "sign"


@dataclass(frozen=True)
class ResolvedSignConfig:
    sign_type: SignType
    panel_profile: PanelProfile
    base_support: BaseSupport
    handle_mechanism: HandleMechanism
    face_shape: FaceShape
    graphic_style: GraphicStyle
    knuckle_count: int
    tether_chain_enabled: bool
    tether_link_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled / derived).
    panel_width: float
    panel_height: float
    panel_thick: float
    apex_half_open: float
    knuckle_band_len: float
    foot_spread: float
    apex_lower: float
    apex_upper: float
    name: str


def config_from_seed(seed: int) -> SignConfig:
    rng = random.Random(seed)
    sign_type = rng.choices(
        SIGN_TYPES,
        weights=(0.30, 0.22, 0.18, 0.16, 0.14),
        k=1,
    )[0]
    profile = rng.choice(PANEL_PROFILES)
    base = rng.choice(BASE_SUPPORTS)
    handle = rng.choice(HANDLE_MECHANISMS)
    face_shape = rng.choice(FACE_SHAPES)
    graphic_style = rng.choice(GRAPHIC_STYLES)
    if sign_type == "roadside_post":
        face_shape = rng.choice(("rectangle", "rounded_rect", "circle", "octagon"))
        graphic_style = rng.choice(("warning", "wayfinding", "street_name", "notice"))
    elif sign_type == "hanging_blade":
        face_shape = rng.choice(("rectangle", "rounded_rect", "circle"))
        graphic_style = rng.choice(("shop", "wayfinding", "notice"))
    elif sign_type == "wall_plaque":
        face_shape = rng.choice(("rectangle", "rounded_rect", "circle", "octagon"))
        graphic_style = rng.choice(("street_name", "notice", "shop"))
    elif sign_type == "table_tent":
        face_shape = rng.choice(("rectangle", "rounded_rect"))
        graphic_style = rng.choice(("shop", "notice", "wayfinding"))
    n = rng.choices(range(N_MIN, N_MAX + 1), weights=KNUCKLE_WEIGHTS, k=1)[0]
    # Tether is a low-frequency optional axis, gated off when the bail is chosen
    # (resolve_config also enforces this; we keep config_from_seed from even
    # sampling the high-debug-risk bail+tether combo).
    tether_on = (handle != "swing_up_bail") and (rng.random() < TETHER_ENABLED_PROB)
    m = rng.choices(range(M_MIN, M_MAX + 1), weights=TETHER_LINK_WEIGHTS, k=1)[0]
    return SignConfig(
        sign_type=sign_type,
        panel_profile=profile,
        base_support=base,
        handle_mechanism=handle,
        face_shape=face_shape,
        graphic_style=graphic_style,
        knuckle_count=n,
        tether_chain_enabled=tether_on,
        tether_link_count=m,
        palette_style=rng.choice(PALETTE_STYLES),
        apex_half_open=round(rng.uniform(0.12, 0.22), 4),
        panel_height_scale=round(rng.uniform(0.92, 1.10), 4),
        panel_width_scale=round(rng.uniform(0.92, 1.12), 4),
        foot_spread_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_sign_{seed}",
    )


def resolve_config(config: SignConfig | None = None) -> ResolvedSignConfig:
    cfg = config or SignConfig()
    sign_type = _pick(cfg.sign_type, SIGN_TYPES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    profile = _pick(cfg.panel_profile, PANEL_PROFILES)
    base = _pick(cfg.base_support, BASE_SUPPORTS)
    handle = _pick(cfg.handle_mechanism, HANDLE_MECHANISMS)
    face_shape = _pick(cfg.face_shape, FACE_SHAPES)
    graphic_style = _pick(cfg.graphic_style, GRAPHIC_STYLES)

    if sign_type == "roadside_post":
        if face_shape == "arrow":
            face_shape = "rectangle"
        if graphic_style == "shop":
            graphic_style = "wayfinding"
    elif sign_type == "hanging_blade":
        if face_shape in ("octagon", "arrow"):
            face_shape = "rounded_rect"
        if graphic_style == "street_name":
            graphic_style = "shop"
    elif sign_type == "wall_plaque":
        if face_shape == "arrow":
            face_shape = "rectangle"
        if graphic_style == "warning":
            graphic_style = "notice"
    elif sign_type == "table_tent":
        if face_shape not in ("rectangle", "rounded_rect"):
            face_shape = "rectangle"
        if graphic_style == "warning":
            graphic_style = "notice"

    n = int(cfg.knuckle_count) if cfg.knuckle_count is not None else 3
    n = int(_clamp(n, N_MIN, N_MAX))

    tether_on = bool(cfg.tether_chain_enabled) if cfg.tether_chain_enabled is not None else False
    m = int(cfg.tether_link_count) if cfg.tether_link_count is not None else 4
    m = int(_clamp(m, M_MIN, M_MAX))

    # --- Compatibility gating (spec). ---
    # (1) shield bottom tapers to a point -> no seat for full-width outrigger
    #     feet; degrade to flush_slab.
    if profile == "shield" and base == "corner_feet":
        base = "flush_slab"
    # (2) swing_up_bail + tether_chain mutually exclusive (two new joint chains).
    if handle == "swing_up_bail":
        tether_on = False

    width = _PANEL_WIDTH * _clamp(cfg.panel_width_scale, 0.92, 1.12)
    height = _PANEL_HEIGHT * _clamp(cfg.panel_height_scale, 0.92, 1.10)
    apex_half_open = _clamp(cfg.apex_half_open, 0.12, 0.22)
    foot_spread = _FOOT_SPREAD_Y * _clamp(cfg.foot_spread_scale, 0.85, 1.20)

    # --- knuckle_band_len (equation): N barrels + gaps must fit in the apex
    # top span. The trapezoid top is narrow, the others reach (near) full width.
    if profile == "trapezoidal_tapered":
        apex_span = 2.0 * (max(0.060, (width / 2.0) * 0.42) - 0.006)
    else:
        apex_span = 2.0 * ((width / 2.0) - 0.004)
    usable = 0.95 * apex_span
    gap = 0.010
    band_len = _HINGE_BAND_LEN
    # total span = N*band_len + (N-1)*gap  <=  usable
    max_band = (usable - (n - 1) * gap) / n
    band_len = min(band_len, max_band)
    band_len = max(band_len, 0.010)  # never degenerate

    return ResolvedSignConfig(
        sign_type=sign_type,
        panel_profile=profile,
        base_support=base,
        handle_mechanism=handle,
        face_shape=face_shape,
        graphic_style=graphic_style,
        knuckle_count=n,
        tether_chain_enabled=tether_on,
        tether_link_count=m,
        palette_style=palette_style,
        panel_width=width,
        panel_height=height,
        panel_thick=_PANEL_THICK,
        apex_half_open=apex_half_open,
        knuckle_band_len=band_len,
        foot_spread=foot_spread,
        # Folding closed = rotating the back leaf from its rest +apex_half_open
        # tilt down to -apex_half_open (parallel with the front leaf); that is a
        # -2·apex_half_open swing about +Y.
        apex_lower=-2.0 * apex_half_open,
        apex_upper=_APEX_UPPER,
        name=cfg.name or "sign",
    )


def with_overrides(config: SignConfig, **kwargs: object) -> SignConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SignConfig | ResolvedSignConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSignConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("sign_type", r.sign_type),
        ("face_shape", r.face_shape),
        ("graphic_style", r.graphic_style),
        ("panel_profile", r.panel_profile),
        ("base_support", r.base_support),
        ("handle_mechanism", r.handle_mechanism),
        ("knuckle_count", f"n{r.knuckle_count}"),
    ]
    if r.tether_chain_enabled:
        choices.append(("tether_chain", f"m{r.tether_link_count}"))
    else:
        choices.append(("tether_chain", "off"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Profile geometry helpers (Slot A). Each preserves the source primitive type
# (threePointArc / polyline / pentagon / arc-chain), no Box/Cylinder downgrade.
# ---------------------------------------------------------------------------
def _top_arc_z(cy: float) -> float:
    """Top-edge Z of the rounded/shield/trapezoid arc at width offset cy."""
    return _ARC_CZ + math.sqrt(max(_ARC_R**2 - cy**2, 0.0))


def _gable_top_z(cy: float, half_w: float) -> float:
    """Top-edge Z of the gabled (pentagon) profile at width offset cy."""
    half_w_inset = half_w - _GABLE_INSET
    abs_y = abs(cy)
    if abs_y >= half_w_inset:
        return _GABLE_SHOULDER_Z
    t = abs_y / half_w_inset
    return _GABLE_PEAK_Z + t * (_GABLE_SHOULDER_Z - _GABLE_PEAK_Z)


def _profile_top_z(r: ResolvedSignConfig, cy: float) -> float:
    """Knuckle-seat Z function selected by the panel profile (conditional)."""
    if r.panel_profile == "gabled_peaked":
        return _gable_top_z(cy, r.panel_width / 2.0)
    if r.panel_profile == "trapezoidal_tapered":
        # Flat top edge (matches _trapezoid_profile_wire).
        return _TRAP_TOP_Z
    return _top_arc_z(cy)


def _apex_half_span(r: ResolvedSignConfig) -> float:
    """Half-width of the apex top edge where knuckles can seat on shell material.

    Rounded/gabled/shield top edges reach (near) the full panel width; the
    trapezoid top edge is narrow, so knuckles cluster within the narrow top.
    """
    half_w = r.panel_width / 2.0
    if r.panel_profile == "trapezoidal_tapered":
        return max(0.060, half_w * 0.42) - 0.006
    return half_w - 0.004


def _rounded_profile_wire(half_w: float, height: float) -> cq.Workplane:
    """Rounded-top profile (001 parent): flat base, straight sides, top arc."""
    return (
        cq.Workplane("YZ")
        .moveTo(-half_w, -height)
        .lineTo(half_w, -height)
        .lineTo(half_w, -0.045)
        .threePointArc((0.0, -0.005), (-half_w, -0.045))
        .close()
    )


_TRAP_TOP_Z = -0.006  # trapezoid top edge Z (near the pivot so knuckles seat)


def _trapezoid_profile_wire(half_w: float, height: float) -> cq.Workplane:
    """Straight tapered trapezoid (002 parent): wide base, narrow top edge."""
    half_top = max(0.060, half_w * 0.42)
    return (
        cq.Workplane("YZ")
        .moveTo(-half_w, -height)
        .lineTo(half_w, -height)
        .lineTo(half_top, _TRAP_TOP_Z)
        .lineTo(-half_top, _TRAP_TOP_Z)
        .close()
    )


def _gable_profile_wire(half_w: float, height: float) -> cq.Workplane:
    """Gabled pentagon (gabled variant): base + shoulders + centered peak."""
    half_w_inset = half_w - _GABLE_INSET
    return (
        cq.Workplane("YZ")
        .moveTo(-half_w, -height)
        .lineTo(half_w, -height)
        .lineTo(half_w_inset, _GABLE_SHOULDER_Z)
        .lineTo(0.0, _GABLE_PEAK_Z)
        .lineTo(-half_w_inset, _GABLE_SHOULDER_Z)
        .close()
    )


def _shield_profile_wire(half_w: float, height: float) -> cq.Workplane:
    """Heraldic shield (shield variant): top arc, straight sides, sweep to point."""
    z_straight = -height * _SHIELD_STRAIGHT_FRAC
    left_mid_1 = (-half_w * 0.92, z_straight - height * 0.10)
    left_mid_2 = (-half_w * 0.55, z_straight - height * 0.22)
    left_knee = (-half_w * 0.22, -height * 0.85)
    right_knee = (half_w * 0.22, -height * 0.85)
    right_mid_2 = (half_w * 0.55, z_straight - height * 0.22)
    right_mid_1 = (half_w * 0.92, z_straight - height * 0.10)
    return (
        cq.Workplane("YZ")
        .moveTo(half_w, -0.045)
        .threePointArc((0.0, -0.005), (-half_w, -0.045))
        .lineTo(-half_w, z_straight)
        .threePointArc(left_mid_1, left_mid_2)
        .threePointArc(left_knee, (0.0, -height))
        .threePointArc(right_knee, right_mid_2)
        .threePointArc(right_mid_1, (half_w, z_straight))
        .close()
    )


_PROFILE_WIRES = {
    "rounded_top": _rounded_profile_wire,
    "trapezoidal_tapered": _trapezoid_profile_wire,
    "gabled_peaked": _gable_profile_wire,
    "shield": _shield_profile_wire,
}


def _hand_hole_cut(r: ResolvedSignConfig, thick: float) -> cq.Workplane:
    """Profile-aware grab hand-hole that never severs the apex cap.

    The hole width is clamped to leave side margins inside the profile (the
    trapezoid top edge is narrow), and the hole TOP edge is dropped below the
    *lowest* profile top-edge Z over the hole's width minus a solid bridge
    margin. This guarantees a continuous band of material above the hole that
    keeps the apex top connected to the panel body -> one connected solid.
    """
    half_w = r.panel_width / 2.0
    # Max half-width that still leaves a side rim of material.
    if r.panel_profile == "trapezoidal_tapered":
        half_top = max(0.060, half_w * 0.42)
        max_half = half_top - 0.012
    else:
        max_half = half_w - 0.014
    hole_half = min(_HANDLE_OPENING_W / 2.0, r.panel_width * 0.55 / 2.0, max_half)
    hole_half = max(hole_half, 0.020)
    hole_w = 2.0 * hole_half

    # Lowest top-edge Z across the hole span (sampled) -> bridge above the hole.
    min_top = min(_profile_top_z(r, hole_half * (k / 8.0)) for k in range(-8, 9))
    bridge = 0.012
    hole_top = min_top - bridge
    hole_h = min(_HANDLE_OPENING_H, max(0.022, hole_top - (-r.panel_height * 0.50)))
    hole_center = hole_top - hole_h / 2.0
    return (
        cq.Workplane("YZ")
        .workplane(offset=-0.01)
        .center(0.0, hole_center)
        .rect(hole_w, hole_h)
        .extrude(thick + 0.02)
    )


def _panel_shell(r: ResolvedSignConfig, *, ribbed: bool, vented: bool) -> cq.Workplane:
    """A single molded sign leaf shell in the canonical apex frame.

    Apex line at z=0, hangs -Z, width along Y, front face +X, thickness +X.
    Hollow back, grab-handle hand-hole near the top, optional ribs (front) or
    vent slots (lower third). Both leaves use this helper -> identical profile.
    """
    half_w = r.panel_width / 2.0
    thick = r.panel_thick
    prof = _PROFILE_WIRES[r.panel_profile](half_w, r.panel_height).extrude(thick)

    # Hollow the back: keep the decorated front wall on +X, cut a cavity toward
    # -X. Cavity zone differs slightly per profile so it stays inside the rims.
    wall = 0.004
    if r.panel_profile == "shield":
        cavity_h = r.panel_height * 0.38
        cavity = (
            cq.Workplane("YZ")
            .workplane(offset=thick - wall)
            .moveTo(0.0, -(0.06 + cavity_h / 2.0))
            .rect(r.panel_width - 2 * wall, cavity_h)
            .extrude(-(thick - wall))
        )
    elif r.panel_profile == "gabled_peaked":
        cavity = (
            cq.Workplane("YZ")
            .workplane(offset=thick - wall)
            .center(0.0, -r.panel_height * 0.55)
            .rect(r.panel_width - 2 * wall, r.panel_height * 0.78)
            .extrude(-(thick - wall))
        )
    else:
        cavity = (
            cq.Workplane("YZ")
            .workplane(offset=thick - wall)
            .moveTo(0.0, -r.panel_height + wall)
            .rect(r.panel_width - 2 * wall, r.panel_height * 0.84)
            .extrude(-(thick - wall))
        )
    shell = prof.cut(cavity)

    # Grab-handle hand-hole near the apex (Slot C: fixed_grab_hole carves this).
    # The hole is placed and sized per profile so a continuous solid bridge of
    # material remains ABOVE it (between the hole top and the profile top edge).
    # Without that bridge the hole top pokes through the sloped/narrow top edge
    # of the gabled/trapezoid profiles and the apex cap floats off as its own
    # disconnected island (front_shell__component_002). See _hand_hole_cut.
    if r.handle_mechanism == "fixed_grab_hole":
        shell = shell.cut(_hand_hole_cut(r, thick))

    if ribbed:
        rib_z0 = -r.panel_height + 0.04
        rib_z1 = -r.panel_height * 0.42
        nribs = 7
        for i in range(nribs):
            zc = rib_z0 + (rib_z1 - rib_z0) * (i / (nribs - 1))
            rib = (
                cq.Workplane("XY")
                .transformed(offset=cq.Vector(thick, 0.0, zc))
                .box(0.006, r.panel_width * 0.80, 0.006, centered=(True, True, True))
            )
            shell = shell.union(rib)

    if vented:
        # Lower-third horizontal vent slots cut clean through (trapezoid source).
        for i in range(4):
            z = -r.panel_height + 0.085 + i * 0.030
            slot_w = r.panel_width * 0.55 - i * 0.012
            slot = (
                cq.Workplane("YZ")
                .workplane(offset=-0.01)
                .center(0.0, z)
                .rect(slot_w, 0.010)
                .extrude(thick + 0.02)
            )
            shell = shell.cut(slot)

    return shell


def _outrigger_foot(r: ResolvedSignConfig, corner_y: float) -> cq.Workplane:
    """One outrigger foot pad fused at a leaf bottom corner (Slot B corner_feet).

    Splays outward along Y, drops below the leaf bottom along -Z, thicker along
    X than the wall. Embeds into the leaf bottom/side for solid fusion.
    """
    splay = 1.0 if corner_y > 0 else -1.0
    spread = r.foot_spread
    cy = corner_y + splay * (spread / 2.0 - _FOOT_INSET_Y)
    cz = -r.panel_height - (_FOOT_DROP_Z - _FOOT_EMBED_Z) / 2.0
    cx = r.panel_thick / 2.0
    pad = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(cx, cy, cz))
        .box(_FOOT_THICK_X, spread, _FOOT_DROP_Z + _FOOT_EMBED_Z, centered=(True, True, True))
    )
    try:
        pad = pad.edges("|Z").fillet(0.003)
    except Exception:
        pass
    return pad


def _knuckle_barrel(r: ResolvedSignConfig, cy: float) -> cq.Workplane:
    """One Y-axis knuckle barrel seated on the apex top edge at width offset cy.

    Spans [cy-band/2, cy+band/2] along Y; centered on the pivot line (x=0) so it
    straddles BOTH leaves around the shared pin (front +X slab and back -X slab),
    capturing the back leaf. Seated a few mm below the local top edge.

    A short ``seat`` block is fused under the barrel spanning X across both apex
    slabs (front tilted -apex_half_open, back tilted +apex_half_open). The bare
    circular barrel sits on the pivot line at x=0, but after the per-leaf apex
    tilt the shell material near the top edge swings a few mm off x=0, leaving a
    ~2-4 mm gap so each barrel floated as its own disconnected island. The seat
    block reaches into both tilted slabs, fusing the knuckle into the panel
    solid uniformly for every knuckle and every knuckle_count.
    """
    band = r.knuckle_band_len
    top_z = _profile_top_z(r, cy)
    barrel_z = top_z - 0.004
    barrel = (
        cq.Workplane("XZ")
        .workplane(offset=-(cy - band / 2.0))
        .center(0.0, barrel_z)
        .circle(_HINGE_PIN_R)
        .extrude(-band)
    )
    # Seat block: wide enough in X to bite the tilted front (+X) and back (-X)
    # slabs, tall enough in Z to reach down into the shell bulk below the top
    # edge. Centered on the pivot line so it stays symmetric about the pin.
    seat_x = 2.0 * r.panel_thick + 0.004
    seat_z = 0.024
    seat_cz = barrel_z - seat_z * 0.30
    seat = (
        cq.Workplane("XY")
        .transformed(offset=cq.Vector(0.0, cy, seat_cz))
        .box(seat_x, band, seat_z, centered=(True, True, True))
    )
    return barrel.union(seat)


def _all_knuckles(r: ResolvedSignConfig) -> cq.Workplane:
    """Union of N knuckle barrels evenly/symmetrically along the apex top edge.

    Seated within the profile's apex top span (narrow for trapezoid, full for
    the others) so every barrel sits on real shell material at both leaves.
    """
    n = r.knuckle_count
    half_span = _apex_half_span(r)
    slot_w = (2.0 * half_span) / n
    bands = None
    for i in range(n):
        cy = -half_span + slot_w * (i + 0.5)
        b = _knuckle_barrel(r, cy)
        bands = b if bands is None else bands.union(b)
    return bands


def _hinge_barrel_bail_mount(r: ResolvedSignConfig) -> cq.Workplane:
    """Molded apex hinge barrel + saddle skirt + 2 pivot ears (swing_up_bail).

    Local frame centered on the apex line: barrel runs along Y at z=0; a skirt
    web below it reaches the two leaf top edges; two ear bosses on top carry the
    bail pivot. Authored in the canonical frame (barrel along +Y, thickness +X).
    """
    barrel = (
        cq.Workplane("XZ")
        .workplane(offset=(r.panel_width / 2.0 + 0.010))
        .circle(_HINGE_BARREL_R)
        .extrude(-(r.panel_width + 0.020))
    )
    # Saddle skirt under the barrel spanning the apex thickness (X).
    skirt_h = 0.026
    skirt = (
        cq.Workplane("XY")
        .box(2.0 * _PANEL_THICK + 0.018, r.panel_width + 0.006, skirt_h, centered=(True, True, False))
        .translate((r.panel_thick * 0.0, 0.0, -skirt_h))
        .edges("|Y")
        .fillet(0.005)
    )
    barrel = barrel.union(skirt)
    # Pivot ear bosses on top of the barrel at the bail pivot spacing (along Y).
    for i in range(2):
        sign = -1.0 + 2.0 * i
        ear = (
            cq.Workplane("XY")
            .circle(_PIVOT_EAR_R)
            .extrude(_PIVOT_EAR_H)
            .translate((0.0, sign * _BAIL_HALF_W, _HINGE_BARREL_R))
        )
        barrel = barrel.union(ear)
    return barrel


def _carry_bail():
    """Curved bail carry handle as a tubular spline arch (swing_up_bail).

    Legs sit at y = ±BAIL_HALF_W (the pivot spacing along the apex width); the
    arch sweeps through +X and rises in +Z. The bail rotates about the Y axis
    (the line through both pivot ears) to swing up over the apex. The
    handle_pivot frame is pre-rotated so q=0 folds the bail flat down.
    """
    hw = _BAIL_HALF_W
    ah = _BAIL_ARCH_H
    # Flat arch lying in -X at rest (legs at the pivot line z=0, arch sweeping out
    # toward -X). The handle_pivot (axis +Y) lifts this -X arch up to +Z as q
    # grows: rest pose folded flat, upper limit upright over the apex.
    points = [
        (0.0, -hw, 0.0),
        (-ah * 0.30, -hw, 0.012),
        (-ah * 0.70, -hw * 0.5, 0.018),
        (-ah * 0.92, 0.0, 0.020),
        (-ah * 0.70, hw * 0.5, 0.018),
        (-ah * 0.30, hw, 0.012),
        (0.0, hw, 0.0),
    ]
    arch = tube_from_spline_points(
        points,
        radius=_BAIL_BAR_R,
        samples_per_segment=14,
        radial_segments=14,
        cap_ends=True,
        up_hint=(0.0, 1.0, 0.0),
    )
    # Pivot rod through both legs along Y at the pivot line (z=0, x=0): guarantees
    # the bail geometry AABB straddles the child link origin (the joint origin),
    # satisfying the flat articulation-origin baseline, and ties the two legs.
    rod = tube_from_spline_points(
        [(0.0, -hw - 0.004, 0.0), (0.0, hw + 0.004, 0.0)],
        radius=_BAIL_BAR_R,
        samples_per_segment=2,
        radial_segments=12,
        cap_ends=True,
        up_hint=(1.0, 0.0, 0.0),
    )
    arch.merge(rod)
    return arch


def _chain_link() -> cq.Workplane:
    """One flat stadium chain link (tether), hanging DOWN from its top pivot.

    The chain dangles into the inter-leaf gap, so a link runs along -Z: top
    (near) pivot at the origin, bottom (far) pivot at ``(0, 0, -PITCH)``. The
    plate lies in the X-Z plane and is thin along Y (the pin direction); the pin
    holes are drilled along Y so the link hinges about +Y (perpendicular to the
    drop run) and can actually droop/flex.
    """
    half_w = _LINK_WIDTH / 2.0
    link_len = _PITCH + _LINK_WIDTH
    # X=thin (pin), Y drawn along width... build on XZ so the plate is X-Z, thin Y.
    body = (
        cq.Workplane("XZ")
        .box(_LINK_WIDTH, link_len, _LINK_THICK, centered=(True, True, True))
        .translate((0.0, 0.0, -_PITCH / 2.0))
        .edges("|Y")
        .fillet(half_w - 0.001)
    )
    hole_h = _LINK_THICK + 0.012
    hole_near = (
        cq.Workplane("XZ")
        .workplane(offset=-hole_h / 2.0)
        .moveTo(0.0, 0.0)
        .circle(_LINK_HOLE_R)
        .extrude(hole_h)
    )
    hole_far = (
        cq.Workplane("XZ")
        .workplane(offset=-hole_h / 2.0)
        .moveTo(0.0, -_PITCH)
        .circle(_LINK_HOLE_R)
        .extrude(hole_h)
    )
    return body.cut(hole_near).cut(hole_far)


def _anchor_pad() -> cq.Workplane:
    """Molded anchor bracket bridging the front shell wall to the stood-off chain.

    Built about the chain pivot (gap side): reaches +X to bite the front leaf
    inner shell wall (a solid fuse, no floating island) and -X to the chain top
    pivot, with a short -Z span so it meets the first hanging link.
    """
    pad_w = _LINK_WIDTH + 0.010
    span_x = _CHAIN_STANDOFF + 0.012
    # Centered so the box spans roughly [chain_x - 0.004, chain_x + standoff + 0.008].
    return (
        cq.Workplane("XY")
        .box(span_x, pad_w, 0.018, centered=(True, True, True))
        .translate((_CHAIN_STANDOFF / 2.0 + 0.002, 0.0, 0.0))
    )


# ---------------------------------------------------------------------------
# Placard / warning visuals (Rule 1: raised inline visuals on the front leaf).
# ---------------------------------------------------------------------------
def _emit_placard(
    part,
    r: ResolvedSignConfig,
    mats,
    *,
    tilt: Origin,
    base_x: float,
    out_dir: float,
    depth: float | None = None,
    suffix: str = "",
) -> None:
    """Emit the raised warning placard (hazard triangle + two text bands).

    Called for BOTH leaves (a real sandwich board warns front and back). ``base_x``
    is the mesh-X the extrusion starts from and ``out_dir`` (+1/-1) the raised
    direction. The front leaf's decorated wall is on +X so the front placard sits
    proud of +X with a thin depth. The back leaf's solid wall faces the gap (+X at
    x=0) while its outward face is -X; a shallow -X placard would float over the
    back cavity, so the back leaf passes an override ``depth`` that runs the visual
    through the wall from the (uniformly solid) +X face out past the -X face -> it
    stays FUSED to the wall (no floating island) yet shows proud on the rear.
    ``suffix`` keeps the two leaves' element names distinct.
    """
    tri_depth = 0.004 if depth is None else depth
    band_depth = 0.0035 if depth is None else depth
    # Hazard triangle -- apex points UP (single top vertex, flat bottom edge).
    radius = min(0.11, r.panel_width * 0.36) / 2.0
    tri = (
        cq.Workplane("YZ")
        .workplane(offset=base_x)
        .center(0.0, -r.panel_height * 0.42)
        .polyline(
            [
                (0.0, radius),
                (-radius * 0.866, -radius * 0.5),
                (radius * 0.866, -radius * 0.5),
            ]
        )
        .close()
        .extrude(tri_depth * out_dir)
    )
    part.visual(
        mesh_from_cadquery(tri, f"hazard_triangle{suffix}"),
        origin=tilt,
        material=mats["hazard"],
        name=f"hazard_triangle{suffix}", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    # Placard text bands.
    for idx, (zc, h) in enumerate([(-r.panel_height * 0.26, 0.050), (-r.panel_height * 0.62, 0.050)]):
        band = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, zc)
            .rect(r.panel_width * 0.70, h)
            .extrude(band_depth * out_dir)
        )
        part.visual(
            mesh_from_cadquery(band, f"text_band_{idx}{suffix}"),
            origin=tilt,
            material=mats["text"],
            name=f"text_band_{idx}{suffix}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


# ---------------------------------------------------------------------------
# Leaf builders.
# ---------------------------------------------------------------------------
def _build_front_leaf(model, r: ResolvedSignConfig, mats):
    front = model.part("front_panel")
    tilt = Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, -r.apex_half_open, 0.0))
    # trapezoid -> vented + ribbed; others -> ribbed only.
    vented = r.panel_profile == "trapezoidal_tapered"
    shell = _panel_shell(r, ribbed=True, vented=vented)
    front.visual(
        mesh_from_cadquery(shell, "front_shell"),
        origin=tilt,
        material=mats["shell"],
        name="front_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_placard(
        front, r, mats, tilt=tilt, base_x=r.panel_thick - 0.002, out_dir=1.0, suffix=""
    )

    if r.base_support == "corner_feet":
        for i, corner_y in enumerate((-r.panel_width / 2.0, r.panel_width / 2.0)):
            foot = _outrigger_foot(r, corner_y)
            front.visual(
                mesh_from_cadquery(foot, f"front_foot_{i}"),
                origin=tilt,
                material=mats["accent"],
                name=f"front_foot_{i}", material_class_id="rubber.smooth_plain",
            )

    # Knuckle barrels live on the front leaf at the apex (NOT tilted: the apex
    # frame is the part frame at z=0; the barrels straddle the pin line and
    # capture the back leaf). Inline visuals -> share the one apex_hinge joint.
    front.visual(
        mesh_from_cadquery(_all_knuckles(r), "hinge_knuckles"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hinge"],
        name="hinge_knuckles", material_class_id="metal.blackened_gunmetal",
    )

    front.inertial = Inertial.from_geometry(
        cq_bbox_box(r.panel_width, r.panel_thick, r.panel_height),
        mass=0.9,
        origin=Origin(xyz=(0.04, 0.0, -r.panel_height / 2.0)),
    )
    return front


def _build_back_leaf(model, r: ResolvedSignConfig, mats, front):
    back = model.part("back_panel")
    # Back leaf authored on the -X side of the pivot so its apex slab does not
    # share the pivot volume with the front leaf's +X apex slab.
    vented = r.panel_profile == "trapezoidal_tapered"
    shell = _panel_shell(r, ribbed=False, vented=vented).translate((-r.panel_thick, 0.0, 0.0))
    back_tilt = Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, r.apex_half_open, 0.0))
    back.visual(
        mesh_from_cadquery(shell, "back_shell"),
        origin=back_tilt,
        material=mats["back"],
        name="back_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # Warning placard on the back leaf's outward (-X) face too (real sandwich
    # boards warn both sides). The back shell's solid wall's +X face is uniformly
    # solid at x=0 (the -X face varies: full-thickness -0.018 vs -0.004 over the
    # cavity), so start the extrude just inside that +X face and run it THROUGH
    # the wall out past the -X face: fused to the wall (no floating island) and
    # proud on the rear.
    _emit_placard(
        back,
        r,
        mats,
        tilt=back_tilt,
        base_x=-0.001,
        out_dir=-1.0,
        depth=r.panel_thick + 0.003,
        suffix="_back",
    )
    if r.base_support == "corner_feet":
        for i, corner_y in enumerate((-r.panel_width / 2.0, r.panel_width / 2.0)):
            foot = _outrigger_foot(r, corner_y).translate((-r.panel_thick, 0.0, 0.0))
            back.visual(
                mesh_from_cadquery(foot, f"back_foot_{i}"),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, r.apex_half_open, 0.0)),
                material=mats["accent"],
                name=f"back_foot_{i}", material_class_id="rubber.smooth_plain",
            )
    back.inertial = Inertial.from_geometry(
        cq_bbox_box(r.panel_width, r.panel_thick, r.panel_height),
        mass=0.9,
        origin=Origin(xyz=(-0.04, 0.0, -r.panel_height / 2.0)),
    )
    # Apex hinge: REVOLUTE about +Y at z=0. Rest q=0 is the open A-frame; the
    # NEGATIVE range folds the back leaf toward the front (flat to store) and the
    # small POSITIVE range opens a touch wider (capped so the back leaf can never
    # sweep through the front-mounted carry bail).
    model.articulation(
        "apex_hinge",
        ArticulationType.REVOLUTE,
        parent=front,
        child=back,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=2.0, lower=r.apex_lower, upper=r.apex_upper
        ),
    )
    return back


def cq_bbox_box(w: float, t: float, h: float):
    from sdk import Box

    return Box((t * 2.6, w, h))


# ---------------------------------------------------------------------------
# Generic real-world sign families.
# ---------------------------------------------------------------------------
def _flat_face_plate(shape: FaceShape, width: float, height: float, thick: float) -> cq.Workplane:
    """Flat sign face in the YZ plane, front face toward +X."""
    half_w = width / 2.0
    half_h = height / 2.0
    if shape == "circle":
        radius = min(width, height) / 2.0
        plate = cq.Workplane("YZ").circle(radius).extrude(thick)
    elif shape == "octagon":
        r = min(width, height) / 2.0
        pts = []
        for i in range(8):
            a = math.pi / 8.0 + i * math.pi / 4.0
            pts.append((math.cos(a) * r, math.sin(a) * r))
        plate = cq.Workplane("YZ").polyline(pts).close().extrude(thick)
    elif shape == "arrow":
        pts = [
            (-half_w, -half_h * 0.55),
            (half_w * 0.28, -half_h * 0.55),
            (half_w * 0.28, -half_h),
            (half_w, 0.0),
            (half_w * 0.28, half_h),
            (half_w * 0.28, half_h * 0.55),
            (-half_w, half_h * 0.55),
        ]
        plate = cq.Workplane("YZ").polyline(pts).close().extrude(thick)
    else:
        plate = cq.Workplane("YZ").rect(width, height).extrude(thick)
        if shape == "rounded_rect":
            try:
                plate = plate.edges("|X").fillet(min(width, height) * 0.08)
            except Exception:
                pass
    return plate


def _generic_sign_dimensions(r: ResolvedSignConfig) -> tuple[float, float, float]:
    if r.sign_type == "roadside_post":
        return (0.42, 0.30, 0.010)
    if r.sign_type == "hanging_blade":
        return (0.34, 0.24, 0.009)
    if r.sign_type == "wall_plaque":
        return (0.38, 0.18, 0.008)
    if r.sign_type == "table_tent":
        return (0.26, 0.16, 0.004)
    return (0.32, 0.22, 0.008)


def _emit_generic_sign_graphics(
    part,
    r: ResolvedSignConfig,
    mats,
    *,
    width: float,
    height: float,
    base_x: float,
    origin: Origin,
    out_dir: float = 1.0,
    z_offset: float = 0.0,
    suffix: str = "",
) -> None:
    """Raised symbolic graphics that read like real sign printing without text."""
    style = r.graphic_style
    accent = mats["hazard"] if style == "warning" else mats["accent"]
    text = mats["text"]

    if style == "warning":
        radius = min(width, height) * 0.18
        tri = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, height * 0.12 + z_offset)
            .polyline([(0.0, radius), (-radius * 0.866, -radius * 0.5), (radius * 0.866, -radius * 0.5)])
            .close()
            .extrude(0.003 * out_dir)
        )
        part.visual(mesh_from_cadquery(tri, f"warning_symbol{suffix}"), origin=origin, material=accent, name=f"warning_symbol{suffix}", appearance_only=AppearanceOnlySpec(kind="overlay"))
    elif style == "wayfinding":
        aw = width * 0.46
        ah = height * 0.22
        arrow = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .polyline(
                [
                    (-aw / 2.0, z_offset - ah * 0.35),
                    (aw * 0.15, z_offset - ah * 0.35),
                    (aw * 0.15, z_offset - ah * 0.65),
                    (aw / 2.0, z_offset),
                    (aw * 0.15, z_offset + ah * 0.65),
                    (aw * 0.15, z_offset + ah * 0.35),
                    (-aw / 2.0, z_offset + ah * 0.35),
                ]
            )
            .close()
            .extrude(0.003 * out_dir)
        )
        part.visual(mesh_from_cadquery(arrow, f"direction_arrow{suffix}"), origin=origin, material=accent, name=f"direction_arrow{suffix}", appearance_only=AppearanceOnlySpec(kind="overlay"))
    elif style == "shop":
        oval = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, z_offset)
            .ellipse(width * 0.24, height * 0.18)
            .extrude(0.003 * out_dir)
        )
        part.visual(mesh_from_cadquery(oval, f"shop_mark{suffix}"), origin=origin, material=accent, name=f"shop_mark{suffix}", appearance_only=AppearanceOnlySpec(kind="overlay"))

    if style == "street_name":
        bands = [(-height * 0.12, height * 0.18), (height * 0.13, height * 0.12)]
    elif style == "notice":
        bands = [(height * 0.16, height * 0.11), (0.0, height * 0.08), (-height * 0.15, height * 0.08)]
    else:
        bands = [(-height * 0.22, height * 0.08), (-height * 0.34, height * 0.055)]
    for idx, (zc, band_h) in enumerate(bands):
        band = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, zc + z_offset)
            .rect(width * 0.62, band_h)
            .extrude(0.0025 * out_dir)
        )
        part.visual(mesh_from_cadquery(band, f"legend_band_{idx}{suffix}"), origin=origin, material=text, name=f"legend_band_{idx}{suffix}", appearance_only=AppearanceOnlySpec(kind="overlay"))


def _add_screw_caps(part, mats, *, width: float, height: float, base_x: float, origin: Origin) -> None:
    screw_y = min(width * 0.38, min(width, height) * 0.28)
    screw_z = min(height * 0.34, min(width, height) * 0.28)
    for idx, (y, z) in enumerate(
        [
            (-screw_y, screw_z),
            (screw_y, screw_z),
            (-screw_y, -screw_z),
            (screw_y, -screw_z),
        ]
    ):
        cap = cq.Workplane("YZ").workplane(offset=base_x).center(y, z).circle(0.010).extrude(0.003)
        part.visual(mesh_from_cadquery(cap, f"screw_cap_{idx}"), origin=origin, material=mats["hinge"], name=f"screw_cap_{idx}", material_class_id="metal.paint_coated")


def _emit_table_tent_graphics(
    part,
    r: ResolvedSignConfig,
    mats,
    *,
    width: float,
    height: float,
    thick: float,
    origin: Origin,
    suffix: str = "",
) -> None:
    """One connected ink/relief patch for folded table tents."""
    z0 = -height / 2.0
    base_x = -thick * 1.25
    depth = thick * 2.5
    graphic = (
        cq.Workplane("YZ")
        .workplane(offset=base_x)
        .center(0.0, z0 - height * 0.05)
        .rect(width * 0.045, height * 0.56)
        .extrude(depth)
    )
    name = f"legend_band_0{suffix}"
    material = mats["text"]

    if r.graphic_style == "warning":
        rad = min(width, height) * 0.16
        symbol = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, z0 + height * 0.14)
            .polyline([(0.0, rad), (-rad * 0.866, -rad * 0.5), (rad * 0.866, -rad * 0.5)])
            .close()
            .extrude(depth)
        )
        graphic = graphic.union(symbol)
        name = f"warning_symbol{suffix}"
        material = mats["hazard"]
    elif r.graphic_style == "wayfinding":
        aw = width * 0.44
        ah = height * 0.20
        arrow_z = z0 + height * 0.08
        arrow = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .polyline(
                [
                    (-aw / 2.0, arrow_z - ah * 0.35),
                    (aw * 0.15, arrow_z - ah * 0.35),
                    (aw * 0.15, arrow_z - ah * 0.65),
                    (aw / 2.0, arrow_z),
                    (aw * 0.15, arrow_z + ah * 0.65),
                    (aw * 0.15, arrow_z + ah * 0.35),
                    (-aw / 2.0, arrow_z + ah * 0.35),
                ]
            )
            .close()
            .extrude(depth)
        )
        graphic = graphic.union(arrow)
        name = f"direction_arrow{suffix}"
        material = mats["accent"]
    elif r.graphic_style == "shop":
        mark = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, z0 + height * 0.12)
            .ellipse(width * 0.22, height * 0.16)
            .extrude(depth)
        )
        graphic = graphic.union(mark)
        name = f"shop_mark{suffix}"
        material = mats["accent"]

    if r.graphic_style == "street_name":
        bands = [(z0 + height * 0.08, height * 0.14), (z0 - height * 0.10, height * 0.10)]
    elif r.graphic_style == "notice":
        bands = [
            (z0 + height * 0.13, height * 0.10),
            (z0 - height * 0.02, height * 0.075),
            (z0 - height * 0.16, height * 0.075),
        ]
    else:
        bands = [(z0 - height * 0.18, height * 0.075), (z0 - height * 0.30, height * 0.055)]
    for zc, band_h in bands:
        band = (
            cq.Workplane("YZ")
            .workplane(offset=base_x)
            .center(0.0, zc)
            .rect(width * 0.60, band_h)
            .extrude(depth)
        )
        graphic = graphic.union(band)

    part.visual(mesh_from_cadquery(graphic, name), origin=origin, material=material, name=name, appearance_only=AppearanceOnlySpec(kind="overlay"))


def _build_roadside_post_sign(model, r: ResolvedSignConfig, mats) -> None:
    width, height, thick = _generic_sign_dimensions(r)
    post = model.part("post")
    pole_h = 0.92
    pole = cq.Workplane("XY").circle(0.018).extrude(pole_h).translate((-0.035, 0.0, 0.0))
    post.visual(mesh_from_cadquery(pole, "galvanized_post"), material=mats["hinge"], name="galvanized_post", material_class_id="metal.steel_galvanized")
    post.inertial = Inertial.from_geometry(cq_bbox_box(0.05, 0.05, pole_h), mass=1.2, origin=Origin(xyz=(-0.035, 0.0, pole_h / 2.0)))

    face = model.part("sign_face")
    plate = _flat_face_plate(r.face_shape, width, height, thick).translate((0.0, 0.0, 0.0))
    face.visual(mesh_from_cadquery(plate, "sign_plate"), material=mats["shell"], name="sign_plate", material_class_id="metal.paint_coated")
    for idx, zc in enumerate((-height * 0.22, height * 0.22)):
        rail = cq.Workplane("XY").box(0.024, width * 0.82, 0.016, centered=(True, True, True)).translate((-0.004, 0.0, zc))
        face.visual(mesh_from_cadquery(rail, f"back_rail_{idx}"), material=mats["hinge"], name=f"back_rail_{idx}", material_class_id="metal.steel_galvanized")
    _emit_generic_sign_graphics(face, r, mats, width=width, height=height, base_x=thick - 0.0010, origin=Origin())
    face.inertial = Inertial.from_geometry(cq_bbox_box(width, thick, height), mass=0.5, origin=Origin())
    model.articulation(
        "post_swivel",
        ArticulationType.REVOLUTE,
        parent=post,
        child=face,
        origin=Origin(xyz=(-0.017, 0.0, 0.80)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=-0.20, upper=0.20),
    )


def _build_hanging_blade_sign(model, r: ResolvedSignConfig, mats) -> None:
    width, height, thick = _generic_sign_dimensions(r)
    bracket = model.part("wall_bracket")
    wall = cq.Workplane("XY").box(0.018, 0.16, 0.42, centered=(True, True, True)).translate((-0.030, 0.0, 0.36))
    arm = cq.Workplane("XY").box(0.26, 0.016, 0.016, centered=(True, True, True)).translate((0.085, 0.0, 0.55))
    rod = cq.Workplane("XY").box(0.014, width * 0.78, 0.014, centered=(True, True, True)).translate((0.18, 0.0, 0.542))
    bracket.visual(mesh_from_cadquery(wall.union(arm).union(rod), "wall_arm_bracket"), material=mats["hinge"], name="wall_arm_bracket", material_class_id="metal.paint_coated")
    bracket.inertial = Inertial.from_geometry(cq_bbox_box(0.20, 0.06, 0.44), mass=0.7, origin=Origin(xyz=(0.04, 0.0, 0.42)))

    panel = model.part("hanging_panel")
    panel_origin = Origin(xyz=(0.0, 0.0, -height * 0.50))
    plate = _flat_face_plate(r.face_shape, width, height, thick)
    panel.visual(mesh_from_cadquery(plate, "hanging_sign_plate"), origin=panel_origin, material=mats["shell"], name="hanging_sign_plate", material_class_id="metal.paint_coated")
    for idx, y in enumerate((-width * 0.32, width * 0.32)):
        loop = cq.Workplane("XY").box(0.012, 0.024, 0.050, centered=(True, True, True)).translate((0.0, y, 0.000))
        panel.visual(mesh_from_cadquery(loop, f"hanger_loop_{idx}"), material=mats["hinge"], name=f"hanger_loop_{idx}", material_class_id="metal.paint_coated")
    top_bar = cq.Workplane("XY").box(0.012, width * 0.78, 0.012, centered=(True, True, True))
    panel.visual(mesh_from_cadquery(top_bar, "top_hanger_bar"), material=mats["hinge"], name="top_hanger_bar", material_class_id="metal.paint_coated")
    _emit_generic_sign_graphics(panel, r, mats, width=width, height=height, base_x=thick - 0.0010, origin=panel_origin)
    panel.inertial = Inertial.from_geometry(cq_bbox_box(width, thick, height), mass=0.35, origin=Origin(xyz=(0.0, 0.0, -height * 0.50)))
    model.articulation(
        "hanging_swing",
        ArticulationType.REVOLUTE,
        parent=bracket,
        child=panel,
        origin=Origin(xyz=(0.18, 0.0, 0.53)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=1.0, lower=-0.28, upper=0.28),
    )


def _build_wall_plaque_sign(model, r: ResolvedSignConfig, mats) -> None:
    width, height, thick = _generic_sign_dimensions(r)
    mount = model.part("wall_mount")
    backplate = (
        cq.Workplane("YZ")
        .workplane(offset=-0.035)
        .center(width * 0.50, 0.0)
        .rect(width + 0.020, height + 0.030)
        .extrude(0.006)
    )
    hinge_pin = (
        cq.Workplane("XY")
        .circle(0.006)
        .extrude(height + 0.030)
        .translate((0.0, 0.0, -(height + 0.030) / 2.0))
    )
    hinge_bridge = (
        cq.Workplane("XY")
        .box(0.050, 0.020, height + 0.020, centered=(True, True, True))
        .translate((-0.014, 0.0, 0.0))
    )
    mount.visual(
        mesh_from_cadquery(backplate.union(hinge_bridge).union(hinge_pin), "wall_backplate_hinge"),
        material=mats["hinge"],
        name="wall_backplate_hinge", material_class_id="metal.paint_coated",
    )
    mount.inertial = Inertial.from_geometry(
        cq_bbox_box(width, 0.020, height),
        mass=0.25,
        origin=Origin(xyz=(-0.010, width * 0.45, 0.0)),
    )

    plaque = model.part("wall_plaque")
    plate = _flat_face_plate(r.face_shape, width, height, thick).translate((0.0, width * 0.50, 0.0))
    if r.face_shape in ("circle", "octagon"):
        left_edge_y = width * 0.50 - min(width, height) * 0.50
    else:
        left_edge_y = 0.0
    hinge_leaf_span_y = max(0.026, left_edge_y + 0.030)
    hinge_leaf = (
        cq.Workplane("XY")
        .box(thick + 0.014, hinge_leaf_span_y, height * 0.88, centered=(True, True, True))
        .translate((0.0, hinge_leaf_span_y / 2.0 - 0.006, 0.0))
    )
    hinge_barrel = (
        cq.Workplane("XY")
        .circle(0.007)
        .extrude(height * 0.96)
        .translate((0.0, 0.0, -height * 0.48))
    )
    plaque.visual(mesh_from_cadquery(plate, "plaque_plate"), material=mats["shell"], name="plaque_plate", material_class_id="metal.paint_coated")
    plaque.visual(
        mesh_from_cadquery(hinge_leaf.union(hinge_barrel), "plaque_hinge_leaf"),
        material=mats["hinge"],
        name="plaque_hinge_leaf", material_class_id="metal.paint_coated",
    )
    plaque_origin = Origin(xyz=(0.0, width * 0.50, 0.0))
    _emit_generic_sign_graphics(
        plaque, r, mats, width=width, height=height, base_x=thick - 0.0010, origin=plaque_origin
    )
    _add_screw_caps(
        plaque, mats, width=width, height=height, base_x=thick - 0.0015, origin=plaque_origin
    )
    plaque.inertial = Inertial.from_geometry(
        cq_bbox_box(width, thick, height),
        mass=0.28,
        origin=Origin(xyz=(0.0, width * 0.50, 0.0)),
    )
    model.articulation(
        "plaque_hinge",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=plaque,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.2, lower=0.0, upper=1.20),
    )


def _build_table_tent_sign(model, r: ResolvedSignConfig, mats) -> None:
    width, height, thick = _generic_sign_dimensions(r)
    half_open = 0.34
    front = model.part("front_tent_panel")
    back = model.part("back_tent_panel")
    panel = _flat_face_plate(r.face_shape, width, height, thick).translate((0.0, 0.0, -height / 2.0))
    front_tilt = Origin(rpy=(0.0, -half_open, 0.0))
    back_tilt = Origin(rpy=(0.0, half_open, 0.0))
    front.visual(
        mesh_from_cadquery(panel, "front_tent_plate"),
        origin=front_tilt,
        material=mats["shell"],
        name="front_tent_plate", material_class_id="paper.cardboard",
    )
    back.visual(
        mesh_from_cadquery(panel.translate((-thick, 0.0, 0.0)), "back_tent_plate"),
        origin=back_tilt,
        material=mats["back"],
        name="back_tent_plate", material_class_id="paper.cardboard",
    )
    crease = cq.Workplane("XY").box(thick * 14.0, width, 0.020, centered=(True, True, True)).translate((0.0, 0.0, -0.006))
    front.visual(mesh_from_cadquery(crease, "folded_top_crease"), material=mats["hinge"], name="folded_top_crease", material_class_id="paper.cardboard")
    _emit_table_tent_graphics(front, r, mats, width=width, height=height, thick=thick, origin=front_tilt)
    _emit_table_tent_graphics(
        back, r, mats, width=width, height=height, thick=thick, origin=back_tilt, suffix="_back"
    )
    front.inertial = Inertial.from_geometry(
        cq_bbox_box(width, thick * 5.0, height),
        mass=0.11,
        origin=Origin(xyz=(0.0, 0.0, -height / 2.0)),
    )
    back.inertial = Inertial.from_geometry(
        cq_bbox_box(width, thick * 5.0, height),
        mass=0.11,
        origin=Origin(xyz=(0.0, 0.0, -height / 2.0)),
    )
    model.articulation(
        "tent_crease",
        ArticulationType.REVOLUTE,
        parent=front,
        child=back,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-2.0 * half_open, upper=0.18),
    )


# ---------------------------------------------------------------------------
# Handle (Slot C: swing_up_bail). fixed_grab_hole is the carved hand-hole
# above (no extra part / joint).
# ---------------------------------------------------------------------------
def _build_swing_up_bail(model, r: ResolvedSignConfig, mats, front) -> list[str]:
    hinge = model.part("hinge_barrel")
    hinge.visual(
        mesh_from_cadquery(_hinge_barrel_bail_mount(r), "hinge_barrel"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hinge"],
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    hinge.inertial = Inertial.from_geometry(
        cq_bbox_box(r.panel_width, _HINGE_BARREL_R, 0.05),
        mass=0.08,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # Hinge barrel rigidly fixed to the front leaf top edge (one molded piece).
    model.articulation(
        "front_to_hinge",
        ArticulationType.FIXED,
        parent=front,
        child=hinge,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    carry = model.part("carry_handle")
    carry.visual(
        mesh_from_geometry(_carry_bail(), "carry_bail"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hinge"],
        name="carry_bail", material_class_id="metal.blackened_gunmetal",
    )
    carry.inertial = Inertial.from_geometry(
        cq_bbox_box(2.0 * _BAIL_HALF_W, _BAIL_BAR_R, _BAIL_ARCH_H),
        mass=0.04,
        origin=Origin(xyz=(0.0, 0.0, _BAIL_ARCH_H / 2.0)),
    )
    # Bail pivots on the ear bosses on top of the barrel. The pivot axis is Y
    # (the line through both ears, parallel to the apex width). The bail arch is
    # authored flat in -X at rest; positive q (axis +Y) lifts the -X arch up to
    # +Z, so q=0 is folded flat and the upper limit is upright over the apex.
    pivot_z = _HINGE_BARREL_R + _PIVOT_EAR_H
    model.articulation(
        "handle_pivot",
        ArticulationType.REVOLUTE,
        parent=hinge,
        child=carry,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=2.0, lower=0.0, upper=math.pi / 2.0 + 0.08
        ),
    )
    return ["hinge_barrel", "carry_handle"]


# ---------------------------------------------------------------------------
# Tether spreader chain (optional multiplicity axis).
# ---------------------------------------------------------------------------
def _tether_anchor_points(r: ResolvedSignConfig):
    """Return the front anchor xyz (chain pivot) in the FRONT part frame.

    The chain runs along +X (the inter-leaf gap direction). The front anchor sits
    on the front leaf inner (back) face, which lies at mesh x = thick - wall (the
    back wall of the hollowed front shell) before the apex tilt. The front visual
    is tilted by ``-apex_half_open`` about Y, so a mesh point ``(x, z)`` maps to
    the part frame as::

        x' =  x*cos(a) - z*sin(a)
        z' =  x*sin(a) + z*cos(a)

    Anchoring at the real inner-face x (not x=0) and using the correct rotation
    sign keeps the anchor pad ON the tilted shell -> no floating island.
    """
    cos_a = math.cos(r.apex_half_open)
    sin_a = math.sin(r.apex_half_open)
    z_mesh = -r.panel_height * _STRAP_HT_FRAC
    x_inner_mesh = r.panel_thick - 0.004  # inner (back) wall of the hollow shell
    anchor_x = x_inner_mesh * cos_a - z_mesh * sin_a
    anchor_z = x_inner_mesh * sin_a + z_mesh * cos_a
    return (anchor_x, 0.0, anchor_z)


def _build_tether_chain(model, r: ResolvedSignConfig, mats, front, back) -> list[str]:
    face = _tether_anchor_points(r)
    # Stand the chain pivot off the front inner face into the gap so the link body
    # clears the front shell wall (see _CHAIN_STANDOFF).
    anchor = (face[0] - _CHAIN_STANDOFF, 0.0, face[2])
    # Anchor bracket bridges the front shell wall to the stood-off chain pivot.
    front.visual(
        mesh_from_cadquery(_anchor_pad(), "front_anchor_pad"),
        origin=Origin(xyz=(anchor[0], 0.0, anchor[2])),
        material=mats["accent"],
        name="front_anchor_pad", material_class_id="metal.paint_coated",
    )
    names: list[str] = []
    links = []
    for i in range(r.tether_link_count):
        link = model.part(f"link_{i}")
        link.visual(
            mesh_from_cadquery(_chain_link(), f"link_{i}"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["accent"],
            name=f"link_{i}_body", material_class_id="metal.paint_coated",
        )
        link.inertial = Inertial.from_geometry(
            cq_bbox_box(_LINK_WIDTH, _LINK_THICK, _PITCH + _LINK_WIDTH),
            mass=0.01,
            origin=Origin(xyz=(0.0, 0.0, -_PITCH / 2.0)),
        )
        links.append(link)
        names.append(f"link_{i}")

    # Chain dangles from the front leaf into the inter-leaf gap and hangs -Z; each
    # link pivots about +Y (perpendicular to the drop) so the chain droops/flexes.
    model.articulation(
        "front_to_link_0",
        ArticulationType.REVOLUTE,
        parent=front,
        child=links[0],
        origin=Origin(xyz=anchor),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=2.0, lower=-_CHAIN_FWD, upper=_CHAIN_DROOP
        ),
    )
    for i in range(r.tether_link_count - 1):
        model.articulation(
            f"link_{i}_to_link_{i + 1}",
            ArticulationType.REVOLUTE,
            parent=links[i],
            child=links[i + 1],
            origin=Origin(xyz=(0.0, 0.0, -_PITCH)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=2.0, lower=-_CHAIN_FWD, upper=_CHAIN_DROOP
            ),
        )
    return names


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_sign(
    config: SignConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"sign_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in _PALETTES[r.palette_style].items()
    }

    if r.sign_type == "roadside_post":
        _build_roadside_post_sign(model, r, mats)
        model.meta["slot_choices"] = slot_choices_for_config(r)
        return model
    if r.sign_type == "hanging_blade":
        _build_hanging_blade_sign(model, r, mats)
        model.meta["slot_choices"] = slot_choices_for_config(r)
        return model
    if r.sign_type == "wall_plaque":
        _build_wall_plaque_sign(model, r, mats)
        model.meta["slot_choices"] = slot_choices_for_config(r)
        return model
    if r.sign_type == "table_tent":
        _build_table_tent_sign(model, r, mats)
        model.meta["slot_choices"] = slot_choices_for_config(r)
        return model

    front = _build_front_leaf(model, r, mats)
    back = _build_back_leaf(model, r, mats, front)

    if r.handle_mechanism == "swing_up_bail":
        _build_swing_up_bail(model, r, mats, front)
    if r.tether_chain_enabled:
        _build_tether_chain(model, r, mats, front, back)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_sign(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_sign(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _run_general_sign_tests(
    object_model: ArticulatedObject,
    r: ResolvedSignConfig,
) -> TestReport:
    ctx = TestContext(object_model)

    if r.sign_type == "roadside_post":
        post = object_model.get_part("post")
        face = object_model.get_part("sign_face")
        ctx.allow_overlap(
            post,
            face,
            elem_a="galvanized_post",
            elem_b="back_rail_0",
            reason="Road-sign back rails are clamped against the support post.",
        )
        ctx.allow_overlap(
            post,
            face,
            elem_a="galvanized_post",
            elem_b="back_rail_1",
            reason="Road-sign back rails are clamped against the support post.",
        )
    elif r.sign_type == "hanging_blade":
        bracket = object_model.get_part("wall_bracket")
        panel = object_model.get_part("hanging_panel")
        ctx.allow_overlap(
            bracket,
            panel,
            elem_a="wall_arm_bracket",
            elem_b="top_hanger_bar",
            reason="The hanging panel top bar rides on the bracket rod at the swing pivot.",
        )
        for i in range(2):
            ctx.allow_overlap(
                bracket,
                panel,
                elem_a="wall_arm_bracket",
                elem_b=f"hanger_loop_{i}",
                reason="Hanger loops wrap over the bracket arm at the swing pivot.",
            )
    elif r.sign_type == "wall_plaque":
        mount = object_model.get_part("wall_mount")
        plaque = object_model.get_part("wall_plaque")
        ctx.allow_overlap(
            mount,
            plaque,
            elem_a="wall_backplate_hinge",
            elem_b="plaque_hinge_leaf",
            reason="The plaque hinge leaf shares the hinge pin carried by the wall backplate.",
        )
        ctx.allow_overlap(
            mount,
            plaque,
            elem_a="wall_backplate_hinge",
            elem_b="plaque_plate",
            reason="The wall hinge leaf is fastened through the plaque's hinged edge.",
        )
    elif r.sign_type == "table_tent":
        front = object_model.get_part("front_tent_panel")
        back = object_model.get_part("back_tent_panel")
        ctx.allow_overlap(
            front,
            back,
            elem_a="folded_top_crease",
            elem_b="back_tent_plate",
            reason="The two tent panels meet at the folded top crease.",
        )
        for name in ("warning_symbol", "direction_arrow", "shop_mark"):
            ctx.allow_overlap(
                front,
                back,
                elem_a=name,
                elem_b=f"{name}_back",
                reason="Table-tent printed/raised ink layers are visual graphics, not structural collision parts.",
            )
        for idx in range(3):
            ctx.allow_overlap(
                front,
                back,
                elem_a=f"legend_band_{idx}",
                elem_b=f"legend_band_{idx}_back",
                reason="Table-tent printed/raised ink layers are visual graphics, not structural collision parts.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    ctx.check(
        "slot_choices record real sign family",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    nonfixed_joints = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "every sign seed has at least one real moving joint",
        len(nonfixed_joints) >= 1,
        details=str([a.name for a in nonfixed_joints]),
    )

    if r.sign_type == "roadside_post":
        post = object_model.get_part("post")
        face = object_model.get_part("sign_face")
        swivel = object_model.get_articulation("post_swivel")
        post_aabb = ctx.part_world_aabb(post)
        face_aabb = ctx.part_world_aabb(face)
        ctx.check("roadside sign has a post", post.get_visual("galvanized_post") is not None)
        ctx.check("roadside sign has a mounted plate", face.get_visual("sign_plate") is not None)
        ctx.check(
            "roadside plate swivels on an adjustable post bracket",
            swivel.articulation_type == ArticulationType.REVOLUTE and abs(swivel.axis[2]) > 0.99,
            details=f"type={swivel.articulation_type} axis={tuple(swivel.axis)}",
        )
        rest = ctx.part_world_aabb(face)
        with ctx.pose({swivel: swivel.motion_limits.upper}):
            swung = ctx.part_world_aabb(face)
        if rest is not None and swung is not None:
            ctx.check(
                "post swivel changes the sign face footprint",
                abs(swung[0][0] - rest[0][0]) > 0.010 or abs(swung[0][1] - rest[0][1]) > 0.010,
                details=f"rest={rest} swung={swung}",
            )
        if post_aabb is not None and face_aabb is not None:
            ctx.check(
                "roadside sign plate is mounted above the post base",
                face_aabb[0][2] > post_aabb[0][2] + 0.45,
                details=f"face_bottom={face_aabb[0][2]:.3f} post_base={post_aabb[0][2]:.3f}",
            )
            ctx.check(
                "roadside sign reads as a broad thin panel",
                (face_aabb[1][1] - face_aabb[0][1]) > 0.24
                and (face_aabb[1][0] - face_aabb[0][0]) < 0.08,
                details=f"aabb={face_aabb}",
            )
        ctx.check(
            "roadside sign has rear mounting rails",
            face.get_visual("back_rail_0") is not None and face.get_visual("back_rail_1") is not None,
        )

    elif r.sign_type == "hanging_blade":
        bracket = object_model.get_part("wall_bracket")
        panel = object_model.get_part("hanging_panel")
        swing = object_model.get_articulation("hanging_swing")
        ctx.check("hanging sign has a wall arm bracket", bracket.get_visual("wall_arm_bracket") is not None)
        ctx.check("hanging sign has a blade panel", panel.get_visual("hanging_sign_plate") is not None)
        ctx.check(
            "hanging blade swings on a real pivot",
            swing.articulation_type == ArticulationType.REVOLUTE and abs(swing.axis[1]) > 0.99,
            details=f"type={swing.articulation_type} axis={tuple(swing.axis)}",
        )
        rest = ctx.part_world_aabb(panel)
        with ctx.pose({swing: swing.motion_limits.upper}):
            swung = ctx.part_world_aabb(panel)
        if rest is not None and swung is not None:
            ctx.check(
                "swinging the hanging sign changes its footprint",
                abs(swung[0][0] - rest[0][0]) > 0.010 or abs(swung[1][0] - rest[1][0]) > 0.010,
                details=f"rest={rest} swung={swung}",
            )
        ctx.check(
            "hanging panel has two hanger loops",
            panel.get_visual("hanger_loop_0") is not None and panel.get_visual("hanger_loop_1") is not None,
        )

    elif r.sign_type == "wall_plaque":
        mount = object_model.get_part("wall_mount")
        plaque = object_model.get_part("wall_plaque")
        hinge = object_model.get_articulation("plaque_hinge")
        aabb = ctx.part_world_aabb(plaque)
        ctx.check(
            "wall plaque has a wall-mounted hinge backplate",
            mount.get_visual("wall_backplate_hinge") is not None,
        )
        ctx.check("wall plaque is a single mounted plate", plaque.get_visual("plaque_plate") is not None)
        ctx.check(
            "wall plaque has visible screw caps",
            plaque.get_visual("screw_cap_0") is not None and plaque.get_visual("screw_cap_3") is not None,
        )
        ctx.check(
            "wall plaque opens on a side service hinge",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[2]) > 0.99,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        rest = ctx.part_world_aabb(plaque)
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            open_aabb = ctx.part_world_aabb(plaque)
        if rest is not None and open_aabb is not None:
            ctx.check(
                "plaque hinge swings the face open",
                abs(open_aabb[1][1] - rest[1][1]) > 0.050
                or abs(open_aabb[0][0] - rest[0][0]) > 0.030,
                details=f"rest={rest} open={open_aabb}",
            )
        if aabb is not None:
            ctx.check(
                "wall plaque is a shallow plate",
                (aabb[1][0] - aabb[0][0]) < 0.08,
                details=f"x_extent={aabb[1][0] - aabb[0][0]:.3f}",
            )

    elif r.sign_type == "table_tent":
        front = object_model.get_part("front_tent_panel")
        back = object_model.get_part("back_tent_panel")
        hinge = object_model.get_articulation("tent_crease")
        ctx.check("table tent has a front panel", front.get_visual("front_tent_plate") is not None)
        ctx.check("table tent has a back panel", back.get_visual("back_tent_plate") is not None)
        ctx.check("table tent has a folded top crease", front.get_visual("folded_top_crease") is not None)
        ctx.check(
            "table tent has a top crease hinge",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[1]) > 0.99,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        front_aabb = ctx.part_world_aabb(front)
        back_aabb = ctx.part_world_aabb(back)
        if front_aabb is not None and back_aabb is not None:
            ctx.check(
                "table tent is compact desk signage",
                (front_aabb[1][2] - front_aabb[0][2]) < 0.24
                and (front_aabb[1][1] - front_aabb[0][1]) < 0.32,
                details=f"front_aabb={front_aabb}",
            )
            ctx.check(
                "table tent panels form a shallow A profile",
                abs((front_aabb[0][0] + front_aabb[1][0]) - (back_aabb[0][0] + back_aabb[1][0])) > 0.010,
                details=f"front={front_aabb} back={back_aabb}",
            )
        rest = ctx.part_world_aabb(back)
        with ctx.pose({hinge: hinge.motion_limits.lower}):
            folded = ctx.part_world_aabb(back)
        if rest is not None and folded is not None:
            ctx.check(
                "tent crease folds the rear panel",
                abs(folded[1][0] - rest[1][0]) > 0.020,
                details=f"rest={rest} folded={folded}",
            )

    # All real sign families need a visible legend/symbol, not a bare slab.
    visual_names = {
        visual.name
        for part in object_model.parts
        for visual in getattr(part, "visuals", [])
    }
    ctx.check(
        "sign carries printed or raised sign information",
        any(
            name.startswith(("legend_band_", "warning_symbol", "direction_arrow", "shop_mark"))
            for name in visual_names
        ),
        details=str(sorted(visual_names)[:12]),
    )

    return ctx.report()


def run_sign_tests(
    object_model: ArticulatedObject,
    config: SignConfig,
) -> TestReport:
    r = resolve_config(config)
    if r.sign_type != "floor_caution_a_frame":
        return _run_general_sign_tests(object_model, r)

    ctx = TestContext(object_model)
    front = object_model.get_part("front_panel")
    back = object_model.get_part("back_panel")
    apex = object_model.get_articulation("apex_hinge")

    # ---- Captured-pin / molded allowances (element-scoped). ----
    ctx.allow_overlap(
        front,
        back,
        elem_a="hinge_knuckles",
        elem_b="back_shell",
        reason=(
            "Apex hinge knuckle barrels straddle the pin line and capture the "
            "back leaf at the shared hinge axis."
        ),
    )
    # The two leaf apex slabs may share the pivot region depending on profile.
    ctx.allow_overlap(
        front,
        back,
        elem_a="front_shell",
        elem_b="back_shell",
        reason="The two leaf apex slabs meet at the shared pivot line at rest.",
    )

    if r.base_support == "corner_feet":
        # Open-pose feet of the two leaves can splay toward each other near the
        # ground; allow the leaf-to-leaf foot overlaps.
        for i in range(2):
            ctx.allow_overlap(
                front,
                back,
                elem_a=f"front_foot_{i}",
                elem_b="back_shell",
                reason="Outrigger feet splay near the ground at the open A-frame footprint.",
            )

    if r.handle_mechanism == "swing_up_bail":
        hinge = object_model.get_part("hinge_barrel")
        carry = object_model.get_part("carry_handle")
        ctx.allow_overlap(
            hinge,
            front,
            elem_a="hinge_barrel",
            elem_b="front_shell",
            reason="Molded hinge barrel is one piece with the front leaf top edge.",
        )
        ctx.allow_overlap(
            hinge,
            back,
            elem_a="hinge_barrel",
            elem_b="back_shell",
            reason="Molded hinge barrel captures the back leaf top edge at the apex.",
        )
        ctx.allow_overlap(
            hinge,
            front,
            elem_a="hinge_barrel",
            elem_b="hinge_knuckles",
            reason="The bail hinge barrel shares the apex pin line with the knuckle barrels.",
        )
        ctx.allow_overlap(
            carry,
            hinge,
            elem_a="carry_bail",
            elem_b="hinge_barrel",
            reason="Bail handle pivots on the ear bosses; the tube embeds slightly at the pivot.",
        )

    if r.tether_chain_enabled:
        link0 = object_model.get_part("link_0")
        ctx.allow_overlap(
            front,
            link0,
            elem_a="front_anchor_pad",
            elem_b="link_0_body",
            reason="Chain link_0 pivot is anchored on the front leaf inner-face pad.",
        )
        # Adjacent chain links interlock at their shared pivot (captured-pin, no
        # MatingContract) -> allow the parent-child link overlaps along the chain.
        for i in range(r.tether_link_count - 1):
            ctx.allow_overlap(
                object_model.get_part(f"link_{i}"),
                object_model.get_part(f"link_{i + 1}"),
                elem_a=f"link_{i}_body",
                elem_b=f"link_{i + 1}_body",
                reason="Adjacent tether links interlock at the shared captured-pin pivot.",
            )
        # Folding the board flat to store sweeps the back leaf across the gap onto
        # the decorative dangle chain (a real, deliberate storing collapse). This
        # only occurs at the folded-closed apex extreme, never in the display pose.
        for i in range(r.tether_link_count):
            ctx.allow_overlap(
                back,
                object_model.get_part(f"link_{i}"),
                elem_a="back_shell",
                elem_b=f"link_{i}_body",
                reason="Folding the board flat to store collapses the back leaf onto the dangle chain.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    nonfixed_joints = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "every sign seed has at least one real moving joint",
        len(nonfixed_joints) >= 1,
        details=str([a.name for a in nonfixed_joints]),
    )

    # ---- Identity: apex fold is REVOLUTE about +Y, opens. ----
    ctx.check(
        "apex hinge is revolute",
        apex.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={apex.articulation_type}",
    )
    ax = tuple(round(a, 6) for a in apex.axis)
    ctx.check(
        "apex hinge axis is along Y (panel width)",
        abs(ax[1]) > 0.99 and abs(ax[0]) < 1e-3 and abs(ax[2]) < 1e-3,
        details=f"axis={ax}",
    )
    lim = apex.motion_limits
    ctx.check(
        "apex fold folds toward closed and opens to a capped A (rest q=0 is open)",
        lim is not None and lim.lower is not None and lim.upper is not None
        and lim.lower < -1e-6  # negative travel folds the leaves flat to store
        and lim.upper > 1e-6  # positive travel opens a touch wider
        and lim.upper <= 0.8  # ...but capped so it never sweeps the carry bail
        and (lim.upper - lim.lower) > 0.3,
        details=f"limits=({getattr(lim, 'lower', None)}, {getattr(lim, 'upper', None)})",
    )

    # ---- Hero parts present, floor-sign proportions. ----
    front_aabb = ctx.part_world_aabb(front)
    back_aabb = ctx.part_world_aabb(back)
    ctx.check("front leaf exists in world", front_aabb is not None)
    ctx.check("back leaf exists in world", back_aabb is not None)
    if front_aabb is not None:
        (fx0, fy0, fz0), (fx1, fy1, fz1) = front_aabb
        ctx.check(
            "front leaf is tall like a floor sign",
            (fz1 - fz0) > 0.45,
            details=f"height={fz1 - fz0:.3f}",
        )
        ctx.check(
            "front leaf spans the sign width",
            (fy1 - fy0) > 0.25,
            details=f"width={fy1 - fy0:.3f}",
        )
        ctx.check(
            "front leaf is a thin tilted shell, not a deep box",
            (fx1 - fx0) < 0.34,
            details=f"x_extent={fx1 - fx0:.3f}",
        )

    # ---- Warning placard + knuckles present (Rule 1 raised visuals). ----
    ctx.check("hinge knuckles visual present", front.get_visual("hinge_knuckles") is not None)
    ctx.check("hazard triangle visual present", front.get_visual("hazard_triangle") is not None)
    # Both leaves warn (real sandwich boards print front and back).
    ctx.check(
        "back leaf also carries a warning placard",
        back.get_visual("hazard_triangle_back") is not None
        and back.get_visual("text_band_0_back") is not None,
        details="back placard visuals missing",
    )

    # Knuckle count is encoded; barrels capture the back leaf.
    ctx.expect_contact(
        front,
        back,
        elem_a="hinge_knuckles",
        elem_b="back_shell",
        contact_tol=0.001,
        name="apex knuckles capture the back leaf at the hinge",
    )

    # ---- Both leaves share the same profile (identical silhouette). ----
    fsh = ctx.part_element_world_aabb(front, elem="front_shell")
    bsh = ctx.part_element_world_aabb(back, elem="back_shell")
    if fsh is not None and bsh is not None:
        f_dy = fsh[1][1] - fsh[0][1]
        b_dy = bsh[1][1] - bsh[0][1]
        ctx.check(
            "both leaves share the same profile width",
            abs(f_dy - b_dy) < 0.012,
            details=f"front_y={f_dy:.3f} back_y={b_dy:.3f}",
        )

    # ---- Base support topology. ----
    if r.base_support == "corner_feet":
        ctx.check(
            "front leaf has two outrigger feet",
            front.get_visual("front_foot_0") is not None
            and front.get_visual("front_foot_1") is not None,
            details="missing front_foot",
        )
        if front_aabb is not None:
            (_, fy0, _), (_, fy1, _) = front_aabb
            ctx.check(
                "feet widen footprint beyond bare panel width",
                (fy1 - fy0) > r.panel_width + 0.008,
                details=f"y_span={fy1 - fy0:.3f} panel_w={r.panel_width:.3f}",
            )

    # ---- Handle topology. ----
    if r.handle_mechanism == "swing_up_bail":
        hinge = object_model.get_part("hinge_barrel")
        carry = object_model.get_part("carry_handle")
        fix = object_model.get_articulation("front_to_hinge")
        pivot = object_model.get_articulation("handle_pivot")
        ctx.check(
            "hinge barrel is FIXED to the front leaf",
            fix.articulation_type == ArticulationType.FIXED
            and fix.parent == "front_panel"
            and fix.child == "hinge_barrel",
            details=f"{fix.parent}->{fix.child} {fix.articulation_type}",
        )
        ctx.check(
            "handle pivot is a 2nd REVOLUTE about Y (bail swings up over the apex)",
            pivot.articulation_type == ArticulationType.REVOLUTE and abs(pivot.axis[1]) > 0.99,
            details=f"type={pivot.articulation_type} axis={tuple(pivot.axis)}",
        )
        ctx.check("carry bail visual present", carry.get_visual("carry_bail") is not None)
        # Bail swings up: Z extent at the upper limit >> at rest.
        rest = ctx.part_world_aabb(carry)
        with ctx.pose({pivot: pivot.motion_limits.upper}):
            up = ctx.part_world_aabb(carry)
        if rest is not None and up is not None:
            ctx.check(
                "bail swings up (Z extent grows from folded to upright)",
                (up[1][2] - up[0][2]) > (rest[1][2] - rest[0][2]) + 0.025,
                details=f"rest_zext={rest[1][2] - rest[0][2]:.3f} up_zext={up[1][2] - up[0][2]:.3f}",
            )
        # Bail/hinge contact at the pivot ears.
        ctx.expect_contact(
            carry,
            hinge,
            elem_a="carry_bail",
            elem_b="hinge_barrel",
            name="bail pivots on the hinge barrel ear bosses",
        )
        ctx.check(
            "two real non-fixed joints (apex fold + bail pivot)",
            len([a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED]) >= 2,
            details=str([a.name for a in object_model.articulations]),
        )
    else:
        # fixed_grab_hole: no extra part / joint beyond apex fold (+ optional tether).
        carry_parts = [p.name for p in object_model.parts if p.name in ("carry_handle", "hinge_barrel")]
        ctx.check(
            "fixed grab hole adds no carry-handle part",
            carry_parts == [],
            details=str(carry_parts),
        )

    # ---- Tether topology. ----
    if r.tether_chain_enabled:
        link0_j = object_model.get_articulation("front_to_link_0")
        ctx.check(
            "tether front_to_link_0 is REVOLUTE about Y (perpendicular to the drop)",
            link0_j.articulation_type == ArticulationType.REVOLUTE and abs(link0_j.axis[1]) > 0.99,
            details=f"type={link0_j.articulation_type} axis={tuple(link0_j.axis)}",
        )
        # The chain must actually droop: posing a link about its +Y pivot moves it.
        with ctx.pose({link0_j: link0_j.motion_limits.upper}):
            link0_swung = ctx.part_world_aabb(object_model.get_part("link_0"))
        link0_rest = ctx.part_world_aabb(object_model.get_part("link_0"))
        if link0_rest is not None and link0_swung is not None:
            drift = max(
                abs(link0_swung[0][0] - link0_rest[0][0]),
                abs(link0_swung[1][0] - link0_rest[1][0]),
            )
            ctx.check(
                "tether link swings (posing the +Y pivot moves the link in X)",
                drift > 0.003,
                details=f"x_drift={drift:.4f}",
            )
        for i in range(r.tether_link_count):
            li = object_model.get_part(f"link_{i}")
            ctx.check(
                f"link_{i} exists with body visual",
                li.get_visual(f"link_{i}_body") is not None,
                details=f"link_{i}_body missing",
            )
        ctx.check(
            "front anchor pad present",
            front.get_visual("front_anchor_pad") is not None,
            details="front_anchor_pad missing",
        )
        ctx.check(
            "bail and tether are mutually exclusive",
            r.handle_mechanism != "swing_up_bail",
            details=f"handle={r.handle_mechanism}",
        )

    # ---- Rest pose A-frame + decisive bidirectional fold. ----
    with ctx.pose({apex: 0.0}):
        ctx.expect_origin_distance(
            front, back, axes="xz", max_dist=0.22, name="leaves meet near the apex at rest"
        )
        back_rest = ctx.part_world_aabb(back)
    with ctx.pose({apex: apex.motion_limits.upper}):
        back_open = ctx.part_world_aabb(back)
    with ctx.pose({apex: apex.motion_limits.lower}):
        back_closed = ctx.part_world_aabb(back)

    def _cx(aabb):
        return None if aabb is None else 0.5 * (aabb[0][0] + aabb[1][0])

    rest_cx, open_cx, closed_cx = _cx(back_rest), _cx(back_open), _cx(back_closed)
    # Opening (positive q) swings the back leaf OUTWARD (its centroid moves -X);
    # folding (negative q) swings it back TOWARD the front leaf (centroid moves
    # +X) so the two leaves stack flat to store.
    opened = rest_cx is not None and open_cx is not None and open_cx < rest_cx - 0.05
    closed = rest_cx is not None and closed_cx is not None and closed_cx > rest_cx + 0.03
    ctx.check(
        "opening the apex hinge swings the back leaf outward",
        opened,
        details=f"rest_cx={None if rest_cx is None else round(rest_cx, 3)} "
        f"open_cx={None if open_cx is None else round(open_cx, 3)}",
    )
    ctx.check(
        "folding the apex hinge (negative q) closes the leaves together to store",
        closed,
        details=f"rest_cx={None if rest_cx is None else round(rest_cx, 3)} "
        f"closed_cx={None if closed_cx is None else round(closed_cx, 3)}",
    )
    # Lock-in: at the (capped) full-open pose the swinging back leaf must NOT sweep
    # through the front-mounted carry bail (root cause of the old back_shell X
    # carry_bail 穿模 when the open ceiling was an over-wide 2.4 rad).
    if r.handle_mechanism == "swing_up_bail":
        with ctx.pose({apex: apex.motion_limits.upper}):
            ctx.fail_if_parts_overlap_in_current_pose(
                name="no back-leaf X carry-bail collision at the capped full-open pose"
            )

    # ---- slot_choices recorded (N + tether encoded). ----
    ctx.check(
        "slot_choices recorded with knuckle N + tether encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Carry handle is near the apex (top). ----
    if front_aabb is not None and r.handle_mechanism == "swing_up_bail":
        hinge_aabb = ctx.part_world_aabb(object_model.get_part("hinge_barrel"))
        if hinge_aabb is not None:
            ctx.check(
                "carry handle sits near the apex (top of the sign)",
                hinge_aabb[1][2] >= front_aabb[1][2] - 0.03,
                details=f"hinge_top={hinge_aabb[1][2]:.3f} panel_top={front_aabb[1][2]:.3f}",
            )

    return ctx.report()


__all__ = (
    "SignConfig",
    "ResolvedSignConfig",
    "build_sign",
    "build_seeded_sign",
    "config_from_seed",
    "resolve_config",
    "run_sign_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
