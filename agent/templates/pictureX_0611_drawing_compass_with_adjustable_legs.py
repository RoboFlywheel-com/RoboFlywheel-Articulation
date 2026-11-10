# SPDX-License-Identifier: Apache-2.0

"""Self-contained 'drawing_compass_with_adjustable_legs' template.

Rebuilt from the four ``pictureX/0611/drawing_compass_with_adjustable_legs``
origin records and the eleven accepted forks listed in
``articraft_template_authoring/source_maps/pictureX_0611_drawing_compass_with_adjustable_legs.md``.

Category identity: one head / hinge hub carrying exactly two legs on a shared
transverse pivot, a radius adjuster, a centre point on one leg, a lead or pen
holder on the other, and a top handle.  Six independent structural axes:

* ``head_style``       — horseshoe ring, solid disk hub, fabricated plate yoke,
  sprung bow arch, or a cheeked horseshoe.
* ``leg_style``        — tapered sheet blade, layered plate profile, hollow
  tube, or a two-section leg with a real knee joint.
* ``adjuster_style``   — cross screw, centred spindle, side link + wheel, head
  wheel, bow spreader, rack and pinion, ratchet quadrant, or quick-set wheel.
* ``lead_end_style``   — fused collet, hinged holder, prismatic extension rail,
  hinged pen adapter, or a rotating collet.
* ``needle_end_style`` — fused needle, or a prismatic cartridge in a collet
  with a knurled release sleeve.
* ``handle_style``     — spinning grip, bounded knurled handle, or a moulded
  fixed cap.

Alongside those, two decorative axes that contribute to NEITHER the core nor
the raw domain: ``finish`` (four source finish families) and ``head_tone``
(whether the head shares the leg tone or contrasts with it).  See the finish
table below for their provenance.

Solids are built as real CAD, not as stacks of primitives: extruded front-view
plate profiles (``ExtrudeGeometry``) for the legs, heads, spines and holders,
revolved half-sections (``LatheGeometry``) for the collets, grips, tips and
threads, ``KnobGeometry`` + ``KnobGrip`` for every knurled control, and a real
involute ``SpurGear`` for the rack-and-pinion.  This is the construction every
source record uses.  Approximating them with stepped boxes, rotated-box arcs
and rim-mounted rib cylinders — which is what this file used to do — put a
visible staircase down every leg, a scalloped polygon on every ring, and a
starburst of half-buried spikes on every thumbwheel.

Coordinate frame: the head pivot is the world origin.  +Z is up, the hinge axis
is +Y (the plate thickness direction), and the legs hang into -Z splayed in ±X.
Every candidate consumes only the small interface its host exposes (the pivot
axis for the legs, a station frame on each leg for the adjuster and the tip
hardware, the head crown for the handle), so all 5 x 4 x 8 x 5 x 2 x 3 = 4800
combinations build without a compatibility gate.

This file is the only runtime truth.  It imports the stdlib and the Articraft
``sdk`` only.
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
    ConeGeometry,
    Cylinder,
    ExtrudeGeometry,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MotionLimits,
    MotionProperties,
    Origin,
    PlaneInterface,
    Sphere,
    SpurGear,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_cadquery,
    mesh_from_geometry,
    register_interface_mate,
)

HeadStyle = Literal[
    "horseshoe_ring",
    "disk_hub",
    "plate_yoke",
    "spring_bow",
    "cheeked_horseshoe",
]
LegStyle = Literal["sheet_taper", "plate_profile", "tubular", "folding_knee"]
AdjusterStyle = Literal[
    "cross_screw",
    "center_spindle",
    "side_link_wheel",
    "head_wheel",
    "bow_spreader",
    "rack_pinion",
    "ratchet_quadrant",
    "center_wheel",
]
LeadEndStyle = Literal[
    "fixed_collet",
    "hinged_holder",
    "extension_rail",
    "pen_adapter",
    "rotating_collet",
]
NeedleEndStyle = Literal["fixed_needle", "collet_cartridge"]
HandleStyle = Literal["spin_grip", "knurled_handle", "fixed_cap"]

HEAD_STYLES: tuple[HeadStyle, ...] = (
    "horseshoe_ring",
    "disk_hub",
    "plate_yoke",
    "spring_bow",
    "cheeked_horseshoe",
)
LEG_STYLES: tuple[LegStyle, ...] = (
    "sheet_taper",
    "plate_profile",
    "tubular",
    "folding_knee",
)
ADJUSTER_STYLES: tuple[AdjusterStyle, ...] = (
    "cross_screw",
    "center_spindle",
    "side_link_wheel",
    "head_wheel",
    "bow_spreader",
    "rack_pinion",
    "ratchet_quadrant",
    "center_wheel",
)
LEAD_END_STYLES: tuple[LeadEndStyle, ...] = (
    "fixed_collet",
    "hinged_holder",
    "extension_rail",
    "pen_adapter",
    "rotating_collet",
)
NEEDLE_END_STYLES: tuple[NeedleEndStyle, ...] = ("fixed_needle", "collet_cartridge")
HANDLE_STYLES: tuple[HandleStyle, ...] = ("spin_grip", "knurled_handle", "fixed_cap")

# --------------------------------------------------------------------------- #
# Finish families
#
# Palette is decoration: it contributes to neither the core nor the raw domain
# (VISUAL_DIVERSITY_MODEL §"palette"), so it is NOT a component slot.  It is
# drawn from the seed alongside the continuous parameters.
#
# Each family is one source record's own material block, read off
# ``model.material(...)`` in the cited revision.  The pool really does hold four
# distinct instrument finishes and the template used to collapse all four into a
# single near-white alloy:
#
#   bright_steel  001 / center_point_collet / side_spindle_adjuster
#                 satin .72/.74/.75, bright .88/.89/.89, dark .30, graphite .12
#   satin_alloy   002 / quick_set_center_wheel / tubular_legs / rack_pinion_head
#                 satin .88/.90/.89, polished .72/.74/.73, dark .12, grip .045
#   warm_steel    003 / folding_lower_legs / lead_cartridge / ratchet_quadrant
#                 satin .72/.73/.70, polished .88/.89/.86, dark .18/.20/.20
#   matte_black   004 / extension_bar_radius / hinged_pen_adapter
#                 matte .025/.028/.032, gloss .075, gunmetal .18/.20/.22,
#                 polished .76/.78/.80
#
# One deliberate departure from the literal source numbers: the shared gallery
# light rig runs ``view_transform: Standard`` with no tonemap, so a broad face at
# albedo >= 0.6 turned toward the key clips to flat white.  The source records
# are rendered one at a time in the viewer, where that never bites.  Each family
# therefore keeps its source HUE and its source ordering (which tone is
# structure, which is the polished accent) but seats the large-area ``body``
# tone in a readable band and spends the source's brightest value on the small
# machined accents, which is also how the sources themselves use it: 001 puts
# ``satin_steel`` on the legs and ``bright_steel`` only on hardware.
FinishStyle = Literal["bright_steel", "satin_alloy", "warm_steel", "matte_black"]

FINISH_STYLES: tuple[FinishStyle, ...] = (
    "bright_steel",
    "satin_alloy",
    "warm_steel",
    "matte_black",
)

# role -> rgb.  Roles are consumed through the ``mats`` dict every builder takes.
_FINISH_TABLE: dict[FinishStyle, dict[str, tuple[float, float, float]]] = {
    # The four families are ordered by their SOURCE body brightness — 002 (.88)
    # > 001 (.72) ~ 003 (.72, warm) > 004 (.025) — and separated by hue as well
    # as by value, so no two read alike even in a grey render.
    #
    # Cool neutral steel, the 001 family.  The workhorse mid tone.
    "bright_steel": {
        "body": (0.322, 0.338, 0.350),
        "body_dark": (0.196, 0.206, 0.214),
        "bright": (0.560, 0.576, 0.588),
        "steel": (0.165, 0.172, 0.176),
        "grip": (0.098, 0.102, 0.104),
        "needle": (0.505, 0.520, 0.532),
        "lead": (0.120, 0.120, 0.120),
    },
    # 002's light, faintly green alloy — the brightest family, and the one whose
    # whole identity is that it is bright.  Measured against this rig: a large
    # face at 0.50 comes back flat white and at 0.42 it still carries its
    # shading, so 0.42 is the ceiling, not the source's own 0.88.
    "satin_alloy": {
        "body": (0.412, 0.428, 0.418),
        "body_dark": (0.248, 0.258, 0.252),
        "bright": (0.588, 0.604, 0.592),
        "steel": (0.120, 0.130, 0.130),
        "grip": (0.045, 0.050, 0.050),
        "needle": (0.545, 0.560, 0.550),
        "lead": (0.100, 0.100, 0.095),
    },
    # 003's satin is measurably warm (.72/.73/.70 against 001's .72/.74/.75);
    # that warmth is amplified into a bronzed gunmetal so the family is
    # separable from ``bright_steel`` by hue as well as by value.
    "warm_steel": {
        "body": (0.262, 0.244, 0.202),
        "body_dark": (0.152, 0.141, 0.114),
        "bright": (0.512, 0.492, 0.424),
        "steel": (0.150, 0.146, 0.128),
        "grip": (0.108, 0.100, 0.086),
        "needle": (0.478, 0.464, 0.422),
        "lead": (0.100, 0.100, 0.090),
    },
    # 004's black instrument: a matte anodised body over polished hardware.
    "matte_black": {
        "body": (0.048, 0.052, 0.058),
        "body_dark": (0.026, 0.029, 0.033),
        "bright": (0.640, 0.658, 0.672),
        "steel": (0.180, 0.200, 0.220),
        "grip": (0.075, 0.080, 0.088),
        "needle": (0.500, 0.515, 0.528),
        "lead": (0.100, 0.100, 0.110),
    },
}

# Real compass sets are commonly two-tone — origin 004 is a matte-black head
# yoke and handle over polished steel hardware.  ``head_tone`` decides whether
# the head frame shares the leg tone or drops to the family's darker structural
# tone, which is the difference between a one-piece look and that two-tone one.
HeadTone = Literal["matched", "contrast"]
HEAD_TONES: tuple[HeadTone, ...] = ("matched", "contrast")

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("head_style", HEAD_STYLES),
        component_slot("leg_style", LEG_STYLES),
        component_slot("adjuster_style", ADJUSTER_STYLES),
        component_slot("lead_end_style", LEAD_END_STYLES),
        component_slot("needle_end_style", NEEDLE_END_STYLES),
        component_slot("handle_style", HANDLE_STYLES),
    )
)

# Independent continuous parameters (honest dimensions; not core/raw domain).
_LEG_LENGTH_RANGE = (0.100, 0.190)
_OPEN_ANGLE_RANGE = (0.14, 0.40)
_HEAD_SCALE_RANGE = (0.85, 1.30)
_LEG_THICKNESS_RANGE = (0.0024, 0.0060)
_STATION_RATIO_RANGE = (0.20, 0.45)

# Fixed instrument hardware sizes (metres) shared by every candidate.
_HINGE_EYE_R = 0.0062
_HINGE_PIN_R = 0.0026
_KNEE_RATIO = 0.55
_SHAFT_R = 0.0011
_WALL = 0.0012  # thin cross-leg hardware keeps any interference shallow
_CLEAR = 0.0012  # nominal running clearance
_FRONT_GAP = 0.0035  # the shared front hardware plane stands this far off a leg face
_WELD = 0.0004  # every fused feature keeps at least this much real overlap
_LEG_TOP_HALF_W = 0.0072
_LEG_TIP_HALF_W = 0.0026


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class Config:
    head_style: HeadStyle = "horseshoe_ring"
    leg_style: LegStyle = "sheet_taper"
    adjuster_style: AdjusterStyle = "cross_screw"
    lead_end_style: LeadEndStyle = "fixed_collet"
    needle_end_style: NeedleEndStyle = "fixed_needle"
    handle_style: HandleStyle = "spin_grip"
    leg_length_m: float | None = None
    open_angle_rad: float | None = None
    head_scale: float | None = None
    leg_thickness_m: float | None = None
    adjuster_station_ratio: float | None = None
    finish: FinishStyle | None = None
    head_tone: HeadTone | None = None
    name: str = "pictureX_0611_drawing_compass_with_adjustable_legs"


@dataclass(frozen=True)
class ResolvedConfig:
    head_style: HeadStyle
    leg_style: LegStyle
    adjuster_style: AdjusterStyle
    lead_end_style: LeadEndStyle
    needle_end_style: NeedleEndStyle
    handle_style: HandleStyle
    leg_length_m: float
    open_angle_rad: float
    head_scale: float
    leg_thickness_m: float
    adjuster_station_ratio: float
    finish: FinishStyle
    head_tone: HeadTone
    hub_radius_m: float
    crown_z_m: float
    leg_offset_y_m: float
    station_m: float
    knee_m: float
    tip_span_m: float
    open_travel_rad: float
    close_travel_rad: float
    name: str


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(seed ^ 0x0C0FA55)
    return Config(
        head_style=choices["head_style"],
        leg_style=choices["leg_style"],
        adjuster_style=choices["adjuster_style"],
        lead_end_style=choices["lead_end_style"],
        needle_end_style=choices["needle_end_style"],
        handle_style=choices["handle_style"],
        leg_length_m=round(rng.uniform(*_LEG_LENGTH_RANGE), 5),
        open_angle_rad=round(rng.uniform(*_OPEN_ANGLE_RANGE), 5),
        head_scale=round(rng.uniform(*_HEAD_SCALE_RANGE), 5),
        leg_thickness_m=round(rng.uniform(*_LEG_THICKNESS_RANGE), 5),
        adjuster_station_ratio=round(rng.uniform(*_STATION_RATIO_RANGE), 5),
        # Decoration only — drawn from its own stream so adding it does not
        # shift the continuous parameters any cached seed already resolved.
        finish=FINISH_STYLES[random.Random(seed ^ 0x5F1235).randrange(len(FINISH_STYLES))],
        head_tone=HEAD_TONES[random.Random(seed ^ 0x70E11).randrange(len(HEAD_TONES))],
    )


def _range_check(name: str, value: float, bounds: tuple[float, float]) -> None:
    low, high = bounds
    if not low <= value <= high:
        raise ValueError(f"{name} must be in [{low}, {high}], got {value}")


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "head_style": config.head_style,
            "leg_style": config.leg_style,
            "adjuster_style": config.adjuster_style,
            "lead_end_style": config.lead_end_style,
            "needle_end_style": config.needle_end_style,
            "handle_style": config.handle_style,
        }
    )
    leg_length = 0.148 if config.leg_length_m is None else float(config.leg_length_m)
    open_angle = 0.240 if config.open_angle_rad is None else float(config.open_angle_rad)
    head_scale = 1.0 if config.head_scale is None else float(config.head_scale)
    thickness = 0.0034 if config.leg_thickness_m is None else float(config.leg_thickness_m)
    station_ratio = (
        0.300 if config.adjuster_station_ratio is None else float(config.adjuster_station_ratio)
    )
    _range_check("leg_length_m", leg_length, _LEG_LENGTH_RANGE)
    _range_check("open_angle_rad", open_angle, _OPEN_ANGLE_RANGE)
    _range_check("head_scale", head_scale, _HEAD_SCALE_RANGE)
    _range_check("leg_thickness_m", thickness, _LEG_THICKNESS_RANGE)
    _range_check("adjuster_station_ratio", station_ratio, _STATION_RATIO_RANGE)
    finish = config.finish or "bright_steel"
    if finish not in _FINISH_TABLE:
        raise ValueError(f"finish must be one of {FINISH_STYLES}, got {finish!r}")
    head_tone = config.head_tone or "matched"
    if head_tone not in HEAD_TONES:
        raise ValueError(f"head_tone must be one of {HEAD_TONES}, got {head_tone!r}")

    hub_radius = 0.0135 * head_scale
    crown_z = hub_radius + 0.0060 * head_scale
    # The two leg plates sit side by side on the shared pin, so a thicker leg
    # pushes the whole hinge stack wider and every mount plane with it.
    offset_y = thickness / 2.0 + 0.0005
    station = leg_length * station_ratio
    knee = leg_length * _KNEE_RATIO
    tip_span = 2.0 * leg_length * math.sin(open_angle)
    # Opening travel is limited by the span the adjuster can still bridge;
    # closing travel stops before the legs stack exactly on top of each other.
    open_travel = _clamp(0.52 - open_angle, 0.10, 0.28)
    close_travel = _clamp(open_angle - 0.06, 0.06, 0.20)
    return ResolvedConfig(
        head_style=config.head_style,
        leg_style=config.leg_style,
        adjuster_style=config.adjuster_style,
        lead_end_style=config.lead_end_style,
        needle_end_style=config.needle_end_style,
        handle_style=config.handle_style,
        leg_length_m=leg_length,
        open_angle_rad=open_angle,
        head_scale=head_scale,
        leg_thickness_m=thickness,
        adjuster_station_ratio=station_ratio,
        finish=finish,
        head_tone=head_tone,
        hub_radius_m=hub_radius,
        crown_z_m=crown_z,
        leg_offset_y_m=offset_y,
        station_m=station,
        knee_m=knee,
        tip_span_m=tip_span,
        open_travel_rad=open_travel,
        close_travel_rad=close_travel,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("head_style", config.head_style),
        ("leg_style", config.leg_style),
        ("adjuster_style", config.adjuster_style),
        ("lead_end_style", config.lead_end_style),
        ("needle_end_style", config.needle_end_style),
        ("handle_style", config.handle_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Materials and primitive helpers
# --------------------------------------------------------------------------- #
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    """Register the seed's finish family and return the role -> material map.

    Seven roles, not the five this template used to carry.  The old map sent
    every structural surface — head frame, both legs, holders, spines, blades —
    to one high-albedo alloy, so the whole instrument rendered as a single white
    silhouette with no readable form.  Splitting structure into ``body`` and
    ``body_dark`` and pulling the needle out of ``steel`` is what makes the
    hinge stack, the tips and the controls legible against the legs.
    """
    table = _FINISH_TABLE[r.finish]
    for role, rgb in table.items():
        model.material(f"{r.finish}__{role}", rgba=(rgb[0], rgb[1], rgb[2], 1.0))
    mats = {role: f"{r.finish}__{role}" for role in table}
    # The head either shares the leg tone or drops to the darker structural tone
    # (origin 004's black yoke over bright hardware).
    mats["head"] = mats["body_dark"] if r.head_tone == "contrast" else mats["body"]
    return mats


def _box(part, size, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part, radius, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _ball(part, radius, xyz, material: str, name: str) -> None:
    part.visual(Sphere(radius=radius), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="metal.blackened_gunmetal")


_Y_AXIS_RPY = (math.pi / 2.0, 0.0, 0.0)
_X_AXIS_RPY = (0.0, math.pi / 2.0, 0.0)


def _mesh(part, geometry, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    """Emit one meshed visual.  Mesh keys are namespaced by the owning part.

    ``mesh_from_geometry`` registers the OBJ text under the logical name it is
    given, so two structurally different solids must never share one.  Part
    names are unique inside a model, which makes ``<part>__<local>`` safe.
    """
    part.visual(
        mesh_from_geometry(geometry, f"{part.name}__{name}"),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _plate(part, profile, thickness: float, xyz, material: str, name: str, rpy) -> None:
    """One extruded front-view X/Z plate, the construction origin ``004`` uses.

    ``ExtrudeGeometry`` builds along local +Z, so the caller's ``rpy`` turns the
    extrusion into the instrument's Y (thickness) direction.
    """
    _mesh(part, ExtrudeGeometry(profile, thickness, center=True), xyz, material, name, rpy=rpy)


# Extrusions authored as a front-view (x, z) profile are turned into the
# instrument's Y thickness direction by the same rotation the cylinders use.
_PLATE_RPY = _Y_AXIS_RPY


def _threaded_rod(
    part, core_r, crest_r, length, xyz, material: str, name: str, rpy=(0.0, 0.0, 0.0)
) -> None:
    """A screw shank whose thread is one revolved sawtooth, not a disc stack.

    Every adjuster screw here used to carry eight or nine separate 0.6 mm discs
    threaded onto its shank at a fixed pitch.  At a 1.1 mm core radius those
    discs are the same order as the shank itself, so the screw read as a coil
    spring rather than a thread.  Revolving a single crest/root half-section
    gives a continuous thread form in one solid.

    Built from local z = 0 to z = ``length``, so ``xyz`` is the shank root.
    """
    pitch = 0.0011
    turns = max(3, int(length / pitch))
    profile: list[tuple[float, float]] = [(0.0, 0.0)]
    for index in range(turns):
        z = length * float(index) / float(turns)
        profile.append((core_r, z))
        profile.append((crest_r, z + length / float(turns) * 0.45))
    profile.append((core_r, length))
    profile.append((0.0, length))
    _mesh(part, LatheGeometry(profile, segments=24), xyz, material, name, rpy=rpy)


def _tapered_bar_profile(
    start: tuple[float, float],
    end: tuple[float, float],
    width_start: float,
    width_end: float,
) -> list[tuple[float, float]]:
    """A straight bar profile that tapers from ``width_start`` to ``width_end``.

    Copied in construction from the ratchet fork's ``_tapered_bar_xz``
    (model.py:L45-L64): offset both ends along the bar's own normal so the taper
    is a single trapezoid rather than a stack of stepped boxes.
    """
    dx = end[0] - start[0]
    dz = end[1] - start[1]
    length = math.hypot(dx, dz)
    if length <= 0.0:
        raise ValueError("a tapered bar needs a non-zero length")
    nx, nz = -dz / length, dx / length
    return [
        (start[0] + nx * width_start * 0.5, start[1] + nz * width_start * 0.5),
        (end[0] + nx * width_end * 0.5, end[1] + nz * width_end * 0.5),
        (end[0] - nx * width_end * 0.5, end[1] - nz * width_end * 0.5),
        (start[0] - nx * width_start * 0.5, start[1] - nz * width_start * 0.5),
    ]


def _annular_sector_profile(
    inner_r: float,
    outer_r: float,
    start: float,
    end: float,
    *,
    segments: int = 24,
) -> list[tuple[float, float]]:
    """An arc band profile in the (x, z) plane, angles measured from +Z.

    This is the construction the rack fork uses for its rack sector
    (``_rack_sector_body_shape``, model.py:L120-L144) and the ratchet fork for
    its quadrant (``_quadrant_arc``, model.py:L96-L134): walk the outer radius
    forward, the inner radius back, and close.  It replaces the overlapping
    rotated boxes that gave every curved feature a scalloped silhouette.
    """
    outer = []
    inner = []
    for index in range(segments):
        t = float(index) / float(segments - 1)
        angle = start + (end - start) * t
        sin_a, cos_a = math.sin(angle), math.cos(angle)
        outer.append((outer_r * sin_a, outer_r * cos_a))
        inner.append((inner_r * sin_a, inner_r * cos_a))
    return outer + list(reversed(inner))


def _knurled(part, radius, length, xyz, mats, name: str, rpy, bands: int = 10) -> None:
    """A knurled control wheel, built as one real knob solid.

    This used to be a plain cylinder ringed by ``bands`` small cylinders whose
    centres sat exactly ON the rim at radius ``0.10 * radius``, so half of every
    rib stood proud — a 7 mm thumbwheel grew eighteen 0.7 mm spikes and read as
    a starburst rather than as knurling.  Every source record instead builds its
    controls with ``KnobGeometry`` + ``KnobGrip`` and a grip depth of 0.22-0.45
    mm CUT INTO the rim (rack fork L360-L366 / L387-L393, ratchet fork
    L422-L435 / L496-L501).  One mesh visual also means one collision solid
    instead of ``1 + bands``.
    """
    # Source grip depths run 0.00022-0.00070 m and about 0.09-0.13 of the wheel
    # radius; both bounds matter, since this template's wheels span 3.8-7.2 mm.
    depth = _clamp(radius * 0.095, 0.00022, 0.00060)
    # Tall knobs are ribbed (a hand turns them), flat thumbwheels are knurled.
    if length > radius * 1.4:
        grip = KnobGrip(style="ribbed", count=max(bands, 12), depth=depth, width=radius * 0.22)
    else:
        grip = KnobGrip(
            style="knurled",
            count=max(bands, 14),
            depth=depth,
            helix_angle_deg=20.0,
        )
    _mesh(
        part,
        KnobGeometry(
            2.0 * radius,
            length,
            body_style="cylindrical",
            edge_radius=min(radius * 0.10, length * 0.22),
            grip=grip,
        ),
        xyz,
        mats["grip"],
        name,
        rpy=rpy,
    )


# --------------------------------------------------------------------------- #
# Interfaces shared by the whole instrument
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Head:
    part: object
    crown_z: float  # z of the handle seat on the head crown
    front_y: float  # y of the front hardware plane


@dataclass(frozen=True)
class _Leg:
    """One compass leg as seen by the adjuster and the tip hardware."""

    side: float  # -1.0 = needle leg, +1.0 = lead leg
    root: object  # part hinged on the head
    tip_part: object  # part that carries the tip hardware
    tip_z: float  # tip position in tip_part's own frame (always on -Z)
    station_part: object  # part that carries the adjuster station
    station_z: float  # station position in station_part's own frame
    knee_joint: str | None


def _spin_joint(
    model: ArticulatedObject,
    parent,
    child,
    *,
    name: str,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    radial: tuple[float, float, float],
    radius: float,
    joint_type: ArticulationType,
    limits: MotionLimits,
    child_radial: tuple[float, float, float] | None = None,
    meta: dict | None = None,
) -> str:
    """Solve one rotational joint from a real axis interface pair."""
    provider = AxisInterface(
        name=f"{name}__provider",
        point=point,
        axis=axis,
        radial=radial,
        radius=radius + _CLEAR,
    )
    consumer = AxisInterface(
        name=f"{name}__consumer",
        point=(0.0, 0.0, 0.0),
        axis=axis,
        radial=radial if child_radial is None else child_radial,
        radius=radius,
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        joint_type,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        motion_properties=MotionProperties(damping=0.4, friction=0.2),
        meta=meta or {},
    )
    register_interface_mate(model, name, mate)
    return name


# --------------------------------------------------------------------------- #
# head_style candidates
# --------------------------------------------------------------------------- #
def _hinge_hardware(part, r: ResolvedConfig, mats) -> None:
    """The shared transverse pin and its two caps hold both leg eyes."""
    stack = 2.0 * (r.leg_offset_y_m + r.leg_thickness_m / 2.0)
    _cyl(
        part,
        _HINGE_PIN_R,
        stack + 0.0026,
        (0.0, 0.0, 0.0),
        mats["steel"],
        "hinge_pin",
        rpy=_Y_AXIS_RPY,
    )
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            part,
            _HINGE_EYE_R * 0.72,
            0.0009,
            (0.0, sign * (stack / 2.0 + 0.0016), 0.0),
            mats["steel"],
            f"hinge_cap_{index}",
            rpy=_Y_AXIS_RPY,
        )


def _front_plane_y(r: ResolvedConfig) -> float:
    """World y of the shared front hardware plane, clear of both leg plates."""
    return -(r.leg_offset_y_m + r.leg_thickness_m / 2.0 + _FRONT_GAP)


def _crown_boss(part, mats, top_z: float) -> None:
    """A real seat the handle candidates can mate to, fused into the head."""
    _cyl(part, 0.0032, 0.0070, (0.0, 0.0, top_z - 0.0030), mats["body"], "crown_boss")


def _head_style_horseshoe_ring_build(model, r: ResolvedConfig, mats) -> _Head:
    """001 L79-L101: a hollow annular bow with an integral hinge bridge.

    The bow is one extruded arc band, the way ``_head_ring`` builds it as one
    ``circle().circle().extrude()`` annulus.  It used to be fourteen rotated
    boxes overlapping by 35% of their own tangential length, which read as a
    coarse polygon and put fourteen collision solids where one belongs.
    """
    part = model.part(
        "head_style__horseshoe_ring__head",
        meta={"role": "head", "construction": "hollow horseshoe ring"},
    )
    outer = r.hub_radius_m
    wall = outer * 0.19
    ring_r = outer - wall / 2.0
    _plate(
        part,
        _annular_sector_profile(
            ring_r - wall / 2.0,
            ring_r + wall / 2.0,
            -math.pi * 0.06,
            math.pi * 1.06,
            segments=40,
        ),
        0.0022,
        (0.0, 0.0, 0.0),
        mats["head"],
        "ring_bow",
        _PLATE_RPY,
    )
    # The hinge bridge spans the whole bore, so the ring and the pivot are one body.
    _box(
        part,
        (2.0 * ring_r + wall, 0.0026, wall),
        (0.0, 0.0, 0.0),
        mats["head"],
        "hinge_bridge",
    )
    _hinge_hardware(part, r, mats)
    top = ring_r + wall * 0.5
    _crown_boss(part, mats, top)
    return _Head(part=part, crown_z=top, front_y=_front_plane_y(r))


def _head_style_disk_hub_build(model, r: ResolvedConfig, mats) -> _Head:
    """003 L179-L197: a closed disk hub with a rectangular saddle below it."""
    part = model.part(
        "head_style__disk_hub__head",
        meta={"role": "head", "construction": "solid disk hub with saddle"},
    )
    _cyl(
        part,
        r.hub_radius_m,
        0.0026,
        (0.0, 0.0, 0.0),
        mats["head"],
        "head_hub",
        rpy=_Y_AXIS_RPY,
    )
    # The saddle narrows as it drops away from the disc, so the hub reads as a
    # turned boss on a bracket rather than a disc parked on a slab.
    _plate(
        part,
        _tapered_bar_profile(
            (0.0, -r.hub_radius_m * 0.44),
            (0.0, -r.hub_radius_m * 1.24),
            r.hub_radius_m * 1.50,
            r.hub_radius_m * 0.98,
        ),
        0.0040,
        (0.0, 0.0, 0.0),
        mats["head"],
        "head_saddle",
        _PLATE_RPY,
    )
    _hinge_hardware(part, r, mats)
    _crown_boss(part, mats, r.hub_radius_m)
    return _Head(part=part, crown_z=r.hub_radius_m, front_y=_front_plane_y(r))


def _head_style_plate_yoke_build(model, r: ResolvedConfig, mats) -> _Head:
    """004 L76-L174: a fabricated plate yoke with a front bridge and spindles.

    Origin ``004``'s head is a single extruded front-view polygon
    (``head_profile`` at model.py:L77-L90 through ``_plate_mesh``): an angular
    shouldered yoke, wide at the pivot and clipped back to a flat crown.  That
    profile is reproduced here scaled by ``hub_radius_m``, replacing three boxes
    — two splayed cheeks and a crown bar — that met at open corners.
    """
    part = model.part(
        "head_style__plate_yoke__head",
        meta={"role": "head", "construction": "fabricated plate yoke"},
    )
    top = r.hub_radius_m * 1.26
    # Source polygon normalised against its own 0.025 m half-width so the
    # template's hub radius drives it.  Read anticlockwise from the lower left.
    unit_profile = (
        (-1.00, -0.48),
        (-0.80, 0.40),
        (-0.42, 0.86),
        (0.00, 0.98),
        (0.42, 0.86),
        (0.80, 0.40),
        (1.00, -0.48),
        (0.80, -0.90),
        (0.40, -1.05),
        (-0.40, -1.05),
        (-0.80, -0.90),
    )
    half_w = r.hub_radius_m * 1.05
    half_h = top / 0.98
    _plate(
        part,
        [(x * half_w, z * half_h) for x, z in unit_profile],
        0.0050,
        (0.0, 0.0, 0.0),
        mats["head"],
        "yoke_plate",
        _PLATE_RPY,
    )
    _cyl(
        part,
        r.hub_radius_m * 0.30,
        0.0140,
        (0.0, 0.0, 0.0),
        mats["bright"],
        "front_bridge",
        rpy=_Y_AXIS_RPY,
    )
    _hinge_hardware(part, r, mats)
    _crown_boss(part, mats, top)
    return _Head(part=part, crown_z=top, front_y=_front_plane_y(r))


def _head_style_spring_bow_build(model, r: ResolvedConfig, mats) -> _Head:
    """bow_spring fork L82-L130: a sprung bow arch on a tapered spine."""
    part = model.part(
        "head_style__spring_bow__head",
        meta={"role": "head", "construction": "sprung bow arch"},
    )
    half_span = r.hub_radius_m * 1.15
    apex = r.hub_radius_m * 1.55
    # One sprung arch band: walk the parabola once for the outer edge and back
    # for the inner edge, offsetting along the curve's own normal.  The old
    # construction laid ten boxes end to end at 25% tangential overlap, so the
    # arch read as a chain of facets with a step at every joint.
    band = 0.0032
    samples = 21
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for index in range(samples):
        t = -1.0 + 2.0 * float(index) / float(samples - 1)
        x, z = half_span * t, apex * (1.0 - t * t)
        # d/dt of the curve, normalised, rotated a quarter turn for the normal.
        dx, dz = half_span, -2.0 * apex * t
        norm = math.hypot(dx, dz)
        nx, nz = -dz / norm, dx / norm
        outer.append((x + nx * band * 0.5, z + nz * band * 0.5))
        inner.append((x - nx * band * 0.5, z - nz * band * 0.5))
    _plate(
        part,
        outer + list(reversed(inner)),
        0.0024,
        (0.0, 0.0, 0.0),
        mats["bright"],
        "spring_bow",
        _PLATE_RPY,
    )
    # The sprung arch is rooted in a tie bar that runs through the pivot, so the
    # bow, the spine and the hinge pin stay one connected body.
    _box(
        part,
        (2.0 * half_span + 0.0030, 0.0028, 0.0036),
        (0.0, 0.0, 0.0),
        mats["head"],
        "bow_root_tie",
    )
    # A single tapered spine from the tie bar up into the bow apex.  Its top is
    # derived from the band, not from a fraction of the apex, so it bites into
    # the arch by _WELD at every head scale instead of leaving a scale-dependent
    # gap between the spine and the thing it is supposed to hold up.
    _plate(
        part,
        _tapered_bar_profile((0.0, -_WELD), (0.0, apex - band * 0.5 + _WELD), 0.0090, 0.0062),
        0.0028,
        (0.0, 0.0, 0.0),
        mats["head"],
        "bow_spine",
        _PLATE_RPY,
    )
    _hinge_hardware(part, r, mats)
    _crown_boss(part, mats, apex)
    return _Head(part=part, crown_z=apex, front_y=_front_plane_y(r))


def _head_style_cheeked_horseshoe_build(model, r: ResolvedConfig, mats) -> _Head:
    """002 L27-L58: a horseshoe frame with a solid pivot cheek and two flared cheeks.

    The source fuses four bodies — a hollow annulus, a solid pivot disc at the
    bore centre and two triangular cheeks splaying down and out — which is a
    different silhouette from 001's plain ring and narrow bridge.
    """
    part = model.part(
        "head_style__cheeked_horseshoe__head",
        meta={"role": "head", "construction": "horseshoe frame with flared pivot cheeks"},
    )
    outer = r.hub_radius_m
    wall = outer * 0.22
    ring_r = outer - wall / 2.0
    _plate(
        part,
        _annular_sector_profile(
            ring_r - wall / 2.0,
            ring_r + wall / 2.0,
            -math.pi * 0.10,
            math.pi * 1.10,
            segments=40,
        ),
        0.0026,
        (0.0, 0.0, 0.0),
        mats["head"],
        "frame_bow",
        _PLATE_RPY,
    )
    # The solid pivot cheek fills the bore centre and reaches the ring bore wall.
    _cyl(
        part,
        ring_r - wall * 0.5 + 0.0004,
        0.0026,
        (0.0, 0.0, 0.0),
        mats["head"],
        "pivot_cheek",
        rpy=_Y_AXIS_RPY,
    )
    # Two cheeks splay up and out from the pivot disc to the ring shoulders,
    # following the source polyline's inner-to-outer run.  They are real
    # trapezoids that widen into the disc, not constant-width bars.
    for index, sign in enumerate((-1.0, 1.0)):
        x0, z0 = sign * ring_r * 0.22, -ring_r * 0.12
        x1, z1 = sign * (ring_r + wall * 0.30), ring_r * 0.44
        _plate(
            part,
            _tapered_bar_profile((x0, z0), (x1, z1), wall * 0.90, wall * 0.48),
            0.0026,
            (0.0, 0.0, 0.0),
            mats["head"],
            f"flared_cheek_{index}",
            _PLATE_RPY,
        )
    _hinge_hardware(part, r, mats)
    top = ring_r + wall * 0.5
    _crown_boss(part, mats, top)
    return _Head(part=part, crown_z=top, front_y=_front_plane_y(r))


_HEAD_BUILDERS = {
    "horseshoe_ring": _head_style_horseshoe_ring_build,
    "disk_hub": _head_style_disk_hub_build,
    "plate_yoke": _head_style_plate_yoke_build,
    "spring_bow": _head_style_spring_bow_build,
    "cheeked_horseshoe": _head_style_cheeked_horseshoe_build,
}


# --------------------------------------------------------------------------- #
# leg_style candidates
# --------------------------------------------------------------------------- #
def _leg_name(r: ResolvedConfig, side: float, local: str) -> str:
    tag = "needle" if side < 0.0 else "lead"
    return f"leg_style__{r.leg_style}__{tag}_{local}"


def _taper_half_width(frac: float) -> float:
    return _LEG_TOP_HALF_W + (_LEG_TIP_HALF_W - _LEG_TOP_HALF_W) * frac


def _add_hinge_eye(part, r: ResolvedConfig, mats) -> None:
    _cyl(
        part,
        _HINGE_EYE_R,
        r.leg_thickness_m,
        (0.0, 0.0, 0.0),
        mats["body_dark"],
        "hinge_eye",
        rpy=_Y_AXIS_RPY,
    )


def _add_blade(
    part,
    r: ResolvedConfig,
    mats,
    *,
    z0: float,
    z1: float,
    f0: float,
    f1: float,
    segments: int,
    prefix: str,
) -> None:
    """A tapered forged blade between two fractions of the full leg length.

    Origin ``001`` builds this as ONE polyline prism whose two ends carry
    different half-widths (``_leg_body``, model.py:L41-L76); the ratchet fork
    does the same through ``_tapered_bar_xz``.  This used to emit ``segments``
    stacked boxes of piecewise-constant width instead, which put a visible
    staircase down the outside of every leg — four to six steps, each a full
    ``leg_thickness`` deep, on the single largest surface in the render.

    ``segments`` is kept in the signature because callers use it to say how far
    along the taper this section runs; the solid itself no longer needs it.
    """
    del segments
    # Overhang the top end so the blade always bites into the hinge eye it hangs
    # from, and the bottom end so the tip hardware has real material to sit in.
    lead_in = _WELD * 2.0
    profile = _tapered_bar_profile(
        (0.0, z0 - math.copysign(lead_in, z1 - z0)),
        (0.0, z1),
        2.0 * _taper_half_width(f0),
        2.0 * _taper_half_width(f1),
    )
    _plate(part, profile, r.leg_thickness_m, (0.0, 0.0, 0.0), mats["body"], prefix, _PLATE_RPY)


def _hinge_leg(model, r: ResolvedConfig, head: _Head, part, side: float, name: str) -> str:
    """Hinge one leg root on the shared head pivot."""
    splay = side * r.open_angle_rad
    axis = (0.0, 1.0 if side < 0.0 else -1.0, 0.0)
    radial = (math.sin(splay), 0.0, -math.cos(splay))
    return _spin_joint(
        model,
        head.part,
        part,
        name=name,
        point=(0.0, side * r.leg_offset_y_m, 0.0),
        axis=axis,
        radial=radial,
        child_radial=(0.0, 0.0, -1.0),
        radius=_HINGE_EYE_R,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(
            effort=3.0,
            velocity=1.5,
            lower=-r.close_travel_rad,
            upper=r.open_travel_rad,
        ),
        meta={"mechanism": "compass leg hinge", "positive_motion": "opens the leg outward"},
    )


def _leg_style_sheet_taper_build(model, r, mats, head, side) -> _Leg:
    """001 L41-L76: one lofted tapered forged blade with an annular hinge eye."""
    part = model.part(
        _leg_name(r, side, "leg"),
        meta={"role": "leg", "side": "needle" if side < 0.0 else "lead"},
    )
    _add_hinge_eye(part, r, mats)
    _add_blade(
        part, r, mats, z0=0.0, z1=-r.leg_length_m, f0=0.0, f1=1.0, segments=6, prefix="blade"
    )
    _hinge_leg(model, r, head, part, side, _leg_name(r, side, "hinge"))
    return _Leg(
        side=side,
        root=part,
        tip_part=part,
        tip_z=-r.leg_length_m,
        station_part=part,
        station_z=-r.station_m,
        knee_joint=None,
    )


def _leg_style_plate_profile_build(model, r, mats, head, side) -> _Leg:
    """004 L176-L237: an extruded profile with a separate eye, inlay and rivet."""
    part = model.part(
        _leg_name(r, side, "leg"),
        meta={"role": "leg", "side": "needle" if side < 0.0 else "lead"},
    )
    _cyl(
        part,
        _HINGE_EYE_R * 1.45,
        r.leg_thickness_m,
        (0.0, 0.0, 0.0),
        mats["body"],
        "hinge_eye",
        rpy=_Y_AXIS_RPY,
    )
    _add_blade(
        part, r, mats, z0=0.0, z1=-r.leg_length_m, f0=0.0, f1=1.0, segments=5, prefix="plate"
    )
    # The face inlay and its rivet are the layered plate construction.  Origin
    # 004 lays ONE thin face plate down the leg (``needle_leg_inlay``), so this
    # follows the blade's own taper as a single strip rather than four boxes of
    # stepped width butted end to end.
    inlay_y = -side * (r.leg_thickness_m / 2.0 + 0.0004)
    _plate(
        part,
        _tapered_bar_profile(
            (0.0, -r.leg_length_m * 0.10),
            (0.0, -r.leg_length_m * 0.80),
            2.0 * _taper_half_width(0.10) * 0.52,
            2.0 * _taper_half_width(0.80) * 0.52,
        ),
        0.0012,
        (0.0, inlay_y, 0.0),
        mats["bright"],
        "face_inlay",
        _PLATE_RPY,
    )
    _cyl(
        part,
        0.0026,
        r.leg_thickness_m + 0.0022,
        (0.0, 0.0, -r.leg_length_m * 0.76),
        mats["bright"],
        "plate_rivet",
        rpy=_Y_AXIS_RPY,
    )
    _hinge_leg(model, r, head, part, side, _leg_name(r, side, "hinge"))
    return _Leg(
        side=side,
        root=part,
        tip_part=part,
        tip_z=-r.leg_length_m,
        station_part=part,
        station_z=-r.station_m,
        knee_joint=None,
    )


def _leg_style_tubular_build(model, r, mats, head, side) -> _Leg:
    """tubular fork L220-L298: a hollow tube leg with a pivot lug and tip socket."""
    part = model.part(
        _leg_name(r, side, "leg"),
        meta={"role": "leg", "side": "needle" if side < 0.0 else "lead"},
    )
    _add_hinge_eye(part, r, mats)
    _box(
        part,
        (0.0090, r.leg_thickness_m, 0.0130),
        (0.0, 0.0, -0.0060),
        mats["body"],
        "pivot_lug",
    )
    tube_r = max(r.leg_thickness_m * 0.90, 0.0022)
    # One smoothly drawn tube.  Five stacked cylinders of stepped radius left a
    # visible shoulder every fifth of the leg — the same staircase the flat legs
    # had, turned into a tube.
    z_top = -r.leg_length_m * 0.06
    z_end = -r.leg_length_m * 0.96
    run = z_top - z_end
    samples = 9
    profile: list[tuple[float, float]] = [(0.0, 0.0)]
    for index in range(samples):
        # Local z runs from the tip end up to the hinge end, so the leg fraction
        # counts DOWN across the profile: the tube is thickest at the pivot.
        t = float(index) / float(samples - 1)
        frac = 0.96 - 0.90 * t
        profile.append((tube_r * (1.0 - 0.30 * frac), run * t))
    profile.append((0.0, run))
    _mesh(part, LatheGeometry(profile, segments=28), (0.0, 0.0, z_end), mats["body"], "tube")
    _cyl(
        part,
        tube_r * 0.85,
        0.0110,
        (0.0, 0.0, -r.leg_length_m * 0.955),
        mats["bright"],
        "tip_socket",
    )
    _hinge_leg(model, r, head, part, side, _leg_name(r, side, "hinge"))
    return _Leg(
        side=side,
        root=part,
        tip_part=part,
        tip_z=-r.leg_length_m,
        station_part=part,
        station_z=-r.station_m,
        knee_joint=None,
    )


def _leg_style_folding_knee_build(model, r, mats, head, side) -> _Leg:
    """folding fork L65-L103: an upper and a lower section joined by a knee."""
    upper = model.part(
        _leg_name(r, side, "upper_leg"),
        meta={"role": "leg", "side": "needle" if side < 0.0 else "lead"},
    )
    _add_hinge_eye(upper, r, mats)
    knee_frac = _KNEE_RATIO
    _add_blade(
        upper, r, mats, z0=0.0, z1=-r.knee_m, f0=0.0, f1=knee_frac, segments=4, prefix="upper"
    )
    _cyl(
        upper,
        0.0044,
        r.leg_thickness_m + 0.0016,
        (0.0, 0.0, -r.knee_m),
        mats["bright"],
        "knee_knuckle",
        rpy=_Y_AXIS_RPY,
    )
    lower = model.part(
        _leg_name(r, side, "lower_leg"),
        meta={"role": "leg_lower", "side": "needle" if side < 0.0 else "lead"},
    )
    _cyl(
        lower,
        0.0038,
        r.leg_thickness_m,
        (0.0, 0.0, 0.0),
        mats["body"],
        "knee_eye",
        rpy=_Y_AXIS_RPY,
    )
    lower_len = r.leg_length_m - r.knee_m
    _add_blade(
        lower, r, mats, z0=0.0, z1=-lower_len, f0=knee_frac, f1=1.0, segments=4, prefix="lower"
    )
    _hinge_leg(model, r, head, upper, side, _leg_name(r, side, "hinge"))
    knee_joint = _spin_joint(
        model,
        upper,
        lower,
        name=_leg_name(r, side, "knee"),
        point=(0.0, 0.0, -r.knee_m),
        axis=(0.0, -1.0 if side < 0.0 else 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=0.0044,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=1.9),
        meta={"mechanism": "folding leg knee"},
    )
    return _Leg(
        side=side,
        root=upper,
        tip_part=lower,
        tip_z=-lower_len,
        station_part=upper,
        station_z=-r.station_m,
        knee_joint=knee_joint,
    )


_LEG_BUILDERS = {
    "sheet_taper": _leg_style_sheet_taper_build,
    "plate_profile": _leg_style_plate_profile_build,
    "tubular": _leg_style_tubular_build,
    "folding_knee": _leg_style_folding_knee_build,
}


# --------------------------------------------------------------------------- #
# adjuster_style candidates
# --------------------------------------------------------------------------- #
def _station_y(leg: _Leg, r: ResolvedConfig) -> float:
    """The shared front hardware plane expressed in one leg's own frame.

    Both legs hang off the same pivot but their local +Y points in opposite
    world directions, so the same world plane sits at a different local depth on
    each leg.  Every feature placed here is tied back to the leg face by
    ``_add_standoff``.
    """
    depth = r.leg_thickness_m / 2.0 + _FRONT_GAP
    if leg.side < 0.0:
        return -depth
    return depth + 2.0 * r.leg_offset_y_m


def _add_standoff(
    part, r: ResolvedConfig, leg: _Leg, mats, z: float, name: str, width: float = 0.0058
) -> None:
    """Fuse a boss from the leg face out to the front hardware plane."""
    target = _station_y(leg, r)
    face = math.copysign(r.leg_thickness_m / 2.0, target)
    length = abs(target - face) + 2.0 * _WELD
    center = (target + face) / 2.0
    _box(part, (width, length, width), (0.0, center, z), mats["body"], name)


def _adjuster_name(r: ResolvedConfig, local: str) -> str:
    return f"adjuster_style__{r.adjuster_style}__{local}"


def _head_spine(head: _Head, r: ResolvedConfig, mats, depth: float, tag: str) -> None:
    """Host adaptation: a head-mounted adjuster grows its own spine downward."""
    # The spine hangs on the front plane, so a web ties it back to the hub.
    _box(
        head.part,
        (0.0052, abs(head.front_y) + 0.0026, 0.0052),
        (0.0, head.front_y / 2.0, -0.0022),
        mats["bright"],
        f"{tag}_spine_web",
    )
    # One tapered spine, not four stacked boxes: a head-mounted adjuster spine
    # is the most visible thing on the front of the instrument.
    _plate(
        head.part,
        _tapered_bar_profile((0.0, _WELD), (0.0, -depth), 0.0058, 0.0042),
        0.0026,
        (0.0, head.front_y, 0.0),
        mats["bright"],
        f"{tag}_spine",
        _PLATE_RPY,
    )


def _adjuster_style_cross_screw_build(model, r, mats, head, needle, lead) -> list[str]:
    """001 L104-L145: a threaded cross screw with an end wheel and guide collar."""
    boss_y = _station_y(needle, r)
    _add_standoff(needle.station_part, r, needle, mats, needle.station_z, "anchor_standoff")
    _cyl(
        needle.station_part,
        0.0042,
        0.0028,
        (0.0, boss_y, needle.station_z),
        mats["bright"],
        "adjustment_anchor",
        rpy=_Y_AXIS_RPY,
    )
    # The opposite leg carries a thin open crescent guide, so any interference as
    # the legs swing stays inside a 1.2 mm wall.
    guide_y = _station_y(lead, r)
    _add_standoff(lead.station_part, r, lead, mats, lead.station_z, "guide_standoff")
    for index, dz in enumerate((-0.0034, 0.0034)):
        _box(
            lead.station_part,
            (0.0060, _WALL, 0.0016),
            (0.0, guide_y, lead.station_z + dz),
            mats["steel"],
            f"guide_jaw_{index}",
        )
    _box(
        lead.station_part,
        (_WALL, 0.0034, 0.0084),
        (0.0028, guide_y, lead.station_z),
        mats["steel"],
        "guide_spine",
    )

    screw = model.part(
        _adjuster_name(r, "screw"),
        meta={"role": "adjuster", "mechanism": "threaded cross screw"},
    )
    span = r.tip_span_m * 0.55 + 0.020
    _cyl(
        screw, _SHAFT_R, span, (span / 2.0, 0.0, 0.0), mats["steel"], "screw_shaft", rpy=_X_AXIS_RPY
    )
    # The threaded run between the two legs, as one continuous thread form.
    _threaded_rod(
        screw,
        _SHAFT_R,
        _SHAFT_R * 1.45,
        span * 0.62,
        (0.0055, 0.0, 0.0),
        mats["bright"],
        "screw_thread",
        rpy=_X_AXIS_RPY,
    )
    _knurled(screw, 0.0044, 0.0034, (span * 0.86, 0.0, 0.0), mats, "adjust_wheel", _X_AXIS_RPY)
    _ball(screw, 0.0020, (span, 0.0, 0.0), mats["grip"], "screw_end_ball")
    joint = _spin_joint(
        model,
        needle.station_part,
        screw,
        name=_adjuster_name(r, "spin"),
        point=(0.0, boss_y, needle.station_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=_SHAFT_R,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.8, velocity=6.0),
        meta={"mechanism": "fine-adjust cross screw"},
    )
    return [joint]


def _adjuster_style_center_spindle_build(model, r, mats, head, needle, lead) -> list[str]:
    """side_spindle fork L471-L514: a centred wheel between two hex pivot nuts."""
    for leg, tag in ((needle, "needle"), (lead, "lead")):
        nut_y = _station_y(leg, r)
        _add_standoff(leg.station_part, r, leg, mats, leg.station_z, f"nut_standoff_{tag}")
        _cyl(
            leg.station_part,
            0.0038,
            0.0026,
            (0.0, nut_y, leg.station_z),
            mats["bright"],
            f"hex_pivot_nut_{tag}",
            rpy=_X_AXIS_RPY,
        )
        for index, dz in enumerate((-0.0040, 0.0040)):
            _box(
                leg.station_part,
                (0.0056, _WALL, 0.0014),
                (0.0, nut_y, leg.station_z + dz),
                mats["steel"],
                f"nut_pocket_{tag}_{index}",
            )
    spindle = model.part(
        _adjuster_name(r, "spindle"),
        meta={"role": "adjuster", "mechanism": "centred threaded spindle"},
    )
    half = r.tip_span_m * 0.30 + 0.012
    _cyl(
        spindle,
        _SHAFT_R,
        2.0 * half,
        (half, 0.0, 0.0),
        mats["steel"],
        "spindle_shaft",
        rpy=_X_AXIS_RPY,
    )
    _knurled(
        spindle, 0.0050, 0.0040, (half, 0.0, 0.0), mats, "spindle_wheel", _X_AXIS_RPY, bands=12
    )
    # A threaded run each side of the centre wheel, opposed as a real turnbuckle
    # spindle is: turning the wheel draws both hex nuts toward it.
    for index, x0 in enumerate((half * 0.20, half * 1.16)):
        _threaded_rod(
            spindle,
            _SHAFT_R,
            _SHAFT_R * 1.55,
            half * 0.64,
            (x0, 0.0, 0.0),
            mats["bright"],
            f"spindle_thread_{index}",
            rpy=_X_AXIS_RPY,
        )
    joint = _spin_joint(
        model,
        needle.station_part,
        spindle,
        name=_adjuster_name(r, "spin"),
        point=(0.0, _station_y(needle, r), needle.station_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=_SHAFT_R,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.8, velocity=6.0),
        meta={"mechanism": "centred spindle adjuster"},
    )
    return [joint]


def _adjuster_style_side_link_wheel_build(model, r, mats, head, needle, lead) -> list[str]:
    """003 L362-L402: a swinging side link carrying its own knurled wheel."""
    pin_y = _station_y(needle, r)
    _add_standoff(needle.station_part, r, needle, mats, needle.station_z, "link_standoff")
    _cyl(
        needle.station_part,
        0.0030,
        0.0032,
        (0.0, pin_y, needle.station_z),
        mats["bright"],
        "link_pivot_pin",
        rpy=_Y_AXIS_RPY,
    )
    link = model.part(
        _adjuster_name(r, "link"),
        meta={"role": "adjuster", "mechanism": "side adjustment link"},
    )
    reach = r.tip_span_m * 0.42 + 0.014
    # The link tapers from its leg pivot toward the wheel end, as a stamped
    # linkage does, instead of running as a constant-section bar.
    _plate(
        link,
        _tapered_bar_profile((0.0, 0.0), (reach, 0.0), 0.0058, 0.0042),
        0.0026,
        (0.0, 0.0, 0.0),
        mats["bright"],
        "link_bar",
        _PLATE_RPY,
    )
    _cyl(link, 0.0034, 0.0026, (0.0, 0.0, 0.0), mats["bright"], "link_eye", rpy=_Y_AXIS_RPY)
    _cyl(link, 0.0030, 0.0026, (reach, 0.0, 0.0), mats["bright"], "link_end_eye", rpy=_Y_AXIS_RPY)
    swing = _spin_joint(
        model,
        needle.station_part,
        link,
        name=_adjuster_name(r, "swing"),
        point=(0.0, pin_y, needle.station_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0030,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.0, velocity=1.8, lower=-0.16, upper=0.16),
        meta={"mechanism": "adjustment link swing"},
    )
    wheel = model.part(
        _adjuster_name(r, "wheel"),
        meta={"role": "adjuster_control", "mechanism": "link thumbwheel"},
    )
    _knurled(wheel, 0.0058, 0.0038, (0.0, 0.0, 0.0), mats, "knurled_wheel", _X_AXIS_RPY, bands=14)
    _cyl(wheel, 0.0016, 0.0100, (0.0, 0.0, 0.0), mats["steel"], "wheel_spindle", rpy=_X_AXIS_RPY)
    spin = _spin_joint(
        model,
        link,
        wheel,
        name=_adjuster_name(r, "wheel_spin"),
        point=(reach * 0.72, 0.0, 0.0),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0016,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.25, velocity=7.0),
        meta={"mechanism": "link thumbwheel"},
    )
    return [swing, spin]


def _adjuster_style_head_wheel_build(model, r, mats, head, needle, lead) -> list[str]:
    """004 L388-L414: one wheel riding the head's own threaded spindle spine."""
    depth = r.station_m + 0.010
    _head_spine(head, r, mats, depth, "head_wheel")
    _cyl(
        head.part,
        0.0014,
        0.0140,
        (0.0, head.front_y, -depth * 0.55),
        mats["steel"],
        "head_wheel_spindle",
    )
    wheel = model.part(
        _adjuster_name(r, "wheel"),
        meta={"role": "adjuster", "mechanism": "head-mounted adjustment wheel"},
    )
    _knurled(
        wheel, 0.0070, 0.0042, (0.0, 0.0, 0.0), mats, "adjust_wheel", (0.0, 0.0, 0.0), bands=16
    )
    _cyl(wheel, 0.0018, 0.0090, (0.0, 0.0, 0.0), mats["steel"], "wheel_hub")
    joint = _spin_joint(
        model,
        head.part,
        wheel,
        name=_adjuster_name(r, "spin"),
        point=(0.0, head.front_y, -depth * 0.55),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0018,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.7, velocity=5.0),
        meta={"mechanism": "head adjustment wheel"},
    )
    return [joint]


