# SPDX-License-Identifier: Apache-2.0

"""Kitchen knife block set modular template.

NOTE on the slug: ``knife_set`` here = a **kitchen knife BLOCK set** (one holder
``knife_block`` root that carries N kitchen knives + a pair of kitchen shears),
NOT a single chef's knife (blade + handle alone), NOT a folding / retractable
utility knife, NOT a generic utensil crock / cutlery caddy, and NOT a magnetic
wall knife bar. Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Kitchen_Knife_set.md`` and the
``picture/Kitchen/Knife set`` 5-star pool (1 parent + 7 slot / multiplicity fork
variants), all synced under ``data/records/``.

Structure (pattern = ``multiplicity``; the knife count is the dominant
multiplicity axis): a single root part holds the holder body + decorative logo;
N knives + a 2-part shears parent directly to it as parallel children:

  * N ``knife_{i}`` parts (PRISMATIC slide-out -- the **multiplicity main axis**,
    N in [3, 8]; emitted via ``for i in range(N)`` + a shared knife helper).
  * ``shears_inner_half`` (PRISMATIC slide) + ``shears_outer_half`` (REVOLUTE
    pivot on the inner half's central rivet) -- always present, the second
    non-fixed-joint anchor (kept on every candidate, never multiplicity).

Slot A (``block_form``) chooses the holder shell geometry + slot axis:
  * ``slanted_block``  -- back-leaning 12-deg oak wedge; knives draw along the
    tilted slot axis (slide rpy = (0, -TILT, 0)); two rows.
  * ``upright_block``  -- vertical axis-aligned box; knives draw straight up
    (slide rpy = (0,0,0), no tilt); shears slide out a horizontal front slot
    (slide axis = (1,0,0), pivot axis = (0,0,1)); two rows.
  * ``horizontal_bar`` -- long low countertop bar; knives lie at a shallow
    15-deg angle in a single row (slide rpy = (JOINT_ROLL=75deg, 0, 0)).

Slot B (``holding_mechanism``) chooses how the knives are held:
  * ``angled_prismatic_slots`` -- solid holder milled with one slot per knife;
    **all N knives are independent PRISMATIC slides** (the multiplicity carrier).
  * ``bristle_insert``         -- hollow smoked-acrylic housing + dense bristle
    rod grid; **only 1 chef knife is an independent PRISMATIC part**, the other
    N-1 are FIXED inline housing visuals (Rule 1: loose bristles cannot each
    anchor a prismatic child). N still encoded into slot_choices.

Slot C (``base_stand``) chooses what the holder sits on:
  * ``rubber_feet``          -- four inline foot visuals on the holder (Rule 1);
    the holder body is the root, sits on the ground.
  * ``sculptural_pedestal``  -- a turned bronze ``pedestal`` column root; the
    holder is FIXED-mounted on top (``pedestal_to_block`` FIXED, z=0.130).
  * ``cast_metal_stand``     -- a heavy cast ``cast_metal_stand`` cradle root;
    the holder is FIXED-seated in it (``stand_to_block`` FIXED, z=0.012); the
    holder's rubber feet seat on the stand plate (expect_contact).

All knife-in-slot / shears-in-pocket / shears pivot-pin / base FIXED fits are
captured geometry, so those joints omit ``MatingContract`` (grandfathered) and
are guarded by the flat 0.015 m articulation-origin baseline plus element-scoped
``allow_isolated_part`` / ``allow_overlap`` / ``expect_contact`` (mirroring each
source's run_tests block).

PERFORMANCE: each knife mesh is a light blade+grip lathe/loft; slot cuts are kept
to one coarse milling pass per holder (the solid blocks) rather than per-knife
boolean cuts after the fact, and tessellation is left at the SDK default. N is
capped at 8.
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

BlockForm = Literal["slanted_block", "upright_block", "horizontal_bar"]
HoldingMechanism = Literal["angled_prismatic_slots", "bristle_insert"]
BaseStand = Literal["rubber_feet", "sculptural_pedestal", "cast_metal_stand"]
PaletteStyle = Literal[
    "natural_oak_walnut",
    "dark_acrylic_steel",
    "bamboo_blond",
    "brushed_steel_black",
    "bronze_pedestal_oak",
]

BLOCK_FORMS: tuple[BlockForm, ...] = (
    "slanted_block",
    "upright_block",
    "horizontal_bar",
)
HOLDING_MECHANISMS: tuple[HoldingMechanism, ...] = (
    "angled_prismatic_slots",
    "bristle_insert",
)
BASE_STANDS: tuple[BaseStand, ...] = (
    "rubber_feet",
    "sculptural_pedestal",
    "cast_metal_stand",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "natural_oak_walnut",
    "dark_acrylic_steel",
    "bamboo_blond",
    "brushed_steel_black",
    "bronze_pedestal_oak",
)

# knife_count multiplicity domain (spec section 8). Weighted small: N=4/5/6
# high, 3/7 common, 8 long tail.
N_KNIFE_MIN, N_KNIFE_MAX = 3, 8
_KNIFE_COUNT_CHOICES = (3, 4, 5, 6, 7, 8)
_KNIFE_COUNT_WEIGHTS = (0.14, 0.22, 0.22, 0.20, 0.13, 0.09)

# ---------------------------------------------------------------------------
# Shared knife geometry constants (all forms share the blade / grip lathe).
# ---------------------------------------------------------------------------
GRIP_Z0 = 0.031  # handle base in the knife-local frame
RIVET_FRACS = (0.30, 0.70)

# Shears (always present; the 2nd non-fixed-joint anchor).
SHEARS_TRAVEL = 0.10
SHEARS_OPEN = 0.70  # rad (~40 deg)
PIVOT_Z = 0.006

# slanted_block geometry (from the parent + count_8 sources).
TILT_DEG_BASE = 12.0
LIFT = 0.008
SL_FRONT_BOTTOM = (0.062, 0.0)
SL_BACK_BOTTOM = (-0.058, 0.0)
SL_POCKET_GAP = 0.020
SL_PANEL_THICK = 0.010
SL_PANEL_LEN = 0.150
SL_SHEARS_PLANE_OFF = 0.010
SL_SLOT_THICK = 0.0066

# upright_block geometry.
UP_BLOCK_D = 0.120  # X (depth)
UP_BLOCK_H = 0.240  # Z (height)
UP_SLOT_THICK = 0.013
UP_SLOT_EXTRA = 0.005
UP_SHEARS_W = 0.060
UP_SHEARS_H = 0.016
UP_SHEARS_D = 0.105

# horizontal_bar geometry.
HB_SLOT_ANGLE_DEG = 15.0
HB_LIFT = 0.005
HB_BASE_DEPTH = 0.22
HB_BASE_HB = 0.065  # height at back
HB_BASE_HF = 0.040  # height at front
HB_SLOT_MOUTH_Y = -0.07
HB_SLOT_THICK = 0.014
HB_SLOT_ABOVE = 0.030
HB_SHEARS_SLOT_W = 0.022

# bristle_insert geometry.
BR_HW = 0.140  # housing width (Y)
BR_HD = 0.100  # housing depth (X)
BR_HH = 0.220  # housing height (Z)
BR_WT = 0.004
BR_FT = 0.006
BR_R = 0.0015
BR_SP = 0.013
BR_PK_W = 0.110
BR_PK_D = 0.025
BR_PK_H = 0.140
BR_VIS_ZOFF = -0.023
CHEF_TRAVEL = 0.20

# sculptural_pedestal geometry.
PEDESTAL_TOP = 0.130

# cast_metal_stand geometry.
STAND_PLATE_TOP = 0.012

# ---------------------------------------------------------------------------
# Palettes (5 colorways from the 8 source records, spec section 7).
# Keys: block (holder shell), logo, grip (handle), steel (blade), accent
# (feet / bristle / base), base (pedestal / stand metal).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "natural_oak_walnut": {
        "block": (0.80, 0.64, 0.42, 1.0),
        "logo": (0.42, 0.28, 0.15, 1.0),
        "grip": (0.32, 0.19, 0.11, 1.0),
        "steel": (0.78, 0.79, 0.82, 1.0),
        "accent": (0.08, 0.08, 0.08, 1.0),
        "base": (0.28, 0.24, 0.19, 1.0),
    },
    "dark_acrylic_steel": {
        "block": (0.30, 0.33, 0.38, 0.75),
        "logo": (0.18, 0.20, 0.22, 1.0),
        "grip": (0.32, 0.19, 0.11, 1.0),
        "steel": (0.80, 0.81, 0.84, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
        "base": (0.22, 0.22, 0.24, 1.0),
    },
    "bamboo_blond": {
        "block": (0.85, 0.74, 0.52, 1.0),
        "logo": (0.40, 0.30, 0.16, 1.0),
        "grip": (0.70, 0.56, 0.36, 1.0),
        "steel": (0.78, 0.79, 0.82, 1.0),
        "accent": (0.08, 0.08, 0.08, 1.0),
        "base": (0.30, 0.26, 0.20, 1.0),
    },
    "brushed_steel_black": {
        "block": (0.66, 0.67, 0.70, 1.0),
        "logo": (0.20, 0.21, 0.23, 1.0),
        "grip": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.80, 0.81, 0.84, 1.0),
        "accent": (0.08, 0.08, 0.09, 1.0),
        "base": (0.24, 0.24, 0.26, 1.0),
    },
    "bronze_pedestal_oak": {
        "block": (0.80, 0.64, 0.42, 1.0),
        "logo": (0.42, 0.28, 0.15, 1.0),
        "grip": (0.32, 0.19, 0.11, 1.0),
        "steel": (0.78, 0.79, 0.82, 1.0),
        "accent": (0.08, 0.08, 0.08, 1.0),
        "base": (0.28, 0.24, 0.19, 1.0),
    },
}

# Bristle-insert mechanism overrides the holder shell material to a translucent
# acrylic when the chosen palette is wood-toned, so the housing still reads as a
# hollow acrylic crock.
_ACRYLIC_BLOCK = (0.30, 0.33, 0.38, 0.75)


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class KnifeSetConfig:
    block_form: BlockForm | None = None
    holding_mechanism: HoldingMechanism | None = None
    base_stand: BaseStand | None = None
    knife_count: int | None = None
    palette_style: PaletteStyle = "natural_oak_walnut"
    block_width_scale: float = 1.0
    block_depth_scale: float = 1.0
    block_height_scale: float = 1.0
    knife_travel_scale: float = 1.0
    shears_open_scale: float = 1.0
    tilt_angle_scale: float = 1.0
    name: str = "knife_set"


@dataclass(frozen=True)
class ResolvedKnifeSetConfig:
    block_form: BlockForm
    holding_mechanism: HoldingMechanism
    base_stand: BaseStand
    knife_count: int
    palette_style: PaletteStyle
    block_width_scale: float
    block_depth_scale: float
    block_height_scale: float
    knife_travel_scale: float
    shears_open_scale: float
    tilt_rad: float  # resolved lean-back angle (slanted only)
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> KnifeSetConfig:
    rng = random.Random(seed)
    block_form = rng.choice(BLOCK_FORMS)
    holding_mechanism = rng.choice(HOLDING_MECHANISMS)
    base_stand = rng.choice(BASE_STANDS)
    knife_count = rng.choices(_KNIFE_COUNT_CHOICES, weights=_KNIFE_COUNT_WEIGHTS, k=1)[0]
    return KnifeSetConfig(
        block_form=block_form,
        holding_mechanism=holding_mechanism,
        base_stand=base_stand,
        knife_count=knife_count,
        palette_style=rng.choice(PALETTE_STYLES),
        block_width_scale=round(rng.uniform(0.90, 1.18), 4),
        block_depth_scale=round(rng.uniform(0.90, 1.12), 4),
        block_height_scale=round(rng.uniform(0.90, 1.12), 4),
        knife_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        shears_open_scale=round(rng.uniform(0.85, 1.10), 4),
        tilt_angle_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_knife_set_{seed}",
    )


def resolve_config(config: KnifeSetConfig | None = None) -> ResolvedKnifeSetConfig:
    cfg = config or KnifeSetConfig()
    block_form = _pick(cfg.block_form, BLOCK_FORMS)
    holding_mechanism = _pick(cfg.holding_mechanism, HOLDING_MECHANISMS)
    base_stand = _pick(cfg.base_stand, BASE_STANDS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Compatibility (spec section 9): the long low horizontal_bar is a
    # countertop holder that rests directly on the counter -- it does not nest
    # in the compact cast cradle nor perch on the turned pedestal column (both
    # are sized for the small slanted/upright block). Resolve its base to
    # rubber_feet so the holder always sits flat on the ground.
    if block_form == "horizontal_bar":
        base_stand = "rubber_feet"

    knife_count = int(cfg.knife_count) if cfg.knife_count is not None else 6
    knife_count = int(_clamp(knife_count, N_KNIFE_MIN, N_KNIFE_MAX))

    tilt_scale = _clamp(cfg.tilt_angle_scale, 0.85, 1.15)
    tilt_deg = _clamp(TILT_DEG_BASE * tilt_scale, 8.0, 16.0)

    return ResolvedKnifeSetConfig(
        block_form=block_form,
        holding_mechanism=holding_mechanism,
        base_stand=base_stand,
        knife_count=knife_count,
        palette_style=palette_style,
        block_width_scale=_clamp(cfg.block_width_scale, 0.90, 1.18),
        block_depth_scale=_clamp(cfg.block_depth_scale, 0.90, 1.12),
        block_height_scale=_clamp(cfg.block_height_scale, 0.90, 1.12),
        knife_travel_scale=_clamp(cfg.knife_travel_scale, 0.85, 1.10),
        shears_open_scale=_clamp(cfg.shears_open_scale, 0.85, 1.10),
        tilt_rad=math.radians(tilt_deg),
        name=cfg.name or "knife_set",
    )


def with_overrides(config: KnifeSetConfig, **kwargs: object) -> KnifeSetConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: KnifeSetConfig | ResolvedKnifeSetConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedKnifeSetConfig) else resolve_config(config)
    return (
        ("block_form", r.block_form),
        ("holding_mechanism", r.holding_mechanism),
        ("base_stand", r.base_stand),
        ("knife_count", f"n{r.knife_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Per-knife specs (blade graded chef -> paring), derived for any N in [3, 8].
# ===========================================================================
# Full 8-knife graded set (chef largest -> bird's beak smallest), the count_8
# ordering. For N < 8 we take the first N entries (largest knives), so the set
# always reads chef-down. Each spec: (blade_len, blade_w, travel, grip_len, slot_w).
_KNIFE_LADDER = (
    (0.175, 0.040, 0.18, 0.110, 0.048),  # 0 chef
    (0.160, 0.034, 0.16, 0.105, 0.042),  # 1 carving
    (0.155, 0.028, 0.16, 0.105, 0.046),  # 2 bread
    (0.145, 0.040, 0.15, 0.105, 0.048),  # 3 santoku
    (0.125, 0.024, 0.13, 0.090, 0.034),  # 4 utility
    (0.110, 0.022, 0.12, 0.088, 0.032),  # 5 fillet
    (0.092, 0.020, 0.10, 0.085, 0.032),  # 6 paring
    (0.080, 0.018, 0.10, 0.082, 0.030),  # 7 bird's beak
)


def _knife_specs(n: int, travel_scale: float) -> list[dict]:
    specs: list[dict] = []
    for i in range(n):
        blade_len, blade_w, travel, grip_len, slot_w = _KNIFE_LADDER[i]
        # Travel may not exceed the blade length (blade must clear the slot but
        # not derail), spec section 7 inequality #3.
        eff_travel = min(travel * travel_scale, 0.95 * blade_len)
        specs.append(
            dict(
                blade_len=blade_len,
                blade_w=blade_w,
                travel=eff_travel,
                grip_len=grip_len,
                slot_w=slot_w,
            )
        )
    return specs


def _row_split(n: int) -> tuple[int, int]:
    """Back-row / front-row knife counts for two-row forms (slanted/upright).

    Larger knives in the back row. N<=3 collapses to a single back row; bigger
    N is split with the back row holding the (slightly larger) half.
    """
    if n <= 3:
        return n, 0
    back = (n + 1) // 2
    return back, n - back


def _row_ys(count: int, span: float) -> list[float]:
    """Even, symmetric Y positions for `count` slots across width `span`."""
    if count <= 0:
        return []
    if count == 1:
        return [0.0]
    step = span / (count - 1)
    return [-span / 2.0 + i * step for i in range(count)]


# ===========================================================================
# Shared knife / shears lathe geometry (identical across all 8 sources).
# ===========================================================================
def _grip_loft(sections: list[tuple[float, float, float, float, float]]) -> cq.Workplane:
    """Loft elliptical cross-sections stacked along +Z: (z, x, y, rx, ry)."""
    z0, x0, y0, a0, b0 = sections[0]
    wp = cq.Workplane("XY").workplane(offset=z0).center(x0, y0).ellipse(a0, b0)
    pz, px, py = z0, x0, y0
    for z, x, y, a, b in sections[1:]:
        wp = wp.workplane(offset=z - pz).center(x - px, y - py).ellipse(a, b)
        pz, px, py = z, x, y
    return wp.loft(combine=True)


def _knife_steel(blade_len: float, blade_w: float) -> cq.Workplane:
    """Tapered blade (down -Z) plus a bolster block, in the knife-local frame."""
    half = blade_w / 2.0
    pts = [
        (-half, 0.015),
        (half, 0.015),
        (half, -0.45 * blade_len),
        (-half + 0.003, -blade_len),
    ]
    blade = cq.Workplane("XZ").polyline(pts).close().extrude(0.00125, both=True)
    bolster = cq.Workplane("XY").box(0.013, 0.011, 0.020).translate((0, 0, 0.023))
    return blade.union(bolster)


def _knife_grip(grip_len: float) -> cq.Workplane:
    """Curved walnut handle, sweeping back (-X) as it rises along +Z."""
    return _grip_loft(
        [
            (GRIP_Z0, 0.000, 0.0, 0.0110, 0.0085),
            (GRIP_Z0 + 0.35 * grip_len, -0.004, 0.0, 0.0130, 0.0100),
            (GRIP_Z0 + 0.75 * grip_len, -0.010, 0.0, 0.0125, 0.0095),
            (GRIP_Z0 + grip_len, -0.016, 0.0, 0.0090, 0.0070),
        ]
    )


def _knife_rivet_x(grip_len: float, frac: float) -> float:
    """Interpolated handle-curve x offset for a rivet at frac of grip length."""
    stations = [(0.0, 0.0), (0.35, -0.004), (0.75, -0.010), (1.0, -0.016)]
    for (f0, x0), (f1, x1) in zip(stations, stations[1:]):
        if frac <= f1:
            t = (frac - f0) / (f1 - f0)
            return x0 + t * (x1 - x0)
    return stations[-1][1]


def _shears_steel(inner: bool) -> cq.Workplane:
    """One shears half: tang + tapered blade, flats stacked along x."""
    if inner:
        pts = [
            (-0.008, 0.016),
            (0.008, 0.016),
            (0.008, -0.025),
            (0.001, -0.094),
            (-0.004, -0.094),
            (-0.008, -0.025),
        ]
        xoff = -0.00225
    else:
        pts = [
            (-0.008, 0.010),
            (0.008, 0.010),
            (0.008, -0.031),
            (0.001, -0.100),
            (-0.004, -0.100),
            (-0.008, -0.031),
        ]
        xoff = 0.00225
    half = (
        cq.Workplane("YZ")
        .polyline(pts)
        .close()
        .extrude(0.00175, both=True)
        .translate((xoff, 0.0, 0.0))
    )
    if not inner:
        hole = cq.Workplane("YZ").circle(0.0045).extrude(0.02, both=True)
        half = half.cut(hole)
    return half


def _shears_grip(inner: bool) -> cq.Workplane:
    if inner:
        sections = [
            (0.012, -0.00425, 0.0050, 0.00375, 0.0060),
            (0.040, -0.00425, 0.0145, 0.00375, 0.0070),
            (0.070, -0.00425, 0.0235, 0.00375, 0.0070),
            (0.092, -0.00425, 0.0190, 0.00350, 0.0055),
        ]
    else:
        sections = [
            (0.006, 0.00425, -0.0050, 0.00375, 0.0060),
            (0.034, 0.00425, -0.0145, 0.00375, 0.0070),
            (0.064, 0.00425, -0.0235, 0.00375, 0.0070),
            (0.086, 0.00425, -0.0190, 0.00350, 0.0055),
        ]
    return _grip_loft(sections)


def _knife_inertial() -> Inertial:
    return Inertial.from_geometry(
        Box((0.045, 0.020, 0.220)),
        mass=0.12,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )


def _emit_knife_visuals(knife, spec: dict, mats, *, assets, zoff: float = 0.0) -> None:
    """Blade + grip + 2 rivets for one knife, in the knife-local frame."""
    knife.visual(
        mesh_from_cadquery(_knife_steel(spec["blade_len"], spec["blade_w"]), "knife_steel", assets=assets),
        material=mats["steel"],
        name="knife_steel", material_class_id="metal.stainless_matte",
        origin=Origin(xyz=(0.0, 0.0, zoff)),
    )
    knife.visual(
        mesh_from_cadquery(_knife_grip(spec["grip_len"]), "knife_grip", assets=assets),
        material=mats["grip"],
        name="knife_grip", material_class_id="wood.walnut_dark",
        origin=Origin(xyz=(0.0, 0.0, zoff)),
    )
    for j, frac in enumerate(RIVET_FRACS):
        knife.visual(
            Cylinder(radius=0.0032, length=0.022),
            origin=Origin(
                xyz=(_knife_rivet_x(spec["grip_len"], frac), 0.0, zoff + GRIP_Z0 + frac * spec["grip_len"]),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["steel"],
            name=f"knife_rivet_{j}", material_class_id="metal.stainless_matte",
        )


def _emit_shears_parts(model, mats, *, assets, horizontal: bool = False):
    """Create the two shears parts (inner + outer) with all visuals. Returns
    (inner, outer). Joints are emitted by the caller (per block_form).

    ``horizontal=True`` rotates the blade halves 90 deg about +Y so the blades
    lie along -X (used by upright_block, whose shears slide along +X out of a
    horizontal front slot).
    """
    steel = _shears_steel_h if horizontal else _shears_steel
    grip = _shears_grip_h if horizontal else _shears_grip
    inner = model.part("shears_inner_half")
    inner.visual(
        mesh_from_cadquery(steel(inner=True), "shears_inner_steel", assets=assets),
        material=mats["steel"],
        name="shears_inner_steel", material_class_id="metal.stainless_matte",
    )
    inner.visual(
        mesh_from_cadquery(grip(inner=True), "shears_inner_grip", assets=assets),
        material=mats["grip"],
        name="shears_inner_grip", material_class_id="wood.walnut_dark",
    )
    # Pivot rivet: vertical frame has it along +X through the pivot at z=PIVOT_Z;
    # the horizontal (upright) frame rotates the half 90 deg about +Y, mapping
    # (x,y,z) -> (z,y,-x), so the pivot moves to (PIVOT_Z, 0, 0) along +Z.
    if horizontal:
        pivot_xyz = (PIVOT_Z, 0.0, 0.0)
        pivot_rpy = (0.0, 0.0, 0.0)
    else:
        pivot_xyz = (0.0, 0.0, PIVOT_Z)
        pivot_rpy = (0.0, math.pi / 2.0, 0.0)
    inner.visual(
        Cylinder(radius=0.0035, length=0.013),
        origin=Origin(xyz=pivot_xyz, rpy=pivot_rpy),
        material=mats["steel"],
        name="shears_pivot_rivet", material_class_id="metal.stainless_matte",
    )
    # Decorative grip rivet heads poke through the narrow grip in the vertical
    # frame. The horizontal (upright) half rotates the grip onto its own length
    # axis, where the small rivet heads can no longer be cleanly seated on the
    # rotated lofted surface, so they are omitted for that orientation (the
    # pivot rivet -- the load-bearing one -- is always present).
    inner_rivets = () if horizontal else ((0.030, 0.011), (0.065, 0.022))
    for j, (rz, ry) in enumerate(inner_rivets):
        inner.visual(
            Cylinder(radius=0.0022, length=0.0085),
            origin=Origin(xyz=(-0.00425, ry, rz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name=f"shears_inner_rivet_{j}", material_class_id="metal.stainless_matte",
        )
    inner.inertial = Inertial.from_geometry(
        Box((0.020, 0.030, 0.110)), mass=0.06, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )

    outer = model.part("shears_outer_half")
    outer.visual(
        mesh_from_cadquery(steel(inner=False), "shears_outer_steel", assets=assets),
        material=mats["steel"],
        name="shears_outer_steel", material_class_id="metal.stainless_matte",
    )
    outer.visual(
        mesh_from_cadquery(grip(inner=False), "shears_outer_grip", assets=assets),
        material=mats["grip"],
        name="shears_outer_grip", material_class_id="wood.walnut_dark",
    )
    outer_rivets = () if horizontal else ((0.024, -0.011), (0.059, -0.022))
    for j, (rz, ry) in enumerate(outer_rivets):
        outer.visual(
            Cylinder(radius=0.0022, length=0.0085),
            origin=Origin(xyz=(0.00425, ry, rz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name=f"shears_outer_rivet_{j}", material_class_id="metal.stainless_matte",
        )
    outer.inertial = Inertial.from_geometry(
        Box((0.020, 0.030, 0.110)), mass=0.05, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    return inner, outer


# ===========================================================================
# Slot A: block_form -- holder shell geometry + slot layout descriptor.
# ===========================================================================
@dataclass(frozen=True)
class _SlotLayout:
    """Per-knife (and per-shears) slot placement for the chosen block_form."""

    knife_origins: list[tuple[float, float, float]]
    knife_rpy: tuple[float, float, float]
    knife_axis: tuple[float, float, float]
    knife_visual_zoff: float
    shears_origin: tuple[float, float, float]
    shears_rpy: tuple[float, float, float]
    shears_axis: tuple[float, float, float]
    shears_pivot_axis: tuple[float, float, float]
    block_top_z: float  # world z of the slot mouth row (for stow checks)


# ---- slanted_block -------------------------------------------------------
def _slanted_dims(r: ResolvedKnifeSetConfig) -> dict:
    s = math.sin(r.tilt_rad)
    c = math.cos(r.tilt_rad)
    tan = math.tan(r.tilt_rad)
    back, front = _row_split(r.knife_count)
    per_row = max(back, front, 1)
    # Width must hold per_row knives without colliding (section 7 inequality #1).
    max_slot_w = max(sp["slot_w"] for sp in _knife_specs(r.knife_count, r.knife_travel_scale))
    needed = per_row * (max_slot_w + 0.014) + 0.018
    width = max(0.130 * r.block_width_scale, needed)
    height_top = 0.205 * r.block_height_scale
    return dict(s=s, c=c, tan=tan, back=back, front=front, width=width, height_top=height_top)


def _slanted_geom(r: ResolvedKnifeSetConfig, d: dict):
    s, c, tan = d["s"], d["c"], d["tan"]
    width = d["width"]
    deg = math.degrees(r.tilt_rad)
    fb = SL_FRONT_BOTTOM
    bb = SL_BACK_BOTTOM
    front_top = (fb[0] - d["height_top"] * tan, d["height_top"])
    back_top = (bb[0] - (d["height_top"] + 0.030) * tan, d["height_top"] + 0.030)

    def top_point(frac: float) -> tuple[float, float]:
        return (
            front_top[0] + frac * (back_top[0] - front_top[0]),
            front_top[1] + frac * (back_top[1] - front_top[1]),
        )

    def face_pt(length: float, off: float, y: float = 0.0):
        return (fb[0] - length * s + off * c, y, length * c + off * s)

    def tilted_box(sx, sy, sz, center):
        return (
            cq.Workplane("XY").box(sx, sy, sz).rotate((0, 0, 0), (0, 1, 0), -deg).translate(center)
        )

    return front_top, back_top, top_point, face_pt, tilted_box


def _build_slanted_solid(r: ResolvedKnifeSetConfig, specs, d: dict) -> cq.Workplane:
    front_top, back_top, top_point, face_pt, tilted_box = _slanted_geom(r, d)
    width = d["width"]
    prof = [SL_FRONT_BOTTOM, front_top, back_top, SL_BACK_BOTTOM]
    body = cq.Workplane("XZ").polyline(prof).close().extrude(width / 2.0, both=True)

    panel = tilted_box(
        SL_PANEL_THICK,
        width,
        SL_PANEL_LEN,
        face_pt(SL_PANEL_LEN / 2.0, SL_POCKET_GAP + SL_PANEL_THICK / 2.0),
    )
    cheek_off = width / 2.0 - 0.006
    cheek_a = tilted_box(0.028, 0.012, SL_PANEL_LEN, face_pt(SL_PANEL_LEN / 2.0, 0.010, -cheek_off))
    cheek_b = tilted_box(0.028, 0.012, SL_PANEL_LEN, face_pt(SL_PANEL_LEN / 2.0, 0.010, cheek_off))
    floor = tilted_box(0.028, width - 0.012, 0.018, face_pt(0.013, 0.010))
    block = body.union(panel).union(cheek_a).union(cheek_b).union(floor)

    back_m = top_point(0.70)
    front_m = top_point(0.26)
    s = d["s"]
    c = d["c"]
    for spec, (mx, mz, y) in zip(specs, _slanted_slot_xyz(r, specs, d)):
        depth = spec["blade_len"] + 0.020
        clen = depth + 0.050
        coff = (0.050 - depth) / 2.0
        center = (mx - coff * s, y, mz + coff * c)
        block = block.cut(tilted_box(spec["slot_w"], SL_SLOT_THICK, clen, center))
    _ = (back_m, front_m)
    return block


def _slanted_slot_xyz(r: ResolvedKnifeSetConfig, specs, d: dict):
    """Per-knife (mx, mz, y) slot mouth tuples in the block frame (pre-LIFT)."""
    front_top, back_top, top_point, _face, _tb = _slanted_geom(r, d)
    back_m = top_point(0.70)
    front_m = top_point(0.26)
    back, front = d["back"], d["front"]
    width = d["width"]
    y_span = width - 0.030
    back_ys = _row_ys(back, y_span)
    front_ys = _row_ys(front, y_span)
    out: list[tuple[float, float, float]] = []
    for i in range(len(specs)):
        if i < back:
            out.append((back_m[0], back_m[1], back_ys[i]))
        else:
            out.append((front_m[0], front_m[1], front_ys[i - back]))
    return out


def _layout_slanted(r: ResolvedKnifeSetConfig, specs) -> _SlotLayout:
    d = _slanted_dims(r)
    s, c = d["s"], d["c"]
    knife_origins = [(mx, y, mz + LIFT) for (mx, mz, y) in _slanted_slot_xyz(r, specs, d)]
    _ft, _bt, _tp, face_pt, _tb = _slanted_geom(r, d)
    mouth = face_pt(SL_PANEL_LEN, SL_SHEARS_PLANE_OFF)
    block_top = max(mz for (_x, mz, _y) in _slanted_slot_xyz(r, specs, d)) + LIFT
    _ = (s, c)
    return _SlotLayout(
        knife_origins=knife_origins,
        knife_rpy=(0.0, -r.tilt_rad, 0.0),
        knife_axis=(0.0, 0.0, 1.0),
        knife_visual_zoff=0.0,
        shears_origin=(mouth[0], 0.0, mouth[2] + LIFT),
        shears_rpy=(0.0, -r.tilt_rad, 0.0),
        shears_axis=(0.0, 0.0, 1.0),
        shears_pivot_axis=(1.0, 0.0, 0.0),
        block_top_z=block_top,
    )


# ---- upright_block -------------------------------------------------------
def _upright_dims(r: ResolvedKnifeSetConfig) -> dict:
    back, front = _row_split(r.knife_count)
    per_row = max(back, front, 1)
    max_slot_w = max(sp["slot_w"] for sp in _knife_specs(r.knife_count, r.knife_travel_scale))
    needed = per_row * (max_slot_w + 0.012) + 0.018
    width = max(0.130 * r.block_width_scale, needed)
    depth = UP_BLOCK_D * r.block_depth_scale
    height = UP_BLOCK_H * r.block_height_scale
    return dict(back=back, front=front, width=width, depth=depth, height=height)


def _upright_slot_xy(r: ResolvedKnifeSetConfig, d: dict) -> list[tuple[float, float]]:
    back, front = d["back"], d["front"]
    depth = d["depth"]
    width = d["width"]
    back_x = -depth * 0.17
    front_x = depth * 0.17
    y_span = width - 0.030
    back_ys = _row_ys(back, y_span)
    front_ys = _row_ys(front, y_span)
    out: list[tuple[float, float]] = []
    for i in range(r.knife_count):
        if i < back:
            out.append((back_x, back_ys[i]))
        else:
            out.append((front_x, front_ys[i - back]))
    return out


def _build_upright_solid(r: ResolvedKnifeSetConfig, specs, d: dict) -> cq.Workplane:
    depth = d["depth"]
    width = d["width"]
    height = d["height"]
    top_z = LIFT + height
    body = cq.Workplane("XY").box(depth, width, height).translate((0.0, 0.0, LIFT + height / 2.0))
    for spec, (kx, ky) in zip(specs, _upright_slot_xy(r, d)):
        slot_depth = spec["blade_len"] + 0.020
        slot = cq.Workplane("XY").box(spec["slot_w"], UP_SLOT_THICK, slot_depth + UP_SLOT_EXTRA).translate(
            (kx, ky, top_z - slot_depth / 2.0 + UP_SLOT_EXTRA / 2.0)
        )
        body = body.cut(slot)
    # Horizontal shears slot in the front (+X) face.
    front_x = depth / 2.0
    shears_slot_z = LIFT + 0.080
    sslot = cq.Workplane("XY").box(UP_SHEARS_D, UP_SHEARS_W, UP_SHEARS_H).translate(
        (front_x - UP_SHEARS_D / 2.0 + 0.001, 0.0, shears_slot_z)
    )
    body = body.cut(sslot)
    return body


def _shears_steel_h(inner: bool) -> cq.Workplane:
    return _shears_steel(inner).rotate((0, 0, 0), (0, 1, 0), 90)


def _shears_grip_h(inner: bool) -> cq.Workplane:
    return _shears_grip(inner).rotate((0, 0, 0), (0, 1, 0), 90)


def _layout_upright(r: ResolvedKnifeSetConfig, specs) -> _SlotLayout:
    d = _upright_dims(r)
    top_z = LIFT + d["height"]
    knife_origins = [(kx, ky, top_z) for (kx, ky) in _upright_slot_xy(r, d)]
    front_x = d["depth"] / 2.0
    shears_slot_z = LIFT + 0.080
    return _SlotLayout(
        knife_origins=knife_origins,
        knife_rpy=(0.0, 0.0, 0.0),
        knife_axis=(0.0, 0.0, 1.0),
        knife_visual_zoff=0.0,
        shears_origin=(front_x, 0.0, shears_slot_z),
        shears_rpy=(0.0, 0.0, 0.0),
        shears_axis=(1.0, 0.0, 0.0),
        shears_pivot_axis=(0.0, 0.0, 1.0),
        block_top_z=top_z,
    )


# ---- horizontal_bar ------------------------------------------------------
def _hb_dims(r: ResolvedKnifeSetConfig) -> dict:
    n = r.knife_count
    spacing = 0.058
    # The single knife row spans [-(n-1)*spacing/2, +(n-1)*spacing/2]; the shears
    # sits beyond the last knife with a clear margin, so the bar must be long
    # enough to hold the row + the shears pocket + end margins.
    row_half = (n - 1) * spacing / 2.0
    shears_clear = 0.075  # gap from last knife center to the shears center
    needed_half = row_half + shears_clear + 0.045
    base_len = max(0.46 * r.block_width_scale, 2.0 * needed_half)
    depth = HB_BASE_DEPTH * r.block_depth_scale
    hb = HB_BASE_HB * r.block_height_scale
    hf = HB_BASE_HF * r.block_height_scale
    half_l = base_len / 2.0
    shears_x = row_half + shears_clear
    return dict(
        spacing=spacing,
        base_len=base_len,
        depth=depth,
        hb=hb,
        hf=hf,
        half_l=half_l,
        half_d=depth / 2.0,
        shears_x=shears_x,
    )


def _hb_z_top(d: dict, y: float) -> float:
    t = (y + d["half_d"]) / d["depth"]
    return d["hb"] + (d["hf"] - d["hb"]) * t


def _knife_x_hb(r: ResolvedKnifeSetConfig, d: dict, i: int) -> float:
    n = r.knife_count
    return -(n - 1) * d["spacing"] / 2.0 + i * d["spacing"]


def _build_hb_solid(r: ResolvedKnifeSetConfig, specs, d: dict) -> cq.Workplane:
    slot_angle = math.radians(HB_SLOT_ANGLE_DEG)
    ca = math.cos(slot_angle)
    sa = math.sin(slot_angle)
    slot_cut_deg = -(90.0 + HB_SLOT_ANGLE_DEG)
    half_d = d["half_d"]
    half_l = d["half_l"]
    prof = [(-half_d, 0.0), (-half_d, d["hb"]), (half_d, d["hf"]), (half_d, 0.0)]
    body = cq.Workplane("YZ").polyline(prof).close().extrude(half_l, both=True)

    mouth_z = _hb_z_top(d, HB_SLOT_MOUTH_Y)

    def slot_cutter(x_center: float, width: float, blade_depth: float) -> cq.Workplane:
        total = blade_depth + HB_SLOT_ABOVE
        offset = (blade_depth - HB_SLOT_ABOVE) / 2.0
        cy = HB_SLOT_MOUTH_Y + offset * ca
        cz = mouth_z - offset * sa
        return (
            cq.Workplane("XY")
            .box(width, HB_SLOT_THICK, total)
            .rotate((0, 0, 0), (1, 0, 0), slot_cut_deg)
            .translate((x_center, cy, cz))
        )

    for i, spec in enumerate(specs):
        body = body.cut(slot_cutter(_knife_x_hb(r, d, i), spec["slot_w"], spec["blade_len"] + 0.005))
    body = body.cut(slot_cutter(d["shears_x"], HB_SHEARS_SLOT_W, 0.105))
    return body


def _layout_hb(r: ResolvedKnifeSetConfig, specs) -> _SlotLayout:
    d = _hb_dims(r)
    joint_roll = math.radians(90.0 - HB_SLOT_ANGLE_DEG)
    mzw = _hb_z_top(d, HB_SLOT_MOUTH_Y) + HB_LIFT
    knife_origins = [(_knife_x_hb(r, d, i), HB_SLOT_MOUTH_Y, mzw) for i in range(r.knife_count)]
    shears_x = d["shears_x"]
    return _SlotLayout(
        knife_origins=knife_origins,
        knife_rpy=(joint_roll, 0.0, 0.0),
        knife_axis=(0.0, 0.0, 1.0),
        knife_visual_zoff=0.0,
        shears_origin=(shears_x, HB_SLOT_MOUTH_Y, mzw),
        shears_rpy=(joint_roll, 0.0, 0.0),
        shears_axis=(0.0, 0.0, 1.0),
        shears_pivot_axis=(1.0, 0.0, 0.0),
        block_top_z=mzw,
    )


# ===========================================================================
# Bristle-insert housing geometry.
# ===========================================================================
def _br_dims(r: ResolvedKnifeSetConfig) -> dict:
    width = max(BR_HW * r.block_width_scale, 0.110)
    depth = BR_HD * r.block_depth_scale
    height = BR_HH * r.block_height_scale
    return dict(width=width, depth=depth, height=height)


def _build_housing(d: dict) -> cq.Workplane:
    width, depth, height = d["width"], d["depth"], d["height"]
    outer = cq.Workplane("XY").box(depth, width, height).translate((0, 0, height / 2.0))
    cav_h = height - BR_FT
    inner = cq.Workplane("XY").box(depth - 2 * BR_WT, width - 2 * BR_WT, cav_h).translate(
        (0, 0, BR_FT + cav_h / 2.0)
    )
    housing = outer.cut(inner)
    pk_x = depth / 2.0 + BR_PK_D / 2.0
    pk_outer = cq.Workplane("XY").box(BR_PK_D, BR_PK_W, BR_PK_H).translate((pk_x, 0, BR_PK_H / 2.0))
    pk_inner_h = BR_PK_H - BR_WT
    pk_inner = cq.Workplane("XY").box(BR_PK_D - 2 * BR_WT, BR_PK_W - 2 * BR_WT, pk_inner_h).translate(
        (pk_x, 0, BR_WT + pk_inner_h / 2.0)
    )
    return housing.union(pk_outer.cut(pk_inner))


# ===========================================================================
# Base / stand geometry.
# ===========================================================================
def _build_pedestal() -> cq.Workplane:
    pts = [
        (0.000, 0.000),
        (0.100, 0.000),
        (0.100, 0.016),
        (0.094, 0.020),
        (0.072, 0.026),
        (0.054, 0.032),
        (0.046, 0.038),
    ]
    col_z0, col_z1 = 0.040, 0.110
    col_r0, col_r1 = 0.044, 0.036
    n_col = 8
    for i in range(n_col + 1):
        t = i / n_col
        z = col_z0 + t * (col_z1 - col_z0)
        bulge = 0.005 * math.sin(t * math.pi)
        r = col_r0 + t * (col_r1 - col_r0) + bulge
        pts.append((round(r, 4), round(z, 4)))
    pts += [
        (0.033, 0.113),
        (0.038, 0.116),
        (0.052, 0.119),
        (0.074, 0.122),
        (0.082, 0.124),
        (0.082, PEDESTAL_TOP),
        (0.000, PEDESTAL_TOP),
    ]
    return cq.Workplane("XZ").polyline(pts).close().revolve(360, (0, 0), (0, 1))


def _build_stand(r: ResolvedKnifeSetConfig) -> cq.Workplane:
    deg = math.degrees(r.tilt_rad)
    tan = math.tan(r.tilt_rad)

    def tilted_box(sx, sy, sz, center):
        return cq.Workplane("XY").box(sx, sy, sz).rotate((0, 0, 0), (0, 1, 0), -deg).translate(center)

    plate_d, plate_w, plate_h = 0.155, 0.168, 0.012
    base = cq.Workplane("XY").rect(plate_d, plate_w).extrude(plate_h)
    try:
        base = base.edges("|Z").fillet(0.006)
    except Exception:
        pass

    wf_x, wb_x = 0.068, -0.068
    wf_h = 0.055
    wb_h = wf_h + (wf_x - wb_x) * tan
    side_prof = [(wf_x, plate_h), (wf_x, plate_h + wf_h), (wb_x, plate_h + wb_h), (wb_x, plate_h)]
    wall_t = 0.010
    wall_y = 0.073 + wall_t / 2.0
    left = cq.Workplane("XZ").polyline(side_prof).close().extrude(wall_t / 2.0, both=True).translate((0, -wall_y, 0))
    right = cq.Workplane("XZ").polyline(side_prof).close().extrude(wall_t / 2.0, both=True).translate((0, wall_y, 0))

    bw_h, bw_w, bw_t = 0.120, 0.134, 0.008
    bw_cz = plate_h + bw_h / 2.0 - 0.003
    bw_cx = -0.058 - (bw_h / 2.0) * tan - 0.006
    back = tilted_box(bw_t, bw_w, bw_h, (bw_cx, 0, bw_cz))

    stand = base.union(left).union(right).union(back)
    gusset_h, gusset_t, gusset_d = 0.020, 0.004, 0.016
    for y_sign in (-1.0, 1.0):
        for x_off in (-0.040, 0.040):
            g = cq.Workplane("XY").box(gusset_d, gusset_t, gusset_h).translate(
                (x_off, y_sign * wall_y, plate_h + gusset_h / 2.0 - 0.002)
            )
            stand = stand.union(g)
    return stand


# ===========================================================================
# Holder body builder (chooses block_form x holding_mechanism) -> block part.
# ===========================================================================
def _foot_positions(r: ResolvedKnifeSetConfig) -> list[tuple[float, float]]:
    # The feet must sit under the actual holder shell. When the holding
    # mechanism is bristle_insert the shell is the acrylic housing (regardless
    # of block_form), so place the feet under the housing footprint.
    if r.holding_mechanism == "bristle_insert":
        d = _br_dims(r)
        fx = d["depth"] / 2.0 - 0.022
        fy = d["width"] / 2.0 - 0.022
        return [(fx, -fy), (fx, fy), (-fx, -fy), (-fx, fy)]
    if r.block_form == "horizontal_bar":
        d = _hb_dims(r)
        fx = d["half_l"] - 0.04
        fy = d["half_d"] - 0.03
        return [(-fx, -fy), (-fx, fy), (fx, -fy), (fx, fy)]
    if r.block_form == "upright_block":
        d = _upright_dims(r)
    else:
        d = _slanted_dims(r)
    fx = 0.045
    fy = d["width"] / 2.0 - 0.022
    # When the holder is FIXED-mounted on a base, the feet must land on the
    # base's support surface, not hang off it: the turned pedestal capital is
    # ~0.082 m radius and the cast stand plate is ~0.155 x 0.168 m, both sized
    # for the compact baseline block. Pull the feet inward to fit.
    if r.base_stand == "sculptural_pedestal":
        # Keep each foot center within ~0.060 m of the column axis.
        max_fy = math.sqrt(max(0.060**2 - fx**2, 0.030**2))
        fy = min(fy, max_fy)
    elif r.base_stand == "cast_metal_stand":
        fy = min(fy, 0.070)  # within the 0.168 m-wide plate (half 0.084)
        fx = min(fx, 0.065)  # within the 0.155 m-deep plate (half 0.0775)
    return [(fx, -fy), (fx, fy), (-fx, -fy), (-fx, fy)]


def _block_lift(r: ResolvedKnifeSetConfig) -> float:
    return HB_LIFT if r.block_form == "horizontal_bar" else LIFT


def _build_block_part(model, r: ResolvedKnifeSetConfig, specs, mats, *, assets):
    """Create the holder body part (named ``knife_block``) with its shell +
    feet + logo. Returns (block_part, layout)."""
    block = model.part("knife_block")
    lift = _block_lift(r)

    if r.holding_mechanism == "bristle_insert":
        d = _br_dims(r)
        block.visual(
            mesh_from_cadquery(_build_housing(d), "block_shell", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, LIFT)),
            material=mats["block_acrylic"],
            name="block_shell", material_class_id="plastic.frosted_translucent",
        )
        layout = None  # bristle handles knives internally; built below
    elif r.block_form == "slanted_block":
        d = _slanted_dims(r)
        block.visual(
            mesh_from_cadquery(_build_slanted_solid(r, specs, d), "block_shell", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, LIFT)),
            material=mats["block"],
            name="block_shell", material_class_id=("wood.oak" if r.palette_style in {"natural_oak_walnut", "dark_acrylic_steel", "bamboo_blond", "bronze_pedestal_oak"} else "metal.brushed_silver"),
        )
        layout = _layout_slanted(r, specs)
    elif r.block_form == "upright_block":
        d = _upright_dims(r)
        block.visual(
            mesh_from_cadquery(_build_upright_solid(r, specs, d), "block_shell", assets=assets),
            origin=Origin(),
            material=mats["block"],
            name="block_shell", material_class_id=("wood.oak" if r.palette_style in {"natural_oak_walnut", "dark_acrylic_steel", "bamboo_blond", "bronze_pedestal_oak"} else "metal.brushed_silver"),
        )
        layout = _layout_upright(r, specs)
    else:  # horizontal_bar
        d = _hb_dims(r)
        block.visual(
            mesh_from_cadquery(_build_hb_solid(r, specs, d), "block_shell", assets=assets),
            origin=Origin(xyz=(0.0, 0.0, HB_LIFT)),
            material=mats["block"],
            name="block_shell", material_class_id=("wood.oak" if r.palette_style in {"natural_oak_walnut", "dark_acrylic_steel", "bamboo_blond", "bronze_pedestal_oak"} else "metal.brushed_silver"),
        )
        layout = _layout_hb(r, specs)

    # Rubber feet (inline FIXED visuals on the holder, Rule 1).
    for i, (fx, fy) in enumerate(_foot_positions(r)):
        block.visual(
            Cylinder(radius=0.009, length=0.009),
            origin=Origin(xyz=(fx, fy, 0.0045)),
            material=mats["accent"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )

    # Engraved logo seal on the front-facing surface.
    _emit_logo(block, r, mats, lift)

    # Block inertial (roughly the holder body bounding box).
    if r.block_form == "horizontal_bar":
        hd = _hb_dims(r)
        block.inertial = Inertial.from_geometry(
            Box((hd["base_len"], hd["depth"], hd["hb"])),
            mass=2.2,
            origin=Origin(xyz=(0.0, 0.0, hd["hb"] / 2.0 + lift)),
        )
    else:
        if r.holding_mechanism == "bristle_insert":
            bd = _br_dims(r)
            bw, bdp, bh = bd["width"], bd["depth"], bd["height"]
        elif r.block_form == "upright_block":
            ud = _upright_dims(r)
            bw, bdp, bh = ud["width"], ud["depth"], ud["height"]
        else:
            sd = _slanted_dims(r)
            bw, bdp, bh = sd["width"], 0.120, 0.240
        block.inertial = Inertial.from_geometry(
            Box((bdp, bw, bh)),
            mass=2.8,
            origin=Origin(xyz=(0.0, 0.0, lift + bh / 2.0)),
        )
    return block, layout


def _emit_logo(block, r: ResolvedKnifeSetConfig, mats, lift: float) -> None:
    if r.holding_mechanism == "bristle_insert":
        d = _br_dims(r)
        logo_x = d["depth"] / 2.0 + 0.001
        logo_z = LIFT + d["height"] * 0.62
        block.visual(
            Box((0.002, 0.060, 0.040)),
            origin=Origin(xyz=(logo_x, 0.0, logo_z)),
            material=mats["logo"],
            name="logo_seal", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        return
    if r.block_form == "horizontal_bar":
        d = _hb_dims(r)
        front_y = d["half_d"] + 0.001
        logo_z = HB_LIFT + d["hf"] * 0.60
        block.visual(
            Box((0.090, 0.002, 0.018)),
            origin=Origin(xyz=(0.0, front_y, logo_z)),
            material=mats["logo"],
            name="logo_seal", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        return
    if r.block_form == "upright_block":
        d = _upright_dims(r)
        front_x = d["depth"] / 2.0 + 0.001
        logo_z = LIFT + 0.175
        block.visual(
            Box((0.002, 0.052, 0.052)),
            origin=Origin(xyz=(front_x, 0.0, logo_z)),
            material=mats["logo"],
            name="logo_seal", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        return
    # slanted_block: place on the front pocket panel face.
    d = _slanted_dims(r)
    _ft, _bt, _tp, face_pt, _tb = _slanted_geom(r, d)
    seal_c = face_pt(0.075, SL_POCKET_GAP + SL_PANEL_THICK)
    block.visual(
        Box((0.002, 0.052, 0.052)),
        origin=Origin(xyz=(seal_c[0], seal_c[1], seal_c[2] + LIFT), rpy=(0.0, -r.tilt_rad, 0.0)),
        material=mats["logo"],
        name="logo_seal", appearance_only=AppearanceOnlySpec(kind="decal"),
    )


# ===========================================================================
# Knife emission (multiplicity axis).
# ===========================================================================
def _emit_knives_prismatic(model, block, r, specs, layout, mats, *, assets) -> None:
    """angled_prismatic_slots: all N knives are independent PRISMATIC slides."""
    for i, spec in enumerate(specs):
        knife = model.part(f"knife_{i}")
        _emit_knife_visuals(knife, spec, mats, assets=assets, zoff=layout.knife_visual_zoff)
        knife.inertial = _knife_inertial()
        model.articulation(
            f"knife_{i}_slide",
            ArticulationType.PRISMATIC,
            parent=block,
            child=knife,
            origin=Origin(xyz=layout.knife_origins[i], rpy=layout.knife_rpy),
            axis=layout.knife_axis,
            motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=spec["travel"]),
        )


def _emit_knives_bristle(model, block, r, specs, mats, *, assets) -> None:
    """bristle_insert: 1 chef PRISMATIC part + (N-1) FIXED inline visuals +
    a dense bristle rod grid (all on the housing part)."""
    d = _br_dims(r)
    width, depth, height = d["width"], d["depth"], d["height"]
    cw = width - 2 * BR_WT
    cd = depth - 2 * BR_WT
    insert_z = LIFT + height
    br_h = height - BR_FT - 0.010

    # Bristle rod grid (inline visuals, Rule 1: no joints).
    n_bx = max(2, int(cd / BR_SP) - 1)
    n_by = max(2, int(cw / BR_SP) - 1)
    x_start = -cd / 2.0 + BR_SP
    y_start = -cw / 2.0 + BR_SP
    base_z = LIFT + BR_FT - 0.001
    for k in range(n_bx * n_by):
        ix = k // n_by
        iy = k % n_by
        bx = x_start + ix * BR_SP
        by = y_start + iy * BR_SP
        block.visual(
            Cylinder(radius=BR_R, length=br_h + 0.001),
            origin=Origin(xyz=(bx, by, base_z + (br_h + 0.001) / 2.0)),
            material=mats["accent"],
            name=f"bristle_{k}", material_class_id="plastic.opaque_generic",
        )

    n = r.knife_count
    grid = _bristle_grid_xy(n, depth, width)

    # The lone chef knife is the independent PRISMATIC part (knife_0), seated in
    # the first grid cell.
    chef_x, chef_y = grid[0]
    chef = model.part("knife_0")
    _emit_knife_visuals(chef, specs[0], mats, assets=assets, zoff=BR_VIS_ZOFF)
    chef.inertial = _knife_inertial()
    chef_travel = min(CHEF_TRAVEL * r.knife_travel_scale, 0.95 * specs[0]["blade_len"])
    model.articulation(
        "knife_0_slide",
        ArticulationType.PRISMATIC,
        parent=block,
        child=chef,
        origin=Origin(xyz=(chef_x, chef_y, insert_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=chef_travel),
    )

    # The remaining N-1 knives are FIXED inline housing visuals (Rule 1). Each
    # blade tip (local z = -blade_len) is dropped so it embeds a few mm into the
    # housing floor (top at LIFT + BR_FT): this gives every FIXED knife real
    # solid contact with block_shell, so it is not an isolated island, while the
    # handle still protrudes well above the housing rim.
    floor_top = LIFT + BR_FT
    for j in range(1, n):
        spec = specs[j]
        kx, ky = grid[j]
        zoff = floor_top - 0.003 + spec["blade_len"]
        block.visual(
            mesh_from_cadquery(_knife_steel(spec["blade_len"], spec["blade_w"]), f"fixed_knife_{j}_steel", assets=assets),
            origin=Origin(xyz=(kx, ky, zoff)),
            material=mats["steel"],
            name=f"fixed_knife_{j}_steel", material_class_id="metal.stainless_matte",
        )
        block.visual(
            mesh_from_cadquery(_knife_grip(spec["grip_len"]), f"fixed_knife_{j}_grip", assets=assets),
            origin=Origin(xyz=(kx, ky, zoff)),
            material=mats["grip"],
            name=f"fixed_knife_{j}_grip", material_class_id="wood.walnut_dark",
        )
        for ridx, frac in enumerate(RIVET_FRACS):
            block.visual(
                Cylinder(radius=0.0032, length=0.022),
                origin=Origin(
                    xyz=(kx + _knife_rivet_x(spec["grip_len"], frac), ky, zoff + GRIP_Z0 + frac * spec["grip_len"]),
                    rpy=(math.pi / 2.0, 0.0, 0.0),
                ),
                material=mats["steel"],
                name=f"fixed_knife_{j}_rivet_{ridx}", material_class_id="metal.stainless_matte",
            )


def _bristle_grid_xy(n: int, depth: float, width: float) -> list[tuple[float, float]]:
    """A 2-row insertion grid for all N knives in the bristle housing.

    Back row (-X) holds the larger knives, front row (+X) the smaller. Y is
    evenly spread per row with a minimum lateral pitch so the curved walnut
    grips never overlap. Index 0 (the lone chef) takes the first cell.
    """
    if n <= 0:
        return []
    back_x = -depth * 0.22
    front_x = depth * 0.22
    back = (n + 1) // 2
    front = n - back
    min_pitch = 0.032
    back_span = max(width - 0.044, min_pitch * max(back - 1, 1))
    front_span = max(width - 0.044, min_pitch * max(front - 1, 1))
    back_ys = _row_ys(back, back_span)
    front_ys = _row_ys(front, front_span)
    out: list[tuple[float, float]] = []
    for i in range(n):
        if i < back:
            out.append((back_x, back_ys[i]))
        else:
            out.append((front_x, front_ys[i - back]))
    return out


def _emit_shears(model, block, r, layout, mats, *, assets) -> tuple[object, object]:
    """Always-present 2-part shears: PRISMATIC slide + REVOLUTE pivot."""
    upright = r.block_form == "upright_block" and r.holding_mechanism != "bristle_insert"
    inner, outer = _emit_shears_parts(model, mats, assets=assets, horizontal=upright)

    if r.holding_mechanism == "bristle_insert":
        d = _br_dims(r)
        pk_x = d["depth"] / 2.0 + BR_PK_D / 2.0
        shears_origin = (pk_x, 0.0, LIFT + BR_PK_H)
        shears_rpy = (0.0, 0.0, 0.0)
        shears_axis = (0.0, 0.0, 1.0)
        pivot_axis = (1.0, 0.0, 0.0)
    else:
        shears_origin = layout.shears_origin
        shears_rpy = layout.shears_rpy
        shears_axis = layout.shears_axis
        pivot_axis = layout.shears_pivot_axis

    shears_open = min(SHEARS_OPEN * r.shears_open_scale, 0.95 * math.pi / 2.0)
    model.articulation(
        "shears_slide",
        ArticulationType.PRISMATIC,
        parent=block,
        child=inner,
        origin=Origin(xyz=shears_origin, rpy=shears_rpy),
        axis=shears_axis,
        motion_limits=MotionLimits(effort=15.0, velocity=0.5, lower=0.0, upper=SHEARS_TRAVEL),
    )
    model.articulation(
        "shears_pivot",
        ArticulationType.REVOLUTE,
        parent=inner,
        child=outer,
        origin=Origin(xyz=(0.0, 0.0, PIVOT_Z)),
        axis=pivot_axis,
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=shears_open),
    )
    return inner, outer


# ===========================================================================
# Build
# ===========================================================================
def build_knife_set(
    config: KnifeSetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = dict(PALETTES[r.palette_style])
    # bristle_insert always needs a translucent acrylic holder shell.
    block_acrylic = pal["block"] if len(pal["block"]) == 4 and pal["block"][3] < 1.0 else _ACRYLIC_BLOCK
    mats = {
        key: model.material(f"knife_set_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }
    mats["block_acrylic"] = model.material(f"knife_set_block_acrylic_{r.palette_style}", rgba=block_acrylic)

    specs = _knife_specs(r.knife_count, r.knife_travel_scale)

    # --- Base / stand root (Slot C) ---
    root = None
    base_lift = _block_lift(r)
    if r.base_stand == "sculptural_pedestal":
        root = model.part("pedestal")
        root.visual(
            mesh_from_cadquery(_build_pedestal(), "pedestal_column", assets=assets),
            material=mats["base"],
            name="pedestal_column", material_class_id="metal.bronze_cast",
        )
        pad_r = 0.078
        for i in range(4):
            ang = i * math.pi / 2.0
            root.visual(
                Cylinder(radius=0.010, length=0.003),
                origin=Origin(xyz=(pad_r * math.cos(ang), pad_r * math.sin(ang), -0.0015)),
                material=mats["accent"],
                name=f"base_pad_{i}", material_class_id="rubber.smooth_plain",
            )
        root.inertial = Inertial.from_geometry(
            Box((0.20, 0.20, PEDESTAL_TOP)),
            mass=4.0,
            origin=Origin(xyz=(0.0, 0.0, PEDESTAL_TOP / 2.0)),
        )
    elif r.base_stand == "cast_metal_stand":
        root = model.part("cast_metal_stand")
        root.visual(
            mesh_from_cadquery(_build_stand(r), "stand_frame", assets=assets),
            material=mats["base"],
            name="stand_frame", material_class_id="metal.cast_iron_bare",
        )
        root.visual(
            Box((0.010, 0.140, 0.006)),
            origin=Origin(xyz=(0.076, 0.0, 0.003)),
            material=mats["base"],
            name="stand_front_lip", material_class_id="metal.cast_iron_bare",
        )
        root.inertial = Inertial.from_geometry(
            Box((0.155, 0.168, 0.096)),
            mass=5.0,
            origin=Origin(xyz=(0.0, 0.0, 0.048)),
        )

    # --- Holder body (block_form x holding_mechanism) ---
    block, layout = _build_block_part(model, r, specs, mats, assets=assets)

    # --- Mount the block on the base (FIXED) or ground it ---
    if r.base_stand == "sculptural_pedestal":
        # Drop the mount 1 mm so the block feet (bottom at z=0 in the block
        # frame) embed into the pedestal capital top -- real seated contact, not
        # a sub-mm air gap that reads as an isolated part.
        model.articulation(
            "pedestal_to_block",
            ArticulationType.FIXED,
            parent=root,
            child=block,
            origin=Origin(xyz=(0.0, 0.0, PEDESTAL_TOP - 0.001)),
        )
    elif r.base_stand == "cast_metal_stand":
        model.articulation(
            "stand_to_block",
            ArticulationType.FIXED,
            parent=root,
            child=block,
            origin=Origin(xyz=(0.0, 0.0, STAND_PLATE_TOP - 0.001)),
        )
    _ = base_lift

    # --- Knives (multiplicity axis) ---
    if r.holding_mechanism == "bristle_insert":
        _emit_knives_bristle(model, block, r, specs, mats, assets=assets)
    else:
        _emit_knives_prismatic(model, block, r, specs, layout, mats, assets=assets)

    # --- Shears (always: PRISMATIC slide + REVOLUTE pivot) ---
    _emit_shears(model, block, r, layout, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_knife_set(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_knife_set(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_knife_set_tests(
    object_model: ArticulatedObject,
    config: KnifeSetConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    block = object_model.get_part("knife_block")
    inner = object_model.get_part("shears_inner_half")
    outer = object_model.get_part("shears_outer_half")
    slide = object_model.get_articulation("shears_slide")
    pivot = object_model.get_articulation("shears_pivot")
    n = r.knife_count

    # --- knife parts: count + each is an independent PRISMATIC slide (or the
    #     lone chef slide for bristle_insert). At least one non-fixed joint. ---
    if r.holding_mechanism == "bristle_insert":
        knife_parts = [object_model.get_part("knife_0")]
        knife_joints = [object_model.get_articulation("knife_0_slide")]
    else:
        knife_parts = [object_model.get_part(f"knife_{i}") for i in range(n)]
        knife_joints = [object_model.get_articulation(f"knife_{i}_slide") for i in range(n)]

    ctx.check(
        "at least one prismatic knife slide authored",
        len(knife_joints) >= 1,
        details=f"knife_joints={len(knife_joints)}, holding={r.holding_mechanism}",
    )
    for i, kj in enumerate(knife_joints):
        ctx.check(
            f"knife slide {i} is prismatic",
            str(kj.articulation_type).upper().endswith("PRISMATIC"),
            details=f"type={kj.articulation_type}",
        )
        lim = kj.motion_limits
        ctx.check(
            f"knife slide {i} has positive draw travel from 0",
            lim is not None and lim.lower is not None and lim.upper is not None
            and abs(lim.lower) < 1e-9 and lim.upper > 0.03,
            details=f"lower={None if lim is None else lim.lower}, upper={None if lim is None else lim.upper}",
        )

    # Each moving knife rests by gravity in a loose clearance-fit slot.
    for kp in knife_parts:
        ctx.allow_isolated_part(
            kp,
            reason=(
                "Knife rests by gravity in its holder slot; the slot is a loose "
                "clearance fit so the blade never touches the slot walls, and the "
                "prismatic joint provides the connection."
            ),
        )

    # horizontal_bar uses a solid-proxy sleeve (the milled slot is narrower than
    # the captured blade), so allow the blade/grip-in-shell overlap (source
    # rec_knife_set_var_block_horizontal_bar allows both steel and grip).
    if r.block_form == "horizontal_bar" and r.holding_mechanism != "bristle_insert":
        for i in range(n):
            kp = object_model.get_part(f"knife_{i}")
            ctx.allow_overlap(
                block,
                kp,
                elem_a="block_shell",
                elem_b="knife_steel",
                reason="Captured blade rides inside the milled bar slot (solid-proxy sleeve overlap).",
            )
            ctx.allow_overlap(
                block,
                kp,
                elem_a="block_shell",
                elem_b="knife_grip",
                reason="The bolster/grip junction seats at the slot mouth of the low bar (captured slide contact).",
            )

    # bristle_insert: the chef blade is intentionally inserted into the cavity.
    if r.holding_mechanism == "bristle_insert":
        ctx.allow_overlap(
            block,
            object_model.get_part("knife_0"),
            elem_a="block_shell",
            elem_b="knife_steel",
            reason="Chef blade is intentionally inserted into the bristle housing cavity.",
        )

    # --- holder body present + grounded (or elevated on a base). ---
    bb = ctx.part_world_aabb(block)
    ctx.check("holder body present with world AABB", bb is not None, details=f"block_aabb={bb}")

    if r.base_stand == "rubber_feet":
        ctx.check(
            "holder rests on its feet near the ground",
            bb is not None and abs(bb[0][2]) < 0.006,
            details=f"block_z_min={None if bb is None else bb[0][2]}",
        )
    elif r.base_stand == "sculptural_pedestal":
        pedestal = object_model.get_part("pedestal")
        mount = object_model.get_articulation("pedestal_to_block")
        ctx.check(
            "pedestal_to_block is FIXED",
            str(mount.articulation_type).upper().endswith("FIXED"),
            details=f"type={mount.articulation_type}",
        )
        ped_bb = ctx.part_world_aabb(pedestal)
        ctx.check(
            "pedestal is grounded at z~0",
            ped_bb is not None and abs(ped_bb[0][2]) < 0.006,
            details=f"ped_z_min={None if ped_bb is None else ped_bb[0][2]}",
        )
        ctx.check(
            "holder is elevated on the pedestal",
            bb is not None and bb[0][2] > 0.10,
            details=f"block_z_min={None if bb is None else bb[0][2]}",
        )
    else:  # cast_metal_stand
        stand = object_model.get_part("cast_metal_stand")
        mount = object_model.get_articulation("stand_to_block")
        ctx.check(
            "stand_to_block is FIXED",
            str(mount.articulation_type).upper().endswith("FIXED"),
            details=f"type={mount.articulation_type}",
        )
        sa = ctx.part_world_aabb(stand)
        ctx.check(
            "stand base sits on the counter at z~0",
            sa is not None and abs(sa[0][2]) < 0.006,
            details=f"stand_z_min={None if sa is None else sa[0][2]}",
        )
        # The holder feet seat on the cast stand plate (captured contact).
        for i in range(4):
            ctx.allow_overlap(
                stand,
                block,
                elem_a="stand_frame",
                elem_b=f"foot_{i}",
                reason=f"Rubber foot {i} seats on the cast-metal stand base plate; contact is intentional.",
            )
            ctx.expect_contact(
                stand,
                block,
                elem_a="stand_frame",
                elem_b=f"foot_{i}",
                name=f"foot_{i} contacts the stand base plate",
            )
        # The holder body nests down into the cast cradle: the block shell
        # intentionally overlaps the cradle walls/back support (captured fit).
        ctx.allow_overlap(
            stand,
            block,
            elem_a="stand_frame",
            elem_b="block_shell",
            reason="The holder body nests into the cast-metal cradle; the shell overlapping the cradle walls is the captured seat.",
        )

    # --- knife draws out along its slot axis (sample the chef knife). ---
    if knife_parts and bb is not None:
        kj0 = knife_joints[0]
        kp0 = knife_parts[0]
        travel = kj0.motion_limits.upper if kj0.motion_limits else 0.1
        with ctx.pose({kj0: 0.0}):
            rest = ctx.part_world_aabb(kp0)
        with ctx.pose({kj0: travel}):
            drawn = ctx.part_world_aabb(kp0)
        if rest is not None and drawn is not None:
            moved = math.sqrt(
                sum((0.5 * (drawn[0][k] + drawn[1][k]) - 0.5 * (rest[0][k] + rest[1][k])) ** 2 for k in range(3))
            )
            ctx.check(
                "drawing the chef knife translates it out of its slot",
                moved > 0.5 * travel,
                details=f"moved={moved:.4f}, travel={travel:.3f}",
            )

    # --- shears: slide (PRISMATIC) + pivot (REVOLUTE), the 2nd non-fixed anchor.
    ctx.allow_isolated_part(
        inner,
        reason="Shears inner half rests by gravity in the wide front pocket slot (loose clearance fit).",
    )
    ctx.allow_isolated_part(
        outer,
        reason="Outer shears half rides the pivot rivet through its clearance hole, gravity-seated in the pocket.",
    )
    if r.holding_mechanism == "bristle_insert":
        ctx.allow_overlap(
            block,
            inner,
            elem_a="block_shell",
            elem_b="shears_inner_steel",
            reason="Shears inner blade sits inside the front pocket cavity.",
        )
    elif r.block_form == "horizontal_bar":
        # The shears stow in a milled bar slot like the knives: the captured
        # blade rides the solid-proxy sleeve and the outer handle rests at the
        # slot mouth (source allows holder_shell vs inner_steel + outer_grip).
        ctx.allow_overlap(
            block,
            inner,
            elem_a="block_shell",
            elem_b="shears_inner_steel",
            reason="Captured shears inner blade rides inside the milled bar slot (solid-proxy sleeve).",
        )
        ctx.allow_overlap(
            block,
            outer,
            elem_a="block_shell",
            elem_b="shears_outer_grip",
            reason="The outer shears handle rests at the bar slot mouth when stowed.",
        )

    slim = slide.motion_limits
    ctx.check(
        "shears slide is prismatic with ~0.10 m travel",
        str(slide.articulation_type).upper().endswith("PRISMATIC")
        and slim is not None and slim.upper is not None and abs(slim.upper - SHEARS_TRAVEL) < 1e-6,
        details=f"limits=({None if slim is None else slim.lower}, {None if slim is None else slim.upper})",
    )
    plim = pivot.motion_limits
    ctx.check(
        "shears pivot is revolute opening 0..~40 deg",
        str(pivot.articulation_type).upper().endswith("REVOLUTE")
        and plim is not None and plim.lower is not None and plim.upper is not None
        and abs(plim.lower) < 1e-9 and 0.5 < plim.upper < math.pi / 2.0 + 0.01,
        details=f"limits=({None if plim is None else plim.lower}, {None if plim is None else plim.upper})",
    )

    # Sliding out then opening the pivot swings the outer handle (off-axis sweep).
    rest_handle = ctx.part_element_world_aabb(outer, elem="shears_outer_grip")
    with ctx.pose({slide: SHEARS_TRAVEL, pivot: min(0.6, plim.upper if plim else 0.6)}):
        open_handle = ctx.part_element_world_aabb(outer, elem="shears_outer_grip")
    if rest_handle is not None and open_handle is not None:
        rest_c = [0.5 * (rest_handle[0][k] + rest_handle[1][k]) for k in range(3)]
        open_c = [0.5 * (open_handle[0][k] + open_handle[1][k]) for k in range(3)]
        moved = math.sqrt(sum((open_c[k] - rest_c[k]) ** 2 for k in range(3)))
        ctx.check(
            "sliding out + opening the pivot moves the outer shears handle",
            moved > 0.01,
            details=f"moved={moved:.4f}",
        )

    return ctx.report()
