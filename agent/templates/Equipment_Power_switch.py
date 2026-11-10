# SPDX-License-Identifier: Apache-2.0

"""Equipment / power-switch modular procedural template.

A power switch is a workbench-scale device-level power control: a fixed
load-bearing *mount* (wall plate / pendant box / industrial enclosure /
inline cord barrel) carries a user-operated *actuator* that makes one
limited-throw open/close motion about the mount's front control face
(flip, rock, rotate, press, or linear push-pull). A single flat wall plate
may carry several identical roller units gang-ganged along its width.

Pattern (= ``mixed``): one root ``mount`` part, with the actuator + its
fixed support attached as parallel children, plus a ``gang_count`` chain
multiplicity axis (roller units on a flat plate only).

Sourced from the reviewed spec
``articraft_template_authoring/specs_modular_v1/Equipment_Power_Other_Switch.md`` and the
``picture/Equipment/Power switch`` 5-star fork batch (2 parents + 8 slot
variants):

  * Slot A ``actuator`` (6): roller_bail_drawlatch (REVOLUTE X) /
    flip_toggle_dolly (REVOLUTE X) / rocker_paddle (REVOLUTE X) /
    rotary_cam_selector (REVOLUTE Z) / pushbutton_cap (PRISMATIC -Z) /
    grab_handle_slider (PRISMATIC +Y). The consumer joint axis/type is
    PER-CANDIDATE — never hard-coded to one axis. Each actuator carries its
    own fixed support hardware (keeper+side_bolts / raised_boss /
    rocker_well / rotary_mount escutcheon / button_bezel bore / slot face),
    so swapping the actuator swaps its support too.
  * Slot B ``mount`` (4): flat_wall_plate / pendant_box /
    industrial_enclosure_box / inline_cord_barrel. Each changes the root
    part geometry + the fixed decorations (louver+screws / conduit+gland /
    lid_lip+lugs / cord bosses+stubs) carried as parent visuals (Rule 1).
  * ``gang_count`` (N in [1,6]): roller units copied along X on the flat
    wall plate; ``bail_{i}`` + ``plate_to_bail_{i}`` per unit, evenly spaced
    by ``_unit_x(i)``, plate widened with N. Copy-logic follows the n2/n3
    variants (not the un-looped parent N=1).

Compatibility gating (resolve_config, spec §Multiplicity / §Validator):
  * ``gang_count > 1`` only when mount == flat_wall_plate AND actuator ==
    roller_bail_drawlatch; every other combination is forced to N=1.
  * inline_cord_barrel is narrow and only hosts compact actuators
    {grab_handle_slider, pushbutton_cap, flip_toggle_dolly}; any other
    actuator falls back to grab_handle_slider, and N is forced to 1.

All actuator joints are real mechanical fits (captured pin in eyes/ears,
seated knob/cap skirt, paddle foot in well, slide block in slot). Following
the 5-star sources and the cushion reference, these joints are grandfathered
(no MatingContract) and supported by a real visible support piece on the
mount plus element-scoped ``allow_overlap``, satisfying the visual support
graph without risking false mating-gap failures on captured-pin geometry.
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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

ActuatorStyle = Literal[
    "roller_bail_drawlatch",
    "flip_toggle_dolly",
    "rocker_paddle",
    "rotary_cam_selector",
    "pushbutton_cap",
    "grab_handle_slider",
]
MountStyle = Literal[
    "flat_wall_plate",
    "pendant_box",
    "industrial_enclosure_box",
    "inline_cord_barrel",
]
PaletteStyle = Literal[
    "brushed_steel",
    "abs_gray",
    "industrial_yellow",
    "safety_red",
    "ivory_white",
    "matte_black",
]

ACTUATOR_STYLES: tuple[ActuatorStyle, ...] = (
    "roller_bail_drawlatch",
    "flip_toggle_dolly",
    "rocker_paddle",
    "rotary_cam_selector",
    "pushbutton_cap",
    "grab_handle_slider",
)
MOUNT_STYLES: tuple[MountStyle, ...] = (
    "flat_wall_plate",
    "pendant_box",
    "industrial_enclosure_box",
    "inline_cord_barrel",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_steel",
    "abs_gray",
    "industrial_yellow",
    "safety_red",
    "ivory_white",
    "matte_black",
)

N_MIN = 1
N_MAX = 6
# Small N high-frequency, 4..6 a rare tail (spec §Multiplicity).
GANG_WEIGHTS = (0.42, 0.26, 0.16, 0.08, 0.05, 0.03)

GANG_MOUNT: MountStyle = "flat_wall_plate"
GANG_ACTUATOR: ActuatorStyle = "roller_bail_drawlatch"
# inline cord barrel is narrow -> only compact actuators fit.
BARREL_ACTUATORS: tuple[ActuatorStyle, ...] = (
    "grab_handle_slider",
    "pushbutton_cap",
    "flip_toggle_dolly",
)

# ---------------------------------------------------------------------------
# Palettes: realistic colorways drawn from the 5-star sources.
#   body   - main housing / plate shell
#   field  - recessed field / secondary surface
#   support- actuator support hardware metal (keeper/boss/well/bezel/...)
#   mover  - moving actuator body
#   accent - roller / handle / pointer dark detail
#   screw  - zinc screw heads
#   detail - conduit / cord / lug metal
#   trim   - gland white / pointer light highlight
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_steel": {  # flat wall-plate parent (5b4ad2d8)
        "body": (0.60, 0.62, 0.64, 1.0),
        "field": (0.54, 0.56, 0.58, 1.0),
        "support": (0.56, 0.58, 0.61, 1.0),
        "mover": (0.60, 0.62, 0.65, 1.0),
        "accent": (0.16, 0.17, 0.19, 1.0),
        "screw": (0.78, 0.80, 0.82, 1.0),
        "detail": (0.46, 0.48, 0.51, 1.0),
        "trim": (0.86, 0.88, 0.90, 1.0),
    },
    "abs_gray": {  # pendant box parent (621bac5e)
        "body": (0.55, 0.56, 0.58, 1.0),
        "field": (0.34, 0.35, 0.37, 1.0),
        "support": (0.44, 0.45, 0.47, 1.0),
        "mover": (0.19, 0.20, 0.22, 1.0),
        "accent": (0.26, 0.27, 0.29, 1.0),
        "screw": (0.76, 0.78, 0.80, 1.0),
        "detail": (0.52, 0.54, 0.57, 1.0),
        "trim": (0.88, 0.89, 0.90, 1.0),
    },
    "industrial_yellow": {  # painted-steel isolator enclosure
        "body": (0.86, 0.72, 0.10, 1.0),
        "field": (0.20, 0.20, 0.21, 1.0),
        "support": (0.30, 0.30, 0.31, 1.0),
        "mover": (0.10, 0.10, 0.11, 1.0),
        "accent": (0.08, 0.08, 0.09, 1.0),
        "screw": (0.80, 0.82, 0.84, 1.0),
        "detail": (0.40, 0.41, 0.43, 1.0),
        "trim": (0.92, 0.93, 0.94, 1.0),
    },
    "safety_red": {  # emergency isolator red body / black switch
        "body": (0.74, 0.10, 0.10, 1.0),
        "field": (0.22, 0.05, 0.05, 1.0),
        "support": (0.30, 0.30, 0.31, 1.0),
        "mover": (0.09, 0.09, 0.10, 1.0),
        "accent": (0.06, 0.06, 0.07, 1.0),
        "screw": (0.80, 0.82, 0.84, 1.0),
        "detail": (0.42, 0.43, 0.45, 1.0),
        "trim": (0.94, 0.92, 0.90, 1.0),
    },
    "ivory_white": {  # white domestic plastic plate
        "body": (0.92, 0.91, 0.88, 1.0),
        "field": (0.84, 0.83, 0.80, 1.0),
        "support": (0.78, 0.78, 0.76, 1.0),
        "mover": (0.30, 0.31, 0.33, 1.0),
        "accent": (0.20, 0.21, 0.23, 1.0),
        "screw": (0.74, 0.76, 0.78, 1.0),
        "detail": (0.64, 0.65, 0.66, 1.0),
        "trim": (0.97, 0.96, 0.94, 1.0),
    },
    "matte_black": {  # matte black industrial body
        "body": (0.14, 0.14, 0.15, 1.0),
        "field": (0.09, 0.09, 0.10, 1.0),
        "support": (0.26, 0.26, 0.27, 1.0),
        "mover": (0.66, 0.67, 0.68, 1.0),
        "accent": (0.80, 0.81, 0.82, 1.0),
        "screw": (0.70, 0.72, 0.74, 1.0),
        "detail": (0.34, 0.35, 0.37, 1.0),
        "trim": (0.88, 0.88, 0.86, 1.0),
    },
}


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class PowerSwitchConfig:
    actuator_style: ActuatorStyle | None = None
    mount_style: MountStyle | None = None
    gang_count: int | None = None
    palette_style: PaletteStyle = "brushed_steel"
    body_scale: float = 1.0
    throw_scale: float = 1.0
    unit_pitch: float = 0.066
    name: str = "power_switch"


@dataclass(frozen=True)
class ResolvedPowerSwitchConfig:
    actuator_style: ActuatorStyle
    mount_style: MountStyle
    gang_count: int
    palette_style: PaletteStyle
    body_scale: float
    throw_scale: float
    unit_pitch: float
    plate_w: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> PowerSwitchConfig:
    rng = random.Random(seed)
    mount_style = rng.choice(MOUNT_STYLES)
    actuator_style = rng.choice(ACTUATOR_STYLES)
    gang_count = rng.choices(range(N_MIN, N_MAX + 1), weights=GANG_WEIGHTS, k=1)[0]
    return PowerSwitchConfig(
        actuator_style=actuator_style,
        mount_style=mount_style,
        gang_count=gang_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_scale=round(rng.uniform(0.92, 1.12), 4),
        throw_scale=round(rng.uniform(0.85, 1.12), 4),
        unit_pitch=round(rng.uniform(0.058, 0.070), 4),
        name=f"seeded_power_switch_{seed}",
    )


def resolve_config(config: PowerSwitchConfig | None = None) -> ResolvedPowerSwitchConfig:
    cfg = config or PowerSwitchConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    mount_style = _pick(cfg.mount_style, MOUNT_STYLES)
    actuator_style = _pick(cfg.actuator_style, ACTUATOR_STYLES)

    # --- Compatibility gating. ---
    # inline cord barrel only hosts compact actuators.
    if mount_style == "inline_cord_barrel" and actuator_style not in BARREL_ACTUATORS:
        actuator_style = "grab_handle_slider"

    gang_count = int(cfg.gang_count) if cfg.gang_count is not None else 1
    gang_count = int(_clamp(gang_count, N_MIN, N_MAX))
    # gang > 1 only on flat_wall_plate x roller_bail_drawlatch.
    if not (mount_style == GANG_MOUNT and actuator_style == GANG_ACTUATOR):
        gang_count = 1

    body_scale = _clamp(cfg.body_scale, 0.92, 1.12)
    throw_scale = _clamp(cfg.throw_scale, 0.85, 1.12)
    unit_pitch = _clamp(cfg.unit_pitch, 0.058, 0.070)

    # Flat plate widens with gang count (n2: 0.154 for N=2 pitch 0.066).
    plate_w = max(0.090 * body_scale, gang_count * unit_pitch + 0.022)

    return ResolvedPowerSwitchConfig(
        actuator_style=actuator_style,
        mount_style=mount_style,
        gang_count=gang_count,
        palette_style=palette_style,
        body_scale=body_scale,
        throw_scale=throw_scale,
        unit_pitch=unit_pitch,
        plate_w=plate_w,
        name=cfg.name or "power_switch",
    )


def slot_choices_for_config(
    config: PowerSwitchConfig | ResolvedPowerSwitchConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedPowerSwitchConfig) else resolve_config(config)
    return (
        ("mount", r.mount_style),
        ("actuator", r.actuator_style),
        ("gang", f"n{r.gang_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Mount surface descriptor: where the actuator(s) attach.
# ===========================================================================
@dataclass(frozen=True)
class MountSurface:
    ctrl_z: float       # front control plane (top of the mount front face)
    field_z: float      # recess floor where support bases extrude from
    act_cy: float       # actuator vertical center on the front face
    half_w: float       # half-width of the available control field (X)
    half_h: float       # half-height of the available control field (Y)


def _unit_centers(r: ResolvedPowerSwitchConfig) -> list[float]:
    n = r.gang_count
    return [(i - (n - 1) / 2.0) * r.unit_pitch for i in range(n)]


# ---------------------------------------------------------------------------
# Profile helpers (from the 5-star sources).
# ---------------------------------------------------------------------------
def _chamfer_rect(w: float, h: float, c: float) -> list[tuple[float, float]]:
    hx, hy = w / 2.0, h / 2.0
    return [
        (-hx + c, -hy), (hx - c, -hy), (hx, -hy + c), (hx, hy - c),
        (hx - c, hy), (-hx + c, hy), (-hx, hy - c), (-hx, -hy + c),
    ]


def _rounded_plate(width: float, length: float, height: float, radius: float):
    radius = min(radius, width / 2.0 - 0.001, length / 2.0 - 0.001)
    return (
        cq.Workplane("XY")
        .rect(width, length)
        .extrude(height)
        .edges("|Z")
        .fillet(radius)
    )


def _box_inertial(part, sx, sy, sz, mass, cz):
    part.inertial = Inertial.from_geometry(
        Box((sx, sy, sz)), mass=mass, origin=Origin(xyz=(0.0, 0.0, cz))
    )


# ===========================================================================
# Mount modules (Slot B). Each emits the root `mount` part (shell +
# decorations as parent visuals, Rule 1) and returns a MountSurface.
# ===========================================================================
_FLAT_H = 0.130
_FLAT_T = 0.008
_FLAT_RECESS = 0.0018


def _build_flat_wall_plate(model, r, mats) -> MountSurface:
    mount = model.part("mount")
    pw, ph, pt = r.plate_w, _FLAT_H, _FLAT_T
    field_z = pt - _FLAT_RECESS

    # Faceplate shell: rounded vertical plate with a recessed chamfered field.
    plate = (
        cq.Workplane("XY")
        .box(pw, ph, pt, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.012)
    )
    field = _chamfer_rect(pw - 0.016, ph - 0.016, 0.016)
    pocket = (
        cq.Workplane("XY")
        .workplane(offset=field_z)
        .polyline(field)
        .close()
        .extrude(_FLAT_RECESS + 0.001)
    )
    plate = plate.cut(pocket)
    mount.visual(
        mesh_from_cadquery(plate, "faceplate_shell"),
        material=mats["body"],
        name="faceplate_shell", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "industrial_yellow", "safety_red", "matte_black"} else "plastic.opaque_glossy_molded"),
    )

    # Top louver vent pad (raised sub-panel with horizontal slots).
    pad_cy = ph / 2.0 - 0.024
    pad_w = min(0.086, pw - 0.030)
    louver_w = pad_w * 0.78
    pad = (
        cq.Workplane("XY")
        .workplane(offset=field_z)
        .center(0.0, pad_cy)
        .box(pad_w, 0.028, _FLAT_RECESS + 0.0016, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.004)
    )
    pad_front = field_z + _FLAT_RECESS + 0.0016
    band = 4 * 0.0016 + 3 * 0.0024
    y0 = pad_cy + band / 2.0 - 0.0008
    for i in range(4):
        cy = y0 - i * 0.0040
        slot = (
            cq.Workplane("XY")
            .workplane(offset=pad_front - 0.0014)
            .center(0.0, cy)
            .box(louver_w, 0.0016, 0.0015, centered=(True, True, False))
        )
        pad = pad.cut(slot)
    mount.visual(
        mesh_from_cadquery(pad, "louver_pad"), material=mats["field"], name="louver_pad", material_class_id=("metal.stainless_matte" if r.palette_style in {"brushed_steel", "industrial_yellow", "safety_red", "matte_black"} else "plastic.opaque_generic")
    )

    # Two corner mounting screws flanking the louver.
    mount.visual(
        mesh_from_cadquery(_flat_screws(pw, ph), "mount_screws"),
        material=mats["screw"],
        name="mount_screws", material_class_id="metal.steel_galvanized",
    )

    _box_inertial(mount, pw, ph, pt, 0.18, pt / 2.0)
    return MountSurface(
        ctrl_z=pt, field_z=field_z, act_cy=0.0,
        half_w=(pw - 0.016) / 2.0, half_h=(ph - 0.016) / 2.0,
    )


def _flat_screws(pw, ph):
    screws = None
    off_x = pw / 2.0 - 0.011
    off_y = ph / 2.0 - 0.012
    for sx in (-1, 1):
        head = (
            cq.Workplane("XY")
            .workplane(offset=_FLAT_T - 0.0006)
            .center(sx * off_x, off_y)
            .circle(0.0034)
            .extrude(0.0018)
        )
        slot_a = (
            cq.Workplane("XY")
            .workplane(offset=_FLAT_T + 0.0012 - 0.0004)
            .center(sx * off_x, off_y)
            .box(0.0054, 0.0008, 0.001, centered=(True, True, False))
        )
        head = head.cut(slot_a)
        screws = head if screws is None else screws.union(head)
    return screws


def _octagon(w: float, h: float, chamfer: float) -> list[tuple[float, float]]:
    hx, hy, c = w / 2.0, h / 2.0, chamfer
    return [
        (-hx + c, -hy), (hx - c, -hy), (hx, -hy + c), (hx, hy - c),
        (hx - c, hy), (-hx + c, hy), (-hx, hy - c), (-hx, -hy + c),
    ]


def _build_pendant_box(model, r, mats) -> MountSurface:
    mount = model.part("mount")
    pw = 0.090 * r.body_scale
    ph = 0.110 * r.body_scale
    pt = 0.014
    # Octagonal ABS shell.
    shell = cq.Workplane("XY").polyline(_octagon(pw, ph, 0.020)).close().extrude(pt)
    shell = shell.edges("|Z").fillet(0.0015)
    mount.visual(
        mesh_from_cadquery(shell, "housing_shell"), material=mats["body"], name="housing_shell", material_class_id="plastic.opaque_glossy_molded"
    )

    # White sealing gland collar at the top.
    collar_cy = ph / 2.0 - 0.006
    collar = (
        cq.Workplane("XY")
        .center(0.0, collar_cy)
        .workplane(offset=pt - 0.002)
        .rect(0.026, 0.013)
        .extrude(0.007)
        .edges("|Z")
        .fillet(0.0025)
    )
    mount.visual(
        mesh_from_cadquery(collar, "gland_collar"), material=mats["trim"], name="gland_collar", material_class_id="plastic.opaque_glossy_molded"
    )

    # Two FIXED metallic conduit tubes rising from the gland (Rule 1, no joint).
    tubes = None
    tube_bottom = collar_cy - 0.004
    tube_top = ph / 2.0 + 0.080
    for sx in (-1, 1):
        tube = (
            cq.Workplane("XZ")
            .workplane(offset=-tube_top)
            .center(sx * 0.008, pt + 0.001)
            .circle(0.0036)
            .extrude(tube_top - tube_bottom)
        )
        tubes = tube if tubes is None else tubes.union(tube)
    mount.visual(
        mesh_from_cadquery(tubes, "conduit_tubes"), material=mats["detail"], name="conduit_tubes", material_class_id="metal.steel_galvanized"
    )

    _box_inertial(mount, pw, ph, pt, 0.30, pt / 2.0)
    return MountSurface(
        ctrl_z=pt, field_z=pt - 0.0006, act_cy=0.0,
        half_w=(pw - 0.016) / 2.0, half_h=(ph - 0.030) / 2.0,
    )


def _build_industrial_enclosure_box(model, r, mats) -> MountSurface:
    mount = model.part("mount")
    pw = 0.112 * r.body_scale
    ph = 0.112 * r.body_scale
    pt = 0.040
    shell = cq.Workplane("XY").rect(pw, ph).extrude(pt)
    shell = shell.edges("|Z").fillet(0.0040).edges(">Z").fillet(0.0012)
    mount.visual(
        mesh_from_cadquery(shell, "housing_shell"), material=mats["body"], name="housing_shell", material_class_id=("metal.brushed_silver" if r.palette_style == "brushed_steel" else "metal.paint_coated")
    )

    # Proud square perimeter lip on the front lid.
    outer_w, outer_h = pw - 0.004, ph - 0.004
    lip = (
        cq.Workplane("XY").workplane(offset=pt - 0.0005).rect(outer_w, outer_h).extrude(0.0037)
    )
    lip_in = (
        cq.Workplane("XY")
        .workplane(offset=pt - 0.0010)
        .rect(outer_w - 0.010, outer_h - 0.010)
        .extrude(0.0052)
    )
    lip = lip.cut(lip_in).edges("|Z").fillet(0.0012)
    mount.visual(
        mesh_from_cadquery(lip, "lid_lip"), material=mats["support"], name="lid_lip", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte")
    )

    # Four corner mounting lug bosses.
    lugs = None
    for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1)):
        bx = sx * (pw / 2.0 - 0.0140)
        by = sy * (ph / 2.0 - 0.0140)
        boss = (
            cq.Workplane("XY")
            .center(bx, by)
            .workplane(offset=pt - 0.0005)
            .circle(0.0062)
            .extrude(0.0047)
            .edges(">Z")
            .fillet(0.0009)
        )
        recess = (
            cq.Workplane("XY")
            .center(bx, by)
            .workplane(offset=pt + 0.0042 - 0.0006)
            .circle(0.0027)
            .extrude(0.0015)
        )
        boss = boss.cut(recess)
        lugs = boss if lugs is None else lugs.union(boss)
    mount.visual(
        mesh_from_cadquery(lugs, "lug_bosses"), material=mats["detail"], name="lug_bosses", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte")
    )

    _box_inertial(mount, pw, ph, pt, 0.55, pt / 2.0)
    return MountSurface(
        ctrl_z=pt, field_z=pt - 0.0006, act_cy=0.0,
        half_w=(pw - 0.030) / 2.0, half_h=(ph - 0.030) / 2.0,
    )


_BARREL_W = 0.052
_BARREL_L = 0.112
_BARREL_T = 0.020


def _build_inline_cord_barrel(model, r, mats) -> MountSurface:
    mount = model.part("mount")
    bw = _BARREL_W * r.body_scale
    bl = _BARREL_L * r.body_scale
    bt = _BARREL_T
    shell = _rounded_plate(bw, bl, bt, 0.016)
    shell = shell.edges(">Z").fillet(0.0012).edges("<Z").fillet(0.0008)
    mount.visual(
        mesh_from_cadquery(shell, "barrel_shell"), material=mats["body"], name="barrel_shell", material_class_id="plastic.opaque_glossy_molded"
    )

    # Inset top cover panel (case seam).
    cover = _rounded_plate(bw - 0.009, bl - 0.020, 0.0006, 0.010).translate(
        (0.0, 0.0, bt - 0.00015)
    )
    mount.visual(
        mesh_from_cadquery(cover, "top_cover"), material=mats["field"], name="top_cover", material_class_id="plastic.opaque_glossy_molded"
    )

    # Two oval cord-entry bosses + fixed cord stubs at the barrel ends.
    bosses = None
    stubs = None
    for sign in (1, -1):
        start_y = sign * (bl / 2.0 - 0.0020)
        length = sign * (0.014 + 0.0020)
        boss = (
            cq.Workplane("XZ")
            .workplane(offset=start_y)
            .center(0.0, bt / 2.0)
            .ellipse(0.0120, 0.0068)
            .extrude(length)
        )
        hole = (
            cq.Workplane("XZ")
            .workplane(offset=start_y - sign * 0.0005)
            .center(0.0, bt / 2.0)
            .circle(0.0039)
            .extrude(length + sign * 0.0010)
        )
        boss = boss.cut(hole)
        bosses = boss if bosses is None else bosses.union(boss)
        stub = (
            cq.Workplane("XZ")
            .workplane(offset=sign * (bl / 2.0 + 0.014 - 0.0030))
            .center(0.0, bt / 2.0)
            .circle(0.0042)
            .extrude(sign * 0.040)
        )
        stubs = stub if stubs is None else stubs.union(stub)
    mount.visual(
        mesh_from_cadquery(bosses, "cord_bosses"), material=mats["field"], name="cord_bosses", material_class_id="plastic.opaque_glossy_molded"
    )
    mount.visual(
        mesh_from_cadquery(stubs, "cord_stubs"), material=mats["accent"], name="cord_stubs", material_class_id="rubber.smooth_plain"
    )

    _box_inertial(mount, bw, bl, bt, 0.10, bt / 2.0)
    return MountSurface(
        ctrl_z=bt, field_z=bt - 0.0006, act_cy=0.0,
        half_w=(bw - 0.010) / 2.0, half_h=(bl - 0.040) / 2.0,
    )


_MOUNT_BUILDERS = {
    "flat_wall_plate": _build_flat_wall_plate,
    "pendant_box": _build_pendant_box,
    "industrial_enclosure_box": _build_industrial_enclosure_box,
    "inline_cord_barrel": _build_inline_cord_barrel,
}


# ===========================================================================
# Actuator modules (Slot A). Each emits its fixed support hardware as
# parent visuals on `mount` plus the moving part(s) + per-candidate joint.
# Returns (mover_part_names, joint_names).
# ===========================================================================
# ---- roller_bail_drawlatch (REVOLUTE X, gang-capable) ---------------------
_ROLL_KEEP_W = 0.030
_ROLL_KEEP_H = 0.032
_ROLL_KEEP_PROUD = 0.007
_ROLL_HUB_R = 0.0058
_ROLL_HUB_X = 0.022
_ROLL_HUB_LEN = 0.006
_ROLL_ARM_RISE = 0.024
_ROLL_ARM_W = 0.006
_ROLL_ARM_T = 0.006
_ROLL_ROLLER_R = 0.0052
_ROLL_ROLLER_LEN = 0.052
_ROLL_PIVOT_DY = 0.004
_ROLL_PIVOT_DZ = 0.006
_ROLL_LOWER = -0.20
_ROLL_UPPER = 1.30


def _roller_keeper(surf, cx):
    recess = surf.ctrl_z - surf.field_z
    keep = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z)
        .center(cx, surf.act_cy)
        .box(_ROLL_KEEP_W, _ROLL_KEEP_H, recess + _ROLL_KEEP_PROUD, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.004)
    )
    keep_front = surf.field_z + recess + _ROLL_KEEP_PROUD
    for sy in (-1, 1):
        rivet = (
            cq.Workplane("XY")
            .workplane(offset=keep_front - 0.0004)
            .center(cx, surf.act_cy + sy * 0.010)
            .circle(0.0020)
            .extrude(0.0008)
        )
        keep = keep.union(rivet)
    return keep


def _roller_side_bolts(surf, cx):
    pivot_z = surf.ctrl_z + _ROLL_PIVOT_DZ
    pivot_y = surf.act_cy + _ROLL_PIVOT_DY
    bolts = None
    for sx in (-1, 1):
        bx = cx + sx * (_ROLL_HUB_X + 0.004)
        bolt = (
            cq.Workplane("YZ")
            .workplane(offset=bx - _ROLL_HUB_LEN / 2.0)
            .center(pivot_y, pivot_z)
            .circle(0.0046)
            .extrude(_ROLL_HUB_LEN)
        )
        stub_x = cx + sx * (_ROLL_KEEP_W / 2.0 - 0.002)
        stub = (
            cq.Workplane("YZ")
            .workplane(offset=stub_x)
            .center(pivot_y, pivot_z)
            .circle(0.0030)
            .extrude(bx - stub_x)
        )
        part = bolt.union(stub)
        bolts = part if bolts is None else bolts.union(part)
    return bolts


def _roller_bail():
    # Authored in the pivot frame at x=0 (joint origin places it at cx).
    # Shared pivot axle along X through (y=0,z=0) so real geometry sits at the
    # joint origin (the center between the two hubs) for the origin-on-hardware
    # baseline.
    asm = (
        cq.Workplane("YZ")
        .workplane(offset=-(_ROLL_HUB_X + _ROLL_HUB_LEN / 2.0))
        .center(0.0, 0.0)
        .circle(_ROLL_HUB_R * 0.5)
        .extrude(2.0 * (_ROLL_HUB_X + _ROLL_HUB_LEN / 2.0))
    )
    for sx in (-1, 1):
        cxh = sx * _ROLL_HUB_X
        hub = (
            cq.Workplane("YZ")
            .workplane(offset=cxh - _ROLL_HUB_LEN / 2.0)
            .center(0.0, 0.0)
            .circle(_ROLL_HUB_R)
            .extrude(_ROLL_HUB_LEN)
        )
        arm = (
            cq.Workplane("XY")
            .center(cxh, _ROLL_ARM_RISE / 2.0)
            .box(_ROLL_ARM_W, _ROLL_ARM_RISE, _ROLL_ARM_T, centered=(True, True, True))
            .edges("|Z")
            .fillet(0.0015)
        )
        stub = (
            cq.Workplane("YZ")
            .workplane(offset=cxh - _ROLL_HUB_LEN / 2.0)
            .center(_ROLL_ARM_RISE, 0.0)
            .circle(_ROLL_ROLLER_R + 0.0010)
            .extrude(_ROLL_HUB_LEN)
        )
        part = hub.union(arm).union(stub)
        asm = part if asm is None else asm.union(part)
    return asm


def _roller_roller():
    return (
        cq.Workplane("YZ")
        .workplane(offset=-_ROLL_ROLLER_LEN / 2.0)
        .center(_ROLL_ARM_RISE, 0.0)
        .circle(_ROLL_ROLLER_R)
        .extrude(_ROLL_ROLLER_LEN)
    )


def _build_roller(model, mount, surf, mats, r):
    movers, joints = [], []
    pivot_z = surf.ctrl_z + _ROLL_PIVOT_DZ
    pivot_y = surf.act_cy + _ROLL_PIVOT_DY
    lo = _ROLL_LOWER * r.throw_scale
    hi = _ROLL_UPPER * r.throw_scale
    for i, cx in enumerate(_unit_centers(r)):
        mount.visual(
            mesh_from_cadquery(_roller_keeper(surf, cx), f"keeper_block_{i}"),
            material=mats["support"],
            name=f"keeper_block_{i}", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte"),
        )
        mount.visual(
            mesh_from_cadquery(_roller_side_bolts(surf, cx), f"side_bolts_{i}"),
            material=mats["detail"],
            name=f"side_bolts_{i}", material_class_id="metal.steel_bare",
        )
        bail = model.part(f"bail_{i}")
        bail.visual(
            mesh_from_cadquery(_roller_bail(), f"bail_{i}_arms"),
            material=mats["mover"],
            name="bail_arms", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "matte_black"} else "metal.blackened_gunmetal"),
        )
        bail.visual(
            mesh_from_cadquery(_roller_roller(), f"bail_{i}_roller"),
            material=mats["accent"],
            name="roller", material_class_id=("metal.brushed_silver" if r.palette_style == "matte_black" else "metal.blackened_gunmetal"),
        )
        _box_inertial(bail, _ROLL_ROLLER_LEN, _ROLL_ARM_RISE, 0.012, 0.03, _ROLL_ARM_RISE / 2.0)
        jn = f"plate_to_bail_{i}"
        model.articulation(
            jn,
            ArticulationType.REVOLUTE,
            parent=mount,
            child=bail,
            origin=Origin(xyz=(cx, pivot_y, pivot_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=lo, upper=hi),
        )
        movers.append(f"bail_{i}")
        joints.append(jn)
    return movers, joints


# ---- flip_toggle_dolly (REVOLUTE X) ---------------------------------------
_TOG_BOSS_W = 0.034
_TOG_BOSS_H = 0.046
_TOG_BOSS_PROUD = 0.0085
_TOG_HUB_R = 0.0042
_TOG_HUB_LEN = 0.020
_TOG_BUSH_R = 0.0049
_TOG_EAR_LEN = 0.0055
_TOG_LEVER_LEN = 0.027
_TOG_STEM_R = 0.0024
_TOG_STEM_Z = 0.0030
_TOG_PAD_W = 0.014
_TOG_PAD_H = 0.010
_TOG_PAD_T = 0.006
_TOG_PIVOT_DY = 0.004
_TOG_LOWER = math.radians(-10.0)
_TOG_UPPER = math.radians(9.0)


def _toggle_boss(surf):
    recess = surf.ctrl_z - surf.field_z
    pivot_z = surf.ctrl_z + _TOG_BOSS_PROUD + _TOG_HUB_R + 0.0003
    pivot_y = surf.act_cy + _TOG_PIVOT_DY
    boss_front = surf.ctrl_z + _TOG_BOSS_PROUD
    boss = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z)
        .center(0.0, surf.act_cy)
        .box(_TOG_BOSS_W, _TOG_BOSS_H, recess + _TOG_BOSS_PROUD, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.004)
    )
    for sx in (-1, 1):
        cx = sx * (_TOG_HUB_LEN / 2.0 + _TOG_EAR_LEN / 2.0)
        bridge = (
            cq.Workplane("XY")
            .workplane(offset=boss_front - 0.0008)
            .center(cx, pivot_y)
            .box(
                _TOG_EAR_LEN, 2.0 * _TOG_BUSH_R,
                pivot_z - boss_front + _TOG_BUSH_R + 0.0010,
                centered=(True, True, False),
            )
            .edges("|Z")
            .fillet(0.0015)
        )
        ear = (
            cq.Workplane("YZ")
            .workplane(offset=cx - _TOG_EAR_LEN / 2.0)
            .center(pivot_y, pivot_z)
            .circle(_TOG_BUSH_R)
            .extrude(_TOG_EAR_LEN)
        )
        boss = boss.union(bridge).union(ear)
    return boss


def _toggle_lever():
    hub = (
        cq.Workplane("YZ")
        .workplane(offset=-_TOG_HUB_LEN / 2.0)
        .center(0.0, 0.0)
        .circle(_TOG_HUB_R)
        .extrude(_TOG_HUB_LEN)
    )
    stem = (
        cq.Workplane("XZ").workplane(offset=0.0).center(0.0, _TOG_STEM_Z).circle(_TOG_STEM_R).extrude(_TOG_LEVER_LEN)
    )
    pad = (
        cq.Workplane("XY")
        .workplane(offset=_TOG_STEM_Z - _TOG_PAD_T / 2.0)
        .center(0.0, _TOG_LEVER_LEN + _TOG_PAD_H / 2.0 - 0.0015)
        .box(_TOG_PAD_W, _TOG_PAD_H, _TOG_PAD_T, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.003)
    )
    web = (
        cq.Workplane("XY")
        .workplane(offset=-0.0015)
        .center(0.0, _TOG_LEVER_LEN / 2.0)
        .box(_TOG_STEM_R * 1.6, _TOG_LEVER_LEN + 0.004, 0.0045, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.0010)
    )
    return hub.union(stem).union(web).union(pad)


def _build_toggle(model, mount, surf, mats, r):
    pivot_z = surf.ctrl_z + _TOG_BOSS_PROUD + _TOG_HUB_R + 0.0003
    pivot_y = surf.act_cy + _TOG_PIVOT_DY
    mount.visual(
        mesh_from_cadquery(_toggle_boss(surf), "raised_boss"),
        material=mats["support"],
        name="raised_boss", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte"),
    )
    toggle = model.part("toggle")
    toggle.visual(
        mesh_from_cadquery(_toggle_lever(), "toggle_lever"),
        material=mats["mover"],
        name="toggle_lever", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "matte_black"} else "metal.blackened_gunmetal"),
    )
    _box_inertial(toggle, _TOG_PAD_W, _TOG_LEVER_LEN, _TOG_PAD_T, 0.015, _TOG_LEVER_LEN / 2.0)
    model.articulation(
        "plate_to_toggle",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=toggle,
        origin=Origin(xyz=(0.0, pivot_y, pivot_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=4.0,
            lower=_TOG_LOWER * r.throw_scale, upper=_TOG_UPPER * r.throw_scale,
        ),
    )
    return ["toggle"], ["plate_to_toggle"]


# ---- rocker_paddle (REVOLUTE X) -------------------------------------------
_RK_PADDLE_W = 0.058
_RK_PADDLE_H = 0.046
_RK_PADDLE_T = 0.0068
_RK_STANDOFF = 0.0012
_RK_FOOT_W = _RK_PADDLE_W - 0.010
_RK_FOOT_H = 0.0040
_RK_WELL_PROUD = 0.0014
_RK_LOWER = -0.24
_RK_UPPER = 0.24


def _rocker_well(surf):
    outer = _chamfer_rect(_RK_PADDLE_W + 0.012, _RK_PADDLE_H + 0.012, 0.007)
    inner = _chamfer_rect(_RK_PADDLE_W + 0.004, _RK_PADDLE_H + 0.004, 0.003)
    well = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z)
        .center(0.0, surf.act_cy)
        .polyline(outer)
        .close()
        .extrude(_RK_WELL_PROUD)
        .edges("|Z")
        .fillet(0.0016)
    )
    cutter = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z - 0.0005)
        .center(0.0, surf.act_cy)
        .polyline(inner)
        .close()
        .extrude(_RK_WELL_PROUD + 0.0012)
    )
    return well.cut(cutter)


def _rocker_paddle():
    shell = (
        cq.Workplane("XY")
        .workplane(offset=_RK_STANDOFF)
        .box(_RK_PADDLE_W, _RK_PADDLE_H, _RK_PADDLE_T, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.006)
        .faces(">Z")
        .edges()
        .fillet(0.0018)
    )
    foot = (
        cq.Workplane("XY")
        .box(_RK_FOOT_W, _RK_FOOT_H, _RK_STANDOFF + 0.00015, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.0016)
    )
    return shell.union(foot)


def _rocker_mark(top: bool):
    front_z = _RK_STANDOFF + _RK_PADDLE_T - 0.00065
    sgn = 1.0 if top else -1.0
    return (
        cq.Workplane("XY")
        .workplane(offset=front_z)
        .center(0.0, sgn * _RK_PADDLE_H * 0.25)
        .box(0.0022, 0.0100, 0.00095, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.00045)
    )


def _build_rocker(model, mount, surf, mats, r):
    mount.visual(
        mesh_from_cadquery(_rocker_well(surf), "rocker_well"),
        material=mats["support"],
        name="rocker_well", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte"),
    )
    paddle = model.part("rocker_paddle")
    paddle.visual(
        mesh_from_cadquery(_rocker_paddle(), "paddle_shell"),
        material=mats["mover"],
        name="paddle_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    paddle.visual(
        mesh_from_cadquery(_rocker_mark(True), "top_mark"),
        material=mats["accent"],
        name="top_mark", material_class_id="plastic.opaque_generic",
    )
    paddle.visual(
        mesh_from_cadquery(_rocker_mark(False), "bottom_mark"),
        material=mats["accent"],
        name="bottom_mark", material_class_id="plastic.opaque_generic",
    )
    _box_inertial(paddle, _RK_PADDLE_W, _RK_PADDLE_H, _RK_PADDLE_T, 0.02, _RK_PADDLE_T / 2.0)
    # Pivot on the field contact plane (paddle foot touches at local z=0).
    model.articulation(
        "plate_to_paddle",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=paddle,
        origin=Origin(xyz=(0.0, surf.act_cy, surf.field_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=4.0,
            lower=_RK_LOWER * r.throw_scale, upper=_RK_UPPER * r.throw_scale,
        ),
    )
    return ["rocker_paddle"], ["plate_to_paddle"]


# ---- rotary_cam_selector (REVOLUTE Z) -------------------------------------
_RO_MOUNT_R = 0.024
_RO_MOUNT_PROUD = 0.0035
_RO_RING_R = 0.022
_RO_RING_W = 0.0028
_RO_SKIRT_R = 0.0195
_RO_SKIRT_T = 0.0042
_RO_CAP_R = 0.0120
_RO_CAP_H = 0.0080
_RO_HANDLE_W = 0.010
_RO_HANDLE_L = 0.031
_RO_HANDLE_H = 0.0055
_RO_POINTER_W = 0.007
_RO_POINTER_LEN = 0.020
_RO_POINTER_T = 0.0014
_RO_LOWER = -0.85
_RO_UPPER = 0.85


def _rotary_mount(surf):
    recess = surf.ctrl_z - surf.field_z
    seat_z = surf.ctrl_z + _RO_MOUNT_PROUD
    base = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z)
        .center(0.0, surf.act_cy)
        .circle(_RO_MOUNT_R)
        .extrude(recess + _RO_MOUNT_PROUD)
    )
    ring_o = (
        cq.Workplane("XY")
        .workplane(offset=seat_z - 0.0008)
        .center(0.0, surf.act_cy)
        .circle(_RO_RING_R)
        .extrude(0.0008)
    )
    ring_i = (
        cq.Workplane("XY")
        .workplane(offset=seat_z - 0.0010)
        .center(0.0, surf.act_cy)
        .circle(_RO_RING_R - _RO_RING_W)
        .extrude(0.0012)
    )
    base = base.union(ring_o.cut(ring_i))
    screw_circle = _RO_MOUNT_R - 0.0020
    for i in range(4):
        angle = math.pi / 4.0 + i * math.pi / 2.0
        sx = screw_circle * math.cos(angle)
        sy = surf.act_cy + screw_circle * math.sin(angle)
        screw = (
            cq.Workplane("XY")
            .workplane(offset=seat_z - 0.00065)
            .center(sx, sy)
            .circle(0.00155)
            .extrude(0.00055)
        )
        base = base.union(screw)
    return base


def _rotary_knob():
    skirt = cq.Workplane("XY").circle(_RO_SKIRT_R).extrude(_RO_SKIRT_T)
    cap = (
        cq.Workplane("XY")
        .workplane(offset=_RO_SKIRT_T - 0.00025)
        .circle(_RO_CAP_R)
        .extrude(_RO_CAP_H + 0.00025)
    )
    handle = (
        cq.Workplane("XY")
        .workplane(offset=_RO_SKIRT_T + _RO_CAP_H - 0.00035)
        .center(0.0, _RO_HANDLE_L / 2.0 - 0.004)
        .box(_RO_HANDLE_W, _RO_HANDLE_L, _RO_HANDLE_H, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.0020)
    )
    return skirt.union(cap).union(handle)


def _rotary_pointer():
    pts = [
        (-_RO_POINTER_W / 2.0, 0.0),
        (_RO_POINTER_W / 2.0, 0.0),
        (0.0, _RO_POINTER_LEN),
    ]
    return (
        cq.Workplane("XY")
        .workplane(offset=_RO_SKIRT_T + _RO_CAP_H + _RO_HANDLE_H - 0.00045)
        .polyline(pts)
        .close()
        .extrude(_RO_POINTER_T)
    )


def _build_rotary(model, mount, surf, mats, r):
    seat_z = surf.ctrl_z + _RO_MOUNT_PROUD
    mount.visual(
        mesh_from_cadquery(_rotary_mount(surf), "rotary_mount"),
        material=mats["support"],
        name="rotary_mount", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte"),
    )
    knob = model.part("selector_knob")
    knob.visual(
        mesh_from_cadquery(_rotary_knob(), "knob_skirt"),
        material=mats["mover"],
        name="knob_skirt", material_class_id="plastic.opaque_glossy_molded",
    )
    knob.visual(
        mesh_from_cadquery(_rotary_pointer(), "pointer_skirt"),
        material=mats["trim"],
        name="pointer_skirt", material_class_id="plastic.opaque_glossy_molded",
    )
    _box_inertial(knob, 2.0 * _RO_SKIRT_R, _RO_HANDLE_L, _RO_CAP_H, 0.02, _RO_CAP_H / 2.0)
    model.articulation(
        "plate_to_selector",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=knob,
        origin=Origin(xyz=(0.0, surf.act_cy, seat_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=1.0, velocity=3.0,
            lower=_RO_LOWER * r.throw_scale, upper=_RO_UPPER * r.throw_scale,
        ),
    )
    return ["selector_knob"], ["plate_to_selector"]


# ---- pushbutton_cap (PRISMATIC -Z) ----------------------------------------
_PB_BEZEL_OUTER_R = 0.0235
_PB_BEZEL_BORE_R = 0.0182
_PB_BEZEL_PROUD = 0.0048
_PB_BTN_R = 0.0162
_PB_FACE_H = 0.0072
_PB_SKIRT_R = 0.0128
_PB_SKIRT_INSERT = 0.0042
_PB_TRAVEL = 0.0040


def _pushbutton_bezel(surf):
    recess = surf.ctrl_z - surf.field_z
    bezel = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z)
        .center(0.0, surf.act_cy)
        .circle(_PB_BEZEL_OUTER_R)
        .circle(_PB_BEZEL_BORE_R)
        .extrude(recess + _PB_BEZEL_PROUD)
    )
    return bezel


def _pushbutton_bore_shadow(surf):
    return (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z - 0.0008)
        .center(0.0, surf.act_cy)
        .circle(_PB_BEZEL_BORE_R)
        .circle(_PB_SKIRT_R)
        .extrude(_PB_BEZEL_PROUD + 0.0012 + (surf.ctrl_z - surf.field_z))
    )


def _pushbutton_cap():
    skirt = (
        cq.Workplane("XY")
        .workplane(offset=-_PB_SKIRT_INSERT)
        .circle(_PB_SKIRT_R)
        .extrude(_PB_SKIRT_INSERT + 0.0012)
    )
    face = (
        cq.Workplane("XY").workplane(offset=0.0004).circle(_PB_BTN_R).extrude(_PB_FACE_H)
    )
    cap = skirt.union(face)
    groove = (
        cq.Workplane("XY")
        .workplane(offset=_PB_FACE_H + 0.0001)
        .circle(_PB_BTN_R * 0.68)
        .extrude(0.0010)
    )
    return cap.cut(groove)


def _build_pushbutton(model, mount, surf, mats, r):
    seat_z = surf.ctrl_z + _PB_BEZEL_PROUD
    mount.visual(
        mesh_from_cadquery(_pushbutton_bezel(surf), "button_bezel"),
        material=mats["support"],
        name="button_bezel", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte"),
    )
    mount.visual(
        mesh_from_cadquery(_pushbutton_bore_shadow(surf), "bore_shadow"),
        material=mats["field"],
        name="bore_shadow", material_class_id="plastic.opaque_generic",
    )
    button = model.part("button_cap")
    button.visual(
        mesh_from_cadquery(_pushbutton_cap(), "button_cap"),
        material=mats["mover"],
        name="button_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    _box_inertial(button, 2.0 * _PB_BTN_R, 2.0 * _PB_BTN_R, _PB_FACE_H, 0.01, _PB_FACE_H / 2.0)
    travel = _PB_TRAVEL * r.throw_scale
    model.articulation(
        "plate_to_button",
        ArticulationType.PRISMATIC,
        parent=mount,
        child=button,
        origin=Origin(xyz=(0.0, surf.act_cy, seat_z)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=6.0, velocity=0.25, lower=0.0, upper=travel),
    )
    return ["button_cap"], ["plate_to_button"]


# ---- grab_handle_slider (PRISMATIC +Y) ------------------------------------
_SL_FACE_W = 0.030
_SL_FACE_H = 0.044
_SL_FACE_PROUD = 0.0040
_SL_SLOT_W = 0.0095
_SL_SLOT_H = 0.030
_SL_BLOCK_W = 0.0072
_SL_BLOCK_H = 0.0098
_SL_CLEAR = 0.0010
_SL_TRAVEL = _SL_SLOT_H - _SL_BLOCK_H - 2.0 * _SL_CLEAR


def _slider_face(surf):
    recess = surf.ctrl_z - surf.field_z
    plate = (
        cq.Workplane("XY")
        .workplane(offset=surf.field_z)
        .center(0.0, surf.act_cy)
        .polyline(_octagon(_SL_FACE_W, _SL_FACE_H, 0.0045))
        .close()
        .extrude(recess + _SL_FACE_PROUD)
        .edges("|Z")
        .fillet(0.0012)
    )
    face_front = surf.ctrl_z + _SL_FACE_PROUD
    slot = (
        cq.Workplane("XY")
        .workplane(offset=face_front + 0.001)
        .center(0.0, surf.act_cy)
        .rect(_SL_SLOT_W, _SL_SLOT_H)
        .extrude(-(_SL_FACE_PROUD + 0.0016))
        .edges("|Z")
        .fillet(0.0018)
    )
    return plate.cut(slot)


def _slider_handle(surf):
    # Authored about the joint origin: local z=0 sits on the control face.
    face_front = surf.ctrl_z + _SL_FACE_PROUD
    block_front = face_front + 0.0006
    block_back = surf.field_z - 0.0003
    block = (
        cq.Workplane("XY")
        .workplane(offset=block_back - surf.ctrl_z)
        .rect(_SL_BLOCK_W, _SL_BLOCK_H)
        .extrude(block_front - block_back)
        .edges("|Z")
        .fillet(0.0010)
    )
    loop_cy = -0.0032
    loop_z = (block_front - surf.ctrl_z) + 0.0008
    ring_o = (
        cq.Workplane("XY").center(0.0, loop_cy).workplane(offset=loop_z).circle(0.0072).extrude(0.0030)
    )
    ring_i = (
        cq.Workplane("XY").center(0.0, loop_cy).workplane(offset=loop_z - 0.0004).circle(0.0040).extrude(0.0038)
    )
    neck = (
        cq.Workplane("XY")
        .center(0.0, -0.0022)
        .workplane(offset=(block_front - surf.ctrl_z) - 0.0008)
        .rect(0.0036, 0.0084)
        .extrude(0.0030)
    )
    return block.union(neck).union(ring_o.cut(ring_i))


def _build_slider(model, mount, surf, mats, r):
    mount.visual(
        mesh_from_cadquery(_slider_face(surf), "selector_faceplate"),
        material=mats["support"],
        name="selector_faceplate", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "abs_gray", "industrial_yellow", "safety_red", "matte_black"} else "metal.stainless_matte"),
    )
    slider = model.part("slider")
    slider.visual(
        mesh_from_cadquery(_slider_handle(surf), "slide_handle"),
        material=mats["mover"],
        name="slide_handle", material_class_id=("metal.brushed_silver" if r.palette_style in {"brushed_steel", "matte_black"} else "metal.blackened_gunmetal"),
    )
    _box_inertial(slider, _SL_BLOCK_W, _SL_BLOCK_H, 0.006, 0.01, 0.002)
    # Rest = slider parked at the bottom of the slot; joint origin on the face.
    rest_cy = surf.act_cy - _SL_SLOT_H / 2.0 + _SL_CLEAR + _SL_BLOCK_H / 2.0
    travel = _SL_TRAVEL * r.throw_scale
    model.articulation(
        "mount_to_slider",
        ArticulationType.PRISMATIC,
        parent=mount,
        child=slider,
        origin=Origin(xyz=(0.0, rest_cy, surf.ctrl_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=0.1, lower=0.0, upper=travel),
    )
    return ["slider"], ["mount_to_slider"]


_ACTUATOR_BUILDERS = {
    "roller_bail_drawlatch": _build_roller,
    "flip_toggle_dolly": _build_toggle,
    "rocker_paddle": _build_rocker,
    "rotary_cam_selector": _build_rotary,
    "pushbutton_cap": _build_pushbutton,
    "grab_handle_slider": _build_slider,
}

# Per-candidate consumer joint contract (CRITICAL — never one hard-coded axis).
ACTUATOR_JOINT = {
    "roller_bail_drawlatch": (ArticulationType.REVOLUTE, (1.0, 0.0, 0.0)),
    "flip_toggle_dolly": (ArticulationType.REVOLUTE, (1.0, 0.0, 0.0)),
    "rocker_paddle": (ArticulationType.REVOLUTE, (1.0, 0.0, 0.0)),
    "rotary_cam_selector": (ArticulationType.REVOLUTE, (0.0, 0.0, 1.0)),
    "pushbutton_cap": (ArticulationType.PRISMATIC, (0.0, 0.0, -1.0)),
    "grab_handle_slider": (ArticulationType.PRISMATIC, (0.0, 1.0, 0.0)),
}


# ===========================================================================
# Build
# ===========================================================================
def build_power_switch(
    config: PowerSwitchConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"ps_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    surf = _MOUNT_BUILDERS[r.mount_style](model, r, mats)
    mount = model.get_part("mount")
    _ACTUATOR_BUILDERS[r.actuator_style](model, mount, surf, mats, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_power_switch(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_power_switch(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def _allow_actuator_overlaps(ctx, model, r):
    mount = model.get_part("mount")
    if r.actuator_style == "roller_bail_drawlatch":
        for i in range(r.gang_count):
            bail = model.get_part(f"bail_{i}")
            ctx.allow_overlap(
                mount, bail, elem_a=f"side_bolts_{i}", elem_b="bail_arms",
                reason="Roller bail pivot hubs are captured around the fixed side bolts.",
            )
            ctx.allow_overlap(
                mount, bail, elem_a=f"keeper_block_{i}", elem_b="bail_arms",
                reason="Roller bail hub straddles the fixed keeper block at rest.",
            )
    elif r.actuator_style == "flip_toggle_dolly":
        toggle = model.get_part("toggle")
        ctx.allow_overlap(
            mount, toggle, elem_a="raised_boss", elem_b="toggle_lever",
            reason="Toggle hub is captured between the raised boss ears.",
        )
    elif r.actuator_style == "rocker_paddle":
        paddle = model.get_part("rocker_paddle")
        ctx.allow_overlap(
            mount, paddle, elem_a="rocker_well", elem_b="paddle_shell",
            reason="Rocker paddle see-saws inside the molded well.",
        )
    elif r.actuator_style == "rotary_cam_selector":
        knob = model.get_part("selector_knob")
        ctx.allow_overlap(
            mount, knob, elem_a="rotary_mount", elem_b="knob_skirt",
            reason="Rotary knob skirt seats on the escutcheon mount face.",
        )
    elif r.actuator_style == "pushbutton_cap":
        button = model.get_part("button_cap")
        ctx.allow_overlap(
            mount, button, elem_a="button_bezel", elem_b="button_cap",
            reason="Button skirt rides inside the bezel through-bore.",
        )
        ctx.allow_overlap(
            mount, button, elem_a="bore_shadow", elem_b="button_cap",
            reason="Button skirt rides inside the bore shadow sleeve.",
        )
    else:  # grab_handle_slider
        slider = model.get_part("slider")
        ctx.allow_overlap(
            mount, slider, elem_a="selector_faceplate", elem_b="slide_handle",
            reason="Grab-handle slider block rides inside the faceplate slot.",
        )


def run_power_switch_tests(
    object_model: ArticulatedObject,
    config: PowerSwitchConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    mount = object_model.get_part("mount")

    _allow_actuator_overlaps(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Root / identity. ----
    ctx.check(
        "mount is the single root",
        mount in object_model.root_parts() and len(object_model.root_parts()) == 1,
        details=f"roots={[p.name for p in object_model.root_parts()]}",
    )

    # ---- Per-candidate consumer joint type + axis (CRITICAL). ----
    want_type, want_axis = ACTUATOR_JOINT[r.actuator_style]
    if r.actuator_style == "roller_bail_drawlatch":
        joint_names = [f"plate_to_bail_{i}" for i in range(r.gang_count)]
    else:
        joint_names = {
            "flip_toggle_dolly": ["plate_to_toggle"],
            "rocker_paddle": ["plate_to_paddle"],
            "rotary_cam_selector": ["plate_to_selector"],
            "pushbutton_cap": ["plate_to_button"],
            "grab_handle_slider": ["mount_to_slider"],
        }[r.actuator_style]
    for jn in joint_names:
        j = object_model.get_articulation(jn)
        ax = tuple(float(a) for a in j.axis)
        type_ok = j.articulation_type == want_type
        axis_ok = all(abs(ax[k] - want_axis[k]) < 1e-6 for k in range(3))
        ctx.check(
            f"{jn}: correct per-candidate joint type",
            type_ok,
            details=f"type={j.articulation_type} want={want_type}",
        )
        ctx.check(
            f"{jn}: correct per-candidate joint axis",
            axis_ok,
            details=f"axis={ax} want={want_axis}",
        )
        lo = float(j.motion_limits.lower)
        hi = float(j.motion_limits.upper)
        ctx.check(
            f"{jn}: finite limited throw (not free)",
            hi > lo and (hi - lo) < (2.0 * math.pi - 0.01),
            details=f"lower={lo} upper={hi}",
        )

    # ---- Actuator support hardware present (its own support, swapped with it). ----
    support_visual = {
        "roller_bail_drawlatch": "keeper_block_0",
        "flip_toggle_dolly": "raised_boss",
        "rocker_paddle": "rocker_well",
        "rotary_cam_selector": "rotary_mount",
        "pushbutton_cap": "button_bezel",
        "grab_handle_slider": "selector_faceplate",
    }[r.actuator_style]
    mount_visuals = {v.name for v in mount.visuals}
    ctx.check(
        "actuator support hardware is a mount parent visual (Rule 1)",
        support_visual in mount_visuals,
        details=f"support={support_visual} mount_visuals={sorted(mount_visuals)}",
    )

    # ---- Mount decorations are parent visuals, not separate parts (Rule 1). ----
    deco = {
        "flat_wall_plate": {"louver_pad", "mount_screws"},
        "pendant_box": {"gland_collar", "conduit_tubes"},
        "industrial_enclosure_box": {"lid_lip", "lug_bosses"},
        "inline_cord_barrel": {"cord_bosses", "cord_stubs"},
    }[r.mount_style]
    ctx.check(
        "mount decorations are parent visuals (Rule 1)",
        deco <= mount_visuals,
        details=f"want={sorted(deco)} have={sorted(mount_visuals)}",
    )

    # ---- Gang gating + copy logic. ----
    if r.mount_style == GANG_MOUNT and r.actuator_style == GANG_ACTUATOR:
        ctx.check(
            "gang plate widens with N",
            r.plate_w >= r.gang_count * r.unit_pitch + 0.022 - 1e-6,
            details=f"plate_w={r.plate_w:.4f} N={r.gang_count} pitch={r.unit_pitch:.4f}",
        )
        bail_parts = [p.name for p in object_model.parts if p.name.startswith("bail_")]
        ctx.check(
            "one moving bail part per gang unit",
            len(bail_parts) == r.gang_count,
            details=f"bails={sorted(bail_parts)} N={r.gang_count}",
        )
        # Independent units: actuating one bail must not move another.
        if r.gang_count >= 2:
            j0 = object_model.get_articulation("plate_to_bail_0")
            other = object_model.get_part("bail_1")
            rest = ctx.part_world_aabb(other)
            with ctx.pose({j0: _ROLL_UPPER * 0.6}):
                moved = ctx.part_world_aabb(other)
            if rest is not None and moved is not None:
                same = abs(rest[0][2] - moved[0][2]) < 1e-4 and abs(rest[1][2] - moved[1][2]) < 1e-4
                ctx.check(
                    "gang units are independent (one bail does not drive another)",
                    same,
                    details=f"rest={rest} moved={moved}",
                )
    else:
        ctx.check(
            "non-gang combos are forced to N=1",
            r.gang_count == 1,
            details=f"mount={r.mount_style} actuator={r.actuator_style} N={r.gang_count}",
        )

    # ---- inline barrel never hosts a roller / rotary (compatibility cut). ----
    if r.mount_style == "inline_cord_barrel":
        ctx.check(
            "inline barrel hosts only compact actuators",
            r.actuator_style in BARREL_ACTUATORS,
            details=f"actuator={r.actuator_style}",
        )

    # ---- Actuator actually moves about its declared joint. ----
    if r.actuator_style == "pushbutton_cap":
        j = object_model.get_articulation("plate_to_button")
        button = object_model.get_part("button_cap")
        rest = ctx.part_world_aabb(button)
        with ctx.pose({j: float(j.motion_limits.upper)}):
            pressed = ctx.part_world_aabb(button)
        if rest is not None and pressed is not None:
            ctx.check(
                "pushbutton presses inward (-Z)",
                pressed[1][2] < rest[1][2] - 0.0010,
                details=f"rest_z={rest[1][2]:.4f} pressed_z={pressed[1][2]:.4f}",
            )
    elif r.actuator_style == "grab_handle_slider":
        j = object_model.get_articulation("mount_to_slider")
        slider = object_model.get_part("slider")
        rest = ctx.part_world_aabb(slider)
        with ctx.pose({j: float(j.motion_limits.upper)}):
            up = ctx.part_world_aabb(slider)
        if rest is not None and up is not None:
            ctx.check(
                "slider travels up the slot (+Y)",
                up[0][1] > rest[0][1] + 0.006,
                details=f"rest_y={rest[0][1]:.4f} up_y={up[0][1]:.4f}",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with gang encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "PowerSwitchConfig",
    "ResolvedPowerSwitchConfig",
    "build_power_switch",
    "build_seeded_power_switch",
    "config_from_seed",
    "resolve_config",
    "run_power_switch_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
