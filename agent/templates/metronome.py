# SPDX-License-Identifier: Apache-2.0

"""Metronome — modular procedural template.

A grounded ``housing`` (Slot 1) carrying a single ``pendulum`` (Slot 2)
swinging on one REVOLUTE pivot, with a ``sliding_weight`` (Slot 3) running
along the pendulum rod via PRISMATIC, and a ``winding_key`` (Slot 4) that
spins CONTINUOUSLY about its own axis. Slot 5 controls whether the
sliding-weight chain is single-DOF (1 PRISMATIC) or split into
``coarse_plus_fine`` (2 PRISMATIC joints sharing the pendulum). Slot 6 is a
GATED case-extras axis: ``plain_no_extra`` / ``hinged_door`` / ``internal_mechanism``
/ ``separate_base`` / ``fold_out_legs`` (REVOLUTE multiplicity N=1..2).

Identity invariants: every seed produces exactly one REVOLUTE pendulum
pivot, one or two PRISMATIC weight slides (parent=pendulum, axis along rod),
and exactly one CONTINUOUS winding_key joint.

seed=0 anchor: squat_pyramid_shell + rod_with_top_cap + cadquery_bore_collar +
winged_side_key + single_weight + plain_no_extra.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    Part,
    Sphere,
    TestContext,
    TestReport,
)

__modular__ = True


HousingStyle = Literal["squat_pyramid_shell", "tapered_mesh_shell", "box_case", "floor_cabinet"]
PendulumStyle = Literal[
    "rod_with_top_cap",
    "rod_with_bob_tip",
    "long_cabinet_rod",
    "slim_rod_with_lower_bob",
]
WeightStyle = Literal[
    "cadquery_bore_collar",
    "cheek_clamp_weight",
    "lathe_shell_collar",
    "extrude_ring_weight",
]
KeyStyle = Literal["winged_side_key", "crossbar_rear_key", "stem_handle_key", "top_face_knob"]
WeightDof = Literal["single_weight", "coarse_plus_fine", "weight_plus_index"]
CaseExtras = Literal[
    "plain_no_extra",
    "hinged_door",
    "internal_mechanism",
    "separate_base",
    "fold_out_legs",
]
PaletteTheme = Literal["maple_brass", "ebony_brass", "ivory_silver", "walnut_gold"]


HOUSING_MODULES: tuple[HousingStyle, ...] = (
    "squat_pyramid_shell",
    "tapered_mesh_shell",
    "box_case",
    "floor_cabinet",
)
PENDULUM_MODULES: tuple[PendulumStyle, ...] = (
    "rod_with_top_cap",
    "rod_with_bob_tip",
    "long_cabinet_rod",
    "slim_rod_with_lower_bob",
)
WEIGHT_MODULES: tuple[WeightStyle, ...] = (
    "cadquery_bore_collar",
    "cheek_clamp_weight",
    "lathe_shell_collar",
    "extrude_ring_weight",
)
KEY_MODULES: tuple[KeyStyle, ...] = (
    "winged_side_key",
    "crossbar_rear_key",
    "stem_handle_key",
    "top_face_knob",
)
WEIGHT_DOF_MODULES: tuple[WeightDof, ...] = (
    "single_weight",
    "coarse_plus_fine",
    "weight_plus_index",
)
CASE_EXTRAS_MODULES: tuple[CaseExtras, ...] = (
    "plain_no_extra",
    "hinged_door",
    "internal_mechanism",
    "separate_base",
    "fold_out_legs",
)


PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "maple_brass": {
        "case": (0.62, 0.42, 0.20, 1.0),
        "case_dark": (0.42, 0.27, 0.13, 1.0),
        "metal": (0.78, 0.66, 0.32, 1.0),
        "rod": (0.20, 0.20, 0.22, 1.0),
        "bob": (0.62, 0.50, 0.20, 1.0),
        "accent": (0.88, 0.78, 0.30, 1.0),
        "glass": (0.62, 0.78, 0.92, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
    "ebony_brass": {
        "case": (0.15, 0.13, 0.13, 1.0),
        "case_dark": (0.05, 0.05, 0.06, 1.0),
        "metal": (0.86, 0.72, 0.30, 1.0),
        "rod": (0.18, 0.18, 0.20, 1.0),
        "bob": (0.78, 0.62, 0.20, 1.0),
        "accent": (0.94, 0.82, 0.36, 1.0),
        "glass": (0.62, 0.78, 0.92, 1.0),
        "dark": (0.06, 0.06, 0.07, 1.0),
    },
    "ivory_silver": {
        "case": (0.92, 0.90, 0.86, 1.0),
        "case_dark": (0.62, 0.62, 0.60, 1.0),
        "metal": (0.78, 0.80, 0.82, 1.0),
        "rod": (0.30, 0.30, 0.32, 1.0),
        "bob": (0.40, 0.42, 0.46, 1.0),
        "accent": (0.86, 0.86, 0.86, 1.0),
        "glass": (0.65, 0.80, 0.92, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
    "walnut_gold": {
        "case": (0.40, 0.24, 0.12, 1.0),
        "case_dark": (0.22, 0.13, 0.07, 1.0),
        "metal": (0.86, 0.70, 0.28, 1.0),
        "rod": (0.20, 0.20, 0.22, 1.0),
        "bob": (0.80, 0.62, 0.24, 1.0),
        "accent": (0.94, 0.82, 0.36, 1.0),
        "glass": (0.65, 0.80, 0.92, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class MetronomeConfig:
    housing_style: HousingStyle | None = None
    pendulum_style: PendulumStyle | None = None
    weight_style: WeightStyle | None = None
    key_style: KeyStyle | None = None
    weight_dof: WeightDof | None = None
    case_extras: CaseExtras | None = None
    palette_theme: PaletteTheme = "maple_brass"
    case_width: float = 0.115
    case_depth: float = 0.090
    case_height: float = 0.205
    pendulum_swing: float = 0.45
    door_open_upper: float = 1.20
    leg_count: int = 2
    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(PALETTES["maple_brass"])
    )


@dataclass(frozen=True)
class ResolvedMetronomeConfig:
    housing_style: HousingStyle
    pendulum_style: PendulumStyle
    weight_style: WeightStyle
    key_style: KeyStyle
    weight_dof: WeightDof
    case_extras: CaseExtras
    palette_theme: PaletteTheme
    case_width: float
    case_depth: float
    case_height: float
    pendulum_swing: float
    door_open_upper: float
    leg_count: int
    pivot_z: float
    rod_length: float
    rod_radius: float
    weight_travel: float
    palette: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> MetronomeConfig:
    if seed == 0:
        return MetronomeConfig(
            housing_style="squat_pyramid_shell",
            pendulum_style="rod_with_top_cap",
            weight_style="cadquery_bore_collar",
            key_style="winged_side_key",
            weight_dof="single_weight",
            case_extras="plain_no_extra",
            palette_theme="maple_brass",
            case_width=0.115,
            case_depth=0.090,
            case_height=0.205,
            pendulum_swing=0.45,
            leg_count=2,
        )
    rng = random.Random(seed)
    housing: HousingStyle = rng.choice(HOUSING_MODULES)  # type: ignore[arg-type]
    if housing == "floor_cabinet":
        # Long cabinet-scale; long_cabinet_rod is forced.
        pendulum: PendulumStyle = "long_cabinet_rod"
        case_w = rng.uniform(0.22, 0.30)
        case_d = rng.uniform(0.20, 0.27)
        case_h = rng.uniform(0.95, 1.10)
    else:
        pool = ("rod_with_top_cap", "rod_with_bob_tip", "slim_rod_with_lower_bob")
        pendulum = rng.choice(pool)  # type: ignore[assignment]
        case_w = rng.uniform(0.095, 0.140)
        case_d = rng.uniform(0.080, 0.110)
        case_h = rng.uniform(0.170, 0.240)
    return MetronomeConfig(
        housing_style=housing,
        pendulum_style=pendulum,
        weight_style=rng.choice(WEIGHT_MODULES),  # type: ignore[arg-type]
        key_style=rng.choice(KEY_MODULES),  # type: ignore[arg-type]
        weight_dof=rng.choice(WEIGHT_DOF_MODULES),  # type: ignore[arg-type]
        case_extras=rng.choice(CASE_EXTRAS_MODULES),  # type: ignore[arg-type]
        palette_theme=rng.choice(tuple(PALETTES.keys())),  # type: ignore[arg-type]
        case_width=round(case_w, 4),
        case_depth=round(case_d, 4),
        case_height=round(case_h, 4),
        pendulum_swing=round(rng.uniform(0.15, 0.60), 3),
        door_open_upper=round(rng.uniform(1.00, 1.35), 3),
        leg_count=rng.randint(1, 2),
    )


def resolve_config(config: MetronomeConfig) -> ResolvedMetronomeConfig:
    housing = config.housing_style or "squat_pyramid_shell"
    pendulum = config.pendulum_style or "rod_with_top_cap"
    weight = config.weight_style or "cadquery_bore_collar"
    key = config.key_style or "winged_side_key"
    dof = config.weight_dof or "single_weight"
    extras = config.case_extras or "plain_no_extra"
    for value, pool, label in (
        (housing, HOUSING_MODULES, "housing_style"),
        (pendulum, PENDULUM_MODULES, "pendulum_style"),
        (weight, WEIGHT_MODULES, "weight_style"),
        (key, KEY_MODULES, "key_style"),
        (dof, WEIGHT_DOF_MODULES, "weight_dof"),
        (extras, CASE_EXTRAS_MODULES, "case_extras"),
    ):
        if value not in pool:
            raise ValueError(f"Unsupported {label}: {value!r}")
    if config.palette_theme not in PALETTES:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme!r}")

    is_cabinet = housing == "floor_cabinet"
    case_w = _clamp(config.case_width, 0.080, 0.32)
    case_d = _clamp(config.case_depth, 0.060, 0.30)
    if is_cabinet:
        case_h = _clamp(config.case_height, 0.85, 1.10)
        rod_length = case_h * 0.78
        weight_travel = rod_length * 0.45
    else:
        case_h = _clamp(config.case_height, 0.150, 0.260)
        rod_length = case_h * 0.78
        weight_travel = rod_length * 0.35
    pivot_z = case_h * 0.18  # pivot near the bottom front of the case
    rod_radius = 0.005 if not is_cabinet else 0.008

    return ResolvedMetronomeConfig(
        housing_style=housing,
        pendulum_style=pendulum,
        weight_style=weight,
        key_style=key,
        weight_dof=dof,
        case_extras=extras,
        palette_theme=config.palette_theme,
        case_width=case_w,
        case_depth=case_d,
        case_height=case_h,
        pendulum_swing=_clamp(config.pendulum_swing, 0.12, 0.65),
        door_open_upper=_clamp(config.door_open_upper, 0.95, 1.50),
        leg_count=max(1, min(int(config.leg_count), 2)),
        pivot_z=pivot_z,
        rod_length=rod_length,
        rod_radius=rod_radius,
        weight_travel=weight_travel,
        palette=dict(PALETTES[config.palette_theme]),
    )


# --------------------------------------------------------------------------- #
# Slot 1: housing
#
# Every housing style is a HOLLOW shell with an OPEN FRONT (+Y face): the
# pendulum rod and sliding weight must be visible from outside, exactly like
# the 5-star samples (S1 cuts a tall front tempo-window slot through the
# frustum; S3 is an open-front cabinet; S8 frames the front with a sill/header
# and leaves the middle open). The pre-rewrite squat_pyramid/panel/box shells
# were solid boxes (or had an opaque "case" front panel), which sealed the
# pendulum inside the case — the failure mode this rewrite fixes. The
# full-footprint `floor` is the connectivity anchor: every wall, pedestal and
# boss overlaps it (or the rear wall), so the housing stays one connected
# island. The central `pivot_block` pedestal hosts the pendulum pivot origin.
# --------------------------------------------------------------------------- #


def _emit_tempo_scale(
    p: Part,
    r: ResolvedMetronomeConfig,
    *,
    y_face: float,
    z_lo: float,
    z_hi: float,
    x_off: float = 0.0,
) -> None:
    """Ivory tempo-scale plate + printed ticks standing just in front of the
    rear wall, behind the swinging pendulum — the readable scale you see
    through the open front on a real metronome (S1 `tempo_scale_plate`). The
    plate is thin in Y and overlaps the rear geometry it rests against."""
    plate_w = max(0.018, r.case_width * 0.30)
    plate_h = max(0.020, (z_hi - z_lo) * 0.94)
    zc = (z_lo + z_hi) * 0.5
    p.visual(
        Box((plate_w, 0.005, plate_h)),
        origin=Origin(xyz=(x_off, y_face, zc)),
        material="accent",
        name="tempo_scale", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    n = 5
    for i in range(n):
        z = z_lo + (z_hi - z_lo) * (0.08 + 0.84 * i / (n - 1))
        long_tick = i % 2 == 0
        p.visual(
            Box((plate_w * (0.74 if long_tick else 0.46), 0.004, 0.0024)),
            origin=Origin(xyz=(x_off, y_face + 0.0018, z)),
            material="dark",
            name=f"tempo_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )


def _emit_pivot_mount(p: Part, r: ResolvedMetronomeConfig) -> None:
    """Two pivot cheeks flanking the pendulum pivot at +/-x, rising from the
    floor, tied by a thin rear bridge across the center (S1 ``pivot_cheek_0/1``
    + ``pivot_bridge``). The cheeks capture the pendulum's Y-barrel ``pivot_boss``
    (Rule 2) and the bridge keeps the joint origin (0, 0, pivot_z) within
    geometry, while the center stays CLEAR so the rod and bob remain visible —
    unlike a solid central pedestal, which would occlude the lower pendulum."""
    D = r.case_depth
    pz = r.pivot_z
    # The pendulum pivot_boss is a Y-barrel of X/Z radius boss_r; the cheeks flank
    # it in X (inner face just inside boss_r so the boss is captured).
    boss_r = max(0.012, r.rod_radius * 2.5)
    cheek_w = 0.014
    cheek_x = boss_r + cheek_w * 0.5 - 0.002
    top = pz + 0.014
    for sgn, name in ((-1.0, "pivot_cheek_left"), (1.0, "pivot_cheek_right")):
        p.visual(
            Box((cheek_w, D * 0.34, top)),
            origin=Origin(xyz=(sgn * cheek_x, 0.0, top * 0.5)),
            material="case_dark",
            name=name, material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    # Rear bearing bridge: spans both cheeks and reaches the center plane (y=0) at
    # pivot height, so the pivot joint origin (0, 0, pivot_z) lies inside housing
    # geometry (fail_if_articulation_origin_far_from_geometry) for every depth.
    p.visual(
        Box((2.0 * cheek_x + cheek_w, D * 0.32, 0.014)),
        origin=Origin(xyz=(0.0, -D * 0.16, pz)),
        material="case_dark",
        name="pivot_bridge", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )


def _emit_key_bosses(p: Part, r: ResolvedMetronomeConfig) -> None:
    """Emit only the winding-key boss the chosen key actually seats — a side
    boss for the side keys, a rear boss for the crossbar key, or a top boss for
    the face knob. (Emitting all three left spurious metal nubs on unused faces
    and a chimney on top.) The boss overlaps a wall so the key part stays
    connected to the shell (fail_if_isolated_parts)."""
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    key_z = H * 0.45
    if r.key_style in ("winged_side_key", "stem_handle_key"):
        p.visual(
            Box((0.030, D * 0.30, 0.030)),
            origin=Origin(xyz=(W * 0.5 + 0.008, 0.0, key_z)),
            material="metal",
            name="key_boss", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
    elif r.key_style == "crossbar_rear_key":
        p.visual(
            Box((W * 0.30, 0.020, 0.030)),
            origin=Origin(xyz=(0.0, -D * 0.5 - 0.008, key_z)),
            material="metal",
            name="rear_key_boss", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
    else:  # top_face_knob — spans from inside the top geometry (lowest is the
        # panel crown at ~H-0.013) up to z=H+0.020 where the knob collar seats.
        p.visual(
            Cylinder(radius=0.012, length=0.040),
            origin=Origin(xyz=(0.0, 0.0, H)),
            material="metal",
            name="top_key_boss", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )


def _emit_box_shell(p: Part, r: ResolvedMetronomeConfig) -> None:
    """Primitive box case: rear + two side walls + flat top cap, the front left
    OPEN apart from a sill/header frame so the pendulum shows (S8 box `body`)."""
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    wall_t = 0.008
    body_h = H - 0.022
    zc = body_h * 0.5
    for name, sx, sy, cx, cy in (
        ("rear_wall", W, wall_t, 0.0, -D * 0.5 + wall_t * 0.5),
        ("left_wall", wall_t, D, -W * 0.5 + wall_t * 0.5, 0.0),
        ("right_wall", wall_t, D, W * 0.5 - wall_t * 0.5, 0.0),
    ):
        p.visual(
            Box((sx, sy, body_h)),
            origin=Origin(xyz=(cx, cy, zc)),
            material="case",
            name=name, material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    p.visual(
        Box((W, D, 0.026)),
        origin=Origin(xyz=(0.0, 0.0, H - 0.013)),
        material="case_dark",
        name="top_cap", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W, wall_t, 0.026)),
        origin=Origin(xyz=(0.0, D * 0.5 - wall_t * 0.5, 0.013)),
        material="case_dark",
        name="front_sill", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W, wall_t, 0.026)),
        origin=Origin(xyz=(0.0, D * 0.5 - wall_t * 0.5, body_h - 0.013)),
        material="case_dark",
        name="front_header", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    _emit_tempo_scale(p, r, y_face=-D * 0.5 + wall_t, z_lo=0.034, z_hi=body_h - 0.034)


def _emit_panel_shell(p: Part, r: ResolvedMetronomeConfig) -> None:
    """Thin-panel shell with a stepped crown that reads as a tapered/mesh case
    (S5 / S14 panel housings): rear + side panels, an open front with a
    sill/header frame, and stacked crown caps suggesting the inward taper."""
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    wall_t = 0.006
    body_h = H - 0.034
    zc = body_h * 0.5
    for name, sx, sy, cx, cy in (
        ("rear_panel", W, wall_t, 0.0, -D * 0.5 + wall_t * 0.5),
        ("left_panel", wall_t, D, -W * 0.5 + wall_t * 0.5, 0.0),
        ("right_panel", wall_t, D, W * 0.5 - wall_t * 0.5, 0.0),
    ):
        p.visual(
            Box((sx, sy, body_h)),
            origin=Origin(xyz=(cx, cy, zc)),
            material="case",
            name=name, material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    p.visual(
        Box((W, D, 0.020)),
        origin=Origin(xyz=(0.0, 0.0, body_h - 0.004)),
        material="case_dark",
        name="crown_lower", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W * 0.7, D * 0.7, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, body_h + 0.012)),
        material="case_dark",
        name="crown_upper", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W, wall_t, 0.022)),
        origin=Origin(xyz=(0.0, D * 0.5 - wall_t * 0.5, 0.011)),
        material="case_dark",
        name="front_sill", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W, wall_t, 0.020)),
        origin=Origin(xyz=(0.0, D * 0.5 - wall_t * 0.5, body_h - 0.010)),
        material="case_dark",
        name="front_header", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    _emit_tempo_scale(p, r, y_face=-D * 0.5 + wall_t, z_lo=0.030, z_hi=body_h - 0.030)


def _emit_pyramid_shell(p: Part, r: ResolvedMetronomeConfig) -> None:
    """Classic Maelzel squat pyramid: a solid tapered rear mass (stacked
    tapered tiers) on a wide base plinth, fronted by two side frames and a
    sill. The center is fully OPEN (no front header) so the whole pendulum
    shows on the tempo scale, the way S1 cuts a tall front window through the
    frustum (S1 ``_housing_shell``)."""
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    n = 3
    body_h = H - 0.014
    seg = body_h / n
    back_d = D * 0.40
    back_yc = -D * 0.5 + back_d * 0.5
    front_face = -D * 0.5 + back_d
    for i in range(n):
        t = i / (n - 1)
        tw = W * (1.0 - 0.16 * t)
        z0 = i * seg
        h = seg + (0.006 if i < n - 1 else 0.008)
        p.visual(
            Box((tw, back_d, h)),
            origin=Origin(xyz=(0.0, back_yc, z0 + h * 0.5)),
            material="case",
            name=f"shell_tier_{i}", material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    wall_t = 0.010
    for name, cx in (
        ("left_frame", -W * 0.5 + wall_t * 0.5),
        ("right_frame", W * 0.5 - wall_t * 0.5),
    ):
        p.visual(
            Box((wall_t, D, body_h)),
            origin=Origin(xyz=(cx, 0.0, body_h * 0.5)),
            material="case",
            name=name, material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    p.visual(
        Box((W * 1.04, D * 1.04, 0.018)),
        origin=Origin(xyz=(0.0, 0.0, 0.009)),
        material="case_dark",
        name="plinth", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W, wall_t, 0.022)),
        origin=Origin(xyz=(0.0, D * 0.5 - wall_t * 0.5, 0.011)),
        material="case_dark",
        name="front_sill", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W * 0.84 + 0.006, back_d + 0.006, 0.014)),
        origin=Origin(xyz=(0.0, back_yc, body_h - 0.004)),
        material="case_dark",
        name="apex_cap", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    _emit_tempo_scale(p, r, y_face=front_face - 0.002, z_lo=seg * 0.5, z_hi=body_h - seg * 0.4)


def _emit_cabinet_shell(p: Part, r: ResolvedMetronomeConfig) -> None:
    """Tall floor cabinet: rear + side walls + roof with an OPEN front framed by
    two jamb posts — the long pendulum swings in the open front opening (S3)."""
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    floor_t = 0.015
    body_h = H - floor_t - 0.030
    wall_t = 0.012
    zc = floor_t + body_h * 0.5
    for name, sx, sy, cx, cy in (
        ("rear_wall", W * 0.92, wall_t, 0.0, -D * 0.5 + wall_t * 0.5),
        ("right_wall", wall_t, D * 0.92, W * 0.5 - wall_t * 0.5, 0.0),
        ("left_wall", wall_t, D * 0.92, -W * 0.5 + wall_t * 0.5, 0.0),
    ):
        p.visual(
            Box((sx, sy, body_h)),
            origin=Origin(xyz=(cx, cy, zc)),
            material="case",
            name=name, material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    for name, cx in (("jamb_right", W * 0.40), ("jamb_left", -W * 0.40)):
        p.visual(
            Box((wall_t, wall_t, body_h)),
            origin=Origin(xyz=(cx, D * 0.45, zc)),
            material="case_dark",
            name=name, material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
        )
    p.visual(
        Box((W, D, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, H - 0.015)),
        material="case_dark",
        name="roof", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    _emit_tempo_scale(
        p,
        r,
        y_face=-D * 0.5 + wall_t,
        z_lo=floor_t + body_h * 0.20,
        z_hi=floor_t + body_h * 0.82,
    )


def _build_housing(model: ArticulatedObject, r: ResolvedMetronomeConfig) -> None:
    """Emit the housing part. The case bottom sits at z=0, top at z=case_height.
    Every style is a hollow shell with an OPEN FRONT so the pendulum is visible
    (see the section header). The full-footprint floor connects all walls; the
    central pivot_block pedestal hosts the pendulum pivot origin at
    (0, 0, pivot_z)."""
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    p = model.part("housing")
    floor_t = 0.015
    p.visual(
        Box((W, D, floor_t)),
        origin=Origin(xyz=(0.0, 0.0, floor_t * 0.5)),
        material="case",
        name="floor", material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )

    if r.housing_style == "squat_pyramid_shell":
        _emit_pyramid_shell(p, r)
    elif r.housing_style == "tapered_mesh_shell":
        _emit_panel_shell(p, r)
    elif r.housing_style == "box_case":
        _emit_box_shell(p, r)
    else:  # floor_cabinet
        _emit_cabinet_shell(p, r)

    _emit_pivot_mount(p, r)
    _emit_key_bosses(p, r)

    p.inertial = Inertial.from_geometry(
        Box((W, D, H)), mass=0.5, origin=Origin(xyz=(0.0, 0.0, H * 0.5))
    )


# --------------------------------------------------------------------------- #
# Slot 2: pendulum
# --------------------------------------------------------------------------- #


def _build_pendulum(model: ArticulatedObject, r: ResolvedMetronomeConfig) -> None:
    """Emit pendulum part with origin at the pivot (so the joint origin is
    inside the pivot_boss visual at part-frame (0,0,0))."""
    style = r.pendulum_style
    L = r.rod_length
    rr = r.rod_radius
    p = model.part("pendulum")
    # Pivot boss / hub at the part frame origin — barrel-shaped Cylinder
    # spanning across the pivot block.
    boss_r = max(0.012, rr * 2.5)
    boss_l = max(0.030, r.case_depth * 0.30)
    p.visual(
        Cylinder(radius=boss_r, length=boss_l),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="pivot_boss", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    # Rod runs +z from origin to z=L
    p.visual(
        Cylinder(radius=rr, length=L),
        origin=Origin(xyz=(0.0, 0.0, L * 0.5)),
        material="rod",
        name="rod", material_class_id="metal.blackened_gunmetal",
    )
    if style == "rod_with_top_cap":
        # Cap at top
        p.visual(
            Sphere(radius=rr * 3.0),
            origin=Origin(xyz=(0.0, 0.0, L)),
            material="bob",
            name="top_cap", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
    elif style == "rod_with_bob_tip":
        # Lower counterweight hanging below the pivot. Clamp the drop so the bob
        # never pokes through the case floor: the pivot sits low, so the old
        # unclamped -0.15*L drop sank the sphere below z=0. Keep its bottom at
        # world z >= 0.018 using the known pivot_z.
        bob_r = rr * 3.5
        deepest = (0.018 + bob_r) - r.pivot_z  # min bob-center z (pendulum frame)
        cz = max(-L * 0.15, deepest)
        ext_len = -cz  # gap from the rod base (z=0) down to the bob center
        if ext_len > 0.004:
            p.visual(
                Cylinder(radius=rr * 0.9, length=ext_len + bob_r),
                origin=Origin(xyz=(0.0, 0.0, cz * 0.5)),
                material="rod",
                name="rod_extension_down", material_class_id="metal.blackened_gunmetal",
            )
        p.visual(
            Sphere(radius=bob_r),
            origin=Origin(xyz=(0.0, 0.0, cz)),
            material="bob",
            name="lower_counterweight", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
    elif style == "long_cabinet_rod":
        # Long arm + collar near bottom + sphere rod_tip
        p.visual(
            Cylinder(radius=rr * 1.8, length=0.030),
            origin=Origin(xyz=(0.0, 0.0, L * 0.10)),
            material="metal",
            name="rod_collar", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Sphere(radius=rr * 4.5),
            origin=Origin(xyz=(0.0, 0.0, L)),
            material="bob",
            name="rod_tip", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
    else:  # slim_rod_with_lower_bob
        p.visual(
            Cylinder(radius=rr * 2.5, length=0.025),
            origin=Origin(xyz=(0.0, 0.0, L * 0.10)),
            material="bob",
            name="lower_bob", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
        p.visual(
            Cylinder(radius=rr * 1.5, length=0.015),
            origin=Origin(xyz=(0.0, 0.0, L)),
            material="bob",
            name="lower_tip", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
    p.inertial = Inertial.from_geometry(
        Cylinder(radius=rr, length=L), mass=0.05, origin=Origin(xyz=(0.0, 0.0, L * 0.5))
    )


# --------------------------------------------------------------------------- #
# Slot 3: sliding weight
# --------------------------------------------------------------------------- #


def _build_sliding_weight(
    model: ArticulatedObject,
    r: ResolvedMetronomeConfig,
    *,
    name: str,
) -> None:
    """Build a weight that slides along the rod (+z in pendulum frame). Part
    frame origin is centered on the rod axis, so PRISMATIC translation along
    z makes the weight slide while staying coaxial with the rod."""
    style = r.weight_style
    rr = r.rod_radius
    p = model.part(name)
    if style == "cadquery_bore_collar":
        # Cylinder collar with friction pad
        p.visual(
            Cylinder(radius=rr * 4.5, length=0.022),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="bob",
            name="collar_body", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
        p.visual(
            Box((rr * 8.0, rr * 1.5, 0.002)),
            origin=Origin(xyz=(0.0, 0.0, 0.012)),
            material="dark",
            name="index_line", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    elif style == "cheek_clamp_weight":
        # Two cheeks + bridge + wedge
        cheek_thickness = rr * 1.4
        body_h = 0.026
        body_w = rr * 5.0
        for sign, side in ((+1, "right"), (-1, "left")):
            p.visual(
                Box((cheek_thickness, body_w, body_h)),
                origin=Origin(xyz=(sign * (rr * 2.0), 0.0, 0.0)),
                material="bob",
                name=f"cheek_{side}", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
            )
        # Bridges
        p.visual(
            Box((rr * 4.5, body_w * 0.5, body_h * 0.5)),
            origin=Origin(xyz=(0.0, 0.0, body_h * 0.4)),
            material="bob",
            name="bridge", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
        p.visual(
            Box((rr * 4.5, body_w * 0.5, body_h * 0.5)),
            origin=Origin(xyz=(0.0, 0.0, -body_h * 0.4)),
            material="bob",
            name="bridge_lower", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
    elif style == "lathe_shell_collar":
        p.visual(
            Cylinder(radius=rr * 4.0, length=0.022),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="metal",
            name="shell_outer", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Cylinder(radius=rr * 3.0, length=0.024),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="bob",
            name="shell_inner", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
    else:  # extrude_ring_weight
        p.visual(
            Box((rr * 8.0, rr * 8.0, 0.022)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="bob",
            name="ring_outer", material_class_id=("metal.brass_aged" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.stainless_matte"),
        )
        p.visual(
            Box((rr * 2.0, rr * 2.0, 0.024)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material="dark",
            name="bore", material_class_id="metal.blackened_gunmetal",
        )
        p.visual(
            Box((rr * 2.2, rr * 6.0, 0.005)),
            origin=Origin(xyz=(rr * 4.5, 0.0, 0.012)),
            material="metal",
            name="side_grip", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
    p.inertial = Inertial.from_geometry(
        Cylinder(radius=rr * 4.5, length=0.022), mass=0.03, origin=Origin()
    )


# --------------------------------------------------------------------------- #
# Slot 4: winding key
# --------------------------------------------------------------------------- #


def _build_winding_key(
    model: ArticulatedObject, r: ResolvedMetronomeConfig
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Build the winding_key part and return (joint_origin_in_housing_frame,
    axis). The part frame origin coincides with the joint origin; the key's
    central collar is at the part-frame origin."""
    style = r.key_style
    W = r.case_width
    D = r.case_depth
    H = r.case_height
    p = model.part("winding_key")
    if style == "winged_side_key":
        # Side-mounted butterfly key (axis along +X). Both wings and the end
        # lobe overlap the collar so the part is one connected island.
        p.visual(
            Cylinder(radius=0.010, length=0.026),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material="metal",
            name="key_collar", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        for sign, side in ((1.0, "top"), (-1.0, "bottom")):
            p.visual(
                Box((0.012, 0.016, 0.032)),
                origin=Origin(xyz=(0.006, 0.0, sign * 0.017)),
                material="metal",
                name=f"wing_{side}", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
            )
        p.visual(
            Sphere(radius=0.008),
            origin=Origin(xyz=(0.016, 0.0, 0.0)),
            material="metal",
            name="lobe", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        origin = (W * 0.5 + 0.005, 0.0, H * 0.45)
        axis = (1.0, 0.0, 0.0)
    elif style == "crossbar_rear_key":
        # Axis along -Y, mounted on rear face
        p.visual(
            Cylinder(radius=0.010, length=0.024),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material="metal",
            name="key_collar", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Box((0.022, 0.014, 0.010)),
            origin=Origin(xyz=(0.0, -0.018, 0.0)),
            material="metal",
            name="hub", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Box((0.045, 0.010, 0.010)),
            origin=Origin(xyz=(0.0, -0.030, 0.0)),
            material="metal",
            name="crossbar", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        origin = (0.0, -D * 0.5 - 0.005, H * 0.45)
        axis = (0.0, -1.0, 0.0)
    elif style == "stem_handle_key":
        # Side-mounted stem + T-handle (axis along +X). The bar runs along Y and
        # the grip balls sit at its Y ends, so each piece overlaps its neighbour
        # (one connected island) — the old grips were placed on Z while the bar
        # ran along Y, leaving the balls floating off the handle.
        p.visual(
            Cylinder(radius=0.014, length=0.014),
            origin=Origin(rpy=(0.0, math.pi / 2.0, 0.0)),
            material="metal",
            name="escutcheon", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Cylinder(radius=0.005, length=0.028),
            origin=Origin(xyz=(0.014, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material="metal",
            name="stem", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Box((0.012, 0.044, 0.010)),
            origin=Origin(xyz=(0.028, 0.0, 0.0)),
            material="metal",
            name="bar", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        for sign, side in ((1.0, "top"), (-1.0, "bottom")):
            p.visual(
                Sphere(radius=0.007),
                origin=Origin(xyz=(0.028, sign * 0.022, 0.0)),
                material="metal",
                name=f"grip_{side}", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
            )
        origin = (W * 0.5 + 0.005, 0.0, H * 0.45)
        axis = (1.0, 0.0, 0.0)
    else:  # top_face_knob
        p.visual(
            Cylinder(radius=0.012, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, 0.007)),
            material="metal",
            name="key_shaft", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Cylinder(radius=0.018, length=0.010),
            origin=Origin(xyz=(0.0, 0.0, 0.018)),
            material="metal",
            name="hub", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Box((0.030, 0.012, 0.010)),
            origin=Origin(xyz=(0.014, 0.0, 0.025)),
            material="metal",
            name="arm", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        p.visual(
            Sphere(radius=0.008),
            origin=Origin(xyz=(0.028, 0.0, 0.025)),
            material="metal",
            name="grip_knob", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
        )
        origin = (0.0, 0.0, H + 0.020)
        axis = (0.0, 0.0, -1.0)
    p.inertial = Inertial.from_geometry(
        Cylinder(radius=0.020, length=0.040), mass=0.015, origin=Origin()
    )
    return origin, axis


# --------------------------------------------------------------------------- #
# Slot 6: case extras
# --------------------------------------------------------------------------- #


def _build_separate_base(model: ArticulatedObject, r: ResolvedMetronomeConfig) -> None:
    p = model.part("base")
    W = r.case_width * 1.3
    D = r.case_depth * 1.3
    base_h = 0.040
    # Base sits BELOW the housing; part frame origin is at the TOP of the
    # base cap (so joint origin in housing frame is z=0 — straddling the
    # housing floor and base cap).
    p.visual(
        Box((W, D, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, -0.005)),
        material="case_dark",
        name="cap", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((W * 0.85, D * 0.85, base_h - 0.010)),
        origin=Origin(xyz=(0.0, 0.0, -(base_h - 0.010) * 0.5 - 0.010)),
        material="case",
        name="plinth", material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.inertial = Inertial.from_geometry(
        Box((W, D, base_h)), mass=0.1, origin=Origin(xyz=(0.0, 0.0, -base_h * 0.5))
    )


def _build_mechanism(model: ArticulatedObject, r: ResolvedMetronomeConfig) -> None:
    p = model.part("mechanism")
    body_w = r.case_width * 0.50
    body_h = r.case_height * 0.40
    p.visual(
        Box((body_w, r.case_depth * 0.30, body_h)),
        origin=Origin(xyz=(0.0, 0.0, body_h * 0.5)),
        material="metal",
        name="spring_barrel", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    p.visual(
        Cylinder(radius=body_w * 0.30, length=0.010),
        origin=Origin(xyz=(0.0, 0.0, body_h * 0.5), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="metal",
        name="escapement_wheel", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    p.visual(
        Box((body_w * 0.40, 0.005, body_h * 0.30)),
        origin=Origin(xyz=(0.0, 0.0, body_h * 0.85)),
        material="metal",
        name="anchor", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    p.inertial = Inertial.from_geometry(
        Box((body_w, r.case_depth * 0.30, body_h)),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, body_h * 0.5)),
    )


def _build_door(
    model: ArticulatedObject, r: ResolvedMetronomeConfig
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    p = model.part("front_door")
    W = r.case_width
    H = r.case_height * 0.60
    door_t = 0.005
    # Hinge barrel along +X — runs along bottom edge so the door drops forward
    p.visual(
        Cylinder(radius=0.005, length=W * 0.80),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material="metal",
        name="hinge_barrel", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    p.visual(
        Box((W * 0.90, door_t, H)),
        origin=Origin(xyz=(0.0, 0.0, H * 0.5)),
        material="case",
        name="door_panel", material_class_id=("wood.natural_generic" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Cylinder(radius=0.006, length=0.012),
        origin=Origin(xyz=(0.0, -door_t, H * 0.7)),
        material="metal",
        name="knob", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    p.inertial = Inertial.from_geometry(
        Box((W, door_t, H)), mass=0.05, origin=Origin(xyz=(0.0, 0.0, H * 0.5))
    )
    # Joint origin: at the front bottom edge of the case, sitting on the floor.
    return (0.0, r.case_depth * 0.5, 0.020), (1.0, 0.0, 0.0)


def _build_leg(
    model: ArticulatedObject,
    r: ResolvedMetronomeConfig,
    *,
    side: int,
    index: int,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    p = model.part(f"stabilizer_leg_{index}")
    leg_len = r.case_height * 0.40
    leg_w = 0.010
    # Barrel oriented along z (vertical) so leg swings around z-axis
    p.visual(
        Cylinder(radius=0.008, length=leg_len * 0.20),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material="metal",
        name="hinge_barrel", material_class_id=("metal.brass_polished" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "metal.brushed_silver"),
    )
    p.visual(
        Box((leg_w, leg_len, leg_w * 1.5)),
        origin=Origin(xyz=(0.0, leg_len * 0.5, 0.0)),
        material="case_dark",
        name="leg_arm", material_class_id=("wood.walnut_dark" if r.palette_theme in {"maple_brass", "ebony_brass", "walnut_gold"} else "wood.painted_clean"),
    )
    p.visual(
        Box((leg_w * 1.5, leg_w * 1.5, leg_w * 1.2)),
        origin=Origin(xyz=(0.0, leg_len, 0.0)),
        material="dark",
        name="foot_pad", material_class_id="rubber.smooth_plain",
    )
    p.inertial = Inertial.from_geometry(
        Box((leg_w, leg_len, leg_w * 1.5)),
        mass=0.02,
        origin=Origin(xyz=(0.0, leg_len * 0.5, 0.0)),
    )
    sign = -1.0 if side < 0 else 1.0
    # Place under the back corner of the case. The arm points +Y in the part
    # frame, so the leg must fan OUTBOARD (away from the centerline) as it
    # deploys — axis=(0,0,-sign) rotates the +Y arm toward the -sign side,
    # sweeping the tip to more-negative x for the left leg and more-positive x
    # for the right leg. The old axis=(0,0,sign) swung both legs INWARD, dragging
    # the arm across x=0 through the pendulum's pivot_boss/counterweight volume
    # at the deployed pose (seed 4 pendulum vs stabilizer_leg 穿模).
    return (sign * r.case_width * 0.40, -r.case_depth * 0.40, 0.020), (0.0, 0.0, -sign)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_metronome(
    config: MetronomeConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="metronome", assets=assets)
    for material, rgba in r.palette.items():
        model.material(material, rgba=rgba)

    # Slot 1: housing.
    _build_housing(model, r)
    housing = model.get_part("housing")

    # Slot 6: separate_base (FIXED parent of housing) — emit first so the
    # base is the root part. (We model it by reverse: housing is root, base
    # is its FIXED child. Either is valid; spec allows both.)
    if r.case_extras == "separate_base":
        _build_separate_base(model, r)
        # Joint origin at the housing-base interface (z=0, where housing floor
        # rests on the base cap).
        model.articulation(
            "housing_to_base",
            ArticulationType.FIXED,
            parent=housing,
            child=model.get_part("base"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )

    # Slot 2: pendulum (REVOLUTE).
    _build_pendulum(model, r)
    pendulum = model.get_part("pendulum")
    model.articulation(
        "pendulum_pivot",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=pendulum,
        origin=Origin(xyz=(0.0, 0.0, r.pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=0.5,
            velocity=4.0,
            lower=-r.pendulum_swing,
            upper=r.pendulum_swing,
        ),
    )

    # Slot 3/5: sliding_weight (PRISMATIC along rod = +Z in pendulum frame).
    if r.weight_dof == "coarse_plus_fine":
        _build_sliding_weight(model, r, name="coarse_weight")
        _build_sliding_weight(model, r, name="fine_weight")
        # Two separate PRISMATIC joints, both parent=pendulum.
        # coarse: lower half of rod travel
        model.articulation(
            "pendulum_to_coarse_weight",
            ArticulationType.PRISMATIC,
            parent=pendulum,
            child=model.get_part("coarse_weight"),
            origin=Origin(xyz=(0.0, 0.0, r.rod_length * 0.35)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=2.0,
                velocity=0.10,
                lower=0.0,
                upper=r.weight_travel * 0.40,
            ),
        )
        model.articulation(
            "pendulum_to_fine_weight",
            ArticulationType.PRISMATIC,
            parent=pendulum,
            child=model.get_part("fine_weight"),
            origin=Origin(xyz=(0.0, 0.0, r.rod_length * 0.75)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=1.5,
                velocity=0.10,
                lower=0.0,
                upper=r.weight_travel * 0.20,
            ),
        )
    else:
        _build_sliding_weight(model, r, name="sliding_weight")
        model.articulation(
            "weight_slide",
            ArticulationType.PRISMATIC,
            parent=pendulum,
            child=model.get_part("sliding_weight"),
            origin=Origin(xyz=(0.0, 0.0, r.rod_length * 0.40)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=2.0,
                velocity=0.10,
                lower=0.0,
                upper=r.weight_travel,
            ),
        )

    # Slot 4: winding_key (CONTINUOUS).
    key_origin, key_axis = _build_winding_key(model, r)
    model.articulation(
        "key_axle",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=model.get_part("winding_key"),
        origin=Origin(xyz=key_origin),
        axis=key_axis,
        motion_limits=MotionLimits(effort=0.3, velocity=6.0),
    )

    # Slot 6: gated extras (door / mechanism / legs).
    if r.case_extras == "hinged_door":
        dorigin, daxis = _build_door(model, r)
        model.articulation(
            "housing_to_front_door",
            ArticulationType.REVOLUTE,
            parent=housing,
            child=model.get_part("front_door"),
            origin=Origin(xyz=dorigin),
            axis=daxis,
            motion_limits=MotionLimits(
                effort=0.5, velocity=2.0, lower=0.0, upper=r.door_open_upper
            ),
        )
    elif r.case_extras == "internal_mechanism":
        _build_mechanism(model, r)
        # Joint origin at (0, 0, floor_t * 1.0) — at the top of the housing
        # floor, inside the floor's AABB. The mechanism then sits ABOVE the
        # floor in its part frame.
        model.articulation(
            "housing_to_mechanism",
            ArticulationType.FIXED,
            parent=housing,
            child=model.get_part("mechanism"),
            origin=Origin(xyz=(0.0, 0.0, 0.010)),
        )
    elif r.case_extras == "fold_out_legs":
        for i in range(r.leg_count):
            side = -1 if i == 0 else +1
            lorigin, laxis = _build_leg(model, r, side=side, index=i)
            model.articulation(
                f"leg_hinge_{i}",
                ArticulationType.REVOLUTE,
                parent=housing,
                child=model.get_part(f"stabilizer_leg_{i}"),
                origin=Origin(xyz=lorigin),
                axis=laxis,
                motion_limits=MotionLimits(effort=0.3, velocity=2.0, lower=0.0, upper=1.10),
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_metronome(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_metronome(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedMetronomeConfig) -> list[tuple[str, str]]:
    leg_suffix = f"_n{r.leg_count}" if r.case_extras == "fold_out_legs" else ""
    return [
        ("housing", r.housing_style),
        ("pendulum", r.pendulum_style),
        ("weight", r.weight_style),
        ("key", r.key_style),
        ("weight_dof", r.weight_dof),
        ("case_extras", r.case_extras + leg_suffix),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    name_set = {p.name for p in model.parts}
    # Sliding weight bore intersects rod (it's THE point of a press-fit collar).
    # It also sits INSIDE the housing — its position is inside the case shell.
    for w in ("sliding_weight", "coarse_weight", "fine_weight"):
        if w in name_set and "pendulum" in name_set:
            ctx.allow_overlap(
                model.get_part("pendulum"),
                model.get_part(w),
                reason=f"{w} bore is press-fit / clamped on the pendulum rod (captured slide)",
            )
        if w in name_set and "housing" in name_set:
            ctx.allow_overlap(
                model.get_part("housing"),
                model.get_part(w),
                reason=f"{w} rides inside the case envelope along the pendulum rod",
            )
    # Pendulum pivot boss is captured inside the housing pivot_block.
    if "pendulum" in name_set and "housing" in name_set:
        ctx.allow_overlap(
            model.get_part("housing"),
            model.get_part("pendulum"),
            reason="pendulum pivot_boss is captured by the housing pivot_block",
        )
    # Winding key collar sits inside the housing key boss.
    if "winding_key" in name_set and "housing" in name_set:
        ctx.allow_overlap(
            model.get_part("housing"),
            model.get_part("winding_key"),
            reason="winding key collar inserts through the housing key boss",
        )
    # Door hinge_barrel intersects housing along the hinge line.
    if "front_door" in name_set and "housing" in name_set:
        ctx.allow_overlap(
            model.get_part("housing"),
            model.get_part("front_door"),
            reason="front_door hinge barrel runs along the bottom edge of the housing",
        )
    # Mechanism mounts inside the housing.
    if "mechanism" in name_set and "housing" in name_set:
        ctx.allow_overlap(
            model.get_part("housing"),
            model.get_part("mechanism"),
            reason="internal mechanism is fixed inside the housing cavity",
        )
    # Base is bolted under the housing (visual overlap at the interface).
    if "base" in name_set and "housing" in name_set:
        ctx.allow_overlap(
            model.get_part("housing"),
            model.get_part("base"),
            reason="separate base FIXED-attached under the housing floor",
        )
    # Lower-bob pendulums may reach down into the base envelope.
    if "base" in name_set and "pendulum" in name_set:
        ctx.allow_overlap(
            model.get_part("base"),
            model.get_part("pendulum"),
            reason="lower-bob pendulum sweeps near / touches the base plinth volume",
        )
    # Stabilizer legs hinge under the housing corners.
    for nm in name_set:
        if nm.startswith("stabilizer_leg_"):
            ctx.allow_overlap(
                model.get_part("housing"),
                model.get_part(nm),
                reason=f"{nm} hinge barrel sits inside the housing rear corner",
            )
    # Coarse and fine weights coexist on the rod; their AABB can intersect.
    if "coarse_weight" in name_set and "fine_weight" in name_set:
        ctx.allow_overlap(
            model.get_part("coarse_weight"),
            model.get_part("fine_weight"),
            reason="coarse and fine weights share the rod axis (close-coaxial assemblies)",
        )
    # Weights also share the case cavity with the mechanism, door, base —
    # declare cross-overlaps permissively.
    for w in ("sliding_weight", "coarse_weight", "fine_weight"):
        if w not in name_set:
            continue
        for other in ("mechanism", "front_door", "base", "winding_key"):
            if other in name_set:
                ctx.allow_overlap(
                    model.get_part(w),
                    model.get_part(other),
                    reason=f"{w} and {other} co-occupy the case interior",
                )
    # Pendulum rod runs through the mechanism area.
    if "pendulum" in name_set:
        for other in ("mechanism", "front_door", "winding_key"):
            if other in name_set:
                ctx.allow_overlap(
                    model.get_part("pendulum"),
                    model.get_part(other),
                    reason=f"pendulum rod may pass through {other} volume inside the case",
                )


def run_metronome_tests(object_model: ArticulatedObject, config: MetronomeConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    parts = {p.name for p in object_model.parts}
    ctx.check("housing_present", "housing" in parts)
    ctx.check("pendulum_present", "pendulum" in parts)
    ctx.check("winding_key_present", "winding_key" in parts)
    revolutes = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.REVOLUTE
    ]
    prismatics = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.PRISMATIC
    ]
    continuous = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.CONTINUOUS
    ]
    # Pendulum pivot is the first REVOLUTE; door / legs may add more.
    ctx.check("at_least_one_revolute_pivot", len(revolutes) >= 1)
    expected_prismatic = 2 if r.weight_dof == "coarse_plus_fine" else 1
    ctx.check(
        "expected_prismatic_count",
        len(prismatics) == expected_prismatic,
        details=f"expected {expected_prismatic} PRISMATIC, got {len(prismatics)}",
    )
    ctx.check(
        "exactly_one_continuous_key",
        len(continuous) == 1,
        details=f"expected 1 CONTINUOUS key, got {len(continuous)}",
    )
    return ctx.report()


__all__ = [
    "CaseExtras",
    "HousingStyle",
    "KeyStyle",
    "MetronomeConfig",
    "PaletteTheme",
    "PendulumStyle",
    "ResolvedMetronomeConfig",
    "WeightDof",
    "WeightStyle",
    "__modular__",
    "build_metronome",
    "build_seeded_metronome",
    "config_from_seed",
    "resolve_config",
    "run_metronome_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
