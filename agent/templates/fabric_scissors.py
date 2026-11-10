# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Modular fabric_scissors template (Textiles_Fabric / Fabric scissors).
#
# Identity: two forged steel blades crossing at ONE pivot screw, opening/closing
# on a single REVOLUTE joint, with a honed shear line and finger grip(s). Every
# 5-star source (2 origins + 8 forks) is EXACTLY two parts + one pivot revolute;
# edges, handles and spring yokes are non-articulating VISUALS on those two
# parts (Rule 1). This template preserves that skeleton and derives all module
# geometry from the declared sources.
#
# Slots (discrete, report via slot_choices_for_seed):
#   - blade_form  (Slot A, ROOT / ③ Primary Form Family, the dominant axis):
#       pointed_honed / pinking_zigzag / scalloping_wave / micro_serrated
#       / duckbill_paddle / curved_trimming. Chooses the two blade plates + the
#       cutting-edge treatment on both shears, and emits the pivot revolute.
#   - handle_style (Slot B, ② handle topology): offset_asymmetric_bent /
#       symmetric_inline_bows / spring_squeeze_yoke. Adds tang + grip VISUALS to
#       both shears (parallel-children over the two blade parts; no new joint —
#       a scissor grip does not articulate).
#   - edge multiplicity (§8 axis): pinking / scalloping tooth count N (loop
#       emitted, meshing rows on both blades).
#
# Backbone: pure-python extruded-polygon meshes (ExtrudeGeometry /
# ExtrudeWithHolesGeometry / ring-extrude), matching family-001 sources; the
# cadquery forks' extruded-polygon primitives are reproduced as the same mesh
# family (Rule 3 — no downgrade to Box/Cylinder for the blade bodies).
import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    superellipse_profile,
)

__modular__ = True

BladeForm = Literal[
    "pointed_honed",
    "pinking_zigzag",
    "scalloping_wave",
    "micro_serrated",
    "duckbill_paddle",
    "curved_trimming",
]
HandleStyle = Literal[
    "offset_asymmetric_bent",
    "symmetric_inline_bows",
    "spring_squeeze_yoke",
]
PaletteTheme = Literal[
    "brushed_steel_black",
    "blued_black_brass",
    "chrome_red",
    "gold_ivory",
]

BLADE_FORMS: tuple[BladeForm, ...] = (
    "pointed_honed",
    "pinking_zigzag",
    "scalloping_wave",
    "micro_serrated",
    "duckbill_paddle",
    "curved_trimming",
)
HANDLE_STYLES: tuple[HandleStyle, ...] = (
    "offset_asymmetric_bent",
    "symmetric_inline_bows",
    "spring_squeeze_yoke",
)
PALETTE_THEMES: tuple[PaletteTheme, ...] = (
    "brushed_steel_black",
    "blued_black_brass",
    "chrome_red",
    "gold_ivory",
)

# blade_form -> (body_style, edge_style). body drives the plate profile / warp;
# edge drives the cutting-bevel treatment. Each pairing traces to a real fork.
_FORM_MAP: dict[BladeForm, tuple[str, str]] = {
    "pointed_honed": ("pointed", "honed"),  # origins A/B
    "pinking_zigzag": ("pointed", "pinking"),  # var_pinking_n9 / n15
    "scalloping_wave": ("pointed", "scallop"),  # var_scalloping
    "micro_serrated": ("pointed", "serrated"),  # var_serrated
    "duckbill_paddle": ("duckbill", "honed"),  # var_duckbill
    "curved_trimming": ("curved", "honed"),  # var_curved
}

# ---- nominal key dimensions (meters), from the 5-star sources ----
BLADE_T = 0.0030  # blade plate thickness (family-001 BLADE_THICKNESS)
BEVEL_T = 0.0008  # polished cutting bevel thickness
HANDLE_T = 0.0070  # plastic loop / yoke extrusion width (family-001 HANDLE_THICKNESS)
UPPER_Z = 0.0025  # upper plate mid-z  -> [0.001, 0.004]
LOWER_Z = -0.0025  # lower plate mid-z -> [-0.004, -0.001]
PIVOT_HOLE_R = 0.0072
UPPER_LOOP_Z = 0.0050
LOWER_LOOP_Z = -0.0050
YOKE_Z = 0.0  # spring yoke centered on the blade plane

CURVE_RISE = 0.012  # curved_trimming tip lift (var_curved)
CURVE_REF_X = -0.210

SERR_COUNT = 18  # micro_serrated fixed tooth count (lower blade only)


