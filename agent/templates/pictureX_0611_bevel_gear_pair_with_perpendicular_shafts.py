# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — pictureX_0611_bevel_gear_pair_with_perpendicular_shafts.

Two conical (bevel) gears meshing at a 90-degree shaft angle, each mounted on its
own rotating shaft, the two rotations physically coupled by the gear mesh. A
grounded ``support_frame`` root carries two parallel-children drives:

    support_frame ──[CONTINUOUS axis X]──> horizontal_drive   (gear_meshes[0])
                  └─[CONTINUOUS axis Z]──> vertical_drive     (gear_meshes[1],
                                                               Mimic of horizontal)

The vertical joint is a Mimic of the horizontal at ``multiplier =
-gear_teeth/pinion_teeth`` in EVERY seed (the bevel mesh ratio). Both gears come
from ONE ``BevelGearPair(...).assemble()`` split by
``mesh_components_from_cadquery`` — never downgraded to boxes/cylinders.

Slots (all source-backed, see specs_modular_v1/<slug>.md):
  - tooth_form : straight | spiral | zerol | hypoid   (③ tooth face; hypoid = ① offset)
  - ratio      : miter | mild | high                  (① cone-pair size + mesh ratio)
  - teeth_grade: coarse | mid | fine                  (multiplicity N, module rescaled)
  - shaft_form : keyed | bare | hub_setscrew | flanged(① shaft-to-gear interface)
  - housing    : open_cage | bracketed | gearbox      (① support envelope)
  - hub_boss   : thin_spacer | extended_hub           (③ gear body construction)

5-star sources (adapted, joint semantics preserved): origin 001 (skeleton, two
CONTINUOUS joints + Mimic, BevelGearPair, open_cage, keyed, thin_spacer, straight,
mild, mid); var_spiral_bevel / var_zerol_bevel / var_hypoid_offset (tooth form);
var_miter_1to1 / var_reduction_high (ratio); var_teeth_coarse / var_teeth_fine
(teeth grade); var_shaft_bare / var_shaft_hub_setscrew / var_shaft_flanged (shaft);
var_housing_bracketed / var_housing_gearbox (housing); var_hub_boss (hub).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    BevelGearPair,
    Box,
    Cylinder,
    Mimic,
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    mesh_components_from_cadquery,
    mesh_from_cadquery,
)

__modular__ = True

PI = math.pi
MM = 0.001
SHAFT_CENTER_Z = 0.072  # world Z of the shaft-crossing line (parent L26)

# ---------------------------------------------------------------------------
# Discrete slot domains
# ---------------------------------------------------------------------------
TOOTH_FORMS = ("straight", "spiral", "zerol", "hypoid")
RATIOS = ("miter", "mild", "high")
TEETH_GRADES = ("coarse", "mid", "fine")
SHAFT_FORMS = ("keyed", "bare", "hub_setscrew", "flanged")
HOUSINGS = ("open_cage", "bracketed", "gearbox")
HUB_BOSSES = ("thin_spacer", "extended_hub")
PALETTE_STYLES = ("bright_steel", "blackened", "brass_gears", "cast_iron", "oiled_bronze")

# teeth_grade weighting (spec §8: small N high-frequency, large N tail).
TEETH_GRADE_WEIGHTS = (0.30, 0.45, 0.25)
N_FLANGE_BOLT_CHOICES = (4, 6, 8)
N_FLANGE_BOLT_WEIGHTS = (0.5, 0.3, 0.2)

# tooth_form -> helix angle (deg). hypoid keeps 0 helix + a lateral Y offset.
_HELIX = {"straight": 0.0, "spiral": 35.0, "zerol": 10.0, "hypoid": 0.0}
HYPOID_OFFSET = 0.010  # lateral Y offset between shaft axes (var_hypoid_offset L27)

# ratio -> nominal mesh multiplier magnitude.
_RATIO_MULT = {"miter": 1.0, "mild": 1.25, "high": 3.0}
# teeth_grade -> (pinion base, module mm). module holds pitch dia ~34mm (spec §8).
_PINION_BASE = {"coarse": 10, "mid": 16, "fine": 26}
_MODULE = {"coarse": 3.5, "mid": 2.1, "fine": 1.3}
# high reduction uses a SMALL pinion (var_reduction_high 33/11); per grade.
_PINION_HIGH = {"coarse": 8, "mid": 11, "fine": 14}

# Tessellation (compile budget §7.5): gear mesh is intrinsically heavy at build
# time, so keep tessellation coarse (cheap, and lighter FCL collision meshes).
_GEAR_TOL, _GEAR_ANG = 0.35, 0.20
_FRAME_TOL, _FRAME_ANG = 0.35, 0.12

