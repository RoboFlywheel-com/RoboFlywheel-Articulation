# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained Bag_Suitcase / Shopping bucket template (TEMPLATE_DOMAIN).

Rebuilt from the reviewed source pool of the ``Bag_Suitcase / Shopping bucket``
picture subcategory; see
``articraft_template_authoring/source_maps/Bag_Suitcase_Shopping_bucket.md`` and
``articraft_template_authoring/designs/Bag_Suitcase_Shopping_bucket.json``.

Subcategory identity: **one hand-held shopping basket**. An open-mouth tapered
tub standing on the floor, thin-walled with a rolled rim, carrying either a
rim-hinged bail or -- when the mouth is closed by a lid -- molded short-wall grip
cutouts, plus optional interior storage. The shell stays closed all round: no
opening is cut through the wall and nothing hangs under the floor (the
side-opening gate and under-basket drawer sources were rejected in review). Stacks/nests of several baskets,
wheeled trolley baskets, collapsible crates and telescoping pull-up bars are
explicitly out of scope and were rejected during source review.

Two decisions drive the whole file:

* **One rim profile.** ``_profile_points`` returns the closed mouth outline of
  the selected ``body_form``, and the tub loft, the rolled rim, the lid outline,
  the hinge line, the pivot bosses and the interior floor are all derived from
  it. A lid therefore follows a hexagonal or round mouth instead of overhanging
  it, which a hard-coded rectangular panel cannot do.
* **handle and closure are one slot.** A bail arching over the mouth and a lid
  seating on it occupy the same space, so ``top_configuration`` is a single
  structural family (AUTHORING §7) rather than two slots behind a compatibility
  gate. Closed-top candidates carry the molded grip cutouts that source record
  ``..._ab5a00e2`` uses in place of a bail; the front-wall candidates keep the
  bail their own sources have, since a front opening does not contest the mouth.

Every revolute joint is solved with ``mate_axes`` and registered with
``register_interface_mate``. **No ``allow_overlap`` anywhere**: captured pivots
are a bore with a running clearance around a real axle, not interpenetrating
solids. No source runtime, snapshot or other template is imported.
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
    Inertial,
    MotionLimits,
    MotionProperties,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    register_interface_mate,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "rectangular",
    "rounded_oval_deep",
    "hexagonal_footprint",
    "round_cylindrical_bucket",
    "tapered_stackable",
    "shallow_wide_tray",
]
WallStyle = Literal[
    "slotted_perforated",
    "steel_wire_mesh",
    "horizontal_slot_grid",
    "diagonal_lattice",
    "solid_smooth",
]
TopConfiguration = Literal[
    "open_bail_fixed_arch",
    "open_bail_swing",
    "open_bail_dual_fold",
    "lid_hinged_top",
    "lid_clamshell",
]
SecondaryStorage = Literal[
    "none",
    "two_compartment_divider",
    "removable_inner_caddy",
]
PaletteStyle = Literal["red_plastic", "blue_plastic", "galvanized_steel", "charcoal"]

BODY_FORMS: tuple[BodyForm, ...] = (
    "rectangular",
    "rounded_oval_deep",
    "hexagonal_footprint",
    "round_cylindrical_bucket",
    "tapered_stackable",
    "shallow_wide_tray",
)
WALL_STYLES: tuple[WallStyle, ...] = (
    "slotted_perforated",
    "steel_wire_mesh",
    "horizontal_slot_grid",
    "diagonal_lattice",
    "solid_smooth",
)
TOP_CONFIGURATIONS: tuple[TopConfiguration, ...] = (
    "open_bail_fixed_arch",
    "open_bail_swing",
    "open_bail_dual_fold",
    "lid_hinged_top",
    "lid_clamshell",
)
SECONDARY_STORAGES: tuple[SecondaryStorage, ...] = (
    "none",
    "two_compartment_divider",
    "removable_inner_caddy",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "red_plastic",
    "blue_plastic",
    "galvanized_steel",
    "charcoal",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("body_form", BODY_FORMS, role="tub plan/section family"),
        component_slot("wall_style", WALL_STYLES, role="wall treatment"),
        component_slot(
            "top_configuration",
            TOP_CONFIGURATIONS,
            role="mouth mechanism: carry hardware together with any closure",
        ),
        component_slot(
            "secondary_storage", SECONDARY_STORAGES, role="optional extra storage mechanism"
        ),
    )
)

# Closed-top families: the mouth is covered, so the carry hardware is a pair of
# molded short-wall grip cutouts instead of a bail (source ``..._ab5a00e2``).
CLOSED_TOPS: frozenset[str] = frozenset({"lid_hinged_top", "lid_clamshell"})
BAIL_TOPS: frozenset[str] = frozenset(
    {"open_bail_fixed_arch", "open_bail_swing", "open_bail_dual_fold"}
)

# ---------------------------------------------------------------------------
# Fixed hardware constants (unscaled metres)
# ---------------------------------------------------------------------------
_BOSS_CLEARANCE = 0.0008  # running clearance between a bail bore and its axle
_HINGE_KNUCKLE_R = 0.0075  # lid hinge knuckle outer radius
_HINGE_AXLE_R = 0.0032  # rim hinge axle radius
_LID_RUNNING_CLEAR = 0.0015  # lid outline inset from the rim profile
_FRONT_PANEL_CLEAR = 0.0015  # running clearance around the hinged front panel
# Hinge bores are tessellated polygons, so a nominal 0.8 mm gap reads as ~2.3 mm
# once faceted -- past the 1 mm support tolerance. Keep the hinge fit tight.
_HINGE_BORE_CLEAR = 0.0003
_CADDY_GUIDE_CLEAR = 0.0008  # caddy-to-rib running clearance
_CADDY_GUIDE_T = 0.010
_CADDY_GUIDE_ENGAGE = 0.010  # tray still overlapping the ribs at full lift
# Plan-outline resolution. Every wall boolean runs against a solid lofted from
# these polylines, so the count is a direct multiplier on build time; 20/4 keeps
# the curved forms visually round while staying well inside the 12 s per-build
# preflight budget.
_PROFILE_SEGMENTS = 20  # points around a curved profile
_CORNER_SEGMENTS = 4  # points per rounded-rectangle corner arc


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ShoppingBucketConfig:
    body_form: BodyForm | None = None
    wall_style: WallStyle | None = None
    top_configuration: TopConfiguration | None = None
    secondary_storage: SecondaryStorage | None = None

    mouth_len_m: float = 0.360
    mouth_depth_m: float = 0.245
    body_height_m: float = 0.225
    taper_ratio: float = 0.84
    wall_thickness_m: float = 0.0040
    rim_lip_m: float = 0.0060

    slot_columns: int = 5
    slot_width_m: float = 0.015
    wire_pitch_m: float = 0.025
    wire_radius_m: float = 0.0016
    slot_rows: int = 4
    slot_row_span_ratio: float = 0.68
    slot_row_stagger: int = 1
    lattice_pitch_m: float = 0.034
    lattice_bar_m: float = 0.006
    rib_count: int = 2

    bail_rise_m: float = 0.125
    bail_bar_radius_m: float = 0.0055
    bail_swing_rad: float = 1.40
    side_bail_rise_m: float = 0.100
    lid_thickness_m: float = 0.011
    lid_open_rad: float = 1.90
    leaf_thickness_m: float = 0.010
    leaf_open_rad: float = 1.60
    grip_cutout_w_m: float = 0.105
    grip_cutout_h_m: float = 0.042

    divider_thickness_m: float = 0.0040
    divider_height_ratio: float = 0.88
    caddy_height_ratio: float = 0.42
    caddy_plan_ratio: float = 0.68

    palette_style: PaletteStyle = "red_plastic"
    name: str = "shopping_bucket"


@dataclass(frozen=True)
class ResolvedShoppingBucketConfig:
    body_form: BodyForm
    wall_style: WallStyle
    top_configuration: TopConfiguration
    secondary_storage: SecondaryStorage

    mouth_len_m: float
    mouth_depth_m: float
    body_height_m: float
    taper_ratio: float
    wall_thickness_m: float
    rim_lip_m: float

    slot_columns: int
    slot_width_m: float
    wire_pitch_m: float
    wire_radius_m: float
    slot_rows: int
    slot_row_span_ratio: float
    slot_row_stagger: int
    lattice_pitch_m: float
    lattice_bar_m: float
    rib_count: int

    bail_rise_m: float
    bail_bar_radius_m: float
    bail_swing_rad: float
    side_bail_rise_m: float
    lid_thickness_m: float
    lid_open_rad: float
    leaf_thickness_m: float
    leaf_open_rad: float
    grip_cutout_w_m: float
    grip_cutout_h_m: float

    divider_thickness_m: float
    divider_height_ratio: float
    caddy_height_ratio: float
    caddy_plan_ratio: float

    palette_style: PaletteStyle
    name: str

    # -- derived reads used all over the build ------------------------------
    @property
    def has_bail(self) -> bool:
        return self.top_configuration in BAIL_TOPS

    @property
    def has_closed_top(self) -> bool:
        return self.top_configuration in CLOSED_TOPS

    @property
    def rim_z(self) -> float:
        return self.body_height_m

    @property
    def floor_top_z(self) -> float:
        return self.wall_thickness_m


# AUTHORING §4 names the exported dataclasses `Config` / `ResolvedConfig`; the
# corner runner builds its cases through those names.
Config = ShoppingBucketConfig
ResolvedConfig = ResolvedShoppingBucketConfig


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, options):
    return value if value in options else options[0]


