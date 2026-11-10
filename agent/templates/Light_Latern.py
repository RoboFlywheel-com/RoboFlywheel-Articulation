# SPDX-License-Identifier: Apache-2.0

"""Hurricane (kerosene) lantern modular template.

A hand-carried oil lantern: a grounded ``lantern_body`` root carrying a stepped
fuel fount, a translucent light chamber (barrel glass globe / square candle-panel
cage / wire railroad cage), an internal burner + wick + flame, a top vent cap,
and a single swinging carry handle. Two non-FIXED joints define the motion
identity (both captured-pin/stem joints, so they are grandfathered — no
MatingContract, guarded by element-scoped ``allow_overlap`` mirroring every
5-star source record):

  * the carry handle's REVOLUTE about the body (axis / range set by Slot C);
  * ``fount_to_wick_knob`` CONTINUOUS wick-adjust knob (local +Y, all variants).

Structure (pattern = ``mixed``): one root ``lantern_body`` part with three named
module slots attaching as parallel children / inline visuals (cushion.py style),
plus a side-guard multiplicity axis:

  * ``type`` (Slot A, 4): light chamber + draft structure —
    hurricane_side_tube / railroad_cage / candle_panel / tubular_coldblast.
  * ``cap`` (Slot B, 4): top vent crown —
    domed_vent_cap / flat_pierced_crown / conical_louver / peaked_roof.
  * ``carry`` (Slot C, 4): the lone swinging handle (owns the 2nd non-FIXED
    REVOLUTE) — swinging_bail / top_swivel_ring / folding_side_strap /
    swivel_hook_hanger.
  * ``guard_count`` (N in [2,16]): a multiplicity axis — N equiangular FIXED
    guard members (curved air tubes for side_tube, straight lugged cage wires +
    rings for railroad_cage). Inline visuals (Rule 1, no joint). Disabled for
    candle_panel (square chamber has no circumferential guard seat) and fixed at
    the cold-blast pair for tubular_coldblast.

Sourced from ``articraft_template_authoring/specs_modular_v1/Light_Latern.md``
and the ``Light/Latern`` 5-star pool (1 parent baseline 5da4cb46 + 12 slot-fork
variants), rooted in the ``articraft_data`` repo.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from functools import reduce
from typing import Literal

import cadquery as cq

from sdk import (
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
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

TypeStyle = Literal["hurricane_side_tube", "railroad_cage", "candle_panel", "tubular_coldblast"]
CapStyle = Literal["domed_vent_cap", "flat_pierced_crown", "conical_louver", "peaked_roof"]
CarryStyle = Literal["swinging_bail", "top_swivel_ring", "folding_side_strap", "swivel_hook_hanger"]
PaletteStyle = Literal[
    "classic_green",
    "barn_red",
    "galvanized_steel",
    "matte_black",
    "weathered_copper",
    "polished_brass",
]

TYPE_STYLES: tuple[TypeStyle, ...] = (
    "hurricane_side_tube",
    "railroad_cage",
    "candle_panel",
    "tubular_coldblast",
)
CAP_STYLES: tuple[CapStyle, ...] = (
    "domed_vent_cap",
    "flat_pierced_crown",
    "conical_louver",
    "peaked_roof",
)
CARRY_STYLES: tuple[CarryStyle, ...] = (
    "swinging_bail",
    "top_swivel_ring",
    "folding_side_strap",
    "swivel_hook_hanger",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_green",
    "barn_red",
    "galvanized_steel",
    "matte_black",
    "weathered_copper",
    "polished_brass",
)

# Types whose round globe accepts an equiangular guard multiplicity axis.
GUARD_TYPES: tuple[TypeStyle, ...] = ("hurricane_side_tube", "railroad_cage")

N_MIN = 2
N_MAX = 16
# Small N is the common real lantern; dense cages are a rarer tail.
GUARD_N_CHOICES = (2, 3, 4, 5, 6, 8, 10, 12, 16)
GUARD_N_WEIGHTS = (0.20, 0.14, 0.14, 0.12, 0.12, 0.10, 0.08, 0.06, 0.04)

VENT_MIN = 8
VENT_MAX = 16

# Realistic lantern colorways. Every .visual material is driven off mats[...]
# resolved from one of these styles.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_green": {
        "body": (0.05, 0.28, 0.12, 1.0),
        "accent": (0.80, 0.64, 0.30, 1.0),
        "glass": (0.82, 0.88, 0.90, 0.28),
        "burner": (0.30, 0.30, 0.32, 1.0),
        "flame": (1.0, 0.58, 0.12, 1.0),
        "vent_dark": (0.05, 0.06, 0.05, 1.0),
    },
    "barn_red": {
        "body": (0.55, 0.09, 0.07, 1.0),
        "accent": (0.82, 0.66, 0.32, 1.0),
        "glass": (0.86, 0.86, 0.84, 0.28),
        "burner": (0.28, 0.27, 0.27, 1.0),
        "flame": (1.0, 0.60, 0.14, 1.0),
        "vent_dark": (0.07, 0.04, 0.04, 1.0),
    },
    "galvanized_steel": {
        "body": (0.62, 0.64, 0.66, 1.0),
        "accent": (0.78, 0.79, 0.80, 1.0),
        "glass": (0.84, 0.90, 0.92, 0.26),
        "burner": (0.34, 0.34, 0.36, 1.0),
        "flame": (1.0, 0.62, 0.16, 1.0),
        "vent_dark": (0.10, 0.11, 0.12, 1.0),
    },
    "matte_black": {
        "body": (0.07, 0.07, 0.08, 1.0),
        "accent": (0.80, 0.64, 0.30, 1.0),
        "glass": (0.80, 0.86, 0.90, 0.30),
        "burner": (0.36, 0.36, 0.38, 1.0),
        "flame": (1.0, 0.58, 0.12, 1.0),
        "vent_dark": (0.03, 0.03, 0.03, 1.0),
    },
    "weathered_copper": {
        "body": (0.28, 0.52, 0.46, 1.0),
        "accent": (0.72, 0.45, 0.20, 1.0),
        "glass": (0.84, 0.90, 0.88, 0.27),
        "burner": (0.30, 0.30, 0.30, 1.0),
        "flame": (1.0, 0.60, 0.14, 1.0),
        "vent_dark": (0.06, 0.10, 0.09, 1.0),
    },
    "polished_brass": {
        "body": (0.74, 0.58, 0.26, 1.0),
        "accent": (0.42, 0.31, 0.15, 1.0),
        "glass": (0.86, 0.90, 0.92, 0.27),
        "burner": (0.32, 0.30, 0.26, 1.0),
        "flame": (1.0, 0.60, 0.12, 1.0),
        "vent_dark": (0.18, 0.13, 0.06, 1.0),
    },
}

# ---------------------------------------------------------------- core dims (m)
FOOT_R = 0.070  # base radius -> ~0.14 m diameter
PIVOT_Z = 0.212  # side handle / bail pivot height
PIVOT_X = 0.058  # bail wire end / pin centre
BAIL_RISE = 0.085  # bail apex above pivot
BAIL_LIMIT = math.radians(100.0)
HINGE_X = 0.073  # folding-strap hinge centre on the +X side
STRAP_LIMIT = math.radians(112.0)
CARRY_LIMIT = math.pi  # top swivel ring +/-180 deg
CARRY_POST_H = 0.010
CARRY_RING_R = 0.012
# swivel_hook_hanger -> a closed carry ring interlinked (chain-link) with the
# fixed top eye ring: stands vertical at 0 deg and swings +/-45 deg left-right
# (about +Y, the front-view horizontal). 0 deg = ring straight up over the cap.
HANGER_SWING_LIMIT = math.radians(45.0)
EYE_RING_R = 0.0072  # fixed top eye-ring radius (Y-Z plane, faces +/-X)
EYE_RING_TUBE = 0.0015
HANGER_RING_R = 0.0165  # swinging carry-ring radius (X-Z plane, faces +/-Y)
HANGER_RING_TUBE = 0.0023
KNOB_BASE_Y = 0.0565  # fount surface radius at knob height
KNOB_Z = 0.055

# Light-chamber vertical span (shared collar seats).
COLLAR_TOP_Z = 0.108  # lower collar top / chamber floor
UPPER_RIM_Z = 0.205  # cap lower rim / chamber ceiling

# Per-cap apex height (drives carry pivot for apex-mounted handles).
CAP_APEX_Z: dict[CapStyle, float] = {
    "domed_vent_cap": 0.278,
    "flat_pierced_crown": 0.260,
    "conical_louver": 0.278,
    "peaked_roof": 0.278,
}


SHELL_TOL = 0.0026  # coarse tessellation for big revolved shells (QC O(n^2) fcl)
MESH_TOL = 0.0016  # coarse tessellation for swept/lofted detail meshes


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# =================================================================== config
@dataclass(frozen=True)
class HurricaneLanternConfig:
    type_style: TypeStyle | None = None
    cap_style: CapStyle | None = None
    carry_style: CarryStyle | None = None
    guard_count: int | None = None
    palette_style: PaletteStyle = "classic_green"
    vent_slot_count: int = 12
    globe_radius_scale: float = 1.0
    name: str = "hurricane_lantern"


@dataclass(frozen=True)
class ResolvedHurricaneLanternConfig:
    type_style: TypeStyle
    cap_style: CapStyle
    carry_style: CarryStyle
    guard_count: int  # 0 == no guard axis (candle_panel)
    palette_style: PaletteStyle
    vent_slot_count: int
    globe_radius_scale: float
    guard_radius: float  # derived cage radius (m)
    globe_max_r: float  # derived widest globe radius (m)
    apex_z: float  # chosen cap apex height (m)
    name: str


def config_from_seed(seed: int) -> HurricaneLanternConfig:
    rng = random.Random(seed)
    return HurricaneLanternConfig(
        type_style=rng.choice(TYPE_STYLES),
        cap_style=rng.choice(CAP_STYLES),
        carry_style=rng.choice(CARRY_STYLES),
        guard_count=rng.choices(GUARD_N_CHOICES, weights=GUARD_N_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        vent_slot_count=rng.randint(VENT_MIN, VENT_MAX),
        globe_radius_scale=round(rng.uniform(0.90, 1.15), 4),
        name=f"seeded_hurricane_lantern_{seed}",
    )


def resolve_config(
    config: HurricaneLanternConfig | None = None,
) -> ResolvedHurricaneLanternConfig:
    cfg = config or HurricaneLanternConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    type_style = _pick(cfg.type_style, TYPE_STYLES)
    cap_style = _pick(cfg.cap_style, CAP_STYLES)
    carry_style = _pick(cfg.carry_style, CARRY_STYLES)

    vent_slot_count = int(_clamp(cfg.vent_slot_count, VENT_MIN, VENT_MAX))
    globe_radius_scale = _clamp(cfg.globe_radius_scale, 0.90, 1.15)

    # --- Compatibility gating (spec §9). ---
    # candle_panel: square chamber has no circumferential guard seat -> no guard.
    # tubular_coldblast: identity is its fixed pair of fat draft tubes -> N=2.
    raw_n = int(cfg.guard_count) if cfg.guard_count is not None else 2
    if type_style == "candle_panel":
        guard_count = 0
    elif type_style == "tubular_coldblast":
        guard_count = 2
    else:
        guard_count = int(_clamp(raw_n, N_MIN, N_MAX))

    # folding_side_strap mounts on a clear flat/wire side; the +/-X air tubes of
    # side_tube and cold_blast occupy that face -> redirect to the bail there.
    if carry_style == "folding_side_strap" and type_style in (
        "hurricane_side_tube",
        "tubular_coldblast",
    ):
        carry_style = "swinging_bail"

    # Widest globe radius by type (the candle chamber has no globe).
    if type_style == "tubular_coldblast":
        base_globe_max = 0.054
    elif type_style == "candle_panel":
        base_globe_max = 0.0
    else:
        base_globe_max = 0.048
    globe_max_r = base_globe_max * globe_radius_scale

    # Derived cage radius: must clear the (possibly scaled) globe + wire (spec §7
    # inequality). Curved members peak well outside; straight wires sit just out.
    guard_radius = max(0.055, globe_max_r + 0.007)

    apex_z = CAP_APEX_Z[cap_style]

    return ResolvedHurricaneLanternConfig(
        type_style=type_style,
        cap_style=cap_style,
        carry_style=carry_style,
        guard_count=guard_count,
        palette_style=palette_style,
        vent_slot_count=vent_slot_count,
        globe_radius_scale=globe_radius_scale,
        guard_radius=guard_radius,
        globe_max_r=globe_max_r,
        apex_z=apex_z,
        name=cfg.name or "hurricane_lantern",
    )


def with_overrides(config: HurricaneLanternConfig, **kwargs: object) -> HurricaneLanternConfig:
    return replace(config, **kwargs)


def _guard_token(r: ResolvedHurricaneLanternConfig) -> str:
    return f"n{r.guard_count}"


def slot_choices_for_config(
    config: HurricaneLanternConfig | ResolvedHurricaneLanternConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedHurricaneLanternConfig) else resolve_config(config)
    return (
        ("type", r.type_style),
        ("cap", r.cap_style),
        ("carry", r.carry_style),
        ("guard_count", _guard_token(r)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# =================================================================== cq solids
def _fount_solid() -> cq.Workplane:
    """Stepped foot + bulged kerosene fount, revolved about Z (S0 L50-67)."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(0.070, 0.0)
        .lineTo(0.070, 0.010)
        .lineTo(0.060, 0.014)
        .lineTo(0.060, 0.024)
        .spline(
            [(0.0545, 0.034), (0.0565, 0.055), (0.049, 0.080), (0.036, 0.092)],
            includeCurrent=True,
        )
        .lineTo(0.036, 0.095)
        .lineTo(0.0, 0.095)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


