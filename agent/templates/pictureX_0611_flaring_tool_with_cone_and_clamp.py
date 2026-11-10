# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained plumbing/tubing flaring tool template (pictureX_0611).

A split clamp bar (root, ``clamp_bar``) carries ``tube_hole_count`` progressively
sized tube seats plus the continuous flare groove that links them.  A cast yoke
bridges the working seat and hosts the rotary feed screw (revolute on the TRUE
spindle Z axis, registered through ``mate_axes``) and the flaring cone, which
advances axially (prismatic, -Z) down that same spindle axis into the seat.  A
side yoke-lock screw turns about Y, and the ``screw_clamp`` family adds a
captured end tightening screw turning about Z.

Structural slots (all source-derived, freely combinable -> core_domain = 16):
  * handle_style : tommy_bar       | wing_handle
  * yoke_frame   : inverted_u_cast | twin_cheek_cast
  * yoke_mount   : sliding         | pivoting
  * end_clamp    : plain_hinge     | screw_clamp
Multiplicity: tube_hole_count = 4|5|6|7 on the ``end_clamp`` slot.

Frame: +X along the bar, the split plane at y=0 (the fixed half occupies y<0,
the moving half y>0), +Z up from the bar's underside.  The working seat sits at
x = 0 and the yoke's local origin rides there.

MECHANISM NOTES (hard-won, do not "simplify" away):

* The yoke is an X-legged bridge: its legs come down fore and aft of the working
  seat and seat on the bar's TOP face.  It deliberately does NOT straddle the
  bar in Y.  A Y-straddling yoke is geometrically incompatible with a hinged
  split bar: at the yoke station the moving jaw sweeps a*tan(q) sideways
  (~63 mm at q=0.45 with a=130 mm), so any cheek outboard of the bar is hit long
  before the clamp is usefully open.  Bridging in X keeps the whole yoke above
  z=H on the jaw side, so clamp-open and yoke poses are genuinely independent.

* The cone descends into the continuous flare groove that runs the length of the
  seat row, not only into the discrete seats.  The sliding yoke can stop between
  seats (random motion-QC poses do exactly that), so the cone's radius at the
  bar's top plane is derived from the GROOVE half width, giving real clearance
  at every yoke position and at every jaw angle.

* No ``allow_overlap`` anywhere.  Every captured contact is real geometry lapping
  by ``_MOUNT`` = 0.6 mm, under the collision tolerance, and each one is
  invariant along its own joint's travel so it survives both limits:
    - yoke legs seat on the bar top face          (vertical lap, any x / any pivot)
    - hinge knuckles lap the moving jaw's barrel  (vertical lap, concentric)
    - feed-screw thrust flange on the collar top  (vertical lap, spin invariant)
    - cone shank on the yoke's guide detents      (radial lap, whole stroke)
    - yoke-lock hub on the lock boss face         (axial lap, spin invariant)
    - clamp-screw flange on the bar top face      (vertical lap, spin invariant)
  Element overlap is measured on world AABBs and ``min_depth`` is the SMALLEST
  axis, so every one of these is built so exactly one axis carries the 0.6 mm.

* Clearance fits (yoke bore vs cone, collar vs screw shaft, knuckle bore vs pin,
  lock bore vs stem, clamp bore vs stem) are real CAD cuts: their AABBs
  interpenetrate but fcl reports no contact, which is what the gate needs.

No source runtime, snapshot or other template is imported; stdlib + sdk +
cadquery only.  No motion clamping: every joint keeps its full authored travel.
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
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

HandleStyle = Literal["tommy_bar", "wing_handle"]
YokeFrame = Literal["inverted_u_cast", "twin_cheek_cast"]
YokeMount = Literal["sliding", "pivoting"]
EndClamp = Literal["plain_hinge", "screw_clamp"]
PaletteStyle = Literal["cast_zinc", "black_oxide", "bright_alloy"]

HANDLE_STYLES: tuple[HandleStyle, ...] = ("tommy_bar", "wing_handle")
YOKE_FRAMES: tuple[YokeFrame, ...] = ("inverted_u_cast", "twin_cheek_cast")
YOKE_MOUNTS: tuple[YokeMount, ...] = ("sliding", "pivoting")
END_CLAMPS: tuple[EndClamp, ...] = ("plain_hinge", "screw_clamp")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("cast_zinc", "black_oxide", "bright_alloy")
TUBE_HOLE_COUNTS: tuple[int, ...] = (4, 5, 6, 7)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("handle_style", HANDLE_STYLES),
        component_slot("yoke_frame", YOKE_FRAMES),
        component_slot("yoke_mount", YOKE_MOUNTS),
        component_slot("end_clamp", END_CLAMPS),
        multiplicity_slot("tube_hole_count", TUBE_HOLE_COUNTS, item_slot="end_clamp"),
    )
)

# --- independent continuous parameter bounds (do NOT inflate core/raw) -------
_PITCH_MIN, _PITCH_MAX = 0.038, 0.046
_WIDTH_MIN, _WIDTH_MAX = 0.024, 0.030
_HEIGHT_MIN, _HEIGHT_MAX = 0.018, 0.030

# --- fixed proportions (surface/hardware detail, not core/raw) ---------------
_MOUNT = 0.0006          # captured-contact engagement, under the collision tolerance
_SEAM = 0.0003           # split-line gap between the two clamp halves
_FIT = 0.0008            # running clearance in every real bore

_HOLE_D_MIN = 0.0070     # smallest tube seat diameter
_HOLE_D_STEP = 0.0020    # progressive step across the seat row
_CBORE_RATIO = 1.25      # counterbore radius factor
_CBORE_DEPTH = 0.0015

_GROOVE_HALF = 0.0032    # flare groove half width on the split plane
_GROOVE_DEPTH = 0.0060

_HINGE_PIN_R = 0.0040
_KNUCKLE_R = 0.0110
_KNUCKLE_BORE_R = _HINGE_PIN_R + _FIT
_KNUCKLE_END = 0.0060    # fixed upper/lower knuckle thickness
_PIN_HEAD_R = 0.0080

_LEG_INNER_X = 0.020     # yoke leg inner face
_LEG_OUTER_X = 0.030     # yoke leg outer face == yoke half length in X
_BORE_WIDE_R = 0.0135    # cone clearance bore through the yoke
_BORE_THREAD_R = 0.0080  # threaded feed-screw bore
_FEED_SHAFT_R = 0.0072

_CONE_TIP_R = 0.0012
_CONE_PILOT_Z = 0.0060
_CONE_MAX_R = 0.0110
_CONE_FLANK_Z = 0.0170
_CONE_BAND_Z = 0.0190
_CONE_SHANK_R = 0.0058
_CONE_SHANK_Z = 0.0230   # local z where the parallel shank starts
_CONE_SHANK_LEN = 0.0340
_CONE_TOP_Z = _CONE_SHANK_Z + _CONE_SHANK_LEN

_CONE_RETRACT = 0.0120   # tip height above the bar top at q=0
_CONE_PENETRATION = 0.0050
_CONE_STROKE = _CONE_RETRACT + _CONE_PENETRATION

_DETENT_R = 0.0011
_DETENT_DC = _CONE_SHANK_R + _DETENT_R - _MOUNT
_GUIDE_DZ = 0.0440       # detent height above the bar top

_COLLAR_TOP_DZ = 0.0680  # yoke collar top above the bar top
_BORE_THREAD_DZ = 0.0520  # where the wide cone bore steps down to the thread bore

_LOCK_AXIS_DZ = 0.0170   # yoke-lock axis height above the bar top
_LOCK_BOSS_OUT = 0.0060  # lock boss face outboard of the bar's -Y face
_LOCK_BORE_R = 0.0050
_LOCK_STEM_R = _LOCK_BORE_R - _FIT
_LOCK_HUB_R = 0.0090
_LOCK_HANDLE_DY = 0.0140  # handle plane outboard of the lock boss face
_LOCK_DETENT_R = 0.0012
_LOCK_DETENT_DC = _LOCK_BORE_R + _MOUNT - _LOCK_DETENT_R