def config_from_seed(seed: int) -> ShoppingBucketConfig:
    """Deterministic sampling over the declared domain (seed 0 is not special)."""
    rng = random.Random(seed)
    choice = TEMPLATE_DOMAIN.sample(rng)
    return ShoppingBucketConfig(
        body_form=choice["body_form"],
        wall_style=choice["wall_style"],
        top_configuration=choice["top_configuration"],
        secondary_storage=choice["secondary_storage"],
        mouth_len_m=round(rng.uniform(0.300, 0.440), 4),
        mouth_depth_m=round(rng.uniform(0.200, 0.300), 4),
        body_height_m=round(rng.uniform(0.170, 0.290), 4),
        taper_ratio=round(rng.uniform(0.66, 0.94), 4),
        wall_thickness_m=round(rng.uniform(0.0028, 0.0060), 5),
        rim_lip_m=round(rng.uniform(0.0040, 0.0090), 5),
        slot_columns=rng.randint(3, 8),
        slot_width_m=round(rng.uniform(0.010, 0.022), 4),
        wire_pitch_m=round(rng.uniform(0.018, 0.034), 4),
        wire_radius_m=round(rng.uniform(0.0011, 0.0022), 5),
        slot_rows=rng.randint(2, 6),
        slot_row_span_ratio=round(rng.uniform(0.45, 0.85), 4),
        slot_row_stagger=rng.randint(0, 1),
        lattice_pitch_m=round(rng.uniform(0.024, 0.048), 4),
        lattice_bar_m=round(rng.uniform(0.004, 0.010), 4),
        rib_count=rng.randint(0, 4),
        bail_rise_m=round(rng.uniform(0.090, 0.165), 4),
        bail_bar_radius_m=round(rng.uniform(0.0040, 0.0080), 5),
        bail_swing_rad=round(rng.uniform(1.10, 1.57), 4),
        side_bail_rise_m=round(rng.uniform(0.070, 0.140), 4),
        lid_thickness_m=round(rng.uniform(0.008, 0.015), 4),
        lid_open_rad=round(rng.uniform(1.40, 2.10), 4),
        leaf_thickness_m=round(rng.uniform(0.007, 0.013), 4),
        leaf_open_rad=round(rng.uniform(1.30, 1.90), 4),
        grip_cutout_w_m=round(rng.uniform(0.085, 0.130), 4),
        grip_cutout_h_m=round(rng.uniform(0.032, 0.055), 4),
        divider_thickness_m=round(rng.uniform(0.0028, 0.0060), 5),
        divider_height_ratio=round(rng.uniform(0.70, 1.00), 4),
        caddy_height_ratio=round(rng.uniform(0.30, 0.55), 4),
        caddy_plan_ratio=round(rng.uniform(0.55, 0.80), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"seeded_shopping_bucket_{seed}",
    )


def resolve_config(
    config: ShoppingBucketConfig | None = None,
) -> ResolvedShoppingBucketConfig:
    """Range-check the independent parameters. No slot is ever silently rewritten:
    the domain has no compatibility gate, so every declared combination builds."""
    cfg = config or ShoppingBucketConfig()

    mouth_len = _clamp(cfg.mouth_len_m, 0.300, 0.440)
    mouth_depth = _clamp(cfg.mouth_depth_m, 0.200, 0.300)
    # The long axis is the identity of the plan: keep X strictly wider than Y.
    mouth_depth = min(mouth_depth, mouth_len - 0.060)

    return ResolvedShoppingBucketConfig(
        body_form=_pick(cfg.body_form, BODY_FORMS),
        wall_style=_pick(cfg.wall_style, WALL_STYLES),
        top_configuration=_pick(cfg.top_configuration, TOP_CONFIGURATIONS),
        secondary_storage=_pick(cfg.secondary_storage, SECONDARY_STORAGES),
        mouth_len_m=mouth_len,
        mouth_depth_m=mouth_depth,
        body_height_m=_clamp(cfg.body_height_m, 0.170, 0.290),
        taper_ratio=_clamp(cfg.taper_ratio, 0.66, 0.94),
        wall_thickness_m=_clamp(cfg.wall_thickness_m, 0.0028, 0.0060),
        rim_lip_m=_clamp(cfg.rim_lip_m, 0.0040, 0.0090),
        slot_columns=int(_clamp(cfg.slot_columns, 3, 8)),
        slot_width_m=_clamp(cfg.slot_width_m, 0.010, 0.022),
        wire_pitch_m=_clamp(cfg.wire_pitch_m, 0.018, 0.034),
        wire_radius_m=_clamp(cfg.wire_radius_m, 0.0011, 0.0022),
        slot_rows=int(_clamp(cfg.slot_rows, 2, 6)),
        slot_row_span_ratio=_clamp(cfg.slot_row_span_ratio, 0.45, 0.85),
        slot_row_stagger=int(_clamp(cfg.slot_row_stagger, 0, 1)),
        lattice_pitch_m=_clamp(cfg.lattice_pitch_m, 0.024, 0.048),
        lattice_bar_m=_clamp(cfg.lattice_bar_m, 0.004, 0.010),
        rib_count=int(_clamp(cfg.rib_count, 0, 4)),
        bail_rise_m=_clamp(cfg.bail_rise_m, 0.090, 0.165),
        bail_bar_radius_m=_clamp(cfg.bail_bar_radius_m, 0.0040, 0.0080),
        bail_swing_rad=_clamp(cfg.bail_swing_rad, 1.10, 1.57),
        side_bail_rise_m=_clamp(cfg.side_bail_rise_m, 0.070, 0.140),
        lid_thickness_m=_clamp(cfg.lid_thickness_m, 0.008, 0.015),
        lid_open_rad=_clamp(cfg.lid_open_rad, 1.40, 2.10),
        leaf_thickness_m=_clamp(cfg.leaf_thickness_m, 0.007, 0.013),
        leaf_open_rad=_clamp(cfg.leaf_open_rad, 1.30, 1.90),
        grip_cutout_w_m=_clamp(cfg.grip_cutout_w_m, 0.085, 0.130),
        grip_cutout_h_m=_clamp(cfg.grip_cutout_h_m, 0.032, 0.055),
        divider_thickness_m=_clamp(cfg.divider_thickness_m, 0.0028, 0.0060),
        divider_height_ratio=_clamp(cfg.divider_height_ratio, 0.70, 1.00),
        caddy_height_ratio=_clamp(cfg.caddy_height_ratio, 0.30, 0.55),
        caddy_plan_ratio=_clamp(cfg.caddy_plan_ratio, 0.55, 0.80),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        name=cfg.name or "shopping_bucket",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedShoppingBucketConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("wall_style", r.wall_style),
        ("top_configuration", r.top_configuration),
        ("secondary_storage", r.secondary_storage),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


TEMPLATE_CORNERS = (
    corner_case(
        "hex_mouth_with_hinged_lid",
        {"body_form": "hexagonal_footprint", "top_configuration": "lid_hinged_top"},
        reason="Widest profile mismatch risk: a six-sided mouth must still receive a lid whose outline follows it.",
    ),
    corner_case(
        "round_mouth_with_clamshell",
        {"body_form": "round_cylindrical_bucket", "top_configuration": "lid_clamshell"},
        reason="Two leaves split across a circular rim; both halves must follow the arc and meet on the centreline.",
    ),
    corner_case(
        "shallow_tray_with_caddy",
        {
            "body_form": "shallow_wide_tray",
            "secondary_storage": "removable_inner_caddy",
            "top_configuration": "lid_hinged_top",
        },
        reason="Least headroom: the guided tray lift, its ribs and a closed lid all share a very shallow cavity.",
    ),
)


# ===========================================================================
# The rim profile: ONE outline drives the tub, the rim, the lid and the hinge
# ===========================================================================
def _profile_points(r: ResolvedShoppingBucketConfig, *, scale: float = 1.0, offset: float = 0.0):
    """Closed plan outline of the selected body form, centred on the origin.

    ``scale`` shrinks the outline towards the centre (the floor section is the
    mouth section scaled by ``taper_ratio``); ``offset`` grows it radially, which
    is how the rolled rim lip and the interior cavity are derived. Returns a list
    of ``(x, y)`` points, counter-clockwise, without repeating the first point.

    This is the single place the plan shape is decided. Everything that has to
    agree with the mouth -- the rim, the lid outline, the hinge line, the pivot
    bosses, the cavity floor -- reads it, so they cannot disagree.
    """
    hx = 0.5 * r.mouth_len_m * scale + offset
    hy = 0.5 * r.mouth_depth_m * scale + offset
    form = r.body_form

    if form in ("rectangular", "tapered_stackable", "shallow_wide_tray"):
        # Rounded-corner rectangle. The corner radius is a fixed fraction of the
        # short half-span so it survives the taper without self-intersecting.
        rad = min(0.030, 0.35 * hy)
        pts = []
        corners = (
            (hx - rad, hy - rad),
            (-(hx - rad), hy - rad),
            (-(hx - rad), -(hy - rad)),
            (hx - rad, -(hy - rad)),
        )
        starts = (0.0, 0.5 * math.pi, math.pi, 1.5 * math.pi)
        for (cx, cy), start in zip(corners, starts):
            for i in range(_CORNER_SEGMENTS + 1):
                a = start + (0.5 * math.pi) * i / _CORNER_SEGMENTS
                pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
        return pts

    if form in ("rounded_oval_deep", "round_cylindrical_bucket"):
        # Ellipse; the round bucket is the near-circular member of the family.
        if form == "round_cylindrical_bucket":
            hy = min(hy, hx) * 0.96
            hx = hy / 0.96
        return [
            (
                hx * math.cos(2.0 * math.pi * i / _PROFILE_SEGMENTS),
                hy * math.sin(2.0 * math.pi * i / _PROFILE_SEGMENTS),
            )
            for i in range(_PROFILE_SEGMENTS)
        ]

    # hexagonal_footprint: flat-topped hexagon stretched to the mouth aspect.
    base = [
        (1.0, 0.0),
        (0.5, 1.0),
        (-0.5, 1.0),
        (-1.0, 0.0),
        (-0.5, -1.0),
        (0.5, -1.0),
    ]
    return [(hx * ux, hy * uy) for ux, uy in base]


def _profile_wire(points):
    return cq.Workplane("XY").polyline([(x, y) for x, y in points]).close()


def _loft_between(points_bottom, z_bottom: float, points_top, z_top: float):
    """Ruled loft between two plan outlines at two heights.

    Both sections have to live on one Workplane chain (``.workplane(offset=...)``);
    adding a second independent Workplane does not give ``loft`` two wires.
    """
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .polyline([(x, y) for x, y in points_bottom])
        .close()
        .workplane(offset=z_top - z_bottom)
        .polyline([(x, y) for x, y in points_top])
        .close()
        .loft(ruled=True)
    )


def _prism(points, z_bottom: float, height: float):
    """Straight prism from a plan outline."""
    return (
        cq.Workplane("XY")
        .workplane(offset=z_bottom)
        .polyline([(x, y) for x, y in points])
        .close()
        .extrude(height)
    )


def _profile_at(r: ResolvedShoppingBucketConfig, z: float, *, offset: float = 0.0):
    """Outline of the tub wall at height ``z`` (the loft is linear in z)."""
    t = 0.0 if r.body_height_m <= 0 else _clamp(z / r.body_height_m, 0.0, 1.0)
    scale = r.taper_ratio + (1.0 - r.taper_ratio) * t
    return _profile_points(r, scale=scale, offset=offset)


def _profile_y_at_x(points, x: float) -> float:
    """Max |y| of the outline at a given x, by scanning the polygon edges.

    A lug placed at (x, max_y) is off the wall entirely on an ellipse or hexagon,
    which the compiler reports as a floating island inside basket_tub.
    """
    best = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        if (x0 - x) * (x1 - x) <= 0.0 and abs(x1 - x0) > 1e-12:
            t = (x - x0) / (x1 - x0)
            best = max(best, abs(y0 + t * (y1 - y0)))
    return best


def _profile_x_at_y(points, y: float) -> float:
    """Max |x| of the outline at a given y (mirror of ``_profile_y_at_x``)."""
    best = 0.0
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        if (y0 - y) * (y1 - y) <= 0.0 and abs(y1 - y0) > 1e-12:
            t = (y - y0) / (y1 - y0)
            best = max(best, abs(x0 + t * (x1 - x0)))
    return best


def _profile_half_spans(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return max(xs), max(ys)


# ===========================================================================
# body_form candidates: the tub solid
# ===========================================================================
def _body_form_solid(r: ResolvedShoppingBucketConfig):
    """Hollow tapered tub lofted between the floor and mouth profiles."""
    outer = _loft_between(
        _profile_at(r, 0.0), 0.0, _profile_at(r, r.body_height_m), r.body_height_m
    )
    cavity = _loft_between(
        _profile_at(r, r.floor_top_z, offset=-r.wall_thickness_m),
        r.floor_top_z,
        _profile_at(r, r.body_height_m, offset=-r.wall_thickness_m),
        r.body_height_m + 0.002,
    )
    tub = outer.cut(cavity)

    # Rolled rim: a lipped band around the mouth, derived from the same profile.
    rim_h = max(0.006, 2.2 * r.rim_lip_m)
    rim_solid = _prism(
        _profile_at(r, r.body_height_m, offset=r.rim_lip_m), r.body_height_m - rim_h, rim_h
    )
    rim_bore = _prism(
        _profile_at(r, r.body_height_m, offset=-r.wall_thickness_m),
        r.body_height_m - rim_h - 0.001,
        rim_h + 0.002,
    )
    tub = tub.union(rim_solid.cut(rim_bore))
    return tub


def _body_form_build(r: ResolvedShoppingBucketConfig):
    return _body_form_solid(r)


# ===========================================================================
# wall_style candidates
# ===========================================================================
def _wall_window(r: ResolvedShoppingBucketConfig, z0: float, z1: float):
    """A ring-shaped solid filling the wall between two heights.

    Wall treatments subtract their pattern from THIS, then hit the tub with one
    boolean. Cutting the tub once per slot instead makes each successive cut work
    on a more complex solid and blows the per-build budget.
    """
    outer = _prism(_profile_at(r, 0.5 * (z0 + z1), offset=0.03), z0, z1 - z0)
    inner = _prism(_profile_at(r, 0.5 * (z0 + z1), offset=-0.03), z0 - 0.002, z1 - z0 + 0.004)
    return outer.cut(inner)


def _wall_band_range(r: ResolvedShoppingBucketConfig, bottom_pad: float, top_pad: float):
    z0 = r.floor_top_z + bottom_pad
    z1 = r.body_height_m - 2.4 * r.rim_lip_m - top_pad
    return z0, z1


def _wall_style_slotted_perforated_build(r: ResolvedShoppingBucketConfig, tub):
    """Vertical slot columns cut through the walls (source ..._254643d5)."""
    z0, z1 = _wall_band_range(r, 0.020, 0.012)
    if z1 <= z0 + 0.010:
        return tub
    hx, _hy = _profile_half_spans(_profile_at(r, 0.5 * (z0 + z1)))
    span = 2.0 * hx * 0.72
    n = max(1, r.slot_columns)
    cutter = None
    for i in range(n):
        x = -span * 0.5 + span * (i + 0.5) / n
        col = (
            cq.Workplane("XY")
            .box(r.slot_width_m, 1.0, z1 - z0, centered=(True, True, False))
            .translate((x, 0.0, z0))
        )
        cutter = col if cutter is None else cutter.union(col)
    return tub.cut(cutter.intersect(_wall_window(r, z0, z1)))


def _wall_style_steel_wire_mesh_build(r: ResolvedShoppingBucketConfig, tub):
    """Open wire grid: the wall is removed except for the welded wire courses
    (source ..._1d416a15 builds the equivalent grid from wire segments)."""
    z0, z1 = _wall_band_range(r, 0.014, 0.010)
    if z1 <= z0 + 0.012:
        return tub
    pitch = max(r.wire_pitch_m, 0.018)
    wire_d = 2.0 * r.wire_radius_m
    hx, hy = _profile_half_spans(_profile_at(r, 0.5 * (z0 + z1)))
    reach = 3.0 * max(hx, hy)

    # The openings between the wires are punched as two compound hole grids --
    # one through the long walls, one through the short walls -- so the whole
    # pattern costs two booleans. Building the wires themselves by unioning
    # dozens of overlapping bars instead took ~100 s per build.
    def _grid(span_a: float, count_a: int, count_z: int):
        pts = []
        for i in range(count_a):
            a = -span_a + 2.0 * span_a * (i + 0.5) / count_a
            for k in range(count_z):
                z = z0 + (z1 - z0) * (k + 0.5) / count_z
                pts.append((a, z))
        return pts

    hole_h = max(0.005, pitch - wire_d)
    n_z = max(2, min(5, int((z1 - z0) / pitch)))
    n_x = max(2, min(7, int(2.0 * hx * 0.86 / pitch)))
    n_y = max(2, min(5, int(2.0 * hy * 0.86 / pitch)))
    hole_w_x = max(0.005, (2.0 * hx * 0.86) / n_x - wire_d)
    hole_w_y = max(0.005, (2.0 * hy * 0.86) / n_y - wire_d)

    through_y = (
        cq.Workplane("XZ")
        .pushPoints(_grid(hx * 0.86, n_x, n_z))
        .box(hole_w_x, hole_h, reach, combine=False)
    )
    through_x = (
        cq.Workplane("YZ")
        .pushPoints(_grid(hy * 0.86, n_y, n_z))
        .box(hole_w_y, hole_h, reach, combine=False)
    )
    # Both grids go into one boolean: two sequential cuts each re-traverse the
    # whole tub solid and cost roughly twice as much.
    return tub.cut(through_y.add(through_x))


def _wall_style_solid_smooth_build(r: ResolvedShoppingBucketConfig, tub):
    """Closed wall with optional shallow stiffening ribs (source ..._77eca573)."""
    if r.rib_count <= 0:
        return tub
    z0, z1 = _wall_band_range(r, 0.018, 0.014)
    if z1 <= z0 + 0.010:
        return tub
    band_h = min(0.008, (z1 - z0) / (r.rib_count + 2))
    ribs = None
    for i in range(r.rib_count):
        z = z0 + (z1 - z0) * (i + 1) / (r.rib_count + 1)
        rib = _prism(_profile_at(r, z, offset=0.0016), z, band_h)
        bore = _prism(_profile_at(r, z, offset=-0.001), z - 0.001, band_h + 0.002)
        band = rib.cut(bore)
        ribs = band if ribs is None else ribs.union(band)
    return tub.union(ribs)


def _wall_style_horizontal_slot_grid_build(r: ResolvedShoppingBucketConfig, tub):
    """Wide short slots on a brick pitch (source ..._b050efd5).

    That source lays its walls out with ``SlotPatternPanelGeometry`` -- slot
    70x8 mm on a 90x20 mm pitch with an optional row stagger. Here the same
    pattern is punched through the lofted shell so it follows every plan; the
    whole grid is one boolean, as for the wire mesh.
    """
    z0, z1 = _wall_band_range(r, 0.016, 0.012)
    if z1 <= z0 + 0.012:
        return tub
    hx, hy = _profile_half_spans(_profile_at(r, 0.5 * (z0 + z1)))
    reach = 3.0 * max(hx, hy)
    rows = max(2, r.slot_rows)
    slot_h = max(0.005, min(0.012, (z1 - z0) / (rows * 2.0)))
    cols_x = max(2, min(4, int(2.0 * hx * r.slot_row_span_ratio / 0.090)))
    cols_y = max(1, min(3, int(2.0 * hy * r.slot_row_span_ratio / 0.090)))

    def _rows(span_a: float, count_a: int):
        pts = []
        for k in range(rows):
            z = z0 + (z1 - z0) * (k + 0.5) / rows
            shift = 0.5 if (r.slot_row_stagger and k % 2) else 0.0
            for i in range(count_a):
                a = -span_a + 2.0 * span_a * (i + 0.5 + shift) / count_a
                if abs(a) > span_a:
                    continue
                pts.append((a, z))
        return pts

    slot_w_x = max(0.010, (2.0 * hx * r.slot_row_span_ratio) / cols_x - 0.014)
    slot_w_y = max(0.010, (2.0 * hy * r.slot_row_span_ratio) / cols_y - 0.014)
    through_y = (
        cq.Workplane("XZ")
        .pushPoints(_rows(hx * r.slot_row_span_ratio, cols_x))
        .box(slot_w_x, slot_h, reach, combine=False)
    )
    through_x = (
        cq.Workplane("YZ")
        .pushPoints(_rows(hy * r.slot_row_span_ratio, cols_y))
        .box(slot_w_y, slot_h, reach, combine=False)
    )
    return tub.cut(through_y.add(through_x))


def _wall_style_diagonal_lattice_build(r: ResolvedShoppingBucketConfig, tub):
    """X-pattern lattice (source ..._50948264 ``_build_lattice_wall``).

    The source unions +45/-45 degree bars into a panel; punching the diamond
    openings out of the shell instead leaves the same crossing-bar lattice and
    costs one boolean rather than a union per bar.
    """
    z0, z1 = _wall_band_range(r, 0.016, 0.012)
    if z1 <= z0 + 0.014:
        return tub
    hx, hy = _profile_half_spans(_profile_at(r, 0.5 * (z0 + z1)))
    reach = 3.0 * max(hx, hy)
    pitch = max(0.024, r.lattice_pitch_m)
    diag = max(0.008, pitch - r.lattice_bar_m)

    def _diamonds(span_a: float):
        pts = []
        # Capped: the diamond grid is one boolean but a dense compound still
        # costs seconds on curved plans, and the per-build budget is 12 s.
        n_a = max(2, min(6, int(2.0 * span_a * 0.86 / pitch)))
        n_z = max(2, min(4, int((z1 - z0) / pitch)))
        for k in range(n_z):
            z = z0 + (z1 - z0) * (k + 0.5) / n_z
            shift = 0.5 if k % 2 else 0.0
            for i in range(n_a):
                a = -span_a * 0.86 + 2.0 * span_a * 0.86 * (i + 0.5 + shift) / n_a
                if abs(a) > span_a * 0.86:
                    continue
                pts.append((a, z))
        return pts

    # Diamonds: rotate the hole grid 45 degrees WITHIN the wall plane, by
    # pushing points expressed in that rotated frame. Rotating the finished
    # compound about the global Y axis instead moves every hole out of the wall --
    # one of them landed on the floor and cut a fragment loose.
    k = math.sqrt(0.5)

    def _rotated(pts):
        return [(a * k + z * k, -a * k + z * k) for a, z in pts]

    side = diag * 0.72
    through_y = (
        cq.Workplane("XZ")
        .transformed(rotate=(0.0, 0.0, 45.0))
        .pushPoints(_rotated(_diamonds(hx)))
        .box(side, side, reach, combine=False)
    )
    through_x = (
        cq.Workplane("YZ")
        .transformed(rotate=(0.0, 0.0, 45.0))
        .pushPoints(_rotated(_diamonds(hy)))
        .box(side, side, reach, combine=False)
    )
    return tub.cut(through_y.add(through_x))


WALL_STYLE_BUILDERS = {
    "slotted_perforated": _wall_style_slotted_perforated_build,
    "steel_wire_mesh": _wall_style_steel_wire_mesh_build,
    "horizontal_slot_grid": _wall_style_horizontal_slot_grid_build,
    "diagonal_lattice": _wall_style_diagonal_lattice_build,
    "solid_smooth": _wall_style_solid_smooth_build,
}


# ===========================================================================
# Mouth hardware cut into the tub (bosses / grips / front opening)
# ===========================================================================
def _bail_axle_r(r: ResolvedShoppingBucketConfig) -> float:
    """Pivot pin radius. Fat enough that the pin itself bridges the rim crest,
    which is what lets the bail hang off the rim with no post under it."""
    return r.bail_bar_radius_m * 0.80


def _pivot_axle_z(r: ResolvedShoppingBucketConfig) -> float:
    """Bail pivot height: the pin sits ON the rim edge, sunk 1 mm into the crest.

    It still has to clear the rim, because a folding bail sweeps its arch through
    the pivot plane -- but the pin's own radius provides that clearance, so no
    boss or post is needed. At the 90-degree fold limit the bar's underside comes
    back down to roughly the crest, which is exactly how a bail rests on a rim.
    """
    return r.body_height_m + _bail_axle_r(r) - 0.001


def _bail_half_span(r: ResolvedShoppingBucketConfig) -> float:
    """Half-distance between the two bail knuckles (central bail).

    The feet sit OUTBOARD of the wall on their bosses, so a folded bail hangs
    down the outside of the basket instead of through the wall.
    """
    hx, _hy = _profile_half_spans(_profile_at(r, r.body_height_m, offset=r.rim_lip_m))
    return hx + r.bail_bar_radius_m * 2.2


def _side_bail_half_span(r: ResolvedShoppingBucketConfig) -> float:
    """Half-distance between one side bail's knuckles, measured along Y."""
    _hx, hy = _profile_half_spans(_profile_at(r, r.body_height_m, offset=r.rim_lip_m))
    return hy * 0.55


def _pivot_point(r: ResolvedShoppingBucketConfig):
    """Centre of the central bail's axle line: the joint origin must lie ON the
    axis, and the bail mesh carries its knuckles symmetrically about its own
    origin, so the mid-point is the only consistent choice."""
    return (0.0, 0.0, _pivot_axle_z(r))


def _side_pivot_point(r: ResolvedShoppingBucketConfig, sx: float):
    """Side-bail axle centre on the +/-X short wall.

    Source ..._35468439 hangs its two folding bails off the short ends about Y
    axes, so each bail's knuckles spread along Y and its axle centre sits at the
    short wall.
    """
    rim_pts = _profile_at(r, r.body_height_m, offset=r.rim_lip_m)
    span = _side_bail_half_span(r)
    px = min(_profile_x_at_y(rim_pts, span), _profile_x_at_y(rim_pts, 0.0)) - 0.004
    return (sx * px, 0.0, _pivot_axle_z(r))


def _add_pivot_bosses(r: ResolvedShoppingBucketConfig, tub):
    """Raised bosses carrying the bail axle, plus the axle stub itself.

    The bail knuckle is a bore of ``axle_radius + clearance`` around this stub,
    so the pivot is captured by a running fit -- there is nothing interpenetrating
    that would need an overlap allowance.
    """
    axle_r = _bail_axle_r(r)
    pz = _pivot_axle_z(r)
    hx, hy = _profile_half_spans(_profile_at(r, r.body_height_m, offset=r.rim_lip_m))

    if r.top_configuration == "open_bail_dual_fold":
        span = _side_bail_half_span(r)
        rim_pts = _profile_at(r, r.body_height_m, offset=r.rim_lip_m)
        for sx in (-1.0, 1.0):
            # Sit the pin where the rim actually is across the bail's own span,
            # so it is embedded in the crest along its whole length.
            px = sx * (min(_profile_x_at_y(rim_pts, span), _profile_x_at_y(rim_pts, 0.0)) - 0.004)
            stub = (
                cq.Workplane("XZ", origin=(px, span + 0.016, pz))
                .circle(axle_r)
                .extrude(2.0 * (span + 0.016))
            )
            tub = tub.union(stub)
        return tub

    span = _bail_half_span(r)
    for sx in (-1.0, 1.0):
        # The pin starts inside the rim band and runs out to the bail knuckle.
        stub = (
            cq.Workplane("YZ", origin=(sx * (hx - 0.004), 0.0, pz))
            .circle(axle_r)
            .extrude(sx * (span - hx + 0.022))
        )
        tub = tub.union(stub)
    return tub


def _norm(value: float, low: float, high: float) -> float:
    """Position of ``value`` inside its declared range, as 0..1."""
    if high <= low:
        return 0.0
    return _clamp((value - low) / (high - low), 0.0, 1.0)


def _grip_cutout_dims(r: ResolvedShoppingBucketConfig):
    """``(centre_z, width, height, corner_radius)`` of one molded grip opening.

    Source ..._ab5a00e2 cuts ``GRIP_W`` 0.110 into a ``BODY_Y`` 0.340 short wall
    (0.32 of the wall run) at ``GRIP_H/GRIP_W`` = 0.41, with ``GRIP_R`` 0.018
    rounded corners. Those are RATIOS of that source's own basket, and its basket
    is much bigger than this template's (0.340 deep, 0.560 tall against 0.200-0.300
    and 0.170-0.290 here). Taking the source's absolute 85-130 mm opening instead
    put 36-58% of the short-wall run through the wall, and on the four curved plans
    that spans up to 68 degrees of arc, which reads as a missing wall panel rather
    than a hand grip.

    So the opening is derived from the wall run AT ITS OWN HEIGHT -- which is where
    the taper has already narrowed the plan -- and the declared parameters move it
    inside that band, keeping both of them geometrically live over their full range.
    """
    t_w = _norm(r.grip_cutout_w_m, 0.085, 0.130)
    t_h = _norm(r.grip_cutout_h_m, 0.032, 0.055)
    rim_band_bottom = r.body_height_m - 2.4 * r.rim_lip_m
    # Width follows the wall run at the opening's own height, and the height then
    # follows the width, so both need the centre height that they in turn set.
    # Two passes settle it: pass one uses a nominal band, pass two the real one.
    centre = rim_band_bottom - 0.030
    width = height = 0.0
    for _ in range(2):
        hy = _profile_half_spans(_profile_at(r, centre))[1]
        width = 2.0 * hy * (0.30 + 0.10 * t_w)
        height = width * (0.40 + 0.12 * t_h)
        # Keep a readable strip of wall between the rolled rim and the opening.
        centre = rim_band_bottom - max(0.014, 0.5 * height) - 0.5 * height
    return centre, width, height, min(0.018, 0.32 * min(width, height))


def _wall_shell_ring(r: ResolvedShoppingBucketConfig, z0: float, z1: float):
    """The wall itself between two heights, as a solid band.

    Lofted rather than prismatic: over a 30-40 mm tall band the taper moves the
    wall by more than its own thickness, so a straight prism ring built at the mid
    height misses the wall at both ends of the band.
    """
    outer = _loft_between(
        _profile_at(r, z0, offset=0.004), z0, _profile_at(r, z1, offset=0.004), z1
    )
    bore = _loft_between(
        _profile_at(r, z0, offset=-r.wall_thickness_m - 0.0006),
        z0 - 0.002,
        _profile_at(r, z1, offset=-r.wall_thickness_m - 0.0006),
        z1 + 0.002,
    )
    return outer.cut(bore)


def _add_grip_cutouts(r: ResolvedShoppingBucketConfig, tub):
    """Hand-hold cutouts through the two short walls -- the carry hardware of
    every closed-top configuration (source ..._ab5a00e2 uses these in place of a
    bail).

    The source frames each cutout with a raised surround, but that surround is a
    flat plate and this template's walls are curved on four of six plans, so it
    stood off the wall as a rectangular picture frame. The rounded opening alone
    reads correctly on every plan.

    The cutter is masked by the wall band, so the opening is a slot THROUGH THE
    SHELL. Extruding a bare 60 mm prism inward instead also scooped out whatever
    stood behind the wall: on a divided basket it took the top corners off both
    ends of the central divider.
    """
    grip_z, width, height, corner_r = _grip_cutout_dims(r)
    z0 = grip_z - 0.5 * height
    z1 = grip_z + 0.5 * height

    # Reach from just outside the rim lip to just inside the cavity wall at the
    # opening's own y extent -- the wall falls away from the cutter plane both
    # with the taper and, on a curved plan, with the arc.
    x_hi = _profile_half_spans(_profile_at(r, z1, offset=r.rim_lip_m))[0] + 0.005
    x_lo = _profile_x_at_y(_profile_at(r, z0, offset=-r.wall_thickness_m), 0.5 * width) - 0.005
    # Never let a cutter cross the centreline and reach the opposite wall.
    x_lo = max(x_lo, 0.30 * x_hi)
    depth = x_hi - x_lo

    cutters = None
    for sx in (-1.0, 1.0):
        slot = (
            cq.Workplane("YZ", origin=(sx * x_lo, 0.0, grip_z))
            .rect(width, height)
            .extrude(sx * depth)
            .edges("|X")
            .fillet(corner_r)
        )
        cutters = slot if cutters is None else cutters.union(slot)
    return tub.cut(cutters.intersect(_wall_shell_ring(r, z0, z1)))


def _lid_hinge_y(r: ResolvedShoppingBucketConfig) -> float:
    """Y of the lid hinge line, one knuckle radius inboard of the rim edge.

    The panel mesh and the joint origin BOTH read this. Deriving them separately
    (rim edge for one, rim edge minus the knuckle for the other) shifted each
    clamshell leaf inboard by the knuckle radius, so the two leaves overlapped by
    exactly one knuckle diameter on the centreline.
    """
    # Put the axle exactly on the lid's own outboard edge. Setting it one knuckle
    # radius further inboard let the panel overhang the hinge by that much, and
    # the overhang then sat on the axle and the tub lugs.
    return _profile_half_spans(_lid_outline(r))[1]


def _lid_lug_x(r: ResolvedShoppingBucketConfig) -> float:
    """X of the tub-side hinge lugs. The lid notches out exactly these positions,
    the way real hinge knuckles interleave -- a lug that simply rose past the rim
    would stand in the lid panel."""
    pts = _profile_at(r, r.body_height_m, offset=r.rim_lip_m)
    hx, hy = _profile_half_spans(pts)
    # Take the outermost x whose rim edge is still close to the hinge line. On a
    # hexagon or ellipse the wall falls away fast, and a lug bridging that gap
    # would be a solid bar reaching across the mouth for the lid to land on.
    for frac in (0.80, 0.70, 0.60, 0.50, 0.40):
        x = hx * frac
        if hy - _profile_y_at_x(pts, x) <= 0.006:
            return x
    return hx * 0.35


_LID_LUG_R = _HINGE_KNUCKLE_R * 0.9
_LID_NOTCH_CLEAR = 0.0007


def _lid_panel_drop(r: ResolvedShoppingBucketConfig) -> float:
    """Vertical offset from the hinge axle down to the panel mid-plane.

    The knuckle has to clear the rim crest, so the axle rides above it; the panel
    then hangs back down onto the rim. Putting the axle at rim height instead
    buried the lower half of every knuckle in the rolled rim.
    """
    return _HINGE_KNUCKLE_R + 0.003


def _lid_hinge_z(r: ResolvedShoppingBucketConfig) -> float:
    thickness = r.leaf_thickness_m if r.top_configuration == "lid_clamshell" else r.lid_thickness_m
    return r.body_height_m + _lid_panel_drop(r) + thickness * 0.5


def _lid_hinge_axle_point(r: ResolvedShoppingBucketConfig):
    """Hinge line on the +Y rim edge, taken from the rim profile itself."""
    return (0.0, _lid_hinge_y(r), _lid_hinge_z(r))


def _add_lid_hinge_axles(r: ResolvedShoppingBucketConfig, tub):
    """Rim-edge hinge axles the lid/leaf knuckles run on."""
    # Reach past the lugs: an axle that stopped at the knuckle span never touched
    # the lugs meant to carry it and floated inside basket_tub.
    span = _lid_lug_x(r) + _LID_LUG_R
    signs = (1.0, -1.0) if r.top_configuration == "lid_clamshell" else (1.0,)
    hinge_z = _lid_hinge_z(r)
    for sy in signs:
        hinge_y = sy * _lid_hinge_y(r)
        axle = (
            cq.Workplane("YZ", origin=(-span, hinge_y, hinge_z))
            .circle(_HINGE_AXLE_R)
            .extrude(2.0 * span)
        )
        tub = tub.union(axle)
        # Standing lugs from the rim crest up to the axle. The axle rides above
        # the rim so the knuckles clear it, which leaves it floating in mid-air
        # unless something carries it -- the compiler reports exactly that as a
        # disconnected geometry island inside basket_tub.
        rim_pts = _profile_at(r, r.body_height_m, offset=r.rim_lip_m)
        for sx in (-1.0, 1.0):
            lug_x = sx * _lid_lug_x(r)
            wall_y = sy * _profile_y_at_x(rim_pts, lug_x)
            y_lo, y_hi = sorted((wall_y, hinge_y))
            lug = (
                cq.Workplane("XY", origin=(lug_x, 0.5 * (y_lo + y_hi), r.body_height_m - 0.006))
                .rect(2.0 * _LID_LUG_R, max(2.0 * _LID_LUG_R, y_hi - y_lo))
                .extrude(hinge_z - (r.body_height_m - 0.006))
            )
            tub = tub.union(lug)
    return tub


# ===========================================================================
# secondary_storage host features cut into / added to the tub
# ===========================================================================
_CADDY_CLEAR_MARGIN = 0.008  # gap kept between the raised tray and mouth hardware


def _mouth_clear_ceiling(r: ResolvedShoppingBucketConfig) -> float:
    """Lowest z of any sibling hardware spanning the mouth.

    The bail rests over the mouth on its raised bosses; a closed lid seats on the
    rim. Whichever is lower bounds how far the inner tray may rise.
    """
    if r.has_bail:
        return _pivot_axle_z(r) - r.bail_bar_radius_m
    return r.body_height_m - 0.002


def _caddy_dims(r: ResolvedShoppingBucketConfig):
    """(half_x, half_y, height, seat_z, rib_top, lift) for the inner caddy."""
    floor_pts = _profile_at(r, r.floor_top_z, offset=-r.wall_thickness_m)
    hx, hy = _profile_half_spans(floor_pts)
    cx = hx * r.caddy_plan_ratio
    # A rectangle sized from the widest x and y overflows a hexagonal or oval
    # cavity at its corners. Inscribe it: cap the half-depth by the polygon's own
    # y at the tray's x extent.
    cy = min(hy * r.caddy_plan_ratio, _profile_y_at_x(floor_pts, cx) - 0.004)
    cy = max(cy, hy * 0.30)
    height = r.body_height_m * r.caddy_height_ratio
    seat = r.floor_top_z
    # Ribs may run up to just under the rim; the lid, when present, sits above it.
    rib_top = r.body_height_m - 2.4 * r.rim_lip_m - 0.008
    # The tray is a sibling of the mouth hardware, so QC poses a raised tray
    # against a resting bail. Derive a ceiling from whatever hangs lowest over
    # the mouth, or the tray drives straight through the bail.
    ceiling = _mouth_clear_ceiling(r)
    guided = rib_top - seat - _CADDY_GUIDE_ENGAGE
    headroom = ceiling - _CADDY_CLEAR_MARGIN - seat - height
    lift = max(0.006, min(guided, headroom))
    return cx, cy, height, seat, rib_top, lift


def _add_caddy_guide_ribs(r: ResolvedShoppingBucketConfig, tub):
    """Vertical guide ribs straddling the caddy's long walls.

    The tub wall tapers outward with height while these stay vertical, so the
    rib-to-tray gap is constant over the whole lift: the tray is supported at
    every pose instead of floating free the moment it leaves the floor.
    """
    cx, cy, _h, _seat, rib_top, _lift = _caddy_dims(r)
    floor_pts = _profile_at(r, r.floor_top_z, offset=-r.wall_thickness_m)
    y_in = cy + _CADDY_GUIDE_CLEAR
    for sx in (-1.0, 1.0):
        rib_x = sx * cx * 0.55
        # Reach out to the cavity wall AT THIS x, not to the widest point: on a
        # curved plan a rib sized to the centre span stands outside the shell.
        y_out = min(y_in + 0.012, _profile_y_at_x(floor_pts, rib_x) - 0.0005)
        if y_out <= y_in + 0.002:
            continue
        for sy in (-1.0, 1.0):
            rib = cq.Workplane("XY", origin=(rib_x, sy * 0.5 * (y_in + y_out), 0.0)).box(
                _CADDY_GUIDE_T, y_out - y_in, rib_top, centered=(True, True, False)
            )
            tub = tub.union(rib)
    return tub


def _add_divider(r: ResolvedShoppingBucketConfig, tub):
    """Fused central divider wall (source ..._31a4dbd5)."""
    height = (r.body_height_m - r.floor_top_z) * r.divider_height_ratio
    hx = _profile_half_spans(_profile_at(r, r.floor_top_z, offset=-r.wall_thickness_m))[0]
    wall = (
        cq.Workplane("XY")
        .box(2.0 * hx * 0.98, r.divider_thickness_m, height, centered=(True, True, False))
        .translate((0.0, 0.0, r.floor_top_z))
    )
    keep = _loft_between(
        _profile_at(r, r.floor_top_z, offset=-r.wall_thickness_m),
        r.floor_top_z,
        _profile_at(r, r.body_height_m, offset=-r.wall_thickness_m),
        r.body_height_m,
    )
    return tub.union(wall.intersect(keep))


# ===========================================================================
# Tub assembly
# ===========================================================================
def _tub_mesh(r: ResolvedShoppingBucketConfig, assets):
    tub = _body_form_build(r)
    tub = WALL_STYLE_BUILDERS[r.wall_style](r, tub)

    if r.has_bail:
        tub = _add_pivot_bosses(r, tub)
    if r.has_closed_top:
        tub = _add_grip_cutouts(r, tub)
        tub = _add_lid_hinge_axles(r, tub)

    if r.secondary_storage == "two_compartment_divider":
        tub = _add_divider(r, tub)
    elif r.secondary_storage == "removable_inner_caddy":
        tub = _add_caddy_guide_ribs(r, tub)

    # No bottom fillet: on hexagonal / slotted plans OCC returns sliver faces at
    # the floor that the compiler reports as disconnected geometry islands.
    return mesh_from_cadquery(tub, "basket_tub", assets=assets)


# ===========================================================================
# top_configuration candidates: carry hardware and closure
# ===========================================================================
def _bail_bar_mesh(r: ResolvedShoppingBucketConfig, assets, *, name: str, span: float, rise: float):
    """Bail arch authored with its pivot line through the LOCAL ORIGIN.

    ``register_interface_mate`` rejects a rotational joint whose axis misses the
    child-frame origin, and a bail really does turn about the axle running
    through its two knuckles, so the knuckles sit at z=0 either side of the
    origin. Each knuckle is a sleeve bored to ``bar_radius + clearance`` so it
    runs on the tub axle stub without interpenetrating it.
    """
    bar_r = r.bail_bar_radius_m
    path = cq.Workplane("XZ").moveTo(-span, 0.0).threePointArc((0.0, rise), (span, 0.0))
    wire = path.val()
    start = wire.positionAt(0.0)
    tan = wire.tangentAt(0.0)
    arch = (
        cq.Workplane(cq.Plane(origin=start.toTuple(), normal=tan.toTuple()))
        .circle(bar_r)
        .sweep(path, transition="round")
    )
    bore_r = _bail_axle_r(r) + _BOSS_CLEARANCE
    for sx in (-1.0, 1.0):
        sleeve = (
            cq.Workplane("YZ", origin=(sx * (span - 0.007), 0.0, 0.0))
            .circle(bar_r * 1.55)
            .circle(bore_r)
            .extrude(sx * 0.021)
        )
        arch = arch.union(sleeve)
    # Clear the axle line through the whole bail. The arch feet sit ON the pivot
    # line, so the swept tube itself would otherwise occupy the axle -- the bore
    # in the sleeves alone still leaves the bar solid where it meets the stub.
    arch = arch.cut(
        cq.Workplane("YZ", origin=(-span * 1.3, 0.0, 0.0)).circle(bore_r).extrude(2.6 * span)
    )
    return mesh_from_cadquery(arch, name, assets=assets)


def _side_bail_mesh(
    r: ResolvedShoppingBucketConfig, assets, *, name: str, span: float, rise: float
):
    """One folding side bail, hung off a short wall about a Y axis.

    Its knuckles therefore spread along local Y (not X): the pivot line and the
    knuckles have to be the same line, or the joint turns about an axis the
    hardware does not sit on.
    """
    bar_r = r.bail_bar_radius_m
    path = cq.Workplane("YZ").moveTo(-span, 0.0).threePointArc((0.0, rise), (span, 0.0))
    wire = path.val()
    start = wire.positionAt(0.0)
    tan = wire.tangentAt(0.0)
    arch = (
        cq.Workplane(cq.Plane(origin=start.toTuple(), normal=tan.toTuple()))
        .circle(bar_r)
        .sweep(path, transition="round")
    )
    bore_r = _bail_axle_r(r) + _BOSS_CLEARANCE
    for sy in (-1.0, 1.0):
        sleeve = (
            # "XZ" extrudes along its -Y normal, so negate to grow outboard.
            cq.Workplane("XZ", origin=(0.0, sy * (span - 0.007), 0.0))
            .circle(bar_r * 1.32)
            .circle(bore_r)
            .extrude(-sy * 0.021)
        )
        arch = arch.union(sleeve)
    # Start at +y and extrude along the -Y normal so the bore actually spans the
    # whole bail. Starting at -y put the entire clearance hole on one side and
    # left the bar solid where it sits on the axle.
    arch = arch.cut(
        cq.Workplane("XZ", origin=(0.0, span * 1.3, 0.0)).circle(bore_r).extrude(2.6 * span)
    )
    return mesh_from_cadquery(arch, name, assets=assets)


def _lid_outline(r: ResolvedShoppingBucketConfig):
    """Lid plan = rim profile inset by a running clearance.

    THIS is what keeps a hexagonal mouth under a hexagonal lid. The old template
    emitted a fixed rectangle here regardless of body_form, which is why lids
    overhung the corners of every non-rectangular mouth.
    """
    return _profile_at(r, r.body_height_m, offset=r.rim_lip_m - _LID_RUNNING_CLEAR)


def _lid_panel_mesh(r: ResolvedShoppingBucketConfig, assets, *, name: str, half: int = 0):
    """Lid panel authored with its hinge line through the LOCAL ORIGIN.

    ``half`` selects a clamshell leaf: +1 keeps the +Y side of the outline, -1 the
    -Y side, so the two leaves are cut from the same rim profile and meet on the
    centreline.
    """
    pts = _lid_outline(r)
    hinge_y = _lid_hinge_y(r)
    thickness = r.lid_thickness_m if half == 0 else r.leaf_thickness_m
    panel = _profile_wire(pts).extrude(thickness).translate((0.0, 0.0, -thickness * 0.5))
    if half != 0:
        # Split on the long axis; each leaf hinges on its own rim edge.
        keep = (
            cq.Workplane("XY")
            .box(4.0 * hinge_y, 2.0 * hinge_y, 4.0 * thickness, centered=(True, False, True))
            .rotate((0, 0, 0), (0, 0, 1), 0.0 if half > 0 else 180.0)
        )
        panel = panel.intersect(keep)
    # Move the panel into the hinge frame: hinge at the local origin, panel
    # reaching away from it.
    panel = panel.translate((0.0, -half_sign(half) * hinge_y, -_lid_panel_drop(r)))

    # Hinge knuckles centred on the local origin axis.
    drop = _lid_panel_drop(r)
    panel_half_t = thickness * 0.5
    # Park each bracket immediately inboard of its tub lug, just clear of the
    # notch. The two faces then keep a sub-millimetre AXIAL gap at every swing
    # angle -- unlike the bore/axle radial fit, whose tessellated gap reads as
    # ~2.3 mm once faceted and left the opened leaf looking detached.
    bracket_outer = _lid_lug_x(r) - (_LID_LUG_R + _LID_NOTCH_CLEAR)
    # Interleave: clear the tub lugs out of the panel at the hinge edge.
    notch_w = 2.0 * (_LID_LUG_R + _LID_NOTCH_CLEAR)
    for sx in (-1.0, 1.0):
        notch = (
            cq.Workplane("XY", origin=(sx * _lid_lug_x(r), 0.0, -drop - 0.02))
            .rect(notch_w, 2.0 * (_LID_LUG_R + _LID_NOTCH_CLEAR))
            .extrude(0.08)
        )
        panel = panel.cut(notch)
    for sx in (-1.0, 1.0):
        # One solid bracket from the axle line down onto the panel, bored for the
        # axle afterwards. It has to reach the panel EDGE, which on an oval or
        # hexagonal plan sits well inboard of the hinge line at this x -- a
        # bracket sized to the hinge alone hangs off the leaf entirely.
        bx = sx * (bracket_outer - 0.009)
        # The leaf extends away from its hinge in -local-y for half>=0 and +y for
        # the mirrored leaf, so the bracket has to run that way to land on it.
        reach_sign = -half_sign(half)
        edge_depth = max(0.008, hinge_y - _profile_y_at_x(pts, bx))
        y_edge = reach_sign * (edge_depth + 0.005)
        y_lo = min(y_edge, -_HINGE_KNUCKLE_R)
        y_hi = max(y_edge, _HINGE_KNUCKLE_R)
        bracket = (
            cq.Workplane(
                "XY",
                origin=(
                    (bracket_outer - 0.018) if sx > 0 else -bracket_outer,
                    0.5 * (y_lo + y_hi),
                    -drop - panel_half_t,
                ),
            )
            .rect(0.018, y_hi - y_lo, centered=(False, True))
            .extrude(drop + panel_half_t + _HINGE_KNUCKLE_R)
        )
        panel = panel.union(bracket)
    # Clear the axle line through the WHOLE leaf. The knuckles are bored, but the
    # straps that carry them down to the dropped panel sit right on the axle, so
    # the tub-side axle ended up buried inside the lid between the knuckles.
    hx_full = _profile_half_spans(_profile_at(r, r.body_height_m, offset=r.rim_lip_m))[0]
    panel = panel.cut(
        cq.Workplane("YZ", origin=(-hx_full * 1.3, 0.0, 0.0))
        .circle(_HINGE_AXLE_R + _HINGE_BORE_CLEAR)
        .extrude(2.6 * hx_full)
    )
    return mesh_from_cadquery(panel, name, assets=assets)


def half_sign(half: int) -> float:
    """+1 for a single lid or the +Y leaf, -1 for the -Y leaf."""
    return 1.0 if half >= 0 else -1.0


# ===========================================================================
# secondary_storage moving parts
# ===========================================================================
def _caddy_mesh(r: ResolvedShoppingBucketConfig, assets):
    cx, cy, height, _seat, _rib_top, _lift = _caddy_dims(r)
    wall = 0.005
    outer = (
        cq.Workplane("XY")
        .box(2.0 * cx, 2.0 * cy, height, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(0.010, 0.4 * cy))
    )
    tray = outer.faces(">Z").shell(-wall)
    return mesh_from_cadquery(tray, "inner_caddy", assets=assets)


# ===========================================================================
# Axis-mated joint helper: every rotational joint is registered for QC
# ===========================================================================
def _axis_joint(
    model,
    *,
    name,
    parent,
    child,
    point,
    axis,
    radial,
    limits,
    articulation_type=ArticulationType.REVOLUTE,
):
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(
        name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=radial
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=0.08, friction=0.05),
    )
    register_interface_mate(model, name, mate)


# ===========================================================================
# Build
# ===========================================================================
_PALETTES = {
    "red_plastic": ((0.86, 0.24, 0.20, 1.0), (0.52, 0.12, 0.10, 1.0)),
    "blue_plastic": ((0.20, 0.34, 0.78, 1.0), (0.12, 0.18, 0.42, 1.0)),
    "galvanized_steel": ((0.72, 0.74, 0.77, 1.0), (0.44, 0.46, 0.50, 1.0)),
    "charcoal": ((0.28, 0.29, 0.31, 1.0), (0.16, 0.17, 0.18, 1.0)),
}


def _emit_top_configuration(model, r, tub, *, assets, mats) -> list[str]:
    """Emit the mouth mechanism: carry hardware plus any closure."""
    names: list[str] = []
    top = r.top_configuration

    if top in ("open_bail_fixed_arch", "open_bail_swing"):
        hx = _bail_half_span(r)
        rise = r.bail_rise_m
        bail = model.part("carry_bail")
        bail.visual(
            _bail_bar_mesh(r, assets, name="carry_bail", span=hx, rise=rise),
            material=mats["hardware"],
            name="bail_bar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_plastic", "blue_plastic", "charcoal"} else "metal.steel_galvanized"),
        )
        bail.meta = {"role": "carry_bail"}
        bail.inertial = Inertial.from_geometry(
            Box((2.0 * hx, 2.0 * r.bail_bar_radius_m, rise)),
            mass=0.12,
            origin=Origin(xyz=(0.0, 0.0, rise * 0.45)),
        )
        limit = r.bail_swing_rad
        _axis_joint(
            model,
            name="tub_to_bail",
            parent=tub,
            child=bail,
            point=_pivot_point(r),
            axis=(1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            limits=MotionLimits(effort=4.0, velocity=2.5, lower=-limit, upper=limit),
        )
        names.append("carry_bail")

    elif top == "open_bail_dual_fold":
        span = _side_bail_half_span(r)
        for k, sx in ((0, 1.0), (1, -1.0)):
            bail = model.part(f"carry_bail_{k}")
            bail.visual(
                _side_bail_mesh(
                    r, assets, name=f"side_bail_{k}", span=span, rise=r.side_bail_rise_m
                ),
                material=mats["hardware"],
                name=f"side_bail_{k}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_plastic", "blue_plastic", "charcoal"} else "metal.steel_galvanized"),
            )
            bail.meta = {"role": "carry_bail"}
            bail.inertial = Inertial.from_geometry(
                Box((2.0 * r.bail_bar_radius_m, 2.0 * span, r.side_bail_rise_m)),
                mass=0.08,
                origin=Origin(xyz=(0.0, 0.0, r.side_bail_rise_m * 0.45)),
            )
            _axis_joint(
                model,
                name=f"tub_to_bail_{k}",
                parent=tub,
                child=bail,
                point=_side_pivot_point(r, sx),
                # Mirrored axis with a one-sided range, as source ..._35468439
                # does: each bail folds outward over its OWN end. A symmetric
                # range let both swing inward and meet over the mouth.
                axis=(0.0, sx, 0.0),
                radial=(0.0, 0.0, 1.0),
                limits=MotionLimits(effort=4.0, velocity=2.5, lower=0.0, upper=r.bail_swing_rad),
            )
            names.append(f"carry_bail_{k}")

    if top == "lid_hinged_top":
        lid = model.part("top_lid")
        lid.visual(
            _lid_panel_mesh(r, assets, name="lid_panel", half=0),
            material=mats["accent"],
            name="lid_panel", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_plastic", "blue_plastic", "charcoal"} else "metal.steel_galvanized"),
        )
        lid.meta = {"role": "top_lid"}
        lid.inertial = Inertial.from_geometry(
            Box((r.mouth_len_m, r.mouth_depth_m, r.lid_thickness_m)),
            mass=0.28,
            origin=Origin(xyz=(0.0, -r.mouth_depth_m * 0.4, 0.0)),
        )
        _axis_joint(
            model,
            name="tub_to_lid",
            parent=tub,
            child=lid,
            point=_lid_hinge_axle_point(r),
            axis=(-1.0, 0.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.lid_open_rad),
        )
        names.append("top_lid")

    elif top == "lid_clamshell":
        for k, sy in ((0, 1.0), (1, -1.0)):
            leaf = model.part(f"top_lid_{k}")
            leaf.visual(
                _lid_panel_mesh(r, assets, name=f"clamshell_leaf_{k}", half=1 if sy > 0 else -1),
                material=mats["accent"],
                name=f"clamshell_leaf_{k}", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_plastic", "blue_plastic", "charcoal"} else "metal.steel_galvanized"),
            )
            leaf.meta = {"role": "top_lid"}
            leaf.inertial = Inertial.from_geometry(
                Box((r.mouth_len_m, r.mouth_depth_m * 0.5, r.leaf_thickness_m)),
                mass=0.14,
                origin=Origin(xyz=(0.0, -sy * r.mouth_depth_m * 0.2, 0.0)),
            )
            _axis_joint(
                model,
                name=f"tub_to_lid_{k}",
                parent=tub,
                child=leaf,
                point=(0.0, sy * _lid_hinge_y(r), _lid_hinge_z(r)),
                # The leaf reaches away from its own rim edge, so the lifting
                # sense is the OPPOSITE X sign: a leaf hinged on +Y that covers
                # -Y rises about -X. With axis=(sy,...) both leaves swung down
                # into the tub instead of opening.
                axis=(-sy, 0.0, 0.0),
                radial=(0.0, 0.0, 1.0),
                limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.leaf_open_rad),
            )
            names.append(f"top_lid_{k}")

    return names


