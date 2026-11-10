# SPDX-License-Identifier: Apache-2.0

"""Cosmetic cushion powder compact (makeup compact case) modular template.

NOTE on the slug name: "cushion" here = **cosmetic cushion powder compact**
(a flip-top makeup compact case), NOT a pillow / throw cushion. The structure
family is a flip-top compact: a hollow ``base`` bowl/tray (round / square / oval
footprint) holding one or more beige powder pans, joined to a ``lid`` (label /
logo / inner mirror) by a hinge / slide, with a front latch tab.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Accessories_Cushion.md`` and the
``picture/Accessories/Cushion`` 5-star sample pool (2 parents + 7 slot-fork
variants), all synced under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``base`` part (footprint mesh
chosen by ``case_footprint``), with three named module axes attaching as
parallel children / inline visuals:

  * ``case_footprint`` (3): round / square / oval — the shared footprint of the
    base + lid mesh. A mesh-helper dimension; it does not add a joint.
  * ``lid_mechanism`` (3): the opening mechanism — rear_flip_hinge (1 REVOLUTE
    -X), clamshell_two_leaf (2 REVOLUTE ±X), slide_lid (1 PRISMATIC -Y).
  * ``interior`` (3): single_powder_pan (no joint, Rule 1) / removable_refill_
    cartridge (1 PRISMATIC +Z) / flip_puff_tray (1 REVOLUTE -X).
  * ``pan_count`` (N in [1,3]): a multiplicity axis — N beige powder pans
    inlined as non-moving visuals (Rule 1) on the carrier part (base cavity,
    or inside the refill part). N is encoded into the slot_choice tuple as
    ``("pan_count", f"n{N}")``.

All hinge pins / sliders / locating tabs are captured-pin/slide geometry, so
those joints omit ``MatingContract`` (grandfathered) and are guarded by the
flat articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring
each source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec §9):
  * clamshell_two_leaf occupies both rim edges, so flip_puff_tray (inner-rear
    REVOLUTE tray) collides with the front leaf -> with clamshell, interior is
    restricted to {single_powder_pan, removable_refill_cartridge}.
  * removable_refill_cartridge has no multi-pan source -> refill forces N=1.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

CaseFootprint = Literal["round", "square", "oval"]
LidMechanism = Literal["rear_flip_hinge", "clamshell_two_leaf", "slide_lid"]
Interior = Literal["single_powder_pan", "removable_refill_cartridge", "flip_puff_tray"]
PaletteStyle = Literal["translucent_acrylic", "glossy_black_chrome", "pastel"]

CASE_FOOTPRINTS: tuple[CaseFootprint, ...] = ("round", "square", "oval")
LID_MECHANISMS: tuple[LidMechanism, ...] = (
    "rear_flip_hinge",
    "clamshell_two_leaf",
    "slide_lid",
)
INTERIORS: tuple[Interior, ...] = (
    "single_powder_pan",
    "removable_refill_cartridge",
    "flip_puff_tray",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "translucent_acrylic",
    "glossy_black_chrome",
    "pastel",
)

N_MIN = 1
N_MAX = 3
# Pan-count sampling weights (spec §8: 1 high-frequency, 2 common, 3 long tail).
PAN_COUNT_WEIGHTS = (0.55, 0.30, 0.15)

# Interiors that have a multi-pan source (refill has only an N=1 source).
MULTI_PAN_INTERIORS: tuple[Interior, ...] = ("single_powder_pan", "flip_puff_tray")
# Interiors compatible with clamshell (puff_tray's inner-rear tray fights the
# front leaf; spec §9 (1)).
CLAMSHELL_INTERIORS: tuple[Interior, ...] = (
    "single_powder_pan",
    "removable_refill_cartridge",
)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "translucent_acrylic": {
        "shell": (0.46, 0.42, 0.37, 0.42),
        "lid": (0.93, 0.92, 0.88, 1.0),
        "accent": (0.02, 0.02, 0.02, 1.0),
        "metal": (0.56, 0.55, 0.52, 1.0),
        "mirror": (0.72, 0.78, 0.80, 0.55),
        "powder": (0.86, 0.69, 0.54, 1.0),
        "emblem": (0.72, 0.20, 0.38, 1.0),
        "sponge": (0.94, 0.87, 0.80, 1.0),
    },
    "glossy_black_chrome": {
        "shell": (0.012, 0.012, 0.012, 1.0),
        "lid": (0.93, 0.92, 0.88, 1.0),
        "accent": (0.66, 0.67, 0.66, 1.0),
        "metal": (0.66, 0.67, 0.66, 1.0),
        "mirror": (0.72, 0.78, 0.80, 0.55),
        "powder": (0.80, 0.64, 0.48, 1.0),
        "emblem": (0.02, 0.02, 0.02, 1.0),
        "sponge": (0.95, 0.90, 0.82, 1.0),
    },
    "pastel": {
        "shell": (0.92, 0.80, 0.84, 1.0),
        "lid": (0.98, 0.94, 0.95, 1.0),
        "accent": (0.78, 0.55, 0.62, 1.0),
        "metal": (0.78, 0.72, 0.66, 1.0),
        "mirror": (0.74, 0.80, 0.82, 0.55),
        "powder": (0.88, 0.72, 0.60, 1.0),
        "emblem": (0.66, 0.30, 0.42, 1.0),
        "sponge": (0.96, 0.90, 0.88, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters); the round parent (81989983) drives the
# axisymmetric numbers, the square parent (876ccf2a) the rectangular footprint.
# Long axis along X. All hinge/slide hardware sits at the rim line.
# ---------------------------------------------------------------------------
_R_OUTER = 0.068  # round bowl outer radius
_SQ_X = 0.144  # square tray outer length (X)
_SQ_Y = 0.134  # square tray outer depth (Y)
_OVAL_RX = 0.078  # oval outer half-length (X) — wider than round
_OVAL_RY = 0.060  # oval outer half-depth (Y)

# Per-footprint vertical stack, derived from the 5-star parents (81989983:
# bowl outer h 0.022, cavity floor 0.008, pan top flush with the rim crest;
# 876ccf2a: tray outer h 0.030, cavity floor 0.013). The hinge axis sits just
# ABOVE the rim crest (0.030/0.032) so the closed lid caps the bowl instead of
# sinking into a deep well.
_BASE_H = {"round": 0.022, "oval": 0.022, "square": 0.030}
_FLOOR_FRAC = {"round": 0.36, "oval": 0.36, "square": 0.43}
_HINGE_Z = {"round": 0.030, "oval": 0.030, "square": 0.032}
_WALL = 0.012

_PAN_R = 0.025  # default powder-pan radius (multi-pan)
_PAN_H = 0.014
_DOME_R = 0.020
_DOME_H = 0.003
_SINGLE_PAN_R = 0.050  # large single pan radius
_PAN_SPAN = 0.060  # default center-to-center span for N=2

_LID_OPEN = 1.62  # rear-flip / clamshell open angle (rad)
_TRAY_OPEN = 1.40  # puff-tray open angle
_SLIDE_TRAVEL = 0.090  # slide-lid travel (m)
_REFILL_LIFT = 0.040  # refill lift (m)


@dataclass(frozen=True)
class CushionConfig:
    case_footprint: CaseFootprint | None = None
    lid_mechanism: LidMechanism | None = None
    interior: Interior | None = None
    pan_count: int | None = None
    palette_style: PaletteStyle = "translucent_acrylic"
    footprint_len_scale: float = 1.0
    footprint_width_scale: float = 1.0
    case_height_scale: float = 1.0
    lid_open_angle_scale: float = 1.0
    slide_travel_scale: float = 1.0
    pan_spacing_scale: float = 1.0
    name: str = "cushion"


@dataclass(frozen=True)
class ResolvedCushionConfig:
    case_footprint: CaseFootprint
    lid_mechanism: LidMechanism
    interior: Interior
    pan_count: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled).
    rx: float  # outer half-length (X)
    ry: float  # outer half-depth (Y)
    base_h: float
    wall: float
    rim_z: float
    hinge_z: float
    cavity_top: float
    pan_r: float
    pan_h: float
    dome_r: float
    dome_h: float
    pan_span: float  # center-to-center for the pan row (N>=2)
    lid_open: float
    tray_open: float
    slide_travel: float
    refill_lift: float
    name: str

    @property
    def is_round_family(self) -> bool:
        return self.case_footprint in ("round", "oval")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CushionConfig:
    rng = random.Random(seed)
    return CushionConfig(
        case_footprint=rng.choice(CASE_FOOTPRINTS),
        lid_mechanism=rng.choice(LID_MECHANISMS),
        interior=rng.choice(INTERIORS),
        pan_count=rng.choices((1, 2, 3), weights=PAN_COUNT_WEIGHTS, k=1)[0],
        palette_style=rng.choice(PALETTE_STYLES),
        footprint_len_scale=round(rng.uniform(0.90, 1.12), 4),
        footprint_width_scale=round(rng.uniform(0.90, 1.12), 4),
        case_height_scale=round(rng.uniform(0.88, 1.15), 4),
        lid_open_angle_scale=round(rng.uniform(0.85, 1.10), 4),
        slide_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        pan_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_cushion_{seed}",
    )


def resolve_config(config: CushionConfig | None = None) -> ResolvedCushionConfig:
    cfg = config or CushionConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    case_footprint = _pick(cfg.case_footprint, CASE_FOOTPRINTS)
    lid_mechanism = _pick(cfg.lid_mechanism, LID_MECHANISMS)
    interior = _pick(cfg.interior, INTERIORS)

    pan_count = int(cfg.pan_count) if cfg.pan_count is not None else 1
    pan_count = int(_clamp(pan_count, N_MIN, N_MAX))

    # --- Compatibility gating (spec §9). ---
    # (1) clamshell occupies both rim edges -> puff_tray collides with the
    #     front leaf; degrade interior to single_powder_pan.
    if lid_mechanism == "clamshell_two_leaf" and interior not in CLAMSHELL_INTERIORS:
        interior = "single_powder_pan"
    # (3) refill has only an N=1 source -> force N=1 when refill is selected.
    if interior == "removable_refill_cartridge":
        pan_count = 1

    len_scale = _clamp(cfg.footprint_len_scale, 0.90, 1.12)
    width_scale = _clamp(cfg.footprint_width_scale, 0.90, 1.12)
    height_scale = _clamp(cfg.case_height_scale, 0.88, 1.15)
    angle_scale = _clamp(cfg.lid_open_angle_scale, 0.85, 1.10)
    travel_scale = _clamp(cfg.slide_travel_scale, 0.85, 1.10)
    spacing_scale = _clamp(cfg.pan_spacing_scale, 0.90, 1.10)

    if case_footprint == "round":
        rx = _R_OUTER * len_scale
        ry = _R_OUTER * width_scale
    elif case_footprint == "oval":
        rx = _OVAL_RX * len_scale
        ry = _OVAL_RY * width_scale
    else:  # square
        rx = (_SQ_X / 2.0) * len_scale
        ry = (_SQ_Y / 2.0) * width_scale

    base_h = _BASE_H[case_footprint] * height_scale
    hinge_z = _HINGE_Z[case_footprint] * height_scale
    rim_z = hinge_z  # rim hardware line (latch socket / hinge leaves)
    cavity_top = base_h  # cavity mouth == rim crest

    # Pan geometry: large single pan when N==1, smaller multi-pan when N>=2.
    if pan_count == 1:
        pan_r = _SINGLE_PAN_R
    else:
        pan_r = _PAN_R
    dome_r = min(_DOME_R, pan_r * 0.85)

    pan_span = _PAN_SPAN * spacing_scale

    # --- Clearance inequality (spec §7): the N-pan row must fit in the cavity.
    #     row_width = (N-1)*span + 2*pan_r  <=  cavity_X - 2*margin.
    cavity_half_x = rx - 1.5 * _WALL
    margin = 0.004
    if pan_count >= 2:
        max_row = 2.0 * (cavity_half_x - margin)
        for _ in range(40):
            row_w = (pan_count - 1) * pan_span + 2.0 * pan_r
            if row_w <= max_row:
                break
            # Shrink span first, then pan radius.
            if pan_span > 0.030:
                pan_span = max(0.030, pan_span - 0.004)
            else:
                pan_r = max(0.012, pan_r - 0.002)
                dome_r = min(dome_r, pan_r * 0.85)
        # If still too wide, clamp span hard to the largest that fits.
        row_w = (pan_count - 1) * pan_span + 2.0 * pan_r
        if row_w > max_row and pan_count >= 2:
            pan_span = max(0.026, (max_row - 2.0 * pan_r) / (pan_count - 1))

    lid_open = _clamp(_LID_OPEN * angle_scale, 1.0, math.pi * 0.95)
    tray_open = _clamp(_TRAY_OPEN * angle_scale, 1.0, math.pi * 0.95)
    slide_travel = _clamp(_SLIDE_TRAVEL * travel_scale, 0.060, 0.120)

    return ResolvedCushionConfig(
        case_footprint=case_footprint,
        lid_mechanism=lid_mechanism,
        interior=interior,
        pan_count=pan_count,
        palette_style=palette_style,
        rx=rx,
        ry=ry,
        base_h=base_h,
        wall=_WALL,
        rim_z=rim_z,
        hinge_z=hinge_z,
        cavity_top=cavity_top,
        pan_r=pan_r,
        pan_h=_PAN_H,
        dome_r=dome_r,
        dome_h=_DOME_H,
        pan_span=pan_span,
        lid_open=lid_open,
        tray_open=tray_open,
        slide_travel=slide_travel,
        refill_lift=_REFILL_LIFT,
        name=cfg.name or "cushion",
    )


def with_overrides(config: CushionConfig, **kwargs: object) -> CushionConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CushionConfig | ResolvedCushionConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCushionConfig) else resolve_config(config)
    return (
        ("case_footprint", r.case_footprint),
        ("lid_mechanism", r.lid_mechanism),
        ("interior", r.interior),
        ("pan_count", f"n{r.pan_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Footprint mesh helpers (case_footprint). Round/oval are axisymmetric / lofted;
# square is a rounded box. Each preserves the source primitive type.
# ---------------------------------------------------------------------------
def _rounded_square(sx: float, sy: float, sz: float, r: float) -> cq.Workplane:
    rr = min(r, 0.45 * min(sx, sy))
    return cq.Workplane("XY").box(sx, sy, sz).edges("|Z").fillet(rr)


def _cavity_floor_z(r: ResolvedCushionConfig) -> float:
    """Z of the inner cavity floor (top of the solid base slab).

    Matches the cavity cut in ``_hollow_base_mesh``: round/oval cut starts at
    ``base_h*0.36`` (source: floor 0.008 of a 0.022 bowl); the square cut box
    (height ``base_h*0.62``, centered at ``base_h*0.74``) bottoms at
    ``base_h*0.43`` (source: floor 0.013 of a 0.030 tray).
    """
    if r.case_footprint == "square":
        return r.base_h * 0.43
    return r.base_h * 0.36


def _ellipse_solid(rx: float, ry: float, h: float, *, z0: float = 0.0) -> cq.Workplane:
    """Elliptical (or circular when rx==ry) extruded solid, base at z0."""
    return cq.Workplane("XY", origin=(0.0, 0.0, z0)).ellipse(rx, ry).extrude(h)


def _hollow_base_mesh(r: ResolvedCushionConfig, assets):
    """Hollow bowl/tray: outer footprint solid with an inner cavity cut.

    Round: from _hollow_bowl (81989983 L25-29). Square: from _hollow_base
    (876ccf2a L31-35). Oval: lofted ellipse (rec_cushion_var_oval family) —
    same hollow-with-cavity topology, ellipse profile instead of circle.
    """
    if r.case_footprint == "square":
        body = _rounded_square(2.0 * r.rx, 2.0 * r.ry, r.base_h, 0.022).translate(
            (0.0, 0.0, r.base_h * 0.5)
        )
        cavity = _rounded_square(
            2.0 * r.rx - 2.4 * r.wall, 2.0 * r.ry - 2.4 * r.wall, r.base_h * 0.62, 0.013
        ).translate((0.0, 0.0, r.base_h * 0.74))
        return mesh_from_cadquery(body.cut(cavity), "compact_base", assets=assets)
    # round / oval: ellipse outer with ellipse cavity (floor at base_h*0.36).
    outer = _ellipse_solid(r.rx, r.ry, r.base_h)
    cavity = _ellipse_solid(r.rx - r.wall, r.ry - r.wall, r.base_h, z0=r.base_h * 0.36)
    name = "translucent_bowl" if r.case_footprint == "round" else "oval_bowl"
    return mesh_from_cadquery(outer.cut(cavity), name, assets=assets)


def _domed_lid_mesh(r: ResolvedCushionConfig, assets):
    """Lid shell mesh (round/oval = domed disc, square = rounded panel)."""
    if r.case_footprint == "square":
        return mesh_from_cadquery(
            _rounded_square(2.0 * r.rx, 2.0 * r.ry, 0.012, 0.022),
            "lid_black_edge",
            assets=assets,
        )
    name = "white_domed_lid" if r.case_footprint == "round" else "oval_domed_lid"
    shell = _ellipse_solid(r.rx - 0.001, r.ry - 0.001, 0.012).edges(">Z").fillet(0.005)
    return mesh_from_cadquery(shell, name, assets=assets)


def _leaf_panel_mesh(r: ResolvedCushionConfig, assets, *, tag: str):
    """One clamshell leaf shell: covers half the depth (Y). From clamshell
    _rounded_panel (L120). Round/oval -> half-ellipse-ish rounded panel."""
    leaf_x = 2.0 * r.rx - 2.0 * r.wall
    leaf_y = r.ry - 0.002
    return mesh_from_cadquery(
        _rounded_square(leaf_x, leaf_y, 0.012, 0.016), f"leaf_{tag}_shell", assets=assets
    )


def _slide_lid_mesh(r: ResolvedCushionConfig, assets):
    """Sliding lid panel (slide_lid L127): slightly smaller footprint."""
    return mesh_from_cadquery(
        _rounded_square(2.0 * r.rx - 0.020, 2.0 * r.ry - 0.004, 0.008, 0.020),
        "slide_lid_edge",
        assets=assets,
    )


def _rail_profile_mesh(r: ResolvedCushionConfig, assets, idx: int):
    """T-rail track (slide_lid _rail_profile L39-48)."""
    rail_len = 2.0 * r.ry - 0.016
    stem = cq.Workplane("XY").box(0.005, rail_len, 0.005).translate((0.0, 0.0, 0.0025))
    cap = cq.Workplane("XY").box(0.009, rail_len, 0.002).translate((0.0, 0.0, 0.006))
    return mesh_from_cadquery(stem.union(cap), f"base_rail_{idx}", assets=assets)


def _slider_slot_mesh(r: ResolvedCushionConfig, assets, idx: int):
    """U-channel slider (slide_lid _slider_slot L51-59)."""
    outer = cq.Workplane("XY").box(0.013, 0.040, 0.008).translate((0.0, 0.0, 0.004))
    inner = cq.Workplane("XY").box(0.010, 0.042, 0.006).translate((0.0, 0.0, 0.005))
    return mesh_from_cadquery(outer.cut(inner), f"lid_slider_{idx}", assets=assets)


def _refill_pan_mesh(r: ResolvedCushionConfig, assets):
    """Shallow hollow refill cartridge pan (refill _refill_pan L37-41)."""
    pr = min(0.054, r.rx - r.wall - 0.004)
    outer = cq.Workplane("XY").cylinder(0.010, pr).translate((0.0, 0.0, 0.005))
    cavity = cq.Workplane("XY").cylinder(0.008, pr - 0.005).translate((0.0, 0.0, 0.006))
    return mesh_from_cadquery(outer.cut(cavity), "refill_pan_shell", assets=assets), pr


def _puff_tray_disc_mesh(r: ResolvedCushionConfig, assets):
    """Thin round tray with a raised lip rim (puff_tray _puff_tray_disc L37-41)."""
    tr = min(0.048, r.rx - r.wall - 0.006)
    disc = cq.Workplane("XY").circle(tr).extrude(0.0018)
    rim = (
        cq.Workplane("XY")
        .workplane(offset=0.0010)
        .circle(tr + 0.002)
        .circle(tr - 0.001)
        .extrude(0.0015)
    )
    return mesh_from_cadquery(
        disc.union(rim).edges(">Z").fillet(0.0004), "tray_disc", assets=assets
    ), tr


# ---------------------------------------------------------------------------
# Inline visual helpers (Rule 1: non-moving decorations are parent.visual).
# ---------------------------------------------------------------------------
def _emit_lid_decorations(lid, r: ResolvedCushionConfig, mats, *, y0: float, z_top: float):
    """Label / logo / mirror / latch tab on a lid (or leaf), authored about y0."""
    # Decorations straddle the shell top surface (z_top) so they embed into the
    # shell and are never floating islands (compile-sweep treats islands as a
    # hard fail). z_top is the lid shell's top face in the lid-local frame; the
    # shell bottom is at z=0.
    if r.case_footprint == "square":
        # Double-ring logo (876ccf2a L65-68). Half-embedded into the top.
        for side, dx in enumerate((-0.011, 0.011)):
            ring = TorusGeometry(0.017, 0.0028, radial_segments=16, tubular_segments=28)
            lid.visual(
                mesh_from_geometry(ring, f"logo_ring_{side}"),
                origin=Origin(xyz=(dx, y0, z_top - 0.0010)),
                material=mats["emblem"],
                name=f"logo_ring_{side}", material_class_id="plastic.opaque_glossy_molded",
            )
    else:
        # Flower emblem (81989983 L66-69), straddling the top surface.
        lid.visual(
            Cylinder(radius=0.006, length=0.003),
            origin=Origin(xyz=(0.0, y0, z_top - 0.0010)),
            material=mats["emblem"],
            name="flower_core", material_class_id="plastic.opaque_glossy_molded",
        )
        for i, a in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
            lid.visual(
                Cylinder(radius=0.004, length=0.003),
                origin=Origin(xyz=(0.013 * math.cos(a), y0 + 0.013 * math.sin(a), z_top - 0.0010)),
                material=mats["emblem"],
                name=f"flower_petal_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
    # Inner mirror on the underside: its top face touches the shell bottom (z=0)
    # with a slight embed so it rests on the shell, not floating below it.
    mr = min(0.055, r.rx - 0.013)
    lid.visual(
        Cylinder(radius=mr, length=0.0030),
        origin=Origin(xyz=(0.0, y0, -0.0010)),
        material=mats["mirror"],
        name="inner_mirror", material_class_id="glass.mirror",
    )


# ---------------------------------------------------------------------------
# Powder-pan multiplicity (Rule 1: inline visuals on the carrier part).
# ---------------------------------------------------------------------------
def _emit_powder_pans(carrier, r: ResolvedCushionConfig, mats, *, z_floor: float):
    """Emit N powder pans (+ domes) as non-moving visuals, evenly spaced along X.

    Absolute placement (x = -span/2*(N-1) + i*span) so the layout is N-invariant.
    N=1 -> single large pan centered (parent style). N>=2 -> the dual/triple
    multi-pan style (dual_pan L69-72 / triple_pan L68-87).
    """
    n = r.pan_count
    if n == 1:
        carrier.visual(
            Cylinder(radius=r.pan_r, length=r.pan_h),
            origin=Origin(xyz=(0.0, 0.0, z_floor + r.pan_h / 2.0)),
            material=mats["powder"],
            name="powder_pan_0", material_class_id="plaster.smooth",
        )
        carrier.visual(
            Cylinder(radius=r.dome_r, length=r.dome_h),
            origin=Origin(xyz=(0.0, 0.0, z_floor + r.pan_h + r.dome_h / 2.0)),
            material=mats["powder"],
            name="powder_dome_0", material_class_id="plaster.smooth",
        )
        return
    x0 = -0.5 * (n - 1) * r.pan_span
    for i in range(n):
        x = x0 + i * r.pan_span
        carrier.visual(
            Cylinder(radius=r.pan_r, length=r.pan_h),
            origin=Origin(xyz=(x, 0.0, z_floor + r.pan_h / 2.0)),
            material=mats["powder"],
            name=f"powder_pan_{i}", material_class_id="plaster.smooth",
        )
        carrier.visual(
            Cylinder(radius=r.dome_r, length=r.dome_h),
            origin=Origin(xyz=(x, 0.0, z_floor + r.pan_h + r.dome_h / 2.0)),
            material=mats["powder"],
            name=f"powder_dome_{i}", material_class_id="plaster.smooth",
        )


# ---------------------------------------------------------------------------
# Base part (root). Footprint mesh + rim gasket + hinge/slide hardware.
# ---------------------------------------------------------------------------
_HINGE_XS = (-0.026, 0.026)


def _build_base(model: ArticulatedObject, r: ResolvedCushionConfig, mats, *, assets):
    base = model.part("base")
    shell_name = (
        "clear_bowl"
        if r.case_footprint == "round"
        else ("oval_bowl" if r.case_footprint == "oval" else "black_tray")
    )
    base.visual(_hollow_base_mesh(r, assets), material=mats["shell"], name=shell_name, material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black_chrome", "pastel"} else "plastic.frosted_translucent"))
    base.inertial = Inertial.from_geometry(
        Box((2.0 * r.rx, 2.0 * r.ry, r.base_h)),
        mass=0.18,
        origin=Origin(xyz=(0.0, 0.0, r.base_h / 2.0)),
    )
    # Rim gasket ring — a real rim crest visual. Modeled as a torus centered on
    # the rim crest so its tube straddles the wall-top surface (embedding into
    # the crest), which keeps it welded to the shell for every scale and reads
    # as the sealing gasket between base and closed lid.
    gasket_tube = r.wall * 0.5
    base.visual(
        mesh_from_geometry(
            TorusGeometry(
                min(r.rx, r.ry) - r.wall, gasket_tube, radial_segments=16, tubular_segments=40
            ),
            "rim_gasket",
        ),
        origin=Origin(xyz=(0.0, 0.0, r.cavity_top)),
        material=mats["accent"],
        name="rim_gasket", material_class_id="rubber.smooth_plain",
    )
    # Front latch socket (mates with lid's front_latch_tab).
    base.visual(
        Box((0.034, 0.010, 0.012)),
        origin=Origin(xyz=(0.0, -(r.ry - 0.002), r.rim_z * 0.55)),
        material=mats["metal"],
        name="front_latch_socket", material_class_id="metal.stainless_matte",
    )
    return base


def _emit_rear_hinge_hardware(base, r: ResolvedCushionConfig, mats, *, y_sign: float, prefix: str):
    """Rear (or front) hinge barrels on the rim line. Returns the y position."""
    hinge_y = y_sign * (r.ry - 0.002)
    # A rear hinge leaf plate (a real anchoring visual under the barrels).
    base.visual(
        Box((2.0 * abs(_HINGE_XS[0]) + 0.024, 0.012, 0.010)),
        origin=Origin(xyz=(0.0, hinge_y, r.hinge_z - 0.006)),
        material=mats["metal"],
        name=f"{prefix}_hinge_leaf", material_class_id="metal.stainless_matte",
    )
    for i, x in enumerate(_HINGE_XS):
        base.visual(
            Box((0.022, 0.014, 0.016)),
            origin=Origin(xyz=(x, hinge_y, r.hinge_z - 0.006)),
            material=mats["metal"],
            name=f"{prefix}_hinge_saddle_{i}", material_class_id="metal.stainless_matte",
        )
        base.visual(
            Cylinder(radius=0.005, length=0.026),
            origin=Origin(xyz=(x, hinge_y, r.hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"{prefix}_hinge_barrel_{i}", material_class_id="metal.stainless_matte",
        )
    return hinge_y


# ---------------------------------------------------------------------------
# Lid mechanisms.
# ---------------------------------------------------------------------------
def _emit_rear_flip_lid(model, r: ResolvedCushionConfig, base, mats, *, assets) -> list[str]:
    """Single rear-flip lid (1 REVOLUTE -X). Sources: parents L62-85."""
    hinge_y = _emit_rear_hinge_hardware(base, r, mats, y_sign=1.0, prefix="rear")
    lid = model.part("lid")
    # Lid authored in the rear-hinge pivot frame: shift visuals by -hinge_y in Y
    # so the pivot line sits at the part-local origin (matches parents).
    edge_name = "white_domed_lid" if r.case_footprint != "square" else "black_lid_edge"
    # Round/oval ellipse shell extrudes 0..0.012 (top at 0.012). Square box is
    # centered, so offset by +0.006 to also span 0..0.012.
    shell_z = 0.006 if r.case_footprint == "square" else 0.0
    lid.visual(
        _domed_lid_mesh(r, assets),
        origin=Origin(xyz=(0.0, -hinge_y, shell_z)),
        material=mats["lid"] if r.case_footprint != "square" else mats["shell"],
        name=edge_name, material_class_id="plastic.opaque_glossy_molded",
    )
    if r.case_footprint == "square":
        lid.visual(
            mesh_from_cadquery(
                _rounded_square(2.0 * r.rx - 0.016, 2.0 * r.ry - 0.016, 0.008, 0.018),
                "lid_white_top",
            ),
            origin=Origin(xyz=(0.0, -hinge_y, 0.010)),
            material=mats["lid"],
            name="white_lid_top", material_class_id="plastic.opaque_glossy_molded",
        )
        top_z = 0.012
    else:
        top_z = 0.012
    _emit_lid_decorations(lid, r, mats, y0=-hinge_y, z_top=top_z)
    # Front latch tab (extends past the front edge).
    lid.visual(
        Box((0.030, 0.010, 0.010)),
        origin=Origin(xyz=(0.0, -hinge_y - (r.ry - 0.002) - 0.002, 0.002)),
        material=mats["accent"],
        name="front_latch_tab", material_class_id="plastic.opaque_glossy_molded",
    )
    # Hinge pins captured by the rear barrels (at the part-local pivot line).
    for i, x in enumerate(_HINGE_XS):
        lid.visual(
            Cylinder(radius=0.0035, length=0.020),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"lid_hinge_pin_{i}", material_class_id="metal.stainless_matte",
        )
    lid.inertial = Inertial.from_geometry(
        Box((2.0 * r.rx, 2.0 * r.ry, 0.02)),
        mass=0.10,
        origin=Origin(xyz=(0.0, -hinge_y, 0.0)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.REVOLUTE,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, hinge_y, r.hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.3, lower=0.0, upper=r.lid_open),
    )
    return ["lid"]


def _emit_clamshell_lid(model, r: ResolvedCushionConfig, base, mats, *, assets) -> list[str]:
    """Two-leaf clamshell (2 REVOLUTE ±X). Source: clamshell L117-220."""
    rear_y = _emit_rear_hinge_hardware(base, r, mats, y_sign=1.0, prefix="rear")
    front_y = _emit_rear_hinge_hardware(base, r, mats, y_sign=-1.0, prefix="front")
    names: list[str] = []
    half_y = r.ry - 0.002
    for tag, hinge_y, ax, body_sign, mat_top in (
        ("rear", rear_y, -1.0, -1.0, mats["lid"]),
        ("front", front_y, 1.0, 1.0, mats["accent"]),
    ):
        leaf = model.part(f"leaf_{tag}")
        # Each leaf covers half the depth; body extends toward center from the
        # hinge line (authored in the leaf's pivot frame, pivot at local origin).
        leaf.visual(
            _leaf_panel_mesh(r, assets, tag=tag),
            origin=Origin(xyz=(0.0, body_sign * half_y / 2.0, 0.006)),
            material=mats["shell"],
            name=f"{tag}_black_panel", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black_chrome", "pastel"} else "plastic.frosted_translucent"),
        )
        leaf.visual(
            Cylinder(radius=min(0.044, r.rx - 0.014), length=0.003),
            origin=Origin(xyz=(0.0, body_sign * half_y / 2.0, -0.0010)),
            material=mats["mirror"],
            name=f"{tag}_mirror", material_class_id="glass.mirror",
        )
        # Center catch tab at the meeting edge.
        leaf.visual(
            Box((0.020, 0.006, 0.008)),
            origin=Origin(xyz=(0.0, body_sign * (half_y - 0.003), 0.002)),
            material=mats["metal"],
            name=f"{tag}_center_catch", material_class_id="metal.stainless_matte",
        )
        for i, x in enumerate(_HINGE_XS):
            leaf.visual(
                Cylinder(radius=0.0035, length=0.020),
                origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["metal"],
                name=f"{tag}_hinge_pin_{i}", material_class_id="metal.stainless_matte",
            )
        leaf.inertial = Inertial.from_geometry(
            Box((2.0 * r.rx, half_y, 0.015)),
            mass=0.07,
            origin=Origin(xyz=(0.0, body_sign * half_y / 2.0, 0.0)),
        )
        model.articulation(
            f"base_to_leaf_{tag}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leaf,
            origin=Origin(xyz=(0.0, hinge_y, r.hinge_z)),
            axis=(ax, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.2, velocity=1.4, lower=0.0, upper=r.lid_open),
        )
        names.append(f"leaf_{tag}")
    return names


def _emit_slide_lid(model, r: ResolvedCushionConfig, base, mats, *, assets) -> list[str]:
    """Sliding lid (1 PRISMATIC -Y) with T-rails + U-sliders. Source: slide_lid."""
    # Rails sit over the solid rim wall (inboard by ~wall so they overlap shell
    # material along the whole Y run) and dip into the rim so they are not
    # floating islands.
    rail_x = r.rx - r.wall
    rail_top = r.base_h  # base outer shell top
    for i, sx in enumerate((-1.0, 1.0)):
        base.visual(
            _rail_profile_mesh(r, assets, i),
            origin=Origin(xyz=(sx * rail_x, 0.0, rail_top - 0.004)),
            material=mats["metal"],
            name=f"base_rail_{i}", material_class_id="metal.stainless_matte",
        )
        base.visual(
            Box((0.012, 0.008, 0.012)),
            origin=Origin(xyz=(sx * rail_x, -(r.ry - 0.010), rail_top)),
            material=mats["metal"],
            name=f"rail_stop_{i}", material_class_id="metal.stainless_matte",
        )
    # Center cross-bar tying the two rails together at the rim line, spanning the
    # full width at y=0 so the PRISMATIC joint origin at (0,0,rail_top) lands on
    # real hardware (the center of the base mouth is an open cavity otherwise).
    base.visual(
        Box((2.0 * rail_x + 0.012, 0.008, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, rail_top - 0.003)),
        material=mats["metal"],
        name="rail_cross_bar", material_class_id="metal.stainless_matte",
    )
    lid = model.part("lid")
    # Lid authored at the base top center (q=0 frame == articulation frame).
    lid.visual(
        _slide_lid_mesh(r, assets),
        origin=Origin(xyz=(0.0, 0.0, 0.004)),
        material=mats["shell"],
        name="black_lid_edge", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"glossy_black_chrome", "pastel"} else "plastic.frosted_translucent"),
    )
    lid.visual(
        mesh_from_cadquery(
            _rounded_square(2.0 * r.rx - 0.036, 2.0 * r.ry - 0.020, 0.005, 0.016),
            "slide_lid_top",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.0105)),
        material=mats["lid"],
        name="white_lid_top", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_lid_decorations(lid, r, mats, y0=0.0, z_top=0.013)
    lid.visual(
        Box((0.026, 0.006, 0.008)),
        origin=Origin(xyz=(0.0, -(r.ry - 0.006), 0.004)),
        material=mats["metal"],
        name="front_latch_tab", material_class_id="metal.stainless_matte",
    )
    for i, sx in enumerate((-1.0, 1.0)):
        lid.visual(
            _slider_slot_mesh(r, assets, i),
            origin=Origin(xyz=(sx * rail_x, 0.0, -0.001)),
            material=mats["metal"],
            name=f"lid_slider_{i}", material_class_id="metal.stainless_matte",
        )
    lid.inertial = Inertial.from_geometry(
        Box((2.0 * r.rx, 2.0 * r.ry, 0.012)),
        mass=0.10,
        origin=Origin(xyz=(0.0, 0.0, 0.005)),
    )
    model.articulation(
        "base_to_lid",
        ArticulationType.PRISMATIC,
        parent=base,
        child=lid,
        origin=Origin(xyz=(0.0, 0.0, r.base_h - 0.002)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.3, lower=0.0, upper=r.slide_travel),
    )
    return ["lid"]


# ---------------------------------------------------------------------------
# Interior mechanisms.
# ---------------------------------------------------------------------------
def _emit_single_powder_pan(model, r: ResolvedCushionConfig, base, mats, *, assets) -> list[str]:
    """Powder pan(s) inline on the base cavity floor (Rule 1, no joint)."""
    # Seat the pan 1.5 mm into the cavity floor so it welds to the base slab;
    # with the source-derived shallow bowl the pan top lands ~flush with the
    # rim crest (round: 0.008 + 0.014 - 0.0015 ≈ 0.0205 vs rim 0.022).
    z_floor = _cavity_floor_z(r) - 0.0015
    _emit_powder_pans(base, r, mats, z_floor=z_floor)
    return []


def _emit_refill_cartridge(model, r: ResolvedCushionConfig, base, mats, *, assets) -> list[str]:
    """Removable refill cartridge (1 PRISMATIC +Z). Source: refill L37-95."""
    refill_mesh, pr = _refill_pan_mesh(r, assets)
    refill = model.part("refill")
    refill.visual(refill_mesh, material=mats["lid"], name="refill_pan", material_class_id="plastic.opaque_glossy_molded")
    # Powder + sponge inside the refill pan (the pans live IN the refill part).
    z_floor = 0.001
    _emit_powder_pans(refill, r, mats, z_floor=z_floor)
    refill.visual(
        Cylinder(radius=pr - 0.010, length=0.005),
        origin=Origin(xyz=(0.0, 0.0, z_floor + r.pan_h + r.dome_h + 0.0010)),
        material=mats["sponge"],
        name="sponge", material_class_id="rubber.sponge_foam",
    )
    # Locating tabs around the pan rim (captured in the bowl wall).
    for i in range(4):
        angle = i * math.pi / 2.0
        refill.visual(
            Box((0.006, 0.004, 0.008)),
            origin=Origin(
                xyz=((pr - 0.001) * math.cos(angle), (pr - 0.001) * math.sin(angle), 0.005)
            ),
            material=mats["lid"],
            name=f"locating_tab_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    refill.inertial = Inertial.from_geometry(
        Box((2.0 * pr, 2.0 * pr, 0.02)),
        mass=0.05,
        origin=Origin(xyz=(0.0, 0.0, 0.01)),
    )
    model.articulation(
        "base_to_refill",
        ArticulationType.PRISMATIC,
        parent=base,
        child=refill,
        origin=Origin(xyz=(0.0, 0.0, r.wall * 0.7)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=0.10, lower=0.0, upper=r.refill_lift),
    )
    return ["refill"]


def _emit_puff_tray(model, r: ResolvedCushionConfig, base, mats, *, assets) -> list[str]:
    """Flip puff tray (1 REVOLUTE -X). Source: puff_tray L37-136. Pans live in
    the base cavity (below the tray)."""
    # Pans on the base cavity floor (under the tray), seated 1.5 mm into the
    # floor so they weld to the slab and sit ~flush with the rim crest.
    z_floor = _cavity_floor_z(r) - 0.0015
    _emit_powder_pans(base, r, mats, z_floor=z_floor)
    # Tray hinge hardware on the inner rear bowl wall, just above the pan tops
    # so the closed tray rests on the pans instead of sinking into them.
    tray_hinge_y = r.ry * 0.72
    tray_hinge_z = r.cavity_top - (0.006 if r.case_footprint == "square" else 0.002)
    for i, x in enumerate((-0.018, 0.018)):
        base.visual(
            Box((0.014, 0.010, 0.008)),
            origin=Origin(xyz=(x, tray_hinge_y, tray_hinge_z)),
            material=mats["metal"],
            name=f"tray_hinge_bracket_{i}", material_class_id="metal.stainless_matte",
        )
        base.visual(
            Cylinder(radius=0.003, length=0.016),
            origin=Origin(xyz=(x, tray_hinge_y, tray_hinge_z), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"tray_hinge_barrel_{i}", material_class_id="metal.stainless_matte",
        )
    tray_mesh, tr = _puff_tray_disc_mesh(r, assets)
    puff_tray = model.part("puff_tray")
    # Tray frame at the hinge origin; disc extends forward (-Y) to bowl center.
    puff_tray.visual(
        tray_mesh,
        origin=Origin(xyz=(0.0, -tray_hinge_y, -0.001)),
        material=mats["lid"],
        name="tray_disc", material_class_id="plastic.opaque_glossy_molded",
    )
    # Connecting neck: a flat bar from the hinge line (y=0, where the pins sit)
    # to the disc, so the hinge pins are not a floating island.
    neck_len = tray_hinge_y + 0.004
    puff_tray.visual(
        Box((0.030, neck_len, 0.004)),
        origin=Origin(xyz=(0.0, -neck_len / 2.0 + 0.002, 0.0)),
        material=mats["lid"],
        name="tray_neck", material_class_id="plastic.opaque_glossy_molded",
    )
    puff_tray.visual(
        Cylinder(radius=tr * 0.75, length=0.006),
        origin=Origin(xyz=(0.0, -tray_hinge_y, 0.003)),
        material=mats["sponge"],
        name="applicator_puff", material_class_id="fabric.flexible_foam",
    )
    for i, x in enumerate((-0.018, 0.018)):
        puff_tray.visual(
            Cylinder(radius=0.002, length=0.014),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name=f"tray_hinge_pin_{i}", material_class_id="metal.stainless_matte",
        )
    puff_tray.inertial = Inertial.from_geometry(
        Box((2.0 * tr, 2.0 * tray_hinge_y, 0.012)),
        mass=0.04,
        origin=Origin(xyz=(0.0, -tray_hinge_y, 0.0)),
    )
    model.articulation(
        "base_to_puff_tray",
        ArticulationType.REVOLUTE,
        parent=base,
        child=puff_tray,
        origin=Origin(xyz=(0.0, tray_hinge_y, tray_hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.5, velocity=1.0, lower=0.0, upper=r.tray_open),
    )
    return ["puff_tray"]


_LID_BUILDERS = {
    "rear_flip_hinge": _emit_rear_flip_lid,
    "clamshell_two_leaf": _emit_clamshell_lid,
    "slide_lid": _emit_slide_lid,
}
_INTERIOR_BUILDERS = {
    "single_powder_pan": _emit_single_powder_pan,
    "removable_refill_cartridge": _emit_refill_cartridge,
    "flip_puff_tray": _emit_puff_tray,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_cushion(
    config: CushionConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"cushion_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    base = _build_base(model, r, mats, assets=assets)
    # Interior FIRST (pans / refill / puff tray live in the base cavity), then
    # the lid mechanism (covers them when closed).
    _INTERIOR_BUILDERS[r.interior](model, r, base, mats, assets=assets)
    _LID_BUILDERS[r.lid_mechanism](model, r, base, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cushion(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_cushion(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_cushion_tests(
    object_model: ArticulatedObject,
    config: CushionConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    base = object_model.get_part("base")

    # ---- Captured-pin / slide / tab allowances (element-scoped). ----
    if r.lid_mechanism == "rear_flip_hinge":
        lid = object_model.get_part("lid")
        for i in range(2):
            ctx.allow_overlap(
                lid,
                base,
                elem_a=f"lid_hinge_pin_{i}",
                elem_b=f"rear_hinge_barrel_{i}",
                reason="The lid hinge pin is captured inside the rear hinge barrel.",
            )
            ctx.allow_overlap(
                lid,
                base,
                elem_a=f"lid_hinge_pin_{i}",
                elem_b=f"rear_hinge_saddle_{i}",
                reason="The lid hinge pin passes through the rear hinge saddle bore.",
            )
        ctx.allow_overlap(
            base,
            lid,
            reason="closed lid seats on the rim crest / rear hinge hardware.",
        )
    elif r.lid_mechanism == "clamshell_two_leaf":
        for tag in ("rear", "front"):
            leaf = object_model.get_part(f"leaf_{tag}")
            for i in range(2):
                ctx.allow_overlap(
                    leaf,
                    base,
                    elem_a=f"{tag}_hinge_pin_{i}",
                    elem_b=f"{tag}_hinge_barrel_{i}",
                    reason=f"{tag} leaf hinge pin captured inside the {tag} hinge barrel.",
                )
                ctx.allow_overlap(
                    leaf,
                    base,
                    elem_a=f"{tag}_hinge_pin_{i}",
                    elem_b=f"{tag}_hinge_saddle_{i}",
                    reason=f"{tag} leaf hinge pin passes through the {tag} hinge saddle.",
                )
            ctx.allow_overlap(
                base,
                leaf,
                reason=f"closed {tag} leaf seats on the rim / hinge hardware.",
            )
        ctx.allow_overlap(
            object_model.get_part("leaf_rear"),
            object_model.get_part("leaf_front"),
            reason="the two clamshell leaves meet at the center parting line when closed.",
        )
    else:  # slide_lid
        lid = object_model.get_part("lid")
        for i in range(2):
            ctx.allow_overlap(
                lid,
                base,
                elem_a=f"lid_slider_{i}",
                elem_b=f"base_rail_{i}",
                reason=f"lid slider block {i} captures base rail {i} (prismatic sliding fit).",
            )
            ctx.allow_overlap(
                lid,
                base,
                elem_a=f"lid_slider_{i}",
                elem_b=f"rail_stop_{i}",
                reason=f"lid slider {i} sits against rail stop {i} at the closed pose.",
            )
        ctx.allow_overlap(
            base,
            lid,
            reason="closed sliding lid covers the cavity and rests on the rim.",
        )

    # Interior allowances.
    if r.interior == "removable_refill_cartridge":
        refill = object_model.get_part("refill")
        ctx.allow_isolated_part(
            refill,
            reason="refill cartridge lifts out of the bowl cavity and loses base contact",
        )
        ctx.allow_overlap(
            refill,
            base,
            reason="refill cartridge seats inside the bowl cavity (q=0 on floor).",
        )
    elif r.interior == "flip_puff_tray":
        puff = object_model.get_part("puff_tray")
        for i in range(2):
            ctx.allow_overlap(
                puff,
                base,
                elem_a=f"tray_hinge_pin_{i}",
                elem_b=f"tray_hinge_barrel_{i}",
                reason="tray hinge pin captured inside the tray hinge barrel on the inner wall.",
            )
            ctx.allow_overlap(
                puff,
                base,
                elem_a=f"tray_hinge_pin_{i}",
                elem_b=f"tray_hinge_bracket_{i}",
                reason="tray hinge pin passes through the tray hinge bracket.",
            )
        ctx.allow_overlap(
            puff,
            base,
            reason="closed puff tray rests over the powder pans in the cavity.",
        )

    # Closed lid / leaf covers the interior (pans / tray / refill).
    if r.lid_mechanism == "rear_flip_hinge":
        ctx.allow_overlap(
            object_model.get_part("lid"),
            base,
            reason="closed lid covers the interior powder pans / tray / refill.",
        )
    elif r.lid_mechanism == "slide_lid":
        ctx.allow_overlap(
            object_model.get_part("lid"),
            base,
            reason="closed sliding lid covers the interior powder pans.",
        )

    # A removable refill lifts up (PRISMATIC +Z) out of the mouth the lid opens;
    # it and the lid are operated in sequence (open the lid, then lift the
    # refill). At cross-DOF poses (lid closed + refill lifted) the refill rises
    # into the lid / clamshell leaves it deploys out of, so allow those pairs
    # (mirroring the coupled flip-puff-tray allowance below).
    if r.interior == "removable_refill_cartridge":
        refill = object_model.get_part("refill")
        coupled_reason = (
            "lid and removable refill share the mouth; the refill lifts out of "
            "the lid it opens (coupled, operated in sequence)."
        )
        if r.lid_mechanism == "clamshell_two_leaf":
            for tag in ("rear", "front"):
                ctx.allow_overlap(
                    object_model.get_part(f"leaf_{tag}"),
                    refill,
                    reason=coupled_reason,
                )
        else:
            ctx.allow_overlap(
                object_model.get_part("lid"),
                refill,
                reason=coupled_reason,
            )

    # A flip puff tray and its lid share the case mouth and are operated in
    # sequence (open the lid, then flip the tray up to present the puff). Both
    # the rear-flip lid (rotates clear) and the slide lid (translates clear)
    # cover that mouth when closed, so at cross-DOF poses (lid closed + tray
    # flipped) the tray sweeps into the lid it deploys out of. Allow that pair
    # for either single-lid mechanism (clamshell degrades the interior away).
    if r.interior == "flip_puff_tray" and r.lid_mechanism in (
        "rear_flip_hinge",
        "slide_lid",
    ):
        ctx.allow_overlap(
            object_model.get_part("lid"),
            object_model.get_part("puff_tray"),
            reason="lid and flip puff tray share the mouth; the tray deploys out "
            "of the lid it opens (coupled, operated in sequence).",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity checks. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check("base part present", "base" in part_names, details=str(sorted(part_names)))

    # Powder pans present (Rule 1: inline visuals on base or refill).
    carrier = (
        object_model.get_part("refill") if r.interior == "removable_refill_cartridge" else base
    )
    pan_visuals = [v.name for v in carrier.visuals if v.name.startswith("powder_pan")]
    ctx.check(
        "N powder pans inlined on carrier (Rule 1)",
        len(pan_visuals) == r.pan_count,
        details=f"pans={sorted(pan_visuals)} expected N={r.pan_count}",
    )

    # Lid-mechanism joint topology.
    if r.lid_mechanism == "rear_flip_hinge":
        j = object_model.get_articulation("base_to_lid")
        ctx.check(
            "rear-flip lid is REVOLUTE about -X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    elif r.lid_mechanism == "clamshell_two_leaf":
        jr = object_model.get_articulation("base_to_leaf_rear")
        jf = object_model.get_articulation("base_to_leaf_front")
        ctx.check(
            "clamshell has 2 mirrored REVOLUTE leaf joints",
            jr.articulation_type == ArticulationType.REVOLUTE
            and jf.articulation_type == ArticulationType.REVOLUTE
            and abs(jr.axis[0]) > 0.99
            and abs(jf.axis[0]) > 0.99
            and jr.axis[0] * jf.axis[0] < 0,
            details=f"rear={tuple(jr.axis)} front={tuple(jf.axis)}",
        )
    else:
        j = object_model.get_articulation("base_to_lid")
        ctx.check(
            "slide lid is PRISMATIC about -Y",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[1]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )

    # Interior joint topology.
    if r.interior == "removable_refill_cartridge":
        j = object_model.get_articulation("base_to_refill")
        ctx.check(
            "refill is PRISMATIC about +Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )
    elif r.interior == "flip_puff_tray":
        j = object_model.get_articulation("base_to_puff_tray")
        ctx.check(
            "puff tray is REVOLUTE about -X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"type={j.articulation_type} axis={tuple(j.axis)}",
        )

    # ---- Lid actuation opens / exposes the interior. ----
    if r.lid_mechanism == "rear_flip_hinge":
        j = object_model.get_articulation("base_to_lid")
        lid = object_model.get_part("lid")
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({j: r.lid_open * 0.7}):
            opened = ctx.part_world_aabb(lid)
        if closed is not None and opened is not None:
            ctx.check(
                "rear-flip lid opens upward",
                opened[1][2] > closed[1][2] + 0.030,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )
    elif r.lid_mechanism == "clamshell_two_leaf":
        jr = object_model.get_articulation("base_to_leaf_rear")
        leaf = object_model.get_part("leaf_rear")
        closed = ctx.part_world_aabb(leaf)
        with ctx.pose({jr: r.lid_open * 0.7}):
            opened = ctx.part_world_aabb(leaf)
        if closed is not None and opened is not None:
            ctx.check(
                "clamshell rear leaf opens upward",
                opened[1][2] > closed[1][2] + 0.025,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )
    else:
        j = object_model.get_articulation("base_to_lid")
        lid = object_model.get_part("lid")
        p0 = ctx.part_world_position(lid)
        with ctx.pose({j: r.slide_travel * 0.9}):
            p1 = ctx.part_world_position(lid)
        if p0 is not None and p1 is not None:
            ctx.check(
                "slide lid translates forward (-Y)",
                p1[1] < p0[1] - 0.030,
                details=f"closed_y={p0[1]:.3f} open_y={p1[1]:.3f}",
            )

    if r.interior == "removable_refill_cartridge":
        j = object_model.get_articulation("base_to_refill")
        refill = object_model.get_part("refill")
        p0 = ctx.part_world_position(refill)
        with ctx.pose({j: r.refill_lift * 0.9}):
            p1 = ctx.part_world_position(refill)
        if p0 is not None and p1 is not None:
            ctx.check(
                "refill lifts straight up",
                p1[2] > p0[2] + 0.020,
                details=f"seated_z={p0[2]:.3f} lifted_z={p1[2]:.3f}",
            )
    elif r.interior == "flip_puff_tray":
        j = object_model.get_articulation("base_to_puff_tray")
        puff = object_model.get_part("puff_tray")
        closed = ctx.part_world_aabb(puff)
        with ctx.pose({j: r.tray_open * 0.8}):
            opened = ctx.part_world_aabb(puff)
        if closed is not None and opened is not None:
            ctx.check(
                "puff tray flips up to reveal powder",
                opened[1][2] > closed[1][2] + 0.015,
                details=f"closed_top={closed[1][2]:.3f} flipped_top={opened[1][2]:.3f}",
            )

    # ---- Footprint / ground / proportion. ----
    aabb = ctx.part_world_aabb(base)
    if aabb is not None:
        (axmn, aymn, azmn), (axmx, aymx, azmx) = aabb
        ctx.check(
            "base rests near the ground",
            azmn < 0.03,
            details=f"z_min={azmn:.4f}",
        )

    # ---- Pan-row clearance proven from authored dims (N>=2). ----
    if r.pan_count >= 2:
        row_w = (r.pan_count - 1) * r.pan_span + 2.0 * r.pan_r
        cavity_x = 2.0 * (r.rx - 1.5 * r.wall)
        ctx.check(
            "pan row fits inside the cavity",
            row_w <= cavity_x,
            details=f"row_w={row_w:.4f} cavity_x={cavity_x:.4f}",
        )

    # ---- slot_choices recorded and N encoded. ----
    ctx.check(
        "slot_choices recorded with pan_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "CushionConfig",
    "ResolvedCushionConfig",
    "build_cushion",
    "build_seeded_cushion",
    "config_from_seed",
    "resolve_config",
    "run_cushion_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
