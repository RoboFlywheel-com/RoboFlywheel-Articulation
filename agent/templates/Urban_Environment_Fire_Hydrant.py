# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template: cast-iron PILLAR fire hydrant.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Urban_Environment_Fire_Hydrant.md``.

Identity: a vertical cast-iron pillar hydrant. A single root ``body`` chassis
carries (as inline visuals, Rule 1) the ground base, ribbed barrel, widened
valve chamber, bonnet flange, the chosen bonnet shape, the per-outlet stubs /
collars and the tether eyes. The only articulations are:

- ``operating_nut``  — REVOLUTE about +Z at the bonnet apex (defining joint).
- ``outlet_{i}_cap`` — PRISMATIC lift-off straight along the outlet axis.
- ``outlet_{i}_chain_{j}`` — a serial-REVOLUTE round-link chain tethering each
  cap back to a body eye.

Slots (mixed pattern = parallel named slots + an outlet multiplicity axis):
- Slot A ``bonnet_shape``      : domed / flat-bolted / pointed-cone.
- Slot B ``outlet_cap_style``  : knurled-screw / storz-lever / plain-dome-bail
  (one style applied uniformly to every outlet).
- Slot C ``base_form``         : bolted-flange / straight-sleeve.
- Multiplicity ``outlet_count``: N in [1, 4].
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Cylinder,
    DomeGeometry,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

BonnetShape = Literal["bonnet_domed", "bonnet_flat_bolted", "bonnet_pointed_cone"]
OutletCapStyle = Literal["cap_knurled_screw", "cap_storz_lever", "cap_plain_dome_bail"]
BaseForm = Literal["base_bolted_flange", "base_straight_sleeve"]
PaletteStyle = Literal[
    "municipal_red",
    "high_vis_yellow",
    "silver_chrome",
    "safety_green",
    "industrial_blue",
    "matte_black",
]

BONNET_SHAPES: tuple[BonnetShape, ...] = (
    "bonnet_domed",
    "bonnet_flat_bolted",
    "bonnet_pointed_cone",
)
OUTLET_CAP_STYLES: tuple[OutletCapStyle, ...] = (
    "cap_knurled_screw",
    "cap_storz_lever",
    "cap_plain_dome_bail",
)
BASE_FORMS: tuple[BaseForm, ...] = ("base_bolted_flange", "base_straight_sleeve")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "municipal_red",
    "high_vis_yellow",
    "silver_chrome",
    "safety_green",
    "industrial_blue",
    "matte_black",
)

N_MIN = 1
N_MAX = 4
# outlet-count weights: N=3 high, N=2 next, N=1, N=4 rare (spec multiplicity).
OUTLET_COUNT_WEIGHTS = (0.15, 0.30, 0.45, 0.10)  # for N = 1, 2, 3, 4