def _lower_collar_solid() -> cq.Workplane:
    """Green collar / globe seat plate under the chamber (S0 L70-81)."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.095)
        .lineTo(0.050, 0.095)
        .lineTo(0.050, 0.103)
        .lineTo(0.040, 0.108)
        .lineTo(0.0, 0.108)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


# ---- Slot B: cap top-assembly solids (revolved, unioned into the body shell).
def _cap_domed_solid() -> cq.Workplane:
    """Domed chimney + perforated vent band + flared top disk (S0 L84-102)."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.205)
        .lineTo(0.046, 0.205)
        .lineTo(0.046, 0.209)
        .lineTo(0.032, 0.222)
        .lineTo(0.032, 0.246)
        .lineTo(0.047, 0.250)
        .lineTo(0.047, 0.253)
        .lineTo(0.030, 0.2555)
        .spline(
            [(0.027, 0.260), (0.019, 0.269), (0.008, 0.2755), (0.0, 0.278)],
            includeCurrent=True,
        )
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


def _cap_flat_crown_solid() -> cq.Workplane:
    """Low flat pierced vent crown, open chimney throat (S4 L85-114)."""
    crown = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.205)
        .lineTo(0.046, 0.205)
        .lineTo(0.046, 0.209)
        .lineTo(0.032, 0.222)
        .lineTo(0.032, 0.254)
        .lineTo(0.047, 0.254)
        .lineTo(0.047, 0.260)
        .lineTo(0.022, 0.260)
        .lineTo(0.022, 0.224)
        .lineTo(0.018, 0.216)
        .lineTo(0.024, 0.205)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )
    return crown


