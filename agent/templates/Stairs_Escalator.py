# SPDX-License-Identifier: Apache-2.0

"""Inclined escalator (moving staircase) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stairs_Escalator.md`` and the
``picture/Stairs/Escalator`` 5-star sample pool (2 parents + 8 slot/multiplicity
forks), all synced under ``data/records/``.

Topology (pattern = ``mixed``): a sloped steel ``frame``/truss running from a
lower landing up to an upper landing, carrying a band of N moving steps (the
``step_band``) on a PRISMATIC joint whose axis follows the incline direction
(the category-defining motion). Balustrades (glass / solid metal) flank the
sides, capped by welded rubber handrails (FIXED — a rigidly translating closed
loop would detach from the newel ends). The lower landing may have a hinged
maintenance pit cover (REVOLUTE about +Y) or a flush open landing.

Two independent spines (multiplicity axis D = ``unit_layout``):
  * single — a solid-wedge truss carrying one step band (parent A e7415cae).
  * twin   — two side trusses + a shared center divider, each side carrying its
    own step band (parent B 8388963a), mirrored about y=0.

Slots:
  * ``balustrade_style`` — glass vs solid metal panel (spine-gated candidates).
  * ``incline_geometry`` — standard_30 / standard_28_long / steep_35 /
    shallow_22; sets theta -> incline axis, truss profile, step pitch.
  * ``landing_pit`` — hinged_pit_cover (adds a REVOLUTE child part) vs
    open_flush_landing (no extra part / joint).
  * ``step_count`` (N in [4,60]) — the moving-step multiplicity axis. Weighted
    toward small/medium N (most seeds N<=20) because N steps x a per-step mesh
    is the dominant mesh-perf cost.

MESH-PERF: steps are intentionally COARSE low-poly Box primitives (a tread Box
+ a riser Box per step, plus continuous stringer/chain bars). The truss, glass
balustrade and swept handrails keep their mesh/lathe fidelity but are built
ONCE (FIXED), so only the cheap Box step band scales with N. Twin reuses every
fixed mesh through ``Origin(xyz=(0, y_off, 0))`` so its compile cost stays near
the single-unit cost.

3 HARD RULES honored:
  1. Non-moving decorations (skirts, newels, combs, divider, handrails) are
     parent visuals on ``frame``/``truss_frame``, not FIXED child parts.
  2. Every non-FIXED joint (step_band PRISMATIC, pit_cover REVOLUTE) has a
     MatingContract OR is grandfathered for captured/seated geometry; the
     element-scoped allow_overlap blocks mirror each source record.
  3. No primitive downgrade where sources use mesh/lathe (curved handrail =
     rotated box + sphere/extrude noses via cadquery mesh; glass balustrade =
     extruded cadquery slab). Coarse Box steps are explicitly allowed for perf.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
UnitLayout = Literal["single", "twin"]
InclineGeometry = Literal[
    "standard_30", "standard_28_long", "steep_35", "shallow_22"
]
# Spine-neutral balustrade roles; concrete material is the spine-gated identity.
BalustradeStyle = Literal["glass_panel", "metal_panel"]
LandingPit = Literal["hinged_pit_cover", "open_flush_landing"]
PaletteStyle = Literal[
    "brushed_steel_glass",
    "dark_metal",
    "warm_bronze",
    "transit_white",
    "stainless_smoked",
]

UNIT_LAYOUTS: tuple[UnitLayout, ...] = ("single", "twin")
INCLINE_GEOMETRIES: tuple[InclineGeometry, ...] = (
    "standard_30",
    "standard_28_long",
    "steep_35",
    "shallow_22",
)
BALUSTRADE_STYLES: tuple[BalustradeStyle, ...] = ("glass_panel", "metal_panel")
LANDING_PITS: tuple[LandingPit, ...] = ("hinged_pit_cover", "open_flush_landing")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_steel_glass",
    "dark_metal",
    "warm_bronze",
    "transit_white",
    "stainless_smoked",
)

# Step-count multiplicity domain (spec axis N). [4, 60], weighted toward small.
N_MIN = 4
N_MAX = 60

# unit_layout sampling weights (single ~55% / twin ~45%, spec axis D).
UNIT_WEIGHTS = {"single": 0.55, "twin": 0.45}

# ---------------------------------------------------------------------------
# Incline geometry table (spec Slot B). theta + nominal truss run.
#   theta_deg          : nominal incline angle
#   run_per_step_scale : not used directly; run is N-derived (see resolve)
#   step_rise          : nominal vertical rise per step
#   step_depth         : nominal horizontal tread depth per step
# step_rise = step_depth * tan(theta) is enforced in resolve_config so the
# treads stay on the incline line (shallow source does this explicitly).
# ---------------------------------------------------------------------------
INCLINE_TABLE: dict[InclineGeometry, dict[str, float]] = {
    # parent A: 30 deg, medium run, rise 0.205 / depth 0.355.
    "standard_30": {"theta_deg": 30.0, "step_depth": 0.355},
    # parent B (twin default): ~28 deg, long run.
    "standard_28_long": {"theta_deg": 28.0, "step_depth": 0.395},
    # space-saver: 35 deg, short run, taller steps.
    "steep_35": {"theta_deg": 35.0, "step_depth": 0.343},
    # transit-hall / airport: 22 deg, long run, deep treads.
    "shallow_22": {"theta_deg": 22.0, "step_depth": 0.400},
}

# ---------------------------------------------------------------------------
# Palette (>=5 colorways; every .visual material comes from here).
#   body   : truss / skirt / deck body
#   metal  : bright stainless skirt strips, newels, hardware
#   tread  : step tread / riser metal
#   glass  : balustrade glass (when glass_panel) — alpha < 1
#   panel  : balustrade solid metal (when metal_panel) — opaque
#   rubber : handrail
#   dark   : pit machinery box / divider
#   comb   : comb / floor / landing plate
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_steel_glass": {
        "body": (0.86, 0.88, 0.90, 1.0),
        "metal": (0.78, 0.80, 0.83, 1.0),
        "tread": (0.42, 0.45, 0.48, 1.0),
        "glass": (0.10, 0.11, 0.13, 0.55),
        "panel": (0.62, 0.64, 0.67, 1.0),
        "rubber": (0.07, 0.07, 0.08, 1.0),
        "dark": (0.12, 0.13, 0.15, 1.0),
        "comb": (0.74, 0.76, 0.78, 1.0),
    },
    "dark_metal": {
        "body": (0.30, 0.32, 0.35, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0),
        "tread": (0.40, 0.42, 0.45, 1.0),
        "glass": (0.20, 0.24, 0.28, 0.55),
        "panel": (0.26, 0.28, 0.31, 1.0),
        "rubber": (0.08, 0.08, 0.10, 1.0),
        "dark": (0.10, 0.11, 0.12, 1.0),
        "comb": (0.50, 0.50, 0.52, 1.0),
    },
    "warm_bronze": {
        "body": (0.46, 0.36, 0.24, 1.0),
        "metal": (0.72, 0.58, 0.38, 1.0),
        "tread": (0.34, 0.28, 0.20, 1.0),
        "glass": (0.32, 0.24, 0.12, 0.50),
        "panel": (0.58, 0.46, 0.30, 1.0),
        "rubber": (0.10, 0.08, 0.06, 1.0),
        "dark": (0.16, 0.12, 0.08, 1.0),
        "comb": (0.66, 0.56, 0.40, 1.0),
    },
    "transit_white": {
        "body": (0.93, 0.93, 0.94, 1.0),
        "metal": (0.82, 0.84, 0.86, 1.0),
        "tread": (0.46, 0.48, 0.50, 1.0),
        "glass": (0.55, 0.66, 0.74, 0.42),
        "panel": (0.88, 0.89, 0.90, 1.0),
        "rubber": (0.12, 0.12, 0.14, 1.0),
        "dark": (0.18, 0.19, 0.21, 1.0),
        "comb": (0.80, 0.82, 0.84, 1.0),
    },
    "stainless_smoked": {
        "body": (0.74, 0.76, 0.79, 1.0),
        "metal": (0.88, 0.90, 0.92, 1.0),
        "tread": (0.40, 0.43, 0.46, 1.0),
        "glass": (0.22, 0.22, 0.25, 0.58),
        "panel": (0.70, 0.72, 0.75, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
        "dark": (0.14, 0.15, 0.16, 1.0),
        "comb": (0.78, 0.80, 0.82, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Configs
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EscalatorConfig:
    unit_layout: UnitLayout | None = None
    incline_geometry: InclineGeometry | None = None
    balustrade_style: BalustradeStyle | None = None
    landing_pit: LandingPit | None = None
    step_count: int | None = None
    palette_style: PaletteStyle = "brushed_steel_glass"
    width_scale: float = 1.0
    balustrade_height_scale: float = 1.0
    incline_angle_perturb_deg: float = 0.0  # +-1.5 deg about the nominal theta
    unit_gap_scale: float = 1.0  # twin only
    name: str = "escalator"


@dataclass(frozen=True)
class ResolvedEscalatorConfig:
    unit_layout: UnitLayout
    incline_geometry: InclineGeometry
    balustrade_style: BalustradeStyle
    landing_pit: LandingPit
    step_count: int
    palette_style: PaletteStyle
    # Derived geometry (meters / radians).
    theta: float
    cos_t: float
    sin_t: float
    step_depth: float
    step_rise: float
    step_pitch: float  # = hypot(step_depth, step_rise) = PRISMATIC travel
    truss_run: float  # horizontal run of the incline
    truss_rise: float  # vertical rise of the incline
    width: float  # overall machine width per unit
    tread_width: float  # usable tread width
    landing_len: float
    landing_top_z: float
    skirt_h: float
    balus_h: float
    incl_x0: float  # x where incline begins (end of lower landing)
    incl_z0: float  # z of tread line at the incline bottom
    unit_gap: float  # twin: clear gap between units
    unit_offset: float  # twin: |y| centerline offset
    name: str

    @property
    def incl_x1(self) -> float:
        return self.incl_x0 + self.truss_run

    @property
    def incl_z1(self) -> float:
        return self.incl_z0 + self.truss_rise

    def incline_dir(self) -> tuple[float, float, float]:
        return (self.cos_t, 0.0, self.sin_t)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Step-count weighted sampling (spec axis N: most seeds small/medium).
#   ~70% N in [6,16] (incl. nominal 11/16), ~22% [17,30], ~8% [31,60];
#   small N<6 kept rare for boundary coverage. Large N is mesh-perf heavy, so
#   the sampler downweights it; large N stays safe by construction.
# ---------------------------------------------------------------------------
def _sample_step_count(rng: random.Random) -> int:
    band = rng.choices(
        ("tiny", "small", "mid", "large"),
        weights=(0.06, 0.66, 0.22, 0.06),
        k=1,
    )[0]
    if band == "tiny":
        return rng.randint(4, 5)
    if band == "small":
        return rng.randint(6, 16)
    if band == "mid":
        return rng.randint(17, 30)
    return rng.randint(31, 60)


def config_from_seed(seed: int) -> EscalatorConfig:
    rng = random.Random(seed)
    unit_layout = rng.choices(
        list(UNIT_LAYOUTS),
        weights=[UNIT_WEIGHTS[u] for u in UNIT_LAYOUTS],
        k=1,
    )[0]
    return EscalatorConfig(
        unit_layout=unit_layout,
        incline_geometry=rng.choice(INCLINE_GEOMETRIES),
        balustrade_style=rng.choice(BALUSTRADE_STYLES),
        landing_pit=rng.choice(LANDING_PITS),
        step_count=_sample_step_count(rng),
        palette_style=rng.choice(PALETTE_STYLES),
        width_scale=round(rng.uniform(0.90, 1.15), 4),
        balustrade_height_scale=round(rng.uniform(0.90, 1.10), 4),
        incline_angle_perturb_deg=round(rng.uniform(-1.5, 1.5), 4),
        unit_gap_scale=round(rng.uniform(0.80, 1.40), 4),
        name=f"seeded_escalator_{seed}",
    )


def resolve_config(config: EscalatorConfig | None = None) -> ResolvedEscalatorConfig:
    cfg = config or EscalatorConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    unit_layout = _pick(cfg.unit_layout, UNIT_LAYOUTS)
    incline_geometry = _pick(cfg.incline_geometry, INCLINE_GEOMETRIES)
    balustrade_style = _pick(cfg.balustrade_style, BALUSTRADE_STYLES)
    landing_pit = _pick(cfg.landing_pit, LANDING_PITS)

    step_count = int(cfg.step_count) if cfg.step_count is not None else 11
    step_count = int(_clamp(step_count, N_MIN, N_MAX))

    # --- Continuous scales (clamped). ---
    width_scale = _clamp(cfg.width_scale, 0.90, 1.15)
    balus_scale = _clamp(cfg.balustrade_height_scale, 0.90, 1.10)
    perturb = _clamp(cfg.incline_angle_perturb_deg, -1.5, 1.5)
    gap_scale = _clamp(cfg.unit_gap_scale, 0.80, 1.40)

    # --- Incline geometry: theta + step pitch (equation). ---
    tbl = INCLINE_TABLE[incline_geometry]
    theta = math.radians(tbl["theta_deg"] + perturb)
    theta = _clamp(theta, math.radians(18.0), math.radians(40.0))
    cos_t = math.cos(theta)
    sin_t = math.sin(theta)
    step_depth = tbl["step_depth"]
    # equation: keep treads on the incline line (shallow source L57-58).
    step_rise = step_depth * math.tan(theta)
    step_pitch = math.hypot(step_depth, step_rise)

    # --- Truss run/rise derived from N (steps7/steps22/twinsteps14 pattern). ---
    # run = lead-in margin + (N-1)*depth + one tread depth + end margin.
    lead_in = 0.10
    end_margin = 0.40
    truss_run = lead_in + (step_count - 1) * step_depth + step_depth + end_margin
    truss_rise = truss_run * math.tan(theta)

    # --- Lateral dims (parent A baseline, width-scaled). ---
    width = 1.20 * width_scale
    tread_width = 0.78 * width_scale
    landing_len = 1.05
    landing_top_z = 0.16
    skirt_h = 0.30
    balus_h = 0.95 * balus_scale

    incl_x0 = landing_len
    incl_z0 = landing_top_z

    # --- Twin layout (unit gap + offset). ---
    unit_gap = _clamp(0.16 * gap_scale, 0.10, 0.40)
    unit_offset = (width + unit_gap) / 2.0
    # inequality (spec): twin band y intervals must be disjoint. Each band y
    # half-width is tread_width/2; offsets are +-unit_offset. Disjoint requires
    # unit_offset - tread_width/2 > unit_offset - tread_width/2 ... i.e. the two
    # bands sit at +-unit_offset and each is +-tread_width/2 wide -> gap between
    # inner edges = 2*unit_offset - tread_width. Keep it > 0.05.
    if unit_layout == "twin":
        inner_gap = 2.0 * unit_offset - tread_width
        if inner_gap <= 0.05:
            unit_offset = (tread_width + 0.06) / 2.0 + 0.001

    return ResolvedEscalatorConfig(
        unit_layout=unit_layout,
        incline_geometry=incline_geometry,
        balustrade_style=balustrade_style,
        landing_pit=landing_pit,
        step_count=step_count,
        palette_style=palette_style,
        theta=theta,
        cos_t=cos_t,
        sin_t=sin_t,
        step_depth=step_depth,
        step_rise=step_rise,
        step_pitch=step_pitch,
        truss_run=truss_run,
        truss_rise=truss_rise,
        width=width,
        tread_width=tread_width,
        landing_len=landing_len,
        landing_top_z=landing_top_z,
        skirt_h=skirt_h,
        balus_h=balus_h,
        incl_x0=incl_x0,
        incl_z0=incl_z0,
        unit_gap=unit_gap,
        unit_offset=unit_offset,
        name=cfg.name or "escalator",
    )


def with_overrides(config: EscalatorConfig, **kwargs: object) -> EscalatorConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def _n_bucket(n: int) -> str:
    if n < 6:
        return "tiny"
    if n <= 16:
        return "small"
    if n <= 30:
        return "mid"
    if n <= 45:
        return "large"
    return "xlarge"


def slot_choices_for_config(
    config: EscalatorConfig | ResolvedEscalatorConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedEscalatorConfig) else resolve_config(config)
    # Spine-qualified balustrade module name so single vs twin glass/metal read
    # as distinct topology candidates (spec Slot A: 4 candidates, 2 per spine).
    bal = f"{r.unit_layout}_{r.balustrade_style}"
    pit = r.landing_pit if r.landing_pit == "hinged_pit_cover" else "open_flush_landing"
    pit = f"{r.unit_layout}_{pit}"
    return (
        ("unit_layout", r.unit_layout),
        ("incline_geometry", r.incline_geometry),
        ("balustrade_style", bal),
        ("landing_pit", pit),
        ("step_count", f"n_{_n_bucket(r.step_count)}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers — FIXED structure built ONCE per "unit prototype" so twin
# reuses meshes via Origin offsets (mesh-perf). All authored about y=0.
# ---------------------------------------------------------------------------
def _truss_wedge_mesh(r: ResolvedEscalatorConfig):
    """Solid-wedge side truss profile (parent A L94-136), one connected slab
    spanning the full width. Extruded XZ polygon thickened in Y. Built once."""
    half_w = r.width / 2.0
    band_x_lo = r.incl_x0 + 0.10
    band_x_hi = band_x_lo + (r.step_count - 1) * r.step_depth + r.step_depth
    band_z_lo = r.incl_z0
    band_slope = r.step_rise / r.step_depth
    margin = r.step_rise + 0.07
    top_lo_z = band_z_lo - margin
    top_hi_z = band_z_lo + (band_x_hi - band_x_lo) * band_slope - margin
    truss_bottom_z = r.incl_z0 - 0.55
    side_profile = [
        (r.incl_x0 - 0.30, truss_bottom_z),
        (r.incl_x1 + 0.30, truss_bottom_z + r.truss_rise),
        (r.incl_x1 + 0.30, r.incl_z1 - 0.05),
        (band_x_hi, top_hi_z),
        (band_x_lo, top_lo_z),
        (r.incl_x0 - 0.30, r.incl_z0 - 0.05),
    ]
    truss = (
        cq.Workplane("XZ")
        .polyline(side_profile)
        .close()
        .extrude(r.width)
        .translate((0.0, half_w, 0.0))
    )
    return mesh_from_cadquery(truss, "truss_body")


def _lower_landing_mesh(r: ResolvedEscalatorConfig, *, with_pit: bool):
    """Lower landing slab; cut an access pit when the hinged cover is present."""
    lower = cq.Workplane("XY").box(
        r.landing_len, r.width, r.landing_top_z, centered=(False, True, False)
    )
    if with_pit:
        pit_len, pit_x0 = _PIT_LEN, _PIT_X0
        pit_w = r.width - 0.30
        pit = (
            cq.Workplane("XY")
            .transformed(offset=(pit_x0 + pit_len / 2.0, 0.0, r.landing_top_z - 0.02))
            .box(pit_len, pit_w, 0.10, centered=(True, True, False))
        )
        lower = lower.cut(pit)
    return mesh_from_cadquery(lower, "lower_landing")


def _pit_box_mesh(r: ResolvedEscalatorConfig):
    """Dark machinery box in the pit (parent A L159-184)."""
    pit_len, pit_x0 = _PIT_LEN, _PIT_X0
    pit_w = r.width - 0.30
    box_wall = 0.03
    box_depth = 0.34
    box_outer = (
        cq.Workplane("XY")
        .transformed(offset=(pit_x0 + pit_len / 2.0, 0.0, r.landing_top_z - box_depth))
        .box(pit_len - 0.02, pit_w - 0.02, box_depth, centered=(True, True, False))
    )
    box_inner = (
        cq.Workplane("XY")
        .transformed(
            offset=(pit_x0 + pit_len / 2.0, 0.0, r.landing_top_z - box_depth + box_wall)
        )
        .box(
            pit_len - 0.02 - 2 * box_wall,
            pit_w - 0.02 - 2 * box_wall,
            box_depth,
            centered=(True, True, False),
        )
    )
    return mesh_from_cadquery(box_outer.cut(box_inner), "pit_box")


def _upper_landing_mesh(r: ResolvedEscalatorConfig):
    upper = (
        cq.Workplane("XY")
        .transformed(offset=(r.incl_x1, 0.0, r.incl_z1 - r.landing_top_z))
        .box(r.landing_len, r.width, r.landing_top_z, centered=(False, True, False))
    )
    return mesh_from_cadquery(upper, "upper_landing")


def _comb_mesh(r: ResolvedEscalatorConfig):
    comb = (
        cq.Workplane("XY")
        .transformed(offset=(r.incl_x0 + 0.06, 0.0, r.incl_z0))
        .box(0.16, r.tread_width, 0.02, centered=(True, True, False))
    )
    return mesh_from_cadquery(comb, "lower_comb")


def _skirt_strip_mesh(r: ResolvedEscalatorConfig, *, sign: float, side: str):
    skirt_strip_t = 0.025
    y = sign * (r.tread_width / 2.0 + skirt_strip_t / 2.0)
    strip = (
        cq.Workplane("XZ")
        .polyline(
            [
                (r.incl_x0, r.incl_z0),
                (r.incl_x1, r.incl_z1),
                (r.incl_x1, r.incl_z1 + r.skirt_h),
                (r.incl_x0, r.incl_z0 + r.skirt_h),
            ]
        )
        .close()
        .extrude(skirt_strip_t)
        .translate((0.0, y + skirt_strip_t / 2.0, 0.0))
    )
    return mesh_from_cadquery(strip, f"skirt_{side}")


def _balustrade_deck_mesh(r: ResolvedEscalatorConfig, *, sign: float, side: str):
    """Deck rail bridging skirt->newel that carries the balustrade panel."""
    half_w = r.width / 2.0
    skirt_inner_y = r.tread_width / 2.0 + 0.025
    newel_outer_y = half_w
    deck_span = max(0.04, newel_outer_y - skirt_inner_y)
    deck = (
        cq.Workplane("XZ")
        .polyline(
            [
                (r.incl_x0 - 0.10, r.incl_z0 + r.skirt_h - 0.02),
                (r.incl_x1 + 0.10, r.incl_z1 + r.skirt_h - 0.02),
                (r.incl_x1 + 0.10, r.incl_z1 + r.skirt_h + 0.05),
                (r.incl_x0 - 0.10, r.incl_z0 + r.skirt_h + 0.05),
            ]
        )
        .close()
        .extrude(deck_span)
    )
    if sign > 0:
        deck = deck.translate((0.0, newel_outer_y, 0.0))
    else:
        deck = deck.translate((0.0, -skirt_inner_y, 0.0))
    return mesh_from_cadquery(deck, f"balustrade_deck_{side}")


def _balustrade_panel_mesh(r: ResolvedEscalatorConfig, *, sign: float, side: str):
    """Balustrade panel running along the incline + elliptical nose end-caps.

    Glass (glass_panel) and solid metal (metal_panel) share this extruded-slab
    build path (spec: single-spine glass uses a thinner translucent slab, metal
    a thicker opaque slab); the material role is what carries the identity. The
    cadquery extrude + nose union preserves the source's curved-nose mesh (Rule
    3: no downgrade to a bare box)."""
    glass_inner_y = r.tread_width / 2.0 + 0.05
    panel_t = 0.022 if r.balustrade_style == "glass_panel" else 0.030
    y_base = sign * (glass_inner_y + panel_t / 2.0)
    panel = (
        cq.Workplane("XZ")
        .polyline(
            [
                (r.incl_x0 - 0.10, r.incl_z0 + r.skirt_h),
                (r.incl_x1 + 0.10, r.incl_z1 + r.skirt_h),
                (r.incl_x1 + 0.10, r.incl_z1 + r.balus_h),
                (r.incl_x0 - 0.10, r.incl_z0 + r.balus_h),
            ]
        )
        .close()
        .extrude(panel_t)
        .translate((0.0, y_base + (sign * panel_t / 2.0), 0.0))
    )
    nose_ry = (r.balus_h - r.skirt_h) / 2.0
    end_low = (
        cq.Workplane("XZ")
        .center(r.incl_x0 - 0.10, r.incl_z0 + (r.skirt_h + r.balus_h) / 2.0)
        .ellipse(0.22, nose_ry)
        .extrude(panel_t)
        .translate((0.0, y_base + (sign * panel_t / 2.0), 0.0))
    )
    end_high = (
        cq.Workplane("XZ")
        .center(r.incl_x1 + 0.10, r.incl_z1 + (r.skirt_h + r.balus_h) / 2.0)
        .ellipse(0.22, nose_ry)
        .extrude(panel_t)
        .translate((0.0, y_base + (sign * panel_t / 2.0), 0.0))
    )
    panel = panel.union(end_low).union(end_high)
    name = f"glass_{side}" if r.balustrade_style == "glass_panel" else f"panel_{side}"
    return mesh_from_cadquery(panel, name), name


def _newel_mesh(r: ResolvedEscalatorConfig, *, sign: float, side: str):
    half_w = r.width / 2.0
    y_out = sign * (half_w - 0.03)
    shell = (
        cq.Workplane("XZ")
        .polyline(
            [
                (r.incl_x0 - 0.20, r.incl_z0),
                (r.incl_x1 + 0.20, r.incl_z1),
                (r.incl_x1 + 0.20, r.incl_z1 + r.skirt_h + 0.02),
                (r.incl_x0 - 0.20, r.incl_z0 + r.skirt_h + 0.02),
            ]
        )
        .close()
        .extrude(0.06)
        .translate((0.0, y_out + (sign * 0.03), 0.0))
    )
    return mesh_from_cadquery(shell, f"newel_{side}")


def _handrail_mesh(r: ResolvedEscalatorConfig, *, sign: float, side: str):
    """Curved rubber handrail capping the balustrade top edge (parent A
    L403-447): a rounded bar rotated to the incline + spherical return noses.
    cadquery mesh — preserves the source's filleted/curved profile (Rule 3)."""
    panel_t = 0.022 if r.balustrade_style == "glass_panel" else 0.030
    y = sign * (r.tread_width / 2.0 + 0.05 + panel_t / 2.0)
    handrail_w = 0.075
    handrail_h = 0.055

    def z_top(x: float) -> float:
        return r.incl_z0 + (x - r.incl_x0) * math.tan(r.theta) + r.balus_h

    x_lo = r.incl_x0 - 0.18
    x_hi = r.incl_x1 + 0.18
    cx = (x_lo + x_hi) / 2.0
    cz = (z_top(x_lo) + z_top(x_hi)) / 2.0
    length = math.hypot(x_hi - x_lo, z_top(x_hi) - z_top(x_lo))
    bar = (
        cq.Workplane("XZ")
        .center(0.0, 0.0)
        .box(length, handrail_h, handrail_w, centered=(True, True, True))
        .edges("|X")
        .fillet(handrail_h * 0.35)
    )
    bar = bar.rotate((0, 0, 0), (0, 1, 0), -math.degrees(r.theta))
    bar = bar.translate((cx, y, cz))
    nose_lo = (
        cq.Workplane("XY")
        .transformed(offset=(x_lo, y, z_top(x_lo)))
        .sphere(handrail_h / 2.0)
    )
    nose_hi = (
        cq.Workplane("XY")
        .transformed(offset=(x_hi, y, z_top(x_hi)))
        .sphere(handrail_h / 2.0)
    )
    rail = bar.union(nose_lo).union(nose_hi)
    return mesh_from_cadquery(rail, f"{side}_rail"), f"{side}_rail"