_CLAMP_STEM_R = 0.0045
_CLAMP_BORE_R = _CLAMP_STEM_R + _FIT
_CLAMP_FLANGE_R = 0.0090
_CLAMP_HEAD_DZ = 0.0100
_CLAMP_HUB_R = 0.0072

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "cast_zinc": {
        "bar": (0.54, 0.52, 0.47, 1.0),
        "cast": (0.57, 0.58, 0.57, 1.0),
        "thread": (0.20, 0.19, 0.18, 1.0),
        "bright": (0.78, 0.80, 0.80, 1.0),
        "mark": (0.72, 0.16, 0.08, 1.0),
    },
    "black_oxide": {
        "bar": (0.055, 0.065, 0.065, 1.0),
        "cast": (0.68, 0.71, 0.71, 1.0),
        "thread": (0.11, 0.13, 0.13, 1.0),
        "bright": (0.76, 0.79, 0.80, 1.0),
        "mark": (0.80, 0.62, 0.10, 1.0),
    },
    "bright_alloy": {
        "bar": (0.70, 0.71, 0.73, 1.0),
        "cast": (0.80, 0.81, 0.82, 1.0),
        "thread": (0.30, 0.31, 0.33, 1.0),
        "bright": (0.88, 0.89, 0.90, 1.0),
        "mark": (0.15, 0.35, 0.70, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    handle_style: HandleStyle = "tommy_bar"
    yoke_frame: YokeFrame = "inverted_u_cast"
    yoke_mount: YokeMount = "sliding"
    end_clamp: EndClamp = "plain_hinge"
    tube_hole_count: int = 5
    bar_pitch_m: float | None = None
    bar_width_m: float | None = None
    bar_height_m: float | None = None
    palette_style: PaletteStyle = "cast_zinc"
    name: str = "pictureX_0611_flaring_tool_with_cone_and_clamp"


@dataclass(frozen=True)
class ResolvedConfig:
    handle_style: HandleStyle
    yoke_frame: YokeFrame
    yoke_mount: YokeMount
    end_clamp: EndClamp
    tube_hole_count: int
    bar_pitch_m: float
    bar_width_m: float
    bar_height_m: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    name: str
    end_margin: float
    hole_xs: tuple[float, ...]
    hole_radii: tuple[float, ...]
    working_index: int
    bar_x_lo: float
    bar_x_hi: float
    bar_length: float
    hinge_x: float
    moving_x_lo: float
    moving_x_hi: float
    clamp_screw_x: float
    clamp_screw_y: float
    yoke_travel_lo: float
    yoke_travel_hi: float
    yoke_pivot_span: float
    jaw_open: float
    cone_stroke: float
    cone_tip_clearance: float
    groove_x_lo: float
    groove_x_hi: float
    yoke_half_span_y: float
    leg_foot_z: float

    @property
    def bar_height(self) -> float:
        return self.bar_height_m

    @property
    def bar_width(self) -> float:
        return self.bar_width_m

    def cone_radius_at_height(self, dz: float) -> float:
        """Cone radius dz above its own tip (local profile lookup)."""
        if dz <= 0.0:
            return 0.0
        if dz <= _CONE_PILOT_Z:
            return _CONE_TIP_R * dz / _CONE_PILOT_Z
        if dz <= _CONE_FLANK_Z:
            t = (dz - _CONE_PILOT_Z) / (_CONE_FLANK_Z - _CONE_PILOT_Z)
            return _CONE_TIP_R + t * (_CONE_MAX_R - _CONE_TIP_R)
        return _CONE_MAX_R


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(int(seed))
    rng = random.Random(int(seed) ^ 0x0F1A_2B3C)
    return Config(
        handle_style=choices["handle_style"],
        yoke_frame=choices["yoke_frame"],
        yoke_mount=choices["yoke_mount"],
        end_clamp=choices["end_clamp"],
        tube_hole_count=int(choices["tube_hole_count"]),
        bar_pitch_m=round(rng.uniform(_PITCH_MIN, _PITCH_MAX), 5),
        bar_width_m=round(rng.uniform(_WIDTH_MIN, _WIDTH_MAX), 5),
        bar_height_m=round(rng.uniform(_HEIGHT_MIN, _HEIGHT_MAX), 5),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"pictureX_0611_flaring_tool_with_cone_and_clamp_seed_{int(seed)}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "handle_style": cfg.handle_style,
            "yoke_frame": cfg.yoke_frame,
            "yoke_mount": cfg.yoke_mount,
            "end_clamp": cfg.end_clamp,
            "tube_hole_count": int(cfg.tube_hole_count),
        }
    )
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"unknown palette_style {cfg.palette_style!r}")

    pitch = _clamp(
        _PITCH_MIN if cfg.bar_pitch_m is None else cfg.bar_pitch_m, _PITCH_MIN, _PITCH_MAX
    )
    width = _clamp(
        _WIDTH_MIN if cfg.bar_width_m is None else cfg.bar_width_m, _WIDTH_MIN, _WIDTH_MAX
    )
    height = _clamp(
        _HEIGHT_MIN if cfg.bar_height_m is None else cfg.bar_height_m, _HEIGHT_MIN, _HEIGHT_MAX
    )

    n = int(cfg.tube_hole_count)
    working = n // 2
    hole_xs = tuple((i - working) * pitch for i in range(n))
    hole_radii = tuple(0.5 * (_HOLE_D_MIN + i * _HOLE_D_STEP) for i in range(n))

    # The end margin clears the yoke's half length plus the end screw head, and
    # holds the hinge hardware clear of the yoke at the other travel extreme.
    end_margin = 1.4 * pitch
    bar_x_lo = hole_xs[0] - end_margin
    bar_x_hi = hole_xs[-1] + end_margin + 0.010
    hinge_x = bar_x_lo + 0.012
    moving_x_lo = hinge_x + 0.013
    moving_x_hi = hole_xs[-1] + 0.45 * end_margin

    return ResolvedConfig(
        handle_style=cfg.handle_style,
        yoke_frame=cfg.yoke_frame,
        yoke_mount=cfg.yoke_mount,
        end_clamp=cfg.end_clamp,
        tube_hole_count=n,
        bar_pitch_m=pitch,
        bar_width_m=width,
        bar_height_m=height,
        palette_style=cfg.palette_style,
        palette=dict(PALETTES[cfg.palette_style]),
        name=cfg.name,
        end_margin=end_margin,
        hole_xs=hole_xs,
        hole_radii=hole_radii,
        working_index=working,
        bar_x_lo=bar_x_lo,
        bar_x_hi=bar_x_hi,
        bar_length=bar_x_hi - bar_x_lo,
        hinge_x=hinge_x,
        moving_x_lo=moving_x_lo,
        moving_x_hi=moving_x_hi,
        clamp_screw_x=hole_xs[-1] + end_margin,
        clamp_screw_y=-0.5 * width,
        # The sliding yoke indexes the whole seat row; the pivoting yoke swings
        # about the working seat itself, so the cone never leaves that bore.
        yoke_travel_lo=hole_xs[0],
        yoke_travel_hi=hole_xs[-1],
        yoke_pivot_span=0.16,
        jaw_open=0.45,
        cone_stroke=_CONE_STROKE,
        cone_tip_clearance=_GROOVE_DEPTH - _CONE_PENETRATION,
        groove_x_lo=hole_xs[0] - 0.006,
        groove_x_hi=hole_xs[-1] + 0.006,
        yoke_half_span_y=width - 0.003,
        # The yoke's leg-feet plane: 0.6 mm into the bar's top face.  This is the
        # single captured seating that carries the whole bridge, and it is the
        # same value at every yoke position and every jaw angle.
        leg_foot_z=height - _MOUNT,
    )


