# SPDX-License-Identifier: Apache-2.0

"""Sci-fi gate (blast / airlock / security door) modular template.

A wall-mounted sci-fi gate: a fixed structural ``frame`` surround standing on
z=0 that frames a *true through-opening* (no back wall), cleared by one of five
genuinely different powered opening mechanisms. Sourced from the reviewed
modular spec ``articraft_template_authoring/specs_modular_v1/Door_Scifi_Gate.md`` and
the 11 5-star sample pool (2 telescope parents + 9 converged variants) synced
under ``data/records/``.

Pattern = ``mixed``: a single root ``frame`` part (the surround, whose doorway
bore is rectangular for the lateral mechanisms and round for the iris families),
with the moving segments of the selected mechanism attaching as parallel
children of ``frame``. Some mechanisms multiplicity-loop their segments.

Four structural axes (slots):

  * ``opening_mechanism`` (4) — how the doorway is cleared, each a DIFFERENT
    joint topology:
      - ``biparting_lateral_telescope``: ±X PRISMATIC mimic chain
        (1 driver + 1 same-rate mimic + 2 outer ×0.5 mimics), 4 hand-named
        leaves (door_0/1 + _outer). Retract into carved hex-slab side pockets.
      - ``single_leaf_sliding_pocket``: +X PRISMATIC, 1 driver + 1 ×0.5 mimic,
        one full-width leaf + rear stage into a carved right wall pocket.
      - ``vertical_lift``: ±Z PRISMATIC, N independent slabs (no mimic), either
        overhead-staggered (all +Z, bottom travels farthest) or bi-parting
        even-pitch (lower −Z / upper +Z); nest into the lintel header/sill
        housing.
      - ``iris_radial_slide``: the round-aperture door. N pie-wedge leaves that
        CONVERGE to the aperture centre when closed (tiling the disc) and slide
        radially OUTWARD into carved wall slots when open (a true through-hole).
        leaf_0 driver + (N-1) ×1.0 mimics so none can float. N in [2,8]
        (n=2 is a biparting half-disc). This is the only round iris — the old
        ``iris_revolute_swing`` petal-swing mechanism was removed.
  * ``frame_surround`` (3) — the fixed surround: ``hex_beveled_slab`` (lateral
    doors, side pockets carved), ``lintel_sill_side_housing`` (vertical lift),
    ``circular_bulkhead_ring`` (radial iris, realised as a thick round disc with
    a round bore + carved radial wedge slots).
  * ``seam_motif`` (5) — the face / seam treatment on the moving segments,
    inlined as ``parent.visual`` (Rule 1): ``hazard_cosine_seam``,
    ``zigzag_dovetail_seam``, ``horizontal_louver_slab``,
    ``radial_petal_wedge``, ``flat_armor_plate``. Legal set is conditional on
    the mechanism (see compatibility matrix).
  * multiplicity ``N`` — per-mechanism: slab_count [3,8] (lift),
    leaf_count [2,8] (iris-radial, i.e. 2/3/4/5/6/7/8 doors to the centre),
    leaves_per_side [1,2] (telescope=2 / pocket=1, fixed set). Encoded into the
    slot_choice tuple as ``("mech_count", f"n{N}")``.

  * ``palette_style`` (5) — top-dressing colorway, sampled per seed, driving
    EVERY ``.visual`` material. Not a structural axis.

3 hard rules honoured:
  1. Decorations (hazard decals, grooves, bolts, keypad, lamps, rivets, ribs)
     are ``parent.visual``, never FIXED parts. The spec's "fixed furniture"
     layer (keypad / hazard chevrons / bolts / lamps) is realised as frame
     sub-visuals with no per-greeble joint.
  2. Every non-FIXED joint is a captured wall pocket / rail / pivot / radial slide whose
     contact face is tangential to the motion axis, so (like cushion's slide
     lid and the source records) the mating contract is grandfathered and the
     captured overlap is declared element-scoped in run_scifi_gate_tests.
  3. No primitive downgrade: curved iris petals, radial wedges, hex/round bores,
     zig-zag / cosine seams use CadQuery, never crude Box/Cylinder.
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
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

OpeningMechanism = Literal[
    "biparting_lateral_telescope",
    "single_leaf_sliding_pocket",
    "vertical_lift",
    "iris_radial_slide",
]
FrameSurround = Literal[
    "hex_beveled_slab",
    "lintel_sill_side_housing",
    "circular_bulkhead_ring",
]
SeamMotif = Literal[
    "hazard_cosine_seam",
    "zigzag_dovetail_seam",
    "horizontal_louver_slab",
    "radial_petal_wedge",
    "flat_armor_plate",
]
PaletteStyle = Literal[
    "gunmetal_hazard_yellow",
    "dark_armor_cyan_glow",
    "riveted_steel_amber",
    "olive_mil_hazard",
    "airlock_white_cyan",
]

OPENING_MECHANISMS: tuple[OpeningMechanism, ...] = (
    "biparting_lateral_telescope",
    "single_leaf_sliding_pocket",
    "vertical_lift",
    "iris_radial_slide",
)
FRAME_SURROUNDS: tuple[FrameSurround, ...] = (
    "hex_beveled_slab",
    "lintel_sill_side_housing",
    "circular_bulkhead_ring",
)
SEAM_MOTIFS: tuple[SeamMotif, ...] = (
    "hazard_cosine_seam",
    "zigzag_dovetail_seam",
    "horizontal_louver_slab",
    "radial_petal_wedge",
    "flat_armor_plate",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gunmetal_hazard_yellow",
    "dark_armor_cyan_glow",
    "riveted_steel_amber",
    "olive_mil_hazard",
    "airlock_white_cyan",
)

# Mechanism sampling weights, order matches OPENING_MECHANISMS
# (biparting / pocket / lift / radial-iris). The radial iris is the headline
# round-aperture door, so it carries a healthy share.
MECHANISM_WEIGHTS = (0.28, 0.12, 0.26, 0.34)

# Mechanisms that need a round aperture (the radial sliding iris).
IRIS_MECHANISMS: frozenset[OpeningMechanism] = frozenset(("iris_radial_slide",))
# Rectangular mechanisms (rect / hex bore).
RECT_MECHANISMS: frozenset[OpeningMechanism] = frozenset(
    ("biparting_lateral_telescope", "single_leaf_sliding_pocket", "vertical_lift")
)

# Compatibility matrix: legal seam_motif set per mechanism (spec §9).
MECH_MOTIFS: dict[OpeningMechanism, tuple[SeamMotif, ...]] = {
    "biparting_lateral_telescope": (
        "hazard_cosine_seam",
        "zigzag_dovetail_seam",
        "flat_armor_plate",
    ),
    "single_leaf_sliding_pocket": (
        "flat_armor_plate",
        "hazard_cosine_seam",
        "zigzag_dovetail_seam",
    ),
    "vertical_lift": ("horizontal_louver_slab", "flat_armor_plate"),
    "iris_radial_slide": ("radial_petal_wedge", "flat_armor_plate"),
}
# Legal surround set per mechanism (spec §9). Pocket needs the lintel family
# (enlarged right pocket); iris needs a round-aperture-capable surround.
MECH_SURROUNDS: dict[OpeningMechanism, tuple[FrameSurround, ...]] = {
    # Lateral pocket doors need a solid wall to retract INTO — gate them to the
    # hex slab, whose side pockets are boolean-carved so the leaves hide in a
    # real wall slot (no tunnelling, no leaves parked floating in open air on a
    # lintel/ring surround).
    "biparting_lateral_telescope": ("hex_beveled_slab",),
    "single_leaf_sliding_pocket": ("hex_beveled_slab",),
    # Lift slabs retract vertically into the overhead header + floor sill
    # housing — gate to the lintel housing so they nest into a real captured
    # pocket rather than tunnelling a solid hex slab's header region.
    "vertical_lift": ("lintel_sill_side_housing",),
    # The radial sliding iris (the only round-aperture door) renders its own
    # thick round disc with carved radial slots; the surround slot is fixed to
    # the bulkhead-ring family so the round reference frame stays consistent.
    "iris_radial_slide": ("circular_bulkhead_ring",),
}

# Per-mechanism multiplicity domains.
SLAB_N_MIN, SLAB_N_MAX = 3, 8
# The radial iris supports 2..8 leaves converging on the centre (user request):
# n=2 is a biparting half-disc, n=3..8 tile the disc into that many wedges.
LEAF_N_MIN, LEAF_N_MAX = 2, 8
# Small-N high-frequency weighting helpers (spec §8).
_SLAB_WEIGHTS = {3: 0.26, 4: 0.26, 5: 0.20, 6: 0.14, 7: 0.08, 8: 0.06}
_LEAF_WEIGHTS = {2: 0.14, 3: 0.18, 4: 0.20, 5: 0.16, 6: 0.13, 7: 0.10, 8: 0.09}


# ---------------------------------------------------------------------------
# Palettes — each colorway drives every .visual material (Rule: >=4-5 colorway).
# Keys are role names used uniformly across surround / mechanism / motif.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gunmetal_hazard_yellow": {
        "frame": (0.32, 0.34, 0.37, 1.0),
        "trim": (0.12, 0.13, 0.14, 1.0),
        "armor": (0.18, 0.20, 0.22, 1.0),
        "armor_deep": (0.14, 0.16, 0.18, 1.0),
        "accent": (0.95, 0.78, 0.06, 1.0),
        "glow": (0.45, 0.98, 1.0, 1.0),
        "status": (0.85, 0.16, 0.12, 1.0),
        "rib": (0.10, 0.11, 0.12, 1.0),
    },
    "dark_armor_cyan_glow": {
        "frame": (0.16, 0.18, 0.21, 1.0),
        "trim": (0.07, 0.08, 0.09, 1.0),
        "armor": (0.12, 0.14, 0.17, 1.0),
        "armor_deep": (0.09, 0.10, 0.12, 1.0),
        "accent": (0.30, 0.92, 0.98, 1.0),
        "glow": (0.40, 0.95, 1.0, 1.0),
        "status": (0.20, 0.80, 0.95, 1.0),
        "rib": (0.05, 0.06, 0.07, 1.0),
    },
    "riveted_steel_amber": {
        "frame": (0.56, 0.55, 0.52, 1.0),
        "trim": (0.30, 0.29, 0.27, 1.0),
        "armor": (0.42, 0.41, 0.38, 1.0),
        "armor_deep": (0.34, 0.33, 0.30, 1.0),
        "accent": (0.92, 0.62, 0.10, 1.0),
        "glow": (0.98, 0.74, 0.30, 1.0),
        "status": (0.90, 0.42, 0.08, 1.0),
        "rib": (0.24, 0.23, 0.21, 1.0),
    },
    "olive_mil_hazard": {
        "frame": (0.27, 0.30, 0.26, 1.0),
        "trim": (0.16, 0.18, 0.15, 1.0),
        "armor": (0.22, 0.25, 0.21, 1.0),
        "armor_deep": (0.17, 0.20, 0.16, 1.0),
        "accent": (0.92, 0.74, 0.06, 1.0),
        "glow": (0.60, 0.85, 0.35, 1.0),
        "status": (0.85, 0.20, 0.14, 1.0),
        "rib": (0.12, 0.14, 0.11, 1.0),
    },
    "airlock_white_cyan": {
        "frame": (0.86, 0.87, 0.89, 1.0),
        "trim": (0.42, 0.44, 0.47, 1.0),
        "armor": (0.74, 0.76, 0.79, 1.0),
        "armor_deep": (0.62, 0.64, 0.68, 1.0),
        "accent": (0.20, 0.78, 0.92, 1.0),
        "glow": (0.45, 0.98, 1.0, 1.0),
        "status": (0.92, 0.32, 0.30, 1.0),
        "rib": (0.40, 0.42, 0.45, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Base real-world dimensions (metres). Common door geometry shared by all
# mechanisms; sampled scales applied in resolve_config.
# ---------------------------------------------------------------------------
_OPENING_W = 1.40  # clear doorway width (X), midpoint of S1(1.18)/S2(1.62)
_OPENING_H = 1.95  # clear doorway height (Z)
_SILL_H = 0.05  # floor sill / leaf bottom z
_FRAME_DEPTH = 0.30  # surround depth (Y)
_DOOR_THK = 0.06  # one telescoping stage thickness (Y)

# Telescope split per side (fractions of half opening).
_A_OUT_FRAC = 0.58  # outer edge of inner seam leaf
_B_IN_FRAC = 0.55  # inner edge of outer leaf (laps inner)
_SEAM_AMP = 0.055  # cosine seam amplitude
_TOOTH = 0.09  # zig-zag tooth half-amplitude
_SEAM_CLEAR = 0.003  # running seam clearance per side
_A_PLANE_Y = -0.045  # inner leaf plane (front)
_B_PLANE_Y = 0.035  # outer leaf plane (rear)

# Iris (radial sliding wedge door).
_IRIS_R = 0.52  # nominal iris reference radius (scaled per seed)
_IRIS_OPEN_ANGLE = 1.05  # retained for the resolved-config record only
_LEAF_OUTER_R = 0.55
_LEAF_THICK = 0.05

_RING_OUTER_R = 1.30  # bulkhead ring outer radius
_RING_THK = 0.08
_IRIS_BORE_CLEAR = 0.055


# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ScifiGateConfig:
    opening_mechanism: OpeningMechanism | None = None
    frame_surround: FrameSurround | None = None
    seam_motif: SeamMotif | None = None
    mech_count: int | None = None  # per-mechanism multiplicity (N)
    palette_style: PaletteStyle = "gunmetal_hazard_yellow"
    opening_width_scale: float = 1.0
    opening_height_scale: float = 1.0
    surround_depth_scale: float = 1.0
    iris_radius_scale: float = 1.0
    iris_open_angle_scale: float = 1.0
    name: str = "scifi_gate"


@dataclass(frozen=True)
class ResolvedScifiGateConfig:
    opening_mechanism: OpeningMechanism
    frame_surround: FrameSurround
    seam_motif: SeamMotif
    mech_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    opening_w: float
    opening_h: float
    half_w: float
    sill_h: float
    frame_depth: float
    door_thk: float
    leaf_top_z: float
    leaf_cz: float
    # telescope / pocket
    a_out: float
    b_in: float
    travel_a: float
    travel_b: float
    leaves_per_side: int
    pocket_right_w: float
    # iris
    iris_r: float
    iris_open_angle: float
    leaf_outer_r: float
    leaf_travel: float
    aperture_shape: str  # "rect" | "hex" | "round"
    name: str

    @property
    def is_iris(self) -> bool:
        return self.opening_mechanism in IRIS_MECHANISMS


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _weighted_n(rng: random.Random, weights: dict[int, float]) -> int:
    ns = list(weights.keys())
    ws = [weights[n] for n in ns]
    return rng.choices(ns, weights=ws, k=1)[0]


# ---------------------------------------------------------------------------
# Procedural sampling (deterministic; seed 0 not special).
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ScifiGateConfig:
    rng = random.Random(seed)
    mech: OpeningMechanism = rng.choices(
        list(OPENING_MECHANISMS), weights=list(MECHANISM_WEIGHTS), k=1
    )[0]
    surround = rng.choice(MECH_SURROUNDS[mech])
    motif = rng.choice(MECH_MOTIFS[mech])

    if mech == "vertical_lift":
        n = _weighted_n(rng, _SLAB_WEIGHTS)
    elif mech == "iris_radial_slide":
        n = _weighted_n(rng, _LEAF_WEIGHTS)
    elif mech == "biparting_lateral_telescope":
        n = 2  # 2 leaves per side (fixed set)
    else:  # single_leaf_sliding_pocket
        n = 1

    return ScifiGateConfig(
        opening_mechanism=mech,
        frame_surround=surround,
        seam_motif=motif,
        mech_count=n,
        palette_style=rng.choice(PALETTE_STYLES),
        opening_width_scale=round(rng.uniform(0.85, 1.15), 4),
        opening_height_scale=round(rng.uniform(0.90, 1.12), 4),
        surround_depth_scale=round(rng.uniform(0.90, 1.20), 4),
        iris_radius_scale=round(rng.uniform(0.90, 1.15), 4),
        iris_open_angle_scale=round(rng.uniform(0.92, 1.10), 4),
        name=f"seeded_scifi_gate_{seed}",
    )


def resolve_config(config: ScifiGateConfig | None = None) -> ResolvedScifiGateConfig:
    cfg = config or ScifiGateConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    mech = _pick(cfg.opening_mechanism, OPENING_MECHANISMS)
    # --- Compatibility gating (spec §9): legalise surround / motif. ---
    surround = cfg.frame_surround
    if surround not in MECH_SURROUNDS[mech]:
        surround = MECH_SURROUNDS[mech][0]
    motif = cfg.seam_motif
    if motif not in MECH_MOTIFS[mech]:
        motif = MECH_MOTIFS[mech][0]

    # Aperture shape gated by mechanism + surround.
    if mech in IRIS_MECHANISMS:
        aperture_shape = "round"
    elif surround == "hex_beveled_slab":
        aperture_shape = "hex"
    else:  # lintel or bulkhead with a rectangular mechanism
        aperture_shape = "rect"

    # --- Continuous scales (independent -> clamp). ---
    w_scale = _clamp(cfg.opening_width_scale, 0.85, 1.15)
    h_scale = _clamp(cfg.opening_height_scale, 0.90, 1.12)
    d_scale = _clamp(cfg.surround_depth_scale, 0.90, 1.20)
    ir_scale = _clamp(cfg.iris_radius_scale, 0.90, 1.15)
    ang_scale = _clamp(cfg.iris_open_angle_scale, 0.92, 1.10)

    opening_w = _OPENING_W * w_scale
    opening_h = _OPENING_H * h_scale
    half_w = opening_w / 2.0
    frame_depth = _FRAME_DEPTH * d_scale
    sill_h = _SILL_H
    leaf_top_z = sill_h + opening_h
    leaf_cz = sill_h + opening_h / 2.0

    # --- Multiplicity per mechanism. ---
    if mech == "vertical_lift":
        n = int(_clamp(cfg.mech_count or 4, SLAB_N_MIN, SLAB_N_MAX))
        leaves_per_side = 2
    elif mech == "iris_radial_slide":
        n = int(_clamp(cfg.mech_count or 4, LEAF_N_MIN, LEAF_N_MAX))
        leaves_per_side = 2
    elif mech == "biparting_lateral_telescope":
        n = 2
        leaves_per_side = 2
    else:  # pocket
        n = 1
        leaves_per_side = 1

    # --- Telescope / pocket derived travel (spec equation). ---
    a_out = half_w * _A_OUT_FRAC
    b_in = half_w * _B_IN_FRAC
    if mech == "single_leaf_sliding_pocket":
        # Full-width single leaf slides right into an enlarged right pocket.
        travel_a = opening_w * 0.78
        pocket_right_w = opening_w * 0.72
    else:
        travel_a = half_w + 0.10  # inner leaf clears the opening into the pocket
        pocket_right_w = half_w * 0.66
    travel_b = travel_a / 2.0

    # --- Iris derived geometry + inscribed-circle inequality (spec §7). ---
    iris_r = _IRIS_R * ir_scale
    # The round aperture must inscribe in the surround bore: keep the iris
    # outer reach within half the smaller opening dim minus a rim lip.
    leaf_outer_r = _LEAF_OUTER_R * ir_scale
    rim_lip = 0.04
    max_reach = 0.5 * min(opening_w, opening_h) - rim_lip
    if mech in IRIS_MECHANISMS:
        # Project iris reach into the feasible inscribed circle, including a
        # real bore clearance so moving iris leaves do not scrape/cut into the
        # fixed slab when sampled scales are near their upper bounds.
        feasible_leaf_outer = max(0.20, max_reach - _IRIS_BORE_CLEAR)
        if leaf_outer_r > feasible_leaf_outer:
            shrink = feasible_leaf_outer / leaf_outer_r
            leaf_outer_r = feasible_leaf_outer
            iris_r = iris_r * shrink
    # iris radial travel: retract leaves clear of the aperture, stay in frame.
    leaf_travel = leaf_outer_r * 0.65
    if mech == "iris_radial_slide":
        # Radial pie-wedge leaves converge to the circle centre when closed and
        # must retract FULLY clear of the round aperture when open (a true
        # through-opening). Grow the wedge so it overlaps the bore rim (sealing
        # the disc, no gap ring), and size travel so each wedge's inner tip
        # withdraws past the bore rim into its carved wall slot. The wedge is
        # authored pointing +X (angle 0) and rotated into its sector by the
        # joint frame, so all wedges share one joint origin at the aperture
        # centre (no double-rotation, no fixed centre spider).
        leaf_outer_r = max(0.20, max_reach - 0.02)
        bore_r = leaf_outer_r - 0.03  # wedges overlap the rim by 0.03
        leaf_travel = bore_r + 0.06  # inner tip clears the rim -> open

    # Retained for the resolved-config record; the radial iris drives its motion
    # off leaf_travel, not a swing angle.
    iris_open_angle = _IRIS_OPEN_ANGLE * ang_scale

    return ResolvedScifiGateConfig(
        opening_mechanism=mech,
        frame_surround=surround,
        seam_motif=motif,
        mech_count=n,
        palette_style=palette_style,
        opening_w=opening_w,
        opening_h=opening_h,
        half_w=half_w,
        sill_h=sill_h,
        frame_depth=frame_depth,
        door_thk=_DOOR_THK,
        leaf_top_z=leaf_top_z,
        leaf_cz=leaf_cz,
        a_out=a_out,
        b_in=b_in,
        travel_a=travel_a,
        travel_b=travel_b,
        leaves_per_side=leaves_per_side,
        pocket_right_w=pocket_right_w,
        iris_r=iris_r,
        iris_open_angle=iris_open_angle,
        leaf_outer_r=leaf_outer_r,
        leaf_travel=leaf_travel,
        aperture_shape=aperture_shape,
        name=cfg.name or "scifi_gate",
    )


def with_overrides(config: ScifiGateConfig, **kwargs: object) -> ScifiGateConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ScifiGateConfig | ResolvedScifiGateConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedScifiGateConfig) else resolve_config(config)
    return (
        ("opening_mechanism", r.opening_mechanism),
        ("frame_surround", r.frame_surround),
        ("seam_motif", r.seam_motif),
        ("mech_count", f"n{r.mech_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Surround mesh helpers (Slot D). Each builds the fixed frame slab/ring with
# the appropriate doorway bore (rect / hex / round) cut through it.
# ===========================================================================
def _hex_opening_profile(w: float, h: float, chamf: float) -> list[tuple[float, float]]:
    hw = w / 2.0
    hh = h / 2.0
    cz = h / 2.0 - chamf
    return [
        (-hw, -cz),
        (-hw, cz),
        (-hw + chamf, hh),
        (hw - chamf, hh),
        (hw, cz),
        (hw, -cz),
        (hw - chamf, -hh),
        (-hw + chamf, -hh),
    ]


def _bore_cutter(r: ResolvedScifiGateConfig, depth: float, cy: float) -> cq.Workplane:
    """Doorway bore cutter centred at opening centre, shape per aperture_shape."""
    if r.aperture_shape == "round":
        bore_r = max(r.iris_r + 0.06, r.leaf_outer_r + _IRIS_BORE_CLEAR)
        cutter = cq.Workplane("XZ").circle(bore_r).extrude(depth * 2.0, both=True)
    elif r.aperture_shape == "hex":
        # Elongated hexagon that CIRCUMSCRIBES the opening_w x opening_h rectangle
        # with margin on BOTH axes: the straight section extends `margin` beyond
        # the opening width AND height and the chamfer flares OUTward, so a
        # full-opening rectangular leaf (e.g. the single_leaf_sliding_pocket leaf)
        # sits entirely inside the bore with a running clearance — its side/top
        # edges never go coincident with the slab bore wall (which would register
        # a coincident-edge mesh overlap with the surround). The leaf sits in
        # front of the bore rim so the rebate is hidden and the opening stays
        # sealed when closed.
        chamf = min(0.26, r.opening_h * 0.14)
        margin = 0.06
        hw = r.opening_w / 2.0 + margin
        cz = r.opening_h / 2.0 + margin
        hh = cz + chamf
        pts = [
            (-hw, -cz),
            (-hw, cz),
            (-hw + chamf, hh),
            (hw - chamf, hh),
            (hw, cz),
            (hw, -cz),
            (hw - chamf, -hh),
            (-hw + chamf, -hh),
        ]
        cutter = cq.Workplane("XZ").polyline(pts).close().extrude(depth * 2.0, both=True)
    else:  # rect
        cutter = cq.Workplane("XZ").rect(r.opening_w, r.opening_h).extrude(depth * 2.0, both=True)
    return cutter.translate((0.0, 0.0, cy))


# Leaf y-band spanned by the lateral telescope stages (A-plane + B-plane leaves,
# each door_thk thick), used to size the carved wall pockets.
_LATERAL_LEAF_Y_LO = min(_A_PLANE_Y, _B_PLANE_Y) - _DOOR_THK / 2.0 - 0.02
_LATERAL_LEAF_Y_HI = max(_A_PLANE_Y, _B_PLANE_Y) + _DOOR_THK / 2.0 + 0.02


def _is_lateral(r: ResolvedScifiGateConfig) -> bool:
    return r.opening_mechanism in (
        "biparting_lateral_telescope",
        "single_leaf_sliding_pocket",
    )


def _lateral_open_reach(r: ResolvedScifiGateConfig) -> float:
    """Largest |x| a moving leaf edge reaches when fully open."""
    if r.opening_mechanism == "single_leaf_sliding_pocket":
        return r.half_w + r.travel_a
    return r.a_out + r.travel_a


def _carve_side_pockets(
    slab: cq.Workplane, r: ResolvedScifiGateConfig, slab_half_w: float
) -> cq.Workplane:
    """Hollow a real pocket into each side of the slab (at the leaf y-band, over
    the clear-door height) so a retracting lateral leaf slides INTO the wall
    instead of tunnelling through solid material. The front + back skins stay
    solid so the parked leaf is hidden from the front; the pocket mouth opens
    toward the doorway so the leaf enters cleanly."""
    py_lo, py_hi = _LATERAL_LEAF_Y_LO, _LATERAL_LEAF_Y_HI
    py_c, py_d = (py_lo + py_hi) / 2.0, (py_hi - py_lo)
    z0, z1 = r.sill_h, r.leaf_top_z
    pz_c, pz_d = (z0 + z1) / 2.0, (z1 - z0)
    sides = (1.0,) if r.opening_mechanism == "single_leaf_sliding_pocket" else (-1.0, 1.0)
    x_in = r.half_w - 0.03
    x_out = slab_half_w - 0.02
    if x_out <= x_in:
        return slab
    px_d = x_out - x_in
    for s in sides:
        px_c = s * (x_in + x_out) / 2.0
        cavity = (
            cq.Workplane("XY")
            .box(px_d, py_d, pz_d, centered=(True, True, True))
            .translate((px_c, py_c, pz_c))
        )
        slab = slab.cut(cavity)
    return slab


def _hex_slab_mesh(r: ResolvedScifiGateConfig) -> cq.Workplane:
    """Hex-beveled slab surround (S1 _frame_mesh): flat slab + bevelled bore.

    For the lateral sliding mechanisms the slab is widened to contain the fully
    open leaves and side pockets are carved so the doors retract into a real wall
    slot (no tunnelling through solid material)."""
    frame_w = r.opening_w + 2.0 * (r.half_w * 0.45 + 0.18)
    if _is_lateral(r):
        frame_w = max(frame_w, 2.0 * (_lateral_open_reach(r) + 0.12))
    frame_h = r.sill_h + r.opening_h + 0.34
    slab = cq.Workplane("XY").box(frame_w, r.frame_depth, frame_h, centered=(True, True, False))
    # Bevel the four outer vertical corners of the slab BEFORE cutting the bore
    # (so the bore shape — round or hex — never starves the chamfer selector).
    try:
        slab = slab.edges("|Z").chamfer(0.012)
    except Exception:
        pass
    slab = slab.cut(_bore_cutter(r, r.frame_depth, r.leaf_cz))
    if _is_lateral(r):
        slab = _carve_side_pockets(slab, r, frame_w / 2.0)
    return slab


def _bulkhead_ring_mesh(r: ResolvedScifiGateConfig) -> cq.Workplane:
    """Circular bulkhead ring (S11 _make_bulkhead_ring): disc + bore + rim lip
    + door-stop frame, deck-cut at z=0. Built local, centred on opening centre."""
    outer_r = max(_RING_OUTER_R, r.opening_w * 0.85, r.opening_h * 0.72)
    thk = _RING_THK
    centre_z = r.leaf_cz

    ring = cq.Workplane("XZ").circle(outer_r).extrude(thk).translate((0.0, -thk / 2.0, 0.0))
    # Doorway bore (rect for telescope, round for iris).
    if r.aperture_shape == "round":
        bore_r = max(r.iris_r + 0.06, r.leaf_outer_r + _IRIS_BORE_CLEAR)
        bore = (
            cq.Workplane("XZ")
            .circle(bore_r)
            .extrude(thk + 0.04)
            .translate((0.0, -(thk + 0.04) / 2.0, 0.0))
        )
    else:
        bore = (
            cq.Workplane("XZ")
            .rect(r.opening_w, r.opening_h)
            .extrude(thk + 0.04)
            .translate((0.0, -(thk + 0.04) / 2.0, 0.0))
        )
    ring = ring.cut(bore)
    # Outer rim lip (raised annular band on the front face).
    lip_w, lip_t = 0.035, 0.015
    lip = (
        cq.Workplane("XZ")
        .circle(outer_r + 0.001)
        .circle(outer_r - lip_w)
        .extrude(lip_t)
        .translate((0.0, -thk / 2.0 - lip_t, 0.0))
    )
    ring = ring.union(lip)
    # Inner door-stop frame.
    stop_w, stop_t = 0.025, 0.012
    if r.aperture_shape == "round":
        bore_r = max(r.iris_r + 0.06, r.leaf_outer_r + _IRIS_BORE_CLEAR)
        stop = (
            cq.Workplane("XZ")
            .circle(bore_r + stop_w)
            .circle(bore_r + 0.002)
            .extrude(stop_t)
            .translate((0.0, -thk / 2.0 - stop_t, 0.0))
        )
    else:
        stop = (
            cq.Workplane("XZ")
            .rect(r.opening_w + 2 * stop_w, r.opening_h + 2 * stop_w)
            .extrude(stop_t)
            .translate((0.0, -thk / 2.0 - stop_t, 0.0))
        )
        stop_hole = (
            cq.Workplane("XZ")
            .rect(r.opening_w + 0.004, r.opening_h + 0.004)
            .extrude(stop_t + 0.02)
            .translate((0.0, -thk / 2.0 - stop_t - 0.01, 0.0))
        )
        stop = stop.cut(stop_hole)
    ring = ring.union(stop)
    # Deck cut: remove everything below the floor (local z = -centre_z).
    deck = (
        cq.Workplane("XY")
        .rect(2.0 * outer_r + 0.4, thk + lip_t + 0.4)
        .extrude(3.0)
        .translate((0.0, 0.0, -centre_z - 3.0))
    )
    ring = ring.cut(deck)
    return ring


# ===========================================================================
# Surround factory: builds the fixed `frame` root part + inline greebles.
# Returns useful frame anchors.
# ===========================================================================
def _build_surround(model, r: ResolvedScifiGateConfig, mats) -> object:
    frame = model.part("frame")
    frame_front_y = r.frame_depth / 2.0

    if r.opening_mechanism == "iris_radial_slide":
        # Thick round disc: round bore + carved mid-plane radial wedge slots.
        frame.visual(
            mesh_from_cadquery(_round_disc_slab_mesh(r), "round_disc"),
            material=mats["frame"],
            name="frame_slab", material_class_id="tech.scifi_panel",
        )
        frame_front_y = r.frame_depth / 2.0
        outer_r = r.leaf_travel + r.leaf_outer_r + 0.06 + 0.16
        n_bolts = 24
        bolt_circle_r = outer_r - 0.08
        for i in range(n_bolts):
            ang = 2.0 * math.pi * i / n_bolts
            bx = bolt_circle_r * math.cos(ang)
            bz = bolt_circle_r * math.sin(ang) + r.leaf_cz
            if bz < 0.06:
                continue
            frame.visual(
                Box((0.030, 0.030, 0.030)),
                origin=Origin(xyz=(bx, frame_front_y - 0.013, bz)),
                material=mats["trim"],
                name=f"ring_bolt_{i}", material_class_id="metal.blackened_gunmetal",
            )
    elif r.frame_surround == "circular_bulkhead_ring":
        ring_front_y = -r.frame_depth / 2.0
        ring_y = ring_front_y + _RING_THK / 2.0
        frame.visual(
            mesh_from_cadquery(_bulkhead_ring_mesh(r), "bulkhead_ring"),
            origin=Origin(xyz=(0.0, ring_y, r.leaf_cz)),
            material=mats["frame"],
            name="frame_slab", material_class_id="tech.scifi_panel",
        )
        frame_front_y = ring_front_y
        outer_r = max(_RING_OUTER_R, r.opening_w * 0.85, r.opening_h * 0.72)
        # Perimeter bolt circle (inline visuals, no joints — Rule 1).
        n_bolts = 20
        bolt_circle_r = outer_r - 0.07
        for i in range(n_bolts):
            ang = 2.0 * math.pi * i / n_bolts
            bx = bolt_circle_r * math.cos(ang)
            bz = bolt_circle_r * math.sin(ang) + r.leaf_cz
            # Skip bolts overlapping the bore or below floor.
            if r.aperture_shape == "round":
                if math.hypot(bx, bz - r.leaf_cz) < r.iris_r + 0.12:
                    continue
            else:
                if abs(bx) < r.half_w + 0.06 and abs(bz - r.leaf_cz) < r.opening_h / 2.0 + 0.06:
                    continue
            if bz < 0.06:
                continue
            frame.visual(
                Box((0.028, 0.014, 0.028)),
                origin=Origin(xyz=(bx, ring_front_y - 0.007, bz)),
                material=mats["trim"],
                name=f"ring_bolt_{i}", material_class_id="metal.blackened_gunmetal",
            )
    elif r.frame_surround == "lintel_sill_side_housing":
        header_h = 0.22
        header_w = r.opening_w + 2.0 * (r.half_w * 0.62 + 0.1)
        frame_cx = 0.0
        # Lintel header.
        frame.visual(
            Box((header_w, r.frame_depth, header_h)),
            origin=Origin(xyz=(frame_cx, 0.0, r.leaf_top_z + header_h / 2.0)),
            material=mats["frame"],
            name="lintel_header", material_class_id="tech.scifi_panel",
        )
        frame.visual(
            Box((header_w * 0.96, 0.03, header_h * 0.5)),
            origin=Origin(
                xyz=(frame_cx, -r.frame_depth / 2.0 - 0.015, r.leaf_top_z + header_h * 0.55)
            ),
            material=mats["trim"],
            name="header_trim", material_class_id="metal.blackened_gunmetal",
        )
        # Floor sill.
        frame.visual(
            Box((header_w, r.frame_depth, r.sill_h)),
            origin=Origin(xyz=(frame_cx, 0.0, r.sill_h / 2.0)),
            material=mats["frame"],
            name="sill", material_class_id="tech.scifi_panel",
        )
        # Side jambs framing the opening (closing the bore sides on a lintel).
        jamb_w = max(0.06, (header_w - r.opening_w) / 2.0)
        for s, jname in ((-1.0, "left_jamb"), (1.0, "right_jamb")):
            jcx = s * (r.opening_w / 2.0 + jamb_w / 2.0)
            frame.visual(
                Box((jamb_w, r.frame_depth, r.opening_h)),
                origin=Origin(xyz=(jcx, 0.0, r.leaf_cz)),
                material=mats["frame"],
                name=jname, material_class_id="tech.scifi_panel",
            )
        # Warning lamps on the header trim.
        for s, lname in ((-1.0, "warning_lamp_l"), (1.0, "warning_lamp_r")):
            frame.visual(
                Box((0.10, 0.012, 0.05)),
                origin=Origin(
                    xyz=(s * 0.42, -r.frame_depth / 2.0 - 0.036, r.leaf_top_z + header_h * 0.55)
                ),
                material=mats["accent"],
                name=lname, material_class_id="tech.emissive_surface",
            )
    else:  # hex_beveled_slab
        frame.visual(
            mesh_from_cadquery(_hex_slab_mesh(r), "hex_slab"),
            material=mats["frame"],
            name="frame_slab", material_class_id="tech.scifi_panel",
        )
        # Chamfer trim + bolts (inline, Rule 1).
        for sx in (-1.0, 1.0):
            for bz, btag in (
                (r.sill_h + 0.25, "lo"),
                (r.leaf_cz, "mid"),
                (r.leaf_top_z - 0.10, "hi"),
            ):
                frame.visual(
                    Box((0.03, 0.012, 0.03)),
                    origin=Origin(xyz=(sx * (r.half_w + 0.18), frame_front_y - 0.006, bz)),
                    material=mats["trim"],
                    name=f"bolt_{'l' if sx < 0 else 'r'}_{btag}", material_class_id="metal.blackened_gunmetal",
                )

    # --- Shared fixed greebles for all surrounds (Rule 1: inline visuals). ---
    # The exposed face of every surround is at frame_front_y; greebles embed
    # their back into that face (so they touch the surround and are not islands)
    # and stand proud toward `out` (the viewer side). For the bulkhead the
    # exposed face is the -Y ring front; for hex/lintel it is the +Y slab face.
    out = (
        -1.0
        if (
            r.frame_surround == "circular_bulkhead_ring"
            and r.opening_mechanism != "iris_radial_slide"
        )
        else 1.0
    )
    face_y = frame_front_y
    strip_h = r.opening_h * 0.62
    backing_w = 0.05
    if r.opening_mechanism == "iris_radial_slide":
        # Straddle the disc front face (poke slightly proud) so each backing box
        # overlaps the front-face convex hull of the disc's collision mesh. A
        # fully BURIED box lands in a VHACD concavity gap over the radial slots
        # and reads as a floating island in the connectivity gate. Keep greebles
        # outside the round bore.
        face_y = frame_front_y - 0.004
        flank_x = _iris_radial_bore_r(r) + 0.18
    elif r.aperture_shape == "round":
        flank_x = r.iris_r + 0.14
    else:
        flank_x = r.half_w + 0.02
    for s, tag in ((-1.0, "0"), (1.0, "1")):
        # Backing straddles the face (embeds ~0.012 into the surround).
        frame.visual(
            Box((backing_w, 0.023, strip_h)),
            origin=Origin(xyz=(s * (flank_x + backing_w / 2.0), face_y + out * 0.0, r.leaf_cz)),
            material=mats["trim"],
            name=f"strip_backing_{tag}", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            Box((0.018, 0.012, strip_h - 0.06)),
            origin=Origin(xyz=(s * (flank_x + backing_w / 2.0), face_y + out * 0.015, r.leaf_cz)),
            material=mats["glow"],
            name=f"light_strip_{tag}", material_class_id="tech.emissive_surface",
        )

    # Keypad cluster on the left side (inline visuals, no joint — Rule 1).
    kp_cx = -(flank_x + 0.12)
    kp_y = face_y + out * 0.018
    kp_z = r.leaf_cz + r.opening_h * 0.10
    frame.visual(
        Box((0.12, 0.05, 0.18)),
        origin=Origin(xyz=(kp_cx, kp_y, kp_z)),
        material=mats["trim"],
        name="keypad_box", material_class_id="metal.blackened_gunmetal",
    )
    # Screen + keys embed into the box's exposed (out-facing) face.
    frame.visual(
        Box((0.085, 0.014, 0.045)),
        origin=Origin(xyz=(kp_cx, kp_y + out * 0.022, kp_z + 0.05)),
        material=mats["glow"],
        name="keypad_screen", material_class_id="tech.control_interface",
    )
    for rr in range(3):
        for cc in range(3):
            frame.visual(
                Box((0.02, 0.018, 0.02)),
                origin=Origin(
                    xyz=(kp_cx + (cc - 1) * 0.028, kp_y + out * 0.022, kp_z - 0.02 - rr * 0.028)
                ),
                material=mats["rib"],
                name=f"key_{rr}_{cc}", material_class_id="plastic.opaque_glossy_molded",
            )
    # Status lamp seated just above the keypad box top (touches the box so it is
    # not a floating island; box spans kp_z +/- 0.09).
    frame.visual(
        Box((0.05, 0.014, 0.025)),
        origin=Origin(xyz=(kp_cx, kp_y + out * 0.022, kp_z + 0.10)),
        material=mats["status"],
        name="status_lamp", material_class_id="tech.emissive_surface",
    )

    # Hazard chevron blocks at the lower corners (inline, Rule 1).
    haz_w, haz_h = 0.24, 0.28
    haz_z = r.sill_h + haz_h / 2.0 + 0.18
    for s, tag in ((-1.0, "l"), (1.0, "r")):
        hcx = s * (flank_x + 0.10)
        # Backing block straddles the face (embeds into the surround).
        frame.visual(
            Box((haz_w, 0.024, haz_h)),
            origin=Origin(xyz=(hcx, face_y, haz_z)),
            material=mats["rib"],
            name=f"hazard_back_{tag}", material_class_id="metal.blackened_gunmetal",
        )
        # Stripes embed into the hazard_back block (each diagonal bar touches the
        # back block and stays part of the connected island).
        frame.visual(
            mesh_from_cadquery(
                _make_hazard_stripes(haz_w * 0.9, haz_h * 0.9), f"hazard_stripes_{tag}"
            ),
            origin=Origin(
                xyz=(hcx, face_y + out * 0.006, haz_z), rpy=(0.0, 0.0, 0.0 if s < 0 else math.pi)
            ),
            material=mats["accent"],
            name=f"hazard_stripes_{tag}", material_class_id="metal.paint_coated",
        )

    frame.inertial = Inertial.from_geometry(
        Box((r.opening_w + 0.6, r.frame_depth, r.sill_h + r.opening_h + 0.2)),
        mass=120.0,
        origin=Origin(xyz=(0.0, 0.0, (r.sill_h + r.opening_h) / 2.0)),
    )
    return frame


def _make_hazard_stripes(block_w: float, block_h: float) -> cq.Workplane:
    """Diagonal yellow hazard bands clipped to a block face (S2)."""
    band, gap, thk = 0.045, 0.045, 0.008
    diag = block_w + block_h
    step = band + gap
    n = int(diag / step) + 2
    slashes: cq.Workplane | None = None
    for k in range(-n, n + 1):
        c = k * step * math.sqrt(2.0)
        bar = (
            cq.Workplane("XZ")
            .center(c / 2.0, 0.0)
            .rect(band, diag * 1.6)
            .extrude(thk)
            .rotate((0, 0, 0), (0, 1, 0), 45.0)
        )
        slashes = bar if slashes is None else slashes.union(bar)
    assert slashes is not None
    clip = (
        cq.Workplane("XZ")
        .rect(block_w, block_h)
        .extrude(thk * 2.0)
        .translate((0.0, thk * 0.5, 0.0))
    )
    return slashes.intersect(clip)


# ===========================================================================
# Seam-motif helpers (Slot C) — leaf face geometry, inlined per moving part.
# Each returns a CadQuery solid in the leaf-local frame.
# ===========================================================================
def _cosine_seam_pts(r: ResolvedScifiGateConfig, side: float) -> list[tuple[float, float]]:
    n = 24
    pts = []
    for i in range(n + 1):
        t = i / n
        z = r.sill_h + t * r.opening_h
        x = _SEAM_AMP * math.cos(t * math.pi * 3.0) + side * _SEAM_CLEAR
        pts.append((x, z))
    return pts


def _zigzag_seam_pts(r: ResolvedScifiGateConfig, side: float) -> list[tuple[float, float]]:
    h = r.opening_h
    a = _TOOTH
    base = [(+a, 0.0), (-a, h * 0.25), (+a, h * 0.50), (-a, h * 0.75), (+a, h)]
    return [(x + side * _SEAM_CLEAR, r.sill_h + z) for (x, z) in base]


def _inner_seam_leaf_mesh(r: ResolvedScifiGateConfig, side: float, zigzag: bool):
    """Inner telescope seam leaf: seam edge + straight outer edge (S1/S2)."""
    seam = _zigzag_seam_pts(r, side) if zigzag else _cosine_seam_pts(r, side)
    edge_x = side * r.a_out
    pts = list(seam)
    pts.append((edge_x, r.sill_h + r.opening_h))
    pts.append((edge_x, r.sill_h))
    leaf = cq.Workplane("XZ").polyline(pts).close().extrude(r.door_thk)
    leaf = leaf.translate((0.0, r.door_thk / 2.0, 0.0))
    return leaf


def _seam_accent_mesh(r: ResolvedScifiGateConfig, side: float, zigzag: bool):
    """Yellow ribbon hugging the seam edge (S2 _make_inner_accent)."""
    strip = 0.06
    outer = _zigzag_seam_pts(r, side) if zigzag else _cosine_seam_pts(r, side)
    inner = [(x + side * strip, z) for (x, z) in outer]
    pts = outer + list(reversed(inner))
    ribbon_thk = r.door_thk * 0.5
    ribbon = cq.Workplane("XZ").polyline(pts).close().extrude(ribbon_thk)
    ribbon = ribbon.translate((0.0, -r.door_thk / 2.0 + ribbon_thk - 0.006, 0.0))
    return ribbon


def _flat_armor_leaf_mesh(width: float, height: float, thk: float):
    """Flat armoured plate with chamfered long edges (S9 _make_leaf_panel)."""
    panel = cq.Workplane("XY").box(width, thk, height, centered=(True, True, True))
    panel = panel.edges("|X").chamfer(0.008)
    return panel


# Radial-wedge mesh helpers (iris) -------------------------------------------
_LEAF_INNER_ARC_R = (
    0.008  # tiny centre-tip radius; no fixed centre spider (all wedges converge here)
)


_IRIS_RADIAL_GAP_DEG = 1.2  # thin running seam between adjacent closed wedges


def _iris_radial_bore_r(r: ResolvedScifiGateConfig) -> float:
    """Round aperture radius for the radial iris (wedges overlap the rim)."""
    return max(0.12, r.leaf_outer_r - 0.03)


def _radial_wedge_half_span(n: int) -> float:
    """Half angular span (radians) of one closed radial wedge sector."""
    span_deg = 360.0 / n
    return math.radians((span_deg - _IRIS_RADIAL_GAP_DEG) / 2.0)


def _leaf_wedge_mesh(r: ResolvedScifiGateConfig, n: int):
    """Pie-wedge radial iris leaf, authored pointing +X (angle 0), straddling
    y=0 so the part-local origin (= the shared radial joint origin at the
    aperture centre) sits inside the wedge tip.

    Each leaf is IDENTICAL geometry; the joint frame's rpy=(0,-theta_i,0)
    rotates it into its 360/N sector. Authoring the wedge at absolute angle
    theta_c AND rotating the joint by theta_i (the old code) double-rotated the
    wedge to 2*theta_i and scattered the leaves off the centre — this version
    fixes that. The fixed centre spider from the source variants is omitted:
    support is derived from each leaf's outer guide shoe riding its carved wall
    slot, and every leaf is a mimic of leaf_0 so none can float."""
    half_span = _radial_wedge_half_span(n)
    a0, a1 = -half_span, half_span
    inner_r = _LEAF_INNER_ARC_R
    n_arc = 18
    pts: list[tuple[float, float]] = []
    for k in range(n_arc + 1):
        a = a0 + (a1 - a0) * k / n_arc
        pts.append((inner_r * math.cos(a), inner_r * math.sin(a)))
    for k in range(n_arc + 1):
        a = a1 - (a1 - a0) * k / n_arc
        pts.append((r.leaf_outer_r * math.cos(a), r.leaf_outer_r * math.sin(a)))
    wedge = cq.Workplane("XZ").polyline(pts).close().extrude(_LEAF_THICK)
    wedge = wedge.translate((0.0, -_LEAF_THICK / 2.0, 0.0))
    return wedge


def _leaf_stripe_mesh(r: ResolvedScifiGateConfig, n: int):
    """Accent arc band near the wedge outer edge, authored at angle 0."""
    half_span = _radial_wedge_half_span(n) * 0.72
    a0, a1 = -half_span, half_span
    r0 = r.leaf_outer_r - 0.10
    r1 = r.leaf_outer_r - 0.02
    n_arc = 12
    pts: list[tuple[float, float]] = []
    for k in range(n_arc + 1):
        a = a0 + (a1 - a0) * k / n_arc
        pts.append((r0 * math.cos(a), r0 * math.sin(a)))
    for k in range(n_arc + 1):
        a = a1 - (a1 - a0) * k / n_arc
        pts.append((r1 * math.cos(a), r1 * math.sin(a)))
    stripe = cq.Workplane("XZ").polyline(pts).close().extrude(0.012)
    stripe = stripe.translate((0.0, -0.006 + _LEAF_THICK / 2.0, 0.0))
    return stripe


def _round_disc_slab_mesh(r: ResolvedScifiGateConfig) -> cq.Workplane:
    """Thick full-depth round surround disc for the radial iris: a round bore
    cut through, plus N mid-plane radial wedge slots that receive the leaves
    when they retract, so an open gate is a true through-hole and a retracting
    wedge hides inside the wall (no tunnelling through a solid slab). Deck-cut
    at the floor so the disc stands on z=0."""
    n = r.mech_count
    span_deg = 360.0 / n
    bore_r = _iris_radial_bore_r(r)
    depth = r.frame_depth
    cz = r.leaf_cz
    # Outer radius must contain a fully retracted wedge: [travel .. travel+R].
    slot_outer_r = r.leaf_travel + r.leaf_outer_r + 0.06
    outer_r = slot_outer_r + 0.16

    # extrude(..., both=True) keeps the disc symmetric about y=0 (front +y/2,
    # back -y/2). A plain XZ extrude runs toward -Y only, which would park the
    # whole disc behind the greeble planes.
    disc = cq.Workplane("XZ").circle(outer_r).extrude(depth / 2.0, both=True)
    bore = cq.Workplane("XZ").circle(bore_r).extrude((depth + 0.04) / 2.0, both=True)
    disc = disc.cut(bore)

    # Mid-plane radial slots (thin in Y) opening into the bore. A touch wider
    # (angular + radial) than the wedge so the leaf runs with clearance; only
    # the mid-Y band is removed so the front/back skins stay solid and hide the
    # parked wedge from the front while the bore itself reads fully open.
    slot_hy = _LEAF_THICK / 2.0 + 0.014
    slot_half = _radial_wedge_half_span(n) + math.radians(0.9)
    r_in = bore_r - 0.03
    n_arc = 16
    for i in range(n):
        theta_c = math.radians(i * span_deg)
        a0, a1 = theta_c - slot_half, theta_c + slot_half
        pts: list[tuple[float, float]] = []
        for k in range(n_arc + 1):
            a = a0 + (a1 - a0) * k / n_arc
            pts.append((r_in * math.cos(a), r_in * math.sin(a)))
        for k in range(n_arc + 1):
            a = a1 - (a1 - a0) * k / n_arc
            pts.append((slot_outer_r * math.cos(a), slot_outer_r * math.sin(a)))
        slot = cq.Workplane("XZ").polyline(pts).close().extrude(slot_hy, both=True)
        disc = disc.cut(slot)

    disc = disc.translate((0.0, 0.0, cz))
    # Deck cut: drop everything below the floor (z < 0).
    deck = (
        cq.Workplane("XY")
        .box(2.0 * outer_r + 0.4, depth + 0.4, 6.0, centered=(True, True, True))
        .translate((0.0, 0.0, -3.0))
    )
    disc = disc.cut(deck)
    return disc


# ===========================================================================
# Mechanism factories (Slot A). Each parents moving parts to `frame`.
# ===========================================================================
def _drive_anchor(
    frame, child, world_origin, mats, name: str, *, sill_h: float, size=(0.05, 0.022, 0.05)
):
    """Anchor a moving child's joint to real hardware (satisfies the flat 0.015
    articulation-origin baseline).

    Emits (a) a compact flush guide socket on the fixed ``frame`` centred at the
    joint's world origin so ``parent_distance`` ~ 0, and (b) a thin slider shoe
    on the moving ``child`` centred at its part-local origin (= the joint origin)
    so ``child_distance`` ~ 0. Earlier versions used tall sill posts here; those
    sat directly in the sliding sweep. The compact socket keeps the mating
    constraint without placing a visible upright obstruction in the doorway.
    """
    ox, oy, oz = world_origin
    sx, sy, sz = size
    socket_h = min(sz, 0.030)
    frame.visual(
        Box((sx, sy, socket_h)),
        origin=Origin(xyz=(ox, oy, oz)),
        material=mats["rib"],
        name=f"{name}_boss", material_class_id="metal.blackened_gunmetal",
    )
    # Child slider shoe: a stub whose +Y face sits ON the part-local origin (so
    # child_distance ~ 0) and which extends back through the leaf's rear face so
    # it makes real surface contact with the leaf (not a buried island). Length
    # 0.09 in Y reliably pokes past a 0.06-thick leaf at either plane.
    shoe_len = 0.09
    child.visual(
        Box((sx * 0.7, shoe_len, sz * 0.7)),
        origin=Origin(xyz=(0.0, -shoe_len / 2.0 + 0.0005, 0.0)),
        material=mats["rib"],
        name="drive_shoe", material_class_id="metal.blackened_gunmetal",
    )


def _guide_rail_visuals(frame, r: ResolvedScifiGateConfig, mats):
    """Top/bottom dark guide rails that capture lateral / lift leaves. Inline
    visuals on the frame (Rule 1); the leaves ride captured (allow_overlap).

    The rails span Y from in front of the leaf planes all the way back to the
    surround's deepest plane so they embed into whichever surround is present
    (front/full slab, lintel beam/sill, or back ring) and stay connected."""
    guide_half_len = r.half_w + r.pocket_right_w + 0.10
    y_front = _B_PLANE_Y + 0.04
    y_back = -r.frame_depth / 2.0
    guide_depth = y_front - y_back
    guide_cy = (y_front + y_back) / 2.0
    capture = 0.012
    top_h, bot_h = 0.06, 0.04
    frame.visual(
        Box((2.0 * guide_half_len, guide_depth, top_h)),
        origin=Origin(xyz=(0.0, guide_cy, r.leaf_top_z - capture + top_h / 2.0)),
        material=mats["trim"],
        name="top_track", material_class_id="metal.blackened_gunmetal",
    )
    frame.visual(
        Box((2.0 * guide_half_len, guide_depth, bot_h)),
        origin=Origin(xyz=(0.0, guide_cy, r.sill_h + capture - bot_h / 2.0)),
        material=mats["trim"],
        name="bottom_track", material_class_id="metal.blackened_gunmetal",
    )


def _sliding_wall_pocket_visuals(
    frame,
    r: ResolvedScifiGateConfig,
    mats,
    *,
    left: bool,
    right: bool,
    right_extra: bool = False,
):
    """Dark back-liner + mouth lips lining the carved side wall pockets.

    The pocket CAVITY itself is boolean-carved into the hex slab
    (``_carve_side_pockets``); this only adds a thin dark liner at the BACK of the
    cavity (behind the leaf sweep, embedded into the back skin so it stays
    connected) plus a slim mouth lip, so the recess reads as a real dark wall
    slot. Only emitted for the carved hex slab — on the open lintel/bulkhead
    surrounds there is no solid side wall, so the leaf simply parks on its track
    with nothing to line and nothing to clip.
    """
    if r.frame_surround != "hex_beveled_slab":
        return
    slot_h = r.opening_h - 0.02
    # Liner sits just behind the rearmost leaf plane (outside the leaf sweep).
    liner_y = _LATERAL_LEAF_Y_LO - 0.012
    for side, tag, enabled in ((-1.0, "left", left), (1.0, "right", right)):
        if not enabled:
            continue
        reach = _lateral_open_reach(r)
        x_in = r.half_w + 0.02
        x_out = reach + (0.10 if (side > 0.0 and right_extra) else 0.06)
        if x_out <= x_in:
            continue
        liner_w = x_out - x_in
        liner_cx = side * (x_in + x_out) / 2.0
        frame.visual(
            Box((liner_w, 0.03, slot_h)),
            origin=Origin(xyz=(liner_cx, liner_y, r.leaf_cz)),
            material=mats["armor_deep"],
            name=f"{tag}_wall_pocket_liner", material_class_id="metal.blackened_gunmetal",
        )


def _build_biparting_lateral_telescope(model, frame, r, mats) -> list[str]:
    """4 leaves (door_0/1 + _outer), ±X PRISMATIC mimic chain (S1/S2).

    Each leaf is authored in its OWN part-local frame whose origin is the leaf's
    low drive point (so the prismatic joint origin lands on real hardware and the
    child geometry contains its local origin); the leaf visuals are shifted by
    -anchor so they sit at the correct absolute world pose at q=0."""
    _guide_rail_visuals(frame, r, mats)
    _sliding_wall_pocket_visuals(frame, r, mats, left=True, right=True)
    zigzag = r.seam_motif == "zigzag_dovetail_seam"
    flat = r.seam_motif == "flat_armor_plate"
    panel_h = r.opening_h
    parts: list[str] = []
    # Drive point kept low so its frame boss/socket lands ON the bottom guide
    # rail (real hardware) instead of floating in the open bore. The joint Z is
    # irrelevant to the ±X slide, so this only moves the anchor, not the leaf.
    drive_z = r.sill_h + 0.02
    b_out = r.half_w - 0.025

    # door_0 (right inner, +X side), door_1 (left inner, -X side).
    for tag, side in (("0", 1.0), ("1", -1.0)):
        part = model.part(f"door_{tag}")
        ax = side * r.a_out * 0.45  # anchor inside the leaf body
        # Visuals are authored relative to the joint origin (which already carries
        # the A-plane Y); the leaf mesh is Y-centred so its visual Y origin is 0.
        if flat:
            inner_w = r.a_out
            part.visual(
                mesh_from_cadquery(
                    _flat_armor_leaf_mesh(inner_w, panel_h, r.door_thk), f"leaf_{tag}"
                ),
                origin=Origin(xyz=(side * inner_w / 2.0 - ax, 0.0, r.leaf_cz - drive_z)),
                material=mats["armor"],
                name="leaf_panel", material_class_id="tech.scifi_panel",
            )
        else:
            part.visual(
                mesh_from_cadquery(_inner_seam_leaf_mesh(r, side, zigzag), f"leaf_{tag}"),
                origin=Origin(xyz=(-ax, 0.0, -drive_z)),
                material=mats["armor"],
                name="leaf_panel", material_class_id="tech.scifi_panel",
            )
        part.inertial = Inertial.from_geometry(
            Box((r.a_out, r.door_thk, panel_h)),
            mass=14.0,
            origin=Origin(xyz=(side * r.a_out / 2.0 - ax, 0.0, r.leaf_cz - drive_z)),
        )
        o = (ax, _A_PLANE_Y, drive_z)
        if tag == "0":
            model.articulation(
                "door_0_slide",
                ArticulationType.PRISMATIC,
                parent=frame,
                child=part,
                origin=Origin(xyz=o),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=600.0, velocity=0.5, lower=0.0, upper=r.travel_a),
            )
        else:
            model.articulation(
                "door_1_slide",
                ArticulationType.PRISMATIC,
                parent=frame,
                child=part,
                origin=Origin(xyz=o),
                axis=(-1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=600.0, velocity=0.5, lower=0.0, upper=r.travel_a),
                mimic=Mimic(joint="door_0_slide", multiplier=1.0, offset=0.0),
            )
        _drive_anchor(frame, part, o, mats, f"door_{tag}", sill_h=r.sill_h)
        parts.append(f"door_{tag}")

    # outer leaves (rear plane), grey panels. Outer edge insets from the jamb.
    b_w = b_out - r.b_in
    for tag, side in (("0", 1.0), ("1", -1.0)):
        part = model.part(f"door_{tag}_outer")
        b_cx = side * (r.b_in + b_out) / 2.0
        ax = b_cx  # anchor at the outer-leaf centre
        part.visual(
            Box((b_w, r.door_thk, panel_h)),
            origin=Origin(xyz=(0.0, 0.0, r.leaf_cz - drive_z)),
            material=mats["armor_deep"],
            name="leaf_panel", material_class_id="tech.scifi_panel",
        )
        for gz in (r.leaf_cz - 0.5, r.leaf_cz, r.leaf_cz + 0.5):
            part.visual(
                Box((b_w - 0.06, 0.008, 0.022)),
                origin=Origin(xyz=(0.0, -r.door_thk / 2.0 - 0.004, gz - drive_z)),
                material=mats["trim"],
                name=f"groove_{int((gz - r.leaf_cz) * 100)}", material_class_id="metal.blackened_gunmetal",
            )
        part.inertial = Inertial.from_geometry(
            Box((b_w, r.door_thk, panel_h)),
            mass=10.0,
            origin=Origin(xyz=(0.0, 0.0, r.leaf_cz - drive_z)),
        )
        o = (ax, _B_PLANE_Y, drive_z)
        model.articulation(
            f"door_{tag}_outer_slide",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=part,
            origin=Origin(xyz=o),
            axis=(side, 0.0, 0.0),
            motion_limits=MotionLimits(effort=600.0, velocity=0.25, lower=0.0, upper=r.travel_b),
            mimic=Mimic(joint="door_0_slide", multiplier=0.5, offset=0.0),
        )
        _drive_anchor(frame, part, o, mats, f"door_{tag}_outer", sill_h=r.sill_h)
        parts.append(f"door_{tag}_outer")
    return parts


def _build_single_leaf_sliding_pocket(model, frame, r, mats) -> list[str]:
    """1 full-width leaf + rear stage, +X PRISMATIC driver + ×0.5 mimic (S9).

    Leaves authored in part-local frames anchored at their low drive point."""
    _guide_rail_visuals(frame, r, mats)
    _sliding_wall_pocket_visuals(frame, r, mats, left=False, right=True, right_extra=True)
    panel_h = r.opening_h
    leaf_w = r.opening_w
    # Drive point kept low so its frame boss/socket lands ON the bottom guide
    # rail (real hardware) instead of floating in the open bore. The joint Z is
    # irrelevant to the ±X slide, so this only moves the anchor, not the leaf.
    drive_z = r.sill_h + 0.02

    door0 = model.part("door_0")
    door0.visual(
        mesh_from_cadquery(_flat_armor_leaf_mesh(leaf_w, panel_h, r.door_thk), "leaf_0"),
        origin=Origin(xyz=(0.0, 0.0, r.leaf_cz - drive_z)),
        material=mats["armor"],
        name="leaf_panel", material_class_id="tech.scifi_panel",
    )
    door0.inertial = Inertial.from_geometry(
        Box((leaf_w, r.door_thk, panel_h)),
        mass=20.0,
        origin=Origin(xyz=(0.0, 0.0, r.leaf_cz - drive_z)),
    )

    # Rear stage (slightly narrower, in the rear plane).
    rear_w = leaf_w * 0.55
    rear_cx = r.half_w * 0.4
    door0o = model.part("door_0_outer")
    door0o.visual(
        Box((rear_w, r.door_thk, panel_h)),
        origin=Origin(xyz=(0.0, 0.0, r.leaf_cz - drive_z)),
        material=mats["armor_deep"],
        name="leaf_panel", material_class_id="tech.scifi_panel",
    )
    door0o.inertial = Inertial.from_geometry(
        Box((rear_w, r.door_thk, panel_h)),
        mass=12.0,
        origin=Origin(xyz=(0.0, 0.0, r.leaf_cz - drive_z)),
    )

    o_inner = (0.0, _A_PLANE_Y, drive_z)
    o_outer = (rear_cx, _B_PLANE_Y, drive_z)
    driver = model.articulation(
        "door_0_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=door0,
        origin=Origin(xyz=o_inner),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=700.0, velocity=0.5, lower=0.0, upper=r.travel_a),
    )
    _drive_anchor(frame, door0, o_inner, mats, "door_0", sill_h=r.sill_h)
    model.articulation(
        "door_0_outer_slide",
        ArticulationType.PRISMATIC,
        parent=frame,
        child=door0o,
        origin=Origin(xyz=o_outer),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=700.0, velocity=0.25, lower=0.0, upper=r.travel_b),
        mimic=Mimic(joint=driver.name, multiplier=0.5, offset=0.0),
    )
    _drive_anchor(frame, door0o, o_outer, mats, "door_0_outer", sill_h=r.sill_h)
    return ["door_0", "door_0_outer"]


def _build_vertical_lift(model, frame, r, mats) -> list[str]:
    """N horizontal slabs, ±Z PRISMATIC. Overhead-staggered (all +Z) for odd N,
    bi-parting even-pitch (lower −Z / upper +Z) for even N (S3/S4)."""
    n = r.mech_count
    slab_pitch = r.opening_h / n
    slab_h = min(0.05, slab_pitch * 0.55)
    slab_thk = r.door_thk
    slab_w = r.opening_w
    louver = r.seam_motif == "horizontal_louver_slab"

    # Vertical guide channels at each jamb (inline, Rule 1). They capture the
    # slab ends at x=+/-half_w AND must embed into the surround solid to stay
    # connected: on the hex slab the doorway bore is cut with a small margin
    # beyond the opening width, so the channel extends OUTWARD past that margin
    # (outer edge at half_w + 0.15) to sink into the slab; the inner edge stays
    # near half_w so the slab joint origin (on the channel, at x=-half_w) is
    # inside the channel solid (distance ~0 to its surface).
    guide_ch_h = r.opening_h
    guide_w = 0.16
    guide_cx = r.half_w + 0.07  # inner edge ~half_w-0.01, outer edge ~half_w+0.15
    for s, cname in ((-1.0, "left_guide"), (1.0, "right_guide")):
        frame.visual(
            Box((guide_w, 0.08, guide_ch_h)),
            origin=Origin(xyz=(s * guide_cx, 0.0, r.leaf_cz)),
            material=mats["trim"],
            name=cname, material_class_id="metal.blackened_gunmetal",
        )

    biparting = n % 2 == 0
    parts: list[str] = []
    # The slab part-local origin sits on the LEFT guide channel; the slab body
    # is authored at local +half_w so it ends up centred at world x=0 while the
    # part origin (= joint origin) lands on real guide hardware.
    sx0 = r.half_w
    for i in range(n):
        slab = model.part(f"slab_{i}")
        slab.visual(
            Box((slab_w, slab_thk, slab_h)),
            origin=Origin(xyz=(sx0, 0.0, 0.0)),
            material=mats["armor"],
            name="slab_body", material_class_id="tech.scifi_panel",
        )
        if louver:
            slab.visual(
                Box((slab_w * 0.88, 0.006, 0.010)),
                origin=Origin(xyz=(sx0, -slab_thk / 2.0 + 0.001, -slab_h / 2.0 + 0.006)),
                material=mats["accent"],
                name="accent_line", material_class_id="metal.paint_coated",
            )
            slab.visual(
                Box((slab_w * 0.5, 0.006, 0.008)),
                origin=Origin(xyz=(sx0, -slab_thk / 2.0 + 0.001, 0.0)),
                material=mats["rib"],
                name="center_rib", material_class_id="metal.blackened_gunmetal",
            )
        else:
            slab.visual(
                Box((slab_w * 0.84, 0.008, 0.014)),
                origin=Origin(xyz=(sx0, -slab_thk / 2.0 + 0.001, 0.0)),
                material=mats["accent"],
                name="accent_line", material_class_id="metal.paint_coated",
            )
        # Guide shoe at the part-local origin (rides in the left guide channel).
        slab.visual(
            Box((0.05, 0.07, slab_h * 0.9)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["rib"],
            name="guide_shoe", material_class_id="metal.blackened_gunmetal",
        )
        slab.inertial = Inertial.from_geometry(
            Box((slab_w, slab_thk, slab_h)),
            mass=8.0,
            origin=Origin(xyz=(sx0, 0.0, 0.0)),
        )
        parts.append(f"slab_{i}")

    # Joints: ONE coupled PRISMATIC ±Z DOF. slab_0 is the driver; every other
    # slab mimics it. Because the slabs telescope-nest at DIFFERENT rates, each
    # mimic multiplier is travel_i / travel_0 (staggered). Coupling to a single
    # DOF means the gate can only be sampled fully-closed → fully-open together,
    # so no mixed pose (slab_0 lifted + slab_2 closed) can stack them in a shared
    # swept volume — the reason the old pairwise slab allow_overlaps existed.
    nest_gap = slab_h + 0.004
    # First resolve each slab's axis + travel so slabs nest with >= slab_h
    # spacing at BOTH the closed pose (pitch apart) and the open pose (nest_gap
    # apart); linear coupling keeps the gap between those bounds at every pose.
    specs: list[tuple[tuple[float, float, float], float]] = []
    for i in range(n):
        rest_cz = r.sill_h + (i + 0.5) * slab_pitch
        if biparting:
            # lower half nests DOWN toward the sill (bottom slab lowest), upper
            # half nests UP under the header (top slab highest); the two halves
            # part away from each other so they never share a volume.
            if i < n // 2:
                axis = (0.0, 0.0, -1.0)
                open_cz = r.sill_h + slab_h * 0.5 + i * nest_gap
                travel = rest_cz - open_cz
            else:
                axis = (0.0, 0.0, 1.0)
                header_top = r.leaf_top_z + 0.18 - slab_h * 0.5
                open_cz = header_top - (n - 1 - i) * nest_gap
                travel = open_cz - rest_cz
        else:
            # overhead staggered: all +Z, bottom slab travels farthest.
            axis = (0.0, 0.0, 1.0)
            nest_top = r.leaf_top_z + 0.18 - slab_h / 2.0
            open_cz = nest_top - (n - 1 - i) * nest_gap
            travel = open_cz - rest_cz
        specs.append((axis, max(0.05, travel)))

    travel_0 = specs[0][1]
    for i in range(n):
        axis, travel = specs[i]
        rest_cz = r.sill_h + (i + 0.5) * slab_pitch
        art = model.articulation(
            f"slab_{i}_slide",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=model.get_part(f"slab_{i}"),
            origin=Origin(xyz=(-r.half_w, 0.0, rest_cz)),
            axis=axis,
            motion_limits=MotionLimits(effort=400.0, velocity=0.4, lower=0.0, upper=travel),
        )
        if i > 0:
            art.mimic = Mimic(joint="slab_0_slide", multiplier=travel / travel_0, offset=0.0)
    return parts


def _build_iris_radial_slide(model, frame, r, mats) -> list[str]:
    """N pie-wedge leaves, radial PRISMATIC: leaf_0 driver + (N-1) ×1.0 (S8).

    The leaves now derive their support from outer rim pockets instead of a
    centre spider. Closed pose brings the leaf tips together at the aperture
    centre; positive travel retracts each leaf outward into its wall slot.
    """
    n = r.mech_count
    span_deg = 360.0 / n
    # The shared radial prismatic joint origin sits on the bore rim at the wedge
    # OUTER arc (anchor_r), where both a fixed frame guide pad and the leaf's
    # guide shoe provide real hardware (the aperture centre is a through-hole, so
    # the joint cannot live there). Each wedge is authored pointing +X (angle 0)
    # with its apex at the mesh origin; shifting the visual by -anchor_r in the
    # part-local frame puts the apex at the aperture centre, and the joint frame
    # rpy=(0,-theta_i,0) rotates the whole leaf into its 360/N sector. axis is
    # the part-local +X, so positive travel drives the wedge radially OUTWARD,
    # withdrawing its tip past the bore rim into the carved wall slot.
    anchor_r = r.leaf_outer_r

    # Fixed frame guide pads (full surround depth so they fuse with the disc's
    # front + back skins and stay one connected island; the mid-plane slot only
    # removes the skinless band between them). One per leaf at its rim anchor.
    for i in range(n):
        theta_i = math.radians(i * span_deg)
        frame.visual(
            Box((0.050, r.frame_depth, 0.050)),
            origin=Origin(
                xyz=(anchor_r * math.cos(theta_i), 0.0, r.leaf_cz + anchor_r * math.sin(theta_i)),
                rpy=(0.0, -theta_i, 0.0),
            ),
            material=mats["rib"],
            name=f"radial_joint_pad_{i}", material_class_id="metal.blackened_gunmetal",
        )

    wedge_geom = mesh_from_cadquery(_leaf_wedge_mesh(r, n), "wedge")
    stripe_geom = mesh_from_cadquery(_leaf_stripe_mesh(r, n), "stripe")
    parts: list[str] = []
    for i in range(n):
        leaf = model.part(f"leaf_{i}")
        leaf.visual(
            wedge_geom,
            origin=Origin(xyz=(-anchor_r, 0.0, 0.0)),
            material=mats["armor"],
            name="wedge", material_class_id="tech.scifi_panel",
        )
        leaf.visual(
            stripe_geom,
            origin=Origin(xyz=(-anchor_r, 0.0, 0.0)),
            material=mats["accent"],
            name="stripe", material_class_id="metal.paint_coated",
        )
        leaf.visual(
            Box((0.050, _LEAF_THICK + 0.020, 0.045)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["rib"],
            name="outer_guide_shoe", material_class_id="metal.blackened_gunmetal",
        )
        leaf.inertial = Inertial.from_geometry(
            Box((r.leaf_outer_r, _LEAF_THICK, r.leaf_outer_r)),
            mass=5.0,
            origin=Origin(xyz=(-anchor_r / 2.0, 0.0, 0.0)),
        )
        parts.append(f"leaf_{i}")

    driver = None
    for i in range(n):
        theta_i = math.radians(i * span_deg)
        art = model.articulation(
            f"leaf_{i}_slide",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=model.get_part(f"leaf_{i}"),
            origin=Origin(
                xyz=(anchor_r * math.cos(theta_i), 0.0, r.leaf_cz + anchor_r * math.sin(theta_i)),
                rpy=(0.0, -theta_i, 0.0),
            ),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=700.0, velocity=0.5, lower=0.0, upper=r.leaf_travel),
        )
        if i == 0:
            driver = art
        else:
            art.mimic = Mimic(joint=driver.name, multiplier=1.0, offset=0.0)
    return parts


_MECHANISM_BUILDERS = {
    "biparting_lateral_telescope": _build_biparting_lateral_telescope,
    "single_leaf_sliding_pocket": _build_single_leaf_sliding_pocket,
    "vertical_lift": _build_vertical_lift,
    "iris_radial_slide": _build_iris_radial_slide,
}


# ===========================================================================
# Build
# ===========================================================================
def build_scifi_gate(
    config: ScifiGateConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"scifi_gate_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    frame = _build_surround(model, r, mats)
    _MECHANISM_BUILDERS[r.opening_mechanism](model, frame, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_scifi_gate(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_scifi_gate(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_scifi_gate_tests(
    object_model: ArticulatedObject,
    config: ScifiGateConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    mech = r.opening_mechanism

    # ---- Captured-rail / pivot / radial allowances (element-scoped). ----
    if mech == "biparting_lateral_telescope":
        leaves = ("door_0", "door_1", "door_0_outer", "door_1_outer")
        for lp in leaves:
            part = object_model.get_part(lp)
            # Captured wall pocket (Rule 2): the leaf retracts into the boolean-
            # carved side slot. The visual mesh has a real recess so it renders
            # hidden-in-wall, but the convex-hull collision proxy of the slab
            # fills that concavity, so declare the whole leaf/frame pair.
            ctx.allow_overlap(
                part,
                frame,
                reason=f"{lp} retracts captured into its carved side wall pocket.",
            )
            for rail in ("top_track", "bottom_track"):
                ctx.allow_overlap(
                    part,
                    frame,
                    elem_a="leaf_panel",
                    elem_b=rail,
                    reason=f"{lp} leaf panel rides captured inside the {rail} guide rail.",
                )
            # The leaf's drive shoe / panel is captured by the frame drive posts.
            for bn in ("door_0_boss", "door_1_boss", "door_0_outer_boss", "door_1_outer_boss"):
                for le in ("drive_shoe", "leaf_panel"):
                    ctx.allow_overlap(
                        part,
                        frame,
                        elem_a=le,
                        elem_b=bn,
                        reason=f"{lp} rides on the {bn} drive post.",
                    )
        # All four leaves converge / lap / share drive shoes at the centre when
        # closed (seam interleave + telescoping stage lap + centred drive shoes).
        door_parts = [object_model.get_part(p) for p in leaves]
        for ai in range(len(door_parts)):
            for bi in range(ai + 1, len(door_parts)):
                ctx.allow_overlap(
                    door_parts[ai],
                    door_parts[bi],
                    reason="telescope leaves interleave / lap / share centred drive shoes when closed.",
                )
    elif mech == "single_leaf_sliding_pocket":
        d0 = object_model.get_part("door_0")
        d0o = object_model.get_part("door_0_outer")
        for dp in (d0, d0o):
            ctx.allow_overlap(
                dp,
                frame,
                reason="pocket leaf retracts captured into its carved right wall pocket.",
            )
        for rail in ("top_track", "bottom_track"):
            ctx.allow_overlap(
                d0,
                frame,
                elem_a="leaf_panel",
                elem_b=rail,
                reason=f"single leaf rides captured inside the {rail} guide rail.",
            )
            ctx.allow_overlap(
                d0o,
                frame,
                elem_a="leaf_panel",
                elem_b=rail,
                reason=f"rear stage rides captured inside the {rail} guide rail.",
            )
        for dp in (d0, d0o):
            for bn in ("door_0_boss", "door_0_outer_boss"):
                ctx.allow_overlap(
                    dp,
                    frame,
                    elem_a="leaf_panel",
                    elem_b=bn,
                    reason=f"pocket leaf rides on the {bn} drive post.",
                )
                ctx.allow_overlap(
                    dp,
                    frame,
                    elem_a="drive_shoe",
                    elem_b=bn,
                    reason=f"leaf drive shoe rides on the {bn} at the centre.",
                )
        ctx.allow_overlap(
            d0,
            d0o,
            reason="the full-width leaf and its rear stage lap (2-stage telescope).",
        )
    elif mech == "vertical_lift":
        n = r.mech_count
        for i in range(n):
            slab = object_model.get_part(f"slab_{i}")
            # Captured overhead/sill housing (Rule 2): slabs nest up into the
            # header housing / down into the sill when open. The convex-hull
            # collision proxy of the header beam fills that housing, so declare
            # the whole slab/frame pair.
            ctx.allow_overlap(
                slab,
                frame,
                reason=f"slab_{i} nests captured into the header/sill housing when open.",
            )
            for ch in ("left_guide", "right_guide", "left_jamb", "right_jamb"):
                ctx.allow_overlap(
                    slab,
                    frame,
                    elem_a="slab_body",
                    elem_b=ch,
                    reason=f"slab_{i} end rides captured at the {ch}.",
                )
            for ch in ("left_guide", "left_jamb"):
                ctx.allow_overlap(
                    slab,
                    frame,
                    elem_a="guide_shoe",
                    elem_b=ch,
                    reason=f"slab_{i} guide shoe rides captured at the {ch}.",
                )
        # No slab↔slab allowances: all slabs are mimic-coupled to slab_0 (one
        # DOF), so mixed poses are impossible and the staggered nest keeps every
        # adjacent pair >= slab_h apart at every coupled pose.
    else:  # iris_radial_slide
        n = r.mech_count
        for i in range(n):
            leaf = object_model.get_part(f"leaf_{i}")
            # The wedge and its guide shoe ride captured in the carved wall slot
            # and on the fixed rim guide pad; declare the whole leaf/frame pair.
            ctx.allow_overlap(
                leaf,
                frame,
                reason=f"leaf_{i} wedge + guide shoe ride captured in the carved "
                f"radial wall slot / on the rim guide pad.",
            )
            for j in range(i + 1, n):
                ctx.allow_overlap(
                    leaf,
                    object_model.get_part(f"leaf_{j}"),
                    elem_a="wedge",
                    elem_b="wedge",
                    reason=f"radial leaves {i} and {j} converge at the centre when closed.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "frame (surround root) present", "frame" in part_names, details=str(sorted(part_names))
    )

    aabb = ctx.part_world_aabb(frame)
    if aabb is not None:
        ctx.check(
            "frame stands on the floor",
            aabb[0][2] < 0.05,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- Mechanism joint topology + opening motion. ----
    if mech == "biparting_lateral_telescope":
        j = object_model.get_articulation("door_0_slide")
        ctx.check(
            "telescope driver is PRISMATIC about X",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        d0 = object_model.get_part("door_0")
        for lp in ("door_0", "door_1"):
            visuals = {v.name for v in object_model.get_part(lp).visuals}
            ctx.check(
                f"{lp} has no protruding seam/accent strip in the slide path",
                "leaf_seam_accent" not in visuals and "leaf_accent" not in visuals,
                details=str(sorted(visuals)),
            )
        p0 = ctx.part_world_position(d0)
        with ctx.pose({j: r.travel_a * 0.9}):
            p1 = ctx.part_world_position(d0)
        if p0 is not None and p1 is not None:
            ctx.check(
                "telescope opens (door_0 retracts +X)",
                p1[0] > p0[0] + 0.20,
                details=f"closed_x={p0[0]:.3f} open_x={p1[0]:.3f}",
            )
    elif mech == "single_leaf_sliding_pocket":
        j = object_model.get_articulation("door_0_slide")
        ctx.check(
            "pocket driver is PRISMATIC about +X",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
        d0 = object_model.get_part("door_0")
        visuals = {v.name for v in d0.visuals}
        ctx.check(
            "pocket leaf has no protruding accent/kick strip in the slide path",
            "edge_accent" not in visuals and "kick_plate" not in visuals,
            details=str(sorted(visuals)),
        )
        p0 = ctx.part_world_position(d0)
        with ctx.pose({j: r.travel_a * 0.9}):
            p1 = ctx.part_world_position(d0)
        if p0 is not None and p1 is not None:
            ctx.check(
                "pocket leaf slides +X",
                p1[0] > p0[0] + 0.30,
                details=f"closed_x={p0[0]:.3f} open_x={p1[0]:.3f}",
            )
    elif mech == "vertical_lift":
        n = r.mech_count
        j0 = object_model.get_articulation("slab_0_slide")
        ctx.check(
            "lift slab_0 is PRISMATIC about Z",
            j0.articulation_type == ArticulationType.PRISMATIC and abs(j0.axis[2]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        ctx.check(
            f"vertical_lift emits {n} slabs",
            all(f"slab_{i}" in part_names for i in range(n)),
        )
        # Every non-driver slab mimics slab_0 so the gate is a SINGLE coupled
        # DOF (spec: derived constraints) — no mixed pose can stack the slabs.
        for i in range(1, n):
            ji = object_model.get_articulation(f"slab_{i}_slide")
            mimic = getattr(ji, "mimic", None)
            ctx.check(
                f"slab_{i} mimics slab_0 (one coupled lift DOF, no mixed-pose stacking)",
                mimic is not None and getattr(mimic, "joint", None) == "slab_0_slide",
                details=str(mimic),
            )
        slab = object_model.get_part("slab_0")
        a0 = ctx.part_world_aabb(slab)
        # Only the driver is posed; the mimic-coupled slabs follow it.
        pose = {j0: j0.motion_limits.upper}
        with ctx.pose(pose):
            a1 = ctx.part_world_aabb(slab)
        if a0 is not None and a1 is not None:
            ctx.check(
                "lift slab_0 moves vertically when open",
                abs((a1[0][2] + a1[1][2]) / 2 - (a0[0][2] + a0[1][2]) / 2) > 0.10,
                details=f"closed_cz={(a0[0][2] + a0[1][2]) / 2:.3f} open_cz={(a1[0][2] + a1[1][2]) / 2:.3f}",
            )
    else:  # iris_radial_slide
        n = r.mech_count
        j0 = object_model.get_articulation("leaf_0_slide")
        frame_visuals = {v.name for v in frame.visuals}
        ctx.check(
            "radial leaf_0 is PRISMATIC (radial)",
            j0.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        ctx.check(
            "iris_radial leaf count supports centre-closing 2..8 variants",
            LEAF_N_MIN <= n <= LEAF_N_MAX,
            details=f"n={n}",
        )
        ctx.check(
            "iris_radial has no fixed centre spider/hub",
            "hub" not in frame_visuals,
            details=str(sorted(name for name in frame_visuals if "hub" in str(name))),
        )
        ctx.check(
            "iris_radial surround is the round disc (frame_slab)",
            "frame_slab" in frame_visuals,
            details=str(sorted(frame_visuals)),
        )
        ctx.check(
            "iris_radial emits a fixed rim guide pad for every leaf",
            all(f"radial_joint_pad_{i}" in frame_visuals for i in range(n)),
            details=str(
                sorted(name for name in frame_visuals if str(name).startswith("radial_joint_pad_"))
            ),
        )
        ctx.check(
            f"iris_radial emits {n} leaves",
            all(f"leaf_{i}" in part_names for i in range(n)),
        )
        for i in range(n):
            j = object_model.get_articulation(f"leaf_{i}_slide")
            leaf_visuals = {v.name for v in object_model.get_part(f"leaf_{i}").visuals}
            ctx.check(
                f"leaf_{i} is supported by an outer guide shoe",
                "outer_guide_shoe" in leaf_visuals,
                details=str(sorted(leaf_visuals)),
            )
            # Every non-driver leaf mimics leaf_0 so none can float / lag when
            # the gate closes to the centre (spec: derived constraints).
            if i > 0:
                mimic = getattr(j, "mimic", None)
                ctx.check(
                    f"leaf_{i} mimics leaf_0 (converges together, no float)",
                    mimic is not None and getattr(mimic, "joint", None) == "leaf_0_slide",
                    details=str(mimic),
                )
        leaf0 = object_model.get_part("leaf_0")
        bore_r = _iris_radial_bore_r(r)
        a_closed = ctx.part_world_aabb(leaf0)
        q0 = ctx.part_world_position(leaf0)
        with ctx.pose({j0: r.leaf_travel * 0.9}):
            a_open = ctx.part_world_aabb(leaf0)
            q1 = ctx.part_world_position(leaf0)
        if a_closed is not None:
            # leaf_0 points +X: its inner tip reaches the aperture centre (x~0)
            # when closed, so the wedges seal to the circle centre.
            ctx.check(
                "closed radial wedge reaches the aperture centre",
                a_closed[0][0] <= 0.10,
                details=f"leaf0_xmin_closed={a_closed[0][0]:.3f}",
            )
        if a_open is not None:
            # Opened, leaf_0's inner tip has withdrawn past the bore rim, so the
            # aperture centre is a true through-hole (not a wall).
            ctx.check(
                "open radial wedge clears the aperture (true through-opening)",
                a_open[0][0] >= bore_r * 0.85,
                details=f"leaf0_xmin_open={a_open[0][0]:.3f} bore_r={bore_r:.3f}",
            )
        if q0 is not None and q1 is not None:
            ctx.check(
                "radial leaf_0 slides radially outward",
                math.hypot(q1[0] - q0[0], q1[2] - q0[2]) > r.leaf_travel * 0.6,
                details=f"disp={math.hypot(q1[0] - q0[0], q1[2] - q0[2]):.3f}",
            )

    # ---- Iris inscribed-circle feasibility (closed-pose). ----
    if r.is_iris:
        rim_lip = 0.04
        max_reach = 0.5 * min(r.opening_w, r.opening_h) - rim_lip
        ctx.check(
            "iris reach inscribes in the surround bore",
            r.leaf_outer_r <= max_reach + 1e-6,
            details=f"leaf_outer_r={r.leaf_outer_r:.4f} max_reach={max_reach:.4f}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with mech_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ScifiGateConfig",
    "ResolvedScifiGateConfig",
    "build_scifi_gate",
    "build_seeded_scifi_gate",
    "config_from_seed",
    "resolve_config",
    "run_scifi_gate_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