def _cap_conical_solid() -> cq.Workplane:
    """Tall hollow conical chimney funnel, open throat + flared lip (S5 L84-106)."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.025, 0.205)
        .lineTo(0.047, 0.205)
        .lineTo(0.047, 0.210)
        .lineTo(0.039, 0.218)
        .lineTo(0.038, 0.222)
        .lineTo(0.031, 0.270)
        .lineTo(0.039, 0.274)
        .lineTo(0.039, 0.278)
        .lineTo(0.023, 0.278)
        .lineTo(0.023, 0.274)
        .lineTo(0.027, 0.270)
        .lineTo(0.033, 0.222)
        .lineTo(0.030, 0.218)
        .lineTo(0.025, 0.210)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


# Peaked roof helpers (S6 L90-135).
TENT_ROOF_SIDES = 8
TENT_EAVE_R = 0.043
TENT_EAVE_Z = 0.253
TENT_PEAK_R = 0.0055
TENT_PEAK_Z = 0.274
TENT_FINIAL_TOP_Z = 0.278


def _cap_peaked_collar_solid() -> cq.Workplane:
    """Upper collar + vent band + flared eave disk under the tent roof (S6)."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.205)
        .lineTo(0.046, 0.205)
        .lineTo(0.046, 0.209)
        .lineTo(0.032, 0.222)
        .lineTo(0.032, 0.246)
        .lineTo(0.047, 0.250)
        .lineTo(0.047, TENT_EAVE_Z)
        .lineTo(0.0, TENT_EAVE_Z)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


def _tent_roof_solid() -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, TENT_EAVE_Z - 0.0007))
        .polygon(TENT_ROOF_SIDES, 2.0 * TENT_EAVE_R)
        .workplane(offset=TENT_PEAK_Z - (TENT_EAVE_Z - 0.0007))
        .polygon(TENT_ROOF_SIDES, 2.0 * TENT_PEAK_R)
        .loft(ruled=True)
    )


def _top_finial_solid() -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, TENT_PEAK_Z - 0.0010)
        .lineTo(0.0060, TENT_PEAK_Z - 0.0010)
        .lineTo(0.0060, TENT_PEAK_Z + 0.0022)
        .spline(
            [
                (0.0045, TENT_PEAK_Z + 0.0045),
                (0.0022, TENT_FINIAL_TOP_Z - 0.0008),
                (0.0, TENT_FINIAL_TOP_Z),
            ],
            includeCurrent=True,
        )
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )


def _cap_core_solid(cap_style: CapStyle) -> cq.Workplane:
    """The revolved top-assembly lump unioned into green_body_shell."""
    if cap_style == "domed_vent_cap":
        return _cap_domed_solid()
    if cap_style == "flat_pierced_crown":
        return _cap_flat_crown_solid()
    if cap_style == "conical_louver":
        return _cap_conical_solid()
    return _cap_peaked_collar_solid()


# ---- Slot A: type structural solids.
def _side_member_solid(angle_rad: float) -> cq.Workplane:
    """Curved side air tube swept once, placed equiangularly (S10 L105-121)."""
    path = (
        cq.Workplane("XZ")
        .moveTo(0.050, 0.055)
        .spline(
            [(0.061, 0.095), (0.0655, 0.150), (0.058, 0.198), (0.042, 0.218)],
            includeCurrent=True,
        )
    )
    tangent = cq.Vector(0.011, 0.0, 0.040).normalized()
    profile = cq.Workplane(
        cq.Plane(origin=(0.050, 0.0, 0.055), xDir=(0, 1, 0), normal=tangent)
    ).circle(0.0075)
    return profile.sweep(path, isFrenet=True).rotate(
        (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), math.degrees(angle_rad)
    )


def _draft_tube_solid(side: float) -> cq.Workplane:
    """Fat outer cold-blast draft tube (S3 L106-128)."""
    path = (
        cq.Workplane("XZ")
        .moveTo(0.054, 0.062)
        .spline(
            [(0.066, 0.094), (0.069, 0.148), (0.064, 0.196), (0.043, 0.226)],
            includeCurrent=True,
        )
    )
    tangent = cq.Vector(0.012, 0.0, 0.032).normalized()
    profile = cq.Workplane(
        cq.Plane(origin=(0.054, 0.0, 0.062), xDir=(0, 1, 0), normal=tangent)
    ).circle(0.0105)
    tube = profile.sweep(path, isFrenet=True)
    if side < 0.0:
        tube = tube.mirror("YZ")
    return tube


def _cage_wire_solid(guard_radius: float) -> cq.Workplane:
    """One straight cage wire with bottom/top lugs into the collars (S11 L135-152)."""
    bottom_z = 0.102
    top_z = 0.206
    wire_r = 0.0018
    vertical = (
        cq.Workplane("XY", origin=(guard_radius, 0.0, bottom_z))
        .circle(wire_r)
        .extrude(top_z - bottom_z)
    )
    bottom_lug = (
        cq.Workplane("YZ", origin=(0.048, 0.0, bottom_z))
        .circle(wire_r)
        .extrude(guard_radius - 0.048)
    )
    top_lug = (
        cq.Workplane("YZ", origin=(0.044, 0.0, top_z)).circle(wire_r).extrude(guard_radius - 0.044)
    )
    return vertical.union(bottom_lug).union(top_lug)


