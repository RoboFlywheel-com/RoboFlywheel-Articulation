# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained Urban Environment / Tilt Truck1 template (TEMPLATE_DOMAIN).

Rebuilt from fourteen source assets (four reference-image origin anchors plus ten
accepted single-axis fork variants); see
``articraft_data/picture_expansion/template_source_maps/Urban_Environment__Tilt_Truck1.md``.

Subcategory identity: a **rigid-body wheeled tilt truck / hopper cart**.  One
rotationally-moulded open-top hopper with a broad continuous top flange and an
asymmetric silhouette (tall near-vertical rear wall, long forward-and-down
discharge nose), moulded side stiffening ribs, a push handle at the tall rear
end, a hidden steel underframe, two large road wheels on one lateral axle line
and one small front wheel/caster.

The cargo shell is **RIGIDLY fixed** to the rolling chassis (``body_mount``,
FIXED).  There is deliberately no hopper-tilt/dump joint anywhere: a tipping
body belongs to the sibling subcategory Tilt Truck2 and stays excluded.

Every revolute/continuous joint is built from ``mate_axes`` and registered with
``register_interface_mate``.  No source runtime, snapshot or other template is
imported; geometry uses only the SDK plus the Python standard library.
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
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    MotionProperties,
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
ShellForm = Literal["tapered_rect", "chamfered_octagon", "obround", "v_nose"]
Underframe = Literal["rail_cradle", "fork_pockets", "tube_perimeter"]
FrontSupport = Literal["rigid_fork", "swivel_caster", "swivel_caster_brake"]
HandleStyle = Literal["twin_grab_bars", "u_frame_fixed", "folding_u_frame", "molded_grips"]
LidStyle = Literal["open_top", "hinged_lid"]
RearWheelStyle = Literal["spoked_rim", "disc_rim"]
RibStyle = Literal["draft_panel", "raised_rail"]
PaletteStyle = Literal["rotomould_grey", "hazard_orange", "utility_blue", "graphite"]

SHELL_FORMS: tuple[ShellForm, ...] = ("tapered_rect", "chamfered_octagon", "obround", "v_nose")
UNDERFRAMES: tuple[Underframe, ...] = ("rail_cradle", "fork_pockets", "tube_perimeter")
FRONT_SUPPORTS: tuple[FrontSupport, ...] = (
    "rigid_fork",
    "swivel_caster",
    "swivel_caster_brake",
)
HANDLE_STYLES: tuple[HandleStyle, ...] = (
    "twin_grab_bars",
    "u_frame_fixed",
    "folding_u_frame",
    "molded_grips",
)
LID_STYLES: tuple[LidStyle, ...] = ("open_top", "hinged_lid")
REAR_WHEEL_STYLES: tuple[RearWheelStyle, ...] = ("spoked_rim", "disc_rim")
RIB_STYLES: tuple[RibStyle, ...] = ("draft_panel", "raised_rail")
RIB_COUNTS: tuple[int, ...] = (2, 3, 4, 5)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "rotomould_grey",
    "hazard_orange",
    "utility_blue",
    "graphite",
)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("shell_form", SHELL_FORMS, role="moulded hopper plan family"),
        component_slot("underframe", UNDERFRAMES, role="hidden steel underframe skeleton"),
        component_slot("front_support", FRONT_SUPPORTS, role="front wheel support mechanism"),
        component_slot("handle", HANDLE_STYLES, role="operator push/grab handle"),
        component_slot("lid", LID_STYLES, role="hopper top closure"),
        component_slot("rear_wheel", REAR_WHEEL_STYLES, role="road wheel construction"),
        component_slot("rib", RIB_STYLES, role="moulded side stiffening rib profile"),
        multiplicity_slot(
            "rib_count",
            RIB_COUNTS,
            role="moulded stiffening ribs per side wall",
            item_slot="rib",
        ),
    )
)

# ---------------------------------------------------------------------------
# Palettes (not counted in core/raw diversity)
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "rotomould_grey": {
        "shell": (0.545, 0.552, 0.560, 1.0),
        "shell_dark": (0.430, 0.438, 0.446, 1.0),
    },
    "hazard_orange": {
        "shell": (0.940, 0.352, 0.105, 1.0),
        "shell_dark": (0.760, 0.270, 0.075, 1.0),
    },
    "utility_blue": {
        "shell": (0.050, 0.258, 0.585, 1.0),
        "shell_dark": (0.035, 0.190, 0.440, 1.0),
    },
    "graphite": {
        "shell": (0.250, 0.272, 0.288, 1.0),
        "shell_dark": (0.170, 0.186, 0.200, 1.0),
    },
}
_HARDWARE: dict[str, tuple[float, float, float, float]] = {
    "frame": (0.058, 0.063, 0.068, 1.0),
    "zinc": (0.640, 0.665, 0.685, 1.0),
    "rubber": (0.048, 0.050, 0.052, 1.0),
    "wheel": (0.400, 0.420, 0.440, 1.0),
    "accent": (0.900, 0.720, 0.070, 1.0),
}

# ---------------------------------------------------------------------------
# Shared construction constants (metres; +X = discharge nose, -X = tall rear
# wall, +Z up, Y lateral, Z = 0 is the ground plane).
# ---------------------------------------------------------------------------
WALL_T = 0.026          # moulded shell wall thickness
FLOOR_T = 0.044         # moulded shell floor thickness
FLANGE_OUT = 0.036      # top flange outset beyond the wall
FLANGE_T = 0.026        # top flange slab thickness
REAR_LEAN = 0.035       # rear wall lean across the full wall height
DECK_RISE = 0.058       # chassis deck top above the rear axle line
SHELL_BITE = 0.0005     # deliberate seating interference (< the 1 mm overlap tol)
SWIVEL_DROP = 0.050     # caster swivel plane below the deck top
DECK_T = 0.036          # deck rail section height
RIB_EMBED = 0.006       # rib embed into the moulded wall
SIDES: tuple[tuple[str, float], ...] = (("0", -1.0), ("1", 1.0))

# Hinged-lid moulding (var_hinged_lid_v2 model.py:L42-L59, L80-L181).  The lid
# plan is the shell's own rim outline, so every dimension below is a *metric*
# offset from that outline rather than an independent plan shape.
LID_RIM_CLEAR = 0.008     # running clearance between the skirt lip and the rim edge
LID_SKIRT_T = 0.010       # downturned perimeter skirt-lip wall thickness
LID_SKIRT_DROP = 0.040    # skirt-lip depth below the panel underside
LID_SKIRT_BITE = 0.006    # skirt-lip fusion into the panel underside
LID_OVERHANG = LID_RIM_CLEAR + LID_SKIRT_T + 0.006  # panel edge past the rim edge
LID_PANEL_T = 0.022       # moulded lid panel thickness
LID_PANEL_SETBACK = 0.026  # panel rear edge forward of the hinge axis
LID_SKIRT_SETBACK = 0.030  # skirt lip stops this far forward of the panel rear edge


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


# ---------------------------------------------------------------------------
# Plan outlines: one machinery, four moulded plan families
# ---------------------------------------------------------------------------
def _outline_tapered_rect(x_lo, x_hi, y_half, corner):
    """002 model.py:L112-L182 — rounded-rectangle station with a drafted wall."""
    length = x_hi - x_lo
    c = max(0.006, min(corner, 0.42 * length, 0.42 * y_half))
    centres = (
        (x_hi - c, -y_half + c, -math.pi / 2.0),
        (x_hi - c, y_half - c, 0.0),
        (x_lo + c, y_half - c, math.pi / 2.0),
        (x_lo + c, -y_half + c, math.pi),
    )
    points: list[tuple[float, float]] = []
    for cx, cy, a0 in centres:
        for index in range(6):
            angle = a0 + (math.pi / 2.0) * index / 6.0
            points.append((cx + c * math.cos(angle), cy + c * math.sin(angle)))
    return points


def _outline_chamfered_octagon(x_lo, x_hi, y_half, corner):
    """var_form_chamfered_octagonal model.py:L71-L91 — constant 45-degree facets."""
    length = x_hi - x_lo
    ch = max(0.010, min(0.28 * length, 0.40 * y_half, 2.0 * corner))
    verts = (
        (x_hi - ch, -y_half),
        (x_hi, -y_half + ch),
        (x_hi, y_half - ch),
        (x_hi - ch, y_half),
        (x_lo + ch, y_half),
        (x_lo, y_half - ch),
        (x_lo, -y_half + ch),
        (x_lo + ch, -y_half),
    )
    points: list[tuple[float, float]] = []
    for index in range(8):
        a = verts[index]
        b = verts[(index + 1) % 8]
        for step in range(3):
            t = step / 3.0
            points.append((_lerp(a[0], b[0], t), _lerp(a[1], b[1], t)))
    return points


def _outline_obround(x_lo, x_hi, y_half, corner):
    """var_form_obround model.py:L68-L95 — stadium plan: straight sides, round ends."""
    del corner
    length = x_hi - x_lo
    rad = min(y_half, 0.48 * length)
    straight = 0.5 * length - rad
    mid = 0.5 * (x_lo + x_hi)
    points: list[tuple[float, float]] = [(mid - straight, -y_half), (mid + straight, -y_half)]
    for index in range(1, 12):
        angle = -math.pi / 2.0 + math.pi * index / 12.0
        points.append((mid + straight + rad * math.cos(angle), y_half * math.sin(angle)))
    points.append((mid + straight, y_half))
    points.append((mid - straight, y_half))
    for index in range(1, 12):
        angle = math.pi / 2.0 + math.pi * index / 12.0
        points.append((mid - straight + rad * math.cos(angle), y_half * math.sin(angle)))
    return points


def _outline_v_nose(x_lo, x_hi, y_half, corner):
    """var_form_vnose model.py:L58-L86 — plan tapering to a rounded V discharge spout."""
    length = x_hi - x_lo
    c = max(0.008, min(corner, 0.40 * y_half, 0.24 * length))
    nose_r = max(0.012, min(0.16 * y_half, 0.16 * length))
    nose_y = nose_r * 0.55
    apex = (
        (x_hi - nose_r, -nose_y),
        (x_hi, -nose_y * 0.35),
        (x_hi, nose_y * 0.35),
        (x_hi - nose_r, nose_y),
    )
    top = (x_lo + c, y_half)
    bottom = (x_lo + c, -y_half)
    points: list[tuple[float, float]] = list(apex)
    for step in range(1, 6):
        t = step / 6.0
        points.append((_lerp(apex[3][0], top[0], t), _lerp(apex[3][1], top[1], t)))
    points.append(top)
    for step in range(1, 6):
        angle = math.pi / 2.0 + (math.pi / 2.0) * step / 5.0
        points.append((x_lo + c + c * math.cos(angle), y_half - c + c * math.sin(angle)))
    for step in range(1, 6):
        angle = math.pi + (math.pi / 2.0) * step / 5.0
        points.append((x_lo + c + c * math.cos(angle), -y_half + c + c * math.sin(angle)))
    for step in range(1, 6):
        t = step / 6.0
        points.append((_lerp(bottom[0], apex[0][0], t), _lerp(bottom[1], apex[0][1], t)))
    return points


_OUTLINES = {
    "tapered_rect": _outline_tapered_rect,
    "chamfered_octagon": _outline_chamfered_octagon,
    "obround": _outline_obround,
    "v_nose": _outline_v_nose,
}


def _plan_outline(form: str, x_lo: float, x_hi: float, y_half: float, corner: float):
    return _OUTLINES[form](x_lo, x_hi, max(0.030, y_half), corner)


def _outline_y_at(points, x_target: float, side: float) -> float | None:
    """Interpolate the plan half-width on one side at a given X station."""
    best: float | None = None
    count = len(points)
    for index in range(count):
        p = points[index]
        q = points[(index + 1) % count]
        if (p[0] - x_target) * (q[0] - x_target) > 0.0:
            continue
        if abs(q[0] - p[0]) < 1e-12:
            y = max(p[1], q[1]) if side > 0 else min(p[1], q[1])
        else:
            t = (x_target - p[0]) / (q[0] - p[0])
            y = p[1] + (q[1] - p[1]) * t
        value = side * y
        if value > 0.0 and (best is None or value > best):
            best = value
    return None if best is None else side * best


def _outline_x_at(points, y_target: float, side: float) -> float | None:
    """Rear-most plan X where the outline reaches a given lateral station.

    Non-rectangular plan families (stadium ends, chamfers, the V nose) pull the
    rear flange forward as |y| grows, so handle posts, hinge barrels and moulded
    grab handles must be seated from the real outline rather than from a
    rectangle corner (var_form_obround model.py:L98-L112 reuses its own plan for
    exactly this reason).
    """
    target = side * abs(y_target)
    best = None
    count = len(points)
    for index in range(count):
        p0 = points[index]
        p1 = points[(index + 1) % count]
        if (p0[1] - target) * (p1[1] - target) > 0.0:
            continue
        if abs(p1[1] - p0[1]) < 1e-12:
            x = min(p0[0], p1[0])
        else:
            t = (target - p0[1]) / (p1[1] - p0[1])
            x = p0[0] + (p1[0] - p0[0]) * t
        if best is None or x < best:
            best = x
    return best


