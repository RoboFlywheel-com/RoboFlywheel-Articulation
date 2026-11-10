# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Modular procedural template for category ``Technology_Flashlight`` (handheld torch).

Spec: ``articraft_template_authoring/specs_modular_v1/Technology_Flashlight.md``.

Frame convention (adopted from origin A ``rec_a-yellow...5b5f681c``):
the flashlight axis runs along world X; the HEAD (reflector + lens + LED) points
toward **-X** and the TAIL toward **+X**. Cylinders/lathes are authored with
local +Z axis and rotated onto +X by ``rpy=(0, pi/2, 0)``.

Pattern = parallel_children: ``body`` is the root. The head optics are fused
INTO ``body`` as visuals when they do not move (Rule 1); only the twist-focus
switch makes the head a separate CONTINUOUS ``focus_head`` part. The switch is
always a separate movable part (PRISMATIC) OR the head twist (CONTINUOUS), so
every seed keeps >=1 non-FIXED joint. Crenellation ribs/teeth are a real N-copy
multiplicity of FIXED inline visuals on whichever part carries the head.

5-star module sources: smooth_reflector_cone / straight_cyl_barrel / side_push /
lanyard  <- rec_a-yellow...5b5f681c; crenellated_strike / stepped_tactical /
twist_focus  <- rec_black...baf8fda5; wide_floodlight <- rec_flashlight_var_floodhead;
tailcap_click <- rec_flashlight_var_tailswitch; slide <- rec_flashlight_var_slideswitch;
pocket_clip <- rec_flashlight_var_pocketclip; bezelN <- rec_flashlight_var_bezelN.
penlight_micro_head is a ③ Volumetric-Envelope world_knowledge_extrapolation over
the same head part-tree / lathe primitive / interface.
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
    Inertial,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
    tube_from_spline_points,
)

__modular__ = True

HeadForm = Literal[
    "smooth_reflector_cone",
    "crenellated_strike_bezel",
    "wide_floodlight_head",
    "penlight_micro_head",
]
BodyForm = Literal["straight_cyl_barrel", "stepped_tactical_tube"]
SwitchMech = Literal[
    "side_push_button",
    "twist_focus_head",
    "tailcap_click_switch",
    "longitudinal_slide_switch",
]
CarryFeature = Literal["none", "lanyard_strap_loop", "spring_pocket_clip"]
PaletteStyle = Literal[
    "yellow_plastic",
    "black_tactical",
    "silver_industrial",
    "olive_drab",
    "hi_vis_orange",
    "gunmetal",
]

VALID_HEADS = set(HeadForm.__args__)  # type: ignore[attr-defined]
VALID_BODIES = set(BodyForm.__args__)  # type: ignore[attr-defined]
VALID_SWITCHES = set(SwitchMech.__args__)  # type: ignore[attr-defined]
VALID_CARRIES = set(CarryFeature.__args__)  # type: ignore[attr-defined]
VALID_PALETTES = set(PaletteStyle.__args__)  # type: ignore[attr-defined]

PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "yellow_plastic",
    "black_tactical",
    "silver_industrial",
    "olive_drab",
    "hi_vis_orange",
    "gunmetal",
)

# Each palette resolves to material tokens consumed by every .visual(...) call.
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "yellow_plastic": {
        "body": (1.0, 0.86, 0.0, 1.0),
        "bezel": (0.02, 0.02, 0.02, 1.0),
        "reflector": (0.86, 0.88, 0.86, 1.0),
        "lens": (0.82, 0.94, 1.0, 0.35),
        "led": (1.0, 0.86, 0.45, 1.0),
        "button": (0.03, 0.03, 0.03, 1.0),
        "accent": (0.03, 0.03, 0.03, 1.0),
    },
    "black_tactical": {
        "body": (0.10, 0.10, 0.11, 1.0),
        "bezel": (0.18, 0.18, 0.20, 1.0),
        "reflector": (0.62, 0.63, 0.66, 1.0),
        "lens": (0.86, 0.94, 0.90, 0.35),
        "led": (0.30, 0.95, 0.35, 1.0),
        "button": (0.14, 0.14, 0.15, 1.0),
        "accent": (0.07, 0.07, 0.08, 1.0),
    },
    "silver_industrial": {
        "body": (0.74, 0.76, 0.79, 1.0),
        "bezel": (0.30, 0.31, 0.33, 1.0),
        "reflector": (0.90, 0.91, 0.93, 1.0),
        "lens": (0.85, 0.95, 1.0, 0.33),
        "led": (1.0, 0.92, 0.62, 1.0),
        "button": (0.16, 0.16, 0.18, 1.0),
        "accent": (0.42, 0.43, 0.46, 1.0),
    },
    "olive_drab": {
        "body": (0.29, 0.33, 0.19, 1.0),
        "bezel": (0.10, 0.11, 0.08, 1.0),
        "reflector": (0.80, 0.82, 0.80, 1.0),
        "lens": (0.86, 0.94, 0.88, 0.35),
        "led": (1.0, 0.88, 0.55, 1.0),
        "button": (0.08, 0.09, 0.06, 1.0),
        "accent": (0.14, 0.16, 0.10, 1.0),
    },
    "hi_vis_orange": {
        "body": (0.98, 0.42, 0.03, 1.0),
        "bezel": (0.05, 0.05, 0.05, 1.0),
        "reflector": (0.87, 0.88, 0.87, 1.0),
        "lens": (0.82, 0.94, 1.0, 0.35),
        "led": (1.0, 0.85, 0.42, 1.0),
        "button": (0.05, 0.05, 0.05, 1.0),
        "accent": (0.06, 0.06, 0.06, 1.0),
    },
    "gunmetal": {
        "body": (0.26, 0.28, 0.31, 1.0),
        "bezel": (0.14, 0.15, 0.17, 1.0),
        "reflector": (0.78, 0.80, 0.83, 1.0),
        "lens": (0.85, 0.93, 1.0, 0.34),
        "led": (0.55, 0.85, 1.0, 1.0),
        "button": (0.10, 0.11, 0.12, 1.0),
        "accent": (0.20, 0.21, 0.24, 1.0),
    },
}

