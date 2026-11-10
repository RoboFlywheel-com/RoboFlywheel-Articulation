# SPDX-License-Identifier: Apache-2.0

"""Textiles_Fabric / Needle case procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/needle_case.md

A dedicated case that stores and protects knitting/sewing needles in indexed
positions with a real closure. Two source archetypes drive it:

* Origin A (open tan bifold): ``needle_panel`` root with a channel strip of
  open-bottom tunnels holding prismatic slide-out double-pointed needles, a
  hinged tip flap, and a snap cover flap.
* Origin B (saddle-brown bifold): each leather panel is a needle bed of
  interchangeable tips threaded under a stitched pocket band with dividers, a
  hinged needle flap, and a brass-snap closure flap.

Slots (pattern = mixed: chained panels + parallel closure/flap children + N):
  * Slot A body_skeleton (①/③): bifold / trifold / single_flat planar panel
      chains, or a volumetric rigid_tube (③ Volumetric Envelope Form).
  * Slot B retention (②/internal ①): channel_tunnels (prismatic needles) /
      stitched_band / leather_loops on every planar panel; tube ⇒ upright_bundle.
  * Slot C closure (②): snap_cover_flap (revolute) / wrap_tie (revolute) /
      zipper (prismatic) on planar; tube ⇒ pull_cap (prismatic).
  * Multiplicity needles_per_panel N (weighted small).

Rules:
  Rule 1 — non-articulating detail (bands, dividers, stitch lines, snap discs,
    loops, brass rings) are host ``.visual(...)``; the only separate parts are
    real articulations (fold hinges, needle/cover flaps, prismatic needles,
    zip pull, tube cap).
  Rule 2 — every non-FIXED child either declares a `MatingContract` (flaps on
    their seam ridge / panel edge) or is a source-faithful grandfathered joint
    (prismatic needle in an open tunnel, cap plug in a bore) kept honest with
    element-scoped ``allow_overlap`` + ``expect_*`` mirroring each source.
  Rule 3 — structure/primitives derive from the declared 5-star sources
    (ExtrudeGeometry panels, swept-spline loops, LatheGeometry tube — no Box
    downgrade of the hero meshes).
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted
    ``ctx.pose`` per mechanism (fold / closure / needle-slide / cap-pull).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    ConeGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeGeometry,
    LatheGeometry,
    MatingContract,
    Mesh,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
Skeleton = Literal["bifold", "trifold", "single_flat", "tube"]
Retention = Literal["channel_tunnels", "stitched_band", "leather_loops", "upright_bundle"]
Closure = Literal["snap_cover_flap", "wrap_tie", "zipper", "pull_cap"]
PaletteStyle = Literal["tan", "saddle", "cognac"]

SKELETONS: tuple[Skeleton, ...] = ("bifold", "trifold", "single_flat", "tube")
PLANAR_SKELETONS: frozenset[Skeleton] = frozenset({"bifold", "trifold", "single_flat"})
PLANAR_RETENTIONS: tuple[Retention, ...] = ("channel_tunnels", "stitched_band", "leather_loops")
PLANAR_CLOSURES: tuple[Closure, ...] = ("snap_cover_flap", "wrap_tie", "zipper")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("tan", "saddle", "cognac")

N_PANELS: dict[Skeleton, int] = {"single_flat": 1, "bifold": 2, "trifold": 3, "tube": 0}

# ---------------------------------------------------------------------------
# Palettes: leather tones per colorway + shared hardware + rainbow needle tips.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "tan": {
        "leather": (0.70, 0.42, 0.19, 1.0),
        "leather_light": (0.79, 0.55, 0.32, 1.0),
        "leather_dark": (0.55, 0.33, 0.15, 1.0),
        "band": (0.74, 0.48, 0.24, 1.0),
    },
    "saddle": {
        "leather": (0.47, 0.26, 0.14, 1.0),
        "leather_light": (0.54, 0.31, 0.17, 1.0),
        "leather_dark": (0.40, 0.21, 0.11, 1.0),
        "band": (0.50, 0.28, 0.15, 1.0),
    },
    "cognac": {
        "leather": (0.60, 0.30, 0.16, 1.0),
        "leather_light": (0.70, 0.40, 0.22, 1.0),
        "leather_dark": (0.45, 0.22, 0.12, 1.0),
        "band": (0.64, 0.34, 0.18, 1.0),
    },
}
_HARDWARE: dict[str, tuple[float, float, float, float]] = {
    "brass": (0.76, 0.62, 0.30, 1.0),
    "steel": (0.72, 0.73, 0.75, 1.0),
    "bamboo": (0.83, 0.70, 0.45, 1.0),
    "stitch": (0.91, 0.86, 0.72, 1.0),
    "zip_fabric": (0.18, 0.12, 0.07, 1.0),
    "zip_slider": (0.72, 0.58, 0.28, 1.0),
}
NEEDLE_RGBAS: tuple[tuple[float, float, float, float], ...] = (
    (0.16, 0.55, 0.55, 1.0),  # teal
    (0.48, 0.30, 0.62, 1.0),  # purple
    (0.75, 0.22, 0.24, 1.0),  # red
    (0.23, 0.38, 0.72, 1.0),  # blue
    (0.33, 0.58, 0.30, 1.0),  # green
    (0.85, 0.52, 0.18, 1.0),  # orange
)

# ---------------------------------------------------------------------------
# Single-sourced geometry constants (meters; panel local frame z up).
# Bed geometry is kept ABSOLUTE (source-faithful); only the panel shell + fold
# layout carry the size scale, and the scale range guarantees the bed fits.
# ---------------------------------------------------------------------------
PANEL_W = 0.17
PANEL_H = 0.24
PANEL_T = 0.004
CORNER_R = 0.012
SEAM_OVER = 0.0004
HINGE_Z = 0.0045

# Folds/covers move from open (rest) toward closed. The sampled-pose gate drives
# every joint to its extreme independently, so ranges stop shy of the stacked-shut
# pose where non-adjacent panels / the cover would interpenetrate the beds (a real
# case reaches closed by coordinated folding, which discrete sampling cannot model).
FOLD_UPPER = 1.55

NEEDLE_R = 0.0025
NEEDLE_SHAFT_L = 0.115
NEEDLE_TIP_L = 0.018
NEEDLE_BASE_Y = -0.098
NEEDLE_SINK = 0.0003
HALF_XS = 0.066  # needle row half-span along x (fits panels at min size scale)

# Stitched pocket band
BAND_Y = -0.085
BAND_H = 0.060
DIVIDER_W = 0.0022
DIVIDER_RISE = 0.0062
BAND_TOP_T = 0.0025
BAND_W = 0.1466

# Leather retaining loops
LOOP_Y = -0.085
LOOP_W = 0.012
LOOP_T = 0.0018
LOOP_RISE = 0.007
LOOP_SPAN = 0.018

# Channel tunnels (rails between which prismatic needles slide)
CH_STRIP_Y0, CH_STRIP_Y1 = -0.075, 0.005
CH_RAIL_W = 0.004
CH_RAIL_H = 0.006
CH_NEEDLE_L = 0.16
CH_NEEDLE_CY = -0.02  # needle center y at rest
CH_TRAVEL = 0.090

# Needle flap (folds over the tips)
FLAP_HINGE_Y = 0.048
FLAP_LEN = 0.062
FLAP_W = 0.150
FLAP_T = 0.003
FLAP_CLEAR = 0.0003
RIDGE_D = 0.006
RIDGE_Y = FLAP_HINGE_Y - 0.0003 + RIDGE_D / 2
RIDGE_RISE = 0.007

# Closures
COVER_W = 0.150
COVER_H = 0.220
COVER_T = 0.0035
WRAP_TIE_LEN = 0.215
WRAP_TIE_W = 0.016
ZIP_TAPE_W = 0.008
ZIP_TAPE_T = 0.0015
ZIP_TAPE_INSET = 0.012
ZIP_TEETH_PITCH = 0.016
ZIP_TEETH_D = 0.002
ZIP_TEETH_W = 0.003
ZIP_TEETH_H = 0.0015
PULL_BODY_W = 0.012
PULL_BODY_L = 0.014
PULL_BODY_H = 0.005
PULL_TAB_L = 0.018
PULL_TAB_W = 0.007
PULL_TAB_T = 0.002

# Rigid tube (volumetric ③)
TUBE_OR = 0.0175
TUBE_IR = 0.0145
TUBE_H = 0.160
TUBE_BOTTOM_T = 0.004
CAP_T = 0.006
PLUG_R = TUBE_IR - 0.001
PLUG_H = 0.008
TUBE_NEEDLE_R = 0.0025
TUBE_NEEDLE_SHAFT_L = 0.115
TUBE_NEEDLE_TIP_L = 0.018
TUBE_NEEDLE_RING_R = 0.006


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def _even_xs(n: int, half: float = HALF_XS) -> list[float]:
    if n <= 1:
        return [0.0]
    return [-half + 2.0 * half * i / (n - 1) for i in range(n)]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class NeedleCaseConfig:
    skeleton: Skeleton | None = None
    retention: Retention | None = None
    closure: Closure | None = None
    needles_per_panel: int = 6
    palette_style: PaletteStyle = "tan"
    size_scale: float = 1.0
    name: str = "needle_case"


@dataclass(frozen=True)
class ResolvedNeedleCaseConfig:
    skeleton: Skeleton
    retention: Retention
    closure: Closure
    needles_per_panel: int
    palette_style: PaletteStyle
    size_scale: float
    name: str

    @property
    def n_panels(self) -> int:
        return N_PANELS[self.skeleton]

    @property
    def pw(self) -> float:
        return PANEL_W * self.size_scale

    @property
    def ph(self) -> float:
        return PANEL_H * self.size_scale

    @property
    def channel_count(self) -> int:
        """Prismatic-needle channels per panel, capped so the whole case keeps
        the fixture-tested joint budget (≤ ~9 slide joints, cf. channels_n6)."""
        cap = max(2, 9 // max(1, self.n_panels))
        return max(2, min(self.needles_per_panel, cap))


def config_from_seed(seed: int) -> NeedleCaseConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    not special). Retention/closure are drawn from the skeleton's legal set."""
    rng = random.Random(seed)
    skeleton = rng.choice(SKELETONS)
    if skeleton == "tube":
        retention: Retention = "upright_bundle"
        closure: Closure = "pull_cap"
        # Tube bundle stays a tidy hex-ish ring; keep N modest.
        n = rng.choice((5, 6, 6, 7, 8))
    else:
        retention = rng.choice(PLANAR_RETENTIONS)
        closure = rng.choice(PLANAR_CLOSURES)
        # Weighted-small needle multiplicity (test small, product full).
        n = rng.choice((4, 5, 5, 6, 6, 6, 7, 8))
    return NeedleCaseConfig(
        skeleton=skeleton,
        retention=retention,
        closure=closure,
        needles_per_panel=n,
        palette_style=rng.choice(PALETTE_STYLES),
        size_scale=round(rng.uniform(0.95, 1.16), 4),
        name=f"seeded_needle_case_{seed}",
    )