# --------------------------------------------------------------------------- #
# Palette
# --------------------------------------------------------------------------- #
def _palette(theme: PaletteTheme) -> dict[str, tuple[float, float, float, float]]:
    steel = (0.74, 0.76, 0.78, 1.0)
    blued = (0.12, 0.14, 0.18, 1.0)
    chrome = (0.85, 0.87, 0.90, 1.0)
    gold = (0.87, 0.70, 0.28, 1.0)
    bright = (0.92, 0.94, 0.96, 1.0)
    black_pl = (0.03, 0.03, 0.035, 1.0)
    red_pl = (0.72, 0.10, 0.11, 1.0)
    ivory = (0.90, 0.86, 0.76, 1.0)
    brass = (0.96, 0.73, 0.34, 1.0)
    slot_dark = (0.02, 0.02, 0.02, 1.0)
    if theme == "brushed_steel_black":
        blade, edge, handle, screw = steel, bright, black_pl, (0.55, 0.57, 0.60, 1.0)
    elif theme == "blued_black_brass":
        blade, edge, handle, screw = blued, (0.72, 0.77, 0.82, 1.0), black_pl, brass
    elif theme == "chrome_red":
        blade, edge, handle, screw = chrome, bright, red_pl, chrome
    else:  # gold_ivory
        blade, edge, handle, screw = steel, bright, ivory, gold
    return {
        "blade": blade,
        "edge": edge,
        "handle": handle,
        "screw": screw,
        "slot": slot_dark,
        "yoke": (0.48, 0.52, 0.58, 1.0),
    }


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class FabricScissorsConfig:
    blade_form: BladeForm = "pointed_honed"
    handle_style: HandleStyle = "offset_asymmetric_bent"
    palette_theme: PaletteTheme = "brushed_steel_black"
    n_edge_teeth: int = 0
    size_scale: float = 1.0
    loop_scale: float = 1.0
    name: str = "fabric_tailor_shears"


@dataclass(frozen=True)
class ResolvedFabricScissorsConfig:
    blade_form: BladeForm
    handle_style: HandleStyle
    palette_theme: PaletteTheme
    body_style: str
    edge_style: str
    n_edge_teeth: int
    size_scale: float
    loop_scale: float
    pivot_lower: float
    pivot_upper: float
    name: str


def config_from_seed(seed: int) -> FabricScissorsConfig:
    """Deterministic procedural sampling for every seed (seed 0 not special)."""
    rng = random.Random(seed)
    blade_form: BladeForm = rng.choice(BLADE_FORMS)
    handle_style: HandleStyle = rng.choice(HANDLE_STYLES)
    palette_theme: PaletteTheme = rng.choice(PALETTE_THEMES)

    body_style, edge_style = _FORM_MAP[blade_form]
    # §8 multiplicity: pinking/scalloping tooth rows are loop-emitted, weighted
    # toward small N with a rarer fine tail.
    if edge_style == "pinking":
        n_edge_teeth = rng.choices((7, 9, 11, 13, 15, 18), weights=(0.24, 0.24, 0.20, 0.14, 0.10, 0.08))[0]
    elif edge_style == "scallop":
        n_edge_teeth = rng.choices((7, 8, 9, 10, 12), weights=(0.26, 0.24, 0.22, 0.16, 0.12))[0]
    else:
        n_edge_teeth = 0

    return FabricScissorsConfig(
        blade_form=blade_form,
        handle_style=handle_style,
        palette_theme=palette_theme,
        n_edge_teeth=n_edge_teeth,
        size_scale=round(rng.uniform(0.90, 1.12), 3),
        loop_scale=round(rng.uniform(0.90, 1.12), 3),
        name=f"seeded_fabric_scissors_{seed}",
    )


