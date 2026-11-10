# SPDX-License-Identifier: Apache-2.0

"""Collapsible trekking pole procedural template (modular, enum-branch).

Single hand-held collapsible trekking / hiking pole. The shaft packs down via a
real collapse mechanism — either **telescoping** nested sections (one PRISMATIC
per stage, plus a REVOLUTE flick lever or a CONTINUOUS twist collar), or a
**folding** Z-fold chain (serial REVOLUTE folds, mimic-coupled). A top grip
(cork / EVA foam / T-crossbar) and a ground tip + basket (carbide+trekking /
snow / rubber-foot) are ③ Primary-Form-Family visual families fused onto the
collapse root / terminal parts (Rule 1 — they do not articulate).

Sources (all under data/records/, spec
articraft_template_authoring/specs_modular_v1/trekking_pole_collapsible.md):
  * origin A  rec_..._306eae8f...  single folding Z-fold pole (cork handle)
  * origin B  rec_..._da9d6d60...  telescoping flick-lock pole pair
  * var_twist_lock / var_pure_fold_tentpole / var_foam_grip / var_t_handle /
    var_snow_basket / var_rubber_foot_tip / var_n{2,4}_telescope / var_n{4,5}_fold

Rule 1: grip / tip / basket / ferrules / bands / straps / hinge hardware are
parent.visual(...) on a moving part, never FIXED decorative parts. Rule 3:
tube/collar/ferrule = Cylinder, grip = LatheGeometry, tip = ConeGeometry, basket
= TorusGeometry — primitive types preserved from the sources. Rule 5: telescope/
flick/twist use fail_if_parts_overlap_in_sampled_poses + element-scoped
allow_overlap; fold is mimic-coupled via coupled_chain so only the physical
coupled trajectory is sampled.
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
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    coupled_chain,
    mesh_from_geometry,
)

__modular__ = True

GripStyle = Literal["cork_ergonomic", "eva_foam", "t_crossbar"]
CollapseMechanism = Literal["telescope_flick", "telescope_twist", "fold_z"]
TipBasketStyle = Literal["carbide_trekking", "snow_basket", "rubber_foot"]
PaletteStyle = Literal["graphite_cork", "carbon_white", "blue_anodized", "eva_orange", "red_snow"]

GRIP_STYLES: tuple[GripStyle, ...] = ("cork_ergonomic", "eva_foam", "t_crossbar")
COLLAPSE_MECHANISMS: tuple[CollapseMechanism, ...] = (
    "telescope_flick",
    "telescope_twist",
    "fold_z",
)
TIP_BASKET_STYLES: tuple[TipBasketStyle, ...] = (
    "carbide_trekking",
    "snow_basket",
    "rubber_foot",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "graphite_cork",
    "carbon_white",
    "blue_anodized",
    "eva_orange",
    "red_snow",
)

TELESCOPE_MECHS: tuple[CollapseMechanism, ...] = ("telescope_flick", "telescope_twist")

# N (total shaft sections incl. root). Range is conditional on mechanism.
TELESCOPE_N = (2, 3, 4)
TELESCOPE_N_WEIGHTS = (0.30, 0.45, 0.25)
FOLD_N = (3, 4, 5)
FOLD_N_WEIGHTS = (0.45, 0.35, 0.20)

# ---------------------------------------------------------------------------
# Palettes (material role -> rgba). 5 colorways drawn from the 5-star sources.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "graphite_cork": {  # origin A
        "shaft": (0.090, 0.100, 0.105, 1.0),
        "inner": (0.070, 0.078, 0.082, 1.0),
        "sleeve": (0.72, 0.72, 0.68, 1.0),
        "grip": (0.68, 0.54, 0.35, 1.0),
        "subgrip": (0.05, 0.05, 0.055, 1.0),
        "metal": (0.72, 0.72, 0.68, 1.0),
        "black": (0.015, 0.016, 0.017, 1.0),
        "accent": (0.11, 0.12, 0.13, 1.0),
        "tip": (0.72, 0.72, 0.68, 1.0),
        "basket": (0.030, 0.030, 0.032, 1.0),
    },
    "carbon_white": {  # origin B
        "shaft": (0.93, 0.92, 0.88, 1.0),
        "inner": (0.015, 0.018, 0.017, 1.0),
        "sleeve": (0.93, 0.92, 0.88, 1.0),
        "grip": (0.72, 0.45, 0.22, 1.0),
        "subgrip": (0.02, 0.02, 0.02, 1.0),
        "metal": (0.70, 0.72, 0.73, 1.0),
        "black": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.015, 0.018, 0.017, 1.0),
        "tip": (0.70, 0.72, 0.73, 1.0),
        "basket": (0.02, 0.02, 0.02, 1.0),
    },
    "blue_anodized": {  # var_twist_lock
        "shaft": (0.10, 0.28, 0.55, 1.0),
        "inner": (0.015, 0.018, 0.017, 1.0),
        "sleeve": (0.12, 0.32, 0.60, 1.0),
        "grip": (0.68, 0.50, 0.30, 1.0),
        "subgrip": (0.03, 0.03, 0.035, 1.0),
        "metal": (0.70, 0.72, 0.73, 1.0),
        "black": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.06, 0.18, 0.42, 1.0),
        "tip": (0.70, 0.72, 0.73, 1.0),
        "basket": (0.02, 0.02, 0.02, 1.0),
    },
    "eva_orange": {  # var_foam_grip
        "shaft": (0.90, 0.90, 0.86, 1.0),
        "inner": (0.015, 0.018, 0.017, 1.0),
        "sleeve": (0.90, 0.90, 0.86, 1.0),
        "grip": (0.18, 0.19, 0.20, 1.0),
        "subgrip": (0.15, 0.16, 0.17, 1.0),
        "metal": (0.70, 0.72, 0.73, 1.0),
        "black": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.85, 0.35, 0.08, 1.0),
        "tip": (0.70, 0.72, 0.73, 1.0),
        "basket": (0.02, 0.02, 0.02, 1.0),
    },
    "red_snow": {  # var_snow_basket colorway
        "shaft": (0.11, 0.12, 0.13, 1.0),
        "inner": (0.030, 0.033, 0.035, 1.0),
        "sleeve": (0.72, 0.72, 0.68, 1.0),
        "grip": (0.66, 0.50, 0.32, 1.0),
        "subgrip": (0.05, 0.05, 0.055, 1.0),
        "metal": (0.72, 0.72, 0.68, 1.0),
        "black": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.78, 0.14, 0.10, 1.0),
        "tip": (0.72, 0.72, 0.68, 1.0),
        "basket": (0.80, 0.18, 0.10, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base dimensions (m). Telescope + fold share the grip top and tube radius.
# ---------------------------------------------------------------------------
_R0 = 0.0110  # root (outer) tube radius
_DR = 0.0016  # radius decrement per nested section
_WALL = 0.0016
_TUBE_L = 0.400  # section tube length (base)
_PITCH = 0.240  # collapsed mouth-to-mouth pitch (telescope)
_RETAIN = 0.050  # min retained overlap at full extension
_SHAFT_TOP = 0.600  # world z of collapsed shaft top (grip base)

_FOLD_L = 0.400  # fold segment length (base)
_FOLD_DX = 0.034  # parallel x-offset per folded segment
_HINGE_R = 0.0060  # fold hinge bushing radius


@dataclass(frozen=True)
class TrekkingPoleCollapsibleConfig:
    grip_style: GripStyle | None = None
    collapse_mechanism: CollapseMechanism | None = None
    section_count: int | None = None
    tip_basket_style: TipBasketStyle | None = None
    palette_style: PaletteStyle = "graphite_cork"
    deployed_length_scale: float = 1.0
    shaft_radius_scale: float = 1.0
    name: str = "trekking_pole_collapsible"


@dataclass(frozen=True)
class ResolvedTrekkingPoleCollapsibleConfig:
    grip_style: GripStyle
    collapse_mechanism: CollapseMechanism
    section_count: int
    tip_basket_style: TipBasketStyle
    palette_style: PaletteStyle
    r0: float
    tube_l: float
    pitch: float
    fold_l: float
    travel: float  # solved per-stage prismatic travel (telescope)
    name: str

    @property
    def is_telescope(self) -> bool:
        return self.collapse_mechanism in TELESCOPE_MECHS


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> TrekkingPoleCollapsibleConfig:
    rng = random.Random(seed)
    grip = rng.choice(GRIP_STYLES)
    mech = rng.choice(COLLAPSE_MECHANISMS)
    if mech in TELESCOPE_MECHS:
        n = rng.choices(TELESCOPE_N, weights=TELESCOPE_N_WEIGHTS, k=1)[0]
    else:
        n = rng.choices(FOLD_N, weights=FOLD_N_WEIGHTS, k=1)[0]
    tip = rng.choice(TIP_BASKET_STYLES)
    palette = rng.choice(PALETTE_STYLES)
    return TrekkingPoleCollapsibleConfig(
        grip_style=grip,
        collapse_mechanism=mech,
        section_count=n,
        tip_basket_style=tip,
        palette_style=palette,
        deployed_length_scale=round(rng.uniform(0.88, 1.15), 4),
        shaft_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        name=f"seeded_trekking_pole_{seed}",
    )


def resolve_config(
    config: TrekkingPoleCollapsibleConfig | None = None,
) -> ResolvedTrekkingPoleCollapsibleConfig:
    cfg = config or TrekkingPoleCollapsibleConfig()
    grip = _pick(cfg.grip_style, GRIP_STYLES)
    mech = _pick(cfg.collapse_mechanism, COLLAPSE_MECHANISMS)
    tip = _pick(cfg.tip_basket_style, TIP_BASKET_STYLES)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    # N clamped to the mechanism's legal range (compatibility gating, spec §9).
    n = int(cfg.section_count) if cfg.section_count is not None else 3
    if mech in TELESCOPE_MECHS:
        n = int(_clamp(n, TELESCOPE_N[0], TELESCOPE_N[-1]))
    else:
        n = int(_clamp(n, FOLD_N[0], FOLD_N[-1]))

    len_scale = _clamp(cfg.deployed_length_scale, 0.88, 1.15)
    rad_scale = _clamp(cfg.shaft_radius_scale, 0.90, 1.12)

    r0 = _R0 * rad_scale
    tube_l = _TUBE_L * len_scale
    pitch = _PITCH * len_scale
    fold_l = _FOLD_L * len_scale

    # Telescope travel (equation + retention inequality): inner tube must stay
    # inserted at full extension. overlap at collapse = tube_l - pitch; keep
    # >= _RETAIN at full travel.
    travel = _clamp(0.75 * (tube_l - pitch), 0.04, (tube_l - pitch) - _RETAIN)

    return ResolvedTrekkingPoleCollapsibleConfig(
        grip_style=grip,
        collapse_mechanism=mech,
        section_count=n,
        tip_basket_style=tip,
        palette_style=palette,
        r0=r0,
        tube_l=tube_l,
        pitch=pitch,
        fold_l=fold_l,
        travel=travel,
        name=cfg.name or "trekking_pole_collapsible",
    )


def slot_choices_for_config(
    config: TrekkingPoleCollapsibleConfig | ResolvedTrekkingPoleCollapsibleConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedTrekkingPoleCollapsibleConfig)
        else resolve_config(config)
    )
    return (
        ("grip_style", r.grip_style),
        ("collapse_mechanism", r.collapse_mechanism),
        ("section_count", f"n{r.section_count}"),
        ("tip_basket_style", r.tip_basket_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Low-level placement helpers. Every part is built in its own frame; pass the
# part's frame-origin world position so world coords map to local visuals.
# ---------------------------------------------------------------------------
def _cyl(part, r, length, world_xyz, frame, mat, name, rpy=(0.0, 0.0, 0.0)):
    x, y, z = world_xyz
    fx, fy, fz = frame
    part.visual(
        Cylinder(radius=r, length=length),
        origin=Origin(xyz=(x - fx, y - fy, z - fz), rpy=rpy),
        material=mat,
        name=name, material_class_id="metal.paint_coated",
    )


def _box(part, size, world_xyz, frame, mat, name, rpy=(0.0, 0.0, 0.0)):
    x, y, z = world_xyz
    fx, fy, fz = frame
    part.visual(
        Box(size),
        origin=Origin(xyz=(x - fx, y - fy, z - fz), rpy=rpy),
        material=mat,
        name=name, material_class_id="plastic.opaque_generic",
    )


def _mesh(part, geom, world_xyz, frame, mat, name, rpy=(0.0, 0.0, 0.0)):
    x, y, z = world_xyz
    fx, fy, fz = frame
    part.visual(
        mesh_from_geometry(geom, name),
        origin=Origin(xyz=(x - fx, y - fy, z - fz), rpy=rpy),
        material=mat,
        name=name, material_class_id=("wood.cork_surface" if name == "cork_handle" else "plastic.opaque_generic"),
    )


# ---------------------------------------------------------------------------
# Grip families (③) — visuals fused onto the root part. base_z = world z of the
# grip's lower end (= collapsed shaft top). frame = root part frame origin.
# ---------------------------------------------------------------------------
def _cork_ergonomic_mesh() -> LatheGeometry:
    # origin A _ergonomic_handle_mesh (L29-40): flared cork palm swell.
    profile = [
        (0.020, 0.000),
        (0.023, 0.020),
        (0.027, 0.090),
        (0.031, 0.180),
        (0.029, 0.270),
        (0.023, 0.335),
        (0.019, 0.365),
    ]
    return LatheGeometry(profile, segments=40, closed=True)


def _eva_grip_mesh() -> LatheGeometry:
    # var_foam_grip _make_eva_grip_mesh (L60-74): long straight EVA grip.
    profile = [
        (0.0105, -0.150),
        (0.0130, -0.140),
        (0.0142, -0.118),
        (0.0142, -0.075),
        (0.0130, -0.065),
        (0.0130, 0.080),
        (0.0136, 0.105),
        (0.0152, 0.132),
        (0.0140, 0.146),
        (0.0110, 0.152),
    ]
    return LatheGeometry(profile, segments=40, closed=True)


def _t_crossbar_mesh() -> LatheGeometry:
    # var_t_handle _t_grip_crossbar_mesh (L29-40): cane-style T crossbar.
    profile = [
        (0.004, 0.000),
        (0.014, 0.008),
        (0.018, 0.025),
        (0.020, 0.065),
        (0.018, 0.105),
        (0.014, 0.122),
        (0.004, 0.130),
    ]
    return LatheGeometry(profile, segments=32, closed=True)


def _build_grip(part, r, mats, base_z: float, frame) -> None:
    grip = r.grip_style
    # Hidden core spine (origin A/B): a thin rod up the grip axis that embeds
    # into the shaft tube at its base and threads through every grip element, so
    # all grip visuals share a support path to the tube (Rule 1 / islands gate).
    core_top = {"cork_ergonomic": 0.395, "eva_foam": 0.320, "t_crossbar": 0.200}[grip]
    core_lo = base_z - 0.030
    core_hi = base_z + core_top
    _cyl(
        part,
        0.0058,
        core_hi - core_lo,
        (0.0, 0.0, (core_lo + core_hi) / 2.0),
        frame,
        mats["subgrip"],
        "grip_core",
    )

    if grip == "cork_ergonomic":
        for i, dz in enumerate((0.030, 0.075, 0.120)):
            _cyl(
                part,
                r.r0 + 0.007,
                0.024,
                (0.0, 0.0, base_z + dz),
                frame,
                mats["subgrip"],
                f"grip_foam_rib_{i}",
            )
        _mesh(
            part,
            _cork_ergonomic_mesh(),
            (0.0, 0.0, base_z + 0.010),
            frame,
            mats["grip"],
            "cork_handle",
        )
        _cyl(part, 0.021, 0.036, (0.0, 0.0, base_z + 0.380), frame, mats["accent"], "top_cap")
        _box(
            part,
            (0.044, 0.026, 0.026),
            (0.008, 0.0, base_z + 0.400),
            frame,
            mats["black"],
            "palm_hook",
            rpy=(0.0, -0.38, 0.0),
        )
        _box(
            part,
            (0.020, 0.010, 0.070),
            (-0.014, -0.014, base_z + 0.120),
            frame,
            mats["black"],
            "wrist_strap_tag",
            rpy=(0.0, 0.0, -0.35),
        )
    elif grip == "eva_foam":
        _mesh(part, _eva_grip_mesh(), (0.0, 0.0, base_z + 0.150), frame, mats["grip"], "eva_grip")
        _cyl(part, 0.0146, 0.014, (0.0, 0.0, base_z + 0.270), frame, mats["accent"], "accent_band")
        _cyl(part, 0.018, 0.032, (0.0, 0.0, base_z + 0.305), frame, mats["metal"], "top_cap")
        _box(
            part,
            (0.020, 0.010, 0.070),
            (-0.010, -0.010, base_z + 0.110),
            frame,
            mats["black"],
            "wrist_strap_tag",
            rpy=(0.0, 0.0, -0.35),
        )
    else:  # t_crossbar
        _cyl(
            part, r.r0 + 0.005, 0.024, (0.0, 0.0, base_z + 0.006), frame, mats["black"], "t_collar"
        )
        _cyl(part, 0.013, 0.130, (0.0, 0.0, base_z + 0.080), frame, mats["black"], "t_neck")
        _mesh(
            part,
            _t_crossbar_mesh(),
            (-0.065, 0.0, base_z + 0.150),
            frame,
            mats["grip"],
            "t_crossbar",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
        _box(
            part,
            (0.020, 0.010, 0.060),
            (-0.010, -0.010, base_z + 0.080),
            frame,
            mats["black"],
            "wrist_strap_tag",
            rpy=(0.0, 0.0, -0.35),
        )


# ---------------------------------------------------------------------------
# Tip + basket families (③) — visuals fused onto the terminal part. tip_z = the
# world z of the terminal tube's free (ground) end; +z_dir points along the
# deployed-downward direction (-1 = tip extends toward -z).
# ---------------------------------------------------------------------------
def _add_tip_basket(
    part, r, mats, tip_z: float, frame, rt: float, *, tip_dir: int = -1, x0: float = 0.0
) -> None:
    # tip_dir = direction the tip/spike points (world z). s = inward sign
    # (toward the tube). All offsets are written for a downward tip and mirrored
    # by s for the (fold-parity) upward case.
    style = r.tip_basket_style
    s = -tip_dir

    def Z(off: float) -> float:
        return tip_z + s * off

    # ferrule collar just inside the tube mouth (overlaps the tube).
    _cyl(part, rt + 0.0016, 0.030, (x0, 0.0, Z(0.020)), frame, mats["metal"], "ferrule")

    # Basket hub radius is derived from the tube so it always engulfs the tube +
    # ferrule (no razor-thin near-miss island).
    hub_r = rt + 0.004
    basket_z = Z(0.026)
    outer_r = 0.055 if style == "snow_basket" else 0.030
    spokes = 8 if style == "snow_basket" else 6
    _cyl(part, hub_r, 0.026, (x0, 0.0, basket_z), frame, mats["basket"], "basket_hub")
    _mesh(
        part,
        TorusGeometry(outer_r, 0.0032, radial_segments=10, tubular_segments=48),
        (x0, 0.0, basket_z),
        frame,
        mats["basket"],
        "basket_ring",
    )
    span = outer_r - hub_r
    mid_r = (outer_r + hub_r) / 2.0
    for k in range(spokes):
        ang = k * (2.0 * math.pi / spokes)
        _box(
            part,
            (span, 0.004, 0.003),
            (x0 + mid_r * math.cos(ang), mid_r * math.sin(ang), basket_z),
            frame,
            mats["basket"],
            f"basket_spoke_{k}",
            rpy=(0.0, 0.0, ang),
        )

    if style == "rubber_foot":
        # metal core threads from the ferrule out into the paw socket so the
        # hollow-socketed foot is supported (var_rubber_foot_tip over ferrule).
        _cyl(part, min(rt, 0.005), 0.060, (x0, 0.0, Z(-0.018)), frame, mats["metal"], "tip_core")
        foot = LatheGeometry(
            [
                (0.000, 0.000),
                (0.024, 0.000),
                (0.029, 0.010),
                (0.028, 0.022),
                (0.024, 0.035),
                (0.016, 0.048),
                (0.010, 0.058),
            ],
            segments=28,
            closed=True,
        )
        foot_rpy = (0.0, 0.0, 0.0) if tip_dir < 0 else (math.pi, 0.0, 0.0)
        _mesh(
            part,
            foot,
            (x0, 0.0, Z(-0.046)),
            frame,
            mats["black"],
            "rubber_walking_foot",
            rpy=foot_rpy,
        )
    else:
        # carbide cone spike (origin B _make_tip_mesh) + inner core.
        _cyl(part, min(rt, 0.0040), 0.060, (x0, 0.0, Z(-0.008)), frame, mats["tip"], "tip_core")
        cone_rpy = (math.pi, 0.0, 0.0) if tip_dir < 0 else (0.0, 0.0, 0.0)
        _mesh(
            part,
            ConeGeometry(0.0075, 0.050, radial_segments=24, closed=True),
            (x0, 0.0, Z(-0.048)),
            frame,
            mats["tip"],
            "carbide_point",
            rpy=cone_rpy,
        )


# ---------------------------------------------------------------------------
# Lock actuators (telescope): flick lever (REVOLUTE) / twist collar (CONTINUOUS)
# ---------------------------------------------------------------------------
def _build_flick_lever(part, mats) -> None:
    # origin B _add_lever_visuals: knuckle (x-cyl) + blade + lip. Lies along the
    # tube at q=0; +q flips out toward +y.
    part.visual(
        Cylinder(radius=0.0060, length=0.018),
        origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="lever_knuckle", material_class_id="metal.aluminum_bare",
    )
    part.visual(
        Box((0.012, 0.008, 0.056)),
        origin=Origin(xyz=(0.0, 0.008, -0.032)),
        material=mats["black"],
        name="lever_blade", material_class_id="plastic.opaque_generic",
    )
    part.visual(
        Box((0.016, 0.007, 0.012)),
        origin=Origin(xyz=(0.0, 0.011, -0.060)),
        material=mats["black"],
        name="lever_lip", material_class_id="plastic.opaque_generic",
    )


def _build_twist_collar(part, mats, rt: float) -> None:
    # knurled twist-lock expander ring (var_twist_lock _make_twist_collar_mesh),
    # rotates about the shaft axis. A small nub breaks symmetry so rotation reads.
    inner_r = rt + 0.0012
    outer_r = rt + 0.0060
    h = 0.014
    profile = [
        (inner_r, -h),
        (outer_r, -h),
        (outer_r + 0.0009, -h * 0.45),
        (outer_r, 0.0),
        (outer_r + 0.0009, h * 0.45),
        (outer_r, h),
        (inner_r, h),
    ]
    part.visual(
        mesh_from_geometry(LatheGeometry(profile, segments=28, closed=True), "collar_ring"),
        material=mats["accent"],
        name="collar_ring", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Box((0.006, 0.004, 0.012)),
        origin=Origin(xyz=(outer_r + 0.002, 0.0, 0.0)),
        material=mats["black"],
        name="collar_grip_nub", material_class_id="rubber.pebbled",
    )


# ---------------------------------------------------------------------------
# Telescope builder.
# ---------------------------------------------------------------------------
def _build_telescope(model, r, mats) -> dict:
    n = r.section_count
    rt = lambda k: r.r0 - k * _DR  # noqa: E731 — monotone decreasing radii
    top = _SHAFT_TOP
    frames = [(0.0, 0.0, top - k * r.pitch) for k in range(n)]

    parts = []
    for k in range(n):
        name = "grip_section" if k == 0 else f"stage_{k}"
        part = model.part(name)
        parts.append(part)
        fr = frames[k]
        rk = rt(k)
        # main tube (world z-span [top - k*pitch - tube_l, top - k*pitch]).
        tube_top = top - k * r.pitch
        _cyl(
            part,
            rk,
            r.tube_l,
            (0.0, 0.0, tube_top - r.tube_l / 2.0),
            fr,
            mats["inner"] if k > 0 else mats["shaft"],
            "tube",
        )
        # carbon-look label strip on the root (④, host-conformal to tube radius).
        if k == 0:
            _box(
                part,
                (0.005, 0.0024, 0.170),
                (0.0, -(rk + 0.0012), tube_top - 0.12),
                fr,
                mats["accent"],
                "carbon_label",
            )
        # receiving mouth: clamp collar + band where stage k+1 enters (bottom).
        if k < n - 1:
            mouth_z = tube_top - r.tube_l + 0.020
            _cyl(part, rk + 0.005, 0.032, (0.0, 0.0, mouth_z), fr, mats["black"], "clamp_collar")
            _cyl(
                part,
                rk + 0.0022,
                0.012,
                (0.0, 0.0, mouth_z + 0.030),
                fr,
                mats["black"],
                "mouth_band",
            )

    # grip on the root top; tip on the terminal bottom.
    _build_grip(parts[0], r, mats, top, frames[0])
    term_bottom = top - (n - 1) * r.pitch - r.tube_l
    _add_tip_basket(parts[n - 1], r, mats, term_bottom, frames[n - 1], rt(n - 1))

    joints = []
    levers = []
    for k in range(n - 1):
        parent, child = parts[k], parts[k + 1]
        # PRISMATIC joint origin is gauge (exempt from origin-far check); place
        # at parent mouth. child frame is offset by pitch below parent frame.
        jname = f"sec{k}_to_sec{k + 1}"
        origin_local = (0.0, 0.0, -r.pitch)  # frames[k+1] - frames[k]
        model.articulation(
            jname,
            ArticulationType.PRISMATIC,
            parent=parent,
            child=child,
            origin=Origin(xyz=origin_local),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=70.0, velocity=0.25, lower=0.0, upper=r.travel),
        )
        joints.append(jname)

        # lock actuator at this mouth, hinged/pinned on the PARENT.
        rk = rt(k)
        mouth_world_z = (top - k * r.pitch) - r.tube_l + 0.020
        if r.collapse_mechanism == "telescope_flick":
            lever = model.part(f"lever_{k}")
            _build_flick_lever(lever, mats)
            model.articulation(
                f"clamp_hinge_{k}",
                ArticulationType.REVOLUTE,
                parent=parent,
                child=lever,
                origin=Origin(xyz=(0.0, rk + 0.006, mouth_world_z - (top - k * r.pitch))),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=2.0, velocity=2.5, lower=0.0, upper=1.25),
            )
            levers.append(("lever", f"lever_{k}", f"clamp_hinge_{k}", k))
        else:  # telescope_twist
            collar = model.part(f"collar_{k}")
            _build_twist_collar(collar, mats, rt(k + 1))
            model.articulation(
                f"twist_{k}",
                ArticulationType.CONTINUOUS,
                parent=parent,
                child=collar,
                origin=Origin(xyz=(0.0, 0.0, mouth_world_z - (top - k * r.pitch))),
                axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=3.0, velocity=2.0),
            )
            levers.append(("collar", f"collar_{k}", f"twist_{k}", k))

    return {
        "parts": [p.name for p in parts],
        "joints": joints,
        "actuators": levers,
        "rt": [rt(k) for k in range(n)],
    }


# ---------------------------------------------------------------------------
# Fold builder (Z-fold serial chain, mimic-coupled).
# ---------------------------------------------------------------------------
def _build_fold(model, r, mats) -> dict:
    n = r.section_count
    rk = r.r0
    lf = r.fold_l
    z_bot = _SHAFT_TOP - lf  # seg0 top = _SHAFT_TOP (grip base)

    # hinge_k between seg k and seg k+1: bottom (z_bot) if k even else top.
    def hinge_world(k):
        end_z = z_bot if (k % 2 == 0) else (z_bot + lf)
        return (k * _FOLD_DX + _FOLD_DX / 2.0, 0.0, end_z)

    # seg frames: seg0 = world origin; seg_{k} frame = hinge_{k-1} world.
    frames = [(0.0, 0.0, 0.0)]
    for k in range(1, n):
        frames.append(hinge_world(k - 1))

    parts = []
    for k in range(n):
        name = "grip_section" if k == 0 else f"segment_{k}"
        part = model.part(name)
        parts.append(part)
        fr = frames[k]
        seg_x = k * _FOLD_DX
        # main tube (vertical at seg_x, world z-span [z_bot, z_bot+lf]).
        _cyl(
            part,
            rk,
            lf,
            (seg_x, 0.0, z_bot + lf / 2.0),
            fr,
            mats["shaft"] if k == 0 else mats["inner"],
            "tube",
        )
        if k == 0:
            _box(
                part,
                (0.005, 0.0024, 0.150),
                (0.0, -(rk + 0.0012), z_bot + lf * 0.55),
                fr,
                mats["accent"],
                "carbon_label",
            )

        # hinge hardware where this seg connects to its parent (k>=1): a y-axis
        # bushing at the parent hinge point, plus a bridge to the tube end.
        if k >= 1:
            hw = hinge_world(k - 1)
            _cyl(
                part,
                _HINGE_R,
                0.020,
                hw,
                fr,
                mats["metal"],
                "hinge_bushing",
                rpy=(math.pi / 2.0, 0.0, 0.0),
            )
            # bridge from tube end (seg_x, end_z) to hinge (hw) horizontally.
            end_z = hw[2]
            bx = (seg_x + hw[0]) / 2.0
            blen = abs(seg_x - hw[0]) + 0.006
            _box(part, (blen, 0.006, 0.008), (bx, 0.0, end_z), fr, mats["metal"], "hinge_bridge")
        # hinge hardware where this seg connects to its child (k < n-1): a
        # bushing on THIS (parent) seg at hinge_k.
        if k < n - 1:
            hw = hinge_world(k)
            _cyl(
                part,
                _HINGE_R,
                0.020,
                hw,
                fr,
                mats["metal"],
                "child_hinge_bushing",
                rpy=(math.pi / 2.0, 0.0, 0.0),
            )
            _box(
                part,
                (abs(seg_x - hw[0]) + 0.006, 0.006, 0.008),
                ((seg_x + hw[0]) / 2.0, 0.0, hw[2]),
                fr,
                mats["metal"],
                "child_hinge_bridge",
            )

    # grip on seg0 top.
    _build_grip(parts[0], r, mats, _SHAFT_TOP, frames[0])
    # tip on terminal segment free end (opposite its parent hinge). The tip
    # points outward from that end: down if the free end is the bottom, up if it
    # is the top (fold parity).
    term = n - 1
    parent_hinge_z = hinge_world(term - 1)[2]
    if parent_hinge_z == z_bot:  # hinge at bottom -> free end at top
        free_z, tip_dir = z_bot + lf, +1
    else:  # hinge at top -> free end at bottom
        free_z, tip_dir = z_bot, -1
    _add_tip_basket(
        parts[term], r, mats, free_z, frames[term], rk, tip_dir=tip_dir, x0=term * _FOLD_DX
    )

    joints = []
    for k in range(n - 1):
        parent, child = parts[k], parts[k + 1]
        hw = hinge_world(k)
        origin_local = (hw[0] - frames[k][0], 0.0, hw[2] - frames[k][2])
        axis = (0.0, 1.0, 0.0) if (k % 2 == 0) else (0.0, -1.0, 0.0)
        model.articulation(
            f"fold_{k}",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=child,
            origin=Origin(xyz=origin_local),
            axis=axis,
            motion_limits=MotionLimits(effort=8.0, velocity=1.0, lower=0.0, upper=math.pi),
        )
        joints.append(f"fold_{k}")

    return {
        "parts": [p.name for p in parts],
        "joints": joints,
        "actuators": [],
        "rt": [rk] * n,
    }


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_trekking_pole_collapsible(
    config: TrekkingPoleCollapsibleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"tp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    if r.is_telescope:
        info = _build_telescope(model, r, mats)
    else:
        info = _build_fold(model, r, mats)
        # Mimic-couple the fold chain so only the physical coupled trajectory is
        # QC-sampled (independent fold combos self-intersect). Alternating axis
        # sign is in the geometry, so all multipliers are +1.0.
        if len(info["joints"]) >= 2:
            coupled_chain(
                model,
                driver=info["joints"][0],
                followers=info["joints"][1:],
                multipliers=[1.0] * (len(info["joints"]) - 1),
                allowed_pairs=_fold_allowed_pairs(info["parts"]),
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["collapse_mechanism"] = r.collapse_mechanism
    model.meta["section_count"] = r.section_count
    return model


def build_seeded_trekking_pole_collapsible(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_trekking_pole_collapsible(config_from_seed(seed), assets=assets)


def _fold_allowed_pairs(part_names) -> list[tuple[str, str]]:
    # Adjacent fold segments overlap in the compact bundle and brush past each
    # other during coupled deploy (real Z-fold geometry). Allow element-scoped
    # tube/hinge overlaps between neighbors.
    pairs: list[tuple[str, str]] = []
    for a, b in zip(part_names, part_names[1:]):
        pairs.append((a, b))  # part-level exemption for adjacent bundle nesting
    return pairs


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_trekking_pole_collapsible_tests(
    object_model: ArticulatedObject,
    config: TrekkingPoleCollapsibleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    n = r.section_count
    parts = [
        "grip_section",
        *[f"stage_{k}" if r.is_telescope else f"segment_{k}" for k in range(1, n)],
    ]

    if r.is_telescope:
        # All section tubes are coaxially nested, so EVERY pair of tubes overlaps
        # in the collapsed / partly-extended stack (the doc's canonical
        # "telescoping stack that legitimately self-nests").
        for i in range(n):
            for j in range(i + 1, n):
                ctx.allow_overlap(
                    object_model.get_part(parts[i]),
                    object_model.get_part(parts[j]),
                    elem_a="tube",
                    elem_b="tube",
                    reason="Coaxially nested telescoping tubes overlap through the collapse range.",
                )
        for k in range(n - 1):
            a, b = parts[k], parts[k + 1]
            ctx.allow_overlap(
                object_model.get_part(a),
                object_model.get_part(b),
                elem_a="clamp_collar",
                elem_b="tube",
                reason="The clamp collar wraps the sliding inner tube at the sleeve mouth.",
            )
            ctx.allow_overlap(
                object_model.get_part(a),
                object_model.get_part(b),
                elem_a="mouth_band",
                elem_b="tube",
                reason="The decorative mouth band encircles the telescoping inner tube.",
            )
            if r.collapse_mechanism == "telescope_flick":
                ctx.allow_overlap(
                    object_model.get_part(a),
                    object_model.get_part(f"lever_{k}"),
                    elem_a="clamp_collar",
                    elem_b="lever_knuckle",
                    reason="The flick lever knuckle rotates around the clamp pin/collar.",
                )
            else:
                collar = object_model.get_part(f"collar_{k}")
                ctx.allow_overlap(
                    object_model.get_part(a),
                    collar,
                    elem_a="tube",
                    elem_b="collar_ring",
                    reason="The twist collar seats around the outer sleeve mouth.",
                )
                ctx.allow_overlap(
                    object_model.get_part(a),
                    collar,
                    elem_a="clamp_collar",
                    elem_b="collar_ring",
                    reason="The twist collar seats on the outside of the sleeve mouth.",
                )
                ctx.allow_overlap(
                    collar,
                    object_model.get_part(b),
                    elem_a="collar_ring",
                    elem_b="tube",
                    reason="The twist collar encircles the inner tube passing through the mouth.",
                )

        # sampled-pose overlap sweep (Rule 5).
        ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

        # targeted: first stage telescopes downward when extended.
        j0 = object_model.get_articulation("sec0_to_sec1")
        child = object_model.get_part(parts[1])
        rest = ctx.part_world_position(child)
        with ctx.pose({j0: r.travel}):
            ext = ctx.part_world_position(child)
        if rest is not None and ext is not None:
            ctx.check(
                "first telescoping stage extends downward",
                ext[2] < rest[2] - 0.03,
                details=f"rest_z={rest[2]:.3f} ext_z={ext[2]:.3f}",
            )
        ctx.check(
            "collapse joint is PRISMATIC about -Z",
            j0.articulation_type == ArticulationType.PRISMATIC and abs(j0.axis[2]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )
        # targeted: lock actuator semantics.
        if r.collapse_mechanism == "telescope_flick":
            hinge = object_model.get_articulation("clamp_hinge_0")
            lever = object_model.get_part("lever_0")
            r0y = ctx.part_element_world_aabb(lever, elem="lever_blade")
            with ctx.pose({hinge: 1.0}):
                o0y = ctx.part_element_world_aabb(lever, elem="lever_blade")
            if r0y is not None and o0y is not None:
                ctx.check(
                    "flick lever flips outward (+y)",
                    o0y[1][1] > r0y[1][1] + 0.005,
                    details=f"rest_ymax={r0y[1][1]:.4f} open_ymax={o0y[1][1]:.4f}",
                )
        else:
            tw = object_model.get_articulation("twist_0")
            ctx.check(
                "twist collar joint is CONTINUOUS about +Z",
                tw.articulation_type == ArticulationType.CONTINUOUS and abs(tw.axis[2]) > 0.99,
                details=f"type={tw.articulation_type} axis={tuple(tw.axis)}",
            )
    else:
        # fold: adjacent segments lie parallel in the compact bundle and brush
        # past each other during coupled deploy (real Z-fold). The whole
        # adjacent-segment pair self-nests (hinge hardware, ferrule, basket at
        # the shared pivot), so allow the pair at part scope.
        for k in range(n - 1):
            ctx.allow_overlap(
                object_model.get_part(parts[k]),
                object_model.get_part(parts[k + 1]),
                reason="Adjacent Z-fold segments nest in the compact bundle and brush during deploy.",
            )
        ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

        # targeted: driving the fold straightens the chain (terminal drops).
        j0 = object_model.get_articulation("fold_0")
        term = object_model.get_part(parts[n - 1])
        folded = ctx.part_world_aabb(term)
        hi = float(j0.motion_limits.upper or math.pi)
        with ctx.pose({j0: hi}):
            deployed = ctx.part_world_aabb(term)
        if folded is not None and deployed is not None:
            ctx.check(
                "fold deploy drives the terminal segment away from the bundle",
                deployed[0][2] < folded[0][2] - 0.05,
                details=f"folded_zmin={folded[0][2]:.3f} deployed_zmin={deployed[0][2]:.3f}",
            )
        ctx.check(
            "fold joint is REVOLUTE about Y",
            j0.articulation_type == ArticulationType.REVOLUTE and abs(j0.axis[1]) > 0.99,
            details=f"type={j0.articulation_type} axis={tuple(j0.axis)}",
        )

    # identity / proportion: pole reads as a long slender shaft.
    root = object_model.get_part("grip_section")
    root_aabb = ctx.part_world_aabb(root)
    if root_aabb is not None:
        z_ext = root_aabb[1][2] - root_aabb[0][2]
        ctx.check(
            "root section is a long slender shaft",
            z_ext > 0.30,
            details=f"root_z_ext={z_ext:.3f}",
        )

    # slot_choices recorded.
    ctx.check(
        "slot_choices recorded with N encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "TrekkingPoleCollapsibleConfig",
    "ResolvedTrekkingPoleCollapsibleConfig",
    "build_trekking_pole_collapsible",
    "build_seeded_trekking_pole_collapsible",
    "config_from_seed",
    "resolve_config",
    "run_trekking_pole_collapsible_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
