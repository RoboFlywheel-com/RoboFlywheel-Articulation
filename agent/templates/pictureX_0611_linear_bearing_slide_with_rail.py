# SPDX-License-Identifier: Apache-2.0

"""Self-contained linear bearing slide with rail.

One fixed guide rail carries N bearing carriages that translate genuinely end-to-end
along the rail X axis.  The template is the only runtime truth: no source runtime, no
snapshot, no other template is imported.

Mechanical contract (see articraft_template_authoring/MECHANICAL_PRIORS.md Sec.6):

* the prismatic axis is the true travel direction and both limits are real;
* the carriage never nests a solid block around a solid rail -- it is an open bore
  (round shaft) or a stepped open channel (profile rail) whose cavity clears the rail
  by 1.2 mm on every face at every travel position;
* captured contact is made by discrete bearing balls that penetrate the rail race by
  0.6 mm.  A sphere has an orientation-invariant AABB and the penetrated axis' AABB
  intersection depth is exactly the penetration, so the pair reads as connected for
  ``fail_if_isolated_parts`` while staying below the overlap tolerance.  No
  ``allow_overlap`` is used anywhere.
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
    Cylinder,
    MotionLimits,
    MotionProperties,
    Origin,
    PlaneInterface,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_planes,
    mesh_from_cadquery,
    multiplicity_slot,
)

RailProfile = Literal["round_shaft", "profile_rail"]
CarriageBlock = Literal["plain_block", "top_flanged_block", "pedestal_plate_block"]
RailMount = Literal["continuous_base_plate", "end_pillow_feet"]
EndTreatment = Literal["open_ends", "capped_end_stops"]
PaletteStyle = Literal["satin_aluminium", "black_anodised", "galvanised", "warm_bronze"]


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("rail_profile", ("round_shaft", "profile_rail")),
        component_slot(
            "carriage_block",
            ("plain_block", "top_flanged_block", "pedestal_plate_block"),
        ),
        component_slot("rail_mount", ("continuous_base_plate", "end_pillow_feet")),
        component_slot("end_treatment", ("open_ends", "capped_end_stops")),
        multiplicity_slot("carriage_count", (1, 2, 3), item_slot="carriage_block"),
    )
)


# ---------------------------------------------------------------------------
# fixed cross-section constants taken from the source records
# ---------------------------------------------------------------------------

# rail_mount
PLATE_W = 0.052
PLATE_T = 0.010
FOOT_LEN = 0.036
FOOT_W = 0.072
FOOT_T = 0.018

# rail_profile = round_shaft (rec ...__002__png, model.py:L20-L106)
SHAFT_R = 0.0085
NECK_W = 0.014
NECK_H = 0.012
SHOULDER_W = 0.013
SHOULDER_H = 0.004
SHOULDER_Y = 0.0115

# rail_profile = profile_rail (rec ...101211, model.py:L19-L45)
BASE_W = 0.026
BASE_T = 0.005
CROWN_W = 0.016
CROWN_H = 0.008
GROOVE_D = 0.0012

# bearing balls -- the only cross-part contact in the model
BALL_R = 0.0022
BALL_BITE = 0.0006

# carriage envelopes
ROUND_CARRIAGE_W = 0.048
ROUND_CARRIAGE_H = 0.034
ROUND_BORE_CLEAR = 0.0012
PROFILE_CARRIAGE_W = 0.046
PROFILE_WEB_T = 0.010
CHANNEL_CLEAR = 0.0012

# travel bookkeeping
SEAL_PROUD = 0.003
FLANGE_PROUD_X = 0.003
INTER_CARRIAGE_GAP = 0.004
MIN_TRAVEL = 0.010
OPEN_END_MARGIN = 0.008
STOP_T = 0.005
STOP_INSET = 0.007
STOP_CLEAR = 0.004


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "satin_aluminium": {
        "mount": (0.70, 0.72, 0.74, 1.0),
        "rail": (0.80, 0.82, 0.84, 1.0),
        "block": (0.72, 0.75, 0.77, 1.0),
        "seal": (0.035, 0.038, 0.042, 1.0),
        "ball": (0.86, 0.88, 0.90, 1.0),
        "screw": (0.20, 0.22, 0.24, 1.0),
        "accent": (0.62, 0.43, 0.16, 1.0),
    },
    "black_anodised": {
        "mount": (0.16, 0.17, 0.18, 1.0),
        "rail": (0.62, 0.65, 0.67, 1.0),
        "block": (0.11, 0.12, 0.13, 1.0),
        "seal": (0.03, 0.03, 0.035, 1.0),
        "ball": (0.84, 0.86, 0.88, 1.0),
        "screw": (0.55, 0.57, 0.59, 1.0),
        "accent": (0.55, 0.05, 0.04, 1.0),
    },
    "galvanised": {
        "mount": (0.63, 0.67, 0.68, 1.0),
        "rail": (0.68, 0.70, 0.72, 1.0),
        "block": (0.56, 0.58, 0.61, 1.0),
        "seal": (0.055, 0.060, 0.065, 1.0),
        "ball": (0.88, 0.90, 0.92, 1.0),
        "screw": (0.08, 0.09, 0.10, 1.0),
        "accent": (0.48, 0.34, 0.16, 1.0),
    },
    "warm_bronze": {
        "mount": (0.46, 0.38, 0.26, 1.0),
        "rail": (0.74, 0.70, 0.62, 1.0),
        "block": (0.58, 0.48, 0.32, 1.0),
        "seal": (0.06, 0.05, 0.04, 1.0),
        "ball": (0.82, 0.84, 0.86, 1.0),
        "screw": (0.24, 0.20, 0.16, 1.0),
        "accent": (0.72, 0.48, 0.12, 1.0),
    },
}


@dataclass(frozen=True)
class Config:
    rail_profile: RailProfile = "round_shaft"
    carriage_block: CarriageBlock = "plain_block"
    rail_mount: RailMount = "continuous_base_plate"
    end_treatment: EndTreatment = "open_ends"
    carriage_count: int = 2
    rail_length_m: float = 0.400
    carriage_length_m: float = 0.052
    palette_style: PaletteStyle = "satin_aluminium"
    name: str = "picturex_0611_linear_bearing_slide_with_rail"


@dataclass(frozen=True)
class ResolvedConfig:
    rail_profile: RailProfile
    carriage_block: CarriageBlock
    rail_mount: RailMount
    end_treatment: EndTreatment
    carriage_count: int
    rail_length_m: float
    carriage_length_m: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    # rail_mount derivations
    mount_top_z: float
    # rail_profile derivations
    rib_top_z: float
    shaft_z: float
    rail_base_top_z: float
    seat_z: float
    contact_width: float
    # carriage derivations (local frame -- z = 0 is the seat plane)
    carriage_length: float
    carriage_width: float
    carriage_bottom_local: float
    carriage_top_local: float
    bore_radius: float
    ball_offset_local: tuple[float, ...]
    ball_x_local: float
    # travel derivations
    carriage_footprint_x: float
    end_margin: float
    usable_half: float
    zone_len: float
    home_x: tuple[float, ...]
    travel: float
    stop_top_z: float
    name: str


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x4C49_4E42_5241_494C)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        rail_profile=choices["rail_profile"],
        carriage_block=choices["carriage_block"],
        rail_mount=choices["rail_mount"],
        end_treatment=choices["end_treatment"],
        carriage_count=choices["carriage_count"],
        rail_length_m=round(rng.uniform(0.30, 0.50), 4),
        carriage_length_m=round(rng.uniform(0.030, 0.064), 4),
        palette_style=rng.choice(tuple(PALETTES)),
        name=f"linear_bearing_slide_with_rail_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "rail_profile": config.rail_profile,
            "carriage_block": config.carriage_block,
            "rail_mount": config.rail_mount,
            "end_treatment": config.end_treatment,
            "carriage_count": config.carriage_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")

    rail_length = _clamp(config.rail_length_m, 0.30, 0.50)
    requested_carriage_length = _clamp(config.carriage_length_m, 0.030, 0.064)
    count = int(config.carriage_count)

    # rail_mount -> the single height every other structure is derived from.
    mount_top_z = PLATE_T if config.rail_mount == "continuous_base_plate" else FOOT_T

    # rail_profile -> race height and the load-carrying seat plane.
    if config.rail_profile == "round_shaft":
        rib_top_z = mount_top_z + NECK_H
        shaft_z = rib_top_z + 0.4 * SHAFT_R
        rail_base_top_z = mount_top_z
        seat_z = shaft_z + SHAFT_R
        contact_width = 2.0 * SHAFT_R
    else:
        rib_top_z = mount_top_z
        shaft_z = mount_top_z
        rail_base_top_z = mount_top_z + BASE_T
        seat_z = rail_base_top_z + CROWN_H
        contact_width = CROWN_W

    # end_treatment -> how much of the rail the carriages may not enter.
    stop_top_z = seat_z + 0.006
    if config.end_treatment == "capped_end_stops":
        end_margin = STOP_INSET + STOP_T * 0.5 + STOP_CLEAR
    else:
        end_margin = OPEN_END_MARGIN
    usable_half = rail_length * 0.5 - end_margin
    zone_len = 2.0 * usable_half / float(count)

    # host capacity: the block may never be longer than its own travel zone allows.
    flange_extra = FLANGE_PROUD_X * 2.0 if config.carriage_block == "top_flanged_block" else 0.0
    max_length = zone_len - INTER_CARRIAGE_GAP - 2.0 * MIN_TRAVEL - SEAL_PROUD * 2.0 - flange_extra
    carriage_length = min(requested_carriage_length, max_length)
    if carriage_length < 0.020:
        raise ValueError(
            f"rail_length={rail_length:.4f} cannot host {count} carriages (zone={zone_len:.4f})"
        )
    footprint = carriage_length + SEAL_PROUD * 2.0 + flange_extra

    travel = (zone_len - footprint - INTER_CARRIAGE_GAP) * 0.5
    home_x = tuple(-usable_half + zone_len * (index + 0.5) for index in range(count))

    # carriage local frame: z = 0 is the seat plane (shaft crest / crown top).
    if config.rail_profile == "round_shaft":
        carriage_width = ROUND_CARRIAGE_W
        carriage_bottom_local = (mount_top_z + SHOULDER_H + 0.0015) - seat_z
        carriage_top_local = carriage_bottom_local + ROUND_CARRIAGE_H
        bore_radius = SHAFT_R + ROUND_BORE_CLEAR
        # one ball at the crest of the bore per end of the block
        ball_offset_local = (0.0,)
    else:
        carriage_width = PROFILE_CARRIAGE_W
        carriage_bottom_local = (mount_top_z + 0.0015) - seat_z
        carriage_top_local = rail_base_top_z - seat_z + CROWN_H + CHANNEL_CLEAR + PROFILE_WEB_T
        bore_radius = 0.0
        ball_y = CROWN_W * 0.5 + BALL_R - BALL_BITE
        ball_offset_local = (-ball_y, ball_y)
    ball_x_local = max(carriage_length * 0.5 - 0.008, carriage_length * 0.25)

    return ResolvedConfig(
        rail_profile=config.rail_profile,
        carriage_block=config.carriage_block,
        rail_mount=config.rail_mount,
        end_treatment=config.end_treatment,
        carriage_count=count,
        rail_length_m=rail_length,
        carriage_length_m=requested_carriage_length,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        mount_top_z=mount_top_z,
        rib_top_z=rib_top_z,
        shaft_z=shaft_z,
        rail_base_top_z=rail_base_top_z,
        seat_z=seat_z,
        contact_width=contact_width,
        carriage_length=carriage_length,
        carriage_width=carriage_width,
        carriage_bottom_local=carriage_bottom_local,
        carriage_top_local=carriage_top_local,
        bore_radius=bore_radius,
        ball_offset_local=ball_offset_local,
        ball_x_local=ball_x_local,
        carriage_footprint_x=footprint,
        end_margin=end_margin,
        usable_half=usable_half,
        zone_len=zone_len,
        home_x=home_x,
        travel=travel,
        stop_top_z=stop_top_z,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> dict[str, object]:
    return {
        "rail_profile": config.rail_profile,
        "carriage_block": config.carriage_block,
        "rail_mount": config.rail_mount,
        "end_treatment": config.end_treatment,
        "carriage_count": config.carriage_count,
    }


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, object]:
    return {
        key: model.material(f"{r.palette_style}_{key}", rgba=rgba)
        for key, rgba in r.palette.items()
    }


def _slab(size: tuple[float, float, float], center: tuple[float, float, float]) -> cq.Workplane:
    return cq.Workplane("XY").box(*size).translate(center)


def _hole_stations(length: float, pitch: float) -> tuple[float, ...]:
    usable = length - 0.030
    count = max(2, int(usable / pitch) + 1)
    step = usable / float(count - 1)
    return tuple(-usable * 0.5 + step * index for index in range(count))


# ---------------------------------------------------------------------------
# rail_mount candidates
# ---------------------------------------------------------------------------


def _rail_mount_continuous_base_plate_build(part, r: ResolvedConfig, mats) -> None:
    """One full-length plate under the whole rail (rec ...__002__png model.py:L45-L49)."""

    plate = _slab((r.rail_length_m, PLATE_W, PLATE_T), (0.0, 0.0, PLATE_T * 0.5))
    for index, x in enumerate(_hole_stations(r.rail_length_m, 0.060)):
        side = -1.0 if index % 2 == 0 else 1.0
        y = side * (PLATE_W * 0.5 - 0.008)
        plate = plate.cut(
            cq.Workplane("XY", origin=(x, y, -0.002)).circle(0.0024).extrude(PLATE_T + 0.004)
        )
        plate = plate.cut(
            cq.Workplane("XY", origin=(x, y, PLATE_T - 0.0026)).circle(0.0042).extrude(0.006)
        )
    part.visual(
        mesh_from_cadquery(plate, "rail_mount_base_plate", tolerance=0.0005),
        material=mats["mount"],
        name="rail_mount__continuous_base_plate__plate", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "galvanised", "warm_bronze"} else "metal.blackened_gunmetal"),
    )


def _rail_mount_end_pillow_feet_build(part, r: ResolvedConfig, mats) -> None:
    """Two discrete transverse feet, rail bridging open air between them
    (rec ...101508 model.py:L173-L180)."""

    foot_x = r.rail_length_m * 0.5 - FOOT_LEN * 0.5
    for index, sign in enumerate((-1.0, 1.0)):
        foot = _slab((FOOT_LEN, FOOT_W, FOOT_T), (sign * foot_x, 0.0, FOOT_T * 0.5))
        for hole_y in (-FOOT_W * 0.5 + 0.008, FOOT_W * 0.5 - 0.008):
            foot = foot.cut(
                cq.Workplane("XY", origin=(sign * foot_x, hole_y, -0.002))
                .circle(0.0026)
                .extrude(FOOT_T + 0.004)
            )
            foot = foot.cut(
                cq.Workplane("XY", origin=(sign * foot_x, hole_y, FOOT_T - 0.0030))
                .circle(0.0046)
                .extrude(0.006)
            )
        part.visual(
            mesh_from_cadquery(foot, f"rail_mount_pillow_foot_{index}", tolerance=0.0005),
            material=mats["mount"],
            name=f"rail_mount__end_pillow_feet__foot_{index}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "galvanised", "warm_bronze"} else "metal.blackened_gunmetal"),
        )


_RAIL_MOUNT_BUILDERS = {
    "continuous_base_plate": _rail_mount_continuous_base_plate_build,
    "end_pillow_feet": _rail_mount_end_pillow_feet_build,
}


# ---------------------------------------------------------------------------
# rail_profile candidates -- rail side
# ---------------------------------------------------------------------------


def _rail_profile_round_shaft_build(part, r: ResolvedConfig, mats) -> None:
    """Supported round rail: neck rib + shoulder strips + hardened shaft
    (rec ...__002__png model.py:L39-L106, L260-L283)."""

    rib = _slab(
        (r.rail_length_m, NECK_W, NECK_H + 0.0010),
        (0.0, 0.0, r.mount_top_z + NECK_H * 0.5 - 0.0005),
    )
    for sign in (-1.0, 1.0):
        rib = rib.union(
            _slab(
                (r.rail_length_m, SHOULDER_W, SHOULDER_H),
                (0.0, sign * SHOULDER_Y, r.mount_top_z + SHOULDER_H * 0.5),
            )
        )
    part.visual(
        mesh_from_cadquery(rib, "round_shaft_support_extrusion", tolerance=0.0006),
        material=mats["mount"],
        name="rail_profile__round_shaft__support_extrusion", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "galvanised", "warm_bronze"} else "metal.blackened_gunmetal"),
    )
    # The shaft stays a separate element so the grazed race AABB is the shaft itself.
    part.visual(
        Cylinder(radius=SHAFT_R, length=r.rail_length_m - 0.014),
        origin=Origin(xyz=(0.0, 0.0, r.shaft_z), rpy=(0.0, math.pi * 0.5, 0.0)),
        material=mats["rail"],
        name="rail_profile__round_shaft__shaft", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
    )
    for index, x in enumerate(_hole_stations(r.rail_length_m, 0.095)):
        part.visual(
            Cylinder(radius=0.0030, length=0.0012),
            origin=Origin(xyz=(x, SHOULDER_Y, r.mount_top_z + SHOULDER_H)),
            material=mats["screw"],
            name=f"rail_profile__round_shaft__support_screw_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
        )


def _rail_profile_profile_rail_build(part, r: ResolvedConfig, mats) -> None:
    """Profiled crown rail: rectangular base + grooved crown
    (rec ...101211 model.py:L19-L45, rec ...101220 model.py:L27-L66)."""

    base = _slab(
        (r.rail_length_m, BASE_W, BASE_T),
        (0.0, 0.0, r.mount_top_z + BASE_T * 0.5),
    )
    for x in _hole_stations(r.rail_length_m, 0.045):
        base = base.cut(
            cq.Workplane("XY", origin=(x, 0.0, r.mount_top_z - 0.002))
            .circle(0.0018)
            .extrude(BASE_T + 0.004)
        )
        base = base.cut(
            cq.Workplane("XY", origin=(x, 0.0, r.mount_top_z + BASE_T - 0.0018))
            .circle(0.0031)
            .extrude(0.004)
        )
    part.visual(
        mesh_from_cadquery(base, "profile_rail_base", tolerance=0.0005),
        material=mats["rail"],
        name="rail_profile__profile_rail__base", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
    )

    crown_bottom = r.rail_base_top_z - 0.0006
    crown = _slab(
        (r.rail_length_m, CROWN_W, CROWN_H + 0.0006),
        (0.0, 0.0, crown_bottom + (CROWN_H + 0.0006) * 0.5),
    )
    # long shallow race reliefs on both flanks, below the ball track
    for sign in (-1.0, 1.0):
        crown = crown.cut(
            _slab(
                (r.rail_length_m + 0.002, GROOVE_D * 2.0, 0.0020),
                (0.0, sign * CROWN_W * 0.5, r.rail_base_top_z + 0.0025),
            )
        )
    part.visual(
        mesh_from_cadquery(crown, "profile_rail_crown", tolerance=0.0004),
        material=mats["rail"],
        name="rail_profile__profile_rail__crown", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
    )
    # Counterbored socket heads sit in the crown top surface: they straddle it so the
    # element is a real part of the rail body, and their 0.3 mm proud head stays inside
    # the carriage channel clearance.
    for index, x in enumerate(_hole_stations(r.rail_length_m, 0.090)):
        part.visual(
            Cylinder(radius=0.0028, length=0.0010),
            origin=Origin(xyz=(x, 0.0, r.seat_z - 0.0002)),
            material=mats["screw"],
            name=f"rail_profile__profile_rail__mount_screw_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
        )


_RAIL_PROFILE_BUILDERS = {
    "round_shaft": _rail_profile_round_shaft_build,
    "profile_rail": _rail_profile_profile_rail_build,
}


# ---------------------------------------------------------------------------
# end_treatment candidates
# ---------------------------------------------------------------------------


def _end_treatment_open_ends_build(part, r: ResolvedConfig, mats) -> None:
    """Bare rail ends -- travel is bounded only by the rail itself
    (rec ...101211 model.py:L19-L45)."""

    return None


def _end_treatment_capped_end_stops_build(part, r: ResolvedConfig, mats) -> None:
    """Physical end-stop blocks at both rail ends (rec ...101508 model.py:L165-L171)."""

    stop_x = r.rail_length_m * 0.5 - STOP_INSET
    stop_h = r.stop_top_z - r.mount_top_z
    for index, sign in enumerate((-1.0, 1.0)):
        part.visual(
            Box((STOP_T, 0.030, stop_h)),
            origin=Origin(xyz=(sign * stop_x, 0.0, r.mount_top_z + stop_h * 0.5)),
            material=mats["screw"],
            name=f"end_treatment__capped_end_stops__stop_{index}", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
        )
    # End-of-travel sensor cantilevered OUTBOARD of the negative-x stop.  It stays
    # entirely beyond the rail end, so no carriage can ever reach it.
    bracket_x = -(r.rail_length_m * 0.5) - 0.006
    part.visual(
        Box((0.026, 0.030, 0.005)),
        origin=Origin(xyz=(bracket_x, 0.0, r.mount_top_z + 0.008)),
        material=mats["mount"],
        name="end_treatment__capped_end_stops__sensor_bracket", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "galvanised", "warm_bronze"} else "metal.blackened_gunmetal"),
    )
    part.visual(
        Box((0.014, 0.020, 0.016)),
        origin=Origin(xyz=(bracket_x - 0.005, 0.0, r.mount_top_z + 0.016)),
        material=mats["seal"],
        name="end_treatment__capped_end_stops__limit_sensor", material_class_id="tech.control_interface",
    )
    part.visual(
        Box((0.010, 0.0016, 0.008)),
        origin=Origin(xyz=(bracket_x - 0.005, -0.0108, r.mount_top_z + 0.016)),
        material=mats["accent"],
        name="end_treatment__capped_end_stops__sensor_label", material_class_id="plastic.opaque_glossy_molded",
    )


_END_TREATMENT_BUILDERS = {
    "open_ends": _end_treatment_open_ends_build,
    "capped_end_stops": _end_treatment_capped_end_stops_build,
}


# ---------------------------------------------------------------------------
# carriage shells (rail_profile owns the capture cavity)
# ---------------------------------------------------------------------------


def _round_shaft_shell(r: ResolvedConfig) -> cq.Workplane:
    """Open-bottom bearing housing with a true bore and support-rib slot
    (rec ...__002__png model.py:L109-L156)."""

    length = r.carriage_length
    height = r.carriage_top_local - r.carriage_bottom_local
    body = (
        cq.Workplane("XY")
        .box(length, r.carriage_width, height)
        .translate((0.0, 0.0, r.carriage_bottom_local + height * 0.5))
        .edges("|Z")
        .fillet(0.0028)
    )
    body = body.cut(
        cq.Workplane("YZ", origin=(0.0, 0.0, -SHAFT_R))
        .circle(r.bore_radius)
        .extrude(length * 0.5 + 0.006, both=True)
    )
    slot_h = 0.030
    body = body.cut(
        _slab(
            (length + 0.010, NECK_W + 2.0 * CHANNEL_CLEAR, slot_h),
            (0.0, 0.0, -SHAFT_R - slot_h * 0.5),
        )
    )
    return body


def _profile_rail_shell(r: ResolvedConfig) -> cq.Workplane:
    """One-piece block with a stepped open channel that clears the whole rail
    (rec ...101220 model.py:L69-L121, rec ...101508 model.py:L50-L73)."""

    length = r.carriage_length
    height = r.carriage_top_local - r.carriage_bottom_local
    body = _slab(
        (length, r.carriage_width, height),
        (0.0, 0.0, r.carriage_bottom_local + height * 0.5),
    )
    lower_top = (r.rail_base_top_z - r.seat_z) + CHANNEL_CLEAR
    lower_h = 0.040
    body = body.cut(
        _slab(
            (length + 0.010, BASE_W + 2.0 * CHANNEL_CLEAR, lower_h),
            (0.0, 0.0, lower_top - lower_h * 0.5),
        )
    )
    upper_bottom = lower_top - 0.0004
    upper_top = CHANNEL_CLEAR
    body = body.cut(
        _slab(
            (length + 0.010, CROWN_W + 2.0 * CHANNEL_CLEAR, upper_top - upper_bottom),
            (0.0, 0.0, (upper_top + upper_bottom) * 0.5),
        )
    )
    return body


_CARRIAGE_SHELLS = {
    "round_shaft": _round_shaft_shell,
    "profile_rail": _profile_rail_shell,
}


# ---------------------------------------------------------------------------
# carriage_block candidates -- what sits on top of the capture shell
# ---------------------------------------------------------------------------


def _carriage_block_plain_block_build(shell: cq.Workplane, r: ResolvedConfig):
    """Compact block, top face flush with the body, four blind bores
    (rec ...__002__png model.py:L131-L141)."""

    top = r.carriage_top_local
    hole_x = r.carriage_length * 0.28
    hole_y = r.carriage_width * 0.28
    for x in (-hole_x, hole_x):
        for y in (-hole_y, hole_y):
            shell = shell.cut(
                cq.Workplane("XY", origin=(x, y, top - 0.0055)).circle(0.0026).extrude(0.009)
            )
    return shell, top, ()


def _carriage_block_top_flanged_block_build(shell: cq.Workplane, r: ResolvedConfig):
    """Integral top flange overhanging the body on all four sides
    (rec ...093549 model.py:L70)."""

    body_top = r.carriage_top_local
    flange_t = 0.008
    flange = _slab(
        (
            r.carriage_length + 2.0 * FLANGE_PROUD_X,
            r.carriage_width + 0.012,
            flange_t + 0.001,
        ),
        (0.0, 0.0, body_top - 0.001 + (flange_t + 0.001) * 0.5),
    )
    shell = shell.union(flange)
    top = body_top + flange_t
    hole_x = r.carriage_length * 0.30
    hole_y = (r.carriage_width + 0.012) * 0.32
    screws = []
    for x in (-hole_x, hole_x):
        for y in (-hole_y, hole_y):
            shell = shell.cut(
                cq.Workplane("XY", origin=(x, y, top - 0.006)).circle(0.0026).extrude(0.009)
            )
            screws.append((x, y, top - 0.0005))
    return shell, top, tuple(screws)


def _carriage_block_pedestal_plate_block_build(shell: cq.Workplane, r: ResolvedConfig):
    """Raised machine plate standing off the shell on a short pedestal riser
    (rec ...101508 model.py:L68-L73)."""

    body_top = r.carriage_top_local
    riser_h = 0.006
    plate_t = 0.004
    riser = _slab(
        (r.carriage_length * 0.55, r.carriage_width * 0.50, riser_h + 0.001),
        (0.0, 0.0, body_top - 0.001 + (riser_h + 0.001) * 0.5),
    )
    plate = _slab(
        (r.carriage_length * 0.86, r.carriage_width * 0.88, plate_t),
        (0.0, 0.0, body_top + riser_h + plate_t * 0.5),
    )
    shell = shell.union(riser).union(plate)
    top = body_top + riser_h + plate_t
    hole_x = r.carriage_length * 0.30
    hole_y = r.carriage_width * 0.30
    screws = []
    for x in (-hole_x, hole_x):
        for y in (-hole_y, hole_y):
            screws.append((x, y, top - 0.0005))
    return shell, top, tuple(screws)


_CARRIAGE_BLOCK_BUILDERS = {
    "plain_block": _carriage_block_plain_block_build,
    "top_flanged_block": _carriage_block_top_flanged_block_build,
    "pedestal_plate_block": _carriage_block_pedestal_plate_block_build,
}


def _round_shaft_wiper(r: ResolvedConfig) -> cq.Workplane:
    """C-shaped elastomer wiper, open at the bottom for the support rib
    (rec ...__002__png model.py:L159-L174)."""

    seal = (
        cq.Workplane("YZ", origin=(0.0, 0.0, -SHAFT_R))
        .circle(SHAFT_R + 0.0050)
        .circle(r.bore_radius)
        .extrude(0.0008, both=True)
    )
    seal = seal.cut(
        _slab((0.006, NECK_W + 2.0 * CHANNEL_CLEAR, 0.030), (0.0, 0.0, -SHAFT_R - 0.015))
    )
    seal = seal.cut(_slab((0.006, 0.060, 0.030), (0.0, 0.0, r.carriage_bottom_local - 0.015)))
    return seal


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def _build_guide_rail(model: ArticulatedObject, r: ResolvedConfig, mats):
    part = model.part(
        f"rail_profile__{r.rail_profile}__guide_rail",
        meta={
            "role": "guide_rail",
            "rail_profile": r.rail_profile,
            "rail_mount": r.rail_mount,
            "end_treatment": r.end_treatment,
            "usable_travel_span_m": 2.0 * r.usable_half,
        },
    )
    _RAIL_MOUNT_BUILDERS[r.rail_mount](part, r, mats)
    _RAIL_PROFILE_BUILDERS[r.rail_profile](part, r, mats)
    _END_TREATMENT_BUILDERS[r.end_treatment](part, r, mats)
    return part


def _build_carriage(model, rail, r: ResolvedConfig, mats, *, index: int, shell_mesh, wiper_mesh):
    prefix = f"carriage_block__{r.carriage_block}__carriage_{index}"
    part = model.part(
        prefix,
        meta={
            "role": "bearing_carriage",
            "carriage_index": index,
            "carriage_block": r.carriage_block,
            "rail_profile": r.rail_profile,
        },
    )
    part.visual(shell_mesh, material=mats["block"], name=f"{prefix}__shell", material_class_id=("metal.aluminum_bare" if r.palette_style in {"satin_aluminium", "galvanised", "warm_bronze"} else "metal.blackened_gunmetal"))

    # Bearing balls: the single, real, cross-part contact.  BALL_BITE of penetration
    # into the race keeps the pair connected without any overlap allowance.
    ball_index = 0
    for sign in (-1.0, 1.0):
        for offset in r.ball_offset_local:
            if r.rail_profile == "round_shaft":
                ball_z = -SHAFT_R + (SHAFT_R + BALL_R - BALL_BITE)
                ball_y = offset
            else:
                ball_z = (r.rail_base_top_z - r.seat_z) + 0.0055
                ball_y = offset
            part.visual(
                Sphere(radius=BALL_R),
                origin=Origin(xyz=(sign * r.ball_x_local, ball_y, ball_z)),
                material=mats["ball"],
                name=f"{prefix}__bearing_ball_{ball_index}", material_class_id="metal.chrome_polished",
            )
            ball_index += 1

    if r.rail_profile == "round_shaft":
        for seal_index, sign in enumerate((-1.0, 1.0)):
            part.visual(
                wiper_mesh,
                origin=Origin(xyz=(sign * (r.carriage_length * 0.5 + 0.0004), 0.0, 0.0)),
                material=mats["seal"],
                name=f"{prefix}__end_wiper_{seal_index}", material_class_id="rubber.smooth_plain",
            )
    else:
        wiper_h = 0.010
        for seal_index, sign in enumerate((-1.0, 1.0)):
            part.visual(
                Box((0.0016, r.carriage_width * 0.92, wiper_h)),
                origin=Origin(
                    xyz=(
                        sign * (r.carriage_length * 0.5 + 0.0004),
                        0.0,
                        CHANNEL_CLEAR + wiper_h * 0.5,
                    )
                ),
                material=mats["seal"],
                name=f"{prefix}__end_wiper_{seal_index}", material_class_id="rubber.smooth_plain",
            )

    # grease port -- embedded in the block wall, source hardware on every record
    part.visual(
        Cylinder(radius=0.0024, length=0.006),
        origin=Origin(
            xyz=(0.0, r.carriage_width * 0.5 - 0.0015, r.carriage_bottom_local + 0.006),
            rpy=(math.pi * 0.5, 0.0, 0.0),
        ),
        material=mats["accent"],
        name=f"{prefix}__grease_port", material_class_id=("metal.brass_aged" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.brass_polished"),
    )

    seat = PlaneInterface(
        name=f"rail_profile.{r.rail_profile}.race_seat",
        point=(0.0, 0.0, r.seat_z),
        normal=(0.0, 0.0, 1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(2.0 * r.usable_half, r.contact_width),
    )
    footprint = PlaneInterface(
        name=f"carriage_block.{r.carriage_block}.race_footprint",
        point=(0.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
        tangent_u=(1.0, 0.0, 0.0),
        extent=(r.carriage_footprint_x, r.contact_width * 0.9),
    )
    placement = mate_planes(seat, footprint, uv=(r.home_x[index], 0.0))
    model.articulation(
        f"{prefix}_slide",
        ArticulationType.PRISMATIC,
        parent=rail,
        child=part,
        origin=placement.origin,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=220.0,
            velocity=0.65,
            lower=-r.travel,
            upper=r.travel,
        ),
        motion_properties=MotionProperties(damping=2.0, friction=0.8),
        meta={"mechanism": "recirculating linear bearing translation along the guide rail"},
    )
    return part


def build_picturex_0611_linear_bearing_slide_with_rail(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    config = config or config_from_seed(0)
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _materials(model, r)

    rail = _build_guide_rail(model, r, mats)

    shell = _CARRIAGE_SHELLS[r.rail_profile](r)
    shell, block_top, screw_spots = _CARRIAGE_BLOCK_BUILDERS[r.carriage_block](shell, r)
    shell_mesh = mesh_from_cadquery(
        shell,
        f"carriage_{r.rail_profile}_{r.carriage_block}",
        tolerance=0.00045,
        angular_tolerance=0.08,
    )
    wiper_mesh = (
        mesh_from_cadquery(_round_shaft_wiper(r), "carriage_end_wiper", tolerance=0.0004)
        if r.rail_profile == "round_shaft"
        else None
    )

    carriages = []
    for index in range(r.carriage_count):
        part = _build_carriage(
            model, rail, r, mats, index=index, shell_mesh=shell_mesh, wiper_mesh=wiper_mesh
        )
        for screw_index, (sx, sy, sz) in enumerate(screw_spots):
            part.visual(
                Cylinder(radius=0.0028, length=0.0018),
                origin=Origin(xyz=(sx, sy, sz)),
                material=mats["screw"],
                name=(
                    f"carriage_block__{r.carriage_block}__carriage_{index}__cap_screw_{screw_index}"
                ), material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"satin_aluminium", "black_anodised", "galvanised"} else "metal.bronze_cast"),
            )
        carriages.append(part)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["source_family"] = "pictureX/0611/linear_bearing_slide_with_rail"
    model.meta["carriage_home_x"] = list(r.home_x)
    model.meta["carriage_travel_m"] = r.travel
    model.meta["block_top_local_z"] = block_top
    return model


def build_seeded_picturex_0611_linear_bearing_slide_with_rail(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_picturex_0611_linear_bearing_slide_with_rail(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# author tests -- mesh-free (see AUTHORING.md Sec.5)
# ---------------------------------------------------------------------------


def run_picturex_0611_linear_bearing_slide_with_rail_tests(
    object_model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    parts = {part.name: part for part in object_model.parts}
    joints = {joint.name: joint for joint in object_model.articulations}
    rail_name = f"rail_profile__{r.rail_profile}__guide_rail"
    carriage_names = [
        f"carriage_block__{r.carriage_block}__carriage_{index}" for index in range(r.carriage_count)
    ]

    ctx.check(
        "category_anchor: one guide rail hosts every carriage",
        rail_name in parts
        and parts[rail_name].meta.get("role") == "guide_rail"
        and len(carriage_names) == r.carriage_count
        and all(name in parts for name in carriage_names)
        and all(parts[name].meta.get("role") == "bearing_carriage" for name in carriage_names),
        details=f"parts={sorted(parts)}",
    )

    slide_joints = [joints.get(f"{name}_slide") for name in carriage_names]
    ctx.check(
        "category_anchor: every carriage rides a bounded +X prismatic slide",
        all(
            joint is not None
            and joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == (1.0, 0.0, 0.0)
            and joint.parent == rail_name
            and joint.motion_limits is not None
            and joint.motion_limits.lower < 0.0 < joint.motion_limits.upper
            for joint in slide_joints
        ),
        details=f"joints={[getattr(j, 'name', None) for j in slide_joints]}",
    )
    ctx.check(
        "travel is real and never clamped to the rest pose",
        r.travel >= MIN_TRAVEL
        and all(
            abs(joint.motion_limits.upper - r.travel) < 1e-9
            and abs(joint.motion_limits.lower + r.travel) < 1e-9
            for joint in slide_joints
        ),
        details=f"travel={r.travel:.5f}",
    )

    # the rail capture cavity is genuinely empty: the running clearance is a positive
    # derived quantity for whichever cross-section is active.
    if r.rail_profile == "round_shaft":
        cavity_clearance = r.bore_radius - SHAFT_R
        capture_element = f"rail_profile__{r.rail_profile}__shaft"
    else:
        cavity_clearance = CHANNEL_CLEAR
        capture_element = f"rail_profile__{r.rail_profile}__crown"
    rail_elements = {visual.name for visual in parts[rail_name].visuals}
    ctx.check(
        "category_anchor: the active rail cross-section is modelled, not a placeholder",
        capture_element in rail_elements and cavity_clearance >= 0.0010,
        details=f"clearance={cavity_clearance:.5f}, rail_elements={sorted(rail_elements)}",
    )

    ball_names = [
        f"{carriage_names[0]}__bearing_ball_{index}"
        for index in range(2 * len(r.ball_offset_local))
    ]
    carriage_elements = {visual.name for visual in parts[carriage_names[0]].visuals}
    ctx.check(
        "category_anchor: discrete bearing balls make the captured contact",
        all(name in carriage_elements for name in ball_names)
        and f"{carriage_names[0]}__end_wiper_0" in carriage_elements
        and 0.0 < BALL_BITE < 0.0010,
        details=f"balls={ball_names}, elements={sorted(carriage_elements)}",
    )

    # derived engagement arithmetic (no mesh, no AABB)
    ctx.check(
        "the block cavity clears the rail mount at every travel position",
        r.carriage_bottom_local + r.seat_z > r.mount_top_z,
        details=(
            f"carriage_bottom={r.carriage_bottom_local + r.seat_z:.5f}, "
            f"mount_top={r.mount_top_z:.5f}"
        ),
    )
    ctx.check(
        "each carriage stays fully on the usable rail at both limits",
        r.travel + r.carriage_footprint_x * 0.5 <= r.zone_len * 0.5 + 1e-9
        and r.usable_half + r.end_margin <= r.rail_length_m * 0.5 + 1e-9,
        details=(
            f"travel={r.travel:.5f}, footprint={r.carriage_footprint_x:.5f}, "
            f"zone={r.zone_len:.5f}, usable_half={r.usable_half:.5f}"
        ),
    )
    ctx.check(
        "adjacent carriages keep a positive gap at facing extremes",
        r.zone_len - r.carriage_footprint_x - 2.0 * r.travel >= INTER_CARRIAGE_GAP - 1e-9
        and all(
            r.home_x[index + 1] - r.home_x[index] > r.carriage_footprint_x
            for index in range(r.carriage_count - 1)
        ),
        details=f"home_x={[round(x, 5) for x in r.home_x]}",
    )
    if r.end_treatment == "capped_end_stops":
        ctx.check(
            "end stops physically shorten the usable travel envelope",
            r.usable_half < r.rail_length_m * 0.5 - OPEN_END_MARGIN
            and "end_treatment__capped_end_stops__stop_0" in rail_elements,
            details=f"usable_half={r.usable_half:.5f}",
        )
    else:
        ctx.check(
            "open ends emit no stop hardware",
            not any(name.startswith("end_treatment__capped") for name in rail_elements),
            details=f"rail_elements={sorted(rail_elements)}",
        )

    # measured travel direction: +q must move the carriage along +X and nowhere else.
    first_joint = slide_joints[0]
    first_part = parts[carriage_names[0]]
    home = ctx.part_world_position(first_part)
    with ctx.pose({first_joint: first_joint.motion_limits.upper}):
        extended = ctx.part_world_position(first_part)
    with ctx.pose({first_joint: first_joint.motion_limits.lower}):
        retracted = ctx.part_world_position(first_part)
    ctx.check(
        "positive command extends along the true rail axis",
        home is not None
        and extended is not None
        and retracted is not None
        and extended[0] > home[0] + r.travel * 0.9
        and retracted[0] < home[0] - r.travel * 0.9
        and abs(extended[1] - home[1]) < 1e-6
        and abs(extended[2] - home[2]) < 1e-6,
        details=f"home={home}, extended={extended}, retracted={retracted}",
    )

    ctx.check(
        "domain choices are recorded on the model",
        object_model.meta.get("slot_choices") == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    ctx.fail_if_isolated_parts()
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "shortest_rail_max_carriages_capped",
        {
            "rail_profile": "round_shaft",
            "carriage_block": "top_flanged_block",
            "rail_mount": "end_pillow_feet",
            "end_treatment": "capped_end_stops",
            "carriage_count": 3,
            "rail_length_m": 0.30,
            "carriage_length_m": 0.064,
        },
        reason="tightest travel zones: shortest rail, largest block, stops fitted, max N",
    ),
    corner_case(
        "shortest_rail_max_carriages_profile",
        {
            "rail_profile": "profile_rail",
            "carriage_block": "pedestal_plate_block",
            "rail_mount": "continuous_base_plate",
            "end_treatment": "capped_end_stops",
            "carriage_count": 3,
            "rail_length_m": 0.30,
            "carriage_length_m": 0.064,
        },
        reason="same capacity edge on the profiled crown cross-section",
    ),
    corner_case(
        "longest_rail_single_short_carriage",
        {
            "rail_profile": "profile_rail",
            "carriage_block": "plain_block",
            "rail_mount": "end_pillow_feet",
            "end_treatment": "open_ends",
            "carriage_count": 1,
            "rail_length_m": 0.50,
            "carriage_length_m": 0.030,
        },
        reason="longest stroke: one short block must stay captured at both extremes",
    ),
    corner_case(
        "longest_rail_round_shaft_open",
        {
            "rail_profile": "round_shaft",
            "carriage_block": "pedestal_plate_block",
            "rail_mount": "continuous_base_plate",
            "end_treatment": "open_ends",
            "carriage_count": 1,
            "rail_length_m": 0.50,
            "carriage_length_m": 0.030,
        },
        reason="longest stroke on the round shaft with the tallest block silhouette",
    ),
    corner_case(
        "flanged_round_shaft_pillow_feet_open",
        {
            "rail_profile": "round_shaft",
            "carriage_block": "top_flanged_block",
            "rail_mount": "end_pillow_feet",
            "end_treatment": "open_ends",
            "carriage_count": 2,
            "rail_length_m": 0.34,
            "carriage_length_m": 0.064,
        },
        reason="widest block over the elevated bridging mount with no end stops",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "build_picturex_0611_linear_bearing_slide_with_rail",
    "build_seeded_picturex_0611_linear_bearing_slide_with_rail",
    "run_picturex_0611_linear_bearing_slide_with_rail_tests",
]
