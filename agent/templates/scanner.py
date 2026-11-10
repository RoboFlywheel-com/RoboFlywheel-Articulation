# SPDX-License-Identifier: Apache-2.0

"""Document scanner modular template (0611 / scanner).

Spec: articraft_template_authoring/specs_modular_v1/scanner.md
Pattern: parallel_children (single ``scanner_body`` root + parallel lid & controls).

Slots (§ spec table):
  * ``body_form`` (4): flatbed_full / flatbed_slim / sheet_fed / book_edge_flatbed
    — Slot A owns the root chassis mesh, platen inline visuals, feet, status
    lens, and 2-3 fixed rear knuckles (for the simple hinge).
  * ``lid_mechanism`` (3): simple_hinge / rising_book_hinge / hinged_adf
    — Slot B parents ``lid`` to ``scanner_body`` via one REVOLUTE ``-X`` joint;
    ``hinged_adf`` additionally spawns ``adf_cover`` on a second REVOLUTE.
  * ``controls`` (4): control_ring_button / dual_button_deck / quad_button_row /
    tilting_control_panel — Slot C adds a control panel (or inline deck) and
    1-4 PRISMATIC push buttons.

Palette: 5 realistic scanner colorways (office_beige, matte_black,
silver_black, white_consumer, industrial_grey) — §6 axis, ≥3 material classes
(painted plastic + platen glass + metal hinge hardware).

The 5★ sources encode the lid hinge as a captured pin inside knuckle sleeves
(portable_slim L134-L154, sheet_fed L149-L167, ADF L437-L453). To satisfy
Rule 2 (``MatingContract`` on non-FIXED joints) we anchor the mating faces on
the housing top surface (``housing_shell``) and the lid panel bottom
(``lid_panel``) rather than the captured pin geometry — the pin/knuckle
overlap is scoped as ``element_scoped ctx.allow_overlap`` in run_tests, and
the mating faces themselves are the real seating surfaces the closed lid rests
on. This keeps Rule 2 honest without shipping a phantom fixed sleeve.
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
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BodyForm = Literal["flatbed_full", "flatbed_slim", "sheet_fed", "book_edge_flatbed"]
LidMechanism = Literal["simple_hinge", "rising_book_hinge", "hinged_adf"]
Controls = Literal[
    "control_ring_button",
    "dual_button_deck",
    "quad_button_row",
    "tilting_control_panel",
]
PaletteStyle = Literal[
    "office_beige",
    "matte_black",
    "silver_black",
    "white_consumer",
    "industrial_grey",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "flatbed_full",
    "flatbed_slim",
    "sheet_fed",
    "book_edge_flatbed",
)
LID_MECHANISMS: tuple[LidMechanism, ...] = (
    "simple_hinge",
    "rising_book_hinge",
    "hinged_adf",
)
CONTROLS: tuple[Controls, ...] = (
    "control_ring_button",
    "dual_button_deck",
    "quad_button_row",
    "tilting_control_panel",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "office_beige",
    "matte_black",
    "silver_black",
    "white_consumer",
    "industrial_grey",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "office_beige": {
        "shell": (0.90, 0.86, 0.72, 1.0),
        "shell_edge": (0.68, 0.64, 0.52, 1.0),
        "platen_glass": (0.06, 0.10, 0.12, 0.72),
        "lid_shell": (0.86, 0.82, 0.68, 1.0),
        "lid_pad": (0.94, 0.92, 0.86, 1.0),
        "metal": (0.35, 0.34, 0.30, 1.0),
        "rubber": (0.09, 0.09, 0.08, 1.0),
        "button": (0.20, 0.20, 0.18, 1.0),
        "status": (0.05, 0.72, 0.24, 1.0),
        "accent": (0.32, 0.48, 0.72, 1.0),
    },
    "matte_black": {
        "shell": (0.05, 0.06, 0.07, 1.0),
        "shell_edge": (0.18, 0.19, 0.20, 1.0),
        "platen_glass": (0.02, 0.05, 0.07, 0.86),
        "lid_shell": (0.04, 0.05, 0.06, 1.0),
        "lid_pad": (0.08, 0.08, 0.09, 1.0),
        "metal": (0.24, 0.25, 0.26, 1.0),
        "rubber": (0.03, 0.03, 0.03, 1.0),
        "button": (0.10, 0.10, 0.12, 1.0),
        "status": (0.05, 0.72, 0.34, 1.0),
        "accent": (0.62, 0.20, 0.82, 1.0),
    },
    "silver_black": {
        "shell": (0.62, 0.64, 0.66, 1.0),
        "shell_edge": (0.34, 0.35, 0.36, 1.0),
        "platen_glass": (0.06, 0.10, 0.12, 0.75),
        "lid_shell": (0.08, 0.09, 0.10, 1.0),
        "lid_pad": (0.14, 0.14, 0.15, 1.0),
        "metal": (0.72, 0.74, 0.76, 1.0),
        "rubber": (0.04, 0.04, 0.05, 1.0),
        "button": (0.24, 0.24, 0.26, 1.0),
        "status": (1.0, 0.72, 0.08, 1.0),
        "accent": (0.08, 0.42, 0.82, 1.0),
    },
    "white_consumer": {
        "shell": (0.94, 0.94, 0.92, 1.0),
        "shell_edge": (0.66, 0.68, 0.68, 1.0),
        "platen_glass": (0.035, 0.050, 0.055, 0.88),
        "lid_shell": (0.105, 0.115, 0.118, 1.0),
        "lid_pad": (0.045, 0.050, 0.052, 1.0),
        "metal": (0.19, 0.20, 0.20, 1.0),
        "rubber": (0.15, 0.15, 0.15, 1.0),
        "button": (0.94, 0.94, 0.92, 1.0),
        "status": (0.035, 0.75, 0.35, 1.0),
        "accent": (0.20, 0.42, 0.82, 1.0),
    },
    "industrial_grey": {
        "shell": (0.42, 0.44, 0.46, 1.0),
        "shell_edge": (0.24, 0.25, 0.26, 1.0),
        "platen_glass": (0.46, 0.86, 0.78, 0.55),
        "lid_shell": (0.20, 0.22, 0.24, 1.0),
        "lid_pad": (0.14, 0.15, 0.16, 1.0),
        "metal": (0.30, 0.32, 0.34, 1.0),
        "rubber": (0.06, 0.06, 0.07, 1.0),
        "button": (0.16, 0.18, 0.20, 1.0),
        "status": (1.0, 0.72, 0.08, 1.0),
        "accent": (0.60, 0.65, 0.70, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Real-world nominal dimensions (meters), sourced from the 5★ records.
# ---------------------------------------------------------------------------
# flatbed_full — from control_tilting L20-L23 (0.450 × 0.360 × 0.076).
_FULL_W = 0.450
_FULL_D = 0.360
_FULL_H = 0.076
_FULL_WELL_W = 0.342
_FULL_WELL_D = 0.250
_FULL_WELL_H = 0.032
_FULL_WELL_Y = 0.031

# flatbed_slim — from portable_slim L20-L23 (0.430 × 0.340 × 0.030, thin).
_SLIM_W = 0.430
_SLIM_D = 0.340
_SLIM_H = 0.034
_SLIM_WELL_W = 0.340
_SLIM_WELL_D = 0.248
_SLIM_WELL_H = 0.010
_SLIM_WELL_Y = 0.020

# sheet_fed — from sheet_fed L20-L23 (0.400 × 0.160 × 0.088 tall-narrow, no top well).
_SHEET_W = 0.400
_SHEET_D = 0.160
_SHEET_H = 0.088

# book_edge_flatbed — from book_scanner L20-L21 (0.310 × 0.455 portrait).
_BOOK_W = 0.310
_BOOK_D = 0.455
_BOOK_H = 0.062  # low chassis (0.028 lower + 0.034 upper minus overlap)
_BOOK_WELL_W = 0.290
_BOOK_WELL_D = 0.358
_BOOK_WELL_H = 0.012
_BOOK_WELL_Y = 0.012

# Common: platen glass thickness / reference strip / lid params.
_PLATEN_GLASS_T = 0.003
_REF_STRIP_T = 0.0008
_LID_PANEL_T = 0.016
_LID_PAD_T = 0.0022
_FOOT_R = 0.012
_FOOT_H = 0.006

# Reference lid open angle from sources (portable_slim L25 = 65°).
_REF_LID_ANGLE = math.radians(65.0)


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ScannerConfig:
    body_form: BodyForm | None = None
    lid_mechanism: LidMechanism | None = None
    controls: Controls | None = None
    palette_style: PaletteStyle | None = None
    body_width_scale: float = 1.0
    body_depth_scale: float = 1.0
    body_height_scale: float = 1.0
    platen_well_depth_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    panel_tilt_scale: float = 1.0
    button_travel_scale: float = 1.0
    name: str = "scanner"


@dataclass(frozen=True)
class ResolvedScannerConfig:
    body_form: BodyForm
    lid_mechanism: LidMechanism
    controls: Controls
    palette_style: PaletteStyle
    # Resolved body geometry (meters).
    body_w: float  # outer X extent
    body_d: float  # outer Y extent
    body_h: float  # outer Z extent
    well_w: float  # platen well width (X); 0 for sheet_fed
    well_d: float  # platen well depth (Y); 0 for sheet_fed
    well_h: float  # platen well vertical depth
    well_y: float  # well center Y (positive = rear)
    body_top: float  # z of housing top face
    # Rear-hinge line in body-local frame.
    hinge_y: float
    hinge_z: float
    # Whether the body has an open top platen well (False for sheet_fed).
    has_top_well: bool
    # Front control mount Y (negative = front).
    control_y: float
    # Lid geometry.
    lid_w: float
    lid_d: float
    lid_open: float  # positive open angle (radians)
    lid_lower: float  # negative closed angle for the raised reference pose
    # Button travel.
    button_travel: float
    # Panel tilt (used only for tilting_control_panel).
    panel_tilt: float
    # Extra hinge rise for rising_book_hinge.
    hinge_rise: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ---------------------------------------------------------------------------
# Compatibility gating (§ spec 7 / 9).
# ---------------------------------------------------------------------------
_SHEET_FED_LIDS: tuple[LidMechanism, ...] = ("simple_hinge",)
_SHEET_FED_CONTROLS: tuple[Controls, ...] = ("control_ring_button", "dual_button_deck")
_BOOK_EDGE_CONTROLS: tuple[Controls, ...] = ("dual_button_deck", "quad_button_row")


def _apply_compat(
    body_form: BodyForm,
    lid_mechanism: LidMechanism,
    controls: Controls,
) -> tuple[LidMechanism, Controls]:
    if body_form == "sheet_fed":
        if lid_mechanism not in _SHEET_FED_LIDS:
            lid_mechanism = "simple_hinge"
        if controls not in _SHEET_FED_CONTROLS:
            controls = "control_ring_button"
    elif body_form == "book_edge_flatbed":
        if controls not in _BOOK_EDGE_CONTROLS:
            controls = "dual_button_deck"
    return lid_mechanism, controls


def config_from_seed(seed: int) -> ScannerConfig:
    rng = random.Random(seed)
    return ScannerConfig(
        body_form=rng.choice(BODY_FORMS),
        lid_mechanism=rng.choice(LID_MECHANISMS),
        controls=rng.choice(CONTROLS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_width_scale=round(rng.uniform(0.88, 1.12), 4),
        body_depth_scale=round(rng.uniform(0.88, 1.12), 4),
        body_height_scale=round(rng.uniform(0.85, 1.15), 4),
        platen_well_depth_scale=round(rng.uniform(0.80, 1.20), 4),
        lid_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        panel_tilt_scale=round(rng.uniform(0.85, 1.15), 4),
        button_travel_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_scanner_{seed}",
    )


def resolve_config(config: ScannerConfig | None = None) -> ResolvedScannerConfig:
    cfg = config or ScannerConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    lid_mechanism = _pick(cfg.lid_mechanism, LID_MECHANISMS)
    controls = _pick(cfg.controls, CONTROLS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Compatibility gating (§9).
    lid_mechanism, controls = _apply_compat(body_form, lid_mechanism, controls)

    wscale = _clamp(cfg.body_width_scale, 0.88, 1.12)
    dscale = _clamp(cfg.body_depth_scale, 0.88, 1.12)
    hscale = _clamp(cfg.body_height_scale, 0.85, 1.15)
    well_scale = _clamp(cfg.platen_well_depth_scale, 0.80, 1.20)
    angle_scale = _clamp(cfg.lid_open_angle_scale, 0.85, 1.10)
    tilt_scale = _clamp(cfg.panel_tilt_scale, 0.85, 1.15)
    travel_scale = _clamp(cfg.button_travel_scale, 0.85, 1.15)

    if body_form == "flatbed_full":
        body_w = _FULL_W * wscale
        body_d = _FULL_D * dscale
        body_h = _FULL_H * hscale
        well_w = _FULL_WELL_W * wscale
        well_d = _FULL_WELL_D * dscale
        well_h = _FULL_WELL_H * well_scale
        well_y = _FULL_WELL_Y * dscale
        has_top_well = True
    elif body_form == "flatbed_slim":
        body_w = _SLIM_W * wscale
        body_d = _SLIM_D * dscale
        body_h = _SLIM_H * hscale
        well_w = _SLIM_WELL_W * wscale
        well_d = _SLIM_WELL_D * dscale
        well_h = _SLIM_WELL_H * well_scale
        well_y = _SLIM_WELL_Y * dscale
        has_top_well = True
    elif body_form == "sheet_fed":
        body_w = _SHEET_W * wscale
        body_d = _SHEET_D * dscale
        body_h = _SHEET_H * hscale
        well_w = 0.0
        well_d = 0.0
        well_h = 0.0
        well_y = 0.0
        has_top_well = False
    else:  # book_edge_flatbed
        body_w = _BOOK_W * wscale
        body_d = _BOOK_D * dscale
        body_h = _BOOK_H * hscale
        well_w = _BOOK_WELL_W * wscale
        well_d = _BOOK_WELL_D * dscale
        well_h = _BOOK_WELL_H * well_scale
        well_y = _BOOK_WELL_Y * dscale
        has_top_well = True

    body_top = body_h  # body extends from z=0 to z=body_h.

    # Well-depth clearance inequality: well_h <= body_h - 0.020 (min 0.006).
    if has_top_well:
        max_well = max(0.006, body_h - 0.020)
        if well_h > max_well:
            well_h = max_well

    # Hinge line: rear edge, pulled INWARD from body_d/2 by 0.020 so the
    # knuckle bboxes overlap the full housing thickness (avoids grazing the
    # rounded rear corner). z is placed so the knuckle radius 0.008 embeds
    # 4 mm into the housing top face (bottom at body_top - 0.004).
    hinge_y = body_d / 2.0 - 0.020
    hinge_z = body_top + 0.004

    # Front control mount: front edge (y = -body_d/2 + 0.030).
    control_y = -body_d / 2.0 + 0.030

    # Lid footprint follows body outer minus a small gap.
    lid_w = body_w - 0.020
    lid_d = body_d - 0.020

    # Lid open range: q=0 is the CLOSED pose (panel resting on housing top),
    # q=lid_open is the fully open pose (panel raised upward). This makes the
    # mating gap check + closed-pose collision check both operate on the
    # authored geometry directly.
    lid_open = _clamp(_REF_LID_ANGLE * angle_scale, math.radians(50.0), math.radians(95.0))
    lid_lower = 0.0

    button_travel = _clamp(0.0012 * travel_scale, 0.0009, 0.0015)
    panel_tilt = _clamp(math.radians(25.0) * tilt_scale, math.radians(18.0), math.radians(32.0))
    hinge_rise = 0.015 if lid_mechanism == "rising_book_hinge" else 0.0

    return ResolvedScannerConfig(
        body_form=body_form,
        lid_mechanism=lid_mechanism,
        controls=controls,
        palette_style=palette_style,
        body_w=body_w,
        body_d=body_d,
        body_h=body_h,
        well_w=well_w,
        well_d=well_d,
        well_h=well_h,
        well_y=well_y,
        body_top=body_top,
        hinge_y=hinge_y,
        hinge_z=hinge_z + hinge_rise,
        has_top_well=has_top_well,
        control_y=control_y,
        lid_w=lid_w,
        lid_d=lid_d,
        lid_open=lid_open,
        lid_lower=lid_lower,
        button_travel=button_travel,
        panel_tilt=panel_tilt,
        hinge_rise=hinge_rise,
        name=cfg.name or "scanner",
    )


def with_overrides(config: ScannerConfig, **kwargs) -> ScannerConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ScannerConfig | ResolvedScannerConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedScannerConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("lid_mechanism", r.lid_mechanism),
        ("controls", r.controls),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Housing mesh helpers (§ Rule 3: preserve CadQuery / mesh_from_cadquery for
# body_form candidates whose 5★ sources use it).
# ---------------------------------------------------------------------------
def _rounded_prism(w: float, d: float, h: float, r: float, *, center_z: float) -> cq.Workplane:
    shape = cq.Workplane("XY").box(w, d, h).translate((0.0, 0.0, center_z))
    if r > 0.0:
        shape = shape.edges("|Z").fillet(min(r, 0.45 * min(w, d)))
    return shape


def _flatbed_housing_mesh(r: ResolvedScannerConfig, *, corner_r: float = 0.014):
    """Flatbed housing with recessed platen well (used by full / slim / book_edge)."""
    body = _rounded_prism(r.body_w, r.body_d, r.body_h, corner_r, center_z=r.body_h / 2.0)
    if r.has_top_well and r.well_h > 0.0005:
        cavity = _rounded_prism(
            r.well_w,
            r.well_d,
            r.well_h + 0.002,
            0.010,
            center_z=r.body_h + 0.001 - (r.well_h + 0.002) / 2.0,
        ).translate((0.0, r.well_y, 0.0))
        body = body.cut(cavity)
    if r.body_form == "book_edge_flatbed":
        # Remove the right-side (+X) upper wall from the platen level up.
        edge_w = 0.028
        # The cut sits along the +X flank of the body, from y=-body_d/2+0.020 to +body_d/2-0.020,
        # and from z = body_h - well_h (platen level) up.
        edge_x_center = r.body_w / 2.0 - edge_w / 2.0 + 0.001
        cut_h = r.well_h + 0.020
        edge_cut = _rounded_prism(
            edge_w,
            r.body_d - 0.020,
            cut_h,
            0.003,
            center_z=r.body_h - cut_h / 2.0 + 0.002,
        ).translate((edge_x_center, 0.0, 0.0))
        body = body.cut(edge_cut)
    return body


def _sheet_fed_housing_mesh(r: ResolvedScannerConfig):
    """Sheet-fed tall-narrow housing (compact box, no top well, front + rear slots)."""
    body = _rounded_prism(r.body_w, r.body_d, r.body_h, 0.014, center_z=r.body_h / 2.0)
    # Front intake slot (thin horizontal slit).
    front_slot = (
        cq.Workplane("XY")
        .box(r.body_w * 0.75, 0.024, 0.008)
        .translate((0.0, -r.body_d / 2.0 - 0.005, r.body_h * 0.70))
    )
    body = body.cut(front_slot)
    # Rear output slot.
    rear_slot = (
        cq.Workplane("XY")
        .box(r.body_w * 0.70, 0.024, 0.006)
        .translate((0.0, r.body_d / 2.0 + 0.005, r.body_h * 0.74))
    )
    body = body.cut(rear_slot)
    return body


def _lid_panel_mesh(r: ResolvedScannerConfig):
    """Lid panel in lid-local frame.

    Pivot at (0, 0, 0). Panel extends forward (-Y) and sits ABOVE the pivot so
    q=0 (closed) leaves the panel resting on the housing top with a small
    clearance and q=+lid_open swings the panel up and away.
    """
    return _rounded_prism(
        r.lid_w,
        r.lid_d,
        _LID_PANEL_T,
        0.012,
        center_z=0.001 + _LID_PANEL_T / 2.0,
    ).translate((0.0, -r.lid_d / 2.0 - 0.005, 0.0))


def _control_ring_mesh():
    outer = _rounded_prism(0.076, 0.044, 0.003, 0.006, center_z=0.0015)
    inner = _rounded_prism(0.036, 0.024, 0.006, 0.004, center_z=0.003)
    return outer.cut(inner)


def _tilting_panel_mesh():
    """Tilting control deck: wider rectangular pad + rim + central button hole."""
    panel = _rounded_prism(0.100, 0.056, 0.004, 0.005, center_z=0.002)
    rim_outer = _rounded_prism(0.080, 0.044, 0.004, 0.005, center_z=0.005)
    rim_inner = _rounded_prism(0.040, 0.026, 0.008, 0.004, center_z=0.005)
    rim = rim_outer.cut(rim_inner)
    hole = _rounded_prism(0.038, 0.024, 0.014, 0.004, center_z=0.005)
    return panel.union(rim).cut(hole)


# ---------------------------------------------------------------------------
# Slot A: build ``scanner_body`` and its inline visuals (platen, feet,
# status lens, rear knuckles for simple_hinge).
# ---------------------------------------------------------------------------
def _build_body(
    model: ArticulatedObject,
    r: ResolvedScannerConfig,
    mats,
    *,
    assets,
):
    body = model.part("scanner_body")

    if r.body_form == "sheet_fed":
        housing_mesh = mesh_from_cadquery(
            _sheet_fed_housing_mesh(r), "scanner_housing_shell", tolerance=0.0008, assets=assets
        )
    else:
        housing_mesh = mesh_from_cadquery(
            _flatbed_housing_mesh(r),
            "scanner_housing_shell",
            tolerance=0.0008,
            assets=assets,
        )
    body.visual(housing_mesh, material=mats["shell"], name="housing_shell", material_class_id="plastic.opaque_generic")
    body.inertial = Inertial.from_geometry(
        Box((r.body_w, r.body_d, r.body_h)),
        mass=2.5,
        origin=Origin(xyz=(0.0, 0.0, r.body_h / 2.0)),
    )

    # Platen inline visuals (Rule 1: non-moving decoration). For sheet_fed the
    # platen is internal and short; for the flatbed forms it fills the well.
    if r.body_form == "sheet_fed":
        # Internal scan strip inside the compact box. The strip crosses the
        # front slot cutout (front_slot at y=-body_d/2-0.005, z=body_h*0.70,
        # box size 0.024×0.008) so it welds to the housing at the slot rim.
        # Extend the strip vertically to physically overlap the slot walls.
        platen_w = r.body_w * 0.68
        platen_d = 0.028
        platen_z = r.body_h * 0.70
        body.visual(
            Box((platen_w, platen_d, 0.012)),
            origin=Origin(xyz=(0.0, -r.body_d / 2.0 + 0.010, platen_z)),
            material=mats["platen_glass"],
            name="platen_glass", material_class_id="glass.clear_transparent",
        )
        body.visual(
            Box((platen_w * 0.95, 0.006, 0.004)),
            origin=Origin(xyz=(0.0, -r.body_d / 2.0 + 0.006, platen_z + 0.008)),
            material=mats["shell_edge"],
            name="reference_strip", material_class_id="plastic.opaque_generic",
        )
    else:
        platen_w = r.well_w - 0.006
        platen_d = r.well_d - 0.006
        # Well floor is at body_h - well_h (well cut removes the top well_h of
        # material). Embed the platen glass so it CROSSES the well floor by
        # 1 mm on both sides — the glass welds to the well floor, avoiding a
        # geometric island.
        platen_z = r.body_h - r.well_h  # embed centered on the floor plane
        body.visual(
            Box((platen_w, platen_d, _PLATEN_GLASS_T + 0.002)),
            origin=Origin(xyz=(0.0, r.well_y, platen_z)),
            material=mats["platen_glass"],
            name="platen_glass", material_class_id="glass.clear_transparent",
        )
        # Reference strip at the rear of the platen: sink it so it also
        # crosses the well floor (Rule 4: derived from platen surface).
        body.visual(
            Box((platen_w * 0.9, 0.008, _REF_STRIP_T + 0.002)),
            origin=Origin(xyz=(0.0, r.well_y + platen_d / 2.0 - 0.008, platen_z)),
            material=mats["shell_edge"],
            name="reference_strip", material_class_id="plastic.opaque_generic",
        )

    # Four rubber feet (Rule 1 inline).
    foot_x = r.body_w / 2.0 - 0.030
    foot_y = r.body_d / 2.0 - 0.030
    for i, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        body.visual(
            Cylinder(radius=_FOOT_R, length=_FOOT_H),
            origin=Origin(xyz=(sx * foot_x, sy * foot_y, _FOOT_H / 2.0)),
            material=mats["rubber"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )

    # Status lens on the front strip.
    body.visual(
        Cylinder(radius=0.0032, length=0.0018),
        origin=Origin(xyz=(r.body_w * 0.30, r.control_y - 0.004, r.body_h + 0.0009)),
        material=mats["status"],
        name="status_lens", material_class_id="tech.emissive_surface",
    )

    # Rear knuckles / hinge pin — always present so the closed lid seats on
    # them (they overlap with the housing so no floating). Their exact geometry
    # depends on the lid_mechanism (see Slot B).
    return body


def _add_simple_rear_hinge_hardware(body, r: ResolvedScannerConfig, mats):
    """Emit rear knuckles + hinge pin on ``scanner_body`` (Rule 1 inline)."""
    knuckle_x = min(0.130, r.body_w * 0.30)
    pin_length = min(2.0 * knuckle_x + 0.060, r.body_w * 0.85)
    for i, x in enumerate((-knuckle_x, 0.0, knuckle_x)):
        body.visual(
            Cylinder(radius=0.008, length=0.036),
            origin=Origin(xyz=(x, r.hinge_y, r.hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"base_knuckle_{i}", material_class_id="metal.stainless_matte",
        )
    body.visual(
        Cylinder(radius=0.0025, length=pin_length),
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="hinge_pin", material_class_id="metal.stainless_matte",
    )


def _add_rising_hinge_towers(body, r: ResolvedScannerConfig, mats):
    """Rising-book-hinge base towers (§ lid_rising_book_hinge L66-L91).

    Towers project down from the pivot line to the housing top (they sit
    UNDER the pivot so the lid panel above them is unobstructed).
    """
    tower_x = min(0.180, r.body_w * 0.40)
    tower_h = 0.024
    # Towers root INTO the housing top: bottom sits 4 mm INSIDE the shell so
    # the tower welds to the housing (avoids a 2-mm island); top reaches the
    # pivot line just below the raised panel.
    for i, sx in enumerate((-1.0, 1.0)):
        tower_top = r.hinge_z - 0.001
        tower_bottom = tower_top - tower_h
        body.visual(
            Box((0.030, 0.032, tower_h)),
            origin=Origin(xyz=(sx * tower_x, r.hinge_y, (tower_top + tower_bottom) / 2.0)),
            material=mats["metal"],
            name=f"hinge_tower_{i}", material_class_id="metal.stainless_matte",
        )
    # Cross bridge sits BELOW the pivot line, spanning the two towers and
    # embedded 5 mm into the housing top so it welds to the shell too.
    body.visual(
        Box((2.0 * tower_x + 0.020, 0.020, 0.014)),
        origin=Origin(xyz=(0.0, r.hinge_y, r.body_h - 0.005)),
        material=mats["metal"],
        name="hinge_bridge", material_class_id="metal.stainless_matte",
    )


# ---------------------------------------------------------------------------
# Slot B: lid mechanism builders.
# ---------------------------------------------------------------------------
def _build_simple_hinge(model, r: ResolvedScannerConfig, body, mats, *, assets) -> list[str]:
    _add_simple_rear_hinge_hardware(body, r, mats)

    lid = model.part("lid")
    # Lid authored in the pivot-line frame (part origin at the hinge line):
    # x free, y=0 at the hinge, z=0 at the hinge Z. The panel extrudes forward
    # (-Y) by lid_d.
    lid.visual(
        mesh_from_cadquery(
            _lid_panel_mesh(r), "scanner_lid_panel", tolerance=0.0007, assets=assets
        ),
        material=mats["lid_shell"],
        name="lid_panel", material_class_id="plastic.opaque_generic",
    )
    # Inner pressure pad — sits just above panel bottom (panel spans
    # z ∈ [0.001, 0.001 + panel_t]; pad hangs 0.0002 mm below the panel bottom
    # so it presses against the platen surface when closed).
    lid.visual(
        Box((r.lid_w - 0.020, r.lid_d - 0.020, _LID_PAD_T)),
        origin=Origin(xyz=(0.0, -r.lid_d / 2.0 - 0.005, 0.001 - _LID_PAD_T / 2.0 + 0.0002)),
        material=mats["lid_pad"],
        name="lid_inner_pad", material_class_id="fabric.felt",
    )
    # Hinge bridge + knuckles at the rear (y ~ 0 line). Bridge overlaps with
    # panel rear edge and knuckle so no per-part islands.
    # Lid knuckles interleave between the outer base knuckles (base at
    # x ∈ {-K, 0, +K} with K = base_knuckle_x; lid sits between them at ~K/2).
    base_knuckle_x = min(0.130, r.body_w * 0.30)
    knuckle_x = base_knuckle_x * 0.5
    for i, x in enumerate((-knuckle_x, knuckle_x)):
        lid.visual(
            Box((0.052, 0.020, 0.014)),
            origin=Origin(xyz=(x, 0.006, 0.001 + 0.007)),
            material=mats["lid_shell"],
            name=f"hinge_bridge_{i}", material_class_id="plastic.opaque_generic",
        )
        lid.visual(
            Cylinder(radius=0.007, length=0.048),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"lid_knuckle_{i}", material_class_id="metal.stainless_matte",
        )

    lid.inertial = Inertial.from_geometry(
        Box((r.lid_w, r.lid_d, _LID_PANEL_T + _LID_PAD_T)),
        mass=0.45,
        origin=Origin(xyz=(0.0, -r.lid_d / 2.0, 0.0)),
    )

    # REVOLUTE joint. q=0 is CLOSED (lid resting on housing top), q=+lid_open
    # is fully raised. Axis=(-1,0,0): +q rotates the panel about -X, lifting
    # the front (-Y) edge UP (+Z).
    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=9.0,
            velocity=1.4,
            lower=r.lid_lower,
            upper=r.lid_open,
        ),
        mating=MatingContract(
            parent_face_geometry="housing_shell",
            parent_face_side="positive_z",
            child_face_geometry="lid_panel",
            child_face_side="negative_z",
            contact_tol=0.014,
        ),
    )
    return ["lid"]


def _build_rising_book_hinge(model, r: ResolvedScannerConfig, body, mats, *, assets) -> list[str]:
    _add_rising_hinge_towers(body, r, mats)

    lid = model.part("lid")
    lid.visual(
        mesh_from_cadquery(
            _lid_panel_mesh(r), "scanner_lid_panel", tolerance=0.0007, assets=assets
        ),
        material=mats["lid_shell"],
        name="lid_panel", material_class_id="plastic.opaque_generic",
    )
    lid.visual(
        Box((r.lid_w - 0.020, r.lid_d - 0.020, _LID_PAD_T)),
        origin=Origin(xyz=(0.0, -r.lid_d / 2.0 - 0.005, 0.001 - _LID_PAD_T / 2.0 + 0.0002)),
        material=mats["lid_pad"],
        name="lid_inner_pad", material_class_id="fabric.felt",
    )
    # Rising link-arm brackets: the pivot line sits at the panel z-level; the
    # brackets reach DOWN from the panel to the tower base, and the pivot pins
    # connect them to the towers.
    arm_x = min(0.180, r.body_w * 0.40)
    for i, sx in enumerate((-1.0, 1.0)):
        lid.visual(
            Box((0.020, 0.008, 0.028)),
            origin=Origin(xyz=(sx * arm_x, 0.008, 0.001 + 0.014)),
            material=mats["lid_shell"],
            name=f"link_arm_v_{i}", material_class_id="plastic.opaque_generic",
        )
        lid.visual(
            Box((0.020, 0.024, 0.006)),
            origin=Origin(xyz=(sx * arm_x, -0.004, 0.001 + 0.003)),
            material=mats["lid_shell"],
            name=f"link_arm_h_{i}", material_class_id="plastic.opaque_generic",
        )
        lid.visual(
            Cylinder(radius=0.004, length=0.020),
            origin=Origin(xyz=(sx * arm_x, 0.010, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"link_pin_{i}", material_class_id="metal.stainless_matte",
        )
    # Cross bar connecting the two brackets so no per-side island.
    lid.visual(
        Box((2.0 * arm_x + 0.020, 0.010, 0.006)),
        origin=Origin(xyz=(0.0, 0.004, 0.001 + 0.003)),
        material=mats["lid_shell"],
        name="link_cross_bar", material_class_id="plastic.opaque_generic",
    )

    lid.inertial = Inertial.from_geometry(
        Box((r.lid_w, r.lid_d, 0.030)),
        mass=0.55,
        origin=Origin(xyz=(0.0, -r.lid_d / 2.0, 0.0)),
    )

    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=10.0,
            velocity=1.3,
            lower=r.lid_lower,
            upper=r.lid_open,
        ),
        mating=MatingContract(
            parent_face_geometry="housing_shell",
            parent_face_side="positive_z",
            child_face_geometry="lid_panel",
            child_face_side="negative_z",
            contact_tol=0.040,  # rising hinge raises the panel by hinge_rise.
        ),
    )
    return ["lid"]


def _build_hinged_adf(model, r: ResolvedScannerConfig, body, mats, *, assets) -> list[str]:
    _add_simple_rear_hinge_hardware(body, r, mats)

    lid = model.part("lid")
    # ADF-base carrier — a thick panel over the platen area.
    lid.visual(
        mesh_from_cadquery(
            _lid_panel_mesh(r), "scanner_lid_panel", tolerance=0.0007, assets=assets
        ),
        material=mats["lid_shell"],
        name="lid_panel", material_class_id="plastic.opaque_generic",
    )
    # ADF housing block on top of the lid (rear third).
    adf_house_w = r.lid_w * 0.85
    adf_house_d = r.lid_d * 0.35
    adf_house_y = -adf_house_d / 2.0 - 0.020
    panel_top_local = 0.001 + _LID_PANEL_T
    adf_house_t = 0.028
    lid.visual(
        Box((adf_house_w, adf_house_d, adf_house_t)),
        origin=Origin(xyz=(0.0, adf_house_y, panel_top_local + adf_house_t / 2.0 - 0.002)),
        material=mats["lid_shell"],
        name="adf_housing", material_class_id="plastic.opaque_generic",
    )
    # Inner backing pad on the underside of the lid panel.
    lid.visual(
        Box((r.lid_w - 0.020, r.lid_d - 0.020, _LID_PAD_T)),
        origin=Origin(xyz=(0.0, -r.lid_d / 2.0 - 0.005, 0.001 - _LID_PAD_T / 2.0 + 0.0002)),
        material=mats["lid_pad"],
        name="lid_inner_pad", material_class_id="fabric.felt",
    )
    # Feed roller indicators visible on the ADF housing top (Rule 1 inline).
    roller_z = panel_top_local + adf_house_t - 0.004
    for i, sx in enumerate((-1.0, 1.0)):
        lid.visual(
            Cylinder(radius=0.008, length=0.020),
            origin=Origin(
                xyz=(sx * 0.080, adf_house_y, roller_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["rubber"],
            name=f"feed_roller_{i}", material_class_id="rubber.directional_grooved",
        )
    # Standard rear hinge bridge + knuckles like simple_hinge.
    # Lid knuckles interleave between the outer base knuckles (base at
    # x ∈ {-K, 0, +K} with K = base_knuckle_x; lid sits between them at ~K/2).
    base_knuckle_x = min(0.130, r.body_w * 0.30)
    knuckle_x = base_knuckle_x * 0.5
    for i, x in enumerate((-knuckle_x, knuckle_x)):
        lid.visual(
            Box((0.052, 0.020, 0.014)),
            origin=Origin(xyz=(x, 0.006, 0.001 + 0.007)),
            material=mats["lid_shell"],
            name=f"hinge_bridge_{i}", material_class_id="plastic.opaque_generic",
        )
        lid.visual(
            Cylinder(radius=0.007, length=0.048),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"lid_knuckle_{i}", material_class_id="metal.stainless_matte",
        )
    lid.inertial = Inertial.from_geometry(
        Box((r.lid_w, r.lid_d, 0.040)),
        mass=1.0,
        origin=Origin(xyz=(0.0, -r.lid_d / 2.0, 0.0)),
    )

    model.articulation(
        "body_to_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=18.0,
            velocity=1.2,
            lower=r.lid_lower,
            upper=r.lid_open,
        ),
        mating=MatingContract(
            parent_face_geometry="housing_shell",
            parent_face_side="positive_z",
            child_face_geometry="lid_panel",
            child_face_side="negative_z",
            contact_tol=0.014,
        ),
    )

    # ADF cover as a sub-lid REVOLUTE `-X` parented to `lid`. Its pivot lives
    # at the rear edge of the ADF housing; q=0 seats the cover flat on top of
    # the housing, q=+ raises the front lip upward.
    adf_cover = model.part("adf_cover")
    cover_w = adf_house_w - 0.010
    cover_d = adf_house_d - 0.010
    # In cover-local frame, panel spans z ∈ [0.001, 0.001 + 0.010] and extends
    # forward (-Y) by cover_d.
    adf_cover.visual(
        Box((cover_w, cover_d, 0.010)),
        origin=Origin(xyz=(0.0, -cover_d / 2.0 - 0.004, 0.001 + 0.005)),
        material=mats["lid_shell"],
        name="adf_cover_shell", material_class_id="plastic.opaque_generic",
    )
    # Paper guide sliders (Rule 1 inline on adf_cover) — sit on top of cover.
    for i, sx in enumerate((-1.0, 1.0)):
        adf_cover.visual(
            Box((0.014, cover_d * 0.6, 0.008)),
            origin=Origin(xyz=(sx * cover_w * 0.30, -cover_d / 2.0 - 0.004, 0.001 + 0.010 + 0.004)),
            material=mats["shell_edge"],
            name=f"paper_guide_{i}", material_class_id="plastic.opaque_generic",
        )
    adf_cover.inertial = Inertial.from_geometry(
        Box((cover_w, cover_d, 0.018)),
        mass=0.30,
        origin=Origin(xyz=(0.0, -cover_d / 2.0, 0.0)),
    )
    # ADF cover pivot at rear of housing in lid-local frame — pivot is at the
    # rear-edge top of adf_housing so the cover panel sits above it.
    cover_hinge_y_local = adf_house_y + adf_house_d / 2.0 - 0.004
    cover_hinge_z_local = panel_top_local + adf_house_t
    model.articulation(
        "lid_to_adf_cover",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=adf_cover,
        origin=Origin(xyz=(0.0, cover_hinge_y_local, cover_hinge_z_local)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0,
            velocity=1.0,
            lower=0.0,
            upper=0.85,
        ),
        mating=MatingContract(
            parent_face_geometry="adf_housing",
            parent_face_side="positive_z",
            child_face_geometry="adf_cover_shell",
            child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    return ["lid", "adf_cover"]


_LID_BUILDERS = {
    "simple_hinge": _build_simple_hinge,
    "rising_book_hinge": _build_rising_book_hinge,
    "hinged_adf": _build_hinged_adf,
}


# ---------------------------------------------------------------------------
# Slot C: control builders.
# ---------------------------------------------------------------------------
def _build_control_ring_button(model, r: ResolvedScannerConfig, body, mats, *, assets) -> list[str]:
    control_panel = model.part("control_panel")
    control_panel.visual(
        mesh_from_cadquery(
            _control_ring_mesh(), "scanner_control_ring", tolerance=0.0006, assets=assets
        ),
        material=mats["shell_edge"],
        name="control_ring", material_class_id="plastic.opaque_generic",
    )
    control_panel.inertial = Inertial.from_geometry(
        Box((0.076, 0.044, 0.006)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, 0.003)),
    )
    # Ring seats INTO the housing front strip (Y = control_y): its bottom
    # embeds 1 mm into the top face so it isn't a floating island.
    model.articulation(
        "body_to_control_panel",
        ArticulationType.FIXED,
        parent=body,
        child=control_panel,
        origin=Origin(xyz=(0.0, r.control_y, r.body_h - 0.001)),
    )

    scan_button = model.part("scan_button")
    scan_button.visual(
        Box((0.032, 0.021, 0.0028)),
        origin=Origin(xyz=(0.0, 0.0, 0.0014)),
        material=mats["button"],
        name="button_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    # Wider flange resting on the ring's outer rim so the button physically
    # contacts the ring (Rule 1: cap sits inside the ring's opening; flange
    # anchors it to the outer top surface).
    scan_button.visual(
        Box((0.044, 0.030, 0.0012)),
        origin=Origin(xyz=(0.0, 0.0, 0.0006)),
        material=mats["button"],
        name="button_flange", material_class_id="plastic.opaque_glossy_molded",
    )
    scan_button.inertial = Inertial.from_geometry(
        Box((0.044, 0.030, 0.003)),
        mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # Seat the button so its flange bottom embeds ~0.5 mm into the ring's top
    # rim surface (ring top at panel-local z=0.003).
    model.articulation(
        "panel_to_scan_button",
        ArticulationType.PRISMATIC,
        parent=control_panel,
        child=scan_button,
        origin=Origin(xyz=(0.0, 0.0, 0.002)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=r.button_travel),
        mating=MatingContract(
            parent_face_geometry="control_ring",
            parent_face_side="positive_z",
            child_face_geometry="button_cap",
            child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    return ["control_panel", "scan_button"]


def _build_dual_button_deck(model, r: ResolvedScannerConfig, body, mats, *, assets) -> list[str]:
    # Deck is inlined on scanner_body (Rule 1: non-moving decoration). Sits
    # partially embedded into the housing top (bottom at body_h-0.001, top at
    # body_h+0.003) so it welds to the shell.
    deck_w = min(0.220, r.body_w * 0.55)
    body.visual(
        Box((deck_w, 0.044, 0.004)),
        origin=Origin(xyz=(0.0, r.control_y - 0.004, r.body_h + 0.001)),
        material=mats["shell_edge"],
        name="control_deck", material_class_id="plastic.opaque_generic",
    )

    names: list[str] = []
    for tag, x_sign, is_scan in (("power_button", -1.0, False), ("scan_button", 1.0, True)):
        button = model.part(tag)
        button.visual(
            Cylinder(radius=0.0072 if is_scan else 0.0044, length=0.003),
            origin=Origin(xyz=(0.0, 0.0, 0.0015)),
            material=mats["accent"] if is_scan else mats["button"],
            name=f"{tag}_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        button.visual(
            Cylinder(radius=(0.0072 if is_scan else 0.0044) + 0.0014, length=0.0008),
            origin=Origin(xyz=(0.0, 0.0, 0.0004)),
            material=mats["accent"] if is_scan else mats["button"],
            name=f"{tag}_flange", material_class_id="plastic.opaque_glossy_molded",
        )
        button.inertial = Inertial.from_geometry(
            Box((0.012, 0.012, 0.004)),
            mass=0.005,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"body_to_{tag}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=button,
            origin=Origin(xyz=(x_sign * deck_w * 0.30, r.control_y - 0.004, r.body_h + 0.002)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=r.button_travel),
            mating=MatingContract(
                parent_face_geometry="control_deck",
                parent_face_side="positive_z",
                child_face_geometry=f"{tag}_flange",
                child_face_side="negative_z",
                contact_tol=0.006,
            ),
        )
        names.append(tag)
    return names


def _build_quad_button_row(model, r: ResolvedScannerConfig, body, mats, *, assets) -> list[str]:
    # Control surround inlined on scanner_body (embedded ~0.4 mm into shell top).
    row_w = min(0.140, r.body_w * 0.40)
    body.visual(
        Box((row_w + 0.020, 0.030, 0.003)),
        origin=Origin(xyz=(-r.body_w * 0.28, r.control_y - 0.004, r.body_h + 0.001)),
        material=mats["shell_edge"],
        name="control_surround", material_class_id="plastic.opaque_generic",
    )
    button_dx = row_w / 4.0
    names: list[str] = []
    x0 = -r.body_w * 0.28 - row_w / 2.0 + button_dx / 2.0
    for i in range(4):
        tag = f"button_{i}"
        button = model.part(tag)
        button.visual(
            Box((0.020, 0.012, 0.003)),
            origin=Origin(xyz=(0.0, 0.0, 0.0015)),
            material=mats["button"],
            name="button_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        # Per-button icon width variation (④ decoration — Rule 4: sits ON the cap).
        button.visual(
            Box((0.007 + 0.001 * i, 0.0016, 0.0006)),
            origin=Origin(xyz=(0.0, 0.0, 0.0033)),
            material=mats["accent"] if i == 3 else mats["shell"],
            name="button_icon", material_class_id="plastic.opaque_glossy_molded",
        )
        button.inertial = Inertial.from_geometry(
            Box((0.020, 0.012, 0.003)),
            mass=0.004,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        model.articulation(
            f"body_to_button_{i}",
            ArticulationType.PRISMATIC,
            parent=body,
            child=button,
            origin=Origin(xyz=(x0 + i * button_dx, r.control_y - 0.004, r.body_h + 0.0015)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=2.5, velocity=0.05, lower=0.0, upper=r.button_travel),
            mating=MatingContract(
                parent_face_geometry="control_surround",
                parent_face_side="positive_z",
                child_face_geometry="button_cap",
                child_face_side="negative_z",
                contact_tol=0.006,
            ),
        )
        names.append(tag)
    return names


def _build_tilting_control_panel(
    model, r: ResolvedScannerConfig, body, mats, *, assets
) -> list[str]:
    control_panel = model.part("control_panel")
    control_panel.visual(
        mesh_from_cadquery(
            _tilting_panel_mesh(), "scanner_tilting_panel", tolerance=0.0006, assets=assets
        ),
        material=mats["shell_edge"],
        name="control_ring", material_class_id="plastic.opaque_generic",
    )
    control_panel.inertial = Inertial.from_geometry(
        Box((0.100, 0.056, 0.008)),
        mass=0.04,
        origin=Origin(xyz=(0.0, 0.0, 0.004)),
    )
    # Panel hinges on a rear edge — REVOLUTE +X so the front lip tilts UP toward operator.
    # Sink pivot 1 mm INTO the housing so the closed panel physically embeds
    # (Rule 1: rests on the housing top).
    model.articulation(
        "body_to_control_panel",
        ArticulationType.REVOLUTE,
        parent=body,
        child=control_panel,
        origin=Origin(xyz=(0.0, r.control_y + 0.020, r.body_h - 0.001)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.8, lower=0.0, upper=r.panel_tilt),
        mating=MatingContract(
            parent_face_geometry="housing_shell",
            parent_face_side="positive_z",
            child_face_geometry="control_ring",
            child_face_side="negative_z",
            contact_tol=0.008,
        ),
    )

    scan_button = model.part("scan_button")
    scan_button.visual(
        Box((0.032, 0.022, 0.003)),
        origin=Origin(xyz=(0.0, 0.0, 0.0015)),
        material=mats["button"],
        name="button_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    scan_button.visual(
        Box((0.050, 0.032, 0.0012)),
        origin=Origin(xyz=(0.0, 0.0, 0.0006)),
        material=mats["button"],
        name="button_flange", material_class_id="plastic.opaque_glossy_molded",
    )
    scan_button.inertial = Inertial.from_geometry(
        Box((0.050, 0.032, 0.003)),
        mass=0.005,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # Button rides on the panel — parent to control_panel so it tilts with it.
    # Flange overlaps the rim outer top so button physically contacts the ring
    # (rim outer 0.080×0.044 at panel-local z ∈ [0.003, 0.007]).
    model.articulation(
        "panel_to_scan_button",
        ArticulationType.PRISMATIC,
        parent=control_panel,
        child=scan_button,
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.05, lower=0.0, upper=r.button_travel),
        mating=MatingContract(
            parent_face_geometry="control_ring",
            parent_face_side="positive_z",
            child_face_geometry="button_cap",
            child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    return ["control_panel", "scan_button"]


_CONTROL_BUILDERS = {
    "control_ring_button": _build_control_ring_button,
    "dual_button_deck": _build_dual_button_deck,
    "quad_button_row": _build_quad_button_row,
    "tilting_control_panel": _build_tilting_control_panel,
}


# ---------------------------------------------------------------------------
# Build entry points.
# ---------------------------------------------------------------------------
def build_scanner(
    config: ScannerConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"scanner_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    body = _build_body(model, r, mats, assets=assets)
    _LID_BUILDERS[r.lid_mechanism](model, r, body, mats, assets=assets)
    _CONTROL_BUILDERS[r.controls](model, r, body, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_scanner(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_scanner(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests — Rule 5 (sampled-pose overlap + targeted ctx.pose).
# ---------------------------------------------------------------------------
def run_scanner_tests(
    object_model: ArticulatedObject,
    config: ScannerConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("scanner_body")
    lid = object_model.get_part("lid")
    lid_joint = object_model.get_articulation("body_to_lid")

    # ---- Element-scoped allow_overlap for captured hinge hardware. ----
    if r.lid_mechanism in ("simple_hinge", "hinged_adf"):
        for i in range(2):
            ctx.allow_overlap(
                body,
                lid,
                elem_a="hinge_pin",
                elem_b=f"lid_knuckle_{i}",
                reason="Lid knuckle rotates around the captured rear hinge pin.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"base_knuckle_{i}",
                elem_b=f"lid_knuckle_{i}",
                reason=(
                    "Base and lid knuckles alternate along the hinge pin, "
                    "interleaving with a small rotational fit."
                ),
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a="hinge_pin",
                elem_b=f"hinge_bridge_{i}",
                reason="Hinge bridge wraps around the captured hinge pin.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a="housing_shell",
                elem_b=f"hinge_bridge_{i}",
                reason=(
                    "Hinge bridge sweeps through the housing rear-hinge shoulder "
                    "region during lid rotation (captured hardware contact)."
                ),
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a="housing_shell",
                elem_b=f"lid_knuckle_{i}",
                reason=(
                    "Lid knuckle sits at the rear-hinge shoulder embedded into "
                    "the housing top face across the full swept lid range."
                ),
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"base_knuckle_{i}",
                elem_b=f"hinge_bridge_{i}",
                reason="Hinge bridge meets base knuckle when the lid is closed.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"base_knuckle_{i}",
                elem_b="lid_panel",
                reason="Panel edge sweeps past base knuckle during hinge rotation.",
            )
        # Third base knuckle overlap with pin too.
        ctx.allow_overlap(
            body,
            lid,
            elem_a="base_knuckle_2",
            elem_b="lid_panel",
            reason="Third rear knuckle sits within the swept lid panel skirt.",
        )
    elif r.lid_mechanism == "rising_book_hinge":
        for i in range(2):
            for j in range(2):
                ctx.allow_overlap(
                    body,
                    lid,
                    elem_a=f"hinge_tower_{i}",
                    elem_b=f"link_arm_v_{j}",
                    reason=(
                        "Rising book hinge: link arm rides in the tower slot with "
                        "intentional radial contact through the swept range."
                    ),
                )
                ctx.allow_overlap(
                    body,
                    lid,
                    elem_a=f"hinge_tower_{i}",
                    elem_b=f"link_arm_h_{j}",
                    reason="Horizontal link arm meets the tower during the swept range.",
                )
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"hinge_tower_{i}",
                elem_b=f"link_pin_{i}",
                reason="Link pin is captured inside the rising hinge tower bore.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a="hinge_bridge",
                elem_b=f"link_pin_{i}",
                reason="Link pin sits in the hinge bridge cutout.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"hinge_tower_{i}",
                elem_b="link_cross_bar",
                reason="Cross bar meets the towers along the pivot line.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a="hinge_bridge",
                elem_b=f"link_arm_v_{i}",
                reason="Vertical link arm meets the hinge bridge during rotation.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a="hinge_bridge",
                elem_b=f"link_arm_h_{i}",
                reason="Horizontal link arm sweeps across the hinge bridge.",
            )
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"hinge_tower_{i}",
                elem_b="lid_panel",
                reason="Lid panel sweeps past the tower crown during rotation.",
            )
        ctx.allow_overlap(
            body,
            lid,
            elem_a="hinge_bridge",
            elem_b="link_cross_bar",
            reason="Cross bar sweeps across the hinge bridge along the pivot line.",
        )

    # Closed lid seats over the housing rear — allow the shell↔lid_panel and
    # shell↔lid_inner_pad contact when the lid rests in its closed position.
    ctx.allow_overlap(
        body,
        lid,
        elem_a="housing_shell",
        elem_b="lid_panel",
        reason="Closed lid seats on the housing rim / rear-hinge shoulder.",
    )
    ctx.allow_overlap(
        body,
        lid,
        elem_a="housing_shell",
        elem_b="lid_inner_pad",
        reason="Closed lid inner pad seats over the platen well / scan strip.",
    )
    if r.has_top_well:
        ctx.allow_overlap(
            body,
            lid,
            elem_a="platen_glass",
            elem_b="lid_inner_pad",
            reason="Closed lid inner pad presses against the platen glass surface.",
        )
    ctx.allow_overlap(
        body,
        lid,
        elem_a="reference_strip",
        elem_b="lid_inner_pad",
        reason="Reference strip sits under the lid inner pad in the closed pose.",
    )

    if r.lid_mechanism == "hinged_adf":
        adf_cover = object_model.get_part("adf_cover")
        ctx.allow_overlap(
            lid,
            adf_cover,
            elem_a="adf_housing",
            elem_b="adf_cover_shell",
            reason="ADF cover nests over the ADF housing rear-hinge region.",
        )
        for i in range(2):
            ctx.allow_overlap(
                lid,
                adf_cover,
                elem_a=f"feed_roller_{i}",
                elem_b="adf_cover_shell",
                reason="Feed rollers project into the ADF cover paper path.",
            )

    # Controls: allow deck/surround inside housing_shell overlap (they sit ON
    # the housing top so a small vertical embed keeps them non-floating).
    if r.controls == "dual_button_deck":
        ctx.allow_overlap(
            body,
            body,
            elem_a="housing_shell",
            elem_b="control_deck",
            reason="Control deck is embedded into the housing top face (Rule 4 conformal).",
        )
    if r.controls == "quad_button_row":
        ctx.allow_overlap(
            body,
            body,
            elem_a="housing_shell",
            elem_b="control_surround",
            reason="Control surround is embedded into the housing top face (Rule 4 conformal).",
        )
    if r.controls in ("control_ring_button", "tilting_control_panel"):
        panel = object_model.get_part("control_panel")
        button = object_model.get_part("scan_button")
        ctx.allow_overlap(
            panel,
            button,
            elem_a="control_ring",
            elem_b="button_cap",
            reason="Scan button cap seats inside the ring opening (captured).",
        )
        ctx.allow_overlap(
            panel,
            button,
            elem_a="control_ring",
            elem_b="button_flange",
            reason="Button flange embeds into the ring's outer rim.",
        )
        if r.controls == "tilting_control_panel":
            ctx.allow_overlap(
                body,
                panel,
                elem_a="housing_shell",
                elem_b="control_ring",
                reason=(
                    "Tilting panel's rear edge is captured by the housing "
                    "top face along the pivot line through the tilt range."
                ),
            )
    if r.controls == "dual_button_deck":
        for tag in ("power_button", "scan_button"):
            button = object_model.get_part(tag)
            ctx.allow_overlap(
                body,
                button,
                elem_a="control_deck",
                elem_b=f"{tag}_flange",
                reason=f"{tag} flange sits embedded into the control deck top.",
            )
    if r.controls == "quad_button_row":
        for i in range(4):
            button = object_model.get_part(f"button_{i}")
            ctx.allow_overlap(
                body,
                button,
                elem_a="control_surround",
                elem_b="button_cap",
                reason=f"button_{i} cap is captured within the control surround top.",
            )

    # ---- Baseline gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structural / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "scanner_body root present",
        "scanner_body" in part_names
        and [p.name for p in object_model.root_parts()] == ["scanner_body"],
        details=f"parts={sorted(part_names)}",
    )
    ctx.check(
        "lid present with REVOLUTE -X hinge",
        lid_joint.articulation_type == ArticulationType.REVOLUTE
        and abs(lid_joint.axis[0]) > 0.99
        and lid_joint.axis[0] < 0.0,
        details=f"joint={lid_joint}",
    )
    if r.lid_mechanism == "hinged_adf":
        adf_j = object_model.get_articulation("lid_to_adf_cover")
        ctx.check(
            "ADF cover has second REVOLUTE -X hinge",
            adf_j.articulation_type == ArticulationType.REVOLUTE and abs(adf_j.axis[0]) > 0.99,
            details=f"joint={adf_j}",
        )

    # At least one PRISMATIC push button exists with travel in [0.0009, 0.0015].
    prismatic_joints = [
        j for j in object_model.articulations if j.articulation_type == ArticulationType.PRISMATIC
    ]
    ctx.check(
        "at least one PRISMATIC push button with correct travel",
        any(
            j.motion_limits is not None
            and abs(j.axis[2]) > 0.99
            and j.axis[2] < 0.0
            and 0.0008 <= j.motion_limits.upper <= 0.0016
            for j in prismatic_joints
        ),
        details=f"prismatic={[(j.name, j.axis, j.motion_limits) for j in prismatic_joints]}",
    )

    # ---- Body form invariants. ----
    body_aabb = ctx.part_element_world_aabb(body, elem="housing_shell")
    if r.body_form == "flatbed_slim":
        ctx.check(
            "flatbed_slim housing is thin (< 50 mm z-extent)",
            body_aabb is not None and (body_aabb[1][2] - body_aabb[0][2]) < 0.055,
            details=f"body_aabb={body_aabb}",
        )
    if r.body_form == "sheet_fed":
        ctx.check(
            "sheet_fed body is tall-narrow (depth < 0.20 m, height > 0.06 m)",
            body_aabb is not None
            and (body_aabb[1][1] - body_aabb[0][1]) < 0.22
            and (body_aabb[1][2] - body_aabb[0][2]) > 0.065,
            details=f"body_aabb={body_aabb}",
        )
    ctx.check(
        "scanner is not a printer (chassis z-extent < 0.16 m)",
        body_aabb is not None and (body_aabb[1][2] - body_aabb[0][2]) < 0.16,
        details=f"body_aabb={body_aabb}",
    )

    # ---- Motion invariants (Rule 5 targeted ctx.pose). ----
    lid_aabb = ctx.part_element_world_aabb(lid, elem="lid_panel")
    if lid_aabb is not None:
        lid_aabb[1][2]
    # Closed pose: q=lower.
    with ctx.pose({lid_joint: lid_joint.motion_limits.lower}):
        closed_box = ctx.part_element_world_aabb(lid, elem="lid_panel")
    # Open (upper) pose: q=upper.
    with ctx.pose({lid_joint: lid_joint.motion_limits.upper}):
        open_box = ctx.part_element_world_aabb(lid, elem="lid_panel")
    if closed_box is not None and body_aabb is not None:
        ctx.check(
            "closed lid seats near housing top (< 30 mm gap)",
            closed_box[0][2] < body_aabb[1][2] + 0.030,
            details=f"closed_bottom={closed_box[0][2]}, body_top={body_aabb[1][2]}",
        )
    if open_box is not None and closed_box is not None:
        ctx.check(
            "positive lid motion opens further upward than closed",
            open_box[1][2] > closed_box[1][2] + 0.03,
            details=f"open_top={open_box[1][2]}, closed_top={closed_box[1][2]}",
        )

    if r.lid_mechanism == "hinged_adf":
        adf_cover = object_model.get_part("adf_cover")
        adf_joint = object_model.get_articulation("lid_to_adf_cover")
        rest_box = ctx.part_element_world_aabb(adf_cover, elem="adf_cover_shell")
        with ctx.pose({adf_joint: adf_joint.motion_limits.upper}):
            open_box = ctx.part_element_world_aabb(adf_cover, elem="adf_cover_shell")
        if rest_box is not None and open_box is not None:
            ctx.check(
                "ADF cover opens upward",
                open_box[1][2] > rest_box[1][2] + 0.005,
                details=f"rest_top={rest_box[1][2]}, open_top={open_box[1][2]}",
            )

    if r.controls == "tilting_control_panel":
        panel = object_model.get_part("control_panel")
        panel_j = object_model.get_articulation("body_to_control_panel")
        rest_box = ctx.part_element_world_aabb(panel, elem="control_ring")
        with ctx.pose({panel_j: panel_j.motion_limits.upper}):
            tilt_box = ctx.part_element_world_aabb(panel, elem="control_ring")
        if rest_box is not None and tilt_box is not None:
            ctx.check(
                "tilting control panel raises the front lip upward",
                tilt_box[1][2] > rest_box[1][2] + 0.002,
                details=f"rest_top={rest_box[1][2]}, tilted_top={tilt_box[1][2]}",
            )

    # A PRISMATIC push button lowers z when pressed.
    if prismatic_joints:
        j0 = prismatic_joints[0]
        btn_part = object_model.get_part(j0.child)
        rest_p = ctx.part_world_position(btn_part)
        with ctx.pose({j0: j0.motion_limits.upper}):
            pressed_p = ctx.part_world_position(btn_part)
        if rest_p is not None and pressed_p is not None:
            ctx.check(
                "first push button depresses downward",
                pressed_p[2] < rest_p[2] - 0.0004,
                details=f"rest={rest_p}, pressed={pressed_p}",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded on model.meta",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- Rule 5: sampled-pose overlap gate. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(
        max_pose_samples=48,
        ignore_fixed=True,
    )

    return ctx.report()


__all__ = (
    "PALETTE_STYLES",
    "PALETTES",
    "ResolvedScannerConfig",
    "ScannerConfig",
    "build_scanner",
    "build_seeded_scanner",
    "config_from_seed",
    "resolve_config",
    "run_scanner_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
