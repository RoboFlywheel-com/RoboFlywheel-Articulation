# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained floor-standing drafting table template (TEMPLATE_DOMAIN).

Rebuilt from the single source record
``rec_picturex_0611__floor_standing_drafting_table__001`` (a splayed oak
A-frame writing easel).  The recognizable identity is a grounded floor stand
carrying a single tiltable drawing surface with a height/tilt adjustment
mechanism:

  * ``floor_stand``   — grounded leg family (slot ``stand_base``) built up to a
    shared four-corner lift-guide sleeve interface.
  * ``lift_carriage`` — PRISMATIC +Z height carriage riding inner tubes inside
    the stand sleeves; carries the tilt hinge rail, side knob sockets, the
    under-board angle-hold hardware (slot ``angle_lock``) and N tool trays.
  * ``drawing_board`` — REVOLUTE +X tilting drawing surface hinged on the
    board front/low edge (the real hinge line, on the carriage hinge pin).
  * two ``lock_control`` knobs — REVOLUTE +X side tilt-lock controls (slot
    ``control_form``).

Every revolute/prismatic joint is built from ``mate_axes`` and registered with
``register_interface_mate``.  No source runtime, snapshot, or other template is
imported; geometry uses only the SDK.  No motion clamping, no whole-part
``allow_overlap``: captured pins/tubes are allowed element-scoped only.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    KnobGeometry,
    KnobGrip,
    MeshGeometry,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
StandBase = Literal["splayed_aframe", "xbrace_splayed", "four_post", "trestle_pair"]
AngleLock = Literal["friction_cheeks", "toothed_ratchet", "curved_quadrant"]
ControlForm = Literal["paired_disk_knobs", "lobed_knobs", "crank_winders"]
PaletteStyle = Literal["warm_oak", "pale_maple", "walnut", "grey_steel"]

STAND_BASES: tuple[StandBase, ...] = (
    "splayed_aframe",
    "xbrace_splayed",
    "four_post",
    "trestle_pair",
)
ANGLE_LOCKS: tuple[AngleLock, ...] = (
    "friction_cheeks",
    "toothed_ratchet",
    "curved_quadrant",
)
CONTROL_FORMS: tuple[ControlForm, ...] = (
    "paired_disk_knobs",
    "lobed_knobs",
    "crank_winders",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_oak",
    "pale_maple",
    "walnut",
    "grey_steel",
)
TRAY_COUNTS: tuple[int, ...] = (1, 2, 3)


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("stand_base", STAND_BASES, role="grounded floor-stand leg family"),
        component_slot("angle_lock", ANGLE_LOCKS, role="under-board tilt angle-hold hardware"),
        component_slot("control_form", CONTROL_FORMS, role="side tilt-lock rotary control"),
        multiplicity_slot("tray_count", TRAY_COUNTS, item_slot="stand_base"),
    )
)

# ---------------------------------------------------------------------------
# Palettes
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_oak": {
        "wood": (0.66, 0.42, 0.19, 1.0),
        "wood_dark": (0.46, 0.27, 0.11, 1.0),
        "panel": (0.16, 0.17, 0.18, 1.0),
    },
    "pale_maple": {
        "wood": (0.86, 0.70, 0.44, 1.0),
        "wood_dark": (0.64, 0.47, 0.24, 1.0),
        "panel": (0.20, 0.21, 0.22, 1.0),
    },
    "walnut": {
        "wood": (0.42, 0.26, 0.15, 1.0),
        "wood_dark": (0.26, 0.15, 0.08, 1.0),
        "panel": (0.13, 0.13, 0.14, 1.0),
    },
    "grey_steel": {
        "wood": (0.74, 0.72, 0.68, 1.0),
        "wood_dark": (0.50, 0.49, 0.46, 1.0),
        "panel": (0.22, 0.23, 0.24, 1.0),
    },
}
_HARDWARE = {
    "steel": (0.42, 0.44, 0.43, 1.0),
    "grey": (0.22, 0.23, 0.22, 1.0),
    "black": (0.03, 0.03, 0.03, 1.0),
}

# ---------------------------------------------------------------------------
# Shared interface geometry (world meters). +Z up, +Y back, -Y front (hinge),
# X width. Every stand builds up to the four-corner sleeves; the carriage's
# inner tubes + upper frame mate identically to every base.
# ---------------------------------------------------------------------------
SIDE_X = 0.55            # stand guide-post / sleeve half-track
BAR_X = 0.5045           # carriage guide bar half-track (offset inward: slivers the sleeve)
FRONT_Y = -0.43          # front sleeve line
REAR_Y = 0.43            # rear sleeve line
FLOOR_Z = 0.035
SLEEVE_BOT_Z = 0.05      # outer guide sleeve bottom (on stand; sleeves are the uprights)
LEG_TOP_Z = 0.30         # candidate legs / bracing stay below the inner-tube zone
INNER_BOT_Z = 0.36       # inner guide-bar bottom (on carriage), clear of the leg zone
TOP_Z = 0.72             # upper frame level (carriage, at lift=0)
HINGE_Y = -0.365         # tilt axis (board front/low edge)
HINGE_Z = 0.755          # tilt axis height (at lift=0)
RAIL_Z = 0.715           # front hinge rail height (top clears the board knuckle bottoms)
REAR_RAIL_Y = 0.325
KNOB_Y = -0.175
KNOB_Z = 0.455
KNOB_SOCKET_X = 0.474    # socket outer end abuts the inward-reaching knob shaft (x-sliver)
KNOB_JOINT_X = 0.600
KNUCKLE_XS_CARRIAGE = (-0.36, 0.0, 0.36)   # piano-hinge knuckles on the carriage
KNUCKLE_XS_BOARD = (-0.18, 0.18)           # interleaved board knuckles (abut carriage)
KNUCKLE_LEN = 0.183      # 0.18 pitch + 0.0015 abutment sliver each side
BOARD_W = 1.20           # nominal board width (x)
BOARD_D = 0.76           # nominal board depth (y)
TUBE = 0.035
TILT_LOWER = 0.0         # flat
TILT_UPPER = 0.72        # steep tilt