# Head-form-dependent shape knobs: (head_ratio range, head_length range, reflector_depth_ratio).
_HEAD_FORM_KNOBS: dict[str, tuple[tuple[float, float], tuple[float, float], float]] = {
    "smooth_reflector_cone": ((1.55, 1.95), (0.048, 0.066), 0.80),
    "crenellated_strike_bezel": ((1.50, 1.90), (0.046, 0.064), 0.92),
    "wide_floodlight_head": ((1.90, 2.30), (0.038, 0.050), 0.55),
    "penlight_micro_head": ((1.35, 1.60), (0.038, 0.050), 0.70),
}

AXIS_TO_X = Origin(rpy=(0.0, math.pi / 2.0, 0.0))


def _axis_x_origin(x: float, y: float = 0.0, z: float = 0.0) -> Origin:
    """Place a local-Z axis primitive/lathe so its axis runs along world X."""
    return Origin(xyz=(x, y, z), rpy=(0.0, math.pi / 2.0, 0.0))


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


# --------------------------------------------------------------------------- #
#  Config                                                                      #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TechnologyFlashlightConfig:
    head_form: HeadForm = "smooth_reflector_cone"
    body_form: BodyForm = "straight_cyl_barrel"
    switch_mech: SwitchMech = "side_push_button"
    carry_feature: CarryFeature = "lanyard_strap_loop"
    palette_style: PaletteStyle = "yellow_plastic"

    head_crenellation_count: int = 16
    barrel_radius: float = 0.020
    barrel_length: float = 0.150
    head_ratio: float = 1.70
    head_length: float = 0.052
    reflector_depth_ratio: float = 0.80
    shoulder_length: float = 0.018
    seed: int = 0


@dataclass(frozen=True)
class ResolvedTechnologyFlashlightConfig:
    head_form: HeadForm
    body_form: BodyForm
    switch_mech: SwitchMech
    carry_feature: CarryFeature
    palette_style: PaletteStyle
    head_crenellation_count: int
    barrel_radius: float
    barrel_length: float
    head_radius: float
    head_length: float
    reflector_depth_ratio: float
    shoulder_length: float
    seed: int
    palette: dict[str, tuple[float, float, float, float]]


def resolve_config(
    config: TechnologyFlashlightConfig | ResolvedTechnologyFlashlightConfig,
) -> ResolvedTechnologyFlashlightConfig:
    if isinstance(config, ResolvedTechnologyFlashlightConfig):
        return config

    head_form = str(config.head_form)
    body_form = str(config.body_form)
    switch_mech = str(config.switch_mech)
    carry_feature = str(config.carry_feature)
    palette_style = str(config.palette_style)

    if head_form not in VALID_HEADS:
        raise ValueError(f"head_form must be one of {sorted(VALID_HEADS)}, got {head_form!r}")
    if body_form not in VALID_BODIES:
        raise ValueError(f"body_form must be one of {sorted(VALID_BODIES)}, got {body_form!r}")
    if switch_mech not in VALID_SWITCHES:
        raise ValueError(f"switch_mech must be one of {sorted(VALID_SWITCHES)}, got {switch_mech!r}")
    if carry_feature not in VALID_CARRIES:
        raise ValueError(f"carry_feature must be one of {sorted(VALID_CARRIES)}, got {carry_feature!r}")
    if palette_style not in VALID_PALETTES:
        raise ValueError(f"palette_style must be one of {sorted(VALID_PALETTES)}, got {palette_style!r}")

    # Compatibility gate: the tail-cap click switch occupies the rear, so a
    # tail-eyelet lanyard would collide with it. Degrade lanyard -> pocket clip
    # for that combination (documented in the spec compatibility matrix).
    if switch_mech == "tailcap_click_switch" and carry_feature == "lanyard_strap_loop":
        carry_feature = "spring_pocket_clip"

    barrel_radius = _clamp(config.barrel_radius, 0.016, 0.030)
    barrel_length = _clamp(config.barrel_length, 0.110, 0.200)
    head_length = _clamp(config.head_length, 0.036, 0.072)
    shoulder_length = _clamp(config.shoulder_length, 0.012, 0.028)
    head_ratio = _clamp(config.head_ratio, 1.30, 2.35)
    reflector_depth_ratio = _clamp(config.reflector_depth_ratio, 0.50, 0.95)

    # equation + inequality: head radius derives from barrel radius, but must be
    # visibly wider than the barrel (category hero constraint).
    head_radius = max(barrel_radius * head_ratio, barrel_radius + 0.013)

    crenel = int(round(_clamp(config.head_crenellation_count, 6, 24)))

    palette = dict(PALETTES[palette_style])

    return ResolvedTechnologyFlashlightConfig(
        head_form=head_form,  # type: ignore[arg-type]
        body_form=body_form,  # type: ignore[arg-type]
        switch_mech=switch_mech,  # type: ignore[arg-type]
        carry_feature=carry_feature,  # type: ignore[arg-type]
        palette_style=palette_style,  # type: ignore[arg-type]
        head_crenellation_count=crenel,
        barrel_radius=barrel_radius,
        barrel_length=barrel_length,
        head_radius=head_radius,
        head_length=head_length,
        reflector_depth_ratio=reflector_depth_ratio,
        shoulder_length=shoulder_length,
        seed=int(config.seed),
        palette=palette,
    )


