# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — circuit_breaker (Electrical_Wiring / Circuit breaker).

A DIN-rail modular MCB: a FIXED molded ``housing`` (root) plus a SINGLE
``toggle`` part joined by one REVOLUTE joint about the pole axis (X). The toggle
carries a shared ``pivot_shaft`` with one ``rotor_drum`` per pole and the
operating handle fixed to the drum rim. Pole features are multiplied over an
``pole_x`` tuple (multiplicity axis N). Discrete slots (hand-rolled, cushion
style — no SlotSpec assembler):

- ③A ``case_form``     : box / rounded (ExtrudeGeometry+rounded_rect_profile) / stepped
- ③B ``handle_form``   : flag_toggle / thumb_rocker / mccb_wide_handle
- ④C ``terminal_type`` : screw_cavity / screw_wire_leads / plugin_stab
- ④D ``front_feature`` : indicator_window / plain_label / rcbo_test_button
- ④E ``mount``         : din_clip / surface_screw_base
- ①  ``pole_count`` N ∈ [1,4] (weighted), extrapolable
- ⑥  ``palette_style`` : 5 realistic MCB colorways

Sources: origins A (white 3P, box) `rec_use...eeb289c4` + B (black 2P, rounded)
`rec_use...7bb9b32f`, forks 1pole/4pole/mccb_rotary_handle/plugin_stab_terminals/
rcbo_test_button/surface_mount_base. rounded_case keeps ExtrudeGeometry and the
side vent keeps SlotPatternPanelGeometry (TEMPLATE_DESIGN_RULES ③).

Frame: X = pole width, Y = depth (front face at -Y), Z = vertical (top terminal
+Z, bottom -Z). Body centered at origin.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    MotionLimits,
    Origin,
    SlotPatternPanelGeometry,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot vocabularies
# ---------------------------------------------------------------------------
CaseForm = Literal["box_case", "rounded_case", "stepped_case"]
HandleForm = Literal["flag_toggle", "thumb_rocker", "mccb_wide_handle"]
TerminalType = Literal["screw_cavity", "screw_wire_leads", "plugin_stab"]
FrontFeature = Literal["indicator_window", "plain_label", "rcbo_test_button"]
Mount = Literal["din_clip", "surface_screw_base"]
PaletteStyle = Literal["white_blue", "black_gray", "gray_blue", "white_red", "beige_black"]

CASE_FORMS: tuple[CaseForm, ...] = ("box_case", "rounded_case", "stepped_case")
HANDLE_FORMS: tuple[HandleForm, ...] = ("flag_toggle", "thumb_rocker", "mccb_wide_handle")
TERMINAL_TYPES: tuple[TerminalType, ...] = ("screw_cavity", "screw_wire_leads", "plugin_stab")
FRONT_FEATURES: tuple[FrontFeature, ...] = (
    "indicator_window",
    "plain_label",
    "rcbo_test_button",
)
MOUNTS: tuple[Mount, ...] = ("din_clip", "surface_screw_base")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_blue",
    "black_gray",
    "gray_blue",
    "white_red",
    "beige_black",
)

N_MIN = 1
N_MAX = 4
# Pole-count weights (§8): 1P / 2P most common, 3P / 4P rarer.
POLE_COUNT_WEIGHTS = (0.30, 0.35, 0.20, 0.15)

