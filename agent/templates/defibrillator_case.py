# SPDX-License-Identifier: Apache-2.0

"""Defibrillator case — modular procedural template (AED protective enclosure).

Category identity: a dedicated protective case/enclosure holding ONE AED /
defibrillator, opened by a real hinged door/lid (or prismatic shutter) to
retrieve the device. Two structural spines (families), selected by ``body_form``:

  * CABINET family (origin2 ``rec_...ef2187``): a cadquery hollow sheet-metal
    box ``cabinet`` (ROOT) carrying an opening mechanism (side-hinged door /
    bottom drop-flap / top clear flip-up cover / roll-up shutter), a removable
    AED module (prismatic slide-out / revolute swing-out / fixed cradle), a
    door handle or rotary knob latch, an optional roof-top alarm beacon, and a
    right-wall louver of N ventilation slats (multiplicity).
  * CARRYCASE family (origin1 ``rec_...4aa24``): a ``case_base`` ROOT (molded
    soft tray / rigid hard shell / tall shoulder pouch) with a hinged lid
    (side clamshell / fold-over top flap), a FIXED interior AED, and a velcro
    strap flap or over-center snap latches.

Every seed keeps a real non-FIXED opening joint (revolute door/lid/flap or
prismatic shutter). Family-conditional slot sampling gates illegal spine mixes.
``palette_style`` (6 colorways) recolors every ``.visual`` and is not a slot.

Sources (all 14 5-star read): origins ``ef2187`` (cabinet) + ``4aa24`` (carry
case); forks pole_mount / outdoor_cabinet / hardshell_case / shoulder_pouch
(body_form), dropdown_flap / clear_flip_cover / roll_shutter (opening),
rotary_latch (latch), swingout_bracket (aed), alarm_strobe (beacon),
vent_dense / vent_sparse (multiplicity range).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/defibrillator_case.md``
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot domains
# --------------------------------------------------------------------------- #
BodyForm = Literal[
    "wall_cabinet_box",
    "pole_mount_enclosure",
    "outdoor_weatherproof_cabinet",
    "molded_soft_carry_case",
    "rigid_hard_shell_case",
    "soft_shoulder_bag_pouch",
]
OpeningMechanism = Literal[
    "front_hinged_door",
    "drop_down_flap",
    "clear_flip_up_cover",
    "roll_up_shutter",
    "clamshell_side_lid",
    "foldover_top_flap",
]
AedRetention = Literal[
    "prismatic_slideout_shelf",
    "swing_out_revolute_bracket",
    "fixed_cradle",
]
LatchStyle = Literal[
    "pull_handle",
    "rotary_knob_latch",
    "velcro_strap_flap",
    "snap_latch",
]
PaletteStyle = Literal[
    "white_powdercoat",
    "safety_yellow",
    "emergency_green",
    "charcoal_orange",
    "red_black_ems",
    "medical_blue",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "wall_cabinet_box",
    "pole_mount_enclosure",
    "outdoor_weatherproof_cabinet",
    "molded_soft_carry_case",
    "rigid_hard_shell_case",
    "soft_shoulder_bag_pouch",
)
_CABINET_FORMS = frozenset(
    {"wall_cabinet_box", "pole_mount_enclosure", "outdoor_weatherproof_cabinet"}
)
CABINET_OPENINGS: tuple[OpeningMechanism, ...] = (
    "front_hinged_door",
    "drop_down_flap",
    "clear_flip_up_cover",
    "roll_up_shutter",
)
CARRYCASE_OPENINGS: tuple[OpeningMechanism, ...] = (
    "clamshell_side_lid",
    "foldover_top_flap",
)
CABINET_AED: tuple[AedRetention, ...] = (
    "prismatic_slideout_shelf",
    "swing_out_revolute_bracket",
    "fixed_cradle",
)
CABINET_LATCH: tuple[LatchStyle, ...] = ("pull_handle", "rotary_knob_latch")
CARRYCASE_LATCH: tuple[LatchStyle, ...] = ("velcro_strap_flap", "snap_latch")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_powdercoat",
    "safety_yellow",
    "emergency_green",
    "charcoal_orange",
    "red_black_ems",
    "medical_blue",
)

# vent_count weighted sampling (small N favored; spec Multiplicity table).
_VENT_COUNTS: tuple[int, ...] = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
_VENT_WEIGHTS: tuple[float, ...] = (0.14, 0.16, 0.20, 0.16, 0.12, 0.08, 0.06, 0.04, 0.02, 0.02)


def _family_of(body_form: str) -> str:
    return "cabinet" if body_form in _CABINET_FORMS else "carrycase"


# --------------------------------------------------------------------------- #
# Palettes. body / body2 / accent / latch vary per colorway; the semantic
# tokens (aed device yellow, green/red/white medical signage, smoky window,
# amber beacon lens, green status LED, dark interior/foam) stay anchored to the
# 5-star RGBA so the object always reads as an AED enclosure. palette-only.
# --------------------------------------------------------------------------- #
_SEMANTIC = {
    "aed": (0.96, 0.72, 0.14, 1.0),
    "aed_dark": (0.03, 0.07, 0.15, 1.0),
    "green": (0.16, 0.68, 0.38, 1.0),
    "green_dark": (0.08, 0.50, 0.31, 1.0),
    "red": (0.75, 0.07, 0.04, 1.0),
    "white": (0.96, 0.98, 0.95, 1.0),
    "window": (0.55, 0.72, 0.82, 0.32),
    "clear": (0.72, 0.85, 0.90, 0.28),
    "interior": (0.025, 0.026, 0.028, 1.0),
    "foam": (0.035, 0.038, 0.042, 1.0),
    "beacon": (0.06, 0.06, 0.07, 1.0),
    "lens": (0.92, 0.38, 0.05, 0.55),
    "led": (0.10, 0.78, 0.22, 1.0),
}
_PALETTE_VARY: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_powdercoat": {
        "body": (0.88, 0.88, 0.84, 1.0),
        "body2": (0.80, 0.81, 0.80, 1.0),
        "accent": (0.05, 0.05, 0.05, 1.0),
        "latch": (0.62, 0.64, 0.62, 1.0),
    },
    "safety_yellow": {
        "body": (0.95, 0.78, 0.10, 1.0),
        "body2": (0.80, 0.66, 0.08, 1.0),
        "accent": (0.05, 0.05, 0.05, 1.0),
        "latch": (0.52, 0.54, 0.50, 1.0),
    },
    "emergency_green": {
        "body": (0.12, 0.42, 0.22, 1.0),
        "body2": (0.08, 0.30, 0.16, 1.0),
        "accent": (0.02, 0.02, 0.02, 1.0),
        "latch": (0.62, 0.64, 0.62, 1.0),
    },
    "charcoal_orange": {
        "body": (0.18, 0.19, 0.20, 1.0),
        "body2": (0.14, 0.15, 0.16, 1.0),
        "accent": (0.05, 0.05, 0.05, 1.0),
        "latch": (1.0, 0.42, 0.0, 1.0),
    },
    "red_black_ems": {
        "body": (0.82, 0.035, 0.045, 1.0),
        "body2": (0.015, 0.014, 0.016, 1.0),
        "accent": (0.015, 0.014, 0.016, 1.0),
        "latch": (0.05, 0.05, 0.06, 1.0),
    },
    "medical_blue": {
        "body": (0.20, 0.34, 0.55, 1.0),
        "body2": (0.12, 0.20, 0.38, 1.0),
        "accent": (0.05, 0.05, 0.06, 1.0),
        "latch": (0.62, 0.64, 0.62, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DefibrillatorCaseConfig:
    body_form: BodyForm = "wall_cabinet_box"
    opening_mechanism: OpeningMechanism = "front_hinged_door"
    aed_retention: AedRetention = "prismatic_slideout_shelf"
    latch_style: LatchStyle = "pull_handle"
    vent_count: int = 5
    alarm_beacon: bool = False
    palette_style: PaletteStyle = "white_powdercoat"
    body_scale: float = 1.0
    door_open_limit: float = 1.75
    aed_slide_travel: float = 0.22
    name: str = "defibrillator_case"


@dataclass(frozen=True)
class ResolvedDefibrillatorCaseConfig:
    body_form: BodyForm
    family: str
    opening_mechanism: OpeningMechanism
    aed_retention: AedRetention
    latch_style: LatchStyle
    vent_count: int
    alarm_beacon: bool
    palette_style: PaletteStyle
    body_scale: float
    door_open_limit: float
    aed_slide_travel: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


def config_from_seed(seed: int) -> DefibrillatorCaseConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    family = _family_of(body_form)

    if family == "cabinet":
        opening = rng.choice(CABINET_OPENINGS)
        aed = rng.choice(CABINET_AED)
        latch = rng.choice(CABINET_LATCH)
        # Coupling: a roll-up shutter has no flat door face to carry a
        # face-normal rotary knob -> its latch is the bottom lift bar (handle).
        if opening in ("roll_up_shutter", "clear_flip_up_cover"):
            latch = "pull_handle"
        vent_count = rng.choices(_VENT_COUNTS, weights=_VENT_WEIGHTS, k=1)[0]
        alarm_beacon = rng.random() < 0.35
    else:
        opening = rng.choice(CARRYCASE_OPENINGS)
        aed = "fixed_cradle"  # soft/rigid cases hold the AED fixed in foam
        latch = rng.choice(CARRYCASE_LATCH)
        vent_count = 0
        alarm_beacon = False

    return DefibrillatorCaseConfig(
        body_form=body_form,
        opening_mechanism=opening,
        aed_retention=aed,
        latch_style=latch,
        vent_count=vent_count,
        alarm_beacon=alarm_beacon,
        palette_style=rng.choice(PALETTE_STYLES),
        body_scale=round(rng.uniform(0.90, 1.12), 4),
        door_open_limit=round(rng.uniform(1.35, 1.75), 4),
        aed_slide_travel=round(rng.uniform(0.16, 0.24), 4),
        name=f"seeded_defibrillator_case_{seed}",
    )


def resolve_config(
    config: DefibrillatorCaseConfig | None = None,
) -> ResolvedDefibrillatorCaseConfig:
    cfg = config or DefibrillatorCaseConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    family = _family_of(body_form)

    if family == "cabinet":
        opening = _pick(cfg.opening_mechanism, CABINET_OPENINGS)
        aed = _pick(cfg.aed_retention, CABINET_AED)
        latch = _pick(cfg.latch_style, CABINET_LATCH)
        if opening in ("roll_up_shutter", "clear_flip_up_cover"):
            latch = "pull_handle"
        vent_count = int(_clamp(cfg.vent_count, 3, 12))
        alarm_beacon = bool(cfg.alarm_beacon)
    else:
        opening = _pick(cfg.opening_mechanism, CARRYCASE_OPENINGS)
        aed = "fixed_cradle"
        latch = _pick(cfg.latch_style, CARRYCASE_LATCH)
        vent_count = 0
        alarm_beacon = False

    return ResolvedDefibrillatorCaseConfig(
        body_form=body_form,
        family=family,
        opening_mechanism=opening,
        aed_retention=aed,
        latch_style=latch,
        vent_count=vent_count,
        alarm_beacon=alarm_beacon,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        body_scale=_clamp(cfg.body_scale, 0.90, 1.12),
        door_open_limit=_clamp(cfg.door_open_limit, 1.35, 1.75),
        aed_slide_travel=_clamp(cfg.aed_slide_travel, 0.16, 0.24),
        name=cfg.name or "defibrillator_case",
    )


def slot_choices_for_config(r: ResolvedDefibrillatorCaseConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("body_form", r.body_form),
        ("opening_mechanism", r.opening_mechanism),
        ("aed_retention", r.aed_retention),
        ("latch_style", r.latch_style),
        ("vent_count", f"vent_{r.vent_count}"),
        ("alarm_beacon", "on" if r.alarm_beacon else "off"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Materials
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, style: str) -> dict:
    vary = _PALETTE_VARY[style]
    mats: dict = {}
    for key, rgba in vary.items():
        mats[key] = model.material(f"dc_{style}_{key}", rgba=rgba)
    for key, rgba in _SEMANTIC.items():
        mats[key] = model.material(f"dc_{key}", rgba=rgba)
    return mats


# --------------------------------------------------------------------------- #
# Cadquery geometry helpers (hero surfaces stay mesh-typed per Rule 3)
# --------------------------------------------------------------------------- #
_TOL = 0.0012


def _cabinet_shell_cq(w: float, h: float, d: float, wall: float) -> cq.Workplane:
    """Open-front hollow sheet-metal box (origin2 ``_cabinet_shell`` L28-50)."""
    shell = cq.Workplane("XY").box(w, d, h)
    cut_depth = d - wall + 0.040
    cut_cy = (wall + 0.040) / 2.0
    cavity = (
        cq.Workplane("XY")
        .box(w - 2.0 * wall, cut_depth, h - 2.0 * wall)
        .translate((0.0, cut_cy, 0.0))
    )
    return shell.cut(cavity)


def _door_frame_cq(door_w: float, door_h: float, door_t: float) -> cq.Workplane:
    """Flat door slab centered at origin with an upper viewing window cut
    (origin2 ``_door_frame`` L53-63)."""
    door = cq.Workplane("XY").box(door_w, door_t, door_h)
    win_w = min(door_w * 0.66, door_w - 0.05)
    win_h = door_h * 0.33
    win_cz = door_h * 0.17
    window = (
        cq.Workplane("XY").box(win_w, door_t * 3.0, win_h).translate((0.0, 0.0, win_cz))
    )
    return door.cut(window)


def _clear_cover_cq(cover_w: float, cover_h: float, t: float = 0.005, dome: float = 0.010) -> cq.Workplane:
    """Shallow-domed clear polycarbonate flip-up cover (clear_flip_cover
    ``_clear_cover`` L62-84). Cross-section extruded along X, centered."""
    cs = (
        cq.Workplane("YZ")
        .moveTo(0.0, -cover_h / 2.0)
        .lineTo(0.0, cover_h / 2.0)
        .lineTo(t, cover_h / 2.0)
        .threePointArc((t + dome, 0.0), (t, -cover_h / 2.0))
        .close()
    )
    return cs.extrude(cover_w).translate((-cover_w / 2.0, 0.0, 0.0))


def _shutter_slat_cq(slat_w: float, slat_t: float, slat_h: float) -> cq.Workplane:
    """Single roller-shutter slat (roll_shutter ``_shutter_slat_geometry`` L60-67)."""
    return cq.Workplane("XY").box(slat_w, slat_t, slat_h).edges("|X").fillet(0.002)


def _aed_case_cq(s: float) -> cq.Workplane:
    """Rounded removable AED device case (origin2 ``_aed_case`` L66-70)."""
    case = cq.Workplane("XY").box(0.292 * s, 0.064, 0.230 * s).edges("|Y").fillet(0.026)
    return case.translate((0.0, 0.0, 0.005))


def _hard_lower_shell_cq(w: float, d: float, h: float, wall: float, r: float) -> cq.Workplane:
    """Rigid clamshell lower tray (hardshell ``_build_lower_shell`` L87-110)."""
    outer = cq.Workplane("XY").box(w, d, h, centered=(True, True, False)).edges("|Z").fillet(r)
    iw, idd, ih = w - 2 * wall, d - 2 * wall, h - wall
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=wall)
        .box(iw, idd, ih, centered=(True, True, False))
        .edges("|Z")
        .fillet(max(0.002, r - wall))
    )
    return outer.cut(cavity)


def _rounded_plate(width: float, depth: float, thickness: float, radius: float, name: str):
    """ExtrudeGeometry rounded plate (origin1 ``_rounded_plate`` L26-34)."""
    return mesh_from_geometry(
        ExtrudeGeometry(
            rounded_rect_profile(width, depth, radius, corner_segments=10),
            thickness,
            center=True,
        ),
        name,
    )


# --------------------------------------------------------------------------- #
# Cabinet family
# --------------------------------------------------------------------------- #
_WALL = 0.018
_DOOR_T = 0.018


def _cab_dims(r: ResolvedDefibrillatorCaseConfig) -> tuple[float, float, float]:
    s = r.body_scale
    return (0.46 * s, 0.58 * s, 0.16 * s)


def _apply_door_face(door, r, mats, face_cx: float, front_y: float, door_w: float, door_h: float) -> None:
    """Host-conformal medical signage on the door front face (positions derive
    from door_w/door_h so they hug the panel across ③/⑤). origin2 L133-171."""
    door.visual(
        Box((door_w * 0.70, 0.005, door_h * 0.045)),
        origin=Origin(xyz=(face_cx, front_y, door_h / 2.0 - 0.026)),
        material=mats["red"],
        name="red_title_mark", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    door.visual(
        Box((door_w * 0.30, 0.006, door_h * 0.22)),
        origin=Origin(xyz=(face_cx, front_y, -door_h / 2.0 + 0.115)),
        material=mats["green"],
        name="green_label_panel", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    door.visual(
        Box((0.012, 0.007, 0.046)),
        origin=Origin(xyz=(face_cx + door_w * 0.11, front_y, -door_h / 2.0 + 0.150)),
        material=mats["white"],
        name="white_cross_stem", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    door.visual(
        Box((0.046, 0.008, 0.012)),
        origin=Origin(xyz=(face_cx + door_w * 0.11, front_y, -door_h / 2.0 + 0.150)),
        material=mats["white"],
        name="white_cross_bar", appearance_only=AppearanceOnlySpec(kind="decal"),
    )


def _build_cabinet_root(model, r, mats):
    w, h, d = _cab_dims(r)
    cabinet = model.part("cabinet")
    cabinet.visual(
        mesh_from_cadquery(_cabinet_shell_cq(w, h, d, _WALL), "shell", tolerance=_TOL),
        material=mats["body"],
        name="shell", material_class_id="metal.paint_coated",
    )
    cabinet.visual(
        Box((w - 2 * _WALL - 0.010, 0.004, h * 0.57)),
        origin=Origin(xyz=(0.0, -d / 2.0 + _WALL + 0.002, 0.030)),
        material=mats["interior"],
        name="dark_back_panel", material_class_id="metal.paint_coated",
    )
    cabinet.visual(
        Box((w * 0.74, d * 0.79, 0.012)),
        origin=Origin(xyz=(0.0, -0.012, -h * 0.215)),
        material=mats["body2"],
        name="aed_shelf", material_class_id="metal.paint_coated",
    )
    # right-wall louver of N ventilation slats (multiplicity axis).
    n = r.vent_count
    if n > 0:
        z0 = -0.030 * (n - 1) / 2.0 + 0.135
        for i in range(n):
            vz = z0 - i * 0.030 + (n - 1) * 0.030 - 0.030 * i * 0.0
            vz = 0.135 - (n - 1) * 0.015 + i * 0.030
            cabinet.visual(
                Box((0.006, 0.040, 0.012)),
                origin=Origin(xyz=(w / 2.0, 0.030, vz)),
                material=mats["accent"],
                name=f"side_vent_{i}", material_class_id="metal.paint_coated",
            )

    # ③ form-family extras.
    if r.body_form == "pole_mount_enclosure":
        pole_r = 0.038
        pole_cy = -(d / 2.0 + 0.065 + pole_r)
        cabinet.visual(
            Cylinder(radius=pole_r, length=h * 0.95),
            origin=Origin(xyz=(0.0, pole_cy, 0.0)),
            material=mats["latch"],
            name="mounting_pole", material_class_id="metal.steel_galvanized",
        )
        for k, zc in enumerate((0.155, -0.155)):
            cabinet.visual(
                Cylinder(radius=pole_r + 0.012, length=0.048),
                origin=Origin(xyz=(0.0, pole_cy, zc), rpy=(0.0, 0.0, 0.0)),
                material=mats["body2"],
                name=f"pole_collar_{k}", material_class_id="metal.paint_coated",
            )
            cabinet.visual(
                Box((0.100, 0.065 + pole_r, 0.024)),
                origin=Origin(xyz=(0.0, pole_cy / 2.0 - d / 4.0, zc)),
                material=mats["body2"],
                name=f"pole_arm_{k}", material_class_id="metal.paint_coated",
            )
    elif r.body_form == "outdoor_weatherproof_cabinet":
        roof_w = w + 0.040
        roof_d = d + 0.047
        cabinet.visual(
            Box((roof_w, roof_d, 0.014)),
            origin=Origin(xyz=(0.0, 0.006, h / 2.0 + 0.010), rpy=(-0.14, 0.0, 0.0)),
            material=mats["body2"],
            name="roof_cap", material_class_id="metal.paint_coated",
        )
        cabinet.visual(
            Box((roof_w, 0.004, 0.016)),
            origin=Origin(xyz=(0.0, roof_d / 2.0 - 0.002 + 0.006, h / 2.0 - 0.004)),
            material=mats["body2"],
            name="roof_drip", material_class_id="metal.paint_coated",
        )
        if n > 0:
            for i in range(n):
                vz = 0.135 - (n - 1) * 0.015 + i * 0.030
                cabinet.visual(
                    Box((0.012, 0.038, 0.003)),
                    origin=Origin(xyz=(w / 2.0 + 0.006, 0.030, vz + 0.005)),
                    material=mats["body"],
                    name=f"vent_hood_{i}", material_class_id="metal.paint_coated",
                )

    cabinet.inertial = Inertial.from_geometry(
        Box((w, d, h)), mass=9.0, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    return cabinet


def _build_cabinet_aed_module(part, r, mats):
    s = r.body_scale
    part.visual(
        mesh_from_cadquery(_aed_case_cq(s), "removable_aed_case", tolerance=_TOL),
        material=mats["aed"],
        name="yellow_case", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Box((0.245 * s, 0.050, 0.010)),
        origin=Origin(xyz=(0.0, 0.0, -0.114 * s)),
        material=mats["aed"],
        name="module_skid", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        Cylinder(radius=0.055, length=0.006),
        origin=Origin(xyz=(0.0, 0.033, 0.010), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["aed_dark"],
        name="front_round_display", material_class_id="tech.control_interface",
    )
    part.visual(
        Box((0.105 * s, 0.010, 0.018)),
        origin=Origin(xyz=(0.0, 0.031, 0.108 * s)),
        material=mats["aed"],
        name="top_carry_grip", material_class_id="plastic.opaque_glossy_molded",
    )
    part.inertial = Inertial.from_geometry(
        Box((0.292 * s, 0.064, 0.230 * s)), mass=1.6, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )


def _build_cabinet_opening(model, cabinet, r, mats):
    w, h, d = _cab_dims(r)
    door_w = w - 0.030
    door_h = h - 0.035
    front_y = _DOOR_T / 2.0 - 0.001
    cab_front = d / 2.0

    if r.opening_mechanism == "front_hinged_door":
        door = model.part("door")
        door.visual(
            mesh_from_cadquery(_door_frame_cq(door_w, door_h, _DOOR_T), "door_shell", tolerance=_TOL),
            origin=Origin(xyz=(door_w / 2.0, 0.0, 0.0)),
            material=mats["body"],
            name="door_shell", material_class_id="metal.paint_coated",
        )
        door.visual(
            Box((door_w * 0.66 + 0.020, 0.008, door_h * 0.33 + 0.020)),
            origin=Origin(xyz=(door_w / 2.0, 0.0, door_h * 0.17)),
            material=mats["window"],
            name="window_pane", material_class_id="glass.clear_transparent",
        )
        _apply_door_face(door, r, mats, door_w / 2.0, front_y, door_w, door_h)
        door.inertial = Inertial.from_geometry(
            Box((door_w, _DOOR_T, door_h)), mass=3.0, origin=Origin(xyz=(door_w / 2.0, 0.0, 0.0))
        )
        model.articulation(
            "cabinet_to_door",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=door,
            origin=Origin(xyz=(-door_w / 2.0, cab_front + _DOOR_T / 2.0 - 0.001, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=r.door_open_limit),
        )
        return door, "cabinet_to_door", door_w / 2.0, 0.0

    if r.opening_mechanism == "drop_down_flap":
        door = model.part("door")
        door.visual(
            mesh_from_cadquery(_door_frame_cq(door_w, door_h, _DOOR_T), "door_shell", tolerance=_TOL),
            origin=Origin(xyz=(0.0, 0.0, door_h / 2.0)),
            material=mats["body"],
            name="door_shell", material_class_id="metal.paint_coated",
        )
        door.visual(
            Box((door_w * 0.66 + 0.020, 0.008, door_h * 0.33 + 0.020)),
            origin=Origin(xyz=(0.0, 0.0, door_h / 2.0 + door_h * 0.17)),
            material=mats["window"],
            name="window_pane", material_class_id="glass.clear_transparent",
        )
        _apply_door_face(door, r, mats, 0.0, front_y, door_w, door_h)
        for v in list(door.visuals):
            if v.name in ("red_title_mark", "green_label_panel", "white_cross_stem", "white_cross_bar"):
                x, y, z = v.origin.xyz
                v.origin = Origin(xyz=(x, y, z + door_h / 2.0), rpy=v.origin.rpy)
        door.inertial = Inertial.from_geometry(
            Box((door_w, _DOOR_T, door_h)), mass=3.0, origin=Origin(xyz=(0.0, 0.0, door_h / 2.0))
        )
        model.articulation(
            "cabinet_to_door",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=door,
            origin=Origin(xyz=(0.0, cab_front + _DOOR_T / 2.0 - 0.001, -door_h / 2.0)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=min(r.door_open_limit, 1.60)),
        )
        return door, "cabinet_to_door", 0.0, door_h / 2.0

    if r.opening_mechanism == "clear_flip_up_cover":
        cover_w = w - 0.030
        cover_h = h - 0.035
        door = model.part("door")
        door.visual(
            mesh_from_cadquery(_clear_cover_cq(cover_w, cover_h), "door_shell", tolerance=_TOL),
            origin=Origin(xyz=(0.0, 0.0, -cover_h / 2.0)),
            material=mats["clear"],
            name="door_shell", material_class_id="plastic.clear_rigid",
        )
        # interior signage on the cabinet back panel (visible through the cover).
        cabinet.visual(
            Box((w * 0.30, 0.005, h * 0.20)),
            origin=Origin(xyz=(0.0, -d / 2.0 + _WALL + 0.006, 0.020)),
            material=mats["green"],
            name="interior_green_label", appearance_only=AppearanceOnlySpec(kind="decal"),
        )
        cabinet.visual(
            Box((w * 0.55, 0.004, 0.026)),
            origin=Origin(xyz=(0.0, -d / 2.0 + _WALL + 0.006, 0.150)),
            material=mats["red"],
            name="interior_red_header", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        door.inertial = Inertial.from_geometry(
            Box((cover_w, 0.020, cover_h)), mass=1.6, origin=Origin(xyz=(0.0, 0.0, -cover_h / 2.0))
        )
        model.articulation(
            "cabinet_to_door",
            ArticulationType.REVOLUTE,
            parent=cabinet,
            child=door,
            origin=Origin(xyz=(0.0, cab_front - 0.001, h / 2.0 - _WALL / 2.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=min(r.door_open_limit, 1.55)),
        )
        return door, "cabinet_to_door", 0.0, -cover_h / 2.0

    # roll_up_shutter
    slat_t = 0.012
    slat_w = w - 0.036
    slat_h = 0.074
    gap = 0.004
    pitch = slat_h + gap
    open_h = h - 0.060
    n_slats = max(6, int(open_h / pitch))
    total_h = n_slats * slat_h + (n_slats - 1) * gap
    travel = _clamp((n_slats - 4) * pitch, pitch, total_h - pitch)

    # guide rails + roller housing are fixed cabinet visuals.
    rail_x = slat_w / 2.0 + 0.008
    for k, sx in enumerate((-rail_x, rail_x)):
        cabinet.visual(
            Box((0.014, 0.024, h - 0.020)),
            origin=Origin(xyz=(sx, cab_front + 0.002, 0.0)),
            material=mats["latch"],
            name=f"guide_rail_{k}", material_class_id="metal.stainless_matte",
        )
    cabinet.visual(
        Box((slat_w + 0.030, 0.048, 0.032)),
        origin=Origin(xyz=(0.0, cab_front - 0.008, h / 2.0 - 0.004)),
        material=mats["body"],
        name="roller_housing", material_class_id="metal.paint_coated",
    )

    shutter = model.part("shutter")
    slat_mesh = mesh_from_cadquery(_shutter_slat_cq(slat_w, slat_t, slat_h), "shutter_slat", tolerance=_TOL)
    bottom_z = -total_h / 2.0 + slat_h / 2.0
    for i in range(n_slats):
        shutter.visual(
            slat_mesh,
            origin=Origin(xyz=(0.0, 0.0, bottom_z + i * pitch)),
            material=mats["body"],
            name=f"shutter_slat_{i}", material_class_id="metal.paint_coated",
        )
    ch_x = slat_w / 2.0 - 0.009
    for k, sx in enumerate((-ch_x, ch_x)):
        shutter.visual(
            Box((0.014, slat_t, total_h + 0.004)),
            origin=Origin(xyz=(sx, 0.0, 0.0)),
            material=mats["latch"],
            name=f"endlock_{k}", material_class_id="metal.stainless_matte",
        )
    # signage seated into upper slats.
    shutter.visual(
        Box((slat_w * 0.66, 0.005, slat_h * 1.4)),
        origin=Origin(xyz=(0.0, slat_t / 2.0 - 0.001, bottom_z + (n_slats - 3) * pitch)),
        material=mats["window"],
        name="window_pane", material_class_id="glass.clear_transparent",
    )
    shutter.visual(
        Box((slat_w * 0.30, 0.005, slat_h)),
        origin=Origin(xyz=(0.0, slat_t / 2.0 - 0.001, bottom_z + 2 * pitch)),
        material=mats["green"],
        name="green_label_panel", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    shutter.visual(
        Box((0.100, 0.022, 0.016)),
        origin=Origin(xyz=(0.0, slat_t / 2.0 + 0.006, bottom_z)),
        material=mats["latch"],
        name="pull_handle", material_class_id="metal.stainless_matte",
    )
    shutter.inertial = Inertial.from_geometry(
        Box((slat_w, slat_t, total_h)), mass=4.0, origin=Origin(xyz=(0.0, 0.0, 0.0))
    )
    model.articulation(
        "cabinet_to_shutter",
        ArticulationType.PRISMATIC,
        parent=cabinet,
        child=shutter,
        origin=Origin(xyz=(0.0, cab_front + slat_t / 2.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=travel),
    )
    return shutter, "cabinet_to_shutter", 0.0, 0.0


def _build_cabinet_latch(model, cabinet, panel, r, mats, face_cx: float, face_cz: float):
    w, h, d = _cab_dims(r)
    door_w = w - 0.030
    door_h = h - 0.035
    front_y = _DOOR_T / 2.0 - 0.001

    if r.opening_mechanism == "roll_up_shutter":
        # the shutter's lift bar is built by the shutter factory (needs bottom_z).
        return None

    if r.latch_style == "pull_handle":
        panel.visual(
            Box((0.018, 0.020, door_h * 0.24)),
            origin=Origin(xyz=(face_cx + door_w / 2.0 - 0.057, front_y + 0.022, face_cz - 0.065)),
            material=mats["latch"],
            name="pull_handle", material_class_id="metal.stainless_matte",
        )
        panel.visual(
            Box((0.020, 0.030, 0.020)),
            origin=Origin(xyz=(face_cx + door_w / 2.0 - 0.057, front_y + 0.009, face_cz + door_h * 0.10)),
            material=mats["latch"],
            name="handle_upper_post", material_class_id="metal.stainless_matte",
        )
        panel.visual(
            Box((0.020, 0.030, 0.020)),
            origin=Origin(xyz=(face_cx + door_w / 2.0 - 0.057, front_y + 0.009, face_cz - door_h * 0.20)),
            material=mats["latch"],
            name="handle_lower_post", material_class_id="metal.stainless_matte",
        )
        return None

    # rotary_knob_latch: T-handle cam latch, REVOLUTE about the door face normal.
    knob_x = face_cx + door_w / 2.0 - 0.057
    panel.visual(
        Cylinder(radius=0.013, length=0.006),
        origin=Origin(xyz=(knob_x, front_y, face_cz - 0.065), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["latch"],
        name="knob_boss", material_class_id="metal.stainless_matte",
    )
    latch_knob = model.part("latch_knob")
    latch_knob.visual(
        Cylinder(radius=0.021, length=0.007),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["latch"],
        name="knob_plate", material_class_id="metal.stainless_matte",
    )
    latch_knob.visual(
        Box((0.060, 0.016, 0.016)),
        origin=Origin(xyz=(0.0, 0.006, 0.0)),
        material=mats["latch"],
        name="knob_wing", material_class_id="metal.stainless_matte",
    )
    latch_knob.inertial = Inertial.from_geometry(
        Box((0.060, 0.020, 0.042)), mass=0.05, origin=Origin(xyz=(0.0, 0.008, 0.0))
    )
    model.articulation(
        "door_to_latch",
        ArticulationType.REVOLUTE,
        parent=panel,
        child=latch_knob,
        origin=Origin(xyz=(knob_x, front_y + 0.002, face_cz - 0.065)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=math.pi / 2.0),
    )
    return "door_to_latch"


def _build_cabinet_aed(model, cabinet, r, mats):
    w, h, d = _cab_dims(r)
    shelf_top = -h * 0.215 + 0.006
    aed = model.part("aed_module")
    _build_cabinet_aed_module(aed, r, mats)

    if r.aed_retention == "prismatic_slideout_shelf":
        # AED authored in cabinet coords (joint origin 0,0,0); skid rests on shelf.
        skid_z = -0.114 * r.body_scale
        for v in aed.visuals:
            x, y, z = v.origin.xyz
            v.origin = Origin(xyz=(x, y, z + (shelf_top - (skid_z - 0.005))), rpy=v.origin.rpy)
        model.articulation(
            "cabinet_to_aed",
            ArticulationType.PRISMATIC,
            parent=cabinet,
            child=aed,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=35.0, velocity=0.35, lower=0.0, upper=r.aed_slide_travel),
        )
        return aed, "cabinet_to_aed", None

    if r.aed_retention == "fixed_cradle":
        skid_bottom = -0.114 * r.body_scale - 0.005
        for v in aed.visuals:
            x, y, z = v.origin.xyz
            v.origin = Origin(xyz=(x, y, z - skid_bottom), rpy=v.origin.rpy)
        model.articulation(
            "cabinet_to_aed",
            ArticulationType.FIXED,
            parent=cabinet,
            child=aed,
            origin=Origin(xyz=(0.0, -0.012, shelf_top)),
        )
        return aed, None, None

    # swing_out_revolute_bracket
    pivot_x = -w / 2.0 + _WALL
    pivot_z = shelf_top - 0.006
    cradle = model.part("cradle_bracket")
    cradle.visual(
        Cylinder(radius=0.009, length=0.22),
        origin=Origin(xyz=(0.0, 0.0, 0.110)),
        material=mats["latch"],
        name="pivot_shaft", material_class_id="metal.stainless_matte",
    )
    cradle.visual(
        Box((w * 0.78, 0.028, 0.006)),
        origin=Origin(xyz=(w * 0.39, 0.0, 0.003)),
        material=mats["body2"],
        name="swing_arm", material_class_id="metal.paint_coated",
    )
    cradle.visual(
        Box((w * 0.65, 0.070, 0.004)),
        origin=Origin(xyz=(w * 0.46, 0.0, 0.008)),
        material=mats["body2"],
        name="cradle_tray", material_class_id="metal.paint_coated",
    )
    cradle.visual(
        Box((w * 0.65, 0.004, 0.018)),
        origin=Origin(xyz=(w * 0.46, 0.035, 0.019)),
        material=mats["body2"],
        name="retaining_lip", material_class_id="metal.paint_coated",
    )
    cradle.inertial = Inertial.from_geometry(
        Box((w * 0.78, 0.070, 0.22)), mass=0.6, origin=Origin(xyz=(w * 0.39, 0.0, 0.05))
    )
    # Rebase the AED so its skid bottom is at aed-local z=0, then weld it onto the
    # cradle tray top (FIXED origin on real tray geometry, per origin-far check).
    skid_bottom = -0.114 * r.body_scale - 0.005
    for v in aed.visuals:
        x, y, z = v.origin.xyz
        v.origin = Origin(xyz=(x, y, z - skid_bottom), rpy=v.origin.rpy)
    model.articulation(
        "cabinet_to_cradle",
        ArticulationType.REVOLUTE,
        parent=cabinet,
        child=cradle,
        origin=Origin(xyz=(pivot_x, 0.0, pivot_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=12.0, velocity=1.0, lower=0.0, upper=1.45),
    )
    model.articulation(
        "cradle_to_aed",
        ArticulationType.FIXED,
        parent=cradle,
        child=aed,
        origin=Origin(xyz=(w * 0.46, 0.0, 0.010)),
    )
    return aed, "cabinet_to_cradle", cradle


def _build_cabinet_beacon(model, cabinet, r, mats):
    w, h, d = _cab_dims(r)
    beacon = model.part("strobe_beacon")
    beacon.visual(
        Cylinder(radius=0.034, length=0.032),
        origin=Origin(xyz=(0.0, 0.0, 0.016)),
        material=mats["beacon"],
        name="beacon_base", material_class_id="plastic.opaque_generic",
    )
    beacon.visual(
        Sphere(radius=0.028),
        origin=Origin(xyz=(0.0, 0.0, 0.032)),
        material=mats["lens"],
        name="beacon_dome", material_class_id="plastic.frosted_translucent",
    )
    beacon.inertial = Inertial.from_geometry(
        Box((0.068, 0.068, 0.060)), mass=0.1, origin=Origin(xyz=(0.0, 0.0, 0.03))
    )
    model.articulation(
        "cabinet_to_beacon",
        ArticulationType.FIXED,
        parent=cabinet,
        child=beacon,
        origin=Origin(xyz=(0.0, -0.015, h / 2.0)),
    )
    return beacon


def _build_cabinet_family(model, r, mats):
    cabinet = _build_cabinet_root(model, r, mats)
    panel, open_joint, face_cx, face_cz = _build_cabinet_opening(model, cabinet, r, mats)
    _build_cabinet_latch(model, cabinet, panel, r, mats, face_cx, face_cz)
    _build_cabinet_aed(model, cabinet, r, mats)
    if r.alarm_beacon:
        _build_cabinet_beacon(model, cabinet, r, mats)


# --------------------------------------------------------------------------- #
# Carry-case family
# --------------------------------------------------------------------------- #
def _case_dims(r) -> tuple[float, float, float, float, float]:
    """(width, depth, wall_h, wall_t, rim_z) for the carry-case root."""
    s = r.body_scale
    if r.body_form == "soft_shoulder_bag_pouch":
        return (0.320 * s, 0.180 * s, 0.240 * s, 0.014, 0.240 * s)
    if r.body_form == "rigid_hard_shell_case":
        return (0.360 * s, 0.280 * s, 0.082 * s, 0.005, 0.082 * s)
    return (0.360 * s, 0.280 * s, 0.095 * s, 0.014, 0.095 * s)


def _build_case_aed(part, r, mats):
    """AED device (origin1 rounded_plate style, ExtrudeGeometry, Rule 3)."""
    s = r.body_scale
    part.visual(
        _rounded_plate(0.180 * s, 0.135 * s, 0.044, 0.018, "aed_body"),
        origin=Origin(xyz=(0.0, 0.0, 0.022)),
        material=mats["latch"],
        name="aed_body", material_class_id="plastic.opaque_glossy_molded",
    )
    part.visual(
        Box((0.088 * s, 0.052 * s, 0.008)),
        origin=Origin(xyz=(-0.020, -0.012, 0.042)),
        material=mats["aed_dark"],
        name="display_bezel", material_class_id="plastic.opaque_generic",
    )
    part.visual(
        Box((0.067 * s, 0.035 * s, 0.007)),
        origin=Origin(xyz=(-0.020, -0.012, 0.046)),
        material=mats["white"],
        name="display_screen", material_class_id="tech.control_interface",
    )
    part.visual(
        Cylinder(radius=0.014, length=0.012),
        origin=Origin(xyz=(0.045, 0.030, 0.042)),
        material=mats["aed"],
        name="shock_button", material_class_id="tech.control_interface",
    )
    part.inertial = Inertial.from_geometry(
        Box((0.180 * s, 0.135 * s, 0.050)), mass=1.2, origin=Origin(xyz=(0.0, 0.0, 0.025))
    )


def _build_case_root(model, r, mats):
    w, dd, wall_h, wall_t, rim_z = _case_dims(r)
    base = model.part("case_base")

    if r.body_form == "rigid_hard_shell_case":
        base.visual(
            mesh_from_cadquery(_hard_lower_shell_cq(w, dd, wall_h, wall_t, 0.018), "base_shell_body", tolerance=_TOL),
            material=mats["body"],
            name="base_shell_body", material_class_id="plastic.opaque_glossy_molded",
        )
        # external reinforcement ribs on the side faces.
        for i, rz in enumerate((0.020, 0.045)):
            base.visual(
                Box((w - 0.020, 0.003, 0.005)),
                origin=Origin(xyz=(0.0, -(dd / 2.0 + 0.0015), rz)),
                material=mats["body"],
                name=f"rib_left_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            base.visual(
                Box((w - 0.020, 0.003, 0.005)),
                origin=Origin(xyz=(0.0, +(dd / 2.0 + 0.0015), rz)),
                material=mats["body"],
                name=f"rib_right_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        base.visual(
            _rounded_plate(w - 0.060, dd - 0.060, 0.010, 0.014, "inner_floor"),
            origin=Origin(xyz=(0.0, 0.0, wall_t)),
            material=mats["foam"],
            name="inner_floor", material_class_id=("plastic.polystyrene_foam" if r.opening_mechanism == "clamshell_side_lid" else "fabric.flexible_foam"),
        )
    else:
        # box walls + rounded bottom + inner foam floor + top rim.
        base.visual(
            _rounded_plate(w - 0.010, dd - 0.010, 0.012, 0.024, "bottom_skin"),
            origin=Origin(xyz=(0.0, 0.0, 0.006)),
            material=mats["body"],
            name="bottom_skin", material_class_id="fabric.canvas",
        )
        base.visual(
            Box((w, wall_t, wall_h)),
            origin=Origin(xyz=(0.0, -dd / 2.0 + wall_t / 2.0, wall_h / 2.0)),
            material=mats["body2"],
            name="front_wall", material_class_id="fabric.canvas",
        )
        base.visual(
            Box((w, wall_t, wall_h)),
            origin=Origin(xyz=(0.0, dd / 2.0 - wall_t / 2.0, wall_h / 2.0)),
            material=mats["body2"],
            name="back_wall", material_class_id="fabric.canvas",
        )
        base.visual(
            Box((wall_t, dd - 2 * wall_t, wall_h)),
            origin=Origin(xyz=(-w / 2.0 + wall_t / 2.0, 0.0, wall_h / 2.0)),
            material=mats["body"],
            name="left_wall", material_class_id="fabric.canvas",
        )
        base.visual(
            Box((wall_t, dd - 2 * wall_t, wall_h)),
            origin=Origin(xyz=(w / 2.0 - wall_t / 2.0, 0.0, wall_h / 2.0)),
            material=mats["body"],
            name="right_wall", material_class_id="fabric.canvas",
        )
        base.visual(
            _rounded_plate(w - 3 * wall_t, dd - 3 * wall_t, 0.010, 0.016, "inner_floor"),
            origin=Origin(xyz=(0.0, 0.0, wall_t)),
            material=mats["foam"],
            name="inner_floor", material_class_id="fabric.flexible_foam",
        )
        for i, (sx, sy, bw, bd) in enumerate(
            [
                (0.0, -dd / 2.0, w + wall_t, 0.020),
                (0.0, dd / 2.0, w + wall_t, 0.020),
                (-w / 2.0, 0.0, 0.020, dd + wall_t),
                (w / 2.0, 0.0, 0.020, dd + wall_t),
            ]
        ):
            base.visual(
                Box((bw, bd, 0.020)),
                origin=Origin(xyz=(sx, sy, wall_h - 0.010)),
                material=mats["accent"],
                name=f"padded_top_rim_{i}", material_class_id="fabric.webbing",
            )
        if r.body_form == "soft_shoulder_bag_pouch":
            for i, sx in enumerate((-w / 2.0 - 0.008, w / 2.0 + 0.008)):
                base.visual(
                    Cylinder(radius=0.008, length=0.028),
                    origin=Origin(xyz=(sx, 0.0, wall_h * 0.82), rpy=(0.0, math.pi / 2.0, 0.0)),
                    material=mats["latch"],
                    name=f"side_d_ring_{i}", material_class_id="metal.steel_galvanized",
                )
            # The carry handle lives on the lid (see _build_lid_carry_handle) so
            # it can never clash with the lid's swing.

    # medical signage on the front wall (host-conformal).
    base.visual(
        Box((w * 0.28, 0.004, 0.050)),
        origin=Origin(xyz=(w * 0.20, -dd / 2.0 - 0.002, wall_h * 0.55)),
        material=mats["red"],
        name="ems_title", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    base.visual(
        Box((0.006, 0.004, 0.050)),
        origin=Origin(xyz=(-w * 0.22, -dd / 2.0 - 0.002, wall_h * 0.55)),
        material=mats["green"],
        name="ems_cross_v", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    base.visual(
        Box((0.050, 0.004, 0.006)),
        origin=Origin(xyz=(-w * 0.22, -dd / 2.0 - 0.002, wall_h * 0.55)),
        material=mats["green"],
        name="ems_cross_h", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    base.inertial = Inertial.from_geometry(
        Box((w, dd, wall_h)), mass=2.0, origin=Origin(xyz=(0.0, 0.0, wall_h / 2.0))
    )
    return base


def _build_lid_carry_handle(lid, r, mats) -> None:
    """Top carry handle as lid geometry (shoulder pouch).

    Parented to the lid so it rides with the swing and can never intersect it.
    Authored in the lid's pivot frame; posts embed 8 mm into the lid top so the
    handle welds to the leaf. Closed, the grip sits over the case centerline
    (clamshell) or the flap center (foldover).
    """
    w, dd, wall_h, wall_t, rim_z = _case_dims(r)
    if r.opening_mechanism == "clamshell_side_lid":
        hx = -(w / 2.0 + 0.004)  # case center in lid-local X
        hy = 0.0
        top = 0.011  # lid_outer top in lid-local Z
    else:  # foldover_top_flap
        hx = 0.0
        hy = -(dd + 0.020) / 2.0  # flap center in lid-local Y
        top = 0.0
    post_z = top - 0.008 + 0.035
    grip_z = top - 0.008 + 0.070 - 0.010
    for tag, sy in (("l", -(dd / 2.0 - wall_t)), ("r", dd / 2.0 - wall_t)):
        lid.visual(
            Box((0.026, 0.028, 0.070)),
            origin=Origin(xyz=(hx, hy + sy, post_z)),
            material=mats["body2"],
            name=f"handle_post_{tag}", material_class_id="fabric.webbing",
        )
    lid.visual(
        Box((0.026, dd - 2.0 * wall_t, 0.020)),
        origin=Origin(xyz=(hx, hy, grip_z)),
        material=mats["body2"],
        name="top_handle_grip", material_class_id="fabric.webbing",
    )


def _build_case_opening(model, base, r, mats):
    w, dd, wall_h, wall_t, rim_z = _case_dims(r)

    if r.opening_mechanism == "clamshell_side_lid":
        # Lid is wider than the case so it still covers the mouth when the
        # hinge axis sits outboard of the body (see articulation origin below).
        lid_w = w + 0.018
        lid_d = dd - 0.020
        lid = model.part("lid")
        # hinge barrel at lid-local origin (contacts the base rear rim).
        lid.visual(
            Cylinder(radius=0.008, length=lid_d),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
        )
        lid.visual(
            _rounded_plate(lid_w, lid_d, 0.014, 0.030, "lid_outer"),
            origin=Origin(xyz=(-lid_w / 2.0, 0.0, 0.004)),
            material=mats["body"],
            name="lid_outer", material_class_id=("fabric.canvas" if r.body_form in {"molded_soft_carry_case", "soft_shoulder_bag_pouch"} else "plastic.opaque_glossy_molded"),
        )
        lid.visual(
            _rounded_plate(lid_w - 0.020, lid_d - 0.020, 0.006, 0.024, "lid_inner"),
            origin=Origin(xyz=(-lid_w / 2.0, 0.0, -0.004)),
            material=mats["body2"],
            name="lid_inner", material_class_id=("fabric.canvas" if r.body_form in {"molded_soft_carry_case", "soft_shoulder_bag_pouch"} else "plastic.opaque_generic"),
        )
        # instruction icons on the lid outer face (host-conformal).
        for i, lx in enumerate((-0.72, -0.55, -0.38)):
            lid.visual(
                Box((lid_w * 0.10, lid_d * 0.14, 0.004)),
                origin=Origin(xyz=(lx * lid_w, -lid_d * 0.18, 0.013)),
                material=mats["red"],
                name=f"red_icon_panel_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
        lid.inertial = Inertial.from_geometry(
            Box((lid_w, lid_d, 0.020)), mass=0.8, origin=Origin(xyz=(-lid_w / 2.0, 0.0, 0.0))
        )
        model.articulation(
            "base_to_lid",
            ArticulationType.REVOLUTE,
            parent=base,
            child=lid,
            # Hinge axis just outboard of the inner wall face so the barrel
            # nests into the rim crest corner (constant contact through the
            # whole arc, like a real hinge knuckle), while the plate stack
            # seats the closed lid onto the rim and sweeps clear of it when
            # opening (an axis buried in the rim made the leaf clip; a fully
            # outboard axis left the open lid disconnected on thin hard-shell
            # walls).
            origin=Origin(xyz=(w / 2.0 + 0.004, 0.0, rim_z + 0.006)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.80),
        )
        return lid, "base_to_lid"

    # foldover_top_flap: hinge at the rear-top seam, folds back about X.
    flap_w = w * 0.94
    top_len = dd + 0.020
    lid = model.part("lid")
    lid.visual(
        Cylinder(radius=0.009, length=flap_w),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="hinge_barrel", material_class_id="metal.blackened_gunmetal",
    )
    lid.visual(
        Box((flap_w, top_len, 0.012)),
        origin=Origin(xyz=(0.0, -top_len / 2.0, -0.006)),
        material=mats["body2"],
        name="flap_top", material_class_id=("fabric.canvas" if r.body_form in {"molded_soft_carry_case", "soft_shoulder_bag_pouch"} else "plastic.opaque_glossy_molded"),
    )
    lid.visual(
        Box((flap_w * 0.60, 0.004, 0.025)),
        origin=Origin(xyz=(0.0, -top_len / 2.0, -0.014)),
        material=mats["red"],
        name="flap_red_stripe", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    lid.inertial = Inertial.from_geometry(
        Box((flap_w, top_len, 0.150)), mass=0.6, origin=Origin(xyz=(0.0, -top_len / 2.0, -0.04))
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, dd / 2.0 + wall_t, rim_z + 0.004)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.90),
    )
    return lid, "base_to_lid"


def _build_case_latch(model, base, r, mats):
    w, dd, wall_h, wall_t, rim_z = _case_dims(r)

    if r.latch_style == "velcro_strap_flap":
        flap = model.part("front_flap")
        flap.visual(
            Box((w * 0.28, 0.010, 0.045)),
            origin=Origin(xyz=(0.0, -0.006, -0.0225)),
            material=mats["body2"],
            name="soft_flap_body", material_class_id="fabric.canvas",
        )
        flap.visual(
            Box((w * 0.24, 0.004, 0.030)),
            origin=Origin(xyz=(0.0, -0.013, -0.026)),
            material=mats["foam"],
            name="velcro_face", material_class_id="fabric.webbing",
        )
        flap.visual(
            Box((w * 0.30, 0.016, 0.012)),
            origin=Origin(xyz=(0.0, -0.004, -0.002)),
            material=mats["body2"],
            name="sewn_hinge_band", material_class_id="fabric.canvas",
        )
        flap.inertial = Inertial.from_geometry(
            Box((w * 0.30, 0.020, 0.100)), mass=0.1, origin=Origin(xyz=(0.0, 0.0, -0.04))
        )
        model.articulation(
            "base_to_front_flap",
            ArticulationType.REVOLUTE,
            parent=base,
            child=flap,
            origin=Origin(xyz=(0.0, -dd / 2.0, wall_h * 0.62)),
            # Hinge line runs along X (the top edge of the front face): the
            # strap folds outward away from the front wall. (A Y axis would
            # swing it sideways through the side wall.)
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=1.6, lower=0.0, upper=math.radians(100.0)),
        )
        return ["front_flap"], ["base_to_front_flap"]

    # snap_latch: two over-center front snap latches (hardshell-style).
    names, joints = [], []
    for i, ly in enumerate((-w * 0.17, w * 0.17)):
        latch = model.part(f"snap_latch_{i}")
        latch.visual(
            Box((0.028, 0.008, 0.026)),
            origin=Origin(xyz=(0.0, -0.004, 0.013)),
            material=mats["latch"],
            name=f"latch_lever_{i}", material_class_id="metal.stainless_matte",
        )
        latch.visual(
            Box((0.020, 0.012, 0.005)),
            origin=Origin(xyz=(0.0, -0.006, 0.028)),
            material=mats["latch"],
            name=f"latch_hook_{i}", material_class_id="metal.stainless_matte",
        )
        latch.visual(
            Cylinder(radius=0.003, length=0.030),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name=f"latch_pin_{i}", material_class_id="metal.blackened_gunmetal",
        )
        latch.inertial = Inertial.from_geometry(
            Box((0.014, 0.030, 0.040)), mass=0.02, origin=Origin(xyz=(0.0, 0.0, 0.015))
        )
        # mounting boss on the front wall.
        base.visual(
            Box((0.014, 0.010, 0.030)),
            origin=Origin(xyz=(ly, -dd / 2.0 - 0.003, wall_h * 0.42)),
            material=mats["body"],
            name=f"latch_boss_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            f"base_to_latch_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=latch,
            origin=Origin(xyz=(ly, -dd / 2.0 - 0.004, wall_h * 0.42)),
            # Over-center lever flips outward about a hinge line along X (the
            # latch pin axis on the front face), not sideways about Y.
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=math.radians(120.0)),
        )
        names.append(f"snap_latch_{i}")
        joints.append(f"base_to_latch_{i}")
    return names, joints


def _build_carrycase_family(model, r, mats):
    base = _build_case_root(model, r, mats)
    lid, _ = _build_case_opening(model, base, r, mats)
    if r.body_form == "soft_shoulder_bag_pouch":
        _build_lid_carry_handle(lid, r, mats)
    aed = model.part("aed_device")
    _build_case_aed(aed, r, mats)
    w, dd, wall_h, wall_t, rim_z = _case_dims(r)
    model.articulation(
        "base_to_aed",
        ArticulationType.FIXED,
        parent=base,
        child=aed,
        origin=Origin(xyz=(0.0, 0.0, wall_t + 0.005)),
    )
    _build_case_latch(model, base, r, mats)


# --------------------------------------------------------------------------- #
# Build entry point
# --------------------------------------------------------------------------- #
def build_defibrillator_case(
    config: DefibrillatorCaseConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r.palette_style)
    if r.family == "cabinet":
        _build_cabinet_family(model, r, mats)
    else:
        _build_carrycase_family(model, r, mats)
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_defibrillator_case(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_defibrillator_case(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests / QC. Captured-fit overlaps (seated door/lid reveal, shutter in guides,
# knob/latch pins in bosses, swing arm in cavity, AED sliding out of the closed
# door as a sequenced mechanism, beacon on the roof) are declared element/part
# scoped so the sampled-pose motion QC honours them; each mechanism gets a
# targeted pose check proving intended motion.
# --------------------------------------------------------------------------- #
def run_defibrillator_case_tests(
    object_model: ArticulatedObject,
    config: DefibrillatorCaseConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    non_fixed = [j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED]
    ctx.check(
        "at least one non-fixed opening joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed count={len(non_fixed)}",
    )

    if r.family == "cabinet":
        cabinet = object_model.get_part("cabinet")
        opening_part = (
            object_model.get_part("shutter")
            if r.opening_mechanism == "roll_up_shutter"
            else object_model.get_part("door")
        )
        # opening mechanism
        if r.opening_mechanism == "roll_up_shutter":
            shutter = object_model.get_part("shutter")
            joint = object_model.get_articulation("cabinet_to_shutter")
            ctx.allow_overlap(shutter, cabinet, reason="Shutter slats ride in the carcass guide rails and stack into the roller housing.")
            ctx.check(
                "cabinet_to_shutter is PRISMATIC about +Z",
                joint.articulation_type == ArticulationType.PRISMATIC and abs(joint.axis[2]) > 0.99,
                details=f"axis={joint.axis}",
            )
            rest = ctx.part_world_position(shutter)
            with ctx.pose({joint: joint.motion_limits.upper}):
                up = ctx.part_world_position(shutter)
            ctx.check(
                "shutter rises to clear the opening",
                rest is not None and up is not None and up[2] > rest[2] + joint.motion_limits.upper * 0.7,
                details=f"rest={rest}, up={up}",
            )
        else:
            door = object_model.get_part("door")
            joint = object_model.get_articulation("cabinet_to_door")
            ctx.allow_isolated_part(
                door,
                reason="door swings open clear of the cabinet and loses contact",
            )
            if any(p.name == "latch_knob" for p in object_model.parts):
                ctx.allow_isolated_part(
                    object_model.get_part("latch_knob"),
                    reason="door latch knob rides on the door leaf and swings clear with it",
                )
            ctx.allow_overlap(door, cabinet, reason="Door panel is seated proud of the cabinet front at the hinge reveal.")
            ctx.check(
                "cabinet_to_door is REVOLUTE",
                joint.articulation_type == ArticulationType.REVOLUTE,
                details=f"axis={joint.axis}, type={joint.articulation_type}",
            )
            closed = ctx.part_world_aabb(door)
            with ctx.pose({joint: joint.motion_limits.upper}):
                opened = ctx.part_world_aabb(door)
            if r.opening_mechanism == "clear_flip_up_cover":
                moved = opened is not None and closed is not None and opened[0][2] > closed[0][2] + 0.06
            elif r.opening_mechanism == "drop_down_flap":
                moved = opened is not None and closed is not None and opened[1][2] < closed[1][2] - 0.06
            else:
                moved = opened is not None and closed is not None and opened[1][1] > closed[1][1] + 0.08
            ctx.check(
                "opening panel moves clear when actuated",
                moved,
                details=f"closed={closed}, opened={opened}",
            )

        # latch
        if r.latch_style == "rotary_knob_latch" and r.opening_mechanism != "roll_up_shutter":
            knob = object_model.get_part("latch_knob")
            door = object_model.get_part("door")
            kj = object_model.get_articulation("door_to_latch")
            ctx.allow_overlap(knob, door, reason="Rotary knob is seated in its door-face boss and co-rotates with the door.")
            ctx.allow_overlap(knob, cabinet, reason="The knob rides on the door leaf and shares the door reveal at the cabinet edge through the swing arc.")
            ctx.check(
                "door_to_latch is REVOLUTE about the door face normal (+Y)",
                kj.articulation_type == ArticulationType.REVOLUTE and abs(kj.axis[1]) > 0.9,
                details=f"axis={kj.axis}",
            )
            rest = ctx.part_world_aabb(knob)
            with ctx.pose({kj: math.pi / 2.0}):
                turned = ctx.part_world_aabb(knob)
            ctx.check(
                "rotary knob wing rotates",
                rest is not None and turned is not None
                and (turned[1][2] - turned[0][2]) > (rest[1][2] - rest[0][2]) + 0.008,
                details=f"rest={rest}, turned={turned}",
            )

        # AED retention
        aed = object_model.get_part("aed_module")
        ctx.allow_isolated_part(
            aed,
            reason="AED module slides/swings out of the cabinet and loses contact when retrieved",
        )
        if r.aed_retention == "prismatic_slideout_shelf":
            aj = object_model.get_articulation("cabinet_to_aed")
            ctx.allow_overlap(aed, opening_part, reason="AED slides out through the front only once the door/shutter is open (sequenced mechanism).")
            ctx.check(
                "cabinet_to_aed is PRISMATIC about +Y",
                aj.articulation_type == ArticulationType.PRISMATIC and abs(aj.axis[1]) > 0.99,
                details=f"axis={aj.axis}",
            )
            if r.latch_style == "rotary_knob_latch":
                ctx.allow_overlap(aed, object_model.get_part("latch_knob"), reason="AED passes the door-mounted rotary knob only when sliding out through the open door (sequenced).")
            rest = ctx.part_world_position(aed)
            with ctx.pose({aj: aj.motion_limits.upper}):
                pulled = ctx.part_world_position(aed)
            ctx.check(
                "AED module translates outward when removed",
                rest is not None and pulled is not None and pulled[1] > rest[1] + 0.10,
                details=f"rest={rest}, pulled={pulled}",
            )
        elif r.aed_retention == "swing_out_revolute_bracket":
            cradle = object_model.get_part("cradle_bracket")
            cj = object_model.get_articulation("cabinet_to_cradle")
            ctx.allow_overlap(cradle, cabinet, reason="Cradle pivot shaft is embedded in the left wall and the swing arm rests inside the hollow cavity at rest.")
            ctx.allow_overlap(aed, cabinet, reason="AED on the cradle sweeps through the open front when the bracket swings out.")
            ctx.allow_overlap(aed, opening_part, reason="AED swings out through the front only once the door/shutter is open (sequenced mechanism).")
            ctx.allow_overlap(cradle, opening_part, reason="Cradle swing arm passes the opening plane; retrieval happens only with the door/shutter open (sequenced).")
            if r.latch_style == "rotary_knob_latch":
                ctx.allow_overlap(aed, object_model.get_part("latch_knob"), reason="AED passes the door-mounted rotary knob during sequenced retrieval.")
            ctx.check(
                "cabinet_to_cradle is REVOLUTE about +Z",
                cj.articulation_type == ArticulationType.REVOLUTE and abs(cj.axis[2]) > 0.99,
                details=f"axis={cj.axis}",
            )
            rest = ctx.part_world_position(aed)
            with ctx.pose({cj: cj.motion_limits.upper}):
                swung = ctx.part_world_position(aed)
            ctx.check(
                "AED swings forward for retrieval",
                rest is not None and swung is not None and swung[1] > rest[1] + 0.06,
                details=f"rest={rest}, swung={swung}",
            )
        else:  # fixed_cradle
            ctx.check(
                "cabinet_to_aed is a FIXED cradle retaining the AED",
                object_model.get_articulation("cabinet_to_aed").articulation_type == ArticulationType.FIXED,
            )

        # beacon
        if r.alarm_beacon:
            beacon = object_model.get_part("strobe_beacon")
            ctx.allow_overlap(beacon, cabinet, reason="Alarm beacon base is seated on the cabinet roof.")
            ctx.check(
                "roof-top alarm beacon FIXED to cabinet",
                object_model.get_articulation("cabinet_to_beacon").articulation_type == ArticulationType.FIXED,
            )

    else:  # carrycase
        base = object_model.get_part("case_base")
        lid = object_model.get_part("lid")
        lj = object_model.get_articulation("base_to_lid")
        ctx.allow_overlap(lid, base, reason="Lid hinge barrel seats at the rear-top seam and the closed lid rests on the base rim.")
        ctx.check(
            "base_to_lid is REVOLUTE",
            lj.articulation_type == ArticulationType.REVOLUTE,
            details=f"axis={lj.axis}",
        )
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({lj: lj.motion_limits.upper}):
            opened = ctx.part_world_aabb(lid)
        if r.opening_mechanism == "foldover_top_flap":
            lid_moved = closed is not None and opened is not None and (
                abs(opened[1][1] - closed[1][1]) > 0.05
                or abs(opened[0][1] - closed[0][1]) > 0.05
                or abs(opened[1][2] - closed[1][2]) > 0.05
            )
        else:
            lid_moved = closed is not None and opened is not None and opened[1][2] > closed[1][2] + 0.05
        ctx.check(
            "lid opens when actuated",
            lid_moved,
            details=f"closed={closed}, opened={opened}",
        )

        # AED fixed inside
        aed = object_model.get_part("aed_device")
        ctx.allow_overlap(aed, base, reason="AED device is seated on the interior foam floor of the case.")
        ctx.check(
            "base_to_aed FIXED retains the AED inside the case",
            object_model.get_articulation("base_to_aed").articulation_type == ArticulationType.FIXED,
        )

        # latch
        if r.latch_style == "velcro_strap_flap":
            flap = object_model.get_part("front_flap")
            fj = object_model.get_articulation("base_to_front_flap")
            ctx.allow_overlap(flap, base, reason="Velcro strap flap seats against the case front wall when closed.")
            ctx.allow_overlap(flap, lid, reason="Front buckle flap is reached only after the top closure is opened (sequenced closure).")
            ctx.check(
                "base_to_front_flap is REVOLUTE",
                fj.articulation_type == ArticulationType.REVOLUTE,
                details=f"axis={fj.axis}",
            )
            rest = ctx.part_world_aabb(flap)
            with ctx.pose({fj: fj.motion_limits.upper}):
                lifted = ctx.part_world_aabb(flap)
            ctx.check(
                "velcro flap swings open",
                rest is not None and lifted is not None and (rest[0][1] - lifted[0][1]) > 0.02,
                details=f"rest={rest}, lifted={lifted}",
            )
        else:  # snap_latch
            for i in range(2):
                latch = object_model.get_part(f"snap_latch_{i}")
                sj = object_model.get_articulation(f"base_to_latch_{i}")
                ctx.allow_overlap(latch, base, reason="Snap latch pivot pin is captured inside the front-wall mounting boss.")
                ctx.allow_overlap(latch, lid, reason="Front snap latch is reached only after the top closure is opened (sequenced closure).")
                ctx.check(
                    f"base_to_latch_{i} is REVOLUTE",
                    sj.articulation_type == ArticulationType.REVOLUTE,
                    details=f"axis={sj.axis}",
                )
            latch0 = object_model.get_part("snap_latch_0")
            sj0 = object_model.get_articulation("base_to_latch_0")
            rest = ctx.part_world_aabb(latch0)
            with ctx.pose({sj0: math.radians(100.0)}):
                flipped = ctx.part_world_aabb(latch0)
            moved = rest is not None and flipped is not None and (
                abs(flipped[0][0] - rest[0][0]) > 0.004
                or abs(flipped[1][0] - rest[1][0]) > 0.004
                or abs(flipped[1][2] - rest[1][2]) > 0.004
                or abs(flipped[0][2] - rest[0][2]) > 0.004
            )
            ctx.check(
                "snap latch flips outward when released",
                moved,
                details=f"rest={rest}, flipped={flipped}",
            )

    return ctx.report()


__all__ = [
    "BodyForm",
    "OpeningMechanism",
    "AedRetention",
    "LatchStyle",
    "PaletteStyle",
    "DefibrillatorCaseConfig",
    "ResolvedDefibrillatorCaseConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "build_defibrillator_case",
    "build_seeded_defibrillator_case",
    "run_defibrillator_case_tests",
]
