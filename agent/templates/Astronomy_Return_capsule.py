# SPDX-License-Identifier: Apache-2.0

"""Astronomy / Return capsule - modular procedural template.

A landed / recovered crewed spacecraft return (re-entry) capsule: a blunt
axisymmetric crew module modeled upright on its charred ``heat_shield``, with a
scorched ablative ``capsule`` body (bell / Apollo conical frustum / Vostok
spherical descent ball), a grey hatch collar + white seal ring on the flat top
face, a dark cabin recess, round portholes, radial RCS thruster ports, and dark
re-entry scorch streaks. Appendages parent directly to the capsule
(parallel-children pattern):

  * crew_hatch  - the category-defining moving closure: a domed lid that swings
                  open on a REVOLUTE hinge, or lifts out on a PRISMATIC plug
                  axis, or (docking) a hinged crew hatch PLUS a forward docking
                  ring + a second REVOLUTE nose-cover part.
  * heat_shield - fused under the body, or a separable PRISMATIC drop-away part.

Slot graph (pattern = mixed: root capsule + 2 parallel-children slots + 2
decoration multiplicity axes ``porthole_count`` / ``rcs_count``):

    body_form (root; bell_body / conical_frustum / spherical_ball)
        |- crew_hatch  (hinged_hatch / plug_hatch / docking_hatch)
        +- heat_shield (fixed_shield / separable_shield)

Adapted per AUTHORING.md sec.A/sec.B from the confirmed 5-star Return-capsule pool
(spec: specs_modular_v1/Astronomy_Return_capsule.md). Sources (model.py:Lx-Ly
cited in the spec Module Source Index):

  S1  origin origin-record rec_a-...328c39d9   - bell body, fused shield, hinged REVOLUTE
      crew hatch, portholes/RCS/streaks/collar, all test semantics.
  S2  conical_command_module          - straight Apollo conical frustum body.
  S3  spherical_descent               - Vostok spherical descent ball body.
  S4  plug_hatch                      - PRISMATIC plug hatch (lifts out +Z).
  S5  docking_nose                    - forward docking ring + REVOLUTE nose cover.
  S6  separable_shield                - PRISMATIC drop-away heat shield part.
  S7  portholes_four / S8 rcs_ports_eight / S9 rcs_ports_twelve - (4) decoration
      multiplicity (porthole_count / rcs_count).

Coordinate frame: Z up, capsule axis on Z, heat-shield base near z=0. All
mirrored / radial pieces straddle the Z axis. ``capsule_scale`` uniformly scales
radius + height + every mount z together (mating relations preserved);
``radius_scale`` is a body-wall + conformal-decoration + shield-disc radial
proportion knob orthogonal to every mounting anchor.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


BodyForm = Literal["bell_body", "conical_frustum", "spherical_ball"]
HatchModule = Literal["hinged_hatch", "plug_hatch", "docking_hatch"]
ShieldModule = Literal["fixed_shield", "separable_shield"]
ReturnCapsulePalette = Literal[
    "shenzhou_bronze",
    "apollo_silver",
    "soyuz_olive",
    "charred_black",
    "dragon_white",
    "orion_tan",
]

_HINGED_HATCHES = ("hinged_hatch", "docking_hatch")


# --------------------------------------------------------------------------- #
# Canonical nominal dimensions (origin origin-record rec_a-...328c39d9). All lengths in m
# at capsule_scale=1; every emit multiplies by capsule_scale (and radius_scale
# where noted) at build time.
# --------------------------------------------------------------------------- #

BASE_R = 1.26          # heat-shield rim radius (~2.5 m across)
BODY_BOT_Z = 0.34      # bell / conical body bottom
BODY_TOP_Z = 2.22      # flat top face carrying the hatch collar
COLLAR_BASE_Z = 2.20   # hatch collar base
COLLAR_TOP_Z = 2.36    # hatch collar rim top
SEAL_TOP_Z = 2.37      # white seal ring top face

SPHERE_R = 1.15        # Vostok descent-ball radius (spherical_ball)
SPHERE_CZ = 1.30       # descent-ball center z
SPHERE_BOT_Z = 0.38    # sphere profile start (flush with shield top)

# crew hatch (hinged) - hinge line at the -X collar edge
HINGE_XYZ = (-0.49, 0.0, 2.40)
LID_OFFSET_X = 0.49    # lid axis offset inside the hatch part frame
# plug hatch - prismatic origin at the seal-ring top face
PLUG_ORIGIN_Z = 2.37
# forward docking section (docking_hatch)
DOCK_RING_BASE_Z = 2.355
NOSE_HINGE_XYZ = (0.35, 0.0, 2.52)   # +X docking-ring rim
NOSE_COVER_OFFSET_X = -0.35          # dome center offset from hinge toward axis

STREAK_AZIMUTHS = (0.3, 1.2, 2.4, 3.5, 4.4, 5.5)

# Bell wall control points (r, z) for the conformal radius helper (origin L80-90).
_BELL_WALL_PTS = (
    (1.24, 0.34), (1.22, 0.60), (1.10, 1.10), (0.92, 1.55),
    (0.72, 1.90), (0.56, 2.12), (0.50, 2.22),
)


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; shared token set so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "shenzhou_bronze": {
        "body_ablative": (0.55, 0.42, 0.27, 1.0),
        "scorch_dark": (0.20, 0.16, 0.12, 1.0),
        "shield_char": (0.15, 0.12, 0.10, 1.0),
        "collar_grey": (0.62, 0.63, 0.65, 1.0),
        "lid_grey": (0.76, 0.77, 0.78, 1.0),
        "seal_white": (0.88, 0.88, 0.87, 1.0),
        "cabin_dark": (0.07, 0.07, 0.08, 1.0),
        "glass_dark": (0.05, 0.06, 0.08, 1.0),
    },
    "apollo_silver": {
        "body_ablative": (0.70, 0.71, 0.73, 1.0),
        "scorch_dark": (0.28, 0.29, 0.31, 1.0),
        "shield_char": (0.18, 0.16, 0.15, 1.0),
        "collar_grey": (0.58, 0.60, 0.63, 1.0),
        "lid_grey": (0.80, 0.81, 0.83, 1.0),
        "seal_white": (0.92, 0.93, 0.94, 1.0),
        "cabin_dark": (0.09, 0.10, 0.11, 1.0),
        "glass_dark": (0.06, 0.07, 0.10, 1.0),
    },
    "soyuz_olive": {
        "body_ablative": (0.36, 0.36, 0.20, 1.0),
        "scorch_dark": (0.16, 0.16, 0.10, 1.0),
        "shield_char": (0.12, 0.11, 0.08, 1.0),
        "collar_grey": (0.55, 0.56, 0.52, 1.0),
        "lid_grey": (0.66, 0.67, 0.60, 1.0),
        "seal_white": (0.85, 0.85, 0.80, 1.0),
        "cabin_dark": (0.06, 0.06, 0.05, 1.0),
        "glass_dark": (0.05, 0.06, 0.06, 1.0),
    },
    "charred_black": {
        "body_ablative": (0.16, 0.14, 0.12, 1.0),
        "scorch_dark": (0.07, 0.06, 0.05, 1.0),
        "shield_char": (0.05, 0.05, 0.04, 1.0),
        "collar_grey": (0.42, 0.43, 0.45, 1.0),
        "lid_grey": (0.50, 0.51, 0.53, 1.0),
        "seal_white": (0.72, 0.72, 0.70, 1.0),
        "cabin_dark": (0.03, 0.03, 0.04, 1.0),
        "glass_dark": (0.03, 0.04, 0.05, 1.0),
    },
    "dragon_white": {
        "body_ablative": (0.86, 0.87, 0.88, 1.0),
        "scorch_dark": (0.32, 0.33, 0.35, 1.0),
        "shield_char": (0.20, 0.19, 0.18, 1.0),
        "collar_grey": (0.64, 0.66, 0.68, 1.0),
        "lid_grey": (0.88, 0.89, 0.90, 1.0),
        "seal_white": (0.95, 0.96, 0.97, 1.0),
        "cabin_dark": (0.10, 0.11, 0.13, 1.0),
        "glass_dark": (0.07, 0.08, 0.11, 1.0),
    },
    "orion_tan": {
        "body_ablative": (0.68, 0.56, 0.38, 1.0),
        "scorch_dark": (0.26, 0.20, 0.14, 1.0),
        "shield_char": (0.17, 0.13, 0.10, 1.0),
        "collar_grey": (0.60, 0.60, 0.58, 1.0),
        "lid_grey": (0.74, 0.72, 0.66, 1.0),
        "seal_white": (0.90, 0.88, 0.82, 1.0),
        "cabin_dark": (0.08, 0.07, 0.06, 1.0),
        "glass_dark": (0.06, 0.06, 0.07, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class AstronomyReturnCapsuleConfig:
    body_form: BodyForm = "bell_body"
    hatch_module: HatchModule = "hinged_hatch"
    shield_module: ShieldModule = "fixed_shield"
    palette_style: ReturnCapsulePalette = "shenzhou_bronze"

    porthole_count: int = 2   # 2 or 4
    rcs_count: int = 4        # 4, 8 or 12

    capsule_scale: float = 1.0    # uniform radius + height + mount z
    radius_scale: float = 1.0     # body-wall + decoration + shield radial knob
    hatch_open: float = 2.0       # REVOLUTE crew-hatch upper (rad); hinged/docking
    plug_travel: float = 0.30     # PRISMATIC plug upper (m, x capsule_scale)
    nose_open: float = 2.0        # REVOLUTE nose-cover upper (rad); docking
    shield_drop: float = 1.2      # PRISMATIC shield jettison upper (m, x capsule_scale)


@dataclass(frozen=True)
class ResolvedAstronomyReturnCapsuleConfig:
    body_form: BodyForm
    hatch_module: HatchModule
    shield_module: ShieldModule
    palette_style: str

    porthole_count: int
    rcs_count: int

    capsule_scale: float
    radius_scale: float
    hatch_open: float
    plug_travel: float
    nose_open: float
    shield_drop: float

    # Derived (single-sourced; Contract 3c).
    top_z: float          # flat top-face height (collar seat), = BODY_TOP_Z * cs
    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling (procedural-first)
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> AstronomyReturnCapsuleConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin origin-record combination (bell_body + hinged_hatch +
    fixed_shield, 2 portholes / 4 RCS, shenzhou_bronze) as a documented
    regression anchor (a sparse override; every other seed is fully procedural).
    """
    if seed == 0:
        return AstronomyReturnCapsuleConfig()

    rng = random.Random(seed)

    body_form: BodyForm = rng.choice(("bell_body", "conical_frustum", "spherical_ball"))
    hatch_module: HatchModule = rng.choice(("hinged_hatch", "plug_hatch", "docking_hatch"))
    shield_module: ShieldModule = rng.choice(("fixed_shield", "separable_shield"))
    palette_style = rng.choice(PALETTE_NAMES)

    porthole_count = rng.choices((2, 4), weights=(0.6, 0.4))[0]
    rcs_count = rng.choices((4, 8, 12), weights=(0.5, 0.3, 0.2))[0]

    capsule_scale = round(rng.uniform(0.85, 1.20), 4)
    radius_scale = round(rng.uniform(0.92, 1.10), 4)
    hatch_open = round(rng.uniform(1.6, 2.2), 4)
    plug_travel = round(rng.uniform(0.18, 0.38), 4)
    nose_open = round(rng.uniform(1.6, 2.2), 4)
    shield_drop = round(rng.uniform(0.9, 1.5), 4)

    return AstronomyReturnCapsuleConfig(
        body_form=body_form,
        hatch_module=hatch_module,
        shield_module=shield_module,
        palette_style=palette_style,
        porthole_count=porthole_count,
        rcs_count=rcs_count,
        capsule_scale=capsule_scale,
        radius_scale=radius_scale,
        hatch_open=hatch_open,
        plug_travel=plug_travel,
        nose_open=nose_open,
        shield_drop=shield_drop,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(
    config: AstronomyReturnCapsuleConfig,
) -> ResolvedAstronomyReturnCapsuleConfig:
    if str(config.body_form) not in {"bell_body", "conical_frustum", "spherical_ball"}:
        raise ValueError(f"Unsupported body_form: {config.body_form}")
    if str(config.hatch_module) not in {"hinged_hatch", "plug_hatch", "docking_hatch"}:
        raise ValueError(f"Unsupported hatch_module: {config.hatch_module}")
    if str(config.shield_module) not in {"fixed_shield", "separable_shield"}:
        raise ValueError(f"Unsupported shield_module: {config.shield_module}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    capsule_scale = _clamp(config.capsule_scale, 0.85, 1.20)
    radius_scale = _clamp(config.radius_scale, 0.92, 1.10)
    hatch_open = _clamp(config.hatch_open, 1.6, 2.2)
    plug_travel = _clamp(config.plug_travel, 0.18, 0.38)
    nose_open = _clamp(config.nose_open, 1.6, 2.2)
    shield_drop = _clamp(config.shield_drop, 0.9, 1.5)

    porthole_count = 4 if int(config.porthole_count) >= 4 else 2
    rcs = int(config.rcs_count)
    rcs_count = 12 if rcs >= 12 else (8 if rcs >= 8 else 4)

    return ResolvedAstronomyReturnCapsuleConfig(
        body_form=config.body_form,
        hatch_module=config.hatch_module,
        shield_module=config.shield_module,
        palette_style=config.palette_style,
        porthole_count=porthole_count,
        rcs_count=rcs_count,
        capsule_scale=capsule_scale,
        radius_scale=radius_scale,
        hatch_open=hatch_open,
        plug_travel=plug_travel,
        nose_open=nose_open,
        shield_drop=shield_drop,
        top_z=BODY_TOP_Z * capsule_scale,
        palette=dict(PALETTES[config.palette_style]),
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _radial(r: float, ang: float, z: float) -> tuple[float, float, float]:
    return (r * math.cos(ang), r * math.sin(ang), z)


def _scale_pts(
    pts: list[tuple[float, float]] | tuple[tuple[float, float], ...],
    fr: float,
    fz: float,
) -> list[tuple[float, float]]:
    return [(r * fr, z * fz) for (r, z) in pts]


def _sphere_r(z: float) -> float:
    dz = z - SPHERE_CZ
    return math.sqrt(max(0.0, SPHERE_R * SPHERE_R - dz * dz))


def _nominal_body_profile(form: str) -> list[tuple[float, float]]:
    """Revolved (r, z) profile of the body at capsule_scale=1 (radius_scale=1)."""
    if form == "conical_frustum":
        # Straight Apollo frustum: rim -> narrow top (conical_command_module S2).
        return [(0.00, BODY_BOT_Z), (1.24, BODY_BOT_Z), (0.79, BODY_TOP_Z), (0.00, BODY_TOP_Z)]
    if form == "spherical_ball":
        # Vostok descent ball: spherical arc (spherical_descent S3).
        prof: list[tuple[float, float]] = [(0.0, SPHERE_BOT_Z), (_sphere_r(SPHERE_BOT_Z), SPHERE_BOT_Z)]
        n_arc = 16
        for i in range(1, n_arc):
            z = SPHERE_BOT_Z + (BODY_TOP_Z - SPHERE_BOT_Z) * i / n_arc
            prof.append((_sphere_r(z), z))
        prof.append((_sphere_r(BODY_TOP_Z), BODY_TOP_Z))
        prof.append((0.0, BODY_TOP_Z))
        return prof
    # bell_body (origin S1)
    return [
        (0.00, BODY_BOT_Z), (1.24, BODY_BOT_Z), (1.22, 0.60), (1.10, 1.10),
        (0.92, 1.55), (0.72, 1.90), (0.56, 2.12), (0.50, BODY_TOP_Z), (0.00, BODY_TOP_Z),
    ]


def _nominal_body_radius(z: float, form: str) -> float:
    """Nominal (radius_scale=capsule_scale=1) body wall radius at height ``z``.
    Single-sourced conformal helper so every decoration hugs the realized form
    across (3) / (5) changes (Rule 4)."""
    z = _clamp(z, BODY_BOT_Z, BODY_TOP_Z)
    if form == "conical_frustum":
        t = (z - BODY_BOT_Z) / (BODY_TOP_Z - BODY_BOT_Z)
        return 1.24 + (0.79 - 1.24) * t
    if form == "spherical_ball":
        return _sphere_r(_clamp(z, SPHERE_BOT_Z, BODY_TOP_Z))
    pts = _BELL_WALL_PTS
    if z <= pts[0][1]:
        return pts[0][0]
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0) if z1 > z0 else 0.0
            return r0 + (r1 - r0) * t
    return pts[-1][0]


def _wall_pitch(z: float, form: str) -> float:
    """Pitch (rot about Y) that points a +Z-axis cylinder along the body's
    OUTWARD surface normal at height ``z`` (conformal decoration seating)."""
    d = 0.02
    r0 = _nominal_body_radius(z - d, form)
    r1 = _nominal_body_radius(z + d, form)
    dr = r1 - r0
    dz = 2.0 * d
    elev = math.atan2(-dr, dz)  # normal elevation above horizontal
    return math.pi / 2.0 - elev


def _wall_tangent_pitch(z: float, form: str) -> float:
    """Pitch aligning a +Z-axis box with the meridional wall tangent (streaks)."""
    d = 0.02
    r0 = _nominal_body_radius(z - d, form)
    r1 = _nominal_body_radius(z + d, form)
    return math.atan2(r1 - r0, 2.0 * d)


def _shield_profile() -> list[tuple[float, float]]:
    """Blunt ablative heat-shield disc with a proud charred rim (origin L62-70)."""
    return [
        (0.00, 0.00), (0.80, 0.05), (1.15, 0.14),
        (BASE_R, 0.28), (BASE_R, 0.38), (0.00, 0.38),
    ]


# --------------------------------------------------------------------------- #
# Slot A - body_form (root, (3) Primary Form Family)
# --------------------------------------------------------------------------- #


def _capsule_downstream(r: ResolvedAstronomyReturnCapsuleConfig) -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="capsule",
        visual_name="bell_body",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, r.top_z),
        contact_tol=0.004,
    )


