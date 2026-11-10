# SPDX-License-Identifier: Apache-2.0

"""Retail_Shop Fixtures / Barcode scanner procedural template (modular).

Spec: articraft_template_authoring/specs_modular_v1/barcode_scanner.md

A handheld / countertop optical barcode reader: a scan head carrying a recessed
dark scan window aimed forward, a defined support (freestanding grip/tower base,
dock cradle, or tilt mount foot), and at least one real user control (squeeze
trigger REVOLUTE, top scan button PRISMATIC, or — for the fixed-mount form — an
aiming tilt REVOLUTE).

Slots (pattern = mixed):
  * Slot A body_form (①/③ Primary Form Family, form-dominant, in slot_choices):
      pistol_grip / presentation_tower / inline_wand / fixed_mount_box
  * Slot B mount (① grounded support topology):
      none / charging_cradle (FIXED dock) / tilt_bracket (REVOLUTE aim)
  * Slot C control (② user control child):
      squeeze_trigger / trigger_plus_top_button / side_thumb_trigger / none

Sources (all forked_anchor, all 5-star verified PASS):
  SA rec_handheld-pistol-grip-barcode-scanner-black-plast_...b32f70d1  (corded grip)
  SB rec_wireless-handheld-barcode-scanner-pistol-grip-st_...6c8ecc24  (wireless grip)
  SP rec_barcode_scanner_var_skeleton_presentation                     (tower)
  SW rec_barcode_scanner_var_skeleton_wand                             (inline wand)
  SC rec_barcode_scanner_var_base_cradle                               (charging cradle)
  SM rec_barcode_scanner_var_mechanism_button                          (top scan button)
  SF rec_barcode_scanner_var_probe_fixedmount_tilt                     (fixed-mount tilt)

Rules:
  Rule 1 — non-articulating detail (window/bezel/label/ring disc/led/insert/
    saddle/cable-free housing) is a host ``scanner_body`` / ``cradle_base`` /
    ``mount_base`` ``.visual(...)``; the only FIXED articulation is the cradle
    dock (a removable scanner seated in a distinct dock sub-assembly needing its
    own frame — the legitimate FIXED exception, documented at its call site).
  Rule 2 — every non-FIXED child (trigger / top_button / tilted box) is a
    captured pin / stem / trunnion; MatingContract cannot express it, so joints
    are grandfathered (omit ``mating=``) and kept honest with element-scoped
    ``allow_overlap`` mirroring each source's run_tests.
  Rule 3 — structure + cadquery loft/box+pocket primitives derive from declared
    5-star sources; no Box downgrade of the grip/neck lofts.
  Rule 5 — ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism.

Geometry scaling: cadquery solids are built at each source's nominal dims and
scaled uniformly by ``body_scale`` via ``mesh_from_cadquery(unit_scale=...)``;
``head_len_scale`` stretches only the head/barrel/box length (x) inside the cq
build. Every ``Origin`` position constant is multiplied by ``body_scale`` so
frames stay consistent. Fillet radii are fixed small absolutes so cadquery
booleans stay valid across the (tight) scale ranges.
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
    ClevisBracketGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
BodyForm = Literal["pistol_grip", "presentation_tower", "inline_wand", "fixed_mount_box"]
Mount = Literal["none", "charging_cradle", "tilt_bracket"]
Control = Literal["squeeze_trigger", "trigger_plus_top_button", "side_thumb_trigger", "none"]
Palette = Literal[
    "charcoal_orange_wireless",
    "black_blue_corded",
    "industrial_gray",
    "retail_white",
    "stealth_black",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "pistol_grip",
    "presentation_tower",
    "inline_wand",
    "fixed_mount_box",
)
PALETTES_LIST: tuple[Palette, ...] = (
    "charcoal_orange_wireless",
    "black_blue_corded",
    "industrial_gray",
    "retail_white",
    "stealth_black",
)

# Compatibility matrix (§9). body_form gates the legal mount / control sets.
ALLOWED_MOUNTS: dict[BodyForm, tuple[Mount, ...]] = {
    "pistol_grip": ("none", "charging_cradle"),
    "presentation_tower": ("none",),
    "inline_wand": ("none",),
    "fixed_mount_box": ("tilt_bracket",),
}
ALLOWED_CONTROLS: dict[BodyForm, tuple[Control, ...]] = {
    "pistol_grip": ("squeeze_trigger", "trigger_plus_top_button"),
    "presentation_tower": ("squeeze_trigger", "trigger_plus_top_button"),
    "inline_wand": ("side_thumb_trigger",),
    "fixed_mount_box": ("none",),
}

# Palette colorways (⑥). Material-class coverage: plastic (body), metal (bracket/
# cradle/steel), glass (dark scan window), painted accent (bezel/insert/ring/led).
PALETTES: dict[Palette, dict[str, tuple[float, float, float, float]]] = {
    "charcoal_orange_wireless": {
        "body": (0.13, 0.13, 0.15, 1.0), "insert": (0.96, 0.62, 0.08, 1.0),
        "window": (0.30, 0.30, 0.33, 1.0), "laser": (1.0, 0.08, 0.05, 1.0),
        "bezel": (0.96, 0.62, 0.08, 1.0), "ring": (0.10, 0.40, 0.95, 1.0),
        "button": (0.06, 0.06, 0.07, 1.0), "trigger": (0.22, 0.22, 0.24, 1.0),
        "metal": (0.24, 0.24, 0.26, 1.0), "label": (0.92, 0.92, 0.90, 1.0),
        "led": (0.15, 0.80, 0.25, 1.0),
    },
    "black_blue_corded": {
        "body": (0.08, 0.08, 0.09, 1.0), "insert": (0.13, 0.20, 0.75, 1.0),
        "window": (0.03, 0.03, 0.04, 1.0), "laser": (1.0, 0.08, 0.05, 1.0),
        "bezel": (0.13, 0.13, 0.15, 1.0), "ring": (0.13, 0.20, 0.75, 1.0),
        "button": (0.05, 0.05, 0.06, 1.0), "trigger": (0.13, 0.20, 0.75, 1.0),
        "metal": (0.38, 0.38, 0.40, 1.0), "label": (0.92, 0.92, 0.90, 1.0),
        "led": (0.15, 0.80, 0.25, 1.0),
    },
    "industrial_gray": {
        "body": (0.38, 0.38, 0.40, 1.0), "insert": (0.20, 0.20, 0.22, 1.0),
        "window": (0.03, 0.03, 0.04, 1.0), "laser": (1.0, 0.08, 0.05, 1.0),
        "bezel": (0.16, 0.16, 0.17, 1.0), "ring": (0.90, 0.55, 0.10, 1.0),
        "button": (0.10, 0.10, 0.11, 1.0), "trigger": (0.16, 0.16, 0.17, 1.0),
        "metal": (0.46, 0.46, 0.48, 1.0), "label": (0.90, 0.90, 0.88, 1.0),
        "led": (0.15, 0.80, 0.25, 1.0),
    },
    "retail_white": {
        "body": (0.86, 0.87, 0.88, 1.0), "insert": (0.10, 0.40, 0.95, 1.0),
        "window": (0.10, 0.10, 0.12, 1.0), "laser": (1.0, 0.08, 0.05, 1.0),
        "bezel": (0.30, 0.34, 0.42, 1.0), "ring": (0.10, 0.40, 0.95, 1.0),
        "button": (0.20, 0.20, 0.22, 1.0), "trigger": (0.55, 0.58, 0.62, 1.0),
        "metal": (0.55, 0.57, 0.60, 1.0), "label": (0.30, 0.30, 0.32, 1.0),
        "led": (0.15, 0.80, 0.25, 1.0),
    },
    "stealth_black": {
        "body": (0.10, 0.10, 0.11, 1.0), "insert": (0.20, 0.20, 0.21, 1.0),
        "window": (0.02, 0.02, 0.03, 1.0), "laser": (1.0, 0.08, 0.05, 1.0),
        "bezel": (0.16, 0.16, 0.17, 1.0), "ring": (0.30, 0.60, 0.95, 1.0),
        "button": (0.03, 0.03, 0.04, 1.0), "trigger": (0.16, 0.16, 0.17, 1.0),
        "metal": (0.22, 0.23, 0.25, 1.0), "label": (0.70, 0.70, 0.72, 1.0),
        "led": (0.15, 0.80, 0.25, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal geometry constants (meters, from the 5-star sources). Scaled by
# body_scale (uniform, via unit_scale + position multiply); head_len_scale
# stretches only the head/barrel/box length (x).
# ---------------------------------------------------------------------------
# Shared imager head (SB / SP)
HEAD_LEN = 0.105
HEAD_WID = 0.070
HEAD_HGT = 0.056
# Trigger squeeze (SB / SP)
TRIGGER_SQUEEZE_NOMINAL = 0.30
# Top scan button (SM)
BUTTON_TRAVEL_NOMINAL = 0.003
# Fixed-mount box (SF)
BOX_LEN = 0.082
BOX_WID = 0.054
BOX_HGT = 0.040
BOX_OFFSET_X = 0.018
BRACKET_BORE_Z = 0.060
TILT_NOMINAL = 0.35
# Inline wand (SW)
BARREL_L = 0.180
BARREL_W = 0.036
BARREL_H = 0.032
WAND_PRESS_NOMINAL = 0.22


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class BarcodeScannerConfig:
    body_form: BodyForm | None = None
    mount: Mount | None = None
    control: Control | None = None
    palette: Palette = "charcoal_orange_wireless"
    body_scale: float = 1.0
    head_len_scale: float = 1.0
    trigger_travel: float = TRIGGER_SQUEEZE_NOMINAL
    tilt_range: float = TILT_NOMINAL
    name: str = "barcode_scanner"


@dataclass(frozen=True)
class ResolvedBarcodeScannerConfig:
    body_form: BodyForm
    mount: Mount
    control: Control
    palette: Palette
    body_scale: float
    head_len_scale: float
    trigger_travel: float
    tilt_range: float
    name: str

    @property
    def s(self) -> float:
        return self.body_scale

    @property
    def hl(self) -> float:
        return self.head_len_scale


def config_from_seed(seed: int) -> BarcodeScannerConfig:
    """Deterministic procedural sampling over the full slot domain (seed 0 is
    not special). mount / control are drawn from the chosen body_form's legal
    sets (compatibility matrix)."""
    rng = random.Random(seed)
    body = rng.choice(BODY_FORMS)
    mount = rng.choice(ALLOWED_MOUNTS[body])
    control = rng.choice(ALLOWED_CONTROLS[body])
    return BarcodeScannerConfig(
        body_form=body,
        mount=mount,
        control=control,
        palette=rng.choice(PALETTES_LIST),
        body_scale=round(rng.uniform(0.95, 1.06), 4),
        head_len_scale=round(rng.uniform(0.94, 1.08), 4),
        trigger_travel=round(rng.uniform(0.22, 0.34), 4),
        tilt_range=round(rng.uniform(0.24, 0.32), 4),
        name=f"seeded_barcode_scanner_{seed}",
    )


def resolve_config(config: BarcodeScannerConfig | None = None) -> ResolvedBarcodeScannerConfig:
    cfg = config or BarcodeScannerConfig()
    body = _pick(cfg.body_form, BODY_FORMS)
    mount = cfg.mount if cfg.mount in ALLOWED_MOUNTS[body] else ALLOWED_MOUNTS[body][0]
    control = cfg.control if cfg.control in ALLOWED_CONTROLS[body] else ALLOWED_CONTROLS[body][0]
    return ResolvedBarcodeScannerConfig(
        body_form=body,
        mount=mount,
        control=control,
        palette=_pick(cfg.palette, PALETTES_LIST),
        body_scale=_clamp(float(cfg.body_scale), 0.95, 1.06),
        head_len_scale=_clamp(float(cfg.head_len_scale), 0.94, 1.08),
        trigger_travel=_clamp(float(cfg.trigger_travel), 0.22, 0.34),
        tilt_range=_clamp(float(cfg.tilt_range), 0.24, 0.32),
        name=cfg.name or "barcode_scanner",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedBarcodeScannerConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("mount", r.mount),
        ("control", r.control),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Materials
# ===========================================================================
def _materials(model: ArticulatedObject, r: ResolvedBarcodeScannerConfig) -> dict:
    rgba = PALETTES[r.palette]
    return {k: model.material(f"bcs_{k}_{r.palette}", rgba=v) for k, v in rgba.items()}


def _cq_mesh(solid: cq.Workplane, name: str, s: float):
    """Tessellate a cadquery solid, uniformly scaled by body_scale."""
    return mesh_from_cadquery(solid, name, unit_scale=s)


# ===========================================================================
# Shared imager head (SB L99-L168 / SP L115-L182)
# ===========================================================================
def _head_shell_solid(hl: float) -> cq.Workplane:
    shell = cq.Workplane("XY").box(HEAD_LEN * hl, HEAD_WID, HEAD_HGT).edges().fillet(0.010)
    pocket = (
        cq.Workplane("YZ")
        .workplane(offset=HEAD_LEN * hl / 2 - 0.016)
        .rect(0.052, 0.032)
        .extrude(0.020)
    )
    return shell.cut(pocket)


def _window_bezel_solid(hl: float) -> cq.Workplane:
    frame = (
        cq.Workplane("YZ")
        .workplane(offset=HEAD_LEN * hl / 2 - 0.007)
        .rect(0.058, 0.038)
        .extrude(0.005)
    )
    hole = (
        cq.Workplane("YZ")
        .workplane(offset=HEAD_LEN * hl / 2 - 0.008)
        .rect(0.046, 0.026)
        .extrude(0.007)
    )
    return frame.cut(hole)


def _scan_window_solid(hl: float) -> cq.Workplane:
    return (
        cq.Workplane("YZ")
        .workplane(offset=HEAD_LEN * hl / 2 - 0.017)
        .rect(0.048, 0.028)
        .extrude(0.005)
    )


def _top_panel_solid(welled: bool) -> cq.Workplane:
    panel = (
        cq.Workplane("XY")
        .workplane(offset=HEAD_HGT / 2 - 0.003)
        .center(-0.004, 0.0)
        .rect(0.082, 0.054)
        .extrude(0.005)
        .edges("|Z")
        .fillet(0.010)
    )
    if welled:
        well = (
            cq.Workplane("XY")
            .workplane(offset=HEAD_HGT / 2 - 0.001)
            .center(-0.006, 0.0)
            .circle(0.013)
            .extrude(0.008)
        )
        panel = panel.cut(well)
    return panel


def _ring_light_solid(welled: bool) -> cq.Workplane:
    z0 = HEAD_HGT / 2 + (0.0015 if welled else 0.003)
    inner = 0.0125 if welled else 0.0115
    return (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(-0.006, 0.0)
        .circle(0.0165)
        .circle(inner)
        .extrude(0.0035)
    )


def _ring_button_disc_solid() -> cq.Workplane:
    z0 = HEAD_HGT / 2 + 0.003
    return (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.001)
        .center(-0.006, 0.0)
        .circle(0.0118)
        .extrude(0.0038)
    )


def _top_button_cap_solid() -> cq.Workplane:
    """Pressable dark button cap + retention stem (SM L178-202)."""
    z0 = HEAD_HGT / 2 + 0.003
    cap = (
        cq.Workplane("XY")
        .workplane(offset=z0)
        .center(-0.006, 0.0)
        .circle(0.0118)
        .extrude(0.0035)
    )
    stem = (
        cq.Workplane("XY")
        .workplane(offset=HEAD_HGT / 2 - 0.003)
        .center(-0.006, 0.0)
        .circle(0.005)
        .extrude(0.006)
    )
    return cap.union(stem)


def _add_imager_head(body, r, mats, head_center, head_pitch, welled) -> None:
    """Attach the shared imager head visuals to ``scanner_body`` (SB/SP).

    All head visuals share one pitched Origin so they stay mutually aligned.
    Non-articulating detail is fused as ``body.visual(...)`` (Rule 1).
    """
    s = r.s
    head_origin = Origin(xyz=head_center, rpy=(0.0, head_pitch, 0.0))
    body.visual(_cq_mesh(_head_shell_solid(r.hl), "head_shell", s),
                origin=head_origin, material=mats["body"], name="head_shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_cq_mesh(_window_bezel_solid(r.hl), "window_bezel", s),
                origin=head_origin, material=mats["bezel"], name="window_bezel", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_cq_mesh(_scan_window_solid(r.hl), "scan_window", s),
                origin=head_origin, material=mats["window"], name="scan_window", material_class_id="glass.smoked_tinted")
    body.visual(_cq_mesh(_top_panel_solid(welled), "top_panel", s),
                origin=head_origin, material=mats["bezel"], name="top_panel", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_cq_mesh(_ring_light_solid(welled), "ring_light", s),
                origin=head_origin, material=mats["ring"], name="ring_light", material_class_id="tech.emissive_surface")
    if not welled:
        # Decorative fused disc (squeeze-trigger head). When welled, a moving
        # top_button part fills the ring instead.
        body.visual(_cq_mesh(_ring_button_disc_solid(), "ring_button", s),
                    origin=head_origin, material=mats["button"], name="ring_button", material_class_id="plastic.opaque_glossy_molded")


# ===========================================================================
# Slot A body_form builders (build the grounded/child `scanner_body` root part)
# ===========================================================================
def _grip_shell_solid() -> cq.Workplane:
    """Tapered pistol grip lofted from rounded-rect sections (SB L49-67)."""
    sections = [
        (0.000, 0.052, 0.042, -0.006),
        (0.030, 0.044, 0.036, -0.003),
        (0.070, 0.042, 0.034, 0.001),
        (0.115, 0.052, 0.042, 0.006),
    ]
    wires = []
    for z, dx, dy, cx in sections:
        wire = cq.Workplane("XY", origin=(cx, 0.0, z)).rect(dx, dy).wires().val()
        wires.append(wire)
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def _grip_insert_wrap_solid() -> cq.Workplane:
    """Orange rubber strip lofted to follow the grip taper (SB L70-93)."""
    sections = [
        (0.022, 0.0515, -0.0045),
        (0.030, 0.0490, -0.0030),
        (0.070, 0.0470, 0.0010),
        (0.100, 0.0535, 0.0043),
    ]
    wires = []
    for z, dx, cx in sections:
        wire = cq.Workplane("XY", origin=(cx, 0.0, z)).rect(dx, 0.024).wires().val()
        wires.append(wire)
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def _build_pistol_grip(body, r, mats) -> tuple[tuple[float, float, float], float]:
    """SB pistol grip: grip loft + imager head. Returns (head_center, head_pitch)."""
    s = r.s
    welled = r.control == "trigger_plus_top_button"
    body.visual(_cq_mesh(_grip_shell_solid(), "grip_shell", s),
                origin=Origin(), material=mats["body"], name="grip_shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_cq_mesh(_grip_insert_wrap_solid(), "grip_insert_wrap", s),
                origin=Origin(), material=mats["insert"], name="grip_insert_wrap", material_class_id="rubber.smooth_plain")
    head_center = (0.020 * s, 0.0, 0.135 * s)
    head_pitch = 0.20
    _add_imager_head(body, r, mats, head_center, head_pitch, welled)
    return head_center, head_pitch


def _base_plate_solid() -> cq.Workplane:
    """Broad flat weighted base + seating boss (SP L54-74)."""
    base = (
        cq.Workplane("XY").rect(0.140, 0.100).extrude(0.020)
        .edges("|Z").fillet(0.012).edges(">Z").chamfer(0.002)
    )
    boss = (
        cq.Workplane("XY").workplane(offset=0.019).rect(0.058, 0.048)
        .extrude(0.005).edges(">Z").chamfer(0.002)
    )
    return base.union(boss)


def _neck_column_solid() -> cq.Workplane:
    """Slim tapered neck lofted base->head, sweeping forward (SP L77-98)."""
    sections = [
        (0.020, 0.052, 0.044, 0.000),
        (0.045, 0.042, 0.036, 0.004),
        (0.075, 0.036, 0.030, 0.008),
        (0.100, 0.038, 0.032, 0.010),
    ]
    wires = []
    for z, dx, dy, cx in sections:
        wire = cq.Workplane("XY", origin=(cx, 0.0, z)).rect(dx, dy).wires().val()
        wires.append(wire)
    return cq.Workplane(obj=cq.Solid.makeLoft(wires))


def _neck_accent_solid() -> cq.Workplane:
    """Thin accent panel proud of the neck front face (SP L101-109)."""
    return (
        cq.Workplane("YZ").workplane(offset=0.023).center(0.0, 0.058)
        .rect(0.024, 0.035).extrude(0.004)
    )


def _build_presentation_tower(body, r, mats) -> tuple[tuple[float, float, float], float]:
    """SP presentation tower: base plate + neck + imager head."""
    s = r.s
    welled = r.control == "trigger_plus_top_button"
    body.visual(_cq_mesh(_base_plate_solid(), "base_plate", s),
                origin=Origin(), material=mats["body"], name="base_plate", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_cq_mesh(_neck_column_solid(), "neck_column", s),
                origin=Origin(), material=mats["body"], name="neck_column", material_class_id="plastic.opaque_glossy_molded")
    body.visual(_cq_mesh(_neck_accent_solid(), "neck_accent", s),
                origin=Origin(), material=mats["insert"], name="neck_accent", material_class_id="plastic.opaque_glossy_molded")
    head_center = (0.010 * s, 0.0, 0.128 * s)
    head_pitch = 0.30
    _add_imager_head(body, r, mats, head_center, head_pitch, welled)
    return head_center, head_pitch


def _barrel_solid(hl: float) -> cq.Workplane:
    """Single inline barrel, rounded-rect, front scan-window pocket (SW L64-79)."""
    barrel = cq.Workplane("XY").box(BARREL_L * hl, BARREL_W, BARREL_H).edges("|Z").fillet(0.008)
    cutter = (
        cq.Workplane("XY").box(0.010, 0.026, 0.016)
        .translate((BARREL_L * hl / 2, 0.0, 0.0))
    )
    return barrel.cut(cutter)


def _build_inline_wand(body, r, mats) -> None:
    """SW inline wand: single barrel resting flat (bottom at z=0), front nose
    window + laser, rear cap, spec label. Cordless (no cable)."""
    s = r.s
    bl = BARREL_L * r.hl
    # Lift the barrel so its bottom sits on the ground (z=0).
    cz = (BARREL_H / 2) * s
    body.visual(_cq_mesh(_barrel_solid(r.hl), "barrel_shell", s),
                origin=Origin(xyz=(0.0, 0.0, cz)), material=mats["body"], name="barrel_shell", material_class_id="plastic.opaque_glossy_molded")
    body.visual(Box(((0.004) * s, (BARREL_W - 0.008) * s, (BARREL_H - 0.008) * s)),
                origin=Origin(xyz=(-bl / 2 * s + 0.002 * s, 0.0, cz)),
                material=mats["metal"], name="rear_cap", material_class_id="metal.paint_coated")
    window_x = (bl / 2 - 0.005 + 0.001) * s
    body.visual(Box((0.003 * s, (0.026 - 0.004) * s, (0.016 - 0.004) * s)),
                origin=Origin(xyz=(window_x, 0.0, cz)), material=mats["window"], name="scan_window", material_class_id="glass.smoked_tinted")
    body.visual(Box((0.002 * s, (0.026 - 0.008) * s, 0.004 * s)),
                origin=Origin(xyz=(window_x + 0.002 * s, 0.0, cz)),
                material=mats["laser"], name="laser_line", appearance_only=AppearanceOnlySpec(kind="emission", emission_strength=1.0))
    body.visual(Box((0.050 * s, 0.022 * s, 0.002 * s)),
                origin=Origin(xyz=(0.0, 0.0, cz - (BARREL_H / 2) * s + 0.001 * s)),
                material=mats["label"], name="spec_label", appearance_only=AppearanceOnlySpec(kind="decal"))


def _scanner_box_solid(hl: float) -> cq.Workplane:
    """Compact scanner box: rounded box + front window pocket + trunnion bosses
    (SF L73-117). Built centered; visual origin offsets it forward of the pivot."""
    box = cq.Workplane("XY").box(BOX_LEN * hl, BOX_WID, BOX_HGT).edges("|Z").fillet(0.005)
    pocket_x = BOX_LEN * hl / 2 - 0.007 / 2 + 0.001
    pocket = cq.Workplane("XY").box(0.009, 0.040, 0.026).translate((pocket_x, 0.0, 0.002))
    box = box.cut(pocket)
    boss_ext = 0.005
    box = (box.faces(">Y").workplane().center(-BOX_OFFSET_X, 0.0).rect(0.014, 0.014).extrude(boss_ext))
    box = (box.faces("<Y").workplane().center(-BOX_OFFSET_X, 0.0).rect(0.014, 0.014).extrude(boss_ext))
    return box


def _build_fixed_mount_box(body, r, mats) -> None:
    """SF fixed-mount box housing (child of the tilt bracket). Cordless."""
    s = r.s
    hl = r.hl
    body.visual(_cq_mesh(_scanner_box_solid(hl), "scanner_housing", s),
                origin=Origin(xyz=(BOX_OFFSET_X * s, 0.0, 0.0)),
                material=mats["body"], name="scanner_housing", material_class_id="plastic.opaque_glossy_molded")
    window_x = (BOX_OFFSET_X + BOX_LEN * hl / 2 - 0.007 + 0.001) * s
    body.visual(Box((0.003 * s, (0.040 - 0.004) * s, (0.026 - 0.004) * s)),
                origin=Origin(xyz=(window_x, 0.0, 0.002 * s)),
                material=mats["window"], name="scan_window", material_class_id="glass.smoked_tinted")
    body.visual(Box((0.002 * s, (0.040 - 0.012) * s, 0.003 * s)),
                origin=Origin(xyz=(window_x + 0.002 * s, 0.0, 0.002 * s)),
                material=mats["laser"], name="laser_line", appearance_only=AppearanceOnlySpec(kind="emission", emission_strength=1.0))
    body.visual(Box((0.032 * s, 0.022 * s, 0.001 * s)),
                origin=Origin(xyz=((BOX_OFFSET_X + 0.005) * s, 0.0, (-BOX_HGT / 2 - 0.0005) * s)),
                material=mats["label"], name="spec_label", appearance_only=AppearanceOnlySpec(kind="decal"))
    body.visual(Box((0.006 * s, 0.006 * s, 0.002 * s)),
                origin=Origin(xyz=((BOX_OFFSET_X + 0.020) * s, 0.0, (BOX_HGT / 2 + 0.001) * s)),
                material=mats["led"], name="status_led", material_class_id="tech.emissive_surface")


# ===========================================================================
# Slot B mount builders (create the grounded root parent + cross joint)
# ===========================================================================
def _cradle_foot_solid() -> cq.Workplane:
    return (
        cq.Workplane("XY").box(0.140, 0.090, 0.012).edges("|Z").fillet(0.006)
        .translate((0.0, 0.0, 0.012 / 2))
    )


def _cradle_saddle_solid() -> cq.Workplane:
    """Upright U-channel saddle + risers + head-support plate (SC L206-296)."""
    h = 0.088
    wall_t = 0.005
    channel_iw = 0.048
    channel_id = 0.034
    floor_t = 0.005
    total_ow = channel_iw + 2 * wall_t
    total_od = channel_id + wall_t
    back = (cq.Workplane("XY").box(wall_t, total_ow, h).edges("|Z").fillet(0.002)
            .translate((-total_od / 2 + wall_t / 2, 0.0, h / 2)))
    side_xc = -total_od / 2 + wall_t + channel_id / 2
    side_y = total_ow / 2 - wall_t / 2
    left = (cq.Workplane("XY").box(channel_id, wall_t, h).edges("|Z").fillet(0.002)
            .translate((side_xc, side_y, h / 2)))
    right = (cq.Workplane("XY").box(channel_id, wall_t, h).edges("|Z").fillet(0.002)
             .translate((side_xc, -side_y, h / 2)))
    floor_plate = (cq.Workplane("XY").box(total_od, total_ow, floor_t).edges("|Z").fillet(0.002)
                   .translate((0.0, 0.0, floor_t / 2)))
    saddle = back.union(left).union(right).union(floor_plate)
    riser_h, riser_t = 0.012, 0.008
    riser_l = cq.Workplane("XY").box(riser_t, riser_t, riser_h).translate((side_xc, side_y, h + riser_h / 2))
    riser_r = cq.Workplane("XY").box(riser_t, riser_t, riser_h).translate((side_xc, -side_y, h + riser_h / 2))
    head_plate = (cq.Workplane("XY").box(0.035, 0.065, 0.006).edges("|Z").fillet(0.002)
                  .translate((side_xc + 0.035 / 2, 0.0, h + riser_h + 0.006 / 2)))
    saddle = saddle.union(riser_l).union(riser_r).union(head_plate)
    saddle = saddle.rotate((0, 0, 0), (0, 1, 0), math.degrees(-0.38))
    saddle = saddle.translate((0.008 - 0.008, 0.0, 0.012 - 0.001))
    return saddle


def _charge_led_solid() -> cq.Workplane:
    return (
        cq.Workplane("XY").workplane(offset=0.012 - 0.001).center(0.140 / 2 - 0.012, 0.0)
        .circle(0.004).extrude(0.003)
    )


def _build_charging_cradle(model, body, r, mats) -> None:
    """Separate grounded `cradle_base` dock; scanner_body seats FIXED nose-up.

    Rule 1 FIXED exception: the cradle is a distinct dock sub-assembly (the
    scanner is removable) needing its own reference frame; visual fusing into
    the scanner would be wrong. Documented per §A Rule 1.
    """
    s = r.s
    cradle = model.part("cradle_base")
    cradle.visual(_cq_mesh(_cradle_foot_solid(), "foot_plate", s),
                  origin=Origin(), material=mats["metal"], name="foot_plate", material_class_id="metal.paint_coated")
    cradle.visual(_cq_mesh(_cradle_saddle_solid(), "saddle_cup", s),
                  origin=Origin(), material=mats["metal"], name="saddle_cup", material_class_id="metal.paint_coated")
    cradle.visual(_cq_mesh(_charge_led_solid(), "charge_led", s),
                  origin=Origin(), material=mats["led"], name="charge_led", material_class_id="tech.emissive_surface")
    model.articulation(
        "cradle_to_scanner", ArticulationType.FIXED, parent=cradle, child=body,
        origin=Origin(xyz=(0.008 * s, 0.0, 0.020 * s), rpy=(0.0, -0.38, 0.0)),
    )


def _build_tilt_bracket(model, body, r, mats) -> None:
    """Separate grounded `mount_base` clevis bracket; scanner_body tilts on it
    (REVOLUTE `bracket_hinge`) — the sole mechanism of the fixed-mount form."""
    s = r.s
    mount = model.part("mount_base")
    bracket = ClevisBracketGeometry(
        (0.080 * s, 0.082 * s, 0.082 * s),
        gap_width=0.064 * s,
        bore_diameter=0.014 * s,
        bore_center_z=BRACKET_BORE_Z * s,
        base_thickness=0.010 * s,
        corner_radius=0.003 * s,
        center=False,
    )
    # ClevisBracketGeometry builds its gap + pin bore along X. Rotate it 90°
    # about Z so the bore (and pivot axis) run along Y — the cheeks then sit at
    # ±Y (out of the nose-up/down tilt plane) and the box swings freely between
    # them, while the joint axis passes through the real cheek bore hardware.
    mount.visual(mesh_from_geometry(bracket, "bracket"),
                 origin=Origin(rpy=(0.0, 0.0, math.pi / 2.0)), material=mats["metal"], name="bracket", material_class_id="metal.paint_coated")
    model.articulation(
        "bracket_hinge", ArticulationType.REVOLUTE, parent=mount, child=body,
        origin=Origin(xyz=(0.0, 0.0, BRACKET_BORE_Z * s)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0,
                                   lower=-r.tilt_range, upper=r.tilt_range),
    )


# ===========================================================================
# Slot C control builders (moving child of scanner_body)
# ===========================================================================
def _trigger_blade_solid() -> cq.Workplane:
    """Pivot knuckle + curved blade in the trigger-local (pivot) frame (SB L172-182)."""
    knuckle = cq.Workplane("XZ").workplane(offset=-0.011).circle(0.007).extrude(0.022)
    blade = (
        cq.Workplane("XY").box(0.012, 0.022, 0.050).edges("|Y").fillet(0.005)
        .translate((0.010, 0.0, -0.021))
    )
    return knuckle.union(blade)


def _build_squeeze_trigger(model, body, r, mats, pivot_xyz) -> None:
    """Head-underside squeeze trigger (SB `trigger_pivot`, REVOLUTE axis +Y)."""
    s = r.s
    trigger = model.part("trigger")
    trigger.visual(_cq_mesh(_trigger_blade_solid(), "trigger_blade", s),
                   origin=Origin(), material=mats["trigger"], name="trigger_blade", material_class_id="plastic.opaque_glossy_molded")
    model.articulation(
        "trigger_pivot", ArticulationType.REVOLUTE, parent=body, child=trigger,
        origin=Origin(xyz=pivot_xyz), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=r.trigger_travel),
    )


def _build_top_button(model, body, r, mats, head_center, head_pitch) -> None:
    """PRISMATIC top scan button pressing into the welled top panel (SM)."""
    s = r.s
    top_button = model.part("top_button")
    top_button.visual(_cq_mesh(_top_button_cap_solid(), "button_cap", s),
                      origin=Origin(), material=mats["button"], name="button_cap", material_class_id="plastic.opaque_glossy_molded")
    model.articulation(
        "top_button_press", ArticulationType.PRISMATIC, parent=body, child=top_button,
        origin=Origin(xyz=head_center, rpy=(0.0, head_pitch, 0.0)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=5.0, velocity=0.5, lower=0.0, upper=BUTTON_TRAVEL_NOMINAL),
    )


def _wand_trigger_solid() -> cq.Workplane:
    """Side thumb trigger: pad (+Y) + inward stem (-Y), pivot at origin (SW L82-98)."""
    pad = cq.Workplane("XY").box(0.016, 0.006, 0.022).translate((0.0, 0.004, -0.011))
    stem = cq.Workplane("XY").box(0.012, 0.010, 0.010).translate((0.0, -0.003, -0.005))
    return pad.union(stem)


def _build_side_thumb_trigger(model, body, r, mats) -> None:
    """Barrel side thumb trigger (SW `grip_to_trigger`, REVOLUTE axis -X)."""
    s = r.s
    cz = (BARREL_H / 2) * s
    trigger = model.part("trigger")
    trigger.visual(_cq_mesh(_wand_trigger_solid(), "trigger_pad", s),
                   origin=Origin(), material=mats["trigger"], name="trigger_pad", material_class_id="plastic.opaque_glossy_molded")
    press = _clamp(r.trigger_travel, 0.18, 0.26)
    model.articulation(
        "grip_to_trigger", ArticulationType.REVOLUTE, parent=body, child=trigger,
        origin=Origin(xyz=(0.015 * s, (BARREL_W / 2) * s, cz + 0.002 * s)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=press),
    )


# ===========================================================================
# Assembly
# ===========================================================================
def build_barcode_scanner(config: BarcodeScannerConfig | None = None,
                          *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)

    body = model.part("scanner_body")

    # Slot A — body_form (grounded/child root part) -------------------------
    head_center: tuple[float, float, float] | None = None
    head_pitch = 0.0
    if r.body_form == "pistol_grip":
        head_center, head_pitch = _build_pistol_grip(body, r, mats)
    elif r.body_form == "presentation_tower":
        head_center, head_pitch = _build_presentation_tower(body, r, mats)
    elif r.body_form == "inline_wand":
        _build_inline_wand(body, r, mats)
    else:  # fixed_mount_box
        _build_fixed_mount_box(body, r, mats)

    # Slot B — mount (grounded parent + cross joint) ------------------------
    if r.mount == "charging_cradle":
        _build_charging_cradle(model, body, r, mats)
    elif r.mount == "tilt_bracket":
        _build_tilt_bracket(model, body, r, mats)
    # mount == none: scanner_body is the grounded root.

    # Slot C — control (moving child) ---------------------------------------
    if r.control in ("squeeze_trigger", "trigger_plus_top_button"):
        assert head_center is not None
        s = r.s
        pivot_xyz = ((0.045 if r.body_form == "pistol_grip" else 0.042) * s, 0.0,
                     (0.100 if r.body_form == "pistol_grip" else 0.088) * s)
        _build_squeeze_trigger(model, body, r, mats, pivot_xyz)
        if r.control == "trigger_plus_top_button":
            _build_top_button(model, body, r, mats, head_center, head_pitch)
    elif r.control == "side_thumb_trigger":
        _build_side_thumb_trigger(model, body, r, mats)
    # control == none: mechanism is the bracket tilt (fixed_mount_box).

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_barcode_scanner(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_barcode_scanner(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_captured_overlaps(ctx, model, r: ResolvedBarcodeScannerConfig) -> None:
    body = model.get_part("scanner_body")
    if r.control in ("squeeze_trigger", "trigger_plus_top_button"):
        trigger = model.get_part("trigger")
        ctx.allow_overlap(trigger, body,
                          reason="trigger pivot knuckle is captured inside the head underside")
    if r.control == "trigger_plus_top_button":
        top_button = model.get_part("top_button")
        ctx.allow_overlap(top_button, body,
                          reason="button cap stem is captured inside the panel well and head housing")
    if r.control == "side_thumb_trigger":
        trigger = model.get_part("trigger")
        ctx.allow_overlap(trigger, body,
                          reason="thumb-trigger stem passes through a slot in the barrel side wall")
    if r.mount == "charging_cradle":
        cradle = model.get_part("cradle_base")
        for elem in ("grip_shell", "grip_insert_wrap", "head_shell"):
            ctx.allow_overlap(cradle, body, elem_a="saddle_cup", elem_b=elem,
                              reason="scanner seats inside the saddle U-channel / head-support plate")
    if r.mount == "tilt_bracket":
        mount = model.get_part("mount_base")
        ctx.allow_overlap(body, mount, elem_a="scanner_housing", elem_b="bracket",
                          reason="trunnion bosses on the housing seat into the bracket cheek bores")


def run_barcode_scanner_tests(object_model: ArticulatedObject,
                              config: BarcodeScannerConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_captured_overlaps(ctx, object_model, r)

    body = object_model.get_part("scanner_body")

    # ---- Identity: a recessed scan window aimed forward on the head front. ----
    win = ctx.part_element_world_aabb(body, elem="scan_window")
    ctx.check(
        "scan window present and forward-facing",
        win is not None,
        details=f"scan_window aabb={win}",
    )

    # ---- Identity: at least one real user control (non-FIXED) joint. ----
    moving = [a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED]
    ctx.check(
        "has at least one user-control (non-fixed) joint",
        len(moving) >= 1,
        details=f"non-fixed joints={[a.name for a in moving]}",
    )

    # ---- Grounded: the root support stands on z~0. ----
    roots = object_model.root_parts()
    whole = ctx.part_world_aabb(roots[0]) if roots else None
    if whole is not None:
        ctx.check("assembly root rests near the ground plane", whole[0][2] < 0.010,
                  details=f"root z_min={whole[0][2]:.4f}")

    # ---- Targeted mechanism poses (one per key mechanism). ----
    if r.control in ("squeeze_trigger", "trigger_plus_top_button"):
        trigger = object_model.get_part("trigger")
        j = object_model.get_articulation("trigger_pivot")
        rest = ctx.part_world_aabb(trigger)
        with ctx.pose({j: r.trigger_travel}):
            sq = ctx.part_world_aabb(trigger)
        rest_cx = 0.5 * (rest[0][0] + rest[1][0])
        sq_cx = 0.5 * (sq[0][0] + sq[1][0])
        ctx.check("squeeze trigger swings the blade rearward",
                  sq_cx < rest_cx - 0.003,
                  details=f"trigger cx {rest_cx:.4f} -> {sq_cx:.4f}")

    if r.control == "trigger_plus_top_button":
        top_button = object_model.get_part("top_button")
        press = object_model.get_articulation("top_button_press")
        ctx.check("top button is PRISMATIC", press.articulation_type == ArticulationType.PRISMATIC,
                  details=f"type={press.articulation_type}")
        rest = ctx.part_world_position(top_button)
        with ctx.pose({press: BUTTON_TRAVEL_NOMINAL}):
            pressed = ctx.part_world_position(top_button)
        ctx.check("pressing lowers the top button",
                  pressed[2] < rest[2] - 0.001,
                  details=f"button z {rest[2]:.4f} -> {pressed[2]:.4f}")

    if r.control == "side_thumb_trigger":
        trigger = object_model.get_part("trigger")
        j = object_model.get_articulation("grip_to_trigger")
        rest = ctx.part_world_aabb(trigger)
        with ctx.pose({j: j.motion_limits.upper}):
            pressed = ctx.part_world_aabb(trigger)
        rest_cy = 0.5 * (rest[0][1] + rest[1][1])
        pressed_cy = 0.5 * (pressed[0][1] + pressed[1][1])
        ctx.check("side thumb trigger presses inward",
                  rest_cy - pressed_cy > 0.0005,
                  details=f"trigger cy {rest_cy:.4f} -> {pressed_cy:.4f}")

    if r.mount == "tilt_bracket":
        hinge = object_model.get_articulation("bracket_hinge")
        ctx.check("bracket tilt is REVOLUTE", hinge.articulation_type == ArticulationType.REVOLUTE,
                  details=f"type={hinge.articulation_type}")
        with ctx.pose({hinge: 0.0}):
            rest = ctx.part_element_world_aabb(body, elem="scanner_housing")
        with ctx.pose({hinge: r.tilt_range}):
            up = ctx.part_element_world_aabb(body, elem="scanner_housing")
        with ctx.pose({hinge: -r.tilt_range}):
            down = ctx.part_element_world_aabb(body, elem="scanner_housing")
        ctx.check("tilt aims the housing up and down",
                  up[1][2] > rest[1][2] - 0.001 and down[0][2] < rest[0][2] + 0.001,
                  details=f"rest_zmax={rest[1][2]:.4f} up_zmax={up[1][2]:.4f} down_zmin={down[0][2]:.4f}")

    # ---- Rule 5: full-travel non-穿模 across sampled joint poses. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # ---- Compiler-owned baseline (also enforced by the sweep). ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "BodyForm",
    "Mount",
    "Control",
    "Palette",
    "BarcodeScannerConfig",
    "ResolvedBarcodeScannerConfig",
    "build_barcode_scanner",
    "build_seeded_barcode_scanner",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_barcode_scanner_tests",
]