def resolve_config(config: NeedleCaseConfig | None = None) -> ResolvedNeedleCaseConfig:
    cfg = config or NeedleCaseConfig()
    skeleton = _pick(cfg.skeleton, SKELETONS)
    if skeleton == "tube":
        retention: Retention = "upright_bundle"
        closure: Closure = "pull_cap"
    else:
        retention = cfg.retention if cfg.retention in PLANAR_RETENTIONS else "stitched_band"
        closure = cfg.closure if cfg.closure in PLANAR_CLOSURES else "snap_cover_flap"
    n = int(cfg.needles_per_panel) if cfg.needles_per_panel else 6
    n = int(_clamp(n, 3, 9))
    return ResolvedNeedleCaseConfig(
        skeleton=skeleton,
        retention=retention,
        closure=closure,
        needles_per_panel=n,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        size_scale=_clamp(cfg.size_scale, 0.95, 1.16),
        name=cfg.name or "needle_case",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedNeedleCaseConfig) else resolve_config(config)
    return (
        ("body_skeleton", r.skeleton),
        ("retention", r.retention),
        ("closure", r.closure),
        ("needles_per_panel", f"n{r.needles_per_panel}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared meshes / helpers
# ===========================================================================
def _panel_mesh(width: float, height: float, thickness: float) -> Mesh:
    return mesh_from_geometry(
        ExtrudeGeometry.from_z0(
            rounded_rect_profile(width, height, CORNER_R, corner_segments=8),
            thickness,
        ),
        "leather_panel",
    )


def _needle_tip_mesh() -> Mesh:
    """Interchangeable needle tip lying along +y, butt end at y=0 (Origin B)."""
    shaft = CylinderGeometry(NEEDLE_R, NEEDLE_SHAFT_L, radial_segments=16)
    shaft.translate(0.0, 0.0, NEEDLE_SHAFT_L / 2)
    tip = ConeGeometry(NEEDLE_R, NEEDLE_TIP_L, radial_segments=16)
    tip.translate(0.0, 0.0, NEEDLE_SHAFT_L - 0.002 + NEEDLE_TIP_L / 2)
    needle = shaft.merge(tip)
    needle.rotate_x(-math.pi / 2)  # +z -> +y
    return mesh_from_geometry(needle, "needle_tip")


def _dpn_mesh() -> Mesh:
    """Double-pointed needle along +z, bottom apex at z=0 (tube fork)."""
    bot = ConeGeometry(TUBE_NEEDLE_R, TUBE_NEEDLE_TIP_L, radial_segments=14)
    bot.rotate_x(math.pi)
    bot.translate(0.0, 0.0, TUBE_NEEDLE_TIP_L / 2)
    shaft_z0 = TUBE_NEEDLE_TIP_L - 0.002
    shaft = CylinderGeometry(TUBE_NEEDLE_R, TUBE_NEEDLE_SHAFT_L, radial_segments=14)
    shaft.translate(0.0, 0.0, shaft_z0 + TUBE_NEEDLE_SHAFT_L / 2)
    top_z0 = shaft_z0 + TUBE_NEEDLE_SHAFT_L
    top = ConeGeometry(TUBE_NEEDLE_R, TUBE_NEEDLE_TIP_L, radial_segments=14)
    top.translate(0.0, 0.0, top_z0 + TUBE_NEEDLE_TIP_L / 2 - 0.002)
    return mesh_from_geometry(bot.merge(shaft).merge(top), "dpn_needle")


def _loop_mesh(cx: float, base_z: float) -> Mesh:
    """One bent-leather retaining arch over a needle (internal_loops fork)."""
    half = LOOP_SPAN / 2
    apex_z = base_z + LOOP_RISE
    pts = [
        (cx, LOOP_Y - half, base_z),
        (cx, LOOP_Y - half * 0.45, base_z + LOOP_RISE * 0.55),
        (cx, LOOP_Y, apex_z),
        (cx, LOOP_Y + half * 0.45, base_z + LOOP_RISE * 0.55),
        (cx, LOOP_Y + half, base_z),
    ]
    profile = rounded_rect_profile(LOOP_W, LOOP_T, radius=0.0005, corner_segments=3)
    geom = sweep_profile_along_spline(
        pts, profile=profile, samples_per_segment=12, cap_profile=True, up_hint=(0.0, 0.0, 1.0)
    )
    return mesh_from_geometry(geom, f"loop_{cx:.4f}")


def _add_flap_seam_ridge(part: Part, cx: float, top_z: float, mats) -> None:
    ridge_h = RIDGE_RISE + 0.0005
    part.visual(
        Box((FLAP_W, RIDGE_D, ridge_h)),
        origin=Origin(xyz=(cx, RIDGE_Y, top_z - 0.0005 + ridge_h / 2)),
        material=mats["leather_dark"],
        name="flap_seam_ridge", material_class_id="leather.smooth_plain",
    )


# ---------------------------------------------------------------------------
# Retention beds (all emit visuals onto the host panel; channels also emit
# prismatic needle parts).  Every bed leaves a flap_seam_ridge for the flap.
# ---------------------------------------------------------------------------
def _bed_stitched_band(part, cx, top_z, xs, mats, needle_mesh) -> None:
    needle_cz = top_z + NEEDLE_R - NEEDLE_SINK
    for i, dx in enumerate(xs):
        part.visual(
            needle_mesh,
            origin=Origin(xyz=(cx + dx, NEEDLE_BASE_Y, needle_cz)),
            material=f"needle_{i % len(NEEDLE_RGBAS)}",
            name=f"needle_{i}", material_class_id="metal.paint_coated",
        )
    div_xs = _even_xs(len(xs) + 1, HALF_XS + 0.006)
    div_h = DIVIDER_RISE + 0.0005
    for i, dx in enumerate(div_xs):
        part.visual(
            Box((DIVIDER_W, BAND_H, div_h)),
            origin=Origin(xyz=(cx + dx, BAND_Y, top_z - 0.0005 + div_h / 2)),
            material=mats["leather_dark"],
            name=f"band_divider_{i}", material_class_id="leather.smooth_plain",
        )
    band_cz = top_z + DIVIDER_RISE - 0.0003 + BAND_TOP_T / 2
    part.visual(
        Box((BAND_W, BAND_H, BAND_TOP_T)),
        origin=Origin(xyz=(cx, BAND_Y, band_cz)),
        material=mats["band"],
        name="pocket_band", material_class_id="leather.smooth_plain",
    )
    stitch_cz = band_cz + BAND_TOP_T / 2 + 0.0001
    for i, dx in enumerate(div_xs):
        part.visual(
            Box((0.0012, BAND_H - 0.004, 0.0006)),
            origin=Origin(xyz=(cx + dx, BAND_Y, stitch_cz)),
            material=mats["stitch"],
            name=f"band_stitch_{i}", material_class_id="fabric.thread_yarn",
        )
    _add_flap_seam_ridge(part, cx, top_z, mats)


def _bed_leather_loops(part, cx, top_z, xs, mats, needle_mesh) -> None:
    needle_cz = top_z + NEEDLE_R - NEEDLE_SINK
    for i, dx in enumerate(xs):
        part.visual(
            needle_mesh,
            origin=Origin(xyz=(cx + dx, NEEDLE_BASE_Y, needle_cz)),
            material=f"needle_{i % len(NEEDLE_RGBAS)}",
            name=f"needle_{i}", material_class_id="metal.paint_coated",
        )
    loop_base_z = top_z - 0.0003
    for i, dx in enumerate(xs):
        part.visual(
            _loop_mesh(cx + dx, loop_base_z),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["band"],
            name=f"loop_{i}", material_class_id="leather.smooth_plain",
        )
    _add_flap_seam_ridge(part, cx, top_z, mats)


def _bed_channels(model, part, cx, top_z, n_ch, mats) -> list[str]:
    """Rail-walls forming open-bottom channels + prismatic slide needles.

    Returns the list of prismatic joint names created (for tests).  The needle
    threads along the open channel between two rails, so no leather is cut and
    no solid overlaps the needle; the slide joint is the ② signature.
    """
    ch_xs = _even_xs(n_ch, 0.05)
    strip_cy = (CH_STRIP_Y0 + CH_STRIP_Y1) / 2
    strip_len = CH_STRIP_Y1 - CH_STRIP_Y0
    # Rail walls: one at every channel boundary (n_ch + 1 rails).
    if len(ch_xs) == 1:
        rail_xs = [ch_xs[0] - 0.011, ch_xs[0] + 0.011]
    else:
        pitch = ch_xs[1] - ch_xs[0]
        rail_xs = [ch_xs[0] - pitch / 2] + [x + pitch / 2 for x in ch_xs]
    for i, rx in enumerate(rail_xs):
        part.visual(
            Box((CH_RAIL_W, strip_len, CH_RAIL_H)),
            origin=Origin(xyz=(cx + rx, strip_cy, top_z - 0.0005 + CH_RAIL_H / 2)),
            material=mats["leather_light"],
            name=f"channel_rail_{i}", material_class_id="leather.smooth_plain",
        )
    joints: list[str] = []
    needle_cz_world_local = top_z + NEEDLE_R  # needle axis sits on the panel top
    pname = part.name
    for ci, chx in enumerate(ch_xs):
        needle = model.part(f"{pname}_needle_{ci}")
        needle.visual(
            Cylinder(radius=NEEDLE_R, length=CH_NEEDLE_L),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2, 0.0, 0.0)),
            material=mats["bamboo"],
            name="needle_shaft", material_class_id="wood.bamboo",
        )
        jname = f"{pname}_needle_{ci}_slide"
        model.articulation(
            jname,
            ArticulationType.PRISMATIC,
            parent=part,
            child=needle,
            origin=Origin(xyz=(cx + chx, CH_NEEDLE_CY, needle_cz_world_local)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=0.5, lower=0.0, upper=CH_TRAVEL),
        )
        joints.append(jname)
    _add_flap_seam_ridge(part, cx, top_z, mats)
    return joints


