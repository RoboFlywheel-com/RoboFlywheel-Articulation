# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template: Emergency exit door.

Core identity: a building egress door leaf that swings on hinges (REVOLUTE) in a
fixed frame and is opened by panic/exit hardware (touch bar / surface vertical
rod / crash paddle / recessed touch bar), carrying a green "push to open" exit
sign. Structure is derived from 14 five-star sources (2 origin anchors + 12
forks); see ``specs_modular_v1/emergency_exit_door.md``.

Enum-driven modular template (``__modular__ = True``). Discrete diversity axes:
  A opening_config  : double_leaf / single_leaf / leaf_and_half / single_plus_sidelite  (① + multiplicity N)
  B leaf_form       : solid_slab / vision_lite / narrow_vision / full_glazed            (③ Primary Form Family)
  C panic_hardware  : touch_bar / vertical_rod / crash_paddle / recessed_bar            (② mechanism)
  D header_style    : plain_header / glazed_transom                                     (① frame extension)
  E closer          : no_closer / overhead_arm (gated)                                  (② closer linkage)

Rule notes:
  * Rule 1: leaf body / signs / stiles / rails / beads / clamps / pockets are host
    ``part.visual(...)``; only genuinely articulated pieces (leaves, push bars,
    rods, paddle, latch bolt, closer arm) are separate parts.
  * Rule 2: leaf hinges / paddle pivot / closer spindle are pin hinges -> grandfathered
    (no MatingContract); their origins land on real hinge-line / pivot-pin / spindle
    hardware. Prismatic bar/rod/latch joints are captured sliders (grandfathered,
    element-scoped allow_overlap for the captured-shaft contacts).
  * Rule 3: all hardware is rectangular metal (Box/Cylinder). The plain-box hardware
    form is itself the 26c10e origin 5-star form; no sculpted lathe/mesh is downgraded.
  * Rule 4: exit sign / stiles / rails / beads derive x-center and z from the leaf's
    realized width/height and leaf_form (③->⑤->④ order).
  * Rule 5: run_tests calls fail_if_parts_overlap_in_sampled_poses(...) plus targeted
    ctx.pose(...) per mechanism.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from math import pi

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Discrete axes
# ---------------------------------------------------------------------------
OPENING_CONFIGS = ("double_leaf", "single_leaf", "leaf_and_half", "single_plus_sidelite")
LEAF_FORMS = ("solid_slab", "vision_lite", "narrow_vision", "full_glazed")
PANIC_HARDWARE = ("touch_bar", "vertical_rod", "crash_paddle", "recessed_bar")
HEADER_STYLES = ("plain_header", "glazed_transom")
CLOSERS = ("no_closer", "overhead_arm")

PaletteStyle = str
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "galvanized_steel",
    "satin_offwhite_steel",
    "fire_door_red",
    "brushed_stainless",
    "bronze_glass",
    "matte_black_brass",
)

# Keys: frame, leaf, hardware, shadow, green, white, glass. Every .visual reads one.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "galvanized_steel": {
        "frame": (0.34, 0.36, 0.35, 1.0),
        "leaf": (0.56, 0.58, 0.56, 1.0),
        "hardware": (0.78, 0.79, 0.76, 1.0),
        "shadow": (0.03, 0.035, 0.035, 1.0),
        "green": (0.0, 0.62, 0.28, 1.0),
        "white": (0.94, 0.96, 0.93, 1.0),
        "glass": (0.62, 0.66, 0.64, 0.55),
    },
    "satin_offwhite_steel": {
        "frame": (0.18, 0.19, 0.20, 1.0),
        "leaf": (0.76, 0.78, 0.82, 1.0),
        "hardware": (0.68, 0.69, 0.67, 1.0),
        "shadow": (0.015, 0.016, 0.018, 1.0),
        "green": (0.02, 0.62, 0.36, 1.0),
        "white": (0.97, 0.98, 0.94, 1.0),
        "glass": (0.66, 0.72, 0.76, 0.50),
    },
    "fire_door_red": {
        "frame": (0.22, 0.05, 0.04, 1.0),
        "leaf": (0.62, 0.11, 0.09, 1.0),
        "hardware": (0.80, 0.81, 0.80, 1.0),
        "shadow": (0.04, 0.02, 0.02, 1.0),
        "green": (0.0, 0.60, 0.28, 1.0),
        "white": (0.96, 0.96, 0.94, 1.0),
        "glass": (0.60, 0.66, 0.64, 0.52),
    },
    "brushed_stainless": {
        "frame": (0.46, 0.47, 0.48, 1.0),
        "leaf": (0.70, 0.71, 0.72, 1.0),
        "hardware": (0.82, 0.83, 0.84, 1.0),
        "shadow": (0.05, 0.05, 0.06, 1.0),
        "green": (0.0, 0.62, 0.30, 1.0),
        "white": (0.95, 0.96, 0.95, 1.0),
        "glass": (0.64, 0.70, 0.72, 0.50),
    },
    "bronze_glass": {
        "frame": (0.42, 0.40, 0.38, 1.0),
        "leaf": (0.40, 0.36, 0.30, 1.0),
        "hardware": (0.72, 0.66, 0.52, 1.0),
        "shadow": (0.05, 0.045, 0.035, 1.0),
        "green": (0.0, 0.58, 0.30, 1.0),
        "white": (0.95, 0.93, 0.86, 1.0),
        "glass": (0.52, 0.42, 0.32, 0.40),
    },
    "matte_black_brass": {
        "frame": (0.10, 0.10, 0.11, 1.0),
        "leaf": (0.16, 0.16, 0.17, 1.0),
        "hardware": (0.72, 0.58, 0.26, 1.0),
        "shadow": (0.02, 0.02, 0.02, 1.0),
        "green": (0.0, 0.60, 0.30, 1.0),
        "white": (0.94, 0.94, 0.90, 1.0),
        "glass": (0.30, 0.34, 0.36, 0.45),
    },
}

# Nominal absolute dims (basis: 26c10e origin, meters).
_LEAF_H = 2.03
_LEAF_T = 0.045
_JAMB_W = 0.10
_JAMB_D = 0.11
_SILL = 0.06
_CENTER_SEAM = 0.020


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class EmergencyExitDoorConfig:
    opening_config: str | None = None
    leaf_form: str | None = None
    panic_hardware: str | None = None
    header_style: str | None = None
    closer: str | None = None
    palette_style: PaletteStyle = "galvanized_steel"
    door_height: float = _LEAF_H
    door_thickness: float = _LEAF_T
    opening_width_scale: float = 1.0
    bar_travel: float = 0.015
    paddle_open: float = 0.35
    hinge_upper: float = 1.55
    name: str = "emergency_exit_door"


