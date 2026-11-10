# SPDX-License-Identifier: Apache-2.0

"""Modular template for AC OUTDOOR (condenser / condensing) units.

The outdoor condensing unit: a rectangular sheet-metal cabinet hollowed from the
back (-Y), with one or more circular axial-fan throats cut into the FRONT (+Y) or
TOP (+Z) face. Behind each throat spins an axial condenser fan rotor
(``FanRotorGeometry``) about the throat normal (CONTINUOUS). Each throat is
covered by a protective guard (concentric wire grille / rectangular louver
panel). The cabinet carries a side service access skin (panel or hinged door)
and exposed copper refrigerant service valves, and is carried by a mounting
support (floor angle-iron bracket / heavy wall brackets / floor feet).

This is the OUTDOOR unit and is deliberately distinct from the indoor wall-split
``air_conditioner`` slug: it reads as rotors + guard grilles + copper valves +
metal support bracket, with the primary motion = continuous axial fan spin (plus
a revolute side service door), not swinging louver vanes on a wall-hugging shell.

Slot graph (parallel children on a common ``housing`` + a ``fan_count``
multiplicity axis):

  Slot A  fan_discharge_layout : front_fan_row (N fans, +Y) | top_discharge_fan (1, +Z)
  Slot B  front_service_skin   : wire_ring_grille | louver_vent_panel | side_service_door
  Slot C  mounting_support     : angle_iron_bracket | wall_brackets | base_feet

5-star sources (synced into data/records/, rating 5):
  P1  rec_build-...-air-_..._0710784e   bracket-root single-fan family
  P2  rec_build-...-air-_..._0ffac329   housing-root dual-fan family
  S5  rec_ac_unit_var_three_fans        front_fan_row N=3 multiplicity loop
  S6  rec_ac_unit_var_top_discharge_fan top-discharge single fan
  S3  rec_ac_unit_var_louvered_front    louver_vent_panel (VentGrilleGeometry)
  S4  rec_ac_unit_var_side_service_door side_service_door (hinge barrels + cam latch)
  S7  rec_ac_unit_var_wall_brackets     wall_brackets x2 (shelf + gusset)
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    FanRotorBlade,
    FanRotorGeometry,
    FanRotorHub,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    VentGrilleFrame,
    VentGrilleGeometry,
    VentGrilleSleeve,
    VentGrilleSlats,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums.
# --------------------------------------------------------------------------- #

FanDischargeLayout = Literal["front_fan_row", "top_discharge_fan"]
FrontServiceSkin = Literal["wire_ring_grille", "louver_vent_panel", "side_service_door"]
MountingSupport = Literal["angle_iron_bracket", "wall_brackets", "base_feet"]
PaletteStyle = Literal[
    "white_steel",
    "cream_white",
    "beige_panel",
    "cool_grey",
    "panel_face_two_tone",
]

FAN_DISCHARGE_LAYOUTS: tuple[FanDischargeLayout, ...] = ("front_fan_row", "top_discharge_fan")
_LAYOUT_WEIGHTS = (0.70, 0.30)
FRONT_SERVICE_SKINS: tuple[FrontServiceSkin, ...] = (
    "wire_ring_grille",
    "louver_vent_panel",
    "side_service_door",
)
_SKIN_WEIGHTS = (0.40, 0.30, 0.30)
MOUNTING_SUPPORTS: tuple[MountingSupport, ...] = (
    "angle_iron_bracket",
    "wall_brackets",
    "base_feet",
)
_SUPPORT_WEIGHTS = (0.40, 0.30, 0.30)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "white_steel",
    "cream_white",
    "beige_panel",
    "cool_grey",
    "panel_face_two_tone",
)

# sweep/test multiplicity domain (product domain is [1, 20]; sweep covers [1, 5]).
_FAN_COUNTS = (1, 2, 3, 4, 5)
_FAN_COUNT_WEIGHTS = (0.16, 0.40, 0.24, 0.12, 0.08)
_FAN_BLADE_COUNTS = (3, 4, 5, 6)

# --------------------------------------------------------------------------- #
# Palette colorways (RGBA pulled from the 5-star samples).
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "white_steel": {
        "cabinet": (0.86, 0.85, 0.82, 1.0),
        "grille": (0.18, 0.18, 0.19, 1.0),
        "fan": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.35, 0.35, 0.37, 1.0),
        "panel": (0.78, 0.77, 0.74, 1.0),
        "copper": (0.62, 0.40, 0.22, 1.0),
        "badge": (0.62, 0.64, 0.66, 1.0),
    },
    "cream_white": {
        "cabinet": (0.880, 0.870, 0.815, 1.0),
        "grille": (0.930, 0.925, 0.905, 1.0),
        "fan": (0.855, 0.845, 0.800, 1.0),
        "steel": (0.300, 0.300, 0.310, 1.0),
        "panel": (0.815, 0.805, 0.755, 1.0),
        "copper": (0.66, 0.44, 0.26, 1.0),
        "badge": (0.620, 0.640, 0.660, 1.0),
    },
    "beige_panel": {
        "cabinet": (0.86, 0.85, 0.82, 1.0),
        "grille": (0.20, 0.20, 0.21, 1.0),
        "fan": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.32, 0.33, 0.36, 1.0),
        "panel": (0.80, 0.79, 0.75, 1.0),
        "copper": (0.62, 0.40, 0.22, 1.0),
        "badge": (0.60, 0.62, 0.64, 1.0),
    },
    "cool_grey": {
        "cabinet": (0.72, 0.73, 0.75, 1.0),
        "grille": (0.16, 0.16, 0.18, 1.0),
        "fan": (0.12, 0.12, 0.13, 1.0),
        "steel": (0.40, 0.40, 0.42, 1.0),
        "panel": (0.66, 0.67, 0.69, 1.0),
        "copper": (0.60, 0.42, 0.26, 1.0),
        "badge": (0.58, 0.60, 0.63, 1.0),
    },
    "panel_face_two_tone": {
        "cabinet": (0.880, 0.870, 0.815, 1.0),
        "grille": (0.20, 0.20, 0.22, 1.0),
        "fan": (0.10, 0.10, 0.11, 1.0),
        "steel": (0.300, 0.300, 0.310, 1.0),
        "panel": (0.500, 0.510, 0.530, 1.0),
        "copper": (0.62, 0.40, 0.22, 1.0),
        "badge": (0.620, 0.640, 0.660, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Fixed geometry constants (meters).
# --------------------------------------------------------------------------- #

WALL = 0.012            # sheet-metal apparent wall thickness
PANEL_BAND_W = 0.110    # left control-panel band width (X)
FAN_CTR_Z = 0.030       # front fan center height (slightly above mid-height)
FAN_GAP = 0.030         # min gap between adjacent front bores

# side service skin (panel/door)
SVC_PANEL_W = 0.170     # service skin extent along depth (+Y from hinge)
SVC_PANEL_H = 0.300     # service skin height (Z)
SVC_PANEL_TH = 0.010    # service skin thickness (X)
POCKET_DEPTH = 0.008    # recessed service pocket depth (< WALL, leaves a solid floor)

# angle-iron bracket
BRACKET_LEG_H = 0.150
BRACKET_ANGLE = 0.035

# wall brackets
WB_PLATE_W = 0.060
WB_PLATE_TH = 0.008
WB_WALL_H = 0.300
WB_SHELF_TH = 0.010
WB_GUSSET_TH = 0.006
WB_GUSSET_DROP = 0.230
WB_INSET = 0.080
WB_LIP_H = 0.018

# louver panel
LOUVER_FRAME = 0.014
LOUVER_FACE_TH = 0.004
LOUVER_DUCT_DEPTH = 0.028

_ROT_Z_TO_Y = Origin(rpy=(-math.pi / 2.0, 0.0, 0.0))  # local +Z -> world +Y


# --------------------------------------------------------------------------- #
# Config dataclasses.
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class ACOutdoorUnitConfig:
    """Public configuration sampled by ``config_from_seed`` or supplied directly."""

    fan_discharge_layout: FanDischargeLayout = "front_fan_row"
    front_service_skin: FrontServiceSkin = "wire_ring_grille"
    mounting_support: MountingSupport = "angle_iron_bracket"
    palette_style: PaletteStyle = "white_steel"
    fan_count: int = 2
    fan_blade_count: int = 4
    body_w: float = 0.860
    body_h: float = 0.520
    body_d: float = 0.300
    fan_bore_r: float = 0.150
    grille_ring_count: int = 4
    louver_slat_pitch: float = 0.022
    fan_velocity: float = 20.0
    name: str = "reference_ac_outdoor_unit"


@dataclass(frozen=True)
class ResolvedACOutdoorUnitConfig:
    fan_discharge_layout: FanDischargeLayout
    front_service_skin: FrontServiceSkin
    mounting_support: MountingSupport
    palette_style: PaletteStyle
    fan_count: int
    fan_blade_count: int
    body_w: float
    body_h: float
    body_d: float
    fan_bore_r: float
    grille_ring_count: int
    louver_slat_pitch: float
    fan_velocity: float
    name: str
    # derived
    palette: dict[str, tuple[float, float, float, float]]
    fan_x_positions: tuple[float, ...]
    front_y: float
    has_service_skin: bool      # is there a side panel/door + valves?
    is_door: bool               # side skin is a hinged service_door (vs flat panel)


# --------------------------------------------------------------------------- #
# Sampling.
# --------------------------------------------------------------------------- #


def _clamp(value: float, lo: float, hi: float) -> float:
    if lo > hi:
        lo, hi = hi, lo
    return max(lo, min(hi, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ACOutdoorUnitConfig:
    """Deterministic per-seed procedural sampling (seed=0 is not special).

    Order: A (layout) -> fan_count -> fan_blade_count -> B (skin) -> C (support)
    -> palette -> independent continuous scales. Compatibility gating
    (top_discharge => fan_count=1; louver => fan_count=1 else fallback) is
    enforced in ``resolve_config``.
    """
    rng = random.Random(seed)

    layout: FanDischargeLayout = rng.choices(
        FAN_DISCHARGE_LAYOUTS, weights=_LAYOUT_WEIGHTS, k=1
    )[0]
    if layout == "top_discharge_fan":
        fan_count = 1
    else:
        fan_count = rng.choices(_FAN_COUNTS, weights=_FAN_COUNT_WEIGHTS, k=1)[0]
    fan_blade_count = rng.choice(_FAN_BLADE_COUNTS)

    skin: FrontServiceSkin = rng.choices(FRONT_SERVICE_SKINS, weights=_SKIN_WEIGHTS, k=1)[0]
    support: MountingSupport = rng.choices(MOUNTING_SUPPORTS, weights=_SUPPORT_WEIGHTS, k=1)[0]
    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    body_h = round(rng.uniform(0.48, 0.56), 4)
    body_d = round(rng.uniform(0.27, 0.34), 4)
    fan_bore_r = round(rng.uniform(0.125, 0.165), 4)
    grille_ring_count = rng.choice((3, 4, 5))
    louver_slat_pitch = round(rng.uniform(0.018, 0.028), 4)
    fan_velocity = round(rng.uniform(15.0, 120.0), 2)

    # body_w is derived from fan_count in resolve_config; seed a nominal value.
    body_w = round(rng.uniform(0.78, 1.25), 4)

    return ACOutdoorUnitConfig(
        fan_discharge_layout=layout,
        front_service_skin=skin,
        mounting_support=support,
        palette_style=palette,
        fan_count=fan_count,
        fan_blade_count=fan_blade_count,
        body_w=body_w,
        body_h=body_h,
        body_d=body_d,
        fan_bore_r=fan_bore_r,
        grille_ring_count=grille_ring_count,
        louver_slat_pitch=louver_slat_pitch,
        fan_velocity=fan_velocity,
        name=f"seeded_ac_outdoor_unit_{seed}",
    )


def resolve_config(config: ACOutdoorUnitConfig) -> ResolvedACOutdoorUnitConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    layout = _pick(config.fan_discharge_layout, FAN_DISCHARGE_LAYOUTS)
    skin = _pick(config.front_service_skin, FRONT_SERVICE_SKINS)
    support = _pick(config.mounting_support, MOUNTING_SUPPORTS)

    fan_blade_count = int(config.fan_blade_count)
    if fan_blade_count not in _FAN_BLADE_COUNTS:
        fan_blade_count = 4

    # --- multiplicity gating ------------------------------------------------ #
    fan_count = int(config.fan_count)
    if layout == "top_discharge_fan":
        fan_count = 1
    fan_count = max(1, min(20, fan_count))

    # --- skin compatibility gating ------------------------------------------ #
    # louver is a single rectangular panel covering one bore: only valid for a
    # single-bore front row. top_discharge has no front bore for a louver panel.
    if skin == "louver_vent_panel" and (layout == "top_discharge_fan" or fan_count != 1):
        skin = "wire_ring_grille"

    body_h = _clamp(config.body_h, 0.48, 0.56)
    body_d = _clamp(config.body_d, 0.27, 0.34)

    if layout == "top_discharge_fan":
        # Single top fan: bore must fit within the top face min(W,D)/2.
        body_w = _clamp(config.body_w, 0.78, 0.95)
        fan_bore_r = _clamp(config.fan_bore_r, 0.110, 0.150)
        max_top_r = min(body_w, body_d) / 2.0 - 0.030
        fan_bore_r = min(fan_bore_r, max(0.080, max_top_r))
        fan_x_positions: tuple[float, ...] = (0.0,)
        front_y = body_d / 2.0
    else:
        fan_bore_r = _clamp(config.fan_bore_r, 0.125, 0.165)
        # usable span (right of the left control-panel band) must fit N bores.
        # body_w derived from fan_count so the row always fits with clearance.
        edge = 0.020
        needed = PANEL_BAND_W + 2.0 * edge + fan_count * (2.0 * fan_bore_r + FAN_GAP)
        body_w = _clamp(max(config.body_w, needed), 0.78, 2.0)
        # Recompute usable span and shrink bore if (for big N) it still won't fit.
        usable0 = -body_w / 2.0 + PANEL_BAND_W
        usable1 = body_w / 2.0 - edge
        span = usable1 - usable0
        max_bore_r = 0.5 * (span / fan_count - FAN_GAP)
        if max_bore_r < fan_bore_r:
            fan_bore_r = max(0.060, max_bore_r)
        fan_x_positions = tuple(
            usable0 + span * (i + 0.5) / fan_count for i in range(fan_count)
        )
        front_y = body_d / 2.0

    grille_ring_count = int(config.grille_ring_count)
    if grille_ring_count not in (3, 4, 5):
        grille_ring_count = 4
    louver_slat_pitch = _clamp(config.louver_slat_pitch, 0.018, 0.028)
    fan_velocity = _clamp(config.fan_velocity, 15.0, 120.0)

    # Side service skin + valves: present for the bracket / wall families (P1
    # heritage). The floor-feet (P2) family omits them, matching the source.
    has_service_skin = support != "base_feet"
    is_door = has_service_skin and skin == "side_service_door"

    return ResolvedACOutdoorUnitConfig(
        fan_discharge_layout=layout,
        front_service_skin=skin,
        mounting_support=support,
        palette_style=config.palette_style,
        fan_count=fan_count,
        fan_blade_count=fan_blade_count,
        body_w=round(body_w, 4),
        body_h=body_h,
        body_d=body_d,
        fan_bore_r=round(fan_bore_r, 4),
        grille_ring_count=grille_ring_count,
        louver_slat_pitch=louver_slat_pitch,
        fan_velocity=fan_velocity,
        name=config.name,
        palette=dict(PALETTES[config.palette_style]),
        fan_x_positions=fan_x_positions,
        front_y=front_y,
        has_service_skin=has_service_skin,
        is_door=is_door,
    )


# --------------------------------------------------------------------------- #
# Geometry helpers.
# --------------------------------------------------------------------------- #


def _housing_shell(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Hollow sheet-metal cabinet: closed sides/top/floor, open back (-Y), with
    fan throats cut into the front (+Y) or top (+Z) face, and (for the service
    families) a shallow recessed pocket on the right (+X) side."""
    W, D, H = r.body_w, r.body_d, r.body_h
    # No corner fillet on the hollow multi-cut shell: filleting a booleaned solid
    # is the dominant compile cost; a crisp rectangular cabinet is fine.
    outer = cq.Workplane("XY").box(W, D, H)
    # Hollow from the open back face (-Y), leaving real wall thickness.
    inner = cq.Workplane("XY").box(W - 2 * WALL, D - WALL, H - 2 * WALL)
    inner = inner.translate((0.0, -WALL / 2.0, 0.0))
    shell = outer.cut(inner)

    # Top cover overhang lip (reads as a separate flat lid; no fillet for speed).
    # Union it BEFORE the throat/pocket cuts so a top-discharge bore is cut
    # THROUGH the lid -- otherwise the full-span lid re-seals the top throat.
    lid = (
        cq.Workplane("XY", origin=(0.0, 0.0, H / 2.0 + 0.002))
        .box(W + 0.018, D + 0.018, 0.014)
    )
    shell = shell.union(lid)

    if r.fan_discharge_layout == "front_fan_row":
        for cx in r.fan_x_positions:
            bore = cq.Solid.makeCylinder(
                r.fan_bore_r,
                D,
                pnt=cq.Vector(cx, D / 2.0 + 0.001, FAN_CTR_Z),
                dir=cq.Vector(0.0, -1.0, 0.0),
            )
            shell = shell.cut(cq.Workplane("XY").add(bore))
    else:  # top_discharge_fan
        top_cut = cq.Solid.makeCylinder(
            r.fan_bore_r,
            WALL + 0.012,
            pnt=cq.Vector(0.0, 0.0, H / 2.0 - WALL - 0.002),
            dir=cq.Vector(0.0, 0.0, 1.0),
        )
        shell = shell.cut(cq.Workplane("XY").add(top_cut))

    if r.has_service_skin:
        pocket = (
            cq.Workplane("YZ")
            .workplane(offset=W / 2.0 + 0.001)
            .rect(SVC_PANEL_W + 0.010, SVC_PANEL_H + 0.010)
            .extrude(-POCKET_DEPTH)
        )
        shell = shell.cut(pocket)

    # Left control-panel raised band on the front face (front-row only; the top
    # face has no front control band station). Start inside the front skin.
    if r.fan_discharge_layout == "front_fan_row":
        panel_cx = -W / 2.0 + PANEL_BAND_W / 2.0
        frame = (
            cq.Workplane("XZ", origin=(panel_cx, D / 2.0 - WALL, FAN_CTR_Z))
            .rect(PANEL_BAND_W - 0.012, H - 0.080)
            .extrude(-(WALL + 0.006))
        )
        shell = shell.union(frame)

    return shell