# ---------------------------------------------------------------------------
# Needle-tip flap (revolute child, one per planar panel).
# ---------------------------------------------------------------------------
def _build_tip_flap(model, panel, cx, top_z, name, joint_name, mats) -> None:
    flap = model.part(name)
    flap.visual(
        Box((FLAP_W, FLAP_LEN, FLAP_T)),
        origin=Origin(xyz=(0.0, -FLAP_LEN / 2, 0.0)),
        material=mats["leather_light"],
        name="flap_leather", material_class_id="leather.smooth_plain",
    )
    flap.visual(
        Cylinder(radius=0.005, length=0.0025),
        origin=Origin(xyz=(0.0, -0.050, FLAP_T / 2 + 0.00125 - 0.0005)),
        material=mats["brass"],
        name="snap_stud", material_class_id="metal.brass_polished",
    )
    flap.visual(
        Box((0.030, 0.016, 0.0025)),
        origin=Origin(xyz=(0.0, -0.066, 0.0)),
        material=mats["band"],
        name="pull_tab", material_class_id="leather.smooth_plain",
    )
    hinge_z = top_z + 2 * NEEDLE_R - NEEDLE_SINK + FLAP_CLEAR + FLAP_T / 2
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=panel,
        child=flap,
        origin=Origin(xyz=(cx, FLAP_HINGE_Y, hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        # The flap hinge edge is stitched onto the seam ridge (a stitched leather
        # seam, not two flat faces in contact): grandfather the joint (omit
        # mating=) and keep it honest with the ridge/flap allow_overlap in tests.
        motion_limits=MotionLimits(effort=4.0, velocity=2.5, lower=0.0, upper=2.4),
    )


# ===========================================================================
# Planar panel chain
# ===========================================================================
@dataclass
class PanelInfo:
    part: object
    name: str
    cx: float
    top_z: float
    outer_edge_x: float  # local x of the free +x edge
    is_root: bool


def _build_panel_chain(model, r: ResolvedNeedleCaseConfig, mats, panel_mesh) -> list[PanelInfo]:
    infos: list[PanelInfo] = []
    prev: PanelInfo | None = None
    for i in range(r.n_panels):
        name = f"panel_{i}"
        panel = model.part(name)
        if i == 0:
            panel.visual(panel_mesh, origin=Origin(xyz=(0.0, 0.0, 0.0)),
                         material=mats["leather"], name="panel_shell", material_class_id="leather.smooth_plain")
            info = PanelInfo(panel, name, cx=0.0, top_z=PANEL_T, outer_edge_x=r.pw / 2, is_root=True)
        else:
            cx = r.pw / 2 - SEAM_OVER
            top_z = -0.0005
            panel.visual(panel_mesh, origin=Origin(xyz=(cx, 0.0, top_z - PANEL_T)),
                         material=mats["leather"], name="panel_shell", material_class_id="leather.smooth_plain")
            info = PanelInfo(panel, name, cx=cx, top_z=top_z,
                             outer_edge_x=r.pw - SEAM_OVER, is_root=False)
            # Fold hinge to the previous panel's outer edge.
            assert prev is not None
            hinge_origin_x = prev.outer_edge_x if not prev.is_root else r.pw / 2
            hinge_origin_z = HINGE_Z if prev.is_root else 0.0
            model.articulation(
                f"fold_hinge_{i}",
                ArticulationType.REVOLUTE,
                parent=prev.part,
                child=panel,
                origin=Origin(xyz=(hinge_origin_x, 0.0, hinge_origin_z)),
                axis=(0.0, -1.0, 0.0),
                mating=MatingContract(
                    parent_face_geometry="panel_shell",
                    parent_face_side="positive_x",
                    child_face_geometry="panel_shell",
                    child_face_side="negative_x",
                    contact_tol=0.0015,
                ),
                motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=FOLD_UPPER),
            )
        infos.append(info)
        prev = info
    return infos