@dataclass(frozen=True)
class ResolvedEmergencyExitDoorConfig:
    opening_config: str
    leaf_form: str
    panic_hardware: str
    header_style: str
    closer: str
    palette_style: PaletteStyle
    door_height: float
    door_thickness: float
    opening_width_scale: float
    bar_travel: float
    paddle_open: float
    hinge_upper: float
    # Derived.
    leaf_count: int
    latch_travel: float
    rod_retraction: float
    name: str

    @property
    def hf(self) -> float:
        """Height factor vs nominal 2.03 leaf (⑤ scales z positions)."""
        return self.door_height / _LEAF_H

    @property
    def front_y(self) -> float:
        return self.door_thickness / 2.0

    @property
    def z_bar(self) -> float:
        return 0.52 * self.door_height

    @property
    def frame_height(self) -> float:
        return self.door_height + 0.16


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (deterministic; seed 0 not special).
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> EmergencyExitDoorConfig:
    rng = random.Random(seed)
    opening_config = rng.choice(OPENING_CONFIGS)
    leaf_form = rng.choice(LEAF_FORMS)
    panic_hardware = rng.choice(PANIC_HARDWARE)
    header_style = rng.choice(HEADER_STYLES)
    closer = rng.choice(CLOSERS)
    # Decorrelated palette stream so colorways spread across consecutive seeds.
    palette_style = random.Random(seed * 2654435761 + 0x9E37).choice(PALETTE_STYLES)
    return EmergencyExitDoorConfig(
        opening_config=opening_config,
        leaf_form=leaf_form,
        panic_hardware=panic_hardware,
        header_style=header_style,
        closer=closer,
        palette_style=palette_style,
        door_height=round(rng.uniform(1.95, 2.12), 4),
        door_thickness=round(rng.uniform(0.040, 0.052), 4),
        opening_width_scale=round(rng.uniform(0.94, 1.08), 4),
        bar_travel=round(rng.uniform(0.014, 0.024), 4),
        paddle_open=round(rng.uniform(0.26, 0.34), 4),
        hinge_upper=round(rng.uniform(1.35, 1.55), 4),
        name=f"seeded_emergency_exit_door_{seed}",
    )