def _adjuster_style_bow_spreader_build(model, r, mats, head, needle, lead) -> list[str]:
    """bow_spring fork L133-L175: a vertical threaded spreader under the bow."""
    depth = r.station_m * 0.70 + 0.008
    _head_spine(head, r, mats, depth, "bow_spreader")
    _box(
        head.part,
        (0.0140, 0.0026, 0.0034),
        (0.0, head.front_y, -depth),
        mats["bright"],
        "spreader_yoke",
    )
    screw = model.part(
        _adjuster_name(r, "spreader"),
        meta={"role": "adjuster", "mechanism": "bow spreader screw"},
    )
    length = r.station_m * 0.85 + 0.010
    _cyl(screw, _SHAFT_R * 1.15, length, (0.0, 0.0, -length / 2.0), mats["steel"], "spreader_shaft")
    _threaded_rod(
        screw,
        _SHAFT_R * 1.15,
        _SHAFT_R * 1.70,
        length * 0.74,
        (0.0, 0.0, -length * 0.90),
        mats["bright"],
        "spreader_thread",
    )
    _knurled(
        screw,
        0.0056,
        0.0038,
        (0.0, 0.0, -0.0022),
        mats,
        "spreader_wheel",
        (0.0, 0.0, 0.0),
        bands=12,
    )
    _ball(screw, 0.0020, (0.0, 0.0, -length), mats["grip"], "spreader_end_ball")
    joint = _spin_joint(
        model,
        head.part,
        screw,
        name=_adjuster_name(r, "spin"),
        point=(0.0, head.front_y, -depth),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=_SHAFT_R * 1.15,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.8, velocity=6.0),
        meta={"mechanism": "bow spreader screw"},
    )
    return [joint]


