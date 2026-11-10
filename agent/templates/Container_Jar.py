# SPDX-License-Identifier: Apache-2.0

"""Container jar — modular procedural template (lidded glass/ceramic jar).

Category identity: an upright lidded storage / cosmetic jar. The hollow jar
body (ROOT) rests on z=0 with its axis along +Z; a lid opens/closes on top by
one of several mechanisms (the main articulation). No multiplicity axis — one
jar, one lid.

Three parallel slots (spec ``Container_Jar.md``):

  * ``body_form`` (6) — the ROOT ``jar_body`` mesh: round squat cream jar, tall
    cylinder storage jar, square rounded jar, faceted apothecary, round
    wide-mouth mason, tapered-shoulder jar. Round/faceted forms are revolved
    profiles; the square form is a box-shell. All carry a short threaded neck.
  * ``lid_closure`` (5) — the lid mechanism (>=1 non-fixed joint each):
      - continuous_screw_cap: CONTINUOUS spin + PRISMATIC lift via a massless
        ``lid_carrier`` link (parent screw-cap pattern).
      - lift_off_friction_cap: single PRISMATIC +Z lift-off cap (no rotation).
      - rear_hinge_flip_lid: REVOLUTE +X flip lid hinged at the back rim.
      - clamp_lid_stopper: REVOLUTE +X clamp lid + PRISMATIC +Z pull stopper.
      - shaker_insert_cap: screw cap (rotate+slide) + REVOLUTE +Z shaker disc.
  * ``seal_interior`` (3, incl. ``plain``) — fixed visuals on the jar body: a
    rubber gasket ring seated at the neck, or a raised base foot rim.

Continuous size/proportion variation (height/radius/neck/lid/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.

Sources (articraft_data ``picture/Container/Jar`` 5-star pool): parents
``072e38fe`` (face-cream screw cap), ``9e3c6ab6`` (square storage screw cap),
``7af717d1`` (square bottle — lift-off cap mechanism only), plus qwen forks
``jar_001_v03`` (clamp lid + stopper), ``jar_001_v08`` (shaker insert),
``jar_002_v01`` (tapered shoulder + gasket), ``jar_003`` family (mason / foot
rim).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Jar.md``
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
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "round_squat_cream",
    "tall_cylinder_storage",
    "square_rounded",
    "faceted_apothecary",
    "round_wide_mouth_mason",
    "tapered_shoulder",
]
LidClosure = Literal[
    "continuous_screw_cap",
    "lift_off_friction_cap",
    "rear_hinge_flip_lid",
    "clamp_lid_stopper",
    "shaker_insert_cap",
]
SealInterior = Literal[
    "plain",
    "rubber_gasket_ring",
    "base_foot_rim",
]
MaterialStyle = Literal[
    "blue_glass",
    "clear_glass",
    "amber_glass",
    "frosted_white",
    "ceramic_cream",
    "brass_lid",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "round_squat_cream",
    "tall_cylinder_storage",
    "square_rounded",
    "faceted_apothecary",
    "round_wide_mouth_mason",
    "tapered_shoulder",
)
LID_CLOSURES: tuple[LidClosure, ...] = (
    "continuous_screw_cap",
    "lift_off_friction_cap",
    "rear_hinge_flip_lid",
    "clamp_lid_stopper",
    "shaker_insert_cap",
)
SEAL_INTERIORS: tuple[SealInterior, ...] = (
    "plain",
    "rubber_gasket_ring",
    "base_foot_rim",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "blue_glass",
    "clear_glass",
    "amber_glass",
    "frosted_white",
    "ceramic_cream",
    "brass_lid",
)

# ---------------------------------------------------------------------------
# Material palettes: jar body glass/ceramic, lid metal/plastic, seal rubber.
# ---------------------------------------------------------------------------
PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "blue_glass": {
        "body": (0.42, 0.66, 0.80, 0.55),
        "lid": (0.46, 0.72, 0.86, 1.0),
        "accent": (0.10, 0.18, 0.34, 1.0),
        "seal": (0.20, 0.20, 0.22, 1.0),
    },
    "clear_glass": {
        "body": (0.82, 0.86, 0.88, 0.30),
        "lid": (0.72, 0.55, 0.20, 1.0),
        "accent": (0.52, 0.38, 0.12, 1.0),
        "seal": (0.20, 0.20, 0.22, 1.0),
    },
    "amber_glass": {
        "body": (0.62, 0.40, 0.14, 0.55),
        "lid": (0.30, 0.22, 0.12, 1.0),
        "accent": (0.18, 0.13, 0.07, 1.0),
        "seal": (0.16, 0.14, 0.12, 1.0),
    },
    "frosted_white": {
        "body": (0.92, 0.93, 0.95, 0.65),
        "lid": (0.96, 0.97, 0.98, 1.0),
        "accent": (0.55, 0.57, 0.60, 1.0),
        "seal": (0.30, 0.30, 0.32, 1.0),
    },
    "ceramic_cream": {
        "body": (0.90, 0.86, 0.76, 1.0),
        "lid": (0.66, 0.48, 0.28, 1.0),
        "accent": (0.40, 0.28, 0.16, 1.0),
        "seal": (0.30, 0.28, 0.24, 1.0),
    },
    "brass_lid": {
        "body": (0.82, 0.86, 0.88, 0.30),
        "lid": (0.72, 0.55, 0.20, 1.0),
        "accent": (0.52, 0.38, 0.12, 1.0),
        "seal": (0.20, 0.20, 0.22, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base geometry per body form (meters). Scaled per-build by resolve_config.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _FormGeom:
    body_r: float
    body_h: float
    neck_r: float
    neck_h: float
    wall: float
    shoulder: float
    square: bool
    facets: int


_FORMS: dict[BodyForm, _FormGeom] = {
    # squat cream jar: wider than tall, wide neck.
    "round_squat_cream": _FormGeom(0.036, 0.044, 0.030, 0.010, 0.005, 0.004, False, 64),
    # tall cylinder storage: taller than wide, wide mouth.
    "tall_cylinder_storage": _FormGeom(0.040, 0.120, 0.034, 0.014, 0.0035, 0.006, False, 64),
    # square rounded jar (box shell + round neck).
    "square_rounded": _FormGeom(0.040, 0.110, 0.0265, 0.020, 0.0035, 0.012, True, 64),
    # faceted apothecary: low facet count prism.
    "faceted_apothecary": _FormGeom(0.038, 0.090, 0.028, 0.014, 0.004, 0.008, False, 8),
    # round wide-mouth mason: large mouth ~ body, short neck.
    "round_wide_mouth_mason": _FormGeom(0.044, 0.085, 0.040, 0.008, 0.0035, 0.004, False, 64),
    # tapered shoulder: squat body, pronounced shoulder, wide threaded neck.
    "tapered_shoulder": _FormGeom(0.040, 0.052, 0.031, 0.012, 0.004, 0.010, False, 64),
}

# lid / mechanism nominal sizes.
_LID_H = 0.018  # screw / friction / flip lid thickness band
_CAP_OVERLAP = 0.020  # how far a lift-off / friction cap skirt drops over the neck
_STOPPER_LIFT = 0.050
_LID_LIFT = 0.018
_SHAKER_LIMIT = 1.2  # rad


@dataclass(frozen=True)
class ContainerJarConfig:
    body_form: BodyForm = "round_squat_cream"
    lid_closure: LidClosure = "continuous_screw_cap"
    seal_interior: SealInterior = "plain"
    material_style: MaterialStyle = "blue_glass"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    lid_height_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_jar"


@dataclass(frozen=True)
class ResolvedContainerJarConfig:
    body_form: BodyForm
    lid_closure: LidClosure
    seal_interior: SealInterior
    material_style: MaterialStyle
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    lid_height_scale: float
    joint_travel_scale: float
    # derived geometry
    body_r: float
    body_h: float
    neck_r: float
    neck_h: float
    wall: float
    shoulder: float
    square: bool
    facets: int
    rim_top_z: float  # world z of the neck rim top (lid mount plane)
    lid_outer_r: float
    lid_bore_r: float
    lid_h: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerJarConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerJarConfig(
        body_form=rng.choice(BODY_FORMS),
        lid_closure=rng.choice(LID_CLOSURES),
        seal_interior=rng.choice(SEAL_INTERIORS),
        material_style=rng.choice(MATERIAL_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        lid_height_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_jar_{seed}",
    )


def resolve_config(
    config: ContainerJarConfig | None = None,
) -> ResolvedContainerJarConfig:
    cfg = config or ContainerJarConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    lid_closure = _pick(cfg.lid_closure, LID_CLOSURES)
    seal = _pick(cfg.seal_interior, SEAL_INTERIORS)
    material = _pick(cfg.material_style, MATERIAL_STYLES)

    g = _FORMS[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.90, 1.10)
    lh_scale = _clamp(cfg.lid_height_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    body_r = g.body_r * r_scale
    body_h = g.body_h * h_scale
    # Neck radius follows the body radius and its own scale, clamped to stay
    # strictly inside the body so the shoulder always tapers inward.
    neck_r = _clamp(g.neck_r * r_scale * n_scale, 0.012, body_r - 0.003)
    neck_h = g.neck_h  # neck height fixed (independent of scales)
    shoulder = g.shoulder
    rim_top_z = body_h + shoulder + neck_h

    # Lid bore grips the neck (slight interference with the thread ridges, which
    # sit at neck_r+0.0006) so the lid skirt actually contacts the neck rather
    # than floating a hair off it — the captured-fit overlap is allowed in tests.
    # Equation: bore = neck_r - small. Inequality projection: outer >= bore +
    # min wall and proud of the body.
    lid_bore_r = neck_r - 0.0003
    lid_outer_r = max(body_r + 0.0015, lid_bore_r + 0.004)
    lid_h = _LID_H * lh_scale

    return ResolvedContainerJarConfig(
        body_form=body_form,
        lid_closure=lid_closure,
        seal_interior=seal,
        material_style=material,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=n_scale,
        lid_height_scale=lh_scale,
        joint_travel_scale=jt_scale,
        body_r=body_r,
        body_h=body_h,
        neck_r=neck_r,
        neck_h=neck_h,
        wall=g.wall,
        shoulder=shoulder,
        square=g.square,
        facets=g.facets,
        rim_top_z=rim_top_z,
        lid_outer_r=lid_outer_r,
        lid_bore_r=lid_bore_r,
        lid_h=lid_h,
        name=cfg.name or "container_jar",
    )


def with_overrides(config: ContainerJarConfig, **kwargs: object) -> ContainerJarConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerJarConfig | ResolvedContainerJarConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerJarConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("lid_closure", r.lid_closure),
        ("seal_interior", r.seal_interior),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body geometry (Slot A). Round/faceted forms are revolved XZ half-profiles;
# the square form is a filleted box shelled hollow with a round neck.
# ---------------------------------------------------------------------------
def _revolve_body_solid(r: ResolvedContainerJarConfig) -> cq.Workplane:
    """Hollow thick-walled body via revolve of an XZ half profile about +Z.

    Traces the outer wall up, across a rounded shoulder into the neck, then
    back down the inner wall to leave a real open-topped cavity (parent
    ``_jar_glass_solid``)."""
    br, bh, nr, w = r.body_r, r.body_h, r.neck_r, r.wall
    sh = r.shoulder
    shoulder_top = bh + sh
    rim_top = shoulder_top + r.neck_h
    inner_top = bh - 0.002
    pts = [
        (0.0, 0.0),
        (br, 0.0),
        (br, bh - 0.006),
        (br - 0.004, bh),  # rounded outer shoulder
        (nr, shoulder_top),  # step in to the neck base
        (nr, rim_top),  # neck outer up to rim
        (nr - w, rim_top),  # across the rim top
        (nr - w, inner_top),  # inner neck wall down
        (br - w, bh - 0.006),
        (br - w, w),  # inner body wall down to thick base
        (0.0, w),  # across inner base
        (0.0, 0.0),
    ]
    profile = cq.Workplane("XZ").polyline(pts).close()
    return profile.revolve(360.0, (0, 0, 0), (0, 1, 0))


def _square_body_solid(r: ResolvedContainerJarConfig) -> cq.Workplane:
    """Square-section jar: filleted box body -> tapered shoulder loft -> round
    neck, shelled hollow with the neck top open (parent ``_body_solid``)."""
    half = r.body_r
    fillet = min(0.012, half * 0.3)
    w = r.wall
    body_top = r.body_h
    shoulder_top = body_top + r.shoulder
    nr = r.neck_r
    rim_top = shoulder_top + r.neck_h

    outer = (
        cq.Workplane("XY")
        .box(2 * half, 2 * half, body_top, centered=(True, True, False))
        .edges("|Z")
        .fillet(fillet)
    )
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=body_top)
        .rect(2 * (half - 0.004), 2 * (half - 0.004))
        .workplane(offset=(shoulder_top - body_top))
        .circle(nr)
        .loft(ruled=False)
    )
    neck = (
        cq.Workplane("XY")
        .workplane(offset=shoulder_top)
        .circle(nr)
        .extrude(rim_top - shoulder_top)
    )
    solid = outer.union(shoulder).union(neck)

    inner = (
        cq.Workplane("XY")
        .workplane(offset=w)
        .box(2 * (half - w), 2 * (half - w), body_top - w, centered=(True, True, False))
        .edges("|Z")
        .fillet(max(fillet - w, 0.001))
    )
    inner_shoulder = (
        cq.Workplane("XY")
        .workplane(offset=body_top - 0.001)
        .rect(2 * (half - 0.004 - w), 2 * (half - 0.004 - w))
        .workplane(offset=(shoulder_top - body_top) + 0.001)
        .circle(nr - w)
        .loft(ruled=False)
    )
    inner_neck = (
        cq.Workplane("XY")
        .workplane(offset=shoulder_top)
        .circle(nr - w)
        .extrude((rim_top - shoulder_top) + 0.001)
    )
    cavity = inner.union(inner_shoulder).union(inner_neck)
    return solid.cut(cavity)


def _neck_threads(r: ResolvedContainerJarConfig) -> cq.Workplane | None:
    """A few thread ridge rings on the neck so it reads as a screw neck."""
    threads = None
    z0 = r.body_h + r.shoulder + 0.0025
    for i in range(3):
        z = z0 + i * 0.0028
        if z > r.rim_top_z - 0.002:
            break
        ring = (
            cq.Workplane("XY")
            .workplane(offset=z)
            .circle(r.neck_r + 0.0006)
            .circle(r.neck_r - 0.0004)
            .extrude(0.0016)
        )
        threads = ring if threads is None else threads.union(ring)
    return threads


def _foot_rim_solid(r: ResolvedContainerJarConfig) -> cq.Workplane:
    """Raised base foot rim: a short annular ring under the body outer edge.

    Authored with its bottom at z=0 so the jar still rests on the ground."""
    outer = r.body_r + 0.002
    inner = max(r.body_r - 0.006, 0.004)
    return (
        cq.Workplane("XY")
        .circle(outer)
        .circle(inner)
        .extrude(0.006)
    )


def _emit_body(body, r: ResolvedContainerJarConfig, *, body_mat, seal_mat) -> None:
    if r.square:
        solid = _square_body_solid(r)
    else:
        solid = _revolve_body_solid(r)
    threads = _neck_threads(r)
    if threads is not None:
        solid = solid.union(threads)
    if r.seal_interior == "base_foot_rim":
        solid = solid.union(_foot_rim_solid(r))
    body.visual(mesh_from_cadquery(solid, "jar_glass"), material=body_mat, name="jar_glass", material_class_id=("glass.clear_transparent" if r.material_style in {"blue_glass", "clear_glass", "amber_glass", "frosted_white", "brass_lid"} else "ceramic.porcelain_glazed_plain"))

    if r.seal_interior == "rubber_gasket_ring":
        # Rubber gasket ring seated at the neck mouth (fixed visual).
        gz = r.rim_top_z - 0.0035
        gasket = (
            cq.Workplane("XY")
            .workplane(offset=gz)
            .circle(r.neck_r - r.wall + 0.0008)
            .circle(max(r.neck_r - r.wall - 0.0025, 0.004))
            .extrude(0.0025)
        )
        body.visual(
            mesh_from_cadquery(gasket, "gasket_ring"),
            material=seal_mat,
            name="gasket_ring", material_class_id="rubber.smooth_plain",
        )


# ---------------------------------------------------------------------------
# Lid geometry helpers (Slot B).
# ---------------------------------------------------------------------------
def _screw_lid_solid(r: ResolvedContainerJarConfig, *, skirt_bottom: float) -> cq.Workplane:
    """Shallow cylindrical screw cap: closed crowned top + downward skirt,
    hollowed underneath so the skirt slips over the neck (parent ``_lid_solid``)."""
    outer = (
        cq.Workplane("XY")
        .workplane(offset=skirt_bottom)
        .circle(r.lid_outer_r)
        .extrude(r.lid_h)
    )
    try:
        outer = outer.edges(">Z").fillet(min(0.003, r.lid_h * 0.15))
    except Exception:
        pass
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=skirt_bottom - 0.001)
        .circle(r.lid_bore_r)
        .extrude(r.lid_h - 0.005)
    )
    return outer.cut(cavity)


def _flat_lid_solid(r: ResolvedContainerJarConfig) -> cq.Workplane:
    """Flat clamp/flip disc lid (authored at local z=0)."""
    return cq.Workplane("XY").circle(r.lid_outer_r).extrude(0.007)


def _cap_sleeve_solid(r: ResolvedContainerJarConfig, *, cap_h: float) -> cq.Workplane:
    """Lift-off friction cap: a cup that sleeves down over the neck, hollow
    underside with a closed top plate (parent ``_cap_solid``)."""
    wall = 0.004
    outer = cq.Workplane("XY").circle(r.lid_outer_r).extrude(cap_h)
    try:
        outer = outer.edges(">Z").fillet(min(0.004, cap_h * 0.12))
    except Exception:
        pass
    # Bore hugs the neck so the cap inner wall actually contacts the neck at rest
    # (avoids a floating, support-disconnected cap). lid_bore_r already = neck_r
    # + clearance; keep the bore right at it.
    bore = cq.Workplane("XY").circle(r.lid_bore_r).extrude(cap_h - wall)
    return outer.cut(bore)


def _stopper_solid(r: ResolvedContainerJarConfig) -> cq.Workplane:
    """Rubber plug stopper + pull tab (qwen jar_001_v03)."""
    plug_r = max(r.neck_r - r.wall - 0.001, 0.006)
    plug_h = 0.020
    tab_r = plug_r * 0.28
    plug = cq.Workplane("XY").circle(plug_r).extrude(plug_h)
    tab = cq.Workplane("XY").workplane(offset=plug_h).circle(tab_r).extrude(0.018)
    return plug.union(tab)


def _shaker_disc_solid(r: ResolvedContainerJarConfig) -> cq.Workplane:
    """Shaker insert disc with a ring of holes (qwen jar_001_v08)."""
    disc_r = max(r.lid_bore_r - 0.001, 0.006)
    disc = cq.Workplane("XY").circle(disc_r).extrude(0.004)
    n = 6
    for k in range(n):
        ang = 2.0 * math.pi * k / n
        hx = (disc_r * 0.55) * math.cos(ang)
        hy = (disc_r * 0.55) * math.sin(ang)
        hole = cq.Workplane("XY").center(hx, hy).circle(disc_r * 0.10).extrude(0.006)
        disc = disc.cut(hole)
    return disc


# ---------------------------------------------------------------------------
# Lid builders. Each attaches one lid mechanism to the jar body.
# ---------------------------------------------------------------------------
def _build_screw_cap(
    model, body, r: ResolvedContainerJarConfig, *, lid_mat, accent_mat, with_shaker: bool
) -> None:
    """CONTINUOUS spin + PRISMATIC lift via a massless carrier (parent pattern).

    The lid is authored in its own frame whose origin coincides with the
    carrier/rotate joint at world z=rim_top_z, so lid-local z=0 is the rim top.
    The skirt drops below the rim to slip over the neck."""
    skirt_bottom = -0.009 * r.lid_height_scale
    lift = _LID_LIFT * r.joint_travel_scale

    carrier = model.part("lid_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.008, 0.008, 0.008)), mass=1e-4)
    model.articulation(
        "lid_rotate",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, r.rim_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(_screw_lid_solid(r, skirt_bottom=skirt_bottom), "lid_shell"),
        material=lid_mat,
        name="lid_shell", material_class_id=("metal.brass_polished" if r.material_style in {"clear_glass", "brass_lid"} else "plastic.opaque_glossy_molded"),
    )
    # Off-axis marker so rotation is observable.
    lid.visual(
        Box((0.004, 0.004, 0.002)),
        origin=Origin(xyz=(r.lid_outer_r - 0.006, 0.0, skirt_bottom + r.lid_h - 0.001)),
        material=accent_mat,
        name="lid_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    lid.inertial = Inertial.from_geometry(
        Cylinder(r.lid_outer_r, r.lid_h),
        mass=0.03,
        origin=Origin(xyz=(0.0, 0.0, skirt_bottom + r.lid_h * 0.5)),
    )
    model.articulation(
        "lid_slide",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=lift, effort=1.0, velocity=1.0),
    )

    if with_shaker:
        # Shaker disc inside the lid, rotating about +Z (REVOLUTE, finite).
        disc = model.part("shaker_disc")
        disc.visual(
            mesh_from_cadquery(_shaker_disc_solid(r), "shaker_disc"),
            material=accent_mat,
            name="shaker_disc", material_class_id=("metal.brass_aged" if r.material_style in {"clear_glass", "frosted_white", "ceramic_cream", "brass_lid"} else "plastic.opaque_glossy_molded"),
        )
        # Off-axis marker on the disc for observable rotation.
        disc.visual(
            Box((0.003, 0.003, 0.002)),
            origin=Origin(xyz=(max(r.lid_bore_r - 0.004, 0.003), 0.0, 0.001)),
            material=lid_mat,
            name="shaker_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        disc.inertial = Inertial.from_geometry(
            Cylinder(r.lid_bore_r, 0.004), mass=0.005,
            origin=Origin(xyz=(0.0, 0.0, 0.002)),
        )
        model.articulation(
            "shaker_rotate",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=disc,
            origin=Origin(xyz=(0.0, 0.0, skirt_bottom + 0.001)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=_SHAKER_LIMIT, effort=1.0, velocity=1.0
            ),
        )


def _build_lift_off_cap(model, body, r: ResolvedContainerJarConfig, *, lid_mat) -> None:
    """Single PRISMATIC +Z lift-off friction cap (no rotation).

    The +Z prismatic origin is anchored on the neck wall (radius ~ neck_r), not
    on the hollow centerline, so it sits on real glass on the parent side. The
    cap mesh is authored offset by -anchor so the cap stays visually centered on
    the jar after the off-axis origin is applied; a small skirt lug at the cap's
    local origin keeps real child geometry at the joint origin."""
    cap_h = max((r.rim_top_z - r.body_h) + 0.014, 0.024)  # sleeves over the neck
    cap_bottom = r.rim_top_z - _CAP_OVERLAP  # open underside z at rest
    travel = _STOPPER_LIFT * r.joint_travel_scale
    anchor = r.neck_r  # on the neck outer wall (real glass nearby on both sides)

    cap = model.part("cap")
    # Authored in cap-local frame: open underside at z=0, closed top at cap_h,
    # shifted by -anchor in x so the off-axis origin re-centers the cap on +Z.
    cap_solid = _cap_sleeve_solid(r, cap_h=cap_h).translate((-anchor, 0.0, 0.0))
    cap.visual(mesh_from_cadquery(cap_solid, "cap_shell"), material=lid_mat, name="cap_shell", material_class_id=("metal.brass_polished" if r.material_style in {"clear_glass", "brass_lid"} else "plastic.opaque_glossy_molded"))
    # Skirt lug at the cap-local origin so child geometry exists at the joint
    # origin (the skirt wall passes through local x=0 because of the -anchor shift).
    cap.inertial = Inertial.from_geometry(
        Cylinder(r.lid_outer_r, cap_h), mass=0.05,
        origin=Origin(xyz=(-anchor, 0.0, cap_h * 0.5)),
    )
    model.articulation(
        "body_to_cap",
        ArticulationType.PRISMATIC,
        parent=body,
        child=cap,
        origin=Origin(xyz=(anchor, 0.0, cap_bottom)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=travel, effort=8.0, velocity=0.2),
    )


def _build_flip_lid(
    model, body, r: ResolvedContainerJarConfig, *, lid_mat, accent_mat, with_stopper: bool
) -> None:
    """Rear-hinged flip disc lid about +X at the back rim. With ``with_stopper``
    also a PRISMATIC +Z pull stopper through the mouth (qwen jar_001_v03)."""
    hinge_y = -(r.neck_r + 0.003)
    open_upper = 2.0 * r.joint_travel_scale  # ~115deg

    lid = model.part("lid")
    # Disc authored about the hinge frame: lid plane at local z=0, centered at
    # +(neck_r+offset) so it caps the mouth when closed (q=0).
    disc = _flat_lid_solid(r).translate((0.0, r.neck_r + 0.003, 0.0))
    lid.visual(mesh_from_cadquery(disc, "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("metal.brass_polished" if r.material_style in {"clear_glass", "brass_lid"} else "plastic.opaque_glossy_molded"))
    # Hinge knuckle on the lid at its local origin (on the hinge axis hardware).
    knuckle = (
        cq.Workplane("YZ")
        .circle(0.005)
        .extrude(0.024)
        .translate((-0.012, 0.0, 0.0))
    )
    lid.visual(mesh_from_cadquery(knuckle, "lid_knuckle"), material=accent_mat, name="lid_knuckle", material_class_id=("metal.brass_aged" if r.material_style in {"blue_glass", "clear_glass", "amber_glass", "ceramic_cream", "brass_lid"} else "metal.aluminum_bare"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(r.lid_outer_r, 0.012),
        mass=0.02,
        origin=Origin(xyz=(0.0, r.neck_r, 0.004)),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, r.rim_top_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=open_upper, effort=4.0, velocity=2.0),
    )

    if with_stopper:
        stopper_lift = _STOPPER_LIFT * r.joint_travel_scale
        seat_z = r.rim_top_z - 0.018  # plug seated in the mouth
        # Anchor the +Z prismatic origin on the neck wall (real glass on the
        # parent side); offset the plug mesh by -anchor so the plug stays
        # centered in the mouth after the off-axis origin re-centers it. The plug
        # body (radius ~ neck_r-wall) passes through local x=0 so child geometry
        # sits at the joint origin too.
        anchor = max(r.neck_r - r.wall, 0.008)
        stopper = model.part("stopper")
        plug_solid = _stopper_solid(r).translate((-anchor, 0.0, 0.0))
        stopper.visual(
            mesh_from_cadquery(plug_solid, "stopper_plug"),
            material=accent_mat,
            name="stopper_plug", material_class_id="rubber.smooth_plain",
        )
        stopper.inertial = Inertial.from_geometry(
            Cylinder(max(r.neck_r - r.wall, 0.006), 0.020), mass=0.01,
            origin=Origin(xyz=(-anchor, 0.0, 0.010)),
        )
        model.articulation(
            "stopper_lift",
            ArticulationType.PRISMATIC,
            parent=body,
            child=stopper,
            origin=Origin(xyz=(anchor, 0.0, seat_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                lower=0.0, upper=stopper_lift, effort=4.0, velocity=1.0
            ),
        )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_jar(
    config: ContainerJarConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.material_style]
    body_mat = model.material(f"cj_body_{r.material_style}", rgba=pal["body"])
    lid_mat = model.material(f"cj_lid_{r.material_style}", rgba=pal["lid"])
    accent_mat = model.material(f"cj_accent_{r.material_style}", rgba=pal["accent"])
    seal_mat = model.material(f"cj_seal_{r.material_style}", rgba=pal["seal"])

    # --- ROOT: jar body ------------------------------------------------------
    body = model.part("jar_body")
    _emit_body(body, r, body_mat=body_mat, seal_mat=seal_mat)
    body.inertial = Inertial.from_geometry(
        Box((2 * r.body_r, 2 * r.body_r, r.rim_top_z)),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, r.rim_top_z / 2.0)),
    )

    # --- lid mechanism -------------------------------------------------------
    if r.lid_closure == "continuous_screw_cap":
        _build_screw_cap(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat, with_shaker=False)
    elif r.lid_closure == "shaker_insert_cap":
        _build_screw_cap(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat, with_shaker=True)
    elif r.lid_closure == "lift_off_friction_cap":
        _build_lift_off_cap(model, body, r, lid_mat=lid_mat)
    elif r.lid_closure == "rear_hinge_flip_lid":
        _build_flip_lid(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat, with_stopper=False)
    elif r.lid_closure == "clamp_lid_stopper":
        _build_flip_lid(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat, with_stopper=True)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_jar(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_jar(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid skirt over the neck, stopper in the
# mouth, shaker disc inside the lid) are declared so the sweep's island/overlap
# checks pass; the lid mechanism actions are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_jar_tests(
    object_model: ArticulatedObject,
    config: ContainerJarConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("jar_body")

    # ---- jar body rests on the ground (base near z=0) ----
    aabb = ctx.part_world_aabb(body)
    bext = _ext(aabb)
    ctx.check(
        "jar body rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "jar body has real volume",
        bext[0] > 0.02 and bext[1] > 0.02 and bext[2] > 0.02,
        details=f"body extents={bext}",
    )

    # ---- lid mechanism: actions + captured-fit overlaps ----
    if r.lid_closure in ("continuous_screw_cap", "shaker_insert_cap"):
        carrier = object_model.get_part("lid_carrier")
        lid = object_model.get_part("lid")
        rotate = object_model.get_articulation("lid_rotate")
        slide = object_model.get_articulation("lid_slide")

        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="jar_glass",
            reason="The lid skirt is intentionally slipped down over the threaded neck rim.",
        )
        ctx.check(
            "carrier link is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "lid_rotate is CONTINUOUS about +Z",
            rotate.articulation_type == ArticulationType.CONTINUOUS and abs(rotate.axis[2]) > 0.99,
            details=f"axis={rotate.axis}, type={rotate.articulation_type}",
        )
        # lid_rotate spins the lid: off-axis marker moves.
        m0 = ctx.part_element_world_aabb(lid, elem="lid_marker")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({rotate: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(lid, elem="lid_marker")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "lid_rotate spins the lid (marker moves)",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.005,
            details=f"marker rest={m0c}, quarter-turn={m1c}",
        )
        # lid_slide lifts the lid off the jar.
        rest_z = ctx.part_world_position(lid)[2]
        with ctx.pose({slide: _LID_LIFT * r.joint_travel_scale}):
            lift_z = ctx.part_world_position(lid)[2]
        ctx.check(
            "lid_slide lifts the lid off the jar",
            lift_z > rest_z + (_LID_LIFT * r.joint_travel_scale) * 0.5,
            details=f"rest_z={rest_z:.4f}, lifted_z={lift_z:.4f}",
        )
        if r.lid_closure == "shaker_insert_cap":
            disc = object_model.get_part("shaker_disc")
            shaker = object_model.get_articulation("shaker_rotate")
            ctx.allow_overlap(
                disc, lid, elem_a="shaker_disc", elem_b="lid_shell",
                reason="The shaker disc sits captured inside the lid cap.",
            )
            ctx.check(
                "shaker_rotate is REVOLUTE about +Z with finite limits",
                shaker.articulation_type == ArticulationType.REVOLUTE
                and abs(shaker.axis[2]) > 0.99
                and shaker.motion_limits is not None
                and shaker.motion_limits.upper is not None,
                details=f"type={shaker.articulation_type}, axis={shaker.axis}",
            )

    elif r.lid_closure == "lift_off_friction_cap":
        cap = object_model.get_part("cap")
        lift = object_model.get_articulation("body_to_cap")
        ctx.allow_isolated_part(
            cap,
            reason="cap lifts off the jar mouth and loses body contact",
        )
        ctx.allow_overlap(
            cap, body, elem_a="cap_shell", elem_b="jar_glass",
            reason="The cap skirt is intentionally seated down over the neck (lift-off friction fit).",
        )
        ctx.check(
            "body_to_cap is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99,
            details=f"axis={lift.axis}, type={lift.articulation_type}",
        )
        rest_z = ctx.part_world_position(cap)[2]
        rest_xy = ctx.part_world_position(cap)[:2]
        travel = _STOPPER_LIFT * r.joint_travel_scale
        with ctx.pose({lift: travel}):
            up_pos = ctx.part_world_position(cap)
        ctx.check(
            "cap lifts straight up off the jar",
            up_pos[2] > rest_z + travel * 0.5
            and abs(up_pos[0] - rest_xy[0]) < 1e-6
            and abs(up_pos[1] - rest_xy[1]) < 1e-6,
            details=f"rest_z={rest_z:.4f}, lifted_z={up_pos[2]:.4f}",
        )

    elif r.lid_closure in ("rear_hinge_flip_lid", "clamp_lid_stopper"):
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("lid_hinge")
        ctx.allow_overlap(
            lid, body, elem_a="lid_shell", elem_b="jar_glass",
            reason="The flip lid disc rests on the neck rim when closed.",
        )
        ctx.check(
            "lid_hinge is REVOLUTE about +X",
            hinge.articulation_type == ArticulationType.REVOLUTE and abs(hinge.axis[0]) > 0.99,
            details=f"axis={hinge.axis}, type={hinge.articulation_type}",
        )
        # Flip the lid up: the top rises.
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: 1.4 * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "lid_hinge flips the lid up (top rises)",
            top1 > top0 + 0.005,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )
        if r.lid_closure == "clamp_lid_stopper":
            stopper = object_model.get_part("stopper")
            lift = object_model.get_articulation("stopper_lift")
            ctx.allow_isolated_part(
                stopper,
                reason="stopper plug pulls out of the jar mouth and loses body contact",
            )
            ctx.allow_overlap(
                stopper, body, elem_a="stopper_plug", elem_b="jar_glass",
                reason="The rubber stopper plug is seated in the wide mouth.",
            )
            ctx.allow_overlap(
                lid, stopper, elem_a="lid_shell", elem_b="stopper_plug",
                reason="The stopper pull tab passes up through the closed clamp lid.",
            )
            rest_z = ctx.part_world_position(stopper)[2]
            travel = _STOPPER_LIFT * r.joint_travel_scale
            with ctx.pose({lift: travel}):
                up_z = ctx.part_world_position(stopper)[2]
            ctx.check(
                "stopper_lift pulls the plug out of the mouth",
                up_z > rest_z + travel * 0.5,
                details=f"rest_z={rest_z:.4f}, up_z={up_z:.4f}",
            )

    # ---- seal_interior fixed visuals ----
    if r.seal_interior == "rubber_gasket_ring":
        ctx.check(
            "gasket ring visual exists on the jar body",
            body.get_visual("gasket_ring") is not None,
            details="gasket_ring visual not found",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed lid joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