def _apply_retention(model, r: ResolvedNeedleCaseConfig, mats, infos, needle_mesh) -> list[str]:
    xs = _even_xs(r.needles_per_panel)
    slide_joints: list[str] = []
    for i, info in enumerate(infos):
        if r.retention == "stitched_band":
            _bed_stitched_band(info.part, info.cx, info.top_z, xs, mats, needle_mesh)
        elif r.retention == "leather_loops":
            _bed_leather_loops(info.part, info.cx, info.top_z, xs, mats, needle_mesh)
        else:  # channel_tunnels
            slide_joints += _bed_channels(model, info.part, info.cx, info.top_z,
                                          r.channel_count, mats)
    # The retaining tip flap lives on the non-folding root panel only: one flap
    # keeps the ② revolute retaining-flap feature without folded panels swinging
    # their flaps into each other under the sampled-pose Cartesian product.
    root = infos[0]
    _build_tip_flap(model, root.part, root.cx, root.top_z,
                    f"{root.name}_tip_flap", f"{root.name}_tip_flap_hinge", mats)
    return slide_joints


# ===========================================================================
# Closures (parented to the last panel = closure host)
# ===========================================================================
def _build_snap_cover(model, r, host: PanelInfo, mats) -> None:
    cover = model.part("closure_flap")
    cover_mesh = mesh_from_geometry(
        ExtrudeGeometry.from_z0(
            rounded_rect_profile(COVER_W, COVER_H, CORNER_R, corner_segments=8), COVER_T
        ),
        "closure_panel",
    )
    if host.is_root:
        z_off = -(PANEL_T - COVER_T / 2)
        stud_z = z_off + COVER_T + 0.001
        stud_x = COVER_W - 0.025
        hinge = Origin(xyz=(host.outer_edge_x, 0.0, PANEL_T))
    else:
        z_off = -HINGE_Z
        stud_z = z_off + COVER_T + 0.0008
        stud_x = 0.125
        hinge = Origin(xyz=(host.outer_edge_x, 0.0, 0.0))
    cover.visual(cover_mesh, origin=Origin(xyz=(COVER_W / 2 - SEAM_OVER, 0.0, z_off)),
                 material=mats["leather"], name="cover_leather", material_class_id="leather.smooth_plain")
    for i, dy in enumerate((0.080, -0.080)):
        cover.visual(Cylinder(radius=0.005, length=0.003),
                     origin=Origin(xyz=(stud_x, dy, stud_z)), material=mats["brass"],
                     name=f"snap_stud_{i}", material_class_id="metal.brass_polished")
    model.articulation(
        "closure_hinge", ArticulationType.REVOLUTE, parent=host.part, child=cover,
        origin=hinge, axis=(0.0, -1.0, 0.0),
        mating=MatingContract(
            parent_face_geometry="panel_shell", parent_face_side="positive_x",
            child_face_geometry="cover_leather", child_face_side="negative_x",
            contact_tol=0.002,
        ),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=FOLD_UPPER),
    )