def _cage_ring_solid(z: float, guard_radius: float) -> cq.Workplane:
    """Round-section cage ring encircling the globe (S1 L112-119)."""
    return cq.Workplane("XZ").moveTo(guard_radius, z).circle(0.0045).revolve(360.0, (0, 0), (0, 1))


def _scaled_barrel_globe(
    start: tuple[float, float],
    outer_mid: list[tuple[float, float]],
    inner_top: tuple[float, float],
    inner_mid: list[tuple[float, float]],
    rscale: float,
) -> cq.Workplane:
    """Hollow barrel glass globe shell; radial coords scaled by rscale."""

    def s(pt: tuple[float, float]) -> tuple[float, float]:
        return (pt[0] * rscale, pt[1])

    wp = cq.Workplane("XZ").moveTo(*s(start)).spline([s(p) for p in outer_mid], includeCurrent=True)
    wp = wp.lineTo(*s(inner_top)).spline([s(p) for p in inner_mid], includeCurrent=True)
    return wp.close().revolve(360.0, (0, 0), (0, 1))


def _globe_solid(type_style: TypeStyle, rscale: float) -> cq.Workplane:
    if type_style == "tubular_coldblast":
        return _scaled_barrel_globe(
            (0.040, 0.103),
            [(0.052, 0.128), (0.054, 0.160), (0.052, 0.190), (0.040, 0.215)],
            (0.0375, 0.215),
            [(0.0495, 0.190), (0.0515, 0.160), (0.0495, 0.128), (0.0375, 0.103)],
            rscale,
        )
    return _scaled_barrel_globe(
        (0.036, 0.108),
        [(0.0465, 0.130), (0.048, 0.1565), (0.0465, 0.182), (0.036, 0.205)],
        (0.034, 0.205),
        [(0.0445, 0.182), (0.046, 0.1565), (0.0445, 0.130), (0.034, 0.108)],
        rscale,
    )


def _burner_wick_solid() -> cq.Workplane:
    burner = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.104)
        .lineTo(0.018, 0.104)
        .lineTo(0.016, 0.112)
        .lineTo(0.0075, 0.117)
        .lineTo(0.0, 0.117)
        .close()
        .revolve(360.0, (0, 0), (0, 1))
    )
    wick = cq.Workplane("XY", origin=(0.0, 0.0, 0.104)).circle(0.0055).extrude(0.022)
    return burner.union(wick)


def _flame_solid() -> cq.Workplane:
    return (
        cq.Workplane("XY", origin=(0.0, 0.0, 0.124))
        .circle(0.0045)
        .workplane(offset=0.011)
        .circle(0.0085)
        .workplane(offset=0.015)
        .circle(0.004)
        .workplane(offset=0.008)
        .circle(0.0012)
        .loft(ruled=False)
    )


# Candle-panel chamber (S2).
CHAMBER_Z0 = 0.108
CHAMBER_Z1 = 0.205
CHAMBER_HALF = 0.040
PANE_THICK = 0.0018
POST_W = 0.0065
RAIL_W = 0.0060


def _rounded_box_solid(dx: float, dy: float, dz: float, fillet: float) -> cq.Workplane:
    solid = cq.Workplane("XY").box(dx, dy, dz)
    if fillet > 0.0:
        solid = solid.edges("|Z").fillet(fillet)
    return solid


def _corner_post_solid() -> cq.Workplane:
    return _rounded_box_solid(POST_W, POST_W, CHAMBER_Z1 - CHAMBER_Z0 + 0.010, 0.0012)


def _frame_rail_solid(length: float, along_x: bool) -> cq.Workplane:
    if along_x:
        return _rounded_box_solid(length, RAIL_W, RAIL_W, 0.0010)
    return _rounded_box_solid(RAIL_W, length, RAIL_W, 0.0010)


def _glass_pane_solid(along_x: bool) -> cq.Workplane:
    span = 2.0 * CHAMBER_HALF - POST_W * 0.80
    height = CHAMBER_Z1 - CHAMBER_Z0 - 0.008
    if along_x:
        return _rounded_box_solid(span, PANE_THICK, height, 0.00045)
    return _rounded_box_solid(PANE_THICK, span, height, 0.00045)


# ---- Slot C: carry child solids (built in their own joint frame).
def _bail_solid() -> cq.Workplane:
    """Brass wire bail arc + pivot pins in the bail joint frame (S0 L194-214)."""
    path = cq.Workplane("XZ").moveTo(-PIVOT_X, 0.0).threePointArc((0.0, BAIL_RISE), (PIVOT_X, 0.0))
    arc_cz = (BAIL_RISE**2 - PIVOT_X**2) / (2.0 * BAIL_RISE)
    tangent = cq.Vector(-(BAIL_RISE - arc_cz), 0.0, PIVOT_X).normalized()
    profile = cq.Workplane(
        cq.Plane(origin=(-PIVOT_X, 0.0, 0.0), xDir=(0, 1, 0), normal=tangent)
    ).circle(0.002)
    wire_arc = profile.sweep(path, isFrenet=True)
    # One continuous pivot rod through the centre so the joint origin (0,0,0)
    # sits on real bail geometry (fail_if_articulation_origin_far_from_geometry
    # measures distance to the mesh, not the AABB).
    pin_rod = cq.Workplane("YZ", origin=(-0.064, 0.0, 0.0)).circle(0.0025).extrude(0.128)
    return wire_arc.union(pin_rod)


def _carry_ring_wire_geometry():
    """Vertical brass swivel ring mesh in the apex joint frame (S7 L196-217)."""
    ring_center_z = CARRY_POST_H + CARRY_RING_R
    points = []
    for i in range(24):
        theta = -math.pi / 2.0 + (2.0 * math.pi * i / 24.0)
        points.append(
            (
                CARRY_RING_R * math.cos(theta),
                0.0,
                ring_center_z + CARRY_RING_R * math.sin(theta),
            )
        )
    return tube_from_spline_points(
        points,
        radius=0.002,
        closed_spline=True,
        samples_per_segment=4,
        radial_segments=16,
        cap_ends=False,
        up_hint=(0.0, 1.0, 0.0),
    )


def _side_strap_barrel_solid() -> cq.Workplane:
    return cq.Workplane("XZ", origin=(0.0, 0.011, 0.0)).circle(0.0042).extrude(0.022)


def _side_strap_loop_solid() -> cq.Workplane:
    return (
        cq.Workplane("YZ", origin=(0.008, 0.0, -0.075))
        .ellipse(0.034, 0.078)
        .ellipse(0.027, 0.070)
        .extrude(0.002)
    )


def _side_strap_tab_solid() -> cq.Workplane:
    top_tab = cq.Workplane("XY").box(0.014, 0.024, 0.006).translate((0.004, 0.0, -0.002))
    neck = cq.Workplane("XY").box(0.020, 0.010, 0.008).translate((0.007, 0.0, 0.0))
    return top_tab.union(neck)