# Pit geometry constants (shared by mesh + joint).
_PIT_LEN = 0.62
_PIT_X0 = 0.18


# ---------------------------------------------------------------------------
# Step band (COARSE low-poly Box steps — mesh-perf). One part per band.
#   N tread Boxes + N riser Boxes + 2 continuous stringer Boxes tying the band
#   into one connected solid. Authored about y=0; twin reuses via the part's
#   visual origins (separate part per unit so each has its own PRISMATIC joint).
# ---------------------------------------------------------------------------
def _stringer_wedge_mesh(r: ResolvedEscalatorConfig, *, sign: float):
    """One continuous side stringer following the riser-bottom incline line,
    tying every tread/riser into one connected band (parent A L355-371). Built
    as a cadquery extruded polyline wedge (the source primitive) — a single
    cheap mesh per side that does NOT scale with N (only the Box treads do)."""
    x_lo = r.incl_x0 + 0.10
    x_hi = x_lo + (r.step_count - 1) * r.step_depth + r.step_depth
    slope = r.step_rise / r.step_depth
    z_bot_lo = r.incl_z0  # bottom edge passes through the riser bottoms
    band_thk = 0.30  # tall enough to intersect every riser/tread above it
    string_t = 0.04
    y = sign * (r.tread_width / 2.0 - 0.02)
    stringer = (
        cq.Workplane("XZ")
        .polyline(
            [
                (x_lo, z_bot_lo),
                (x_hi, z_bot_lo + (x_hi - x_lo) * slope),
                (x_hi, z_bot_lo + (x_hi - x_lo) * slope + band_thk),
                (x_lo, z_bot_lo + band_thk),
            ]
        )
        .close()
        .extrude(string_t)
        .translate((0.0, y - sign * string_t / 2.0, 0.0))
    )
    tag = "p" if sign > 0 else "n"
    return mesh_from_cadquery(stringer, f"stringer_{tag}"), f"stringer_{tag}"