def slot_choices_for_config(r: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("handle_style", r.handle_style),
        ("yoke_frame", r.yoke_frame),
        ("yoke_mount", r.yoke_mount),
        ("end_clamp", r.end_clamp),
        ("tube_hole_count", int(r.tube_hole_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    return {key: model.material(f"flaring_{key}", rgba=rgba) for key, rgba in r.palette.items()}


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.steel_bare",
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cq_cyl(radius: float, z0: float, z1: float, x: float = 0.0, y: float = 0.0):
    return cq.Workplane("XY", origin=(x, y, z0)).circle(radius).extrude(z1 - z0)


def _cq_box(x0, x1, y0, y1, z0, z1):
    return (
        cq.Workplane("XY")
        .box(x1 - x0, y1 - y0, z1 - z0)
        .translate((0.5 * (x0 + x1), 0.5 * (y0 + y1), 0.5 * (z0 + z1)))
    )


def _wing_shape(span: float, lobe: float, thickness: float, hub_r: float):
    """Cast butterfly wing: two elliptical lobes bridged over a boss."""
    solid = (
        cq.Workplane("XY", origin=(0.0, 0.0, -0.5 * thickness))
        .rect(0.60 * span, 0.60 * lobe)
        .extrude(thickness)
    )
    for side in (-1.0, 1.0):
        solid = solid.union(
            cq.Workplane("XY", origin=(0.0, 0.0, -0.5 * thickness))
            .center(side * 0.30 * span, 0.0)
            .ellipse(0.19 * span, 0.5 * lobe)
            .extrude(thickness)
        )
    return solid.union(_cq_cyl(hub_r, -0.62 * thickness, 0.62 * thickness))


# ---------------------------------------------------------------------------
# handle_style slot: the turning-handle family shared by the feed, lock and end
# screws.  Both candidates change the part tree of every screw they dress.
# ---------------------------------------------------------------------------
def _handle_style_tommy_bar_build(
    part, mats, *, scope: str, center, half_span: float, bar_radius: float, stop_radius: float
) -> None:
    """REC001 family: a straight sliding tommy bar with two ball stops."""
    _cyl(
        part,
        bar_radius,
        2.0 * half_span,
        center,
        mats["bright"],
        f"handle_style__tommy_bar__{scope}_tommy_bar",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    for k, side in enumerate((-1.0, 1.0)):
        part.visual(
            Sphere(radius=stop_radius),
            origin=Origin(xyz=(center[0] + side * half_span, center[1], center[2])),
            material=mats["bright"],
            name=f"handle_style__tommy_bar__{scope}_bar_stop_{k}", material_class_id="metal.chrome_polished",
        )


def _handle_style_wing_handle_build(
    part,
    mats,
    assets,
    *,
    scope: str,
    center,
    span: float,
    lobe: float,
    thickness: float,
    hub_radius: float,
    material_key: str,
    rpy=(0.0, 0.0, 0.0),
) -> None:
    """REC002 family: a broad cast two-lobe butterfly wing on a boss."""
    part.visual(
        mesh_from_cadquery(
            _wing_shape(span, lobe, thickness, hub_radius),
            f"flaring_{scope}_wing",
            assets=assets,
            tolerance=0.0003,
        ),
        origin=Origin(xyz=center, rpy=rpy),
        material=mats[material_key],
        name=f"handle_style__wing_handle__{scope}_wing", material_class_id="metal.cast_iron_bare",
    )


# ---------------------------------------------------------------------------
# end_clamp slot: the split clamp bar family (hosts the N tube seats)
# ---------------------------------------------------------------------------
def _bar_shell_shape(r: ResolvedConfig):
    h = r.bar_height
    body = _cq_box(r.bar_x_lo, r.bar_x_hi, -r.bar_width, 0.0, 0.0, h)
    # Hinge relief: the moving jaw's barrel turns inside the fixed knuckles with
    # a real running clearance, so fcl never reports contact with the bar shell.
    body = body.cut(
        _cq_cyl(
            _KNUCKLE_R + _FIT,
            _KNUCKLE_END - _MOUNT - 0.0006,
            h - _KNUCKLE_END + _MOUNT + 0.0006,
            x=r.hinge_x,
        )
    )
    for x, radius in zip(r.hole_xs, r.hole_radii):
        body = body.cut(_cq_cyl(radius, -0.002, h + 0.002, x=x))
        body = body.cut(_cq_cyl(_CBORE_RATIO * radius, h - _CBORE_DEPTH, h + 0.002, x=x))
    # Continuous flare groove linking the seat row: the cone rides it at every
    # yoke position, so the cone/bar clearance is pose independent.
    body = body.cut(
        _cq_box(
            r.groove_x_lo, r.groove_x_hi, -_GROOVE_HALF, _GROOVE_HALF, h - _GROOVE_DEPTH, h + 0.002
        )
    )
    if r.end_clamp == "screw_clamp":
        body = body.cut(
            _cq_cyl(_CLAMP_BORE_R, -0.002, h + 0.002, x=r.clamp_screw_x, y=r.clamp_screw_y)
        )
    return body


def _build_clamp_bar(model, r: ResolvedConfig, mats, assets):
    cand = r.end_clamp
    h = r.bar_height
    bar = model.part(
        f"end_clamp__{cand}__clamp_bar",
        meta={
            "role": "clamp_bar",
            "candidate": cand,
            "tube_hole_count": r.tube_hole_count,
            "tube_hole_centers_m": list(r.hole_xs),
            "tube_hole_diameters_m": [2.0 * v for v in r.hole_radii],
        },
    )
    bar.visual(
        mesh_from_cadquery(
            _bar_shell_shape(r), f"flaring_{cand}_bar_shell", assets=assets, tolerance=0.0005
        ),
        material=mats["bar"],
        name="bar_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_zinc", "bright_alloy"} else "metal.blackened_gunmetal"),
    )
    # Hinge hardware: pin plus the two fixed knuckles that capture the moving
    # jaw's barrel from below and above (vertical 0.6 mm lap, concentric with
    # the pivot so it holds through the whole swing).
    _cyl(
        bar,
        _HINGE_PIN_R,
        h + 0.010,
        (r.hinge_x, 0.0, 0.5 * (h + 0.010)),
        mats["thread"],
        "hinge_pin",
    )
    _cyl(
        bar,
        _KNUCKLE_R,
        _KNUCKLE_END,
        (r.hinge_x, 0.0, 0.5 * _KNUCKLE_END),
        mats["bar"],
        "hinge_knuckle_lower",
    )
    _cyl(
        bar,
        _KNUCKLE_R,
        _KNUCKLE_END,
        (r.hinge_x, 0.0, h - 0.5 * _KNUCKLE_END),
        mats["bar"],
        "hinge_knuckle_upper",
    )
    _cyl(bar, _PIN_HEAD_R, 0.003, (r.hinge_x, 0.0, h + 0.0115), mats["thread"], "hinge_pin_head")
    # N size-index plates, one per seat: the multiplicity's slot-scoped growth.
    for i, x in enumerate(r.hole_xs):
        _box(
            bar,
            (0.010, 0.0012, 0.005),
            (x, -r.bar_width + 0.0002, 0.55 * h),
            mats["mark"],
            f"end_clamp__{cand}__hole_size_marker_{i}",
        )
    return bar


def _moving_jaw_shell_shape(r: ResolvedConfig):
    h = r.bar_height
    body = _cq_box(r.moving_x_lo, r.moving_x_hi, _SEAM, _SEAM + r.bar_width, 0.0, h)
    for x, radius in zip(r.hole_xs, r.hole_radii):
        body = body.cut(_cq_cyl(radius, -0.002, h + 0.002, x=x))
        body = body.cut(_cq_cyl(_CBORE_RATIO * radius, h - _CBORE_DEPTH, h + 0.002, x=x))
    body = body.cut(
        _cq_box(
            r.groove_x_lo,
            r.groove_x_hi,
            -0.001,
            _SEAM + _GROOVE_HALF,
            h - _GROOVE_DEPTH,
            h + 0.002,
        )
    )
    # The jaw's joint frame sits ON the hinge axis, so its geometry has to be
    # authored there: built in bar coordinates it would be carried away by the
    # joint origin and the whole clamp would fly apart.
    return body.translate((-r.hinge_x, 0.0, 0.0))


def _moving_jaw_knuckle_shape(r: ResolvedConfig):
    h = r.bar_height
    z0 = _KNUCKLE_END - _MOUNT
    z1 = h - _KNUCKLE_END + _MOUNT
    barrel = _cq_cyl(_KNUCKLE_R, z0, z1, x=r.hinge_x).cut(
        _cq_cyl(_KNUCKLE_BORE_R, z0 - 0.002, z1 + 0.002, x=r.hinge_x)
    )
    neck = _cq_box(r.hinge_x + 0.006, r.hinge_x + 0.016, _SEAM, _SEAM + 0.010, z0, z1)
    return barrel.union(neck).translate((-r.hinge_x, 0.0, 0.0))


def _build_moving_jaw(model, r: ResolvedConfig, mats, assets):
    cand = r.end_clamp
    jaw = model.part(
        f"end_clamp__{cand}__moving_jaw",
        meta={"role": "moving_jaw", "candidate": cand},
    )
    jaw.visual(
        mesh_from_cadquery(
            _moving_jaw_shell_shape(r),
            f"flaring_{cand}_moving_jaw",
            assets=assets,
            tolerance=0.0005,
        ),
        material=mats["bar"],
        name="jaw_shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_zinc", "bright_alloy"} else "metal.blackened_gunmetal"),
    )
    jaw.visual(
        mesh_from_cadquery(
            _moving_jaw_knuckle_shape(r),
            f"flaring_{cand}_jaw_knuckle",
            assets=assets,
            tolerance=0.0004,
        ),
        material=mats["bar"],
        name="hinge_knuckle", material_class_id=("metal.aluminum_bare" if r.palette_style in {"cast_zinc", "bright_alloy"} else "metal.blackened_gunmetal"),
    )
    # Raised grip rib on the moving half's outer face.  Primitive on purpose:
    # it is the mesh-free probe the author tests measure the swing with.
    _box(
        jaw,
        (0.030, 0.0014, 0.006),
        (r.moving_x_hi - 0.020 - r.hinge_x, _SEAM + r.bar_width - 0.0002, 0.55 * r.bar_height),
        mats["mark"],
        f"end_clamp__{cand}__jaw_grip_rib",
    )
    return jaw