# 5 realistic DIN MCB colorways (case + handle families) driving every visual.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_blue": {  # Chint NB1 / Legrand
        "case": (0.92, 0.95, 0.95, 1.0),
        "case_accent": (0.82, 0.87, 0.88, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
        "handle": (0.00, 0.28, 0.70, 1.0),
        "handle_print": (0.00, 0.62, 0.78, 1.0),
        "screw": (0.13, 0.14, 0.14, 1.0),
        "terminal_metal": (0.80, 0.58, 0.25, 1.0),
        "stab_metal": (0.74, 0.74, 0.70, 1.0),
        "copper": (0.85, 0.36, 0.15, 1.0),
        "wire_a": (0.55, 0.035, 0.025, 1.0),
        "wire_b": (0.02, 0.02, 0.02, 1.0),
        "label": (0.46, 0.49, 0.51, 1.0),
        "print": (0.02, 0.02, 0.02, 1.0),
        "din_metal": (0.58, 0.61, 0.58, 1.0),
        "indicator": (0.10, 0.55, 0.20, 1.0),
        "test_button": (0.95, 0.72, 0.08, 1.0),
        "test_bezel": (0.70, 0.72, 0.73, 1.0),
        "vent": (0.60, 0.63, 0.63, 1.0),
    },
    "black_gray": {  # Eaton / CH
        "case": (0.015, 0.017, 0.016, 1.0),
        "case_accent": (0.06, 0.065, 0.06, 1.0),
        "dark": (0.0, 0.0, 0.0, 1.0),
        "handle": (0.26, 0.27, 0.26, 1.0),
        "handle_print": (0.82, 0.84, 0.80, 1.0),
        "screw": (0.55, 0.57, 0.55, 1.0),
        "terminal_metal": (0.80, 0.58, 0.25, 1.0),
        "stab_metal": (0.74, 0.74, 0.70, 1.0),
        "copper": (0.85, 0.36, 0.15, 1.0),
        "wire_a": (0.55, 0.035, 0.025, 1.0),
        "wire_b": (0.01, 0.01, 0.008, 1.0),
        "label": (0.30, 0.32, 0.31, 1.0),
        "print": (0.82, 0.84, 0.80, 1.0),
        "din_metal": (0.58, 0.61, 0.58, 1.0),
        "indicator": (0.85, 0.30, 0.05, 1.0),
        "test_button": (0.90, 0.70, 0.05, 1.0),
        "test_bezel": (0.45, 0.47, 0.47, 1.0),
        "vent": (0.10, 0.11, 0.10, 1.0),
    },
    "gray_blue": {  # ABB S200
        "case": (0.60, 0.63, 0.62, 1.0),
        "case_accent": (0.50, 0.53, 0.52, 1.0),
        "dark": (0.05, 0.05, 0.05, 1.0),
        "handle": (0.10, 0.34, 0.66, 1.0),
        "handle_print": (0.90, 0.92, 0.92, 1.0),
        "screw": (0.35, 0.36, 0.36, 1.0),
        "terminal_metal": (0.72, 0.72, 0.68, 1.0),
        "stab_metal": (0.70, 0.70, 0.66, 1.0),
        "copper": (0.85, 0.36, 0.15, 1.0),
        "wire_a": (0.55, 0.035, 0.025, 1.0),
        "wire_b": (0.02, 0.02, 0.02, 1.0),
        "label": (0.85, 0.87, 0.86, 1.0),
        "print": (0.05, 0.05, 0.05, 1.0),
        "din_metal": (0.55, 0.58, 0.55, 1.0),
        "indicator": (0.90, 0.20, 0.10, 1.0),
        "test_button": (0.15, 0.30, 0.60, 1.0),
        "test_bezel": (0.40, 0.42, 0.42, 1.0),
        "vent": (0.42, 0.44, 0.43, 1.0),
    },
    "white_red": {  # main switch / isolator
        "case": (0.90, 0.92, 0.92, 1.0),
        "case_accent": (0.80, 0.83, 0.83, 1.0),
        "dark": (0.03, 0.03, 0.03, 1.0),
        "handle": (0.62, 0.06, 0.05, 1.0),
        "handle_print": (0.95, 0.95, 0.92, 1.0),
        "screw": (0.15, 0.15, 0.15, 1.0),
        "terminal_metal": (0.80, 0.60, 0.26, 1.0),
        "stab_metal": (0.74, 0.74, 0.70, 1.0),
        "copper": (0.85, 0.36, 0.15, 1.0),
        "wire_a": (0.02, 0.02, 0.02, 1.0),
        "wire_b": (0.35, 0.20, 0.05, 1.0),
        "label": (0.40, 0.42, 0.44, 1.0),
        "print": (0.03, 0.03, 0.03, 1.0),
        "din_metal": (0.60, 0.63, 0.60, 1.0),
        "indicator": (0.10, 0.55, 0.20, 1.0),
        "test_button": (0.90, 0.70, 0.05, 1.0),
        "test_bezel": (0.65, 0.67, 0.68, 1.0),
        "vent": (0.58, 0.61, 0.61, 1.0),
    },
    "beige_black": {  # Siemens 5SL / vintage
        "case": (0.86, 0.82, 0.72, 1.0),
        "case_accent": (0.76, 0.72, 0.62, 1.0),
        "dark": (0.04, 0.04, 0.03, 1.0),
        "handle": (0.16, 0.16, 0.16, 1.0),
        "handle_print": (0.90, 0.88, 0.82, 1.0),
        "screw": (0.20, 0.20, 0.19, 1.0),
        "terminal_metal": (0.80, 0.58, 0.25, 1.0),
        "stab_metal": (0.72, 0.72, 0.68, 1.0),
        "copper": (0.85, 0.36, 0.15, 1.0),
        "wire_a": (0.15, 0.20, 0.55, 1.0),
        "wire_b": (0.35, 0.20, 0.05, 1.0),
        "label": (0.45, 0.44, 0.40, 1.0),
        "print": (0.10, 0.10, 0.08, 1.0),
        "din_metal": (0.58, 0.60, 0.57, 1.0),
        "indicator": (0.85, 0.30, 0.05, 1.0),
        "test_button": (0.88, 0.68, 0.06, 1.0),
        "test_bezel": (0.55, 0.55, 0.52, 1.0),
        "vent": (0.55, 0.53, 0.47, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). DIN MCB: 18 mm per pole module.
# ---------------------------------------------------------------------------
_POLE_SPACING = 0.018
_BODY_DEPTH = 0.069
_BODY_HEIGHT = 0.086
_CORNER_R = 0.006  # rounded_case fillet radius

_PIVOT_FRONT = 0.008  # pivot line is this far in FRONT of the body front face
_SHELF_DEPTH = 0.010  # handle escutcheon (raised front hub) depth
_SHELF_H = 0.030  # handle window height
_BLOCK_PROUD = 0.006  # terminal shoulder front protrusion
_STEP_PROUD = 0.005  # stepped_case front spine protrusion

_DRUM_R = 0.0062
_SHAFT_R = 0.0034
_THROW = 0.40  # nominal handle half-swing (rad)


@dataclass(frozen=True)
class CircuitBreakerConfig:
    case_form: CaseForm | None = None
    handle_form: HandleForm | None = None
    terminal_type: TerminalType | None = None
    front_feature: FrontFeature | None = None
    mount: Mount | None = None
    pole_count: int | None = None
    palette_style: PaletteStyle = "white_blue"
    body_depth_scale: float = 1.0
    body_height_scale: float = 1.0
    handle_throw: float = _THROW
    name: str = "circuit_breaker"


@dataclass(frozen=True)
class ResolvedCircuitBreakerConfig:
    case_form: CaseForm
    handle_form: HandleForm
    terminal_type: TerminalType
    front_feature: FrontFeature
    mount: Mount
    pole_count: int
    palette_style: PaletteStyle
    # Derived geometry.
    pole_spacing: float
    housing_width: float
    half_w: float
    body_depth: float
    half_d: float
    body_height: float
    half_h: float
    front_face_y: float
    pivot_y: float
    pivot_z: float
    front_step: float
    tie_len: float
    pivot_cyl_len: float
    throw: float
    name: str

    @property
    def pole_x(self) -> tuple[float, ...]:
        return tuple(
            (i - (self.pole_count - 1) / 2.0) * self.pole_spacing
            for i in range(self.pole_count)
        )

    @property
    def block_front_y(self) -> float:
        # stepped_case reads as proud terminal shoulders over a recessed center.
        return self.front_face_y - _BLOCK_PROUD - self.front_step

    @property
    def panel_front_y(self) -> float:
        # Label panel stays flush so it never clips the proud rotor drums.
        return self.front_face_y

    @property
    def shelf_front_y(self) -> float:
        # Escutcheon front cups the drum back (drum back = pivot_y + _DRUM_R).
        return self.front_face_y - 0.006

    @property
    def z_top_row(self) -> float:
        return self.half_h - 0.013

    @property
    def z_bot_row(self) -> float:
        return -self.half_h + 0.013


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> CircuitBreakerConfig:
    rng = random.Random(seed)
    return CircuitBreakerConfig(
        case_form=rng.choice(CASE_FORMS),
        handle_form=rng.choice(HANDLE_FORMS),
        terminal_type=rng.choice(TERMINAL_TYPES),
        front_feature=rng.choice(FRONT_FEATURES),
        mount=rng.choice(MOUNTS),
        pole_count=rng.choices(range(N_MIN, N_MAX + 1), weights=POLE_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        body_depth_scale=round(rng.uniform(0.92, 1.10), 4),
        body_height_scale=round(rng.uniform(0.92, 1.12), 4),
        handle_throw=round(rng.uniform(0.32, 0.46), 4),
        name=f"seeded_circuit_breaker_{seed}",
    )


def resolve_config(config: CircuitBreakerConfig | None = None) -> ResolvedCircuitBreakerConfig:
    cfg = config or CircuitBreakerConfig()

    case_form = _pick(cfg.case_form, CASE_FORMS)
    handle_form = _pick(cfg.handle_form, HANDLE_FORMS)
    terminal_type = _pick(cfg.terminal_type, TERMINAL_TYPES)
    front_feature = _pick(cfg.front_feature, FRONT_FEATURES)
    mount = _pick(cfg.mount, MOUNTS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    pole_count = int(cfg.pole_count) if cfg.pole_count is not None else 2
    pole_count = int(_clamp(pole_count, N_MIN, N_MAX))

    depth_scale = _clamp(cfg.body_depth_scale, 0.92, 1.10)
    height_scale = _clamp(cfg.body_height_scale, 0.92, 1.12)

    pole_spacing = _POLE_SPACING
    housing_width = pole_count * pole_spacing
    half_w = housing_width / 2.0
    body_depth = _BODY_DEPTH * depth_scale
    half_d = body_depth / 2.0
    body_height = _BODY_HEIGHT * height_scale
    half_h = body_height / 2.0
    front_face_y = -half_d
    pivot_y = front_face_y - _PIVOT_FRONT
    pivot_z = 0.0
    front_step = _STEP_PROUD if case_form == "stepped_case" else 0.0

    # Equation-derived spans (§7): everything that must co-vary with N.
    tie_len = housing_width + 0.006
    pivot_cyl_len = housing_width + 0.006

    throw = _clamp(cfg.handle_throw, 0.32, 0.46)

    return ResolvedCircuitBreakerConfig(
        case_form=case_form,
        handle_form=handle_form,
        terminal_type=terminal_type,
        front_feature=front_feature,
        mount=mount,
        pole_count=pole_count,
        palette_style=palette_style,
        pole_spacing=pole_spacing,
        housing_width=housing_width,
        half_w=half_w,
        body_depth=body_depth,
        half_d=half_d,
        body_height=body_height,
        half_h=half_h,
        front_face_y=front_face_y,
        pivot_y=pivot_y,
        pivot_z=pivot_z,
        front_step=front_step,
        tie_len=tie_len,
        pivot_cyl_len=pivot_cyl_len,
        throw=throw,
        name=cfg.name or "circuit_breaker",
    )


def with_overrides(config: CircuitBreakerConfig, **kwargs: object) -> CircuitBreakerConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CircuitBreakerConfig | ResolvedCircuitBreakerConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedCircuitBreakerConfig)
        else resolve_config(config)
    )
    return (
        ("case_form", r.case_form),
        ("handle_form", r.handle_form),
        ("terminal_type", r.terminal_type),
        ("front_feature", r.front_feature),
        ("mount", r.mount),
        ("pole_count", f"{r.pole_count}pole"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Housing builders
# ---------------------------------------------------------------------------
def _build_housing(model, r: ResolvedCircuitBreakerConfig, mats: dict):
    housing = model.part("housing")
    fy = r.front_face_y

    # --- Case shell (③A primary form family). ---
    if r.case_form == "rounded_case":
        # Keep ExtrudeGeometry + rounded_rect_profile (rule ③). Profile in XY,
        # extruded along Z, centered at origin.
        profile = rounded_rect_profile(r.housing_width, r.body_depth, _CORNER_R)
        shell = mesh_from_geometry(ExtrudeGeometry(profile, r.body_height), "body_shell")
        housing.visual(shell, origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["case"],
                       name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    else:  # box_case and stepped_case share the rectangular shell
        housing.visual(
            Box((r.housing_width, r.body_depth, r.body_height)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["case"],
            name="body_shell", material_class_id="plastic.opaque_glossy_molded",
        )

    # Terminal shoulders (top + bottom); proud for stepped_case.
    block_depth = _BLOCK_PROUD + r.front_step + 0.004
    block_cy = r.block_front_y + block_depth / 2.0
    for row, zc in (("top", r.half_h - 0.010), ("bottom", -r.half_h + 0.010)):
        housing.visual(
            Box((r.housing_width, block_depth, 0.020)),
            origin=Origin(xyz=(0.0, block_cy, zc)),
            material=mats["case"],
            name=f"{row}_terminal_block", material_class_id="plastic.opaque_glossy_molded",
        )

    # Flush front label panel spanning the mid height (features sit on it).
    panel_depth = 0.0015
    panel_cy = r.panel_front_y + panel_depth / 2.0
    housing.visual(
        Box((r.housing_width - 0.003, panel_depth, r.body_height - 0.028)),
        origin=Origin(xyz=(0.0, panel_cy, 0.0)),
        material=mats["case_accent"],
        name="front_label_panel", material_class_id="plastic.opaque_glossy_molded",
    )

    # Handle escutcheon (raised front hub the toggle sits in).
    shelf_cy = r.shelf_front_y + _SHELF_DEPTH / 2.0
    housing.visual(
        Box((r.housing_width, _SHELF_DEPTH, _SHELF_H)),
        origin=Origin(xyz=(0.0, shelf_cy, r.pivot_z)),
        material=mats["case"],
        name="handle_escutcheon", material_class_id="plastic.opaque_glossy_molded",
    )
    # ON / OFF slot walls (detents) at the window edges.
    for tag, zc in (("on", r.pivot_z + 0.013), ("off", r.pivot_z - 0.013)):
        housing.visual(
            Box((r.housing_width - 0.006, 0.003, 0.003)),
            origin=Origin(xyz=(0.0, r.shelf_front_y + 0.002, zc)),
            material=mats["case_accent"],
            name=f"detent_stop_{tag}", material_class_id="plastic.opaque_glossy_molded",
        )

    pole_x = r.pole_x
    # Inner pole separators (between adjacent poles).
    for i in range(r.pole_count - 1):
        sep_x = (pole_x[i] + pole_x[i + 1]) / 2.0
        housing.visual(
            Box((0.0030, _SHELF_DEPTH * 0.7, 0.026)),
            origin=Origin(xyz=(sep_x, r.shelf_front_y + 0.004, r.pivot_z)),
            material=mats["case_accent"],
            name=f"pole_separator_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Outer ribs at side walls.
    for i, x in enumerate((-(r.half_w - 0.001), r.half_w - 0.001)):
        housing.visual(
            Box((0.0022, 0.006, 0.050)),
            origin=Origin(xyz=(x, fy - 0.002, r.pivot_z)),
            material=mats["case_accent"],
            name=f"outer_rib_{i}", material_class_id="plastic.opaque_glossy_molded",
        )

    # Side pivot cheeks: small bosses at the side walls that the shaft ends seat
    # against (kept flush with the case, not proud axle stubs). The revolute
    # origin sits on the escutcheon front, well within the 15mm tolerance.
    for i, x in enumerate((-(r.half_w - 0.002), r.half_w - 0.002)):
        housing.visual(
            Box((0.004, 0.007, 0.014)),
            origin=Origin(xyz=(x, r.shelf_front_y + 0.003, r.pivot_z)),
            material=mats["case_accent"],
            name=f"pivot_cheek_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    # Side arc-chute vent (SlotPatternPanelGeometry, rule ③) embedded in -X face.
    vent_u = min(0.030, r.body_depth - 0.020)
    vent_v = min(0.044, r.body_height - 0.024)
    side_vent = SlotPatternPanelGeometry(
        (vent_u, vent_v),
        0.0022,
        slot_size=(min(0.017, vent_u * 0.55), 0.0032),
        pitch=(min(0.021, vent_u * 0.7), 0.008),
        frame=0.004,
        corner_radius=0.0015,
    )
    housing.visual(
        mesh_from_geometry(side_vent, "side_vent_panel"),
        origin=Origin(xyz=(-r.half_w + 0.0012, 0.0, 0.0), rpy=(0.0, -math.pi / 2.0, 0.0)),
        material=mats["vent"],
        name="side_vent_panel", material_class_id="plastic.patterned_textured",
    )
    # Side rating label plaque.
    housing.visual(
        Box((0.0018, min(0.030, r.body_depth - 0.024), min(0.050, r.body_height - 0.020))),
        origin=Origin(xyz=(-r.half_w + 0.0004, 0.010, 0.0)),
        material=mats["label"],
        name="side_rating_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    # Per-pole printed rating text on the front label panel (④ host-conformal).
    dy = r.panel_front_y + 0.0004
    for col, x in enumerate(pole_x):
        housing.visual(
            Box((0.012, 0.0016, 0.0034)),
            origin=Origin(xyz=(x, dy, r.pivot_z + 0.0225)),
            material=mats["handle_print"],
            name=f"brand_stripe_{col}", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        for k, (w, dz) in enumerate(
            ((0.011, 0.019), (0.009, 0.016), (0.010, -0.020), (0.008, -0.023))
        ):
            housing.visual(
                Box((w, 0.0018, 0.0011)),
                origin=Origin(xyz=(x, dy, r.pivot_z + dz)),
                material=mats["print"],
                name=f"rating_text_{col}_{k}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )

    return housing


def _apply_terminals(housing, r: ResolvedCircuitBreakerConfig, mats: dict):
    """④C terminal_type — per-pole, top + bottom rows (loop)."""
    pole_x = r.pole_x
    rows = (("top", r.z_top_row), ("bottom", r.z_bot_row))
    by = r.block_front_y  # terminal shoulder front

    if r.terminal_type == "screw_cavity":
        for row_name, z in rows:
            for col, x in enumerate(pole_x):
                housing.visual(
                    Cylinder(radius=0.0044, length=0.004),
                    origin=Origin(xyz=(x, by + 0.0016, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["dark"],
                    name=f"terminal_cavity_{row_name}_{col}", material_class_id="plastic.opaque_glossy_molded",
                )
                housing.visual(
                    Cylinder(radius=0.0029, length=0.005),
                    origin=Origin(xyz=(x, by + 0.0004, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["screw"],
                    name=f"terminal_screw_{row_name}_{col}", material_class_id="metal.stainless_matte",
                )
                housing.visual(
                    Box((0.0056, 0.0008, 0.0009)),
                    origin=Origin(
                        xyz=(x, by - 0.0018, z),
                        rpy=(0.0, 0.0, (0.55 if col % 2 else -0.55)),
                    ),
                    material=mats["label"],
                    name=f"terminal_slot_{row_name}_{col}", appearance_only=AppearanceOnlySpec(kind="overlay"),
                )
    elif r.terminal_type == "screw_wire_leads":
        for row_name, z in rows:
            up = 1.0 if row_name == "top" else -1.0
            for col, x in enumerate(pole_x):
                housing.visual(
                    Cylinder(radius=0.0055, length=0.004),
                    origin=Origin(xyz=(x, by + 0.0012, z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["terminal_metal"],
                    name=f"brass_terminal_{row_name}_{col}", material_class_id="metal.brass_polished",
                )
                housing.visual(
                    Box((0.012, 0.0018, 0.004)),
                    origin=Origin(xyz=(x, by - 0.0016, z)),
                    material=mats["dark"],
                    name=f"terminal_slot_{row_name}_{col}", material_class_id="plastic.opaque_glossy_molded",
                )
                # Wire jacket lead exiting the top/bottom face.
                housing.visual(
                    Cylinder(radius=0.0042, length=0.030),
                    origin=Origin(
                        xyz=(x, r.front_face_y + 0.010, up * (r.half_h + 0.014)),
                    ),
                    material=mats["wire_a"] if col % 2 == 0 else mats["wire_b"],
                    name=f"wire_jacket_{row_name}_{col}", material_class_id="rubber.smooth_plain",
                )
                housing.visual(
                    Cylinder(radius=0.0022, length=0.010),
                    origin=Origin(
                        xyz=(x, r.front_face_y + 0.010, up * (r.half_h + 0.001)),
                    ),
                    material=mats["copper"],
                    name=f"copper_core_{row_name}_{col}", material_class_id="metal.copper_bare",
                )
    else:  # plugin_stab
        for row_name, z in rows:
            up = 1.0 if row_name == "top" else -1.0
            for col, x in enumerate(pole_x):
                housing.visual(
                    Box((0.010, 0.004, 0.024)),
                    origin=Origin(
                        xyz=(x, r.front_face_y + 0.010, up * (r.half_h + 0.008)),
                    ),
                    material=mats["stab_metal"],
                    name=f"stab_blade_{row_name}_{col}", material_class_id="metal.stainless_matte",
                )


def _apply_front_feature(housing, r: ResolvedCircuitBreakerConfig, mats: dict):
    """④D front_feature."""
    pole_x = r.pole_x
    dy = r.panel_front_y + 0.0004

    if r.front_feature == "indicator_window":
        for col, x in enumerate(pole_x):
            housing.visual(
                Box((0.0055, 0.0016, 0.0055)),
                origin=Origin(xyz=(x, dy, r.pivot_z - 0.0225)),
                material=mats["case_accent"],
                name=f"indicator_bezel_{col}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                Box((0.0032, 0.0022, 0.0032)),
                origin=Origin(xyz=(x, dy + 0.0004, r.pivot_z - 0.0225)),
                material=mats["indicator"],
                name=f"indicator_window_{col}", material_class_id="plastic.frosted_translucent",
            )
    elif r.front_feature == "plain_label":
        # A wide engraved rating band, no window / no button.
        housing.visual(
            Box((r.housing_width - 0.006, 0.0018, 0.006)),
            origin=Origin(xyz=(0.0, dy, r.pivot_z - 0.0225)),
            material=mats["label"],
            name="plain_rating_band", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    else:  # rcbo_test_button
        bz = r.pivot_z - 0.0225
        housing.visual(
            Cylinder(radius=0.0048, length=0.0016),
            origin=Origin(xyz=(0.0, dy + 0.0002, bz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["test_bezel"],
            name="rcbo_test_bezel", material_class_id="plastic.opaque_glossy_molded",
        )
        housing.visual(
            Cylinder(radius=0.0036, length=0.0034),
            origin=Origin(xyz=(0.0, dy - 0.0016, bz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["test_button"],
            name="rcbo_test_button", material_class_id="plastic.opaque_glossy_molded",
        )
        housing.visual(
            Box((0.0060, 0.0016, 0.0013)),
            origin=Origin(xyz=(0.0, dy, bz + 0.0075)),
            material=mats["print"],
            name="rcbo_test_label", appearance_only=AppearanceOnlySpec(kind="decal"),
        )


def _apply_mount(housing, r: ResolvedCircuitBreakerConfig, mats: dict):
    """④E mount — rear-side hardware (away from the front handle)."""
    ry = r.half_d  # rear face y

    if r.mount == "din_clip":
        housing.visual(
            Box((r.housing_width, 0.004, 0.040)),
            origin=Origin(xyz=(0.0, ry + 0.002, r.pivot_z)),
            material=mats["din_metal"],
            name="din_clip_backplate", material_class_id="metal.steel_galvanized",
        )
        housing.visual(
            Box((r.housing_width - 0.004, 0.008, 0.006)),
            origin=Origin(xyz=(0.0, ry + 0.005, r.pivot_z + 0.019)),
            material=mats["din_metal"],
            name="din_upper_hook", material_class_id="metal.steel_galvanized",
        )
        housing.visual(
            Box((r.housing_width - 0.010, 0.008, 0.006)),
            origin=Origin(xyz=(0.0, ry + 0.005, r.pivot_z - 0.019)),
            material=mats["din_metal"],
            name="din_lower_latch", material_class_id="metal.steel_galvanized",
        )
        housing.visual(
            Box((0.014, 0.010, 0.010)),
            origin=Origin(xyz=(0.0, ry + 0.006, r.pivot_z - 0.026)),
            material=mats["case_accent"],
            name="din_latch_tab", material_class_id="plastic.opaque_glossy_molded",
        )
    else:  # surface_screw_base
        flange_w = r.housing_width + 0.020
        flange_h = r.body_height + 0.028
        housing.visual(
            Box((flange_w, 0.004, flange_h)),
            origin=Origin(xyz=(0.0, ry + 0.002, r.pivot_z)),
            material=mats["din_metal"],
            name="mounting_foot", material_class_id="metal.steel_galvanized",
        )
        hx = flange_w / 2.0 - 0.005
        hz = flange_h / 2.0 - 0.006
        for idx, (sx, sz) in enumerate(((-hx, hz), (hx, hz), (-hx, -hz), (hx, -hz))):
            housing.visual(
                Cylinder(radius=0.0055, length=0.002),
                origin=Origin(xyz=(sx, ry + 0.003, sz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["case_accent"],
                name=f"mount_recess_{idx}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                Cylinder(radius=0.0025, length=0.006),
                origin=Origin(xyz=(sx, ry + 0.002, sz), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["dark"],
                name=f"mount_hole_{idx}", material_class_id="plastic.opaque_glossy_molded",
            )


# ---------------------------------------------------------------------------
# Toggle builder (③B handle_form) — the single revolute part.
# ---------------------------------------------------------------------------
def _build_toggle(model, housing, r: ResolvedCircuitBreakerConfig, mats: dict):
    toggle = model.part("toggle")
    pole_x = r.pole_x

    # Shared pivot shaft (spans all poles); child-local origin = pivot line.
    toggle.visual(
        Cylinder(radius=_SHAFT_R, length=r.pivot_cyl_len),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["din_metal"],
        name="pivot_shaft", material_class_id="metal.steel_galvanized",
    )
    # Per-pole rotor drums + hubs + index ribs (ONE loop; A copy-pasted these).
    for col, x in enumerate(pole_x):
        toggle.visual(
            Cylinder(radius=_DRUM_R, length=0.0115),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["handle"],
            name=f"rotor_drum_{col}", material_class_id="plastic.opaque_glossy_molded",
        )
        toggle.visual(
            Cylinder(radius=0.0034, length=0.0122),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark"],
            name=f"rotor_hub_{col}", material_class_id="plastic.opaque_glossy_molded",
        )
        toggle.visual(
            Box((0.0122, 0.0018, 0.0018)),
            origin=Origin(xyz=(x, 0.0, _DRUM_R - 0.0009)),
            material=mats["handle_print"],
            name=f"rotor_index_rib_{col}", material_class_id="plastic.opaque_glossy_molded",
        )

    # Lower tie bar linking all poles (touches every drum; length ∝ N).
    toggle.visual(
        Box((r.tie_len, 0.008, 0.012)),
        origin=Origin(xyz=(0.0, -0.005, -0.005)),
        material=mats["handle"],
        name="common_tie_bar", material_class_id="plastic.opaque_glossy_molded",
    )

    # Handle form (③B). Grip sits FORWARD of the axis (|yc|>=0.008) — grip sweep
    # is 2*|yc|*sin(throw), so this clears the 4mm test even at min throw.
    if r.handle_form == "flag_toggle":
        for col, x in enumerate(pole_x):
            toggle.visual(
                Box((0.0105, 0.008, 0.021)),
                origin=Origin(xyz=(x, -0.008, 0.0085)),
                material=mats["handle"],
                name=f"flag_paddle_{col}", material_class_id="plastic.opaque_glossy_molded",
            )
            toggle.visual(
                Box((0.008, 0.0009, 0.002)),
                origin=Origin(xyz=(x, -0.0122, 0.014)),
                material=mats["handle_print"],
                name=f"paddle_off_print_{col}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
    elif r.handle_form == "thumb_rocker":
        toggle.visual(
            Box((r.tie_len - 0.004, 0.008, 0.006)),
            origin=Origin(xyz=(0.0, -0.007, -0.003)),
            material=mats["handle"],
            name="finger_ridge", material_class_id="plastic.opaque_glossy_molded",
        )
        for col, x in enumerate(pole_x):
            toggle.visual(
                Box((0.015, 0.009, 0.019)),
                origin=Origin(xyz=(x, -0.008, 0.0075)),
                material=mats["handle"],
                name=f"rocker_paddle_{col}", material_class_id="plastic.opaque_glossy_molded",
            )
            toggle.visual(
                Box((0.011, 0.0011, 0.0015)),
                origin=Origin(xyz=(x, -0.0128, 0.013)),
                material=mats["handle_print"],
                name=f"rocker_on_print_{col}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
    else:  # mccb_wide_handle — single ganged flipper, no per-pole paddle
        toggle.visual(
            Box((r.housing_width - 0.005, 0.009, 0.026)),
            origin=Origin(xyz=(0.0, -0.008, 0.008)),
            material=mats["handle"],
            name="mccb_flipper_body", material_class_id="plastic.opaque_glossy_molded",
        )
        for k, dz in enumerate((-0.002, 0.002, 0.006, 0.010, 0.014)):
            toggle.visual(
                Box((r.housing_width - 0.008, 0.0012, 0.0009)),
                origin=Origin(xyz=(0.0, -0.0128, dz)),
                material=mats["handle"],
                name=f"mccb_grip_rib_{k}", material_class_id="plastic.opaque_glossy_molded",
            )
        toggle.visual(
            Box((0.012, 0.0009, 0.002)),
            origin=Origin(xyz=(0.0, -0.0125, 0.017)),
            material=mats["handle_print"],
            name="mccb_on_print", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )

    # The single revolute joint. Axis = pole axis X; origin on the pivot line
    # (through the pivot_shaft; within tol of the escutcheon + pivot cheeks).
    model.articulation(
        "housing_to_toggle",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=toggle,
        origin=Origin(xyz=(0.0, r.pivot_y, r.pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=-r.throw, upper=r.throw),
    )
    return toggle


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_circuit_breaker(
    config: CircuitBreakerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Electrical_Wiring", "small_class": "Circuit breaker"},
    )
    mats = {
        key: model.material(f"cb_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    housing = _build_housing(model, r, mats)
    _apply_terminals(housing, r, mats)
    _apply_front_feature(housing, r, mats)
    _apply_mount(housing, r, mats)
    _build_toggle(model, housing, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_circuit_breaker(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_circuit_breaker(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_pivot_overlaps(ctx, housing, toggle, r: ResolvedCircuitBreakerConfig):
    """Captured-pivot overlaps: drums/shaft nest in the escutcheon + bearings."""
    for col in range(r.pole_count):
        ctx.allow_overlap(
            toggle, housing, elem_a=f"rotor_drum_{col}", elem_b="handle_escutcheon",
            reason="rotor drum back seats in the escutcheon bore (captured pivot).",
        )
        ctx.allow_overlap(
            toggle, housing, elem_a=f"rotor_hub_{col}", elem_b="handle_escutcheon",
            reason="rotor hub is concentric with the drum inside the bore (captured pivot).",
        )


def run_circuit_breaker_tests(
    object_model: ArticulatedObject,
    config: CircuitBreakerConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("housing")
    toggle = object_model.get_part("toggle")
    joint = object_model.get_articulation("housing_to_toggle")
    hvis = {v.name for v in housing.visuals}
    tvis = {v.name for v in toggle.visuals}

    _allow_pivot_overlaps(ctx, housing, toggle, r)
    # Stab blades / wire leads are intentionally embedded in the housing.
    if r.terminal_type == "plugin_stab":
        for row in ("top", "bottom"):
            for col in range(r.pole_count):
                ctx.allow_overlap(
                    housing, housing, elem_a="body_shell",
                    elem_b=f"stab_blade_{row}_{col}",
                    reason="flat stab blade is embedded in the housing for retention.",
                )

    # --- Identity / structure. ---
    ctx.check(
        "small class is Circuit breaker",
        object_model.meta.get("small_class") == "Circuit breaker",
        details=str(object_model.meta),
    )
    ctx.check(
        "single housing_to_toggle REVOLUTE about pole axis X",
        joint.articulation_type == ArticulationType.REVOLUTE
        and joint.parent == "housing"
        and joint.child == "toggle"
        and joint.motion_limits is not None
        and joint.motion_limits.lower is not None
        and joint.motion_limits.upper is not None
        and joint.motion_limits.lower < joint.motion_limits.upper,
        details=f"type={joint.articulation_type}, limits={joint.motion_limits}",
    )
    revolute_children = [
        j.child
        for j in object_model.articulations
        if j.articulation_type == ArticulationType.REVOLUTE
    ]
    ctx.check(
        "only the toggle is a revolute child",
        revolute_children == ["toggle"],
        details=str(revolute_children),
    )

    # --- Multiplicity: N drums on the shared shaft, tie-bar spans them. ---
    ctx.check(
        "pivot shaft + one rotor drum per pole are on the toggle",
        "pivot_shaft" in tvis
        and all(f"rotor_drum_{c}" in tvis for c in range(r.pole_count))
        and "common_tie_bar" in tvis,
        details=f"toggle visuals={sorted(tvis)}",
    )
    ctx.check(
        "tie bar length spans all poles",
        r.tie_len >= r.housing_width,
        details=f"tie_len={r.tie_len:.4f} housing_width={r.housing_width:.4f}",
    )

    # --- ③A rounded case keeps ExtrudeGeometry (no Box downgrade). ---
    ctx.check(
        "case shell present; side vent is a SlotPatternPanel mesh",
        "body_shell" in hvis and "side_vent_panel" in hvis,
        details=f"missing={ {'body_shell', 'side_vent_panel'} - hvis }",
    )

    # --- Slot-specific geometry present. ---
    handle_marker = {
        "flag_toggle": f"flag_paddle_{r.pole_count - 1}",
        "thumb_rocker": f"rocker_paddle_{r.pole_count - 1}",
        "mccb_wide_handle": "mccb_flipper_body",
    }[r.handle_form]
    ctx.check(
        f"handle form {r.handle_form} geometry present",
        handle_marker in tvis,
        details=f"want {handle_marker}; toggle={sorted(tvis)}",
    )
    if r.handle_form == "mccb_wide_handle":
        ctx.check(
            "mccb has no per-pole paddles",
            not any(n.startswith("flag_paddle_") or n.startswith("rocker_paddle_") for n in tvis),
            details=str(sorted(tvis)),
        )
    term_marker = {
        "screw_cavity": f"terminal_screw_top_{r.pole_count - 1}",
        "screw_wire_leads": f"wire_jacket_top_{r.pole_count - 1}",
        "plugin_stab": f"stab_blade_top_{r.pole_count - 1}",
    }[r.terminal_type]
    ctx.check(
        f"terminal type {r.terminal_type} geometry present",
        term_marker in hvis,
        details=f"want {term_marker}",
    )
    front_marker = {
        "indicator_window": f"indicator_window_{r.pole_count - 1}",
        "plain_label": "plain_rating_band",
        "rcbo_test_button": "rcbo_test_button",
    }[r.front_feature]
    ctx.check(
        f"front feature {r.front_feature} geometry present",
        front_marker in hvis,
        details=f"want {front_marker}",
    )
    mount_marker = "din_clip_backplate" if r.mount == "din_clip" else "mounting_foot"
    ctx.check(
        f"mount {r.mount} geometry present",
        mount_marker in hvis,
        details=f"want {mount_marker}",
    )

    # --- Handle protrudes proud of the fixed front case. ---
    ctx.expect_gap(
        housing,
        toggle,
        axis="y",
        min_gap=0.0005,
        positive_elem="body_shell",
        negative_elem="common_tie_bar",
        name="handle assembly sits proud of the molded front",
    )

    # --- Motion: handle rocks (rotor stays on axis, grip sweeps), through-travel
    #     collision proven by the sampled-pose gate below. ---
    lower = joint.motion_limits.lower
    upper = joint.motion_limits.upper
    grip_elem = {
        "flag_toggle": f"flag_paddle_{r.pole_count - 1}",
        "thumb_rocker": f"rocker_paddle_{r.pole_count - 1}",
        "mccb_wide_handle": "mccb_flipper_body",
    }[r.handle_form]
    drum_elem = f"rotor_drum_{r.pole_count - 1}"

    def _c(aabb):
        if aabb is None:
            return None
        lo, hi = aabb
        return ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2)

    drum_rest = _c(ctx.part_element_world_aabb(toggle, elem=drum_elem))
    base_pos = ctx.part_world_position(housing)
    with ctx.pose({joint: lower}):
        grip_down = _c(ctx.part_element_world_aabb(toggle, elem=grip_elem))
    with ctx.pose({joint: upper}):
        grip_up = _c(ctx.part_element_world_aabb(toggle, elem=grip_elem))
        drum_up = _c(ctx.part_element_world_aabb(toggle, elem=drum_elem))
        housing_pos = ctx.part_world_position(housing)
    ctx.check(
        "housing stays fixed while the toggle rotates",
        base_pos == housing_pos,
        details=f"rest={base_pos} posed={housing_pos}",
    )
    ctx.check(
        "grip sweeps up/down between OFF and ON",
        grip_down is not None
        and grip_up is not None
        and abs(grip_up[2] - grip_down[2]) > 0.004,
        details=f"down_z={None if grip_down is None else grip_down[2]:.4f} "
        f"up_z={None if grip_up is None else grip_up[2]:.4f}",
    )
    ctx.check(
        "rotor drum stays on the pivot axis while the grip sweeps",
        drum_rest is not None
        and drum_up is not None
        and math.hypot(drum_up[1] - drum_rest[1], drum_up[2] - drum_rest[2]) < 0.0025,
        details=f"drum_travel="
        f"{math.hypot(drum_up[1] - drum_rest[1], drum_up[2] - drum_rest[2]):.4f}"
        if (drum_rest and drum_up)
        else "n/a",
    )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices recorded with all axes",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # --- Rule 5: no through-travel 穿模 across the whole handle swing. ---
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=64,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = (
    "CircuitBreakerConfig",
    "ResolvedCircuitBreakerConfig",
    "build_circuit_breaker",
    "build_seeded_circuit_breaker",
    "config_from_seed",
    "resolve_config",
    "run_circuit_breaker_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