def _front_shroud_ring(cx: float, r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Raised venturi flow-ring framing a front (+Y) fan throat."""
    D = r.body_d
    y0 = D / 2.0 - 0.004
    outer = cq.Solid.makeCylinder(
        r.fan_bore_r + 0.020, 0.026,
        pnt=cq.Vector(cx, y0, FAN_CTR_Z), dir=cq.Vector(0.0, 1.0, 0.0),
    )
    bore = cq.Solid.makeCylinder(
        r.fan_bore_r, 0.040,
        pnt=cq.Vector(cx, y0 - 0.005, FAN_CTR_Z), dir=cq.Vector(0.0, 1.0, 0.0),
    )
    return cq.Workplane("XY").add(outer).cut(cq.Workplane("XY").add(bore))


def _top_shroud_ring(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Raised venturi flow-ring framing the top (+Z) fan throat."""
    H = r.body_h
    z0 = H / 2.0 - 0.004
    outer = cq.Solid.makeCylinder(
        r.fan_bore_r + 0.020, 0.026,
        pnt=cq.Vector(0.0, 0.0, z0), dir=cq.Vector(0.0, 0.0, 1.0),
    )
    bore = cq.Solid.makeCylinder(
        r.fan_bore_r, 0.040,
        pnt=cq.Vector(0.0, 0.0, z0 - 0.005), dir=cq.Vector(0.0, 0.0, 1.0),
    )
    return cq.Workplane("XY").add(outer).cut(cq.Workplane("XY").add(bore))


def _front_motor_mount(cx: float, r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Rear motor pod + 3-arm spider grounding a front rotor WITHOUT crossing the
    throat face.

    The motor can hangs on the axis BEHIND the rotor; three thin radial arms
    (angled so none is horizontal) seat it on the recessed duct sleeve; a stub
    shaft runs forward into the rotor hub bore (captured fit, no float). Because
    every part lives behind the rotor plane, nothing reads as a bar across the
    fan the way the old front cross-strut did.
    """
    D = r.body_d
    rotor_y = D / 2.0 - 0.015            # rotor plane
    support_y = rotor_y - 0.024          # spider plane, behind the rotor
    bore_r = r.fan_bore_r
    boss_r = _clamp(bore_r * 0.20, 0.022, 0.030)
    solids: list[cq.Solid] = []
    # Motor can on the axis, fully behind the rotor.
    can_len = 0.050
    can_back = support_y - 0.026
    can_front = can_back + can_len
    solids.append(cq.Solid.makeCylinder(
        boss_r, can_len, pnt=cq.Vector(cx, can_back, FAN_CTR_Z), dir=cq.Vector(0.0, 1.0, 0.0)))
    # Output shaft forward into the rotor hub bore (captured fit; ends at the hub,
    # never past the rotor front face -> no poke-through the grille).
    solids.append(cq.Solid.makeCylinder(
        0.008, (rotor_y + 0.004) - (can_front - 0.002),
        pnt=cq.Vector(cx, can_front - 0.002, FAN_CTR_Z), dir=cq.Vector(0.0, 1.0, 0.0)))
    # Three radial spider arms at the support plane, seating the pod on the duct
    # sleeve (tips reach the bore wall for a solid connection). The +90deg base
    # angle keeps every arm off the horizontal so the support never reads as a
    # bar across the throat.
    arm_out = bore_r
    for k in range(3):
        ang = math.pi / 2.0 + 2.0 * math.pi * k / 3.0
        bar = cq.Solid.makeBox(
            arm_out, 0.009, 0.011,
            pnt=cq.Vector(cx, support_y - 0.0045, FAN_CTR_Z - 0.0055))
        bar = bar.rotate(
            cq.Vector(cx, support_y, FAN_CTR_Z),
            cq.Vector(cx, support_y + 1.0, FAN_CTR_Z),
            math.degrees(ang))
        solids.append(bar)
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)
    return cq.Workplane("XY").add(fused)


def _front_duct_sleeve(cx: float, r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Short dark venturi duct lining a front throat so the opening reads as a
    deep OPEN air path (not a flat sealed disc), and the fan spider seats on it.

    The tube bites 1 mm into the shell bore for connectivity; its bore is wider
    than the rotor tip so the rotor spins freely just inside the duct mouth."""
    D = r.body_d
    y_front = D / 2.0  # flush with the front outer face -> overlaps the full skin
    depth = 0.060
    outer = cq.Solid.makeCylinder(
        r.fan_bore_r + 0.001, depth,
        pnt=cq.Vector(cx, y_front, FAN_CTR_Z), dir=cq.Vector(0.0, -1.0, 0.0))
    inner = cq.Solid.makeCylinder(
        r.fan_bore_r - 0.004, depth + 0.004,
        pnt=cq.Vector(cx, y_front + 0.002, FAN_CTR_Z), dir=cq.Vector(0.0, -1.0, 0.0))
    return cq.Workplane("XY").add(outer).cut(cq.Workplane("XY").add(inner))


def _top_motor_mount(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Rear motor pod + 3-arm spider hung BELOW a top throat, grounding the rotor
    without any cross-bar spanning the opening (mirror of the front mount)."""
    H = r.body_h
    rotor_z = H / 2.0 - 0.018
    support_z = rotor_z - 0.024
    bore_r = r.fan_bore_r
    boss_r = _clamp(bore_r * 0.20, 0.022, 0.030)
    solids: list[cq.Solid] = []
    can_len = 0.050
    can_bottom = support_z - 0.026
    can_top = can_bottom + can_len
    solids.append(cq.Solid.makeCylinder(
        boss_r, can_len, pnt=cq.Vector(0.0, 0.0, can_bottom), dir=cq.Vector(0.0, 0.0, 1.0)))
    solids.append(cq.Solid.makeCylinder(
        0.008, (rotor_z + 0.004) - (can_top - 0.002),
        pnt=cq.Vector(0.0, 0.0, can_top - 0.002), dir=cq.Vector(0.0, 0.0, 1.0)))
    arm_out = bore_r
    for k in range(3):
        ang = math.pi / 2.0 + 2.0 * math.pi * k / 3.0
        bar = cq.Solid.makeBox(
            arm_out, 0.011, 0.009,
            pnt=cq.Vector(0.0, -0.0055, support_z - 0.0045))
        bar = bar.rotate(
            cq.Vector(0.0, 0.0, support_z),
            cq.Vector(0.0, 0.0, support_z + 1.0),
            math.degrees(ang))
        solids.append(bar)
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)
    return cq.Workplane("XY").add(fused)


def _top_duct_sleeve(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Short dark venturi duct lining the top throat (mirror of the front duct)."""
    H = r.body_h
    z_top = H / 2.0  # flush with the top outer face -> overlaps the full skin
    depth = 0.060
    outer = cq.Solid.makeCylinder(
        r.fan_bore_r + 0.001, depth,
        pnt=cq.Vector(0.0, 0.0, z_top), dir=cq.Vector(0.0, 0.0, -1.0))
    inner = cq.Solid.makeCylinder(
        r.fan_bore_r - 0.004, depth + 0.004,
        pnt=cq.Vector(0.0, 0.0, z_top + 0.002), dir=cq.Vector(0.0, 0.0, -1.0))
    return cq.Workplane("XY").add(outer).cut(cq.Workplane("XY").add(inner))


def _fan_rotor_mesh(name: str, r: ResolvedACOutdoorUnitConfig):
    """Axial condenser fan rotor (spins about local +Z, FanRotorGeometry)."""
    rotor = FanRotorGeometry(
        r.fan_bore_r - 0.008,       # outer radius just inside the bore
        max(0.024, r.fan_bore_r * 0.20),  # hub radius
        r.fan_blade_count,
        thickness=0.020,
        blade_pitch_deg=26.0,
        blade_sweep_deg=18.0,
        blade=FanRotorBlade(shape="broad", camber=0.11),
        hub=FanRotorHub(style="domed", bore_diameter=0.012),
        center=True,
    )
    return mesh_from_geometry(rotor, name)


def _wire_grille_solids(bore_r: float, rings: int, z_front: float):
    """Shared protective wire grille built in a +Z-tube-axis local frame at the
    grille plane z=z_front: concentric flat annular rings (cheap to tessellate vs
    tori) + 4 diametral spokes + center boss + 4 rim mounting tabs reaching back
    to z=0 (into the shroud). Returns a list of cq.Solid (caller orients them)."""
    wire_t = 0.007  # ring radial wall (flat annulus)
    ring_face_t = 0.006  # ring thickness along the tube axis (+Z)
    solids: list[cq.Solid] = []
    for i in range(rings):
        rr = bore_r * (i + 1) / rings
        ring = (
            cq.Workplane("XY", origin=(0.0, 0.0, z_front))
            .circle(rr + wire_t * 0.5).circle(max(0.001, rr - wire_t * 0.5))
            .extrude(ring_face_t)
        )
        solids.append(ring.val())
    # Diametral spokes (4) tying rings to center; thin bars across the opening.
    for k in range(4):
        ang = math.pi * k / 4.0
        dx, dy = math.cos(ang), math.sin(ang)
        bar = cq.Solid.makeBox(
            2.0 * bore_r, 0.008, ring_face_t,
            pnt=cq.Vector(-bore_r, -0.004, z_front))
        bar = bar.rotate(
            cq.Vector(0, 0, z_front), cq.Vector(0, 0, z_front + 1.0), math.degrees(ang))
        solids.append(bar)
    # Center boss overlapping the spokes -> one connected island. It reaches from
    # the mounting plane (z=0, the joint origin) up past the grille plane so the
    # child-frame origin sits on real boss geometry (joint-origin baseline).
    solids.append(cq.Solid.makeCylinder(
        max(0.020, bore_r * 0.16), z_front + 0.010,
        pnt=cq.Vector(0.0, 0.0, 0.0), dir=cq.Vector(0.0, 0.0, 1.0)))
    # Four rim mounting tabs reaching back (-Z) into the shroud ring.
    tab_r = bore_r + 0.006
    for k in range(4):
        ang = math.pi / 4.0 + math.pi * k / 2.0
        tx, ty = math.cos(ang) * tab_r, math.sin(ang) * tab_r
        solids.append(cq.Solid.makeCylinder(
            0.007, z_front + ring_face_t,
            pnt=cq.Vector(tx, ty, 0.0), dir=cq.Vector(0.0, 0.0, 1.0)))
    return solids


def _wire_grille_front(cx: float, r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Front (+Y normal) wire grille: build in a +Z local frame, then rotate the
    tube axis to +Y. The FIXED joint places it on the front throat."""
    solids = _wire_grille_solids(r.fan_bore_r, r.grille_ring_count, 0.024)
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)
    # Rotate local +Z (tube axis) to world +Y: rotate -90deg about X.
    fused = fused.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), -90.0)
    return cq.Workplane("XY").add(fused)


def _wire_grille_top(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Top (+Z normal) wire grille: built directly in the +Z local frame."""
    solids = _wire_grille_solids(r.fan_bore_r, r.grille_ring_count, 0.020)
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)
    return cq.Workplane("XY").add(fused)


def _louver_panel_geometry(r: ResolvedACOutdoorUnitConfig) -> VentGrilleGeometry:
    """Rectangular louvered front grille (VentGrilleGeometry) for single-bore row.

    Local XY plane extending +Z; the visual origin rotates the face into XZ
    facing +Y, sleeve extending -Y into the housing shroud.
    """
    panel_w = max(0.36, 2.0 * r.fan_bore_r + 0.140)
    panel_h = max(0.36, 2.0 * r.fan_bore_r + 0.130)
    return VentGrilleGeometry(
        (panel_w, panel_h),
        frame=LOUVER_FRAME,
        face_thickness=LOUVER_FACE_TH,
        duct_depth=LOUVER_DUCT_DEPTH,
        duct_wall=0.003,
        slat_pitch=r.louver_slat_pitch,
        slat_width=0.012,
        slat_angle_deg=35.0,
        corner_radius=0.005,
        slats=VentGrilleSlats(
            profile="flat", direction="down", divider_count=1, divider_width=0.005),
        frame_profile=VentGrilleFrame(style="radiused", depth=0.002),
        sleeve=VentGrilleSleeve(style="short"),
        center=True,
    )


def _service_panel_mesh() -> cq.Workplane:
    """Flat hinged sheet-metal service cover. Hinge along local Z at origin,
    panel extends +Y, thin along X (outward normal)."""
    panel = (
        cq.Workplane("XY")
        .box(SVC_PANEL_TH, SVC_PANEL_W, SVC_PANEL_H, centered=(True, False, True))
        .edges("|X").fillet(0.006)
    )
    pull = (
        cq.Workplane("XY")
        .box(0.006, 0.040, 0.060, centered=(True, False, True))
        .translate((SVC_PANEL_TH / 2.0, SVC_PANEL_W - 0.040, 0.0))
    )
    return panel.union(pull)


def _door_latch_mesh() -> cq.Workplane:
    """Quarter-turn cam latch near the door free (+Y) edge, protruding +X."""
    latch_y = SVC_PANEL_W - 0.040
    face_x = SVC_PANEL_TH / 2.0
    body = cq.Solid.makeCylinder(
        0.012, 0.010, pnt=cq.Vector(face_x, latch_y, 0.0), dir=cq.Vector(1.0, 0.0, 0.0))
    tab = cq.Solid.makeBox(
        0.004, 0.030, 0.010, pnt=cq.Vector(face_x + 0.010, latch_y - 0.015, -0.005))
    washer = cq.Solid.makeCylinder(
        0.015, 0.002, pnt=cq.Vector(face_x - 0.001, latch_y, 0.0), dir=cq.Vector(1.0, 0.0, 0.0))
    return cq.Workplane("XY").add(body.fuse(tab).fuse(washer))


def _hinge_barrels_mesh(r: ResolvedACOutdoorUnitConfig, hinge_x: float, hinge_y: float):
    """Two visible hinge barrel knuckles (barrel + leaf + pin cap) on the housing
    side wall at the service-door hinge line. Authored in housing part frame."""
    W = r.body_w
    barrel_r = 0.007
    barrel_len = 0.038
    leaf_width = W / 2.0 - hinge_x + barrel_r
    leaf_thick = 0.020
    solids: list[cq.Solid] = []
    for zc in (SVC_PANEL_H * 0.35, -SVC_PANEL_H * 0.35):
        solids.append(cq.Solid.makeCylinder(
            barrel_r, barrel_len,
            pnt=cq.Vector(hinge_x, hinge_y, zc - barrel_len / 2.0), dir=cq.Vector(0.0, 0.0, 1.0)))
        solids.append(cq.Solid.makeBox(
            leaf_width, leaf_thick, barrel_len,
            pnt=cq.Vector(hinge_x, hinge_y - leaf_thick / 2.0, zc - barrel_len / 2.0)))
        solids.append(cq.Solid.makeCylinder(
            barrel_r + 0.002, 0.003,
            pnt=cq.Vector(hinge_x, hinge_y, zc + barrel_len / 2.0), dir=cq.Vector(0.0, 0.0, 1.0)))
    fused = solids[0]
    for s in solids[1:]:
        fused = fused.fuse(s)
    return cq.Workplane("XY").add(fused)


def _refrigerant_lines_mesh() -> cq.Workplane:
    """Two copper service valves / stub lines, authored around the PART ORIGIN
    so the FIXED joint origin lands on the geometry. The part origin sits at the
    valve-body root on the side wall; stubs point out +X, manifold ties them.
    Vertical spread along Z is centered on 0."""
    lines = None

    def _add(wp):
        nonlocal lines
        lines = wp if lines is None else lines.union(wp)

    for zc in (-0.022, 0.022):
        stub = cq.Solid.makeCylinder(
            0.009, 0.060, pnt=cq.Vector(-0.012, 0.0, zc), dir=cq.Vector(1.0, 0.0, 0.0))
        _add(cq.Workplane("XY").add(stub))
        valve = cq.Solid.makeCylinder(
            0.015, 0.026, pnt=cq.Vector(-0.012, 0.0, zc), dir=cq.Vector(1.0, 0.0, 0.0))
        _add(cq.Workplane("XY").add(valve))
    manifold = cq.Solid.makeCylinder(
        0.008, 0.058, pnt=cq.Vector(0.0, 0.0, -0.029), dir=cq.Vector(0.0, 0.0, 1.0))
    _add(cq.Workplane("XY").add(manifold))
    return lines


def _badge_mesh(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Small rating-label badge on the left control-panel band (front face)."""
    W = r.body_w
    D = r.body_d
    panel_cx = -W / 2.0 + PANEL_BAND_W / 2.0
    badge = (
        cq.Workplane("XZ", origin=(panel_cx, D / 2.0 + 0.004, FAN_CTR_Z + 0.120))
        .rect(0.055, 0.040)
        .extrude(-0.006)
    )
    return badge


# --- Mounting support meshes ----------------------------------------------- #


def _angle_iron_bracket_mesh(r: ResolvedACOutdoorUnitConfig, z_top: float) -> cq.Workplane:
    """Floor angle-iron support: 2 L legs (along Y) + foot/top flange + front/rear
    cross rails. Authored so the shelf/top flange sits at ``z_top`` (the housing
    bottom-seat height = +H/2), reaching down to the floor. This puts real bracket
    hardware at the FIXED joint origin (0,0,z_top)."""
    W, D = r.body_w, r.body_d
    leg_w = BRACKET_ANGLE
    leg_t = 0.006
    rail_t = 0.006
    inset = 0.060
    leg_bottom = z_top - BRACKET_LEG_H
    parts = None

    def _add(wp):
        nonlocal parts
        parts = wp if parts is None else parts.union(wp)

    for sign in (-1.0, 1.0):
        x0 = sign * (W / 2.0 - inset)
        web = (cq.Workplane("XY").box(leg_t, D + 0.040, BRACKET_LEG_H)
               .translate((x0, 0.0, z_top - BRACKET_LEG_H / 2.0)))
        _add(web)
        foot = (cq.Workplane("XY").box(leg_w, D + 0.040, leg_t)
                .translate((x0 + sign * leg_w / 2.0, 0.0, leg_bottom + leg_t / 2.0)))
        _add(foot)
        top = (cq.Workplane("XY").box(leg_w, D + 0.040, leg_t)
               .translate((x0 + sign * leg_w / 2.0, 0.0, z_top - leg_t / 2.0)))
        _add(top)
    for yy in (D / 2.0 - 0.010, -(D / 2.0 - 0.010)):
        rail = (cq.Workplane("XY").box(W - 2 * inset + leg_w, rail_t, leg_w)
                .translate((0.0, yy, leg_bottom + leg_w / 2.0)))
        _add(rail)
    # Top mounting rail spanning the full width at the shelf line (z_top), passing
    # through the center so the housing FIXED joint origin (0,0,z_top) lands on it.
    top_rail = (cq.Workplane("XY").box(W - 2 * inset + leg_w, 0.030, leg_t)
                .translate((0.0, 0.0, z_top - leg_t / 2.0)))
    _add(top_rail)
    return parts


def _one_wall_bracket(x0: float, shelf_d: float, z_top: float) -> cq.Workplane:
    """One heavy wall bracket centered at X=x0 with shelf top at ``z_top``: shelf
    + vertical wall plate (down from shelf at -Y edge) + triangular gusset +
    front stop + bolt holes."""
    half_d = shelf_d / 2.0
    result = None

    def _add(wp):
        nonlocal result
        result = wp if result is None else result.union(wp)

    shelf = (cq.Workplane("XY").box(WB_PLATE_W, shelf_d, WB_SHELF_TH)
             .translate((x0, 0.0, z_top - WB_SHELF_TH / 2.0)))
    _add(shelf)
    wp_y = -half_d + WB_PLATE_TH / 2.0
    wall_plate = (cq.Workplane("XY").box(WB_PLATE_W, WB_PLATE_TH, WB_WALL_H)
                  .translate((x0, wp_y, z_top - WB_WALL_H / 2.0)))
    _add(wall_plate)
    y_a = -half_d + WB_PLATE_TH
    z_a = z_top - WB_SHELF_TH
    z_b = z_top - WB_GUSSET_DROP
    y_c = half_d - 0.020
    gusset = (cq.Workplane("YZ")
              .moveTo(y_a, z_a).lineTo(y_a, z_b).lineTo(y_c, z_a).close()
              .extrude(WB_GUSSET_TH)
              .translate((x0 - WB_GUSSET_TH / 2.0, 0.0, 0.0)))
    _add(gusset)
    stop = (cq.Workplane("XY").box(WB_PLATE_W, WB_PLATE_TH, WB_LIP_H)
            .translate((x0, half_d - WB_PLATE_TH / 2.0, z_top - WB_SHELF_TH - WB_LIP_H / 2.0)))
    _add(stop)
    for z_hole in (z_top - 0.060, z_top - 0.200):
        hole = cq.Solid.makeCylinder(
            0.006, WB_PLATE_TH + 0.020,
            pnt=cq.Vector(x0, -half_d - 0.010, z_hole), dir=cq.Vector(0.0, 1.0, 0.0))
        result = result.cut(cq.Workplane("XY").add(hole))
    return result


def _wall_brackets_mesh(r: ResolvedACOutdoorUnitConfig, z_top: float) -> cq.Workplane:
    """Two heavy wall brackets at ±spacing/2 joined by a cross-rail at the shelf
    line ``z_top`` (= +H/2). ONE part: the rail at (0,0,z_top) carries the
    FIXED housing joint origin so it lands on real connecting geometry."""
    D = r.body_d
    shelf_d = D + 0.020
    spacing = max(0.20, r.body_w - 2.0 * WB_INSET)
    left = _one_wall_bracket(-spacing / 2.0, shelf_d, z_top)
    right = _one_wall_bracket(spacing / 2.0, shelf_d, z_top)
    support = left.union(right)
    rail = (cq.Workplane("XY")
            .box(spacing, 0.030, WB_SHELF_TH)
            .translate((0.0, 0.0, z_top - WB_SHELF_TH / 2.0)))
    support = support.union(rail)
    return support


def _base_feet_mesh(r: ResolvedACOutdoorUnitConfig) -> cq.Workplane:
    """Four dark floor feet under the cabinet (housing visual; no support part)."""
    W, D, H = r.body_w, r.body_d, r.body_h
    foot = None
    fz = -H / 2.0 - 0.011
    for fx in (-W * 0.40, W * 0.40):
        for fy in (-D * 0.32, D * 0.32):
            f = (cq.Workplane("XY", origin=(fx, fy, fz))
                 .box(0.060, 0.040, 0.022).edges("|Z").fillet(0.004))
            foot = f if foot is None else foot.union(f)
    return foot


# --------------------------------------------------------------------------- #
# Build.
# --------------------------------------------------------------------------- #


def _materials(model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig) -> dict:
    out = {}
    for key, rgba in r.palette.items():
        out[key] = model.material(f"acou_{key}_{r.palette_style}", rgba=rgba)
    return out


def _add_housing(model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig, mats: dict):
    """Build the housing part (root for base_feet; child of support otherwise).

    Returns the housing part. Front skin (grille/louver/door), fans, valves are
    added by their slot builders.
    """
    W, D, H = r.body_w, r.body_d, r.body_h
    zc = H / 2.0  # housing sits with its bottom at z=0 (center at +H/2 in part frame)
    housing = model.part("housing")

    def _hv(wp):
        return wp.translate((0.0, 0.0, zc))

    housing.visual(
        mesh_from_cadquery(_hv(_housing_shell(r)), "housing_shell"),
        material=mats["cabinet"], name="housing_shell", material_class_id="metal.paint_coated",
    )
    # Shroud ring(s) framing each throat (cabinet metal).
    if r.fan_discharge_layout == "front_fan_row":
        for i, cx in enumerate(r.fan_x_positions):
            housing.visual(
                mesh_from_cadquery(_hv(_front_shroud_ring(cx, r)), f"fan_shroud_ring_{i}"),
                material=mats["cabinet"], name=f"fan_shroud_ring_{i}", material_class_id="metal.paint_coated",
            )
            housing.visual(
                mesh_from_cadquery(_hv(_front_duct_sleeve(cx, r)), f"fan_duct_{i}"),
                material=mats["fan"], name=f"fan_duct_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                mesh_from_cadquery(_hv(_front_motor_mount(cx, r)), f"fan_motor_mount_{i}"),
                material=mats["steel"], name=f"fan_motor_mount_{i}", material_class_id="metal.steel_bare",
            )
        housing.visual(
            mesh_from_cadquery(_hv(_badge_mesh(r)), "rating_badge"),
            material=mats["badge"], name="rating_badge", material_class_id="metal.brushed_silver",
        )
    else:
        housing.visual(
            mesh_from_cadquery(_hv(_top_shroud_ring(r)), "fan_shroud_ring_0"),
            material=mats["cabinet"], name="fan_shroud_ring_0", material_class_id="metal.paint_coated",
        )
        housing.visual(
            mesh_from_cadquery(_hv(_top_duct_sleeve(r)), "fan_duct_0"),
            material=mats["fan"], name="fan_duct_0", material_class_id="plastic.opaque_glossy_molded",
        )
        housing.visual(
            mesh_from_cadquery(_hv(_top_motor_mount(r)), "fan_motor_mount_0"),
            material=mats["steel"], name="fan_motor_mount_0", material_class_id="metal.steel_bare",
        )

    # base_feet: feet are housing visuals (floor family, no support part).
    if r.mounting_support == "base_feet":
        housing.visual(
            mesh_from_cadquery(_hv(_base_feet_mesh(r)), "mount_feet"),
            material=mats["steel"], name="mount_feet", material_class_id="metal.steel_bare",
        )

    housing.inertial = Inertial.from_geometry(
        Box((W, D, H)), mass=24.0, origin=Origin(xyz=(0.0, 0.0, zc)))
    return housing


def _add_fans(model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig, mats: dict, housing):
    """Slot A: emit fan_{i} rotor parts + housing_to_fan_{i} CONTINUOUS joints."""
    H = r.body_h
    zc = H / 2.0
    if r.fan_discharge_layout == "front_fan_row":
        rotor_y = r.body_d / 2.0 - 0.015
        for i, cx in enumerate(r.fan_x_positions):
            fan = model.part(f"fan_{i}")
            fan.visual(
                _fan_rotor_mesh(f"fan_{i}_rotor", r),
                origin=_ROT_Z_TO_Y, material=mats["fan"], name=f"fan_{i}_rotor", material_class_id="plastic.opaque_glossy_molded",
            )
            fan.inertial = Inertial.from_geometry(Box((0.28, 0.02, 0.28)), mass=0.45)
            model.articulation(
                f"housing_to_fan_{i}",
                ArticulationType.CONTINUOUS,
                parent=housing, child=fan,
                origin=Origin(xyz=(cx, rotor_y, FAN_CTR_Z + zc)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=2.0, velocity=r.fan_velocity),
            )
    else:  # top_discharge_fan
        rotor_z = H - 0.018  # near the top face (housing spans [0, H])
        fan = model.part("fan_0")
        fan.visual(
            _fan_rotor_mesh("fan_0_rotor", r),
            origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["fan"], name="fan_0_rotor", material_class_id="plastic.opaque_glossy_molded",
        )
        fan.inertial = Inertial.from_geometry(Box((0.24, 0.24, 0.04)), mass=0.6)
        model.articulation(
            "housing_to_fan_0",
            ArticulationType.CONTINUOUS,
            parent=housing, child=fan,
            origin=Origin(xyz=(0.0, 0.0, rotor_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=r.fan_velocity),
        )


def _add_front_skin(model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig, mats: dict, housing):
    """Slot B (front guard portion): emit the fan_grille part(s) over each throat.

    wire_ring_grille / side_service_door -> wire grille per throat.
    louver_vent_panel -> single rectangular louver panel (single front bore only).
    """
    if r.fan_discharge_layout == "front_fan_row":
        fan_z = FAN_CTR_Z + r.body_h / 2.0
        front_y = r.body_d / 2.0
        if r.front_service_skin == "louver_vent_panel":
            # single-bore guaranteed by gating
            cx = r.fan_x_positions[0]
            grille = model.part("fan_grille_0")
            grille.visual(
                mesh_from_geometry(_louver_panel_geometry(r), "louver_grille_0"),
                origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
                material=mats["grille"], name="louver_panel_0", material_class_id="metal.paint_coated",
            )
            grille.inertial = Inertial.from_geometry(
                Box((0.46, LOUVER_DUCT_DEPTH + LOUVER_FACE_TH, 0.46)), mass=0.8)
            model.articulation(
                "housing_to_grille_0",
                ArticulationType.FIXED,
                parent=housing, child=grille,
                origin=Origin(xyz=(cx, front_y, fan_z)),
            )
        else:
            for i, cx in enumerate(r.fan_x_positions):
                grille = model.part(f"fan_grille_{i}")
                grille.visual(
                    mesh_from_cadquery(_wire_grille_front(cx, r), f"grille_rings_{i}"),
                    material=mats["grille"], name=f"grille_rings_{i}", material_class_id="metal.mesh_chainmail",
                )
                grille.inertial = Inertial.from_geometry(
                    Box((0.34, 0.06, 0.34)), mass=0.5)
                model.articulation(
                    f"housing_to_grille_{i}",
                    ArticulationType.FIXED,
                    parent=housing, child=grille,
                    origin=Origin(xyz=(cx, front_y, fan_z)),
                )
    else:  # top_discharge_fan -> single top wire grille
        H = r.body_h
        grille = model.part("fan_grille_0")
        grille.visual(
            mesh_from_cadquery(_wire_grille_top(r), "grille_rings_0"),
            material=mats["grille"], name="grille_rings_0", material_class_id="metal.mesh_chainmail",
        )
        grille.inertial = Inertial.from_geometry(Box((0.30, 0.30, 0.06)), mass=0.5)
        model.articulation(
            "housing_to_grille_0",
            ArticulationType.FIXED,
            parent=housing, child=grille,
            origin=Origin(xyz=(0.0, 0.0, H)),  # top face (housing spans [0, H])
        )


def _add_service(model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig, mats: dict, housing):
    """Side service skin + copper valves (bracket/wall families only).

    side_service_door -> hinged service_door part (panel + cam latch) + visible
    hinge barrels on the housing. Otherwise a flat REVOLUTE service_panel.
    """
    if not r.has_service_skin:
        return
    W = r.body_w
    zc = r.body_h / 2.0  # housing center z (housing spans [0, H])
    pocket_floor_x = W / 2.0 - POCKET_DEPTH
    # Seat the panel's inner face ~2 mm into the pocket floor (solid, since
    # POCKET_DEPTH < WALL) so the closed skin rests on the housing (no gap).
    hinge_x = pocket_floor_x + SVC_PANEL_TH / 2.0 - 0.002
    hinge_y = -(SVC_PANEL_W / 2.0)

    # copper refrigerant service valves (FIXED, penetrate side wall). The mesh is
    # authored around its own part origin; the FIXED joint origin places that
    # origin at the valve station on the +X side wall (joint origin on geometry).
    valves = model.part("service_valves")
    valves.visual(
        mesh_from_cadquery(_refrigerant_lines_mesh(), "service_valves"),
        material=mats["copper"], name="valve_stubs", material_class_id="metal.copper_bare",
    )
    valves.inertial = Inertial.from_geometry(Box((0.07, 0.02, 0.10)), mass=0.5)
    valve_z = 0.066  # near the bottom of the cabinet (housing bottom at z=0)
    model.articulation(
        "housing_to_service_valves",
        ArticulationType.FIXED,
        parent=housing, child=valves,
        origin=Origin(xyz=(r.body_w / 2.0 - 0.006, 0.030, valve_z)),
    )

    if r.is_door:
        # Visible hinge barrels on the housing side wall (mesh authored centered
        # on z=0, lifted to the housing center).
        housing.visual(
            mesh_from_cadquery(
                _hinge_barrels_mesh(r, hinge_x, hinge_y).translate((0.0, 0.0, zc)),
                "hinge_barrels"),
            material=mats["steel"], name="hinge_barrels", material_class_id="metal.steel_bare",
        )
        door = model.part("service_door")
        door.visual(
            mesh_from_cadquery(_service_panel_mesh(), "service_door"),
            material=mats["panel"], name="door_panel", material_class_id="metal.paint_coated",
        )
        door.visual(
            mesh_from_cadquery(_door_latch_mesh(), "door_latch"),
            material=mats["steel"], name="door_latch", material_class_id="metal.steel_bare",
        )
        door.inertial = Inertial.from_geometry(
            Box((SVC_PANEL_TH, SVC_PANEL_W, SVC_PANEL_H)), mass=0.8)
        model.articulation(
            "housing_to_service_door",
            ArticulationType.REVOLUTE,
            parent=housing, child=door,
            origin=Origin(xyz=(hinge_x, hinge_y, zc)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.9),
        )
    else:
        panel = model.part("service_panel")
        panel.visual(
            mesh_from_cadquery(_service_panel_mesh(), "service_panel"),
            material=mats["panel"], name="panel_cover", material_class_id="metal.paint_coated",
        )
        panel.inertial = Inertial.from_geometry(
            Box((SVC_PANEL_TH, SVC_PANEL_W, SVC_PANEL_H)), mass=0.8)
        model.articulation(
            "housing_to_service_panel",
            ArticulationType.REVOLUTE,
            parent=housing, child=panel,
            origin=Origin(xyz=(hinge_x, hinge_y, zc)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.9),
        )


def _add_support(model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig, mats: dict, housing):
    """Slot C: emit the mounting support root + FIXED join lifting the housing.

    base_feet -> no support part (housing is root; feet are housing visuals).
    angle_iron_bracket -> mounting_bracket root + bracket_to_housing FIXED.
    wall_brackets -> wall_bracket_0 root + wall_bracket_1 FIXED + bracket_to_housing.
    """
    H = r.body_h
    if r.mounting_support == "base_feet":
        return  # housing is the root; feet already added as housing visuals.

    # Housing bottom sits at z=0; supports place their shelf top at z=0 and reach
    # DOWN to the floor. The FIXED joint origin (0,0,0) lands on real support
    # hardware (shelf/flange/rail) AND the housing bottom.
    z_top = 0.0
    if r.mounting_support == "angle_iron_bracket":
        bracket = model.part("mounting_bracket")
        bracket.visual(
            mesh_from_cadquery(_angle_iron_bracket_mesh(r, z_top), "mounting_bracket"),
            material=mats["steel"], name="bracket_frame", material_class_id="metal.steel_bare",
        )
        bracket.inertial = Inertial.from_geometry(
            Box((r.body_w, r.body_d, BRACKET_LEG_H)), mass=4.0,
            origin=Origin(xyz=(0.0, 0.0, -BRACKET_LEG_H / 2.0)))
        model.articulation(
            "bracket_to_housing",
            ArticulationType.FIXED,
            parent=bracket, child=housing,
            origin=Origin(xyz=(0.0, 0.0, z_top)),
        )
    else:  # wall_brackets (single root part: two brackets + connecting rail)
        support = model.part("wall_brackets")
        support.visual(
            mesh_from_cadquery(_wall_brackets_mesh(r, z_top), "wall_brackets"),
            material=mats["steel"], name="bracket_bodies", material_class_id="metal.steel_bare",
        )
        support.inertial = Inertial.from_geometry(
            Box((r.body_w, r.body_d + 0.020, WB_WALL_H)), mass=7.0,
            origin=Origin(xyz=(0.0, 0.0, -WB_WALL_H / 2.0)))
        model.articulation(
            "bracket_to_housing",
            ArticulationType.FIXED,
            parent=support, child=housing,
            origin=Origin(xyz=(0.0, 0.0, z_top)),
        )


def build_ac_outdoor_unit(
    config: ACOutdoorUnitConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or ACOutdoorUnitConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-ac-outdoor-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = [list(t) for t in slot_choices_for_config(r)]

    mats = _materials(model, r)
    housing = _add_housing(model, r, mats)
    _add_support(model, r, mats, housing)   # establishes root + lifts housing
    _add_fans(model, r, mats, housing)
    _add_front_skin(model, r, mats, housing)
    _add_service(model, r, mats, housing)
    return model


def build_seeded_ac_outdoor_unit(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_ac_outdoor_unit(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices.
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedACOutdoorUnitConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("fan_discharge_layout", r.fan_discharge_layout),
        ("fan_count", f"fan_count_{r.fan_count}"),
        ("fan_blade_count", f"blades_{r.fan_blade_count}"),
        ("front_service_skin", r.front_service_skin),
        ("mounting_support", r.mounting_support),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #


def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedACOutdoorUnitConfig, housing
) -> None:
    parts = {p.name for p in model.parts}
    n = r.fan_count if r.fan_discharge_layout == "front_fan_row" else 1

    for i in range(n):
        fan = model.get_part(f"fan_{i}")
        fan_elem = f"fan_{i}_rotor"
        # rotor recessed inside the hollow cabinet
        ctx.allow_overlap(
            housing, fan, elem_a="housing_shell", elem_b=fan_elem,
            reason=f"Fan {i} impeller is recessed inside the hollow cabinet shell.",
        )
        # rotor hub captured on the motor-mount shaft
        ctx.allow_overlap(
            housing, fan, elem_a=f"fan_motor_mount_{i}", elem_b=fan_elem,
            reason=f"Fan {i} rotor hub is captured on the motor-mount shaft.",
        )
        # rotor recessed within the shroud ring
        ctx.allow_overlap(
            housing, fan, elem_a=f"fan_shroud_ring_{i}", elem_b=fan_elem,
            reason=f"Fan {i} impeller sits within the venturi shroud ring.",
        )
        # rotor spinning just inside the dark venturi duct sleeve
        ctx.allow_overlap(
            housing, fan, elem_a=f"fan_duct_{i}", elem_b=fan_elem,
            reason=f"Fan {i} impeller spins recessed within the dark venturi duct.",
        )
        # grille seats over the throat (rear spigot / tabs into shroud ring)
        grille = model.get_part(f"fan_grille_{i}")
        if r.front_service_skin == "louver_vent_panel":
            ctx.allow_overlap(
                grille, housing, elem_a=f"louver_panel_{i}", elem_b=f"fan_shroud_ring_{i}",
                reason="Louver panel rear sleeve seats into the shroud ring.",
            )
            ctx.allow_overlap(
                grille, housing, elem_a=f"louver_panel_{i}", elem_b="housing_shell",
                reason="Rectangular louver frame corners overlap the front skin around the round bore.",
            )
            ctx.allow_overlap(
                grille, fan, elem_a=f"louver_panel_{i}", elem_b=fan_elem,
                reason="Recessed rotor sits just behind the louver panel rear sleeve (captured fit).",
            )
            ctx.allow_overlap(
                grille, housing, elem_a=f"louver_panel_{i}", elem_b=f"fan_duct_{i}",
                reason="Louver rear sleeve seats into the recessed venturi duct.",
            )
        else:
            grille_elem = f"grille_rings_{i}"
            ctx.allow_overlap(
                grille, housing, elem_a=grille_elem, elem_b=f"fan_shroud_ring_{i}",
                reason="Grille mounting tabs seat into the raised shroud ring.",
            )
            ctx.allow_overlap(
                grille, housing, elem_a=grille_elem, elem_b="housing_shell",
                reason="Grille rim ring seats on the front/top skin around the throat bore.",
            )
            ctx.allow_overlap(
                grille, housing, elem_a=grille_elem, elem_b=f"fan_duct_{i}",
                reason="Grille rear tabs reach into the recessed venturi duct.",
            )

    if r.has_service_skin:
        valves = model.get_part("service_valves")
        ctx.allow_overlap(
            housing, valves, elem_a="housing_shell", elem_b="valve_stubs",
            reason="Copper service valves intentionally penetrate the side wall.",
        )
        if r.is_door:
            door = model.get_part("service_door")
            ctx.allow_overlap(
                housing, door, elem_a="hinge_barrels", elem_b="door_panel",
                reason="Hinge barrels embed into the door edge at the hinge line.",
            )
            ctx.allow_overlap(
                housing, door, elem_a="housing_shell", elem_b="door_panel",
                reason="Closed service door seats into the recessed side pocket floor.",
            )
            ctx.allow_overlap(
                door, valves, elem_a="door_panel", elem_b="valve_stubs",
                reason="Copper valves exit the side wall just beneath the service door.",
            )
        else:
            panel = model.get_part("service_panel")
            ctx.allow_overlap(
                housing, panel, elem_a="housing_shell", elem_b="panel_cover",
                reason="Closed service panel seats into the recessed side pocket floor.",
            )
            ctx.allow_overlap(
                panel, valves, elem_a="panel_cover", elem_b="valve_stubs",
                reason="Copper valves exit the side wall just beneath the service panel.",
            )


def run_ac_outdoor_unit_tests(
    object_model: ArticulatedObject, config: ACOutdoorUnitConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("housing")

    _declare_overlap_allowances(ctx, object_model, r, housing)

    # --- Hero parts present ------------------------------------------------- #
    ctx.check("housing_present", housing is not None, "Expected a housing part.")
    n = r.fan_count if r.fan_discharge_layout == "front_fan_row" else 1
    fans = [object_model.get_part(f"fan_{i}") for i in range(n)]
    for i in range(n):
        ctx.check(f"fan_{i}_present", fans[i] is not None, f"Expected fan_{i}.")

    # --- Single root depends on mounting support ---------------------------- #
    roots = object_model.root_parts()
    if r.mounting_support == "base_feet":
        expected_root = "housing"
    elif r.mounting_support == "angle_iron_bracket":
        expected_root = "mounting_bracket"
    else:
        expected_root = "wall_brackets"
    ctx.check(
        "single_root",
        len(roots) == 1 and roots[0].name == expected_root,
        f"roots={[p.name for p in roots]} expected={expected_root}",
    )

    # --- Cabinet proportions ------------------------------------------------ #
    hb = ctx.part_world_aabb(housing)
    if hb is not None:
        (hx0, hy0, hz0), (hx1, hy1, hz1) = hb
        hw, hd, hh = hx1 - hx0, hy1 - hy0, hz1 - hz0
        ctx.check("cabinet_height", 0.45 <= hh <= 0.62, f"height={hh:.3f}")
        ctx.check("cabinet_depth", 0.26 <= hd <= 0.38, f"depth={hd:.3f}")
        ctx.check("cabinet_wide_enough", hw >= 0.70, f"width={hw:.3f}")

    # --- Each fan is a real thin disc, on-axis, behind the face ------------- #
    front_row = r.fan_discharge_layout == "front_fan_row"
    for i in range(n):
        fan = fans[i]
        joint = object_model.get_articulation(f"housing_to_fan_{i}")
        # joint type/axis
        ctx.check(
            f"fan_{i}_joint_continuous",
            str(joint.articulation_type).endswith("CONTINUOUS"),
            f"type={joint.articulation_type}",
        )
        ax = tuple(joint.axis)
        if front_row:
            ctx.check(
                f"fan_{i}_axis_front_y",
                abs(ax[1]) > 0.99 and abs(ax[0]) < 0.01 and abs(ax[2]) < 0.01,
                f"axis={ax}",
            )
        else:
            ctx.check(
                f"fan_{i}_axis_top_z",
                abs(ax[2]) > 0.99 and abs(ax[0]) < 0.01 and abs(ax[1]) < 0.01,
                f"axis={ax}",
            )
        fb = ctx.part_world_aabb(fan)
        if fb is not None:
            (fx0, fy0, fz0), (fx1, fy1, fz1) = fb
            if front_row:
                diam = max(fx1 - fx0, fz1 - fz0)
                thin = fy1 - fy0
            else:
                diam = max(fx1 - fx0, fy1 - fy0)
                thin = fz1 - fz0
            ctx.check(
                f"fan_{i}_diameter",
                2.0 * (r.fan_bore_r - 0.008) - 0.05 <= diam <= 2.0 * (r.fan_bore_r - 0.008) + 0.05,
                f"diam={diam:.3f}",
            )
            ctx.check(f"fan_{i}_is_disc", thin <= 0.10, f"thin={thin:.3f}")

    # --- Each fan actually spins about its hub ------------------------------ #
    for i in range(n):
        fan = fans[i]
        joint = object_model.get_articulation(f"housing_to_fan_{i}")
        a0 = None
        a1 = None
        with ctx.pose({joint: 0.0}):
            a0 = ctx.part_world_aabb(fan)
        with ctx.pose({joint: 0.6}):
            a1 = ctx.part_world_aabb(fan)
        if a0 is not None and a1 is not None:
            moved = (
                abs(a1[0][0] - a0[0][0]) > 0.003
                or abs(a1[1][0] - a0[1][0]) > 0.003
                or abs(a1[1][2] - a0[1][2]) > 0.003
                or abs(a1[1][1] - a0[1][1]) > 0.003
            )
            ctx.check(f"fan_{i}_spins", moved, f"q0={a0} q1={a1}")

    # --- Grille present over each throat, supported on the shroud ----------- #
    for i in range(n):
        grille = object_model.get_part(f"fan_grille_{i}")
        ctx.check(f"grille_{i}_present", grille is not None, f"Expected fan_grille_{i}.")
        if grille is not None:
            grille_elem = (
                f"louver_panel_{i}" if r.front_service_skin == "louver_vent_panel"
                else f"grille_rings_{i}"
            )
            ctx.expect_contact(
                grille, housing,
                elem_a=grille_elem, elem_b=f"fan_shroud_ring_{i}",
                contact_tol=0.003,
                name=f"grille_{i}_seated_on_shroud",
            )

    # --- Support sits below / carries the housing --------------------------- #
    if r.mounting_support != "base_feet" and hb is not None:
        support_part = object_model.get_part(expected_root)
        sb = ctx.part_world_aabb(support_part)
        if sb is not None:
            ctx.check(
                "support_below_housing",
                sb[0][2] < hb[0][2] + 0.02,
                f"support_minz={sb[0][2]:.3f} housing_minz={hb[0][2]:.3f}",
            )

    # --- Service door / panel opens outward (+X) ---------------------------- #
    if r.has_service_skin:
        skin_part_name = "service_door" if r.is_door else "service_panel"
        skin_joint_name = "housing_to_service_door" if r.is_door else "housing_to_service_panel"
        skin_part = object_model.get_part(skin_part_name)
        skin_joint = object_model.get_articulation(skin_joint_name)
        ctx.check(
            "service_revolute",
            str(skin_joint.articulation_type).endswith("REVOLUTE"),
            f"type={skin_joint.articulation_type}",
        )
        ctx.check(
            "service_axis_vertical",
            abs(skin_joint.axis[2]) > 0.99,
            f"axis={skin_joint.axis}",
        )
        closed_aabb = ctx.part_world_aabb(skin_part)
        with ctx.pose({skin_joint: 1.4}):
            open_aabb = ctx.part_world_aabb(skin_part)
        if closed_aabb is not None and open_aabb is not None:
            ctx.check(
                "service_opens_outward",
                open_aabb[1][0] > closed_aabb[1][0] + 0.05,
                f"closed_maxx={closed_aabb[1][0]:.3f} open_maxx={open_aabb[1][0]:.3f}",
            )
        if r.is_door:
            ctx.check(
                "hinge_barrels_on_housing",
                any(v.name == "hinge_barrels" for v in housing.visuals),
                "Expected hinge_barrels visual on the housing frame.",
            )

    return ctx.report()


# Module-level model so external `compile`/`view` tooling can import it directly.
object_model = build_ac_outdoor_unit()