def _adjuster_style_rack_pinion_build(model, r, mats, head, needle, lead) -> list[str]:
    """rack_pinion fork L337-L433: a head pinion between two concentric racks."""
    rack_radius = r.hub_radius_m + 0.0140
    # A real involute pinion: module 0.8 mm x 14 teeth puts the pitch radius at
    # exactly 5.6 mm, which is the pitch radius this mechanism was laid out
    # around, so nothing about the rack geometry moves.
    pinion_module_mm = 0.8
    pinion_teeth = 14
    pinion_width = 0.0030
    pitch_r = pinion_module_mm * pinion_teeth / 2000.0
    pinion_z = -(rack_radius - 0.0094)
    _head_spine(head, r, mats, abs(pinion_z), "rack_pinion")
    # The racks are concentric with the hinge, so a swinging leg slides its rack
    # tangentially past the pinion instead of driving into it.  Each rack is
    # rooted on its leg by a standoff at the arc's inboard end.
    rack_teeth = 9
    for leg, tag in ((needle, "needle"), (lead, "lead")):
        rack_y = _station_y(leg, r)
        start, end = 0.05, 0.26
        _add_standoff(
            leg.root,
            r,
            leg,
            mats,
            -rack_radius * math.cos(start),
            f"rack_standoff_{tag}",
            width=0.0060,
        )
        # One curved backing plate, exactly the construction the rack fork uses
        # (``_rack_sector_body_shape``, model.py:L120-L144).  Five rotated boxes
        # used to stand in for this arc, each 4.6 mm long on a 1.5 mm pitch, so
        # every box overhung its neighbours by 3x and the sector read as a
        # ragged sawtooth fan rather than a rack.
        _plate(
            leg.root,
            _annular_sector_profile(
                rack_radius - 0.0013,
                rack_radius + 0.0013,
                math.pi + leg.side * start,
                math.pi + leg.side * end,
                segments=20,
            ),
            _WALL,
            (0.0, rack_y, 0.0),
            mats["steel"],
            f"rack_rim_{tag}",
            _PLATE_RPY,
        )
        # Teeth stand off the arc's inboard face toward the pinion, seated into
        # the backing plate so the sector stays one connected island.
        for index in range(rack_teeth):
            angle = -leg.side * (start + (end - start) * float(index) / float(rack_teeth - 1))
            radius = rack_radius - 0.0022
            _box(
                leg.root,
                (0.0016, _WALL, 0.0028),
                (radius * math.sin(angle), rack_y, -radius * math.cos(angle)),
                mats["steel"],
                f"rack_tooth_{tag}_{index}",
                rpy=(0.0, -angle, 0.0),
            )
    pinion = model.part(
        _adjuster_name(r, "pinion"),
        meta={
            "role": "adjuster",
            "mechanism": "rack and pinion",
            "module_m": pinion_module_mm / 1000.0,
            "teeth": pinion_teeth,
        },
    )
    # Built in MILLIMETRES and meshed with unit_scale=0.001.  OCC tolerances are
    # absolute, so an involute wheel authored directly at metre scale comes back
    # degenerate and in several disconnected components; ``.build()`` is called
    # bare because passing bore_d returns stray construction solids.
    gear_solid = SpurGear(
        module=pinion_module_mm,
        teeth_number=pinion_teeth,
        width=pinion_width * 1000.0,
    ).build()
    pinion.visual(
        mesh_from_cadquery(
            gear_solid,
            f"{pinion.name}__pinion_gear",
            tolerance=0.0003,
            unit_scale=0.001,
        ),
        # SpurGear runs from z=0 to z=width, so half the width recentres it once
        # the +90 degrees about X has laid the axis down onto -Y.
        origin=Origin(xyz=(0.0, pinion_width / 2.0, 0.0), rpy=_Y_AXIS_RPY),
        material=mats["steel"],
        name="pinion_gear", material_class_id="metal.steel_bare",
    )
    _cyl(pinion, 0.0016, 0.0064, (0.0, 0.0, 0.0), mats["bright"], "pinion_shaft", rpy=_Y_AXIS_RPY)
    # A knurled thumbwheel on the front end is how the fork drives the pinion
    # (model.py:L360-L372); without it the gear has no hand interface at all.
    _knurled(
        pinion,
        pitch_r * 0.72,
        0.0022,
        (0.0, -pinion_width / 2.0 - 0.0009, 0.0),
        mats,
        "pinion_thumbwheel",
        _Y_AXIS_RPY,
        bands=18,
    )
    joint = _spin_joint(
        model,
        head.part,
        pinion,
        name=_adjuster_name(r, "spin"),
        point=(0.0, head.front_y, pinion_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=0.0016,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.5, velocity=4.0, lower=-2.0, upper=2.0),
        meta={"mechanism": "radius-setting pinion"},
    )
    return [joint]


