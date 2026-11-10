# SPDX-License-Identifier: Apache-2.0

"""Hole punch procedural template (modular).

A hand tool that perforates paper by driving one or more punch pins straight
through the sheet into matching dies, actuated by a single press/squeeze DOF.

This template is modular (``__modular__ = True``): it derives topology from
per-module 5-star sources declared in
``specs_modular_v1/hole_punch.md``. Two discrete structural slots plus one
multiplicity axis, resolved procedurally per seed:

  Slot A — skeleton (the grounded body + dies + pivot/guide mount hardware):
    * ``desktop_base``  — flat rubber-footed slab, rear-hinge / guide mount,
                          loop-emitted round dies (source B / plunger record).
    * ``plier_frame``   — compact chrome C-frame, central rivet pivot post,
                          two knurled handles (source A, plier).
    * ``cloop_frame``   — compact chrome frame with a continuous bent
                          spring-steel C-loop bridge at the rear
                          (source: skeleton_sprung_loop fork).

  Slot B — actuator (the moving punch carrier chained to the skeleton):
    * ``pivot_lever``   — a lever that pivots (REVOLUTE, axis +Y) and carries
                          the N pins directly (sources A / B / sprung_loop).
    * ``plunger``       — a palm-press head that slides straight down
                          (PRISMATIC, axis -Z) carrying the pin
                          (source: mechanism_plunger fork). desktop, N=1.
    * ``lever_carriage``— compound: REVOLUTE lever + PRISMATIC carriage; pins
                          FIXED to the carriage (source: skeleton_lever_carriage
                          fork). desktop, N in {2,3,4}.

  Multiplicity N — number of punch-pin + matching-die pairs (1..4). The dies
    (skeleton) and pins (actuator) both read the single ``pin_ys`` layout from
    the resolved config, so alignment holds by construction (Contract 3c).

Design-rule compliance (AUTHORING.md §A):
  * Rule 1 — every non-articulating detail (grips, ribs, die rings, screw
    heads, C-loop bridge) is a ``part.visual(...)``, never a FIXED-joint part.
    The only separate parts are the ones that actually move (lever, plunger,
    carriage, pins).
  * Rule 2 — every non-FIXED joint here is a captured mechanical pivot /
    sliding fit (hinge barrel in a hinge block, plunger stem in a column,
    guide posts through carriage bores). Per the Rule-2 grandfather clause
    these omit ``MatingContract`` (their surfaces cannot be two axis-aligned
    faces in contact) and are documented via element-scoped ``allow_overlap``
    in ``run_hole_punch_tests`` — exactly as the 5-star source records and the
    ``monitor_mount`` reference template do.
  * Rule 3 — part trees, joint topology and primitive families are adapted
    from the declared sources; literals are parameterised.
  * Rule 5 — the template has non-FIXED joints, so the tests call
    ``fail_if_parts_overlap_in_sampled_poses(...)`` plus targeted
    ``ctx.pose(...)`` checks proving the punch stroke drives the pins into the
    dies.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

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
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

Skeleton = Literal["desktop_base", "plier_frame", "cloop_frame"]
Mechanism = Literal["pivot_lever", "plunger", "lever_carriage"]
PaletteTheme = Literal[
    "chrome",
    "nickel",
    "gunmetal",
    "office_blue",
    "office_red",
    "graphite",
    "forest_green",
]

_HANDHELD_SKELETONS = frozenset({"plier_frame", "cloop_frame"})
_HANDHELD_THEMES = ("chrome", "nickel", "gunmetal")
_DESKTOP_THEMES = ("office_blue", "office_red", "graphite", "forest_green")


# --------------------------------------------------------------------------- #
# Palette presets (⑥). Every preset provides the same material-name keys so
# module factories can reference them by string regardless of theme.
# --------------------------------------------------------------------------- #
_SHARED = {
    "steel": (0.60, 0.62, 0.66, 1.0),
    "dark_steel": (0.30, 0.30, 0.32, 1.0),
    "black": (0.02, 0.02, 0.02, 1.0),
    "rubber": (0.045, 0.045, 0.045, 1.0),
    "spring": (0.55, 0.55, 0.52, 1.0),
}


def _preset(body, body_hi, body_shadow, grip, **overrides) -> dict:
    p = {
        "body": body,
        "body_hi": body_hi,
        "body_shadow": body_shadow,
        "grip": grip,
        **_SHARED,
    }
    p.update(overrides)
    return p


HOLE_PUNCH_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "chrome": _preset(
        (0.80, 0.82, 0.86, 1.0), (0.88, 0.90, 0.93, 1.0),
        (0.50, 0.52, 0.55, 1.0), (0.42, 0.44, 0.47, 1.0),
    ),
    "nickel": _preset(
        (0.74, 0.72, 0.66, 1.0), (0.84, 0.82, 0.75, 1.0),
        (0.46, 0.45, 0.40, 1.0), (0.40, 0.39, 0.35, 1.0),
    ),
    "gunmetal": _preset(
        (0.34, 0.36, 0.40, 1.0), (0.46, 0.48, 0.52, 1.0),
        (0.18, 0.19, 0.22, 1.0), (0.12, 0.13, 0.15, 1.0),
    ),
    "office_blue": _preset(
        (0.08, 0.24, 0.62, 1.0), (0.12, 0.33, 0.78, 1.0),
        (0.035, 0.09, 0.25, 1.0), (0.06, 0.06, 0.07, 1.0),
    ),
    "office_red": _preset(
        (0.62, 0.11, 0.11, 1.0), (0.80, 0.20, 0.18, 1.0),
        (0.26, 0.04, 0.04, 1.0), (0.07, 0.07, 0.07, 1.0),
    ),
    "graphite": _preset(
        (0.20, 0.21, 0.23, 1.0), (0.30, 0.31, 0.34, 1.0),
        (0.09, 0.09, 0.10, 1.0), (0.05, 0.05, 0.06, 1.0),
    ),
    "forest_green": _preset(
        (0.10, 0.34, 0.20, 1.0), (0.16, 0.46, 0.28, 1.0),
        (0.04, 0.15, 0.09, 1.0), (0.06, 0.07, 0.06, 1.0),
    ),
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class HolePunchConfig:
    skeleton: Skeleton = "desktop_base"
    mechanism: Mechanism = "pivot_lever"
    n_holes: int = 2
    palette_theme: PaletteTheme = "office_blue"

    # Controlled local scales (⑤); all clamped + derived in resolve_config.
    reach_scale: float = 1.0        # throat depth / station-from-pivot distance
    body_height_scale: float = 1.0  # z of die table + pivot
    hole_pitch_scale: float = 1.0   # Y spacing between holes
    handle_len_scale: float = 1.0   # rear/front handle length
    pin_radius_scale: float = 1.0   # punch-pin gauge (die bore derives from it)

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(HOLE_PUNCH_PALETTE_PRESETS["office_blue"])
    )


@dataclass(frozen=True)
class ResolvedHolePunchConfig:
    skeleton: Skeleton
    mechanism: Mechanism
    n_holes: int
    palette_theme: PaletteTheme
    palette: dict[str, tuple[float, float, float, float]]

    # Single-sourced geometric quantities (Contract 3c). Every module reads
    # these; nothing re-derives "the same" number in two places.
    is_handheld: bool
    pin_x: float          # world X of the pin/die station
    pivot_x: float        # world X of the press pivot (pivot_x < pin_x)
    pivot_z: float        # world Z of the pin-mount plane (lever/carriage underside)
    lever_pivot_z: float  # world Z of the revolute lever pivot
    die_top_z: float      # world Z of the die table (paper rests here)
    base_top_z: float     # world Z of the body top surface the dies sit on
    hole_pitch: float
    pin_ys: tuple[float, ...]      # per-hole Y (dies AND pins share this)
    base_y_half: float
    row_half: float
    stroke_upper: float           # revolute press travel (rad)
    slide_travel: float           # prismatic press travel (m)
    handle_len: float
    # pin / die gauge
    pin_body_r: float
    pin_cap_r: float
    pin_tip_r: float
    die_hole_r: float
    die_ring_r: float
    die_boss_r: float


_PAPER_SLOT = 0.003   # rest gap between pin tip and die table
_PIN_HANG = 0.018     # pin-local distance from FIXED joint (cap top) to tip bottom
_PLATE_H = 0.012      # lever plate thickness (Z)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def config_from_seed(seed: int) -> HolePunchConfig:
    """Deterministic procedural sampling. seed 0 is NOT special-cased.

    Compatibility gating lives here (Contract 4 / spec §9): handheld frames are
    single-hole revolute punches; the vertical plunger and the lever+carriage
    mechanisms are desktop-only, and the plunger is single-hole while the
    carriage is a multi-hole office punch.
    """
    rng = random.Random(seed)

    skeleton: Skeleton = _weighted(
        rng, {"desktop_base": 0.55, "plier_frame": 0.23, "cloop_frame": 0.22}
    )

    if skeleton in _HANDHELD_SKELETONS:
        mechanism: Mechanism = "pivot_lever"
        n_holes = 1
        palette_theme: PaletteTheme = rng.choice(_HANDHELD_THEMES)
    else:
        mechanism = _weighted(
            rng, {"pivot_lever": 0.45, "plunger": 0.25, "lever_carriage": 0.30}
        )
        if mechanism == "plunger":
            n_holes = 1
        elif mechanism == "lever_carriage":
            n_holes = _weighted(rng, {2: 0.5, 3: 0.3, 4: 0.2})
        else:  # pivot_lever on a desktop base — full office range
            n_holes = _weighted(rng, {1: 0.3, 2: 0.4, 3: 0.2, 4: 0.1})
        palette_theme = rng.choice(_DESKTOP_THEMES)

    reach_scale = round(rng.uniform(0.88, 1.18), 4)
    body_height_scale = round(rng.uniform(0.90, 1.14), 4)
    hole_pitch_scale = round(rng.uniform(0.90, 1.14), 4)
    handle_len_scale = round(rng.uniform(0.85, 1.22), 4)
    pin_radius_scale = round(rng.uniform(0.90, 1.15), 4)

    return HolePunchConfig(
        skeleton=skeleton,
        mechanism=mechanism,
        n_holes=n_holes,
        palette_theme=palette_theme,
        reach_scale=reach_scale,
        body_height_scale=body_height_scale,
        hole_pitch_scale=hole_pitch_scale,
        handle_len_scale=handle_len_scale,
        pin_radius_scale=pin_radius_scale,
        palette=dict(HOLE_PUNCH_PALETTE_PRESETS[palette_theme]),
    )


def _weighted(rng: random.Random, weights: dict):
    keys = list(weights.keys())
    return rng.choices(keys, weights=[weights[k] for k in keys], k=1)[0]


def resolve_config(config: HolePunchConfig) -> ResolvedHolePunchConfig:
    skeleton = str(config.skeleton)
    if skeleton not in {"desktop_base", "plier_frame", "cloop_frame"}:
        raise ValueError(f"Unsupported skeleton: {config.skeleton}")
    mechanism = str(config.mechanism)
    if mechanism not in {"pivot_lever", "plunger", "lever_carriage"}:
        raise ValueError(f"Unsupported mechanism: {config.mechanism}")
    theme = str(config.palette_theme)
    if theme not in HOLE_PUNCH_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    is_handheld = skeleton in _HANDHELD_SKELETONS

    # Compatibility clamps (defensive — sampler already gates these).
    if is_handheld:
        mechanism = "pivot_lever"
    n_holes = int(config.n_holes)
    if mechanism == "plunger" or is_handheld:
        n_holes = 1
    n_holes = max(1, min(n_holes, 4))
    if mechanism == "lever_carriage":
        n_holes = max(2, n_holes)

    rs = _clamp(config.reach_scale, 0.85, 1.20)
    bhs = _clamp(config.body_height_scale, 0.88, 1.16)
    hps = _clamp(config.hole_pitch_scale, 0.88, 1.16)
    hls = _clamp(config.handle_len_scale, 0.82, 1.25)
    prs = _clamp(config.pin_radius_scale, 0.88, 1.18)

    if is_handheld:
        # Rear pivot + forward lever (compact), like the desktop but small and
        # metallic. A generous pivot->station gap gives a real lever arm and
        # keeps the moving lever entirely forward of the pivot (no rearward
        # moving handle that would clash with the fixed frame at the pivot).
        pin_x = 0.024 * rs
        pivot_x = -0.032 * rs
        die_top_z = 0.020 * bhs
        base_top_z = 0.013 * bhs
    else:
        pin_x = 0.034 * rs
        pivot_x = -0.070 * rs
        die_top_z = 0.049 * bhs
        base_top_z = 0.045 * bhs

    # Pin-mount plane: pins hang _PIN_HANG below it and rest _PAPER_SLOT above
    # the die table. Single equation ties the three together. For pivot_lever
    # the lever's underside IS this plane; for lever_carriage the carriage sits
    # here and the revolute lever rides ~20 mm higher (cams the carriage down).
    pivot_z = die_top_z + _PAPER_SLOT + _PIN_HANG
    lever_pivot_z = pivot_z + (0.035 if mechanism == "lever_carriage" else 0.0)

    # Pin / die gauge (die bore derives from the pin so the pin always fits).
    pin_body_r = 0.0028 * prs
    die_hole_r = pin_body_r + 0.0014
    die_ring_r = die_hole_r + 0.0034
    die_boss_r = die_hole_r + 0.0053
    pin_cap_r = die_boss_r * 0.62
    pin_tip_r = pin_body_r + 0.0004

    hole_pitch = (0.030 if not is_handheld else 0.0) * hps
    ys = tuple((i - (n_holes - 1) / 2.0) * hole_pitch for i in range(n_holes))
    row_half = (n_holes - 1) * hole_pitch / 2.0
    base_y_half = (max(0.036, row_half + 0.021) if not is_handheld else 0.011)

    # Revolute press travel: solve the angle that drops the pin ~13 mm-worth of
    # arc at the station (Contract 3e — derived, not a tuned constant).
    d = pin_x - pivot_x
    drop_target = min(0.013, 0.42 * d)
    stroke_upper = _clamp(math.asin(drop_target / d), 0.10, 0.50)

    slide_travel = 0.012

    handle_len = (0.090 if not is_handheld else 0.075) * hls

    palette = dict(HOLE_PUNCH_PALETTE_PRESETS[theme])

    return ResolvedHolePunchConfig(
        skeleton=skeleton,  # type: ignore[arg-type]
        mechanism=mechanism,  # type: ignore[arg-type]
        n_holes=n_holes,
        palette_theme=theme,  # type: ignore[arg-type]
        palette=palette,
        is_handheld=is_handheld,
        pin_x=pin_x,
        pivot_x=pivot_x,
        pivot_z=pivot_z,
        lever_pivot_z=lever_pivot_z,
        die_top_z=die_top_z,
        base_top_z=base_top_z,
        hole_pitch=hole_pitch,
        pin_ys=ys,
        base_y_half=base_y_half,
        row_half=row_half,
        stroke_upper=stroke_upper,
        slide_travel=slide_travel,
        handle_len=handle_len,
        pin_body_r=pin_body_r,
        pin_cap_r=pin_cap_r,
        pin_tip_r=pin_tip_r,
        die_hole_r=die_hole_r,
        die_ring_r=die_ring_r,
        die_boss_r=die_boss_r,
    )


def slot_choices_for_config(r: ResolvedHolePunchConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("skeleton", str(r.skeleton)),
        ("mechanism", str(r.mechanism)),
        ("n_holes", str(r.n_holes)),
        ("palette_theme", str(r.palette_theme)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Shared geometry helpers
# --------------------------------------------------------------------------- #
def _add_dies(part, r: ResolvedHolePunchConfig) -> None:
    """Loop-emitted round dies (boss/ring/bore) on the body top, one per hole.

    Adapted from source B / plunger records (die_boss/die_ring/die_hole cylinder
    stack). The stack top == r.die_top_z; the boss bottom overlaps the body top
    so the die is supported (no per-part island)."""
    ring_len = 0.0032
    bore_len = 0.0038
    boss_len = max(0.004, r.die_top_z - r.base_top_z + 0.003)
    ring_z = r.die_top_z - ring_len * 0.5
    bore_z = r.die_top_z - bore_len * 0.4
    boss_z = r.die_top_z - boss_len * 0.5
    for i, y in enumerate(r.pin_ys):
        part.visual(
            Cylinder(radius=r.die_boss_r, length=boss_len),
            origin=Origin(xyz=(r.pin_x, y, boss_z)),
            material="body",
            name=f"die_boss_{i}", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
        part.visual(
            Cylinder(radius=r.die_ring_r, length=ring_len),
            origin=Origin(xyz=(r.pin_x, y, ring_z)),
            material="steel",
            name=f"die_ring_{i}", material_class_id="metal.steel_bare",
        )
        part.visual(
            Cylinder(radius=r.die_hole_r, length=bore_len),
            origin=Origin(xyz=(r.pin_x, y, bore_z)),
            material="black",
            name=f"die_hole_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _build_pin(part, r: ResolvedHolePunchConfig) -> None:
    """One punch pin (body + top cap + cutting tip), pin-local frame with the
    FIXED joint at the cap top (z≈0). Adapted from source pin visuals."""
    part.visual(
        Cylinder(radius=r.pin_body_r, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, -0.008)),
        material="steel",
        name="punch_pin", material_class_id="metal.steel_bare",
    )
    part.visual(
        Cylinder(radius=r.pin_cap_r, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, 0.0020)),
        material="dark_steel",
        name="pin_top_cap", material_class_id="metal.blackened_gunmetal",
    )
    part.visual(
        Cylinder(radius=r.pin_tip_r, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, -0.016)),
        material="steel",
        name="pin_cutting_tip", material_class_id="metal.steel_bare",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=0.004, length=0.024),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, -0.008)),
    )


# --------------------------------------------------------------------------- #
# Slot A — skeletons
# --------------------------------------------------------------------------- #
def _build_desktop_base(body, r: ResolvedHolePunchConfig) -> None:
    """Flat rubber-footed slab body + dies + mechanism mount hardware.

    Adapted from source B (rec_workspace__hole_punch__002) / plunger fork:
    rubber_pad, blue_base_shell, top_channel (die platform), paper_throat_gap,
    side detail, loop dies. The pivot/guide MOUNT is emitted here conditioned on
    r.mechanism so only the used mount exists (never a floating unused mount)."""
    L = 0.190 * (r.pin_x / 0.034)          # body length tracks reach
    W = max(0.076, 2 * r.base_y_half)
    shell_c = 0.0205 * (r.base_top_z / 0.045)
    shell_h = 0.023 * (r.base_top_z / 0.045)

    body.visual(
        Box((L + 0.012, W + 0.012, 0.009)),
        origin=Origin(xyz=(0.0, 0.0, 0.0045)),
        material="rubber",
        name="rubber_pad", material_class_id="rubber.smooth_plain",
    )
    body.visual(
        Box((L, W, shell_h)),
        origin=Origin(xyz=(0.0, 0.0, shell_c)),
        material="body",
        name="blue_base_shell", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Raised die platform (top_channel): the dies sit on this.
    plat_h = max(0.010, r.base_top_z - shell_c + shell_h * 0.5 + 0.004)
    body.visual(
        Box((L * 0.78, W * 0.66, plat_h)),
        origin=Origin(xyz=(0.0, 0.0, r.base_top_z - plat_h * 0.5)),
        material="body_hi",
        name="top_channel", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((L * 0.55, W * 0.52, 0.004)),
        origin=Origin(xyz=(r.pin_x * 0.3, 0.0, r.base_top_z + 0.001)),
        material="body_shadow",
        name="paper_throat_gap", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Two visible assembly screws on the front face (④ decoration).
    for i, x in enumerate((-L * 0.30, -L * 0.10)):
        body.visual(
            Cylinder(radius=0.0055, length=0.003),
            origin=Origin(xyz=(x, -(W * 0.5 - 0.0015), shell_c),
                          rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="steel",
            name=f"side_screw_{i}", material_class_id="metal.steel_bare",
        )
    _add_dies(body, r)
    _add_mount(body, r)
    body.inertial = Inertial.from_geometry(
        Box((L, W, r.die_top_z + 0.02)),
        mass=0.55,
        origin=Origin(xyz=(0.0, 0.0, r.base_top_z * 0.5)),
    )


def _build_plier_frame(body, r: ResolvedHolePunchConfig) -> None:
    """Compact chrome C-frame with a central rivet pivot (source A, plier).

    Fixed lower jaw + die plate + rising central pivot post + rearward fixed
    handle with a knurled grip + proud rivet caps. The moving upper arm is the
    ``pivot_lever`` actuator; the two arms are captured at the rivet."""
    _build_handheld_frame(body, r, cloop=False)


def _build_cloop_frame(body, r: ResolvedHolePunchConfig) -> None:
    """Compact chrome frame with a continuous bent spring-steel C-loop bridge
    at the rear (source: skeleton_sprung_loop fork)."""
    _build_handheld_frame(body, r, cloop=True)


def _build_handheld_frame(body, r: ResolvedHolePunchConfig, *, cloop: bool) -> None:
    jaw_x0 = r.pivot_x - 0.004
    jaw_x1 = r.pin_x + 0.012
    jaw_len = jaw_x1 - jaw_x0
    jaw_cx = (jaw_x0 + jaw_x1) * 0.5
    jaw_w = 0.017
    mount_top = r.pivot_z - 0.002   # only the lever hinge barrel dips into it
    # Lower jaw / die plate (flat bar carrying the dies).
    body.visual(
        Box((jaw_len, jaw_w, r.base_top_z)),
        origin=Origin(xyz=(jaw_cx, 0.0, r.base_top_z * 0.5)),
        material="body",
        name="lower_jaw", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        Box((0.010, jaw_w + 0.004, 0.004)),
        origin=Origin(xyz=(jaw_x1 - 0.004, 0.0, r.base_top_z + 0.002)),
        material="body_hi",
        name="throat_lip", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Rear pivot post rising from the jaw to just under the pivot. Its front
    # face is at the pivot so the forward lever plate clears it (only the
    # captured hinge barrel dips in).
    post_bot = r.base_top_z - 0.004
    post_h = mount_top - post_bot
    post_w = 0.020
    body.visual(
        Box((post_w, jaw_w, post_h)),
        origin=Origin(xyz=(r.pivot_x - post_w * 0.5, 0.0, post_bot + post_h * 0.5)),
        material="body",
        name="pivot_post", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    if cloop:
        # Continuous bent spring-steel C-loop bridge bowing behind the pivot
        # (elastic return identity); both ends embed in the pivot post.
        y = 0.0
        x0 = r.pivot_x
        body.visual(
            mesh_from_geometry(
                tube_from_spline_points(
                    [
                        (x0 - 0.006, y, r.base_top_z + 0.004),
                        (x0 - 0.026, y, r.base_top_z + 0.002),
                        (x0 - 0.034, y, r.pivot_z * 0.55),
                        (x0 - 0.026, y, mount_top - 0.002),
                        (x0 - 0.006, y, mount_top - 0.002),
                    ],
                    radius=0.0035, samples_per_segment=12,
                    radial_segments=12, cap_ends=True,
                ),
                "c_loop_bridge",
            ),
            material="body",
            name="c_loop_bridge", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
    else:
        # Fixed rear handle (low, behind the pivot) + knurled grip + a single
        # through pivot rivet (plier scissor identity, ④). The rivet is the real
        # pivot pin the lever's hinge barrel turns on: it passes through the
        # pivot post along Y (embedding in it, so it is anchored — Rule 2) and
        # stands proud on both faces.
        _emit_handle(body, r, name_prefix="fixed", forward=False,
                     z_off=-(r.pivot_z - r.base_top_z) * 0.5)
        body.visual(
            Cylinder(radius=0.006, length=jaw_w + 0.008),
            origin=Origin(xyz=(r.pivot_x, 0.0, r.pivot_z),
                          rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="steel",
            name="pivot_rivet", material_class_id="metal.steel_bare",
        )
    _add_dies(body, r)
    body.inertial = Inertial.from_geometry(
        Box((jaw_len + r.handle_len, jaw_w + 0.006, r.pivot_z + 0.01)),
        mass=0.16,
        origin=Origin(xyz=(jaw_cx - 0.02, 0.0, r.pivot_z * 0.5)),
    )


def _emit_handle(part, r: ResolvedHolePunchConfig, *, name_prefix: str,
                 forward: bool, z_off: float, y: float = 0.0,
                 local: bool = False) -> None:
    """A rearward (or forward) handle bar + knurled grip.

    ``local`` places it in a lever-local frame (origin at the pivot); otherwise
    world coordinates on the fixed frame."""
    ox = 0.0 if local else r.pivot_x
    oz = z_off if local else (r.pivot_z + z_off)
    sign = 1.0 if forward else -1.0
    bar_len = r.handle_len
    bar_w = 0.011
    cx = ox + sign * bar_len * 0.5
    part.visual(
        Box((bar_len, bar_w, 0.008)),
        origin=Origin(xyz=(cx, y, oz)),
        material="body",
        name=f"{name_prefix}_handle", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    grip_len = bar_len * 0.45
    gx = ox + sign * (bar_len - grip_len * 0.5)
    part.visual(
        Box((grip_len, bar_w + 0.003, 0.010)),
        origin=Origin(xyz=(gx, y, oz)),
        material="grip",
        name=f"{name_prefix}_grip", material_class_id="rubber.directional_grooved",
    )


def _add_mount(body, r: ResolvedHolePunchConfig) -> None:
    """Emit the pivot / guide mount hardware on a desktop body, matched to the
    chosen mechanism (revolute pivot vs. vertical guide)."""
    if r.mechanism in ("pivot_lever", "lever_carriage"):
        # Rear hinge block: rises from the shell to just under the pivot and
        # hosts the lever's hinge barrel (Rule 2 real anchoring visual). Its
        # top is 2 mm below the pivot so ONLY the captured barrel dips into it.
        blk_bot = r.base_top_z - 0.012
        blk_top = r.lever_pivot_z - 0.002
        blk_h = blk_top - blk_bot
        blk_w = 0.034
        # Front face sits at the pivot so the forward-reaching lever plate
        # clears it through the whole stroke — only the hinge barrel dips in.
        body.visual(
            Box((blk_w, 2 * r.base_y_half * 0.9, blk_h)),
            origin=Origin(xyz=(r.pivot_x - blk_w * 0.5, 0.0, blk_bot + blk_h * 0.5)),
            material="body",
            name="rear_hinge_block", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
    if r.mechanism == "lever_carriage":
        # Head casting: a low raised block on the base straddling the die row.
        # Its top must stay BELOW the carriage's fully-descended underside so
        # the carriage never bottoms into it at full stroke. The carriage body
        # bottom rests at r.pivot_z and descends by r.slide_travel, so we cap
        # the casting a clearance below that (derived, not a tuned constant).
        hc_bot = r.base_top_z - 0.004
        hc_top = r.pivot_z - r.slide_travel - 0.004
        hc_h = hc_top - hc_bot
        body.visual(
            Box((0.040, 2 * r.base_y_half * 0.86, hc_h)),
            origin=Origin(xyz=(r.pin_x, 0.0, hc_bot + hc_h * 0.5)),
            material="body",
            name="head_casting", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
        # Guide posts rise from the head casting up through the carriage bores;
        # long enough to stay engaged across the full descent.
        for i, ys in enumerate((-r.base_y_half * 0.62, r.base_y_half * 0.62)):
            body.visual(
                Cylinder(radius=0.003, length=0.030),
                origin=Origin(xyz=(r.pin_x, ys, hc_top + 0.011)),
                material="steel",
                name=f"guide_post_{i}", material_class_id="metal.steel_bare",
            )
    if r.mechanism == "plunger":
        # Guide flange + hollow-looking column (solid cyl + dark bore) at the
        # pin station; the plunger stem slides in it. The column sits ABOVE the
        # die (paper throat stays open beneath it), so it cannot reach the base
        # directly — it is carried by a rear C-throat frame (back post + top
        # yoke) that arches over the open throat and anchors it to the shell
        # (Rule 2 real support; no floating island).
        col_bot = r.die_top_z + 0.002
        col_h = 0.048
        col_top = col_bot + col_h
        body.visual(
            Cylinder(radius=0.024, length=0.006),
            origin=Origin(xyz=(r.pin_x, 0.0, col_bot + 0.003)),
            material="body",
            name="guide_flange", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
        body.visual(
            Cylinder(radius=0.018, length=col_h),
            origin=Origin(xyz=(r.pin_x, 0.0, col_bot + col_h * 0.5)),
            material="body",
            name="guide_column", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
        body.visual(
            Cylinder(radius=0.0135, length=col_h - 0.006),
            origin=Origin(xyz=(r.pin_x, 0.0, col_bot + col_h * 0.5 + 0.004)),
            material="black",
            name="guide_bore", material_class_id="metal.blackened_gunmetal",
        )
        # Rear throat post: rises from inside the shell (dips below the body top
        # so it is embedded, not merely touching) up behind the die to the yoke.
        back_x = r.pin_x - 0.048
        post_bot = r.base_top_z - 0.012
        post_h = col_top - post_bot
        body.visual(
            Box((0.018, 0.034, post_h)),
            origin=Origin(xyz=(back_x, 0.0, post_bot + post_h * 0.5)),
            material="body",
            name="throat_post", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )
        # Top yoke: arches forward from the post onto the column's rear shoulder
        # (ends short of the plunger stem so it never fouls the moving stem).
        yoke_x0 = back_x - 0.009
        yoke_x1 = r.pin_x - 0.015
        yoke_len = yoke_x1 - yoke_x0
        body.visual(
            Box((yoke_len, 0.030, 0.012)),
            origin=Origin(xyz=((yoke_x0 + yoke_x1) * 0.5, 0.0, col_top - 0.006)),
            material="body",
            name="throat_yoke", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
        )


# --------------------------------------------------------------------------- #
# Slot B — actuators
# --------------------------------------------------------------------------- #
def _build_pivot_lever(model, body, r: ResolvedHolePunchConfig) -> None:
    """A lever that pivots about +Y and carries the N pins (sources A / B /
    sprung_loop). Lever-local origin sits at the pivot; underside at z=0."""
    lever = model.part("pressing_lever")
    d = r.pin_x - r.pivot_x
    # The lever reaches FORWARD from the pivot over the pins to a front grip.
    # It starts just forward of the pivot (+0.004) so the plate never overlaps
    # the pivot mount — only the captured hinge barrel does.
    plate_x0 = 0.004
    plate_x1 = d + (0.012 if r.is_handheld else 0.030)
    plate_len = plate_x1 - plate_x0
    plate_cx = (plate_x0 + plate_x1) * 0.5
    plate_w = max(0.024, 2 * r.base_y_half * 0.7)
    lever.visual(
        Box((plate_len, plate_w, _PLATE_H)),
        origin=Origin(xyz=(plate_cx, 0.0, _PLATE_H * 0.5)),
        material="body",
        name="lever_plate", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Raised rib along the top (④ decoration, host-conformal box on the plate).
    lever.visual(
        Box((plate_len * 0.7, plate_w * 0.35, 0.004)),
        origin=Origin(xyz=(plate_cx, 0.0, _PLATE_H + 0.002)),
        material="body_hi",
        name="handle_rib", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Hinge barrel at the pivot (axis Y) — anchors the revolute joint and
    # bridges back to the plate (contains the part-frame origin).
    lever.visual(
        Cylinder(radius=0.0085, length=plate_w * 0.9),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="body",
        name="hinge_barrel", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Front grip pad where the hand presses (knurled).
    lever.visual(
        Box((0.028, plate_w * 0.8, 0.006)),
        origin=Origin(xyz=(plate_x1 - 0.012, 0.0, _PLATE_H + 0.003)),
        material="grip",
        name="lever_grip", material_class_id="rubber.directional_grooved",
    )
    lever.inertial = Inertial.from_geometry(
        Box((plate_len + r.handle_len, plate_w, 0.03)),
        mass=0.12,
        origin=Origin(xyz=(plate_cx - 0.01, 0.0, 0.0)),
    )

    model.articulation(
        "lever_pivot",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lever,
        origin=Origin(xyz=(r.pivot_x, 0.0, r.pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=2.0,
                                   lower=0.0, upper=r.stroke_upper),
    )
    # Pins FIXED to the lever underside at each station.
    for i, y in enumerate(r.pin_ys):
        pin = model.part(f"punch_pin_{i}")
        _build_pin(pin, r)
        model.articulation(
            f"lever_to_pin_{i}",
            ArticulationType.FIXED,
            parent=lever,
            child=pin,
            origin=Origin(xyz=(r.pin_x - r.pivot_x, y, 0.0)),
        )


def _build_plunger(model, body, r: ResolvedHolePunchConfig) -> None:
    """A palm-press head that slides straight down in the guide column
    (PRISMATIC, axis -Z), carrying the single pin (mechanism_plunger fork).
    Plunger-local origin at the column top; the stem descends into the bore."""
    plunger = model.part("plunger_head")
    col_top = r.die_top_z + 0.002 + 0.048
    # Stem runs from deep in the bore up THROUGH the cap so the cap/rim are
    # continuous with the stem (no floating button island); its top is enclosed
    # by the cap.
    stem_bot, stem_top = -0.040, 0.014
    stem_len = stem_top - stem_bot
    plunger.visual(
        Cylinder(radius=0.013, length=stem_len),
        origin=Origin(xyz=(0.0, 0.0, (stem_bot + stem_top) * 0.5)),
        material="body_hi",
        name="plunger_stem", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Cap sits clearly above the column top so it stays above it through the
    # full downward travel (col top is at plunger-local z=0).
    plunger.visual(
        Cylinder(radius=0.022, length=0.013),
        origin=Origin(xyz=(0.0, 0.0, 0.018)),
        material="body_hi",
        name="plunger_cap", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    plunger.visual(
        Cylinder(radius=0.024, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.012)),
        material="body_shadow",
        name="plunger_cap_rim", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Return spring collar around the stem, held high enough that even at full
    # press (slide_travel down) it never dips to the die table / top channel.
    plunger.visual(
        Cylinder(radius=0.0145, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, -0.030)),
        material="spring",
        name="return_spring", material_class_id="metal.steel_bare",
    )
    plunger.inertial = Inertial.from_geometry(
        Cylinder(radius=0.022, length=0.058),
        mass=0.1,
        origin=Origin(xyz=(0.0, 0.0, -0.012)),
    )
    model.articulation(
        "plunger_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=plunger,
        origin=Origin(xyz=(r.pin_x, 0.0, col_top)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=0.8,
                                   lower=0.0, upper=r.slide_travel),
    )
    # Single pin FIXED to the plunger, resting just above the die table.
    pin = model.part("punch_pin_0")
    _build_pin(pin, r)
    # column top -> pin cap top distance so the tip rests _PAPER_SLOT above table.
    mount_z = -(col_top - r.pivot_z)
    model.articulation(
        "plunger_to_pin_0",
        ArticulationType.FIXED,
        parent=plunger,
        child=pin,
        origin=Origin(xyz=(0.0, 0.0, mount_z)),
    )


def _build_lever_carriage(model, body, r: ResolvedHolePunchConfig) -> None:
    """Compound: a REVOLUTE lever whose cam nose pushes a PRISMATIC carriage;
    the N pins are FIXED to the carriage so they travel straight down
    (skeleton_lever_carriage fork)."""
    d = r.pin_x - r.pivot_x
    plate_w = max(0.030, 2 * r.base_y_half * 0.7)

    # --- Carriage (prismatic, vertical) at the pin station ---
    # Carriage-local origin sits on the pin-mount plane (r.pivot_z); the body
    # rises above it and the cam pad caps the top.
    carriage = model.part("plunger_carriage")
    carriage.visual(
        Box((0.030, 2 * r.base_y_half * 0.7, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="dark_steel",
        name="carriage_body", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        Box((0.020, 2 * r.base_y_half * 0.5, 0.005)),
        origin=Origin(xyz=(0.0, 0.0, 0.0145)),
        material="steel",
        name="carriage_cam_pad", material_class_id="metal.steel_bare",
    )
    for i, ys in enumerate((-r.base_y_half * 0.62, r.base_y_half * 0.62)):
        carriage.visual(
            Cylinder(radius=0.0045, length=0.014),
            origin=Origin(xyz=(0.0, ys, 0.006)),
            material="dark_steel",
            name=f"guide_bore_{i}", material_class_id="metal.blackened_gunmetal",
        )
    carriage.inertial = Inertial.from_geometry(
        Cylinder(radius=0.02, length=0.016),
        mass=0.06,
        origin=Origin(xyz=(0.0, 0.0, 0.007)),
    )
    model.articulation(
        "carriage_guide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=carriage,
        origin=Origin(xyz=(r.pin_x, 0.0, r.pivot_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=14.0, velocity=0.6,
                                   lower=0.0, upper=r.slide_travel),
    )
    # Pins FIXED to the carriage underside at each station.
    for i, y in enumerate(r.pin_ys):
        pin = model.part(f"punch_pin_{i}")
        _build_pin(pin, r)
        model.articulation(
            f"carriage_to_pin_{i}",
            ArticulationType.FIXED,
            parent=carriage,
            child=pin,
            origin=Origin(xyz=(0.0, y, 0.0)),
        )

    # --- Lever (revolute), rides above the carriage and cams it down ---
    lever = model.part("pressing_lever")
    plate_x0, plate_x1 = 0.004, d + 0.028
    plate_len = plate_x1 - plate_x0
    plate_cx = (plate_x0 + plate_x1) * 0.5
    lever.visual(
        Box((plate_len, plate_w, _PLATE_H)),
        origin=Origin(xyz=(plate_cx, 0.0, _PLATE_H * 0.5)),
        material="body",
        name="lever_plate", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    lever.visual(
        Box((plate_len * 0.7, plate_w * 0.35, 0.004)),
        origin=Origin(xyz=(plate_cx, 0.0, _PLATE_H + 0.002)),
        material="body_hi",
        name="handle_rib", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    lever.visual(
        Cylinder(radius=0.0085, length=plate_w * 0.9),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="body",
        name="hinge_barrel", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    # Cam nose hangs from the lever underside down onto the carriage cam pad
    # (which tops out ~r.lever_pivot_z-0.0035). Nose top touches the plate.
    lever.visual(
        Box((0.020, plate_w * 0.6, 0.012)),
        origin=Origin(xyz=(d, 0.0, -0.006)),
        material="body",
        name="cam_nose", material_class_id=("metal.paint_coated" if r.palette_theme in {"chrome", "nickel", "office_blue", "office_red", "graphite", "forest_green"} else "metal.blackened_gunmetal"),
    )
    lever.visual(
        Box((0.028, plate_w * 0.8, 0.006)),
        origin=Origin(xyz=(plate_x1 - 0.012, 0.0, _PLATE_H + 0.003)),
        material="grip",
        name="lever_grip", material_class_id="rubber.directional_grooved",
    )
    lever.inertial = Inertial.from_geometry(
        Box((plate_len, plate_w, 0.03)),
        mass=0.12,
        origin=Origin(xyz=(plate_cx, 0.0, 0.0)),
    )
    model.articulation(
        "lever_pivot",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lever,
        origin=Origin(xyz=(r.pivot_x, 0.0, r.lever_pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=2.0,
                                   lower=0.0, upper=r.stroke_upper),
    )


_SKELETON_BUILDERS = {
    "desktop_base": _build_desktop_base,
    "plier_frame": _build_plier_frame,
    "cloop_frame": _build_cloop_frame,
}
_MECHANISM_BUILDERS = {
    "pivot_lever": _build_pivot_lever,
    "plunger": _build_plunger,
    "lever_carriage": _build_lever_carriage,
}


# --------------------------------------------------------------------------- #
# Builder
# --------------------------------------------------------------------------- #
def build_hole_punch(
    config: HolePunchConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="hole_punch", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    body = model.part("body")
    _SKELETON_BUILDERS[str(r.skeleton)](body, r)
    _MECHANISM_BUILDERS[str(r.mechanism)](model, body, r)

    model.meta["template_slug"] = "hole_punch"
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    return model


def build_seeded_hole_punch(seed: int) -> ArticulatedObject:
    return build_hole_punch(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _allow_captured_overlaps(ctx: TestContext, model, r: ResolvedHolePunchConfig) -> None:
    """Element-scoped allowances for every intentional captured-hardware
    overlap (Rule 2 grandfathered pivots / sliding fits). Kept local and
    element-scoped per AUTHORING §B (no broad part-level allowances)."""
    body = model.get_part("body")
    die_elems = ("die_boss", "die_ring", "die_hole")
    pin_elems = ("punch_pin", "pin_cutting_tip", "pin_top_cap")

    def _allow_pin_into_die(pin, i: int) -> None:
        for de in die_elems:
            for pe in pin_elems:
                ctx.allow_overlap(
                    body, pin, elem_a=f"{de}_{i}", elem_b=pe,
                    reason=f"punch pin {i} descends into its die stack (captured cutting fit)",
                )

    if r.mechanism in ("pivot_lever", "lever_carriage"):
        lever = model.get_part("pressing_lever")
        mount = "rear_hinge_block" if not r.is_handheld else "pivot_post"
        ctx.allow_overlap(
            body, lever, elem_a=mount, elem_b="hinge_barrel",
            reason="lever hinge barrel is captured in the pivot mount (revolute pin-in-block)",
        )
        if r.skeleton == "plier_frame":
            ctx.allow_overlap(
                body, lever, elem_a="pivot_rivet", elem_b="hinge_barrel",
                reason="pivot rivet is the pin the lever hinge barrel turns on (captured revolute)",
            )

    if r.mechanism == "pivot_lever":
        lever = model.get_part("pressing_lever")
        for i in range(r.n_holes):
            pin = model.get_part(f"punch_pin_{i}")
            ctx.allow_overlap(
                lever, pin, elem_a="lever_plate", elem_b="pin_top_cap",
                reason="pin top cap is captured under the lever plate (FIXED mount)",
            )
            _allow_pin_into_die(pin, i)

    if r.mechanism == "plunger":
        plunger = model.get_part("plunger_head")
        pin = model.get_part("punch_pin_0")
        # The stem/spring/cap and the pin all live inside the guide column and
        # slide as one captured assembly (the primitive column is modelled
        # solid, so everything nested in it registers as overlap).
        for ge in ("guide_column", "guide_bore", "guide_flange"):
            for pe in ("plunger_stem", "plunger_cap", "plunger_cap_rim", "return_spring"):
                ctx.allow_overlap(
                    body, plunger, elem_a=ge, elem_b=pe,
                    reason="plunger assembly slides captured inside the guide column",
                )
            for pe in ("punch_pin", "pin_top_cap", "pin_cutting_tip"):
                ctx.allow_overlap(
                    body, pin, elem_a=ge, elem_b=pe,
                    reason="punch pin runs captured inside the guide column",
                )
        for pe in ("plunger_stem", "return_spring"):
            ctx.allow_overlap(
                plunger, pin, elem_a=pe, elem_b="pin_top_cap",
                reason="pin head is captured inside the hollow plunger stem",
            )
        _allow_pin_into_die(pin, 0)

    if r.mechanism == "lever_carriage":
        lever = model.get_part("pressing_lever")
        carriage = model.get_part("plunger_carriage")
        for ce in ("carriage_body", "carriage_cam_pad"):
            ctx.allow_overlap(
                lever, carriage, elem_a="cam_nose", elem_b=ce,
                reason="lever cam nose pushes on the carriage (contact interface)",
            )
        for i in range(2):
            ctx.allow_overlap(
                body, carriage, elem_a=f"guide_post_{i}", elem_b=f"guide_bore_{i}",
                reason=f"guide post {i} passes through the carriage bore (captured shaft)",
            )
            ctx.allow_overlap(
                body, carriage, elem_a=f"guide_post_{i}", elem_b="carriage_body",
                reason=f"guide post {i} is captured in the carriage body",
            )
        for i in range(r.n_holes):
            pin = model.get_part(f"punch_pin_{i}")
            for ce in ("carriage_body", "carriage_cam_pad"):
                ctx.allow_overlap(
                    carriage, pin, elem_a=ce, elem_b="pin_top_cap",
                    reason="pin cap is captured under the carriage (FIXED mount)",
                )
            for pe in ("punch_pin", "pin_top_cap", "pin_cutting_tip"):
                ctx.allow_overlap(
                    body, pin, elem_a="head_casting", elem_b=pe,
                    reason="head casting straddles the pins at the station",
                )
            ctx.allow_overlap(
                lever, pin, elem_a="cam_nose", elem_b="pin_top_cap",
                reason="lever cam nose sweeps over the pin caps at the station",
            )
            _allow_pin_into_die(pin, i)


def run_hole_punch_tests(
    model: ArticulatedObject,
    config: HolePunchConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _allow_captured_overlaps(ctx, model, r)

    # Baseline-equivalent checks (deduplicated against the compiler baseline).
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    body = model.get_part("body")
    body_visuals = {v.name for v in body.visuals}

    # --- Category identity: N dies present ---
    for i in range(r.n_holes):
        ctx.check(
            f"die_{i}_present",
            {f"die_hole_{i}", f"die_ring_{i}", f"die_boss_{i}"}.issubset(body_visuals),
            details=f"body visuals={sorted(body_visuals)}",
        )

    # --- Pin/die alignment (XY) at rest, for every hole ---
    pin_parts = [model.get_part(f"punch_pin_{i}") for i in range(r.n_holes)]
    for i, pin in enumerate(pin_parts):
        ctx.expect_overlap(
            pin, body, axes="xy",
            elem_a="punch_pin", elem_b=f"die_hole_{i}",
            min_overlap=0.002,
            name=f"pin {i} aligns with die {i}",
        )
        ctx.expect_gap(
            pin, body, axis="z",
            positive_elem="pin_cutting_tip", negative_elem=f"die_ring_{i}",
            min_gap=0.0008, max_gap=0.014,
            name=f"pin {i} tip clears die {i} at rest (open paper slot)",
        )

    # --- Primary press DOF drives the pins down into the dies ---
    press_joints: dict = {}
    if r.mechanism in ("pivot_lever", "lever_carriage"):
        press_joints[model.get_articulation("lever_pivot")] = (
            model.get_articulation("lever_pivot").motion_limits.upper
        )
    if r.mechanism == "plunger":
        press_joints[model.get_articulation("plunger_slide")] = (
            model.get_articulation("plunger_slide").motion_limits.upper
        )
    if r.mechanism == "lever_carriage":
        press_joints[model.get_articulation("carriage_guide")] = (
            model.get_articulation("carriage_guide").motion_limits.upper
        )

    die_top = r.die_top_z
    rest_tips = [ctx.part_element_world_aabb(p, elem="pin_cutting_tip") for p in pin_parts]
    with ctx.pose(press_joints):
        for i, pin in enumerate(pin_parts):
            pressed = ctx.part_element_world_aabb(pin, elem="pin_cutting_tip")
            rest = rest_tips[i]
            ok = (
                pressed is not None and rest is not None
                and pressed[0][2] < die_top - 0.001
                and pressed[0][2] < rest[0][2] - 0.005
            )
            ctx.check(
                f"press stroke drives pin {i} into die {i}",
                ok,
                details=f"rest={rest}, pressed={pressed}, die_top={die_top:.4f}",
            )

    # --- Full-travel collision sweep (Rule 5) ---
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=64,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = [
    "Skeleton",
    "Mechanism",
    "PaletteTheme",
    "HolePunchConfig",
    "ResolvedHolePunchConfig",
    "build_hole_punch",
    "build_seeded_hole_punch",
    "config_from_seed",
    "resolve_config",
    "run_hole_punch_tests",
    "slot_choices_for_seed",
    "__modular__",
]