def _end_clamp_plain_hinge_build(model, r, mats, assets):
    """REC001 family: the split bar closes on the hinge alone, no end screw."""
    bar = _build_clamp_bar(model, r, mats, assets)
    jaw = _build_moving_jaw(model, r, mats, assets)
    # A pressed retaining collar over the pin is the plain family's read.
    _cyl(
        bar,
        _PIN_HEAD_R + 0.0022,
        0.0025,
        (r.hinge_x, 0.0, r.bar_height + 0.0055),
        mats["bright"],
        "end_clamp__plain_hinge__pin_retainer",
    )
    return bar, jaw, None


def _end_clamp_screw_clamp_build(model, r, mats, assets):
    """REC002 family: adds a captured rotary end screw in the split end bore."""
    bar = _build_clamp_bar(model, r, mats, assets)
    jaw = _build_moving_jaw(model, r, mats, assets)
    screw = model.part(
        "end_clamp__screw_clamp__clamp_screw",
        meta={"role": "clamp_screw", "candidate": "screw_clamp"},
    )
    _cyl(
        screw,
        _CLAMP_STEM_R,
        0.020,
        (0.0, 0.0, -0.008),
        mats["bright"],
        "end_clamp__screw_clamp__clamp_stem",
    )
    # Flange bears on the bar's top face: 0.6 mm on Z only, spin invariant.
    _cyl(
        screw,
        _CLAMP_FLANGE_R,
        0.004,
        (0.0, 0.0, -_MOUNT + 0.002),
        mats["thread"],
        "end_clamp__screw_clamp__clamp_flange",
    )
    # Hub bridging the flange to the head: without it every head element read
    # as a floating island inside the screw.
    _cyl(
        screw,
        _CLAMP_HUB_R,
        0.010,
        (0.0, 0.0, 0.007),
        mats["thread"],
        "end_clamp__screw_clamp__clamp_hub",
    )
    if r.handle_style == "tommy_bar":
        _handle_style_tommy_bar_build(
            screw,
            mats,
            scope="clamp",
            center=(0.0, 0.0, _CLAMP_HEAD_DZ),
            half_span=0.015,
            bar_radius=0.0030,
            stop_radius=0.0040,
        )
    else:
        _handle_style_wing_handle_build(
            screw,
            mats,
            assets,
            scope="clamp",
            center=(0.0, 0.0, _CLAMP_HEAD_DZ),
            span=0.034,
            lobe=0.013,
            thickness=0.006,
            hub_radius=_CLAMP_HUB_R,
            material_key="thread",
        )
    return bar, jaw, screw


_END_CLAMP_BUILDERS = {
    "plain_hinge": _end_clamp_plain_hinge_build,
    "screw_clamp": _end_clamp_screw_clamp_build,
}


# ---------------------------------------------------------------------------
# yoke_frame slot: the cast bridge that carries the spindle over the seat row
# ---------------------------------------------------------------------------
def _yoke_bores(solid, r: ResolvedConfig):
    h = r.bar_height
    solid = solid.cut(_cq_cyl(_BORE_WIDE_R, h - 0.010, h + _BORE_THREAD_DZ))
    solid = solid.cut(_cq_cyl(_BORE_THREAD_R, h + _BORE_THREAD_DZ, h + _COLLAR_TOP_DZ + 0.004))
    # Transverse lock bore.  Built from an explicit oriented solid: a positive
    # "XZ" extrusion runs toward -Y, which silently left the boss un-bored and
    # the lock stem interpenetrating the casting.
    lock_bore = cq.Workplane(
        obj=cq.Solid.makeCylinder(
            _LOCK_BORE_R,
            0.100,
            cq.Vector(0.0, -(r.bar_width + _LOCK_BOSS_OUT + 0.020), h + _LOCK_AXIS_DZ),
            cq.Vector(0.0, 1.0, 0.0),
        )
    )
    return solid.cut(lock_bore)


def _lock_boss_solid(r: ResolvedConfig):
    """Side boss carrying the yoke-lock bore.

    It reaches inboard to mid-span and up into the crown/bridge so the casting
    actually carries it; a boss that only met a cheek at its face read as a
    disconnected island.  The wide cone bore is cut afterwards, so the boss
    never intrudes on the cone's envelope.
    """
    h = r.bar_height
    return _cq_box(
        -0.011,
        0.011,
        -(r.bar_width + _LOCK_BOSS_OUT),
        -0.5 * r.yoke_half_span_y,
        h + _LOCK_AXIS_DZ - 0.007,
        h + 0.030,
    )


def _yoke_frame_inverted_u_cast_shape(r: ResolvedConfig):
    """REC001 family: one continuous cast arch, full width, windowed below."""
    h = r.bar_height
    zf = r.leg_foot_z
    span = r.yoke_half_span_y
    profile = [
        (-_LEG_OUTER_X, zf),
        (-_LEG_OUTER_X, h + 0.020),
        (-0.022, h + 0.034),
        (-0.010, h + 0.042),
        (0.010, h + 0.042),
        (0.022, h + 0.034),
        (_LEG_OUTER_X, h + 0.020),
        (_LEG_OUTER_X, zf),
        (_LEG_INNER_X, zf),
        (_LEG_INNER_X, h + 0.018),
        (-_LEG_INNER_X, h + 0.018),
        (-_LEG_INNER_X, zf),
    ]
    arch = (
        cq.Workplane("XZ", origin=(0.0, span, 0.0)).polyline(profile).close().extrude(2.0 * span)
    )
    boss = _cq_cyl(0.016, h + 0.038, h + _COLLAR_TOP_DZ)
    solid = arch.union(boss).union(_lock_boss_solid(r))
    return _yoke_bores(solid, r)


def _yoke_frame_twin_cheek_cast_shape(r: ResolvedConfig):
    """REC002 family: two opposed cheeks tied by a top bridge and a bored collar."""
    h = r.bar_height
    zf = r.leg_foot_z
    span = r.yoke_half_span_y
    cheek_t = 0.010
    profile = [
        (-_LEG_OUTER_X, zf),
        (-_LEG_OUTER_X, h + 0.030),
        (_LEG_OUTER_X, h + 0.030),
        (_LEG_OUTER_X, zf),
        (_LEG_INNER_X, zf),
        (_LEG_INNER_X, h + 0.022),
        (-_LEG_INNER_X, h + 0.022),
        (-_LEG_INNER_X, zf),
    ]
    solid = None
    for side in (-1.0, 1.0):
        y_far = span if side > 0 else -span + cheek_t
        cheek = (
            cq.Workplane("XZ", origin=(0.0, y_far, 0.0)).polyline(profile).close().extrude(cheek_t)
        )
        solid = cheek if solid is None else solid.union(cheek)
    bridge = _cq_box(-0.026, 0.026, -span, span, h + 0.026, h + 0.040)
    collar = _cq_cyl(0.021, h + 0.034, h + _COLLAR_TOP_DZ)
    solid = solid.union(bridge).union(collar).union(_lock_boss_solid(r))
    return _yoke_bores(solid, r)


_YOKE_SHAPES = {
    "inverted_u_cast": _yoke_frame_inverted_u_cast_shape,
    "twin_cheek_cast": _yoke_frame_twin_cheek_cast_shape,
}


def _yoke_frame_inverted_u_cast_build(model, r: ResolvedConfig, mats, assets):
    return _build_yoke(model, r, mats, assets, candidate="inverted_u_cast")


def _yoke_frame_twin_cheek_cast_build(model, r: ResolvedConfig, mats, assets):
    return _build_yoke(model, r, mats, assets, candidate="twin_cheek_cast")


_YOKE_FRAME_BUILDERS = {
    "inverted_u_cast": _yoke_frame_inverted_u_cast_build,
    "twin_cheek_cast": _yoke_frame_twin_cheek_cast_build,
}