def _adjuster_style_ratchet_quadrant_build(model, r, mats, head, needle, lead) -> list[str]:
    """ratchet fork L442-L503: a toothed quadrant, a pawl and a release tab."""
    quad_pin_y = _station_y(lead, r)
    _add_standoff(lead.station_part, r, lead, mats, lead.station_z, "quadrant_standoff")
    _cyl(
        lead.station_part,
        0.0028,
        0.0030,
        (0.0, quad_pin_y, lead.station_z),
        mats["bright"],
        "quadrant_pin",
        rpy=_Y_AXIS_RPY,
    )
    quadrant = model.part(
        _adjuster_name(r, "quadrant"),
        meta={"role": "adjuster", "mechanism": "toothed locking quadrant"},
    )
    arc_r = r.tip_span_m * 0.34 + 0.012
    _cyl(quadrant, 0.0034, 0.0024, (0.0, 0.0, 0.0), mats["bright"], "quadrant_hub", rpy=_Y_AXIS_RPY)
    # A toothed QUADRANT is an arc struck about its own pivot, and its teeth
    # have to sit on that arc — the pawl sweeps a circle about the pivot, so a
    # tooth row laid along a straight chord can only meet the pawl at one point.
    # This used to be a rectangular web with nine teeth in a straight line at a
    # fixed z.  The ratchet fork builds the real thing: an annular sector plus a
    # pivot boss and a connecting spoke (``_quadrant_arc``, model.py:L96-L134).
    half_angle = 0.42
    band = 0.0030
    _plate(
        quadrant,
        _annular_sector_profile(
            arc_r - band,
            arc_r,
            math.pi / 2.0 - half_angle,
            math.pi / 2.0 + half_angle,
            segments=22,
        ),
        0.0024,
        (0.0, 0.0, 0.0),
        mats["bright"],
        "quadrant_arc",
        _PLATE_RPY,
    )
    # The spoke ties the arc back to the pivot boss so the sector is one island.
    _plate(
        quadrant,
        _tapered_bar_profile((0.0, 0.0), (arc_r - band * 0.5, 0.0), 0.0056, 0.0038),
        0.0024,
        (0.0, 0.0, 0.0),
        mats["bright"],
        "quadrant_spoke",
        _PLATE_RPY,
    )
    # Teeth ride the outer face of the arc, each turned so its own +Z is the
    # radial direction.  Angles are measured from +Z like every other arc here,
    # and R_y(a) carries local +Z onto (sin a, 0, cos a) — the outward radial.
    tooth_count = 11
    tooth_r = arc_r - 0.0006
    for index in range(tooth_count):
        angle = (
            math.pi / 2.0 - half_angle + 2.0 * half_angle * float(index) / float(tooth_count - 1)
        )
        _box(
            quadrant,
            (0.0019, 0.0026, 0.0034),
            (tooth_r * math.sin(angle), 0.0, tooth_r * math.cos(angle)),
            mats["steel"],
            f"quadrant_tooth_{index}",
            rpy=(0.0, angle, 0.0),
        )
    quad_joint = _spin_joint(
        model,
        lead.station_part,
        quadrant,
        name=_adjuster_name(r, "quadrant_swing"),
        point=(0.0, quad_pin_y, lead.station_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0028,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.0, velocity=1.8, lower=-0.20, upper=0.20),
        meta={"mechanism": "locking quadrant"},
    )
    pawl_pin_y = _station_y(needle, r)
    _add_standoff(needle.station_part, r, needle, mats, needle.station_z, "pawl_standoff")
    _cyl(
        needle.station_part,
        0.0024,
        0.0028,
        (0.0, pawl_pin_y, needle.station_z),
        mats["bright"],
        "pawl_pin",
        rpy=_Y_AXIS_RPY,
    )
    pawl = model.part(
        _adjuster_name(r, "pawl"),
        meta={"role": "adjuster_control", "mechanism": "ratchet pawl"},
    )
    _box(pawl, (0.0130, 0.0022, 0.0034), (0.0065, 0.0, 0.0), mats["steel"], "pawl_arm")
    _box(pawl, (0.0022, _WALL, 0.0030), (0.0135, 0.0, -0.0022), mats["steel"], "pawl_tooth")
    _cyl(pawl, 0.0028, 0.0022, (0.0, 0.0, 0.0), mats["steel"], "pawl_eye", rpy=_Y_AXIS_RPY)
    pawl_joint = _spin_joint(
        model,
        needle.station_part,
        pawl,
        name=_adjuster_name(r, "pawl_swing"),
        point=(0.0, pawl_pin_y, needle.station_z),
        axis=(0.0, 1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0028,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=0.8, velocity=2.5, lower=-0.03, upper=0.15),
        meta={"mechanism": "ratchet pawl"},
    )
    tab = model.part(
        _adjuster_name(r, "release_tab"),
        meta={"role": "adjuster_control", "mechanism": "pawl release tab"},
    )
    _box(tab, (0.0090, 0.0020, 0.0026), (-0.0045, 0.0, 0.0), mats["grip"], "release_blade")
    _cyl(tab, 0.0022, 0.0020, (0.0, 0.0, 0.0), mats["grip"], "release_eye", rpy=_Y_AXIS_RPY)
    tab_joint = _spin_joint(
        model,
        pawl,
        tab,
        name=_adjuster_name(r, "release_swing"),
        point=(0.0040, 0.0, 0.0040),
        axis=(0.0, -1.0, 0.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0022,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=0.3, velocity=4.0, lower=0.0, upper=0.25),
        meta={"mechanism": "pawl release tab"},
    )
    return [quad_joint, pawl_joint, tab_joint]


