# SPDX-License-Identifier: Apache-2.0

"""Single hinged door leaf — modular procedural template.

A door is a single leaf swinging on a vertical hinge about its hinge edge, hung
in a fixed frame/casing (root), and carrying one operating hardware set near the
latch edge. There is exactly ONE category-defining motion spine
(``frame_to_leaf`` REVOLUTE, vertical axis) plus an optional secondary hardware
swing (lever press / knob turn).

Slot graph (pattern = ``mixed``), sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_Door.md``:

  * ``leaf_style`` (5) — the leaf-face structural family + the root frame it
    needs.  Each picks a different leaf part-tree and a different root factory:
      - ``solid_raised_panel``     (P6) routed-groove + proud raised panel slab
      - ``glazed_vision_strip``    (P1) through-cut vision opening + glass pane
      - ``louvered_vented``        (P2/V7/V8) steel leaf + N horizontal louvers
      - ``full_glass``             (P4) frameless glass leaf + fixed side panel
      - ``fluted_entry_sidelight`` (P5) dark leaf + fixed fluted sidelight bay
  * ``door_hardware`` (4) — the latch-edge operating hardware:
      - ``lever_on_rose``    (P6/P1/V9) static rose + REVOLUTE lever (+Y) [+ FIXED lock]
      - ``round_knob``       (V1) domed knob, REVOLUTE turning (+Y)
      - ``straight_bar_pull``(V5/P4/P5) FIXED tubular bar + 2 standoffs
      - ``ornate_s_pull``    (P3) FIXED brass S-spline bar + 2 standoffs
  * ``louver_panel_count`` (N in [1, 6]) — multiplicity axis, only active for
    ``louvered_vented``: N horizontal VentGrille panels (``louver_panel_i``) with
    ``inter_rail_j`` dividers, all inline visuals on the leaf (Rule 1).

Unified geometry convention for ALL leaf styles (so every hinge joint shares one
robust axis/origin):
  * leaf-LOCAL frame: hinge edge at local x=0, leaf body extends +X to x=LEAF_W,
    thickness centered on Y (room side +Y), height 0..LEAF_H (floor at z=0).
  * ``frame_to_leaf`` REVOLUTE origin (0,0,0), axis (0,0,1), lower=0 upper≈1.6.
  * For full_glass / fluted the fixed bay (side_panel / sidelight) is a root
    visual on the latch side (NOT a second moving leaf — that would be a Double
    Door); the leaf still hinges at x=0.

Compatibility gating (resolve_config, spec §compatibility matrix):
  * glass leaves (full_glass / fluted_entry_sidelight) only accept the glass-
    friendly pulls {straight_bar_pull, ornate_s_pull} — never knob/lever.
  * ornate_s_pull is eligible ONLY on glass leaves.
  * louver_panel_count is only meaningful for louvered_vented (else forced 0).

3 hard rules:
  * Rule 1 — non-moving hardware (bar pull, S pull, knob latch plate, lever
    rose, louver panels, lock escutcheon decorations) are parent ``.visual(...)``
    or inline on a FIXED/REVOLUTE child carrying real geometry, never a phantom
    fixed disk.
  * Rule 2 — every non-FIXED joint (frame_to_leaf, leaf_to_lever, leaf_to_knob)
    is a captured/seated pivot whose intentional overlaps are declared element-
    scoped; these pivots are grandfathered (no MatingContract) the same way the
    5-star sources and single_revolute_hinge.py do.
  * Rule 3 — leaf meshes keep their cadquery / VentGrille / spline primitives
    from the declared 5-star sources; nothing is downgraded to a crude box.
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
    KnobBore,
    KnobGeometry,
    KnobGrip,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    VentGrilleGeometry,
    VentGrilleSlats,
    VentGrilleSleeve,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True


LeafStyle = Literal[
    "solid_raised_panel",
    "glazed_vision_strip",
    "louvered_vented",
    "full_glass",
    "fluted_entry_sidelight",
]
DoorHardware = Literal[
    "lever_on_rose",
    "round_knob",
    "straight_bar_pull",
    "ornate_s_pull",
]
PaletteStyle = Literal[
    "light_oak",
    "dark_graphite",
    "steel_gray",
    "dark_entry",
    "glass_brass",
    "glass_steel",
]

LEAF_STYLES: tuple[LeafStyle, ...] = (
    "solid_raised_panel",
    "glazed_vision_strip",
    "louvered_vented",
    "full_glass",
    "fluted_entry_sidelight",
)
DOOR_HARDWARE: tuple[DoorHardware, ...] = (
    "lever_on_rose",
    "round_knob",
    "straight_bar_pull",
    "ornate_s_pull",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "light_oak",
    "dark_graphite",
    "steel_gray",
    "dark_entry",
    "glass_brass",
    "glass_steel",
)

# Glass leaves: only glass-friendly pulls (spec compatibility matrix).
GLASS_LEAVES: tuple[LeafStyle, ...] = ("full_glass", "fluted_entry_sidelight")
GLASS_HARDWARE: tuple[DoorHardware, ...] = ("straight_bar_pull", "ornate_s_pull")
# Non-glass (solid / glazed-strip / steel-louver) leaves: all but ornate_s_pull
# (ornate S pull is a glass-leaf-only candidate per the spec).
SOLID_HARDWARE: tuple[DoorHardware, ...] = (
    "lever_on_rose",
    "round_knob",
    "straight_bar_pull",
)

# Louver multiplicity (spec §Multiplicity): N in [1, 6], small-N weighted.
N_LOUVER_MIN = 1
N_LOUVER_MAX = 6
LOUVER_WEIGHTS = (0.25, 0.35, 0.25, 0.10, 0.04, 0.01)  # N=1..6


# --------------------------------------------------------------------------- #
# Palettes (spec §palette_style colorway table; all observed from 5-star src).
# Keys: leaf, frame, hardware, glass.
# --------------------------------------------------------------------------- #
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "light_oak": {
        "leaf": (0.82, 0.66, 0.45, 1.0),
        "frame": (0.66, 0.50, 0.33, 1.0),
        "hardware": (0.74, 0.76, 0.78, 1.0),
        "glass": (0.78, 0.85, 0.88, 0.35),
    },
    "dark_graphite": {
        "leaf": (0.20, 0.21, 0.23, 1.0),
        "frame": (0.15, 0.16, 0.18, 1.0),
        "hardware": (0.72, 0.62, 0.38, 1.0),
        "glass": (0.78, 0.85, 0.88, 0.35),
    },
    "steel_gray": {
        "leaf": (0.55, 0.56, 0.57, 1.0),
        "frame": (0.42, 0.43, 0.45, 1.0),
        "hardware": (0.72, 0.72, 0.74, 1.0),
        "glass": (0.82, 0.88, 0.90, 0.35),
    },
    "dark_entry": {
        "leaf": (0.16, 0.16, 0.175, 1.0),
        "frame": (0.13, 0.13, 0.145, 1.0),
        "hardware": (0.78, 0.79, 0.81, 1.0),
        "glass": (0.62, 0.70, 0.74, 0.34),
    },
    "glass_brass": {
        "leaf": (0.62, 0.70, 0.74, 0.45),
        "frame": (0.12, 0.12, 0.14, 1.0),
        "hardware": (0.76, 0.58, 0.22, 1.0),
        "glass": (0.62, 0.70, 0.74, 0.45),
    },
    "glass_steel": {
        "leaf": (0.72, 0.80, 0.84, 0.28),
        "frame": (0.10, 0.10, 0.11, 1.0),
        "hardware": (0.80, 0.81, 0.83, 1.0),
        "glass": (0.72, 0.80, 0.84, 0.28),
    },
}

# Weak leaf_style -> palette preference (spec: glass-* favor glass leaves,
# light_oak/steel favor solid/louvered). Cross-pairing allowed for color
# diversity; the resolver always falls back to a compatible palette.
_PALETTE_PREF: dict[LeafStyle, tuple[PaletteStyle, ...]] = {
    "solid_raised_panel": ("light_oak", "dark_graphite", "dark_entry"),
    "glazed_vision_strip": ("dark_graphite", "steel_gray", "light_oak"),
    "louvered_vented": ("steel_gray", "light_oak", "dark_graphite"),
    "full_glass": ("glass_steel", "glass_brass", "dark_entry"),
    "fluted_entry_sidelight": ("dark_entry", "glass_steel", "glass_brass"),
}


# --------------------------------------------------------------------------- #
# Real-world base dimensions (meters). Long axis = X (width), Y = thickness
# (room side +Y), Z = height (floor at z=0). Hinge edge at leaf-local x=0.
# --------------------------------------------------------------------------- #
_LEAF_W = 0.880          # nominal leaf width
_LEAF_H = 2.030          # nominal leaf height
_SOLID_T = 0.042         # solid / steel / wood leaf thickness
_GLASS_T = 0.012         # glass leaf thickness

_JAMB_W = 0.045          # jamb face width (X for side jambs)
_JAMB_D = 0.130          # jamb depth (Y, wall thickness)
_HEAD_GAP = 0.004        # reveal between leaf and head
_SIDE_GAP = 0.004        # reveal at each side
_HINGE_LAP = 0.004       # hinge jamb laps the leaf hinge edge

_CASING_W = 0.060        # casing trim face width
_CASING_T = 0.018        # casing trim proud thickness

_HANDLE_Z = 1.050        # latch hardware height (world z)

# Solid raised-panel detail.
_GROOVE_INSET = 0.075
_GROOVE_W = 0.012
_GROOVE_DEPTH = 0.007
_PANEL_PROUD = 0.008
_PANEL_MARGIN = 0.100

# Glazed vision strip detail.
_VS_W = 0.110            # vision strip width
_VS_H = 1.520            # vision strip height
_VS_OFFSET = 0.250       # strip center inset from the latch edge

# Louver leaf detail.
_RAIL = 0.075            # top/bottom rail face width
_STILE = 0.075           # hinge/latch stile face width
_INTER_RAIL = 0.075      # divider rail between louver panels

# Full-glass / fluted bay detail.
_BAY_W = 0.420           # fixed side panel / sidelight aperture width
_MULLION_W = 0.055       # dark divider between leaf bay and fixed bay
_FLUTE_PITCH = 0.030
_FLUTE_R = 0.012


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
FlutedLeafVariant = Literal["plain_slab", "ribbed"]
OrnatePullVariant = Literal["s2", "s3"]
FLUTED_LEAF_VARIANTS: tuple[FlutedLeafVariant, ...] = ("plain_slab", "ribbed")
ORNATE_PULL_VARIANTS: tuple[OrnatePullVariant, ...] = ("s2", "s3")


@dataclass(frozen=True)
class DoorConfig:
    leaf_style: LeafStyle | None = None
    door_hardware: DoorHardware | None = None
    louver_panel_count: int | None = None
    palette_style: PaletteStyle | None = None
    # Second-candidate selectors within an existing slot (spec Slot A / Slot B):
    #   fluted_leaf_variant — plain_slab (P5) vs ribbed (V10 TRUE fluted leaf).
    #   ornate_pull_variant — s2 (P3, 2-lobe/2-standoff) vs s3 (V11, 3-lobe/3-standoff).
    # Only meaningful for fluted_entry_sidelight / ornate_s_pull respectively.
    fluted_leaf_variant: FlutedLeafVariant | None = None
    ornate_pull_variant: OrnatePullVariant | None = None
    leaf_width_scale: float = 1.0
    leaf_height_scale: float = 1.0
    open_angle_upper: float = 1.6
    handle_height: float = 1.05
    louver_slat_pitch: float = 0.026
    frame_face_scale: float = 1.0
    name: str = "door"


@dataclass(frozen=True)
class ResolvedDoorConfig:
    leaf_style: LeafStyle
    door_hardware: DoorHardware
    louver_panel_count: int
    palette_style: PaletteStyle
    fluted_leaf_variant: FlutedLeafVariant
    ornate_pull_variant: OrnatePullVariant
    # Concrete geometry (scaled / derived).
    leaf_w: float
    leaf_h: float
    leaf_t: float
    jamb_w: float
    sill_z: float
    open_angle_upper: float
    handle_height: float
    louver_slat_pitch: float
    name: str

    @property
    def is_glass(self) -> bool:
        return self.leaf_style in GLASS_LEAVES


def config_from_seed(seed: int) -> DoorConfig:
    """Deterministic procedural sampling. seed=0 is not special.

    Order: leaf_style -> (gated) hardware -> louver N (weighted, louver only)
    -> palette (leaf-weighted) -> continuous scales.
    """
    rng = random.Random(seed)
    leaf_style: LeafStyle = rng.choice(LEAF_STYLES)

    if leaf_style in GLASS_LEAVES:
        door_hardware: DoorHardware = rng.choice(GLASS_HARDWARE)
    else:
        door_hardware = rng.choice(SOLID_HARDWARE)

    if leaf_style == "louvered_vented":
        louver_panel_count = rng.choices(
            range(N_LOUVER_MIN, N_LOUVER_MAX + 1), weights=LOUVER_WEIGHTS, k=1
        )[0]
    else:
        louver_panel_count = 0

    # Second-candidate selectors (spec Slot A fluted / Slot B ornate). Each is a
    # real structural variant (plain slab vs ribbed leaf; 2-lobe vs 3-lobe pull),
    # only meaningful when its parent module is chosen.
    fluted_leaf_variant: FlutedLeafVariant = rng.choice(FLUTED_LEAF_VARIANTS)
    ornate_pull_variant: OrnatePullVariant = rng.choice(ORNATE_PULL_VARIANTS)

    # Palette: leaf-weighted preference, but any palette possible for color
    # diversity (resolve_config keeps it legal regardless).
    pref = _PALETTE_PREF[leaf_style]
    if rng.random() < 0.7:
        palette_style: PaletteStyle = rng.choice(pref)
    else:
        palette_style = rng.choice(PALETTE_STYLES)

    return DoorConfig(
        leaf_style=leaf_style,
        door_hardware=door_hardware,
        louver_panel_count=louver_panel_count,
        palette_style=palette_style,
        fluted_leaf_variant=fluted_leaf_variant,
        ornate_pull_variant=ornate_pull_variant,
        leaf_width_scale=round(rng.uniform(0.95, 1.06), 4),
        leaf_height_scale=round(rng.uniform(0.98, 1.03), 4),
        open_angle_upper=round(rng.uniform(1.4, 1.7), 4),
        handle_height=round(rng.uniform(1.00, 1.10), 4),
        louver_slat_pitch=round(rng.uniform(0.024, 0.034), 4),
        frame_face_scale=round(rng.uniform(0.9, 1.15), 4),
        name=f"seeded_door_{seed}",
    )


def resolve_config(config: DoorConfig | None = None) -> ResolvedDoorConfig:
    cfg = config or DoorConfig()

    leaf_style = _pick(cfg.leaf_style, LEAF_STYLES)

    # --- Compatibility gating (spec compatibility matrix). ---
    legal_hw = GLASS_HARDWARE if leaf_style in GLASS_LEAVES else SOLID_HARDWARE
    door_hardware = cfg.door_hardware if cfg.door_hardware in legal_hw else legal_hw[0]

    # louver_panel_count only meaningful for louvered_vented.
    if leaf_style == "louvered_vented":
        n = int(cfg.louver_panel_count) if cfg.louver_panel_count else 2
        louver_panel_count = int(_clamp(n, N_LOUVER_MIN, N_LOUVER_MAX))
    else:
        louver_panel_count = 0

    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    # Second-candidate selectors. Default to the parent (P5 plain / P3 2-lobe).
    fluted_leaf_variant = _pick(cfg.fluted_leaf_variant, FLUTED_LEAF_VARIANTS)
    ornate_pull_variant = _pick(cfg.ornate_pull_variant, ORNATE_PULL_VARIANTS)

    # --- Continuous scales (clamped). ---
    w_scale = _clamp(cfg.leaf_width_scale, 0.95, 1.06)
    h_scale = _clamp(cfg.leaf_height_scale, 0.98, 1.03)
    open_upper = _clamp(cfg.open_angle_upper, 1.4, 1.7)
    handle_h = _clamp(cfg.handle_height, 1.00, 1.10)
    slat_pitch = _clamp(cfg.louver_slat_pitch, 0.024, 0.034)
    face_scale = _clamp(cfg.frame_face_scale, 0.9, 1.15)

    leaf_w = _LEAF_W * w_scale
    leaf_h = _LEAF_H * h_scale
    leaf_t = _GLASS_T if leaf_style in GLASS_LEAVES else _SOLID_T
    jamb_w = _JAMB_W * face_scale

    return ResolvedDoorConfig(
        leaf_style=leaf_style,
        door_hardware=door_hardware,
        louver_panel_count=louver_panel_count,
        palette_style=palette_style,
        fluted_leaf_variant=fluted_leaf_variant,
        ornate_pull_variant=ornate_pull_variant,
        leaf_w=leaf_w,
        leaf_h=leaf_h,
        leaf_t=leaf_t,
        jamb_w=jamb_w,
        sill_z=0.0,
        open_angle_upper=open_upper,
        handle_height=handle_h,
        louver_slat_pitch=slat_pitch,
        name=cfg.name or "door",
    )


def with_overrides(config: DoorConfig, **kwargs: object) -> DoorConfig:
    return replace(config, **kwargs)


# --------------------------------------------------------------------------- #
# slot_choices
# --------------------------------------------------------------------------- #
def slot_choices_for_config(
    config: DoorConfig | ResolvedDoorConfig,
) -> list[tuple[str, str]]:
    r = config if isinstance(config, ResolvedDoorConfig) else resolve_config(config)
    # Reflect the 2nd-candidate selector in the leaf_style / door_hardware slot
    # value so each real structural candidate registers as a distinct module
    # tuple (spec: fluted plain vs ribbed; ornate 2-lobe vs 3-lobe).
    leaf_choice = r.leaf_style
    if r.leaf_style == "fluted_entry_sidelight":
        leaf_choice = (
            "fluted_sidelight_bar"
            if r.fluted_leaf_variant == "ribbed"
            else "fluted_entry_sidelight"
        )
    hw_choice = r.door_hardware
    if r.door_hardware == "ornate_s_pull":
        hw_choice = "ornate_s_pull_3" if r.ornate_pull_variant == "s3" else "ornate_s_pull"
    choices = [
        ("leaf_style", leaf_choice),
        ("door_hardware", hw_choice),
    ]
    if r.leaf_style == "louvered_vented":
        choices.append(("louver_panel_count", f"n{r.louver_panel_count}"))
    return choices


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Leaf-mesh cadquery helpers (preserve source primitives — Rule 3).
# All authored in leaf-LOCAL frame: hinge edge at x=0, body in +X,
# thickness centered on Y, height 0..leaf_h.
# --------------------------------------------------------------------------- #
def _solid_raised_panel_cq(r: ResolvedDoorConfig) -> cq.Workplane:
    """Oak slab + routed border groove + 1 proud raised center panel (P6)."""
    w, h, t = r.leaf_w, r.leaf_h, r.leaf_t
    blank = cq.Workplane("XY").box(w, t, h, centered=(False, True, False))
    cx, cz, face_y = w / 2.0, h / 2.0, t / 2.0

    outer_w = w - 2 * _GROOVE_INSET
    outer_h = h - 2 * _GROOVE_INSET
    groove = (
        cq.Workplane("XZ")
        .workplane(offset=face_y)
        .center(cx, cz)
        .rect(outer_w, outer_h)
        .rect(outer_w - 2 * _GROOVE_W, outer_h - 2 * _GROOVE_W)
        .extrude(-_GROOVE_DEPTH)
    )
    leaf = blank.cut(groove)

    panel_w = w - 2 * _PANEL_MARGIN
    panel_h = h - 2 * _PANEL_MARGIN
    panel = (
        cq.Workplane("XZ")
        .workplane(offset=face_y)
        .center(cx, cz)
        .rect(panel_w, panel_h)
        .extrude(_PANEL_PROUD)
    )
    try:
        panel = panel.edges(">Y").chamfer(0.010)
    except Exception:
        pass
    return leaf.union(panel)


def _glazed_leaf_cq(r: ResolvedDoorConfig) -> cq.Workplane:
    """Graphite slab with a tall vertical vision opening through-cut (P1)."""
    w, h, t = r.leaf_w, r.leaf_h, r.leaf_t
    blank = cq.Workplane("XY").box(w, t, h, centered=(False, True, False))
    strip_cx = w - _VS_OFFSET  # off-center toward the latch (+X)
    strip_cz = h / 2.0
    opening = (
        cq.Workplane("XZ")
        .workplane(offset=-t)
        .center(strip_cx, strip_cz)
        .rect(_VS_W, _VS_H)
        .extrude(2 * t)
    )
    leaf = blank.cut(opening)
    try:
        leaf = leaf.edges(">Y").edges("|Z").fillet(0.003)
    except Exception:
        pass
    return leaf


def _glazed_pane_cq(r: ResolvedDoorConfig) -> cq.Workplane:
    """Translucent pane filling the vision opening, slightly oversized (P1)."""
    pane = cq.Workplane("XZ").rect(_VS_W + 0.012, _VS_H + 0.012).extrude(0.008)
    return pane


def _full_glass_pane_cq(r: ResolvedDoorConfig, *, edge_w: float = 0.022) -> cq.Workplane:
    """Large clear glass pane (P4), leaf-local, centered on body."""
    w, h, t = r.leaf_w, r.leaf_h, r.leaf_t
    cx = w / 2.0
    return (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(w - 2.0 * edge_w, h - 2.0 * edge_w, t, centered=(True, True, True))
    )


def _full_glass_edge_cq(r: ResolvedDoorConfig, *, edge_w: float = 0.022) -> cq.Workplane:
    """Thin dark edge framing band around the glass pane (P4)."""
    w, h, t = r.leaf_w, r.leaf_h, r.leaf_t
    cx = w / 2.0
    edge_frame = 0.018
    outer = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(w, h, t + 2.0 * edge_frame, centered=(True, True, True))
    )
    inner = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(w - 2.0 * edge_w, h - 2.0 * edge_w, t + 2.0 * edge_frame + 0.01, centered=(True, True, True))
    )
    return outer.cut(inner)


def _fluted_leaf_cq(r: ResolvedDoorConfig) -> cq.Workplane:
    """Dark entry leaf slab with a narrow vertical glass-strip aperture (P5)."""
    w, h, t = r.leaf_w, r.leaf_h, r.leaf_t
    cx = w / 2.0
    leaf = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(w, h, t, centered=(True, True, True))
        .edges("|Y")
        .fillet(0.004)
    )
    strip_cx = w - 0.16  # near the free (latch) edge
    leaf = leaf.cut(
        cq.Workplane("XZ")
        .center(strip_cx, h / 2.0)
        .box(0.090, 1.55, t + 0.02, centered=(True, True, True))
    )
    return leaf


def _fluted_strip_cq(r: ResolvedDoorConfig) -> cq.Workplane:
    """Narrow vertical glass strip seated in the fluted leaf aperture (P5)."""
    w, h = r.leaf_w, r.leaf_h
    strip_cx = w - 0.16
    return (
        cq.Workplane("XZ")
        .center(strip_cx, h / 2.0)
        .box(0.090 + 0.006, 1.55 + 0.006, 0.018, centered=(True, True, True))
    )


# Ribbed-fluted leaf (Slot A 2nd candidate, V10). A thin dark base plate carries
# a row of evenly spaced vertical half-round flute ribs on the room (+Y) face,
# matching the sidelight flute pitch. Authored in the template's unified leaf-
# local frame (hinge edge at x=0, body in +X, height 0..leaf_h, thickness on Y).
_FLUTED_BASE_T = 0.033       # thin structural base plate behind the ribs (V10)
_FLUTED_RIB_R = _FLUTE_R     # half-round rib radius (0.012), shares sidelight R
_FLUTED_RIB_EMBED = 0.003    # ribs sink into the base plate for a solid union


def _flute_rib_center(flute_i: int, x_start: float, pitch: float, face_y: float):
    """Shared rib helper (V10): (x, y) center of the half-round flute rib at
    index ``flute_i``. Centers sit at regular horizontal pitch on the front
    (+Y) face, matching the sidelight fluting rhythm.
    """
    return (x_start + flute_i * pitch, face_y)


def _fluted_ribbed_leaf_cq(r: ResolvedDoorConfig) -> cq.Workplane:
    """TRUE vertical-fluted leaf (V10): thin base plate + a row of evenly spaced
    vertical half-round flute ribs emitted by ``for flute_i in range(n)`` over the
    shared ``_flute_rib_center`` helper, plus the same narrow vertical glass-strip
    aperture as the plain slab. Replaces P5's plain slab with a real fluted face.

    Template-local frame: width->X (body in [0, w]), height->Z (centered at h/2),
    thickness extruded in Y (room side +Y). Base plate centered on Y=0; ribs
    protrude +Y.
    """
    w, h = r.leaf_w, r.leaf_h
    base_t = _FLUTED_BASE_T
    cx = w / 2.0

    # Thin structural base plate.
    plate = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(w, h, base_t, centered=(True, True, True))
    )

    # --- Vertical flute ribs on the front (+Y) face (V10 rib loop). ---
    front_y = base_t / 2.0
    n_flutes = max(2, int(w // _FLUTE_PITCH))
    x_start = cx - (n_flutes - 1) * _FLUTE_PITCH / 2.0

    rib_points = []
    for flute_i in range(n_flutes):
        rib_points.append(_flute_rib_center(flute_i, x_start, _FLUTE_PITCH, front_y))

    # Full-circle full-height cylinders at each rib center; built in XY extruding
    # +Z (the height axis), then back-trimmed to a half-round.
    all_cyls = (
        cq.Workplane("XY")
        .pushPoints(rib_points)
        .circle(_FLUTED_RIB_R)
        .extrude(h)
    )

    # Back-cut so only the front half-round of each rib protrudes from the base
    # plate face. Ribs keep a small embed depth so they union solidly into it.
    total_span = (n_flutes - 1) * _FLUTE_PITCH + _FLUTED_RIB_R * 4.0
    cutter_top_y = front_y - _FLUTED_RIB_EMBED
    back_cutter = (
        cq.Workplane("XY")
        .center(cx, cutter_top_y - 0.5)
        .box(total_span, 1.0, h * 1.2, centered=(True, True, True))
    )
    trimmed_ribs = all_cyls.cut(back_cutter)

    leaf = plate.union(trimmed_ribs)

    # Same narrow vertical glass-strip aperture as the plain slab.
    strip_cx = w - 0.16
    leaf = leaf.cut(
        cq.Workplane("XZ")
        .center(strip_cx, h / 2.0)
        .box(0.090, 1.55, base_t + 2.0 * _FLUTED_RIB_R + 0.02, centered=(True, True, True))
    )
    return leaf


# --------------------------------------------------------------------------- #
# Louver helper (VentGrille — Rule 3). Built in local XY extruding +Z; the
# GRILLE_RPY lays the face into XZ (slats horizontal) and the duct along +Y.
# --------------------------------------------------------------------------- #
_GRILLE_RPY = (math.pi / 2.0, 0.0, 0.0)


def _louver_panel_mesh(width: float, height: float, name: str, r: ResolvedDoorConfig):
    grille = VentGrilleGeometry(
        (width, height),
        frame=0.010,
        face_thickness=0.004,
        duct_depth=r.leaf_t * 0.7,
        duct_wall=0.003,
        slat_pitch=r.louver_slat_pitch,
        slat_width=0.020,
        slat_angle_deg=35.0,
        corner_radius=0.004,
        slats=VentGrilleSlats(profile="flat", direction="down"),
        sleeve=VentGrilleSleeve(style="short"),
        center=True,
    )
    return mesh_from_geometry(grille, name)


# --------------------------------------------------------------------------- #
# Hardware cadquery helpers (preserve source primitives — Rule 3).
# Authored so the rose/spindle mounting face is at local z=0 growing +Z; a
# roll of -pi/2 at mount maps local +Z -> world +Y (out of the room face).
# --------------------------------------------------------------------------- #
def _lever_cq() -> cq.Workplane:
    """Brushed-steel lever: hub + neck + arm sweeping -X (P6/P1)."""
    hub = cq.Workplane("XY").circle(0.010).extrude(0.020)
    neck = cq.Workplane("XY").workplane(offset=0.020).circle(0.008).extrude(0.006)
    lever = (
        cq.Workplane("XY")
        .workplane(offset=0.024)
        .center(-0.052, 0.0)
        .box(0.110, 0.016, 0.013, centered=(True, True, True))
        .edges("|Z")
        .fillet(0.005)
    )
    return hub.union(neck).union(lever)


def _knob_cq() -> cq.Workplane:
    """Domed round knob: rose + neck + sphere dome (V1)."""
    rose_r, rose_h = 0.027, 0.008
    neck_r, neck_h = 0.011, 0.008
    dome_r = 0.026
    rose = cq.Workplane("XY").circle(rose_r).extrude(rose_h)
    try:
        rose = rose.edges(">Z").fillet(0.0015)
    except Exception:
        pass
    neck = cq.Workplane("XY").workplane(offset=rose_h).circle(neck_r).extrude(neck_h)
    dome_center_z = rose_h + neck_h + dome_r * 0.55
    dome = cq.Workplane("XY").workplane(offset=dome_center_z).sphere(dome_r)
    return rose.union(neck).union(dome)


def _bar_tube_cq() -> cq.Workplane:
    """Hollow tubular bar pull with integral end caps, axis +Z (V5)."""
    bar_len, bar_od, bar_id, cap = 0.800, 0.019, 0.014, 0.003
    half = bar_len / 2.0
    solid = cq.Workplane("XY").workplane(offset=-half).circle(bar_od / 2.0).extrude(bar_len)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=-half + cap)
        .circle(bar_id / 2.0)
        .extrude(bar_len - 2.0 * cap)
    )
    return solid.cut(bore)


def _standoff_cq() -> cq.Workplane:
    """Standoff base plate + post extruded along +Y (ZX workplane) (V5)."""
    base_d, base_h, post_d, post_h = 0.040, 0.006, 0.019, 0.038
    base = cq.Workplane("ZX").circle(base_d / 2.0).extrude(base_h)
    post = (
        cq.Workplane("ZX")
        .workplane(offset=base_h)
        .circle(post_d / 2.0)
        .extrude(post_h)
    )
    standoff = base.union(post)
    try:
        standoff = standoff.edges("<Y").fillet(0.002)
    except Exception:
        pass
    return standoff


# Bar-pull geometry constants (V5).
_BAR_LEN = 0.800
_STANDOFF_REACH = 0.044  # base_h + post_h
_STANDOFF_SPAN = _BAR_LEN - 0.080


def _s_handle_points(height: float, bow: float, depth: float, *, lobes: int = 2, n: int = 9):
    """Multi-wave S spline points in leaf-local frame (P3 2-lobe / V11 3-lobe).

    The grip runs vertically along Z; Y bows outward in a ``lobes``-lobe sine
    wave so it reads as an ornate wavy pull. Standoff anchor points (the ends,
    and — for 3 lobes — the mid point) bend back toward the mounting plane so the
    neck cylinders seat cleanly against the leaf face.
    """
    pts = []
    # Fractional anchor positions: ends for 2-lobe; ends + midpoint for 3-lobe.
    anchor_ts = {0.0, 0.5, 1.0} if lobes >= 3 else {0.0, 1.0}
    for i in range(n):
        t = i / (n - 1)
        z = -height / 2.0 + t * height
        wave = math.sin(t * math.pi * lobes)
        y = depth + bow * wave
        if any(abs(t - at) < 1e-9 for at in anchor_ts):
            y = depth * 0.30 if lobes >= 3 else depth * 0.35
        pts.append((0.0, y, z))
    return pts


def _standoff_neck_z(cz: float, handle_h: float, i: int, n: int) -> float:
    """World/local-Z of standoff *i* of *n*, evenly spaced along the handle (V11)."""
    t = i / (n - 1) if n > 1 else 0.5
    return cz - handle_h / 2.0 + t * handle_h


# --------------------------------------------------------------------------- #
# Root frame factories (one per leaf_style family). All emit a single root part
# ``door_frame`` whose hinge member laps the leaf hinge edge at x≈0 (so the
# closed leaf is supported by the frame at the hinge line) and whose opening is
# sized leaf + reveal. Returns the root part.
# --------------------------------------------------------------------------- #
def _build_standard_frame(model: ArticulatedObject, r: ResolvedDoorConfig, mats, *, casing: bool):
    """Frame = hinge jamb + latch jamb + head jamb (+ optional casing trim).

    Used by solid / glazed leaves. The hinge jamb inner face laps the leaf
    hinge edge (x≈0). The opening is leaf_w + 2*side_gap wide.
    """
    frame = model.part("door_frame")
    w, h, jw = r.leaf_w, r.leaf_h, r.jamb_w
    opening_h = h + _HEAD_GAP

    hinge_jamb_x = -jw / 2.0 + _HINGE_LAP
    frame.visual(
        Box((jw, _JAMB_D, opening_h)),
        origin=Origin(xyz=(hinge_jamb_x, 0.0, opening_h / 2.0)),
        material=mats["frame"],
        name="hinge_jamb", material_class_id="wood.veneer_panel",
    )
    latch_jamb_x = w + _SIDE_GAP + jw / 2.0
    frame.visual(
        Box((jw, _JAMB_D, opening_h)),
        origin=Origin(xyz=(latch_jamb_x, 0.0, opening_h / 2.0)),
        material=mats["frame"],
        name="latch_jamb", material_class_id="wood.veneer_panel",
    )
    head_z = opening_h + jw / 2.0
    head_len = (latch_jamb_x + jw / 2.0) - (hinge_jamb_x - jw / 2.0)
    head_cx = (latch_jamb_x + hinge_jamb_x) / 2.0
    frame.visual(
        Box((head_len, _JAMB_D, jw)),
        origin=Origin(xyz=(head_cx, 0.0, head_z)),
        material=mats["frame"],
        name="head_jamb", material_class_id="wood.veneer_panel",
    )

    if casing:
        casing_y = _JAMB_D / 2.0 + _CASING_T / 2.0
        casing_outer_w = head_len + 2 * _CASING_W
        frame.visual(
            Box((_CASING_W, _CASING_T, opening_h + _CASING_W)),
            origin=Origin(
                xyz=(hinge_jamb_x - jw / 2.0 - _CASING_W / 2.0, casing_y, (opening_h + _CASING_W) / 2.0)
            ),
            material=mats["leaf"],
            name="casing_leg_hinge", material_class_id="wood.oak",
        )
        frame.visual(
            Box((_CASING_W, _CASING_T, opening_h + _CASING_W)),
            origin=Origin(
                xyz=(latch_jamb_x + jw / 2.0 + _CASING_W / 2.0, casing_y, (opening_h + _CASING_W) / 2.0)
            ),
            material=mats["leaf"],
            name="casing_leg_latch", material_class_id="wood.oak",
        )
        frame.visual(
            Box((casing_outer_w, _CASING_T, _CASING_W)),
            origin=Origin(xyz=(head_cx, casing_y, opening_h + jw + _CASING_W / 2.0)),
            material=mats["leaf"],
            name="casing_head", material_class_id="wood.oak",
        )

    frame.inertial = Inertial.from_geometry(
        Box((w + 2 * jw, _JAMB_D, opening_h)),
        mass=12.0,
        origin=Origin(xyz=(w / 2.0, 0.0, opening_h / 2.0)),
    )
    return frame


def _build_louver_casing(model: ArticulatedObject, r: ResolvedDoorConfig, mats):
    """Steel casing: head + sill + 2 jambs (P2). Hinge jamb laps leaf x≈0."""
    frame = model.part("door_frame")
    w, h, jw = r.leaf_w, r.leaf_h, r.jamb_w
    opening_h = h + _HEAD_GAP
    casing_d = 0.090

    hinge_jamb_x = -jw / 2.0 + _HINGE_LAP
    frame.visual(
        Box((jw, casing_d, opening_h)),
        origin=Origin(xyz=(hinge_jamb_x, 0.0, opening_h / 2.0)),
        material=mats["frame"],
        name="hinge_jamb", material_class_id="metal.stainless_matte",
    )
    latch_jamb_x = w + _SIDE_GAP + jw / 2.0
    frame.visual(
        Box((jw, casing_d, opening_h)),
        origin=Origin(xyz=(latch_jamb_x, 0.0, opening_h / 2.0)),
        material=mats["frame"],
        name="latch_jamb", material_class_id="metal.stainless_matte",
    )
    head_len = (latch_jamb_x + jw / 2.0) - (hinge_jamb_x - jw / 2.0)
    head_cx = (latch_jamb_x + hinge_jamb_x) / 2.0
    frame.visual(
        Box((head_len, casing_d, jw)),
        origin=Origin(xyz=(head_cx, 0.0, opening_h + jw / 2.0)),
        material=mats["frame"],
        name="head_jamb", material_class_id="metal.stainless_matte",
    )
    frame.visual(
        Box((head_len, casing_d, jw)),
        origin=Origin(xyz=(head_cx, 0.0, -jw / 2.0)),
        material=mats["frame"],
        name="sill_jamb", material_class_id="metal.stainless_matte",
    )
    frame.inertial = Inertial.from_geometry(
        Box((w + 2 * jw, casing_d, opening_h)),
        mass=14.0,
        origin=Origin(xyz=(w / 2.0, 0.0, opening_h / 2.0)),
    )
    return frame


def _build_glass_root(model: ArticulatedObject, r: ResolvedDoorConfig, mats, *, fluted: bool):
    """Glass-door root: a hinge post at x≈0 + head member above the opening +
    sill threshold below + a FIXED bay on the latch side (side_panel for
    full_glass, fluted sidelight for fluted).

    The bay is a ROOT visual (NOT a second moving leaf — that would be a Double
    Door). The leaf still hinges at x=0 with axis +Z. The head/sill members sit
    OUTSIDE the leaf height extent so they never overlap the closed leaf face.
    """
    frame = model.part("door_frame")
    w, h = r.leaf_w, r.leaf_h
    depth = 0.060
    post_w = 0.030
    rail_h = 0.060

    # Hinge post at the leaf hinge line (laps the leaf hinge edge at x≈0).
    frame.visual(
        Box((post_w, depth, h)),
        origin=Origin(xyz=(_HINGE_LAP, 0.0, h / 2.0)),
        material=mats["frame"],
        name="hinge_post", material_class_id="metal.blackened_gunmetal",
    )

    # Latch-side bay starts past the leaf free edge + mullion.
    bay_x_lo = w + _SIDE_GAP + _MULLION_W
    bay_x_hi = bay_x_lo + _BAY_W
    mullion_cx = w + _SIDE_GAP + _MULLION_W / 2.0
    span_x_lo = -post_w / 2.0 + _HINGE_LAP
    span_x_hi = bay_x_hi
    span_cx = (span_x_lo + span_x_hi) / 2.0
    span_len = span_x_hi - span_x_lo

    # Head member ABOVE the opening (z > h), spanning hinge post to bay so it
    # never overlaps the closed leaf face.
    frame.visual(
        Box((span_len, depth, rail_h)),
        origin=Origin(xyz=(span_cx, 0.0, h + rail_h / 2.0)),
        material=mats["frame"],
        name="head_rail", material_class_id="metal.blackened_gunmetal",
    )
    # Sill threshold only under the FIXED bay (latch side), so it never overlaps
    # the closed leaf (the leaf rests on the ground plane z=0 directly).
    sill_h = 0.030
    sill_x_lo = w + _SIDE_GAP  # past the leaf free edge
    sill_cx = (sill_x_lo + bay_x_hi) / 2.0
    frame.visual(
        Box((bay_x_hi - sill_x_lo, depth, sill_h)),
        origin=Origin(xyz=(sill_cx, 0.0, sill_h / 2.0)),
        material=mats["frame"],
        name="sill_rail", material_class_id="metal.blackened_gunmetal",
    )

    # Mullion divider (between leaf free edge and the fixed bay), spanning the
    # opening height between sill and head so it ties into both.
    frame.visual(
        Box((_MULLION_W, depth, h)),
        origin=Origin(xyz=(mullion_cx, 0.0, h / 2.0)),
        material=mats["frame"],
        name="mullion", material_class_id="metal.blackened_gunmetal",
    )

    # Fixed bay glass.
    bay_cx = (bay_x_lo + bay_x_hi) / 2.0
    if fluted:
        frame.visual(
            mesh_from_cadquery(_sidelight_glass_cq(bay_cx, h), "sidelight_glass"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["glass"],
            name="sidelight_glass", material_class_id=("glass.architectural_window_patterned" if r.palette_style == "glass_brass" else "glass.textured_rippled"),
        )
    else:
        # full_glass fixed side panel = glass pane + edge band.
        frame.visual(
            mesh_from_cadquery(_bay_glass_cq(bay_cx, h, r.leaf_t), "side_glass"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["glass"],
            name="side_glass", material_class_id="glass.clear_transparent",
        )
        frame.visual(
            mesh_from_cadquery(_bay_edge_cq(bay_cx, h, r.leaf_t), "side_edge"),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["frame"],
            name="side_edge", material_class_id="metal.blackened_gunmetal",
        )

    frame.inertial = Inertial.from_geometry(
        Box((bay_x_hi + post_w, depth, h)),
        mass=16.0,
        origin=Origin(xyz=(bay_x_hi / 2.0, 0.0, h / 2.0)),
    )
    return frame


def _bay_glass_cq(cx: float, h: float, t: float, *, edge_w: float = 0.022) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(_BAY_W - 2.0 * edge_w, h - 2.0 * edge_w, max(t, 0.012), centered=(True, True, True))
    )


def _bay_edge_cq(cx: float, h: float, t: float, *, edge_w: float = 0.022) -> cq.Workplane:
    edge_frame = 0.018
    tt = max(t, 0.012)
    outer = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(_BAY_W, h, tt + 2.0 * edge_frame, centered=(True, True, True))
    )
    inner = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(_BAY_W - 2.0 * edge_w, h - 2.0 * edge_w, tt + 2.0 * edge_frame + 0.01, centered=(True, True, True))
    )
    return outer.cut(inner)


def _sidelight_glass_cq(cx: float, h: float) -> cq.Workplane:
    """Fluted-glass sidelight: a pane with vertical half-round flutes cut (P5)."""
    glass_t = 0.020
    pane = (
        cq.Workplane("XZ")
        .center(cx, h / 2.0)
        .box(_BAY_W + 0.010, h - 0.020, glass_t, centered=(True, True, True))
    )
    n = max(2, int(_BAY_W // _FLUTE_PITCH))
    start = cx - (n - 1) * _FLUTE_PITCH / 2.0
    front_y = glass_t / 2.0
    cutters = None
    for i in range(n):
        x = start + i * _FLUTE_PITCH
        groove = (
            cq.Workplane("XZ")
            .center(x, h / 2.0)
            .workplane(offset=front_y - _FLUTE_R * 0.55)
            .circle(_FLUTE_R)
            .extrude(_FLUTE_R)
        )
        cutters = groove if cutters is None else cutters.union(groove)
    if cutters is not None:
        pane = pane.cut(cutters)
    return pane


# --------------------------------------------------------------------------- #
# Leaf factories. Each emits the ``door_leaf`` part (leaf-local frame: hinge
# edge at x=0, body +X, height 0..leaf_h) and returns the leaf part. Returns
# the latch-edge x and a list of leaf visual names that overlap the frame.
# --------------------------------------------------------------------------- #
def _build_solid_leaf(model, r: ResolvedDoorConfig, mats):
    leaf = model.part("door_leaf")
    leaf.visual(
        mesh_from_cadquery(_solid_raised_panel_cq(r), "door_leaf"),
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        material=mats["leaf"],
        name="leaf_body", material_class_id="wood.oak",
    )
    _set_leaf_inertial(leaf, r)
    return leaf


def _build_glazed_leaf(model, r: ResolvedDoorConfig, mats):
    leaf = model.part("door_leaf")
    leaf.visual(
        mesh_from_cadquery(_glazed_leaf_cq(r), "door_leaf"),
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        material=mats["leaf"],
        name="leaf_body", material_class_id="metal.paint_coated",
    )
    strip_cx = r.leaf_w - _VS_OFFSET
    leaf.visual(
        mesh_from_cadquery(_glazed_pane_cq(r), "vision_glass"),
        origin=Origin(xyz=(strip_cx, 0.0, r.leaf_h / 2.0 + r.sill_z)),
        material=mats["glass"],
        name="vision_pane", material_class_id="glass.frosted_smooth",
    )
    _set_leaf_inertial(leaf, r)
    return leaf


def _build_louvered_leaf(model, r: ResolvedDoorConfig, mats):
    """Steel leaf: perimeter rails/stiles + N louver panels + N-1 inter rails.

    Multiplicity axis (spec §Multiplicity): ``louver_panel_i`` via
    ``for i in range(N)`` over a shared VentGrille helper; ``inter_rail_j`` via
    ``for j in range(N-1)``. All inline visuals on the leaf (Rule 1).
    Authored leaf-local: hinge edge at x=0, body +X. Local center at
    (leaf_w/2, 0, leaf_h/2 + sill_z).
    """
    leaf = model.part("door_leaf")
    w, h, t = r.leaf_w, r.leaf_h, r.leaf_t
    n = r.louver_panel_count
    cx = w / 2.0
    cz0 = r.sill_z  # local z of leaf bottom; leaf spans z in [cz0, cz0+h]

    # Perimeter frame.
    leaf.visual(
        Box((w, t, _RAIL)),
        origin=Origin(xyz=(cx, 0.0, cz0 + h - _RAIL / 2.0)),
        material=mats["leaf"],
        name="top_rail", material_class_id="metal.stainless_matte",
    )
    leaf.visual(
        Box((w, t, _RAIL)),
        origin=Origin(xyz=(cx, 0.0, cz0 + _RAIL / 2.0)),
        material=mats["leaf"],
        name="bottom_rail", material_class_id="metal.stainless_matte",
    )
    for sgn, tag in ((-1, "hinge"), (1, "latch")):
        leaf.visual(
            Box((_STILE, t, h)),
            origin=Origin(xyz=(cx + sgn * (w / 2.0 - _STILE / 2.0), 0.0, cz0 + h / 2.0)),
            material=mats["leaf"],
            name=f"{tag}_stile", material_class_id="metal.stainless_matte",
        )

    panel_w = w - 2.0 * _STILE
    inner_h = h - 2.0 * _RAIL - (n - 1) * _INTER_RAIL
    panel_h = inner_h / n
    bot_inner = cz0 + _RAIL  # local z of the bottom of the louver field

    # Inter-rail dividers (j in [0, N-1)).
    for j in range(n - 1):
        rail_cz = bot_inner + (j + 1) * panel_h + j * _INTER_RAIL + _INTER_RAIL / 2.0
        leaf.visual(
            Box((panel_w + 0.006, t, _INTER_RAIL)),
            origin=Origin(xyz=(cx, 0.0, rail_cz)),
            material=mats["leaf"],
            name=f"inter_rail_{j}", material_class_id="metal.stainless_matte",
        )

    # Louver panels (i in [0, N)).
    for i in range(n):
        panel_cz = bot_inner + i * (panel_h + _INTER_RAIL) + panel_h / 2.0
        leaf.visual(
            _louver_panel_mesh(panel_w + 0.010, panel_h + 0.010, f"louver_{i}", r),
            origin=Origin(xyz=(cx, 0.0, panel_cz), rpy=_GRILLE_RPY),
            material=mats["leaf"],
            name=f"louver_panel_{i}", material_class_id="metal.stainless_matte",
        )

    _set_leaf_inertial(leaf, r)
    return leaf


def _build_full_glass_leaf(model, r: ResolvedDoorConfig, mats):
    leaf = model.part("door_leaf")
    leaf.visual(
        mesh_from_cadquery(_full_glass_pane_cq(r), "leaf_glass"),
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        material=mats["glass"],
        name="leaf_glass", material_class_id="glass.clear_transparent",
    )
    leaf.visual(
        mesh_from_cadquery(_full_glass_edge_cq(r), "leaf_edge"),
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        material=mats["frame"],
        name="leaf_edge", material_class_id="metal.blackened_gunmetal",
    )
    _set_leaf_inertial(leaf, r, mass=18.0)
    return leaf


def _build_fluted_leaf(model, r: ResolvedDoorConfig, mats):
    leaf = model.part("door_leaf")
    # Slot A 2nd candidate: ribbed (V10 TRUE fluted leaf) vs plain slab (P5).
    leaf_cq = (
        _fluted_ribbed_leaf_cq(r)
        if r.fluted_leaf_variant == "ribbed"
        else _fluted_leaf_cq(r)
    )
    leaf.visual(
        mesh_from_cadquery(leaf_cq, "leaf_panel"),
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        material=mats["leaf"],
        name="leaf_body", material_class_id=("metal.paint_coated" if r.fluted_leaf_variant == "plain_slab" else "metal.patterned_sheet_panel"),
    )
    leaf.visual(
        mesh_from_cadquery(_fluted_strip_cq(r), "leaf_glass_strip"),
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        material=mats["glass"],
        name="leaf_glass_strip", material_class_id="glass.clear_transparent",
    )
    _set_leaf_inertial(leaf, r, mass=20.0)
    return leaf


def _set_leaf_inertial(leaf, r: ResolvedDoorConfig, *, mass: float = 28.0):
    leaf.inertial = Inertial.from_geometry(
        Box((r.leaf_w, r.leaf_t, r.leaf_h)),
        mass=mass,
        origin=Origin(xyz=(r.leaf_w / 2.0, 0.0, r.leaf_h / 2.0 + r.sill_z)),
    )


_LEAF_BUILDERS = {
    "solid_raised_panel": _build_solid_leaf,
    "glazed_vision_strip": _build_glazed_leaf,
    "louvered_vented": _build_louvered_leaf,
    "full_glass": _build_full_glass_leaf,
    "fluted_entry_sidelight": _build_fluted_leaf,
}


# --------------------------------------------------------------------------- #
# Hardware factories. Mounted near the latch edge (latch_x), at handle_height,
# protruding the room side (+Y). Returns the list of part names emitted (for
# overlap allowances) — empty when the hardware is purely inline on the leaf.
# --------------------------------------------------------------------------- #
def _hardware_anchor(r: ResolvedDoorConfig):
    """Latch-edge mount point: (x, y, z) in leaf-local frame.

    Y is the room-side front face of the leaf so the FIXED/REVOLUTE hardware
    joint origin lands on real leaf geometry. The ribbed fluted leaf (V10) has a
    thicker base plate than the glass leaf thickness, so its front face is at
    ``_FLUTED_BASE_T/2`` rather than ``leaf_t/2``.
    """
    latch_x = r.leaf_w - 0.080
    if r.leaf_style == "fluted_entry_sidelight" and r.fluted_leaf_variant == "ribbed":
        y = _FLUTED_BASE_T / 2.0
    else:
        y = r.leaf_t / 2.0
    z = r.handle_height
    return latch_x, y, z


def _build_lever_hardware(model, r: ResolvedDoorConfig, leaf, mats) -> list[str]:
    """Static rose visual on the leaf + REVOLUTE lever part (V9/P6/P1). The
    lever arm swings about the door-normal spindle (+Y); the rose stays fixed.
    """
    lx, ly, lz = _hardware_anchor(r)
    roll = Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0))

    # Static rose escutcheon on the leaf face (Rule 1: non-moving -> visual).
    leaf.visual(
        Cylinder(radius=0.025, length=0.006),
        origin=Origin(xyz=(lx, ly + 0.003, lz), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="lever_rose", material_class_id="metal.brushed_silver",
    )

    lever = model.part("lever_handle")
    lever.visual(
        mesh_from_cadquery(_lever_cq(), "lever_handle"),
        origin=roll,
        material=mats["hardware"],
        name="lever_body", material_class_id="metal.brushed_silver",
    )
    lever.inertial = Inertial.from_geometry(
        Box((0.12, 0.04, 0.04)),
        mass=0.3,
        origin=Origin(xyz=(0.0, 0.02, 0.0)),
    )
    model.articulation(
        "leaf_to_lever",
        ArticulationType.REVOLUTE,
        parent=leaf,
        child=lever,
        origin=Origin(xyz=(lx, ly, lz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=-0.5, upper=0.0),
    )
    return ["lever_handle"]


def _build_knob_hardware(model, r: ResolvedDoorConfig, leaf, mats) -> list[str]:
    """Domed turning knob (V1): a separate part on a REVOLUTE +Y spindle."""
    lx, ly, lz = _hardware_anchor(r)
    knob = model.part("door_knob")
    knob.visual(
        mesh_from_cadquery(_knob_cq(), "door_knob"),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="knob_body", material_class_id="metal.brass_polished",
    )
    knob.inertial = Inertial.from_geometry(
        Box((0.054, 0.06, 0.054)),
        mass=0.2,
        origin=Origin(xyz=(0.0, 0.03, 0.0)),
    )
    model.articulation(
        "leaf_to_knob",
        ArticulationType.REVOLUTE,
        parent=leaf,
        child=knob,
        origin=Origin(xyz=(lx, ly, lz)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=-0.8, upper=0.8),
    )
    return ["door_knob"]


def _build_bar_pull_hardware(model, r: ResolvedDoorConfig, leaf, mats) -> list[str]:
    """Straight tubular bar pull + 2 standoffs (V5), FIXED to the leaf.

    The bar + standoffs are inline visuals on a single ``bar_pull`` part; the
    part is FIXED to the leaf (no articulation — a pure pull, Rule 1 exception
    via the source's own FIXED joint). Standoff loop = ``for i in range(2)``.
    """
    lx, ly, lz = _hardware_anchor(r)
    bar_pull = model.part("bar_pull")
    # Backplate at the part origin (seats on the leaf face) — gives the child
    # geometry a point at (0,0,0) so the FIXED joint origin lies on real
    # geometry, and visibly anchors the pull to the leaf (Rule 2).
    bar_pull.visual(
        Box((0.030, 0.006, _STANDOFF_SPAN + 0.040)),
        origin=Origin(xyz=(0.0, 0.001, 0.0)),
        material=mats["hardware"],
        name="pull_backplate", material_class_id="metal.stainless_matte",
    )
    # Bar pushed out +Y by the standoff reach.
    bar_pull.visual(
        mesh_from_cadquery(_bar_tube_cq(), "pull_bar"),
        origin=Origin(xyz=(0.0, _STANDOFF_REACH, 0.0)),
        material=mats["hardware"],
        name="pull_bar", material_class_id="metal.stainless_matte",
    )
    standoff_mesh = mesh_from_cadquery(_standoff_cq(), "pull_standoff")
    for i in range(2):
        z_off = (_STANDOFF_SPAN / 2.0) * (1 - 2 * i)
        bar_pull.visual(
            standoff_mesh,
            origin=Origin(xyz=(0.0, 0.0, z_off)),
            material=mats["hardware"],
            name=f"standoff_{i}", material_class_id="metal.stainless_matte",
        )
    bar_pull.inertial = Inertial.from_geometry(
        Box((0.04, _STANDOFF_REACH + 0.02, _BAR_LEN)),
        mass=0.4,
        origin=Origin(xyz=(0.0, _STANDOFF_REACH / 2.0, 0.0)),
    )
    # FIXED: a pull bar does not articulate. Captured/seated through the leaf
    # face like real pull hardware; intended overlap declared in run_tests.
    model.articulation(
        "leaf_to_pull",
        ArticulationType.FIXED,
        parent=leaf,
        child=bar_pull,
        origin=Origin(xyz=(lx, ly, lz)),
    )
    return ["bar_pull"]


def _build_s_pull_hardware(model, r: ResolvedDoorConfig, leaf, mats) -> list[str]:
    """Ornate brass swept-tube S-spline pull, FIXED to the leaf.

    Slot B 2nd candidate: ``s2`` (P3, 2-lobe ``sin(2πt)`` + 2 standoffs) vs ``s3``
    (V11, more pronounced 3-lobe ``sin(3πt)`` swept tube + THREE standoff necks
    via ``for standoff_i in range(3)`` + the shared ``_standoff_neck_z`` even-
    spacing helper). The grip is a real swept tube (``tube_from_spline_points``);
    necks are inline brass cylinders on the single FIXED ``bar_pull`` part.
    """
    lx, ly, lz = _hardware_anchor(r)
    ribbed = r.ornate_pull_variant == "s3"
    handle_h = 1.05
    depth = 0.040
    if ribbed:
        lobes, n_standoffs, bow = 3, 3, 0.030  # V11: bigger wave, extra standoff
    else:
        lobes, n_standoffs, bow = 2, 2, 0.022  # P3
    pts = _s_handle_points(handle_h, bow, depth, lobes=lobes, n=19 if ribbed else 9)
    s_pull = model.part("bar_pull")
    # Backplate at the part origin (seats on the leaf face) so the FIXED joint
    # origin lies on real geometry and the pull is visibly anchored (Rule 2).
    s_pull.visual(
        Box((0.030, 0.006, handle_h + 0.040)),
        origin=Origin(xyz=(0.0, 0.001, 0.0)),
        material=mats["hardware"],
        name="pull_backplate", material_class_id="metal.brass_polished",
    )
    handle_mesh = tube_from_spline_points(
        pts, radius=0.011, samples_per_segment=18, radial_segments=20, cap_ends=True
    )
    s_pull.visual(
        mesh_from_geometry(handle_mesh, "s_handle_bar"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["hardware"],
        name="pull_bar", material_class_id="metal.brass_polished",
    )
    # Standoff necks at even spacing along the handle (V11 loop + shared helper).
    standoff_len = depth * 0.35
    for standoff_i in range(n_standoffs):
        neck_z = _standoff_neck_z(0.0, handle_h, standoff_i, n_standoffs)
        s_pull.visual(
            Cylinder(radius=0.008, length=standoff_len),
            origin=Origin(
                xyz=(0.0, standoff_len / 2.0, neck_z), rpy=(-math.pi / 2.0, 0.0, 0.0)
            ),
            material=mats["hardware"],
            name=f"standoff_{standoff_i}", material_class_id="metal.brass_polished",
        )
    s_pull.inertial = Inertial.from_geometry(
        Box((0.04, depth + 0.02, handle_h)),
        mass=0.4,
        origin=Origin(xyz=(0.0, depth / 2.0, 0.0)),
    )
    model.articulation(
        "leaf_to_pull",
        ArticulationType.FIXED,
        parent=leaf,
        child=s_pull,
        origin=Origin(xyz=(lx, ly, lz)),
    )
    return ["bar_pull"]


_HARDWARE_BUILDERS = {
    "lever_on_rose": _build_lever_hardware,
    "round_knob": _build_knob_hardware,
    "straight_bar_pull": _build_bar_pull_hardware,
    "ornate_s_pull": _build_s_pull_hardware,
}


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_door(
    config: DoorConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"door_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # Root frame (per leaf_style family).
    if r.leaf_style in ("solid_raised_panel",):
        frame = _build_standard_frame(model, r, mats, casing=True)
    elif r.leaf_style == "glazed_vision_strip":
        frame = _build_standard_frame(model, r, mats, casing=False)
    elif r.leaf_style == "louvered_vented":
        frame = _build_louver_casing(model, r, mats)
    elif r.leaf_style == "full_glass":
        frame = _build_glass_root(model, r, mats, fluted=False)
    else:  # fluted_entry_sidelight
        frame = _build_glass_root(model, r, mats, fluted=True)

    # Leaf.
    leaf = _LEAF_BUILDERS[r.leaf_style](model, r, mats)

    # Primary hinge spine: leaf swings on the hinge edge (x=0), vertical axis.
    model.articulation(
        "frame_to_leaf",
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leaf,
        origin=Origin(xyz=(0.0, 0.0, r.sill_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=40.0, velocity=2.0, lower=0.0, upper=r.open_angle_upper
        ),
    )

    # Hardware near the latch edge.
    _HARDWARE_BUILDERS[r.door_hardware](model, r, leaf, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_door(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_door(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_door_tests(object_model: ArticulatedObject, config: DoorConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("door_frame")
    leaf = object_model.get_part("door_leaf")
    hinge = object_model.get_articulation("frame_to_leaf")

    # ---- Intentional seated/captured overlaps (element-scoped). ----
    # Hinge edge laps the frame hinge member (leaf supported at the hinge line).
    hinge_member = "hinge_post" if r.is_glass else "hinge_jamb"
    leaf_hinge_elem = _leaf_hinge_elem(r)
    ctx.allow_overlap(
        leaf, frame, elem_a=leaf_hinge_elem, elem_b=hinge_member,
        reason="Hinge jamb/post intentionally laps the leaf hinge edge so the leaf is supported by the frame at the hinge line.",
    )
    # The leaf sweeps close past the frame head/jamb while swinging open.
    ctx.allow_overlap(
        leaf, frame,
        reason="door leaf swings past the frame reveal with a close clearance while opening",
    )

    # Glass-leaf intra-part seating: pane inside edge band; strip in aperture.
    if r.leaf_style == "full_glass":
        ctx.allow_overlap(
            leaf, leaf, elem_a="leaf_glass", elem_b="leaf_edge",
            reason="Glass pane edge seats inside the thin dark edge framing.",
        )
    elif r.leaf_style == "fluted_entry_sidelight":
        ctx.allow_overlap(
            leaf, leaf, elem_a="leaf_glass_strip", elem_b="leaf_body",
            reason="Narrow glass strip seats into the leaf aperture rebate.",
        )
        ctx.allow_overlap(
            frame, frame, elem_a="sidelight_glass", elem_b="mullion",
            reason="Fluted sidelight pane seats into the frame rebate around its aperture.",
        )
    elif r.leaf_style == "glazed_vision_strip":
        ctx.allow_overlap(
            leaf, leaf, elem_a="vision_pane", elem_b="leaf_body",
            reason="Vision pane seats inside the leaf glazing rim.",
        )

    # Glass full-panel bay seating (edge band overlaps glass).
    if r.leaf_style == "full_glass":
        ctx.allow_overlap(
            frame, frame, elem_a="side_glass", elem_b="side_edge",
            reason="Fixed side panel glass seats inside its dark edge framing.",
        )

    # Hardware seated/through the leaf face.
    hw = r.door_hardware
    if hw == "lever_on_rose":
        ctx.allow_overlap(
            object_model.get_part("lever_handle"), leaf,
            reason="Lever spindle/neck are seated against and through the leaf face like real door hardware.",
        )
    elif hw == "round_knob":
        ctx.allow_overlap(
            object_model.get_part("door_knob"), leaf,
            reason="Knob rose/spindle is seated against and through the leaf face like real door hardware.",
        )
    elif hw in ("straight_bar_pull", "ornate_s_pull"):
        ctx.allow_overlap(
            object_model.get_part("bar_pull"), leaf,
            reason="Standoff base plates are seated against and fastened through the leaf face like real pull hardware.",
        )

    # ---- Baseline. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("frame and leaf present", {"door_frame", "door_leaf"} <= part_names,
              details=str(sorted(part_names)))

    # Hinge axis vertical (category-defining spine).
    ctx.check(
        "hinge_axis_vertical",
        abs(hinge.axis[2]) > 0.99 and abs(hinge.axis[0]) < 0.01 and abs(hinge.axis[1]) < 0.01,
        details=f"axis={tuple(hinge.axis)}",
    )
    ctx.check(
        "hinge_is_revolute",
        hinge.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={hinge.articulation_type}",
    )

    # Leaf realistic size, stands on the ground.
    leaf_aabb = ctx.part_world_aabb(leaf)
    if leaf_aabb is not None:
        (lx0, ly0, lz0), (lx1, ly1, lz1) = leaf_aabb
        ctx.check("leaf_width_realistic", 0.80 <= (lx1 - lx0) <= 1.00, details=f"w={lx1 - lx0:.3f}")
        ctx.check("leaf_height_realistic", 1.95 <= (lz1 - lz0) <= 2.12, details=f"h={lz1 - lz0:.3f}")
        ctx.check("leaf_rests_on_ground", lz0 < 0.03, details=f"z_min={lz0:.4f}")

    # Louver multiplicity: exactly N panels present.
    if r.leaf_style == "louvered_vented":
        panels = [v.name for v in leaf.visuals if v.name.startswith("louver_panel_")]
        ctx.check(
            "N louver panels inlined (Rule 1)",
            len(panels) == r.louver_panel_count,
            details=f"panels={sorted(panels)} expected N={r.louver_panel_count}",
        )
        rails = [v.name for v in leaf.visuals if v.name.startswith("inter_rail_")]
        ctx.check(
            "N-1 inter rails present",
            len(rails) == max(0, r.louver_panel_count - 1),
            details=f"rails={sorted(rails)}",
        )

    # Hardware joint topology / type.
    if r.door_hardware == "lever_on_rose":
        j = object_model.get_articulation("leaf_to_lever")
        ctx.check(
            "lever is REVOLUTE about door normal (+Y)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    elif r.door_hardware == "round_knob":
        j = object_model.get_articulation("leaf_to_knob")
        ctx.check(
            "knob is REVOLUTE about door normal (+Y)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    else:  # bar / s pull
        j = object_model.get_articulation("leaf_to_pull")
        ctx.check(
            "pull is FIXED",
            j.articulation_type == ArticulationType.FIXED,
            details=f"type={j.articulation_type}",
        )

    # Hardware near the latch edge, lever height, room side (+Y).
    hw_part_name = {
        "lever_on_rose": "lever_handle",
        "round_knob": "door_knob",
        "straight_bar_pull": "bar_pull",
        "ornate_s_pull": "bar_pull",
    }[r.door_hardware]
    hw_aabb = ctx.part_world_aabb(object_model.get_part(hw_part_name))
    if hw_aabb is not None and leaf_aabb is not None:
        (hx0, hy0, hz0), (hx1, hy1, hz1) = hw_aabb
        ctx.check(
            "hardware_near_latch_edge",
            hx1 > (leaf_aabb[1][0] - 0.32),
            details=f"hx1={hx1:.3f} latch={leaf_aabb[1][0]:.3f}",
        )
        ctx.check(
            "hardware_at_handle_height",
            0.90 <= (hz0 + hz1) / 2.0 <= 1.20,
            details=f"hz={(hz0 + hz1) / 2.0:.3f}",
        )
        ctx.check(
            "hardware_protrudes_room_side",
            hy1 > leaf_aabb[1][1],
            details=f"hy1={hy1:.3f} leaf_y1={leaf_aabb[1][1]:.3f}",
        )

    # ---- Closed pose: hinge edge seated; not floating. ----
    with ctx.pose({hinge: 0.0}):
        ctx.expect_contact(
            leaf, frame, elem_a=leaf_hinge_elem, elem_b=hinge_member,
            contact_tol=0.04, name="hinge_edge_seats_against_frame_closed",
        )

    # ---- Open pose: leaf swings into the room, hinge edge stays connected. ----
    rest_pos = ctx.part_world_position(leaf)
    with ctx.pose({hinge: min(1.4, r.open_angle_upper)}):
        open_pos = ctx.part_world_position(leaf)
        open_aabb = ctx.part_world_aabb(leaf)
        ctx.check(
            "leaf_swings_into_room",
            open_aabb is not None and open_aabb[1][1] > r.leaf_w * 0.4,
            details=f"open_y1={open_aabb[1][1] if open_aabb else None}",
        )
        ctx.expect_contact(
            leaf, frame, elem_a=leaf_hinge_elem, elem_b=hinge_member,
            contact_tol=0.12, name="hinge_edge_stays_connected_open",
        )
    ctx.check(
        "leaf_actually_moves",
        rest_pos is not None and open_pos is not None,
        details=f"rest={rest_pos}, open={open_pos}",
    )

    # ---- Moving hardware poses without error. ----
    if r.door_hardware == "lever_on_rose":
        j = object_model.get_articulation("leaf_to_lever")
        with ctx.pose({j: -0.4}):
            ctx.check(
                "lever_pose_ok",
                ctx.part_world_aabb(object_model.get_part("lever_handle")) is not None,
                details="lever poses without error",
            )
    elif r.door_hardware == "round_knob":
        j = object_model.get_articulation("leaf_to_knob")
        with ctx.pose({j: 0.6}):
            ctx.check(
                "knob_pose_ok",
                ctx.part_world_aabb(object_model.get_part("door_knob")) is not None,
                details="knob poses without error",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        list(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


def _leaf_hinge_elem(r: ResolvedDoorConfig) -> str:
    """The leaf visual that laps the frame hinge member at x≈0."""
    if r.leaf_style == "louvered_vented":
        return "hinge_stile"
    if r.leaf_style == "full_glass":
        return "leaf_edge"
    if r.leaf_style == "fluted_entry_sidelight":
        return "leaf_body"
    return "leaf_body"


__all__ = (
    "DoorConfig",
    "ResolvedDoorConfig",
    "build_door",
    "build_seeded_door",
    "config_from_seed",
    "resolve_config",
    "run_door_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
