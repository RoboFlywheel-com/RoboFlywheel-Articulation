# SPDX-License-Identifier: Apache-2.0

"""Pair-of-pliers modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Other_Other_pliers.md`` and the
``picture/Other/pliers`` 5-star sample pool (2 parents + 6 single-axis fork
variants: P1 flush_cut_snips / P2 lineman_pliers + needle_nose /
locking_vise_grip / looped_bow / cushioned_ergonomic / slip_joint /
tongue_and_groove).

Structure (pattern = ``mixed``): two mirrored **forged steel halves** crossing
about a central rivet. ``plier_half_0`` (root, jaw on +Y) and ``plier_half_1``
(mirror, jaw on -Y) rotate relative to each other about the central rivet
(REVOLUTE, axis -Z, origin at the world origin where the two hubs half-lap). The
jaws point +X and the handles sweep to -X spreading in +/-Y. Each half is
authored in a pivot-at-origin local frame and mirrored by ``s = +/-1``.

Slots:

  * ``jaw_function`` (4): flush_cutter (compact tapered cutting blade) /
    combination_grip (squared serrated nose + pipe-grip recess + wire cutter) /
    needle_nose (long lofted taper) / locking_vise_grip (curved C jaw + a third
    ``toggle_link`` part on a second over-center REVOLUTE ``toggle``).
  * ``handle_form`` (3): straight_dipped (over-molded grip loft + inlay) /
    looped_bow (steel neck arm + a closed-loop torus finger ring) /
    cushioned_ergonomic (thicker finger-ridged grip).
  * ``pivot_mechanism`` (3): fixed_rivet (2-part chain, rivet inline on half_0,
    1 REVOLUTE) / slip_joint / tongue_and_groove (each a 3-part chain inserting
    a real ``pivot_carriage`` sliding part on a PRISMATIC ``slot_slide`` plus a
    REVOLUTE ``pivot``).
  * ``groove_count`` **multiplicity** (2-7, conditional on slip_joint /
    tongue_and_groove only): N detent / channel-lock grooves emitted along the
    shank by a shared helper; the PRISMATIC travel derives from N. Encoded in
    slot_choices as ``groove_n{N}``; absent under fixed_rivet.

The rivet seam/boss/head is always an inline visual (of half_0 for fixed_rivet
or of the carriage for the slip mechanisms) — never a FIXED decoration part. The
pivot is captured-pin geometry (the rivet shaft passes through the moving hub
lap), so its joint omits ``MatingContract`` (grandfathered) and is guarded by
the flat articulation-origin baseline + a broad ``allow_overlap`` between the
two halves (mirroring P2's rivet-shaft treatment).
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
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

JawFunction = Literal["flush_cutter", "combination_grip", "needle_nose", "locking_vise_grip"]
HandleForm = Literal["straight_dipped", "looped_bow", "cushioned_ergonomic"]
PivotMechanism = Literal["fixed_rivet", "slip_joint", "tongue_and_groove"]
PaletteStyle = Literal[
    "steel_red_dipped",
    "black_chrome",
    "gunmetal_yellow",
    "polished_blue",
    "chrome_natural",
]

JAW_FUNCTIONS: tuple[JawFunction, ...] = (
    "flush_cutter",
    "combination_grip",
    "needle_nose",
    "locking_vise_grip",
)
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "straight_dipped",
    "looped_bow",
    "cushioned_ergonomic",
)
PIVOT_MECHANISMS: tuple[PivotMechanism, ...] = (
    "fixed_rivet",
    "slip_joint",
    "tongue_and_groove",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_red_dipped",
    "black_chrome",
    "gunmetal_yellow",
    "polished_blue",
    "chrome_natural",
)

# groove_count multiplicity domain (spec §Multiplicity); conditional on slip.
N_GROOVE_MIN, N_GROOVE_MAX = 2, 7

# A slip mechanism is present for these pivot choices.
SLIP_MECHANISMS: tuple[PivotMechanism, ...] = ("slip_joint", "tongue_and_groove")

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_red_dipped": {
        "jaw": (0.80, 0.81, 0.84, 1.0),
        "forged": (0.66, 0.67, 0.70, 1.0),
        "brushed": (0.61, 0.62, 0.65, 1.0),
        "seam": (0.45, 0.46, 0.48, 1.0),
        "grip": (0.08, 0.08, 0.09, 1.0),
        "inlay": (0.80, 0.09, 0.11, 1.0),
        "accent": (0.30, 0.31, 0.33, 1.0),
    },
    "black_chrome": {
        "jaw": (0.20, 0.21, 0.23, 1.0),
        "forged": (0.14, 0.14, 0.16, 1.0),
        "brushed": (0.72, 0.74, 0.77, 1.0),
        "seam": (0.30, 0.31, 0.33, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "inlay": (0.74, 0.76, 0.79, 1.0),
        "accent": (0.55, 0.56, 0.58, 1.0),
    },
    "gunmetal_yellow": {
        "jaw": (0.52, 0.54, 0.57, 1.0),
        "forged": (0.40, 0.41, 0.44, 1.0),
        "brushed": (0.48, 0.49, 0.52, 1.0),
        "seam": (0.33, 0.34, 0.36, 1.0),
        "grip": (0.93, 0.78, 0.10, 1.0),
        "inlay": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.20, 0.20, 0.22, 1.0),
    },
    "polished_blue": {
        "jaw": (0.78, 0.80, 0.84, 1.0),
        "forged": (0.62, 0.64, 0.68, 1.0),
        "brushed": (0.58, 0.60, 0.64, 1.0),
        "seam": (0.42, 0.44, 0.47, 1.0),
        "grip": (0.10, 0.24, 0.55, 1.0),
        "inlay": (0.86, 0.88, 0.92, 1.0),
        "accent": (0.06, 0.14, 0.34, 1.0),
    },
    "chrome_natural": {
        "jaw": (0.84, 0.85, 0.88, 1.0),
        "forged": (0.70, 0.71, 0.74, 1.0),
        "brushed": (0.66, 0.67, 0.70, 1.0),
        "seam": (0.48, 0.49, 0.51, 1.0),
        "grip": (0.16, 0.17, 0.19, 1.0),
        "inlay": (0.74, 0.16, 0.14, 1.0),
        "accent": (0.40, 0.41, 0.43, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters); from P2 (lineman) baseline + variants.
# The tool lies in XY with Z the thickness/pivot axis. The rivet is at origin.
# ---------------------------------------------------------------------------
HALF_T = 0.009          # half thickness of each forged plate (full plate 0.018)
LAP_R = 0.016           # half-lap joint disc radius at the pivot
HUB_R = 0.015           # forged hub radius around the rivet
BOSS_R = 0.0125         # rivet boss radius (~0.025 m diameter)
BOSS_H = 0.0030
SEAM_R = 0.0132         # visible circular seam ring under the boss cap
SEAM_H = 0.0006
RIVET_R = 0.004         # rivet shaft captured through the moving half's lap
EPS = 0.0001            # lap clearance so the stacked halves do not penetrate
JAW_FACE = 0.0003       # closed jaw inner faces sit at y = +/-JAW_FACE
NOSE_X = 0.075          # blunt squared nose tip
_OPEN_LIMIT = math.radians(30.0)

TANG_HALF_W = 0.004     # steel handle tang half width in plan

# Steel handle tang centerline in the tool plane (jaw-on-+Y half).
TANG_PTS = [
    (-0.010, -0.004),
    (-0.030, -0.011),
    (-0.070, -0.019),
    (-0.100, -0.024),
    (-0.118, -0.026),
]
CENTERLINE = TANG_PTS + [(-0.131, -0.0274)]

# Grip loft stations: (x, half_width_y, half_height_z) — straight_dipped baseline.
GRIP_SECTIONS = [
    (-0.032, 0.0100, 0.0130),
    (-0.040, 0.0080, 0.0110),
    (-0.060, 0.0078, 0.0108),
    (-0.085, 0.0080, 0.0112),
    (-0.105, 0.0086, 0.0118),
    (-0.120, 0.0088, 0.0120),
    (-0.128, 0.0062, 0.0086),
    (-0.131, 0.0028, 0.0040),
]
# Thicker ergonomic grip stations (cushioned_ergonomic): half-width > 0.010,
# half-height > 0.014 across the body so it clears the 28 mm / 20 mm thresholds.
GRIP_SECTIONS_CUSHION = [
    (-0.032, 0.0118, 0.0150),
    (-0.040, 0.0108, 0.0148),
    (-0.060, 0.0112, 0.0150),
    (-0.085, 0.0116, 0.0152),
    (-0.105, 0.0118, 0.0150),
    (-0.120, 0.0114, 0.0146),
    (-0.128, 0.0080, 0.0104),
    (-0.131, 0.0034, 0.0048),
]

INLAY_XS = [-0.036, -0.055, -0.075, -0.095, -0.112, -0.118]
INLAY_HALF_H = 0.0075
INLAY_Z_CENTER = 0.006

# Needle-nose loft stations: (x, half_width_y, half_height_z).
NEEDLE_STATIONS = [
    (0.010, 0.0130, HALF_T),
    (0.018, 0.0115, HALF_T),
    (0.028, 0.0095, HALF_T * 0.97),
    (0.040, 0.0072, HALF_T * 0.88),
    (0.052, 0.0050, HALF_T * 0.74),
    (0.062, 0.0032, HALF_T * 0.56),
    (0.070, 0.0018, HALF_T * 0.38),
    (0.075, 0.0008, HALF_T * 0.22),
]

# Looped-bow handle (V3): steel neck arm + closed-loop torus finger ring.
BOW_RING_R = 0.013      # major radius of the finger ring torus
BOW_TUBE_R = 0.003      # tube cross-section radius
BOW_RING_CX = -0.112    # ring center X in local half frame
BOW_RING_CY_BASE = -0.026  # ring center Y at the tang end (before mirror)

# Slip-joint mechanism (V5).
SLOT_LENGTH = 0.020     # capsule length of the elongated slot
SLOT_WIDTH = 0.009      # slot width (capsule diameter)
_SLOT_TRAVEL = 0.010    # nominal prismatic travel
SLOT_HUB_MARGIN = 0.002 # keep the shaft + slot capsule clear of the hub edge
# Largest prismatic travel the fixed hub slot can carry while the captured rivet
# shaft (radius RIVET_R) stays fully inside the hub disc (radius HUB_R). The T&G
# travel derives from N and is clamped to this so large N never slides the shaft
# out of the slot / past the hub edge.
MAX_SLOT_TRAVEL = 2.0 * (HUB_R - RIVET_R - SLOT_HUB_MARGIN)  # ~0.018 m

# Tongue-and-groove channel-lock (V6).
GROOVE_SPACING = 0.004  # center-to-center groove spacing along X
GROOVE_X_START = -0.022 # first groove center X (beyond the lap disc, full shank)
GROOVE_TRACK_Y = -0.006 # groove track centerline Y

# Locking vise-grip (V2) toggle hardware.
TOGGLE_PIVOT_X = -0.080
TOGGLE_RANGE = math.radians(25.0)
TOGGLE_LINK_LEN = 0.040


@dataclass(frozen=True)
class PliersConfig:
    jaw_function: JawFunction | None = None
    handle_form: HandleForm | None = None
    pivot_mechanism: PivotMechanism | None = None
    groove_count: int | None = None
    palette_style: PaletteStyle = "steel_red_dipped"
    overall_len_scale: float = 1.0
    jaw_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    slide_travel_scale: float = 1.0
    name: str = "pliers"


@dataclass(frozen=True)
class ResolvedPliersConfig:
    jaw_function: JawFunction
    handle_form: HandleForm
    pivot_mechanism: PivotMechanism
    groove_count: int          # meaningful only under slip mechanisms
    palette_style: PaletteStyle
    overall_len_scale: float
    jaw_len_scale: float
    grip_girth_scale: float
    open_angle: float
    slot_travel: float
    name: str

    @property
    def is_slip(self) -> bool:
        return self.pivot_mechanism in SLIP_MECHANISMS

    @property
    def is_locking(self) -> bool:
        return self.jaw_function == "locking_vise_grip"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PliersConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling (spec §9): combination jaw / straight grip /
    # fixed rivet are the common case; small groove counts most common.
    jaw = rng.choices(JAW_FUNCTIONS, weights=[3, 5, 3, 2], k=1)[0]
    handle = rng.choices(HANDLE_FORMS, weights=[6, 3, 3], k=1)[0]
    pivot = rng.choices(PIVOT_MECHANISMS, weights=[5, 3, 3], k=1)[0]
    # locking_vise_grip is a fixed-rivet-only tool (its over-center toggle needs a
    # rigid pivot); it can never combine with a sliding slip pivot.
    if jaw == "locking_vise_grip":
        pivot = "fixed_rivet"
    n_groove = rng.choices(
        [2, 3, 4, 5, 6, 7], weights=[3, 5, 5, 6, 2, 1], k=1
    )[0]
    return PliersConfig(
        jaw_function=jaw,
        handle_form=handle,
        pivot_mechanism=pivot,
        groove_count=n_groove,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.85, 1.20), 4),
        jaw_len_scale=round(rng.uniform(0.90, 1.15), 4),
        grip_girth_scale=round(rng.uniform(0.90, 1.15), 4),
        open_angle_scale=round(rng.uniform(0.80, 1.20), 4),
        slide_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pliers_{seed}",
    )


def resolve_config(config: PliersConfig | None = None) -> ResolvedPliersConfig:
    cfg = config or PliersConfig()
    jaw = _pick(cfg.jaw_function, JAW_FUNCTIONS)
    handle = _pick(cfg.handle_form, HANDLE_FORMS)
    pivot = _pick(cfg.pivot_mechanism, PIVOT_MECHANISMS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Compatibility: the locking vise-grip over-center toggle demands a rigid
    # fixed rivet — it cannot ride a sliding slip pivot. Coerce any config
    # (seed / variant / override) to the buildable combination.
    if jaw == "locking_vise_grip":
        pivot = "fixed_rivet"

    is_slip = pivot in SLIP_MECHANISMS

    # groove_count is conditional on a slip mechanism; fixed_rivet pins it to 0.
    if is_slip:
        n_groove = int(
            _clamp(
                cfg.groove_count if cfg.groove_count is not None else 5,
                N_GROOVE_MIN,
                N_GROOVE_MAX,
            )
        )
    else:
        n_groove = 0

    overall = _clamp(cfg.overall_len_scale, 0.85, 1.20)
    jaw_len = _clamp(cfg.jaw_len_scale, 0.90, 1.15)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.90, 1.15)
    open_scale = _clamp(cfg.open_angle_scale, 0.80, 1.20)
    open_angle = _clamp(
        _OPEN_LIMIT * open_scale, math.radians(15.0), math.radians(40.0)
    )

    # slide_travel_scale is conditional on a slip mechanism. The travel must stay
    # within the slot capsule (slip) or the groove track span (channel-lock).
    if is_slip:
        slide_scale = _clamp(cfg.slide_travel_scale, 0.85, 1.15)
        if pivot == "tongue_and_groove":
            # PRISMATIC travel derives from N (channel-lock): GROOVE_SPACING*(N-1).
            base_travel = GROOVE_SPACING * (n_groove - 1)
        else:
            base_travel = _SLOT_TRAVEL
        # Clamp to the span the fixed hub slot can carry so the captured rivet
        # shaft never slides out of the slot / past the hub edge for large N.
        slot_travel = _clamp(max(0.004, base_travel * slide_scale), 0.004, MAX_SLOT_TRAVEL)
    else:
        slot_travel = 0.0

    return ResolvedPliersConfig(
        jaw_function=jaw,
        handle_form=handle,
        pivot_mechanism=pivot,
        groove_count=n_groove,
        palette_style=palette_style,
        overall_len_scale=overall,
        jaw_len_scale=jaw_len,
        grip_girth_scale=grip_girth,
        open_angle=open_angle,
        slot_travel=slot_travel,
        name=cfg.name or "pliers",
    )


def with_overrides(config: PliersConfig, **kwargs: object) -> PliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PliersConfig | ResolvedPliersConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPliersConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("jaw_function", r.jaw_function),
        ("handle_form", r.handle_form),
        ("pivot_mechanism", r.pivot_mechanism),
    ]
    if r.is_slip:
        choices.append(("groove_count", f"groove_n{r.groove_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Interpolation + 2D helpers (from P2).
# ---------------------------------------------------------------------------
def _interp(x: float, pts: list[tuple[float, float]]) -> float:
    pts = sorted(pts)
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, v0), (x1, v1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return v0 + t * (v1 - v0)
    return pts[-1][1]


def _yc(x: float, xk: float = 1.0) -> float:
    # ``x`` is a world (already X-stretched) coordinate; divide by the overall
    # length scale so the tang centerline Y is read in the canonical frame.
    return _interp(x / xk, CENTERLINE)


def _grip_w(x: float, sections) -> float:
    return _interp(x, [(sx, w) for sx, w, _h in sections])


def _strip_loop(pts: list[tuple[float, float]], half_w: float) -> list[tuple[float, float]]:
    n = len(pts)
    normals: list[tuple[float, float]] = []
    for i in range(n):
        if i == 0:
            dx, dy = pts[1][0] - pts[0][0], pts[1][1] - pts[0][1]
        elif i == n - 1:
            dx, dy = pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1]
        else:
            dx, dy = pts[i + 1][0] - pts[i - 1][0], pts[i + 1][1] - pts[i - 1][1]
        length = math.hypot(dx, dy)
        normals.append((-dy / length, dx / length))
    left = [(p[0] + half_w * nx, p[1] + half_w * ny) for p, (nx, ny) in zip(pts, normals)]
    right = [(p[0] - half_w * nx, p[1] - half_w * ny) for p, (nx, ny) in zip(pts, normals)]
    return left + right[::-1]


def _lap_cut(s: int) -> cq.Workplane:
    """Material removed at the pivot so this half keeps only its lap layer."""
    cut = cq.Workplane("XY").circle(LAP_R).extrude(0.012)
    if s > 0:
        return cut.translate((0.0, 0.0, -EPS))
    return cut.translate((0.0, 0.0, -0.012 + EPS))


# ---------------------------------------------------------------------------
# Slot A — jaw_function. Each returns a cq.Workplane in the pivot-at-origin
# local frame, jaw running toward +X, inner face on y = s*JAW_FACE.
# ``jlen`` scales the jaw reach.
# ---------------------------------------------------------------------------
def _combination_jaw(s: int, jlen: float) -> cq.Workplane:
    nose = NOSE_X * jlen
    profile = [
        (0.010, JAW_FACE),
        (nose, JAW_FACE),
        (nose, 0.0105),
        (0.066 * jlen, 0.0118),
        (0.052 * jlen, 0.0136),
        (0.038 * jlen, 0.0152),
        (0.026 * jlen, 0.0162),
        (0.014, 0.0166),
        (0.009, 0.0150),
    ]
    pts = [(x, s * y) for x, y in profile]
    jaw = cq.Workplane("XY").polyline(pts).close().extrude(HALF_T, both=True)
    for i in range(7):
        xi = (0.046 + 0.004 * i) * jlen
        groove = cq.Workplane("XY").box(0.0014, 0.0024, 0.020).translate((xi, s * JAW_FACE, 0.0))
        jaw = jaw.cut(groove)
    recess = (
        cq.Workplane("XY").circle(0.0045).extrude(0.011, both=True).translate((0.030, s * JAW_FACE, 0.0))
    )
    jaw = jaw.cut(recess)
    for ang_deg in (40.0, 75.0, 105.0, 140.0):
        a = math.radians(ang_deg)
        sx = 0.030 + 0.0045 * math.cos(a)
        sy = s * (JAW_FACE + 0.0045 * math.sin(a))
        scallop = cq.Workplane("XY").circle(0.0008).extrude(0.011, both=True).translate((sx, sy, 0.0))
        jaw = jaw.cut(scallop)
    notch_pts = [(0.015, s * -0.001), (0.0215, s * -0.001), (0.0185, s * 0.0035)]
    notch = cq.Workplane("XY").polyline(notch_pts).close().extrude(0.011, both=True)
    jaw = jaw.cut(notch)
    return jaw.cut(_lap_cut(s))


def _flush_cutter_jaw(s: int, jlen: float) -> cq.Workplane:
    """Compact tapered cutting blade with a land along the centerline."""
    tip = 0.060 * jlen
    profile = [
        (0.010, JAW_FACE),
        (tip, JAW_FACE),          # cutting land along the centerline
        (tip, 0.0030),            # sharp narrow nose
        (0.044 * jlen, 0.0080),
        (0.030 * jlen, 0.0120),
        (0.018, 0.0142),
        (0.010, 0.0130),
    ]
    pts = [(x, s * y) for x, y in profile]
    jaw = cq.Workplane("XY").polyline(pts).close().extrude(HALF_T, both=True)
    # Bevel wedge cut from the outer face to leave a flush cutting land.
    bevel = (
        cq.Workplane("XY")
        .polyline([(0.012, s * 0.0009), (tip, s * 0.0009), (0.012, s * 0.0060)])
        .close()
        .extrude(HALF_T, both=True)
        .translate((0.0, 0.0, HALF_T * 0.5))
    )
    jaw = jaw.cut(bevel)
    return jaw.cut(_lap_cut(s))


def _needle_jaw(s: int, jlen: float) -> cq.Workplane:
    """Long thin tapering needle-nose jaw (lofted rectangular sections)."""
    wires = []
    for x, hw, hh in NEEDLE_STATIONS:
        xx = x * jlen
        cy = s * (JAW_FACE + hw)
        wp = cq.Workplane("YZ", origin=(xx, 0.0, 0.0)).center(cy, 0.0)
        wires.append(wp.rect(2.0 * hw, 2.0 * hh).val())
    solid = cq.Solid.makeLoft(wires, ruled=True)
    jaw = cq.Workplane("XY").newObject([solid])
    for i in range(14):
        xi = (0.014 + 0.004 * i) * jlen
        if xi > NEEDLE_STATIONS[-1][0] * jlen:
            break
        hh_i = _interp(xi / jlen, [(x, h) for x, _w, h in NEEDLE_STATIONS])
        groove = cq.Workplane("XY").box(0.0005, 0.0010, 2.2 * hh_i).translate((xi, s * JAW_FACE, 0.0))
        jaw = jaw.cut(groove)
    notch_pts = [(0.012, s * -0.001), (0.019, s * -0.001), (0.0155, s * 0.003)]
    notch = cq.Workplane("XY").polyline(notch_pts).close().extrude(0.011, both=True)
    jaw = jaw.cut(notch)
    return jaw.cut(_lap_cut(s))


def _locking_jaw(s: int, jlen: float) -> cq.Workplane:
    """Curved C-shaped clamping jaw with cross-hatch serration + clamp recess."""
    nose = 0.058 * jlen
    # Inner (cutting/clamp) edge bows toward the centerline; outer arc bulges out.
    inner = [
        (0.010, JAW_FACE),
        (0.026 * jlen, 0.0009),
        (0.042 * jlen, 0.0016),
        (nose, 0.0026),
    ]
    outer = [
        (nose, 0.0120),
        (0.046 * jlen, 0.0150),
        (0.030 * jlen, 0.0168),
        (0.016, 0.0170),
        (0.009, 0.0150),
    ]
    pts = [(x, s * y) for x, y in (inner + outer)]
    jaw = cq.Workplane("XY").polyline(pts).close().extrude(HALF_T, both=True)
    # Cross-hatch serration on the inner clamp face.
    for i in range(6):
        xi = (0.020 + 0.005 * i) * jlen
        groove = cq.Workplane("XY").box(0.0012, 0.0022, 0.020).translate((xi, s * 0.0014, 0.0))
        jaw = jaw.cut(groove)
    # Clamp recess behind the nose.
    recess = (
        cq.Workplane("XY").circle(0.0040).extrude(0.011, both=True).translate((0.034 * jlen, s * 0.0020, 0.0))
    )
    jaw = jaw.cut(recess)
    return jaw.cut(_lap_cut(s))


def _jaw_solid(r: ResolvedPliersConfig, s: int) -> cq.Workplane:
    jlen = r.jaw_len_scale
    if r.jaw_function == "flush_cutter":
        return _flush_cutter_jaw(s, jlen)
    if r.jaw_function == "needle_nose":
        return _needle_jaw(s, jlen)
    if r.jaw_function == "locking_vise_grip":
        return _locking_jaw(s, jlen)
    return _combination_jaw(s, jlen)


# ---------------------------------------------------------------------------
# Hub + shank.
# ---------------------------------------------------------------------------
def _hub_solid(s: int) -> cq.Workplane:
    hub = cq.Workplane("XY").circle(HUB_R).extrude(HALF_T, both=True)
    return hub.cut(_lap_cut(s))


def _slot_cut_solid(travel: float = _SLOT_TRAVEL) -> cq.Workplane:
    # Capsule whose straight portion spans the full prismatic travel, so the
    # captured rivet shaft rides inside the flat-width channel across the whole
    # joint range (endcaps add SLOT_WIDTH/2 of clearance beyond each extreme).
    half_rect = travel / 2.0
    rr = SLOT_WIDTH / 2.0
    h = HALF_T * 2 + 0.004
    body = cq.Workplane("XY").box(travel, SLOT_WIDTH, h)
    end_l = cq.Workplane("XY").circle(rr).extrude(h / 2.0, both=True).translate((-half_rect, 0.0, 0.0))
    end_r = cq.Workplane("XY").circle(rr).extrude(h / 2.0, both=True).translate((half_rect, 0.0, 0.0))
    return body.union(end_l).union(end_r)


def _hub_slotted_solid(s: int, travel: float = _SLOT_TRAVEL) -> cq.Workplane:
    hub = cq.Workplane("XY").circle(HUB_R).extrude(HALF_T, both=True)
    hub = hub.cut(_lap_cut(s))
    return hub.cut(_slot_cut_solid(travel))


def _shank_solid(s: int, xk: float = 1.0) -> cq.Workplane:
    pts = [(x * xk, s * y) for x, y in TANG_PTS]
    loop = _strip_loop(pts, TANG_HALF_W)
    shank = cq.Workplane("XY").polyline(loop).close().extrude(HALF_T, both=True)
    return shank.cut(_lap_cut(s))


# ---------------------------------------------------------------------------
# Slot B — handle_form geometry.
# ---------------------------------------------------------------------------
def _ellipse_wire(x: float, yc: float, zc: float, w: float, h: float) -> cq.Wire:
    wp = cq.Workplane("YZ", origin=(x, 0.0, 0.0)).center(yc, zc).ellipse(w, h)
    return wp.val()


def _grip_solid(s: int, sections, girth: float, xk: float = 1.0) -> cq.Solid:
    # Loft stations are placed in the canonical frame then stretched in X by the
    # overall length scale (girth is a separate cross-section scale).
    wires = [
        _ellipse_wire(x * xk, s * _yc(x), 0.0, w * girth, h * girth)
        for x, w, h in sections
    ]
    return cq.Solid.makeLoft(wires, ruled=False)


def _inlay_solid(s: int, sections, girth: float, xk: float = 1.0) -> cq.Solid:
    wires = [
        _ellipse_wire(x * xk, s * _yc(x), INLAY_Z_CENTER * girth, _grip_w(x, sections) * girth - 0.0012, INLAY_HALF_H)
        for x in INLAY_XS
    ]
    return cq.Solid.makeLoft(wires, ruled=False)


def _bow_arm_solid(s: int, xk: float = 1.0) -> cq.Workplane:
    """Steel neck arm sweeping from the shank to the finger ring (looped_bow)."""
    arm_pts = [
        (-0.020, -0.007),
        (-0.050, -0.014),
        (-0.080, -0.021),
        (BOW_RING_CX + 0.010, BOW_RING_CY_BASE + 0.004),
    ]
    pts = [(x * xk, s * y) for x, y in arm_pts]
    loop = _strip_loop(pts, 0.0035)
    arm = cq.Workplane("XY").polyline(loop).close().extrude(HALF_T, both=True)
    try:
        arm = arm.edges("|Z").fillet(0.0010)
    except Exception:
        pass
    return arm


def _bow_ring_geom(s: int, xk: float = 1.0):
    """Closed-loop torus finger ring for the bow handle."""
    return TorusGeometry(
        radius=BOW_RING_R,
        tube=BOW_TUBE_R,
        radial_segments=20,
        tubular_segments=48,
    ).translate(BOW_RING_CX * xk, s * BOW_RING_CY_BASE, 0.0)


# ---------------------------------------------------------------------------
# Slip mechanism: groove multiplicity emitters (shared helpers).
# ---------------------------------------------------------------------------
def _slip_groove_x(r: ResolvedPliersConfig, i: int) -> float:
    n = r.groove_count
    if n <= 1:
        return 0.0
    return -r.slot_travel / 2.0 + (i / (n - 1)) * r.slot_travel


def _slip_groove_solid(r: ResolvedPliersConfig, i: int) -> cq.Workplane:
    """One slip-joint detent mark on either side of the slot (hub bottom face)."""
    x = _slip_groove_x(r, i)
    notch_pos = cq.Workplane("XY").box(0.0014, 0.003, 0.0008).translate((x, 0.007, -(HALF_T + 0.0002)))
    notch_neg = cq.Workplane("XY").box(0.0014, 0.003, 0.0008).translate((x, -0.007, -(HALF_T + 0.0002)))
    return notch_pos.union(notch_neg)


def _channel_groove_x(i: int) -> float:
    return GROOVE_X_START - i * GROOVE_SPACING


def _channel_groove_solid(i: int, xk: float = 1.0) -> cq.Workplane:
    """One channel-lock groove track step recessed into the lower shank top.

    The ridge straddles the shank centerline (which sweeps in -Y as x decreases)
    and embeds down into the shank top so it always has steel beneath it.
    """
    x = _channel_groove_x(i)  # canonical shank X
    yc = _yc(x)  # follow the tang centerline so the ridge sits on the shank
    # The shank top is at z=+HALF_T; the ridge half-height 0.0010 with center
    # at HALF_T-0.0008 embeds ~0.0018 into the steel (no floating island). The
    # ridge X follows the same overall-length stretch as the shank it rides on.
    ridge = cq.Workplane("XY").box(0.0020, 0.0075, 0.0020).translate((x * xk, yc, HALF_T - 0.0008))
    return ridge


# ---------------------------------------------------------------------------
# Locking vise-grip: toggle link.
# ---------------------------------------------------------------------------
def _toggle_link_solid() -> cq.Workplane:
    """Flat steel over-center toggle bar, authored at the toggle pin origin."""
    bar = cq.Workplane("XY").box(TOGGLE_LINK_LEN, 0.0060, 0.0040, centered=(False, True, True))
    bar = bar.translate((0.0, 0.0, 0.0))
    # Pin boss at the origin so the part AABB contains (0,0,0).
    pin = cq.Workplane("XY").circle(0.0030).extrude(HALF_T, both=True)
    return bar.union(pin)


# ---------------------------------------------------------------------------
# Rivet (inline visuals).
# ---------------------------------------------------------------------------
def _emit_rivet_visuals(part, mats) -> None:
    part.visual(
        Cylinder(SEAM_R, SEAM_H),
        origin=Origin(xyz=(0.0, 0.0, -(HALF_T + SEAM_H / 2.0 - EPS))),
        name="boss_seam", material_class_id="metal.blackened_gunmetal",
        material=mats["seam"],
    )
    part.visual(
        Cylinder(BOSS_R, BOSS_H),
        origin=Origin(xyz=(0.0, 0.0, -(HALF_T + SEAM_H + BOSS_H / 2.0 - 2.0 * EPS))),
        name="rivet_boss", material_class_id="metal.brushed_silver",
        material=mats["brushed"],
    )
    part.visual(
        Cylinder(RIVET_R, 2.0 * HALF_T + SEAM_H + 2.0 * EPS + 0.0005),
        origin=Origin(xyz=(0.0, 0.0, 0.00005)),
        name="rivet_shaft", material_class_id="metal.brushed_silver",
        material=mats["brushed"],
    )
    part.visual(
        Cylinder(SEAM_R, SEAM_H),
        origin=Origin(xyz=(0.0, 0.0, HALF_T + SEAM_H / 2.0 + EPS)),
        name="head_seam", material_class_id="metal.blackened_gunmetal",
        material=mats["seam"],
    )
    part.visual(
        Cylinder(BOSS_R, BOSS_H),
        origin=Origin(xyz=(0.0, 0.0, HALF_T + SEAM_H + BOSS_H / 2.0)),
        name="rivet_head", material_class_id="metal.brushed_silver",
        material=mats["brushed"],
    )


# ---------------------------------------------------------------------------
# Per-half emit.
# ---------------------------------------------------------------------------
def _emit_half(model, r, part, s, mats, *, assets, slotted: bool, tag: str) -> None:
    xk = r.overall_len_scale
    part.visual(
        mesh_from_cadquery(_jaw_solid(r, s), f"{tag}_jaw", tolerance=0.0002),
        name="jaw", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_red_dipped", "black_chrome", "gunmetal_yellow", "polished_blue"} else "metal.chrome_polished"),
        material=mats["jaw"],
    )
    hub_mesh = _hub_slotted_solid(s, r.slot_travel) if slotted else _hub_solid(s)
    part.visual(
        mesh_from_cadquery(hub_mesh, f"{tag}_hub", tolerance=0.0002),
        name="hub", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_red_dipped", "black_chrome", "gunmetal_yellow", "polished_blue"} else "metal.chrome_polished"),
        material=mats["forged"],
    )
    part.visual(
        mesh_from_cadquery(_shank_solid(s, xk), f"{tag}_shank", tolerance=0.0002),
        name="shank", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_red_dipped", "black_chrome", "gunmetal_yellow", "polished_blue"} else "metal.chrome_polished"),
        material=mats["forged"],
    )
    if r.handle_form == "looped_bow":
        part.visual(
            mesh_from_cadquery(_bow_arm_solid(s, xk), f"{tag}_bow_arm", tolerance=0.0002),
            name="bow_arm", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_red_dipped", "black_chrome", "gunmetal_yellow", "polished_blue"} else "metal.chrome_polished"),
            material=mats["forged"],
        )
        part.visual(
            mesh_from_geometry(_bow_ring_geom(s, xk), f"{tag}_bow_ring"),
            name="grip", material_class_id="plastic.opaque_glossy_molded",
            material=mats["grip"],
        )
    else:
        sections = GRIP_SECTIONS_CUSHION if r.handle_form == "cushioned_ergonomic" else GRIP_SECTIONS
        part.visual(
            mesh_from_cadquery(_grip_solid(s, sections, r.grip_girth_scale, xk), f"{tag}_grip", tolerance=0.0002),
            name="grip", material_class_id="plastic.opaque_glossy_molded",
            material=mats["grip"],
        )
        part.visual(
            mesh_from_cadquery(_inlay_solid(s, sections, r.grip_girth_scale, xk), f"{tag}_inlay", tolerance=0.0002),
            name="grip_inlay", material_class_id="plastic.opaque_glossy_molded",
            material=mats["inlay"],
        )


def _emit_carriage(model, r, mats):
    """Slip-mechanism sliding carriage carrying the whole rivet assembly."""
    carriage = model.part("pivot_carriage")
    carriage.visual(
        Cylinder(RIVET_R, 2.0 * HALF_T + SEAM_H + 2.0 * EPS + 0.0005),
        origin=Origin(xyz=(0.0, 0.0, 0.00005)),
        name="rivet_shaft", material_class_id="metal.brushed_silver",
        material=mats["brushed"],
    )
    # The bottom seam is pulled up so it overlaps half_0's hub bottom face by
    # ~0.0008 m: this is the carriage's captured-pin contact to the slotted half
    # (a clean support path so the carriage group is never isolated).
    carriage.visual(
        Cylinder(SEAM_R, SEAM_H + 0.0016),
        origin=Origin(xyz=(0.0, 0.0, -(HALF_T - 0.0008 + (SEAM_H + 0.0016) / 2.0))),
        name="boss_seam", material_class_id="metal.blackened_gunmetal",
        material=mats["seam"],
    )
    carriage.visual(
        Cylinder(BOSS_R, BOSS_H),
        origin=Origin(xyz=(0.0, 0.0, -(HALF_T + SEAM_H + BOSS_H / 2.0))),
        name="rivet_boss", material_class_id="metal.brushed_silver",
        material=mats["brushed"],
    )
    carriage.visual(
        Cylinder(SEAM_R, SEAM_H),
        origin=Origin(xyz=(0.0, 0.0, HALF_T + SEAM_H / 2.0 + EPS)),
        name="head_seam", material_class_id="metal.blackened_gunmetal",
        material=mats["seam"],
    )
    carriage.visual(
        Cylinder(BOSS_R, BOSS_H),
        origin=Origin(xyz=(0.0, 0.0, HALF_T + SEAM_H + BOSS_H / 2.0)),
        name="rivet_head", material_class_id="metal.brushed_silver",
        material=mats["brushed"],
    )
    carriage.inertial = Inertial.from_geometry(
        Box((0.026, 0.026, 0.026)), mass=0.02, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    return carriage


def _half_bbox(r) -> tuple[float, float, float]:
    return (0.20 * r.overall_len_scale, 0.06, 2.0 * HALF_T + 0.006)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_pliers(
    config: PliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"pliers_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    slotted_half0 = r.is_slip

    # --- Half 0 (root): jaw on +Y, hub (slotted for slip), shank, handle. ---
    half_0 = model.part("plier_half_0")
    _emit_half(model, r, half_0, 1, mats, assets=assets, slotted=slotted_half0, tag="half0")
    half_0.inertial = Inertial.from_geometry(
        Box(_half_bbox(r)), mass=0.06, origin=Origin(xyz=(0.0, 0.02, 0.0))
    )

    # --- Half 1 (moving child): mirror, plain hub. ---
    half_1 = model.part("plier_half_1")
    _emit_half(model, r, half_1, -1, mats, assets=assets, slotted=False, tag="half1")
    half_1.inertial = Inertial.from_geometry(
        Box(_half_bbox(r)), mass=0.06, origin=Origin(xyz=(0.0, -0.02, 0.0))
    )

    if not r.is_slip:
        # fixed_rivet: rivet is an inline visual of half_0; single REVOLUTE.
        _emit_rivet_visuals(half_0, mats)
        model.articulation(
            "pivot",
            ArticulationType.REVOLUTE,
            parent=half_0,
            child=half_1,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=80.0, velocity=3.0, lower=0.0, upper=r.open_angle),
        )
    else:
        # slip mechanism: grooves on half_0, a sliding carriage, PRISMATIC + REVOLUTE.
        if r.pivot_mechanism == "slip_joint":
            for i in range(r.groove_count):
                half_0.visual(
                    mesh_from_cadquery(_slip_groove_solid(r, i), f"slip_groove_{i}", tolerance=0.0002),
                    name=f"groove_{i}", material_class_id="metal.stainless_matte",
                    material=mats["accent"],
                )
        else:  # tongue_and_groove channel-lock track on the lower shank
            for i in range(r.groove_count):
                half_0.visual(
                    mesh_from_cadquery(_channel_groove_solid(i, r.overall_len_scale), f"chan_groove_{i}", tolerance=0.0002),
                    name=f"groove_{i}", material_class_id="metal.stainless_matte",
                    material=mats["accent"],
                )

        carriage = _emit_carriage(model, r, mats)
        model.articulation(
            "slot_slide",
            ArticulationType.PRISMATIC,
            parent=half_0,
            child=carriage,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=50.0, velocity=0.5, lower=-r.slot_travel / 2.0, upper=r.slot_travel / 2.0
            ),
        )
        model.articulation(
            "pivot",
            ArticulationType.REVOLUTE,
            parent=carriage,
            child=half_1,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=80.0, velocity=3.0, lower=0.0, upper=r.open_angle),
        )

    # --- Optional locking toggle (second REVOLUTE), independent of pivot mech. ---
    if r.is_locking:
        toggle = model.part("toggle_link")
        toggle.visual(
            mesh_from_cadquery(_toggle_link_solid(), "toggle_link_bar", tolerance=0.0002),
            name="toggle_link", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"steel_red_dipped", "black_chrome", "gunmetal_yellow", "polished_blue"} else "metal.chrome_polished"),
            material=mats["forged"],
        )
        # Adjustment screw: inline visual on half_0's handle butt end (decoration).
        # Seated on the grip centerline so it embeds into the grip body (no island).
        xk = r.overall_len_scale
        screw_x = -0.118 * xk
        half_0.visual(
            Cylinder(0.0035, 0.014),
            origin=Origin(xyz=(screw_x, _yc(screw_x, xk), 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            name="adjustment_screw", material_class_id="metal.brushed_silver",
            material=mats["brushed"],
        )
        toggle.inertial = Inertial.from_geometry(
            Box((TOGGLE_LINK_LEN, 0.006, 0.004)),
            mass=0.01,
            origin=Origin(xyz=(TOGGLE_LINK_LEN / 2.0, 0.0, 0.0)),
        )
        # The toggle pin sits inside the handle butt (real shank/grip geometry),
        # tracking the same overall-length stretch as the handle.
        toggle_x = TOGGLE_PIVOT_X * xk
        toggle_yc = _yc(toggle_x, xk)
        model.articulation(
            "toggle",
            ArticulationType.REVOLUTE,
            parent=half_0,
            child=toggle,
            origin=Origin(xyz=(toggle_x, toggle_yc, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=40.0, velocity=2.0, lower=-0.05, upper=TOGGLE_RANGE
            ),
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pliers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_pliers_tests(
    object_model: ArticulatedObject,
    config: PliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    half_0 = object_model.get_part("plier_half_0")
    half_1 = object_model.get_part("plier_half_1")
    pivot = object_model.get_articulation("pivot")

    jaw0 = half_0.get_visual("jaw")
    jaw1 = half_1.get_visual("jaw")
    hub0 = half_0.get_visual("hub")
    hub1 = half_1.get_visual("hub")

    # --- Captured-pin allowance: the rivet shaft passes through the moving lap. ---
    if r.is_slip:
        carriage = object_model.get_part("pivot_carriage")
        ctx.allow_overlap(
            carriage,
            half_1,
            reason=(
                "the carriage rivet shaft intentionally passes through half_1's "
                "hub lap, capturing it at the pivot (captured-pin geometry)."
            ),
        )
        ctx.allow_overlap(
            carriage,
            half_0,
            reason=(
                "the carriage rivet shaft slides through the elongated slot / "
                "groove track in half_0 — the core slip mechanism."
            ),
        )
        ctx.allow_overlap(
            half_0,
            half_1,
            reason="the two forged hub laps nest at the shared pivot footprint.",
        )
    else:
        ctx.allow_overlap(
            half_0,
            half_1,
            reason=(
                "the rivet shaft is fixed to half_0 and intentionally passes "
                "through the moving half's hub lap, capturing it at the pivot "
                "(captured-pin geometry); the hub laps also nest."
            ),
        )

    if r.is_locking:
        toggle = object_model.get_part("toggle_link")
        ctx.allow_overlap(
            half_0,
            toggle,
            reason="the toggle link's pin boss is captured inside half_0's handle butt.",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # Pivot / slot_slide / toggle omit MatingContract (captured-pin geometry,
    # grandfathered); the flat 0.015 m articulation-origin baseline runs in the
    # compiler and all origins sit on real hub / slot / pin hardware.
    ctx.fail_if_joint_mating_has_gap()

    # --- Pivot joint contract. ---
    ctx.check(
        "pivot is REVOLUTE about Z opening 0..OPEN",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(abs(c), 3) for c in pivot.axis) == (0.0, 0.0, 1.0)
        and pivot.motion_limits is not None
        and abs(pivot.motion_limits.lower) < 1e-9
        and pivot.motion_limits.upper > pivot.motion_limits.lower,
        details=f"type={pivot.articulation_type} axis={tuple(round(c, 3) for c in pivot.axis)}",
    )

    # --- Chain topology by pivot_mechanism. ---
    if r.is_slip:
        slide = object_model.get_articulation("slot_slide")
        ctx.check(
            "slot_slide is a PRISMATIC joint along X with travel",
            slide.articulation_type == ArticulationType.PRISMATIC
            and tuple(round(abs(c), 3) for c in slide.axis) == (1.0, 0.0, 0.0)
            and slide.motion_limits is not None
            and slide.motion_limits.upper > slide.motion_limits.lower,
            details=f"type={slide.articulation_type} axis={tuple(round(c, 3) for c in slide.axis)}",
        )
        ctx.check(
            "pivot parents to the sliding carriage (3-part chain)",
            pivot.parent == "pivot_carriage",
            details=f"pivot.parent={pivot.parent}",
        )
        # Carriage actually slides.
        carriage = object_model.get_part("pivot_carriage")
        rest = ctx.part_world_position(carriage)
        with ctx.pose({slide: slide.motion_limits.upper}):
            shifted = ctx.part_world_position(carriage)
        if rest is not None and shifted is not None:
            ctx.check(
                "carriage slides along X at the slot travel",
                shifted[0] > rest[0] + 0.001,
                details=f"rest_x={rest[0]:.4f} shifted_x={shifted[0]:.4f}",
            )
        # --- Slot containment (T&G travel derives from N): the captured rivet
        #     shaft must stay inside the hub slot across the FULL prismatic
        #     travel, including the largest N. The design invariant bounds the
        #     clamped worst case; the kinematic check confirms this build. ---
        ctx.check(
            "max slot travel keeps the rivet shaft inside the hub (design invariant)",
            MAX_SLOT_TRAVEL / 2.0 + RIVET_R <= HUB_R + 1e-9,
            details=f"max_half_travel+r={MAX_SLOT_TRAVEL / 2.0 + RIVET_R:.4f} hub_r={HUB_R:.4f}",
        )
        for lim, tag in ((slide.motion_limits.lower, "retracted"), (slide.motion_limits.upper, "extended")):
            with ctx.pose({slide: lim}):
                shaft = ctx.part_element_world_aabb(carriage, elem="rivet_shaft")
            if shaft is not None:
                reach = max(abs(shaft[0][0]), abs(shaft[1][0]), abs(shaft[0][1]), abs(shaft[1][1]))
                ctx.check(
                    f"rivet shaft stays inside the hub at slot {tag}",
                    reach <= HUB_R + 1e-4,
                    details=f"shaft_reach={reach:.4f} hub_r={HUB_R:.4f} travel={r.slot_travel:.4f}",
                )
        # groove multiplicity present + evenly spaced.
        n = r.groove_count
        gnames = [f"groove_{i}" for i in range(n)]
        names0 = {v.name for v in half_0.visuals}
        for gn in gnames:
            ctx.check(
                f"{gn} groove visual present on half_0",
                gn in names0,
                details=f"visuals={sorted(names0)}",
            )
        boxes = [ctx.part_element_world_aabb(half_0, elem=gn) for gn in gnames]
        boxes = [b for b in boxes if b is not None]
        if len(boxes) >= 2:
            cxs = sorted((b[0][0] + b[1][0]) / 2.0 for b in boxes)
            gaps = [cxs[j + 1] - cxs[j] for j in range(len(cxs) - 1)]
            ctx.check(
                "grooves evenly spaced along the shank",
                all(g > 0.0005 for g in gaps)
                and (max(gaps) - min(gaps)) < 0.003,
                details=f"gaps={[round(g, 5) for g in gaps]}",
            )
    else:
        ctx.check(
            "fixed_rivet pivot parents half_0 directly (2-part chain)",
            pivot.parent == "plier_half_0",
            details=f"pivot.parent={pivot.parent}",
        )
        # Rivet is an inline visual of half_0 (no separate decoration part).
        a_names = {v.name for v in half_0.visuals}
        ctx.check(
            "rivet boss/shaft/head are inline half_0 visuals",
            {"rivet_boss", "rivet_shaft", "rivet_head"} <= a_names,
            details=f"visuals={sorted(a_names)}",
        )
        ctx.check(
            "no groove visuals under fixed_rivet",
            not any(v.name.startswith("groove_") for v in half_0.visuals),
            details=f"visuals={sorted(a_names)}",
        )

    # --- Both halves carry jaw + hub + a handle (grip). ---
    for half in (half_0, half_1):
        names = {v.name for v in half.visuals}
        ctx.check(
            f"{half.name} carries jaw + hub + grip",
            {"jaw", "hub", "grip"} <= names,
            details=f"visuals={sorted(names)}",
        )

    # --- Jaws cross (steel halves on opposite sides of the centerline). ---
    a_jaw = ctx.part_element_world_aabb(half_0, elem="jaw")
    b_jaw = ctx.part_element_world_aabb(half_1, elem="jaw")
    if a_jaw is not None and b_jaw is not None:
        a_cy = (a_jaw[0][1] + a_jaw[1][1]) / 2.0
        b_cy = (b_jaw[0][1] + b_jaw[1][1]) / 2.0
        ctx.check(
            "jaws sit on opposite sides of the centerline",
            a_cy * b_cy < 0.0,
            details=f"a_jaw_cy={a_cy:.4f} b_jaw_cy={b_cy:.4f}",
        )

    # --- Geometry sanity: jaw reaches +X, grip reaches -X. ---
    grip0 = ctx.part_element_world_aabb(half_0, elem="grip")
    if a_jaw is not None and grip0 is not None:
        ctx.check(
            "jaw extends toward the nose (+X)",
            a_jaw[1][0] > 0.04,
            details=f"jaw max_x={a_jaw[1][0]:.4f}",
        )
        ctx.check(
            "grip extends toward the handle end (-X)",
            grip0[0][0] < -0.04,
            details=f"grip min_x={grip0[0][0]:.4f}",
        )

    # --- Cushioned ergonomic grip is genuinely thick. ---
    if r.handle_form == "cushioned_ergonomic" and grip0 is not None:
        thick_z = grip0[1][2] - grip0[0][2]
        width_y = grip0[1][1] - grip0[0][1]
        ctx.check(
            "cushioned grip is thick (>28mm) and wide (>20mm)",
            thick_z > 0.028 and width_y > 0.020,
            details=f"thick_z={thick_z:.4f} width_y={width_y:.4f}",
        )

    # --- Looped bow finger ring is a real closed loop (hollow center). ---
    if r.handle_form == "looped_bow":
        for half, tag in ((half_0, "half0"), (half_1, "half1")):
            ring = ctx.part_element_world_aabb(half, elem="grip")
            arm = ctx.part_element_world_aabb(half, elem="bow_arm")
            if ring is not None:
                span_x = ring[1][0] - ring[0][0]
                span_y = ring[1][1] - ring[0][1]
                ctx.check(
                    f"{half.name} bow ring is a sizeable closed loop",
                    span_x > 2.0 * BOW_RING_R - 0.004 and span_y > 2.0 * BOW_RING_R - 0.004,
                    details=f"span_x={span_x:.4f} span_y={span_y:.4f}",
                )
            ctx.check(
                f"{half.name} carries a steel bow arm",
                arm is not None,
                details=f"bow_arm aabb missing on {half.name}",
            )

    # --- Locking vise-grip: third toggle_link part + second REVOLUTE. ---
    if r.is_locking:
        toggle = object_model.get_part("toggle_link")
        tj = object_model.get_articulation("toggle")
        ctx.check(
            "toggle is a genuine (non-fixed) REVOLUTE second joint",
            tj.articulation_type == ArticulationType.REVOLUTE
            and tj.motion_limits is not None
            and tj.motion_limits.upper > tj.motion_limits.lower,
            details=f"type={tj.articulation_type}",
        )
        rest = ctx.part_world_aabb(toggle)
        with ctx.pose({tj: tj.motion_limits.upper}):
            flexed = ctx.part_world_aabb(toggle)
        if rest is not None and flexed is not None:
            rc = ((rest[0][0] + rest[1][0]) / 2.0, (rest[0][1] + rest[1][1]) / 2.0)
            fc = ((flexed[0][0] + flexed[1][0]) / 2.0, (flexed[0][1] + flexed[1][1]) / 2.0)
            ctx.check(
                "toggling the over-center link moves it",
                math.dist(rc, fc) > 1e-4,
                details=f"rest={rc} flexed={fc}",
            )

    # --- Pivot kinematics: opening separates the jaws and spreads the handles. ---
    rest_jaw1 = ctx.part_element_world_aabb(half_1, elem="jaw")
    rest_grip1 = ctx.part_element_world_aabb(half_1, elem="grip")
    with ctx.pose({pivot: pivot.motion_limits.upper}):
        open_jaw1 = ctx.part_element_world_aabb(half_1, elem="jaw")
        open_grip1 = ctx.part_element_world_aabb(half_1, elem="grip")
    if rest_jaw1 is not None and open_jaw1 is not None:
        ctx.check(
            "opening swings the moving jaw away (jaws separate)",
            open_jaw1[0][1] < rest_jaw1[0][1] - 0.010,
            details=f"rest_min_y={rest_jaw1[0][1]:.4f} open_min_y={open_jaw1[0][1]:.4f}",
        )
    if rest_grip1 is not None and open_grip1 is not None:
        ctx.check(
            "opening spreads the moving handle outward",
            open_grip1[1][1] > rest_grip1[1][1] + 0.015,
            details=f"rest_max_y={rest_grip1[1][1]:.4f} open_max_y={open_grip1[1][1]:.4f}",
        )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "PliersConfig",
    "ResolvedPliersConfig",
    "build_pliers",
    "build_seeded_pliers",
    "config_from_seed",
    "resolve_config",
    "run_pliers_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