def _emit_step_band(
    band,
    r: ResolvedEscalatorConfig,
    mat_tread,
    *,
    local_x: float,
    local_z: float,
) -> None:
    """Emit the moving step band into its OWN link frame, which is placed at the
    PRISMATIC joint origin (local_x, *, local_z) in world. The band geometry is
    authored in world coords (matching the fixed frame), so each visual origin
    is shifted by (-local_x, 0, -local_z) to land at the right world place while
    the child link frame coincides with the joint origin (so the articulation
    origin sits on real band geometry — baseline flat 0.015 tol)."""
    tread_t = 0.03
    riser_t = 0.025

    # Continuous side stringers (one cheap cadquery wedge mesh per side) tie the
    # treads/risers into one connected band; their bottom edge is the band's
    # lowest line and the truss top stays a clear margin below it.
    for sgn in (1.0, -1.0):
        smesh, sname = _stringer_wedge_mesh(r, sign=sgn)
        band.visual(
            smesh,
            origin=Origin(xyz=(-local_x, 0.0, -local_z)),
            material=mat_tread,
            name=sname, material_class_id="metal.aluminum_bare",
        )

    # N coarse steps: a tread Box + a riser Box each (box-like, low-poly).
    for i in range(r.step_count):
        x = r.incl_x0 + 0.10 + i * r.step_depth
        z = r.incl_z0 + i * r.step_rise
        band.visual(
            Box((r.step_depth, r.tread_width, tread_t)),
            origin=Origin(
                xyz=(
                    x + r.step_depth / 2.0 - local_x,
                    0.0,
                    z + r.step_rise - tread_t / 2.0 - local_z,
                )
            ),
            material=mat_tread,
            name=f"tread_{i}", material_class_id="metal.aluminum_bare",
        )
        band.visual(
            Box((riser_t, r.tread_width, r.step_rise)),
            origin=Origin(
                xyz=(
                    x + r.step_depth - riser_t / 2.0 - local_x,
                    0.0,
                    z + r.step_rise / 2.0 - local_z,
                )
            ),
            material=mat_tread,
            name=f"riser_{i}", material_class_id="metal.aluminum_bare",
        )


