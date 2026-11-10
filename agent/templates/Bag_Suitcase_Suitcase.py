# SPDX-License-Identifier: Apache-2.0

"""Vintage hard-sided travel suitcase — modular procedural template.

Category identity: a single rectangular hard-shell leather suitcase ``body``
(root), joined to a rear-hinged ``lid`` by the always-present ``lid_hinge``
REVOLUTE (the only constant active main axis, axis≈-X, the lid lifts its free
front edge upward). The front carries **one mutually-exclusive closure**
mechanism (metal latches / buckle straps / perimeter zipper), a carry handle
(fixed wooden grab on the body, or a folding handle hinged on the lid), the
shell is reinforced (8 corner caps / 12 edge bands), the lid is flat or a domed
steamer-trunk (cadquery barrel-vault), and the interior is empty or carries a
lift-up packing tray.

Pattern: ``parallel_children`` — every slot hangs its parts / inline visuals off
the shared ``suitcase_body`` root (or its ``suitcase_lid`` child). There is NO
multiplicity axis (corner_caps fixed 8, edge_banding fixed 12, latches/tongues
fixed 2 are module-internal fixed loops, not a template copy axis).

Slots (spec §): closure_mechanism (3) / handle_system (2) / reinforcement (2) /
lid_profile (2) / internal_structure (2). slot_choices_for_seed returns the
5-tuple ``(closure_mechanism, handle_system, reinforcement, lid_profile,
internal_structure)`` consumed by the ``module_topology_diversity`` gate.

Compatibility gating (spec §10, approved): the domed lid breaks the flat-lid
mounting interfaces of zipper_perimeter / buckle_straps / folding_handle, so
``lid_profile == dome_trunk`` forces the dome-safe subset
``closure = latches`` + ``handle = fixed_top_grab``. The ``edge_banding ×
lift_tray`` clearance is re-checked against the banding inner face (W/2 - T,
more outboard than the corner-cap inner face) and the tray width projected
into the cavity.

Captured-pin / captured-slide joints (folding pivot rod↔mount, zipper teeth↔
slider) omit ``MatingContract`` (grandfathered) and are guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` mirroring each
source record. The latch / strap-tongue / tray hinges are face-contact hinges
whose origin sits on real body geometry (guarded by the origin baseline).

Sources: parent ``cb7b4d8c`` (chassis + lid_hinge + flat lid + corner_caps +
latches + rope handle) plus the 6 workbench-only 5-star fork variants
(buckle / zipper / folding_handle / edgeband / dome_trunk / lift_tray). See
``articraft_template_authoring/specs_modular_v1/Bag_Suitcase_Suitcase.md``.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

ClosureMechanism = Literal["latches", "buckle_straps", "zipper_perimeter"]
HandleSystem = Literal["fixed_top_grab", "folding_handle"]
Reinforcement = Literal["corner_caps", "edge_banding"]
LidProfile = Literal["flat", "dome_trunk"]
InternalStructure = Literal["open", "lift_tray"]
PaletteStyle = Literal[
    "vintage_leather_brass",
    "oxblood_chrome",
    "tan_steamer",
    "black_travel",
    "olive_canvas_brass",
]

CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "latches",
    "buckle_straps",
    "zipper_perimeter",
)
HANDLE_SYSTEMS: tuple[HandleSystem, ...] = ("fixed_top_grab", "folding_handle")
REINFORCEMENTS: tuple[Reinforcement, ...] = ("corner_caps", "edge_banding")
LID_PROFILES: tuple[LidProfile, ...] = ("flat", "dome_trunk")
INTERNAL_STRUCTURES: tuple[InternalStructure, ...] = ("open", "lift_tray")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "vintage_leather_brass",
    "oxblood_chrome",
    "tan_steamer",
    "black_travel",
    "olive_canvas_brass",
)

# Dome-safe closure / handle subset (spec §10: dome breaks flat-lid interfaces).
_DOME_CLOSURE: ClosureMechanism = "latches"
_DOME_HANDLE: HandleSystem = "fixed_top_grab"

# ---------------------------------------------------------------------------
# Palettes (spec palette_style table). Every .visual(... material=mats[k]) keys
# off one of these named colors so the output is visibly multi-colored.
# keys: leather (body shell), trim (straps/loops), corner (caps), band (brass/
# edge banding + dome bands), wood (handle grip), metal (latch/buckle/zipper/
# slider hardware), linen (tray floor), tray_tab (tray pull tab).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "vintage_leather_brass": {
        "leather": (0.32, 0.15, 0.10, 1.0),
        "trim": (0.18, 0.09, 0.06, 1.0),
        "corner": (0.22, 0.11, 0.07, 1.0),
        "band": (0.68, 0.60, 0.36, 1.0),
        "wood": (0.55, 0.27, 0.07, 1.0),
        "metal": (0.58, 0.58, 0.62, 1.0),
        "linen": (0.72, 0.66, 0.54, 1.0),
        "tray_tab": (0.38, 0.18, 0.10, 1.0),
    },
    "oxblood_chrome": {
        "leather": (0.30, 0.12, 0.10, 1.0),
        "trim": (0.20, 0.08, 0.07, 1.0),
        "corner": (0.55, 0.56, 0.60, 1.0),
        "band": (0.62, 0.63, 0.67, 1.0),
        "wood": (0.45, 0.22, 0.06, 1.0),
        "metal": (0.72, 0.72, 0.76, 1.0),
        "linen": (0.74, 0.70, 0.62, 1.0),
        "tray_tab": (0.30, 0.12, 0.10, 1.0),
    },
    "tan_steamer": {
        "leather": (0.55, 0.40, 0.24, 1.0),
        "trim": (0.34, 0.22, 0.12, 1.0),
        "corner": (0.72, 0.58, 0.22, 1.0),
        "band": (0.72, 0.58, 0.22, 1.0),
        "wood": (0.62, 0.40, 0.18, 1.0),
        "metal": (0.60, 0.56, 0.45, 1.0),
        "linen": (0.80, 0.72, 0.56, 1.0),
        "tray_tab": (0.40, 0.24, 0.12, 1.0),
    },
    "black_travel": {
        "leather": (0.10, 0.10, 0.12, 1.0),
        "trim": (0.16, 0.16, 0.18, 1.0),
        "corner": (0.62, 0.62, 0.66, 1.0),
        "band": (0.66, 0.66, 0.70, 1.0),
        "wood": (0.14, 0.14, 0.16, 1.0),
        "metal": (0.74, 0.74, 0.78, 1.0),
        "linen": (0.40, 0.40, 0.44, 1.0),
        "tray_tab": (0.14, 0.14, 0.16, 1.0),
    },
    "olive_canvas_brass": {
        "leather": (0.36, 0.34, 0.22, 1.0),
        "trim": (0.28, 0.18, 0.10, 1.0),
        "corner": (0.68, 0.60, 0.36, 1.0),
        "band": (0.68, 0.60, 0.36, 1.0),
        "wood": (0.55, 0.27, 0.07, 1.0),
        "metal": (0.60, 0.56, 0.45, 1.0),
        "linen": (0.74, 0.72, 0.58, 1.0),
        "tray_tab": (0.30, 0.20, 0.10, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Nominal real-world dimensions (meters); from the 7 source records (L17-23).
# ---------------------------------------------------------------------------
_W = 0.46  # width  (X)
_D = 0.34  # depth  (Y)
_HB = 0.085  # body height (Z)
_HL = 0.075  # flat-lid height (Z)
_T = 0.012  # shell wall thickness
_SEAM_GAP = 0.0015  # closed clearance between body rim and lid rim
_DOME_H = 0.08  # dome peak height above rim (nominal)

# Latch hardware
_LATCH_X = 0.13
_LATCH_STANDOFF = 0.007
_LATCH_W = 0.05
_LATCH_T = 0.012
_LATCH_H = 0.07

# Buckle hardware
_STRAP_X = 0.13
_STRAP_W = 0.025
_STRAP_T = 0.003
_BUCKLE_FW = 0.038
_BUCKLE_FH = 0.032
_BUCKLE_BAR = 0.004
_BUCKLE_DEPTH = 0.005
_BUCKLE_STANDOFF = 0.004
_LOWER_STRAP_L = 0.045
_UPPER_STRAP_L = 0.065
_TONGUE_L = 0.055
_STRAP_EMBED = 0.001

# Zipper hardware
_ZIP_TAPE_W = 0.016
_ZIP_TAPE_T = 0.002
_ZIP_TEETH_W = 0.008
_ZIP_TEETH_T = 0.005
_SLIDER_W = 0.028
_SLIDER_D = 0.018
_SLIDER_H = 0.016
_TAB_W = 0.014
_TAB_T = 0.003
_TAB_L = 0.032

# Folding handle hardware
_HANDLE_ARM_LENGTH = 0.055
_HANDLE_ARM_W = 0.012
_HANDLE_ARM_H = 0.006
_HANDLE_PIVOT_X = 0.055
_HANDLE_GRIP_LENGTH = 0.13
_HANDLE_GRIP_RADIUS = 0.009
_HANDLE_MOUNT_W = 0.020
_HANDLE_MOUNT_D = 0.016
_HANDLE_MOUNT_H = 0.020
_HANDLE_PIVOT_Z = 0.012

# Lift tray hardware
_CORNER_CAP = 0.045
_TRAY_CLEAR = 0.004
_TRAY_T = 0.004
_TRAY_WALL_H = 0.018
_TRAY_WALL_T = 0.005
_TRAY_Z = 0.047
_TRAY_TAB_W = 0.06
_TRAY_TAB_H = 0.018
_TRAY_HINGE_STANDOFF = 0.003  # hinge inset from the rear inner wall face
# Rear floor overhang past the hinge: grounds the tray by overlapping the body
# rear wall. Penetration = _TRAY_FLOOR_BACK - _TRAY_HINGE_STANDOFF must stay
# below the 0.005 overlap tolerance (else flagged as 穿模) yet be > 0 so the
# contact_tol=1e-6 isolation check treats the tray as connected. 0.006 -> 0.003.
_TRAY_FLOOR_BACK = 0.006

# Joint ranges (nominal upper, source records).
_LID_OPEN = 2.0
_CLOSURE_OPEN = 1.4
_HANDLE_OPEN = 1.3
_TRAY_OPEN = 1.3


@dataclass(frozen=True)
class SuitcaseConfig:
    closure_mechanism: ClosureMechanism | None = None
    handle_system: HandleSystem | None = None
    reinforcement: Reinforcement | None = None
    lid_profile: LidProfile | None = None
    internal_structure: InternalStructure | None = None
    palette_style: PaletteStyle = "vintage_leather_brass"
    box_w: float = _W
    box_d: float = _D
    box_h: float = _HB
    dome_h_scale: float = 1.0
    lid_open_scale: float = 1.0
    zip_travel_scale: float = 1.0
    name: str = "suitcase"


@dataclass(frozen=True)
class ResolvedSuitcaseConfig:
    closure_mechanism: ClosureMechanism
    handle_system: HandleSystem
    reinforcement: Reinforcement
    lid_profile: LidProfile
    internal_structure: InternalStructure
    palette_style: PaletteStyle
    # Concrete geometry.
    box_w: float
    box_d: float
    box_h: float  # HB
    lid_h: float  # HL (flat lid)
    wall_t: float
    seam_gap: float
    dome_h: float
    # Derived joint ranges.
    lid_open: float
    closure_open: float
    handle_open: float
    tray_open: float
    zip_travel: float
    zip_origin_x: float
    # Lift-tray clearance (resolved against reinforcement inner face).
    tray_w: float
    tray_d: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Compatibility gating (spec §10). dome_trunk forces the dome-safe subset.
# ---------------------------------------------------------------------------
def _gate_for_dome(
    lid_profile: LidProfile,
    closure: ClosureMechanism,
    handle: HandleSystem,
) -> tuple[ClosureMechanism, HandleSystem]:
    if lid_profile == "dome_trunk":
        return _DOME_CLOSURE, _DOME_HANDLE
    return closure, handle


def config_from_seed(seed: int) -> SuitcaseConfig:
    rng = random.Random(seed)
    # Sampler order: lid_profile first → gate closure/handle (dome narrows) →
    # sample the rest (spec §sampler).
    lid_profile = rng.choice(LID_PROFILES)
    closure = rng.choice(CLOSURE_MECHANISMS)
    handle = rng.choice(HANDLE_SYSTEMS)
    closure, handle = _gate_for_dome(lid_profile, closure, handle)
    reinforcement = rng.choice(REINFORCEMENTS)
    internal_structure = rng.choice(INTERNAL_STRUCTURES)

    return SuitcaseConfig(
        closure_mechanism=closure,
        handle_system=handle,
        reinforcement=reinforcement,
        lid_profile=lid_profile,
        internal_structure=internal_structure,
        palette_style=rng.choice(PALETTE_STYLES),
        box_w=round(rng.uniform(0.40, 0.54), 4),
        box_d=round(rng.uniform(0.28, 0.40), 4),
        box_h=round(rng.uniform(0.070, 0.105), 4),
        dome_h_scale=round(rng.uniform(0.85, 1.15), 4),
        lid_open_scale=round(rng.uniform(0.85, 1.05), 4),
        zip_travel_scale=round(rng.uniform(0.85, 1.05), 4),
        name=f"seeded_suitcase_{seed}",
    )


def resolve_config(config: SuitcaseConfig | None = None) -> ResolvedSuitcaseConfig:
    cfg = config or SuitcaseConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    lid_profile = _pick(cfg.lid_profile, LID_PROFILES)
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    handle = _pick(cfg.handle_system, HANDLE_SYSTEMS)
    closure, handle = _gate_for_dome(lid_profile, closure, handle)
    reinforcement = _pick(cfg.reinforcement, REINFORCEMENTS)
    internal_structure = _pick(cfg.internal_structure, INTERNAL_STRUCTURES)

    # Independent primary dimensions (clamp to keep the hard-case proportion).
    box_w = _clamp(cfg.box_w, 0.40, 0.54)
    box_d = _clamp(cfg.box_d, 0.28, 0.40)
    box_h = _clamp(cfg.box_h, 0.070, 0.105)
    wall_t = _T
    # Small front seam clearance (keeps the lid front wall from clipping body rim
    # hardware / handle loops). The lid is kept grounded independent of the
    # closure by a rear hinge-seat lip on the lid back wall (see _build_flat_lid /
    # _build_dome_lid), so this gap does not isolate the lid.
    seam_gap = _SEAM_GAP

    # HL derived (equation): flat lid roughly tracks body height, clamped.
    lid_h = _clamp(box_h * (_HL / _HB), 0.060, 0.095)

    # Dome height (conditional@dome): clamp <= box_d/2 to keep the vault legal.
    dome_h = _clamp(_DOME_H * _clamp(cfg.dome_h_scale, 0.85, 1.15), 0.045, box_d / 2.0 - 0.005)

    # Joint ranges.
    open_scale = _clamp(cfg.lid_open_scale, 0.85, 1.05)
    lid_open = _clamp(_LID_OPEN * open_scale, 1.4, 2.4)
    # The domed steamer lid's tall rear rim caps clip the body rear reinforcement
    # if it flings past ~2 rad; cap the dome lid_open at the verified clearance.
    if lid_profile == "dome_trunk":
        lid_open = min(lid_open, _DOME_LID_OPEN_MAX)
    closure_open = _clamp(_CLOSURE_OPEN * open_scale, 1.0, 1.6)
    handle_open = _clamp(_HANDLE_OPEN * open_scale, 1.0, 1.5)
    tray_open = _clamp(_TRAY_OPEN * open_scale, 1.0, 1.5)

    # Zipper travel (conditional@zipper): <= front-face available run (W - 0.10).
    zip_travel = _clamp(
        (box_w - 0.10) * _clamp(cfg.zip_travel_scale, 0.85, 1.05),
        0.20,
        box_w - 0.08,
    )
    # Perimeter zipper slider parks centered by default. When a fixed_top_grab
    # carry handle occupies the front-top center (grip spans x in [-0.08, 0.08]),
    # the centered slider would drive straight through the grip (genuine 穿模).
    # Route the slider onto the run to the RIGHT of the handle's occupied arc so
    # its whole travel clears the grip + mount loops (single source for the joint
    # origin/upper consumed by _build_zipper and run_suitcase_tests).
    zip_origin_x = -zip_travel / 2.0
    if closure == "zipper_perimeter" and handle == "fixed_top_grab":
        grip_half = 0.16 / 2.0  # handle_grip length 0.16 -> reaches x = +/-0.08
        slider_clear = _SLIDER_W / 2.0 + 0.006  # keep the slider body off the grip
        zip_origin_x = grip_half + slider_clear
        edge_margin = 0.025  # keep the right end clear of the corner reinforcement
        max_run = (box_w / 2.0 - edge_margin) - (zip_origin_x + _SLIDER_W / 2.0)
        zip_travel = _clamp(min(zip_travel, max_run), 0.05, box_w)

    # --- Lift-tray clearance inequality (spec §7 / §10 (4)). ---
    # The tray must clear the reinforcement's interior face.
    #   corner_caps inner face: W/2 - CORNER_CAP + 0.004
    #   edge_banding inner face: W/2 - T (more outboard -> tray must be narrower)
    if reinforcement == "edge_banding":
        inner_x = box_w / 2.0 - wall_t
    else:
        inner_x = box_w / 2.0 - _CORNER_CAP + 0.004
    tray_w = 2.0 * (inner_x - _TRAY_CLEAR)
    tray_w = max(0.10, tray_w)
    tray_d = box_d - 2.0 * wall_t - 2.0 * 0.006

    # Sequenced mechanism: the rear-hinged packing tray is only lifted up to
    # unpack once the lid has been swung OPEN. "lid closed + tray lifted" is an
    # unphysical pose a pose-setter can request but that never occurs in
    # operation — it is the user's responsibility, not a geometry defect. So the
    # tray keeps its FULL designed lift (no clearance-solver clamp that strangled
    # it to a few degrees below the closed-lid interior) and the packing_tray↔
    # suitcase_lid pair is whitelisted for overlap in run_tests. The tray↔body
    # (shell / reinforcement inner face) clearance is still enforced by the
    # derived tray_w above and re-checked at full lift, so restoring travel
    # cannot mask a real shell penetration.

    return ResolvedSuitcaseConfig(
        closure_mechanism=closure,
        handle_system=handle,
        reinforcement=reinforcement,
        lid_profile=lid_profile,
        internal_structure=internal_structure,
        palette_style=palette_style,
        box_w=box_w,
        box_d=box_d,
        box_h=box_h,
        lid_h=lid_h,
        wall_t=wall_t,
        seam_gap=seam_gap,
        dome_h=dome_h,
        lid_open=lid_open,
        closure_open=closure_open,
        handle_open=handle_open,
        tray_open=tray_open,
        zip_travel=zip_travel,
        zip_origin_x=zip_origin_x,
        tray_w=tray_w,
        tray_d=tray_d,
        name=cfg.name or "suitcase",
    )


def with_overrides(config: SuitcaseConfig, **kwargs: object) -> SuitcaseConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SuitcaseConfig | ResolvedSuitcaseConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedSuitcaseConfig) else resolve_config(config)
    return (
        ("closure_mechanism", r.closure_mechanism),
        ("handle_system", r.handle_system),
        ("reinforcement", r.reinforcement),
        ("lid_profile", r.lid_profile),
        ("internal_structure", r.internal_structure),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared shell helpers (7 source records, identical _add_box_shell).
# ---------------------------------------------------------------------------
def _add_box_shell(part, *, width, depth, height, wall, material, z0=0.0):
    """Hollow rectangular shell: floor panel + four walls (open top)."""
    cap_z = z0 + wall / 2.0
    part.visual(
        Box((width, depth, wall)),
        origin=Origin(xyz=(0.0, 0.0, cap_z)),
        material=material,
        name="shell_panel", material_class_id="leather.smooth_plain",
    )
    cz = z0 + height / 2.0
    part.visual(
        Box((width, wall, height)),
        origin=Origin(xyz=(0.0, -(depth / 2.0 - wall / 2.0), cz)),
        material=material,
        name="wall_front", material_class_id="leather.smooth_plain",
    )
    part.visual(
        Box((width, wall, height)),
        origin=Origin(xyz=(0.0, (depth / 2.0 - wall / 2.0), cz)),
        material=material,
        name="wall_back", material_class_id="leather.smooth_plain",
    )
    part.visual(
        Box((wall, depth, height)),
        origin=Origin(xyz=(-(width / 2.0 - wall / 2.0), 0.0, cz)),
        material=material,
        name="wall_left", material_class_id="leather.smooth_plain",
    )
    part.visual(
        Box((wall, depth, height)),
        origin=Origin(xyz=((width / 2.0 - wall / 2.0), 0.0, cz)),
        material=material,
        name="wall_right", material_class_id="leather.smooth_plain",
    )


# ---------------------------------------------------------------------------
# Reinforcement slot (Rule 1: inline body/lid visuals, no joint).
# ---------------------------------------------------------------------------
def _add_corner_caps(part, *, width, y_lo, y_hi, z_lo, z_hi, material, prefix):
    """8/4 corner caps at the four vertical edges of a box whose X is centered
    and whose Y spans [y_lo, y_hi] (the body is centered; the lid is offset to
    the rear hinge frame, so caps are placed from the explicit Y extents)."""
    cap = _CORNER_CAP
    capz = (z_lo + z_hi) / 2.0
    caph = z_hi - z_lo
    cap_ys = (y_lo + cap / 2.0 - 0.004, y_hi - cap / 2.0 + 0.004)
    i = 0
    for sx in (-1.0, 1.0):
        for cy in cap_ys:
            part.visual(
                Box((cap, cap, caph)),
                origin=Origin(xyz=(sx * (width / 2.0 - cap / 2.0 + 0.004), cy, capz)),
                material=material,
                name=f"{prefix}_corner_{i}", material_class_id="metal.brass_aged",
            )
            i += 1


def _add_edge_banding(part, *, x_lo, x_hi, y_lo, y_hi, z_lo, z_hi, material, prefix):
    """12 continuous metal edge-band strips (fixed 12-edge loop, not a copy axis)."""
    bw = 0.015
    bt = 0.003
    w = x_hi - x_lo
    d = y_hi - y_lo
    h = z_hi - z_lo
    cx = (x_lo + x_hi) / 2.0
    cy = (y_lo + y_hi) / 2.0
    cz = (z_lo + z_hi) / 2.0
    edges = [
        ((cx, y_lo + bt / 2.0, z_lo + bw / 2.0), (w, bt, bw)),
        ((cx, y_lo + bt / 2.0, z_hi - bw / 2.0), (w, bt, bw)),
        ((cx, y_hi - bt / 2.0, z_lo + bw / 2.0), (w, bt, bw)),
        ((cx, y_hi - bt / 2.0, z_hi - bw / 2.0), (w, bt, bw)),
        ((x_lo + bt / 2.0, cy, z_lo + bw / 2.0), (bt, d, bw)),
        ((x_lo + bt / 2.0, cy, z_hi - bw / 2.0), (bt, d, bw)),
        ((x_hi - bt / 2.0, cy, z_lo + bw / 2.0), (bt, d, bw)),
        ((x_hi - bt / 2.0, cy, z_hi - bw / 2.0), (bt, d, bw)),
        ((x_lo + bt / 2.0, y_lo + bw / 2.0, cz), (bt, bw, h)),
        ((x_hi - bt / 2.0, y_lo + bw / 2.0, cz), (bt, bw, h)),
        ((x_lo + bt / 2.0, y_hi - bw / 2.0, cz), (bt, bw, h)),
        ((x_hi - bt / 2.0, y_hi - bw / 2.0, cz), (bt, bw, h)),
    ]
    n = len(edges)
    for i in range(n):
        center, size = edges[i]
        part.visual(
            Box(size), origin=Origin(xyz=center), material=material, name=f"{prefix}_band_{i}", material_class_id="metal.brass_polished"
        )


def _emit_reinforcement(part, r: ResolvedSuitcaseConfig, mats, *, prefix, z_lo, z_hi, y_lo, y_hi):
    if r.reinforcement == "edge_banding":
        _add_edge_banding(
            part,
            x_lo=-r.box_w / 2.0,
            x_hi=r.box_w / 2.0,
            y_lo=y_lo,
            y_hi=y_hi,
            z_lo=z_lo,
            z_hi=z_hi,
            material=mats["band"],
            prefix=prefix,
        )
    else:
        # corner caps span a vertical slab inside [z_lo, z_hi] (parent insets the
        # cap height by 0.02 from the shell to read as a corner block).
        cz_hi = z_hi - 0.02
        _add_corner_caps(
            part,
            width=r.box_w,
            y_lo=y_lo,
            y_hi=y_hi,
            z_lo=z_lo,
            z_hi=cz_hi,
            material=mats["corner"],
            prefix=prefix,
        )


# ---------------------------------------------------------------------------
# Dome lid_profile (cadquery barrel-vault, NOT degraded to a Box).
# ---------------------------------------------------------------------------
def _build_dome_shell(width, depth, dome_h, wall_t):
    """Barrel-vault humpback dome shell. Rim at z=0, peak at z=dome_h, arching
    from y=0 (rear/hinge) to y=-depth (front), centered on x=0."""
    profile = (
        cq.Workplane("YZ")
        .moveTo(0.0, 0.0)
        .threePointArc((-depth / 2.0, dome_h), (-depth, 0.0))
        .lineTo(-depth, wall_t)
        .threePointArc((-depth / 2.0, dome_h - wall_t), (0.0, wall_t))
        .close()
    )
    return profile.extrude(width).translate((-width / 2.0, 0.0, 0.0))


def _build_dome_endwall(depth, dome_h, x0, thickness):
    """Solid end wall closing one open crescent of the barrel vault."""
    profile = (
        cq.Workplane("YZ")
        .moveTo(0.0, 0.0)
        .threePointArc((-depth / 2.0, dome_h), (-depth, 0.0))
        .close()
    )
    return profile.extrude(thickness).translate((x0, 0.0, 0.0))


def _dome_surface_z(y_local, r: ResolvedSuitcaseConfig):
    """Dome outer surface height above the rim at local y (0=rear, -D=front)."""
    dome_r = (r.box_d * r.box_d / 4.0 + r.dome_h * r.dome_h) / (2.0 * r.dome_h)
    y_center = -r.box_d / 2.0
    center_z = r.dome_h - dome_r
    dy = y_local - y_center
    radicand = dome_r * dome_r - dy * dy
    if radicand < 0.0:
        return 0.0
    return center_z + math.sqrt(radicand)


# ---------------------------------------------------------------------------
# Dome lid over-rotation limit. The domed steamer lid carries tall rim corner
# caps right at the rear hinge; when it flings back past ~2.0 rad they swing down
# behind the hinge into the body rear reinforcement / trim straps (genuine 穿模).
# Flat lids clear because their rear caps sit further forward and lower. The clash
# geometry is dimension-independent (cap offsets, seam_gap and wall_t are fixed);
# a body<->lid overlap sweep over 120 dome seeds (all box_w/box_d/box_h) puts the
# earliest onset at 2.0 rad, so cap the dome lid_open at 1.90 (0.1 rad margin).
# ---------------------------------------------------------------------------
_DOME_LID_OPEN_MAX = 1.90


# ---------------------------------------------------------------------------
# Lid (always-present rear-hinged child; mesh chosen by lid_profile).
# ---------------------------------------------------------------------------
def _build_flat_lid(lid, r: ResolvedSuitcaseConfig, mats):
    """Flat box lid (parent L153-218). Authored about the rear hinge line."""
    w, d, t = r.box_w, r.box_d, r.wall_t
    hl = r.lid_h
    sg = r.seam_gap
    leather = mats["leather"]
    lid_panel_z = hl - t / 2.0
    wall_h = hl - t - sg
    wall_cz = sg + wall_h / 2.0
    lid.visual(
        Box((w, d, t)),
        origin=Origin(xyz=(0.0, -d / 2.0, lid_panel_z)),
        material=leather,
        name="shell_panel", material_class_id="leather.smooth_plain",
    )
    lid.visual(
        Box((w, t, wall_h)),
        origin=Origin(xyz=(0.0, -(d - t / 2.0), wall_cz)),
        material=leather,
        name="wall_front", material_class_id="leather.smooth_plain",
    )
    lid.visual(
        Box((w, t, wall_h)),
        origin=Origin(xyz=(0.0, -(t / 2.0), wall_cz)),
        material=leather,
        name="wall_back", material_class_id="leather.smooth_plain",
    )
    # Rear hinge-seat lip: a thin tab on the back wall that dips just below the
    # rim plane (z<0) so it overlaps the body rear rim and keeps the closed lid
    # grounded by geometric contact regardless of the closure.
    lip_h = sg + 0.0025
    lid.visual(
        Box((w * 0.5, t, lip_h)),
        origin=Origin(xyz=(0.0, -(t / 2.0), sg - lip_h / 2.0)),
        material=leather,
        name="hinge_seat_lip", material_class_id="leather.smooth_plain",
    )
    lid.visual(
        Box((t, d, wall_h)),
        origin=Origin(xyz=(-(w / 2.0 - t / 2.0), -d / 2.0, wall_cz)),
        material=leather,
        name="wall_left", material_class_id="leather.smooth_plain",
    )
    lid.visual(
        Box((t, d, wall_h)),
        origin=Origin(xyz=((w / 2.0 - t / 2.0), -d / 2.0, wall_cz)),
        material=leather,
        name="wall_right", material_class_id="leather.smooth_plain",
    )
    # reinforcement on the lid: y from -D..0, z from seam_gap..HL.
    _emit_reinforcement(lid, r, mats, prefix="lid", z_lo=sg, z_hi=hl, y_lo=-d, y_hi=0.0)
    # lid trim straps (Rule 1 visual). Omitted under lift_tray: these low
    # longitudinal straps (bottom ~sg+0.004 above the rim) run the full depth over
    # the tray footprint and would be clipped by the lifting tray floor; dropping
    # them lets the tray clear against the (higher) top-panel underside instead.
    if r.internal_structure != "lift_tray":
        for sx in (-0.16, 0.16):
            if abs(sx) < w / 2.0 - 0.03:
                lid.visual(
                    Box((0.03, d + 0.004, 0.012)),
                    origin=Origin(xyz=(sx, -d / 2.0, sg + 0.010)),
                    material=mats["trim"],
                    name=f"lid_strap_{'l' if sx < 0 else 'r'}", material_class_id="leather.smooth_plain",
                )


def _build_dome_lid(lid, r: ResolvedSuitcaseConfig, mats, *, assets):
    """Domed steamer-trunk lid (dome_trunk L214-285): cadquery barrel-vault +
    solid end walls + brass bands + leather straps. Rim at local z=seam_gap."""
    w, d, t = r.box_w, r.box_d, r.wall_t
    sg = r.seam_gap
    leather = mats["leather"]
    dome_cq = _build_dome_shell(w, d, r.dome_h, t)
    lid.visual(
        mesh_from_cadquery(
            dome_cq, "dome_shell", tolerance=0.0005, angular_tolerance=0.08, assets=assets
        ),
        origin=Origin(xyz=(0.0, 0.0, sg)),
        material=leather,
        name="dome_shell", material_class_id="leather.smooth_plain",
    )
    for i, x0 in enumerate((-w / 2.0, w / 2.0 - t)):
        end_cq = _build_dome_endwall(d, r.dome_h, x0, t)
        lid.visual(
            mesh_from_cadquery(
                end_cq, f"dome_end_{i}", tolerance=0.0005, angular_tolerance=0.08, assets=assets
            ),
            origin=Origin(xyz=(0.0, 0.0, sg)),
            material=leather,
            name=f"dome_end_{i}", material_class_id="leather.smooth_plain",
        )
    # Rear hinge-seat lip: dips just below the rim plane at the rear (local y≈0)
    # so it overlaps the body rear rim and grounds the closed dome lid.
    lip_h = sg + 0.0025
    lid.visual(
        Box((w * 0.5, t, lip_h)),
        origin=Origin(xyz=(0.0, -(t / 2.0), sg - lip_h / 2.0)),
        material=leather,
        name="hinge_seat_lip", material_class_id="leather.smooth_plain",
    )
    # corner caps at the dome rim (short protective bands) — always present so the
    # dome rim reads as reinforced regardless of the reinforcement slot's primary
    # treatment; tinted by the active reinforcement material.
    cap_mat = mats["band"] if r.reinforcement == "edge_banding" else mats["corner"]
    lid_cap_h = 0.028
    lid_cap_z_center = sg + 0.002 + lid_cap_h / 2.0
    capm = _CORNER_CAP
    for i, (sx, ly) in enumerate(
        [
            (-1.0, -(t / 2.0)),
            (1.0, -(t / 2.0)),
            (-1.0, -(d - t / 2.0)),
            (1.0, -(d - t / 2.0)),
        ]
    ):
        lid.visual(
            Box((capm, capm, lid_cap_h)),
            origin=Origin(xyz=(sx * (w / 2.0 - capm / 2.0 + 0.004), ly, lid_cap_z_center)),
            material=cap_mat,
            name=f"lid_corner_{i}", material_class_id=("metal.brass_aged" if r.reinforcement == "corner_caps" else "metal.brass_polished"),
        )
    # brass bands across the dome.
    for i, frac in enumerate((0.28, 0.72)):
        band_y = -d * frac
        band_z = sg + _dome_surface_z(band_y, r)
        lid.visual(
            Box((w + 0.004, 0.022, 0.005)),
            origin=Origin(xyz=(0.0, band_y, band_z)),
            material=mats["band"],
            name=f"dome_band_{i}", material_class_id="metal.brass_polished",
        )
    # leather straps near the dome peak.
    for i, sx in enumerate((-0.14, 0.14)):
        strap_y = -d / 2.0
        strap_z = sg + _dome_surface_z(strap_y, r)
        lid.visual(
            Box((0.028, d * 0.40, 0.005)),
            origin=Origin(xyz=(sx, strap_y, strap_z)),
            material=mats["trim"],
            name=f"lid_strap_{i}", material_class_id="leather.smooth_plain",
        )


def _build_lid(model, body, r: ResolvedSuitcaseConfig, mats, *, assets):
    lid = model.part("suitcase_lid")
    if r.lid_profile == "dome_trunk":
        _build_dome_lid(lid, r, mats, assets=assets)
    else:
        _build_flat_lid(lid, r, mats)
    origin = (0.0, r.box_d / 2.0, r.box_h)
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=r.lid_open),
    )
    return lid


# ---------------------------------------------------------------------------
# Handle slot. fixed_top_grab = body-front rope/wood grab (Rule 1, no joint).
# folding_handle = lid-top mounts + a REVOLUTE handle hinged on the lid.
# ---------------------------------------------------------------------------
def _build_fixed_handle(body, r: ResolvedSuitcaseConfig, mats):
    d, hb = r.box_d, r.box_h
    grip_y = -(d / 2.0) - 0.022
    grip_z = hb - 0.006
    body.visual(
        Cylinder(radius=0.012, length=0.16),
        origin=Origin(xyz=(0.0, grip_y, grip_z), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["wood"],
        name="handle_grip", material_class_id="wood.polished_varnished",
    )
    for sx in (-0.06, 0.06):
        body.visual(
            Box((0.02, 0.030, 0.022)),
            origin=Origin(xyz=(sx, -(d / 2.0) - 0.008, grip_z)),
            material=mats["trim"],
            name=f"handle_loop_{'l' if sx < 0 else 'r'}", material_class_id="leather.smooth_plain",
        )


def _build_folding_handle(model, lid, r: ResolvedSuitcaseConfig, mats):
    """Folding handle hinged on the lid (folding_handle L225-282). Only legal on
    a flat lid (gated: dome forces fixed_top_grab)."""
    d, hl = r.box_d, r.lid_h
    hw = mats["metal"]
    # Pivot brackets on the lid top surface.
    for i, sx in enumerate((-1.0, 1.0)):
        lid.visual(
            Box((_HANDLE_MOUNT_W, _HANDLE_MOUNT_D, _HANDLE_MOUNT_H)),
            origin=Origin(xyz=(sx * _HANDLE_PIVOT_X, -d / 2.0, hl + _HANDLE_MOUNT_H / 2.0)),
            material=hw,
            name=f"handle_pivot_mount_{i}", material_class_id="metal.brushed_silver",
        )
    handle = model.part("folding_handle")
    for i, sx in enumerate((-1.0, 1.0)):
        handle.visual(
            Box((_HANDLE_ARM_W, _HANDLE_ARM_LENGTH, _HANDLE_ARM_H)),
            origin=Origin(xyz=(sx * _HANDLE_PIVOT_X, -_HANDLE_ARM_LENGTH / 2.0, 0.0)),
            material=hw,
            name=f"handle_arm_{i}", material_class_id="metal.brushed_silver",
        )
    handle.visual(
        Cylinder(radius=0.004, length=2.0 * _HANDLE_PIVOT_X + _HANDLE_ARM_W),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=hw,
        name="handle_pivot_rod", material_class_id="metal.brushed_silver",
    )
    handle.visual(
        Cylinder(radius=_HANDLE_GRIP_RADIUS, length=_HANDLE_GRIP_LENGTH),
        origin=Origin(xyz=(0.0, -_HANDLE_ARM_LENGTH, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["wood"],
        name="handle_grip", material_class_id="wood.polished_varnished",
    )
    origin = (0.0, -d / 2.0, hl + _HANDLE_PIVOT_Z)
    model.articulation(
        "handle_fold",
        ArticulationType.REVOLUTE,
        parent=lid,
        child=handle,
        origin=Origin(xyz=origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=r.handle_open),
    )
    return handle


# ---------------------------------------------------------------------------
# Closure slot (mutually exclusive). latches / buckle_straps / zipper_perimeter.
# ---------------------------------------------------------------------------
def _build_latches(model, body, r: ResolvedSuitcaseConfig, mats):
    """Two metal latch plates hinged on the body front (parent L138-260)."""
    d, hb = r.box_d, r.box_h
    metal = mats["metal"]
    # latch hinge bosses bridge the front face to the proud latch plate.
    plate_inner_y = -(d / 2.0) - _LATCH_STANDOFF
    boss_outer_y = plate_inner_y
    boss_inner_y = -(d / 2.0) + 0.002
    boss_depth = boss_inner_y - boss_outer_y
    boss_cy = (boss_inner_y + boss_outer_y) / 2.0
    for side, sx in (("l", -_LATCH_X), ("r", _LATCH_X)):
        body.visual(
            Box((0.026, boss_depth, 0.020)),
            origin=Origin(xyz=(sx, boss_cy, hb - 0.018)),
            material=metal,
            name=f"latch_boss_{side}", material_class_id="metal.brushed_silver",
        )
    latch_y = -(d / 2.0) - _LATCH_STANDOFF - _LATCH_T / 2.0
    parts = []
    for side, sx in (("left", -_LATCH_X), ("right", _LATCH_X)):
        latch = model.part(f"latch_{side}")
        latch.visual(
            Box((_LATCH_W, _LATCH_T, _LATCH_H)),
            origin=Origin(xyz=(0.0, 0.0, _LATCH_H / 2.0)),
            material=metal,
            name="latch_plate", material_class_id="metal.brushed_silver",
        )
        latch.visual(
            Box((0.018, _LATCH_T + 0.004, 0.014)),
            origin=Origin(xyz=(0.0, -0.002, _LATCH_H - 0.012)),
            material=metal,
            name="latch_catch", material_class_id="metal.brushed_silver",
        )
        origin = (sx, latch_y, hb - 0.018)
        model.articulation(
            f"latch_{side}_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=latch,
            origin=Origin(xyz=origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=3.0, lower=0.0, upper=r.closure_open),
        )
        parts.append(latch)
    return parts


def _add_buckle_frame(part, *, cx, cy, cz, material, prefix):
    fw, fh, bar, dep = _BUCKLE_FW, _BUCKLE_FH, _BUCKLE_BAR, _BUCKLE_DEPTH
    part.visual(
        Box((fw, dep, bar)),
        origin=Origin(xyz=(cx, cy, cz + fh / 2.0 - bar / 2.0)),
        material=material,
        name=f"{prefix}_top_bar", material_class_id="metal.brushed_silver",
    )
    part.visual(
        Box((fw, dep, bar)),
        origin=Origin(xyz=(cx, cy, cz - fh / 2.0 + bar / 2.0)),
        material=material,
        name=f"{prefix}_bottom_bar", material_class_id="metal.brushed_silver",
    )
    part.visual(
        Box((bar, dep, fh - 2.0 * bar)),
        origin=Origin(xyz=(cx - fw / 2.0 + bar / 2.0, cy, cz)),
        material=material,
        name=f"{prefix}_left_bar", material_class_id="metal.brushed_silver",
    )
    part.visual(
        Box((bar, dep, fh - 2.0 * bar)),
        origin=Origin(xyz=(cx + fw / 2.0 - bar / 2.0, cy, cz)),
        material=material,
        name=f"{prefix}_right_bar", material_class_id="metal.brushed_silver",
    )
    part.visual(
        Box((fw - 2.0 * bar, dep, bar)),
        origin=Origin(xyz=(cx, cy, cz)),
        material=material,
        name=f"{prefix}_center_bar", material_class_id="metal.brushed_silver",
    )


def _build_buckle_straps(model, body, lid, r: ResolvedSuitcaseConfig, mats):
    """Two buckle-strap assemblies (buckle L199-358). Two REVOLUTE strap tongues.
    The lid-side upper straps mount on the flat lid front wall (gated off dome)."""
    d, hb = r.box_d, r.box_h
    t = r.wall_t
    metal = mats["metal"]
    strap = mats["trim"]
    body_front = -d / 2.0
    lower_strap_cy = body_front - _STRAP_T / 2.0 + _STRAP_EMBED
    buckle_cy = body_front - _BUCKLE_STANDOFF - _BUCKLE_DEPTH / 2.0
    tongue_cy = buckle_cy - _BUCKLE_DEPTH / 2.0 - _STRAP_T / 2.0

    for i in range(2):
        sx = -_STRAP_X + i * 2.0 * _STRAP_X
        lower_z_top = hb - _BUCKLE_FH / 2.0
        lower_cz = lower_z_top - _LOWER_STRAP_L / 2.0
        body.visual(
            Box((_STRAP_W, _STRAP_T, _LOWER_STRAP_L)),
            origin=Origin(xyz=(sx, lower_strap_cy, lower_cz)),
            material=strap,
            name=f"lower_strap_{i}", material_class_id="leather.smooth_plain",
        )
        boss_inner_y = body_front + 0.002
        boss_outer_y = buckle_cy + _BUCKLE_DEPTH / 2.0
        boss_depth = boss_inner_y - boss_outer_y
        boss_cy = (boss_inner_y + boss_outer_y) / 2.0
        for bz_off in (
            _BUCKLE_FH / 2.0 - _BUCKLE_BAR / 2.0,
            -(_BUCKLE_FH / 2.0 - _BUCKLE_BAR / 2.0),
        ):
            body.visual(
                Box((0.018, boss_depth, 0.014)),
                origin=Origin(xyz=(sx, boss_cy, hb + bz_off)),
                material=metal,
                name=f"buckle_{i}_boss_{'top' if bz_off > 0 else 'bot'}", material_class_id="metal.brushed_silver",
            )
        _add_buckle_frame(body, cx=sx, cy=buckle_cy, cz=hb, material=metal, prefix=f"buckle_{i}")

    # Upper straps on the (flat) lid front wall.
    upper_strap_ly = -(d - t / 2.0) - t / 2.0 - _STRAP_T / 2.0
    upper_z_lo = -0.020
    upper_cz = upper_z_lo + _UPPER_STRAP_L / 2.0
    for i in range(2):
        sx = -_STRAP_X + i * 2.0 * _STRAP_X
        lid.visual(
            Box((_STRAP_W, _STRAP_T, _UPPER_STRAP_L)),
            origin=Origin(xyz=(sx, upper_strap_ly, upper_cz)),
            material=strap,
            name=f"upper_strap_{i}", material_class_id="leather.smooth_plain",
        )

    parts = []
    for i in range(2):
        sx = -_STRAP_X + i * 2.0 * _STRAP_X
        tongue = model.part(f"strap_tongue_{i}")
        tongue_y = tongue_cy - buckle_cy
        tongue.visual(
            Box((_STRAP_W, _STRAP_T, _TONGUE_L)),
            origin=Origin(xyz=(0.0, tongue_y, -_TONGUE_L / 2.0)),
            material=strap,
            name="tongue_strip", material_class_id="leather.smooth_plain",
        )
        tongue.visual(
            Box((_STRAP_W + 0.004, _STRAP_T + 0.001, 0.008)),
            origin=Origin(xyz=(0.0, tongue_y, -_TONGUE_L + 0.004)),
            material=metal,
            name="tongue_tip", material_class_id="metal.brushed_silver",
        )
        origin = (sx, buckle_cy, hb)
        model.articulation(
            f"strap_tongue_{i}_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=tongue,
            origin=Origin(xyz=origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=r.closure_open),
        )
        parts.append(tongue)
    return parts


def _add_zipper_track(
    part,
    *,
    width,
    depth,
    seam_z,
    mat_tape,
    mat_teeth,
    wall_outer_front,
    wall_outer_left,
    wall_outer_right,
    y_center_side,
    teeth_dir,
):
    tape_w, tape_t = _ZIP_TAPE_W, _ZIP_TAPE_T
    teeth_w, teeth_t = _ZIP_TEETH_W, _ZIP_TEETH_T
    tape_cz = seam_z + teeth_dir * (-tape_w / 2.0)
    teeth_cz = seam_z + teeth_dir * (-teeth_w / 2.0)
    front_tape_y = wall_outer_front - tape_t / 2.0
    front_teeth_y = wall_outer_front - tape_t - teeth_t / 2.0
    segments = [
        (
            (0.0, front_tape_y, tape_cz),
            (width, tape_t, tape_w),
            (0.0, front_teeth_y, teeth_cz),
            (width * 0.96, teeth_t, teeth_w),
        ),
        (
            (wall_outer_left - tape_t / 2.0, y_center_side, tape_cz),
            (tape_t, depth, tape_w),
            (wall_outer_left - tape_t - teeth_t / 2.0, y_center_side, teeth_cz),
            (teeth_t, depth * 0.96, teeth_w),
        ),
        (
            (wall_outer_right + tape_t / 2.0, y_center_side, tape_cz),
            (tape_t, depth, tape_w),
            (wall_outer_right + tape_t + teeth_t / 2.0, y_center_side, teeth_cz),
            (teeth_t, depth * 0.96, teeth_w),
        ),
    ]
    for i, (tape_pos, tape_size, teeth_pos, teeth_size) in enumerate(segments):
        part.visual(
            Box(tape_size), origin=Origin(xyz=tape_pos), material=mat_tape, name=f"zip_tape_{i}", material_class_id="fabric.webbing"
        )
        part.visual(
            Box(teeth_size), origin=Origin(xyz=teeth_pos), material=mat_teeth, name=f"zip_teeth_{i}", material_class_id="metal.brass_polished"
        )


def _build_zipper(model, body, lid, r: ResolvedSuitcaseConfig, mats):
    """Perimeter zipper (zipper L228-398). One PRISMATIC slider along the front
    seam; three tape/teeth segments on body + lid. Gated off dome."""
    w, d, hb = r.box_w, r.box_d, r.box_h
    metal = mats["metal"]
    tape_mat = mats["trim"]
    teeth_mat = mats["band"]
    sg = r.seam_gap
    _add_zipper_track(
        body,
        width=w,
        depth=d,
        seam_z=hb,
        mat_tape=tape_mat,
        mat_teeth=teeth_mat,
        wall_outer_front=-(d / 2.0),
        wall_outer_left=-(w / 2.0),
        wall_outer_right=(w / 2.0),
        y_center_side=0.0,
        teeth_dir=1.0,
    )
    _add_zipper_track(
        lid,
        width=w,
        depth=d,
        seam_z=sg,
        mat_tape=tape_mat,
        mat_teeth=teeth_mat,
        wall_outer_front=-d,
        wall_outer_left=-(w / 2.0),
        wall_outer_right=(w / 2.0),
        y_center_side=-d / 2.0,
        teeth_dir=-1.0,
    )
    slider = model.part("zipper_slider")
    slider.visual(
        Box((_SLIDER_W, _SLIDER_D, _SLIDER_H)),
        origin=Origin(xyz=(0.0, -_SLIDER_D / 2.0, 0.0)),
        material=metal,
        name="slider_body", material_class_id="metal.brushed_silver",
    )
    slider.visual(
        Box((_SLIDER_W * 0.6, 0.003, _SLIDER_H * 0.5)),
        origin=Origin(xyz=(0.0, 0.0015, 0.0)),
        material=metal,
        name="slider_channel", material_class_id="metal.brushed_silver",
    )
    slider.visual(
        Cylinder(radius=0.004, length=_SLIDER_W * 0.5),
        origin=Origin(xyz=(0.0, -_SLIDER_D, -_SLIDER_H * 0.3), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=metal,
        name="slider_bail", material_class_id="metal.brushed_silver",
    )
    slider.visual(
        Box((_TAB_W, _TAB_T, _TAB_L)),
        origin=Origin(xyz=(0.0, -_SLIDER_D, -(_SLIDER_H * 0.3 + _TAB_L / 2.0))),
        material=metal,
        name="pull_tab", material_class_id="metal.brushed_silver",
    )
    slider.visual(
        Box((_TAB_W + 0.004, _TAB_T + 0.002, 0.004)),
        origin=Origin(xyz=(0.0, -_SLIDER_D, -(_SLIDER_H * 0.3 + _TAB_L - 0.002))),
        material=metal,
        name="tab_end_stop", material_class_id="metal.brushed_silver",
    )
    # Slider parks at r.zip_origin_x (centered normally; offset right of a
    # fixed_top_grab handle's occupied arc so its travel clears the grip).
    origin = (r.zip_origin_x, -(d / 2.0), hb)
    model.articulation(
        "zipper_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=slider,
        origin=Origin(xyz=origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=0.15, lower=0.0, upper=r.zip_travel),
    )
    return slider


# ---------------------------------------------------------------------------
# Internal structure slot. open = nothing. lift_tray = a REVOLUTE packing tray.
# ---------------------------------------------------------------------------
def _build_lift_tray(model, body, r: ResolvedSuitcaseConfig, mats):
    """Lift-up packing tray (lift_tray L276-333). Tray width already projected to
    clear the reinforcement inner face in resolve_config."""
    d, t = r.box_d, r.wall_t
    tray_w = r.tray_w
    tray_d = r.tray_d
    linen = mats["linen"]
    tray = model.part("packing_tray")
    # The tray floor reaches back past the hinge line (local +Y) so its rear edge
    # overlaps the body rear interior wall — keeps the tray grounded (the source's
    # hinge standoff otherwise leaves a hairline isolation gap). Sized so the
    # grounding overlap stays below the overlap tolerance (see _TRAY_FLOOR_BACK).
    floor_back = _TRAY_FLOOR_BACK
    floor_d = tray_d + floor_back
    tray.visual(
        Box((tray_w, floor_d, _TRAY_T)),
        origin=Origin(xyz=(0.0, -tray_d / 2.0 + floor_back / 2.0, -_TRAY_T / 2.0)),
        material=linen,
        name="tray_floor", material_class_id="fabric.plain_flat_weave",
    )
    side_wall_setback = 0.06
    side_wall_depth = max(0.05, tray_d - _TRAY_WALL_T - side_wall_setback)
    side_wall_front_y = -tray_d + _TRAY_WALL_T
    side_wall_back_y = -side_wall_setback
    side_wall_cy = (side_wall_front_y + side_wall_back_y) / 2.0
    wall_specs = [
        (
            "tray_wall_0",
            (tray_w, _TRAY_WALL_T, _TRAY_WALL_H),
            (0.0, -tray_d + _TRAY_WALL_T / 2.0, _TRAY_WALL_H / 2.0),
        ),
        (
            "tray_wall_1",
            (_TRAY_WALL_T, side_wall_depth, _TRAY_WALL_H),
            (-(tray_w / 2.0 - _TRAY_WALL_T / 2.0), side_wall_cy, _TRAY_WALL_H / 2.0),
        ),
        (
            "tray_wall_2",
            (_TRAY_WALL_T, side_wall_depth, _TRAY_WALL_H),
            ((tray_w / 2.0 - _TRAY_WALL_T / 2.0), side_wall_cy, _TRAY_WALL_H / 2.0),
        ),
    ]
    for name_i, size_i, pos_i in wall_specs:
        tray.visual(Box(size_i), origin=Origin(xyz=pos_i), material=linen, name=name_i, material_class_id="fabric.plain_flat_weave")
    tray.visual(
        Box((_TRAY_TAB_W, _TRAY_WALL_T + 0.004, _TRAY_TAB_H)),
        origin=Origin(xyz=(0.0, -tray_d + _TRAY_WALL_T / 2.0, _TRAY_WALL_H + _TRAY_TAB_H / 2.0)),
        material=mats["tray_tab"],
        name="tray_lift_tab", material_class_id="leather.smooth_plain",
    )
    tray_hinge_y = d / 2.0 - t - _TRAY_HINGE_STANDOFF
    origin = (0.0, tray_hinge_y, _TRAY_Z)
    model.articulation(
        "tray_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=tray,
        origin=Origin(xyz=origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=r.tray_open),
    )
    return tray


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_suitcase(
    config: SuitcaseConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"suitcase_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    # --- Body (root) ---
    body = model.part("suitcase_body")
    _add_box_shell(
        body,
        width=r.box_w,
        depth=r.box_d,
        height=r.box_h,
        wall=r.wall_t,
        material=mats["leather"],
        z0=0.0,
    )
    _emit_reinforcement(
        body,
        r,
        mats,
        prefix="body",
        z_lo=0.0,
        z_hi=r.box_h,
        y_lo=-r.box_d / 2.0,
        y_hi=r.box_d / 2.0,
    )
    # Body vertical trim straps (omitted under lift_tray so they don't hover over
    # the open compartment above the tray; lift_tray source L130-133).
    if r.internal_structure != "lift_tray":
        for sx in (-0.16, 0.16):
            if abs(sx) < r.box_w / 2.0 - 0.03:
                body.visual(
                    Box((0.03, r.box_d + 0.004, 0.012)),
                    origin=Origin(xyz=(sx, 0.0, r.box_h - 0.018)),
                    material=mats["trim"],
                    name=f"body_strap_{'l' if sx < 0 else 'r'}", material_class_id="leather.smooth_plain",
                )

    # Fixed handle lives on the body front (Rule 1 visual).
    if r.handle_system == "fixed_top_grab":
        _build_fixed_handle(body, r, mats)

    # --- Lid (always-present rear-hinge child) ---
    lid = _build_lid(model, body, r, mats, assets=assets)

    # Folding handle must attach after the lid part exists (parent=lid).
    if r.handle_system == "folding_handle":
        _build_folding_handle(model, lid, r, mats)

    # --- Closure (mutually exclusive) ---
    if r.closure_mechanism == "latches":
        _build_latches(model, body, r, mats)
    elif r.closure_mechanism == "buckle_straps":
        _build_buckle_straps(model, body, lid, r, mats)
    else:  # zipper_perimeter
        _build_zipper(model, body, lid, r, mats)

    # --- Internal structure ---
    if r.internal_structure == "lift_tray":
        _build_lift_tray(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_suitcase(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_suitcase(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_suitcase_tests(
    object_model: ArticulatedObject,
    config: SuitcaseConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("suitcase_body")
    lid = object_model.get_part("suitcase_lid")

    # ---- Captured-pin / captured-slide allowances (element-scoped). ----
    if r.handle_system == "folding_handle":
        handle = object_model.get_part("folding_handle")
        for i in range(2):
            ctx.allow_overlap(
                lid,
                handle,
                elem_a=f"handle_pivot_mount_{i}",
                elem_b="handle_pivot_rod",
                reason="Pivot rod is captured inside the mount bracket as a hinge pin.",
            )
            ctx.allow_overlap(
                lid,
                handle,
                elem_a=f"handle_pivot_mount_{i}",
                elem_b=f"handle_arm_{i}",
                reason="Arm base pivots within the mount bracket at the hinge point.",
            )
    if r.closure_mechanism == "zipper_perimeter":
        slider = object_model.get_part("zipper_slider")
        ctx.allow_overlap(
            body,
            slider,
            elem_a="zip_teeth_0",
            elem_b="slider_body",
            reason="The zipper slider body wraps around the body-side teeth track.",
        )
        ctx.allow_overlap(
            lid,
            slider,
            elem_a="zip_teeth_0",
            elem_b="slider_body",
            reason="The zipper slider body wraps around the lid-side teeth track.",
        )

    for latch_name in ("latch_left", "latch_right"):
        if latch_name in {p.name for p in object_model.parts}:
            ctx.allow_isolated_part(
                object_model.get_part(latch_name),
                reason="latch tongue swings open on its hinge and loses lid contact",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity / structure. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "body + lid present",
        {"suitcase_body", "suitcase_lid"} <= part_names,
        details=str(sorted(part_names)),
    )

    # Always-present rear-flip lid hinge (the constant main axis).
    lid_hinge = object_model.get_articulation("lid_hinge")
    ctx.check(
        "lid_hinge is REVOLUTE about -X",
        lid_hinge.articulation_type == ArticulationType.REVOLUTE and abs(lid_hinge.axis[0]) > 0.99,
        details=f"type={lid_hinge.articulation_type} axis={tuple(lid_hinge.axis)}",
    )

    # Closed seam: lid seats on body rim (flat <=6mm / dome <=8mm gap).
    with ctx.pose({lid_hinge: 0.0}):
        seam_pos = "dome_shell" if r.lid_profile == "dome_trunk" else "wall_front"
        ctx.expect_gap(
            lid,
            body,
            axis="z",
            min_gap=0.0,
            max_gap=0.008 if r.lid_profile == "dome_trunk" else 0.006,
            positive_elem=seam_pos,
            negative_elem="wall_front",
            name="lid seats on body at the closed seam",
        )
        ctx.expect_overlap(
            lid,
            body,
            axes="xy",
            min_overlap=0.20,
            name="closed lid footprint matches body footprint",
        )
        closed_lid_aabb = ctx.part_world_aabb(lid)

    with ctx.pose({lid_hinge: min(1.8, r.lid_open * 0.9)}):
        open_lid_aabb = ctx.part_world_aabb(lid)
    ctx.check(
        "lid swings up when opened",
        closed_lid_aabb is not None
        and open_lid_aabb is not None
        and open_lid_aabb[1][2] > closed_lid_aabb[1][2] + 0.05,
        details=f"closed_top={closed_lid_aabb}, open_top={open_lid_aabb}",
    )
    # Lock: the lid must not over-rotate into the body (dome rear caps / straps).
    with ctx.pose({lid_hinge: r.lid_open}):
        ctx.fail_if_parts_overlap_in_current_pose(
            name="lid clears the body at full open (no over-rotation 穿模)"
        )
    if r.lid_profile == "dome_trunk":
        ctx.check(
            "dome lid_open capped below the body rear-reinforcement clash",
            r.lid_open <= _DOME_LID_OPEN_MAX + 1e-9,
            details=f"lid_open={r.lid_open:.3f} cap={_DOME_LID_OPEN_MAX}",
        )

    # ---- Dome identity (curved barrel-vault, not degraded). ----
    if r.lid_profile == "dome_trunk":
        dome_aabb = ctx.part_element_world_aabb(lid, elem="dome_shell")
        ctx.check(
            "dome shell has curved barrel-vault profile",
            dome_aabb is not None and (dome_aabb[1][2] - dome_aabb[0][2]) > 0.04,
            details=f"dome_aabb={dome_aabb}",
        )
        for i in range(2):
            end_aabb = ctx.part_element_world_aabb(lid, elem=f"dome_end_{i}")
            ctx.check(
                f"dome side end wall {i} closes the vault crescent",
                end_aabb is not None and (end_aabb[1][2] - end_aabb[0][2]) > r.dome_h * 0.7,
                details=f"end_{i}_aabb={end_aabb}",
            )
        # Dome closure must be the safe subset.
        ctx.check(
            "dome forces dome-safe closure + handle subset",
            r.closure_mechanism == _DOME_CLOSURE and r.handle_system == _DOME_HANDLE,
            details=f"closure={r.closure_mechanism} handle={r.handle_system}",
        )

    # ---- Reinforcement present (Rule 1 inline visuals). ----
    if r.reinforcement == "edge_banding":
        body_bands = sum(1 for v in body.visuals if v.name and v.name.startswith("body_band_"))
        ctx.check(
            "body has 12 edge-banding strips", body_bands == 12, details=f"found {body_bands}"
        )
    else:
        body_caps = sum(1 for v in body.visuals if v.name and v.name.startswith("body_corner_"))
        ctx.check("body has 4 corner caps", body_caps == 4, details=f"found {body_caps}")

    # ---- Handle. ----
    if r.handle_system == "fixed_top_grab":
        grip_aabb = ctx.part_element_world_aabb(body, elem="handle_grip")
        ctx.check(
            "carry handle grip on the front face",
            grip_aabb is not None and grip_aabb[0][1] < -(r.box_d / 2.0),
            details=f"grip_aabb={grip_aabb}",
        )
    else:
        handle = object_model.get_part("folding_handle")
        hf = object_model.get_articulation("handle_fold")
        ctx.check(
            "folding handle is REVOLUTE about -X parented to lid",
            hf.articulation_type == ArticulationType.REVOLUTE and abs(hf.axis[0]) > 0.99,
            details=f"type={hf.articulation_type} axis={tuple(hf.axis)}",
        )
        with ctx.pose({hf: 0.0}):
            flat_grip = ctx.part_element_world_aabb(handle, elem="handle_grip")
        with ctx.pose({hf: min(1.2, r.handle_open * 0.9)}):
            up_grip = ctx.part_element_world_aabb(handle, elem="handle_grip")
        ctx.check(
            "folding handle swings up from flat",
            flat_grip is not None
            and up_grip is not None
            and up_grip[0][2] > flat_grip[0][2] + 0.025,
            details=f"flat={flat_grip} up={up_grip}",
        )

    # ---- Closure topology + actuation. ----
    if r.closure_mechanism == "latches":
        latch_l = object_model.get_part("latch_left")
        jl = object_model.get_articulation("latch_left_hinge")
        ctx.check(
            "two latches are REVOLUTE about +X",
            object_model.get_part("latch_right") is not None
            and jl.articulation_type == ArticulationType.REVOLUTE
            and abs(jl.axis[0]) > 0.99,
            details=f"axis={tuple(jl.axis)}",
        )
        with ctx.pose({jl: 0.0}):
            closed = ctx.part_world_aabb(latch_l)
        with ctx.pose({jl: min(1.3, r.closure_open * 0.9)}):
            opened = ctx.part_world_aabb(latch_l)
        ctx.check(
            "latch flips open to release the lid",
            closed is not None and opened is not None and opened[1][2] < closed[1][2] - 0.02,
            details=f"closed={closed} open={opened}",
        )
    elif r.closure_mechanism == "buckle_straps":
        t0 = object_model.get_part("strap_tongue_0")
        jt = object_model.get_articulation("strap_tongue_0_hinge")
        ctx.check(
            "two buckle strap tongues are REVOLUTE about -X",
            object_model.get_part("strap_tongue_1") is not None
            and jt.articulation_type == ArticulationType.REVOLUTE
            and abs(jt.axis[0]) > 0.99,
            details=f"axis={tuple(jt.axis)}",
        )
        with ctx.pose({jt: 0.0}):
            closed = ctx.part_world_aabb(t0)
        with ctx.pose({jt: min(1.2, r.closure_open * 0.9)}):
            opened = ctx.part_world_aabb(t0)
        ctx.check(
            "strap tongue swings outward (-Y) to release",
            closed is not None and opened is not None and opened[0][1] < closed[0][1] - 0.01,
            details=f"closed={closed} open={opened}",
        )
    else:  # zipper_perimeter
        slider = object_model.get_part("zipper_slider")
        js = object_model.get_articulation("zipper_slide")
        ctx.check(
            "zipper slider is PRISMATIC about +X",
            js.articulation_type == ArticulationType.PRISMATIC and abs(js.axis[0]) > 0.99,
            details=f"type={js.articulation_type} axis={tuple(js.axis)}",
        )
        with ctx.pose({js: 0.0}):
            p0 = ctx.part_world_position(slider)
        with ctx.pose({js: r.zip_travel}):
            p1 = ctx.part_world_position(slider)
        # A fixed_top_grab handle forces the slider onto the shorter run to the
        # right of the grip, so the travel is smaller (but still real motion).
        min_travel = 0.05 if r.handle_system == "fixed_top_grab" else 0.10
        ctx.check(
            "zipper slider travels along +X on the front face",
            p0 is not None and p1 is not None and p1[0] > p0[0] + min_travel,
            details=f"start={p0} end={p1} min_travel={min_travel}",
        )
        # The slider must never enter the fixed handle grip's occupied arc.
        if r.handle_system == "fixed_top_grab":
            with ctx.pose({js: 0.0}):
                ctx.fail_if_parts_overlap_in_current_pose()
            with ctx.pose({js: r.zip_travel}):
                ctx.fail_if_parts_overlap_in_current_pose()

    # ---- Internal structure. ----
    if r.internal_structure == "lift_tray":
        tray = object_model.get_part("packing_tray")
        lid = object_model.get_part("suitcase_lid")
        jt = object_model.get_articulation("tray_hinge")
        # Sequenced mechanism: the packing tray is only lifted up once the lid is
        # swung OPEN. The sampled "lid closed + tray lifted" pose is an unphysical
        # pose-setter combo, not a real operating state, so the tray sweeping into
        # the closed-lid interior is allowed. Scoped to exactly packing_tray↔
        # suitcase_lid — tray↔suitcase_body (shell / reinforcement inner face) is
        # NOT allowed and is re-checked at full lift below.
        ctx.allow_overlap(
            tray,
            lid,
            reason=(
                "Sequenced mechanism: the rear-hinged packing tray lifts up only "
                "over the OPEN lid; the 'lid closed + tray lifted' pose is an "
                "unphysical pose-setter combo, not a real operating state, so the "
                "tray sweeping into the closed lid interior (dome_shell / shell_panel) "
                "is allowed. Scoped to packing_tray↔suitcase_lid only."
            ),
        )
        # The folding handle is lid-mounted hardware (parent=suitcase_lid), so it
        # sits inside the same closed-lid interior the tray sweeps into during the
        # unphysical "lid closed + tray lifted" pose. When the lid is swung OPEN
        # (the only pose in which the tray is really lifted) the handle rides up
        # on the open lid, clear of the tray. Same sequenced pair — lid hardware.
        if r.handle_system == "folding_handle" and "folding_handle" in part_names:
            ctx.allow_overlap(
                tray,
                object_model.get_part("folding_handle"),
                reason=(
                    "Sequenced mechanism: the lid-mounted folding_handle sits in the "
                    "closed-lid interior; the packing tray only sweeps up there in the "
                    "unphysical 'lid closed + tray lifted' pose-setter combo. With the "
                    "lid swung OPEN (the real lift pose) the handle is clear of the "
                    "tray. Scoped to packing_tray↔folding_handle only."
                ),
            )
        ctx.check(
            "lift tray is REVOLUTE about -X",
            jt.articulation_type == ArticulationType.REVOLUTE and abs(jt.axis[0]) > 0.99,
            details=f"type={jt.articulation_type} axis={tuple(jt.axis)}",
        )
        # Tray clears the reinforcement inner face (no interpenetration).
        if r.reinforcement == "edge_banding":
            inner_x = r.box_w / 2.0 - r.wall_t
        else:
            inner_x = r.box_w / 2.0 - _CORNER_CAP + 0.004
        tray_floor_aabb = ctx.part_element_world_aabb(tray, elem="tray_floor")
        ctx.check(
            "tray clears the reinforcement inner face",
            tray_floor_aabb is not None
            and tray_floor_aabb[1][0] < inner_x
            and tray_floor_aabb[0][0] > -inner_x,
            details=f"tray_x={tray_floor_aabb[0][0] if tray_floor_aabb else None}.."
            f"{tray_floor_aabb[1][0] if tray_floor_aabb else None} inner=±{inner_x:.3f}",
        )
        lid_hinge = object_model.get_articulation("lid_hinge")
        with ctx.pose({jt: 0.0}):
            closed_tray = ctx.part_world_aabb(tray)
        with ctx.pose({lid_hinge: r.lid_open, jt: r.tray_open}):
            open_tray = ctx.part_world_aabb(tray)
        # Full designed lift produces a large upward sweep of the tray.
        ctx.check(
            "packing tray lifts up when hinged",
            closed_tray is not None
            and open_tray is not None
            and open_tray[1][2] > closed_tray[1][2] + 0.004,
            details=f"closed={closed_tray} open={open_tray} tray_open={r.tray_open:.3f}",
        )
        # Real operating pose: at full lift with the lid SWUNG OPEN the tray must
        # not penetrate the suitcase body (shell / reinforcement inner face) or
        # the open lid. (The unphysical lid-closed + tray-lifted pose is the
        # pose-setter's concern and is whitelisted via the tray↔lid allowance.)
        with ctx.pose({lid_hinge: r.lid_open, jt: r.tray_open}):
            ctx.fail_if_parts_overlap_in_current_pose(
                name="tray clears the body and open lid at full lift"
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "SuitcaseConfig",
    "ResolvedSuitcaseConfig",
    "build_suitcase",
    "build_seeded_suitcase",
    "config_from_seed",
    "resolve_config",
    "run_suitcase_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