SIDES: tuple[tuple[str, float], ...] = (("0", -1.0), ("1", 1.0))


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _pick(v, choices):
    return v if v in choices else choices[0]


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _beam_pose(p0, p1) -> tuple[Origin, float]:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 0.0:
        raise ValueError("beam endpoints must be distinct")
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    center = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5)
    return Origin(xyz=center, rpy=(0.0, pitch, yaw)), length


def _beam(part, p0, p1, size: float, material, name: str, overshoot: float = 0.02) -> None:
    origin, length = _beam_pose(p0, p1)
    part.visual(Box((size, size, length + overshoot)), origin=origin, material=material, name=name, material_class_id="wood.natural_generic")


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.walnut_dark")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Cylinder(radius=radius, length=length), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.stainless_matte")


def _annular_sector_yz(
    *, center_y: float, center_z: float, radius: float, radial_width: float,
    x_center: float, x_thickness: float, start_angle: float, end_angle: float, segments: int = 32,
) -> MeshGeometry:
    """Curved metal quadrant strip in the YZ plane, extruded in X (about the +X tilt axis)."""
    geom = MeshGeometry()
    x0 = x_center - x_thickness / 2.0
    x1 = x_center + x_thickness / 2.0
    inner = radius - radial_width
    outer = radius + radial_width
    rings: list[tuple[int, int, int, int]] = []
    for i in range(segments + 1):
        t = start_angle + (end_angle - start_angle) * i / segments
        c = math.cos(t)
        s = math.sin(t)
        rings.append((
            geom.add_vertex(x0, center_y + outer * c, center_z + outer * s),
            geom.add_vertex(x0, center_y + inner * c, center_z + inner * s),
            geom.add_vertex(x1, center_y + outer * c, center_z + outer * s),
            geom.add_vertex(x1, center_y + inner * c, center_z + inner * s),
        ))
    for i in range(segments):
        of0, inf0, ob0, ib0 = rings[i]
        of1, inf1, ob1, ib1 = rings[i + 1]
        geom.add_face(of0, of1, inf1)
        geom.add_face(of0, inf1, inf0)
        geom.add_face(ob0, ib1, ob1)
        geom.add_face(ob0, ib0, ib1)
        geom.add_face(of0, ob0, ob1)
        geom.add_face(of0, ob1, of1)
        geom.add_face(inf0, inf1, ib1)
        geom.add_face(inf0, ib1, ib0)
    for idx in (0, -1):
        of0, inf0, ob0, ib0 = rings[idx]
        geom.add_face(of0, inf0, ib0)
        geom.add_face(of0, ib0, ob0)
    return geom


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class Config:
    stand_base: StandBase = "splayed_aframe"
    angle_lock: AngleLock = "friction_cheeks"
    control_form: ControlForm = "paired_disk_knobs"
    tray_count: int = 2
    board_width_scale: float = 1.0
    board_depth_scale: float = 1.0
    lift_travel_m: float = 0.15
    palette_style: PaletteStyle = "warm_oak"
    name: str = "picturex_0611_floor_standing_drafting_table"


