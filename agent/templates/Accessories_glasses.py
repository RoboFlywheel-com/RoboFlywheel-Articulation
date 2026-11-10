# SPDX-License-Identifier: Apache-2.0

"""Glasses / eyewear modular procedural template.

Modular slot graph (pattern = parallel_children):

    front_frame  (root part — rim/brow visuals + bridge + nose + 2 hinge mounts)
        ├── lens_right / lens_left          FIXED children  (or 1 shield visual)
        ├── [Slot B bridge / nose detail]   visuals on front_frame
        ├── temple_right                    REVOLUTE fold  (axis ±Z, 0..fold_range)
        └── temple_left                     REVOLUTE fold  (axis ±Z, 0..fold_range)

    (Slot C = spring_hinges inserts a flex_link_{side} intermediate part:
        front_frame -[REVOLUTE spring_{side}]-> flex_link_{side}
        flex_link_{side} -[REVOLUTE fold_{side}]-> temple_{side}     → 4 revolute)

Slots (spec articraft_template_authoring/specs_modular_v1/Accessories_Accessories_glasses.md):
  A  front_shape : rectangular_clear_rims / sport_front_frame / cat_eye_frame /
                   round_wire_rims / wraparound_shield / hexagonal_lenses /
                   oval_panto_lenses                                     (7)
  B  bridge_style: standard_bridge / keyhole_bridge                     (2)
  C  temple_style: folding_temples / spring_hinges / thick_sport_temples (3)
  palette_style  : clear_acetate / tortoise / matte_black / smoky_tint /
                   amber_tint / silver_metal                            (6 colorways)

Compatibility gate: wraparound_shield (Slot A) has no inter-rim gap, so it
forces Slot B to an internal nose-support form (no separate per-eye rims, no
keyhole saddle). clear↔tint is carried by palette_style, NOT a slot.

ALL geometry is unified on ONE coordinate convention (spec-recommended
lineage B, geometry-primitive):
    +X = wearer's right (image right)   +Y = forward (lenses face +Y)   +Z = up
The front frame sits in the XZ plane near Y=0; temple arms run back (-Y).
Lineage-A cadquery sources (browline brow, keyhole bridge, hex/panto outlines,
spring barrel/flex link) are re-authored here as geometry-primitive
outlines/extrudes/tubes in this frame (AUTHORING.md §A Rule 3: keep mesh
geometry, never downgrade to crude Box/Cylinder placeholders).

Per-module 5★ sources (see spec Module Source Index S1..S12):
  S1  rectangular_clear_rims  parent A (aviator 211959)  L48-L115
  S2  sport_front_frame       parent B (clubmaster 209562) L56-L183
  S3  cat_eye_frame           rec_glasses_var_cat_eye_frame L52-L98
  S4  round_wire_rims         rec_glasses_var_round_wire_rims L65-L103
  S5  wraparound_shield       rec_glasses_var_wraparound_shield L75-L403
  S6  hexagonal_lenses        rec_glasses_var_qwen_hexagonal_lenses L56-L106
  S7  oval_panto_lenses       rec_glasses_var_qwen_oval_panto_lenses L56-L111
  S8  standard_bridge         parents A+B
  S9  keyhole_bridge          rec_glasses_var_keyhole_bridge L178-L257
  S10 folding_temples         parent B  L218-L394
  S11 spring_hinges           rec_glasses_var_spring_hinges L184-L517
  S12 thick_sport_temples     rec_glasses_var_thick_sport_temples L191-L268
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
    BoxGeometry,
    CylinderGeometry,
    Inertial,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True

FrontShape = Literal[
    "rectangular_clear_rims",
    "sport_front_frame",
    "cat_eye_frame",
    "round_wire_rims",
    "wraparound_shield",
    "hexagonal_lenses",
    "oval_panto_lenses",
]
BridgeStyle = Literal["standard_bridge", "keyhole_bridge"]
TempleStyle = Literal["folding_temples", "spring_hinges", "thick_sport_temples"]
PaletteStyle = Literal[
    "clear_acetate",
    "tortoise",
    "matte_black",
    "smoky_tint",
    "amber_tint",
    "silver_metal",
]

FRONT_SHAPES: tuple[FrontShape, ...] = (
    "rectangular_clear_rims",
    "sport_front_frame",
    "cat_eye_frame",
    "round_wire_rims",
    "wraparound_shield",
    "hexagonal_lenses",
    "oval_panto_lenses",
)
BRIDGE_STYLES: tuple[BridgeStyle, ...] = ("standard_bridge", "keyhole_bridge")
TEMPLE_STYLES: tuple[TempleStyle, ...] = (
    "folding_temples",
    "spring_hinges",
    "thick_sport_temples",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_acetate",
    "tortoise",
    "matte_black",
    "smoky_tint",
    "amber_tint",
    "silver_metal",
)

# Front shapes whose lens outline is a *full* (closed-loop) per-eye rim.
_OUTLINE_SHAPES = {
    "rectangular_clear_rims",
    "sport_front_frame",
    "cat_eye_frame",
    "hexagonal_lenses",
    "oval_panto_lenses",
}

SIDES: tuple[tuple[str, float], ...] = (("right", 1.0), ("left", -1.0))

FRAME_Y = 0.0  # lens / frame plane

# --------------------------------------------------------------------------- #
# Palette colorways (≥3 required; 6 observed across the 10 sources).
# Every key resolved here is consumed by a `.visual(material=...)` call.
# --------------------------------------------------------------------------- #
# token roles:
#   frame  : rim / brow / temple metal-or-acetate
#   rim    : per-eye rim wire / lower rim / bezel highlight
#   lens   : translucent lens fill (alpha < 1 except clear which is very low)
#   tip    : ear-tip acetate / rubber
#   accent : hinge blocks / bridge struts / nose pads
PALETTE_PRESETS: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "clear_acetate": {
        "frame": (0.86, 0.87, 0.90, 1.0),
        "rim": (0.78, 0.80, 0.84, 1.0),
        "lens": (0.80, 0.83, 0.88, 0.28),
        "tip": (0.70, 0.72, 0.76, 1.0),
        "accent": (0.74, 0.76, 0.80, 1.0),
    },
    "tortoise": {
        "frame": (0.36, 0.21, 0.09, 1.0),
        "rim": (0.30, 0.17, 0.07, 1.0),
        "lens": (0.55, 0.36, 0.16, 0.50),
        "tip": (0.24, 0.14, 0.06, 1.0),
        "accent": (0.62, 0.46, 0.26, 1.0),
    },
    "matte_black": {
        "frame": (0.10, 0.10, 0.12, 1.0),
        "rim": (0.08, 0.08, 0.10, 1.0),
        "lens": (0.07, 0.07, 0.09, 0.52),
        "tip": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.18, 0.18, 0.20, 1.0),
    },
    "smoky_tint": {
        "frame": (0.16, 0.17, 0.19, 1.0),
        "rim": (0.62, 0.64, 0.66, 1.0),
        "lens": (0.10, 0.11, 0.13, 0.55),
        "tip": (0.08, 0.08, 0.10, 1.0),
        "accent": (0.62, 0.64, 0.66, 1.0),
    },
    "amber_tint": {
        "frame": (0.82, 0.84, 0.87, 1.0),
        "rim": (0.82, 0.84, 0.87, 1.0),
        "lens": (0.42, 0.16, 0.03, 0.62),
        "tip": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.06, 0.06, 0.07, 1.0),
    },
    "silver_metal": {
        "frame": (0.80, 0.82, 0.85, 1.0),
        "rim": (0.86, 0.88, 0.90, 1.0),
        "lens": (0.70, 0.72, 0.76, 0.45),
        "tip": (0.30, 0.31, 0.33, 1.0),
        "accent": (0.88, 0.90, 0.92, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class GlassesConfig:
    front_shape: FrontShape = "rectangular_clear_rims"
    bridge_style: BridgeStyle = "standard_bridge"
    temple_style: TempleStyle = "folding_temples"
    palette_style: PaletteStyle = "smoky_tint"

    lens_half_w: float = 0.0265
    lens_aspect: float = 0.90  # lens_half_h = lens_half_w * lens_aspect
    lens_gap: float = 0.018
    temple_len: float = 0.127
    fold_range_deg: float = 95.0
    spring_range_deg: float = 20.0


@dataclass(frozen=True)
class ResolvedGlassesConfig:
    front_shape: FrontShape
    bridge_style: BridgeStyle
    temple_style: TempleStyle
    palette_style: PaletteStyle

    lens_half_w: float
    lens_half_h: float
    lens_gap: float
    rim_center_x: float
    temple_len: float
    fold_range: float  # radians
    spring_range: float  # radians
    hinge_x: float  # |X| of each hinge mount (outer-top rim corner)
    hinge_z: float  # Z of hinge mount
    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> GlassesConfig:
    """Deterministic weighted procedural draw over (front, bridge, temple,
    palette) + continuous scales. seed=0 is NOT special."""
    rng = random.Random(seed)

    # front_shape ~uniform; wraparound slightly downweighted (constrains B).
    front_weights = {
        "rectangular_clear_rims": 1.0,
        "sport_front_frame": 1.0,
        "cat_eye_frame": 1.0,
        "round_wire_rims": 1.0,
        "wraparound_shield": 0.6,
        "hexagonal_lenses": 1.0,
        "oval_panto_lenses": 1.0,
    }
    front_shape = _weighted_choice(rng, front_weights)

    # temple_style: favour the common plain fold; spring is the rare 4-joint path.
    temple_weights = {
        "folding_temples": 1.0,
        "spring_hinges": 0.7,
        "thick_sport_temples": 0.9,
    }
    temple_style = _weighted_choice(rng, temple_weights)

    # bridge_style: favour standard; keyhole rarer.  (Legalized for shield below.)
    bridge_weights = {"standard_bridge": 1.0, "keyhole_bridge": 0.7}
    bridge_style = _weighted_choice(rng, bridge_weights)

    palette_style = rng.choice(PALETTE_STYLES)

    lens_half_w = round(rng.uniform(0.024, 0.030), 5)
    # round_wire forces a circular lens (aspect = 1.0); others 0.82..1.0.
    lens_aspect = 1.0 if front_shape == "round_wire_rims" else round(rng.uniform(0.82, 1.0), 4)
    lens_gap = round(rng.uniform(0.014, 0.022), 5)
    temple_len = round(rng.uniform(0.115, 0.140), 5)
    fold_range_deg = round(rng.uniform(85.0, 100.0), 2)
    spring_range_deg = round(rng.uniform(12.0, 25.0), 2)

    return GlassesConfig(
        front_shape=front_shape,
        bridge_style=bridge_style,
        temple_style=temple_style,
        palette_style=palette_style,
        lens_half_w=lens_half_w,
        lens_aspect=lens_aspect,
        lens_gap=lens_gap,
        temple_len=temple_len,
        fold_range_deg=fold_range_deg,
        spring_range_deg=spring_range_deg,
    )


def _weighted_choice(rng: random.Random, weights: dict) -> str:
    keys = list(weights.keys())
    ws = [weights[k] for k in keys]
    return rng.choices(keys, weights=ws, k=1)[0]


def _legalize(front_shape: str, bridge_style: str) -> str:
    """Compatibility matrix: wraparound_shield (one continuous shield, no rim
    gap) forces Slot B to the internal nose-support form. We model that by
    pinning bridge_style to 'standard_bridge' (which degrades to internal nose
    support when shield is active — no inter-rim bar, just nose pads)."""
    if front_shape == "wraparound_shield":
        return "standard_bridge"
    return bridge_style


def resolve_config(config: GlassesConfig) -> ResolvedGlassesConfig:
    if str(config.front_shape) not in FRONT_SHAPES:
        raise ValueError(f"Unsupported front_shape: {config.front_shape}")
    if str(config.temple_style) not in TEMPLE_STYLES:
        raise ValueError(f"Unsupported temple_style: {config.temple_style}")
    if str(config.palette_style) not in PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    front_shape = str(config.front_shape)
    bridge_style = _legalize(front_shape, str(config.bridge_style))
    if bridge_style not in BRIDGE_STYLES:
        raise ValueError(f"Unsupported bridge_style: {bridge_style}")

    lens_half_w = max(0.024, min(float(config.lens_half_w), 0.030))
    aspect = 1.0 if front_shape == "round_wire_rims" else max(0.82, min(float(config.lens_aspect), 1.0))
    lens_half_h = lens_half_w * aspect
    lens_gap = max(0.014, min(float(config.lens_gap), 0.022))
    rim_center_x = lens_half_w + lens_gap / 2.0
    temple_len = max(0.115, min(float(config.temple_len), 0.140))
    fold_range = math.radians(max(85.0, min(float(config.fold_range_deg), 100.0)))
    spring_range = math.radians(max(12.0, min(float(config.spring_range_deg), 25.0)))

    # Hinge mount at the outer-top rim corner.
    hinge_x = rim_center_x + lens_half_w - 0.001
    hinge_z = lens_half_h - 0.006

    return ResolvedGlassesConfig(
        front_shape=front_shape,  # type: ignore[arg-type]
        bridge_style=bridge_style,  # type: ignore[arg-type]
        temple_style=str(config.temple_style),  # type: ignore[arg-type]
        palette_style=str(config.palette_style),  # type: ignore[arg-type]
        lens_half_w=lens_half_w,
        lens_half_h=lens_half_h,
        lens_gap=lens_gap,
        rim_center_x=rim_center_x,
        temple_len=temple_len,
        fold_range=fold_range,
        spring_range=spring_range,
        hinge_x=hinge_x,
        hinge_z=hinge_z,
        palette=dict(PALETTE_PRESETS[str(config.palette_style)]),
    )


# --------------------------------------------------------------------------- #
# Slot A — lens outline helpers (shared by lens geometry AND matching rim path)
# --------------------------------------------------------------------------- #
def _rounded_square_loop(half_w, half_h, corner, n_corner=7):
    """Closed (x,z) loop of a rounded square, centered at origin, CCW.
    Adapted from parent A L48-L65."""
    pts = []
    cx = max(half_w - corner, 1e-4)
    cz = max(half_h - corner, 1e-4)
    corners = [
        (cx, cz, 0.0),
        (-cx, cz, math.pi / 2),
        (-cx, -cz, math.pi),
        (cx, -cz, 3 * math.pi / 2),
    ]
    for ccx, ccz, base in corners:
        for i in range(n_corner + 1):
            a = base + (math.pi / 2) * (i / n_corner)
            pts.append((ccx + corner * math.cos(a), ccz + corner * math.sin(a)))
    return pts


def _cateye_loop(sx, half_w, half_h, n=44):
    """Cat-eye outline with upswept outer-upper corner.  sx=+1 right, -1 left.
    Adapted from cat_eye_frame L52-L98."""
    peak_angle = math.radians(58.0)
    peak_width = math.radians(26.0)
    upsweep = half_h * 0.42
    pts = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        x = half_w * math.cos(t)
        z = half_h * math.sin(t)
        if 0.0 < t < math.pi:
            angle_from_outer = t if sx > 0 else (math.pi - t)
        else:
            angle_from_outer = math.pi * 10.0
        if angle_from_outer < math.pi:
            dist = abs(angle_from_outer - peak_angle)
            bump = math.exp(-0.5 * (dist / peak_width) ** 2)
            z += upsweep * bump
            x += sx * 0.003 * bump
        if math.sin(t) < -0.5:
            flat = (-math.sin(t) - 0.5) / 0.5
            z *= 1.0 - 0.05 * flat
        pts.append((x, z))
    return pts


def _hex_loop(sx, half_w, half_h):
    """Hexagonal outline.  Adapted from hexagonal_lenses L56-L66.
    Source authors in (Y,Z); here we map to per-eye (x,z) with x = outer dir."""
    hw, hh = half_w, half_h
    # mirror about x so the angled corners stay symmetric per side
    base = [
        (-hw * 0.65, hh),
        (hw * 0.65, hh),
        (hw, hh * 0.15),
        (hw * 0.75, -hh),
        (-hw * 0.75, -hh),
        (-hw, hh * 0.15),
    ]
    return [(sx * x, z) for (x, z) in base]


def _panto_loop(sx, half_w, half_h, segments=44):
    """Soft oval panto outline (fuller lower curve).
    Adapted from oval_panto_lenses L56-L75."""
    hw, hh = half_w, half_h
    pts = []
    for i in range(segments):
        a = 2.0 * math.pi * i / segments
        sin_a = math.sin(a)
        cos_a = math.cos(a)
        ry, rz = hw, hh
        if sin_a < 0.0:
            t = abs(sin_a)
            ry *= 1.0 + 0.06 * t
            rz *= 1.0 + 0.08 * t
        else:
            t = sin_a
            ry *= 1.0 - 0.04 * t
            rz *= 1.0 - 0.06 * t
        pts.append((sx * ry * cos_a, rz * sin_a))
    return pts


def _circle_loop(half_w, half_h, n=40):
    r = (half_w + half_h) * 0.5
    return [(r * math.cos(2.0 * math.pi * i / n), r * math.sin(2.0 * math.pi * i / n)) for i in range(n)]


def _lens_outline(front_shape, sx, half_w, half_h):
    """Per-eye (x,z) closed outline used by BOTH the lens geometry and the rim
    path (every Slot A source does exactly this)."""
    if front_shape == "cat_eye_frame":
        return _cateye_loop(sx, half_w, half_h)
    if front_shape == "hexagonal_lenses":
        return _hex_loop(sx, half_w, half_h)
    if front_shape == "oval_panto_lenses":
        return _panto_loop(sx, half_w, half_h)
    if front_shape == "round_wire_rims":
        return _circle_loop(half_w, half_h)
    # rectangular_clear_rims / sport_front_frame
    corner = min(half_w, half_h) * 0.34
    return _rounded_square_loop(half_w, half_h, corner)


def _lower_outline_arc(loop, z_cut):
    """Return the contiguous lower portion of a closed (x,z) outline: every
    point with z <= z_cut, ordered along the perimeter from one upper end around
    the bottom to the other. Used so the browline lower rim traces the lens
    outline EXACTLY (the lens edge sits inside the rim and never pokes past it).
    """
    n = len(loop)
    below = [loop[i][1] <= z_cut for i in range(n)]
    if all(below) or not any(below):
        return list(loop)
    # start at a below-point whose predecessor is above (one upper end of the arc)
    start = next(i for i in range(n) if below[i] and not below[(i - 1) % n])
    arc = []
    i = start
    while below[i % n] and len(arc) <= n:
        arc.append(loop[i % n])
        i += 1
    return arc


def _lens_geometry(loop, cx, dome=0.0024, back=-0.0010) -> MeshGeometry:
    """Slightly domed translucent lens filling an (x,z) outline at center cx.
    Adapted from parent A L303-L327."""
    g = MeshGeometry()
    ring_f, ring_b = [], []
    for (x, z) in loop:
        ring_f.append(g.add_vertex(cx + x, 0.0, z))
        ring_b.append(g.add_vertex(cx + x, back, z))
    apex_f = g.add_vertex(cx, dome, 0.0)
    apex_b = g.add_vertex(cx, back, 0.0)
    n = len(loop)
    for i in range(n):
        j = (i + 1) % n
        g.add_face(ring_f[i], ring_f[j], apex_f)
        g.add_face(ring_b[j], ring_b[i], apex_b)
        g.add_face(ring_f[i], ring_b[i], ring_b[j])
        g.add_face(ring_f[i], ring_b[j], ring_f[j])
    return g


# --------------------------------------------------------------------------- #
# Slot A module builders — emit visuals onto the front_frame + return lens loops
# --------------------------------------------------------------------------- #
def _build_full_rim(front, r: ResolvedGlassesConfig, mats) -> None:
    """Per-eye continuous bent-tube rim following the lens outline (closed
    spline).  Adapted from parent A L75-L88 / outline-matched rim across
    cat_eye / hex / panto / round_wire."""
    for side, sx in SIDES:
        cx = sx * r.rim_center_x
        loop2d = _lens_outline(r.front_shape, sx, r.lens_half_w, r.lens_half_h)
        pts3d = [(cx + x, FRAME_Y, z) for (x, z) in loop2d]
        rim = tube_from_spline_points(
            pts3d, radius=0.0019, closed_spline=True,
            samples_per_segment=3, radial_segments=10,
        )
        front.visual(mesh_from_geometry(rim, f"rim_{side}"),
                     material=mats["rim"], name=f"rim_{side}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))


def _build_round_wire_rim(front, r: ResolvedGlassesConfig, mats) -> None:
    """Full circular wire rim (torus, axis = Y so it lies in the XZ plane).
    Adapted from round_wire_rims L65-L75."""
    radius = (r.lens_half_w + r.lens_half_h) * 0.5
    for side, sx in SIDES:
        cx = sx * r.rim_center_x
        rim = TorusGeometry(radius, 0.0019, radial_segments=10, tubular_segments=40)
        rim.rotate_x(math.pi / 2.0)  # axis Z -> axis Y (ring in XZ plane)
        rim.translate(cx, FRAME_Y, 0.0)
        front.visual(mesh_from_geometry(rim, f"rim_{side}"),
                     material=mats["rim"], name=f"rim_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))


def _build_brow_bar(front, r: ResolvedGlassesConfig, mats) -> None:
    """Chunky glossy browline bar spanning both eyes (a single continuous band
    across the top).  Re-authored (lineage B) from parent B L125-L165 cadquery
    brow as a geometry-primitive band tube + a heavier upper bar."""
    hw_total = r.rim_center_x + r.lens_half_w + 0.006
    z_top = r.lens_half_h - 0.002
    # eased band that thins over the bridge and grows toward the temples
    n = 28
    top_pts, bot_pts = [], []
    for i in range(n + 1):
        t = i / n
        x = -hw_total + 2.0 * hw_total * t
        frac = abs(x) / hw_total
        band_h = 0.0035 + (0.011 - 0.0035) * (frac ** 1.4)
        top_pts.append((x, FRAME_Y, z_top + band_h))
        bot_pts.append((x, FRAME_Y, z_top - 0.003))
    # build as one solid band by sweeping a tall rounded-rect profile along
    # the top centreline (keeps mesh geometry, reads as a chunky brow).
    centre_pts = [
        (-hw_total, FRAME_Y, z_top + 0.004),
        (0.0, FRAME_Y, z_top + 0.0015),
        (hw_total, FRAME_Y, z_top + 0.004),
    ]
    brow = sweep_profile_along_spline(
        centre_pts,
        profile=rounded_rect_profile(0.010, 0.013, radius=0.0028),
        samples_per_segment=12,
        up_hint=(0.0, 0.0, 1.0),
    )
    front.visual(mesh_from_geometry(brow, "brow_bar"),
                 material=mats["frame"], name="brow_bar", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))
    # thin lower half-rim wires hugging the lens bottoms (browline signature).
    # The wire MUST trace the actual lens outline (lower arc) so the lens edge
    # sits inside the rim and never pokes past it; the brow bar covers the top.
    z_cut = r.lens_half_h * 0.42  # rim climbs to ~mid-height on each side, then around
    for side, sx in SIDES:
        cx = sx * r.rim_center_x
        loop2d = _lens_outline("sport_front_frame", sx, r.lens_half_w, r.lens_half_h)
        arc = _lower_outline_arc(loop2d, z_cut)
        edge_pts = [(cx + x, FRAME_Y, z) for (x, z) in arc]
        rim = tube_from_spline_points(
            edge_pts, radius=0.0012, samples_per_segment=4, radial_segments=8,
        )
        front.visual(mesh_from_geometry(rim, f"lower_rim_{side}"),
                     material=mats["rim"], name=f"lower_rim_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))


def _shield_lens_geometry(r: ResolvedGlassesConfig) -> MeshGeometry:
    """Single continuous wraparound shield spanning both eyes, curving back at
    the edges.  Adapted from wraparound_shield L308-L403."""
    g = MeshGeometry()
    # Span both eyes out toward (but not far past) the hinge corners. The thin
    # shield edge overlaps the captured temple knuckle at the hinge — that is
    # the wraparound hinge interface and is declared as an allowed overlap in
    # run_glasses_tests. Asserted > 0.10 m total width by the spec.
    total_half_w = r.rim_center_x + r.lens_half_w + 0.002
    half_h = r.lens_half_h + 0.003
    n_x, n_z = 24, 12
    wrap_depth = 0.004
    front_v, back_v = {}, {}
    for iz in range(n_z + 1):
        z = -half_h + (iz / n_z) * 2 * half_h
        for ix in range(n_x + 1):
            x = -total_half_w + (ix / n_x) * 2 * total_half_w
            edge = (abs(x) / total_half_w) ** 2
            y_front = 0.001 - wrap_depth * edge
            y_back = y_front - 0.0018
            dome = 0.002 * (1.0 - edge) * (1.0 - abs(z) / half_h * 0.3)
            y_front += dome
            front_v[(ix, iz)] = g.add_vertex(x, y_front, z)
            back_v[(ix, iz)] = g.add_vertex(x, y_back, z)
    for iz in range(n_z):
        for ix in range(n_x):
            f00, f10 = front_v[(ix, iz)], front_v[(ix + 1, iz)]
            f01, f11 = front_v[(ix, iz + 1)], front_v[(ix + 1, iz + 1)]
            b00, b10 = back_v[(ix, iz)], back_v[(ix + 1, iz)]
            b01, b11 = back_v[(ix, iz + 1)], back_v[(ix + 1, iz + 1)]
            g.add_face(f00, f10, f11)
            g.add_face(f00, f11, f01)
            g.add_face(b00, b11, b10)
            g.add_face(b00, b01, b11)
    for ix in range(n_x):  # bottom + top rims
        f0, f1 = front_v[(ix, 0)], front_v[(ix + 1, 0)]
        b0, b1 = back_v[(ix, 0)], back_v[(ix + 1, 0)]
        g.add_face(f0, b0, b1)
        g.add_face(f0, b1, f1)
        tf0, tf1 = front_v[(ix, n_z)], front_v[(ix + 1, n_z)]
        tb0, tb1 = back_v[(ix, n_z)], back_v[(ix + 1, n_z)]
        g.add_face(tf0, tf1, tb1)
        g.add_face(tf0, tb1, tb0)
    for iz in range(n_z):  # left + right rims
        f0, f1 = front_v[(0, iz)], front_v[(0, iz + 1)]
        b0, b1 = back_v[(0, iz)], back_v[(0, iz + 1)]
        g.add_face(f0, f1, b1)
        g.add_face(f0, b1, b0)
        rf0, rf1 = front_v[(n_x, iz)], front_v[(n_x, iz + 1)]
        rb0, rb1 = back_v[(n_x, iz)], back_v[(n_x, iz + 1)]
        g.add_face(rf0, rb0, rb1)
        g.add_face(rf0, rb1, rf1)
    return g


def _build_shield_brow(front, r: ResolvedGlassesConfig, mats) -> None:
    """Shallow brow bar across the top of the shield.  Adapted from
    wraparound_shield L80-L92."""
    brow_span = (r.rim_center_x + r.lens_half_w) * 2.0 + 0.006
    brow_pts = [
        (-brow_span / 2, FRAME_Y, r.lens_half_h + 0.003),
        (0.0, FRAME_Y, r.lens_half_h + 0.004),
        (brow_span / 2, FRAME_Y, r.lens_half_h + 0.003),
    ]
    brow = tube_from_spline_points(
        brow_pts, radius=0.0025, samples_per_segment=10, radial_segments=10,
    )
    front.visual(mesh_from_geometry(brow, "brow_frame"),
                 material=mats["frame"], name="brow_frame", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))


# --------------------------------------------------------------------------- #
# Slot B — bridge / nose support
# --------------------------------------------------------------------------- #
def _build_standard_bridge(front, r: ResolvedGlassesConfig, mats, *, shield: bool) -> None:
    """Bridge bar(s) spanning the inner rim edges + 2 nose pads on stems.
    Adapted from parent A L117-L174.  When shield=True the inter-rim bar is
    DROPPED (one continuous shield has no rim gap) and only the internal nose
    support is emitted (compatibility-matrix degrade)."""
    inner_edge = r.rim_center_x - r.lens_half_w + 0.001
    if not shield:
        # double bridge: two parallel horizontal bars overlapping both rims.
        for tag, bz in (("upper", 0.0125), ("lower", -0.0035)):
            bz = min(bz, r.lens_half_h - 0.006)
            bar_pts = [
                (-inner_edge - 0.001, FRAME_Y, bz),
                (0.0, FRAME_Y, bz + (0.0006 if tag == "upper" else -0.0006)),
                (inner_edge + 0.001, FRAME_Y, bz),
            ]
            bar = tube_from_spline_points(
                bar_pts, radius=0.0013, samples_per_segment=8, radial_segments=10,
            )
            front.visual(mesh_from_geometry(bar, f"bridge_bar_{tag}"),
                         material=mats["frame"], name=f"bridge_bar_{tag}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))
        for i, stx in enumerate((-inner_edge + 0.004, inner_edge - 0.004)):
            strut = CylinderGeometry(radius=0.0011, height=0.0175, radial_segments=8)
            strut.translate(stx, FRAME_Y, 0.0045)
            front.visual(mesh_from_geometry(strut, f"bridge_strut_{i}"),
                         material=mats["accent"], name=f"bridge_strut_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))

    # nose pads on thin curved stems (rear -Y face) — common to both cases.
    for side, sx in SIDES:
        attach_x = sx * (inner_edge + 0.002)
        stem_pts = [
            (attach_x, FRAME_Y - 0.001, -r.lens_half_h * 0.30),
            (sx * (inner_edge - 0.002), FRAME_Y - 0.005, -r.lens_half_h - 0.006),
            (sx * (inner_edge - 0.003), FRAME_Y - 0.010, -r.lens_half_h - 0.014),
        ]
        stem = tube_from_spline_points(
            stem_pts, radius=0.0009, samples_per_segment=10, radial_segments=8,
        )
        front.visual(mesh_from_geometry(stem, f"nose_stem_{side}"),
                     material=mats["accent"], name=f"nose_stem_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))
        pad = _nose_pad_geometry()
        pad.rotate_z(sx * 0.35)
        pad.rotate_x(math.pi)
        pad.translate(sx * (inner_edge - 0.003), FRAME_Y - 0.011, -r.lens_half_h - 0.015)
        front.visual(mesh_from_geometry(pad, f"nose_pad_{side}"),
                     material=mats["accent"], name=f"nose_pad_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))


def _build_keyhole_bridge(front, r: ResolvedGlassesConfig, mats) -> None:
    """Keyhole saddle bridge solid (replaces the separate nose pads).
    Re-authored (lineage B) from keyhole_bridge L178-L257 as a mesh: a solid
    block spanning the rim gap with a keyhole-shaped through cut, built as a
    frame ring around the keyhole outline so the saddle opening is visible."""
    bridge_w = r.lens_gap + 0.012
    bridge_h = r.lens_half_h * 1.1
    bridge_cz = (r.lens_half_h - 0.006) - bridge_h * 0.25
    depth = 0.008

    g = MeshGeometry()
    # keyhole outline (x,z): round top opening + tapered slot below.
    kh_r = min(0.0055, bridge_w * 0.30)
    kh_slot_hw = kh_r * 0.40
    kh_cz = bridge_cz + bridge_h * 0.12
    kh_bot = bridge_cz - bridge_h * 0.42
    n_arc = 18
    arc = []
    for i in range(n_arc + 1):
        ang = math.radians(210.0 - 240.0 * i / n_arc)
        arc.append((kh_r * math.cos(ang), kh_r * math.sin(ang) + kh_cz))
    left_top, right_top = arc[0], arc[-1]
    taper = 1.3
    slot = [
        (-kh_slot_hw * taper, left_top[1]),
        (-kh_slot_hw, kh_bot + 0.002),
        (-kh_slot_hw * 0.6, kh_bot),
        (kh_slot_hw * 0.6, kh_bot),
        (kh_slot_hw, kh_bot + 0.002),
        (kh_slot_hw * taper, right_top[1]),
    ]
    inner = arc + slot  # keyhole hole outline (x,z)
    outer = _rounded_square_loop(bridge_w / 2.0, bridge_h / 2.0, 0.003, n_corner=5)
    outer = [(x, z + bridge_cz) for (x, z) in outer]
    # resample inner to match outer length for the ring band
    inner = _resample_loop(inner, len(outer))
    bridge = _ring_band(g, outer, inner, depth)
    front.visual(mesh_from_geometry(bridge, "keyhole_bridge"),
                 material=mats["frame"], name="keyhole_bridge", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))


def _resample_loop(loop, n):
    """Resample a closed (x,z) loop to exactly n points by arc-length."""
    m = len(loop)
    if m == n:
        return loop
    # cumulative perimeter
    segd = []
    total = 0.0
    for i in range(m):
        a = loop[i]
        b = loop[(i + 1) % m]
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        segd.append(d)
        total += d
    out = []
    target = 0.0
    step = total / n
    acc = 0.0
    i = 0
    for _ in range(n):
        while acc + segd[i] < target and i < m - 1:
            acc += segd[i]
            i += 1
        a = loop[i]
        b = loop[(i + 1) % m]
        frac = 0.0 if segd[i] < 1e-9 else (target - acc) / segd[i]
        out.append((a[0] + (b[0] - a[0]) * frac, a[1] + (b[1] - a[1]) * frac))
        target += step
    return out


def _ring_band(g: MeshGeometry, outer, inner, thickness):
    """Closed ring band between two (x,z) loops, thickness along Y. Returns g."""
    n = min(len(outer), len(inner))
    hy = thickness / 2.0
    idx = {}
    for i in range(n):
        ox, oz = outer[i]
        ix, iz = inner[i]
        idx[("of", i)] = g.add_vertex(ox, hy, oz)
        idx[("ob", i)] = g.add_vertex(ox, -hy, oz)
        idx[("if", i)] = g.add_vertex(ix, hy, iz)
        idx[("ib", i)] = g.add_vertex(ix, -hy, iz)
    for i in range(n):
        j = (i + 1) % n
        of_i, of_j = idx[("of", i)], idx[("of", j)]
        ob_i, ob_j = idx[("ob", i)], idx[("ob", j)]
        if_i, if_j = idx[("if", i)], idx[("if", j)]
        ib_i, ib_j = idx[("ib", i)], idx[("ib", j)]
        g.add_face(of_i, of_j, if_j)
        g.add_face(of_i, if_j, if_i)
        g.add_face(ob_i, ib_j, ob_j)
        g.add_face(ob_i, ib_i, ib_j)
        g.add_face(of_i, ob_j, of_j)
        g.add_face(of_i, ob_i, ob_j)
        g.add_face(if_i, if_j, ib_j)
        g.add_face(if_i, ib_j, ib_i)
    return g


def _nose_pad_geometry() -> MeshGeometry:
    """Small oval slightly-cupped metal nose pad. Adapted from parent A L330-L352."""
    g = MeshGeometry()
    rw, rh, th, n = 0.0046, 0.0068, 0.0010, 14
    ring_f, ring_b = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        ring_f.append(g.add_vertex(rw * math.cos(a), 0.0, rh * math.sin(a)))
        ring_b.append(g.add_vertex(rw * math.cos(a), -th, rh * math.sin(a)))
    cf = g.add_vertex(0.0, 0.0006, 0.0)
    cb = g.add_vertex(0.0, -th, 0.0)
    for i in range(n):
        j = (i + 1) % n
        g.add_face(ring_f[i], ring_f[j], cf)
        g.add_face(ring_b[j], ring_b[i], cb)
        g.add_face(ring_f[i], ring_b[i], ring_b[j])
        g.add_face(ring_f[i], ring_b[j], ring_f[j])
    return g


# --------------------------------------------------------------------------- #
# Hinge mounts (front_frame visuals) + Slot C temple chains
# --------------------------------------------------------------------------- #
def _build_hinge_blocks(front, r: ResolvedGlassesConfig, mats) -> dict:
    """Boxy metal hinge blocks at the outer-top rim corners. The block is an
    X-elongated bar reaching from inside the rim outline (so it always overlaps
    the rim/brow wire — no disconnected island) out past the pivot point.
    Returns per-side pivot origins.  Adapted from parent A L176-L186."""
    hinge_data = {}
    pivot_x = r.hinge_x + 0.004  # |X| of the pivot, just outboard of the rim
    inner_x = r.rim_center_x + r.lens_half_w * 0.45  # well inside the rim outline
    bar_len = pivot_x - inner_x + 0.004
    bar_cx = (inner_x + pivot_x) / 2.0
    for side, sx in SIDES:
        hz = r.hinge_z
        hinge = BoxGeometry((bar_len, 0.009, 0.010))
        hinge.translate(sx * bar_cx, FRAME_Y - 0.001, hz)
        front.visual(mesh_from_geometry(hinge, f"hinge_block_{side}"),
                     material=mats["accent"], name=f"hinge_block_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))
        hinge_data[side] = (sx * pivot_x, FRAME_Y - 0.001, hz)
    return hinge_data


def _temple_arm_geometry(side, r: ResolvedGlassesConfig, *, thick: bool) -> tuple:
    """Temple arm authored in LOCAL frame (origin at the hinge pivot), extending
    along local +X.  Returns (arm_mesh, tip_mesh, knuckle_mesh).
    Adapted from parent A L196-L226 (slim) + thick_sport_temples (thick)."""
    L = r.temple_len
    if thick:
        prof = rounded_rect_profile(0.0060, 0.0050, radius=0.0018)
        tip_r = 0.0042
    else:
        prof = rounded_rect_profile(0.0034, 0.0026, radius=0.0010)
        tip_r = 0.0026
    arm_pts = [
        (0.0, 0.0, 0.0),
        (L * 0.45, 0.0, -0.001),
        (L * 0.80, 0.0, -0.004),
        (L * 0.93, 0.0, -0.012),
    ]
    arm = sweep_profile_along_spline(
        arm_pts, profile=prof, samples_per_segment=8, up_hint=(0.0, 0.0, 1.0),
    )
    tip_pts = [
        (L * 0.90, 0.0, -0.010),
        (L * 0.98, 0.0, -0.016),
        (L * 1.02, 0.0, -0.026),
        (L * 1.03, 0.0, -0.038),
    ]
    tip = tube_from_spline_points(
        tip_pts, radius=tip_r, samples_per_segment=10, radial_segments=8,
    )
    # hinge knuckle at the pivot end so its AABB contains the part-frame origin
    # (and reads as a real captured hinge knuckle).
    knuckle = BoxGeometry((0.008, 0.012, 0.012))
    knuckle.translate(0.001, 0.0, 0.0)
    return arm, tip, knuckle


def _build_temples_folding(model, front, r: ResolvedGlassesConfig, mats, hinge_data, *, thick: bool):
    """Slim folding temples (or thick sport temples): 1 revolute fold per side.
    Adapted from parent A L188-L261 / thick_sport_temples L191-L268."""
    for side, sx in SIDES:
        hx, hy, hz = hinge_data[side]
        temple = model.part(f"temple_{side}")
        arm, tip, knuckle = _temple_arm_geometry(side, r, thick=thick)
        temple.visual(mesh_from_geometry(arm, f"arm_{side}"),
                      material=mats["frame"], name=f"arm_{side}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))
        temple.visual(mesh_from_geometry(tip, f"ear_tip_{side}"),
                      material=mats["tip"], name=f"ear_tip_{side}", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_black", "smoky_tint", "amber_tint", "silver_metal"} else "plastic.clear_rigid"))
        temple.visual(mesh_from_geometry(knuckle, f"knuckle_{side}"),
                      material=mats["accent"], name=f"knuckle_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))
        temple.inertial = Inertial.from_geometry(
            Box((r.temple_len, 0.006, 0.012)), mass=0.02,
            origin=Origin(xyz=(r.temple_len * 0.5, 0.0, -0.006)),
        )
        yaw = -math.pi / 2
        axis = (0.0, 0.0, -1.0) if sx > 0 else (0.0, 0.0, 1.0)
        model.articulation(
            f"fold_{side}",
            ArticulationType.REVOLUTE,
            parent=front,
            child=temple,
            origin=Origin(xyz=(hx, hy, hz), rpy=(0.0, 0.0, yaw)),
            axis=axis,
            motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.fold_range),
            # Mechanical pivot: the temple knuckle is captured inside the hinge
            # block (pin-through-sleeve). MatingContract does not model this
            # cleanly, so the joint is grandfathered (mating omitted) and the
            # intentional capture overlap is declared via allow_overlap in tests.
        )


def _build_temples_spring(model, front, r: ResolvedGlassesConfig, mats, hinge_data):
    """Spring hinges: insert a flex_link intermediate part per side with its own
    upstream small-range spring revolute, then the main fold downstream.
    front -> flex_link (spring 0..spring_range) -> temple (fold 0..fold_range).
    4 revolute joints total, chain depth 2.
    Re-authored (lineage B) from spring_hinges L184-L517."""
    flex_len = 0.014
    flex_w = 0.010
    for side, sx in SIDES:
        hx, hy, hz = hinge_data[side]
        yaw = -math.pi / 2
        # spring barrel visual on the front frame (the larger hinge barrel).
        barrel = CylinderGeometry(radius=0.0042, height=0.011, radial_segments=12)
        barrel.rotate_x(math.pi / 2.0)  # axis along Y (pin direction)
        barrel.translate(sx * r.hinge_x + sx * 0.0015, FRAME_Y - 0.001, hz)
        front.visual(mesh_from_geometry(barrel, f"spring_barrel_{side}"),
                     material=mats["accent"], name=f"spring_barrel_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))

        # flex link: small plate authored in LOCAL +X frame (origin at barrel).
        flex = model.part(f"flex_link_{side}")
        plate_pts = [
            (0.0, 0.0, 0.0),
            (flex_len * 0.5, 0.0, 0.0),
            (flex_len, 0.0, -0.001),
        ]
        plate = sweep_profile_along_spline(
            plate_pts, profile=rounded_rect_profile(0.005, flex_w, radius=0.0012),
            samples_per_segment=6, up_hint=(0.0, 0.0, 1.0),
        )
        flex.visual(mesh_from_geometry(plate, f"flex_link_{side}"),
                    material=mats["frame"], name=f"flex_link_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))
        # boss at flex pivot end so its AABB contains the local origin.
        boss = BoxGeometry((0.006, flex_w, 0.008))
        boss.translate(0.001, 0.0, 0.0)
        flex.visual(mesh_from_geometry(boss, f"flex_boss_{side}"),
                    material=mats["accent"], name=f"flex_boss_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))
        flex.inertial = Inertial.from_geometry(
            Box((flex_len, flex_w, 0.008)), mass=0.004,
            origin=Origin(xyz=(flex_len * 0.5, 0.0, 0.0)),
        )

        axis_spring = (0.0, 0.0, -1.0) if sx > 0 else (0.0, 0.0, 1.0)
        model.articulation(
            f"spring_{side}",
            ArticulationType.REVOLUTE,
            parent=front,
            child=flex,
            origin=Origin(xyz=(hx, hy, hz), rpy=(0.0, 0.0, yaw)),
            axis=axis_spring,
            motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.spring_range),
            # Grandfathered mechanical pivot (flex boss captured in the spring
            # barrel); capture overlap declared via allow_overlap in tests.
        )

        # temple arm authored in LOCAL +X frame (origin at flex far end).
        temple = model.part(f"temple_{side}")
        arm, tip, knuckle = _temple_arm_geometry(side, r, thick=False)
        temple.visual(mesh_from_geometry(arm, f"arm_{side}"),
                      material=mats["frame"], name=f"arm_{side}", material_class_id=("plastic.frosted_translucent" if r.palette_style in {"clear_acetate", "tortoise", "matte_black", "smoky_tint", "amber_tint"} else "metal.aluminum_bare"))
        temple.visual(mesh_from_geometry(tip, f"ear_tip_{side}"),
                      material=mats["tip"], name=f"ear_tip_{side}", material_class_id=("rubber.smooth_plain" if r.palette_style in {"matte_black", "smoky_tint", "amber_tint", "silver_metal"} else "plastic.clear_rigid"))
        temple.visual(mesh_from_geometry(knuckle, f"knuckle_{side}"),
                      material=mats["accent"], name=f"knuckle_{side}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"clear_acetate", "tortoise", "smoky_tint", "silver_metal"} else "metal.blackened_gunmetal"))
        temple.inertial = Inertial.from_geometry(
            Box((r.temple_len, 0.006, 0.012)), mass=0.02,
            origin=Origin(xyz=(r.temple_len * 0.5, 0.0, -0.006)),
        )
        # fold joint sits at the flex link's far end; both flex and temple are
        # authored along local +X, so the downstream fold origin is +X=flex_len.
        axis_fold = (0.0, 0.0, 1.0) if sx > 0 else (0.0, 0.0, -1.0)
        # NOTE: flex local +X already points world -Y (via the spring yaw), and
        # the temple is authored along its own local +X which the fold origin
        # rotates; we mirror so positive q still folds inward.
        model.articulation(
            f"fold_{side}",
            ArticulationType.REVOLUTE,
            parent=flex,
            child=temple,
            origin=Origin(xyz=(flex_len, 0.0, 0.0)),
            axis=axis_fold,
            motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.fold_range),
            # Grandfathered mechanical pivot (temple knuckle captured at the
            # flex-link far end); capture overlap declared via allow_overlap.
        )


# --------------------------------------------------------------------------- #
# Lens children (FIXED, normalized per-eye for QC) — Slot A lens emission
# --------------------------------------------------------------------------- #
def _build_lens_children(model, front, r: ResolvedGlassesConfig, mats):
    """Lenses are NON-articulating, so per AUTHORING.md §A Rule 1 they are
    emitted as `front_frame.visual(...)` (lineage B's native form — both parent
    sources author lenses as front-frame visuals), NOT as FIXED-jointed parts.
    They sit in the rim openings at the lens plane (rim outline == lens outline).
    wraparound_shield emits one continuous shield visual instead of 2 lenses."""
    if r.front_shape == "wraparound_shield":
        shield = _shield_lens_geometry(r)
        front.visual(mesh_from_geometry(shield, "shield_lens"),
                     material=mats["lens"], name="shield_lens", material_class_id=("glass.smoked_tinted" if r.palette_style in {"tortoise", "matte_black", "smoky_tint", "amber_tint", "silver_metal"} else "glass.clear_transparent"))
        return
    for side, sx in SIDES:
        cx = sx * r.rim_center_x
        loop = _lens_outline(r.front_shape, sx, r.lens_half_w - 0.001, r.lens_half_h - 0.001)
        lens_geo = _lens_geometry(loop, cx)  # centred at the rim center
        front.visual(mesh_from_geometry(lens_geo, f"lens_{side}"),
                     material=mats["lens"], name=f"lens_{side}", material_class_id=("glass.smoked_tinted" if r.palette_style in {"tortoise", "matte_black", "smoky_tint", "amber_tint", "silver_metal"} else "glass.clear_transparent"))


# --------------------------------------------------------------------------- #
# Top-level build
# --------------------------------------------------------------------------- #
def build_glasses(config: GlassesConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="glasses", assets=assets)
    mat_names = {}
    for token, rgba in r.palette.items():
        model.material(f"{r.palette_style}_{token}", rgba=rgba)
        mat_names[token] = f"{r.palette_style}_{token}"
    mats = mat_names

    front = model.part("front_frame")
    shield = r.front_shape == "wraparound_shield"

    # --- Slot A front rim/brow visuals ---
    if r.front_shape == "sport_front_frame":
        _build_brow_bar(front, r, mats)
    elif r.front_shape == "round_wire_rims":
        _build_round_wire_rim(front, r, mats)
    elif shield:
        _build_shield_brow(front, r, mats)
    else:
        _build_full_rim(front, r, mats)

    # --- Hinge mounts (must exist before temple chains) ---
    hinge_data = _build_hinge_blocks(front, r, mats)

    # --- Slot B bridge / nose ---
    if r.bridge_style == "keyhole_bridge" and not shield:
        _build_keyhole_bridge(front, r, mats)
    else:
        _build_standard_bridge(front, r, mats, shield=shield)

    # front_frame inertial (anchors the root).
    front.inertial = Inertial.from_geometry(
        Box(((r.rim_center_x + r.lens_half_w) * 2, 0.012, r.lens_half_h * 2 + 0.02)),
        mass=0.04,
        origin=Origin(xyz=(0.0, FRAME_Y, 0.0)),
    )

    # --- Slot A lens children ---
    _build_lens_children(model, front, r, mats)

    # --- Slot C temple chain(s) ---
    if r.temple_style == "spring_hinges":
        _build_temples_spring(model, front, r, mats, hinge_data)
    else:
        thick = r.temple_style == "thick_sport_temples"
        _build_temples_folding(model, front, r, mats, hinge_data, thick=thick)

    return model


def build_seeded_glasses(seed: int) -> ArticulatedObject:
    return build_glasses(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    cfg = config_from_seed(seed)
    front = str(cfg.front_shape)
    bridge = _legalize(front, str(cfg.bridge_style))
    return [
        ("front_shape", front),
        ("bridge_style", bridge),
        ("temple_style", str(cfg.temple_style)),
    ]


# --------------------------------------------------------------------------- #
# Author tests
# --------------------------------------------------------------------------- #
def run_glasses_tests(model: ArticulatedObject, config: GlassesConfig) -> TestReport:
    ctx = TestContext(model)
    r = resolve_config(config)

    # Captured-pin hinge overlaps (element-scoped). Replicate per chosen names.
    for side in ("right", "left"):
        if r.temple_style == "spring_hinges":
            ctx.allow_overlap(
                "front_frame", f"flex_link_{side}",
                elem_a=f"spring_barrel_{side}", elem_b=f"flex_boss_{side}",
                reason="Flex-link boss captured inside the spring barrel.",
            )
            ctx.allow_overlap(
                f"flex_link_{side}", f"temple_{side}",
                elem_a=f"flex_link_{side}", elem_b=f"knuckle_{side}",
                reason="Temple hinge knuckle captured inside the flex link.",
            )
        else:
            ctx.allow_overlap(
                "front_frame", f"temple_{side}",
                elem_a=f"hinge_block_{side}", elem_b=f"knuckle_{side}",
                reason="Temple hinge knuckle captured inside the hinge block.",
            )
        if r.front_shape == "wraparound_shield":
            # The wide shield edge reaches the hinge corner and overlaps the
            # captured knuckle — this is the wraparound hinge interface.
            ctx.allow_overlap(
                "front_frame", f"temple_{side}",
                elem_a="shield_lens", elem_b=f"knuckle_{side}",
                reason="Wraparound shield edge meets the captured temple knuckle at the hinge.",
            )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ≥1 real revolute fold per side (the core articulation).
    fold_joints = [
        j for j in model.articulations
        if j.articulation_type == ArticulationType.REVOLUTE and j.name.startswith("fold_")
    ]
    ctx.check(
        "exactly two temple revolute fold joints",
        len(fold_joints) == 2,
        details=f"found {[j.name for j in fold_joints]}",
    )
    for j in fold_joints:
        lim = j.motion_limits
        span = abs((lim.upper or 0.0) - (lim.lower or 0.0)) if lim else 0.0
        ctx.check(
            f"{j.name} folds a meaningful angle (>=60deg)",
            span >= math.radians(60.0),
            details=f"span={math.degrees(span):.1f} deg",
        )

    # spring_hinges => 4 revolute total (2 spring + 2 fold), spring range 5..30deg.
    if r.temple_style == "spring_hinges":
        spring_joints = [
            j for j in model.articulations
            if j.articulation_type == ArticulationType.REVOLUTE and j.name.startswith("spring_")
        ]
        ctx.check(
            "spring_hinges adds two upstream spring revolute joints",
            len(spring_joints) == 2,
            details=f"found {[j.name for j in spring_joints]}",
        )
        for j in spring_joints:
            lim = j.motion_limits
            span = abs((lim.upper or 0.0) - (lim.lower or 0.0)) if lim else 0.0
            ctx.check(
                f"{j.name} spring range within 5..30deg",
                math.radians(5.0) <= span <= math.radians(30.0),
                details=f"span={math.degrees(span):.1f} deg",
            )

    # Both temples actually fold: AABB extent flips from along fore/aft (Y) to
    # across width (X) when folded 90deg.
    for side in ("right", "left"):
        temple = model.get_part(f"temple_{side}")
        fold = model.get_articulation(f"fold_{side}")
        rest = ctx.part_world_aabb(temple)
        with ctx.pose({fold: math.radians(90.0)}):
            folded = ctx.part_world_aabb(temple)
        if rest is None or folded is None:
            continue
        rest_ext = [rest[1][k] - rest[0][k] for k in range(3)]
        fold_ext = [folded[1][k] - folded[0][k] for k in range(3)]
        ctx.check(
            f"temple_{side} swings from along-Y to across-X when folded",
            rest_ext[1] > 0.09 and fold_ext[0] > rest_ext[0] + 0.04,
            details=f"rest={rest_ext}, folded={fold_ext}",
        )

    # Lens / shield present.
    if r.front_shape == "wraparound_shield":
        sv = model.get_part("front_frame").get_visual("shield_lens")
        ctx.check("shield lens present", sv is not None)
        aabb = ctx.part_element_world_aabb(model.get_part("front_frame"), elem="shield_lens")
        if aabb is not None:
            width = aabb[1][0] - aabb[0][0]
            ctx.check("shield spans both eyes (>0.10m)", width > 0.10,
                      details=f"shield_width={width:.4f}")
    else:
        front_part = model.get_part("front_frame")
        for side in ("right", "left"):
            lv = front_part.get_visual(f"lens_{side}")
            ctx.check(f"{side} lens visual present", lv is not None)

    # Lenses translucent (palette lens alpha < 1).
    lens_alpha = r.palette["lens"][3]
    ctx.check("lens material is translucent", lens_alpha < 0.95,
              details=f"lens alpha={lens_alpha}")

    # Total frame width in the eyewear envelope.
    front_aabb = ctx.part_world_aabb(model.get_part("front_frame"))
    if front_aabb is not None:
        w = front_aabb[1][0] - front_aabb[0][0]
        ctx.check("frame width in eyewear range", 0.09 <= w <= 0.18,
                  details=f"frame_width={w:.4f}")

    return ctx.report()


__all__ = [
    "FrontShape",
    "BridgeStyle",
    "TempleStyle",
    "PaletteStyle",
    "GlassesConfig",
    "ResolvedGlassesConfig",
    "config_from_seed",
    "resolve_config",
    "build_glasses",
    "build_seeded_glasses",
    "slot_choices_for_seed",
    "run_glasses_tests",
]