def _build_yoke(model, r: ResolvedConfig, mats, assets, *, candidate: str | None = None):
    cand = candidate or r.yoke_frame
    h = r.bar_height
    yoke = model.part(
        f"yoke_frame__{cand}__yoke",
        meta={"role": "yoke", "candidate": cand, "mount": r.yoke_mount},
    )
    yoke.visual(
        mesh_from_cadquery(
            _YOKE_SHAPES[cand](r), f"flaring_{cand}_yoke", assets=assets, tolerance=0.0005
        ),
        material=mats["cast"],
        name=f"yoke_frame__{cand}__cast_frame", material_class_id="metal.cast_iron_bare",
    )
    # Cone guide: four ball detents on stub ribs graze the cone's shank by
    # _MOUNT for the WHOLE stroke, so the cone is captured at both extremes.
    # Spheres are used because their AABB is orientation invariant and their
    # world-AABB overlap with the cone is only one detent diameter on EVERY
    # axis, well under the collision tolerance.
    rib_mid = 0.5 * ((_DETENT_DC + _DETENT_R) + _BORE_WIDE_R + 0.0004)
    rib_len = (_BORE_WIDE_R + 0.0004) - (_DETENT_DC + _DETENT_R)
    for k in range(4):
        ang = 0.5 * math.pi * k
        cx, cy = math.cos(ang), math.sin(ang)
        _box(
            yoke,
            (rib_len, 0.0024, 0.0024) if k % 2 == 0 else (0.0024, rib_len, 0.0024),
            (cx * rib_mid, cy * rib_mid, h + _GUIDE_DZ),
            mats["cast"],
            f"cone_guide_rib_{k}",
        )
        yoke.visual(
            Sphere(radius=_DETENT_R),
            origin=Origin(xyz=(cx * _DETENT_DC, cy * _DETENT_DC, h + _GUIDE_DZ)),
            material=mats["bright"],
            name=f"cone_guide_pad_{k}", material_class_id="metal.chrome_polished",
        )
    return yoke


# ---------------------------------------------------------------------------
# feed screw, flaring cone and yoke lock (shared core mechanism)
# ---------------------------------------------------------------------------
def _threaded_shaft_geometry(z0: float, z1: float, radius: float):
    """Lathed ring-thread silhouette: the real screw thread form, not a tube."""
    pitch = 0.0032
    root = radius - 0.0011
    profile: list[tuple[float, float]] = [(0.0, z0), (root, z0)]
    z = z0
    while z < z1 - pitch:
        profile.extend(
            [
                (root, z + 0.18 * pitch),
                (radius, z + 0.36 * pitch),
                (radius, z + 0.58 * pitch),
                (root, z + 0.78 * pitch),
            ]
        )
        z += pitch
    profile.extend([(root, z1), (0.0, z1)])
    return LatheGeometry(profile, segments=48)


def _cone_geometry():
    """45-degree flaring die: slender pilot, conical flank, band, shank."""
    return LatheGeometry(
        [
            (0.0, 0.0),
            (_CONE_TIP_R, _CONE_PILOT_Z),
            (_CONE_MAX_R, _CONE_FLANK_Z),
            (_CONE_MAX_R, _CONE_BAND_Z),
            (_CONE_SHANK_R, _CONE_SHANK_Z),
            (_CONE_SHANK_R, _CONE_TOP_Z),
            (0.0, _CONE_TOP_Z),
        ],
        segments=56,
    )


def _build_feed_screw(model, r: ResolvedConfig, mats, assets):
    """Feed screw: threaded shaft + thrust flange on the collar + handle head."""
    screw = model.part("feed_screw", meta={"role": "feed_screw", "candidate": r.handle_style})
    # local z = 0 is the collar top; the shaft's nose bears on the cone shank.
    shaft_bottom = (_CONE_RETRACT + _CONE_TOP_Z) - _COLLAR_TOP_DZ - _MOUNT
    screw.visual(
        mesh_from_geometry(
            _threaded_shaft_geometry(shaft_bottom, 0.018, _FEED_SHAFT_R), "flaring_feed_thread"
        ),
        material=mats["thread"],
        name="threaded_shaft", material_class_id=("metal.steel_bare" if r.palette_style in {"cast_zinc", "bright_alloy"} else "metal.blackened_gunmetal"),
    )
    _cyl(screw, _BORE_WIDE_R, 0.004, (0.0, 0.0, -_MOUNT + 0.002), mats["bright"], "thrust_flange")
    if r.handle_style == "tommy_bar":
        _cyl(
            screw,
            0.013,
            0.014,
            (0.0, 0.0, 0.015),
            mats["thread"],
            "handle_style__tommy_bar__screw_head",
        )
        _handle_style_tommy_bar_build(
            screw,
            mats,
            scope="feed",
            center=(0.0, 0.0, 0.024),
            half_span=0.095,
            bar_radius=0.0042,
            stop_radius=0.0054,
        )
    else:
        _handle_style_wing_handle_build(
            screw,
            mats,
            assets,
            scope="feed",
            center=(0.0, 0.0, 0.024),
            span=0.160,
            lobe=0.032,
            thickness=0.011,
            hub_radius=0.014,
            material_key="cast",
        )
        _cyl(
            screw,
            0.0060,
            0.016,
            (0.0, 0.0, 0.024),
            mats["thread"],
            "handle_style__wing_handle__feed_rivet",
        )
    return screw


def _build_cone(model, r: ResolvedConfig, mats):
    del r
    cone = model.part("flaring_cone", meta={"role": "flaring_cone"})
    cone.visual(
        mesh_from_geometry(_cone_geometry(), "flaring_conical_die"),
        material=mats["bright"],
        name="conical_die", material_class_id="metal.chrome_polished",
    )
    return cone