def _offset_outline(points, distance: float):
    """Normal-offset a closed plan polygon by a true metric distance.

    var_form_vnose model.py:L93-L124 (`_offset_outline_points`) builds the shell
    wall this way: shift every edge along its own outward normal, re-intersect
    the neighbouring shifted edges to get the mitred vertex, and fall back to the
    plain shifted vertex when the mitre runs away at a tightly curved lip.  The
    lid reuses the same machinery so its panel edge and skirt lip keep a
    *constant* metric clearance to the rim on every plan family, instead of the
    station-parameter offset (which is only metric for the rounded-rect plan and
    collapses to a fraction of its nominal value on the V-nose flanks).

    Positive ``distance`` moves outward.
    """
    count = len(points)
    area2 = sum(
        points[index][0] * points[(index + 1) % count][1]
        - points[(index + 1) % count][0] * points[index][1]
        for index in range(count)
    )
    orientation = 1.0 if area2 > 0.0 else -1.0
    shifted: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for index in range(count):
        point = points[index]
        nxt = points[(index + 1) % count]
        dx, dy = nxt[0] - point[0], nxt[1] - point[1]
        length = math.hypot(dx, dy)
        if length < 1e-12:
            shifted.append((point, (dx, dy)))
            continue
        nx, ny = orientation * (dy / length), orientation * (-dx / length)
        shifted.append(((point[0] + distance * nx, point[1] + distance * ny), (dx, dy)))

    result: list[tuple[float, float]] = []
    for index in range(count):
        p1, d1 = shifted[index - 1]
        p2, d2 = shifted[index]
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        if abs(cross) < 1e-9:
            result.append(p2)
            continue
        rx, ry = p2[0] - p1[0], p2[1] - p1[1]
        t = (rx * d2[1] - ry * d2[0]) / cross
        candidate = (p1[0] + t * d1[0], p1[1] + t * d1[1])
        miter = math.hypot(candidate[0] - points[index][0], candidate[1] - points[index][1])
        if miter > 3.0 * abs(distance):
            candidate = p2
        result.append(candidate)
    return result


def _clip_outline_front(points, x_cut: float):
    """Sutherland-Hodgman trim of a closed plan polygon to ``x >= x_cut``.

    The hinged lid only covers the rim forward of its hinge line, so the moulded
    plan is trimmed there rather than replaced by a rectangle.
    """
    result: list[tuple[float, float]] = []
    count = len(points)
    for index in range(count):
        p = points[index]
        q = points[(index + 1) % count]
        p_in = p[0] >= x_cut
        q_in = q[0] >= x_cut
        if p_in:
            result.append(p)
        if p_in != q_in and abs(q[0] - p[0]) > 1e-12:
            t = (x_cut - p[0]) / (q[0] - p[0])
            result.append((x_cut, p[1] + (q[1] - p[1]) * t))
    return result if len(result) >= 3 else list(points)


def _point_in_outline(points, target) -> bool:
    """Ray-cast containment test for a closed plan polygon."""
    inside = False
    count = len(points)
    for index in range(count):
        p = points[index]
        q = points[(index + 1) % count]
        if (p[1] > target[1]) != (q[1] > target[1]):
            x = p[0] + (target[1] - p[1]) * (q[0] - p[0]) / (q[1] - p[1])
            if x > target[0]:
                inside = not inside
    return inside


def _outline_edge_distance(points, target) -> float:
    """Shortest distance from a point to a closed plan polygon's boundary."""
    best = float("inf")
    count = len(points)
    for index in range(count):
        p = points[index]
        q = points[(index + 1) % count]
        dx, dy = q[0] - p[0], q[1] - p[1]
        span = dx * dx + dy * dy
        if span < 1e-18:
            best = min(best, math.hypot(target[0] - p[0], target[1] - p[1]))
            continue
        t = _clamp(((target[0] - p[0]) * dx + (target[1] - p[1]) * dy) / span, 0.0, 1.0)
        best = min(best, math.hypot(target[0] - (p[0] + t * dx), target[1] - (p[1] + t * dy)))
    return best


# ---------------------------------------------------------------------------
# Mesh stitching machinery (004 model.py:L30-L56)
# ---------------------------------------------------------------------------
def _stitch(geometry: MeshGeometry, loop_a: list[int], loop_b: list[int]) -> None:
    count = len(loop_a)
    for index in range(count):
        nxt = (index + 1) % count
        geometry.add_face(loop_a[index], loop_a[nxt], loop_b[nxt])
        geometry.add_face(loop_a[index], loop_b[nxt], loop_b[index])


def _cap(geometry: MeshGeometry, loop: list[int], centre, *, reverse: bool) -> None:
    centre_index = geometry.add_vertex(*centre)
    count = len(loop)
    for index in range(count):
        nxt = (index + 1) % count
        if reverse:
            geometry.add_face(centre_index, loop[nxt], loop[index])
        else:
            geometry.add_face(centre_index, loop[index], loop[nxt])


def _prism(sections, z_lo: float, z_hi: float) -> MeshGeometry:
    """Close a two-station prism from matching horizontal cross sections."""
    geometry = MeshGeometry()
    lower = [geometry.add_vertex(x, y, z_lo) for x, y in sections[0]]
    upper = [geometry.add_vertex(x, y, z_hi) for x, y in sections[1]]
    _stitch(geometry, lower, upper)
    lower_centre = (
        sum(p[0] for p in sections[0]) / len(sections[0]),
        sum(p[1] for p in sections[0]) / len(sections[0]),
        z_lo,
    )
    upper_centre = (
        sum(p[0] for p in sections[1]) / len(sections[1]),
        sum(p[1] for p in sections[1]) / len(sections[1]),
        z_hi,
    )
    _cap(geometry, lower, lower_centre, reverse=True)
    _cap(geometry, upper, upper_centre, reverse=False)
    return geometry


def _local_origin(origin: Origin | None, offset: tuple[float, float, float]) -> Origin:
    base = origin or Origin()
    return Origin(
        xyz=tuple(value - shift for value, shift in zip(base.xyz, offset)),
        rpy=base.rpy,
    )


def _local_point(
    xyz: tuple[float, float, float], offset: tuple[float, float, float]
) -> tuple[float, float, float]:
    return tuple(value - shift for value, shift in zip(xyz, offset))


_ZERO_OFFSET = (0.0, 0.0, 0.0)


def _box(
    part,
    size,
    xyz,
    material,
    name,
    rpy=(0.0, 0.0, 0.0),
    *,
    offset=_ZERO_OFFSET,
) -> None:
    part.visual(
        Box(size),
        origin=_local_origin(Origin(xyz=xyz, rpy=rpy), offset),
        material=material,
        name=name,
        material_class_id="metal.paint_coated",
    )