def _hanger_ring_geometry():
    """Closed carry-ring mesh in its pivot joint frame (X-Z plane, faces +/-Y).

    The ring stands above the pivot (rises over the cap at 0 deg) and dips a few
    mm below it so its lower arc threads through the fixed top eye ring like a
    chain link. Built directly as a torus so it is one watertight closed loop."""
    center_z = HANGER_RING_R - 0.0035  # dip ~3.5 mm below the pivot to thread the eye
    points = []
    n = 48
    for i in range(n):
        theta = 2.0 * math.pi * i / n
        points.append(
            (
                HANGER_RING_R * math.cos(theta),
                0.0,
                center_z + HANGER_RING_R * math.sin(theta),
            )
        )
    return tube_from_spline_points(
        points,
        radius=HANGER_RING_TUBE,
        closed_spline=True,
        samples_per_segment=3,
        radial_segments=18,
        cap_ends=False,
        up_hint=(0.0, 1.0, 0.0),
    )


def _knob_solid() -> cq.Workplane:
    """Knurled wick knob in its joint frame; spin axis = local +Y (S0 L217-230)."""
    stem = cq.Workplane("ZX", origin=(0.0, -0.012, 0.0)).circle(0.0035).extrude(0.024)
    disk = cq.Workplane("ZX", origin=(0.0, 0.009, 0.0)).circle(0.012).extrude(0.007)
    knob = stem.union(disk)
    for i in range(12):
        ang = 2.0 * math.pi * i / 12.0
        rib = (
            cq.Workplane("XY")
            .box(0.0024, 0.007, 0.0024)
            .translate((0.012 * math.cos(ang), 0.0125, 0.012 * math.sin(ang)))
        )
        knob = knob.union(rib)
    return knob


# =================================================================== assembly
def _green_body_shell(r: ResolvedHurricaneLanternConfig) -> cq.Workplane:
    """Fount + lower collar + chosen cap core, unioned into one shell mesh."""
    pieces = [_fount_solid(), _lower_collar_solid(), _cap_core_solid(r.cap_style)]
    return reduce(lambda a, b: a.union(b), pieces)


