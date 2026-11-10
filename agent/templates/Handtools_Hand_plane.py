# SPDX-License-Identifier: Apache-2.0

"""Cast-iron hand plane (bench / block / rabbet plane) modular template.

NOTE on the slug name: "hand_plane" here = a **cast-iron hand plane** (a
Stanley/Bailey-style bench smoothing plane, a low-angle block plane, or a
narrow rabbet/shoulder plane), NOT a chisel (single tanged blade, no frog), NOT
a power planer / belt sander (motor + rotating cutter drum), and NOT a
spokeshave / scraper (two-handled, no sole spine, no depth wheel). The structure
family is a cast-iron plane: a fixed ``plane_body`` (root; japanned casting +
bright machined ``sole_edge`` + integral ``frog`` bed) that beds a steel
``cutting_iron`` (blade + chipbreaker) at the mouth (FIXED), a blade-clamp
mechanism (lever cap + flip cam / cross-bar + thumbscrew / threaded post + cap
nut, which decides the PRIMARY joint), a small ``lateral_lever`` (REVOLUTE
about the bed normal) and a knurled brass ``depth_wheel`` (CONTINUOUS about the
up-the-bed axis), plus a user grip (front knob + D-tote / front horn + ring
tote / single palm hump).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Hand_plane.md`` and the
``picture/Handtools/Hand plane`` 5-star sample pool (1 parent + 6 slot-fork
variants), all synced under ``data/records/``.

Coordinate convention (unified across all 7 samples): the plane runs along +X
(toe/front at +X, heel/rear at -X), the flat sole bottom sits on z=0, width is
along Y. The frog bed angle ``bed_deg`` is DERIVED from ``body_silhouette``
(45 deg for solid_block_45 / narrow_open_cheek, 20 deg for low_block_trough)
and drives the whole bed-coordinate stack: ``SQ_BED``/``CQ_BED``, ``_bed_pt``,
``_tilt_back``, ``BED_NORMAL`` (bed normal m; lateral-lever / thumbscrew /
cap-nut axis), ``BED_UP`` (up-the-bed u; depth-wheel axis). Every fixed part's
mesh is authored directly in body-world with an identity part origin; moving
parts are authored about their pivot at the local origin and the joint origin
places the pivot in body-world.

Structure (pattern = ``parallel_children``): a single root ``plane_body`` part
(body + frog mesh chosen by ``body_silhouette``), with three named module axes
plus a shared moving spine:

  * ``body_silhouette`` (3): solid_block_45 (tall solid 45 deg casting) /
    low_block_trough (short 20 deg open trough, low sidewalls) /
    narrow_open_cheek (narrow 45 deg body, open +Y cheek, full-width iron). This
    swaps body+frog mesh + bed angle + iron width; it does NOT change the part
    tree. (parent / blocksole / rabbet variants)
  * ``blade_clamp`` (3): levercap_flipcam (FIXED ``lever_cap`` + a ``cam_lever``
    on a REVOLUTE about -Y, parent=lever_cap, two-level mount) / crossbar_thumbscrew
    (FIXED ``clamp_bar`` on two body ``clamp_boss_{i}`` + a ``thumbscrew`` on a
    REVOLUTE about the bed normal, parent=body) / capnut_post (a ``cap_post`` body
    visual + a ``cap_nut`` KnobGeometry part on a CONTINUOUS about the bed normal,
    parent=body; iron drilled with a ``post_hole``). This is the PRIMARY joint
    axis. (parent / clampbar / screwcap variants)
  * ``grip`` (3): knob_plus_Dtote (turned ``front_knob`` + open-D ``rear_tote``,
    2 FIXED parts) / horn_plus_ringtote (lofted ``front_horn`` + closed-ring
    ``rear_tote``, 2 FIXED parts) / single_palm_hump (one ``palm_rest`` dome,
    no front knob, widened heel boss). (parent / closedtote / palmgrip variants)

The cast-screw / boss / stud / knurl decorations are always body or part visuals
(no FIXED decoration parts; Rule 1). The iron-on-frog bedding, cap/bar/nut
clamping, cam-boss-on-cap-pin, bar-end-on-boss-pin, thumbscrew/cap-nut bore on
stud/post, lateral-boss-in-iron, and wheel-bore-on-stud captures are all
captured-fit geometry, so those joints omit ``MatingContract`` (grandfathered)
and rely on the flat articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source record's run_tests allow_overlap block).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq
from cadquery.selectors import BoxSelector

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    KnobBore,
    KnobGeometry,
    KnobGrip,
    LoftSection,
    MotionLimits,
    Origin,
    SectionLoftSpec,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    section_loft,
)

__modular__ = True

BodySilhouette = Literal["solid_block_45", "low_block_trough", "narrow_open_cheek"]
BladeClamp = Literal["levercap_flipcam", "crossbar_thumbscrew", "capnut_post"]
Grip = Literal["knob_plus_Dtote", "horn_plus_ringtote", "single_palm_hump"]
PaletteStyle = Literal[
    "japanned_cast_iron",
    "bare_steel_sole",
    "brass_adjusters",
    "boxwood_tote",
    "nickel_modern",
]

BODY_SILHOUETTES: tuple[BodySilhouette, ...] = (
    "solid_block_45",
    "low_block_trough",
    "narrow_open_cheek",
)
BLADE_CLAMPS: tuple[BladeClamp, ...] = (
    "levercap_flipcam",
    "crossbar_thumbscrew",
    "capnut_post",
)
GRIPS: tuple[Grip, ...] = (
    "knob_plus_Dtote",
    "horn_plus_ringtote",
    "single_palm_hump",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "japanned_cast_iron",
    "bare_steel_sole",
    "brass_adjusters",
    "boxwood_tote",
    "nickel_modern",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: body (japanned casting) / sole_edge (bright
# machined sole edge) / steel (blade + bright steel hardware: studs, cap_screw,
# lever_cap, clamp_bar, lateral lever) / clamp (cap / bar face accent) /
# brass (depth wheel + thumbscrew + cap nut) / wood (knob / tote / horn / palm).
# Every .visual material is driven off this dict so the swept pool is colorful
# (module_topology_diversity only counts structure).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "japanned_cast_iron": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "sole_edge": (0.78, 0.79, 0.82, 1.0),
        "steel": (0.70, 0.71, 0.74, 1.0),
        "clamp": (0.78, 0.79, 0.82, 1.0),
        "brass": (0.80, 0.62, 0.22, 1.0),
        "wood": (0.40, 0.16, 0.10, 1.0),
    },
    "bare_steel_sole": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "sole_edge": (0.84, 0.85, 0.88, 1.0),
        "steel": (0.72, 0.73, 0.76, 1.0),
        "clamp": (0.80, 0.81, 0.84, 1.0),
        "brass": (0.80, 0.62, 0.22, 1.0),
        "wood": (0.40, 0.16, 0.10, 1.0),
    },
    "brass_adjusters": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "sole_edge": (0.78, 0.79, 0.82, 1.0),
        "steel": (0.70, 0.71, 0.74, 1.0),
        "clamp": (0.82, 0.64, 0.24, 1.0),  # brass-faced lever cap / bar
        "brass": (0.84, 0.66, 0.26, 1.0),
        "wood": (0.40, 0.16, 0.10, 1.0),
    },
    "boxwood_tote": {
        "body": (0.13, 0.13, 0.14, 1.0),
        "sole_edge": (0.78, 0.79, 0.82, 1.0),
        "steel": (0.70, 0.71, 0.74, 1.0),
        "clamp": (0.78, 0.79, 0.82, 1.0),
        "brass": (0.80, 0.62, 0.22, 1.0),
        "wood": (0.72, 0.58, 0.32, 1.0),  # boxwood / beech grips
    },
    "nickel_modern": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "sole_edge": (0.86, 0.87, 0.89, 1.0),
        "steel": (0.74, 0.75, 0.78, 1.0),
        "clamp": (0.84, 0.85, 0.87, 1.0),  # nickel-plated cap
        "brass": (0.84, 0.85, 0.87, 1.0),  # nickel adjusters
        "wood": (0.18, 0.16, 0.15, 1.0),  # dark dyed / hard-rubber grips
    },
}


# ---------------------------------------------------------------------------
# Per-silhouette base dimensions (meters). The frog bed angle is DERIVED here.
#   solid_block_45  : No.4 bench plane     0.245 x 0.062, 45 deg, tall casting.
#   low_block_trough: low-angle block plane 0.155 x 0.052, 20 deg, low walls.
#   narrow_open_cheek: rabbet/shoulder plane 0.200 x 0.030, 45 deg, open cheek.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _SilBase:
    body_len: float
    body_width: float
    sole_thick: float
    height: float  # cheek/wall height above the sole plate
    bed_deg: float
    mouth_x: float
    iron_inset: float  # blade_w = body_width - iron_inset
    knob_dx: float  # toe-boss / knob distance back from the toe (+X) tip
    tote_x: float  # heel grip seat x


_SIL_BASE: dict[BodySilhouette, _SilBase] = {
    "solid_block_45": _SilBase(
        body_len=0.245, body_width=0.062, sole_thick=0.010, height=0.040,
        bed_deg=45.0, mouth_x=0.018, iron_inset=0.020, knob_dx=0.040, tote_x=-0.058,
    ),
    "low_block_trough": _SilBase(
        body_len=0.155, body_width=0.052, sole_thick=0.008, height=0.020,
        bed_deg=20.0, mouth_x=0.015, iron_inset=0.014, knob_dx=0.025, tote_x=-0.050,
    ),
    "narrow_open_cheek": _SilBase(
        body_len=0.200, body_width=0.030, sole_thick=0.008, height=0.035,
        bed_deg=45.0, mouth_x=0.015, iron_inset=0.002, knob_dx=0.035, tote_x=-0.048,
    ),
}


@dataclass(frozen=True)
class HandPlaneConfig:
    body_silhouette: BodySilhouette | None = None
    blade_clamp: BladeClamp | None = None
    grip: Grip | None = None
    palette_style: PaletteStyle = "japanned_cast_iron"
    body_len_scale: float = 1.0
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    cam_open_scale: float = 1.0  # @levercap_flipcam
    screw_turn_scale: float = 1.0  # @crossbar_thumbscrew
    lateral_range_scale: float = 1.0
    knob_height_scale: float = 1.0  # @grips with a front knob/horn
    tote_height_scale: float = 1.0  # @grips with a rear tote
    name: str = "hand_plane"


@dataclass(frozen=True)
class ResolvedHandPlaneConfig:
    body_silhouette: BodySilhouette
    blade_clamp: BladeClamp
    grip: Grip
    palette_style: PaletteStyle
    # Concrete geometry (scaled / derived).
    body_len: float
    body_width: float
    sole_thick: float
    height: float
    bed_deg: float
    mouth_x: float
    iron_width: float  # derived: body_width - inset
    knob_x: float
    tote_x: float
    # Derived bed coordinate helpers.
    sq_bed: float  # sin(bed)
    cq_bed: float  # cos(bed)
    iron_edge_z: float
    sole_top_z: float
    body_top_z: float
    # Joint ranges.
    cam_upper: float
    screw_upper: float
    lateral_lower: float
    lateral_upper: float
    lat_pivot_u: float  # derived: up-the-bed pivot of the lateral lever
    depth_u: float  # derived: up-the-bed center of the depth wheel
    # Grip scales.
    grip_scale: float  # derived: shrink grips proportionally on short bodies
    knob_height_scale: float
    tote_height_scale: float
    name: str

    # ---- bed-coordinate helpers (parameterized by bed angle) ----
    def bed_pt(self, u: float, m: float) -> tuple[float, float, float]:
        return (
            self.mouth_x - self.cq_bed * u + self.sq_bed * m,
            0.0,
            self.iron_edge_z + self.sq_bed * u + self.cq_bed * m,
        )

    @property
    def bed_normal(self) -> tuple[float, float, float]:
        return (self.sq_bed, 0.0, self.cq_bed)

    @property
    def bed_up(self) -> tuple[float, float, float]:
        return (-self.cq_bed, 0.0, self.sq_bed)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> HandPlaneConfig:
    rng = random.Random(seed)
    return HandPlaneConfig(
        body_silhouette=rng.choice(BODY_SILHOUETTES),
        blade_clamp=rng.choice(BLADE_CLAMPS),
        grip=rng.choice(GRIPS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_len_scale=round(rng.uniform(0.90, 1.12), 4),
        body_width_scale=round(rng.uniform(0.90, 1.12), 4),
        body_height_scale=round(rng.uniform(0.90, 1.15), 4),
        cam_open_scale=round(rng.uniform(0.85, 1.10), 4),
        screw_turn_scale=round(rng.uniform(0.85, 1.10), 4),
        lateral_range_scale=round(rng.uniform(0.80, 1.10), 4),
        knob_height_scale=round(rng.uniform(0.85, 1.15), 4),
        tote_height_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_hand_plane_{seed}",
    )


def resolve_config(config: HandPlaneConfig | None = None) -> ResolvedHandPlaneConfig:
    cfg = config or HandPlaneConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    body_silhouette = _pick(cfg.body_silhouette, BODY_SILHOUETTES)
    blade_clamp = _pick(cfg.blade_clamp, BLADE_CLAMPS)
    grip = _pick(cfg.grip, GRIPS)

    base = _SIL_BASE[body_silhouette]

    len_scale = _clamp(cfg.body_len_scale, 0.90, 1.12)
    width_scale = _clamp(cfg.body_width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.body_height_scale, 0.90, 1.15)

    body_len = base.body_len * len_scale
    body_width = base.body_width * width_scale
    height = base.height * height_scale
    sole_thick = base.sole_thick
    bed_deg = base.bed_deg

    # Derived: iron width follows body width minus the candidate inset.
    iron_width = max(0.012, body_width - base.iron_inset)

    # The mouth x and grip seats scale with body length so they stay in
    # proportion to the (scaled) toe and heel.
    mouth_x = base.mouth_x * len_scale
    knob_x = body_len * 0.5 - base.knob_dx * len_scale
    tote_x = base.tote_x * len_scale

    bed_rad = math.radians(bed_deg)
    sq_bed = math.sin(bed_rad)
    cq_bed = math.cos(bed_rad)
    sole_top_z = sole_thick
    iron_edge_z = sole_top_z + 0.0005
    body_top_z = sole_top_z + height

    # Joint ranges (conditional scales only meaningful on the matching module).
    cam_upper = _clamp(1.5 * cfg.cam_open_scale, 1.0, math.pi * 0.95)
    screw_upper = _clamp(6.28 * cfg.screw_turn_scale, 3.0, 2.0 * math.pi)
    lateral_upper = _clamp(0.35 * cfg.lateral_range_scale, 0.15, 0.40)
    lateral_lower = -lateral_upper

    # Grips (knob / tote / horn / palm) are authored at No.4 bench-plane size
    # (~0.245 m body). On the short block plane / narrow rabbet body a full-size
    # tall tote would overhang and collide with the up-the-bed mechanism, so the
    # grip mesh is shrunk proportionally to the body length (spec §7 proportion
    # constraint). The bench plane keeps grip_scale ~1.0.
    grip_scale = _clamp(0.55 + 0.45 * (body_len / 0.245), 0.62, 1.10)

    # Up-the-bed mount positions for the moving spine. The bench plane (long,
    # 45 deg) seats the depth wheel / lateral lever high up the bed (u~0.085 /
    # 0.105); the short block / rabbet body must seat them much closer to the
    # mouth (cf. blocksole source u~0.035 / 0.068) or they collide with the rear
    # grip. Scale u to the body length, then cap by tote clearance (spec §7).
    body_ref = body_len / 0.245  # 1.0 at the bench-plane reference length
    # The lateral lever stem (~0.039 m up the bed) and the depth wheel rim
    # (~0.010 m) point up the bed (-X); their back ends must stay clear (margin)
    # of the rear grip front face (tote_x).
    _LAT_STEM = 0.039
    _MARGIN = 0.004
    lat_pivot_max = (mouth_x - tote_x - _MARGIN) / max(cq_bed, 0.05) - _LAT_STEM
    lat_pivot_u = _clamp(0.105 * body_ref, 0.045, max(0.045, lat_pivot_max))
    # The crossbar_thumbscrew stud / capnut_post rise steeply along the bed
    # normal (m up to ~0.022) right beside the lateral pivot. With the pivot
    # sitting only ~3 mm up the bed from that stud, the lateral lever's boss hub
    # is swallowed by the stud (a whitelisted overlap that still reads as a
    # visible clip in the viewer). Seat the pivot far enough UP the bed that the
    # boss (radius 0.0045) clears the stud/post (radius 0.003) with a small
    # margin. Both stud up-bed positions derive from body_len (see _bar_u /
    # _post_u), so the clearance scales with the body. levercap_flipcam has no
    # protruding stud, so it keeps the base pivot.
    if blade_clamp in ("crossbar_thumbscrew", "capnut_post"):
        if blade_clamp == "crossbar_thumbscrew":
            clamp_u = min(0.060, max(0.030, body_len * 0.245))  # _bar_u
        else:
            clamp_u = min(0.055, max(0.028, body_len * 0.225))  # _post_u
        _BOSS_R = 0.0045
        _STUD_R = 0.003
        _STUD_CLEAR = 0.0005
        lat_pivot_u = max(lat_pivot_u, clamp_u + _BOSS_R + _STUD_R + _STUD_CLEAR)
    depth_max = (mouth_x - tote_x - _MARGIN) / max(cq_bed, 0.05) - 0.011
    depth_u = _clamp(0.085 * body_ref, 0.030, max(0.030, depth_max))

    return ResolvedHandPlaneConfig(
        body_silhouette=body_silhouette,
        blade_clamp=blade_clamp,
        grip=grip,
        palette_style=palette_style,
        body_len=body_len,
        body_width=body_width,
        sole_thick=sole_thick,
        height=height,
        bed_deg=bed_deg,
        mouth_x=mouth_x,
        iron_width=iron_width,
        knob_x=knob_x,
        tote_x=tote_x,
        sq_bed=sq_bed,
        cq_bed=cq_bed,
        iron_edge_z=iron_edge_z,
        sole_top_z=sole_top_z,
        body_top_z=body_top_z,
        cam_upper=cam_upper,
        screw_upper=screw_upper,
        lateral_lower=lateral_lower,
        lateral_upper=lateral_upper,
        lat_pivot_u=lat_pivot_u,
        depth_u=depth_u,
        grip_scale=grip_scale,
        knob_height_scale=_clamp(cfg.knob_height_scale, 0.85, 1.15),
        tote_height_scale=_clamp(cfg.tote_height_scale, 0.85, 1.15),
        name=cfg.name or "hand_plane",
    )


def with_overrides(config: HandPlaneConfig, **kwargs: object) -> HandPlaneConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: HandPlaneConfig | ResolvedHandPlaneConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedHandPlaneConfig)
        else resolve_config(config)
    )
    return (
        ("body_silhouette", r.body_silhouette),
        ("blade_clamp", r.blade_clamp),
        ("grip", r.grip),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared bed geometry helpers (authored in body-world, identity part origin).
# ===========================================================================
def _tilt_back(r: ResolvedHandPlaneConfig, wp: cq.Workplane) -> cq.Workplane:
    """Rotate a flat -X-extending part to the bed angle about +Y."""
    return wp.rotate((0, 0, 0), (0, 1, 0), r.bed_deg)


def _neg(p: tuple[float, float, float]) -> tuple[float, float, float]:
    return (-p[0], -p[1], -p[2])


def _emit_bodyworld_fixed(
    model, body, part_name, mesh, material, visual_name, joint_name, seat
):
    """Emit a FIXED child whose mesh is authored in body-world. The FIXED joint
    origin is the seat point (parent frame) and the visual is shifted by -seat,
    so the child link frame's (0,0,0) lands on the seat geometry (satisfies the
    flat articulation-origin baseline) while the world geometry stays put."""
    part = model.part(part_name)
    part.visual(mesh, origin=Origin(xyz=_neg(seat)), material=material, name=visual_name, material_class_id="metal.generic_plain")
    model.articulation(
        joint_name, ArticulationType.FIXED,
        parent=body, child=part, origin=Origin(xyz=seat),
    )
    return part


def _safe_fillet(wp: cq.Workplane, selector: str, radius: float) -> cq.Workplane:
    """Apply a cosmetic fillet, falling back to the unfilleted solid if OCC
    cannot complete it (e.g. on a small-scaled grip where the radius is too
    large for the thinned feature). The fillet is purely cosmetic, so dropping
    it keeps a valid mesh rather than failing the whole compile."""
    try:
        return wp.edges(selector).fillet(radius)
    except Exception:
        return wp


# ---------------------------------------------------------------------------
# Slot A: body + frog mesh (one helper per silhouette). Each returns the body
# casting Workplane; _frog returns the bed plate Workplane.
# ---------------------------------------------------------------------------
def _bench_plane_body(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    """Cast-iron sole + SOLID mid block with a tight 45 deg iron slot."""
    bw = r.body_width
    sole = cq.Workplane("XY").box(
        r.body_len, bw, r.sole_thick, centered=(True, True, False)
    )
    block_len = min(0.102 * (r.body_len / 0.245), r.body_len - 0.04)
    block = (
        cq.Workplane("XY")
        .box(block_len, bw, r.height, centered=(True, True, False))
        .translate((0.001, 0.0, r.sole_top_z))
    )
    # Slanted iron slot hugging the iron + lever-cap stack.
    slot = (
        cq.Workplane("XY")
        .box(0.204, bw - 0.014, 0.0253, centered=(False, True, False))
        .translate((-0.200, 0.0, -0.0123))
    )
    relief = (
        cq.Workplane("XY")
        .box(0.190, min(0.023, bw - 0.02), 0.0115, centered=(False, True, False))
        .translate((-0.200, 0.0, 0.010))
    )
    channel = _tilt_back(r, slot.union(relief)).translate(
        (r.mouth_x, 0.0, r.iron_edge_z)
    )
    block = block.cut(channel)

    toe_boss = (
        cq.Workplane("XY")
        .circle(0.021)
        .extrude(0.0020)
        .translate((r.knob_x, 0.0, r.sole_top_z))
    )
    heel_boss = (
        cq.Workplane("XY")
        .box(0.058, 0.030, 0.0020, centered=(True, True, False))
        .translate((r.tote_x - 0.026, 0.0, r.sole_top_z))
    )
    body = sole.union(block).union(toe_boss).union(heel_boss)

    mouth = (
        cq.Workplane("XY")
        .box(0.008, bw - 0.018, r.sole_thick + 0.02, centered=(True, True, True))
        .translate((r.mouth_x, 0.0, r.sole_thick * 0.5))
    )
    body = body.cut(mouth)

    half = r.body_len * 0.5
    body = (
        body.edges("|Z")
        .edges(BoxSelector((half - 0.020, -0.05, -0.002), (half + 0.01, 0.05, 0.009)))
        .fillet(0.007)
    )
    body = (
        body.edges("|Z")
        .edges(BoxSelector((-half - 0.01, -0.05, -0.002), (-half + 0.020, 0.05, 0.009)))
        .fillet(0.007)
    )
    return body


def _bench_frog(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    ramp = (
        cq.Workplane("XY")
        .box(0.077, r.body_width - 0.014, 0.0125, centered=(False, True, False))
        .translate((-0.079, 0.0, -0.0125))
    )
    ramp = _tilt_back(r, ramp)
    return ramp.translate((r.mouth_x, 0.0, r.iron_edge_z + 0.0003))


def _block_plane_body(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    """Cast-iron sole + low sidewalls forming an open iron trough (20 deg)."""
    bw = r.body_width
    half = r.body_len * 0.5
    wall_thick = 0.005
    trough_w = bw - 2 * wall_thick

    sole = cq.Workplane("XY").box(
        r.body_len, bw, r.sole_thick, centered=(True, True, False)
    )
    setback = 0.006
    wall_len = r.body_len - 2 * setback
    left_wall = (
        cq.Workplane("XY")
        .box(wall_len, wall_thick, r.height, centered=(True, True, False))
        .translate((0.0, bw * 0.5 - wall_thick * 0.5, r.sole_top_z))
    )
    right_wall = (
        cq.Workplane("XY")
        .box(wall_len, wall_thick, r.height, centered=(True, True, False))
        .translate((0.0, -(bw * 0.5 - wall_thick * 0.5), r.sole_top_z))
    )
    body = sole.union(left_wall).union(right_wall)

    mouth = (
        cq.Workplane("XY")
        .box(0.006, trough_w - 0.004, r.sole_thick + 0.002, centered=(True, True, False))
        .translate((r.mouth_x, 0.0, -0.001))
    )
    body = body.cut(mouth)

    knob_boss = (
        cq.Workplane("XY")
        .circle(0.015)
        .extrude(0.002)
        .translate((r.knob_x, 0.0, r.sole_top_z))
    )
    body = body.union(knob_boss)
    grip_boss = (
        cq.Workplane("XY")
        .box(0.040, 0.030, 0.002, centered=(True, True, False))
        .translate((r.tote_x, 0.0, r.sole_top_z))
    )
    body = body.union(grip_boss)

    body = (
        body.edges("|Z")
        .edges(BoxSelector((half - 0.015, -0.05, -0.002), (half + 0.01, 0.05, r.sole_thick + 0.001)))
        .fillet(0.005)
    )
    body = (
        body.edges("|Z")
        .edges(BoxSelector((-half - 0.01, -0.05, -0.002), (-half + 0.015, 0.05, r.sole_thick + 0.001)))
        .fillet(0.005)
    )
    return body


def _block_frog(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    ramp = (
        cq.Workplane("XY")
        .box(0.042, r.body_width - 0.016, 0.004, centered=(False, True, False))
        .translate((-0.044, 0.0, -0.004))
    )
    ramp = _tilt_back(r, ramp)
    return ramp.translate((r.mouth_x, 0.0, r.iron_edge_z + 0.0002))


def _rabbet_plane_body(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    """Cast-iron sole + asymmetric block: full -Y cheek, open +Y lip (45 deg)."""
    bw = r.body_width
    half = r.body_len * 0.5
    open_cheek_height = 0.003

    sole = cq.Workplane("XY").box(
        r.body_len, bw, r.sole_thick, centered=(True, True, False)
    )
    mid_len = 0.090
    block = (
        cq.Workplane("XY")
        .box(mid_len, bw, r.height, centered=(True, True, False))
        .translate((0.0, 0.0, r.sole_top_z))
    )
    cut_h = r.height - open_cheek_height + 0.002
    open_cut = (
        cq.Workplane("XY")
        .box(mid_len + 0.004, bw * 0.5 + 0.002, cut_h, centered=(True, False, False))
        .translate((0.0, -0.001, r.sole_top_z + open_cheek_height))
    )
    block = block.cut(open_cut)

    slot = (
        cq.Workplane("XY")
        .box(0.180, bw, 0.023, centered=(False, True, False))
        .translate((-0.180, 0.0, -0.0115))
    )
    relief = (
        cq.Workplane("XY")
        .box(0.170, max(0.006, bw - 0.006), 0.010, centered=(False, True, False))
        .translate((-0.170, 0.0, 0.008))
    )
    channel = _tilt_back(r, slot.union(relief)).translate(
        (r.mouth_x, 0.0, r.iron_edge_z)
    )
    block = block.cut(channel)

    toe_boss = (
        cq.Workplane("XY")
        .circle(0.013)
        .extrude(0.002)
        .translate((r.knob_x, 0.0, r.sole_top_z))
    )
    heel_boss = (
        cq.Workplane("XY")
        .box(0.046, 0.024, 0.002, centered=(True, True, False))
        .translate((r.tote_x - 0.021, 0.0, r.sole_top_z))
    )
    body = sole.union(block).union(toe_boss).union(heel_boss)

    mouth = (
        cq.Workplane("XY")
        .box(0.004, bw - 0.006, r.sole_thick + 0.002, centered=(True, True, False))
        .translate((r.mouth_x, 0.0, -0.001))
    )
    body = body.cut(mouth)

    body = (
        body.edges("|Z")
        .edges(BoxSelector((half - 0.015, -0.05, -0.002), (half + 0.01, 0.05, 0.009)))
        .fillet(0.005)
    )
    body = (
        body.edges("|Z")
        .edges(BoxSelector((-half - 0.01, -0.05, -0.002), (-half + 0.015, 0.05, 0.009)))
        .fillet(0.005)
    )
    return body


def _rabbet_frog(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    ramp = (
        cq.Workplane("XY")
        .box(0.068, max(0.006, r.body_width - 0.006), 0.012, centered=(False, True, False))
        .translate((-0.070, 0.0, -0.012))
    )
    ramp = _tilt_back(r, ramp)
    return ramp.translate((r.mouth_x, 0.0, r.iron_edge_z + 0.0003))


_BODY_BUILDERS = {
    "solid_block_45": (_bench_plane_body, _bench_frog),
    "low_block_trough": (_block_plane_body, _block_frog),
    "narrow_open_cheek": (_rabbet_plane_body, _rabbet_frog),
}


def _palm_heel_boss(r: ResolvedHandPlaneConfig) -> cq.Workplane | None:
    """Extra widened heel boss for single_palm_hump (no toe knob boss)."""
    return (
        cq.Workplane("XY")
        .box(0.068, min(0.048, r.body_width + 0.006), 0.0020, centered=(True, True, False))
        .translate((r.tote_x - 0.026, 0.0, r.sole_top_z))
    )


# ---------------------------------------------------------------------------
# Shared body hardware visuals (studs / cap-screw), authored in body-world.
# ---------------------------------------------------------------------------
def _depth_stud(r: ResolvedHandPlaneConfig, stud_center: tuple[float, float, float]) -> cq.Workplane:
    # The stud is coaxial with the depth wheel (along the bed-up axis) and passes
    # through the wheel bore. Its radius slightly exceeds the wheel bore (0.0024)
    # so the wheel is physically captured on (touching) the stud, not floating in
    # the bore. ``stud_center`` is the wheel center; the stud extends down the bed
    # (-Z local) into the body casting so its lower end is grounded (never a
    # floating island) while its upper end holds the wheel.
    stud = cq.Workplane("XY").circle(0.0026).extrude(0.040).translate((0.0, 0.0, -0.032))
    stud = stud.rotate((0, 0, 0), (0, 1, 0), -(90.0 - r.bed_deg))
    return stud.translate(stud_center)


def _cap_screw(r: ResolvedHandPlaneConfig, screw_pos: tuple[float, float, float]) -> cq.Workplane:
    shaft = cq.Workplane("XY").circle(0.0035).extrude(0.030).translate((0.0, 0.0, -0.010))
    head = cq.Workplane("XY").circle(0.005).extrude(0.0035).translate((0.0, 0.0, 0.0195))
    screw = shaft.union(head)
    screw = screw.rotate((0, 0, 0), (0, 1, 0), 90.0 - r.bed_deg)
    return screw.translate(screw_pos)


# ---------------------------------------------------------------------------
# Cutting iron (FIXED, shared). Width follows iron_width; capnut_post drills a
# post_hole; the iron beds at the mouth and rises toward the heel.
# ---------------------------------------------------------------------------
def _cutting_iron(r: ResolvedHandPlaneConfig, *, post_hole_u: float | None) -> cq.Workplane:
    blade_w = r.iron_width
    blade_len = min(0.120, max(0.060, r.body_len * 0.49))
    blade_t = 0.0030

    blade = (
        cq.Workplane("XY")
        .box(blade_len + 0.003, blade_w, blade_t, centered=(False, True, False))
        .translate((-blade_len, 0.0, 0.0))
    )
    cap_len = min(0.095, blade_len - 0.020)
    cap = (
        cq.Workplane("XY")
        .box(cap_len, max(0.004, blade_w - 0.006), 0.0040, centered=(False, True, False))
        .translate((-(cap_len + 0.005), 0.0, blade_t))
    )
    cap = cap.edges("|Y and >Z").fillet(0.0012)
    slot = (
        cq.Workplane("XY")
        .box(min(0.085, cap_len - 0.010), 0.009, 0.02, centered=(False, True, True))
        .translate((-(cap_len + 0.005), 0.0, blade_t + 0.002))
    )
    iron = blade.union(cap).cut(slot)

    if post_hole_u is not None:
        post_hole = (
            cq.Workplane("XY")
            .circle(0.004)
            .extrude(0.020)
            .translate((-post_hole_u, 0.0, -0.005))
        )
        iron = iron.cut(post_hole)

    iron = _tilt_back(r, iron)
    return iron.translate((r.mouth_x, 0.0, r.iron_edge_z))


# ---------------------------------------------------------------------------
# Shared moving spine: lateral lever (REVOLUTE) + depth wheel (CONTINUOUS).
# Authored about their pivot at the local origin.
# ---------------------------------------------------------------------------
def _lateral_lever(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    boss = cq.Workplane("XY").circle(0.0045).extrude(0.004).translate((0.0, 0.0, -0.001))
    stem = (
        cq.Workplane("XY")
        .box(0.030, 0.006, 0.0025, centered=(False, True, False))
        .translate((-0.030, 0.0, 0.0))
    )
    disc = cq.Workplane("XY").circle(0.0065).extrude(0.0025).translate((-0.030, 0.0, 0.0))
    lever = boss.union(stem).union(disc)
    # local -X -> up the bed, local +Z -> bed normal m.
    return lever.rotate((0, 0, 0), (0, 1, 0), r.bed_deg)


def _depth_wheel(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    wheel = cq.Workplane("XY").circle(0.010).extrude(0.0075).translate((0.0, 0.0, -0.00375))
    n = 24
    for i in range(n):
        a = 2.0 * math.pi * i / n
        notch = (
            cq.Workplane("XY")
            .box(0.0016, 0.0016, 0.012, centered=(True, True, True))
            .translate((0.010 * math.cos(a), 0.010 * math.sin(a), 0.0))
        )
        wheel = wheel.cut(notch)
    bore = cq.Workplane("XY").circle(0.0024).extrude(0.03).translate((0.0, 0.0, -0.015))
    wheel = wheel.cut(bore)
    # local +Z -> up-the-bed direction u (the stud axis).
    return wheel.rotate((0, 0, 0), (0, 1, 0), -(90.0 - r.bed_deg))


# ===========================================================================
# Slot B: blade_clamp helpers + emitters.
# ===========================================================================
# --- levercap_flipcam ---
def _cap_plate_len(r: ResolvedHandPlaneConfig) -> float:
    # The cap length follows the body so it does not overhang the heel / collide
    # with the rear grip on a short body.
    return min(0.100, max(0.050, r.body_len * 0.41))


def _lever_cap(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    plate_len = _cap_plate_len(r)
    spine_len = plate_len - 0.014
    plate = (
        cq.Workplane("XY")
        .box(plate_len, min(0.040, r.iron_width + 0.004), 0.0040, centered=(False, True, False))
        .translate((-plate_len, 0.0, 0.0))
    )
    plate = _safe_fillet(plate, "|Z", 0.010)
    spine = (
        cq.Workplane("XY")
        .box(spine_len, 0.018, 0.009, centered=(False, True, False))
        .translate((-(spine_len + 0.012), 0.0, 0.004))
    )
    spine = _safe_fillet(spine, "|X", 0.003)
    cap = plate.union(spine)
    slot = (
        cq.Workplane("XY")
        .slot2D(min(0.038, plate_len * 0.45), 0.009, 0.0)
        .extrude(0.05)
        .translate((-plate_len * 0.5, 0.0, -0.01))
    )
    cap = cap.cut(slot)
    cap = _tilt_back(r, cap)
    return cap.translate(r.bed_pt(0.0018, 0.0068))


def _cam_lever(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    boss = cq.Workplane("XZ").circle(0.0050).extrude(0.016).translate((0.0, 0.008, 0.0))
    finger = (
        cq.Workplane("XY")
        .box(0.032, 0.015, 0.0040, centered=(False, True, False))
        .translate((0.004, 0.0, -0.0042))
    )
    finger = finger.edges("|Z and >X").fillet(0.005)
    cam = boss.union(finger)
    return cam.rotate((0, 0, 0), (0, 1, 0), r.bed_deg)


def _emit_levercap(model, r, body, mats, *, assets) -> None:
    # cap_screw is a body inline visual (no joint; Rule 1).
    screw_pos = r.bed_pt(0.0518, 0.0)
    body.visual(
        mesh_from_cadquery(_cap_screw(r, screw_pos), "cap_screw", assets=assets),
        material=mats["steel"], name="cap_screw", material_class_id="metal.steel_bare",
    )

    # The lever cap is FIXED-seated; its link frame origin sits at cap_seat in
    # body-world (visual shifted by -cap_seat). Seat at the cap mid-length.
    plate_len = _cap_plate_len(r)
    cap_seat = r.bed_pt(plate_len * 0.5, 0.0068)
    cap = _emit_bodyworld_fixed(
        model, body, "lever_cap",
        mesh_from_cadquery(_lever_cap(r), "lever_cap", assets=assets),
        mats["clamp"], "cap", "body_to_lever_cap",
        cap_seat,
    )

    cam = model.part("cam_lever")
    cam.visual(
        mesh_from_cadquery(_cam_lever(r), "cam_lever", assets=assets),
        origin=Origin(), material=mats["steel"], name="cam", material_class_id="metal.steel_bare",
    )
    # PRIMARY: cam flips about -Y; mounted on the lever cap (two-level mount).
    # The pivot is body-world CAM_PIVOT; expressed in the (seated) cap frame it
    # is CAM_PIVOT - cap_seat. The cam mesh is authored about its pivot at the
    # local origin, so the cam child frame's (0,0,0) is on the cam geometry.
    # Cam pin sits near the spine top (just below the plate's heel-end), at m
    # above the spine.
    cam_pivot_world = r.bed_pt(plate_len - 0.006, 0.0238)
    cam_pivot_cap = tuple(a - b for a, b in zip(cam_pivot_world, cap_seat))
    model.articulation(
        "lever_cap_cam", ArticulationType.REVOLUTE,
        parent=cap, child=cam,
        origin=Origin(xyz=cam_pivot_cap),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=3.0, lower=0.0, upper=r.cam_upper),
    )


# --- crossbar_thumbscrew ---
_BAR_M_BOT = 0.007
_BAR_M_TOP = _BAR_M_BOT + 0.005


def _bar_u(r: ResolvedHandPlaneConfig) -> float:
    return min(0.060, max(0.030, r.body_len * 0.245))


def _bar_y_half(r: ResolvedHandPlaneConfig) -> float:
    # Source 0.022 for a 62 mm body; shrink to stay inside narrow bodies so the
    # bar does not overhang (spec §7 BAR_Y_HALF constraint).
    return min(0.022, r.body_width / 2.0 - 0.006)


def _bar_boss_dy(r: ResolvedHandPlaneConfig) -> float:
    return max(0.006, _bar_y_half(r) - 0.002)


def _thumbscrew_stud(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    stud = cq.Workplane("XY").circle(0.003).extrude(0.032).translate((0.0, 0.0, -0.010))
    stud = stud.rotate((0, 0, 0), (0, 1, 0), r.bed_deg)
    return stud.translate(r.bed_pt(_bar_u(r), 0.0))


def _clamp_boss(r: ResolvedHandPlaneConfig, y_sign: int) -> cq.Workplane:
    dy = _bar_boss_dy(r)
    pad = (
        cq.Workplane("XY")
        .box(0.016, 0.008, 0.012, centered=(True, True, False))
        .translate((0.0, y_sign * dy, -0.005))
    )
    pad = pad.edges("|Z").fillet(0.001)
    pin = (
        cq.Workplane("XY")
        .circle(0.002)
        .extrude(0.006)
        .translate((0.0, y_sign * dy, 0.007))
    )
    boss = pad.union(pin)
    boss = _tilt_back(r, boss)
    return boss.translate(r.bed_pt(_bar_u(r), 0.0))


def _clamp_bar(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    bar_u = 0.014
    bar_y = 2.0 * _bar_y_half(r)
    bar_m = _BAR_M_TOP - _BAR_M_BOT
    dy = _bar_boss_dy(r)

    bar = cq.Workplane("XY").box(bar_u, bar_y, bar_m, centered=(True, True, False))
    bar = bar.edges("|Y").fillet(0.001)
    center_hole = (
        cq.Workplane("XY")
        .circle(0.0035)
        .extrude(bar_m + 0.01)
        .translate((0.0, 0.0, -0.005))
    )
    bar = bar.cut(center_hole)
    for i in range(2):
        y_sign = 1 - 2 * i
        pin_hole = (
            cq.Workplane("XY")
            .circle(0.0025)
            .extrude(bar_m + 0.01)
            .translate((0.0, y_sign * dy, -0.005))
        )
        bar = bar.cut(pin_hole)
    bar = _tilt_back(r, bar)
    return bar.translate(r.bed_pt(_bar_u(r), _BAR_M_BOT))


def _thumbscrew(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    radius = 0.010
    height = 0.008
    disc = cq.Workplane("XY").circle(radius).extrude(height)
    n_knurl = 24
    for i in range(n_knurl):
        a = 2.0 * math.pi * i / n_knurl
        notch = (
            cq.Workplane("XY")
            .box(0.0014, 0.0014, height + 0.004, centered=(True, True, True))
            .translate((radius * math.cos(a), radius * math.sin(a), height * 0.5))
        )
        disc = disc.cut(notch)
    bore = (
        cq.Workplane("XY")
        .circle(0.0032)
        .extrude(height + 0.02)
        .translate((0.0, 0.0, -0.010))
    )
    disc = disc.cut(bore)
    washer = cq.Workplane("XY").circle(0.007).extrude(0.001)
    disc = washer.union(disc)
    return disc.rotate((0, 0, 0), (0, 1, 0), r.bed_deg)


def _emit_thumbscrew(model, r, body, mats, *, assets) -> None:
    # thumbscrew_stud + two clamp bosses are body inline visuals (no joint).
    body.visual(
        mesh_from_cadquery(_thumbscrew_stud(r), "thumbscrew_stud", assets=assets),
        material=mats["steel"], name="thumbscrew_stud", material_class_id="metal.steel_bare",
    )
    for i in range(2):
        y_sign = 1 - 2 * i
        body.visual(
            mesh_from_cadquery(_clamp_boss(r, y_sign), f"clamp_boss_{i}", assets=assets),
            material=mats["body"], name=f"clamp_boss_{i}", material_class_id="metal.paint_coated",
        )

    _emit_bodyworld_fixed(
        model, body, "clamp_bar",
        mesh_from_cadquery(_clamp_bar(r), "clamp_bar", assets=assets),
        mats["clamp"], "bar", "body_to_clamp_bar",
        r.bed_pt(_bar_u(r), _BAR_M_BOT),
    )

    screw = model.part("thumbscrew")
    screw.visual(
        mesh_from_cadquery(_thumbscrew(r), "thumbscrew", assets=assets),
        origin=Origin(), material=mats["brass"], name="screw", material_class_id=("metal.brass_polished" if r.palette_style in {"japanned_cast_iron", "bare_steel_sole", "brass_adjusters", "boxwood_tote"} else "metal.chrome_polished"),
    )
    # PRIMARY: thumbscrew spins about the bed normal, parent=body.
    model.articulation(
        "thumbscrew", ArticulationType.REVOLUTE,
        parent=body, child=screw,
        origin=Origin(xyz=r.bed_pt(_bar_u(r), _BAR_M_TOP)),
        axis=r.bed_normal,
        motion_limits=MotionLimits(effort=3.0, velocity=4.0, lower=0.0, upper=r.screw_upper),
    )


# --- capnut_post ---
_POST_RADIUS = 0.003
_CHIPBREAKER_TOP_M = 0.007


def _post_u(r: ResolvedHandPlaneConfig) -> float:
    return min(0.055, max(0.028, r.body_len * 0.225))


def _cap_post(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    post_len = 0.027
    post = (
        cq.Workplane("XY")
        .circle(_POST_RADIUS)
        .extrude(post_len)
        .translate((0.0, 0.0, -0.005))
    )
    post = post.rotate((0, 0, 0), (0, 1, 0), r.bed_deg)
    return post.translate(r.bed_pt(_post_u(r), 0.0))


def _emit_capnut(model, r, body, mats, *, assets) -> None:
    # cap_post is a body inline visual (no joint).
    body.visual(
        mesh_from_cadquery(_cap_post(r), "cap_post", assets=assets),
        material=mats["steel"], name="cap_post", material_class_id="metal.steel_bare",
    )

    cap_nut = model.part("cap_nut")
    cap_nut.visual(
        mesh_from_geometry(
            KnobGeometry(
                0.022,
                0.010,
                body_style="cylindrical",
                grip=KnobGrip(style="knurled", count=24, depth=0.001),
                bore=KnobBore(style="round", diameter=0.007),
                center=False,
            ),
            "cap_nut",
        ),
        # KnobGeometry mounting face at z=0, axis +Z; pitch +bed to align +Z to
        # the bed normal.
        origin=Origin(rpy=(0.0, math.radians(r.bed_deg), 0.0)),
        material=mats["brass"], name="nut", material_class_id=("metal.brass_polished" if r.palette_style in {"japanned_cast_iron", "bare_steel_sole", "brass_adjusters", "boxwood_tote"} else "metal.chrome_polished"),
    )
    # PRIMARY: cap nut spins freely about the bed normal, parent=body.
    model.articulation(
        "cap_nut_spin", ArticulationType.CONTINUOUS,
        parent=body, child=cap_nut,
        origin=Origin(xyz=r.bed_pt(_post_u(r), _CHIPBREAKER_TOP_M)),
        axis=r.bed_normal,
        motion_limits=MotionLimits(effort=2.0, velocity=6.0),
    )


_CLAMP_EMITTERS = {
    "levercap_flipcam": _emit_levercap,
    "crossbar_thumbscrew": _emit_thumbscrew,
    "capnut_post": _emit_capnut,
}


def _clamp_post_hole_u(r: ResolvedHandPlaneConfig) -> float | None:
    return _post_u(r) if r.blade_clamp == "capnut_post" else None


# ===========================================================================
# Slot C: grip helpers + emitters (all FIXED).
# ===========================================================================
def _front_knob(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    gs = r.grip_scale
    kz = r.knob_height_scale * gs  # vertical: knob-height knob × proportion
    prof = [
        (0.0, 0.0),
        (0.020 * gs, 0.0),
        (0.020 * gs, 0.006 * gs),
        (0.013 * gs, 0.010 * gs),
        (0.011 * gs, 0.022 * kz),
        (0.014 * gs, 0.034 * kz),
        (0.018 * gs, 0.044 * kz),
        (0.018 * gs, 0.052 * kz),
        (0.012 * gs, 0.058 * kz),
        (0.0, 0.060 * kz),
    ]
    return (
        cq.Workplane("XZ")
        .polyline([(rad, z) for rad, z in prof])
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )


def _rear_tote_open(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    gs = r.grip_scale
    tz = r.tote_height_scale * gs  # vertical: tote-height × proportion
    outline = [
        (0.000, 0.000),
        (0.060 * gs, 0.000),
        (0.058 * gs, 0.018 * tz),
        (0.052 * gs, 0.030 * tz),
        (0.060 * gs, 0.050 * tz),
        (0.066 * gs, 0.078 * tz),
        (0.060 * gs, 0.110 * tz),
        (0.046 * gs, 0.124 * tz),
        (0.030 * gs, 0.122 * tz),
        (0.022 * gs, 0.104 * tz),
        (0.030 * gs, 0.082 * tz),
        (0.030 * gs, 0.060 * tz),
        (0.018 * gs, 0.046 * tz),
        (0.000, 0.034 * tz),
    ]
    handle = (
        cq.Workplane("XZ")
        .polyline(outline)
        .close()
        .extrude(0.024 * gs)
        .translate((0.0, 0.012 * gs, 0.0))
    )
    hole = (
        cq.Workplane("XZ")
        .center(0.040 * gs, 0.066 * tz)
        .ellipse(0.013 * gs, 0.026 * tz)
        .extrude(0.05)
        .translate((0.0, -0.01, 0.0))
    )
    handle = handle.cut(hole)
    handle = _safe_fillet(handle, "|Y", 0.0015 * gs)
    return handle.rotate((0, 0, 0), (0, 0, 1), 180.0)


def _front_horn_geom(r: ResolvedHandPlaneConfig):
    gs = r.grip_scale
    kz = r.knob_height_scale * gs
    n_pts = 28
    spine = [
        (0.000 * gs, 0.000 * kz, 0.015 * gs),
        (0.004 * gs, 0.014 * kz, 0.014 * gs),
        (0.014 * gs, 0.028 * kz, 0.012 * gs),
        (0.028 * gs, 0.039 * kz, 0.010 * gs),
        (0.042 * gs, 0.045 * kz, 0.007 * gs),
        (0.054 * gs, 0.048 * kz, 0.004 * gs),
    ]
    sections = []
    for sx, sz, rad in spine:
        pts = []
        for j in range(n_pts):
            a = 2.0 * math.pi * j / n_pts
            pts.append((sx + rad * math.cos(a), rad * math.sin(a), sz))
        sections.append(LoftSection(points=tuple(pts)))
    path = tuple((sx, 0.0, sz) for sx, sz, _ in spine)
    return section_loft(
        SectionLoftSpec(sections=tuple(sections), path=path, cap=True, solid=True)
    )


def _rear_tote_ring(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    gs = r.grip_scale
    tz = r.tote_height_scale * gs
    outer = [
        (0.000, 0.000),
        (0.054 * gs, 0.000),
        (0.058 * gs, 0.014 * tz),
        (0.062 * gs, 0.042 * tz),
        (0.066 * gs, 0.076 * tz),
        (0.060 * gs, 0.108 * tz),
        (0.048 * gs, 0.122 * tz),
        (0.032 * gs, 0.128 * tz),
        (0.016 * gs, 0.122 * tz),
        (0.004 * gs, 0.106 * tz),
        (-0.002 * gs, 0.080 * tz),
        (-0.004 * gs, 0.054 * tz),
        (-0.002 * gs, 0.030 * tz),
        (0.000, 0.012 * tz),
    ]
    handle = (
        cq.Workplane("XZ")
        .polyline(outer)
        .close()
        .extrude(0.026 * gs)
        .translate((0.0, -0.013 * gs, 0.0))
    )
    hole = (
        cq.Workplane("XZ")
        .center(0.032 * gs, 0.068 * tz)
        .ellipse(0.011 * gs, 0.024 * tz)
        .extrude(0.06)
        .translate((0.0, -0.017, 0.0))
    )
    handle = handle.cut(hole)
    handle = _safe_fillet(handle, "|Y", 0.0018 * gs)
    return handle.rotate((0, 0, 0), (0, 0, 1), 180.0)


def _palm_rest(r: ResolvedHandPlaneConfig) -> cq.Workplane:
    gs = r.grip_scale
    rad = 0.036 * gs
    h = 0.024 * gs
    pts = []
    n = 40
    for i in range(n + 1):
        a = i / n * math.pi / 2.0
        pts.append((rad * math.cos(a), h * math.sin(a)))
    pts.append((0.0, 0.0))
    dome = (
        cq.Workplane("XZ")
        .polyline(pts)
        .close()
        .revolve(360, (0, 0, 0), (0, 1, 0))
    )
    fp_x = min(0.078 * gs, r.body_len * 0.45)
    fp_y = min(0.054 * gs, r.body_width + 0.010)
    footprint = cq.Workplane("XY").box(fp_x, fp_y, 0.060, centered=(True, True, False))
    hump = dome.intersect(footprint)
    groove = (
        cq.Workplane("YZ")
        .circle(0.009 * gs)
        .extrude(0.068)
        .translate((-fp_x * 0.5, 0.0, 0.018 * gs))
    )
    return hump.cut(groove)


# Grip meshes are authored at the LOCAL origin (base at z=0). The grip's seat
# point goes in the FIXED joint origin (parent frame) and the visual is placed
# at the local origin, so the child link frame's (0,0,0) sits on the grip base
# (satisfies the flat articulation-origin baseline) and the parent point lands
# on the boss it bolts onto.
def _emit_grip_knob_dtote(model, r, body, mats, *, assets) -> None:
    knob_seat = (r.knob_x, 0.0, r.sole_top_z)
    knob = model.part("front_knob")
    knob.visual(
        mesh_from_cadquery(_front_knob(r), "front_knob", assets=assets),
        origin=Origin(), material=mats["wood"], name="knob", material_class_id="wood.polished_varnished",
    )
    model.articulation(
        "body_to_front_knob", ArticulationType.FIXED,
        parent=body, child=knob, origin=Origin(xyz=knob_seat),
    )
    tote_seat = (r.tote_x, 0.0, r.sole_top_z)
    tote = model.part("rear_tote")
    tote.visual(
        mesh_from_cadquery(_rear_tote_open(r), "rear_tote", assets=assets),
        origin=Origin(), material=mats["wood"], name="tote", material_class_id="wood.polished_varnished",
    )
    model.articulation(
        "body_to_rear_tote", ArticulationType.FIXED,
        parent=body, child=tote, origin=Origin(xyz=tote_seat),
    )


def _emit_grip_horn_ringtote(model, r, body, mats, *, assets) -> None:
    horn_seat = (r.knob_x, 0.0, r.sole_top_z)
    horn = model.part("front_horn")
    horn.visual(
        mesh_from_geometry(_front_horn_geom(r), "front_horn"),
        origin=Origin(), material=mats["wood"], name="horn", material_class_id="wood.polished_varnished",
    )
    model.articulation(
        "body_to_front_horn", ArticulationType.FIXED,
        parent=body, child=horn, origin=Origin(xyz=horn_seat),
    )
    tote_seat = (r.tote_x, 0.0, r.sole_top_z)
    tote = model.part("rear_tote")
    tote.visual(
        mesh_from_cadquery(_rear_tote_ring(r), "rear_tote", assets=assets),
        origin=Origin(), material=mats["wood"], name="tote", material_class_id="wood.polished_varnished",
    )
    model.articulation(
        "body_to_rear_tote", ArticulationType.FIXED,
        parent=body, child=tote, origin=Origin(xyz=tote_seat),
    )


def _emit_grip_palm(model, r, body, mats, *, assets) -> None:
    rest_seat = (r.tote_x - 0.004, 0.0, r.sole_top_z)
    rest = model.part("palm_rest")
    rest.visual(
        mesh_from_cadquery(_palm_rest(r), "palm_rest", assets=assets),
        origin=Origin(), material=mats["wood"], name="hump", material_class_id="wood.polished_varnished",
    )
    model.articulation(
        "body_to_palm_rest", ArticulationType.FIXED,
        parent=body, child=rest, origin=Origin(xyz=rest_seat),
    )


_GRIP_EMITTERS = {
    "knob_plus_Dtote": _emit_grip_knob_dtote,
    "horn_plus_ringtote": _emit_grip_horn_ringtote,
    "single_palm_hump": _emit_grip_palm,
}


# ===========================================================================
# Build
# ===========================================================================
def _build_body(model, r, mats, *, assets):
    body_fn, frog_fn = _BODY_BUILDERS[r.body_silhouette]
    body = model.part("plane_body")
    body.visual(
        mesh_from_cadquery(body_fn(r), "plane_body", assets=assets),
        material=mats["body"], name="casting", material_class_id="metal.paint_coated",
    )
    sole_edge = (
        cq.Workplane("XY")
        .box(r.body_len - 0.006, r.body_width + 0.0006, 0.0015, centered=(True, True, False))
        .edges("|Z")
        .fillet(min(0.009, r.body_width * 0.14))
    )
    body.visual(
        mesh_from_cadquery(sole_edge, "sole_edge", assets=assets),
        material=mats["sole_edge"], name="sole_edge", material_class_id="metal.steel_bare",
    )
    body.visual(
        mesh_from_cadquery(frog_fn(r), "frog", assets=assets),
        material=mats["body"], name="frog", material_class_id="metal.paint_coated",
    )
    # single_palm_hump widens the heel boss (no toe knob boss is needed; the
    # palm rest seats on the widened heel).
    if r.grip == "single_palm_hump":
        boss = _palm_heel_boss(r)
        if boss is not None:
            body.visual(
                mesh_from_cadquery(boss, "palm_heel_boss", assets=assets),
                material=mats["body"], name="palm_heel_boss", material_class_id="metal.paint_coated",
            )
    # Depth-wheel stud (shared body hardware visual; CONTINUOUS wheel rides it).
    # The stud is coaxial with the wheel at the wheel center and extends down the
    # bed into the body casting.
    body.visual(
        mesh_from_cadquery(
            _depth_stud(r, r.bed_pt(r.depth_u, -0.0085)), "depth_stud", assets=assets
        ),
        material=mats["steel"], name="depth_stud", material_class_id="metal.steel_bare",
    )
    return body


def _emit_shared_spine(model, r, body, mats, *, assets):
    lat = model.part("lateral_lever")
    lat.visual(
        mesh_from_cadquery(_lateral_lever(r), "lateral_lever", assets=assets),
        origin=Origin(), material=mats["steel"], name="lever", material_class_id="metal.steel_bare",
    )
    model.articulation(
        "lateral_adjust", ArticulationType.REVOLUTE,
        parent=body, child=lat,
        origin=Origin(xyz=r.bed_pt(r.lat_pivot_u, 0.003)),
        axis=r.bed_normal,
        motion_limits=MotionLimits(
            effort=2.0, velocity=3.0, lower=r.lateral_lower, upper=r.lateral_upper
        ),
    )

    wheel = model.part("depth_wheel")
    wheel.visual(
        mesh_from_cadquery(_depth_wheel(r), "depth_wheel", assets=assets),
        origin=Origin(), material=mats["brass"], name="wheel", material_class_id=("metal.brass_polished" if r.palette_style in {"japanned_cast_iron", "bare_steel_sole", "brass_adjusters", "boxwood_tote"} else "metal.chrome_polished"),
    )
    model.articulation(
        "depth_adjust", ArticulationType.CONTINUOUS,
        parent=body, child=wheel,
        origin=Origin(xyz=r.bed_pt(r.depth_u, -0.0085)),
        axis=r.bed_up,
        motion_limits=MotionLimits(effort=1.0, velocity=6.0),
    )


def build_hand_plane(
    config: HandPlaneConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"hand_plane_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)

    # Cutting iron (FIXED, bedded on the frog). post_hole only for capnut_post.
    # The iron mesh is authored in body-world; seat the FIXED joint at the iron's
    # mid-bed point so the child frame origin lands on it.
    _emit_bodyworld_fixed(
        model, body, "cutting_iron",
        mesh_from_cadquery(
            _cutting_iron(r, post_hole_u=_clamp_post_hole_u(r)), "cutting_iron", assets=assets
        ),
        mats["steel"], "iron", "body_to_cutting_iron",
        r.bed_pt(min(0.060, r.body_len * 0.25), 0.0015),
    )

    _CLAMP_EMITTERS[r.blade_clamp](model, r, body, mats, assets=assets)
    _GRIP_EMITTERS[r.grip](model, r, body, mats, assets=assets)
    _emit_shared_spine(model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hand_plane(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_hand_plane(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_hand_plane_tests(
    object_model: ArticulatedObject,
    config: HandPlaneConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("plane_body")
    iron = object_model.get_part("cutting_iron")

    # ---- Captured / bedded / seated overlap allowances (element-scoped). ----
    ctx.allow_overlap(
        iron, body, elem_a="iron", elem_b="frog",
        reason="The cutting iron is bedded flat against the cast frog plate.",
    )
    ctx.allow_overlap(
        iron, body, elem_a="iron", elem_b="casting",
        reason="The bedded iron shares the body's iron slot opening.",
    )

    # blade_clamp captured overlaps + topology.
    if r.blade_clamp == "levercap_flipcam":
        cap = object_model.get_part("lever_cap")
        cam = object_model.get_part("cam_lever")
        ctx.allow_overlap(cap, body, elem_a="cap", elem_b="frog",
                          reason="The lever cap's lower end seats onto the frog/iron seat.")
        ctx.allow_overlap(cap, body, elem_a="cap", elem_b="casting",
                          reason="The lever cap sits within the body's iron slot.")
        ctx.allow_overlap(cap, body, elem_a="cap", elem_b="cap_screw",
                          reason="The cap screw head bears down onto the lever-cap spine.")
        ctx.allow_overlap(iron, body, elem_a="iron", elem_b="cap_screw",
                          reason="The cap screw shaft passes up through the iron slot to the lever cap.")
        ctx.allow_overlap(cap, iron, elem_a="cap", elem_b="iron",
                          reason="The lever cap clamps flat onto the cutting iron.")
        ctx.allow_overlap(cam, cap, elem_a="cam", elem_b="cap",
                          reason="The cam lever's boss is captured on the lever-cap pin; its finger lies on the spine.")
        ctx.allow_overlap(cam, iron, elem_a="cam", elem_b="iron",
                          reason="The cam bears down onto the iron through the lever cap when clamped.")
        ctx.allow_overlap(cam, body, elem_a="cam", elem_b="cap_screw",
                          reason="The cam finger lies over the cap screw head when clamped flat.")
        ctx.allow_overlap(cam, body, elem_a="cam", elem_b="casting",
                          reason="The cam finger lies in the body's iron slot opening when clamped.")
    elif r.blade_clamp == "crossbar_thumbscrew":
        bar = object_model.get_part("clamp_bar")
        screw = object_model.get_part("thumbscrew")
        for i in range(2):
            ctx.allow_overlap(iron, body, elem_a="iron", elem_b=f"clamp_boss_{i}",
                              reason="The iron passes through the slot where the clamp boss anchors the bar.")
            ctx.allow_overlap(bar, body, elem_a="bar", elem_b=f"clamp_boss_{i}",
                              reason="The clamp bar end hole captures the boss pin on the slot wall.")
        ctx.allow_overlap(bar, iron, elem_a="bar", elem_b="iron",
                          reason="The clamp bar sits flat on the chipbreaker to clamp the iron.")
        ctx.allow_overlap(screw, bar, elem_a="screw", elem_b="bar",
                          reason="The thumbscrew washer face bears down on the clamp bar top.")
        ctx.allow_overlap(screw, body, elem_a="screw", elem_b="thumbscrew_stud",
                          reason="The thumbscrew bore rides on the steel mounting stud.")
        for i in range(2):
            ctx.allow_overlap(screw, body, elem_a="screw", elem_b=f"clamp_boss_{i}",
                              reason="The thumbscrew disc edge overhangs the cast clamp boss beside the stud.")
        ctx.allow_overlap(iron, body, elem_a="iron", elem_b="thumbscrew_stud",
                          reason="The thumbscrew stud passes up through the iron slot.")
    else:  # capnut_post
        cap_nut = object_model.get_part("cap_nut")
        ctx.allow_overlap(cap_nut, iron, elem_a="nut", elem_b="iron",
                          reason="The cap nut's bottom face bears on the chipbreaker to clamp the iron stack.")
        ctx.allow_overlap(cap_nut, body, elem_a="nut", elem_b="cap_post",
                          reason="The cap nut's bore threads onto the steel cap post (captured fit).")
        ctx.allow_overlap(iron, body, elem_a="iron", elem_b="cap_post",
                          reason="The cap post passes up through the iron's post hole.")
        ctx.allow_overlap(cap_nut, body, elem_a="nut", elem_b="frog",
                          reason="The cap nut sits partly within the body's iron slot opening above the frog.")
        ctx.allow_overlap(cap_nut, body, elem_a="nut", elem_b="casting",
                          reason="The cap nut sits within the body's iron slot opening.")

    # grip captured overlaps.
    if r.grip == "knob_plus_Dtote":
        knob = object_model.get_part("front_knob")
        tote = object_model.get_part("rear_tote")
        ctx.allow_overlap(knob, body, elem_a="knob", elem_b="casting",
                          reason="The front knob base is seated/bolted onto the toe boss of the sole.")
        ctx.allow_overlap(tote, body, elem_a="tote", elem_b="casting",
                          reason="The rear tote foot is seated/bolted onto the heel boss of the sole.")
        ctx.allow_overlap(tote, iron, elem_a="tote", elem_b="iron",
                          reason="The tote's lower throat sits just behind the bedded iron.")
    elif r.grip == "horn_plus_ringtote":
        horn = object_model.get_part("front_horn")
        tote = object_model.get_part("rear_tote")
        ctx.allow_overlap(horn, body, elem_a="horn", elem_b="casting",
                          reason="The front horn base is seated onto the toe boss of the sole.")
        ctx.allow_overlap(tote, body, elem_a="tote", elem_b="casting",
                          reason="The rear tote foot is seated onto the heel boss of the sole.")
        ctx.allow_overlap(tote, iron, elem_a="tote", elem_b="iron",
                          reason="The tote's lower throat sits just behind the bedded iron.")
    else:  # single_palm_hump
        rest = object_model.get_part("palm_rest")
        wheel_p = object_model.get_part("depth_wheel")
        ctx.allow_overlap(rest, body, elem_a="hump", elem_b="casting",
                          reason="The palm rest seats onto the widened heel boss of the sole.")
        ctx.allow_overlap(rest, body, elem_a="hump", elem_b="palm_heel_boss",
                          reason="The palm rest seats onto the widened heel boss of the sole.")
        ctx.allow_overlap(rest, body, elem_a="hump", elem_b="frog",
                          reason="The palm rest's front throat sits over the frog bed.")
        ctx.allow_overlap(rest, body, elem_a="hump", elem_b="depth_stud",
                          reason="The palm rest's front throat covers the depth-wheel stud under the heel.")
        ctx.allow_overlap(rest, iron, elem_a="hump", elem_b="iron",
                          reason="The palm rest's lower throat sits just behind the bedded iron.")
        ctx.allow_overlap(rest, wheel_p, elem_a="hump", elem_b="wheel",
                          reason="The depth wheel tucks under the palm rest's front throat.")

    # shared spine captured overlaps.
    lat = object_model.get_part("lateral_lever")
    wheel = object_model.get_part("depth_wheel")
    ctx.allow_overlap(lat, iron, elem_a="lever", elem_b="iron",
                      reason="The lateral lever's boss is riveted into the iron; its stem slides on the iron face.")
    # On a short body the lateral lever and the up-the-bed clamp hardware both
    # ride the same iron-face region and can graze each other (captured fit).
    if r.blade_clamp == "levercap_flipcam":
        ctx.allow_overlap(lat, body, elem_a="lever", elem_b="cap_screw",
                          reason="The lateral lever stem grazes the cap screw shaft on the iron face.")
    elif r.blade_clamp == "crossbar_thumbscrew":
        ctx.allow_overlap(lat, body, elem_a="lever", elem_b="thumbscrew_stud",
                          reason="The lateral lever stem and the thumbscrew stud share the iron-face region.")
        for i in range(2):
            ctx.allow_overlap(lat, body, elem_a="lever", elem_b=f"clamp_boss_{i}",
                              reason="The lateral lever stem grazes the cast clamp boss on the iron face.")
    elif r.blade_clamp == "capnut_post":
        ctx.allow_overlap(lat, body, elem_a="lever", elem_b="cap_post",
                          reason="The lateral lever stem grazes the cap post on the iron face.")
    ctx.allow_overlap(wheel, body, elem_a="wheel", elem_b="frog",
                      reason="The brass depth wheel is a captured rotor seated against the frog on its stud.")
    ctx.allow_overlap(wheel, body, elem_a="wheel", elem_b="depth_stud",
                      reason="The depth wheel's bore rides on the steel mounting stud.")
    ctx.allow_overlap(wheel, body, elem_a="wheel", elem_b="casting",
                      reason="The depth wheel tucks into the body's iron slot opening.")
    ctx.allow_overlap(wheel, iron, elem_a="wheel", elem_b="iron",
                      reason="The depth wheel's rim engages the iron's adjuster slot from below.")
    # On a short body the depth wheel sits close to the up-the-bed clamp hardware.
    if r.blade_clamp == "levercap_flipcam":
        ctx.allow_overlap(wheel, body, elem_a="wheel", elem_b="cap_screw",
                          reason="The depth wheel sits beside the cap screw shaft under the iron.")
    elif r.blade_clamp == "crossbar_thumbscrew":
        ctx.allow_overlap(wheel, body, elem_a="wheel", elem_b="thumbscrew_stud",
                          reason="The depth wheel sits beside the thumbscrew stud under the iron.")
    elif r.blade_clamp == "capnut_post":
        ctx.allow_overlap(wheel, body, elem_a="wheel", elem_b="cap_post",
                          reason="The depth wheel sits beside the cap post under the iron.")

    # ---- Baseline checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root + shared FIXED iron. ----
    roots = object_model.root_parts()
    ctx.check(
        "plane_body is the single root",
        len(roots) == 1 and roots[0].name == "plane_body",
        details=f"roots={[p.name for p in roots]}",
    )
    iron_joint = object_model.get_articulation("body_to_cutting_iron")
    ctx.check(
        "iron is FIXED-bedded to the body",
        iron_joint.articulation_type == ArticulationType.FIXED,
        details=str(iron_joint.articulation_type),
    )

    part_names = {p.name for p in object_model.parts}
    articulation_names = {a.name for a in object_model.articulations}

    # ---- PRIMARY blade-clamp joint topology (differs per candidate). ----
    if r.blade_clamp == "levercap_flipcam":
        ctx.check("lever_cap + cam_lever present",
                  {"lever_cap", "cam_lever"} <= part_names, details=str(sorted(part_names)))
        cam_joint = object_model.get_articulation("lever_cap_cam")
        ctx.check(
            "lever_cap_cam is REVOLUTE about -Y, parent=lever_cap",
            cam_joint.articulation_type == ArticulationType.REVOLUTE
            and abs(cam_joint.axis[1]) > 0.99 and abs(cam_joint.axis[0]) < 0.01
            and cam_joint.parent == "lever_cap",
            details=f"type={cam_joint.articulation_type} axis={tuple(cam_joint.axis)} parent={cam_joint.parent}",
        )
        ctx.check("no thumbscrew/cap_nut joints for levercap",
                  not ({"thumbscrew", "cap_nut_spin"} & articulation_names),
                  details=str(sorted(articulation_names)))
    elif r.blade_clamp == "crossbar_thumbscrew":
        ctx.check("clamp_bar + thumbscrew present",
                  {"clamp_bar", "thumbscrew"} <= part_names, details=str(sorted(part_names)))
        sj = object_model.get_articulation("thumbscrew")
        ctx.check(
            "thumbscrew is REVOLUTE about the bed normal, parent=body",
            sj.articulation_type == ArticulationType.REVOLUTE
            and sj.axis[0] > 0.2 and sj.axis[2] > 0.2 and abs(sj.axis[1]) < 0.01
            and sj.parent == "plane_body",
            details=f"type={sj.articulation_type} axis={tuple(sj.axis)} parent={sj.parent}",
        )
        ctx.check("no lever_cap cam / cap_nut for thumbscrew",
                  not ({"lever_cap_cam", "cap_nut_spin"} & articulation_names)
                  and not ({"lever_cap", "cam_lever"} & part_names),
                  details=str(sorted(articulation_names)))
    else:  # capnut_post
        ctx.check("cap_nut present", "cap_nut" in part_names, details=str(sorted(part_names)))
        nj = object_model.get_articulation("cap_nut_spin")
        ctx.check(
            "cap_nut_spin is CONTINUOUS about the bed normal, parent=body",
            nj.articulation_type == ArticulationType.CONTINUOUS
            and nj.axis[0] > 0.2 and nj.axis[2] > 0.2 and abs(nj.axis[1]) < 0.01
            and nj.parent == "plane_body",
            details=f"type={nj.articulation_type} axis={tuple(nj.axis)} parent={nj.parent}",
        )
        ctx.check("no lever_cap cam / thumbscrew for capnut",
                  not ({"lever_cap_cam", "thumbscrew"} & articulation_names)
                  and not ({"lever_cap", "cam_lever"} & part_names),
                  details=str(sorted(articulation_names)))

    # ---- grip topology. ----
    if r.grip == "knob_plus_Dtote":
        ctx.check("knob + tote present", {"front_knob", "rear_tote"} <= part_names,
                  details=str(sorted(part_names)))
    elif r.grip == "horn_plus_ringtote":
        ctx.check("horn + tote present", {"front_horn", "rear_tote"} <= part_names,
                  details=str(sorted(part_names)))
    else:  # single_palm_hump
        ctx.check("only palm_rest grip (no front knob/horn/tote)",
                  "palm_rest" in part_names
                  and not ({"front_knob", "front_horn", "rear_tote"} & part_names),
                  details=str(sorted(part_names)))

    # ---- Shared SECONDARY / TERTIARY spine (all candidates). ----
    lat_joint = object_model.get_articulation("lateral_adjust")
    ctx.check(
        "lateral_adjust is REVOLUTE about the bed normal",
        lat_joint.articulation_type == ArticulationType.REVOLUTE
        and lat_joint.axis[0] > 0.2 and lat_joint.axis[2] > 0.2 and abs(lat_joint.axis[1]) < 0.01,
        details=f"type={lat_joint.articulation_type} axis={tuple(lat_joint.axis)}",
    )
    depth_joint = object_model.get_articulation("depth_adjust")
    ctx.check(
        "depth_adjust is CONTINUOUS",
        depth_joint.articulation_type == ArticulationType.CONTINUOUS,
        details=str(depth_joint.articulation_type),
    )

    # ---- Identity: iron is bedded at an incline reaching the mouth. ----
    def cy(aabb):
        return 0.5 * (aabb[0][1] + aabb[1][1])

    iron_aabb = ctx.part_world_aabb(iron)
    if iron_aabb is not None:
        ctx.check(
            "cutting iron reaches the mouth/sole",
            iron_aabb[0][2] < r.sole_top_z + 0.005,
            details=str(iron_aabb),
        )
        ctx.check(
            "iron rises from the mouth toward the heel",
            iron_aabb[0][0] < r.mouth_x + 0.002,
            details=str(iron_aabb),
        )

    # ---- Connectivity / seating proofs. ----
    ctx.expect_contact(iron, body, contact_tol=0.003, name="iron bedded on frog")
    ctx.expect_contact(lat, iron, contact_tol=0.003, name="lateral lever rides on iron")
    ctx.expect_contact(wheel, body, contact_tol=0.003, name="depth wheel mounted on stud")

    # ---- PRIMARY mechanism actuates correctly & stays seated. ----
    if r.blade_clamp == "levercap_flipcam":
        cam = object_model.get_part("cam_lever")
        cam_joint = object_model.get_articulation("lever_cap_cam")
        with ctx.pose({cam_joint: 0.0}):
            rest_top = ctx.part_world_aabb(cam)[1][2]
        with ctx.pose({cam_joint: r.cam_upper}):
            lifted_top = ctx.part_world_aabb(cam)[1][2]
        ctx.check(
            "flipping the cam lever raises it",
            lifted_top > rest_top + 0.005,
            details=f"rest_top={rest_top}, lifted_top={lifted_top}",
        )
    elif r.blade_clamp == "crossbar_thumbscrew":
        screw = object_model.get_part("thumbscrew")
        sj = object_model.get_articulation("thumbscrew")
        with ctx.pose({sj: 0.0}):
            rest_z = ctx.part_world_aabb(screw)[1][2]
        with ctx.pose({sj: math.pi}):
            turned_z = ctx.part_world_aabb(screw)[1][2]
        ctx.check(
            "thumbscrew stays at the same height when turned",
            abs(turned_z - rest_z) < 0.006,
            details=f"rest_top={rest_z}, turned_top={turned_z}",
        )
    else:  # capnut_post
        cap_nut = object_model.get_part("cap_nut")
        nj = object_model.get_articulation("cap_nut_spin")
        with ctx.pose({nj: 0.0}):
            c0 = ctx.part_world_position(cap_nut)
        with ctx.pose({nj: math.pi}):
            cpi = ctx.part_world_position(cap_nut)
        ctx.check(
            "cap nut stays in place when spun (rotates, no translation)",
            c0 is not None and cpi is not None
            and all(abs(a - b) < 0.003 for a, b in zip(c0, cpi)),
            details=f"q0={c0}, q_pi={cpi}",
        )

    # ---- SECONDARY: lateral lever rocks sideways and stays on the iron. ----
    with ctx.pose({lat_joint: 0.0}):
        lat_cy0 = cy(ctx.part_world_aabb(lat))
    with ctx.pose({lat_joint: r.lateral_upper}):
        lat_cy1 = cy(ctx.part_world_aabb(lat))
        ctx.expect_contact(lat, iron, contact_tol=0.003, name="lateral lever stays on iron when rocked")
    ctx.check(
        "rocking the lateral lever shifts it sideways",
        abs(lat_cy1 - lat_cy0) > 0.003,
        details=f"cy0={lat_cy0}, cy1={lat_cy1}",
    )

    return ctx.report()


__all__ = (
    "HandPlaneConfig",
    "ResolvedHandPlaneConfig",
    "build_hand_plane",
    "build_seeded_hand_plane",
    "config_from_seed",
    "resolve_config",
    "run_hand_plane_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