# --------------------------------------------------------------------------- #
#  Seed sampling                                                               #
# --------------------------------------------------------------------------- #
def _sample_crenellation_count(rng: random.Random) -> int:
    # Weighted: small N (coarse teeth / medium ribs) common, dense ribs rare.
    band = rng.choices(("low", "mid", "high"), weights=(0.5, 0.35, 0.15))[0]
    if band == "low":
        return rng.randint(6, 10)
    if band == "mid":
        return rng.randint(11, 16)
    return rng.randint(17, 24)


def config_from_seed(seed: int) -> ResolvedTechnologyFlashlightConfig:
    # Procedural for every seed, including 0 (no special-cased curated table).
    rng = random.Random(seed)
    head_form = rng.choice(list(HeadForm.__args__))  # type: ignore[attr-defined]
    body_form = rng.choice(list(BodyForm.__args__))  # type: ignore[attr-defined]
    switch_mech = rng.choice(list(SwitchMech.__args__))  # type: ignore[attr-defined]
    carry_feature = rng.choice(list(CarryFeature.__args__))  # type: ignore[attr-defined]
    palette_style = rng.choice(PALETTE_STYLES)

    ratio_range, len_range, depth = _HEAD_FORM_KNOBS[head_form]
    cfg = TechnologyFlashlightConfig(
        head_form=head_form,
        body_form=body_form,
        switch_mech=switch_mech,
        carry_feature=carry_feature,
        palette_style=palette_style,
        head_crenellation_count=_sample_crenellation_count(rng),
        barrel_radius=rng.uniform(0.016, 0.030),
        barrel_length=rng.uniform(0.115, 0.195),
        head_ratio=rng.uniform(*ratio_range),
        head_length=rng.uniform(*len_range),
        reflector_depth_ratio=_clamp(depth + rng.uniform(-0.05, 0.05), 0.50, 0.95),
        shoulder_length=rng.uniform(0.013, 0.026),
        seed=seed,
    )
    return resolve_config(cfg)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    cfg = config_from_seed(seed)
    n = cfg.head_crenellation_count
    n_band = "n_le_8" if n <= 8 else ("n_9_16" if n <= 16 else "n_17_24")
    return [
        ("head_form", cfg.head_form),
        ("body_form", cfg.body_form),
        ("switch_mech", cfg.switch_mech),
        ("carry_feature", cfg.carry_feature),
        ("crenellation_count", n_band),
    ]


# --------------------------------------------------------------------------- #
#  Geometry helpers                                                            #
# --------------------------------------------------------------------------- #
def _material_map(model: ArticulatedObject, cfg: ResolvedTechnologyFlashlightConfig):
    return {key: model.material(f"flashlight_{key}", rgba=rgba) for key, rgba in cfg.palette.items()}


def _mesh(assets: AssetContext, geom, name: str):
    fname = name if name.endswith(".obj") else f"flashlight_{name}.obj"
    return mesh_from_geometry(geom, assets.mesh_path(fname))


def _head_stations(cfg: ResolvedTechnologyFlashlightConfig):
    """Return the longitudinal stations of the head (head points toward -X)."""
    head_back_x = -cfg.shoulder_length
    head_front_x = head_back_x - cfg.head_length
    return head_front_x, head_back_x


