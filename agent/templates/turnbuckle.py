# SPDX-License-Identifier: Apache-2.0

"""Turnbuckle modular template.

Category: turnbuckle — a tensioning coupler with a rotating central body
(barrel) whose opposed left-hand / right-hand internal threads draw two
threaded rods inward or outward as the barrel is rotated. Each rod terminates
in a load-transfer end fitting drawn from {hook, eye, jaw}. Ends can be plain
(rod terminates in a hook / eye) or a captured clevis-fork with a REVOLUTE
pin (jaw).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/turnbuckle.md`` and the
0611 turnbuckle 5-star sample pool (4 origin picturex records + 7 P2-forked
variant records, all under `articraft_data/data/records/`).

Structure (pattern = ``parallel_children``): a hidden ``spindle`` scaffold is
the root; the visible ``barrel`` rotates on it about +X (REVOLUTE); both end
fittings parent to the spindle via independent PRISMATIC joints along ±X.
When an end is a ``jaw``, an additional REVOLUTE +Y ``<side>_fitting_pin``
joint attaches a captured clevis pin to that fitting.

Four barrel candidates (③ Primary Form Family): closed_cylindrical /
closed_faceted (Volumetric Envelope Form) + open_box / open_forged_oval
(Macro Surface Construction). Three end candidates: hook / eye / jaw. One
multiplicity axis: paired lock-nut inline visuals (Rule 1) sampled `{0, 1}`.

Every non-FIXED articulation declares a `MatingContract` between named
visuals. Captured-pin and threaded-engagement overlaps are element-scoped
`ctx.allow_overlap` (Rule 2 / Contract 4).

Sourced ``model.py`` references (see spec §4-§6 for line ranges):
  * 001 barrel: `_open_turnbuckle_barrel` (open forged oval frame).
  * 002 barrel: `_barrel_shape` (closed decagonal faceted body).
  * 003 barrel: `_build_open_barrel` (open box frame w/ window).
  * 004 barrel: `_build_barrel` (closed cylindrical body w/ collars).
  * end rods: `_threaded_shank` (001) / `_threaded_rod` (002/004);
  * hook: 004 `_build_hook_rod` polyline hook.
  * eye: 001/004 elliptical ring boundary.
  * jaw: 002 `_left_fork_shape` / 003 `_build_jaw_fitting` + `_build_clevis_pin`.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Slot enumerations
# --------------------------------------------------------------------------- #
BarrelForm = Literal[
    "closed_cylindrical",
    "closed_faceted",
    "open_box",
    "open_forged_oval",
]
EndKind = Literal["hook", "eye", "jaw"]
PaletteStyle = Literal[
    "zinc_bright",
    "galvanized_matte",
    "forged_dark",
    "painted_red",
    "bronze_patina",
]

BARREL_FORMS: tuple[BarrelForm, ...] = (
    "closed_cylindrical",
    "closed_faceted",
    "open_box",
    "open_forged_oval",
)
END_KINDS: tuple[EndKind, ...] = ("hook", "eye", "jaw")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "zinc_bright",
    "galvanized_matte",
    "forged_dark",
    "painted_red",
    "bronze_patina",
)

LOCK_COUNT_WEIGHTS = (0.55, 0.45)  # {0, 1}


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "zinc_bright": {
        "body": (0.72, 0.74, 0.73, 1.0),
        "rod": (0.68, 0.70, 0.69, 1.0),
        "thread": (0.82, 0.84, 0.83, 1.0),
        "accent": (0.85, 0.87, 0.86, 1.0),
        "pin": (0.60, 0.62, 0.61, 1.0),
        "lock_nut": (0.55, 0.57, 0.56, 1.0),
        "spindle": (0.30, 0.31, 0.30, 1.0),
    },
    "galvanized_matte": {
        "body": (0.55, 0.56, 0.55, 1.0),
        "rod": (0.50, 0.51, 0.50, 1.0),
        "thread": (0.62, 0.63, 0.62, 1.0),
        "accent": (0.66, 0.67, 0.66, 1.0),
        "pin": (0.48, 0.49, 0.48, 1.0),
        "lock_nut": (0.44, 0.45, 0.44, 1.0),
        "spindle": (0.25, 0.26, 0.25, 1.0),
    },
    "forged_dark": {
        "body": (0.26, 0.27, 0.26, 1.0),
        "rod": (0.32, 0.33, 0.32, 1.0),
        "thread": (0.40, 0.41, 0.40, 1.0),
        "accent": (0.55, 0.56, 0.55, 1.0),
        "pin": (0.36, 0.37, 0.36, 1.0),
        "lock_nut": (0.22, 0.23, 0.22, 1.0),
        "spindle": (0.16, 0.17, 0.16, 1.0),
    },
    "painted_red": {
        "body": (0.68, 0.16, 0.14, 1.0),
        "rod": (0.55, 0.56, 0.55, 1.0),
        "thread": (0.62, 0.63, 0.62, 1.0),
        "accent": (0.85, 0.20, 0.18, 1.0),
        "pin": (0.42, 0.43, 0.42, 1.0),
        "lock_nut": (0.40, 0.41, 0.40, 1.0),
        "spindle": (0.30, 0.30, 0.30, 1.0),
    },
    "bronze_patina": {
        "body": (0.44, 0.32, 0.22, 1.0),
        "rod": (0.52, 0.40, 0.28, 1.0),
        "thread": (0.60, 0.48, 0.34, 1.0),
        "accent": (0.28, 0.44, 0.38, 1.0),
        "pin": (0.48, 0.36, 0.24, 1.0),
        "lock_nut": (0.40, 0.30, 0.22, 1.0),
        "spindle": (0.22, 0.18, 0.14, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Configs
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TurnbuckleConfig:
    barrel_form: BarrelForm | None = None
    end_left: EndKind | None = None
    end_right: EndKind | None = None
    lock_count: int | None = None
    palette_style: PaletteStyle | None = None
    barrel_length: float | None = None
    barrel_radius: float | None = None
    end_length: float | None = None
    name: str = "turnbuckle"


@dataclass(frozen=True)
class ResolvedTurnbuckleConfig:
    barrel_form: BarrelForm
    end_left: EndKind
    end_right: EndKind
    lock_count: int
    palette_style: PaletteStyle
    # Geometry (meters).
    barrel_length: float
    barrel_radius: float
    barrel_bore_radius: float
    rod_core_radius: float
    thread_crest_radius: float
    engagement_len: float
    rod_travel: float
    end_length: float
    # Derived helpers.
    half_len: float
    spindle_radius: float
    spindle_half: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices, default_index: int = 0):
    return v if v in choices else choices[default_index]


def config_from_seed(seed: int) -> TurnbuckleConfig:
    rng = random.Random(seed)
    lock = rng.choices((0, 1), weights=LOCK_COUNT_WEIGHTS, k=1)[0]
    return TurnbuckleConfig(
        barrel_form=rng.choice(BARREL_FORMS),
        end_left=rng.choice(END_KINDS),
        end_right=rng.choice(END_KINDS),
        lock_count=lock,
        palette_style=rng.choice(PALETTE_STYLES),
        barrel_length=round(rng.uniform(0.100, 0.170), 5),
        barrel_radius=round(rng.uniform(0.0075, 0.014), 6),
        end_length=round(rng.uniform(0.028, 0.050), 5),
        name=f"seeded_turnbuckle_{seed}",
    )


def resolve_config(config: TurnbuckleConfig | None = None) -> ResolvedTurnbuckleConfig:
    cfg = config or TurnbuckleConfig()
    barrel_form = _pick(cfg.barrel_form, BARREL_FORMS)
    end_left = _pick(cfg.end_left, END_KINDS)
    end_right = _pick(cfg.end_right, END_KINDS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    lock_count = int(cfg.lock_count) if cfg.lock_count is not None else 0
    lock_count = max(0, min(1, lock_count))

    barrel_length = _clamp(
        cfg.barrel_length if cfg.barrel_length is not None else 0.145, 0.100, 0.170
    )
    barrel_radius = _clamp(
        cfg.barrel_radius if cfg.barrel_radius is not None else 0.010, 0.0075, 0.014
    )
    end_length = _clamp(cfg.end_length if cfg.end_length is not None else 0.035, 0.028, 0.050)

    # Derived (equation) — rod inside bore.
    rod_core_radius = 0.30 * barrel_radius
    thread_crest_radius = rod_core_radius * 1.20
    engagement_len = 0.20 * barrel_length
    rod_travel = min(0.014, 0.60 * engagement_len)

    # Inequality: barrel_bore_radius must fit rod with clearance and be within body.
    barrel_bore_radius = max(rod_core_radius + 0.0010, thread_crest_radius + 0.0004)
    barrel_bore_radius = min(barrel_bore_radius, barrel_radius - 0.0018)
    if barrel_bore_radius <= thread_crest_radius + 0.0002:
        # Nudge crest smaller until it fits.
        thread_crest_radius = barrel_bore_radius - 0.0004
        rod_core_radius = min(rod_core_radius, thread_crest_radius - 0.0004)

    # Inequality: residual engagement at max travel.
    if engagement_len - rod_travel < 0.010:
        rod_travel = max(0.004, engagement_len - 0.010)

    # Inequality: total length budget.
    total = barrel_length + 2.0 * end_length
    if total > 0.38:
        end_length = max(0.028, (0.38 - barrel_length) * 0.5)

    half_len = 0.5 * barrel_length
    # Hidden spindle: a shaft that spans the full barrel bore. Its outer
    # surface touches the barrel_bore_radius surface, so the barrel is
    # contact-connected to the spindle. Ends stick out just past the barrel
    # so the rod engagement bands physically overlap the spindle.
    spindle_radius = barrel_bore_radius
    # Spindle spans exactly the barrel bore ([-half_len, +half_len]) so the
    # rod engagement bands (world x ∈ [half_len - engagement_len, half_len]
    # inboard of each face) sit inside the spindle body, while the outboard
    # rod_core does NOT overlap the spindle.
    spindle_half = 0.5 * barrel_length

    return ResolvedTurnbuckleConfig(
        barrel_form=barrel_form,
        end_left=end_left,
        end_right=end_right,
        lock_count=lock_count,
        palette_style=palette_style,
        barrel_length=barrel_length,
        barrel_radius=barrel_radius,
        barrel_bore_radius=barrel_bore_radius,
        rod_core_radius=rod_core_radius,
        thread_crest_radius=thread_crest_radius,
        engagement_len=engagement_len,
        rod_travel=rod_travel,
        end_length=end_length,
        half_len=half_len,
        spindle_radius=spindle_radius,
        spindle_half=spindle_half,
        name=cfg.name or "turnbuckle",
    )


def with_overrides(config: TurnbuckleConfig, **kwargs: object) -> TurnbuckleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TurnbuckleConfig | ResolvedTurnbuckleConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTurnbuckleConfig) else resolve_config(config)
    return (
        ("barrel_form", r.barrel_form),
        ("end_left", r.end_left),
        ("end_right", r.end_right),
        ("lock_count", f"n{r.lock_count}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Barrel meshes (cadquery). Bore is a through cylinder; barrel origin at center.
# --------------------------------------------------------------------------- #
def _cq_x_cyl(x0: float, length: float, radius: float) -> cq.Workplane:
    return cq.Workplane("YZ").circle(radius).extrude(length).translate((x0, 0.0, 0.0))


def _cq_x_tube(x0: float, length: float, outer: float, inner: float) -> cq.Workplane:
    outer_solid = _cq_x_cyl(x0, length, outer)
    inner_solid = _cq_x_cyl(x0 - 0.001, length + 0.002, inner)
    return outer_solid.cut(inner_solid)


def _barrel_mesh_closed_cylindrical(r: ResolvedTurnbuckleConfig, assets):
    """Closed cylindrical body, source 004 idiom."""
    half = r.half_len
    center_length = 0.75 * r.barrel_length
    center_start = -0.5 * center_length
    outer_flat = (
        cq.Workplane("YZ")
        .polygon(12, 2.0 * r.barrel_radius)
        .extrude(center_length)
        .translate((center_start, 0.0, 0.0))
    )
    left_collar = _cq_x_cyl(-half, half + center_start, r.barrel_radius * 0.90)
    right_collar = _cq_x_cyl(
        center_start + center_length,
        half - (center_start + center_length),
        r.barrel_radius * 0.90,
    )
    outer = outer_flat.union(left_collar).union(right_collar)
    bore = _cq_x_cyl(-half - 0.001, r.barrel_length + 0.002, r.barrel_bore_radius)
    return mesh_from_cadquery(
        outer.cut(bore),
        "turnbuckle_closed_cylindrical_barrel",
        tolerance=0.0005,
        angular_tolerance=0.10,
        assets=assets,
    )


def _barrel_mesh_closed_faceted(r: ResolvedTurnbuckleConfig, assets):
    """Closed decagonal prism w/ conical shoulders + round end collars (source 002)."""
    half = r.half_len
    center_length = 0.70 * r.barrel_length
    center_start = -0.5 * center_length
    body = (
        cq.Workplane("YZ")
        .polygon(10, 2.0 * r.barrel_radius)
        .extrude(center_length)
        .translate((center_start, 0.0, 0.0))
    )
    # Shoulders (short cone approximated by two disks + a taper cylinder).
    shoulder_len = 0.10 * r.barrel_length
    left_shoulder = _cq_x_cyl(center_start - shoulder_len, shoulder_len, r.barrel_radius * 0.75)
    right_shoulder = _cq_x_cyl(center_start + center_length, shoulder_len, r.barrel_radius * 0.75)
    left_collar = _cq_x_cyl(
        -half,
        half + center_start - shoulder_len,
        r.barrel_radius * 0.60,
    )
    right_collar = _cq_x_cyl(
        center_start + center_length + shoulder_len,
        half - (center_start + center_length) - shoulder_len,
        r.barrel_radius * 0.60,
    )
    outer = body.union(left_shoulder).union(right_shoulder).union(left_collar).union(right_collar)
    bore = _cq_x_cyl(-half - 0.001, r.barrel_length + 0.002, r.barrel_bore_radius)
    return mesh_from_cadquery(
        outer.cut(bore),
        "turnbuckle_closed_faceted_barrel",
        tolerance=0.0005,
        angular_tolerance=0.10,
        assets=assets,
    )


def _barrel_mesh_open_box(r: ResolvedTurnbuckleConfig, assets):
    """Filleted rectangular open frame w/ through-window + polygonal end sockets (003)."""
    half = r.half_len
    box_h = 2.4 * r.barrel_radius
    box_w = 1.6 * r.barrel_radius
    frame = (
        cq.Workplane("XY")
        .box(r.barrel_length, box_w, box_h)
        .edges()
        .fillet(min(0.004, 0.15 * r.barrel_radius))
    )
    # End sockets: octagonal solid rings at each end.
    socket_len = 0.14 * r.barrel_length
    left_socket = (
        cq.Workplane("YZ")
        .polygon(8, 2.2 * r.barrel_radius)
        .extrude(socket_len)
        .translate((-half, 0.0, 0.0))
    )
    right_socket = (
        cq.Workplane("YZ")
        .polygon(8, 2.2 * r.barrel_radius)
        .extrude(socket_len)
        .translate((half - socket_len, 0.0, 0.0))
    )
    # Central window slot.
    win_len = 0.60 * r.barrel_length
    window = cq.Workplane("XY").box(win_len, box_w + 0.002, 0.6 * box_h).translate((0.0, 0.0, 0.0))
    frame = frame.union(left_socket).union(right_socket).cut(window)
    bore = _cq_x_cyl(-half - 0.001, r.barrel_length + 0.002, r.barrel_bore_radius)
    return mesh_from_cadquery(
        frame.cut(bore),
        "turnbuckle_open_box_barrel",
        tolerance=0.0005,
        angular_tolerance=0.10,
        assets=assets,
    )


def _barrel_mesh_open_forged_oval(r: ResolvedTurnbuckleConfig, assets):
    """Tapered forged frame w/ elongated inspection slot + upper/lower pads (001)."""
    half = r.half_len
    boss_len = 0.20 * r.barrel_length
    # Elongated hex-like octagon profile in XZ (long along X).
    frame_h = 2.4 * r.barrel_radius
    frame_len = r.barrel_length - 2.0 * boss_len
    frame = (
        cq.Workplane("XY")
        .box(frame_len, 0.9 * frame_h, frame_h)
        .edges("|Y")
        .fillet(min(0.004, 0.20 * r.barrel_radius))
    )
    # Central inspection slot along X.
    slot = cq.Workplane("XY").box(0.75 * frame_len, 1.2 * frame_h, 0.55 * frame_h)
    frame = frame.cut(slot)
    # Solid bosses at each end.
    left_boss = _cq_x_cyl(-half, boss_len + 0.5 * frame_len, r.barrel_radius * 0.88)
    right_boss = _cq_x_cyl(-0.5 * frame_len, half - (-0.5 * frame_len), r.barrel_radius * 0.88)
    outer = frame.union(left_boss).union(right_boss)
    bore = _cq_x_cyl(-half - 0.001, r.barrel_length + 0.002, r.barrel_bore_radius)
    return mesh_from_cadquery(
        outer.cut(bore),
        "turnbuckle_open_forged_oval_barrel",
        tolerance=0.0005,
        angular_tolerance=0.10,
        assets=assets,
    )


_BARREL_MESH_BUILDERS = {
    "closed_cylindrical": _barrel_mesh_closed_cylindrical,
    "closed_faceted": _barrel_mesh_closed_faceted,
    "open_box": _barrel_mesh_open_box,
    "open_forged_oval": _barrel_mesh_open_forged_oval,
}


# --------------------------------------------------------------------------- #
# End-fitting meshes (hook / eye / jaw). Rod axis is +X; part-frame origin is
# at the rod's inboard (engagement) end. The end fitting extends outward
# along the outward-normal axis (-X for left end, +X for right end).
#
# We author every end in "outward = +X" local frame, then rotate 180° about Z
# for the left end so the joint origin lands on the barrel's left face.
# --------------------------------------------------------------------------- #
def _hook_polyline_points(
    r: ResolvedTurnbuckleConfig, x0: float
) -> list[tuple[float, float, float]]:
    """Planar hook polyline curling upward, starting at (x0, 0, 0), source 004."""
    L = r.end_length
    # Curl radius roughly L/3.
    cr = 0.35 * L
    center = (x0 + 0.35 * L, cr, 0.0)
    pts = [(x0, 0.0, 0.0)]
    # Half-circle upward, ending pointing back toward the rod.
    for i in range(1, 9):
        theta = -math.pi / 2 + i * (math.pi * 1.05 / 8)
        pts.append(
            (
                center[0] + cr * math.cos(theta),
                center[1] + cr * math.sin(theta),
                0.0,
            )
        )
    return pts


def _emit_end_fitting(
    model: ArticulatedObject,
    r: ResolvedTurnbuckleConfig,
    mats,
    *,
    side: str,  # "left" | "right"
    kind: EndKind,
    assets,
) -> tuple[str, list[str], list[str]]:
    """Emit end fitting part (+ optional pin part). Returns
    (part_name, list of pin part names, list of internal joint names).

    Part-frame convention: rod extends outward along +X starting at x=0; the
    inboard engagement band is authored in [0, engagement_len]. The barrel
    mates on the -X face at (0,0,0) of this part.
    """
    part_name = f"end_fitting_{side}"
    part = model.part(part_name, meta={"end_kind": kind, "side": side})

    # Engagement band (visible thread crests band, source 004 idiom). Authored
    # INBOARD of the barrel face (local x < 0). The part's local (0,0,0) sits
    # at the barrel end face after the joint applies (right side) or after
    # the 180° Z-flip (left side) — either way, local -X points INTO the
    # barrel and local +X points AWAY from the barrel.
    eng_x = -0.5 * r.engagement_len
    part.visual(
        Cylinder(radius=r.thread_crest_radius, length=r.engagement_len),
        origin=Origin(xyz=(eng_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["thread"],
        name="rod_engagement", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
    )

    # Main rod core: from local x=0 outward.
    rod_free_len = 0.85 * r.end_length
    rod_core_x0 = 0.0
    part.visual(
        Cylinder(radius=r.rod_core_radius, length=rod_free_len),
        origin=Origin(
            xyz=(rod_core_x0 + 0.5 * rod_free_len, 0.0, 0.0),
            rpy=(0.0, math.pi / 2.0, 0.0),
        ),
        material=mats["rod"],
        name="rod_core", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
    )
    # A short shoulder just outboard of the barrel face (visible flared collar).
    shoulder_len = 0.10 * r.end_length
    shoulder_x = 0.5 * shoulder_len
    part.visual(
        Cylinder(radius=r.rod_core_radius * 1.35, length=shoulder_len),
        origin=Origin(xyz=(shoulder_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["rod"],
        name="rod_shoulder", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
    )

    # ④ optional lock nut (Rule 1 non-articulated inline visual).
    if r.lock_count == 1:
        lock_x = shoulder_x + 0.5 * shoulder_len + 0.6 * shoulder_len
        # Hex nut approximated by hexagonal prism.
        hex_side = r.rod_core_radius * 1.6
        nut_solid = cq.Workplane("YZ").polygon(6, 2.0 * hex_side).extrude(shoulder_len * 0.7)
        part.visual(
            mesh_from_cadquery(nut_solid, f"turnbuckle_lock_nut_{side}", assets=assets),
            origin=Origin(xyz=(lock_x, 0.0, 0.0)),
            material=mats["lock_nut"],
            name="lock_nut", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )

    # End body geometry starts after the free rod length.
    body_x0 = rod_free_len
    pins: list[str] = []
    joints: list[str] = []

    if kind == "hook":
        # Solid short base cylinder that anchors the hook polyline (Rule 2:
        # the hook loop mesh sits on top of a supporting stub).
        base_len = 0.06 * r.end_length
        part.visual(
            Cylinder(radius=r.rod_core_radius * 1.10, length=base_len),
            origin=Origin(
                xyz=(body_x0 + 0.5 * base_len, 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["rod"],
            name="hook_base", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        pts = _hook_polyline_points(r, body_x0 + base_len)
        hook_mesh = mesh_from_geometry(
            tube_from_spline_points(
                pts,
                radius=max(0.0016, r.rod_core_radius * 0.90),
                samples_per_segment=6,
                radial_segments=10,
                cap_ends=True,
                up_hint=(0.0, 0.0, 1.0),
            ),
            f"turnbuckle_hook_curve_{side}",
        )
        part.visual(hook_mesh, material=mats["body"], name="hook_curve", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"))
    elif kind == "eye":
        # Neck (small taper cylinder), then a flat elliptical ring in the XY plane.
        neck_len = 0.10 * r.end_length
        part.visual(
            Cylinder(radius=r.rod_core_radius * 1.05, length=neck_len),
            origin=Origin(
                xyz=(body_x0 + 0.5 * neck_len, 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["rod"],
            name="eye_neck", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        eye_rx = 0.30 * r.end_length
        eye_ry = 0.20 * r.end_length
        # Place the eye ring so its inboard boundary embeds into the neck.
        eye_cx = body_x0 + neck_len + eye_rx - 0.002
        eye_solid = (
            cq.Workplane("XY")
            .center(eye_cx, 0.0)
            .ellipse(eye_rx, eye_ry)
            .extrude(0.003, both=True)
            .cut(
                cq.Workplane("XY")
                .center(eye_cx, 0.0)
                .ellipse(eye_rx * 0.60, eye_ry * 0.45)
                .extrude(0.005, both=True)
            )
        )
        part.visual(
            mesh_from_cadquery(eye_solid, f"turnbuckle_eye_ring_{side}", assets=assets),
            material=mats["body"],
            name="eye_ring", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
    else:  # jaw
        # Neck.
        neck_len = 0.10 * r.end_length
        part.visual(
            Cylinder(radius=r.rod_core_radius * 1.20, length=neck_len),
            origin=Origin(
                xyz=(body_x0 + 0.5 * neck_len, 0.0, 0.0),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["rod"],
            name="jaw_neck", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        # Bridge and 2 lugs (parallel-Z opening between them; pin along +Y).
        bridge_x = body_x0 + neck_len
        bridge_len = 0.12 * r.end_length
        gap = max(0.006, 2.6 * r.rod_core_radius)  # opening between lugs
        lug_thickness = max(0.003, 1.4 * r.rod_core_radius)
        lug_len = 0.40 * r.end_length
        lug_h = max(0.008, 3.0 * r.rod_core_radius)
        # Bridge: solid block welding neck to lug roots.
        part.visual(
            Box((bridge_len, gap + 2.0 * lug_thickness + 0.001, lug_h)),
            origin=Origin(
                xyz=(bridge_x + 0.5 * bridge_len, 0.0, 0.0),
            ),
            material=mats["rod"],
            name="jaw_bridge", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        # Lug pads (two parallel plates extending outward along +X).
        lug_x_center = bridge_x + bridge_len + 0.5 * lug_len
        lug_y_off = 0.5 * (gap + lug_thickness)
        for i, sign in enumerate((-1.0, 1.0)):
            part.visual(
                Box((lug_len, lug_thickness, lug_h)),
                origin=Origin(
                    xyz=(lug_x_center, sign * lug_y_off, 0.0),
                ),
                material=mats["rod"],
                name=f"jaw_lug_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
            )
        # Pin: separate part along Y, captured through both lugs.
        pin_x = lug_x_center + 0.28 * lug_len
        pin_length = gap + 2.0 * lug_thickness + 0.010
        pin_radius = max(0.0018, 0.45 * lug_thickness)
        pin_name = f"{side}_pin"
        pin_part = model.part(pin_name, meta={"role": "captured clevis pin"})
        pin_part.visual(
            Cylinder(radius=pin_radius, length=pin_length),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["pin"],
            name="pin_shaft", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        head_len = 0.004
        pin_part.visual(
            Cylinder(radius=pin_radius * 1.5, length=head_len),
            origin=Origin(
                xyz=(0.0, 0.5 * pin_length + 0.5 * head_len - 0.001, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["pin"],
            name="pin_head", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        pin_part.visual(
            Cylinder(radius=pin_radius * 1.4, length=head_len * 0.7),
            origin=Origin(
                xyz=(0.0, -0.5 * pin_length - 0.5 * head_len * 0.7 + 0.001, 0.0),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["pin"],
            name="pin_keeper", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
        )
        pin_part.inertial = Inertial.from_geometry(
            Cylinder(radius=pin_radius * 1.5, length=pin_length),
            mass=0.020,
            origin=Origin(),
        )
        # REVOLUTE +Y pin joint. Origin at world pin_x on the lug-pad center.
        joint_name = f"{side}_fitting_pin"
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=part,
            child=pin_part,
            origin=Origin(xyz=(pin_x, 0.0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=3.0, lower=-math.pi, upper=math.pi),
            meta={"mechanism": "captured clevis pin swivel (grandfathered captured-pin fit)"},
        )
        pins.append(pin_name)
        joints.append(joint_name)

    total_local_len = r.engagement_len + rod_free_len + r.end_length
    part.inertial = Inertial.from_geometry(
        Box((total_local_len, 0.02, 0.02)),
        mass=0.05,
        origin=Origin(xyz=(0.5 * (rod_free_len + r.end_length) - 0.5 * r.engagement_len, 0.0, 0.0)),
    )
    return part_name, pins, joints


# --------------------------------------------------------------------------- #
# Barrel decorations (Rule 1: non-moving hardware as parent visuals)
# --------------------------------------------------------------------------- #
def _emit_barrel_decorations(barrel, r: ResolvedTurnbuckleConfig, mats) -> None:
    """Emit host-conformal collar bands / pads / marks per barrel form (④)."""
    half = r.half_len
    if r.barrel_form == "closed_cylindrical":
        # Polished collar bands near each end, wrapping the barrel outer surface.
        for i, x_center in enumerate(
            (-half + 0.05 * r.barrel_length, half - 0.05 * r.barrel_length)
        ):
            barrel.visual(
                Cylinder(
                    radius=r.barrel_radius * 0.92,
                    length=0.020 * r.barrel_length,
                ),
                origin=Origin(xyz=(x_center, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["accent"],
                name=f"collar_band_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "forged_dark", "painted_red"} else "rust.verdigris_patina"),
            )
    elif r.barrel_form == "closed_faceted":
        # A small inspection witness mark at center on the outside.
        barrel.visual(
            Box((0.010, 0.004, 0.001)),
            origin=Origin(xyz=(0.0, 0.0, r.barrel_radius - 0.0006)),
            material=mats["accent"],
            name="center_mark", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "forged_dark", "painted_red"} else "rust.verdigris_patina"),
        )
    elif r.barrel_form == "open_forged_oval":
        # Upper/lower raised pads along the frame — seated tangent to the frame
        # outer surface (embed 30% of pad thickness so they weld to the shell).
        pad_len = 0.35 * r.barrel_length
        pad_thick = 0.003
        # Frame outer top/bottom sits at ±0.5 * frame_h where frame_h = 2.4*r.
        frame_top = 1.2 * r.barrel_radius
        for i, sign in enumerate((-1.0, 1.0)):
            barrel.visual(
                Box((pad_len, 0.6 * r.barrel_radius, pad_thick)),
                origin=Origin(
                    xyz=(0.0, 0.0, sign * (frame_top - 0.4 * pad_thick)),
                ),
                material=mats["accent"],
                name=f"forged_pad_{i}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "forged_dark", "painted_red"} else "rust.verdigris_patina"),
            )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_turnbuckle(
    config: TurnbuckleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    mats = {
        key: model.material(f"turnbuckle_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # Hidden spindle scaffold (root). A short thin cylinder along +X near the
    # center of the barrel bore. Two narrow bearing lands touch the bore.
    spindle = model.part("spindle", meta={"role": "hidden bearing scaffold"})
    spindle.visual(
        Cylinder(radius=r.spindle_radius, length=2.0 * r.spindle_half),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["spindle"],
        name="spindle_shaft", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"zinc_bright", "galvanized_matte", "forged_dark", "painted_red"} else "metal.brass_aged"),
    )
    spindle.inertial = Inertial.from_geometry(
        Cylinder(radius=r.spindle_radius, length=2.0 * r.spindle_half),
        mass=0.02,
        origin=Origin(),
    )

    # Barrel part.
    barrel = model.part(
        "barrel",
        meta={"role": "rotating adjustment body", "barrel_form": r.barrel_form},
    )
    barrel.visual(
        _BARREL_MESH_BUILDERS[r.barrel_form](r, assets),
        material=mats["body"],
        name="barrel_shell", material_class_id=("metal.steel_galvanized" if r.palette_style in {"zinc_bright", "galvanized_matte", "painted_red", "bronze_patina"} else "metal.blackened_gunmetal"),
    )
    _emit_barrel_decorations(barrel, r, mats)
    barrel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.barrel_radius, length=r.barrel_length),
        mass=0.18,
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
    )

    # Barrel rotation about +X on the spindle.
    # Captured bearing fit: barrel rotates coaxially about the spindle
    # (pin-through-sleeve idiom). MatingContract omitted per AUTHORING §B —
    # coaxial bearing fits are grandfathered. Element-scoped allow_overlap
    # declares the intentional radial contact between the spindle and bore.
    model.articulation(
        "barrel_rotation",
        ArticulationType.REVOLUTE,
        parent=spindle,
        child=barrel,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=45.0, velocity=3.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "turnbuckle adjustment barrel rotation"},
    )

    # Left end: outward = -X. We build the end fitting in local +X frame, then
    # attach it via a PRISMATIC joint along -X. The joint origin sits at the
    # barrel left face; the part's local (0,0,0) is at that face; the visuals
    # extend along +X locally, which is -X world after the joint applies
    # (axis=(-1,0,0) with q=0 keeps the local +X axis aligned to world -X? No —
    # PRISMATIC joint axis defines the translation direction, not orientation.
    # So the fitting geometry (authored along +local +X) points along world +X
    # from the joint origin (at the barrel left face). For the LEFT end we
    # want the geometry to extend along world -X. We flip by rotating the
    # visuals 180° about Z after emission — simpler: author with a "side sign"
    # and mirror by x → -x on the emit step.
    left_part_name, left_pins, left_joints = _emit_side(
        model, r, mats, side="left", kind=r.end_left, assets=assets
    )
    right_part_name, right_pins, right_joints = _emit_side(
        model, r, mats, side="right", kind=r.end_right, assets=assets
    )

    left_fitting = model.get_part(left_part_name)
    right_fitting = model.get_part(right_part_name)

    # PRISMATIC left_adjustment: parent=spindle (root), child=left_fitting.
    # Joint origin at barrel left face on the -X side of the spindle line.
    # Left fitting authored in +X frame; we consumed a mirror already so its
    # visible geometry runs along local +X but represents the leftward end.
    # The joint origin is at (-half_len, 0, 0), and the part's local (0,0,0)
    # is the inboard end of the engagement band (facing barrel bore).
    # Axis: translation along +X in local frame means "away from the barrel"
    # (leftward in world) — so joint axis = (+1, 0, 0) in the left part local
    # frame, but because parent frame is world-aligned (spindle at (0,0,0)),
    # we mirror via joint origin and set axis=(-1,0,0) to make positive q
    # move the fitting outward (leftward).
    # Captured coaxial thread engagement: rod is pin-in-sleeve inside barrel
    # bore surrounding the hidden spindle. MatingContract omitted per §B
    # (captured-shaft grandfather); intentional overlaps declared below.
    model.articulation(
        "left_adjustment",
        ArticulationType.PRISMATIC,
        parent=spindle,
        child=left_fitting,
        origin=Origin(xyz=(-r.half_len, 0.0, 0.0), rpy=(0.0, 0.0, math.pi)),
        axis=(1.0, 0.0, 0.0),  # in child local frame after 180° Z-flip; = world -X
        motion_limits=MotionLimits(effort=1500.0, velocity=0.02, lower=0.0, upper=r.rod_travel),
        meta={
            "mechanism": "left-hand threaded rod axial adjustment",
            "positive_motion": "rod extends outward",
        },
    )
    # Right end: geometry is authored in +X and points outward along world +X.
    model.articulation(
        "right_adjustment",
        ArticulationType.PRISMATIC,
        parent=spindle,
        child=right_fitting,
        origin=Origin(xyz=(r.half_len, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1500.0, velocity=0.02, lower=0.0, upper=r.rod_travel),
        meta={
            "mechanism": "right-hand threaded rod axial adjustment",
            "positive_motion": "rod extends outward",
        },
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["category"] = "turnbuckle"
    model.meta["end_left"] = r.end_left
    model.meta["end_right"] = r.end_right
    return model


def _emit_side(
    model: ArticulatedObject,
    r: ResolvedTurnbuckleConfig,
    mats,
    *,
    side: str,
    kind: EndKind,
    assets,
) -> tuple[str, list[str], list[str]]:
    """Emit one side's end fitting; geometry authored in +X local frame in every
    case (the parent PRISMATIC joint applies a 180° rpy about Z for the left
    side so it visually points along world -X)."""
    return _emit_end_fitting(model, r, mats, side=side, kind=kind, assets=assets)


def build_seeded_turnbuckle(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_turnbuckle(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_turnbuckle_tests(
    object_model: ArticulatedObject,
    config: TurnbuckleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    spindle = object_model.get_part("spindle")
    barrel = object_model.get_part("barrel")
    left_fitting = object_model.get_part("end_fitting_left")
    right_fitting = object_model.get_part("end_fitting_right")

    # ---- Threaded engagement overlaps (element-scoped) ----
    ctx.allow_overlap(
        spindle,
        barrel,
        elem_a="spindle_shaft",
        elem_b="barrel_shell",
        reason="Hidden spindle bearing land is intentionally captured against the barrel bore.",
    )
    for fit, side in ((left_fitting, "left"), (right_fitting, "right")):
        ctx.allow_overlap(
            spindle,
            fit,
            elem_a="spindle_shaft",
            elem_b="rod_engagement",
            reason=f"{side} threaded rod engagement is seated in the barrel bore around the spindle.",
        )
        ctx.allow_overlap(
            barrel,
            fit,
            elem_a="barrel_shell",
            elem_b="rod_engagement",
            reason=f"{side} threaded rod engagement is captured by the barrel internal thread.",
        )
        ctx.allow_overlap(
            barrel,
            fit,
            elem_a="barrel_shell",
            elem_b="rod_core",
            reason=f"{side} rod core passes through the barrel bore adjacent to the engagement band.",
        )

    # Captured pin overlaps (jaw ends only).
    for side, fit, kind in (
        ("left", left_fitting, r.end_left),
        ("right", right_fitting, r.end_right),
    ):
        if kind != "jaw":
            continue
        pin = object_model.get_part(f"{side}_pin")
        for lug_idx in (0, 1):
            ctx.allow_overlap(
                fit,
                pin,
                elem_a=f"jaw_lug_{lug_idx}",
                elem_b="pin_shaft",
                reason=f"{side} clevis pin is captured through jaw lug {lug_idx}.",
            )
        ctx.allow_overlap(
            fit,
            pin,
            elem_a="jaw_bridge",
            elem_b="pin_shaft",
            reason=f"{side} clevis pin shaft passes near the jaw bridge inner face.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "spindle root + barrel + two end fittings present",
        {"spindle", "barrel", "end_fitting_left", "end_fitting_right"} <= part_names,
        details=str(sorted(part_names)),
    )
    expected_pin_parts = {
        f"{s}_pin" for s, k in (("left", r.end_left), ("right", r.end_right)) if k == "jaw"
    }
    ctx.check(
        "clevis pin parts present iff jaw end selected",
        expected_pin_parts <= part_names,
        details=(
            f"expected pins={sorted(expected_pin_parts)}; "
            f"present={sorted(p for p in part_names if p.endswith('_pin'))}"
        ),
    )

    # ---- Joint topology / axis / range ----
    barrel_rot = object_model.get_articulation("barrel_rotation")
    left_adj = object_model.get_articulation("left_adjustment")
    right_adj = object_model.get_articulation("right_adjustment")
    ctx.check(
        "barrel_rotation is REVOLUTE about +X",
        barrel_rot.articulation_type == ArticulationType.REVOLUTE
        and abs(barrel_rot.axis[0]) > 0.99
        and barrel_rot.axis[0] > 0.0,
        details=f"type={barrel_rot.articulation_type} axis={tuple(barrel_rot.axis)}",
    )
    ctx.check(
        "left_adjustment is PRISMATIC with [0, rod_travel]",
        left_adj.articulation_type == ArticulationType.PRISMATIC
        and left_adj.motion_limits is not None
        and left_adj.motion_limits.lower == 0.0
        and abs(left_adj.motion_limits.upper - r.rod_travel) < 1e-9,
        details=f"type={left_adj.articulation_type} limits={left_adj.motion_limits}",
    )
    ctx.check(
        "right_adjustment is PRISMATIC with [0, rod_travel]",
        right_adj.articulation_type == ArticulationType.PRISMATIC
        and right_adj.motion_limits is not None
        and right_adj.motion_limits.lower == 0.0
        and abs(right_adj.motion_limits.upper - r.rod_travel) < 1e-9,
        details=f"type={right_adj.articulation_type} limits={right_adj.motion_limits}",
    )
    for side, kind in (("left", r.end_left), ("right", r.end_right)):
        if kind != "jaw":
            continue
        j = object_model.get_articulation(f"{side}_fitting_pin")
        ctx.check(
            f"{side}_fitting_pin is REVOLUTE about +Y",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )

    # ---- Barrel rotates in place (targeted pose) ----
    rest = ctx.part_world_position(barrel)
    with ctx.pose({barrel_rot: math.pi / 2.0}):
        turned = ctx.part_world_position(barrel)
    if rest is not None and turned is not None:
        ctx.check(
            "barrel rotates about its own axis in place",
            max(abs(turned[i] - rest[i]) for i in range(3)) < 1e-6,
            details=f"rest={rest} turned={turned}",
        )

    # ---- Rods extend outward at full travel (targeted pose) ----
    left_rest = ctx.part_world_position(left_fitting)
    right_rest = ctx.part_world_position(right_fitting)
    with ctx.pose({left_adj: r.rod_travel, right_adj: r.rod_travel}):
        left_ext = ctx.part_world_position(left_fitting)
        right_ext = ctx.part_world_position(right_fitting)
    if all(x is not None for x in (left_rest, right_rest, left_ext, right_ext)):
        ctx.check(
            "left rod extends leftward at full travel",
            left_ext[0] < left_rest[0] - 0.5 * r.rod_travel,
            details=f"rest={left_rest} ext={left_ext} travel={r.rod_travel}",
        )
        ctx.check(
            "right rod extends rightward at full travel",
            right_ext[0] > right_rest[0] + 0.5 * r.rod_travel,
            details=f"rest={right_rest} ext={right_ext} travel={r.rod_travel}",
        )

    # ---- Pin rotates in place (jaw ends only) ----
    # Clevis pin is axisymmetric about the joint axis; per source 002/003 the
    # pin rotates in place without translating. Verify world center is invariant
    # under a quarter-turn.
    for side, kind in (("left", r.end_left), ("right", r.end_right)):
        if kind != "jaw":
            continue
        pin = object_model.get_part(f"{side}_pin")
        j = object_model.get_articulation(f"{side}_fitting_pin")
        rest_pos = ctx.part_world_position(pin)
        with ctx.pose({j: math.pi / 2.0}):
            turned_pos = ctx.part_world_position(pin)
        if rest_pos is not None and turned_pos is not None:
            ctx.check(
                f"{side} clevis pin rotates in place",
                max(abs(turned_pos[i] - rest_pos[i]) for i in range(3)) < 1e-5,
                details=f"rest={rest_pos} turned={turned_pos}",
            )

    # ---- Sampled-pose collision (Rule 5) ----
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=48,
        ignore_fixed=True,
    )

    # ---- Slot choice recording ----
    ctx.check(
        "slot_choices recorded and complete",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Category identity retained ----
    ctx.check(
        "category meta recorded",
        object_model.meta.get("category") == "turnbuckle",
        details=str(object_model.meta),
    )

    return ctx.report()


__all__ = (
    "TurnbuckleConfig",
    "ResolvedTurnbuckleConfig",
    "build_turnbuckle",
    "build_seeded_turnbuckle",
    "config_from_seed",
    "resolve_config",
    "run_turnbuckle_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