# ---------------------------------------------------------------------------
# Pit cover (REVOLUTE about +Y) — single & twin share this Box-based helper.
# ---------------------------------------------------------------------------
def _emit_pit_cover(
    cover, r: ResolvedEscalatorConfig, mats, *, y_off: float, suffix: str
) -> None:
    pit_len = _PIT_LEN
    pit_w = r.width - 0.30
    plate_t = 0.03
    # Plate extends along local -X from the hinge (local origin) toward the pit,
    # flat at z=0 so +Y rotation lifts the free edge. Authored in pivot frame;
    # the part's articulation origin is at the hinge world point.
    cover.visual(
        Box((pit_len, pit_w, plate_t)),
        origin=Origin(xyz=(-pit_len / 2.0, y_off, plate_t / 2.0)),
        material=mats["comb"],
        name=f"pit_cover_plate_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.brass_aged"),
    )
    # Two hinge knuckles at the hinge line (local x=0) — Boxes that touch the
    # plate so the part is one connected solid (the knuckle straddles the plate
    # edge, no floating island).
    for ky, tag in ((-pit_w / 2.0 + 0.06, "n"), (pit_w / 2.0 - 0.06, "p")):
        cover.visual(
            Box((0.05, 0.05, 0.05)),
            origin=Origin(xyz=(-0.02, y_off + ky, plate_t / 2.0)),
            material=mats["metal"],
            name=f"hinge_knuckle_{tag}_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.brass_polished"),
        )


