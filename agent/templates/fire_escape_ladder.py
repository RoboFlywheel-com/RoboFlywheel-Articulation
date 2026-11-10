# SPDX-License-Identifier: Apache-2.0

"""Fire escape ladder — modular procedural template.

A deployable/climbable ladder for emergency egress from a building: two parallel
side members with regularly spaced horizontal rungs, a building anchor interface,
and at least one real deploy joint. Authored from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/fire_escape_ladder.md`` and the
14-record 5-star pool (2 origins + 12 forks) under ``data/records/``.

Pattern = ``mixed``: a ③ Primary-Form-Family slot (``ladder_family``) dispatches
one of four structurally distinct bodies, each porting its 5-star source(s):

  * ``fixed_cage``   — rigid caged steel wall ladder (origins e6a5530c / 20b875b6);
                       carries a ``guard_system`` (full_cage / grab_rail /
                       fall_arrest) and a ``deploy`` drop child (PRISMATIC slide
                       or REVOLUTE swing). fall_arrest adds a PRISMATIC shuttle.
  * ``portable_hook``— flexible side-member roll-up ladder with a REVOLUTE sill
                       hook; ``side_member`` ∈ {chain_link (chain_rollup),
                       webbing_strap (strap_webbing)}.
  * ``folding``      — 3 rigid segments + 2 REVOLUTE fold hinges (folding_articulated).
  * ``telescoping``  — 3 nested stages + 2 PRISMATIC joints (telescoping_multistage).

Every seed keeps ≥1 real non-FIXED joint. ``rung_count`` N∈[4,16] is the strong
multiplicity axis (rungs emitted by a ``for i in range(N)`` loop). All
captured-pin / captured-slide joints omit ``MatingContract`` (grandfathered,
AUTHORING Rule 2) and are guarded by element-scoped ``allow_overlap`` mirroring
each source record's ``run_tests`` block + the flat articulation-origin baseline.
Non-moving guard / cage / hook / standoff geometry is emitted as ``parent.visual``
(Rule 1), never a FIXED joint.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

LadderFamily = Literal["fixed_cage", "portable_hook", "folding", "telescoping"]
SideMember = Literal["rigid_rail", "chain_link", "webbing_strap"]
GuardSystem = Literal["full_cage", "grab_rail", "fall_arrest", "open"]
Deploy = Literal[
    "prismatic_drop", "revolute_swing", "sill_hook", "fold_hinges", "telescope"
]
PaletteStyle = Literal[
    "galvanized_steel",
    "zinc_plated",
    "safety_orange",
    "anodized_aluminium",
    "painted_red_brackets",
]

LADDER_FAMILIES: tuple[LadderFamily, ...] = (
    "fixed_cage",
    "portable_hook",
    "folding",
    "telescoping",
)
PORTABLE_SIDE_MEMBERS: tuple[SideMember, ...] = ("chain_link", "webbing_strap")
FIXED_GUARDS: tuple[GuardSystem, ...] = ("full_cage", "grab_rail", "fall_arrest")
FIXED_DEPLOYS: tuple[Deploy, ...] = ("prismatic_drop", "revolute_swing")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_steel",
    "zinc_plated",
    "safety_orange",
    "anodized_aluminium",
    "painted_red_brackets",
)

N_MIN = 4
N_MAX = 16
# Rung-count sampling: small N high-frequency, large N long tail (spec §8).
_N_VALUES = tuple(range(N_MIN, N_MAX + 1))
_N_WEIGHTS = tuple(1.0 / (1.0 + 0.32 * (n - N_MIN)) for n in _N_VALUES)

# Palette roles: rail (structural rails/rungs/cage/hooks/segments), hardware
# (standoffs/guides/collars/sleeves/brackets/plates), accent (safety release
# sleeve / latch / pin / shuttle), foot (rubber feet), bolt (dark bolt heads),
# web (webbing strap color). Material classes: metal + painted.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_steel": {
        "rail": (0.78, 0.80, 0.78, 1.0),
        "hardware": (0.56, 0.58, 0.56, 1.0),
        "accent": (1.0, 0.85, 0.02, 1.0),
        "foot": (0.03, 0.03, 0.03, 1.0),
        "bolt": (0.08, 0.09, 0.09, 1.0),
        "web": (0.86, 0.80, 0.20, 1.0),
    },
    "zinc_plated": {
        "rail": (0.72, 0.76, 0.74, 1.0),
        "hardware": (0.50, 0.54, 0.52, 1.0),
        "accent": (0.90, 0.05, 0.03, 1.0),
        "foot": (0.03, 0.03, 0.03, 1.0),
        "bolt": (0.10, 0.11, 0.11, 1.0),
        "web": (0.16, 0.18, 0.20, 1.0),
    },
    "safety_orange": {
        "rail": (1.0, 0.45, 0.0, 1.0),
        "hardware": (0.56, 0.58, 0.56, 1.0),
        "accent": (1.0, 0.85, 0.02, 1.0),
        "foot": (0.04, 0.04, 0.04, 1.0),
        "bolt": (0.09, 0.09, 0.09, 1.0),
        "web": (1.0, 0.55, 0.05, 1.0),
    },
    "anodized_aluminium": {
        "rail": (0.82, 0.84, 0.86, 1.0),
        "hardware": (0.62, 0.64, 0.66, 1.0),
        "accent": (0.90, 0.05, 0.03, 1.0),
        "foot": (0.05, 0.05, 0.06, 1.0),
        "bolt": (0.20, 0.20, 0.22, 1.0),
        "web": (0.30, 0.40, 0.55, 1.0),
    },
    "painted_red_brackets": {
        "rail": (0.80, 0.82, 0.80, 1.0),
        "hardware": (0.72, 0.10, 0.08, 1.0),
        "accent": (1.0, 0.85, 0.02, 1.0),
        "foot": (0.03, 0.03, 0.03, 1.0),
        "bolt": (0.12, 0.05, 0.05, 1.0),
        "web": (0.72, 0.14, 0.10, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), from the origin records.
# ---------------------------------------------------------------------------
_RAIL_HALF_GAP = 0.25  # half-spacing between side members (origins rail_x)
_RUNG_PITCH = 0.30  # vertical rung pitch
_RAIL_RADIUS = 0.022  # side-member tube radius
_RUNG_RADIUS = 0.015  # rung tube radius
_RUNG_Z0 = 0.18  # first-rung height on the main run
_RUNG_OVERHANG = 0.045  # rung length past the rails (per side, halved)
_CAGE_RADIUS = 0.58  # semicircular cage envelope radius
_DROP_TRAVEL = 0.95  # PRISMATIC drop / telescope stage travel
_STANDOFF_DEPTH = 0.19  # wall standoff arm depth


@dataclass(frozen=True)
class FireEscapeLadderConfig:
    ladder_family: LadderFamily | None = None
    side_member: SideMember | None = None
    guard_system: GuardSystem | None = None
    deploy: Deploy | None = None
    rung_count: int | None = None
    palette_style: PaletteStyle = "galvanized_steel"
    rail_gap_scale: float = 1.0
    rung_pitch_scale: float = 1.0
    rail_radius_scale: float = 1.0
    cage_radius_scale: float = 1.0
    drop_travel_scale: float = 1.0
    standoff_depth_scale: float = 1.0
    name: str = "fire_escape_ladder"


@dataclass(frozen=True)
class ResolvedFireEscapeLadderConfig:
    ladder_family: LadderFamily
    side_member: SideMember
    guard_system: GuardSystem
    deploy: Deploy
    rung_count: int
    palette_style: PaletteStyle
    g: float  # rail half-gap
    lg: float  # drop/lower rail half-gap
    pitch: float
    rail_r: float
    rung_r: float
    rung_len: float  # derived: spans both members
    cage_radius: float
    drop_travel: float
    standoff_depth: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Sampling / resolution
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FireEscapeLadderConfig:
    rng = random.Random(seed)
    family = rng.choice(LADDER_FAMILIES)

    if family == "portable_hook":
        side_member = rng.choice(PORTABLE_SIDE_MEMBERS)
    else:
        side_member = "rigid_rail"

    if family == "fixed_cage":
        guard_system = rng.choice(FIXED_GUARDS)
        deploy = rng.choice(FIXED_DEPLOYS)
    else:
        guard_system = "open"
        deploy = {
            "portable_hook": "sill_hook",
            "folding": "fold_hinges",
            "telescoping": "telescope",
        }[family]

    rung_count = rng.choices(_N_VALUES, weights=_N_WEIGHTS, k=1)[0]

    return FireEscapeLadderConfig(
        ladder_family=family,
        side_member=side_member,
        guard_system=guard_system,
        deploy=deploy,
        rung_count=rung_count,
        palette_style=rng.choice(PALETTE_STYLES),
        rail_gap_scale=round(rng.uniform(0.85, 1.15), 4),
        rung_pitch_scale=round(rng.uniform(0.90, 1.12), 4),
        rail_radius_scale=round(rng.uniform(0.85, 1.20), 4),
        cage_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        drop_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        standoff_depth_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_fire_escape_ladder_{seed}",
    )


def resolve_config(
    config: FireEscapeLadderConfig | None = None,
) -> ResolvedFireEscapeLadderConfig:
    cfg = config or FireEscapeLadderConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    family = _pick(cfg.ladder_family, LADDER_FAMILIES)

    # --- Compatibility gating (spec §9). ---
    if family == "portable_hook":
        side_member = _pick(cfg.side_member, PORTABLE_SIDE_MEMBERS)
    else:
        side_member = "rigid_rail"

    if family == "fixed_cage":
        guard_system = _pick(cfg.guard_system, FIXED_GUARDS)
        deploy = _pick(cfg.deploy, FIXED_DEPLOYS)
        # Gate: a central fall-arrest rail + shuttle occupy the forward
        # centerline, exactly where a swing-down section stows; the two are
        # physically incompatible, so fall_arrest only pairs with the sliding
        # drop (which deploys straight down, clear of the arrest rail).
        if guard_system == "fall_arrest" and deploy == "revolute_swing":
            deploy = "prismatic_drop"
    else:
        guard_system = "open"
        deploy = {
            "portable_hook": "sill_hook",
            "folding": "fold_hinges",
            "telescoping": "telescope",
        }[family]

    rung_count = int(cfg.rung_count) if cfg.rung_count is not None else 8
    rung_count = int(_clamp(rung_count, N_MIN, N_MAX))

    gap_scale = _clamp(cfg.rail_gap_scale, 0.85, 1.15)
    pitch_scale = _clamp(cfg.rung_pitch_scale, 0.90, 1.12)
    radius_scale = _clamp(cfg.rail_radius_scale, 0.85, 1.20)
    cage_scale = _clamp(cfg.cage_radius_scale, 0.90, 1.12)
    travel_scale = _clamp(cfg.drop_travel_scale, 0.85, 1.15)
    depth_scale = _clamp(cfg.standoff_depth_scale, 0.85, 1.20)

    g = _RAIL_HALF_GAP * gap_scale
    lg = 0.72 * g  # drop/lower rail half-gap tracks the main gap
    pitch = _RUNG_PITCH * pitch_scale
    rail_r = _RAIL_RADIUS * radius_scale
    rung_r = _RUNG_RADIUS * radius_scale
    # Derived (equation): rung spans both members with a small overhang.
    rung_len = 2.0 * g + _RUNG_OVERHANG
    # Derived (inequality): cage hoop must bracket the rails.
    cage_radius = max(_CAGE_RADIUS * cage_scale, g + 0.14)
    drop_travel = _DROP_TRAVEL * travel_scale
    standoff_depth = _STANDOFF_DEPTH * depth_scale

    return ResolvedFireEscapeLadderConfig(
        ladder_family=family,
        side_member=side_member,
        guard_system=guard_system,
        deploy=deploy,
        rung_count=rung_count,
        palette_style=palette_style,
        g=g,
        lg=lg,
        pitch=pitch,
        rail_r=rail_r,
        rung_r=rung_r,
        rung_len=rung_len,
        cage_radius=cage_radius,
        drop_travel=drop_travel,
        standoff_depth=standoff_depth,
        name=cfg.name or "fire_escape_ladder",
    )


def with_overrides(
    config: FireEscapeLadderConfig, **kwargs: object
) -> FireEscapeLadderConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FireEscapeLadderConfig | ResolvedFireEscapeLadderConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedFireEscapeLadderConfig)
        else resolve_config(config)
    )
    return (
        ("ladder_family", r.ladder_family),
        ("side_member", r.side_member),
        ("guard_system", r.guard_system),
        ("deploy", r.deploy),
        ("rung_count", f"n{r.rung_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (preserved from the origin records).
# ---------------------------------------------------------------------------
def _cyl_x(part, name, *, center, length, radius, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=center, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _cyl_y(part, name, *, center, length, radius, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=center, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _cyl_z(part, name, *, center, length, radius, material) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=center),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _arc_points(radius, z, *, steps=26):
    """Semicircular horizontal cage-hoop path (front half, +y)."""
    return [
        (
            radius * math.cos(math.pi - math.pi * i / steps),
            radius * math.sin(math.pi - math.pi * i / steps),
            z,
        )
        for i in range(steps + 1)
    ]


def _chain_link(part, side_idx, link_idx, x, z, link_h, material) -> None:
    """One chain-link box: even=flat face, odd=edge-on (chain_rollup L52-77)."""
    lw, lt = 0.034, 0.007
    if link_idx % 2 == 0:
        part.visual(
            Box((lw, lt, link_h)),
            origin=Origin(xyz=(x, 0.0, z)),
            material=material,
            name=f"chain_link_{side_idx}_{link_idx}", material_class_id="metal.mesh_chainmail",
        )
    else:
        part.visual(
            Box((lt, lw, link_h)),
            origin=Origin(xyz=(x, 0.0, z)),
            material=material,
            name=f"chain_link_{side_idx}_{link_idx}", material_class_id="metal.mesh_chainmail",
        )


def _standoff_levels(z_lo: float, z_hi: float) -> list[float]:
    n = max(2, int(round((z_hi - z_lo) / 0.90)) + 1)
    if n == 1:
        return [(z_lo + z_hi) / 2.0]
    return [z_lo + (z_hi - z_lo) * i / (n - 1) for i in range(n)]


def _wall_anchor(part, si, lv, x, z, mats, depth, *, bolts=False) -> None:
    """One wall standoff arm + anchor plate (+ optional bolts).

    The arm spans y in [-depth, 0] (touching the rail at y=0), and the plate
    straddles the arm's outer tip so both stay connected for ANY depth scale.
    """
    _cyl_y(
        part,
        f"wall_standoff_{si}_{lv}",
        center=(x, -depth / 2.0, z),
        length=depth,
        radius=0.017,
        material=mats["hardware"],
    )
    plate_y = -depth - 0.0155
    part.visual(
        Box((0.15, 0.035, 0.20)),
        origin=Origin(xyz=(x, plate_y, z)),
        material=mats["hardware"],
        name=f"wall_plate_{si}_{lv}", material_class_id="metal.paint_coated",
    )
    if bolts:
        for bs, dz in (("top", 0.065), ("bottom", -0.065)):
            _cyl_z(
                part,
                f"bolt_{bs}_{si}_{lv}",
                center=(x, plate_y - 0.016, z + dz),
                length=0.012,
                radius=0.017,
                material=mats["bolt"],
            )


# ===========================================================================
# Family: fixed_cage  (origins 20b875b6 / e6a5530c + guard/deploy forks)
# ===========================================================================
def _build_fixed_cage(model, r, mats) -> None:
    fixed = model.part("fixed_ladder")
    g, rail_r, rung_r = r.g, r.rail_r, r.rung_r

    last_rung_z = _RUNG_Z0 + (r.rung_count - 1) * r.pitch
    height = last_rung_z + 0.24
    # Main side rails (0 .. height).
    for x, s in ((-g, "0"), (g, "1")):
        _cyl_z(
            fixed,
            f"fixed_side_rail_{s}",
            center=(x, 0.0, height / 2.0),
            length=height,
            radius=rail_r,
            material=mats["rail"],
        )
    # Rungs via for-loop (the N multiplicity axis).
    for i in range(r.rung_count):
        _cyl_x(
            fixed,
            f"fixed_rung_{i}",
            center=(0.0, 0.0, _RUNG_Z0 + i * r.pitch),
            length=r.rung_len,
            radius=rung_r,
            material=mats["rail"],
        )
    # Wall standoff brackets + anchor plates + bolts (origin A L91-102).
    for lv, z in enumerate(_standoff_levels(0.45, height - 0.40)):
        for si, x in ((0, -g), (1, g)):
            _wall_anchor(fixed, si, lv, x, z, mats, r.standoff_depth, bolts=True)

    # Guard system (non-moving visuals on the root body; Rule 1).
    if r.guard_system == "full_cage":
        _emit_full_cage(fixed, r, mats, height)
    elif r.guard_system == "grab_rail":
        _emit_grab_rail(fixed, r, mats, height)
    else:  # fall_arrest
        _emit_fall_arrest(model, fixed, r, mats, height, last_rung_z)

    # Deploy mechanism (the guaranteed non-FIXED joint).
    if r.deploy == "prismatic_drop":
        _emit_prismatic_drop(model, fixed, r, mats)
    else:  # revolute_swing
        _emit_revolute_swing(model, fixed, r, mats)


def _emit_full_cage(fixed, r, mats, height) -> None:
    cage_bottom = max(1.3, 0.30 * height)
    cage_top = height - 0.13
    if cage_top <= cage_bottom + 0.2:
        cage_bottom = max(0.5, cage_top - 0.6)
    cr = r.cage_radius
    n_hoops = max(2, int(round((cage_top - cage_bottom) / 0.60)) + 1)
    for hi in range(n_hoops):
        z = cage_bottom + (cage_top - cage_bottom) * hi / (n_hoops - 1)
        hoop = tube_from_spline_points(
            _arc_points(cr, z, steps=26),
            radius=0.016,
            samples_per_segment=2,
            radial_segments=14,
            cap_ends=True,
        )
        fixed.visual(
            mesh_from_geometry(hoop, f"cage_hoop_mesh_{hi}"),
            material=mats["rail"],
            name=f"cage_hoop_{hi}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_steel", "zinc_plated", "safety_orange", "painted_red_brackets"} else "metal.aluminum_bare"),
        )
        # Short arms tie each hoop back to the rails.
        arm_len = cr - r.g + 0.035
        _cyl_x(
            fixed,
            f"cage_arm_{hi}_0",
            center=(-(r.g + cr) / 2.0, 0.0, z),
            length=arm_len,
            radius=0.016,
            material=mats["rail"],
        )
        _cyl_x(
            fixed,
            f"cage_arm_{hi}_1",
            center=((r.g + cr) / 2.0, 0.0, z),
            length=arm_len,
            radius=0.016,
            material=mats["rail"],
        )
    # Vertical cage bars following the semicircular envelope.
    bar_h = (cage_top - cage_bottom) + 0.06
    bar_mid = (cage_bottom + cage_top) / 2.0
    for bi, ang in enumerate(
        (math.pi, 5 * math.pi / 6, 2 * math.pi / 3, math.pi / 2, math.pi / 3, math.pi / 6, 0.0)
    ):
        _cyl_z(
            fixed,
            f"cage_bar_{bi}",
            center=(cr * math.cos(ang), cr * math.sin(ang), bar_mid),
            length=bar_h,
            radius=0.014,
            material=mats["rail"],
        )


def _emit_grab_rail(fixed, r, mats, height) -> None:
    # Curved handhold rails rising from each rail top (no_cage_grabrail L118-154).
    for x, s in ((-r.g, "0"), (r.g, "1")):
        pts = [
            (x, 0.00, height - 0.02),
            (x, 0.08, height + 0.18),
            (x, 0.22, height + 0.38),
            (x, 0.36, height + 0.53),
            (x, 0.44, height + 0.60),
        ]
        mesh = tube_from_spline_points(
            pts,
            radius=0.018,
            samples_per_segment=8,
            closed_spline=False,
            radial_segments=12,
            cap_ends=True,
            up_hint=(0.0, 0.0, 1.0),
        )
        fixed.visual(
            mesh_from_geometry(mesh, f"grab_rail_mesh_{s}"),
            material=mats["accent"],
            name=f"grab_rail_{s}", material_class_id="metal.paint_coated",
        )


def _emit_fall_arrest(model, fixed, r, mats, height, last_rung_z) -> None:
    # Central fall-arrest rail + brackets + travelling shuttle (fall_arrest_rail).
    # Offset forward (+y) so the rail/shuttle clear the rung plane (y=0).
    y_off = 0.11
    arr_bottom = _RUNG_Z0 + 0.30
    arr_top = last_rung_z - 0.10
    if arr_top <= arr_bottom + 0.3:
        arr_top = arr_bottom + 0.3
    arr_len = arr_top - arr_bottom
    _cyl_z(
        fixed,
        "arrest_rail",
        center=(0.0, y_off, (arr_bottom + arr_top) / 2.0),
        length=arr_len,
        radius=0.016,
        material=mats["rail"],
    )
    n_br = max(2, int(round(arr_len / 0.60)) + 1)
    for bi in range(n_br):
        z = arr_bottom + arr_len * bi / (n_br - 1)
        _cyl_y(
            fixed,
            f"arrest_bracket_{bi}",
            center=(0.0, y_off / 2.0, z),
            length=y_off,
            radius=0.012,
            material=mats["hardware"],
        )

    shuttle = model.part("arrest_shuttle")
    shuttle.visual(
        Box((0.08, 0.06, 0.07)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["accent"],
        name="shuttle_body", material_class_id="metal.paint_coated",
    )
    _cyl_y(
        shuttle,
        "shuttle_eye",
        center=(0.0, 0.055, 0.0),
        length=0.05,
        radius=0.008,
        material=mats["hardware"],
    )
    half_travel = max(0.05, arr_len / 2.0 - 0.12)
    model.articulation(
        "shuttle_to_rail",
        ArticulationType.PRISMATIC,
        parent=fixed,
        child=shuttle,
        origin=Origin(xyz=(0.0, y_off, (arr_bottom + arr_top) / 2.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=50.0, velocity=0.5, lower=-half_travel, upper=half_travel
        ),
    )


def _emit_prismatic_drop(model, fixed, r, mats) -> None:
    g, lg = r.g, r.lg
    # Forward slide guide hardware at the base (origin A L140-173).
    for si, x in ((0, -(g + 0.06)), (1, (g + 0.06))):
        rail_side = -1.0 if x < 0.0 else 1.0
        _cyl_y(
            fixed,
            f"lower_guide_cross_{si}",
            center=(x, 0.065, 0.22),
            length=0.14,
            radius=0.015,
            material=mats["hardware"],
        )
        fixed.visual(
            Box((0.11, 0.018, 0.28)),
            origin=Origin(xyz=(x, 0.155, 0.22)),
            material=mats["hardware"],
            name=f"lower_guide_plate_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
        fixed.visual(
            Box((0.10, 0.17, 0.060)),
            origin=Origin(xyz=(rail_side * (g + 0.035), 0.075, 0.22)),
            material=mats["hardware"],
            name=f"lower_guide_web_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
    for si, x in ((0, -lg), (1, lg)):
        fixed.visual(
            Box((0.080, 0.070, 0.100)),
            origin=Origin(xyz=(x, 0.105, 0.140)),
            material=mats["hardware"],
            name=f"lower_slide_collar_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
        fixed.visual(
            Box((0.075, 0.080, 0.070)),
            origin=Origin(xyz=(-g if x < 0.0 else g, 0.045, 0.140)),
            material=mats["hardware"],
            name=f"lower_slide_bridge_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
    fixed.visual(
        Box((0.18, 0.050, 0.055)),
        origin=Origin(xyz=(0.0, 0.020, 0.460)),
        material=mats["accent"],
        name="release_latch", material_class_id="metal.paint_coated",
    )

    lower = model.part("lower_ladder")
    ly = 0.10
    lower_top, lower_bottom = 1.25, -1.12
    lh = lower_top - lower_bottom
    for si, x in ((0, -lg), (1, lg)):
        _cyl_z(
            lower,
            f"lower_rail_{si}",
            center=(x, ly, (lower_top + lower_bottom) / 2.0),
            length=lh,
            radius=0.022,
            material=mats["rail"],
        )
        _cyl_z(
            lower,
            f"release_sleeve_{si}",
            center=(x, ly + 0.03, -0.55),
            length=0.55,
            radius=0.026,
            material=mats["accent"],
        )
        lower.visual(
            Box((0.075, 0.070, 0.045)),
            origin=Origin(xyz=(x, ly, lower_bottom - 0.02)),
            material=mats["foot"],
            name=f"rubber_foot_{si}", material_class_id="rubber.smooth_plain",
        )
    for ri, z in enumerate((-0.95, -0.65, -0.35, -0.05)):
        _cyl_x(
            lower,
            f"lower_rung_{ri}",
            center=(0.0, ly, z),
            length=2.0 * lg + 0.04,
            radius=0.016,
            material=mats["rail"],
        )
    _cyl_x(
        lower,
        "lower_foot_bar",
        center=(0.0, ly, lower_bottom),
        length=2.0 * lg + 0.12,
        radius=0.022,
        material=mats["rail"],
    )
    lower.visual(
        Box((0.42, 0.024, 0.045)),
        origin=Origin(xyz=(0.0, ly + 0.020, 0.07)),
        material=mats["accent"],
        name="lower_latch_tab", material_class_id="metal.paint_coated",
    )

    model.articulation(
        "ladder_to_lower",
        ArticulationType.PRISMATIC,
        parent=fixed,
        child=lower,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=120.0, velocity=0.35, lower=0.0, upper=r.drop_travel
        ),
    )


def _emit_revolute_swing(model, fixed, r, mats) -> None:
    g, lg = r.g, r.lg
    hinge_z = 0.06
    # Hinge bracket ears + gussets + cross brace at the base (hinged_drop L139-152).
    for si, x in ((0, -g), (1, g)):
        fixed.visual(
            Box((0.070, 0.120, 0.090)),
            origin=Origin(xyz=(x, 0.060, hinge_z)),
            material=mats["hardware"],
            name=f"hinge_ear_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
        _cyl_y(
            fixed,
            f"hinge_gusset_{si}",
            center=(x, 0.035, hinge_z),
            length=0.10,
            radius=0.014,
            material=mats["hardware"],
        )
    _cyl_x(
        fixed,
        "hinge_cross_brace",
        center=(0.0, 0.060, hinge_z),
        length=2.0 * g + 0.04,
        radius=0.016,
        material=mats["hardware"],
    )

    lower = model.part("lower_ladder")
    ly = 0.06
    sleeve_top = 0.12
    rail_start = sleeve_top + 0.02
    rail_end = 2.10
    rail_len = rail_end - rail_start
    rail_mid = (rail_start + rail_end) / 2.0
    # Swing hinge hardware at the child origin (on the joint axis).
    _cyl_x(
        lower,
        "swing_sleeve",
        center=(0.0, 0.0, 0.0),
        length=2.0 * lg + 0.06,
        radius=0.032,
        material=mats["rail"],
    )
    _cyl_x(
        lower,
        "swing_pin",
        center=(0.0, 0.0, 0.0),
        length=2.0 * lg + 0.10,
        radius=0.018,
        material=mats["bolt"],
    )
    for si, xe in ((0, -lg - 0.05), (1, lg + 0.05)):
        _cyl_x(
            lower,
            f"swing_pin_cap_{si}",
            center=(xe, 0.0, 0.0),
            length=0.018,
            radius=0.028,
            material=mats["bolt"],
        )
    for si, x in ((0, -lg), (1, lg)):
        _cyl_z(
            lower,
            f"hinge_bracket_{si}",
            center=(x, ly / 2.0, rail_start / 2.0),
            length=rail_start + 0.04,
            radius=0.018,
            material=mats["rail"],
        )
        _cyl_z(
            lower,
            f"lower_rail_{si}",
            center=(x, ly, rail_mid),
            length=rail_len,
            radius=0.022,
            material=mats["rail"],
        )
    n_lower = max(3, min(6, r.rung_count // 2))
    for ri in range(n_lower):
        _cyl_x(
            lower,
            f"lower_rung_{ri}",
            center=(0.0, ly, rail_start + 0.15 + 0.30 * ri),
            length=2.0 * lg + 0.04,
            radius=0.016,
            material=mats["rail"],
        )
    _cyl_x(
        lower,
        "lower_foot_bar",
        center=(0.0, ly, rail_end),
        length=2.0 * lg + 0.12,
        radius=0.022,
        material=mats["rail"],
    )
    _cyl_z(
        lower,
        "counterweight_arm",
        center=(0.0, 0.0, -0.225),
        length=0.45,
        radius=0.016,
        material=mats["rail"],
    )
    _cyl_z(
        lower,
        "counterweight_mass",
        center=(0.0, 0.0, -0.39),
        length=0.12,
        radius=0.040,
        material=mats["bolt"],
    )
    lower.visual(
        Box((2.0 * lg + 0.06, 0.024, 0.045)),
        origin=Origin(xyz=(0.0, ly + 0.020, rail_start + 0.15)),
        material=mats["accent"],
        name="lower_latch_tab", material_class_id="metal.paint_coated",
    )

    model.articulation(
        "ladder_to_lower",
        ArticulationType.REVOLUTE,
        parent=fixed,
        child=lower,
        origin=Origin(xyz=(0.0, 0.06, hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.8, lower=0.0, upper=2.90),
    )


# ===========================================================================
# Family: portable_hook  (chain_rollup / strap_webbing + REVOLUTE sill hook)
# ===========================================================================
def _build_portable_hook(model, r, mats) -> None:
    g = r.g
    ladder_height = _RUNG_Z0 + (r.rung_count - 1) * r.pitch + 0.30
    upper = model.part("ladder_body")

    if r.side_member == "chain_link":
        cx = 0.60 * g  # chain centre-line half-gap
        num_links = max(6, int(round(ladder_height / 0.15)))
        link_pitch = ladder_height / num_links
        for si, sx in ((0, -cx), (1, cx)):
            for li in range(num_links):
                _chain_link(
                    upper, si, li, sx, link_pitch * (li + 0.5), link_pitch, mats["rail"]
                )
        member_half = cx
    else:  # webbing_strap
        sx = 0.60 * g
        for si, xs in ((0, -1.0), (1, 1.0)):
            upper.visual(
                Box((0.048, 0.004, ladder_height)),
                origin=Origin(xyz=(xs * sx, 0.0, ladder_height / 2.0)),
                material=mats["web"],
                name=f"side_strap_{si}", material_class_id="fabric.webbing",
            )
        member_half = sx

    # Rungs (for-loop) + wall standoff stubs.
    for i in range(r.rung_count):
        z = _RUNG_Z0 + i * r.pitch
        _cyl_x(
            upper,
            f"rung_{i}",
            center=(0.0, 0.0, z),
            length=2.0 * member_half + 0.05,
            radius=0.013,
            material=mats["rail"],
        )
        for si, sx in ((0, -member_half), (1, member_half)):
            _cyl_y(
                upper,
                f"standoff_{i}_{si}",
                center=(sx, -0.05, z),
                length=0.08,
                radius=0.010,
                material=mats["hardware"],
            )

    _cyl_x(
        upper,
        "head_bar",
        center=(0.0, 0.0, ladder_height),
        length=2.0 * member_half + 0.08,
        radius=0.016,
        material=mats["hardware"],
    )
    _cyl_x(
        upper,
        "foot_bar",
        center=(0.0, 0.0, 0.018),
        length=2.0 * member_half + 0.10,
        radius=0.016,
        material=mats["rail"],
    )
    # Pivot boss rises from the head bar to the pivot axis (lifted clear of the
    # head bar / chain top so the hook throat does not intersect them).
    pivot_z = ladder_height + 0.12
    _cyl_z(
        upper,
        "pivot_boss",
        center=(0.0, 0.0, ladder_height + 0.06),
        length=0.16,
        radius=0.022,
        material=mats["hardware"],
    )

    # Sill hook child on a REVOLUTE pivot (windowsill_hook geometry: hinge arm
    # at the child local origin so it sits on the joint axis).
    hook = model.part("sill_hook")
    _cyl_x(
        hook,
        "sill_hook_arm",
        center=(0.0, 0.0, 0.0),
        length=2.0 * r.g + 0.12,
        radius=0.020,
        material=mats["rail"],
    )
    for si, x in ((0, -r.g), (1, r.g)):
        _cyl_x(
            hook,
            f"sill_hook_barrel_{si}",
            center=(x, 0.0, 0.0),
            length=0.06,
            radius=0.026,
            material=mats["bolt"],
        )
    throat, drop = 0.28, 0.22
    for si, x in ((0, -r.g + 0.06), (1, r.g - 0.06)):
        _cyl_y(
            hook,
            f"sill_hook_throat_{si}",
            center=(x, -throat / 2.0, 0.0),
            length=throat,
            radius=0.018,
            material=mats["rail"],
        )
        _cyl_z(
            hook,
            f"sill_hook_finger_{si}",
            center=(x, -throat, -drop / 2.0),
            length=drop,
            radius=0.018,
            material=mats["rail"],
        )
        hook.visual(
            Box((0.04, 0.04, 0.016)),
            origin=Origin(xyz=(x, -throat, -drop - 0.008)),
            material=mats["rail"],
            name=f"sill_hook_tip_{si}", material_class_id=("metal.steel_galvanized" if r.palette_style in {"galvanized_steel", "zinc_plated", "safety_orange", "painted_red_brackets"} else "metal.aluminum_bare"),
        )

    # Deployed at q=0 (hook throat/fingers reach over the sill toward -y); stows
    # by folding UP (negative q) so the throat swings clear of the head bar
    # rather than sweeping down through it.
    model.articulation(
        "sill_hook_pivot",
        ArticulationType.REVOLUTE,
        parent=upper,
        child=hook,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=1.5, lower=-1.30, upper=0.0),
    )


# ===========================================================================
# Family: folding  (folding_articulated: 3 segments + 2 REVOLUTE fold hinges)
# ===========================================================================
def _build_folding(model, r, mats) -> None:
    g, rail_r, rung_r = r.g, r.rail_r, r.rung_r
    seg_rungs = max(2, round(r.rung_count / 3))
    seg_len = (seg_rungs - 1) * r.pitch + 2 * 0.20
    rung_off = 0.20
    seg0_z = 4.0
    pin_len = 2.0 * g + 0.06
    slv_len = 2.0 * g + 0.04

    # Segment 0 — top, wall-anchored.
    seg0 = model.part("ladder_seg_0")
    for x, s in ((-g, "0"), (g, "1")):
        _cyl_z(
            seg0,
            f"seg0_rail_{s}",
            center=(x, 0.0, seg0_z + seg_len / 2.0),
            length=seg_len,
            radius=rail_r,
            material=mats["rail"],
        )
    for i in range(seg_rungs):
        _cyl_x(
            seg0,
            f"seg0_rung_{i}",
            center=(0.0, 0.0, seg0_z + rung_off + i * r.pitch),
            length=r.rung_len,
            radius=rung_r,
            material=mats["rail"],
        )
    for lv, z in enumerate((seg0_z + 0.55 * seg_len, seg0_z + 0.90 * seg_len)):
        for si, x in ((0, -g), (1, g)):
            _wall_anchor(seg0, si, lv, x, z, mats, r.standoff_depth)
    _cyl_x(
        seg0,
        "fold_pin_0",
        center=(0.0, 0.0, seg0_z),
        length=pin_len,
        radius=0.015,
        material=mats["accent"],
    )

    def _segment(name, sleeve_name, pin_name, y_off, with_feet, next_pin):
        seg = model.part(name)
        # Sleeve at the child local origin (on the fold axis).
        _cyl_x(
            seg,
            sleeve_name,
            center=(0.0, 0.0, 0.0),
            length=slv_len,
            radius=0.025,
            material=mats["hardware"],
        )
        for x, s in ((-g, "0"), (g, "1")):
            _cyl_z(
                seg,
                f"{name}_rail_{s}",
                center=(x, y_off, -seg_len / 2.0),
                length=seg_len,
                radius=rail_r,
                material=mats["rail"],
            )
        for i in range(seg_rungs):
            _cyl_x(
                seg,
                f"{name}_rung_{i}",
                center=(0.0, y_off, -(rung_off + i * r.pitch)),
                length=r.rung_len,
                radius=rung_r,
                material=mats["rail"],
            )
        if next_pin is not None:
            _cyl_x(
                seg,
                next_pin,
                center=(0.0, y_off, -seg_len),
                length=pin_len,
                radius=0.015,
                material=mats["accent"],
            )
        if with_feet:
            for x, s in ((-g, "0"), (g, "1")):
                seg.visual(
                    Box((0.06, 0.05, 0.04)),
                    origin=Origin(xyz=(x, y_off, -seg_len)),
                    material=mats["foot"],
                    name=f"rubber_foot_{s}", material_class_id="rubber.smooth_plain",
                )
        return seg

    # Segments stay collinear (y_off=0): at q=0 each child hangs straight below
    # its parent, meeting end-to-end at the hinge pin. Folding forward stays
    # below 90 deg so the swinging child never rises into the parent's column;
    # they only ever touch at the pin knuckle (allowed via element-scoped
    # allow_overlap in run_tests).
    _segment("ladder_seg_1", "fold_sleeve_0", "fold_pin_0", 0.0, False, "fold_pin_1")
    _segment("ladder_seg_2", "fold_sleeve_1", "fold_pin_1", 0.0, True, None)

    seg0p = model.get_part("ladder_seg_0")
    seg1p = model.get_part("ladder_seg_1")
    seg2p = model.get_part("ladder_seg_2")
    fold_upper = 1.45  # < pi/2, keeps the folded child clear of the parent column
    model.articulation(
        "fold_hinge_0",
        ArticulationType.REVOLUTE,
        parent=seg0p,
        child=seg1p,
        origin=Origin(xyz=(0.0, 0.0, seg0_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=50.0, velocity=1.0, lower=0.0, upper=fold_upper),
    )
    model.articulation(
        "fold_hinge_1",
        ArticulationType.REVOLUTE,
        parent=seg1p,
        child=seg2p,
        origin=Origin(xyz=(0.0, 0.0, -seg_len)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=50.0, velocity=1.0, lower=0.0, upper=fold_upper),
    )


# ===========================================================================
# Family: telescoping  (telescoping_multistage: 3 nested stages, 2 PRISMATIC)
# ===========================================================================
def _build_telescoping(model, r, mats) -> None:
    g = r.g
    stage_rungs = max(2, round(r.rung_count / 3))
    s0_last = _RUNG_Z0 + (stage_rungs - 1) * r.pitch
    height = s0_last + 0.24

    stage0 = model.part("stage_0")
    for x, s in ((-g, "0"), (g, "1")):
        _cyl_z(
            stage0,
            f"stage0_rail_{s}",
            center=(x, 0.0, height / 2.0),
            length=height,
            radius=r.rail_r,
            material=mats["rail"],
        )
    for i in range(stage_rungs):
        _cyl_x(
            stage0,
            f"stage0_rung_{i}",
            center=(0.0, 0.0, _RUNG_Z0 + i * r.pitch),
            length=r.rung_len,
            radius=r.rung_r,
            material=mats["rail"],
        )
    for lv, z in enumerate(_standoff_levels(0.45, height - 0.40)):
        for si, x in ((0, -g), (1, g)):
            _wall_anchor(stage0, si, lv, x, z, mats, r.standoff_depth)

    g1 = 0.72 * g
    g2 = 0.48 * g
    collar_z0 = 0.06
    for si, x in ((0, -g1), (1, g1)):
        stage0.visual(
            Box((0.080, 0.070, 0.100)),
            origin=Origin(xyz=(x, 0.060, collar_z0)),
            material=mats["hardware"],
            name=f"stage0_slide_collar_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
        rail_side = -1.0 if x < 0.0 else 1.0
        # Gusset from the stage-0 rail (x=±g) to the collar's OUTBOARD edge
        # (x=±(g1+0.045)) so it never reaches the inner stage-1 rail at ±g1.
        inner = rail_side * (g1 + 0.045)
        outer = rail_side * g
        stage0.visual(
            Box((abs(g - (g1 + 0.045)) + 0.02, 0.09, 0.05)),
            origin=Origin(xyz=((inner + outer) / 2.0, 0.030, collar_z0)),
            material=mats["hardware"],
            name=f"stage0_collar_bracket_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )

    # Stage 1 — nested inner stage, offset forward (+y) so its rungs clear the
    # stage-0 rung plane. Rail spans from below collar0 up near stage0 top; its
    # rungs start ABOVE the collar band so the collar never intersects a rung.
    stage1 = model.part("stage_1")
    s1_y = 0.06
    s1_bot = collar_z0 - 0.12
    s1_top = 0.88 * height
    s1_h = s1_top - s1_bot
    s1_mid = (s1_top + s1_bot) / 2.0
    for x, s in ((-g1, "0"), (g1, "1")):
        _cyl_z(
            stage1,
            f"stage1_rail_{s}",
            center=(x, s1_y, s1_mid),
            length=s1_h,
            radius=r.rail_r * 0.85,
            material=mats["rail"],
        )
    s1_rung_z0 = collar_z0 + 0.18  # first rung well above the collar top
    s1_rungs = max(2, stage_rungs - 1)
    for i in range(s1_rungs):
        z = s1_rung_z0 + i * r.pitch
        if z > s1_top - 0.08:
            break
        _cyl_x(
            stage1,
            f"stage1_rung_{i}",
            center=(0.0, s1_y, z),
            length=2.0 * g1 + 0.04,
            radius=r.rung_r,
            material=mats["rail"],
        )
    collar1_z = s1_bot  # near stage-1 bottom, clear of the stage-0 collar band
    for si, x in ((0, -g2), (1, g2)):
        stage1.visual(
            Box((0.060, 0.060, 0.080)),
            origin=Origin(xyz=(x, s1_y + 0.06, collar1_z)),
            material=mats["hardware"],
            name=f"stage1_slide_collar_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )
        rail_side = -1.0 if x < 0.0 else 1.0
        inner = rail_side * (g2 + 0.04)
        outer = rail_side * g1
        stage1.visual(
            Box((abs(g1 - (g2 + 0.04)) + 0.02, 0.11, 0.05)),
            origin=Origin(xyz=((inner + outer) / 2.0, s1_y + 0.03, collar1_z)),
            material=mats["hardware"],
            name=f"stage1_collar_bracket_{si}", material_class_id=("metal.paint_coated" if r.palette_style in {"safety_orange", "anodized_aluminium", "painted_red_brackets"} else "metal.steel_galvanized"),
        )

    # Stage 2 — innermost, offset further forward.
    stage2 = model.part("stage_2")
    s2_y = 0.12
    s2_bot = collar1_z - 0.12
    s2_top = 0.72 * height
    s2_h = s2_top - s2_bot
    s2_mid = (s2_top + s2_bot) / 2.0
    for x, s in ((-g2, "0"), (g2, "1")):
        _cyl_z(
            stage2,
            f"stage2_rail_{s}",
            center=(x, s2_y, s2_mid),
            length=s2_h,
            radius=r.rail_r * 0.70,
            material=mats["rail"],
        )
    s2_rung_z0 = collar1_z + 0.18
    s2_rungs = max(2, stage_rungs - 2)
    for i in range(s2_rungs):
        z = s2_rung_z0 + i * r.pitch
        if z > s2_top - 0.08:
            break
        _cyl_x(
            stage2,
            f"stage2_rung_{i}",
            center=(0.0, s2_y, z),
            length=2.0 * g2 + 0.035,
            radius=r.rung_r,
            material=mats["rail"],
        )
    _cyl_x(
        stage2,
        "stage2_foot_bar",
        center=(0.0, s2_y, s2_bot),
        length=2.0 * g2 + 0.10,
        radius=0.020,
        material=mats["rail"],
    )

    # Travel is clamped to keep each inner rail retained in its collar
    # (retained overlap >= 0.30 at full deploy).
    s1_travel = _clamp(1.60 * r.drop_travel, 0.20, s1_h - 0.30)
    s2_travel = _clamp(1.30 * r.drop_travel, 0.20, s2_h - 0.30)
    model.articulation(
        "stage0_to_stage1",
        ArticulationType.PRISMATIC,
        parent=stage0,
        child=stage1,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=120.0, velocity=0.35, lower=0.0, upper=s1_travel
        ),
    )
    model.articulation(
        "stage1_to_stage2",
        ArticulationType.PRISMATIC,
        parent=stage1,
        child=stage2,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=100.0, velocity=0.30, lower=0.0, upper=s2_travel
        ),
    )


_FAMILY_BUILDERS = {
    "fixed_cage": _build_fixed_cage,
    "portable_hook": _build_portable_hook,
    "folding": _build_folding,
    "telescoping": _build_telescoping,
}


def build_fire_escape_ladder(
    config: FireEscapeLadderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"fel_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    _FAMILY_BUILDERS[r.ladder_family](model, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_fire_escape_ladder(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_fire_escape_ladder(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_fire_escape_ladder_tests(
    object_model: ArticulatedObject,
    config: FireEscapeLadderConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    # ---- Captured-pin / captured-slide allowances (element-scoped). ----
    if r.ladder_family == "fixed_cage":
        fixed = object_model.get_part("fixed_ladder")
        lower = object_model.get_part("lower_ladder")
        if r.deploy == "prismatic_drop":
            for i in (0, 1):
                ctx.allow_overlap(
                    fixed,
                    lower,
                    elem_a=f"lower_slide_collar_{i}",
                    elem_b=f"lower_rail_{i}",
                    reason="The sliding lower rail is captured inside the fixed guide collar.",
                )
        else:  # revolute_swing
            for i in (0, 1):
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a="swing_sleeve",
                    elem_b=f"hinge_ear_{i}",
                    reason="Swing sleeve is captured between the hinge bracket ears.",
                )
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a="swing_pin",
                    elem_b=f"hinge_ear_{i}",
                    reason="Swing pin passes through the hinge ear (pivot axis).",
                )
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a=f"swing_pin_cap_{i}",
                    elem_b=f"hinge_ear_{i}",
                    reason="Swing pin cap retains the pivot pin outside the hinge ear.",
                )
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a=f"swing_pin_cap_{i}",
                    elem_b="hinge_cross_brace",
                    reason="Swing pin cap overlaps the cross brace at the pivot capture.",
                )
            for elem in ("swing_sleeve", "swing_pin", "counterweight_arm"):
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a=elem,
                    elem_b="hinge_cross_brace",
                    reason="Hinge hardware passes through the cross brace at the pivot axis.",
                )
            for i in (0, 1):
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a=f"hinge_bracket_{i}",
                    elem_b="hinge_cross_brace",
                    reason="The child hinge bracket sweeps past the cross brace near the pivot.",
                )
                ctx.allow_overlap(
                    lower,
                    fixed,
                    elem_a=f"hinge_bracket_{i}",
                    elem_b=f"hinge_ear_{i}",
                    reason="The child hinge bracket sweeps past the hinge ear near the pivot.",
                )
                for elem in ("swing_sleeve", "swing_pin", f"swing_pin_cap_{i}"):
                    ctx.allow_overlap(
                        lower,
                        fixed,
                        elem_a=elem,
                        elem_b=f"hinge_gusset_{i}",
                        reason="Swing hinge hardware overlaps the hinge gusset at the pivot.",
                    )
        if r.guard_system == "fall_arrest":
            shuttle = object_model.get_part("arrest_shuttle")
            ctx.allow_overlap(
                fixed,
                shuttle,
                elem_a="arrest_rail",
                elem_b="shuttle_body",
                reason="The travelling shuttle clamp wraps around the fall-arrest rail.",
            )
            # The shuttle slides along the rail past the standoff brackets that
            # tie the rail to the ladder (the real clamp is an open C-channel).
            for bv in [
                v for v in fixed.visuals if v.name.startswith("arrest_bracket_")
            ]:
                ctx.allow_overlap(
                    fixed,
                    shuttle,
                    elem_a=bv.name,
                    elem_b="shuttle_body",
                    reason="The shuttle passes the rail standoff brackets as it travels.",
                )
    elif r.ladder_family == "portable_hook":
        upper = object_model.get_part("ladder_body")
        hook = object_model.get_part("sill_hook")
        for i in (0, 1):
            ctx.allow_overlap(
                hook,
                upper,
                elem_a=f"sill_hook_barrel_{i}",
                elem_b="head_bar",
                reason="The hinge barrel wraps around the ladder head bar at the pivot.",
            )
        ctx.allow_overlap(
            hook,
            upper,
            elem_a="sill_hook_arm",
            elem_b="head_bar",
            reason="The hook cross-arm is the hinge pin passing through the head bar at the pivot.",
        )
        ctx.allow_overlap(
            hook,
            upper,
            elem_a="sill_hook_arm",
            elem_b="pivot_boss",
            reason="The hook cross-arm passes through the pivot boss at the hinge axis.",
        )
    elif r.ladder_family == "folding":
        seg0 = object_model.get_part("ladder_seg_0")
        seg1 = object_model.get_part("ladder_seg_1")
        seg2 = object_model.get_part("ladder_seg_2")
        ctx.allow_overlap(
            seg0, seg1, elem_a="fold_pin_0", elem_b="fold_sleeve_0",
            reason="Fold hinge sleeve captures the pin (pinned revolute joint).",
        )
        ctx.allow_overlap(
            seg1, seg2, elem_a="fold_pin_1", elem_b="fold_sleeve_1",
            reason="Fold hinge sleeve captures the pin (pinned revolute joint).",
        )
        for s in ("0", "1"):
            ctx.allow_overlap(
                seg0, seg1, elem_a="fold_pin_0", elem_b=f"ladder_seg_1_rail_{s}",
                reason="Pin passes through the child rail end at the hinge.",
            )
            ctx.allow_overlap(
                seg1, seg2, elem_a="fold_pin_1", elem_b=f"ladder_seg_2_rail_{s}",
                reason="Pin passes through the child rail end at the hinge.",
            )
            ctx.allow_overlap(
                seg0, seg1, elem_a=f"seg0_rail_{s}", elem_b="fold_sleeve_0",
                reason="Sleeve contacts the parent rail end at the hinge barrel.",
            )
            ctx.allow_overlap(
                seg1, seg2, elem_a=f"ladder_seg_1_rail_{s}", elem_b="fold_sleeve_1",
                reason="Sleeve contacts the parent rail end at the hinge barrel.",
            )
            ctx.allow_overlap(
                seg0, seg1, elem_a=f"seg0_rail_{s}", elem_b=f"ladder_seg_1_rail_{s}",
                reason="Adjacent segment rail ends share the hinge knuckle about the fold pin.",
            )
            ctx.allow_overlap(
                seg1, seg2, elem_a=f"ladder_seg_1_rail_{s}", elem_b=f"ladder_seg_2_rail_{s}",
                reason="Adjacent segment rail ends share the hinge knuckle about the fold pin.",
            )
    else:  # telescoping
        stage0 = object_model.get_part("stage_0")
        stage1 = object_model.get_part("stage_1")
        stage2 = object_model.get_part("stage_2")
        for i in (0, 1):
            ctx.allow_overlap(
                stage0, stage1, elem_a=f"stage0_slide_collar_{i}",
                elem_b=f"stage1_rail_{i}",
                reason="Stage 1 rail captured inside the stage 0 guide collar.",
            )
            ctx.allow_overlap(
                stage1, stage2, elem_a=f"stage1_slide_collar_{i}",
                elem_b=f"stage2_rail_{i}",
                reason="Stage 2 rail captured inside the stage 1 guide collar.",
            )
        # Inner-stage rungs pass through the outer simplified guide collars as
        # the ladder telescopes (the real guide is an open channel at the rail).
        for i in (0, 1):
            for rv in [v for v in stage1.visuals if v.name.startswith("stage1_rung_")]:
                ctx.allow_overlap(
                    stage0, stage1, elem_a=f"stage0_slide_collar_{i}", elem_b=rv.name,
                    reason="Inner-stage rung passes the outer guide collar during telescoping.",
                )
            for rv in [v for v in stage2.visuals if v.name.startswith("stage2_rung_")]:
                ctx.allow_overlap(
                    stage1, stage2, elem_a=f"stage1_slide_collar_{i}", elem_b=rv.name,
                    reason="Inner-stage rung passes the outer guide collar during telescoping.",
                )

    # ---- Compiler baseline (mirrors sweep). ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        f"family={r.ladder_family} root present",
        len(part_names) >= 1,
        details=str(sorted(part_names)),
    )

    # Rung multiplicity via for-loop.
    def _count_rungs(part, prefix):
        return len(
            [
                v
                for v in part.visuals
                if v.name.startswith(prefix) and "spacer" not in v.name
            ]
        )

    if r.ladder_family == "fixed_cage":
        n = _count_rungs(object_model.get_part("fixed_ladder"), "fixed_rung_")
        ctx.check("N rungs emitted", n == r.rung_count, details=f"got {n} expected {r.rung_count}")
    elif r.ladder_family == "portable_hook":
        n = _count_rungs(object_model.get_part("ladder_body"), "rung_")
        ctx.check("N rungs emitted", n == r.rung_count, details=f"got {n}")

    # slot_choices recorded.
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Deploy joint topology + targeted motion (Rule 5). ----
    if r.ladder_family == "fixed_cage":
        j = object_model.get_articulation("ladder_to_lower")
        lower = object_model.get_part("lower_ladder")
        if r.deploy == "prismatic_drop":
            ctx.check(
                "drop is PRISMATIC -z",
                j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            p0 = ctx.part_world_position(lower)
            with ctx.pose({j: r.drop_travel}):
                p1 = ctx.part_world_position(lower)
            if p0 and p1:
                ctx.check(
                    "lower ladder drops downward",
                    p1[2] < p0[2] - 0.5,
                    details=f"rest={p0[2]:.3f} deployed={p1[2]:.3f}",
                )
        else:
            ctx.check(
                "swing is REVOLUTE +x",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            a0 = ctx.part_element_world_aabb(lower, elem="lower_foot_bar")
            with ctx.pose({j: 2.90}):
                a1 = ctx.part_element_world_aabb(lower, elem="lower_foot_bar")
            if a0 and a1:
                ctx.check(
                    "swing drops the foot bar",
                    a1[0][2] < a0[0][2] - 0.5,
                    details=f"stowed={a0[0][2]:.3f} deployed={a1[0][2]:.3f}",
                )
        if r.guard_system == "fall_arrest":
            sj = object_model.get_articulation("shuttle_to_rail")
            shuttle = object_model.get_part("arrest_shuttle")
            s0 = ctx.part_world_position(shuttle)
            with ctx.pose({sj: sj.motion_limits.upper}):
                s1 = ctx.part_world_position(shuttle)
            if s0 and s1:
                ctx.check(
                    "shuttle slides up the arrest rail",
                    s1[2] > s0[2] + 0.7 * sj.motion_limits.upper,
                    details=f"rest={s0[2]:.3f} high={s1[2]:.3f} travel={sj.motion_limits.upper:.3f}",
                )
    elif r.ladder_family == "portable_hook":
        j = object_model.get_articulation("sill_hook_pivot")
        hook = object_model.get_part("sill_hook")
        ctx.check(
            "sill hook is REVOLUTE +x",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        a0 = ctx.part_element_world_aabb(hook, elem="sill_hook_finger_0")
        with ctx.pose({j: -1.2}):
            a1 = ctx.part_element_world_aabb(hook, elem="sill_hook_finger_0")
        if a0 and a1:
            ctx.check(
                "sill hook folds",
                abs(a1[1][2] - a0[1][2]) > 0.05,
                details=f"rest={a0[1][2]:.3f} folded={a1[1][2]:.3f}",
            )
    elif r.ladder_family == "folding":
        for jn, cn, en in (
            ("fold_hinge_0", "ladder_seg_1", "ladder_seg_1_rail_0"),
            ("fold_hinge_1", "ladder_seg_2", "ladder_seg_2_rail_0"),
        ):
            j = object_model.get_articulation(jn)
            child = object_model.get_part(cn)
            ctx.check(
                f"{jn} is REVOLUTE +x",
                j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
                details=f"axis={tuple(j.axis)}",
            )
            a0 = ctx.part_element_world_aabb(child, elem=en)
            with ctx.pose({j: 1.4}):
                a1 = ctx.part_element_world_aabb(child, elem=en)
            if a0 and a1:
                ctx.check(
                    f"{jn} swings the segment",
                    abs(a1[0][2] - a0[0][2]) > 0.3,
                    details=f"rest={a0[0][2]:.3f} folded={a1[0][2]:.3f}",
                )
    else:  # telescoping
        for jn, cn in (("stage0_to_stage1", "stage_1"), ("stage1_to_stage2", "stage_2")):
            j = object_model.get_articulation(jn)
            child = object_model.get_part(cn)
            ctx.check(
                f"{jn} is PRISMATIC -z",
                j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
                details=f"axis={tuple(j.axis)}",
            )
            p0 = ctx.part_world_position(child)
            with ctx.pose({j: j.motion_limits.upper}):
                p1 = ctx.part_world_position(child)
            if p0 and p1:
                ctx.check(
                    f"{jn} extends downward",
                    p1[2] < p0[2] - 0.9 * j.motion_limits.upper,
                    details=f"rest={p0[2]:.3f} ext={p1[2]:.3f} travel={j.motion_limits.upper:.3f}",
                )

    # ---- Full-travel sampled-pose overlap gate (Rule 5). ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    return ctx.report()


__all__ = (
    "FireEscapeLadderConfig",
    "ResolvedFireEscapeLadderConfig",
    "build_fire_escape_ladder",
    "build_seeded_fire_escape_ladder",
    "config_from_seed",
    "resolve_config",
    "run_fire_escape_ladder_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