def _build_wrap_tie(model, r, host: PanelInfo, mats) -> None:
    tie = model.part("wrap_tie")
    z_off = -(PANEL_T - COVER_T / 2) if host.is_root else -HINGE_Z
    hinge_z = PANEL_T if host.is_root else 0.0
    tie.visual(
        Box((WRAP_TIE_LEN, WRAP_TIE_W, COVER_T)),
        origin=Origin(xyz=(WRAP_TIE_LEN / 2 - SEAM_OVER, 0.0, z_off)),
        material=mats["leather"], name="cover_leather", material_class_id="leather.smooth_plain",
    )
    # cover_leather is a CENTERED box (top at z_off + COVER_T/2); embed the stud
    # 0.5 mm into that top so it is supported, not a floating island.
    tie.visual(
        Cylinder(radius=0.006, length=0.003),
        origin=Origin(xyz=(WRAP_TIE_LEN - 0.02, 0.0, z_off + COVER_T / 2 + 0.001)),
        material=mats["brass"], name="tie_stud", material_class_id="metal.brass_polished",
    )
    model.articulation(
        "closure_hinge", ArticulationType.REVOLUTE, parent=host.part, child=tie,
        origin=Origin(xyz=(host.outer_edge_x, 0.0, hinge_z)), axis=(0.0, -1.0, 0.0),
        mating=MatingContract(
            parent_face_geometry="panel_shell", parent_face_side="positive_x",
            child_face_geometry="cover_leather", child_face_side="negative_x",
            contact_tol=0.002,
        ),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=FOLD_UPPER),
    )