def _cyl(
    part,
    radius,
    length,
    xyz,
    material,
    name,
    rpy=(0.0, 0.0, 0.0),
    *,
    offset=_ZERO_OFFSET,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=_local_origin(Origin(xyz=xyz, rpy=rpy), offset),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _beam(part, p0, p1, section, material, name, *, offset=_ZERO_OFFSET) -> None:
    """One straight box member spanning p0..p1 with its local +Z along the span."""
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return
    mid = (0.5 * (p0[0] + p1[0]), 0.5 * (p0[1] + p1[1]), 0.5 * (p0[2] + p1[2]))
    pitch = math.acos(_clamp(dz / length, -1.0, 1.0))
    yaw = math.atan2(dy, dx) if (abs(dx) > 1e-12 or abs(dy) > 1e-12) else 0.0
    part.visual(
        Box((section, section, length)),
        origin=_local_origin(Origin(xyz=mid, rpy=(0.0, pitch, yaw)), offset),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    shell_form: ShellForm = "tapered_rect"
    underframe: Underframe = "rail_cradle"
    front_support: FrontSupport = "swivel_caster"
    handle: HandleStyle = "u_frame_fixed"
    lid: LidStyle = "open_top"
    rear_wheel: RearWheelStyle = "spoked_rim"
    rib: RibStyle = "draft_panel"
    rib_count: int = 3
    tub_length_m: float = 1.32
    tub_width_m: float = 0.78
    tub_height_m: float = 0.60
    wall_draft_ratio: float = 0.70
    nose_run_ratio: float = 0.42
    rear_wheel_radius_m: float = 0.155
    front_wheel_ratio: float = 0.36
    rib_relief_m: float = 0.016
    handle_rise_m: float = 0.28
    lid_open_rad: float = 1.38
    handle_fold_rad: float = 1.30
    brake_travel_rad: float = 0.32
    palette_style: PaletteStyle = "rotomould_grey"
    name: str = "urban_environment_tilt_truck1"


@dataclass(frozen=True)
class ResolvedConfig:
    shell_form: ShellForm
    underframe: Underframe
    front_support: FrontSupport
    handle: HandleStyle
    lid: LidStyle
    rear_wheel: RearWheelStyle
    rib: RibStyle
    rib_count: int
    tub_length_m: float
    tub_width_m: float
    tub_height_m: float
    wall_draft_ratio: float
    nose_run_ratio: float
    rear_wheel_radius_m: float
    front_wheel_ratio: float
    rib_relief_m: float
    handle_rise_m: float
    lid_open_rad: float
    handle_fold_rad: float
    brake_travel_rad: float
    palette_style: PaletteStyle
    name: str

    # -- plan descriptor shared by shell, ribs, frame, wheels and lid --------
    @property
    def half_len(self) -> float:
        return 0.5 * self.tub_length_m

    @property
    def half_wid(self) -> float:
        return 0.5 * self.tub_width_m

    @property
    def nose_run(self) -> float:
        return min(
            self.nose_run_ratio * self.tub_length_m,
            self.tub_length_m - 0.34 - REAR_LEAN,
        )

    @property
    def axle_z(self) -> float:
        return self.rear_wheel_radius_m

    @property
    def deck_z(self) -> float:
        return self.axle_z + DECK_RISE

    @property
    def floor_z(self) -> float:
        return self.deck_z - SHELL_BITE

    @property
    def rim_z(self) -> float:
        return self.floor_z + self.tub_height_m

    @property
    def wall_h(self) -> float:
        return self.tub_height_m - FLANGE_T

    @property
    def rim_wall_z(self) -> float:
        return self.rim_z - FLANGE_T

    @property
    def x_axle(self) -> float:
        return -0.10 * self.tub_length_m

    @property
    def x_front(self) -> float:
        return self.half_len - 0.10

    @property
    def swivel_z(self) -> float:
        return self.deck_z - SWIVEL_DROP

    @property
    def rear_wheel_width(self) -> float:
        return 0.30 * self.rear_wheel_radius_m + 0.020

    @property
    def front_wheel_radius(self) -> float:
        return self.front_wheel_ratio * self.rear_wheel_radius_m

    @property
    def front_wheel_width(self) -> float:
        return 0.30 * self.front_wheel_radius + 0.016

    @property
    def caster_trail(self) -> float:
        return max(0.022, 0.30 * self.front_wheel_radius)

    @property
    def mount_datum(self) -> tuple[float, float, float]:
        """Weld datum: mid-deck, on the crossmember top face / shell floor seat."""
        return (0.5 * (self.plan_x_lo(0.0) + self.plan_x_hi(0.0)), 0.0, self.deck_z)

    @property
    def x_rear_flange(self) -> float:
        """Outer X of the rear top flange: the handle / lid hinge datum."""
        return self.plan_x_lo(1.0) - FLANGE_OUT

    @property
    def rear_ref_y(self) -> float:
        """Widest lateral station the rear-flange hardware must be seated at."""
        return min(
            self.handle_half_y + 0.100,
            self.plan_y_half(1.0) + FLANGE_OUT - 0.030,
        )

    def rim_rear_x(self, y_abs: float) -> float:
        value = _outline_x_at(self.outline(1.0, FLANGE_OUT), y_abs, 1.0)
        return self.x_rear_flange if value is None else value

    def wall_rear_x(self, t: float, y_abs: float) -> float:
        value = _outline_x_at(self.outline(t, 0.0), y_abs, 1.0)
        return self.plan_x_lo(t) if value is None else value

    @property
    def rear_datum_x(self) -> float:
        """Rear-flange hardware datum resolved from the active plan family."""
        return self.rim_rear_x(self.rear_ref_y)

    @property
    def lid_knuckle_half(self) -> float:
        """Lid knuckle half span: always inboard of the handle uprights."""
        return _clamp(0.16 * self.tub_width_m, 0.060, self.handle_half_y - 0.115)

    @property
    def lid_barrel_outer_y(self) -> float:
        return self.lid_knuckle_half + 0.5 * _LID_BARREL_LEN

    @property
    def fixed_handle_post_x(self) -> float:
        """Rigid handle posts are seated from the flange edge at their own station."""
        return self.rim_rear_x(self.handle_half_y) + 0.016

    def plan_x_lo(self, t: float) -> float:
        return -self.half_len + REAR_LEAN * (1.0 - t)

    def plan_x_hi(self, t: float) -> float:
        return self.half_len - self.nose_run * (1.0 - t)

    def plan_y_half(self, t: float) -> float:
        return self.half_wid * (self.wall_draft_ratio + (1.0 - self.wall_draft_ratio) * t)

    def plan_corner(self, t: float) -> float:
        return 0.055 + 0.035 * t

    def station(self, t: float, offset: float):
        return (
            self.plan_x_lo(t) - offset,
            self.plan_x_hi(t) + offset,
            self.plan_y_half(t) + offset,
            max(0.006, self.plan_corner(t) + offset),
        )

    def outline(self, t: float, offset: float = 0.0):
        return _plan_outline(self.shell_form, *self.station(t, offset))

    def t_at_z(self, z: float) -> float:
        return _clamp((z - self.floor_z) / max(1e-6, self.wall_h), 0.0, 1.0)

    def wall_y(self, z: float, x: float, side: float = 1.0) -> float:
        """Resolve the moulded wall surface at (x, z) on one side.

        The query station is clamped into the plan's own X extent first, so a
        strongly converging plan (v_nose) still seats its ribs on real wall
        instead of collapsing them toward the centreline.
        """
        points = self.outline(self.t_at_z(z))
        lo = min(point[0] for point in points)
        hi = max(point[0] for point in points)
        query = _clamp(x, lo + 0.012, hi - 0.012)
        value = _outline_y_at(points, query, side)
        if value is None:
            return side * 0.55 * self.plan_y_half(self.t_at_z(z))
        return value

    @property
    def wheel_reach_z(self) -> float:
        return min(2.0 * self.rear_wheel_radius_m + 0.020, self.rim_wall_z)

    @property
    def rear_clear_y(self) -> float:
        """Widest shell half-width over the rear wheel footprint (host adaptation)."""
        radius = self.rear_wheel_radius_m
        best = 0.0
        for step in range(5):
            x = self.x_axle + radius * (-1.0 + 0.5 * step)
            best = max(best, abs(self.wall_y(self.wheel_reach_z, x)))
        # The moulded ribs stand proud of the wall over the same footprint, so
        # the road wheels have to clear the rib crest, not just the shell.
        return best + 1.35 * self.rib_relief_m

    @property
    def rear_wheel_y(self) -> float:
        return self.rear_clear_y + 0.012 + 0.5 * self.rear_wheel_width

    @property
    def bearing_face_y(self) -> float:
        """Outer face of the rear bearing block / axle beam."""
        return self.rear_clear_y + 0.006

    @property
    def deck_rail_y(self) -> float:
        return min(
            max(0.06, 0.52 * self.plan_y_half(0.0)),
            self.bearing_face_y - 0.035,
        )

    @property
    def bumper_z(self) -> float:
        return min(2.0 * self.rear_wheel_radius_m + 0.035, self.rim_wall_z - 0.090)

    @property
    def bumper_offset(self) -> float:
        """Bumper stand-off: past the deepest rib relief plus the tube section."""
        return 0.050 + 1.35 * self.rib_relief_m

    @property
    def rib_relief(self) -> float:
        return self.rib_relief_m

    @property
    def lid_hinge_x(self) -> float:
        """Hinge station on the rear flange, resolved from the active plan family."""
        return self.rim_rear_x(self.handle_half_y) + 0.030

    @property
    def lid_hinge_z(self) -> float:
        return self.rim_z + 0.030

    @property
    def lid_rear_cut_x(self) -> float:
        """Rear trim plane of the lid: the lid covers the rim forward of it."""
        return self.lid_hinge_x + LID_PANEL_SETBACK

    def lid_plan(self, offset: float):
        """The moulded lid plan for the ACTIVE shell_form.

        var_hinged_lid_v2 model.py:L80-L95 lofts the lid panel from the shared
        ``_rim_outline`` descriptor, not from an unrelated rectangle.  Here the
        shared descriptor is ``outline(1.0, FLANGE_OUT)`` — the real top-flange
        edge of whichever plan family is active — outset by a true metric
        ``offset`` and trimmed to the region forward of the hinge line.
        """
        rim = self.outline(1.0, FLANGE_OUT)
        return _clip_outline_front(_offset_outline(rim, offset), self.lid_rear_cut_x)

    @property
    def lid_length(self) -> float:
        return (self.plan_x_hi(1.0) + FLANGE_OUT + LID_OVERHANG) - self.lid_rear_cut_x

    @property
    def lid_half_wid(self) -> float:
        return self.plan_y_half(1.0) + FLANGE_OUT + LID_OVERHANG

    @property
    def handle_post_x(self) -> float:
        return self.rear_datum_x + 0.014

    @property
    def handle_half_y(self) -> float:
        return min(0.30 * self.tub_width_m, 0.58 * self.plan_y_half(1.0))

    @property
    def handle_hinge_z(self) -> float:
        """Fold hinge line: on the rear wall below the rim, so the folding handle
        and the rim-mounted lid hinge never share space."""
        return self.rim_z - 0.090

    @property
    def handle_fold_x(self) -> float:
        return self.rim_rear_x(self.handle_half_y) - 0.026


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x0726_7411)
    return Config(
        shell_form=choices["shell_form"],
        underframe=choices["underframe"],
        front_support=choices["front_support"],
        handle=choices["handle"],
        lid=choices["lid"],
        rear_wheel=choices["rear_wheel"],
        rib=choices["rib"],
        rib_count=int(choices["rib_count"]),
        tub_length_m=round(rng.uniform(1.05, 1.60), 4),
        tub_width_m=round(rng.uniform(0.62, 0.95), 4),
        tub_height_m=round(rng.uniform(0.44, 0.78), 4),
        wall_draft_ratio=round(rng.uniform(0.55, 0.86), 4),
        nose_run_ratio=round(rng.uniform(0.28, 0.58), 4),
        rear_wheel_radius_m=round(rng.uniform(0.115, 0.200), 4),
        front_wheel_ratio=round(rng.uniform(0.28, 0.44), 4),
        rib_relief_m=round(rng.uniform(0.010, 0.024), 4),
        handle_rise_m=round(rng.uniform(0.17, 0.42), 4),
        lid_open_rad=round(rng.uniform(1.20, 1.52), 4),
        handle_fold_rad=round(rng.uniform(1.05, 1.55), 4),
        brake_travel_rad=round(rng.uniform(0.22, 0.40), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"urban_environment_tilt_truck1_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "shell_form": cfg.shell_form,
            "underframe": cfg.underframe,
            "front_support": cfg.front_support,
            "handle": cfg.handle,
            "lid": cfg.lid,
            "rear_wheel": cfg.rear_wheel,
            "rib": cfg.rib,
            "rib_count": int(cfg.rib_count),
        }
    )
    return ResolvedConfig(
        shell_form=_pick(cfg.shell_form, SHELL_FORMS),
        underframe=_pick(cfg.underframe, UNDERFRAMES),
        front_support=_pick(cfg.front_support, FRONT_SUPPORTS),
        handle=_pick(cfg.handle, HANDLE_STYLES),
        lid=_pick(cfg.lid, LID_STYLES),
        rear_wheel=_pick(cfg.rear_wheel, REAR_WHEEL_STYLES),
        rib=_pick(cfg.rib, RIB_STYLES),
        rib_count=int(_pick(int(cfg.rib_count), RIB_COUNTS)),
        tub_length_m=_clamp(cfg.tub_length_m, 1.05, 1.60),
        tub_width_m=_clamp(cfg.tub_width_m, 0.62, 0.95),
        tub_height_m=_clamp(cfg.tub_height_m, 0.44, 0.78),
        wall_draft_ratio=_clamp(cfg.wall_draft_ratio, 0.55, 0.86),
        nose_run_ratio=_clamp(cfg.nose_run_ratio, 0.28, 0.58),
        rear_wheel_radius_m=_clamp(cfg.rear_wheel_radius_m, 0.115, 0.200),
        front_wheel_ratio=_clamp(cfg.front_wheel_ratio, 0.28, 0.44),
        rib_relief_m=_clamp(cfg.rib_relief_m, 0.010, 0.024),
        handle_rise_m=_clamp(cfg.handle_rise_m, 0.17, 0.42),
        lid_open_rad=_clamp(cfg.lid_open_rad, 1.20, 1.52),
        handle_fold_rad=_clamp(cfg.handle_fold_rad, 1.05, 1.55),
        brake_travel_rad=_clamp(cfg.brake_travel_rad, 0.22, 0.40),
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        name=cfg.name or "urban_environment_tilt_truck1",
    )


def slot_choices_for_config(config) -> tuple[tuple[str, object], ...]:
    r = config if isinstance(config, ResolvedConfig) else resolve_config(config)
    return (
        ("shell_form", r.shell_form),
        ("underframe", r.underframe),
        ("front_support", r.front_support),
        ("handle", r.handle),
        ("lid", r.lid),
        ("rear_wheel", r.rear_wheel),
        ("rib", r.rib),
        ("rib_count", r.rib_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Axis-mated joint helper (every rotational joint is registered for QC)
# ---------------------------------------------------------------------------
def _axis_joint(
    model,
    *,
    name,
    parent,
    child,
    point,
    axis,
    radial,
    articulation_type,
    limits,
    damping=0.10,
    friction=0.05,
    meta=None,
):
    provider = AxisInterface(name=f"{name}.provider", point=point, axis=axis, radial=radial)
    consumer = AxisInterface(
        name=f"{name}.consumer", point=(0.0, 0.0, 0.0), axis=axis, radial=radial
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        articulation_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=damping, friction=friction),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)


__all__ = [
    "TEMPLATE_DOMAIN",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]


# ===========================================================================
# shell_form candidates: the moulded hopper
# ===========================================================================
def _shell_stations(r: ResolvedConfig):
    """Outer wall up, flange ring over, inner wall down, moulded floor."""
    mid_z = r.floor_z + 0.5 * r.wall_h
    return (
        (0.0, 0.0, r.floor_z),
        (0.5, 0.0, mid_z),
        (1.0, 0.0, r.rim_wall_z),
        (1.0, FLANGE_OUT, r.rim_wall_z),
        (1.0, FLANGE_OUT, r.rim_z),
        (1.0, -WALL_T, r.rim_z),
        (0.5, -WALL_T, mid_z),
        (0.0, -WALL_T, r.floor_z + FLOOR_T),
    )


def _shell_geometry(r: ResolvedConfig) -> MeshGeometry:
    geometry = MeshGeometry()
    loops: list[list[int]] = []
    for t, offset, z in _shell_stations(r):
        points = r.outline(t, offset)
        loops.append([geometry.add_vertex(x, y, z) for x, y in points])
    for lower, upper in zip(loops, loops[1:]):
        _stitch(geometry, lower, upper)
    outer_lo = r.station(0.0, 0.0)
    inner_lo = r.station(0.0, -WALL_T)
    _cap(
        geometry,
        loops[0],
        (0.5 * (outer_lo[0] + outer_lo[1]), 0.0, r.floor_z),
        reverse=True,
    )
    _cap(
        geometry,
        loops[-1],
        (0.5 * (inner_lo[0] + inner_lo[1]), 0.0, r.floor_z + FLOOR_T),
        reverse=False,
    )
    return geometry


def _emit_shell_body(shell, offset, r: ResolvedConfig, mats, candidate: str) -> None:
    shell.visual(
        mesh_from_geometry(_shell_geometry(r), f"tilt_truck1_hopper_{candidate}"),
        origin=_local_origin(None, offset),
        material=mats["shell"],
        name=f"shell_form__{candidate}__hopper", material_class_id="plastic.opaque_glossy_molded",
    )


def _shell_form_tapered_rect_build(shell, offset, r: ResolvedConfig, mats) -> None:
    """002 model.py:L63-L89, L112-L182 — rounded-rect stations, near-vertical rear
    wall and a long forward-and-down discharge nose under one fused top flange."""
    _emit_shell_body(shell, offset, r, mats, "tapered_rect")


def _shell_form_chamfered_octagon_build(shell, offset, r: ResolvedConfig, mats) -> None:
    """var_form_chamfered_octagonal model.py:L52-L107, L162-L194 — the same station
    descriptor read through a constant 45-degree chamfered octagon outline."""
    _emit_shell_body(shell, offset, r, mats, "chamfered_octagon")


def _shell_form_obround_build(shell, offset, r: ResolvedConfig, mats) -> None:
    """var_form_obround model.py:L28-L112, L168-L204 — true stadium plan: straight
    side runs with semicircular rear and nose ends."""
    _emit_shell_body(shell, offset, r, mats, "obround")


def _shell_form_v_nose_build(shell, offset, r: ResolvedConfig, mats) -> None:
    """var_form_vnose model.py:L53-L137, L140-L182 — plan half-width tapering to a
    rounded V discharge spout while the rear end stays a full-width hopper."""
    _emit_shell_body(shell, offset, r, mats, "v_nose")


_SHELL_BUILDERS = {
    "tapered_rect": _shell_form_tapered_rect_build,
    "chamfered_octagon": _shell_form_chamfered_octagon_build,
    "obround": _shell_form_obround_build,
    "v_nose": _shell_form_v_nose_build,
}


# ===========================================================================
# rib candidates + rib_count multiplicity
# ===========================================================================
def _rib_band(r: ResolvedConfig) -> tuple[float, float]:
    z_lo = r.floor_z + 0.22 * r.wall_h
    z_hi = r.rim_wall_z - 0.045
    return z_lo, max(z_lo + 0.04, z_hi)


def _rib_positions(r: ResolvedConfig) -> list[float]:
    """var_ribs_n5 model.py:L63-L88 — one capacity rule, not hand-tuned offsets.

    The usable span is intersected with the plan at the LOWEST rib station, so
    every rib has real wall under its full height on a converging nose.
    """
    t = 0.6
    x_lo = r.plan_x_lo(t)
    span = r.plan_x_hi(t) - x_lo
    z_lo, _z_hi = _rib_band(r)
    t_lo = r.t_at_z(z_lo)
    low_lo = r.plan_x_lo(t_lo)
    low_span = r.plan_x_hi(t_lo) - low_lo
    start = max(x_lo + 0.16 * span, low_lo + 0.12 * low_span)
    end = min(x_lo + 0.68 * span, low_lo + 0.80 * low_span)
    if end <= start + 0.02:
        end = start + 0.02
    count = int(r.rib_count)
    if count < 2:
        return [0.5 * (start + end)]
    pitch = (end - start) / (count - 1)
    return [start + index * pitch for index in range(count)]


def _rib_section(r: ResolvedConfig, candidate: str, x: float, side: float, z: float):
    surface = abs(r.wall_y(z, x, side))
    inner = side * (surface - RIB_EMBED)
    if candidate == "raised_rail":
        half = 0.015
        outer = side * (surface + r.rib_relief * 1.35)
        points = [
            (x - half, inner),
            (x + half, inner),
            (x + half, outer),
            (x - half, outer),
        ]
    else:
        half = 0.046
        mid = side * (surface + r.rib_relief * 0.45)
        outer = side * (surface + r.rib_relief * 0.85)
        points = [
            (x - half, inner),
            (x - half * 0.62, mid),
            (x - half * 0.22, outer),
            (x + half * 0.22, outer),
            (x + half * 0.62, mid),
            (x + half, inner),
        ]
    return points if side > 0 else list(reversed(points))


def _emit_ribs(shell, offset, r: ResolvedConfig, mats, candidate: str) -> None:
    z_lo, z_hi = _rib_band(r)
    for index, x in enumerate(_rib_positions(r)):
        for tag, side in SIDES:
            name = f"rib__{candidate}__wall{tag}_{index}"
            geometry = _prism(
                (
                    _rib_section(r, candidate, x, side, z_lo),
                    _rib_section(r, candidate, x, side, z_hi),
                ),
                z_lo,
                z_hi,
            )
            shell.visual(
                mesh_from_geometry(geometry, f"tilt_truck1_{name}"),
                origin=_local_origin(None, offset),
                material=mats["shell_dark"],
                name=name, material_class_id="plastic.opaque_glossy_molded",
            )


def _rib_draft_panel_build(shell, offset, r: ResolvedConfig, mats) -> None:
    """004 model.py:L59-L122 — broad shallow draft-matched panel rib with stepped
    shoulders, embedded into the moulded wall."""
    _emit_ribs(shell, offset, r, mats, "draft_panel")


def _rib_raised_rail_build(shell, offset, r: ResolvedConfig, mats) -> None:
    """002 model.py:L153-L161, L360-L376 — fine raised rail seated on the tapered
    side wall, a narrow high-relief section instead of a broad panel."""
    _emit_ribs(shell, offset, r, mats, "raised_rail")


_RIB_BUILDERS = {
    "draft_panel": _rib_draft_panel_build,
    "raised_rail": _rib_raised_rail_build,
}


# ===========================================================================
# handle candidates
# ===========================================================================
def _handle_twin_grab_bars_build(model, shell, offset, r: ResolvedConfig, mats) -> None:
    """001 model.py:L392-L411 — two separate horizontal grab bars with rubber grip
    sleeves seated into the moulded rear end; no crossbar and no added joint."""
    post_h = 0.55 * r.handle_rise_m
    post_x = r.fixed_handle_post_x
    for tag, side in SIDES:
        y = side * r.handle_half_y
        _cyl(
            shell,
            0.014,
            post_h + 0.020,
            (post_x, y, r.rim_z + 0.5 * post_h - 0.010),
            mats["frame"],
            f"handle__twin_grab_bars__post_{tag}",
            offset=offset,
        )
        bar_len = 0.16
        _cyl(
            shell,
            0.014,
            bar_len,
            (post_x - 0.5 * bar_len + 0.012, y, r.rim_z + post_h),
            mats["frame"],
            f"handle__twin_grab_bars__bar_{tag}",
            rpy=(0.0, math.pi / 2.0, 0.0),
            offset=offset,
        )
        _cyl(
            shell,
            0.019,
            0.085,
            (post_x - bar_len + 0.055, y, r.rim_z + post_h),
            mats["rubber"],
            f"handle__twin_grab_bars__grip_{tag}",
            rpy=(0.0, math.pi / 2.0, 0.0),
            offset=offset,
        )


def _handle_u_frame_fixed_build(model, shell, offset, r: ResolvedConfig, mats) -> None:
    """004 model.py:L440-L456 / 002 model.py:L378-L401 — a square-cornered U push
    handle: two uprights off the rear flange joined by one straight crossbar."""
    rise = r.handle_rise_m
    post_x = r.fixed_handle_post_x
    for tag, side in SIDES:
        y = side * r.handle_half_y
        _cyl(
            shell,
            0.016,
            rise + 0.020,
            (post_x, y, r.rim_z + 0.5 * rise - 0.010),
            mats["frame"],
            f"handle__u_frame_fixed__upright_{tag}",
            offset=offset,
        )
        _box(
            shell,
            (0.046, 0.046, 0.030),
            (post_x, y, r.rim_z + rise - 0.014),
            mats["frame"],
            f"handle__u_frame_fixed__corner_{tag}",
            offset=offset,
        )
    _cyl(
        shell,
        0.016,
        2.0 * r.handle_half_y,
        (post_x, 0.0, r.rim_z + rise),
        mats["frame"],
        "handle__u_frame_fixed__crossbar",
        rpy=(math.pi / 2.0, 0.0, 0.0),
        offset=offset,
    )


def _handle_folding_u_frame_build(model, shell, offset, r: ResolvedConfig, mats) -> None:
    """var_handle_folding model.py:L153-L172, L398-L460, L512-L530 — moulded lateral
    hinge barrels on the rear flange plus a separate REVOLUTE push-handle part."""
    barrel_y = r.handle_half_y + 0.075
    fold_x = r.handle_fold_x
    fold_z = r.handle_hinge_z
    fold_t = r.t_at_z(fold_z)
    for tag, side in SIDES:
        y = side * barrel_y
        _cyl(
            shell,
            0.020,
            0.090,
            (fold_x, y, fold_z),
            mats["shell_dark"],
            f"handle__folding_u_frame__barrel_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
            offset=offset,
        )
        seat_lo = fold_x - 0.018
        seat_hi = r.wall_rear_x(fold_t, barrel_y) + 0.030
        _box(
            shell,
            (max(0.044, seat_hi - seat_lo), 0.086, 0.056),
            (0.5 * (seat_lo + seat_hi), y, fold_z),
            mats["shell_dark"],
            f"handle__folding_u_frame__pedestal_{tag}",
            offset=offset,
        )

    handle = model.part(
        "push_handle", meta={"role": "push_handle", "candidate": "folding_u_frame"}
    )
    rise = r.handle_rise_m + 0.090
    for tag, side in SIDES:
        y = side * r.handle_half_y
        _cyl(
            handle,
            0.016,
            rise,
            (0.0, y, 0.5 * rise),
            mats["frame"],
            f"handle__folding_u_frame__upright_{tag}",
        )
        stub_lo = r.handle_half_y
        stub_hi = barrel_y - 0.045 + SHELL_BITE
        _cyl(
            handle,
            0.014,
            stub_hi - stub_lo,
            (0.0, side * 0.5 * (stub_lo + stub_hi), 0.0),
            mats["zinc"],
            f"handle__folding_u_frame__hinge_stub_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    _cyl(
        handle,
        0.016,
        2.0 * r.handle_half_y,
        (0.0, 0.0, rise),
        mats["frame"],
        "handle__folding_u_frame__crossbar",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _cyl(
        handle,
        0.020,
        0.110,
        (0.0, 0.0, rise),
        mats["rubber"],
        "handle__folding_u_frame__grip",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _axis_joint(
        model,
        name="push_handle_fold",
        parent=shell.name,
        child=handle.name,
        point=_local_point((fold_x, 0.0, fold_z), offset),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=22.0, velocity=2.0, lower=0.0, upper=r.handle_fold_rad),
        damping=0.30,
        friction=0.18,
        meta={"mechanism": "rear flange handle fold"},
    )


def _handle_molded_grips_build(model, shell, offset, r: ResolvedConfig, mats) -> None:
    """var_handle_molded_grips model.py:L167-L197, L329-L359, L721-L741 — no steel
    hardware: moulded C-section grab handles on the drafted rear wall plus a
    thickened continuous rim ledge handhold."""
    grip_z = r.rim_z - 0.115
    grip_t = r.t_at_z(grip_z)
    for tag, side in SIDES:
        grip_y = 0.36 * r.plan_y_half(grip_t)
        y = side * grip_y
        wall_x = r.wall_rear_x(grip_t, grip_y + 0.068)
        for index, dy in ((0, -0.055), (1, 0.055)):
            _box(
                shell,
                (0.060, 0.026, 0.070),
                (wall_x - 0.020, y + side * dy, grip_z),
                mats["shell_dark"],
                f"handle__molded_grips__web_{tag}_{index}",
                offset=offset,
            )
        _box(
            shell,
            (0.026, 0.150, 0.070),
            (wall_x - 0.042, y, grip_z),
            mats["shell_dark"],
            f"handle__molded_grips__bar_{tag}",
            offset=offset,
        )
    ledge_y = 0.35 * r.plan_y_half(1.0)
    _box(
        shell,
        (0.050, 2.0 * ledge_y, 0.026),
        (r.rim_rear_x(ledge_y) + 0.018, 0.0, r.rim_z - 0.015),
        mats["shell_dark"],
        "handle__molded_grips__rim_ledge",
        offset=offset,
    )


_HANDLE_BUILDERS = {
    "twin_grab_bars": _handle_twin_grab_bars_build,
    "u_frame_fixed": _handle_u_frame_fixed_build,
    "folding_u_frame": _handle_folding_u_frame_build,
    "molded_grips": _handle_molded_grips_build,
}


# ===========================================================================
# lid candidates
# ===========================================================================
_LID_BARREL_LEN = 0.090
# Knuckle / web geometry (lid-local frame, origin on the hinge axis).  The webs
# are what fuse the moving knuckle to the panel; the v1 fork was rejected for
# leaving a 19 mm air gap here, so these are asserted, not assumed.
_LID_KNUCKLE_R = 0.017
_LID_WEB_REAR_X = 0.0
_LID_WEB_FRONT_X = 0.052
_LID_WEB_TOP_Z = 0.014
_LID_WEB_HALF_Y = 0.025


def _lid_barrel_y(r: ResolvedConfig) -> float:
    """Barrel centre: the barrels flank the knuckle and overlap its ends by the
    bearing bite, so the moving lid stays journalled at every hinge pose
    (var_hinged_lid_v2 model.py:L62-L77)."""
    return r.lid_knuckle_half + 0.5 * _LID_BARREL_LEN - SHELL_BITE


def _lid_local_plan(r: ResolvedConfig, points):
    """Re-express a truck-frame lid plan in the lid link's own frame.

    The lid link's origin is the hinge axis, so the shared rim outline has to be
    published relative to it before it becomes lid geometry.
    """
    return [(x - r.lid_hinge_x, y) for x, y in points]


def _lid_open_top_build(model, shell, offset, r: ResolvedConfig, mats) -> None:
    """003 model.py:L53-L116, L253-L268 — open hopper: the heavy rolled lip is the
    only top structure, no lid part and no lid joint."""
    points = r.outline(1.0, FLANGE_OUT - 0.013)
    count = len(points)
    for index in range(count):
        p0 = points[index]
        p1 = points[(index + 1) % count]
        _beam(
            shell,
            (p0[0], p0[1], r.rim_z + 0.002),
            (p1[0], p1[1], r.rim_z + 0.002),
            0.020,
            mats["shell_dark"],
            f"lid__open_top__lip_bead_{index}",
            offset=offset,
        )


def _lid_hinged_lid_build(model, shell, offset, r: ResolvedConfig, mats) -> None:
    """var_hinged_lid_v2 model.py:L42-L77, L80-L181, L427-L449, L613-L641, L685-L699.

    Bored hinge barrels on integral pedestals fused into the rear flange, a
    one-piece moulded lid (panel + downturned perimeter skirt lip + knuckle tube
    + real webs) and a bounded REVOLUTE hinge.  The v1 fork was rejected for
    leaving the knuckle as a floating island, so the knuckle here is joined to
    the panel by webs whose rear face sits on the hinge plane and can never dip
    under the flange.

    ``_lid_shell`` (model.py:L80-L181) derives every lid dimension from the
    shared ``_rim_outline`` descriptor.  This template therefore takes the panel
    plan and the skirt lip from ``r.lid_plan(...)`` — the ACTIVE shell_form's own
    top-flange outline, metrically outset and trimmed at the hinge line — so the
    lid follows the rim on all four plan families (rounded rect, chamfered
    octagon, obround stadium ends, converging V nose) instead of overhanging at
    the corners and gapping at the curved runs.
    """
    barrel_y = _lid_barrel_y(r)
    knuckle_half = r.lid_knuckle_half
    for tag, side in SIDES:
        y = side * barrel_y
        _cyl(
            shell,
            0.020,
            _LID_BARREL_LEN,
            (r.lid_hinge_x, y, r.lid_hinge_z),
            mats["shell_dark"],
            f"lid__hinged_lid__barrel_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
            offset=offset,
        )
        seat_lo = r.rim_rear_x(barrel_y) + 0.006
        seat_hi = r.lid_hinge_x + 0.018
        _box(
            shell,
            (max(0.040, seat_hi - seat_lo), 0.086, r.lid_hinge_z - r.rim_z + 0.018),
            (
                0.5 * (seat_lo + seat_hi),
                y,
                0.5 * (r.rim_z - 0.018 + r.lid_hinge_z),
            ),
            mats["shell_dark"],
            f"lid__hinged_lid__pedestal_{tag}",
            offset=offset,
        )
        pin_lo = knuckle_half + 0.004
        pin_hi = barrel_y + 0.5 * _LID_BARREL_LEN - 0.006
        _cyl(
            shell,
            0.008,
            max(0.010, pin_hi - pin_lo),
            (r.lid_hinge_x, side * 0.5 * (pin_lo + pin_hi), r.lid_hinge_z),
            mats["zinc"],
            f"lid__hinged_lid__hinge_pin_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
            offset=offset,
        )

    lid = model.part("lid", meta={"role": "lid", "candidate": "hinged_lid"})
    panel_under = r.rim_z - SHELL_BITE - r.lid_hinge_z

    # -- moulded panel: the rim outline itself, outset and trimmed -----------
    panel_points = _lid_local_plan(r, r.lid_plan(LID_OVERHANG))
    lid.visual(
        mesh_from_geometry(
            _prism((panel_points, panel_points), panel_under, panel_under + LID_PANEL_T),
            "tilt_truck1_lid_panel",
        ),
        material=mats["shell"],
        name="lid__hinged_lid__panel", material_class_id="plastic.opaque_glossy_molded",
    )

    # -- downturned perimeter skirt lip on the same outline ------------------
    # var_hinged_lid_v2 model.py:L96-L145 builds the skirt as real moulded walls
    # standing just outboard of the shared rim outline and open at the rear so
    # the hinge barrels stay clear.  Following the outline (rather than two
    # straight side bars) is what makes the lid *seat* on the rim on the obround
    # and V-nose plans instead of floating over a corner gap.
    skirt_points = _lid_local_plan(r, r.lid_plan(LID_RIM_CLEAR + 0.5 * LID_SKIRT_T))
    skirt_hi = panel_under + LID_SKIRT_BITE
    skirt_lo = panel_under - LID_SKIRT_DROP
    skirt_start = LID_PANEL_SETBACK + LID_SKIRT_SETBACK
    count = len(skirt_points)
    for index in range(count):
        p = skirt_points[index]
        q = skirt_points[(index + 1) % count]
        if min(p[0], q[0]) < skirt_start:
            continue
        dx, dy = q[0] - p[0], q[1] - p[1]
        span = math.hypot(dx, dy)
        if span < 1e-6:
            continue
        _box(
            lid,
            (span + LID_SKIRT_T, LID_SKIRT_T, skirt_hi - skirt_lo),
            (0.5 * (p[0] + q[0]), 0.5 * (p[1] + q[1]), 0.5 * (skirt_lo + skirt_hi)),
            mats["shell_dark"],
            f"lid__hinged_lid__skirt_{index}",
            rpy=(0.0, 0.0, math.atan2(dy, dx)),
        )
    _cyl(
        lid,
        _LID_KNUCKLE_R,
        2.0 * knuckle_half,
        (0.0, 0.0, 0.0),
        mats["shell_dark"],
        "lid__hinged_lid__knuckle",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    for tag, side in SIDES:
        _box(
            lid,
            (
                _LID_WEB_FRONT_X - _LID_WEB_REAR_X,
                2.0 * _LID_WEB_HALF_Y,
                _LID_WEB_TOP_Z - panel_under,
            ),
            (
                0.5 * (_LID_WEB_REAR_X + _LID_WEB_FRONT_X),
                side * 0.5 * knuckle_half,
                0.5 * (panel_under + _LID_WEB_TOP_Z),
            ),
            mats["shell_dark"],
            f"lid__hinged_lid__web_{tag}",
        )
    _axis_joint(
        model,
        name="lid_hinge",
        parent=shell.name,
        child=lid.name,
        point=_local_point((r.lid_hinge_x, 0.0, r.lid_hinge_z), offset),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=30.0, velocity=1.8, lower=0.0, upper=r.lid_open_rad),
        damping=0.60,
        friction=0.30,
        meta={"mechanism": "rear rim lid hinge"},
    )


_LID_BUILDERS = {
    "open_top": _lid_open_top_build,
    "hinged_lid": _lid_hinged_lid_build,
}


# ===========================================================================
# Wheels (local spin axis is +Y; the hub boss is the bearing contact)
# ===========================================================================
HUB_STICK = 0.0065


def _tyre_geometry(radius: float, width: float, name: str):
    """004 model.py:L276-L319 — one-piece utility tyre revolved from a real
    cross-section (bead shelf, shoulders, crowned tread)."""
    half = 0.5 * width
    inner = radius * 0.62
    profile = [
        (inner, -half * 0.72),
        (inner * 1.04, -half),
        (radius * 0.93, -half),
        (radius, -half * 0.66),
        (radius, half * 0.66),
        (radius * 0.93, half),
        (inner * 1.04, half),
        (inner, half * 0.72),
    ]
    geometry = LatheGeometry(profile, segments=26)
    geometry.rotate((1.0, 0.0, 0.0), math.pi / 2.0)
    return mesh_from_geometry(geometry, name)


def _ring_geometry(outer: float, inner: float, width: float, name: str):
    half = 0.5 * width
    geometry = LatheGeometry(
        [(inner, -half), (outer, -half), (outer, half), (inner, half)], segments=24
    )
    geometry.rotate((1.0, 0.0, 0.0), math.pi / 2.0)
    return mesh_from_geometry(geometry, name)


def _emit_hub_boss(part, radius: float, width: float, mats, name: str) -> None:
    _cyl(
        part,
        radius * 0.21,
        width + 2.0 * HUB_STICK,
        (0.0, 0.0, 0.0),
        mats["zinc"],
        name,
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )


def _rear_wheel_spoked_rim_build(part, r: ResolvedConfig, mats, tag: str) -> None:
    """001 model.py:L113-L181 — rim barrel with a bolted domed hub and straight
    spokes leaving real windows between them."""
    radius = r.rear_wheel_radius_m
    width = r.rear_wheel_width
    part.visual(
        _tyre_geometry(radius, width, f"tilt_truck1_rear_tyre_{tag}"),
        material=mats["rubber"],
        name=f"rear_wheel__spoked_rim__tyre_{tag}", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        _ring_geometry(radius * 0.64, radius * 0.55, width * 0.70, f"tilt_truck1_rear_rim_{tag}"),
        material=mats["wheel"],
        name=f"rear_wheel__spoked_rim__rim_barrel_{tag}", material_class_id="metal.paint_coated",
    )
    spoke_len = radius * 0.62 - radius * 0.19
    for index in range(5):
        angle = 2.0 * math.pi * index / 5.0
        mid = radius * 0.19 + 0.5 * spoke_len
        part.visual(
            Box((0.018, width * 0.34, spoke_len)),
            origin=Origin(
                xyz=(mid * math.sin(angle), 0.0, mid * math.cos(angle)),
                rpy=(0.0, angle, 0.0),
            ),
            material=mats["wheel"],
            name=f"rear_wheel__spoked_rim__spoke_{tag}_{index}", material_class_id="metal.paint_coated",
        )
    _emit_hub_boss(part, radius, width, mats, f"rear_wheel__spoked_rim__hub_boss_{tag}")


def _rear_wheel_disc_rim_build(part, r: ResolvedConfig, mats, tag: str) -> None:
    """004 model.py:L276-L319 — pressed full-web wheel centre plus a small hub cap:
    a solid disc with no spokes and no windows."""
    radius = r.rear_wheel_radius_m
    width = r.rear_wheel_width
    part.visual(
        _tyre_geometry(radius, width, f"tilt_truck1_rear_tyre_{tag}"),
        material=mats["rubber"],
        name=f"rear_wheel__disc_rim__tyre_{tag}", material_class_id="rubber.smooth_plain",
    )
    _cyl(
        part,
        radius * 0.63,
        width * 0.42,
        (0.0, 0.0, 0.0),
        mats["wheel"],
        f"rear_wheel__disc_rim__web_disc_{tag}",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _cyl(
        part,
        radius * 0.30,
        width * 0.66,
        (0.0, 0.0, 0.0),
        mats["zinc"],
        f"rear_wheel__disc_rim__hub_cap_{tag}",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _emit_hub_boss(part, radius, width, mats, f"rear_wheel__disc_rim__hub_boss_{tag}")


_REAR_WHEEL_BUILDERS = {
    "spoked_rim": _rear_wheel_spoked_rim_build,
    "disc_rim": _rear_wheel_disc_rim_build,
}


def _emit_front_wheel(model, r: ResolvedConfig, mats, parent, point, parent_name: str):
    """Small solid-rubber caster roller with a through hub boss (002 model.py:L281-L298)."""
    radius = r.front_wheel_radius
    width = r.front_wheel_width
    wheel = model.part("front_wheel", meta={"role": "front_wheel", "candidate": r.front_support})
    wheel.visual(
        _tyre_geometry(radius, width, "tilt_truck1_front_tyre"),
        material=mats["rubber"],
        name="front_support__front_tyre", material_class_id="rubber.smooth_plain",
    )
    _cyl(
        wheel,
        radius * 0.62,
        width * 0.52,
        (0.0, 0.0, 0.0),
        mats["zinc"],
        "front_support__front_wheel_centre",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _cyl(
        wheel,
        radius * 0.24,
        width + 2.0 * HUB_STICK,
        (0.0, 0.0, 0.0),
        mats["zinc"],
        "front_support__front_hub_boss",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _axis_joint(
        model,
        name="front_wheel_roll",
        parent=parent_name,
        child=wheel.name,
        point=point,
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=14.0, velocity=28.0),
        damping=0.04,
        friction=0.02,
        meta={"mechanism": "front wheel roll"},
    )
    del parent
    return wheel


# ===========================================================================
# front_support candidates
# ===========================================================================
def _front_support_rigid_fork_build(model, chassis, r: ResolvedConfig, mats) -> None:
    """001 model.py:L356-L390 / 003 model.py:L141-L149 — a non-swivelling centre
    fork welded to the underframe: two cheeks, a top bridge and the axle caps.
    Only the wheel roll is articulated."""
    half = 0.5 * r.front_wheel_width
    cheek_lo = r.front_wheel_radius - 0.012
    cheek_hi = r.swivel_z + 0.010
    height = max(0.040, cheek_hi - cheek_lo)
    for tag, side in SIDES:
        y = side * (half + 0.0105)
        _box(
            chassis,
            (0.070, 0.009, height),
            (r.x_front, y, 0.5 * (cheek_lo + cheek_hi)),
            mats["frame"],
            f"front_support__rigid_fork__cheek_{tag}",
        )
        _cyl(
            chassis,
            0.010,
            0.008,
            (r.x_front, side * (half + 0.017), r.front_wheel_radius),
            mats["zinc"],
            f"front_support__rigid_fork__axle_cap_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    _box(
        chassis,
        (0.086, 2.0 * (half + 0.016), 0.024),
        (r.x_front, 0.0, r.swivel_z + 0.014),
        mats["frame"],
        "front_support__rigid_fork__bridge",
    )
    _emit_front_wheel(
        model,
        r,
        mats,
        chassis,
        (r.x_front, 0.0, r.front_wheel_radius),
        chassis.name,
    )


def _emit_caster_yoke(model, chassis, r: ResolvedConfig, mats, candidate: str):
    """002 model.py:L213-L225, L403-L433 — offset swivel yoke: thrust collar
    captured under the frame bearing housing, forged crown, two open cheeks."""
    _cyl(
        chassis,
        0.034,
        0.030,
        (r.x_front, 0.0, r.swivel_z + 0.015),
        mats["frame"],
        f"front_support__{candidate}__bearing_housing",
    )
    yoke = model.part("caster_yoke", meta={"role": "caster_yoke", "candidate": candidate})
    trail = r.caster_trail
    fork_len = r.swivel_z - r.front_wheel_radius
    half = 0.5 * r.front_wheel_width
    _cyl(
        yoke,
        0.034,
        0.014,
        (0.0, 0.0, -0.0065),
        mats["zinc"],
        f"front_support__{candidate}__thrust_collar",
    )
    cheek_lo = -fork_len - 0.012
    cheek_hi = -0.020
    for tag, side in SIDES:
        # 002 model.py:L213-L225 — an open clevis: the shoulder rises outboard of
        # the tyre to the thrust collar, so the wheel envelope stays clear of the
        # yoke no matter how large the roller is.
        _box(
            yoke,
            (trail + 0.050, 0.009, 0.028),
            (0.005 - 0.5 * trail, side * (half + 0.0105), -0.026),
            mats["frame"],
            f"front_support__{candidate}__shoulder_{tag}",
        )
        _box(
            yoke,
            (0.060, 0.009, max(0.030, cheek_hi - cheek_lo)),
            (-trail, side * (half + 0.0105), 0.5 * (cheek_lo + cheek_hi)),
            mats["frame"],
            f"front_support__{candidate}__cheek_{tag}",
        )
        _cyl(
            yoke,
            0.010,
            0.008,
            (-trail, side * (half + 0.017), -fork_len),
            mats["zinc"],
            f"front_support__{candidate}__axle_cap_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )
    _axis_joint(
        model,
        name="caster_swivel",
        parent=chassis.name,
        child=yoke.name,
        point=(r.x_front, 0.0, r.swivel_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        articulation_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=12.0, velocity=10.0),
        damping=0.08,
        friction=0.05,
        meta={"mechanism": "vertical caster swivel"},
    )
    _emit_front_wheel(model, r, mats, yoke, (-trail, 0.0, -fork_len), yoke.name)
    return yoke


def _front_support_swivel_caster_build(model, chassis, r: ResolvedConfig, mats) -> None:
    """002 model.py:L444-L478 — CONTINUOUS vertical swivel plus the trailing
    CONTINUOUS wheel roll."""
    _emit_caster_yoke(model, chassis, r, mats, "swivel_caster")


def _brake_pivot_local(r: ResolvedConfig) -> tuple[float, float, float]:
    """Pedal pivot in the yoke frame: above and behind the wheel, but always
    hanging clear of the frame's front mount plate at local z >= 0."""
    trail = r.caster_trail
    fork_len = r.swivel_z - r.front_wheel_radius
    px = -trail + 0.020
    pz = min(-fork_len + 0.55 * r.front_wheel_radius + 0.055, -0.034)
    py = 0.5 * r.front_wheel_width + 0.030
    return px, py, pz


def _brake_shoe_local(r: ResolvedConfig) -> tuple[float, float]:
    """Derived `brake_shoe_local`.

    var_caster_brake_pedal model.py:L263-L299 — back-rotate the applied tyre
    contact point into the released pedal frame, so the shoe closes on the tread
    exactly at `brake_travel_rad` and swings clear at every smaller angle.
    """
    _px, _py, pz = _brake_pivot_local(r)
    tx = -(r.front_wheel_radius + 0.031)
    tz = (r.front_wheel_radius - r.swivel_z) - pz
    angle = r.brake_travel_rad
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    return (tx * cos_a + tz * sin_a, -tx * sin_a + tz * cos_a)


def _front_support_swivel_caster_brake_build(model, chassis, r: ResolvedConfig, mats) -> None:
    """var_caster_brake_pedal model.py:L254-L311, L521-L565, L597-L611 — the swivel
    caster plus a welded pivot boss and a one-piece REVOLUTE step brake pedal."""
    yoke = _emit_caster_yoke(model, chassis, r, mats, "swivel_caster_brake")
    px, py, pz = _brake_pivot_local(r)
    _cyl(
        yoke,
        0.014,
        0.014,
        (px, py - 0.013, pz),
        mats["frame"],
        "front_support__swivel_caster_brake__pivot_boss",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )

    pedal = model.part(
        "brake_pedal", meta={"role": "brake_pedal", "candidate": "swivel_caster_brake"}
    )
    shoe_x, shoe_z = _brake_shoe_local(r)
    _cyl(
        pedal,
        0.010,
        0.013,
        (0.0, 0.0, 0.0),
        mats["zinc"],
        "front_support__swivel_caster_brake__pivot_hub",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    _beam(
        pedal,
        (0.0, 0.0, 0.0),
        (shoe_x, 0.0, shoe_z),
        0.013,
        mats["accent"],
        "front_support__swivel_caster_brake__lever_arm",
    )
    _beam(
        pedal,
        (0.0, 0.004, 0.0),
        (-0.055, 0.020, 0.002),
        0.012,
        mats["accent"],
        "front_support__swivel_caster_brake__foot_stem",
    )
    _box(
        pedal,
        (0.052, 0.044, 0.010),
        (-0.055, 0.030, 0.002),
        mats["accent"],
        "front_support__swivel_caster_brake__step_pad",
    )
    _box(
        pedal,
        (0.012, py, 0.010),
        (shoe_x, -0.5 * py, shoe_z),
        mats["accent"],
        "front_support__swivel_caster_brake__neck",
    )
    _box(
        pedal,
        (0.014, 0.016, 0.012),
        (shoe_x, -py, shoe_z),
        mats["rubber"],
        "front_support__swivel_caster_brake__shoe",
    )
    _axis_joint(
        model,
        name="caster_brake_pivot",
        parent=yoke.name,
        child=pedal.name,
        point=(px, py, pz),
        axis=(0.0, -1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        articulation_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=18.0, velocity=2.0, lower=0.0, upper=r.brake_travel_rad),
        damping=0.25,
        friction=0.15,
        meta={"mechanism": "caster step brake"},
    )


_FRONT_BUILDERS = {
    "rigid_fork": _front_support_rigid_fork_build,
    "swivel_caster": _front_support_swivel_caster_build,
    "swivel_caster_brake": _front_support_swivel_caster_brake_build,
}


# ===========================================================================
# Shared chassis core + underframe candidates
# ===========================================================================
def _cross_half_y(r: ResolvedConfig) -> float:
    return min(
        max(r.deck_rail_y + 0.030, 0.80 * r.plan_y_half(0.0) + 0.012),
        r.bearing_face_y - 0.012,
    )


def _emit_chassis_core(chassis, r: ResolvedConfig, mats) -> None:
    """Deck rails, transverse axle beam with its bearing blocks, forward spine and
    the front support mount plane shared by every underframe candidate."""
    deck_lo = r.plan_x_lo(0.0) + 0.020
    deck_hi = r.plan_x_hi(0.0) - 0.020
    for tag, side in SIDES:
        _box(
            chassis,
            (deck_hi - deck_lo, 0.050, DECK_T),
            (0.5 * (deck_lo + deck_hi), side * r.deck_rail_y, r.deck_z - 0.5 * DECK_T),
            mats["frame"],
            f"chassis__deck_rail_{tag}",
        )
    cross_y = _cross_half_y(r)
    for index, x in enumerate(
        (
            deck_lo + 0.040,
            0.5 * (deck_lo + deck_hi),
            deck_hi - 0.040,
        )
    ):
        _box(
            chassis,
            (0.045, 2.0 * cross_y, 0.036),
            (x, 0.0, r.deck_z - 0.018),
            mats["frame"],
            f"chassis__deck_crossmember_{index}",
        )

    _box(
        chassis,
        (0.075, 2.0 * r.bearing_face_y, 0.052),
        (r.x_axle, 0.0, r.axle_z),
        mats["frame"],
        "chassis__axle_beam",
    )
    for tag, side in SIDES:
        _box(
            chassis,
            (0.100, 0.050, 0.100),
            (r.x_axle, side * (r.bearing_face_y - 0.025), r.axle_z),
            mats["frame"],
            f"chassis__bearing_block_{tag}",
        )
        _cyl(
            chassis,
            0.014,
            0.024,
            (r.x_axle, side * (r.bearing_face_y - 0.012), r.axle_z),
            mats["zinc"],
            f"chassis__axle_stub_{tag}",
            rpy=(math.pi / 2.0, 0.0, 0.0),
        )

    spine_lo = deck_hi - 0.100
    spine_hi = r.x_front + 0.075
    _box(
        chassis,
        (max(0.10, spine_hi - spine_lo), 0.100, 0.036),
        (0.5 * (spine_lo + spine_hi), 0.0, r.deck_z - 0.032),
        mats["frame"],
        "chassis__front_spine",
    )
    _box(
        chassis,
        (0.140, 0.140, 0.030),
        (r.x_front, 0.0, r.swivel_z + 0.015),
        mats["frame"],
        "chassis__front_mount_plate",
    )


def _underframe_rail_cradle_build(chassis, r: ResolvedConfig, mats) -> None:
    """002 model.py:L185-L210 — welded twin-rail cradle: outer longitudinal rails
    tied to the deck crossmembers with corner gussets."""
    rail_y = min(0.80 * r.plan_y_half(0.0), _cross_half_y(r) - 0.014)
    deck_lo = r.plan_x_lo(0.0) + 0.030
    deck_hi = r.plan_x_hi(0.0) - 0.030
    for tag, side in SIDES:
        _box(
            chassis,
            (deck_hi - deck_lo, 0.032, 0.030),
            (0.5 * (deck_lo + deck_hi), side * rail_y, r.deck_z - 0.030),
            mats["frame"],
            f"underframe__rail_cradle__side_rail_{tag}",
        )
        for index, x in enumerate((deck_lo + 0.055, deck_hi - 0.055)):
            _box(
                chassis,
                (0.070, 0.026, 0.052),
                (x, side * (rail_y - 0.020), r.deck_z - 0.048),
                mats["frame"],
                f"underframe__rail_cradle__gusset_{tag}_{index}",
            )


def _underframe_fork_pockets_build(chassis, r: ResolvedConfig, mats) -> None:
    """var_frame_fork_pockets model.py:L63-L79, L203-L267 — two open-ended
    rectangular fork tunnels with real side walls, a raised floor and the skid
    plate acting as their roof."""
    outer = r.bearing_face_y - 0.004
    width = min(0.190, 0.42 * outer)
    pocket_y = max(0.5 * width + 0.020, outer - 0.5 * width - 0.010)
    lo = r.plan_x_lo(0.0) + 0.040
    hi = r.plan_x_hi(0.0) + 0.020
    length = max(0.20, hi - lo)
    roof_top = r.deck_z - 0.030
    floor_bottom = r.deck_z - 0.125
    for tag, side in SIDES:
        y = side * pocket_y
        for index, dy in ((0, -1.0), (1, 1.0)):
            _box(
                chassis,
                (length, 0.010, roof_top - floor_bottom),
                (
                    0.5 * (lo + hi),
                    y + dy * (0.5 * width + 0.005),
                    0.5 * (roof_top + floor_bottom),
                ),
                mats["frame"],
                f"underframe__fork_pockets__wall_{tag}_{index}",
            )
        _box(
            chassis,
            (length, width + 0.020, 0.020),
            (0.5 * (lo + hi), y, roof_top - 0.010),
            mats["frame"],
            f"underframe__fork_pockets__roof_{tag}",
        )
        _box(
            chassis,
            (length, width + 0.020, 0.014),
            (0.5 * (lo + hi), y, floor_bottom + 0.007),
            mats["frame"],
            f"underframe__fork_pockets__floor_{tag}",
        )


def _bumper_stations(r: ResolvedConfig) -> tuple[float, float, float]:
    # Evaluate the plan at the TOP of the tube section: the drafted wall is
    # widest there, so the whole ring clears it (004 model.py:L391-L412).
    t = r.t_at_z(r.bumper_z + 0.020)
    x_lo = r.plan_x_lo(t)
    x_hi = r.plan_x_hi(t)
    return t, x_lo, x_hi


def _underframe_tube_perimeter_build(chassis, r: ResolvedConfig, mats) -> None:
    """004 model.py:L391-L438 — closed tubular perimeter bumper ring following the
    moulded plan outline, carried on two transverse cross-tubes and four struts."""
    t, x_lo, x_hi = _bumper_stations(r)
    span = x_hi - x_lo
    points = r.outline(t, r.bumper_offset)
    count = len(points)
    for index in range(count):
        p = points[index]
        q = points[(index + 1) % count]
        _beam(
            chassis,
            (p[0], p[1], r.bumper_z),
            (q[0], q[1], r.bumper_z),
            0.028,
            mats["frame"],
            f"underframe__tube_perimeter__bumper_{index}",
        )

    # The struts stand outboard of the moulded wall, level with the wheels, so
    # every support station must clear the road-wheel envelope in X.
    keep_lo = r.x_axle - (r.rear_wheel_radius_m + 0.085)
    keep_hi = r.x_axle + (r.rear_wheel_radius_m + 0.085)
    stations: list[float] = []
    for fraction in (0.05, 0.20, 0.92, 0.78, 0.36, 0.62):
        x = x_lo + fraction * span
        if keep_lo < x < keep_hi:
            continue
        if any(abs(x - other) < 0.14 for other in stations):
            continue
        stations.append(x)
        if len(stations) == 2:
            break
    if not stations:
        stations = [x_lo + 0.05 * span]
    tube_z = r.deck_z - 0.030
    for index, x in enumerate(stations):
        y_edge = _outline_y_at(points, x, 1.0)
        if y_edge is None:
            y_edge = r.plan_y_half(t) + r.bumper_offset
        _box(
            chassis,
            (0.036, 2.0 * y_edge, 0.028),
            (x, 0.0, tube_z),
            mats["frame"],
            f"underframe__tube_perimeter__cross_tube_{index}",
        )
        for tag, side in SIDES:
            _box(
                chassis,
                (0.032, 0.032, r.bumper_z - tube_z),
                (x, side * y_edge, 0.5 * (r.bumper_z + tube_z)),
                mats["frame"],
                f"underframe__tube_perimeter__strut_{index}_{tag}",
            )


_UNDERFRAME_BUILDERS = {
    "rail_cradle": _underframe_rail_cradle_build,
    "fork_pockets": _underframe_fork_pockets_build,
    "tube_perimeter": _underframe_tube_perimeter_build,
}


# ===========================================================================
# Assembly
# ===========================================================================
def build_urban_environment_tilt_truck1(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "urban_environment_tilt_truck1",
            "body_motion": "rigidly_fixed",
            "wheel_topology": "two_rear_one_front",
        },
    )
    palette = dict(PALETTES[r.palette_style])
    palette.update(_HARDWARE)
    mats = {
        key: model.material(f"tilt_truck1_{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in palette.items()
    }

    chassis = model.part("chassis", meta={"role": "chassis", "candidate": r.underframe})
    _emit_chassis_core(chassis, r, mats)
    _UNDERFRAME_BUILDERS[r.underframe](chassis, r, mats)

    shell_link = model.part(
        "cargo_shell",
        meta={"role": "cargo_shell", "candidate": r.shell_form, "rigid_to_chassis": True},
    )
    shell_offset = r.mount_datum
    _SHELL_BUILDERS[r.shell_form](shell_link, shell_offset, r, mats)
    _RIB_BUILDERS[r.rib](shell_link, shell_offset, r, mats)
    _HANDLE_BUILDERS[r.handle](model, shell_link, shell_offset, r, mats)
    _LID_BUILDERS[r.lid](model, shell_link, shell_offset, r, mats)

    model.articulation(
        "body_mount",
        ArticulationType.FIXED,
        parent=chassis,
        child=shell_link,
        origin=Origin(xyz=r.mount_datum),
        meta={"mechanism": "rigid cargo shell mount", "tilting": False},
    )

    for tag, side in SIDES:
        wheel = model.part(
            f"rear_wheel_{tag}", meta={"role": "rear_wheel", "candidate": r.rear_wheel}
        )
        _REAR_WHEEL_BUILDERS[r.rear_wheel](wheel, r, mats, tag)
        _axis_joint(
            model,
            name=f"rear_wheel_{tag}_roll",
            parent=chassis.name,
            child=wheel.name,
            point=(r.x_axle, side * r.rear_wheel_y, r.axle_z),
            axis=(0.0, 1.0, 0.0),
            radial=(0.0, 0.0, 1.0),
            articulation_type=ArticulationType.CONTINUOUS,
            limits=MotionLimits(effort=45.0, velocity=22.0),
            damping=0.06,
            friction=0.03,
            meta={"mechanism": "rear road wheel roll"},
        )

    _FRONT_BUILDERS[r.front_support](model, chassis, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_urban_environment_tilt_truck1(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_urban_environment_tilt_truck1(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
_TILT_TOKENS = ("tilt", "dump", "tip", "hopper_pivot")


def run_urban_environment_tilt_truck1_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    joints = list(object_model.articulations)
    parts = {part.name: part for part in object_model.parts}
    movable = [
        joint
        for joint in joints
        if joint.articulation_type
        in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC, ArticulationType.CONTINUOUS)
    ]

    # ---- Category anchors -------------------------------------------------
    body_joints = [joint for joint in joints if joint.child == "cargo_shell"]
    ctx.check(
        "category_anchor: cargo shell is rigidly fixed to the rolling chassis",
        len(body_joints) == 1
        and body_joints[0].name == "body_mount"
        and body_joints[0].articulation_type == ArticulationType.FIXED
        and body_joints[0].parent == "chassis"
        and not any(
            token in joint.name.lower()
            for joint in movable
            for token in _TILT_TOKENS
        ),
        details=(
            f"body_joints={[(j.name, str(j.articulation_type), j.parent) for j in body_joints]}, "
            f"movable={[j.name for j in movable]}"
        ),
    )

    rear_rolls = [
        joint
        for joint in joints
        if joint.name.startswith("rear_wheel_") and joint.name.endswith("_roll")
    ]
    ctx.check(
        "category_anchor: two rear road wheels roll on one lateral axle line",
        len(rear_rolls) == 2
        and all(
            joint.parent == "chassis"
            and joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(joint.axis[1]) > 0.999
            and abs(joint.axis[0]) < 1e-6
            and abs(joint.axis[2]) < 1e-6
            and abs(joint.origin.xyz[0] - r.x_axle) < 1e-6
            and abs(joint.origin.xyz[2] - r.axle_z) < 1e-6
            for joint in rear_rolls
        ),
        details=f"rear_rolls={[(j.name, j.axis, j.origin.xyz) for j in rear_rolls]}",
    )

    front_rolls = [joint for joint in joints if joint.name == "front_wheel_roll"]
    expected_front_parent = (
        "chassis" if r.front_support == "rigid_fork" else "caster_yoke"
    )
    ctx.check(
        "category_anchor: the front support carries a rolling front wheel",
        len(front_rolls) == 1
        and front_rolls[0].articulation_type == ArticulationType.CONTINUOUS
        and front_rolls[0].parent == expected_front_parent
        and abs(front_rolls[0].axis[1]) > 0.999,
        details=(
            f"front_rolls={[(j.name, j.parent, j.axis) for j in front_rolls]}, "
            f"expected_parent={expected_front_parent}"
        ),
    )

    rib_names = sorted(
        visual.name
        for visual in parts["cargo_shell"].visuals
        if visual.name.startswith(f"rib__{r.rib}__")
    )
    ctx.check(
        "category_anchor: moulded side ribs follow the shell wall",
        len(rib_names) == 2 * r.rib_count,
        details=f"rib_count={r.rib_count}, ribs={len(rib_names)}",
    )

    if r.front_support in ("swivel_caster", "swivel_caster_brake"):
        swivel = object_model.get_articulation("caster_swivel")
        ctx.check(
            "category_anchor: front caster swivels about a vertical axis",
            swivel.articulation_type == ArticulationType.CONTINUOUS
            and swivel.parent == "chassis"
            and swivel.child == "caster_yoke"
            and abs(swivel.axis[2] - 1.0) < 1e-6
            and abs(swivel.axis[0]) < 1e-6
            and abs(swivel.axis[1]) < 1e-6,
            details=f"swivel={(swivel.parent, swivel.child, swivel.axis)!r}",
        )

    if r.front_support == "swivel_caster_brake":
        brake = object_model.get_articulation("caster_brake_pivot")
        ctx.check(
            "category_anchor: caster step brake pivots on the yoke",
            brake.articulation_type == ArticulationType.REVOLUTE
            and brake.parent == "caster_yoke"
            and brake.child == "brake_pedal"
            and abs(brake.axis[1] + 1.0) < 1e-6
            and brake.motion_limits is not None
            and abs(brake.motion_limits.upper - r.brake_travel_rad) < 1e-9,
            details=f"brake={(brake.parent, brake.child, brake.axis, brake.motion_limits)!r}",
        )

    if r.lid == "hinged_lid":
        hinge = object_model.get_articulation("lid_hinge")
        ctx.check(
            "category_anchor: hinged lid turns on the rear rim hinge",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and hinge.parent == "cargo_shell"
            and hinge.child == "lid"
            and abs(hinge.axis[1] + 1.0) < 1e-6
            and abs(hinge.origin.xyz[0] - (r.lid_hinge_x - r.mount_datum[0])) < 1e-6
            and abs(hinge.origin.xyz[2] - (r.lid_hinge_z - r.mount_datum[2])) < 1e-6,
            details=f"lid_hinge={(hinge.parent, hinge.child, hinge.axis, hinge.origin.xyz)!r}",
        )
        # The lid plan must be the shell's own rim outline, not a rectangle:
        # every rim vertex forward of the hinge line has to sit inside the lid
        # panel with a near-uniform moulded overhang.  A rectangular slab would
        # blow the upper bound open at the obround stadium ends and the V nose.
        rim_points = r.outline(1.0, FLANGE_OUT)
        panel_plan = r.lid_plan(LID_OVERHANG)
        gaps = []
        escaped = 0
        for point in rim_points:
            if point[0] < r.lid_rear_cut_x + 0.030:
                continue
            if not _point_in_outline(panel_plan, point):
                escaped += 1
                continue
            gaps.append(_outline_edge_distance(panel_plan, point))
        ctx.check(
            "hinged lid panel follows the moulded rim outline",
            escaped == 0
            and len(gaps) >= 4
            and min(gaps) >= 0.5 * LID_OVERHANG
            and max(gaps) <= 2.2 * LID_OVERHANG,
            details=(
                f"shell_form={r.shell_form}, escaped={escaped}, samples={len(gaps)}, "
                f"overhang_min={min(gaps) if gaps else None}, "
                f"overhang_max={max(gaps) if gaps else None}, nominal={LID_OVERHANG}"
            ),
        )

        # Connectivity: the moving lid must stay ONE fused island.  The rejected
        # v1 fork (rec_tilt_truck1_var_hinged_lid model.py:L123-L186) floated its
        # knuckle 19 mm clear of the panel; v2 (model.py:L80-L181) fuses panel,
        # skirt and knuckle with real webs and asserts a single solid.
        panel_under = r.rim_z - SHELL_BITE - r.lid_hinge_z
        knuckle_web_x = min(_LID_WEB_FRONT_X, _LID_KNUCKLE_R) - max(
            _LID_WEB_REAR_X, -_LID_KNUCKLE_R
        )
        knuckle_web_z = min(_LID_WEB_TOP_Z, _LID_KNUCKLE_R) - max(
            panel_under, -_LID_KNUCKLE_R
        )
        web_panel_x = _LID_WEB_FRONT_X - LID_PANEL_SETBACK
        web_panel_z = min(_LID_WEB_TOP_Z, panel_under + LID_PANEL_T) - panel_under
        skirt_inset = LID_OVERHANG - LID_RIM_CLEAR - LID_SKIRT_T
        ctx.check(
            "hinged lid knuckle, webs, panel and skirt are one fused island",
            knuckle_web_x >= 0.008
            and knuckle_web_z >= 0.008
            and web_panel_x >= 0.010
            and web_panel_z >= 0.010
            and _LID_WEB_HALF_Y > 0.0
            and LID_SKIRT_BITE >= 0.002
            and skirt_inset >= 0.002,
            details=(
                f"knuckle_web=({knuckle_web_x:.4f}, {knuckle_web_z:.4f}), "
                f"web_panel=({web_panel_x:.4f}, {web_panel_z:.4f}), "
                f"skirt_bite={LID_SKIRT_BITE:.4f}, skirt_inset={skirt_inset:.4f}"
            ),
        )

        # The downturned skirt lip must seat outboard of the rim edge with a real
        # running clearance, and must clear the rib crest in Z.
        ctx.check(
            "hinged lid skirt lip seats outboard of the rim with running clearance",
            LID_RIM_CLEAR >= 0.004
            and r.rim_z - SHELL_BITE - LID_SKIRT_DROP > _rib_band(r)[1] + 0.010,
            details=(
                f"rim_clear={LID_RIM_CLEAR}, skirt_bottom_z="
                f"{r.rim_z - SHELL_BITE - LID_SKIRT_DROP:.4f}, "
                f"rib_top_z={_rib_band(r)[1]:.4f}"
            ),
        )

        lid = object_model.get_part("lid")
        closed = ctx.part_world_aabb(lid)
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            opened = ctx.part_world_aabb(lid)
        ctx.check(
            "hinged lid swings up and clear of the rim",
            closed is not None
            and opened is not None
            and opened[1][2] > closed[1][2] + 0.25
            and opened[0][0] >= closed[0][0] - 0.030,
            details=f"closed={closed}, opened={opened}",
        )

    if r.handle == "folding_u_frame":
        fold = object_model.get_articulation("push_handle_fold")
        handle_part = object_model.get_part("push_handle")
        ctx.check(
            "category_anchor: push handle folds on the rear flange hinge",
            fold.articulation_type == ArticulationType.REVOLUTE
            and fold.parent == "cargo_shell"
            and fold.child == "push_handle"
            and abs(fold.axis[1] + 1.0) < 1e-6,
            details=f"fold={(fold.parent, fold.child, fold.axis)!r}",
        )
        upright = ctx.part_world_aabb(handle_part)
        with ctx.pose({fold: fold.motion_limits.upper}):
            folded = ctx.part_world_aabb(handle_part)
        ctx.check(
            "folding handle lays back behind the rear flange",
            upright is not None
            and folded is not None
            and folded[1][2] < upright[1][2] - 0.05
            and folded[0][0] < upright[0][0] - 0.02,
            details=f"upright={upright}, folded={folded}",
        )

    # ---- Identity geometry -------------------------------------------------
    ctx.check(
        "every seed is a rolling three-wheel truck",
        len(movable) >= 3
        and {"chassis", "cargo_shell", "rear_wheel_0", "rear_wheel_1", "front_wheel"}
        <= set(parts),
        details=f"movable={[j.name for j in movable]}, parts={sorted(parts)}",
    )
    roots = object_model.root_parts()
    ctx.check(
        "single chassis-rooted hierarchy",
        len(roots) == 1 and roots[0].name == "chassis",
        details=f"roots={[part.name for part in roots]}",
    )
    ctx.check(
        "shell candidate emits its own moulded hopper",
        any(
            visual.name == f"shell_form__{r.shell_form}__hopper"
            for visual in parts["cargo_shell"].visuals
        ),
        details=f"shell visuals={[v.name for v in parts['cargo_shell'].visuals][:6]}",
    )
    ctx.check(
        "underframe candidate emits its own skeleton members",
        any(
            visual.name.startswith(f"underframe__{r.underframe}__")
            for visual in parts["chassis"].visuals
        ),
        details=f"chassis visuals={[v.name for v in parts['chassis'].visuals][:8]}",
    )

    # ---- Host adaptation: the rolling base follows the moulded plan --------
    ctx.check(
        "rear wheels clear the widest moulded section over their footprint",
        r.rear_wheel_y - 0.5 * r.rear_wheel_width >= r.rear_clear_y + 0.010
        and r.bearing_face_y < r.rear_wheel_y - 0.5 * r.rear_wheel_width,
        details=(
            f"rear_clear_y={r.rear_clear_y:.4f}, wheel_inner="
            f"{r.rear_wheel_y - 0.5 * r.rear_wheel_width:.4f}, "
            f"bearing_face_y={r.bearing_face_y:.4f}"
        ),
    )
    ctx.check(
        "moulded hopper is seated on the chassis deck with a real bite",
        abs(r.floor_z - (r.deck_z - SHELL_BITE)) < 1e-9 and r.floor_z > 0.10,
        details=f"floor_z={r.floor_z:.4f}, deck_z={r.deck_z:.4f}",
    )
    ctx.check(
        "discharge nose stays forward-and-down of the tall rear wall",
        r.plan_x_hi(0.0) < r.plan_x_hi(1.0) - 0.20
        and r.plan_x_lo(0.0) > r.plan_x_lo(1.0)
        and r.plan_y_half(0.0) < r.plan_y_half(1.0),
        details=(
            f"x_hi floor={r.plan_x_hi(0.0):.4f} rim={r.plan_x_hi(1.0):.4f}, "
            f"y_half floor={r.plan_y_half(0.0):.4f} rim={r.plan_y_half(1.0):.4f}"
        ),
    )
    ctx.check(
        "front support hangs below the deck and above the ground",
        0.02 < r.swivel_z < r.deck_z and 2.0 * r.front_wheel_radius < r.swivel_z - 0.008,
        details=(
            f"swivel_z={r.swivel_z:.4f}, deck_z={r.deck_z:.4f}, "
            f"front_wheel_radius={r.front_wheel_radius:.4f}"
        ),
    )

    for name in ("rear_wheel_0", "rear_wheel_1", "front_wheel"):
        aabb = ctx.part_world_aabb(object_model.get_part(name))
        ctx.check(
            f"{name} rests on the ground plane",
            aabb is not None and abs(aabb[0][2]) < 0.010,
            details=f"aabb_min={None if aabb is None else aabb[0]}",
        )

    if r.front_support == "swivel_caster_brake":
        shoe_x, shoe_z = _brake_shoe_local(r)
        px, _py, pz = _brake_pivot_local(r)
        wheel_x = -r.caster_trail - px
        wheel_z = -(r.swivel_z - r.front_wheel_radius) - pz
        applied = r.brake_travel_rad
        cos_a, sin_a = math.cos(applied), math.sin(applied)
        rot_x = shoe_x * cos_a - shoe_z * sin_a
        rot_z = shoe_x * sin_a + shoe_z * cos_a
        gap = math.hypot(rot_x - wheel_x, rot_z - wheel_z) - r.front_wheel_radius
        ctx.check(
            "brake shoe closes on the tyre without touching it",
            0.004 < gap < 0.030,
            details=f"applied_gap={gap:.5f}",
        )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ===========================================================================
# High-risk cross-slot corners
# ===========================================================================
TEMPLATE_CORNERS = (
    corner_case(
        "vnose_brake_lid_max_ribs",
        {
            "shell_form": "v_nose",
            "underframe": "tube_perimeter",
            "front_support": "swivel_caster_brake",
            "handle": "folding_u_frame",
            "lid": "hinged_lid",
            "rear_wheel": "spoked_rim",
            "rib": "draft_panel",
            "rib_count": 5,
            "tub_length_m": 1.05,
            "tub_width_m": 0.95,
            "tub_height_m": 0.78,
            "wall_draft_ratio": 0.55,
            "nose_run_ratio": 0.58,
            "rear_wheel_radius_m": 0.200,
            "front_wheel_ratio": 0.44,
            "rib_relief_m": 0.024,
            "handle_rise_m": 0.42,
            "lid_open_rad": 1.52,
            "handle_fold_rad": 1.55,
            "brake_travel_rad": 0.40,
        },
        reason="shortest widest V-nose hopper with the longest discharge run, the biggest wheels, a full-travel brake, a folding handle and a hinged lid all at once",
    ),
    corner_case(
        "obround_fork_pockets_min_shell",
        {
            "shell_form": "obround",
            "underframe": "fork_pockets",
            "front_support": "rigid_fork",
            "handle": "molded_grips",
            "lid": "open_top",
            "rear_wheel": "disc_rim",
            "rib": "raised_rail",
            "rib_count": 2,
            "tub_length_m": 1.05,
            "tub_width_m": 0.62,
            "tub_height_m": 0.44,
            "wall_draft_ratio": 0.86,
            "nose_run_ratio": 0.28,
            "rear_wheel_radius_m": 0.115,
            "front_wheel_ratio": 0.28,
            "rib_relief_m": 0.010,
            "handle_rise_m": 0.17,
            "lid_open_rad": 1.20,
            "handle_fold_rad": 1.05,
            "brake_travel_rad": 0.22,
        },
        reason="smallest stadium hopper on the tightest fork-pocket tunnels with the smallest wheels: minimum host capacity everywhere",
    ),
    corner_case(
        "octagon_perimeter_lid_wide",
        {
            "shell_form": "chamfered_octagon",
            "underframe": "tube_perimeter",
            "front_support": "swivel_caster",
            "handle": "u_frame_fixed",
            "lid": "hinged_lid",
            "rear_wheel": "disc_rim",
            "rib": "draft_panel",
            "rib_count": 4,
            "tub_length_m": 1.60,
            "tub_width_m": 0.95,
            "tub_height_m": 0.78,
            "wall_draft_ratio": 0.55,
            "nose_run_ratio": 0.28,
            "rear_wheel_radius_m": 0.200,
            "front_wheel_ratio": 0.28,
            "rib_relief_m": 0.024,
            "handle_rise_m": 0.42,
            "lid_open_rad": 1.52,
            "handle_fold_rad": 1.30,
            "brake_travel_rad": 0.32,
        },
        reason="largest chamfered hopper: the perimeter bumper ring and the longest lid must both follow the octagonal plan",
    ),
    corner_case(
        "rect_rail_cradle_folding_over_lid",
        {
            "shell_form": "tapered_rect",
            "underframe": "rail_cradle",
            "front_support": "swivel_caster_brake",
            "handle": "folding_u_frame",
            "lid": "hinged_lid",
            "rear_wheel": "spoked_rim",
            "rib": "raised_rail",
            "rib_count": 5,
            "tub_length_m": 1.60,
            "tub_width_m": 0.62,
            "tub_height_m": 0.44,
            "wall_draft_ratio": 0.86,
            "nose_run_ratio": 0.58,
            "rear_wheel_radius_m": 0.115,
            "front_wheel_ratio": 0.44,
            "rib_relief_m": 0.010,
            "handle_rise_m": 0.42,
            "lid_open_rad": 1.52,
            "handle_fold_rad": 1.55,
            "brake_travel_rad": 0.40,
        },
        reason="narrow long hopper where the folded handle and the fully opened lid share the rear flange datum with the smallest wheels",
    ),
    corner_case(
        "vnose_rigid_fork_min_nose",
        {
            "shell_form": "v_nose",
            "underframe": "rail_cradle",
            "front_support": "rigid_fork",
            "handle": "twin_grab_bars",
            "lid": "open_top",
            "rear_wheel": "spoked_rim",
            "rib": "draft_panel",
            "rib_count": 2,
            "tub_length_m": 1.60,
            "tub_width_m": 0.95,
            "tub_height_m": 0.44,
            "wall_draft_ratio": 0.86,
            "nose_run_ratio": 0.28,
            "rear_wheel_radius_m": 0.200,
            "front_wheel_ratio": 0.44,
            "rib_relief_m": 0.024,
            "handle_rise_m": 0.17,
            "lid_open_rad": 1.20,
            "handle_fold_rad": 1.05,
            "brake_travel_rad": 0.22,
        },
        reason="shallowest widest V-nose shell on a rigid fork: the deep-relief ribs must still seat on a strongly converging plan",
    ),
)

__all__ += [
    "TEMPLATE_CORNERS",
    "ShellForm",
    "Underframe",
    "FrontSupport",
    "HandleStyle",
    "LidStyle",
    "RearWheelStyle",
    "RibStyle",
    "PaletteStyle",
    "build_urban_environment_tilt_truck1",
    "build_seeded_urban_environment_tilt_truck1",
    "run_urban_environment_tilt_truck1_tests",
]