def _build_yoke_lock(model, r: ResolvedConfig, mats, assets):
    lock = model.part("yoke_lock", meta={"role": "yoke_lock", "candidate": r.handle_style})
    # Local frame on the lock axis at the boss face; +y points into the yoke.
    _cyl(
        lock,
        _LOCK_STEM_R,
        0.026,
        (0.0, 0.007, 0.0),
        mats["thread"],
        "lock_stem",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    # Capture is by two ball detents inside the bore, NOT by a shoulder bearing
    # on the boss face: the yoke's world AABB shears when the yoke pivots, so a
    # face lap that reads 0.6 mm at neutral inflated to ~7 mm at +-0.16 rad.  A
    # small sphere's AABB is orientation invariant and sits wholly inside the
    # casting's AABB, so its overlap depth is one detent diameter in every pose.
    for k, ang in enumerate((0.0, math.pi)):
        lock.visual(
            Sphere(radius=_LOCK_DETENT_R),
            origin=Origin(
                xyz=(
                    math.cos(ang) * _LOCK_DETENT_DC,
                    0.009,
                    math.sin(ang) * _LOCK_DETENT_DC,
                )
            ),
            material=mats["bright"],
            name=f"lock_thread_detent_{k}", material_class_id="metal.chrome_polished",
        )
    _cyl(
        lock,
        _LOCK_HUB_R,
        0.012,
        (0.0, -0.0085, 0.0),
        mats["thread"],
        "lock_hub",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    if r.handle_style == "tommy_bar":
        _handle_style_tommy_bar_build(
            lock,
            mats,
            scope="lock",
            center=(0.0, -_LOCK_HANDLE_DY, 0.0),
            half_span=0.026,
            bar_radius=0.0035,
            stop_radius=0.0045,
        )
    else:
        _handle_style_wing_handle_build(
            lock,
            mats,
            assets,
            scope="lock",
            center=(0.0, -_LOCK_HANDLE_DY, 0.0),
            span=0.052,
            lobe=0.020,
            thickness=0.008,
            hub_radius=0.0095,
            material_key="cast",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    return lock


# ---------------------------------------------------------------------------
# Joints.  Every revolute/continuous joint is solved by mate_axes on the TRUE
# hardware axis and registered so the interface-mate contract can check it.
# ---------------------------------------------------------------------------
def _axis_joint(model, *, name, parent, child, provider, consumer, kind, limits, meta=None):
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        kind,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)
    return name


def _add_jaw_pivot(model, r: ResolvedConfig, bar, jaw) -> str:
    # MEASURED with a ctx.pose probe: with the hinge at the bar's left end and
    # the moving half on +Y, a POSITIVE rotation about +Z swings the free end
    # AWAY from the fixed half (y grows like a*sin q).  A negative rotation
    # would drive the moving half straight through the fixed one, so travel
    # runs 0 -> jaw_open and never the other way.
    return _axis_joint(
        model,
        name=f"end_clamp__{r.end_clamp}__jaw_pivot",
        parent=bar,
        child=jaw,
        provider=AxisInterface(
            name="bar_hinge_axis",
            point=(r.hinge_x, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=_KNUCKLE_BORE_R,
        ),
        consumer=AxisInterface(
            name="jaw_barrel_axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=_HINGE_PIN_R,
        ),
        kind=ArticulationType.REVOLUTE,
        limits=MotionLimits(lower=0.0, upper=r.jaw_open, effort=40.0, velocity=1.4),
        meta={"mechanism": "split clamp bar hinge"},
    )


def _yoke_mount_sliding_build(model, r: ResolvedConfig, bar, yoke) -> str:
    """REC001 family: the yoke is a carriage indexing along the seat row."""
    name = "yoke_mount__sliding__yoke_slide"
    model.articulation(
        name,
        ArticulationType.PRISMATIC,
        parent=bar,
        child=yoke,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            lower=r.yoke_travel_lo, upper=r.yoke_travel_hi, effort=90.0, velocity=0.18
        ),
        meta={"mechanism": "yoke indexes the tube seat row"},
    )
    return name


def _yoke_mount_pivoting_build(model, r: ResolvedConfig, bar, yoke) -> str:
    """REC002 family: the yoke swings about the working seat's own axis."""
    return _axis_joint(
        model,
        name="yoke_mount__pivoting__yoke_pivot",
        parent=bar,
        child=yoke,
        provider=AxisInterface(
            name="bar_working_seat_axis",
            point=(0.0, 0.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
        ),
        consumer=AxisInterface(
            name="yoke_spindle_axis", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
        ),
        kind=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            lower=-r.yoke_pivot_span, upper=r.yoke_pivot_span, effort=30.0, velocity=1.2
        ),
        meta={"mechanism": "yoke swings about the working seat"},
    )


_YOKE_MOUNT_BUILDERS = {
    "sliding": _yoke_mount_sliding_build,
    "pivoting": _yoke_mount_pivoting_build,
}


def _add_feed_joint(model, r: ResolvedConfig, yoke, screw) -> str:
    h = r.bar_height
    return _axis_joint(
        model,
        name="feed_screw_turn",
        parent=yoke,
        child=screw,
        provider=AxisInterface(
            name="yoke_collar_axis",
            point=(0.0, 0.0, h + _COLLAR_TOP_DZ),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=_BORE_THREAD_R,
        ),
        consumer=AxisInterface(
            name="feed_shaft_axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=_FEED_SHAFT_R,
        ),
        kind=ArticulationType.REVOLUTE,
        limits=MotionLimits(lower=0.0, upper=8.0 * math.pi, effort=55.0, velocity=7.0),
        meta={"mechanism": "feed screw", "screw_pitch_m_per_turn": 0.0020},
    )


def _add_cone_joint(model, r: ResolvedConfig, yoke, cone) -> str:
    h = r.bar_height
    name = "cone_feed"
    model.articulation(
        name,
        ArticulationType.PRISMATIC,
        parent=yoke,
        child=cone,
        origin=Origin(xyz=(0.0, 0.0, h + _CONE_RETRACT)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(lower=0.0, upper=r.cone_stroke, effort=80.0, velocity=0.012),
        meta={
            "mechanism": "flaring cone axial advance",
            "constrained_by": "feed_screw_turn",
            "nominal_pitch_m_per_turn": 0.0020,
        },
    )
    return name


def _add_lock_joint(model, r: ResolvedConfig, yoke, lock) -> str:
    h = r.bar_height
    return _axis_joint(
        model,
        name="yoke_lock_turn",
        parent=yoke,
        child=lock,
        provider=AxisInterface(
            name="yoke_lock_boss_axis",
            point=(0.0, -(r.bar_width + _LOCK_BOSS_OUT), h + _LOCK_AXIS_DZ),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=_LOCK_BORE_R,
        ),
        consumer=AxisInterface(
            name="lock_stem_axis",
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            radius=_LOCK_STEM_R,
        ),
        kind=ArticulationType.REVOLUTE,
        limits=MotionLimits(lower=-math.pi, upper=math.pi, effort=22.0, velocity=8.0),
        meta={"mechanism": "yoke lock screw"},
    )


def _add_clamp_screw_joint(model, r: ResolvedConfig, bar, screw) -> str:
    h = r.bar_height
    return _axis_joint(
        model,
        name="end_clamp__screw_clamp__clamp_rotation",
        parent=bar,
        child=screw,
        provider=AxisInterface(
            name="bar_clamp_bore_axis",
            point=(r.clamp_screw_x, r.clamp_screw_y, h),
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=_CLAMP_BORE_R,
        ),
        consumer=AxisInterface(
            name="clamp_stem_axis",
            axis=(0.0, 0.0, 1.0),
            radial=(1.0, 0.0, 0.0),
            radius=_CLAMP_STEM_R,
        ),
        kind=ArticulationType.REVOLUTE,
        limits=MotionLimits(lower=-math.pi, upper=math.pi, effort=16.0, velocity=8.0),
        meta={"mechanism": "end clamp tightening screw"},
    )


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_picturex_0611_flaring_tool_with_cone_and_clamp(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_flaring_tool_with_cone_and_clamp",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/flaring_tool_with_cone_and_clamp",
        },
    )
    mats = _materials(model, r)

    bar, jaw, clamp_screw = _END_CLAMP_BUILDERS[r.end_clamp](model, r, mats, assets)
    yoke = _YOKE_FRAME_BUILDERS[r.yoke_frame](model, r, mats, assets)
    feed_screw = _build_feed_screw(model, r, mats, assets)
    cone = _build_cone(model, r, mats)
    lock = _build_yoke_lock(model, r, mats, assets)

    jaw_joint = _add_jaw_pivot(model, r, bar, jaw)
    mount_joint = _YOKE_MOUNT_BUILDERS[r.yoke_mount](model, r, bar, yoke)
    feed_joint = _add_feed_joint(model, r, yoke, feed_screw)
    cone_joint = _add_cone_joint(model, r, yoke, cone)
    lock_joint = _add_lock_joint(model, r, yoke, lock)
    clamp_joint = (
        _add_clamp_screw_joint(model, r, bar, clamp_screw) if clamp_screw is not None else None
    )

    mount_lo = r.yoke_travel_lo if r.yoke_mount == "sliding" else -r.yoke_pivot_span
    mount_hi = r.yoke_travel_hi if r.yoke_mount == "sliding" else r.yoke_pivot_span

    # Coupled extremes the automatic pair budget would not necessarily reach:
    # a fully open clamp against a fully advanced cone, at both yoke extremes.
    risk: list[dict[str, float]] = [
        {cone_joint: r.cone_stroke, jaw_joint: r.jaw_open},
        {cone_joint: r.cone_stroke, jaw_joint: r.jaw_open, mount_joint: mount_lo},
        {cone_joint: r.cone_stroke, jaw_joint: r.jaw_open, mount_joint: mount_hi},
        {cone_joint: r.cone_stroke, mount_joint: mount_lo, feed_joint: math.pi},
        {cone_joint: r.cone_stroke, mount_joint: mount_hi, lock_joint: 0.5 * math.pi},
        {
            cone_joint: 0.5 * r.cone_stroke,
            mount_joint: 0.5 * (mount_lo + mount_hi),
            jaw_joint: 0.5 * r.jaw_open,
        },
        {cone_joint: r.cone_stroke, jaw_joint: 0.02 * r.jaw_open},
    ]
    if clamp_joint is not None:
        risk.append({clamp_joint: math.pi, jaw_joint: r.jaw_open, cone_joint: r.cone_stroke})
        risk.append({clamp_joint: -0.5 * math.pi, mount_joint: mount_hi})
    model.meta["risk_poses"] = tuple(risk)
    model.meta["coupled_joint_pairs"] = (
        (cone_joint, jaw_joint),
        (cone_joint, mount_joint),
        (jaw_joint, mount_joint),
    )
    model.meta["assembly_dimensions"] = {
        "bar_length": r.bar_length,
        "cone_stroke": r.cone_stroke,
        "cone_radius_at_bar_top": r.cone_radius_at_height(_CONE_PENETRATION),
        "groove_half_width": _GROOVE_HALF,
        "yoke_travel": (r.yoke_travel_lo, r.yoke_travel_hi),
    }
    return model


def build_seeded_picturex_0611_flaring_tool_with_cone_and_clamp(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_flaring_tool_with_cone_and_clamp(
        config_from_seed(seed), assets=assets
    )


# ---------------------------------------------------------------------------
# Author tests -- category invariants only, and deliberately MESH FREE.
# (No expect_overlap / expect_contact / mesh-element AABB: preflight intercepts
# mesh materialization, so any whole-model AABB cache would abort the probe.)
# Exact collision, isolated geometry and sampled-pose QC belong to the harness.
# ---------------------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def _joint(model: ArticulatedObject, name: str):
    return next((j for j in model.articulations if j.name == name), None)


def _elem_names(part) -> set[str]:
    return {v.name or "" for v in part.visuals}


def run_picturex_0611_flaring_tool_with_cone_and_clamp_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    bars = _parts_by_role(object_model, "clamp_bar")
    jaws = _parts_by_role(object_model, "moving_jaw")
    yokes = _parts_by_role(object_model, "yoke")
    screws = _parts_by_role(object_model, "feed_screw")
    cones = _parts_by_role(object_model, "flaring_cone")
    locks = _parts_by_role(object_model, "yoke_lock")
    clamps = _parts_by_role(object_model, "clamp_screw")

    jaw_joint = _joint(object_model, f"end_clamp__{r.end_clamp}__jaw_pivot")
    feed_joint = _joint(object_model, "feed_screw_turn")
    cone_joint = _joint(object_model, "cone_feed")
    lock_joint = _joint(object_model, "yoke_lock_turn")

    ctx.check(
        "category_anchor: flaring tool core mechanism",
        len(bars) == 1
        and len(jaws) == 1
        and len(yokes) == 1
        and len(screws) == 1
        and len(cones) == 1
        and len(locks) == 1
        and jaw_joint is not None
        and jaw_joint.articulation_type == ArticulationType.REVOLUTE
        and lock_joint is not None
        and lock_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(v, 6) for v in lock_joint.axis) == (0.0, 1.0, 0.0),
        details=(
            f"bars={len(bars)} jaws={len(jaws)} yokes={len(yokes)} screws={len(screws)} "
            f"cones={len(cones)} locks={len(locks)}"
        ),
    )

    # --- the screw-fed cone rides the TRUE spindle axis ---------------------
    spindle_ok = (
        feed_joint is not None
        and cone_joint is not None
        and feed_joint.articulation_type == ArticulationType.REVOLUTE
        and cone_joint.articulation_type == ArticulationType.PRISMATIC
        and tuple(round(v, 6) for v in feed_joint.axis) == (0.0, 0.0, 1.0)
        and tuple(round(v, 6) for v in cone_joint.axis) == (0.0, 0.0, -1.0)
        # both frames on the same vertical line: the cone is fed along the
        # spindle, never along a surface tangent
        and abs(feed_joint.origin.xyz[0] - cone_joint.origin.xyz[0]) < 1e-9
        and abs(feed_joint.origin.xyz[1] - cone_joint.origin.xyz[1]) < 1e-9
        and cone_joint.motion_limits is not None
        and math.isclose(cone_joint.motion_limits.upper, r.cone_stroke, rel_tol=1e-9)
        and math.isclose(cone_joint.motion_limits.lower, 0.0, abs_tol=1e-12)
    )
    tip_retracted = _CONE_RETRACT
    tip_advanced = _CONE_RETRACT - r.cone_stroke
    radius_at_bar_top = r.cone_radius_at_height(_CONE_PENETRATION)
    ctx.check(
        "category_anchor: screw-fed cone on the spindle axis",
        spindle_ok
        and tip_retracted > 0.005
        and math.isclose(tip_advanced, -_CONE_PENETRATION, abs_tol=1e-12)
        and _CONE_PENETRATION > 0.002
        # real radial clearance inside the seat/groove at full advance
        and radius_at_bar_top + _FIT <= _GROOVE_HALF
        and _GROOVE_HALF < min(r.hole_radii)
        and r.cone_tip_clearance >= 0.0008
        # and a real motion envelope through the yoke
        and _CONE_MAX_R + 0.002 <= _BORE_WIDE_R,
        details=(
            f"spindle_ok={spindle_ok} tip_retracted={tip_retracted:.4f} "
            f"tip_advanced={tip_advanced:.4f} r_at_top={radius_at_bar_top:.5f} "
            f"groove_half={_GROOVE_HALF} floor_clearance={r.cone_tip_clearance:.5f}"
        ),
    )

    # --- clamp bar with real, progressively sized tube seats ----------------
    bar = bars[0] if bars else None
    bar_elems = _elem_names(bar) if bar is not None else set()
    markers = sorted(n for n in bar_elems if "hole_size_marker_" in n)
    diameters = tuple(2.0 * v for v in r.hole_radii)
    ctx.check(
        "category_anchor: clamp bar with sized tube holes",
        bar is not None
        and len(r.hole_xs) == r.tube_hole_count
        and len(markers) == r.tube_hole_count
        and all(m.startswith(f"end_clamp__{r.end_clamp}__") for m in markers)
        and all(diameters[i] < diameters[i + 1] for i in range(r.tube_hole_count - 1))
        and all(
            math.isclose(r.hole_xs[i + 1] - r.hole_xs[i], r.bar_pitch_m, abs_tol=1e-9)
            for i in range(r.tube_hole_count - 1)
        )
        and math.isclose(r.hole_xs[r.working_index], 0.0, abs_tol=1e-12)
        # each seat plus its counterbore stays inside the bar's half width and
        # the whole row stays inside the bar's ends
        and max(r.hole_radii) * _CBORE_RATIO + 0.002 < r.bar_width
        and r.bar_x_lo < r.hole_xs[0] - max(r.hole_radii)
        and r.bar_x_hi > r.hole_xs[-1] + max(r.hole_radii),
        details=f"n={r.tube_hole_count} markers={len(markers)} pitch={r.bar_pitch_m} d={diameters}",
    )

    # --- end_clamp identity -------------------------------------------------
    if r.end_clamp == "plain_hinge":
        ctx.check(
            "category_anchor: plain_hinge identity",
            not clamps
            and _joint(object_model, "end_clamp__screw_clamp__clamp_rotation") is None
            and "end_clamp__plain_hinge__pin_retainer" in bar_elems
            and {"hinge_pin", "hinge_knuckle_lower", "hinge_knuckle_upper"} <= bar_elems,
            details=f"clamp_screws={len(clamps)} elems={sorted(bar_elems)}",
        )
    else:
        clamp_joint = _joint(object_model, "end_clamp__screw_clamp__clamp_rotation")
        clamp_elems = _elem_names(clamps[0]) if clamps else set()
        ctx.check(
            "category_anchor: screw_clamp identity",
            len(clamps) == 1
            and clamp_joint is not None
            and clamp_joint.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(v, 6) for v in clamp_joint.axis) == (0.0, 0.0, 1.0)
            and "end_clamp__screw_clamp__clamp_stem" in clamp_elems
            and "end_clamp__screw_clamp__clamp_flange" in clamp_elems
            and "end_clamp__screw_clamp__clamp_hub" in clamp_elems
            # the end screw clears the moving jaw's tip entirely and stays out
            # of the yoke's outermost travel position
            and r.clamp_screw_x > r.moving_x_hi + 0.010
            and r.end_margin - _LEG_OUTER_X > 0.019
            and _CLAMP_FLANGE_R < 0.5 * r.bar_width + abs(r.clamp_screw_y),
            details=(
                f"clamps={len(clamps)} screw_x={r.clamp_screw_x:.4f} "
                f"jaw_tip={r.moving_x_hi:.4f} margin={r.end_margin:.4f}"
            ),
        )

    # --- yoke_mount identity + motion envelope ------------------------------
    if r.yoke_mount == "sliding":
        slide = _joint(object_model, "yoke_mount__sliding__yoke_slide")
        ctx.check(
            "category_anchor: sliding yoke mount",
            slide is not None
            and slide.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(v, 6) for v in slide.axis) == (1.0, 0.0, 0.0)
            and slide.motion_limits is not None
            and math.isclose(slide.motion_limits.lower, r.hole_xs[0], abs_tol=1e-12)
            and math.isclose(slide.motion_limits.upper, r.hole_xs[-1], abs_tol=1e-12)
            and slide.motion_limits.upper > slide.motion_limits.lower
            # the carriage stays on the bar and inside the flare groove at both
            # ends of travel, so the cone always has somewhere to descend
            and r.hole_xs[0] - _LEG_OUTER_X > r.bar_x_lo
            and r.hole_xs[-1] + _LEG_OUTER_X < r.bar_x_hi
            and r.groove_x_lo <= r.hole_xs[0]
            and r.groove_x_hi >= r.hole_xs[-1],
            details=(
                f"travel=({r.yoke_travel_lo:.4f},{r.yoke_travel_hi:.4f}) "
                f"bar=({r.bar_x_lo:.4f},{r.bar_x_hi:.4f})"
            ),
        )
    else:
        pivot = _joint(object_model, "yoke_mount__pivoting__yoke_pivot")
        ctx.check(
            "category_anchor: pivoting yoke mount",
            pivot is not None
            and pivot.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(v, 6) for v in pivot.axis) == (0.0, 0.0, 1.0)
            and abs(pivot.origin.xyz[0]) < 1e-12
            and abs(pivot.origin.xyz[1]) < 1e-12
            and pivot.motion_limits is not None
            and math.isclose(pivot.motion_limits.upper, r.yoke_pivot_span, abs_tol=1e-12)
            # the swing axis IS the spindle axis, so the cone never leaves the
            # working seat however far the yoke is swung
            and cone_joint is not None
            and abs(cone_joint.origin.xyz[0]) < 1e-12
            and abs(cone_joint.origin.xyz[1]) < 1e-12,
            details=f"span=+-{r.yoke_pivot_span}",
        )

    # --- yoke_frame identity ------------------------------------------------
    yoke = yokes[0] if yokes else None
    yoke_elems = _elem_names(yoke) if yoke is not None else set()
    guide_pads = sorted(n for n in yoke_elems if n.startswith("cone_guide_pad_"))
    frame_elem = f"yoke_frame__{r.yoke_frame}__cast_frame"
    frame_ok = (
        yoke is not None
        and frame_elem in yoke_elems
        and len(guide_pads) == 4
        # the guide pads capture the shank across the WHOLE stroke: shoulder
        # stays below them retracted, shank top stays above them advanced
        and (_CONE_SHANK_Z + _CONE_RETRACT) <= (_GUIDE_DZ - _DETENT_R - 0.001)
        and (_CONE_TOP_Z + _CONE_RETRACT - r.cone_stroke) >= (_GUIDE_DZ + _DETENT_R + 0.001)
        and math.isclose(_CONE_SHANK_R - (_DETENT_DC - _DETENT_R), _MOUNT, abs_tol=1e-12)
        # legs straddle the cone envelope in X and seat on the bar's top face
        and _LEG_INNER_X > _CONE_MAX_R + 0.006
        and _LEG_OUTER_X > _LEG_INNER_X
    )
    if r.yoke_frame == "inverted_u_cast":
        ctx.check(
            "category_anchor: inverted_u_cast frame", frame_ok, details=f"elems={sorted(yoke_elems)}"
        )
    else:
        ctx.check(
            "category_anchor: twin_cheek_cast frame", frame_ok, details=f"elems={sorted(yoke_elems)}"
        )

    # --- handle_style identity ----------------------------------------------
    screw_elems = _elem_names(screws[0]) if screws else set()
    lock_elems = _elem_names(locks[0]) if locks else set()
    if r.handle_style == "tommy_bar":
        ctx.check(
            "category_anchor: tommy_bar handles",
            "handle_style__tommy_bar__feed_tommy_bar" in screw_elems
            and sum(1 for n in screw_elems if "feed_bar_stop_" in n) == 2
            and "handle_style__tommy_bar__lock_tommy_bar" in lock_elems
            and sum(1 for n in lock_elems if "lock_bar_stop_" in n) == 2,
            details=f"screw={sorted(screw_elems)} lock={sorted(lock_elems)}",
        )
    else:
        ctx.check(
            "category_anchor: wing_handle handles",
            "handle_style__wing_handle__feed_wing" in screw_elems
            and "handle_style__wing_handle__feed_rivet" in screw_elems
            and "handle_style__wing_handle__lock_wing" in lock_elems,
            details=f"screw={sorted(screw_elems)} lock={sorted(lock_elems)}",
        )

    # --- measured motion semantics (mesh free) ------------------------------
    if jaws and jaw_joint is not None:
        rib = f"end_clamp__{r.end_clamp}__jaw_grip_rib"
        closed = ctx.part_element_world_aabb(jaws[0], elem=rib)
        with ctx.pose({jaw_joint: r.jaw_open}):
            opened = ctx.part_element_world_aabb(jaws[0], elem=rib)
        ctx.check(
            "moving jaw swings AWAY from the fixed half on +q",
            closed is not None
            and opened is not None
            # +q must lift the whole free end into +Y, never back through the
            # fixed half at y<0
            and opened[0][1] > closed[0][1] + 0.010
            and opened[0][1] > 0.0,
            details=f"closed={closed}, open={opened}",
        )
    if cones and cone_joint is not None:
        rest = ctx.part_world_position(cones[0])
        with ctx.pose({cone_joint: r.cone_stroke}):
            fed = ctx.part_world_position(cones[0])
        ctx.check(
            "cone advances down the spindle axis only",
            rest is not None
            and fed is not None
            and abs(fed[0] - rest[0]) < 1e-9
            and abs(fed[1] - rest[1]) < 1e-9
            and math.isclose(rest[2] - fed[2], r.cone_stroke, abs_tol=1e-9),
            details=f"rest={rest}, fed={fed}",
        )
    if locks and lock_joint is not None:
        rest = ctx.part_element_world_aabb(locks[0], elem="lock_hub")
        with ctx.pose({lock_joint: 0.5 * math.pi}):
            turned = ctx.part_element_world_aabb(locks[0], elem="lock_hub")
        ctx.check(
            "yoke lock turns about its own transverse (Y) axis",
            rest is not None
            and turned is not None
            and abs((rest[1][1] - rest[0][1]) - (turned[1][1] - turned[0][1])) < 1e-6,
            details=f"rest={rest}, turned={turned}",
        )

    # --- derived clearance invariants (pure arithmetic, no geometry) --------
    ctx.check(
        "yoke bridges the seat on real 0.6 mm captured seating",
        _MOUNT < 0.001
        and 0.0 < r.yoke_half_span_y < r.bar_width
        and _BORE_THREAD_DZ < _COLLAR_TOP_DZ
        and _GUIDE_DZ < _BORE_THREAD_DZ,
        details=f"mount={_MOUNT} span={r.yoke_half_span_y:.4f} width={r.bar_width:.4f}",
    )
    ctx.check(
        "hinge barrel clears the pin and is captured between both knuckles",
        _KNUCKLE_BORE_R - _HINGE_PIN_R >= _FIT - 1e-12
        and _KNUCKLE_R > _KNUCKLE_BORE_R + 0.004
        and r.bar_height - 2.0 * _KNUCKLE_END > 0.004
        and r.moving_x_lo > r.hinge_x + _KNUCKLE_R + 0.001,
        details=f"bore={_KNUCKLE_BORE_R} pin={_HINGE_PIN_R} h={r.bar_height:.4f}",
    )
    ctx.check(
        "yoke lock, feed screw and end screw run in real bores, not press fits",
        _LOCK_BORE_R - _LOCK_STEM_R >= _FIT - 1e-12
        and math.isclose((_LOCK_DETENT_DC + _LOCK_DETENT_R) - _LOCK_BORE_R, _MOUNT, abs_tol=1e-12)
        and _BORE_THREAD_R - _FEED_SHAFT_R >= _FIT - 1e-12
        and _CLAMP_BORE_R - _CLAMP_STEM_R >= _FIT - 1e-12,
    )
    ctx.check(
        "domain choices are recorded on the model",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
    )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ---------------------------------------------------------------------------
