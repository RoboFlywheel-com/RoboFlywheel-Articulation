# SPDX-License-Identifier: Apache-2.0

"""Container lipstick — modular procedural template (twist-up lipstick / lip-gloss tube).

Category identity: a slim upright hollow tube (ROOT ``tube_base``) seated on z=0
with its axis along +Z, height >> 2.5 * width. A dispense / applicator mechanism
rides inside the bore (the category-identity action) and a cap opens/closes on top
(the cap action). No multiplicity axis — one tube, one dispense mechanism, one cap.

OPEN-MOUTH INVARIANT (hard rule): the tube's TOP opening is never sealed by
internal geometry. The seated product / carrier cup / gloss stays below the rim so
the mouth is an open aperture and the product reads as the lipstick visible down in
the cavity — never a disc plugging the top. The bullet product is widened to fill
the bore and seated just below the rim (visible), not retracted out of sight. This
is enforced by the "tube mouth is open" / "seated product fills the bore" checks in
``run_container_lipstick_tests`` (sweep-gated). A cap covering the mouth when CLOSED
is fine — that is the cap, not an internal plug.

Three parallel slots (spec ``specs_modular_v1/Container_Lipstick.md``):

  * ``body_form`` (4) — the ROOT ``tube_base`` mesh cross-section family:
      - round_cylinder: circle.extrude hollow open-top tube (parent A).
      - octagon_faceted: 8-gon polyline.extrude faceted prism (parent B).
      - square_rounded: rect.fillet("|Z") squircle prism (var square_rounded).
      - tapered_waisted: SDK LatheGeometry hourglass profile (var tapered_waisted).
  * ``dispense_mech`` (3) — the in-bore mechanism (>=1 non-fixed joint each):
      - twist_up_bullet: massless ``bullet_carrier`` CONTINUOUS +Z twist DECOUPLES
        ``bullet`` PRISMATIC +Z rise (parent A — 2 joints, massless carrier link).
      - doe_foot_applicator: one rigid ``cap_applicator`` (cap shell + wand stem +
        doe-foot tip) on a single PRISMATIC +Z pull. This part IS the cap, so the
        cap_closure slot is MERGED into it (parent B — compat rule).
      - push_up_swivel_pot: single ``slider`` PRISMATIC +Z, external thumb tab
        through a vertical wall slot, no rotating carrier (var push_up_swivel_pot).
  * ``cap_closure`` (3, suppressed when dispense=doe_foot) — the cap mechanism.
    Every cap opens by lifting straight UP except the flip cap (which swings), and
    every cap shell follows the body cross-section so it just covers the tube (no
    round-cap-over-facets 穿模):
      - friction_pull_off: single PRISMATIC +Z lift-off cap (parent A).
      - screw_thread_twist_off: PRISMATIC +Z lift-off twist cap (opens upward) with
        visible internal/external helical thread ridges + a narrow round threaded
        neck (var screw_thread_twist_off).
      - hinged_flip_cap: REVOLUTE +X flip cap hinged on a rear-rim lug (var
        hinged_flip_cap).

Continuous size / proportion variation (tube height/radius, cap radius=equation,
cap height, dispense travel) lives in ``resolve_config`` as clamped params, never
as slot candidates. ``palette_style`` is a pure palette axis (10 colorways + a
finish dimension) and is NOT a slot choice.

Sources (5-star pool, this repo ``data/records``): parent A
``rec_lipstick-...d2d2bc8b`` (round body + twist-up + pull-off), parent B
``rec_lip-gloss-...86a4438e`` (octagon body + doe-foot merged cap + gloss), plus
forks ``rec_container_lipstick_var_square_rounded`` / ``_tapered_waisted`` /
``_push_up_swivel_pot`` / ``_screw_thread_twist_off`` / ``_hinged_flip_cap``.
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
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "round_cylinder",
    "octagon_faceted",
    "square_rounded",
    "tapered_waisted",
]
DispenseMech = Literal[
    "twist_up_bullet",
    "doe_foot_applicator",
    "push_up_swivel_pot",
]
CapClosure = Literal[
    "friction_pull_off",
    "screw_thread_twist_off",
    "hinged_flip_cap",
    "merged_into_dispense",  # synthetic: cap merged into doe-foot applicator
]
PaletteStyle = Literal[
    "classic_white_silver_red",
    "gold_pink_gloss",
    "matte_black_gunmetal",
    "rose_gold_nude",
    "frosted_clear_berry",
    "pearlescent_lilac_silver",
    "lacquer_red_gold",
    "gunmetal_softtouch_plum",
    "two_tone_cream_navy_coral",
    "marble_print_mauve",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "round_cylinder",
    "octagon_faceted",
    "square_rounded",
    "tapered_waisted",
)
DISPENSE_MECHS: tuple[DispenseMech, ...] = (
    "twist_up_bullet",
    "doe_foot_applicator",
    "push_up_swivel_pot",
)
# cap candidates that the sampler may pick (merged is assigned, not sampled)
CAP_CLOSURES: tuple[CapClosure, ...] = (
    "friction_pull_off",
    "screw_thread_twist_off",
    "hinged_flip_cap",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_white_silver_red",
    "gold_pink_gloss",
    "matte_black_gunmetal",
    "rose_gold_nude",
    "frosted_clear_berry",
    "pearlescent_lilac_silver",
    "lacquer_red_gold",
    "gunmetal_softtouch_plum",
    "two_tone_cream_navy_coral",
    "marble_print_mauve",
)

# ---------------------------------------------------------------------------
# Palettes (spec §palette: 10 colorways + finish). Components:
#   tube  = tube_base body
#   cap   = cap shell (or merged applicator shell)
#   product = bullet / gloss product head, plus an applicator tip variant
#   accent = center band
# RGBA anchored to 5-star sources; later styles interpolated to real lipstick
# colorways. ``finish`` is a fixed per-style attribute (render semantics only).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _Palette:
    tube: tuple[float, float, float, float]
    cap: tuple[float, float, float, float]
    product: tuple[float, float, float, float]
    tip: tuple[float, float, float, float]
    accent: tuple[float, float, float, float]
    finish: str


PALETTES: dict[PaletteStyle, _Palette] = {
    "classic_white_silver_red": _Palette(
        tube=(0.93, 0.93, 0.94, 1.0),
        cap=(0.93, 0.93, 0.94, 1.0),
        product=(0.86, 0.10, 0.10, 1.0),
        tip=(0.86, 0.10, 0.10, 1.0),
        accent=(0.74, 0.75, 0.78, 1.0),
        finish="glossy_lacquer",
    ),
    "gold_pink_gloss": _Palette(
        tube=(0.78, 0.62, 0.18, 1.0),
        cap=(0.86, 0.88, 0.90, 0.32),
        product=(0.93, 0.55, 0.66, 1.0),
        tip=(0.86, 0.18, 0.45, 1.0),
        accent=(0.78, 0.62, 0.18, 1.0),
        finish="frosted_gloss",
    ),
    "matte_black_gunmetal": _Palette(
        tube=(0.12, 0.12, 0.13, 1.0),
        cap=(0.12, 0.12, 0.13, 1.0),
        product=(0.86, 0.10, 0.10, 1.0),
        tip=(0.86, 0.10, 0.10, 1.0),
        accent=(0.40, 0.42, 0.45, 1.0),
        finish="matte",
    ),
    "rose_gold_nude": _Palette(
        tube=(0.80, 0.55, 0.50, 1.0),
        cap=(0.80, 0.55, 0.50, 1.0),
        product=(0.78, 0.52, 0.45, 1.0),
        tip=(0.78, 0.52, 0.45, 1.0),
        accent=(0.74, 0.75, 0.78, 1.0),
        finish="metallic",
    ),
    "frosted_clear_berry": _Palette(
        tube=(0.88, 0.88, 0.90, 0.55),
        cap=(0.88, 0.88, 0.90, 0.55),
        product=(0.55, 0.10, 0.25, 1.0),
        tip=(0.55, 0.10, 0.25, 1.0),
        accent=(0.74, 0.75, 0.78, 1.0),
        finish="frosted_gloss",
    ),
    "pearlescent_lilac_silver": _Palette(
        tube=(0.86, 0.82, 0.90, 1.0),
        cap=(0.86, 0.82, 0.90, 1.0),
        product=(0.80, 0.45, 0.55, 1.0),
        tip=(0.80, 0.45, 0.55, 1.0),
        accent=(0.74, 0.75, 0.78, 1.0),
        finish="pearlescent",
    ),
    "lacquer_red_gold": _Palette(
        tube=(0.72, 0.08, 0.12, 1.0),
        cap=(0.72, 0.08, 0.12, 1.0),
        product=(0.86, 0.10, 0.10, 1.0),
        tip=(0.86, 0.10, 0.10, 1.0),
        accent=(0.78, 0.62, 0.18, 1.0),
        finish="glossy_lacquer",
    ),
    "gunmetal_softtouch_plum": _Palette(
        tube=(0.14, 0.14, 0.16, 1.0),
        cap=(0.32, 0.33, 0.36, 1.0),
        product=(0.45, 0.12, 0.28, 1.0),
        tip=(0.45, 0.12, 0.28, 1.0),
        accent=(0.40, 0.42, 0.45, 1.0),
        finish="soft_touch",
    ),
    "two_tone_cream_navy_coral": _Palette(
        tube=(0.95, 0.92, 0.84, 1.0),
        cap=(0.13, 0.18, 0.34, 1.0),
        product=(0.90, 0.38, 0.34, 1.0),
        tip=(0.90, 0.38, 0.34, 1.0),
        accent=(0.78, 0.62, 0.18, 1.0),
        finish="two_tone",
    ),
    "marble_print_mauve": _Palette(
        tube=(0.90, 0.89, 0.88, 1.0),
        cap=(0.74, 0.75, 0.78, 1.0),
        product=(0.72, 0.40, 0.48, 1.0),
        tip=(0.72, 0.40, 0.48, 1.0),
        accent=(0.74, 0.75, 0.78, 1.0),
        finish="marble_print",
    ),
}

# ---------------------------------------------------------------------------
# Nominal geometry (meters) — anchored to parent A. Scaled per-build.
# ---------------------------------------------------------------------------
_TUBE_R = 0.0105          # outer radius / half-width of the tube (matches 5★ sources)
_TUBE_WALL = 0.0016
# Proportions anchored to the 5★ source assets (parent A + var_*): every source
# tube body is ~50 mm tall × ~21-25 mm wide (ratio ~2.0-2.4), and with the cap on
# reads as a proper elongated 💄 (~90 mm closed). We DON'T over-stretch it into a
# thin straw — the closed silhouette, not a needle body, is what makes it a
# lipstick. width ~= 2*_TUBE_R = 0.021 (round), ~0.0227 (waisted flare).
_BASE_TOP_Z = 0.056       # top rim of the body (round/octa/squircle straight tube)
_BAND_Z = 0.050           # accent band height, wrapping the OUTER surface near the top
_FLOOR_Z = 0.004          # closed floor thickness at the bottom of the bore

_CAP_LEN = 0.046          # cap height (≈ source: cap nearly as tall as the body)
_CAP_WALL = 0.0014

_BULLET_R = 0.0072        # nominal red product radius (resolve widens it to fill the bore)
_CUP_LEN = 0.008          # carrier cup height (short — stays hidden under the product)
# The seated product is a TALL red column that nearly fills the bore (radius ≈ bore)
# and rests with its rounded head ~18 mm below the rim, so looking into the open
# mouth you see the lipstick product itself, NOT a wide carrier disc plugging the
# bore. ``_BULLET_LEN`` is only a floor; ``resolve_config`` derives the real length
# from the tube height. The rise travel auto-extends to emerge it above the mouth.
_BULLET_LEN = 0.013       # straight portion of bullet below the rounded nose (floor)
_PRODUCT_TOP_GAP = 0.012  # rest gap from the rim down to the product head (≈ source)
_RISE_HEIGHT = 0.030      # twist-up / push-up travel
# Seat the carrier/slider on the tube floor (retracted). The cup grips the bore
# wall for the contact path; the tall product column rises out of it.
_DISPENSE_SEAT_Z = 0.004
_BULLET_DOME_H = _BULLET_R * 0.75  # gentle rounded lipstick-nose height above the column

# screw neck nominal
_NECK_R = 0.0095
_NECK_LEN = 0.008
_THREAD_PITCH = 0.004
_THREAD_TURNS = 2
_THREAD_RIDGE_H = 0.0006
_THREAD_RIDGE_W = 0.0010

# flip hinge nominal
_LUG_W = 0.008
_LUG_D = 0.004
_LUG_H = 0.008
_KNUCKLE_R = 0.0028
_KNUCKLE_LEN = 0.007


@dataclass(frozen=True)
class ContainerLipstickConfig:
    body_form: BodyForm = "round_cylinder"
    dispense_mech: DispenseMech = "twist_up_bullet"
    cap_closure: CapClosure = "friction_pull_off"
    palette_style: PaletteStyle = "classic_white_silver_red"
    tube_height_scale: float = 1.0
    tube_radius_scale: float = 1.0
    cap_height_scale: float = 1.0
    dispense_travel_scale: float = 1.0
    name: str = "container_lipstick"


@dataclass(frozen=True)
class ResolvedContainerLipstickConfig:
    body_form: BodyForm
    dispense_mech: DispenseMech
    cap_closure: CapClosure  # may be "merged_into_dispense" for doe_foot
    palette_style: PaletteStyle
    tube_height_scale: float
    tube_radius_scale: float
    cap_height_scale: float
    dispense_travel_scale: float
    # derived geometry
    tube_r: float            # outer radius / half-width
    inner_r: float           # bore radius
    base_top_z: float        # body top rim (straight tube)
    band_z: float
    floor_z: float
    cup_r: float
    bullet_r: float
    cup_len: float
    bullet_len: float
    rise_height: float
    cap_outer_r: float       # equation: tube_r + proud
    cap_bore_r: float        # equation: tube_r + clearance
    cap_len: float
    cap_rest_z: float        # cap mount plane (band rim / neck shoulder / rear rim)
    # screw neck (only meaningful when cap_closure == screw)
    neck_r: float
    neck_len: float
    neck_bottom_z: float
    neck_top_z: float
    has_neck: bool
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerLipstickConfig:
    """Deterministic procedural sampling (seed 0 is not special).

    Sample body_form -> dispense_mech; if dispense is doe_foot the cap_closure
    slot is merged into the applicator (compat rule), otherwise sample a cap.
    Then uniform continuous scales + palette_style.
    """
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    dispense_mech = rng.choice(DISPENSE_MECHS)
    if dispense_mech == "doe_foot_applicator":
        cap_closure: CapClosure = "merged_into_dispense"
    else:
        cap_closure = rng.choice(CAP_CLOSURES)
    return ContainerLipstickConfig(
        body_form=body_form,
        dispense_mech=dispense_mech,
        cap_closure=cap_closure,
        palette_style=rng.choice(PALETTE_STYLES),
        tube_height_scale=round(rng.uniform(0.85, 1.20), 4),
        tube_radius_scale=round(rng.uniform(0.88, 1.12), 4),
        cap_height_scale=round(rng.uniform(0.85, 1.15), 4),
        dispense_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_container_lipstick_{seed}",
    )


def resolve_config(
    config: ContainerLipstickConfig | None = None,
) -> ResolvedContainerLipstickConfig:
    cfg = config or ContainerLipstickConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    dispense_mech = _pick(cfg.dispense_mech, DISPENSE_MECHS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    # Compatibility matrix: doe_foot merges the cap into the applicator.
    if dispense_mech == "doe_foot_applicator":
        cap_closure: CapClosure = "merged_into_dispense"
    else:
        cap_closure = _pick(cfg.cap_closure, CAP_CLOSURES)

    h_scale = _clamp(cfg.tube_height_scale, 0.85, 1.20)
    r_scale = _clamp(cfg.tube_radius_scale, 0.88, 1.12)
    ch_scale = _clamp(cfg.cap_height_scale, 0.85, 1.15)
    dt_scale = _clamp(cfg.dispense_travel_scale, 0.85, 1.10)

    tube_r = _TUBE_R * r_scale
    inner_r = tube_r - _TUBE_WALL
    base_top_z = _BASE_TOP_Z * h_scale
    band_z = _BAND_Z * h_scale
    floor_z = _FLOOR_Z

    # Bullet/cup径配合: the carrier cup is a sliding fit that GRIPS the bore wall
    # (cup_r a hair over inner_r) so the bullet part actually contacts the grounded
    # tube — without that contact ``fail_if_isolated_parts`` floats the bullet (the
    # massless carrier joint alone is not a support path). Captured overlap is
    # grandfathered via allow_overlap.
    #
    # 口红可见: the red product column is widened to ~bore radius so it FILLS the
    # cavity and is the thing you see looking into the open mouth — the short cup
    # ring stays hidden under it instead of reading as a wide disc plugging the bore.
    cup_r = inner_r + 0.0003
    bullet_r = inner_r - 0.0004
    cup_len = _CUP_LEN
    # Tall product column: seat the rounded head ~_PRODUCT_TOP_GAP below the rim so
    # the product is clearly visible in the cavity at rest. Length derived from the
    # tube height so it scales with h_scale (floored by _BULLET_LEN for tiny tubes).
    target_top = base_top_z - _PRODUCT_TOP_GAP
    bullet_len = max(
        _BULLET_LEN,
        target_top - _DISPENSE_SEAT_Z - cup_len - _BULLET_DOME_H,
    )

    # 升出露口: the rise must lift the seated bullet clear above the mouth. The
    # bullet sits with its base at the twist/slider seat z (_DISPENSE_SEAT_Z) and
    # its top (cup + column + rounded dome head) at seated_top. Derive the minimum
    # travel that pushes seated_top above base_top_z with margin, then apply
    # dt_scale as an *increase-only* factor so the bullet always emerges.
    seated_top = _DISPENSE_SEAT_Z + cup_len + bullet_len + _BULLET_DOME_H
    required_rise = (base_top_z - seated_top) + 0.012  # clear the mouth + margin
    rise_height = max(_RISE_HEIGHT * h_scale, required_rise) * dt_scale
    rise_height = max(rise_height, required_rise)  # dt_scale<1 never under-travels

    # cap_radius equation: the friction/flip cap skirt GRIPS the rim/band as a
    # captured fit — bore slightly smaller than the band (tube_r+0.0006) so the
    # cap inner wall actually contacts the body (parent A: cap_bore=tube_r-0.0002),
    # not floats a hair off it. Outer is proud of the body. Captured overlap is
    # grandfathered via element-scoped allow_overlap in run_tests.
    cap_bore_r = tube_r + 0.0002
    cap_outer_r = cap_bore_r + (_CAP_WALL + 0.0008)
    cap_len = _CAP_LEN * ch_scale

    has_neck = cap_closure == "screw_thread_twist_off"
    if has_neck:
        # narrow threaded neck collared above a shoulder
        neck_len = _NECK_LEN
        neck_r = min(_NECK_R * r_scale, tube_r - 0.0006)
        neck_top_z = base_top_z
        neck_bottom_z = neck_top_z - neck_len
        cap_rest_z = neck_bottom_z          # cap seats on the round shoulder collar
        # screw cap bore clears the external thread ridges (outer=neck_r+ridge_h)
        # AND the round shoulder collar (neck_r+0.0014); internal cap threads
        # protrude back inward to mesh with the neck threads (captured fit).
        cap_bore_r = neck_r + 0.0016
        cap_outer_r = max(tube_r + 0.0012, cap_bore_r + _CAP_WALL)
    else:
        neck_len = 0.0
        neck_r = tube_r
        neck_top_z = base_top_z
        neck_bottom_z = base_top_z
        if cap_closure == "hinged_flip_cap":
            cap_rest_z = base_top_z         # flip cap seats on the top rim
        else:
            cap_rest_z = band_z             # friction cap drops to the band

    return ResolvedContainerLipstickConfig(
        body_form=body_form,
        dispense_mech=dispense_mech,
        cap_closure=cap_closure,
        palette_style=palette,
        tube_height_scale=h_scale,
        tube_radius_scale=r_scale,
        cap_height_scale=ch_scale,
        dispense_travel_scale=dt_scale,
        tube_r=tube_r,
        inner_r=inner_r,
        base_top_z=base_top_z,
        band_z=band_z,
        floor_z=floor_z,
        cup_r=cup_r,
        bullet_r=bullet_r,
        cup_len=cup_len,
        bullet_len=bullet_len,
        rise_height=rise_height,
        cap_outer_r=cap_outer_r,
        cap_bore_r=cap_bore_r,
        cap_len=cap_len,
        cap_rest_z=cap_rest_z,
        neck_r=neck_r,
        neck_len=neck_len,
        neck_bottom_z=neck_bottom_z,
        neck_top_z=neck_top_z,
        has_neck=has_neck,
        name=cfg.name or "container_lipstick",
    )


def with_overrides(
    config: ContainerLipstickConfig, **kwargs: object
) -> ContainerLipstickConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerLipstickConfig | ResolvedContainerLipstickConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerLipstickConfig)
        else resolve_config(config)
    )
    return (
        ("body_form", r.body_form),
        ("dispense_mech", r.dispense_mech),
        ("cap_closure", r.cap_closure),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot A — body_form mesh emitters (root tube_base)
# ===========================================================================
def _round_tube_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Round hollow open-top tube (parent A ``_tube_base_solid``)."""
    outer = cq.Workplane("XY").circle(r.tube_r).extrude(r.base_top_z)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=r.floor_z)
        .circle(r.inner_r)
        .extrude(r.base_top_z)
    )
    return outer.cut(bore)