# ---------------------------------------------------------------------------
# Twin-only fixed extras: center divider + cross bracing (fuse the two trusses).
# ---------------------------------------------------------------------------
def _center_divider_mesh(r: ResolvedEscalatorConfig):
    """Center divider slab between the two units, wide enough to overlap both
    inner truss faces so the twin frame reads as one connected body."""
    half_w = r.width / 2.0
    band_x_lo = r.incl_x0 + 0.10
    truss_bottom_z = r.incl_z0 - 0.55
    side_profile = [
        (r.incl_x0 - 0.30, truss_bottom_z),
        (r.incl_x1 + 0.30, truss_bottom_z + r.truss_rise),
        (r.incl_x1 + 0.30, r.incl_z1 - 0.05),
        (band_x_lo, r.incl_z0 - 0.05),
        (r.incl_x0 - 0.30, r.incl_z0 - 0.05),
    ]
    half_thk = r.unit_offset - half_w + 0.04  # span the gap + bite both faces
    half_thk = max(half_thk, r.unit_gap / 2.0 + 0.04)
    divider = (
        cq.Workplane("XZ")
        .polyline(side_profile)
        .close()
        .extrude(half_thk, both=True)
    )
    return mesh_from_cadquery(divider, "center_divider")


def _cross_brace_mesh(r: ResolvedEscalatorConfig):
    """Transverse bars tying the two side trusses (across both units) into one
    fixed body, plus a longitudinal spine bar tying every transverse bar into
    one connected solid (so the cross_brace visual is a single mesh, not
    disconnected islands). Bars hang below the step line so they never clip the
    steps."""
    asm = None
    n = 5
    deck = 0.47
    bar_h = 0.07
    inner = r.unit_offset + r.width / 2.0 - 0.03  # reach into both outer slabs
    for i in range(n):
        t = i / (n - 1)
        x = r.incl_x0 + 0.20 + (r.truss_run - 0.30) * t
        z = r.incl_z0 + ((x - r.incl_x0) / r.truss_run) * r.truss_rise - deck
        bar = (
            cq.Workplane("XY")
            .box(0.08, 2 * inner + 0.10, bar_h)
            .translate((x, 0.0, z))
        )
        asm = bar if asm is None else asm.union(bar)
    # Longitudinal spine along the incline at y=0 connecting every bar.
    x_lo = r.incl_x0 + 0.20
    x_hi = r.incl_x0 + 0.20 + (r.truss_run - 0.30)
    spine_len = math.hypot(x_hi - x_lo, (x_hi - x_lo) * (r.truss_rise / r.truss_run))
    cx = (x_lo + x_hi) / 2.0
    cz = r.incl_z0 + ((cx - r.incl_x0) / r.truss_run) * r.truss_rise - deck
    spine = (
        cq.Workplane("XY")
        .box(spine_len, 0.10, bar_h)
        .rotate((0, 0, 0), (0, 1, 0), -math.degrees(r.theta))
        .translate((cx, 0.0, cz))
    )
    asm = asm.union(spine)
    return mesh_from_cadquery(asm, "cross_brace")


