# SPDX-License-Identifier: Apache-2.0

"""Concertina / accordion trellis security gate (folding scissor gate).

A fixed rectangular steel frame (root) spans the door opening and carries a
folding lattice / leaf column that expands and collapses as ONE motion driven
by a single REVOLUTE ``fold`` joint; every other joint is 100% mimic-coupled to
it, so the whole gate concertinas together like an accordion. ``q=0`` is the
fully DEPLOYED hero pose (lattice spans the opening); positive drive folds the
gate toward the left stile.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Door_Folding_Door_Gate.md`` and the
``folding_gate`` 5-star sample pool (1 parent + 6 slot-fork variants), all
synced under ``data/records/``:

  * rec_door_folding_gate              — single_diamond + linear_concertina +
                                         mid_latch_knob + dual_track (baseline)
  * rec_folding_gate_var_picket_pantograph — bare_pantograph lattice
  * rec_folding_gate_var_accordion_panels  — solid_panels + accordion_hinge
  * rec_folding_gate_var_dropbolt_post     — drop_bolt endpost lock
  * rec_folding_gate_var_top_track_only     — top_track_only guide track
  * rec_folding_gate_var_ncells5 / ncells16 — cell_count N multiplicity axis

Slot graph (pattern = ``mixed``): a single root ``frame`` part with four named
module axes plus one multiplicity axis (cell count N):

  * lattice_pattern (3): single_diamond / bare_pantograph / solid_panels — what
    fills each cell. The first two ride a scissor picket chain; solid_panels are
    leaf panels of the accordion spine.
  * kinematics (2): linear_concertina (1:-2:1 lambda scissor chain, axis -Y) /
    accordion_hinge (piano-hinge zigzag, alternating ±2 mimic, axis +Z).
  * endpost_lock (2): mid_latch_knob (static frame keeper visual, no joint) /
    drop_bolt (end-post FIXED to trailing link + drop_bolt PRISMATIC into a
    floor socket).
  * guide_track (2): dual_track (head + sill + top + bottom track, floor-standing)
    / top_track_only (head + top track only, ceiling-hung, pickets clear of floor).
  * cell_count N in [4, 20]: a multiplicity axis — N scissor cells (pickets
    ``picket_0..N``) or N accordion panels (``panel_0..N-1``), re-emitted by a
    ``for`` loop. Encoded into the slot_choice tuple as ``("cell_count", f"n{N}")``.

Compatibility gating (resolve_config, spec §9):
  * solid_panels  <=> accordion_hinge  (strong binding both ways).
  * single_diamond / bare_pantograph  <=> linear_concertina.
  * drop_bolt's end-post FIXES to the trailing picket (concertina) or trailing
    panel (accordion); resolve_config selects the trailing-link name by spine.

3 hard rules honoured:
  (1) Non-moving decoration (frame stiles/rails/tracks, latch keeper plate +
      knob, picket rivets, floor socket) are ``part.visual`` not FIXED parts.
  (2) The single fold REVOLUTE drive and the drop_bolt PRISMATIC are the only
      non-grandfathered joints whose contact is element-scoped; the captured-pin
      mimic chain joints (lambda halves through their elbow rivets, strap rivets,
      hinge barrels, bolt-through-post) are real articulations whose riveted-lap
      overlaps are declared with element-scoped ``allow_overlap`` and verified by
      the flat articulation-origin baseline (MatingContract omitted /
      grandfathered, like every source record's run_tests block).
  (3) No primitive downgrade: the sources are Box/Cylinder throughout, preserved.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

LatticePattern = Literal["single_diamond", "bare_pantograph", "solid_panels"]
Kinematics = Literal["linear_concertina", "accordion_hinge"]
EndpostLock = Literal["mid_latch_knob", "drop_bolt"]
GuideTrack = Literal["dual_track", "top_track_only"]
PaletteStyle = Literal[
    "terracotta_salmon",
    "galvanized_steel",
    "black_iron",
    "forest_green",
    "powder_white",
]

LATTICE_PATTERNS: tuple[LatticePattern, ...] = (
    "single_diamond",
    "bare_pantograph",
    "solid_panels",
)
KINEMATICS: tuple[Kinematics, ...] = ("linear_concertina", "accordion_hinge")
ENDPOST_LOCKS: tuple[EndpostLock, ...] = ("mid_latch_knob", "drop_bolt")
GUIDE_TRACKS: tuple[GuideTrack, ...] = ("dual_track", "top_track_only")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "terracotta_salmon",
    "galvanized_steel",
    "black_iron",
    "forest_green",
    "powder_white",
)

# Lattice patterns that ride the scissor picket chain (linear_concertina).
SCISSOR_PATTERNS: tuple[LatticePattern, ...] = ("single_diamond", "bare_pantograph")

N_MIN = 4
N_MAX = 20
# Cell-count sampling weights (spec §8): small N high-frequency, large N rare.
# Buckets: [4,6] ~35%, [7,10] ~35%, [11,14] ~20%, [15,20] ~10%.
_N_BUCKETS = ((4, 6), (7, 10), (11, 14), (15, 20))
_N_BUCKET_WEIGHTS = (0.35, 0.35, 0.20, 0.10)

# Kinematics weights (spec §8): linear_concertina ~75%, accordion_hinge ~25%.
_KINEMATICS_WEIGHTS = (0.75, 0.25)


# palette_style -> material rgba tokens (spec §7 "palette" table). Each palette
# only swaps the rgba of the body / dark accent / rivet materials; no geometry
# or topology change. All five are realistic security-gate colorways.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "terracotta_salmon": {
        "body": (0.87, 0.66, 0.59, 1.0),
        "body_dk": (0.73, 0.52, 0.46, 1.0),
        "rivet": (0.46, 0.42, 0.42, 1.0),
        "bolt": (0.28, 0.28, 0.30, 1.0),
    },
    "galvanized_steel": {
        "body": (0.74, 0.76, 0.78, 1.0),
        "body_dk": (0.55, 0.57, 0.60, 1.0),
        "rivet": (0.40, 0.41, 0.43, 1.0),
        "bolt": (0.32, 0.33, 0.35, 1.0),
    },
    "black_iron": {
        "body": (0.16, 0.16, 0.18, 1.0),
        "body_dk": (0.10, 0.10, 0.12, 1.0),
        "rivet": (0.30, 0.30, 0.32, 1.0),
        "bolt": (0.42, 0.43, 0.45, 1.0),
    },
    "forest_green": {
        "body": (0.18, 0.34, 0.24, 1.0),
        "body_dk": (0.12, 0.24, 0.17, 1.0),
        "rivet": (0.35, 0.35, 0.33, 1.0),
        "bolt": (0.24, 0.24, 0.26, 1.0),
    },
    "powder_white": {
        "body": (0.92, 0.92, 0.90, 1.0),
        "body_dk": (0.78, 0.78, 0.76, 1.0),
        "rivet": (0.55, 0.55, 0.55, 1.0),
        "bolt": (0.40, 0.40, 0.42, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). From rec_door_folding_gate L52-125.
# Long axis along X; gate stands on z=0; depth along Y. q=0 = deployed.
# ---------------------------------------------------------------------------
_FRAME_W = 1.20  # overall frame width (X) at nominal scale
_FRAME_H = 2.00  # overall frame height (Z)
_FRAME_D = 0.060  # frame depth (Y)
_STILE_W = 0.060  # vertical frame member width (X)
_RAIL_H = 0.060  # horizontal frame member height (Z)
_TRACK_T = 0.018

_LEAD_X = 0.075  # x of the anchored leading picket / panel hinge line

_PITCH_CLOSED = 0.044  # picket spacing when collapsed
_V_RISE = 0.045  # half-diamond rise (crossing height above rivet)
_PICKET_CX = 0.013  # picket cross-section (X)
_PICKET_CY = 0.022  # picket cross-section (Y / depth)

_STRAP_W = 0.020  # diamond strap face width
_STRAP_T = 0.008  # diamond strap thickness (Y)
_LAM_W = 0.022  # load lambda bar face width
_LAM_T = 0.010  # load lambda bar thickness (Y)
_BAR_EXT = 0.012  # bar end extension past its pivot (rivet lap)

_Y_FRONT = 0.0115  # front strap-family offset (asc on front face)
_RIVET_R = 0.0055
_CROSS_RIVET_LEN = 0.040

# Accordion-panel dims (rec_folding_gate_var_accordion_panels L58-78).
_PANEL_T = 0.012  # panel leaf thickness (Y)
_HINGE_R = 0.005
_RAIL_H_PANEL = 0.022  # panel edge-rail height
_FOLD_UPPER = 1.1  # accordion fold limit (~63 deg)

# Drop-bolt / end-post dims (rec_folding_gate_var_dropbolt_post L110-125).
_END_POST_CX = 0.022
_END_POST_CY = 0.028
_BOLT_R = 0.006
_BOLT_LEN = 0.350
_BOLT_HANDLE_W = 0.040
_BOLT_HANDLE_H = 0.012
_BOLT_RETRACT = 0.180
_SOCKET_DEPTH = 0.025
_SOCKET_R = _BOLT_R + 0.003

# Four diamond bands per the reference photo's banded trellis; expressed as
# fractions of the opening height so they scale with frame_height_scale.
_BAND_BOTTOM_FRACS = (0.0638, 0.2851, 0.5023, 0.7325)  # of opening @ nominal
_ROWS_PER_BAND = 2
_DRIVE_BAND = 2  # the load-path lambda row rides band 2, row 0


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class FoldingGateConfig:
    lattice_pattern: LatticePattern | None = None
    kinematics: Kinematics | None = None
    endpost_lock: EndpostLock | None = None
    guide_track: GuideTrack | None = None
    cell_count: int | None = None
    palette_style: PaletteStyle = "terracotta_salmon"
    frame_width_scale: float = 1.0
    frame_height_scale: float = 1.0
    v_rise: float = _V_RISE
    picket_cross: float = _PICKET_CX
    fold_upper: float = _FOLD_UPPER
    name: str = "folding_gate"


@dataclass(frozen=True)
class ResolvedFoldingGateConfig:
    lattice_pattern: LatticePattern
    kinematics: Kinematics
    endpost_lock: EndpostLock
    guide_track: GuideTrack
    cell_count: int
    palette_style: PaletteStyle
    # Frame geometry (scaled).
    frame_w: float
    frame_h: float
    frame_d: float
    stile_w: float
    rail_h: float
    track_t: float
    open_x0: float
    open_x1: float
    open_z0: float
    open_z1: float
    lead_x: float
    # Scissor geometry (concertina).
    pitch_open: float
    pitch_closed: float
    v_rise: float
    s_half: float
    theta0: float
    fold_angle: float
    picket_cx: float
    picket_cy: float
    picket_z0: float
    picket_z1: float
    load_z: float
    band_bottoms: tuple[float, ...]
    row_h: float
    drive_row_index: int
    # Accordion geometry.
    panel_w: float
    panel_h: float
    panel_cz: float
    fold_upper: float
    name: str

    @property
    def n_verts(self) -> int:
        return self.cell_count + 1

    @property
    def row_bottoms(self) -> tuple[float, ...]:
        zs: list[float] = []
        for zb in self.band_bottoms:
            for r in range(_ROWS_PER_BAND):
                zs.append(zb + r * self.row_h)
        return tuple(zs)

    @property
    def trailing_link(self) -> str:
        if self.kinematics == "accordion_hinge":
            return f"panel_{self.cell_count - 1}"
        return f"picket_{self.cell_count}"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Procedural sampling (deterministic; seed 0 is not special)
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> FoldingGateConfig:
    rng = random.Random(seed)

    # (1) Weighted N over [4,20], small N favoured.
    lo, hi = rng.choices(_N_BUCKETS, weights=_N_BUCKET_WEIGHTS, k=1)[0]
    cell_count = rng.randint(lo, hi)

    # (2) Sample kinematics first; derive the compatible lattice set.
    kinematics = rng.choices(KINEMATICS, weights=_KINEMATICS_WEIGHTS, k=1)[0]
    if kinematics == "accordion_hinge":
        lattice_pattern: LatticePattern = "solid_panels"
    else:
        lattice_pattern = rng.choice(SCISSOR_PATTERNS)

    # (3) Orthogonal slots.
    endpost_lock = rng.choice(ENDPOST_LOCKS)
    guide_track = rng.choice(GUIDE_TRACKS)
    palette_style = rng.choice(PALETTE_STYLES)

    # (4) Continuous local scale.
    return FoldingGateConfig(
        lattice_pattern=lattice_pattern,
        kinematics=kinematics,
        endpost_lock=endpost_lock,
        guide_track=guide_track,
        cell_count=cell_count,
        palette_style=palette_style,
        frame_width_scale=round(rng.uniform(0.85, 1.25), 4),
        frame_height_scale=round(rng.uniform(0.90, 1.15), 4),
        v_rise=round(rng.uniform(0.035, 0.055), 4),
        picket_cross=round(rng.uniform(0.010, 0.018), 4),
        fold_upper=round(rng.uniform(0.9, 1.25), 4),
        name=f"seeded_folding_gate_{seed}",
    )


def resolve_config(
    config: FoldingGateConfig | None = None,
) -> ResolvedFoldingGateConfig:
    cfg = config or FoldingGateConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    kinematics = _pick(cfg.kinematics, KINEMATICS)
    lattice_pattern = _pick(cfg.lattice_pattern, LATTICE_PATTERNS)
    endpost_lock = _pick(cfg.endpost_lock, ENDPOST_LOCKS)
    guide_track = _pick(cfg.guide_track, GUIDE_TRACKS)

    # --- Compatibility gating (spec §9): solid_panels <=> accordion_hinge. ---
    if kinematics == "accordion_hinge":
        lattice_pattern = "solid_panels"
    elif lattice_pattern == "solid_panels":
        # solid_panels only legal with accordion spine; pick accordion.
        kinematics = "accordion_hinge"
    # (concertina spine with diamond/pantograph lattice is the other branch.)

    cell_count = int(cfg.cell_count) if cfg.cell_count is not None else 10
    cell_count = int(_clamp(cell_count, N_MIN, N_MAX))

    # --- Continuous scale (clamped). ---
    w_scale = _clamp(cfg.frame_width_scale, 0.85, 1.25)
    h_scale = _clamp(cfg.frame_height_scale, 0.90, 1.15)
    v_rise = _clamp(cfg.v_rise, 0.035, 0.055)
    picket_cx = _clamp(cfg.picket_cross, 0.010, 0.018)
    fold_upper = _clamp(cfg.fold_upper, 0.9, 1.25)

    frame_w = _FRAME_W * w_scale
    frame_h = _FRAME_H * h_scale
    frame_d = _FRAME_D
    stile_w = _STILE_W
    rail_h = _RAIL_H
    track_t = _TRACK_T

    open_x0 = stile_w
    open_x1 = frame_w - stile_w
    open_z1 = frame_h - rail_h
    # guide_track conditional: ceiling-hung => no sill, opening to floor.
    open_z0 = 0.0 if guide_track == "top_track_only" else rail_h

    lead_x = _LEAD_X
    pitch_closed = _PITCH_CLOSED

    # --- pitch_open equation (spec §7): deployed pitch from usable opening / N,
    #     clamped so the scissor stays solvable and inside the right stile. A
    #     small end gap keeps the deployed trailing link clear of the stile (the
    #     end-post + drop-bolt occupy it instead). ---
    end_gap = 0.060  # deployed lattice stops short of the right stile
    usable = open_x1 - lead_x - end_gap  # span leading picket -> just shy of stile
    pitch_open = usable / cell_count
    # S_HALF must exceed pitch_open*0.5 (else acos arg > 1) and pitch_closed*0.5
    # must be < S_HALF.  Choose S_HALF from pitch_open & v_rise then verify; if
    # unsolvable, shrink pitch_open until the scissor has a valid fold solution.
    pitch_open = _clamp(pitch_open, pitch_closed + 0.012, 0.16)
    s_half = math.hypot(pitch_open * 0.5, v_rise)
    # Ensure the fully-deployed pitch is reachable (cos arg <= 1) AND the
    # collapsed pitch is reachable.  pitch_open*0.5 <= s_half always holds by
    # construction; guard pitch_closed*0.5 <= s_half by raising v_rise floor.
    for _ in range(40):
        if (pitch_closed * 0.5) <= s_half and (pitch_open * 0.5) <= s_half:
            break
        pitch_open = max(pitch_closed + 0.012, pitch_open - 0.004)
        s_half = math.hypot(pitch_open * 0.5, v_rise)

    theta0 = math.atan2(v_rise, pitch_open * 0.5)
    fold_angle = math.acos(_clamp((pitch_closed * 0.5) / s_half, -1.0, 1.0)) - theta0
    if fold_angle <= 0.05:
        fold_angle = 0.05

    # Band layout scales with opening height so straps clear the head rail.
    opening_h = open_z1 - open_z0
    band_bottoms = tuple(open_z0 + f * opening_h for f in _BAND_BOTTOM_FRACS)
    row_h = 2.0 * v_rise
    drive_row_index = _DRIVE_BAND * _ROWS_PER_BAND  # band 2, row 0
    load_z = band_bottoms[_DRIVE_BAND]

    picket_cy = _PICKET_CY
    # Pickets ride within the opening height (just inside both tracks).
    if guide_track == "top_track_only":
        picket_z0 = open_z0 + 0.025
    else:
        picket_z0 = open_z0 + 0.022
    picket_z1 = open_z1 - 0.022

    # Accordion geometry.
    panel_w = usable / cell_count
    panel_w = _clamp(panel_w, 0.040, 0.20)
    panel_h = opening_h - 0.040
    panel_cz = (open_z0 + open_z1) * 0.5

    return ResolvedFoldingGateConfig(
        lattice_pattern=lattice_pattern,
        kinematics=kinematics,
        endpost_lock=endpost_lock,
        guide_track=guide_track,
        cell_count=cell_count,
        palette_style=palette_style,
        frame_w=frame_w,
        frame_h=frame_h,
        frame_d=frame_d,
        stile_w=stile_w,
        rail_h=rail_h,
        track_t=track_t,
        open_x0=open_x0,
        open_x1=open_x1,
        open_z0=open_z0,
        open_z1=open_z1,
        lead_x=lead_x,
        pitch_open=pitch_open,
        pitch_closed=pitch_closed,
        v_rise=v_rise,
        s_half=s_half,
        theta0=theta0,
        fold_angle=fold_angle,
        picket_cx=picket_cx,
        picket_cy=picket_cy,
        picket_z0=picket_z0,
        picket_z1=picket_z1,
        load_z=load_z,
        band_bottoms=band_bottoms,
        row_h=row_h,
        drive_row_index=drive_row_index,
        panel_w=panel_w,
        panel_h=panel_h,
        panel_cz=panel_cz,
        fold_upper=fold_upper,
        name=cfg.name or "folding_gate",
    )


def with_overrides(config: FoldingGateConfig, **kwargs: object) -> FoldingGateConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FoldingGateConfig | ResolvedFoldingGateConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFoldingGateConfig) else resolve_config(config)
    return (
        ("lattice_pattern", r.lattice_pattern),
        ("kinematics", r.kinematics),
        ("endpost_lock", r.endpost_lock),
        ("guide_track", r.guide_track),
        ("cell_count", f"n{r.cell_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Slot D: guide_track — emits frame track/rail visuals (Rule 1, no joints).
# Source: rec_door_folding_gate L150-173 / rec_folding_gate_var_top_track_only
# L156-169.
# ---------------------------------------------------------------------------
def _emit_frame(model: ArticulatedObject, r: ResolvedFoldingGateConfig, mats):
    frame = model.part("frame")
    body, body_dk = mats["body"], mats["body_dk"]

    frame.visual(
        Box((r.stile_w, r.frame_d, r.frame_h)),
        origin=Origin(xyz=(r.stile_w * 0.5, 0.0, r.frame_h * 0.5)),
        material=body,
        name="stile_a", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    frame.visual(
        Box((r.stile_w, r.frame_d, r.frame_h)),
        origin=Origin(xyz=(r.frame_w - r.stile_w * 0.5, 0.0, r.frame_h * 0.5)),
        material=body,
        name="stile_b", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    frame.visual(
        Box((r.frame_w, r.frame_d, r.rail_h)),
        origin=Origin(xyz=(r.frame_w * 0.5, 0.0, r.frame_h - r.rail_h * 0.5)),
        material=body,
        name="head_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    # Top track sits just under the head rail (shared by both guide tracks).
    frame.visual(
        Box((r.open_x1 - r.open_x0, r.track_t, r.track_t)),
        origin=Origin(xyz=(r.frame_w * 0.5, 0.0, r.open_z1 - r.track_t * 0.5)),
        material=body_dk,
        name="top_track", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    if r.guide_track == "dual_track":
        # Floor-standing: sill rail + bottom track on the ground line.
        frame.visual(
            Box((r.frame_w, r.frame_d, r.rail_h)),
            origin=Origin(xyz=(r.frame_w * 0.5, 0.0, r.rail_h * 0.5)),
            material=body,
            name="sill_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
        frame.visual(
            Box((r.open_x1 - r.open_x0, r.track_t, r.track_t)),
            origin=Origin(xyz=(r.frame_w * 0.5, 0.0, r.open_z0 + r.track_t * 0.5)),
            material=body_dk,
            name="bottom_track", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
    return frame


# ---------------------------------------------------------------------------
# Slot C: endpost_lock — static keeper visual OR drop-bolt assembly.
# ---------------------------------------------------------------------------
def _emit_mid_latch_knob(model, r: ResolvedFoldingGateConfig, frame, mats):
    """Static keeper plate + catch knob on the right stile (Rule 1, no joint).

    Source: rec_door_folding_gate L177-193.
    """
    latch_z = r.frame_h * 0.5
    plate_x = r.frame_w - r.stile_w * 0.5
    frame.visual(
        Box((r.stile_w * 0.5, r.frame_d + 0.010, 0.090)),
        origin=Origin(xyz=(plate_x, 0.0, latch_z)),
        material=mats["body_dk"],
        name="latch_plate", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    frame.visual(
        Cylinder(radius=0.009, length=0.050),
        origin=Origin(
            xyz=(plate_x, r.frame_d * 0.5 + 0.018, latch_z),
            rpy=(math.pi / 2.0, 0.0, 0.0),
        ),
        material=mats["rivet"],
        name="latch_knob", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    return []


def _bolt_y_offset(r: ResolvedFoldingGateConfig) -> float:
    """Lateral (Y) seat of the drop-bolt / floor socket.

    bare_pantograph runs its full-length bars on the centerline (y=0); at large
    cell counts the steeply-angled last-cell bar overhangs its trailing picket by
    up to the end-post ``attach_x``, so a centerline bolt rod is grazed by the
    bar tip even fully deployed. Seat the bolt just off the centerline (+y, the
    side clear of the ascending bars' back-reaching cross-rivet) so it clears the
    bar tips while still overlapping the end-post bore. single_diamond keeps its
    bars on the ±_Y_FRONT faces, leaving the centerline free, and accordion has
    no lattice bars — both keep the bolt centered.
    """
    if r.kinematics != "accordion_hinge" and r.lattice_pattern == "bare_pantograph":
        return _STRAP_T * 0.5 + _BOLT_R + 0.004
    return 0.0


def _emit_drop_bolt_socket(model, r: ResolvedFoldingGateConfig, frame, mats):
    """Floor socket in the sill where the drop-bolt seats (Rule 1, frame visual).

    Source: rec_folding_gate_var_dropbolt_post L194-207. Returns the socket
    world x so the end-post / bolt can align to it at q=0.
    """
    # Align the socket exactly under the deployed drop-bolt: the bolt rides at
    # the end-post local x=0, which is mounted outboard of the trailing link.
    if r.kinematics == "accordion_hinge":
        trailing_x = r.lead_x + (r.cell_count - 1) * r.panel_w
        bolt_world_x = trailing_x + r.panel_w * 0.5 + _END_POST_CX * 0.5
    else:
        trailing_x = r.lead_x + r.cell_count * r.pitch_open
        bolt_world_x = trailing_x + r.picket_cx * 0.5 + _END_POST_CX * 0.5
    socket_x = min(bolt_world_x, r.open_x1 - _SOCKET_R - 0.004)
    # A floor boss resting ON the ground (z>=0): the bolt seats into the recess
    # at its top so the frame stays grounded for both guide tracks.
    seat_top = max(r.open_z0, _SOCKET_DEPTH)  # top of the socket boss
    bolt_y = _bolt_y_offset(r)
    frame.visual(
        Cylinder(radius=_SOCKET_R + 0.006, length=seat_top),
        origin=Origin(xyz=(socket_x, bolt_y, seat_top * 0.5)),
        material=mats["rivet"],
        name="floor_socket", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    frame.visual(
        Cylinder(radius=_SOCKET_R + 0.005, length=0.004),
        origin=Origin(xyz=(socket_x, bolt_y, seat_top + 0.002)),
        material=mats["rivet"],
        name="floor_socket_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    # Floor cleat tying the socket boss to the right stile (so the socket is a
    # real grounded frame visual, not a floating island). Embeds into both.
    stile_inner = r.frame_w - r.stile_w  # inner face of the right stile
    cleat_x_lo = socket_x  # from the socket center outward to the stile
    cleat_x_hi = stile_inner + 0.004  # embed slightly into the stile
    cleat_len = cleat_x_hi - cleat_x_lo
    if cleat_len > 0.0:
        frame.visual(
            Box((cleat_len, r.frame_d * 0.6, seat_top)),
            origin=Origin(xyz=((cleat_x_lo + cleat_x_hi) * 0.5, 0.0, seat_top * 0.5)),
            material=mats["body_dk"],
            name="floor_cleat", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
    return socket_x, seat_top


def _emit_drop_bolt_assembly(
    model, r: ResolvedFoldingGateConfig, mats, *, lap_pairs, overlap_only, socket_x, seat_top
):
    """End-post FIXED to the trailing link + drop_bolt PRISMATIC into socket.

    Source: rec_folding_gate_var_dropbolt_post L454-570. The end-post body and
    the bolt rod are authored about the trailing link's local origin (the load
    rivet height ``load_z`` for concertina, the panel center for accordion).
    """
    body, body_dk, bolt_mat = mats["body"], mats["body_dk"], mats["bolt"]
    trailing = model.get_part(r.trailing_link)
    is_accordion = r.kinematics == "accordion_hinge"

    # Vertical extent / local-frame z offset of the trailing link.
    if is_accordion:
        ref_z = r.panel_cz
        post_z0, post_z1 = r.open_z0 + 0.02, r.open_z1 - 0.02
        attach_x = r.panel_w * 0.5 + _END_POST_CX * 0.5
    else:
        ref_z = r.load_z
        post_z0, post_z1 = r.picket_z0, r.picket_z1
        attach_x = r.picket_cx * 0.5 + _END_POST_CX * 0.5

    end_post = model.part("end_post")
    end_post.visual(
        Box((_END_POST_CX, _END_POST_CY, post_z1 - post_z0)),
        origin=Origin(xyz=(0.0, 0.0, (post_z0 + post_z1) * 0.5 - ref_z)),
        material=body,
        name="post_body", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    # Two clips wrapping back toward the trailing link (real anchoring visuals).
    for ci, clip_frac in enumerate((0.30, 0.72)):
        clip_z_world = r.open_z0 + clip_frac * (r.open_z1 - r.open_z0)
        end_post.visual(
            Box((_END_POST_CX + 0.012, _END_POST_CY + 0.004, 0.018)),
            origin=Origin(xyz=(-(_END_POST_CX) * 0.5 - 0.004, 0.0, clip_z_world - ref_z)),
            material=body_dk,
            name=f"clip_{ci}", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )

    model.articulation(
        "trailing_to_end_post",
        ArticulationType.FIXED,
        parent=trailing,
        child=end_post,
        origin=Origin(xyz=(attach_x, 0.0, 0.0)),
    )

    # Drop bolt: slim vertical rod sliding through the end-post; q=0 = seated.
    # The pointed tip seats DOWN into the socket boss recess (just below its
    # top face) so the gate is locked and the frame stays grounded (z>=0).
    bolt_tip_bottom = seat_top - 0.012  # tip bottom inside the socket recess
    bolt_center_z = bolt_tip_bottom + 0.015 + _BOLT_LEN * 0.5
    drop_bolt = model.part("drop_bolt")
    drop_bolt.visual(
        Cylinder(radius=_BOLT_R, length=_BOLT_LEN),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=bolt_mat,
        name="bolt_rod", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    # Operating handle offset OUTBOARD (+x, toward the right stile / away from
    # the lattice). The trailing cell's descending lattice bar swings up to the
    # bolt rod as the gate folds; a handle centered on the rod would extend
    # ~half its width back into that bar's swept envelope. The bar tip overhangs
    # the trailing picket by at most ``_BAR_EXT`` (< the end-post ``attach_x``),
    # so it always stays inboard of the rod centerline. Seating the handle's
    # inboard edge at the rod center keeps it clear of the folded lattice for any
    # fold angle / cell count while still solidly overlapping the rod (the thin
    # rod's own residual lap with the bar stays sub-tol).
    handle_x_off = _BOLT_HANDLE_W * 0.5
    drop_bolt.visual(
        Box((_BOLT_HANDLE_W, _BOLT_R * 2.0, _BOLT_HANDLE_H)),
        origin=Origin(xyz=(handle_x_off, 0.0, _BOLT_LEN * 0.5 - _BOLT_HANDLE_H * 0.5)),
        material=bolt_mat,
        name="bolt_handle", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    drop_bolt.visual(
        Cylinder(radius=_BOLT_R * 0.6, length=0.015),
        origin=Origin(xyz=(0.0, 0.0, -(_BOLT_LEN * 0.5 + 0.0075))),
        material=bolt_mat,
        name="bolt_tip", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    model.articulation(
        "bolt_slide",
        ArticulationType.PRISMATIC,
        parent=end_post,
        child=drop_bolt,
        origin=Origin(xyz=(0.0, _bolt_y_offset(r), bolt_center_z - ref_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.3, lower=0.0, upper=_BOLT_RETRACT),
    )

    lap_pairs.append(
        ("end_post", r.trailing_link, "End-post is bolted to the trailing link via mounting clips.")
    )
    lap_pairs.append(
        ("drop_bolt", "end_post", "Drop-bolt rod slides through a bore in the end-post.")
    )
    lap_pairs.append(
        ("drop_bolt", "frame", "Drop-bolt tip seats into the frame floor socket when locked.")
    )
    # Speculative protrusion overlaps (geometry-dependent on N / scale): silence
    # the overlap gate WITHOUT asserting tight contact.
    overlap_only.append(
        (
            "drop_bolt",
            r.trailing_link,
            "Bolt handle may pass near the trailing link where the end-post is mounted.",
        )
    )
    overlap_only.append(
        (
            "end_post",
            "frame",
            "End-post may seat into the right-stile rebate when the gate is deployed.",
        )
    )
    # The trailing cell's protruding bar / strap extensions may lap onto the
    # wider end-post body (source: dropbolt L544-560).
    if not is_accordion:
        last = r.cell_count - 1
        if r.lattice_pattern == "single_diamond":
            for ri in range(len(r.row_bottoms)):
                overlap_only.append(
                    (
                        f"asc_{last}_{ri}",
                        "end_post",
                        "Last-cell ascending strap may lap onto the end-post body.",
                    )
                )
                overlap_only.append(
                    (
                        f"desc_{last}_{ri}",
                        "end_post",
                        "Last-cell descending strap may lap onto the end-post body.",
                    )
                )
        else:
            for ri in range(len(r.band_bottoms)):
                if ri == _DRIVE_BAND:
                    continue
                overlap_only.append(
                    (
                        f"xup_{last}_{ri}",
                        "end_post",
                        "Last-cell ascending bar may lap onto the end-post body.",
                    )
                )
                overlap_only.append(
                    (
                        f"xdn_{last}_{ri}",
                        "end_post",
                        "Last-cell descending bar may lap onto the end-post body.",
                    )
                )
        overlap_only.append(
            (
                f"lam_dn_{last}",
                "end_post",
                "Last-cell lower lambda bar may lap near the end-post mounting.",
            )
        )
    return ["end_post", "drop_bolt"]


# ---------------------------------------------------------------------------
# Slot B = linear_concertina: scissor picket chain (Slot A rides on it).
# Source: rec_door_folding_gate L195-442 / rec_folding_gate_var_picket_pantograph.
# ---------------------------------------------------------------------------
def _build_pickets(model, r: ResolvedFoldingGateConfig, mats):
    body, body_dk, rivet = mats["body"], mats["body_dk"], mats["rivet"]
    rivet_len = r.picket_cy + 2.0 * _STRAP_T + 0.004
    rivet_zs = sorted({z for zb in r.row_bottoms for z in (zb, zb + r.row_h)})
    pickets = []
    for i in range(r.n_verts):
        p = model.part(f"picket_{i}")
        p.visual(
            Box((r.picket_cx, r.picket_cy, r.picket_z1 - r.picket_z0)),
            origin=Origin(xyz=(0.0, 0.0, (r.picket_z0 + r.picket_z1) * 0.5 - r.load_z)),
            material=body,
            name="picket_bar", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
        for k, z in enumerate(rivet_zs):
            p.visual(
                Cylinder(radius=_RIVET_R, length=rivet_len),
                origin=Origin(xyz=(0.0, 0.0, z - r.load_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=rivet,
                name=f"rivet_{k}", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
            )
        pickets.append(p)

    # Leading picket bolted to the left stile (real anchoring bracket visual).
    b_lo = (r.stile_w - r.lead_x) - 0.002
    b_hi = (-r.picket_cx * 0.5) + 0.002
    pickets[0].visual(
        Box((b_hi - b_lo, 0.030, 0.080)),
        origin=Origin(xyz=((b_lo + b_hi) * 0.5, 0.0, 0.0)),
        material=body_dk,
        name="mount_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    return pickets


def _lam_bar(model, name: str, r: ResolvedFoldingGateConfig, mats):
    part = model.part(name)
    part.visual(
        Box((r.s_half + 2.0 * _BAR_EXT, _LAM_T, _LAM_W)),
        origin=Origin(xyz=(r.s_half * 0.5, 0.0, 0.0)),
        material=mats["body_dk"],
        name="bar", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    return part


def _full_bar(model, name: str, r: ResolvedFoldingGateConfig, mats, *, with_cross_rivet):
    part = model.part(name)
    part.visual(
        Box((2.0 * r.s_half + 2.0 * _BAR_EXT, _STRAP_T, _STRAP_W)),
        origin=Origin(xyz=(r.s_half, 0.0, 0.0)),
        material=mats["body"],
        name="bar", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    if with_cross_rivet:
        part.visual(
            Cylinder(radius=_RIVET_R, length=_CROSS_RIVET_LEN),
            origin=Origin(xyz=(r.s_half, -_Y_FRONT, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["rivet"],
            name="cross_rivet", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
    return part


def _build_concertina(model, r: ResolvedFoldingGateConfig, frame, mats, *, lap_pairs, overlap_only):
    """Single REVOLUTE ``fold`` drive + 1:-2:1 lambda mimic chain + Slot-A straps.

    Source: rec_door_folding_gate L230-442 (single_diamond) and
    rec_folding_gate_var_picket_pantograph L276-427 (bare_pantograph).
    """
    pickets = _build_pickets(model, r, mats)

    model.articulation(
        "frame_to_picket_0",
        ArticulationType.FIXED,
        parent=frame,
        child=pickets[0],
        origin=Origin(xyz=(r.lead_x, 0.0, r.load_z)),
    )

    drive_name = "fold"
    rev_limits = MotionLimits(effort=120.0, velocity=0.8, lower=0.0, upper=r.fold_angle)
    elbow_limits = MotionLimits(effort=120.0, velocity=1.6, lower=0.0, upper=2.0 * r.fold_angle)

    lap_pairs.append(
        ("picket_0", "frame", "Leading picket is bolted to the left stile by its mount bracket.")
    )

    is_diamond = r.lattice_pattern == "single_diamond"
    if is_diamond:
        # single_diamond: 8 rows (2 per band); asc/desc on opposite faces.
        row_bottoms = r.row_bottoms
        drive_ri = r.drive_row_index  # band 2, row 0
    else:
        # bare_pantograph: 4 widely-spaced rows (one per band) on the
        # centerline; bars are full length so rows must not stack closely.
        row_bottoms = r.band_bottoms
        drive_ri = _DRIVE_BAND  # band 2

    for c in range(r.cell_count):
        left = pickets[c]
        right = pickets[c + 1]

        # --- Load-path lambda linkage (the cell's real scissor half). ---
        up = _lam_bar(model, f"lam_up_{c}", r, mats)
        up_kwargs = dict(
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, -r.theta0, 0.0)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=rev_limits,
        )
        if c == 0:
            model.articulation(
                drive_name, ArticulationType.REVOLUTE, parent=left, child=up, **up_kwargs
            )
        else:
            up_kwargs["mimic"] = Mimic(joint=drive_name, multiplier=1.0)
            model.articulation(
                f"lam_up_{c}_pivot", ArticulationType.REVOLUTE, parent=left, child=up, **up_kwargs
            )

        dn = _lam_bar(model, f"lam_dn_{c}", r, mats)
        dn.visual(
            Cylinder(radius=_RIVET_R, length=_CROSS_RIVET_LEN),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["rivet"],
            name="elbow_rivet", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
        model.articulation(
            f"lam_elbow_{c}",
            ArticulationType.REVOLUTE,
            parent=up,
            child=dn,
            origin=Origin(xyz=(r.s_half, 0.0, 0.0), rpy=(0.0, 2.0 * r.theta0, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=elbow_limits,
            mimic=Mimic(joint=drive_name, multiplier=2.0),
        )
        model.articulation(
            f"lam_dn_{c}_to_picket_{c + 1}",
            ArticulationType.REVOLUTE,
            parent=dn,
            child=right,
            origin=Origin(xyz=(r.s_half, 0.0, 0.0), rpy=(0.0, -r.theta0, 0.0)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=rev_limits,
            mimic=Mimic(joint=drive_name, multiplier=1.0),
        )

        lap_pairs.append(
            (f"lam_up_{c}", f"picket_{c}", "Lambda bar riveted (lapped) to its pivot picket.")
        )
        lap_pairs.append(
            (f"lam_up_{c}", f"lam_dn_{c}", "Lambda halves lap at their shared elbow rivet.")
        )
        lap_pairs.append(
            (
                f"lam_dn_{c}",
                f"picket_{c + 1}",
                "Lambda bar riveted (lapped) to the picket it carries.",
            )
        )
        if c > 0:
            lap_pairs.append(
                (
                    f"lam_dn_{c - 1}",
                    f"lam_up_{c}",
                    "Adjacent lambda bars share the picket rivet and lap there.",
                )
            )

        # --- Slot A lattice rows (mimic +1 to fold). ---
        for ri, z_bot in enumerate(row_bottoms):
            z_top = z_bot + r.row_h

            if is_diamond:
                # single_diamond: asc on the front face, desc on the back face.
                asc = _full_bar(model, f"asc_{c}_{ri}", r, mats, with_cross_rivet=True)
                model.articulation(
                    f"asc_{c}_{ri}_pivot",
                    ArticulationType.REVOLUTE,
                    parent=left,
                    child=asc,
                    origin=Origin(xyz=(0.0, _Y_FRONT, z_bot - r.load_z), rpy=(0.0, -r.theta0, 0.0)),
                    axis=(0.0, -1.0, 0.0),
                    motion_limits=rev_limits,
                    mimic=Mimic(joint=drive_name, multiplier=1.0),
                )
                desc = _full_bar(model, f"desc_{c}_{ri}", r, mats, with_cross_rivet=False)
                model.articulation(
                    f"desc_{c}_{ri}_pivot",
                    ArticulationType.REVOLUTE,
                    parent=left,
                    child=desc,
                    origin=Origin(xyz=(0.0, -_Y_FRONT, z_top - r.load_z), rpy=(0.0, r.theta0, 0.0)),
                    axis=(0.0, 1.0, 0.0),
                    motion_limits=rev_limits,
                    mimic=Mimic(joint=drive_name, multiplier=1.0),
                )
                up_nm, dn_nm = f"asc_{c}_{ri}", f"desc_{c}_{ri}"
            else:
                # bare_pantograph: full-length crossed bars on the centerline,
                # one row carries the drive lambda (skip it to avoid doubling).
                if ri == drive_ri:
                    continue
                asc = _full_bar(model, f"xup_{c}_{ri}", r, mats, with_cross_rivet=True)
                model.articulation(
                    f"xup_{c}_{ri}_pivot",
                    ArticulationType.REVOLUTE,
                    parent=left,
                    child=asc,
                    origin=Origin(xyz=(0.0, 0.0, z_bot - r.load_z), rpy=(0.0, -r.theta0, 0.0)),
                    axis=(0.0, -1.0, 0.0),
                    motion_limits=rev_limits,
                    mimic=Mimic(joint=drive_name, multiplier=1.0),
                )
                desc = _full_bar(model, f"xdn_{c}_{ri}", r, mats, with_cross_rivet=False)
                model.articulation(
                    f"xdn_{c}_{ri}_pivot",
                    ArticulationType.REVOLUTE,
                    parent=left,
                    child=desc,
                    origin=Origin(xyz=(0.0, 0.0, z_top - r.load_z), rpy=(0.0, r.theta0, 0.0)),
                    axis=(0.0, 1.0, 0.0),
                    motion_limits=rev_limits,
                    mimic=Mimic(joint=drive_name, multiplier=1.0),
                )
                up_nm, dn_nm = f"xup_{c}_{ri}", f"xdn_{c}_{ri}"

            for nm in (up_nm, dn_nm):
                lap_pairs.append(
                    (nm, f"picket_{c}", "Strap/bar riveted (lapped) to its pivot picket.")
                )
                lap_pairs.append(
                    (
                        nm,
                        f"picket_{c + 1}",
                        "Strap/bar slides past the neighbouring picket (slotted rivet).",
                    )
                )
            lap_pairs.append((up_nm, dn_nm, "Crossed straps/bars pinned by the mid-cell rivet."))

            # Adjacent cells' bars continue the zigzag through the shared picket
            # rivet; the full-length bars lap there (and ascending/descending of
            # neighbouring cells cross). Geometry-dependent => overlap-only.
            if c + 1 < r.cell_count:
                if is_diamond:
                    # Same-row cross (asc/desc) and the banded zigzag continuation
                    # (asc -> asc_{c+1}_{ri+1}, desc -> desc_{c+1}_{ri-1} within band).
                    overlap_only.append(
                        (
                            dn_nm,
                            f"asc_{c + 1}_{ri}",
                            "Adjacent cells' straps lap at the shared picket rivet (zigzag).",
                        )
                    )
                    overlap_only.append(
                        (
                            up_nm,
                            f"desc_{c + 1}_{ri}",
                            "Adjacent cells' straps lap at the shared picket rivet (zigzag).",
                        )
                    )
                    in_band_row = ri % _ROWS_PER_BAND
                    if in_band_row + 1 < _ROWS_PER_BAND:
                        overlap_only.append(
                            (
                                up_nm,
                                f"asc_{c + 1}_{ri + 1}",
                                "Ascending straps of adjacent cells lap (continuous zigzag).",
                            )
                        )
                    if in_band_row > 0:
                        overlap_only.append(
                            (
                                dn_nm,
                                f"desc_{c + 1}_{ri - 1}",
                                "Descending straps of adjacent cells lap (continuous zigzag).",
                            )
                        )
                else:
                    overlap_only.append(
                        (
                            dn_nm,
                            f"xup_{c + 1}_{ri}",
                            "Adjacent cells' bars lap at the shared picket rivet (zigzag).",
                        )
                    )
                    overlap_only.append(
                        (
                            up_nm,
                            f"xdn_{c + 1}_{ri}",
                            "Adjacent cells' bars lap at the shared picket rivet (zigzag).",
                        )
                    )

    # Load lambda row shares rivets with the load-row straps (single_diamond).
    if is_diamond:
        load_ri = drive_ri
        for c in range(r.cell_count):
            lap_pairs.append(
                (
                    f"lam_up_{c}",
                    f"asc_{c}_{load_ri}",
                    "Load lambda stacks on the load-row strap rivet.",
                )
            )
            lap_pairs.append(
                (
                    f"lam_dn_{c}",
                    f"asc_{c}_{load_ri}",
                    "Load lambda stacks on the load-row strap rivet.",
                )
            )
            lap_pairs.append(
                (
                    f"lam_dn_{c}",
                    f"desc_{c}_{load_ri}",
                    "Elbow rivet pins the descending load-row strap.",
                )
            )

        # Within-band adjacent-row slats stack in the compressed lattice. A dense
        # diamond trellis packs its diagonal slats coplanar per face (asc on the
        # front, desc on the back); the two rows sharing a band sit only row_h
        # apart, so as the gate folds toward full collapse they nest into a tight
        # slat bundle (exactly the coplanar lapping already declared between
        # adjacent CELLS above — just for the two rows within a band). The asc
        # cross-rivet also pins across to the paired row's descending slat.
        n_rows = len(r.row_bottoms)
        for c in range(r.cell_count):
            for ri in range(n_rows - 1):
                if (ri + 1) // _ROWS_PER_BAND != ri // _ROWS_PER_BAND:
                    continue  # different band => rows stay clear
                overlap_only.append(
                    (
                        f"asc_{c}_{ri}",
                        f"asc_{c}_{ri + 1}",
                        "Same-band ascending slats nest into the folded slat bundle.",
                    )
                )
                overlap_only.append(
                    (
                        f"desc_{c}_{ri}",
                        f"desc_{c}_{ri + 1}",
                        "Same-band descending slats nest into the folded slat bundle.",
                    )
                )
                overlap_only.append(
                    (
                        f"asc_{c}_{ri}",
                        f"desc_{c}_{ri + 1}",
                        "Ascending cross-rivet pins across to the paired row's descending slat.",
                    )
                )
                overlap_only.append(
                    (
                        f"asc_{c}_{ri + 1}",
                        f"desc_{c}_{ri}",
                        "Ascending cross-rivet pins across to the paired row's descending slat.",
                    )
                )
                # The next cell's lower-row ascending slat crosses this cell's
                # upper-row descending slat at the shared picket as the zigzag
                # continues (folded coplanar lap).
                if c + 1 < r.cell_count:
                    overlap_only.append(
                        (
                            f"asc_{c + 1}_{ri}",
                            f"desc_{c}_{ri + 1}",
                            "Next cell's low-row ascending slat laps this cell's "
                            "high-row descending slat at the shared picket.",
                        )
                    )

        # The load-path lambda is the drive linkage embedded IN the drive band;
        # it rides between two pickets and shares those bands' slat/rivet stack,
        # so both lambda halves lap both drive-band rows (both faces) of their own
        # cell and the neighbouring cells that share the carried picket, plus both
        # pivot pickets. These are structural (present at all fold angles).
        drive_rows = tuple(dr for dr in (drive_ri, drive_ri + 1) if 0 <= dr < n_rows)
        for c in range(r.cell_count):
            for lam in (f"lam_up_{c}", f"lam_dn_{c}"):
                for cc in (c - 1, c, c + 1):
                    if not (0 <= cc < r.cell_count):
                        continue
                    for dr in drive_rows:
                        overlap_only.append(
                            (
                                lam,
                                f"asc_{cc}_{dr}",
                                "Load lambda shares the drive-band ascending slat stack.",
                            )
                        )
                        overlap_only.append(
                            (
                                lam,
                                f"desc_{cc}_{dr}",
                                "Load lambda shares the drive-band descending slat stack.",
                            )
                        )
                for pk in (f"picket_{c}", f"picket_{c + 1}"):
                    overlap_only.append((lam, pk, "Load lambda laps the pickets it rides between."))

    return pickets


# ---------------------------------------------------------------------------
# Slot A+B = solid_panels + accordion_hinge: piano-hinge zigzag panel column.
# Source: rec_folding_gate_var_accordion_panels L85-290.
# ---------------------------------------------------------------------------
def _add_panel_visuals(part, index, r: ResolvedFoldingGateConfig, mats):
    body, body_dk, rivet = mats["body"], mats["body_dk"], mats["rivet"]
    rail_w = r.panel_w - 0.006
    rail_t = _PANEL_T + 0.006
    part.visual(
        Box((r.panel_w, _PANEL_T, r.panel_h)),
        origin=Origin(xyz=(r.panel_w * 0.5, 0.0, 0.0)),
        material=body,
        name="leaf", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    part.visual(
        Box((rail_w, rail_t, _RAIL_H_PANEL)),
        origin=Origin(xyz=(r.panel_w * 0.5, 0.0, r.panel_h * 0.5 - _RAIL_H_PANEL * 0.5)),
        material=rivet,
        name="top_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    part.visual(
        Box((rail_w, rail_t, _RAIL_H_PANEL)),
        origin=Origin(xyz=(r.panel_w * 0.5, 0.0, -r.panel_h * 0.5 + _RAIL_H_PANEL * 0.5)),
        material=rivet,
        name="bottom_rail", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
    )
    if index < r.cell_count - 1:
        part.visual(
            Cylinder(radius=_HINGE_R, length=r.panel_h * 0.85),
            origin=Origin(xyz=(r.panel_w, 0.0, 0.0)),
            material=rivet,
            name="hinge_barrel", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )
    if index == 0:
        b_lo = (r.stile_w - r.lead_x) - 0.002
        b_hi = 0.002
        part.visual(
            Box((b_hi - b_lo, 0.040, 0.080)),
            origin=Origin(xyz=((b_lo + b_hi) * 0.5, 0.0, 0.0)),
            material=body_dk,
            name="mount_bracket", material_class_id=("metal.paint_coated" if r.palette_style in {"terracotta_salmon", "black_iron", "forest_green", "powder_white"} else "metal.steel_galvanized"),
        )


def _build_accordion(model, r: ResolvedFoldingGateConfig, frame, mats, *, lap_pairs, overlap_only):
    """Single REVOLUTE ``fold`` drive (panel_0->panel_1) + alternating ±2 mimic.

    Source: rec_folding_gate_var_accordion_panels L216-290.
    """
    panels = []
    for i in range(r.cell_count):
        p = model.part(f"panel_{i}")
        _add_panel_visuals(p, i, r, mats)
        panels.append(p)

    model.articulation(
        "frame_to_panel_0",
        ArticulationType.FIXED,
        parent=frame,
        child=panels[0],
        origin=Origin(xyz=(r.lead_x, 0.0, r.panel_cz)),
    )

    drive_name = "fold"
    if r.cell_count >= 2:
        model.articulation(
            drive_name,
            ArticulationType.REVOLUTE,
            parent=panels[0],
            child=panels[1],
            origin=Origin(xyz=(r.panel_w, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=0.8, lower=0.0, upper=r.fold_upper),
        )

    lap_pairs.append(
        ("panel_0", "frame", "Leading panel is bolted to the left stile by its mount bracket.")
    )

    for i in range(1, r.cell_count - 1):
        multiplier = 2.0 * ((-1) ** i)  # -2, +2, -2, ...
        if multiplier < 0:
            lo, hi = multiplier * r.fold_upper, 0.0
        else:
            lo, hi = 0.0, multiplier * r.fold_upper
        model.articulation(
            f"hinge_{i}",
            ArticulationType.REVOLUTE,
            parent=panels[i],
            child=panels[i + 1],
            origin=Origin(xyz=(r.panel_w, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=120.0, velocity=1.6, lower=lo, upper=hi),
            mimic=Mimic(joint=drive_name, multiplier=multiplier),
        )

    for i in range(r.cell_count - 1):
        lap_pairs.append(
            (
                f"panel_{i}",
                f"panel_{i + 1}",
                f"Hinge barrel at the seam between panel_{i} and panel_{i + 1}.",
            )
        )
    return panels


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_folding_gate(
    config: FoldingGateConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"folding_gate_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    lap_pairs: list[tuple[str, str, str]] = []
    overlap_only: list[tuple[str, str, str]] = []

    # Slot D: frame (root) emits its track/rail visuals.
    frame = _emit_frame(model, r, mats)

    # Slot C: floor socket BEFORE the spine (frame visual) so drop_bolt aligns.
    socket_x = None
    socket_seat = None
    if r.endpost_lock == "drop_bolt":
        socket_x, socket_seat = _emit_drop_bolt_socket(model, r, frame, mats)

    # Slot B + Slot A: the folding spine.
    if r.kinematics == "accordion_hinge":
        _build_accordion(model, r, frame, mats, lap_pairs=lap_pairs, overlap_only=overlap_only)
    else:
        _build_concertina(model, r, frame, mats, lap_pairs=lap_pairs, overlap_only=overlap_only)

    # Slot C: end-post + drop-bolt (FIXED to trailing link) OR static keeper.
    if r.endpost_lock == "drop_bolt":
        _emit_drop_bolt_assembly(
            model,
            r,
            mats,
            lap_pairs=lap_pairs,
            overlap_only=overlap_only,
            socket_x=socket_x,
            seat_top=socket_seat,
        )
    else:
        _emit_mid_latch_knob(model, r, frame, mats)

    frame.inertial = Inertial.from_geometry(
        Box((r.frame_w, r.frame_d, r.frame_h)),
        mass=8.0,
        origin=Origin(xyz=(r.frame_w * 0.5, 0.0, r.frame_h * 0.5)),
    )

    model.meta["lap_pairs"] = lap_pairs
    model.meta["overlap_only"] = overlap_only
    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_folding_gate(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_folding_gate(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_folding_gate_tests(
    object_model: ArticulatedObject,
    config: FoldingGateConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    frame = object_model.get_part("frame")
    is_accordion = r.kinematics == "accordion_hinge"

    # ---- Declare intentional riveted-lap / captured-pin overlaps. ----
    # Guaranteed contacts: allow the overlap AND assert the parts are seated.
    for a, b, reason in object_model.meta.get("lap_pairs", []):
        ctx.allow_overlap(a, b, reason=reason)
        ctx.expect_contact(
            object_model.get_part(a),
            object_model.get_part(b),
            contact_tol=1.5e-3,
            name=f"{a} seated on {b}",
        )
    # Speculative protrusion overlaps (geometry-dependent): silence the overlap
    # gate only, without asserting tight contact.
    for a, b, reason in object_model.meta.get("overlap_only", []):
        ctx.allow_overlap(a, b, reason=reason)
    # Drop-bolt floor cleat / socket boss sit at the trailing link's foot; the
    # deployed trailing link's low edge may brush them (element-scoped — both
    # element names supplied so the allowance actually matches).
    if r.endpost_lock == "drop_bolt":
        _frame_vis0 = {v.name for v in frame.visuals}
        _trailing0 = object_model.get_part(r.trailing_link)
        if r.kinematics == "accordion_hinge":
            _trailing_elems = ("leaf", "bottom_rail")
        else:
            _trailing_elems = ("picket_bar",)
        for _ea in _trailing_elems:
            for _eb in ("floor_cleat", "floor_socket", "floor_socket_rim"):
                if _eb in _frame_vis0:
                    ctx.allow_overlap(
                        _trailing0,
                        frame,
                        elem_a=_ea,
                        elem_b=_eb,
                        reason="Trailing link foot brushes the drop-bolt floor cleat / socket boss.",
                    )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Frame identity (root grounded, spans the opening). ----
    fb = ctx.part_world_aabb(frame)
    ctx.check(
        "frame stands on ground",
        fb is not None and abs(fb[0][2]) < 1e-4,
        details=f"frame z-min={None if fb is None else fb[0][2]}",
    )
    ctx.check(
        "frame ~width and ~height match resolved scale",
        fb is not None
        and abs((fb[1][2] - fb[0][2]) - r.frame_h) < 2e-3
        and abs((fb[1][0] - fb[0][0]) - r.frame_w) < 2e-3,
        details=f"aabb={fb}",
    )

    # ---- Single explicit drive: exactly one non-mimic actuated joint. ----
    drive = object_model.get_articulation("fold")
    ctx.check(
        "fold is the single REVOLUTE drive",
        drive.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={drive.articulation_type}",
    )

    # ---- Guide-track conditional consistency. ----
    frame_vis = {v.name for v in frame.visuals}
    if r.guide_track == "top_track_only":
        ctx.check(
            "top_track_only omits sill_rail / bottom_track",
            "sill_rail" not in frame_vis
            and "bottom_track" not in frame_vis
            and "top_track" in frame_vis,
            details=str(sorted(frame_vis)),
        )
        ctx.check(
            "ceiling-hung opening reaches floor",
            abs(r.open_z0) < 1e-9,
            details=f"open_z0={r.open_z0}",
        )
    else:
        ctx.check(
            "dual_track emits sill_rail + bottom_track + top_track",
            {"sill_rail", "bottom_track", "top_track"} <= frame_vis,
            details=str(sorted(frame_vis)),
        )

    # ---- Endpost-lock topology. ----
    if r.endpost_lock == "drop_bolt":
        ctx.check(
            "floor_socket present on frame",
            "floor_socket" in frame_vis,
            details=str(sorted(frame_vis)),
        )
        jb = object_model.get_articulation("bolt_slide")
        ctx.check(
            "drop_bolt is PRISMATIC about +Z",
            jb.articulation_type == ArticulationType.PRISMATIC and abs(jb.axis[2]) > 0.99,
            details=f"type={jb.articulation_type} axis={tuple(jb.axis)}",
        )
        jp = object_model.get_articulation("trailing_to_end_post")
        ctx.check(
            "end_post FIXED to trailing link",
            jp.articulation_type == ArticulationType.FIXED,
            details=f"type={jp.articulation_type}",
        )
        # Seated bolt tip sits low in the floor socket at q=0; retract lifts it.
        bolt = object_model.get_part("drop_bolt")
        seated = ctx.part_world_aabb(bolt)
        with ctx.pose({jb: _BOLT_RETRACT * 0.9}):
            lifted = ctx.part_world_aabb(bolt)
        # Seated bolt tip rests near the floor/sill line (within the socket boss
        # height + the opening floor); retracting lifts it well clear.
        seat_low_limit = max(r.open_z0, _SOCKET_DEPTH) + 0.02
        if seated is not None and lifted is not None:
            ctx.check(
                "drop_bolt seats low at q=0 and retracts upward",
                seated[0][2] < seat_low_limit and lifted[0][2] > seated[0][2] + 0.05,
                details=f"seated_zmin={seated[0][2]:.3f} lifted_zmin={lifted[0][2]:.3f} limit={seat_low_limit:.3f}",
            )
    else:
        ctx.check(
            "mid_latch_knob is static frame keeper (plate + knob)",
            {"latch_plate", "latch_knob"} <= frame_vis,
            details=str(sorted(frame_vis)),
        )

    # ---- Spine-specific kinematics. ----
    if is_accordion:
        panels = [object_model.get_part(f"panel_{i}") for i in range(r.cell_count)]
        ctx.check(
            "all accordion panels present",
            all(p is not None for p in panels),
            details=f"N={r.cell_count}",
        )
        ctx.check(
            "fold drive is REVOLUTE about +Z",
            abs(drive.axis[2]) > 0.99,
            details=f"axis={tuple(drive.axis)}",
        )

        def panel_x() -> list[float]:
            return [ctx.part_world_position(p)[0] for p in panels]

        x_open = panel_x()
        ctx.check(
            "leading panel anchored at lead_x",
            abs(x_open[0] - r.lead_x) < 1e-4,
            details=f"x0={x_open[0]}",
        )
        # The trailing panel origin is at its LEFT hinge edge; the column's right
        # edge is one more panel_w out. Span check uses that right edge.
        deployed_right = x_open[-1] + r.panel_w
        ctx.check(
            "deployed panels span most of the opening",
            deployed_right > r.lead_x + 0.5 * (r.open_x1 - r.lead_x),
            details=f"right edge={deployed_right:.3f} trailing origin={x_open[-1]:.3f}",
        )
        ctx.check(
            "deployed panel pitch uniform (=PANEL_W)",
            all(
                abs((x_open[i + 1] - x_open[i]) - r.panel_w) < 1e-4 for i in range(r.cell_count - 1)
            ),
            details=f"pitches={[round(x_open[i + 1] - x_open[i], 4) for i in range(r.cell_count - 1)]}",
        )
        if r.cell_count >= 3:
            deployed_span = x_open[-1] - x_open[0]
            with ctx.pose({drive: r.fold_upper}):
                x_fold = panel_x()
                folded_span = x_fold[-1] - x_fold[0]
                y_fold = [abs(ctx.part_world_position(p)[1]) for p in panels]
            ctx.check(
                "gate concertinas: span contracts when folded",
                folded_span < deployed_span * 0.75,
                details=f"deployed={deployed_span:.3f} folded={folded_span:.3f}",
            )
            ctx.check(
                "folded panels zigzag out of the frame plane",
                max(y_fold) > 0.02,
                details=f"max|y|={max(y_fold):.3f}",
            )
    else:
        pickets = [object_model.get_part(f"picket_{i}") for i in range(r.n_verts)]
        ctx.check(
            "all pickets present", all(p is not None for p in pickets), details=f"N+1={r.n_verts}"
        )
        ctx.check(
            "fold drive is REVOLUTE about -Y",
            abs(drive.axis[1]) > 0.99,
            details=f"axis={tuple(drive.axis)}",
        )

        def picket_pos() -> list[tuple[float, float, float]]:
            return [ctx.part_world_position(p) for p in pickets]

        pos_open = picket_pos()
        ctx.check(
            "leading picket anchored at lead_x",
            abs(pos_open[0][0] - r.lead_x) < 1e-4,
            details=f"x0={pos_open[0][0]}",
        )
        ctx.check(
            "deployed lattice spans most of the opening",
            pos_open[-1][0] > r.lead_x + 0.5 * (r.open_x1 - r.lead_x),
            details=f"trailing x={pos_open[-1][0]:.3f}",
        )
        ctx.check(
            "deployed picket pitch matches PITCH_OPEN",
            all(
                abs((pos_open[i + 1][0] - pos_open[i][0]) - r.pitch_open) < 1e-5
                for i in range(r.cell_count)
            ),
            details=f"pitches={[round(pos_open[i + 1][0] - pos_open[i][0], 4) for i in range(r.cell_count)]}",
        )
        ctx.check(
            "deployed lattice stays inside the right stile",
            pos_open[-1][0] <= r.open_x1 + 1e-4,
            details=f"trailing x={pos_open[-1][0]:.3f} open_x1={r.open_x1:.3f}",
        )

        # The lambda chain keeps every picket level + uniform pitch at EVERY pose.
        for frac, label in ((0.5, "half-folded"), (1.0, "fully folded")):
            with ctx.pose({drive: r.fold_angle * frac}):
                pos = picket_pos()
                ctx.check(
                    f"pickets stay level when {label}",
                    all(abs(p[2] - r.load_z) < 1e-4 for p in pos),
                    details=f"z-spread={max(abs(p[2] - r.load_z) for p in pos):.2e}",
                )
                expected = 2.0 * r.s_half * math.cos(r.theta0 + r.fold_angle * frac)
                ctx.check(
                    f"picket pitch contracts uniformly when {label}",
                    all(
                        abs((pos[i + 1][0] - pos[i][0]) - expected) < 1e-5
                        for i in range(r.cell_count)
                    ),
                    details=f"expected pitch={expected:.4f}",
                )
        with ctx.pose({drive: r.fold_angle}):
            pos_closed = picket_pos()
            ctx.check(
                "gate collapses toward the left stile",
                pos_closed[-1][0] < pos_open[-1][0] - 0.1,
                details=f"open_x={pos_open[-1][0]:.3f} closed_x={pos_closed[-1][0]:.3f}",
            )

    # ---- slot_choices recorded (with N encoded). ----
    ctx.check(
        "slot_choices recorded with cell_count encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "FoldingGateConfig",
    "ResolvedFoldingGateConfig",
    "build_folding_gate",
    "build_seeded_folding_gate",
    "config_from_seed",
    "resolve_config",
    "run_folding_gate_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
