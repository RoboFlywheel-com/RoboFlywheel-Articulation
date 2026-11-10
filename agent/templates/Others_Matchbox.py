# SPDX-License-Identifier: Apache-2.0

"""Matchbox — modular procedural template.

Category identity: a small (~0.055 x 0.037 x 0.014 m, tabletop / handheld)
safety matchbox / book of matches: a thin-walled paper / wood closure
mechanism that opens, N homogeneous matchsticks inside, and an external
striker surface. The closure root part rests on z=0, centered on (x=0, y=0),
with X = long axis, Y = width, Z = height. Its single active joint is the
closure (PRISMATIC drawer / REVOLUTE flip-lid or matchbook). The matches are
all FIXED (they do not articulate); two loose ``ground_match_{i}`` lie splayed
in front (+Y) of the box as isolated parts.

Three parallel slots + one multiplicity axis (spec ``Others_Matchbox.md``):

  * ``closure`` (3, each >=1 non-fixed joint) — the active closure root:
      - drawer_slide: cream sleeve (open-ended hollow shell) + inner open-top
        tray sliding PRISMATIC +X (rest ~half open).
      - flip_lid: open-top body tray + cylindrical hinge knuckle + flat lid
        hinged REVOLUTE +X at the rear-top edge (rest ~50 deg open).
      - matchbook (COUPLED): folded cover (tall back panel + short front panel
        + spine + base strip) + top flap hinged REVOLUTE -X at the top fold
        line (rest ~70 deg open). Carries its own native standing paper-match
        comb fill + a front-panel striker, so it does NOT read
        ``match_arrangement`` / ``striker_style``.
  * ``match_arrangement`` (2) — how the N matchsticks are emitted (drawer /
    flip only):
      - flat_row: wooden stick lying along +X with an ellipsoid head toward
        +X, equally Y-pitched; when N exceeds single-layer width, packs into
        a double layer (n24 packing).
      - standing_bundle: wooden stick along +Z with an ellipsoid head at the
        top, in a rectangular grid; heads protrude above the rim.
  * ``striker_style`` (2) — the striker visual layout (drawer / flip only;
    inline visuals on the closure root, no joint):
      - both_long_sides: a reddish striker strip on each long side wall.
      - one_side_plus_top_patch: a single -Y side striker + a top-panel patch.

``match_count`` N in [4, 40] is the multiplicity axis (weighted toward small
N). Continuous size / travel / pitch scales live in ``resolve_config`` as
clamped params, never as slot candidates. ``palette_style`` (6 colorways) is a
per-seed material-only axis (not a slot choice).

Sources (articraft_data ``picture/Others/Matchbox`` 5-star pool): 1 parent
(classic safety matchbox ``a0e600f3``) + 7 converged forks (flip_lid /
matchbook / standing / striker_top / n6 / n16 / n24).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Others_Matchbox.md``
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
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    SphereGeometry,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
Closure = Literal["drawer_slide", "flip_lid", "matchbook"]
MatchArrangement = Literal["flat_row", "standing_bundle"]
StrikerStyle = Literal["both_long_sides", "one_side_plus_top_patch"]
PaletteStyle = Literal[
    "classic_cream_kraft",
    "white_blue_safety",
    "brown_kraft_green",
    "black_box_red",
    "glossy_white_navy",
    "red_safety",
]

CLOSURES: tuple[Closure, ...] = ("drawer_slide", "flip_lid", "matchbook")
MATCH_ARRANGEMENTS: tuple[MatchArrangement, ...] = ("flat_row", "standing_bundle")
STRIKER_STYLES: tuple[StrikerStyle, ...] = (
    "both_long_sides",
    "one_side_plus_top_patch",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_cream_kraft",
    "white_blue_safety",
    "brown_kraft_green",
    "black_box_red",
    "glossy_white_navy",
    "red_safety",
)

# match_count multiplicity axis — weighted toward small N (spec §Multiplicity).
# Bucketed weights: [4,8]:0.30 / [9,14]:0.30 / [15,22]:0.22 / [23,30]:0.12 /
# [31,40]:0.06. Expanded to per-N weights below.
MATCH_NS: tuple[int, ...] = tuple(range(4, 41))


def _match_weights() -> tuple[float, ...]:
    buckets = ((4, 8, 0.30), (9, 14, 0.30), (15, 22, 0.22), (23, 30, 0.12), (31, 40, 0.06))
    weights: list[float] = []
    for n in MATCH_NS:
        for lo, hi, w in buckets:
            if lo <= n <= hi:
                weights.append(w / (hi - lo + 1))
                break
    return tuple(weights)


MATCH_WEIGHTS: tuple[float, ...] = _match_weights()

# ---------------------------------------------------------------------------
# Palette: body (sleeve / body / cover) + closure (tray / lid / flap) +
# striker + match_wood + match_head + accent (printed border / label).
# realistic paper / wood matchbox colorways (spec palette table).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_cream_kraft": {
        "body": (0.89, 0.84, 0.71, 1.0),
        "closure": (0.92, 0.88, 0.76, 1.0),
        "striker": (0.66, 0.36, 0.28, 1.0),
        "wood": (0.85, 0.72, 0.50, 1.0),
        "head": (0.38, 0.13, 0.08, 1.0),
        "accent": (0.24, 0.14, 0.09, 1.0),
    },
    "white_blue_safety": {
        "body": (0.93, 0.92, 0.90, 1.0),
        "closure": (0.95, 0.94, 0.92, 1.0),
        "striker": (0.20, 0.26, 0.42, 1.0),
        "wood": (0.85, 0.72, 0.50, 1.0),
        "head": (0.16, 0.24, 0.50, 1.0),
        "accent": (0.16, 0.22, 0.40, 1.0),
    },
    "brown_kraft_green": {
        "body": (0.72, 0.56, 0.36, 1.0),
        "closure": (0.66, 0.50, 0.32, 1.0),
        "striker": (0.18, 0.34, 0.22, 1.0),
        "wood": (0.82, 0.68, 0.46, 1.0),
        "head": (0.20, 0.40, 0.24, 1.0),
        "accent": (0.22, 0.14, 0.09, 1.0),
    },
    "black_box_red": {
        "body": (0.13, 0.13, 0.14, 1.0),
        "closure": (0.20, 0.20, 0.22, 1.0),
        "striker": (0.45, 0.43, 0.42, 1.0),
        "wood": (0.84, 0.70, 0.48, 1.0),
        "head": (0.62, 0.14, 0.12, 1.0),
        "accent": (0.80, 0.66, 0.30, 1.0),
    },
    "glossy_white_navy": {
        "body": (0.96, 0.96, 0.95, 1.0),
        "closure": (0.97, 0.97, 0.96, 1.0),
        "striker": (0.18, 0.24, 0.40, 1.0),
        "wood": (0.85, 0.72, 0.50, 1.0),
        "head": (0.14, 0.22, 0.46, 1.0),
        "accent": (0.20, 0.28, 0.46, 1.0),
    },
    "red_safety": {
        "body": (0.66, 0.16, 0.16, 1.0),
        "closure": (0.58, 0.14, 0.14, 1.0),
        "striker": (0.30, 0.18, 0.14, 1.0),
        "wood": (0.82, 0.68, 0.46, 1.0),
        "head": (0.36, 0.12, 0.08, 1.0),
        "accent": (0.90, 0.86, 0.78, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal matchbox geometry (meters). From the 5-star sources: ~0.055 x 0.037
# x 0.014 m. X = long axis, Y = width (front -Y), Z = height. Floor at z=0.
# ---------------------------------------------------------------------------
_BOX_L = 0.055   # X, long axis (sleeve / body / cover width)
_BOX_W = 0.037   # Y, short axis
_BOX_H = 0.014   # Z, height (drawer / flip body wall height)
_T = 0.0008      # cardboard wall thickness

# matchbook back-panel height (taller than a drawer/flip box) — derived as a
# multiple of _BOX_H so palette/scale stay coherent.
_BACK_H = 0.035   # matchbook back panel height
_FRONT_H = 0.018  # matchbook front panel height
_POCKET_D = 0.010  # matchbook pocket depth (Y)
_FLAP_H = 0.020   # matchbook flap height

# Match stick (wooden, drawer/flip).
_STICK_L = 0.045   # full length
_STICK_S = 0.002   # square cross-section
_HEAD_LX = 0.0045  # ellipsoid head full length (along stick)
_HEAD_R = 0.0014   # ellipsoid head half radius

# Paper match (matchbook native fill).
_TAB_W = 0.003
_TAB_T = 0.0005
_TAB_H = 0.025
_PHEAD_H = 0.005
_PHEAD_EMBED = 0.001
_BASE_W = 0.048
_BASE_T = 0.001
_BASE_H = 0.003

# Closure travel / angle nominals.
_SLIDE_HALF = 0.020       # drawer rest-half-open travel each way
_DRAWER_RETAIN = 0.012    # min insertion kept inside the sleeve at full pull
_FLIP_REST = math.radians(50.0)
_BOOK_REST = math.radians(70.0)

# drawer + standing_bundle: the tray is drawn well out at rest so full-length
# upright matches stand in the exposed region beyond the sleeve mouth (a shallow
# horizontal sleeve cannot contain standing matches). The standing grid is then
# confined to that exposed region so the sticks never pierce the sleeve top panel.
_STAND_EXPOSE_FRAC = 0.58  # fraction of box_l the tray is drawn out at rest
_STAND_EXPOSE_CLR = 0.003  # X clearance from the sleeve mouth / tray tip each side

# matchbook flap: hinged at the top fold line of the back panel and extending
# UP from there (continuation of the back panel) so folding it never sweeps the
# panel through the back wall. Rotation about +X: positive leans it back (open),
# negative folds it forward and down over the front (closed).
_BOOK_CLOSED_Q = math.radians(-175.0)  # joint value that folds the flap shut
_BOOK_OPEN_Q = math.radians(30.0)      # joint value for fully open (a bit further back)

# flat_row single-layer packing.
_FLAT_PITCH = 0.0031      # nominal Y pitch (single layer, ~10 sticks)
_FLAT_PITCH_MIN = 0.0022  # tightest pitch before splitting to a second layer
_LAYER_DZ = _STICK_S      # upper layer sits on the lower layer
_UPPER_X_OFFSET = -0.005  # upper layer nudged back so lower heads show

# standing_bundle grid.
_STAND_PITCH = 0.006

_LOOSE_GROUND_COUNT = 2


@dataclass(frozen=True)
class MatchboxConfig:
    closure: Closure = "drawer_slide"
    match_arrangement: MatchArrangement = "flat_row"
    striker_style: StrikerStyle = "both_long_sides"
    palette_style: PaletteStyle = "classic_cream_kraft"
    match_count: int = 10
    box_length_scale: float = 1.0
    box_width_scale: float = 1.0
    box_height_scale: float = 1.0
    closure_travel_scale: float = 1.0
    match_pitch_scale: float = 1.0
    name: str = "matchbox"


@dataclass(frozen=True)
class ResolvedMatchboxConfig:
    closure: Closure
    match_arrangement: MatchArrangement
    striker_style: StrikerStyle
    palette_style: PaletteStyle
    match_count: int
    box_length_scale: float
    box_width_scale: float
    box_height_scale: float
    closure_travel_scale: float
    match_pitch_scale: float
    # derived box geometry
    box_l: float
    box_w: float
    box_h: float
    wall: float
    # matchbook derived geometry
    back_h: float
    front_h: float
    pocket_d: float
    flap_h: float
    # derived closure travel / angle
    slide_half: float
    flip_open: float
    book_open: float
    # drawer joint rest/limits (arrangement-dependent: flat_row keeps the
    # symmetric half-open rest; standing_bundle draws the tray well out so the
    # upright matches clear the sleeve top panel).
    drawer_rest: float
    drawer_lower: float
    drawer_upper: float
    # derived match params
    flat_pitch: float
    sticks_per_layer: int
    num_layers: int
    grid_cols: int
    grid_rows: int
    stand_pitch_x: float
    stand_pitch_y: float
    stand_stick_l: float  # standing stick length (clamped for flip closed-lid)
    stand_grid_xc: float  # standing grid X center in the parent (tray/body) frame
    name: str

    @property
    def hx(self) -> float:
        return self.box_l / 2.0

    @property
    def hy(self) -> float:
        return self.box_w / 2.0

    @property
    def tray_w(self) -> float:
        # inner tray outer width with sliding clearance to the sleeve walls.
        return self.box_w - 2.0 * self.wall - 2.0 * 0.0004

    @property
    def tray_inner_w(self) -> float:
        return self.tray_w - 2.0 * self.wall


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> MatchboxConfig:
    """Deterministic procedural sampling (seed 0 is not special).

    Weighted closure; for drawer/flip also sample match_arrangement /
    striker_style; matchbook forces native paper-comb + front striker so those
    two axes are NOT sampled. Then weighted match_count, uniform scales, and a
    per-seed palette.
    """
    rng = random.Random(seed)
    closure = rng.choice(CLOSURES)
    if closure == "matchbook":
        # Coupled closure: arrangement / striker are native, not sampled.
        arrangement: MatchArrangement = "flat_row"
        striker: StrikerStyle = "both_long_sides"
    else:
        arrangement = rng.choice(MATCH_ARRANGEMENTS)
        striker = rng.choice(STRIKER_STYLES)
    palette = rng.choice(PALETTE_STYLES)
    match_count = rng.choices(MATCH_NS, weights=MATCH_WEIGHTS, k=1)[0]
    return MatchboxConfig(
        closure=closure,
        match_arrangement=arrangement,
        striker_style=striker,
        palette_style=palette,
        match_count=match_count,
        box_length_scale=round(rng.uniform(0.88, 1.18), 4),
        box_width_scale=round(rng.uniform(0.88, 1.15), 4),
        box_height_scale=round(rng.uniform(0.85, 1.20), 4),
        closure_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        match_pitch_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_matchbox_{seed}",
    )


def resolve_config(
    config: MatchboxConfig | None = None,
) -> ResolvedMatchboxConfig:
    cfg = config or MatchboxConfig()
    closure = _pick(cfg.closure, CLOSURES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    # matchbook is a coupled closure: force native fill + front striker.
    if closure == "matchbook":
        arrangement: MatchArrangement = "flat_row"
        striker: StrikerStyle = "both_long_sides"
    else:
        arrangement = _pick(cfg.match_arrangement, MATCH_ARRANGEMENTS)
        striker = _pick(cfg.striker_style, STRIKER_STYLES)

    l_scale = _clamp(cfg.box_length_scale, 0.88, 1.18)
    w_scale = _clamp(cfg.box_width_scale, 0.88, 1.15)
    h_scale = _clamp(cfg.box_height_scale, 0.85, 1.20)
    ct_scale = _clamp(cfg.closure_travel_scale, 0.85, 1.10)
    mp_scale = _clamp(cfg.match_pitch_scale, 0.85, 1.20)

    box_l = _BOX_L * l_scale
    box_w = _BOX_W * w_scale
    box_h = _BOX_H * h_scale
    wall = _T
    back_h = _BACK_H * h_scale
    front_h = _FRONT_H * h_scale
    pocket_d = _POCKET_D * w_scale
    flap_h = _FLAP_H * h_scale

    # --- closure travel inequality projection -------------------------------
    # drawer: keep >= _DRAWER_RETAIN of the tray inside the sleeve at full
    # pull. The tray is box_l long; full insertion is box_l. half travel each
    # way; at +slide_half the overlap is box_l - 2*slide_half, which must
    # stay >= retain.
    max_slide = max((box_l - _DRAWER_RETAIN) / 2.0, 0.004)
    slide_half = _clamp(_SLIDE_HALF * ct_scale, 0.006, max_slide)
    flip_open = _clamp(_FLIP_REST * ct_scale, math.radians(35.0), math.radians(75.0))
    book_open = _clamp(_BOOK_REST * ct_scale, math.radians(50.0), math.radians(85.0))

    # --- match_count + arrangement packing ----------------------------------
    n = int(_clamp(cfg.match_count, 4, 40))

    # Tray inner width (Y) for flat_row Y-pitch capacity.
    tray_inner_w = box_w - 2.0 * wall - 2.0 * 0.0004 - 2.0 * wall

    # flat_row: derive per-layer capacity at the nominal pitch (scaled), tighten
    # pitch toward the min, then split to a second layer if N still overflows.
    flat_pitch = _clamp(_FLAT_PITCH * mp_scale, _FLAT_PITCH_MIN, 0.0060)
    usable_w = tray_inner_w - _STICK_S  # need half a stick of margin each side
    sticks_per_layer = max(1, int(usable_w / flat_pitch) + 1)
    if sticks_per_layer >= n:
        num_layers = 1
        sticks_per_layer = n
    else:
        # tighten pitch first (down to min) to fit more per layer.
        flat_pitch = _clamp(usable_w / max(n - 1, 1), _FLAT_PITCH_MIN, flat_pitch)
        sticks_per_layer = max(1, int(usable_w / flat_pitch) + 1)
        if sticks_per_layer >= n:
            num_layers = 1
            sticks_per_layer = n
        else:
            num_layers = math.ceil(n / sticks_per_layer)

    # standing_bundle: rectangular grid sized to fit N within the available
    # cavity. For drawer + standing the matches must fit in the *exposed* region
    # of the drawn-out tray (not the whole tray), so the X cavity is narrowed to
    # that exposed width; flip+standing uses the full open-top body length.
    drawer_standing = closure == "drawer_slide" and arrangement == "standing_bundle"
    stand_pitch = _clamp(_STAND_PITCH * mp_scale, 0.0045, 0.0070)
    if drawer_standing:
        expose_w = _STAND_EXPOSE_FRAC * box_l
        cav_x = max(expose_w - _STICK_S - 2.0 * _STAND_EXPOSE_CLR, stand_pitch)
    else:
        cav_x = box_l - 2.0 * wall - _STICK_S
    cav_y = tray_inner_w - _STICK_S
    max_cols = max(1, int(cav_x / stand_pitch) + 1)
    max_rows = max(1, int(cav_y / stand_pitch) + 1)
    grid_cols = max(1, min(max_cols, math.ceil(math.sqrt(n))))
    grid_rows = math.ceil(n / grid_cols)
    # if rows overflow the cavity, widen columns then tighten pitch.
    if grid_rows > max_rows:
        grid_cols = min(max_cols, math.ceil(n / max_rows))
        grid_rows = math.ceil(n / grid_cols)
    if grid_rows > max_rows or grid_cols > max_cols:
        needed = max(grid_cols, math.ceil(n / max(max_rows, 1)))
        grid_cols = min(max_cols, max(1, needed))
        grid_rows = math.ceil(n / grid_cols)
        span_x = max((grid_cols - 1), 1)
        span_y = max((grid_rows - 1), 1)
        stand_pitch = min(
            stand_pitch,
            cav_x / span_x if span_x > 0 else stand_pitch,
            cav_y / span_y if span_y > 0 else stand_pitch,
        )
        stand_pitch = max(stand_pitch, 0.0030)
    stand_pitch_x = stand_pitch
    stand_pitch_y = stand_pitch

    # standing stick length: nominal, but for flip_lid clamp so the head top
    # stays under the closed-lid plane (lid closes to body_h) — keeps standing
    # heads from piercing the closed lid (spec §9 flip+standing clearance).
    stand_stick_l = _STICK_L
    if closure == "flip_lid":
        flip_floor_top = wall  # body floor occupies z in [0, wall]
        head_top_allow = box_h - 0.0010  # stay just under the closed lid
        max_stick = head_top_allow - flip_floor_top - _HEAD_LX
        # Do not let the box become absurd: keep a sensible minimum.
        stand_stick_l = _clamp(max_stick, 0.008, _STICK_L)

    # --- drawer joint rest/limits + standing grid center --------------------
    # flat_row drawer: symmetric half-open rest (unchanged). standing_bundle
    # drawer: draw the tray well out so the exposed region (= drawer_rest wide)
    # holds the upright grid clear of the sleeve mouth; close fully on the lower
    # limit, extend a little further on the upper.
    if drawer_standing:
        drawer_rest = _STAND_EXPOSE_FRAC * box_l
        drawer_lower = -drawer_rest  # retract flush into the sleeve
        drawer_upper = _clamp(
            box_l - drawer_rest - _DRAWER_RETAIN, 0.002, slide_half
        )
        # Center the grid in the exposed region [box_l/2, drawer_rest+box_l/2]
        # (tray-local: subtract drawer_rest).
        stand_grid_xc = box_l / 2.0 - drawer_rest / 2.0
    else:
        drawer_rest = slide_half
        drawer_lower = -slide_half
        drawer_upper = slide_half
        stand_grid_xc = 0.003  # flip / default: grid near the parent center

    return ResolvedMatchboxConfig(
        closure=closure,
        match_arrangement=arrangement,
        striker_style=striker,
        palette_style=palette,
        match_count=n,
        box_length_scale=l_scale,
        box_width_scale=w_scale,
        box_height_scale=h_scale,
        closure_travel_scale=ct_scale,
        match_pitch_scale=mp_scale,
        box_l=box_l,
        box_w=box_w,
        box_h=box_h,
        wall=wall,
        back_h=back_h,
        front_h=front_h,
        pocket_d=pocket_d,
        flap_h=flap_h,
        slide_half=slide_half,
        flip_open=flip_open,
        book_open=book_open,
        drawer_rest=drawer_rest,
        drawer_lower=drawer_lower,
        drawer_upper=drawer_upper,
        flat_pitch=flat_pitch,
        sticks_per_layer=sticks_per_layer,
        num_layers=num_layers,
        grid_cols=grid_cols,
        grid_rows=grid_rows,
        stand_pitch_x=stand_pitch_x,
        stand_pitch_y=stand_pitch_y,
        stand_stick_l=stand_stick_l,
        stand_grid_xc=stand_grid_xc,
        name=cfg.name or "matchbox",
    )


def slot_choices_for_config(
    config: MatchboxConfig | ResolvedMatchboxConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedMatchboxConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [("closure", r.closure)]
    if r.closure == "matchbook":
        # Coupled: arrangement / striker are native, not free slots.
        choices.append(("match_arrangement", "native_paper_comb"))
        choices.append(("striker_style", "native_front"))
    else:
        choices.append(("match_arrangement", r.match_arrangement))
        choices.append(("striker_style", r.striker_style))
    layer = "double" if (r.closure != "matchbook" and r.num_layers > 1
                         and r.match_arrangement == "flat_row") else "single"
    choices.append(("match_count", f"n{r.match_count}_{layer}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared match-visual helpers (adapted from the 5-star sources; primitives
# preserved: Box stick + ellipsoid head mesh / Box paper tab + Box head).
# ---------------------------------------------------------------------------
def _add_match_visuals(part, head_mesh, *, wood_mat, head_mat) -> None:
    """Horizontal wooden matchstick: square stick + ellipsoid head at +X tip.

    Adapted from ``_add_match_visuals`` (P1 / flip_lid / striker_top sources).
    """
    part.visual(
        Box((_STICK_L, _STICK_S, _STICK_S)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=wood_mat,
        name="stick", material_class_id="wood.natural_generic",
    )
    part.visual(
        head_mesh,
        origin=Origin(xyz=(_STICK_L / 2.0 - 0.0002, 0.0, 0.0006)),
        material=head_mat,
        name="head", material_class_id="plastic.opaque_glossy_molded",
    )


def _add_vertical_match_visuals(part, head_mesh, stick_l, *, wood_mat, head_mat) -> None:
    """Vertical wooden matchstick: stick along +Z + ellipsoid head at the top.

    Adapted from ``_add_vertical_match_visuals`` (standing source).
    """
    part.visual(
        Box((_STICK_S, _STICK_S, stick_l)),
        origin=Origin(xyz=(0.0, 0.0, stick_l / 2.0)),
        material=wood_mat,
        name="stick", material_class_id="wood.natural_generic",
    )
    part.visual(
        head_mesh,
        origin=Origin(xyz=(0.0, 0.0, stick_l - 0.0002)),
        material=head_mat,
        name="head", material_class_id="plastic.opaque_glossy_molded",
    )


def _add_paper_match_standing(part, name, xc, yc, z_base, *, paper_mat, head_mat) -> None:
    """One standing paper match tab + box head (matchbook native fill).

    Adapted from ``_add_paper_match_standing`` (matchbook source).
    """
    tab_zc = z_base + _TAB_H / 2.0
    head_zc = z_base + _TAB_H + _PHEAD_H / 2.0 - _PHEAD_EMBED
    part.visual(
        Box((_TAB_W, _TAB_T, _TAB_H)),
        origin=Origin(xyz=(xc, yc, tab_zc)),
        material=paper_mat,
        name=f"{name}_tab", material_class_id="paper.cardboard",
    )
    part.visual(
        Box((_TAB_W, _TAB_T, _PHEAD_H)),
        origin=Origin(xyz=(xc, yc, head_zc)),
        material=head_mat,
        name=f"{name}_head", material_class_id="plastic.opaque_glossy_molded",
    )


def _make_head_mesh_h() -> object:
    geom = SphereGeometry(1.0, width_segments=24, height_segments=16)
    geom.scale(_HEAD_LX / 2.0, _HEAD_R, _HEAD_R)
    return mesh_from_geometry(geom, "match_head_h")


def _make_head_mesh_v() -> object:
    geom = SphereGeometry(1.0, width_segments=24, height_segments=16)
    geom.scale(_HEAD_R, _HEAD_R, _HEAD_LX / 2.0)
    return mesh_from_geometry(geom, "match_head_v")


# ---------------------------------------------------------------------------
# Match placement (drawer / flip closures share this; matchbook has its own).
# Returns list of (xc, yc, zc, vertical: bool) placements for match_{i}.
# ---------------------------------------------------------------------------
def _match_placements(
    r: ResolvedMatchboxConfig, floor_top: float
) -> list[tuple[float, float, float, bool]]:
    """``floor_top`` is the z (in the parent's local frame) of the surface the
    matches rest on: for the drawer this is the tray floor top, for the flip
    body it is the body floor top."""
    n = r.match_count
    placements: list[tuple[float, float, float, bool]] = []

    if r.match_arrangement == "standing_bundle":
        cols = r.grid_cols
        for i in range(n):
            col = i % cols
            row = i // cols
            xc = r.stand_pitch_x * (col - (cols - 1) / 2.0) + r.stand_grid_xc
            yc = r.stand_pitch_y * (row - (r.grid_rows - 1) / 2.0)
            placements.append((xc, yc, floor_top, True))
        return placements

    # flat_row (single/double/triple layer). Upper layers stagger back in -X so
    # the lower heads peek out; naively (fixed -0.005/layer) that pushes the
    # back layer past the tray rear wall at high match_count (穿模: +3.5 mm at
    # N=24, +8.5 mm at N=40). Anchor the *backmost* layer on the known-safe
    # single-layer position and cap the per-layer stagger to a box-relative
    # forward budget, so no layer pokes out the rear wall or the drawn-out
    # mouth regardless of N.
    stick_zc = floor_top + _STICK_S / 2.0
    per = r.sticks_per_layer
    base_xc = -r.box_l / 2.0 + _STICK_L / 2.0 + 0.0015
    n_layers = max(1, r.num_layers)
    if n_layers > 1:
        front_budget = 0.10 * r.box_l  # room to shift forward toward the mouth
        off_mag = min(-_UPPER_X_OFFSET, front_budget / (n_layers - 1))
    else:
        off_mag = 0.0
    # shift the base forward so the backmost layer lands on base_xc (safe) and
    # the frontmost layer advances by at most front_budget.
    stick_xc = base_xc + (n_layers - 1) * off_mag
    for i in range(n):
        layer = i // per
        col = i % per
        yc = r.flat_pitch * (col - (per - 1) / 2.0)
        xc = stick_xc - layer * off_mag
        zc = stick_zc + layer * _LAYER_DZ
        placements.append((xc, yc, zc, False))
    return placements


def _emit_matches(model, parent, r: ResolvedMatchboxConfig, joint_prefix: str,
                  floor_top: float, *, wood_mat, head_mat) -> None:
    """Emit N match_{i} parts, all FIXED to the tray/body (drawer / flip)."""
    head_h = _make_head_mesh_h()
    head_v = _make_head_mesh_v()
    for i, (xc, yc, zc, vertical) in enumerate(_match_placements(r, floor_top)):
        match = model.part(f"match_{i}")
        if vertical:
            _add_vertical_match_visuals(
                match, head_v, r.stand_stick_l, wood_mat=wood_mat, head_mat=head_mat
            )
        else:
            _add_match_visuals(match, head_h, wood_mat=wood_mat, head_mat=head_mat)
        model.articulation(
            f"{joint_prefix}_to_match_{i}",
            ArticulationType.FIXED,
            parent=parent,
            child=match,
            origin=Origin(xyz=(xc, yc, zc)),
        )


def _emit_ground_matches(model, parent, r: ResolvedMatchboxConfig, joint_prefix: str,
                         front_y: float, *, wood_mat, head_mat) -> None:
    """Two loose wooden matches lying flat in front (+Y), isolated parts.

    ``front_y`` is the +Y extent of the parent's front geometry. The FIXED
    joint origin is kept within ~10 mm of it (the sticks lie along X so they do
    not intrude into the box) so the baseline
    ``fail_if_articulation_origin_far_from_geometry`` (15 mm tol) is satisfied,
    while the matches still read as splayed loose on the ground in front.
    """
    head_h = _make_head_mesh_h()
    ground_zc = _STICK_S / 2.0
    fy = front_y + 0.009
    placements = (
        ((0.000, fy), math.pi + 0.10),
        ((0.010, fy + 0.005), math.pi + 0.35),
    )
    for i, ((cx, cy), yaw) in enumerate(placements):
        gm = model.part(f"ground_match_{i}")
        _add_match_visuals(gm, head_h, wood_mat=wood_mat, head_mat=head_mat)
        model.articulation(
            f"{joint_prefix}_to_ground_match_{i}",
            ArticulationType.FIXED,
            parent=parent,
            child=gm,
            origin=Origin(xyz=(cx, cy, ground_zc), rpy=(0.0, 0.0, yaw)),
        )


# ---------------------------------------------------------------------------
# Striker / border decorations (Rule 1: inline visuals on the closure root).
# ---------------------------------------------------------------------------
def _add_strikers_drawer_flip(part, r: ResolvedMatchboxConfig, *, striker_mat, accent_mat,
                              has_top_panel: bool) -> None:
    """Striker strips on the closure root (sleeve / body). Both styles emit a
    -Y side striker; both_long_sides adds a +Y side striker; the top-patch
    style adds a top-panel patch instead (spec §Slot C).

    ``has_top_panel`` is True for the drawer sleeve (closed top, the patch lies
    on the top panel) and False for the open-top flip body (the patch is
    embedded onto the rear-wall top rim so it connects to real geometry rather
    than floating over the open cavity)."""
    box_w, box_h = r.box_w, r.box_h
    strip_len = min(0.050, r.box_l - 0.005)
    if r.striker_style == "both_long_sides":
        for i, sy in enumerate((-1.0, 1.0)):
            part.visual(
                Box((strip_len, 0.0006, min(0.010, box_h * 0.75))),
                origin=Origin(xyz=(0.0, sy * (box_w / 2.0 + 0.0001), box_h / 2.0)),
                material=striker_mat,
                name=f"striker_{i}", material_class_id="paper.cardboard",
            )
    else:
        # one_side_plus_top_patch: single -Y side striker + a top patch.
        part.visual(
            Box((strip_len, 0.0006, min(0.010, box_h * 0.75))),
            origin=Origin(xyz=(0.0, -(box_w / 2.0 + 0.0001), box_h / 2.0)),
            material=striker_mat,
            name="side_striker", material_class_id="paper.cardboard",
        )
        if has_top_panel:
            # Lies flat on the closed top panel beside the printed border.
            part.visual(
                Box((min(0.040, r.box_l - 0.012), min(0.012, box_w * 0.4), 0.0004)),
                origin=Origin(xyz=(0.0, 0.005, box_h)),
                material=striker_mat,
                name="top_striker_patch", material_class_id="paper.cardboard",
            )
        else:
            # Open-top body: embed the patch onto the rear (-Y) wall top rim so
            # it touches the real side wall (which reaches z=box_h) instead of
            # floating over the open cavity.
            patch_w = min(0.0035, box_w * 0.18)
            part.visual(
                Box((min(0.040, r.box_l - 0.012), patch_w, 0.0006)),
                origin=Origin(xyz=(0.0, -(box_w / 2.0 - patch_w / 2.0), box_h - 0.0001)),
                material=striker_mat,
                name="top_striker_patch", material_class_id="paper.cardboard",
            )


def _add_top_border(part, r: ResolvedMatchboxConfig, *, accent_mat) -> None:
    """Dark printed border on the top face (inline visuals, proud of panel)."""
    box_l, box_w, box_h = r.box_l, r.box_w, r.box_h
    border_z = box_h
    border_w = 0.0012
    inset = 0.0035
    long_len = box_l - 2.0 * inset
    short_len = box_w - 2.0 * inset
    for i, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((long_len, border_w, 0.0004)),
            origin=Origin(xyz=(0.0, sy * (box_w / 2.0 - inset - border_w / 2.0), border_z)),
            material=accent_mat,
            name=f"border_long_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    for i, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((border_w, short_len, 0.0004)),
            origin=Origin(xyz=(sx * (box_l / 2.0 - inset - border_w / 2.0), 0.0, border_z)),
            material=accent_mat,
            name=f"border_short_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


# ---------------------------------------------------------------------------
# Slot A: closure builders.
# ---------------------------------------------------------------------------
def _build_drawer_slide(model, r: ResolvedMatchboxConfig, *, mats) -> object:
    """Sleeve (open-ended hollow shell) + inner open-top tray, PRISMATIC +X.

    Adapted from P1 ``sleeve`` / ``tray`` / ``sleeve_to_tray``.
    """
    box_l, box_w, box_h, wall = r.box_l, r.box_w, r.box_h, r.wall

    sleeve = model.part("sleeve")
    sleeve.visual(
        Box((box_l, box_w, wall)),
        origin=Origin(xyz=(0.0, 0.0, wall / 2.0)),
        material=mats["body"],
        name="bottom_panel", material_class_id="paper.cardboard",
    )
    sleeve.visual(
        Box((box_l, box_w, wall)),
        origin=Origin(xyz=(0.0, 0.0, box_h - wall / 2.0)),
        material=mats["body"],
        name="top_panel", material_class_id="paper.cardboard",
    )
    for i, sy in enumerate((-1.0, 1.0)):
        sleeve.visual(
            Box((box_l, wall, box_h)),
            origin=Origin(xyz=(0.0, sy * (box_w / 2.0 - wall / 2.0), box_h / 2.0)),
            material=mats["body"],
            name=f"side_wall_{i}", material_class_id="paper.cardboard",
        )
    _add_strikers_drawer_flip(sleeve, r, striker_mat=mats["striker"], accent_mat=mats["accent"],
                              has_top_panel=True)
    _add_top_border(sleeve, r, accent_mat=mats["accent"])
    sleeve.inertial = Inertial.from_geometry(
        Box((box_l, box_w, box_h)),
        mass=0.010,
        origin=Origin(xyz=(0.0, 0.0, box_h / 2.0)),
    )

    # Inner tray: open-top hollow (floor + 2 side + 2 end wall).
    tray_w = r.tray_w
    # The sleeve inner clear cavity is z in [wall, box_h - wall], height
    # cavity_h = box_h - 2*wall. The tray floor rides on the sleeve bottom at
    # z = wall, so the tray must be SHORTER than cavity_h or its top wall pierces
    # the sleeve top panel (viewer bug: 抽屉盒穿模). Derive a small vertical
    # clearance (~5% of the cavity, floored at 0.3 mm) so it stays positive and
    # non-piercing across every scale (min cavity ~10.3 mm -> gap ~0.5 mm).
    cavity_h = box_h - 2.0 * wall
    tray_gap = max(0.05 * cavity_h, 0.0003)
    tray_h = cavity_h - tray_gap  # floor rides on the sleeve bottom, top stays clear
    tray_z0 = wall
    tray = model.part("tray")
    tray.visual(
        Box((box_l, tray_w, wall)),
        origin=Origin(xyz=(0.0, 0.0, tray_z0 + wall / 2.0)),
        material=mats["closure"],
        name="tray_floor", material_class_id="paper.cardboard",
    )
    wall_zc = tray_z0 + tray_h / 2.0
    for i, sy in enumerate((-1.0, 1.0)):
        tray.visual(
            Box((box_l, wall, tray_h)),
            origin=Origin(xyz=(0.0, sy * (tray_w / 2.0 - wall / 2.0), wall_zc)),
            material=mats["closure"],
            name=f"tray_side_wall_{i}", material_class_id="paper.cardboard",
        )
    for i, sx in enumerate((-1.0, 1.0)):
        tray.visual(
            Box((wall, tray_w, tray_h)),
            origin=Origin(xyz=(sx * (box_l / 2.0 - wall / 2.0), 0.0, wall_zc)),
            material=mats["closure"],
            name=f"tray_end_wall_{i}", material_class_id="paper.cardboard",
        )
    tray.inertial = Inertial.from_geometry(
        Box((box_l, tray_w, tray_h)),
        mass=0.008,
        origin=Origin(xyz=(0.0, 0.0, wall_zc)),
    )

    model.articulation(
        "sleeve_to_tray",
        ArticulationType.PRISMATIC,
        parent=sleeve,
        child=tray,
        origin=Origin(xyz=(r.drawer_rest, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=0.15, lower=r.drawer_lower, upper=r.drawer_upper
        ),
    )
    return tray


def _build_flip_lid(model, r: ResolvedMatchboxConfig, *, mats) -> object:
    """Open-top body tray + cylindrical hinge knuckle + flat lid REVOLUTE +X.

    Adapted from flip_lid ``body`` / ``lid`` / ``body_to_lid``.
    """
    box_l, box_w, box_h, wall = r.box_l, r.box_w, r.box_h, r.wall

    body = model.part("body")
    body.visual(
        Box((box_l, box_w, wall)),
        origin=Origin(xyz=(0.0, 0.0, wall / 2.0)),
        material=mats["body"],
        name="floor", material_class_id="paper.cardboard",
    )
    wall_zc = box_h / 2.0
    for i, sy in enumerate((-1.0, 1.0)):
        body.visual(
            Box((box_l, wall, box_h)),
            origin=Origin(xyz=(0.0, sy * (box_w / 2.0 - wall / 2.0), wall_zc)),
            material=mats["body"],
            name=f"side_wall_{i}", material_class_id="paper.cardboard",
        )
    end_wall_w = box_w - 2.0 * wall
    for i, sx in enumerate((-1.0, 1.0)):
        body.visual(
            Box((wall, end_wall_w, box_h)),
            origin=Origin(xyz=(sx * (box_l / 2.0 - wall / 2.0), 0.0, wall_zc)),
            material=mats["body"],
            name=f"end_wall_{i}", material_class_id="paper.cardboard",
        )
    # Hinge knuckle: cylinder along X on the rear (-Y) top edge.
    knuckle_r = 0.0012
    knuckle_l = box_l * 0.70
    body.visual(
        Cylinder(radius=knuckle_r, length=knuckle_l),
        origin=Origin(xyz=(0.0, -(box_w / 2.0), box_h), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="hinge_knuckle", material_class_id="paper.cardboard",
    )
    _add_strikers_drawer_flip(body, r, striker_mat=mats["striker"], accent_mat=mats["accent"],
                              has_top_panel=False)
    body.inertial = Inertial.from_geometry(
        Box((box_l, box_w, box_h)),
        mass=0.010,
        origin=Origin(xyz=(0.0, 0.0, box_h / 2.0)),
    )

    # Lid: flat panel, hinge edge at part origin (y=0), extends +Y.
    lid = model.part("lid")
    lid.visual(
        Box((box_l, box_w, wall)),
        origin=Origin(xyz=(0.0, box_w / 2.0, wall / 2.0)),
        material=mats["closure"],
        name="lid_panel", material_class_id="paper.cardboard",
    )
    # Printed border on the lid top. The lid panel is centered at y=box_w/2
    # (lid-local), spanning y in [0, box_w]; borders are placed relative to that
    # center and embedded so they connect to the panel top (no floating island).
    panel_cy = box_w / 2.0
    border_z = wall - 0.0001  # embed slightly into the panel top (z=wall)
    border_w = 0.0012
    inset = 0.0035
    long_len = box_l - 2.0 * inset
    for i, sy in enumerate((-1.0, 1.0)):
        lid.visual(
            Box((long_len, border_w, 0.0006)),
            origin=Origin(xyz=(0.0, panel_cy + sy * (box_w / 2.0 - inset - border_w / 2.0),
                               border_z)),
            material=mats["accent"],
            name=f"lid_border_long_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    lid.inertial = Inertial.from_geometry(
        Box((box_l, box_w, wall)),
        mass=0.004,
        origin=Origin(xyz=(0.0, box_w / 2.0, wall / 2.0)),
    )

    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, -(box_w / 2.0), box_h), rpy=(r.flip_open, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=2.0, lower=-r.flip_open, upper=math.radians(75.0)
        ),
    )
    return body


def _build_matchbook(model, r: ResolvedMatchboxConfig, *, mats) -> object:
    """Folded cover (back/front panel + spine + base strip + native paper comb
    + front striker) + top flap REVOLUTE -X.

    Adapted from matchbook ``cover`` / ``flap`` / ``cover_to_flap`` +
    ``_add_paper_match_standing`` comb loop.
    """
    cover_w = r.box_l
    back_h = r.back_h
    front_h = r.front_h
    pocket_d = r.pocket_d
    wall = r.wall
    flap_h = r.flap_h

    cover = model.part("cover")
    # Tall back panel (at -Y face).
    cover.visual(
        Box((cover_w, wall, back_h)),
        origin=Origin(xyz=(0.0, -wall / 2.0, back_h / 2.0)),
        material=mats["body"],
        name="back_panel", material_class_id="paper.cardboard",
    )
    # Short front panel, offset +Y by the pocket.
    cover.visual(
        Box((cover_w, wall, front_h)),
        origin=Origin(xyz=(0.0, pocket_d + wall / 2.0, front_h / 2.0)),
        material=mats["body"],
        name="front_panel", material_class_id="paper.cardboard",
    )
    # Bottom spine connecting the panels.
    cover.visual(
        Box((cover_w, pocket_d, wall)),
        origin=Origin(xyz=(0.0, pocket_d / 2.0, wall / 2.0)),
        material=mats["body"],
        name="spine", material_class_id="paper.cardboard",
    )
    # Striker on the +Y face of the front panel (native front striker).
    cover.visual(
        Box((min(0.050, cover_w - 0.005), 0.0006, min(0.014, front_h * 0.8))),
        origin=Origin(xyz=(0.0, pocket_d + wall + 0.0001, front_h / 2.0)),
        material=mats["striker"],
        name="striker", material_class_id="paper.cardboard",
    )
    # Base strip across the bottom inside the pocket.
    base_w = min(_BASE_W, cover_w - 0.006)
    cover.visual(
        Box((base_w, _BASE_T, _BASE_H)),
        origin=Origin(xyz=(0.0, pocket_d / 2.0, wall + _BASE_H / 2.0)),
        material=mats["closure"],
        name="base_strip", material_class_id="paper.cardboard",
    )
    # Native paper-match comb: N tabs standing on the base strip.
    n = r.match_count
    pitch = base_w / n
    tab_z_base = wall + _BASE_H
    tab_y = pocket_d / 2.0
    for i in range(n):
        xc = -base_w / 2.0 + pitch / 2.0 + i * pitch
        _add_paper_match_standing(
            cover, f"match_{i}", xc, tab_y, tab_z_base,
            paper_mat=mats["closure"], head_mat=mats["head"],
        )
    cover.inertial = Inertial.from_geometry(
        Box((cover_w, pocket_d + 2.0 * wall, back_h)),
        mass=0.008,
        origin=Origin(xyz=(0.0, pocket_d / 2.0, back_h / 2.0)),
    )

    # Top flap: hinged at the top fold line (front-top edge of the back panel)
    # and extending UP from there (a continuation of the back panel), sitting
    # just in front of the back panel plane (y in [0, wall]). Because the panel
    # lives above the pivot, folding it forward to close never sweeps it through
    # the back panel below the hinge.
    flap = model.part("flap")
    flap.visual(
        Box((cover_w, wall, flap_h)),
        origin=Origin(xyz=(0.0, wall / 2.0, flap_h / 2.0)),
        material=mats["body"],
        name="flap_panel", material_class_id="paper.cardboard",
    )
    flap.inertial = Inertial.from_geometry(
        Box((cover_w, wall, flap_h)),
        mass=0.003,
        origin=Origin(xyz=(0.0, wall / 2.0, flap_h / 2.0)),
    )
    # Rest lean-back derived from the sampled book_open (kept moderate so the
    # open flap clears the comb but reads as wide open). axis +X: positive q
    # leans further back, the lower limit folds the flap forward and down over
    # the front to close.
    back_tilt = _clamp(r.book_open * 0.6, math.radians(20.0), math.radians(50.0))
    model.articulation(
        "cover_to_flap",
        ArticulationType.REVOLUTE,
        parent=cover,
        child=flap,
        origin=Origin(xyz=(0.0, 0.0, back_h), rpy=(back_tilt, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=3.0, lower=_BOOK_CLOSED_Q, upper=_BOOK_OPEN_Q
        ),
    )
    return cover


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_matchbox(
    config: MatchboxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"mb_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    if r.closure == "drawer_slide":
        parent = _build_drawer_slide(model, r, mats=mats)
        # tray-local: tray floor occupies z in [wall, 2*wall], top = 2*wall.
        _emit_matches(model, parent, r, "tray", 2.0 * r.wall,
                      wood_mat=mats["wood"], head_mat=mats["head"])
        _emit_ground_matches(model, model.get_part("sleeve"), r, "sleeve", r.hy,
                             wood_mat=mats["wood"], head_mat=mats["head"])
    elif r.closure == "flip_lid":
        parent = _build_flip_lid(model, r, mats=mats)
        # body-local: body floor occupies z in [0, wall], top = wall.
        _emit_matches(model, parent, r, "body", r.wall,
                      wood_mat=mats["wood"], head_mat=mats["head"])
        _emit_ground_matches(model, parent, r, "body", r.hy,
                             wood_mat=mats["wood"], head_mat=mats["head"])
    else:  # matchbook (coupled, native fill — no separate match parts)
        cover = _build_matchbook(model, r, mats=mats)
        # cover front panel outer +Y face is at pocket_d + wall.
        _emit_ground_matches(model, cover, r, "cover", r.pocket_d + r.wall,
                             wood_mat=mats["wood"], head_mat=mats["head"])

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["palette_style"] = r.palette_style
    return model


def build_seeded_matchbox(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_matchbox(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (tray-in-sleeve, knuckle-on-lid,
# flap-against-panels, standing-stick-through-top-panel) are declared
# element-scoped; the closure action is exercised; ground matches are isolated.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_matchbox_tests(
    object_model: ArticulatedObject,
    config: MatchboxConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    # Loose ground matches are intentionally isolated on the floor in front.
    ground_matches = [
        object_model.get_part(f"ground_match_{i}") for i in range(_LOOSE_GROUND_COUNT)
    ]
    for gm in ground_matches:
        ctx.allow_isolated_part(
            gm, reason="Loose match placed on the ground in front of the box per the category."
        )

    # =====================================================================
    # Closure: root rests on the ground, real volume, action exercised.
    # =====================================================================
    if r.closure == "drawer_slide":
        sleeve = object_model.get_part("sleeve")
        tray = object_model.get_part("tray")
        slide = object_model.get_articulation("sleeve_to_tray")

        # tray rides captured inside the hollow sleeve cross-section.
        ctx.expect_within(
            tray, sleeve, axes="yz", margin=0.0005,
            name="tray cross-section stays captured inside the hollow sleeve",
        )

        aabb = ctx.part_world_aabb(sleeve)
        bext = _ext(aabb)
        ctx.check(
            "sleeve rests on the ground (base near z=0)",
            abs(aabb[0][2]) < 0.003,
            details=f"sleeve min z={aabb[0][2]:.4f}",
        )
        ctx.check(
            "sleeve has a real matchbox footprint",
            bext[0] > 0.03 and bext[1] > 0.02 and bext[2] > 0.005,
            details=f"sleeve extents={bext}",
        )
        ctx.check(
            "sleeve_to_tray is PRISMATIC about +X",
            slide.articulation_type == ArticulationType.PRISMATIC
            and abs(slide.axis[0]) == 1.0 and slide.axis[1] == 0.0 and slide.axis[2] == 0.0,
            details=f"type={slide.articulation_type} axis={slide.axis}",
        )
        rest = ctx.part_world_position(tray)
        with ctx.pose({slide: r.drawer_upper}):
            out = ctx.part_world_position(tray)
        ctx.check(
            "tray slides out toward +X",
            out[0] > rest[0] + r.drawer_upper * 0.5,
            details=f"rest_x={rest[0]:.4f}, out_x={out[0]:.4f}",
        )
        with ctx.pose({slide: r.drawer_lower}):
            ctx.expect_within(
                tray, sleeve, axes="x", margin=0.001,
                name="closed tray sits flush inside the sleeve",
            )
        with ctx.pose({slide: r.drawer_upper}):
            ctx.expect_overlap(
                tray, sleeve, axes="x", min_overlap=0.008,
                name="fully extended tray is still captured by the sleeve",
            )
        # drawer + standing: the upright matches stand in the exposed region of
        # the drawn-out tray, clear of the sleeve top panel (no piercing).
        if r.match_arrangement == "standing_bundle":
            mouth_x = r.box_l / 2.0
            clear_all = True
            worst = None
            for i in range(r.match_count):
                m = object_model.get_part(f"match_{i}")
                sb = ctx.part_element_world_aabb(m, elem="stick")
                if sb is None or sb[0][0] <= mouth_x:
                    clear_all = False
                    worst = sb[0][0] if sb is not None else None
                    break
            ctx.check(
                "standing matches stand clear of the sleeve mouth (no top-panel piercing)",
                clear_all,
                details=f"sleeve mouth x={mouth_x:.4f}, worst stick x-min={worst}",
            )
        _allow_match_overlaps(ctx, object_model, tray, r, sleeve_for_top="sleeve")

    elif r.closure == "flip_lid":
        body = object_model.get_part("body")
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("body_to_lid")

        ctx.allow_overlap(
            body, lid, elem_a="hinge_knuckle", elem_b="lid_panel",
            reason="The lid panel edge wraps around the cylindrical hinge knuckle "
                   "at the fold line (small local interpenetration).",
        )
        aabb = ctx.part_world_aabb(body)
        bext = _ext(aabb)
        ctx.check(
            "body rests on the ground (base near z=0)",
            abs(aabb[0][2]) < 0.003,
            details=f"body min z={aabb[0][2]:.4f}",
        )
        ctx.check(
            "body has a real matchbox footprint",
            bext[0] > 0.03 and bext[1] > 0.02 and bext[2] > 0.005,
            details=f"body extents={bext}",
        )
        ctx.check(
            "body_to_lid is REVOLUTE about +X at the rear-top edge",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.9 and abs(hinge.axis[1]) < 0.1 and abs(hinge.axis[2]) < 0.1
            and hinge.origin.xyz[1] < -(r.box_w / 2.0 - 0.005)
            and abs(hinge.origin.xyz[2] - r.box_h) < 0.004,
            details=f"type={hinge.articulation_type} axis={hinge.axis} origin={hinge.origin.xyz}",
        )
        # closed pose: lid covers the body top, lying flat near the rim.
        with ctx.pose({hinge: hinge.motion_limits.lower}):
            closed = ctx.part_world_aabb(lid)
            closed_top = closed[1][2]
            ctx.expect_overlap(
                lid, body, axes="xy", min_overlap=0.015,
                name="closed lid overlaps the body footprint",
            )
            ctx.check(
                "closed lid lies flat over the body opening",
                closed_top < r.box_h + 0.004,
                details=f"closed lid aabb={closed}",
            )
        # rest pose (q=0) is open: the free edge has risen above its closed
        # height, proving the hinge tilts the lid up (source flip_lid semantics).
        rest_top = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "lid free edge swings up when opened from closed",
            rest_top > closed_top + 0.005,
            details=f"closed_top={closed_top:.4f}, rest_top={rest_top:.4f}",
        )
        _allow_match_overlaps(ctx, object_model, body, r, sleeve_for_top=None)

    else:  # matchbook
        cover = object_model.get_part("cover")
        flap = object_model.get_part("flap")
        hinge = object_model.get_articulation("cover_to_flap")

        # The open flap (rest pose) stands clear above the back panel and clear
        # of the match comb, so no overlap masking is needed at the displayed pose.
        back_bb = ctx.part_element_world_aabb(cover, elem="back_panel")
        ctx.check(
            "matchbook back panel rests on the ground (base near z=0)",
            back_bb is not None and abs(back_bb[0][2]) < 0.003,
            details=f"back_panel aabb={back_bb}",
        )
        front_bb = ctx.part_element_world_aabb(cover, elem="front_panel")
        ctx.check(
            "front panel is shorter than the back panel (folded shell)",
            front_bb is not None and back_bb is not None
            and front_bb[1][2] < back_bb[1][2] - 0.003,
            details=f"front={front_bb} back={back_bb}",
        )
        ctx.check(
            "cover_to_flap is REVOLUTE about +X at the top fold line",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.9 and abs(hinge.axis[1]) < 0.1 and abs(hinge.axis[2]) < 0.1
            and abs(hinge.origin.xyz[2] - r.back_h) < 0.003,
            details=f"type={hinge.articulation_type} axis={hinge.axis} origin={hinge.origin.xyz}",
        )
        # native paper comb present.
        ctx.check(
            "native paper match comb tabs present",
            all(cover.get_visual(f"match_{i}_tab") is not None for i in range(r.match_count)),
            details=f"match_count={r.match_count}",
        )
        # rest pose open: flap leans back above the back panel plane.
        flap_rest = ctx.part_world_aabb(flap)
        ctx.check(
            "rest pose shows the flap open (leans back behind the back panel plane)",
            flap_rest is not None and back_bb is not None
            and flap_rest[0][1] < back_bb[0][1] - 0.001,
            details=f"flap rest aabb={flap_rest}",
        )
        # the open flap rises above the back panel top, clear of the comb.
        ctx.check(
            "open flap stands above the back panel top (clear of the matches)",
            flap_rest is not None and flap_rest[0][2] > r.back_h - 0.001,
            details=f"flap rest z-min={flap_rest[0][2] if flap_rest else None}, back_h={r.back_h}",
        )
        # the open flap does not interpenetrate the comb (no Y overlap with the
        # tabs, which sit in front of the back panel).
        fb = ctx.part_element_world_aabb(flap, elem="flap_panel")
        tb = ctx.part_element_world_aabb(cover, elem="match_0_tab")
        ctx.check(
            "open flap stays clear of the match comb (no penetration)",
            fb is not None and tb is not None and fb[1][1] < tb[0][1],
            details=f"flap_panel={fb} comb_tab={tb}",
        )
        # opening further leans the flap further back.
        with ctx.pose({hinge: _BOOK_OPEN_Q}):
            more = ctx.part_world_aabb(flap)
        ctx.check(
            "opening further leans the flap further back",
            more is not None and flap_rest is not None and more[0][1] < flap_rest[0][1] - 0.0005,
            details=f"more={more} rest={flap_rest}",
        )

    # =====================================================================
    # Matches present (drawer / flip) + striker visual present.
    # =====================================================================
    if r.closure != "matchbook":
        matches = [object_model.get_part(f"match_{i}") for i in range(r.match_count)]
        ctx.check(
            f"{r.match_count} matchsticks fill the box",
            len(matches) == r.match_count,
            details=f"match_count={r.match_count}",
        )
        # striker visual exists per style.
        root = object_model.get_part("sleeve" if r.closure == "drawer_slide" else "body")
        if r.striker_style == "both_long_sides":
            ok = root.get_visual("striker_0") is not None and root.get_visual("striker_1") is not None
        else:
            ok = (root.get_visual("side_striker") is not None
                  and root.get_visual("top_striker_patch") is not None)
        ctx.check("striker surface visual exists on the closure root", ok)
    else:
        ctx.check(
            "matchbook front striker visual exists",
            object_model.get_part("cover").get_visual("striker") is not None,
        )

    # ---- at least one non-fixed closure joint exists (category identity) ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed closure joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()


def _allow_match_overlaps(ctx, object_model, parent, r: ResolvedMatchboxConfig,
                          *, sleeve_for_top) -> None:
    """Element-scoped overlaps for matches inside the tray/body.

    Standing matches now stand in the exposed region of the drawn-out tray and
    no longer pierce the sleeve top panel, so no stick/top-panel mask is needed.
    Matches in a tightly-packed grid / double layer may still touch adjacent
    matches; that contact is allowed here.
    """
    matches = [object_model.get_part(f"match_{i}") for i in range(r.match_count)]
    # Adjacent matches in a packed grid / double layer may touch.
    for i in range(len(matches)):
        for j in (i + 1, i + r.grid_cols if r.match_arrangement == "standing_bundle" else i + 1):
            if 0 <= j < len(matches) and j != i:
                ctx.allow_overlap(
                    matches[i], matches[j],
                    reason="Densely packed matches touch their neighbours in the box.",
                )
