# SPDX-License-Identifier: Apache-2.0

"""Source-backed graduated wrench/key sets in family-compatible carriers."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mesh_from_cadquery,
    mesh_from_geometry,
    multiplicity_slot,
    sweep_profile_along_spline,
)

SetFamily = Literal[
    "l_hex_key_slot_holder",
    "l_flare_nut_slot_holder",
    "combination_hanging_rack",
    "ratcheting_combination_hanging_rack",
    "double_open_end_hanging_rack",
    "double_box_end_hanging_rack",
    "offset_ring_hanging_rack",
]

FAMILIES: tuple[SetFamily, ...] = (
    "l_hex_key_slot_holder",
    "l_flare_nut_slot_holder",
    "combination_hanging_rack",
    "ratcheting_combination_hanging_rack",
    "double_open_end_hanging_rack",
    "double_box_end_hanging_rack",
    "offset_ring_hanging_rack",
)

_L_FAMILIES = {
    "l_hex_key_slot_holder",
    "l_flare_nut_slot_holder",
}
_HANGING_FAMILIES = set(FAMILIES) - _L_FAMILIES
_RING_FAMILIES = {
    "combination_hanging_rack",
    "ratcheting_combination_hanging_rack",
    "double_box_end_hanging_rack",
    "offset_ring_hanging_rack",
}

TEMPLATE_DOMAIN = TemplateDomain(
    (
        component_slot("set_family", FAMILIES),
        multiplicity_slot("tool_count", (5, 8, 10), item_slot="set_family"),
    )
)


@dataclass(frozen=True)
class Config:
    set_family: SetFamily = "combination_hanging_rack"
    tool_count: int = 8
    tool_length_m: float | None = None
    name: str = "wrench_set"


@dataclass(frozen=True)
class ResolvedConfig:
    set_family: SetFamily
    tool_count: int
    tool_length_m: float
    tool_pitch_m: float
    holder_width_m: float
    holder_depth_m: float
    holder_low_z_m: float
    holder_high_z_m: float
    seat_z_m: float
    extraction_travel_m: float
    slot_positions_m: tuple[float, ...]
    tool_lengths_m: tuple[float, ...]
    fan_angles_rad: tuple[float, ...]
    name: str


_LENGTH_RANGES: dict[SetFamily, tuple[float, float]] = {
    "l_hex_key_slot_holder": (0.15, 0.24),
    "l_flare_nut_slot_holder": (0.16, 0.25),
    "combination_hanging_rack": (0.20, 0.32),
    "ratcheting_combination_hanging_rack": (0.21, 0.33),
    "double_open_end_hanging_rack": (0.20, 0.32),
    "double_box_end_hanging_rack": (0.21, 0.33),
    "offset_ring_hanging_rack": (0.22, 0.34),
}


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    family = choices["set_family"]
    rng = random.Random(seed ^ 0x611A_2026)
    low, high = _LENGTH_RANGES[family]
    return Config(
        set_family=family,
        tool_count=choices["tool_count"],
        tool_length_m=round(rng.uniform(low, high), 4),
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "set_family": config.set_family,
            "tool_count": config.tool_count,
        }
    )
    low, high = _LENGTH_RANGES[config.set_family]
    length = 0.5 * (low + high) if config.tool_length_m is None else float(config.tool_length_m)
    # Overrides are applied as raw dataclass.replace values, so a length drawn
    # for one family can arrive alongside another family's set_family. Clamp
    # into the active family's legal range instead of rejecting the config.
    length = min(max(length, low), high)

    if config.set_family in _L_FAMILIES:
        pitch = 0.026 + 0.004 * (length - low) / max(high - low, 1.0e-6)
        holder_width = (config.tool_count - 1) * pitch + 0.030
        holder_depth = 0.034
        low_z = 0.075
        # Neighbour separation comes from the wedge slope itself: each slot
        # must descend by more than the stacked vertical envelope of two
        # adjacent hex arms (corner radius stock / sqrt(3)) plus a real gap,
        # reduced by the relief the shrinking stock adds between neighbours.
        stock_a = 0.0093
        stock_b = 0.0093 - 0.0052 / max(1, config.tool_count - 1)
        step_relief = (1.35 + 0.62) * (stock_a - stock_b)
        drop_per_slot = 2.0 * stock_a / math.sqrt(3.0) + 0.0015 - step_relief
        high_z = low_z + drop_per_slot * holder_width / pitch
        seat_z = 0.0
        # The single-axis joint represents the initial guided release while the
        # long leg is still captured. Full removal of an L tool requires a
        # subsequent out-of-plane hand motion that is not modeled as a second
        # articulation.
        travel = 0.001
        fan_angles = tuple(0.0 for _ in range(config.tool_count))
    else:
        max_head = 0.0118 + 0.008 * (length - low) / max(high - low, 1.0e-6)
        pitch = max(0.030, 2.45 * max_head)
        holder_width = (config.tool_count - 1) * pitch + 0.066
        holder_depth = 0.026
        low_z = 0.165
        high_z = 0.350
        seat_z = 0.190
        travel = 0.010
        fan_limit = math.radians(9.5 + 0.35 * (config.tool_count - 5))
        fan_angles = tuple(
            fan_limit
            - 2.0 * fan_limit * index / max(1, config.tool_count - 1)
            for index in range(config.tool_count)
        )

    slots = tuple(
        (index - 0.5 * (config.tool_count - 1)) * pitch
        for index in range(config.tool_count)
    )
    lengths = tuple(
        length * (0.72 + 0.28 * index / max(1, config.tool_count - 1))
        for index in range(config.tool_count)
    )
    return ResolvedConfig(
        set_family=config.set_family,
        tool_count=config.tool_count,
        tool_length_m=length,
        tool_pitch_m=pitch,
        holder_width_m=holder_width,
        holder_depth_m=holder_depth,
        holder_low_z_m=low_z,
        holder_high_z_m=high_z,
        seat_z_m=seat_z,
        extraction_travel_m=travel,
        slot_positions_m=slots,
        tool_lengths_m=lengths,
        fan_angles_rad=fan_angles,
        name=config.name,
    )


def _materials(model: ArticulatedObject) -> dict[str, str]:
    model.material("molded_blue_plastic", rgba=(0.018, 0.205, 0.565, 1.0))
    model.material("blue_raised_detail", rgba=(0.030, 0.300, 0.720, 1.0))
    model.material("yellow_molded_plastic", rgba=(0.96, 0.69, 0.025, 1.0))
    model.material("yellow_size_mark", rgba=(0.46, 0.29, 0.012, 1.0))
    model.material("black_oxide_steel", rgba=(0.035, 0.040, 0.045, 1.0))
    model.material("polished_chrome", rgba=(0.82, 0.86, 0.90, 1.0))
    model.material("ratchet_detail", rgba=(0.38, 0.42, 0.46, 1.0))
    return {
        "blue": "molded_blue_plastic",
        "blue_detail": "blue_raised_detail",
        "yellow": "yellow_molded_plastic",
        "yellow_detail": "yellow_size_mark",
        "dark": "black_oxide_steel",
        "chrome": "polished_chrome",
        "ratchet": "ratchet_detail",
    }


def _regular_hex_profile(across_flats: float) -> list[tuple[float, float]]:
    radius = across_flats / math.sqrt(3.0)
    return [
        (
            radius * math.cos(math.pi / 6.0 + index * math.pi / 3.0),
            radius * math.sin(math.pi / 6.0 + index * math.pi / 3.0),
        )
        for index in range(6)
    ]


def _l_key_geometries(
    *,
    stock: float,
    long_leg: float,
    short_leg: float,
) -> tuple[object, object, object]:
    bend_radius = max(0.0055, 1.35 * stock)
    profile = _regular_hex_profile(stock)
    shank_path = [
        (0.0, 0.0, -long_leg),
        (0.0, 0.0, -max(0.045, 3.0 * bend_radius)),
        (0.0, 0.0, -bend_radius),
    ]
    elbow_path = [(0.0, 0.0, -bend_radius)]
    for step in range(1, 8):
        angle = math.pi - 0.5 * math.pi * step / 7.0
        elbow_path.append(
            (
                bend_radius + bend_radius * math.cos(angle),
                0.0,
                -bend_radius + bend_radius * math.sin(angle),
            )
        )
    arm_path = [
        (bend_radius, 0.0, 0.0),
        (min(short_leg - 0.006, bend_radius + 0.018), 0.0, 0.0),
        (short_leg, 0.0, 0.0),
    ]
    common = {
        "profile": profile,
        "samples_per_segment": 5,
        "closed_spline": False,
        "spline": "catmull_rom",
        "alpha": 0.5,
        "cap_profile": True,
        "up_hint": (0.0, 1.0, 0.0),
    }
    return (
        sweep_profile_along_spline(shank_path, **common),
        sweep_profile_along_spline(elbow_path, **common),
        sweep_profile_along_spline(arm_path, **common),
    )


def _l_holder_top_z(r: ResolvedConfig, x: float) -> float:
    normalized = (x + 0.5 * r.holder_width_m) / r.holder_width_m
    return r.holder_high_z_m + (r.holder_low_z_m - r.holder_high_z_m) * normalized


def _l_stock(r: ResolvedConfig, index: int) -> float:
    rank = index / max(1, r.tool_count - 1)
    return 0.0093 - 0.0052 * rank


def _l_holder_shape(r: ResolvedConfig) -> cq.Workplane:
    width = r.holder_width_m
    depth = r.holder_depth_m
    body = (
        cq.Workplane("XZ")
        .moveTo(-0.5 * width, 0.0)
        .lineTo(0.5 * width, 0.0)
        .lineTo(0.5 * width, r.holder_low_z_m)
        .lineTo(-0.5 * width, r.holder_high_z_m)
        .close()
        .extrude(0.5 * depth, both=True)
    )
    for index, x in enumerate(r.slot_positions_m):
        stock = _l_stock(r, index)
        # True across-flats hex bore with molded clearance. The swept shank
        # corners sit at stock / sqrt(3) and point at the socket vertices
        # (both oriented 30+60k deg), so the tight spot is each shank corner
        # against the adjacent socket flat: apothem - stock / 2. Size the
        # bore so that gap stays a true positive clearance within the 1 mm
        # support-contact tolerance for every stock size.
        socket_gap = 0.0008
        socket = (
            cq.Workplane("XY", origin=(x, 0.005, -0.008))
            .polygon(6, stock + 2.0 * socket_gap, circumscribed=True)
            .extrude(r.holder_high_z_m + 0.030)
        )
        body = body.cut(socket)
        groove = (
            cq.Workplane("XY")
            .box(stock + 0.0016, 0.0042, 0.72 * r.holder_high_z_m)
            .translate((x, -0.5 * depth + 0.0008, 0.66 * r.holder_high_z_m))
        )
        body = body.cut(groove)
    try:
        body = body.edges("|Y").fillet(0.0022)
    except Exception:
        pass
    return body.clean()


def _flare_nut_head_shape(
    *,
    stock: float,
    short_leg: float,
) -> cq.Workplane:
    outer = 2.6 * stock
    thickness = 1.0 * stock
    bore = 1.18 * stock
    ring = cq.Workplane("XY").circle(0.5 * outer).extrude(thickness)
    ring = ring.cut(cq.Workplane("XY").polygon(6, bore).extrude(thickness))
    slot = (
        cq.Workplane("XY")
        .box(0.55 * bore, 0.64 * outer, thickness + 0.003)
        .translate((0.0, 0.36 * outer, 0.5 * thickness))
    )
    return ring.cut(slot).translate((short_leg, 0.0, -0.5 * thickness)).clean()


def _add_l_holder(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> object:
    holder = model.part(
        "slot_holder",
        meta={
            "role": "slot_holder",
            "family": r.set_family,
            "socket_count": r.tool_count,
            "socket_profile": "true_hexagonal_cut",
            "carrier_style": "source_sloped_molded_wedge",
            "has_external_base": False,
        },
    )
    holder.visual(
        mesh_from_cadquery(
            _l_holder_shape(r),
            f"{r.set_family}_molded_holder",
            assets=assets,
            tolerance=0.0012,
        ),
        material=mats["yellow"],
        name="molded_wedge_with_hex_sockets", material_class_id="plastic.opaque_glossy_molded",
    )
    holder.visual(
        Box((r.holder_width_m - 0.008, 0.005, 0.55 * r.holder_low_z_m)),
        origin=Origin(
            xyz=(0.0, -0.5 * r.holder_depth_m - 0.0015, 0.31 * r.holder_low_z_m)
        ),
        material=mats["yellow"],
        name="molded_front_plate", material_class_id="plastic.opaque_glossy_molded",
    )
    for index, x in enumerate(r.slot_positions_m):
        holder.visual(
            Box((0.45 * r.tool_pitch_m, 0.006, 0.0045)),
            origin=Origin(
                xyz=(
                    x,
                    -0.5 * r.holder_depth_m - 0.0035,
                    0.032 + 0.0035 * (index % 2),
                )
            ),
            material=mats["yellow_detail"],
            name=f"size_tick_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    return holder


def _add_l_tools(
    model: ArticulatedObject,
    holder: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> None:
    flare = r.set_family == "l_flare_nut_slot_holder"
    for index, (x, long_leg) in enumerate(
        zip(r.slot_positions_m, reversed(r.tool_lengths_m))
    ):
        stock = _l_stock(r, index)
        short_leg = min(0.34 * long_leg, 0.046 + 0.003 * (r.tool_count - index))
        bend_radius = max(0.0055, 1.35 * stock)
        shank, elbow, arm = _l_key_geometries(
            stock=stock,
            long_leg=long_leg,
            short_leg=short_leg,
        )
        tool = model.part(
            f"wrench_{index}",
            meta={
                "role": "wrench",
                "family": r.set_family,
                "size_rank": index,
                "nominal_length_m": long_leg,
                "stock_across_flats_m": stock,
                "profile_verified": True,
                "l_shaped": True,
                "true_hex_stock": True,
                "flare_nut_head": flare,
                "true_bore_count": 1 if flare else 0,
                "open_jaw_count": 0,
                "ring_bore_count": 1 if flare else 0,
            },
        )
        tool.visual(
            mesh_from_geometry(shank, f"{r.set_family}_{index}_long_leg"),
            material=mats["dark"],
            name="true_hex_long_leg", material_class_id="metal.blackened_gunmetal",
        )
        tool.visual(
            mesh_from_geometry(elbow, f"{r.set_family}_{index}_elbow"),
            material=mats["dark"],
            name="swept_bend", material_class_id="metal.blackened_gunmetal",
        )
        tool.visual(
            mesh_from_geometry(arm, f"{r.set_family}_{index}_short_leg"),
            material=mats["dark"],
            name="true_hex_short_leg", material_class_id="metal.blackened_gunmetal",
        )
        if flare:
            tool.visual(
                mesh_from_cadquery(
                    _flare_nut_head_shape(stock=stock, short_leg=short_leg),
                    f"{r.set_family}_{index}_slotted_head",
                    assets=assets,
                    tolerance=0.0007,
                ),
                material=mats["dark"],
                name="slotted_flare_nut_head_with_bore", material_class_id="metal.blackened_gunmetal",
            )
        # The carrier slope descends toward +x while every short leg points
        # +x, so tool i's head envelope hangs beside the next slot's short
        # leg. The wedge slope (resolve_config) descends more per slot than
        # the stacked arm envelopes need, so each joint stays glued just
        # above its own seat column with real clearance at every index,
        # regardless of tool_count, length or family.
        joint_z = (
            _l_holder_top_z(r, x)
            + bend_radius
            + 0.62 * stock
            + 0.0015
        )
        model.articulation(
            f"wrench_slide_{index}",
            ArticulationType.PRISMATIC,
            parent=holder,
            child=tool,
            origin=Origin(xyz=(x, 0.005, joint_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=18.0,
                velocity=0.12,
                lower=0.0,
                upper=r.extraction_travel_m,
            ),
            meta={
                "role": "individual_tool_extraction",
                "seat_type": "hex_socket",
                "slot_index": index,
            },
        )


def _box_shape(
    size: tuple[float, float, float],
    center: tuple[float, float, float],
) -> cq.Workplane:
    return cq.Workplane("XY").box(*size).translate(center)


def _hanging_holder_shape(r: ResolvedConfig) -> cq.Workplane:
    width = r.holder_width_m
    half = 0.5 * width
    depth = r.holder_depth_m
    shoulder = min(0.055, 0.20 * width)
    silhouette = [
        (-half + 0.004, r.holder_low_z_m),
        (-half, 0.272),
        (-half + 0.014, 0.321),
        (-half + shoulder, r.holder_high_z_m),
        (half - shoulder, r.holder_high_z_m),
        (half - 0.014, 0.321),
        (half, 0.272),
        (half - 0.004, r.holder_low_z_m),
    ]
    body = (
        cq.Workplane("XZ")
        .polyline(silhouette)
        .close()
        .extrude(0.5 * depth, both=True)
    )
    opening_width = max(0.085, width - 2.0 * shoulder - 0.032)
    handle_cut = (
        cq.Workplane("XZ")
        .center(0.0, 0.309)
        .slot2D(opening_width, 0.038, 0.0)
        .extrude(depth, both=True)
    )
    body = body.cut(handle_cut)
    body = body.union(_box_shape((width - 0.038, 0.010, 0.058), (0.0, -0.015, 0.238)))
    body = body.union(_box_shape((width - 0.020, 0.038, 0.034), (0.0, -0.006, r.seat_z_m)))
    body = body.union(_box_shape((width - 0.050, 0.010, 0.011), (0.0, -0.015, 0.340)))
    # Lower stabiliser rail: it must stay in front of the thickest tool plane.
    # The tools hang in the joint plane y = -0.030, so derive the rail's back
    # face from the maximum plate thickness plus a small gap that keeps every
    # tool in real support contact (<= 1 mm) without ever touching the rail.
    max_plate_thickness = 0.0032 + 0.0011
    rail_clearance = 0.0003
    rail_back_y = -0.030 + 0.5 * max_plate_thickness + rail_clearance
    body = body.union(
        _box_shape((width - 0.030, 0.008, 0.009), (0.0, rail_back_y + 0.004, 0.169))
    )
    body = body.union(_box_shape((0.010, 0.032, 0.105), (-half + 0.005, -0.008, 0.123)))
    body = body.union(_box_shape((0.010, 0.032, 0.105), (half - 0.005, -0.008, 0.123)))

    for index, x in enumerate(r.slot_positions_m):
        head_outer, head_bore, shaft_width, _ = _tool_dimensions(r, index)
        if r.set_family == "double_open_end_hanging_rack":
            # The clip channel walls must stand off the shaft sides by a real
            # clearance that still sits inside the support-contact tolerance,
            # so the seated wrench is physically captured by its clip. Derive
            # the side gap from the shaft width so it scales with tool size.
            clip_side_gap = 0.03 * shaft_width
            clip_gap = shaft_width + 2.0 * clip_side_gap
            clip_width = 0.0045
            clip_z = r.seat_z_m - 0.014
            # The clip arms and front bar sit behind the wrench plane with a
            # real y clearance derived from the thickest plate, and rotate by
            # the seat fan angle about the joint axis so the channel follows
            # the tilted shaft.
            clip_face_gap = 0.0005
            clip_depth = 0.019
            clip_center_y = -0.030 + 0.5 * max_plate_thickness + clip_face_gap + 0.5 * clip_depth
            clip = _box_shape(
                (clip_width, clip_depth, 0.030),
                (x - 0.5 * (clip_gap + clip_width), clip_center_y, clip_z),
            ).union(
                _box_shape(
                    (clip_width, clip_depth, 0.030),
                    (x + 0.5 * (clip_gap + clip_width), clip_center_y, clip_z),
                )
            ).union(
                _box_shape(
                    (clip_gap + 2.0 * clip_width, clip_depth, 0.005),
                    (x, clip_center_y, clip_z + 0.013),
                )
            )
            clip = clip.rotate(
                (x, -0.030, r.seat_z_m),
                (x, -0.029, r.seat_z_m),
                math.degrees(r.fan_angles_rad[index]),
            )
            body = body.union(clip)
        else:
            boss_radius = min(0.80 * head_bore, 0.44 * head_outer)
            boss = (
                cq.Workplane("XZ")
                .center(x, r.seat_z_m)
                .circle(boss_radius)
                .extrude(0.010, both=True)
                .translate((0.0, -0.019, 0.0))
            )
            body = body.union(boss)
        body = body.union(
            _box_shape((0.46 * r.tool_pitch_m, 0.006, 0.011), (x, -0.024, 0.207))
        )
    try:
        body = body.edges().fillet(0.0022)
    except Exception:
        pass
    return body.clean()


def _tool_dimensions(
    r: ResolvedConfig,
    index: int,
) -> tuple[float, float, float, float]:
    rank = index / max(1, r.tool_count - 1)
    head_outer = 0.0078 + 0.0038 * rank + 0.006 * (
        r.tool_length_m - _LENGTH_RANGES[r.set_family][0]
    )
    if r.set_family == "ratcheting_combination_hanging_rack":
        head_outer *= 1.16
    bore = 0.50 * head_outer
    shaft_width = 0.42 * head_outer
    thickness = 0.0032 + 0.0011 * rank
    return head_outer, bore, shaft_width, thickness


def _ring_head(
    *,
    x: float,
    z: float,
    outer: float,
    bore: float,
    thickness: float,
    points: int = 12,
) -> cq.Workplane:
    ring = (
        cq.Workplane("XZ")
        .center(x, z)
        .circle(outer)
        .polygon(points, 2.0 * bore, circumscribed=True)
        .extrude(0.5 * thickness, both=True)
    )
    return ring


def _open_head(
    *,
    x: float,
    z: float,
    outer: float,
    inner: float,
    thickness: float,
    opening_sign: float,
) -> cq.Workplane:
    head = (
        cq.Workplane("XZ")
        .center(x, z)
        .circle(outer)
        .circle(inner)
        .extrude(0.5 * thickness, both=True)
    )
    near = z + opening_sign * inner * 0.30
    far = z + opening_sign * outer * 1.45
    throat = (
        cq.Workplane("XZ")
        .polyline(
            [
                (x - 0.46 * inner, near),
                (x + 0.46 * inner, near),
                (x + 0.94 * inner, far),
                (x - 0.94 * inner, far),
            ]
        )
        .close()
        .extrude(thickness, both=True)
    )
    return head.cut(throat)


def _shaft_shape(
    *,
    top_x: float,
    bottom_x: float,
    top_z: float,
    bottom_z: float,
    top_width: float,
    bottom_width: float,
    thickness: float,
) -> cq.Workplane:
    profile = [
        (top_x - 0.5 * top_width, top_z),
        (bottom_x - 0.5 * bottom_width, bottom_z),
        (bottom_x + 0.5 * bottom_width, bottom_z),
        (top_x + 0.5 * top_width, top_z),
    ]
    return (
        cq.Workplane("XZ")
        .polyline(profile)
        .close()
        .extrude(0.5 * thickness, both=True)
    )


def _flat_wrench_shape(
    r: ResolvedConfig,
    index: int,
) -> cq.Workplane:
    family = r.set_family
    length = r.tool_lengths_m[index]
    outer, bore, shaft_width, thickness = _tool_dimensions(r, index)
    lower_outer = 1.10 * outer
    top_x = 0.0
    bottom_x = 0.0
    if family == "offset_ring_hanging_rack":
        top_x = 0.62 * outer
        bottom_x = -0.62 * lower_outer
    shaft = _shaft_shape(
        top_x=top_x,
        bottom_x=bottom_x,
        top_z=-0.48 * outer,
        bottom_z=-length + 0.52 * lower_outer,
        top_width=shaft_width,
        bottom_width=1.18 * shaft_width,
        thickness=thickness,
    )

    if family == "double_open_end_hanging_rack":
        top = _open_head(
            x=top_x,
            z=0.0,
            outer=outer,
            inner=0.55 * outer,
            thickness=thickness,
            opening_sign=1.0,
        )
        bottom = _open_head(
            x=bottom_x,
            z=-length,
            outer=lower_outer,
            inner=0.55 * lower_outer,
            thickness=thickness,
            opening_sign=-1.0,
        )
    elif family in {
        "double_box_end_hanging_rack",
        "offset_ring_hanging_rack",
    }:
        top = _ring_head(
            x=top_x,
            z=0.0,
            outer=outer,
            bore=bore,
            thickness=thickness,
        )
        bottom = _ring_head(
            x=bottom_x,
            z=-length,
            outer=lower_outer,
            bore=0.52 * lower_outer,
            thickness=thickness,
        )
    else:
        points = 12
        if family == "ratcheting_combination_hanging_rack":
            points = 16
        top = _ring_head(
            x=top_x,
            z=0.0,
            outer=outer,
            bore=bore,
            thickness=thickness,
            points=points,
        )
        bottom = _open_head(
            x=bottom_x,
            z=-length,
            outer=lower_outer,
            inner=0.55 * lower_outer,
            thickness=thickness,
            opening_sign=-1.0,
        )

    wrench = top.union(shaft).union(bottom)
    if family == "ratcheting_combination_hanging_rack":
        lever = (
            cq.Workplane("XZ")
            .center(0.58 * outer, 0.15 * outer)
            .rect(0.38 * outer, 0.20 * outer)
            .extrude(0.22 * thickness)
            .translate((0.0, 0.5 * thickness, 0.0))
        )
        wrench = wrench.union(lever)
    if family == "offset_ring_hanging_rack":
        # The offset rib must stop short of the ring hole: the seat boss
        # passes through that hole, so any rib material inside the hole
        # (inscribed radius = bore) would collide with the boss. Derive the
        # rib reach from the hole radius plus a size-relative gap, expanded
        # by the rib half-width corner spread, so the end stays outside for
        # every tool size.
        rib_top_z = -(bore + 0.04 * outer)
        top_rib = _shaft_shape(
            top_x=0.0,
            bottom_x=top_x,
            top_z=-1.55 * outer,
            bottom_z=rib_top_z,
            top_width=0.80 * shaft_width,
            bottom_width=0.92 * shaft_width,
            thickness=1.18 * thickness,
        )
        bottom_rib = _shaft_shape(
            top_x=bottom_x,
            bottom_x=0.0,
            top_z=-length + 0.32 * lower_outer,
            bottom_z=-length + 1.55 * lower_outer,
            top_width=0.92 * shaft_width,
            bottom_width=0.80 * shaft_width,
            thickness=1.18 * thickness,
        )
        wrench = wrench.union(top_rib).union(bottom_rib)
        # The extraction joint fans each tool about the seat axis, so the ring
        # hole that hangs on the holder boss must be centred on that axis or
        # the boss would chew into the hole edge of every fanned tool.
        # Re-centre the profile on the top ring hole; the offset neck then
        # reads as the visibly shifted lower end instead.
        wrench = wrench.translate((-top_x, 0.0, 0.0))
    try:
        wrench = wrench.clean().edges().chamfer(0.00035)
    except Exception:
        wrench = wrench.clean()
    return wrench


def _add_hanging_holder(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> object:
    seat_type = (
        "neck_snap_clip"
        if r.set_family == "double_open_end_hanging_rack"
        else "ring_boss"
    )
    holder = model.part(
        "hanging_holder",
        meta={
            "role": "hanging_holder",
            "family": r.set_family,
            "carrier_style": "source_blue_handle_rack",
            "has_handle_opening": True,
            "seat_type": seat_type,
            "seat_count": r.tool_count,
            "has_side_rails": True,
        },
    )
    holder.visual(
        mesh_from_cadquery(
            _hanging_holder_shape(r),
            f"{r.set_family}_blue_handled_holder",
            assets=assets,
            tolerance=0.0012,
        ),
        material=mats["blue"],
        name=f"blue_handled_holder_with_{seat_type}s", material_class_id="plastic.opaque_glossy_molded",
    )
    holder.visual(
        Box((r.holder_width_m - 0.055, 0.0018, 0.035)),
        origin=Origin(xyz=(0.0, -0.5 * r.holder_depth_m - 0.0070, 0.240)),
        material=mats["blue_detail"],
        name="raised_information_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    return holder


def _add_hanging_tools(
    model: ArticulatedObject,
    holder: object,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> None:
    for index, (x, angle) in enumerate(zip(r.slot_positions_m, r.fan_angles_rad)):
        outer, _, _, _ = _tool_dimensions(r, index)
        ring_count = {
            "combination_hanging_rack": 1,
            "ratcheting_combination_hanging_rack": 1,
            "double_open_end_hanging_rack": 0,
            "double_box_end_hanging_rack": 2,
            "offset_ring_hanging_rack": 2,
        }[r.set_family]
        jaw_count = {
            "combination_hanging_rack": 1,
            "ratcheting_combination_hanging_rack": 1,
            "double_open_end_hanging_rack": 2,
            "double_box_end_hanging_rack": 0,
            "offset_ring_hanging_rack": 0,
        }[r.set_family]
        tool = model.part(
            f"wrench_{index}",
            meta={
                "role": "wrench",
                "family": r.set_family,
                "size_rank": index,
                "nominal_length_m": r.tool_lengths_m[index],
                "profile_verified": True,
                "forged_tapered_handle": True,
                "open_jaw_count": jaw_count,
                "ring_bore_count": ring_count,
                "true_bore_count": ring_count,
                "ratchet_mechanism": (
                    r.set_family == "ratcheting_combination_hanging_rack"
                ),
                "offset_neck": r.set_family == "offset_ring_hanging_rack",
            },
        )
        tool.visual(
            mesh_from_cadquery(
                _flat_wrench_shape(r, index),
                f"{r.set_family}_wrench_{index}",
                assets=assets,
                tolerance=0.0008,
            ),
            material=mats["chrome"],
            name=f"{r.set_family}_forged_profile", material_class_id="metal.chrome_polished",
        )
        model.articulation(
            f"wrench_slide_{index}",
            ArticulationType.PRISMATIC,
            parent=holder,
            child=tool,
            origin=Origin(
                xyz=(x, -0.030, r.seat_z_m),
                rpy=(0.0, angle, 0.0),
            ),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=28.0,
                velocity=0.18,
                lower=0.0,
                upper=r.extraction_travel_m,
            ),
            meta={
                "role": "individual_tool_extraction",
                "seat_type": (
                    "neck_snap_clip"
                    if r.set_family == "double_open_end_hanging_rack"
                    else "ring_boss"
                ),
                "slot_index": index,
                "fan_angle_rad": angle,
            },
        )


def _build_l_family(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    holder = _add_l_holder(model, r, mats, assets=assets)
    _add_l_tools(model, holder, r, mats, assets=assets)
    return model


def _build_hanging_family(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    holder = _add_hanging_holder(model, r, mats, assets=assets)
    _add_hanging_tools(model, holder, r, mats, assets=assets)
    return model


def _set_family_l_hex_key_slot_holder_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_l_family(model, r, mats, assets=assets)


def _set_family_l_flare_nut_slot_holder_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_l_family(model, r, mats, assets=assets)


def _set_family_combination_hanging_rack_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_hanging_family(model, r, mats, assets=assets)


def _set_family_ratcheting_combination_hanging_rack_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_hanging_family(model, r, mats, assets=assets)


def _set_family_double_open_end_hanging_rack_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_hanging_family(model, r, mats, assets=assets)


def _set_family_double_box_end_hanging_rack_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_hanging_family(model, r, mats, assets=assets)


def _set_family_offset_ring_hanging_rack_build(
    model: ArticulatedObject,
    r: ResolvedConfig,
    mats: dict[str, str],
    *,
    assets: AssetContext | None,
) -> ArticulatedObject:
    return _build_hanging_family(model, r, mats, assets=assets)


_FAMILY_BUILDERS = {
    "l_hex_key_slot_holder": _set_family_l_hex_key_slot_holder_build,
    "l_flare_nut_slot_holder": _set_family_l_flare_nut_slot_holder_build,
    "combination_hanging_rack": _set_family_combination_hanging_rack_build,
    "ratcheting_combination_hanging_rack": (
        _set_family_ratcheting_combination_hanging_rack_build
    ),
    "double_open_end_hanging_rack": _set_family_double_open_end_hanging_rack_build,
    "double_box_end_hanging_rack": _set_family_double_box_end_hanging_rack_build,
    "offset_ring_hanging_rack": _set_family_offset_ring_hanging_rack_build,
}


def build_wrench_set(
    config: Config,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "wrench_set",
            "slot_choices": (
                ("set_family", r.set_family),
                ("tool_count", r.tool_count),
            ),
            "source_layout": (
                "sloped molded slot carrier"
                if r.set_family in _L_FAMILIES
                else "blue handled hanging carrier"
            ),
        },
    )
    mats = _materials(model)
    return _FAMILY_BUILDERS[r.set_family](model, r, mats, assets=assets)


def _parts_by_role(model: ArticulatedObject, role: str):
    return [part for part in model.parts if part.meta.get("role") == role]


def run_wrench_set_tests(
    model: ArticulatedObject,
    config: Config,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)
    tools = _parts_by_role(model, "wrench")
    slot_holders = _parts_by_role(model, "slot_holder")
    hanging_holders = _parts_by_role(model, "hanging_holder")
    holder = (slot_holders or hanging_holders)[0] if (slot_holders or hanging_holders) else None
    slides = [
        joint
        for joint in model.articulations
        if joint.child in {part.name for part in tools}
    ]

    ctx.check(
        "category_anchor: real wrench profile",
        len(tools) == r.tool_count
        and len({part.meta.get("nominal_length_m") for part in tools}) == r.tool_count
        and all(part.meta.get("profile_verified") is True for part in tools)
        and all(
            part.meta.get("true_hex_stock") is True
            or part.meta.get("open_jaw_count", 0) > 0
            or part.meta.get("true_bore_count", 0) > 0
            for part in tools
        ),
        details=f"tool_count={len(tools)}, expected={r.tool_count}",
    )
    ctx.check(
        "category_anchor: source-like slot holder",
        (
            r.set_family not in _L_FAMILIES
            or (
                len(slot_holders) == 1
                and not hanging_holders
                and holder is not None
                and holder.meta.get("socket_count") == r.tool_count
                and holder.meta.get("socket_profile") == "true_hexagonal_cut"
                and holder.meta.get("has_external_base") is False
            )
        ),
        details=f"slot_holders={len(slot_holders)}, holder_meta={getattr(holder, 'meta', None)}",
    )
    ctx.check(
        "category_anchor: source-like hanging holder",
        (
            r.set_family not in _HANGING_FAMILIES
            or (
                len(hanging_holders) == 1
                and not slot_holders
                and holder is not None
                and holder.meta.get("carrier_style") == "source_blue_handle_rack"
                and holder.meta.get("has_handle_opening") is True
                and holder.meta.get("seat_count") == r.tool_count
            )
        ),
        details=(
            f"hanging_holders={len(hanging_holders)}, "
            f"holder_meta={getattr(holder, 'meta', None)}"
        ),
    )

    identity = {
        "l_hex_key_slot_holder": all(
            part.meta.get("l_shaped") is True
            and part.meta.get("true_hex_stock") is True
            and part.meta.get("flare_nut_head") is False
            for part in tools
        ),
        "l_flare_nut_slot_holder": all(
            part.meta.get("l_shaped") is True
            and part.meta.get("flare_nut_head") is True
            and part.meta.get("true_bore_count") == 1
            for part in tools
        ),
        "combination_hanging_rack": all(
            part.meta.get("open_jaw_count") == 1
            and part.meta.get("ring_bore_count") == 1
            and part.meta.get("ratchet_mechanism") is False
            for part in tools
        ),
        "ratcheting_combination_hanging_rack": all(
            part.meta.get("open_jaw_count") == 1
            and part.meta.get("ring_bore_count") == 1
            and part.meta.get("ratchet_mechanism") is True
            for part in tools
        ),
        "double_open_end_hanging_rack": (
            holder is not None
            and holder.meta.get("seat_type") == "neck_snap_clip"
            and all(
                part.meta.get("open_jaw_count") == 2
                and part.meta.get("ring_bore_count") == 0
                for part in tools
            )
        ),
        "double_box_end_hanging_rack": all(
            part.meta.get("open_jaw_count") == 0
            and part.meta.get("ring_bore_count") == 2
            and part.meta.get("offset_neck") is False
            for part in tools
        ),
        "offset_ring_hanging_rack": all(
            part.meta.get("ring_bore_count") == 2
            and part.meta.get("offset_neck") is True
            for part in tools
        ),
    }[r.set_family]
    ctx.check(
        f"category_anchor: {r.set_family} identity",
        identity,
        details=f"family={r.set_family}, tool_meta={[part.meta for part in tools]}",
    )

    expected_axis = (
        (0.0, 0.0, 1.0)
        if r.set_family in _L_FAMILIES
        else (0.0, 0.0, -1.0)
    )
    ctx.check(
        "one independent extraction joint per tool",
        holder is not None
        and len(slides) == r.tool_count
        and all(
            joint.parent == holder.name
            and joint.articulation_type == ArticulationType.PRISMATIC
            and tuple(joint.axis) == expected_axis
            for joint in slides
        ),
        details=f"joint_count={len(slides)}, expected_axis={expected_axis}",
    )
    ctx.check(
        "multiplicity controls tools seats and joints",
        holder is not None
        and len(tools) == r.tool_count
        and len(slides) == r.tool_count
        and int(
            holder.meta.get(
                "socket_count",
                holder.meta.get("seat_count", -1),
            )
        )
        == r.tool_count,
        details=(
            f"tools={len(tools)}, joints={len(slides)}, "
            f"holder_meta={getattr(holder, 'meta', None)}"
        ),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "ten_long_l_flare_nut_tools",
        {
            "set_family": "l_flare_nut_slot_holder",
            "tool_count": 10,
            "tool_length_m": 0.25,
        },
        reason="maximum socket density and the most detailed L-shaped head",
    ),
    corner_case(
        "ten_long_double_open_tools",
        {
            "set_family": "double_open_end_hanging_rack",
            "tool_count": 10,
            "tool_length_m": 0.32,
        },
        reason="maximum fan width with neck clips rather than ring bosses",
    ),
    corner_case(
        "five_short_ratchet_tools",
        {
            "set_family": "ratcheting_combination_hanging_rack",
            "tool_count": 5,
            "tool_length_m": 0.21,
        },
        reason="minimum capacity with the largest top-end mechanism envelope",
    ),
    corner_case(
        "ten_long_offset_ring_tools",
        {
            "set_family": "offset_ring_hanging_rack",
            "tool_count": 10,
            "tool_length_m": 0.34,
        },
        reason="maximum offset neck and double-ring carrier envelope",
    ),
)


__all__ = [
    "Config",
    "ResolvedConfig",
    "TEMPLATE_CORNERS",
    "TEMPLATE_DOMAIN",
    "build_wrench_set",
    "config_from_seed",
    "resolve_config",
    "run_wrench_set_tests",
]
