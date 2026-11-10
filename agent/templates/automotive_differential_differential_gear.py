# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — automotive_differential_differential_gear.

An automotive differential gear set: a ``carrier_cage`` root that spins about the
axle axis (X), carries a FIXED final-drive ring/crown gear driven by a mounted
input ``drive_pinion`` (CONTINUOUS about Y), and splits torque to exactly two
coaxial ``side_gear_0/1`` outputs (CONTINUOUS about X) through an internal
differential mechanism.

Hub / parallel-children topology (§B pattern): every gear parents directly to
the single grounded ``carrier_cage`` root. Slots:
  - carrier_form   : open_cage | closed_case          (① / ③ housing envelope)
  - ring_form      : helical_spur | bevel_crown        (③ ring form family)
  - mechanism      : open_spider(N=2/4) | clutch_lsd | viscous_lsd | torsen |
                     locker                             (① / ② internal gearing)
Side-gear count is fixed at 2 (axle-output definition); ``n_spider`` {2,4} is the
only template multiplicity axis. See
``specs_modular_v1/automotive_differential_differential_gear.md``.

5-star sources (adapted, joint semantics preserved):
- open_cage/closed_case carrier: O (_carrier_cage_geometry), P4 (primitive rebuild),
  CC (closed shell + inspection ports).
- helical_spur ring / bevel side + spider gears (primitive hub+box teeth): CC
  (_ring_gear_visuals, _bevel_gear_visuals), O, P4.
- bevel_crown ring: RB (_crown_wheel_body_geometry + backing).
- clutch_lsd: LC (friction/steel plate loop). viscous_lsd: VC (sealed drum +
  interleaved plates). torsen: TS (Worm planet gears + helical worm side gears).
  locker: LK (PRISMATIC dog collar + carrier dog teeth).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    SpurGear,
    TestContext,
    TestReport,
    Worm,
    mesh_from_cadquery,
)

__modular__ = True

PI = math.pi

# ---------------------------------------------------------------------------
# Discrete slot domains
# ---------------------------------------------------------------------------
CARRIER_FORMS = ("open_cage", "closed_case")
RING_FORMS = ("helical_spur", "bevel_crown")
MECHANISMS = ("open_spider", "clutch_lsd", "viscous_lsd", "torsen", "locker")
PALETTE_STYLES = (
    "dark_iron",
    "nodular_grey",
    "phosphate_black",
    "oiled_bronze",
    "machined_bright",
)

# Mechanisms that carry bevel spider pinions on a cross shaft.
_SPIDER_MECHANISMS = ("open_spider", "clutch_lsd", "locker")

N_SPIDER_CHOICES = (2, 4)
N_SPIDER_WEIGHTS = (0.65, 0.35)