def resolve_config(
    config: EmergencyExitDoorConfig | None = None,
) -> ResolvedEmergencyExitDoorConfig:
    cfg = config or EmergencyExitDoorConfig()
    opening_config = _pick(cfg.opening_config, OPENING_CONFIGS)
    leaf_form = _pick(cfg.leaf_form, LEAF_FORMS)
    panic_hardware = _pick(cfg.panic_hardware, PANIC_HARDWARE)
    header_style = _pick(cfg.header_style, HEADER_STYLES)
    closer = _pick(cfg.closer, CLOSERS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # --- Compatibility gating (spec compatibility matrix). ---
    # overhead closer only on a plain header and non-sidelite opening (its frame
    # anchor geometry assumes a plain header + hinged near leaf).
    if closer == "overhead_arm" and (
        header_style != "plain_header" or opening_config == "single_plus_sidelite"
    ):
        closer = "no_closer"

    # A central recessed touch-bar pocket conflicts with a central full-height
    # vision slot; fall back to a surface touch bar for that leaf form.
    if leaf_form == "narrow_vision" and panic_hardware in ("recessed_bar", "crash_paddle"):
        panic_hardware = "touch_bar"

    leaf_count = 2 if opening_config in ("double_leaf", "leaf_and_half") else 1

    door_height = _clamp(cfg.door_height, 1.95, 2.12)
    door_thickness = _clamp(cfg.door_thickness, 0.040, 0.052)
    opening_width_scale = _clamp(cfg.opening_width_scale, 0.94, 1.08)
    bar_travel = _clamp(cfg.bar_travel, 0.014, 0.024)
    paddle_open = _clamp(cfg.paddle_open, 0.24, 0.34)
    hinge_upper = _clamp(cfg.hinge_upper, 1.30, 1.55)

    # Derived (equation): latch/rod retraction driven off bar travel (mimic ratios
    # from e8695a x1.65 latch, vertical_rod 0.025/0.015 rod).
    latch_travel = round(min(0.055, bar_travel * 1.65), 4)
    rod_retraction = round(min(0.030, bar_travel * (0.025 / 0.015)), 4)

    return ResolvedEmergencyExitDoorConfig(
        opening_config=opening_config,
        leaf_form=leaf_form,
        panic_hardware=panic_hardware,
        header_style=header_style,
        closer=closer,
        palette_style=palette_style,
        door_height=door_height,
        door_thickness=door_thickness,
        opening_width_scale=opening_width_scale,
        bar_travel=bar_travel,
        paddle_open=paddle_open,
        hinge_upper=hinge_upper,
        leaf_count=leaf_count,
        latch_travel=latch_travel,
        rod_retraction=rod_retraction,
        name=cfg.name or "emergency_exit_door",
    )


def slot_choices_for_config(
    config: EmergencyExitDoorConfig | ResolvedEmergencyExitDoorConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedEmergencyExitDoorConfig)
        else resolve_config(config)
    )
    return (
        ("opening_config", r.opening_config),
        ("leaf_form", r.leaf_form),
        ("panic_hardware", r.panic_hardware),
        ("header_style", r.header_style),
        ("closer", r.closer),
        ("leaf_count", f"N{r.leaf_count}"),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Geometry helpers
# ===========================================================================
def _leaf_layout(r: ResolvedEmergencyExitDoorConfig):
    """Return (frame_dict, leaves) for the opening_config.

    frame_dict: jambs=[(x_center, w)], span_w, has_sidelite, sidelite_x, sidelite_w, mullion_x.
    leaves: list of (name, sign, width, active, hinge_x, is_primary).
    hinge_x is the |world x| of the hinge; sign gives leaf direction (+1 left leaf, -1 right).
    """
    s = r.opening_width_scale
    if r.opening_config == "double_leaf":
        hinge_x = 0.86 * s
        leaf_w = (hinge_x - _CENTER_SEAM / 2.0)
        jamb_x = hinge_x + _JAMB_W / 2.0
        frame = {
            "jambs": [(-jamb_x, _JAMB_W), (jamb_x, _JAMB_W)],
            "span_w": 2.0 * jamb_x + _JAMB_W,
            "center_x": 0.0,
            "has_sidelite": False,
        }
        leaves = [
            ("door_0", 1.0, leaf_w, True, hinge_x, True),
            ("door_1", -1.0, leaf_w, True, hinge_x, False),
        ]
        return frame, leaves
    if r.opening_config == "leaf_and_half":
        hinge_x = 0.86 * s
        wide_w = 1.15 * s
        narrow_w = (2.0 * hinge_x - _CENTER_SEAM) - wide_w
        jamb_x = hinge_x + _JAMB_W / 2.0
        frame = {
            "jambs": [(-jamb_x, _JAMB_W), (jamb_x, _JAMB_W)],
            "span_w": 2.0 * jamb_x + _JAMB_W,
            "center_x": 0.0,
            "has_sidelite": False,
        }
        leaves = [
            ("door_0", 1.0, wide_w, True, hinge_x, True),
            ("door_1", -1.0, narrow_w, False, hinge_x, False),
        ]
        return frame, leaves
    if r.opening_config == "single_leaf":
        opening = 0.95 * s
        hinge_x = opening / 2.0
        leaf_w = opening - 0.02
        jamb_x = hinge_x + _JAMB_W / 2.0
        frame = {
            "jambs": [(-jamb_x, _JAMB_W), (jamb_x, _JAMB_W)],
            "span_w": 2.0 * jamb_x + _JAMB_W,
            "center_x": 0.0,
            "has_sidelite": False,
        }
        leaves = [("door_0", 1.0, leaf_w, True, hinge_x, True)]
        return frame, leaves
    # single_plus_sidelite: active leaf on the left, fixed glazed sidelite on the right.
    opening = 0.95 * s
    hinge_x = opening / 2.0
    leaf_w = opening - 0.02
    left_jamb_x = hinge_x + _JAMB_W / 2.0
    mullion_w = 0.08
    mullion_x = hinge_x + 0.04
    sidelite_w = 0.50 * s
    sidelite_x = mullion_x + mullion_w / 2.0 + sidelite_w / 2.0
    right_jamb_x = sidelite_x + sidelite_w / 2.0 + _JAMB_W / 2.0
    center_x = (-left_jamb_x + right_jamb_x) / 2.0
    frame = {
        "jambs": [(-left_jamb_x, _JAMB_W), (right_jamb_x, _JAMB_W)],
        "span_w": (right_jamb_x - (-left_jamb_x)) + _JAMB_W,
        "center_x": center_x,
        "has_sidelite": True,
        "sidelite_x": sidelite_x,
        "sidelite_w": sidelite_w,
        "mullion_x": mullion_x,
        "mullion_w": mullion_w,
    }
    leaves = [("door_0", 1.0, leaf_w, True, hinge_x, True)]
    return frame, leaves


def _build_frame(model, r, mats, frame_dict):
    frame = model.part("frame")
    fh = r.frame_height
    span = frame_dict["span_w"]
    cx = frame_dict["center_x"]
    header_z = r.door_height + 0.11

    for i, (jx, jw) in enumerate(frame_dict["jambs"]):
        frame.visual(
            Box((jw, _JAMB_D, fh)),
            origin=Origin(xyz=(jx, 0.0, fh / 2.0)),
            material=mats["frame"],
            name=f"jamb_{i}", material_class_id="metal.paint_coated",
        )
    frame.visual(
        Box((span, _JAMB_D, 0.10)),
        origin=Origin(xyz=(cx, 0.0, header_z)),
        material=mats["frame"],
        name="header", material_class_id="metal.paint_coated",
    )
    frame.visual(
        Box((span, _JAMB_D + 0.01, _SILL)),
        origin=Origin(xyz=(cx, 0.0, _SILL / 2.0)),
        material=mats["frame"],
        name="threshold", material_class_id="metal.aluminum_bare",
    )
    # Hinge/pivot lines sit exactly on each leaf hinge axis (anchors the joint).
    _, leaves = _leaf_layout(r)
    for i, (_, sign, _w, _a, hinge_x, _p) in enumerate(leaves):
        frame.visual(
            Cylinder(radius=0.012, length=r.door_height - 0.02),
            origin=Origin(xyz=(-sign * hinge_x, 0.035, _SILL + r.door_height / 2.0)),
            material=mats["shadow"],
            name=f"hinge_line_{i}", material_class_id="metal.blackened_gunmetal",
        )

    # Fixed glazed sidelite (single_plus_sidelite).
    if frame_dict["has_sidelite"]:
        mx, mw = frame_dict["mullion_x"], frame_dict["mullion_w"]
        sx, sw = frame_dict["sidelite_x"], frame_dict["sidelite_w"]
        frame.visual(
            Box((mw, _JAMB_D, fh)),
            origin=Origin(xyz=(mx, 0.0, fh / 2.0)),
            material=mats["frame"],
            name="mullion", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((sw, 0.020, r.door_height - 0.10)),
            origin=Origin(xyz=(sx, 0.0, _SILL + (r.door_height - 0.10) / 2.0)),
            material=mats["glass"],
            name="sidelite_glass", material_class_id="glass.clear_transparent",
        )
        # Glazing bead frame around the sidelite (host-conformal).
        for nm, box, xyz in (
            ("sidelite_bead_top", (sw + 0.02, 0.028, 0.03),
             (sx, 0.0, _SILL + r.door_height - 0.10 + 0.005)),
            ("sidelite_bead_bottom", (sw + 0.02, 0.028, 0.03),
             (sx, 0.0, _SILL + 0.005)),
        ):
            frame.visual(Box(box), origin=Origin(xyz=xyz), material=mats["frame"], name=nm, material_class_id="metal.paint_coated")

    # Header style D: glazed transom above the door header.
    if r.header_style == "glazed_transom":
        base = r.door_height + 0.16
        top = r.door_height + 0.47
        gh = top - base
        frame.visual(
            Box((span, _JAMB_D, 0.10)),
            origin=Origin(xyz=(cx, 0.0, r.door_height + 0.52)),
            material=mats["frame"],
            name="transom_header", material_class_id="metal.paint_coated",
        )
        frame.visual(
            Box((0.05, _JAMB_D, gh)),
            origin=Origin(xyz=(cx, 0.0, base + gh / 2.0)),
            material=mats["frame"],
            name="transom_mullion", material_class_id="metal.paint_coated",
        )
        half = (span - 0.10) / 4.0
        for i, tx in enumerate((cx - half, cx + half)):
            frame.visual(
                Box((2.0 * half - 0.06, 0.022, gh)),
                origin=Origin(xyz=(tx, 0.0, base + gh / 2.0)),
                material=mats["glass"],
                name=f"transom_glass_{i}", material_class_id="glass.clear_transparent",
            )
    return frame


def _add_leaf_body(door, r, mats, *, width, sign, leaf_form):
    """Emit leaf body visuals (③ form family). x_center is sign*width/2 (local)."""
    h = r.door_height
    t = r.door_thickness
    fy = r.front_y
    x_center = sign * width / 2.0
    direction = sign

    if leaf_form == "full_glazed":
        # Stile-and-rail: narrow anodized frame around a large glass infill.
        stile_w = 0.065
        rail_h = 0.100
        glass_w = width - 2.0 * stile_w + 0.004
        glass_h = h - 2.0 * rail_h + 0.004
        door.visual(
            Box((glass_w, 0.010, glass_h)),
            origin=Origin(xyz=(x_center, 0.0, h / 2.0)),
            material=mats["glass"],
            name="door_body", material_class_id="glass.clear_transparent",
        )
        for nm, x in (
            ("hinge_stile", direction * (stile_w / 2.0)),
            ("meeting_stile", direction * (width - stile_w / 2.0)),
        ):
            door.visual(
                Box((stile_w, t, h)),
                origin=Origin(xyz=(x, 0.0, h / 2.0)),
                material=mats["leaf"],
                name=nm, material_class_id="metal.aluminum_bare",
            )
        for nm, z in (("top_rail", h - rail_h / 2.0), ("bottom_rail", rail_h / 2.0)):
            door.visual(
                Box((glass_w, t, rail_h)),
                origin=Origin(xyz=(x_center, 0.0, z)),
                material=mats["leaf"],
                name=nm, material_class_id="metal.aluminum_bare",
            )
        # Mid lock rail (full leaf thickness) gives the panic device a solid
        # mounting surface at bar height on an otherwise-glazed leaf.
        door.visual(
            Box((glass_w, t, 0.16)),
            origin=Origin(xyz=(x_center, 0.0, 0.52 * h)),
            material=mats["leaf"],
            name="lock_rail", material_class_id="metal.aluminum_bare",
        )
    else:
        # Solid slab body + raised stiles/rails.
        door.visual(
            Box((width, t, h)),
            origin=Origin(xyz=(x_center, 0.0, h / 2.0)),
            material=mats["leaf"],
            name="door_body", material_class_id="metal.paint_coated",
        )
        for nm, x in (
            ("hinge_stile", direction * 0.035),
            ("meeting_stile", direction * (width - 0.035)),
        ):
            door.visual(
                Box((0.052, 0.014, h - 0.08)),
                origin=Origin(xyz=(x, fy + 0.003, h / 2.0)),
                material=mats["frame"],
                name=nm, material_class_id="metal.paint_coated",
            )
        door.visual(
            Box((width - 0.08, 0.014, 0.050)),
            origin=Origin(xyz=(x_center, fy + 0.003, h - 0.040)),
            material=mats["frame"],
            name="top_rail", material_class_id="metal.paint_coated",
        )
        door.visual(
            Box((width - 0.08, 0.014, 0.055)),
            origin=Origin(xyz=(x_center, fy + 0.003, 0.040)),
            material=mats["frame"],
            name="bottom_rail", material_class_id="metal.paint_coated",
        )
        if leaf_form == "vision_lite":
            lite_z = h - 0.32
            lw, lh, bead = 0.18, 0.25, 0.015
            door.visual(
                Box((lw, 0.006, lh)),
                origin=Origin(xyz=(x_center, fy - 0.002, lite_z)),
                material=mats["glass"],
                name="vision_glass", material_class_id="glass.clear_transparent",
            )
            for nm, box, xyz in (
                ("glaze_top", (lw + 2 * bead, 0.012, bead), (x_center, fy + 0.002, lite_z + lh / 2 + bead / 2)),
                ("glaze_bottom", (lw + 2 * bead, 0.012, bead), (x_center, fy + 0.002, lite_z - lh / 2 - bead / 2)),
                ("glaze_left", (bead, 0.012, lh), (x_center - lw / 2 - bead / 2, fy + 0.002, lite_z)),
                ("glaze_right", (bead, 0.012, lh), (x_center + lw / 2 + bead / 2, fy + 0.002, lite_z)),
            ):
                door.visual(Box(box), origin=Origin(xyz=xyz), material=mats["frame"], name=nm, material_class_id="metal.paint_coated")
        elif leaf_form == "narrow_vision":
            lw, lh, bead = 0.12, h - 0.70, 0.015
            lite_z = h / 2.0 + 0.05
            door.visual(
                Box((lw, 0.006, lh)),
                origin=Origin(xyz=(x_center, fy - 0.002, lite_z)),
                material=mats["glass"],
                name="vision_glass", material_class_id="glass.clear_transparent",
            )
            for nm, box, xyz in (
                ("glaze_top", (lw + 2 * bead, 0.012, bead), (x_center, fy + 0.002, lite_z + lh / 2 + bead / 2)),
                ("glaze_bottom", (lw + 2 * bead, 0.012, bead), (x_center, fy + 0.002, lite_z - lh / 2 - bead / 2)),
                ("glaze_left", (bead, 0.012, lh), (x_center - lw / 2 - bead / 2, fy + 0.002, lite_z)),
                ("glaze_right", (bead, 0.012, lh), (x_center + lw / 2 + bead / 2, fy + 0.002, lite_z)),
            ):
                door.visual(Box(box), origin=Origin(xyz=xyz), material=mats["frame"], name=nm, material_class_id="metal.paint_coated")

    # Exit sign (④ host-conformal; derived from the leaf's realized front face + width/height).
    # body_hy = the leaf body's actual front-face y (glass body is thin; slab body is t/2).
    body_hy = 0.005 if leaf_form == "full_glazed" else fy
    sign_z = min(h - 0.55, 1.28 * r.hf)
    sign_y = body_hy - 0.002  # back face embeds into the body front for support
    door.visual(
        Box((min(0.34, width - 0.06), 0.007, 0.115)),
        origin=Origin(xyz=(x_center, sign_y, sign_z)),
        material=mats["green"],
        name="exit_sign", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    door.visual(
        Box((min(0.245, width - 0.12), 0.004, 0.018)),
        origin=Origin(xyz=(x_center, sign_y + 0.001, sign_z + 0.015)),
        material=mats["white"],
        name="sign_line", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    door.visual(
        Box((min(0.170, width - 0.16), 0.004, 0.014)),
        origin=Origin(xyz=(x_center, sign_y + 0.001, sign_z - 0.022)),
        material=mats["white"],
        name="sign_small_line", appearance_only=AppearanceOnlySpec(kind="decal"),
    )


def _add_flush_bolts(door, r, mats, *, width, sign):
    """Inactive leaf hardware (leaf_and_half door_1): top/bottom flush bolts."""
    h = r.door_height
    fy = r.front_y
    bolt_x = sign * (width - 0.030)
    for nm, z in (("flush_bolt_top", h - 0.10), ("flush_bolt_bottom", 0.14)):
        door.visual(
            Box((0.032, 0.030, 0.14)),
            origin=Origin(xyz=(bolt_x, fy + 0.005, z)),
            material=mats["hardware"],
            name=nm, material_class_id="metal.stainless_matte",
        )


def _bar_slider_allows(dn, bn, idx):
    """Captured-slider allowances: push bar retracts into its end housings."""
    pairs = []
    for k in (0, 1):
        for host in (f"bar_mount_{idx}_{k}", f"mount_slot_{idx}_{k}"):
            for be in ("bar_rail", "bar_end_0", "bar_end_1", "bar_back_pad"):
                pairs.append((dn, bn, host, be))
    return pairs


# --- Panic hardware (C) helpers. Each mounts on an ACTIVE leaf. -------------
def _panic_static_mounts(door, r, mats, *, width, sign, x_center, idx):
    """Two touch-bar end housings on the leaf face (shared by touch/vertical/recessed)."""
    fy = r.front_y
    z = r.z_bar
    mount_off = 0.36 * width
    for k, x in enumerate((x_center - sign * mount_off, x_center + sign * mount_off)):
        door.visual(
            Box((0.055, 0.052, 0.18)),
            origin=Origin(xyz=(x, fy + 0.026, z)),
            material=mats["hardware"],
            name=f"bar_mount_{idx}_{k}", material_class_id="metal.stainless_matte",
        )
        door.visual(
            Box((0.036, 0.040, 0.060)),
            origin=Origin(xyz=(x, fy + 0.024, z)),
            material=mats["shadow"],
            name=f"mount_slot_{idx}_{k}", material_class_id="metal.blackened_gunmetal",
        )


def _make_push_bar(model, r, mats, *, name, width):
    bar = model.part(name)
    bar_len = 0.74 * width
    bar.visual(
        Cylinder(radius=0.016, length=bar_len),
        origin=Origin(rpy=(0.0, pi / 2.0, 0.0)),
        material=mats["hardware"],
        name="bar_rail", material_class_id="metal.stainless_matte",
    )
    for k, x in enumerate((-bar_len / 2.0 + 0.012, bar_len / 2.0 - 0.012)):
        bar.visual(
            Box((0.030, 0.036, 0.036)),
            origin=Origin(xyz=(x, 0.0, 0.0)),
            material=mats["hardware"],
            name=f"bar_end_{k}", material_class_id="metal.stainless_matte",
        )
    # Green "push to open" label overlapping the rail front + white text ticks (④).
    bar.visual(
        Box((0.60 * bar_len, 0.010, 0.030)),
        origin=Origin(xyz=(0.0, -0.012, 0.0)),
        material=mats["green"],
        name="bar_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    for k in range(5):
        bar.visual(
            Box((0.03, 0.006, 0.006)),
            origin=Origin(xyz=(-0.20 * bar_len + k * 0.10 * bar_len, -0.016, 0.0)),
            material=mats["white"],
            name=f"bar_tick_{k}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # Back contact pad bridges the rail to the leaf bar_mount (support path).
    bar.visual(
        Box((0.09, 0.047, 0.05)),
        origin=Origin(xyz=(0.0, 0.030, 0.0)),
        material=mats["shadow"],
        name="bar_back_pad", material_class_id="rubber.smooth_plain",
    )
    return bar


def _add_touch_bar(model, door, r, mats, *, width, sign, x_center, idx):
    _panic_static_mounts(door, r, mats, width=width, sign=sign, x_center=x_center, idx=idx)
    bar = _make_push_bar(model, r, mats, name=f"push_bar_{idx}", width=width)
    model.articulation(
        f"door_{idx}_to_push_bar_{idx}",
        ArticulationType.PRISMATIC,
        parent=door,
        child=bar,
        origin=Origin(xyz=(x_center, r.front_y + 0.066, r.z_bar)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=0.20, lower=0.0, upper=r.bar_travel),
    )
    return _bar_slider_allows(door.name, f"push_bar_{idx}", idx)


def _add_recessed_bar(model, door, r, mats, *, width, sign, x_center, idx):
    """Flush touch bar mortised into a pocket + latch bolt (mimic push)."""
    fy = r.front_y
    z = r.z_bar
    # Mortise pocket walls on the leaf (host visuals).
    pw, ph = 0.37, 0.088
    for nm, box, xyz in (
        ("pocket_top", (pw + 0.008, r.door_thickness, 0.006), (x_center, 0.0, z + ph / 2 + 0.003)),
        ("pocket_bottom", (pw + 0.008, r.door_thickness, 0.006), (x_center, 0.0, z - ph / 2 - 0.003)),
        ("pocket_left", (0.006, r.door_thickness, ph + 0.006), (x_center - pw / 2 - 0.003, 0.0, z)),
        ("pocket_right", (0.006, r.door_thickness, ph + 0.006), (x_center + pw / 2 + 0.003, 0.0, z)),
    ):
        door.visual(Box(box), origin=Origin(xyz=xyz), material=mats["hardware"], name=f"{nm}_{idx}", material_class_id="metal.stainless_matte")
    door.visual(
        Box((pw - 0.008, 0.008, ph - 0.008)),
        origin=Origin(xyz=(x_center, fy - 0.004, z)),
        material=mats["shadow"],
        name=f"pocket_back_{idx}", material_class_id="metal.blackened_gunmetal",
    )
    # Flush touch plate part (sits within the pocket, slightly proud).
    plate = model.part(f"push_bar_{idx}")
    plate.visual(
        Box((0.34, 0.012, 0.068)),
        origin=Origin(),
        material=mats["hardware"],
        name="touch_plate", material_class_id="metal.stainless_matte",
    )
    plate.visual(
        Box((0.31, 0.005, 0.040)),
        origin=Origin(xyz=(0.0, -0.008, 0.0)),
        material=mats["green"],
        name="bar_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    for k in range(5):
        plate.visual(
            Box((0.03, 0.004, 0.006)),
            origin=Origin(xyz=(-0.12 + k * 0.06, -0.011, 0.0)),
            material=mats["white"],
            name=f"bar_tick_{k}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    # Guide tongues ride inside the pocket (captured, connects to leaf).
    for k, x in enumerate((-0.16, 0.16)):
        plate.visual(
            Box((0.036, 0.030, 0.052)),
            origin=Origin(xyz=(x, 0.014, 0.0)),
            material=mats["shadow"],
            name=f"tongue_{k}", material_class_id="metal.blackened_gunmetal",
        )
    model.articulation(
        f"door_{idx}_to_push_bar_{idx}",
        ArticulationType.PRISMATIC,
        parent=door,
        child=plate,
        origin=Origin(xyz=(x_center, fy + 0.006, z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=95.0, velocity=0.35, lower=0.0, upper=r.bar_travel),
    )
    latch = _add_latch_bolt(model, door, r, mats, width=width, sign=sign, idx=idx,
                            driver=f"door_{idx}_to_push_bar_{idx}", mult=1.65)
    pairs = []
    hosts = ("door_body", "lock_rail", f"pocket_top_{idx}", f"pocket_bottom_{idx}",
             f"pocket_left_{idx}", f"pocket_right_{idx}", f"pocket_back_{idx}")
    plate_elems = ("touch_plate", "tongue_0", "tongue_1", "bar_label") + tuple(
        f"bar_tick_{k}" for k in range(5)
    )
    for host in hosts:
        for be in plate_elems:
            pairs.append((door.name, f"push_bar_{idx}", host, be))
    return pairs + latch


def _add_latch_bolt(model, door, r, mats, *, width, sign, idx, driver, mult):
    """Center latch bolt near the meeting stile; retracts toward the hinge."""
    fy = r.front_y
    z = r.z_bar
    latch_x = sign * (width - 0.030)
    # Center latch block on the leaf (static host visual, seats the bolt); its
    # back face embeds into the leaf front for support.
    door.visual(
        Box((0.050, 0.062, 0.19)),
        origin=Origin(xyz=(latch_x, fy + 0.028, z)),
        material=mats["hardware"],
        name=f"center_latch_block_{idx}", material_class_id="metal.stainless_matte",
    )
    bolt = model.part("latch_bolt")
    bolt.visual(
        Box((0.034, 0.022, 0.032)),
        origin=Origin(xyz=(0.015, 0.0, 0.0)),
        material=mats["hardware"],
        name="latch_bolt_tip", material_class_id="metal.stainless_matte",
    )
    bolt.visual(
        Box((0.040, 0.018, 0.024)),
        origin=Origin(xyz=(-0.014, 0.0, 0.0)),
        material=mats["shadow"],
        name="latch_bolt_tail", material_class_id="metal.blackened_gunmetal",
    )
    kwargs = {}
    if driver is not None:
        kwargs["mimic"] = Mimic(joint=driver, multiplier=mult, offset=0.0)
    model.articulation(
        f"door_{idx}_to_latch_bolt",
        ArticulationType.PRISMATIC,
        parent=door,
        child=bolt,
        origin=Origin(xyz=(latch_x, fy + 0.030, z)),
        axis=(-sign, 0.0, 0.0),
        motion_limits=MotionLimits(effort=45.0, velocity=0.25, lower=0.0, upper=r.latch_travel),
        **kwargs,
    )
    return [
        (door.name, "latch_bolt", f"center_latch_block_{idx}", "latch_bolt_tip"),
        (door.name, "latch_bolt", f"center_latch_block_{idx}", "latch_bolt_tail"),
    ]


def _add_vertical_rod(model, door, r, mats, *, width, sign, x_center, idx):
    """Surface vertical-rod exit device: push bar drives top+bottom rod bolts."""
    fy = r.front_y
    h = r.door_height
    z = r.z_bar
    rod_x = sign * (width - 0.035)
    rod_y = fy + 0.05
    # Push bar (drives the rods) + its mounts.
    _panic_static_mounts(door, r, mats, width=width, sign=sign, x_center=x_center, idx=idx)
    bar = _make_push_bar(model, r, mats, name=f"push_bar_{idx}", width=width)
    push_joint = f"door_{idx}_to_push_bar_{idx}"
    model.articulation(
        push_joint,
        ArticulationType.PRISMATIC,
        parent=door,
        child=bar,
        origin=Origin(xyz=(x_center, fy + 0.066, z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=0.20, lower=0.0, upper=r.bar_travel),
    )
    # Guide clamps (static host visuals) along the rod line.
    clamp_zs = [0.23 * r.hf, 0.78 * r.hf, z, h - 0.12]
    for k, cz in enumerate(clamp_zs):
        door.visual(
            Box((0.070, 0.048, 0.030)),
            origin=Origin(xyz=(rod_x, fy + 0.026, cz)),
            material=mats["hardware"],
            name=f"rod_clamp_{idx}_{k}", material_class_id="metal.stainless_matte",
        )
    mult = r.rod_retraction / r.bar_travel
    # Leave a center gap so the two rods do not collide when both retract inward
    # (top retracts down out of the header, bottom retracts up out of the sill).
    gap_c = 0.045
    # Top rod.
    top_len = h - (z + gap_c)
    top_center = (z + gap_c) + top_len / 2.0
    top_latch_z = h - 0.025
    top_rod = model.part("top_rod")
    top_rod.visual(
        Cylinder(radius=0.010, length=top_len),
        origin=Origin(),
        material=mats["hardware"],
        name="top_rod_bar", material_class_id="metal.stainless_matte",
    )
    top_rod.visual(
        Box((0.040, 0.055, 0.060)),
        origin=Origin(xyz=(0.0, 0.0, top_latch_z - top_center)),
        material=mats["hardware"],
        name="rod_top_latch", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        f"door_{idx}_to_top_rod",
        ArticulationType.PRISMATIC,
        parent=door,
        child=top_rod,
        origin=Origin(xyz=(rod_x, rod_y, top_center)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.15, lower=0.0, upper=r.rod_retraction),
        mimic=Mimic(joint=push_joint, multiplier=mult, offset=0.0),
    )
    # Bottom rod.
    bot_len = (z - gap_c) - _SILL
    bot_center = _SILL + bot_len / 2.0
    bot_latch_z = 0.045
    bottom_rod = model.part("bottom_rod")
    bottom_rod.visual(
        Cylinder(radius=0.010, length=bot_len),
        origin=Origin(),
        material=mats["hardware"],
        name="bottom_rod_bar", material_class_id="metal.stainless_matte",
    )
    bottom_rod.visual(
        Box((0.040, 0.055, 0.060)),
        origin=Origin(xyz=(0.0, 0.0, bot_latch_z - bot_center)),
        material=mats["hardware"],
        name="rod_bottom_latch", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        f"door_{idx}_to_bottom_rod",
        ArticulationType.PRISMATIC,
        parent=door,
        child=bottom_rod,
        origin=Origin(xyz=(rod_x, rod_y, bot_center)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.15, lower=0.0, upper=r.rod_retraction),
        mimic=Mimic(joint=push_joint, multiplier=mult, offset=0.0),
    )
    pairs = _bar_slider_allows(door.name, f"push_bar_{idx}", idx)
    for k in range(4):
        pairs.append((door.name, "top_rod", f"rod_clamp_{idx}_{k}", "top_rod_bar"))
        pairs.append((door.name, "top_rod", f"rod_clamp_{idx}_{k}", "rod_top_latch"))
        pairs.append((door.name, "bottom_rod", f"rod_clamp_{idx}_{k}", "bottom_rod_bar"))
        pairs.append((door.name, "bottom_rod", f"rod_clamp_{idx}_{k}", "rod_bottom_latch"))
    return pairs


def _add_crash_paddle(model, door, r, mats, *, width, sign, x_center, idx):
    """Pivoting push paddle (REVOLUTE) + independent center latch bolt."""
    fy = r.front_y
    z = r.z_bar
    pivot_y = fy + 0.045
    pivot_z = z + 0.05
    paddle = model.part("push_paddle")
    # Face plate hangs below the pivot; brackets reach back to the leaf face.
    paddle.visual(
        Box((0.28, 0.012, 0.10)),
        origin=Origin(xyz=(0.0, -0.006, -0.050)),
        material=mats["hardware"],
        name="paddle_face", material_class_id="metal.stainless_matte",
    )
    for nm, x in (("outer", -0.15), ("inner", 0.15)):
        paddle.visual(
            Box((0.025, 0.050, 0.020)),
            origin=Origin(xyz=(x, -0.030, 0.0)),
            material=mats["shadow"],
            name=f"paddle_{nm}_bracket", material_class_id="metal.blackened_gunmetal",
        )
        paddle.visual(
            Cylinder(radius=0.008, length=0.030),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, pi / 2.0, 0.0)),
            material=mats["hardware"],
            name=f"paddle_{nm}_pin", material_class_id="metal.stainless_matte",
        )
    paddle.visual(
        Box((0.24, 0.006, 0.055)),
        origin=Origin(xyz=(0.0, -0.014, -0.050)),
        material=mats["green"],
        name="paddle_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )
    for k in range(4):
        paddle.visual(
            Box((0.03, 0.004, 0.008)),
            origin=Origin(xyz=(-0.09 + k * 0.06, -0.018, -0.050)),
            material=mats["white"],
            name=f"paddle_tick_{k}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    model.articulation(
        f"door_{idx}_to_push_paddle",
        ArticulationType.REVOLUTE,
        parent=door,
        child=paddle,
        origin=Origin(xyz=(x_center, pivot_y, pivot_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=95.0, velocity=2.0, lower=0.0, upper=r.paddle_open),
    )
    latch = _add_latch_bolt(model, door, r, mats, width=width, sign=sign, idx=idx,
                            driver=None, mult=1.0)
    pairs = []
    paddle_elems = ("paddle_outer_bracket", "paddle_inner_bracket",
                    "paddle_outer_pin", "paddle_inner_pin",
                    "paddle_face", "paddle_label") + tuple(f"paddle_tick_{k}" for k in range(4))
    for host in ("door_body", "lock_rail"):
        for e in paddle_elems:
            pairs.append((door.name, "push_paddle", host, e))
    return pairs + latch


_PANIC_DISPATCH = {
    "touch_bar": _add_touch_bar,
    "vertical_rod": _add_vertical_rod,
    "crash_paddle": _add_crash_paddle,
    "recessed_bar": _add_recessed_bar,
}


def _add_closer(model, door, frame, r, mats, *, sign, hinge_x, body_hy):
    """Overhead surface closer: housing on the leaf + a short REVOLUTE arm mimicking
    the hinge (folds toward the frame head corner as the door opens)."""
    front = body_hy  # mount to the leaf's actual front face (glass or slab)
    z = r.door_height - 0.22
    # Housing sits inboard (toward leaf center) so the folding arm stays clear of
    # the hinge-side jamb through the full swing.
    x_center = sign * 0.34
    door.visual(
        Box((0.240, 0.020, 0.060)),
        origin=Origin(xyz=(x_center, front + 0.005, z)),
        material=mats["shadow"],
        name="closer_mount_plate", material_class_id="metal.blackened_gunmetal",
    )
    door.visual(
        Box((0.220, 0.048, 0.048)),
        origin=Origin(xyz=(x_center, front + 0.030, z)),
        material=mats["hardware"],
        name="closer_housing", material_class_id="metal.stainless_matte",
    )
    # Spindle at the hinge-ward end of the housing.
    spindle_x = x_center - sign * 0.10
    door.visual(
        Cylinder(radius=0.014, length=0.030),
        origin=Origin(xyz=(spindle_x, front + 0.030, z + 0.030)),
        material=mats["hardware"],
        name="closer_spindle", material_class_id="metal.stainless_matte",
    )
    # Anchor shoe on the frame header above the leaf (visual only; arm is leaf child).
    frame.visual(
        Box((0.05, 0.05, 0.04)),
        origin=Origin(xyz=(-sign * (hinge_x - 0.30), 0.055, r.door_height + 0.06)),
        material=mats["hardware"],
        name="closer_anchor_shoe", material_class_id="metal.stainless_matte",
    )
    arm = model.part("closer_arm")
    # Short arm extends back toward the hinge (local -x) so its tip tucks into the
    # frame head corner at full open rather than sweeping past the jamb.
    arm.visual(
        Box((0.16, 0.016, 0.012)),
        origin=Origin(xyz=(-0.08, 0.0, 0.0)),
        material=mats["hardware"],
        name="closer_arm_bar", material_class_id="metal.stainless_matte",
    )
    arm.visual(
        Cylinder(radius=0.014, length=0.024),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="closer_arm_bushing", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        f"{door.name}_to_closer_arm",
        ArticulationType.REVOLUTE,
        parent=door,
        child=arm,
        origin=Origin(xyz=(spindle_x, front + 0.030, z + 0.030)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=25.0, velocity=1.2, lower=0.0, upper=0.40),
        mimic=Mimic(joint=f"frame_to_{door.name}", multiplier=0.30, offset=0.0),
    )
    pairs = []
    for host in ("closer_spindle", "closer_housing", "closer_mount_plate", "door_body",
                 "lock_rail", "top_rail", "bottom_rail", "hinge_stile", "meeting_stile",
                 "exit_sign"):
        for e in ("closer_arm_bushing", "closer_arm_bar"):
            pairs.append((door.name, "closer_arm", host, e))
    # The folded arm tucks into the frame head corner at full open (real closer geometry).
    for host in ("jamb_0", "jamb_1", "header", "closer_anchor_shoe",
                 "transom_glass_0", "transom_mullion"):
        for e in ("closer_arm_bushing", "closer_arm_bar"):
            pairs.append(("frame", "closer_arm", host, e))
    return pairs


# ===========================================================================
# Build
# ===========================================================================
def build_emergency_exit_door(
    config: EmergencyExitDoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"eed_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    frame_dict, leaves = _leaf_layout(r)
    frame = _build_frame(model, r, mats, frame_dict)

    allow_pairs: list[tuple[str, str, str, str]] = []

    for idx, (name, sign, width, active, hinge_x, is_primary) in enumerate(leaves):
        door = model.part(name)
        # ③ leaf form applies to every active leaf; inactive leaf is a plain slab.
        leaf_form = r.leaf_form if active else "solid_slab"
        _add_leaf_body(door, r, mats, width=width, sign=sign, leaf_form=leaf_form)
        x_center = sign * width / 2.0

        # Leaf hinge (pin hinge, grandfathered; origin on the hinge_line hardware).
        model.articulation(
            f"frame_to_{name}",
            ArticulationType.REVOLUTE,
            parent=frame,
            child=door,
            origin=Origin(xyz=(-sign * hinge_x, 0.0, _SILL)),
            axis=(0.0, 0.0, sign),
            motion_limits=MotionLimits(effort=90.0, velocity=1.2, lower=0.0, upper=r.hinge_upper),
        )

        if not active:
            _add_flush_bolts(door, r, mats, width=width, sign=sign)
            continue

        if is_primary:
            body_hy = 0.005 if leaf_form == "full_glazed" else r.front_y
            builder = _PANIC_DISPATCH[r.panic_hardware]
            allow_pairs += builder(model, door, r, mats, width=width, sign=sign,
                                   x_center=x_center, idx=idx)
            if r.closer == "overhead_arm":
                allow_pairs += _add_closer(model, door, frame, r, mats, sign=sign,
                                           hinge_x=hinge_x, body_hy=body_hy)
        else:
            # Secondary active leaf (double_leaf door_1) carries a plain touch bar.
            allow_pairs += _add_touch_bar(model, door, r, mats, width=width, sign=sign,
                                          x_center=x_center, idx=idx)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["allow_pairs"] = allow_pairs
    return model


def build_seeded_emergency_exit_door(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_emergency_exit_door(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_emergency_exit_door_tests(
    object_model: ArticulatedObject,
    config: EmergencyExitDoorConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    part_names = {p.name for p in object_model.parts}

    # ---- Captured-shaft / mortise / bracket allowances (element-scoped). ----
    for parent_name, child_name, elem_a, elem_b in object_model.meta.get("allow_pairs", []):
        if parent_name in part_names and child_name in part_names:
            ctx.allow_overlap(
                object_model.get_part(parent_name),
                object_model.get_part(child_name),
                elem_a=elem_a,
                elem_b=elem_b,
                reason="captured slider / mortised bar / hinge bracket rides on the leaf hardware.",
            )

    # Closed leaves seat against frame jambs / stops; closed pair meets at seam.
    for name in [lf[0] for lf in _leaf_layout(r)[1]]:
        if name in part_names:
            ctx.allow_overlap(
                object_model.get_part(name), frame,
                reason="closed leaf hinge edge / hardware seats against the frame jamb reveal.",
            )

    # ---- Baseline gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: frame root + at least one hinged active leaf w/ panic hardware. ----
    ctx.check("frame root present", "frame" in part_names)
    ctx.check("door_0 primary leaf present", "door_0" in part_names)
    hinge0 = object_model.get_articulation("frame_to_door_0")
    ctx.check(
        "frame_to_door_0 REVOLUTE about vertical Z",
        hinge0.articulation_type == ArticulationType.REVOLUTE and abs(hinge0.axis[2]) > 0.99,
        details=f"type={hinge0.articulation_type} axis={tuple(hinge0.axis)}",
    )
    door0 = object_model.get_part("door_0")
    ctx.check(
        "door_0 carries an exit sign",
        any(v.name == "exit_sign" for v in door0.visuals),
    )
    panic_present = (
        "push_bar_0" in part_names
        or "push_paddle" in part_names
    )
    ctx.check("door_0 has panic hardware", panic_present, details=r.panic_hardware)

    # ---- Multiplicity: leaf count matches opening_config. ----
    n_leaves = sum(1 for n in ("door_0", "door_1") if n in part_names)
    ctx.check(
        "leaf count matches opening_config",
        n_leaves == r.leaf_count,
        details=f"n={n_leaves} expected={r.leaf_count} cfg={r.opening_config}",
    )

    # ---- ③ leaf form realized on door_0. ----
    d0_names = {v.name for v in door0.visuals}
    if r.leaf_form in ("vision_lite", "narrow_vision"):
        ctx.check("vision glass present on door_0", "vision_glass" in d0_names)
    elif r.leaf_form == "full_glazed":
        ctx.check("full glazed body + stiles present",
                  "door_body" in d0_names and "meeting_stile" in d0_names)

    # ---- Header D. ----
    frame_names = {v.name for v in frame.visuals}
    if r.header_style == "glazed_transom":
        ctx.check("glazed transom present",
                  "transom_glass_0" in frame_names and "transom_header" in frame_names)
    if r.opening_config == "single_plus_sidelite":
        ctx.check("fixed sidelite glass present", "sidelite_glass" in frame_names)

    # ---- Closed-pose center seam (double leaf). ----
    if r.opening_config == "double_leaf" and "door_1" in part_names:
        # Whole-leaf AABB (edges/meeting stiles), not the inset glass body.
        ctx.expect_gap(
            object_model.get_part("door_1"), door0, axis="x",
            min_gap=-0.03, max_gap=0.10,
            name="closed leaves meet at a narrow center seam",
        )

    # ---- Sampled-pose non-penetration (Rule 5). ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # ---- Targeted mechanism poses (Rule 5). ----
    # Leaf swings outward (+Y) when opened.
    closed0 = ctx.part_world_aabb(door0)
    with ctx.pose({hinge0: r.hinge_upper * 0.8}):
        open0 = ctx.part_world_aabb(door0)
    if closed0 is not None and open0 is not None:
        ctx.check(
            "door_0 swings outward (+Y) when opened",
            open0[1][1] > closed0[1][1] + 0.35,
            details=f"closed={closed0[1][1]:.3f} open={open0[1][1]:.3f}",
        )

    # Panic hardware actuation.
    if r.panic_hardware in ("touch_bar", "recessed_bar", "vertical_rod"):
        bar = object_model.get_part("push_bar_0")
        push_j = object_model.get_articulation("door_0_to_push_bar_0")
        rest = ctx.part_world_position(bar)
        with ctx.pose({push_j: r.bar_travel}):
            pressed = ctx.part_world_position(bar)
        if rest is not None and pressed is not None:
            ctx.check(
                "push bar depresses toward the leaf (-Y)",
                pressed[1] < rest[1] - 0.008,
                details=f"rest={rest[1]:.4f} pressed={pressed[1]:.4f}",
            )
        if r.panic_hardware == "vertical_rod":
            top_rod = object_model.get_part("top_rod")
            rest_t = ctx.part_world_position(top_rod)
            with ctx.pose({push_j: r.bar_travel}):
                ret_t = ctx.part_world_position(top_rod)
            if rest_t is not None and ret_t is not None:
                ctx.check(
                    "top rod retracts downward when bar pressed",
                    ret_t[2] < rest_t[2] - 0.005,
                    details=f"rest={rest_t[2]:.4f} ret={ret_t[2]:.4f}",
                )
        if r.panic_hardware == "recessed_bar":
            bolt = object_model.get_part("latch_bolt")
            rest_b = ctx.part_world_position(bolt)
            with ctx.pose({push_j: r.bar_travel}):
                ret_b = ctx.part_world_position(bolt)
            if rest_b is not None and ret_b is not None:
                ctx.check(
                    "latch bolt retracts when bar pressed",
                    abs(ret_b[0] - rest_b[0]) > 0.010,
                    details=f"rest={rest_b[0]:.4f} ret={ret_b[0]:.4f}",
                )
    elif r.panic_hardware == "crash_paddle":
        paddle = object_model.get_part("push_paddle")
        pad_j = object_model.get_articulation("door_0_to_push_paddle")
        rest = ctx.part_element_world_aabb(paddle, elem="paddle_face")
        with ctx.pose({pad_j: r.paddle_open}):
            pressed = ctx.part_element_world_aabb(paddle, elem="paddle_face")
        if rest is not None and pressed is not None:
            rest_cy = (rest[0][1] + rest[1][1]) / 2.0
            press_cy = (pressed[0][1] + pressed[1][1]) / 2.0
            ctx.check(
                "paddle face swings toward the leaf (-Y) when pressed",
                press_cy < rest_cy - 0.006,
                details=f"rest={rest_cy:.4f} pressed={press_cy:.4f}",
            )

    # Overhead closer arm folds as the door opens.
    if r.closer == "overhead_arm" and "closer_arm" in part_names:
        arm = object_model.get_part("closer_arm")
        rest_a = ctx.part_world_aabb(arm)
        with ctx.pose({hinge0: r.hinge_upper * 0.6}):
            open_a = ctx.part_world_aabb(arm)
        ctx.check(
            "closer arm moves as the door swings",
            rest_a is not None and open_a is not None
            and (abs(open_a[1][1] - rest_a[1][1]) > 0.02 or abs(open_a[1][0] - rest_a[1][0]) > 0.02),
            details=f"rest={rest_a}, open={open_a}",
        )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
    )

    return ctx.report()


__all__ = (
    "EmergencyExitDoorConfig",
    "ResolvedEmergencyExitDoorConfig",
    "build_emergency_exit_door",
    "build_seeded_emergency_exit_door",
    "config_from_seed",
    "resolve_config",
    "run_emergency_exit_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