# ---------------------------------------------------------------------------
# Palettes (⑥). role keys: frame / shaft / gear / bearing / accent
# ---------------------------------------------------------------------------
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "bright_steel": {
        "frame": (0.72, 0.74, 0.76, 1.0),
        "shaft": (0.73, 0.76, 0.79, 1.0),
        "gear": (0.19, 0.21, 0.22, 1.0),
        "bearing": (0.34, 0.36, 0.38, 1.0),
        "accent": (0.12, 0.13, 0.14, 1.0),
    },
    "blackened": {
        "frame": (0.22, 0.23, 0.24, 1.0),
        "shaft": (0.40, 0.41, 0.43, 1.0),
        "gear": (0.10, 0.10, 0.11, 1.0),
        "bearing": (0.26, 0.27, 0.28, 1.0),
        "accent": (0.05, 0.05, 0.06, 1.0),
    },
    "brass_gears": {
        "frame": (0.70, 0.72, 0.74, 1.0),
        "shaft": (0.74, 0.77, 0.80, 1.0),
        "gear": (0.71, 0.55, 0.24, 1.0),
        "bearing": (0.55, 0.45, 0.24, 1.0),
        "accent": (0.40, 0.30, 0.12, 1.0),
    },
    "cast_iron": {
        "frame": (0.40, 0.41, 0.42, 1.0),
        "shaft": (0.66, 0.68, 0.70, 1.0),
        "gear": (0.24, 0.25, 0.26, 1.0),
        "bearing": (0.32, 0.33, 0.34, 1.0),
        "accent": (0.14, 0.14, 0.15, 1.0),
    },
    "oiled_bronze": {
        "frame": (0.30, 0.28, 0.24, 1.0),
        "shaft": (0.60, 0.58, 0.52, 1.0),
        "gear": (0.44, 0.34, 0.20, 1.0),
        "bearing": (0.42, 0.34, 0.22, 1.0),
        "accent": (0.20, 0.16, 0.10, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PictureX0611BevelGearPairWithPerpendicularShaftsConfig:
    tooth_form: str | None = None
    ratio: str | None = None
    teeth_grade: str | None = None
    shaft_form: str | None = None
    housing: str | None = None
    hub_boss: str | None = None
    palette_style: str = "bright_steel"
    n_flange_bolt: int | None = None
    shaft_len_scale: float = 1.0
    gear_scale: float = 1.0
    name: str = "pictureX_0611_bevel_gear_pair_with_perpendicular_shafts"


@dataclass(frozen=True)
class ResolvedPictureX0611BevelGearPairWithPerpendicularShaftsConfig:
    tooth_form: str
    ratio: str
    teeth_grade: str
    shaft_form: str
    housing: str
    hub_boss: str
    palette_style: str
    n_flange_bolt: int
    # derived gearing
    gear_teeth: int
    pinion_teeth: int
    module: float
    helix_angle: float
    face_width: float
    hypoid_offset: float
    mimic_mult: float
    # derived dims
    shaft_len_scale: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> PictureX0611BevelGearPairWithPerpendicularShaftsConfig:
    rng = random.Random(seed)
    return PictureX0611BevelGearPairWithPerpendicularShaftsConfig(
        tooth_form=rng.choice(TOOTH_FORMS),
        ratio=rng.choice(RATIOS),
        teeth_grade=rng.choices(TEETH_GRADES, weights=TEETH_GRADE_WEIGHTS, k=1)[0],
        shaft_form=rng.choice(SHAFT_FORMS),
        housing=rng.choice(HOUSINGS),
        hub_boss=rng.choice(HUB_BOSSES),
        palette_style=rng.choice(PALETTE_STYLES),
        n_flange_bolt=rng.choices(N_FLANGE_BOLT_CHOICES, weights=N_FLANGE_BOLT_WEIGHTS, k=1)[0],
        shaft_len_scale=round(rng.uniform(0.90, 1.12), 4),
        gear_scale=round(rng.uniform(0.92, 1.08), 4),
        name=f"seeded_pictureX_0611_bevel_gear_pair_with_perpendicular_shafts_{seed}",
    )


def resolve_config(
    config: PictureX0611BevelGearPairWithPerpendicularShaftsConfig | None = None,
) -> ResolvedPictureX0611BevelGearPairWithPerpendicularShaftsConfig:
    cfg = config or PictureX0611BevelGearPairWithPerpendicularShaftsConfig()

    tooth_form = _pick(cfg.tooth_form, TOOTH_FORMS)
    ratio = _pick(cfg.ratio, RATIOS)
    teeth_grade = _pick(cfg.teeth_grade, TEETH_GRADES)
    shaft_form = _pick(cfg.shaft_form, SHAFT_FORMS)
    housing = _pick(cfg.housing, HOUSINGS)
    hub_boss = _pick(cfg.hub_boss, HUB_BOSSES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    n_flange_bolt = int(cfg.n_flange_bolt) if cfg.n_flange_bolt is not None else 4
    n_flange_bolt = n_flange_bolt if n_flange_bolt in N_FLANGE_BOLT_CHOICES else 4

    # --- teeth / module derivation (equation, spec §7) --------------------
    module = _MODULE[teeth_grade] * _clamp(cfg.gear_scale, 0.92, 1.08)
    if ratio == "high":
        pinion_teeth = _PINION_HIGH[teeth_grade]
        gear_teeth = int(round(pinion_teeth * _RATIO_MULT["high"]))
    elif ratio == "miter":
        pinion_teeth = _PINION_BASE[teeth_grade]
        gear_teeth = pinion_teeth  # equal cones, 1:1
    else:  # mild
        pinion_teeth = _PINION_BASE[teeth_grade]
        gear_teeth = int(round(pinion_teeth * _RATIO_MULT["mild"]))
    gear_teeth = max(gear_teeth, pinion_teeth)  # gear >= pinion (reduction/miter)

    mimic_mult = -float(gear_teeth) / float(pinion_teeth)
    helix_angle = _HELIX[tooth_form]
    hypoid_offset = HYPOID_OFFSET if tooth_form == "hypoid" else 0.0

    # --- face_width safety band (inequality): BevelGear asserts gs_r > fw,
    # gs_r == module/2 * sqrt(g^2 + p^2) at axis_angle=90 for both gears. ------
    gs_r = module / 2.0 * math.sqrt(gear_teeth**2 + pinion_teeth**2)
    face_width = min(10.0, 0.32 * gs_r)

    return ResolvedPictureX0611BevelGearPairWithPerpendicularShaftsConfig(
        tooth_form=tooth_form,
        ratio=ratio,
        teeth_grade=teeth_grade,
        shaft_form=shaft_form,
        housing=housing,
        hub_boss=hub_boss,
        palette_style=palette_style,
        n_flange_bolt=n_flange_bolt,
        gear_teeth=gear_teeth,
        pinion_teeth=pinion_teeth,
        module=module,
        helix_angle=helix_angle,
        face_width=face_width,
        hypoid_offset=hypoid_offset,
        mimic_mult=mimic_mult,
        shaft_len_scale=_clamp(cfg.shaft_len_scale, 0.90, 1.12),
        name=cfg.name or "pictureX_0611_bevel_gear_pair_with_perpendicular_shafts",
    )


def with_overrides(config, **kwargs):
    return replace(config, **kwargs)


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedPictureX0611BevelGearPairWithPerpendicularShaftsConfig)
        else resolve_config(config)
    )
    return (
        ("tooth_form", r.tooth_form),
        ("ratio", r.ratio),
        ("teeth_grade", r.teeth_grade),
        ("shaft_form", r.shaft_form),
        ("housing", r.housing),
        ("hub_boss", r.hub_boss),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Housing (Slot E) cadquery frame builders. Each returns a machined frame body
# with horizontal + vertical shaft bores at the parent positions; the bearing
# races are added separately as visuals so all housings share the bore geometry.
# ---------------------------------------------------------------------------
def _bores(shape):
    horizontal_bore = cq.Workplane("YZ", origin=(-76.0, 0.0, 72.0)).circle(6.2).extrude(152.0)
    vertical_bore = cq.Workplane("XY", origin=(0.0, 0.0, 100.0)).circle(6.2).extrude(60.0)
    return shape.cut(horizontal_bore).cut(vertical_bore)


def _bearing_bosses(shape):
    side_boss_0 = cq.Workplane("YZ", origin=(-60.0, 0.0, 72.0)).circle(18.0).extrude(-12.0)
    side_boss_1 = cq.Workplane("YZ", origin=(60.0, 0.0, 72.0)).circle(18.0).extrude(12.0)
    top_boss = cq.Workplane("XY", origin=(0.0, 0.0, 140.0)).circle(22.0).extrude(14.0)
    return shape.union(side_boss_0).union(side_boss_1).union(top_boss)


def _open_cage_frame() -> cq.Shape:
    """Machined windowed box + integral bearing bosses (origin 001, L29-76)."""
    outer = cq.Workplane("XY").box(120.0, 30.0, 132.0, centered=(True, True, False))
    window = (
        cq.Workplane("XY")
        .box(82.0, 46.0, 86.0, centered=(True, True, True))
        .translate((0.0, 0.0, 66.0))
    )
    frame = outer.cut(window).edges("|Y").fillet(7.0)
    top_bridge = (
        cq.Workplane("XY")
        .box(100.0, 42.0, 8.0, centered=(True, True, False))
        .translate((0.0, 0.0, 132.0))
        .edges("|Z")
        .fillet(2.0)
    )
    frame = _bearing_bosses(frame.union(top_bridge))
    return _bores(frame)


def _bracketed_frame() -> cq.Shape:
    """Open pillow-block stand: base plate + two upright brackets carrying the
    horizontal bearing bosses, and a top cross-arm carrying the vertical boss
    (var_housing_bracketed — rebuilt _make_support_frame, more open than cage)."""
    base = (
        cq.Workplane("XY")
        .box(150.0, 60.0, 12.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(6.0)
    )
    # two tall pillow-block uprights at x=+-60 carrying the side bearing bosses
    # (z=72) and rising to the top cross-arm; base -> uprights -> arm is one solid.
    upright_l = (
        cq.Workplane("XY")
        .box(20.0, 30.0, 128.0, centered=(True, True, False))
        .translate((-60.0, 0.0, 12.0))
    )
    upright_r = (
        cq.Workplane("XY")
        .box(20.0, 30.0, 128.0, centered=(True, True, False))
        .translate((60.0, 0.0, 12.0))
    )
    # top cross-arm bridging the two uprights (x=-60..60), holds the top boss.
    top_arm = (
        cq.Workplane("XY")
        .box(140.0, 34.0, 12.0, centered=(True, True, False))
        .translate((0.0, 0.0, 128.0))
    )
    frame = base.union(upright_l).union(upright_r).union(top_arm)
    frame = _bearing_bosses(frame)
    return _bores(frame)


def _gearbox_frame() -> cq.Shape:
    """Closed gearbox housing: solid walls + internal cavity + cast ribs +
    cover-bolt heads + bottom mounting flange (var_housing_gearbox L30-125)."""
    outer = (
        cq.Workplane("XY")
        .box(120.0, 70.0, 132.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(4.0)
    )
    cavity = (
        cq.Workplane("XY")
        .box(82.0, 48.0, 86.0, centered=(True, True, True))
        .translate((0.0, 0.0, 66.0))
    )
    housing = outer.cut(cavity)
    top_bridge = (
        cq.Workplane("XY")
        .box(100.0, 42.0, 8.0, centered=(True, True, False))
        .translate((0.0, 0.0, 132.0))
    )
    housing = _bearing_bosses(housing.union(top_bridge))
    housing = _bores(housing)
    # cast reinforcing ribs on front/back faces.
    for y_sign in (-1.0, 1.0):
        ribs = (
            cq.Workplane("XY", origin=(0.0, y_sign * 36.0, 16.0))
            .pushPoints([(-35.0, 0.0), (0.0, 0.0), (35.0, 0.0)])
            .rect(4.0, 4.0)
            .extrude(100.0)
        )
        housing = housing.union(ribs)
    # cover-plate bolt heads on the top face perimeter.
    bolts = (
        cq.Workplane("XY", origin=(0.0, 0.0, 132.0))
        .pushPoints(
            [
                (-45.0, -25.0),
                (-45.0, 25.0),
                (-20.0, -25.0),
                (-20.0, 25.0),
                (20.0, -25.0),
                (20.0, 25.0),
                (45.0, -25.0),
                (45.0, 25.0),
            ]
        )
        .circle(4.0)
        .extrude(2.5)
    )
    housing = housing.union(bolts)
    # bottom mounting flange with through-holes.
    flange = (
        cq.Workplane("XY")
        .box(140.0, 90.0, 5.0, centered=(True, True, False))
        .edges("|Z")
        .fillet(3.0)
    )
    housing = housing.union(flange)
    mount = (
        cq.Workplane("XY", origin=(0.0, 0.0, -1.0))
        .pushPoints([(-64.0, -38.0), (-64.0, 38.0), (64.0, -38.0), (64.0, 38.0)])
        .circle(5.0)
        .extrude(8.0)
    )
    return housing.cut(mount)


_FRAME_BUILDERS = {
    "open_cage": _open_cage_frame,
    "bracketed": _bracketed_frame,
    "gearbox": _gearbox_frame,
}


def _annulus(axis: str, outer_r: float, inner_r: float, length: float) -> cq.Shape:
    plane = {"x": "YZ", "z": "XY"}[axis]
    return cq.Workplane(plane).circle(outer_r).circle(inner_r).extrude(length)


def _flange_disc(n_bolts: int) -> cq.Shape:
    """Flanged coupling disc: disc + locating hub spigot + bolt-circle holes
    (var_shaft_flanged _make_flange_disc L89-127; n_bolts is a copy loop)."""
    disc = cq.Workplane("XY").circle(18.0).extrude(7.0).translate((0.0, 0.0, -3.5))
    hub = cq.Workplane("XY").circle(8.0).extrude(3.0).translate((0.0, 0.0, 3.5))
    disc = disc.union(hub)
    for i in range(n_bolts):
        a = 2.0 * PI * i / n_bolts
        hole = (
            cq.Workplane("XY")
            .center(13.0 * math.cos(a), 13.0 * math.sin(a))
            .circle(2.8)
            .extrude(7.0)
            .translate((0.0, 0.0, -3.5))
        )
        disc = disc.cut(hole)
    return disc


# ---------------------------------------------------------------------------
# Drive (horizontal / vertical) builder — shared helper
# ---------------------------------------------------------------------------
def _build_drive(part, mats, r, gear_mesh, *, which, gear_x):
    """Build one drive part in its local frame (origin = shaft-crossing point).

    ``which`` in {"horizontal","vertical"}; the shaft runs along the drive axis
    and the gear (from the shared BevelGearPair assembly) meshes at the apex.
    Both gears carry the SAME (gear_x, rpy=(0,pi/2,0)) transform so the meshed
    pair stays engaged (parent L172-180 / L204-212)."""
    horizontal = which == "horizontal"
    shaft_len = (0.205 if horizontal else 0.122) * r.shaft_len_scale
    gear_rpy = (0.0, PI / 2.0, 0.0)

    if horizontal:
        # shaft centered on the crossing, along X.
        part.visual(
            Cylinder(radius=0.005, length=shaft_len),
            origin=Origin(rpy=gear_rpy),
            material=mats["shaft"],
            name="horizontal_shaft", material_class_id="metal.steel_bare",
        )
    else:
        # shaft runs +Z from the crossing up to the top bearing.
        part.visual(
            Cylinder(radius=0.005, length=shaft_len),
            origin=Origin(xyz=(0.0, 0.0, shaft_len / 2.0)),
            material=mats["shaft"],
            name="vertical_shaft", material_class_id="metal.steel_bare",
        )

    part.visual(
        gear_mesh,
        origin=Origin(xyz=(gear_x, 0.0, 0.0), rpy=gear_rpy),
        material=mats["gear"],
        name=f"{which}_bevel_gear", material_class_id="metal.blackened_gunmetal",
    )

    # hub / spacer on the shaft behind the gear (Slot F). It rides on the shaft
    # along the drive axis: -X for the horizontal drive, +Z for the vertical
    # drive (parent horizontal_spacer L181-189 / vertical_spacer L213-218).
    hub_r = 0.009 if horizontal else 0.010
    if r.hub_boss == "extended_hub":
        hub_r += 0.006
        hub_len = 0.024
    else:
        hub_len = 0.010
    if horizontal:
        # just outboard of the gear back face, wrapping the shaft.
        hub_pos = gear_x - (r.face_width * MM * 0.5 + hub_len * 0.5 + 0.001)
        part.visual(
            Cylinder(radius=hub_r, length=hub_len),
            origin=Origin(xyz=(hub_pos, 0.0, 0.0), rpy=gear_rpy),
            material=mats["shaft"],
            name="horizontal_hub", material_class_id="metal.steel_bare",
        )
    else:
        # on the vertical shaft, just above the crossing (parent z=0.031).
        hub_pos = 0.020 + hub_len * 0.5
        part.visual(
            Cylinder(radius=hub_r, length=hub_len),
            origin=Origin(xyz=(0.0, 0.0, hub_pos)),
            material=mats["shaft"],
            name="vertical_hub", material_class_id="metal.steel_bare",
        )

    # shaft-end interface (Slot D). Placed outboard on the shaft.
    _emit_shaft_feature(part, mats, r, which=which, hub_x=gear_x)


def _emit_shaft_feature(part, mats, r, *, which, hub_x):
    horizontal = which == "horizontal"
    gear_rpy = (0.0, PI / 2.0, 0.0)
    # a small radial position on the shaft surface (shaft radius 0.005).
    if r.shaft_form == "keyed":
        # rectangular key sitting on the shaft (parent L190-195 / L219-224).
        if horizontal:
            part.visual(
                Box((0.015, 0.004, 0.003)),
                origin=Origin(xyz=(hub_x - 0.006, 0.0, 0.0055)),
                material=mats["accent"],
                name="horizontal_key", material_class_id="metal.blackened_gunmetal",
            )
        else:
            part.visual(
                Box((0.003, 0.004, 0.016)),
                origin=Origin(xyz=(0.0055, 0.0, 0.030)),
                material=mats["accent"],
                name="vertical_key", material_class_id="metal.blackened_gunmetal",
            )
    elif r.shaft_form == "bare":
        return  # plain shaft (var_shaft_bare)
    elif r.shaft_form == "hub_setscrew":
        # hub collar + radial setscrew boss + hex socket mark
        # (var_shaft_hub_setscrew L190-208).
        cx = hub_x - 0.004
        cz = 0.030
        if horizontal:
            part.visual(
                Cylinder(radius=0.0058, length=0.012),
                origin=Origin(xyz=(cx, 0.0, 0.0), rpy=gear_rpy),
                material=mats["shaft"],
                name="horizontal_hub_collar", material_class_id="metal.steel_bare",
            )
            part.visual(
                Cylinder(radius=0.0025, length=0.007),
                origin=Origin(xyz=(cx, 0.0093, 0.0), rpy=(PI / 2.0, 0.0, 0.0)),
                material=mats["shaft"],
                name="horizontal_setscrew_boss", material_class_id="metal.steel_bare",
            )
            part.visual(
                Cylinder(radius=0.0015, length=0.002),
                origin=Origin(xyz=(cx, 0.0138, 0.0), rpy=(PI / 2.0, 0.0, 0.0)),
                material=mats["accent"],
                name="horizontal_hex_socket", material_class_id="metal.blackened_gunmetal",
            )
        else:
            part.visual(
                Cylinder(radius=0.0058, length=0.012),
                origin=Origin(xyz=(0.0, 0.0, cz)),
                material=mats["shaft"],
                name="vertical_hub_collar", material_class_id="metal.steel_bare",
            )
            part.visual(
                Cylinder(radius=0.0025, length=0.007),
                origin=Origin(xyz=(0.0093, 0.0, cz), rpy=gear_rpy),
                material=mats["shaft"],
                name="vertical_setscrew_boss", material_class_id="metal.steel_bare",
            )
            part.visual(
                Cylinder(radius=0.0015, length=0.002),
                origin=Origin(xyz=(0.0138, 0.0, cz), rpy=gear_rpy),
                material=mats["accent"],
                name="vertical_hex_socket", material_class_id="metal.blackened_gunmetal",
            )
    elif r.shaft_form == "flanged":
        # flange disc at the outboard shaft end (var_shaft_flanged L228-237/263-272).
        disc = mesh_from_cadquery(
            _flange_disc(r.n_flange_bolt),
            f"{which}_flange",
            unit_scale=MM,
            tolerance=0.25,
            angular_tolerance=0.12,
        )
        if horizontal:
            part.visual(
                disc,
                origin=Origin(xyz=(-0.100 * r.shaft_len_scale, 0.0, 0.0), rpy=gear_rpy),
                material=mats["shaft"],
                name="horizontal_flange", material_class_id="metal.steel_bare",
            )
        else:
            part.visual(
                disc,
                origin=Origin(xyz=(0.0, 0.0, 0.116 * r.shaft_len_scale)),
                material=mats["shaft"],
                name="vertical_flange", material_class_id="metal.steel_bare",
            )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_pictureX_0611_bevel_gear_pair_with_perpendicular_shafts(config=None, *, assets=None):
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        meta={"template": "pictureX_0611_bevel_gear_pair_with_perpendicular_shafts"},
    )
    mats = {
        k: model.material(f"{r.palette_style}_{k}", rgba=v)
        for k, v in PALETTES[r.palette_style].items()
    }

    # --- root support frame (Slot E) ---
    support = model.part("support_frame")
    support.visual(
        mesh_from_cadquery(
            _FRAME_BUILDERS[r.housing](),
            "support_frame_body",
            assets=assets,
            unit_scale=MM,
            tolerance=_FRAME_TOL,
            angular_tolerance=_FRAME_ANG,
        ),
        material=mats["frame"],
        name="frame_body", material_class_id=("metal.steel_bare" if config.palette_style in {"bright_steel", "brass_gears", "cast_iron", "oiled_bronze"} else "metal.blackened_gunmetal"),
    )
    # pressed bearing races (inner-race == shaft dia; explicit support path).
    side_race = _annulus("x", outer_r=13.5, inner_r=5.0, length=4.0)
    support.visual(
        mesh_from_cadquery(side_race, "side_bearing_0", unit_scale=MM),
        origin=Origin(xyz=(-0.072, 0.0, SHAFT_CENTER_Z)),
        material=mats["bearing"],
        name="side_bearing_0", material_class_id=("metal.chrome_polished" if config.palette_style in {"bright_steel", "brass_gears", "cast_iron", "oiled_bronze"} else "metal.blackened_gunmetal"),
    )
    support.visual(
        mesh_from_cadquery(side_race, "side_bearing_1", unit_scale=MM),
        origin=Origin(xyz=(0.068, 0.0, SHAFT_CENTER_Z)),
        material=mats["bearing"],
        name="side_bearing_1", material_class_id=("metal.chrome_polished" if config.palette_style in {"bright_steel", "brass_gears", "cast_iron", "oiled_bronze"} else "metal.blackened_gunmetal"),
    )
    top_race = _annulus("z", outer_r=16.0, inner_r=5.0, length=4.0)
    support.visual(
        mesh_from_cadquery(top_race, "top_bearing", unit_scale=MM),
        origin=Origin(xyz=(0.0, r.hypoid_offset, 0.151)),
        material=mats["bearing"],
        name="top_bearing", material_class_id=("metal.chrome_polished" if config.palette_style in {"bright_steel", "brass_gears", "cast_iron", "oiled_bronze"} else "metal.blackened_gunmetal"),
    )

    # --- ONE bevel gear pair; split into gear (horizontal) + pinion (vertical) ---
    bevel_pair = BevelGearPair(
        module=r.module,
        gear_teeth=r.gear_teeth,
        pinion_teeth=r.pinion_teeth,
        face_width=r.face_width,
        axis_angle=90.0,
        pressure_angle=20.0,
        helix_angle=r.helix_angle,
        backlash=0.15,
    )
    pair_assembly = bevel_pair.assemble(
        gear_build_args={"bore_d": 10.0},
        pinion_build_args={"bore_d": 10.0},
    )
    gear_meshes = mesh_components_from_cadquery(
        pair_assembly,
        "meshing_bevel_gears",
        unit_scale=MM,
        tolerance=_GEAR_TOL,
        angular_tolerance=_GEAR_ANG,
    )
    gear_x = -bevel_pair.gear.cone_h * MM  # apex offset (== parent -0.0187605 for m2.1)

    horizontal = model.part("horizontal_drive")
    _build_drive(horizontal, mats, r, gear_meshes[0], which="horizontal", gear_x=gear_x)
    vertical = model.part("vertical_drive")
    _build_drive(vertical, mats, r, gear_meshes[1], which="vertical", gear_x=gear_x)

    # --- two CONTINUOUS shaft joints, vertical Mimic of horizontal ---
    # shaft-in-bearing is a captured pin (radial containment, not two axis-aligned
    # faces) -> MatingContract omitted / grandfathered (AUTHORING Rule 2). Origin
    # sits on the bearing symmetry centerline (fail_if_articulation_origin passes).
    horizontal_joint = model.articulation(
        "support_to_horizontal",
        ArticulationType.CONTINUOUS,
        parent=support,
        child=horizontal,
        origin=Origin(xyz=(0.0, 0.0, SHAFT_CENTER_Z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=8.0),
        motion_properties=MotionProperties(damping=0.02, friction=0.01),
    )
    model.articulation(
        "support_to_vertical",
        ArticulationType.CONTINUOUS,
        parent=support,
        child=vertical,
        origin=Origin(xyz=(0.0, r.hypoid_offset, SHAFT_CENTER_Z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=10.0),
        motion_properties=MotionProperties(damping=0.02, friction=0.01),
        mimic=Mimic(joint=horizontal_joint.name, multiplier=r.mimic_mult),
    )
    return model


def build_seeded_pictureX_0611_bevel_gear_pair_with_perpendicular_shafts(
    seed: int,
) -> ArticulatedObject:
    return build_pictureX_0611_bevel_gear_pair_with_perpendicular_shafts(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _drive_elems(part):
    return [v.name for v in part.visuals]


def _setup_allowances(ctx, model, r):
    support = model.get_part("support_frame")
    horizontal = model.get_part("horizontal_drive")
    vertical = model.get_part("vertical_drive")
    h_elems = _drive_elems(horizontal)
    v_elems = _drive_elems(vertical)

    # (1) bevel gears mesh at the pitch cones — intentional interpenetration, and
    # the two shafts cross at the apex. Allow every h-elem vs v-elem overlap near
    # the crossing (the whole point of a 90-degree bevel pair).
    for he in h_elems:
        for ve in v_elems:
            ctx.allow_overlap(
                horizontal,
                vertical,
                elem_a=he,
                elem_b=ve,
                reason="bevel pitch cones mesh and the perpendicular shafts cross at the apex",
            )

    # (2) each drive is captured in its bearings / rotates inside the frame
    # (shaft-in-bore captured pin; gearbox encloses the gears).
    for he in h_elems:
        for se in ("frame_body", "side_bearing_0", "side_bearing_1"):
            ctx.allow_overlap(
                support,
                horizontal,
                elem_a=se,
                elem_b=he,
                reason="horizontal drive is captured in the side bearings / rotates inside the frame",
            )
    for ve in v_elems:
        for se in ("frame_body", "top_bearing"):
            ctx.allow_overlap(
                support,
                vertical,
                elem_a=se,
                elem_b=ve,
                reason="vertical drive is captured in the top bearing / rotates inside the frame",
            )


def run_pictureX_0611_bevel_gear_pair_with_perpendicular_shafts_tests(
    model, config=None
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    _setup_allowances(ctx, model, r)

    support = model.get_part("support_frame")
    horizontal = model.get_part("horizontal_drive")
    vertical = model.get_part("vertical_drive")
    hj = model.get_articulation("support_to_horizontal")
    vj = model.get_articulation("support_to_vertical")

    # --- core identity ---
    ctx.check(
        "core three-part inventory",
        {p.name for p in model.parts} == {"support_frame", "horizontal_drive", "vertical_drive"},
        details=f"parts={[p.name for p in model.parts]}",
    )
    ctx.check(
        "single grounded support root",
        [p.name for p in model.root_parts()] == ["support_frame"],
        details=f"roots={[p.name for p in model.root_parts()]}",
    )
    ctx.check(
        "two CONTINUOUS shaft rotation joints",
        len(model.articulations) == 2
        and hj.articulation_type == ArticulationType.CONTINUOUS
        and vj.articulation_type == ArticulationType.CONTINUOUS,
        details=f"joints={[(j.name, j.articulation_type) for j in model.articulations]}",
    )
    ctx.check(
        "perpendicular shaft axes (X and Z)",
        tuple(round(v, 6) for v in hj.axis) == (1.0, 0.0, 0.0)
        and tuple(round(v, 6) for v in vj.axis) == (0.0, 0.0, 1.0),
        details=f"horizontal={hj.axis}, vertical={vj.axis}",
    )
    ctx.check(
        "bevel mesh coupling: vertical mimics horizontal at -gear/pinion",
        vj.mimic is not None
        and vj.mimic.joint == hj.name
        and abs(vj.mimic.multiplier - (-float(r.gear_teeth) / float(r.pinion_teeth))) < 1e-9,
        details=f"mimic={vj.mimic}, gear/pinion={r.gear_teeth}/{r.pinion_teeth}",
    )
    ctx.check(
        "both bevel gear meshes present (not downgraded)",
        horizontal.get_visual("horizontal_bevel_gear") is not None
        and vertical.get_visual("vertical_bevel_gear") is not None,
        details="each drive must carry a BevelGearPair mesh component",
    )
    ctx.check(
        "every visible component carries a metal material",
        all(vis.material is not None for p in model.parts for vis in p.visuals),
        details="metal finish on all visuals",
    )
    if r.ratio == "miter":
        ctx.check(
            "miter ratio has equal teeth and unit coupling",
            r.gear_teeth == r.pinion_teeth and abs(r.mimic_mult + 1.0) < 1e-9,
            details=f"g/p={r.gear_teeth}/{r.pinion_teeth}, mult={r.mimic_mult}",
        )

    # --- mesh geometry: the two gear cones share the meshing envelope ---
    ctx.expect_overlap(
        horizontal,
        vertical,
        axes="xyz",
        elem_a="horizontal_bevel_gear",
        elem_b="vertical_bevel_gear",
        min_overlap=0.002,
        name="pitch cones occupy the common meshing envelope",
    )

    # --- shaft centered in its bearings (radial containment) ---
    ctx.expect_within(
        horizontal,
        support,
        axes="yz",
        inner_elem="horizontal_shaft",
        outer_elem="side_bearing_0",
        margin=0.0,
        name="horizontal shaft centered in first bearing",
    )
    if r.hypoid_offset == 0.0:
        ctx.expect_within(
            vertical,
            support,
            axes="xy",
            inner_elem="vertical_shaft",
            outer_elem="top_bearing",
            margin=0.0,
            name="vertical shaft centered in top bearing",
        )
    else:
        # hypoid: the vertical axis is laterally offset from the horizontal axis.
        ctx.check(
            "hypoid Y offset between shaft axes",
            abs(vj.origin.xyz[1] - hj.origin.xyz[1] - r.hypoid_offset) < 1e-6,
            details=f"vertical_origin={vj.origin.xyz}, horizontal_origin={hj.origin.xyz}",
        )

    # --- targeted motion semantics: gears stay meshed through rotation ---
    with ctx.pose({hj: 0.6}):
        ctx.expect_overlap(
            horizontal,
            vertical,
            axes="xyz",
            elem_a="horizontal_bevel_gear",
            elem_b="vertical_bevel_gear",
            min_overlap=0.001,
            name="coupled bevel teeth remain engaged after rotation",
        )

    # --- Rule 5: no unintended self-intersection through the motion envelope ---
    # (only the horizontal joint is free; vertical is a Mimic and not sampled.)
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)
    return ctx.report()


run_tests = run_pictureX_0611_bevel_gear_pair_with_perpendicular_shafts_tests