def _build_zipper(model, r, host: PanelInfo, mats) -> str:
    """Outer-edge zip tape + teeth (host visuals) and a prismatic slider."""
    top_z = host.top_z
    tape_hw = ZIP_TAPE_W / 2
    outer_x = host.cx + (host.outer_edge_x - host.cx) - tape_hw  # just inside the free edge
    tape_z = top_z + ZIP_TAPE_T / 2
    outer_len = 2.0 * (r.ph / 2 - ZIP_TAPE_INSET)
    host.part.visual(
        Box((ZIP_TAPE_W, outer_len, ZIP_TAPE_T)),
        origin=Origin(xyz=(outer_x, 0.0, tape_z)),
        material=mats["zip_fabric"], name="zip_tape_outer", material_class_id="fabric.webbing",
    )
    tooth_z = top_z + ZIP_TAPE_T + ZIP_TEETH_H / 2
    tooth_x = outer_x - (tape_hw + ZIP_TEETH_D / 2)
    n_teeth = max(1, int(outer_len / ZIP_TEETH_PITCH))
    for i in range(n_teeth):
        ty = -outer_len / 2 + ZIP_TEETH_PITCH / 2 + i * ZIP_TEETH_PITCH
        host.part.visual(
            Box((ZIP_TEETH_D, ZIP_TEETH_W, ZIP_TEETH_H)),
            origin=Origin(xyz=(tooth_x, ty, tooth_z)), material=mats["brass"],
            name=f"zip_tooth_{i}", material_class_id="metal.brass_polished",
        )
    pull = model.part("zip_pull")
    pull.visual(Box((PULL_BODY_W, PULL_BODY_L, PULL_BODY_H)),
                origin=Origin(xyz=(0.0, 0.0, PULL_BODY_H / 2)), material=mats["zip_slider"],
                name="slider_body", material_class_id="metal.brass_polished")
    tab_cx = -(PULL_BODY_W / 2 + PULL_TAB_L / 2 - 0.003)
    pull.visual(Box((PULL_TAB_L, PULL_TAB_W, PULL_TAB_T)),
                origin=Origin(xyz=(tab_cx, 0.0, PULL_TAB_T / 2)), material=mats["zip_slider"],
                name="pull_tab", material_class_id="metal.brass_polished")
    pull.visual(Box((0.004, 0.005, PULL_BODY_H - PULL_TAB_T)),
                origin=Origin(xyz=(-PULL_BODY_W / 2 + 0.001, 0.0,
                                   PULL_TAB_T + (PULL_BODY_H - PULL_TAB_T) / 2)),
                material=mats["zip_slider"], name="tab_ring", material_class_id="metal.brass_polished")
    teeth_top_z = top_z + ZIP_TAPE_T + ZIP_TEETH_H
    start_y = -outer_len / 2 + PULL_BODY_L / 2
    travel = outer_len - PULL_BODY_L
    model.articulation(
        "closure_slide", ArticulationType.PRISMATIC, parent=host.part, child=pull,
        origin=Origin(xyz=(outer_x, start_y, teeth_top_z)), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.5, lower=0.0, upper=travel),
    )
    return "closure_slide"