def _emit_head_visuals(
    part,
    cfg: ResolvedTechnologyFlashlightConfig,
    mats,
    assets: AssetContext,
    *,
    twist: bool,
) -> None:
    """Emit the head optics (hollow shell + curved reflector + lens + LED + bezel
    ring + N crenellations) onto ``part`` (``body`` when fixed, ``focus_head``
    when twist)."""
    head_r = cfg.head_radius
    head_wall = min(0.011, head_r * 0.30)
    head_inner_r = max(0.010, head_r - head_wall)
    head_back_r = head_r * 0.96
    head_front_x, head_back_x = _head_stations(cfg)

    # Hollow flared head shell (curved Lathe surface, opens toward -X).
    shell_outer = [
        (head_front_x, head_r),
        (0.5 * (head_front_x + head_back_x), head_r * 0.99),
        (head_back_x, head_back_r),
    ]
    shell = LatheGeometry.from_shell_profiles(
        [(r, x) for (x, r) in shell_outer],
        [(max(0.008, r - head_wall), x) for (x, r) in shell_outer],
        segments=72,
        start_cap="flat",
        end_cap="flat",
        lip_samples=5,
    )
    part.visual(_mesh(assets, shell, "head_shell"), origin=AXIS_TO_X, material=mats["body"], name="head_shell", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"))

    # Deep/shallow curved reflector funnel nested inside the head.
    refl_depth = cfg.head_length * cfg.reflector_depth_ratio
    mouth_x = head_front_x + 0.005
    throat_x = min(mouth_x + refl_depth, head_back_x - 0.003)
    # Mouth reaches into the head-shell inner wall so the reflector is a
    # connected island (touches head_shell), not a floating funnel.
    mouth_r = head_inner_r + 0.0015
    throat_r = max(0.005, cfg.barrel_radius * 0.28)
    refl_outer: list[tuple[float, float]] = []
    for s in (0.0, 0.33, 0.66, 1.0):
        x = mouth_x + s * (throat_x - mouth_x)
        r = mouth_r + (throat_r - mouth_r) * (s**0.7)
        refl_outer.append((x, r))
    reflector = LatheGeometry.from_shell_profiles(
        [(r, x) for (x, r) in refl_outer],
        [(max(0.0035, r - 0.0015), x) for (x, r) in refl_outer],
        segments=64,
        start_cap="flat",
        end_cap="round",
        lip_samples=6,
    )
    part.visual(_mesh(assets, reflector, "reflector"), origin=AXIS_TO_X, material=mats["reflector"], name="reflector", material_class_id="metal.aluminum_bare")

    # LED emitter plugging the reflector throat (overlaps the reflector wall).
    part.visual(
        Sphere(radius=max(0.006, throat_r + 0.004)),
        origin=Origin(xyz=(throat_x, 0.0, 0.0)),
        material=mats["led"],
        name="led_emitter", material_class_id="tech.emissive_surface",
    )

    # Clear lens disc seated against the front rim / inner wall.
    lens_r = head_inner_r + 0.0006
    part.visual(
        Cylinder(radius=lens_r, length=0.004),
        origin=_axis_x_origin(head_front_x + 0.002),
        material=mats["lens"],
        name="lens_disc", material_class_id="glass.clear_transparent",
    )

    # Black front bezel ring at the rim.
    ring = LatheGeometry.from_shell_profiles(
        [(head_r + 0.001, head_front_x), (head_r + 0.001, head_front_x + 0.006)],
        [(head_inner_r, head_front_x), (head_inner_r, head_front_x + 0.006)],
        segments=48,
        start_cap="flat",
        end_cap="flat",
        lip_samples=4,
    )
    part.visual(_mesh(assets, ring, "front_bezel_ring"), origin=AXIS_TO_X, material=mats["bezel"], name="front_bezel_ring", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"))

    # ---- N crenellations (multiplicity, FIXED inline visuals) ----
    n = cfg.head_crenellation_count
    if cfg.head_form == "crenellated_strike_bezel":
        # Proud attack teeth standing off the front rim.
        tooth_r = max(0.003, head_r * 0.11)
        tooth_len = 0.012
        ring_r = head_r - tooth_r * 0.6
        for i in range(n):
            theta = 2.0 * math.pi * i / n
            y = ring_r * math.cos(theta)
            z = ring_r * math.sin(theta)
            part.visual(
                Cylinder(radius=tooth_r, length=tooth_len),
                origin=_axis_x_origin(head_front_x - 0.004, y, z),
                material=mats["bezel"],
                name=f"bezel_tooth_{i}", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
            )
    else:
        # Longitudinal grip ribs hugging the head surface.
        rib_r = max(0.0022, head_r * 0.055)
        rib_len = 0.62 * cfg.head_length
        rib_cx = 0.5 * (head_front_x + head_back_x)
        surf_r = head_r + rib_r * 0.4
        for i in range(n):
            theta = 2.0 * math.pi * i / n
            y = surf_r * math.cos(theta)
            z = surf_r * math.sin(theta)
            part.visual(
                Cylinder(radius=rib_r, length=rib_len),
                origin=_axis_x_origin(rib_cx, y, z),
                material=mats["body"],
                name=f"head_rib_{i}", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
            )

    if twist:
        # Off-axis marker so the continuous twist is detectable.
        part.visual(
            Cylinder(radius=max(0.004, head_r * 0.12), length=0.016),
            origin=_axis_x_origin(head_front_x - 0.005, head_r - 0.004, 0.0),
            material=mats["bezel"],
            name="bezel_marker", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
        )


def _emit_shoulder(body, cfg: ResolvedTechnologyFlashlightConfig, mats, assets, front_r: float) -> None:
    """Curved collar connecting the body front (x=0) to the head back."""
    _, head_back_x = _head_stations(cfg)
    head_back_r = cfg.head_radius * 0.96
    wall = 0.004
    outer = [
        (head_back_x, head_back_r),
        (0.5 * head_back_x, 0.5 * (front_r + head_back_r)),
        (0.0, front_r),
    ]
    shoulder = LatheGeometry.from_shell_profiles(
        [(r, x) for (x, r) in outer],
        [(max(0.006, r - wall), x) for (x, r) in outer],
        segments=64,
        start_cap="flat",
        end_cap="flat",
        lip_samples=5,
    )
    body.visual(_mesh(assets, shoulder, "shoulder_shell"), origin=AXIS_TO_X, material=mats["body"], name="shoulder_shell", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"))


def _emit_body(body, cfg: ResolvedTechnologyFlashlightConfig, mats, assets) -> float:
    """Emit the barrel/grip geometry. Returns the body front radius at x=0."""
    r_b = cfg.barrel_radius
    L = cfg.barrel_length
    if cfg.body_form == "straight_cyl_barrel":
        body.visual(
            Cylinder(radius=r_b, length=L),
            origin=_axis_x_origin(L / 2.0),
            material=mats["body"],
            name="barrel_shell", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
        )
        front_r = r_b
    else:
        # Stepped tactical tube from stacked curved cylinders (tail / grip swell /
        # mid / front lip) -- different volumetric envelope, same round primitive.
        # Overlapping stacked cylinders (contiguous along X, no island gaps).
        segs = [
            ("tail_seg", r_b * 0.96, 0.40 * L, 0.83 * L),
            ("grip_seg", r_b * 1.11, 0.30 * L, 0.55 * L),
            ("mid_seg", r_b, 0.40 * L, 0.28 * L),
            ("lip_seg", r_b * 1.06, 0.12 * L, 0.05 * L),
        ]
        for name, r, seg_len, cx in segs:
            body.visual(
                Cylinder(radius=r, length=seg_len),
                origin=_axis_x_origin(cx),
                material=mats["body"],
                name=name, material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
            )
        # Longitudinal grip ridges on the swell (molded knurl, host-conformal).
        for i in range(8):
            theta = 2.0 * math.pi * i / 8.0
            y = (r_b * 1.11 + 0.0012) * math.cos(theta)
            z = (r_b * 1.11 + 0.0012) * math.sin(theta)
            body.visual(
                Cylinder(radius=0.0016, length=0.30 * L),
                origin=_axis_x_origin(0.54 * L, y, z),
                material=mats["accent"],
                name=f"grip_knurl_{i}", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
            )
        front_r = r_b * 1.06
    return front_r


def _barrel_element_name(cfg: ResolvedTechnologyFlashlightConfig) -> str:
    return "barrel_shell" if cfg.body_form == "straight_cyl_barrel" else "mid_seg"


def _tail_element_name(cfg: ResolvedTechnologyFlashlightConfig) -> str:
    return "barrel_shell" if cfg.body_form == "straight_cyl_barrel" else "tail_seg"


def _tail_end_x(cfg: ResolvedTechnologyFlashlightConfig) -> float:
    """World +X coordinate of the rear-most barrel face (the tail seat)."""
    if cfg.body_form == "straight_cyl_barrel":
        return cfg.barrel_length
    # stepped: tail_seg cx=0.83L, len=0.40L -> +X extreme = 1.03L.
    return 1.03 * cfg.barrel_length


# --------------------------------------------------------------------------- #
#  Switch modules                                                             #
# --------------------------------------------------------------------------- #
def _emit_side_push(model, body, cfg, mats) -> None:
    r_b = cfg.barrel_radius
    bx = 0.22 * cfg.barrel_length
    boss_h = 0.006
    body.visual(
        Cylinder(radius=0.008, height=boss_h),
        origin=Origin(xyz=(bx, 0.0, r_b)),
        material=mats["body"],
        name="button_boss", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
    )
    button = model.part("push_button")
    button.visual(
        Cylinder(radius=0.006, height=0.006),
        origin=Origin(),
        material=mats["button"],
        name="button_cap", material_class_id="rubber.smooth_plain",
    )
    button.inertial = Inertial.from_geometry(Box((0.012, 0.012, 0.006)), mass=0.004)
    model.articulation(
        "button_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=button,
        origin=Origin(xyz=(bx, 0.0, r_b + boss_h / 2.0 + 0.003)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.05, lower=0.0, upper=0.0015),
        mating=MatingContract(
            parent_face_geometry="button_boss",
            parent_face_side="positive_z",
            child_face_geometry="button_cap",
            child_face_side="negative_z",
            contact_tol=0.0018,
        ),
    )


def _emit_tailcap_click(model, body, cfg, mats) -> None:
    r_b = cfg.barrel_radius
    tail_end = _tail_end_x(cfg)
    tail = model.part("tail_button")
    tail.visual(
        Cylinder(radius=r_b + 0.003, length=0.014),
        origin=_axis_x_origin(0.007),
        material=mats["bezel"],
        name="tail_cap", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
    )
    tail.visual(
        Cylinder(radius=(r_b + 0.003) * 0.55, height=0.003),
        origin=_axis_x_origin(0.0155),
        material=mats["button"],
        name="rubber_boot", material_class_id="rubber.smooth_plain",
    )
    tail.inertial = Inertial.from_geometry(Box((0.016, 0.02, 0.02)), mass=0.02)
    model.articulation(
        "tail_press",
        ArticulationType.PRISMATIC,
        parent=body,
        child=tail,
        origin=Origin(xyz=(tail_end, 0.0, 0.0)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.05, lower=0.0, upper=0.003),
        mating=MatingContract(
            parent_face_geometry=_tail_element_name(cfg),
            parent_face_side="positive_x",
            child_face_geometry="tail_cap",
            child_face_side="negative_x",
            contact_tol=0.0018,
        ),
    )


def _emit_slide_switch(model, body, cfg, mats) -> None:
    r_b = cfg.barrel_radius
    tx = 0.30 * cfg.barrel_length
    track_h = 0.004
    body.visual(
        Box((0.030, 0.014, track_h)),
        origin=Origin(xyz=(tx, 0.0, r_b + track_h / 2.0)),
        material=mats["bezel"],
        name="slide_track", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
    )
    slider = model.part("slider")
    slider.visual(
        Box((0.012, 0.010, 0.006)),
        origin=Origin(),
        material=mats["button"],
        name="slider_knob", material_class_id="rubber.smooth_plain",
    )
    slider.inertial = Inertial.from_geometry(Box((0.012, 0.010, 0.006)), mass=0.004)
    model.articulation(
        "body_to_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=slider,
        origin=Origin(xyz=(tx, 0.0, r_b + track_h + 0.003)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.05, lower=0.0, upper=0.008),
        mating=MatingContract(
            parent_face_geometry="slide_track",
            parent_face_side="positive_z",
            child_face_geometry="slider_knob",
            child_face_side="negative_z",
            contact_tol=0.0018,
        ),
    )


def _emit_twist_head(model, body, cfg, mats, assets) -> None:
    head = model.part("focus_head")
    _emit_head_visuals(head, cfg, mats, assets, twist=True)
    head.inertial = Inertial.from_geometry(
        Box((cfg.head_length + 0.02, 2 * cfg.head_radius, 2 * cfg.head_radius)),
        mass=0.08,
        origin=Origin(xyz=(-(cfg.shoulder_length + 0.5 * cfg.head_length), 0.0, 0.0)),
    )
    model.articulation(
        "head_focus_twist",
        ArticulationType.CONTINUOUS,
        parent=body,
        child=head,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.6, velocity=4.0),
    )


# --------------------------------------------------------------------------- #
#  Carry modules                                                              #
# --------------------------------------------------------------------------- #
def _emit_tail_cap(body, cfg, mats) -> None:
    """Plain fixed tail cap (used when the switch is not a tail-cap click)."""
    r_b = cfg.barrel_radius
    body.visual(
        Cylinder(radius=r_b + 0.002, length=0.014),
        origin=_axis_x_origin(_tail_end_x(cfg) + 0.006),
        material=mats["bezel"],
        name="tail_cap", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
    )


def _emit_lanyard(model, body, cfg, mats, assets) -> None:
    r_b = cfg.barrel_radius
    tail_end = _tail_end_x(cfg)
    # Short tail cap flush with the barrel end; eyelet mounts on its rear face,
    # so the strap loop emerges BEHIND the cap (no strap/cap overlap).
    body.visual(
        Cylinder(radius=r_b + 0.002, length=0.012),
        origin=_axis_x_origin(tail_end + 0.005),
        material=mats["bezel"],
        name="tail_cap", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"black_tactical", "silver_industrial", "olive_drab", "gunmetal"} else "plastic.opaque_glossy_molded"),
    )
    eyelet_x = tail_end + 0.013  # torus tube (±0.0026) overlaps the cap rear face.
    body.visual(
        _mesh(
            assets,
            TorusGeometry(radius=r_b * 0.72, tube=0.0026, radial_segments=16, tubular_segments=48),
            "tail_eyelet",
        ),
        origin=_axis_x_origin(eyelet_x),
        material=mats["bezel"],
        name="tail_eyelet", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"yellow_plastic", "black_tactical", "silver_industrial", "hi_vis_orange", "gunmetal"} else "metal.paint_coated"),
    )
    strap = model.part("strap")
    re = r_b * 0.72  # eyelet ring radius; strap endpoints sit ON the ring tube.
    loop = tube_from_spline_points(
        [
            (0.0, re, 0.000),
            (0.026, re + 0.020, -0.002),
            (0.082, re + 0.026, -0.006),
            (0.114, 0.000, -0.008),
            (0.082, -(re + 0.026), -0.006),
            (0.026, -(re + 0.020), -0.002),
            (0.0, -re, 0.000),
        ],
        radius=0.0026,
        samples_per_segment=16,
        closed_spline=True,
        radial_segments=14,
        cap_ends=False,
    )
    strap.visual(_mesh(assets, loop, "strap_loop"), origin=Origin(), material=mats["accent"], name="strap_loop", material_class_id="fabric.webbing")
    strap.inertial = Inertial.from_geometry(Box((0.12, 0.09, 0.02)), mass=0.01)
    model.articulation(
        "body_to_strap",
        ArticulationType.FIXED,
        parent=body,
        child=strap,
        origin=Origin(xyz=(eyelet_x, 0.0, 0.0)),
    )