# ---------------------------------------------------------------------------
# Frame builders (FIXED root). Single = one solid-wedge unit; twin = two units
# reusing the same fixed meshes via Origin offsets + divider + cross bracing.
# ---------------------------------------------------------------------------
def _emit_fixed_unit_visuals(
    frame, r: ResolvedEscalatorConfig, mats, *, y_off: float, suffix: str
) -> None:
    """Emit one unit's fixed structure (truss/landings/skirts/balustrade/
    handrails) as parent visuals on the frame, offset by y_off (twin reuse)."""
    has_pit = r.landing_pit == "hinged_pit_cover"
    bal_mat = mats["glass"] if r.balustrade_style == "glass_panel" else mats["panel"]

    frame.visual(
        _truss_wedge_mesh(r),
        origin=Origin(xyz=(0.0, y_off, 0.0)),
        material=mats["body"],
        name=f"truss_body_{suffix}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.bronze_cast"),
    )
    frame.visual(
        _lower_landing_mesh(r, with_pit=has_pit),
        origin=Origin(xyz=(0.0, y_off, 0.0)),
        material=mats["comb"],
        name=f"lower_landing_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.brass_aged"),
    )
    if has_pit:
        frame.visual(
            _pit_box_mesh(r),
            origin=Origin(xyz=(0.0, y_off, 0.0)),
            material=mats["dark"],
            name=f"pit_box_{suffix}", material_class_id="metal.blackened_gunmetal",
        )
    frame.visual(
        _upper_landing_mesh(r),
        origin=Origin(xyz=(0.0, y_off, 0.0)),
        material=mats["comb"],
        name=f"upper_landing_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.brass_aged"),
    )
    frame.visual(
        _comb_mesh(r),
        origin=Origin(xyz=(0.0, y_off, 0.0)),
        material=mats["metal"],
        name=f"lower_comb_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.brass_polished"),
    )
    for sgn, side in ((1.0, "left"), (-1.0, "right")):
        frame.visual(
            _skirt_strip_mesh(r, sign=sgn, side=side),
            origin=Origin(xyz=(0.0, y_off, 0.0)),
            material=mats["metal"],
            name=f"skirt_{side}_{suffix}", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.brass_polished"),
        )
        frame.visual(
            _balustrade_deck_mesh(r, sign=sgn, side=side),
            origin=Origin(xyz=(0.0, y_off, 0.0)),
            material=mats["body"],
            name=f"balustrade_deck_{side}_{suffix}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.bronze_cast"),
        )
        panel_mesh, panel_name = _balustrade_panel_mesh(r, sign=sgn, side=side)
        frame.visual(
            panel_mesh,
            origin=Origin(xyz=(0.0, y_off, 0.0)),
            material=bal_mat,
            name=f"{panel_name}_{suffix}", material_class_id=("glass.smoked_tinted" if r.balustrade_style == "glass_panel" else "metal.paint_coated"),
        )
        frame.visual(
            _newel_mesh(r, sign=sgn, side=side),
            origin=Origin(xyz=(0.0, y_off, 0.0)),
            material=mats["body"],
            name=f"newel_{side}_{suffix}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.bronze_cast"),
        )
        rail_mesh, rail_name = _handrail_mesh(r, sign=sgn, side=side)
        frame.visual(
            rail_mesh,
            origin=Origin(xyz=(0.0, y_off, 0.0)),
            material=mats["rubber"],
            name=f"{rail_name}_{suffix}", material_class_id="rubber.smooth_plain",
        )


def _unit_specs(r: ResolvedEscalatorConfig) -> tuple[tuple[str, float], ...]:
    if r.unit_layout == "twin":
        return (("a", r.unit_offset), ("b", -r.unit_offset))
    return (("a", 0.0),)