def _octa_prism(half_flat: float, z0: float, z1: float) -> cq.Workplane:
    """Regular octagonal prism (parent B ``_octa_prism``)."""
    rad = half_flat / math.cos(math.pi / 8.0)
    pts = []
    for i in range(8):
        a = math.pi / 8.0 + i * math.pi / 4.0
        pts.append((rad * math.cos(a), rad * math.sin(a)))
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .polyline(pts)
        .close()
        .extrude(z1 - z0)
    )


def _octa_tube_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Octagonal faceted hollow open-top body (parent B ``_tube_body_mesh``)."""
    body = _octa_prism(r.tube_r, 0.0, r.base_top_z)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=r.floor_z)
        .circle(r.inner_r)
        .extrude(r.base_top_z)
    )
    body = body.cut(bore)
    body = body.edges("|Z").fillet(0.0006)
    return body


def _squircle_prism(
    half_w: float, fillet_r: float, length: float, offset_z: float = 0.0
) -> cq.Workplane:
    """Rounded-square (squircle) prism (var square_rounded ``_squircle_prism``)."""
    w = 2.0 * half_w
    solid = (
        cq.Workplane("XY")
        .workplane(offset=offset_z)
        .rect(w, w)
        .extrude(length)
    )
    if 0 < fillet_r < half_w:
        solid = solid.edges("|Z").fillet(fillet_r)
    return solid


def _squircle_tube_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Hollow squircle prism with closed floor and open top (var square_rounded)."""
    fillet_r = 0.40 * r.tube_r
    outer = _squircle_prism(r.tube_r, fillet_r, r.base_top_z)
    inner_half_w = r.tube_r - _TUBE_WALL
    inner_fillet = max(0.0005, fillet_r - _TUBE_WALL)
    bore = _squircle_prism(inner_half_w, inner_fillet, r.base_top_z, r.floor_z)
    return outer.cut(bore)


