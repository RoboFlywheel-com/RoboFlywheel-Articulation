# SPDX-License-Identifier: Apache-2.0

"""Container cup — modular procedural template (drinking cup / travel mug / tumbler).

Category identity: an upright hollow drinking cup. The cup body (ROOT) rests on
z=0 with its axis along +Z; a sip/flip/screw/slide lid mechanism opens on top
(the main articulation), an optional handle/grip is attached to the side, and a
``wall_pattern_count`` multiplicity axis copies N ribs (or, at low N, N facet
panels) around the wall.

Four axes (spec ``Container_Cup.md``):

  * ``body_form`` (4) — the ROOT ``cup`` part mesh (all loft/extrude/revolve
    hollow open shells): tapered_cone, straight_cylinder, waisted_tumbler,
    stemmed_foot (lathe pedestal + bowl loft).
  * ``lid_closure`` (4) — the lid mechanism (>=1 non-fixed joint each):
      - snap_lift_dome: ``cup_to_lid`` PRISMATIC +Z lid + ``lid_to_sip_flap``
        REVOLUTE +X flap (child of lid). 2 joints.
      - screw_twist_lid: ``cup_to_lid`` REVOLUTE +Z (origin@rim, no Z drift) +
        thread lugs + ``lid_to_sip_flap`` REVOLUTE +X flap. 2 joints.
      - flip_top_lid: lid shell INLINED into the cup visual (not removable),
        only ``cup_to_flap`` REVOLUTE +X (the sole joint).
      - slide_close_ring: ``cup_to_lid`` PRISMATIC +Z lid (pivot boss + capture
        flange) + ``lid_to_slide_ring`` REVOLUTE +Z ring (child of lid). 2 joints.
  * ``handle_grip`` (4, incl. ``ribbed_none``) — none / loop_handle (swept-tube
    cup visual) / snap_sleeve (PRISMATIC +Z sleeve part) / fold_clip_handle
    (bracket cup visual + REVOLUTE -Y bail part).
  * ``wall_pattern_count`` N in [6, 60] — N ribs (N>~10) or N facet panels
    (N<=~10), equiangularly copied as fixed cup visuals.

Continuous size/proportion variation (height/radius/rim/dome/travel scales)
lives in ``resolve_config`` as clamped params, never as slot candidates.
Palette (9 coordinated colorways) is sampled per seed and drives every visual.

Sources (articraft_data ``picture/Container/Cup`` 5-star fork pool): parent
``2eedb76c`` (kraft cone + snap sip lid) plus fork variants straight_cylinder,
waisted_tumbler, stemmed_foot, screw_twist_lid, flip_top_lid, slide_close_ring,
loop_handle, snap_sleeve, fold_clip_handle, n12_bold_flutes, n8_facet_panels.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Container_Cup.md``
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
    CylinderGeometry,
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

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "tapered_cone",
    "straight_cylinder",
    "waisted_tumbler",
    "stemmed_foot",
]
LidClosure = Literal[
    "snap_lift_dome",
    "screw_twist_lid",
    "flip_top_lid",
    "slide_close_ring",
]
HandleGrip = Literal[
    "ribbed_none",
    "loop_handle",
    "snap_sleeve",
    "fold_clip_handle",
]
PaletteStyle = Literal[
    "kraft_paper",
    "glossy_white_ceramic",
    "matte_black_ceramic",
    "brushed_steel_tumbler",
    "pastel_matte_ceramic",
    "colorprint_plastic",
    "enamel_camp",
    "frosted_translucent",
    "polished_copper_tumbler",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "tapered_cone",
    "straight_cylinder",
    "waisted_tumbler",
    "stemmed_foot",
)
LID_CLOSURES: tuple[LidClosure, ...] = (
    "snap_lift_dome",
    "screw_twist_lid",
    "flip_top_lid",
    "slide_close_ring",
)
HANDLE_GRIPS: tuple[HandleGrip, ...] = (
    "ribbed_none",
    "loop_handle",
    "snap_sleeve",
    "fold_clip_handle",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "kraft_paper",
    "glossy_white_ceramic",
    "matte_black_ceramic",
    "brushed_steel_tumbler",
    "pastel_matte_ceramic",
    "colorprint_plastic",
    "enamel_camp",
    "frosted_translucent",
    "polished_copper_tumbler",
)

# Wall pattern multiplicity: low-N facet form vs high-N thin ribs.
N_MIN = 6
N_MAX = 60
FACET_THRESHOLD = 10  # N <= this -> facet panels; N > this -> thin ribs

# ---------------------------------------------------------------------------
# Palettes. Each colorway anchors body / lid / accent (handle, sleeve, bail,
# thread lug, foot) / band (ribs, facets, print, seam). RGBA from spec table,
# anchored to 5-star sample materials where cited.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "kraft_paper": {
        "body": (0.74, 0.55, 0.36, 1.0),
        "lid": (0.93, 0.93, 0.92, 1.0),
        "accent": (0.70, 0.50, 0.30, 1.0),
        "band": (0.62, 0.45, 0.29, 1.0),
    },
    "glossy_white_ceramic": {
        "body": (0.95, 0.95, 0.94, 1.0),
        "lid": (0.86, 0.85, 0.83, 1.0),
        "accent": (0.82, 0.81, 0.80, 1.0),
        "band": (0.80, 0.79, 0.78, 1.0),
    },
    "matte_black_ceramic": {
        "body": (0.14, 0.14, 0.16, 1.0),
        "lid": (0.18, 0.18, 0.20, 1.0),
        "accent": (0.55, 0.56, 0.58, 1.0),
        "band": (0.24, 0.24, 0.26, 1.0),
    },
    "brushed_steel_tumbler": {
        "body": (0.66, 0.67, 0.69, 1.0),
        "lid": (0.58, 0.59, 0.61, 1.0),
        "accent": (0.55, 0.56, 0.58, 1.0),
        "band": (0.48, 0.49, 0.51, 1.0),
    },
    "pastel_matte_ceramic": {
        "body": (0.92, 0.87, 0.78, 1.0),
        "lid": (0.93, 0.93, 0.92, 1.0),
        "accent": (0.80, 0.73, 0.63, 1.0),
        "band": (0.80, 0.73, 0.63, 1.0),
    },
    "colorprint_plastic": {
        "body": (0.84, 0.20, 0.36, 1.0),
        "lid": (0.93, 0.93, 0.92, 1.0),
        "accent": (0.90, 0.90, 0.88, 1.0),
        "band": (0.30, 0.28, 0.32, 1.0),
    },
    "enamel_camp": {
        "body": (0.16, 0.32, 0.46, 1.0),
        "lid": (0.14, 0.28, 0.42, 1.0),
        "accent": (0.30, 0.30, 0.32, 1.0),
        "band": (0.93, 0.93, 0.92, 1.0),
    },
    "frosted_translucent": {
        "body": (0.88, 0.90, 0.91, 0.65),
        "lid": (0.82, 0.85, 0.87, 0.75),
        "accent": (0.78, 0.82, 0.85, 0.85),
        "band": (0.72, 0.78, 0.82, 0.85),
    },
    "polished_copper_tumbler": {
        "body": (0.72, 0.45, 0.30, 1.0),
        "lid": (0.58, 0.36, 0.24, 1.0),
        "accent": (0.66, 0.41, 0.27, 1.0),
        "band": (0.50, 0.31, 0.20, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base geometry constants (meters). Shared baseline across all body forms; the
# rim radius RIM_R stays fixed across forms so the lid family always fits.
# ---------------------------------------------------------------------------
_CUP_H = 0.190           # nominal cup wall height
_BASE_R = 0.028          # tapered/stemmed base outer radius (narrow)
_RIM_R = 0.045           # outer radius at rim (lid mount diameter)
_WALL_T = 0.0018         # wall thickness

_LID_SKIRT_H = 0.018     # how far the lid skirt wraps down over the rim
_LID_OVERLAP = 0.008     # vertical overlap of skirt onto the cup wall (snap)
_LID_DOME_H = 0.020      # raised drink-dome height above the rim plane

_LID_LIFT = 0.045        # snap/slide lid prismatic travel
_SLEEVE_TRAVEL_LO = -0.020
_SLEEVE_TRAVEL_HI = 0.030


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ContainerCupConfig:
    body_form: BodyForm = "tapered_cone"
    lid_closure: LidClosure = "snap_lift_dome"
    handle_grip: HandleGrip = "ribbed_none"
    palette_style: PaletteStyle = "kraft_paper"
    wall_pattern_count: int = 56
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    rim_radius_scale: float = 1.0
    lid_dome_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_cup"


@dataclass(frozen=True)
class ResolvedContainerCupConfig:
    body_form: BodyForm
    lid_closure: LidClosure
    handle_grip: HandleGrip
    palette_style: PaletteStyle
    wall_pattern_count: int
    use_facets: bool
    body_height_scale: float
    body_radius_scale: float
    rim_radius_scale: float
    lid_dome_scale: float
    joint_travel_scale: float
    # derived geometry
    cup_h: float          # height of the wall/bowl portion (rim above base/pedestal)
    base_r: float
    rim_r: float          # outer radius at the rim (lid mount)
    wall_t: float
    pedestal_z: float     # z of the pedestal->bowl junction (0 unless stemmed_foot)
    rim_top_z: float      # world z of the rim plane (lid mount)
    lid_skirt_h: float
    lid_overlap: float
    lid_dome_h: float
    lid_lift: float
    name: str


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def _sample_wall_pattern_count(rng: random.Random) -> int:
    """Weighted N draw: small N frequent, large N rare (typical cups carry
    ~8-28 ribs/facets; the [28,60] tail is sampled sparsely)."""
    bucket = rng.random()
    if bucket < 0.45:
        return rng.randint(6, 14)
    if bucket < 0.80:
        return rng.randint(14, 28)
    if bucket < 0.94:
        return rng.randint(28, 44)
    return rng.randint(44, 60)


def config_from_seed(seed: int) -> ContainerCupConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerCupConfig(
        body_form=rng.choice(BODY_FORMS),
        lid_closure=rng.choice(LID_CLOSURES),
        handle_grip=rng.choice(HANDLE_GRIPS),
        palette_style=rng.choice(PALETTE_STYLES),
        wall_pattern_count=_sample_wall_pattern_count(rng),
        body_height_scale=round(rng.uniform(0.85, 1.20), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        rim_radius_scale=round(rng.uniform(0.92, 1.08), 4),
        lid_dome_scale=round(rng.uniform(0.85, 1.15), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_cup_{seed}",
    )


def resolve_config(
    config: ContainerCupConfig | None = None,
) -> ResolvedContainerCupConfig:
    cfg = config or ContainerCupConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    lid_closure = _pick(cfg.lid_closure, LID_CLOSURES)
    handle_grip = _pick(cfg.handle_grip, HANDLE_GRIPS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(_clamp(cfg.wall_pattern_count, N_MIN, N_MAX))
    use_facets = n <= FACET_THRESHOLD

    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    rim_scale = _clamp(cfg.rim_radius_scale, 0.92, 1.08)
    dome_scale = _clamp(cfg.lid_dome_scale, 0.85, 1.15)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.10)

    # rim_radius is an equation driver: rim_r follows body radius and its own
    # scale; lid skirt bore / dome / thread lug radii derive from rim_r so the
    # lid family always fits the rim (cap-over-rim inequality holds by design).
    rim_r = _RIM_R * r_scale * rim_scale
    base_r = _BASE_R * r_scale

    # stemmed_foot lifts the bowl onto a pedestal; the bowl portion is shorter so
    # the overall height stays in the cup band. Other forms have pedestal_z=0.
    if body_form == "stemmed_foot":
        pedestal_z = (0.012 + 0.058) * h_scale  # foot + stem
        cup_h = 0.120 * h_scale                 # bowl wall height
    else:
        pedestal_z = 0.0
        cup_h = _CUP_H * h_scale

    rim_top_z = pedestal_z + cup_h
    lid_dome_h = _LID_DOME_H * dome_scale
    lid_lift = _LID_LIFT * jt_scale

    return ResolvedContainerCupConfig(
        body_form=body_form,
        lid_closure=lid_closure,
        handle_grip=handle_grip,
        palette_style=palette,
        wall_pattern_count=n,
        use_facets=use_facets,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        rim_radius_scale=rim_scale,
        lid_dome_scale=dome_scale,
        joint_travel_scale=jt_scale,
        cup_h=cup_h,
        base_r=base_r,
        rim_r=rim_r,
        wall_t=_WALL_T,
        pedestal_z=pedestal_z,
        rim_top_z=rim_top_z,
        lid_skirt_h=_LID_SKIRT_H,
        lid_overlap=_LID_OVERLAP,
        lid_dome_h=lid_dome_h,
        lid_lift=lid_lift,
        name=cfg.name or "container_cup",
    )


def with_overrides(config: ContainerCupConfig, **kwargs: object) -> ContainerCupConfig:
    return replace(config, **kwargs)


def _wall_pattern_module(r: ResolvedContainerCupConfig) -> str:
    return f"facet_x{r.wall_pattern_count}" if r.use_facets else f"rib_x{r.wall_pattern_count}"


def slot_choices_for_config(
    config: ContainerCupConfig | ResolvedContainerCupConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedContainerCupConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("lid_closure", r.lid_closure),
        ("handle_grip", r.handle_grip),
        ("wall_pattern_count", _wall_pattern_module(r)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Cup outer-radius profile per body form (used by ribs / facets / sleeve /
# handle / bracket so wall hardware follows the actual wall).
# ---------------------------------------------------------------------------
def _cup_outer_radius(r: ResolvedContainerCupConfig, z: float) -> float:
    """Outer wall radius at world height z for the cup body (bowl region)."""
    pz = r.pedestal_z
    top = r.rim_top_z
    if r.body_form == "straight_cylinder":
        return r.rim_r
    if r.body_form == "waisted_tumbler":
        return _waist_radius(r, z)
    # tapered_cone and stemmed_foot: linear taper from base_r (at pz) to rim_r.
    t = _clamp((z - pz) / max(top - pz, 1e-6), 0.0, 1.0)
    return r.base_r + (r.rim_r - r.base_r) * t


def _waist_stations(r: ResolvedContainerCupConfig) -> list[tuple[float, float]]:
    """Waisted hourglass stations (z, outer_r) for the bowl, scaled to cup_h.
    Wide at base and rim, narrowest at the mid grip waist. Rim radius == rim_r."""
    h = r.cup_h
    base = r.base_r + 0.009  # waisted forms have a wider, more stable base
    return [
        (0.000 * h, base),
        (0.263 * h, base + 0.005),
        (0.500 * h, base - 0.004),   # waist (narrowest)
        (0.789 * h, base + 0.006),
        (1.000 * h, r.rim_r),
    ]


def _waist_radius(r: ResolvedContainerCupConfig, z: float) -> float:
    pz = r.pedestal_z
    stations = _waist_stations(r)
    zl = z - pz
    if zl <= stations[0][0]:
        return stations[0][1]
    if zl >= stations[-1][0]:
        return stations[-1][1]
    for i in range(len(stations) - 1):
        z0, r0 = stations[i]
        z1, r1 = stations[i + 1]
        if z0 <= zl <= z1:
            t = (zl - z0) / (z1 - z0)
            return r0 + t * (r1 - r0)
    return stations[-1][1]


# ---------------------------------------------------------------------------
# Body shell geometry (Slot A). All hollow open shells (real drinking cavity).
# Authored in WORLD frame (base at z=pedestal_z or 0, rim at rim_top_z).
# ---------------------------------------------------------------------------
def _rim_bead(r: ResolvedContainerCupConfig) -> cq.Workplane:
    """Rolled rim bead ring at the top lip, common to every body form. Starts a
    touch below the rim and a hair inside the wall radius so it always fuses with
    the outer wall (avoids a tangent union that splits into a separate solid)."""
    return (
        cq.Workplane("XY")
        .workplane(offset=r.rim_top_z - 0.018)
        .circle(r.rim_r - 0.001)
        .workplane(offset=0.016)
        .circle(r.rim_r + 0.0016)
        .workplane(offset=0.004)
        .circle(r.rim_r + 0.0016)
        .loft(ruled=False)
    )


def _tapered_shell(r: ResolvedContainerCupConfig) -> cq.Workplane:
    h = r.cup_h
    mid_r = r.base_r + (r.rim_r - r.base_r) * 0.5
    w = r.wall_t
    outer = (
        cq.Workplane("XY")
        .circle(r.base_r)
        .workplane(offset=h * 0.5)
        .circle(mid_r)
        .workplane(offset=h * 0.5)
        .circle(r.rim_r)
        .loft(ruled=False)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=w)
        .circle(r.base_r - w)
        .workplane(offset=h * 0.5)
        .circle(mid_r - w)
        .workplane(offset=h * 0.5 + 0.006)
        .circle(r.rim_r - w)
        .loft(ruled=False)
    )
    outer = outer.union(_rim_bead(r))
    return outer.cut(inner)


def _straight_shell(r: ResolvedContainerCupConfig) -> cq.Workplane:
    h = r.cup_h
    w = r.wall_t
    outer = cq.Workplane("XY").circle(r.rim_r).extrude(h)
    inner = (
        cq.Workplane("XY")
        .workplane(offset=w)
        .circle(r.rim_r - w)
        .extrude(h + 0.006)
    )
    bead = (
        cq.Workplane("XY")
        .workplane(offset=r.rim_top_z - 0.012)
        .circle(r.rim_r + 0.0016)
        .extrude(0.014)
    )
    outer = outer.union(bead)
    return outer.cut(inner)


def _waisted_shell(r: ResolvedContainerCupConfig) -> cq.Workplane:
    stations = _waist_stations(r)
    # Use a slightly thicker effective wall for the waisted form: the narrow
    # grip waist plus a small rim radius can pinch a thin-wall smooth-loft shell
    # into two disjoint solids, so a thicker wall keeps the inner cavity strictly
    # inside the outer everywhere.
    w = max(r.wall_t, 0.0035)
    # outer loft through stations (smooth, keeps the waisted identity)
    wp = cq.Workplane("XY").circle(stations[0][1])
    for i in range(1, len(stations)):
        dz = stations[i][0] - stations[i - 1][0]
        wp = wp.workplane(offset=dz).circle(stations[i][1])
    outer = wp.loft(ruled=False)
    # inner cavity (ruled=True piecewise-linear so it never overshoots the smooth
    # outer near the waist; closed bottom, open top)
    inner_stations = [(w, stations[0][1] - w)]
    for z, rr in stations[1:-1]:
        inner_stations.append((z, rr - w))
    inner_stations.append((r.cup_h + 0.006, stations[-1][1] - w))
    wp = (
        cq.Workplane("XY")
        .workplane(offset=inner_stations[0][0])
        .circle(inner_stations[0][1])
    )
    for i in range(1, len(inner_stations)):
        dz = inner_stations[i][0] - inner_stations[i - 1][0]
        wp = wp.workplane(offset=dz).circle(inner_stations[i][1])
    inner = wp.loft(ruled=True)
    outer = outer.union(_rim_bead(r))
    return outer.cut(inner)


def _stemmed_shell(r: ResolvedContainerCupConfig) -> cq.Workplane:
    """Lathe-revolved pedestal (foot + stem) united with a hollow tapered bowl
    sitting at pedestal_z (parent stemmed-foot ``_cup_body``)."""
    foot_h = 0.012 * r.body_height_scale
    foot_r = max(r.base_r + 0.010, 0.034)
    stem_r = 0.008 * r.body_radius_scale
    pz = r.pedestal_z
    bowl_base_r = r.base_r - 0.004
    bowl_rim_r = r.rim_r
    bowl_h = r.cup_h
    w = r.wall_t

    ped = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(foot_r, 0.0)
        .lineTo(foot_r, foot_h * 0.18)
        .lineTo(foot_r * 0.88, foot_h * 0.40)
        .lineTo(foot_r * 0.60, foot_h * 0.65)
        .lineTo(stem_r + 0.008, foot_h * 0.85)
        .lineTo(stem_r + 0.003, foot_h * 0.95)
        .lineTo(stem_r, foot_h + 0.008)
        .lineTo(stem_r, pz - 0.010)
        .lineTo(stem_r + 0.004, pz - 0.006)
        .lineTo(stem_r + 0.010, pz - 0.003)
        .lineTo(bowl_base_r, pz)
        .lineTo(0.0, pz)
        .close()
        .revolve(360, (0, 0), (0, 1))
    )
    bowl_outer = (
        cq.Workplane("XY")
        .workplane(offset=pz - 0.001)
        .circle(bowl_base_r)
        .workplane(offset=bowl_h * 0.5 + 0.001)
        .circle(bowl_base_r + (bowl_rim_r - bowl_base_r) * 0.5)
        .workplane(offset=bowl_h * 0.5)
        .circle(bowl_rim_r)
        .loft(ruled=False)
    )
    body = ped.union(bowl_outer).union(_rim_bead(r))
    inner = (
        cq.Workplane("XY")
        .workplane(offset=pz + w)
        .circle(bowl_base_r - w)
        .workplane(offset=bowl_h * 0.5)
        .circle(bowl_base_r + (bowl_rim_r - bowl_base_r) * 0.5 - w)
        .workplane(offset=bowl_h * 0.5 + 0.006)
        .circle(bowl_rim_r - w)
        .loft(ruled=False)
    )
    return body.cut(inner)


def _cup_shell(r: ResolvedContainerCupConfig) -> cq.Workplane:
    if r.body_form == "straight_cylinder":
        return _straight_shell(r)
    if r.body_form == "waisted_tumbler":
        return _waisted_shell(r)
    if r.body_form == "stemmed_foot":
        return _stemmed_shell(r)
    return _tapered_shell(r)


# ---------------------------------------------------------------------------
# Wall pattern multiplicity (Slot N). High N -> thin ribs (one union visual);
# low N -> facet panels (one named visual each).
# ---------------------------------------------------------------------------
def _cup_ribs(r: ResolvedContainerCupConfig) -> cq.Workplane:
    """N thin vertical ribs standing proud of the wall, following the contour."""
    n = r.wall_pattern_count
    pz = r.pedestal_z
    z0 = pz + 0.012
    z1 = r.rim_top_z - 0.012
    # multi-station contour samples (more for waisted to follow the curve)
    n_stations = 5 if r.body_form == "waisted_tumbler" else 2
    zs = [z0 + (z1 - z0) * k / (n_stations - 1) for k in range(n_stations)]
    rib_r = 0.0011
    ribs = None
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        cos_a, sin_a = math.cos(ang), math.sin(ang)
        positions = []
        for z in zs:
            rad = _cup_outer_radius(r, z) + 0.0006
            positions.append((rad * cos_a, rad * sin_a))
        wp = (
            cq.Workplane("XY")
            .workplane(offset=zs[0])
            .center(positions[0][0], positions[0][1])
            .circle(rib_r)
        )
        for j in range(1, len(zs)):
            dz = zs[j] - zs[j - 1]
            dx = positions[j][0] - positions[j - 1][0]
            dy = positions[j][1] - positions[j - 1][1]
            wp = wp.workplane(offset=dz).center(dx, dy).circle(rib_r)
        seg = wp.loft(ruled=True)
        ribs = seg if ribs is None else ribs.union(seg)
    return ribs


def _facet_panel(r: ResolvedContainerCupConfig, i: int) -> cq.Workplane:
    """One flat trapezoidal facet panel (low-N polygonal wall). Half-width
    r*tan(pi/N) follows N analytically (parent n8 ``_facet_panel``)."""
    n = r.wall_pattern_count
    ang = 2.0 * math.pi * i / n
    cos_a, sin_a = math.cos(ang), math.sin(ang)
    pz = r.pedestal_z
    z0 = pz + 0.012
    z1 = r.rim_top_z - 0.012
    inset = 0.0008
    t = 0.002  # panel radial thickness

    r_lo = _cup_outer_radius(r, z0) - inset
    r_hi = _cup_outer_radius(r, z1) - inset
    hw_lo = r_lo * math.tan(math.pi / n)
    hw_hi = r_hi * math.tan(math.pi / n)

    b_ri = (r_lo * cos_a + hw_lo * sin_a, r_lo * sin_a - hw_lo * cos_a)
    b_li = (r_lo * cos_a - hw_lo * sin_a, r_lo * sin_a + hw_lo * cos_a)
    b_lo = (b_li[0] + t * cos_a, b_li[1] + t * sin_a)
    b_ro = (b_ri[0] + t * cos_a, b_ri[1] + t * sin_a)

    t_ri = (r_hi * cos_a + hw_hi * sin_a, r_hi * sin_a - hw_hi * cos_a)
    t_li = (r_hi * cos_a - hw_hi * sin_a, r_hi * sin_a + hw_hi * cos_a)
    t_lo = (t_li[0] + t * cos_a, t_li[1] + t * sin_a)
    t_ro = (t_ri[0] + t * cos_a, t_ri[1] + t * sin_a)

    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .moveTo(b_ri[0], b_ri[1])
        .lineTo(b_li[0], b_li[1])
        .lineTo(b_lo[0], b_lo[1])
        .lineTo(b_ro[0], b_ro[1])
        .close()
        .workplane(offset=z1 - z0)
        .moveTo(t_ri[0], t_ri[1])
        .lineTo(t_li[0], t_li[1])
        .lineTo(t_lo[0], t_lo[1])
        .lineTo(t_ro[0], t_ro[1])
        .close()
        .loft(ruled=True)
    )


def _emit_wall_pattern(cup, r: ResolvedContainerCupConfig, *, band_mat) -> list[str]:
    """Emit the wall pattern as fixed cup visuals. Returns the visual names so
    captured-fit overlaps with the lid skirt can be declared per element."""
    names: list[str] = []
    if r.use_facets:
        for i in range(r.wall_pattern_count):
            name = f"facet_panel_{i}"
            cup.visual(
                mesh_from_cadquery(_facet_panel(r, i), name),
                material=band_mat,
                name=name, material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
            )
            names.append(name)
    else:
        cup.visual(
            mesh_from_cadquery(_cup_ribs(r), "cup_ribs"),
            material=band_mat,
            name="cup_ribs", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
        )
        names.append("cup_ribs")
    return names


# ---------------------------------------------------------------------------
# Lid geometry helpers (Slot B). Two authoring frames:
#   - snap / slide / flip: WORLD frame (z = rim_top_z + ...). The lid PRISMATIC
#     joint origin is world (0,0,0), so the child frame == world frame.
#   - screw: LOCAL frame (z=0 == rim top). The REVOLUTE joint origin is at
#     (0,0,rim_top_z), so the lid is authored about rim_top_z.
# `z0_offset` is the world z of the rim plane in the lid's authoring frame
# (rim_top_z for world-frame lids, 0.0 for the screw lid's local frame).
# ---------------------------------------------------------------------------
def _spout_geom(r: ResolvedContainerCupConfig, *, big: bool):
    """Spout opening + hinge geometry (relative to the rim plane)."""
    spout_w = 0.030 if big else 0.024
    spout_d = 0.022 if big else 0.018
    spout_cy = -(r.rim_r - (0.023 if big else 0.020))
    hinge_y = spout_cy - spout_d * 0.5 - 0.003
    return spout_w, spout_d, spout_cy, hinge_y


def _lid_dome_solid(
    r: ResolvedContainerCupConfig,
    *,
    z0: float,
    spout_w: float,
    spout_d: float,
    spout_cy: float,
    hinge_y: float,
    with_hinge_bar: bool,
    flat_top_for_ring: bool = False,
) -> cq.Workplane:
    """Skirt + shoulder + dome, optional hinge bar, spout cut. `z0` is the rim
    plane in the authoring frame."""
    rim_r = r.rim_r
    skirt_h = r.lid_skirt_h
    dome_h = r.lid_dome_h
    z_base = z0 - r.lid_overlap

    skirt_outer = (
        cq.Workplane("XY")
        .workplane(offset=z_base)
        .circle(rim_r + 0.0035)
        .workplane(offset=skirt_h)
        .circle(rim_r + 0.0035)
        .loft(ruled=False)
    )
    skirt_inner = (
        cq.Workplane("XY")
        .workplane(offset=z_base - 0.001)
        .circle(rim_r - 0.0006)
        .workplane(offset=skirt_h + 0.002)
        .circle(rim_r - 0.0006)
        .loft(ruled=False)
    )
    skirt = skirt_outer.cut(skirt_inner)

    z_top = z_base + skirt_h
    shoulder = (
        cq.Workplane("XY")
        .workplane(offset=z_top - 0.001)
        .circle(rim_r + 0.0035)
        .workplane(offset=0.0025)
        .circle(rim_r + 0.0035)
        .loft(ruled=False)
    )
    if flat_top_for_ring:
        dome = (
            cq.Workplane("XY")
            .workplane(offset=z_top)
            .circle(rim_r - 0.004)
            .workplane(offset=dome_h * 0.55)
            .circle(rim_r - 0.009)
            .workplane(offset=dome_h * 0.45)
            .circle(rim_r - 0.013)
            .loft(ruled=False)
        )
    else:
        dome = (
            cq.Workplane("XY")
            .workplane(offset=z_top)
            .circle(rim_r - 0.004)
            .workplane(offset=dome_h * 0.55)
            .circle(rim_r - 0.012)
            .workplane(offset=dome_h * 0.45)
            .circle(rim_r - 0.022)
            .loft(ruled=False)
        )

    lid = skirt.union(shoulder).union(dome)

    if with_hinge_bar:
        hinge_z = z_top + 0.007
        bar_w = spout_w + 0.010
        bar_d = 0.007
        bar_h = 0.006
        hinge_bar = (
            cq.Workplane("XY")
            .workplane(offset=hinge_z - bar_h * 0.5)
            .center(0.0, hinge_y + 0.001)
            .rect(bar_w, bar_d)
            .extrude(bar_h)
        )
        lid = lid.union(hinge_bar)
        spout_cut = (
            cq.Workplane("XY")
            .workplane(offset=z_top - 0.002)
            .center(0.0, spout_cy)
            .rect(spout_w, spout_d)
            .extrude(dome_h + 0.012)
        )
        lid = lid.cut(spout_cut)

    return lid


def _flap_panel_solid(spout_w: float, spout_d: float) -> cq.Workplane:
    """Hinged drink flap (hinge edge at local y=0, panel extends to +Y)."""
    flap_w = spout_w - 0.002
    flap_d = spout_d + 0.004
    flap_t = 0.003
    panel = (
        cq.Workplane("XY")
        .moveTo(-flap_w * 0.5, 0.0)
        .lineTo(flap_w * 0.5, 0.0)
        .lineTo(flap_w * 0.5 - 0.003, flap_d)
        .lineTo(-flap_w * 0.5 + 0.003, flap_d)
        .close()
        .extrude(flap_t)
    )
    tab = (
        cq.Workplane("XY")
        .workplane(offset=flap_t)
        .center(0.0, flap_d - 0.004)
        .rect(0.010, 0.005)
        .extrude(0.0035)
    )
    seal = (
        cq.Workplane("XY")
        .center(0.0, flap_d * 0.45)
        .rect(flap_w - 0.008, flap_d - 0.008)
        .extrude(-0.003)
    )
    return panel.union(tab).union(seal)


def _emit_sip_flap(
    model,
    lid,
    r: ResolvedContainerCupConfig,
    *,
    parent_for_flap,
    flap_part_name: str,
    joint_name: str,
    hinge_z_world: float,
    spout_w: float,
    spout_d: float,
    hinge_y: float,
    lid_mat,
    hinge_x: float = 0.0,
) -> None:
    """Emit a flap part hinged about +X. `hinge_z_world` is the world z of the
    hinge line; the flap part frame sits at the joint origin. `hinge_x` offsets
    the origin to follow an off-axis-anchored parent lid."""
    flap_w = spout_w - 0.002
    flap_d = spout_d + 0.004
    flap = model.part(flap_part_name)
    flap.visual(
        mesh_from_geometry(
            CylinderGeometry(0.0025, spout_w * 0.6).rotate_y(math.pi / 2.0),
            "flap_knuckle",
        ),
        material=lid_mat,
        name="flap_knuckle", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    flap.visual(
        mesh_from_cadquery(_flap_panel_solid(spout_w, spout_d), "flap_panel"),
        material=lid_mat,
        name="flap_panel", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    flap.inertial = Inertial.from_geometry(
        Box((flap_w, flap_d, 0.003 + 0.004)),
        mass=0.0010,
        origin=Origin(xyz=(0.0, flap_d * 0.5, 0.0015)),
    )
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=parent_for_flap,
        child=flap,
        origin=Origin(xyz=(hinge_x, hinge_y, hinge_z_world)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=0.5, velocity=2.0, lower=0.0, upper=math.radians(120.0)
        ),
    )


# ---- screw thread lugs (cup external + lid internal) ----
_N_THREADS = 3
_THREAD_LUG_W = 0.007
_THREAD_LUG_H = 0.006
_THREAD_LUG_D = 0.0025


def _cup_threads(r: ResolvedContainerCupConfig) -> cq.Workplane:
    """External thread lugs on the cup rim collar (world frame)."""
    r_outer = r.rim_r + 0.0016
    z_center = r.rim_top_z - 0.006
    result = None
    for i in range(_N_THREADS):
        base_angle = 2.0 * math.pi * i / _N_THREADS
        for j in range(2):
            angle = base_angle + j * 0.12
            x_c = r_outer * math.cos(angle)
            y_c = r_outer * math.sin(angle)
            single = (
                cq.Workplane("XY")
                .workplane(offset=z_center - _THREAD_LUG_H * 0.5)
                .center(x_c, y_c)
                .transformed(rotate=(0, 0, math.degrees(angle)))
                .rect(_THREAD_LUG_D, _THREAD_LUG_W)
                .extrude(_THREAD_LUG_H)
            )
            result = single if result is None else result.union(single)
    return result


def _lid_threads(r: ResolvedContainerCupConfig) -> cq.Workplane:
    """Internal thread lugs inside the lid skirt (lid LOCAL frame, z=0=rim top)."""
    r_inner = r.rim_r - 0.0006
    local_z = -0.006  # z_center - rim_top_z
    result = None
    for i in range(_N_THREADS):
        base_angle = 2.0 * math.pi * i / _N_THREADS
        for j in range(2):
            angle = base_angle + j * 0.12
            x_c = r_inner * math.cos(angle)
            y_c = r_inner * math.sin(angle)
            single = (
                cq.Workplane("XY")
                .workplane(offset=local_z - _THREAD_LUG_H * 0.5)
                .center(x_c, y_c)
                .transformed(rotate=(0, 0, math.degrees(angle)))
                .rect(_THREAD_LUG_D, _THREAD_LUG_W)
                .extrude(_THREAD_LUG_H)
            )
            result = single if result is None else result.union(single)
    return result


def _slide_ring_solid(r: ResolvedContainerCupConfig):
    """Flat annular slide ring rotating on the lid dome (local z=0 = dome top)."""
    ring_outer_r = min(0.028, r.rim_r - 0.013)
    ring_inner_r = 0.0038
    ring_thick = 0.0025
    ring_hole_r = 0.005
    ring_hole_orbit = min(0.018, ring_outer_r - 0.006)

    ring = (
        cq.Workplane("XY")
        .circle(ring_outer_r)
        .circle(ring_inner_r)
        .extrude(ring_thick)
    )
    hole = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .center(-ring_hole_orbit, 0.0)
        .circle(ring_hole_r)
        .extrude(ring_thick + 0.002)
    )
    ring = ring.cut(hole)
    tab = (
        cq.Workplane("XY")
        .center(ring_outer_r + 0.002, 0.0)
        .circle(0.005)
        .extrude(ring_thick)
    )
    return ring.union(tab), ring_outer_r, ring_thick


# ---------------------------------------------------------------------------
# Lid builders. Each attaches one lid mechanism to the cup.
# ---------------------------------------------------------------------------
def _build_snap_lift(model, cup, r, *, lid_mat) -> None:
    spout_w, spout_d, spout_cy, hinge_y = _spout_geom(r, big=False)
    # The PRISMATIC joint origin is anchored on the rim WALL at (rim_r,0,rim_top_z)
    # — real cup geometry on the parent side and the lid skirt ring on the child
    # side. The lid is authored in LOCAL frame (z=0 == rim top) and translated by
    # -anchor in x so the off-axis origin re-centers it on the cup axis; the skirt
    # ring passes through child-local x=0 so child geometry exists at the origin.
    anchor = r.rim_r
    lid_solid = _lid_dome_solid(
        r, z0=0.0,
        spout_w=spout_w, spout_d=spout_d, spout_cy=spout_cy, hinge_y=hinge_y,
        with_hinge_bar=True,
    ).translate((-anchor, 0.0, 0.0))
    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(lid_solid, "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=r.rim_r + 0.0035, length=r.lid_skirt_h + r.lid_dome_h),
        mass=0.006,
        origin=Origin(xyz=(-anchor, 0.0, r.lid_dome_h * 0.4)),
    )
    model.articulation(
        "cup_to_lid",
        ArticulationType.PRISMATIC,
        parent=cup,
        child=lid,
        origin=Origin(xyz=(anchor, 0.0, r.rim_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.1, lower=0.0, upper=r.lid_lift),
    )
    z_top_local = -r.lid_overlap + r.lid_skirt_h
    # The flap hinge is in the lid's local frame; the lid mesh was shifted by
    # -anchor in x, so shift the flap hinge x by -anchor too (the flap part frame
    # is placed by the joint origin in the lid frame).
    _emit_sip_flap(
        model, lid, r,
        parent_for_flap=lid, flap_part_name="sip_flap", joint_name="lid_to_sip_flap",
        hinge_z_world=z_top_local + 0.007, spout_w=spout_w, spout_d=spout_d, hinge_y=hinge_y,
        lid_mat=lid_mat, hinge_x=-anchor,
    )


def _screw_neck_collar(r: ResolvedContainerCupConfig) -> cq.Workplane:
    """Inward threaded-neck collar ring at the rim (real screw-cap cups neck the
    mouth inward to a smaller threaded drinking aperture). Spans from the rim
    wall inward to a small central aperture so the cup carries geometry at the
    rim center — the screw REVOLUTE origin (on the cup axis at the rim) lands on
    real cup hardware (origin-on-hardware) while the axis stays central."""
    aperture_r = 0.011  # central drinking aperture
    z_lo = r.rim_top_z - 0.012
    # Outer radius reaches OUT to the rim outer wall (rim_r + small) so the collar
    # embeds into the shell wall/bead and is a connected island, not tangent.
    outer_r = r.rim_r + 0.0016
    collar = (
        cq.Workplane("XY")
        .workplane(offset=z_lo)
        .circle(outer_r)
        .circle(aperture_r)
        .extrude(0.012)
    )
    # The annular collar inner edge sits at aperture_r=0.011 < 0.015, so the
    # rim-center screw origin is within tol of it; the outer edge embeds the shell.
    return collar


def _build_screw_twist(model, cup, r, *, lid_mat, accent_mat) -> None:
    spout_w, spout_d, spout_cy, hinge_y = _spout_geom(r, big=False)
    # Inward threaded-neck collar so the rim-center screw origin lands on real
    # cup geometry; the cup mouth necks to a small aperture (real screw-cup look).
    cup.visual(
        mesh_from_cadquery(_screw_neck_collar(r), "neck_collar"),
        material=lid_mat,
        name="neck_collar", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    # cup external threads (world frame) — add to the cup part as a visual.
    cup.visual(
        mesh_from_cadquery(_cup_threads(r), "cup_threads"),
        material=accent_mat,
        name="cup_threads", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    # lid authored in LOCAL frame (z=0 = rim top).
    lid_solid = _lid_dome_solid(
        r, z0=0.0,
        spout_w=spout_w, spout_d=spout_d, spout_cy=spout_cy, hinge_y=hinge_y,
        with_hinge_bar=True,
    )
    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(lid_solid, "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"))
    lid.visual(mesh_from_cadquery(_lid_threads(r), "lid_threads"), material=accent_mat, name="lid_threads", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=r.rim_r + 0.0035, length=r.lid_skirt_h + r.lid_dome_h),
        mass=0.006,
        origin=Origin(xyz=(0.0, 0.0, r.lid_dome_h * 0.4)),
    )
    model.articulation(
        "cup_to_lid",
        ArticulationType.REVOLUTE,
        parent=cup,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, r.rim_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=5.0, velocity=2.0, lower=0.0, upper=math.radians(270.0)
        ),
    )
    # flap is child of lid, in lid LOCAL frame (z=0 = rim top).
    z_top_local = -r.lid_overlap + r.lid_skirt_h
    _emit_sip_flap(
        model, lid, r,
        parent_for_flap=lid, flap_part_name="sip_flap", joint_name="lid_to_sip_flap",
        hinge_z_world=z_top_local + 0.007, spout_w=spout_w, spout_d=spout_d, hinge_y=hinge_y,
        lid_mat=lid_mat,
    )


def _build_flip_top(model, cup, r, *, lid_mat) -> None:
    """Lid permanently inlined into the cup visual; only the flap articulates."""
    spout_w, spout_d, spout_cy, hinge_y = _spout_geom(r, big=True)
    lid_solid = _lid_dome_solid(
        r, z0=r.rim_top_z,
        spout_w=spout_w, spout_d=spout_d, spout_cy=spout_cy, hinge_y=hinge_y,
        with_hinge_bar=True,
    )
    cup.visual(mesh_from_cadquery(lid_solid, "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"))
    z_top = r.rim_top_z - r.lid_overlap + r.lid_skirt_h
    _emit_sip_flap(
        model, cup, r,
        parent_for_flap=cup, flap_part_name="drink_flap", joint_name="cup_to_flap",
        hinge_z_world=z_top + 0.007, spout_w=spout_w, spout_d=spout_d, hinge_y=hinge_y,
        lid_mat=lid_mat,
    )


def _build_slide_close(model, cup, r, *, lid_mat, accent_mat) -> None:
    # Dome with flat top, center pivot boss + capture flange + drink hole.
    # Lid authored in LOCAL frame (z=0 == rim top) and translated by -anchor in x
    # so the PRISMATIC joint origin on the rim WALL re-centers it (off-axis anchor;
    # see _build_snap_lift). The slide ring is a child of the lid.
    anchor = r.rim_r
    boss_r = 0.003
    boss_h = max(0.005 * r.lid_dome_scale, 0.004)
    drink_hole_r = 0.005
    drink_hole_orbit = min(0.018, r.rim_r - 0.020)

    base = _lid_dome_solid(
        r, z0=0.0,
        spout_w=0.0, spout_d=0.0, spout_cy=0.0, hinge_y=0.0,
        with_hinge_bar=False, flat_top_for_ring=True,
    )
    z_top_local = -r.lid_overlap + r.lid_skirt_h
    dome_top_local = z_top_local + r.lid_dome_h
    boss = (
        cq.Workplane("XY")
        .workplane(offset=dome_top_local - 0.001)
        .circle(boss_r)
        .extrude(boss_h + 0.001)
    )
    flange = (
        cq.Workplane("XY")
        .workplane(offset=dome_top_local + boss_h - 0.001)
        .circle(boss_r + 0.0012)
        .extrude(0.0015)
    )
    lid_solid = base.union(boss).union(flange)
    drink_hole = (
        cq.Workplane("XY")
        .workplane(offset=z_top_local - 0.005)
        .center(drink_hole_orbit, 0.0)
        .circle(drink_hole_r)
        .extrude(r.lid_dome_h + boss_h + 0.015)
    )
    lid_solid = lid_solid.cut(drink_hole).translate((-anchor, 0.0, 0.0))

    lid = model.part("lid")
    lid.visual(mesh_from_cadquery(lid_solid, "lid_shell"), material=lid_mat, name="lid_shell", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"))
    lid.inertial = Inertial.from_geometry(
        Cylinder(radius=r.rim_r + 0.0035, length=r.lid_skirt_h + r.lid_dome_h),
        mass=0.006,
        origin=Origin(xyz=(-anchor, 0.0, r.lid_dome_h * 0.4)),
    )
    model.articulation(
        "cup_to_lid",
        ArticulationType.PRISMATIC,
        parent=cup,
        child=lid,
        origin=Origin(xyz=(anchor, 0.0, r.rim_top_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.1, lower=0.0, upper=r.lid_lift),
    )

    # slide ring (child of lid). The ring is authored centered on its OWN local
    # origin (z=0 at its base); the REVOLUTE joint origin in the lid frame is the
    # (shifted) dome top center, so the ring's center sits there with child
    # geometry at the joint origin (the ring annulus spans the origin).
    ring_solid, ring_outer_r, ring_thick = _slide_ring_solid(r)
    ring = model.part("slide_ring")
    ring.visual(mesh_from_cadquery(ring_solid, "ring_disc"), material=accent_mat, name="ring_disc", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"))
    ring.inertial = Inertial.from_geometry(
        Cylinder(radius=ring_outer_r, length=ring_thick),
        mass=0.001,
        origin=Origin(xyz=(0.0, 0.0, ring_thick * 0.5)),
    )
    model.articulation(
        "lid_to_slide_ring",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=ring,
        origin=Origin(xyz=(-anchor, 0.0, dome_top_local)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=0.5, velocity=2.0, lower=0.0, upper=math.pi),
    )


# ---------------------------------------------------------------------------
# Handle / grip builders (Slot C).
# ---------------------------------------------------------------------------
def _loop_handle_geom(r: ResolvedContainerCupConfig):
    """C-shaped ear handle swept tube on +X, embedded into the wall at two ends."""
    pz = r.pedestal_z
    span = r.rim_top_z - pz
    z_lo = pz + span * 0.30
    z_hi = pz + span * 0.82
    r_lo = _cup_outer_radius(r, z_lo)
    r_hi = _cup_outer_radius(r, z_hi)
    embed = 0.003
    points = [
        (r_lo - embed, 0.0, z_lo),
        (r_lo + 0.016, 0.0, z_lo - 0.004),
        (r_lo + 0.033, 0.0, z_lo + 0.018),
        ((r_lo + r_hi) * 0.5 + 0.038, 0.0, (z_lo + z_hi) * 0.5),
        (r_hi + 0.030, 0.0, z_hi - 0.020),
        (r_hi + 0.013, 0.0, z_hi - 0.004),
        (r_hi - embed, 0.0, z_hi),
    ]
    return tube_from_spline_points(
        points,
        radius=0.006,
        samples_per_segment=18,
        radial_segments=20,
        cap_ends=True,
        up_hint=(0.0, 1.0, 0.0),
    )


def _build_loop_handle(model, cup, r, *, accent_mat) -> None:
    cup.visual(
        mesh_from_geometry(_loop_handle_geom(r), "loop_handle"),
        material=accent_mat,
        name="loop_handle", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )


def _sleeve_body_solid(r: ResolvedContainerCupConfig, *, z_world_base: float, sleeve_h: float):
    """Tapered hollow band following the wall contour with friction-fit bore.
    Authored in LOCAL frame (z from 0 to sleeve_h) but with radii sampled at the
    world heights z_world_base + local_z so the band hugs the wall taper."""
    sleeve_t = 0.003
    r_in_lo = _cup_outer_radius(r, z_world_base)
    r_in_hi = _cup_outer_radius(r, z_world_base + sleeve_h)
    r_out_lo = r_in_lo + sleeve_t
    r_out_hi = r_in_hi + sleeve_t
    outer = (
        cq.Workplane("XY")
        .circle(r_out_lo)
        .workplane(offset=sleeve_h)
        .circle(r_out_hi)
        .loft(ruled=False)
    )
    inner = (
        cq.Workplane("XY")
        .workplane(offset=-0.001)
        .circle(r_in_lo)
        .workplane(offset=sleeve_h + 0.002)
        .circle(r_in_hi)
        .loft(ruled=False)
    )
    return outer.cut(inner)


def _sleeve_ridges_solid(r: ResolvedContainerCupConfig, *, z_world_base: float, sleeve_h: float):
    sleeve_t = 0.003
    n_ridges = 14
    ridge_proud = 0.0008
    ridge_h = 0.002
    r_in_lo = _cup_outer_radius(r, z_world_base)
    r_out_lo = r_in_lo + sleeve_t
    r_in_hi = _cup_outer_radius(r, z_world_base + sleeve_h)
    r_out_hi = r_in_hi + sleeve_t
    ridges = None
    for i in range(n_ridges):
        tt = (i + 0.5) / n_ridges
        z_r = tt * sleeve_h  # local z
        r_out_at = r_out_lo + (r_out_hi - r_out_lo) * tt
        ring_outer = (
            cq.Workplane("XY")
            .workplane(offset=z_r - ridge_h * 0.5)
            .circle(r_out_at + ridge_proud)
            .workplane(offset=ridge_h)
            .circle(r_out_at + ridge_proud)
            .loft(ruled=True)
        )
        ring_cut = (
            cq.Workplane("XY")
            .workplane(offset=z_r - ridge_h * 0.5 - 0.0001)
            .circle(r_out_at - 0.0002)
            .workplane(offset=ridge_h + 0.0002)
            .circle(r_out_at - 0.0002)
            .loft(ruled=True)
        )
        ring = ring_outer.cut(ring_cut)
        ridges = ring if ridges is None else ridges.union(ring)
    return ridges


def _build_snap_sleeve(model, cup, r, *, accent_mat, band_mat) -> None:
    pz = r.pedestal_z
    span = r.rim_top_z - pz
    sleeve_h = min(0.070, span * 0.45)
    rest_z = pz + span * 0.30  # sleeve bottom at rest (mid-wall)
    # Anchor the +Z prismatic origin on the cup WALL at (wall_r,0,rest_z) — real
    # cup glass on the parent side and the sleeve band's bottom ring on the child
    # side. anchor is the wall radius at the joint's z-plane (sleeve bottom) so
    # the band's inner wall passes through child-local x=0 there. The sleeve mesh
    # is shifted by -anchor in x so the off-axis origin re-centers it on the axis.
    anchor = _cup_outer_radius(r, rest_z)
    sleeve = model.part("sleeve")
    sleeve.visual(
        mesh_from_cadquery(
            _sleeve_body_solid(r, z_world_base=rest_z, sleeve_h=sleeve_h).translate((-anchor, 0.0, 0.0)),
            "sleeve_band",
        ),
        material=accent_mat,
        name="sleeve_band", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    sleeve.visual(
        mesh_from_cadquery(
            _sleeve_ridges_solid(r, z_world_base=rest_z, sleeve_h=sleeve_h).translate((-anchor, 0.0, 0.0)),
            "sleeve_ridges",
        ),
        material=band_mat,
        name="sleeve_ridges", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    sleeve.inertial = Inertial.from_geometry(
        Cylinder(radius=r.rim_r * 0.9, length=sleeve_h),
        mass=0.012,
        origin=Origin(xyz=(-anchor, 0.0, sleeve_h * 0.5)),
    )
    travel_lo = _SLEEVE_TRAVEL_LO * r.joint_travel_scale
    travel_hi = _SLEEVE_TRAVEL_HI * r.joint_travel_scale
    model.articulation(
        "cup_to_sleeve",
        ArticulationType.PRISMATIC,
        parent=cup,
        child=sleeve,
        origin=Origin(xyz=(anchor, 0.0, rest_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.08, lower=travel_lo, upper=travel_hi),
    )


_BRACKET_PW = 0.028
_BRACKET_PH = 0.028
_BRACKET_PT = 0.0025
_EAR_W = 0.005
_EAR_H = 0.010
_EAR_T = 0.003
_EAR_SPACING = 0.012
_HANDLE_WIRE_R = 0.0020


def _bracket_solid(r: ResolvedContainerCupConfig, *, z_center: float, wall_r: float, ear_tip_x: float):
    """Clip-on bracket: a wall-hugging plate plus two pivot ears whose outer face
    reaches ear_tip_x so the bail pivot is captured at the standoff distance."""
    # The plate spans from the wall outward to just under the ear so the ear is
    # supported on a real standoff (no floating ear above the wall).
    plate_inner_x = wall_r
    plate_outer_x = max(ear_tip_x, wall_r + _BRACKET_PT)
    plate_depth_x = plate_outer_x - plate_inner_x
    plate_z_lo = z_center - _BRACKET_PH / 2.0
    plate = (
        cq.Workplane("XY")
        .workplane(offset=plate_z_lo)
        .center(plate_inner_x + plate_depth_x / 2.0, 0.0)
        .rect(plate_depth_x, _BRACKET_PW)
        .extrude(_BRACKET_PH)
    )
    plate_top_z = z_center + _BRACKET_PH / 2.0
    ear_x_center = ear_tip_x - _EAR_T / 2.0
    for sign in (-1, 1):
        ear = (
            cq.Workplane("XY")
            .workplane(offset=plate_top_z - _EAR_H * 0.15)
            .center(ear_x_center, sign * _EAR_SPACING)
            .rect(_EAR_T, _EAR_W)
            .extrude(_EAR_H)
        )
        plate = plate.union(ear)
    return plate


def _handle_bail_points():
    return [
        (0.002, -0.008, 0.000),
        (0.001, -0.010, -0.014),
        (-0.001, -0.014, -0.030),
        (-0.003, -0.012, -0.046),
        (-0.004, 0.000, -0.055),
        (-0.003, 0.012, -0.046),
        (-0.001, 0.014, -0.030),
        (0.001, 0.010, -0.014),
        (0.002, 0.008, 0.000),
    ]


def _build_fold_clip_handle(model, cup, r, *, accent_mat, band_mat) -> None:
    pz = r.pedestal_z
    span = r.rim_top_z - pz
    z_center = pz + span * 0.55  # bracket high on the bowl wall
    # The plate inner face must embed the wall over its whole z-span, so hug the
    # MINIMUM wall radius across the plate (waisted walls neck inward at the
    # waist) minus a small inset so the plate always overlaps the shell.
    plate_zs = (
        z_center - _BRACKET_PH / 2.0,
        z_center,
        z_center + _BRACKET_PH / 2.0,
    )
    wall_r = min(_cup_outer_radius(r, z) for z in plate_zs) - 0.0015
    # The bail hangs ~0.055 m below the pivot at rest. On a swelling (waisted /
    # tapered) wall the lower wall radius can exceed the bracket-mount radius, so
    # set the pivot to clear the widest wall radius over the bail's vertical span
    # plus the bail's inward reach, so the resting bail stays just off the wall.
    bail_drop = 0.055
    max_wall_r = max(
        _cup_outer_radius(r, z) for z in (z_center, z_center - bail_drop * 0.5, z_center - bail_drop)
    )
    bail_inward = 0.004  # |min bail x offset| (grip reaches toward the wall)
    pivot_x = max(
        wall_r + _BRACKET_PT + _EAR_T / 2.0,
        max_wall_r + bail_inward + 0.005,
    )
    ear_tip_x = pivot_x + _EAR_T / 2.0
    cup.visual(
        mesh_from_cadquery(
            _bracket_solid(r, z_center=z_center, wall_r=wall_r, ear_tip_x=ear_tip_x),
            "handle_bracket",
        ),
        material=band_mat,
        name="handle_bracket", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    pivot_z = z_center + _BRACKET_PH / 2.0 + _EAR_H * 0.35
    handle = model.part("carry_handle")
    handle.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                _handle_bail_points(),
                radius=_HANDLE_WIRE_R,
                samples_per_segment=16,
                radial_segments=16,
                cap_ends=True,
                up_hint=(1.0, 0.0, 0.0),
            ),
            "handle_bail",
        ),
        material=accent_mat,
        name="handle_bail", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    handle.inertial = Inertial.from_geometry(
        Box((0.010, 0.032, 0.060)), mass=0.004, origin=Origin(xyz=(-0.003, 0.0, -0.028))
    )
    model.articulation(
        "cup_to_handle",
        ArticulationType.REVOLUTE,
        parent=cup,
        child=handle,
        origin=Origin(xyz=(pivot_x, 0.0, pivot_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.radians(115.0)),
    )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_container_cup(
    config: ContainerCupConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    body_mat = model.material(f"cc_body_{r.palette_style}", rgba=pal["body"])
    lid_mat = model.material(f"cc_lid_{r.palette_style}", rgba=pal["lid"])
    accent_mat = model.material(f"cc_accent_{r.palette_style}", rgba=pal["accent"])
    band_mat = model.material(f"cc_band_{r.palette_style}", rgba=pal["band"])

    # --- ROOT: cup body (shell + wall pattern [+ inlined lid / handle visuals]) ---
    cup = model.part("cup")
    cup.visual(
        mesh_from_cadquery(_cup_shell(r), "cup_shell"),
        material=body_mat,
        name="cup_shell", material_class_id=("ceramic.decorative_glazed" if r.palette_style in {"kraft_paper", "glossy_white_ceramic", "matte_black_ceramic", "pastel_matte_ceramic", "colorprint_plastic", "frosted_translucent"} else "metal.brushed_silver"),
    )
    _emit_wall_pattern(cup, r, band_mat=band_mat)
    cup.inertial = Inertial.from_geometry(
        Cylinder(radius=r.rim_r, length=r.rim_top_z),
        mass=0.030,
        origin=Origin(xyz=(0.0, 0.0, r.rim_top_z * 0.45)),
    )

    # --- handle / grip (emit bracket/loop visual on cup before lid for clean union) ---
    if r.handle_grip == "loop_handle":
        _build_loop_handle(model, cup, r, accent_mat=accent_mat)
    elif r.handle_grip == "snap_sleeve":
        _build_snap_sleeve(model, cup, r, accent_mat=accent_mat, band_mat=band_mat)
    elif r.handle_grip == "fold_clip_handle":
        _build_fold_clip_handle(model, cup, r, accent_mat=accent_mat, band_mat=band_mat)

    # --- lid mechanism ---
    if r.lid_closure == "snap_lift_dome":
        _build_snap_lift(model, cup, r, lid_mat=lid_mat)
    elif r.lid_closure == "screw_twist_lid":
        _build_screw_twist(model, cup, r, lid_mat=lid_mat, accent_mat=accent_mat)
    elif r.lid_closure == "flip_top_lid":
        _build_flip_top(model, cup, r, lid_mat=lid_mat)
    elif r.lid_closure == "slide_close_ring":
        _build_slide_close(model, cup, r, lid_mat=lid_mat, accent_mat=accent_mat)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_cup(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_cup(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / QC. Captured-fit overlaps (lid skirt over the rim, thread lugs, slide
# ring in the lid, sleeve over the wall, bail in the bracket) are declared so
# the sweep's island/overlap checks pass; the lid + handle actions are exercised.
# ---------------------------------------------------------------------------
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_cup_tests(
    object_model: ArticulatedObject,
    config: ContainerCupConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    cup = object_model.get_part("cup")

    # ---- cup is an upright hollow drinking cup, base near z=0 ----
    aabb = ctx.part_world_aabb(cup)
    cext = _ext(aabb)
    ctx.check(
        "cup rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"cup min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "cup is upright (height >= footprint)",
        cext[2] > 0.12 and cext[2] > cext[0] - 0.02,
        details=f"cup extents={cext}",
    )
    shell_aabb = ctx.part_element_world_aabb(cup, elem="cup_shell")
    ctx.check(
        "cup is a hollow shell with a real base",
        shell_aabb is not None and shell_aabb[0][2] < 0.008,
        details=f"cup_shell min z={shell_aabb[0][2] if shell_aabb else None}",
    )

    # ---- wall pattern present (ribs union or N facet panels) ----
    if r.use_facets:
        found = sum(
            1 for i in range(r.wall_pattern_count)
            if cup.get_visual(f"facet_panel_{i}") is not None
        )
        ctx.check(
            f"cup has {r.wall_pattern_count} facet panels",
            found == r.wall_pattern_count,
            details=f"found {found} of {r.wall_pattern_count}",
        )
    else:
        ctx.check(
            "cup has a ribbed wall pattern",
            cup.get_visual("cup_ribs") is not None,
            details="cup_ribs visual not found",
        )

    # ---- wall pattern captured-fit overlap with the lid skirt ----
    def _allow_skirt_over_wall(skirt_part, skirt_elem):
        if r.use_facets:
            for i in range(r.wall_pattern_count):
                ctx.allow_overlap(
                    skirt_part, cup, elem_a=skirt_elem, elem_b=f"facet_panel_{i}",
                    reason="Lid/cap skirt overlaps the top of the facet panel where it grips the rim.",
                )
        else:
            ctx.allow_overlap(
                skirt_part, cup, elem_a=skirt_elem, elem_b="cup_ribs",
                reason="Lid/cap skirt overlaps the top of the ribbed wall where it grips the rim.",
            )

    # ---- lid mechanism: actions + captured-fit overlaps ----
    if r.lid_closure == "snap_lift_dome":
        lid = object_model.get_part("lid")
        flap = object_model.get_part("sip_flap")
        lid_joint = object_model.get_articulation("cup_to_lid")
        flap_joint = object_model.get_articulation("lid_to_sip_flap")
        ctx.allow_isolated_part(
            lid,
            reason="lift-off lid clears the cup rim and loses body contact",
        )
        ctx.allow_isolated_part(
            flap,
            reason="sip flap opens clear of the lid and loses contact",
        )
        ctx.allow_overlap(
            lid, cup, elem_a="lid_shell", elem_b="cup_shell",
            reason="Lid skirt is intentionally snapped down over the cup rim bead (snap-on fit).",
        )
        _allow_skirt_over_wall(lid, "lid_shell")
        ctx.allow_overlap(
            flap, lid, elem_a="flap_knuckle", elem_b="lid_shell",
            reason="Flap hinge knuckle barrel is intentionally embedded at the lid hinge bar.",
        )
        ctx.allow_overlap(
            flap, lid, elem_a="flap_panel", elem_b="lid_shell",
            reason="Closed flap seal ridge intentionally seats into the spout opening as a closure.",
        )
        ctx.check(
            "cup_to_lid is PRISMATIC about +Z",
            lid_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(lid_joint.axis[2]) > 0.99,
            details=f"axis={lid_joint.axis}, type={lid_joint.articulation_type}",
        )
        rest_top = ctx.part_world_aabb(lid)[1][2]
        rest_xy = ctx.part_world_position(lid)[:2]
        with ctx.pose({lid_joint: r.lid_lift}):
            lifted_top = ctx.part_world_aabb(lid)[1][2]
            lifted_xy = ctx.part_world_position(lid)[:2]
        ctx.check(
            "lid lifts straight up off the cup",
            lifted_top > rest_top + r.lid_lift * 0.7
            and abs(lifted_xy[0] - rest_xy[0]) < 1e-4
            and abs(lifted_xy[1] - rest_xy[1]) < 1e-4,
            details=f"rest_top={rest_top:.3f}, lifted_top={lifted_top:.3f}",
        )
        ctx.check(
            "lid_to_sip_flap is REVOLUTE about +X",
            flap_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(flap_joint.axis[0]) > 0.99,
            details=f"axis={flap_joint.axis}",
        )
        rest_tip = ctx.part_world_aabb(flap)[1][2]
        with ctx.pose({flap_joint: math.radians(110.0)}):
            open_tip = ctx.part_world_aabb(flap)[1][2]
        ctx.check(
            "sip flap flips up about its hinge",
            open_tip > rest_tip + 0.008,
            details=f"rest_tip={rest_tip:.3f}, open_tip={open_tip:.3f}",
        )
        rest_flap_z = ctx.part_world_position(flap)[2]
        with ctx.pose({lid_joint: r.lid_lift}):
            lifted_flap_z = ctx.part_world_position(flap)[2]
        ctx.check(
            "sip flap lifts together with the lid (child of lid)",
            lifted_flap_z > rest_flap_z + r.lid_lift * 0.7,
            details=f"rest={rest_flap_z:.3f}, lifted={lifted_flap_z:.3f}",
        )

    elif r.lid_closure == "screw_twist_lid":
        lid = object_model.get_part("lid")
        flap = object_model.get_part("sip_flap")
        lid_joint = object_model.get_articulation("cup_to_lid")
        ctx.allow_overlap(
            lid, cup, elem_a="lid_shell", elem_b="cup_shell",
            reason="Lid skirt threads down over the cup rim collar (screw engagement).",
        )
        _allow_skirt_over_wall(lid, "lid_shell")
        ctx.allow_overlap(
            lid, cup, elem_a="lid_threads", elem_b="cup_threads",
            reason="Internal lid thread lugs engage external cup thread lugs (screw fit).",
        )
        ctx.allow_overlap(
            lid, cup, elem_a="lid_threads", elem_b="cup_shell",
            reason="Lid thread lugs sit inside the rim collar engagement zone.",
        )
        ctx.allow_overlap(
            lid, cup, elem_a="lid_shell", elem_b="cup_threads",
            reason="Cup external thread lugs engage inside the lid skirt inner surface.",
        )
        ctx.allow_overlap(
            lid, cup, elem_a="lid_threads", elem_b="neck_collar",
            reason="Lid internal thread lugs seat against the inward threaded-neck collar.",
        )
        ctx.allow_overlap(
            lid, cup, elem_a="lid_shell", elem_b="neck_collar",
            reason="The lid dome closes down onto the threaded-neck collar mouth.",
        )
        # The neck collar embeds into the shell wall/bead at the rim (it is a
        # mouth-necking ring fused into the rim) — intra-part overlap is intended.
        ctx.allow_overlap(
            cup, cup, elem_a="neck_collar", elem_b="cup_shell",
            reason="Threaded-neck collar embeds into the shell rim wall/bead (fused mouth ring).",
        )
        _allow_skirt_over_wall(lid, "lid_threads")
        ctx.allow_overlap(
            flap, lid, elem_a="flap_knuckle", elem_b="lid_shell",
            reason="Flap hinge knuckle barrel is embedded at the lid hinge bar.",
        )
        ctx.allow_overlap(
            flap, lid, elem_a="flap_panel", elem_b="lid_shell",
            reason="Closed flap seal ridge seats into the spout opening as a closure.",
        )
        ctx.check(
            "cup_to_lid is REVOLUTE about +Z (twist)",
            lid_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(lid_joint.axis[2]) > 0.99,
            details=f"axis={lid_joint.axis}, type={lid_joint.articulation_type}",
        )
        rest_z = ctx.part_world_position(lid)[2]
        rest_xy = ctx.part_world_position(lid)[:2]
        with ctx.pose({lid_joint: math.radians(270.0)}):
            twist_z = ctx.part_world_position(lid)[2]
            twist_xy = ctx.part_world_position(lid)[:2]
        ctx.check(
            "lid twists about Z without lifting or translating",
            abs(twist_z - rest_z) < 0.002
            and abs(twist_xy[0] - rest_xy[0]) < 0.002
            and abs(twist_xy[1] - rest_xy[1]) < 0.002,
            details=f"rest_z={rest_z:.4f}, twist_z={twist_z:.4f}",
        )
        rest_flap = ctx.part_world_position(flap)[:2]
        with ctx.pose({lid_joint: math.radians(90.0)}):
            rot_flap = ctx.part_world_position(flap)[:2]
        ctx.check(
            "lid rotation moves the flap circumferentially",
            abs(rot_flap[0] - rest_flap[0]) > 0.005 or abs(rot_flap[1] - rest_flap[1]) > 0.005,
            details=f"rest={rest_flap}, rot={rot_flap}",
        )

    elif r.lid_closure == "flip_top_lid":
        flap = object_model.get_part("drink_flap")
        flap_joint = object_model.get_articulation("cup_to_flap")
        ctx.allow_overlap(
            flap, cup, elem_a="flap_knuckle", elem_b="lid_shell",
            reason="Flap hinge knuckle barrel is embedded at the (inlined) lid hinge bar.",
        )
        ctx.allow_overlap(
            flap, cup, elem_a="flap_panel", elem_b="lid_shell",
            reason="Flap seal ridge seats into the spout opening as a flip-top closure.",
        )
        ctx.check(
            "flip-top lid is inlined into the cup (no separate lid part)",
            cup.get_visual("lid_shell") is not None,
            details="lid_shell should be a cup visual",
        )
        # The flip-top lid itself is not removable: there must be no PRISMATIC
        # *lid* joint. (A snap_sleeve handle may add its own cup_to_sleeve
        # PRISMATIC joint, which is unrelated to the lid.)
        lid_prismatics = [
            a for a in object_model.articulations
            if a.articulation_type == ArticulationType.PRISMATIC
            and a.name in ("cup_to_lid",)
        ]
        ctx.check(
            "no prismatic lid lift-off joint exists (flip-top not removable)",
            len(lid_prismatics) == 0,
            details=f"unexpected lid prismatic joints={[a.name for a in lid_prismatics]}",
        )
        ctx.check(
            "cup_to_flap is REVOLUTE about +X",
            flap_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(flap_joint.axis[0]) > 0.99,
            details=f"axis={flap_joint.axis}",
        )
        rest_top = ctx.part_world_aabb(flap)[1][2]
        with ctx.pose({flap_joint: math.radians(110.0)}):
            open_top = ctx.part_world_aabb(flap)[1][2]
        ctx.check(
            "drink flap swings open (free edge rises)",
            open_top > rest_top + 0.012,
            details=f"rest_top={rest_top:.3f}, open_top={open_top:.3f}",
        )

    elif r.lid_closure == "slide_close_ring":
        lid = object_model.get_part("lid")
        ring = object_model.get_part("slide_ring")
        lid_joint = object_model.get_articulation("cup_to_lid")
        ring_joint = object_model.get_articulation("lid_to_slide_ring")
        ctx.allow_overlap(
            lid, cup, elem_a="lid_shell", elem_b="cup_shell",
            reason="Lid skirt is snapped down over the cup rim bead (snap-on fit).",
        )
        _allow_skirt_over_wall(lid, "lid_shell")
        ctx.allow_overlap(
            ring, lid, elem_a="ring_disc", elem_b="lid_shell",
            reason="The slide ring sits captured on the lid dome over the pivot boss.",
        )
        ctx.check(
            "cup_to_lid is PRISMATIC about +Z",
            lid_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(lid_joint.axis[2]) > 0.99,
            details=f"axis={lid_joint.axis}",
        )
        ctx.check(
            "lid_to_slide_ring is REVOLUTE about +Z",
            ring_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(ring_joint.axis[2]) > 0.99,
            details=f"axis={ring_joint.axis}",
        )
        ring_rest = ctx.part_world_position(ring)
        ring_rest_aabb = ctx.part_world_aabb(ring)
        with ctx.pose({ring_joint: math.pi}):
            ring_open = ctx.part_world_position(ring)
            ring_open_aabb = ctx.part_world_aabb(ring)
        ctx.check(
            "slide ring rotates about its center axis",
            abs(ring_open[0] - ring_rest[0]) < 0.002 and abs(ring_open[1] - ring_rest[1]) < 0.002,
            details=f"rest={ring_rest[:2]}, open={ring_open[:2]}",
        )
        ctx.check(
            "slide ring tab swings from one side to the other",
            abs(ring_open_aabb[0][0] - ring_rest_aabb[0][0]) > 0.003
            or abs(ring_open_aabb[1][0] - ring_rest_aabb[1][0]) > 0.003,
            details=f"rest_x={ring_rest_aabb[0][0]:.4f}, open_x={ring_open_aabb[0][0]:.4f}",
        )
        rest_ring_z = ctx.part_world_position(ring)[2]
        with ctx.pose({lid_joint: r.lid_lift}):
            lifted_ring_z = ctx.part_world_position(ring)[2]
        ctx.check(
            "slide ring lifts together with the lid (child of lid)",
            lifted_ring_z > rest_ring_z + r.lid_lift * 0.7,
            details=f"rest={rest_ring_z:.3f}, lifted={lifted_ring_z:.3f}",
        )

    # ---- handle / grip: actions + captured-fit overlaps ----
    if r.handle_grip == "loop_handle":
        handle_aabb = ctx.part_element_world_aabb(cup, elem="loop_handle")
        ctx.check(
            "loop handle extends outward beyond the cup wall on +X",
            handle_aabb is not None and handle_aabb[1][0] > shell_aabb[1][0] + 0.015,
            details=f"handle max x={handle_aabb[1][0] if handle_aabb else None}",
        )

    elif r.handle_grip == "snap_sleeve":
        sleeve = object_model.get_part("sleeve")
        sleeve_joint = object_model.get_articulation("cup_to_sleeve")
        ctx.allow_overlap(
            sleeve, cup, elem_a="sleeve_band", elem_b="cup_shell",
            reason="Sleeve inner surface is a friction-fit wrap on the cup outer wall.",
        )
        _allow_skirt_over_wall(sleeve, "sleeve_band")
        _allow_skirt_over_wall(sleeve, "sleeve_ridges")
        ctx.check(
            "cup_to_sleeve is PRISMATIC about +Z",
            sleeve_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(sleeve_joint.axis[2]) > 0.99,
            details=f"axis={sleeve_joint.axis}",
        )
        rest_z = ctx.part_world_position(sleeve)[2]
        with ctx.pose({sleeve_joint: _SLEEVE_TRAVEL_HI * r.joint_travel_scale}):
            up_z = ctx.part_world_position(sleeve)[2]
        with ctx.pose({sleeve_joint: _SLEEVE_TRAVEL_LO * r.joint_travel_scale}):
            down_z = ctx.part_world_position(sleeve)[2]
        ctx.check(
            "sleeve slides up and down along the cup wall",
            up_z > rest_z + 0.010 and down_z < rest_z - 0.008,
            details=f"rest={rest_z:.3f}, up={up_z:.3f}, down={down_z:.3f}",
        )

    elif r.handle_grip == "fold_clip_handle":
        carry = object_model.get_part("carry_handle")
        handle_joint = object_model.get_articulation("cup_to_handle")
        ctx.allow_overlap(
            carry, cup, elem_a="handle_bail", elem_b="handle_bracket",
            reason="Bail wire is captured between the bracket ears at the pivot.",
        )
        ctx.allow_overlap(
            cup, cup, elem_a="handle_bracket", elem_b="cup_shell",
            reason="Clip-on bracket plate is intentionally embedded into the cup wall (clip fit).",
        )
        ctx.check(
            "cup_to_handle is REVOLUTE about -Y",
            handle_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(handle_joint.axis[1]) > 0.99,
            details=f"axis={handle_joint.axis}",
        )
        bracket_aabb = ctx.part_element_world_aabb(cup, elem="handle_bracket")
        ctx.check(
            "handle bracket mounted on the +X cup wall",
            bracket_aabb is not None and bracket_aabb[0][0] > 0.020,
            details=f"bracket min x={bracket_aabb[0][0] if bracket_aabb else None}",
        )
        rest_x = ctx.part_world_aabb(carry)[1][0]
        with ctx.pose({handle_joint: math.radians(100.0)}):
            deployed_x = ctx.part_world_aabb(carry)[1][0]
        ctx.check(
            "carry handle swings outward when deployed",
            deployed_x > rest_x + 0.015,
            details=f"rest_x={rest_x:.4f}, deployed_x={deployed_x:.4f}",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