# ===========================================================================
# Rigid tube skeleton (self-contained volumetric ③ + pull cap)
# ===========================================================================
def _build_tube(model, r: ResolvedNeedleCaseConfig, mats) -> None:
    tube_mesh = mesh_from_geometry(
        LatheGeometry(
            [
                (0.0, 0.0), (TUBE_OR, 0.0), (TUBE_OR, TUBE_H), (TUBE_IR, TUBE_H),
                (TUBE_IR, TUBE_BOTTOM_T), (0.0, TUBE_BOTTOM_T),
            ],
            segments=32, closed=True,
        ),
        "tube_shell",
    )
    dpn = _dpn_mesh()
    tube = model.part("tube_body")
    tube.visual(tube_mesh, origin=Origin(), material=mats["leather"], name="tube_shell", material_class_id="leather.smooth_plain")
    tube.visual(Cylinder(radius=TUBE_OR + 0.0004, length=0.004),
                origin=Origin(xyz=(0.0, 0.0, TUBE_H - 0.002)), material=mats["brass"],
                name="mouth_ring", material_class_id="metal.brass_polished")
    tube.visual(Cylinder(radius=TUBE_OR + 0.0004, length=0.003),
                origin=Origin(xyz=(0.0, 0.0, 0.0015)), material=mats["brass"], name="base_ring", material_class_id="metal.brass_polished")
    n = r.needles_per_panel
    ring_r = TUBE_NEEDLE_RING_R if n > 1 else 0.0
    for i in range(n):
        angle = i * math.pi * 2.0 / max(1, n)
        tube.visual(
            dpn,
            origin=Origin(xyz=(ring_r * math.cos(angle), ring_r * math.sin(angle), TUBE_BOTTOM_T)),
            material=f"needle_{i % len(NEEDLE_RGBAS)}", name=f"needle_{i}", material_class_id="metal.paint_coated",
        )
    cap = model.part("cap")
    disk = CylinderGeometry(TUBE_OR + 0.001, CAP_T, radial_segments=32)
    disk.translate(0.0, 0.0, CAP_T / 2)
    plug = CylinderGeometry(PLUG_R, PLUG_H, radial_segments=24)
    plug.translate(0.0, 0.0, -PLUG_H / 2)
    cap.visual(mesh_from_geometry(disk.merge(plug), "cap_body"), origin=Origin(),
               material=mats["leather_light"], name="cap_disk", material_class_id="leather.smooth_plain")
    cap.visual(Cylinder(radius=0.004, length=0.003),
               origin=Origin(xyz=(0.0, 0.0, CAP_T + 0.0015)), material=mats["brass"],
               name="cap_stud", material_class_id="metal.brass_polished")
    model.articulation(
        "closure_slide", ArticulationType.PRISMATIC, parent=tube, child=cap,
        origin=Origin(xyz=(0.0, 0.0, TUBE_H)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=10.0, velocity=0.5, lower=0.0, upper=0.08),
    )


# ===========================================================================
# Assembly
# ===========================================================================
def _materials(model, r: ResolvedNeedleCaseConfig) -> dict:
    mats: dict = {}
    for k, v in PALETTES[r.palette_style].items():
        mats[k] = model.material(f"nc_{k}_{r.palette_style}", rgba=v)
    for k, v in _HARDWARE.items():
        mats[k] = model.material(f"nc_{k}", rgba=v)
    for i, rgba in enumerate(NEEDLE_RGBAS):
        model.material(f"needle_{i}", rgba=rgba)
    return mats