def _waisted_body_mesh(r: ResolvedContainerLipstickConfig) -> LatheGeometry:
    """Hourglass waisted hollow body via LatheGeometry (var tapered_waisted)."""
    r_top = r.tube_r
    r_base = r.tube_r * 1.08
    r_waist = r.tube_r * 0.95
    h = r.base_top_z
    inner_r = r.inner_r
    # Outer-wall control points (radius, z) — smooth hourglass.
    outer_ctrl = [
        (r_base, 0.0),
        (r_base, 0.004 * (h / _BASE_TOP_Z)),
        (r_base * 0.976, 0.16 * h),
        (r_base * 0.92, 0.28 * h),
        (r_waist, 0.40 * h),
        (r_waist, 0.50 * h),
        (r_waist * 1.02, 0.60 * h),
        (r_top * 1.01, 0.72 * h),
        (r_top * 1.05, 0.80 * h),
        (r_top, 0.88 * h),
        (r_top, h),
    ]
    outer_smooth = sample_catmull_rom_spline_2d(
        outer_ctrl, samples_per_segment=8, closed=False
    )
    profile: list[tuple[float, float]] = []
    profile.append((0.0, 0.0))
    profile.extend(outer_smooth)
    profile.append((inner_r, h))
    profile.append((inner_r, r.floor_z))
    profile.append((0.0, r.floor_z))
    return LatheGeometry(profile, segments=48, closed=True)


def _band_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Decorative accent band as a thin WALL stripe that follows the body's OWN
    cross-section at ``band_z``, essentially flush with the surface (a printed
    stripe wrapping the tube). NOT a protruding cylinder ring — the old cylinder
    band stood proud and, on faceted/square bodies, showed as cylinder tabs that
    made the tube read as two stacked sections. This slice matches the facets and
    is cut hollow at the bore so it never crosses the open mouth.
    """
    eps = 0.0002          # a hair proud so it reads as a flush printed stripe
    h = 0.004
    z0 = r.band_z
    bf = r.body_form
    if bf == "octagon_faceted":
        outer = _octa_prism(r.tube_r + eps, z0, z0 + h)
    elif bf == "square_rounded":
        outer = _squircle_prism(r.tube_r + eps, 0.40 * r.tube_r, h, z0)
    else:  # round_cylinder + tapered_waisted (≈ tube_r near the top)
        outer = (
            cq.Workplane("XY").workplane(offset=z0).circle(r.tube_r + eps).extrude(h)
        )
    bore = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.001)
        .circle(r.inner_r)
        .extrude(h + 0.002)
    )
    return outer.cut(bore)


def _push_slot_cutter(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Vertical thumb-tab slot through the +X wall (var push_up_swivel_pot)."""
    slot_w = 0.005
    slot_bottom_z = 0.005
    slot_dx = _TUBE_WALL + 0.002
    return (
        cq.Workplane("XY")
        .workplane(offset=slot_bottom_z)
        .center(r.tube_r, 0.0)
        .rect(slot_dx, slot_w)
        .extrude(r.base_top_z - slot_bottom_z)
    )