def _balustrade_panel_basename(r: ResolvedEscalatorConfig, side: str) -> str:
    return f"glass_{side}" if r.balustrade_style == "glass_panel" else f"panel_{side}"


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_escalator(
    config: EscalatorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"escalator_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    units = _unit_specs(r)

    # --- FIXED root frame: all static structure as parent visuals (Rule 1). ---
    frame = model.part("frame")
    for suffix, y_off in units:
        _emit_fixed_unit_visuals(frame, r, mats, y_off=y_off, suffix=suffix)
    if r.unit_layout == "twin":
        frame.visual(
            _center_divider_mesh(r),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["dark"],
            name="center_divider", material_class_id="metal.blackened_gunmetal",
        )
        frame.visual(
            _cross_brace_mesh(r),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["body"],
            name="cross_brace", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel_glass", "dark_metal", "transit_white", "stainless_smoked"} else "metal.bronze_cast"),
        )
    frame.inertial = Inertial.from_geometry(
        Box((r.truss_run + 2.0 * r.landing_len, r.unit_offset * 2.0 + r.width, r.truss_rise)),
        mass=400.0,
        origin=Origin(xyz=(r.incl_x0 + r.truss_run / 2.0, 0.0, r.incl_z0 + r.truss_rise / 2.0)),
    )

    incl = r.incline_dir()

    # PRISMATIC translation is axis-only, so the joint origin may sit anywhere
    # along the slide; place it on the bottom step (comb boarding point) so it
    # lands on real frame comb + step-band geometry (baseline flat 0.015 tol).
    boarding_x = r.incl_x0 + 0.10 + r.step_depth / 2.0
    boarding_z = r.incl_z0 + r.step_rise

    # --- Moving step band(s): PRISMATIC up the incline (category motion). ---
    # The band link frame is placed at the joint origin (boarding point) so the
    # articulation origin sits on real band geometry; band visuals are authored
    # relative to that frame (local_x/local_z) yet land in world place.
    for suffix, y_off in units:
        band = model.part(f"step_band_{suffix}")
        _emit_step_band(band, r, mats["tread"], local_x=boarding_x, local_z=boarding_z)
        band.inertial = Inertial.from_geometry(
            Box((r.truss_run, r.tread_width, r.truss_rise)),
            mass=80.0,
            origin=Origin(
                xyz=(
                    r.incl_x0 + r.truss_run / 2.0 - boarding_x,
                    0.0,
                    r.incl_z0 + r.truss_rise / 2.0 - boarding_z,
                )
            ),
        )
        model.articulation(
            f"step_travel_{suffix}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=band,
            origin=Origin(xyz=(boarding_x, y_off, boarding_z)),
            axis=incl,
            motion_limits=MotionLimits(
                effort=8000.0, velocity=0.65, lower=0.0, upper=r.step_pitch
            ),
        )

    # --- Handrails: NOT separate parts. They are welded parent visuals on the
    #     frame (Rule 1 — a rigidly translating closed loop detaches from the
    #     newel ends, so the rail carries no joint). Already emitted above.

    # --- Optional hinged pit cover(s): REVOLUTE about +Y. ---
    if r.landing_pit == "hinged_pit_cover":
        hinge_x = _PIT_X0 + _PIT_LEN  # up-slope edge of the pit
        for suffix, y_off in units:
            cover = model.part(f"pit_cover_{suffix}")
            _emit_pit_cover(cover, r, mats, y_off=0.0, suffix=suffix)
            cover.inertial = Inertial.from_geometry(
                Box((_PIT_LEN, r.width - 0.30, 0.03)),
                mass=8.0,
                origin=Origin(xyz=(-_PIT_LEN / 2.0, 0.0, 0.015)),
            )
            model.articulation(
                f"pit_hinge_{suffix}",
                ArticulationType.REVOLUTE,
                parent=frame,
                child=cover,
                origin=Origin(xyz=(hinge_x, y_off, r.landing_top_z)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(
                    effort=120.0, velocity=1.5, lower=0.0, upper=1.3
                ),
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_escalator(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_escalator(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_escalator_tests(
    object_model: ArticulatedObject,
    config: EscalatorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    units = _unit_specs(r)

    # ---- Seated / captured allowances (element-scoped, mirror the sources). --
    for suffix, _ in units:
        band = object_model.get_part(f"step_band_{suffix}")
        # Comb plate teeth intentionally mesh with the bottom step treads at the
        # boarding point (parent A L592-599).
        ctx.allow_overlap(
            frame,
            band,
            elem_a=f"lower_comb_{suffix}",
            elem_b="tread_0",
            reason="Comb plate teeth mesh with the bottom step tread at the boarding point.",
        )
        ctx.allow_overlap(
            frame,
            band,
            elem_a=f"lower_comb_{suffix}",
            elem_b="stringer_n",
            reason="Comb plate sits over the step-band stringer at the landing edge.",
        )
        ctx.allow_overlap(
            frame,
            band,
            elem_a=f"lower_comb_{suffix}",
            elem_b="stringer_p",
            reason="Comb plate sits over the step-band stringer at the landing edge.",
        )

    if r.landing_pit == "hinged_pit_cover":
        for suffix, _ in units:
            cover = object_model.get_part(f"pit_cover_{suffix}")
            ctx.allow_overlap(
                cover,
                frame,
                reason="Closed pit cover seats flush over the access pit on the lower landing.",
            )

    # ---- Baseline structural checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    part_names = {p.name for p in object_model.parts}
    ctx.check("frame part present", "frame" in part_names, details=str(sorted(part_names)))

    incl = r.incline_dir()

    # ---- Per-unit step band: PRISMATIC up the incline; advances when posed. --
    for suffix, _ in units:
        band = object_model.get_part(f"step_band_{suffix}")
        j = object_model.get_articulation(f"step_travel_{suffix}")
        ctx.check(
            f"unit {suffix}: step band is PRISMATIC",
            j.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={j.articulation_type}",
        )
        ax = j.axis
        ctx.check(
            f"unit {suffix}: step axis points up the incline",
            abs(ax[0] - incl[0]) < 1e-6
            and abs(ax[1]) < 1e-6
            and abs(ax[2] - incl[2]) < 1e-6,
            details=f"axis={tuple(ax)} incline={incl}",
        )
        # N coarse Box treads present (the multiplicity).
        tread_visuals = [v.name for v in band.visuals if v.name.startswith("tread_")]
        ctx.check(
            f"unit {suffix}: N coarse-box treads present",
            len(tread_visuals) == r.step_count,
            details=f"treads={len(tread_visuals)} expected N={r.step_count}",
        )
        # Band rises along the incline and stays within the skirts.
        band_aabb = ctx.part_world_aabb(band)
        if band_aabb is not None:
            (sx0, sy0, sz0), (sx1, sy1, sz1) = band_aabb
            ctx.check(
                f"unit {suffix}: step band rises along the incline",
                (sz1 - sz0) > 0.20 and (sx1 - sx0) > 0.40,
                details=f"dx={sx1 - sx0:.3f} dz={sz1 - sz0:.3f}",
            )
            ctx.check(
                f"unit {suffix}: step band width within the skirts",
                (sy1 - sy0) <= r.tread_width + 0.02,
                details=f"dy={sy1 - sy0:.3f} tread_width={r.tread_width:.3f}",
            )
        # Advances up-slope when driven by one step pitch.
        rest = ctx.part_world_position(band)
        with ctx.pose({j: r.step_pitch}):
            advanced = ctx.part_world_position(band)
        if rest is not None and advanced is not None:
            ctx.check(
                f"unit {suffix}: step band advances up the incline when posed",
                advanced[0] > rest[0] + 0.01 and advanced[2] > rest[2] + 0.005,
                details=f"rest={rest} advanced={advanced}",
            )

    # ---- Handrails: welded parent visuals on the frame, invariant on travel. -
    for suffix, _ in units:
        for side in ("left", "right"):
            has_rail = any(v.name == f"{side}_rail_{suffix}" for v in frame.visuals)
            ctx.check(
                f"unit {suffix}: {side} handrail welded as a frame visual (no joint)",
                has_rail,
                details=f"{side}_rail_{suffix} present={has_rail}",
            )
        # No handrail joint exists (it is a parent visual, not a part).
    joint_names = {a.name for a in object_model.articulations}
    ctx.check(
        "no handrail articulation exists (handrails are welded parent visuals)",
        not any("handrail" in n or "rail" in n for n in joint_names),
        details=f"joints={sorted(joint_names)}",
    )

    # Handrail world AABB invariant under step-band travel (welded, not moving).
    for suffix, _ in units:
        j = object_model.get_articulation(f"step_travel_{suffix}")
        hr0 = ctx.part_element_world_aabb(frame, elem=f"left_rail_{suffix}")
        with ctx.pose({j: r.step_pitch}):
            hr1 = ctx.part_element_world_aabb(frame, elem=f"left_rail_{suffix}")
        if hr0 is not None and hr1 is not None:
            drift = max(abs(hr0[i][k] - hr1[i][k]) for i in range(2) for k in range(3))
            ctx.check(
                f"unit {suffix}: handrail invariant under step travel",
                drift < 1e-9,
                details=f"drift={drift:.2e}",
            )

    # ---- Balustrade panels present on both sides per unit (identity). ----
    for suffix, _ in units:
        for side in ("left", "right"):
            base = _balustrade_panel_basename(r, side)
            present = any(v.name == f"{base}_{suffix}" for v in frame.visuals)
            ctx.check(
                f"unit {suffix}: {side} balustrade panel present",
                present,
                details=f"{base}_{suffix} present={present}",
            )

    # ---- Handrails ride above the step band, outboard of the treads. ----
    for suffix, _ in units:
        band = object_model.get_part(f"step_band_{suffix}")
        band_aabb = ctx.part_world_aabb(band)
        lr = ctx.part_element_world_aabb(frame, elem=f"left_rail_{suffix}")
        rr = ctx.part_element_world_aabb(frame, elem=f"right_rail_{suffix}")
        if band_aabb is not None and lr is not None and rr is not None:
            ctx.check(
                f"unit {suffix}: handrails ride above the step band",
                lr[1][2] > band_aabb[1][2] and rr[1][2] > band_aabb[1][2],
                details=f"rail_tops=({lr[1][2]:.2f},{rr[1][2]:.2f}) band_top={band_aabb[1][2]:.2f}",
            )

    # ---- Pit cover: REVOLUTE about +Y, seats flush closed, lifts open. ----
    if r.landing_pit == "hinged_pit_cover":
        for suffix, _ in units:
            cover = object_model.get_part(f"pit_cover_{suffix}")
            j = object_model.get_articulation(f"pit_hinge_{suffix}")
            ctx.check(
                f"unit {suffix}: pit cover is REVOLUTE about +Y",
                j.articulation_type == ArticulationType.REVOLUTE
                and abs(j.axis[1] - 1.0) < 1e-6,
                details=f"type={j.articulation_type} axis={tuple(j.axis)}",
            )
            with ctx.pose({j: 0.0}):
                closed = ctx.part_world_aabb(cover)
            with ctx.pose({j: 1.2}):
                opened = ctx.part_world_aabb(cover)
            if closed is not None and opened is not None:
                ctx.check(
                    f"unit {suffix}: pit cover lifts when the hinge opens",
                    opened[1][2] > closed[1][2] + 0.25,
                    details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
                )
                ctx.check(
                    f"unit {suffix}: closed pit cover lies near the landing surface",
                    closed[1][2] < r.landing_top_z + 0.06,
                    details=f"closed_top={closed[1][2]:.3f} landing={r.landing_top_z:.3f}",
                )

    # ---- Twin layout: two disjoint step bands mirrored about y=0 + divider. --
    if r.unit_layout == "twin":
        aabb_a = ctx.part_world_aabb(object_model.get_part("step_band_a"))
        aabb_b = ctx.part_world_aabb(object_model.get_part("step_band_b"))
        if aabb_a is not None and aabb_b is not None:
            ctx.check(
                "twin: two side-by-side step bands with a clear gap",
                aabb_a[0][1] > aabb_b[1][1] + 0.03,
                details=f"a_y=({aabb_a[0][1]:.2f},{aabb_a[1][1]:.2f}) "
                f"b_y=({aabb_b[0][1]:.2f},{aabb_b[1][1]:.2f})",
            )
        ctx.check(
            "twin: center divider fuses the two trusses",
            any(v.name == "center_divider" for v in frame.visuals),
            details="center_divider present",
        )

    # ---- Frame rests near the ground. ----
    aabb = ctx.part_world_aabb(frame)
    if aabb is not None:
        ctx.check(
            "frame rests near the ground",
            aabb[0][2] < 0.05,
            details=f"z_min={aabb[0][2]:.4f}",
        )

    # ---- step_pitch == PRISMATIC travel (equation, not independently sampled).
    for suffix, _ in units:
        j = object_model.get_articulation(f"step_travel_{suffix}")
        ctx.check(
            f"unit {suffix}: PRISMATIC upper == one step pitch",
            abs(j.motion_limits.upper - r.step_pitch) < 1e-6,
            details=f"upper={j.motion_limits.upper:.4f} pitch={r.step_pitch:.4f}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with N + spine encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "EscalatorConfig",
    "ResolvedEscalatorConfig",
    "build_escalator",
    "build_seeded_escalator",
    "config_from_seed",
    "resolve_config",
    "run_escalator_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