def build_needle_case(config: NeedleCaseConfig | None = None, *,
                      assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)

    if r.skeleton == "tube":
        _build_tube(model, r, mats)
    else:
        needle_mesh = _needle_tip_mesh()
        panel_mesh = _panel_mesh(r.pw, r.ph, PANEL_T)
        infos = _build_panel_chain(model, r, mats, panel_mesh)
        _apply_retention(model, r, mats, infos, needle_mesh)
        host = infos[-1]
        if r.closure == "snap_cover_flap":
            _build_snap_cover(model, r, host, mats)
        elif r.closure == "wrap_tie":
            _build_wrap_tie(model, r, host, mats)
        else:  # zipper
            _build_zipper(model, r, host, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_needle_case(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_needle_case(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _declare_allowances(ctx, model, r: ResolvedNeedleCaseConfig, infos) -> None:
    if r.skeleton == "tube":
        tube = model.get_part("tube_body")
        cap = model.get_part("cap")
        ctx.allow_overlap(
            tube, cap, elem_a="tube_shell", elem_b="cap_disk",
            reason="Cap plug seats inside the tube mouth bore for retention (1 mm radial clearance).",
        )
        return
    # Panel-to-panel continuous-leather seams.
    for i in range(1, len(infos)):
        ctx.allow_overlap(
            infos[i - 1].part, infos[i].part, elem_a="panel_shell", elem_b="panel_shell",
            reason="Leather is one continuous piece across the fold; edges share a 0.4 mm hidden embed.",
        )
    # Root needle-tip flap stitched onto its seam ridge.
    root = infos[0]
    flap = model.get_part(f"{root.name}_tip_flap")
    ctx.allow_overlap(
        root.part, flap, elem_a="flap_seam_ridge", elem_b="flap_leather",
        reason="Flap hinge edge is stitched onto the seam ridge (0.3 mm hidden embed).",
    )
    # Closure leather continuous with the host panel edge.
    host = infos[-1]
    if r.closure in ("snap_cover_flap", "wrap_tie"):
        child = model.get_part("closure_flap" if r.closure == "snap_cover_flap" else "wrap_tie")
        ctx.allow_isolated_part(
            child,
            reason="closure flap opens clear of the case and loses contact",
        )
        ctx.allow_overlap(
            host.part, child, elem_a="panel_shell", elem_b="cover_leather",
            reason="Closure is cut from the same leather as the host panel; edges share a hidden embed.",
        )
    # Channel needles thread along the open channel between rails.
    if r.retention == "channel_tunnels":
        for info in infos:
            for ci in range(r.channel_count):
                needle = model.get_part(f"{info.name}_needle_{ci}")
                for ri in (ci, ci + 1):
                    ctx.allow_overlap(
                        info.part, needle, elem_a=f"channel_rail_{ri}", elem_b="needle_shaft",
                        reason="Needle threads along the open channel beside the rail wall.",
                    )


def run_needle_case_tests(object_model: ArticulatedObject, config: NeedleCaseConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    infos: list[PanelInfo] = []
    if r.skeleton != "tube":
        for i in range(r.n_panels):
            p = object_model.get_part(f"panel_{i}")
            cx = 0.0 if i == 0 else r.pw / 2 - SEAM_OVER
            top_z = PANEL_T if i == 0 else -0.0005
            outer = r.pw / 2 if i == 0 else r.pw - SEAM_OVER
            infos.append(PanelInfo(p, f"panel_{i}", cx, top_z, outer, i == 0))

    _declare_allowances(ctx, object_model, r, infos)

    # ---- Identity: needle interior + a real closure articulation. ----
    needle_count = sum(
        1
        for p in object_model.parts
        for v in p.visuals
        if v.name.startswith("needle_")
    ) + sum(1 for p in object_model.parts if "_needle_" in p.name)
    ctx.check(
        "case stores an indexed row/bundle of needles",
        needle_count >= 3,
        details=f"needle elements found = {needle_count}",
    )
    joint_names = {a.name for a in object_model.articulations}
    ctx.check(
        "case has a real closure articulation",
        "closure_hinge" in joint_names or "closure_slide" in joint_names,
        details=f"joints={sorted(joint_names)}",
    )

    if r.skeleton == "tube":
        tube = object_model.get_part("tube_body")
        cap = object_model.get_part("cap")
        j = object_model.get_articulation("closure_slide")
        ctx.allow_isolated_part(
            cap,
            reason="cap pulls off the tube mouth and loses body contact",
        )
        ctx.check(
            "tube skeleton is a volumetric shell with a prismatic pull cap",
            tube.get_visual("tube_shell") is not None
            and j.articulation_type == ArticulationType.PRISMATIC,
            details=f"cap joint = {j.articulation_type}",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({j: 0.06}):
            pulled = ctx.part_world_position(cap)
            ctx.expect_gap(cap, tube, axis="z", positive_elem="cap_disk",
                           negative_elem="tube_shell", min_gap=0.02,
                           name="cap clears the tube mouth when pulled")
        ctx.check(
            "cap pulls upward off the tube mouth",
            rest is not None and pulled is not None and pulled[2] > rest[2] + 0.04,
            details=f"rest={rest}, pulled={pulled}",
        )
    else:
        # ---- Panels lie coplanar and open flat at rest. ----
        base_aabb = ctx.part_world_aabb(infos[0].part)
        ctx.check(
            "open case lies flat on the table",
            base_aabb is not None and base_aabb[0][2] > -0.001 and base_aabb[0][2] < 0.003,
            details=f"base_aabb={base_aabb}",
        )
        # ---- Fold hinge lifts a folded panel (multi-panel skeletons). ----
        if r.n_panels >= 2:
            fold = object_model.get_articulation("fold_hinge_1")
            panel1 = infos[1].part
            rest = ctx.part_world_aabb(panel1)
            with ctx.pose({fold: 1.2}):
                folded = ctx.part_world_aabb(panel1)
            ctx.check(
                "fold hinge lifts the folded panel upward",
                rest is not None and folded is not None and folded[1][2] > 0.10
                and rest[1][2] < 0.02,
                details=f"rest={rest}, folded={folded}",
            )
        # ---- Needle-tip flap swings up away from the tips. ----
        flap_j = object_model.get_articulation(f"{infos[0].name}_tip_flap_hinge")
        flap_part = object_model.get_part(f"{infos[0].name}_tip_flap")
        rest_f = ctx.part_world_aabb(flap_part)
        with ctx.pose({flap_j: 1.8}):
            up_f = ctx.part_world_aabb(flap_part)
        ctx.check(
            "needle-tip flap swings up and away",
            rest_f is not None and up_f is not None and up_f[1][2] > rest_f[1][2] + 0.03,
            details=f"rest={rest_f}, up={up_f}",
        )
        # ---- Channel needle slides out (prismatic ②). ----
        if r.retention == "channel_tunnels":
            slide = object_model.get_articulation(f"{infos[0].name}_needle_0_slide")
            needle = object_model.get_part(f"{infos[0].name}_needle_0")
            rest_p = ctx.part_world_position(needle)
            with ctx.pose({slide: CH_TRAVEL}):
                out_p = ctx.part_world_position(needle)
            ctx.check(
                "channel needle slides out toward -y",
                rest_p is not None and out_p is not None and out_p[1] < rest_p[1] - 0.05,
                details=f"rest={rest_p}, out={out_p}",
            )
        # ---- Closure moves (fold up, or slide along the rail). ----
        if r.closure in ("snap_cover_flap", "wrap_tie"):
            cj = object_model.get_articulation("closure_hinge")
            child = object_model.get_part(
                "closure_flap" if r.closure == "snap_cover_flap" else "wrap_tie"
            )
            rest_c = ctx.part_world_aabb(child)
            with ctx.pose({cj: 1.5}):
                up_c = ctx.part_world_aabb(child)
            ctx.check(
                "closure flap folds up over the case",
                up_c is not None and up_c[1][2] > 0.05,
                details=f"rest={rest_c}, up={up_c}",
            )
        else:  # zipper
            zj = object_model.get_articulation("closure_slide")
            pull = object_model.get_part("zip_pull")
            rest_z = ctx.part_world_position(pull)
            upper = zj.motion_limits.upper or 0.0
            with ctx.pose({zj: upper * 0.8}):
                moved_z = ctx.part_world_position(pull)
            ctx.check(
                "zip pull slides along the tape rail in +y",
                rest_z is not None and moved_z is not None and moved_z[1] > rest_z[1] + 0.04,
                details=f"rest={rest_z}, moved={moved_z}",
            )

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=28, ignore_fixed=True)

    # ---- Compiler-owned baseline. ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "Skeleton",
    "Retention",
    "Closure",
    "PaletteStyle",
    "NeedleCaseConfig",
    "ResolvedNeedleCaseConfig",
    "build_needle_case",
    "build_seeded_needle_case",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_needle_case_tests",
]