def resolve_config(config: FabricScissorsConfig) -> ResolvedFabricScissorsConfig:
    if config.blade_form not in BLADE_FORMS:
        raise ValueError(f"Unsupported blade_form: {config.blade_form}")
    if config.handle_style not in HANDLE_STYLES:
        raise ValueError(f"Unsupported handle_style: {config.handle_style}")
    if config.palette_theme not in PALETTE_THEMES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    body_style, edge_style = _FORM_MAP[config.blade_form]

    n_edge_teeth = int(config.n_edge_teeth)
    if edge_style == "pinking":
        n_edge_teeth = max(6, min(n_edge_teeth if n_edge_teeth else 9, 18))
    elif edge_style == "scallop":
        n_edge_teeth = max(6, min(n_edge_teeth if n_edge_teeth else 9, 12))
    else:
        n_edge_teeth = 0

    size_scale = max(0.85, min(float(config.size_scale), 1.15))
    loop_scale = max(0.85, min(float(config.loop_scale), 1.18))

    # ② motion envelope: the spring squeeze yoke rests open and squeezes closed,
    # so its revolute lives on a non-negative squeeze range; loop shears swing
    # both directions about the crossed rest pose. Single-sourced here.
    if config.handle_style == "spring_squeeze_yoke":
        pivot_lower, pivot_upper = 0.0, 0.40
    else:
        pivot_lower, pivot_upper = -0.30, 0.55

    return ResolvedFabricScissorsConfig(
        blade_form=config.blade_form,
        handle_style=config.handle_style,
        palette_theme=config.palette_theme,
        body_style=body_style,
        edge_style=edge_style,
        n_edge_teeth=n_edge_teeth,
        size_scale=size_scale,
        loop_scale=loop_scale,
        pivot_lower=pivot_lower,
        pivot_upper=pivot_upper,
        name=config.name,
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    if r.edge_style in ("pinking", "scallop"):
        mult = str(r.n_edge_teeth)
    elif r.edge_style == "serrated":
        mult = "serr_fixed"
    else:
        mult = "none"
    return [
        ("blade_form", r.blade_form),
        ("handle_style", r.handle_style),
        ("edge_multiplicity", mult),
    ]


# --------------------------------------------------------------------------- #
# 2-D helpers
# --------------------------------------------------------------------------- #
def _scale(pts: list[tuple[float, float]], sc: float) -> list[tuple[float, float]]:
    return [(x * sc, y * sc) for x, y in pts]


def _mirror_y(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(x, -y) for x, y in pts]


def _oriented(pts: list[tuple[float, float]], sign: int, sc: float) -> list[tuple[float, float]]:
    """Upper (sign>0) keeps the nominal +y-spine profile; lower mirrors it."""
    out = pts if sign > 0 else _mirror_y(pts)
    return _scale(out, sc)


def _oval_profile(width, height, *, center=(0.0, 0.0), exponent=2.2, segments=40):
    prof = superellipse_profile(width, height, exponent=exponent, segments=segments)
    cx, cy = center
    return [(x + cx, y + cy) for x, y in prof]


def _ring_geometry(outer, inner, height) -> MeshGeometry:
    if len(outer) != len(inner):
        raise ValueError("ring profiles need matching segment counts")
    z0 = -height / 2.0
    z1 = height / 2.0
    geom = MeshGeometry()
    ob = [geom.add_vertex(x, y, z0) for x, y in outer]
    ot = [geom.add_vertex(x, y, z1) for x, y in outer]
    ib = [geom.add_vertex(x, y, z0) for x, y in inner]
    it = [geom.add_vertex(x, y, z1) for x, y in inner]
    n = len(outer)
    for i in range(n):
        j = (i + 1) % n
        geom.add_face(ob[i], ob[j], ot[j])
        geom.add_face(ob[i], ot[j], ot[i])
        geom.add_face(ib[i], it[j], ib[j])
        geom.add_face(ib[i], it[i], it[j])
        geom.add_face(ot[i], ot[j], it[j])
        geom.add_face(ot[i], it[j], it[i])
        geom.add_face(ob[i], ib[j], ob[j])
        geom.add_face(ob[i], ib[i], ib[j])
    return geom


def _arc_z(x: float) -> float:
    if x >= 0.0:
        return 0.0
    t = min(1.0, abs(x) / abs(CURVE_REF_X))
    return CURVE_RISE * t * t


def _apply_curve(flat: MeshGeometry) -> MeshGeometry:
    curved = MeshGeometry()
    for x, y, z in flat.vertices:
        curved.add_vertex(x, y, z + _arc_z(x))
    for face in flat.faces:
        curved.add_face(*face)
    return curved


# --------------------------------------------------------------------------- #
# Blade plate + cutting bevel (nominal profiles in the upper-blade frame)
# --------------------------------------------------------------------------- #
# Pointed forged blade: tip -> spine (+y) -> pivot shoulder -> cutting edge (-y
# near pivot, rising to the tip) -> back to tip. Encloses the pivot at (0,0).
_POINTED_PLATE = [
    (-0.210, 0.030),   # sharp point
    (-0.055, 0.048),   # thick spine back
    (-0.015, 0.034),
    (0.020, 0.020),    # pivot shoulder (top)
    (0.032, 0.006),    # rear shoulder near pivot
    (0.032, -0.013),   # rear shoulder (below axis)
    (-0.030, -0.007),  # honed cutting edge near pivot
    (-0.205, 0.020),   # honed cutting edge to the tip
]

# Broad duckbill / pelican paddle (lower blade only): rounded blunt nose, wide
# flat top riding surface, broad underside. Kept in the lower orientation.
_DUCKBILL_PADDLE = [
    (-0.216, -0.022),  # bottom of the rounded blunt nose
    (-0.232, -0.002),  # nose apex
    (-0.216, 0.018),   # top of the rounded nose
    (-0.150, 0.021),   # flat riding top
    (-0.060, 0.019),
    (0.020, 0.014),    # pivot shoulder
    (0.032, 0.004),
    (0.032, -0.016),
    (-0.060, -0.044),  # broad flat underside
    (-0.150, -0.050),
    (-0.208, -0.040),
]

# Cutting-edge polyline (upper frame), tip -> pivot, along the honed side.
_POINTED_EDGE = [(-0.200, 0.017), (-0.130, 0.010), (-0.060, 0.001), (-0.014, -0.005)]
# Duckbill riding edge runs along the flat paddle top.
_DUCKBILL_EDGE = [(-0.208, 0.012), (-0.130, 0.014), (-0.060, 0.013), (-0.014, 0.011)]


def _plate_profile(sign: int, body_style: str, sc: float) -> list[tuple[float, float]]:
    if body_style == "duckbill" and sign < 0:
        return _scale(_DUCKBILL_PADDLE, sc)
    return _oriented(_POINTED_PLATE, sign, sc)


def _edge_polyline(sign: int, body_style: str, sc: float) -> list[tuple[float, float]]:
    base = _DUCKBILL_EDGE if (body_style == "duckbill" and sign < 0) else _POINTED_EDGE
    return _oriented(base, sign, sc)


def _plate_geometry(sign: int, r: ResolvedFabricScissorsConfig) -> MeshGeometry:
    prof = _plate_profile(sign, r.body_style, r.size_scale)
    hole = _oval_profile(
        PIVOT_HOLE_R * 2.0 * r.size_scale,
        PIVOT_HOLE_R * 2.0 * r.size_scale,
        exponent=2.0,
        segments=28,
    )
    flat = ExtrudeWithHolesGeometry(prof, [hole], BLADE_T, center=True)
    if r.body_style == "curved":
        return _apply_curve(flat)
    return flat


def _bevel_geometry(sign: int, r: ResolvedFabricScissorsConfig) -> MeshGeometry:
    """Thin polished strip hugging the cutting edge (inner offset into the body)."""
    edge = _edge_polyline(sign, r.body_style, r.size_scale)
    inward = 0.006 * r.size_scale * (1.0 if sign > 0 else -1.0)
    inner = [(x, y + inward) for x, y in edge]
    poly = edge + list(reversed(inner))
    flat = ExtrudeGeometry(poly, BEVEL_T, center=True)
    if r.body_style == "curved":
        return _apply_curve(flat)
    return flat


def _tooth_geometry(base_w: float, height: float, thickness: float) -> MeshGeometry:
    """Triangular tooth pointing +x-local; rooted at x<0 for edge embedding."""
    prof = [(-0.0015, -base_w / 2.0), (-0.0015, base_w / 2.0), (height, 0.0)]
    return ExtrudeGeometry(prof, thickness, center=True)


def _emit_edge_teeth(
    part, sign: int, r: ResolvedFabricScissorsConfig, z_center: float, mat
) -> int:
    """Loop-emit meshing edge teeth (pinking / scallop / serration).

    Teeth protrude from the cutting edge toward the shear line; each root embeds
    into the bevel strip for connectivity. Returns the tooth count emitted.
    """
    edge = _edge_polyline(sign, r.body_style, r.size_scale)
    style = r.edge_style
    if style == "pinking":
        n, amp, base_w = r.n_edge_teeth, 0.0034 * r.size_scale, None
        half_off = 0.5 if sign > 0 else 0.0  # half-pitch offset so rows mesh
    elif style == "scallop":
        n, amp, base_w = r.n_edge_teeth, 0.0022 * r.size_scale, None
        half_off = 0.5 if sign > 0 else 0.0
    elif style == "serrated":
        if sign > 0:  # micro serrations on the lower blade only
            return 0
        n, amp, base_w = SERR_COUNT, 0.0008 * r.size_scale, 0.0013 * r.size_scale
        half_off = 0.0
    else:
        return 0

    # Arc-length resample of the edge for even tooth spacing.
    seglen = []
    for i in range(len(edge) - 1):
        seglen.append(math.hypot(edge[i + 1][0] - edge[i][0], edge[i + 1][1] - edge[i][1]))
    total = sum(seglen)

    def _interp(t: float):
        target = t * total
        acc = 0.0
        for i, sl in enumerate(seglen):
            if acc + sl >= target or i == len(seglen) - 1:
                lt = (target - acc) / sl if sl > 1e-12 else 0.0
                lt = max(0.0, min(1.0, lt))
                x = edge[i][0] + lt * (edge[i + 1][0] - edge[i][0])
                y = edge[i][1] + lt * (edge[i + 1][1] - edge[i][1])
                tx = (edge[i + 1][0] - edge[i][0]) / sl if sl > 1e-12 else 1.0
                ty = (edge[i + 1][1] - edge[i][1]) / sl if sl > 1e-12 else 0.0
                return (x, y), (tx, ty)
            acc += sl
        return edge[-1], (1.0, 0.0)

    tw = base_w if base_w is not None else (total / max(1, n)) * 0.9
    tooth_mesh = mesh_from_geometry(_tooth_geometry(tw, amp, BEVEL_T + 0.0004), f"{part.name}_edge_tooth")
    count = 0
    for i in range(n):
        t = (i + 0.5 + half_off) / n
        if t >= 1.0:
            continue
        (x, y), (tx, ty) = _interp(t)
        # outward normal (toward the shear line = away from blade body/spine)
        nx, ny = ty, -tx
        if (sign > 0 and ny > 0) or (sign < 0 and ny < 0):
            nx, ny = -nx, -ny
        yaw = math.atan2(ny, nx)
        part.visual(
            tooth_mesh,
            origin=Origin(xyz=(x, y, z_center), rpy=(0.0, 0.0, yaw)),
            material=mat,
            name=f"edge_tooth_{count}", material_class_id="metal.stainless_matte",
        )
        count += 1
    return count


# --------------------------------------------------------------------------- #
# Blade builder (one shear)
# --------------------------------------------------------------------------- #
def _build_blade(part, sign: int, r: ResolvedFabricScissorsConfig, pal) -> None:
    sc = r.size_scale
    z_plate = UPPER_Z if sign > 0 else LOWER_Z
    plate_top = z_plate + BLADE_T / 2.0

    part.visual(
        mesh_from_geometry(_plate_geometry(sign, r), f"{part.name}_plate"),
        origin=Origin(xyz=(0.0, 0.0, z_plate)),
        material=pal["blade"],
        name="blade_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"blued_black_brass", "chrome_red", "gold_ivory"} else "metal.brushed_silver"),
    )
    # Polished cutting bevel just proud of the plate outer face.
    bevel_z = plate_top + BEVEL_T / 2.0 - 0.0002
    part.visual(
        mesh_from_geometry(_bevel_geometry(sign, r), f"{part.name}_bevel"),
        origin=Origin(xyz=(0.0, 0.0, bevel_z)),
        material=pal["edge"],
        name="cutting_bevel", material_class_id="metal.stainless_matte",
    )
    _emit_edge_teeth(part, sign, r, bevel_z, pal["edge"])

    # Pivot boss disc — real hardware on the joint axis (origin honesty +
    # cross-part capture), fills the pivot hole from the plate's inner face.
    part.visual(
        Cylinder(radius=0.015 * sc, length=BLADE_T),
        origin=Origin(xyz=(0.0, 0.0, z_plate)),
        material=pal["blade"],
        name="pivot_boss", material_class_id=("metal.blackened_gunmetal" if r.palette_theme in {"blued_black_brass", "chrome_red", "gold_ivory"} else "metal.brushed_silver"),
    )
    if sign > 0:
        # Screw head + shank captured through both blades (parent-side hardware).
        part.visual(
            Cylinder(radius=0.0165 * sc, length=0.0050),
            origin=Origin(xyz=(0.0, 0.0, plate_top + 0.0035)),
            material=pal["screw"],
            name="screw_head", material_class_id=("metal.brass_polished" if r.palette_theme in {"brushed_steel_black", "blued_black_brass", "gold_ivory"} else "metal.chrome_polished"),
        )
        part.visual(
            Cylinder(radius=0.0050 * sc, length=0.0130),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=pal["screw"],
            name="screw_shank", material_class_id=("metal.brass_polished" if r.palette_theme in {"brushed_steel_black", "blued_black_brass", "gold_ivory"} else "metal.chrome_polished"),
        )
        part.visual(
            Box((0.020 * sc, 0.0028, 0.0009)),
            origin=Origin(xyz=(0.0, 0.0, plate_top + 0.0059), rpy=(0.0, 0.0, -0.38)),
            material=pal["slot"],
            name="screw_slot", material_class_id="metal.blackened_gunmetal",
        )


# --------------------------------------------------------------------------- #
# Handle builders (add tang + grip visuals onto an existing shear part)
# --------------------------------------------------------------------------- #
def _neck_quad(x0, y0a, y0b, x1, y1a, y1b):
    return [(x0, y0a), (x0, y0b), (x1, y1b), (x1, y1a)]


def _build_handle(part, sign: int, r: ResolvedFabricScissorsConfig, pal) -> None:
    sc = r.size_scale
    ls = r.loop_scale
    z_loop = UPPER_LOOP_Z if sign > 0 else LOWER_LOOP_Z
    s = 1.0 if sign > 0 else -1.0

    if r.handle_style == "offset_asymmetric_bent":
        if sign > 0:
            neck = _neck_quad(0.010, 0.014, -0.006, 0.095, 0.040, 0.012)
            loop_c = (0.120 * sc, 0.036 * sc)
            outer = (0.075 * sc * ls, 0.058 * sc * ls)
            inner = (0.050 * sc * ls, 0.036 * sc * ls)
        else:
            neck = _neck_quad(0.010, -0.014, 0.006, 0.100, -0.046, -0.014)
            loop_c = (0.128 * sc, -0.055 * sc)
            outer = (0.100 * sc * ls, 0.066 * sc * ls)
            inner = (0.074 * sc * ls, 0.044 * sc * ls)
        neck = _scale(neck, sc)
    elif r.handle_style == "symmetric_inline_bows":
        neck = _scale(_neck_quad(0.010, 0.009 * s, -0.009 * s, 0.100, 0.009 * s, -0.009 * s), sc)
        loop_c = (0.126 * sc, 0.0)
        outer = (0.076 * sc * ls, 0.076 * sc * ls)
        inner = (0.050 * sc * ls, 0.050 * sc * ls)
    else:  # spring_squeeze_yoke — handled separately below
        _build_yoke(part, sign, r, pal)
        return

    part.visual(
        mesh_from_geometry(ExtrudeGeometry(neck, HANDLE_T, center=True), f"{part.name}_neck"),
        origin=Origin(xyz=(0.0, 0.0, z_loop)),
        material=pal["handle"],
        name="handle_neck", material_class_id=("plastic.opaque_generic" if r.palette_theme in {"brushed_steel_black", "blued_black_brass", "gold_ivory"} else "plastic.opaque_glossy_molded"),
    )
    exp = 2.0 if r.handle_style == "symmetric_inline_bows" else 2.3
    ring = _ring_geometry(
        _oval_profile(outer[0], outer[1], center=loop_c, exponent=exp, segments=44),
        _oval_profile(inner[0], inner[1], center=loop_c, exponent=exp, segments=44),
        HANDLE_T,
    )
    part.visual(
        mesh_from_geometry(ring, f"{part.name}_loop"),
        origin=Origin(xyz=(0.0, 0.0, z_loop)),
        material=pal["handle"],
        name="handle_loop", material_class_id=("plastic.opaque_generic" if r.palette_theme in {"brushed_steel_black", "blued_black_brass", "gold_ivory"} else "plastic.opaque_glossy_molded"),
    )


# Leaf-spring yoke half profiles (spring_snips fork), in the upper frame.
_YOKE_UPPER = [
    (0.070, 0.0205),
    (0.090, 0.0250),
    (0.112, 0.0245),
    (0.132, 0.0165),
    (0.148, 0.0035),
    (0.158, -0.0110),
    (0.155, -0.0110),
    (0.146, 0.0020),
    (0.128, 0.0130),
    (0.106, 0.0210),
    (0.088, 0.0210),
    (0.070, 0.0165),
]


def _build_yoke(part, sign: int, r: ResolvedFabricScissorsConfig, pal) -> None:
    sc = r.size_scale
    prof = _oriented(_YOKE_UPPER, sign, sc)
    part.visual(
        mesh_from_geometry(ExtrudeGeometry(prof, HANDLE_T + 0.005, center=True), f"{part.name}_yoke"),
        origin=Origin(xyz=(0.0, 0.0, YOKE_Z)),
        material=pal["yoke"],
        name="spring_yoke", material_class_id="metal.steel_bare",
    )
    # Tang connector: blade pivot shoulder -> yoke start. Offset per arm in z so
    # the two tangs (which both cross the blade axis near the pivot) never share
    # the same z plane; each still overlaps its own blade plate AND the yoke.
    tang_z = 0.004 * (1.0 if sign > 0 else -1.0)
    if sign > 0:
        neck = _neck_quad(0.010, 0.016, -0.002, 0.078, 0.028, 0.014)
    else:
        neck = _neck_quad(0.010, -0.016, 0.002, 0.078, -0.028, -0.014)
    part.visual(
        mesh_from_geometry(ExtrudeGeometry(_scale(neck, sc), HANDLE_T, center=True), f"{part.name}_ytang"),
        origin=Origin(xyz=(0.0, 0.0, tang_z)),
        material=pal["yoke"],
        name="yoke_tang", material_class_id="metal.steel_bare",
    )
    rivet_y = 0.020 if sign > 0 else -0.020  # on the yoke start (mirror-symmetric)
    part.visual(
        Cylinder(radius=0.004 * sc, length=0.011),
        origin=Origin(xyz=(0.074 * sc, rivet_y * sc, tang_z * 0.5)),
        material=pal["screw"],
        name="yoke_rivet", material_class_id=("metal.brass_polished" if r.palette_theme in {"brushed_steel_black", "blued_black_brass", "gold_ivory"} else "metal.chrome_polished"),
    )


# --------------------------------------------------------------------------- #
# Public build
# --------------------------------------------------------------------------- #
def build_fabric_scissors(
    config: FabricScissorsConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or FabricScissorsConfig()
    r = resolve_config(config)
    pal = _palette(r.palette_theme)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Textiles_Fabric / Fabric scissors"},
    )
    mats = {k: model.material(f"fs_{k}_{r.palette_theme}", rgba=v) for k, v in pal.items()}

    upper = model.part("upper_shear")
    _build_blade(upper, +1, r, mats)
    _build_handle(upper, +1, r, mats)
    upper.inertial = Inertial.from_geometry(
        Box((0.30 * r.size_scale, 0.10 * r.size_scale, BLADE_T)),
        mass=0.045,
        origin=Origin(xyz=(-0.06 * r.size_scale, 0.02 * r.size_scale, UPPER_Z)),
    )

    lower = model.part("lower_shear")
    _build_blade(lower, -1, r, mats)
    _build_handle(lower, -1, r, mats)
    lower.inertial = Inertial.from_geometry(
        Box((0.30 * r.size_scale, 0.12 * r.size_scale, BLADE_T)),
        mass=0.050,
        origin=Origin(xyz=(-0.06 * r.size_scale, -0.02 * r.size_scale, LOWER_Z)),
    )

    # The single pivot screw: captured pin through both blade bores. Grandfathered
    # (no MatingContract) per Rule 2 — the mating surfaces are two crossed plates
    # with a thin z clearance, not two axis-aligned contact faces; capture is
    # verified by element-scoped allow_overlap + expect_overlap in run_tests.
    model.articulation(
        "pivot_screw",
        ArticulationType.REVOLUTE,
        parent=upper,
        child=lower,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(lower=r.pivot_lower, upper=r.pivot_upper, effort=3.0, velocity=2.5),
        meta={"role": "pivot_screw", "opens": "positive"},
    )
    return model


def build_seeded_fabric_scissors(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_fabric_scissors(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def _center_y(aabb):
    return (aabb[0][1] + aabb[1][1]) / 2.0 if aabb else None


def run_fabric_scissors_tests(model: ArticulatedObject, config: FabricScissorsConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    upper = model.get_part("upper_shear")
    lower = model.get_part("lower_shear")
    pivot = model.get_articulation("pivot_screw")
    up_names = {v.name for v in upper.visuals}
    lo_names = {v.name for v in lower.visuals}

    # Captured pivot screw: the parent-side screw shank / boss are retained
    # through the child blade bore (intentional pin-through overlap). Declared
    # BEFORE any overlap check so both the in-line and sampled-pose gates honor it.
    ctx.allow_overlap(
        upper, lower,
        elem_a="screw_shank", elem_b="blade_plate",
        reason="Pivot screw shank is captured through the lower blade bore.",
    )
    ctx.allow_overlap(
        upper, lower,
        elem_a="screw_shank", elem_b="pivot_boss",
        reason="Pivot screw shank passes through the lower pivot boss.",
    )
    ctx.allow_overlap(
        upper, lower,
        elem_a="pivot_boss", elem_b="pivot_boss",
        reason="Upper and lower pivot bosses stack around the screw axis.",
    )
    if r.handle_style == "spring_squeeze_yoke":
        ctx.allow_overlap(
            upper, lower,
            elem_a="spring_yoke", elem_b="spring_yoke",
            reason="The two leaf-spring yoke halves meet at the bend apex (continuous U spring).",
        )

    # Baseline (deduped against the compiler-owned baseline).
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # --- Identity: two crossed blades on ONE pivot revolute. ---
    ctx.check(
        "single pivot revolute joins two blade parts",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(v, 6) for v in pivot.axis) == (0.0, 0.0, 1.0)
        and len([j for j in model.articulations if j.articulation_type != ArticulationType.FIXED]) == 1,
        details=f"type={pivot.articulation_type}, axis={pivot.axis}",
    )
    ctx.expect_overlap(
        upper, lower, axes="xy", elem_a="blade_plate", elem_b="blade_plate",
        min_overlap=0.020, name="blade plates cross in plan at the screw",
    )
    # Thin z clearance between the stacked plates. Curved blades warp each plate's
    # AABB up by the arc rise so the two AABBs overlap in z even though at every x
    # the plates stay ~2mm apart (verified for all forms by the sampled-pose gate);
    # the AABB gap check only applies to the flat forms.
    if r.body_style != "curved":
        ctx.expect_gap(
            upper, lower, axis="z", positive_elem="blade_plate", negative_elem="blade_plate",
            min_gap=0.0005, max_gap=0.004, name="stacked blades keep a thin pivot clearance",
        )

    # --- Blade length reads as hand-held tailor shears. ---
    up_blade = ctx.part_element_world_aabb(upper, elem="blade_plate")
    ctx.check(
        "blade spans a tailoring cutting length",
        up_blade is not None and (up_blade[1][0] - up_blade[0][0]) > 0.14 * r.size_scale,
        details=f"upper blade aabb={up_blade}",
    )

    # --- ③ form-family specific identity. ---
    if r.body_style == "duckbill":
        lo = ctx.part_element_world_aabb(lower, elem="blade_plate")
        up = ctx.part_element_world_aabb(upper, elem="blade_plate")
        if lo and up:
            ctx.check(
                "lower blade is a broad duckbill paddle wider than the pointed upper",
                (lo[1][1] - lo[0][1]) > 0.046 * r.size_scale
                and (lo[1][1] - lo[0][1]) > (up[1][1] - up[0][1]) + 0.004 * r.size_scale,
                details=f"lower_y={lo[1][1]-lo[0][1]:.4f}, upper_y={up[1][1]-up[0][1]:.4f}",
            )
    if r.body_style == "curved":
        lo = ctx.part_element_world_aabb(lower, elem="blade_plate")
        ctx.check(
            "curved blade tip lifts out of the handle plane",
            lo is not None and (lo[1][2] - lo[0][2]) > 0.006,
            details=f"lower blade z-extent={None if not lo else lo[1][2]-lo[0][2]:.4f}",
        )

    # --- ③ edge multiplicity: meshing tooth rows. ---
    up_teeth = [v.name for v in upper.visuals if v.name.startswith("edge_tooth_")]
    lo_teeth = [v.name for v in lower.visuals if v.name.startswith("edge_tooth_")]
    if r.edge_style in ("pinking", "scallop"):
        ctx.check(
            f"{r.edge_style} tooth rows loop-emitted on both blades (N={r.n_edge_teeth})",
            len(up_teeth) >= r.n_edge_teeth - 1 and len(lo_teeth) >= r.n_edge_teeth - 1,
            details=f"upper teeth={len(up_teeth)}, lower teeth={len(lo_teeth)}, N={r.n_edge_teeth}",
        )
    elif r.edge_style == "serrated":
        ctx.check(
            "micro serrations on the lower blade only",
            len(lo_teeth) >= SERR_COUNT - 1 and len(up_teeth) == 0,
            details=f"lower serr={len(lo_teeth)}, upper serr={len(up_teeth)}",
        )
    else:
        ctx.check(
            "honed smooth edge carries no cutting teeth",
            len(up_teeth) == 0 and len(lo_teeth) == 0,
            details=f"upper teeth={len(up_teeth)}, lower teeth={len(lo_teeth)}",
        )

    # --- ② handle topology specific identity. ---
    if r.handle_style == "offset_asymmetric_bent":
        ul = ctx.part_element_world_aabb(upper, elem="handle_loop")
        ll = ctx.part_element_world_aabb(lower, elem="handle_loop")
        if ul and ll:
            ctx.check(
                "asymmetric grip: large finger loop bigger than the small thumb loop",
                (ll[1][0] - ll[0][0]) > (ul[1][0] - ul[0][0]) + 0.012 * r.size_scale,
                details=f"lower loop w={ll[1][0]-ll[0][0]:.3f}, upper loop w={ul[1][0]-ul[0][0]:.3f}",
            )
    elif r.handle_style == "symmetric_inline_bows":
        ctx.expect_overlap(
            upper, lower, axes="xy", elem_a="handle_loop", elem_b="handle_loop",
            min_overlap=0.025, name="symmetric inline bows share the same footprint on the blade axis",
        )
    else:  # spring_squeeze_yoke
        ctx.check(
            "spring squeeze yoke present on both shears (no finger loops)",
            "spring_yoke" in up_names and "spring_yoke" in lo_names
            and "handle_loop" not in up_names and "handle_loop" not in lo_names,
            details=f"upper={sorted(up_names)}",
        )
        ctx.check(
            "spring yoke revolute rests open on a non-negative squeeze range",
            pivot.motion_limits.lower == 0.0 and pivot.motion_limits.upper > 0.0,
            details=f"limits=({pivot.motion_limits.lower}, {pivot.motion_limits.upper})",
        )

    # --- Rule 5: full-travel clearance + a targeted opening pose. ---
    lower_lim = pivot.motion_limits.lower
    upper_lim = pivot.motion_limits.upper
    with ctx.pose({pivot: lower_lim}):
        closed_up = ctx.part_element_world_aabb(upper, elem="blade_plate")
        closed_lo = ctx.part_element_world_aabb(lower, elem="blade_plate")
        closed_span = (
            abs(_center_y(closed_up) - _center_y(closed_lo)) if closed_up and closed_lo else None
        )
    with ctx.pose({pivot: upper_lim}):
        open_up = ctx.part_element_world_aabb(upper, elem="blade_plate")
        open_lo = ctx.part_element_world_aabb(lower, elem="blade_plate")
        open_span = abs(_center_y(open_up) - _center_y(open_lo)) if open_up and open_lo else None
    ctx.check(
        "pivot opens the blades (shear line separates)",
        closed_span is not None and open_span is not None and open_span > closed_span + 0.018,
        details=f"closed_span={closed_span}, open_span={open_span}",
    )

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


object_model = build_fabric_scissors()


__all__ = [
    "BladeForm",
    "HandleStyle",
    "PaletteTheme",
    "FabricScissorsConfig",
    "ResolvedFabricScissorsConfig",
    "build_fabric_scissors",
    "build_seeded_fabric_scissors",
    "config_from_seed",
    "resolve_config",
    "run_fabric_scissors_tests",
    "slot_choices_for_seed",
]
