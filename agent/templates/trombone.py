# SPDX-License-Identifier: Apache-2.0

"""Brass trombone — modular template.

A lacquered-brass trombone on the S1 tenor spine (``picture/0611/trombone/001``):
a grounded ``body`` (fixed bell section + fixed inner slide legs, legs stacked in
Z) carries a telescoping ``outer_slide`` (PRISMATIC +X — the defining hand-slide
DOF) and a rear ``tuning_slide`` (PRISMATIC -X), plus 0-2 rotary-valve child
parts (REVOLUTE +Z).

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/trombone.md`` and the
``picture/0611/trombone`` 5-star pool (2 origins + 9 slot forks), synced under
``data/records/``. Primitive strategy = S1: ``Cylinder`` tubes + ``LatheGeometry``
bell/mouthpiece shells + ``tube_from_spline_points``/``WirePath`` sweeps +
``TorusGeometry`` disc rim — no cadquery booleans (cheap tessellation, ≤12 s/seed).

Structure (pattern = ``mixed``): a fixed 3-part / 2-prismatic-joint spine; four
axes swap one layer each:

  * ``bell_form`` (4, ③ Primary Form Family): tenor / bass / soprano / slender —
    the bell flare Volumetric Envelope (Lathe母线 throat/rim/len/exp) + derived
    BELL_Z. Carries primary visual diversity.
  * ``slide_style`` (2): disc_brace (ribbed chrome disc) / plain_collar (nickel
    stocking collars + U-bend ferrule) — outer-slide hardware.
  * ``valve_attachment`` (3, ② joint type): none / single_rotary / dual_rotary —
    0/1/2 captured REVOLUTE +Z rotor parts + host casings/wrap-loops.
  * ``water_key_count`` (0/1/2 multiplicity): fused host water-key visuals.

Global similarity ``s = frame_scale * form_scale`` multiplies every literal dim /
origin / joint origin / travel, and every mesh's profile/point coordinates, so the
bell母线 and every telescoping clearance stay intact at every scale. ``BELL_Z`` is
single-sourced from the per-form bell rim radius so the flare always clears the top
slide tube (Rule 4/Contract 3c).

Telescoping prismatic joints (outer/inner tubes, tuning sleeves/loop) and captured
rotor pins are intentional overlaps: they **omit** ``MatingContract`` (Rule 2
grandfather for sleeves/captured pins) and are declared element-scoped in
``run_trombone_tests`` (mirroring both origins' run_tests).
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
    Cylinder,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    WirePath,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BellForm = Literal["tenor", "bass", "soprano", "slender"]
SlideStyle = Literal["disc_brace", "plain_collar"]
ValveAttachment = Literal["none", "single_rotary", "dual_rotary"]
PaletteStyle = Literal[
    "gold_lacquer",
    "pale_gold_polished",
    "silver_plated",
    "rose_brass",
    "dark_lacquer",
]

BELL_FORMS: tuple[BellForm, ...] = ("tenor", "bass", "soprano", "slender")
SLIDE_STYLES: tuple[SlideStyle, ...] = ("disc_brace", "plain_collar")
VALVE_ATTACHMENTS: tuple[ValveAttachment, ...] = ("none", "single_rotary", "dual_rotary")
WATER_KEY_COUNTS: tuple[int, ...] = (0, 1, 2)
WATER_KEY_WEIGHTS: tuple[float, ...] = (0.3, 0.5, 0.2)  # {0,1,2}
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "gold_lacquer",
    "pale_gold_polished",
    "silver_plated",
    "rose_brass",
    "dark_lacquer",
)

# Palette roles: brass (main lacquer body/bell/tubing), brass_deep (ferrules /
# sleeves / dark braces), bright (chromed inner tubes / disc / collars),
# accent (dark ribs / disc rim / rotor caps). Every .visual(material=) is driven
# by the sampled palette. gold_lacquer == S1 origin colorway; pale_gold_polished
# == S2 origin colorway.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "gold_lacquer": {
        "brass": (0.78, 0.59, 0.20, 1.0),
        "brass_deep": (0.66, 0.49, 0.16, 1.0),
        "bright": (0.80, 0.82, 0.85, 1.0),
        "accent": (0.45, 0.47, 0.50, 1.0),
    },
    "pale_gold_polished": {
        "brass": (0.88, 0.67, 0.25, 1.0),
        "brass_deep": (0.50, 0.32, 0.09, 1.0),
        "bright": (0.80, 0.82, 0.78, 1.0),
        "accent": (0.40, 0.42, 0.40, 1.0),
    },
    "silver_plated": {
        "brass": (0.82, 0.84, 0.86, 1.0),  # silver-plated body
        "brass_deep": (0.72, 0.55, 0.20, 1.0),  # gold trim
        "bright": (0.90, 0.91, 0.93, 1.0),
        "accent": (0.34, 0.36, 0.38, 1.0),
    },
    "rose_brass": {
        "brass": (0.80, 0.52, 0.36, 1.0),
        "brass_deep": (0.62, 0.38, 0.24, 1.0),
        "bright": (0.82, 0.80, 0.78, 1.0),
        "accent": (0.42, 0.30, 0.24, 1.0),
    },
    "dark_lacquer": {
        "brass": (0.52, 0.40, 0.16, 1.0),
        "brass_deep": (0.38, 0.28, 0.10, 1.0),
        "bright": (0.62, 0.60, 0.55, 1.0),
        "accent": (0.28, 0.24, 0.16, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal geometry constants (meters, s == 1), from S1 origin model.py L31-48.
# ---------------------------------------------------------------------------
X_RPY = (0.0, math.pi / 2.0, 0.0)  # rotate a +Z cylinder onto +X

TUBE_R_INNER = 0.0070
TUBE_R_OUTER = 0.0086
SLEEVE_R = 0.0095
TOP_Z = 0.072  # upper slide leg axis (lower leg at z=0)
LOOP_LOW_Z = 0.046  # rear tuning-loop lower leg height

INNER_X0, INNER_X1 = 0.0, 0.70  # fixed inner slide tubes
OUTER_X0 = 0.13  # rear of outer slide at rest = slide joint origin
OUTER_LEN = 0.65
TUNING_X0 = -0.16
TUNING_TRAVEL = 0.025

MIN_ENGAGE = 0.06  # min closed slide insertion beyond the rest overlap floor
BELL_THROAT_X = -0.05  # bell throat x (flare opens toward +X from here)

# Per-form bell母线 + size. (throat_r, rim_r, flare_len, flare_exp, form_scale)
# tenor: S1 L69-99; bass: bass fork bell; soprano: soprano fork; slender: S2 L155-186.
BELL_FORM_PARAMS: dict[BellForm, tuple[float, float, float, float, float]] = {
    "tenor": (0.0095, 0.100, 0.400, 2.60, 1.00),
    "bass": (0.0110, 0.118, 0.460, 2.40, 1.09),
    "soprano": (0.0075, 0.062, 0.240, 2.80, 0.82),
    "slender": (0.0066, 0.090, 0.420, 3.20, 1.03),
}

FRAME_SCALE_RANGE = (0.90, 1.12)
SLIDE_EXTENSION_RANGE = (0.75, 1.0)
VALVE_RANGE = 0.6  # rotary trigger throw (rad)
VALVE_CY = 0.030  # rotary valve casing/rotor outboard offset (+Y, clears bell tube)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TromboneConfig:
    bell_form: BellForm | None = None
    slide_style: SlideStyle | None = None
    valve_attachment: ValveAttachment | None = None
    water_key_count: int | None = None
    palette_style: PaletteStyle = "gold_lacquer"
    frame_scale: float = 1.0
    slide_extension_scale: float = 1.0
    name: str = "trombone"


@dataclass(frozen=True)
class ResolvedTromboneConfig:
    bell_form: BellForm
    slide_style: SlideStyle
    valve_attachment: ValveAttachment
    water_key_count: int
    palette_style: PaletteStyle
    s: float  # global similarity (frame_scale * form_scale)
    ext: float  # slide_extension_scale
    name: str
    # derived bell母线 (nominal, pre-scale)
    throat_r: float
    rim_r: float
    flare_len: float
    flare_exp: float


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> TromboneConfig:
    rng = random.Random(seed)
    return TromboneConfig(
        bell_form=rng.choice(BELL_FORMS),
        slide_style=rng.choice(SLIDE_STYLES),
        valve_attachment=rng.choice(VALVE_ATTACHMENTS),
        water_key_count=rng.choices(WATER_KEY_COUNTS, weights=WATER_KEY_WEIGHTS)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        frame_scale=round(rng.uniform(*FRAME_SCALE_RANGE), 4),
        slide_extension_scale=round(rng.uniform(*SLIDE_EXTENSION_RANGE), 4),
        name=f"seeded_trombone_{seed}",
    )


def resolve_config(config: TromboneConfig | None = None) -> ResolvedTromboneConfig:
    cfg = config or TromboneConfig()
    bell_form = _pick(cfg.bell_form, BELL_FORMS)
    throat_r, rim_r, flare_len, flare_exp, form_scale = BELL_FORM_PARAMS[bell_form]
    s = _clamp(cfg.frame_scale, *FRAME_SCALE_RANGE) * form_scale
    ext = _clamp(cfg.slide_extension_scale, *SLIDE_EXTENSION_RANGE)
    wk = cfg.water_key_count
    wk = wk if wk in WATER_KEY_COUNTS else 1
    return ResolvedTromboneConfig(
        bell_form=bell_form,
        slide_style=_pick(cfg.slide_style, SLIDE_STYLES),
        valve_attachment=_pick(cfg.valve_attachment, VALVE_ATTACHMENTS),
        water_key_count=wk,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        s=s,
        ext=ext,
        name=cfg.name or "trombone",
        throat_r=throat_r,
        rim_r=rim_r,
        flare_len=flare_len,
        flare_exp=flare_exp,
    )


def slot_choices_for_config(
    config: TromboneConfig | ResolvedTromboneConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTromboneConfig) else resolve_config(config)
    return (
        ("bell_form", r.bell_form),
        ("slide_style", r.slide_style),
        ("valve_attachment", r.valve_attachment),
        ("water_key_count", str(r.water_key_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Derived quantities (single-sourced; Contract 3c).
# ---------------------------------------------------------------------------
def _bell_z_nom(r: ResolvedTromboneConfig) -> float:
    """Bell axis height (nominal). Rises with rim so the flare clears the top
    slide tube (z=TOP_Z, radius TUBE_R_OUTER)."""
    return TOP_Z + r.rim_r + 0.020


def _slide_travel_nom(r: ResolvedTromboneConfig) -> float:
    """Max hand-slide travel (nominal) that keeps ≥0.05 extended insertion.
    Rest overlap = (INNER_X1 - OUTER_X0); reserve MIN_ENGAGE at full stroke."""
    max_travel = (INNER_X1 - OUTER_X0) - MIN_ENGAGE  # 0.51
    return max_travel * r.ext


# ---------------------------------------------------------------------------
# Scaled-Origin + geometry helpers (every coordinate × s).
# ---------------------------------------------------------------------------
def _o(s: float, x: float = 0.0, y: float = 0.0, z: float = 0.0, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(x * s, y * s, z * s), rpy=rpy)


def _x_tube(part, name, x0, x1, z, radius, material, s):
    part.visual(
        Cylinder(radius=radius * s, length=abs(x1 - x0) * s),
        origin=_o(s, (x0 + x1) / 2.0, 0.0, z, rpy=X_RPY),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _z_bar(part, name, x, z0, z1, radius, material, s):
    part.visual(
        Cylinder(radius=radius * s, length=abs(z1 - z0) * s),
        origin=_o(s, x, 0.0, (z0 + z1) / 2.0),
        material=material,
        name=name, material_class_id="metal.brass_polished",
    )


def _bell_flare_geom(r: ResolvedTromboneConfig, s: float):
    """Parametric hollow revolved bell flare (LatheGeometry — never a Cylinder).
    母线: r(z) = throat + (rim-throat)*(z/len)^exp. (S1 L69-99 generalized.)"""
    n = 13
    outer = []
    for i in range(n + 1):
        t = i / n
        z = t * r.flare_len
        rad = r.throat_r + (r.rim_r - r.throat_r) * (t ** r.flare_exp)
        outer.append((rad * s, z * s))
    inner = [(max(rad - 0.0015 * s, 0.0008 * s), zz) for rad, zz in outer]
    geom = LatheGeometry.from_shell_profiles(
        outer, inner, segments=64, start_cap="flat", end_cap="round", lip_samples=8
    )
    geom.rotate_y(math.pi / 2.0).translate(BELL_THROAT_X * s, 0.0, _bell_z_nom(r) * s)
    return geom


def _mouthpiece_geom(s: float):
    """Solid lathe mouthpiece: shank tapers into the receiver, cup+rim rear. (S1 L102-122)"""
    profile = [
        (0.0000, 0.000), (0.0042, 0.001), (0.0048, 0.010), (0.0055, 0.020),
        (0.0062, 0.028), (0.0072, 0.033), (0.0090, 0.039), (0.0112, 0.045),
        (0.0126, 0.050), (0.0128, 0.053), (0.0118, 0.0555), (0.0085, 0.056),
        (0.0000, 0.056),
    ]
    geom = LatheGeometry([(rr * s, zz * s) for rr, zz in profile], segments=40)
    geom.rotate_y(-math.pi / 2.0).translate(-0.026 * s, 0.0, TOP_Z * s)
    return geom


def _gooseneck_geom(s: float):
    """Bottom slide leg rear curving back and up into the tuning loop. (S1 L125-139)"""
    pts = [
        (0.048, 0.0, 0.0), (-0.010, 0.0, 0.008), (-0.070, 0.0, 0.028),
        (-0.105, 0.0, 0.040), (-0.128, 0.0, LOOP_LOW_Z),
    ]
    return tube_from_spline_points(
        [(x * s, y * s, z * s) for x, y, z in pts],
        radius=0.008 * s, samples_per_segment=10, radial_segments=18, cap_ends=True,
    )


def _slide_bow_geom(s: float):
    """Outer-slide U-crook (outer-slide local frame), bulging forward. (S1 L142-159)"""
    top = TOP_Z * s
    wp = WirePath((0.630 * s, 0.0, top))
    wp.line_to((0.665 * s, 0.0, top))
    wp.arc(center=(0.665 * s, 0.0, top / 2.0), normal=(0.0, 1.0, 0.0), angle=math.pi, segments=24)
    wp.line_to((0.630 * s, 0.0, 0.0))
    return tube_from_spline_points(
        wp.to_points(), radius=TUBE_R_OUTER * s, samples_per_segment=2, radial_segments=18, cap_ends=True
    )


def _tuning_crook_geom(r: ResolvedTromboneConfig, s: float):
    """Tuning-slide U-crook (tuning local frame), bulging rearward. (S1 L162-179)"""
    up = (_bell_z_nom(r) - LOOP_LOW_Z) * s
    wp = WirePath((-0.068 * s, 0.0, up))
    wp.line_to((-0.078 * s, 0.0, up))
    wp.arc(center=(-0.078 * s, 0.0, up / 2.0), normal=(0.0, -1.0, 0.0), angle=math.pi, segments=24)
    wp.line_to((-0.068 * s, 0.0, 0.0))
    return tube_from_spline_points(
        wp.to_points(), radius=TUBE_R_OUTER * s, samples_per_segment=2, radial_segments=18, cap_ends=True
    )


def _wrap_loop_geom(cx: float, s: float, bz: float):
    """Small F-attachment wrap loop bridging bell_tube (y≈0) out to the valve
    casing OUTER wall (stops short of the rotor at the casing center). Host visual
    on body. (single fork L355-366 generalized.)"""
    y_wall = VALVE_CY - 0.017  # casing outer wall (casing radius 0.017)
    pts = [
        (cx + 0.018, 0.0, bz - 0.002), (cx + 0.006, y_wall * 0.5, bz - 0.008),
        (cx, y_wall, bz - 0.014),
    ]
    return tube_from_spline_points(
        [(x * s, y * s, z * s) for x, y, z in pts],
        radius=0.0055 * s, samples_per_segment=8, radial_segments=14, cap_ends=True,
    )


# ---------------------------------------------------------------------------
# body (root, fixed bell section + fixed inner slide legs).  Slot A writes here.
# ---------------------------------------------------------------------------
def _build_body(model, r, mats) -> object:
    s = r.s
    bz = _bell_z_nom(r)
    body = model.part("body")

    # fixed inner slide legs + rear air path (S1 L195-221)
    _x_tube(body, "inner_top_tube", INNER_X0, INNER_X1, TOP_Z, TUBE_R_INNER, mats["bright"], s)
    _x_tube(body, "inner_bottom_tube", INNER_X0, INNER_X1, 0.0, TUBE_R_INNER, mats["bright"], s)
    _x_tube(body, "inner_top_stocking", 0.63, INNER_X1, TOP_Z, 0.0078, mats["bright"], s)
    _x_tube(body, "inner_bottom_stocking", 0.63, INNER_X1, 0.0, 0.0078, mats["bright"], s)
    _x_tube(body, "mouthpiece_receiver", -0.03, 0.05, TOP_Z, SLEEVE_R, mats["brass_deep"], s)
    _x_tube(body, "gooseneck_ferrule", 0.0, 0.055, 0.0, SLEEVE_R, mats["brass_deep"], s)
    _z_bar(body, "inner_slide_brace", 0.075, 0.004, 0.068, 0.0038, mats["brass"], s)
    body.visual(
        mesh_from_geometry(_mouthpiece_geom(s), "mouthpiece"), material=mats["bright"], name="mouthpiece", material_class_id="metal.chrome_polished"
    )
    body.visual(
        mesh_from_geometry(_gooseneck_geom(s), "gooseneck_tube"), material=mats["brass"], name="gooseneck_tube", material_class_id=("metal.brass_polished" if r.palette_style in {"gold_lacquer", "pale_gold_polished", "silver_plated", "rose_brass"} else "metal.brass_aged")
    )
    _x_tube(body, "loop_lower_tube", -0.125, -0.21, LOOP_LOW_Z, 0.008, mats["brass"], s)
    _x_tube(body, "bell_tube", -0.21, -0.04, bz, 0.008, mats["brass"], s)
    body.visual(
        mesh_from_geometry(_bell_flare_geom(r, s), "bell_flare"), material=mats["brass"], name="bell_flare", material_class_id=("metal.brass_polished" if r.palette_style in {"gold_lacquer", "pale_gold_polished", "silver_plated", "rose_brass"} else "metal.brass_aged")
    )
    _z_bar(body, "bell_brace", 0.02, 0.076, bz - 0.004, 0.0038, mats["brass"], s)
    _z_bar(body, "loop_brace", -0.15, 0.050, bz - 0.006, 0.0035, mats["brass"], s)

    # --- valve_attachment host visuals (casings + wrap loops) on the body. ---
    for cx in _valve_casing_x(r):
        i = _valve_casing_x(r).index(cx)
        body.visual(
            Cylinder(radius=0.017 * s, length=0.026 * s),
            origin=_o(s, cx, VALVE_CY, bz - 0.02),
            material=mats["brass_deep"],
            name=f"valve_casing_{i}", material_class_id="metal.brass_aged",
        )
        body.visual(
            mesh_from_geometry(_wrap_loop_geom(cx, s, bz), f"valve_wrap_loop_{i}"),
            material=mats["brass"],
            name=f"valve_wrap_loop_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"gold_lacquer", "pale_gold_polished", "silver_plated", "rose_brass"} else "metal.brass_aged"),
        )
    return body


# ---------------------------------------------------------------------------
# outer_slide (PRISMATIC +X).  Slot B writes hardware; water key 0 lives here.
# ---------------------------------------------------------------------------
def _build_outer_slide(model, r, mats) -> object:
    s = r.s
    outer = model.part("outer_slide")
    _x_tube(outer, "outer_top_tube", 0.0, OUTER_LEN, TOP_Z, TUBE_R_OUTER, mats["brass"], s)
    _x_tube(outer, "outer_bottom_tube", 0.0, OUTER_LEN, 0.0, TUBE_R_OUTER, mats["brass"], s)
    _x_tube(outer, "outer_top_sleeve", 0.0, 0.028, TOP_Z, SLEEVE_R, mats["brass_deep"], s)
    _x_tube(outer, "outer_bottom_sleeve", 0.0, 0.028, 0.0, SLEEVE_R, mats["brass_deep"], s)
    outer.visual(
        mesh_from_geometry(_slide_bow_geom(s), "slide_bow"), material=mats["brass"], name="slide_bow", material_class_id=("metal.brass_polished" if r.palette_style in {"gold_lacquer", "pale_gold_polished", "silver_plated", "rose_brass"} else "metal.brass_aged")
    )
    _z_bar(outer, "outer_slide_brace", 0.04, 0.006, 0.066, 0.004, mats["brass"], s)

    if r.slide_style == "disc_brace":
        disc_center = (0.04, 0.0, TOP_Z / 2.0)
        outer.visual(
            Cylinder(radius=0.0245 * s, length=0.013 * s),
            origin=_o(s, *disc_center, rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["bright"], name="brace_disc", material_class_id="metal.chrome_polished",
        )
        rim = TorusGeometry(0.0245 * s, 0.003 * s, radial_segments=12, tubular_segments=48)
        rim.rotate_x(math.pi / 2.0).translate(disc_center[0] * s, 0.0, disc_center[2] * s)
        outer.visual(mesh_from_geometry(rim, "disc_rim"), material=mats["accent"], name="disc_rim", material_class_id="metal.blackened_gunmetal")
        outer.visual(
            Cylinder(radius=0.009 * s, length=0.0165 * s),
            origin=_o(s, *disc_center, rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"], name="disc_hub", material_class_id="metal.blackened_gunmetal",
        )
    else:  # plain_collar (S2 L323-345): stocking collars + U-bend ferrule
        for i, z in ((0, TOP_Z), (1, 0.0)):
            outer.visual(
                Cylinder(radius=0.0104 * s, length=0.024 * s),
                origin=_o(s, 0.014, 0.0, z, rpy=X_RPY),
                material=mats["bright"], name=f"slide_collar_{i}", material_class_id="metal.chrome_polished",
            )
        outer.visual(
            Cylinder(radius=0.0102 * s, length=0.012 * s),
            origin=_o(s, 0.6825, 0.0, TOP_Z / 2.0, rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["bright"], name="u_bend_ferrule", material_class_id="metal.chrome_polished",
        )

    if r.water_key_count >= 1:
        _water_key(outer, 0, 0.60, 0.0, TOP_Z, s, mats)
    return outer


# ---------------------------------------------------------------------------
# tuning_slide (PRISMATIC -X).  Water key 1 lives here.
# ---------------------------------------------------------------------------
def _build_tuning_slide(model, r, mats) -> object:
    s = r.s
    up = _bell_z_nom(r) - LOOP_LOW_Z
    tuning = model.part("tuning_slide")
    _x_tube(tuning, "tuning_lower_sleeve", 0.0, -0.075, 0.0, SLEEVE_R, mats["brass_deep"], s)
    _x_tube(tuning, "tuning_upper_sleeve", 0.0, -0.075, up, SLEEVE_R, mats["brass_deep"], s)
    tuning.visual(
        mesh_from_geometry(_tuning_crook_geom(r, s), "tuning_crook"), material=mats["brass"], name="tuning_crook", material_class_id=("metal.brass_polished" if r.palette_style in {"gold_lacquer", "pale_gold_polished", "silver_plated", "rose_brass"} else "metal.brass_aged")
    )
    _z_bar(tuning, "tuning_slide_brace", -0.055, 0.006, up - 0.006, 0.0035, mats["brass"], s)
    if r.water_key_count >= 2:
        _water_key(tuning, 1, -0.05, 0.0, 0.0, s, mats)
    return tuning


def _water_key(host, i, x, y, z, s, mats):
    """Fused spit-key: saddle nub + lever + touch-cork (host visuals, Rule 1)."""
    host.visual(
        Cylinder(radius=0.006 * s, length=0.010 * s),
        origin=_o(s, x, y, z + 0.011),
        material=mats["brass_deep"], name=f"water_key_saddle_{i}", material_class_id="metal.brass_aged",
    )
    host.visual(
        Box((0.018 * s, 0.004 * s, 0.004 * s)),
        origin=_o(s, x - 0.010, y, z + 0.017),
        material=mats["bright"], name=f"water_key_lever_{i}", material_class_id="metal.chrome_polished",
    )
    host.visual(
        Cylinder(radius=0.004 * s, length=0.004 * s),
        origin=_o(s, x - 0.001, y, z + 0.013),
        material=mats["accent"], name=f"water_key_cork_{i}", material_class_id="organic.cork",
    )


# ---------------------------------------------------------------------------
# valve_attachment: 0/1/2 captured REVOLUTE +Z rotor parts.  Slot C.
# ---------------------------------------------------------------------------
def _valve_casing_x(r: ResolvedTromboneConfig) -> tuple[float, ...]:
    if r.valve_attachment == "single_rotary":
        return (-0.12,)
    if r.valve_attachment == "dual_rotary":
        return (-0.15, -0.08)
    return ()


def _build_valve_rotor(model, r, mats, i: int) -> object:
    """A captured rotary-valve rotor: stem in the casing bore + hub + outboard
    thumb-lever paddle. (single fork trigger L420-450.) Built about local (0,0,0)
    = casing center; the +Z revolute joint origin lands on the casing centerline."""
    s = r.s
    rotor = model.part(f"valve_rotor_{i}")
    rotor.visual(
        Cylinder(radius=0.0055 * s, length=0.030 * s),
        origin=_o(s, 0.0, 0.0, 0.0), material=mats["bright"], name="rotor_stem", material_class_id="metal.chrome_polished",
    )
    rotor.visual(
        Cylinder(radius=0.010 * s, length=0.006 * s),
        origin=_o(s, 0.0, 0.0, 0.016), material=mats["accent"], name="rotor_hub", material_class_id="metal.blackened_gunmetal",
    )
    rotor.visual(
        Box((0.006 * s, 0.045 * s, 0.005 * s)),
        origin=_o(s, 0.0, 0.026, 0.016), material=mats["bright"], name="trigger_lever", material_class_id="metal.chrome_polished",
    )
    rotor.visual(
        Cylinder(radius=0.011 * s, length=0.004 * s),
        origin=_o(s, 0.0, 0.048, 0.016), material=mats["brass_deep"], name="thumb_paddle", material_class_id="metal.brass_aged",
    )
    return rotor


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_trombone(
    config: TromboneConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    s = r.s
    bz = _bell_z_nom(r)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"tbn_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats)
    outer = _build_outer_slide(model, r, mats)
    tuning = _build_tuning_slide(model, r, mats)

    # Hand slide — the defining trombone DOF (PRISMATIC +X). Travel clamped to
    # retained-insertion inequality; joint omits MatingContract (telescoping
    # sleeve, grandfathered — Rule 2).
    travel = _slide_travel_nom(r) * s
    model.articulation(
        "outer_slide_travel", ArticulationType.PRISMATIC, parent=body, child=outer,
        origin=_o(s, OUTER_X0, 0.0, 0.0), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=2.0, lower=0.0, upper=travel),
    )
    # Rear tuning slide (PRISMATIC -X, small throw).
    model.articulation(
        "tuning_slide_travel", ArticulationType.PRISMATIC, parent=body, child=tuning,
        origin=_o(s, TUNING_X0, 0.0, LOOP_LOW_Z), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=40.0, velocity=0.05, lower=0.0, upper=TUNING_TRAVEL * s),
    )

    # Rotary valve attachment(s) — captured REVOLUTE +Z rotors (② joint type).
    for i, cx in enumerate(_valve_casing_x(r)):
        rotor = _build_valve_rotor(model, r, mats, i)
        model.articulation(
            f"body_to_valve_rotor_{i}", ArticulationType.REVOLUTE, parent=body, child=rotor,
            origin=_o(s, cx, VALVE_CY, bz - 0.02), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=5.0, lower=0.0, upper=VALVE_RANGE),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_trombone(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_trombone(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _declare_captured_overlaps(ctx, model, r) -> None:
    body = model.get_part("body")
    outer = model.get_part("outer_slide")
    tuning = model.get_part("tuning_slide")

    # Telescoping outer slide over the fixed inner tubes (S1 L320-390).
    for oe, ie in (
        ("outer_top_tube", "inner_top_tube"), ("outer_bottom_tube", "inner_bottom_tube"),
        ("outer_top_tube", "inner_top_stocking"), ("outer_bottom_tube", "inner_bottom_stocking"),
        ("outer_top_sleeve", "inner_top_tube"), ("outer_bottom_sleeve", "inner_bottom_tube"),
        ("outer_top_sleeve", "inner_top_stocking"), ("outer_bottom_sleeve", "inner_bottom_stocking"),
        ("outer_slide_brace", "inner_top_tube"), ("outer_slide_brace", "inner_bottom_tube"),
    ):
        ctx.allow_overlap(outer, body, elem_a=oe, elem_b=ie,
                          reason="Outer slide tube/sleeve is a solid proxy telescoping over the inner tube.")
    if r.slide_style == "plain_collar":
        for i, tube, stock in (
            (0, "inner_top_tube", "inner_top_stocking"),
            (1, "inner_bottom_tube", "inner_bottom_stocking"),
        ):
            for ie in (tube, stock):
                ctx.allow_overlap(outer, body, elem_a=f"slide_collar_{i}", elem_b=ie,
                                  reason="Stocking collar is captured concentrically on its inner slide tube/stocking.")

    # Tuning slide sleeves over the fixed loop legs (S1 L391-404).
    ctx.allow_overlap(tuning, body, elem_a="tuning_lower_sleeve", elem_b="loop_lower_tube",
                      reason="Tuning sleeve is a solid proxy sliding over the fixed loop leg.")
    ctx.allow_overlap(tuning, body, elem_a="tuning_upper_sleeve", elem_b="bell_tube",
                      reason="Tuning sleeve is a solid proxy sliding over the fixed bell tube end.")

    # Captured rotary-valve rotor pins in their casings.
    for i in range(len(_valve_casing_x(r))):
        rotor = model.get_part(f"valve_rotor_{i}")
        ctx.allow_overlap(rotor, body, elem_a="rotor_stem", elem_b=f"valve_casing_{i}",
                          reason="Rotary valve rotor stem is captured in the casing bore.")
        ctx.allow_overlap(rotor, body, elem_a="rotor_hub", elem_b=f"valve_casing_{i}",
                          reason="Rotor hub seats on the casing top.")


def run_trombone_tests(object_model: ArticulatedObject, config: TromboneConfig) -> TestReport:
    r = resolve_config(config)
    s = r.s
    ctx = TestContext(object_model)
    _declare_captured_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    # ---- Structure / identity. ----
    roots = object_model.root_parts()
    ctx.check("single root is the body", len(roots) == 1 and roots[0].name == "body",
              details=f"roots={[p.name for p in roots]}")
    part_names = {p.name for p in object_model.parts}
    ctx.check("core skeleton present", {"body", "outer_slide", "tuning_slide"} <= part_names,
              details=str(sorted(part_names)))
    n_valve = len(_valve_casing_x(r))
    ctx.check("valve rotor count matches attachment",
              sum(1 for p in part_names if p.startswith("valve_rotor_")) == n_valve,
              details=f"attachment={r.valve_attachment} parts={sorted(part_names)}")

    # ---- Joint topology. ----
    slide_j = object_model.get_articulation("outer_slide_travel")
    tuning_j = object_model.get_articulation("tuning_slide_travel")
    ctx.check("hand slide is PRISMATIC +X",
              slide_j.articulation_type == ArticulationType.PRISMATIC and abs(slide_j.axis[0]) > 0.99,
              details=f"type={slide_j.articulation_type} axis={tuple(slide_j.axis)}")
    ctx.check("tuning slide is PRISMATIC -X",
              tuning_j.articulation_type == ArticulationType.PRISMATIC and slide_j.axis[0] > 0
              and tuning_j.axis[0] < 0, details=f"axis={tuple(tuning_j.axis)}")
    sl = slide_j.motion_limits
    ctx.check("hand slide travel realistic (lower=0, retains insertion)",
              sl is not None and sl.lower == 0.0 and sl.upper > 0.30 * s,
              details=f"upper={getattr(sl, 'upper', None)}")
    for i in range(n_valve):
        vj = object_model.get_articulation(f"body_to_valve_rotor_{i}")
        ctx.check(f"valve rotor {i} is REVOLUTE +Z",
                  vj.articulation_type == ArticulationType.REVOLUTE and abs(vj.axis[2]) > 0.99,
                  details=f"type={vj.articulation_type} axis={tuple(vj.axis)}")

    # ---- Category geometry: the hero bell flare (Lathe, far wider than tubing). ----
    bell_aabb = ctx.part_element_world_aabb(object_model.get_part("body"), elem="bell_flare")
    if bell_aabb is not None:
        (bx0, by0, bz0), (bx1, by1, bz1) = bell_aabb
        dz, dy = bz1 - bz0, by1 - by0
        ctx.check("bell flare is a wide hollow flare, far wider than the tubing",
                  dz / 2.0 > 4.0 * TUBE_R_OUTER * s and 0.9 < dz / max(dy, 1e-6) < 1.15,
                  details=f"bell dz={dz:.3f} dy={dy:.3f}")
    else:
        ctx.fail("bell flare aabb", "missing bell_flare element")

    # bell rim clears the top slide tube (BELL_Z risen with rim across ③/⑤).
    ctx.expect_gap(object_model.get_part("body"), object_model.get_part("outer_slide"),
                   axis="z", positive_elem="bell_flare", negative_elem="outer_top_tube",
                   min_gap=0.0003, max_gap=0.06, name="bell rim clears the top slide tube")

    # slide legs parallel, ~72 mm * s spacing.
    top_a = ctx.part_element_world_aabb(object_model.get_part("outer_slide"), elem="outer_top_tube")
    bot_a = ctx.part_element_world_aabb(object_model.get_part("outer_slide"), elem="outer_bottom_tube")
    if top_a and bot_a:
        spacing = (top_a[0][2] + top_a[1][2]) / 2.0 - (bot_a[0][2] + bot_a[1][2]) / 2.0
        ctx.check("slide legs parallel ~72mm*s apart", 0.055 * s <= spacing <= 0.090 * s,
                  details=f"spacing={spacing:.4f}")

    # ---- Rule 5: retained insertion + sampled-pose motion + targeted checks. ----
    body = object_model.get_part("body")
    outer = object_model.get_part("outer_slide")
    tuning = object_model.get_part("tuning_slide")
    ctx.expect_overlap(outer, body, axes="x", elem_a="outer_top_tube", elem_b="inner_top_tube",
                       min_overlap=0.40 * s, name="closed slide keeps deep insertion")
    ctx.expect_overlap(tuning, body, axes="x", elem_a="tuning_lower_sleeve", elem_b="loop_lower_tube",
                       min_overlap=0.03 * s, name="tuning slide seated on the loop legs at rest")

    bow_rest = ctx.part_element_world_aabb(outer, elem="slide_bow")
    with ctx.pose({slide_j: sl.upper}):
        ctx.expect_overlap(outer, body, axes="x", elem_a="outer_top_tube", elem_b="inner_top_tube",
                           min_overlap=0.04 * s, name="extended slide retains insertion")
        bow_ext = ctx.part_element_world_aabb(outer, elem="slide_bow")
    ctx.check("positive slide motion extends the bow forward by the travel",
              bow_rest is not None and bow_ext is not None
              and abs((bow_ext[0][0] - bow_rest[0][0]) - sl.upper) < 0.01 * s,
              details=f"bow rest={bow_rest} ext={bow_ext}")

    crook_rest = ctx.part_element_world_aabb(tuning, elem="tuning_crook")
    with ctx.pose({tuning_j: tuning_j.motion_limits.upper}):
        crook_ext = ctx.part_element_world_aabb(tuning, elem="tuning_crook")
    ctx.check("positive tuning motion pulls the crook rearward",
              crook_rest is not None and crook_ext is not None
              and (crook_rest[0][0] - crook_ext[0][0]) > 0.5 * TUNING_TRAVEL * s,
              details=f"crook rest={crook_rest} ext={crook_ext}")

    for i in range(n_valve):
        vj = object_model.get_articulation(f"body_to_valve_rotor_{i}")
        rotor = object_model.get_part(f"valve_rotor_{i}")
        pad_rest = ctx.part_element_world_aabb(rotor, elem="thumb_paddle")
        with ctx.pose({vj: vj.motion_limits.upper}):
            pad_turn = ctx.part_element_world_aabb(rotor, elem="thumb_paddle")
        if pad_rest and pad_turn:
            moved = max(abs(pad_turn[0][k] - pad_rest[0][k]) for k in range(2))
            ctx.check(f"valve rotor {i} paddle swings", moved > 0.005 * s,
                      details=f"paddle moved {moved:.4f}")

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)

    ctx.check("slot_choices recorded",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))
    return ctx.report()


__all__ = (
    "TromboneConfig",
    "ResolvedTromboneConfig",
    "build_trombone",
    "build_seeded_trombone",
    "config_from_seed",
    "resolve_config",
    "run_trombone_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