def _emit_pocket_clip(body, cfg, mats, assets) -> None:
    r_b = cfg.barrel_radius
    L = cfg.barrel_length
    # Clamp band around the body where the clip attaches (on -Z side).
    band_x = 0.30 * L
    body.visual(
        _mesh(
            assets,
            TorusGeometry(radius=r_b + 0.0016, tube=0.0026, radial_segments=16, tubular_segments=40),
            "clip_mount",
        ),
        origin=_axis_x_origin(band_x),
        material=mats["accent"],
        name="clip_mount", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"yellow_plastic", "black_tactical", "silver_industrial", "hi_vis_orange", "gunmetal"} else "metal.paint_coated"),
    )
    # Bent spring clip running toward the tail on the -Z side.
    pts = [
        (band_x, 0.0, -(r_b + 0.0016)),
        (band_x + 0.010, 0.0, -(r_b + 0.006)),
        (band_x + 0.045, 0.0, -(r_b + 0.008)),
        (band_x + 0.085, 0.0, -(r_b + 0.007)),
        (band_x + 0.104, 0.0, -(r_b + 0.003)),
    ]
    clip = sweep_profile_along_spline(
        pts,
        profile=rounded_rect_profile(0.0012, 0.010, radius=0.0004),
        samples_per_segment=14,
        up_hint=(0.0, 1.0, 0.0),
        cap_profile=True,
    )
    body.visual(_mesh(assets, clip, "pocket_clip"), origin=Origin(), material=mats["accent"], name="pocket_clip", material_class_id=("metal.blackened_gunmetal" if cfg.palette_style in {"yellow_plastic", "black_tactical", "silver_industrial", "hi_vis_orange", "gunmetal"} else "metal.paint_coated"))


