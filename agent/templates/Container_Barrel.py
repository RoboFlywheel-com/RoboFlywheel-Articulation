# SPDX-License-Identifier: Apache-2.0

"""Container barrel — modular procedural template (lidded storage drum / barrel keg).

Category identity: an upright hollow plastic storage drum / ribbed barrel keg. A
thick-walled open-top barrel shell (ROOT) rests on z=0 with its axis along +Z,
clearly **taller than wide**, with molded horizontal stiffening ribs and a
rolled / threaded rim. A lid opens/closes on top by one of several mechanisms
(the main articulation); an optional grip (front buckle clasp or top swing bail)
may hang off the body. No multiplicity axis — one barrel, one lid.

Three parallel slots (spec ``Container_Barrel.md``):

  * ``body_form`` (5) — the ROOT ``barrel_body`` mesh:
      - tall_cylindrical_ribbed (drum parent): CadQuery loft + ``shell`` open-top
        belly + N rib rings + rolled rim lip.
      - bulged_belly_ribbed (keg parent): SDK ``LatheGeometry`` bulged shell
        (closed bottom, hollow, visible mouth) + N rib tori + threaded neck.
      - conical_tapered_body: CadQuery loft, wide base -> narrow top, ribs follow
        the taper.
      - stepped_waisted_body: CadQuery loft, stepped belts + middle waist + N
        recessed vertical panels (inline body visuals).
      - scalloped_lobed_body: hand-written ``MeshGeometry`` with ``cos(N*theta)``
        radius modulation (rounded lobes + channels) + fused rib belts.
  * ``closure`` (3) — the lid mechanism (>=1 non-fixed joint each):
      - lift_off_lid (drum): single PRISMATIC +Z lift-off disc (no rotation).
      - screw_cap (keg): CONTINUOUS spin + PRISMATIC lift via a massless
        ``lid_carrier`` link; default pose lifts the cap so the mouth is visible.
      - flip_top_hinged_lid: REVOLUTE +X flip lid hinged at the rear neck rim
        (body emits hinge lug ears + pin + front latch catch inline).
  * ``grip`` (3, incl. ``no_grip_flat_badge``) — front buckle clasp (FIXED base +
    REVOLUTE swing ring) / top swing bail (REVOLUTE +X over lid, +/-X lugs inline)
    / no grip (flat badge inline body visual).

``rib_count`` [3,16] and ``lobe_count`` [8,14] are body-visual texture N inlined
into the body mesh — NOT slot candidates, NOT structural multiplicity. Continuous
size/proportion variation (height/radius/neck/lid/travel scales) lives in
``resolve_config`` as clamped params.

Sources (articraft_data ``picture/Container/Barrel`` 5-star pool): parents
``4e3a36bf`` (lift-off drum + front clasp), ``b410e9f1`` (screw-cap keg), plus
forks ``flip_top_hinged_lid``, ``conical_tapered_body``, ``clamp_ring_lid``
(stepped waisted), ``side_swing_bail_handles`` (scalloped lobed),
``top_swing_bail_handle``.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Barrel.md``
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
    BoxGeometry,
    Cylinder,
    CylinderGeometry,
    Inertial,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "tall_cylindrical_ribbed",
    "bulged_belly_ribbed",
    "conical_tapered_body",
    "stepped_waisted_body",
    "scalloped_lobed_body",
]
Closure = Literal[
    "lift_off_lid",
    "screw_cap",
    "flip_top_hinged_lid",
]
Grip = Literal[
    "no_grip_flat_badge",
    "swing_buckle_clasp_front",
    "top_swing_bail_handle",
]
PaletteStyle = Literal[
    "industrial_blue_black",
    "keg_blue_black",
    "stepped_two_tone_blue",
    "scalloped_deep_blue",
    "zinc_bail_blue",
    "green_drum_black",
    "food_grade_hdpe_blue",
    "safety_red_drum",
    "galvanized_steel_keg",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "tall_cylindrical_ribbed",
    "bulged_belly_ribbed",
    "conical_tapered_body",
    "stepped_waisted_body",
    "scalloped_lobed_body",
)
CLOSURES: tuple[Closure, ...] = (
    "lift_off_lid",
    "screw_cap",
    "flip_top_hinged_lid",
)
GRIPS: tuple[Grip, ...] = (
    "no_grip_flat_badge",
    "swing_buckle_clasp_front",
    "top_swing_bail_handle",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "industrial_blue_black",
    "keg_blue_black",
    "stepped_two_tone_blue",
    "scalloped_deep_blue",
    "zinc_bail_blue",
    "green_drum_black",
    "food_grade_hdpe_blue",
    "safety_red_drum",
    "galvanized_steel_keg",
)


# ---------------------------------------------------------------------------
# Palette styles: each colorway has body / lid / accent (grip hardware) /
# panel colors plus a ``finish`` descriptor that drives the molded-plastic vs
# painted-steel vs galvanized look. Palette only — never a slot candidate.
# Colors are sourced from the 5-star records' measured materials (6 colorways)
# plus 3 realistic-for-the-class inferred families (green / safety red / zinc).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    finish: str
    body: tuple[float, float, float, float]
    lid: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    panel: tuple[float, float, float, float]


PALETTES: dict[PaletteStyle, _Palette] = {
    "industrial_blue_black": _Palette(
        finish="satin_molded_plastic",
        body=(0.16, 0.36, 0.72, 1.0),
        lid=(0.09, 0.09, 0.10, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        panel=(0.08, 0.20, 0.46, 1.0),
    ),
    "keg_blue_black": _Palette(
        finish="glossy_molded_plastic",
        body=(0.16, 0.34, 0.78, 1.0),
        lid=(0.10, 0.10, 0.11, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        panel=(0.08, 0.20, 0.46, 1.0),
    ),
    "stepped_two_tone_blue": _Palette(
        finish="satin_molded_plastic",
        body=(0.15, 0.34, 0.70, 1.0),
        lid=(0.09, 0.09, 0.10, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        panel=(0.08, 0.20, 0.46, 1.0),
    ),
    "scalloped_deep_blue": _Palette(
        finish="glossy_molded_plastic",
        body=(0.14, 0.32, 0.74, 1.0),
        lid=(0.10, 0.10, 0.11, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        panel=(0.08, 0.20, 0.46, 1.0),
    ),
    "zinc_bail_blue": _Palette(
        finish="satin_molded_plastic",
        body=(0.16, 0.36, 0.72, 1.0),
        lid=(0.09, 0.09, 0.10, 1.0),
        accent=(0.55, 0.55, 0.52, 1.0),
        panel=(0.08, 0.20, 0.46, 1.0),
    ),
    "green_drum_black": _Palette(
        finish="matte_molded_plastic",
        body=(0.18, 0.45, 0.24, 1.0),
        lid=(0.09, 0.09, 0.10, 1.0),
        accent=(0.12, 0.12, 0.13, 1.0),
        panel=(0.10, 0.28, 0.14, 1.0),
    ),
    "food_grade_hdpe_blue": _Palette(
        finish="food_grade_hdpe",
        body=(0.20, 0.42, 0.78, 1.0),
        lid=(0.90, 0.90, 0.88, 1.0),
        accent=(0.16, 0.34, 0.70, 1.0),
        panel=(0.12, 0.26, 0.52, 1.0),
    ),
    "safety_red_drum": _Palette(
        finish="painted_steel_drum",
        body=(0.62, 0.13, 0.11, 1.0),
        lid=(0.55, 0.11, 0.10, 1.0),
        accent=(0.55, 0.55, 0.52, 1.0),
        panel=(0.42, 0.10, 0.09, 1.0),
    ),
    "galvanized_steel_keg": _Palette(
        finish="galvanized_steel",
        body=(0.66, 0.67, 0.64, 1.0),
        lid=(0.58, 0.59, 0.57, 1.0),
        accent=(0.55, 0.55, 0.52, 1.0),
        panel=(0.50, 0.51, 0.49, 1.0),
    ),
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ContainerBarrelConfig:
    body_form: BodyForm = "tall_cylindrical_ribbed"
    closure: Closure = "lift_off_lid"
    grip: Grip = "no_grip_flat_badge"
    palette_style: PaletteStyle = "industrial_blue_black"
    rib_count: int = 7
    lobe_count: int = 10
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    lid_height_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_barrel"


@dataclass(frozen=True)
class ResolvedContainerBarrelConfig:
    body_form: BodyForm
    closure: Closure
    grip: Grip
    palette_style: PaletteStyle
    rib_count: int
    lobe_count: int
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    lid_height_scale: float
    joint_travel_scale: float
    # derived geometry (world meters)
    barrel_h: float  # overall barrel height (rim top z)
    body_max_r: float  # widest outer radius (belly / base)
    rim_r: float  # outer radius of the rim / top lip
    neck_r: float  # outer radius of the screw / hinge neck
    mouth_r: float  # visible open mouth radius
    rim_z: float  # z of the lid mount plane (rim top)
    lid_bore_r: float  # cap inner skirt radius (grips the neck)
    lid_outer_r: float  # cap / lid outer radius
    lid_h: float  # lid / cap thickness band
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _clampi(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Per-body-form nominal geometry. ``base_*`` are the source-record literals;
# resolve scales them. Each form has a different intrinsic scale & rim/neck
# vocabulary, so the closure / grip mounts derive from these (NOT a constant).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _FormBase:
    barrel_h: float
    body_max_r: float
    rim_r: float
    neck_r: float
    mouth_r: float


_FORM_BASES: dict[BodyForm, _FormBase] = {
    # drum parent: BARREL_H 0.35, belly 0.125, top rim 0.115.
    "tall_cylindrical_ribbed": _FormBase(0.35, 0.125, 0.115, 0.104, 0.092),
    # keg parent: lathe, top 0.270, belly 0.110, neck 0.070, mouth 0.055.
    "bulged_belly_ribbed": _FormBase(0.27, 0.112, 0.082, 0.070, 0.055),
    # conical: BARREL_H 0.35, base 0.145, top 0.105.
    "conical_tapered_body": _FormBase(0.35, 0.145, 0.105, 0.095, 0.082),
    # stepped waisted: BARREL_H 0.35, base 0.136, top 0.108.
    "stepped_waisted_body": _FormBase(0.35, 0.139, 0.108, 0.097, 0.084),
    # scalloped lobed: lathe-like mesh, top 0.270, belly 0.124, neck 0.070.
    "scalloped_lobed_body": _FormBase(0.27, 0.124, 0.082, 0.070, 0.055),
}


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def _weighted_rib_count(rng: random.Random) -> int:
    """rib_count weighted small (N in [4,8] ~70%, N in [9,16] ~30%)."""
    if rng.random() < 0.70:
        return rng.randint(4, 8)
    return rng.randint(9, 16)


def _weighted_lobe_count(rng: random.Random) -> int:
    """lobe_count weighted (N in [8,12] high, N in [13,14] rare)."""
    if rng.random() < 0.80:
        return rng.randint(8, 12)
    return rng.randint(13, 14)


def config_from_seed(seed: int) -> ContainerBarrelConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    closure = rng.choice(CLOSURES)
    grip = rng.choice(GRIPS)
    palette_style = rng.choice(PALETTE_STYLES)
    rib_count = _weighted_rib_count(rng)
    lobe_count = _weighted_lobe_count(rng)
    return ContainerBarrelConfig(
        body_form=body_form,
        closure=closure,
        grip=grip,
        palette_style=palette_style,
        rib_count=rib_count,
        lobe_count=lobe_count,
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.90, 1.10), 4),
        lid_height_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_barrel_{seed}",
    )


def resolve_config(
    config: ContainerBarrelConfig | None = None,
) -> ResolvedContainerBarrelConfig:
    cfg = config or ContainerBarrelConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    closure = _pick(cfg.closure, CLOSURES)
    grip = _pick(cfg.grip, GRIPS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    base = _FORM_BASES[body_form]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.90, 1.10)
    lh_scale = _clamp(cfg.lid_height_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    rib_count = _clampi(cfg.rib_count, 3, 16)
    lobe_count = _clampi(cfg.lobe_count, 8, 14)

    barrel_h = base.barrel_h * h_scale
    body_max_r = base.body_max_r * r_scale
    rim_r = base.rim_r * r_scale
    # Neck radius follows body radius * its own scale, clamped strictly inside
    # the rim so the rim lip and lid skirt still wrap it (equation axis).
    neck_r = _clamp(base.neck_r * r_scale * n_scale, 0.030, rim_r - 0.004)
    mouth_r = _clamp(base.mouth_r * r_scale, 0.020, neck_r - 0.004)

    # Taller-than-wide identity inequality: barrel_h must clearly exceed the
    # belly diameter. If a large radius_scale + small height_scale would break
    # it, project barrel_h up so the category identity holds.
    min_h = 2.0 * body_max_r + 0.06
    if barrel_h < min_h:
        barrel_h = min_h

    rim_z = barrel_h

    # Lid cover-fit equations: the cap skirt bore grips the neck; the lid outer
    # is proud of the rim so it actually wraps it.
    lid_bore_r = neck_r + 0.004
    lid_outer_r = max(rim_r + 0.006, lid_bore_r + 0.006)
    lid_h = 0.030 * lh_scale

    return ResolvedContainerBarrelConfig(
        body_form=body_form,
        closure=closure,
        grip=grip,
        palette_style=palette_style,
        rib_count=rib_count,
        lobe_count=lobe_count,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=n_scale,
        lid_height_scale=lh_scale,
        joint_travel_scale=jt_scale,
        barrel_h=barrel_h,
        body_max_r=body_max_r,
        rim_r=rim_r,
        neck_r=neck_r,
        mouth_r=mouth_r,
        rim_z=rim_z,
        lid_bore_r=lid_bore_r,
        lid_outer_r=lid_outer_r,
        lid_h=lid_h,
        name=cfg.name or "container_barrel",
    )


def with_overrides(config: ContainerBarrelConfig, **kwargs: object) -> ContainerBarrelConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerBarrelConfig | ResolvedContainerBarrelConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerBarrelConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("closure", r.closure),
        ("grip", r.grip),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Body surface radius helpers (front +Y wall radius at a given z). Used to seat
# the front buckle clasp on whichever body form is chosen.
# ---------------------------------------------------------------------------
def _surface_r(r: ResolvedContainerBarrelConfig, z: float) -> float:
    """Outer radius of the body wall at height ``z`` (0..rim_z).

    For the three CadQuery-loft forms (drum / conical / stepped) this evaluates
    the SAME (z, r) section list the body mesh is revolved from, so hardware
    (front clasp, badge, bail lugs) seats exactly on the real wall rather than
    on a rough constant — the stepped waist in particular dips well inside
    ``body_max_r`` and a constant estimate left the clasp floating off the wall.
    """
    if r.body_form == "tall_cylindrical_ribbed":
        return _profile_r_from_sections(_drum_sections(r), z)
    if r.body_form == "conical_tapered_body":
        return _profile_r_from_sections(_conical_sections(r), z)
    if r.body_form == "stepped_waisted_body":
        return _profile_r_from_sections(_stepped_sections(r), z)
    t = _clamp(z / max(r.rim_z, 1e-6), 0.0, 1.0)
    if r.body_form in ("bulged_belly_ribbed", "scalloped_lobed_body"):
        # Lathe/scalloped keg: belly through the body, then a short shoulder that
        # tapers from the belly down to the neck radius at the very top.
        if t < 0.80:
            return r.body_max_r * 0.96
        if t >= 0.944:
            return r.neck_r
        # shoulder: belly -> neck across t in [0.80, 0.944]
        f = (t - 0.80) / (0.944 - 0.80)
        return r.body_max_r * 0.96 + (r.neck_r - r.body_max_r * 0.96) * f
    # drum: near-straight belly tapering to the rim in the top fifth.
    if t < 0.80:
        return r.body_max_r * 0.96
    return r.rim_r


# ---------------------------------------------------------------------------
# Slot A: body geometry. Each form returns its barrel mesh; rib_count /
# lobe_count are inlined into the mesh (body-visual texture N, no extra joints).
# ---------------------------------------------------------------------------
def _profile_r_from_sections(sections, z: float) -> float:
    """Linear-interpolate the loft outer radius at height ``z`` from sections."""
    if z <= sections[0][0]:
        return sections[0][1]
    if z >= sections[-1][0]:
        return sections[-1][1]
    for (z0, r0), (z1, r1) in zip(sections, sections[1:]):
        if z0 <= z <= z1:
            t = (z - z0) / (z1 - z0) if z1 > z0 else 0.0
            return r0 + (r1 - r0) * t
    return sections[-1][1]


def _merge_rib_tori(
    geom: MeshGeometry,
    r: ResolvedContainerBarrelConfig,
    sections,
) -> None:
    """Merge N horizontal stiffening rib tori into the (already tessellated)
    body mesh. rib_count drives the count (body-visual texture N). Each torus
    radius follows the local loft profile so it sits proud of and fuses to the
    wall. Merging tori avoids the expensive CadQuery booleans that hang at high N.
    """
    n = r.rib_count
    z0 = 0.20 * r.rim_z
    z1 = 0.80 * r.rim_z
    for i in range(n):
        frac = (i + 0.5) / n
        z = z0 + (z1 - z0) * frac
        # Seat the rib center ~2.5mm inward of the wall surface so the tube
        # straddles and solidly interpenetrates the shell (never grazes -> no
        # disconnected island), while still standing proud on the outside.
        local_r = _profile_r_from_sections(sections, z) - 0.0025
        rib = TorusGeometry(local_r, 0.0085, radial_segments=10, tubular_segments=48)
        rib.translate(0.0, 0.0, z)
        geom.merge(rib)


def _drum_sections(r: ResolvedContainerBarrelConfig):
    bmr, h = r.body_max_r, r.rim_z
    return [
        (0.000, bmr * 0.93),
        (0.012 * h / 0.35, bmr * 0.976),
        (0.060 * h / 0.35, bmr),
        (0.500 * h, bmr * 0.992),
        (0.857 * h, bmr * 0.952),
        (0.943 * h, bmr * 0.936),
        (h, r.rim_r),
    ]


def _conical_sections(r: ResolvedContainerBarrelConfig):
    bmr, h = r.body_max_r, r.rim_z

    def taper_r(z: float) -> float:
        t = _clamp(z / h, 0.0, 1.0)
        return bmr + (r.rim_r - bmr) * t

    return [
        (0.000, bmr),
        (0.012 * h / 0.35, bmr + 0.003),
        (0.500 * h, taper_r(0.500 * h)),
        (h, r.rim_r),
    ]


def _stepped_sections(r: ResolvedContainerBarrelConfig):
    bmr, h = r.body_max_r, r.rim_z
    waist = bmr * 0.80
    return [
        (0.000, bmr * 0.89),
        (0.051 * h, bmr * 0.978),
        (0.157 * h, bmr * 0.906),
        (0.249 * h, waist),  # recessed waist
        (0.343 * h, bmr * 0.885),
        (0.471 * h, bmr * 0.863),
        (0.857 * h, bmr * 0.864),
        (0.943 * h, r.rim_r + 0.006),
        (h, r.rim_r),
    ]


def _loft_body_mesh(r: ResolvedContainerBarrelConfig, sections) -> MeshGeometry:
    """Build an open-top hollow barrel shell by revolving the (z, r) outer
    profile (and a wall-shrunk inner profile) into a ``LatheGeometry``, then
    merge N rib tori + the rolled rim lip.

    These are surfaces of revolution (circular cross-sections), so a revolved
    profile mesh is faithful to the source loft+shell geometry (same intent as
    the keg parent's LatheGeometry) while tessellating instantly — the OCCT
    BSpline loft tessellation hangs on near-cylindrical profiles at high rib N.
    """
    wall = 0.012
    h = r.rim_z
    rim_top = h
    # Outer profile bottom -> rim, with a closed base and inner return wall down
    # to a thick floor, leaving a real open-top hollow cavity + visible mouth.
    outer_pts: list[tuple[float, float]] = [(0.0, 0.0)]
    for z, rad in sections:
        outer_pts.append((max(rad, 0.005), z))
    # Inner return: from the rim mouth back down the inner wall to the floor.
    floor_z = max(0.012, wall)
    inner_pts: list[tuple[float, float]] = []
    mouth_r = max(r.mouth_r, r.rim_r - wall - 0.004)
    inner_pts.append((mouth_r, rim_top))
    for z, rad in reversed(sections):
        if z <= floor_z:
            continue
        inner_pts.append((max(rad - wall, 0.01), z))
    inner_pts.append((max(sections[0][1] - wall, 0.01), floor_z))
    inner_pts.append((0.0, floor_z))
    geom = LatheGeometry(outer_pts + inner_pts, segments=64, closed=True)
    _merge_rib_tori(geom, r, sections)
    # Rolled rim lip as a torus proud of the rim (the lid seats over it). Seat
    # its center radius ON the local wall profile (a few mm in from the surface)
    # so the tube straddles the shell wall and solidly interpenetrates it — a
    # lip pinned exactly at the rim edge radius only grazes the wall and reads
    # as a disconnected geometry island after export rounding.
    lip_z = rim_top - 0.010
    lip_r = _profile_r_from_sections(sections, lip_z) - 0.003
    lip = TorusGeometry(lip_r, 0.009, radial_segments=10, tubular_segments=48)
    lip.translate(0.0, 0.0, lip_z)
    geom.merge(lip)
    return geom


def _lathe_body_mesh(r: ResolvedContainerBarrelConfig) -> MeshGeometry:
    """bulged_belly_ribbed (keg): revolved bulged shell + N rib tori + threads."""
    bmr = r.body_max_r
    h = r.rim_z
    neck = r.neck_r
    mouth = r.mouth_r
    floor_z = 0.012 * h / 0.27
    # Outer profile bottom->neck (radii scaled by body_max_r ratio).
    outer = [
        (0.000, 0.000),
        (bmr * 0.80, 0.000),
        (bmr * 0.875, 0.022 * h),
        (bmr * 0.938, 0.111 * h),
        (bmr, 0.407 * h),  # belly
        (bmr * 0.982, 0.593 * h),
        (bmr * 0.875, 0.796 * h),
        (bmr * 0.732, 0.907 * h),  # shoulder
        (neck, 0.944 * h),  # top of body, meeting neck
        (neck, h),
    ]
    inner = [
        (mouth, h),  # open mouth
        (mouth + 0.005, 0.944 * h),
        (bmr * 0.66, 0.907 * h),
        (bmr * 0.80, 0.796 * h),
        (bmr * 0.893, 0.593 * h),
        (bmr * 0.911, 0.407 * h),
        (bmr * 0.866, 0.130 * h),
        (bmr * 0.804, 0.067 * h),
        (bmr * 0.732, floor_z),
        (0.000, floor_z),
    ]
    body = LatheGeometry(outer + inner, segments=64, closed=True)

    # Horizontal rib tori (rib_count). Place along the belly band, radius
    # following the bulge so they sit proud.
    n = r.rib_count
    z0 = 0.13 * h
    z1 = 0.82 * h
    for i in range(n):
        frac = (i + 0.5) / n
        z = z0 + (z1 - z0) * frac
        # belly bulge shape: widest mid-body.
        bulge = bmr * (0.94 + 0.06 * math.sin(math.pi * frac))
        rib = TorusGeometry(bulge - 0.004, 0.009, radial_segments=12, tubular_segments=64)
        rib.translate(0.0, 0.0, z)
        body.merge(rib)
    # Threaded neck rings around the mouth. Center the tube ON the neck wall
    # radius with a fat (6mm) tube so it straddles the thin neck shell from both
    # sides and solidly interpenetrates it (a ring offset inside/outside the thin
    # wall only grazes it and exports as a floating geometry island).
    for tz in (0.933 * h, 0.970 * h, 1.007 * h):
        thread = TorusGeometry(neck, 0.006, radial_segments=10, tubular_segments=48)
        thread.translate(0.0, 0.0, tz)
        body.merge(thread)
    return body


def _scalloped_body_mesh(r: ResolvedContainerBarrelConfig) -> MeshGeometry:
    """scalloped_lobed_body: cos(N*theta) radius-modulated one-piece shell."""
    h = r.rim_z
    bmr = r.body_max_r
    neck = r.neck_r
    mouth = r.mouth_r
    floor_z = 0.012 * h / 0.27
    lobe_count = r.lobe_count
    segments = 96
    barrel_top = 0.944 * h

    def smoothstep(e0: float, e1: float, x: float) -> float:
        if e0 == e1:
            return 0.0
        t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
        return t * t * (3.0 - 2.0 * t)

    def profile_radius(z: float) -> float:
        f = z / h
        if f <= 0.111:
            return bmr * (0.677 + (0.823 - 0.677) * smoothstep(0.0, 0.111, f))
        if f <= 0.426:
            return bmr * (0.823 + (0.935 - 0.823) * smoothstep(0.111, 0.426, f))
        if f <= 0.611:
            return bmr * (0.935 + (0.952 - 0.935) * smoothstep(0.426, 0.611, f))
        if f <= 0.870:
            return bmr * (0.952 + (0.702 - 0.952) * smoothstep(0.611, 0.870, f))
        if f <= barrel_top / h:
            return bmr * (0.702 + (neck / bmr - 0.702) * smoothstep(0.870, barrel_top / h, f))
        return neck

    def rib_bump(z: float) -> float:
        # Fused horizontal belts integrated into the radius (rib_count count).
        bump = 0.0
        n = r.rib_count
        z0 = 0.13 * h
        z1 = 0.82 * h
        for i in range(n):
            center = z0 + (z1 - z0) * (i + 0.5) / n
            bump += 0.007 * math.exp(-(((z - center) / 0.010) ** 2))
        return bump

    def lobe_amp(z: float) -> float:
        envelope = smoothstep(0.13 * h, 0.30 * h, z) * (1.0 - smoothstep(0.807 * h, 0.933 * h, z))
        return 0.010 * envelope

    def outer_radius(z: float, theta: float) -> float:
        lobes = math.cos(lobe_count * theta)
        scallop = 0.70 * lobes + 0.30 * math.cos(2.0 * lobe_count * theta)
        return profile_radius(z) + rib_bump(z) + lobe_amp(z) * scallop

    def inner_radius(z: float) -> float:
        if z >= barrel_top:
            return mouth
        return max(mouth, profile_radius(z) - 0.020)

    geom = MeshGeometry()
    outer_z = [
        f * h
        for f in (
            0.0,
            0.044,
            0.093,
            0.167,
            0.241,
            0.315,
            0.389,
            0.463,
            0.537,
            0.611,
            0.685,
            0.759,
            0.833,
            0.896,
            0.944,
            1.0,
        )
    ]
    outer_rings: list[list[int]] = []
    for z in outer_z:
        ring = []
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            rad = outer_radius(z, theta)
            ring.append(geom.add_vertex(rad * math.cos(theta), rad * math.sin(theta), z))
        outer_rings.append(ring)
    for a, b in zip(outer_rings, outer_rings[1:]):
        for i in range(segments):
            j = (i + 1) % segments
            geom.add_face(a[i], a[j], b[j])
            geom.add_face(a[i], b[j], b[i])

    bottom_center = geom.add_vertex(0.0, 0.0, 0.0)
    for i in range(segments):
        j = (i + 1) % segments
        geom.add_face(bottom_center, outer_rings[0][j], outer_rings[0][i])

    inner_z = [floor_z, 0.167 * h, 0.315 * h, 0.463 * h, 0.611 * h, 0.759 * h, barrel_top, h]
    inner_rings: list[list[int]] = []
    for z in inner_z:
        ring = []
        for i in range(segments):
            theta = 2.0 * math.pi * i / segments
            rad = inner_radius(z)
            ring.append(geom.add_vertex(rad * math.cos(theta), rad * math.sin(theta), z))
        inner_rings.append(ring)
    for a, b in zip(inner_rings, inner_rings[1:]):
        for i in range(segments):
            j = (i + 1) % segments
            geom.add_face(a[i], b[j], a[j])
            geom.add_face(a[i], b[i], b[j])

    floor_center = geom.add_vertex(0.0, 0.0, floor_z)
    for i in range(segments):
        j = (i + 1) % segments
        geom.add_face(floor_center, inner_rings[0][i], inner_rings[0][j])

    outer_top = outer_rings[-1]
    inner_top = inner_rings[-1]
    for i in range(segments):
        j = (i + 1) % segments
        geom.add_face(outer_top[i], inner_top[j], outer_top[j])
        geom.add_face(outer_top[i], inner_top[i], inner_top[j])

    # Integrated thread cue near the mouth. Center the tube ON the neck wall
    # radius with a fat (6mm) tube so it straddles the thin neck shell from both
    # sides and solidly interpenetrates it (a ring offset inside/outside the thin
    # wall only grazes it and exports as a floating geometry island).
    for tz in (0.933 * h, 0.970 * h, 1.007 * h):
        thread = TorusGeometry(neck, 0.006, radial_segments=10, tubular_segments=48)
        thread.translate(0.0, 0.0, tz)
        geom.merge(thread)
    return geom


# ---------------------------------------------------------------------------
# flip closure: body must emit hinge lug ears + pin + front latch (inline).
# These are CadQuery-friendly only for lathe forms; for loft forms we add them
# as primitive mesh visuals on the same part.
# ---------------------------------------------------------------------------
def _hinge_radius(r: ResolvedContainerBarrelConfig) -> float:
    """Radius the flip-top hinge frame + lid mount sits at. The hinge pin must
    bridge the rear body WALL, not the (smaller) neck radius: on the loft forms
    (drum / conical / stepped) the top wall is at ~rim_r, well outside neck_r, so
    a frame pinned at neck_r floats in the cavity. Use the real body surface just
    below the rim, never smaller than neck_r so the lid still clears the mouth."""
    surf = _surface_r(r, r.rim_z - 0.010)
    return max(r.neck_r, surf - 0.004)


def _hinge_hardware_geom(r: ResolvedContainerBarrelConfig) -> MeshGeometry:
    """Rear hinge lug ears + pin + front latch catch, merged into one mesh. All
    pieces are seated at the real body-wall radius (``_hinge_radius``) so each
    one solidly touches the barrel shell (no floating latch island)."""
    hr = _hinge_radius(r)
    rim_z = r.rim_z
    hinge_y = -hr
    ear_h = 0.014
    ear_w = 0.016
    ear_thick = 0.006
    hinge_len = min(0.036, 1.4 * hr)
    ear_z = rim_z - ear_h / 2.0
    geom = MeshGeometry()
    half = hinge_len / 2.0
    for x_off in (-half + ear_thick / 2, half - ear_thick / 2):
        ear = BoxGeometry((ear_thick, ear_w, ear_h))
        # Ear inner face bites into the wall (starts ~6mm inside the surface).
        ear.translate(x_off, hinge_y + ear_w / 2.0 - 0.006, ear_z)
        geom.merge(ear)
    pin = CylinderGeometry(0.004, hinge_len, radial_segments=16)
    pin.rotate_y(math.pi / 2.0)
    pin.translate(0.0, hinge_y, rim_z - 0.002)
    geom.merge(pin)
    # Front latch catch straddling the +Y body wall (deep enough to bite it).
    latch = BoxGeometry((0.014, 0.014, 0.012))
    latch.translate(0.0, hr - 0.004, rim_z - 0.008)
    geom.merge(latch)
    return geom


# ---------------------------------------------------------------------------
# Grip inline body visuals: bail lug bosses (top bail), flat badge (no grip).
# ---------------------------------------------------------------------------
def _bail_lug_z(r: ResolvedContainerBarrelConfig) -> float:
    """Z of the +/-X bail pivot lug center. Seated on the upper belly, but kept
    far enough below the rim that the 34mm-tall boss clears any depending lid
    skirt (the lift-off lid skirt hangs ~28mm below the rim and, on the narrow
    keg neck, would otherwise collide with the lug boss)."""
    base = r.rim_z - 0.044 * (r.rim_z / 0.35)
    # The lift-off lid skirt bottom is rim_z - 0.006 - 0.022*lid_height_scale;
    # keep the lug top (= lug_z + 0.017) at least 4mm below that.
    skirt_bottom = r.rim_z - 0.006 - 0.022 * r.lid_height_scale
    lug_top_cap = skirt_bottom - 0.004 - 0.017
    return min(base, lug_top_cap)


def _bail_span(r: ResolvedContainerBarrelConfig) -> float:
    """Pivot-hole X distance: just outside the *widest* body radius so the bail
    legs hang clear of the whole barrel shell at rest (avoids leg-in-wall
    overlap as the legs descend past the belly)."""
    return r.body_max_r + 0.016


def _bail_lug_geom(r: ResolvedContainerBarrelConfig, sign: int, lug_z: float) -> MeshGeometry:
    """One molded bail lug boss on the +/-X side (mesh box, no CadQuery boolean).

    The boss straddles the wall: its inner face overlaps the shell (connectivity)
    and its outer face reaches past the bail pivot span so the bore midpoint
    (= bail_swing origin x = span) is well inside the boss."""
    span = _bail_span(r)
    surf = _surface_r(r, lug_z)
    lug_hgt = 0.034
    lug_d = 0.026
    # Inner face bites into the wall. On the scalloped form the cos(N*theta)
    # modulation pulls the wall up to ~10mm inward at a lobe valley (and an odd
    # lobe_count makes the -X and +X sides differ), so embed deeper there to
    # guarantee the lug overlaps the shell on whichever side it lands.
    embed = 0.020 if r.body_form == "scalloped_lobed_body" else 0.008
    inner_x = surf - embed
    outer_x = span + 0.012
    lug_w = outer_x - inner_x
    cx = sign * ((inner_x + outer_x) / 2.0)
    boss = BoxGeometry((lug_w, lug_d, lug_hgt))
    boss.translate(cx, 0.0, lug_z)
    return boss


# ---------------------------------------------------------------------------
# Body emit (ROOT). Returns nothing; attaches the barrel_shell visual(s).
# ---------------------------------------------------------------------------
def _emit_body(
    body,
    r: ResolvedContainerBarrelConfig,
    *,
    body_mat,
    panel_mat,
    accent_mat,
) -> None:
    form = r.body_form
    if form == "tall_cylindrical_ribbed":
        geom = _loft_body_mesh(r, _drum_sections(r))
        body.visual(
            mesh_from_geometry(geom, "barrel_shell"), material=body_mat, name="barrel_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
        )
    elif form == "conical_tapered_body":
        geom = _loft_body_mesh(r, _conical_sections(r))
        body.visual(
            mesh_from_geometry(geom, "barrel_shell"), material=body_mat, name="barrel_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
        )
    elif form == "stepped_waisted_body":
        geom = _loft_body_mesh(r, _stepped_sections(r))
        body.visual(
            mesh_from_geometry(geom, "barrel_shell"), material=body_mat, name="barrel_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
        )
        # Dark recessed vertical panels (inline body visuals, ring-replicated).
        panel_count = 8
        panel_geom = BoxGeometry((0.010, 0.004, 0.150 * (r.rim_z / 0.35)))
        panel_r = r.body_max_r * 0.82 + 0.004
        for i in range(panel_count):
            a = 2.0 * math.pi * i / panel_count
            body.visual(
                mesh_from_geometry(panel_geom, f"recessed_panel_{i}_mesh"),
                material=panel_mat,
                name=f"recessed_panel_{i}", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated"),
                origin=Origin(
                    xyz=(math.cos(a) * panel_r, math.sin(a) * panel_r, 0.50 * r.rim_z),
                    rpy=(0.0, 0.0, a),
                ),
            )
    elif form == "bulged_belly_ribbed":
        geom = _lathe_body_mesh(r)
        body.visual(
            mesh_from_geometry(geom, "barrel_shell"), material=body_mat, name="barrel_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
        )
    elif form == "scalloped_lobed_body":
        geom = _scalloped_body_mesh(r)
        body.visual(
            mesh_from_geometry(geom, "barrel_shell"), material=body_mat, name="barrel_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
        )

    # Flip closure needs hinge hardware inline on the body.
    if r.closure == "flip_top_hinged_lid":
        body.visual(
            mesh_from_geometry(_hinge_hardware_geom(r), "hinge_hardware"),
            material=accent_mat,
            name="hinge_hardware", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.steel_galvanized"),
        )

    # Grip-dependent inline body visuals.
    if r.grip == "top_swing_bail_handle":
        lug_z = _bail_lug_z(r)
        for i in range(2):
            sign = -1 if i == 0 else 1
            body.visual(
                mesh_from_geometry(_bail_lug_geom(r, sign, lug_z), f"lug_{i}_mesh"),
                material=body_mat,
                name=f"lug_{i}", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated"),
            )
    elif r.grip == "no_grip_flat_badge":
        # Flat front badge / label plate fused onto the +Y belly wall.
        badge_z = 0.50 * r.rim_z
        front_r = _surface_r(r, badge_z)
        badge = BoxGeometry((0.06, 0.004, 0.045))
        badge.translate(0.0, front_r - 0.001, badge_z)
        body.visual(
            mesh_from_geometry(badge, "front_badge"),
            material=accent_mat,
            name="front_badge", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated"),
        )

    body.inertial = Inertial.from_geometry(
        Cylinder(radius=r.body_max_r, length=r.rim_z),
        mass=2.4,
        origin=Origin(xyz=(0.0, 0.0, r.rim_z / 2.0)),
    )


# ---------------------------------------------------------------------------
# Slot B: closure builders. Each parents the lid mechanism to the body at the
# rim. The lid joint origin sits on the rim hardware (rim top / rear neck).
# ---------------------------------------------------------------------------
def _lift_off_lid_solid(r: ResolvedContainerBarrelConfig) -> cq.Workplane:
    """Domed disc + depending skirt that caps the rim from outside.

    Authored so local z=0 is the disc underside (rests on the rim)."""
    outer = r.lid_outer_r
    disc = (
        cq.Workplane("XY")
        .circle(outer)
        .extrude(0.012)
        .faces(">Z")
        .workplane()
        .circle(outer)
        .workplane(offset=0.006)
        .circle(outer * 0.72)
        .loft(ruled=False)
    )
    skirt = (
        cq.Workplane("XY")
        .workplane(offset=-0.022 * r.lid_height_scale)
        .circle(outer + 0.005)
        .circle(outer - 0.001)
        .extrude(0.030 * r.lid_height_scale)
    )
    return disc.union(skirt)


def _build_lift_off_lid(
    model, body, r: ResolvedContainerBarrelConfig, *, lid_mat, accent_mat
) -> None:
    """Single PRISMATIC +Z lift-off disc. q=0 seats on the rim; +q lifts off.

    The prismatic origin is anchored on the rolled rim lip ring (+Y side) so the
    joint origin lies on real body geometry (a wide open mouth puts the
    centerline >15mm from the rim ring). The lid mesh is authored offset by
    -anchor in Y so the disc re-centers on the barrel axis after the off-axis
    origin; the lid disc still spans the local origin (outer radius > anchor),
    so child geometry sits at the joint origin too. PRISMATIC +Z translation is
    unaffected by the tangential origin offset."""
    lid_z = r.rim_z - 0.006
    travel = 0.05 * r.joint_travel_scale
    # Anchor on the body's actual top outer wall (+Y side) so the joint origin
    # lies on real geometry for every body form (loft rim lip ~rim_r, but the
    # scalloped/keg forms taper to the neck radius at the top).
    anchor = min(r.rim_r, _surface_r(r, lid_z))

    lid = model.part("lid")
    lid_solid = _lift_off_lid_solid(r).translate((0.0, -anchor, 0.0))
    lid.visual(mesh_from_cadquery(lid_solid, "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated"))
    boss = CylinderGeometry(0.024, 0.012).translate(0.0, -anchor, 0.024)
    lid.visual(mesh_from_geometry(boss, "lid_boss"), material=accent_mat, name="lid_boss", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=r.lid_outer_r, length=0.04),
        mass=0.30,
        origin=Origin(xyz=(0.0, -anchor, 0.0)),
    )
    model.articulation(
        "lid_lift",
        ArticulationType.PRISMATIC,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, anchor, lid_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.2, lower=0.0, upper=travel),
    )


def _screw_cap_geom(r: ResolvedContainerBarrelConfig) -> MeshGeometry:
    """Knurled screw cap. Authored local z=0 at the cap underside."""
    outer = r.lid_outer_r
    cap_h = r.lid_h
    cap = CylinderGeometry(outer, cap_h, radial_segments=48)
    cap.translate(0.0, 0.0, cap_h / 2.0)
    n = 28
    for k in range(n):
        a = 2.0 * math.pi * k / n
        ridge = CylinderGeometry(0.0035, cap_h * 0.85, radial_segments=6)
        ridge.translate(outer, 0.0, cap_h / 2.0)
        ridge.rotate_z(a)
        cap.merge(ridge)
    rim = TorusGeometry(outer - 0.006, 0.006, radial_segments=10, tubular_segments=48)
    rim.translate(0.0, 0.0, cap_h)
    cap.merge(rim)
    # Skirt grips the neck (a short downward ring below z=0).
    skirt = CylinderGeometry(outer * 0.92, 0.014, radial_segments=48)
    skirt.translate(0.0, 0.0, -0.007)
    cap.merge(skirt)
    return cap


def _build_screw_cap(model, body, r: ResolvedContainerBarrelConfig, *, lid_mat, accent_mat) -> None:
    """CONTINUOUS spin + PRISMATIC lift via a massless carrier (keg pattern).

    Default pose lifts the cap a clearance so the open mouth is visible."""
    rest_clearance = 0.040 * r.joint_travel_scale
    lift_extra = r.lid_h

    carrier = model.part("lid_carrier")  # NO visuals
    carrier.inertial = Inertial.from_geometry(Box((0.01, 0.01, 0.01)), mass=1e-4)
    model.articulation(
        "lid_rotate",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, r.rim_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    lid = model.part("lid")
    lid.visual(
        mesh_from_geometry(_screw_cap_geom(r), "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
    )
    # Off-axis molded key so rotation is observable.
    lid.visual(
        Box((0.012, 0.018, 0.012)),
        origin=Origin(xyz=(r.lid_outer_r - 0.010, 0.0, r.lid_h + 0.004)),
        material=accent_mat,
        name="lid_molded_key", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated"),
    )
    lid.inertial = Inertial.from_geometry(
        Cylinder(r.lid_outer_r, r.lid_h),
        mass=0.08,
        origin=Origin(xyz=(0.0, 0.0, r.lid_h / 2.0)),
    )
    model.articulation(
        "lid_slide",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, rest_clearance)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=-rest_clearance, upper=lift_extra, effort=1.0, velocity=1.0
        ),
    )


def _flip_lid_geom(r: ResolvedContainerBarrelConfig) -> MeshGeometry:
    """Flip-top disc with hinge knuckle + front latch tab + seal ring.

    Local frame origin = the hinge point (at the rear body wall radius). Disk
    center is offset +Y by that radius so it re-centers on the barrel axis /
    mouth."""
    hr = _hinge_radius(r)
    lid_radius = max(hr * 0.92, r.mouth_r + 0.006)
    lid_thick = 0.008
    hinge_len = min(0.036, 1.4 * hr)
    disk = CylinderGeometry(lid_radius, lid_thick, radial_segments=48)
    disk.translate(0.0, hr, lid_thick / 2.0)
    seal = TorusGeometry(lid_radius - 0.006, 0.002, radial_segments=8, tubular_segments=48)
    seal.translate(0.0, hr, 0.001)
    disk.merge(seal)
    # Strap bridges the knuckle (at origin) to the disk edge for connectivity.
    strap_y_start = -0.002
    strap_y_end = hr - lid_radius + 0.010
    strap_len = strap_y_end - strap_y_start
    strap = BoxGeometry((0.028, max(strap_len, 0.006), lid_thick))
    strap.translate(0.0, strap_y_start + strap_len / 2.0, lid_thick / 2.0)
    disk.merge(strap)
    knuckle = CylinderGeometry(0.008, hinge_len * 0.60, radial_segments=16)
    knuckle.rotate_y(math.pi / 2.0)
    disk.merge(knuckle)
    tab = BoxGeometry((0.012, 0.018, 0.006))
    tab.translate(0.0, hr + lid_radius - 0.008, lid_thick / 2.0)
    disk.merge(tab)
    return disk


def _build_flip_lid(model, body, r: ResolvedContainerBarrelConfig, *, lid_mat) -> None:
    """Rear-hinged flip disc about +X at the rear body-wall rim. q=0 closed.

    The hinge sits at the real rear wall radius (``_hinge_radius`` >= neck_r), so
    the joint origin lands on the body's hinge pin and still satisfies the
    rear-of-neck origin check (y <= -neck_r)."""
    hr = _hinge_radius(r)
    hinge_y = -hr
    open_upper = 2.6 * r.joint_travel_scale

    lid = model.part("lid")
    lid.visual(
        mesh_from_geometry(_flip_lid_geom(r), "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("plastic.opaque_generic" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "zinc_bail_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.paint_coated")
    )
    lid_radius = max(hr * 0.92, r.mouth_r + 0.006)
    lid.inertial = Inertial.from_geometry(
        Cylinder(lid_radius, 0.008),
        mass=0.05,
        origin=Origin(xyz=(0.0, hr, 0.004)),
    )
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, r.rim_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(lower=0.0, upper=open_upper, effort=3.0, velocity=2.0),
    )


# ---------------------------------------------------------------------------
# Slot C: grip builders. front clasp (FIXED base + REVOLUTE ring) / top bail
# (REVOLUTE +X) / no grip (badge inline, no part).
# ---------------------------------------------------------------------------
def _clasp_base_mesh():
    """Static buckle body (lever plate + cam block). Clasp-local origin = mount."""
    plate = (
        cq.Workplane("XZ")
        .rect(0.060, 0.050, centered=True)
        .extrude(0.012)
        .translate((0.0, 0.012, -0.020))
    )
    block = (
        cq.Workplane("XY").box(0.052, 0.030, 0.034, centered=True).translate((0.0, 0.018, -0.022))
    )
    return mesh_from_cadquery(plate.union(block), "clasp_base_shell")


def _clasp_ring_mesh():
    """The swinging U-shaped catch wire. Ring-local origin = its own pivot.

    A short pivot rod through the ring-local origin (along X) puts child geometry
    at the ring_swing joint origin (the legs alone start ~24mm off-axis)."""
    # Pivot rod along X straddling the ring-local origin (the hinge line).
    pivot = cq.Workplane("YZ").circle(0.005).extrude(0.058).translate((-0.029, 0.0, 0.0))
    ring = pivot
    for sx in (-0.024, 0.024):
        leg = cq.Workplane("XY").circle(0.005).extrude(0.050).translate((sx, 0.0, -0.050))
        ring = ring.union(leg)
    cross = cq.Workplane("YZ").circle(0.005).extrude(0.052).translate((-0.026, 0.0, -0.048))
    return mesh_from_cadquery(ring.union(cross), "clasp_ring_shell")


def _build_front_clasp(model, body, r: ResolvedContainerBarrelConfig, *, accent_mat) -> None:
    """Front +Y buckle clasp: FIXED base + REVOLUTE swing ring (only ring moves).

    Mounted on the upper belly (flip-top latch lives at the rim, so the clasp
    sits a little lower to avoid it). The clasp_base plate's back face is ~6mm
    in front of its local origin, so the mount origin is placed at the body wall
    radius MINUS that back-face offset MINUS a 2mm bite, guaranteeing the plate
    back solidly touches/penetrates the (now exactly-evaluated) wall surface and
    the base never floats off the narrow stepped waist."""
    clasp_z = r.rim_z * 0.62
    clasp_y = _surface_r(r, clasp_z) - 0.006 - 0.002

    clasp_base = model.part("clasp_base")
    clasp_base.visual(_clasp_base_mesh(), material=accent_mat, name="clasp_base_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.steel_galvanized"))
    clasp_base.inertial = Inertial.from_geometry(
        Box((0.06, 0.04, 0.05)),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.015, -0.020)),
    )
    model.articulation(
        "clasp_mount",
        ArticulationType.FIXED,
        parent=body,
        child=clasp_base,
        origin=Origin(xyz=(0.0, clasp_y, clasp_z)),
    )

    clasp_ring = model.part("clasp_ring")
    clasp_ring.visual(_clasp_ring_mesh(), material=accent_mat, name="clasp_ring_shell", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.steel_galvanized"))
    clasp_ring.inertial = Inertial.from_geometry(
        Box((0.06, 0.012, 0.05)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, -0.025)),
    )
    model.articulation(
        "ring_swing",
        ArticulationType.REVOLUTE,
        parent=clasp_base,
        child=clasp_ring,
        origin=Origin(xyz=(0.0, 0.020, -0.016)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=2.0, lower=0.0, upper=math.radians(120.0) * r.joint_travel_scale
        ),
    )


def _wire_segment(p0, p1, wire_r: float) -> CylinderGeometry | None:
    """A wire cylinder spanning p0->p1 (default +Z geometry rotated to align).

    Built with mesh-geometry rotate_y/rotate_z only (no CadQuery booleans, which
    hang on the long bail union chain at sweep scale)."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    seg_len = math.sqrt(dx * dx + dy * dy + dz * dz)
    if seg_len < 1e-9:
        return None
    seg = CylinderGeometry(wire_r, seg_len, radial_segments=8)
    # Center the +Z cylinder at its midpoint, then rotate +Z -> direction.
    seg.translate(0.0, 0.0, seg_len / 2.0)
    polar = math.acos(max(-1.0, min(1.0, dz / seg_len)))  # angle from +Z
    azim = math.atan2(dy, dx)
    seg.rotate_y(polar)
    seg.rotate_z(azim)
    seg.translate(p0[0], p0[1], p0[2])
    return seg


def _bail_mesh(r: ResolvedContainerBarrelConfig) -> MeshGeometry:
    """U-shaped wire bail (mesh segments, no CadQuery booleans).

    q=0: legs hang in -Z, grip arches outward in +Y below the legs.

    The part frame origin is the +X lug pivot (``pivot_x`` = +half_span in the
    parent), so the bail is authored shifted by -pivot_x in X; bail-local (0,0,0)
    is the +X lug hole, where the pivot rod stub exists (child geometry at the
    joint origin), and the REVOLUTE axis is +X (along the shift), so the swing
    is identical to a center-pivoted authoring."""
    half_span = _bail_span(r)
    pivot_x = half_span  # +X lug = part frame origin
    leg_h = 0.130 * (r.rim_z / 0.35)
    arch_depth = 0.022
    grip_reach = max(r.body_max_r * 1.25, 0.14)
    wire_r = 0.004

    geom = MeshGeometry()
    # Short pivot rod stubs seated in each lug bore (along X at bail-local z=0).
    # The +X stub straddles local x=0 (the joint origin); short so the rod does
    # NOT span the full width and pierce the barrel shoulder/neck.
    stub_len = 0.024
    s0 = _wire_segment((-stub_len / 2.0, 0.0, 0.0), (stub_len / 2.0, 0.0, 0.0), wire_r)
    if s0 is not None:
        geom.merge(s0)
    s1 = _wire_segment(
        (-2.0 * half_span - stub_len / 2.0, 0.0, 0.0),
        (-2.0 * half_span + stub_len / 2.0, 0.0, 0.0),
        wire_r,
    )
    if s1 is not None:
        geom.merge(s1)
    # Two vertical legs from pivot down to the grip junction.
    for sx in (1, -1):
        lx = sx * half_span - pivot_x
        leg = _wire_segment((lx, 0.0, wire_r), (lx, 0.0, -leg_h), wire_r)
        if leg is not None:
            geom.merge(leg)

    # Arching grip bar from left leg bottom to right leg bottom.
    n_seg = 10
    pts = []
    for j in range(n_seg + 1):
        t = j / n_seg
        x = -half_span * math.cos(math.pi * t) - pivot_x
        # Grip arches toward -Y at rest so a full +X swing (q=pi) carries it to
        # the FRONT-up (+Y, +Z). A +Y-arching grip instead ends REAR-up, the same
        # quadrant the rear-hinged flip lid opens into, causing bail-vs-lid 穿模.
        # The barrel shell is axisymmetric, so this direction is equally clear of
        # the body for every form/closure.
        y = -grip_reach * math.sin(math.pi * t)
        z = -leg_h - arch_depth * math.sin(math.pi * t)
        pts.append((x, y, z))
    for j in range(n_seg):
        seg = _wire_segment(pts[j], pts[j + 1], wire_r)
        if seg is not None:
            geom.merge(seg)
    return mesh_from_geometry(geom, "bail_wire")


def _build_top_bail(model, body, r: ResolvedContainerBarrelConfig, *, accent_mat) -> None:
    """Top swing bail: REVOLUTE +X about the +/-X lug pivots (lugs inline body)."""
    lug_z = _bail_lug_z(r)
    half_span = _bail_span(r)
    leg_h = 0.130 * (r.rim_z / 0.35)
    arch_depth = 0.022
    grip_reach = max(r.body_max_r * 1.25, 0.14)

    bail = model.part("bail_handle")
    bail.visual(_bail_mesh(r), material=accent_mat, name="bail_wire", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"industrial_blue_black", "keg_blue_black", "stepped_two_tone_blue", "scalloped_deep_blue", "green_drum_black", "food_grade_hdpe_blue"} else "metal.steel_galvanized"))
    # Inertial box re-centered on the bail span (authored shifted by -half_span).
    bail.inertial = Inertial.from_geometry(
        Box((2 * half_span, grip_reach, leg_h + arch_depth)),
        mass=0.12,
        origin=Origin(xyz=(-half_span, -grip_reach / 2, -(leg_h + arch_depth) / 2)),
    )
    model.articulation(
        "bail_swing",
        ArticulationType.REVOLUTE,
        parent=body,
        child=bail,
        origin=Origin(xyz=(half_span, 0.0, lug_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.pi),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_barrel(
    config: ContainerBarrelConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cb_body_{r.palette_style}", rgba=pal.body)
    lid_mat = model.material(f"cb_lid_{r.palette_style}", rgba=pal.lid)
    accent_mat = model.material(f"cb_accent_{r.palette_style}", rgba=pal.accent)
    panel_mat = model.material(f"cb_panel_{r.palette_style}", rgba=pal.panel)

    # --- ROOT: barrel body --------------------------------------------------
    body = model.part("barrel_body")
    _emit_body(body, r, body_mat=body_mat, panel_mat=panel_mat, accent_mat=accent_mat)

    # --- closure (lid mechanism) --------------------------------------------
    if r.closure == "lift_off_lid":
        _build_lift_off_lid(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat)
    elif r.closure == "screw_cap":
        _build_screw_cap(model, body, r, lid_mat=lid_mat, accent_mat=accent_mat)
    elif r.closure == "flip_top_hinged_lid":
        _build_flip_lid(model, body, r, lid_mat=lid_mat)

    # --- grip (optional) ----------------------------------------------------
    if r.grip == "swing_buckle_clasp_front":
        _build_front_clasp(model, body, r, accent_mat=accent_mat)
    elif r.grip == "top_swing_bail_handle":
        _build_top_bail(model, body, r, accent_mat=accent_mat)
    # no_grip_flat_badge emits only the inline badge (in _emit_body).

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_barrel(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_barrel(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid skirt over rim, cap over neck, hinge
# knuckle around pin, bail wire in lug bore, clasp ring in cam block) are
# declared element-scoped + grandfathered so the sweep's overlap / island
# checks pass; the lid / grip mechanism actions are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_barrel_tests(
    object_model: ArticulatedObject,
    config: ContainerBarrelConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("barrel_body")

    # ---- barrel rests on the ground and is taller than wide ----
    aabb = ctx.part_world_aabb(body)
    ctx.check(
        "barrel rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.015,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    # Taller-than-wide is the silhouette of the barrel SHELL (small bail lugs /
    # clasp hardware widen the whole-part AABB but are not the body silhouette).
    shell_aabb = ctx.part_element_world_aabb(body, elem="barrel_shell")
    sext = _ext(shell_aabb)
    ctx.check(
        "barrel is taller than wide (category identity)",
        sext[2] > sext[0] + 0.03 and sext[2] > sext[1] + 0.03,
        details=f"barrel_shell extents={sext}",
    )

    # ---- closure: actions + captured-fit overlaps ----
    if r.closure == "lift_off_lid":
        lid = object_model.get_part("lid")
        lift = object_model.get_articulation("lid_lift")
        ctx.allow_overlap(
            lid,
            body,
            elem_a="lid_shell",
            elem_b="barrel_shell",
            reason="Lift-off lid skirt is intentionally seated over the rolled rim lip.",
        )
        ctx.check(
            "lid_lift is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC and abs(lift.axis[2]) > 0.99,
            details=f"axis={lift.axis}, type={lift.articulation_type}",
        )
        travel = 0.05 * r.joint_travel_scale
        rest = ctx.part_world_position(lid)
        with ctx.pose({lift: travel}):
            up = ctx.part_world_position(lid)
        ctx.check(
            "lid lifts straight up off the rim",
            up[2] > rest[2] + travel * 0.5
            and abs(up[0] - rest[0]) < 1e-4
            and abs(up[1] - rest[1]) < 1e-4,
            details=f"rest_z={rest[2]:.4f}, lifted_z={up[2]:.4f}",
        )

    elif r.closure == "screw_cap":
        carrier = object_model.get_part("lid_carrier")
        lid = object_model.get_part("lid")
        rotate = object_model.get_articulation("lid_rotate")
        slide = object_model.get_articulation("lid_slide")
        ctx.allow_overlap(
            lid,
            body,
            elem_a="lid_shell",
            elem_b="barrel_shell",
            reason="The screw-cap skirt is intentionally seated over the barrel neck when lowered.",
        )
        ctx.allow_isolated_part(
            lid,
            reason="Default display pose lifts the screw cap so the open barrel mouth is visible.",
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
        ctx.check(
            "lid_slide is PRISMATIC about +Z",
            slide.articulation_type == ArticulationType.PRISMATIC and abs(slide.axis[2]) > 0.99,
            details=f"axis={slide.axis}, type={slide.articulation_type}",
        )
        # lid_rotate spins the lid: off-axis key moves.
        m0 = ctx.part_element_world_aabb(lid, elem="lid_molded_key")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({rotate: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(lid, elem="lid_molded_key")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "lid_rotate spins the lid (off-axis key moves)",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.005,
            details=f"rest={m0c}, quarter-turn={m1c}",
        )
        # lid_slide lifts the lid.
        rest_z = ctx.part_world_position(lid)[2]
        with ctx.pose({slide: r.lid_h}):
            up_z = ctx.part_world_position(lid)[2]
        ctx.check(
            "lid_slide lifts the lid off the neck",
            up_z > rest_z + 0.01,
            details=f"rest_z={rest_z:.4f}, lifted_z={up_z:.4f}",
        )

    elif r.closure == "flip_top_hinged_lid":
        lid = object_model.get_part("lid")
        hinge = object_model.get_articulation("lid_hinge")
        ctx.allow_overlap(
            lid,
            body,
            elem_a="lid_shell",
            elem_b="barrel_shell",
            reason="The flip lid hinge knuckle wraps the body hinge pin; the disc rests on the neck rim.",
        )
        ctx.allow_overlap(
            lid,
            body,
            elem_a="lid_shell",
            elem_b="hinge_hardware",
            reason="The lid front latch tab clips into the body latch catch and the knuckle wraps the hinge pin.",
        )
        ctx.check(
            "lid_hinge is REVOLUTE about +X at the rear neck rim",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.99
            and hinge.origin is not None
            and hinge.origin.xyz[1] < -r.neck_r + 0.01
            and abs(hinge.origin.xyz[2] - r.rim_z) < 0.006,
            details=f"axis={hinge.axis}, origin={hinge.origin.xyz if hinge.origin else None}",
        )
        top0 = ctx.part_world_aabb(lid)[1][2]
        with ctx.pose({hinge: 1.6 * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(lid)[1][2]
        ctx.check(
            "lid_hinge flips the lid up (top rises)",
            top1 > top0 + 0.01,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    # ---- grip: actions + captured-fit overlaps ----
    if r.grip == "swing_buckle_clasp_front":
        clasp_base = object_model.get_part("clasp_base")
        clasp_ring = object_model.get_part("clasp_ring")
        ring_swing = object_model.get_articulation("ring_swing")
        clasp_mount = object_model.get_articulation("clasp_mount")
        ctx.allow_overlap(
            clasp_base,
            body,
            elem_a="clasp_base_shell",
            elem_b="barrel_shell",
            reason="Buckle plate is intentionally riveted flush against the front barrel wall.",
        )
        ctx.allow_overlap(
            clasp_ring,
            clasp_base,
            elem_a="clasp_ring_shell",
            elem_b="clasp_base_shell",
            reason="Wire ring legs are intentionally seated into the cam block at the hinge.",
        )
        ctx.allow_overlap(
            clasp_ring,
            body,
            elem_a="clasp_ring_shell",
            elem_b="barrel_shell",
            reason="The swinging wire ring grazes/seats against the front barrel wall under the buckle.",
        )
        ctx.check(
            "clasp_mount is FIXED (static base)",
            clasp_mount.articulation_type == ArticulationType.FIXED,
            details=f"type={clasp_mount.articulation_type}",
        )
        ctx.check(
            "ring_swing is REVOLUTE about +X",
            ring_swing.articulation_type == ArticulationType.REVOLUTE
            and abs(ring_swing.axis[0]) > 0.99,
            details=f"axis={ring_swing.axis}, type={ring_swing.articulation_type}",
        )
        # Only the ring moves; the clasp base stays put.
        base_before = ctx.part_world_position(clasp_base)
        z_rest = ctx.part_world_aabb(clasp_ring)[1][2]
        with ctx.pose({ring_swing: math.radians(110.0)}):
            z_swung = ctx.part_world_aabb(clasp_ring)[1][2]
            base_during = ctx.part_world_position(clasp_base)
        ctx.check(
            "ring swings up about its own pivot",
            z_swung > z_rest + 0.01,
            details=f"ring top_z rest={z_rest:.4f}, swung={z_swung:.4f}",
        )
        ctx.check(
            "buckle base does not move when the ring swings",
            max(abs(a - b) for a, b in zip(base_before, base_during)) < 1e-6,
            details=f"base before={base_before}, during={base_during}",
        )

    elif r.grip == "top_swing_bail_handle":
        bail = object_model.get_part("bail_handle")
        bail_swing = object_model.get_articulation("bail_swing")
        for i in range(2):
            ctx.allow_overlap(
                bail,
                body,
                elem_a="bail_wire",
                elem_b=f"lug_{i}",
                reason=f"Bail wire leg is intentionally seated inside lug_{i} pivot bore.",
            )
        ctx.check(
            "bail_swing is REVOLUTE about +X",
            bail_swing.articulation_type == ArticulationType.REVOLUTE
            and abs(bail_swing.axis[0]) > 0.99,
            details=f"axis={bail_swing.axis}, type={bail_swing.articulation_type}",
        )
        rest_bottom = ctx.part_world_aabb(bail)[0][2]
        with ctx.pose({bail_swing: math.pi / 2}):
            mid_top = ctx.part_world_aabb(bail)[1][2]
        with ctx.pose({bail_swing: math.pi}):
            full_top = ctx.part_world_aabb(bail)[1][2]
        ctx.check(
            "bail swings up from rest",
            mid_top > rest_bottom + 0.03,
            details=f"rest_bottom_z={rest_bottom:.4f}, mid_top_z={mid_top:.4f}",
        )
        ctx.check(
            "bail arches over the lid at full swing",
            full_top > r.rim_z,
            details=f"full_top_z={full_top:.4f}, rim_z={r.rim_z:.4f}",
        )
    else:
        # no_grip_flat_badge: front badge inline body visual present.
        ctx.check(
            "front badge visual exists on the body",
            body.get_visual("front_badge") is not None,
            details="front_badge visual not found",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