def _emit_secondary_storage(model, r, tub, *, assets, mats) -> list[str]:
    if r.secondary_storage == "removable_inner_caddy":
        _cx, _cy, height, seat, _rib_top, lift = _caddy_dims(r)
        caddy = model.part("inner_caddy")
        caddy.visual(_caddy_mesh(r, assets), material=mats["accent"], name="caddy_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_plastic", "blue_plastic", "charcoal"} else "metal.steel_galvanized"))
        caddy.meta = {"role": "inner_caddy"}
        cx, cy, _h, _s, _rt, _l = _caddy_dims(r)
        caddy.inertial = Inertial.from_geometry(
            Box((2.0 * cx, 2.0 * cy, height)),
            mass=0.12,
            origin=Origin(xyz=(0.0, 0.0, height * 0.5)),
        )
        model.articulation(
            "tub_to_caddy",
            ArticulationType.PRISMATIC,
            parent=tub,
            child=caddy,
            origin=Origin(xyz=(0.0, 0.0, seat)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=1.0, lower=0.0, upper=lift),
            motion_properties=MotionProperties(damping=0.08, friction=0.05),
        )
        return ["inner_caddy"]

    return []


def build_shopping_bucket(
    config: ShoppingBucketConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name)
    body_rgba, hardware_rgba = _PALETTES[r.palette_style]
    mats = {
        "body": model.material("body_finish", rgba=body_rgba),
        "hardware": model.material("hardware_finish", rgba=hardware_rgba),
        "accent": model.material("accent_finish", rgba=body_rgba),
    }

    tub = model.part("basket_tub")
    tub.visual(_tub_mesh(r, assets), material=mats["body"], name="tub_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"red_plastic", "blue_plastic", "charcoal"} else "metal.steel_galvanized"))
    tub.meta = {"role": "basket_tub"}
    tub.inertial = Inertial.from_geometry(
        Box((r.mouth_len_m, r.mouth_depth_m, r.body_height_m)),
        mass=0.9,
        origin=Origin(xyz=(0.0, 0.0, r.body_height_m * 0.45)),
    )

    _emit_top_configuration(model, r, tub, assets=assets, mats=mats)
    _emit_secondary_storage(model, r, tub, assets=assets, mats=mats)

    model.meta = {"slot_choices": slot_choices_for_config(r)}
    return model


# ===========================================================================
# Authored tests
# ===========================================================================
def run_shopping_bucket_tests(
    object_model: ArticulatedObject,
    config: ShoppingBucketConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    tub = object_model.get_part("basket_tub")

    # --- identity: one open tub standing on the floor, long axis in X --------
    aabb = ctx.part_world_aabb(tub)
    ctx.check("basket tub resolves", aabb is not None, details=f"aabb={aabb}")
    if aabb is not None:
        (mn, _mx) = aabb
        ctx.check(
            "category_anchor: basket rests on the floor with an open mouth",
            abs(mn[2]) < 0.02,
            details=f"z_min={mn[2]:.4f}",
        )
    # Long-axis identity is a claim about the mouth plan, so read the profile
    # rather than the part AABB: side-mounted pivot bosses legitimately stick out
    # past the mouth in Y and would otherwise fail a shape that is in fact wider
    # in X.
    rim_hx, rim_hy = _profile_half_spans(_profile_at(r, r.body_height_m))
    ctx.check(
        "mouth plan is wider along X than Y",
        rim_hx > rim_hy,
        details=f"body_form={r.body_form} half_x={rim_hx:.4f} half_y={rim_hy:.4f}",
    )

    # --- the rim profile really drives the lid outline ----------------------
    if r.has_closed_top:
        rim_pts = _profile_at(r, r.body_height_m, offset=r.rim_lip_m)
        lid_pts = _lid_outline(r)
        rim_hx, rim_hy = _profile_half_spans(rim_pts)
        lid_hx, lid_hy = _profile_half_spans(lid_pts)
        ctx.check(
            "category_anchor: lid outline follows the rim profile",
            len(lid_pts) == len(rim_pts)
            and lid_hx <= rim_hx + 1e-9
            and lid_hy <= rim_hy + 1e-9
            and lid_hx > rim_hx - 0.004
            and lid_hy > rim_hy - 0.004,
            details=(
                f"body_form={r.body_form} rim_points={len(rim_pts)} lid_points={len(lid_pts)} "
                f"rim=({rim_hx:.4f},{rim_hy:.4f}) lid=({lid_hx:.4f},{lid_hy:.4f})"
            ),
        )
        # The molded grips are the carry hardware when the mouth is covered.
        part_names = {p.name for p in object_model.parts}
        ctx.check(
            "category_anchor: molded side grips replace the bail on a closed top",
            not any(n.startswith("carry_bail") for n in part_names),
            details=f"parts={sorted(part_names)}",
        )

        lid_joints = (
            ["tub_to_lid_0", "tub_to_lid_1"]
            if r.top_configuration == "lid_clamshell"
            else ["tub_to_lid"]
        )
        for jn in lid_joints:
            joint = object_model.get_articulation(jn)
            lid_part = object_model.get_part(
                joint.child.name if hasattr(joint.child, "name") else str(joint.child)
            )
            hinge_z = float(joint.origin.xyz[2])
            ctx.check(
                f"{jn} is a REVOLUTE hinge about X",
                joint.articulation_type == ArticulationType.REVOLUTE and abs(joint.axis[0]) > 0.99,
                details=f"type={joint.articulation_type} axis={tuple(joint.axis)}",
            )
            with ctx.pose({joint: 0.0}):
                closed = ctx.part_world_aabb(lid_part)
            with ctx.pose({joint: float(joint.motion_limits.upper)}):
                opened = ctx.part_world_aabb(lid_part)
            if closed is not None and opened is not None:
                ctx.check(
                    f"{jn}: free edge swings up when opened",
                    opened[1][2] > closed[1][2] + r.mouth_depth_m * 0.15,
                    details=f"closed_zmax={closed[1][2]:.4f} open_zmax={opened[1][2]:.4f}",
                )
                ctx.check(
                    f"category_anchor: lid hinge edge stays on the rim through the swing ({jn})",
                    opened[0][2] <= hinge_z + 0.03,
                    details=f"open_zmin={opened[0][2]:.4f} hinge_z={hinge_z:.4f}",
                )

    # --- bail configurations -------------------------------------------------
    if r.has_bail:
        bail_names = (
            ["carry_bail_0", "carry_bail_1"]
            if r.top_configuration == "open_bail_dual_fold"
            else ["carry_bail"]
        )
        joint_names = (
            ["tub_to_bail_0", "tub_to_bail_1"]
            if r.top_configuration == "open_bail_dual_fold"
            else ["tub_to_bail"]
        )
        # One check carrying the exact anchor name; the category anchor matches
        # author-check names literally, so per-joint suffixes would not register.
        axle_ok = all(
            object_model.get_articulation(jn).articulation_type == ArticulationType.REVOLUTE
            and "interface_mate" in (object_model.get_articulation(jn).meta or {})
            for jn in joint_names
        )
        ctx.check(
            "category_anchor: bail turns about the pivot axle line",
            axle_ok,
            details=", ".join(
                f"{jn}: type={object_model.get_articulation(jn).articulation_type} "
                f"mate={'interface_mate' in (object_model.get_articulation(jn).meta or {})}"
                for jn in joint_names
            ),
        )
        for bn, jn in zip(bail_names, joint_names):
            joint = object_model.get_articulation(jn)
            bail = object_model.get_part(bn)
            with ctx.pose({joint: 0.0}):
                rest = ctx.part_world_aabb(bail)
            with ctx.pose({joint: float(joint.motion_limits.upper)}):
                swung = ctx.part_world_aabb(bail)
            if rest is not None and swung is not None:
                # Compare all three axes: a side bail turns about Y, so its
                # displacement shows up in X, which a Y/Z-only comparison misses.
                moved = max(abs(swung[1][k] - rest[1][k]) for k in range(3))
                ctx.check(
                    f"{jn}: bail actually swings",
                    moved > 0.01,
                    details=f"rest={rest[1]} swung={swung[1]} max_delta={moved:.4f}",
                )

    # --- secondary storage strokes are guided, never free travel -------------
    if r.secondary_storage == "removable_inner_caddy":
        _cx, _cy, _h, seat, rib_top, lift = _caddy_dims(r)
        joint = object_model.get_articulation("tub_to_caddy")
        ctx.check(
            "caddy stays engaged with its guide ribs at full lift",
            rib_top - (seat + lift) >= 0.004,
            details=(
                f"rib_top={rib_top:.4f} seat={seat:.4f} lift={lift:.4f} "
                f"engagement={rib_top - (seat + lift):.4f}"
            ),
        )
        ctx.check(
            "caddy lift matches the derived guided stroke",
            abs(float(joint.motion_limits.upper) - lift) < 1e-9,
            details=f"upper={joint.motion_limits.upper} derived={lift}",
        )

    # --- at least one real mechanism ----------------------------------------
    moving = [
        j
        for j in object_model.articulations
        if j.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC, ArticulationType.CONTINUOUS)
    ]
    ctx.check(
        "basket has at least one non-fixed joint",
        len(moving) >= 1,
        details=f"joints={[j.name for j in object_model.articulations]}",
    )

    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    # The rest-pose overlap check is the harness baseline's job. Calling
    # `fail_if_parts_overlap_in_current_pose` here would also force exact mesh
    # collisions during preflight, which deliberately defers them to sweep.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "ResolvedShoppingBucketConfig",
    "ShoppingBucketConfig",
    "build_shopping_bucket",
    "config_from_seed",
    "resolve_config",
    "run_shopping_bucket_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