def _emit_type_structure(body, r: ResolvedHurricaneLanternConfig, mats) -> None:
    """Slot A: chamber + draft/guard structure as inline visuals (Rule 1)."""
    ts = r.type_style
    if ts == "candle_panel":
        # Square panel chamber: floor/ceiling plates bridge the collars to the
        # corner posts so the frame is supported (not a floating island).
        for tag, z in (("floor", CHAMBER_Z0 + 0.003), ("ceiling", CHAMBER_Z1 - 0.003)):
            body.visual(
                Box((2.0 * 0.046, 2.0 * 0.046, 0.006)),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material=mats["body"],
                name=f"chamber_{tag}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
        post_centres = [
            (-CHAMBER_HALF, -CHAMBER_HALF),
            (CHAMBER_HALF, -CHAMBER_HALF),
            (CHAMBER_HALF, CHAMBER_HALF),
            (-CHAMBER_HALF, CHAMBER_HALF),
        ]
        for i, (x, y) in enumerate(post_centres):
            body.visual(
                mesh_from_cadquery(_corner_post_solid(), f"corner_post_{i}", tolerance=0.0003),
                origin=Origin(xyz=(x, y, (CHAMBER_Z0 + CHAMBER_Z1) / 2.0)),
                material=mats["body"],
                name=f"corner_post_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
        rail_length = 2.0 * CHAMBER_HALF + POST_W
        for level_i, z in enumerate((CHAMBER_Z0 + 0.0015, CHAMBER_Z1 - 0.0015)):
            for side_i, sign in enumerate((-1.0, 1.0)):
                body.visual(
                    mesh_from_cadquery(
                        _frame_rail_solid(rail_length, along_x=True),
                        f"frame_rail_{level_i}_{side_i}",
                        tolerance=0.0003,
                    ),
                    origin=Origin(xyz=(0.0, sign * CHAMBER_HALF, z)),
                    material=mats["body"],
                    name=f"frame_rail_{level_i}_{side_i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
                )
                body.visual(
                    mesh_from_cadquery(
                        _frame_rail_solid(rail_length, along_x=False),
                        f"frame_rail_{level_i}_{side_i + 2}",
                        tolerance=0.0003,
                    ),
                    origin=Origin(xyz=(sign * CHAMBER_HALF, 0.0, z)),
                    material=mats["body"],
                    name=f"frame_rail_{level_i}_{side_i + 2}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
                )
        pane_z = (CHAMBER_Z0 + CHAMBER_Z1) / 2.0
        for i in range(4):
            along_x = i < 2
            sign = -1.0 if i % 2 == 0 else 1.0
            origin = (
                Origin(xyz=(0.0, sign * CHAMBER_HALF, pane_z))
                if along_x
                else Origin(xyz=(sign * CHAMBER_HALF, 0.0, pane_z))
            )
            body.visual(
                mesh_from_cadquery(
                    _glass_pane_solid(along_x), f"glass_pane_{i}", tolerance=0.00025
                ),
                origin=origin,
                material=mats["glass"],
                name=f"glass_pane_{i}", material_class_id="glass.clear_transparent",
            )
        return

    # Round-chamber types: a translucent barrel globe + draft/guard structure.
    body.visual(
        mesh_from_cadquery(
            _globe_solid(ts, r.globe_radius_scale), "globe_glass", tolerance=SHELL_TOL
        ),
        material=mats["glass"],
        name="globe_glass", material_class_id="glass.clear_transparent",
    )

    if ts == "tubular_coldblast":
        for i, side in enumerate((1.0, -1.0)):
            body.visual(
                mesh_from_cadquery(_draft_tube_solid(side), f"draft_tube_{i}", tolerance=MESH_TOL),
                material=mats["body"],
                name=f"draft_tube_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
    elif ts == "hurricane_side_tube":
        # Guard multiplicity: N curved side air tubes around the globe. Phase the
        # ring so the +Y wick-knob azimuth (pi/2) always lands in a gap between
        # members (avoids member/knob collision); N=2 reduces to the classic
        # +/-X tube pair.
        phase = math.pi / 2.0 - math.pi / r.guard_count
        for i in range(r.guard_count):
            ang = phase + 2.0 * math.pi * i / r.guard_count
            body.visual(
                mesh_from_cadquery(
                    _side_member_solid(ang), f"guard_member_{i}", tolerance=MESH_TOL
                ),
                material=mats["body"],
                name=f"guard_member_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
    else:  # railroad_cage: N straight lugged cage wires + two encircling rings.
        for tag, z in (("lower", 0.108), ("upper", 0.205)):
            body.visual(
                mesh_from_cadquery(
                    _cage_ring_solid(z, r.guard_radius), f"guard_ring_{tag}", tolerance=MESH_TOL
                ),
                material=mats["body"],
                name=f"guard_ring_{tag}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
        cage_wire = _cage_wire_solid(r.guard_radius)
        phase = math.pi / 2.0 - math.pi / r.guard_count
        for i in range(r.guard_count):
            ang = phase + 2.0 * math.pi * i / r.guard_count
            body.visual(
                mesh_from_cadquery(cage_wire, f"guard_member_{i}", tolerance=MESH_TOL),
                origin=Origin(rpy=(0.0, 0.0, ang)),
                material=mats["body"],
                name=f"guard_member_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )


def _emit_cap_features(body, r: ResolvedHurricaneLanternConfig, mats) -> None:
    """Slot B: cap-local vent perforations / roof / finial inline visuals."""
    n = r.vent_slot_count
    if r.cap_style == "conical_louver":
        # Slanted louver slits + raised lips landing on the conical surface (S5).
        for i in range(n):
            ang = 2.0 * math.pi * i / n
            z = 0.235 + 0.010 * (i % 3)
            cone_r = 0.038 - (0.038 - 0.031) * ((z - 0.222) / (0.270 - 0.222))
            slot_r = cone_r + 0.0014
            body.visual(
                Box((0.0030, 0.0130, 0.0035)),
                origin=Origin(
                    xyz=(slot_r * math.cos(ang), slot_r * math.sin(ang), z),
                    rpy=(math.radians(25.0), 0.0, ang + math.pi / 2.0),
                ),
                material=mats["vent_dark"],
                name=f"vent_slot_{i}", material_class_id="metal.blackened_gunmetal",
            )
            lip_r = cone_r + 0.0026
            body.visual(
                Box((0.0022, 0.0145, 0.0020)),
                origin=Origin(
                    xyz=(lip_r * math.cos(ang), lip_r * math.sin(ang), z + 0.004),
                    rpy=(math.radians(25.0), 0.0, ang + math.pi / 2.0),
                ),
                material=mats["body"],
                name=f"louver_lip_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
        return

    if r.cap_style == "peaked_roof":
        body.visual(
            mesh_from_cadquery(_tent_roof_solid(), "tent_roof_cap", tolerance=MESH_TOL),
            material=mats["body"],
            name="tent_roof_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        body.visual(
            mesh_from_cadquery(_top_finial_solid(), "top_finial", tolerance=MESH_TOL),
            material=mats["accent"],
            name="top_finial", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )

    # Perforated vent band: dark slots embedded into the cap band (S0 L266-277).
    z_band = 0.238 if r.cap_style == "flat_pierced_crown" else 0.234
    for i in range(n):
        ang = 2.0 * math.pi * i / n
        body.visual(
            Box((0.004, 0.0045, 0.012)),
            origin=Origin(
                xyz=(0.031 * math.cos(ang), 0.031 * math.sin(ang), z_band),
                rpy=(0.0, 0.0, ang),
            ),
            material=mats["vent_dark"],
            name=f"vent_slot_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_apex_seat(body, r: ResolvedHurricaneLanternConfig, mats) -> None:
    """A throat-covering button at the cap apex: puts real body geometry on the
    (0,0,apex_z) pivot datum and bridges the open chimney throat (conical /
    flat crown) so apex-mounted handle hardware is supported, not floating."""
    body.visual(
        Cylinder(radius=0.024, length=0.006),
        origin=Origin(xyz=(0.0, 0.0, r.apex_z - 0.003)),
        material=mats["body"],
        name="apex_seat", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
    )


def _emit_carry(model, body, r: ResolvedHurricaneLanternConfig, mats) -> str:
    """Slot C: the single swinging handle + its body support hardware.

    Returns the carry part name. Owns the 2nd non-FIXED joint (REVOLUTE), a
    captured-pin pivot grandfathered out of the MatingContract check.
    """
    cs = r.carry_style

    if cs == "swinging_bail":
        # A through-axle on the centre X line (bridges the cap walls and puts real
        # body geometry on the pivot origin (0,0,PIVOT_Z) for open-throat caps),
        # plus two outboard ear bosses where the bail pins emerge.
        body.visual(
            Cylinder(radius=0.006, length=0.116),
            origin=Origin(xyz=(0.0, 0.0, PIVOT_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["body"],
            name="bail_pivot_axle", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        for i, side in enumerate((1.0, -1.0)):
            body.visual(
                Cylinder(radius=0.008, length=0.012),
                origin=Origin(xyz=(side * 0.050, 0.0, PIVOT_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["body"],
                name=f"bail_ear_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
        bail = model.part("bail_handle")
        bail.visual(
            mesh_from_cadquery(_bail_solid(), "bail_wire", tolerance=MESH_TOL),
            material=mats["accent"],
            name="bail_wire", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        bail.inertial = Inertial.from_geometry(
            Box((2.0 * PIVOT_X, 0.01, BAIL_RISE)),
            mass=0.03,
            origin=Origin(xyz=(0.0, 0.0, BAIL_RISE / 2.0)),
        )
        model.articulation(
            "body_to_bail_handle",
            ArticulationType.REVOLUTE,
            parent=body,
            child=bail,
            origin=Origin(xyz=(0.0, 0.0, PIVOT_Z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=5.0, velocity=3.0, lower=-BAIL_LIMIT, upper=BAIL_LIMIT
            ),
        )
        return "bail_handle"

    if cs == "top_swivel_ring":
        _emit_apex_seat(body, r, mats)
        ring = model.part("carry_ring")
        ring.visual(
            Cylinder(radius=0.0032, length=CARRY_POST_H + 0.006),
            origin=Origin(xyz=(0.0, 0.0, CARRY_POST_H / 2.0)),
            material=mats["accent"],
            name="swivel_post", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        ring.visual(
            Cylinder(radius=0.0065, length=0.003),
            origin=Origin(xyz=(0.0, 0.0, 0.0015)),
            material=mats["accent"],
            name="post_collar", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        ring.visual(
            mesh_from_geometry(_carry_ring_wire_geometry(), "swivel_ring_wire"),
            material=mats["accent"],
            name="swivel_ring_wire", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        ring.inertial = Inertial.from_geometry(
            Box((2.0 * CARRY_RING_R, 0.01, CARRY_POST_H + 2.0 * CARRY_RING_R)),
            mass=0.015,
            origin=Origin(xyz=(0.0, 0.0, CARRY_POST_H + CARRY_RING_R)),
        )
        model.articulation(
            "body_to_carry_ring",
            ArticulationType.REVOLUTE,
            parent=body,
            child=ring,
            origin=Origin(xyz=(0.0, 0.0, r.apex_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=1.5, velocity=4.0, lower=-CARRY_LIMIT, upper=CARRY_LIMIT
            ),
        )
        return "carry_ring"

    if cs == "folding_side_strap":
        # Clevis hinge bracket reaching from the cap band to the +X hinge line.
        body.visual(
            Box((0.030, 0.038, 0.006)),
            origin=Origin(xyz=((0.044 + HINGE_X) / 2.0, 0.0, PIVOT_Z - 0.001)),
            material=mats["body"],
            name="strap_hinge_saddle", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        for i, y0 in enumerate((-0.013, 0.013)):
            body.visual(
                Cylinder(radius=0.0048, length=0.008),
                origin=Origin(xyz=(HINGE_X, y0, PIVOT_Z), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["body"],
                name=f"strap_hinge_lug_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
            )
        strap = model.part("side_strap_handle")
        strap.visual(
            mesh_from_cadquery(_side_strap_loop_solid(), "strap_loop", tolerance=0.0003),
            material=mats["accent"],
            name="strap_loop", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        strap.visual(
            mesh_from_cadquery(_side_strap_tab_solid(), "strap_tab", tolerance=0.0003),
            material=mats["accent"],
            name="strap_tab", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        strap.visual(
            mesh_from_cadquery(_side_strap_barrel_solid(), "strap_barrel", tolerance=0.0003),
            material=mats["accent"],
            name="strap_barrel", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
        )
        strap.inertial = Inertial.from_geometry(
            Box((0.02, 0.07, 0.08)),
            mass=0.02,
            origin=Origin(xyz=(0.006, 0.0, -0.04)),
        )
        model.articulation(
            "body_to_side_strap",
            ArticulationType.REVOLUTE,
            parent=body,
            child=strap,
            origin=Origin(xyz=(HINGE_X, 0.0, PIVOT_Z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=STRAP_LIMIT),
        )
        return "side_strap_handle"

    # swivel_hook_hanger: a fixed top eye ring on a short stem at the cap apex,
    # with a closed carry ring hooked over the TOP of that eye ring (chain-link).
    # The pivot sits at the eye-ring top: the carry ring bears on the eye's top
    # arc and the lantern swings +/-45 deg left-right about that top axis.
    _emit_apex_seat(body, r, mats)
    # Eye ring center sits a touch above the apex so its bottom clears the cap.
    eye_ring_z = r.apex_z + EYE_RING_R + 0.002
    # Pivot / link point = the top of the eye ring (not its centre).
    pivot_z = eye_ring_z + EYE_RING_R
    body.visual(
        Cylinder(radius=0.0020, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, r.apex_z + 0.001)),
        material=mats["accent"],
        name="top_eye_stem", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
    )
    # Fixed eye ring in the Y-Z plane (faces +/-X) so its lower bar runs along Y
    # and the carry ring can thread through its hole and swing about +Y.
    body.visual(
        mesh_from_geometry(
            TorusGeometry(
                radius=EYE_RING_R, tube=EYE_RING_TUBE, radial_segments=16, tubular_segments=44
            ),
            "top_eye_ring",
        ),
        origin=Origin(xyz=(0.0, 0.0, eye_ring_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="top_eye_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
    )
    hanger = model.part("carry_hanger_ring")
    hanger.visual(
        mesh_from_geometry(_hanger_ring_geometry(), "hanger_ring_wire"),
        material=mats["accent"],
        name="hanger_ring_wire", material_class_id=("metal.brass_polished" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
    )
    hanger.inertial = Inertial.from_geometry(
        Box((2.0 * HANGER_RING_R, 0.01, 2.0 * HANGER_RING_R)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, HANGER_RING_R - 0.0035)),
    )
    # Pivot at the eye-ring TOP; axis +Y => left-right swing in the X-Z plane.
    model.articulation(
        "body_to_hanger_ring",
        ArticulationType.REVOLUTE,
        parent=body,
        child=hanger,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=2.5, lower=-HANGER_SWING_LIMIT, upper=HANGER_SWING_LIMIT
        ),
    )
    return "carry_hanger_ring"


def _emit_wick_knob(model, body, mats) -> None:
    knob = model.part("wick_knob")
    knob.visual(
        mesh_from_cadquery(_knob_solid(), "knob_knurled_disk", tolerance=MESH_TOL),
        material=mats["accent"],
        name="knob_knurled_disk", material_class_id="metal.brass_polished",
    )
    knob.visual(
        Cylinder(radius=0.0018, length=0.0028),
        origin=Origin(xyz=(0.006, 0.0172, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["burner"],
        name="knob_index_nub", material_class_id="metal.blackened_gunmetal",
    )
    knob.inertial = Inertial.from_geometry(
        Cylinder(radius=0.012, length=0.03),
        mass=0.01,
        origin=Origin(xyz=(0.0, 0.009, 0.0)),
    )
    model.articulation(
        "fount_to_wick_knob",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=knob,
        origin=Origin(xyz=(0.0, KNOB_BASE_Y, KNOB_Z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0),
    )


# =================================================================== build
def build_hurricane_lantern(
    config: HurricaneLanternConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"hurricane_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = model.part("lantern_body")
    body.visual(
        mesh_from_cadquery(_green_body_shell(r), "green_body_shell", tolerance=SHELL_TOL),
        material=mats["body"],
        name="green_body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"classic_green", "barn_red", "matte_black", "weathered_copper", "polished_brass"} else "metal.steel_galvanized"),
    )
    body.inertial = Inertial.from_geometry(
        Cylinder(radius=FOOT_R, length=r.apex_z),
        mass=0.45,
        origin=Origin(xyz=(0.0, 0.0, r.apex_z / 2.0)),
    )

    _emit_type_structure(body, r, mats)
    # Internal burner / wick / flame (present in every chamber).
    body.visual(
        mesh_from_cadquery(_burner_wick_solid(), "burner_wick", tolerance=MESH_TOL),
        material=mats["burner"],
        name="burner_wick", material_class_id="metal.blackened_gunmetal",
    )
    body.visual(
        mesh_from_cadquery(_flame_solid(), "flame", tolerance=MESH_TOL),
        material=mats["flame"],
        name="flame", material_class_id="tech.emissive_surface",
    )

    _emit_cap_features(body, r, mats)
    _emit_carry(model, body, r, mats)
    _emit_wick_knob(model, body, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_hurricane_lantern(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_hurricane_lantern(config_from_seed(seed), assets=assets)


# =================================================================== tests
def run_hurricane_lantern_tests(
    object_model: ArticulatedObject,
    config: HurricaneLanternConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("lantern_body")

    # ---- Captured-pin / stem allowances (element-scoped; mirrors sources). ----
    carry_part_name = {
        "swinging_bail": "bail_handle",
        "top_swivel_ring": "carry_ring",
        "folding_side_strap": "side_strap_handle",
        "swivel_hook_hanger": "carry_hanger_ring",
    }[r.carry_style]
    carry = object_model.get_part(carry_part_name)
    knob = object_model.get_part("wick_knob")

    if r.carry_style == "swinging_bail":
        ctx.allow_overlap(
            carry,
            body,
            elem_a="bail_wire",
            elem_b="bail_pivot_axle",
            reason="bail pivot rod is coaxial with the body pivot axle it rides on.",
        )
        ctx.allow_overlap(
            carry,
            body,
            elem_a="bail_wire",
            elem_b="bail_ear_0",
            reason="bail pivot pin seated through the +X ear boss.",
        )
        ctx.allow_overlap(
            carry,
            body,
            elem_a="bail_wire",
            elem_b="bail_ear_1",
            reason="bail pivot pin seated through the -X ear boss.",
        )
    elif r.carry_style == "top_swivel_ring":
        ctx.allow_overlap(
            carry,
            body,
            reason="swivel post seats on the chimney apex.",
        )
    elif r.carry_style == "folding_side_strap":
        ctx.allow_overlap(
            carry,
            body,
            elem_a="strap_barrel",
            elem_b="strap_hinge_lug_0",
            reason="strap hinge barrel captured between the clevis lugs.",
        )
        ctx.allow_overlap(
            carry,
            body,
            elem_a="strap_barrel",
            elem_b="strap_hinge_lug_1",
            reason="strap hinge barrel captured between the clevis lugs.",
        )
    else:  # swivel_hook_hanger
        ctx.allow_overlap(
            carry,
            body,
            elem_a="hanger_ring_wire",
            elem_b="top_eye_ring",
            reason="carry ring is interlinked through the fixed top eye ring (chain link).",
        )

    ctx.allow_overlap(
        knob,
        body,
        elem_a="knob_knurled_disk",
        elem_b="green_body_shell",
        reason="wick knob stem passes through the fount wall to the wick.",
    )

    # ---- Baseline geometry / connectivity gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    # ---- Identity: grounded body, glass chamber, internal flame, vents. ----
    aabb = ctx.part_world_aabb(body)
    ctx.check(
        "lantern body grounded at z=0",
        aabb is not None and abs(aabb[0][2]) <= 0.003,
        details=f"body aabb={aabb}",
    )
    ctx.check(
        "lantern roughly 0.14 m across the base",
        aabb is not None and 0.12 <= (aabb[1][0] - aabb[0][0]) <= 0.18,
        details=f"body aabb={aabb}",
    )

    glass_elem = "glass_pane_0" if r.type_style == "candle_panel" else "globe_glass"
    glass_visual = body.get_visual(glass_elem)
    glass_rgba = glass_visual.material.rgba if glass_visual.material else None
    ctx.check(
        "light chamber is translucent",
        glass_rgba is not None and glass_rgba[3] < 0.5,
        details=f"{glass_elem} rgba={glass_rgba}",
    )

    flame_bb = ctx.part_element_world_aabb(body, elem="flame")
    ctx.check(
        "flame present inside the chamber",
        flame_bb is not None,
        details=f"flame={flame_bb}",
    )

    n_vent = sum(1 for v in body.visuals if (v.name or "").startswith("vent_slot_"))
    ctx.check(
        "cap vent perforations match vent_slot_count",
        n_vent == r.vent_slot_count,
        details=f"vents={n_vent} expected={r.vent_slot_count}",
    )

    # ---- Guard multiplicity: N equiangular FIXED members, no joint. ----
    guard_members = [v for v in body.visuals if (v.name or "").startswith("guard_member_")]
    if r.guard_count and r.type_style in GUARD_TYPES:
        ctx.check(
            "guard members count == guard_count",
            len(guard_members) == r.guard_count,
            details=f"members={len(guard_members)} expected={r.guard_count}",
        )
        ctx.check(
            "no guard articulation (guards are FIXED welds)",
            all("guard" not in a.name for a in object_model.articulations),
            details=f"joints={[a.name for a in object_model.articulations]}",
        )
    else:
        ctx.check(
            "candle_panel / coldblast carry no equiangular guard axis",
            len(guard_members) == 0,
            details=f"members={len(guard_members)}",
        )

    # ---- Joint topology: exactly the carry REVOLUTE + wick CONTINUOUS. ----
    joint_names = {a.name for a in object_model.articulations}
    ctx.check(
        "exactly two non-fixed joints (carry + wick)",
        len(object_model.articulations) == 2
        and all(a.articulation_type != ArticulationType.FIXED for a in object_model.articulations),
        details=f"joints={sorted(joint_names)}",
    )

    carry_joint = next(a for a in object_model.articulations if a.name.startswith("body_to_"))
    ctx.check(
        "carry handle is REVOLUTE",
        carry_joint.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={carry_joint.articulation_type}",
    )
    expected_axis = {
        "swinging_bail": (1.0, 0.0, 0.0),
        "top_swivel_ring": (0.0, 0.0, 1.0),
        "folding_side_strap": (0.0, -1.0, 0.0),
        "swivel_hook_hanger": (0.0, 1.0, 0.0),
    }[r.carry_style]
    dom = max(range(3), key=lambda k: abs(expected_axis[k]))
    ctx.check(
        "carry REVOLUTE axis matches the carry module",
        abs(abs(carry_joint.axis[dom]) - 1.0) < 1e-6,
        details=f"axis={tuple(carry_joint.axis)} expected={expected_axis}",
    )

    knob_joint = object_model.get_articulation("fount_to_wick_knob")
    ctx.check(
        "wick knob is a continuous +Y spinner",
        knob_joint.articulation_type == ArticulationType.CONTINUOUS
        and knob_joint.motion_limits is not None
        and knob_joint.motion_limits.lower is None
        and abs(knob_joint.axis[1]) > 0.99,
        details=f"type={knob_joint.articulation_type} axis={tuple(knob_joint.axis)}",
    )

    # ---- Carry actually swings (REVOLUTE moves the handle AABB). ----
    closed = ctx.part_world_aabb(carry)
    swing_q = {
        "swinging_bail": 1.4,
        "top_swivel_ring": math.pi / 2.0,
        "folding_side_strap": 1.4,
        "swivel_hook_hanger": HANGER_SWING_LIMIT * 0.85,
    }[r.carry_style]
    with ctx.pose({carry_joint: swing_q}):
        swung = ctx.part_world_aabb(carry)
    if closed is not None and swung is not None:
        moved = max(
            abs(swung[0][k] - closed[0][k]) + abs(swung[1][k] - closed[1][k]) for k in range(3)
        )
        ctx.check(
            "carry handle swings on its REVOLUTE",
            moved > 0.01,
            details=f"closed={closed} swung={swung}",
        )

    # ---- off-axis nub sweeps across the spin axis after half a turn. ----
    nub0 = ctx.part_element_world_aabb(knob, elem="knob_index_nub")
    with ctx.pose({knob_joint: math.pi}):
        nub1 = ctx.part_element_world_aabb(knob, elem="knob_index_nub")
    if nub0 is not None and nub1 is not None:
        ctx.check(
            "wick knob nub proves continuous rotation",
            (nub0[0][0] + nub0[1][0]) / 2.0 > 0.003 and (nub1[0][0] + nub1[1][0]) / 2.0 < -0.003,
            details=f"nub rest={nub0} half-turn={nub1}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with guard_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "HurricaneLanternConfig",
    "ResolvedHurricaneLanternConfig",
    "build_hurricane_lantern",
    "build_seeded_hurricane_lantern",
    "config_from_seed",
    "resolve_config",
    "run_hurricane_lantern_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