def _adjuster_style_center_wheel_build(model, r, mats, head, needle, lead) -> list[str]:
    """quick_set fork L308-L358: a quick-set wheel with two release arms."""
    axle_y = _station_y(lead, r)
    _add_standoff(lead.station_part, r, lead, mats, lead.station_z, "quick_set_standoff")
    _cyl(
        lead.station_part,
        0.0032,
        0.0030,
        (0.0, axle_y, lead.station_z),
        mats["bright"],
        "quick_set_axle_boss",
        rpy=_X_AXIS_RPY,
    )
    wheel = model.part(
        _adjuster_name(r, "wheel"),
        meta={"role": "adjuster", "mechanism": "quick-set centre wheel"},
    )
    _knurled(wheel, 0.0072, 0.0044, (0.0, 0.0, 0.0), mats, "center_wheel", _X_AXIS_RPY, bands=18)
    _cyl(wheel, 0.0016, 0.0140, (0.0, 0.0, 0.0), mats["steel"], "threaded_axle", rpy=_X_AXIS_RPY)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            wheel,
            (0.0026, 0.0018, 0.0130),
            (0.0026, sign * 0.0060, 0.0065),
            mats["steel"],
            f"release_arm_{index}",
            rpy=(sign * 0.22, 0.0, 0.0),
        )
    joint = _spin_joint(
        model,
        lead.station_part,
        wheel,
        name=_adjuster_name(r, "spin"),
        point=(0.0, axle_y, lead.station_z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0016,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.2, velocity=6.0, lower=-0.35, upper=0.35),
        meta={"mechanism": "quick-set centre wheel"},
    )
    return [joint]


