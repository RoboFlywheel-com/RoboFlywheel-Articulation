# SPDX-License-Identifier: Apache-2.0

"""Locking pliers modular template (0611 / pilers_locking_pliers).

Sourced from the modular spec
``articraft_template_authoring/specs_modular_v1/pilers_locking_pliers.md`` and the
``pictureX/0611/Pilers_locking_pliers`` 5-star pool (origin
``curved_jaw_locking_pliers`` + 8 single-axis fork variants).

Structure (pattern ``mixed``): every 5-star sample shares ONE fixed 7-part /
6-joint over-center toggle skeleton — no fork adds or removes a part/joint.
Diversity is form-dominated: the registered ③ Primary Form Family slot is
``jaw_form``; three secondary form/mechanism slots swap the recognizable
geometry (and one joint-axis sign) of specific parts.

Skeleton (root = ``jaw_frame``)::

    jaw_frame ─jaw_pivot(REV +Z)──────────> movable_jaw       (Slot A form + Slot B coupling)
             ─upper_handle_pivot(REV +Z)──> upper_handle
             │      └adjustment_travel(PRIS −Y)─> adjustment_screw   (Slot D)
             ─lower_handle_pivot(REV +Z)──> lower_handle
                    ├linkage_pivot(REV +Z)──> locking_link    (Slot B)
                    └release_lever_pivot(REV ±Z)─> release_lever     (Slot C)

Slots:

* ``jaw_form`` (4): curved_jaw / long_nose_jaw / c_clamp_jaw / sheet_metal_wide_jaw.
* ``locking_mechanism`` (2): classic_toggle_link / compound_jaw_linkage.
* ``release`` (2): captured_thumb_lever / one_hand_push_release (axis sign flip).
* ``adjustment`` (2): captured_knurled_screw / quick_adjust_thumbwheel.

``palette_style`` (6): rgba axis only; not in slot_choices, does not change topology.

All pivots are pin-through-plate captured pins → grandfathered (no MatingContract);
captured contact is asserted with element-scoped ``allow_overlap`` + ``expect_contact``.
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
    ExtrudeGeometry,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Enum axes
# ---------------------------------------------------------------------------
JawForm = Literal["curved_jaw", "long_nose_jaw", "c_clamp_jaw", "sheet_metal_wide_jaw"]
LockingMechanism = Literal["classic_toggle_link", "compound_jaw_linkage"]
Release = Literal["captured_thumb_lever", "one_hand_push_release"]
Adjustment = Literal["captured_knurled_screw", "quick_adjust_thumbwheel"]
PaletteStyle = Literal[
    "polished_steel",
    "nickel_bright",
    "black_oxide_red",
    "blue_dipped",
    "gunmetal_yellow",
    "raw_forged_grey",
]

JAW_FORMS: tuple[JawForm, ...] = (
    "curved_jaw",
    "long_nose_jaw",
    "c_clamp_jaw",
    "sheet_metal_wide_jaw",
)
LOCKING_MECHANISMS: tuple[LockingMechanism, ...] = (
    "classic_toggle_link",
    "compound_jaw_linkage",
)
RELEASES: tuple[Release, ...] = ("captured_thumb_lever", "one_hand_push_release")
ADJUSTMENTS: tuple[Adjustment, ...] = (
    "captured_knurled_screw",
    "quick_adjust_thumbwheel",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "polished_steel",
    "nickel_bright",
    "black_oxide_red",
    "blue_dipped",
    "gunmetal_yellow",
    "raw_forged_grey",
)

# Plate / handle extrusion thicknesses (origin source constants).
PLATE_THICKNESS = 0.006
HANDLE_THICKNESS = 0.005
WIDE_JAW_WIDTH = 0.032  # sheet_metal_wide grip-face extrusion (var record L24).

# Per-jaw-form REVOLUTE pivot location on the jaw_frame (metres). c_clamp lowers
# the pivot to seat the deep C-frame (var_jaw_form_c_clamp L461-474).
JAW_PIVOTS: dict[JawForm, tuple[float, float]] = {
    "curved_jaw": (0.010, 0.028),
    "long_nose_jaw": (0.010, 0.028),
    "c_clamp_jaw": (0.010, 0.018),
    "sheet_metal_wide_jaw": (0.010, 0.028),
}

# Baseline REVOLUTE / PRISMATIC motion envelopes (origin motion_limits). +θ about
# +Z closes the jaws; the ranges keep a positive gap across jaw_scale (verified by
# the sampled-pose collision gate).
# A locking plier rests near its clamped position: the movable jaw mainly OPENS
# (−θ). Closing (+θ) past rest is kept tiny so no jaw form (esp. the thick wide
# grip faces) bites the fixed jaw within the sampled-pose overlap tolerance.
BASE_JAW_LOWER = -0.20
BASE_JAW_UPPER = 0.03
BASE_UPPER_HANDLE_LOWER = -0.08
BASE_UPPER_HANDLE_UPPER = 0.08
BASE_LOWER_HANDLE_LOWER = -0.10
BASE_LOWER_HANDLE_UPPER = 0.22
BASE_LINKAGE_LOWER = -0.15
BASE_LINKAGE_UPPER = 0.20
BASE_RELEASE_LOWER = -0.12
BASE_RELEASE_UPPER = 0.32

# ---------------------------------------------------------------------------
# Palettes. Each provides the four material rgba keys every visual references.
# metal category = body/bright/dark; painted category = accent (red/blue/yellow
# on the coloured palettes, dark oxide on the steel palettes).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "polished_steel": {
        "body": (0.78, 0.80, 0.82, 1.0),
        "bright": (0.90, 0.91, 0.92, 1.0),
        "dark": (0.34, 0.35, 0.37, 1.0),
        "accent": (0.055, 0.055, 0.060, 1.0),
    },
    "nickel_bright": {
        "body": (0.86, 0.88, 0.90, 1.0),
        "bright": (0.93, 0.94, 0.96, 1.0),
        "dark": (0.42, 0.44, 0.46, 1.0),
        "accent": (0.12, 0.13, 0.15, 1.0),
    },
    "black_oxide_red": {
        "body": (0.20, 0.20, 0.22, 1.0),
        "bright": (0.55, 0.56, 0.58, 1.0),
        "dark": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.74, 0.10, 0.10, 1.0),
    },
    "blue_dipped": {
        "body": (0.72, 0.74, 0.76, 1.0),
        "bright": (0.88, 0.89, 0.90, 1.0),
        "dark": (0.30, 0.31, 0.33, 1.0),
        "accent": (0.06, 0.22, 0.55, 1.0),
    },
    "gunmetal_yellow": {
        "body": (0.40, 0.42, 0.44, 1.0),
        "bright": (0.60, 0.62, 0.64, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
        "accent": (0.95, 0.78, 0.10, 1.0),
    },
    "raw_forged_grey": {
        "body": (0.52, 0.53, 0.55, 1.0),
        "bright": (0.66, 0.67, 0.68, 1.0),
        "dark": (0.28, 0.29, 0.30, 1.0),
        "accent": (0.14, 0.14, 0.15, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class PilersLockingPliersConfig:
    jaw_form: JawForm | None = None
    locking_mechanism: LockingMechanism | None = None
    release: Release | None = None
    adjustment: Adjustment | None = None
    palette_style: PaletteStyle = "polished_steel"
    jaw_scale: float = 1.0
    handle_len_scale: float = 1.0
    grip_girth_scale: float = 1.0
    open_scale: float = 1.0
    name: str = "pilers_locking_pliers"


@dataclass(frozen=True)
class ResolvedPilersLockingPliersConfig:
    jaw_form: JawForm
    locking_mechanism: LockingMechanism
    release: Release
    adjustment: Adjustment
    palette_style: PaletteStyle
    jaw_scale: float
    handle_len_scale: float
    grip_girth_scale: float
    open_scale: float
    jaw_lower: float
    jaw_upper: float
    upper_handle_lower: float
    upper_handle_upper: float
    lower_handle_lower: float
    lower_handle_upper: float
    linkage_lower: float
    linkage_upper: float
    release_lower: float
    release_upper: float
    name: str

    @property
    def pivot(self) -> tuple[float, float]:
        return JAW_PIVOTS[self.jaw_form]

    @property
    def release_axis(self) -> tuple[float, float, float]:
        # one_hand_push flips the release pivot axis sign (② axis diversity).
        return (0.0, 0.0, -1.0) if self.release == "one_hand_push_release" else (0.0, 0.0, 1.0)

    @property
    def adjustment_upper(self) -> float:
        return 0.010 if self.adjustment == "quick_adjust_thumbwheel" else 0.006

    @property
    def socket_y(self) -> float:
        return -0.170 * self.handle_len_scale


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PilersLockingPliersConfig:
    rng = random.Random(seed)
    jaw = rng.choices(JAW_FORMS, weights=[5, 3, 3, 3], k=1)[0]
    lock = rng.choices(LOCKING_MECHANISMS, weights=[5, 3], k=1)[0]
    rel = rng.choices(RELEASES, weights=[5, 3], k=1)[0]
    adj = rng.choices(ADJUSTMENTS, weights=[5, 3], k=1)[0]
    return PilersLockingPliersConfig(
        jaw_form=jaw,
        locking_mechanism=lock,
        release=rel,
        adjustment=adj,
        palette_style=rng.choice(PALETTE_STYLES),
        jaw_scale=round(rng.uniform(0.90, 1.12), 4),
        handle_len_scale=round(rng.uniform(0.92, 1.10), 4),
        grip_girth_scale=round(rng.uniform(0.92, 1.10), 4),
        open_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_pilers_locking_pliers_{seed}",
    )


def resolve_config(
    config: PilersLockingPliersConfig | None = None,
) -> ResolvedPilersLockingPliersConfig:
    cfg = config or PilersLockingPliersConfig()
    jaw = _pick(cfg.jaw_form, JAW_FORMS)
    lock = _pick(cfg.locking_mechanism, LOCKING_MECHANISMS)
    rel = _pick(cfg.release, RELEASES)
    adj = _pick(cfg.adjustment, ADJUSTMENTS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    jaw_scale = _clamp(cfg.jaw_scale, 0.90, 1.12)
    handle_len = _clamp(cfg.handle_len_scale, 0.92, 1.10)
    grip_girth = _clamp(cfg.grip_girth_scale, 0.92, 1.10)
    ang = _clamp(cfg.open_scale, 0.85, 1.15)

    # Scale ranges by open_scale then clamp to a feasibility band (inequality
    # layer): closing (+upper) is capped so scaled jaws never bite; opening
    # (−lower) stays generous. Enforced by the sampled-pose collision gate.
    jaw_lower = _clamp(BASE_JAW_LOWER * ang, -0.24, -0.14)
    jaw_upper = _clamp(BASE_JAW_UPPER * ang, 0.02, 0.05)
    uh_lower = _clamp(BASE_UPPER_HANDLE_LOWER * ang, -0.11, -0.05)
    uh_upper = _clamp(BASE_UPPER_HANDLE_UPPER * ang, 0.05, 0.11)
    lh_lower = _clamp(BASE_LOWER_HANDLE_LOWER * ang, -0.14, -0.06)
    lh_upper = _clamp(BASE_LOWER_HANDLE_UPPER * ang, 0.14, 0.28)
    link_lower = _clamp(BASE_LINKAGE_LOWER * ang, -0.20, -0.10)
    link_upper = _clamp(BASE_LINKAGE_UPPER * ang, 0.12, 0.26)
    rel_lower = _clamp(BASE_RELEASE_LOWER * ang, -0.16, -0.08)
    rel_upper = _clamp(BASE_RELEASE_UPPER * ang, 0.22, 0.40)

    return ResolvedPilersLockingPliersConfig(
        jaw_form=jaw,
        locking_mechanism=lock,
        release=rel,
        adjustment=adj,
        palette_style=palette,
        jaw_scale=jaw_scale,
        handle_len_scale=handle_len,
        grip_girth_scale=grip_girth,
        open_scale=ang,
        jaw_lower=jaw_lower,
        jaw_upper=jaw_upper,
        upper_handle_lower=uh_lower,
        upper_handle_upper=uh_upper,
        lower_handle_lower=lh_lower,
        lower_handle_upper=lh_upper,
        linkage_lower=link_lower,
        linkage_upper=link_upper,
        release_lower=rel_lower,
        release_upper=rel_upper,
        name=cfg.name or "pilers_locking_pliers",
    )


def slot_choices_for_config(
    config: PilersLockingPliersConfig | ResolvedPilersLockingPliersConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedPilersLockingPliersConfig)
        else resolve_config(config)
    )
    return (
        ("jaw_form", r.jaw_form),
        ("locking_mechanism", r.locking_mechanism),
        ("release", r.release),
        ("adjustment", r.adjustment),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers (from the 5-star sources; primitives preserved — Rule 3).
# ---------------------------------------------------------------------------
def _lerp2(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _serrated_edge(
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    count: int,
    depth: float,
    normal: tuple[float, float],
) -> list[tuple[float, float]]:
    """One continuous saw-tooth boundary between two jaw endpoints (origin L34-55)."""
    points: list[tuple[float, float]] = []
    for index in range(count):
        t0 = index / count
        tm = (index + 0.52) / count
        t1 = (index + 1.0) / count
        base0 = _lerp2(start, end, t0)
        tip = _lerp2(start, end, tm)
        base1 = _lerp2(start, end, t1)
        if not points:
            points.append(base0)
        points.append((tip[0] + normal[0] * depth, tip[1] + normal[1] * depth))
        points.append(base1)
    return points


def _localize(
    points: list[tuple[float, float]], origin: tuple[float, float]
) -> list[tuple[float, float]]:
    return [(x - origin[0], y - origin[1]) for x, y in points]


def _scale_about(
    points: list[tuple[float, float]], center: tuple[float, float], s: float
) -> list[tuple[float, float]]:
    cx, cy = center
    return [(cx + (x - cx) * s, cy + (y - cy) * s) for x, y in points]


def _scale_xy(points: list[tuple[float, float]], sx: float, sy: float) -> list[tuple[float, float]]:
    return [(x * sx, y * sy) for x, y in points]


def _plate_mesh(profile: list[tuple[float, float]], thickness: float, name: str):
    return mesh_from_geometry(ExtrudeGeometry(profile, thickness, center=True), name)


# ---- Slot A jaw profiles (each lifted from its fork record). ----
def _curved_fixed() -> list[tuple[float, float]]:
    teeth = _serrated_edge((-0.008, 0.056), (-0.005, 0.106), count=12, depth=0.0027, normal=(1.0, 0.0))
    return teeth + [
        (-0.012, 0.114), (-0.022, 0.111), (-0.031, 0.100), (-0.037, 0.083),
        (-0.035, 0.066), (-0.028, 0.048), (-0.031, 0.026), (-0.026, 0.008),
        (-0.014, -0.006), (0.007, -0.012), (0.025, -0.006), (0.031, 0.008),
        (0.030, 0.031), (0.020, 0.046), (0.006, 0.054),
    ]


def _curved_movable() -> list[tuple[float, float]]:
    teeth = _serrated_edge((0.004, 0.057), (0.007, 0.104), count=11, depth=0.0027, normal=(-1.0, 0.0))
    return teeth + [
        (0.014, 0.113), (0.024, 0.110), (0.033, 0.100), (0.038, 0.084),
        (0.037, 0.069), (0.031, 0.055), (0.024, 0.044), (0.023, 0.031),
        (0.029, 0.021), (0.025, 0.011), (0.012, 0.007), (-0.002, 0.015), (-0.004, 0.035),
    ]


def _long_nose_fixed() -> list[tuple[float, float]]:
    teeth = _serrated_edge((-0.007, 0.052), (-0.003, 0.139), count=17, depth=0.0018, normal=(1.0, 0.0))
    return teeth + [
        (-0.007, 0.148), (-0.014, 0.149), (-0.020, 0.143), (-0.024, 0.125),
        (-0.027, 0.103), (-0.030, 0.080), (-0.029, 0.061), (-0.024, 0.046),
        (-0.031, 0.026), (-0.026, 0.008), (-0.014, -0.006), (0.007, -0.012),
        (0.025, -0.006), (0.031, 0.008), (0.030, 0.031), (0.020, 0.046), (0.006, 0.054),
    ]


def _long_nose_movable() -> list[tuple[float, float]]:
    teeth = _serrated_edge((0.004, 0.053), (0.002, 0.137), count=16, depth=0.0018, normal=(-1.0, 0.0))
    return teeth + [
        (0.006, 0.146), (0.013, 0.148), (0.019, 0.142), (0.023, 0.124),
        (0.026, 0.102), (0.029, 0.080), (0.029, 0.063), (0.025, 0.049),
        (0.024, 0.044), (0.023, 0.031), (0.029, 0.021), (0.025, 0.011),
        (0.012, 0.007), (-0.002, 0.015), (-0.004, 0.035),
    ]


def _c_clamp_fixed() -> list[tuple[float, float]]:
    teeth = _serrated_edge((-0.034, 0.084), (0.006, 0.084), count=12, depth=0.0024, normal=(0.0, -1.0))
    return teeth + [
        (0.010, 0.094), (-0.005, 0.108), (-0.040, 0.126), (-0.075, 0.120),
        (-0.100, 0.098), (-0.108, 0.068), (-0.100, 0.035), (-0.080, 0.008),
        (-0.048, -0.008), (-0.015, -0.012), (0.020, 0.000), (0.031, 0.016),
        (0.026, 0.033), (0.012, 0.046), (-0.012, 0.050), (-0.042, 0.042),
        (-0.064, 0.048), (-0.076, 0.064), (-0.075, 0.079), (-0.066, 0.092),
        (-0.050, 0.098), (-0.035, 0.094),
    ]


def _c_clamp_movable() -> list[tuple[float, float]]:
    teeth = _serrated_edge((-0.034, 0.061), (0.006, 0.061), count=11, depth=0.0024, normal=(0.0, 1.0))
    return teeth + [
        (0.012, 0.057), (0.026, 0.049), (0.033, 0.035), (0.031, 0.019),
        (0.020, 0.006), (0.002, 0.002), (-0.012, 0.010), (-0.016, 0.026),
        (-0.010, 0.043), (-0.002, 0.055), (-0.034, 0.055),
    ]


def _wide_fixed() -> list[tuple[float, float]]:
    teeth = _serrated_edge((-0.010, 0.058), (-0.010, 0.108), count=13, depth=0.0022, normal=(1.0, 0.0))
    return teeth + [
        (-0.014, 0.113), (-0.044, 0.113), (-0.047, 0.105), (-0.047, 0.092),
        (-0.043, 0.078), (-0.035, 0.062), (-0.028, 0.046), (-0.030, 0.025),
        (-0.025, 0.006), (-0.013, -0.007), (0.008, -0.011), (0.027, -0.004),
        (0.032, 0.011), (0.029, 0.032), (0.017, 0.049), (0.004, 0.057),
    ]


def _wide_movable() -> list[tuple[float, float]]:
    teeth = _serrated_edge((0.006, 0.058), (0.006, 0.108), count=13, depth=0.0022, normal=(-1.0, 0.0))
    return teeth + [
        (0.010, 0.113), (0.043, 0.113), (0.047, 0.105), (0.047, 0.092),
        (0.043, 0.078), (0.035, 0.062), (0.027, 0.047), (0.024, 0.034),
        (0.030, 0.021), (0.026, 0.010), (0.012, 0.006), (-0.003, 0.015), (-0.005, 0.036),
    ]


def _wide_fixed_grip() -> list[tuple[float, float]]:
    teeth = _serrated_edge((-0.010, 0.060), (-0.010, 0.108), count=13, depth=0.0022, normal=(1.0, 0.0))
    return teeth + [
        (-0.013, 0.112), (-0.043, 0.112), (-0.045, 0.106), (-0.045, 0.091),
        (-0.041, 0.076), (-0.034, 0.061),
    ]


def _wide_movable_grip() -> list[tuple[float, float]]:
    teeth = _serrated_edge((0.006, 0.060), (0.006, 0.108), count=13, depth=0.0022, normal=(-1.0, 0.0))
    return teeth + [
        (0.010, 0.112), (0.043, 0.112), (0.045, 0.106), (0.045, 0.091),
        (0.041, 0.076), (0.034, 0.061),
    ]


_JAW_FIXED = {
    "curved_jaw": _curved_fixed,
    "long_nose_jaw": _long_nose_fixed,
    "c_clamp_jaw": _c_clamp_fixed,
    "sheet_metal_wide_jaw": _wide_fixed,
}
_JAW_MOVABLE = {
    "curved_jaw": _curved_movable,
    "long_nose_jaw": _long_nose_movable,
    "c_clamp_jaw": _c_clamp_movable,
    "sheet_metal_wide_jaw": _wide_movable,
}
_JAW_STYLE_META = {
    "curved_jaw": "curved",
    "long_nose_jaw": "long_nose",
    "c_clamp_jaw": "c_clamp",
    "sheet_metal_wide_jaw": "sheet_metal_wide",
}


# ---- Handle profiles (shared across jaw forms; origin L131-170). ----
def _upper_handle_profile() -> list[tuple[float, float]]:
    return [
        (-0.018, 0.013), (-0.004, 0.020), (0.012, 0.016), (0.018, 0.001),
        (0.016, -0.027), (0.012, -0.055), (0.011, -0.094), (0.013, -0.129),
        (0.010, -0.157), (0.007, -0.177), (-0.007, -0.177), (-0.011, -0.151),
        (-0.012, -0.112), (-0.013, -0.075), (-0.016, -0.040), (-0.022, -0.010),
    ]


def _lower_handle_profile() -> list[tuple[float, float]]:
    return [
        (-0.014, 0.010), (0.004, 0.017), (0.014, 0.007), (0.013, -0.018),
        (0.005, -0.048), (0.001, -0.082), (0.005, -0.116), (0.011, -0.151),
        (0.012, -0.174), (0.006, -0.189), (-0.003, -0.184), (-0.010, -0.158),
        (-0.014, -0.126), (-0.017, -0.089), (-0.022, -0.050), (-0.023, -0.018),
    ]


# ---- Slot B locking link profiles. ----
def _short_locking_link_profile() -> list[tuple[float, float]]:
    return [
        (-0.004, 0.005), (0.004, 0.007), (0.015, -0.010), (0.020, -0.031),
        (0.018, -0.047), (0.011, -0.054), (0.006, -0.031), (-0.003, -0.007),
    ]


def _classic_locking_link_profile() -> list[tuple[float, float]]:
    return [
        (-0.006, 0.005), (0.005, 0.007), (0.011, -0.006), (0.015, -0.029),
        (0.019, -0.057), (0.023, -0.085), (0.027, -0.113), (0.028, -0.133),
        (0.024, -0.142), (0.016, -0.146), (0.009, -0.140), (0.009, -0.121),
        (0.007, -0.095), (0.003, -0.065), (-0.001, -0.035), (-0.006, -0.009),
    ]


def _spring_mesh(name: str, *, coils: int, end_y: float):
    """Internal linkage spring — a spline tube anchored inside the link plate
    (origin L367-387). Start sits within the plate footprint so it stays
    connected; the tail extends toward the release area.
    """
    start_x = 0.010
    # Anchor the first two points deep inside the plate body (both the short and
    # classic profiles cover x≈0.010, y≈−0.026..−0.032) so the tube is connected.
    spring_points: list[tuple[float, float, float]] = [
        (start_x, -0.026, 0.0),
        (start_x, -0.032, 0.0),
    ]
    span = (-0.036 - end_y) if end_y < -0.036 else 0.001
    for index in range(coils):
        y = -0.036 - index * (span / max(coils, 1))
        x = start_x + (0.0020 if index % 2 == 0 else -0.0020)
        spring_points.append((x, y, 0.0))
    spring_points.append((0.010, end_y, 0.0))
    return mesh_from_geometry(
        tube_from_spline_points(
            spring_points,
            radius=0.00075,
            samples_per_segment=4,
            radial_segments=10,
            cap_ends=True,
            up_hint=(0.0, 0.0, 1.0),
        ),
        name,
    )


# ---- Slot C release lever profiles. ----
def _thumb_lever_profile() -> list[tuple[float, float]]:
    return [
        (-0.003, 0.005), (0.005, 0.007), (0.010, -0.010), (0.012, -0.035),
        (0.016, -0.064), (0.020, -0.091), (0.016, -0.101), (0.010, -0.095),
        (0.007, -0.069), (0.003, -0.040), (-0.002, -0.013),
    ]


def _push_release_profile() -> list[tuple[float, float]]:
    return [
        (-0.005, 0.004), (0.001, 0.008), (0.008, 0.004), (0.012, -0.012),
        (0.014, -0.035), (0.022, -0.052), (0.030, -0.065), (0.030, -0.078),
        (0.023, -0.087), (0.013, -0.084), (0.008, -0.069), (0.004, -0.045),
        (0.001, -0.020), (-0.004, -0.008),
    ]


# ---------------------------------------------------------------------------
# Builder
# ---------------------------------------------------------------------------
def build_pilers_locking_pliers(
    config: PilersLockingPliersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"plp_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    pivot = r.pivot
    js = r.jaw_scale
    hls = r.handle_len_scale
    ggs = r.grip_girth_scale
    is_wide = r.jaw_form == "sheet_metal_wide_jaw"
    is_compound = r.locking_mechanism == "compound_jaw_linkage"

    # ------------------------------------------------------------------
    # jaw_frame (root): fixed jaw plate + pivot bosses/rivets.
    # ------------------------------------------------------------------
    jaw_frame = model.part(
        "jaw_frame",
        meta={
            "jaw_style": _JAW_STYLE_META[r.jaw_form],
            "jaw_form": r.jaw_form,
            "serrated": True,
            "construction": "thick_forged_plate",
            "locking_mechanism": r.locking_mechanism,
        },
    )
    fixed_profile = _scale_about(_JAW_FIXED[r.jaw_form](), pivot, js)
    jaw_frame.visual(
        _plate_mesh(fixed_profile, PLATE_THICKNESS, "fixed_jaw"),
        origin=Origin(xyz=(0.0, 0.0, -0.003)),
        material=mats["body"],
        name="fixed_jaw_plate", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
    )
    if is_wide:
        wide_fixed = _scale_about(_wide_fixed_grip(), pivot, js)
        jaw_frame.visual(
            _plate_mesh(wide_fixed, WIDE_JAW_WIDTH, "fixed_wide_jaw_face"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["body"],
            name="fixed_wide_jaw_face", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
        )
    jaw_frame.visual(
        Cylinder(radius=0.009, length=0.006),
        origin=Origin(xyz=(pivot[0], pivot[1], -0.003)),
        material=mats["body"],
        name="central_pivot_boss", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
    )
    jaw_frame.visual(
        Cylinder(radius=0.0048, length=0.0014),
        origin=Origin(xyz=(-0.021, 0.012, 0.0007)),
        material=mats["bright"],
        name="frame_rivet", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )
    jaw_frame.visual(
        Cylinder(radius=0.0038, length=0.006),
        origin=Origin(xyz=(-0.022, 0.012, 0.003)),
        material=mats["bright"],
        name="lower_handle_pivot_shaft", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )
    if is_compound:
        # Compound coupling seat welded to the frame cheek (var_...compound L277-282).
        jaw_frame.visual(
            Cylinder(radius=0.0062, length=0.006),
            origin=Origin(xyz=(-0.015, 0.007, -0.003)),
            material=mats["body"],
            name="compound_link_seat", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
        )

    # ------------------------------------------------------------------
    # movable_jaw (localized to pivot).
    # ------------------------------------------------------------------
    movable_meta = {
        "jaw_style": _JAW_STYLE_META[r.jaw_form],
        "jaw_form": r.jaw_form,
        "serrated": True,
        "construction": "thick_forged_plate",
    }
    if is_compound:
        movable_meta["jaw_linkage"] = "compound"
        movable_meta["rocker_tail"] = True
    movable_jaw = model.part("movable_jaw", meta=movable_meta)
    # Movable profiles are authored in the frame's world coords; localize to the
    # pivot so the part frame sits at the pivot (origin L128), then scale.
    movable_profile = _scale_about(_localize(_JAW_MOVABLE[r.jaw_form](), pivot), (0.0, 0.0), js)
    movable_jaw.visual(
        _plate_mesh(movable_profile, PLATE_THICKNESS, "movable_jaw"),
        material=mats["body"],
        name="movable_jaw_plate", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
    )
    if is_wide:
        wide_movable = _scale_about(_localize(_wide_movable_grip(), pivot), (0.0, 0.0), js)
        movable_jaw.visual(
            _plate_mesh(wide_movable, WIDE_JAW_WIDTH, "movable_wide_jaw_face"),
            material=mats["body"],
            name="movable_wide_jaw_face", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
        )
    movable_jaw.visual(
        Cylinder(radius=0.0054, length=0.0016),
        origin=Origin(xyz=(0.0, 0.0, 0.0038)),
        material=mats["bright"],
        name="central_pivot_rivet", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )
    if is_compound:
        # Rocker coupling pin — seated on the movable plate's pivot hub so it
        # stays connected across all jaw forms (the movable frame is localized to
        # the pivot, so the hub is near local origin).
        movable_jaw.visual(
            Cylinder(radius=0.0046, length=0.0016),
            origin=Origin(xyz=(-0.006, -0.008, 0.0038)),
            material=mats["bright"],
            name="compound_link_rivet", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
        )

    # ------------------------------------------------------------------
    # upper_handle (+ adjustment socket, Slot D host).
    # ------------------------------------------------------------------
    upper_handle = model.part(
        "upper_handle", meta={"handle_style": "long_tapered_forged", "steel": True}
    )
    upper_profile = _scale_xy(_upper_handle_profile(), ggs, hls)
    upper_handle.visual(
        _plate_mesh(upper_profile, HANDLE_THICKNESS, "upper_handle"),
        material=mats["body"],
        name="upper_handle_plate", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
    )
    upper_handle.visual(
        Cylinder(radius=0.0047, length=0.0015),
        origin=Origin(xyz=(-0.002, 0.002, -0.00325)),
        material=mats["bright"],
        name="upper_handle_rivet", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )
    if r.adjustment == "quick_adjust_thumbwheel":
        upper_handle.visual(
            Cylinder(radius=0.0062, length=0.018),
            origin=Origin(xyz=(0.0, r.socket_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name="adjustment_socket", material_class_id="metal.blackened_gunmetal",
        )
    else:
        upper_handle.visual(
            Box((0.010, 0.014, 0.008)),
            origin=Origin(xyz=(0.0, r.socket_y, 0.0)),
            material=mats["dark"],
            name="adjustment_socket", material_class_id="metal.blackened_gunmetal",
        )

    # ------------------------------------------------------------------
    # lower_handle (+ link/release pivot pins).
    # ------------------------------------------------------------------
    lower_handle = model.part(
        "lower_handle", meta={"handle_style": "long_tapered_forged", "steel": True}
    )
    lower_profile = _scale_xy(_lower_handle_profile(), ggs, hls)
    lower_handle.visual(
        _plate_mesh(lower_profile, HANDLE_THICKNESS, "lower_handle"),
        material=mats["body"],
        name="lower_handle_plate", material_class_id=("metal.steel_bare" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped", "raw_forged_grey"} else "metal.blackened_gunmetal"),
    )
    lower_handle.visual(
        Cylinder(radius=0.0048, length=0.0015),
        origin=Origin(xyz=(0.0, 0.0, 0.00325)),
        material=mats["bright"],
        name="lower_handle_rivet", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )
    lower_handle.visual(
        Cylinder(radius=0.0023, length=0.005),
        origin=Origin(xyz=(0.012, -0.010, 0.0035)),
        material=mats["bright"],
        name="link_pivot_pin", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )
    release_pin_radius = 0.0027 if r.release == "one_hand_push_release" else 0.0022
    lower_handle.visual(
        Cylinder(radius=release_pin_radius, length=0.0055),
        origin=Origin(xyz=(0.002, -0.055, 0.0045)),
        material=mats["bright"],
        name="release_pivot_pin", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )

    # ------------------------------------------------------------------
    # locking_link (Slot B).
    # ------------------------------------------------------------------
    if r.locking_mechanism == "classic_toggle_link":
        link_profile = _classic_locking_link_profile()
        spring_coils, spring_end = 17, -0.140
    else:
        link_profile = _short_locking_link_profile()
        spring_coils, spring_end = 13, -0.092
    locking_link = model.part(
        "locking_link",
        meta={
            "locking_linkage": True,
            "includes_internal_spring": True,
            "linkage_style": r.locking_mechanism,
            "over_center_lock": True,
        },
    )
    locking_link.visual(
        _plate_mesh(link_profile, 0.002, "locking_link_plate"),
        material=mats["dark"],
        name="linkage_plate", material_class_id="metal.blackened_gunmetal",
    )
    if r.locking_mechanism == "classic_toggle_link":
        locking_link.visual(
            Cylinder(radius=0.0034, length=0.0022),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["bright"],
            name="toggle_pivot_eye", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
        )
    locking_link.visual(
        _spring_mesh("locking_link_spring", coils=spring_coils, end_y=spring_end),
        material=mats["bright"],
        name="linkage_spring", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
    )

    # ------------------------------------------------------------------
    # release_lever (Slot C).
    # ------------------------------------------------------------------
    if r.release == "one_hand_push_release":
        release_profile = _push_release_profile()
        release_thickness = 0.0024
        pad_radius, pad_xy = 0.010, (0.022, -0.073)
        release_style = "one_hand_push"
    else:
        release_profile = _thumb_lever_profile()
        release_thickness = 0.0018
        pad_radius, pad_xy = 0.0031, (0.016, -0.094)
        release_style = "captured_thumb_lever"
    release_lever = model.part(
        "release_lever",
        meta={"release_control": True, "bounded": True, "release_style": release_style},
    )
    release_lever.visual(
        _plate_mesh(release_profile, release_thickness, "release_lever"),
        material=mats["accent"],
        name="release_lever_plate", material_class_id=("metal.paint_coated" if config.palette_style in {"black_oxide_red", "blue_dipped", "gunmetal_yellow"} else "metal.blackened_gunmetal"),
    )
    release_lever.visual(
        Cylinder(radius=pad_radius, length=0.0018),
        origin=Origin(xyz=(pad_xy[0], pad_xy[1], 0.0)),
        material=mats["accent"],
        name="release_thumb_pad", material_class_id=("metal.paint_coated" if config.palette_style in {"black_oxide_red", "blue_dipped", "gunmetal_yellow"} else "metal.blackened_gunmetal"),
    )

    # ------------------------------------------------------------------
    # adjustment_screw (Slot D).
    # ------------------------------------------------------------------
    adjustment_meta = {
        "captured_adjuster": True,
        "knurled": True,
        "changes_jaw_setting": True,
        "adjuster_style": r.adjustment,
    }
    if r.adjustment == "quick_adjust_thumbwheel":
        adjustment_meta["tool_free"] = True
    adjustment_screw = model.part("adjustment_screw", meta=adjustment_meta)
    if r.adjustment == "quick_adjust_thumbwheel":
        shaft_len, shaft_y = 0.044, -0.003
        knob = KnobGeometry(
            0.022, 0.010, body_style="cylindrical", edge_radius=0.0012,
            grip=KnobGrip(style="knurled", count=36, depth=0.0008, helix_angle_deg=18.0),
            center=True,
        )
        knob_y = -0.030
    else:
        shaft_len, shaft_y = 0.036, -0.004
        knob = KnobGeometry(
            0.014, 0.013, body_style="cylindrical", edge_radius=0.0005,
            grip=KnobGrip(style="knurled", count=28, depth=0.00065, helix_angle_deg=22.0),
            center=True,
        )
        knob_y = -0.026
    adjustment_screw.visual(
        Cylinder(radius=0.0024, length=shaft_len),
        origin=Origin(xyz=(0.0, shaft_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["dark"],
        name="adjustment_shaft", material_class_id="metal.blackened_gunmetal",
    )
    if r.adjustment == "quick_adjust_thumbwheel":
        adjustment_screw.visual(
            Cylinder(radius=0.0052, length=0.006),
            origin=Origin(xyz=(0.0, -0.024, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["bright"],
            name="thumbwheel_collar", material_class_id=("metal.chrome_polished" if config.palette_style in {"polished_steel", "nickel_bright", "blue_dipped"} else "metal.brushed_silver"),
        )
    adjustment_screw.visual(
        mesh_from_geometry(knob, "knurled_knob"),
        origin=Origin(xyz=(0.0, knob_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["accent"],
        name="knurled_knob", material_class_id=("metal.paint_coated" if config.palette_style in {"black_oxide_red", "blue_dipped", "gunmetal_yellow"} else "metal.blackened_gunmetal"),
    )

    # ------------------------------------------------------------------
    # Joints (fixed skeleton; captured pins grandfathered — no mating=).
    # ------------------------------------------------------------------
    model.articulation(
        "jaw_pivot", ArticulationType.REVOLUTE, parent=jaw_frame, child=movable_jaw,
        origin=Origin(xyz=(pivot[0], pivot[1], 0.003)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=250.0, velocity=1.4, lower=r.jaw_lower, upper=r.jaw_upper),
    )
    model.articulation(
        "upper_handle_pivot", ArticulationType.REVOLUTE, parent=jaw_frame, child=upper_handle,
        origin=Origin(xyz=(0.015, 0.016, -0.0085)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=300.0, velocity=1.2, lower=r.upper_handle_lower, upper=r.upper_handle_upper
        ),
    )
    model.articulation(
        "lower_handle_pivot", ArticulationType.REVOLUTE, parent=jaw_frame, child=lower_handle,
        origin=Origin(xyz=(-0.022, 0.012, 0.0085)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=300.0, velocity=1.5, lower=r.lower_handle_lower, upper=r.lower_handle_upper
        ),
    )
    model.articulation(
        "linkage_pivot", ArticulationType.REVOLUTE, parent=lower_handle, child=locking_link,
        origin=Origin(xyz=(0.012, -0.010, 0.0035)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=90.0, velocity=2.0, lower=r.linkage_lower, upper=r.linkage_upper
        ),
    )
    model.articulation(
        "release_lever_pivot", ArticulationType.REVOLUTE, parent=lower_handle, child=release_lever,
        origin=Origin(xyz=(0.002, -0.055, 0.006)), axis=r.release_axis,
        motion_limits=MotionLimits(
            effort=18.0, velocity=3.0, lower=r.release_lower, upper=r.release_upper
        ),
    )
    model.articulation(
        "adjustment_travel", ArticulationType.PRISMATIC, parent=upper_handle, child=adjustment_screw,
        origin=Origin(xyz=(0.0, r.socket_y - 0.001, 0.0)), axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=120.0, velocity=0.015, lower=0.0, upper=r.adjustment_upper),
    )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_pilers_locking_pliers(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pilers_locking_pliers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _aabb_center(bounds):
    if bounds is None:
        return None
    low, high = bounds
    return tuple((low[i] + high[i]) * 0.5 for i in range(3))


def _distance3(a, b) -> float:
    if a is None or b is None:
        return 0.0
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def run_pilers_locking_pliers_tests(
    object_model: ArticulatedObject,
    config: PilersLockingPliersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    jaw_frame = object_model.get_part("jaw_frame")
    movable_jaw = object_model.get_part("movable_jaw")
    upper_handle = object_model.get_part("upper_handle")
    lower_handle = object_model.get_part("lower_handle")
    locking_link = object_model.get_part("locking_link")
    release_lever = object_model.get_part("release_lever")
    adjustment_screw = object_model.get_part("adjustment_screw")

    jaw_pivot = object_model.get_articulation("jaw_pivot")
    upper_handle_pivot = object_model.get_articulation("upper_handle_pivot")
    lower_handle_pivot = object_model.get_articulation("lower_handle_pivot")
    linkage_pivot = object_model.get_articulation("linkage_pivot")
    release_pivot = object_model.get_articulation("release_lever_pivot")
    adjustment_travel = object_model.get_articulation("adjustment_travel")

    # ---- Captured-pin allowances (element-scoped; pivots are pin-through-plate). ----
    ctx.allow_overlap(
        jaw_frame, movable_jaw, elem_a="central_pivot_boss", elem_b="central_pivot_rivet",
        reason="The movable jaw is captured on the frame's central pivot boss.",
    )
    ctx.allow_overlap(
        jaw_frame, upper_handle, elem_a="central_pivot_boss", elem_b="upper_handle_rivet",
        reason="The upper handle is riveted onto the frame pivot region.",
    )
    ctx.allow_overlap(
        jaw_frame, lower_handle, elem_a="lower_handle_pivot_shaft", elem_b="lower_handle_rivet",
        reason="The lower handle is captured on the frame's lower pivot shaft.",
    )
    ctx.allow_overlap(
        lower_handle, locking_link, elem_a="link_pivot_pin", elem_b="linkage_plate",
        reason="The locking link is intentionally captured on the handle pivot pin.",
    )
    ctx.expect_contact(
        lower_handle, locking_link, elem_a="link_pivot_pin", elem_b="linkage_plate",
        name="locking link remains captured on pivot pin",
    )
    ctx.allow_overlap(
        lower_handle, release_lever, elem_a="release_pivot_pin", elem_b="release_lever_plate",
        reason="The release lever is intentionally captured on its riveted pivot.",
    )
    ctx.expect_contact(
        lower_handle, release_lever, elem_a="release_pivot_pin", elem_b="release_lever_plate",
        name="release lever remains captured on pivot pin",
    )
    ctx.allow_overlap(
        upper_handle, adjustment_screw, elem_a="adjustment_socket", elem_b="adjustment_shaft",
        reason="The threaded adjuster stays inserted through the rear handle socket.",
    )
    if r.locking_mechanism == "compound_jaw_linkage":
        ctx.allow_overlap(
            jaw_frame, movable_jaw, elem_a="compound_link_seat", elem_b="compound_link_rivet",
            reason="The compound rocker pin couples the movable jaw to the frame seat.",
        )

    # ---- Topology: fixed 7-part / 6-joint over-center skeleton. ----
    ctx.check(
        "fixed 7-part / 6-joint over-center skeleton",
        len(object_model.parts) == 7 and len(object_model.articulations) == 6,
        details=f"parts={len(object_model.parts)}, joints={len(object_model.articulations)}",
    )
    roots = object_model.root_parts()
    ctx.check(
        "connected single-root hierarchy rooted at jaw_frame",
        len(roots) == 1 and roots[0].name == "jaw_frame",
        details=f"roots={[p.name for p in roots]}",
    )

    # ---- Joint types / axes. ----
    required_motion = {
        "jaw_pivot": ArticulationType.REVOLUTE,
        "upper_handle_pivot": ArticulationType.REVOLUTE,
        "lower_handle_pivot": ArticulationType.REVOLUTE,
        "linkage_pivot": ArticulationType.REVOLUTE,
        "release_lever_pivot": ArticulationType.REVOLUTE,
        "adjustment_travel": ArticulationType.PRISMATIC,
    }
    motion_ok = True
    for jname, jtype in required_motion.items():
        j = object_model.get_articulation(jname)
        lim = j.motion_limits
        motion_ok = (
            motion_ok
            and j.articulation_type == jtype
            and lim is not None
            and lim.lower is not None
            and lim.upper is not None
            and lim.upper > lim.lower
        )
    ctx.check("every plier mechanism has bounded motion of the expected type", motion_ok)

    # ---- Slot A: jaw_style meta propagates; wide adds a wide face. ----
    ctx.check(
        "jaw_form meta propagates to both jaws",
        jaw_frame.meta.get("jaw_form") == r.jaw_form
        and movable_jaw.meta.get("jaw_form") == r.jaw_form,
        details=f"frame={jaw_frame.meta.get('jaw_form')}, movable={movable_jaw.meta.get('jaw_form')}",
    )
    if r.jaw_form == "sheet_metal_wide_jaw":
        names = {v.name for v in jaw_frame.visuals} | {v.name for v in movable_jaw.visuals}
        ctx.check(
            "sheet_metal_wide jaw adds wide grip faces",
            {"fixed_wide_jaw_face", "movable_wide_jaw_face"} <= names,
            details=f"visuals={sorted(names)}",
        )

    # ---- Slot B: locking mechanism form. ----
    ctx.check(
        "locking link tags mechanism + carries a spring",
        locking_link.meta.get("linkage_style") == r.locking_mechanism
        and {v.name for v in locking_link.visuals} >= {"linkage_plate", "linkage_spring"},
        details=f"visuals={[v.name for v in locking_link.visuals]}",
    )
    if r.locking_mechanism == "compound_jaw_linkage":
        ctx.check(
            "compound linkage adds seat + rocker rivet",
            any(v.name == "compound_link_seat" for v in jaw_frame.visuals)
            and any(v.name == "compound_link_rivet" for v in movable_jaw.visuals),
        )

    # ---- Slot C: release axis sign differentiates the two candidates. ----
    ctx.check(
        "release pivot axis matches release candidate",
        tuple(round(a, 6) for a in release_pivot.axis) == r.release_axis,
        details=f"axis={release_pivot.axis}, expected={r.release_axis}",
    )

    # ---- Slot D: adjuster style meta + prismatic travel. ----
    ctx.check(
        "adjustment style tags adjuster + PRISMATIC upper matches candidate",
        adjustment_screw.meta.get("adjuster_style") == r.adjustment
        and adjustment_travel.motion_limits is not None
        and math.isclose(adjustment_travel.motion_limits.upper or 0.0, r.adjustment_upper, abs_tol=1e-9),
        details=f"style={adjustment_screw.meta.get('adjuster_style')}, upper={adjustment_travel.motion_limits}",
    )

    # ---- Captured adjuster stays inserted (origin contract). ----
    ctx.expect_within(
        adjustment_screw, upper_handle, axes="xz",
        inner_elem="adjustment_shaft", outer_elem="adjustment_socket",
        margin=0.0002, name="adjustment shaft stays centered in handle socket",
    )
    ctx.expect_overlap(
        adjustment_screw, upper_handle, axes="y",
        elem_a="adjustment_shaft", elem_b="adjustment_socket",
        min_overlap=0.008, name="adjustment shaft has retained insertion",
    )
    with ctx.pose({adjustment_travel: r.adjustment_upper}):
        ctx.expect_overlap(
            adjustment_screw, upper_handle, axes="y",
            elem_a="adjustment_shaft", elem_b="adjustment_socket",
            min_overlap=0.004, name="adjustment shaft stays captured at maximum setting",
        )

    # ---- Targeted kinematics: each mechanism visibly moves. ----
    movable_checks = (
        (movable_jaw, jaw_pivot, r.jaw_lower, "movable jaw opens"),
        (upper_handle, upper_handle_pivot, r.upper_handle_upper, "upper handle rotates"),
        (lower_handle, lower_handle_pivot, r.lower_handle_upper, "lower handle rotates"),
        (locking_link, linkage_pivot, r.linkage_upper, "locking linkage swings over-center"),
        (release_lever, release_pivot, r.release_upper, "release lever swings"),
    )
    for part, joint, position, check_name in movable_checks:
        rest_center = _aabb_center(ctx.part_world_aabb(part))
        with ctx.pose({joint: position}):
            posed_center = _aabb_center(ctx.part_world_aabb(part))
        ctx.check(
            check_name,
            _distance3(rest_center, posed_center) > 0.0005,
            details=f"rest={rest_center}, posed={posed_center}",
        )

    screw_rest = ctx.part_world_position(adjustment_screw)
    with ctx.pose({adjustment_travel: r.adjustment_upper}):
        screw_adjusted = ctx.part_world_position(adjustment_screw)
    ctx.check(
        "rear adjustment screw moves axially while captured",
        screw_rest is not None
        and screw_adjusted is not None
        and screw_adjusted[1] < screw_rest[1] - r.adjustment_upper * 0.6,
        details=f"rest={screw_rest}, adjusted={screw_adjusted}",
    )

    # ---- Broad sampled-pose collision guard (Rule 5). ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    ctx.check(
        "slot_choices metadata is emitted",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=f"meta slot_choices={object_model.meta.get('slot_choices')}",
    )

    return ctx.report()


__all__ = [
    "PilersLockingPliersConfig",
    "ResolvedPilersLockingPliersConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_pilers_locking_pliers",
    "build_seeded_pilers_locking_pliers",
    "run_pilers_locking_pliers_tests",
    "__modular__",
]