# Each palette only re-colors three materials (body / accent / chain).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "municipal_red": {
        "body": (0.74, 0.10, 0.09, 1.0),
        "accent": (0.82, 0.62, 0.16, 1.0),
        "chain": (0.30, 0.27, 0.13, 1.0),
    },
    "high_vis_yellow": {
        "body": (0.92, 0.78, 0.10, 1.0),
        "accent": (0.62, 0.63, 0.66, 1.0),
        "chain": (0.24, 0.24, 0.26, 1.0),
    },
    "silver_chrome": {
        "body": (0.72, 0.73, 0.75, 1.0),
        "accent": (0.82, 0.62, 0.16, 1.0),
        "chain": (0.30, 0.27, 0.13, 1.0),
    },
    "safety_green": {
        "body": (0.10, 0.42, 0.20, 1.0),
        "accent": (0.82, 0.62, 0.16, 1.0),
        "chain": (0.30, 0.27, 0.13, 1.0),
    },
    "industrial_blue": {
        "body": (0.12, 0.30, 0.55, 1.0),
        "accent": (0.62, 0.63, 0.66, 1.0),
        "chain": (0.24, 0.24, 0.26, 1.0),
    },
    "matte_black": {
        "body": (0.14, 0.14, 0.15, 1.0),
        "accent": (0.82, 0.62, 0.16, 1.0),
        "chain": (0.30, 0.27, 0.13, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). ~1.0 m tall cast-iron pillar.
# All Z measured from the ground contact plane z=0.
# ---------------------------------------------------------------------------
_BASE_TOP_Z = 0.090       # top of the base form (barrel starts here)
_BARREL_R = 0.072         # ribbed barrel radius
_BARREL_TOP_Z = 0.560     # top of the ribbed barrel
_CHAMBER_R = 0.105        # widened valve-chamber radius
_CHAMBER_BOT_Z = 0.520    # chamber bottom (overlaps barrel top a touch)
_CHAMBER_TOP_Z = 0.720    # chamber top
_BONNET_FLANGE_R = 0.115
_BONNET_BASE_Z = 0.805    # bonnet flange top face (bonnet sits here)

_N_RIBS = 4               # cast rib bands on the barrel (decoration; fixed)

# nut_seat offsets above bonnet_base_z, keyed by bonnet shape.
_NUT_SEAT_OFFSET = {
    "bonnet_domed": 0.110,
    "bonnet_flat_bolted": 0.048,
    "bonnet_pointed_cone": 0.300,
}

_NUT_HALF = 0.026         # operating-nut half-width (square nut)
_NUT_H = 0.038

_SIDE_OUTLET_R = 0.034    # side hose outlet radius
_PUMPER_R_FACTOR = 1.45   # pumper outlet is larger (front, N>=3 / N=1)
_OUTLET_STUB_LEN = 0.052  # radial length of the outlet stub from chamber wall
_CAP_LEN = 0.030
_CAP_TRAVEL = 0.120       # PRISMATIC upper limit (lift-off distance)

_CHAIN_LINK_STEP = 0.024  # nominal chain link spacing
_CHAIN_LINK_R = 0.010     # round-link torus tube/half-extent


@dataclass(frozen=True)
class FireHydrantConfig:
    bonnet_shape: BonnetShape | None = None
    outlet_cap_style: OutletCapStyle | None = None
    base_form: BaseForm | None = None
    outlet_count: int | None = None
    palette_style: PaletteStyle = "municipal_red"
    barrel_height_scale: float = 1.0
    barrel_radius_scale: float = 1.0
    outlet_r_scale: float = 1.0
    name: str = "fire_hydrant"


@dataclass(frozen=True)
class ResolvedFireHydrantConfig:
    bonnet_shape: BonnetShape
    outlet_cap_style: OutletCapStyle
    base_form: BaseForm
    outlet_count: int
    palette_style: PaletteStyle
    # resolved geometry
    barrel_r: float
    barrel_top_z: float
    chamber_r: float
    chamber_bot_z: float
    chamber_top_z: float
    bonnet_flange_r: float
    bonnet_base_z: float
    nut_seat_z: float
    side_outlet_r: float
    pumper_outlet_r: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> FireHydrantConfig:
    rng = random.Random(seed)
    n = rng.choices((1, 2, 3, 4), weights=OUTLET_COUNT_WEIGHTS, k=1)[0]
    return FireHydrantConfig(
        bonnet_shape=rng.choice(BONNET_SHAPES),
        outlet_cap_style=rng.choice(OUTLET_CAP_STYLES),
        base_form=rng.choice(BASE_FORMS),
        outlet_count=n,
        palette_style=rng.choice(PALETTE_STYLES),
        barrel_height_scale=round(rng.uniform(0.90, 1.12), 4),
        barrel_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        outlet_r_scale=round(rng.uniform(0.85, 1.20), 4),
        name=f"seeded_fire_hydrant_{seed}",
    )


def resolve_config(config: FireHydrantConfig | None) -> ResolvedFireHydrantConfig:
    cfg = config or FireHydrantConfig()
    bonnet = _pick(cfg.bonnet_shape, BONNET_SHAPES)
    cap = _pick(cfg.outlet_cap_style, OUTLET_CAP_STYLES)
    base = _pick(cfg.base_form, BASE_FORMS)
    n = int(cfg.outlet_count if cfg.outlet_count is not None else 3)
    n = max(N_MIN, min(N_MAX, n))
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    h_scale = _clamp(cfg.barrel_height_scale, 0.90, 1.12)
    r_scale = _clamp(cfg.barrel_radius_scale, 0.92, 1.10)
    o_scale = _clamp(cfg.outlet_r_scale, 0.85, 1.20)

    barrel_r = _BARREL_R * r_scale
    chamber_r = _CHAMBER_R * r_scale

    # Height: scale the column above the base, keep base/chamber proportional.
    span = (_BARREL_TOP_Z - _BASE_TOP_Z) * h_scale
    barrel_top_z = _BASE_TOP_Z + span
    chamber_bot_z = barrel_top_z - 0.040
    chamber_top_z = chamber_bot_z + 0.200
    bonnet_flange_r = max(_BONNET_FLANGE_R * r_scale, chamber_r + 0.006)
    bonnet_base_z = chamber_top_z + 0.085
    nut_seat_z = bonnet_base_z + _NUT_SEAT_OFFSET[bonnet]

    side_outlet_r = _SIDE_OUTLET_R * o_scale
    # Clamp outlet radius so adjacent outlets do not overlap circumferentially
    # and the stub doesn't exceed the chamber height window.
    side_outlet_r = min(side_outlet_r, 0.044)
    pumper_outlet_r = side_outlet_r * _PUMPER_R_FACTOR

    return ResolvedFireHydrantConfig(
        bonnet_shape=bonnet,
        outlet_cap_style=cap,
        base_form=base,
        outlet_count=n,
        palette_style=palette,
        barrel_r=barrel_r,
        barrel_top_z=barrel_top_z,
        chamber_r=chamber_r,
        chamber_bot_z=chamber_bot_z,
        chamber_top_z=chamber_top_z,
        bonnet_flange_r=bonnet_flange_r,
        bonnet_base_z=bonnet_base_z,
        nut_seat_z=nut_seat_z,
        side_outlet_r=side_outlet_r,
        pumper_outlet_r=pumper_outlet_r,
        name=cfg.name,
    )


def with_overrides(config: FireHydrantConfig, **kwargs) -> FireHydrantConfig:
    return replace(config, **kwargs)


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def slot_choices_for_config(
    config: FireHydrantConfig | ResolvedFireHydrantConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedFireHydrantConfig)
        else resolve_config(config)
    )
    return (
        ("bonnet_shape", r.bonnet_shape),
        ("outlet_cap_style", r.outlet_cap_style),
        ("base_form", r.base_form),
        ("outlet_count", f"n{r.outlet_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Outlet placement: each spec carries radius / center_z / yaw.
# N=1 -> single front pumper (large, low). N=2 -> symmetric +-90 sides.
# N=3 -> 120 evenly. N=4 -> 90 evenly.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _OutletSpec:
    yaw: float       # circumferential angle about +Z
    radius: float    # outlet bore radius
    center_z: float  # outlet axis center height
    is_pumper: bool


def _outlet_specs(r: ResolvedFireHydrantConfig) -> list[_OutletSpec]:
    n = r.outlet_count
    side_z = r.chamber_top_z - 0.060
    pump_z = r.chamber_bot_z + 0.080
    if n == 1:
        return [_OutletSpec(0.0, r.pumper_outlet_r, pump_z, True)]
    if n == 2:
        return [
            _OutletSpec(math.radians(90.0), r.side_outlet_r, side_z, False),
            _OutletSpec(math.radians(-90.0), r.side_outlet_r, side_z, False),
        ]
    # n in {3, 4}: even circumferential split, uniform side outlets.
    specs: list[_OutletSpec] = []
    for i in range(n):
        yaw = 2.0 * math.pi * i / n
        specs.append(_OutletSpec(yaw, r.side_outlet_r, side_z, False))
    return specs


# ---------------------------------------------------------------------------
# Body chassis (single root part). Everything fixed is an inline visual.
# ---------------------------------------------------------------------------
def _lathe(profile, name, segments=48):
    return mesh_from_geometry(LatheGeometry(profile, segments=segments), name)


def _build_body(model: ArticulatedObject, r: ResolvedFireHydrantConfig, mats):
    body = model.part("body")

    # ---- Base form (Slot C) ----
    if r.base_form == "base_bolted_flange":
        flange_r = max(r.barrel_r + 0.058, r.chamber_r + 0.004)
        shelf_z = 0.030  # flat top shelf of the flange (bolts seat here)
        profile = [
            (0.0, 0.0),
            (flange_r, 0.0),
            (flange_r, shelf_z),
            (r.barrel_r + 0.020, shelf_z),
            (r.barrel_r + 0.010, _BASE_TOP_Z),
            (0.0, _BASE_TOP_Z),
        ]
        body.visual(
            _lathe(profile, "base_flange"),
            material=mats["body"],
            name="base_flange", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )
        # brass hex bolt ring seated on the flat flange shelf (deeply embedded:
        # the bolt body spans down into the solid flange so it is never an
        # island).
        n_bolts = 8
        bolt_r_ring = (flange_r + (r.barrel_r + 0.020)) * 0.5
        for i in range(n_bolts):
            a = 2.0 * math.pi * i / n_bolts
            body.visual(
                Cylinder(radius=0.0085, length=0.024),
                origin=Origin(
                    xyz=(
                        bolt_r_ring * math.cos(a),
                        bolt_r_ring * math.sin(a),
                        shelf_z - 0.006,
                    )
                ),
                material=mats["accent"],
                name=f"base_bolt_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
            )
    else:  # base_straight_sleeve
        skirt_r = r.barrel_r + 0.020
        flare_r = skirt_r + 0.012
        profile = [
            (0.0, 0.0),
            (flare_r, 0.0),
            (flare_r, 0.014),
            (skirt_r, 0.030),
            (skirt_r, _BASE_TOP_Z - 0.010),
            (r.barrel_r + 0.006, _BASE_TOP_Z),
            (0.0, _BASE_TOP_Z),
        ]
        body.visual(
            _lathe(profile, "base_sleeve"),
            material=mats["body"],
            name="base_sleeve", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )

    # ---- Ribbed barrel ----
    barrel_profile = [
        (0.0, _BASE_TOP_Z - 0.004),
        (r.barrel_r + 0.006, _BASE_TOP_Z - 0.004),
        (r.barrel_r, _BASE_TOP_Z + 0.010),
        (r.barrel_r, r.barrel_top_z - 0.010),
        (r.barrel_r + 0.004, r.barrel_top_z),
        (0.0, r.barrel_top_z),
    ]
    body.visual(_lathe(barrel_profile, "barrel"), material=mats["body"], name="barrel", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"))

    # cast rib bands (decoration; small embedded torus rings).
    rib_lo = _BASE_TOP_Z + 0.060
    rib_hi = r.barrel_top_z - 0.060
    for i in range(_N_RIBS):
        t = i / max(1, _N_RIBS - 1)
        z = rib_lo + t * (rib_hi - rib_lo)
        body.visual(
            mesh_from_geometry(
                TorusGeometry(r.barrel_r + 0.002, 0.008, tubular_segments=28), f"rib_{i}"
            ),
            origin=Origin(xyz=(0.0, 0.0, z)),
            material=mats["body"],
            name=f"rib_{i}", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )

    # ---- Valve chamber (widened) ----
    chamber_profile = [
        (0.0, r.chamber_bot_z),
        (r.barrel_r + 0.004, r.chamber_bot_z),
        (r.chamber_r, r.chamber_bot_z + 0.030),
        (r.chamber_r, r.chamber_top_z - 0.020),
        (r.chamber_r - 0.020, r.chamber_top_z),
        (0.0, r.chamber_top_z),
    ]
    body.visual(
        _lathe(chamber_profile, "valve_chamber"),
        material=mats["body"],
        name="valve_chamber", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
    )

    # ---- Bonnet flange ----
    flange_profile = [
        (0.0, r.chamber_top_z - 0.002),
        (r.bonnet_flange_r, r.chamber_top_z - 0.002),
        (r.bonnet_flange_r, r.chamber_top_z + 0.020),
        (r.bonnet_flange_r - 0.020, r.bonnet_base_z),
        (0.0, r.bonnet_base_z),
    ]
    body.visual(
        _lathe(flange_profile, "bonnet_flange"),
        material=mats["body"],
        name="bonnet_flange", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
    )

    # ---- Bonnet shape (Slot A) ----
    _emit_bonnet(body, r, mats)

    # ---- Outlet stubs / collars / tether eyes (fixed body visuals) ----
    specs = _outlet_specs(r)
    for i, spec in enumerate(specs):
        _emit_outlet_body_features(body, r, mats, i, spec)

    return body


def _emit_bonnet(body, r: ResolvedFireHydrantConfig, mats):
    z0 = r.bonnet_base_z
    if r.bonnet_shape == "bonnet_domed":
        dome_r = r.bonnet_flange_r - 0.012
        body.visual(
            mesh_from_geometry(DomeGeometry(dome_r), "bonnet_dome"),
            origin=Origin(xyz=(0.0, 0.0, z0 - 0.004)),
            material=mats["body"],
            name="bonnet_dome", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )
        # Boss rises from the flange top (z0) up through the dome shell so it
        # is anchored to solid geometry (not floating inside the hollow dome).
        boss_len = 0.116
        body.visual(
            Cylinder(radius=0.040, length=boss_len),
            origin=Origin(xyz=(0.0, 0.0, z0 + boss_len / 2.0 - 0.010)),
            material=mats["body"],
            name="nut_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )
    elif r.bonnet_shape == "bonnet_flat_bolted":
        cap_h = 0.028
        cap_r = r.bonnet_flange_r - 0.006
        profile = [
            (0.0, z0),
            (cap_r, z0),
            (cap_r, z0 + cap_h),
            (cap_r - 0.012, z0 + cap_h + 0.006),
            (0.0, z0 + cap_h + 0.006),
        ]
        body.visual(_lathe(profile, "bonnet_flat_cap"), material=mats["body"],
                    name="bonnet_flat_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"))
        n_cap_bolts = 8
        for i in range(n_cap_bolts):
            a = 2.0 * math.pi * i / n_cap_bolts
            body.visual(
                Cylinder(radius=0.0055, length=0.012),
                origin=Origin(
                    xyz=((cap_r - 0.012) * math.cos(a),
                         (cap_r - 0.012) * math.sin(a),
                         z0 + cap_h)
                ),
                material=mats["accent"],
                name=f"cap_bolt_{i}", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
            )
        body.visual(
            Cylinder(radius=0.036, length=0.026),
            origin=Origin(xyz=(0.0, 0.0, z0 + cap_h + 0.014)),
            material=mats["body"],
            name="nut_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )
    else:  # bonnet_pointed_cone
        cone_h = 0.300
        cap_r = r.bonnet_flange_r - 0.008
        profile = [
            (0.0, z0),
            (cap_r, z0),
            (cap_r - 0.004, z0 + 0.030),
            (0.022, z0 + cone_h - 0.040),
            (0.030, z0 + cone_h - 0.030),
            (0.0, z0 + cone_h),
        ]
        body.visual(_lathe(profile, "bonnet_cone"), material=mats["body"],
                    name="bonnet_cone", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"))
        body.visual(
            Cylinder(radius=0.030, length=0.040),
            origin=Origin(xyz=(0.0, 0.0, z0 + cone_h - 0.020)),
            material=mats["body"],
            name="nut_boss", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )


def _outlet_basis(spec: _OutletSpec):
    """Return (outward unit, tangent unit) for an outlet at given yaw."""
    c, s = math.cos(spec.yaw), math.sin(spec.yaw)
    outward = (c, s, 0.0)
    tangent = (-s, c, 0.0)
    return outward, tangent


def _outlet_mouth(r: ResolvedFireHydrantConfig, spec: _OutletSpec):
    """World-frame center of the outlet mouth (where the cap seats)."""
    outward, _ = _outlet_basis(spec)
    wall = r.chamber_r - 0.004
    mouth_dist = wall + _OUTLET_STUB_LEN
    return (
        outward[0] * mouth_dist,
        outward[1] * mouth_dist,
        spec.center_z,
    ), outward, mouth_dist


def _emit_outlet_body_features(body, r, mats, i, spec: _OutletSpec):
    outward, tangent = _outlet_basis(spec)
    wall = r.chamber_r - 0.004
    # Stub: a radial cylinder from the chamber wall outward.
    stub_len = _OUTLET_STUB_LEN
    mid = wall + stub_len * 0.5
    # Cylinder default axis is +Z; rotate so +Z -> outward (radial).
    rpy = _rpy_z_to(outward)
    body.visual(
        Cylinder(radius=spec.radius + 0.008, length=stub_len),
        origin=Origin(
            xyz=(outward[0] * mid, outward[1] * mid, spec.center_z),
            rpy=rpy,
        ),
        material=mats["body"],
        name=f"outlet_{i}_stub", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
    )
    # Collar ring at the mouth (decoration).
    mouth_dist = wall + stub_len
    body.visual(
        mesh_from_geometry(
            TorusGeometry(spec.radius + 0.006, 0.006, tubular_segments=24),
            f"outlet_{i}_collar",
        ),
        origin=Origin(
            xyz=(outward[0] * mouth_dist, outward[1] * mouth_dist, spec.center_z),
            rpy=rpy,
        ),
        material=mats["accent"],
        name=f"outlet_{i}_collar", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
    )
    # Tether eye: a small solid lug boss on the chamber wall, offset
    # tangentially / down, to anchor the chain tail. Embedded into the chamber
    # so it's supported, and solid so the chain tail link reliably contacts it.
    eye = _tether_eye_pos(r, spec)
    rpy_eye = _rpy_z_to(outward)
    body.visual(
        Cylinder(radius=0.014, length=0.026),
        origin=Origin(xyz=eye, rpy=rpy_eye),
        material=mats["accent"],
        name=f"outlet_{i}_tether", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
    )


def _tether_eye_pos(r: ResolvedFireHydrantConfig, spec: _OutletSpec):
    outward, tangent = _outlet_basis(spec)
    wall = r.chamber_r - 0.002
    eye_z = max(spec.center_z - 0.085, r.chamber_bot_z + 0.030)
    # tangential offset so it doesn't sit directly under the outlet bore.
    off = 0.030
    return (
        outward[0] * wall + tangent[0] * off,
        outward[1] * wall + tangent[1] * off,
        eye_z,
    )


def _rpy_z_to(direction):
    """rpy that rotates local +Z onto the given (unit) world direction.

    For a purely horizontal radial outward direction at yaw, this is a
    pitch of +90 deg about Y then yaw about Z. We compose as
    rpy=(0, pi/2, yaw): pitch +Z->+X, then yaw rotates +X to the outward dir.
    """
    dx, dy, dz = direction
    yaw = math.atan2(dy, dx)
    return (0.0, math.pi / 2.0, yaw)


# ---------------------------------------------------------------------------
# Operating nut (REVOLUTE about +Z).
# ---------------------------------------------------------------------------
def _build_operating_nut(model, r: ResolvedFireHydrantConfig, mats):
    nut = model.part("operating_nut")
    # Square-ish nut authored about its own part-frame origin (contains 0,0,0
    # so the joint-origin check is satisfied). Built as a short hex/box prism;
    # use a low-segment lathe square-ish frustum centered at z=0.
    half = _NUT_HALF
    h = _NUT_H
    # Octagonal nut profile (lathe), centered so visuals span z in [-h/2, h/2].
    profile = [
        (0.0, -h / 2.0),
        (half, -h / 2.0),
        (half * 1.06, 0.0),
        (half, h / 2.0),
        (0.0, h / 2.0),
    ]
    nut.visual(
        mesh_from_geometry(LatheGeometry(profile, segments=6), "operating_nut_body"),
        material=mats["accent"],
        name="operating_nut_body", material_class_id=("metal.brass_polished" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
    )
    # small chamfered top cap
    nut.visual(
        Cylinder(radius=half * 0.7, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, h / 2.0 - 0.002)),
        material=mats["accent"],
        name="operating_nut_cap", material_class_id=("metal.brass_polished" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
    )
    model.articulation(
        "operating_nut",
        ArticulationType.REVOLUTE,
        parent=model.get_part("body"),
        child=nut,
        origin=Origin(xyz=(0.0, 0.0, r.nut_seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=-math.pi, upper=math.pi),
    )
    return nut


# ---------------------------------------------------------------------------
# Outlet caps (PRISMATIC lift-off) + serial-REVOLUTE chain.
# ---------------------------------------------------------------------------
def _build_cap(model, r, mats, i, spec: _OutletSpec):
    """Build the lift-off cap part + PRISMATIC joint.

    The cap part frame is placed at the outlet mouth, oriented so its local
    +Z points radially outward (the lift-off / slide axis). Authored about
    the part-frame origin so the visuals contain (0,0,0).
    """
    cap = model.part(f"outlet_{i}_cap")
    rad = spec.radius
    # cap_body: a short lathe cup centered at z in [-cap_len/2, cap_len/2].
    half = _CAP_LEN / 2.0
    profile = [
        (0.0, -half),
        (rad + 0.004, -half),
        (rad + 0.006, 0.0),
        (rad - 0.002, half),
        (0.0, half),
    ]
    cap.visual(
        mesh_from_geometry(LatheGeometry(profile, segments=40), f"outlet_{i}_cap_body"),
        material=mats["body"],
        name=f"outlet_{i}_cap_body", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
    )

    style = r.outlet_cap_style
    if style == "cap_knurled_screw":
        # 6 knurl lug ribs around the rim (decoration, embedded).
        for j in range(6):
            a = 2.0 * math.pi * j / 6
            cap.visual(
                Cylinder(radius=0.004, length=_CAP_LEN * 0.8),
                origin=Origin(xyz=((rad - 0.002) * math.cos(a),
                                   (rad - 0.002) * math.sin(a), 0.0)),
                material=mats["body"],
                name=f"outlet_{i}_lug_{j}", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
            )
        # side chain ring
        cap.visual(
            mesh_from_geometry(TorusGeometry(0.010, 0.004, tubular_segments=18),
                               f"outlet_{i}_cap_ring"),
            origin=Origin(xyz=(rad + 0.002, 0.0, -half + 0.006),
                          rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"outlet_{i}_cap_ring", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
        )
        attach_local = (rad + 0.006, 0.0, -half + 0.006)
    elif style == "cap_storz_lever":
        # 2 storz lug ears projecting beyond the rim at 90/270.
        for j in range(2):
            a = math.radians(90.0 + 180.0 * j)
            cap.visual(
                Cylinder(radius=0.006, length=0.014),
                origin=Origin(xyz=((rad + 0.010) * math.cos(a),
                                   (rad + 0.010) * math.sin(a), 0.0),
                              rpy=(math.pi / 2.0, 0.0, a)),
                material=mats["body"],
                name=f"outlet_{i}_lug_{j}", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
            )
        cap.visual(
            mesh_from_geometry(TorusGeometry(0.010, 0.004, tubular_segments=18),
                               f"outlet_{i}_cap_ring"),
            origin=Origin(xyz=(rad + 0.002, 0.0, -half + 0.006),
                          rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"outlet_{i}_cap_ring", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
        )
        attach_local = (rad + 0.006, 0.0, -half + 0.006)
    else:  # cap_plain_dome_bail
        # smooth dome cap + single top bail loop (no lug, no side ring).
        cap.visual(
            mesh_from_geometry(DomeGeometry(rad - 0.002), f"outlet_{i}_cap_dome"),
            origin=Origin(xyz=(0.0, 0.0, half - 0.006)),
            material=mats["body"],
            name=f"outlet_{i}_cap_dome", material_class_id=("metal.paint_coated" if r.palette_style in {"municipal_red", "high_vis_yellow", "safety_green", "industrial_blue", "matte_black"} else "metal.chrome_polished"),
        )
        cap.visual(
            mesh_from_geometry(TorusGeometry(0.012, 0.004, tubular_segments=18),
                               f"outlet_{i}_cap_bail"),
            origin=Origin(xyz=(0.0, 0.0, half + 0.006), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name=f"outlet_{i}_cap_bail", material_class_id=("metal.brass_aged" if r.palette_style in {"municipal_red", "silver_chrome", "safety_green", "matte_black"} else "metal.stainless_matte"),
        )
        attach_local = (0.0, 0.012, half + 0.006)

    # PRISMATIC joint: origin at outlet mouth, local +Z = outward (radial).
    mouth, outward, _ = _outlet_mouth(r, spec)
    rpy = _rpy_z_to(outward)
    model.articulation(
        f"outlet_{i}_cap",
        ArticulationType.PRISMATIC,
        parent=model.get_part("body"),
        child=cap,
        origin=Origin(xyz=mouth, rpy=rpy),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=0.0, upper=_CAP_TRAVEL),
    )

    # The world position of the cap attach point (chain root) at seated pose.
    attach_world = _local_to_world(mouth, rpy, attach_local)
    return cap, attach_world


def _local_to_world(origin_xyz, rpy, local):
    """Apply rpy (XYZ extrinsic) then translation to a local point."""
    rx, ry, rz = rpy
    x, y, z = local
    # Rx
    cy, sy = math.cos(rx), math.sin(rx)
    y, z = y * cy - z * sy, y * sy + z * cy
    # Ry
    cy, sy = math.cos(ry), math.sin(ry)
    x, z = x * cy + z * sy, -x * sy + z * cy
    # Rz
    cy, sy = math.cos(rz), math.sin(rz)
    x, y = x * cy - y * sy, x * sy + y * cy
    return (origin_xyz[0] + x, origin_xyz[1] + y, origin_xyz[2] + z)


def _build_chain(model, r, mats, i, spec: _OutletSpec, attach_world):
    """Serial-REVOLUTE round-link chain from cap attach -> body tether eye.

    Links are overlapping torus rings strung along the straight line from
    attach point to the eye. The root link is REVOLUTE-attached to the cap; each
    subsequent link is REVOLUTE-attached to the previous link.
    """
    eye = _tether_eye_pos(r, spec)
    ax, ay, az = attach_world
    ex, ey, ez = eye
    span = math.sqrt((ex - ax) ** 2 + (ey - ay) ** 2 + (ez - az) ** 2)
    m = max(5, round(span / _CHAIN_LINK_STEP))
    step = span / m  # actual per-link advance
    # unit direction from attach toward eye
    if span < 1e-6:
        ux, uy, uz = (0.0, 0.0, -1.0)
    else:
        ux, uy, uz = (ex - ax) / span, (ey - ay) / span, (ez - az) / span

    # Ring radius is large enough for neighboring links to interpenetrate, but
    # we intentionally avoid a filled sphere core: the hydrant tether should
    # read as chain links, not a ball/bead chain.
    link_r = max(_CHAIN_LINK_R * 0.75, step * 0.42)
    tube_r = min(0.0034, link_r * 0.38)

    parent_part = model.get_part(f"outlet_{i}_cap")
    prev_world = (ax, ay, az)
    prev_part = parent_part
    parts = []
    joints = []
    for j in range(m):
        link = model.part(f"outlet_{i}_chain_{j}")
        # Round link authored about its own origin. Alternate planes so the
        # strand reads as interlocked metal chain rather than stacked washers.
        link_rpy = (
            (math.pi / 2.0, 0.0, 0.0)
            if j % 2 == 0
            else (0.0, math.pi / 2.0, 0.0)
        )
        link.visual(
            mesh_from_geometry(
                TorusGeometry(link_r, tube_r, tubular_segments=14),
                f"outlet_{i}_chain_{j}_link",
            ),
            origin=Origin(rpy=link_rpy),
            material=mats["chain"],
            name=f"outlet_{i}_chain_{j}_link", material_class_id="metal.mesh_chainmail",
        )
        # World center of this link.
        link_world = (
            ax + ux * step * (j + 1),
            ay + uy * step * (j + 1),
            az + uz * step * (j + 1),
        )
        # Joint origin = previous link's center, expressed in parent frame.
        if j == 0:
            # parent is the cap part; we grandfather the mating (pin-in-eye
            # style) so no MatingContract. Joint origin in cap-local frame.
            # Easiest: place origin at the link bead start in WORLD via the
            # parent part. But articulation origin is in parent frame. The cap
            # part frame == mouth frame; transform attach_world back is complex,
            # so instead parent the whole chain to body and offset.
            pass
        axis = (1.0, 0.0, 0.0) if j % 2 == 0 else (0.0, 1.0, 0.0)
        model.articulation(
            f"outlet_{i}_chain_{j}",
            ArticulationType.REVOLUTE,
            parent=prev_part,
            child=link,
            origin=Origin(xyz=_delta(prev_world, link_world)),
            axis=axis,
            motion_limits=MotionLimits(lower=-math.radians(35), upper=math.radians(35)),
        )
        parts.append(link.name)
        joints.append(f"outlet_{i}_chain_{j}")
        prev_world = link_world
        prev_part = link
    return parts, joints


def _delta(a, b):
    return (b[0] - a[0], b[1] - a[1], b[2] - a[2])


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_fire_hydrant(
    config: FireHydrantConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"fire_hydrant_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    _build_body(model, r, mats)
    _build_operating_nut(model, r, mats)

    specs = _outlet_specs(r)
    for i, spec in enumerate(specs):
        _cap, attach_world = _build_cap(model, r, mats, i, spec)
        _build_chain(model, r, mats, i, spec, attach_world)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_fire_hydrant(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_fire_hydrant(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_fire_hydrant_tests(
    object_model: ArticulatedObject,
    config: FireHydrantConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")
    specs = _outlet_specs(r)

    # ---- Allowances (element-scoped). ----
    nut = object_model.get_part("operating_nut")
    ctx.allow_overlap(
        nut, body,
        reason="the operating nut seats on the bonnet nut_boss (captured seating).",
    )

    for i, spec in enumerate(specs):
        cap = object_model.get_part(f"outlet_{i}_cap")
        # The lifted cap (with its chain tether) leaves the outlet stub.
        ctx.allow_isolated_part(
            cap,
            reason=f"outlet {i} cap lifts off the outlet stub and loses contact",
        )
        for chain_part in (
            p for p in object_model.parts if p.name.startswith(f"outlet_{i}_chain_")
        ):
            ctx.allow_isolated_part(
                chain_part,
                reason=f"outlet {i} chain tether hangs free when the cap is lifted",
            )
        # cap seats over the outlet stub when closed.
        ctx.allow_overlap(
            cap, body,
            reason=f"outlet {i} cap seats over the outlet stub/collar when closed.",
        )
        # chain link <-> cap (root link captured at the cap ring/bail).
        link0 = object_model.get_part(f"outlet_{i}_chain_0")
        ctx.allow_overlap(
            link0, cap,
            reason=f"outlet {i} chain root link is captured at the cap ring/bail.",
        )
        # chain links overlap each other and drape against the body.
        chain_parts = [
            p for p in object_model.parts
            if p.name.startswith(f"outlet_{i}_chain_")
        ]
        for a in range(len(chain_parts)):
            if a + 1 < len(chain_parts):
                ctx.allow_overlap(
                    chain_parts[a], chain_parts[a + 1],
                    reason="consecutive chain links overlap to form a continuous strand.",
                )
            ctx.allow_overlap(
                chain_parts[a], body,
                reason="chain drapes against the body / tether eye.",
            )
            ctx.allow_overlap(
                chain_parts[a], cap,
                reason="chain drapes against the cap.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("body chassis present", "body" in part_names)
    ctx.check("operating_nut present", "operating_nut" in part_names)

    # operating nut REVOLUTE about +Z.
    jn = object_model.get_articulation("operating_nut")
    ctx.check(
        "operating nut REVOLUTE about +Z",
        jn.articulation_type == ArticulationType.REVOLUTE and abs(jn.axis[2]) > 0.99,
        details=f"type={jn.articulation_type} axis={tuple(jn.axis)}",
    )

    # N caps present, each PRISMATIC; lift-off slides straight.
    ctx.check(
        "N outlet caps present",
        all(f"outlet_{i}_cap" in part_names for i in range(r.outlet_count)),
        details=f"N={r.outlet_count}",
    )
    for i, spec in enumerate(specs):
        jc = object_model.get_articulation(f"outlet_{i}_cap")
        ctx.check(
            f"outlet {i} cap PRISMATIC",
            jc.articulation_type == ArticulationType.PRISMATIC,
            details=f"type={jc.articulation_type}",
        )
        cap = object_model.get_part(f"outlet_{i}_cap")
        p0 = ctx.part_world_position(cap)
        with ctx.pose({jc: _CAP_TRAVEL * 0.9}):
            p1 = ctx.part_world_position(cap)
        if p0 is not None and p1 is not None:
            outward, _ = _outlet_basis(spec)
            # displacement should be along outward (radial), lateral small.
            dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
            along = dx * outward[0] + dy * outward[1] + dz * outward[2]
            lateral = math.sqrt(
                max(0.0, (dx * dx + dy * dy + dz * dz) - along * along)
            )
            ctx.check(
                f"outlet {i} cap lifts off straight along outlet axis",
                along > 0.060 and lateral < 0.006,
                details=f"along={along:.4f} lateral={lateral:.5f}",
            )
        # chain present + serial REVOLUTE.
        chain0 = f"outlet_{i}_chain_0"
        ctx.check(
            f"outlet {i} has a tether chain",
            chain0 in part_names,
        )
        chain_count = sum(
            1 for p in object_model.parts if p.name.startswith(f"outlet_{i}_chain_")
        )
        chain_visual_names = {
            visual.name
            for j in range(chain_count)
            for visual in object_model.get_part(f"outlet_{i}_chain_{j}").visuals
        }
        ctx.check(
            f"outlet {i} chain uses ring links, not ball cores",
            all(not name.endswith("_core") for name in chain_visual_names),
            details=str(sorted(chain_visual_names)),
        )
        jch = object_model.get_articulation(chain0)
        ctx.check(
            f"outlet {i} chain links are REVOLUTE",
            jch.articulation_type == ArticulationType.REVOLUTE,
            details=f"type={jch.articulation_type}",
        )

    # ---- Ground contact. ----
    aabb = ctx.part_world_aabb(body)
    if aabb is not None:
        (_, _, zmn), (_, _, zmx) = aabb
        ctx.check("body rests on the ground (z~0)", zmn < 0.012,
                  details=f"z_min={zmn:.4f}")
        # pillar identity: tall vertical body.
        ctx.check("body is a tall pillar", zmx > 0.80, details=f"z_max={zmx:.4f}")

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with N encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "FireHydrantConfig",
    "ResolvedFireHydrantConfig",
    "build_fire_hydrant",
    "build_seeded_fire_hydrant",
    "config_from_seed",
    "resolve_config",
    "run_fire_hydrant_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