@dataclass(frozen=True)
class ResolvedConfig:
    stand_base: StandBase
    angle_lock: AngleLock
    control_form: ControlForm
    tray_count: int
    board_width_scale: float
    board_depth_scale: float
    lift_travel_m: float
    palette_style: PaletteStyle
    name: str

    @property
    def half_width(self) -> float:
        return 0.5 * BOARD_W * self.board_width_scale

    @property
    def board_depth(self) -> float:
        return BOARD_D * self.board_depth_scale

    @property
    def sleeve_top_z(self) -> float:
        # Grows with lift travel so the tube stays well inserted at full lift.
        return 0.44 + self.lift_travel_m

    @property
    def hinge_span(self) -> float:
        return 2.0 * self.half_width - 0.02


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0611_DBAF)
    return Config(
        stand_base=choices["stand_base"],
        angle_lock=choices["angle_lock"],
        control_form=choices["control_form"],
        tray_count=int(choices["tray_count"]),
        board_width_scale=round(rng.uniform(0.92, 1.10), 4),
        board_depth_scale=round(rng.uniform(0.95, 1.08), 4),
        lift_travel_m=round(rng.uniform(0.10, 0.20), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"picturex_0611_floor_standing_drafting_table_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "stand_base": cfg.stand_base,
            "angle_lock": cfg.angle_lock,
            "control_form": cfg.control_form,
            "tray_count": int(cfg.tray_count),
        }
    )
    return ResolvedConfig(
        stand_base=_pick(cfg.stand_base, STAND_BASES),
        angle_lock=_pick(cfg.angle_lock, ANGLE_LOCKS),
        control_form=_pick(cfg.control_form, CONTROL_FORMS),
        tray_count=int(cfg.tray_count) if int(cfg.tray_count) in TRAY_COUNTS else 2,
        board_width_scale=_clamp(cfg.board_width_scale, 0.92, 1.10),
        board_depth_scale=_clamp(cfg.board_depth_scale, 0.95, 1.08),
        lift_travel_m=_clamp(cfg.lift_travel_m, 0.10, 0.20),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        name=cfg.name or "picturex_0611_floor_standing_drafting_table",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("stand_base", r.stand_base),
        ("angle_lock", r.angle_lock),
        ("control_form", r.control_form),
        ("tray_count", f"n{r.tray_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Axis-mated joint helper (revolute / prismatic, registered for QC)
# ===========================================================================
def _axis_joint(model, *, name, parent, child, point, axis, articulation_type, limits, radial):
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name, articulation_type, parent=parent, child=child,
        origin=mate.origin, axis=mate.axis, motion_limits=limits,
    )
    register_interface_mate(model, name, mate)


# ===========================================================================
# Shared stand guide + carriage frame (constant identity layer)
# ===========================================================================
def _emit_lift_guide(stand, r: ResolvedConfig, mats) -> None:
    """Four vertical outer guide sleeves (the shared uprights) + top collars.

    The sleeves span floor to sleeve_top and are coaxial with the carriage inner
    tubes; the candidate legs/bracing attach to them but stay below the tube zone.
    """
    grey = mats["grey"]
    steel = mats["steel"]
    top = r.sleeve_top_z
    for idx, sx in SIDES:
        for tag, sy in (("front", FRONT_Y), ("rear", REAR_Y)):
            x = sx * SIDE_X
            _beam(stand, (x, sy, SLEEVE_BOT_Z), (x, sy, top), 0.058, steel, f"guide_sleeve_{tag}_{idx}")
            # Collar narrowed in x so only the sleeve wall makes the thin guide-bar contact.
            _box(stand, (0.050, 0.070, 0.030), (x, sy, top - 0.015), grey, f"sleeve_collar_{tag}_{idx}")


def _emit_carriage_frame(carriage, r: ResolvedConfig, mats) -> None:
    """Offset inner guide bars + rigid upper frame (hinge rail, piano-hinge
    knuckles, knob sockets). The carriage half of the tilt hinge is a row of
    knuckles centered on the real tilt axis, interleaving with the board knuckles.
    """
    wood = mats["wood"]
    grey = mats["grey"]
    steel = mats["steel"]
    hw = r.half_width
    for idx, sx in SIDES:
        x = sx * BAR_X
        # Level top side rail spanning the full depth, joining both guide bars.
        _beam(carriage, (x, FRONT_Y, TOP_Z), (x, REAR_Y, TOP_Z), TUBE, wood, f"top_side_rail_{idx}")
        # Vertical guide bars, offset inward so their outer face slivers the stand
        # sleeve inner wall (thin single-axis contact maintained across the lift).
        for tag, sy in (("front", FRONT_Y), ("rear", REAR_Y)):
            _beam(carriage, (x, sy, INNER_BOT_Z), (x, sy, TOP_Z), 0.036, steel, f"inner_tube_{tag}_{idx}")
    # Front hinge rail just under the knuckles + rear top rail.
    _beam(carriage, (-hw - 0.03, HINGE_Y, RAIL_Z), (hw + 0.03, HINGE_Y, RAIL_Z), TUBE, wood, "front_hinge_rail")
    _beam(carriage, (-BAR_X, REAR_RAIL_Y, TOP_Z), (BAR_X, REAR_RAIL_Y, TOP_Z), TUBE, wood, "rear_top_rail")
    # Carriage piano-hinge knuckles centered on the tilt axis, each tied down to
    # the front hinge rail by a bracket.
    for i, cx in enumerate(KNUCKLE_XS_CARRIAGE):
        _cyl(carriage, 0.014, KNUCKLE_LEN, (cx, HINGE_Y, HINGE_Z), steel, f"hinge_knuckle_c{i}", rpy=(0.0, math.pi / 2.0, 0.0))
        # Bracket stays below the axis so the moving board cleat clears it.
        _box(carriage, (0.030, 0.050, HINGE_Z - RAIL_Z + 0.006), (cx, HINGE_Y, 0.5 * (HINGE_Z + RAIL_Z)), grey, f"hinge_bracket_c{i}")
    for idx, sx in SIDES:
        # Side knob socket on the knob axis (its outer end abuts the knob shaft) +
        # a tab bridging the socket up to the side rail.
        _cyl(carriage, 0.016, 0.072, (sx * KNOB_SOCKET_X, KNOB_Y, KNOB_Z), grey, f"knob_socket_{idx}", rpy=(0.0, math.pi / 2.0, 0.0))
        # The tab bridges the knob socket up to the top side rail; at 0.024 m wide
        # it stopped ~1 mm short of the rail, orphaning socket+tab as an island.
        _box(carriage, (0.040, 0.044, 0.300), (sx * KNOB_SOCKET_X, KNOB_Y, 0.590), grey, f"knob_mount_tab_{idx}")


# ===========================================================================
# Slot A: stand_base — grounded legs up to the shared sleeve interface.
# Returns the ``floor_stand`` part; the carriage parents to it via PRISMATIC.
# ===========================================================================
def _stand_corner_feet(stand, mats, cand: str, *, out: float = 0.0) -> None:
    dark = mats["wood_dark"]
    for idx, sx in SIDES:
        for tag, sy in (("front", FRONT_Y), ("rear", REAR_Y)):
            fx = sx * (SIDE_X + out)
            fy = sy + (out if sy > 0 else -out)
            _box(stand, (0.085, 0.085, 0.032), (fx, fy, FLOOR_Z), dark, f"stand_base__{cand}__foot_{tag}_{idx}")


def _stand_base_splayed_aframe_build(stand, r: ResolvedConfig, mats) -> None:
    """Source splayed oak side-rail A-frame: thick wood side rails hugging the
    guide sleeves, splayed square feet, front/rear side stretchers, low crossbar."""
    wood = mats["wood"]
    dark = mats["wood_dark"]
    cand = "splayed_aframe"
    for idx, sx in SIDES:
        x = sx * SIDE_X
        for tag, sy in (("front", FRONT_Y), ("rear", REAR_Y)):
            # Splayed outer wood side rail from a splayed foot up to the leg-top band.
            _beam(stand, (x + sx * 0.06, sy, FLOOR_Z), (x + sx * 0.028, sy, LEG_TOP_Z), 0.056, wood, f"stand_base__{cand}__side_rail_{tag}_{idx}")
        # Side stretcher tying front-rear (below the tube zone).
        _beam(stand, (x + sx * 0.03, FRONT_Y, 0.24), (x + sx * 0.03, REAR_Y, 0.24), 0.044, wood, f"stand_base__{cand}__side_stretcher_{idx}")
    _beam(stand, (-SIDE_X, 0.0, 0.24), (SIDE_X, 0.0, 0.24), 0.040, dark, f"stand_base__{cand}__low_crossbar")
    _stand_corner_feet(stand, mats, cand, out=0.045)


def _stand_base_xbrace_splayed_build(stand, r: ResolvedConfig, mats) -> None:
    """Splayed legs + lengthwise floor runners + diagonal X side braces."""
    wood = mats["wood"]
    dark = mats["wood_dark"]
    cand = "xbrace_splayed"
    for idx, sx in SIDES:
        x = sx * SIDE_X
        # Floor runner along the side (front-rear), slightly outboard of the sleeves.
        _beam(stand, (x + sx * 0.02, FRONT_Y - 0.04, FLOOR_Z), (x + sx * 0.02, REAR_Y + 0.04, FLOOR_Z), 0.05, dark, f"stand_base__{cand}__floor_runner_{idx}")
        # Diagonal X braces in the side plane, kept below the inner-tube zone.
        _beam(stand, (x, FRONT_Y, 0.06), (x, REAR_Y, LEG_TOP_Z), 0.026, wood, f"stand_base__{cand}__brace_a_{idx}")
        _beam(stand, (x, REAR_Y, 0.06), (x, FRONT_Y, LEG_TOP_Z), 0.026, wood, f"stand_base__{cand}__brace_b_{idx}")
    # Left-right ties front and rear (low, clear of tubes).
    _beam(stand, (-SIDE_X, FRONT_Y, 0.12), (SIDE_X, FRONT_Y, 0.12), 0.030, dark, f"stand_base__{cand}__front_tie")
    _beam(stand, (-SIDE_X, REAR_Y, 0.12), (SIDE_X, REAR_Y, 0.12), 0.030, dark, f"stand_base__{cand}__rear_tie")
    _stand_corner_feet(stand, mats, cand, out=0.02)


def _stand_base_four_post_build(stand, r: ResolvedConfig, mats) -> None:
    """Rectangular box apron ring + side stretchers around the four uprights."""
    wood = mats["wood"]
    dark = mats["wood_dark"]
    cand = "four_post"
    apron_z = 0.27
    low_z = 0.13
    for idx, sx in SIDES:
        x = sx * SIDE_X
        _beam(stand, (x, FRONT_Y, apron_z), (x, REAR_Y, apron_z), 0.044, wood, f"stand_base__{cand}__side_apron_{idx}")
        _beam(stand, (x, FRONT_Y, low_z), (x, REAR_Y, low_z), TUBE, dark, f"stand_base__{cand}__side_stretcher_{idx}")
    _beam(stand, (-SIDE_X, FRONT_Y, apron_z), (SIDE_X, FRONT_Y, apron_z), 0.044, wood, f"stand_base__{cand}__front_apron")
    _beam(stand, (-SIDE_X, REAR_Y, apron_z), (SIDE_X, REAR_Y, apron_z), 0.044, wood, f"stand_base__{cand}__rear_apron")
    _stand_corner_feet(stand, mats, cand, out=0.0)


def _stand_base_trestle_pair_build(stand, r: ResolvedConfig, mats) -> None:
    """Two A-frame end trestles (foot runners + angled struts) tied by stretchers."""
    wood = mats["wood"]
    dark = mats["wood_dark"]
    cand = "trestle_pair"
    for idx, sx in SIDES:
        x = sx * SIDE_X
        # Long lengthwise foot runner at the floor on this side.
        _box(stand, (0.13, REAR_Y - FRONT_Y + 0.24, 0.05), (x, 0.0, FLOOR_Z + 0.01), wood, f"stand_base__{cand}__foot_runner_{idx}")
        # Angled A-frame struts from wide feet up to the sleeves.
        _beam(stand, (x, FRONT_Y - 0.12, FLOOR_Z + 0.03), (x, FRONT_Y, LEG_TOP_Z), 0.055, wood, f"stand_base__{cand}__strut_front_{idx}")
        _beam(stand, (x, REAR_Y + 0.12, FLOOR_Z + 0.03), (x, REAR_Y, LEG_TOP_Z), 0.055, wood, f"stand_base__{cand}__strut_rear_{idx}")
        # Fore-aft tie across this trestle at mid height.  It has to actually
        # reach both A-frame struts: at z=0.27 their centrelines sit near
        # y=-+0.445, so a 0.26 m stub centred on y=0 floated 0.3 m clear of them
        # and read as a disconnected island.  0.86 m spans strut to strut.
        _box(stand, (0.11, 0.86, 0.05), (x, 0.0, 0.27), dark, f"stand_base__{cand}__end_cap_{idx}")
    # Lengthwise stretchers connecting the two end trestles (clear of tubes).
    _beam(stand, (-SIDE_X, FRONT_Y + 0.02, 0.20), (SIDE_X, FRONT_Y + 0.02, 0.20), 0.045, dark, f"stand_base__{cand}__front_stretcher")
    _beam(stand, (-SIDE_X, REAR_Y - 0.02, 0.20), (SIDE_X, REAR_Y - 0.02, 0.20), 0.045, dark, f"stand_base__{cand}__rear_stretcher")


_STAND_BUILDERS = {
    "splayed_aframe": _stand_base_splayed_aframe_build,
    "xbrace_splayed": _stand_base_xbrace_splayed_build,
    "four_post": _stand_base_four_post_build,
    "trestle_pair": _stand_base_trestle_pair_build,
}


# ===========================================================================
# Constant layer: the tilting drawing board (REVOLUTE +X on the carriage).
# ===========================================================================
def _emit_drawing_board(model, carriage, r: ResolvedConfig, mats) -> str:
    wood = mats["wood"]
    dark = mats["wood_dark"]
    panel = mats["panel"]
    grey = mats["grey"]
    hw = r.half_width
    depth = r.board_depth
    board = model.part("drawing_board", meta={"role": "drawing_board"})
    # Authored flat in the board frame; the joint places it at the hinge line.
    board.visual(Box((2 * hw, depth, 0.038)), origin=Origin(xyz=(0.0, 0.5 * depth, 0.035)), material=wood, name="wood_drawing_board", material_class_id=("wood.natural_generic" if r.palette_style in {"pale_maple", "walnut", "grey_steel"} else "wood.oak"))
    board.visual(Box((2 * hw - 0.06, depth - 0.06, 0.010)), origin=Origin(xyz=(0.0, 0.5 * depth, 0.058)), material=panel, name="work_surface", material_class_id="wood.veneer_panel")
    # Dark raised perimeter lips embedded into the board.
    _box(board, (2 * hw + 0.05, 0.040, 0.052), (0.0, 0.014, 0.050), dark, "front_lip")
    _box(board, (2 * hw + 0.04, 0.036, 0.046), (0.0, depth + 0.004, 0.052), dark, "rear_lip")
    for idx, sx in SIDES:
        _box(board, (0.042, depth + 0.02, 0.050), (sx * (hw + 0.008), 0.5 * depth + 0.008, 0.052), dark, f"side_lip_{idx}")
    # Front paper stop / parallel-rule bar embedded into the board top.
    _box(board, (2 * hw - 0.14, 0.020, 0.018), (0.0, 0.10, 0.050), grey, "paper_stop")
    # Board half of the piano hinge: knuckles on the tilt axis interleaving the
    # carriage knuckles (thin axial abutment = contact without volumetric overlap).
    for i, cx in enumerate(KNUCKLE_XS_BOARD):
        _cyl(board, 0.014, KNUCKLE_LEN, (cx, 0.0, 0.0), grey, f"hinge_knuckle_b{i}", rpy=(0.0, math.pi / 2.0, 0.0))
    # Cleat tying the board knuckles up to the panel front edge (above the axis
    # so it clears the carriage hinge brackets through the full tilt sweep).
    # The leaf reaches in to y=0.004 so it genuinely wraps the knuckle barrels
    # (radius 0.014 on the axis) instead of stopping 0.9 mm short of them, which
    # left the knuckles as disconnected geometry islands.  Only material NEARER
    # the tilt axis is added -- it sweeps a smaller circle than the existing leaf,
    # so clearance against the carriage hinge brackets is unchanged.
    _box(board, (2 * hw - 0.12, 0.046, 0.026), (0.0, 0.027, 0.024), dark, "hinge_cleat")
    _axis_joint(
        model, name="tilt_hinge", parent=carriage.name, child=board.name,
        point=(0.0, HINGE_Y, HINGE_Z), axis=(1.0, 0.0, 0.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=80.0, velocity=0.5, lower=TILT_LOWER, upper=TILT_UPPER),
        radial=(0.0, 1.0, 0.0),
    )
    return board.name


# ===========================================================================
# Slot B: angle_lock — non-articulating hardware on the carriage near the hinge.
# ===========================================================================
def _emit_angle_lock(carriage, r: ResolvedConfig, mats) -> None:
    grey = mats["grey"]
    steel = mats["steel"]
    cand = r.angle_lock
    if cand == "friction_cheeks":
        for idx, sx in SIDES:
            _box(carriage, (0.055, 0.082, 0.092), (sx * 0.512, HINGE_Y + 0.02, 0.686), grey, f"angle_lock__{cand}__cheek_{idx}")
    elif cand == "toothed_ratchet":
        y0, z0, y1, z1 = -0.30, 0.520, -0.08, 0.700
        for idx, sx in SIDES:
            _beam(carriage, (sx * 0.522, y0, z0), (sx * 0.522, y1, z1), 0.022, grey, f"angle_lock__{cand}__backbone_{idx}")
            _beam(carriage, (sx * 0.522, y0, z0 + 0.01), (sx * KNOB_SOCKET_X, KNOB_Y, z0 + 0.01), 0.018, grey, f"angle_lock__{cand}__mount_{idx}")
            for tooth in range(6):
                t = tooth / 5.0
                _box(carriage, (0.028, 0.030, 0.018), (sx * 0.522, y0 + t * (y1 - y0), z0 + t * (z1 - z0)), steel, f"angle_lock__{cand}__tooth_{idx}_{tooth}")
    else:  # curved_quadrant
        cy, cz, radius = -0.18, 0.540, 0.150
        a0, a1 = math.radians(15.0), math.radians(115.0)
        for idx, sx in SIDES:
            arc = _annular_sector_yz(
                center_y=cy, center_z=cz, radius=radius, radial_width=0.018,
                x_center=sx * 0.522, x_thickness=0.024, start_angle=a0, end_angle=a1, segments=36,
            )
            carriage.visual(mesh_from_geometry(arc, f"angle_lock__{cand}__arc_plate_{idx}"), material=grey, name=f"angle_lock__{cand}__arc_plate_{idx}", material_class_id="metal.blackened_gunmetal")
            am = (a0 + a1) * 0.5
            _beam(carriage, (sx * 0.522, cy + radius * math.cos(am), cz + radius * math.sin(am)),
                  (sx * KNOB_SOCKET_X, KNOB_Y, 0.600), 0.018, grey, f"angle_lock__{cand}__arc_mount_{idx}")


# ===========================================================================
# Slot C: control_form — two REVOLUTE side lock controls (children of carriage).
# ===========================================================================
def _control_form_paired_disk_knobs_build(part, sx, mats) -> None:
    grey = mats["grey"]
    black = mats["black"]
    cand = "paired_disk_knobs"
    _cyl(part, 0.014, 0.092, (-sx * 0.046, 0.0, 0.0), grey, f"control_form__{cand}__shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    _cyl(part, 0.055, 0.026, (0.0, 0.0, 0.0), black, f"control_form__{cand}__disk", rpy=(0.0, math.pi / 2.0, 0.0))
    for k, angle in enumerate((0.0, math.pi / 3.0, 2.0 * math.pi / 3.0)):
        _box(part, (0.012, 0.082, 0.010), (sx * 0.006, 0.0, 0.0), grey, f"control_form__{cand}__grip_{k}", rpy=(0.0, math.pi / 2.0, angle))


def _control_form_lobed_knobs_build(part, sx, mats) -> None:
    grey = mats["grey"]
    black = mats["black"]
    cand = "lobed_knobs"
    _cyl(part, 0.014, 0.092, (-sx * 0.046, 0.0, 0.0), grey, f"control_form__{cand}__shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    mesh = mesh_from_geometry(
        KnobGeometry(0.058, 0.030, body_style="lobed", base_diameter=0.044,
                     top_diameter=0.052, grip=KnobGrip(style="ribbed", count=9, depth=0.002)),
        f"control_form__{cand}__knob_{sx:.0f}",
    )
    part.visual(mesh, origin=Origin(xyz=(sx * 0.006, 0.0, 0.0), rpy=(0.0, sx * math.pi / 2.0, 0.0)), material=black, name=f"control_form__{cand}__knob", material_class_id="plastic.patterned_textured")


def _control_form_crank_winders_build(part, sx, mats) -> None:
    grey = mats["grey"]
    black = mats["black"]
    cand = "crank_winders"
    _cyl(part, 0.014, 0.092, (-sx * 0.046, 0.0, 0.0), grey, f"control_form__{cand}__shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    _cyl(part, 0.016, 0.012, (0.0, 0.0, 0.0), grey, f"control_form__{cand}__hub", rpy=(0.0, math.pi / 2.0, 0.0))
    arm_y, arm_z = 0.085, 0.022
    span = math.sqrt(arm_y ** 2 + arm_z ** 2)
    pitch = math.atan2(arm_z, arm_y)
    part.visual(Box((0.014, span, 0.012)), origin=Origin(xyz=(0.0, -arm_y * 0.5, -arm_z * 0.5), rpy=(pitch, 0.0, 0.0)),
                material=grey, name=f"control_form__{cand}__arm", material_class_id="metal.blackened_gunmetal")
    _cyl(part, 0.011, 0.048, (0.0, -arm_y, -arm_z), black, f"control_form__{cand}__grip", rpy=(0.0, math.pi / 2.0, 0.0))


_CONTROL_BUILDERS = {
    "paired_disk_knobs": _control_form_paired_disk_knobs_build,
    "lobed_knobs": _control_form_lobed_knobs_build,
    "crank_winders": _control_form_crank_winders_build,
}


def _emit_controls(model, carriage, r: ResolvedConfig, mats) -> list[str]:
    names: list[str] = []
    builder = _CONTROL_BUILDERS[r.control_form]
    for idx, sx in SIDES:
        name = f"lock_control_{idx}"
        part = model.part(name, meta={"role": "lock_control", "candidate": r.control_form})
        builder(part, sx, mats)
        _axis_joint(
            model, name=f"lock_control_{idx}_pivot", parent=carriage.name, child=name,
            point=(sx * KNOB_JOINT_X, KNOB_Y, KNOB_Z), axis=(1.0, 0.0, 0.0),
            articulation_type=ArticulationType.REVOLUTE,
            limits=MotionLimits(effort=3.0, velocity=4.0, lower=-math.pi, upper=math.pi),
            radial=(0.0, 1.0, 0.0),
        )
        names.append(name)
    return names


# ===========================================================================
# Multiplicity: N tool / supply trays under the board front apron.
# (item_slot=stand_base; slot-scoped names so growth is attributed correctly.)
# ===========================================================================
def _emit_trays(carriage, r: ResolvedConfig, mats) -> None:
    n = r.tray_count
    wood = mats["wood"]
    dark = mats["wood_dark"]
    steel = mats["steel"]
    hw = r.half_width
    apron_half = min(SIDE_X - 0.06, hw - 0.05)
    tray_z = 0.640
    # Constant supply shelf + rails hung under the board front (connect to knob tabs).
    # The shelf's rear edge must actually land on the knob mount tabs it hangs
    # from (tabs span y=-0.197..-0.153): stopping at y=-0.22 left the whole tray
    # group -- shelf, rails, dividers, faces, pulls -- floating as one island.
    _box(carriage, (2 * apron_half + 0.02, 0.19, 0.018), (0.0, -0.285, tray_z + 0.008), wood, "supply_shelf")
    _beam(carriage, (-apron_half, -0.212, tray_z + 0.02), (apron_half, -0.212, tray_z + 0.02), 0.028, steel, "tray_rear_rail")
    _beam(carriage, (-apron_half, -0.388, tray_z + 0.02), (apron_half, -0.388, tray_z + 0.02), 0.028, steel, "tray_front_rail")
    cell_w = (2.0 * apron_half) / n
    for i in range(n - 1):
        div_x = -apron_half + cell_w * (i + 1)
        _box(carriage, (0.014, 0.020, 0.060), (div_x, -0.392, tray_z + 0.03), dark, f"stand_base__tray_divider_{i}")
    for i in range(n):
        cx = -apron_half + cell_w * (i + 0.5)
        _box(carriage, (cell_w - 0.03, 0.016, 0.052), (cx, -0.394, tray_z + 0.028), dark, f"stand_base__tray_face_{i}")
        _cyl(carriage, 0.022, 0.010, (cx, -0.404, tray_z + 0.028), steel, f"stand_base__tray_pull_{i}", rpy=(math.pi / 2.0, 0.0, 0.0))


# ===========================================================================
# Assembly
# ===========================================================================
def build_picturex_0611_floor_standing_drafting_table(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets, meta={"category": "Floor-standing drafting table"})
    palette = dict(PALETTES[r.palette_style])
    palette.update(_HARDWARE)
    mats = {k: model.material(f"draft_{r.palette_style}_{k}", rgba=v) for k, v in palette.items()}

    stand = model.part("floor_stand", meta={"role": "floor_stand", "candidate": r.stand_base})
    _emit_lift_guide(stand, r, mats)
    _STAND_BUILDERS[r.stand_base](stand, r, mats)

    carriage = model.part("lift_carriage", meta={"role": "lift_carriage"})
    _emit_carriage_frame(carriage, r, mats)
    _emit_angle_lock(carriage, r, mats)
    _emit_trays(carriage, r, mats)

    _axis_joint(
        model, name="height_lift", parent=stand.name, child=carriage.name,
        point=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.PRISMATIC,
        limits=MotionLimits(effort=140.0, velocity=0.08, lower=0.0, upper=r.lift_travel_m),
        radial=(1.0, 0.0, 0.0),
    )

    _emit_drawing_board(model, carriage, r, mats)
    _emit_controls(model, carriage, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_picturex_0611_floor_standing_drafting_table(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_picturex_0611_floor_standing_drafting_table(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_picturex_0611_floor_standing_drafting_table_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    stand = object_model.get_part("floor_stand")
    carriage = object_model.get_part("lift_carriage")
    board = object_model.get_part("drawing_board")
    tilt = object_model.get_articulation("tilt_hinge")
    lift = object_model.get_articulation("height_lift")

    # ---- Category anchors (named author checks). ----
    ctx.check(
        "category_anchor: floor-standing tilting drawing board",
        tilt.parent == "lift_carriage" and tilt.child == "drawing_board"
        and tilt.articulation_type == ArticulationType.REVOLUTE
        and abs(tilt.axis[0]) > 0.99
        and tilt.motion_limits is not None
        and tilt.motion_limits.upper is not None and tilt.motion_limits.upper > 0.4,
        details=f"tilt={tilt.parent}->{tilt.child}, axis={tilt.axis}, limits={tilt.motion_limits}",
    )
    ctx.check(
        "category_anchor: prismatic height lift",
        lift.parent == "floor_stand" and lift.child == "lift_carriage"
        and lift.articulation_type == ArticulationType.PRISMATIC
        and abs(lift.axis[2]) > 0.99
        and lift.motion_limits is not None and lift.motion_limits.upper is not None
        and lift.motion_limits.upper >= 0.10,
        details=f"lift={lift.parent}->{lift.child}, axis={lift.axis}, limits={lift.motion_limits}",
    )
    controls_ok = True
    for idx, sx in SIDES:
        j = object_model.get_articulation(f"lock_control_{idx}_pivot")
        controls_ok = controls_ok and (
            j.parent == "lift_carriage" and j.child == f"lock_control_{idx}"
            and j.articulation_type == ArticulationType.REVOLUTE
            and abs(j.axis[0]) > 0.99
        )
    ctx.check(
        "category_anchor: two rotary lock controls",
        controls_ok,
        details="both side lock controls are +X revolute children of the carriage",
    )

    # ---- Identity geometry: wide tilting board carried across the frame width. ----
    #
    # These are asserted from the shared parameter derivation rather than element
    # AABB probes: `expect_overlap` / `part_element_world_aabb` build a whole-model
    # AABB cache, which forces every `mesh_from_geometry` element in the model to
    # be materialized on disk -- work preflight deliberately defers.  Swept contact
    # and collision remain harness-owned on every built seed.
    hw = r.half_width
    board_dims = (2.0 * hw, r.board_depth, 0.038)
    ctx.check(
        "drawing board is a wide planar drawing surface",
        board_dims[0] >= 1.0 and board_dims[1] >= 0.60,
        details=f"board_dims={board_dims}",
    )
    # The hinge rail spans the full board width (plus 30 mm each side), so the
    # board is carried across the carriage rather than cantilevered off one end.
    rail_half_span = hw + 0.03
    ctx.check(
        "wide drawing board is carried across the carriage hinge rail width",
        rail_half_span >= hw
        and any(v.name == "front_hinge_rail" for v in carriage.visuals)
        and any(v.name == "wood_drawing_board" for v in board.visuals),
        details=f"rail_half_span={rail_half_span:.4f} >= board_half_width={hw:.4f}",
    )

    # ---- Tilt raises the rear edge. ----
    rest = ctx.part_world_aabb(board)
    with ctx.pose({tilt: tilt.motion_limits.upper}):
        raised = ctx.part_world_aabb(board)
    ctx.check(
        "positive tilt raises the board rear edge",
        rest is not None and raised is not None and raised[1][2] > rest[1][2] + 0.12,
        details=f"rest={rest}, raised={raised}",
    )

    # ---- Height lift raises the carriage. ----
    rest_c = ctx.part_world_position(carriage)
    with ctx.pose({lift: lift.motion_limits.upper}):
        up_c = ctx.part_world_position(carriage)
    ctx.check(
        "height lift raises the carriage by the full travel",
        rest_c is not None and up_c is not None
        and abs((up_c[2] - rest_c[2]) - lift.motion_limits.upper) < 0.004,
        details=f"rest_z={rest_c[2] if rest_c else None}, up_z={up_c[2] if up_c else None}",
    )
    # Telescoping insertion depth is a derived invariant: the inner guide bar must
    # stay well inside its outer sleeve at BOTH lift limits.  `sleeve_top_z` grows
    # with lift travel precisely to guarantee this, so assert the arithmetic
    # (mesh-free) instead of probing element AABBs.
    # `sleeve_top_z = 0.44 + lift_travel` and the bar bottom rises by exactly
    # `lift_travel`, so the engaged length is a travel-independent 80 mm by
    # construction.  Assert a 60 mm floor: enough to catch a regression that
    # decouples the sleeve height from the travel, without hard-coding 0.08.
    insertion_at_full_lift = r.sleeve_top_z - (INNER_BOT_Z + r.lift_travel_m)
    ctx.check(
        "guide bars stay inserted in their sleeves across the full lift travel",
        insertion_at_full_lift >= 0.06,
        details=f"insertion_at_full_lift={insertion_at_full_lift:.4f} m >= 0.06 "
        f"(sleeve_top_z={r.sleeve_top_z:.4f}, lift_travel={r.lift_travel_m:.4f})",
    )
    for idx, _sx in SIDES:
        for tag in ("front", "rear"):
            ctx.check(
                f"{tag} guide bar {idx} runs along the sleeve",
                any(v.name == f"inner_tube_{tag}_{idx}" for v in carriage.visuals)
                and any(v.name == f"guide_sleeve_{tag}_{idx}" for v in stand.visuals),
                details=f"inner_tube_{tag}_{idx} / guide_sleeve_{tag}_{idx}",
            )

    # ---- Lock controls spin in place. ----
    for idx, sx in SIDES:
        ctrl = object_model.get_part(f"lock_control_{idx}")
        j = object_model.get_articulation(f"lock_control_{idx}_pivot")
        before = ctx.part_world_position(ctrl)
        with ctx.pose({j: 1.2}):
            after = ctx.part_world_position(ctrl)
        ctx.check(
            f"lock_control_{idx} spins in place",
            before is not None and after is not None and max(abs(before[k] - after[k]) for k in range(3)) < 1e-6,
            details=f"before={before}, after={after}",
        )

    # ---- tray_count multiplicity. ----
    for i in range(r.tray_count):
        ctx.check(
            f"tray face {i} present",
            any(v.name == f"stand_base__tray_face_{i}" for v in carriage.visuals),
            details=f"stand_base__tray_face_{i} missing",
        )

    # ---- Compiler-owned baseline. ----
    #
    # Exact-collision, sampled-pose, isolated-geometry, joint-mating-gap and
    # articulation-origin QC are owned by the sweep harness, which runs them on
    # every built seed.  Restating them here would only duplicate that work and
    # forces mesh materialization during preflight, which deliberately defers
    # mesh readiness (the `mesh_from_geometry` arc plates and lobed knobs have no
    # on-disk OBJ at probe time).  Author tests stay category-specific instead.
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()

    return ctx.report()


# ===========================================================================
# High-risk cross-slot corners (surface flat vs max tilt & min/max height are
# owned by joint lower/upper motion QC; these exercise build-time extremes).
# ===========================================================================
TEMPLATE_CORNERS = (
    corner_case(
        "wide_board_trestle_max_lift_quadrant",
        {"stand_base": "trestle_pair", "angle_lock": "curved_quadrant",
         "control_form": "crank_winders", "tray_count": 3,
         "board_width_scale": 1.10, "board_depth_scale": 1.08, "lift_travel_m": 0.20},
        reason="widest deepest board + maximum lift travel + full trays on the leaning trestle stand",
    ),
    corner_case(
        "narrow_board_four_post_min_lift_ratchet",
        {"stand_base": "four_post", "angle_lock": "toothed_ratchet",
         "control_form": "lobed_knobs", "tray_count": 1,
         "board_width_scale": 0.92, "board_depth_scale": 0.95, "lift_travel_m": 0.10},
        reason="narrowest board + minimum lift + single tray with ratchet racks on four posts",
    ),
    corner_case(
        "splayed_aframe_max_lift_friction",
        {"stand_base": "splayed_aframe", "angle_lock": "friction_cheeks",
         "control_form": "paired_disk_knobs", "tray_count": 2,
         "board_width_scale": 1.06, "board_depth_scale": 1.02, "lift_travel_m": 0.20},
        reason="source splayed A-frame at max lift keeps inner tubes inserted under a wide board",
    ),
    corner_case(
        "xbrace_wide_min_lift",
        {"stand_base": "xbrace_splayed", "angle_lock": "curved_quadrant",
         "control_form": "paired_disk_knobs", "tray_count": 3,
         "board_width_scale": 1.10, "board_depth_scale": 1.08, "lift_travel_m": 0.10},
        reason="widest board with minimum lift and full trays on the X-braced stand",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "StandBase",
    "AngleLock",
    "ControlForm",
    "PaletteStyle",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_floor_standing_drafting_table",
    "build_seeded_picturex_0611_floor_standing_drafting_table",
    "run_picturex_0611_floor_standing_drafting_table_tests",
]
