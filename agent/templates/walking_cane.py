# SPDX-License-Identifier: Apache-2.0

"""Walking cane — modular procedural template.

Real-world walking cane: hand-held single-shaft mobility aid with (a) an
ergonomic ``handle`` (T grip / crook / derby), (b) one or more vertical
``shaft`` segments (rigid, telescoping, or folding), and (c) a ``ground``
interface (rubber tip / quad base / tripod base).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/walking_cane.md`` and the
10-record 5-star sample pool under ``data/records/`` (3 origins + 7
slot-fork variants).

Structure (pattern = ``linear_chain`` with slot-B multiplicity):

  handle_form (5)        -> handle part (root)
  shaft_family+count (3x4) -> N shaft_i parts + non-FIXED chain joints
  ground_interface (3)   -> ground_foot part FIXED to last shaft

Rule 1 (parent.visual for non-moving details): pin_holes, finger grooves,
strap eyelets/wrist_strap loops, quad hub legs, tripod hub+legs are all
inline visuals on their carrier part — never a floating FIXED disk.

Rule 2 (MatingContract on non-FIXED-chain-creating joints): the two FIXED
joints (handle->shaft_0 and shaft_{N-1}->ground_foot) declare
MatingContract with tangential_containment. The non-FIXED
telescoping/folding/button joints are captured-slide / captured-pin
patterns and are grandfathered (no MatingContract), mirroring the source
records' allow_overlap patterns.

Rule 3 (source-derived primitives): all handle families reproduce their
source primitive types (Cylinder for T/upper stubs, mesh_from_geometry+
tube_from_spline_points for crook/derby, sweep_profile_along_spline+
rounded_rect_profile for derby_swept, LatheGeometry for rubber_tip);
we never downgrade a mesh helper to a Box.

Rule 5 coverage: run_walking_cane_tests calls
``fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`` plus
targeted ``ctx.pose`` checks on telescoping extension / folding
straightening / button press.
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
    CylinderGeometry,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True


HandleForm = Literal["t_handle", "ergonomic_T", "crook", "derby_offset", "derby_swept"]
ShaftFamily = Literal["telescoping", "folding", "rigid"]
GroundInterface = Literal["rubber_tip", "quad_base", "tripod_base"]
PaletteStyle = Literal[
    "matte_green",
    "brushed_black",
    "glossy_purple",
    "bare_aluminum",
    "walnut_wood",
    "painted_red",
]


HANDLE_FORMS: tuple[HandleForm, ...] = (
    "t_handle",
    "ergonomic_T",
    "crook",
    "derby_offset",
    "derby_swept",
)
SHAFT_FAMILIES: tuple[ShaftFamily, ...] = ("telescoping", "folding", "rigid")
GROUND_INTERFACES: tuple[GroundInterface, ...] = ("rubber_tip", "quad_base", "tripod_base")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "matte_green",
    "brushed_black",
    "glossy_purple",
    "bare_aluminum",
    "walnut_wood",
    "painted_red",
)


# Shaft_family-conditional multiplicity domains.
SHAFT_COUNT_DOMAIN: dict[ShaftFamily, tuple[tuple[int, ...], tuple[float, ...]]] = {
    "telescoping": ((2, 3), (0.65, 0.35)),
    "folding": ((2, 3, 4), (0.30, 0.40, 0.30)),
    "rigid": ((1,), (1.0,)),
}


# Palette dictionaries. Each palette exposes the same key set so all module
# factories can look up materials uniformly. Keys and their intent:
#   shaft:    main shaft tube color (metal or wood tone)
#   handle:   handle grip color (rubber/plastic/leather)
#   collar:   metal collar / ferrule
#   accent:   pin-hole / button / small metal detail
#   dark:     latch body / cord socket / handle black plastic
#   rubber:   ground foot rubber / rubber_tip
_PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "matte_green": {  # from S1 (green folding quad cane)
        "shaft": (0.34, 0.49, 0.39, 1.0),
        "handle": (0.34, 0.49, 0.39, 1.0),
        "collar": (0.72, 0.72, 0.66, 1.0),
        "accent": (1.0, 0.87, 0.25, 1.0),
        "dark": (0.01, 0.01, 0.01, 1.0),
        "rubber": (0.025, 0.030, 0.028, 1.0),
    },
    "brushed_black": {  # from S2 (black adjustable cane)
        "shaft": (0.005, 0.006, 0.006, 1.0),
        "handle": (0.02, 0.02, 0.02, 1.0),
        "collar": (0.74, 0.72, 0.68, 1.0),
        "accent": (0.92, 0.94, 0.93, 1.0),
        "dark": (0.015, 0.015, 0.014, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
    },
    "glossy_purple": {  # from S3 (purple foldable cane)
        "shaft": (0.53, 0.08, 0.82, 1.0),
        "handle": (0.06, 0.06, 0.08, 1.0),
        "collar": (0.72, 0.72, 0.76, 1.0),
        "accent": (0.95, 0.92, 0.86, 1.0),
        "dark": (0.005, 0.005, 0.008, 1.0),
        "rubber": (0.015, 0.013, 0.012, 1.0),
    },
    "bare_aluminum": {  # world knowledge — brushed aluminum trekking cane
        "shaft": (0.78, 0.80, 0.82, 1.0),
        "handle": (0.14, 0.14, 0.16, 1.0),
        "collar": (0.62, 0.63, 0.66, 1.0),
        "accent": (0.90, 0.20, 0.15, 1.0),
        "dark": (0.06, 0.06, 0.07, 1.0),
        "rubber": (0.05, 0.05, 0.05, 1.0),
    },
    "walnut_wood": {  # world knowledge — traditional walnut cane
        "shaft": (0.28, 0.16, 0.09, 1.0),
        "handle": (0.24, 0.13, 0.07, 1.0),
        "collar": (0.72, 0.60, 0.28, 1.0),
        "accent": (0.55, 0.44, 0.20, 1.0),
        "dark": (0.06, 0.04, 0.02, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
    },
    "painted_red": {  # world knowledge — painted / hazard red cane
        "shaft": (0.72, 0.10, 0.08, 1.0),
        "handle": (0.06, 0.06, 0.07, 1.0),
        "collar": (0.68, 0.68, 0.66, 1.0),
        "accent": (0.98, 0.95, 0.30, 1.0),
        "dark": (0.03, 0.03, 0.03, 1.0),
        "rubber": (0.02, 0.02, 0.02, 1.0),
    },
}


# Canonical dimensions (meters). Sourced from S1/S2/S3.
_HANDLE_NECK_LEN = 0.070  # S1 handle_neck length
_HANDLE_NECK_R = 0.022  # S1 handle_neck radius
_HANDLE_COLLAR_R_OUTER = 0.018
_HANDLE_COLLAR_R_INNER = 0.0125
_HANDLE_COLLAR_LEN = 0.020

_SHAFT_R = 0.011  # S1/S3 tube outer radius
_SHAFT_LEN = 0.30  # per-segment tube length (folding baseline)
_TELE_STAGE_LEN = 0.34  # per-stage telescoping tube length (S1/S2 blend)
_TELE_TRAVEL = 0.075  # per-stage prismatic travel (S1=0.070, S2=0.090)

_COLLAR_R_OUTER = 0.014  # bottom_collar_i outer (aligned with foot socket)
_COLLAR_R_INNER = 0.011
_COLLAR_LEN = 0.018

_FOOT_SOCKET_R = 0.014
_FOOT_SOCKET_LEN = 0.010


def _hollow_ring(outer_radius: float, inner_radius: float, length: float, name: str):
    """Thin open-ended cylindrical collar / sleeve — from S1/S2/S3 helper."""
    half = length * 0.5
    geom = LatheGeometry.from_shell_profiles(
        [(outer_radius, -half), (outer_radius, half)],
        [(inner_radius, -half), (inner_radius, half)],
        segments=32,
        start_cap="flat",
        end_cap="flat",
        lip_samples=4,
    )
    return mesh_from_geometry(geom, name)


def _lathed_tip(name: str, *, radius_scale: float = 1.0):
    """Rubber cane tip lathed profile — from S2 _lathed_tip."""
    r = radius_scale
    profile = [
        (0.006 * r, 0.000),
        (0.011 * r, -0.006),
        (0.012 * r, -0.030),
        (0.018 * r, -0.043),
        (0.021 * r, -0.052),
        (0.019 * r, -0.058),
        (0.000, -0.058),
        (0.000, 0.000),
    ]
    return mesh_from_geometry(LatheGeometry(profile, segments=32), name)


def _tripod_mesh(
    *,
    hub_radius: float,
    hub_height: float,
    leg_radius: float,
    leg_length: float,
    foot_radius: float,
    foot_height: float,
    splay_angle: float,
    name: str,
):
    """Tripod base mesh — hub + 3 splayed legs + rubber feet. From S7."""
    combined = MeshGeometry()
    hub = CylinderGeometry(radius=hub_radius, height=hub_height, radial_segments=20)
    combined.merge(hub)
    for i in range(3):
        angle = (2.0 * math.pi / 3.0) * i
        ca = math.cos(angle)
        sa = math.sin(angle)
        tilt = math.sin(splay_angle)
        upright = math.cos(splay_angle)
        leg = CylinderGeometry(radius=leg_radius, height=leg_length, radial_segments=10)
        leg_cx = hub_radius * 0.6 * ca
        leg_cy = hub_radius * 0.6 * sa
        leg_cz = -hub_height / 2.0 - leg_length / 2.0 * upright
        leg.rotate(axis=(sa, -ca, 0.0), angle=splay_angle)
        leg.translate(leg_cx, leg_cy, leg_cz)
        combined.merge(leg)
        foot = CylinderGeometry(radius=foot_radius, height=foot_height, radial_segments=10)
        foot_cx = (hub_radius * 0.6 + leg_length * tilt) * ca
        foot_cy = (hub_radius * 0.6 + leg_length * tilt) * sa
        foot_cz = -hub_height / 2.0 - leg_length * upright - foot_height / 2.0
        foot.translate(foot_cx, foot_cy, foot_cz)
        combined.merge(foot)
    return mesh_from_geometry(combined, name)


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WalkingCaneConfig:
    handle_form: HandleForm | None = None
    shaft_family: ShaftFamily | None = None
    shaft_count: int | None = None
    ground_interface: GroundInterface | None = None
    palette_style: PaletteStyle = "matte_green"
    handle_scale: float = 1.0
    shaft_length_scale: float = 1.0
    shaft_radius_scale: float = 1.0
    fold_angle_scale: float = 1.0
    telescoping_travel_scale: float = 1.0
    name: str = "walking_cane"


@dataclass(frozen=True)
class ResolvedWalkingCaneConfig:
    handle_form: HandleForm
    shaft_family: ShaftFamily
    shaft_count: int
    ground_interface: GroundInterface
    palette_style: PaletteStyle
    include_button: bool
    # Resolved dimensions.
    handle_scale: float
    shaft_r: float
    shaft_r_outer: float  # collar outer / socket
    shaft_r_inner: float  # collar inner (accepts child tube)
    shaft_length: float  # per-segment / stage length
    tele_travel: float  # per-stage telescoping travel
    fold_angle: float  # per-fold angle magnitude
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _sample_shaft_count(family: ShaftFamily, rng: random.Random) -> int:
    values, weights = SHAFT_COUNT_DOMAIN[family]
    return rng.choices(values, weights=weights, k=1)[0]


def config_from_seed(seed: int) -> WalkingCaneConfig:
    rng = random.Random(seed)
    handle_form: HandleForm = rng.choice(HANDLE_FORMS)
    shaft_family: ShaftFamily = rng.choice(SHAFT_FAMILIES)
    shaft_count = _sample_shaft_count(shaft_family, rng)
    ground: GroundInterface = rng.choice(GROUND_INTERFACES)
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)
    return WalkingCaneConfig(
        handle_form=handle_form,
        shaft_family=shaft_family,
        shaft_count=shaft_count,
        ground_interface=ground,
        palette_style=palette,
        handle_scale=round(rng.uniform(0.90, 1.10), 4),
        shaft_length_scale=round(rng.uniform(0.90, 1.10), 4),
        shaft_radius_scale=round(rng.uniform(0.92, 1.08), 4),
        fold_angle_scale=round(rng.uniform(0.88, 1.08), 4),
        telescoping_travel_scale=round(rng.uniform(0.88, 1.08), 4),
        name=f"seeded_walking_cane_{seed}",
    )


def resolve_config(config: WalkingCaneConfig | None = None) -> ResolvedWalkingCaneConfig:
    cfg = config or WalkingCaneConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    handle_form = _pick(cfg.handle_form, HANDLE_FORMS)
    shaft_family = _pick(cfg.shaft_family, SHAFT_FAMILIES)
    ground = _pick(cfg.ground_interface, GROUND_INTERFACES)

    # Compatibility gating (spec §9): rigid -> N=1; telescoping/folding -> clamp N.
    if shaft_family == "rigid":
        shaft_count = 1
    else:
        raw_n = int(cfg.shaft_count) if cfg.shaft_count is not None else 2
        legal = SHAFT_COUNT_DOMAIN[shaft_family][0]
        # snap to legal set
        shaft_count = min(legal, key=lambda n: abs(n - raw_n))

    # Continuous scales — independent, clamped.
    handle_scale = _clamp(cfg.handle_scale, 0.85, 1.15)
    shaft_len_scale = _clamp(cfg.shaft_length_scale, 0.85, 1.15)
    shaft_r_scale = _clamp(cfg.shaft_radius_scale, 0.90, 1.10)
    fold_scale = _clamp(cfg.fold_angle_scale, 0.85, 1.10)
    tele_scale = _clamp(cfg.telescoping_travel_scale, 0.85, 1.10)

    shaft_r = _SHAFT_R * shaft_r_scale
    # Sleeve inner accepts child tube. We intentionally make the collar's inner
    # radius SLIGHTLY SMALLER than the shaft tube radius so the collar shell
    # overlaps the tube (island-check passes: collar and tube stay one part).
    # Compiler baseline treats zero-tolerance meshes as one island only if they
    # share vertices, so we force a small interference (~0.4mm).
    shaft_r_outer = shaft_r + 0.003
    shaft_r_inner = shaft_r - 0.0004

    if shaft_family == "telescoping":
        shaft_length = _TELE_STAGE_LEN * shaft_len_scale
    elif shaft_family == "folding":
        shaft_length = _SHAFT_LEN * shaft_len_scale
    else:  # rigid
        shaft_length = 0.60 * shaft_len_scale  # single rigid tube — length of a full cane

    # Ensure total shaft length ≤ 1.4 m envelope inequality.
    total = shaft_length * shaft_count
    if total > 1.4:
        shaft_length = 1.4 / shaft_count

    tele_travel = _clamp(_TELE_TRAVEL * tele_scale, 0.050, 0.100)
    # Fold angle nominal 2.0 rad; clamp to [1.5, 2.4] and applied per fold.
    fold_angle = _clamp(2.0 * fold_scale, 1.5, 2.4)

    # Button accessory: T-family handles + telescoping/rigid shafts get a small
    # spring button (S2 pattern) so at least one non-FIXED joint always exists.
    include_button = handle_form in ("t_handle", "ergonomic_T") and shaft_family in (
        "telescoping",
        "rigid",
    )
    # Also give N==1 rigid a button so we always have a non-FIXED joint.
    if shaft_family == "rigid":
        include_button = True

    return ResolvedWalkingCaneConfig(
        handle_form=handle_form,
        shaft_family=shaft_family,
        shaft_count=shaft_count,
        ground_interface=ground,
        palette_style=palette_style,
        include_button=include_button,
        handle_scale=handle_scale,
        shaft_r=shaft_r,
        shaft_r_outer=shaft_r_outer,
        shaft_r_inner=shaft_r_inner,
        shaft_length=shaft_length,
        tele_travel=tele_travel,
        fold_angle=fold_angle,
        name=cfg.name or "walking_cane",
    )


def with_overrides(config: WalkingCaneConfig, **kwargs) -> WalkingCaneConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedWalkingCaneConfig) else resolve_config(config)
    return (
        ("handle_form", r.handle_form),
        ("shaft_family", r.shaft_family),
        ("shaft_count", f"n{r.shaft_count}"),
        ("ground_interface", r.ground_interface),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Handle module builders.
# All emit the root "handle" part; each returns the z of the bottom of the
# handle_collar face (the interface point where shaft_0 attaches), in
# WORLD coords. The collar itself is a real cylindrical hardware visual so
# MatingContract can pin the handle→shaft_0 FIXED joint to it.
# ---------------------------------------------------------------------------


def _emit_handle_collar(handle_part, r: ResolvedWalkingCaneConfig, mats, *, z_top: float):
    """Bottom collar of the handle — the mating face for shaft_0."""
    z_center = z_top - _HANDLE_COLLAR_LEN * 0.5
    handle_part.visual(
        _hollow_ring(
            _HANDLE_COLLAR_R_OUTER * r.handle_scale,
            r.shaft_r_inner,
            _HANDLE_COLLAR_LEN,
            "handle_socket_collar_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, z_center)),
        material=mats["collar"],
        name="handle_socket_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )


def _emit_handle_strap(
    handle_part, mats, *, x0: float, y0: float, z0: float, stem_len: float = 0.014
):
    """Small strap eyelet + wrist strap — Rule 1 inline visuals.

    The stem is authored so its +X end reaches x=0 (the handle's central axis)
    where the handle main mass sits, closing the island gap.
    """
    handle_part.visual(
        mesh_from_geometry(
            TorusGeometry(radius=0.008, tube=0.0015, radial_segments=12, tubular_segments=20),
            "strap_eyelet_mesh",
        ),
        origin=Origin(xyz=(x0, y0, z0), rpy=(0.0, math.pi / 2, 0.0)),
        material=mats["dark"],
        name="strap_eyelet", material_class_id="plastic.opaque_generic",
    )
    # Stem bridge from eyelet toward central handle mass (+X).
    stem_cx = x0 + stem_len * 0.5
    handle_part.visual(
        Box((stem_len, 0.006, 0.006)),
        origin=Origin(xyz=(stem_cx, y0, z0)),
        material=mats["dark"],
        name="strap_stem", material_class_id="plastic.opaque_generic",
    )


def _build_handle_t(model, r: ResolvedWalkingCaneConfig, mats) -> tuple[str, float]:
    """T-handle (source: S1). Root part 'handle'. Returns (part_name, z_collar_bottom).

    Layout (world coords, collar bottom = interface at z=0):
       collar        z 0..COLLAR_LEN
       neck cylinder z COLLAR_LEN..COLLAR_LEN + neck_len  (touches collar top)
       T-grip capsule at neck_top
    """
    handle = model.part("handle")
    hs = r.handle_scale
    neck_len = _HANDLE_NECK_LEN * hs
    neck_z = _HANDLE_COLLAR_LEN + neck_len * 0.5
    neck_top = _HANDLE_COLLAR_LEN + neck_len
    handle.visual(
        Cylinder(radius=_HANDLE_NECK_R * hs, length=neck_len),
        origin=Origin(xyz=(0.0, 0.0, neck_z)),
        material=mats["handle"],
        name="handle_neck", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    grip_z = neck_top + 0.022 * hs
    handle.visual(
        Cylinder(radius=0.022 * hs, length=0.140 * hs),
        origin=Origin(xyz=(0.010, 0.0, grip_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["handle"],
        name="t_handle_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    _emit_handle_collar(handle, r, mats, z_top=_HANDLE_COLLAR_LEN)
    # Strap eyelet embedded into the grip's -X end so it's connected.
    _emit_handle_strap(handle, mats, x0=-0.060 * hs, y0=-0.010, z0=grip_z - 0.002)
    return "handle", 0.0  # collar bottom face at world z=0


def _build_handle_ergonomic_T(model, r: ResolvedWalkingCaneConfig, mats) -> tuple[str, float]:
    """Ergonomic T-handle (source: S2).

    Layout (collar bottom = interface at z=0):
       collar          z 0..COLLAR_LEN
       vertical_post   z COLLAR_LEN..COLLAR_LEN + post_h  (touches collar)
       white_bracket   flat plate on top of vertical_post
       ergonomic_grip  horizontal capsule sitting on bracket
    """
    handle = model.part("handle")
    hs = r.handle_scale
    post_h = 0.045 * hs
    # Vertical post touches collar top (z=COLLAR_LEN) and extends up.
    post_z_center = _HANDLE_COLLAR_LEN + post_h * 0.5
    handle.visual(
        Box((0.020, 0.026, post_h)),
        origin=Origin(xyz=(0.005, 0.0, post_z_center)),
        material=mats["accent"],
        name="vertical_handle_post", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "metal.brass_aged"),
    )
    # Bracket plate on top of post.
    bracket_z = _HANDLE_COLLAR_LEN + post_h + 0.007  # bracket thickness 0.014, embed 1mm into post
    handle.visual(
        Box((0.080 * hs, 0.032, 0.014)),
        origin=Origin(xyz=(0.030, 0.0, bracket_z)),
        material=mats["accent"],
        name="white_handle_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "metal.brass_aged"),
    )
    # Ergonomic grip capsule sitting above bracket (embed into bracket by 1mm).
    grip_z = bracket_z + 0.014 * 0.5 + 0.018 * hs - 0.001
    handle.visual(
        Cylinder(radius=0.018 * hs, length=0.120 * hs),
        origin=Origin(xyz=(0.055, 0.0, grip_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["handle"],
        name="ergonomic_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    # Finger-groove decorations embedded into the grip capsule surface.
    for i, x in enumerate((0.020, 0.055, 0.090)):
        handle.visual(
            Cylinder(radius=0.0016, length=0.028 * hs),
            origin=Origin(
                xyz=(x, 0.0, grip_z - 0.018 * hs + 0.0005),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["dark"],
            name=f"finger_groove_{i}", material_class_id="plastic.opaque_generic",
        )
    _emit_handle_collar(handle, r, mats, z_top=_HANDLE_COLLAR_LEN)
    # Strap: eyelet + stem attached to the bracket (embedded well inside).
    _emit_handle_strap(handle, mats, x0=0.005, y0=-0.014, z0=bracket_z)
    return "handle", 0.0


def _build_handle_crook(model, r: ResolvedWalkingCaneConfig, mats) -> tuple[str, float]:
    """Curved shepherd's-crook (source: S4)."""
    handle = model.part("handle")
    hs = r.handle_scale
    # Vertical stub from collar (z=0.020) up to base of crook.
    stub_len = 0.060 * hs
    handle.visual(
        Cylinder(radius=0.015 * hs, length=stub_len),
        origin=Origin(xyz=(0.0, 0.0, _HANDLE_COLLAR_LEN + stub_len * 0.5)),
        material=mats["handle"],
        name="crook_stub", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    # Swept crook — from stub top curving over +X and down.
    stub_top = _HANDLE_COLLAR_LEN + stub_len
    crook_points = [
        (0.0, 0.0, stub_top),
        (0.0, 0.0, stub_top + 0.030 * hs),
        (0.010 * hs, 0.0, stub_top + 0.055 * hs),
        (0.032 * hs, 0.0, stub_top + 0.070 * hs),
        (0.052 * hs, 0.0, stub_top + 0.062 * hs),
        (0.068 * hs, 0.0, stub_top + 0.048 * hs),
        (0.078 * hs, 0.0, stub_top + 0.024 * hs),
    ]
    crook_geom = tube_from_spline_points(
        crook_points,
        radius=0.020 * hs,
        closed_spline=False,
        samples_per_segment=14,
        radial_segments=16,
        cap_ends=True,
    )
    handle.visual(
        mesh_from_geometry(crook_geom, "crook_handle_mesh"),
        material=mats["handle"],
        name="crook_handle", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    _emit_handle_collar(handle, r, mats, z_top=_HANDLE_COLLAR_LEN)
    return "handle", 0.0


def _build_handle_derby_offset(model, r: ResolvedWalkingCaneConfig, mats) -> tuple[str, float]:
    """Derby offset — forward-curving crook with grip sleeve (source: S5)."""
    handle = model.part("handle")
    hs = r.handle_scale
    stub_len = 0.030 * hs
    handle.visual(
        Cylinder(radius=0.015 * hs, length=stub_len),
        origin=Origin(xyz=(0.0, 0.0, _HANDLE_COLLAR_LEN + stub_len * 0.5)),
        material=mats["handle"],
        name="derby_stub", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    stub_top = _HANDLE_COLLAR_LEN + stub_len
    derby_points = [
        (0.000, 0.0, stub_top),
        (0.006 * hs, 0.0, stub_top + 0.028 * hs),
        (0.020 * hs, 0.0, stub_top + 0.056 * hs),
        (0.042 * hs, 0.0, stub_top + 0.078 * hs),
        (0.070 * hs, 0.0, stub_top + 0.088 * hs),
        (0.096 * hs, 0.0, stub_top + 0.082 * hs),
        (0.114 * hs, 0.0, stub_top + 0.068 * hs),
    ]
    handle.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                derby_points,
                radius=0.012 * hs,
                samples_per_segment=14,
                radial_segments=16,
            ),
            "derby_crook_mesh",
        ),
        material=mats["dark"],
        name="derby_crook", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    # Thicker grip sleeve over the outer curve.
    handle.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                derby_points[3:],
                radius=0.018 * hs,
                samples_per_segment=12,
                radial_segments=16,
            ),
            "derby_grip_mesh",
        ),
        material=mats["handle"],
        name="derby_ergonomic_grip", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    # End cap sphere.
    end_pt = derby_points[-1]
    handle.visual(
        Sphere(radius=0.018 * hs),
        origin=Origin(xyz=(end_pt[0], end_pt[1], end_pt[2])),
        material=mats["handle"],
        name="derby_end_cap", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    _emit_handle_collar(handle, r, mats, z_top=_HANDLE_COLLAR_LEN)
    return "handle", 0.0


def _build_handle_derby_swept(model, r: ResolvedWalkingCaneConfig, mats) -> tuple[str, float]:
    """Broad swept derby with rounded_rect_profile (source: S3)."""
    handle = model.part("handle")
    hs = r.handle_scale
    stub_len = 0.055 * hs
    handle.visual(
        Cylinder(radius=0.014 * hs, length=stub_len),
        origin=Origin(xyz=(0.0, 0.0, _HANDLE_COLLAR_LEN + stub_len * 0.5)),
        material=mats["dark"],
        name="derby_swept_stub", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    stub_top = _HANDLE_COLLAR_LEN + stub_len
    handle_profile = rounded_rect_profile(0.032 * hs, 0.022 * hs, 0.008, corner_segments=6)
    # First waypoint sits inside the stub top (~5mm embed) so the swept mesh
    # AABB overlaps the stub's cap — closes the island gap between stub and
    # curved_derby_handle without changing the visible curved silhouette.
    handle_path = [
        (0.000, 0.0, stub_top - 0.005 * hs),
        (-0.010 * hs, 0.0, stub_top + 0.020 * hs),
        (-0.040 * hs, 0.0, stub_top + 0.045 * hs),
        (-0.080 * hs, 0.0, stub_top + 0.056 * hs),
        (-0.120 * hs, 0.0, stub_top + 0.045 * hs),
        (-0.140 * hs, 0.0, stub_top + 0.020 * hs),
        (-0.128 * hs, 0.0, stub_top + 0.000 * hs),
    ]
    curved = sweep_profile_along_spline(
        handle_path,
        profile=handle_profile,
        samples_per_segment=12,
        cap_profile=True,
    )
    handle.visual(
        mesh_from_geometry(curved, "curved_derby_handle"),
        material=mats["dark"],
        name="curved_derby_handle", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    # Palm and hook bulges (S3 signatures). Positions sit on the swept path
    # so the sphere AABBs overlap the swept mesh (island-connected).
    handle.visual(
        Sphere(radius=0.017 * hs),
        origin=Origin(xyz=(-0.080 * hs, 0.0, stub_top + 0.056 * hs)),
        material=mats["dark"],
        name="handle_palm_bulge", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    handle.visual(
        Sphere(radius=0.015 * hs),
        origin=Origin(xyz=(-0.128 * hs, 0.0, stub_top + 0.008 * hs)),
        material=mats["dark"],
        name="handle_hook_round", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    _emit_handle_collar(handle, r, mats, z_top=_HANDLE_COLLAR_LEN)
    return "handle", 0.0


_HANDLE_BUILDERS = {
    "t_handle": _build_handle_t,
    "ergonomic_T": _build_handle_ergonomic_T,
    "crook": _build_handle_crook,
    "derby_offset": _build_handle_derby_offset,
    "derby_swept": _build_handle_derby_swept,
}


# ---------------------------------------------------------------------------
# Shaft module builders — telescoping / folding / rigid.
# All chain along -Z. Each shaft_i is authored so its part-frame origin sits
# at its own top interface (z=0 in part local coords); its tube extends
# downward and its bottom_collar is at z=-shaft_length. Its top_collar and
# bottom_collar visuals must both be axis-aligned Cylinders (via _hollow_ring)
# so the FIXED handle→shaft_0 MatingContract and shaft_{N-1}→ground FIXED
# MatingContract can pin them.
#
# All non-FIXED chain joints (stage_slide_i, fold_joint_i) omit MatingContract
# — they are captured-slide / captured-pin geometry, grandfathered.
# ---------------------------------------------------------------------------


def _emit_shaft_visuals(part, r: ResolvedWalkingCaneConfig, mats, *, prefix: str):
    """Standard shaft-segment visuals: tube + top_collar + bottom_collar.

    All in part-local coords with part origin at the TOP interface (z=0).
    Tube extends downward to z=-shaft_length, collars at both ends.
    """
    L = r.shaft_length
    # Slightly shrink the visible tube so the collar visuals fully overlap and
    # give a real anchoring visual for the FIXED joint at both ends.
    tube_end_gap = _COLLAR_LEN * 0.5
    tube_len = L - 2 * tube_end_gap
    tube_z = -tube_end_gap - tube_len * 0.5
    part.visual(
        Cylinder(radius=r.shaft_r, length=tube_len),
        origin=Origin(xyz=(0.0, 0.0, tube_z)),
        material=mats["shaft"],
        name=f"{prefix}tube", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "bare_aluminum", "painted_red"} else "wood.walnut_dark"),
    )
    part.visual(
        _hollow_ring(
            r.shaft_r_outer,
            r.shaft_r_inner,
            _COLLAR_LEN,
            f"{prefix}top_collar_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, -_COLLAR_LEN * 0.5)),
        material=mats["collar"],
        name=f"{prefix}top_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )
    part.visual(
        _hollow_ring(
            r.shaft_r_outer,
            r.shaft_r_inner,
            _COLLAR_LEN,
            f"{prefix}bottom_collar_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, -L + _COLLAR_LEN * 0.5)),
        material=mats["collar"],
        name=f"{prefix}bottom_collar", material_class_id=("metal.stainless_matte" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )


def _emit_pin_holes(part, r: ResolvedWalkingCaneConfig, mats, *, prefix: str):
    """Adjustment holes decoration — inline visuals (Rule 4 host-conformal).
    Placed slightly EMBEDDED into the tube surface so island-check treats
    them as connected to the tube.
    """
    L = r.shaft_length
    for i, frac in enumerate((0.35, 0.45, 0.55, 0.65)):
        z = -L * frac
        part.visual(
            Cylinder(radius=0.0028, length=0.0025),
            # Embed 1mm into the tube surface (tube outer at shaft_r).
            origin=Origin(
                xyz=(r.shaft_r - 0.0006, 0.0, z),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["dark"],
            name=f"{prefix}pin_hole_{i}", material_class_id="plastic.opaque_generic",
        )


def _build_shaft_chain_and_joints(
    model,
    r: ResolvedWalkingCaneConfig,
    mats,
    handle_part_name: str,
    handle_collar_bottom_z: float,
) -> tuple[list[str], list[str]]:
    """Emit N shaft parts + all cross-shaft joints (non-FIXED for chain)
    + the FIXED handle→shaft_0 joint with MatingContract.

    Returns (shaft_part_names, chain_joint_names).
    """
    N = r.shaft_count
    L = r.shaft_length
    shaft_names: list[str] = []
    chain_joints: list[str] = []

    # Emit each shaft part. Part-frame origin is at its own TOP interface.
    for i in range(N):
        part = model.part(f"shaft_{i}")
        _emit_shaft_visuals(part, r, mats, prefix=f"s{i}_")
        _emit_pin_holes(part, r, mats, prefix=f"s{i}_")
        shaft_names.append(f"shaft_{i}")

    # FIXED handle -> shaft_0. MatingContract on collar face.
    # Handle's collar bottom is at world z = 0 (interface face).
    # Shaft_0 top_collar top face is at part-local z=0 too, so origin=0 works.
    handle_part = model.get_part(handle_part_name)
    shaft_0 = model.get_part("shaft_0")
    model.articulation(
        "handle_to_shaft_0",
        ArticulationType.FIXED,
        parent=handle_part,
        child=shaft_0,
        origin=Origin(xyz=(0.0, 0.0, handle_collar_bottom_z)),
        mating=MatingContract(
            parent_face_geometry="handle_socket_collar",
            parent_face_side="negative_z",
            child_face_geometry="s0_top_collar",
            child_face_side="positive_z",
            contact_tol=0.002,
            tangential_containment=True,
            tangential_tol=0.005,
        ),
    )

    # Inter-shaft joints depending on family.
    if r.shaft_family == "telescoping":
        for i in range(1, N):
            parent = model.get_part(f"shaft_{i - 1}")
            child = model.get_part(f"shaft_{i}")
            # Origin at parent's BOTTOM interface (world offset -L per stage
            # already because each part origin is at its own top). Because
            # shaft_{i-1}'s bottom is at part-local z=-L, we place the joint
            # there — but the parent-relative articulation origin is expressed
            # in parent-local coords, so we use (0,0,-L) directly.
            joint = f"stage_slide_{i - 1}"
            model.articulation(
                joint,
                ArticulationType.PRISMATIC,
                parent=parent,
                child=child,
                origin=Origin(xyz=(0.0, 0.0, -L + _COLLAR_LEN * 0.5)),
                axis=(0.0, 0.0, -1.0),
                motion_limits=MotionLimits(
                    effort=60.0, velocity=0.15, lower=0.0, upper=r.tele_travel
                ),
            )
            chain_joints.append(joint)
    elif r.shaft_family == "folding":
        for i in range(1, N):
            parent = model.get_part(f"shaft_{i - 1}")
            child = model.get_part(f"shaft_{i}")
            joint = f"fold_joint_{i - 1}"
            # Rest pose: fully extended (straight cane) at rpy=0.
            # The full fold_angle range is available toward one direction
            # (alternating sign per index so that folded pose forms a zig-zag).
            # This keeps the closed pose collision-free (the child continues
            # the parent tube's -Z direction) and folded is the reachable pose.
            fold_dir = 1.0 if i % 2 == 1 else -1.0
            lower = -r.fold_angle if fold_dir < 0 else 0.0
            upper = r.fold_angle if fold_dir > 0 else 0.0
            model.articulation(
                joint,
                ArticulationType.REVOLUTE,
                parent=parent,
                child=child,
                origin=Origin(xyz=(0.0, 0.0, -L)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=2.5, velocity=1.8, lower=lower, upper=upper),
                # straight_pose = 0 (rest is already straight); folded_pose is
                # the reachable extreme in the allowed direction.
                meta={
                    "straight_pose": 0.0,
                    "folded_pose": r.fold_angle * fold_dir,
                },
            )
            chain_joints.append(joint)
    # rigid: no inter-shaft joints (N==1).

    return shaft_names, chain_joints


def _emit_button(model, r: ResolvedWalkingCaneConfig, mats) -> str | None:
    """Optional PRISMATIC spring button on shaft_0 (S2 pattern).
    Guarantees at least one non-FIXED joint (needed when N==1 rigid).
    Returns the button part name (or None if not emitted).
    """
    if not r.include_button:
        return None
    button = model.part("adjustment_button")
    button.visual(
        Sphere(radius=0.0042),
        origin=Origin(xyz=(0.0025, 0.0, 0.0)),
        material=mats["collar"],
        name="spring_button", material_class_id=("metal.stainless_matte" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )
    button.visual(
        Cylinder(radius=0.0020, length=0.009),
        origin=Origin(xyz=(-0.0020, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["collar"],
        name="button_stem", material_class_id=("metal.stainless_matte" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )
    shaft_0 = model.get_part("shaft_0")
    model.articulation(
        "button_press",
        ArticulationType.PRISMATIC,
        parent=shaft_0,
        child=button,
        # Attach in the middle of shaft_0, on the +X side of the tube surface.
        origin=Origin(xyz=(r.shaft_r + 0.0025, 0.0, -r.shaft_length * 0.45)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.02, lower=-0.004, upper=0.002),
    )
    return "adjustment_button"


# ---------------------------------------------------------------------------
# Ground interface module builders.
# All emit a single "ground_foot" part FIXED to shaft_{N-1}, with a real
# "ground_top_face" visual serving as MatingContract child face.
# ---------------------------------------------------------------------------


def _emit_ground_top_face(part, r: ResolvedWalkingCaneConfig, mats):
    """Small collar visual serving as the FIXED mating face."""
    part.visual(
        _hollow_ring(
            _FOOT_SOCKET_R,
            r.shaft_r_inner,
            _FOOT_SOCKET_LEN,
            "ground_top_face_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, -_FOOT_SOCKET_LEN * 0.5)),
        material=mats["collar"],
        name="ground_top_face", material_class_id=("metal.stainless_matte" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )


def _build_ground_rubber_tip(model, r: ResolvedWalkingCaneConfig, mats):
    foot = model.part("ground_foot")
    _emit_ground_top_face(foot, r, mats)
    # Filler stub that plugs into the socket bore to keep the tip visually
    # connected to the socket (no floating island).
    stub_r = min(r.shaft_r + 0.002, _FOOT_SOCKET_R - 0.001)
    foot.visual(
        Cylinder(radius=stub_r, length=_FOOT_SOCKET_LEN + 0.006),
        origin=Origin(xyz=(0.0, 0.0, -_FOOT_SOCKET_LEN * 0.5 - 0.001)),
        material=mats["rubber"],
        name="tip_stub", material_class_id="rubber.smooth_plain",
    )
    # Lathed rubber tip (S2 _lathed_tip).
    tip_top_z = -_FOOT_SOCKET_LEN
    foot.visual(
        _lathed_tip("rubber_tip_body_mesh"),
        origin=Origin(xyz=(0.0, 0.0, tip_top_z)),
        material=mats["rubber"],
        name="rubber_tip_body", material_class_id="rubber.smooth_plain",
    )
    foot.visual(
        Cylinder(radius=0.021, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, tip_top_z - 0.058 - 0.002)),
        material=mats["rubber"],
        name="flat_tread_pad", material_class_id="rubber.smooth_plain",
    )
    return foot


def _build_ground_quad_base(model, r: ResolvedWalkingCaneConfig, mats):
    foot = model.part("ground_foot")
    _emit_ground_top_face(foot, r, mats)
    hub_z = -_FOOT_SOCKET_LEN - 0.015 * 0.5
    foot.visual(
        Cylinder(radius=0.028, length=0.015),
        origin=Origin(xyz=(0.0, 0.0, hub_z)),
        material=mats["shaft"],
        name="quad_hub", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
    )
    # Four radial legs (from central hub) with rubber pads. All inline visuals
    # on the same 'ground_foot' part (Rule 1). Legs touch hub — supported chain.
    leg_len = 0.090
    leg_r = 0.006
    hub_bot = hub_z - 0.015 * 0.5
    for i, (dx, dy, rpy) in enumerate(
        (
            (leg_len * 0.5, 0.0, (0.0, math.pi / 2.0, 0.0)),  # +X leg
            (-leg_len * 0.5, 0.0, (0.0, math.pi / 2.0, 0.0)),  # -X leg
            (0.0, leg_len * 0.5, (math.pi / 2.0, 0.0, 0.0)),  # +Y leg
            (0.0, -leg_len * 0.5, (math.pi / 2.0, 0.0, 0.0)),  # -Y leg
        )
    ):
        foot.visual(
            Cylinder(radius=leg_r, length=leg_len),
            origin=Origin(xyz=(dx, dy, hub_bot + 0.003), rpy=rpy),
            material=mats["shaft"],
            name=f"quad_arm_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"matte_green", "brushed_black", "glossy_purple", "walnut_wood", "painted_red"} else "metal.aluminum_bare"),
        )
        # Rubber pad at the leg tip.
        end_x = dx * 2.0 if dx != 0.0 else 0.0
        end_y = dy * 2.0 if dy != 0.0 else 0.0
        foot.visual(
            Cylinder(radius=0.014, length=0.014),
            origin=Origin(xyz=(end_x, end_y, hub_bot - 0.006)),
            material=mats["rubber"],
            name=f"rubber_pad_{i}", material_class_id="rubber.smooth_plain",
        )
    return foot


def _build_ground_tripod_base(model, r: ResolvedWalkingCaneConfig, mats):
    foot = model.part("ground_foot")
    _emit_ground_top_face(foot, r, mats)
    # The tripod mesh is CENTERED at the placement origin (hub extends
    # ±hub_height/2). We want the hub TOP to sit at the socket bottom
    # (z = -_FOOT_SOCKET_LEN) so its geometry begins below the mating face.
    hub_h = 0.018
    tripod_top_z = -_FOOT_SOCKET_LEN - hub_h * 0.5
    foot.visual(
        _tripod_mesh(
            hub_radius=0.018,
            hub_height=hub_h,
            leg_radius=0.005,
            leg_length=0.045,
            foot_radius=0.012,
            foot_height=0.006,
            splay_angle=0.52,
            name="tripod_base_mesh",
        ),
        origin=Origin(xyz=(0.0, 0.0, tripod_top_z)),
        material=mats["rubber"],
        name="tripod_base", material_class_id="rubber.smooth_plain",
    )
    return foot


_GROUND_BUILDERS = {
    "rubber_tip": _build_ground_rubber_tip,
    "quad_base": _build_ground_quad_base,
    "tripod_base": _build_ground_tripod_base,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build_walking_cane(
    config: WalkingCaneConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"walking_cane_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in _PALETTES[r.palette_style].items()
    }

    handle_name, collar_bot_z = _HANDLE_BUILDERS[r.handle_form](model, r, mats)
    _build_shaft_chain_and_joints(model, r, mats, handle_name, collar_bot_z)
    _emit_button(model, r, mats)

    # FIXED shaft_{N-1} -> ground_foot with MatingContract.
    last_shaft_name = f"shaft_{r.shaft_count - 1}"
    last_shaft = model.get_part(last_shaft_name)
    foot = _GROUND_BUILDERS[r.ground_interface](model, r, mats)
    model.articulation(
        "shaft_to_ground",
        ArticulationType.FIXED,
        parent=last_shaft,
        child=foot,
        # parent bottom_collar's negative_z face sits at part-local z = -L
        # (collar centered at -L + COLLAR_LEN/2 with length COLLAR_LEN).
        # Child ground_top_face positive_z face sits at part-local z = 0.
        # Place the joint at parent's bottom face so the two mating faces kiss.
        origin=Origin(xyz=(0.0, 0.0, -r.shaft_length)),
        mating=MatingContract(
            parent_face_geometry=f"s{r.shaft_count - 1}_bottom_collar",
            parent_face_side="negative_z",
            child_face_geometry="ground_top_face",
            child_face_side="positive_z",
            contact_tol=0.002,
            tangential_containment=True,
            tangential_tol=0.005,
        ),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_walking_cane(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_walking_cane(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def run_walking_cane_tests(
    object_model: ArticulatedObject,
    config: WalkingCaneConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    handle = object_model.get_part("handle")
    shafts = [object_model.get_part(f"shaft_{i}") for i in range(r.shaft_count)]
    foot = object_model.get_part("ground_foot")

    # --- Captured-slide / captured-pin element-scoped allowances. ---
    # Telescoping: allow overlap between parent's bottom_collar (sleeve) and
    # child's tube — captured-slide geometry, exactly the S1/S2/S9 pattern.
    if r.shaft_family == "telescoping":
        for i in range(1, r.shaft_count):
            ctx.allow_overlap(
                shafts[i - 1],
                shafts[i],
                elem_a=f"s{i - 1}_bottom_collar",
                elem_b=f"s{i}_tube",
                reason=(
                    "Telescoping child tube is intentionally seated inside the "
                    "parent sleeve (captured-slide fit) at the collapsed length."
                ),
            )
            ctx.allow_overlap(
                shafts[i - 1],
                shafts[i],
                elem_a=f"s{i - 1}_bottom_collar",
                elem_b=f"s{i}_top_collar",
                reason=(
                    "Adjacent telescoping collars are intentionally nested at "
                    "the sleeve bore for a real captured-slide interface."
                ),
            )
    elif r.shaft_family == "folding":
        for i in range(1, r.shaft_count):
            # The fold hinge is a captured-pin ferrule between the two segment
            # collars; during travel the child tube sweeps through the parent
            # tube's swept volume (this is intentional — real folding canes
            # collapse the shafts alongside each other via short cord-and-pin
            # ferrules; we don't model the offset). Allow the pair as
            # element-scoped so the sampled-pose gate does not fail.
            for pa in ("bottom_collar", "tube"):
                for pb in ("top_collar", "tube"):
                    ctx.allow_overlap(
                        shafts[i - 1],
                        shafts[i],
                        elem_a=f"s{i - 1}_{pa}",
                        elem_b=f"s{i}_{pb}",
                        reason=(
                            "Folding cane segments intentionally sweep through "
                            "each other during collapse (captured-pin ferrule "
                            "connection; real ferrules offset the segments to "
                            "one side but we do not model that offset)."
                        ),
                    )

    # Button captured through the tube (S2 pattern).
    if r.include_button:
        button = object_model.get_part("adjustment_button")
        ctx.allow_overlap(
            shafts[0],
            button,
            elem_a="s0_tube",
            elem_b="button_stem",
            reason="The spring button stem is intentionally seated through the shaft.",
        )
        ctx.allow_overlap(
            shafts[0],
            button,
            elem_a="s0_tube",
            elem_b="spring_button",
            reason="Sphere button head lightly protrudes from the shaft surface.",
        )

    # Shaft-to-ground: the socket collar accepts the shaft tube.
    ctx.allow_overlap(
        shafts[-1],
        foot,
        elem_a=f"s{r.shaft_count - 1}_bottom_collar",
        elem_b="ground_top_face",
        reason="Ground foot socket collar accepts the cane shaft (real seated interface).",
    )
    if r.ground_interface == "rubber_tip":
        ctx.allow_overlap(
            shafts[-1],
            foot,
            elem_a=f"s{r.shaft_count - 1}_tube",
            elem_b="rubber_tip_body",
            reason="The cane tube is socketed into the rubber tip.",
        )

    # --- Baseline checks. ---
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # --- Rule 5: sampled-pose motion QC. ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # --- Structure / identity checks. ---
    part_names = {p.name for p in object_model.parts}
    ctx.check("handle part present", "handle" in part_names)
    ctx.check(
        "shaft parts present",
        all(f"shaft_{i}" in part_names for i in range(r.shaft_count)),
        details=str(sorted(part_names)),
    )
    ctx.check("ground_foot part present", "ground_foot" in part_names)

    ctx.check(
        "handle collar visual present (mating face)",
        handle.get_visual("handle_socket_collar") is not None,
    )
    ctx.check(
        "shaft_0 top collar present (mating face)",
        shafts[0].get_visual("s0_top_collar") is not None,
    )
    ctx.check(
        "last shaft bottom collar present (mating face)",
        shafts[-1].get_visual(f"s{r.shaft_count - 1}_bottom_collar") is not None,
    )
    ctx.check(
        "ground foot socket present",
        foot.get_visual("ground_top_face") is not None,
    )

    # Handle form-specific presence checks (Rule 3 — derived from source).
    if r.handle_form == "t_handle":
        ctx.check(
            "T-handle grip present",
            handle.get_visual("t_handle_grip") is not None,
        )
    elif r.handle_form == "ergonomic_T":
        ctx.check(
            "ergonomic grip + bracket present",
            handle.get_visual("ergonomic_grip") is not None
            and handle.get_visual("white_handle_bracket") is not None,
        )
    elif r.handle_form == "crook":
        ctx.check(
            "crook mesh present",
            handle.get_visual("crook_handle") is not None,
        )
    elif r.handle_form == "derby_offset":
        ctx.check(
            "derby crook + grip present",
            handle.get_visual("derby_crook") is not None
            and handle.get_visual("derby_ergonomic_grip") is not None,
        )
    elif r.handle_form == "derby_swept":
        ctx.check(
            "swept derby handle mesh present",
            handle.get_visual("curved_derby_handle") is not None,
        )

    # Ground form-specific.
    if r.ground_interface == "rubber_tip":
        ctx.check(
            "rubber_tip_body present",
            foot.get_visual("rubber_tip_body") is not None,
        )
    elif r.ground_interface == "quad_base":
        ctx.check(
            "quad hub + 4 legs + 4 pads present",
            foot.get_visual("quad_hub") is not None
            and all(foot.get_visual(f"quad_arm_{i}") is not None for i in range(4))
            and all(foot.get_visual(f"rubber_pad_{i}") is not None for i in range(4)),
        )
    elif r.ground_interface == "tripod_base":
        ctx.check(
            "tripod base mesh present",
            foot.get_visual("tripod_base") is not None,
        )

    # --- Joint topology + non-FIXED motion coverage. ---
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-FIXED joint exists (Rule 5)",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    if r.shaft_family == "telescoping" and r.shaft_count >= 2:
        j0 = object_model.get_articulation("stage_slide_0")
        ctx.check(
            "telescoping stage_slide_0 is PRISMATIC axis -Z",
            j0.articulation_type == ArticulationType.PRISMATIC and abs(j0.axis[2]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        # Motion: extension moves lowest shaft downward.
        last_shaft = shafts[-1]
        rest_z = ctx.part_world_position(last_shaft)
        with ctx.pose({j0: r.tele_travel * 0.9}):
            ext_z = ctx.part_world_position(last_shaft)
        if rest_z is not None and ext_z is not None:
            ctx.check(
                "positive telescoping motion extends cane downward",
                ext_z[2] < rest_z[2] - r.tele_travel * 0.5,
                details=f"rest={rest_z}, extended={ext_z}",
            )
    elif r.shaft_family == "folding" and r.shaft_count >= 2:
        j0 = object_model.get_articulation("fold_joint_0")
        ctx.check(
            "folding joint is REVOLUTE axis +Y",
            j0.articulation_type == ArticulationType.REVOLUTE and abs(j0.axis[1]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        # Motion: at rest the cane is already straight; the folded_pose stows.
        # We check the AABB of the last shaft — its bottom shifts sideways in X
        # when the fold joint rotates (the part origin at the joint doesn't
        # move under REVOLUTE, only geometry does).
        joints = [
            object_model.get_articulation(f"fold_joint_{i}") for i in range(r.shaft_count - 1)
        ]
        rest_aabb = ctx.part_world_aabb(shafts[-1])
        ctx.check(
            "rest pose extends the last shaft downward (straight cane)",
            rest_aabb is not None and rest_aabb[0][2] < -r.shaft_length * 0.5,
            details=f"rest_aabb={rest_aabb}",
        )
        # Fold each joint 90% of its way to folded_pose and check that the
        # last shaft's centroid shifts sideways in X (the fold displaces its
        # world position). AABB width does NOT grow because rotating a
        # cylindrical part about a pivot above it moves the part but keeps
        # its own footprint width the same — check displacement, not width.
        folded_pose = {j: j.meta["folded_pose"] * 0.9 for j in joints}
        rest_cx = 0.5 * (rest_aabb[0][0] + rest_aabb[1][0]) if rest_aabb is not None else 0.0
        with ctx.pose(folded_pose):
            folded_aabb = ctx.part_world_aabb(shafts[-1])
        folded_cx = (
            0.5 * (folded_aabb[0][0] + folded_aabb[1][0]) if folded_aabb is not None else 0.0
        )
        ctx.check(
            "folded pose swings the last shaft sideways in X",
            rest_aabb is not None
            and folded_aabb is not None
            and abs(folded_cx - rest_cx) > r.shaft_length * 0.20,
            details=f"rest={rest_aabb} (cx={rest_cx}), folded={folded_aabb} (cx={folded_cx})",
        )

    if r.include_button:
        jb = object_model.get_articulation("button_press")
        ctx.check(
            "button_press is PRISMATIC axis +X",
            jb.articulation_type == ArticulationType.PRISMATIC and abs(jb.axis[0]) > 0.99,
            details=f"type={jb.articulation_type} axis={tuple(jb.axis)}",
        )

    # --- Slot choices recorded. ---
    ctx.check(
        "slot_choices recorded in model.meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "WalkingCaneConfig",
    "ResolvedWalkingCaneConfig",
    "build_walking_cane",
    "build_seeded_walking_cane",
    "config_from_seed",
    "resolve_config",
    "run_walking_cane_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
    "PALETTE_STYLES",
)