def _emit_tube_body(part, r: ResolvedContainerLipstickConfig, *, mats: dict) -> None:
    """Emit the root tube_base body mesh + center band (+ optional neck/lug)."""
    body_form = r.body_form
    if body_form == "round_cylinder":
        solid = _round_tube_solid(r)
    elif body_form == "octagon_faceted":
        solid = _octa_tube_solid(r)
    elif body_form == "square_rounded":
        solid = _squircle_tube_solid(r)
    else:  # tapered_waisted handled separately (lathe geometry)
        solid = None

    # Push-up cuts a vertical wall slot for the external thumb tab.
    if r.dispense_mech == "push_up_swivel_pot":
        if solid is not None:
            solid = solid.cut(_push_slot_cutter(r))

    # Screw cap needs a narrow round threaded neck collared on top.
    if r.has_neck and solid is not None:
        # lower the shoulder: cut the body down to neck_bottom_z then add neck.
        # For prism/round bodies, simply union a round neck above the rim. The
        # body already reaches base_top_z; we instead rebuild with shoulder.
        solid = _add_round_neck(solid, r)

    if body_form == "tapered_waisted":
        part.visual(
            mesh_from_geometry(_waisted_body_mesh(r), "tube_body"),
            material=mats["tube"],
            name="tube_body", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral", "marble_print_mauve"} else "metal.precious_gold"),
        )
        if r.has_neck:
            _emit_neck_threads_waisted(part, r, mats)
    else:
        part.visual(
            mesh_from_cadquery(solid, "tube_body"),
            material=mats["tube"],
            name="tube_body", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral", "marble_print_mauve"} else "metal.precious_gold"),
        )
        if r.has_neck:
            part.visual(
                mesh_from_cadquery(_external_thread_ridges(r), "neck_threads"),
                material=mats["accent"],
                name="neck_threads", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "rose_gold_nude", "frosted_clear_berry", "pearlescent_lilac_silver", "gunmetal_softtouch_plum", "marble_print_mauve"} else "metal.precious_gold"),
            )

    # ---- parting-line band (always): a FLUSH stripe matching the body cross-
    # section, in the SAME body colour — a subtle surface 纹路, NOT a contrasting
    # ring that splits the tube into two sections. (Deliberately not the accent
    # colour: the old proud silver/gray cylinder band was the "两节" culprit.) ----
    part.visual(
        mesh_from_cadquery(_band_solid(r), "center_band"),
        material=mats["tube"],
        name="center_band", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral", "marble_print_mauve"} else "metal.precious_gold"),
    )

    # ---- doe-foot gloss reservoir (fixed visual on body) ----
    if r.dispense_mech == "doe_foot_applicator":
        part.visual(
            mesh_from_cadquery(_gloss_solid(r), "gloss"),
            material=mats["product"],
            name="gloss", material_class_id="organic.wax",
        )

    # ---- flip hinge lug (fixed visual on rear top rim) ----
    if r.cap_closure == "hinged_flip_cap":
        part.visual(
            Box((_LUG_W, _LUG_D, _LUG_H)),
            origin=Origin(
                xyz=(0.0, -(r.tube_r + _LUG_D / 2.0 - 0.001), r.base_top_z + _LUG_H / 2.0)
            ),
            material=mats["accent"],
            name="hinge_lug", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "rose_gold_nude", "frosted_clear_berry", "pearlescent_lilac_silver", "gunmetal_softtouch_plum", "marble_print_mauve"} else "metal.precious_gold"),
        )


def _add_round_neck(solid: cq.Workplane, r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Carve a round threaded neck above a clean round shoulder (screw cap bodies).

    The body solid spans 0..base_top_z. To let a round screw cap seat on ANY body
    footprint (incl. octagon / squircle whose corners would otherwise foul the cap
    skirt) we (1) cut the body down to a round shoulder collar over the top
    shoulder zone so no prism corners protrude where the cap seats, (2) union a
    narrow round neck, and (3) re-bore the mouth open.
    """
    shoulder_r = r.neck_r + 0.0014
    shoulder_z = r.neck_bottom_z - 0.004  # start the round step just below the neck
    # Trim everything above shoulder_z that lies outside the round shoulder collar.
    # Intersect the upper region with a tall round cylinder of shoulder_r.
    upper = (
        cq.Workplane("XY")
        .workplane(offset=shoulder_z)
        .circle(shoulder_r)
        .extrude(r.base_top_z)  # extends past the top
    )
    lower = (
        cq.Workplane("XY")
        .circle(r.tube_r * 2.0)  # generous; keeps the full lower body footprint
        .extrude(shoulder_z)
    )
    keep = upper.union(lower)
    body = solid.intersect(keep)
    # Round threaded neck collared on top of the shoulder.
    neck = (
        cq.Workplane("XY")
        .workplane(offset=r.neck_bottom_z)
        .circle(r.neck_r)
        .extrude(r.neck_len + 0.0015)
    )
    body = body.union(neck)
    # Re-bore through the neck so the mouth is open up to the neck top.
    bore = (
        cq.Workplane("XY")
        .workplane(offset=r.floor_z)
        .circle(r.inner_r)
        .extrude(r.neck_top_z)
    )
    return body.cut(bore)


def _external_thread_ridges(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Helical external thread ridges on the neck (var screw twistExtrude)."""
    r_inner = r.neck_r - 0.0001
    r_outer = r.neck_r + _THREAD_RIDGE_H
    hw = _THREAD_RIDGE_W / 2.0
    start_z = r.neck_bottom_z + 0.001
    total_z = _THREAD_PITCH * _THREAD_TURNS
    return (
        cq.Workplane("XY")
        .workplane(offset=start_z)
        .moveTo(r_inner, -hw)
        .lineTo(r_outer, -hw)
        .lineTo(r_outer, hw)
        .lineTo(r_inner, hw)
        .close()
        .twistExtrude(total_z, _THREAD_TURNS * 360.0)
    )


def _emit_neck_threads_waisted(part, r, mats) -> None:
    """Waisted body uses a round neck cylinder + external threads (separate visuals)."""
    part.visual(
        Cylinder(radius=r.neck_r, length=r.neck_len + 0.0015),
        origin=Origin(xyz=(0.0, 0.0, r.neck_bottom_z + (r.neck_len + 0.0015) / 2.0)),
        material=mats["tube"],
        name="neck_collar", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral", "marble_print_mauve"} else "metal.precious_gold"),
    )
    part.visual(
        mesh_from_cadquery(_external_thread_ridges(r), "neck_threads"),
        material=mats["accent"],
        name="neck_threads", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "rose_gold_nude", "frosted_clear_berry", "pearlescent_lilac_silver", "gunmetal_softtouch_plum", "marble_print_mauve"} else "metal.precious_gold"),
    )


def _gloss_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Product gloss reservoir lining the lower bore (parent B ``_gloss_mesh``).

    Formerly a solid pool+column that plugged the lower bore (a solid slab under
    the opening). It is now an open-top thin-wall reservoir well: a thin floor on
    the tube floor + a thin ring wall, with a hollow centre so the tube interior
    is visible down through the mouth. The doe-foot tip dips into this open well
    at rest (captured-fit overlap, unchanged).
    """
    pool_top = r.floor_z + 0.010 * (r.base_top_z / _BASE_TOP_Z)
    column_top = pool_top - 0.001 + 0.012
    pool = (
        cq.Workplane("XY")
        .workplane(offset=r.floor_z)
        .circle(r.inner_r - 0.0008)
        .extrude(pool_top - r.floor_z)
    )
    column = (
        cq.Workplane("XY")
        .workplane(offset=pool_top - 0.001)
        .circle(r.inner_r - 0.0014)
        .extrude(0.012)
    )
    well = pool.union(column)
    # Hollow the centre so the reservoir reads as an open well, not a solid plug.
    recess = (
        cq.Workplane("XY")
        .workplane(offset=r.floor_z + 0.0016)
        .circle(r.inner_r - 0.0024)
        .extrude(column_top)  # extends past the top -> open well, no center plug
    )
    return well.cut(recess)


# ===========================================================================
# Shared dispense geometry
# ===========================================================================
def _cup_wall_t() -> float:
    """Thin cup wall — grips the bore, leaves the cup interior hollow."""
    return 0.0013


def _cup_floor_t() -> float:
    """Thin cup floor — keeps the cup a real (connected) open-top cup."""
    return 0.0020


def _hollow_cup(cup_r: float, cup_len: float, bore_r: float) -> cq.Workplane:
    """Open-top thin-wall carrier cup gripping the bore, hollow inside.

    The seated cup used to be a solid full-bore disc which read as a solid plug
    under the tube opening. It is now an open-top cup: a thin floor + a thin ring
    wall (outer = ``cup_r`` so it still grips the bore wall for the
    ``fail_if_isolated_parts`` contact path), with an open central recess so the
    tube interior / bullet channel is visible down through the mouth. The bullet
    column seats on the remaining top ring (``bore_r`` is chosen < the bullet
    radius so the column rests on the ring and the part stays one solid).
    """
    outer = cq.Workplane("XY").circle(cup_r).extrude(cup_len)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=_cup_floor_t())
        .circle(bore_r)
        .extrude(cup_len)  # extends past the top -> open cup, no center plug
    )
    return outer.cut(bore)


def _cup_bore_r(r: ResolvedContainerLipstickConfig) -> float:
    """Inner recess radius of the carrier cup.

    Kept a hair below the bullet column radius so the bullet seats on the cup top
    ring (one connected solid) while the centre is still an open recess.
    """
    return max(0.0018, r.bullet_r - 0.0006)


def _bullet_cup_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    return _hollow_cup(r.cup_r, r.cup_len, _cup_bore_r(r))


def _bullet_red_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Red product column with the classic SLANTED-FLAT lipstick tip.

    One solid cylinder (radius ≈ bore, so it fills the cavity and is the thing you
    see looking in), with the top sheared off by a single angled plane to form the
    diagonal oval face of a real lipstick bullet — NOT a pointy dome / spike. The
    high lip of the slant is the tallest point (== the height budget resolve_config
    reserves), the low lip is ~one diameter lower, giving the familiar lipstick
    bevel. The leading edge is lightly rounded so it doesn't read as a sharp point.
    """
    col_bottom = r.cup_len
    total_h = r.bullet_len + _BULLET_DOME_H  # high lip lands at the reserved top
    top_z = col_bottom + total_h
    column = (
        cq.Workplane("XY")
        .workplane(offset=col_bottom)
        .circle(r.bullet_r)
        .extrude(total_h)
    )
    # Slant the top: a slab tilted ~24° about +X, lowered so its underside slices a
    # clean diagonal across the cylinder top. The −Y rim stays highest (== top_z),
    # the +Y rim is cut down ~2·r·tan(24°). Everything above the plane is removed.
    slant_deg = 24.0
    drop = r.bullet_r * math.tan(math.radians(slant_deg))  # half the slant fall
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=top_z)
        .transformed(rotate=(slant_deg, 0.0, 0.0))
        .rect(6.0 * r.bullet_r, 6.0 * r.bullet_r)
        .extrude(0.04)
        .translate((0.0, 0.0, -drop))
    )
    bullet = column.cut(cutter)
    # Soften the sharp slant rim so the tip reads as a worn lipstick, not a blade.
    try:
        bullet = bullet.edges(">Z").fillet(min(0.0010, r.bullet_r * 0.18))
    except Exception:
        pass
    return bullet