_ADJUSTER_BUILDERS = {
    "cross_screw": _adjuster_style_cross_screw_build,
    "center_spindle": _adjuster_style_center_spindle_build,
    "side_link_wheel": _adjuster_style_side_link_wheel_build,
    "head_wheel": _adjuster_style_head_wheel_build,
    "bow_spreader": _adjuster_style_bow_spreader_build,
    "rack_pinion": _adjuster_style_rack_pinion_build,
    "ratchet_quadrant": _adjuster_style_ratchet_quadrant_build,
    "center_wheel": _adjuster_style_center_wheel_build,
}


# --------------------------------------------------------------------------- #
# lead_end_style candidates (always on the lead leg)
# --------------------------------------------------------------------------- #
def _lead_name(r: ResolvedConfig, local: str) -> str:
    return f"lead_end_style__{r.lead_end_style}__{local}"


def _collet_profile(
    body_r: float, nose_r: float, length: float, mouth: float
) -> list[tuple[float, float]]:
    """Half-section of a turned collet: a barrel, a flared nose, a taper to the bore.

    ``LatheGeometry`` revolves an (radius, z) half-section about local Z, which
    is how a collet is actually made and how the source records shape theirs.
    Two coaxial cylinders of different diameters butted end to end give a
    machined step instead; the taper is the whole visual difference between a
    pencil collet and a stack of tubes.
    """
    return [
        (0.0, length),
        (body_r, length),
        (body_r, mouth + 0.0034),
        (nose_r, mouth + 0.0014),
        (nose_r, mouth),
        (nose_r * 0.52, 0.0),
        (0.0, 0.0),
    ]


def _add_collet(part, mats, z: float, prefix: str) -> None:
    """A lead collet and its graphite point, in the owning part's frame."""
    _mesh(
        part,
        LatheGeometry(_collet_profile(0.0026, 0.0032, 0.0140, 0.0016), segments=32),
        (0.0, 0.0, z),
        mats["bright"],
        f"{prefix}_collet",
    )
    # The lead is a real sharpened stick, not a flat-ended rod.
    _cyl(part, 0.0009, 0.0100, (0.0, 0.0, z - 0.0044), mats["lead"], f"{prefix}_lead")
    _mesh(
        part,
        ConeGeometry(0.0009, 0.0026, radial_segments=20),
        (0.0, 0.0, z - 0.0094),
        mats["lead"],
        f"{prefix}_lead_tip",
        rpy=(math.pi, 0.0, 0.0),
    )


def _add_clamp(model, mats, host, host_y: float, z: float, name: str) -> str:
    """The small knurled clamp screw that retains the lead."""
    _cyl(host, 0.0022, 0.0026, (0.0, host_y, z), mats["bright"], f"{name}_boss", rpy=_X_AXIS_RPY)
    clamp = model.part(name, meta={"role": "lead_clamp", "mechanism": "lead clamp screw"})
    _cyl(clamp, 0.0010, 0.0070, (0.0035, 0.0, 0.0), mats["steel"], "clamp_stem", rpy=_X_AXIS_RPY)
    _knurled(clamp, 0.0038, 0.0026, (0.0072, 0.0, 0.0), mats, "clamp_wheel", _X_AXIS_RPY, bands=10)
    return _spin_joint(
        model,
        host,
        clamp,
        name=f"{name}__spin",
        point=(0.0, host_y, z),
        axis=(1.0, 0.0, 0.0),
        radial=(0.0, 0.0, 1.0),
        radius=0.0010,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.4, velocity=8.0),
        meta={"mechanism": "lead clamp screw"},
    )


def _lead_end_style_fixed_collet_build(model, r, mats, lead: _Leg) -> list[str]:
    """001 L337-L363: collet and lead fused into the leg, clamp screw only."""
    _add_collet(lead.tip_part, mats, lead.tip_z, "fixed")
    _box(
        lead.tip_part,
        (0.0080, r.leg_thickness_m + 0.0020, 0.0090),
        (0.0, 0.0, lead.tip_z + 0.0160),
        mats["bright"],
        "lead_clamp_shoe",
    )
    _add_standoff(lead.tip_part, r, lead, mats, lead.tip_z + 0.0160, "clamp_standoff", width=0.0072)
    joint = _add_clamp(
        model,
        mats,
        lead.tip_part,
        _station_y(lead, r),
        lead.tip_z + 0.0160,
        _lead_name(r, "clamp"),
    )
    return [joint]


def _holder_part(model, r, mats, name: str, length: float):
    part = model.part(name, meta={"role": "lead_holder", "mechanism": "hinged lead holder"})
    _cyl(
        part,
        0.0036,
        r.leg_thickness_m,
        (0.0, 0.0, 0.0),
        mats["body"],
        "holder_eye",
        rpy=_Y_AXIS_RPY,
    )
    _plate(
        part,
        _tapered_bar_profile((0.0, _WELD), (0.0, -length), 0.0064, 0.0046),
        r.leg_thickness_m,
        (0.0, 0.0, 0.0),
        mats["body"],
        "holder_body",
        _PLATE_RPY,
    )
    return part


def _holder_lap_y(r: ResolvedConfig) -> float:
    """The holder plate laps alongside the leg plate, never through it."""
    return r.leg_thickness_m + 0.0008


def _add_holder_pin(part, r: ResolvedConfig, mats, hinge_z: float) -> None:
    lap = _holder_lap_y(r)
    y0 = -r.leg_thickness_m / 2.0 - 0.0010
    y1 = lap + 0.0011
    _cyl(
        part,
        0.0030,
        y1 - y0,
        (0.0, (y0 + y1) / 2.0, hinge_z),
        mats["bright"],
        "holder_hinge_pin",
        rpy=_Y_AXIS_RPY,
    )


def _lead_end_style_hinged_holder_build(model, r, mats, lead: _Leg) -> list[str]:
    """004 L287-L341: a separate holder plate hinged on the leg."""
    hinge_z = lead.tip_z + r.leg_length_m * 0.22
    _add_holder_pin(lead.tip_part, r, mats, hinge_z)
    length = r.leg_length_m * 0.22
    holder = _holder_part(model, r, mats, _lead_name(r, "holder"), length)
    _add_collet(holder, mats, -length, "holder")
    joint = _spin_joint(
        model,
        lead.tip_part,
        holder,
        name=_lead_name(r, "hinge"),
        point=(0.0, _holder_lap_y(r), hinge_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=0.0030,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.5, velocity=1.0, lower=-0.22, upper=0.22),
        meta={"mechanism": "hinged lead holder"},
    )
    clamp = _add_clamp(
        model,
        mats,
        holder,
        r.leg_thickness_m / 2.0 + 0.0016,
        -length * 0.45,
        _lead_name(r, "clamp"),
    )
    return [joint, clamp]


def _lead_end_style_extension_rail_build(model, r, mats, lead: _Leg) -> list[str]:
    """extension fork L330-L367: a prismatic rail carrying the hinged holder."""
    rail_top = lead.tip_z + r.leg_length_m * 0.30
    rail_y = _station_y(lead, r)
    for index, dz in enumerate((0.0, -r.leg_length_m * 0.12)):
        _add_standoff(
            lead.tip_part, r, lead, mats, rail_top + dz, f"rail_standoff_{index}", width=0.0050
        )
        _box(
            lead.tip_part,
            (0.0056, _WALL, 0.0022),
            (0.0, rail_y, rail_top + dz),
            mats["steel"],
            f"rail_channel_{index}",
        )
    rail = model.part(
        _lead_name(r, "rail"),
        meta={"role": "lead_extension", "mechanism": "radius extension rail"},
    )
    rail_len = r.leg_length_m * 0.30
    for index, sign in enumerate((-1.0, 1.0)):
        _cyl(
            rail,
            0.0016,
            rail_len,
            (sign * 0.0022, 0.0, -rail_len / 2.0),
            mats["bright"],
            f"rail_rod_{index}",
        )
    _box(
        rail, (0.0074, 0.0026, 0.0030), (0.0, 0.0, -rail_len + 0.0015), mats["bright"], "rail_shoe"
    )
    travel = rail_len * 0.42
    prismatic = _lead_name(r, "extend")
    model.articulation(
        prismatic,
        ArticulationType.PRISMATIC,
        parent=lead.tip_part,
        child=rail,
        origin=Origin(xyz=(0.0, rail_y, rail_top)),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=0.05, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=1.2, friction=0.6),
        meta={"mechanism": "radius extension rail"},
    )
    length = r.leg_length_m * 0.18
    holder = _holder_part(model, r, mats, _lead_name(r, "holder"), length)
    _add_collet(holder, mats, -length, "holder")
    hinge = _spin_joint(
        model,
        rail,
        holder,
        name=_lead_name(r, "hinge"),
        point=(0.0, 0.0, -rail_len),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=0.0030,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.5, velocity=1.0, lower=-0.18, upper=0.18),
        meta={"mechanism": "hinged holder on the extension rail"},
    )
    return [prismatic, hinge]