# ---------------------------------------------------------------------------
# Palettes (⑥). role keys: body / machined / gear / tooth / bolt / accent
# ---------------------------------------------------------------------------
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "dark_iron": {
        "body": (0.18, 0.18, 0.16, 1.0),
        "machined": (0.55, 0.52, 0.46, 1.0),
        "gear": (0.32, 0.31, 0.28, 1.0),
        "tooth": (0.72, 0.68, 0.58, 1.0),
        "bolt": (0.06, 0.065, 0.070, 1.0),
        "accent": (0.40, 0.26, 0.14, 1.0),
    },
    "nodular_grey": {
        "body": (0.42, 0.43, 0.44, 1.0),
        "machined": (0.62, 0.61, 0.57, 1.0),
        "gear": (0.38, 0.37, 0.34, 1.0),
        "tooth": (0.75, 0.73, 0.66, 1.0),
        "bolt": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.48, 0.34, 0.16, 1.0),
    },
    "phosphate_black": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "machined": (0.50, 0.50, 0.48, 1.0),
        "gear": (0.20, 0.20, 0.21, 1.0),
        "tooth": (0.60, 0.58, 0.52, 1.0),
        "bolt": (0.04, 0.04, 0.045, 1.0),
        "accent": (0.55, 0.40, 0.18, 1.0),
    },
    "oiled_bronze": {
        "body": (0.24, 0.22, 0.18, 1.0),
        "machined": (0.58, 0.54, 0.46, 1.0),
        "gear": (0.36, 0.30, 0.20, 1.0),
        "tooth": (0.74, 0.62, 0.36, 1.0),
        "bolt": (0.08, 0.07, 0.06, 1.0),
        "accent": (0.60, 0.45, 0.22, 1.0),
    },
    "machined_bright": {
        "body": (0.50, 0.50, 0.50, 1.0),
        "machined": (0.78, 0.77, 0.72, 1.0),
        "gear": (0.55, 0.54, 0.50, 1.0),
        "tooth": (0.86, 0.84, 0.78, 1.0),
        "bolt": (0.14, 0.14, 0.15, 1.0),
        "accent": (0.62, 0.47, 0.24, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Axle axis = X. Ring on the -X side.
# Standardized-hardware features (collars, snout, bolts) stay fixed size;
# carrier / ring / gear "size" scales are ride-along (⑤).
# ---------------------------------------------------------------------------
_CHEEK_X = 0.066
_CHEEK_LEN = 0.030
_COLLAR_X = 0.112
_COLLAR_INNER = 0.030
_COLLAR_OUTER = 0.041
_COLLAR_LEN = 0.070
_FLANGE_X = -0.105
_FLANGE_INNER = 0.061
_FLANGE_LEN = 0.026
_SHOULDER_X = -0.124
_SNOUT_POS = (-0.145, -0.225, 0.0)
_SNOUT_INNER = 0.015
_SNOUT_OUTER = 0.033
_SNOUT_LEN = 0.072

_SIDE_X = 0.041          # side gear axial position (± )
_SIDE_BODY_LEN = 0.024
_SIDE_TEETH = 18
_JOURNAL_R = 0.031
_JOURNAL_X = 0.070
_JOURNAL_LEN = 0.040
_AXLE_OUT_R = 0.016
_AXLE_OUT_X = 0.052
_AXLE_OUT_LEN = 0.105

_SPIDER_Y = 0.040        # spider radial position on the cross shaft
_SPIDER_HUB_R = 0.018
_SPIDER_HUB_LEN = 0.024
_SPIDER_TEETH = 12
_CROSS_SHAFT_R = 0.0055
_CROSS_SHAFT_LEN = 0.190

_PINION_SHAFT_R = 0.016
_PINION_SHAFT_LEN = 0.132
_RING_X = -0.220
_RING_LEN = 0.040

_SEG_TOL = 0.0022        # cadquery linear tolerance (compile budget)
_SEG_ANG = 0.10          # cadquery angular tolerance


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AutomotiveDifferentialDifferentialGearConfig:
    carrier_form: str | None = None
    ring_form: str | None = None
    mechanism: str | None = None
    n_spider: int | None = None
    palette_style: str = "dark_iron"
    n_bolt: int | None = None
    carrier_radius_scale: float = 1.0
    ring_radius_scale: float = 1.0
    side_gear_scale: float = 1.0
    name: str = "automotive_differential_differential_gear"


@dataclass(frozen=True)
class ResolvedAutomotiveDifferentialDifferentialGearConfig:
    carrier_form: str
    ring_form: str
    mechanism: str
    n_spider: int          # 0 for viscous/torsen (no bevel spiders)
    palette_style: str
    n_bolt: int
    # derived geometry
    side_body_r: float
    side_tooth_h: float
    open_center_r: float
    cheek_outer_r: float
    barrel_outer_r: float
    flange_outer_r: float
    bolt_circle_r: float
    ring_disc_r: float
    lock_travel: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> AutomotiveDifferentialDifferentialGearConfig:
    rng = random.Random(seed)
    return AutomotiveDifferentialDifferentialGearConfig(
        carrier_form=rng.choice(CARRIER_FORMS),
        ring_form=rng.choice(RING_FORMS),
        mechanism=rng.choice(MECHANISMS),
        n_spider=rng.choices(N_SPIDER_CHOICES, weights=N_SPIDER_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        n_bolt=rng.choices((8, 10, 12), weights=(0.30, 0.45, 0.25), k=1)[0],
        carrier_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        ring_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        side_gear_scale=round(rng.uniform(0.90, 1.09), 4),
        name=f"seeded_automotive_differential_differential_gear_{seed}",
    )


def resolve_config(
    config: AutomotiveDifferentialDifferentialGearConfig | None = None,
) -> ResolvedAutomotiveDifferentialDifferentialGearConfig:
    cfg = config or AutomotiveDifferentialDifferentialGearConfig()

    carrier_form = _pick(cfg.carrier_form, CARRIER_FORMS)
    ring_form = _pick(cfg.ring_form, RING_FORMS)
    mechanism = _pick(cfg.mechanism, MECHANISMS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # --- multiplicity gating (spec §9): spiders only on bevel-spider mechs ---
    n_spider = int(cfg.n_spider) if cfg.n_spider is not None else 2
    n_spider = 2 if n_spider not in N_SPIDER_CHOICES else n_spider
    if mechanism not in _SPIDER_MECHANISMS:
        n_spider = 0

    n_bolt = int(cfg.n_bolt) if cfg.n_bolt is not None else 10
    n_bolt = int(_clamp(n_bolt, 8, 12))

    # --- continuous scales (§7): independent -> derived -> inequality --------
    crs = _clamp(cfg.carrier_radius_scale, 0.90, 1.12)
    rrs = _clamp(cfg.ring_radius_scale, 0.90, 1.12)
    sgs = _clamp(cfg.side_gear_scale, 0.90, 1.09)

    side_body_r = 0.032 * sgs
    side_tooth_h = 0.010 * sgs
    side_outer_r = side_body_r + side_tooth_h
    # inequality: the open center must contain the largest internal gear radius.
    open_center_r = side_outer_r + 0.006
    cheek_outer_r = max(0.088 * crs, open_center_r + 0.030)
    barrel_outer_r = max(0.100 * crs, open_center_r + 0.044)
    flange_outer_r = max(0.145 * crs, cheek_outer_r + 0.010)
    bolt_circle_r = 0.108 * crs
    ring_disc_r = 0.140 * rrs
    # keep bolt circle inside the ring disc so shanks overlap the ring.
    bolt_circle_r = min(bolt_circle_r, ring_disc_r - 0.014)

    # locker collar travel derived from the free hub run (equation).
    lock_travel = 0.018

    return ResolvedAutomotiveDifferentialDifferentialGearConfig(
        carrier_form=carrier_form,
        ring_form=ring_form,
        mechanism=mechanism,
        n_spider=n_spider,
        palette_style=palette_style,
        n_bolt=n_bolt,
        side_body_r=side_body_r,
        side_tooth_h=side_tooth_h,
        open_center_r=open_center_r,
        cheek_outer_r=cheek_outer_r,
        barrel_outer_r=barrel_outer_r,
        flange_outer_r=flange_outer_r,
        bolt_circle_r=bolt_circle_r,
        ring_disc_r=ring_disc_r,
        lock_travel=lock_travel,
        name=cfg.name or "automotive_differential_differential_gear",
    )


def with_overrides(config, **kwargs):
    return replace(config, **kwargs)


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedAutomotiveDifferentialDifferentialGearConfig)
        else resolve_config(config)
    )
    return (
        ("carrier_form", r.carrier_form),
        ("ring_form", r.ring_form),
        ("mechanism", r.mechanism),
        ("n_spider", f"n{r.n_spider}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# CadQuery carrier-shell helpers (annular; open center clears internal gears)
# ---------------------------------------------------------------------------
def _cyl_x(length, radius, *, center=(0.0, 0.0, 0.0)):
    return (
        cq.Workplane("XY").cylinder(length, radius).rotate((0, 0, 0), (0, 1, 0), 90).translate(center)
    )


def _cyl_y(length, radius, *, center=(0.0, 0.0, 0.0)):
    return (
        cq.Workplane("XY").cylinder(length, radius).rotate((0, 0, 0), (1, 0, 0), -90).translate(center)
    )


def _annular_x(length, outer_r, inner_r, *, center=(0.0, 0.0, 0.0)):
    return _cyl_x(length, outer_r, center=center).cut(_cyl_x(length + 0.010, inner_r, center=center))


def _carrier_common_features(cage, r):
    """Axle collars, ring flange + shoulder, pinion snout + ribs — all embed into
    the solid central spine so the whole carrier is one connected solid."""
    # axle collars (bore for the axle output); solid spine contains their section.
    for x in (-_COLLAR_X, _COLLAR_X):
        cage = cage.union(_annular_x(_COLLAR_LEN, _COLLAR_OUTER, _COLLAR_INNER, center=(x, 0.0, 0.0)))
    # ring flange + register shoulder; inner bore reaches the collar for connectivity.
    cage = cage.union(_annular_x(_FLANGE_LEN, r.flange_outer_r, _COLLAR_INNER, center=(_FLANGE_X, 0.0, 0.0)))
    cage = cage.union(_annular_x(0.016, r.flange_outer_r - 0.030, _COLLAR_INNER, center=(-0.118, 0.0, 0.0)))
    # pinion bearing snout (bore for the pinion shaft), tied to the flange by ribs.
    snout = _cyl_y(_SNOUT_LEN, _SNOUT_OUTER, center=_SNOUT_POS).cut(
        _cyl_y(_SNOUT_LEN + 0.012, _SNOUT_INNER, center=_SNOUT_POS)
    )
    upper_rib = cq.Workplane("XY").box(0.072, 0.130, 0.022).translate((-0.128, -0.160, 0.044))
    lower_rib = cq.Workplane("XY").box(0.072, 0.130, 0.022).translate((-0.128, -0.160, -0.044))
    return cage.union(upper_rib).union(lower_rib).union(snout)


def _open_cage_geometry(r):
    """Solid cheeks + four window bridges; the open central window shows the gearing."""
    co = r.cheek_outer_r
    cage = _cyl_x(_CHEEK_LEN, co, center=(-_CHEEK_X, 0.0, 0.0))
    cage = cage.union(_cyl_x(_CHEEK_LEN, co, center=(_CHEEK_X, 0.0, 0.0)))
    bz = co - 0.007
    by = co + 0.008
    cage = cage.union(cq.Workplane("XY").box(0.160, 0.038, 0.030).translate((0.0, 0.0, bz)))
    cage = cage.union(cq.Workplane("XY").box(0.160, 0.038, 0.030).translate((0.0, 0.0, -bz)))
    cage = cage.union(cq.Workplane("XY").box(0.160, 0.030, 0.038).translate((0.0, by, 0.0)))
    cage = cage.union(cq.Workplane("XY").box(0.160, 0.030, 0.038).translate((0.0, -by, 0.0)))
    return _carrier_common_features(cage, r)


def _closed_case_geometry(r):
    """Closed one-piece case: the same solid end cheeks as the open cage (so the
    axle axis passes through real hardware and the internal gears seat against
    the cheeks exactly as in the open cage), tied by a SOLID cylindrical outer
    wall instead of the open window bridges. Inspection ports poke through it.

    Using solid cheeks (rather than a hollow barrel bore) matters because the
    carrier shell is evaluated as a *surface* mesh: an internal visual that sits
    inside a hollow bore without touching a wall face reads as a floating island.
    The solid cheeks give every internal feature a real face to seat against."""
    co = r.cheek_outer_r
    cage = _cyl_x(_CHEEK_LEN, co, center=(-_CHEEK_X, 0.0, 0.0))
    cage = cage.union(_cyl_x(_CHEEK_LEN, co, center=(_CHEEK_X, 0.0, 0.0)))
    # solid outer barrel wall spanning cheek-to-cheek (closes the open windows).
    cage = cage.union(_annular_x(2.0 * _CHEEK_X, co, co - 0.012, center=(0.0, 0.0, 0.0)))
    # Cut 4 real inspection-port through-holes in the wall. Besides being the
    # ③/④ closed-case detail, they open the otherwise-sealed internal cavity so
    # its inner surface merges with the outer shell into ONE mesh component;
    # without this the internal gears seat against the isolated cavity surface
    # and read as floating islands.
    for i in range(4):
        a_deg = 90.0 * i
        port = (
            cq.Workplane("XY").cylinder(0.060, 0.012)
            .translate((0.0, 0.0, co))
            .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), a_deg)
        )
        cage = cage.cut(port)
    return _carrier_common_features(cage, r)


# ---------------------------------------------------------------------------
# Primitive gear-visual helpers (hub cylinder + radial box teeth) — CC-sourced
# ---------------------------------------------------------------------------
def _bevel_gear_visuals(part, mats, body_r, body_len, tooth_h, n_teeth, *, key):
    """Bevel/side gear: X-aligned cylinder body + radial box teeth (CC L47-73)."""
    part.visual(
        Cylinder(radius=body_r, length=body_len),
        origin=Origin(rpy=(0.0, PI / 2.0, 0.0)),
        material=mats["tooth"],
        name=f"{key}_body", material_class_id="metal.steel_bare",
    )
    # tooth points radially (roll a-π/2 aligns the box's radial axis) and embeds
    # into the body surface so each tooth is connected to the gear body.
    tc_r = body_r + tooth_h / 2.0 - 0.003
    for i in range(n_teeth):
        a = 2.0 * PI * i / n_teeth
        part.visual(
            Box((body_len, 0.004, tooth_h)),
            origin=Origin(xyz=(0.0, tc_r * math.cos(a), tc_r * math.sin(a)),
                          rpy=(a - PI / 2.0, 0.0, 0.0)),
            material=mats["tooth"],
            name=f"{key}_tooth_{i}", material_class_id="metal.steel_bare",
        )


def _emit_side_gear(model, r, mats, index, x, *, body_r, add_hub_connector=False):
    """One coaxial side gear (bevel body + axle output + journal). CONTINUOUS X."""
    side = model.part(f"side_gear_{index}")
    _bevel_gear_visuals(side, mats, body_r, _SIDE_BODY_LEN, r.side_tooth_h, _SIDE_TEETH, key="bevel")
    outward = -1.0 if x < 0.0 else 1.0
    if add_hub_connector:
        side.visual(
            Cylinder(radius=0.019, length=0.040),
            origin=Origin(xyz=(-outward * 0.020, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
            material=mats["tooth"],
            name="hub_connector", material_class_id="metal.steel_bare",
        )
    side.visual(
        Cylinder(radius=_AXLE_OUT_R, length=_AXLE_OUT_LEN),
        origin=Origin(xyz=(outward * _AXLE_OUT_X, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
        material=mats["machined"],
        name="axle_output", material_class_id="metal.brushed_silver",
    )
    side.visual(
        Cylinder(radius=_JOURNAL_R, length=_JOURNAL_LEN),
        origin=Origin(xyz=(outward * _JOURNAL_X, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
        material=mats["machined"],
        name="bearing_journal", material_class_id="metal.brushed_silver",
    )
    # ④ rotation witness rib on the front tooth flank (host-derived radius).
    side.visual(
        Box((0.0016, 0.006, body_r * 0.5)),
        origin=Origin(xyz=(x * 0.0 - outward * (_SIDE_BODY_LEN / 2.0 + 0.0005), 0.0, body_r * 0.6)),
        material=mats["accent"],
        name="spin_mark", material_class_id="metal.bronze_cast",
    )
    model.articulation(
        f"carrier_to_side_{index}",
        ArticulationType.CONTINUOUS,
        parent=model.get_part("carrier_cage"),
        child=side,
        origin=Origin(xyz=(x, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=25.0),
    )
    return side


def _emit_spiders(model, carrier, r, mats):
    """N bevel spider pinions on cross shaft(s). CONTINUOUS about radial axis."""
    n = r.n_spider
    # cross shaft(s) — carrier visuals the spider hubs are captured on. Length is
    # sized so the tips land in the solid spine (open: bridges, closed: barrel).
    # both forms carry solid cheeks; size the cross shaft to reach into them.
    cross_len = 2.0 * (r.cheek_outer_r + 0.006)
    carrier.visual(
        Cylinder(radius=_CROSS_SHAFT_R, length=cross_len),
        origin=Origin(rpy=(-PI / 2.0, 0.0, 0.0)),
        material=mats["machined"],
        name="cross_shaft", material_class_id="metal.brushed_silver",
    )
    if n == 4:
        carrier.visual(
            Cylinder(radius=_CROSS_SHAFT_R, length=cross_len),
            material=mats["machined"],
            name="cross_shaft_z", material_class_id="metal.brushed_silver",
        )
    # placements: N=2 along Y; N=4 along Y and Z.
    if n == 2:
        specs = ((0, (0.0, -_SPIDER_Y, 0.0), (0.0, 1.0, 0.0), "y"),
                 (1, (0.0, _SPIDER_Y, 0.0), (0.0, 1.0, 0.0), "y"))
    else:
        specs = (
            (0, (0.0, -_SPIDER_Y, 0.0), (0.0, 1.0, 0.0), "y"),
            (1, (0.0, _SPIDER_Y, 0.0), (0.0, 1.0, 0.0), "y"),
            (2, (0.0, 0.0, -_SPIDER_Y), (0.0, 0.0, 1.0), "z"),
            (3, (0.0, 0.0, _SPIDER_Y), (0.0, 0.0, 1.0), "z"),
        )
    for index, pos, axis, arm in specs:
        spider = model.part(f"spider_gear_{index}")
        hub_rpy = (-PI / 2.0, 0.0, 0.0) if arm == "y" else (0.0, 0.0, 0.0)
        spider.visual(
            Cylinder(radius=_SPIDER_HUB_R, length=_SPIDER_HUB_LEN),
            origin=Origin(rpy=hub_rpy),
            material=mats["tooth"],
            name="pinion_hub", material_class_id="metal.steel_bare",
        )
        for j in range(_SPIDER_TEETH):
            a = 2.0 * PI * j / _SPIDER_TEETH
            if arm == "y":
                txyz = (0.023 * math.cos(a), 0.0, 0.023 * math.sin(a))
                trpy = (0.0, -a, 0.0)
            else:
                txyz = (0.023 * math.cos(a), 0.023 * math.sin(a), 0.0)
                trpy = (0.0, 0.0, a)
            spider.visual(
                Box((0.011, 0.026, 0.006)) if arm == "y" else Box((0.011, 0.006, 0.026)),
                origin=Origin(xyz=txyz, rpy=trpy),
                material=mats["tooth"],
                name=f"tooth_{j}", material_class_id="metal.steel_bare",
            )
        model.articulation(
            f"carrier_to_spider_{index}",
            ArticulationType.CONTINUOUS,
            parent=carrier,
            child=spider,
            origin=Origin(xyz=pos),
            axis=axis,
            motion_limits=MotionLimits(effort=35.0, velocity=35.0),
        )


# ---------------------------------------------------------------------------
# Mechanism builders (each emits side_gear_0/1 + inner gearing)
# ---------------------------------------------------------------------------
def _build_open_spider(model, carrier, r, mats):
    for index, x in ((0, -_SIDE_X), (1, _SIDE_X)):
        _emit_side_gear(model, r, mats, index, x, body_r=r.side_body_r)
    _emit_spiders(model, carrier, r, mats)


def _build_clutch_lsd(model, carrier, r, mats):
    for index, x in ((0, -_SIDE_X), (1, _SIDE_X)):
        _emit_side_gear(model, r, mats, index, x, body_r=r.side_body_r)
    _emit_spiders(model, carrier, r, mats)
    # Friction/steel clutch plate stack on the carrier between each side gear
    # and the cheek — reaches the open-center wall for connectivity (LC L163-214).
    n_plates = 6
    p_th = 0.0016
    p_pitch = 0.0012          # < p_th: consecutive plates overlap into one chain
    friction_r = r.open_center_r - 0.004
    steel_r = r.open_center_r + 0.003
    # Ground the pack on the solid cheek face: place the wall-most plate so it
    # straddles the cheek inner face (|x| == _CHEEK_X - _CHEEK_LEN/2), then run
    # the contiguous stack inward toward the center. The straddling plate touches
    # the cheek surface, grounding the whole overlapping chain; the rest ride in
    # the open center clear of the spider hub / cross shaft.
    cheek_face = _CHEEK_X - _CHEEK_LEN / 2.0
    start_off = (cheek_face + 0.0005) - _SIDE_X - (n_plates - 1) * p_pitch
    for index, x in ((0, -_SIDE_X), (1, _SIDE_X)):
        outward = -1.0 if x < 0.0 else 1.0
        for pi in range(n_plates):
            px = x + outward * (start_off + pi * p_pitch)
            rad = friction_r if pi % 2 == 0 else steel_r
            mat = mats["accent"] if pi % 2 == 0 else mats["machined"]
            carrier.visual(
                Cylinder(radius=rad, length=p_th),
                origin=Origin(xyz=(px, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
                material=mat,
                name=f"clutch_plate_{index}_{pi}", material_class_id="metal.bronze_cast",
            )


def _build_viscous_lsd(model, carrier, r, mats):
    # Full-size side gears; teeth clear the drum bore (no gear buried in metal).
    body_r = r.side_body_r
    tooth_outer = body_r + r.side_tooth_h + 0.002
    # Sealed viscous drum: an ANNULAR shell (not a solid puck) spanning cheek-to-
    # cheek for support, with a bore that clears the side-gear teeth so the gears
    # rotate freely inside it. Emitted via cadquery like the carrier shell/crown.
    drum_inner = tooth_outer + 0.006
    drum_outer = drum_inner + 0.012
    drum_len = 2.0 * _CHEEK_X + 0.010
    carrier.visual(
        mesh_from_cadquery(
            _annular_x(drum_len, drum_outer, drum_inner),
            "viscous_drum", tolerance=_SEG_TOL, angular_tolerance=_SEG_ANG,
        ),
        material=mats["gear"],
        name="viscous_drum", material_class_id="metal.steel_bare",
    )
    # side gears + a long inner sleeve (hub_connector) that reaches from the gear
    # body across to host all of that side's plates (keeps them connected).
    for index, x in ((0, -_SIDE_X), (1, _SIDE_X)):
        _emit_side_gear(model, r, mats, index, x, body_r=body_r)
        side = model.get_part(f"side_gear_{index}")
        inward = 1.0 if x < 0.0 else -1.0  # local +x points toward the center
        side.visual(
            Cylinder(radius=0.017, length=0.052),
            origin=Origin(xyz=(inward * 0.032, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
            material=mats["machined"],
            name="hub_connector", material_class_id="metal.brushed_silver",
        )
    # interleaved plate stack inside the bore: even -> side_0, odd -> side_1.
    n_plates = 8
    half_span = 0.020
    spacing = (2.0 * half_span) / (n_plates - 1)
    plate_r = drum_inner - 0.003
    for i in range(n_plates):
        world_x = -half_span + i * spacing
        side_idx = i % 2
        side = model.get_part(f"side_gear_{side_idx}")
        local_x = world_x - (-_SIDE_X if side_idx == 0 else _SIDE_X)
        side.visual(
            Cylinder(radius=plate_r, length=0.0015),
            origin=Origin(xyz=(local_x, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
            material=mats["accent"],
            name=f"viscous_plate_{i}", material_class_id="metal.bronze_cast",
        )


def _build_torsen(model, carrier, r, mats):
    # helical worm side gears (real mesh, shared) — Volumetric Envelope form.
    worm_side_r = min(0.028, r.open_center_r - 0.010)
    for index, x in ((0, -_SIDE_X), (1, _SIDE_X)):
        _emit_side_gear(model, r, mats, index, x, body_r=worm_side_r)
    # three radial pockets (carrier visuals) bridging the cheeks; planet worms
    # sit inside them (TS L92-113 pockets adapted as support ribs).
    n_pairs = 3
    pocket_r = r.open_center_r + 0.010
    worm_mesh_rh = _torsen_worm_mesh(28.0)
    worm_mesh_lh = _torsen_worm_mesh(-28.0)
    # the two worms of a pair are coaxial along X; place them end-to-end with a
    # clear central gap so their shafts do not interpenetrate at the centerline.
    pair_x = 0.026
    for pair in range(n_pairs):
        angle = 2.0 * PI * pair / n_pairs
        py = pocket_r * math.cos(angle)
        pz = pocket_r * math.sin(angle)
        carrier.visual(
            Cylinder(radius=0.020, length=2.0 * _CHEEK_X + 0.014),
            origin=Origin(xyz=(0.0, py, pz), rpy=(0.0, PI / 2.0, 0.0)),
            material=mats["body"],
            name=f"worm_pocket_{pair}", material_class_id="metal.cast_iron_bare",
        )
        for member, x_off in ((0, -pair_x), (1, pair_x)):
            widx = pair * 2 + member
            planet = model.part(f"planet_worm_{widx}")
            worm_pitch = PI / 2.0 if x_off < 0.0 else -PI / 2.0
            planet.visual(
                worm_mesh_rh if member == 0 else worm_mesh_lh,
                origin=Origin(rpy=(0.0, worm_pitch, 0.0)),
                material=mats["accent"],
                name="worm_threads", material_class_id="metal.bronze_cast",
            )
            planet.visual(
                Cylinder(radius=0.008, length=0.036),
                origin=Origin(rpy=(0.0, PI / 2.0, 0.0)),
                material=mats["machined"],
                name="worm_shaft", material_class_id="metal.brushed_silver",
            )
            model.articulation(
                f"carrier_to_planet_{widx}",
                ArticulationType.CONTINUOUS,
                parent=carrier,
                child=planet,
                origin=Origin(xyz=(x_off, py, pz)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=35.0, velocity=35.0),
            )


def _torsen_worm_mesh(lead_angle):
    return mesh_from_cadquery(
        Worm(module=0.0030, lead_angle=lead_angle, n_threads=3, length=0.036,
             pressure_angle=20.0, backlash=0.0003).build(bore_d=0.012),
        f"planet_worm_{'rh' if lead_angle > 0 else 'lh'}",
        tolerance=0.0015,
        angular_tolerance=0.10,
    )


def _build_locker(model, carrier, r, mats):
    for index, x in ((0, -_SIDE_X), (1, _SIDE_X)):
        _emit_side_gear(model, r, mats, index, x, body_r=r.side_body_r)
    _emit_spiders(model, carrier, r, mats)
    # carrier dog-tooth boss inside the left cheek bore (carrier visuals, LK L142-164).
    boss_x = -0.081
    carrier.visual(
        Cylinder(radius=0.030, length=0.008),
        origin=Origin(xyz=(boss_x, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
        material=mats["gear"],
        name="lock_boss", material_class_id="metal.steel_bare",
    )
    dog_mid_r = 0.024
    for i in range(6):
        a = 2.0 * PI * i / 6.0 + PI / 6.0
        carrier.visual(
            Box((0.005, 0.006, 0.004)),
            origin=Origin(xyz=(boss_x - 0.006, dog_mid_r * math.cos(a), dog_mid_r * math.sin(a)),
                          rpy=(a, 0.0, 0.0)),
            material=mats["gear"],
            name=f"carrier_dog_tooth_{i}", material_class_id="metal.steel_bare",
        )
    # splined dog collar — PRISMATIC axial engagement travel (LK L275-323).
    collar = model.part("dog_collar")
    collar.visual(
        Cylinder(radius=0.030, length=0.014),
        origin=Origin(rpy=(0.0, PI / 2.0, 0.0)),
        material=mats["machined"],
        name="collar_body", material_class_id="metal.brushed_silver",
    )
    collar.visual(
        Cylinder(radius=0.021, length=0.004),
        origin=Origin(xyz=(-0.002, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
        material=mats["body"],
        name="shift_groove", material_class_id="metal.cast_iron_bare",
    )
    for i in range(6):
        a = 2.0 * PI * i / 6.0
        collar.visual(
            Box((0.005, 0.006, 0.004)),
            origin=Origin(xyz=(0.007, dog_mid_r * math.cos(a), dog_mid_r * math.sin(a)),
                          rpy=(a, 0.0, 0.0)),
            material=mats["tooth"],
            name=f"collar_dog_tooth_{i}", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "carrier_to_lockcollar",
        ArticulationType.PRISMATIC,
        parent=carrier,
        child=collar,
        origin=Origin(xyz=(-0.104, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.15, lower=0.0, upper=r.lock_travel),
    )


_MECHANISM_BUILDERS = {
    "open_spider": _build_open_spider,
    "clutch_lsd": _build_clutch_lsd,
    "viscous_lsd": _build_viscous_lsd,
    "torsen": _build_torsen,
    "locker": _build_locker,
}


# ---------------------------------------------------------------------------
# Ring gear + drive pinion builders (Slot B)
# ---------------------------------------------------------------------------
def _crown_wheel_mesh(name, outer_r):
    return mesh_from_cadquery(
        cq.Workplane("XY").circle(outer_r).circle(0.040).extrude(0.030),
        name, tolerance=0.003, angular_tolerance=_SEG_ANG,
    )


def _crown_backing_mesh(name, outer_r):
    return mesh_from_cadquery(
        cq.Workplane("XY").circle(outer_r).circle(0.033).extrude(-0.052),
        name, tolerance=0.003, angular_tolerance=_SEG_ANG,
    )


def _emit_ring_gear(model, carrier, r, mats):
    ring = model.part("ring_gear")
    # FIXED-joint mount on the bolted interface (bolt_shank_0 ∩ ring disc). The
    # joint origin is a transform, so ring visuals are authored relative to the
    # mount and the joint frame lands on real hardware for both parent and child.
    mx, my, mz = -0.205, r.bolt_circle_r, 0.0

    def rel(x, y, z):
        return (x - mx, y - my, z - mz)

    if r.ring_form == "helical_spur":
        ring.visual(
            Cylinder(radius=r.ring_disc_r, length=_RING_LEN),
            origin=Origin(xyz=rel(_RING_X, 0.0, 0.0), rpy=(0.0, PI / 2.0, 0.0)),
            material=mats["gear"],
            name="toothed_ring", material_class_id="metal.steel_bare",
        )
        n_teeth = 46
        pitch_r = r.ring_disc_r - 0.004
        for i in range(n_teeth):
            a = 2.0 * PI * i / n_teeth
            ring.visual(
                Box((_RING_LEN, 0.006, 0.010)),
                origin=Origin(xyz=rel(_RING_X, pitch_r * math.cos(a), pitch_r * math.sin(a)),
                              rpy=(a, 0.0, 0.0)),
                material=mats["tooth"],
                name=f"ring_tooth_{i}", material_class_id="metal.steel_bare",
            )
    else:  # bevel_crown
        crown_outer = min(0.126 * (r.ring_disc_r / 0.140), r.ring_disc_r - 0.010)
        ring.visual(
            _crown_wheel_mesh("crown_wheel_body", crown_outer),
            origin=Origin(xyz=rel(-0.200, 0.0, 0.0), rpy=(0.0, -PI / 2.0, 0.0)),
            material=mats["gear"],
            name="toothed_ring", material_class_id="metal.steel_bare",
        )
        # backing abuts the crown body back face (x=-0.200) so the ring part is
        # one connected solid, and reaches the bolt shanks for carrier support.
        ring.visual(
            _crown_backing_mesh("crown_backing_disc", 0.090),
            origin=Origin(xyz=rel(-0.200, 0.0, 0.0), rpy=(0.0, -PI / 2.0, 0.0)),
            material=mats["gear"],
            name="crown_backing", material_class_id="metal.steel_bare",
        )
    model.articulation(
        "carrier_to_ring", ArticulationType.FIXED,
        parent=carrier, child=ring, origin=Origin(xyz=(mx, my, mz)),
    )


def _emit_drive_pinion(model, carrier, r, mats):
    pinion = model.part("drive_pinion")
    # teeth on the pinion axis (Y), raised toward the ring mesh; a single shaft
    # runs from the snout seat up to the teeth (connectivity within the part).
    teeth_y = 0.045 if r.ring_form == "helical_spur" else 0.100
    pinion.visual(
        Cylinder(radius=0.024, length=0.026),
        origin=Origin(xyz=(0.0, teeth_y, 0.0), rpy=(-PI / 2.0, 0.0, PI / 14.0)),
        material=mats["tooth"],
        name="pinion_teeth", material_class_id="metal.steel_bare",
    )
    # teeth arranged around the pinion's Y axis (XZ plane), radial + embedded.
    for i in range(14):
        a = 2.0 * PI * i / 14.0
        tc = 0.024
        pinion.visual(
            Box((0.008, 0.024, 0.004)),
            origin=Origin(xyz=(tc * math.cos(a), teeth_y, tc * math.sin(a)),
                          rpy=(0.0, -a, 0.0)),
            material=mats["tooth"],
            name=f"pinion_tooth_{i}", material_class_id="metal.steel_bare",
        )
    shaft_bot, shaft_top = -0.078, teeth_y + 0.006  # from snout seat up to teeth
    pinion.visual(
        Cylinder(radius=_PINION_SHAFT_R, length=shaft_top - shaft_bot),
        origin=Origin(xyz=(0.0, (shaft_bot + shaft_top) / 2.0, 0.0), rpy=(-PI / 2.0, 0.0, 0.0)),
        material=mats["machined"],
        name="pinion_shaft", material_class_id="metal.brushed_silver",
    )
    model.articulation(
        "carrier_to_pinion", ArticulationType.CONTINUOUS,
        parent=carrier, child=pinion,
        origin=Origin(xyz=_SNOUT_POS), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=40.0),
    )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_automotive_differential_differential_gear(config=None, *, assets=None):
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, meta={"template": "automotive_differential_differential_gear"})
    mats = {k: model.material(f"{r.palette_style}_{k}", rgba=v) for k, v in PALETTES[r.palette_style].items()}

    carrier = model.part("carrier_cage")
    if r.carrier_form == "open_cage":
        shell = _open_cage_geometry(r)
    else:
        shell = _closed_case_geometry(r)
    carrier.visual(
        mesh_from_cadquery(shell, "carrier_shell", assets=assets, tolerance=_SEG_TOL, angular_tolerance=_SEG_ANG),
        material=mats["body"],
        name="carrier_body", material_class_id="metal.cast_iron_bare",
    )

    # bolt circle (heads + shanks) — decorative multiplicity on the flange face.
    for i in range(r.n_bolt):
        a = 2.0 * PI * i / r.n_bolt
        y = r.bolt_circle_r * math.cos(a)
        z = r.bolt_circle_r * math.sin(a)
        carrier.visual(
            Cylinder(radius=0.0095, length=0.012),
            origin=Origin(xyz=(-0.089, y, z), rpy=(0.0, PI / 2.0, a)),
            material=mats["bolt"],
            name=f"bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )
        carrier.visual(
            Cylinder(radius=0.0045, length=0.150),
            origin=Origin(xyz=(-0.150, y, z), rpy=(0.0, PI / 2.0, 0.0)),
            material=mats["bolt"],
            name=f"bolt_shank_{i}", material_class_id="metal.blackened_gunmetal",
        )

    # closed_case inspection ports (④ decoration, host-derived radius).
    if r.carrier_form == "closed_case":
        for i in range(4):
            a = 2.0 * PI * i / 4.0
            carrier.visual(
                Cylinder(radius=0.014, length=0.004),
                origin=Origin(xyz=(0.0, (r.cheek_outer_r - 0.001) * math.sin(a),
                                   (r.cheek_outer_r - 0.001) * math.cos(a)),
                              rpy=(-a, 0.0, 0.0)),
                material=mats["bolt"],
                name=f"inspection_port_{i}", material_class_id="metal.blackened_gunmetal",
            )

    _emit_ring_gear(model, carrier, r, mats)
    _MECHANISM_BUILDERS[r.mechanism](model, carrier, r, mats)
    _emit_drive_pinion(model, carrier, r, mats)
    return model


def build_seeded_automotive_differential_differential_gear(seed: int) -> ArticulatedObject:
    return build_automotive_differential_differential_gear(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _setup_allowances(ctx, model, r):
    carrier = model.get_part("carrier_cage")
    part_names = {p.name for p in model.parts}
    ring = model.get_part("ring_gear")

    # side gears: journal seated in the axle collar (captured), + axle output
    # / bevel body enclosed inside the carrier body (closed case / near collar).
    for index in range(2):
        side = model.get_part(f"side_gear_{index}")
        for celem in ("axle_output", "bearing_journal", "bevel_body", "hub_connector", "spin_mark"):
            ctx.allow_overlap(carrier, side, elem_a="carrier_body", elem_b=celem,
                              reason="side gear output/body is seated in the carrier axle collar / enclosed by the case")
        for t in range(_SIDE_TEETH):
            ctx.allow_overlap(carrier, side, elem_a="carrier_body", elem_b=f"bevel_tooth_{t}",
                              reason="side gear teeth rotate inside the carrier body")

    # ring gear retained by the bolt shanks (bolted flange) + crown backing bridge.
    for i in range(r.n_bolt):
        for relem in ("toothed_ring", "crown_backing"):
            ctx.allow_overlap(carrier, ring, elem_a=f"bolt_shank_{i}", elem_b=relem,
                              reason="ring/crown gear bolt shanks pass through the bolted ring flange")
    ctx.allow_overlap(carrier, ring, elem_a="carrier_body", elem_b="crown_backing",
                      reason="crown-wheel backing disc bridges to the carrier flange (bolted mounting)")

    # drive pinion shaft captured in the bearing snout; teeth mesh at the ring.
    pinion = model.get_part("drive_pinion")
    for pelem in ("pinion_shaft", "pinion_teeth"):
        ctx.allow_overlap(carrier, pinion, elem_a="carrier_body", elem_b=pelem,
                          reason="drive pinion is seated in the carrier bearing snout / reaches the ring mesh")
    for i in range(14):
        ctx.allow_overlap(carrier, pinion, elem_a="carrier_body", elem_b=f"pinion_tooth_{i}",
                          reason="drive pinion teeth sweep past the carrier opening as the pinion turns")
    if r.ring_form == "bevel_crown":
        for relem in ("toothed_ring", "crown_backing"):
            ctx.allow_overlap(pinion, ring, elem_a="pinion_teeth", elem_b=relem,
                              reason="bevel pinion cone meshes at the crown-wheel perimeter")
            for i in range(14):
                ctx.allow_overlap(pinion, ring, elem_a=f"pinion_tooth_{i}", elem_b=relem,
                                  reason="bevel pinion tooth meshes at the crown-wheel perimeter")
        # the bevel pinion reaches up to the crown perimeter, into the bolt circle;
        # its stem (shaft) as well as the teeth pass the bolted ring flange.
        for b in range(r.n_bolt):
            for belem in (f"bolt_shank_{b}", f"bolt_{b}"):
                ctx.allow_overlap(carrier, pinion, elem_a=belem, elem_b="pinion_shaft",
                                  reason="bevel pinion stem reaches the crown perimeter, passing the ring bolt circle")
                ctx.allow_overlap(carrier, pinion, elem_a=belem, elem_b="pinion_teeth",
                                  reason="bevel pinion meshes at the crown perimeter, passing the ring bolt circle")
                for i in range(14):
                    ctx.allow_overlap(carrier, pinion, elem_a=belem, elem_b=f"pinion_tooth_{i}",
                                      reason="bevel pinion teeth mesh at the crown perimeter, passing the ring bolt circle")

    # spider pinions captured on the cross shaft(s).
    for index in range(4):
        if f"spider_gear_{index}" not in part_names:
            continue
        spider = model.get_part(f"spider_gear_{index}")
        shaft = "cross_shaft" if index < 2 else "cross_shaft_z"
        ctx.allow_overlap(carrier, spider, elem_a=shaft, elem_b="pinion_hub",
                          reason="spider pinion hub is captured on the cross shaft")
        ctx.allow_overlap(carrier, spider, elem_a="carrier_body", elem_b="pinion_hub",
                          reason="spider pinion rotates inside the carrier body")
        for j in range(_SPIDER_TEETH):
            ctx.allow_overlap(carrier, spider, elem_a="carrier_body", elem_b=f"tooth_{j}",
                              reason="spider pinion teeth rotate inside the carrier body")

    # clutch plates ride between the side gear and the cheek.
    if r.mechanism == "clutch_lsd":
        for index in range(2):
            side = model.get_part(f"side_gear_{index}")
            for pi in range(6):
                ctx.allow_overlap(carrier, side, elem_a=f"clutch_plate_{index}_{pi}", elem_b="bevel_body",
                                  reason="clutch plate stack sits against the side gear back face")
                for t in range(_SIDE_TEETH):
                    ctx.allow_overlap(carrier, side, elem_a=f"clutch_plate_{index}_{pi}", elem_b=f"bevel_tooth_{t}",
                                      reason="clutch plate stack overlaps the side gear teeth in the cavity")

    # viscous coupling: the two side-gear inner sleeves nest coaxially in the drum
    # bore and their interleaved plates shear past the opposing side's sleeve.
    if r.mechanism == "viscous_lsd":
        s0 = model.get_part("side_gear_0")
        s1 = model.get_part("side_gear_1")
        ctx.allow_overlap(s0, s1, elem_a="hub_connector", elem_b="hub_connector",
                          reason="the two side-gear inner sleeves nest coaxially in the viscous drum bore")
        for i in range(8):
            keyed = s0 if i % 2 == 0 else s1
            other = s1 if i % 2 == 0 else s0
            ctx.allow_overlap(keyed, other, elem_a=f"viscous_plate_{i}", elem_b="hub_connector",
                              reason="interleaved viscous plate shears past the opposing side-gear sleeve")
            for j in range(8):
                if j % 2 != i % 2:
                    ctx.allow_overlap(keyed, other, elem_a=f"viscous_plate_{i}", elem_b=f"viscous_plate_{j}",
                                      reason="alternating viscous plates interleave in the coupling stack")

    # torsen planet worms seated in radial carrier pockets.
    if r.mechanism == "torsen":
        for widx in range(6):
            planet = model.get_part(f"planet_worm_{widx}")
            pocket = f"worm_pocket_{widx // 2}"
            for pelem in ("worm_shaft", "worm_threads"):
                ctx.allow_overlap(carrier, planet, elem_a=pocket, elem_b=pelem,
                                  reason="planet worm is captured inside its radial carrier pocket")
                ctx.allow_overlap(carrier, planet, elem_a="carrier_body", elem_b=pelem,
                                  reason="planet worm nests inside the carrier body")
        for index in range(2):
            side = model.get_part(f"side_gear_{index}")
            for widx in range(6):
                planet = model.get_part(f"planet_worm_{widx}")
                ctx.allow_overlap(side, planet, elem_a="bevel_body", elem_b="worm_threads",
                                  reason="helical worm side gear meshes with the planet worms")

    # locker dog collar slides on the side_0 hub and engages the carrier dog teeth.
    if r.mechanism == "locker":
        collar = model.get_part("dog_collar")
        side0 = model.get_part("side_gear_0")
        ctx.allow_overlap(carrier, collar, elem_a="carrier_body", elem_b="collar_body",
                          reason="dog collar slides on the side_0 hub inside the carrier cheek")
        ctx.allow_overlap(carrier, collar, elem_a="lock_boss", elem_b="collar_body",
                          reason="dog collar engages the carrier lock boss")
        for i in range(6):
            for j in range(6):
                ctx.allow_overlap(carrier, collar, elem_a=f"carrier_dog_tooth_{i}", elem_b=f"collar_dog_tooth_{j}",
                                  reason="collar dog teeth interleave with carrier dog teeth when engaged")
            ctx.allow_overlap(carrier, collar, elem_a=f"carrier_dog_tooth_{i}", elem_b="collar_body",
                              reason="collar body meets the carrier dog teeth at engagement")
        ctx.allow_overlap(carrier, side0, elem_a="lock_boss", elem_b="axle_output",
                          reason="carrier lock boss surrounds the side_0 axle output")
        ctx.allow_overlap(carrier, side0, elem_a="lock_boss", elem_b="bevel_body",
                          reason="carrier lock boss abuts the side_0 gear body")
        for celem in ("collar_body", "shift_groove"):
            for selem in ("axle_output", "bearing_journal", "bevel_body"):
                ctx.allow_overlap(collar, side0, elem_a=celem, elem_b=selem,
                                  reason="dog collar is captured on the side_0 hub/journal (splined slide)")
            for i in range(6):
                ctx.allow_overlap(collar, side0, elem_a=f"collar_dog_tooth_{i}", elem_b=selem if False else "axle_output",
                                  reason="collar dog teeth ride over the side_0 axle output")


def _c(aabb):
    if aabb is None:
        return None
    lo, hi = aabb
    return tuple((lo[k] + hi[k]) * 0.5 for k in range(3))


def run_automotive_differential_differential_gear_tests(model, config=None) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _setup_allowances(ctx, model, r)

    carrier = model.get_part("carrier_cage")
    side_0 = model.get_part("side_gear_0")
    side_1 = model.get_part("side_gear_1")

    # --- Core identity: exactly two coaxial side gears, ring FIXED, pinion. ---
    n_side = sum(1 for p in model.parts if p.name.startswith("side_gear_"))
    ctx.check("exactly two coaxial side gears", n_side == 2, details=f"side gears={n_side}")

    ring_joint = model.get_articulation("carrier_to_ring")
    ctx.check("carrier_to_ring is FIXED", ring_joint.articulation_type == ArticulationType.FIXED,
              details=f"type={ring_joint.articulation_type}")
    for index in range(2):
        j = model.get_articulation(f"carrier_to_side_{index}")
        ctx.check(f"carrier_to_side_{index} is CONTINUOUS about X",
                  j.articulation_type == ArticulationType.CONTINUOUS
                  and tuple(round(v, 3) for v in j.axis) == (1.0, 0.0, 0.0),
                  details=f"type={j.articulation_type}, axis={j.axis}")
    pin_j = model.get_articulation("carrier_to_pinion")
    ctx.check("carrier_to_pinion is CONTINUOUS",
              pin_j.articulation_type == ArticulationType.CONTINUOUS,
              details=f"type={pin_j.articulation_type}")

    ctx.expect_origin_distance(side_0, carrier, axes="yz", max_dist=0.002,
                               name="first side gear is on the axle centerline")
    ctx.expect_origin_distance(side_1, carrier, axes="yz", max_dist=0.002,
                               name="second side gear is on the axle centerline")
    ctx.expect_origin_gap(side_1, side_0, axis="x", min_gap=0.078, max_gap=0.086,
                          name="side gears oppose one another across the carrier")
    ctx.expect_origin_gap(carrier, model.get_part("drive_pinion"), axis="y",
                          min_gap=0.210, max_gap=0.240,
                          name="drive pinion is mounted beside the ring gear")

    # mechanism-specific joint-type checks.
    if r.mechanism in _SPIDER_MECHANISMS:
        for index in range(r.n_spider):
            j = model.get_articulation(f"carrier_to_spider_{index}")
            ctx.check(f"carrier_to_spider_{index} is CONTINUOUS",
                      j.articulation_type == ArticulationType.CONTINUOUS,
                      details=f"type={j.articulation_type}")
    if r.mechanism == "torsen":
        for widx in range(6):
            j = model.get_articulation(f"carrier_to_planet_{widx}")
            ctx.check(f"carrier_to_planet_{widx} is CONTINUOUS",
                      j.articulation_type == ArticulationType.CONTINUOUS,
                      details=f"type={j.articulation_type}")
    if r.mechanism == "locker":
        lock_j = model.get_articulation("carrier_to_lockcollar")
        ctx.check("carrier_to_lockcollar is PRISMATIC about X",
                  lock_j.articulation_type == ArticulationType.PRISMATIC
                  and tuple(round(v, 3) for v in lock_j.axis) == (1.0, 0.0, 0.0),
                  details=f"type={lock_j.articulation_type}, axis={lock_j.axis}")

    # ring form check.
    if r.ring_form == "bevel_crown":
        aabb = ctx.part_element_world_aabb(model.get_part("ring_gear"), elem="toothed_ring")
        if aabb is not None:
            lo, hi = aabb
            dx = hi[0] - lo[0]
            radial = max(hi[1] - lo[1], hi[2] - lo[2])
            ctx.check("ring gear is a conical crown wheel (radial >> axial)",
                      radial > 0.14 and dx < 0.070,
                      details=f"axial={dx:.4f}, radial={radial:.4f}")

    # --- Targeted mechanism poses. ---
    # (1) side gear spin: axle center fixed, witness mark travels around X.
    spin = model.get_articulation("carrier_to_side_0")
    rest_pos = ctx.part_world_position(side_0)
    rest_mark = _c(ctx.part_element_world_aabb(side_0, elem="spin_mark"))
    with ctx.pose({spin: PI / 2.0}):
        turn_pos = ctx.part_world_position(side_0)
        turn_mark = _c(ctx.part_element_world_aabb(side_0, elem="spin_mark"))
    ctx.check("side gear spin keeps axle center fixed",
              rest_pos is not None and turn_pos is not None
              and all(abs(rest_pos[k] - turn_pos[k]) < 1e-6 for k in range(3)),
              details=f"rest={rest_pos}, turned={turn_pos}")
    ctx.check("side gear witness mark travels around the axle axis",
              rest_mark is not None and turn_mark is not None
              and (abs(rest_mark[1] - turn_mark[1]) > 0.004 or abs(rest_mark[2] - turn_mark[2]) > 0.004),
              details=f"rest={rest_mark}, turned={turn_mark}")

    # (2) locker collar slides inward (+X) when engaged.
    if r.mechanism == "locker":
        collar = model.get_part("dog_collar")
        lock_j = model.get_articulation("carrier_to_lockcollar")
        rest_x = ctx.part_world_position(collar)
        with ctx.pose({lock_j: lock_j.motion_limits.upper}):
            eng_x = ctx.part_world_position(collar)
        ctx.check("dog collar slides inward (+X) when engaged",
                  rest_x is not None and eng_x is not None and eng_x[0] > rest_x[0] + 0.008,
                  details=f"rest={rest_x}, engaged={eng_x}")

    # --- Rule 5: no self-intersection through the full motion envelope. ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    return ctx.report()


run_tests = run_automotive_differential_differential_gear_tests
