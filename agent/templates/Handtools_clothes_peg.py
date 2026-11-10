# SPDX-License-Identifier: Apache-2.0

"""Wooden spring clothes peg (spring clothespin) modular template.

NOTE on the slug name: "clothes_peg" here = a **wooden spring clothespin /
clothes peg** (~72 mm long, ~8.5 mm wide, ~13 mm tall at the pivot), NOT a
binder clip / stationery spring clip (that is the separate ``clip`` slug), NOT a
screw clamp (``clamp``), and NOT pliers (``pliers``). The structure family is a
spring peg: two mirror-image wooden legs -- ``lower_half`` (root, lies flat on
the ground) + ``upper_half`` (moving) -- pivot against each other about a single
REVOLUTE ``pivot`` (the spring-barrel / fulcrum axis), biased by a spring part
(torsion coil OR leaf strip) that is rigidly FIXED to the root via
``lower_to_spring``. The spring keeps the front jaws pressed closed at rest
(q=0); squeezing the back tails opens the jaws.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Handtools_clothes_peg.md`` and the
``picture/Handtools/clothes peg`` 5-star sample pool (1 parent + 5 slot-fork
variants), all synced under ``data/records/``.

Coordinate convention (unified across all 6 samples, used verbatim here): the
peg LIES FLAT on its side. The peg-frame long axis = world X; the two legs sit
side by side along world Y (lower_half at +Y, upper_half at -Y); the peg width
spans world Z from 0 (ground) to HALF_W. The ``pivot`` REVOLUTE has
origin=(PIVOT_X, 0, HALF_W/2), rpy=(pi/2,0,0), axis=(0,-1,0) (joint-frame -Y =
world vertical): positive q opens the front jaws while the back tails squeeze
together; q=0 is the closed rest pose. ``lower_to_spring`` FIXED origin=(0,0,0).

Structure (pattern = ``parallel_children``): a single root ``lower_half`` part,
with three named module axes that all rewrite the SAME shared ``_wood_half()``
CadQuery solid (or swap the spring part); NONE add or remove a joint -- the
topology equivalence class is always "1 REVOLUTE ``pivot`` + 1 FIXED
``lower_to_spring``":

  * ``spring_mechanism`` (2): torsion_coil (a one-piece swept-wire steel torsion
    spring -> round SEAT_R barrel seat in the wood) / leaf_spring (two tilted
    flat box arms + a short bend, ``for i in range(2)`` -> rectangular box seat).
  * ``jaw_shape`` (3): flat_notched (flat parting face + half-round clothesline
    groove) / rounded_barrel (half-round BARREL_R arc nose, no groove) /
    toothed_serrated (flat parting face + a module-internal ``for`` loop of V
    grooves making serration teeth).
  * ``tail_shape`` (3): flared_pad (rounded flared finger pad) / dished_thumb
    (raised pressing pad + spherical thumb dish cut) / square_stub (blunt flat
    square stub).

The two wooden legs share ONE ``_wood_half()`` solid emitted twice as two named
parts (``lower_half`` root vs ``upper_half`` revolute child); this is NOT a copy
loop -- the legs have different roles. The leaf-spring's two arms (``arm_0`` /
``arm_1``) and the serration teeth are fixed module-internal arrays (one shared
helper, symmetric / even placement, no joints; Rule 1).

The torsion coil / leaf arms nest captured into the carved wood seats (two
non-aligned faces, not a clean axis-aligned mating), so ``pivot`` and
``lower_to_spring`` omit ``MatingContract`` (grandfathered) and rely on the flat
articulation-origin baseline + element-scoped ``allow_overlap(spring, lower)`` /
``allow_overlap(spring, upper)`` (mirroring each source record's run_tests
allow_overlap block).
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

SpringMechanism = Literal["torsion_coil", "leaf_spring"]
JawShape = Literal["flat_notched", "rounded_barrel", "toothed_serrated"]
TailShape = Literal["flared_pad", "dished_thumb", "square_stub"]
PaletteStyle = Literal[
    "natural_wood",
    "painted_wood",
    "colored_plastic",
    "steel_spring_classic",
    "colored_spring_pop",
]

SPRING_MECHANISMS: tuple[SpringMechanism, ...] = ("torsion_coil", "leaf_spring")
JAW_SHAPES: tuple[JawShape, ...] = (
    "flat_notched",
    "rounded_barrel",
    "toothed_serrated",
)
TAIL_SHAPES: tuple[TailShape, ...] = ("flared_pad", "dished_thumb", "square_stub")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "natural_wood",
    "painted_wood",
    "colored_plastic",
    "steel_spring_classic",
    "colored_spring_pop",
)

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: body (the two wooden legs) / spring.
# Every .visual(material=...) is driven off this dict so the swept pool is
# colorful (module_topology_diversity only counts structure, not color).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # parent / variant sample colors: weathered wood + dark steel.
    "natural_wood": {
        "body": (0.42, 0.29, 0.17, 1.0),
        "spring": (0.16, 0.16, 0.18, 1.0),
    },
    # painted wood (white/red lacquer over the grain) + dark steel.
    "painted_wood": {
        "body": (0.86, 0.20, 0.18, 1.0),
        "spring": (0.16, 0.16, 0.18, 1.0),
    },
    # bright plastic clothespin body + bright spring steel.
    "colored_plastic": {
        "body": (0.12, 0.46, 0.82, 1.0),
        "spring": (0.35, 0.38, 0.42, 1.0),
    },
    # natural wood + bright spring steel (leaf_spring sample's spring_steel).
    "steel_spring_classic": {
        "body": (0.42, 0.29, 0.17, 1.0),
        "spring": (0.35, 0.38, 0.42, 1.0),
    },
    # light wood + colored / brass-anodized spring (pop accent).
    "colored_spring_pop": {
        "body": (0.74, 0.58, 0.38, 1.0),
        "spring": (0.80, 0.56, 0.16, 1.0),
    },
}


def _material_class_id(
    surface: Literal["body", "spring"], palette_style: PaletteStyle
) -> str:
    """Return one exact material pool for each resolved visual."""
    if surface == "spring":
        return "metal.stainless_matte"
    if palette_style == "colored_plastic":
        return "plastic.opaque_glossy_molded"
    return "wood.natural_generic"


# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), shared across all 6 source samples.
# A small wooden spring peg: ~72 mm long, ~8.5 mm wide, ~13 mm at the pivot.
# Mechanical fits (spring captured embed, GAP) are not scaled; the peak length /
# leg width / pivot bulge / spring radius / open angle / jaw / tail features are.
# ---------------------------------------------------------------------------
_LEG_LEN = 0.072  # full peg length along X
_HALF_W = 0.0085  # width of one wooden leg (peg-frame Y / world Z)
_GAP = 0.0006  # closed gap between the two flat jaw faces
_PIVOT_X = -0.004  # X of the pivot/fulcrum (slightly back of center)
_TAIL_ANGLE = 0.08  # rad, tail relief per half (keeps tails splayed at rest)

# Torsion coil (spec §7 spring_radius_scale band).
_SPRING_R = 0.0042  # coil centerline radius
_WIRE_R = 0.00055  # steel wire radius
_SEAT_R = 0.0052  # carved half-round spring seat radius (per half)

# Leaf spring strip (spec §7 leaf_strip_scale band).
_STRIP_T = 0.0005  # strip thickness (0.5 mm)
_STRIP_W = 0.006  # strip width along peg Y (6 mm)
_ARM_LEN = 0.024  # arm length from the pivot centre backward
_SEAT_L = 0.006  # rectangular seat length along X
_SEAT_D = 0.003  # rectangular seat depth into the body

# Pivot bulge / profile heights (peg-frame z up from the parting plane).
_Z_PIVOT = 0.0115  # tallest at the pivot bulge
_Z_MID = 0.0070
_Z_NOSE = 0.0042  # thin gripping nose

# Tail profile heights.
_Z_BACK_FLARED = 0.0095
_Z_BACK_SQUARE = 0.0075
_PAD_BULGE = 0.002  # extra height on the dished pad for dish stock
_DISH_R = 0.006  # curvature radius of the concave thumb dish
_DISH_DEPTH = 0.0015  # depth of the thumb depression

# Barrel jaw (rounded_barrel, spec §7 barrel_radius_scale band).
_BARREL_R = 0.0040

# Serration teeth (toothed_serrated, spec §7 tooth_pitch_scale band).
_TOOTH_PITCH = 0.003
_TOOTH_DEPTH = 0.0006

# Pivot max opening per spring family (spec §7 PIVOT_MAX table): the leaf-spring
# sample uses a smaller baseline (0.10) than the coil family (0.16). Both stay
# below the tail-contact angle (~0.176-0.180 rad) so the halves never touch.
_PIVOT_MAX_COIL = 0.16
_PIVOT_MAX_LEAF = 0.10
# Hard ceiling: tails collide near ~0.176 rad; keep a margin.
_PIVOT_MAX_CEILING = 0.170


@dataclass(frozen=True)
class ClothesPegConfig:
    spring_mechanism: SpringMechanism | None = None
    jaw_shape: JawShape | None = None
    tail_shape: TailShape | None = None
    palette_style: PaletteStyle = "natural_wood"
    leg_len_scale: float = 1.0
    half_width_scale: float = 1.0
    pivot_height_scale: float = 1.0
    pivot_open_scale: float = 1.0
    spring_radius_scale: float = 1.0  # conditional @ torsion_coil
    leaf_strip_scale: float = 1.0  # conditional @ leaf_spring
    barrel_radius_scale: float = 1.0  # conditional @ rounded_barrel
    tooth_pitch_scale: float = 1.0  # conditional @ toothed_serrated
    dish_depth_scale: float = 1.0  # conditional @ dished_thumb
    name: str = "clothes_peg"


@dataclass(frozen=True)
class ResolvedClothesPegConfig:
    spring_mechanism: SpringMechanism
    jaw_shape: JawShape
    tail_shape: TailShape
    palette_style: PaletteStyle
    # Core geometry (scaled / derived).
    leg_len: float
    half_w: float
    gap: float
    pivot_x: float
    nose_x: float
    back_x: float
    tail_angle: float
    tail_rise: float
    z_pivot: float
    z_mid: float
    z_nose: float
    # Spring (torsion coil).
    spring_r: float
    wire_r: float
    seat_r: float
    # Spring (leaf).
    strip_t: float
    strip_w: float
    arm_len: float
    seat_l: float
    seat_w: float
    seat_d: float
    # Jaw.
    barrel_r: float
    tooth_pitch: float
    tooth_depth: float
    teeth_start_x: float
    teeth_end_x: float
    n_teeth: int
    # Tail.
    z_back: float
    pad_bulge: float
    dish_r: float
    dish_depth: float
    # Articulation.
    pivot_max: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ClothesPegConfig:
    rng = random.Random(seed)
    # Procedural sampling (spec §8): pick the three named slots first, then the
    # independent + conditional continuous scales. seed=0 is not special.
    return ClothesPegConfig(
        spring_mechanism=rng.choice(SPRING_MECHANISMS),
        jaw_shape=rng.choice(JAW_SHAPES),
        tail_shape=rng.choice(TAIL_SHAPES),
        palette_style=rng.choice(PALETTE_STYLES),
        leg_len_scale=round(rng.uniform(0.88, 1.15), 4),
        half_width_scale=round(rng.uniform(0.90, 1.12), 4),
        pivot_height_scale=round(rng.uniform(0.90, 1.12), 4),
        pivot_open_scale=round(rng.uniform(0.80, 1.10), 4),
        spring_radius_scale=round(rng.uniform(0.85, 1.15), 4),
        leaf_strip_scale=round(rng.uniform(0.85, 1.15), 4),
        barrel_radius_scale=round(rng.uniform(0.85, 1.15), 4),
        tooth_pitch_scale=round(rng.uniform(0.85, 1.20), 4),
        dish_depth_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_clothes_peg_{seed}",
    )


def resolve_config(
    config: ClothesPegConfig | None = None,
) -> ResolvedClothesPegConfig:
    cfg = config or ClothesPegConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    spring_mechanism = _pick(cfg.spring_mechanism, SPRING_MECHANISMS)
    jaw_shape = _pick(cfg.jaw_shape, JAW_SHAPES)
    tail_shape = _pick(cfg.tail_shape, TAIL_SHAPES)

    leg_len_scale = _clamp(cfg.leg_len_scale, 0.88, 1.15)
    half_width_scale = _clamp(cfg.half_width_scale, 0.90, 1.12)
    pivot_height_scale = _clamp(cfg.pivot_height_scale, 0.90, 1.12)
    pivot_open_scale = _clamp(cfg.pivot_open_scale, 0.80, 1.10)

    # --- Core peak geometry (independent scales). ---
    leg_len = _LEG_LEN * leg_len_scale
    half_w = _HALF_W * half_width_scale
    gap = _GAP
    nose_x = leg_len / 2.0
    back_x = -leg_len / 2.0
    # Keep the pivot at the same fraction of the peg length back of center.
    pivot_x = _PIVOT_X * leg_len_scale
    tail_angle = _TAIL_ANGLE
    tail_rise = (pivot_x - back_x) * math.tan(tail_angle)

    z_pivot = _Z_PIVOT * pivot_height_scale
    z_mid = _Z_MID
    z_nose = _Z_NOSE

    # --- Spring (conditional). ---
    spring_radius_scale = _clamp(cfg.spring_radius_scale, 0.85, 1.15)
    leaf_strip_scale = _clamp(cfg.leaf_strip_scale, 0.85, 1.15)

    spring_r = _SPRING_R * spring_radius_scale
    wire_r = _WIRE_R * spring_radius_scale
    # Torsion-coil seat must keep the coil captured (inequality: seat >= coil
    # outer - embed). Outer coil radius ~ spring_r + wire_r; embed in
    # [0.0004, 0.0008]. Also keep the wood bridge above the seat: z_pivot must
    # exceed the seat radius by wood_bridge_min so the seat does not cut through.
    coil_outer = spring_r + wire_r
    seat_r = max(_SEAT_R * spring_radius_scale, coil_outer + 0.0004)
    wood_bridge_min = 0.001
    if z_pivot < seat_r + wood_bridge_min:
        z_pivot = seat_r + wood_bridge_min

    strip_t = _STRIP_T * leaf_strip_scale
    strip_w = _STRIP_W * leaf_strip_scale
    arm_len = _ARM_LEN * leg_len_scale
    seat_l = _SEAT_L * leaf_strip_scale
    seat_d = _SEAT_D * leaf_strip_scale
    seat_w = half_w + 0.004  # through-width cut, same strategy as the samples
    # Keep the wood bridge above the rectangular leaf seat too.
    if spring_mechanism == "leaf_spring" and z_pivot < seat_d + wood_bridge_min:
        z_pivot = seat_d + wood_bridge_min

    # --- Jaw (conditional). ---
    barrel_radius_scale = _clamp(cfg.barrel_radius_scale, 0.85, 1.15)
    tooth_pitch_scale = _clamp(cfg.tooth_pitch_scale, 0.85, 1.20)
    barrel_r = _BARREL_R * barrel_radius_scale
    tooth_pitch = _TOOTH_PITCH * tooth_pitch_scale
    tooth_depth = _TOOTH_DEPTH
    teeth_start_x = pivot_x + 0.008  # ahead of the pivot / spring seat
    teeth_end_x = nose_x - 0.013  # stop before the clothesline groove
    n_teeth = max(4, int((teeth_end_x - teeth_start_x) / tooth_pitch))

    # --- Tail (conditional). ---
    dish_depth_scale = _clamp(cfg.dish_depth_scale, 0.85, 1.15)
    if tail_shape == "square_stub":
        z_back = _Z_BACK_SQUARE
    else:
        z_back = _Z_BACK_FLARED
    pad_bulge = _PAD_BULGE
    dish_r = _DISH_R
    dish_depth = _DISH_DEPTH * dish_depth_scale
    # The dish must not cut through the back pad: cap its depth below the pad
    # stock so wood remains under the depression.
    z_pad = z_back + pad_bulge
    dish_depth = min(dish_depth, z_pad - 0.0035)
    dish_depth = max(dish_depth, 0.0008)

    # --- Articulation: PIVOT_MAX by spring family, scaled + clamped below the
    #     tail-contact ceiling so the halves never interpenetrate (spec §7). ---
    base_pivot_max = _PIVOT_MAX_LEAF if spring_mechanism == "leaf_spring" else _PIVOT_MAX_COIL
    pivot_max = _clamp(base_pivot_max * pivot_open_scale, 0.06, _PIVOT_MAX_CEILING)

    return ResolvedClothesPegConfig(
        spring_mechanism=spring_mechanism,
        jaw_shape=jaw_shape,
        tail_shape=tail_shape,
        palette_style=palette_style,
        leg_len=leg_len,
        half_w=half_w,
        gap=gap,
        pivot_x=pivot_x,
        nose_x=nose_x,
        back_x=back_x,
        tail_angle=tail_angle,
        tail_rise=tail_rise,
        z_pivot=z_pivot,
        z_mid=z_mid,
        z_nose=z_nose,
        spring_r=spring_r,
        wire_r=wire_r,
        seat_r=seat_r,
        strip_t=strip_t,
        strip_w=strip_w,
        arm_len=arm_len,
        seat_l=seat_l,
        seat_w=seat_w,
        seat_d=seat_d,
        barrel_r=barrel_r,
        tooth_pitch=tooth_pitch,
        tooth_depth=tooth_depth,
        teeth_start_x=teeth_start_x,
        teeth_end_x=teeth_end_x,
        n_teeth=n_teeth,
        z_back=z_back,
        pad_bulge=pad_bulge,
        dish_r=dish_r,
        dish_depth=dish_depth,
        pivot_max=pivot_max,
        name=cfg.name or "clothes_peg",
    )


def with_overrides(config: ClothesPegConfig, **kwargs: object) -> ClothesPegConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ClothesPegConfig | ResolvedClothesPegConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedClothesPegConfig)
        else resolve_config(config)
    )
    return (
        ("spring_mechanism", r.spring_mechanism),
        ("jaw_shape", r.jaw_shape),
        ("tail_shape", r.tail_shape),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared wooden-leg solid (the template core). ONE parametric CadQuery solid
# helper covers jaw_shape (front profile) x tail_shape (back profile) x the
# spring seat (round SEAT_R / rectangular box). It is emitted TWICE as two named
# parts (lower_half root / upper_half revolute child) -- NOT a copy loop.
# Authored in the local part frame: long axis +X, width +/-Y, the parting
# (gripping) face on z=0 from the pivot forward, body growing toward +Z. Behind
# the pivot the bottom face ramps up by tail_angle (tail relief).
# ---------------------------------------------------------------------------
def _wood_half_solid(r: ResolvedClothesPegConfig) -> cq.Workplane:
    z_pivot = r.z_pivot
    z_mid = r.z_mid
    z_nose = r.z_nose

    # --- Front nose profile (jaw_shape) + back tail profile (tail_shape). ---
    if r.jaw_shape == "rounded_barrel":
        # Half-round barrel arc nose (no flat tip).
        bx = r.nose_x - r.barrel_r
        bz = r.barrel_r
        n_arc = 12
        arc_pts: list[tuple[float, float]] = []
        for j in range(n_arc + 1):
            a = -math.pi / 2.0 + math.pi * j / n_arc
            arc_pts.append(
                (bx + r.barrel_r * math.cos(a), bz + r.barrel_r * math.sin(a))
            )
        front_pts: list[tuple[float, float]] = [
            (r.pivot_x, 0.0),
            (bx, 0.0),  # parting face ends, barrel arc begins
        ]
        front_pts.extend(arc_pts[1:])  # skip dup of (bx, 0)
        front_pts.append((r.nose_x - 0.012, 2.0 * r.barrel_r - 0.001))
    else:
        # flat_notched / toothed_serrated: flat parting face + flat thin nose.
        front_pts = [
            (r.pivot_x, 0.0),
            (r.nose_x, 0.0),  # flat parting face from pivot to nose
            (r.nose_x, z_nose),  # nose tip
            (r.nose_x - 0.010, z_nose + 0.0006),
        ]

    # Crown over the pivot bulge.
    crown_pts: list[tuple[float, float]] = [
        (r.pivot_x + 0.012, z_mid),
        (r.pivot_x, z_pivot),  # pivot bulge (tallest)
    ]

    # Back tail profile (tail_shape).
    z_back = r.z_back
    if r.tail_shape == "dished_thumb":
        z_pad = z_back + r.pad_bulge
        back_pts = [
            (r.pivot_x - 0.010, z_mid + 0.0010),
            (r.back_x + 0.012, z_back + 0.001),  # shoulder into pressing pad
            (r.back_x + 0.006, z_pad + 0.0005),  # pressing pad crest
            (r.back_x + 0.001, z_pad),  # back edge of pressing pad
        ]
    elif r.tail_shape == "square_stub":
        back_pts = [
            (r.pivot_x - 0.010, z_mid + 0.0005),
            (r.back_x, z_back),  # blunt square stub end (flat top)
        ]
    else:  # flared_pad
        back_pts = [
            (r.pivot_x - 0.010, z_mid + 0.0010),
            (r.back_x + 0.008, z_back + 0.0010),
            (r.back_x, z_back),  # flared finger pad
        ]

    pts: list[tuple[float, float]] = [(r.back_x, r.tail_rise)]
    pts.extend(front_pts)
    pts.extend(crown_pts)
    pts.extend(back_pts)

    leg = cq.Workplane("XZ").polyline(pts).close().extrude(r.half_w)
    # The XZ extrude lands width in Y=(-half_w, 0); recenter on Y=0.
    leg = leg.translate((0.0, r.half_w / 2.0, 0.0))
    leg = leg.edges("|Y").fillet(0.0010)

    # --- Clothesline groove (flat_notched / toothed_serrated only). ---
    if r.jaw_shape in ("flat_notched", "toothed_serrated"):
        groove_w = r.half_w + 0.002
        groove = (
            cq.Workplane("XZ")
            .center(r.nose_x - 0.009, 0.0)
            .circle(0.0022)
            .extrude(groove_w)
            .translate((0.0, groove_w / 2.0, 0.0))
        )
        leg = leg.cut(groove)

    # --- Spring seat (spring_mechanism): round barrel vs rectangular box. ---
    if r.spring_mechanism == "leaf_spring":
        seat = (
            cq.Workplane("XY")
            .box(r.seat_l, r.seat_w, r.seat_d)
            .translate((r.pivot_x - r.seat_l / 4.0, 0.0, r.seat_d / 2.0))
        )
        leg = leg.cut(seat)
    else:  # torsion_coil -> round half-round barrel seat
        seat = (
            cq.Workplane("XZ")
            .center(r.pivot_x, 0.0)
            .circle(r.seat_r)
            .extrude(r.half_w + 0.004)
            .translate((0.0, (r.half_w + 0.004) / 2.0, 0.0))
        )
        leg = leg.cut(seat)

    # --- Serration teeth (toothed_serrated only): module-internal for-loop. ---
    if r.jaw_shape == "toothed_serrated":
        cut_width = r.half_w + 0.002
        half_pitch = r.tooth_pitch / 4.0
        for i in range(r.n_teeth):
            tx = r.teeth_start_x + i * r.tooth_pitch
            groove = (
                cq.Workplane("XZ")
                .moveTo(tx - half_pitch, -0.0002)
                .lineTo(tx + half_pitch, -0.0002)
                .lineTo(tx, r.tooth_depth)
                .close()
                .extrude(cut_width)
                .translate((0.0, cut_width / 2.0, 0.0))
            )
            leg = leg.cut(groove)

    # --- Dished thumb depression (dished_thumb only). ---
    if r.tail_shape == "dished_thumb":
        z_pad = z_back + r.pad_bulge
        dish_x = r.back_x + 0.005
        dish_center_z = z_pad + r.dish_r - r.dish_depth
        dish_sphere = (
            cq.Workplane("XY")
            .center(dish_x, 0.0)
            .sphere(r.dish_r)
            .translate((0.0, 0.0, dish_center_z))
        )
        leg = leg.cut(dish_sphere)

    return leg


# ---------------------------------------------------------------------------
# Spring meshes (spring_mechanism). torsion_coil -> one swept-wire tube; the
# leaf spring -> two tilted flat box arms (for-loop, shared helper) + a bend.
# ---------------------------------------------------------------------------
def _torsion_coil_mesh(r: ResolvedClothesPegConfig):
    """One-piece steel torsion spring: central coil on the pivot axis + two
    straight legs lying on the relieved inner tail faces of both halves."""
    tan_a = math.tan(r.tail_angle)

    def lower_face_z(d: float) -> float:
        return -r.gap / 2.0 - d * tan_a

    def upper_face_z(d: float) -> float:
        return r.gap / 2.0 + d * tan_a

    y_lo = -r.half_w * 0.42
    y_hi = r.half_w * 0.42

    pts: list[tuple[float, float, float]] = []
    for d in (0.024, 0.012):
        pts.append((r.pivot_x - d, y_lo, lower_face_z(d) + r.wire_r))

    a0 = math.pi + 0.12
    sweep = 2.0 * (2.0 * math.pi) - 0.24
    n = 64
    for i in range(n + 1):
        t = i / n
        a = a0 + sweep * t
        y = y_lo + (y_hi - y_lo) * t
        x = r.pivot_x + r.spring_r * math.cos(a)
        z = r.spring_r * math.sin(a)
        pts.append((x, y, z))

    for d in (0.012, 0.024):
        pts.append((r.pivot_x - d, y_hi, upper_face_z(d) - r.wire_r))

    geom = tube_from_spline_points(
        pts,
        radius=r.wire_r,
        samples_per_segment=8,
        radial_segments=12,
        cap_ends=True,
    )
    return mesh_from_geometry(geom, "torsion_coil")


def _leaf_arm_solid(r: ResolvedClothesPegConfig, sign: float) -> cq.Workplane:
    """One flat leaf-spring arm in the peg frame. sign=+1 upper, -1 lower."""
    arm = cq.Workplane("XY").box(r.arm_len, r.strip_w, r.strip_t)
    arm = arm.rotate(
        (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), sign * math.degrees(r.tail_angle)
    )
    cx = r.pivot_x - (r.arm_len / 2.0) * math.cos(r.tail_angle)
    cz = sign * (r.gap / 2.0 + (r.arm_len / 2.0) * math.sin(r.tail_angle))
    arm = arm.translate((cx, 0.0, cz))
    return arm


def _leaf_bend_solid(r: ResolvedClothesPegConfig) -> cq.Workplane:
    bend_h = r.gap + r.strip_t
    bend = cq.Workplane("XY").box(r.strip_t, r.strip_w, bend_h)
    bend = bend.translate((r.pivot_x, 0.0, 0.0))
    return bend


# ---------------------------------------------------------------------------
# Part builders.
# ---------------------------------------------------------------------------
def _emit_wood_legs(
    model: ArticulatedObject, r: ResolvedClothesPegConfig, mats, *, assets
):
    """Emit the two wooden legs (shared solid, two named parts) + the pivot."""
    half_solid = _wood_half_solid(r)

    # World placement: the peg lies flat. peg-frame +Z maps to world -Y;
    # peg-frame +/-Y (width) maps to world Z; lift by half_w/2 so it rests on z=0.
    lower = model.part("lower_half")
    lower.visual(
        mesh_from_cadquery(half_solid, "lower_half", assets=assets),
        origin=Origin(
            xyz=(0.0, r.gap / 2.0, r.half_w / 2.0),
            rpy=(-math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["body"],
        material_class_id=_material_class_id("body", r.palette_style),
        name="lower_half",
    )
    lower.inertial = Inertial.from_geometry(
        Box((r.leg_len, r.half_w, r.z_pivot)),
        mass=0.004,
        origin=Origin(xyz=(0.0, r.gap / 2.0, r.half_w / 2.0)),
    )

    upper = model.part("upper_half")
    upper.visual(
        mesh_from_cadquery(half_solid, "upper_half", assets=assets),
        origin=Origin(xyz=(-r.pivot_x, 0.0, r.gap / 2.0), rpy=(0.0, 0.0, 0.0)),
        material=mats["body"],
        material_class_id=_material_class_id("body", r.palette_style),
        name="upper_half",
    )
    upper.inertial = Inertial.from_geometry(
        Box((r.leg_len, r.half_w, r.z_pivot)),
        mass=0.004,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    # pivot REVOLUTE: shared single active joint. Origin on the spring-barrel
    # fulcrum; axis (0,-1,0) (joint-frame -Y = world vertical). Captured-pin
    # geometry -> grandfathered (no MatingContract).
    model.articulation(
        "pivot",
        ArticulationType.REVOLUTE,
        parent=lower,
        child=upper,
        origin=Origin(
            xyz=(r.pivot_x, 0.0, r.half_w / 2.0),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=4.0, lower=0.0, upper=r.pivot_max
        ),
    )
    return lower, upper


def _emit_spring(
    model: ArticulatedObject, r: ResolvedClothesPegConfig, lower, mats, *, assets
):
    """Emit the spring part (torsion coil OR leaf strip) + the FIXED joint."""
    spring_origin = Origin(
        xyz=(0.0, 0.0, r.half_w / 2.0), rpy=(math.pi / 2.0, 0.0, 0.0)
    )
    spring = model.part("spring")

    if r.spring_mechanism == "leaf_spring":
        # Two tilted flat arms (for-loop + shared helper) + a short bend.
        for i in range(2):
            sign = 1.0 if i == 1 else -1.0
            arm_solid = _leaf_arm_solid(r, sign)
            spring.visual(
                mesh_from_cadquery(arm_solid, f"arm_{i}", assets=assets),
                origin=spring_origin,
                material=mats["spring"],
                material_class_id=_material_class_id("spring", r.palette_style),
                name=f"arm_{i}",
            )
        bend_solid = _leaf_bend_solid(r)
        spring.visual(
            mesh_from_cadquery(bend_solid, "bend", assets=assets),
            origin=spring_origin,
            material=mats["spring"],
            material_class_id=_material_class_id("spring", r.palette_style),
            name="bend",
        )
        spring.inertial = Inertial.from_geometry(
            Box((r.arm_len, r.strip_w, r.gap + r.strip_t)),
            mass=0.001,
            origin=Origin(xyz=(0.0, 0.0, r.half_w / 2.0)),
        )
    else:  # torsion_coil
        spring.visual(
            _torsion_coil_mesh(r),
            origin=spring_origin,
            material=mats["spring"],
            material_class_id=_material_class_id("spring", r.palette_style),
            name="torsion_coil",
        )
        spring.inertial = Inertial.from_geometry(
            Cylinder(radius=r.spring_r + r.wire_r, length=r.half_w),
            mass=0.001,
            origin=Origin(xyz=(r.pivot_x, 0.0, r.half_w / 2.0)),
        )

    # lower_to_spring FIXED: the spring rides rigidly with the root half.
    model.articulation(
        "lower_to_spring",
        ArticulationType.FIXED,
        parent=lower,
        child=spring,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    return spring


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_clothes_peg(
    config: ClothesPegConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"clothes_peg_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    lower, _upper = _emit_wood_legs(model, r, mats, assets=assets)
    _emit_spring(model, r, lower, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_clothes_peg(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_clothes_peg(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_clothes_peg_tests(
    object_model: ArticulatedObject,
    config: ClothesPegConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    lower = object_model.get_part("lower_half")
    upper = object_model.get_part("upper_half")
    spring = object_model.get_part("spring")

    # ---- Captured-spring allowances (element-scoped): coil/arms nest inside
    #      the carved wood seats of both halves (mirrors each source run_tests). ----
    if r.spring_mechanism == "leaf_spring":
        for elem in ("arm_0", "arm_1", "bend"):
            ctx.allow_overlap(
                spring, lower, elem_a=elem, elem_b="lower_half",
                reason="Leaf spring is captured/seated inside the lower half pivot recess.",
            )
            ctx.allow_overlap(
                spring, upper, elem_a=elem, elem_b="upper_half",
                reason="Leaf spring is captured/seated inside the upper half pivot recess.",
            )
    else:
        ctx.allow_overlap(
            spring, lower, elem_a="torsion_coil", elem_b="lower_half",
            reason="Torsion spring coil is captured/seated inside the lower half pivot seat.",
        )
        ctx.allow_overlap(
            spring, upper, elem_a="torsion_coil", elem_b="upper_half",
            reason="Torsion spring coil is captured/seated inside the upper half pivot seat.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Single root + exactly one non-fixed joint (shared topology). ----
    roots = object_model.root_parts()
    ctx.check(
        "lower_half is the single root",
        len(roots) == 1 and roots[0].name == "lower_half",
        details=f"roots={[p.name for p in roots]}",
    )
    non_fixed = [
        a for a in object_model.articulations
        if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "exactly one non-fixed joint (the pivot)",
        len(non_fixed) == 1 and non_fixed[0].name == "pivot",
        details=f"non_fixed={[a.name for a in non_fixed]}",
    )

    pivot = object_model.get_articulation("pivot")
    ctx.check(
        "pivot is REVOLUTE about the joint-frame -Y (world vertical)",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and abs(pivot.axis[1]) > 0.99
        and abs(pivot.axis[0]) < 1e-6
        and abs(pivot.axis[2]) < 1e-6,
        details=f"type={pivot.articulation_type} axis={tuple(pivot.axis)}",
    )
    fixed = object_model.get_articulation("lower_to_spring")
    ctx.check(
        "spring is FIXED to lower half",
        fixed.articulation_type == ArticulationType.FIXED,
        details=f"type={fixed.articulation_type}",
    )

    # ---- Spring located at the pivot, straddling the parting plane. ----
    spring_box = ctx.part_world_aabb(spring)
    ctx.check(
        "spring located at the pivot",
        spring_box is not None
        and spring_box[0][0] < r.pivot_x
        and spring_box[1][0] >= r.pivot_x,
        details=f"spring_aabb={spring_box}, pivot_x={r.pivot_x}",
    )
    ctx.check(
        "spring straddles the parting plane",
        spring_box is not None
        and spring_box[0][1] < -0.0005
        and spring_box[1][1] > 0.0005,
        details=None if spring_box is None
        else f"spring_y=({spring_box[0][1]:.4f},{spring_box[1][1]:.4f})",
    )
    if r.spring_mechanism == "leaf_spring":
        spring_visual_names = {v.name for v in spring.visuals}
        ctx.check(
            "leaf spring has arm_0, arm_1, bend visuals",
            {"arm_0", "arm_1", "bend"}.issubset(spring_visual_names),
            details=f"visuals={spring_visual_names}",
        )
        ctx.check(
            "leaf spring arms extend backward from the pivot (flat strip)",
            spring_box is not None
            and (r.pivot_x - spring_box[0][0]) > r.arm_len * 0.6,
            details=None if spring_box is None
            else f"backward_extent={r.pivot_x - spring_box[0][0]:.4f}",
        )

    # ---- Both wooden legs span the peg length; peg rests on the ground. ----
    lower_box = ctx.part_world_aabb(lower)
    upper_box = ctx.part_world_aabb(upper)
    lower_len = None if lower_box is None else lower_box[1][0] - lower_box[0][0]
    upper_len = None if upper_box is None else upper_box[1][0] - upper_box[0][0]
    ctx.check(
        "lower leg spans the peg length",
        lower_len is not None and lower_len > r.leg_len * 0.9,
        details=f"len_x={lower_len}",
    )
    ctx.check(
        "upper leg spans the peg length",
        upper_len is not None and upper_len > r.leg_len * 0.9,
        details=f"len_x={upper_len}",
    )
    ctx.check(
        "peg rests on the ground (z_min ~ 0)",
        lower_box is not None and abs(lower_box[0][2]) < 0.0005,
        details=None if lower_box is None else f"lower_zmin={lower_box[0][2]:.5f}",
    )

    # ---- Closed rest pose (q=0): mirror halves nearly touch at the jaws. ----
    with ctx.pose({pivot: 0.0}):
        lb = ctx.part_world_aabb(lower)
        ub = ctx.part_world_aabb(upper)
        ctx.check(
            "closed: lower half at +Y, upper half at -Y of the parting plane",
            lb is not None and ub is not None
            and lb[1][1] > 0.002 and ub[0][1] < -0.002,
            details=None if (lb is None or ub is None)
            else f"lower_ymax={lb[1][1]:.4f}, upper_ymin={ub[0][1]:.4f}",
        )
        ctx.expect_gap(
            lower, upper, axis="y", max_gap=0.005, max_penetration=0.0002,
            name="closed jaws nearly touch at the parting plane",
        )

    # ---- Opened pose (q=PIVOT_MAX): the jaw actually swings open. ----
    with ctx.pose({pivot: 0.0}):
        upper_closed = ctx.part_world_aabb(upper)
    with ctx.pose({pivot: r.pivot_max}):
        upper_open = ctx.part_world_aabb(upper)
        # The tail swings toward +Y in the 1-D Y projection even though the 3-D
        # parts clear via the tail relief; allow the projected penetration.
        ctx.expect_gap(
            lower, upper, axis="y", max_gap=0.02, max_penetration=0.003,
            name="fully open halves clear in the Y projection",
        )
    # The nose Y-swing scales with the nose lever arm and the open angle; small
    # open angles (leaf family, short pegs) move the nose only ~2-3 mm, so the
    # threshold is derived from the geometry (60% of the ideal point swing)
    # rather than a fixed absolute, while still proving meaningful motion.
    nose_lever = r.nose_x - r.pivot_x
    expected_swing = nose_lever * math.sin(r.pivot_max)
    min_swing = max(0.0015, 0.6 * expected_swing)
    ctx.check(
        "opening the pivot swings the upper jaw open",
        upper_closed is not None and upper_open is not None
        and upper_open[0][1] < upper_closed[0][1] - min_swing,
        details=None if (upper_closed is None or upper_open is None)
        else (
            f"ymin_closed={upper_closed[0][1]:.4f}, ymin_open={upper_open[0][1]:.4f}, "
            f"min_swing={min_swing:.4f}"
        ),
    )

    # ---- Jaw identity: the lower leg reaches the gripping nose tip. ----
    nose_tip = ctx.part_element_world_aabb(lower, elem="lower_half")
    lower_max_x = None if nose_tip is None else nose_tip[1][0]
    ctx.check(
        "lower leg reaches the gripping nose",
        lower_max_x is not None and lower_max_x >= r.nose_x - 0.001,
        details=f"lower_max_x={lower_max_x}",
    )

    return ctx.report()


__all__ = (
    "ClothesPegConfig",
    "ResolvedClothesPegConfig",
    "build_clothes_peg",
    "build_seeded_clothes_peg",
    "config_from_seed",
    "resolve_config",
    "run_clothes_peg_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