def _lead_end_style_pen_adapter_build(model, r, mats, lead: _Leg) -> list[str]:
    """pen_adapter fork L441-L540: a second-stage yoke that clamps a pen."""
    hinge_z = lead.tip_z + r.leg_length_m * 0.24
    _add_holder_pin(lead.tip_part, r, mats, hinge_z)
    length = r.leg_length_m * 0.14
    holder = _holder_part(model, r, mats, _lead_name(r, "holder"), length)
    hinge = _spin_joint(
        model,
        lead.tip_part,
        holder,
        name=_lead_name(r, "hinge"),
        point=(0.0, _holder_lap_y(r), hinge_z),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=0.0030,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.5, velocity=1.0, lower=-0.20, upper=0.20),
        meta={"mechanism": "hinged holder"},
    )
    yoke = model.part(
        _lead_name(r, "adapter_yoke"),
        meta={"role": "lead_holder", "mechanism": "technical pen adapter yoke"},
    )
    # The eye has to reach the cheeks' inner faces at x = +-0.0035 on its own,
    # not lean on the pen barrel passing through it.
    _cyl(yoke, 0.0038, 0.0026, (0.0, 0.0, 0.0), mats["bright"], "yoke_eye", rpy=_Y_AXIS_RPY)
    for index, sign in enumerate((-1.0, 1.0)):
        _box(
            yoke,
            (0.0018, 0.0030, 0.0150),
            (sign * 0.0044, 0.0, -0.0075),
            mats["bright"],
            f"yoke_cheek_{index}",
        )
    _box(yoke, (0.0106, 0.0026, 0.0022), (0.0, 0.0, -0.0148), mats["bright"], "yoke_strap")
    # A technical pen: a turned barrel that steps down into a cone nib holder,
    # then the drawing needle itself.  Two butted cylinders read as a dowel.
    _mesh(
        yoke,
        LatheGeometry(
            [
                (0.0, 0.0),
                (0.0030, 0.0),
                (0.0030, 0.0134),
                (0.0022, 0.0152),
                (0.0022, 0.0170),
                (0.0009, 0.0180),
                (0.0, 0.0180),
            ],
            segments=28,
        ),
        # Turned about local +Z, then flipped so the fat end sits at the yoke
        # eye and the stepped nib holder points down the drawing axis.
        (0.0, 0.0, 0.0),
        mats["grip"],
        "pen_barrel",
        rpy=(math.pi, 0.0, 0.0),
    )
    # The nib runs UP into the barrel's bore rather than butting against its
    # end face: a turned tip that only kisses its holder is exactly the fragile
    # tangency the 1e-6 intra-part connectivity check reports as an island.
    _cyl(yoke, 0.0007, 0.0064, (0.0, 0.0, -0.0206), mats["needle"], "pen_nib")
    _mesh(
        yoke,
        ConeGeometry(0.0007, 0.0022, radial_segments=16),
        (0.0, 0.0, -0.0246),
        mats["needle"],
        "pen_nib_tip",
        rpy=(math.pi, 0.0, 0.0),
    )
    adapter = _spin_joint(
        model,
        holder,
        yoke,
        name=_lead_name(r, "adapter_swing"),
        point=(0.0, 0.0, -length),
        axis=(0.0, 1.0, 0.0),
        radial=(0.0, 0.0, -1.0),
        radius=0.0032,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=1.0, velocity=1.0, lower=-0.26, upper=0.26),
        meta={"mechanism": "pen adapter yoke"},
    )
    return [hinge, adapter]


def _lead_end_style_rotating_collet_build(model, r, mats, lead: _Leg) -> list[str]:
    """lead_cartridge fork L444-L477: the collet becomes its own turning part."""
    _cyl(
        lead.tip_part,
        0.0034,
        0.0070,
        (0.0, 0.0, lead.tip_z + 0.0100),
        mats["body"],
        "collet_seat",
    )
    collet = model.part(
        _lead_name(r, "collet"),
        meta={"role": "lead_holder", "mechanism": "screw-in lead collet"},
    )
    # A turned cartridge collet.  The six "slots" used to be 0.4 mm rods laid
    # ON the 2.8 mm barrel, so half of each stood proud and the collet read as a
    # whiskered rod; a real split collet is a knurled grip band and a tapered
    # nose, which is what the lead_cartridge fork turns (model.py:L444-L477).
    _mesh(
        collet,
        LatheGeometry(_collet_profile(0.0028, 0.0034, 0.0130, 0.0018), segments=32),
        (0.0, 0.0, -0.0130),
        mats["bright"],
        "collet_body",
    )
    _knurled(collet, 0.0031, 0.0038, (0.0, 0.0, -0.0034), mats, "collet_grip", (0.0, 0.0, 0.0), 16)
    # Seated up inside the collet nose, not butted against its mouth.
    _cyl(collet, 0.0009, 0.0110, (0.0, 0.0, -0.0181), mats["lead"], "cartridge_lead")
    _mesh(
        collet,
        ConeGeometry(0.0009, 0.0026, radial_segments=20),
        (0.0, 0.0, -0.0248),
        mats["lead"],
        "cartridge_lead_tip",
        rpy=(math.pi, 0.0, 0.0),
    )
    joint = _spin_joint(
        model,
        lead.tip_part,
        collet,
        name=_lead_name(r, "spin"),
        point=(0.0, 0.0, lead.tip_z + 0.0100),
        axis=(0.0, 0.0, -1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0028,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=0.25, velocity=5.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "screw-in lead collet"},
    )
    return [joint]


_LEAD_BUILDERS = {
    "fixed_collet": _lead_end_style_fixed_collet_build,
    "hinged_holder": _lead_end_style_hinged_holder_build,
    "extension_rail": _lead_end_style_extension_rail_build,
    "pen_adapter": _lead_end_style_pen_adapter_build,
    "rotating_collet": _lead_end_style_rotating_collet_build,
}


# --------------------------------------------------------------------------- #
# needle_end_style candidates (always on the needle leg)
# --------------------------------------------------------------------------- #
def _needle_name(r: ResolvedConfig, local: str) -> str:
    return f"needle_end_style__{r.needle_end_style}__{local}"


def _needle_end_style_fixed_needle_build(model, r, mats, needle: _Leg) -> list[str]:
    """001 L279-L305: a socket and needle fused into the leg with a fastener."""
    z = needle.tip_z
    _mesh(
        needle.tip_part,
        LatheGeometry(_collet_profile(0.0018, 0.0022, 0.0140, 0.0014), segments=28),
        (0.0, 0.0, z),
        mats["bright"],
        "needle_socket",
    )
    # A centre point is a ground taper, not a flat-ended pin — the source builds
    # its tips through ``_cone_mesh`` for exactly this reason.
    _cyl(needle.tip_part, 0.0006, 0.0104, (0.0, 0.0, z - 0.0046), mats["needle"], "needle_point")
    _mesh(
        needle.tip_part,
        ConeGeometry(0.0006, 0.0040, radial_segments=20),
        (0.0, 0.0, z - 0.0114),
        mats["needle"],
        "needle_tip",
        rpy=(math.pi, 0.0, 0.0),
    )
    _cyl(
        needle.tip_part,
        0.0022,
        r.leg_thickness_m + 0.0018,
        (0.0, 0.0, z + 0.0170),
        mats["bright"],
        "lower_fastener",
        rpy=_Y_AXIS_RPY,
    )
    return []


def _needle_end_style_collet_cartridge_build(model, r, mats, needle: _Leg) -> list[str]:
    """collet fork L556-L652: a prismatic cartridge plus a release sleeve."""
    z = needle.tip_z
    # The slotted collet body: a turned barrel with a tapered mouth.  The four
    # 0.3 mm "slot" rods this used to lay on the outside of the barrel stood
    # half-proud and read as whiskers; a slit collet's slots are cuts.
    _mesh(
        needle.tip_part,
        LatheGeometry(_collet_profile(0.0032, 0.0038, 0.0180, 0.0020), segments=32),
        (0.0, 0.0, z + 0.0040),
        mats["body_dark"],
        "collet_body",
    )
    cartridge = model.part(
        _needle_name(r, "cartridge"),
        meta={"role": "center_point", "mechanism": "replaceable needle cartridge"},
    )
    _cyl(cartridge, 0.0021, 0.0120, (0.0, 0.0, 0.0060), mats["bright"], "cartridge_body")
    _cyl(cartridge, 0.0025, 0.0012, (0.0, 0.0, 0.0126), mats["bright"], "cartridge_shoulder")
    _cyl(cartridge, 0.0006, 0.0140, (0.0, 0.0, -0.0070), mats["steel"], "needle_point")
    travel = 0.0060
    prismatic = _needle_name(r, "insert")
    model.articulation(
        prismatic,
        ArticulationType.PRISMATIC,
        parent=needle.tip_part,
        child=cartridge,
        origin=Origin(xyz=(0.0, 0.0, z + 0.0020)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.5, velocity=0.5, lower=0.0, upper=travel),
        motion_properties=MotionProperties(damping=1.0, friction=0.5),
        meta={"mechanism": "needle cartridge insertion"},
    )
    sleeve = model.part(
        _needle_name(r, "release_sleeve"),
        meta={"role": "center_point_control", "mechanism": "knurled release sleeve"},
    )
    # One knurled sleeve, not a body ringed by twelve half-buried 0.5 mm rods.
    _knurled(sleeve, 0.0044, 0.0090, (0.0, 0.0, 0.0), mats, "sleeve_body", (0.0, 0.0, 0.0), 20)
    _cyl(sleeve, 0.0050, 0.0012, (0.0, 0.0, 0.0045), mats["steel"], "sleeve_flange")
    spin = _spin_joint(
        model,
        needle.tip_part,
        sleeve,
        name=_needle_name(r, "sleeve_spin"),
        point=(0.0, 0.0, z + 0.0195),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0044,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.6, velocity=5.0),
        meta={"mechanism": "cartridge release sleeve"},
    )
    return [prismatic, spin]


_NEEDLE_BUILDERS = {
    "fixed_needle": _needle_end_style_fixed_needle_build,
    "collet_cartridge": _needle_end_style_collet_cartridge_build,
}


# --------------------------------------------------------------------------- #
# handle_style candidates
# --------------------------------------------------------------------------- #
def _handle_name(r: ResolvedConfig, local: str) -> str:
    return f"handle_style__{r.handle_style}__{local}"


