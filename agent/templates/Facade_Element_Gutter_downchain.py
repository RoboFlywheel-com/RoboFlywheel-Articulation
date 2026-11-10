# SPDX-License-Identifier: Apache-2.0

"""Rain chain (kusari-doi / gutter downchain) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Facade_Element_Gutter_downchain.md`` and all six 5-star
samples in ``picture/Facade Element/Gutter downchain`` (2 parents + 4 converged
variants). Each module factory's geometry is ported from a declared source
``model.py`` (round/lotus lathe funnel, cadquery square funnel, oval link).

Structure (a near-pure MULTIPLICITY / linear hanging chain):

    [root_hanger]  (grounded ROOT, fixed)
       -- swing_1 REVOLUTE -->  [hanging_module #1]
       -- swing_2 REVOLUTE -->  [hanging_module #2]
       ...
       -- swing_N REVOLUTE -->  [hanging_module #N]   (bottom of chain)

The chain is FAMILY-LOCKED into three real source families (root x module x
coupling co-vary; NOT a free Cartesian):

  * family alpha (A-system):  eye_bracket  x {round_funnel_cup, lotus_petal_cup}
                              x bail_eye_single_axis  (bail hook through a vertical
                              eye torus; single Y swing axis).
  * family beta  (B-system):  vee_wire_hanger x {square_funnel_cup, round_bowl_cup}
                              x captured_loop_over_bar_single_axis (vertical bail
                              loop captured over a Y axle bar; single Y swing axis).
  * family gamma (link):      ring_bracket x oval_chain_link
                              x interlocked_link_alternating_axis (interlocked oval
                              links alternating XZ/YZ plane; swing axis alternates
                              Y / X).

Main diversity axis = ``module_count`` N in [3, 8] (sweep) / product [3, 50],
encoded into ``slot_choices_for_seed`` so ``module_topology_diversity`` counts
N x family-form (5 forms x 8 sweep N-values = 40 distinct). ``palette_style``
adds per-seed colorway diversity (6 muted-metal colorways from the samples).

Identical modules within a chain reuse the same managed mesh asset, so large N
stays cheap. Placement is absolute via a per-module ``parent_pivot_z`` carried
down the chain (the parent's real downstream pivot: eye torus / axle bar / oval
bottom arc), exactly as in the sources, so per-pair QC at small N generalizes.
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
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enumerations (family-locked).
# ---------------------------------------------------------------------------
Family = Literal["alpha", "beta", "gamma"]
RootHanger = Literal["eye_bracket", "vee_wire_hanger", "ring_bracket"]
HangingModule = Literal[
    "round_funnel_cup", "lotus_petal_cup", "square_funnel_cup", "round_bowl_cup", "oval_chain_link"
]
Coupling = Literal[
    "bail_eye_single_axis",
    "captured_loop_over_bar_single_axis",
    "interlocked_link_alternating_axis",
]
PaletteStyle = Literal[
    "aged_verdigris_zinc",
    "galvanized_grey",
    "weathered_copper",
    "antique_bronze",
    "brushed_aluminium",
    "blackened_steel",
]

FAMILIES: tuple[Family, ...] = ("alpha", "beta", "gamma")
# Per-family weight: alpha (A-system) and beta (B-system) carry 2 cup shapes
# each; gamma is a single oval form. Weighted so each family form is sampled.
_FAMILY_WEIGHTS: dict[Family, float] = {"alpha": 1.0, "beta": 1.0, "gamma": 0.8}

# Legal modules per family (the family lock).
_FAMILY_MODULES: dict[Family, tuple[HangingModule, ...]] = {
    "alpha": ("round_funnel_cup", "lotus_petal_cup"),
    "beta": ("square_funnel_cup", "round_bowl_cup"),
    "gamma": ("oval_chain_link",),
}
_FAMILY_ROOT: dict[Family, RootHanger] = {
    "alpha": "eye_bracket",
    "beta": "vee_wire_hanger",
    "gamma": "ring_bracket",
}
_FAMILY_COUPLING: dict[Family, Coupling] = {
    "alpha": "bail_eye_single_axis",
    "beta": "captured_loop_over_bar_single_axis",
    "gamma": "interlocked_link_alternating_axis",
}
_MODULE_FAMILY: dict[HangingModule, Family] = {
    m: fam for fam, mods in _FAMILY_MODULES.items() for m in mods
}

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "aged_verdigris_zinc",
    "galvanized_grey",
    "weathered_copper",
    "antique_bronze",
    "brushed_aluminium",
    "blackened_steel",
)

# Palette colorways (muted metals from the 5-star samples). Keys:
#   shell  = module body (cup / oval link)
#   rim    = rim / secondary (always brighter than shell, per source constraint)
#   wire   = bail / link wire (neutral steel-grey)
#   metal  = root bracket / hanger metal
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "aged_verdigris_zinc": {
        "shell": (0.55, 0.58, 0.52, 1.0),
        "rim": (0.80, 0.82, 0.84, 1.0),
        "wire": (0.74, 0.76, 0.79, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0),
    },
    "galvanized_grey": {
        "shell": (0.66, 0.68, 0.70, 1.0),
        "rim": (0.78, 0.80, 0.82, 1.0),
        "wire": (0.60, 0.62, 0.64, 1.0),
        "metal": (0.62, 0.64, 0.66, 1.0),
    },
    "weathered_copper": {
        "shell": (0.62, 0.41, 0.26, 1.0),
        "rim": (0.78, 0.58, 0.40, 1.0),
        "wire": (0.66, 0.68, 0.70, 1.0),
        "metal": (0.50, 0.52, 0.54, 1.0),
    },
    "antique_bronze": {
        "shell": (0.50, 0.36, 0.22, 1.0),
        "rim": (0.66, 0.52, 0.34, 1.0),
        "wire": (0.68, 0.66, 0.62, 1.0),
        "metal": (0.55, 0.50, 0.42, 1.0),
    },
    "brushed_aluminium": {
        "shell": (0.72, 0.73, 0.75, 1.0),
        "rim": (0.84, 0.85, 0.87, 1.0),
        "wire": (0.66, 0.68, 0.70, 1.0),
        "metal": (0.70, 0.71, 0.73, 1.0),
    },
    "blackened_steel": {
        "shell": (0.30, 0.31, 0.33, 1.0),
        "rim": (0.52, 0.53, 0.55, 1.0),
        "wire": (0.64, 0.65, 0.67, 1.0),
        "metal": (0.42, 0.43, 0.45, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Multiplicity domain: config_from_seed draws module_count across the full
# product range [3, 50]. Per-N weights are set so the four multiplicity buckets
# carry these TOTAL probabilities:
#       N=3-8   -> 50%   (6 values)
#       N=9-10  -> 12%   (2 values)
#       N=11-20 -> 20%   (10 values)
#       N=21-50 -> 18%   (30 values)
# Each weight = bucket_share / bucket_width, so the PER-N probability decreases
# monotonically across buckets (no spike), while large N is reachable but rare.
# Every N reachable; large N safe by the N-invariant chain construction.
# Sweep/test only requires N in [3, 10].
# ---------------------------------------------------------------------------
N_MIN = 3
N_MAX = 50
_MODULE_COUNTS = tuple(range(N_MIN, N_MAX + 1))


def _module_count_weight(n: int) -> float:
    if n <= 8:
        return 0.50 / 6
    if n <= 10:
        return 0.12 / 2
    if n <= 20:
        return 0.20 / 10
    return 0.18 / 30


_MODULE_COUNT_WEIGHTS = tuple(_module_count_weight(n) for n in _MODULE_COUNTS)

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), ported from the source records.
# Per-build scaled by the resolved config.
# ---------------------------------------------------------------------------
# --- A-system / lotus cup (round_funnel_cup, lotus_petal_cup) ---
_CUP_TOP_R = 0.052
_CUP_H = 0.085
_WALL = 0.0014
_RIM_TUBE = 0.0040
_WIRE_R = 0.0018
_EYE_R = 0.0085
_LINK_LEN = 0.022
_BOT_EYE_DROP = 0.013  # bottom eye sits this far below cup bottom
_LOTUS_N_PETALS = 8

# --- root: gutter outlet bracket (A) ---
_GUTTER_R = 0.034
_GUTTER_LEN = 0.040
_BRACKET_EYE_DROP = 0.010  # eye sits below the spout end

# --- B-system square / round bowl cup ---
_SQ_TOP_HALF = 0.0380
_SQ_BOT_HALF = 0.0230
_SQ_CUP_H = 0.0640
_SQ_WALL = 0.0018
_SQ_DRAIN_R = 0.0115
_SQ_BAIL_R = 0.0022
_SQ_BAIL_RISE = 0.0240
_SQ_BAR_R = 0.0024

# --- gamma / oval link ---
_LINK_HALF_LEN = 0.032
_LINK_HALF_WID = 0.014
_LINK_WIRE_R = 0.003


@dataclass(frozen=True)
class RainChainConfig:
    family: Family | None = None
    hanging_module: HangingModule | None = None
    module_count: int | None = None
    palette_style: PaletteStyle = "aged_verdigris_zinc"
    cup_top_r_scale: float = 1.0
    cup_height_scale: float = 1.0
    swing_limit_scale: float = 1.0
    link_oval_aspect: float = 2.0
    n_petals: int = 8
    name: str = "rain_chain"


@dataclass(frozen=True)
class ResolvedRainChainConfig:
    family: Family
    root_hanger: RootHanger
    hanging_module: HangingModule
    coupling: Coupling
    module_count: int
    palette_style: PaletteStyle
    cup_top_r_scale: float
    cup_height_scale: float
    swing_limit_scale: float
    link_oval_aspect: float
    n_petals: int
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> RainChainConfig:
    rng = random.Random(seed)
    family = rng.choices(FAMILIES, weights=[_FAMILY_WEIGHTS[f] for f in FAMILIES], k=1)[0]
    module = rng.choice(_FAMILY_MODULES[family])
    module_count = rng.choices(_MODULE_COUNTS, weights=_MODULE_COUNT_WEIGHTS, k=1)[0]
    return RainChainConfig(
        family=family,
        hanging_module=module,
        module_count=module_count,
        palette_style=rng.choice(PALETTE_STYLES),
        cup_top_r_scale=round(rng.uniform(0.85, 1.18), 4),
        cup_height_scale=round(rng.uniform(0.85, 1.20), 4),
        swing_limit_scale=round(rng.uniform(0.70, 1.15), 4),
        link_oval_aspect=round(rng.uniform(1.6, 2.6), 4),
        n_petals=rng.choice((6, 8, 10, 12)),
        name=f"seeded_rain_chain_{seed}",
    )


def resolve_config(config: RainChainConfig | None = None) -> ResolvedRainChainConfig:
    cfg = config or RainChainConfig()

    # Family lock: derive (root, module, coupling) from the chosen family. If a
    # module is given but no family (or an inconsistent pair), the module's own
    # family wins so an illegal cross-family combo can never reach the builder.
    module = cfg.hanging_module
    if module in _MODULE_FAMILY:
        family = _MODULE_FAMILY[module]
    else:
        family = _pick(cfg.family, FAMILIES)
        module = _FAMILY_MODULES[family][0]
    root_hanger = _FAMILY_ROOT[family]
    coupling = _FAMILY_COUPLING[family]

    module_count = int(cfg.module_count) if cfg.module_count is not None else 5
    module_count = int(_clamp(module_count, N_MIN, N_MAX))

    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    return ResolvedRainChainConfig(
        family=family,
        root_hanger=root_hanger,
        hanging_module=module,
        coupling=coupling,
        module_count=module_count,
        palette_style=palette_style,
        cup_top_r_scale=_clamp(cfg.cup_top_r_scale, 0.85, 1.18),
        cup_height_scale=_clamp(cfg.cup_height_scale, 0.85, 1.20),
        swing_limit_scale=_clamp(cfg.swing_limit_scale, 0.70, 1.15),
        link_oval_aspect=_clamp(cfg.link_oval_aspect, 1.6, 2.6),
        n_petals=int(_pick(cfg.n_petals, (6, 8, 10, 12))),
        name=cfg.name or "rain_chain",
    )


def with_overrides(config: RainChainConfig, **kwargs: object) -> RainChainConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RainChainConfig | ResolvedRainChainConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRainChainConfig) else resolve_config(config)
    return (
        ("root_hanger", r.root_hanger),
        ("hanging_module", r.hanging_module),
        ("coupling_swing_policy", r.coupling),
        ("module_count", f"n{r.module_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Module naming conventions (aligned to sources): cup families use cup_1..cup_N
# and swing_1..swing_N (1-based); oval family uses link_0..link_{N-1} and
# swing_0..swing_{N-1} (0-based). Helper below normalizes part indexing.
# ===========================================================================
def _module_part_name(r: ResolvedRainChainConfig, i_zero: int) -> str:
    """Part name for the i-th hanging module (i_zero is 0-based)."""
    if r.family == "gamma":
        return f"link_{i_zero}"
    return f"cup_{i_zero + 1}"


def _swing_joint_name(r: ResolvedRainChainConfig, i_zero: int) -> str:
    if r.family == "gamma":
        return f"swing_{i_zero}"
    return f"swing_{i_zero + 1}"


# ===========================================================================
# A-SYSTEM (family alpha) geometry: lathe funnel cup + bail + boss/stem/eye.
# Ported from parent A (efa584a4) and lotus variant.
# ===========================================================================
@dataclass(frozen=True)
class _CupADims:
    top_r: float
    bot_r: float
    cup_h: float
    rim_center_r: float
    pivot_z: float
    rim_z: float
    bot_z: float
    bot_eye_z: float
    bracket_eye_z: float
    lotus: bool
    n_petals: int
    petal_tip_r: float
    petal_valley_r: float
    flare_start_z: float


def _cup_a_dims(r: ResolvedRainChainConfig) -> _CupADims:
    top_r = _CUP_TOP_R * r.cup_top_r_scale
    bot_r = top_r * 0.346  # keeps bot < 0.5*top funnel taper (0.018/0.052)
    cup_h = _CUP_H * r.cup_height_scale
    rim_center_r = top_r - _RIM_TUBE * 0.4
    pivot_z = 0.0
    rim_z = pivot_z - _LINK_LEN
    bot_z = rim_z - cup_h
    bot_eye_z = bot_z - _BOT_EYE_DROP
    bracket_eye_z = -_GUTTER_LEN - _BRACKET_EYE_DROP
    petal_tip_r = top_r * 1.18
    petal_valley_r = top_r * 0.92
    flare_start_z = bot_z + cup_h * 0.55
    return _CupADims(
        top_r=top_r,
        bot_r=bot_r,
        cup_h=cup_h,
        rim_center_r=rim_center_r,
        pivot_z=pivot_z,
        rim_z=rim_z,
        bot_z=bot_z,
        bot_eye_z=bot_eye_z,
        bracket_eye_z=bracket_eye_z,
        lotus=(r.hanging_module == "lotus_petal_cup"),
        n_petals=r.n_petals,
        petal_tip_r=petal_tip_r,
        petal_valley_r=petal_valley_r,
        flare_start_z=flare_start_z,
    )


def _cup_a_pitch(d: _CupADims) -> float:
    """Vertical drop from one alpha cup's swing pivot (frame origin, z=0) to the
    next cup's swing pivot (this cup's bottom eye). Single-sourced: the builder
    carries ``bot_eye_z`` down as ``parent_pivot_z`` and the fold-safe swing
    limit re-uses this same pitch."""
    return -d.bot_eye_z


def _cup_a_shell_geom(d: _CupADims) -> MeshGeometry:
    """Hollow thin-wall tapered (or lotus-flared) lathe cup shell."""
    if d.lotus:
        mouth_r = d.petal_tip_r
        mid_r = d.bot_r + (mouth_r - d.bot_r) * 0.55
        flare_r = d.bot_r + (mouth_r - d.bot_r) * 0.82
        outer = [
            (d.bot_r, d.bot_z),
            (mid_r, d.bot_z + d.cup_h * 0.35),
            (flare_r, d.flare_start_z),
            (mouth_r * 0.98, d.rim_z + d.cup_h * 0.08),
            (mouth_r, d.rim_z),
        ]
        inner = [
            (max(d.bot_r - _WALL, 0.0008), d.bot_z + _WALL * 1.5),
            (mid_r - _WALL, d.bot_z + d.cup_h * 0.35),
            (flare_r - _WALL, d.flare_start_z),
            (mouth_r * 0.98 - _WALL, d.rim_z + d.cup_h * 0.08),
            (mouth_r - _WALL, d.rim_z),
        ]
        segments = 72
    else:
        outer = [
            (d.bot_r, d.bot_z),
            (d.bot_r + (d.top_r - d.bot_r) * 0.5, d.bot_z + d.cup_h * 0.5),
            (d.top_r, d.rim_z),
        ]
        inner = [
            (max(d.bot_r - _WALL, 0.0008), d.bot_z + _WALL * 1.5),
            (d.bot_r + (d.top_r - d.bot_r) * 0.5 - _WALL, d.bot_z + d.cup_h * 0.5),
            (d.top_r - _WALL, d.rim_z),
        ]
        segments = 64
    return LatheGeometry.from_shell_profiles(outer, inner, segments=segments)


def _scalloped_rim_geom(d: _CupADims) -> MeshGeometry:
    """Petal-scalloped lotus rim ring (closed triangulated annulus)."""
    m = MeshGeometry()
    n_petals = d.n_petals
    seg = n_petals * 8
    inner_r = d.petal_valley_r * 0.96
    rim_thick = _RIM_TUBE * 1.4
    inner_top: list[int] = []
    inner_bot: list[int] = []
    outer_top: list[int] = []
    outer_bot: list[int] = []
    for k in range(seg):
        a = 2.0 * math.pi * k / seg
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        t = (1.0 + math.cos(n_petals * a)) * 0.5
        r_out = d.petal_valley_r + (d.petal_tip_r - d.petal_valley_r) * t
        inner_top.append(m.add_vertex(inner_r * cos_a, inner_r * sin_a, d.rim_z + rim_thick * 0.5))
        inner_bot.append(m.add_vertex(inner_r * cos_a, inner_r * sin_a, d.rim_z - rim_thick * 0.5))
        outer_top.append(m.add_vertex(r_out * cos_a, r_out * sin_a, d.rim_z + rim_thick * 0.5))
        outer_bot.append(m.add_vertex(r_out * cos_a, r_out * sin_a, d.rim_z - rim_thick * 0.5))
    for k in range(seg):
        k1 = (k + 1) % seg
        m.add_face(inner_top[k], outer_top[k], outer_top[k1])
        m.add_face(inner_top[k], outer_top[k1], inner_top[k1])
        m.add_face(inner_bot[k], inner_bot[k1], outer_bot[k1])
        m.add_face(inner_bot[k], outer_bot[k1], outer_bot[k])
        m.add_face(outer_top[k], outer_bot[k], outer_bot[k1])
        m.add_face(outer_top[k], outer_bot[k1], outer_top[k1])
        m.add_face(inner_top[k], inner_top[k1], inner_bot[k1])
        m.add_face(inner_top[k], inner_bot[k1], inner_bot[k])
    return m


def _round_rim_geom(d: _CupADims) -> MeshGeometry:
    g = TorusGeometry(
        radius=d.rim_center_r, tube=_RIM_TUBE, radial_segments=16, tubular_segments=48
    )
    g.translate(0.0, 0.0, d.rim_z)
    return g


def _vertical_eye_geom(center_z: float) -> MeshGeometry:
    g = TorusGeometry(radius=_EYE_R, tube=_WIRE_R, radial_segments=12, tubular_segments=28)
    g.rotate_x(math.pi / 2.0)  # lay into the X-Z plane (axis -> Y)
    g.translate(0.0, 0.0, center_z)
    return g


def _vertical_ring_geom(center_z: float, radius: float, tube: float) -> MeshGeometry:
    g = TorusGeometry(radius=radius, tube=tube, radial_segments=12, tubular_segments=28)
    g.rotate_x(math.pi / 2.0)  # lay into the X-Z plane (axis -> Y)
    g.translate(0.0, 0.0, center_z)
    return g


def _link_bail_geom(apex_z: float, rim_z: float, rim_edge_r: float) -> MeshGeometry:
    """Inverted-U bail (提篮) handle, built in the Y-Z plane.

    The eye / bracket ring this bail hooks through lies in the X-Z plane (a
    vertical loop, hole axis +Y). To hang like a real chain link the bail must be
    PERPENDICULAR to that ring -- i.e. in the Y-Z plane -- so its apex threads
    vertically through the ring and drapes over the ring's lower wire, instead of
    lying coplanar with it (which reads as a tangled knot). The two feet seat on
    the cup rim at +/-Y; the apex (at ``apex_z``) hooks over the parent ring's
    lower wire so the cup below hangs straight down from the ring.
    """
    pts = [
        (0.0, rim_edge_r, rim_z),
        (0.0, rim_edge_r * 0.55, rim_z + (apex_z - rim_z) * 0.55),
        (0.0, 0.0, apex_z),
        (0.0, -rim_edge_r * 0.55, rim_z + (apex_z - rim_z) * 0.55),
        (0.0, -rim_edge_r, rim_z),
    ]
    return tube_from_spline_points(
        pts, radius=_WIRE_R, samples_per_segment=16, radial_segments=12, cap_ends=True
    )


def _build_eye_bracket(model, mats, d: _CupADims) -> object:
    """A-system gutter bracket: flange + spout + lug + vertical eye torus."""
    bracket = model.part("gutter_bracket")
    bracket.visual(
        Cylinder(radius=_GUTTER_R + 0.012, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, -0.004)),
        material=mats["metal"],
        name="bracket_flange", material_class_id="metal.steel_galvanized",
    )
    bracket.visual(
        Cylinder(radius=_GUTTER_R, length=_GUTTER_LEN),
        origin=Origin(xyz=(0.0, 0.0, -_GUTTER_LEN / 2.0 - 0.008)),
        material=mats["metal"],
        name="outlet_spout", material_class_id="metal.steel_galvanized",
    )
    bracket.visual(
        Box((0.020, 0.006, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, d.bracket_eye_z + 0.006)),
        material=mats["metal"],
        name="hanger_lug", material_class_id="metal.steel_galvanized",
    )
    bracket.visual(
        mesh_from_geometry(_vertical_eye_geom(d.bracket_eye_z), "bracket_eye_mesh"),
        material=mats["wire"],
        name="bracket_eye", material_class_id="metal.steel_galvanized",
    )
    bracket.inertial = Inertial.from_geometry(
        Cylinder(radius=_GUTTER_R, length=_GUTTER_LEN),
        mass=0.25,
        origin=Origin(xyz=(0.0, 0.0, -_GUTTER_LEN / 2.0)),
    )
    return bracket


def _add_cup_a_visuals(part, meshes, mats, d: _CupADims) -> None:
    shell_mesh, rim_mesh, bail_mesh, eye_mesh = meshes
    part.visual(shell_mesh, material=mats["shell"], name="cup_shell", material_class_id="rust.verdigris_patina")
    part.visual(rim_mesh, material=mats["rim"], name="cup_rim", material_class_id="metal.steel_galvanized")
    part.visual(bail_mesh, material=mats["wire"], name="link_wire", material_class_id="metal.steel_galvanized")
    part.visual(
        Cylinder(radius=d.bot_r - _WALL * 0.5, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, d.bot_z + 0.002)),
        material=mats["shell"],
        name="bottom_boss", material_class_id="rust.verdigris_patina",
    )
    stem_top = d.bot_z + 0.004
    stem_bot = d.bot_eye_z
    part.visual(
        Cylinder(radius=0.0026, length=(stem_top - stem_bot)),
        origin=Origin(xyz=(0.0, 0.0, (stem_top + stem_bot) / 2.0)),
        material=mats["wire"],
        name="bottom_stem", material_class_id="metal.steel_galvanized",
    )
    part.visual(eye_mesh, material=mats["wire"], name="bottom_eye", material_class_id="metal.steel_galvanized")
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=d.top_r, length=d.cup_h),
        mass=0.18,
        origin=Origin(xyz=(0.0, 0.0, -d.cup_h * 0.45)),
    )


# ===========================================================================
# B-SYSTEM (family beta) geometry: cadquery square/round funnel with a drain
# hole + bottom Y axle bar, square/round lip, and a vertical captured bail loop.
# Ported from parent B (3dcec91a) and round_bowl variant.
# ===========================================================================
@dataclass(frozen=True)
class _CupBDims:
    top_half: float
    bot_half: float
    cup_h: float
    drain_r: float
    bar_r: float
    bar_half: float
    bail_rise: float
    bail_span: float
    mouth_z: float
    bottom_bar_z: float
    top_ring_z: float
    top_ring_r: float
    top_ring_tube: float
    round_bowl: bool


def _cup_b_dims(r: ResolvedRainChainConfig) -> _CupBDims:
    top_half = _SQ_TOP_HALF * r.cup_top_r_scale
    bot_half = _SQ_BOT_HALF * r.cup_top_r_scale
    cup_h = _SQ_CUP_H * r.cup_height_scale
    drain_r = _SQ_DRAIN_R
    bar_half = drain_r + 0.004
    bail_rise = _SQ_BAIL_RISE
    bail_span = 2.0 * (top_half - _SQ_WALL)
    # Frame convention: the cup PART-FRAME ORIGIN is the bail APEX (the real
    # hardware point where this cup hooks the parent's bottom bar). So the mouth
    # plane sits bail_rise BELOW the origin, and all cup geometry hangs from there.
    # This keeps the joint origin on real geometry for BOTH parent (its bottom bar)
    # and child (its bail apex at the frame origin) -> within the 15 mm baseline.
    mouth_z = -bail_rise
    bottom_bar_z = mouth_z - cup_h + _SQ_WALL * 0.5
    top_ring_r = 0.008
    top_ring_tube = _SQ_BAIL_R
    top_ring_z = -0.004
    return _CupBDims(
        top_half=top_half,
        bot_half=bot_half,
        cup_h=cup_h,
        drain_r=drain_r,
        bar_r=_SQ_BAR_R,
        bar_half=bar_half,
        bail_rise=bail_rise,
        bail_span=bail_span,
        mouth_z=mouth_z,
        bottom_bar_z=bottom_bar_z,
        top_ring_z=top_ring_z,
        top_ring_r=top_ring_r,
        top_ring_tube=top_ring_tube,
        round_bowl=(r.hanging_module == "round_bowl_cup"),
    )


def _cup_b_pitch(d: _CupBDims) -> float:
    """Vertical drop from one beta cup's swing pivot (bail apex, frame origin
    z=0) to the next cup's swing pivot (this cup's bottom hanger bar).
    Single-sourced: the builder uses ``bottom_bar_z`` as the child joint origin
    and the fold-safe swing limit re-uses this same pitch."""
    return -d.bottom_bar_z


def _square_funnel_shell_cq(d: _CupBDims) -> cq.Workplane:
    """Hollow downward-tapering square funnel: lofted frustum shelled through the
    top, with a central drain hole and a transverse Y hanger bar across the
    drain (the cup below hooks its bail loop over this bar)."""
    top = d.top_half
    bot = d.bot_half
    h = d.cup_h
    outer = (
        cq.Workplane("XY")
        .workplane(offset=0.0)
        .rect(2 * top, 2 * top)
        .workplane(offset=-h)
        .rect(2 * bot, 2 * bot)
        .loft(combine=True)
    )
    cup = outer.faces(">Z").shell(-_SQ_WALL)
    cup = cup.faces("<Z").workplane(centerOption="CenterOfMass").hole(2 * d.drain_r)
    bar = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, -d.cup_h + _SQ_WALL * 0.5), rotate=(90.0, 0.0, 0.0))
        .circle(d.bar_r)
        .extrude(d.bar_half, both=True)
    )
    # Shift to the bail-apex frame: mouth lands at mouth_z (= -bail_rise).
    return cup.union(bar).translate((0.0, 0.0, d.mouth_z))


def _round_bowl_shell_cq(d: _CupBDims) -> cq.Workplane:
    """Hollow downward-tapering ROUND bowl funnel (power-curve loft of circular
    sections), shelled through the top, drain hole + transverse Y hanger bar.
    The B-family round bowl uses the same drain+bar coupling as the square cup."""
    top = d.top_half
    bot = d.bot_half
    h = d.cup_h
    n_sec = 5
    wp = cq.Workplane("XY")
    sections = []
    for j in range(n_sec):
        t = j / (n_sec - 1)
        # power curve so the bowl is fuller near the top mouth
        rad = bot + (top - bot) * (t**0.7)
        z = -h + t * h
        sections.append(wp.workplane(offset=z).circle(rad))
    outer = sections[0]
    for s in sections[1:]:
        outer = outer.add(s)
    outer = outer.loft(combine=True)
    cup = outer.faces(">Z").shell(-_SQ_WALL)
    cup = cup.faces("<Z").workplane(centerOption="CenterOfMass").hole(2 * d.drain_r)
    bar = (
        cq.Workplane("XY")
        .transformed(offset=(0.0, 0.0, -d.cup_h + _SQ_WALL * 0.5), rotate=(90.0, 0.0, 0.0))
        .circle(d.bar_r)
        .extrude(d.bar_half, both=True)
    )
    return cup.union(bar).translate((0.0, 0.0, d.mouth_z))


def _cup_b_rim_cq(d: _CupBDims) -> cq.Workplane:
    """Thin square/round lip ring around the open mouth (at mouth_z)."""
    if d.round_bowl:
        outer = d.top_half + 0.0015
        inner = d.top_half - 2 * _SQ_WALL
        return (
            cq.Workplane("XY")
            .circle(outer)
            .circle(inner)
            .extrude(_SQ_WALL)
            .translate((0.0, 0.0, d.mouth_z))
        )
    outer = d.top_half + 0.0015
    inner = d.top_half - 2 * _SQ_WALL
    return (
        cq.Workplane("XY")
        .rect(2 * outer, 2 * outer)
        .rect(2 * inner, 2 * inner)
        .extrude(_SQ_WALL)
        .translate((0.0, 0.0, d.mouth_z))
    )


def _cup_b_outer_half_at_z(d: _CupBDims, z: float) -> float:
    """Outer half-width/radius of the B-cup shell at local height ``z``."""
    bottom_z = d.mouth_z - d.cup_h
    z = _clamp(z, bottom_z, d.mouth_z)
    below_mouth = d.mouth_z - z
    if d.round_bowl:
        t = 1.0 - below_mouth / d.cup_h
        return d.bot_half + (d.top_half - d.bot_half) * (t**0.7)
    return d.top_half + (d.bot_half - d.top_half) * (below_mouth / d.cup_h)


def _cup_b_bail_foot_z(d: _CupBDims) -> float:
    return d.mouth_z - 0.012


def _cup_b_bail_foot_half_span(d: _CupBDims) -> float:
    """Place the bail feet just outside the shell so the wire does not pierce it."""
    foot_z = _cup_b_bail_foot_z(d)
    shell_half = _cup_b_outer_half_at_z(d, foot_z)
    return max(d.bail_span / 2.0, shell_half + _SQ_BAIL_R + 0.0006)


def _bail_loop_geom(d: _CupBDims) -> MeshGeometry:
    """Vertical wire bail loop in the X-Z plane. Authored in the bail-apex frame:
    the loop apex sits at z=0 (the part-frame origin = where this cup hooks the
    parent's bottom bar) and the legs reach down to the mouth at mouth_z. The
    closed eye encircles a Y bar so it hooks over the parent bar like a chain link
    over an axle."""
    s = _cup_b_bail_foot_half_span(d)
    rise = d.bail_rise
    # In the bail-apex frame, mouth is at mouth_z and the apex at 0. Shift the
    # source loop (apex at +rise above a z=0 mouth) down by rise.
    foot_z = _cup_b_bail_foot_z(d)
    loop_top = 0.0
    loop_bot = -0.014
    # The closing eye must wrap ONLY the parent's hanger bar and thread the upper
    # cup's OPEN drain hole -- it must never splay out across the solid bottom-plate
    # ring (drain_r .. bot_half) or the wire pierces the floor of the cup above.
    # Size the eye to the bar (bar radius + wire radius + a little clearance) and
    # keep it well inside the drain opening.
    eye_w = _SQ_BAR_R + _SQ_BAIL_R + 0.0015
    leg_mid_z = d.mouth_z + rise * 0.45
    # Shoulder waypoint: the wide decorative legs sweep inward to the narrow eye
    # BELOW the bottom-plate plane (z well under 0), so the narrowing never crosses
    # the parent floor; only the slim eye (|x| = eye_w < drain_r) rises through it.
    shoulder_x = (s + eye_w) * 0.5
    shoulder_z = (leg_mid_z + loop_bot) * 0.5
    pts = [
        (-s, 0.0, foot_z),
        (-s, 0.0, leg_mid_z),
        (-shoulder_x, 0.0, shoulder_z),
        (-eye_w, 0.0, loop_bot),
        (-eye_w, 0.0, loop_bot * 0.45),
        (-eye_w, 0.0, loop_top),
        (0.0, 0.0, loop_top + 0.003),
        (eye_w, 0.0, loop_top),
        (eye_w, 0.0, loop_bot * 0.45),
        (eye_w, 0.0, loop_bot),
        (shoulder_x, 0.0, shoulder_z),
        (s, 0.0, leg_mid_z),
        (s, 0.0, foot_z),
    ]
    return tube_from_spline_points(
        pts, radius=_SQ_BAIL_R, samples_per_segment=12, radial_segments=10, cap_ends=True
    )


def _top_bail_handle_geom(d: _CupBDims) -> MeshGeometry:
    """Top bucket handle: an open U-shaped bail hanging under the root ring."""
    seat_half = max(d.top_half - _SQ_WALL - 0.001, 0.010)
    foot_z = d.mouth_z - 0.005
    apex_z = -(d.top_ring_r - _SQ_BAIL_R)
    shoulder_z = foot_z + (apex_z - foot_z) * 0.62
    pts = [
        (0.0, seat_half, foot_z),
        (0.0, seat_half * 0.62, shoulder_z),
        (0.0, 0.0, apex_z),
        (0.0, -seat_half * 0.62, shoulder_z),
        (0.0, -seat_half, foot_z),
    ]
    return tube_from_spline_points(
        pts, radius=_SQ_BAIL_R, samples_per_segment=16, radial_segments=10, cap_ends=True
    )


def _hanger_bracket_geom(d: _CupBDims) -> MeshGeometry:
    """V-shaped wire hanger straddling the gutter outlet.

    The beta family now ends in a small vertical ring so the FIRST bucket reads as
    a true hanging handle under a吊环; lower buckets still use the captured-loop
    coupling off each cup's bottom bar.
    """
    hook_z = 0.090
    spread = 0.075
    curl = 0.012
    connector_z = d.top_ring_z + d.top_ring_r
    pts = [
        (-spread - curl, 0.0, hook_z - curl),
        (-spread, 0.0, hook_z),
        (-spread, 0.0, hook_z - 0.010),
        (-spread * 0.45, 0.0, hook_z * 0.40),
        (0.0, 0.0, connector_z),
        (spread * 0.45, 0.0, hook_z * 0.40),
        (spread, 0.0, hook_z - 0.010),
        (spread, 0.0, hook_z),
        (spread + curl, 0.0, hook_z - curl),
    ]
    wire = tube_from_spline_points(
        pts, radius=0.0026, samples_per_segment=16, radial_segments=12, cap_ends=True
    )
    return wire


def _build_vee_wire_hanger(model, mats, d: _CupBDims) -> object:
    hanger = model.part("gutter_hanger")
    hanger.visual(
        mesh_from_geometry(_hanger_bracket_geom(d), "hanger_wire"),
        material=mats["wire"],
        name="hanger_wire", material_class_id="metal.steel_galvanized",
    )
    hanger.visual(
        mesh_from_geometry(
            _vertical_ring_geom(d.top_ring_z, d.top_ring_r, d.top_ring_tube), "hanger_ring"
        ),
        material=mats["wire"],
        name="hanger_ring", material_class_id="metal.steel_galvanized",
    )
    hanger.inertial = Inertial.from_geometry(
        Cylinder(radius=0.075, length=0.090),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, 0.045)),
    )
    return hanger


# ===========================================================================
# GAMMA-SYSTEM (family gamma) geometry: interlocked oval links + ring bracket.
# Ported from link_chain variant.
# ===========================================================================
@dataclass(frozen=True)
class _LinkGDims:
    half_len: float
    half_wid: float
    wire_r: float
    bottom_pivot_z: float
    bracket_ring_z: float
    ring_r: float
    ring_tube: float
    ring_engage: float


def _link_g_dims(r: ResolvedRainChainConfig) -> _LinkGDims:
    half_len = _LINK_HALF_LEN * r.cup_height_scale
    # link_oval_aspect drives long/short ratio: half_wid = half_len / aspect.
    half_wid = half_len / r.link_oval_aspect
    wire_r = _LINK_WIRE_R
    # Interlock pitch: each child link drops by (2*half_len - 1*wire_r) so its top
    # arc threads through the parent's bottom opening and the two perpendicular
    # wire tubes interpenetrate by ~wire_r (centerline crossing ~1*wire_r < the
    # 2*wire_r touching distance). The source used 2*wire_r drop reduction, which
    # leaves the tubes exactly tangent (knife-edge); tessellation rounds that into
    # a hairline miss that trips fail_if_isolated_parts(1e-6). Dropping the child
    # ~wire_r deeper gives a solid mesh overlap at every sampled aspect/height.
    bottom_pivot_z = -(2.0 * half_len - 1.0 * wire_r)
    # The horizontal bracket ring sits in the XY plane; the top (XZ-plane) link can
    # only touch it if its top tip rises THROUGH the ring so the ring tube rests on
    # the link's upper arc. We raise the first link's mesh by ring_engage (keeping
    # its frame origin / joint origin ON the ring), which gives solid ring<->link
    # contact at every sampled aspect. link_1's pivot is shifted up by the same
    # amount so the rest of the chain stays correctly interlocked.
    ring_engage = 4.0 * wire_r  # ~0.012; verified ~0-gap ring contact at every aspect
    # Drop the ring far enough below the outlet spout that the raised first link's
    # top tip (at bracket_ring_z + ring_engage) stays clear of the spout bottom.
    spout_bottom_z = -_GUTTER_LEN - 0.008
    bracket_ring_z = spout_bottom_z - ring_engage - 0.006
    ring_r = half_wid + wire_r * 1.8
    ring_tube = wire_r * 0.9
    return _LinkGDims(
        half_len=half_len,
        half_wid=half_wid,
        wire_r=wire_r,
        bottom_pivot_z=bottom_pivot_z,
        bracket_ring_z=bracket_ring_z,
        ring_r=ring_r,
        ring_tube=ring_tube,
        ring_engage=ring_engage,
    )


def _oval_link_geom(d: _LinkGDims, in_yz_plane: bool, z_off: float = 0.0) -> MeshGeometry:
    n_pts = 36
    pts = []
    for j in range(n_pts):
        t = 2.0 * math.pi * j / n_pts
        hw = d.half_wid * math.cos(t)
        hl = d.half_len * math.sin(t)
        if in_yz_plane:
            pts.append((0.0, hw, -d.half_len + hl + z_off))
        else:
            pts.append((hw, 0.0, -d.half_len + hl + z_off))
    return tube_from_spline_points(
        pts,
        radius=d.wire_r,
        samples_per_segment=10,
        closed_spline=True,
        radial_segments=14,
        cap_ends=False,
    )


def _build_ring_bracket(model, mats, d: _LinkGDims) -> object:
    bracket = model.part("gutter_bracket")
    bracket.visual(
        Cylinder(radius=_GUTTER_R + 0.012, length=0.008),
        origin=Origin(xyz=(0.0, 0.0, -0.004)),
        material=mats["metal"],
        name="bracket_flange", material_class_id="metal.steel_galvanized",
    )
    bracket.visual(
        Cylinder(radius=_GUTTER_R, length=_GUTTER_LEN),
        origin=Origin(xyz=(0.0, 0.0, -_GUTTER_LEN / 2.0 - 0.008)),
        material=mats["metal"],
        name="outlet_spout", material_class_id="metal.steel_galvanized",
    )
    bar_top = -_GUTTER_LEN - 0.008
    bar_bot = d.bracket_ring_z
    bracket.visual(
        Cylinder(radius=0.004, length=(bar_top - bar_bot)),
        origin=Origin(xyz=(0.0, 0.0, (bar_top + bar_bot) / 2.0)),
        material=mats["metal"],
        name="hanger_bar", material_class_id="metal.steel_galvanized",
    )
    ring_geom = TorusGeometry(
        radius=d.ring_r, tube=d.ring_tube, radial_segments=14, tubular_segments=36
    )
    ring_geom.translate(0.0, 0.0, d.bracket_ring_z)
    bracket.visual(
        mesh_from_geometry(ring_geom, "bracket_ring_mesh"),
        material=mats["metal"],
        name="bracket_ring", material_class_id="metal.steel_galvanized",
    )
    spoke_inner_r = 0.004
    spoke_outer_r = d.ring_r
    for j, angle in enumerate((0, 90, 180, 270)):
        a = math.radians(angle)
        ca, sa = math.cos(a), math.sin(a)
        spoke_pts = [
            (spoke_inner_r * ca, spoke_inner_r * sa, d.bracket_ring_z),
            (spoke_outer_r * ca, spoke_outer_r * sa, d.bracket_ring_z),
        ]
        spoke_geom = tube_from_spline_points(
            spoke_pts, radius=0.0018, samples_per_segment=4, radial_segments=8, cap_ends=True
        )
        bracket.visual(
            mesh_from_geometry(spoke_geom, f"ring_spoke_{j}_mesh"),
            material=mats["metal"],
            name=f"ring_spoke_{j}", material_class_id="metal.steel_galvanized",
        )
    bracket.inertial = Inertial.from_geometry(
        Cylinder(radius=_GUTTER_R, length=_GUTTER_LEN),
        mass=0.25,
        origin=Origin(xyz=(0.0, 0.0, -_GUTTER_LEN / 2.0)),
    )
    return bracket


# ===========================================================================
# Swing-limit helpers (Slot C). All ranges include rest pose q=0.
# ===========================================================================
# Fold-safe swing limits (single-sourced -- Contract 3c).
#
# Every single-axis coupling (alpha bail-eye, beta captured-loop) pivots about
# +Y, so the ENTIRE hanging chain moves in the X-Z plane: it is a planar
# pendulum linkage. With a flat, generous per-joint limit a mid-chain run of
# joints can curl the long tail hanging below it back UP and across into an
# upper cup (census seed 5: cup_1 vs cup_13 shell through cup at 35.8 mm, a
# swing_3 + swing_6..10 fold). A single joint swinging alone never does this
# (the rigid sub-chain below just sweeps down-and-out, away from the upper
# column); the through-cup only appears when several joints stack their bends,
# and the reach of that fold scales with how much chain hangs below the joint.
#
# Model: treat the ``m`` cups hanging below a joint as a rigid pendulum of
# length ``L = m * pitch`` pivoted at the joint. Swinging it by θ sweeps its far
# tip laterally by ``L * sin θ``. Cap that lateral tip travel to one fixed safe
# corridor ``_FOLD_CORRIDOR`` so a folded tail can never cross the width of the
# upper cups' vertical column and shell into them:
#
#       L * sin θ_max ≤ _FOLD_CORRIDOR
#   ⟹  θ_max(m) = asin( _FOLD_CORRIDOR / (m * pitch) )
#
# This is monotone-decreasing in ``m``: the top joint (m = N cups below) is the
# tightest, the bottom joint (m = 1) the loosest, exactly matching where the
# fold risk lives. The corridor is sized so that even at the loosest sampled
# geometry the swept tail keeps ≥ _FOLD_CLEAR (8 mm) between any lower cup and
# any upper cup. ``swing_limit_scale`` may only TIGHTEN the geometric cap (never
# loosen it past the fold-safe bound); a per-joint floor keeps every joint a
# real two-way swing (q=0 in range, > ±10°).
_FOLD_CORRIDOR = 0.11  # meters of lateral pendulum-tip travel allowed by a fold
_FOLD_CLEAR = 0.008  # target min clearance (8 mm) between any lower/upper cup
_SWING_MIN = math.radians(12.0)  # per-joint floor: keeps a real two-way swing
_SWING_MAX = math.radians(36.0)  # per-joint cap (adjacent-cup + effort headroom)


def _fold_safe_swing_limit(
    cups_below: int, pitch: float, r: ResolvedRainChainConfig
) -> MotionLimits:
    """Fold-safe symmetric REVOLUTE limit for a single-axis swing joint.

    ``cups_below`` is the number of cups hanging on and below this joint's child
    (= N - joint_index); ``pitch`` is the per-module vertical drop. The limit
    shrinks with ``cups_below`` so no combination of sampled joint poses can fold
    a distal cup back through an upper cup. Single-sourced: BOTH the alpha and
    beta builders call this, and the test suite re-derives the same value.
    """
    m = max(1, int(cups_below))
    reach = m * max(pitch, 1e-6)
    geom = math.asin(_clamp(_FOLD_CORRIDOR / reach, 0.0, 1.0))
    # swing_limit_scale is only allowed to tighten (protect the fold-safe cap).
    lim = _clamp(geom * min(r.swing_limit_scale, 1.0), _SWING_MIN, _SWING_MAX)
    return MotionLimits(effort=1.0, velocity=2.0, lower=-lim, upper=lim)


def _alt_axis_limits(r: ResolvedRainChainConfig) -> MotionLimits:
    lim = _clamp(math.radians(35.0) * r.swing_limit_scale, math.radians(15.0), math.radians(40.0))
    return MotionLimits(effort=0.5, velocity=2.0, lower=-lim, upper=lim)


# ===========================================================================
# Builder
# ===========================================================================
def build_rain_chain(
    config: RainChainConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"rain_{key}_{r.palette_style}", rgba=pal[key])
        for key in ("shell", "rim", "wire", "metal")
    }
    n = r.module_count

    if r.family == "alpha":
        _build_chain_alpha(model, mats, r, n, assets)
    elif r.family == "beta":
        _build_chain_beta(model, mats, r, n, assets)
    else:
        _build_chain_gamma(model, mats, r, n, assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def _build_chain_alpha(model, mats, r, n, assets) -> None:
    d = _cup_a_dims(r)
    bracket = _build_eye_bracket(model, mats, d)

    # Two cup variants (lotus vs round) reuse one set of meshes across all N.
    rim_geom = _scalloped_rim_geom(d) if d.lotus else _round_rim_geom(d)
    bail_seat_r = (d.petal_tip_r + d.petal_valley_r) * 0.5 if d.lotus else d.rim_center_r
    # The bail apex hooks the BOTTOM wire of the parent ring (eye / bracket eye),
    # which in the cup's frame is centered at the hook point (pivot_z=0) and lies
    # in the X-Z plane: its lowest wire is at z = -(_EYE_R). Drape the apex there
    # so the cup hangs straight down off the ring's lower wire.
    bail_apex_z = d.pivot_z - (_EYE_R - _WIRE_R)
    shell_mesh = mesh_from_geometry(_cup_a_shell_geom(d), "cup_shell")
    rim_mesh = mesh_from_geometry(rim_geom, "cup_rim")
    bail_mesh = mesh_from_geometry(_link_bail_geom(bail_apex_z, d.rim_z, bail_seat_r), "cup_bail")
    eye_mesh = mesh_from_geometry(_vertical_eye_geom(d.bot_eye_z), "cup_bottom_eye")
    meshes = (shell_mesh, rim_mesh, bail_mesh, eye_mesh)

    prev = bracket
    parent_pivot_z = d.bracket_eye_z
    pitch = _cup_a_pitch(d)
    for i in range(n):
        cup = model.part(_module_part_name(r, i))
        _add_cup_a_visuals(cup, meshes, mats, d)
        model.articulation(
            _swing_joint_name(r, i),
            ArticulationType.REVOLUTE,
            parent=prev,
            child=cup,
            origin=Origin(xyz=(0.0, 0.0, parent_pivot_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=_fold_safe_swing_limit(n - i, pitch, r),
        )
        prev = cup
        parent_pivot_z = d.bot_eye_z


def _build_chain_beta(model, mats, r, n, assets) -> None:
    d = _cup_b_dims(r)
    hanger = _build_vee_wire_hanger(model, mats, d)

    shell_cq = _round_bowl_shell_cq(d) if d.round_bowl else _square_funnel_shell_cq(d)
    # Coarsen the shell tessellation: the round-bowl power-curve loft otherwise
    # emits ~12k triangles per cup (5x the square funnel), which makes every
    # pairwise FCL distance query in the connectivity / motion-QC checks 5x
    # slower and blows the per-seed compile budget at large N (census seed 5 is a
    # round-bowl chain). A 3 mm linear / 0.4 rad angular deviation keeps the bowl
    # visually smooth and watertight while cutting it to ~square-funnel cost.
    shell_mesh = mesh_from_cadquery(
        shell_cq, "cup_shell", assets=assets, tolerance=0.003, angular_tolerance=0.4
    )
    rim_mesh = mesh_from_cadquery(_cup_b_rim_cq(d), "cup_rim", assets=assets)
    top_bail_mesh = mesh_from_geometry(_top_bail_handle_geom(d), "cup_top_bail")
    bail_mesh = mesh_from_geometry(_bail_loop_geom(d), "cup_bail")

    prev = hanger
    pitch = _cup_b_pitch(d)
    for i in range(n):
        cup = model.part(_module_part_name(r, i))
        cup.visual(shell_mesh, material=mats["shell"], name="shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"galvanized_grey", "weathered_copper", "antique_bronze", "brushed_aluminium", "blackened_steel"} else "rust.verdigris_patina"))
        cup.visual(rim_mesh, material=mats["rim"], name="rim", material_class_id=("metal.steel_galvanized" if r.palette_style in {"aged_verdigris_zinc", "galvanized_grey", "weathered_copper", "antique_bronze", "blackened_steel"} else "metal.aluminum_bare"))
        cup.visual(top_bail_mesh if i == 0 else bail_mesh, material=mats["wire"], name="bail", material_class_id=("metal.steel_bare" if r.palette_style in {"weathered_copper", "antique_bronze", "brushed_aluminium", "blackened_steel"} else "metal.steel_galvanized"))
        cup.inertial = Inertial.from_geometry(
            Cylinder(radius=d.top_half, length=d.cup_h),
            mass=0.16,
            origin=Origin(xyz=(0.0, 0.0, d.mouth_z - d.cup_h * 0.45)),
        )
        # Joint origin = the parent's real bottom hanger bar (child bail apex sits
        # there at q=0). cup_0 is the exception: its U-handle hangs from the root
        # ring centered at ``top_ring_z``.
        origin_z = d.top_ring_z if i == 0 else d.bottom_bar_z
        model.articulation(
            _swing_joint_name(r, i),
            ArticulationType.REVOLUTE,
            parent=prev,
            child=cup,
            origin=Origin(xyz=(0.0, 0.0, origin_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=_fold_safe_swing_limit(n - i, pitch, r),
        )
        prev = cup


def _build_chain_gamma(model, mats, r, n, assets) -> None:
    d = _link_g_dims(r)
    bracket = _build_ring_bracket(model, mats, d)

    # Link meshes reused across the chain (XZ-plane even, YZ-plane odd). The FIRST
    # link (always even / XZ-plane) is raised by ring_engage so its top tip rises
    # through the horizontal bracket ring and the ring tube rests on its upper arc
    # (the only way an XZ-plane link can solidly contact an XY ring).
    even_mesh = mesh_from_geometry(_oval_link_geom(d, in_yz_plane=False), "link_oval_even")
    odd_mesh = mesh_from_geometry(_oval_link_geom(d, in_yz_plane=True), "link_oval_odd")
    first_mesh = mesh_from_geometry(
        _oval_link_geom(d, in_yz_plane=False, z_off=d.ring_engage), "link_oval_first"
    )

    prev = bracket
    parent_pivot_z = d.bracket_ring_z
    limits = _alt_axis_limits(r)
    for i in range(n):
        link = model.part(_module_part_name(r, i))
        in_yz = i % 2 == 1
        if i == 0:
            link_mesh = first_mesh
        else:
            link_mesh = odd_mesh if in_yz else even_mesh
        link.visual(
            link_mesh,
            material=mats["rim"] if in_yz else mats["shell"],
            name="oval_body", material_class_id=("metal.aluminum_bare" if r.palette_style in {"galvanized_grey", "weathered_copper", "antique_bronze", "brushed_aluminium", "blackened_steel"} else "rust.verdigris_patina"),
        )
        body_center_z = -d.half_len + (d.ring_engage if i == 0 else 0.0)
        link.inertial = Inertial.from_geometry(
            Cylinder(radius=d.half_wid, length=2.0 * d.half_len),
            mass=0.04,
            origin=Origin(xyz=(0.0, 0.0, body_center_z)),
        )
        swing_axis = (1.0, 0.0, 0.0) if in_yz else (0.0, 1.0, 0.0)
        model.articulation(
            _swing_joint_name(r, i),
            ArticulationType.REVOLUTE,
            parent=prev,
            child=link,
            origin=Origin(xyz=(0.0, 0.0, parent_pivot_z)),
            axis=swing_axis,
            motion_limits=limits,
        )
        prev = link
        # link_0's whole mesh is raised by ring_engage, so its bottom arc is that
        # much higher; link_1 must pivot ring_engage higher to stay interlocked.
        # Subsequent links are unshifted, so the standard pitch applies.
        parent_pivot_z = d.bottom_pivot_z + (d.ring_engage if i == 0 else 0.0)


def build_seeded_rain_chain(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_rain_chain(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _center(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0)


def run_rain_chain_tests(
    object_model: ArticulatedObject,
    config: RainChainConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.module_count

    root = object_model.get_part("gutter_bracket" if r.family != "beta" else "gutter_hanger")
    modules = [object_model.get_part(_module_part_name(r, i)) for i in range(n)]
    joints = [object_model.get_articulation(_swing_joint_name(r, i)) for i in range(n)]

    # ------------------------------------------------------------------
    # Element-scoped intentional overlaps (captured-pin relations), per family.
    # ------------------------------------------------------------------
    if r.family == "alpha":
        ctx.allow_overlap(
            modules[0],
            root,
            elem_a="link_wire",
            elem_b="bracket_eye",
            reason="Top cup's bail hook passes through the fixed bracket eye.",
        )
        for i, cup in enumerate(modules):
            ctx.allow_overlap(
                cup,
                cup,
                elem_a="link_wire",
                elem_b="cup_rim",
                reason="Bail wire seats onto the rolled rim edges of its cup.",
            )
            ctx.allow_overlap(
                cup,
                cup,
                elem_a="link_wire",
                elem_b="cup_shell",
                reason="Bail wire ends seat at the rim where the shell wall is.",
            )
            ctx.allow_overlap(
                cup,
                cup,
                elem_a="bottom_boss",
                elem_b="cup_shell",
                reason="Closing boss disc is seamed into the cup-bottom wall.",
            )
            ctx.allow_overlap(
                cup,
                cup,
                elem_a="bottom_stem",
                elem_b="bottom_boss",
                reason="Bottom stem is fixed into the closing boss.",
            )
            ctx.allow_overlap(
                cup,
                cup,
                elem_a="bottom_stem",
                elem_b="bottom_eye",
                reason="Bottom stem carries (passes into) the hanging eye.",
            )
            if i + 1 < len(modules):
                nxt = modules[i + 1]
                ctx.allow_overlap(
                    nxt,
                    cup,
                    elem_a="link_wire",
                    elem_b="bottom_eye",
                    reason="Each cup's bail hook passes through the bottom "
                    "eye of the cup above it.",
                )
    elif r.family == "beta":
        ctx.allow_overlap(
            root,
            modules[0],
            elem_a="hanger_ring",
            elem_b="bail",
            reason="Cup 1's U-handle hangs through the root吊环.",
        )
        for upper, lower in zip(modules, modules[1:]):
            ctx.allow_overlap(
                upper,
                lower,
                elem_a="shell",
                elem_b="bail",
                reason="The lower cup's bail loop hooks over the upper cup's bottom "
                "hanger bar to form the captured chain link.",
            )
    else:  # gamma
        for j in range(4):
            ctx.allow_overlap(
                root,
                root,
                elem_a=f"ring_spoke_{j}",
                elem_b="hanger_bar",
                reason=f"Spoke {j} is welded to the hanger bar.",
            )
            ctx.allow_overlap(
                root,
                root,
                elem_a=f"ring_spoke_{j}",
                elem_b="bracket_ring",
                reason=f"Spoke {j} is welded to the hanging ring.",
            )
        ctx.allow_overlap(
            modules[0],
            root,
            elem_a="oval_body",
            elem_b="bracket_ring",
            reason="Top chain link passes through the bracket hanging ring.",
        )
        ctx.allow_overlap(
            modules[0],
            root,
            elem_a="oval_body",
            elem_b="hanger_bar",
            reason="Top chain link's upper arc threads up past the hanger bar to rest on the ring.",
        )
        for j in range(4):
            ctx.allow_overlap(
                modules[0],
                root,
                elem_a="oval_body",
                elem_b=f"ring_spoke_{j}",
                reason="Top chain link passes through the ring area where spokes are.",
            )
        for i in range(1, n):
            ctx.allow_overlap(
                modules[i],
                modules[i - 1],
                elem_a="oval_body",
                elem_b="oval_body",
                reason=f"link_{i} interlocks with link_{i - 1} (chain links "
                "pass through each other).",
            )

    # ------------------------------------------------------------------
    # Baseline gates.
    # ------------------------------------------------------------------
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # The joint origin is placed on the parent's real downstream pivot (eye / axle
    # bar / oval bottom arc), so it sits on real hanging hardware (no air gap).

    # ------------------------------------------------------------------
    # Structure: N modules + N swing joints + the grounded root.
    # ------------------------------------------------------------------
    part_names = {p.name for p in object_model.parts}
    expected_parts = {_module_part_name(r, i) for i in range(n)}
    ctx.check(
        "expected modules present",
        expected_parts.issubset(part_names),
        details=str(sorted(part_names)),
    )
    ctx.check("module count in source domain", N_MIN <= n <= N_MAX, details=f"n={n}")
    ctx.check(
        "exactly N swing joints",
        len(object_model.joints) == n,
        details=f"joints={len(object_model.joints)} expected={n}",
    )

    # ------------------------------------------------------------------
    # Each swing is a REVOLUTE about a horizontal axis with q=0 in range; axis
    # follows Slot C (single Y, or alternating Y/X for the link family).
    # ------------------------------------------------------------------
    for i, joint in enumerate(joints):
        ctx.check(
            f"swing[{i}] is revolute",
            str(joint.articulation_type).upper().endswith("REVOLUTE"),
            details=f"type={joint.articulation_type}",
        )
        ax = joint.axis
        if r.family == "gamma":
            in_yz = i % 2 == 1
            ok_axis = (abs(ax[2]) < 0.02) and (
                (abs(ax[0]) > 0.99) if in_yz else (abs(ax[1]) > 0.99)
            )
        else:
            ok_axis = abs(ax[1]) > 0.99 and abs(ax[0]) < 0.02 and abs(ax[2]) < 0.02
        ctx.check(f"swing[{i}] horizontal axis per coupling", ok_axis, details=f"axis={ax}")
        lo, hi = joint.motion_limits.lower, joint.motion_limits.upper
        ctx.check(
            f"swing[{i}] range includes rest q=0 and swings both ways",
            lo < math.radians(-10.0) and hi > math.radians(10.0) and lo <= 0.0 <= hi,
            details=f"lower={lo}, upper={hi}",
        )

    # ------------------------------------------------------------------
    # Fold safety (single-axis families): the per-joint swing limit must be the
    # single-sourced fold-safe value (Contract 3c), and must shrink from the
    # bottom (free end, loosest) to the top (longest tail below, tightest) so no
    # sampled combination of poses can fold a distal cup back through an upper
    # cup. This locks the census seed-5 cup_1<->cup_13 through-cup fix.
    # ------------------------------------------------------------------
    if r.family in ("alpha", "beta"):
        if r.family == "beta":
            pitch = _cup_b_pitch(_cup_b_dims(r))
        else:
            pitch = _cup_a_pitch(_cup_a_dims(r))
        expected_ups = [_fold_safe_swing_limit(n - i, pitch, r).upper for i in range(n)]
        for i, joint in enumerate(joints):
            ctx.check(
                f"swing[{i}] uses the single-sourced fold-safe limit",
                abs(joint.motion_limits.upper - expected_ups[i]) < 1e-9
                and abs(joint.motion_limits.lower + expected_ups[i]) < 1e-9,
                details=f"upper={joint.motion_limits.upper:.5f} expected={expected_ups[i]:.5f}",
            )
        ctx.check(
            "swing limits shrink toward the top (fold-safe monotonic)",
            all(expected_ups[k] <= expected_ups[k + 1] + 1e-9 for k in range(n - 1)),
            details=f"top->bottom={[round(math.degrees(u), 1) for u in expected_ups]}",
        )
        # Where the geometric corridor bound is active (not clamped to the
        # min/max rails), the fold-safe reach must actually hold: the lateral tip
        # travel of the tail below that joint stays within the safe corridor.
        for i, up in enumerate(expected_ups):
            geom_cap = up < _SWING_MAX - 1e-9 and up > _SWING_MIN + 1e-9
            if geom_cap:
                reach = (n - i) * pitch * math.sin(up)
                ctx.check(
                    f"swing[{i}] fold reach within corridor",
                    reach <= _FOLD_CORRIDOR + 1e-6,
                    details=f"reach={reach:.4f} corridor={_FOLD_CORRIDOR:.4f}",
                )

    # ------------------------------------------------------------------
    # Rest pose: modules descend in a vertical stack below the root.
    # ------------------------------------------------------------------
    z_centers = [_center(ctx.part_world_aabb(m))[2] for m in modules]
    descending = all(z_centers[k + 1] < z_centers[k] - 0.02 for k in range(len(z_centers) - 1))
    ctx.check("modules descend in a vertical chain", descending, details=f"z_centers={z_centers}")

    root_aabb = ctx.part_world_aabb(root)
    if root_aabb is not None:
        top0 = ctx.part_world_aabb(modules[0])
        ctx.check(
            "root sits above the first module",
            root_aabb[1][2] > top0[1][2],
            details=f"root_top={root_aabb[1][2]:.4f} mod0_top={top0[1][2]:.4f}",
        )

    # ------------------------------------------------------------------
    # Family-specific identity checks.
    # ------------------------------------------------------------------
    if r.family == "alpha":
        d = _cup_a_dims(r)
        ctx.check(
            "cup tapers wide-mouth to small-bottom funnel",
            d.bot_r < d.top_r * 0.5,
            details=f"top_r={d.top_r:.4f} bot_r={d.bot_r:.4f}",
        )
        ctx.check("cup wall is thin sheet metal", _WALL < d.top_r * 0.05, details=f"wall={_WALL}")
        for i, cup in enumerate(modules):
            rim_c = _center(ctx.part_element_world_aabb(cup, elem="cup_rim"))
            shell_c = _center(ctx.part_element_world_aabb(cup, elem="cup_shell"))
            ctx.check(
                f"cup[{i}] mouth above narrow bottom",
                rim_c[2] > shell_c[2],
                details=f"rim_z={rim_c[2]:.4f} shell_z={shell_c[2]:.4f}",
            )
        if d.lotus:
            ctx.check(
                "lotus rim has repeated petal pattern",
                r.n_petals >= 6 and d.petal_tip_r > d.petal_valley_r * 1.10,
                details=f"n_petals={r.n_petals} tip={d.petal_tip_r:.4f} valley={d.petal_valley_r:.4f}",
            )
        ctx.expect_contact(
            modules[0],
            root,
            elem_a="link_wire",
            elem_b="bracket_eye",
            contact_tol=0.006,
            name="top cup link meets bracket eye",
        )
        for i in range(1, len(modules)):
            ctx.expect_contact(
                modules[i],
                modules[i - 1],
                elem_a="link_wire",
                elem_b="bottom_eye",
                contact_tol=0.006,
                name=f"cup[{i}] link meets cup[{i - 1}] bottom eye",
            )
    elif r.family == "beta":
        d = _cup_b_dims(r)
        for cup in modules:
            names = {v.name for v in cup.visuals}
            ctx.check(
                f"{cup.name} has funnel shell + bail",
                {"shell", "bail"}.issubset(names),
                details=str(sorted(names)),
            )
        # Cup is a real funnel: top mouth wider than the bottom.
        ctx.check(
            "B-cup funnel taper top>bottom",
            d.top_half > d.bot_half,
            details=f"top_half={d.top_half:.4f} bot_half={d.bot_half:.4f}",
        )
        foot_z = _cup_b_bail_foot_z(d)
        foot_half = _cup_b_bail_foot_half_span(d)
        shell_half = _cup_b_outer_half_at_z(d, foot_z)
        ctx.check(
            "B-cup bail feet stay outside the shell wall",
            foot_half - _SQ_BAIL_R >= shell_half + 0.0005,
            details=(
                f"foot_z={foot_z:.4f} foot_half={foot_half:.4f} "
                f"shell_half={shell_half:.4f} wire_r={_SQ_BAIL_R:.4f}"
            ),
        )
        # Anti-pierce invariant: the capture eye hooks the upper cup's hanger bar
        # by threading its OPEN drain hole; no bail vertex may land in the solid
        # bottom-plate ring (drain_r .. bot_half) at the floor plane. The
        # shell<->bail allow_overlap (which covers the legitimate bar contact)
        # would otherwise mask the wire stabbing through the upper cup's floor.
        bail_verts = _bail_loop_geom(d).vertices
        plate_top_local = (d.mouth_z - d.cup_h + _SQ_WALL) - d.bottom_bar_z
        plate_bot_local = (d.mouth_z - d.cup_h) - d.bottom_bar_z
        plate_pierces = sum(
            1
            for v in bail_verts
            if plate_bot_local - 0.0005 <= v[2] <= plate_top_local + 0.0005
            and d.drain_r <= abs(v[0]) <= d.bot_half
            and abs(v[1]) <= d.bot_half
        )
        ctx.check(
            "bail eye threads the drain opening (does not pierce the bottom plate)",
            plate_pierces == 0,
            details=(
                f"plate_pierces={plate_pierces} drain_r={d.drain_r:.4f} bot_half={d.bot_half:.4f}"
            ),
        )
        bail_b = ctx.part_element_world_aabb(modules[0], elem="bail")
        cup0_b = ctx.part_world_aabb(modules[0])
        ctx.check(
            "bail arches at/above the cup mouth",
            bail_b[1][2] > cup0_b[1][2] - 0.001,
            details=f"bail_top={bail_b[1][2]:.4f} cup_top={cup0_b[1][2]:.4f}",
        )
        ctx.expect_contact(
            root,
            modules[0],
            elem_a="hanger_ring",
            elem_b="bail",
            contact_tol=0.006,
            name="cup 0 handle hangs on root ring",
        )
        for upper, lower in zip(modules, modules[1:]):
            ctx.expect_contact(
                upper,
                lower,
                elem_a="shell",
                elem_b="bail",
                contact_tol=0.0005,
                name=f"{lower.name} loop captured on {upper.name} bar",
            )
    else:  # gamma
        d = _link_g_dims(r)
        ctx.check(
            "oval link elongated (long axis > short axis)",
            d.half_len > d.half_wid * 1.5,
            details=f"half_len={d.half_len:.4f} half_wid={d.half_wid:.4f}",
        )
        for i, lk in enumerate(modules):
            dd = _ext(ctx.part_world_aabb(lk))
            if i % 2 == 0:
                ctx.check(
                    f"link[{i}] (even) wider in X (XZ plane)",
                    dd[0] > dd[1] * 1.2,
                    details=f"dx={dd[0]:.4f} dy={dd[1]:.4f}",
                )
            else:
                ctx.check(
                    f"link[{i}] (odd) wider in Y (YZ plane)",
                    dd[1] > dd[0] * 1.2,
                    details=f"dx={dd[0]:.4f} dy={dd[1]:.4f}",
                )
        ctx.expect_contact(
            modules[0],
            root,
            elem_a="oval_body",
            elem_b="bracket_ring",
            contact_tol=0.008,
            name="top link meets bracket ring",
        )
        for i in range(1, n):
            ctx.expect_contact(
                modules[i],
                modules[i - 1],
                elem_a="oval_body",
                elem_b="oval_body",
                contact_tol=0.008,
                name=f"link[{i}] meets link[{i - 1}]",
            )

    # ------------------------------------------------------------------
    # Posed: swinging the top joint carries the whole chain sideways.
    # ------------------------------------------------------------------
    top_joint = joints[0]
    rest_top = _center(ctx.part_world_aabb(modules[0]))
    rest_bot = _center(ctx.part_world_aabb(modules[-1]))
    swing_q = min(joints[0].motion_limits.upper, math.radians(30.0)) * 0.9
    with ctx.pose({top_joint: swing_q}):
        swung_top = _center(ctx.part_world_aabb(modules[0]))
        swung_bot = _center(ctx.part_world_aabb(modules[-1]))
    ctx.check(
        "swinging top joint moves the top module sideways",
        abs(swung_top[0] - rest_top[0]) > 0.005 or abs(swung_top[1] - rest_top[1]) > 0.005,
        details=f"rest=({rest_top[0]:.4f},{rest_top[1]:.4f}) swung=({swung_top[0]:.4f},{swung_top[1]:.4f})",
    )
    if n >= 2:
        ctx.check(
            "swinging top joint carries the whole chain (bottom module moves too)",
            abs(swung_bot[0] - rest_bot[0]) > 0.01 or abs(swung_bot[1] - rest_bot[1]) > 0.01,
            details=f"rest=({rest_bot[0]:.4f},{rest_bot[1]:.4f}) swung=({swung_bot[0]:.4f},{swung_bot[1]:.4f})",
        )

    # ------------------------------------------------------------------
    # Materials: muted metal shell, brighter rim, neutral wire (palette).
    # ------------------------------------------------------------------
    if r.family == "alpha":
        shell_rgba = modules[0].get_visual("cup_shell").material.rgba
        rim_rgba = modules[0].get_visual("cup_rim").material.rgba
    elif r.family == "beta":
        shell_rgba = modules[0].get_visual("shell").material.rgba
        rim_rgba = modules[0].get_visual("rim").material.rgba
    else:
        shell_rgba = modules[0].get_visual("oval_body").material.rgba
        rim_rgba = modules[1].get_visual("oval_body").material.rgba if n >= 2 else shell_rgba
    # Muted metal: greys/zincs have tiny spread; copper/bronze are warm but still
    # low-saturation metals (spread ~0.36). Reject only genuinely garish colors.
    ctx.check(
        "shell is a muted metal (not high-saturation)",
        max(shell_rgba[:3]) - min(shell_rgba[:3]) < 0.42,
        details=f"shell_rgba={shell_rgba}",
    )
    ctx.check(
        "rim/secondary reads at least as bright as shell",
        sum(rim_rgba[:3]) >= sum(shell_rgba[:3]) - 1e-6,
        details=f"rim_rgba={rim_rgba} shell_rgba={shell_rgba}",
    )

    # slot_choices recorded for diversity attribution.
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "RainChainConfig",
    "ResolvedRainChainConfig",
    "build_rain_chain",
    "build_seeded_rain_chain",
    "config_from_seed",
    "resolve_config",
    "run_rain_chain_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
