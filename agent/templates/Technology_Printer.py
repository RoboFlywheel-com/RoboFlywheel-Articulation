# SPDX-License-Identifier: Apache-2.0

"""Technology / Printer (inkjet all-in-one) — modular procedural template.

Category identity: a grounded plastic print-engine housing (``body``) carrying, as
parallel children, an optional REVOLUTE flatbed/ADF scanner lid on top, a PRISMATIC
or fold-out REVOLUTE paper-handling tray at the front/rear, and a control panel
(PRISMATIC push-button strip, fixed flush touchscreen, or REVOLUTE tilting panel).

Three slots (``slot_choices_for_seed``): form_family, paper_handling, control_panel
plus a ``button_count`` multiplicity axis on the flat button strip.

Derived from 9 rating-5 sources (see the spec). Parallel-children pattern, mirroring
``dishwasher_with_dropdown_door_and_sliding_racks`` (dropdown door REVOLUTE + sliding
racks PRISMATIC -> scanner-lid REVOLUTE + fold-out trays PRISMATIC).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/Technology_Printer.md``

Frame: X = width, Y = depth (front = -Y, rear = +Y), Z = height (body bottom z = 0).
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

FormFamily = Literal[
    "flatbed_scanner_top",
    "adf_document_feeder_top",
    "flat_top_no_scanner",
    "tall_workgroup_body",
    "ink_tank_supertank",
    "wide_format_extra",
]
PaperHandling = Literal[
    "rear_feed_output_extension",
    "front_cassette_drawer",
    "front_output_tray_stopper",
    "foldout_rear_input",
]
ControlPanel = Literal[
    "flat_button_strip",
    "fixed_flush_touchscreen",
    "tilting_touchscreen_panel",
]
PaletteStyle = Literal[
    "warm_white",
    "office_white_gray",
    "brother_offwhite",
    "charcoal_workgroup",
    "supertank_white",
    "graphite_two_tone",
]

FORM_FAMILIES: tuple[FormFamily, ...] = (
    "flatbed_scanner_top",
    "adf_document_feeder_top",
    "flat_top_no_scanner",
    "tall_workgroup_body",
    "ink_tank_supertank",
    "wide_format_extra",
)
PAPER_HANDLINGS: tuple[PaperHandling, ...] = (
    "rear_feed_output_extension",
    "front_cassette_drawer",
    "front_output_tray_stopper",
    "foldout_rear_input",
)
CONTROL_PANELS: tuple[ControlPanel, ...] = (
    "flat_button_strip",
    "fixed_flush_touchscreen",
    "tilting_touchscreen_panel",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_white",
    "office_white_gray",
    "brother_offwhite",
    "charcoal_workgroup",
    "supertank_white",
    "graphite_two_tone",
)

MIN_BUTTONS = 2
MAX_BUTTONS = 8

# Per-form base envelope (before scale) + top-structure descriptor.
_FORM_SPEC: dict[FormFamily, dict] = {
    "flatbed_scanner_top": dict(bw=0.42, bd=0.34, bh=0.150, shell="rounded", lid="flatbed"),
    "adf_document_feeder_top": dict(bw=0.48, bd=0.40, bh=0.170, shell="boxy", lid="adf"),
    "flat_top_no_scanner": dict(bw=0.42, bd=0.33, bh=0.145, shell="rounded", lid=None, domed=True),
    "tall_workgroup_body": dict(bw=0.48, bd=0.40, bh=0.285, shell="boxy", lid="adf", base_band=True),
    "ink_tank_supertank": dict(bw=0.42, bd=0.35, bh=0.150, shell="rounded", lid="flatbed", tank=True),
    "wide_format_extra": dict(bw=0.56, bd=0.42, bh=0.135, shell="rounded", lid="flatbed", wide=True),
}

# Six colorways. Semantic keys -> rgba. Translucent CMYK inks are added separately.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_white": {
        "body": (0.94, 0.94, 0.92, 1.0),
        "base": (0.70, 0.72, 0.72, 1.0),
        "panel": (0.72, 0.73, 0.73, 1.0),
        "dark": (0.06, 0.065, 0.065, 1.0),
        "accent": (0.78, 0.95, 0.02, 1.0),
        "glass": (0.30, 0.42, 0.50, 1.0),
        "paper": (0.985, 0.985, 0.965, 1.0),
        "screen": (0.06, 0.14, 0.24, 1.0),
        "lid": (0.92, 0.92, 0.90, 1.0),
        "badge": (0.18, 0.44, 0.76, 1.0),
    },
    "office_white_gray": {
        "body": (0.92, 0.93, 0.91, 1.0),
        "base": (0.16, 0.17, 0.17, 1.0),
        "panel": (0.05, 0.055, 0.06, 1.0),
        "dark": (0.02, 0.025, 0.03, 1.0),
        "accent": (0.0, 0.65, 0.95, 1.0),
        "glass": (0.03, 0.05, 0.08, 1.0),
        "paper": (0.96, 0.94, 0.88, 1.0),
        "screen": (0.05, 0.12, 0.22, 1.0),
        "lid": (0.64, 0.66, 0.65, 1.0),
        "badge": (0.45, 0.47, 0.47, 1.0),
    },
    "brother_offwhite": {
        "body": (0.91, 0.90, 0.87, 1.0),
        "base": (0.52, 0.53, 0.55, 1.0),
        "panel": (0.78, 0.78, 0.77, 1.0),
        "dark": (0.12, 0.12, 0.14, 1.0),
        "accent": (0.40, 0.40, 0.43, 1.0),
        "glass": (0.28, 0.40, 0.48, 1.0),
        "paper": (0.98, 0.98, 0.96, 1.0),
        "screen": (0.08, 0.16, 0.24, 1.0),
        "lid": (0.55, 0.56, 0.58, 1.0),
        "badge": (0.35, 0.36, 0.38, 1.0),
    },
    "charcoal_workgroup": {
        "body": (0.20, 0.21, 0.22, 1.0),
        "base": (0.07, 0.075, 0.08, 1.0),
        "panel": (0.10, 0.10, 0.12, 1.0),
        "dark": (0.03, 0.03, 0.035, 1.0),
        "accent": (0.10, 0.72, 0.35, 1.0),
        "glass": (0.10, 0.20, 0.28, 1.0),
        "paper": (0.94, 0.93, 0.90, 1.0),
        "screen": (0.06, 0.16, 0.26, 1.0),
        "lid": (0.30, 0.31, 0.33, 1.0),
        "badge": (0.70, 0.72, 0.74, 1.0),
    },
    "supertank_white": {
        "body": (0.95, 0.95, 0.94, 1.0),
        "base": (0.60, 0.62, 0.63, 1.0),
        "panel": (0.74, 0.75, 0.75, 1.0),
        "dark": (0.10, 0.10, 0.12, 1.0),
        "accent": (0.05, 0.55, 0.75, 1.0),
        "glass": (0.30, 0.42, 0.50, 1.0),
        "paper": (0.985, 0.985, 0.965, 1.0),
        "screen": (0.06, 0.14, 0.24, 1.0),
        "lid": (0.90, 0.90, 0.88, 1.0),
        "badge": (0.20, 0.30, 0.40, 1.0),
    },
    "graphite_two_tone": {
        "body": (0.80, 0.81, 0.82, 1.0),
        "base": (0.18, 0.19, 0.20, 1.0),
        "panel": (0.06, 0.06, 0.07, 1.0),
        "dark": (0.03, 0.03, 0.035, 1.0),
        "accent": (0.90, 0.45, 0.05, 1.0),
        "glass": (0.10, 0.18, 0.26, 1.0),
        "paper": (0.95, 0.94, 0.91, 1.0),
        "screen": (0.05, 0.12, 0.22, 1.0),
        "lid": (0.30, 0.31, 0.33, 1.0),
        "badge": (0.85, 0.86, 0.88, 1.0),
    },
}

# Translucent CMYK ink-window colors (ink_tank form), palette-independent.
_INK_RGBA = (
    (0.08, 0.08, 0.10, 0.55),
    (0.05, 0.75, 0.90, 0.55),
    (0.85, 0.10, 0.55, 0.55),
    (0.95, 0.85, 0.05, 0.55),
)


@dataclass(frozen=True)
class PrinterConfig:
    form_family: FormFamily | None = None
    paper_handling: PaperHandling | None = None
    control_panel: ControlPanel | None = None
    button_count: int = 4
    palette_style: PaletteStyle = "warm_white"
    width_scale: float = 1.0
    depth_scale: float = 1.0
    height_scale: float = 1.0
    lid_open_scale: float = 1.0
    name: str = "printer"


@dataclass(frozen=True)
class ResolvedPrinterConfig:
    form_family: FormFamily
    paper_handling: PaperHandling
    control_panel: ControlPanel
    button_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    bw: float
    bd: float
    bh: float
    body_top: float
    front_y: float
    rear_y: float
    shell: str
    lid_style: str | None
    domed: bool
    base_band: bool
    tank: bool
    lid_upper: float
    tray_travel: float
    slot_z: float
    cassette_z: float
    panel_z: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def config_from_seed(seed: int) -> PrinterConfig:
    """Deterministic procedural sampling. seed=0 is NOT special."""
    rng = random.Random(seed)
    form = rng.choice(FORM_FAMILIES)
    paper = rng.choice(PAPER_HANDLINGS)
    panel = rng.choice(CONTROL_PANELS)
    n = rng.randint(MIN_BUTTONS, MAX_BUTTONS) if panel == "flat_button_strip" else 0
    return PrinterConfig(
        form_family=form,
        paper_handling=paper,
        control_panel=panel,
        button_count=n,
        palette_style=rng.choice(PALETTE_STYLES),
        width_scale=round(rng.uniform(0.90, 1.12), 3),
        depth_scale=round(rng.uniform(0.92, 1.10), 3),
        height_scale=round(rng.uniform(0.92, 1.12), 3),
        lid_open_scale=round(rng.uniform(0.85, 1.0), 3),
        name=f"seeded_printer_{seed}",
    )


def resolve_config(config: PrinterConfig) -> ResolvedPrinterConfig:
    form = config.form_family or "flatbed_scanner_top"
    paper = config.paper_handling or "front_output_tray_stopper"
    panel = config.control_panel or "flat_button_strip"
    if form not in FORM_FAMILIES:
        raise ValueError(f"Unsupported form_family: {form}")
    if paper not in PAPER_HANDLINGS:
        raise ValueError(f"Unsupported paper_handling: {paper}")
    if panel not in CONTROL_PANELS:
        raise ValueError(f"Unsupported control_panel: {panel}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    spec = _FORM_SPEC[form]
    ws = _clamp(config.width_scale, 0.90, 1.12)
    ds = _clamp(config.depth_scale, 0.92, 1.10)
    hs = _clamp(config.height_scale, 0.92, 1.12)

    bw = round(spec["bw"] * ws, 4)
    bd = round(spec["bd"] * ds, 4)
    bh = round(spec["bh"] * hs, 4)
    if spec.get("base_band"):
        bh = max(bh, 0.26)

    body_top = bh
    front_y = -bd / 2.0
    rear_y = bd / 2.0

    n = int(config.button_count) if panel == "flat_button_strip" else 0
    if panel == "flat_button_strip":
        n = int(_clamp(n, MIN_BUTTONS, MAX_BUTTONS))

    lid_upper = round(1.20 * _clamp(config.lid_open_scale, 0.85, 1.0), 3)
    tray_travel = round(min(0.16, bd * 0.42) * ds, 4)
    slot_z = round(min(0.058, body_top * 0.38), 4)
    cassette_z = 0.024
    panel_z = round(body_top - 0.032, 4)

    return ResolvedPrinterConfig(
        form_family=form,
        paper_handling=paper,
        control_panel=panel,
        button_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        bw=bw,
        bd=bd,
        bh=bh,
        body_top=body_top,
        front_y=front_y,
        rear_y=rear_y,
        shell=spec["shell"],
        lid_style=spec.get("lid"),
        domed=bool(spec.get("domed")),
        base_band=bool(spec.get("base_band")),
        tank=bool(spec.get("tank")),
        lid_upper=lid_upper,
        tray_travel=tray_travel,
        slot_z=slot_z,
        cassette_z=cassette_z,
        panel_z=panel_z,
        name=config.name,
    )


def _box(part: Part, name: str, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.opaque_generic")


def _cyl(part: Part, name: str, radius: float, length: float, xyz, material,
         rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="plastic.opaque_generic",
    )


def _rounded_shell(bw: float, bd: float, bh: float) -> cq.Workplane:
    """Rounded compact housing with a front output-bay cut (DeskJet/Brother)."""
    b = cq.Workplane("XY").box(bw, bd, bh).edges("|Z").fillet(min(0.028, bh * 0.18))
    bay = (
        cq.Workplane("XY")
        .box(bw * 0.70, 0.09, bh * 0.42)
        .translate((0.0, -bd * 0.5 + 0.02, -bh * 0.02))
    )
    return b.cut(bay)


def _domed_deck(bw: float, bd: float) -> cq.Workplane:
    """Slightly domed closed top deck (single-function form)."""
    deck = cq.Workplane("XY").box(bw * 0.94, bd * 0.90, 0.012).edges("|Z").fillet(0.024)
    return deck.edges(">Z").fillet(0.003)


def _build_body(model: ArticulatedObject, r: ResolvedPrinterConfig, mats: dict) -> Part:
    bw, bd, bh = r.bw, r.bd, r.bh
    body = model.part("body")

    if r.shell == "rounded":
        body.visual(
            mesh_from_cadquery(_rounded_shell(bw, bd, bh), "body_shell", tolerance=0.0012),
            origin=Origin(xyz=(0.0, 0.0, bh / 2.0)),
            material=mats["body"],
            name="body_shell", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        _box(body, "body_shell", (bw, bd, bh), (0.0, 0.0, bh / 2.0), mats["body"])

    if r.base_band:
        _box(body, "base_band", (bw + 0.004, bd + 0.004, 0.11),
             (0.0, 0.0, 0.055), mats["base"])

    _box(body, "output_shadow", (bw * 0.72, 0.006, 0.030),
         (0.0, r.front_y + 0.004, r.slot_z), mats["dark"])

    _box(body, "brand_plate", (bw * 0.14, 0.004, 0.012),
         (-bw * 0.32, r.front_y + 0.001, r.body_top - 0.020), mats["base"])
    # straddle the front face (half embedded for support, half proud for visibility)
    _cyl(body, "badge_roundel", 0.014, 0.008,
         (bw * 0.30, r.front_y, r.body_top - 0.020), mats["badge"],
         rpy=(math.pi / 2.0, 0.0, 0.0))

    if r.lid_style is not None:
        _box(body, "scanner_glass", (bw * 0.80, bd * 0.78, 0.004),
             (0.0, -bd * 0.02, r.body_top - 0.002), mats["glass"])

    if r.domed:
        body.visual(
            mesh_from_cadquery(_domed_deck(bw, bd), "top_deck", tolerance=0.0012),
            origin=Origin(xyz=(0.0, 0.0, r.body_top + 0.006)),
            material=mats["body"],
            name="top_deck", material_class_id="plastic.opaque_glossy_molded",
        )

    if r.tank:
        tw, td, th = 0.062, bd * 0.46, bh * 0.72
        tx = bw / 2.0 + tw / 2.0 - 0.006
        tz = th / 2.0 + 0.010
        _box(body, "tank_housing", (tw, td, th), (tx, 0.0, tz), mats["dark"])
        win_h = th - 0.028
        for i, rgba in enumerate(_INK_RGBA):
            m = model.material(f"ink_{i}", rgba=rgba)
            wx = tx - tw / 2.0 + 0.010 + (tw - 0.020) / 4.0 * (i + 0.5)
            _box(body, f"tank_window_{i}", ((tw - 0.024) / 4.0, 0.004, win_h),
                 (wx, -td / 2.0 + 0.002, tz), m)
            _cyl(body, f"tank_cap_{i}", 0.007, 0.006,
                 (tx - 0.020 + 0.013 * i, 0.0, th + 0.010 + 0.003), mats["dark"])

    return body


def _build_scanner_lid(model: ArticulatedObject, body: Part, r: ResolvedPrinterConfig,
                       mats: dict) -> None:
    if r.lid_style is None:
        return
    bw, bd = r.bw, r.bd
    span = bd - 0.014
    lid = model.part("scanner_lid")

    if r.lid_style == "flatbed":
        lid_h = 0.022
        _box(lid, "lid_frame", (bw - 0.014, span, lid_h),
             (0.0, -span / 2.0, lid_h / 2.0 - 0.003), mats["lid"])
        _box(lid, "cover_top", (bw - 0.040, span - 0.026, 0.004),
             (0.0, -span / 2.0, lid_h - 0.003), mats["base"])
        _cyl(lid, "hinge_barrel", 0.006, bw * 0.70,
             (0.0, 0.0, 0.005), mats["lid"], rpy=(0.0, math.pi / 2.0, 0.0))
    else:
        _box(lid, "lid_slab", (bw, bd, 0.025), (0.0, -bd / 2.0, 0.0125 - 0.003), mats["lid"])
        _box(lid, "adf_upper_cover", (bw * 0.90, bd * 0.52, 0.042),
             (0.0, -bd * 0.42, 0.045), mats["base"])
        _box(lid, "adf_top_tray", (bw * 0.72, bd * 0.30, 0.012),
             (0.0, -bd * 0.30, 0.070), mats["lid"])
        _box(lid, "adf_feed_lip", (bw * 0.82, 0.030, 0.016),
             (0.0, -bd * 0.60, 0.030), mats["base"])
        _box(lid, "adf_rear_hinge_strip", (bw * 0.95, 0.018, 0.018),
             (0.0, -0.006, 0.018), mats["base"])

    model.articulation(
        "body_to_scanner_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, r.rear_y - 0.006, r.body_top)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.6, lower=0.0, upper=r.lid_upper),
    )


def _front_output_shelf(body: Part, r: ResolvedPrinterConfig, mats: dict) -> None:
    _box(body, "output_shelf", (r.bw * 0.74, 0.10, 0.010),
         (0.0, r.front_y - 0.045, r.slot_z), mats["base"])


def _build_paper_handling(model: ArticulatedObject, body: Part, r: ResolvedPrinterConfig,
                          mats: dict) -> None:
    bw, bd = r.bw, r.bd

    if r.paper_handling == "rear_feed_output_extension":
        _box(body, "rear_feed_base", (bw * 0.70, 0.026, 0.010),
             (0.0, r.rear_y + 0.013, r.body_top + 0.005), mats["body"])
        _box(body, "rear_feed_upright", (bw * 0.66, 0.012, 0.19),
             (0.0, r.rear_y + 0.004, r.body_top + 0.100), mats["body"])
        _box(body, "rear_feed_paper", (bw * 0.55, 0.003, 0.17),
             (0.0, r.rear_y - 0.001, r.body_top + 0.100), mats["paper"])
        _front_output_shelf(body, r, mats)
        ext = model.part("extension_arm")
        _box(ext, "extension_plate", (bw * 0.62, 0.11, 0.006), (0.0, -0.060, 0.0), mats["accent"])
        # retain lip straddles the body front face so the collapsed arm overlaps body_shell
        _box(ext, "extension_lip", (bw * 0.62, 0.030, 0.008), (0.0, 0.006, -0.003), mats["accent"])
        model.articulation(
            "body_to_extension_arm", ArticulationType.PRISMATIC, parent=body, child=ext,
            origin=Origin(xyz=(0.0, r.front_y + 0.005, r.slot_z + 0.006)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=0.15, lower=0.0, upper=r.tray_travel),
        )

    elif r.paper_handling == "front_cassette_drawer":
        _front_output_shelf(body, r, mats)
        tray = model.part("input_tray")
        _box(tray, "tray_floor", (bw * 0.52, bd * 0.94, 0.012), (0.0, bd * 0.46, 0.006), mats["base"])
        _box(tray, "tray_side_l", (0.012, bd * 0.94, 0.036), (-bw * 0.27, bd * 0.46, 0.024), mats["lid"])
        _box(tray, "tray_side_r", (0.012, bd * 0.94, 0.036), (bw * 0.27, bd * 0.46, 0.024), mats["lid"])
        # keep the drawer face below the tilt-panel hinge line so a tilting panel clears it
        _box(tray, "tray_front_panel", (bw * 0.58, 0.020, 0.032), (0.0, -0.010, 0.012), mats["base"])
        _box(tray, "tray_paper", (bw * 0.46, bd * 0.66, 0.012), (0.0, bd * 0.46, 0.018), mats["paper"])
        model.articulation(
            "body_to_input_tray", ArticulationType.PRISMATIC, parent=body, child=tray,
            origin=Origin(xyz=(0.0, r.front_y - 0.006, r.cassette_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=30.0, velocity=0.25, lower=0.0, upper=r.tray_travel),
        )

    elif r.paper_handling == "front_output_tray_stopper":
        tray_w = bw * 0.62
        tray_len = 0.15
        tray_t = 0.014
        tray = model.part("output_tray")
        _box(tray, "tray_plate", (tray_w, tray_len, tray_t), (0.0, tray_len / 2.0, 0.0), mats["base"])
        for sx, tag in ((-(tray_w / 2.0) + 0.006, "l"), ((tray_w / 2.0) - 0.006, "r")):
            _box(tray, f"tray_rail_{tag}", (0.008, tray_len, 0.010),
                 (sx, tray_len / 2.0, 0.007), mats["base"])
        model.articulation(
            "body_to_output_tray", ArticulationType.PRISMATIC, parent=body, child=tray,
            origin=Origin(xyz=(0.0, r.front_y + 0.012, r.slot_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=0.20, lower=0.0, upper=r.tray_travel),
        )
        stopper = model.part("paper_stopper")
        stop_w = tray_w - 0.020
        stop_len = 0.045
        _box(stopper, "stopper_flap", (stop_w, stop_len, 0.006), (0.0, -stop_len / 2.0, 0.0),
             mats["base"])
        model.articulation(
            "output_tray_to_paper_stopper", ArticulationType.REVOLUTE, parent=tray, child=stopper,
            origin=Origin(xyz=(0.0, 0.0, tray_t / 2.0)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.radians(80.0)),
        )

    else:  # foldout_rear_input
        _front_output_shelf(body, r, mats)
        tray = model.part("rear_tray")
        _box(tray, "rear_hinge_lip", (bw * 0.66, 0.014, 0.010), (0.0, 0.007, 0.005), mats["body"])
        _box(tray, "rear_tray_base", (bw * 0.64, 0.19, 0.010), (0.0, 0.100, 0.005), mats["body"])
        _box(tray, "rear_tray_paper", (bw * 0.52, 0.16, 0.003), (0.0, 0.100, 0.011), mats["paper"])
        model.articulation(
            "body_to_rear_tray", ArticulationType.REVOLUTE, parent=body, child=tray,
            origin=Origin(xyz=(0.0, r.rear_y - 0.006, r.body_top)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.35),
        )


def _button_xs(r: ResolvedPrinterConfig) -> list[float]:
    n = r.button_count
    if n <= 0:
        return []
    span_avail = r.bw * 0.60
    spacing = min(0.026, span_avail / max(n, 1))
    return [(i - (n - 1) / 2.0) * spacing for i in range(n)]


def _build_control_panel(model: ArticulatedObject, body: Part, r: ResolvedPrinterConfig,
                         mats: dict) -> None:
    bw = r.bw
    face_y = r.front_y + 0.004

    if r.control_panel == "flat_button_strip":
        _box(body, "control_panel", (bw * 0.74, 0.014, 0.050),
             (0.0, r.front_y + 0.009, r.panel_z), mats["panel"])
        _box(body, "panel_display", (0.055, 0.004, 0.030),
             (bw * 0.30, face_y + 0.002, r.panel_z), mats["dark"])
        btn_y = face_y - 0.003
        for i, bx in enumerate(_button_xs(r)):
            btn = model.part(f"button_{i}")
            _cyl(btn, f"button_{i}_cap", 0.0095, 0.010, (0.0, 0.0, 0.0),
                 mats["accent"] if i == 0 else mats["dark"], rpy=(math.pi / 2.0, 0.0, 0.0))
            model.articulation(
                f"body_to_button_{i}", ArticulationType.PRISMATIC, parent=body, child=btn,
                origin=Origin(xyz=(bx, btn_y, r.panel_z)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=2.0, velocity=0.05, lower=0.0, upper=0.0015),
            )

    elif r.control_panel == "fixed_flush_touchscreen":
        _box(body, "control_panel", (bw * 0.30, 0.010, 0.070), (0.0, r.front_y + 0.003, r.panel_z),
             mats["panel"])
        _box(body, "touchscreen_glass", (bw * 0.22, 0.006, 0.052), (0.0, face_y - 0.004, r.panel_z),
             mats["screen"])
        for i, (dx, key) in enumerate(((-bw * 0.05, "accent"), (0.0, "badge"), (bw * 0.05, "accent"))):
            _box(body, f"screen_icon_{i}", (0.014, 0.004, 0.018),
                 (dx, face_y - 0.007, r.panel_z), mats[key])

    else:  # tilting_touchscreen_panel
        panel = model.part("control_panel")
        _box(panel, "control_panel_bezel", (bw * 0.26, 0.010, 0.060), (0.0, 0.0, 0.030), mats["panel"])
        _box(panel, "touchscreen_glass", (bw * 0.20, 0.006, 0.044), (0.0, -0.005, 0.032), mats["screen"])
        for i, dx in enumerate((-bw * 0.05, 0.0, bw * 0.05)):
            _box(panel, f"screen_icon_{i}", (0.014, 0.004, 0.018), (dx, -0.008, 0.032),
                 mats["accent"] if i != 1 else mats["badge"])
        model.articulation(
            "body_to_control_panel", ArticulationType.REVOLUTE, parent=body, child=panel,
            origin=Origin(xyz=(0.0, r.front_y + 0.002, r.panel_z - 0.028)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=1.0, lower=0.0, upper=0.62),
        )


def build_printer(config: PrinterConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {key: model.material(f"printer_{key}", rgba=rgba) for key, rgba in r.palette.items()}

    body = _build_body(model, r, mats)
    _build_scanner_lid(model, body, r, mats)
    _build_paper_handling(model, body, r, mats)
    _build_control_panel(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_printer(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_printer(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedPrinterConfig) -> list[tuple[str, str]]:
    n_band = str(r.button_count) if r.control_panel == "flat_button_strip" else "0"
    return [
        ("form_family", r.form_family),
        ("paper_handling", r.paper_handling),
        ("control_panel", r.control_panel),
        ("button_count", n_band),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


def run_printer_tests(object_model: ArticulatedObject, config: PrinterConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}
    body = object_model.get_part("body")

    ctx.check("body root present", "body" in part_names)

    if "scanner_lid" in part_names:
        lid = object_model.get_part("scanner_lid")
        ctx.allow_overlap(lid, body, reason="scanner lid seats flush on the top deck / scanner bed")
    if "extension_arm" in part_names:
        ctx.allow_isolated_part(object_model.get_part("extension_arm"),
                                reason="output extension slides out of the body and loses contact")
        ctx.allow_overlap(object_model.get_part("extension_arm"), body,
                          reason="output extension is retained in the front slot when collapsed")
    if "input_tray" in part_names:
        ctx.allow_overlap(object_model.get_part("input_tray"), body,
                          reason="paper cassette is retained inside the body bay when closed")
    if "output_tray" in part_names:
        tray = object_model.get_part("output_tray")
        ctx.allow_overlap(tray, body, reason="output tray is retained in the body slot when collapsed")
        if "paper_stopper" in part_names:
            stopper = object_model.get_part("paper_stopper")
            ctx.allow_overlap(stopper, tray, elem_a="stopper_flap", elem_b="tray_plate",
                              reason="stopper flap hinges on the tray front edge")
            ctx.allow_overlap(stopper, body,
                              reason="output tray + flip-up stopper are retained in the front output slot")
            if r.control_panel == "tilting_touchscreen_panel":
                ctx.allow_overlap(stopper, object_model.get_part("control_panel"),
                                  reason="flip-up stopper shares the front envelope with the tilting panel")
    if "rear_tray" in part_names:
        rear_tray = object_model.get_part("rear_tray")
        ctx.allow_overlap(rear_tray, body,
                          reason="folding rear paper support seats on the rear-top hinge edge")
        if "scanner_lid" in part_names:
            ctx.allow_overlap(rear_tray, object_model.get_part("scanner_lid"),
                              reason="fold-out rear feed and scanner lid share the rear hinge line")
    for i in range(r.button_count):
        b = object_model.get_part(f"button_{i}")
        ctx.allow_overlap(b, body,
                          reason="button cap base is seated in its panel/body bore and presses inward")
    if r.control_panel == "tilting_touchscreen_panel":
        ctx.allow_overlap(object_model.get_part("control_panel"), body,
                          elem_a="control_panel_bezel", elem_b="body_shell",
                          reason="tilting panel bezel seats proud of the front face")

    ctx.check("at least one non-fixed joint",
              any(j.articulation_type != ArticulationType.FIXED for j in object_model.articulations))

    if "body_to_scanner_lid" in joint_names:
        lid = object_model.get_part("scanner_lid")
        j = object_model.get_articulation("body_to_scanner_lid")
        ctx.check("scanner lid is revolute", j.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb(lid)
        with ctx.pose({j: r.lid_upper}):
            openv = ctx.part_world_aabb(lid)
        ctx.check("scanner lid opens upward",
                  rest is not None and openv is not None and openv[1][2] > rest[1][2] + 0.06,
                  details=f"rest_top={rest[1][2]:.3f} open_top={openv[1][2]:.3f}")

    for jn, pn, thresh in (
        ("body_to_extension_arm", "extension_arm", -0.05),
        ("body_to_input_tray", "input_tray", -0.08),
        ("body_to_output_tray", "output_tray", -0.05),
    ):
        if jn in joint_names:
            part = object_model.get_part(pn)
            j = object_model.get_articulation(jn)
            rest = ctx.part_world_position(part)
            with ctx.pose({j: r.tray_travel}):
                out = ctx.part_world_position(part)
            ctx.check(f"{pn} slides out the front",
                      rest is not None and out is not None and out[1] < rest[1] + thresh,
                      details=f"rest_y={rest[1]:.3f} out_y={out[1]:.3f}")

    if "output_tray_to_paper_stopper" in joint_names:
        stop = object_model.get_part("paper_stopper")
        j = object_model.get_articulation("output_tray_to_paper_stopper")
        rest = ctx.part_world_aabb(stop)
        with ctx.pose({j: math.radians(80.0)}):
            up = ctx.part_world_aabb(stop)
        ctx.check("paper stopper flips up",
                  rest is not None and up is not None and up[1][2] > rest[1][2] + 0.02,
                  details=f"rest_top={rest[1][2]:.3f} up_top={up[1][2]:.3f}")

    if "body_to_rear_tray" in joint_names:
        tray = object_model.get_part("rear_tray")
        j = object_model.get_articulation("body_to_rear_tray")
        rest = ctx.part_world_aabb(tray)
        with ctx.pose({j: 1.30}):
            up = ctx.part_world_aabb(tray)
        ctx.check("rear tray folds up",
                  rest is not None and up is not None and up[1][2] > rest[1][2] + 0.08,
                  details=f"rest_top={rest[1][2]:.3f} up_top={up[1][2]:.3f}")

    if r.button_count > 0 and "body_to_button_0" in joint_names:
        btn = object_model.get_part("button_0")
        j = object_model.get_articulation("body_to_button_0")
        rest = ctx.part_world_position(btn)
        with ctx.pose({j: 0.0015}):
            press = ctx.part_world_position(btn)
        ctx.check("control button presses inward",
                  rest is not None and press is not None and press[1] > rest[1] + 0.0009,
                  details=f"rest_y={rest[1]:.4f} press_y={press[1]:.4f}")

    if "body_to_control_panel" in joint_names:
        panel = object_model.get_part("control_panel")
        j = object_model.get_articulation("body_to_control_panel")
        ctx.check("control panel is revolute tilt", j.articulation_type == ArticulationType.REVOLUTE)
        rest = ctx.part_world_aabb(panel)
        with ctx.pose({j: 0.55}):
            tilt = ctx.part_world_aabb(panel)
        ctx.check("control panel tilts out toward user",
                  rest is not None and tilt is not None and tilt[0][1] < rest[0][1] - 0.004,
                  details=f"rest_min_y={rest[0][1]:.3f} tilt_min_y={tilt[0][1]:.3f}")

    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "PrinterConfig",
    "ResolvedPrinterConfig",
    "build_printer",
    "build_seeded_printer",
    "config_from_seed",
    "resolve_config",
    "run_printer_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