def _handle_style_spin_grip_build(model, r, mats, head: _Head) -> list[str]:
    """001 L227-L256: a banded grip spinning freely on the head crown."""
    _cyl(head.part, 0.0016, 0.0050, (0.0, 0.0, head.crown_z - 0.0020), mats["bright"], "grip_stem")
    grip = model.part(
        _handle_name(r, "grip"),
        meta={"role": "handle", "mechanism": "free-spinning top grip"},
    )
    length = 0.0240 * r.head_scale
    # One turned grip: a waisted barrel with real beads at both ends and a
    # domed cap, revolved as a single half-section.  It used to be a plain
    # cylinder with six 0.6 mm discs threaded onto it, which at this scale read
    # as a stack of washers rather than as a turned handle.
    waist = 0.0027
    bead = 0.0031
    _mesh(
        grip,
        LatheGeometry(
            [
                (0.0, 0.0),
                (bead, 0.0),
                (bead, length * 0.10),
                (waist, length * 0.20),
                (waist, length * 0.74),
                (bead, length * 0.84),
                (bead, length * 0.96),
                (bead * 0.72, length),
                (0.0, length),
            ],
            segments=36,
        ),
        (0.0, 0.0, 0.0),
        mats["grip"],
        "grip_body",
    )
    joint = _spin_joint(
        model,
        head.part,
        grip,
        name=_handle_name(r, "spin"),
        point=(0.0, 0.0, head.crown_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0027,
        joint_type=ArticulationType.CONTINUOUS,
        limits=MotionLimits(effort=0.25, velocity=8.0),
        meta={"mechanism": "top grip"},
    )
    return [joint]


def _handle_style_knurled_handle_build(model, r, mats, head: _Head) -> list[str]:
    """003 L326-L347: a stem plus a knurled knob on a bounded revolute joint."""
    _cyl(
        head.part, 0.0018, 0.0044, (0.0, 0.0, head.crown_z - 0.0018), mats["bright"], "handle_seat"
    )
    handle = model.part(
        _handle_name(r, "handle"),
        meta={"role": "handle", "mechanism": "bounded knurled handle"},
    )
    stem = 0.0210 * r.head_scale
    _cyl(handle, 0.0026, stem, (0.0, 0.0, stem / 2.0), mats["body"], "handle_stem")
    _knurled(
        handle,
        0.0052,
        0.0110,
        (0.0, 0.0, stem + 0.0055),
        mats,
        "knurled_knob",
        (0.0, 0.0, 0.0),
        bands=14,
    )
    joint = _spin_joint(
        model,
        head.part,
        handle,
        name=_handle_name(r, "turn"),
        point=(0.0, 0.0, head.crown_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
        radius=0.0026,
        joint_type=ArticulationType.REVOLUTE,
        limits=MotionLimits(effort=0.35, velocity=6.0, lower=-math.pi, upper=math.pi),
        meta={"mechanism": "knurled handle"},
    )
    return [joint]


def _handle_style_fixed_cap_build(model, r, mats, head: _Head) -> list[str]:
    """004 L103-L115: a moulded stem and cap fused into the head, no joint."""
    stem = 0.0180 * r.head_scale
    # 004 builds this as one extruded ``handle_profile`` plate capped by a
    # turned cylinder (model.py:L92-L110); it was three stacked boxes here.
    _plate(
        head.part,
        _tapered_bar_profile(
            (0.0, head.crown_z - _WELD),
            (0.0, head.crown_z + stem),
            0.0090,
            0.0072,
        ),
        0.0050,
        (0.0, 0.0, 0.0),
        mats["head"],
        "handle_stem",
        _PLATE_RPY,
    )
    # A moulded dome cap, turned rather than a flat disc.
    cap_r = 0.0062 * r.head_scale
    _mesh(
        head.part,
        LatheGeometry(
            [
                (0.0, -0.0025),
                (cap_r, -0.0025),
                (cap_r, 0.0008),
                (cap_r * 0.72, 0.0026),
                (0.0, 0.0030),
            ],
            segments=40,
        ),
        (0.0, 0.0, head.crown_z + stem + 0.0022),
        mats["grip"],
        "handle_cap",
    )
    return []


_HANDLE_BUILDERS = {
    "spin_grip": _handle_style_spin_grip_build,
    "knurled_handle": _handle_style_knurled_handle_build,
    "fixed_cap": _handle_style_fixed_cap_build,
}


# --------------------------------------------------------------------------- #
# Assembly
# --------------------------------------------------------------------------- #
def build_pictureX_0611_drawing_compass_with_adjustable_legs(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_drawing_compass_with_adjustable_legs",
            "identified_object": "drawing compass with adjustable legs",
            "slot_choices": slot_choices_for_config(r),
            "source_layout": (
                "a head hub, two hinged legs, a radius adjuster, a centre point and a lead holder"
            ),
        },
    )
    mats = _materials(model, r)
    head = _HEAD_BUILDERS[r.head_style](model, r, mats)
    needle = _LEG_BUILDERS[r.leg_style](model, r, mats, head, -1.0)
    lead = _LEG_BUILDERS[r.leg_style](model, r, mats, head, 1.0)
    _ADJUSTER_BUILDERS[r.adjuster_style](model, r, mats, head, needle, lead)
    _NEEDLE_BUILDERS[r.needle_end_style](model, r, mats, needle)
    _LEAD_BUILDERS[r.lead_end_style](model, r, mats, lead)
    _HANDLE_BUILDERS[r.handle_style](model, r, mats, head)
    return model


# --------------------------------------------------------------------------- #
# Author tests / category anchors
# --------------------------------------------------------------------------- #
def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def _meshes_materialized(model: ArticulatedObject) -> bool:
    """False while the preflight probe stands in for real mesh assets."""
    for part in model.parts:
        for visual in getattr(part, "visuals", []):
            filename = getattr(getattr(visual, "geometry", None), "filename", None)
            if filename and "__preflight_probe__" in str(filename):
                return False
    return True


def run_pictureX_0611_drawing_compass_with_adjustable_legs_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    heads = _parts_by_role(model, "head")
    legs = _parts_by_role(model, "leg")
    adjusters = _parts_by_role(model, "adjuster")

    ctx.check(
        "category_anchor: one head hub carries the instrument",
        len(heads) == 1,
        details=f"head parts={[part.name for part in heads]}",
    )
    ctx.check(
        "category_anchor: exactly two legs hinge on the head pivot",
        len(legs) == 2,
        details=f"leg parts={[part.name for part in legs]}",
    )
    hinges = [
        joint for joint in model.articulations if joint.meta.get("mechanism") == "compass leg hinge"
    ]
    ctx.check(
        "category_anchor: both leg hinges are revolute on the shared pivot axis",
        len(hinges) == 2
        and all(joint.articulation_type == ArticulationType.REVOLUTE for joint in hinges)
        and all(abs(joint.axis[1]) > 0.99 for joint in hinges),
        details=f"hinges={[(joint.name, joint.axis) for joint in hinges]}",
    )
    ctx.check(
        "category_anchor: a radius adjuster links the legs or the head",
        len(adjusters) == 1,
        details=f"adjuster parts={[part.name for part in adjusters]}",
    )

    needle_legs = [part for part in legs if part.meta.get("side") == "needle"]
    lead_legs = [part for part in legs if part.meta.get("side") == "lead"]
    ctx.check(
        "category_anchor: the centre point and the lead end sit on opposite legs",
        len(needle_legs) == 1 and len(lead_legs) == 1,
        details=(
            f"needle_leg={[part.name for part in needle_legs]}, "
            f"lead_leg={[part.name for part in lead_legs]}"
        ),
    )

    # Opening either leg must widen the drawing radius: the tip really travels.
    for hinge in hinges:
        child = model.get_part(hinge.child)
        rest = ctx.part_world_aabb(child)
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            opened = ctx.part_world_aabb(child)
        moved = None
        if rest is not None and opened is not None:
            moved = abs((opened[0][0] + opened[1][0]) / 2.0 - (rest[0][0] + rest[1][0]) / 2.0)
        ctx.check(
            f"{hinge.name} opens the leg outward",
            moved is not None and moved > 0.002,
            details=f"rest={rest}, opened={opened}, moved={moved}",
        )

    knees = [
        joint for joint in model.articulations if joint.meta.get("mechanism") == "folding leg knee"
    ]
    if r.leg_style == "folding_knee":
        ctx.check(
            "category_anchor: a folding leg has a real knee joint per leg",
            len(knees) == 2
            and all(joint.articulation_type == ArticulationType.REVOLUTE for joint in knees),
            details=f"knees={[joint.name for joint in knees]}",
        )

    if r.lead_end_style == "extension_rail":
        rail = next(joint for joint in model.articulations if joint.name.endswith("__extend"))
        child = model.get_part(rail.child)
        retracted = ctx.part_world_aabb(child)
        with ctx.pose({rail: rail.motion_limits.upper}):
            extended = ctx.part_world_aabb(child)
        ctx.check(
            "the extension rail lengthens the drawing radius",
            retracted is not None
            and extended is not None
            and abs(extended[0][2] - retracted[0][2]) > 0.4 * rail.motion_limits.upper,
            details=f"retracted={retracted}, extended={extended}",
        )

    if r.needle_end_style == "collet_cartridge":
        insert = next(joint for joint in model.articulations if joint.name.endswith("__insert"))
        child = model.get_part(insert.child)
        seated = ctx.part_world_aabb(child)
        with ctx.pose({insert: insert.motion_limits.upper}):
            pushed = ctx.part_world_aabb(child)
        ctx.check(
            "the needle cartridge really slides in its collet",
            seated is not None
            and pushed is not None
            and abs(pushed[0][2] - seated[0][2]) > 0.4 * insert.motion_limits.upper,
            details=f"seated={seated}, pushed={pushed}",
        )

        # --- surface relation: the cartridge seats through the collet mouth ---
        host = model.get_part(insert.parent)
        mouth = PlaneInterface(
            point=(0.0, 0.0, insert.origin.xyz[2] + 0.0020),
            normal=(0.0, 0.0, -1.0),
            tangent_u=(1.0, 0.0, 0.0),
            extent=(0.0064, 0.0064),
            name="collet_mouth",
        )
        cartridge_ok = True
        # Each projection names the element it is really about: the widest
        # section against the bore, and the tip against the mouth plane. A
        # whole-part AABB would be inflated by the leg's own tilt.
        with ctx.pose({insert: insert.motion_limits.upper}):
            cartridge_ok &= ctx.expect_footprint_within(
                child,
                elem="cartridge_shoulder",
                frame=mouth,
                frame_part=host,
                name="the cartridge shoulder stays inside the collet bore at full insertion",
            )
            cartridge_ok &= ctx.expect_normal_band(
                child,
                elem="needle_point",
                frame=mouth,
                frame_part=host,
                minimum=-0.0060,
                maximum=0.0120,
                minimum_protrusion=0.0080,
                name="the needle still protrudes past the collet at full insertion",
            )
        ctx.check(
            "category_anchor: the needle cartridge keeps its point proud of the collet",
            cartridge_ok,
            details=f"insert_travel={insert.motion_limits.upper}, mouth_extent={mouth.extent}",
        )

    ctx.check(
        "the legs are stacked side by side on the shared pin",
        r.leg_offset_y_m > r.leg_thickness_m / 2.0,
        details=f"offset={r.leg_offset_y_m:.5f}, thickness={r.leg_thickness_m:.5f}",
    )
    ctx.check(
        "the drawing radius follows the leg length and opening angle",
        r.tip_span_m > 0.020,
        details=f"tip_span={r.tip_span_m:.4f}",
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "cheeked_head_largest_scale_bow_spreader",
        {
            "head_style": "cheeked_horseshoe",
            "leg_style": "tubular",
            "adjuster_style": "bow_spreader",
            "lead_end_style": "extension_rail",
            "needle_end_style": "collet_cartridge",
            "handle_style": "knurled_handle",
            "leg_length_m": 0.190,
            "open_angle_rad": 0.40,
            "head_scale": 1.30,
            "leg_thickness_m": 0.0060,
            "adjuster_station_ratio": 0.45,
        },
        reason="the flared pivot cheeks reach furthest out at the largest head scale and widest opening",
    ),
    corner_case(
        "longest_legs_widest_open_cross_screw",
        {
            "head_style": "horseshoe_ring",
            "leg_style": "sheet_taper",
            "adjuster_style": "cross_screw",
            "lead_end_style": "extension_rail",
            "needle_end_style": "collet_cartridge",
            "handle_style": "spin_grip",
            "leg_length_m": 0.190,
            "open_angle_rad": 0.40,
            "head_scale": 1.30,
            "leg_thickness_m": 0.0060,
            "adjuster_station_ratio": 0.45,
        },
        reason="longest legs at the widest opening with the deepest adjuster station",
    ),
    corner_case(
        "shortest_legs_tight_open_rack_pinion",
        {
            "head_style": "plate_yoke",
            "leg_style": "folding_knee",
            "adjuster_style": "rack_pinion",
            "lead_end_style": "pen_adapter",
            "needle_end_style": "fixed_needle",
            "handle_style": "fixed_cap",
            "leg_length_m": 0.100,
            "open_angle_rad": 0.14,
            "head_scale": 0.85,
            "leg_thickness_m": 0.0024,
            "adjuster_station_ratio": 0.20,
        },
        reason="smallest instrument where the rack radius and the folding knee collide",
    ),
    corner_case(
        "ratchet_quadrant_on_folding_legs",
        {
            "head_style": "spring_bow",
            "leg_style": "folding_knee",
            "adjuster_style": "ratchet_quadrant",
            "lead_end_style": "hinged_holder",
            "needle_end_style": "collet_cartridge",
            "handle_style": "knurled_handle",
            "leg_length_m": 0.185,
            "open_angle_rad": 0.38,
            "head_scale": 1.25,
            "leg_thickness_m": 0.0056,
            "adjuster_station_ratio": 0.44,
        },
        reason="three-part ratchet reaching across the widest gap on two-section legs",
    ),
    corner_case(
        "bow_spreader_thin_tubular_legs",
        {
            "head_style": "spring_bow",
            "leg_style": "tubular",
            "adjuster_style": "bow_spreader",
            "lead_end_style": "rotating_collet",
            "needle_end_style": "fixed_needle",
            "handle_style": "spin_grip",
            "leg_length_m": 0.105,
            "open_angle_rad": 0.16,
            "head_scale": 0.88,
            "leg_thickness_m": 0.0024,
            "adjuster_station_ratio": 0.21,
        },
        reason="the head spreader reaches down between the thinnest closed tube legs",
    ),
    corner_case(
        "center_spindle_widest_span",
        {
            "head_style": "disk_hub",
            "leg_style": "plate_profile",
            "adjuster_style": "center_spindle",
            "lead_end_style": "fixed_collet",
            "needle_end_style": "fixed_needle",
            "handle_style": "knurled_handle",
            "leg_length_m": 0.190,
            "open_angle_rad": 0.40,
            "head_scale": 0.85,
            "leg_thickness_m": 0.0060,
            "adjuster_station_ratio": 0.45,
        },
        reason="the centred spindle spans the widest leg gap on the smallest head",
    ),
    corner_case(
        "head_wheel_deep_station_pen_adapter",
        {
            "head_style": "disk_hub",
            "leg_style": "tubular",
            "adjuster_style": "head_wheel",
            "lead_end_style": "pen_adapter",
            "needle_end_style": "collet_cartridge",
            "handle_style": "fixed_cap",
            "leg_length_m": 0.188,
            "open_angle_rad": 0.15,
            "head_scale": 1.30,
            "leg_thickness_m": 0.0026,
            "adjuster_station_ratio": 0.45,
        },
        reason="the longest head spine hangs between nearly closed legs",
    ),
    corner_case(
        "quick_set_wheel_extension_rail",
        {
            "head_style": "horseshoe_ring",
            "leg_style": "plate_profile",
            "adjuster_style": "center_wheel",
            "lead_end_style": "extension_rail",
            "needle_end_style": "fixed_needle",
            "handle_style": "knurled_handle",
            "leg_length_m": 0.150,
            "open_angle_rad": 0.30,
            "head_scale": 1.05,
            "leg_thickness_m": 0.0040,
            "adjuster_station_ratio": 0.40,
        },
        reason="the quick-set wheel and the extension rail share the lead leg",
    ),
    corner_case(
        "side_link_wheel_folding_knee",
        {
            "head_style": "plate_yoke",
            "leg_style": "folding_knee",
            "adjuster_style": "side_link_wheel",
            "lead_end_style": "rotating_collet",
            "needle_end_style": "collet_cartridge",
            "handle_style": "spin_grip",
            "leg_length_m": 0.120,
            "open_angle_rad": 0.36,
            "head_scale": 0.95,
            "leg_thickness_m": 0.0030,
            "adjuster_station_ratio": 0.22,
        },
        reason="the swinging side link works just above a knee on short folding legs",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_pictureX_0611_drawing_compass_with_adjustable_legs",
    "config_from_seed",
    "resolve_config",
    "run_pictureX_0611_drawing_compass_with_adjustable_legs_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