# High-risk corners: cone retracted vs advanced, clamp open vs closed and the
# coupled extremes (open clamp + advanced cone at both yoke travel limits) are
# declared as risk_poses on every model; these corners pin the slot/parameter
# combinations those poses are hardest in.
# ---------------------------------------------------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "max_row_sliding_open_clamp_advanced_cone",
        {
            "handle_style": "tommy_bar",
            "yoke_frame": "inverted_u_cast",
            "yoke_mount": "sliding",
            "end_clamp": "screw_clamp",
            "tube_hole_count": 7,
            "bar_pitch_m": _PITCH_MAX,
            "bar_width_m": _WIDTH_MAX,
            "bar_height_m": _HEIGHT_MAX,
        },
        reason="longest seat row, widest yoke, end screw and full cone stroke together",
    ),
    corner_case(
        "min_row_pivoting_shallow_bar",
        {
            "handle_style": "wing_handle",
            "yoke_frame": "twin_cheek_cast",
            "yoke_mount": "pivoting",
            "end_clamp": "plain_hinge",
            "tube_hole_count": 4,
            "bar_pitch_m": _PITCH_MIN,
            "bar_width_m": _WIDTH_MIN,
            "bar_height_m": _HEIGHT_MIN,
        },
        reason="shallowest bar: flare groove, hinge knuckles and cone stroke are tightest here",
    ),
    corner_case(
        "shallow_bar_sliding_wing_screw_clamp",
        {
            "handle_style": "wing_handle",
            "yoke_frame": "inverted_u_cast",
            "yoke_mount": "sliding",
            "end_clamp": "screw_clamp",
            "tube_hole_count": 7,
            "bar_pitch_m": _PITCH_MIN,
            "bar_width_m": _WIDTH_MIN,
            "bar_height_m": _HEIGHT_MIN,
        },
        reason="longest row on the shortest pitch: yoke travel, end screw and lock envelopes crowd",
    ),
    corner_case(
        "deep_bar_pivoting_tommy_screw_clamp",
        {
            "handle_style": "tommy_bar",
            "yoke_frame": "twin_cheek_cast",
            "yoke_mount": "pivoting",
            "end_clamp": "screw_clamp",
            "tube_hole_count": 4,
            "bar_pitch_m": _PITCH_MAX,
            "bar_width_m": _WIDTH_MIN,
            "bar_height_m": _HEIGHT_MAX,
        },
        reason="narrow but deep bar with a swung yoke and a rotating end screw",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_flaring_tool_with_cone_and_clamp",
    "build_seeded_picturex_0611_flaring_tool_with_cone_and_clamp",
    "run_picturex_0611_flaring_tool_with_cone_and_clamp_tests",
]
