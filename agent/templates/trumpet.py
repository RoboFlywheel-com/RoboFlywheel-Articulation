# SPDX-License-Identifier: Apache-2.0

"""Brass trumpet — modular template.

A lacquered / silver-plated valve trumpet on the 0611__trumpet 5-star pool
(2 origins + 10 slot forks, synced under ``data/records/``). Identity: a grounded
fixed ``trumpet_body`` (Lathe bell flare + tube_from_spline leadpipe/bell-tail +
hollow-shell valve casings & slide sleeves + Torus rim/finger-ring + Lathe
mouthpiece — all fused host visuals) carries N independent valves (piston
PRISMATIC -Z, or rotary REVOLUTE +Z), a main tuning slide (PRISMATIC -X) and a
third-valve slide (PRISMATIC +X), plus an optional slide-control trigger lever
(REVOLUTE +Z).

Structure (pattern = ``mixed`` / parallel-children): every moving part parents to
the body. Four axes swap one layer each (see spec
``articraft_template_authoring/specs_modular_v1/trumpet.md``):

  * ``body_family`` (5, ③ Primary Form Family / Volumetric Envelope): standard /
    pocket / piccolo / herald / bass — the bell flare Lathe母线 (throat/rim/len/exp)
    + machine-length envelope. Carries primary visual diversity.
  * ``valve_mechanism`` (2, ② joint type): piston (PRISMATIC -Z plunger captured in
    casing) / rotary (REVOLUTE +Z rotor + thumb paddle).
  * ``slide_control`` (3, ② joint type + optional child): dual_pull / first_valve_trigger
    / main_slide_trigger — 0 or 1 extra REVOLUTE trigger lever.
  * ``valve_count`` (2 multiplicity): 3 / 4 identical valves, evenly spaced on X.

Global similarity ``s = frame_scale * form_scale`` multiplies every literal dim /
origin / joint origin / travel and every mesh profile coordinate, so bell母线 and
telescoping clearances stay intact at every scale. ``BELL_Z`` is single-sourced
from the per-form bell rim (Contract 3c) so the flare always clears the top run.

Primitive strategy = S1 (001 origin): ``LatheGeometry`` bell/mouthpiece/hollow
shells + ``tube_from_spline_points`` leadpipe/bell-tail/slides + ``TorusGeometry``
rim/rings + ``Cylinder``/``Box`` hardware — no cadquery booleans (≤12 s/seed).

Captured pins (valve stem/rotor in casing, trigger pin in boss) and telescoping
slides (u_tube in sleeve/feed/return) are intentional overlaps: joints **omit**
``MatingContract`` (Rule 2 grandfather) and are declared element-scoped in
``run_trumpet_tests`` (mirroring both origins' run_tests). Water keys are fused
host visuals (Rule 1), not articulated parts.
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
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

BodyFamily = Literal["standard", "pocket", "piccolo", "herald", "bass"]
ValveMechanism = Literal["piston", "rotary"]
SlideControl = Literal["dual_pull", "first_valve_trigger", "main_slide_trigger"]
PaletteStyle = Literal[
    "polished_brass",
    "bright_lacquer",
    "silver_plated",
    "rose_brass",
    "dark_lacquer",
]

BODY_FAMILIES: tuple[BodyFamily, ...] = ("standard", "pocket", "piccolo", "herald", "bass")
VALVE_MECHANISMS: tuple[ValveMechanism, ...] = ("piston", "rotary")
SLIDE_CONTROLS: tuple[SlideControl, ...] = (
    "dual_pull",
    "first_valve_trigger",
    "main_slide_trigger",
)
VALVE_COUNTS: tuple[int, ...] = (3, 4)
VALVE_COUNT_WEIGHTS: tuple[float, ...] = (0.7, 0.3)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "polished_brass",
    "bright_lacquer",
    "silver_plated",
    "rose_brass",
    "dark_lacquer",
)

# Palette roles: brass (main lacquer body/tubing), bell (bright flare/highlight),
# ferrule (dark ferrules / valve casing shading), bright (nickel/silver mouthpiece,
# stems, chrome), accent (pearl/felt button inlay). Every .visual(material=) is
# driven by the sampled palette. polished_brass == S1 origin; bright_lacquer == S2.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "polished_brass": {
        "brass": (0.91, 0.63, 0.13, 1.0),
        "bell": (0.98, 0.74, 0.24, 1.0),
        "ferrule": (0.34, 0.19, 0.055, 1.0),
        "bright": (0.80, 0.82, 0.80, 1.0),
        "accent": (0.90, 0.90, 0.84, 1.0),
    },
    "bright_lacquer": {
        "brass": (0.88, 0.60, 0.16, 1.0),
        "bell": (0.98, 0.76, 0.30, 1.0),
        "ferrule": (0.50, 0.32, 0.09, 1.0),
        "bright": (0.82, 0.84, 0.86, 1.0),
        "accent": (0.12, 0.10, 0.08, 1.0),
    },
    "silver_plated": {
        "brass": (0.82, 0.84, 0.86, 1.0),
        "bell": (0.90, 0.91, 0.93, 1.0),
        "ferrule": (0.72, 0.55, 0.20, 1.0),
        "bright": (0.92, 0.93, 0.94, 1.0),
        "accent": (0.34, 0.36, 0.38, 1.0),
    },
    "rose_brass": {
        "brass": (0.80, 0.52, 0.36, 1.0),
        "bell": (0.88, 0.60, 0.42, 1.0),
        "ferrule": (0.55, 0.33, 0.22, 1.0),
        "bright": (0.82, 0.80, 0.78, 1.0),
        "accent": (0.42, 0.30, 0.24, 1.0),
    },
    "dark_lacquer": {
        "brass": (0.52, 0.40, 0.16, 1.0),
        "bell": (0.66, 0.50, 0.20, 1.0),
        "ferrule": (0.30, 0.22, 0.09, 1.0),
        "bright": (0.62, 0.60, 0.55, 1.0),
        "accent": (0.28, 0.24, 0.16, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Per-family bell母线 + envelope. (throat_r, rim_r, flare_len, flare_exp,
# body_len, form_scale). standard: S1 L75-99; pocket/piccolo/herald/bass: forks.
# ---------------------------------------------------------------------------
BODY_FAMILY_PARAMS: dict[BodyFamily, tuple[float, float, float, float, float, float]] = {
    "standard": (0.0055, 0.058, 0.186, 2.40, 1.00, 1.00),
    "pocket": (0.0055, 0.068, 0.116, 2.00, 0.74, 0.96),
    "piccolo": (0.0060, 0.049, 0.150, 2.60, 0.82, 0.86),
    "herald": (0.0055, 0.060, 0.300, 2.80, 1.30, 1.05),
    "bass": (0.0062, 0.076, 0.240, 2.30, 1.18, 1.12),
}

# ---------------------------------------------------------------------------
# Nominal geometry constants (meters, s == 1), from S1 origin model.py.
# ---------------------------------------------------------------------------
X_RPY = (0.0, math.pi / 2.0, 0.0)  # rotate a +Z cylinder onto +X
Y_RPY = (math.pi / 2.0, 0.0, 0.0)  # rotate a +Z cylinder onto +Y

VALVE_SPACING = 0.030  # S1 valve_xs spacing
VALVE_CENTER_X = 0.024  # S1 cluster center
CASING_OUTER = 0.0110
CASING_INNER = 0.0064
CASING_LEN = 0.090
BELL_Y = 0.013  # bell axis y — offset behind the valve stem plane so the bell
#                 tube clears the piston guides/stems while still touching casings
BELL_THROAT_X = -0.100  # bell throat x (flare opens toward -X from here)
LEADPIPE_Z = 0.057
MOUTH_X0 = 0.298  # S1 mouthpiece x at body_len == 1
BRIDGE_Z = (-0.033, 0.045)  # valve-cluster cross braces (clear of piston travel)

VALVE_TRAVEL = 0.012  # piston stroke (S1 L423)
ROTARY_RANGE = 0.42  # rotary rotor throw (rad)
MAIN_TRAVEL = 0.018  # main tuning slide travel (S1 L488)
THIRD_TRAVEL = 0.020  # third slide travel (S1 L541)
TRIGGER_RANGE = 0.34  # slide-control trigger throw (rad)

FRAME_SCALE_RANGE = (0.90, 1.12)
VALVE_TRAVEL_RANGE = (0.85, 1.0)
SLIDE_EXTENSION_RANGE = (0.80, 1.0)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TrumpetConfig:
    body_family: BodyFamily | None = None
    valve_mechanism: ValveMechanism | None = None
    slide_control: SlideControl | None = None
    valve_count: int | None = None
    palette_style: PaletteStyle = "polished_brass"
    frame_scale: float = 1.0
    valve_travel_scale: float = 1.0
    slide_extension_scale: float = 1.0
    name: str = "trumpet"


@dataclass(frozen=True)
class ResolvedTrumpetConfig:
    body_family: BodyFamily
    valve_mechanism: ValveMechanism
    slide_control: SlideControl
    valve_count: int
    palette_style: PaletteStyle
    s: float  # global similarity (frame_scale * form_scale)
    valve_ext: float  # valve travel scale
    slide_ext: float  # slide extension scale
    name: str
    # derived bell母线 (nominal, pre-scale)
    throat_r: float
    rim_r: float
    flare_len: float
    flare_exp: float
    body_len: float


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> TrumpetConfig:
    rng = random.Random(seed)
    return TrumpetConfig(
        body_family=rng.choice(BODY_FAMILIES),
        valve_mechanism=rng.choice(VALVE_MECHANISMS),
        slide_control=rng.choice(SLIDE_CONTROLS),
        valve_count=rng.choices(VALVE_COUNTS, weights=VALVE_COUNT_WEIGHTS)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        frame_scale=round(rng.uniform(*FRAME_SCALE_RANGE), 4),
        valve_travel_scale=round(rng.uniform(*VALVE_TRAVEL_RANGE), 4),
        slide_extension_scale=round(rng.uniform(*SLIDE_EXTENSION_RANGE), 4),
        name=f"seeded_trumpet_{seed}",
    )


def resolve_config(config: TrumpetConfig | None = None) -> ResolvedTrumpetConfig:
    cfg = config or TrumpetConfig()
    body_family = _pick(cfg.body_family, BODY_FAMILIES)
    throat_r, rim_r, flare_len, flare_exp, body_len, form_scale = BODY_FAMILY_PARAMS[body_family]
    s = _clamp(cfg.frame_scale, *FRAME_SCALE_RANGE) * form_scale
    vc = cfg.valve_count if cfg.valve_count in VALVE_COUNTS else 3
    return ResolvedTrumpetConfig(
        body_family=body_family,
        valve_mechanism=_pick(cfg.valve_mechanism, VALVE_MECHANISMS),
        slide_control=_pick(cfg.slide_control, SLIDE_CONTROLS),
        valve_count=vc,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        s=s,
        valve_ext=_clamp(cfg.valve_travel_scale, *VALVE_TRAVEL_RANGE),
        slide_ext=_clamp(cfg.slide_extension_scale, *SLIDE_EXTENSION_RANGE),
        name=cfg.name or "trumpet",
        throat_r=throat_r,
        rim_r=rim_r,
        flare_len=flare_len,
        flare_exp=flare_exp,
        body_len=body_len,
    )


def slot_choices_for_config(
    config: TrumpetConfig | ResolvedTrumpetConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTrumpetConfig) else resolve_config(config)
    return (
        ("body_family", r.body_family),
        ("valve_mechanism", r.valve_mechanism),
        ("slide_control", r.slide_control),
        ("valve_count", str(r.valve_count)),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Derived quantities (single-sourced; Contract 3c).
# ---------------------------------------------------------------------------
def _valve_x(r: ResolvedTrumpetConfig) -> tuple[float, ...]:
    """Nominal valve-center x positions, evenly spaced about VALVE_CENTER_X."""
    n = r.valve_count
    return tuple(VALVE_CENTER_X + (i - (n - 1) / 2.0) * VALVE_SPACING for i in range(n))


def _main_sx(r: ResolvedTrumpetConfig) -> float:
    """Main slide sleeve x — anchored left of the LEFTMOST valve so the slide
    clears valve 0 even when a 4-valve cluster widens leftward (Contract 3c)."""
    return _valve_x(r)[0] - 0.012


def _bell_z(r: ResolvedTrumpetConfig) -> float:
    """Bell axis height (nominal). Sits above the leadpipe so the flare rim
    clears the top tubing; rises with rim so big-bell families stay clear."""
    return 0.040 + max(0.0, r.rim_r - 0.058) * 0.5


# ---------------------------------------------------------------------------
# Scaled-Origin + geometry helpers (every coordinate × s).
# ---------------------------------------------------------------------------
def _o(s: float, x: float = 0.0, y: float = 0.0, z: float = 0.0, rpy=(0.0, 0.0, 0.0)) -> Origin:
    return Origin(xyz=(x * s, y * s, z * s), rpy=rpy)


def _shell_geom(outer_r: float, inner_r: float, length: float, s: float, segments: int = 40):
    """Hollow revolved shell (LatheGeometry — never a Cylinder), centered on +Z."""
    half = length * 0.5
    return LatheGeometry.from_shell_profiles(
        [(outer_r * s, -half * s), (outer_r * s, half * s)],
        [(inner_r * s, -half * s), (inner_r * s, half * s)],
        segments=segments,
    )


def _tube(points, radius: float, s: float, radial_segments: int = 18):
    return tube_from_spline_points(
        [(x * s, y * s, z * s) for x, y, z in points],
        radius=radius * s,
        samples_per_segment=14,
        radial_segments=radial_segments,
        cap_ends=True,
    )


def _bell_geom(r: ResolvedTrumpetConfig, s: float):
    """Parametric hollow revolved bell flare (LatheGeometry). 母线:
    rad(z) = throat + (rim-throat)*(z/len)^exp, rotated to open toward -X."""
    n = 12
    outer = []
    for i in range(n + 1):
        t = i / n
        z = t * r.flare_len
        rad = r.throat_r + (r.rim_r - r.throat_r) * (t**r.flare_exp)
        outer.append((rad * s, z * s))
    inner = [(max(rad - 0.0013 * s, 0.0035 * s), zz) for rad, zz in outer]
    geom = LatheGeometry.from_shell_profiles(
        outer, inner, segments=72, start_cap="flat", end_cap="round", lip_samples=8
    )
    geom.rotate_y(-math.pi / 2.0)
    return geom


def _mouthpiece_geom(s: float):
    """Solid-lipped silver mouthpiece cup (LatheGeometry). (S1 L154-172)"""
    outer = [
        (0.0040, 0.000), (0.0040, 0.022), (0.0055, 0.032), (0.0070, 0.041), (0.0090, 0.047),
    ]
    inner = [(0.0023, 0.000), (0.0025, 0.022), (0.0042, 0.034), (0.0068, 0.047)]
    geom = LatheGeometry.from_shell_profiles(
        [(rr * s, zz * s) for rr, zz in outer],
        [(rr * s, zz * s) for rr, zz in inner],
        segments=48, lip_samples=6,
    )
    geom.rotate_y(math.pi / 2.0)
    return geom


# ---------------------------------------------------------------------------
# body (root, fixed).  Slot A (body_family) writes bell/leadpipe/mouthpiece.
# ---------------------------------------------------------------------------
def _build_body(model, r: ResolvedTrumpetConfig, mats) -> object:
    s = r.s
    bz = _bell_z(r)
    xs = _valve_x(r)
    x_lo, x_hi = xs[0], xs[-1]
    cluster_cx = (x_lo + x_hi) / 2.0
    body = model.part("trumpet_body")

    # --- valve cluster: hollow casings + caps, unified by cross braces. ---
    casing = mesh_from_geometry(_shell_geom(CASING_OUTER, CASING_INNER, CASING_LEN, s), "valve_casing")
    for i, x in enumerate(xs):
        body.visual(casing, origin=_o(s, x, 0.0, 0.0), material=mats["ferrule"], name=f"valve_casing_{i}", material_class_id="metal.brass_aged")
        body.visual(
            Cylinder(radius=0.0130 * s, length=0.010 * s),
            origin=_o(s, x, 0.0, 0.049), material=mats["brass"], name=f"top_cap_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
        )
        body.visual(
            Cylinder(radius=0.0128 * s, length=0.008 * s),
            origin=_o(s, x, 0.0, -0.048), material=mats["brass"], name=f"bottom_cap_{i}", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
        )
    bridge_len = (x_hi - x_lo) + 0.030
    # Upper brace is offset in +Y so it hugs the casing walls without crossing the
    # central valve-stem column; lower brace stays centered (below all stems).
    for tag, z, by in (("lower", BRIDGE_Z[0], 0.0), ("upper", BRIDGE_Z[1], 0.013)):
        body.visual(
            Cylinder(radius=0.0032 * s, length=bridge_len * s),
            origin=_o(s, cluster_cx, by, z, rpy=X_RPY),
            material=mats["brass"], name=f"valve_bridge_{tag}", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
        )

    # --- bell flare + rim + bell tail (Lathe + Torus + tube sweep). ---
    body.visual(
        mesh_from_geometry(_bell_geom(r, s), "bell_shell"),
        origin=_o(s, BELL_THROAT_X, BELL_Y, bz), material=mats["bell"], name="bell_shell", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    rim = TorusGeometry(r.rim_r * s, 0.0018 * s, radial_segments=16, tubular_segments=64)
    rim.rotate_y(math.pi / 2.0)
    body.visual(
        mesh_from_geometry(rim, "bell_rim"),
        origin=_o(s, BELL_THROAT_X - r.flare_len, BELL_Y, bz),
        material=mats["brass"], name="bell_rim", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    # Bell tube runs back over the valve cluster at the bell-axis height and the
    # BELL_Y offset, so it overlaps the wide casings (connectivity) while clearing
    # the thin valve stems/guides (y-gap) and the low rotary hardware (z-gap).
    body.visual(
        mesh_from_geometry(
            _tube(
                [
                    (BELL_THROAT_X - 0.006, BELL_Y, bz),
                    (BELL_THROAT_X + 0.045, BELL_Y, bz),
                    (cluster_cx, BELL_Y, bz),
                    (x_hi + 0.012, BELL_Y, bz),
                ],
                radius=0.0051, s=s,
            ),
            "bell_tail",
        ),
        material=mats["brass"], name="bell_tail", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )

    # --- leadpipe + mouthpiece (length scaled by body_len). The leadpipe runs
    # over the valves at the front-offset y and dives to the casing left of
    # valve 0 (below the guide travel) so it connects without hitting internals.
    mouth_x = MOUTH_X0 * r.body_len
    body.visual(
        mesh_from_geometry(
            _tube(
                [
                    (mouth_x - 0.012, -0.008, LEADPIPE_Z),
                    (mouth_x * 0.72, -0.008, LEADPIPE_Z),
                    (mouth_x * 0.30, -0.008, LEADPIPE_Z - 0.004),
                    (x_lo + 0.020, -0.008, 0.046),
                    (x_lo - 0.005, -0.008, 0.044),
                    (x_lo - 0.009, -0.008, 0.030),
                ],
                radius=0.0043, s=s,
            ),
            "leadpipe",
        ),
        material=mats["brass"], name="leadpipe", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    body.visual(
        Cylinder(radius=0.0060 * s, length=0.030 * s),
        origin=_o(s, mouth_x - 0.009, -0.008, LEADPIPE_Z, rpy=X_RPY),
        material=mats["bright"], name="mouthpiece_receiver", material_class_id="metal.chrome_polished",
    )
    body.visual(
        mesh_from_geometry(_mouthpiece_geom(s), "mouthpiece"),
        origin=_o(s, mouth_x, -0.008, LEADPIPE_Z), material=mats["bright"], name="mouthpiece", material_class_id="metal.chrome_polished",
    )

    # (bell_tail + leadpipe connect directly to the casings; no floating braces.)

    # --- slide receiver sleeves (hollow) + feed/return connectors. ---
    sleeve = mesh_from_geometry(_shell_geom(0.0063, 0.0047, 0.045, s), "slide_sleeve")
    main_sx = _main_sx(r)
    body.visual(sleeve, origin=_o(s, main_sx, -0.012, -0.020, rpy=X_RPY),
                material=mats["brass"], name="main_slide_sleeve_0", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    body.visual(sleeve, origin=_o(s, main_sx, -0.012, -0.060, rpy=X_RPY),
                material=mats["brass"], name="main_slide_sleeve_1", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    third_sx = x_hi + 0.023
    body.visual(sleeve, origin=_o(s, third_sx, 0.010, 0.004, rpy=X_RPY),
                material=mats["brass"], name="third_slide_sleeve_0", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    body.visual(sleeve, origin=_o(s, third_sx, 0.010, -0.036, rpy=X_RPY),
                material=mats["brass"], name="third_slide_sleeve_1", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    body.visual(
        mesh_from_geometry(
            _tube([(x_lo, -0.002, -0.018), (main_sx + 0.010, -0.008, -0.020),
                   (main_sx - 0.004, -0.012, -0.020)], radius=0.0050, s=s), "main_slide_feed"),
        material=mats["brass"], name="main_slide_feed", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    body.visual(
        mesh_from_geometry(
            _tube([(cluster_cx, -0.002, -0.036), (main_sx + 0.019, -0.008, -0.050),
                   (main_sx - 0.004, -0.012, -0.060)], radius=0.0050, s=s), "main_slide_return"),
        material=mats["brass"], name="main_slide_return", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    body.visual(
        mesh_from_geometry(
            _tube([(x_hi + 0.010, 0.003, 0.005), (x_hi + 0.016, 0.008, 0.004),
                   (third_sx + 0.012, 0.010, 0.004)], radius=0.0050, s=s), "third_slide_feed"),
        material=mats["brass"], name="third_slide_feed", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    body.visual(
        mesh_from_geometry(
            _tube([(x_hi + 0.010, 0.003, -0.025), (x_hi + 0.016, 0.008, -0.036),
                   (third_sx + 0.012, 0.010, -0.036)], radius=0.0050, s=s), "third_slide_return"),
        material=mats["brass"], name="third_slide_return", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )

    # --- finger ring + stem (near left valve) and pinky hook (near right). ---
    # Ring center placed so its +x tube point sits at the stem's lower end; the
    # stem's upper end is embedded in valve-0 casing (guaranteed contact chain).
    ring_r = 0.0125
    ring_stem_x = x_lo - 0.010  # clear of the (wider) rotary stem radius at valve 0
    ring_x = ring_stem_x - ring_r
    ring = TorusGeometry(ring_r * s, 0.0025 * s, radial_segments=14, tubular_segments=40)
    ring.rotate_x(math.pi / 2.0)
    body.visual(
        mesh_from_geometry(ring, "finger_ring"),
        origin=_o(s, ring_x, -0.023, 0.008), material=mats["brass"], name="finger_ring", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    body.visual(
        Cylinder(radius=0.0028 * s, length=0.026 * s),
        origin=_o(s, ring_stem_x, -0.010, 0.008, rpy=Y_RPY),
        material=mats["brass"], name="finger_ring_stem", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    # Pinky hook roots on the upper-bridge tip (past the last valve column) and
    # hangs out toward +X, so it never crosses a valve's tall stem/rotor.
    body.visual(
        mesh_from_geometry(
            _tube([(x_hi + 0.013, 0.0, 0.045), (x_hi + 0.020, 0.0, 0.038),
                   (x_hi + 0.024, 0.0, 0.026), (x_hi + 0.024, 0.0, 0.012),
                   (x_hi + 0.037, 0.0, 0.011), (x_hi + 0.042, 0.0, 0.024)],
                  radius=0.0026, s=s, radial_segments=14), "pinky_hook"),
        material=mats["brass"], name="pinky_hook", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    return body


# ---------------------------------------------------------------------------
# valves (Slot B × valve_count).  piston PRISMATIC -Z or rotary REVOLUTE +Z.
# ---------------------------------------------------------------------------
def _build_piston_valve(model, r, mats, i: int):
    """Plunger captured in casing: stem + guide_piston + button (S1 L390-415).
    Local origin = joint at casing top; visuals extend downward into the bore."""
    s = r.s
    valve = model.part(f"valve_{i}")
    valve.visual(Cylinder(radius=0.0030 * s, length=0.052 * s), origin=_o(s, 0.0, 0.0, -0.026),
                 material=mats["bright"], name="stem", material_class_id="metal.chrome_polished")
    valve.visual(Cylinder(radius=0.00642 * s, length=0.006 * s), origin=_o(s, 0.0, 0.0, -0.049),
                 material=mats["bright"], name="guide_piston", material_class_id="metal.chrome_polished")
    valve.visual(Cylinder(radius=0.0068 * s, length=0.004 * s), origin=_o(s, 0.0, 0.0, 0.002),
                 material=mats["brass"], name="button_base", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    valve.visual(Cylinder(radius=0.0058 * s, length=0.0025 * s), origin=_o(s, 0.0, 0.0, 0.0051),
                 material=mats["accent"], name="button_top", material_class_id="plastic.opaque_glossy_molded")
    return valve


def _build_rotary_valve(model, r, mats, i: int):
    """Rotary rotor about +Z: stem in bore + hub + thumb paddle (S8 rotary fork).
    Local origin = casing centerline; the +Z revolute origin lands on the axis."""
    s = r.s
    valve = model.part(f"valve_{i}")
    # Rotor spindle in the casing bore; hub + finger lever at the casing top; the
    # thumb paddle sits fully OUTBOARD (+Y) beyond the casing. The lever exits
    # through the casing top wall (a captured-linkage overlap, declared in tests).
    valve.visual(Cylinder(radius=0.0058 * s, length=0.052 * s), origin=_o(s, 0.0, 0.0, 0.012),
                 material=mats["bright"], name="stem", material_class_id="metal.chrome_polished")
    valve.visual(Cylinder(radius=0.0100 * s, length=0.006 * s), origin=_o(s, 0.0, 0.0, 0.026),
                 material=mats["accent"], name="guide_piston", material_class_id="plastic.opaque_glossy_molded")  # rotor hub (shared overlap decl name)
    valve.visual(Box((0.006 * s, 0.030 * s, 0.005 * s)), origin=_o(s, 0.0, 0.022, 0.026),
                 material=mats["bright"], name="trigger_lever", material_class_id="metal.chrome_polished")
    valve.visual(Cylinder(radius=0.0075 * s, length=0.004 * s), origin=_o(s, 0.0, 0.041, 0.026),
                 material=mats["brass"], name="button_top", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    return valve


# ---------------------------------------------------------------------------
# slides (Slot C).  main PRISMATIC -X + third PRISMATIC +X + optional trigger.
# ---------------------------------------------------------------------------
def _water_key(host, tag, x, y, z, s, mats):
    """Fused spit-key: saddle straddling the tube at (x,y,z) + lever + touch-cork
    (host visuals, Rule 1). Saddle overlaps the carrying tube for support."""
    host.visual(Cylinder(radius=0.0050 * s, length=0.009 * s), origin=_o(s, x, y, z),
                material=mats["ferrule"], name=f"water_key_saddle_{tag}", material_class_id="metal.brass_aged")
    host.visual(Box((0.016 * s, 0.004 * s, 0.004 * s)), origin=_o(s, x - 0.011, y, z + 0.004),
                material=mats["bright"], name=f"water_key_lever_{tag}", material_class_id="metal.chrome_polished")
    host.visual(Cylinder(radius=0.0035 * s, length=0.003 * s), origin=_o(s, x - 0.002, y, z + 0.004),
                material=mats["accent"], name=f"water_key_cork_{tag}", material_class_id="organic.cork")


def _build_main_slide(model, r, mats):
    s = r.s
    cluster_cx = (_valve_x(r)[0] + _valve_x(r)[-1]) / 2.0
    main = model.part("main_slide")
    main.visual(
        mesh_from_geometry(
            _tube([(0.022, 0.0, 0.0), (-0.010, 0.0, 0.0), (-0.040, 0.0, -0.004),
                   (-0.052, 0.0, -0.018), (-0.052, 0.0, -0.025), (-0.040, 0.0, -0.037),
                   (-0.010, 0.0, -0.040), (0.022, 0.0, -0.040)], radius=0.0040, s=s), "u_tube"),
        material=mats["brass"], name="u_tube", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    for tag, z in (("0", 0.0), ("1", -0.040)):
        main.visual(Cylinder(radius=0.0055 * s, length=0.010 * s),
                    origin=_o(s, -0.006, 0.0, z, rpy=X_RPY), material=mats["bright"], name=f"ferrule_{tag}", material_class_id="metal.chrome_polished")
    _water_key(main, "main", -0.030, 0.0, 0.0, s, mats)
    return main, cluster_cx


def _build_third_slide(model, r, mats):
    s = r.s
    third = model.part("third_slide")
    third.visual(
        mesh_from_geometry(
            _tube([(-0.025, 0.0, 0.0), (0.020, 0.0, 0.0), (0.062, 0.0, -0.004),
                   (0.078, 0.0, -0.017), (0.078, 0.0, -0.024), (0.062, 0.0, -0.037),
                   (0.020, 0.0, -0.040), (-0.025, 0.0, -0.040)], radius=0.0040, s=s), "u_tube"),
        material=mats["brass"], name="u_tube", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"),
    )
    for tag, z in (("0", 0.0), ("1", -0.040)):
        third.visual(Cylinder(radius=0.0055 * s, length=0.010 * s),
                     origin=_o(s, 0.014, 0.0, z, rpy=X_RPY), material=mats["bright"], name=f"ferrule_{tag}", material_class_id="metal.chrome_polished")
    _water_key(third, "third", 0.030, 0.0, 0.0, s, mats)
    return third


def _build_trigger(model, r, mats, name: str):
    """Sprung REVOLUTE trigger lever (pivots about +Z): pivot pin captured in a
    body boss + lever + touch paddle reaching forward (-Y, clear of all tubing).
    (S10/S11 slide-control forks.) Local origin = pivot centerline (+Z axis)."""
    s = r.s
    trig = model.part(name)
    trig.visual(Cylinder(radius=0.0028 * s, length=0.014 * s), origin=_o(s, 0.0, 0.0, 0.0),
                material=mats["bright"], name="pivot_pin", material_class_id="metal.chrome_polished")
    trig.visual(Box((0.004 * s, 0.022 * s, 0.004 * s)), origin=_o(s, 0.0, -0.012, 0.0),
                material=mats["brass"], name="lever", material_class_id=("metal.brass_polished" if r.palette_style in {"polished_brass", "bright_lacquer", "silver_plated", "rose_brass"} else "metal.brass_aged"))
    trig.visual(Cylinder(radius=0.0050 * s, length=0.004 * s), origin=_o(s, 0.0, -0.024, 0.0),
                material=mats["accent"], name="touch_paddle", material_class_id="plastic.opaque_glossy_molded")
    return trig


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_trumpet(
    config: TrumpetConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    s = r.s
    xs = _valve_x(r)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"tpt_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats)

    # --- valves (parallel children of body). ---
    for i, x in enumerate(xs):
        if r.valve_mechanism == "piston":
            valve = _build_piston_valve(model, r, mats, i)
            model.articulation(
                f"valve_{i}_press", ArticulationType.PRISMATIC, parent=body, child=valve,
                origin=_o(s, x, 0.0, 0.086), axis=(0.0, 0.0, -1.0),
                motion_limits=MotionLimits(effort=18.0, velocity=0.20, lower=0.0,
                                           upper=VALVE_TRAVEL * s * r.valve_ext),
            )
        else:
            valve = _build_rotary_valve(model, r, mats, i)
            model.articulation(
                f"valve_{i}_turn", ArticulationType.REVOLUTE, parent=body, child=valve,
                origin=_o(s, x, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
                motion_limits=MotionLimits(effort=4.0, velocity=5.0, lower=0.0,
                                           upper=ROTARY_RANGE * r.valve_ext),
            )

    # --- main + third tuning slides (parallel children of body). ---
    main, cluster_cx = _build_main_slide(model, r, mats)
    main_sx = _main_sx(r)
    model.articulation(
        "main_slide_pull", ArticulationType.PRISMATIC, parent=body, child=main,
        origin=_o(s, main_sx + 0.002, -0.012, -0.020), axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.08, lower=0.0,
                                   upper=MAIN_TRAVEL * s * r.slide_ext),
    )
    third = _build_third_slide(model, r, mats)
    third_sx = xs[-1] + 0.023
    model.articulation(
        "third_slide_pull", ArticulationType.PRISMATIC, parent=body, child=third,
        origin=_o(s, third_sx + 0.015, 0.010, 0.004), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=24.0, velocity=0.10, lower=0.0,
                                   upper=THIRD_TRAVEL * s * r.slide_ext),
    )

    # --- optional slide-control trigger lever (REVOLUTE +Z child of body). ---
    if r.slide_control != "dual_pull":
        # Boss overlaps a guaranteed body element (finger-ring stem near valve 0,
        # or the main slide sleeve) and the +Z pivot lands on its centerline.
        if r.slide_control == "first_valve_trigger":
            name, bx, by, bz_ = "first_valve_trigger", xs[0] - 0.006, -0.015, 0.008
        else:  # main_slide_trigger
            name, bx, by, bz_ = "main_slide_trigger", main_sx, -0.019, -0.020
        body.visual(
            Cylinder(radius=0.0050 * s, length=0.014 * s),
            origin=_o(s, bx, by, bz_), material=mats["ferrule"],
            name=f"{name}_boss", material_class_id="metal.brass_aged",
        )
        trig = _build_trigger(model, r, mats, name)
        model.articulation(
            f"operate_{name}", ArticulationType.REVOLUTE, parent=body, child=trig,
            origin=_o(s, bx, by, bz_), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=TRIGGER_RANGE),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_trumpet(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_trumpet(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _trigger_name(r: ResolvedTrumpetConfig) -> str | None:
    if r.slide_control == "first_valve_trigger":
        return "first_valve_trigger"
    if r.slide_control == "main_slide_trigger":
        return "main_slide_trigger"
    return None


def _declare_captured_overlaps(ctx, model, r) -> None:
    body = model.get_part("trumpet_body")
    main = model.get_part("main_slide")
    third = model.get_part("third_slide")

    # Each valve plunger/rotor stem + guide is captured in its casing bore and
    # passes through the top-cap bore (both are guide surfaces of the mechanism).
    for i in range(r.valve_count):
        valve = model.get_part(f"valve_{i}")
        for be in (f"valve_casing_{i}", f"top_cap_{i}"):
            for elem in ("stem", "guide_piston"):
                ctx.allow_overlap(body, valve, elem_a=be, elem_b=elem,
                                  reason="Valve stem/guide is captured in the casing/top-cap bore.")
        if r.valve_mechanism == "rotary":
            # The rotor's finger lever exits through the casing-top wall slot.
            ctx.allow_overlap(body, valve, elem_a=f"valve_casing_{i}", elem_b="trigger_lever",
                              reason="Rotary rotor lever exits through the casing-top wall slot.")
            ctx.allow_overlap(body, valve, elem_a=f"top_cap_{i}", elem_b="trigger_lever",
                              reason="Rotary rotor lever exits over the top cap.")

    # Telescoping main slide: u_tube legs + ferrules retained in fixed sleeves/branches.
    for se in ("u_tube", "ferrule_0", "ferrule_1"):
        for elem in ("main_slide_sleeve_0", "main_slide_sleeve_1", "main_slide_feed", "main_slide_return"):
            ctx.allow_overlap(main, body, elem_a=se, elem_b=elem,
                              reason="Main slide leg/ferrule is a solid proxy telescoping in the fixed sleeve/branch.")
        for elem in ("third_slide_sleeve_0", "third_slide_sleeve_1", "third_slide_feed", "third_slide_return"):
            ctx.allow_overlap(third, body, elem_a=se, elem_b=elem,
                              reason="Third slide leg/ferrule is a solid proxy telescoping in the fixed sleeve/branch.")

    # Optional trigger pivot pin captured in the body boss.
    tname = _trigger_name(r)
    if tname is not None:
        trig = model.get_part(tname)
        ctx.allow_overlap(trig, body, elem_a="pivot_pin", elem_b=f"{tname}_boss",
                          reason="Trigger pivot pin is captured in its bearing boss.")


def run_trumpet_tests(object_model: ArticulatedObject, config: TrumpetConfig) -> TestReport:
    r = resolve_config(config)
    s = r.s
    ctx = TestContext(object_model)
    _declare_captured_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)

    # ---- Structure / identity. ----
    roots = object_model.root_parts()
    ctx.check("single root is trumpet_body", len(roots) == 1 and roots[0].name == "trumpet_body",
              details=f"roots={[p.name for p in roots]}")
    part_names = {p.name for p in object_model.parts}
    ctx.check("core skeleton present",
              {"trumpet_body", "main_slide", "third_slide"} <= part_names,
              details=str(sorted(part_names)))
    n_valve = sum(1 for p in part_names if p.startswith("valve_"))
    ctx.check("valve count matches (>=3, bugle boundary)",
              n_valve == r.valve_count and n_valve >= 3,
              details=f"valve_count={r.valve_count} parts={sorted(part_names)}")

    # ---- Joint topology per mechanism (② axis both types must appear). ----
    for i in range(r.valve_count):
        if r.valve_mechanism == "piston":
            vj = object_model.get_articulation(f"valve_{i}_press")
            ctx.check(f"valve {i} piston is PRISMATIC -Z",
                      vj.articulation_type == ArticulationType.PRISMATIC and vj.axis[2] < -0.99,
                      details=f"type={vj.articulation_type} axis={tuple(vj.axis)}")
        else:
            vj = object_model.get_articulation(f"valve_{i}_turn")
            ctx.check(f"valve {i} rotary is REVOLUTE +Z",
                      vj.articulation_type == ArticulationType.REVOLUTE and vj.axis[2] > 0.99,
                      details=f"type={vj.articulation_type} axis={tuple(vj.axis)}")
    mj = object_model.get_articulation("main_slide_pull")
    tj = object_model.get_articulation("third_slide_pull")
    ctx.check("main slide PRISMATIC -X, third slide PRISMATIC +X",
              mj.articulation_type == ArticulationType.PRISMATIC and mj.axis[0] < -0.99
              and tj.articulation_type == ArticulationType.PRISMATIC and tj.axis[0] > 0.99,
              details=f"main={tuple(mj.axis)} third={tuple(tj.axis)}")
    tname = _trigger_name(r)
    ctx.check("trigger present iff slide_control is a trigger variant",
              (tname in part_names) == (r.slide_control != "dual_pull"),
              details=f"slide_control={r.slide_control} tname={tname}")

    # ---- Category geometry: the hero bell flare (Lathe, far wider than tubing). ----
    bell_aabb = ctx.part_element_world_aabb(object_model.get_part("trumpet_body"), elem="bell_shell")
    if bell_aabb is not None:
        (bx0, by0, bz0), (bx1, by1, bz1) = bell_aabb
        dz, dy = bz1 - bz0, by1 - by0
        ctx.check("bell flare is a wide hollow flare, far wider than the tubing",
                  min(dz, dy) > 4.0 * CASING_INNER * s,
                  details=f"bell dz={dz:.3f} dy={dy:.3f} rim_r={r.rim_r}")
    else:
        ctx.fail("bell flare aabb", "missing bell_shell element")

    body_aabb = ctx.part_world_aabb(object_model.get_part("trumpet_body"))
    if body_aabb is not None:
        length = body_aabb[1][0] - body_aabb[0][0]
        ctx.check("full instrument length in a compact trumpet envelope",
                  0.28 * s < length < 0.95,
                  details=f"length={length:.3f} body_family={r.body_family}")

    # ---- Rule 5: retained insertion + targeted motion + sampled poses. ----
    body = object_model.get_part("trumpet_body")
    main = object_model.get_part("main_slide")
    third = object_model.get_part("third_slide")
    ctx.expect_overlap(main, body, axes="x", elem_a="u_tube", elem_b="main_slide_return",
                       min_overlap=0.006 * s, name="main slide retained in return at rest")
    ctx.expect_overlap(third, body, axes="x", elem_a="u_tube", elem_b="third_slide_return",
                       min_overlap=0.006 * s, name="third slide retained in return at rest")

    main_rest = ctx.part_world_position(main)
    with ctx.pose({mj: mj.motion_limits.upper}):
        main_pulled = ctx.part_world_position(main)
        ctx.expect_overlap(main, body, axes="x", elem_a="u_tube", elem_b="main_slide_return",
                           min_overlap=0.002 * s, name="main slide retains insertion at full pull")
    ctx.check("main tuning slide pulls toward -X",
              main_rest is not None and main_pulled is not None
              and main_pulled[0] < main_rest[0] - 0.5 * MAIN_TRAVEL * s * r.slide_ext,
              details=f"rest={main_rest} pulled={main_pulled}")

    third_rest = ctx.part_world_position(third)
    with ctx.pose({tj: tj.motion_limits.upper}):
        third_pulled = ctx.part_world_position(third)
    ctx.check("third slide pulls toward +X",
              third_rest is not None and third_pulled is not None
              and third_pulled[0] > third_rest[0] + 0.5 * THIRD_TRAVEL * s * r.slide_ext,
              details=f"rest={third_rest} pulled={third_pulled}")

    for i in range(r.valve_count):
        valve = object_model.get_part(f"valve_{i}")
        if r.valve_mechanism == "piston":
            vj = object_model.get_articulation(f"valve_{i}_press")
            rest = ctx.part_world_position(valve)
            with ctx.pose({vj: vj.motion_limits.upper}):
                pressed = ctx.part_world_position(valve)
            ctx.check(f"valve {i} depresses downward",
                      rest is not None and pressed is not None
                      and pressed[2] < rest[2] - 0.6 * VALVE_TRAVEL * s * r.valve_ext,
                      details=f"rest={rest} pressed={pressed}")
        else:
            vj = object_model.get_articulation(f"valve_{i}_turn")
            pad_rest = ctx.part_element_world_aabb(valve, elem="button_top")
            with ctx.pose({vj: vj.motion_limits.upper}):
                pad_turn = ctx.part_element_world_aabb(valve, elem="button_top")
            if pad_rest and pad_turn:
                moved = max(abs(pad_turn[0][k] - pad_rest[0][k]) for k in range(2))
                ctx.check(f"valve {i} rotor paddle swings", moved > 0.004 * s,
                          details=f"paddle moved {moved:.4f}")

    if tname is not None:
        trj = object_model.get_articulation(f"operate_{tname}")
        trig = object_model.get_part(tname)
        pad_rest = ctx.part_element_world_aabb(trig, elem="touch_paddle")
        with ctx.pose({trj: trj.motion_limits.upper}):
            pad_turn = ctx.part_element_world_aabb(trig, elem="touch_paddle")
        if pad_rest and pad_turn:
            moved = max(abs(pad_turn[0][k] - pad_rest[0][k]) for k in range(2))
            ctx.check("trigger lever swings", moved > 0.004 * s, details=f"moved {moved:.4f}")

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    ctx.check("slot_choices recorded",
              tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
              details=str(object_model.meta.get("slot_choices")))
    return ctx.report()


__all__ = (
    "TrumpetConfig",
    "ResolvedTrumpetConfig",
    "build_trumpet",
    "build_seeded_trumpet",
    "config_from_seed",
    "resolve_config",
    "run_trumpet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
