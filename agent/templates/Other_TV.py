# SPDX-License-Identifier: Apache-2.0

"""Vintage 1980s CRT cabinet television — modular template.

NOTE on the slug name: "tv" here = a **1980s wood-grain / retro CRT television
set** (a display cabinet with a recessed CRT glass tube, a control column with a
channel dial + small knobs, on a tabletop / splayed legs / swivel base). It is
NOT a flat wall-mount LCD/OLED TV, NOT a desktop monitor (no separate tilt/swivel
neck), and NOT a radio.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_TV.md`` and the
``picture/Other/TV`` 5-star sample pool (1 parent + 8 slot/multiplicity forks),
all synced under ``data/records/``.

Structure (pattern = ``mixed``). A single root ``cabinet`` part carries the wood
shell / front plate / CRT bezel + glass tube / control-column decorations, plus
a fixed CONTINUOUS ``channel_dial`` and N REVOLUTE control ``knob_{i}`` children.
Three named module axes + one multiplicity axis:

  * ``cabinet_form`` (3): boxy_wood (6 wood panels) / rounded_space_age_pod
    (single cadquery filleted shell) / portable_with_handle (6 panels + a fixed
    arch carry handle). A mesh-helper dimension; it does not add a joint.
  * ``screen_tube`` (3): bulged_crt_glass (LoftGeometry convex tube + rect bezel)
    / flat_face_crt (near-flat Loft + rect bezel) / porthole_round (LatheGeometry
    domed glass + circular bezel). Mesh-helper dimension; no joint.
  * ``base_support`` (3) — the SOLE true part-tree / root / joint topology axis:
    tabletop (cabinet sits on the ground, root=cabinet, no joint) /
    splayed_console_legs (4 lathe legs inlined as cabinet visuals, whole cabinet
    lifted Z_LIFT, no joint, Rule 1) / swivel_base (a NEW root ``swivel_base``
    pedestal; cabinet becomes its child via a ``base_to_cabinet`` CONTINUOUS +Z
    turntable joint).
  * ``knob_count`` (N in [1,8], sweep-sampled [1,6]): a multiplicity axis — N
    control knobs as REVOLUTE +X children along the control column on the Y axis.
    N is encoded into the slot_choice tuple as ``("knob_count", f"n{N}")``.

All dial/knob stems are shaft-in-bore captured-pin geometry and the swivel is a
turntable face contact, so those joints omit ``MatingContract`` (grandfathered)
and are guarded by the flat articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source record's run_tests allow_overlap block).
The channel_dial carries an off-axis ``pointer_wedge`` proving continuous spin.
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
    BezelGeometry,
    BezelRecess,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    KnobIndicator,
    LatheGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

CabinetForm = Literal["boxy_wood", "rounded_space_age_pod", "portable_with_handle"]
ScreenTube = Literal["bulged_crt_glass", "flat_face_crt", "porthole_round"]
BaseSupport = Literal["tabletop", "splayed_console_legs", "swivel_base"]
PaletteStyle = Literal[
    "wood_grain_classic",
    "walnut_console",
    "space_age_cream",
    "glossy_black",
    "retro_teal",
]

CABINET_FORMS: tuple[CabinetForm, ...] = (
    "boxy_wood",
    "rounded_space_age_pod",
    "portable_with_handle",
)
SCREEN_TUBES: tuple[ScreenTube, ...] = (
    "bulged_crt_glass",
    "flat_face_crt",
    "porthole_round",
)
BASE_SUPPORTS: tuple[BaseSupport, ...] = (
    "tabletop",
    "splayed_console_legs",
    "swivel_base",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "wood_grain_classic",
    "walnut_console",
    "space_age_cream",
    "glossy_black",
    "retro_teal",
)

N_MIN = 1
N_MAX = 8
# Knob-count sweep sampling domain [1,6], skewed small (spec §8):
# 2/3 high-frequency, 4 common, 5/6 long tail, 1 sparse.
KNOB_SAMPLE_NS = (1, 2, 3, 4, 5, 6)
KNOB_SAMPLE_WEIGHTS = (0.06, 0.26, 0.30, 0.20, 0.12, 0.06)

# Each palette maps the shared semantic material keys used by every .visual().
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "wood_grain_classic": {
        "shell": (0.72, 0.62, 0.47, 1.0),
        "plastic": (0.79, 0.75, 0.65, 1.0),
        "bezel": (0.70, 0.66, 0.55, 1.0),
        "glass": (0.72, 0.77, 0.72, 1.0),
        "dark": (0.15, 0.15, 0.16, 1.0),
        "metal": (0.63, 0.62, 0.58, 1.0),
        "marking": (0.93, 0.93, 0.90, 1.0),
        "grille": (0.34, 0.31, 0.26, 1.0),
        "silver": (0.76, 0.76, 0.74, 1.0),
        "base": (0.18, 0.17, 0.16, 1.0),
    },
    "walnut_console": {
        "shell": (0.40, 0.27, 0.18, 1.0),
        "plastic": (0.62, 0.55, 0.45, 1.0),
        "bezel": (0.34, 0.26, 0.20, 1.0),
        "glass": (0.66, 0.72, 0.70, 1.0),
        "dark": (0.10, 0.09, 0.09, 1.0),
        "metal": (0.70, 0.66, 0.55, 1.0),
        "marking": (0.92, 0.90, 0.82, 1.0),
        "grille": (0.24, 0.18, 0.13, 1.0),
        "silver": (0.80, 0.74, 0.60, 1.0),
        "base": (0.20, 0.13, 0.08, 1.0),
    },
    "space_age_cream": {
        "shell": (0.86, 0.83, 0.76, 1.0),
        "plastic": (0.90, 0.87, 0.80, 1.0),
        "bezel": (0.78, 0.74, 0.66, 1.0),
        "glass": (0.74, 0.79, 0.76, 1.0),
        "dark": (0.18, 0.18, 0.20, 1.0),
        "metal": (0.72, 0.72, 0.70, 1.0),
        "marking": (0.20, 0.30, 0.45, 1.0),
        "grille": (0.55, 0.52, 0.46, 1.0),
        "silver": (0.82, 0.82, 0.80, 1.0),
        "base": (0.30, 0.30, 0.32, 1.0),
    },
    "glossy_black": {
        "shell": (0.05, 0.05, 0.06, 1.0),
        "plastic": (0.12, 0.12, 0.13, 1.0),
        "bezel": (0.03, 0.03, 0.03, 1.0),
        "glass": (0.40, 0.46, 0.46, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
        "metal": (0.66, 0.67, 0.66, 1.0),
        "marking": (0.90, 0.90, 0.90, 1.0),
        "grille": (0.10, 0.10, 0.11, 1.0),
        "silver": (0.74, 0.74, 0.74, 1.0),
        "base": (0.04, 0.04, 0.05, 1.0),
    },
    "retro_teal": {
        "shell": (0.18, 0.46, 0.46, 1.0),
        "plastic": (0.84, 0.82, 0.74, 1.0),
        "bezel": (0.12, 0.34, 0.34, 1.0),
        "glass": (0.70, 0.78, 0.76, 1.0),
        "dark": (0.10, 0.16, 0.16, 1.0),
        "metal": (0.74, 0.70, 0.58, 1.0),
        "marking": (0.95, 0.93, 0.84, 1.0),
        "grille": (0.10, 0.28, 0.28, 1.0),
        "silver": (0.80, 0.78, 0.70, 1.0),
        "base": (0.08, 0.22, 0.22, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). From the parent f8f3f341. Front face is
# toward +X; ground at z=0. The screen sits on the left two-thirds (Y>0), the
# control column on the right third (Y<0).
# ---------------------------------------------------------------------------
_CAB_W = 0.62  # full width along Y
_CAB_H = 0.45  # full height along Z
_CAB_D = 0.32  # full depth along X
_WOOD_T = 0.020

_PLATE_X0 = 0.132  # rear face of the recessed beige front plate
_PLATE_X1 = 0.144  # front face of the recessed beige front plate

_SCREEN_CY = 0.0875  # bezel / CRT centre (Y)
_SCREEN_CZ = 0.225  # bezel / CRT centre (Z, cabinet-local)

_COL_Y = -0.2025  # control-column centreline (Y)

_DIAL_DIAMETER = 0.070
_DIAL_CZ = 0.300
_KNOB_DIAMETER = 0.024
_KNOB_ROW_Z = 0.225
_KNOB_SPACING = 0.035
_KNOB_RANGE = 0.75 * math.pi  # +/-135 degrees

_DIAL_JOINT_X = 0.150  # escutcheon front face
_KNOB_JOINT_X = _PLATE_X1  # plate front face

# Pod shell.
_POD_FILLET = 0.045
_SHELL_T = 0.024

# Console legs.
_LEG_H = 0.150
_LEG_R_TOP = 0.021
_LEG_R_BOT = 0.013
_SPLAY_ANGLE = math.radians(12.0)
_LEG_INSET = 0.038

# Swivel base.
_BASE_RADIUS = 0.150
_BASE_DISK_H = 0.012
_COLUMN_RADIUS = 0.058
_COLUMN_TOP_Z = 0.050
_PLATE_RADIUS = 0.110
_PLATE_H = 0.008


@dataclass(frozen=True)
class TvConfig:
    cabinet_form: CabinetForm | None = None
    screen_tube: ScreenTube | None = None
    base_support: BaseSupport | None = None
    knob_count: int | None = None
    palette_style: PaletteStyle = "wood_grain_classic"
    cabinet_width_scale: float = 1.0
    cabinet_height_scale: float = 1.0
    dial_diameter_scale: float = 1.0
    knob_range_scale: float = 1.0
    knob_spacing_scale: float = 1.0
    leg_height_scale: float = 1.0
    swivel_pedestal_scale: float = 1.0
    name: str = "tv"


@dataclass(frozen=True)
class ResolvedTvConfig:
    cabinet_form: CabinetForm
    screen_tube: ScreenTube
    base_support: BaseSupport
    knob_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    cab_w: float
    cab_h: float
    cab_d: float
    wood_t: float
    screen_cy: float
    screen_cz: float
    col_y: float
    dial_diameter: float
    dial_cz: float
    knob_row_z: float
    knob_spacing: float
    knob_diameter: float
    knob_range: float
    z_lift: float  # cabinet bottom lift (legs); 0 otherwise
    pedestal_top_z: float  # top of swivel pedestal (swivel only)
    base_radius: float
    plate_radius: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> TvConfig:
    rng = random.Random(seed)
    return TvConfig(
        cabinet_form=rng.choice(CABINET_FORMS),
        screen_tube=rng.choice(SCREEN_TUBES),
        base_support=rng.choice(BASE_SUPPORTS),
        knob_count=rng.choices(KNOB_SAMPLE_NS, weights=KNOB_SAMPLE_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        cabinet_width_scale=round(rng.uniform(0.90, 1.12), 4),
        cabinet_height_scale=round(rng.uniform(0.90, 1.12), 4),
        dial_diameter_scale=round(rng.uniform(0.90, 1.10), 4),
        knob_range_scale=round(rng.uniform(0.85, 1.05), 4),
        knob_spacing_scale=round(rng.uniform(0.85, 1.12), 4),
        leg_height_scale=round(rng.uniform(0.85, 1.20), 4),
        swivel_pedestal_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_tv_{seed}",
    )


def resolve_config(config: TvConfig | None = None) -> ResolvedTvConfig:
    cfg = config or TvConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    cabinet_form = _pick(cfg.cabinet_form, CABINET_FORMS)
    screen_tube = _pick(cfg.screen_tube, SCREEN_TUBES)
    base_support = _pick(cfg.base_support, BASE_SUPPORTS)

    knob_count = int(cfg.knob_count) if cfg.knob_count is not None else 3
    knob_count = int(_clamp(knob_count, N_MIN, N_MAX))

    width_scale = _clamp(cfg.cabinet_width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.cabinet_height_scale, 0.90, 1.12)
    dial_scale = _clamp(cfg.dial_diameter_scale, 0.90, 1.10)
    range_scale = _clamp(cfg.knob_range_scale, 0.85, 1.05)
    spacing_scale = _clamp(cfg.knob_spacing_scale, 0.85, 1.12)
    leg_scale = _clamp(cfg.leg_height_scale, 0.85, 1.20)
    ped_scale = _clamp(cfg.swivel_pedestal_scale, 0.90, 1.15)

    cab_w = _CAB_W * width_scale
    cab_h = _CAB_H * height_scale
    # Derived layout: the control column and screen centre scale with width.
    col_y = _COL_Y * width_scale
    screen_cy = _SCREEN_CY * width_scale
    screen_cz = _SCREEN_CZ * height_scale
    dial_cz = _DIAL_CZ * height_scale
    knob_row_z = _KNOB_ROW_Z * height_scale

    dial_diameter = _DIAL_DIAMETER * dial_scale
    knob_range = _clamp(_KNOB_RANGE * range_scale, 0.5, math.pi * 0.95)

    # --- Clearance inequality (spec §7): the N knobs must (a) fit along the
    #     control column Y span and (b) never overlap one another. Co-solve the
    #     center-to-center spacing AND the knob cap diameter: the row width is
    #     (N-1)*spacing + cap_dia, and adjacent caps need spacing >= cap_dia +
    #     gap. Shrink the cap diameter for large N so the caps stay disjoint.
    knob_diameter = _KNOB_DIAMETER
    knob_spacing = _KNOB_SPACING * spacing_scale
    if knob_count >= 2:
        # Available Y span on the column: ~0.135 m around the column centre at
        # nominal width, scaled with cabinet width.
        col_span = 0.135 * width_scale
        margin = 0.006
        gap = 0.003  # minimum air gap between adjacent caps
        max_row = col_span - 2.0 * margin
        n = knob_count
        # Largest cap diameter for which N caps fit edge-to-edge (spacing>=dia+gap):
        #   row = (N-1)*(dia+gap) + dia = N*dia + (N-1)*gap <= max_row.
        max_dia = (max_row - (n - 1) * gap) / n
        knob_diameter = min(_KNOB_DIAMETER, max(0.008, max_dia))
        # Spacing must keep caps disjoint and fit the row; spread evenly if room.
        min_spacing = knob_diameter + gap
        even_spacing = (max_row - knob_diameter) / (n - 1)
        knob_spacing = _clamp(knob_spacing, min_spacing, max(min_spacing, even_spacing))

    # base_support-dependent quantities.
    z_lift = 0.0
    pedestal_top_z = 0.0
    base_radius = _BASE_RADIUS
    plate_radius = _PLATE_RADIUS
    if base_support == "splayed_console_legs":
        leg_h = _LEG_H * leg_scale
        z_lift = leg_h * math.cos(_SPLAY_ANGLE)
    elif base_support == "swivel_base":
        column_top_z = _COLUMN_TOP_Z * ped_scale
        pedestal_top_z = column_top_z + _PLATE_H * ped_scale
        base_radius = _BASE_RADIUS * ped_scale
        plate_radius = _PLATE_RADIUS * ped_scale

    return ResolvedTvConfig(
        cabinet_form=cabinet_form,
        screen_tube=screen_tube,
        base_support=base_support,
        knob_count=knob_count,
        palette_style=palette_style,
        cab_w=cab_w,
        cab_h=cab_h,
        cab_d=_CAB_D,
        wood_t=_WOOD_T,
        screen_cy=screen_cy,
        screen_cz=screen_cz,
        col_y=col_y,
        dial_diameter=dial_diameter,
        dial_cz=dial_cz,
        knob_row_z=knob_row_z,
        knob_spacing=knob_spacing,
        knob_diameter=knob_diameter,
        knob_range=knob_range,
        z_lift=z_lift,
        pedestal_top_z=pedestal_top_z,
        base_radius=base_radius,
        plate_radius=plate_radius,
        name=cfg.name or "tv",
    )


def with_overrides(config: TvConfig, **kwargs: object) -> TvConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TvConfig | ResolvedTvConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTvConfig) else resolve_config(config)
    return (
        ("cabinet_form", r.cabinet_form),
        ("screen_tube", r.screen_tube),
        ("base_support", r.base_support),
        ("knob_count", f"n{r.knob_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _knob_ys(r: ResolvedTvConfig) -> tuple[float, ...]:
    """Absolute, symmetric knob Y positions along the control column."""
    n = r.knob_count
    return tuple(
        r.col_y + (i - (n - 1) / 2.0) * r.knob_spacing for i in range(n)
    )


# ---------------------------------------------------------------------------
# Shared rounded-rect outline (screen/bezel). From parent _rounded_rect_outline.
# ---------------------------------------------------------------------------
def _rounded_rect_outline(
    height: float, width: float, radius: float, *, segments: int = 5
) -> list[tuple[float, float]]:
    hx = height / 2.0
    hy = width / 2.0
    r = min(radius, hx * 0.95, hy * 0.95)
    arcs = (
        ((hx - r, hy - r), 0.0, math.pi / 2.0),
        ((-(hx - r), hy - r), math.pi / 2.0, math.pi),
        ((-(hx - r), -(hy - r)), math.pi, 1.5 * math.pi),
        ((hx - r, -(hy - r)), 1.5 * math.pi, 2.0 * math.pi),
    )
    points: list[tuple[float, float]] = []
    for (cx, cy), a0, a1 in arcs:
        for index in range(segments + 1):
            t = index / segments
            angle = a0 + (a1 - a0) * t
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return points


# ---------------------------------------------------------------------------
# screen_tube mesh helpers. Each preserves the source primitive type.
# ---------------------------------------------------------------------------
def _build_crt_glass_mesh(*, flat: bool, assets):
    """Lofted rounded-rect CRT face along local +Z (-> world +X).

    bulged (parent _build_crt_glass_mesh L90-103) vs flat_face (d3e64ba3 near-flat
    sections). Same Loft topology; only the sections_spec curvature changes.
    """
    if flat:
        sections_spec = (
            (0.000, 0.300, 0.370, 0.050),
            (0.005, 0.295, 0.363, 0.048),
            (0.012, 0.285, 0.350, 0.046),
            (0.015, 0.283, 0.348, 0.046),  # ~1.5 mm bulge
        )
    else:
        sections_spec = (
            (0.000, 0.300, 0.370, 0.050),
            (0.006, 0.290, 0.355, 0.050),
            (0.012, 0.255, 0.325, 0.050),
            (0.018, 0.210, 0.270, 0.060),  # convex front cap
        )
    sections = []
    for z, h, w, rr in sections_spec:
        outline = _rounded_rect_outline(h, w, rr, segments=5)
        sections.append([(x, y, z) for x, y in outline])
    geom = LoftGeometry(sections, cap=True, closed=True)
    return mesh_from_geometry(geom, "crt_glass_tube")


_PORTHOLE_DIAMETER = 0.260
_PORTHOLE_RADIUS = _PORTHOLE_DIAMETER / 2.0


def _build_porthole_glass_mesh(*, assets):
    """Bulged circular CRT porthole lathed about local +Z (fa608269 L71-90)."""
    pr = _PORTHOLE_RADIUS
    profile = [
        (pr + 0.010, 0.000),
        (pr + 0.005, 0.003),
        (pr, 0.006),
        (pr - 0.005, 0.010),
        (pr - 0.025, 0.014),
        (pr - 0.055, 0.017),
        (pr - 0.085, 0.019),
        (0.020, 0.020),
        (0.000, 0.020),
    ]
    geom = LatheGeometry(profile, segments=48, closed=True)
    return mesh_from_geometry(geom, "crt_porthole_glass")


# ---------------------------------------------------------------------------
# cabinet_form shell helpers.
# ---------------------------------------------------------------------------
def _build_pod_shell(r: ResolvedTvConfig, *, assets):
    """Rounded space-age pod shell (1a475b57 _build_pod_shell): filleted box with
    a front cavity cut. cadquery mesh — primitive preserved (Rule 3)."""
    outer = (
        cq.Workplane("XY")
        .box(r.cab_d, r.cab_w, r.cab_h)
        .edges("|Z")
        .fillet(_POD_FILLET)
    )
    inner_d = r.cab_d - _SHELL_T
    inner_w = r.cab_w - 2.0 * _SHELL_T
    inner_h = r.cab_h - 2.0 * _SHELL_T
    cavity = (
        cq.Workplane("XY")
        .transformed(offset=(_SHELL_T / 2.0, 0.0, 0.0))
        .box(inner_d, inner_w, inner_h)
    )
    pod = outer.cut(cavity)
    return mesh_from_cadquery(pod, "pod_shell", assets=assets)


def _build_console_leg_mesh(r: ResolvedTvConfig, *, assets):
    """Tapered lathe console leg along local +Z (f3c0f936 _build_console_leg_mesh)."""
    leg_h = _LEG_H * (r.z_lift / (_LEG_H * math.cos(_SPLAY_ANGLE))) if r.z_lift else _LEG_H
    profile = [
        (_LEG_R_TOP, 0.0),
        (_LEG_R_TOP * 0.95, leg_h * 0.15),
        (_LEG_R_TOP * 0.75, leg_h * 0.45),
        (_LEG_R_BOT * 1.15, leg_h * 0.75),
        (_LEG_R_BOT, leg_h * 0.92),
        (_LEG_R_BOT * 0.55, leg_h),
    ]
    geom = LatheGeometry(profile, segments=16, closed=True)
    return mesh_from_geometry(geom, "console_leg")


def _build_swivel_base_mesh(r: ResolvedTvConfig, *, assets):
    """Lathed round pedestal (397aff58 _build_swivel_base_mesh)."""
    base_radius = r.base_radius
    column_radius = _COLUMN_RADIUS * (r.base_radius / _BASE_RADIUS)
    plate_radius = r.plate_radius
    column_top_z = r.pedestal_top_z - _PLATE_H * (r.base_radius / _BASE_RADIUS)
    top_z = r.pedestal_top_z
    profile = [
        (0.000, 0.000),
        (base_radius, 0.000),
        (base_radius, _BASE_DISK_H),
        (column_radius + 0.010, _BASE_DISK_H + 0.004),
        (column_radius, _BASE_DISK_H + 0.010),
        (column_radius, column_top_z - 0.006),
        (column_radius - 0.004, column_top_z),
        (plate_radius - 0.006, column_top_z + 0.002),
        (plate_radius, column_top_z + 0.004),
        (plate_radius, top_z),
        (0.000, top_z),
    ]
    geom = LatheGeometry(profile, segments=48, closed=True)
    return mesh_from_geometry(geom, "swivel_pedestal")


# ---------------------------------------------------------------------------
# Cabinet (root or swivel child). Emits the shell + front plate + CRT + control
# column decorations as inline visuals (Rule 1). z0 is the cabinet-bottom lift
# (Z_LIFT for legs; 0 otherwise). All cabinet-local visuals are placed at z0+...
# ---------------------------------------------------------------------------
def _emit_cabinet(model: ArticulatedObject, r: ResolvedTvConfig, mats, *, assets):
    cabinet = model.part("cabinet")
    z0 = r.z_lift
    cab_w, cab_h, cab_d, wood_t = r.cab_w, r.cab_h, r.cab_d, r.wood_t
    inner_h = cab_h - 2.0 * wood_t
    inner_w = cab_w - 2.0 * wood_t

    # --- shell (cabinet_form) ---
    if r.cabinet_form == "rounded_space_age_pod":
        cabinet.visual(
            _build_pod_shell(r, assets=assets),
            origin=Origin(xyz=(0.0, 0.0, z0 + cab_h / 2.0)),
            material=mats["shell"],
            name="pod_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"space_age_cream", "glossy_black", "retro_teal"} else "wood.veneer_panel"),
        )
    else:
        cabinet.visual(
            Box((cab_d, cab_w, wood_t)),
            origin=Origin(xyz=(0.0, 0.0, z0 + wood_t / 2.0)),
            material=mats["shell"],
            name="bottom_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"wood_grain_classic", "walnut_console", "space_age_cream", "retro_teal"} else "wood.polished_varnished"),
        )
        cabinet.visual(
            Box((cab_d, cab_w, wood_t)),
            origin=Origin(xyz=(0.0, 0.0, z0 + cab_h - wood_t / 2.0)),
            material=mats["shell"],
            name="top_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"wood_grain_classic", "walnut_console", "space_age_cream", "retro_teal"} else "wood.polished_varnished"),
        )
        for label, sign in (("left", 1.0), ("right", -1.0)):
            cabinet.visual(
                Box((cab_d, wood_t, inner_h)),
                origin=Origin(
                    xyz=(0.0, sign * (cab_w / 2.0 - wood_t / 2.0), z0 + cab_h / 2.0)
                ),
                material=mats["shell"],
                name=f"{label}_side_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"wood_grain_classic", "walnut_console", "space_age_cream", "retro_teal"} else "wood.polished_varnished"),
            )
        cabinet.visual(
            Box((0.014, inner_w, inner_h)),
            origin=Origin(xyz=(-cab_d / 2.0 + 0.007, 0.0, z0 + cab_h / 2.0)),
            material=mats["shell"],
            name="back_panel", material_class_id=("wood.painted_clean" if r.palette_style in {"wood_grain_classic", "walnut_console", "space_age_cream", "retro_teal"} else "wood.polished_varnished"),
        )

    # Recessed beige front plate filling the cabinet opening.
    cabinet.visual(
        Box((_PLATE_X1 - _PLATE_X0, inner_w, inner_h)),
        origin=Origin(xyz=((_PLATE_X0 + _PLATE_X1) / 2.0, 0.0, z0 + cab_h / 2.0)),
        material=mats["plastic"],
        name="front_plate", material_class_id="plastic.opaque_glossy_molded",
    )

    # --- portable carry handle (cabinet_form = portable_with_handle) ---
    if r.cabinet_form == "portable_with_handle":
        handle_top_z = z0 + cab_h + 0.090
        handle_base_z = z0 + cab_h
        handle_points = [
            (-0.08, 0.0, handle_base_z),
            (-0.06, 0.0, handle_top_z - 0.03),
            (-0.02, 0.0, handle_top_z),
            (0.02, 0.0, handle_top_z),
            (0.06, 0.0, handle_top_z - 0.03),
            (0.08, 0.0, handle_base_z),
        ]
        handle_geom = tube_from_spline_points(
            handle_points, radius=0.006, samples_per_segment=16,
            radial_segments=20, cap_ends=True,
        )
        cabinet.visual(
            mesh_from_geometry(handle_geom, "carry_handle"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["metal"],
            name="carry_handle", material_class_id="metal.chrome_polished",
        )

    # --- CRT bezel + glass (screen_tube) ---
    if r.screen_tube == "porthole_round":
        bezel_outer = _PORTHOLE_DIAMETER + 0.060
        bezel_geom = BezelGeometry(
            (_PORTHOLE_DIAMETER, _PORTHOLE_DIAMETER),
            (bezel_outer, bezel_outer),
            0.014,
            opening_shape="circle",
            outer_shape="circle",
            recess=BezelRecess(depth=0.004, inset=0.005),
            center=False,
        )
        cabinet.visual(
            mesh_from_geometry(bezel_geom, "screen_bezel"),
            origin=Origin(
                xyz=(_PLATE_X1, r.screen_cy, z0 + r.screen_cz),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["bezel"],
            name="screen_bezel", material_class_id="plastic.opaque_glossy_molded",
        )
        cabinet.visual(
            _build_porthole_glass_mesh(assets=assets),
            origin=Origin(
                xyz=(_PLATE_X1 - 0.006, r.screen_cy, z0 + r.screen_cz),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["glass"],
            name="crt_screen", material_class_id="glass.smoked_tinted",
        )
    else:
        bezel_geom = BezelGeometry(
            (0.26, 0.33),
            (0.40, 0.40),
            0.014,
            opening_shape="rounded_rect",
            outer_shape="rounded_rect",
            opening_corner_radius=0.045,
            outer_corner_radius=0.012,
            recess=BezelRecess(depth=0.004, inset=0.005),
            center=False,
        )
        cabinet.visual(
            mesh_from_geometry(bezel_geom, "screen_bezel"),
            origin=Origin(
                xyz=(_PLATE_X1, r.screen_cy, z0 + r.screen_cz),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["bezel"],
            name="screen_bezel", material_class_id="plastic.opaque_glossy_molded",
        )
        cabinet.visual(
            _build_crt_glass_mesh(flat=(r.screen_tube == "flat_face_crt"), assets=assets),
            origin=Origin(
                xyz=(0.138, r.screen_cy, z0 + r.screen_cz),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["glass"],
            name="crt_screen", material_class_id="glass.smoked_tinted",
        )

    # --- column seam trim ---
    cabinet.visual(
        Box((0.005, 0.006, inner_h)),
        origin=Origin(xyz=(0.1445, -0.115 * (r.cab_w / _CAB_W), z0 + cab_h / 2.0)),
        material=mats["bezel"],
        name="column_seam_trim", material_class_id="plastic.opaque_glossy_molded",
    )

    # --- louvered vent (top of control column) ---
    cabinet.visual(
        Box((0.005, 0.120, 0.054)),
        origin=Origin(xyz=(0.1415, r.col_y, z0 + 0.390 * (cab_h / _CAB_H))),
        material=mats["grille"],
        name="vent_recess", material_class_id="plastic.opaque_generic",
    )
    for index, slat_z in enumerate((0.373, 0.390, 0.407)):
        cabinet.visual(
            Box((0.010, 0.118, 0.011)),
            origin=Origin(xyz=(0.146, r.col_y, z0 + slat_z * (cab_h / _CAB_H))),
            material=mats["plastic"],
            name=f"vent_louver_{index}", material_class_id="plastic.opaque_glossy_molded",
        )

    # --- dial escutcheon ---
    cabinet.visual(
        Box((0.006, 0.115, 0.115)),
        origin=Origin(xyz=(0.147, r.col_y, z0 + r.dial_cz)),
        material=mats["plastic"],
        name="dial_escutcheon", material_class_id="plastic.opaque_glossy_molded",
    )

    # --- speaker grille (fixed 12 slats; Rule 1) ---
    cabinet.visual(
        Box((0.005, 0.150, 0.150)),
        origin=Origin(xyz=(0.1415, r.col_y, z0 + 0.1175 * (cab_h / _CAB_H))),
        material=mats["grille"],
        name="grille_recess", material_class_id="fabric.open_mesh",
    )
    for index in range(12):
        slat_z = (0.052 + index * 0.0115) * (cab_h / _CAB_H)
        cabinet.visual(
            Box((0.008, 0.146, 0.0055)),
            origin=Origin(xyz=(0.146, r.col_y, z0 + slat_z)),
            material=mats["plastic"],
            name=f"grille_slat_{index}", material_class_id="plastic.opaque_glossy_molded",
        )

    cabinet.visual(
        Box((0.004, 0.075, 0.013)),
        origin=Origin(xyz=(0.1455, r.col_y, z0 + 0.031 * (cab_h / _CAB_H))),
        material=mats["silver"],
        name="samsung_nameplate", material_class_id="metal.brushed_silver",
    )

    # --- splayed console legs (base_support = splayed_console_legs; Rule 1) ---
    if r.base_support == "splayed_console_legs":
        leg_mesh = _build_console_leg_mesh(r, assets=assets)
        leg_corners = (
            (cab_d / 2.0 - _LEG_INSET, cab_w / 2.0 - _LEG_INSET),
            (cab_d / 2.0 - _LEG_INSET, -(cab_w / 2.0 - _LEG_INSET)),
            (-(cab_d / 2.0 - _LEG_INSET), cab_w / 2.0 - _LEG_INSET),
            (-(cab_d / 2.0 - _LEG_INSET), -(cab_w / 2.0 - _LEG_INSET)),
        )
        for i in range(4):
            cx, cy = leg_corners[i]
            yaw = math.atan2(-cy, -cx)
            cabinet.visual(
                leg_mesh,
                origin=Origin(xyz=(cx, cy, z0), rpy=(math.pi, _SPLAY_ANGLE, yaw)),
                material=mats["shell"],
                name=f"leg_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"walnut_console", "space_age_cream", "glossy_black", "retro_teal"} else "wood.oak"),
            )
        for i in range(4):
            cx, cy = leg_corners[i]
            cabinet.visual(
                Box((0.044, 0.044, 0.012)),
                origin=Origin(xyz=(cx, cy, z0 - 0.006)),
                material=mats["shell"],
                name=f"leg_mount_{i}", material_class_id=("wood.painted_clean" if r.palette_style in {"walnut_console", "space_age_cream", "glossy_black", "retro_teal"} else "wood.oak"),
            )

    return cabinet, z0


# ---------------------------------------------------------------------------
# channel_dial (fixed CONTINUOUS +X) — captured stem + off-axis pointer_wedge.
# ---------------------------------------------------------------------------
def _emit_channel_dial(model, r: ResolvedTvConfig, cabinet, mats, *, z0: float, assets):
    dial = model.part("channel_dial")
    dial.visual(
        Cylinder(radius=0.009, length=0.022),
        origin=Origin(xyz=(-0.0105, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="dial_stem", material_class_id="plastic.opaque_generic",
    )
    dial_ring = KnobGeometry(
        r.dial_diameter,
        0.018,
        body_style="cylindrical",
        grip=KnobGrip(style="ribbed", count=24, depth=0.0012, width=0.002),
        center=False,
    )
    dial.visual(
        mesh_from_geometry(dial_ring, "dial_ribbed_ring"),
        origin=Origin(xyz=(0.0005, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="dial_ribbed_ring", material_class_id="metal.chrome_polished",
    )
    dial.visual(
        Cylinder(radius=0.027, length=0.004),
        origin=Origin(xyz=(0.0205, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="dial_face", material_class_id="plastic.opaque_glossy_molded",
    )
    tick_radius = 0.0215
    for index in range(8):
        angle = index * math.pi / 4.0
        dial.visual(
            Box((0.0015, 0.002, 0.006)),
            origin=Origin(
                xyz=(0.023, -tick_radius * math.sin(angle), tick_radius * math.cos(angle)),
                rpy=(angle, 0.0, 0.0),
            ),
            material=mats["marking"],
            name=f"dial_tick_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # Off-axis pointer proving continuous rotation (spin AABB feature).
    dial.visual(
        Box((0.004, 0.005, 0.013)),
        origin=Origin(xyz=(0.0235, 0.0, 0.0185)),
        material=mats["marking"],
        name="pointer_wedge", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    model.articulation(
        "cabinet_to_channel_dial",
        ArticulationType.CONTINUOUS,
        parent=cabinet,
        child=dial,
        origin=Origin(xyz=(_DIAL_JOINT_X, r.col_y, z0 + r.dial_cz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.6, velocity=8.0),
    )
    return dial


# ---------------------------------------------------------------------------
# knob_count multiplicity (N REVOLUTE +X knobs along the column Y).
# ---------------------------------------------------------------------------
def _emit_knobs(model, r: ResolvedTvConfig, cabinet, mats, *, z0: float, assets) -> list[str]:
    knob_geom = KnobGeometry(
        r.knob_diameter,
        0.015,
        body_style="cylindrical",
        grip=KnobGrip(style="fluted", count=16, depth=0.001),
        indicator=KnobIndicator(style="line", mode="raised"),
        center=False,
    )
    knob_mesh = mesh_from_geometry(knob_geom, "small_control_knob")
    names: list[str] = []
    for i, knob_y in enumerate(_knob_ys(r)):
        knob_name = f"knob_{i}"
        knob = model.part(knob_name)
        knob.visual(
            Cylinder(radius=0.005, length=0.018),
            origin=Origin(xyz=(-0.0085, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark"],
            name=f"{knob_name}_stem", material_class_id="plastic.opaque_generic",
        )
        knob.visual(
            knob_mesh,
            origin=Origin(xyz=(0.0005, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["plastic"],
            name=f"{knob_name}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"cabinet_to_{knob_name}",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=knob,
            origin=Origin(xyz=(_KNOB_JOINT_X, knob_y, z0 + r.knob_row_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=0.3, velocity=8.0, lower=-r.knob_range, upper=r.knob_range
            ),
        )
        names.append(knob_name)
    return names


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_tv(
    config: TvConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"tv_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # base_support = swivel_base: a new root pedestal; cabinet becomes its child.
    if r.base_support == "swivel_base":
        swivel_base = model.part("swivel_base")
        swivel_base.visual(
            _build_swivel_base_mesh(r, assets=assets),
            origin=Origin(),
            material=mats["base"],
            name="pedestal", material_class_id="metal.paint_coated",
        )
        swivel_base.visual(
            Cylinder(radius=r.plate_radius - 0.003, length=0.002),
            origin=Origin(xyz=(0.0, 0.0, r.pedestal_top_z + 0.001)),
            material=mats["metal"],
            name="turntable_ring", material_class_id="metal.chrome_polished",
        )

    cabinet, z0 = _emit_cabinet(model, r, mats, assets=assets)

    if r.base_support == "swivel_base":
        # Cabinet rides the turntable. Joint origin at pedestal top (parent frame);
        # the cabinet's own bottom panel sits at z=wood_t/2 in its local frame so
        # the joint origin (z=0 child-local) is within tol of the cabinet AABB.
        model.articulation(
            "base_to_cabinet",
            ArticulationType.CONTINUOUS,
            parent=swivel_base,
            child=cabinet,
            origin=Origin(xyz=(0.0, 0.0, r.pedestal_top_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=3.0, velocity=2.0),
        )

    _emit_channel_dial(model, r, cabinet, mats, z0=z0, assets=assets)
    _emit_knobs(model, r, cabinet, mats, z0=z0, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_tv(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_tv(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_tv_tests(
    object_model: ArticulatedObject,
    config: TvConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    cabinet = object_model.get_part("cabinet")
    dial = object_model.get_part("channel_dial")
    knob_names = [f"knob_{i}" for i in range(r.knob_count)]
    knobs = [object_model.get_part(n) for n in knob_names]

    # ---- Captured-pin allowances (element-scoped). ----
    ctx.allow_overlap(
        dial, cabinet, elem_a="dial_stem", elem_b="front_plate",
        reason="Dial shaft is intentionally captured inside the front plate bore.",
    )
    ctx.allow_overlap(
        dial, cabinet, elem_a="dial_stem", elem_b="dial_escutcheon",
        reason="Dial shaft passes through the escutcheon boss.",
    )
    for name, knob in zip(knob_names, knobs):
        ctx.allow_overlap(
            knob, cabinet, elem_a=f"{name}_stem", elem_b="front_plate",
            reason="Knob shaft is intentionally captured inside the front plate bore.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- captured stems stay inserted (rest + actuated pose). ----
    ctx.expect_overlap(
        dial, cabinet, axes="x", elem_a="dial_stem", elem_b="front_plate",
        min_overlap=0.008, name="dial shaft stays inserted in the front plate",
    )
    for name, knob in zip(knob_names, knobs):
        ctx.expect_overlap(
            knob, cabinet, axes="x", elem_a=f"{name}_stem", elem_b="front_plate",
            min_overlap=0.008, name=f"{name} shaft stays inserted in the front plate",
        )

    dial_joint = object_model.get_articulation("cabinet_to_channel_dial")
    knob0_joint = object_model.get_articulation("cabinet_to_knob_0")
    with ctx.pose({dial_joint: math.pi, knob0_joint: r.knob_range}):
        ctx.expect_overlap(
            dial, cabinet, axes="x", elem_a="dial_stem", elem_b="front_plate",
            min_overlap=0.008, name="spun dial shaft remains captured",
        )
        ctx.expect_overlap(
            knobs[0], cabinet, axes="x", elem_a="knob_0_stem", elem_b="front_plate",
            min_overlap=0.008, name="turned knob shaft remains captured",
        )

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("cabinet part present", "cabinet" in part_names, details=str(sorted(part_names)))

    # Root part: swivel_base when swivel, else cabinet.
    if r.base_support == "swivel_base":
        ctx.check(
            "swivel_base is the root part",
            "swivel_base" in part_names,
            details=str(sorted(part_names)),
        )
        bj = object_model.get_articulation("base_to_cabinet")
        ctx.check(
            "base_to_cabinet is CONTINUOUS about +Z (turntable)",
            bj.articulation_type == ArticulationType.CONTINUOUS and abs(bj.axis[2]) > 0.99,
            details=f"type={bj.articulation_type} axis={tuple(bj.axis)}",
        )

    # CRT screen on the left two-thirds, recessed.
    screen = cabinet.get_visual("crt_screen")
    bezel = cabinet.get_visual("screen_bezel")
    ctx.check(
        "CRT screen sits on the left two-thirds of the front",
        screen.origin.xyz[1] > 0.04 and bezel.origin.xyz[1] > 0.04,
        details=f"screen_y={screen.origin.xyz[1]:.4f} bezel_y={bezel.origin.xyz[1]:.4f}",
    )

    # Grille has 12 fixed slats (Rule 1).
    n_slats = sum(
        1 for v in cabinet.visuals if v.name and v.name.startswith("grille_slat_")
    )
    ctx.check("speaker grille has 12 fixed slats", n_slats == 12, details=f"got {n_slats}")

    # ---- channel dial joint. ----
    ctx.check(
        "channel dial is CONTINUOUS about +X",
        dial_joint.articulation_type == ArticulationType.CONTINUOUS
        and abs(dial_joint.axis[0]) > 0.99,
        details=f"type={dial_joint.articulation_type} axis={tuple(dial_joint.axis)}",
    )
    lim = dial_joint.motion_limits
    ctx.check(
        "channel dial rotation is unlimited",
        lim is not None and lim.lower is None and lim.upper is None,
        details=f"limits={lim}",
    )
    pointer = dial.get_visual("pointer_wedge")
    pointer_off = math.hypot(pointer.origin.xyz[1], pointer.origin.xyz[2])
    ctx.check(
        "dial carries an off-axis pointer proving continuous rotation",
        pointer_off > 0.012,
        details=f"pointer off-axis distance {pointer_off:.4f}",
    )

    # ---- N knobs REVOLUTE +X, symmetric Y placement. ----
    ctx.check(
        "knob_count knobs present (multiplicity axis)",
        len(knob_names) == r.knob_count and all(n in part_names for n in knob_names),
        details=f"expected N={r.knob_count}, parts={sorted(part_names)}",
    )
    knob_ys = _knob_ys(r)
    for i, knob_y in enumerate(knob_ys):
        j = object_model.get_articulation(f"cabinet_to_knob_{i}")
        ctx.check(
            f"knob_{i} is REVOLUTE about +X with symmetric travel",
            j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[0]) > 0.99
            and j.motion_limits is not None
            and abs(j.motion_limits.lower + r.knob_range) < 1e-6
            and abs(j.motion_limits.upper - r.knob_range) < 1e-6,
            details=f"type={j.articulation_type} axis={tuple(j.axis)} lim={j.motion_limits}",
        )
        ctx.check(
            f"knob_{i} sits on the control column row at the expected Y",
            abs(j.origin.xyz[1] - knob_y) < 1e-6,
            details=f"origin={j.origin.xyz}",
        )

    # ---- knob-row clearance proven from authored dims (N>=2). ----
    if r.knob_count >= 2:
        row_w = (r.knob_count - 1) * r.knob_spacing + r.knob_diameter
        col_span = 0.135 * (r.cab_w / _CAB_W)
        ctx.check(
            "knob row fits within the control column",
            row_w <= col_span,
            details=f"row_w={row_w:.4f} col_span={col_span:.4f}",
        )
        ctx.check(
            "adjacent knob caps stay disjoint",
            r.knob_spacing >= r.knob_diameter + 1e-6,
            details=f"spacing={r.knob_spacing:.4f} cap_dia={r.knob_diameter:.4f}",
        )

    # ---- ground contact. ----
    if r.base_support == "swivel_base":
        anchor = object_model.get_part("swivel_base")
    else:
        anchor = cabinet
    aabb = ctx.part_world_aabb(anchor)
    if aabb is not None:
        ctx.check(
            "object rests near the ground",
            aabb[0][2] < 0.03,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- slot_choices recorded + N encoded. ----
    ctx.check(
        "slot_choices recorded with knob_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "TvConfig",
    "ResolvedTvConfig",
    "build_tv",
    "build_seeded_tv",
    "config_from_seed",
    "resolve_config",
    "run_tv_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
