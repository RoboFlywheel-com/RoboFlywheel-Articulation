# SPDX-License-Identifier: Apache-2.0

"""Handheld game console modular template (Sports / game console).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Sports_game_console.md`` and the
8 five-star samples (3 parents + 5 single-axis forks):

  * S1 PSP slab (``rec_blue-psp...f576a977``) — landscape slab + dpad + N round
    face buttons (PRISMATIC press) + analog nub + L/R shoulder triggers.
  * S2 wireless controller (``rec_purple...a59b32a9``) — ergonomic lofted shell,
    dual thumbsticks (REVOLUTE tilt) seated in dish rings, no screen.
  * S3 brick slab (``rec_red...2a2ee0bb``) — wedge slab, square LCD, dpad rocker.
  * S4 clamshell — lower/upper rounded panels with a REVOLUTE barrel hinge.
  * S5 numeric keypad / S6 8-way joypad lever / S7-S8 N=2/3 face buttons.

Structure (pattern = ``mixed``): a single root ``body`` (or ``lower_panel`` for
the clamshell archetype, which adds an ``upper_panel`` over a REVOLUTE hinge)
carries a set of **parallel input children** plus a **face-button multiplicity**
axis:

  * Slot A ``device_archetype`` (4): psp_slab / controller_ergo / brick_slab /
    clamshell — the shell form + the control-face plane.
  * Slot B ``input_cluster`` (4): dpad_plus_round_buttons / dual_thumbsticks /
    numeric_keypad / single_8way_joypad_lever — the primary directional input.
  * Slot C ``screen_form`` (3): landscape_lcd / square_lcd / no_screen — a fixed
    body (or upper_panel) visual, never a FIXED-joint part.
  * face-button **multiplicity** N ∈ [2,8]: N round dome+stem caps, each its own
    PRISMATIC -Z press, laid out by an N→layout table.
  * optional L/R ``shoulder`` triggers (REVOLUTE about the top edge).

Compatibility gates (spec §slot graph): clamshell forces a screen (no_screen
illegal); controller_ergo forces no_screen (a big LCD reads as a handheld, not a
gamepad) and never takes the numeric_keypad cluster.

Every non-FIXED child uses captured-pin / seated geometry (button stems sink into
wells, sticks/levers seat on raised collars, panels share a barrel hinge), so the
joints omit ``MatingContract`` (grandfathered) and rely on the flat
articulation-origin baseline + broad ``allow_overlap``, mirroring calculator.
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
    CylinderGeometry,
    DomeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

DeviceArchetype = Literal["psp_slab", "controller_ergo", "brick_slab", "clamshell"]
InputCluster = Literal[
    "dpad_plus_round_buttons",
    "dual_thumbsticks",
    "numeric_keypad",
    "single_8way_joypad_lever",
]
ScreenForm = Literal["landscape_lcd", "square_lcd", "no_screen", "dual_screen"]
PaletteStyle = Literal[
    "glossy_blue_psp",
    "brick_red_yellow",
    "charcoal_pro",
    "retro_cream",
    "mint_translucent",
    "neon_arcade",
]

DEVICE_ARCHETYPES: tuple[DeviceArchetype, ...] = (
    "psp_slab",
    "controller_ergo",
    "brick_slab",
    "clamshell",
)
INPUT_CLUSTERS: tuple[InputCluster, ...] = (
    "dpad_plus_round_buttons",
    "dual_thumbsticks",
    "numeric_keypad",
    "single_8way_joypad_lever",
)
SCREEN_FORMS: tuple[ScreenForm, ...] = (
    "landscape_lcd",
    "square_lcd",
    "no_screen",
    "dual_screen",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "glossy_blue_psp",
    "brick_red_yellow",
    "charcoal_pro",
    "retro_cream",
    "mint_translucent",
    "neon_arcade",
)

# face-button multiplicity domain (spec §multiplicity).
N_MIN, N_MAX = 2, 8

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "glossy_blue_psp": {
        "shell": (0.12, 0.52, 0.92, 1.0),
        "screen": (0.03, 0.03, 0.05, 1.0),
        "bezel": (0.78, 0.80, 0.83, 1.0),
        "button": (0.20, 0.60, 0.95, 1.0),
        "accent": (0.16, 0.16, 0.18, 1.0),
        "trim": (0.78, 0.80, 0.83, 1.0),
    },
    "brick_red_yellow": {
        "shell": (0.80, 0.13, 0.13, 1.0),
        "screen": (0.28, 0.34, 0.28, 1.0),
        "bezel": (0.55, 0.56, 0.58, 1.0),
        "button": (0.96, 0.78, 0.10, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "trim": (0.92, 0.86, 0.20, 1.0),
    },
    "charcoal_pro": {
        "shell": (0.16, 0.16, 0.18, 1.0),
        "screen": (0.04, 0.05, 0.07, 1.0),
        "bezel": (0.32, 0.33, 0.36, 1.0),
        "button": (0.55, 0.58, 0.64, 1.0),
        "accent": (0.86, 0.30, 0.24, 1.0),
        "trim": (0.42, 0.44, 0.48, 1.0),
    },
    "retro_cream": {
        "shell": (0.90, 0.85, 0.74, 1.0),
        "screen": (0.20, 0.28, 0.22, 1.0),
        "bezel": (0.70, 0.66, 0.56, 1.0),
        "button": (0.74, 0.32, 0.30, 1.0),
        "accent": (0.40, 0.42, 0.50, 1.0),
        "trim": (0.62, 0.58, 0.50, 1.0),
    },
    "mint_translucent": {
        "shell": (0.62, 0.86, 0.74, 0.95),
        "screen": (0.06, 0.09, 0.08, 1.0),
        "bezel": (0.74, 0.80, 0.78, 1.0),
        "button": (0.30, 0.66, 0.56, 1.0),
        "accent": (0.94, 0.60, 0.40, 1.0),
        "trim": (0.80, 0.90, 0.84, 0.95),
    },
    "neon_arcade": {
        "shell": (0.10, 0.10, 0.16, 1.0),
        "screen": (0.02, 0.06, 0.10, 1.0),
        "bezel": (0.20, 0.22, 0.34, 1.0),
        "button": (0.95, 0.18, 0.55, 1.0),
        "accent": (0.20, 0.90, 0.80, 1.0),
        "trim": (0.55, 0.25, 0.85, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Hand-scale handheld.
# ---------------------------------------------------------------------------
_SLAB_W = 0.170  # psp landscape width (X)
_SLAB_H = 0.074  # psp height (Y)
_SLAB_T = 0.020  # slab thickness (Z)

_CTRL_W = 0.150  # controller body width (X)
_CTRL_H = 0.092  # controller body depth (Y)
_CTRL_T = 0.046  # controller body thickness (Z)

# Real mechanical press sizes (never scaled).
_BTN_TRAVEL = 0.0015
_BTN_R = 0.0072
_BTN_PROUD = 0.0040
_WELL_DEPTH = 0.0022
_WELL_CLEAR = 0.0012

_COLLAR_R = 0.011
_COLLAR_H = 0.005

# Clamshell. The lower deck is a chunky control body; the upper lid is a slim
# screen panel. Keeping them visibly different thicknesses is what makes the
# folded object read as a clamshell instead of two identical stacked bars.
_DECK_T = 0.023   # lower deck (carries controls, + optional lower screen)
_LID_T = 0.011    # upper screen lid (slim)
_PANEL_T = _LID_T  # back-compat alias (lid panel mesh / inertial)
# Visible hinge barrel: interleaved knuckles along the shared back edge.
_KNUCKLE_R = 0.0052
_KNUCKLE_LEN = 0.020


@dataclass(frozen=True)
class HandheldGameConsoleConfig:
    device_archetype: DeviceArchetype | None = None
    input_cluster: InputCluster | None = None
    screen_form: ScreenForm | None = None
    face_button_count: int | None = None
    palette_style: PaletteStyle = "glossy_blue_psp"
    has_shoulders: bool | None = None
    body_width_scale: float = 1.0
    body_thickness_scale: float = 1.0
    face_cluster_pitch_scale: float = 1.0
    hinge_open_limit_deg: float = 130.0
    name: str = "handheld_game_console"


@dataclass(frozen=True)
class ResolvedHandheldGameConsoleConfig:
    device_archetype: DeviceArchetype
    input_cluster: InputCluster
    screen_form: ScreenForm
    face_button_count: int
    palette_style: PaletteStyle
    has_shoulders: bool
    # Concrete geometry (scaled).
    hx: float  # body footprint half-extent X
    hy: float  # body footprint half-extent Y
    body_t: float
    lid_t: float  # clamshell upper-lid thickness (unused for non-clamshell)
    face_z: float  # front control-surface plane
    face_cluster_pitch_scale: float
    hinge_open_limit_deg: float
    name: str

    @property
    def is_clamshell(self) -> bool:
        return self.device_archetype == "clamshell"

    @property
    def root_part(self) -> str:
        return "lower_panel" if self.is_clamshell else "body"

    @property
    def has_screen(self) -> bool:
        return self.screen_form != "no_screen"

    @property
    def is_dual_screen(self) -> bool:
        # DS-style clamshell: a screen on BOTH the lid and the lower deck.
        return self.screen_form == "dual_screen"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Compatibility gating (spec §slot graph: 互斥/可选/派生).
# ---------------------------------------------------------------------------
def _resolve_compat(
    archetype: DeviceArchetype,
    cluster: InputCluster,
    screen: ScreenForm,
) -> tuple[InputCluster, ScreenForm]:
    """Project (cluster, screen) onto the legal region for the archetype."""
    if archetype == "controller_ergo":
        # A gamepad never carries a large LCD (reads as a handheld) and never a
        # phone-style numeric keypad.
        screen = "no_screen"
        if cluster == "numeric_keypad":
            cluster = "dual_thumbsticks"
    else:
        # no_screen is only legal on the controller; everyone else gets a screen.
        if screen == "no_screen":
            screen = "landscape_lcd"
    # A second (deck) screen only makes sense on the folding clamshell; a slab
    # with two screens reads wrong, so project dual_screen down to a single LCD.
    if archetype != "clamshell" and screen == "dual_screen":
        screen = "landscape_lcd"
    if archetype == "clamshell":
        # The lid folds flat over the lower deck, so the deck carries only LOW
        # profile inputs — a tall thumbstick post or 8-way lever would punch
        # through the closed lid. Project those onto the flat dpad cluster.
        if cluster in ("dual_thumbsticks", "single_8way_joypad_lever"):
            cluster = "dpad_plus_round_buttons"
        # The dual_screen deck reserves its centre for the second screen, so it
        # pairs with the compact dpad(left)+round-buttons(right) layout — the
        # mid-board numeric keypad would collide with the deck screen.
        if screen == "dual_screen" and cluster == "numeric_keypad":
            cluster = "dpad_plus_round_buttons"
    return cluster, screen


def config_from_seed(seed: int) -> HandheldGameConsoleConfig:
    rng = random.Random(seed)
    archetype = rng.choices(DEVICE_ARCHETYPES, weights=[5, 3, 4, 2], k=1)[0]
    cluster = rng.choices(INPUT_CLUSTERS, weights=[5, 3, 2, 2], k=1)[0]
    screen = rng.choices(SCREEN_FORMS, weights=[5, 3, 2, 0], k=1)[0]
    # The clamshell is the only body that can carry a second (deck) screen, so
    # give dual_screen real representation within the clamshell population (it is
    # projected away on every other archetype) — keeps the DS form in the pool.
    if archetype == "clamshell":
        screen = rng.choices(
            ["landscape_lcd", "square_lcd", "dual_screen"], weights=[4, 3, 4], k=1
        )[0]
    cluster, screen = _resolve_compat(archetype, cluster, screen)
    # Weighted N: small N common, large N rare (spec §multiplicity).
    n = rng.choices(
        [2, 3, 4, 6, 5, 7, 8],
        weights=[5, 5, 6, 4, 2, 1, 1],
        k=1,
    )[0]
    has_shoulders = rng.random() < 0.55
    return HandheldGameConsoleConfig(
        device_archetype=archetype,
        input_cluster=cluster,
        screen_form=screen,
        face_button_count=n,
        palette_style=rng.choice(PALETTE_STYLES),
        has_shoulders=has_shoulders,
        body_width_scale=round(rng.uniform(0.90, 1.12), 4),
        body_thickness_scale=round(rng.uniform(0.85, 1.15), 4),
        face_cluster_pitch_scale=round(rng.uniform(0.85, 1.20), 4),
        hinge_open_limit_deg=round(rng.uniform(110.0, 135.0), 2),
        name=f"seeded_handheld_game_console_{seed}",
    )


def resolve_config(
    config: HandheldGameConsoleConfig | None = None,
) -> ResolvedHandheldGameConsoleConfig:
    cfg = config or HandheldGameConsoleConfig()
    archetype = _pick(cfg.device_archetype, DEVICE_ARCHETYPES)
    cluster = _pick(cfg.input_cluster, INPUT_CLUSTERS)
    screen = _pick(cfg.screen_form, SCREEN_FORMS)
    cluster, screen = _resolve_compat(archetype, cluster, screen)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(_clamp(cfg.face_button_count if cfg.face_button_count is not None else 4, N_MIN, N_MAX))
    has_shoulders = bool(cfg.has_shoulders) if cfg.has_shoulders is not None else True
    # The clamshell's top edge IS the lid hinge — a shoulder trigger there would
    # be swallowed by the folded upper panel at the closed pose, so the lid form
    # never carries shoulders.
    if archetype == "clamshell":
        has_shoulders = False

    sw = _clamp(cfg.body_width_scale, 0.90, 1.12)
    st = _clamp(cfg.body_thickness_scale, 0.85, 1.15)
    pitch = _clamp(cfg.face_cluster_pitch_scale, 0.85, 1.20)
    # N=6 (2x2 + lower pair) tightens the pitch ceiling so it never spills the grip.
    if n >= 6:
        pitch = min(pitch, 1.05)

    if archetype == "controller_ergo":
        hx = _CTRL_W * sw / 2.0
        hy = _CTRL_H / 2.0
        body_t = _CTRL_T * st
    elif archetype == "clamshell":
        hx = _SLAB_W * sw / 2.0
        hy = _SLAB_H / 2.0
        body_t = _DECK_T * st  # chunky lower control deck
    else:  # psp_slab / brick_slab
        hx = _SLAB_W * sw / 2.0
        hy = _SLAB_H / 2.0
        body_t = _SLAB_T * st

    # Clamshell lid stays slim and scales gently with thickness, but is always
    # clearly thinner than the deck so deck/lid read as distinct halves.
    lid_t = _clamp(_LID_T * st, 0.009, 0.014)

    face_z = body_t / 2.0 if archetype != "controller_ergo" else body_t / 2.0

    hinge_limit = _clamp(cfg.hinge_open_limit_deg, 110.0, 135.0)

    return ResolvedHandheldGameConsoleConfig(
        device_archetype=archetype,
        input_cluster=cluster,
        screen_form=screen,
        face_button_count=n,
        palette_style=palette,
        has_shoulders=has_shoulders,
        hx=hx,
        hy=hy,
        body_t=body_t,
        lid_t=lid_t,
        face_z=face_z,
        face_cluster_pitch_scale=pitch,
        hinge_open_limit_deg=hinge_limit,
        name=cfg.name or "handheld_game_console",
    )


def with_overrides(
    config: HandheldGameConsoleConfig, **kwargs: object
) -> HandheldGameConsoleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: HandheldGameConsoleConfig | ResolvedHandheldGameConsoleConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedHandheldGameConsoleConfig)
        else resolve_config(config)
    )
    return (
        ("device_archetype", r.device_archetype),
        ("input_cluster", r.input_cluster),
        ("screen_form", r.screen_form),
        ("face_buttons", f"n{r.face_button_count}"),
        ("shoulders", "paired" if r.has_shoulders else "none"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------
def _screen_box(r: ResolvedHandheldGameConsoleConfig) -> tuple[float, float, float, float]:
    """(cx, cy, w, h) of the screen footprint on the control face.

    For the dual_screen clamshell this is the LID (upper) screen — a full
    landscape panel; the smaller lower-deck screen uses ``_deck_screen_box``.
    """
    if r.screen_form in ("landscape_lcd", "dual_screen"):
        w = min(2.0 * r.hx * 0.46, 0.090)
        h = min(2.0 * r.hy * 0.62, 0.048)
        return 0.0, r.hy * 0.10, w, h
    # square_lcd: smaller near-square, pushed toward +Y.
    s = min(2.0 * r.hx * 0.34, 2.0 * r.hy * 0.62, 0.052)
    return 0.0, r.hy * 0.18, s, s


def _deck_screen_box(r: ResolvedHandheldGameConsoleConfig) -> tuple[float, float, float, float]:
    """(cx, cy, w, h) of the SECOND (lower-deck) screen on a dual_screen
    clamshell — a smaller centred panel that fits between the flanking dpad and
    round-button clusters."""
    w = min(2.0 * r.hx * 0.34, 0.058)
    h = min(2.0 * r.hy * 0.48, 0.036)
    return 0.0, r.hy * 0.12, w, h


def _dpad_center(r: ResolvedHandheldGameConsoleConfig) -> tuple[float, float]:
    return -r.hx * 0.66, r.hy * 0.05


def _face_cluster_center(r: ResolvedHandheldGameConsoleConfig) -> tuple[float, float]:
    # The numeric keypad occupies the mid-board, so push the round face cluster
    # hard to the right grip to keep it clear of the keypad keys.
    fx = 0.78 if r.input_cluster == "numeric_keypad" else 0.66
    return r.hx * fx, r.hy * 0.05


def _face_offsets(r: ResolvedHandheldGameConsoleConfig) -> list[tuple[float, float]]:
    """N→layout table for the round face buttons (spec §multiplicity)."""
    n = r.face_button_count
    pitch = 0.011 * r.face_cluster_pitch_scale
    if n == 2:
        return [((i - 0.5) * 2.0 * pitch, 0.0) for i in range(2)]
    if n == 3:
        return [
            (pitch * math.cos(math.radians(90.0 + i * 120.0)),
             pitch * math.sin(math.radians(90.0 + i * 120.0)))
            for i in range(3)
        ]
    if n == 4:
        return [(0.0, pitch), (pitch, 0.0), (0.0, -pitch), (-pitch, 0.0)]
    if n == 6:
        # 2 columns x 2 rows + lower pair (classic 6-button).
        cols = (-pitch, pitch)
        rows = (pitch, 0.0, -pitch)
        return [(cx, ry) for ry in rows for cx in cols][:6]
    # 5 / 7 / 8 generic ring fallback.
    rr = pitch * 1.3
    return [
        (rr * math.cos(math.radians(90.0 + i * 360.0 / n)),
         rr * math.sin(math.radians(90.0 + i * 360.0 / n)))
        for i in range(n)
    ]


def _shoulder_specs(r: ResolvedHandheldGameConsoleConfig) -> list[tuple[str, float]]:
    return [("shoulder_l", -1.0), ("shoulder_r", 1.0)]


# ---------------------------------------------------------------------------
# Geometry builders
# ---------------------------------------------------------------------------
def _rounded_slab(width: float, length: float, height: float, radius: float):
    return (
        cq.Workplane("XY")
        .box(width, length, height, centered=(True, True, True))
        .edges("|Z")
        .fillet(min(radius, 0.49 * min(width, length)))
    )


def _build_body_mesh(r: ResolvedHandheldGameConsoleConfig, *, assets):
    """Root shell: rounded slab/panel with screen recess + control wells."""
    if r.device_archetype == "controller_ergo":
        # Build the whole footprint (central deck + two grip horns) as ONE 2-D
        # profile and extrude it once. Unioning separate 3-D boxes leaves a
        # coplanar weld seam that tessellates into vertex-disjoint mesh islands;
        # a single planar profile + single extrude is one watertight shell.
        gw = r.hx * 0.42
        gl = r.hy * 0.62
        sk = cq.Sketch().rect(2.0 * r.hx, 2.0 * r.hy)
        for sx in (-1.0, 1.0):
            sk = sk.push([(sx * r.hx * 0.62, -r.hy * 0.30)]).rect(gw, gl).reset()
        sk = sk.clean()
        body = (
            cq.Workplane("XY")
            .placeSketch(sk)
            .extrude(r.body_t)
            .translate((0.0, 0.0, -r.body_t / 2.0))
        )
    elif r.device_archetype == "brick_slab":
        body = _rounded_slab(2.0 * r.hx, 2.0 * r.hy, r.body_t, 0.010)
    else:  # psp_slab / clamshell lower
        if r.device_archetype == "psp_slab":
            # Single 2-D profile: slab + two side grip rails, extruded once.
            rail_w = 0.044
            sk = cq.Sketch().rect(2.0 * r.hx, 2.0 * r.hy)
            for sx in (-1.0, 1.0):
                sk = sk.push([(sx * (r.hx - 0.012), 0.0)]).rect(
                    rail_w, 2.0 * r.hy + 0.004
                ).reset()
            sk = sk.clean()
            body = (
                cq.Workplane("XY")
                .placeSketch(sk)
                .extrude(r.body_t)
                .translate((0.0, 0.0, -r.body_t / 2.0))
            )
        else:  # clamshell lower
            body = _rounded_slab(2.0 * r.hx, 2.0 * r.hy, r.body_t, 0.012)

    # Screen recess (only when the screen lives on this body, i.e. non-clamshell).
    if r.has_screen and not r.is_clamshell:
        cx, cy, sw, sh = _screen_box(r)
        body = body.cut(
            cq.Workplane("XY")
            .workplane(offset=r.face_z)
            .center(cx, cy)
            .rect(sw + 0.010, sh + 0.010)
            .extrude(-0.004)
        )

    # Dual-screen clamshell: the lower deck also carries a (smaller) screen well
    # centred between the flanking control clusters.
    if r.is_clamshell and r.is_dual_screen:
        dcx, dcy, dsw, dsh = _deck_screen_box(r)
        body = body.cut(
            cq.Workplane("XY")
            .workplane(offset=r.face_z)
            .center(dcx, dcy)
            .rect(dsw + 0.010, dsh + 0.010)
            .extrude(-0.004)
        )

    # Face-button wells.
    fcx, fcy = _face_cluster_center(r)
    for ox, oy in _face_offsets(r):
        body = body.cut(
            cq.Workplane("XY")
            .workplane(offset=r.face_z)
            .center(fcx + ox, fcy + oy)
            .circle(_BTN_R + _WELL_CLEAR)
            .extrude(-_WELL_DEPTH)
        )

    return mesh_from_cadquery(body, "shell", assets=assets)


def _build_upper_panel_mesh(r: ResolvedHandheldGameConsoleConfig, *, assets):
    """Clamshell upper panel (carries the screen) built in its own frame:
    hinge edge at y=0, panel extends in -Y so it folds DOWN OVER the lower deck
    when closed; its inner (screen) face points down (-Z, toward the lower).
    Building it over the lower deck means opening the hinge swings the far edge
    well clear of the body (large, unambiguous lift)."""
    panel = (
        cq.Workplane("XY")
        .center(0.0, -r.hy)
        .box(2.0 * r.hx, 2.0 * r.hy, r.lid_t, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.012)
        .translate((0.0, 0.0, r.lid_t / 2.0))
    )
    return mesh_from_cadquery(panel, "upper_shell", assets=assets)


def _hinge_knuckle_mesh(name: str, *, assets):
    """A single cylindrical hinge knuckle, axis along X (the shared back edge)."""
    knuckle = (
        cq.Workplane("YZ")
        .circle(_KNUCKLE_R)
        .extrude(_KNUCKLE_LEN)
        .translate((-_KNUCKLE_LEN / 2.0, 0.0, 0.0))
    )
    return mesh_from_cadquery(knuckle, name, assets=assets)


def _build_face_button_mesh(name: str, *, assets):
    cap = DomeGeometry(_BTN_R, radial_segments=22, height_segments=10).scale(1.0, 1.0, 0.5)
    cap.translate(0.0, 0.0, _WELL_DEPTH)
    # Seating stem reaches well below the control face into solid body material
    # (past any local recess) so the captured button is supported at rest.
    stem_h = _WELL_DEPTH + _PRESS_SEAT_DROP
    stem = CylinderGeometry(_BTN_R * 0.9, stem_h, radial_segments=18)
    stem.translate(0.0, 0.0, _WELL_DEPTH - stem_h / 2.0)
    cap.merge(stem)
    return mesh_from_geometry(cap, name)


def _build_dpad_mesh(name: str, *, assets):
    arm_w, arm_l, h = 0.0085, 0.024, 0.006
    horiz = cq.Workplane("XY").box(arm_l, arm_w, h)
    vert = cq.Workplane("XY").box(arm_w, arm_l, h)
    cross = horiz.union(vert).edges("|Z").fillet(0.0018)
    return mesh_from_cadquery(cross, name, assets=assets)


# The seated sticks/lever pivot on a raised collar at the control face; their
# post must reach down through the collar into the body so the part is grounded
# (not hovering above the collar) at the rest pose.
_STICK_SEAT_DROP = 0.0060


def _build_thumbstick_mesh(name: str):
    # Post spans from below the collar (into the body) up to the cap.
    post_top = 0.016
    post_bot = -_STICK_SEAT_DROP
    post_h = post_top - post_bot
    post = CylinderGeometry(0.0055, post_h, radial_segments=20)
    post.translate(0.0, 0.0, (post_top + post_bot) / 2.0)
    cap = CylinderGeometry(0.011, 0.006, radial_segments=24)
    cap.translate(0.0, 0.0, 0.018)
    post.merge(cap)
    return mesh_from_geometry(post, name)


def _build_lever_mesh(name: str):
    shaft_top = 0.026
    shaft_bot = -_STICK_SEAT_DROP
    shaft_h = shaft_top - shaft_bot
    shaft = CylinderGeometry(0.004, shaft_h, radial_segments=18)
    shaft.translate(0.0, 0.0, (shaft_top + shaft_bot) / 2.0)
    ball = DomeGeometry(0.010, radial_segments=20, height_segments=12)
    ball.translate(0.0, 0.0, 0.026)
    shaft.merge(ball)
    return mesh_from_geometry(shaft, name)


# A press part's underside must reach below the deepest local body cavity (the
# screen recess is cut ~0.004 down from the control face) so it always seats on
# solid material at the rest pose — otherwise it reads as a floating island.
_PRESS_SEAT_DROP = 0.0050


def _build_key_mesh(name: str, *, assets):
    height = _BTN_PROUD + _WELL_DEPTH
    # Visible square cap above the face plus a square seating stem that sinks down
    # into the body (past any screen recess) so the key is supported, not hovering.
    key = (
        cq.Workplane("XY")
        .box(0.012, 0.012, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.003)
        .edges(">Z")
        .fillet(0.0006)
    )
    stem = (
        cq.Workplane("XY")
        .workplane(offset=-_PRESS_SEAT_DROP)
        .rect(0.0085, 0.0085)
        .extrude(_PRESS_SEAT_DROP + 0.0005)
    )
    key = key.union(stem)
    return mesh_from_cadquery(key, name, assets=assets)


def _build_shoulder_mesh(name: str, *, assets):
    bar = (
        cq.Workplane("XY")
        .center(0.0, 0.006)
        .box(0.034, 0.012, 0.010)
        .edges("|X")
        .fillet(0.004)
        .edges("|Z")
        .fillet(0.004)
        .translate((0.0, -0.002, 0.008))
    )
    return mesh_from_cadquery(bar, name, assets=assets)


# ---------------------------------------------------------------------------
# Emitters
# ---------------------------------------------------------------------------
def _emit_screen(model, r, root, mats, *, assets) -> None:
    """Screen + bezel as fixed visuals on the carrier (body or upper_panel)."""
    if not r.has_screen:
        # no_screen: a small center logo disc trim instead.
        root.visual(
            Cylinder(0.008, 0.0015),
            origin=Origin(xyz=(0.0, r.hy * 0.05, r.face_z - 0.0005)),
            material=mats["trim"],
            name="logo_disc", material_class_id=("plastic.frosted_translucent" if r.palette_style == "mint_translucent" else "metal.paint_coated"),
        )
        return

    cx, cy, sw, sh = _screen_box(r)
    if r.is_clamshell:
        # Upper panel extends in -Y from the hinge; centre the screen on it and
        # sit it just above the inner (z=0) face, which points down at the lower.
        carrier = root  # upper_panel part passed in
        cy = -r.hy
        # The panel inner face is at z=0 (pointing down at the lower deck). Sit the
        # screen + bezels straddling that face so their surfaces actually meet the
        # panel skin (a fully-embedded interior block reads as a floating island).
        scr_z = -0.0010
        screen_top = scr_z
        bez_z = -0.0008
    else:
        carrier = root
        scr_z = r.face_z - 0.005
        screen_top = scr_z
        bez_z = r.face_z - 0.0035

    carrier.visual(
        Box((sw, sh, 0.004)),
        origin=Origin(xyz=(cx, cy, screen_top)),
        material=mats["screen"],
        name="screen", material_class_id="tech.emissive_surface",
    )
    bez_t = 0.0020
    hw = sw / 2.0 + 0.003
    hh = sh / 2.0 + 0.003
    for nm, sz, off in (
        ("bezel_top", (sw + 0.008, bez_t, 0.003), (0.0, hh, 0.0)),
        ("bezel_bot", (sw + 0.008, bez_t, 0.003), (0.0, -hh, 0.0)),
        ("bezel_left", (bez_t, sh + 0.008, 0.003), (-hw, 0.0, 0.0)),
        ("bezel_right", (bez_t, sh + 0.008, 0.003), (hw, 0.0, 0.0)),
    ):
        carrier.visual(
            Box(sz),
            origin=Origin(xyz=(cx + off[0], cy + off[1], bez_z)),
            material=mats["bezel"],
            name=nm, material_class_id="plastic.opaque_glossy_molded",
        )


def _emit_deck_screen(model, r, root, mats, *, assets) -> None:
    """Second screen on the lower deck for the DS-style dual_screen clamshell."""
    cx, cy, sw, sh = _deck_screen_box(r)
    scr_z = r.face_z - 0.005
    bez_z = r.face_z - 0.0035
    root.visual(
        Box((sw, sh, 0.004)),
        origin=Origin(xyz=(cx, cy, scr_z)),
        material=mats["screen"],
        name="deck_screen", material_class_id="tech.emissive_surface",
    )
    bez_t = 0.0020
    hw = sw / 2.0 + 0.003
    hh = sh / 2.0 + 0.003
    for nm, sz, off in (
        ("deck_bezel_top", (sw + 0.008, bez_t, 0.003), (0.0, hh, 0.0)),
        ("deck_bezel_bot", (sw + 0.008, bez_t, 0.003), (0.0, -hh, 0.0)),
        ("deck_bezel_left", (bez_t, sh + 0.008, 0.003), (-hw, 0.0, 0.0)),
        ("deck_bezel_right", (bez_t, sh + 0.008, 0.003), (hw, 0.0, 0.0)),
    ):
        root.visual(
            Box(sz),
            origin=Origin(xyz=(cx + off[0], cy + off[1], bez_z)),
            material=mats["bezel"],
            name=nm, material_class_id="plastic.opaque_glossy_molded",
        )


def _emit_clamshell_upper(model, r, lower, mats, *, assets) -> str:
    upper = model.part("upper_panel")
    upper.visual(_build_upper_panel_mesh(r, assets=assets), material=mats["shell"], name="upper_shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"glossy_blue_psp", "brick_red_yellow", "retro_cream", "mint_translucent", "neon_arcade"} else "plastic.opaque_generic"))
    upper.inertial = Inertial.from_geometry(
        Box((2.0 * r.hx, 2.0 * r.hy, r.lid_t)),
        mass=0.10,
        origin=Origin(xyz=(0.0, -r.hy, r.lid_t / 2.0)),
    )
    # Screen on the upper panel inner face.
    _emit_screen(model, r, upper, mats, assets=assets)

    # Hinge line at the shared back-top edge of the lower deck.
    hinge_y = r.hy
    hinge_z = r.face_z

    # Visible interleaved barrel knuckles, all coaxial with the hinge axis (X)
    # so they read as a real cylindrical hinge. Deck emits the 3 outer/centre
    # knuckles (fixed visuals on the lower deck); the lid emits the 2 that fill
    # the gaps (visuals on the upper panel, at its local hinge origin y=z=0).
    _kn_pitch = 0.021
    _kn_centers = [(_i - 2) * _kn_pitch for _i in range(5)]
    for _i, _xc in enumerate(_kn_centers):
        if _i % 2 == 0:  # 3 deck knuckles
            lower.visual(
                _hinge_knuckle_mesh(f"hinge_knuckle_deck_{_i}", assets=assets),
                origin=Origin(xyz=(_xc, hinge_y, hinge_z)),
                material=mats["trim"],
                name=f"hinge_knuckle_deck_{_i}", material_class_id=("plastic.frosted_translucent" if r.palette_style == "mint_translucent" else "metal.paint_coated"),
            )
        else:  # 2 lid knuckles, at the lid's local hinge origin
            upper.visual(
                _hinge_knuckle_mesh(f"hinge_knuckle_lid_{_i}", assets=assets),
                origin=Origin(xyz=(_xc, 0.0, 0.0)),
                material=mats["trim"],
                name=f"hinge_knuckle_lid_{_i}", material_class_id=("plastic.frosted_translucent" if r.palette_style == "mint_translucent" else "metal.paint_coated"),
            )

    model.articulation(
        "lower_to_upper",
        ArticulationType.REVOLUTE,
        parent=lower,
        child=upper,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=5.0,
            velocity=2.0,
            lower=0.0,
            upper=math.radians(r.hinge_open_limit_deg),
        ),
    )
    return "upper_panel"


def _emit_face_buttons(model, r, root, mats, *, assets) -> list[str]:
    fcx, fcy = _face_cluster_center(r)
    height = _BTN_PROUD + _WELL_DEPTH
    cache = None
    names: list[str] = []
    for i, (ox, oy) in enumerate(_face_offsets(r)):
        name = f"face_btn_{i}"
        btn = model.part(name)
        if cache is None:
            cache = _build_face_button_mesh(name, assets=assets)
            mesh = cache
        else:
            mesh = _build_face_button_mesh(name, assets=assets)
        btn.visual(mesh, material=mats["button"], name=name, material_class_id="plastic.opaque_glossy_molded")
        btn.inertial = Inertial.from_geometry(
            Cylinder(_BTN_R, height), mass=0.0015,
            origin=Origin(xyz=(0.0, 0.0, height / 2.0)),
        )
        model.articulation(
            f"{r.root_part}_to_{name}",
            ArticulationType.PRISMATIC,
            parent=root,
            child=btn,
            origin=Origin(xyz=(fcx + ox, fcy + oy, r.face_z - _WELL_DEPTH)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=_BTN_TRAVEL),
        )
        names.append(name)
    return names


def _emit_dpad(model, r, root, mats, *, assets, rocker: bool) -> list[str]:
    dcx, dcy = _dpad_center(r)
    dpad = model.part("dpad")
    dpad.visual(_build_dpad_mesh("dpad", assets=assets), material=mats["accent"], name="dpad", material_class_id="plastic.opaque_glossy_molded")
    dpad.inertial = Inertial.from_geometry(Box((0.026, 0.026, 0.006)), mass=0.006)
    if rocker:
        model.articulation(
            f"{r.root_part}_to_dpad",
            ArticulationType.REVOLUTE,
            parent=root,
            child=dpad,
            origin=Origin(xyz=(dcx, dcy, r.face_z + 0.001)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-0.2, upper=0.2),
        )
    else:
        model.articulation(
            f"{r.root_part}_to_dpad",
            ArticulationType.PRISMATIC,
            parent=root,
            child=dpad,
            origin=Origin(xyz=(dcx, dcy, r.face_z + 0.001)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=0.05, lower=0.0, upper=0.0025),
        )
    return ["dpad"]


def _emit_thumbsticks(model, r, root, mats, *, assets) -> list[str]:
    centers = {"left_thumbstick": (-r.hx * 0.40, r.hy * 0.18),
               "right_thumbstick": (r.hx * 0.30, -r.hy * 0.18)}
    names: list[str] = []
    for name, (cx, cy) in centers.items():
        # Fixed dish collar on the body.
        root.visual(
            Cylinder(_COLLAR_R, _COLLAR_H),
            origin=Origin(xyz=(cx, cy, r.face_z - 0.001)),
            material=mats["accent"],
            name=f"{name}_collar", material_class_id="plastic.opaque_glossy_molded",
        )
        stick = model.part(name)
        stick.visual(_build_thumbstick_mesh(name), material=mats["accent"], name=name, material_class_id="rubber.smooth_plain")
        stick.inertial = Inertial.from_geometry(
            Cylinder(0.011, 0.024), mass=0.004, origin=Origin(xyz=(0.0, 0.0, 0.012)),
        )
        model.articulation(
            f"{r.root_part}_to_{name}",
            ArticulationType.REVOLUTE,
            parent=root,
            child=stick,
            origin=Origin(xyz=(cx, cy, r.face_z + _COLLAR_H)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-0.35, upper=0.35),
        )
        names.append(name)
    return names


def _emit_joypad_lever(model, r, root, mats, *, assets) -> list[str]:
    dcx, dcy = _dpad_center(r)
    # Raised collar to seat the lever.
    root.visual(
        Cylinder(_COLLAR_R, _COLLAR_H),
        origin=Origin(xyz=(dcx, dcy, r.face_z - 0.001)),
        material=mats["accent"],
        name="joystick_collar", material_class_id="plastic.opaque_glossy_molded",
    )
    lever = model.part("joystick")
    lever.visual(_build_lever_mesh("joystick"), material=mats["accent"], name="joystick", material_class_id="plastic.opaque_glossy_molded")
    lever.inertial = Inertial.from_geometry(
        Cylinder(0.010, 0.036), mass=0.006, origin=Origin(xyz=(0.0, 0.0, 0.018)),
    )
    model.articulation(
        f"{r.root_part}_to_joystick",
        ArticulationType.REVOLUTE,
        parent=root,
        child=lever,
        origin=Origin(xyz=(dcx, dcy, r.face_z + _COLLAR_H)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.5, velocity=2.0,
            lower=-math.radians(20.0), upper=math.radians(20.0),
        ),
    )
    return ["joystick"]


def _emit_numeric_keypad(model, r, root, mats, *, assets) -> list[str]:
    """A 4x3 phone-style press grid, placed below the screen, alongside a dpad."""
    n_rows, n_cols = 4, 3
    pitch = 0.0125
    grid_cx = r.hx * 0.12
    grid_cy = -r.hy * 0.10
    height = _BTN_PROUD + _WELL_DEPTH
    names: list[str] = []
    k = 0
    for i in range(n_rows):
        for j in range(n_cols):
            kx = grid_cx + (j - (n_cols - 1) / 2.0) * pitch
            ky = grid_cy - (i - (n_rows - 1) / 2.0) * pitch
            name = f"key_{k}"
            key = model.part(name)
            key.visual(_build_key_mesh(name, assets=assets), material=mats["button"], name=name, material_class_id="plastic.opaque_glossy_molded")
            key.inertial = Inertial.from_geometry(
                Box((0.012, 0.012, height)), mass=0.0015,
                origin=Origin(xyz=(0.0, 0.0, height / 2.0)),
            )
            model.articulation(
                f"{r.root_part}_to_{name}",
                ArticulationType.PRISMATIC,
                parent=root,
                child=key,
                origin=Origin(xyz=(kx, ky, r.face_z - _WELL_DEPTH)),
                axis=(0.0, 0.0, -1.0),
                motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=0.002),
            )
            names.append(name)
            k += 1
    return names


def _emit_input_cluster(model, r, root, mats, *, assets) -> list[str]:
    rocker = r.device_archetype in ("brick_slab",)
    if r.input_cluster == "dpad_plus_round_buttons":
        return _emit_dpad(model, r, root, mats, assets=assets, rocker=rocker)
    if r.input_cluster == "dual_thumbsticks":
        names = _emit_thumbsticks(model, r, root, mats, assets=assets)
        names += _emit_dpad(model, r, root, mats, assets=assets, rocker=rocker)
        return names
    if r.input_cluster == "single_8way_joypad_lever":
        return _emit_joypad_lever(model, r, root, mats, assets=assets)
    if r.input_cluster == "numeric_keypad":
        names = _emit_numeric_keypad(model, r, root, mats, assets=assets)
        names += _emit_dpad(model, r, root, mats, assets=assets, rocker=rocker)
        return names
    return []


def _emit_shoulders(model, r, root, mats, *, assets) -> list[str]:
    if not r.has_shoulders:
        return []
    top_y = r.hy
    back_z = -r.body_t / 2.0
    names: list[str] = []
    for name, sx in _shoulder_specs(r):
        sh = model.part(name)
        sh.visual(_build_shoulder_mesh(name, assets=assets), material=mats["shell"], name=name, material_class_id=("plastic.frosted_translucent" if r.palette_style in {"glossy_blue_psp", "brick_red_yellow", "retro_cream", "mint_translucent", "neon_arcade"} else "plastic.opaque_generic"))
        sh.inertial = Inertial.from_geometry(Box((0.030, 0.010, 0.012)), mass=0.004)
        model.articulation(
            f"{r.root_part}_to_{name}",
            ArticulationType.REVOLUTE,
            parent=root,
            child=sh,
            origin=Origin(xyz=(sx * r.hx * 0.62, top_y - 0.004, back_z + 0.006)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.radians(18.0)),
        )
        names.append(name)
    return names


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_handheld_game_console(
    config: HandheldGameConsoleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"hgc_{key}_{r.palette_style}", rgba=palette[key])
        for key in ("shell", "screen", "bezel", "button", "accent", "trim")
    }

    root = model.part(r.root_part)
    root.visual(_build_body_mesh(r, assets=assets), material=mats["shell"], name="shell", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"glossy_blue_psp", "brick_red_yellow", "retro_cream", "mint_translucent", "neon_arcade"} else "plastic.opaque_generic"))
    root.inertial = Inertial.from_geometry(
        Box((2.0 * r.hx, 2.0 * r.hy, r.body_t)),
        mass=0.24,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    if r.is_clamshell:
        # Screen lives on the upper panel; lower carries controls. The DS-style
        # dual_screen clamshell additionally carries a second screen on the deck.
        _emit_clamshell_upper(model, r, root, mats, assets=assets)
        if r.is_dual_screen:
            _emit_deck_screen(model, r, root, mats, assets=assets)
    else:
        _emit_screen(model, r, root, mats, assets=assets)

    _emit_input_cluster(model, r, root, mats, assets=assets)
    _emit_face_buttons(model, r, root, mats, assets=assets)
    _emit_shoulders(model, r, root, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_handheld_game_console(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_handheld_game_console(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_handheld_game_console_tests(
    object_model: ArticulatedObject,
    config: HandheldGameConsoleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    root = object_model.get_part(r.root_part)

    # --- captured-pin / seated allowances. ---
    n = r.face_button_count
    for i in range(n):
        btn = object_model.get_part(f"face_btn_{i}")
        ctx.allow_overlap(
            btn, root,
            reason="face button dome+stem seats into its control-face well (captured press).",
        )
    if r.input_cluster in ("dpad_plus_round_buttons", "dual_thumbsticks", "numeric_keypad"):
        ctx.allow_overlap(
            object_model.get_part("dpad"), root,
            reason="dpad cross seats into its shell aperture.",
        )
    if r.input_cluster == "dual_thumbsticks":
        for name in ("left_thumbstick", "right_thumbstick"):
            ctx.allow_overlap(
                object_model.get_part(name), root,
                reason="thumbstick post seats inside its dish collar on the shell.",
            )
    if r.input_cluster == "single_8way_joypad_lever":
        ctx.allow_overlap(
            object_model.get_part("joystick"), root,
            reason="joypad lever shaft seats inside its raised collar on the shell.",
        )
    if r.input_cluster == "numeric_keypad":
        for i in range(12):
            ctx.allow_overlap(
                object_model.get_part(f"key_{i}"), root,
                reason="keypad key seats into its control-face well.",
            )
    if r.has_shoulders:
        for name in ("shoulder_l", "shoulder_r"):
            ctx.allow_overlap(
                object_model.get_part(name), root,
                reason="shoulder trigger wraps the top-edge hinge of the shell.",
            )
    if r.is_clamshell:
        upper = object_model.get_part("upper_panel")
        ctx.allow_overlap(
            upper, root,
            reason="clamshell upper panel folds flat over the lower panel + controls (captured hinge).",
        )
        # At the closed (zero) pose the lid rests on the low-profile deck controls;
        # they are captured beneath the folded lid (open the hinge to clear them).
        clam_controls = [f"face_btn_{i}" for i in range(n)] + ["dpad"]
        if r.input_cluster == "numeric_keypad":
            clam_controls += [f"key_{i}" for i in range(12)]
        for cname in clam_controls:
            ctx.allow_overlap(
                upper, object_model.get_part(cname),
                reason="closed clamshell lid rests over the captured low-profile deck control.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # --- face-button multiplicity. ---
    ctx.check(
        "face buttons match N",
        all(f"face_btn_{i}" in {p.name for p in object_model.parts} for i in range(n))
        and f"face_btn_{n}" not in {p.name for p in object_model.parts},
        details=f"N={n}",
    )
    for i in range(n):
        j = object_model.get_articulation(f"{r.root_part}_to_face_btn_{i}")
        ctx.check(
            f"face_btn_{i} is PRISMATIC pressing -Z",
            j.articulation_type == ArticulationType.PRISMATIC and round(j.axis[2], 3) == -1.0,
            details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
        )

    # --- a face button presses straight down. ---
    b0 = object_model.get_part("face_btn_0")
    j0 = object_model.get_articulation(f"{r.root_part}_to_face_btn_0")
    rest = ctx.part_world_position(b0)
    with ctx.pose({j0: _BTN_TRAVEL}):
        pressed = ctx.part_world_position(b0)
    if rest is not None and pressed is not None:
        drop = rest[2] - pressed[2]
        ctx.check(
            "pressing face_btn_0 moves it down by the stroke",
            abs(drop - _BTN_TRAVEL) < 1e-4 and drop > 0.0,
            details=f"drop={drop:.5f} expected={_BTN_TRAVEL:.5f}",
        )

    # --- screen presence per screen_form. ---
    carrier = object_model.get_part("upper_panel") if r.is_clamshell else root
    if r.has_screen:
        ctx.check(
            "screen is a fixed visual on the carrier",
            "screen" in {v.name for v in carrier.visuals},
            details=str([v.name for v in carrier.visuals]),
        )
    else:
        ctx.check(
            "no_screen carries only a logo trim",
            "screen" not in {v.name for v in root.visuals}
            and "logo_disc" in {v.name for v in root.visuals},
            details=str([v.name for v in root.visuals]),
        )

    # --- dual_screen clamshell carries a SECOND screen on the deck. ---
    if r.is_dual_screen:
        ctx.check(
            "dual_screen clamshell has a lid screen AND a deck screen",
            r.is_clamshell
            and "screen" in {v.name for v in object_model.get_part("upper_panel").visuals}
            and "deck_screen" in {v.name for v in root.visuals},
            details=f"lid={[v.name for v in object_model.get_part('upper_panel').visuals]} "
            f"deck={[v.name for v in root.visuals]}",
        )

    # --- compatibility gates. ---
    ctx.check(
        "controller_ergo never carries a screen",
        not (r.device_archetype == "controller_ergo" and r.has_screen),
        details=f"archetype={r.device_archetype} screen={r.screen_form}",
    )
    ctx.check(
        "clamshell always carries a screen",
        not (r.is_clamshell and not r.has_screen),
        details=f"archetype={r.device_archetype} screen={r.screen_form}",
    )
    ctx.check(
        "dual_screen only on the clamshell",
        not (r.is_dual_screen and not r.is_clamshell),
        details=f"archetype={r.device_archetype} screen={r.screen_form}",
    )

    # --- clamshell hinge opens upward. ---
    if r.is_clamshell:
        jh = object_model.get_articulation("lower_to_upper")
        ctx.check(
            "clamshell hinge is REVOLUTE about -X",
            jh.articulation_type == ArticulationType.REVOLUTE and round(jh.axis[0], 3) == -1.0,
            details=f"type={jh.articulation_type} axis={tuple(round(c, 3) for c in jh.axis)}",
        )
        upper = object_model.get_part("upper_panel")
        with ctx.pose({jh: 0.0}):
            a0 = ctx.part_world_aabb(upper)
        with ctx.pose({jh: math.radians(110.0)}):
            a1 = ctx.part_world_aabb(upper)
        if a0 is not None and a1 is not None:
            ctx.check(
                "opening the clamshell lifts the upper panel",
                a1[1][2] > a0[1][2] + 0.01,
                details=f"closed_top={a0[1][2]:.4f} open_top={a1[1][2]:.4f}",
            )
        # The lower control deck must read as a CHUNKIER body than the slim
        # screen lid, otherwise the folded object looks like two identical bars
        # instead of a clamshell.
        ctx.check(
            "clamshell deck is clearly thicker than the lid",
            r.body_t >= r.lid_t * 1.4,
            details=f"deck_t={r.body_t:.4f} lid_t={r.lid_t:.4f}",
        )
        # Visible interleaved barrel knuckles read as a real cylindrical hinge:
        # 3 fixed on the deck, 2 on the lid (loop-emitted, coaxial).
        deck_kn = [v.name for v in root.visuals if v.name.startswith("hinge_knuckle_deck_")]
        lid_kn = [v.name for v in upper.visuals if v.name.startswith("hinge_knuckle_lid_")]
        ctx.check(
            "clamshell hinge shows interleaved barrel knuckles (deck 3 / lid 2)",
            len(deck_kn) == 3 and len(lid_kn) == 2,
            details=f"deck_knuckles={sorted(deck_kn)} lid_knuckles={sorted(lid_kn)}",
        )

    # --- thumbsticks / lever tilt about the seated pivot. ---
    if r.input_cluster == "dual_thumbsticks":
        jt = object_model.get_articulation(f"{r.root_part}_to_left_thumbstick")
        ctx.check(
            "thumbstick is REVOLUTE tilt",
            jt.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={jt.articulation_type}",
        )
    if r.input_cluster == "single_8way_joypad_lever":
        jl = object_model.get_articulation(f"{r.root_part}_to_joystick")
        lever = object_model.get_part("joystick")
        ctx.check(
            "joypad lever is REVOLUTE tilt about +X",
            jl.articulation_type == ArticulationType.REVOLUTE and round(jl.axis[0], 3) == 1.0,
            details=f"type={jl.articulation_type} axis={tuple(round(c, 3) for c in jl.axis)}",
        )
        with ctx.pose({jl: 0.0}):
            l0 = ctx.part_world_aabb(lever)
        with ctx.pose({jl: math.radians(20.0)}):
            l1 = ctx.part_world_aabb(lever)
        if l0 is not None and l1 is not None:
            ymid0 = 0.5 * (l0[0][1] + l0[1][1])
            ymid1 = 0.5 * (l1[0][1] + l1[1][1])
            ctx.check(
                "tilting the lever swings its top",
                abs(ymid1 - ymid0) > 0.001,
                details=f"ymid0={ymid0:.4f} ymid1={ymid1:.4f}",
            )

    # --- optional shoulders on the top edge. ---
    if r.has_shoulders:
        for name in ("shoulder_l", "shoulder_r"):
            js = object_model.get_articulation(f"{r.root_part}_to_{name}")
            ctx.check(
                f"{name} is REVOLUTE about +X (top edge)",
                js.articulation_type == ArticulationType.REVOLUTE and round(js.axis[0], 3) == 1.0,
                details=f"type={js.articulation_type} axis={tuple(round(c, 3) for c in js.axis)}",
            )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "HandheldGameConsoleConfig",
    "ResolvedHandheldGameConsoleConfig",
    "build_handheld_game_console",
    "build_seeded_handheld_game_console",
    "config_from_seed",
    "resolve_config",
    "run_handheld_game_console_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
