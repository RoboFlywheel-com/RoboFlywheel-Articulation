# SPDX-License-Identifier: Apache-2.0

"""Rack-and-pinion slider procedural template (modular).

A linear-motion transmission: a rotating toothed pinion (spur gear) meshes a
toothed straight rack on a guide frame, converting rotation to straight-line
travel. Every candidate keeps the subcategory identity — one REVOLUTE pinion
spin + one PRISMATIC linear slide, coupled by pitch radius — and derives its
part tree / joint topology / primitive types from the declared 5-star sources
(see specs_modular_v1/rack_and_pinion_slider.md).

Modular structure (3 slots + 1 multiplicity axis):

  Slot A  drive_skeleton     (① topology/support/pinion-count)
            moving_rack_straddle    — origin B/A: fixed pinion on two-side
                                       torus-collar bearings, rack translates
            moving_rack_cantilever  — fork skeleton_cantilever_pinion: pinion
                                       overhung on a single-side motor block
            traveling_pinion        — fork skeleton_traveling_pinion: rack
                                       FIXED to frame, a pinion_carriage travels
            moving_rack_dual        — fork n2_dual_pinion: two pinions on one
                                       rack, each its own REVOLUTE
  Slot B  rack_form          (③ primary form family — rack cross-section)
            flat_bar_rack           — origin B/A: rectangular bar + top teeth
            round_shaft_rack        — fork form_round_rack: cylindrical shaft
  Slot C  envelope_carriage  (③ macro construction — sliding member / shroud)
            bare_open               — origin B/A: exposed bridge/shoe carriage
            linear_stage_table      — fork carriage_linear_table: broad T-slot
                                       stage table
            enclosed_tube_housing   — fork form_enclosed_tube: gearbox shroud
                                       over the pinion, rack tunnels through
  Multiplicity  rack_tooth_count N  (rack length / stroke), source {16,30,44}

Both non-FIXED joints are mechanical captures (pinion axle in a bearing bore;
rack sliding above a guide rail with an intentional running gap), so — like
monitor_mount / dj_equipment's hinge — they carry NO MatingContract and are
grandfathered through fail_if_joint_mating_has_gap. The captured bearing fit
and the gear-tooth mesh interleave are declared as element-scoped
`ctx.allow_overlap(...)` in run_tests. No FIXED articulations exist: all
non-articulating detail (bearing hardware, motor housing, shroud walls, T-slot
ribs, end caps, bolts) is `parent.visual(...)` on the owning moving part
(Rule 1). All geometry is Box / Cylinder / TorusGeometry / trapezoid Mesh —
no cadquery boolean — keeping the per-seed compile budget <=12s (spec 7.5).
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
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

DriveSkeleton = Literal[
    "moving_rack_straddle",
    "moving_rack_cantilever",
    "traveling_pinion",
    "moving_rack_dual",
]
RackForm = Literal["flat_bar_rack", "round_shaft_rack"]
EnvelopeCarriage = Literal["bare_open", "linear_stage_table", "enclosed_tube_housing"]
RPPaletteTheme = Literal[
    "steel_oxide",
    "warm_machined",
    "office_white",
    "dark_carbon",
    "anodized_blue",
]

_DRIVE_SKELETONS: tuple[DriveSkeleton, ...] = (
    "moving_rack_straddle",
    "moving_rack_cantilever",
    "traveling_pinion",
    "moving_rack_dual",
)
_RACK_FORMS: tuple[RackForm, ...] = ("flat_bar_rack", "round_shaft_rack")

# Locked mesh constant (spec 7): tooth_pitch is fixed so the delicate
# rack<->pinion mesh cannot drift; diversity comes from pinion_teeth / N /
# face_scale / the discrete slots.
TOOTH_PITCH = 0.019


RP_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    # material keys: frame_metal, dark_metal, rack_metal, gear_metal,
    # accent, housing, bearing_black
    "steel_oxide": {
        "frame_metal": (0.72, 0.75, 0.76, 1.0),
        "dark_metal": (0.10, 0.11, 0.12, 1.0),
        "rack_metal": (0.62, 0.64, 0.63, 1.0),
        "gear_metal": (0.74, 0.68, 0.58, 1.0),
        "accent": (0.20, 0.36, 0.55, 1.0),
        "housing": (0.20, 0.22, 0.26, 1.0),
        "bearing_black": (0.03, 0.03, 0.035, 1.0),
    },
    "warm_machined": {
        "frame_metal": (0.66, 0.64, 0.60, 1.0),
        "dark_metal": (0.14, 0.13, 0.12, 1.0),
        "rack_metal": (0.70, 0.66, 0.58, 1.0),
        "gear_metal": (0.82, 0.72, 0.52, 1.0),
        "accent": (0.72, 0.42, 0.20, 1.0),
        "housing": (0.30, 0.26, 0.20, 1.0),
        "bearing_black": (0.05, 0.04, 0.035, 1.0),
    },
    "office_white": {
        "frame_metal": (0.90, 0.90, 0.89, 1.0),
        "dark_metal": (0.34, 0.35, 0.36, 1.0),
        "rack_metal": (0.78, 0.79, 0.80, 1.0),
        "gear_metal": (0.66, 0.66, 0.64, 1.0),
        "accent": (0.24, 0.46, 0.66, 1.0),
        "housing": (0.82, 0.83, 0.84, 1.0),
        "bearing_black": (0.20, 0.20, 0.21, 1.0),
    },
    "dark_carbon": {
        "frame_metal": (0.16, 0.17, 0.19, 1.0),
        "dark_metal": (0.045, 0.048, 0.052, 1.0),
        "rack_metal": (0.40, 0.42, 0.44, 1.0),
        "gear_metal": (0.55, 0.53, 0.50, 1.0),
        "accent": (0.85, 0.55, 0.15, 1.0),
        "housing": (0.10, 0.10, 0.11, 1.0),
        "bearing_black": (0.02, 0.02, 0.02, 1.0),
    },
    "anodized_blue": {
        "frame_metal": (0.30, 0.42, 0.56, 1.0),
        "dark_metal": (0.10, 0.13, 0.18, 1.0),
        "rack_metal": (0.60, 0.64, 0.68, 1.0),
        "gear_metal": (0.74, 0.70, 0.62, 1.0),
        "accent": (0.90, 0.78, 0.30, 1.0),
        "housing": (0.16, 0.24, 0.34, 1.0),
        "bearing_black": (0.03, 0.03, 0.04, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class RackAndPinionSliderConfig:
    drive_skeleton: DriveSkeleton = "moving_rack_straddle"
    rack_form: RackForm = "flat_bar_rack"
    envelope_carriage: EnvelopeCarriage = "bare_open"
    palette_theme: RPPaletteTheme = "steel_oxide"

    rack_tooth_count: int = 30
    pinion_teeth: int = 22
    face_scale: float = 1.0


@dataclass(frozen=True)
class ResolvedRackAndPinionSliderConfig:
    drive_skeleton: DriveSkeleton
    rack_form: RackForm
    envelope_carriage: EnvelopeCarriage
    palette_theme: RPPaletteTheme
    rack_tooth_count: int
    pinion_teeth: int
    face_scale: float
    palette: dict[str, tuple[float, float, float, float]]


def _legal_envelopes(skeleton: str) -> tuple[EnvelopeCarriage, ...]:
    """Compatibility gate (spec 9): which envelope_carriage candidates are
    structurally legal for a given drive_skeleton."""
    if skeleton == "traveling_pinion":
        # No rack_carriage to dress; the pinion carriage is inherently exposed.
        return ("bare_open",)
    if skeleton == "moving_rack_dual":
        return ("bare_open", "linear_stage_table")
    if skeleton == "moving_rack_cantilever":
        return ("bare_open", "linear_stage_table")
    # moving_rack_straddle — the enclosed shroud is faithful only here (single
    # pinion, two-side support), matching origin A.
    return ("bare_open", "linear_stage_table", "enclosed_tube_housing")


def _sample_rack_tooth_count(rng: random.Random) -> int:
    """Weighted N sampler: small (short-stroke) frequent, long-stroke rare."""
    u = rng.random()
    if u < 0.5:
        return rng.randint(12, 20)
    if u < 0.85:
        return rng.randint(21, 40)
    return rng.randint(41, 56)


def _rack_tooth_band(n: int) -> str:
    if n <= 20:
        return "short"
    if n <= 40:
        return "mid"
    return "long"


def config_from_seed(seed: int) -> RackAndPinionSliderConfig:
    """Deterministic procedural sampling for EVERY seed, including seed 0
    (Contract 4 — no seed-0 special-casing, no curated table)."""
    rng = random.Random(seed)

    skeleton: DriveSkeleton = rng.choice(_DRIVE_SKELETONS)
    rack_form: RackForm = rng.choice(_RACK_FORMS)
    envelope: EnvelopeCarriage = rng.choice(_legal_envelopes(skeleton))
    palette_theme: RPPaletteTheme = rng.choice(tuple(RP_PALETTE_PRESETS.keys()))

    rack_tooth_count = _sample_rack_tooth_count(rng)
    pinion_teeth = rng.randint(18, 26)
    face_scale = round(rng.uniform(0.90, 1.15), 4)

    return RackAndPinionSliderConfig(
        drive_skeleton=skeleton,
        rack_form=rack_form,
        envelope_carriage=envelope,
        palette_theme=palette_theme,
        rack_tooth_count=rack_tooth_count,
        pinion_teeth=pinion_teeth,
        face_scale=face_scale,
    )


def resolve_config(
    config: RackAndPinionSliderConfig,
) -> ResolvedRackAndPinionSliderConfig:
    skeleton = str(config.drive_skeleton)
    if skeleton not in _DRIVE_SKELETONS:
        raise ValueError(f"Unsupported drive_skeleton: {config.drive_skeleton}")
    rack_form = str(config.rack_form)
    if rack_form not in _RACK_FORMS:
        raise ValueError(f"Unsupported rack_form: {config.rack_form}")
    if str(config.palette_theme) not in RP_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    # conditional gate: fall back to bare_open when an illegal envelope was
    # requested for this skeleton (defensive; sampler already respects it).
    envelope = str(config.envelope_carriage)
    legal = _legal_envelopes(skeleton)
    if envelope not in legal:
        envelope = "bare_open"

    n = max(12, min(int(config.rack_tooth_count), 56))
    pinion_teeth = max(18, min(int(config.pinion_teeth), 26))
    face_scale = max(0.85, min(float(config.face_scale), 1.20))

    palette = dict(RP_PALETTE_PRESETS[str(config.palette_theme)])

    return ResolvedRackAndPinionSliderConfig(
        drive_skeleton=skeleton,  # type: ignore[arg-type]
        rack_form=rack_form,  # type: ignore[arg-type]
        envelope_carriage=envelope,  # type: ignore[arg-type]
        palette_theme=config.palette_theme,
        rack_tooth_count=n,
        pinion_teeth=pinion_teeth,
        face_scale=face_scale,
        palette=palette,
    )


def slot_choices_for_config(
    r: ResolvedRackAndPinionSliderConfig,
) -> tuple[tuple[str, str], ...]:
    return (
        ("drive_skeleton", str(r.drive_skeleton)),
        ("rack_form", str(r.rack_form)),
        ("envelope_carriage", str(r.envelope_carriage)),
        ("rack_tooth_band", _rack_tooth_band(r.rack_tooth_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Shared geometric quantities (Contract 3c — single-sourced in _GearGeom).
# All z heights / radii / lengths derive from here so the mesh clearance
# (pinion_center_z = rack_tooth_tip_z + gear_root_radius + 0.001) can never
# drift. Numbers are the proven origin-B / fork-family values.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class _GearGeom:
    tooth_pitch: float
    pinion_teeth: int
    pitch_radius: float
    gear_root_radius: float
    gear_tooth_depth: float
    gear_width: float
    rack_width: float
    rack_bar_height: float
    rack_bar_top_z: float
    rack_tooth_height: float
    rack_tooth_tip_z: float
    pinion_center_z: float
    rack_tooth_count: int
    rack_half_len: float
    rack_bar_len: float
    base_length: float
    base_half: float
    travel: float
    pinion_travel_rad: float
    bearing_y_offset: float
    axle_len: float


def _gear_geom(r: ResolvedRackAndPinionSliderConfig) -> _GearGeom:
    tp = TOOTH_PITCH
    teeth = r.pinion_teeth
    pitch_radius = tp * teeth / (2.0 * math.pi)
    gear_root_radius = pitch_radius - 0.006
    gear_tooth_depth = 0.014
    gear_width = 0.034 * r.face_scale
    rack_width = 0.060 * r.face_scale
    rack_bar_height = 0.026
    rack_bar_top_z = 0.085
    rack_tooth_height = 0.017
    rack_tooth_tip_z = rack_bar_top_z + rack_tooth_height
    pinion_center_z = rack_tooth_tip_z + gear_root_radius + 0.001

    n = r.rack_tooth_count
    # teeth at (i+0.5)*tp for i in [-(n//2), n-(n//2)) -> n teeth centered on 0.
    lo = -(n // 2)
    hi = n - (n // 2)
    rack_half_len = (max(abs(lo), abs(hi - 1)) + 0.5) * tp + 0.028
    rack_bar_len = 2.0 * rack_half_len

    # travel scales with rack length; capped by pitch radius (inequality).
    travel = min(pitch_radius, max(0.030, n * tp * 0.12), 0.11)
    base_half = rack_half_len + travel + 0.060
    base_length = 2.0 * base_half
    pinion_travel_rad = max(0.4, min(travel / pitch_radius, 1.6))

    # Bearing supports sit at a wide Y offset so the broad linear_stage_table
    # (half-width 0.061) clears them (fork carriage_linear_table moved them to
    # 0.068). The axle then reaches past the collars to be captured on both
    # sides (fork used axle length 0.150).
    bearing_y_offset = 0.068
    axle_len = 2.0 * (bearing_y_offset + 0.008)

    return _GearGeom(
        tooth_pitch=tp,
        pinion_teeth=teeth,
        pitch_radius=pitch_radius,
        gear_root_radius=gear_root_radius,
        gear_tooth_depth=gear_tooth_depth,
        gear_width=gear_width,
        rack_width=rack_width,
        rack_bar_height=rack_bar_height,
        rack_bar_top_z=rack_bar_top_z,
        rack_tooth_height=rack_tooth_height,
        rack_tooth_tip_z=rack_tooth_tip_z,
        pinion_center_z=pinion_center_z,
        rack_tooth_count=n,
        rack_half_len=rack_half_len,
        rack_bar_len=rack_bar_len,
        base_length=base_length,
        base_half=base_half,
        travel=travel,
        pinion_travel_rad=pinion_travel_rad,
        bearing_y_offset=bearing_y_offset,
        axle_len=axle_len,
    )


# --------------------------------------------------------------------------- #
# Tooth mesh helper (adapted verbatim from origin B model.py:L21-L67).
# X = tooth thickness (tangent), Y = face width, Z = tooth height.
# --------------------------------------------------------------------------- #


def _trapezoid_prism(
    inner_width: float,
    outer_width: float,
    height: float,
    depth: float,
    *,
    centered_z: bool = False,
) -> MeshGeometry:
    z0, z1 = (-height / 2.0, height / 2.0) if centered_z else (0.0, height)
    y0, y1 = -depth / 2.0, depth / 2.0
    xi, xo = inner_width / 2.0, outer_width / 2.0

    geom = MeshGeometry()
    verts = [
        (-xi, y0, z0),
        (xi, y0, z0),
        (xo, y0, z1),
        (-xo, y0, z1),
        (-xi, y1, z0),
        (xi, y1, z0),
        (xo, y1, z1),
        (-xo, y1, z1),
    ]
    for x, y, z in verts:
        geom.add_vertex(x, y, z)
    for tri in (
        (0, 1, 2),
        (0, 2, 3),
        (4, 7, 6),
        (4, 6, 5),
        (0, 4, 5),
        (0, 5, 1),
        (3, 2, 6),
        (3, 6, 7),
        (0, 3, 7),
        (0, 7, 4),
        (1, 5, 6),
        (1, 6, 2),
    ):
        geom.add_face(*tri)
    return geom


def _rack_tooth_mesh(g: _GearGeom) -> object:
    return mesh_from_geometry(
        _trapezoid_prism(0.011, 0.006, g.rack_tooth_height, g.rack_width),
        "rack_tooth_profile",
    )


def _gear_tooth_mesh(g: _GearGeom) -> object:
    return mesh_from_geometry(
        _trapezoid_prism(
            0.009, 0.006, g.gear_tooth_depth, g.gear_width, centered_z=True
        ),
        "pinion_tooth_profile",
    )


# --------------------------------------------------------------------------- #
# Pinion builder (adapted from n2_dual_pinion `_build_pinion`, L70-L114).
# --------------------------------------------------------------------------- #


def _build_pinion(part, g: _GearGeom, gear_tooth_mesh: object, *, with_axle: bool = True) -> None:
    part.visual(
        Cylinder(radius=g.gear_root_radius, length=g.gear_width),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="gear_metal",
        name="root_wheel", material_class_id="metal.brass_polished",
    )
    place_radius = g.gear_root_radius + g.gear_tooth_depth / 2.0 - 0.0008
    for idx in range(g.pinion_teeth):
        theta = math.pi + idx * (2.0 * math.pi / g.pinion_teeth)
        part.visual(
            gear_tooth_mesh,
            origin=Origin(
                xyz=(place_radius * math.sin(theta), 0.0, place_radius * math.cos(theta)),
                rpy=(0.0, theta, 0.0),
            ),
            material="gear_metal",
            name=f"pinion_tooth_{idx:02d}", material_class_id="metal.brass_polished",
        )
    part.visual(
        Cylinder(radius=0.026, length=0.052),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame_metal",
        name="raised_hub", material_class_id="metal.aluminum_bare",
    )
    if not with_axle:
        # Traveling-pinion: the carriage's pinion_shaft IS the journal; the
        # pinion carries no redundant axle of its own.
        return
    axle_len = g.axle_len
    part.visual(
        # Radius slightly over the bearing-collar inner radius (0.0132) so the
        # captured journal fit is a guaranteed contact, not a tangent.
        Cylinder(radius=0.0135, length=axle_len),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="axle", material_class_id="metal.blackened_gunmetal",
    )
    for sgn, nm in ((-1.0, "axle_cap_0"), (1.0, "axle_cap_1")):
        part.visual(
            Cylinder(radius=0.018, length=0.006),
            origin=Origin(xyz=(0.0, sgn * (axle_len / 2.0 - 0.004), 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="accent",
            name=nm, material_class_id="metal.paint_coated",
        )


def _bearing_collar_mesh() -> object:
    return mesh_from_geometry(
        TorusGeometry(radius=0.018, tube=0.0048, radial_segments=20, tubular_segments=36),
        "bearing_collar_ring",
    )


# --------------------------------------------------------------------------- #
# Rack teeth + rack member (Slot B).
# --------------------------------------------------------------------------- #


def _emit_rack_member(part, g: _GearGeom, r: ResolvedRackAndPinionSliderConfig,
                      rack_tooth_mesh: object) -> None:
    """Emit the toothed rack (bar/shaft + teeth loop + end caps) onto `part`.

    `part` is the sliding rack_carriage (moving-rack) or the fixed frame
    (traveling_pinion). Rack cross-section switches on rack_form (Slot B).
    """
    if r.rack_form == "round_shaft_rack":
        # form_round_rack fork L180-L198: cylindrical shaft, teeth on the top.
        shaft_radius = g.rack_bar_height / 2.0
        part.visual(
            Cylinder(radius=shaft_radius, length=g.rack_bar_len),
            origin=Origin(
                xyz=(0.0, 0.0, g.rack_bar_top_z - shaft_radius),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material="rack_metal",
            name="rack_bar", material_class_id="metal.steel_bare",
        )
        for idx, x in enumerate((-g.rack_half_len + 0.008, g.rack_half_len - 0.008)):
            part.visual(
                Cylinder(radius=shaft_radius + 0.005, length=0.016),
                origin=Origin(
                    xyz=(x, 0.0, g.rack_bar_top_z - shaft_radius),
                    rpy=(0.0, math.pi / 2.0, 0.0),
                ),
                material="rack_metal",
                name=f"rack_end_cap_{idx}", material_class_id="metal.steel_bare",
            )
    else:
        # flat_bar_rack (origin B L178-L190): rectangular back bar.
        part.visual(
            Box((g.rack_bar_len, g.rack_width, g.rack_bar_height)),
            origin=Origin(xyz=(0.0, 0.0, g.rack_bar_top_z - g.rack_bar_height / 2.0)),
            material="rack_metal",
            name="rack_bar", material_class_id="metal.steel_bare",
        )
        for idx, x in enumerate((-g.rack_half_len + 0.008, g.rack_half_len - 0.008)):
            part.visual(
                Box((0.016, g.rack_width + 0.010, g.rack_bar_height + 0.010)),
                origin=Origin(
                    xyz=(x, 0.0, g.rack_bar_top_z - g.rack_bar_height / 2.0 + 0.001)
                ),
                material="rack_metal",
                name=f"rack_end_cap_{idx}", material_class_id="metal.steel_bare",
            )

    # Rack teeth loop (multiplicity axis). Half-pitch phasing leaves a valley
    # directly under each pinion mesh point (origin B L191-L199).
    n = g.rack_tooth_count
    lo = -(n // 2)
    for idx, i in enumerate(range(lo, n + lo)):
        x = (i + 0.5) * g.tooth_pitch
        part.visual(
            rack_tooth_mesh,
            origin=Origin(xyz=(x, 0.0, g.rack_bar_top_z - 0.0005)),
            material="rack_metal",
            name=f"rack_tooth_{idx:02d}", material_class_id="metal.steel_bare",
        )


# --------------------------------------------------------------------------- #
# Carriage understructure + shroud (Slot C).
# --------------------------------------------------------------------------- #


def _emit_carriage_understructure(rack_part, frame_part, g: _GearGeom,
                                  r: ResolvedRackAndPinionSliderConfig) -> None:
    """Emit the sliding member's under-body (Slot C) on rack_part, plus (for
    enclosed_tube_housing) the gearbox shroud on frame_part."""
    envelope = r.envelope_carriage
    shoe_len = min(0.250, g.rack_bar_len - 0.04)

    if envelope == "linear_stage_table":
        # carriage_linear_table fork L165-L213: broad T-slot stage table below
        # the rack bar (flush with rack_bar bottom), plus guide shoes.
        table_thickness = 0.012
        table_top_z = g.rack_bar_top_z - g.rack_bar_height  # flush with bar bottom
        table_center_z = table_top_z - table_thickness / 2.0
        table_len = min(0.340, g.rack_bar_len - 0.02)
        table_half_y = 0.061
        rack_part.visual(
            Box((table_len, 2.0 * table_half_y, table_thickness)),
            origin=Origin(xyz=(0.0, 0.0, table_center_z)),
            material="frame_metal",
            name="stage_table", material_class_id="metal.aluminum_bare",
        )
        for idx, y in enumerate((-0.050, -0.038, 0.038, 0.050)):
            rack_part.visual(
                Box((table_len - 0.04, 0.006, 0.003)),
                origin=Origin(xyz=(0.0, y, table_top_z + 0.0015)),
                material="dark_metal",
                name=f"table_slot_rib_{idx}", material_class_id="metal.blackened_gunmetal",
            )
        for idx, y in enumerate((-0.034, 0.034)):
            rack_part.visual(
                Box((shoe_len, 0.018, 0.024)),
                origin=Origin(xyz=(0.0, y, 0.035)),
                material="frame_metal",
                name=f"carriage_shoe_{idx}", material_class_id="metal.aluminum_bare",
            )
        return

    # bare_open (origin B L164-L177) — also used as the carriage body for the
    # enclosed shroud (the distinguishing shroud is emitted on the frame).
    rack_part.visual(
        Box((shoe_len, 0.085, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.053)),
        material="frame_metal",
        name="carriage_bridge", material_class_id="metal.aluminum_bare",
    )
    for idx, y in enumerate((-0.034, 0.034)):
        rack_part.visual(
            Box((shoe_len, 0.018, 0.024)),
            origin=Origin(xyz=(0.0, y, 0.035)),
            material="frame_metal",
            name=f"carriage_shoe_{idx}", material_class_id="metal.aluminum_bare",
        )

    if envelope == "enclosed_tube_housing":
        _emit_gearbox_shroud(frame_part, g)


def _emit_gearbox_shroud(frame_part, g: _GearGeom) -> None:
    """Gearbox shroud over the pinion (form_enclosed_tube fork, adapted to a
    tunnel-open shroud so the rack passes through both ends collision-free —
    2 side walls + top plate + stiffener ribs/bolts). Frame visual (fixed)."""
    shroud_len = 0.20
    wall = 0.006
    inner_half_y = 0.078
    top_z = g.pinion_center_z + g.gear_root_radius + g.gear_tooth_depth + 0.020
    base_top = 0.018
    side_h = top_z - base_top
    side_center_z = base_top + side_h / 2.0
    for idx, sgn in enumerate((-1.0, 1.0)):
        frame_part.visual(
            Box((shroud_len, wall, side_h)),
            origin=Origin(xyz=(0.0, sgn * (inner_half_y + wall / 2.0), side_center_z)),
            material="housing",
            name=f"housing_side_{idx}", material_class_id="metal.paint_coated",
        )
    frame_part.visual(
        Box((shroud_len, 2.0 * inner_half_y + 2.0 * wall, wall)),
        origin=Origin(xyz=(0.0, 0.0, top_z + wall / 2.0)),
        material="housing",
        name="housing_top", material_class_id="metal.paint_coated",
    )
    # Short front/back lintels only in the upper region (clear of the rack).
    for idx, sgn in enumerate((-1.0, 1.0)):
        frame_part.visual(
            Box((wall, 2.0 * inner_half_y, side_h * 0.32)),
            origin=Origin(
                xyz=(sgn * (shroud_len / 2.0 - wall / 2.0), 0.0, top_z - side_h * 0.16)
            ),
            material="housing",
            name=f"housing_lintel_{idx}", material_class_id="metal.paint_coated",
        )
    for idx, x in enumerate((-0.06, 0.0, 0.06)):
        frame_part.visual(
            Cylinder(radius=0.004, length=0.004),
            origin=Origin(xyz=(x, 0.0, top_z + wall + 0.001)),
            material="dark_metal",
            name=f"housing_bolt_{idx}", material_class_id="metal.blackened_gunmetal",
        )


# --------------------------------------------------------------------------- #
# Frame builder + pinion support (Slot A).
# --------------------------------------------------------------------------- #


def _emit_base(frame, g: _GearGeom) -> None:
    frame.visual(
        Box((g.base_length, 0.24, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material="frame_metal",
        name="base_plate", material_class_id="metal.paint_coated",
    )
    for idx, x in enumerate((-(g.base_half - 0.014), g.base_half - 0.014)):
        frame.visual(
            Box((0.028, 0.12, 0.040)),
            origin=Origin(xyz=(x, 0.0, 0.038)),
            material="frame_metal",
            name=f"rail_stop_{idx}", material_class_id="metal.paint_coated",
        )
    bx = g.base_half * 0.84
    for idx, (x, y) in enumerate(((-bx, -0.09), (-bx, 0.09), (bx, -0.09), (bx, 0.09))):
        frame.visual(
            Cylinder(radius=0.010, length=0.006),
            origin=Origin(xyz=(x, y, 0.021)),
            material="dark_metal",
            name=f"mount_bolt_{idx}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_straddle_supports(frame, g: _GearGeom, bearing_mesh: object,
                            x_offsets: tuple[float, ...]) -> None:
    """Two-side torus-collar bearing support per pinion (origin B L143-L162 /
    n2 fork L198-L222)."""
    b = 0
    for px in x_offsets:
        for y in (-g.bearing_y_offset, g.bearing_y_offset):
            web_height = g.pinion_center_z - 0.038
            frame.visual(
                Box((0.050, 0.014, web_height)),
                origin=Origin(xyz=(px, y, 0.018 + web_height / 2.0)),
                material="frame_metal",
                name=f"bearing_web_{b}", material_class_id="metal.paint_coated",
            )
            frame.visual(
                Box((0.060, 0.014, 0.014)),
                origin=Origin(xyz=(px, y, g.pinion_center_z - 0.026)),
                material="frame_metal",
                name=f"bearing_saddle_{b}", material_class_id="metal.paint_coated",
            )
            frame.visual(
                bearing_mesh,
                origin=Origin(xyz=(px, y, g.pinion_center_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="dark_metal",
                name=f"bearing_collar_{b}", material_class_id="metal.blackened_gunmetal",
            )
            b += 1


def _emit_cantilever_support(frame, g: _GearGeom, bearing_mesh: object) -> None:
    """Single-side overhung support (skeleton_cantilever_pinion L113-L154):
    one beefy bearing cheek on -Y + motor housing stub + inner bearing collar."""
    cheek_y = -g.bearing_y_offset
    web_height = g.pinion_center_z - 0.038
    frame.visual(
        Box((0.060, 0.020, web_height)),
        origin=Origin(xyz=(0.0, cheek_y, 0.018 + web_height / 2.0)),
        material="dark_metal",
        name="bearing_web_0", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Box((0.070, 0.022, 0.014)),
        origin=Origin(xyz=(0.0, cheek_y, g.pinion_center_z - 0.026)),
        material="dark_metal",
        name="bearing_saddle_0", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        bearing_mesh,
        origin=Origin(xyz=(0.0, cheek_y, g.pinion_center_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="bearing_collar_0", material_class_id="metal.blackened_gunmetal",
    )
    # Gearmotor / bearing housing stub on the outer -Y face.
    motor_len = 0.030
    frame.visual(
        Cylinder(radius=0.024, length=motor_len),
        origin=Origin(
            xyz=(0.0, cheek_y - 0.010 - motor_len / 2.0, g.pinion_center_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material="bearing_black",
        name="motor_housing", material_class_id="metal.blackened_gunmetal",
    )


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #


def build_rack_and_pinion_slider(
    config: RackAndPinionSliderConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    g = _gear_geom(r)
    model = ArticulatedObject(name="rack_and_pinion_slider", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    rack_tooth_mesh = _rack_tooth_mesh(g)
    gear_tooth_mesh = _gear_tooth_mesh(g)
    bearing_mesh = _bearing_collar_mesh()

    frame = model.part("frame")
    _emit_base(frame, g)

    if r.drive_skeleton == "traveling_pinion":
        _build_traveling_pinion(model, frame, g, r, rack_tooth_mesh, gear_tooth_mesh)
    else:
        _build_moving_rack(model, frame, g, r, rack_tooth_mesh, gear_tooth_mesh, bearing_mesh)

    model.meta["category"] = "Robotics / Rack-and-pinion slider"
    model.meta["template_slug"] = "rack_and_pinion_slider"
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]
    model.meta["pinion_pitch_radius_m"] = g.pitch_radius
    return model


def _build_moving_rack(model, frame, g, r, rack_tooth_mesh, gear_tooth_mesh,
                       bearing_mesh) -> None:
    dual = r.drive_skeleton == "moving_rack_dual"
    if dual:
        # Even multiple of pitch keeps a valley under both pinions.
        spacing = round(0.28 / g.tooth_pitch) * g.tooth_pitch
        px_offsets = (-spacing / 2.0, spacing / 2.0)
    else:
        px_offsets = (0.0,)

    # Two guide rails sit directly under the carriage shoes (y=+-0.034) so the
    # sliding rack is carried on real rail contact — connectivity to the frame
    # does NOT depend on the micron-precise gear mesh (isolation tol is 1um).
    for idx, sgn in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((g.base_length - 0.12, 0.014, 0.014)),
            origin=Origin(xyz=(0.0, sgn * 0.034, 0.017)),
            material="dark_metal",
            name=f"guide_rail_{idx}", material_class_id="metal.blackened_gunmetal",
        )

    if r.drive_skeleton == "moving_rack_cantilever":
        _emit_cantilever_support(frame, g, bearing_mesh)
    else:
        _emit_straddle_supports(frame, g, bearing_mesh, px_offsets)

    # Sliding rack carriage.
    rack = model.part("rack_carriage")
    _emit_rack_member(rack, g, r, rack_tooth_mesh)
    _emit_carriage_understructure(rack, frame, g, r)

    model.articulation(
        "rack_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=rack,
        # Child visuals are authored in world coords; PRISMATIC origin is gauge
        # freedom, so keep it at 0 (origin B) — a nonzero z would lift the rack
        # off the mesh.
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=70.0, velocity=0.25, lower=-g.travel, upper=g.travel),
        meta={"pitch_radius_m": g.pitch_radius, "tooth_pitch_m": g.tooth_pitch},
    )

    # Pinion(s).
    for k, px in enumerate(px_offsets):
        pinion_name = f"pinion_{k}" if dual else "pinion"
        pinion = model.part(pinion_name)
        _build_pinion(pinion, g, gear_tooth_mesh)
        spin_name = f"pinion_spin_{k}" if dual else "pinion_spin"
        model.articulation(
            spin_name,
            ArticulationType.REVOLUTE,
            parent=frame,
            child=pinion,
            origin=Origin(xyz=(px, 0.0, g.pinion_center_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=12.0, velocity=4.0,
                lower=-g.pinion_travel_rad, upper=g.pinion_travel_rad,
            ),
        )


def _build_traveling_pinion(model, frame, g, r, rack_tooth_mesh, gear_tooth_mesh) -> None:
    # Carriage cheeks straddle outside the fixed rack; the guide rails / sliders
    # sit just outside the cheeks. Single-sourced rail_y so rail and slider
    # cannot drift apart.
    cheek_y = g.rack_width / 2.0 + 0.014
    rail_y = cheek_y + 0.006
    # Two guide rails carry the traveling carriage's sliders.
    for idx, sgn in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((g.base_length - 0.12, 0.014, 0.014)),
            origin=Origin(xyz=(0.0, sgn * rail_y, 0.025)),
            material="dark_metal",
            name=f"guide_rail_{idx}", material_class_id="metal.blackened_gunmetal",
        )
    # Rack bed riser + FIXED rack as frame visuals (fixed-rack topology).
    bed_h = (g.rack_bar_top_z - g.rack_bar_height) - 0.018
    if bed_h > 0.002:
        frame.visual(
            Box((g.rack_bar_len * 0.98, g.rack_width + 0.006, bed_h)),
            origin=Origin(xyz=(0.0, 0.0, 0.018 + bed_h / 2.0)),
            material="frame_metal",
            name="rack_bed", material_class_id="metal.paint_coated",
        )
    _emit_rack_member(frame, g, r, rack_tooth_mesh)

    # Traveling pinion carriage (skeleton_traveling_pinion L143-L214).
    carriage = model.part("pinion_carriage")
    rail_top = 0.032
    pinion_top = g.pinion_center_z + g.pitch_radius + g.gear_tooth_depth
    cheek_bottom = rail_top
    cheek_top = pinion_top + 0.014
    cheek_h = cheek_top - cheek_bottom
    cheek_cz = 0.5 * (cheek_bottom + cheek_top)
    for idx, sgn in enumerate((-1.0, 1.0)):
        carriage.visual(
            Box((0.050, 0.010, cheek_h)),
            origin=Origin(xyz=(0.0, sgn * cheek_y, cheek_cz)),
            material="dark_metal",
            name=f"bearing_cheek_{idx}", material_class_id="metal.blackened_gunmetal",
        )
    slider_h = 0.014
    guide_rail_top = 0.018 + 0.014  # base top + rail height
    for idx, sgn in enumerate((-1.0, 1.0)):
        carriage.visual(
            Box((0.050, 0.016, slider_h)),
            origin=Origin(xyz=(0.0, sgn * rail_y, guide_rail_top - 0.003 + slider_h / 2.0)),
            material="bearing_black",
            name=f"guide_slider_{idx}", material_class_id="metal.blackened_gunmetal",
        )
    crossbar_bottom = pinion_top + 0.006
    carriage.visual(
        Box((0.050, 2.0 * cheek_y + 0.010, 0.008)),
        origin=Origin(xyz=(0.0, 0.0, crossbar_bottom + 0.004)),
        material="dark_metal",
        name="carriage_crossbar", material_class_id="metal.blackened_gunmetal",
    )
    carriage.visual(
        Cylinder(radius=0.007, length=2.0 * cheek_y + 0.020),
        origin=Origin(xyz=(0.0, 0.0, g.pinion_center_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="dark_metal",
        name="pinion_shaft", material_class_id="metal.blackened_gunmetal",
    )
    for idx, x in enumerate((-0.018, 0.018)):
        carriage.visual(
            Cylinder(radius=0.004, length=0.003),
            origin=Origin(xyz=(x, 0.0, cheek_top + 0.0015)),
            material="dark_metal",
            name=f"carriage_bolt_{idx}", material_class_id="metal.blackened_gunmetal",
        )

    model.articulation(
        "rack_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=carriage,
        # Carriage visuals authored in world coords; keep PRISMATIC origin at 0.
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.30, lower=-g.travel, upper=g.travel),
        meta={"pitch_radius_m": g.pitch_radius, "tooth_pitch_m": g.tooth_pitch},
    )

    pinion = model.part("pinion")
    _build_pinion(pinion, g, gear_tooth_mesh, with_axle=False)
    model.articulation(
        "pinion_spin",
        ArticulationType.REVOLUTE,
        parent=carriage,
        child=pinion,
        origin=Origin(xyz=(0.0, 0.0, g.pinion_center_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=8.0,
            lower=-g.pinion_travel_rad, upper=g.pinion_travel_rad,
        ),
    )


def build_seeded_rack_and_pinion_slider(seed: int) -> ArticulatedObject:
    return build_rack_and_pinion_slider(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #


def _pinion_names(model, r: ResolvedRackAndPinionSliderConfig) -> list[str]:
    if r.drive_skeleton == "moving_rack_dual":
        return ["pinion_0", "pinion_1"]
    return ["pinion"]


def _declare_intentional_overlaps(ctx, model, r, g) -> None:
    """Element/part-scoped allowances: (a) the pinion axle captured in its
    bearing bore(s) as a journal fit; (b) the rack<->pinion gear-tooth mesh,
    whose tooth envelopes intentionally interleave at the pitch line."""
    frame = model.get_part("frame")
    is_traveling = r.drive_skeleton == "traveling_pinion"
    rack_part = model.get_part("frame") if is_traveling else model.get_part("rack_carriage")
    shaft_owner = model.get_part("pinion_carriage") if is_traveling else frame

    for pname in _pinion_names(model, r):
        pinion = model.get_part(pname)
        # Gear mesh: teeth interleave — intentional captured contact.
        ctx.allow_overlap(
            pinion,
            rack_part,
            reason=(
                f"{pname} gear teeth intentionally mesh/interleave with the rack "
                "teeth at the pitch line; tooth envelopes overlap as the "
                "rack-and-pinion drive requires."
            ),
        )
        if is_traveling:
            ctx.allow_overlap(
                shaft_owner, pinion, elem_a="pinion_shaft", elem_b="root_wheel",
                reason="Carriage shaft is a captured journal fit inside the pinion bore.",
            )
            ctx.allow_overlap(
                shaft_owner, pinion, elem_a="pinion_shaft", elem_b="raised_hub",
                reason="Carriage shaft seats inside the rotating hub bore.",
            )
        else:
            # Every straddle/cantilever bearing collar captures the axle.
            for v in frame.visuals:
                nm = getattr(v, "name", "")
                if nm.startswith("bearing_collar_"):
                    ctx.allow_overlap(
                        frame, pinion, elem_a=nm, elem_b="axle",
                        reason="Rotating axle captured in the bearing collar as a close journal fit.",
                    )
            if r.drive_skeleton == "moving_rack_cantilever":
                for cap_elem in ("axle", "axle_cap_0"):
                    ctx.allow_overlap(
                        frame, pinion, elem_a="motor_housing", elem_b=cap_elem,
                        reason="Overhung motor/bearing housing captures the cantilever axle end as a journal seat.",
                    )


def run_rack_and_pinion_slider_tests(
    model: ArticulatedObject,
    config: RackAndPinionSliderConfig,
) -> TestReport:
    r = resolve_config(config)
    g = _gear_geom(r)
    ctx = TestContext(model)

    frame = model.get_part("frame")
    is_traveling = r.drive_skeleton == "traveling_pinion"
    slider_part = model.get_part("pinion_carriage") if is_traveling else model.get_part("rack_carriage")
    slide = model.get_articulation("rack_slide")

    _declare_intentional_overlaps(ctx, model, r, g)

    # Baseline geometry stack.
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # Category identity.
    ctx.check(
        "classification matches rack-and-pinion slider",
        model.meta.get("category") == "Robotics / Rack-and-pinion slider",
        details=str(model.meta.get("category")),
    )
    ctx.check(
        "rack_slide is PRISMATIC along x",
        slide.articulation_type == ArticulationType.PRISMATIC and tuple(slide.axis) == (1.0, 0.0, 0.0),
        details=f"type={slide.articulation_type}, axis={slide.axis!r}",
    )
    pinion_names = _pinion_names(model, r)
    for pname in pinion_names:
        spin_name = "pinion_spin" if pname == "pinion" else f"pinion_spin_{pname.split('_')[-1]}"
        spin = model.get_articulation(spin_name)
        ctx.check(
            f"{spin_name} is REVOLUTE about -y",
            spin.articulation_type == ArticulationType.REVOLUTE and tuple(spin.axis) == (0.0, -1.0, 0.0),
            details=f"type={spin.articulation_type}, axis={spin.axis!r}",
        )
    if r.drive_skeleton == "moving_rack_dual":
        ctx.check("dual-pinion has two pinion parts", len(pinion_names) == 2, details=str(pinion_names))
    ctx.check(
        "pitch metadata present",
        0.03 < float(slide.meta.get("pitch_radius_m", 0.0)) < 0.12,
        details=f"meta={slide.meta}",
    )

    # rack member exists on the moving carriage (moving-rack) or fixed frame.
    rack_owner = frame if is_traveling else slider_part
    rack_visuals = {getattr(v, "name", "") for v in rack_owner.visuals}
    ctx.check(
        "toothed rack present (bar + teeth)",
        "rack_bar" in rack_visuals and any(nm.startswith("rack_tooth_") for nm in rack_visuals),
        details=f"rack owner visuals sample: {sorted(rack_visuals)[:6]}",
    )
    ctx.check(
        f"rack carries {g.rack_tooth_count} teeth",
        sum(1 for nm in rack_visuals if nm.startswith("rack_tooth_")) == g.rack_tooth_count,
        details=f"expected {g.rack_tooth_count}",
    )

    # Rack sits at its authored height and the pinion meshes it (guards the
    # joint-origin-shift bug: a nonzero prismatic origin would float the rack
    # off the mesh).
    rack_bar_box = ctx.part_element_world_aabb(rack_owner, elem="rack_bar")
    if rack_bar_box is not None:
        ctx.check(
            "rack_bar sits at its authored height (not lifted off the mesh)",
            abs(rack_bar_box[1][2] - g.rack_bar_top_z) < 0.010,
            details=f"rack_bar top z={rack_bar_box[1][2]:.4f}, expected ~{g.rack_bar_top_z:.4f}",
        )
    drive_pinion = model.get_part(pinion_names[0])
    wheel_box = ctx.part_element_world_aabb(drive_pinion, elem="root_wheel")
    if wheel_box is not None and rack_bar_box is not None:
        wheel_bottom = wheel_box[0][2]
        # Pinion tooth roots dip toward the rack tooth tips: the wheel bottom
        # must straddle the rack tooth band (below the tip, above the bar top).
        ctx.check(
            "pinion meshes the rack at the pitch line (z band)",
            g.rack_bar_top_z - 0.002 <= wheel_bottom <= g.rack_tooth_tip_z + 0.006,
            details=f"pinion root_wheel bottom z={wheel_bottom:.4f}, rack tip z={g.rack_tooth_tip_z:.4f}",
        )

    # round-shaft rack must be a round cross-section (Y ~= Z).
    if r.rack_form == "round_shaft_rack":
        bbox = ctx.part_element_world_aabb(rack_owner, elem="rack_bar")
        if bbox is not None:
            lo, hi = bbox
            dy, dz = hi[1] - lo[1], hi[2] - lo[2]
            ctx.check(
                "round_shaft_rack has round cross-section (Y~=Z)",
                abs(dy - dz) < 0.006 and dy < 0.05,
                details=f"rack_bar dy={dy:.4f} dz={dz:.4f}",
            )

    # Sampled-pose collision QC (Rule 5). Intentional captures declared above.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    # Targeted motion: coupled pinion spin + rack slide advances the slider +X.
    rest = ctx.part_world_position(slider_part)
    drive_spin = model.get_articulation(
        "pinion_spin" if not r.drive_skeleton == "moving_rack_dual" else "pinion_spin_0"
    )
    with ctx.pose({slide: g.travel, drive_spin: g.pinion_travel_rad}):
        moved = ctx.part_world_position(slider_part)
    ctx.check(
        "coupled drive advances the sliding member in +X",
        rest is not None and moved is not None and moved[0] > rest[0] + min(0.015, g.travel * 0.5),
        details=f"rest={rest}, moved={moved}, travel={g.travel:.4f}",
    )

    # At full extension the (moving-rack) rack stays carried over the base.
    if not is_traveling:
        with ctx.pose({slide: g.travel}):
            ext = ctx.part_world_aabb(slider_part)
        base_box = ctx.part_element_world_aabb(frame, elem="base_plate")
        if ext is not None and base_box is not None:
            ctx.check(
                "extended rack stays within base footprint (x)",
                ext[1][0] <= base_box[1][0] + 0.02 and ext[0][0] >= base_box[0][0] - 0.02,
                details=f"rack x=[{ext[0][0]:.3f},{ext[1][0]:.3f}] base x=[{base_box[0][0]:.3f},{base_box[1][0]:.3f}]",
            )

    return ctx.report()


__all__ = [
    "__modular__",
    "DriveSkeleton",
    "RackForm",
    "EnvelopeCarriage",
    "RPPaletteTheme",
    "RackAndPinionSliderConfig",
    "ResolvedRackAndPinionSliderConfig",
    "build_rack_and_pinion_slider",
    "build_seeded_rack_and_pinion_slider",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "run_rack_and_pinion_slider_tests",
]
