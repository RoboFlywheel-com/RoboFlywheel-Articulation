# SPDX-License-Identifier: Apache-2.0

"""Bedside nightstand / storage cabinet — modular procedural template.

NOTE on the slug name: "bedside" here = **bedside nightstand / 床头收纳柜**: a
grounded hollow ``carcass`` shell (gray-lacquered panels with a three-sided
gallery lip top, side + back panels, inner runner rails / bottom panel) sitting
on one of four **base supports**, with one of four interior **storage
mechanisms**, whose storage faces wear one of three **handle** styles. It is a
small single-width nightstand (~0.65 W x 0.45 D x 0.45 H m), NOT a tall
multi-column dresser / chest of drawers (see
``drawer_cabinet_with_sliding_drawers``).

World layout (inherited from every 5-star source): front faces +X (back at
x=0, front at x=D), width along Y, height along +Z, object grounded at z=0.

Structure (pattern = ``mixed``): a single root ``carcass`` part with four
module axes:

  * ``base_support`` (4): inset_floating_plinth / four_splayed_legs /
    solid_toe_kick_box / hairpin_metal_legs — carcass-local visuals below the
    body, deciding the lift ``BODY_BOT_Z`` and overall ``H``; NO joint.
  * ``storage_mechanism`` (4) — the only joint-topology axis:
      - two_prismatic_drawers : N ``drawer_i`` children, each
        ``carcass_to_drawer_i`` PRISMATIC about +X.
      - hinged_cabinet_door   : single ``door`` child, ``carcass_to_door``
        REVOLUTE about +Z (side hinge, swings outward).
      - drop_down_flap_door   : single ``flap_door`` child,
        ``carcass_to_flap_door`` REVOLUTE about +Y (bottom hinge, drops down).
      - open_niche_over_drawer: a fixed ``divider_shelf`` carcass visual over a
        single ``drawer`` (1 PRISMATIC +X), N forced to 1.
  * ``handle`` (3): chrome_bar_on_posts / recessed_finger_pull / round_knobs —
    inline non-moving visuals on the storage face (Rule 1, no joint).
  * ``drawer_count`` (N in [1,4]): a multiplicity axis. N drawers stacked along
    +Z; only free under two_prismatic_drawers (door/flap force N=0, niche N=1).
    Encoded into the slot_choice tuple as ``("drawer_count", f"n{N}")``.

All drawer slides / door hinges are captured-slide / hinge-at-edge geometry, so
those joints omit ``MatingContract`` (grandfathered) and are guarded by the
flat articulation-origin baseline + element-scoped/whole-part ``allow_overlap``
(mirroring each source record's run_tests block).

Per-module 5-star sources (see spec §14): parent c9162b4f (carcass + plinth +
two_prismatic_drawers + chrome_bar), 65751baf (four_splayed_legs LatheGeometry),
6dddcda5 (solid_toe_kick_box), dcdcb159 (hairpin_metal_legs tube_from_spline),
02643395 (hinged_cabinet_door), 2bf8cef6 (drop_down_flap_door), bd3941ca
(open_niche_over_drawer), 968aa0b6 (recessed_finger_pull cadquery), 0504431c
(round_knobs lathe), b8d0c6c4 (drawer_count N=1), 50c223fe (drawer_count N=3).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Other_Bedside.md``
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
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
    tube_from_spline_points,
)

__modular__ = True

BaseSupport = Literal[
    "inset_floating_plinth",
    "four_splayed_legs",
    "solid_toe_kick_box",
    "hairpin_metal_legs",
]
StorageMechanism = Literal[
    "two_prismatic_drawers",
    "hinged_cabinet_door",
    "drop_down_flap_door",
    "open_niche_over_drawer",
]
Handle = Literal["chrome_bar_on_posts", "recessed_finger_pull", "round_knobs"]
PaletteStyle = Literal["gray_lacquer", "warm_walnut", "matte_white", "charcoal_chrome"]

BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "inset_floating_plinth",
    "four_splayed_legs",
    "solid_toe_kick_box",
    "hairpin_metal_legs",
)
STORAGE_MECHANISMS: tuple[StorageMechanism, ...] = (
    "two_prismatic_drawers",
    "hinged_cabinet_door",
    "drop_down_flap_door",
    "open_niche_over_drawer",
)
HANDLES: tuple[Handle, ...] = (
    "chrome_bar_on_posts",
    "recessed_finger_pull",
    "round_knobs",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gray_lacquer",
    "warm_walnut",
    "matte_white",
    "charcoal_chrome",
)

LEGGED_BASES: tuple[BaseSupport, ...] = ("four_splayed_legs", "hairpin_metal_legs")

N_MIN = 1
N_MAX = 4
# Drawer-count weights (spec §8: 1/2 high-frequency, 3 common, 4 long tail).
DRAWER_COUNT_WEIGHTS = (0.32, 0.34, 0.22, 0.12)

# ---------------------------------------------------------------------------
# Palettes. Keys: carcass, plinth (base accent), front (drawer/door face),
# tray (interior box), hardware (handle / knob / chrome bar), leg, accent
# (finger-pull groove shadow). Every .visual material is driven off this map.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gray_lacquer": {
        "carcass": (0.50, 0.52, 0.55, 1.0),
        "plinth": (0.27, 0.28, 0.30, 1.0),
        "front": (0.85, 0.87, 0.88, 1.0),
        "tray": (0.72, 0.74, 0.76, 1.0),
        "hardware": (0.80, 0.82, 0.85, 1.0),
        "leg": (0.35, 0.22, 0.14, 1.0),
        "accent": (0.35, 0.36, 0.38, 1.0),
    },
    "warm_walnut": {
        "carcass": (0.40, 0.27, 0.17, 1.0),
        "plinth": (0.26, 0.17, 0.10, 1.0),
        "front": (0.55, 0.40, 0.26, 1.0),
        "tray": (0.62, 0.50, 0.36, 1.0),
        "hardware": (0.74, 0.62, 0.30, 1.0),
        "leg": (0.22, 0.14, 0.09, 1.0),
        "accent": (0.20, 0.13, 0.08, 1.0),
    },
    "matte_white": {
        "carcass": (0.92, 0.91, 0.88, 1.0),
        "plinth": (0.74, 0.74, 0.72, 1.0),
        "front": (0.97, 0.96, 0.94, 1.0),
        "tray": (0.82, 0.81, 0.78, 1.0),
        "hardware": (0.32, 0.33, 0.35, 1.0),
        "leg": (0.62, 0.50, 0.36, 1.0),
        "accent": (0.58, 0.59, 0.60, 1.0),
    },
    "charcoal_chrome": {
        "carcass": (0.20, 0.21, 0.23, 1.0),
        "plinth": (0.10, 0.10, 0.12, 1.0),
        "front": (0.28, 0.29, 0.31, 1.0),
        "tray": (0.34, 0.35, 0.37, 1.0),
        "hardware": (0.80, 0.82, 0.86, 1.0),
        "leg": (0.66, 0.68, 0.72, 1.0),
        "accent": (0.66, 0.68, 0.72, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), preserved from the parent (c9162b4f).
# Nominal carcass: W=0.650 (Y), D=0.450 (X), body height 0.405.
# ---------------------------------------------------------------------------
_W = 0.650
_D = 0.450
_WALL = 0.018
_LIP = 0.060
_SHELF_THK = 0.016
_CARCASS_BODY_H = 0.405  # carcass body height above the base (parent: 0.450-0.045)

_PLINTH_H = 0.045
_PLINTH_INSET = 0.045
_TOEKICK_BASE_H = 0.055
_TOEKICK_NOTCH_H = 0.025
_TOEKICK_RECESS = 0.038
_LEG_H = 0.120

_FACE_THK = 0.016
_FACE_GAP = 0.010
_FACE_TOP_MARGIN = 0.004
_BOX_D = 0.400
_BOX_W = 0.600
_TRAY_T = 0.012
_TRAVEL = 0.360
_RAIL_LEN = 0.400

# Leg geometry (65751baf).
_LEG_TOP_R = 0.020
_LEG_BOT_R = 0.012
_LEG_INSET = 0.040
_SPLAY_RAD = math.radians(8.0)
# Hairpin geometry (dcdcb159).
_ROD_R = 0.005
_HAIRPIN_SPLAY = 0.052
_HAIRPIN_INSET_X = 0.036
_HAIRPIN_INSET_Y = 0.040

# Finger-pull groove (968aa0b6).
_GROOVE_W = 0.140
_GROOVE_H = 0.014
_GROOVE_DEPTH = 0.010
_GROOVE_LIP = 0.001


@dataclass(frozen=True)
class BedsideConfig:
    base_support: BaseSupport | None = None
    storage_mechanism: StorageMechanism | None = None
    handle: Handle | None = None
    drawer_count: int | None = None
    palette_style: PaletteStyle = "gray_lacquer"
    width_scale: float = 1.0
    depth_scale: float = 1.0
    body_height_scale: float = 1.0
    leg_lift_scale: float = 1.0
    drawer_travel: float = _TRAVEL
    door_open_angle: float = 1.40
    drawer_pitch_scale: float = 1.0
    name: str = "bedside"


@dataclass(frozen=True)
class ResolvedBedsideConfig:
    base_support: BaseSupport
    storage_mechanism: StorageMechanism
    handle: Handle
    drawer_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    w: float  # overall width (Y)
    d: float  # overall depth (X)
    wall: float
    lip: float
    shelf_thk: float
    body_bot_z: float  # carcass body starts here (top of base support)
    carcass_body_h: float
    h: float  # overall height (incl. base lift)
    inner_w: float
    shelf_bot_z: float
    zone_h: float  # storage-face vertical zone height
    leg_h: float
    face_thk: float
    box_d: float
    box_w: float
    tray_t: float
    drawer_travel: float
    door_open_angle: float
    # Drawer stack (two_prismatic_drawers / niche).
    face_h: float
    cz: tuple[float, ...]
    name: str

    @property
    def front_x(self) -> float:
        return self.d


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> BedsideConfig:
    rng = random.Random(seed)
    storage = rng.choice(STORAGE_MECHANISMS)
    if storage == "two_prismatic_drawers":
        drawer_count = rng.choices((1, 2, 3, 4), weights=DRAWER_COUNT_WEIGHTS, k=1)[0]
    elif storage == "open_niche_over_drawer":
        drawer_count = 1
    else:
        drawer_count = 0
    return BedsideConfig(
        base_support=rng.choice(BASE_SUPPORTS),
        storage_mechanism=storage,
        handle=rng.choice(HANDLES),
        drawer_count=drawer_count,
        palette_style=rng.choice(PALETTE_STYLES),
        width_scale=round(rng.uniform(0.85, 1.18), 4),
        depth_scale=round(rng.uniform(0.88, 1.15), 4),
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        leg_lift_scale=round(rng.uniform(0.85, 1.20), 4),
        drawer_travel=round(rng.uniform(0.10, 0.36), 4),
        door_open_angle=round(rng.uniform(0.80 * math.pi / 2.0, 1.45), 4),
        drawer_pitch_scale=round(rng.uniform(0.92, 1.08), 4),
        name=f"seeded_bedside_{seed}",
    )


def resolve_config(config: BedsideConfig | None = None) -> ResolvedBedsideConfig:
    cfg = config or BedsideConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    base_support = _pick(cfg.base_support, BASE_SUPPORTS)
    storage = _pick(cfg.storage_mechanism, STORAGE_MECHANISMS)
    handle = _pick(cfg.handle, HANDLES)

    # --- drawer_count gating (spec §8/§9): only two_prismatic_drawers is free. ---
    if storage == "two_prismatic_drawers":
        n = int(cfg.drawer_count) if cfg.drawer_count is not None else 2
        drawer_count = int(_clamp(n, N_MIN, N_MAX))
    elif storage == "open_niche_over_drawer":
        drawer_count = 1
    else:  # hinged_cabinet_door / drop_down_flap_door
        drawer_count = 0

    # --- continuous scales. ---
    width_scale = _clamp(cfg.width_scale, 0.85, 1.18)
    depth_scale = _clamp(cfg.depth_scale, 0.88, 1.15)
    height_scale = _clamp(cfg.body_height_scale, 0.88, 1.15)
    leg_lift_scale = _clamp(cfg.leg_lift_scale, 0.85, 1.20)

    w = _W * width_scale
    d = _D * depth_scale
    wall = _WALL
    inner_w = w - 2.0 * wall
    carcass_body_h = _CARCASS_BODY_H * height_scale

    # --- base lift -> BODY_BOT_Z + overall H (spec §7). ---
    if base_support in LEGGED_BASES:
        leg_h = _LEG_H * leg_lift_scale
        body_bot_z = leg_h
    elif base_support == "solid_toe_kick_box":
        leg_h = _LEG_H  # unused (no legs)
        body_bot_z = _TOEKICK_BASE_H
    else:  # inset_floating_plinth
        leg_h = _LEG_H
        body_bot_z = _PLINTH_H
    h = body_bot_z + carcass_body_h

    shelf_bot_z = h - _LIP - _SHELF_THK
    zone_h = shelf_bot_z - body_bot_z

    # --- drawer stack derivation (absolute, N-invariant). ---
    box_d = min(_BOX_D, d - wall - 0.020)
    box_w = min(_BOX_W, inner_w - 0.010)
    pitch_scale = _clamp(cfg.drawer_pitch_scale, 0.92, 1.08)

    if storage == "open_niche_over_drawer":
        # Upper fixed niche (NICHE_H) over a single lower drawer (bd3941ca).
        niche_h = min(0.155, zone_h * 0.48)
        divider_thk = _SHELF_THK
        drawer_zone_h = zone_h - niche_h - divider_thk
        face_h = max(0.05, drawer_zone_h - _FACE_TOP_MARGIN)
        cz = (body_bot_z + face_h / 2.0,)
    elif storage == "two_prismatic_drawers":
        n = drawer_count
        # FACE_H derived to fill the zone (50c223fe L52); pitch_scale only
        # nudges the reveal, never breaks the stack-fits-zone invariant.
        gap = _FACE_GAP * pitch_scale
        face_h = (zone_h - (n - 1) * gap - _FACE_TOP_MARGIN) / n
        # Clearance inequality (spec §7): n*face_h + (n-1)*gap + margin <= zone_h.
        # By construction face_h fills exactly; guard against degenerate n.
        face_h = max(0.04, face_h)
        cz = tuple(body_bot_z + i * (face_h + gap) + face_h / 2.0 for i in range(n))
    else:
        # door / flap span the full opening; reuse zone for a single "face".
        face_h = max(0.05, zone_h - _FACE_TOP_MARGIN)
        cz = ()

    # Tray height scales with the front (50c223fe: BOX_H = FACE_H * 0.70 for
    # multi-drawer; parent used a fixed 0.112). Cap so the tray fits the front.
    tray_t = _TRAY_T

    drawer_travel = _clamp(cfg.drawer_travel, 0.10, 0.36)
    # retains_insertion (spec §7): open drawer keeps part of the tray inside.
    drawer_travel = min(drawer_travel, box_d - 0.030)

    door_open_angle = _clamp(cfg.door_open_angle, 0.80 * math.pi / 2.0, 0.95 * math.pi)
    # flap-door must not hit the floor (spec §7): drop height limited by lift.
    if storage == "drop_down_flap_door":
        # door length ~= face_h; opened it sweeps down by ~face_h*sin(angle).
        # keep the swept tip above floor: body_bot_z >= face_h*sin(angle).
        max_drop = max(0.0, min(0.999, body_bot_z / max(face_h, 1e-6)))
        max_angle = math.asin(max_drop) if max_drop < 1.0 else math.pi / 2.0
        # allow a bit beyond horizontal-from-vertical; cap at the safe angle.
        door_open_angle = min(door_open_angle, max(0.6, max_angle + 0.2))

    return ResolvedBedsideConfig(
        base_support=base_support,
        storage_mechanism=storage,
        handle=handle,
        drawer_count=drawer_count,
        palette_style=palette_style,
        w=w,
        d=d,
        wall=wall,
        lip=_LIP,
        shelf_thk=_SHELF_THK,
        body_bot_z=body_bot_z,
        carcass_body_h=carcass_body_h,
        h=h,
        inner_w=inner_w,
        shelf_bot_z=shelf_bot_z,
        zone_h=zone_h,
        leg_h=leg_h,
        face_thk=_FACE_THK,
        box_d=box_d,
        box_w=box_w,
        tray_t=tray_t,
        drawer_travel=drawer_travel,
        door_open_angle=door_open_angle,
        face_h=face_h,
        cz=cz,
        name=cfg.name or "bedside",
    )


def with_overrides(config: BedsideConfig, **kwargs: object) -> BedsideConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: BedsideConfig | ResolvedBedsideConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedBedsideConfig) else resolve_config(config)
    return (
        ("base_support", r.base_support),
        ("storage_mechanism", r.storage_mechanism),
        ("handle", r.handle),
        ("drawer_count", f"n{r.drawer_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Base-support mesh helpers (preserve source primitives: Lathe / tube).
# ---------------------------------------------------------------------------
def _make_splayed_leg_mesh(r: ResolvedBedsideConfig, i: int, dx: int, dy: int):
    """Splayed tapered lathe leg (65751baf _make_leg_mesh)."""
    leg_h = r.leg_h
    leg_len = leg_h / math.cos(_SPLAY_RAD)
    profile = [
        (0.001, 0.0),
        (_LEG_BOT_R, 0.0),
        (_LEG_TOP_R, leg_len),
        (0.001, leg_len),
    ]
    geom = LatheGeometry(profile, segments=16)
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    ax = dy * inv_sqrt2
    ay = -dx * inv_sqrt2
    geom.rotate((ax, ay, 0.0), _SPLAY_RAD, origin=(0.0, 0.0, leg_len))
    z_drop = leg_len * (1.0 - math.cos(_SPLAY_RAD)) - 0.002
    geom.translate(0.0, 0.0, -z_drop)
    return mesh_from_geometry(geom, f"leg_{i}")


def _make_hairpin_leg_mesh(r: ResolvedBedsideConfig, cx: float, cy: float):
    """U-shaped hairpin steel rod in the XZ plane (dcdcb159)."""
    leg_h = r.leg_h
    hs = _HAIRPIN_SPLAY / 2.0
    points = [
        (cx - hs, cy, leg_h),
        (cx - hs * 0.84, cy, leg_h * 0.70),
        (cx - hs * 0.52, cy, leg_h * 0.36),
        (cx - hs * 0.18, cy, leg_h * 0.08),
        (cx, cy, _ROD_R),
        (cx + hs * 0.18, cy, leg_h * 0.08),
        (cx + hs * 0.52, cy, leg_h * 0.36),
        (cx + hs * 0.84, cy, leg_h * 0.70),
        (cx + hs, cy, leg_h),
    ]
    return tube_from_spline_points(
        points, radius=_ROD_R, samples_per_segment=18, radial_segments=12, cap_ends=True
    )


def _emit_base_support(carcass, r: ResolvedBedsideConfig, mats) -> None:
    """Emit the base-support visuals below the carcass body (no joint)."""
    d, w = r.d, r.w
    if r.base_support == "inset_floating_plinth":
        carcass.visual(
            Box((d - 2 * _PLINTH_INSET, w - 2 * _PLINTH_INSET, _PLINTH_H)),
            origin=Origin(xyz=(d / 2.0, 0.0, _PLINTH_H / 2.0)),
            material=mats["plinth"],
            name="plinth", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
    elif r.base_support == "solid_toe_kick_box":
        upper_h = _TOEKICK_BASE_H - _TOEKICK_NOTCH_H
        carcass.visual(
            Box((d, w, upper_h)),
            origin=Origin(xyz=(d / 2.0, 0.0, _TOEKICK_NOTCH_H + upper_h / 2.0)),
            material=mats["plinth"],
            name="base_upper", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
        lower_d = d - _TOEKICK_RECESS
        carcass.visual(
            Box((lower_d, w, _TOEKICK_NOTCH_H)),
            origin=Origin(xyz=(lower_d / 2.0, 0.0, _TOEKICK_NOTCH_H / 2.0)),
            material=mats["plinth"],
            name="base_toekick", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
    elif r.base_support == "four_splayed_legs":
        for i, (dx, dy) in enumerate([(-1, -1), (-1, 1), (1, -1), (1, 1)]):
            cx = d / 2.0 + dx * (d / 2.0 - _LEG_INSET)
            cy = dy * (w / 2.0 - _LEG_INSET)
            carcass.visual(
                _make_splayed_leg_mesh(r, i, dx, dy),
                origin=Origin(xyz=(cx, cy, 0.0)),
                material=mats["leg"],
                name=f"leg_{i}", material_class_id=("metal.brushed_silver" if r.palette_style == "charcoal_chrome" else "wood.mahogany_teak_dark"),
            )
    else:  # hairpin_metal_legs
        corners = [
            (_HAIRPIN_INSET_X, -(w / 2.0 - _HAIRPIN_INSET_Y)),
            (_HAIRPIN_INSET_X, +(w / 2.0 - _HAIRPIN_INSET_Y)),
            (d - _HAIRPIN_INSET_X, -(w / 2.0 - _HAIRPIN_INSET_Y)),
            (d - _HAIRPIN_INSET_X, +(w / 2.0 - _HAIRPIN_INSET_Y)),
        ]
        for i, (cx, cy) in enumerate(corners):
            carcass.visual(
                mesh_from_geometry(_make_hairpin_leg_mesh(r, cx, cy), f"hairpin_leg_{i}"),
                material=mats["leg"],
                name=f"hairpin_leg_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"warm_walnut", "matte_white", "charcoal_chrome"} else "metal.brass_aged"),
            )
            # Mounting plate bridging leg prongs to the carcass bottom.
            carcass.visual(
                Box((_HAIRPIN_SPLAY + 0.014, 0.024, 0.006)),
                origin=Origin(xyz=(cx, cy, r.leg_h - 0.003)),
                material=mats["leg"],
                name=f"mount_plate_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"warm_walnut", "matte_white", "charcoal_chrome"} else "metal.brass_aged"),
            )


# ---------------------------------------------------------------------------
# Carcass body (shared shell). Side/back panels + gallery lip top shelf +
# bottom panel + (for drawer mechanisms) runner rails on the +X opening plane.
# ---------------------------------------------------------------------------
def _build_carcass_body(carcass, r: ResolvedBedsideConfig, mats) -> None:
    d, w, wall = r.d, r.w, r.wall
    bz, h = r.body_bot_z, r.h
    inner_w = r.inner_w
    panel_h = h - bz

    for i in range(2):
        s = 1 - 2 * i  # +1, -1
        carcass.visual(
            Box((d, wall, panel_h)),
            origin=Origin(xyz=(d / 2.0, s * (w / 2.0 - wall / 2.0), bz + panel_h / 2.0)),
            material=mats["carcass"],
            name=f"side_panel_{i}", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
    carcass.visual(
        Box((wall, inner_w, panel_h)),
        origin=Origin(xyz=(wall / 2.0, 0.0, bz + panel_h / 2.0)),
        material=mats["carcass"],
        name="back_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
    )
    carcass.visual(
        Box((d, inner_w, r.shelf_thk)),
        origin=Origin(xyz=(d / 2.0, 0.0, r.shelf_bot_z + r.shelf_thk / 2.0)),
        material=mats["carcass"],
        name="top_shelf", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
    )
    carcass.visual(
        Box((d - r.face_thk, inner_w, 0.016)),
        origin=Origin(xyz=((d - r.face_thk) / 2.0, 0.0, bz + 0.008)),
        material=mats["carcass"],
        name="bottom_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
    )


def _emit_runner_rails(carcass, r: ResolvedBedsideConfig, mats, box_h: float) -> None:
    """Side runner rails carrying each drawer tray (parent L192-205) plus a
    thin front-edge slide rail at the +X opening plane so the PRISMATIC joint
    origin (D, 0, cz) lands on real carcass geometry (drawer_cabinet pattern)."""
    rail_h = 0.010
    rail_len = min(_RAIL_LEN, r.d - 0.040)
    inner_w = r.inner_w
    front_rail_thk = 0.012  # thin reveal at the front opening plane
    front_x = r.d - front_rail_thk / 2.0
    for idx, cz in enumerate(r.cz):
        rail_top = cz - box_h / 2.0
        # Keep the rail body within the side-panel span (which starts at
        # body_bot_z); clamp so the lowest drawer's rail still touches it.
        rail_center_z = max(r.body_bot_z + rail_h / 2.0, rail_top - rail_h / 2.0)
        for s, stag in ((1, "0"), (-1, "1")):
            carcass.visual(
                Box((rail_len, 0.014, rail_h)),
                origin=Origin(
                    xyz=(0.030 + rail_len / 2.0, s * (inner_w / 2.0 - 0.007),
                         rail_center_z)
                ),
                material=mats["carcass"],
                name=f"runner_rail_{idx}_{stag}", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
            )
        # Front slide rail at the opening plane, centered on cz: anchors the
        # joint origin and spans the inner width (a slim reveal band).
        carcass.visual(
            Box((front_rail_thk, inner_w, 0.012)),
            origin=Origin(xyz=(front_x, 0.0, cz)),
            material=mats["carcass"],
            name=f"front_slide_rail_{idx}", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )


# ---------------------------------------------------------------------------
# Handle helpers (Rule 1: inline non-moving visuals on the storage face).
# face_z0 is the storage-face outer surface (local x=0 in each child frame).
# ---------------------------------------------------------------------------
def _emit_chrome_bar(part, r: ResolvedBedsideConfig, mats, *, cy: float, cz: float,
                     bar_axis: str) -> None:
    """Two-post chrome bar handle (parent L116-131). bar_axis 'y' (drawer/flap)
    or local Y for the door. Posts straddle the bar along Y."""
    post_d = 0.075
    bar_len = 0.180
    for i in range(2):
        s = 1 - 2 * i
        part.visual(
            Box((0.016, 0.012, 0.012)),
            origin=Origin(xyz=(0.004, cy + s * post_d, cz)),
            material=mats["hardware"],
            name=f"handle_post_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "metal.blackened_gunmetal"),
        )
    part.visual(
        Box((0.014, bar_len, 0.016)),
        origin=Origin(xyz=(0.019, cy, cz)),
        material=mats["hardware"],
        name="handle_bar", material_class_id=("metal.chrome_polished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "metal.blackened_gunmetal"),
    )


def _make_knob_mesh():
    """Round turned knob, lathe-revolved, protruding along +X (0504431c)."""
    ctrl = [
        (0.000, 0.000),
        (0.006, 0.000),
        (0.005, 0.004),
        (0.006, 0.008),
        (0.010, 0.011),
        (0.014, 0.015),
        (0.015, 0.019),
        (0.013, 0.023),
        (0.007, 0.026),
        (0.000, 0.028),
    ]
    smooth = sample_catmull_rom_spline_2d(ctrl, samples_per_segment=8, closed=False)
    profile = [(max(rad, 0.0), z) for rad, z in smooth]
    geom = LatheGeometry(profile, segments=28, closed=True)
    geom.rotate_y(-math.pi / 2.0)
    return mesh_from_geometry(geom, "drawer_knob")


def _emit_round_knobs(part, r: ResolvedBedsideConfig, mats, *, cy: float, cz: float,
                      knob_mesh) -> None:
    """Two round turned knobs (0504431c L150-161)."""
    spacing = 0.080
    for i in range(2):
        sy = -1.0 if i == 0 else 1.0
        part.visual(
            knob_mesh,
            origin=Origin(xyz=(0.014, cy + sy * spacing, cz)),
            material=mats["hardware"],
            name=f"knob_{i}", material_class_id=("metal.chrome_polished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "metal.blackened_gunmetal"),
        )


def _finger_pull_slab_mesh(r: ResolvedBedsideConfig, face_w: float, face_h: float, name: str):
    """CadQuery front slab with finger-pull groove (968aa0b6)."""
    slab = cq.Workplane("XY").box(r.face_thk, face_w, face_h)
    groove_w = min(_GROOVE_W, face_w - 0.040)
    groove_center_z = face_h / 2.0 - _GROOVE_LIP - _GROOVE_H / 2.0
    slab = (
        slab.faces(">X").workplane()
        .center(0.0, groove_center_z)
        .slot2D(groove_w, _GROOVE_H)
        .cutBlind(-_GROOVE_DEPTH)
    )
    return mesh_from_cadquery(slab, f"{name}_front_slab"), groove_w


# ---------------------------------------------------------------------------
# Storage face (drawer front / door panel) with the chosen handle inlined.
# ---------------------------------------------------------------------------
def _emit_face_slab(part, r: ResolvedBedsideConfig, mats, *, face_w: float,
                    face_h: float, cy: float, knob_mesh) -> None:
    """Emit the front slab + handle. The face outer surface is at local x=0;
    slab spans face_w (Y, centered on cy) x face_h (Z, centered on 0)."""
    if r.handle == "recessed_finger_pull":
        slab_mesh, groove_w = _finger_pull_slab_mesh(r, face_w, face_h, part.name)
        part.visual(
            slab_mesh,
            origin=Origin(xyz=(-r.face_thk / 2.0, cy, 0.0)),
            material=mats["front"],
            name="front_slab", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
        # Groove accent strip seated in the pocket (small embed).
        accent_thk = 0.002
        accent_w = groove_w - _GROOVE_H - 0.006
        accent_h = _GROOVE_H - 0.004
        accent_z = face_h / 2.0 - _GROOVE_LIP - _GROOVE_H / 2.0
        accent_x = -_GROOVE_DEPTH + accent_thk / 2.0 - 0.0005
        part.visual(
            Box((accent_thk, accent_w, accent_h)),
            origin=Origin(xyz=(accent_x, cy, accent_z)),
            material=mats["accent"],
            name="finger_pull_groove", material_class_id=("metal.brushed_silver" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.walnut_dark"),
        )
        return

    part.visual(
        Box((r.face_thk, face_w, face_h)),
        origin=Origin(xyz=(-r.face_thk / 2.0, cy, 0.0)),
        material=mats["front"],
        name="front_slab", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
    )
    handle_z = face_h * 0.30 if face_h * 0.30 < face_h / 2.0 - 0.02 else 0.0
    if r.handle == "chrome_bar_on_posts":
        _emit_chrome_bar(part, r, mats, cy=cy, cz=handle_z, bar_axis="y")
    else:  # round_knobs
        _emit_round_knobs(part, r, mats, cy=cy, cz=handle_z, knob_mesh=knob_mesh)


def _emit_tray(drawer, r: ResolvedBedsideConfig, mats, box_h: float) -> None:
    """Hollow open-top tray behind the front slab (parent L75-113)."""
    box_d, box_w, tray_t, face_thk = r.box_d, r.box_w, r.tray_t, r.face_thk
    box_back_x = -(face_thk + box_d)
    box_cx = -(face_thk + box_d / 2.0)
    box_bot = -box_h / 2.0
    drawer.visual(
        Box((box_d, box_w, tray_t)),
        origin=Origin(xyz=(box_cx, 0.0, box_bot + tray_t / 2.0)),
        material=mats["tray"],
        name="tray_bottom", material_class_id=("wood.engineered_board" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.veneer_panel"),
    )
    wall_h = box_h - tray_t + 0.002
    wall_cz = box_bot + tray_t - 0.002 + wall_h / 2.0
    drawer.visual(
        Box((tray_t, box_w, wall_h)),
        origin=Origin(xyz=(box_back_x + tray_t / 2.0, 0.0, wall_cz)),
        material=mats["tray"],
        name="tray_back_wall", material_class_id=("wood.engineered_board" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.veneer_panel"),
    )
    side_len = box_d + 0.002
    for s, tag in ((1, "0"), (-1, "1")):
        drawer.visual(
            Box((side_len, tray_t, wall_h)),
            origin=Origin(
                xyz=(-face_thk + 0.002 - side_len / 2.0,
                     s * (box_w / 2.0 - tray_t / 2.0), wall_cz)
            ),
            material=mats["tray"],
            name=f"tray_side_wall_{tag}", material_class_id=("wood.engineered_board" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.veneer_panel"),
        )
    drawer.visual(
        Box((tray_t, box_w, wall_h)),
        origin=Origin(xyz=(-face_thk - tray_t / 2.0 + 0.002, 0.0, wall_cz)),
        material=mats["tray"],
        name="tray_front_wall", material_class_id=("wood.engineered_board" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.veneer_panel"),
    )


# ---------------------------------------------------------------------------
# Storage mechanism builders.
# ---------------------------------------------------------------------------
def _build_drawer(model, r: ResolvedBedsideConfig, carcass, mats, *, name: str,
                  cz: float, box_h: float, knob_mesh) -> None:
    """One PRISMATIC drawer child sliding along +X."""
    drawer = model.part(name)
    face_w = r.inner_w - 0.004
    _emit_face_slab(drawer, r, mats, face_w=face_w, face_h=r.face_h, cy=0.0,
                    knob_mesh=knob_mesh)
    _emit_tray(drawer, r, mats, box_h)
    drawer.inertial = Inertial.from_geometry(
        Box((r.box_d, r.box_w, box_h)), mass=4.0
    )
    model.articulation(
        f"carcass_to_{name}",
        ArticulationType.PRISMATIC,
        parent=carcass,
        child=drawer,
        origin=Origin(xyz=(r.d, 0.0, cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.5, lower=0.0,
                                   upper=r.drawer_travel),
    )


def _emit_two_prismatic_drawers(model, r: ResolvedBedsideConfig, carcass, mats,
                                knob_mesh) -> list[str]:
    box_h = max(0.05, min(0.112, r.face_h * 0.70 + 0.04))
    _emit_runner_rails(carcass, r, mats, box_h)
    names: list[str] = []
    for i, cz in enumerate(r.cz):
        name = f"drawer_{i}"
        _build_drawer(model, r, carcass, mats, name=name, cz=cz, box_h=box_h,
                      knob_mesh=knob_mesh)
        names.append(name)
    return names


def _emit_open_niche_over_drawer(model, r: ResolvedBedsideConfig, carcass, mats,
                                 knob_mesh) -> list[str]:
    # Fixed divider shelf over a single drawer (bd3941ca).
    d, inner_w = r.d, r.inner_w
    niche_h = min(0.155, r.zone_h * 0.48)
    divider_thk = _SHELF_THK
    divider_bot_z = r.shelf_bot_z - niche_h - divider_thk
    carcass.visual(
        Box((d - r.face_thk, inner_w, divider_thk)),
        origin=Origin(xyz=((d - r.face_thk) / 2.0, 0.0, divider_bot_z + divider_thk / 2.0)),
        material=mats["carcass"],
        name="divider_shelf", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
    )
    box_h = max(0.05, min(0.112, r.face_h * 0.70 + 0.04))
    _emit_runner_rails(carcass, r, mats, box_h)
    _build_drawer(model, r, carcass, mats, name="drawer_0", cz=r.cz[0], box_h=box_h,
                  knob_mesh=knob_mesh)
    return ["drawer_0"]


def _emit_hinged_cabinet_door(model, r: ResolvedBedsideConfig, carcass, mats,
                              knob_mesh) -> list[str]:
    """Single side-hinged door, REVOLUTE about +Z (02643395)."""
    d, inner_w = r.d, r.inner_w
    door_w = inner_w - 0.004
    door_h = r.face_h
    door_cz = r.body_bot_z + _FACE_TOP_MARGIN + door_h / 2.0
    hinge_y = inner_w / 2.0

    # Interior shelf (visible when open).
    shelf_back_x = r.wall
    shelf_front_x = d - r.face_thk - 0.014
    shelf_depth = max(0.02, shelf_front_x - shelf_back_x)
    int_shelf_z = r.body_bot_z + (r.shelf_bot_z - r.body_bot_z) * 0.45
    carcass.visual(
        Box((shelf_depth, inner_w, _SHELF_THK)),
        origin=Origin(xyz=((shelf_front_x + shelf_back_x) / 2.0, 0.0, int_shelf_z)),
        material=mats["tray"],
        name="interior_shelf", material_class_id=("wood.engineered_board" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.veneer_panel"),
    )

    door = model.part("door")
    # Door-local frame: origin at the hinge line; panel extends toward -Y
    # (free edge) and -X. Outer face at local x=0. cy = -door_w/2 centers it.
    cy = -door_w / 2.0
    _emit_face_slab(door, r, mats, face_w=door_w, face_h=door_h, cy=cy,
                    knob_mesh=knob_mesh)
    door.inertial = Inertial.from_geometry(
        Box((r.face_thk, door_w, door_h)), mass=3.0,
        origin=Origin(xyz=(-r.face_thk / 2.0, cy, 0.0)),
    )
    model.articulation(
        "carcass_to_door",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=door,
        origin=Origin(xyz=(d, hinge_y, door_cz)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=1.0, lower=0.0,
                                   upper=r.door_open_angle),
    )
    return ["door"]


def _emit_drop_down_flap_door(model, r: ResolvedBedsideConfig, carcass, mats,
                              knob_mesh) -> list[str]:
    """Single bottom-hinged flap door, REVOLUTE about +Y (2bf8cef6)."""
    d, inner_w = r.d, r.inner_w
    door_w = inner_w - 0.004
    door_h = max(0.05, r.zone_h - _FACE_TOP_MARGIN)
    hinge_x = d
    hinge_z = r.body_bot_z

    int_shelf_d = max(0.02, d - r.wall - r.face_thk - 0.006)
    int_shelf_z = r.body_bot_z + r.zone_h * 0.48
    carcass.visual(
        Box((int_shelf_d, inner_w - 0.004, _SHELF_THK)),
        origin=Origin(xyz=(r.wall + int_shelf_d / 2.0, 0.0, int_shelf_z)),
        material=mats["tray"],
        name="interior_shelf", material_class_id=("wood.engineered_board" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.veneer_panel"),
    )
    # Front bottom sill at the opening plane so the REVOLUTE hinge origin
    # (D, 0, body_bot_z) lands on real carcass geometry (anchors the hinge).
    sill_thk = 0.012
    carcass.visual(
        Box((sill_thk, inner_w, 0.014)),
        origin=Origin(xyz=(d - sill_thk / 2.0, 0.0, r.body_bot_z + 0.007)),
        material=mats["carcass"],
        name="flap_hinge_sill", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
    )

    flap = model.part("flap_door")
    # Part frame at the hinge line (bottom). Slab extends +Z; outer face x=0.
    if r.handle == "recessed_finger_pull":
        slab_mesh, groove_w = _finger_pull_slab_mesh(r, door_w, door_h, "flap_door")
        flap.visual(
            slab_mesh,
            origin=Origin(xyz=(-r.face_thk / 2.0, 0.0, door_h / 2.0)),
            material=mats["front"],
            name="door_slab", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
        accent_thk = 0.002
        accent_w = groove_w - _GROOVE_H - 0.006
        accent_h = _GROOVE_H - 0.004
        accent_z = door_h - _GROOVE_LIP - _GROOVE_H / 2.0
        accent_x = -_GROOVE_DEPTH + accent_thk / 2.0 - 0.0005
        flap.visual(
            Box((accent_thk, accent_w, accent_h)),
            origin=Origin(xyz=(accent_x, 0.0, accent_z)),
            material=mats["accent"],
            name="finger_pull_groove", material_class_id=("metal.brushed_silver" if r.palette_style in {"gray_lacquer", "matte_white", "charcoal_chrome"} else "wood.walnut_dark"),
        )
    else:
        flap.visual(
            Box((r.face_thk, door_w, door_h)),
            origin=Origin(xyz=(-r.face_thk / 2.0, 0.0, door_h / 2.0)),
            material=mats["front"],
            name="door_slab", material_class_id=("wood.polished_varnished" if r.palette_style in {"gray_lacquer", "warm_walnut", "charcoal_chrome"} else "wood.painted_clean"),
        )
        handle_z = door_h - 0.040
        if r.handle == "chrome_bar_on_posts":
            _emit_chrome_bar(flap, r, mats, cy=0.0, cz=handle_z, bar_axis="y")
        else:
            _emit_round_knobs(flap, r, mats, cy=0.0, cz=handle_z, knob_mesh=knob_mesh)

    flap.inertial = Inertial.from_geometry(
        Box((r.face_thk, door_w, door_h)), mass=3.0,
        origin=Origin(xyz=(-r.face_thk / 2.0, 0.0, door_h / 2.0)),
    )
    model.articulation(
        "carcass_to_flap_door",
        ArticulationType.REVOLUTE,
        parent=carcass,
        child=flap,
        origin=Origin(xyz=(hinge_x, 0.0, hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=1.5, lower=0.0,
                                   upper=r.door_open_angle),
    )
    return ["flap_door"]


_STORAGE_BUILDERS = {
    "two_prismatic_drawers": _emit_two_prismatic_drawers,
    "hinged_cabinet_door": _emit_hinged_cabinet_door,
    "drop_down_flap_door": _emit_drop_down_flap_door,
    "open_niche_over_drawer": _emit_open_niche_over_drawer,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_bedside(
    config: BedsideConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"bedside_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    knob_mesh = _make_knob_mesh() if r.handle == "round_knobs" else None

    carcass = model.part("carcass")
    _emit_base_support(carcass, r, mats)
    _build_carcass_body(carcass, r, mats)
    carcass.inertial = Inertial.from_geometry(
        Box((r.d, r.w, r.h)), mass=22.0, origin=Origin(xyz=(r.d / 2.0, 0.0, r.h / 2.0))
    )

    _STORAGE_BUILDERS[r.storage_mechanism](model, r, carcass, mats, knob_mesh)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_bedside(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_bedside(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_bedside_tests(
    object_model: ArticulatedObject,
    config: BedsideConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    carcass = object_model.get_part("carcass")

    # ---- captured-slide / hinge overlaps (whole-part, mirrors sources). ----
    if r.storage_mechanism in ("two_prismatic_drawers", "open_niche_over_drawer"):
        drawer_names = [f"drawer_{i}" for i in range(max(r.drawer_count, 1))] \
            if r.storage_mechanism == "two_prismatic_drawers" else ["drawer_0"]
        for nm in drawer_names:
            drawer = object_model.get_part(nm)
            ctx.allow_overlap(
                carcass, drawer,
                reason="drawer slides inside the carcass cavity; closed front meets "
                       "the opening plane / runner rails.",
            )
        for i in range(len(drawer_names) - 1):
            ctx.allow_overlap(
                object_model.get_part(drawer_names[i]),
                object_model.get_part(drawer_names[i + 1]),
                reason="stacked drawer fronts share the same carcass opening plane.",
            )
    elif r.storage_mechanism == "hinged_cabinet_door":
        ctx.allow_overlap(
            carcass, object_model.get_part("door"),
            reason="closed door seats flush in the carcass opening over the interior shelf.",
        )
    else:  # drop_down_flap_door
        ctx.allow_overlap(
            carcass, object_model.get_part("flap_door"),
            reason="closed flap seats flush in the carcass opening over the interior shelf.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # ---- identity / grounding. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("carcass part present", "carcass" in part_names,
              details=str(sorted(part_names)))
    cb = ctx.part_world_aabb(carcass)
    if cb is not None:
        ctx.check("grounded near floor", abs(cb[0][2]) < 0.01,
                  details=f"min z={cb[0][2]:.4f}")

    # ---- base-support visuals present. ----
    carcass_vis = {v.name for v in carcass.visuals}
    if r.base_support == "inset_floating_plinth":
        ctx.check("plinth present", "plinth" in carcass_vis)
    elif r.base_support == "solid_toe_kick_box":
        ctx.check("toe-kick present", "base_toekick" in carcass_vis)
    elif r.base_support == "four_splayed_legs":
        ctx.check("4 splayed legs present",
                  all(f"leg_{i}" in carcass_vis for i in range(4)))
    else:
        ctx.check("4 hairpin legs present",
                  all(f"hairpin_leg_{i}" in carcass_vis for i in range(4)))

    # ---- storage joint topology. ----
    joint_names = {j.name for j in object_model.articulations}
    if r.storage_mechanism == "two_prismatic_drawers":
        ctx.check("drawer part count matches N",
                  len([n for n in part_names if n.startswith("drawer_")]) == r.drawer_count,
                  details=f"N={r.drawer_count}")
        for i in range(r.drawer_count):
            j = object_model.get_articulation(f"carcass_to_drawer_{i}")
            ctx.check(f"drawer_{i} PRISMATIC +X",
                      j.articulation_type == ArticulationType.PRISMATIC
                      and abs(j.axis[0]) > 0.99 and abs(j.axis[2]) < 0.01,
                      details=f"type={j.articulation_type} axis={tuple(j.axis)}")
    elif r.storage_mechanism == "open_niche_over_drawer":
        ctx.check("divider shelf present", "divider_shelf" in carcass_vis)
        j = object_model.get_articulation("carcass_to_drawer_0")
        ctx.check("niche drawer PRISMATIC +X",
                  j.articulation_type == ArticulationType.PRISMATIC
                  and abs(j.axis[0]) > 0.99,
                  details=f"axis={tuple(j.axis)}")
    elif r.storage_mechanism == "hinged_cabinet_door":
        j = object_model.get_articulation("carcass_to_door")
        ctx.check("door REVOLUTE +Z",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and abs(j.axis[2]) > 0.99 and abs(j.axis[0]) < 0.01
                  and abs(j.axis[1]) < 0.01,
                  details=f"axis={tuple(j.axis)}")
    else:
        j = object_model.get_articulation("carcass_to_flap_door")
        ctx.check("flap REVOLUTE +Y",
                  j.articulation_type == ArticulationType.REVOLUTE
                  and abs(j.axis[1]) > 0.99 and abs(j.axis[0]) < 0.01
                  and abs(j.axis[2]) < 0.01,
                  details=f"axis={tuple(j.axis)}")

    # ---- handle present on the storage face. ----
    storage_part = None
    if r.storage_mechanism in ("two_prismatic_drawers", "open_niche_over_drawer"):
        storage_part = object_model.get_part("drawer_0") if "drawer_0" in part_names else None
    elif r.storage_mechanism == "hinged_cabinet_door":
        storage_part = object_model.get_part("door")
    else:
        storage_part = object_model.get_part("flap_door")
    if storage_part is not None:
        sv = {v.name for v in storage_part.visuals}
        if r.handle == "chrome_bar_on_posts":
            ctx.check("chrome bar handle present", "handle_bar" in sv)
        elif r.handle == "round_knobs":
            ctx.check("round knobs present", "knob_0" in sv and "knob_1" in sv)
        else:
            ctx.check("finger-pull groove present", "finger_pull_groove" in sv)

    # ---- drawer-stack clearance proven from authored dims. ----
    if r.storage_mechanism == "two_prismatic_drawers" and r.drawer_count >= 1:
        # Top of the highest front must stay under the shelf underside.
        top_front_z = r.cz[-1] + r.face_h / 2.0
        ctx.check("drawer stack fits under the shelf",
                  top_front_z <= r.shelf_bot_z + 1e-4,
                  details=f"top_front_z={top_front_z:.4f} shelf_bot={r.shelf_bot_z:.4f}")

    # ---- slot_choices recorded with drawer_count encoded. ----
    ctx.check(
        "slot_choices recorded with drawer_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "BedsideConfig",
    "ResolvedBedsideConfig",
    "build_bedside",
    "build_seeded_bedside",
    "config_from_seed",
    "resolve_config",
    "run_bedside_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
