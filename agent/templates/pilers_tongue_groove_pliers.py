# SPDX-License-Identifier: Apache-2.0

"""Tongue-and-groove pliers modular template (0611 / pilers_tongue_groove_pliers).

Baseline skeleton (3-part / 2-joint):
- ``slotted_shank`` (ROOT): forged polyline + through-slot along ``slot_axis`` +
  N tooth cuts + jaw face (Slot A) + blue vinyl grip (Slot D).
- ``pivot_carriage``: captured pivot hardware (round rivet or rect block).
- ``tongue_shank``: mirrored forged polyline + pivot boss + engaging_tongue +
  jaw face + grip.

Joints:
- ``slot_setting`` PRISMATIC (slotted_shank -> pivot_carriage), axis =
  ``(slot_axis[0], 0, slot_axis[1])``, range ``[0, 0.036]``.
- ``jaw_pivot`` REVOLUTE (pivot_carriage -> tongue_shank), axis +Y,
  range ``[-1.05, +0.42]``.

Slot B = push_button_carriage adds ``push_button`` part + ``button_press``
PRISMATIC axis -Y (4-part / 3-joint).

Slots:
- ``jaw_form`` (4): straight_serrated / deep_v_pipe_jaw / replaceable_smooth_pads
  / narrow_offset_jaw.
- ``adjustment`` (3): slotted_rivet_carriage / box_joint_opening / push_button_carriage.
- ``groove_positions`` (4): 3 / 5 / 7 / 8.
- ``handle_form`` (3): standard_dipped / extended_leverage_handle / guarded_grip.

``palette_style`` (6): pure material rgba axis; not in slot_choices.
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
    MotionLimits,
    MotionProperties,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Enum axes.
# ---------------------------------------------------------------------------
JawForm = Literal[
    "straight_serrated",
    "deep_v_pipe_jaw",
    "replaceable_smooth_pads",
    "narrow_offset_jaw",
]
Adjustment = Literal[
    "slotted_rivet_carriage",
    "box_joint_opening",
    "push_button_carriage",
]
HandleForm = Literal["standard_dipped", "extended_leverage_handle", "guarded_grip"]
PaletteStyle = Literal[
    "steel_blue",
    "gunmetal_red",
    "chrome_dark_blue",
    "black_yellow",
    "industrial_green",
    "brushed_steel_orange",
]

JAW_FORMS: tuple[JawForm, ...] = (
    "straight_serrated",
    "deep_v_pipe_jaw",
    "replaceable_smooth_pads",
    "narrow_offset_jaw",
)
ADJUSTMENTS: tuple[Adjustment, ...] = (
    "slotted_rivet_carriage",
    "box_joint_opening",
    "push_button_carriage",
)
GROOVE_POSITIONS_VALUES: tuple[int, ...] = (3, 5, 7, 8)
HANDLE_FORMS: tuple[HandleForm, ...] = (
    "standard_dipped",
    "extended_leverage_handle",
    "guarded_grip",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "steel_blue",
    "gunmetal_red",
    "chrome_dark_blue",
    "black_yellow",
    "industrial_green",
    "brushed_steel_orange",
)

# Slot geometry (P0 origin).
SLOT_AXIS: tuple[float, float] = (-0.342, -0.940)
SLOT_NORMAL: tuple[float, float] = (0.940, -0.342)
SLOT_LENGTH: float = 0.058
SLOT_WIDTH: float = 0.012
BASE_SLIDE_UPPER: float = 0.036
BASE_PIVOT_LOWER: float = -1.05
BASE_PIVOT_UPPER: float = math.radians(24.0)


# ---------------------------------------------------------------------------
# Palettes. Each provides material rgba keys the builder always references.
# Metal: steel_blue / chrome_dark_blue / brushed_steel_orange. Vinyl/rubber
# grip: gunmetal_red / black_yellow / industrial_green.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "steel_blue": {
        "forged": (0.52, 0.55, 0.56, 1.0),
        "dark_steel": (0.18, 0.20, 0.20, 1.0),
        "jaw_steel": (0.10, 0.11, 0.11, 1.0),
        "grip": (0.02, 0.43, 0.93, 1.0),
        "button": (0.85, 0.12, 0.08, 1.0),
    },
    "gunmetal_red": {
        "forged": (0.40, 0.42, 0.44, 1.0),
        "dark_steel": (0.20, 0.22, 0.22, 1.0),
        "jaw_steel": (0.10, 0.10, 0.11, 1.0),
        "grip": (0.85, 0.10, 0.08, 1.0),
        "button": (0.20, 0.20, 0.22, 1.0),
    },
    "chrome_dark_blue": {
        "forged": (0.80, 0.82, 0.85, 1.0),
        "dark_steel": (0.22, 0.24, 0.28, 1.0),
        "jaw_steel": (0.28, 0.30, 0.32, 1.0),
        "grip": (0.05, 0.10, 0.32, 1.0),
        "button": (0.85, 0.15, 0.10, 1.0),
    },
    "black_yellow": {
        "forged": (0.20, 0.20, 0.22, 1.0),
        "dark_steel": (0.10, 0.10, 0.11, 1.0),
        "jaw_steel": (0.06, 0.06, 0.08, 1.0),
        "grip": (0.95, 0.80, 0.10, 1.0),
        "button": (0.10, 0.10, 0.12, 1.0),
    },
    "industrial_green": {
        "forged": (0.55, 0.57, 0.58, 1.0),
        "dark_steel": (0.18, 0.20, 0.20, 1.0),
        "jaw_steel": (0.10, 0.11, 0.11, 1.0),
        "grip": (0.09, 0.44, 0.20, 1.0),
        "button": (0.90, 0.75, 0.10, 1.0),
    },
    "brushed_steel_orange": {
        "forged": (0.60, 0.62, 0.64, 1.0),
        "dark_steel": (0.22, 0.24, 0.25, 1.0),
        "jaw_steel": (0.12, 0.13, 0.14, 1.0),
        "grip": (0.94, 0.44, 0.08, 1.0),
        "button": (0.20, 0.20, 0.22, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersTongueGroovePliersConfig:
    jaw_form: JawForm | None = None
    adjustment: Adjustment | None = None
    groove_positions: int | None = None
    handle_form: HandleForm | None = None
    palette_style: PaletteStyle = "steel_blue"
    overall_len_scale: float = 1.0
    jaw_face_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "pilers_tongue_groove_pliers"


@dataclass(frozen=True)
class ResolvedConfig:
    jaw_form: JawForm
    adjustment: Adjustment
    groove_positions: int
    handle_form: HandleForm
    palette_style: PaletteStyle
    overall_len_scale: float
    jaw_face_scale: float
    grip_girth_scale: float
    pivot_lower: float
    pivot_upper: float
    slide_upper: float
    name: str

    @property
    def has_button(self) -> bool:
        return self.adjustment == "push_button_carriage"


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersTongueGroovePliersConfig:
    rng = random.Random(seed)
    jaw = rng.choices(JAW_FORMS, weights=[5, 3, 3, 3], k=1)[0]
    adj = rng.choices(ADJUSTMENTS, weights=[5, 3, 3], k=1)[0]
    groove = rng.choices(GROOVE_POSITIONS_VALUES, weights=[3, 3, 2, 3], k=1)[0]
    hand = rng.choices(HANDLE_FORMS, weights=[5, 3, 3], k=1)[0]
    return PilersTongueGroovePliersConfig(
        jaw_form=jaw,
        adjustment=adj,
        groove_positions=groove,
        handle_form=hand,
        palette_style=rng.choice(PALETTE_STYLES),
        overall_len_scale=round(rng.uniform(0.92, 1.10), 4),
        jaw_face_scale=round(rng.uniform(0.92, 1.08), 4),
        grip_girth_scale=round(rng.uniform(0.92, 1.08), 4),
        open_angle_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pilers_tongue_groove_pliers_{seed}",
    )


def resolve_config(
    config: PilersTongueGroovePliersConfig | None = None,
) -> ResolvedConfig:
    cfg = config or PilersTongueGroovePliersConfig()
    jaw = _pick(cfg.jaw_form, JAW_FORMS)
    adj = _pick(cfg.adjustment, ADJUSTMENTS)
    groove = cfg.groove_positions if cfg.groove_positions in GROOVE_POSITIONS_VALUES else 8
    hand = _pick(cfg.handle_form, HANDLE_FORMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    overall = _clamp(cfg.overall_len_scale, 0.92, 1.10)
    jaw_face_s = _clamp(cfg.jaw_face_scale, 0.92, 1.08)
    grip_g = _clamp(cfg.grip_girth_scale, 0.92, 1.08)
    ang = _clamp(cfg.open_angle_scale, 0.85, 1.15)

    pivot_lower = _clamp(BASE_PIVOT_LOWER * ang, -1.25, -0.85)
    pivot_upper = _clamp(BASE_PIVOT_UPPER * ang, 0.30, 0.55)
    slide_upper = BASE_SLIDE_UPPER  # keep slot geometry constant

    return ResolvedConfig(
        jaw_form=jaw,
        adjustment=adj,
        groove_positions=groove,
        handle_form=hand,
        palette_style=palette,
        overall_len_scale=overall,
        jaw_face_scale=jaw_face_s,
        grip_girth_scale=grip_g,
        pivot_lower=pivot_lower,
        pivot_upper=pivot_upper,
        slide_upper=slide_upper,
        name=cfg.name or "pilers_tongue_groove_pliers",
    )


def with_overrides(
    config: PilersTongueGroovePliersConfig, **kwargs: object
) -> PilersTongueGroovePliersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: PilersTongueGroovePliersConfig | ResolvedConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("jaw_form", r.jaw_form),
        ("adjustment", r.adjustment),
        ("groove_positions", f"{r.groove_positions}_position"),
        ("handle_form", r.handle_form),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (P0 origin).
# ---------------------------------------------------------------------------
def _xz_prism(
    points: list[tuple[float, float]],
    thickness: float,
    *,
    y_center: float = 0.0,
    edge_radius: float = 0.0,
) -> cq.Workplane:
    solid = cq.Workplane("XZ").polyline(points).close().extrude(thickness / 2.0, both=True)
    if edge_radius > 0.0:
        try:
            solid = solid.edges("|Y").fillet(edge_radius)
        except Exception:
            pass
    return solid.translate((0.0, y_center, 0.0))


def _slot_cutter(
    *,
    length: float,
    width: float,
    direction: tuple[float, float],
    thickness: float,
) -> cq.Workplane:
    sx, sz = direction
    nx, nz = -sz, sx
    r = width / 2.0
    p0 = (0.0, 0.0)
    p1 = (sx * length, sz * length)
    rect = [
        (p0[0] + nx * r, p0[1] + nz * r),
        (p1[0] + nx * r, p1[1] + nz * r),
        (p1[0] - nx * r, p1[1] - nz * r),
        (p0[0] - nx * r, p0[1] - nz * r),
    ]
    cutter = _xz_prism(rect, thickness)
    for px, pz in (p0, p1):
        end = cq.Workplane("XZ").center(px, pz).circle(r).extrude(thickness / 2.0, both=True)
        cutter = cutter.union(end)
    return cutter


def _serration_strip(
    p0: tuple[float, float],
    p1: tuple[float, float],
    normal: tuple[float, float],
    *,
    count: int,
    tooth_height: float,
    thickness: float,
    y_center: float,
) -> cq.Workplane:
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    length = math.hypot(dx, dz)
    ux, uz = dx / length, dz / length
    nx, nz = normal
    base_depth = 0.0022
    face_land = 0.0006
    base = [
        (p0[0] - nx * base_depth, p0[1] - nz * base_depth),
        (p1[0] - nx * base_depth, p1[1] - nz * base_depth),
        (p1[0] + nx * face_land, p1[1] + nz * face_land),
        (p0[0] + nx * face_land, p0[1] + nz * face_land),
    ]
    strip = _xz_prism(base, thickness, y_center=y_center)
    pitch = length / max(count, 1)
    for i in range(count):
        a = (i + 0.12) * pitch
        b = (i + 0.88) * pitch
        m = (i + 0.50) * pitch
        tooth = [
            (p0[0] + ux * a, p0[1] + uz * a),
            (p0[0] + ux * b, p0[1] + uz * b),
            (p0[0] + ux * m + nx * tooth_height, p0[1] + uz * m + nz * tooth_height),
        ]
        strip = strip.union(_xz_prism(tooth, thickness, y_center=y_center))
    return strip


def _deep_v_pipe_jaw(
    p0: tuple[float, float],
    p1: tuple[float, float],
    face_normal: tuple[float, float],
    *,
    v_depth: float = 0.016,
    tooth_count_per_face: int = 5,
    tooth_height: float = 0.0024,
    thickness: float = 0.012,
    y_center: float = 0.0,
) -> cq.Workplane:
    nx, nz = face_normal
    mx = (p0[0] + p1[0]) / 2.0
    mz = (p0[1] + p1[1]) / 2.0
    vx = mx - nx * v_depth
    vz = mz - nz * v_depth
    vertex = (vx, vz)

    def outward(pa, pb):
        dx = pb[0] - pa[0]
        dz = pb[1] - pa[1]
        seg = math.hypot(dx, dz)
        cx, cz = dz / seg, -dx / seg
        if cx * nx + cz * nz >= 0:
            return (cx, cz)
        return (-cx, -cz)

    na = outward(p0, vertex)
    nb = outward(vertex, p1)

    fa = _serration_strip(
        p0,
        vertex,
        na,
        count=tooth_count_per_face,
        tooth_height=tooth_height,
        thickness=thickness,
        y_center=y_center,
    )
    fb = _serration_strip(
        vertex,
        p1,
        nb,
        count=tooth_count_per_face,
        tooth_height=tooth_height,
        thickness=thickness,
        y_center=y_center,
    )
    r_b = 0.003
    bridge = _xz_prism(
        [
            (vx - r_b, vz - r_b),
            (vx + r_b, vz - r_b),
            (vx + r_b, vz + r_b),
            (vx - r_b, vz + r_b),
        ],
        thickness,
        y_center=y_center,
    )
    return fa.union(fb).union(bridge)


def _smooth_jaw_pad(
    p0: tuple[float, float],
    p1: tuple[float, float],
    normal: tuple[float, float],
    *,
    thickness: float,
    pad_depth: float,
    face_land: float,
    y_center: float,
) -> cq.Workplane:
    nx, nz = normal
    pad = [
        (p0[0] - nx * pad_depth, p0[1] - nz * pad_depth),
        (p1[0] - nx * pad_depth, p1[1] - nz * pad_depth),
        (p1[0] + nx * face_land, p1[1] + nz * face_land),
        (p0[0] + nx * face_land, p0[1] + nz * face_land),
    ]
    return _xz_prism(pad, thickness, y_center=y_center)


# ---------------------------------------------------------------------------
# Grip polylines (Slot D).
# ---------------------------------------------------------------------------
_ROOT_STANDARD_GRIP = [
    (-0.002, -0.088),
    (0.027, -0.089),
    (0.034, -0.111),
    (0.034, -0.205),
    (0.031, -0.226),
    (0.024, -0.242),
    (0.014, -0.245),
    (0.006, -0.236),
    (0.004, -0.210),
]
_TONGUE_STANDARD_GRIP = [
    (-0.043, -0.089),
    (-0.017, -0.099),
    (-0.020, -0.125),
    (-0.033, -0.211),
    (-0.038, -0.234),
    (-0.046, -0.247),
    (-0.056, -0.246),
    (-0.064, -0.235),
    (-0.063, -0.216),
    (-0.050, -0.113),
]

# Extended leverage: prolong grip further into -Y.
_ROOT_EXTENDED_GRIP = [
    (-0.002, -0.088),
    (0.028, -0.089),
    (0.036, -0.115),
    (0.037, -0.240),
    (0.033, -0.276),
    (0.024, -0.294),
    (0.014, -0.297),
    (0.005, -0.288),
    (0.003, -0.245),
]
_TONGUE_EXTENDED_GRIP = [
    (-0.043, -0.089),
    (-0.017, -0.099),
    (-0.022, -0.130),
    (-0.037, -0.248),
    (-0.042, -0.278),
    (-0.050, -0.296),
    (-0.060, -0.296),
    (-0.068, -0.285),
    (-0.067, -0.256),
    (-0.050, -0.115),
]

# Guarded grip: add a finger-guard bulge near the top of the grip.
_ROOT_GUARDED_GRIP = [
    (-0.002, -0.088),
    (0.030, -0.088),
    (0.043, -0.095),
    (0.044, -0.108),
    (0.036, -0.118),
    (0.034, -0.205),
    (0.031, -0.226),
    (0.024, -0.242),
    (0.014, -0.245),
    (0.006, -0.236),
    (0.004, -0.210),
]
_TONGUE_GUARDED_GRIP = [
    (-0.043, -0.089),
    (-0.017, -0.099),
    (-0.028, -0.108),
    (-0.030, -0.118),
    (-0.022, -0.130),
    (-0.033, -0.211),
    (-0.038, -0.234),
    (-0.046, -0.247),
    (-0.056, -0.246),
    (-0.064, -0.235),
    (-0.063, -0.216),
    (-0.050, -0.113),
]


_ROOT_GRIP_OUTLINES: dict[HandleForm, list[tuple[float, float]]] = {
    "standard_dipped": _ROOT_STANDARD_GRIP,
    "extended_leverage_handle": _ROOT_EXTENDED_GRIP,
    "guarded_grip": _ROOT_GUARDED_GRIP,
}
_TONGUE_GRIP_OUTLINES: dict[HandleForm, list[tuple[float, float]]] = {
    "standard_dipped": _TONGUE_STANDARD_GRIP,
    "extended_leverage_handle": _TONGUE_EXTENDED_GRIP,
    "guarded_grip": _TONGUE_GUARDED_GRIP,
}


def _scale_grip(
    outline: list[tuple[float, float]], *, x_scale: float, y_scale: float
) -> list[tuple[float, float]]:
    return [(x * x_scale, y * y_scale) for x, y in outline]


# ---------------------------------------------------------------------------
# Shank profiles (P0 origin).
# ---------------------------------------------------------------------------
_ROOT_PROFILE = [
    (-0.052, 0.073),
    (-0.060, 0.063),
    (-0.060, 0.052),
    (-0.053, 0.035),
    (-0.043, 0.017),
    (-0.039, -0.013),
    (-0.029, -0.056),
    (-0.006, -0.105),
    (0.011, -0.214),
    (0.024, -0.224),
    (0.030, -0.214),
    (0.030, -0.106),
    (0.024, -0.061),
    (0.020, -0.028),
    (0.026, 0.004),
    (0.021, 0.025),
    (0.008, 0.038),
    (-0.011, 0.031),
    (-0.048, 0.063),
]

_TONGUE_PROFILE = [
    (-0.038, 0.073),
    (-0.002, 0.041),
    (0.017, 0.032),
    (0.031, 0.014),
    (0.034, -0.006),
    (0.026, -0.026),
    (0.008, -0.047),
    (-0.010, -0.067),
    (-0.033, -0.106),
    (-0.056, -0.207),
    (-0.052, -0.225),
    (-0.043, -0.233),
    (-0.034, -0.226),
    (-0.020, -0.116),
    (-0.002, -0.083),
    (0.019, -0.056),
    (0.038, -0.025),
    (0.046, 0.004),
    (0.045, 0.029),
    (0.035, 0.054),
    (0.016, 0.073),
    (-0.027, 0.087),
]

# Root jaw face (line segment for serration / pad).
_ROOT_JAW_P0 = (-0.048, 0.063)
_ROOT_JAW_P1 = (-0.011, 0.031)
_ROOT_JAW_NORMAL: tuple[float, float] = (0.655, 0.756)

# Tongue jaw face.
_TONGUE_JAW_P0 = (-0.038, 0.073)
_TONGUE_JAW_P1 = (-0.002, 0.041)
_TONGUE_JAW_NORMAL: tuple[float, float] = (-0.655, -0.756)


def _y_scale_points(pts: list[tuple[float, float]], factor: float) -> list[tuple[float, float]]:
    return [(x, y * factor) for x, y in pts]


# ---------------------------------------------------------------------------
# Jaw face dispatch.
# ---------------------------------------------------------------------------
def _make_jaw_face(
    r: ResolvedConfig,
    *,
    which: str,  # "root" or "tongue"
    thickness: float,
    y_center: float,
) -> tuple[cq.Workplane, str]:
    """Return (workplane, visual_name) for the jaw face on the given shank."""
    if which == "root":
        p0, p1 = _ROOT_JAW_P0, _ROOT_JAW_P1
        normal = _ROOT_JAW_NORMAL
    else:
        p0, p1 = _TONGUE_JAW_P0, _TONGUE_JAW_P1
        normal = _TONGUE_JAW_NORMAL

    if r.jaw_form == "straight_serrated":
        wp = _serration_strip(
            p0,
            p1,
            normal,
            count=9,
            tooth_height=0.0024 * r.jaw_face_scale,
            thickness=thickness,
            y_center=y_center,
        )
        return wp, "straight_jaw_serrations"
    if r.jaw_form == "narrow_offset_jaw":
        wp = _serration_strip(
            p0,
            p1,
            normal,
            count=7,
            tooth_height=0.0020 * r.jaw_face_scale,
            thickness=thickness * 0.85,
            y_center=y_center,
        )
        return wp, "straight_jaw_serrations"
    if r.jaw_form == "deep_v_pipe_jaw":
        wp = _deep_v_pipe_jaw(
            p0,
            p1,
            normal,
            v_depth=0.016 * r.jaw_face_scale,
            tooth_count_per_face=5,
            tooth_height=0.0024 * r.jaw_face_scale,
            thickness=thickness,
            y_center=y_center,
        )
        return wp, "deep_v_pipe_jaw"
    # replaceable_smooth_pads
    wp = _smooth_jaw_pad(
        p0,
        p1,
        normal,
        thickness=thickness,
        pad_depth=0.0018,
        face_land=0.0022 * r.jaw_face_scale,
        y_center=y_center,
    )
    return wp, "smooth_jaw_pad"


# ---------------------------------------------------------------------------
# Slotted shank forging + tooth cuts (Slot C multiplicity).
# ---------------------------------------------------------------------------
def _build_slotted_forging(
    r: ResolvedConfig,
) -> cq.Workplane:
    forging = _xz_prism(_ROOT_PROFILE, 0.008, edge_radius=0.0013)
    # Through slot (constant length).
    forging = forging.cut(
        _slot_cutter(
            length=SLOT_LENGTH,
            width=SLOT_WIDTH,
            direction=SLOT_AXIS,
            thickness=0.030,
        )
    )
    # Slot C: N tooth cuts along slot axis.
    sx, sz = SLOT_AXIS
    nx, nz = SLOT_NORMAL
    n = r.groove_positions
    slot_start = 0.009
    slot_end = SLOT_LENGTH - 0.009
    if n > 1:
        pitch = (slot_end - slot_start) / (n - 1)
    else:
        pitch = 0.0
    tooth_len = min(0.0037, max(0.0022, pitch * 0.55)) if pitch > 0.0 else 0.0037
    for i in range(n):
        v0 = slot_start + i * pitch if n > 1 else (slot_start + slot_end) * 0.5
        v1 = v0 + tooth_len
        vm = (v0 + v1) / 2.0
        tooth_cut = [
            (sx * v0 + nx * 0.0052, sz * v0 + nz * 0.0052),
            (sx * v1 + nx * 0.0052, sz * v1 + nz * 0.0052),
            (sx * vm + nx * 0.0080, sz * vm + nz * 0.0080),
        ]
        forging = forging.cut(_xz_prism(tooth_cut, 0.030))

    if r.adjustment == "box_joint_opening":
        # Widen visual box-joint window: cut a rect around the slot mouth
        # so the shank reads as an open box-joint opening.
        # Placed at the mid-slot region (world position ~ mid).
        mid_x = sx * (SLOT_LENGTH / 2.0)
        mid_z = sz * (SLOT_LENGTH / 2.0)
        window = (
            cq.Workplane("XZ")
            .center(mid_x + nx * 0.001, mid_z + nz * 0.001)
            .rect(0.006, 0.006)
            .extrude(0.030, both=True)
        )
        try:
            forging = forging.cut(window)
        except Exception:
            pass
    return forging


def _build_tongue_forging() -> cq.Workplane:
    forging = _xz_prism(_TONGUE_PROFILE, 0.006, y_center=0.008, edge_radius=0.0012)
    pivot_boss = (
        cq.Workplane("XZ").circle(0.018).extrude(0.003, both=True).translate((0.0, 0.008, 0.0))
    )
    pivot_bridge = _xz_prism(
        [(-0.012, -0.013), (0.039, -0.013), (0.039, 0.017), (-0.012, 0.017)],
        0.006,
        y_center=0.008,
        edge_radius=0.001,
    )
    forging = forging.union(pivot_boss).union(pivot_bridge)
    pivot_bore = (
        cq.Workplane("XZ").circle(0.00475).extrude(0.020, both=True).translate((0.0, 0.008, 0.0))
    )
    return forging.cut(pivot_bore)


def _build_engaging_tongue() -> cq.Workplane:
    sx, sz = SLOT_AXIS
    nx, nz = SLOT_NORMAL
    tongue_center_v = 0.016
    tongue_half_v = 0.010
    u0 = -0.0036
    u1 = 0.0046

    def sp(u: float, v: float) -> tuple[float, float]:
        return (sx * v + nx * u, sz * v + nz * u)

    outline = [
        sp(u0, tongue_center_v - tongue_half_v),
        sp(u1, tongue_center_v - tongue_half_v),
        sp(0.0053, tongue_center_v),
        sp(u1, tongue_center_v + tongue_half_v),
        sp(u0, tongue_center_v + tongue_half_v),
    ]
    return _xz_prism(outline, 0.010, y_center=0.001)


# ---------------------------------------------------------------------------
# Pivot carriage variants (Slot B).
# ---------------------------------------------------------------------------
def _round_rivet() -> cq.Workplane:
    shaft = (
        cq.Workplane("XZ").circle(0.0042).extrude(0.0095, both=True).translate((0.0, 0.0035, 0.0))
    )
    rear_head = (
        cq.Workplane("XZ")
        .circle(0.0072)
        .extrude(0.00125, both=True)
        .translate((0.0, -0.00525, 0.0))
    )
    front_head = (
        cq.Workplane("XZ").circle(0.0072).extrude(0.00125, both=True).translate((0.0, 0.01225, 0.0))
    )
    return shaft.union(rear_head).union(front_head)


def _pushbutton_carriage_body() -> cq.Workplane:
    body = (
        cq.Workplane("XZ")
        .rect(0.0105, 0.014)
        .extrude(0.018, both=True)
        .translate((0.0, 0.003, 0.0))
    )
    try:
        body = body.edges("|Y").fillet(0.0018)
    except Exception:
        pass
    top_flange = (
        cq.Workplane("XZ")
        .rect(0.014, 0.017)
        .extrude(0.0014, both=True)
        .translate((0.0, 0.0127, 0.0))
    )
    try:
        top_flange = top_flange.edges("|Y").fillet(0.002)
    except Exception:
        pass
    bot_flange = (
        cq.Workplane("XZ")
        .rect(0.014, 0.017)
        .extrude(0.0014, both=True)
        .translate((0.0, -0.0057, 0.0))
    )
    try:
        bot_flange = bot_flange.edges("|Y").fillet(0.002)
    except Exception:
        pass
    body = body.union(top_flange).union(bot_flange)
    pivot_bore = (
        cq.Workplane("XZ").circle(0.00475).extrude(0.025, both=True).translate((0.0, 0.003, 0.0))
    )
    body = body.cut(pivot_bore)
    button_bore = (
        cq.Workplane("XZ").circle(0.0028).extrude(0.012, both=True).translate((0.0, 0.009, -0.004))
    )
    return body.cut(button_bore)


def _push_button_geom() -> cq.Workplane:
    # Positioned in the button's local frame with base at y=0. The joint
    # origin y-offset places the whole part above the carriage top flange.
    shaft = (
        cq.Workplane("XZ").circle(0.0025).extrude(0.0025, both=True).translate((0.0, 0.0025, 0.0))
    )
    cap = cq.Workplane("XZ").circle(0.0038).extrude(0.0012, both=True).translate((0.0, 0.0062, 0.0))
    try:
        cap = cap.edges("|Y").fillet(0.0006)
    except Exception:
        pass
    grip_ring = (
        cq.Workplane("XZ").circle(0.0042).extrude(0.0005, both=True).translate((0.0, 0.0079, 0.0))
    )
    return shaft.union(cap).union(grip_ring)


# ---------------------------------------------------------------------------
# Builders.
# ---------------------------------------------------------------------------
def build_pilers_tongue_groove_pliers(
    config: PilersTongueGroovePliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "overall_length_m": 0.325 * r.overall_len_scale,
            "asset_count": 1,
        },
    )
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"ptgp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    # ------------------------------------------------------------------
    # slotted_shank (ROOT).
    # ------------------------------------------------------------------
    slotted_shank = model.part(
        "slotted_shank",
        meta={
            "role": "forged shank with true through adjustment slot",
            "through_slot": True,
            "slot_length_m": SLOT_LENGTH,
            "slot_width_m": SLOT_WIDTH,
            "slot_tooth_count": r.groove_positions,
            "groove_position_count": r.groove_positions,
            "jaw_face_style": (
                "deep_v_pipe_jaw"
                if r.jaw_form == "deep_v_pipe_jaw"
                else "replaceable_smooth_pad"
                if r.jaw_form == "replaceable_smooth_pads"
                else "straight_opposing_serration_row"
            ),
            "jaw_form": r.jaw_form,
            "handle_form": r.handle_form,
            "adjustment": r.adjustment,
        },
    )
    root_forging = _build_slotted_forging(r)
    slotted_shank.visual(
        mesh_from_cadquery(root_forging, "slotted_forging", tolerance=0.00035),
        material=mats["forged"],
        name="slotted_forging", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_red", "chrome_dark_blue", "black_yellow", "brushed_steel_orange"} else "metal.steel_bare"),
    )
    # Jaw face on root.
    root_jaw_wp, root_jaw_name = _make_jaw_face(r, which="root", thickness=0.012, y_center=0.002)
    slotted_shank.visual(
        mesh_from_cadquery(root_jaw_wp, "slotted_jaw_face", tolerance=0.00025),
        material=mats["jaw_steel"],
        name=root_jaw_name, material_class_id="metal.blackened_gunmetal",
    )
    # Grip on root.
    root_grip_outline = _scale_grip(
        _ROOT_GRIP_OUTLINES[r.handle_form],
        x_scale=r.grip_girth_scale,
        y_scale=r.overall_len_scale,
    )
    root_grip = _xz_prism(root_grip_outline, 0.017, edge_radius=0.003)
    slotted_shank.visual(
        mesh_from_cadquery(root_grip, "slotted_blue_grip", tolerance=0.00045),
        material=mats["grip"],
        name="blue_handle_grip", material_class_id="rubber.smooth_plain",
    )

    # ------------------------------------------------------------------
    # pivot_carriage.
    # ------------------------------------------------------------------
    pivot_carriage = model.part(
        "pivot_carriage",
        meta={
            "role": "captured sliding pivot hardware",
            "adjustment": r.adjustment,
            "hardware": (
                "push_button_carriage" if r.adjustment == "push_button_carriage" else "round_rivet"
            ),
            "captured_in_slot": True,
        },
    )
    if r.adjustment == "push_button_carriage":
        body = _pushbutton_carriage_body()
        pivot_carriage.visual(
            mesh_from_cadquery(body, "push_button_carriage_body", tolerance=0.0003),
            material=mats["forged"],
            name="carriage_body", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_red", "chrome_dark_blue", "black_yellow", "brushed_steel_orange"} else "metal.steel_bare"),
        )
        # Also emit a small pivot_rivet visual for uniform overlap semantics.
        rivet = _round_rivet()
        pivot_carriage.visual(
            mesh_from_cadquery(rivet, "pushbutton_rivet_shaft", tolerance=0.00025),
            material=mats["forged"],
            name="pivot_rivet", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_red", "chrome_dark_blue", "black_yellow", "brushed_steel_orange"} else "metal.steel_bare"),
        )
    else:
        rivet = _round_rivet()
        pivot_carriage.visual(
            mesh_from_cadquery(rivet, "round_pivot_rivet", tolerance=0.00025),
            material=mats["forged"],
            name="pivot_rivet", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"gunmetal_red", "chrome_dark_blue", "black_yellow", "brushed_steel_orange"} else "metal.steel_bare"),
        )

    # ------------------------------------------------------------------
    # tongue_shank.
    # ------------------------------------------------------------------
    tongue_shank = model.part(
        "tongue_shank",
        meta={
            "role": "crossing forged shank with solid engaging tongue",
            "solid_tongue": True,
            "jaw_face_style": slotted_shank.meta["jaw_face_style"],
            "jaw_form": r.jaw_form,
            "handle_form": r.handle_form,
        },
    )
    tongue_forging = _build_tongue_forging()
    tongue_shank.visual(
        mesh_from_cadquery(tongue_forging, "tongue_forging", tolerance=0.00035),
        material=mats["dark_steel"],
        name="tongue_forging", material_class_id="metal.blackened_gunmetal",
    )
    engaging_tongue = _build_engaging_tongue()
    tongue_shank.visual(
        mesh_from_cadquery(engaging_tongue, "engaging_tongue", tolerance=0.0002),
        material=mats["dark_steel"],
        name="engaging_tongue", material_class_id="metal.blackened_gunmetal",
    )
    tongue_jaw_wp, tongue_jaw_name = _make_jaw_face(
        r, which="tongue", thickness=0.012, y_center=0.004
    )
    tongue_shank.visual(
        mesh_from_cadquery(tongue_jaw_wp, "tongue_jaw_face", tolerance=0.00025),
        material=mats["jaw_steel"],
        name=tongue_jaw_name, material_class_id="metal.blackened_gunmetal",
    )
    tongue_grip_outline = _scale_grip(
        _TONGUE_GRIP_OUTLINES[r.handle_form],
        x_scale=r.grip_girth_scale,
        y_scale=r.overall_len_scale,
    )
    tongue_grip = _xz_prism(
        tongue_grip_outline,
        0.017,
        y_center=0.008,
        edge_radius=0.003,
    )
    tongue_shank.visual(
        mesh_from_cadquery(tongue_grip, "tongue_blue_grip", tolerance=0.00045),
        material=mats["grip"],
        name="blue_handle_grip", material_class_id="rubber.smooth_plain",
    )

    # ------------------------------------------------------------------
    # Joints.
    # ------------------------------------------------------------------
    model.articulation(
        "slot_setting",
        ArticulationType.PRISMATIC,
        parent=slotted_shank,
        child=pivot_carriage,
        origin=Origin(),
        axis=(SLOT_AXIS[0], 0.0, SLOT_AXIS[1]),
        motion_limits=MotionLimits(
            effort=180.0,
            velocity=0.08,
            lower=0.0,
            upper=r.slide_upper,
        ),
        motion_properties=MotionProperties(damping=2.0, friction=8.0),
        meta={
            "mechanism": "guided captured adjustment along toothed through-slot",
        },
    )
    model.articulation(
        "jaw_pivot",
        ArticulationType.REVOLUTE,
        parent=pivot_carriage,
        child=tongue_shank,
        origin=Origin(),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=240.0,
            velocity=2.2,
            lower=r.pivot_lower,
            upper=r.pivot_upper,
        ),
        motion_properties=MotionProperties(damping=0.35, friction=0.8),
        meta={
            "mechanism": "shanks rotate about captured pivot; negative tilt disengages tongue and guides slot adjustment",
        },
    )

    if r.has_button:
        push_button = model.part(
            "push_button",
            meta={
                "role": "spring-loaded push-button quick release",
                "button_type": "push_button",
                "press_travel_m": 0.004,
            },
        )
        push_button.visual(
            mesh_from_cadquery(_push_button_geom(), "push_button_geom", tolerance=0.0003),
            material=mats["button"],
            name="button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "button_press",
            ArticulationType.PRISMATIC,
            parent=pivot_carriage,
            child=push_button,
            origin=Origin(xyz=(0.0, 0.0125, -0.004)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(
                effort=25.0,
                velocity=0.15,
                lower=0.0,
                upper=0.004,
            ),
            motion_properties=MotionProperties(damping=4.0, friction=1.5),
            meta={
                "mechanism": "spring-loaded push-button release",
            },
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_tongue_groove_pliers(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pilers_tongue_groove_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_pilers_tongue_groove_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersTongueGroovePliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    slotted = object_model.get_part("slotted_shank")
    carriage = object_model.get_part("pivot_carriage")
    tongue = object_model.get_part("tongue_shank")
    setting = object_model.get_articulation("slot_setting")
    pivot = object_model.get_articulation("jaw_pivot")

    # Captured-pin allowances.
    ctx.allow_overlap(
        carriage,
        slotted,
        elem_a="pivot_rivet",
        elem_b="slotted_forging",
        reason=(
            "The pivot rivet is captured in the toothed through-slot of the slotted "
            "shank across the full guided-adjustment travel."
        ),
    )
    ctx.allow_overlap(
        carriage,
        tongue,
        elem_a="pivot_rivet",
        elem_b="tongue_forging",
        reason=(
            "The rivet shaft is intentionally captured through the tongue shank's "
            "pivot boss (captured-pin joint)."
        ),
    )
    ctx.allow_overlap(
        tongue,
        slotted,
        elem_a="engaging_tongue",
        elem_b="slotted_forging",
        reason=(
            "The solid engaging tongue seats against the toothed wall of the true "
            "through-slot while remaining captured across adjustment settings."
        ),
    )
    # Two crossed shanks share a z-lap at the pivot region.
    ctx.allow_overlap(
        slotted,
        tongue,
        elem_a="slotted_forging",
        elem_b="tongue_forging",
        reason=(
            "The two crossed forged plier shanks overlap in z at the pivot boss "
            "region where the captured rivet joins them."
        ),
    )
    # Pivot rivet threads through the engaging tongue (captured-pin geometry).
    ctx.allow_overlap(
        carriage,
        tongue,
        elem_a="pivot_rivet",
        elem_b="engaging_tongue",
        reason=(
            "The pivot rivet shaft passes through the engaging tongue's seating "
            "region as part of the captured-pin joint."
        ),
    )
    # Closed-pose jaw bite: tongue's jaw face seats against the slotted forging.
    jaw_names_seen: set[str] = {
        "straight_jaw_serrations",
        "deep_v_pipe_jaw",
        "smooth_jaw_pad",
    }
    for jaw_name in jaw_names_seen:
        ctx.allow_overlap(
            slotted,
            tongue,
            elem_a="slotted_forging",
            elem_b=jaw_name,
            reason=(
                "In the closed pose the tongue shank's jaw face seats against the "
                "slotted shank's forged body (the pliers bite)."
            ),
        )
        ctx.allow_overlap(
            tongue,
            slotted,
            elem_a="tongue_forging",
            elem_b=jaw_name,
            reason=(
                "In the closed pose the slotted shank's jaw face seats against "
                "the tongue shank's forged body (the pliers bite)."
            ),
        )
    # Opposing jaw faces meet in the closed pose (bite contact).
    for jaw_name in jaw_names_seen:
        ctx.allow_overlap(
            slotted,
            tongue,
            elem_a=jaw_name,
            elem_b=jaw_name,
            reason=(
                "Opposing jaw faces meet in the closed / gripping pose across the captured pivot."
            ),
        )
    # Handle grips can converge in extreme closed poses.
    ctx.allow_overlap(
        slotted,
        tongue,
        elem_a="blue_handle_grip",
        elem_b="blue_handle_grip",
        reason=(
            "In extreme closed poses the two vinyl handle grips converge past "
            "each other at the handle crossing."
        ),
    )
    if r.adjustment == "push_button_carriage":
        push_button_part = object_model.get_part("push_button")
        # Button seats into the carriage's counter-bore.
        ctx.allow_overlap(
            carriage,
            push_button_part,
            elem_a="carriage_body",
            elem_b="button_cap",
            reason=(
                "The push-button seats into the carriage body's counter-bore at "
                "rest and along its short press travel."
            ),
        )
        ctx.allow_overlap(
            carriage,
            push_button_part,
            elem_a="pivot_rivet",
            elem_b="button_cap",
            reason=(
                "The push-button seats close to the retention flange around the "
                "carriage's rivet visual on the outward face."
            ),
        )
        # Extra carriage-body overlap allowances.
        ctx.allow_overlap(
            carriage,
            slotted,
            elem_a="carriage_body",
            elem_b="slotted_forging",
            reason=(
                "The push-button carriage body rides captured in the through-slot; "
                "the retention flanges intentionally overlap the outside faces."
            ),
        )
        ctx.allow_overlap(
            carriage,
            tongue,
            elem_a="carriage_body",
            elem_b="tongue_forging",
            reason=(
                "The push-button carriage body shares the pivot boss z-lap with "
                "the tongue shank at the captured jaw_pivot joint."
            ),
        )
        ctx.allow_overlap(
            carriage,
            tongue,
            elem_a="carriage_body",
            elem_b="engaging_tongue",
            reason=(
                "The push-button carriage body wraps the engaging tongue seating "
                "region as part of the captured slip-joint pivot."
            ),
        )
    if r.handle_form == "guarded_grip":
        ctx.allow_overlap(
            tongue,
            slotted,
            elem_a="blue_handle_grip",
            elem_b="slotted_forging",
            reason=(
                "The tongue shank's finger-guard grip flange passes near the slotted "
                "shank body at the handle crossing on guarded-grip variants."
            ),
        )
        ctx.allow_overlap(
            slotted,
            tongue,
            elem_a="blue_handle_grip",
            elem_b="tongue_forging",
            reason=(
                "The slotted shank's finger-guard grip flange passes near the tongue "
                "shank body at the handle crossing on guarded-grip variants."
            ),
        )

    # Topology sanity.
    expected_parts = 4 if r.has_button else 3
    expected_joints = 3 if r.has_button else 2
    ctx.check(
        f"chain topology is {expected_parts}-part / {expected_joints}-joint",
        len(object_model.parts) == expected_parts
        and len(object_model.articulations) == expected_joints,
        details=(f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}"),
    )

    # slot_setting is PRISMATIC along slot_axis.
    ctx.check(
        "slot_setting PRISMATIC along slot_axis",
        setting.articulation_type == ArticulationType.PRISMATIC
        and setting.parent == "slotted_shank"
        and setting.child == "pivot_carriage"
        and setting.motion_limits is not None
        and math.isclose(setting.motion_limits.upper or 0.0, r.slide_upper, abs_tol=1e-9),
        details=f"limits={setting.motion_limits}",
    )
    ctx.check(
        "jaw_pivot REVOLUTE about +Y with negative-open and positive-close range",
        pivot.articulation_type == ArticulationType.REVOLUTE
        and pivot.parent == "pivot_carriage"
        and pivot.child == "tongue_shank"
        and pivot.motion_limits is not None
        and pivot.motion_limits.lower is not None
        and pivot.motion_limits.lower < 0.0
        and pivot.motion_limits.upper is not None
        and pivot.motion_limits.upper > 0.0,
        details=f"limits={pivot.motion_limits}",
    )

    # Slot C multiplicity: groove_positions metadata is exposed.
    ctx.check(
        f"slotted_shank exposes groove_positions={r.groove_positions}",
        slotted.meta.get("groove_position_count") == r.groove_positions
        and slotted.meta.get("slot_tooth_count") == r.groove_positions,
        details=f"meta={slotted.meta}",
    )

    # Slot A visual claim: jaw_face visual exists on both shanks.
    jaw_names = {
        "straight_serrated": "straight_jaw_serrations",
        "narrow_offset_jaw": "straight_jaw_serrations",
        "deep_v_pipe_jaw": "deep_v_pipe_jaw",
        "replaceable_smooth_pads": "smooth_jaw_pad",
    }
    expected_name = jaw_names[r.jaw_form]
    ctx.check(
        f"both shanks carry the {expected_name} jaw visual",
        slotted.get_visual(expected_name) is not None
        and tongue.get_visual(expected_name) is not None,
        details=(
            f"slotted visuals={[v.name for v in slotted.visuals]}, "
            f"tongue visuals={[v.name for v in tongue.visuals]}"
        ),
    )

    # Slot D handle_form propagates.
    ctx.check(
        "handle_form propagates to both shanks",
        slotted.meta.get("handle_form") == r.handle_form
        and tongue.meta.get("handle_form") == r.handle_form,
        details=f"handle_form={r.handle_form}",
    )

    # ---- Kinematics: slide moves carriage along -X and -Z (slanted axis). ----
    rest_carriage = ctx.part_world_position(carriage)
    with ctx.pose({setting: r.slide_upper}):
        far_carriage = ctx.part_world_position(carriage)
    ctx.check(
        "slot_setting slides the pivot carriage along slot_axis",
        rest_carriage is not None
        and far_carriage is not None
        and far_carriage[0] < rest_carriage[0] - 0.005
        and far_carriage[2] < rest_carriage[2] - 0.020,
        details=f"rest={rest_carriage}, far={far_carriage}",
    )

    # ---- Kinematics: jaw_pivot moves the tongue shank grip. ----
    grip_rest = ctx.part_element_world_aabb(tongue, elem="blue_handle_grip")
    with ctx.pose({pivot: r.pivot_lower * 0.7}):
        grip_open = ctx.part_element_world_aabb(tongue, elem="blue_handle_grip")
    if grip_rest is not None and grip_open is not None:
        rest_x = 0.5 * (grip_rest[0][0] + grip_rest[1][0])
        open_x = 0.5 * (grip_open[0][0] + grip_open[1][0])
        rest_z = 0.5 * (grip_rest[0][2] + grip_rest[1][2])
        open_z = 0.5 * (grip_open[0][2] + grip_open[1][2])
        ctx.check(
            "jaw_pivot rotates the tongue shank grip",
            abs(open_x - rest_x) > 0.015 or abs(open_z - rest_z) > 0.015,
            details=(f"rest=({rest_x:.4f}, {rest_z:.4f}), open=({open_x:.4f}, {open_z:.4f})"),
        )

    if r.has_button:
        button_joint = object_model.get_articulation("button_press")
        push_button = object_model.get_part("push_button")
        rest_btn = ctx.part_world_aabb(push_button)
        with ctx.pose({button_joint: 0.004}):
            pressed_btn = ctx.part_world_aabb(push_button)
        ctx.check(
            "push button presses inward along -Y",
            rest_btn is not None
            and pressed_btn is not None
            and pressed_btn[0][1] < rest_btn[0][1] - 0.0005,
            details=f"rest={rest_btn}, pressed={pressed_btn}",
        )

    # Broad sampled-pose collision guard.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # Slot choices metadata.
    ctx.check(
        "slot_choices metadata reflects picks",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersTongueGroovePliersConfig",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "with_overrides",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_tongue_groove_pliers",
    "build_seeded_pilers_tongue_groove_pliers",
    "run_pilers_tongue_groove_pliers_tests",
    "__modular__",
]