def _slider_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Cup + rib through the slot + external thumb tab (var push_up ``_slider_solid``)."""
    cup = _hollow_cup(r.cup_r, r.cup_len, _cup_bore_r(r))
    rib_w = 0.003
    rib_z_lo, rib_z_hi = 0.002, 0.008
    rib_x_lo = r.cup_r * 0.5
    rib_x_hi = r.tube_r + 0.001
    rib = (
        cq.Workplane("XY")
        .workplane(offset=rib_z_lo)
        .center((rib_x_lo + rib_x_hi) / 2.0, 0.0)
        .rect(rib_x_hi - rib_x_lo, rib_w)
        .extrude(rib_z_hi - rib_z_lo)
    )
    tab_w, tab_h, tab_d = 0.007, 0.008, 0.004
    tab = (
        cq.Workplane("XY")
        .workplane(offset=0.001)
        .center(r.tube_r + tab_d / 2.0, 0.0)
        .rect(tab_d, tab_w)
        .extrude(tab_h)
    )
    return cup.union(rib).union(tab)


# ===========================================================================
# Slot B — dispense mechanism builders
# ===========================================================================
def _build_twist_up(model, base, r, *, mats) -> None:
    """Massless carrier CONTINUOUS twist DECOUPLES bullet PRISMATIC rise (parent A)."""
    carrier = model.part("bullet_carrier")
    carrier.inertial = Inertial.from_geometry(Box((0.004, 0.004, 0.004)), mass=1e-4)
    model.articulation(
        "bullet_twist",
        ArticulationType.CONTINUOUS,
        parent=base,
        child=carrier,
        origin=Origin(xyz=(0.0, 0.0, _DISPENSE_SEAT_Z)),  # carrier seated on the bore floor
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0),
    )

    bullet = model.part("bullet")
    bullet.visual(
        mesh_from_cadquery(_bullet_cup_solid(r), "carrier_cup"),
        # Product-coloured (not gray accent): the carrier cup sits low in the bore
        # under the bullet; colouring it like the product means looking into the
        # open mouth you see lipstick, never a foreign gray disc plugging the top.
        material=mats["product"],
        name="carrier_cup", material_class_id="organic.wax",
    )
    bullet.visual(
        mesh_from_cadquery(_bullet_red_solid(r), "bullet_red"),
        material=mats["product"],
        name="bullet_red", material_class_id="organic.wax",
    )
    # Off-axis spin reference riding in the cup wall (pokes through the outer wall
    # so it is surface-connected to the cup — not a disconnected island). Now
    # PRODUCT-coloured (not a dark dot) and it sits low in the bore, hidden behind
    # the product, so it is not a visible dot — it only lets the spin test see the
    # otherwise-axisymmetric bullet rotate.
    bullet.visual(
        Box((0.0016, 0.0016, 0.004)),
        origin=Origin(xyz=(r.cup_r - 0.0006, 0.0, r.cup_len / 2.0)),
        material=mats["product"],
        name="twist_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    bullet.inertial = Inertial.from_geometry(
        Cylinder(radius=r.bullet_r, length=r.cup_len + r.bullet_len),
        mass=0.004,
        origin=Origin(xyz=(0.0, 0.0, (r.cup_len + r.bullet_len) / 2.0)),
    )
    model.articulation(
        "bullet_rise",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=bullet,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=1.0, lower=0.0, upper=r.rise_height
        ),
    )


def _build_push_up(model, base, r, *, mats) -> None:
    """Single PRISMATIC slider carrying the bullet (var push_up_swivel_pot)."""
    slider = model.part("slider")
    slider.visual(
        mesh_from_cadquery(_slider_solid(r), "slider_body"),
        # Product-coloured so the in-bore cup reads as lipstick, not a gray disc.
        material=mats["product"],
        name="slider_body", material_class_id="organic.wax",
    )
    slider.visual(
        mesh_from_cadquery(_bullet_red_solid(r), "bullet_red"),
        material=mats["product"],
        name="bullet_red", material_class_id="organic.wax",
    )
    slider.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cup_r, length=r.cup_len + r.bullet_len + 0.010),
        mass=0.006,
        origin=Origin(xyz=(0.0, 0.0, (r.cup_len + r.bullet_len) / 2.0)),
    )
    model.articulation(
        "slider_push",
        ArticulationType.PRISMATIC,
        parent=base,
        child=slider,
        origin=Origin(xyz=(0.0, 0.0, _DISPENSE_SEAT_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=1.5, velocity=0.3, lower=0.0, upper=r.rise_height
        ),
    )


def _doe_geom(r: ResolvedContainerLipstickConfig) -> dict:
    """Shared z-frame for the merged doe-foot applicator (cap socket / wand / tip).

    Returns the cap z-range and the cap inner socket roof so the wand stem can be
    extruded right up into the solid cap crown (one connected applicator body).
    """
    cap_h = r.cap_len * 0.65
    z1 = r.base_top_z + 0.012
    z0 = z1 - cap_h
    socket_h = cap_h - 0.006
    socket_roof_z = (z0 - 0.001) + socket_h  # top of the hollow socket cavity
    # Seat the tip so its lower hemisphere dips into the SOLID gloss floor (the
    # pool below the open recess), giving the cap_applicator a real contact with
    # the grounded tube_base — independent of the (now flush) accent band, which
    # used to be the accidental contact path before it was made flush.
    tip_center_z = r.floor_z + 0.0045
    return {
        "cap_flat": r.tube_r + 0.0013,
        "cap_h": cap_h,
        "z0": z0,
        "z1": z1,
        "socket_h": socket_h,
        "socket_roof_z": socket_roof_z,
        "tip_center_z": tip_center_z,
        "tip_r": 0.0045,
        "wand_r": 0.0019,
    }


def _doe_cap_mesh(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Merged applicator cap shell matching the body cross-section, with a body-
    shaped socket so it seats snugly over the tube rim (a round socket clipped the
    corners of faceted/square bodies — 穿模). Outer is one wall thicker than the
    socket, both following the body footprint."""
    g = _doe_geom(r)
    socket_dim = r.tube_r + 0.0006
    outer = _cap_outline_prism(r, socket_dim + 0.0013, g["z0"], g["z1"] - g["z0"])
    socket = _cap_outline_prism(r, socket_dim, g["z0"] - 0.001, g["socket_h"])
    cap = outer.cut(socket)
    try:
        cap = cap.edges("|Z").fillet(0.0008)
    except Exception:
        pass
    return cap