# --------------------------------------------------------------------------- #
#  Build                                                                       #
# --------------------------------------------------------------------------- #
def build_flashlight(
    config: TechnologyFlashlightConfig | ResolvedTechnologyFlashlightConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = resolve_config(config or TechnologyFlashlightConfig())
    assets = assets or AssetContext.from_script(__file__)
    model = ArticulatedObject(
        name=f"technology_flashlight_{cfg.seed}",
        meta={"category": "Technology_Flashlight"},
    )
    model.set_assets(assets)
    mats = _material_map(model, cfg)

    body = model.part("body")
    front_r = _emit_body(body, cfg, mats, assets)
    _emit_shoulder(body, cfg, mats, assets, front_r)

    twist = cfg.switch_mech == "twist_focus_head"
    if not twist:
        _emit_head_visuals(body, cfg, mats, assets, twist=False)

    # Plain tail cap unless the tail is occupied by the tail-cap click switch or
    # the lanyard module (which emits its own cap + eyelet).
    if cfg.switch_mech != "tailcap_click_switch" and cfg.carry_feature != "lanyard_strap_loop":
        _emit_tail_cap(body, cfg, mats)

    body.inertial = Inertial.from_geometry(
        Box((cfg.barrel_length + 2 * cfg.head_length, 2.4 * cfg.head_radius, 2.4 * cfg.head_radius)),
        mass=0.28,
        origin=Origin(xyz=(0.4 * cfg.barrel_length, 0.0, 0.0)),
    )

    # ---- switch ----
    if cfg.switch_mech == "side_push_button":
        _emit_side_push(model, body, cfg, mats)
    elif cfg.switch_mech == "twist_focus_head":
        _emit_twist_head(model, body, cfg, mats, assets)
    elif cfg.switch_mech == "tailcap_click_switch":
        _emit_tailcap_click(model, body, cfg, mats)
    else:
        _emit_slide_switch(model, body, cfg, mats)

    # ---- carry ----
    if cfg.carry_feature == "lanyard_strap_loop":
        _emit_lanyard(model, body, cfg, mats, assets)
    elif cfg.carry_feature == "spring_pocket_clip":
        _emit_pocket_clip(body, cfg, mats, assets)

    return model


def build_seeded_flashlight(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_flashlight(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
#  Tests                                                                       #
# --------------------------------------------------------------------------- #
def run_flashlight_tests(
    object_model: ArticulatedObject,
    config: TechnologyFlashlightConfig | ResolvedTechnologyFlashlightConfig | None = None,
) -> TestReport:
    cfg = resolve_config(config or TechnologyFlashlightConfig())
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()

    ctx.check(
        "category_is_technology_flashlight",
        object_model.meta.get("category") == "Technology_Flashlight",
    )
    part_names = {p.name for p in object_model.parts}
    ctx.check("has_body_root", "body" in part_names)

    twist = cfg.switch_mech == "twist_focus_head"
    head_part = "focus_head" if twist else "body"

    # ---- Hero: head optics exist and the head is visibly wider than the barrel ----
    head_box = ctx.part_element_world_aabb(object_model.get_part(head_part), elem="head_shell")
    refl_box = ctx.part_element_world_aabb(object_model.get_part(head_part), elem="reflector")
    lens_box = ctx.part_element_world_aabb(object_model.get_part(head_part), elem="lens_disc")
    ctx.check("head_shell_present", head_box is not None)
    ctx.check("reflector_present", refl_box is not None)
    ctx.check("lens_present", lens_box is not None)
    if head_box is not None:
        head_y = head_box[1][1] - head_box[0][1]
        ctx.check(
            "head_wider_than_barrel",
            head_y > 2.0 * cfg.barrel_radius + 0.020,
            details=f"head_y={head_y}, barrel_dia={2 * cfg.barrel_radius}",
        )
    if refl_box is not None and lens_box is not None:
        # Lens sits at/near the front of the reflector mouth (both curved optics visible).
        ctx.check(
            "lens_in_front_of_reflector",
            lens_box[0][0] <= refl_box[0][0] + 0.006,
            details=f"lens_x0={lens_box[0][0]}, refl_x0={refl_box[0][0]}",
        )

    # ---- >=1 non-FIXED joint always exists ----
    joints = {j.name: j for j in object_model.articulations}
    movable = [
        n
        for n, j in joints.items()
        if getattr(j.articulation_type, "name", str(j.articulation_type)).upper() != "FIXED"
    ]
    ctx.check("has_movable_joint", len(movable) >= 1, details=f"movable={movable}")

    # ---- allowances for intentional seated/threaded contacts ----
    if twist:
        ctx.allow_overlap(
            "focus_head", "body", elem_a="head_shell", elem_b="shoulder_shell",
            reason="Twist head sleeve is seated over the body shoulder collar.",
        )
    if cfg.switch_mech == "side_push_button":
        ctx.allow_overlap(
            "push_button", "body", elem_a="button_cap", elem_b="button_boss",
            reason="Push button cap is seated into the boss and depresses into it.",
        )
    if cfg.switch_mech == "tailcap_click_switch":
        ctx.allow_overlap(
            "tail_button", "body", elem_a="tail_cap", elem_b=_tail_element_name(cfg),
            reason="Tail-cap click button seats on and presses forward into the barrel rear.",
        )
    if cfg.switch_mech == "longitudinal_slide_switch":
        ctx.allow_overlap(
            "slider", "body", elem_a="slider_knob", elem_b="slide_track",
            reason="Thumb slider rides in the recessed track.",
        )
    if cfg.carry_feature == "lanyard_strap_loop":
        ctx.allow_overlap(
            "strap", "body", elem_a="strap_loop", elem_b="tail_eyelet",
            reason="Soft nylon strap is threaded through the tail eyelet opening.",
        )

    # ---- targeted motion semantics per mechanism ----
    if cfg.switch_mech == "side_push_button":
        press = object_model.get_articulation("button_press")
        rest = ctx.part_world_position(object_model.get_part("push_button"))
        with ctx.pose({press: 0.0015}):
            pressed = ctx.part_world_position(object_model.get_part("push_button"))
        ctx.check("side_button_presses_inward", pressed[2] < rest[2] - 0.001, details=f"rest={rest}, pressed={pressed}")
    elif cfg.switch_mech == "tailcap_click_switch":
        press = object_model.get_articulation("tail_press")
        rest = ctx.part_world_position(object_model.get_part("tail_button"))
        with ctx.pose({press: 0.003}):
            pressed = ctx.part_world_position(object_model.get_part("tail_button"))
        ctx.check("tail_button_presses_forward", pressed[0] < rest[0] - 0.002, details=f"rest={rest}, pressed={pressed}")
    elif cfg.switch_mech == "longitudinal_slide_switch":
        slide = object_model.get_articulation("body_to_slide")
        rest = ctx.part_world_position(object_model.get_part("slider"))
        with ctx.pose({slide: 0.008}):
            slid = ctx.part_world_position(object_model.get_part("slider"))
        ctx.check("slider_travels_along_axis", slid[0] > rest[0] + 0.004, details=f"rest={rest}, slid={slid}")
    else:  # twist_focus_head
        twist_j = object_model.get_articulation("head_focus_twist")
        m0 = ctx.part_element_world_aabb(object_model.get_part("focus_head"), elem="bezel_marker")
        c0 = (0.5 * (m0[0][1] + m0[1][1]), 0.5 * (m0[0][2] + m0[1][2]))
        with ctx.pose({twist_j: math.pi / 2.0}):
            m1 = ctx.part_element_world_aabb(object_model.get_part("focus_head"), elem="bezel_marker")
            c1 = (0.5 * (m1[0][1] + m1[1][1]), 0.5 * (m1[0][2] + m1[1][2]))
        ctx.check(
            "focus_twist_rotates_marker",
            c0[0] > 0.010 and c1[1] > 0.010 and abs(c1[0]) < 0.010,
            details=f"rest(y,z)={c0}, quarter(y,z)={c1}",
        )

    ctx.check("slot_choices_exposed", len(slot_choices_for_seed(cfg.seed)) == 5)

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "TechnologyFlashlightConfig",
    "ResolvedTechnologyFlashlightConfig",
    "build_flashlight",
    "build_seeded_flashlight",
    "config_from_seed",
    "resolve_config",
    "run_flashlight_tests",
    "slot_choices_for_seed",
]