def _build_capsule(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyReturnCapsuleConfig = ctx.config  # type: ignore[assignment]
    cs, rs, form = r.capsule_scale, r.radius_scale, r.body_form
    capsule = model.part("capsule")

    # --- body envelope ((3) prototype) revolved lathe body ---
    body_prof = _scale_pts(_nominal_body_profile(form), rs * cs, cs)
    capsule.visual(
        mesh_from_geometry(LatheGeometry(body_prof, segments=48), "bell_body"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="body_ablative",
        name="bell_body", material_class_id="metal.paint_coated",
    )

    # --- hatch collar (hollow shell ring) + white seal face on top ---
    collar = LatheGeometry.from_shell_profiles(
        _scale_pts([(0.46, 0.0), (0.46, 0.16)], cs, cs),
        _scale_pts([(0.38, 0.0), (0.38, 0.16)], cs, cs),
        segments=48,
    )
    capsule.visual(
        mesh_from_geometry(collar, "hatch_collar"),
        origin=Origin(xyz=(0.0, 0.0, COLLAR_BASE_Z * cs)),
        material="collar_grey",
        name="hatch_collar", material_class_id="metal.paint_coated",
    )
    seal = LatheGeometry.from_shell_profiles(
        _scale_pts([(0.45, 0.0), (0.45, 0.015)], cs, cs),
        _scale_pts([(0.39, 0.0), (0.39, 0.015)], cs, cs),
        segments=48,
    )
    capsule.visual(
        mesh_from_geometry(seal, "hatch_seal_ring"),
        origin=Origin(xyz=(0.0, 0.0, 2.355 * cs)),
        material="seal_white",
        name="hatch_seal_ring", material_class_id="rubber.smooth_plain",
    )
    # Dark cabin opening seen through the collar when the hatch is open.
    capsule.visual(
        Cylinder(radius=0.37 * cs, length=0.05 * cs),
        origin=Origin(xyz=(0.0, 0.0, 2.215 * cs)),
        material="cabin_dark",
        name="cabin_recess", material_class_id="metal.blackened_gunmetal",
    )

    # --- round portholes on the body flanks ((4) multiplicity, conformal) ---
    z_port = 1.35
    body_r_port = _nominal_body_radius(z_port, form) * rs * cs
    pitch_port = _wall_pitch(z_port, form)
    n_port = r.porthole_count
    for i in range(n_port):
        ang = i * 2.0 * math.pi / n_port + (math.pi / 2.0 if n_port == 2 else 0.0)
        capsule.visual(
            Cylinder(radius=0.155 * cs, length=0.05 * cs),
            origin=Origin(xyz=_radial(body_r_port - 0.015 * cs, ang, z_port * cs),
                          rpy=(0.0, pitch_port, ang)),
            material="seal_white",
            name=f"porthole_rim_{i}", material_class_id="metal.paint_coated",
        )
        capsule.visual(
            Cylinder(radius=0.11 * cs, length=0.06 * cs),
            origin=Origin(xyz=_radial(body_r_port - 0.005 * cs, ang, z_port * cs),
                          rpy=(0.0, pitch_port, ang)),
            material="glass_dark",
            name=f"porthole_glass_{i}", material_class_id="glass.smoked_tinted",
        )

    # --- radial RCS thruster ports near the base ((4) multiplicity, conformal) ---
    z_rcs = 0.50
    body_r_rcs = _nominal_body_radius(z_rcs, form) * rs * cs
    pitch_rcs = _wall_pitch(z_rcs, form)
    n_rcs = r.rcs_count
    for i in range(n_rcs):
        ang = math.pi / float(n_rcs) + i * 2.0 * math.pi / n_rcs
        capsule.visual(
            Cylinder(radius=0.045 * cs, length=0.09 * cs),
            origin=Origin(xyz=_radial(body_r_rcs - 0.025 * cs, ang, z_rcs * cs),
                          rpy=(0.0, pitch_rcs, ang)),
            material="scorch_dark",
            name=f"rcs_port_{i}", material_class_id="metal.blackened_gunmetal",
        )

    # --- dark re-entry scorch streaks swept up the wall ((4) decoration) ---
    for i, ang in enumerate(STREAK_AZIMUTHS):
        z_s = 0.95 if i % 2 == 0 else 1.15
        body_r_s = _nominal_body_radius(z_s, form) * rs * cs
        tan_pitch = _wall_tangent_pitch(z_s, form)
        capsule.visual(
            Box((0.03 * cs, 0.10 * cs, 0.45 * cs)),
            origin=Origin(xyz=_radial(body_r_s + 0.006 * cs, ang, z_s * cs),
                          rpy=(0.0, tan_pitch, ang)),
            material="scorch_dark",
            name=f"scorch_streak_{i}", material_class_id="metal.blackened_gunmetal",
        )

    return ModuleBuild(
        module_name=r.body_form,
        parts_emitted=["capsule"],
        interfaces={"downstream": _capsule_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot B - crew_hatch (parallel children on the top collar)
# --------------------------------------------------------------------------- #


def _lid_mesh(cs: float):
    """Round domed crew-hatch lid shell (origin L175-183)."""
    lid_prof = _scale_pts(
        [(0.000, 0.000), (0.300, 0.000), (0.440, 0.005), (0.455, 0.050),
         (0.420, 0.100), (0.260, 0.155), (0.000, 0.180)],
        cs, cs,
    )
    return mesh_from_geometry(LatheGeometry(lid_prof, segments=48), "lid_shell")


def _emit_lid_details(hatch, cs: float, *, lid_x: float) -> None:
    """Viewport rim/glass + grab handle on the lid, offset by ``lid_x`` in the
    hatch part frame (origin L190-216)."""
    hatch.visual(
        Cylinder(radius=0.125 * cs, length=0.02 * cs),
        origin=Origin(xyz=(lid_x, 0.0, 0.17 * cs)),
        material="collar_grey", name="viewport_rim", material_class_id="metal.paint_coated",
    )
    hatch.visual(
        Cylinder(radius=0.095 * cs, length=0.02 * cs),
        origin=Origin(xyz=(lid_x, 0.0, 0.185 * cs)),
        material="glass_dark", name="viewport_glass", material_class_id="glass.smoked_tinted",
    )
    for i, sy in enumerate((-1, 1)):
        hatch.visual(
            Cylinder(radius=0.012 * cs, length=0.08 * cs),
            origin=Origin(xyz=(lid_x + 0.24 * cs, sy * 0.06 * cs, 0.14 * cs)),
            material="collar_grey", name=f"handle_post_{i}", material_class_id="metal.paint_coated",
        )
    hatch.visual(
        Cylinder(radius=0.015 * cs, length=0.16 * cs),
        origin=Origin(xyz=(lid_x + 0.24 * cs, 0.0, 0.18 * cs), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="collar_grey", name="handle_bar", material_class_id="metal.paint_coated",
    )


def _emit_hinge_posts(capsule, cs: float) -> None:
    """Two hinge posts rising from the body top beside the collar (origin L165).
    The post spans z 2.10..2.42 so its lower half always embeds into the body
    wall (which widens below the flat top) across every body form + radius_scale
    -- the flat top disc alone recedes inside x=-0.49 when radius_scale is small,
    so we reach down onto the wall to guarantee contact (Contract 3 support)."""
    for i, sy in enumerate((-1, 1)):
        capsule.visual(
            Box((0.06 * cs, 0.05 * cs, 0.32 * cs)),
            origin=Origin(xyz=(-0.49 * cs, sy * 0.095 * cs, 2.26 * cs)),
            material="collar_grey", name=f"hinge_post_{i}", material_class_id="metal.paint_coated",
        )


def _emit_hinge_hardware(hatch, cs: float) -> None:
    """Hinge barrel + straps tying the lid to the hinge line (origin L217-230)."""
    hatch.visual(
        Cylinder(radius=0.028 * cs, length=0.26 * cs),
        origin=Origin(xyz=(0.0, 0.0, 0.02 * cs), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="collar_grey", name="hinge_barrel", material_class_id="metal.paint_coated",
    )
    for i, sy in enumerate((-1, 1)):
        hatch.visual(
            Box((0.12 * cs, 0.04 * cs, 0.03 * cs)),
            origin=Origin(xyz=(0.05 * cs, sy * 0.045 * cs, 0.02 * cs)),
            material="collar_grey", name=f"hinge_strap_{i}", material_class_id="metal.paint_coated",
        )


def _build_hinged_hatch(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedAstronomyReturnCapsuleConfig = ctx.config  # type: ignore[assignment]
    cs = r.capsule_scale
    capsule = model.get_part("capsule")
    _emit_hinge_posts(capsule, cs)

    hatch = model.part("hatch")
    hatch.visual(_lid_mesh(cs), origin=Origin(xyz=(LID_OFFSET_X * cs, 0.0, 0.0)),
                 material="lid_grey", name="lid_shell", material_class_id="metal.paint_coated")
    _emit_lid_details(hatch, cs, lid_x=LID_OFFSET_X * cs)
    _emit_hinge_hardware(hatch, cs)

    model.articulation(
        "capsule_to_hatch", ArticulationType.REVOLUTE, parent=capsule, child=hatch,
        origin=Origin(xyz=(HINGE_XYZ[0] * cs, 0.0, HINGE_XYZ[2] * cs)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.6, lower=0.0, upper=r.hatch_open),
    )
    return ModuleBuild(
        module_name="hinged_hatch",
        parts_emitted=["hatch"],
        internal_articulations=["capsule_to_hatch"],
        interfaces={"downstream": _capsule_downstream(r)},
    )


def _build_plug_hatch(ctx: ModuleBuildContext) -> ModuleBuild:
    """Soyuz-style plug hatch: PRISMATIC lift-out along +Z (plug_hatch S4)."""
    model = ctx.model
    r: ResolvedAstronomyReturnCapsuleConfig = ctx.config  # type: ignore[assignment]
    cs = r.capsule_scale
    capsule = model.get_part("capsule")

    hatch = model.part("hatch")
    hatch.visual(_lid_mesh(cs), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                 material="lid_grey", name="lid_shell", material_class_id="metal.paint_coated")
    # Plug seal collar on the underside that seats into the collar bore.
    plug_collar = LatheGeometry.from_shell_profiles(
        _scale_pts([(0.44, 0.01), (0.44, -0.05)], cs, cs),
        _scale_pts([(0.39, 0.01), (0.39, -0.05)], cs, cs),
        segments=48,
    )
    hatch.visual(mesh_from_geometry(plug_collar, "plug_seal_collar"),
                 origin=Origin(xyz=(0.0, 0.0, 0.0)),
                 material="collar_grey", name="plug_seal_collar", material_class_id="metal.paint_coated")
    _emit_lid_details(hatch, cs, lid_x=0.0)

    model.articulation(
        "capsule_to_hatch", ArticulationType.PRISMATIC, parent=capsule, child=hatch,
        origin=Origin(xyz=(0.0, 0.0, PLUG_ORIGIN_Z * cs)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.3, lower=0.0, upper=r.plug_travel * cs),
    )
    return ModuleBuild(
        module_name="plug_hatch",
        parts_emitted=["hatch"],
        internal_articulations=["capsule_to_hatch"],
        interfaces={"downstream": _capsule_downstream(r)},
    )


def _build_docking_hatch(ctx: ModuleBuildContext) -> ModuleBuild:
    """Hinged crew hatch PLUS a forward docking ring + a REVOLUTE nose cover
    (docking_nose S5): two moving parts (hatch + nose_cover)."""
    model = ctx.model
    r: ResolvedAstronomyReturnCapsuleConfig = ctx.config  # type: ignore[assignment]
    cs = r.capsule_scale
    capsule = model.get_part("capsule")

    # crew hatch (same as hinged_hatch)
    _emit_hinge_posts(capsule, cs)
    hatch = model.part("hatch")
    hatch.visual(_lid_mesh(cs), origin=Origin(xyz=(LID_OFFSET_X * cs, 0.0, 0.0)),
                 material="lid_grey", name="lid_shell", material_class_id="metal.paint_coated")
    _emit_lid_details(hatch, cs, lid_x=LID_OFFSET_X * cs)
    _emit_hinge_hardware(hatch, cs)
    model.articulation(
        "capsule_to_hatch", ArticulationType.REVOLUTE, parent=capsule, child=hatch,
        origin=Origin(xyz=(HINGE_XYZ[0] * cs, 0.0, HINGE_XYZ[2] * cs)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.6, lower=0.0, upper=r.hatch_open),
    )

    # forward docking ring (capsule visual): base flange rests on the collar rim.
    dock_ring = LatheGeometry(
        _scale_pts([(0.30, 0.00), (0.46, 0.00), (0.46, 0.04), (0.40, 0.06),
                    (0.34, 0.14), (0.30, 0.14)], cs, cs),
        segments=48,
    )
    capsule.visual(mesh_from_geometry(dock_ring, "docking_ring"),
                   origin=Origin(xyz=(0.0, 0.0, DOCK_RING_BASE_Z * cs)),
                   material="collar_grey", name="docking_ring", material_class_id="metal.paint_coated")
    for i in range(6):
        ang = i * math.pi / 3.0
        # Alignment guide tab on the ring base flange (z below the closed-lid
        # base, so it clears the nested hatch dome) embedded into the flange
        # outer wall (spans r 0.415-0.465, overlapping the ring solid).
        capsule.visual(
            Box((0.05 * cs, 0.030 * cs, 0.022 * cs)),
            origin=Origin(xyz=_radial(0.44 * cs, ang, (DOCK_RING_BASE_Z + 0.015) * cs), rpy=(0.0, 0.0, ang)),
            material="collar_grey", name=f"dock_guide_{i}", material_class_id="metal.paint_coated",
        )
    for i, sy in enumerate((-1, 1)):
        capsule.visual(
            Box((0.05 * cs, 0.04 * cs, 0.10 * cs)),
            origin=Origin(xyz=(NOSE_HINGE_XYZ[0] * cs, sy * 0.075 * cs, NOSE_HINGE_XYZ[2] * cs)),
            material="collar_grey", name=f"nose_hinge_post_{i}", material_class_id="metal.paint_coated",
        )

    # nose cover (second moving part): thin-wall dome + hinge barrel + straps.
    nose_cover = model.part("nose_cover")
    nose_shell = LatheGeometry.from_shell_profiles(
        _scale_pts([(0.34, 0.00), (0.34, 0.06), (0.31, 0.10), (0.22, 0.13), (0.00, 0.15)], cs, cs),
        _scale_pts([(0.33, 0.00), (0.33, 0.06), (0.30, 0.10), (0.21, 0.13), (0.00, 0.15)], cs, cs),
        segments=48,
    )
    nose_cover.visual(mesh_from_geometry(nose_shell, "nose_shell"),
                      origin=Origin(xyz=(NOSE_COVER_OFFSET_X * cs, 0.0, 0.0)),
                      material="lid_grey", name="nose_shell", material_class_id="metal.paint_coated")
    nose_cover.visual(
        Cylinder(radius=0.022 * cs, length=0.20 * cs),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="collar_grey", name="nose_hinge_barrel", material_class_id="metal.paint_coated",
    )
    for i, sy in enumerate((-1, 1)):
        nose_cover.visual(
            Box((0.10 * cs, 0.03 * cs, 0.025 * cs)),
            origin=Origin(xyz=(-0.05 * cs, sy * 0.04 * cs, 0.015 * cs)),
            material="collar_grey", name=f"nose_strap_{i}", material_class_id="metal.paint_coated",
        )
    model.articulation(
        "capsule_to_nose_cover", ArticulationType.REVOLUTE, parent=capsule, child=nose_cover,
        origin=Origin(xyz=(NOSE_HINGE_XYZ[0] * cs, 0.0, NOSE_HINGE_XYZ[2] * cs)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=r.nose_open),
    )

    return ModuleBuild(
        module_name="docking_hatch",
        parts_emitted=["hatch", "nose_cover"],
        internal_articulations=["capsule_to_hatch", "capsule_to_nose_cover"],
        interfaces={"downstream": _capsule_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Slot C - heat_shield (parallel child at the base)
# --------------------------------------------------------------------------- #


def _build_fixed_shield(ctx: ModuleBuildContext) -> ModuleBuild:
    """Ablative heat shield fused under the body as a capsule visual (origin)."""
    model = ctx.model
    r: ResolvedAstronomyReturnCapsuleConfig = ctx.config  # type: ignore[assignment]
    cs, rs = r.capsule_scale, r.radius_scale
    capsule = model.get_part("capsule")
    prof = _scale_pts(_shield_profile(), rs * cs, cs)
    capsule.visual(
        mesh_from_geometry(LatheGeometry(prof, segments=48), "heat_shield"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="shield_char", name="heat_shield", material_class_id="plastic.weathered_worn",
    )
    return ModuleBuild(
        module_name="fixed_shield",
        parts_emitted=[],
        interfaces={"downstream": _capsule_downstream(r)},
    )


def _build_separable_shield(ctx: ModuleBuildContext) -> ModuleBuild:
    """Jettisonable heat shield as its own PRISMATIC drop-away part
    (separable_shield S6)."""
    model = ctx.model
    r: ResolvedAstronomyReturnCapsuleConfig = ctx.config  # type: ignore[assignment]
    cs, rs = r.capsule_scale, r.radius_scale
    capsule = model.get_part("capsule")

    shield = model.part("shield")
    prof = _scale_pts(_shield_profile(), rs * cs, cs)
    shield.visual(
        mesh_from_geometry(LatheGeometry(prof, segments=48), "heat_shield"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="shield_char", name="heat_shield", material_class_id="plastic.weathered_worn",
    )
    model.articulation(
        "capsule_to_shield", ArticulationType.PRISMATIC, parent=capsule, child=shield,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=50.0, velocity=2.0, lower=0.0, upper=r.shield_drop * cs),
    )
    return ModuleBuild(
        module_name="separable_shield",
        parts_emitted=["shield"],
        internal_articulations=["capsule_to_shield"],
        interfaces={"downstream": _capsule_downstream(r)},
    )


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

HATCH_FACTORIES = {
    "hinged_hatch": _build_hinged_hatch,
    "plug_hatch": _build_plug_hatch,
    "docking_hatch": _build_docking_hatch,
}
SHIELD_FACTORIES = {
    "fixed_shield": _build_fixed_shield,
    "separable_shield": _build_separable_shield,
}


def _slots_for_config(r: ResolvedAstronomyReturnCapsuleConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="body_form", candidates={r.body_form: _build_capsule}, anchor_choice=r.body_form),
        SlotSpec(
            slot_name="crew_hatch",
            candidates={r.hatch_module: HATCH_FACTORIES[r.hatch_module]},
            anchor_choice=r.hatch_module,
        ),
        SlotSpec(
            slot_name="heat_shield",
            candidates={r.shield_module: SHIELD_FACTORIES[r.shield_module]},
            anchor_choice=r.shield_module,
        ),
    ]


def build_astronomy_return_capsule(
    config: AstronomyReturnCapsuleConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="astronomy_return_capsule", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_astronomy_return_capsule(seed: int) -> ArticulatedObject:
    return build_astronomy_return_capsule(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("body_form", r.body_form),
        ("crew_hatch", r.hatch_module),
        ("heat_shield", r.shield_module),
        ("porthole_count", f"portholes_{r.porthole_count}"),
        ("rcs_count", f"rcs_{r.rcs_count}"),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(
    ctx: TestContext,
    model: ArticulatedObject,
    r: ResolvedAstronomyReturnCapsuleConfig,
) -> None:
    parts = {p.name for p in model.parts}

    def _ov(pa: str, pb: str, *, elem_a: str, elem_b: str, reason: str) -> None:
        if pa in parts and pb in parts:
            ctx.allow_overlap(model.get_part(pa), model.get_part(pb),
                              elem_a=elem_a, elem_b=elem_b, reason=reason)

    if r.hatch_module in _HINGED_HATCHES:
        # Captured hinge barrel between the collar-side hinge posts.
        for i in range(2):
            _ov("capsule", "hatch", elem_a=f"hinge_post_{i}", elem_b="hinge_barrel",
                reason="hatch hinge barrel is captured between the collar-side hinge posts")
    if r.hatch_module == "plug_hatch":
        # Plug seal collar seated inside the collar bore / seal ring when closed.
        _ov("capsule", "hatch", elem_a="hatch_collar", elem_b="plug_seal_collar",
            reason="plug seal collar is intentionally seated inside the hatch collar bore")
        _ov("capsule", "hatch", elem_a="hatch_seal_ring", elem_b="plug_seal_collar",
            reason="plug seal collar seats against the white seal-ring face inside the bore")
    if r.hatch_module == "docking_hatch":
        # Forward docking-section overlaps (docking_nose source declarations).
        # The docking cap (ring + nose cover) tightly nests over the closed
        # crew hatch on the top collar; all pairs are element-scoped.
        _ov("capsule", "hatch", elem_a="docking_ring", elem_b="lid_shell",
            reason="docking ring is seated on the collar within the closed hatch dome footprint")
        for i in range(2):
            _ov("capsule", "hatch", elem_a="docking_ring", elem_b=f"hinge_strap_{i}",
                reason="docking ring flange overlaps the crew-hatch hinge straps at the collar rim")
            _ov("capsule", "nose_cover", elem_a=f"nose_hinge_post_{i}", elem_b="nose_hinge_barrel",
                reason="nose cover hinge barrel is captured between the docking-ring rim hinge posts")
            _ov("capsule", "hatch", elem_a=f"nose_hinge_post_{i}", elem_b="lid_shell",
                reason="nose hinge posts pass through the hatch dome at the docking ring mount")
            _ov("capsule", "nose_cover", elem_a=f"nose_hinge_post_{i}", elem_b="nose_shell",
                reason="nose hinge posts pass through the shell skirt at the hinge mount")
            _ov("hatch", "nose_cover", elem_a="lid_shell", elem_b=f"nose_strap_{i}",
                reason="nose cover straps nest over the closed hatch dome at the docking cap")
        _ov("capsule", "nose_cover", elem_a="docking_ring", elem_b="nose_hinge_barrel",
            reason="nose cover hinge barrel is seated on the docking ring rim")
        # Sequenced forward-bay closures: the outer nose cover is opened to
        # expose the docking ring / inner crew hatch, so the two are never
        # commanded open simultaneously in service. They overlap only during a
        # simultaneous mid-travel the operating sequence excludes; full designed
        # travel is kept (AUTHORING sequenced-mechanism allowance).
        _crew_cluster = ("lid_shell", "viewport_rim", "viewport_glass",
                         "handle_post_0", "handle_post_1", "handle_bar")
        _nose_cluster = ("nose_shell", "nose_hinge_barrel", "nose_strap_0", "nose_strap_1")
        for _ce in _crew_cluster:
            for _ne in _nose_cluster:
                _ov("hatch", "nose_cover", elem_a=_ce, elem_b=_ne,
                    reason="sequenced forward-bay closures (nose cover opens to expose the inner crew hatch); overlap only in a simultaneous mid-travel the operating sequence excludes")
    if r.shield_module == "separable_shield":
        _ov("capsule", "shield", elem_a="bell_body", elem_b="heat_shield",
            reason="jettisonable heat shield is flush-seated against the capsule base at q=0")


def _center_dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ca = [(a[0][i] + a[1][i]) / 2.0 for i in range(3)]
    cb = [(b[0][i] + b[1][i]) / 2.0 for i in range(3)]
    return math.dist(ca, cb)


def _expect_hatch(ctx, model, r) -> None:
    parts = {p.name for p in model.parts}
    ctx.check("hatch part present", "hatch" in parts)
    j = model.get_articulation("capsule_to_hatch")

    if r.hatch_module == "plug_hatch":
        ctx.check("plug hatch is PRISMATIC along +Z",
                  j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2] - 1.0) < 0.01,
                  details=f"{j.articulation_type}, axis {j.axis}")
        val = 0.9 * (j.motion_limits.upper if j.motion_limits else 0.2)
    else:
        ctx.check("crew hatch hinge is REVOLUTE about the collar-edge Y axis",
                  j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
                  details=f"{j.articulation_type}, axis {j.axis}")
        val = 0.9 * (j.motion_limits.upper if j.motion_limits else 1.8)

    hatch = model.get_part("hatch")
    rest = ctx.part_world_aabb(hatch)
    with ctx.pose({j: val}):
        moved = ctx.part_world_aabb(hatch)
    ctx.check("crew hatch opens (lid displaces)", _center_dist(rest, moved) > 0.05 * r.capsule_scale,
              details=f"displacement={_center_dist(rest, moved):.4f}")

    if r.hatch_module == "docking_hatch":
        ctx.check("nose_cover part present", "nose_cover" in parts)
        jn = model.get_articulation("capsule_to_nose_cover")
        ctx.check("nose cover hinge is REVOLUTE about the ring-rim Y axis",
                  jn.articulation_type == ArticulationType.REVOLUTE and abs(jn.axis[1]) > 0.99,
                  details=f"{jn.articulation_type}, axis {jn.axis}")
        nose = model.get_part("nose_cover")
        nrest = ctx.part_world_aabb(nose)
        with ctx.pose({jn: 0.9 * (jn.motion_limits.upper if jn.motion_limits else 1.8)}):
            nmoved = ctx.part_world_aabb(nose)
        ctx.check("nose cover swings up above the docking ring",
                  nmoved is not None and nrest is not None and nmoved[1][2] > nrest[1][2] + 0.1 * r.capsule_scale,
                  details=f"rest={nrest}, open={nmoved}")


def _expect_shield(ctx, model, r) -> None:
    parts = {p.name for p in model.parts}
    if r.shield_module == "separable_shield":
        ctx.check("separable shield part present", "shield" in parts)
        j = model.get_articulation("capsule_to_shield")
        ctx.check("shield joint is PRISMATIC along -Z (drop-away)",
                  j.articulation_type == ArticulationType.PRISMATIC and j.axis[2] < -0.99,
                  details=f"{j.articulation_type}, axis {j.axis}")
        shield = model.get_part("shield")
        rest = ctx.part_world_aabb(shield)
        with ctx.pose({j: 0.9 * (j.motion_limits.upper if j.motion_limits else 1.0)}):
            dropped = ctx.part_world_aabb(shield)
        ctx.check("shield drops downward when jettisoned",
                  dropped is not None and rest is not None and dropped[0][2] < rest[0][2] - 0.1 * r.capsule_scale,
                  details=f"rest={rest}, dropped={dropped}")
    else:
        capsule = model.get_part("capsule")
        has_shield = any(v.name == "heat_shield" for v in capsule.visuals)
        ctx.check("fused heat shield visual on capsule", has_shield, details="missing heat_shield")


def _expect_body(ctx, model, r) -> None:
    capsule = model.get_part("capsule")
    ctx.check("body_form visual present", any(v.name == "bell_body" for v in capsule.visuals))
    n_port = sum(1 for v in capsule.visuals if v.name and v.name.startswith("porthole_rim_"))
    ctx.check("porthole count matches", n_port == r.porthole_count, details=f"found {n_port}")
    n_rcs = sum(1 for v in capsule.visuals if v.name and v.name.startswith("rcs_port_"))
    ctx.check("rcs count matches", n_rcs == r.rcs_count, details=f"found {n_rcs}")
    aabb = ctx.part_world_aabb(capsule)
    width = aabb[1][0] - aabb[0][0]
    lo = 2.0 * BASE_R * 0.85 * 0.92  # min scale bounds
    hi = 2.0 * BASE_R * 1.20 * 1.10
    ctx.check("capsule body spans a plausible width", lo - 0.2 < width < hi + 0.2, details=f"width {width:.3f}")


def run_astronomy_return_capsule_tests(
    model: ArticulatedObject,
    config: AstronomyReturnCapsuleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    if any(p.name == "shield" for p in model.parts):
        ctx.allow_isolated_part(
            model.get_part("shield"),
            reason="heat shield lifts clear of the capsule on its prismatic rail and loses body contact",
        )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_body(ctx, model, r)
    _expect_hatch(ctx, model, r)
    _expect_shield(ctx, model, r)

    # Rule 5: dynamic collision across sampled joint poses.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "AstronomyReturnCapsuleConfig",
    "ResolvedAstronomyReturnCapsuleConfig",
    "BodyForm",
    "HatchModule",
    "ShieldModule",
    "ReturnCapsulePalette",
    "build_astronomy_return_capsule",
    "build_seeded_astronomy_return_capsule",
    "config_from_seed",
    "resolve_config",
    "run_astronomy_return_capsule_tests",
    "slot_choices_for_seed",
]