def _doe_wand_mesh(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """White doe-foot wand stem (parent B ``_wand_mesh``).

    Bottom seats into the doe-foot tip; top is buried 1.5 mm into the solid cap
    crown (above the socket roof) so the cap, wand, and tip form one connected
    solid for the per-part connectivity check.
    """
    g = _doe_geom(r)
    stem_bottom = g["tip_center_z"] + g["tip_r"] * 0.5
    stem_top = g["socket_roof_z"] + 0.0015  # embed into the solid crown
    return (
        cq.Workplane("XY")
        .workplane(offset=stem_bottom)
        .circle(g["wand_r"])
        .extrude(max(0.010, stem_top - stem_bottom))
    )


def _doe_tip_mesh(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Soft doe-foot applicator tip (parent B ``_tip_mesh``)."""
    g = _doe_geom(r)
    tip_r = g["tip_r"]
    tip_center_z = g["tip_center_z"]
    body = (
        cq.Workplane("XY")
        .workplane(offset=tip_center_z)
        .circle(tip_r)
        .extrude(0.008)
    )
    nose = cq.Workplane("XY").sphere(tip_r).translate((0.0, 0.0, tip_center_z))
    top = cq.Workplane("XY").sphere(tip_r * 0.85).translate(
        (0.0, 0.0, tip_center_z + 0.008)
    )
    return body.union(nose).union(top)


def _build_doe_foot(model, base, r, *, mats) -> None:
    """One rigid cap+wand+tip part on a single PRISMATIC pull (parent B). Merged cap."""
    cap = model.part("cap_applicator")
    cap.visual(
        mesh_from_cadquery(_doe_cap_mesh(r), "cap"),
        material=mats["cap"],
        name="cap", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "gold_pink_gloss", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral"} else "metal.brushed_silver"),
    )
    cap.visual(
        mesh_from_cadquery(_doe_wand_mesh(r), "wand_stem"),
        material=mats["wand"],
        name="wand_stem", material_class_id="plastic.opaque_glossy_molded",
    )
    cap.visual(
        mesh_from_cadquery(_doe_tip_mesh(r), "doe_foot_tip"),
        material=mats["tip"],
        name="doe_foot_tip", material_class_id="fabric.felt",
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.tube_r, length=r.base_top_z),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, r.base_top_z / 2.0)),
    )
    # Pull must lift the doe-foot tip (seated bottom at tip_center_z) clear above
    # the tube mouth (neck_top_z) with margin, like the bullet rise clears it.
    g = _doe_geom(r)
    pull = (r.neck_top_z - g["tip_center_z"]) + 0.014
    model.articulation(
        "tube_to_cap",
        ArticulationType.PRISMATIC,
        parent=base,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.2, lower=0.0, upper=pull),
    )


# ===========================================================================
# Slot C — cap closure builders (skipped for doe_foot / merged)
# ===========================================================================
def _cap_shell_round_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Round hollow cap shell, open bottom, closed top (screw cap over the round neck)."""
    outer = cq.Workplane("XY").circle(r.cap_outer_r).extrude(r.cap_len)
    bore = (
        cq.Workplane("XY")
        .circle(r.cap_bore_r)
        .extrude(r.cap_len - 0.004)
    )
    return outer.cut(bore)


def _cap_outline_prism(
    r: ResolvedContainerLipstickConfig, dim: float, z0: float, length: float
) -> cq.Workplane:
    """A prism matching the BODY cross-section at half-dimension ``dim`` — used to
    build caps that fit the body shape (round / octagon / squircle / round-top)."""
    bf = r.body_form
    if bf == "octagon_faceted":
        return _octa_prism(dim, z0, z0 + length)
    if bf == "square_rounded":
        return _squircle_prism(dim, 0.40 * dim, length, z0)
    # round_cylinder + tapered_waisted (round near the top)
    return cq.Workplane("XY").workplane(offset=z0).circle(dim).extrude(length)


def _cap_shell_body_solid(
    r: ResolvedContainerLipstickConfig, bore_dim: float, outer_dim: float, length: float
) -> cq.Workplane:
    """Closed-top, open-bottom cap shell that MATCHES the body cross-section so it
    seats snugly over the tube. A plain round cap over a faceted/square body left
    the corners poking through the cap wall (穿模); a body-shaped, axis-aligned cap
    clears every facet with a uniform thin gap and just covers the tube."""
    outer = _cap_outline_prism(r, outer_dim, 0.0, length)
    bore = _cap_outline_prism(r, bore_dim, 0.0, length - 0.004)
    return outer.cut(bore)


def _internal_thread_ridges(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Internal helical thread ridges in the screw cap bore (var screw).

    Protrude inward far enough that the internal ridge crest reaches the external
    neck-thread crest (neck_r + ridge_h) so the screw interface actually meshes
    (captured contact — the cap is supported by the neck, not floating).
    """
    r_outer = r.cap_bore_r + 0.0001
    # crest reaches just inside the external thread outer radius (captured mesh)
    r_inner = r.neck_r + _THREAD_RIDGE_H - 0.0001
    hw = _THREAD_RIDGE_W / 2.0
    z_start = _THREAD_PITCH / 2.0 + 0.001
    total_z = _THREAD_PITCH * _THREAD_TURNS
    return (
        cq.Workplane("XY")
        .workplane(offset=z_start)
        .moveTo(r_inner, -hw)
        .lineTo(r_outer, -hw)
        .lineTo(r_outer, hw)
        .lineTo(r_inner, hw)
        .close()
        .twistExtrude(total_z, _THREAD_TURNS * 360.0)
    )


def _build_friction_cap(model, base, r, *, mats) -> None:
    """Single PRISMATIC +Z lift-off cap (parent A ``cap_pull``), body-shaped fit."""
    cap = model.part("cap")
    cap.visual(
        mesh_from_cadquery(
            _cap_shell_body_solid(r, r.cap_bore_r, r.cap_outer_r, r.cap_len), "cap_shell"
        ),
        material=mats["cap"],
        name="cap_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "gold_pink_gloss", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral"} else "metal.brushed_silver"),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cap_outer_r, length=r.cap_len),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, r.cap_len / 2.0)),
    )
    model.articulation(
        "cap_pull",
        ArticulationType.PRISMATIC,
        parent=base,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, r.cap_rest_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.2, lower=0.0, upper=0.050),
    )


def _build_screw_cap(model, base, r, *, mats) -> None:
    """Round threaded twist-off cap that LIFTS straight up to open (PRISMATIC +Z).

    Real screw caps unscrew then lift off; we model the open action as a straight
    +Z lift (so it opens upward like the other caps and reveals the product), while
    the visible internal/external thread ridges keep the screw-cap identity. The
    cap rides over the round threaded neck, so a round shell fits with no 穿模.
    """
    cap = model.part("cap")
    cap.visual(
        mesh_from_cadquery(_cap_shell_round_solid(r), "cap_shell"),
        material=mats["cap"],
        name="cap_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "gold_pink_gloss", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral"} else "metal.brushed_silver"),
    )
    cap.visual(
        mesh_from_cadquery(_internal_thread_ridges(r), "cap_threads"),
        material=mats["accent"],
        name="cap_threads", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "rose_gold_nude", "frosted_clear_berry", "pearlescent_lilac_silver", "gunmetal_softtouch_plum", "marble_print_mauve"} else "metal.precious_gold"),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cap_outer_r, length=r.cap_len),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, r.cap_len / 2.0)),
    )
    model.articulation(
        "cap_screw",
        ArticulationType.PRISMATIC,
        parent=base,
        child=cap,
        origin=Origin(xyz=(0.0, 0.0, r.cap_rest_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.2, lower=0.0, upper=0.055),
    )


def _flip_cap_shell_solid(r: ResolvedContainerLipstickConfig) -> cq.Workplane:
    """Body-shaped flip-cap shell so it seats snugly on the body rim (no 穿模)."""
    return _cap_shell_body_solid(
        r, r.cap_outer_r - _CAP_WALL, r.cap_outer_r, r.cap_len
    )


def _build_flip_cap(model, base, r, *, mats) -> None:
    """REVOLUTE +X flip cap hinged at the rear top rim (var flip)."""
    cap = model.part("cap")
    # Cap shell authored with bottom at z=0, centered y=0; visual origin offsets it
    # so its center sits over the tube axis (parent var pattern).
    cap.visual(
        mesh_from_cadquery(_flip_cap_shell_solid(r), "cap_shell"),
        origin=Origin(xyz=(0.0, r.tube_r, 0.0)),
        material=mats["cap"],
        name="cap_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"classic_white_silver_red", "gold_pink_gloss", "matte_black_gunmetal", "frosted_clear_berry", "pearlescent_lilac_silver", "lacquer_red_gold", "gunmetal_softtouch_plum", "two_tone_cream_navy_coral"} else "metal.brushed_silver"),
    )
    cap.visual(
        Cylinder(radius=_KNUCKLE_R, length=_KNUCKLE_LEN),
        origin=Origin(xyz=(0.0, 0.0, _LUG_H * 0.4), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="hinge_knuckle", material_class_id=("metal.brushed_silver" if r.palette_style in {"classic_white_silver_red", "matte_black_gunmetal", "rose_gold_nude", "frosted_clear_berry", "pearlescent_lilac_silver", "gunmetal_softtouch_plum", "marble_print_mauve"} else "metal.precious_gold"),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cap_outer_r, length=r.cap_len),
        mass=0.012,
        origin=Origin(xyz=(0.0, r.tube_r, r.cap_len / 2.0)),
    )
    model.articulation(
        "cap_flip",
        ArticulationType.REVOLUTE,
        parent=base,
        child=cap,
        origin=Origin(xyz=(0.0, -r.tube_r, r.base_top_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=2.4),
    )


# ===========================================================================
# Build entry point
# ===========================================================================
def build_container_lipstick(
    config: ContainerLipstickConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        "tube": model.material(f"cl_tube_{r.palette_style}", rgba=pal.tube),
        "cap": model.material(f"cl_cap_{r.palette_style}", rgba=pal.cap),
        "product": model.material(f"cl_product_{r.palette_style}", rgba=pal.product),
        "tip": model.material(f"cl_tip_{r.palette_style}", rgba=pal.tip),
        "accent": model.material(f"cl_accent_{r.palette_style}", rgba=pal.accent),
        "wand": model.material("cl_wand_white", rgba=(0.95, 0.95, 0.95, 1.0)),
        "marker": model.material("cl_marker_dark", rgba=(0.15, 0.15, 0.16, 1.0)),
    }

    # --- ROOT: tube_base body ------------------------------------------------
    base = model.part("tube_base")
    _emit_tube_body(base, r, mats=mats)
    base.inertial = Inertial.from_geometry(
        Box((2 * r.tube_r, 2 * r.tube_r, r.base_top_z)),
        mass=0.030,
        origin=Origin(xyz=(0.0, 0.0, r.base_top_z / 2.0)),
    )

    # --- dispense mechanism (Slot B) ----------------------------------------
    if r.dispense_mech == "twist_up_bullet":
        _build_twist_up(model, base, r, mats=mats)
    elif r.dispense_mech == "push_up_swivel_pot":
        _build_push_up(model, base, r, mats=mats)
    elif r.dispense_mech == "doe_foot_applicator":
        _build_doe_foot(model, base, r, mats=mats)

    # --- cap mechanism (Slot C) — skipped if merged into doe-foot -----------
    if r.cap_closure == "friction_pull_off":
        _build_friction_cap(model, base, r, mats=mats)
    elif r.cap_closure == "screw_thread_twist_off":
        _build_screw_cap(model, base, r, mats=mats)
    elif r.cap_closure == "hinged_flip_cap":
        _build_flip_cap(model, base, r, mats=mats)
    # merged_into_dispense: no independent cap part

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_lipstick(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_lipstick(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests / QC. Captured-fit overlaps (cap over rim, bullet/slider in bore,
# doe-foot in gloss, threads meshing, hinge embedding) are grandfathered via
# element-scoped allow_overlap. Mechanism actions are exercised.
# ===========================================================================
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_lipstick_tests(
    object_model: ArticulatedObject,
    config: ContainerLipstickConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    base = object_model.get_part("tube_base")

    # ---- slim upright tube identity: seated on z=0, height >> 2.5 * width ----
    body_aabb = ctx.part_element_world_aabb(base, elem="tube_body")
    bmn, bmx = body_aabb
    height = bmx[2] - bmn[2]
    width = max(bmx[0] - bmn[0], bmx[1] - bmn[1])
    ctx.check(
        "tube body rests on the ground (base near z=0)",
        abs(bmn[2]) < 0.006,
        details=f"body min z={bmn[2]:.4f}",
    )
    # Slim/elongated lipstick identity. The 5★ source assets themselves run ~2.0
    # (waisted flare) to ~2.38 (round) tall:wide for the BODY; with per-build scale
    # the legitimate range widens a little. We require >= 1.9 to admit the true
    # source range (the cap doubles the closed height into a proper 💄) while still
    # excluding the stubby jar/cosmetic footprint (those are < ~1.4).
    ctx.check(
        "tube body is slim (height >> width, lipstick identity)",
        height > 0.035 and height > 1.9 * width,
        details=f"height={height:.4f}, width={width:.4f}, ratio={height / max(width, 1e-6):.3f}",
    )

    tube_body = base.get_visual("tube_body")
    band = base.get_visual("center_band")
    ctx.check(
        "center band visual exists",
        band is not None,
        details="center_band visual missing",
    )

    # ---- OPEN MOUTH (hard product rule) ----
    # The top opening of the tube must NEVER be sealed by internal geometry: the
    # seated product / carrier cup / gloss must stay below the rim so the mouth is
    # an open aperture and the product is visible looking down into the cavity.
    # (A cap covering the mouth when closed is fine — that is the cap, not an
    # internal plug, so the cap part is excluded from this check.)
    rim_z = r.base_top_z
    if r.dispense_mech == "twist_up_bullet":
        prod = object_model.get_part("bullet")
        seated_aabb = ctx.part_world_aabb(prod)
        red_aabb = ctx.part_element_world_aabb(prod, elem="bullet_red")
    elif r.dispense_mech == "push_up_swivel_pot":
        prod = object_model.get_part("slider")
        seated_aabb = ctx.part_world_aabb(prod)
        red_aabb = ctx.part_element_world_aabb(prod, elem="bullet_red")
    else:  # doe_foot: the internal product is the gloss reservoir on tube_base
        seated_aabb = ctx.part_element_world_aabb(base, elem="gloss")
        red_aabb = seated_aabb
    ctx.check(
        "tube mouth is open — nothing internal seals the top opening",
        seated_aabb[1][2] < rim_z - 0.004,
        details=f"seated internal top z={seated_aabb[1][2]:.4f}, rim z={rim_z:.4f}",
    )
    if r.dispense_mech in ("twist_up_bullet", "push_up_swivel_pot"):
        # The red product nearly fills the bore (not a thin pin dwarfed by a wide
        # carrier disc) and sits high enough to read as the lipstick in the cavity.
        red_w = max(red_aabb[1][0] - red_aabb[0][0], red_aabb[1][1] - red_aabb[0][1])
        ctx.check(
            "seated product fills the bore and is visible in the open cavity",
            red_w > 1.4 * r.inner_r and red_aabb[1][2] > 0.5 * rim_z,
            details=(
                f"product width={red_w:.4f} (bore dia={2 * r.inner_r:.4f}), "
                f"product top z={red_aabb[1][2]:.4f}, rim z={rim_z:.4f}"
            ),
        )

    # ---- dispense mechanism: actions + captured-fit overlaps ----
    if r.dispense_mech == "twist_up_bullet":
        carrier = object_model.get_part("bullet_carrier")
        bullet = object_model.get_part("bullet")
        twist = object_model.get_articulation("bullet_twist")
        rise = object_model.get_articulation("bullet_rise")

        ctx.check(
            "bullet_carrier is massless (no visuals)",
            len(carrier.visuals) == 0,
            details=f"carrier visuals={len(carrier.visuals)}",
        )
        ctx.check(
            "bullet_twist is CONTINUOUS about +Z",
            twist.articulation_type == ArticulationType.CONTINUOUS
            and abs(twist.axis[2]) > 0.99,
            details=f"type={twist.articulation_type}, axis={twist.axis}",
        )
        ctx.check(
            "bullet_rise is PRISMATIC about +Z",
            rise.articulation_type == ArticulationType.PRISMATIC
            and abs(rise.axis[2]) > 0.99,
            details=f"type={rise.articulation_type}, axis={rise.axis}",
        )
        ctx.allow_overlap(
            bullet, base, elem_a="carrier_cup", elem_b="tube_body",
            reason="The carrier cup rides inside the tube bore (twist-up mechanism).",
        )
        ctx.allow_overlap(
            bullet, base, elem_a="bullet_red", elem_b="tube_body",
            reason="The red bullet starts nested inside the tube before being twisted up.",
        )
        # twist spins the bullet (off-axis marker moves)
        m0 = ctx.part_element_world_aabb(bullet, elem="twist_marker")
        m0c = ((m0[0][0] + m0[1][0]) / 2.0, (m0[0][1] + m0[1][1]) / 2.0)
        with ctx.pose({twist: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(bullet, elem="twist_marker")
            m1c = ((m1[0][0] + m1[1][0]) / 2.0, (m1[0][1] + m1[1][1]) / 2.0)
        ctx.check(
            "twist spins the bullet (marker moves)",
            math.hypot(m1c[0] - m0c[0], m1c[1] - m0c[1]) > 0.003,
            details=f"marker rest={m0c}, twisted={m1c}",
        )
        # rise raises the bullet up out of the tube
        rest_z = ctx.part_world_position(bullet)[2]
        with ctx.pose({rise: r.rise_height}):
            up_z = ctx.part_world_position(bullet)[2]
            top_z = ctx.part_world_aabb(bullet)[1][2]
        ctx.check(
            "twist-up raises the bullet",
            up_z > rest_z + r.rise_height * 0.6,
            details=f"rest_z={rest_z:.4f}, raised_z={up_z:.4f}",
        )
        ctx.check(
            "raised bullet emerges above the tube mouth",
            top_z > r.neck_top_z + 0.003,
            details=f"bullet top z={top_z:.4f}, mouth={r.neck_top_z:.4f}",
        )

    elif r.dispense_mech == "push_up_swivel_pot":
        slider = object_model.get_part("slider")
        push = object_model.get_articulation("slider_push")

        ctx.check(
            "slider_push is PRISMATIC about +Z (no rotating carrier)",
            push.articulation_type == ArticulationType.PRISMATIC
            and abs(push.axis[2]) > 0.99
            and "bullet_twist" not in [a.name for a in object_model.articulations],
            details=f"type={push.articulation_type}, axis={push.axis}",
        )
        ctx.allow_overlap(
            slider, base, elem_a="slider_body", elem_b="tube_body",
            reason="Slider cup rides in the bore; thumb tab wraps outside through the slot.",
        )
        ctx.allow_overlap(
            slider, base, elem_a="bullet_red", elem_b="tube_body",
            reason="Bullet starts nested inside the tube before being pushed up.",
        )
        ctx.allow_overlap(
            slider, base, elem_a="slider_body", elem_b="center_band",
            reason="Slider rib passes near the band at high extension through the slot.",
        )
        # thumb tab visible outside the tube radius
        sb = ctx.part_element_world_aabb(slider, elem="slider_body")
        ctx.check(
            "thumb tab extends beyond the tube outer radius",
            sb[1][0] > r.tube_r + 0.0005,
            details=f"slider max_x={sb[1][0]:.4f}, tube_r={r.tube_r:.4f}",
        )
        rest_z = ctx.part_world_position(slider)[2]
        rest_xy = ctx.part_world_position(slider)[:2]
        with ctx.pose({push: r.rise_height}):
            up = ctx.part_world_position(slider)
            top_z = ctx.part_world_aabb(slider)[1][2]
        ctx.check(
            "slider push raises the bullet straight up",
            up[2] > rest_z + r.rise_height * 0.6
            and abs(up[0] - rest_xy[0]) < 0.001
            and abs(up[1] - rest_xy[1]) < 0.001,
            details=f"rest_z={rest_z:.4f}, pushed_z={up[2]:.4f}",
        )
        ctx.check(
            "pushed bullet emerges above the tube mouth",
            top_z > r.neck_top_z + 0.003,
            details=f"bullet top z={top_z:.4f}",
        )

    elif r.dispense_mech == "doe_foot_applicator":
        cap = object_model.get_part("cap_applicator")
        pull = object_model.get_articulation("tube_to_cap")
        ctx.allow_isolated_part(
            cap,
            reason="cap-applicator pulls off the tube and loses body contact",
        )

        ctx.check(
            "doe-foot cap_applicator is one merged part (cap == dispense)",
            "cap" not in [p.name for p in object_model.parts]
            and cap.get_visual("cap") is not None
            and cap.get_visual("doe_foot_tip") is not None,
            details="merged cap_applicator missing a sub-visual",
        )
        ctx.check(
            "tube_to_cap is PRISMATIC about +Z",
            pull.articulation_type == ArticulationType.PRISMATIC
            and abs(pull.axis[2]) > 0.99,
            details=f"type={pull.articulation_type}, axis={pull.axis}",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap", elem_b="tube_body",
            reason="The cap socket is intentionally slipped over the tube rim at rest.",
        )
        ctx.allow_overlap(
            cap, base, elem_a="wand_stem", elem_b="tube_body",
            reason="The long applicator wand hangs down inside the tube bore.",
        )
        ctx.allow_overlap(
            cap, base, elem_a="doe_foot_tip", elem_b="gloss",
            reason="The doe-foot tip is seated in the gloss reservoir at rest.",
        )
        ctx.allow_overlap(
            cap, base, elem_a="doe_foot_tip", elem_b="tube_body",
            reason="The doe-foot tip dips into the lower gloss-filled bore at rest.",
        )
        # wand tip seated inside the tube at rest
        tip_rest = ctx.part_element_world_aabb(cap, elem="doe_foot_tip")
        ctx.check(
            "wand tip seated inside the tube at rest",
            tip_rest[1][2] < r.base_top_z,
            details=f"rest tip top z={tip_rest[1][2]:.4f}, body top={r.base_top_z:.4f}",
        )
        rest_cap_z = ctx.part_world_position(cap)[2]
        with ctx.pose({pull: pull.motion_limits.upper}):
            ext_cap_z = ctx.part_world_position(cap)[2]
            tip_ext = ctx.part_element_world_aabb(cap, elem="doe_foot_tip")
        ctx.check(
            "wand tip clears the tube mouth at full extension",
            tip_ext[0][2] > r.neck_top_z,
            details=f"extended tip bottom z={tip_ext[0][2]:.4f}, mouth={r.neck_top_z:.4f}",
        )
        ctx.check(
            "cap pulls straight up out of the tube",
            ext_cap_z > rest_cap_z + 0.04,
            details=f"rest cap z={rest_cap_z:.4f}, ext cap z={ext_cap_z:.4f}",
        )

    # ---- cap mechanism (Slot C) — only if not merged into doe-foot ----
    if r.cap_closure == "friction_pull_off":
        cap = object_model.get_part("cap")
        lift = object_model.get_articulation("cap_pull")
        ctx.allow_isolated_part(
            cap,
            reason="cap pulls off the tube and loses body contact",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_shell", elem_b="tube_body",
            reason="The cap is intentionally slipped over the tube base top (seated pull-off cap).",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_shell", elem_b="center_band",
            reason="The cap rim seats down onto the silver center band when closed.",
        )
        ctx.check(
            "cap_pull is PRISMATIC about +Z",
            lift.articulation_type == ArticulationType.PRISMATIC
            and abs(lift.axis[2]) > 0.99,
            details=f"type={lift.articulation_type}, axis={lift.axis}",
        )
        rest_z = ctx.part_world_position(cap)[2]
        rest_xy = ctx.part_world_position(cap)[:2]
        with ctx.pose({lift: 0.045}):
            up = ctx.part_world_position(cap)
        ctx.check(
            "cap pulls straight up off the tube",
            up[2] > rest_z + 0.040
            and abs(up[0] - rest_xy[0]) < 1e-6
            and abs(up[1] - rest_xy[1]) < 1e-6,
            details=f"rest_z={rest_z:.4f}, pulled_z={up[2]:.4f}",
        )

    elif r.cap_closure == "screw_thread_twist_off":
        cap = object_model.get_part("cap")
        screw = object_model.get_articulation("cap_screw")
        ctx.allow_isolated_part(
            cap,
            reason="screw cap twists off the tube and loses body contact",
        )
        neck_threads = base.get_visual("neck_threads")
        cap_threads = cap.get_visual("cap_threads")
        ctx.check(
            "neck has visible external thread ridges",
            neck_threads is not None,
            details="neck_threads visual missing from tube_base",
        )
        ctx.check(
            "cap has visible internal thread ridges",
            cap_threads is not None,
            details="cap_threads visual missing from cap",
        )
        ctx.check(
            "cap_screw is PRISMATIC about +Z (twist-off cap opens by lifting up)",
            screw.articulation_type == ArticulationType.PRISMATIC
            and abs(screw.axis[2]) > 0.99,
            details=f"type={screw.articulation_type}, axis={screw.axis}",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_threads", elem_b="neck_threads",
            reason="Internal cap threads mesh with external neck threads (screw interface).",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_threads", elem_b="tube_body",
            reason="Internal cap threads grip the round threaded neck (part of tube_body) — "
            "captured screw-thread fit.",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_shell", elem_b="tube_body",
            reason="Cap shell seats on the tube shoulder and encloses the threaded neck.",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_shell", elem_b="neck_threads",
            reason="Cap shell surrounds the external thread ridges on the neck.",
        )
        # screw cap opens by lifting straight up off the neck
        rest_z = ctx.part_world_position(cap)[2]
        rest_xy = ctx.part_world_position(cap)[:2]
        with ctx.pose({screw: screw.motion_limits.upper}):
            up = ctx.part_world_position(cap)
        ctx.check(
            "screw cap lifts straight up to open",
            up[2] > rest_z + 0.040
            and abs(up[0] - rest_xy[0]) < 1e-6
            and abs(up[1] - rest_xy[1]) < 1e-6,
            details=f"rest_z={rest_z:.4f}, lifted_z={up[2]:.4f}",
        )

    elif r.cap_closure == "hinged_flip_cap":
        cap = object_model.get_part("cap")
        hinge = object_model.get_articulation("cap_flip")
        ctx.allow_isolated_part(
            cap,
            reason="flip cap swings open on its hinge and loses body contact",
        )
        lug = base.get_visual("hinge_lug")
        knuckle = cap.get_visual("hinge_knuckle")
        ctx.check(
            "hinge lug exists on tube_base",
            lug is not None,
            details="no hinge_lug visual found",
        )
        ctx.check(
            "hinge knuckle exists on cap",
            knuckle is not None,
            details="no hinge_knuckle visual found",
        )
        ctx.check(
            "cap_flip is REVOLUTE about +X",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[0]) > 0.9,
            details=f"type={hinge.articulation_type}, axis={hinge.axis}",
        )
        ctx.allow_overlap(
            cap, base, elem_a="hinge_knuckle", elem_b="hinge_lug",
            reason="The hinge knuckle wraps around the hinge lug at the pivot point.",
        )
        ctx.allow_overlap(
            cap, base, elem_a="cap_shell", elem_b="tube_body",
            reason="The flip-cap shell seats onto the tube rim when closed.",
        )
        # closed cap centered over the tube; flips open (top rises, swings back)
        shell_rest = ctx.part_element_world_aabb(cap, elem="cap_shell")
        rest_cy = (shell_rest[0][1] + shell_rest[1][1]) / 2.0
        ctx.check(
            "closed cap shell is centered over the tube",
            abs(rest_cy) < 0.006,
            details=f"closed cap shell center Y={rest_cy:.4f}",
        )
        top0 = ctx.part_world_aabb(cap)[1][2]
        with ctx.pose({hinge: 2.0}):
            shell_open = ctx.part_element_world_aabb(cap, elem="cap_shell")
            top1 = ctx.part_world_aabb(cap)[1][2]
        open_cy = (shell_open[0][1] + shell_open[1][1]) / 2.0
        ctx.check(
            "cap flips open (shell swings backward)",
            open_cy < rest_cy - 0.010,
            details=f"rest center Y={rest_cy:.4f}, open center Y={open_cy:.4f}",
        )

    # ---- exactly one cap action; doe-foot has no separate cap ----
    part_names = [p.name for p in object_model.parts]
    if r.dispense_mech == "doe_foot_applicator":
        ctx.check(
            "doe-foot merges the cap (no separate cap part)",
            "cap" not in part_names,
            details=f"parts={part_names}",
        )

    # ---- at least one non-fixed joint exists ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed mechanism joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
